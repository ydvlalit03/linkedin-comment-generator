import { NextRequest, NextResponse } from "next/server";
import { initDb, getDb, schema } from "@/lib/db";
import { eq } from "drizzle-orm";
import { analyzePost } from "@/lib/services/post-analyzer";
import { shouldSearch, getTopicInsights, formatSearchForPrompt } from "@/lib/services/web-search";
import { getRelevantExamples, formatRagForPrompt } from "@/lib/services/rag-service";
import { createLogger } from "@/lib/utils/logger";
import type { PostMedia } from "@/lib/types";

const log = createLogger("API:Analyze");

export async function POST(request: NextRequest) {
  try {
    const { postId } = await request.json();
    if (!postId) return NextResponse.json({ error: "No postId provided" }, { status: 400 });

    log.section(`ANALYZE POST #${postId}`);

    initDb();
    const db = getDb();

    const post = db.select().from(schema.scrapedPosts).where(eq(schema.scrapedPosts.id, postId)).get();
    if (!post) return NextResponse.json({ error: "Post not found" }, { status: 404 });

    log.info(`Post loaded: "${(post.postText || "").slice(0, 100)}..." by ${post.authorName}`);

    let media: PostMedia[] = [];
    try { media = JSON.parse(post.mediaUrls || "[]"); } catch { media = []; }
    log.info(`Media: ${media.length} items (${media.map(m => m.type).join(", ") || "none"})`);

    // Step 1: Groq Analysis
    log.substep(1, 3, "Analyzing post with Groq AI...");
    const analysis = await analyzePost(post.postText || "", media, {
      name: post.authorName || "",
      headline: post.authorHeadline || "",
    });

    // Step 2: Web Search
    log.substep(2, 3, "Checking if web search needed...");
    let webSearchContext = null;
    if (shouldSearch(analysis.postType, analysis.mainTopic, post.postText || "")) {
      log.info("Web search triggered — fetching topic insights...");
      webSearchContext = await getTopicInsights(
        analysis.mainTopic,
        post.postText || "",
        analysis.postType,
        analysis.specificDetails
      );
      log.info(`Web search results: ${webSearchContext.results.length} results for "${webSearchContext.query}"`);
    }

    // Step 3: RAG Examples
    log.substep(3, 3, "Fetching RAG reference comments...");
    const ragExamples = getRelevantExamples(analysis.postType, analysis.mainTopic);
    log.info(`RAG examples: ${ragExamples.length} found for type "${analysis.postType}"`);

    // Save to DB
    db.update(schema.scrapedPosts)
      .set({
        postAnalysis: JSON.stringify(analysis),
        webSearchContext: webSearchContext ? JSON.stringify(webSearchContext) : null,
        status: "analyzed",
      })
      .where(eq(schema.scrapedPosts.id, postId))
      .run();

    log.info("Analysis saved to DB — status: analyzed");

    return NextResponse.json({
      success: true,
      postId,
      analysis,
      webSearch: webSearchContext ? { query: webSearchContext.query, resultCount: webSearchContext.results.length } : null,
      ragExamples: ragExamples.length,
      ragContext: formatRagForPrompt(ragExamples),
      webContext: webSearchContext ? formatSearchForPrompt(webSearchContext) : "",
    });
  } catch (error) {
    log.error("Analysis failed", String(error));
    return NextResponse.json({ error: "Analysis failed" }, { status: 500 });
  }
}
