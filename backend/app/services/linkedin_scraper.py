"""LinkedIn Scraper — RapidAPI"""
import os
import re
import httpx
import logging

log = logging.getLogger("scraper")

BASE_URL = "https://linkedin-scraper-api-real-time-fast-affordable.p.rapidapi.com"


def _headers():
    return {
        "X-RapidAPI-Key": os.getenv("RAPIDAPI_KEY", ""),
        "X-RapidAPI-Host": os.getenv("RAPIDAPI_HOST", "linkedin-scraper-api-real-time-fast-affordable.p.rapidapi.com"),
        "Content-Type": "application/json",
    }


def extract_username(url: str) -> str:
    if not url:
        return ""
    url = url.strip().rstrip("/")
    for pat in [r"linkedin\.com/in/([^/?&#]+)", r"linkedin\.com/posts/([a-zA-Z0-9_-]+?)[-_]"]:
        m = re.search(pat, url, re.I)
        if m:
            return m.group(1)
    return url.split("/")[-1].split("?")[0] if "/" in url else url


async def fetch_post_by_url(post_url: str) -> dict | None:
    log.info(f"Fetching post: {post_url[:80]}...")
    try:
        async with httpx.AsyncClient(timeout=20) as client:
            resp = await client.get(
                f"{BASE_URL}/post/detail",
                params={"post_url": post_url},
                headers=_headers(),
            )
        if resp.status_code != 200:
            log.error(f"HTTP {resp.status_code}")
            return None
        return _normalize(resp.json())
    except Exception as e:
        log.error(f"Scrape error: {e}")
        return None


async def fetch_latest_post(profile_url: str) -> dict | None:
    username = extract_username(profile_url)
    log.info(f"Fetching latest post for: {username}")
    try:
        async with httpx.AsyncClient(timeout=20) as client:
            resp = await client.get(
                f"{BASE_URL}/profile/posts",
                params={"username": username, "page_number": "1"},
                headers=_headers(),
            )
        if resp.status_code != 200:
            log.error(f"HTTP {resp.status_code} for {username}")
            return None
        data = resp.json()
        posts = data.get("data", [])
        if isinstance(posts, list) and posts:
            return _normalize({"data": posts[0]})
        if data.get("data", {}).get("post"):
            return _normalize(data)
        return None
    except Exception as e:
        log.error(f"Scrape error for {username}: {e}")
        return None


def _normalize(data: dict) -> dict | None:
    d = data.get("data", data)
    post = d.get("post", d)
    author = d.get("author", {})
    media = d.get("media", [])
    stats = d.get("stats", {})

    return {
        "post": {
            "id": post.get("id", ""),
            "url": post.get("url", ""),
            "text": post.get("text", ""),
            "type": post.get("type", "text"),
            "created_at": (post.get("created_at") or {}).get("date", "") if isinstance(post.get("created_at"), dict) else str(post.get("created_at", "")),
            "urn": (post.get("urn") or {}).get("activity_urn", post.get("id", "")) if isinstance(post.get("urn"), dict) else str(post.get("id", "")),
        },
        "author": {
            "name": author.get("name", "Unknown"),
            "headline": author.get("headline", ""),
            "profile_url": author.get("profile_url", ""),
            "profile_picture": author.get("profile_picture", ""),
            "followers": author.get("followers", 0),
        },
        "media": [{"type": m.get("type", "image"), "url": m.get("video_url") or m.get("url", ""), "thumbnail": m.get("thumbnail", "")} for m in (media or [])],
        "stats": {
            "total_reactions": stats.get("total_reactions", 0),
            "comments": stats.get("comments", 0),
            "shares": stats.get("shares", 0),
        },
    }
