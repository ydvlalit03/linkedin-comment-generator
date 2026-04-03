import { NextRequest, NextResponse } from "next/server";
import { initDb, getDb, schema } from "@/lib/db";
import { eq } from "drizzle-orm";
import { generateComments } from "@/lib/services/comment-generator";
import { createLogger } from "@/lib/utils/logger";
import type { PostAnalysis, CommenterProfile } from "@/lib/types";

const log = createLogger("API:Generate");

const DEFAULT_PROFILE: CommenterProfile = {
  name: "Professional",
  username: "default",
  expertise: ["technology", "business"],
  tone: "professional, direct",
  avgCommentLength: 45,
  commonPhrases: [],
  realCommentExamples: [],
};

export async function POST(request: NextRequest) {
  try {
    const { postId, ragContext = "", webContext = "" } = await request.json();
    if (!postId) return NextResponse.json({ error: "No postId provided" }, { status: 400 });

    log.section(`GENERATE COMMENTS FOR POST #${postId}`);

    initDb();
    const db = getDb();

    const post = db.select().from(schema.scrapedPosts).where(eq(schema.scrapedPosts.id, postId)).get();
    if (!post) return NextResponse.json({ error: "Post not found" }, { status: 404 });

    log.info(`Post: "${(post.postText || "").slice(0, 100)}..." by ${post.authorName}`);

    // Parse analysis
    let analysis: PostAnalysis;
    try {
      analysis = JSON.parse(post.postAnalysis || "{}");
    } catch {
      return NextResponse.json({ error: "Post not analyzed yet" }, { status: 400 });
    }
    if (!analysis.postType) return NextResponse.json({ error: "Post not analyzed yet" }, { status: 400 });

    log.info(`Analysis: type=${analysis.postType} | topic="${analysis.mainTopic}" | sentiment=${analysis.sentiment}`);

    // Load commenter profile
    let profile: CommenterProfile = DEFAULT_PROFILE;
    const activeProfile = db.select().from(schema.commenterProfiles).where(eq(schema.commenterProfiles.isActive, 1)).get();

    if (activeProfile) {
      try {
        const pd = JSON.parse(activeProfile.profileData || "{}");
        profile = {
          name: activeProfile.name,
          username: activeProfile.username,
          headline: activeProfile.headline || "",
          expertise: pd.expertise || DEFAULT_PROFILE.expertise,
          tone: pd.tone || DEFAULT_PROFILE.tone,
          avgCommentLength: pd.avgCommentLength || DEFAULT_PROFILE.avgCommentLength,
          commonPhrases: pd.commonPhrases || [],
          realCommentExamples: pd.realCommentExamples || [],
          humorStyle: pd.humorStyle,
        };
        log.info(`Commenter profile: ${profile.name} | tone=${profile.tone} | expertise=${profile.expertise.join(", ")}`);
      } catch {
        log.warn("Failed to parse commenter profile — using default");
      }
    } else {
      log.warn("No commenter profile set — using default. Set one in /settings for better results.");
    }

    // Generate
    const authorCtx = {
      name: post.authorName || "",
      headline: post.authorHeadline || "",
    };
    log.info(`Post author: ${authorCtx.name} — ${authorCtx.headline}`);
    log.info(`Starting generation | RAG context: ${ragContext.length} chars | Web context: ${webContext.length} chars`);

    const comments = await generateComments(
      post.postText || "",
      analysis,
      profile,
      3,
      ragContext,
      webContext,
      authorCtx
    );

    // Store in DB
    for (const comment of comments) {
      db.insert(schema.generatedComments)
        .values({
          postId: post.id,
          text: comment.text,
          angle: comment.angle,
          variationNumber: comment.variationNumber,
          confidence: comment.confidence,
          approach: comment.approach,
          postType: comment.postType,
          wasHumanized: comment.humanized ? 1 : 0,
          qualityScore: comment.validation.qualityScore,
        })
        .run();
    }

    db.update(schema.scrapedPosts).set({ status: "generated" }).where(eq(schema.scrapedPosts.id, postId)).run();

    log.section("GENERATION RESULT");
    log.info(`${comments.length} comments saved to DB for post #${postId}`);
    comments.forEach((c, i) => {
      log.info(`  Comment #${i + 1}: [${c.angle}] "${c.text.slice(0, 60)}..." | ${c.validation.wordCount} words | quality=${c.validation.qualityScore} | confidence=${(c.confidence * 100).toFixed(0)}%`);
    });

    return NextResponse.json({ success: true, postId, count: comments.length, comments });
  } catch (error) {
    log.error("Generation failed", String(error));
    return NextResponse.json({ error: "Generation failed" }, { status: 500 });
  }
}
