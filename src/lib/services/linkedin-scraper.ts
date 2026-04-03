/**
 * LinkedIn Scraper API client — RapidAPI
 * Ported from linkedin_scraper_api.py
 */
import type { ScrapedPostData, PostMedia } from "../types";
import { extractUsername } from "../utils/linkedin-url";
import { createLogger } from "../utils/logger";

const log = createLogger("Scraper");

const BASE_URL =
  "https://linkedin-scraper-api-real-time-fast-affordable.p.rapidapi.com";

function getHeaders() {
  return {
    "X-RapidAPI-Key": process.env.RAPIDAPI_KEY || "",
    "X-RapidAPI-Host":
      process.env.RAPIDAPI_HOST ||
      "linkedin-scraper-api-real-time-fast-affordable.p.rapidapi.com",
  };
}

/**
 * Fetch latest post for a LinkedIn profile
 */
export async function fetchLatestPost(
  profileUrl: string
): Promise<ScrapedPostData | null> {
  const username = extractUsername(profileUrl);
  if (!username) return null;

  log.info(`Fetching latest post for profile: ${username}`);

  try {
    const start = Date.now();
    const response = await fetch(
      `${BASE_URL}/profile/posts?username=${encodeURIComponent(username)}&page_number=1`,
      { headers: getHeaders(), signal: AbortSignal.timeout(20000) }
    );

    if (!response.ok) {
      log.error(`HTTP ${response.status} for ${username}`);
      return null;
    }

    const data = await response.json();
    const result = normalizePostResponse(data);
    log.info(`Profile post fetched in ${Date.now() - start}ms | author=${result?.author.name} | text=${result?.post.text.slice(0, 80)}...`);
    return result;
  } catch (error) {
    log.error(`Error fetching ${username}`, String(error));
    return null;
  }
}

/**
 * Fetch post by direct URL (uses /post/detail endpoint)
 */
export async function fetchPostByUrl(
  postUrl: string
): Promise<ScrapedPostData | null> {
  log.info(`Fetching post by URL: ${postUrl.slice(0, 80)}...`);

  try {
    const start = Date.now();
    const response = await fetch(
      `${BASE_URL}/post/detail?post_url=${encodeURIComponent(postUrl)}`,
      {
        headers: {
          ...getHeaders(),
          "Content-Type": "application/json",
        },
        signal: AbortSignal.timeout(20000),
      }
    );

    if (!response.ok) {
      log.error(`HTTP ${response.status} for post URL`);
      return null;
    }

    const data = await response.json();
    const result = normalizeSinglePost(data);
    log.info(`Post fetched in ${Date.now() - start}ms | author=${result?.author.name} | text=${result?.post.text.slice(0, 80)}...`);
    return result;
  } catch (error) {
    log.error("Error fetching post", String(error));
    return null;
  }
}

// ==========================================
// Response Normalization
// ==========================================

function normalizePostResponse(data: any): ScrapedPostData | null {
  if (!data?.success && !data?.data) return null;

  // Handle different response formats
  const postsArray = data?.data || [];
  if (Array.isArray(postsArray) && postsArray.length > 0) {
    return normalizeSinglePost({ data: postsArray[0] });
  }

  // Single post format
  if (data?.data?.post) {
    return normalizeSinglePost(data);
  }

  return null;
}

function normalizeSinglePost(data: any): ScrapedPostData | null {
  const postData = data?.data;
  if (!postData) return null;

  const post = postData.post || postData;
  const author = postData.author || {};
  const media = postData.media || [];
  const stats = postData.stats || {};

  return {
    post: {
      id: post.id || post.urn?.activity_urn || "",
      url: post.url || "",
      text: post.text || "",
      type: (post.type as any) || "text",
      createdAt: post.created_at?.date || post.created_at || "",
      urn: post.urn?.activity_urn || post.id || "",
    },
    author: {
      name: author.name || "Unknown",
      headline: author.headline || "",
      profileUrl: author.profile_url || "",
      profilePicture: author.profile_picture || "",
      followers: author.followers || 0,
    },
    media: normalizeMedia(media),
    stats: {
      totalReactions: stats.total_reactions || 0,
      reactions: {
        like: stats.reactions?.like || 0,
        appreciation: stats.reactions?.appreciation || 0,
        empathy: stats.reactions?.empathy || 0,
        interest: stats.reactions?.interest || 0,
        praise: stats.reactions?.praise || 0,
        entertainment: stats.reactions?.entertainment || 0,
      },
      comments: stats.comments || 0,
      shares: stats.shares || 0,
    },
  };
}

function normalizeMedia(media: any[]): PostMedia[] {
  if (!Array.isArray(media)) return [];

  return media.map((m) => ({
    type: m.type || "image",
    url: m.video_url || m.url || m.thumbnail || "",
    thumbnailUrl: m.thumbnail || "",
    width: m.width || 0,
    height: m.height || 0,
  }));
}
