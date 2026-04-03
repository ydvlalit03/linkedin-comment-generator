// 15 Standard Post Types — ported from profile_analyzer_anthropic.py

export const STANDARD_POST_TYPES = [
  "celebration_win",
  "failure_setback",
  "advice_tactical",
  "reflective_lessons",
  "vulnerable_emotional",
  "comeback_redemption",
  "hiring_team",
  "hot_take_controversial",
  "frustration_rant",
  "gratitude_inspirational",
  "milestone_announcement",
  "crowd_engagement",
  "philosophical_abstract",
  "crisis_loss_burnout",
  "self_promo_pitch",
] as const;

export type StandardPostType = (typeof STANDARD_POST_TYPES)[number];

// Map non-standard types to standard ones
export const POST_TYPE_MAPPING: Record<string, StandardPostType> = {
  announcement: "milestone_announcement",
  "context-aware": "advice_tactical",
  achievement: "celebration_win",
  insight: "advice_tactical",
  question: "crowd_engagement",
  story: "reflective_lessons",
  opinion: "hot_take_controversial",
  advice: "advice_tactical",
  tactical: "advice_tactical",
  lesson: "reflective_lessons",
  celebration: "celebration_win",
  win: "celebration_win",
  hiring: "hiring_team",
  job: "hiring_team",
  controversial: "hot_take_controversial",
  hot_take: "hot_take_controversial",
  milestone: "milestone_announcement",
  launch: "milestone_announcement",
  failure: "failure_setback",
  vulnerable: "vulnerable_emotional",
  rant: "frustration_rant",
  gratitude: "gratitude_inspirational",
  promo: "self_promo_pitch",
  general: "advice_tactical",
};

export function normalizePostType(rawType: string): StandardPostType {
  if (!rawType) return "advice_tactical";

  const cleaned = rawType.toLowerCase().trim().replace(/\s+/g, "_");

  // Already standard
  if (STANDARD_POST_TYPES.includes(cleaned as StandardPostType)) {
    return cleaned as StandardPostType;
  }

  // Map to standard
  if (cleaned in POST_TYPE_MAPPING) {
    return POST_TYPE_MAPPING[cleaned];
  }

  // Partial match
  for (const [key, value] of Object.entries(POST_TYPE_MAPPING)) {
    if (cleaned.includes(key) || key.includes(cleaned)) {
      return value;
    }
  }

  return "advice_tactical";
}
