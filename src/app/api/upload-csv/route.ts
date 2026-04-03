import { NextRequest, NextResponse } from "next/server";
import { parseLinkedInCsv } from "@/lib/services/csv-parser";
import { randomUUID } from "crypto";

export async function POST(request: NextRequest) {
  try {
    const formData = await request.formData();
    const file = formData.get("file") as File | null;

    if (!file) {
      return NextResponse.json({ error: "No file uploaded" }, { status: 400 });
    }

    const csvContent = await file.text();
    console.log(`[Upload] File: ${file.name}, Size: ${csvContent.length} bytes`);
    console.log(`[Upload] First 500 chars:\n${csvContent.slice(0, 500)}`);

    const profiles = parseLinkedInCsv(csvContent);

    if (profiles.length === 0) {
      return NextResponse.json(
        {
          error: "No LinkedIn profile URLs found in CSV. Supported formats: full LinkedIn URLs (https://linkedin.com/in/username), bare usernames (satyanadella), or LinkedIn post URLs.",
          preview: csvContent.slice(0, 300),
        },
        { status: 400 }
      );
    }

    const batchId = randomUUID();

    return NextResponse.json({
      success: true,
      batchId,
      count: profiles.length,
      profiles: profiles.map((p) => ({
        url: p.url,
        username: p.username,
        row: p.row,
        type: p.type,
        postUrl: p.postUrl,
      })),
    });
  } catch (error) {
    console.error("[API] Upload CSV error:", error);
    return NextResponse.json(
      { error: "Failed to parse CSV" },
      { status: 500 }
    );
  }
}
