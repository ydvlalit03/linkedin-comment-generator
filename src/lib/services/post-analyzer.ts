/**
 * Post Analyzer — detects post type, sentiment, topic, tone, and best angles
 * Uses Groq for AI analysis
 */
import { chat, analyzeImage } from "./groq-client";
import { safeJsonParse } from "../utils/json-parser";
import { normalizePostType } from "../data/post-types";
import { SENTIMENT_PATTERNS } from "../data/comment-angles";
import { createLogger } from "../utils/logger";
import type { PostAnalysis, PostMedia, PostAuthor } from "../types";

const log = createLogger("Analyzer");

/**
 * Analyze a LinkedIn post to determine best comment strategy
 */
export async function analyzePost(
  postText: string,
  media: PostMedia[] = [],
  author?: { name: string; headline: string },
): Promise<PostAnalysis> {
  log.section("POST ANALYSIS");
  log.info(`Post text: ${postText.length} chars`);
  log.debug("Post preview", postText.slice(0, 200));
  if (author) log.info(`Post author: ${author.name} — ${author.headline}`);

  try {
    log.substep(1, 3, "Analyzing post text with Groq...");
    const textAnalysis = await analyzePostText(postText, author);

    log.info("Text analysis result", {
      postType: textAnalysis.postType,
      topic: textAnalysis.mainTopic,
      sentiment: textAnalysis.sentiment,
      tone: textAnalysis.emotionalTone,
      postTone: textAnalysis.postTone,
      details: textAnalysis.specificDetails,
      angles: textAnalysis.bestResponseAngles,
    });

    let mediaContext = "";
    const imageMedia = media.find(
      (m) => m.type === "image" || (m.type === "video" && m.thumbnailUrl)
    );
    if (imageMedia) {
      const imageUrl = imageMedia.thumbnailUrl || imageMedia.url;
      if (imageUrl) {
        log.substep(2, 3, `Analyzing media (${imageMedia.type}) with Groq Vision...`);
        mediaContext = await analyzePostMedia(imageUrl, postText);
        log.info("Media analysis result", mediaContext);
      }
    } else {
      log.substep(2, 3, "No media to analyze — skipping");
    }

    if (mediaContext && textAnalysis) {
      textAnalysis.keyInsights.push(`[Visual context] ${mediaContext}`);
    }

    log.substep(3, 3, "Analysis complete");
    log.info(`Final: type=${textAnalysis.postType} | topic="${textAnalysis.mainTopic}" | postTone=${textAnalysis.postTone}`);

    return textAnalysis;
  } catch (error) {
    log.error("Analysis failed, using fallback", String(error));
    return fallbackAnalysis(postText);
  }
}

async function analyzePostText(
  postText: string,
  author?: { name: string; headline: string }
): Promise<PostAnalysis> {
  const authorContext = author
    ? `\nPOST AUTHOR: ${author.name} — ${author.headline}\n`
    : "";

  const prompt = `Analyze this LinkedIn post to determine the BEST comment strategy.
${authorContext}
POST:
${postText.slice(0, 1500)}

Analyze carefully:
1. Post Type - Choose ONE:
   - "advice_tactical" (how-to, tips, strategy, frameworks)
   - "reflective_lessons" (looking back, lessons learned)
   - "celebration_win" (achievement, promotion, milestone)
   - "crowd_engagement" (asking for input, poll, discussion)
   - "hot_take_controversial" (unpopular opinion, bold claim)
   - "milestone_announcement" (launch, release, news)
   - "failure_setback" (failure, mistake, tough lesson)
   - "vulnerable_emotional" (personal struggle, vulnerability)
   - "hiring_team" (job posting, team building)

2. Post Writing Tone - How is the post WRITTEN? Choose ONE:
   - "casual_conversational" (short sentences, informal, like talking to a friend)
   - "formal_professional" (structured, corporate language)
   - "listicle_breakdown" (uses bullet points, numbered lists)
   - "storytelling_narrative" (tells a story, has a beginning/middle/end)
   - "data_heavy" (stats, numbers, research-backed)
   - "motivational_inspirational" (uplifting, emotional appeal)
   - "humorous_witty" (jokes, sarcasm, wit)

3. What 3 specific details from the post should a commenter reference?

4. What 3 comment ANGLES from this list would get the most engagement?
   Choose from: WHISPERED_TRUTH, HIDDEN_COST, SECRET_NOBODY_ASKED, LIVED_IT_DEEPER, ME_TOO_DEEPER, MINDSET_SHIFT, INEVITABLE_NOT_SURPRISING, CALL_OUT_VALUE, ASK_QUESTION, SHARE_EXPERIENCE, ADD_DATA, INTENSIFY_SURGICAL, REFRAME_SMARTER, EARNED_INSIGHT, REAL_RISK

Return ONLY valid JSON:
{
  "post_type": "ONE type from list above",
  "main_topic": "specific topic in 3-5 words",
  "sentiment": "positive OR negative OR neutral",
  "emotional_tone": "ONE word - strategic/excited/thoughtful/vulnerable/frustrated/curious",
  "post_tone": "ONE tone from the writing tone list above",
  "specific_details": ["detail1", "detail2", "detail3"],
  "key_insights": ["insight1", "insight2"],
  "best_response_angles": ["ANGLE_1", "ANGLE_2", "ANGLE_3"]
}

CRITICAL: Output ONLY valid JSON. No markdown. No extra text. Angles must be from the provided list exactly.`;

  log.debug("Sending analysis prompt to Groq", `${prompt.length} chars`);

  const response = await chat(prompt, {
    jsonMode: true,
    temperature: 0.3,
    maxTokens: 1000,
  });

  const parsed = safeJsonParse<any>(response, "post analysis");

  if (!parsed) {
    log.warn("JSON parsing failed, using keyword fallback");
    return fallbackAnalysis(postText);
  }

  const normalizedType = normalizePostType(parsed.post_type || "");
  log.info(`Post type: "${parsed.post_type}" → normalized: "${normalizedType}"`);
  log.info(`Post writing tone: "${parsed.post_tone}"`);

  return {
    postType: normalizedType,
    mainTopic: parsed.main_topic || "general discussion",
    sentiment: parsed.sentiment || "neutral",
    emotionalTone: parsed.emotional_tone || "thoughtful",
    postTone: parsed.post_tone || "casual_conversational",
    specificDetails: parsed.specific_details || [],
    keyInsights: parsed.key_insights || [],
    bestResponseAngles: parsed.best_response_angles || [],
  };
}

async function analyzePostMedia(imageUrl: string, postText: string): Promise<string> {
  try {
    const prompt = `This image is from a LinkedIn post. The post text says: "${postText.slice(0, 300)}"

Briefly describe what's in this image and how it relates to the post. Keep it under 50 words.`;

    return (await analyzeImage(imageUrl, prompt, { maxTokens: 200, temperature: 0.3 })).trim();
  } catch (error) {
    log.error("Media analysis failed", String(error));
    return "";
  }
}

function fallbackAnalysis(postText: string): PostAnalysis {
  const postLower = postText.toLowerCase();
  let bestType = "advice_tactical";
  let bestScore = 0;

  for (const [type, data] of Object.entries(SENTIMENT_PATTERNS)) {
    const score = data.keywords.filter((kw) => postLower.includes(kw)).length;
    if (score > bestScore) { bestScore = score; bestType = type; }
  }

  log.warn(`Fallback analysis: type=${bestType} (keyword score: ${bestScore})`);

  const angles = SENTIMENT_PATTERNS[bestType]?.angles || ["WHISPERED_TRUTH", "HIDDEN_COST", "EARNED_INSIGHT"];
  return {
    postType: bestType,
    mainTopic: "general discussion",
    sentiment: "neutral",
    emotionalTone: "thoughtful",
    postTone: "casual_conversational",
    specificDetails: [],
    keyInsights: [],
    bestResponseAngles: [...angles],
  };
}
