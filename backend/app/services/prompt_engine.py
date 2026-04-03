"""Dynamic Prompt Engine — builds the master generation prompt"""

WORD_TARGETS = {
    "celebration_win": (15, 30, 40),
    "milestone_announcement": (20, 35, 45),
    "advice_tactical": (35, 50, 65),
    "reflective_lessons": (35, 50, 65),
    "hot_take_controversial": (40, 55, 70),
    "crowd_engagement": (25, 40, 55),
    "failure_setback": (30, 45, 60),
    "vulnerable_emotional": (25, 40, 55),
    "default": (30, 45, 60),
}

TONE_INSTRUCTIONS = {
    "casual_conversational": "Post is CASUAL — short sentences, informal. Match: short sentences, casual words, no corporate speak.",
    "formal_professional": "Post is FORMAL. Be polished but still human. Don't out-formal the post.",
    "listicle_breakdown": "Post uses LISTS. Your comment should be flowing text (NOT a list). Pick ONE item and go deeper.",
    "storytelling_narrative": "Post TELLS A STORY. Respond to the emotional core. Share a parallel experience.",
    "data_heavy": "Post is DATA-HEAVY. Engage with the data: add context, question it, or share related stats.",
    "motivational_inspirational": "Post is MOTIVATIONAL. Add substance — a specific example or counterpoint. Don't just agree.",
    "humorous_witty": "Post is FUNNY. Match the energy — be playful, add to the joke. Don't be the serious person.",
}

ANGLE_INSTRUCTIONS = {
    "WHISPERED_TRUTH": "Share the insider truth others won't mention. Be direct, not preachy.",
    "HIDDEN_COST": "Point out a hidden cost/catch nobody mentions. Acknowledge first, then reveal.",
    "SECRET_NOBODY_ASKED": "Share insider knowledge only real experience gives. Keep tactical.",
    "LIVED_IT_DEEPER": "Share your harder/deeper version. Show what you learned. Don't one-up.",
    "ME_TOO_DEEPER": "Go beyond 'me too' — share SPECIFIC parallel experience + discovery.",
    "MINDSET_SHIFT": "Reframe with a completely different lens. Show a new perspective.",
    "INEVITABLE_NOT_SURPRISING": "Make it feel like natural progression. Ask forward-looking question. Keep SHORT.",
    "CALL_OUT_VALUE": "Name the SPECIFIC value — why it matters. Direct, no fluff. SHORT.",
    "ASK_QUESTION": "Ask a genuine, tactical, specific question. Show deeper thinking.",
    "SHARE_EXPERIENCE": "Share parallel experience with specific data/results/timeframes.",
    "ADD_DATA": "Contribute a relevant data point or metric. Natural and connected.",
    "INTENSIFY_SURGICAL": "Take their best insight and sharpen it. Add evidence or killer example.",
    "REFRAME_SMARTER": "Offer a better perspective. Acknowledge original, then present yours.",
    "EARNED_INSIGHT": "Share wisdom earned through experience. Apply to their situation.",
    "REAL_RISK": "Identify the actual risk nobody's talking about. Short, punchy. Sharp question.",
    "FAILURE_AS_CURRICULUM": "Frame failure as learning. Normalize it, extract the lesson.",
    "SEE_WHOLE_GAME": "Zoom out — connect to a larger trend. Show how pieces fit.",
    "VALIDATION": "Simple, genuine acknowledgment. Short (15-25 words), specific, no fluff.",
}

VARIATION_STRUCTURES = [
    "Start with a direct statement or observation. No questions to start. Flowing single thought.",
    "Start from personal experience — 'we saw this when...' Build to your insight.",
    "Start with a flip or question — challenge a common assumption, then reveal your take.",
]


def build_prompt(
    post_text: str,
    analysis: dict,
    profile: dict,
    angle: str,
    variation: int,
    rag_context: str = "",
    web_context: str = "",
    author: dict | None = None,
) -> str:
    post_type = analysis.get("post_type", "advice_tactical")
    mn, target, mx = WORD_TARGETS.get(post_type, WORD_TARGETS["default"])
    details = ", ".join(analysis.get("specific_details", [])[:3]) or analysis.get("main_topic", "the topic")
    expertise = ", ".join(profile.get("expertise", ["professional"])[:3])
    tone_instr = TONE_INSTRUCTIONS.get(analysis.get("post_tone", ""), TONE_INSTRUCTIONS["casual_conversational"])
    angle_instr = ANGLE_INSTRUCTIONS.get(angle, f"Engage with the post using {angle} angle.")
    var_instr = VARIATION_STRUCTURES[variation % len(VARIATION_STRUCTURES)]

    examples = profile.get("real_comment_examples", [])
    examples_str = "\n".join(f'   {i+1}. "{ex}"' for i, ex in enumerate(examples[:5])) if examples else ""
    phrases_str = "\n".join(f'   - "{p}"' for p in profile.get("common_phrases", [])[:5])

    author_section = ""
    if author:
        author_section = f"""
POST AUTHOR:
Name: {author.get('name', '')}
Role: {author.get('headline', '')}
→ Comment should match the level of this audience."""

    prompt = f"""You are writing a LinkedIn comment as a REAL person. Your comment will be posted publicly.

{'='*70}
POST TO COMMENT ON:
{'='*70}
{post_text[:1500]}
{author_section}

Post Type: {post_type}
Topic: {analysis.get('main_topic', '')}
Key Details: {details}

{'='*70}
WHO YOU ARE (the commenter):
{'='*70}
Name: {profile.get('name', 'Professional')}
{f"Headline: {profile.get('headline', '')}" if profile.get('headline') else ""}
Tone: {profile.get('tone', 'professional, direct')}
Expertise: {expertise}

→ Your comment should reflect YOUR expertise. A {expertise} expert notices different things than a general reader.

{f"YOUR REAL COMMENTS (match this voice):{chr(10)}{examples_str}" if examples_str else ""}
{f"YOUR SIGNATURE PHRASES:{chr(10)}{phrases_str}" if phrases_str else ""}

{'='*70}
COMMENT STRATEGY:
{'='*70}
ANGLE: {angle}
{angle_instr}

VARIATION {variation+1} INSTRUCTION:
STRUCTURE: {var_instr}

{'='*70}
TONE MATCHING (CRITICAL):
{'='*70}
{tone_instr}

{'='*70}
RULES:
{'='*70}
LENGTH: {mn}-{mx} words (target: {target})

MUST:
- Reference specific details: {details}
- Sound like a real {expertise} professional
- Match the post's writing energy

BANNED:
- "Great post!", "Congrats!", "Love this!", "Well said!", "So true!"
- Words: leverage, navigate, unlock, delve, foster, robust, seamless, holistic, innovative, transformative
- Phrases: "it's worth noting", "in today's", "couldn't agree more", "this resonates deeply"
- Starting with "I" every time
- Exclamation marks
- Under 10 words
- Sounding like ChatGPT

{'='*70}
OUTPUT:
{'='*70}
Write ONE comment. Output ONLY the comment text. No quotes. No preamble."""

    if rag_context:
        prompt += "\n\n" + rag_context
    if web_context:
        prompt += "\n\n" + web_context
    return prompt
