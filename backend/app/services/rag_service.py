"""RAG — SQLite-based retrieval of high-engagement reference comments"""
import logging
from app.db.database import get_conn

log = logging.getLogger("rag")


def get_examples(post_type: str, topic: str = "", limit: int = 5) -> list[dict]:
    try:
        conn = get_conn()
        rows = conn.execute(
            "SELECT comment_text, post_content, comment_angle, engagement_score, likes "
            "FROM reference_comments WHERE post_type = ? ORDER BY engagement_score DESC LIMIT ?",
            (post_type, limit)
        ).fetchall()

        if len(rows) < 3 and topic:
            keywords = [w for w in topic.split() if len(w) > 3]
            if keywords:
                clause = " OR ".join(["post_content LIKE ?" for _ in keywords])
                params = [f"%{k}%" for k in keywords] + [limit - len(rows)]
                more = conn.execute(
                    f"SELECT comment_text, post_content, comment_angle, engagement_score, likes "
                    f"FROM reference_comments WHERE {clause} ORDER BY engagement_score DESC LIMIT ?",
                    params
                ).fetchall()
                rows = list(rows) + list(more)

        conn.close()
        results = [dict(r) for r in rows]
        log.info(f"RAG: {len(results)} examples for type='{post_type}'")
        return results
    except Exception as e:
        log.error(f"RAG error: {e}")
        return []


def format_for_prompt(examples: list[dict]) -> str:
    if not examples:
        return ""
    lines = ["\n===== HIGH-ENGAGEMENT EXAMPLES =====",
             "Learn from these real comments that got high engagement:\n"]
    for i, ex in enumerate(examples):
        lines.append(f"Example {i+1}: {ex.get('comment_angle', 'GENERAL')}")
        lines.append(f"Post: \"{str(ex.get('post_content', ''))[:150]}...\"")
        lines.append(f"Comment: \"{ex.get('comment_text', '')}\"")
        lines.append(f"Engagement: {ex.get('likes', 0)} likes\n")
    lines.append("===== END EXAMPLES =====")
    return "\n".join(lines)
