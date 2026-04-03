"""Web Search — SerpAPI"""
import os
import httpx
import logging

log = logging.getLogger("search")

NO_SEARCH = {"gratitude_inspirational", "celebration_win", "hiring_team", "self_promo_pitch", "milestone_announcement"}
YES_SEARCH = {"advice_tactical", "hot_take_controversial", "philosophical_abstract", "reflective_lessons"}


def should_search(post_type: str) -> bool:
    if not os.getenv("SERPAPI_KEY"):
        return False
    if post_type in NO_SEARCH:
        return False
    return post_type in YES_SEARCH


async def search(topic: str, details: list[str] = [], post_type: str = "") -> dict:
    key = os.getenv("SERPAPI_KEY", "")
    if not key:
        return {"query": "", "results": []}

    detail_str = " ".join(details[:2])
    query = f"{topic} {detail_str} 2026".strip()
    log.info(f"SerpAPI search: '{query}'")

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get("https://serpapi.com/search.json", params={
                "api_key": key, "q": query, "engine": "google", "num": "3",
            })
        data = resp.json()
        results = [{"title": r.get("title", ""), "snippet": r.get("snippet", ""), "url": r.get("link", "")}
                   for r in data.get("organic_results", [])[:3]]
        log.info(f"Search returned {len(results)} results")
        return {"query": query, "results": results}
    except Exception as e:
        log.error(f"Search error: {e}")
        return {"query": query, "results": []}


def format_for_prompt(ctx: dict) -> str:
    if not ctx.get("results"):
        return ""
    lines = [f"\n===== WEB CONTEXT =====\nTopic: \"{ctx['query']}\"\n"]
    for r in ctx["results"]:
        lines.append(f"- {r['title']}\n  {r['snippet']}\n")
    lines.append("Use these insights naturally if relevant.\n===== END =====")
    return "\n".join(lines)
