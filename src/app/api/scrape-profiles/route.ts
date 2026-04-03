import { NextRequest, NextResponse } from "next/server";
import { fetchLatestPost, fetchPostByUrl } from "@/lib/services/linkedin-scraper";
import { initDb, getDb, schema } from "@/lib/db";
import { eq, or, like } from "drizzle-orm";

interface ProfileInput {
  url: string;
  username: string;
  type: "profile" | "post";
  postUrl?: string;
}

export async function POST(request: NextRequest) {
  try {
    const { profiles, batchId } = await request.json();

    let profileList: ProfileInput[] = [];
    if (profiles && Array.isArray(profiles)) {
      profileList = profiles;
    }

    if (profileList.length === 0) {
      return NextResponse.json({ error: "No profiles provided" }, { status: 400 });
    }

    if (!batchId) {
      return NextResponse.json({ error: "No batchId provided" }, { status: 400 });
    }

    initDb();
    const db = getDb();

    const results: any[] = [];
    const cached: any[] = [];
    const errors: any[] = [];

    for (let i = 0; i < profileList.length; i++) {
      const profile = profileList[i];

      try {
        // ===== CACHE CHECK — skip already scraped posts =====
        const lookupUrl = profile.postUrl || profile.url;

        // Check by postUrl (for post type) or profileUrl (for profile type)
        const existing = db
          .select()
          .from(schema.scrapedPosts)
          .where(
            or(
              // Match by post URL (contains the slug part)
              like(schema.scrapedPosts.postUrl, `%${profile.username}%`),
              // Match exact profile URL
              eq(schema.scrapedPosts.profileUrl, profile.url)
            )
          )
          .all();

        // For post type: check if this exact post URL is already in DB
        if (profile.type === "post" && profile.postUrl) {
          const exactMatch = existing.find((e) => {
            // Match by post URN or by URL containing same activity ID
            const activityMatch = profile.postUrl!.match(/activity-(\d+)/);
            if (activityMatch && e.postUrn === activityMatch[1]) return true;
            if (e.postUrl && profile.postUrl!.includes(profile.username)) {
              // Same author + similar URL = same post
              return e.postUrl.includes(profile.username);
            }
            return false;
          });

          if (exactMatch) {
            console.log(`[Scrape] CACHE HIT: ${profile.username} (post already in DB, id=${exactMatch.id})`);
            cached.push({
              id: exactMatch.id,
              url: profile.url,
              author: exactMatch.authorName,
              postText: (exactMatch.postText || "").slice(0, 150) + "...",
              status: exactMatch.status,
              cached: true,
            });
            continue;
          }
        }

        // For profile type: check if we already have a post from this profile
        if (profile.type === "profile" && existing.length > 0) {
          const latest = existing[0];
          console.log(`[Scrape] CACHE HIT: ${profile.username} (profile already in DB, id=${latest.id})`);
          cached.push({
            id: latest.id,
            url: profile.url,
            author: latest.authorName,
            postText: (latest.postText || "").slice(0, 150) + "...",
            status: latest.status,
            cached: true,
          });
          continue;
        }

        // ===== NOT CACHED — scrape from API =====
        let postData;

        if (profile.type === "post" && profile.postUrl) {
          console.log(`[Scrape] Fetching post: ${profile.postUrl.slice(0, 80)}...`);
          postData = await fetchPostByUrl(profile.postUrl);
        } else {
          console.log(`[Scrape] Fetching latest post for: ${profile.username}`);
          postData = await fetchLatestPost(profile.url);
        }

        if (!postData) {
          errors.push({ url: profile.url, error: "No post data returned" });
          continue;
        }

        // ===== DEDUPLICATE by postUrn before insert =====
        if (postData.post.urn) {
          const urnExists = db
            .select()
            .from(schema.scrapedPosts)
            .where(eq(schema.scrapedPosts.postUrn, postData.post.urn))
            .get();

          if (urnExists) {
            console.log(`[Scrape] DEDUP: Post URN ${postData.post.urn} already exists (id=${urnExists.id})`);
            cached.push({
              id: urnExists.id,
              url: profile.url,
              author: urnExists.authorName,
              postText: (urnExists.postText || "").slice(0, 150) + "...",
              status: urnExists.status,
              cached: true,
            });
            continue;
          }
        }

        // Insert new post
        const inserted = db
          .insert(schema.scrapedPosts)
          .values({
            profileUrl: profile.url,
            authorName: postData.author.name,
            authorHeadline: postData.author.headline,
            authorProfilePic: postData.author.profilePicture,
            postText: postData.post.text,
            postUrl: postData.post.url || profile.postUrl || "",
            postUrn: postData.post.urn || "",
            likesCount: postData.stats.totalReactions,
            commentsCount: postData.stats.comments,
            sharesCount: postData.stats.shares,
            mediaType: postData.post.type,
            mediaUrls: JSON.stringify(postData.media),
            postedAt: postData.post.createdAt,
            status: "scraped",
            batchId,
          })
          .returning()
          .get();

        results.push({
          id: inserted.id,
          url: profile.url,
          author: postData.author.name,
          postText: postData.post.text.slice(0, 150) + "...",
          stats: postData.stats,
          status: "scraped",
        });
      } catch (error) {
        console.error(`[Scrape] Error for ${profile.username}:`, error);
        errors.push({
          url: profile.url,
          error: error instanceof Error ? error.message : "Unknown error",
        });
      }

      // Rate limiting between API calls only (not for cached)
      if (i < profileList.length - 1 && !cached.find((c) => c.url === profileList[i].url)) {
        await new Promise((r) => setTimeout(r, 1500));
      }
    }

    return NextResponse.json({
      success: true,
      batchId,
      scraped: results.length,
      cached: cached.length,
      failed: errors.length,
      results,
      cached_posts: cached,
      errors,
    });
  } catch (error) {
    console.error("[API] Scrape profiles error:", error);
    return NextResponse.json({ error: "Scraping failed" }, { status: 500 });
  }
}
