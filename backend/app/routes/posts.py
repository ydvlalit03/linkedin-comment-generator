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
        raw = json.loads(post["post_analysis"] or "null")
        if raw:
            analysis = {
                "postType":             raw.get("post_type", ""),
                "mainTopic":            raw.get("main_topic", ""),
                "sentiment":            raw.get("sentiment", ""),
                "emotionalTone":        raw.get("emotional_tone", ""),
                "postTone":             raw.get("post_tone", ""),
                "suggestedCommentTone": raw.get("suggested_comment_tone", ""),
                "specificDetails":      raw.get("specific_details", []),
                "keyInsights":          raw.get("key_insights", []),
                "bestResponseAngles":   raw.get("best_response_angles", []),
            }
    except:
        pass

    media = []
    try:
        media = json.loads(post["media_urls"] or "[]")
    except:
        pass

    # Extract suggested_comment_tone from analysis for the UI
    suggested_tone = analysis.get("suggestedCommentTone", "") if analysis else ""

    # Get the tone used in most recent batch of comments
    used_tone = ""
    if comments:
        used_tone = comments[-1]["comment_tone"] if "comment_tone" in comments[-1].keys() else ""

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
        "suggestedCommentTone": suggested_tone,
        "usedCommentTone": used_tone,
        "comments": [
            {
                "id": c["id"], "text": c["text"], "angle": c["angle"],
                "variationNumber": c["variation_number"],
                "confidence": c["confidence"], "approach": c["approach"],
                "postType": c["post_type"],
                "commentTone": c["comment_tone"] if "comment_tone" in c.keys() else "",
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


@router.put("/api/comments/{comment_id}")
async def update_comment(comment_id: int, data: dict):
    """Update comment text (inline edit)"""
    conn = get_conn()
    text = data.get("text", "").strip()
    if not text:
        conn.close()
        return {"error": "Text required"}, 400
    conn.execute("UPDATE generated_comments SET text = ? WHERE id = ?", (text, comment_id))
    conn.commit()
    conn.close()
    return {"success": True}


@router.get("/api/analytics")
async def get_analytics():
    """Analytics data for the dashboard"""
    init_db()
    conn = get_conn()

    total_posts = conn.execute("SELECT COUNT(*) FROM scraped_posts").fetchone()[0]
    total_comments = conn.execute("SELECT COUNT(*) FROM generated_comments").fetchone()[0]
    total_feedback = conn.execute("SELECT COUNT(*) FROM comment_feedback").fetchone()[0]

    # Angle performance: count + avg confidence + avg quality
    angle_rows = conn.execute("""
        SELECT angle, COUNT(*) as count,
               ROUND(AVG(confidence), 2) as avg_confidence,
               ROUND(AVG(quality_score), 1) as avg_quality
        FROM generated_comments
        GROUP BY angle
        ORDER BY count DESC
    """).fetchall()

    # Post type distribution
    post_type_rows = conn.execute("""
        SELECT post_type, COUNT(*) as count
        FROM generated_comments
        WHERE post_type != ''
        GROUP BY post_type
        ORDER BY count DESC
    """).fetchall()

    # Quality distribution
    quality_rows = conn.execute("""
        SELECT
            SUM(CASE WHEN quality_score >= 80 THEN 1 ELSE 0 END) as excellent,
            SUM(CASE WHEN quality_score >= 60 AND quality_score < 80 THEN 1 ELSE 0 END) as good,
            SUM(CASE WHEN quality_score >= 40 AND quality_score < 60 THEN 1 ELSE 0 END) as fair,
            SUM(CASE WHEN quality_score < 40 THEN 1 ELSE 0 END) as poor
        FROM generated_comments
    """).fetchone()

    # Tone distribution
    tone_rows = conn.execute("""
        SELECT comment_tone, COUNT(*) as count
        FROM generated_comments
        WHERE comment_tone != ''
        GROUP BY comment_tone
        ORDER BY count DESC
    """).fetchall()

    # Feedback stats
    feedback_rows = conn.execute("""
        SELECT
            SUM(CASE WHEN rating = 1 THEN 1 ELSE 0 END) as positive,
            SUM(CASE WHEN rating = -1 THEN 1 ELSE 0 END) as negative,
            SUM(CASE WHEN rating = 0 THEN 1 ELSE 0 END) as neutral
        FROM comment_feedback
    """).fetchone()

    # Avg confidence overall
    avg_conf_row = conn.execute("SELECT ROUND(AVG(confidence), 2) FROM generated_comments").fetchone()
    avg_confidence = avg_conf_row[0] or 0

    conn.close()

    return {
        "totals": {
            "posts": total_posts,
            "comments": total_comments,
            "feedback": total_feedback,
            "avgConfidence": avg_confidence,
        },
        "angles": [
            {"angle": r["angle"], "count": r["count"],
             "avgConfidence": r["avg_confidence"], "avgQuality": r["avg_quality"]}
            for r in angle_rows
        ],
        "postTypes": [{"postType": r["post_type"], "count": r["count"]} for r in post_type_rows],
        "qualityDistribution": {
            "excellent": quality_rows["excellent"] or 0,
            "good": quality_rows["good"] or 0,
            "fair": quality_rows["fair"] or 0,
            "poor": quality_rows["poor"] or 0,
        } if quality_rows else {"excellent": 0, "good": 0, "fair": 0, "poor": 0},
        "tones": [{"tone": r["comment_tone"], "count": r["count"]} for r in tone_rows],
        "feedback": {
            "positive": feedback_rows["positive"] or 0,
            "negative": feedback_rows["negative"] or 0,
            "neutral": feedback_rows["neutral"] or 0,
        } if feedback_rows else {"positive": 0, "negative": 0, "neutral": 0},
    }


@router.get("/api/rag-status")
async def rag_status():
    conn = get_conn()
    total = conn.execute("SELECT COUNT(*) FROM reference_comments").fetchone()[0]
    by_type = conn.execute(
        "SELECT post_type, COUNT(*) as cnt FROM reference_comments GROUP BY post_type ORDER BY cnt DESC LIMIT 10"
    ).fetchall()
    conn.close()
    return {"total": total, "by_type": {r[0]: r[1] for r in by_type}}
