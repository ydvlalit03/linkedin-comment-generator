/**
 * Advanced Comment Humanizer
 * Implements: burstiness, contractions, conversational markers, imperfections
 */
import { createLogger } from "../utils/logger";

const log = createLogger("Humanizer");
import {
  FORMAL_TRANSITIONS,
  CASUAL_CONNECTORS,
  AI_CLICHE_PHRASES,
  AI_CLICHE_WORDS,
} from "../data/ai-cliches";

// Natural conversation starters
const NATURAL_STARTERS = [
  "", "", "", "", // Empty = most natural (high probability)
  "Honestly,",
  "Real talk -",
  "Ngl,",
  "Tbh,",
  "Yeah,",
  "So,",
  "Look,",
];

const NATURAL_FILLERS = [
  "kinda", "sorta", "pretty much", "basically",
  "honestly", "actually", "really", "just",
];

function randomChoice<T>(arr: T[]): T {
  return arr[Math.floor(Math.random() * arr.length)];
}

/**
 * Apply comprehensive humanization pipeline
 */
export function humanizeComment(
  comment: string,
  userStyle: {
    tone?: string;
    avgCommentLength?: number;
    typicalOpenings?: string[];
  } = {}
): string {
  let text = comment;
  const changes: string[] = [];

  // Step 1: Remove AI formality
  const before1 = text;
  text = removeAiFormality(text);
  if (text !== before1) changes.push("removed AI formality");

  // Step 2: Apply contractions
  const before2 = text;
  text = applyContractions(text);
  if (text !== before2) changes.push("applied contractions");

  // Step 3: Vary sentence structure (burstiness)
  const before3 = text;
  text = varySentenceStructure(text);
  if (text !== before3) changes.push("varied sentence structure");

  // Step 4: Add conversational markers
  const before4 = text;
  text = addConversationalMarkers(text, userStyle);
  if (text !== before4) changes.push("added conversational markers");

  // Step 5: Strategic imperfections
  const before5 = text;
  text = addNaturalImperfections(text, userStyle);
  if (text !== before5) changes.push("added imperfections");

  // Step 6: Match user length preference
  const before6 = text;
  text = adjustToUserLength(text, userStyle.avgCommentLength || 45);
  if (text !== before6) changes.push("adjusted length");

  if (changes.length > 0) {
    log.info(`Humanization applied: ${changes.join(" → ")}`);
  } else {
    log.info("No humanization changes needed");
  }

  return text.trim();
}

/**
 * Remove formal AI transitions and replace with casual connectors
 */
function removeAiFormality(text: string): string {
  // Remove formal transition starters
  for (const formal of FORMAL_TRANSITIONS) {
    if (text.startsWith(formal)) {
      text = text.slice(formal.length).trim();
    }
  }

  // Replace formal connectors with casual ones
  for (const [formal, casualList] of Object.entries(CASUAL_CONNECTORS)) {
    const pattern = new RegExp(`\\b${formal}\\b`, "gi");
    if (pattern.test(text)) {
      const casual = randomChoice(casualList);
      text = text.replace(pattern, casual);
    }
  }

  // Remove AI cliche phrases
  for (const phrase of AI_CLICHE_PHRASES) {
    const pattern = new RegExp(phrase.replace(/[.*+?^${}()|[\]\\]/g, "\\$&"), "gi");
    text = text.replace(pattern, "").trim();
  }

  // Flag AI cliche words (replace with simpler alternatives)
  const wordReplacements: Record<string, string> = {
    leverage: "use",
    navigate: "deal with",
    unlock: "find",
    empower: "help",
    delve: "dig into",
    foster: "build",
    robust: "strong",
    seamless: "smooth",
    holistic: "full",
    transformative: "big",
    groundbreaking: "new",
    paradigm: "model",
    synergy: "teamwork",
    streamline: "simplify",
    optimize: "improve",
    innovative: "new",
    catalyze: "start",
    spearhead: "lead",
    harness: "use",
    amplify: "grow",
  };

  for (const [word, replacement] of Object.entries(wordReplacements)) {
    const pattern = new RegExp(`\\b${word}\\b`, "gi");
    text = text.replace(pattern, replacement);
  }

  return text;
}

/**
 * Apply natural contractions — humans use them 70%+ of the time
 */
function applyContractions(text: string): string {
  const contractions: [RegExp, string][] = [
    [/\bdo not\b/gi, "don't"],
    [/\bdoes not\b/gi, "doesn't"],
    [/\bdid not\b/gi, "didn't"],
    [/\bcannot\b/gi, "can't"],
    [/\bwill not\b/gi, "won't"],
    [/\bwould not\b/gi, "wouldn't"],
    [/\bcould not\b/gi, "couldn't"],
    [/\bshould not\b/gi, "shouldn't"],
    [/\bhave not\b/gi, "haven't"],
    [/\bhas not\b/gi, "hasn't"],
    [/\bhad not\b/gi, "hadn't"],
    [/\bis not\b/gi, "isn't"],
    [/\bare not\b/gi, "aren't"],
    [/\bwas not\b/gi, "wasn't"],
    [/\bwere not\b/gi, "weren't"],
    [/\bI am\b/g, "I'm"],
    [/\byou are\b/gi, "you're"],
    [/\bhe is\b/gi, "he's"],
    [/\bshe is\b/gi, "she's"],
    [/\bit is\b/gi, "it's"],
    [/\bwe are\b/gi, "we're"],
    [/\bthey are\b/gi, "they're"],
    [/\bI have\b/g, "I've"],
    [/\byou have\b/gi, "you've"],
    [/\bwe have\b/gi, "we've"],
    [/\bthey have\b/gi, "they've"],
    [/\bI will\b/g, "I'll"],
    [/\byou will\b/gi, "you'll"],
    [/\bwe will\b/gi, "we'll"],
    [/\bthey will\b/gi, "they'll"],
    [/\bthat is\b/gi, "that's"],
    [/\bthere is\b/gi, "there's"],
    [/\bwhat is\b/gi, "what's"],
    [/\bwho is\b/gi, "who's"],
  ];

  for (const [pattern, replacement] of contractions) {
    text = text.replace(pattern, replacement);
  }

  return text;
}

/**
 * Increase burstiness — vary sentence lengths for human-like writing
 */
function varySentenceStructure(text: string): string {
  const parts = text.split(/([.!?]+)/);
  const sentences: string[] = [];
  for (let i = 0; i < parts.length - 1; i += 2) {
    sentences.push(parts[i] + (parts[i + 1] || ""));
  }
  if (parts.length % 2 === 1 && parts[parts.length - 1].trim()) {
    sentences.push(parts[parts.length - 1]);
  }

  if (sentences.length <= 1) return text;

  // 30% chance: combine two short sentences
  if (Math.random() < 0.3 && sentences.length >= 2) {
    const idx = Math.floor(Math.random() * (sentences.length - 1));
    const combined =
      sentences[idx].replace(/[.!?]+$/, "") + ". " + sentences[idx + 1].trim();
    sentences.splice(idx, 2, combined);
  }

  // 25% chance: break a long sentence at "but"
  for (let i = 0; i < sentences.length; i++) {
    const words = sentences[i].split(" ");
    if (words.length > 15 && Math.random() < 0.25) {
      const lower = sentences[i].toLowerCase();
      if (lower.includes(" but ")) {
        const splitParts = sentences[i].split(/\s+but\s+/i);
        if (splitParts.length === 2) {
          sentences[i] = splitParts[0].trim() + ".";
          sentences.splice(i + 1, 0, "But " + splitParts[1].trim());
          break;
        }
      }
    }
  }

  return sentences.join(" ").trim();
}

/**
 * Add natural conversation markers
 */
function addConversationalMarkers(
  text: string,
  userStyle: { typicalOpenings?: string[] }
): string {
  // 30% chance to add a natural starter
  if (Math.random() < 0.3) {
    const userOpenings = userStyle.typicalOpenings || [];
    if (userOpenings.length > 0 && Math.random() < 0.6) {
      const starter = randomChoice(userOpenings);
      if (!text.startsWith(starter)) {
        text = `${starter} ${text[0].toLowerCase()}${text.slice(1)}`;
      }
    } else {
      const starter = randomChoice(NATURAL_STARTERS);
      if (starter) {
        text = `${starter} ${text[0].toLowerCase()}${text.slice(1)}`;
      }
    }
  }

  // 20% chance: add a casual filler mid-sentence
  if (Math.random() < 0.2) {
    const words = text.split(" ");
    if (words.length > 8) {
      const filler = randomChoice(NATURAL_FILLERS);
      const pos = 3 + Math.floor(Math.random() * Math.min(3, words.length - 4));
      words.splice(pos, 0, filler);
      text = words.join(" ");
    }
  }

  return text;
}

/**
 * Add strategic imperfections for authenticity
 */
function addNaturalImperfections(
  text: string,
  userStyle: { tone?: string }
): string {
  // 40% chance: remove trailing period (casual style)
  if (Math.random() < 0.4 && text.endsWith(".")) {
    text = text.slice(0, -1);
  }

  // 25% chance: start with lowercase (very casual)
  if (
    Math.random() < 0.25 &&
    userStyle.tone === "casual" &&
    text.length > 0
  ) {
    const firstWord = text.split(" ")[0];
    // Don't lowercase if it's an acronym
    if (firstWord !== firstWord.toUpperCase()) {
      text = text[0].toLowerCase() + text.slice(1);
    }
  }

  // 15% chance: trailing thought with ellipsis
  if (Math.random() < 0.15 && !text.endsWith("?")) {
    if (text.endsWith(".")) {
      text = text.slice(0, -1) + "...";
    } else if (!text.endsWith("...")) {
      text += "...";
    }
  }

  return text;
}

/**
 * Match user's typical comment length
 */
function adjustToUserLength(text: string, targetLength: number): string {
  const words = text.split(/\s+/);
  const maxLength = Math.floor(targetLength * 1.3);

  if (words.length > maxLength) {
    // Trim by sentences
    const sentences = text.split(/([.!?]+\s*)/);
    let result = "";
    let count = 0;

    for (let i = 0; i < sentences.length; i += 2) {
      const sent = sentences[i] + (sentences[i + 1] || "");
      const sentWords = sent.split(/\s+/).length;
      if (count + sentWords <= maxLength) {
        result += sent;
        count += sentWords;
      } else {
        break;
      }
    }

    if (result) text = result;
  }

  return text;
}
