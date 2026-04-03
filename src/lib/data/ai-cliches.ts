// AI vocabulary tells to detect and remove
// Sources: linkedin-post-writing-skill repo (40+ tells) + advanced_humanizer.py

export const AI_CLICHE_WORDS = [
  "leverage", "navigate", "unlock", "empower", "delve",
  "foster", "robust", "seamless", "synergy", "paradigm",
  "groundbreaking", "transformative", "cutting-edge", "game-changer",
  "disruptive", "holistic", "ecosystem", "landscape", "journey",
  "pivotal", "nuanced", "comprehensive", "streamline", "optimize",
  "innovative", "catalyze", "spearhead", "harness", "amplify",
];

export const AI_CLICHE_PHRASES = [
  "it's worth noting",
  "it's important to",
  "in today's",
  "in today's world",
  "in today's landscape",
  "at the end of the day",
  "couldn't agree more",
  "this resonates deeply",
  "this is so important",
  "great post",
  "love this",
  "well said",
  "spot on",
  "on the other hand",
  "it goes without saying",
  "needless to say",
  "it should be noted",
  "to be fair",
  "that being said",
  "having said that",
  "let's not forget",
  "the fact of the matter",
  "when it comes to",
  "in my humble opinion",
];

// Formal transitions that scream AI
export const FORMAL_TRANSITIONS = [
  "In conclusion,",
  "To summarize,",
  "Furthermore,",
  "Moreover,",
  "Additionally,",
  "Consequently,",
  "Nevertheless,",
  "Subsequently,",
  "Ultimately,",
  "Initially,",
  "In essence,",
  "Essentially,",
  "Fundamentally,",
];

// Casual replacements for formal connectors
export const CASUAL_CONNECTORS: Record<string, string[]> = {
  however: ["but", "though", "still"],
  therefore: ["so", "meaning", "which means"],
  additionally: ["also", "plus", "and"],
  furthermore: ["plus", "and", "also"],
  moreover: ["also", "plus", "and"],
  consequently: ["so", "meaning"],
  nevertheless: ["but", "still", "though"],
  thus: ["so"],
  hence: ["so"],
  regarding: ["about", "on"],
  concerning: ["about"],
  subsequently: ["then", "later"],
  initially: ["first", "at first"],
  ultimately: ["in the end", "finally"],
};
