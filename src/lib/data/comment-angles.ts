import type { CommentAngleKey } from "../types";

// 44 Comment Angles — ported from comment_generator_anthropic.py
export const COMMENT_ANGLES: Record<string, string> = {
  INEVITABLE_NOT_SURPRISING: "This success was inevitable",
  REAL_COST: "Acknowledge the hidden price",
  FAILURE_AS_CURRICULUM: "Frame failure as learning",
  LIVED_IT_DEEPER: "I've been through this exact situation",
  WHISPERED_TRUTH: "Say the quiet part out loud",
  EARNED_INSIGHT: "Share wisdom earned through experience",
  ME_TOO_DEEPER: "Go beyond 'me too' with specific parallel",
  HIDDEN_COST: "Point out what they're not seeing",
  MINDSET_SHIFT: "Reframe the situation entirely",
  REAL_RISK: "Identify the actual risk",
  SECRET_NOBODY_ASKED: "Share insider knowledge",
  INTENSIFY_SURGICAL: "Amplify their point with precision",
  SEE_WHOLE_GAME: "Zoom out to bigger picture",
  PATTERN_NOT_MAD: "Identify the pattern calmly",
  VALIDATION: "Simple acknowledgment of worth",
  SHARE_EXPERIENCE: "Parallel experience",
  ADD_DATA: "Contribute facts or metrics",
  ASK_QUESTION: "Genuine inquiry",
  REFRAME_SMARTER: "Better perspective on the issue",
  CALL_OUT_VALUE: "Name the value they provided",
  GENERAL_ENGAGEMENT: "Standard professional engagement",
};

// Sentiment patterns — ported from dynamic_prompt_engine.py
export const SENTIMENT_PATTERNS: Record<
  string,
  { keywords: string[]; angles: CommentAngleKey[] }
> = {
  advice_tactical: {
    keywords: [
      "how to", "here's how", "steps", "framework", "process",
      "tip", "strategy", "here are", "guide", "approach",
    ],
    angles: ["WHISPERED_TRUTH", "HIDDEN_COST", "SECRET_NOBODY_ASKED"],
  },
  reflective_lessons: {
    keywords: [
      "learned", "realized", "discovered", "wish i knew",
      "looking back", "lesson", "years ago", "experience taught",
    ],
    angles: ["LIVED_IT_DEEPER", "ME_TOO_DEEPER", "MINDSET_SHIFT"],
  },
  celebration_win: {
    keywords: [
      "excited", "thrilled", "proud", "achieved", "milestone",
      "reached", "hit", "joined", "promoted",
    ],
    angles: ["INEVITABLE_NOT_SURPRISING", "REAL_COST", "CALL_OUT_VALUE"],
  },
  crowd_engagement: {
    keywords: [
      "what do you think", "thoughts?", "curious",
      "would love", "agree?", "?",
    ],
    angles: ["ASK_QUESTION", "SHARE_EXPERIENCE", "ADD_DATA"],
  },
  hot_take_controversial: {
    keywords: [
      "unpopular", "controversial", "hot take",
      "nobody talks", "truth is", "let's be honest",
    ],
    angles: ["INTENSIFY_SURGICAL", "SEE_WHOLE_GAME", "REFRAME_SMARTER"],
  },
  milestone_announcement: {
    keywords: [
      "launched", "released", "announcing", "starting",
      "introducing", "available",
    ],
    angles: ["INEVITABLE_NOT_SURPRISING", "CALL_OUT_VALUE", "ASK_QUESTION"],
  },
  failure_setback: {
    keywords: [
      "failed", "lost", "mistake", "wrong", "regret",
      "setback", "tough", "hard lesson",
    ],
    angles: ["FAILURE_AS_CURRICULUM", "LIVED_IT_DEEPER", "PATTERN_NOT_MAD"],
  },
};

// Angle preferences by post type — used when RAG angles not available
export const ANGLE_PREFERENCES: Record<string, CommentAngleKey[]> = {
  advice_tactical: ["WHISPERED_TRUTH", "HIDDEN_COST", "SECRET_NOBODY_ASKED"],
  reflective_lessons: ["ME_TOO_DEEPER", "MINDSET_SHIFT", "LIVED_IT_DEEPER"],
  celebration_win: ["INEVITABLE_NOT_SURPRISING", "REAL_COST", "CALL_OUT_VALUE"],
  milestone_announcement: ["INEVITABLE_NOT_SURPRISING", "CALL_OUT_VALUE", "SEE_WHOLE_GAME"],
  crowd_engagement: ["ASK_QUESTION", "SHARE_EXPERIENCE", "ADD_DATA"],
  hot_take_controversial: ["INTENSIFY_SURGICAL", "SEE_WHOLE_GAME", "REFRAME_SMARTER"],
  failure_setback: ["FAILURE_AS_CURRICULUM", "LIVED_IT_DEEPER", "PATTERN_NOT_MAD"],
  vulnerable_emotional: ["ME_TOO_DEEPER", "VALIDATION", "EARNED_INSIGHT"],
  hiring_team: ["CALL_OUT_VALUE", "ASK_QUESTION", "SHARE_EXPERIENCE"],
  self_promo_pitch: ["ASK_QUESTION", "CALL_OUT_VALUE", "SHARE_EXPERIENCE"],
};

// Word count targets by post type
export const WORD_COUNT_TARGETS: Record<string, { min: number; target: number; max: number }> = {
  celebration_win: { min: 15, target: 30, max: 40 },
  milestone_announcement: { min: 20, target: 35, max: 45 },
  advice_tactical: { min: 35, target: 50, max: 65 },
  reflective_lessons: { min: 35, target: 50, max: 65 },
  hot_take_controversial: { min: 40, target: 55, max: 70 },
  crowd_engagement: { min: 25, target: 40, max: 55 },
  failure_setback: { min: 30, target: 45, max: 60 },
  vulnerable_emotional: { min: 25, target: 40, max: 55 },
  default: { min: 30, target: 45, max: 60 },
};
