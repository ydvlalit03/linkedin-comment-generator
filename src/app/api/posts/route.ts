import { NextResponse } from "next/server";
import { initDb, getDb, schema } from "@/lib/db";
import { desc } from "drizzle-orm";

export async function GET() {
  try {
    initDb();
    const db = getDb();

    const posts = db
      .select()
      .from(schema.scrapedPosts)
      .orderBy(desc(schema.scrapedPosts.id))
      .all();

    return NextResponse.json({ posts });
  } catch (error) {
    console.error("[API] List posts error:", error);
    return NextResponse.json({ posts: [] });
  }
}
