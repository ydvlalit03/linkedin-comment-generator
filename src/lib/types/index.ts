// ==========================================
// LinkedIn Comment Generator - Type Definitions
// ==========================================

export interface LinkedInPost {
  id: string;
  url: string;
  text: string;
  type: "text" | "image" | "video" | "article" | "document";
  createdAt: string;
  urn?: string;
}

export interface PostAuthor {
  name: string;
  headline: string;
  profileUrl: string;
  profilePicture: string;
  followers?: number;
}

export interface PostStats {
  totalReactions: number;
  reactions: {
    like: number;
    appreciation: number;
    empathy: number;
    interest: number;
    praise: number;
    entertainment: number;
  };
  comments: number;
  shares: number;
}

export interface PostMedia {
  type: "image" | "video" | "article" | "document";
  url: string;
  thumbnailUrl?: string;
  width?: number;
  height?: number;
}

export interface ScrapedPostData {
  post: LinkedInPost;
  author: PostAuthor;
  media: PostMedia[];
  stats: PostStats;
}

export interface PostAnalysis {
  postType: string;
  mainTopic: string;
  sentiment: "positive" | "negative" | "neutral";
  emotionalTone: string;
  postTone: string; // casual/formal/listicle/storytelling/data-heavy
  specificDetails: string[];
  keyInsights: string[];
  bestResponseAngles: string[];
}

export interface WebSearchResult {
  title: string;
  snippet: string;
  url: string;
}

export interface WebSearchContext {
  query: string;
  results: WebSearchResult[];
  summary: string;
}

export interface GeneratedComment {
  text: string;
  confidence: number;
  approach: string;
  postType: string;
  angle: string;
  variationNumber: number;
  validation: CommentValidation;
  humanized: boolean;
}

export interface CommentValidation {
  valid: boolean;
  issues: string[];
  warnings: string[];
  wordCount: number;
  qualityScore: number;
  targetRange: string;
  distanceFromTarget: number;
}

export interface CommenterProfile {
  id?: number;
  name: string;
  username: string;
  headline?: string;
  expertise: string[];
  tone: string;
  avgCommentLength: number;
  commonPhrases: string[];
  realCommentExamples: string[];
  humorStyle?: string;
  punctuationProfile?: {
    questionMarks: number;
    exclamationMarks: number;
  };
}

export interface ReferenceComment {
  postContent: string;
  commentText: string;
  likes: number;
  replies: number;
  postType: string;
  commentAngle: string;
  engagementScore: number;
}

// Database row types
export interface ScrapedPostRow {
  id: number;
  profileUrl: string;
  authorName: string;
  authorHeadline: string;
  authorProfilePic: string;
  postText: string;
  postUrl: string;
  postUrn: string;
  likesCount: number;
  commentsCount: number;
  sharesCount: number;
  mediaType: string;
  mediaUrls: string; // JSON string
  postedAt: string;
  postAnalysis: string | null; // JSON string
  webSearchContext: string | null; // JSON string
  status: "scraped" | "analyzed" | "generated" | "error";
  batchId: string;
  createdAt: string;
}

export interface GeneratedCommentRow {
  id: number;
  postId: number;
  text: string;
  angle: string;
  variationNumber: number;
  confidence: number;
  approach: string;
  postType: string;
  wasHumanized: number;
  qualityScore: number;
  createdAt: string;
}

export type CommentAngleKey =
  | "INEVITABLE_NOT_SURPRISING"
  | "REAL_COST"
  | "FAILURE_AS_CURRICULUM"
  | "LIVED_IT_DEEPER"
  | "WHISPERED_TRUTH"
  | "EARNED_INSIGHT"
  | "ME_TOO_DEEPER"
  | "HIDDEN_COST"
  | "MINDSET_SHIFT"
  | "REAL_RISK"
  | "SECRET_NOBODY_ASKED"
  | "INTENSIFY_SURGICAL"
  | "SEE_WHOLE_GAME"
  | "PATTERN_NOT_MAD"
  | "VALIDATION"
  | "SHARE_EXPERIENCE"
  | "ADD_DATA"
  | "ASK_QUESTION"
  | "REFRAME_SMARTER"
  | "CALL_OUT_VALUE"
  | "GENERAL_ENGAGEMENT";
