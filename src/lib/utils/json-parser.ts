/**
 * Robust JSON parser for LLM responses
 * Ported from profile_analyzer_anthropic.py _safe_json_parse()
 */

export function safeJsonParse<T = Record<string, unknown>>(
  text: string,
  context = "parsing"
): T | null {
  if (!text || !text.trim()) {
    console.error(`[JSON] Empty response in ${context}`);
    return null;
  }

  // Try 1: Clean and parse
  try {
    return JSON.parse(cleanJson(text));
  } catch {
    // continue
  }

  // Try 2: Fix common errors
  try {
    return JSON.parse(fixJsonErrors(text));
  } catch {
    // continue
  }

  // Try 3: Extract from mixed content
  try {
    const extracted = extractJsonFromText(text);
    if (extracted) return JSON.parse(extracted);
  } catch {
    // continue
  }

  console.error(`[JSON] All parsing attempts failed for ${context}`);
  return null;
}

function cleanJson(text: string): string {
  // Remove markdown code blocks
  if (text.includes("```json")) {
    text = text.split("```json")[1].split("```")[0];
  } else if (text.includes("```")) {
    text = text.split("```")[1].split("```")[0];
  }

  text = text.trim();

  // Find JSON boundaries
  const start = text.indexOf("{");
  const end = text.lastIndexOf("}");

  if (start !== -1 && end !== -1 && end > start) {
    text = text.slice(start, end + 1);
  }

  return text;
}

function fixJsonErrors(text: string): string {
  text = cleanJson(text);

  // Remove trailing commas before } or ]
  text = text.replace(/,(\s*[}\]])/g, "$1");

  // Remove control characters
  text = text.replace(/[\x00-\x1f\x7f-\x9f]/g, "");

  // Replace smart quotes
  text = text.replace(/[\u201c\u201d]/g, '"');
  text = text.replace(/[\u2018\u2019]/g, "'");

  // Remove multiple spaces (but keep newlines in strings handled by JSON parser)
  text = text.replace(/\s+/g, " ");

  return text;
}

function extractJsonFromText(text: string): string | null {
  // Find all {...} blocks (handles nested objects)
  const pattern = /\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}/g;
  const matches = text.match(pattern);

  if (matches && matches.length > 0) {
    // Return the largest match
    return matches.reduce((a, b) => (a.length > b.length ? a : b));
  }

  return null;
}
