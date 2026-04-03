"""Scrape LinkedIn posts"""
import json
import asyncio
import logging
from fastapi import APIRouter, UploadFile, File
from app.models.schemas import ScrapeRequest
from app.db.database import get_conn, init_db
from app.services.linkedin_scraper import fetch_post_by_url, fetch_latest_post, extract_username
import csv
import io
import re
import uuid

log = logging.getLogger("api")
router = APIRouter()


@router.post("/api/upload-csv")
async def upload_csv(file: UploadFile = File(...)):
    content = (await file.read()).decode("utf-8", errors="replace")
    log.info(f"CSV upload: {file.filename} ({len(content)} bytes)")

    profiles = []
    seen = set()

    for line in content.split("\n"):
        line = line.strip()
        if not line:
            continue
        for cell in re.split(r"[,;\t|]+", line):
            cell = cell.strip().strip('"\'')
            # Post URL
            m = re.search(r"linkedin\.com/posts/([a-zA-Z0-9_-]+?)[-_]", cell, re.I)
            if m:
                full_url = re.search(r"https?://[^\s,;\"']+", cell, re.I)
                username = m.group(1)
                key = username + (full_url.group(0) if full_url else "")
                if key not in seen:
                    seen.add(key)
                    profiles.append({"url": f"https://www.linkedin.com/in/{username}", "username": username,
                                     "type": "post", "postUrl": full_url.group(0) if full_url else cell})
                continue
            # Profile URL
            m = re.search(r"linkedin\.com/(?:in|company|pub)/([^\s,;\"'?&#/]+)", cell, re.I)
            if m:
                username = m.group(1)
                if username.lower() not in seen:
                    seen.add(username.lower())
                    profiles.append({"url": cell.strip(), "username": username, "type": "profile"})

    if not profiles:
        return {"error": "No LinkedIn URLs found in CSV", "status": 400}

    return {"success": True, "batchId": str(uuid.uuid4()), "count": len(profiles), "profiles": profiles}


@router.post("/api/scrape-profiles")
async def scrape_profiles(req: ScrapeRequest):
    init_db()
    conn = get_conn()

    results, cached, errors = [], [], []

    for p in req.profiles:
        username = p.get("username", "")
        post_url = p.get("postUrl", "")
        profile_type = p.get("type", "profile")

        # Cache check
        existing = conn.execute(
            "SELECT * FROM scraped_posts WHERE profile_url LIKE ? LIMIT 1",
            (f"%{username}%",)
        ).fetchone()

        if existing and profile_type == "post":
            # Check if same post URN
            if existing["post_urn"] and post_url:
                m = re.search(r"activity-(\d+)", post_url)
                if m and existing["post_urn"] == m.group(1):
                    log.info(f"CACHE HIT: {username}")
                    cached.append({"id": existing["id"], "author": existing["author_name"], "cached": True})
                    continue

        if existing and profile_type == "profile":
            log.info(f"CACHE HIT: {username}")
            cached.append({"id": existing["id"], "author": existing["author_name"], "cached": True})
            continue

        # Scrape
        try:
            if profile_type == "post" and post_url:
                data = await fetch_post_by_url(post_url)
            else:
                data = await fetch_latest_post(p.get("url", ""))

            if not data:
                errors.append({"url": p.get("url"), "error": "No data"})
                continue

            # Dedup by URN
            urn = data["post"]["urn"]
            if urn:
                dup = conn.execute("SELECT id FROM scraped_posts WHERE post_urn = ?", (urn,)).fetchone()
                if dup:
                    cached.append({"id": dup["id"], "author": data["author"]["name"], "cached": True})
                    continue

            cursor = conn.execute(
                "INSERT INTO scraped_posts (profile_url, author_name, author_headline, author_profile_pic, post_text, post_url, post_urn, likes_count, comments_count, shares_count, media_type, media_urls, posted_at, status, batch_id) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                (p.get("url"), data["author"]["name"], data["author"]["headline"],
                 data["author"]["profile_picture"], data["post"]["text"],
                 data["post"]["url"] or post_url, data["post"]["urn"],
                 data["stats"]["total_reactions"], data["stats"]["comments"], data["stats"]["shares"],
                 data["post"]["type"], json.dumps(data["media"]),
                 data["post"]["created_at"], "scraped", req.get_batch_id)
            )
            conn.commit()
            results.append({"id": cursor.lastrowid, "author": data["author"]["name"], "status": "scraped"})
            log.info(f"Scraped: {data['author']['name']} — {data['post']['text'][:80]}...")

        except Exception as e:
            log.error(f"Error scraping {username}: {e}")
            errors.append({"url": p.get("url"), "error": str(e)})

        await asyncio.sleep(1.5)  # Rate limit

    conn.close()
    return {"success": True, "batchId": req.get_batch_id, "scraped": len(results),
            "cached": len(cached), "failed": len(errors),
            "results": results, "cached_posts": cached, "errors": errors}
