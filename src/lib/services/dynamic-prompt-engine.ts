/**
 * Dynamic Prompt Engine — builds the master generation prompt
 *
 * Fixes applied:
 * - Post author context injected
 * - Post writing tone matching
 * - Angle/variation conflict resolved (variation overrides angle opener)
 * - Better commenter identity section
 * - Smarter search query builder
 */
import { SENTIMENT_PATTERNS, WORD_COUNT_TARGETS } from "../data/comment-angles";
import type { PostAnalysis, CommenterProfile } from "../types";

export function detectSentiment(postContent: string): string {
  const postLower = postContent.toLowerCase();
  const scores: Record<string, number> = {};
  for (const [type, data] of Object.entries(SENTIMENT_PATTERNS)) {
    scores[type] = data.keywords.filter((kw) => postLower.includes(kw)).length;
  }
  const maxScore = Math.max(...Object.values(scores));
  if (maxScore > 0) return Object.entries(scores).find(([, v]) => v === maxScore)![0];
  return "advice_tactical";
}

/**
 * Build a better search query based on post content
 */
export function buildSearchQuery(postAnalysis: PostAnalysis, postContent: string): string {
  // Extract key nouns/topics from details
  const details = postAnalysis.specificDetails.slice(0, 2).join(" ");
  const topic = postAnalysis.mainTopic;

  // More specific than "latest insights 2026"
  if (postAnalysis.postType === "advice_tactical") {
    return `${topic} ${details} tips data 2025 2026`;
  }
  if (postAnalysis.postType === "hot_take_controversial") {
    return `${topic} debate opinions ${details} 2026`;
  }
  return `${topic} ${details} 2026`.trim();
}

/**
 * Build the master generation prompt
 */
export function buildUltimatePrompt(
  postContent: string,
  postAnalysis: PostAnalysis,
  commenterProfile: CommenterProfile,
  angle: string,
  variation: number = 0,
  ragContext: string = "",
  webContext: string = "",
  authorContext?: { name: string; headline: string; followers?: number }
): string {
  const wordTargets =
    WORD_COUNT_TARGETS[postAnalysis.postType] || WORD_COUNT_TARGETS.default;

  const detailsStr =
    postAnalysis.specificDetails.slice(0, 3).join(", ") || postAnalysis.mainTopic;

  const expertiseStr =
    commenterProfile.expertise.slice(0, 3).join(", ") || "professional";

  const examplesStr = commenterProfile.realCommentExamples
    .slice(0, 5)
    .map((ex, i) => `   ${i + 1}. "${ex}"`)
    .join("\n");

  const phrasesStr = commenterProfile.commonPhrases
    .slice(0, 5)
    .map((p) => `   - "${p}"`)
    .join("\n");

  // Get the variation instruction — this OVERRIDES angle's default opener
  const variationInstruction = getVariationInstruction(angle, variation);

  // Tone matching instruction
  const toneInstruction = getToneMatchInstruction(postAnalysis.postTone);

  // Author context section
  const authorSection = authorContext
    ? `
POST AUTHOR:
Name: ${authorContext.name}
Role: ${authorContext.headline}
${authorContext.followers ? `Followers: ${formatFollowers(authorContext.followers)}` : ""}
→ Comment should match the level of this audience.`
    : "";

  let prompt = `You are writing a LinkedIn comment as a REAL person. Your comment will be posted publicly.

${"=".repeat(70)}
POST TO COMMENT ON:
${"=".repeat(70)}
${postContent.slice(0, 1500)}
${authorSection}

Post Type: ${postAnalysis.postType}
Topic: ${postAnalysis.mainTopic}
Key Details: ${detailsStr}

${"=".repeat(70)}
WHO YOU ARE (the commenter):
${"=".repeat(70)}

Name: ${commenterProfile.name}
${commenterProfile.headline ? `Headline: ${commenterProfile.headline}` : ""}
Tone: ${commenterProfile.tone}
Expertise: ${expertiseStr}
${commenterProfile.humorStyle ? `Humor: ${commenterProfile.humorStyle}` : ""}

→ Your comment should reflect YOUR expertise. A ${expertiseStr} expert notices different things than a general reader.

${examplesStr ? `YOUR REAL COMMENTS (match this voice exactly):
${examplesStr}` : ""}

${phrasesStr ? `YOUR SIGNATURE PHRASES:
${phrasesStr}` : ""}

${"=".repeat(70)}
COMMENT STRATEGY:
${"=".repeat(70)}

ANGLE: ${angle}
${getAngleInstruction(angle, postAnalysis.postType, postAnalysis.specificDetails)}

${variationInstruction}

${"=".repeat(70)}
TONE MATCHING (CRITICAL):
${"=".repeat(70)}
${toneInstruction}

${"=".repeat(70)}
RULES:
${"=".repeat(70)}

LENGTH: ${wordTargets.min}-${wordTargets.max} words (target: ${wordTargets.target})

MUST:
- Reference specific details: ${detailsStr}
- Sound like a real ${expertiseStr} professional
- Match the post's writing energy (${postAnalysis.postTone})

BANNED (instant quality fail):
- "Great post!", "Congrats!", "Love this!", "Well said!", "So true!"
- Words: leverage, navigate, unlock, delve, foster, robust, seamless, holistic, innovative, transformative
- Phrases: "it's worth noting", "in today's", "couldn't agree more", "this resonates deeply", "at the end of the day"
- Starting with "I" for every comment
- Exclamation marks (unless the post itself uses them heavily)
- Writing under 10 words
- Sounding like ChatGPT wrote it

${"=".repeat(70)}
OUTPUT:
${"=".repeat(70)}

Write ONE comment. Output ONLY the comment text.
No quotes. No preamble. No "Here's my comment:" prefix. Just the comment.`;

  if (ragContext) prompt += "\n\n" + ragContext;
  if (webContext) prompt += "\n\n" + webContext;

  return prompt;
}

/**
 * Get tone matching instruction based on how the post is written
 */
function getToneMatchInstruction(postTone: string): string {
  const instructions: Record<string, string> = {
    casual_conversational: `The post is CASUAL — short sentences, informal language, like talking to a friend.
→ Your comment should match: short sentences, casual words, no corporate speak.
→ Think: how would you reply to a friend who said this at coffee?`,

    formal_professional: `The post is FORMAL — structured, professional language.
→ Your comment can be slightly more polished, but still human.
→ Don't out-formal the post — match their level, don't exceed it.`,

    listicle_breakdown: `The post uses LISTS and bullet points — structured, scannable format.
→ Your comment should be flowing text (NOT a list — that copies their format).
→ Pick ONE item from their list and go deeper on it.`,

    storytelling_narrative: `The post TELLS A STORY — narrative arc, personal experience.
→ Your comment should respond to the emotional core of the story.
→ Share a parallel experience or insight that connects to their narrative.`,

    data_heavy: `The post is DATA-HEAVY — numbers, stats, research.
→ Your comment should engage with the data: add context, question methodology, or share related data.
→ Don't ignore the numbers — reference specific ones.`,

    motivational_inspirational: `The post is MOTIVATIONAL — uplifting, emotional appeal.
→ Your comment should add substance to the inspiration — a specific example or counterpoint.
→ Don't just agree — add something concrete.`,

    humorous_witty: `The post is FUNNY/WITTY — humor, sarcasm, clever observations.
→ Your comment should match the energy — be playful, add to the joke, or share a related funny observation.
→ Don't be the serious person in a funny thread.`,
  };

  return instructions[postTone] || instructions.casual_conversational;
}

/**
 * Angle-specific instructions — describes WHAT to say, not HOW to open
 * (The variation instruction handles the opener)
 */
function getAngleInstruction(angle: string, postType: string, details: string[]): string {
  const detailsStr = details.slice(0, 2).join(", ") || "the main topic";

  const instructions: Record<string, string> = {
    WHISPERED_TRUTH: `Share the insider truth others won't mention about ${detailsStr}. Be direct, not preachy. Add real insider knowledge.`,

    HIDDEN_COST: `Point out a hidden cost/catch about ${detailsStr} nobody mentions. Acknowledge the point first, then reveal what they're missing.`,

    SECRET_NOBODY_ASKED: `Share insider knowledge about ${detailsStr} that only someone with real experience would know. Keep it tactical and specific.`,

    LIVED_IT_DEEPER: `Share your harder/deeper version of this experience with ${detailsStr}. Show what you learned. Don't one-up — relate.`,

    ME_TOO_DEEPER: `Go beyond "me too" — share a SPECIFIC parallel experience with ${detailsStr} and what you discovered.`,

    MINDSET_SHIFT: `Reframe ${detailsStr} with a completely different lens. Show a perspective they haven't considered.`,

    INEVITABLE_NOT_SURPRISING: `Make this feel like a natural progression, not a surprise. Reference ${detailsStr}. Ask a forward-looking question. Keep SHORT.`,

    CALL_OUT_VALUE: `Name the SPECIFIC value in ${detailsStr} — why it matters, what makes it rare. Direct, no fluff. Keep SHORT.`,

    ASK_QUESTION: `Ask a genuine, tactical question about ${detailsStr}. Show you're thinking deeper. Make it specific and answerable.`,

    SHARE_EXPERIENCE: `Share your parallel experience with ${detailsStr}. Include specific data/results/timeframes.`,

    ADD_DATA: `Contribute a relevant data point or metric about ${detailsStr}. Keep it natural and connected.`,

    INTENSIFY_SURGICAL: `Take their best insight about ${detailsStr} and sharpen it. Add evidence or a killer example.`,

    REFRAME_SMARTER: `Offer a better perspective on ${detailsStr}. Acknowledge original framing, then present your lens.`,

    FAILURE_AS_CURRICULUM: `Frame failure around ${detailsStr} as learning material. Normalize it, extract the lesson.`,

    REAL_RISK: `Identify the actual risk with ${detailsStr} nobody's talking about. Short, punchy. End with a sharp question.`,

    SEE_WHOLE_GAME: `Zoom out — connect ${detailsStr} to a larger trend. Show how pieces fit together.`,

    EARNED_INSIGHT: `Share wisdom you earned through experience with ${detailsStr}. Apply it to their situation.`,

    VALIDATION: `Simple, genuine acknowledgment of ${detailsStr}. Short (15-25 words), specific, no fluff.`,
  };

  return instructions[angle] || `Engage with the post about ${detailsStr} using your expertise.`;
}

/**
 * Variation-specific instructions — controls HOW the comment opens and flows
 * This OVERRIDES the angle's suggested opener to avoid conflicts
 */
function getVariationInstruction(angle: string, variation: number): string {
  // Variation instructions are independent of angle — they control structure
  const structures = [
    // Variation 0: Direct statement opener
    `STRUCTURE: Start with a direct statement or observation. No questions to start. Flowing single thought. ${getWordRange(angle, 0)} words.`,

    // Variation 1: Experience-based opener
    `STRUCTURE: Start from personal experience — "we saw this when..." or "been through this with...". Build to your insight. ${getWordRange(angle, 1)} words.`,

    // Variation 2: Counter-intuitive or questioning opener
    `STRUCTURE: Start with a flip or question — challenge a common assumption, then reveal your take. ${getWordRange(angle, 2)} words.`,
  ];

  const selected = structures[variation % structures.length];

  return `
VARIATION ${variation + 1} INSTRUCTION:
${selected}

Make this comment DISTINCTLY DIFFERENT from other variations — different opener, different structure.`;
}

function getWordRange(angle: string, variation: number): string {
  // Short angles
  if (["INEVITABLE_NOT_SURPRISING", "CALL_OUT_VALUE", "VALIDATION"].includes(angle)) {
    return ["20-30", "25-35", "15-25"][variation] || "20-30";
  }
  // Normal angles
  return ["35-50", "40-55", "30-45"][variation] || "35-50";
}

function formatFollowers(n: number): string {
  if (n >= 1000000) return (n / 1000000).toFixed(1) + "M";
  if (n >= 1000) return (n / 1000).toFixed(0) + "K";
  return String(n);
}
