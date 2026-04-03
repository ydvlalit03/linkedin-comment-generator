import { NextRequest, NextResponse } from "next/server";
import { initDb, getDb, schema } from "@/lib/db";
import { eq } from "drizzle-orm";

export async function GET() {
  try {
    initDb();
    const db = getDb();

    const profile = db
      .select()
      .from(schema.commenterProfiles)
      .where(eq(schema.commenterProfiles.isActive, 1))
      .get();

    return NextResponse.json({ profile: profile || null });
  } catch {
    return NextResponse.json({ profile: null });
  }
}

export async function POST(request: NextRequest) {
  try {
    const { name, username, headline, profileData } = await request.json();

    if (!name || !username) {
      return NextResponse.json(
        { error: "Name and username required" },
        { status: 400 }
      );
    }

    initDb();
    const db = getDb();

    // Deactivate all existing profiles
    db.update(schema.commenterProfiles)
      .set({ isActive: 0 })
      .run();

    // Check if profile exists
    const existing = db
      .select()
      .from(schema.commenterProfiles)
      .where(eq(schema.commenterProfiles.username, username))
      .get();

    if (existing) {
      // Update
      db.update(schema.commenterProfiles)
        .set({
          name,
          headline: headline || "",
          profileData: JSON.stringify(profileData || {}),
          isActive: 1,
        })
        .where(eq(schema.commenterProfiles.username, username))
        .run();
    } else {
      // Insert
      db.insert(schema.commenterProfiles)
        .values({
          name,
          username,
          headline: headline || "",
          profileData: JSON.stringify(profileData || {}),
          isActive: 1,
        })
        .run();
    }

    return NextResponse.json({ success: true });
  } catch (error) {
    console.error("[API] Profile save error:", error);
    return NextResponse.json(
      { error: "Failed to save profile" },
      { status: 500 }
    );
  }
}
