/**
 * RAG Service — SQLite-based retrieval of high-engagement reference comments
 * Replaces ChromaDB with simple SQLite FTS matching
 */
import { getSqlite } from "../db";

export interface RagResult {
  commentText: string;
  postContent: string;
  angle: string;
  engagementScore: number;
  likes: number;
}

/**
 * Retrieve similar high-engagement comments for a post type
 */
export function getRelevantExamples(
  postType: string,
  mainTopic: string,
  limit = 5
): RagResult[] {
  try {
    const sqlite = getSqlite();

    // First try: match by post_type
    let results = sqlite
      .prepare(
        `SELECT comment_text, post_content, comment_angle, engagement_score, likes
         FROM reference_comments
         WHERE post_type = ?
         ORDER BY engagement_score DESC
         LIMIT ?`
      )
      .all(postType, limit) as any[];

    // Fallback: keyword search in post content
    if (results.length < 3 && mainTopic) {
      const keywords = mainTopic.split(" ").filter((w: string) => w.length > 3);
      if (keywords.length > 0) {
        const likeClause = keywords
          .map(() => "post_content LIKE ?")
          .join(" OR ");
        const likeParams = keywords.map((k: string) => `%${k}%`);

        const moreResults = sqlite
          .prepare(
            `SELECT comment_text, post_content, comment_angle, engagement_score, likes
             FROM reference_comments
             WHERE ${likeClause}
             ORDER BY engagement_score DESC
             LIMIT ?`
          )
          .all(...likeParams, limit - results.length) as any[];

        results = [...results, ...moreResults];
      }
    }

    return results.map((r: any) => ({
      commentText: r.comment_text,
      postContent: r.post_content,
      angle: r.comment_angle,
      engagementScore: r.engagement_score,
      likes: r.likes,
    }));
  } catch (error) {
    console.error("[RAG] Error:", error);
    return [];
  }
}

/**
 * Format RAG results for prompt injection
 */
export function formatRagForPrompt(examples: RagResult[]): string {
  if (examples.length === 0) return "";

  let formatted = "\n===== HIGH-ENGAGEMENT EXAMPLES =====\n";
  formatted +=
    "These real comments received high engagement. Learn from their angles and style:\n\n";

  for (let i = 0; i < examples.length; i++) {
    const ex = examples[i];
    formatted += `Example ${i + 1}: ${ex.angle || "GENERAL"}\n`;
    formatted += `Post: "${ex.postContent?.slice(0, 150)}..."\n`;
    formatted += `Comment: "${ex.commentText}"\n`;
    formatted += `Engagement: ${ex.likes} likes (score: ${ex.engagementScore})\n\n`;
  }

  formatted += "===== END EXAMPLES =====\n";
  return formatted;
}
