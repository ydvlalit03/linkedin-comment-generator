/**
 * Extract LinkedIn username from various URL formats
 * Ported from linkedin_scraper_api.py _extract_username()
 */
export function extractUsername(input: string): string {
  if (!input) return "";

  let cleaned = input.trim();

  // Already just a username
  if (!cleaned.includes("/") && !cleaned.includes(".")) {
    return cleaned;
  }

  // Remove trailing slash
  cleaned = cleaned.replace(/\/+$/, "");

  // Handle full URLs
  // https://www.linkedin.com/in/username
  // https://linkedin.com/in/username?param=value
  const patterns = [
    /linkedin\.com\/in\/([^/?&#]+)/i,
    /linkedin\.com\/company\/([^/?&#]+)/i,
    /linkedin\.com\/pub\/([^/?&#]+)/i,
  ];

  for (const pattern of patterns) {
    const match = cleaned.match(pattern);
    if (match) {
      return decodeURIComponent(match[1]);
    }
  }

  // Fallback: take the last path segment
  const parts = cleaned.split("/").filter(Boolean);
  if (parts.length > 0) {
    return parts[parts.length - 1].split("?")[0];
  }

  return cleaned;
}

/**
 * Validate if a string looks like a LinkedIn profile URL
 */
export function isLinkedInUrl(url: string): boolean {
  if (!url) return false;
  return /linkedin\.com\/(in|company|pub)\//i.test(url.trim());
}

/**
 * Normalize a LinkedIn URL to standard format
 */
export function normalizeLinkedInUrl(url: string): string {
  const username = extractUsername(url);
  if (!username) return url;
  return `https://www.linkedin.com/in/${username}`;
}
