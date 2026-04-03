import { drizzle } from "drizzle-orm/better-sqlite3";
import Database from "better-sqlite3";
import * as schema from "./schema";
import path from "path";

const DB_PATH = path.join(process.cwd(), "data", "linkedin-comments.db");

let _db: ReturnType<typeof drizzle> | null = null;
let _sqlite: Database.Database | null = null;

export function getDb() {
  if (!_db) {
    _sqlite = new Database(DB_PATH);
    _sqlite.pragma("journal_mode = WAL");
    _sqlite.pragma("foreign_keys = ON");
    _db = drizzle(_sqlite, { schema });
  }
  return _db;
}

export function getSqlite() {
  if (!_sqlite) {
    getDb(); // Initialize both
  }
  return _sqlite!;
}

// Initialize tables on first import
export function initDb() {
  const sqlite = getSqlite();
  sqlite.exec(`
    CREATE TABLE IF NOT EXISTS scraped_posts (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      profile_url TEXT NOT NULL,
      author_name TEXT DEFAULT '',
      author_headline TEXT DEFAULT '',
      author_profile_pic TEXT DEFAULT '',
      post_text TEXT DEFAULT '',
      post_url TEXT DEFAULT '',
      post_urn TEXT DEFAULT '',
      likes_count INTEGER DEFAULT 0,
      comments_count INTEGER DEFAULT 0,
      shares_count INTEGER DEFAULT 0,
      media_type TEXT DEFAULT 'text',
      media_urls TEXT DEFAULT '[]',
      posted_at TEXT DEFAULT '',
      post_analysis TEXT,
      web_search_context TEXT,
      status TEXT DEFAULT 'scraped',
      batch_id TEXT NOT NULL,
      created_at TEXT DEFAULT (datetime('now'))
    );

    CREATE TABLE IF NOT EXISTS generated_comments (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      post_id INTEGER NOT NULL REFERENCES scraped_posts(id),
      text TEXT NOT NULL,
      angle TEXT DEFAULT 'GENERAL_ENGAGEMENT',
      variation_number INTEGER DEFAULT 1,
      confidence REAL DEFAULT 0,
      approach TEXT DEFAULT '',
      post_type TEXT DEFAULT '',
      was_humanized INTEGER DEFAULT 0,
      quality_score INTEGER DEFAULT 0,
      created_at TEXT DEFAULT (datetime('now'))
    );

    CREATE TABLE IF NOT EXISTS comment_feedback (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      comment_id INTEGER NOT NULL REFERENCES generated_comments(id),
      rating INTEGER DEFAULT 0,
      was_used INTEGER DEFAULT 0,
      actual_likes INTEGER,
      actual_replies INTEGER,
      created_at TEXT DEFAULT (datetime('now'))
    );

    CREATE TABLE IF NOT EXISTS reference_comments (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      post_content TEXT DEFAULT '',
      comment_text TEXT DEFAULT '',
      likes INTEGER DEFAULT 0,
      replies INTEGER DEFAULT 0,
      post_type TEXT DEFAULT '',
      comment_angle TEXT DEFAULT '',
      topic TEXT DEFAULT '',
      engagement_score REAL DEFAULT 0
    );

    CREATE TABLE IF NOT EXISTS commenter_profiles (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      name TEXT NOT NULL,
      username TEXT NOT NULL UNIQUE,
      headline TEXT DEFAULT '',
      profile_data TEXT DEFAULT '{}',
      is_active INTEGER DEFAULT 1,
      created_at TEXT DEFAULT (datetime('now'))
    );
  `);
}

export { schema };
