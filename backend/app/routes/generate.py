"""Generate comments — runs the full LangGraph pipeline"""
import json
import logging
from fastapi import APIRouter
from app.models.schemas import GenerateRequest
from app.db.database import get_conn
from app.graph.pipeline import get_pipeline

log = logging.getLogger("api")
router = APIRouter()


@router.post("/api/generate-comments")
async def generate_comments(req: GenerateRequest):
    conn = get_conn()

    # Load post
    post = conn.execute("SELECT * FROM scraped_posts WHERE id = ?", (req.post_id,)).fetchone()
    if not post:
        conn.close()
        return {"error": "Post not found"}, 404

    # Load commenter profile
    profile_row = conn.execute(
        "SELECT * FROM commenter_profiles WHERE is_active = 1"
    ).fetchone()

    profile = {
        "name": "Professional", "username": "default",
        "expertise": ["technology", "business"],
        "tone": "professional, direct",
        "avg_comment_length": 45,
        "common_phrases": [], "real_comment_examples": [],
    }
    if profile_row:
        try:
            pd = json.loads(profile_row["profile_data"] or "{}")
            profile = {
                "name": profile_row["name"],
                "username": profile_row["username"],
                "headline": profile_row["headline"] or "",
                "expertise": pd.get("expertise", profile["expertise"]),
                "tone": pd.get("tone", profile["tone"]),
                "avg_comment_length": pd.get("avgCommentLength", 45),
                "common_phrases": pd.get("commonPhrases", []),
                "real_comment_examples": pd.get("realCommentExamples", []),
                "humor_style": pd.get("humorStyle"),
            }
            log.info(f"Commenter: {profile['name']} | {profile['tone']}")
        except:
            log.warning("Failed to parse commenter profile")

    media = []
    try:
        media = json.loads(post["media_urls"] or "[]")
    except:
        pass

    # Run LangGraph pipeline
    log.info("=" * 70)
    log.info(f"RUNNING PIPELINE for post #{req.post_id}")
    log.info("=" * 70)

    pipeline = get_pipeline()

    initial_state = {
        "post_id": req.post_id,
        "post_text": post["post_text"] or "",
        "post_author": {
            "name": post["author_name"] or "",
            "headline": post["author_headline"] or "",
        },
        "media": media,
        "analysis": {},
        "web_context": "",
        "rag_context": "",
        "rag_angles": [],
        "profile": profile,
        "comments": [],
        "retry_count": 0,
        "errors": [],
    }

    # Execute the graph
    result = await pipeline.ainvoke(initial_state)

    # Get the final comments (take last 3 — after retry the list may have more)
    all_comments = result.get("comments", [])
    # Filter to only validated ones (have quality_score)
    validated = [c for c in all_comments if "quality_score" in c]
    # Take best 3
    final = sorted(validated, key=lambda c: c.get("confidence", 0), reverse=True)[:3]

    # Re-number variations
    for i, c in enumerate(final):
        c["variation"] = i + 1

    log.info("=" * 70)
    log.info(f"PIPELINE COMPLETE: {len(final)} comments")
    for c in final:
        log.info(f"  [{c['angle']}] ({c['word_count']}w, {int(c['confidence']*100)}%) \"{c['text'][:60]}...\"")
    log.info("=" * 70)

    # Save to DB
    analysis = result.get("analysis", {})
    conn.execute(
        "UPDATE scraped_posts SET post_analysis = ?, web_search_context = ?, status = 'generated' WHERE id = ?",
        (json.dumps(analysis), result.get("web_context", ""), req.post_id)
    )

    for c in final:
        conn.execute(
            "INSERT INTO generated_comments (post_id, text, angle, variation_number, confidence, approach, post_type, was_humanized, quality_score) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (req.post_id, c["text"], c["angle"], c["variation"], c["confidence"],
             "langgraph", analysis.get("post_type", ""), 1, c["quality_score"])
        )

    conn.commit()
    conn.close()

    return {
        "success": True,
        "post_id": req.post_id,
        "count": len(final),
        "analysis": analysis,
        "comments": final,
    }
