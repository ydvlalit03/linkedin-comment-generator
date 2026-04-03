import { NextRequest, NextResponse } from "next/server";
import { initDb, getDb, schema } from "@/lib/db";
import { eq } from "drizzle-orm";

export async function GET(
  _request: NextRequest,
  { params }: { params: Promise<{ postId: string }> }
) {
  try {
    const { postId } = await params;
    initDb();
    const db = getDb();

    const post = db
      .select()
      .from(schema.scrapedPosts)
      .where(eq(schema.scrapedPosts.id, Number(postId)))
      .get();

    if (!post) {
      return NextResponse.json({ error: "Post not found" }, { status: 404 });
    }

    // Load comments
    const comments = db
      .select()
      .from(schema.generatedComments)
      .where(eq(schema.generatedComments.postId, Number(postId)))
      .all();

    // Parse stored JSON
    let analysis = null;
    try {
      analysis = post.postAnalysis ? JSON.parse(post.postAnalysis) : null;
    } catch {
      analysis = null;
    }

    let media = [];
    try {
      media = JSON.parse(post.mediaUrls || "[]");
    } catch {
      media = [];
    }

    return NextResponse.json({
      post: {
        id: post.id,
        authorName: post.authorName,
        authorHeadline: post.authorHeadline,
        authorProfilePic: post.authorProfilePic,
        postText: post.postText,
        postUrl: post.postUrl,
        likesCount: post.likesCount,
        commentsCount: post.commentsCount,
        sharesCount: post.sharesCount,
        mediaType: post.mediaType,
        status: post.status,
        postedAt: post.postedAt,
      },
      analysis,
      media,
      comments: comments.map((c) => ({
        id: c.id,
        text: c.text,
        angle: c.angle,
        variationNumber: c.variationNumber,
        confidence: c.confidence,
        approach: c.approach,
        postType: c.postType,
        validation: {
          qualityScore: c.qualityScore,
          wordCount: c.text?.split(/\s+/).length || 0,
        },
      })),
    });
  } catch (error) {
    console.error("[API] Get post error:", error);
    return NextResponse.json(
      { error: "Failed to load post" },
      { status: 500 }
    );
  }
}
