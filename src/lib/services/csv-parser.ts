/**
 * CSV Parser — extract LinkedIn profile URLs/usernames from uploaded CSV
 * Handles: full URLs, bare usernames, mixed formats, any column
 */
import { parse } from "csv-parse/sync";
import { extractUsername } from "../utils/linkedin-url";

export interface ParsedProfile {
  url: string;
  username: string;
  row: number;
  type: "profile" | "post"; // whether it's a profile URL or a direct post URL
  postUrl?: string; // original post URL if type is "post"
}

/**
 * Check if a string looks like it could be a LinkedIn reference
 * More permissive than before — catches URLs, usernames, etc.
 */
function looksLikeLinkedIn(cell: string): boolean {
  if (!cell || cell.length < 3) return false;

  // Full URL
  if (/linkedin\.com/i.test(cell)) return true;

  // Could be a bare username (no spaces, no special chars except hyphen/underscore)
  // Usernames are typically: lowercase letters, numbers, hyphens
  if (/^[a-zA-Z0-9_-]+$/.test(cell) && cell.length >= 3 && cell.length <= 100) {
    return true;
  }

  return false;
}

/**
 * Extract LinkedIn URL from a cell — handles many formats
 */
function extractLinkedInFromCell(cell: string, allowBareUsername = false): { url: string; username: string; type: "profile" | "post"; postUrl?: string } | null {
  const trimmed = cell.trim();
  if (!trimmed || trimmed.length < 3) return null;

  // 1. LinkedIn POST URL — check first since it's more specific
  //    Format: linkedin.com/posts/username_post-slug-activity-123456
  const postMatch = trimmed.match(
    /linkedin\.com\/posts\/([a-zA-Z0-9_-]+?)[-_]/i
  );
  if (postMatch) {
    // Extract the clean post URL (remove tracking params for display, keep full for API)
    const fullPostUrl = trimmed.match(/https?:\/\/[^\s,;"']+/i)?.[0] || trimmed;
    return {
      url: `https://www.linkedin.com/in/${postMatch[1]}`,
      username: postMatch[1],
      type: "post",
      postUrl: fullPostUrl,
    };
  }

  // 2. Full LinkedIn profile URL (most common)
  const urlMatch = trimmed.match(
    /https?:\/\/(?:www\.)?linkedin\.com\/(?:in|company|pub)\/([^\s,;"'?&#/]+)/i
  );
  if (urlMatch) {
    const username = decodeURIComponent(urlMatch[1]);
    return {
      url: trimmed.match(/https?:\/\/[^\s,;"']+/i)?.[0] || trimmed,
      username,
      type: "profile",
    };
  }

  // 3. LinkedIn URL without protocol
  const noProtoMatch = trimmed.match(
    /(?:www\.)?linkedin\.com\/(?:in|company|pub)\/([^\s,;"'?&#/]+)/i
  );
  if (noProtoMatch) {
    const username = decodeURIComponent(noProtoMatch[1]);
    return {
      url: `https://${trimmed.startsWith("www.") ? "" : "www."}${trimmed}`,
      username,
      type: "profile",
    };
  }

  // 4. Just "linkedin.com/in/username" without any protocol
  const shortMatch = trimmed.match(
    /linkedin\.com\/in\/([^\s,;"'?&#/]+)/i
  );
  if (shortMatch) {
    return {
      url: `https://www.linkedin.com/in/${shortMatch[1]}`,
      username: decodeURIComponent(shortMatch[1]),
      type: "profile",
    };
  }

  // 5. Bare username — only in single-column CSVs (avoid picking up company names etc.)
  if (allowBareUsername && /^[a-zA-Z][a-zA-Z0-9_-]{2,99}$/.test(trimmed) && !trimmed.includes(" ")) {
    // Skip obvious non-usernames (common CSV headers, numbers, etc.)
    const skipWords = [
      "name", "url", "link", "profile", "linkedin", "email", "phone",
      "company", "title", "position", "location", "industry", "website",
      "first", "last", "full", "username", "handle", "id", "row",
      "serial", "number", "index", "sno", "true", "false", "yes", "no",
    ];
    if (skipWords.includes(trimmed.toLowerCase())) return null;

    return {
      url: `https://www.linkedin.com/in/${trimmed}`,
      username: trimmed,
      type: "profile",
    };
  }

  return null;
}

/**
 * Parse CSV content and extract LinkedIn profile URLs
 */
export function parseLinkedInCsv(csvContent: string): ParsedProfile[] {
  const profiles: ParsedProfile[] = [];
  const seen = new Set<string>();

  console.log(`[CSV] Parsing ${csvContent.length} bytes of CSV content`);

  // Detect if single-column CSV (just a list of usernames/URLs)
  let isSingleColumn = false;

  // Strategy 1: Proper CSV parsing
  try {
    const records = parse(csvContent, {
      columns: false,
      skip_empty_lines: true,
      relax_column_count: true,
      relax_quotes: true,
      trim: true,
    });

    console.log(`[CSV] Parsed ${records.length} rows`);

    // Check if single column
    if (records.length > 0) {
      const maxCols = Math.max(...records.map((r: string[]) => r.length));
      isSingleColumn = maxCols <= 1;
      console.log(`[CSV] Max columns: ${maxCols}, single column: ${isSingleColumn}`);
    }

    for (let rowIdx = 0; rowIdx < records.length; rowIdx++) {
      const row = records[rowIdx];

      for (const cell of row) {
        const cellStr = String(cell).trim();
        const result = extractLinkedInFromCell(cellStr, isSingleColumn);

        if (result && !seen.has(result.username.toLowerCase() + (result.postUrl || ""))) {
          seen.add(result.username.toLowerCase() + (result.postUrl || ""));
          profiles.push({
            url: result.url,
            username: result.username,
            row: rowIdx + 1,
            type: result.type,
            postUrl: result.postUrl,
          });
        }
      }
    }
  } catch (error) {
    console.error("[CSV] csv-parse failed, using fallback:", error);
  }

  // Strategy 2: Fallback — line by line scan (if CSV parsing found nothing or failed)
  if (profiles.length === 0) {
    console.log("[CSV] Trying line-by-line fallback...");
    const lines = csvContent.split(/[\n\r]+/);

    for (let i = 0; i < lines.length; i++) {
      const line = lines[i].trim();
      if (!line) continue;

      // Split by common delimiters
      const cells = line.split(/[,;\t|]+/);

      for (const cell of cells) {
        const trimmed = cell.trim().replace(/^["']|["']$/g, ""); // Remove quotes
        const result = extractLinkedInFromCell(trimmed, true); // fallback allows bare usernames

        if (result && !seen.has(result.username.toLowerCase() + (result.postUrl || ""))) {
          seen.add(result.username.toLowerCase() + (result.postUrl || ""));
          profiles.push({
            url: result.url,
            username: result.username,
            row: i + 1,
            type: result.type,
            postUrl: result.postUrl,
          });
        }
      }
    }
  }

  console.log(`[CSV] Found ${profiles.length} LinkedIn profiles`);
  return profiles;
}
