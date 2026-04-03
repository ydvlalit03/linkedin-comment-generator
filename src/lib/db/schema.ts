import { sqliteTable, text, integer, real } from "drizzle-orm/sqlite-core";
import { sql } from "drizzle-orm";

export const scrapedPosts = sqliteTable("scraped_posts", {
  id: integer("id").primaryKey({ autoIncrement: true }),
  profileUrl: text("profile_url").notNull(),
  authorName: text("author_name").default(""),
  authorHeadline: text("author_headline").default(""),
  authorProfilePic: text("author_profile_pic").default(""),
  postText: text("post_text").default(""),
  postUrl: text("post_url").default(""),
  postUrn: text("post_urn").default(""),
  likesCount: integer("likes_count").default(0),
  commentsCount: integer("comments_count").default(0),
  sharesCount: integer("shares_count").default(0),
  mediaType: text("media_type").default("text"),
  mediaUrls: text("media_urls").default("[]"), // JSON array
  postedAt: text("posted_at").default(""),
  postAnalysis: text("post_analysis"), // JSON blob
  webSearchContext: text("web_search_context"), // JSON blob
  status: text("status").default("scraped"), // scraped | analyzed | generated | error
  batchId: text("batch_id").notNull(),
  createdAt: text("created_at").default(sql`(datetime('now'))`),
});

export const generatedComments = sqliteTable("generated_comments", {
  id: integer("id").primaryKey({ autoIncrement: true }),
  postId: integer("post_id")
    .notNull()
    .references(() => scrapedPosts.id),
  text: text("text").notNull(),
  angle: text("angle").default("GENERAL_ENGAGEMENT"),
  variationNumber: integer("variation_number").default(1),
  confidence: real("confidence").default(0),
  approach: text("approach").default(""),
  postType: text("post_type").default(""),
  wasHumanized: integer("was_humanized").default(0),
  qualityScore: integer("quality_score").default(0),
  createdAt: text("created_at").default(sql`(datetime('now'))`),
});

export const commentFeedback = sqliteTable("comment_feedback", {
  id: integer("id").primaryKey({ autoIncrement: true }),
  commentId: integer("comment_id")
    .notNull()
    .references(() => generatedComments.id),
  rating: integer("rating").default(0), // -1, 0, 1
  wasUsed: integer("was_used").default(0),
  actualLikes: integer("actual_likes"),
  actualReplies: integer("actual_replies"),
  createdAt: text("created_at").default(sql`(datetime('now'))`),
});

export const referenceComments = sqliteTable("reference_comments", {
  id: integer("id").primaryKey({ autoIncrement: true }),
  postContent: text("post_content").default(""),
  commentText: text("comment_text").default(""),
  likes: integer("likes").default(0),
  replies: integer("replies").default(0),
  postType: text("post_type").default(""),
  commentAngle: text("comment_angle").default(""),
  topic: text("topic").default(""),
  engagementScore: real("engagement_score").default(0),
});

export const commenterProfiles = sqliteTable("commenter_profiles", {
  id: integer("id").primaryKey({ autoIncrement: true }),
  name: text("name").notNull(),
  username: text("username").notNull().unique(),
  headline: text("headline").default(""),
  profileData: text("profile_data").default("{}"), // JSON
  isActive: integer("is_active").default(1),
  createdAt: text("created_at").default(sql`(datetime('now'))`),
});
