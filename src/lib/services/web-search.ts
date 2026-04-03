/**
 * Web Search Service — SerpAPI (Google Search)
 * Uses serpapi.com for topic context enrichment
 */
import type { WebSearchContext, WebSearchResult } from "../types";
import { createLogger } from "../utils/logger";

const log = createLogger("WebSearch");

// Post types that benefit from web search
const SEARCH_POST_TYPES = [
  "advice_tactical",
  "hot_take_controversial",
  "philosophical_abstract",
  "reflective_lessons",
  "failure_setback",
  "crisis_loss_burnout",
];

// Post types that don't need search
const NO_SEARCH_TYPES = [
  "gratitude_inspirational",
  "celebration_win",
  "hiring_team",
  "self_promo_pitch",
  "milestone_announcement",
];

// Keywords that indicate need for context
const SEARCH_KEYWORDS = [
  "ai", "artificial intelligence", "machine learning", "blockchain",
  "startup", "funding", "acquisition", "ipo", "layoff",
  "regulation", "policy", "market", "research", "study",
  "report", "data shows", "according to", "new tool",
];

/**
 * Determine if web search would help this post
 */
export function shouldSearch(
  postType: string,
  mainTopic: string,
  postText: string
): boolean {
  const serpKey = process.env.SERPAPI_KEY;

  if (!serpKey) { log.info("SerpAPI key not set — skipping search"); return false; }
  if (NO_SEARCH_TYPES.includes(postType)) { log.info(`Post type "${postType}" doesn't need search — skipping`); return false; }
  if (SEARCH_POST_TYPES.includes(postType)) { log.info(`Post type "${postType}" benefits from search — will search`); return true; }

  // Check for technical/news keywords
  const textLower = (postText + " " + mainTopic).toLowerCase();
  return SEARCH_KEYWORDS.some((kw) => textLower.includes(kw));
}

/**
 * Search via SerpAPI
 */
export async function searchTopic(
  query: string,
  numResults = 3
): Promise<WebSearchContext> {
  const serpKey = process.env.SERPAPI_KEY;

  if (!serpKey) {
    return { query, results: [], summary: "" };
  }

  log.info(`Searching: "${query}" (${numResults} results)`);

  try {
    const url = new URL("https://serpapi.com/search.json");
    url.searchParams.set("api_key", serpKey);
    url.searchParams.set("q", query);
    url.searchParams.set("engine", "google");
    url.searchParams.set("num", String(numResults));
    url.searchParams.set("gl", "us");
    url.searchParams.set("hl", "en");

    const response = await fetch(url.toString(), {
      signal: AbortSignal.timeout(10000),
    });

    if (!response.ok) {
      console.error(`[SerpAPI] HTTP ${response.status}`);
      return { query, results: [], summary: "" };
    }

    const data = await response.json();

    // SerpAPI returns organic_results
    const results: WebSearchResult[] = (data.organic_results || [])
      .slice(0, numResults)
      .map((item: any) => ({
        title: item.title || "",
        snippet: item.snippet || "",
        url: item.link || "",
      }));

    const summary = results
      .map((r) => `${r.title}: ${r.snippet}`)
      .join("\n");

    log.info(`Search returned ${results.length} results`);
    results.forEach((r, i) => log.debug(`  ${i + 1}. ${r.title}`));

    return { query, results, summary };
  } catch (error) {
    log.error("SerpAPI request failed", String(error));
    return { query, results: [], summary: "" };
  }
}

/**
 * Get topic insights for a post — uses smarter query building
 */
export async function getTopicInsights(
  mainTopic: string,
  postText: string,
  postType?: string,
  specificDetails?: string[]
): Promise<WebSearchContext> {
  // Build a focused query from details, not just generic "insights"
  const details = specificDetails?.slice(0, 2).join(" ") || "";
  const topic = mainTopic.split(" ").slice(0, 4).join(" ");

  let query: string;
  if (postType === "advice_tactical") {
    query = `${topic} ${details} tips data 2025 2026`.trim();
  } else if (postType === "hot_take_controversial") {
    query = `${topic} debate opinions ${details} 2026`.trim();
  } else {
    query = `${topic} ${details} 2026`.trim();
  }

  log.info(`Smart search query: "${query}" (from topic="${mainTopic}", type="${postType}")`);
  return searchTopic(query);
}

/**
 * Format search results for injection into generation prompt
 */
export function formatSearchForPrompt(context: WebSearchContext): string {
  if (!context.results.length) return "";

  let formatted = "\n===== WEB CONTEXT =====\n";
  formatted += `Topic search: "${context.query}"\n\n`;

  for (const result of context.results.slice(0, 3)) {
    formatted += `- ${result.title}\n  ${result.snippet}\n\n`;
  }

  formatted += "Use these insights naturally in your comment if relevant.\n";
  formatted += "===== END WEB CONTEXT =====\n";

  return formatted;
}
