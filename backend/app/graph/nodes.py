"""LangGraph Nodes — each step of the pipeline"""
import os
import re
import json
import logging
import asyncio
from groq import Groq
from app.services.web_search import should_search, search, format_for_prompt
from app.services.rag_service import get_examples, format_for_prompt as rag_fmt
from app.services.prompt_engine import build_prompt, WORD_TARGETS
from app.services.humanizer import humanize
from app.graph.state import PipelineState

log = logging.getLogger("graph")

ANGLE_PREFERENCES = {
    "advice_tactical": ["WHISPERED_TRUTH", "HIDDEN_COST", "SECRET_NOBODY_ASKED"],
    "reflective_lessons": ["ME_TOO_DEEPER", "MINDSET_SHIFT", "LIVED_IT_DEEPER"],
    "celebration_win": ["INEVITABLE_NOT_SURPRISING", "REAL_COST", "CALL_OUT_VALUE"],
    "milestone_announcement": ["INEVITABLE_NOT_SURPRISING", "CALL_OUT_VALUE", "SEE_WHOLE_GAME"],
    "crowd_engagement": ["ASK_QUESTION", "SHARE_EXPERIENCE", "ADD_DATA"],
    "hot_take_controversial": ["INTENSIFY_SURGICAL", "SEE_WHOLE_GAME", "REFRAME_SMARTER"],
    "failure_setback": ["FAILURE_AS_CURRICULUM", "LIVED_IT_DEEPER", "REAL_RISK"],
}

AI_PHRASES = [
    "it's worth noting", "in today's", "couldn't agree more",
    "this resonates deeply", "at the end of the day", "spot on",
]


def _groq():
    return Groq(api_key=os.getenv("GROQ_API_KEY", ""))


# ==============================
# NODE 1: Analyze Post
# ==============================
async def analyze_node(state: PipelineState) -> dict:
    log.info("=" * 60)
    log.info("NODE: ANALYZE POST")
    log.info("=" * 60)

    post_text = state["post_text"]
    author = state.get("post_author", {})

    author_ctx = f"\nPOST AUTHOR: {author.get('name','')} — {author.get('headline','')}\n" if author.get("name") else ""

    prompt = f"""Analyze this LinkedIn post.
{author_ctx}
POST:
{post_text[:1500]}

Return ONLY valid JSON:
{{
  "post_type": "advice_tactical|reflective_lessons|celebration_win|crowd_engagement|hot_take_controversial|milestone_announcement|failure_setback|vulnerable_emotional|hiring_team",
  "main_topic": "3-5 words",
  "sentiment": "positive|negative|neutral",
  "emotional_tone": "one word",
  "post_tone": "casual_conversational|formal_professional|listicle_breakdown|storytelling_narrative|data_heavy|motivational_inspirational|humorous_witty",
  "specific_details": ["detail1", "detail2", "detail3"],
  "key_insights": ["insight1", "insight2"],
  "best_response_angles": ["ANGLE_1", "ANGLE_2", "ANGLE_3"]
}}"""

    log.info(f"[PROMPT → Groq] Analysis prompt: {len(prompt)} chars")

    client = _groq()
    resp = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        temperature=0.3,
        max_completion_tokens=1000,
        response_format={"type": "json_object"},
        messages=[{"role": "user", "content": prompt}],
    )
    raw = resp.choices[0].message.content or "{}"
    log.info(f"[RESPONSE ← Groq] {len(raw)} chars | tokens: {resp.usage.prompt_tokens}→{resp.usage.completion_tokens}")

    try:
        analysis = json.loads(raw)
    except:
        analysis = {"post_type": "advice_tactical", "main_topic": "general", "sentiment": "neutral",
                     "emotional_tone": "thoughtful", "post_tone": "casual_conversational",
                     "specific_details": [], "key_insights": [], "best_response_angles": []}

    log.info(f"Analysis: type={analysis.get('post_type')} | tone={analysis.get('post_tone')} | topic={analysis.get('main_topic')}")
    return {"analysis": analysis}


# ==============================
# NODE 2: Web Search
# ==============================
async def search_node(state: PipelineState) -> dict:
    analysis = state.get("analysis", {})
    post_type = analysis.get("post_type", "")

    if not should_search(post_type):
        log.info(f"NODE: SEARCH — skipped (type={post_type})")
        return {"web_context": ""}

    log.info("=" * 60)
    log.info("NODE: WEB SEARCH")
    log.info("=" * 60)

    result = await search(
        analysis.get("main_topic", ""),
        analysis.get("specific_details", []),
        post_type,
    )
    ctx = format_for_prompt(result)
    log.info(f"Web context: {len(ctx)} chars")
    return {"web_context": ctx}


# ==============================
# NODE 3: RAG Retrieval
# ==============================
async def rag_node(state: PipelineState) -> dict:
    log.info("=" * 60)
    log.info("NODE: RAG RETRIEVAL")
    log.info("=" * 60)

    analysis = state.get("analysis", {})
    examples = get_examples(analysis.get("post_type", ""), analysis.get("main_topic", ""))
    ctx = rag_fmt(examples)

    # Extract angles from RAG
    angles = []
    for ex in examples:
        a = ex.get("comment_angle", "")
        if a and a not in angles:
            angles.append(a)

    log.info(f"RAG: {len(examples)} examples | angles: {angles[:5]}")
    return {"rag_context": ctx, "rag_angles": angles}


# ==============================
# NODE 4: Generate 3 Comments (PARALLEL)
# ==============================
async def generate_node(state: PipelineState) -> dict:
    log.info("=" * 60)
    log.info("NODE: GENERATE COMMENTS (PARALLEL)")
    log.info("=" * 60)

    analysis = state.get("analysis", {})
    profile = state.get("profile", {})
    rag_angles = state.get("rag_angles", [])
    post_type = analysis.get("post_type", "advice_tactical")

    # Select 3 angles
    angles = []
    for i in range(3):
        if i < len(rag_angles):
            angles.append(rag_angles[i])
        elif i < len(analysis.get("best_response_angles", [])):
            a = analysis["best_response_angles"][i]
            if a in ANGLE_PREFERENCES.get(post_type, []) or len(a) > 3:
                angles.append(a)
            else:
                prefs = ANGLE_PREFERENCES.get(post_type, ["WHISPERED_TRUTH", "HIDDEN_COST", "EARNED_INSIGHT"])
                angles.append(prefs[i % len(prefs)])
        else:
            prefs = ANGLE_PREFERENCES.get(post_type, ["WHISPERED_TRUTH", "HIDDEN_COST", "EARNED_INSIGHT"])
            angles.append(prefs[i % len(prefs)])

    log.info(f"Angles: {angles}")

    # Build prompts for all 3
    tasks = []
    for i, angle in enumerate(angles):
        prompt = build_prompt(
            state["post_text"], analysis, profile, angle, i,
            state.get("rag_context", ""), state.get("web_context", ""),
            state.get("post_author"),
        )
        temp = 0.7 + i * 0.15
        log.info(f"[Variation {i+1}] angle={angle} | temp={temp:.2f} | prompt={len(prompt)} chars")
        tasks.append(_generate_one(prompt, angle, i, temp))

    # Run all 3 in parallel
    results = await asyncio.gather(*tasks, return_exceptions=True)

    comments = []
    for r in results:
        if isinstance(r, Exception):
            log.error(f"Generation failed: {r}")
        elif r:
            comments.append(r)

    log.info(f"Generated {len(comments)} raw comments")
    return {"comments": comments}


async def _generate_one(prompt: str, angle: str, variation: int, temperature: float) -> dict | None:
    try:
        client = _groq()
        resp = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            temperature=temperature,
            max_completion_tokens=500,
            messages=[{"role": "user", "content": prompt}],
        )
        raw = resp.choices[0].message.content or ""
        tokens_in = resp.usage.prompt_tokens
        tokens_out = resp.usage.completion_tokens

        # Clean
        text = raw.strip().strip('"\'').replace("**", "")
        for prefix in ["comment:", "response:", "output:", "here's my comment:"]:
            if text.lower().startswith(prefix):
                text = text[len(prefix):].strip()
        text = " ".join(text.split())

        log.info(f"[Variation {variation+1}] [{angle}] tokens: {tokens_in}→{tokens_out}")
        log.info(f"[Variation {variation+1}] Raw: \"{text}\"")

        return {
            "text": text,
            "angle": angle,
            "variation": variation + 1,
            "raw_text": text,
            "tokens_in": tokens_in,
            "tokens_out": tokens_out,
        }
    except Exception as e:
        log.error(f"[Variation {variation+1}] Error: {e}")
        return None


# ==============================
# NODE 5: Humanize + Validate
# ==============================
async def humanize_validate_node(state: PipelineState) -> dict:
    log.info("=" * 60)
    log.info("NODE: HUMANIZE + VALIDATE")
    log.info("=" * 60)

    profile = state.get("profile", {})
    analysis = state.get("analysis", {})
    post_type = analysis.get("post_type", "advice_tactical")
    rag_angles = state.get("rag_angles", [])
    mn, target, mx = WORD_TARGETS.get(post_type, WORD_TARGETS["default"])

    validated = []
    for c in state.get("comments", []):
        if not c or not c.get("text"):
            continue

        # Humanize
        original = c["text"]
        humanized = humanize(original, profile.get("tone", "professional"), profile.get("avg_comment_length", 45))
        log.info(f"[{c['angle']}] Humanized: \"{humanized}\"")

        # Validate
        wc = len(humanized.split())
        quality = 100
        issues, warnings = [], []

        if wc < mn - 15:
            issues.append(f"Too short: {wc}w"); quality -= 40
        elif wc > mx + 15:
            issues.append(f"Too long: {wc}w"); quality -= 40
        elif wc < mn:
            warnings.append(f"Below target: {wc}w"); quality -= 15
        elif wc > mx:
            warnings.append(f"Above target: {wc}w"); quality -= 15

        ai_count = sum(1 for p in AI_PHRASES if p in humanized.lower())
        if ai_count:
            warnings.append(f"{ai_count} AI phrases"); quality -= ai_count * 10
        quality = max(0, quality)

        # Confidence
        conf = (quality / 100) * 0.4
        conf += 0.30 if c["angle"] in rag_angles else 0.10
        conf += 0.15  # humanized
        conf += 0.10 if abs(wc - target) <= 5 else 0.06 if abs(wc - target) <= 10 else 0.03
        conf += 0.05 if not issues else 0
        conf = min(conf, 0.99)

        log.info(f"[{c['angle']}] quality={quality} | {wc}w ({mn}-{mx}) | confidence={conf:.0%}")

        validated.append({
            "text": humanized,
            "angle": c["angle"],
            "variation": c["variation"],
            "confidence": round(conf, 2),
            "quality_score": quality,
            "word_count": wc,
            "humanized": True,
            "issues": issues,
            "warnings": warnings,
        })

    # Replace comments with validated ones
    # Since comments uses operator.add, we return the validated list
    # But we need to clear old ones — we'll handle this in the pipeline
    return {"comments": validated}


# ==============================
# NODE 6: Retry (conditional)
# ==============================
async def retry_node(state: PipelineState) -> dict:
    """Check if any comment needs retry (quality < 50)"""
    comments = state.get("comments", [])
    retry_count = state.get("retry_count", 0)

    bad = [c for c in comments if c.get("quality_score", 100) < 50]

    if not bad or retry_count >= 2:
        if bad:
            log.warn(f"RETRY: {len(bad)} low quality but max retries reached")
        return {"retry_count": retry_count}

    log.info(f"RETRY: {len(bad)} comments below quality threshold, regenerating...")
    return {"retry_count": retry_count + 1}


def should_retry(state: PipelineState) -> str:
    """Conditional edge: retry or finish"""
    comments = state.get("comments", [])
    retry_count = state.get("retry_count", 0)

    bad = [c for c in comments if c.get("quality_score", 100) < 50]

    if bad and retry_count < 2:
        return "retry"
    return "done"
