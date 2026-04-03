"""Posts & Profile CRUD routes"""
import json
import csv
import io
import logging
from fastapi import APIRouter, UploadFile, File
from app.models.schemas import ProfileSaveRequest
from app.db.database import get_conn, init_db

log = logging.getLogger("api")
router = APIRouter()


def _post_to_camel(row) -> dict:
    r = dict(row)
    return {
        "id": r["id"],
        "profileUrl": r["profile_url"],
        "authorName": r["author_name"],
        "authorHeadline": r["author_headline"],
        "authorProfilePic": r["author_profile_pic"],
        "postText": r["post_text"],
        "postUrl": r["post_url"],
        "postUrn": r["post_urn"],
        "likesCount": r["likes_count"],
        "commentsCount": r["comments_count"],
        "sharesCount": r["shares_count"],
        "mediaType": r["media_type"],
        "mediaUrls": r["media_urls"],
        "postedAt": r["posted_at"],
        "status": r["status"],
        "batchId": r["batch_id"],
    }


@router.get("/api/posts")
async def list_posts():
    init_db()
    conn = get_conn()
    rows = conn.execute("SELECT * FROM scraped_posts ORDER BY id DESC").fetchall()
    conn.close()
    return {"posts": [_post_to_camel(r) for r in rows]}


@router.get("/api/post/{post_id}")
async def get_post(post_id: int):
    conn = get_conn()
    post = conn.execute("SELECT * FROM scraped_posts WHERE id = ?", (post_id,)).fetchone()
    if not post:
        conn.close()
        return {"error": "Not found"}, 404

    comments = conn.execute(
        "SELECT * FROM generated_comments WHERE post_id = ? ORDER BY variation_number", (post_id,)
    ).fetchall()

    analysis = None
    try:
        analysis = json.loads(post["post_analysis"] or "null")
    except:
        pass

    media = []
    try:
        media = json.loads(post["media_urls"] or "[]")
    except:
        pass

    conn.close()

    return {
        "post": {
            "id": post["id"], "authorName": post["author_name"],
            "authorHeadline": post["author_headline"],
            "authorProfilePic": post["author_profile_pic"],
            "postText": post["post_text"], "postUrl": post["post_url"],
            "likesCount": post["likes_count"], "commentsCount": post["comments_count"],
            "sharesCount": post["shares_count"], "mediaType": post["media_type"],
            "status": post["status"], "postedAt": post["posted_at"],
        },
        "analysis": analysis,
        "media": media,
        "comments": [
            {
                "id": c["id"], "text": c["text"], "angle": c["angle"],
                "variationNumber": c["variation_number"],
                "confidence": c["confidence"], "approach": c["approach"],
                "postType": c["post_type"],
                "validation": {"qualityScore": c["quality_score"], "wordCount": len((c["text"] or "").split())},
            }
            for c in comments
        ],
    }


@router.get("/api/profile")
async def get_profile():
    init_db()
    conn = get_conn()
    row = conn.execute("SELECT * FROM commenter_profiles WHERE is_active = 1").fetchone()
    conn.close()
    return {"profile": dict(row) if row else None}


@router.post("/api/profile")
async def save_profile(req: ProfileSaveRequest):
    init_db()
    conn = get_conn()
    conn.execute("UPDATE commenter_profiles SET is_active = 0")
    existing = conn.execute("SELECT id FROM commenter_profiles WHERE username = ?", (req.username,)).fetchone()
    if existing:
        conn.execute(
            "UPDATE commenter_profiles SET name=?, headline=?, profile_data=?, is_active=1 WHERE username=?",
            (req.name, req.headline, json.dumps(req.profile_data), req.username)
        )
    else:
        conn.execute(
            "INSERT INTO commenter_profiles (name, username, headline, profile_data, is_active) VALUES (?,?,?,?,1)",
            (req.name, req.username, req.headline, json.dumps(req.profile_data))
        )
    conn.commit()
    conn.close()
    return {"success": True}


@router.post("/api/feedback")
async def save_feedback(data: dict):
    conn = get_conn()
    conn.execute(
        "INSERT INTO comment_feedback (comment_id, rating, was_used) VALUES (?,?,?)",
        (data.get("commentId"), data.get("rating", 0), 1 if data.get("wasUsed") else 0)
    )
    conn.commit()
    conn.close()
    return {"success": True}


@router.post("/api/import-rag")
async def import_rag(file: UploadFile = File(...)):
    """Import RAG reference comments from CSV"""
    content = (await file.read()).decode("utf-8", errors="replace")
    reader = csv.DictReader(io.StringIO(content))

    conn = get_conn()
    count = 0
    for row in reader:
        try:
            conn.execute(
                "INSERT INTO reference_comments (post_content, comment_text, likes, replies, post_type, comment_angle, topic, engagement_score) VALUES (?,?,?,?,?,?,?,?)",
                (
                    (row.get("post_content", "") or "")[:500],
                    row.get("comment_text", ""),
                    int(row.get("likes", 0) or 0),
                    int(row.get("replies", 0) or 0),
                    row.get("post_type", ""),
                    row.get("comment_angle", ""),
                    row.get("topic", ""),
                    float(row.get("engagement_score", 0) or 0),
                ),
            )
            count += 1
        except Exception:
            pass
    conn.commit()

    total = conn.execute("SELECT COUNT(*) FROM reference_comments").fetchone()[0]
    conn.close()

    log.info(f"RAG import: {count} new rows, {total} total")
    return {"success": True, "imported": count, "total": total}


@router.get("/api/rag-status")
async def rag_status():
    conn = get_conn()
    total = conn.execute("SELECT COUNT(*) FROM reference_comments").fetchone()[0]
    by_type = conn.execute(
        "SELECT post_type, COUNT(*) as cnt FROM reference_comments GROUP BY post_type ORDER BY cnt DESC LIMIT 10"
    ).fetchall()
    conn.close()
    return {"total": total, "by_type": {r[0]: r[1] for r in by_type}}
