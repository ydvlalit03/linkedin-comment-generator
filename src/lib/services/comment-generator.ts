/**
 * Comment Generator — main orchestrator
 * Pipeline: analyze → select angle → generate with Groq → validate → humanize
 */
import { chat } from "./groq-client";
import { buildUltimatePrompt, detectSentiment } from "./dynamic-prompt-engine";
import { humanizeComment } from "./humanizer";
import { createLogger } from "../utils/logger";
import {
  COMMENT_ANGLES,
  ANGLE_PREFERENCES,
  WORD_COUNT_TARGETS,
} from "../data/comment-angles";
import { AI_CLICHE_PHRASES } from "../data/ai-cliches";
import type {
  PostAnalysis,
  CommenterProfile,
  GeneratedComment,
  CommentValidation,
} from "../types";

const log = createLogger("Generator");

/**
 * Generate N comment variations for a post
 */
export async function generateComments(
  postContent: string,
  postAnalysis: PostAnalysis,
  commenterProfile: CommenterProfile,
  numVariations = 3,
  ragContext = "",
  webContext = "",
  authorContext?: { name: string; headline: string; followers?: number }
): Promise<GeneratedComment[]> {
  log.section("COMMENT GENERATION");
  log.info(`Post type: ${postAnalysis.postType} | Topic: "${postAnalysis.mainTopic}"`);
  log.info(`Commenter: ${commenterProfile.name} | Tone: ${commenterProfile.tone} | Expertise: ${commenterProfile.expertise.join(", ")}`);
  log.info(`Generating ${numVariations} variations`);

  if (ragContext) log.info(`RAG context: ${ragContext.length} chars`);
  if (webContext) log.info(`Web context: ${webContext.length} chars`);

  const comments: GeneratedComment[] = [];

  // Extract RAG angles
  const ragAngles = extractRagAngles(ragContext);
  if (ragAngles.length > 0) {
    log.info(`RAG angles extracted: ${ragAngles.join(", ")}`);
  } else {
    log.info("No RAG angles — using post type preferences");
  }

  for (let variation = 0; variation < numVariations; variation++) {
    log.section(`VARIATION ${variation + 1}/${numVariations}`);

    try {
      // STEP 1: Select angle
      const angle = selectAngleForVariation(postAnalysis, variation, ragAngles);
      log.step(`STEP 1: Angle selected → ${angle} (${COMMENT_ANGLES[angle] || "custom"})`);

      // STEP 2: Build prompt
      const prompt = buildUltimatePrompt(
        postContent,
        postAnalysis,
        commenterProfile,
        angle,
        variation,
        ragContext,
        webContext,
        authorContext
      );
      log.step(`STEP 2: Prompt built → ${prompt.length} chars`);
      log.debug("Prompt sections", [
        `Post: ${postContent.slice(0, 100)}...`,
        `Angle: ${angle}`,
        `Voice: ${commenterProfile.tone}`,
        `Word target: ${JSON.stringify(WORD_COUNT_TARGETS[postAnalysis.postType] || WORD_COUNT_TARGETS.default)}`,
      ].join("\n"));

      // STEP 3: Generate with Groq
      const temperature = 0.7 + variation * 0.15;
      log.step(`STEP 3: Calling Groq | temperature=${temperature.toFixed(2)}`);

      const raw = await chat(prompt, { temperature, maxTokens: 500 });
      const cleaned = cleanComment(raw);

      if (!cleaned) {
        log.warn("Empty response from Groq — skipping variation");
        continue;
      }

      log.info(`Raw comment: "${cleaned}"`);
      log.info(`Word count: ${cleaned.split(/\s+/).length}`);

      // STEP 4: Humanize
      log.step("STEP 4: Humanizing comment...");
      const humanized = humanizeComment(cleaned, {
        tone: commenterProfile.tone,
        avgCommentLength: commenterProfile.avgCommentLength,
      });

      if (humanized !== cleaned) {
        log.info(`Humanized: "${humanized}"`);
        log.debug("Changes applied", `Before: ${cleaned.length} chars → After: ${humanized.length} chars`);
      } else {
        log.info("No humanization changes needed");
      }

      // STEP 5: Validate
      log.step("STEP 5: Validating comment...");
      const validation = validateComment(humanized, postAnalysis.postType);
      log.info("Validation result", {
        valid: validation.valid,
        qualityScore: validation.qualityScore,
        wordCount: validation.wordCount,
        targetRange: validation.targetRange,
        issues: validation.issues,
        warnings: validation.warnings,
      });

      // STEP 6: Calculate confidence
      const confidence = calculateConfidence(validation, ragAngles, angle, true);
      log.step(`STEP 6: Confidence → ${(confidence * 100).toFixed(0)}%`);
      log.debug("Confidence breakdown", {
        quality: `${validation.qualityScore}/100 → ${((validation.qualityScore / 100) * 0.4).toFixed(2)}`,
        angleSource: ragAngles.includes(angle) ? "RAG (+0.30)" : ["WHISPERED_TRUTH", "HIDDEN_COST", "SECRET_NOBODY_ASKED"].includes(angle) ? "Good (+0.20)" : "Default (+0.10)",
        humanized: "+0.15",
        wordAccuracy: `distance=${validation.distanceFromTarget} → +${validation.distanceFromTarget <= 5 ? "0.10" : validation.distanceFromTarget <= 10 ? "0.06" : "0.03"}`,
        noIssues: validation.issues.length === 0 ? "+0.05" : "+0.00",
      });

      comments.push({
        text: humanized,
        confidence,
        approach: "context-aware",
        postType: postAnalysis.postType,
        angle,
        variationNumber: variation + 1,
        validation,
        humanized: true,
      });

      log.info(`Variation ${variation + 1} COMPLETE: angle=${angle} | ${validation.wordCount} words | quality=${validation.qualityScore} | confidence=${(confidence * 100).toFixed(0)}%`);
    } catch (error) {
      log.error(`Variation ${variation + 1} FAILED`, String(error));
    }
  }

  // Fallback if all failed
  if (comments.length === 0) {
    log.warn("All variations failed — using fallback generation");
    return fallbackGeneration(postContent, commenterProfile, numVariations);
  }

  log.section("GENERATION COMPLETE");
  log.info(`${comments.length} comments generated`);
  comments.forEach((c, i) => {
    log.info(`  #${i + 1}: [${c.angle}] ${c.text.slice(0, 80)}... (${(c.confidence * 100).toFixed(0)}%)`);
  });

  return comments;
}

// ==========================================
// RAG Angle Extraction
// ==========================================

function extractRagAngles(ragContext: string): string[] {
  if (!ragContext) return [];

  const angles: string[] = [];
  const p1 = /Example \d+:\s*([A-Z_]+)/g;
  let match;
  while ((match = p1.exec(ragContext)) !== null) angles.push(match[1]);

  const p2 = /angles?:\s*([A-Z_,\s]+)/gi;
  while ((match = p2.exec(ragContext)) !== null) {
    angles.push(...match[1].split(",").map((s) => s.trim()));
  }

  return [...new Set(angles.filter((a) => a in COMMENT_ANGLES))];
}

// ==========================================
// Angle Selection (RAG-first)
// ==========================================

function selectAngleForVariation(
  postAnalysis: PostAnalysis,
  variation: number,
  ragAngles: string[]
): string {
  // Priority 1: RAG angles
  if (ragAngles.length > variation) {
    log.debug(`Angle source: RAG (proven winner) → ${ragAngles[variation]}`);
    return ragAngles[variation];
  }

  // Priority 2: AI-suggested angles
  const bestAngles = postAnalysis.bestResponseAngles || [];
  if (bestAngles.length > variation) {
    const angle = bestAngles[variation];
    if (angle in COMMENT_ANGLES) {
      log.debug(`Angle source: AI analysis → ${angle}`);
      return angle;
    }
  }

  // Priority 3: Post type preferences
  const preferred = ANGLE_PREFERENCES[postAnalysis.postType] || ANGLE_PREFERENCES.advice_tactical || ["WHISPERED_TRUTH", "HIDDEN_COST", "EARNED_INSIGHT"];
  const selected = preferred[variation % preferred.length];
  log.debug(`Angle source: Post type preference (${postAnalysis.postType}) → ${selected}`);
  return selected;
}

// ==========================================
// Validation
// ==========================================

function validateComment(comment: string, postType: string): CommentValidation {
  const wordCount = comment.split(/\s+/).length;
  const targets = WORD_COUNT_TARGETS[postType] || WORD_COUNT_TARGETS.default;
  const { min, target, max } = targets;

  const issues: string[] = [];
  const warnings: string[] = [];
  let qualityScore = 100;

  if (wordCount < min - 15) { issues.push(`Too short: ${wordCount} words`); qualityScore -= 40; }
  else if (wordCount > max + 15) { issues.push(`Too long: ${wordCount} words`); qualityScore -= 40; }
  else if (wordCount < min) { warnings.push(`Below target: ${wordCount} words`); qualityScore -= 15; }
  else if (wordCount > max) { warnings.push(`Above target: ${wordCount} words`); qualityScore -= 15; }
  else {
    const distance = Math.abs(wordCount - target);
    if (distance <= 5) qualityScore = 100;
    else if (distance <= 10) qualityScore -= 5;
    else qualityScore -= 10;
  }

  const commentLower = comment.toLowerCase();
  const aiPhraseCount = AI_CLICHE_PHRASES.filter((p) => commentLower.includes(p)).length;
  if (aiPhraseCount > 0) { warnings.push(`${aiPhraseCount} AI phrases detected`); qualityScore -= aiPhraseCount * 10; }

  const exclamations = (comment.match(/!/g) || []).length;
  if (exclamations > 1) { warnings.push("Multiple exclamation marks"); qualityScore -= 15; }

  qualityScore = Math.max(0, qualityScore);

  return {
    valid: issues.length === 0 && qualityScore >= 60,
    issues,
    warnings,
    wordCount,
    qualityScore,
    targetRange: `${min}-${max}`,
    distanceFromTarget: Math.abs(wordCount - target),
  };
}

// ==========================================
// Confidence Calculation
// ==========================================

function calculateConfidence(
  validation: CommentValidation,
  ragAngles: string[],
  angleUsed: string,
  humanized: boolean
): number {
  let confidence = 0;
  confidence += (validation.qualityScore / 100) * 0.4;
  if (ragAngles.includes(angleUsed)) confidence += 0.3;
  else if (["WHISPERED_TRUTH", "HIDDEN_COST", "SECRET_NOBODY_ASKED"].includes(angleUsed)) confidence += 0.2;
  else confidence += 0.1;
  confidence += humanized ? 0.15 : 0.05;
  if (validation.distanceFromTarget <= 5) confidence += 0.1;
  else if (validation.distanceFromTarget <= 10) confidence += 0.06;
  else confidence += 0.03;
  if (validation.issues.length === 0) confidence += 0.05;
  return Math.min(confidence, 0.99);
}

// ==========================================
// Helpers
// ==========================================

function cleanComment(text: string): string {
  text = text.trim().replace(/^["']|["']$/g, "");
  text = text.replace(/\*\*/g, "");
  const prefixes = ["comment:", "response:", "output:", "here's my comment:"];
  for (const prefix of prefixes) {
    if (text.toLowerCase().startsWith(prefix)) text = text.slice(prefix.length).trim();
  }
  return text.replace(/\s+/g, " ").trim();
}

async function fallbackGeneration(
  postContent: string,
  profile: CommenterProfile,
  numVariations: number
): Promise<GeneratedComment[]> {
  log.step("FALLBACK: Generating simple comments...");

  const prompt = `Write ${numVariations} LinkedIn comments for this post. Each should be different.

POST: ${postContent.slice(0, 400)}

You are ${profile.name}, a ${profile.expertise.join(", ")} expert.
Tone: ${profile.tone}
Length: 30-50 words each.

Write each comment on a new line. No numbering. No quotes.`;

  try {
    const response = await chat(prompt, { temperature: 0.8, maxTokens: 600 });
    const lines = response.split("\n").map((l) => l.trim()).filter((l) => l.length > 20);

    return lines.slice(0, numVariations).map((text, i) => ({
      text: humanizeComment(cleanComment(text)),
      confidence: 0.6,
      approach: "fallback",
      postType: "general",
      angle: "GENERAL_ENGAGEMENT",
      variationNumber: i + 1,
      validation: { valid: true, issues: [], warnings: ["fallback"], wordCount: text.split(/\s+/).length, qualityScore: 70, targetRange: "30-60", distanceFromTarget: 0 },
      humanized: true,
    }));
  } catch {
    log.error("Fallback generation also failed");
    return [];
  }
}
