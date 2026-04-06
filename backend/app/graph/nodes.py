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

VALID_ANGLES = {
    "INEVITABLE_NOT_SURPRISING", "REAL_COST", "FAILURE_AS_CURRICULUM",
    "LIVED_IT_DEEPER", "WHISPERED_TRUTH", "EARNED_INSIGHT",
    "ME_TOO_DEEPER", "HIDDEN_COST", "MINDSET_SHIFT", "REAL_RISK",
    "SECRET_NOBODY_ASKED", "INTENSIFY_SURGICAL", "SEE_WHOLE_GAME",
    "PATTERN_NOT_MAD", "VALIDATION", "SHARE_EXPERIENCE",
    "ADD_DATA", "ASK_QUESTION", "REFRAME_SMARTER",
    "CALL_OUT_VALUE", "GENERAL_ENGAGEMENT",
}

ANGLE_PREFERENCES = {
    "advice_tactical": ["WHISPERED_TRUTH", "HIDDEN_COST", "SECRET_NOBODY_ASKED"],
    "reflective_lessons": ["ME_TOO_DEEPER", "MINDSET_SHIFT", "LIVED_IT_DEEPER"],
    "celebration_win": ["INEVITABLE_NOT_SURPRISING", "CALL_OUT_VALUE", "VALIDATION"],
    "milestone_announcement": ["INEVITABLE_NOT_SURPRISING", "CALL_OUT_VALUE", "SEE_WHOLE_GAME"],
    "crowd_engagement": ["ASK_QUESTION", "SHARE_EXPERIENCE", "ADD_DATA"],
    "hot_take_controversial": ["INTENSIFY_SURGICAL", "SEE_WHOLE_GAME", "REFRAME_SMARTER"],
    "failure_setback": ["FAILURE_AS_CURRICULUM", "LIVED_IT_DEEPER", "REAL_RISK"],
    "vulnerable_emotional": ["ME_TOO_DEEPER", "VALIDATION", "EARNED_INSIGHT"],
    "self_promo_pitch": ["ASK_QUESTION", "CALL_OUT_VALUE", "SHARE_EXPERIENCE"],
    "gratitude_inspirational": ["VALIDATION", "CALL_OUT_VALUE", "ME_TOO_DEEPER"],
    "hiring_team": ["CALL_OUT_VALUE", "ASK_QUESTION", "SHARE_EXPERIENCE"],
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
  "suggested_comment_tone": "humorous|empathetic|inspirational|provocative|analytical|celebratory|direct|storytelling",
  "specific_details": ["detail1", "detail2", "detail3"],
  "key_insights": ["insight1", "insight2"],
  "best_response_angles": ["ANGLE_1", "ANGLE_2", "ANGLE_3"]
}}

For suggested_comment_tone: pick the tone that would make the BEST comment on this specific post.
- humorous: post is light/funny or a witty reply would stand out
- empathetic: post is vulnerable/emotional/failure — warm tone fits
- inspirational: post is motivational — uplift and energize
- provocative: post is a hot take — challenge or intensify
- analytical: post is data/advice-heavy — break it down logically
- celebratory: post is a win/milestone — celebrate genuinely
- direct: post is tactical/instructional — be straight and sharp
- storytelling: post is a narrative — respond with your own story"""

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
                     "suggested_comment_tone": "direct",
                     "specific_details": [], "key_insights": [], "best_response_angles": []}

    # If user hasn't overridden tone, use LLM suggestion
    suggested = analysis.get("suggested_comment_tone", "direct")
    existing_tone = state.get("comment_tone", "")
    resolved_tone = existing_tone if existing_tone else suggested

    log.info(f"Analysis: type={analysis.get('post_type')} | post_tone={analysis.get('post_tone')} | suggested_comment_tone={suggested} | resolved={resolved_tone}")
    return {"analysis": analysis, "comment_tone": resolved_tone}


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

    # Select 3 angles — ONLY from our defined set
    angles = []
    # Filter RAG angles to valid ones only
    valid_rag = [a for a in rag_angles if a in VALID_ANGLES]
    # Filter AI-suggested angles to valid ones only
    ai_angles = [a for a in analysis.get("best_response_angles", []) if a in VALID_ANGLES]
    # Post type defaults
    prefs = ANGLE_PREFERENCES.get(post_type, ["WHISPERED_TRUTH", "HIDDEN_COST", "EARNED_INSIGHT"])

    for i in range(3):
        if i < len(valid_rag):
            angles.append(valid_rag[i])
        elif i < len(ai_angles):
            angles.append(ai_angles[i])
        else:
            angles.append(prefs[i % len(prefs)])

    # Deduplicate — no repeat angles
    seen = set()
    unique = []
    for a in angles:
        if a not in seen:
            seen.add(a)
            unique.append(a)
    while len(unique) < 3:
        for p in prefs:
            if p not in seen:
                seen.add(p)
                unique.append(p)
                if len(unique) >= 3:
                    break
    angles = unique[:3]

    log.info(f"Angles: {angles}")

    comment_tone = state.get("comment_tone", "direct")
    log.info(f"Comment tone: {comment_tone}")

    # Build prompts for all 3
    tasks = []
    for i, angle in enumerate(angles):
        prompt = build_prompt(
            state["post_text"], analysis, profile, angle, i,
            state.get("rag_context", ""), state.get("web_context", ""),
            state.get("post_author"), comment_tone,
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
