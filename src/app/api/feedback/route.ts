import { NextRequest, NextResponse } from "next/server";
import { initDb, getDb, schema } from "@/lib/db";

export async function POST(request: NextRequest) {
  try {
    const { commentId, rating, wasUsed, actualLikes, actualReplies } =
      await request.json();

    if (!commentId) {
      return NextResponse.json(
        { error: "No commentId provided" },
        { status: 400 }
      );
    }

    initDb();
    const db = getDb();

    db.insert(schema.commentFeedback)
      .values({
        commentId,
        rating: rating || 0,
        wasUsed: wasUsed ? 1 : 0,
        actualLikes: actualLikes || null,
        actualReplies: actualReplies || null,
      })
      .run();

    return NextResponse.json({ success: true });
  } catch (error) {
    console.error("[API] Feedback error:", error);
    return NextResponse.json(
      { error: "Failed to save feedback" },
      { status: 500 }
    );
  }
}
