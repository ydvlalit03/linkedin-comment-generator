"use client";

import { useState } from "react";
import {
  ThumbsUp,
  MessageCircle,
  Repeat2,
  Send,
  MoreHorizontal,
  Globe,
  Image,
  Video,
  Sparkles,
} from "lucide-react";

interface PostCardProps {
  post: {
    id: number;
    authorName: string;
    authorHeadline: string;
    authorProfilePic: string;
    postText: string;
    likesCount: number;
    commentsCount: number;
    sharesCount: number;
    mediaType: string;
    mediaUrls?: string;
    status: string;
    postedAt: string;
  };
  onGenerateClick?: () => void;
  isProcessing?: boolean;
  onClick?: () => void;
}

export function PostCard({
  post,
  onGenerateClick,
  isProcessing,
  onClick,
}: PostCardProps) {
  const [expanded, setExpanded] = useState(false);
  const textLimit = 280;
  const isLong = post.postText.length > textLimit;
  const displayText = expanded
    ? post.postText
    : post.postText.slice(0, textLimit);

  // Parse media
  let media: any[] = [];
  try {
    media = JSON.parse(post.mediaUrls || "[]");
  } catch {
    media = [];
  }

  const timeAgo = formatTimeAgo(post.postedAt);

  return (
    <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
      {/* Author header */}
      <div className="px-4 pt-3 pb-0">
        <div className="flex items-start gap-2.5">
          {post.authorProfilePic ? (
            <img
              src={post.authorProfilePic}
              alt=""
              className="w-12 h-12 rounded-full object-cover bg-gray-100 flex-shrink-0"
            />
          ) : (
            <div className="w-12 h-12 rounded-full bg-gradient-to-br from-blue-500 to-blue-700 flex items-center justify-center flex-shrink-0">
              <span className="text-white font-bold text-lg">
                {post.authorName.charAt(0)}
              </span>
            </div>
          )}
          <div className="flex-1 min-w-0">
            <p className="font-semibold text-[14px] text-gray-900 leading-tight hover:text-blue-600 hover:underline cursor-pointer">
              {post.authorName}
            </p>
            <p className="text-[12px] text-gray-500 leading-tight mt-0.5 line-clamp-1">
              {post.authorHeadline}
            </p>
            <div className="flex items-center gap-1 mt-0.5">
              <span className="text-[12px] text-gray-500">{timeAgo}</span>
              <span className="text-gray-400">·</span>
              <Globe className="h-3 w-3 text-gray-400" />
            </div>
          </div>
          <button className="p-1.5 hover:bg-gray-100 rounded-full -mt-0.5">
            <MoreHorizontal className="h-5 w-5 text-gray-500" />
          </button>
        </div>
      </div>

      {/* Post text */}
      <div className="px-4 pt-2 pb-1">
        <p className="text-[14px] text-gray-900 leading-[1.4] whitespace-pre-line">
          {displayText}
          {isLong && !expanded && "..."}
        </p>
        {isLong && !expanded && (
          <button
            onClick={(e) => {
              e.stopPropagation();
              setExpanded(true);
            }}
            className="text-[14px] text-gray-500 hover:text-blue-600 font-medium mt-0.5"
          >
            ...more
          </button>
        )}
      </div>

      {/* Media */}
      {media.length > 0 && (
        <div className="mt-2">
          {media[0].type === "video" ? (
            <div className="relative bg-black">
              <img
                src={media[0].thumbnail || media[0].thumbnailUrl || ""}
                alt=""
                className="w-full h-auto max-h-[400px] object-cover opacity-80"
              />
              <div className="absolute inset-0 flex items-center justify-center">
                <div className="w-14 h-14 bg-white/90 rounded-full flex items-center justify-center shadow-lg">
                  <div className="w-0 h-0 border-t-[10px] border-t-transparent border-l-[18px] border-l-gray-800 border-b-[10px] border-b-transparent ml-1" />
                </div>
              </div>
            </div>
          ) : (
            <img
              src={media[0].url || media[0].thumbnailUrl || ""}
              alt=""
              className="w-full h-auto max-h-[400px] object-cover"
            />
          )}
        </div>
      )}

      {/* Reactions bar */}
      <div className="px-4 py-1.5">
        <div className="flex items-center justify-between text-[12px] text-gray-500">
          <div className="flex items-center gap-1">
            {/* Reaction icons */}
            <div className="flex -space-x-0.5">
              <span className="inline-flex items-center justify-center w-4 h-4 rounded-full bg-blue-500 text-white text-[8px]">
                👍
              </span>
              {post.likesCount > 5 && (
                <span className="inline-flex items-center justify-center w-4 h-4 rounded-full bg-red-500 text-white text-[8px]">
                  ❤️
                </span>
              )}
              {post.likesCount > 20 && (
                <span className="inline-flex items-center justify-center w-4 h-4 rounded-full bg-green-500 text-white text-[8px]">
                  👏
                </span>
              )}
            </div>
            <span className="ml-1">{formatNumber(post.likesCount)}</span>
          </div>
          <div className="flex items-center gap-3">
            {post.commentsCount > 0 && (
              <span>{formatNumber(post.commentsCount)} comments</span>
            )}
            {post.sharesCount > 0 && (
              <span>{formatNumber(post.sharesCount)} reposts</span>
            )}
          </div>
        </div>
      </div>

      {/* Divider */}
      <div className="mx-4 border-t border-gray-200" />

      {/* Action buttons — LinkedIn style */}
      <div className="px-2 py-0.5 flex items-center">
        <ActionButton icon={ThumbsUp} label="Like" />
        <ActionButton icon={MessageCircle} label="Comment" />
        <ActionButton icon={Repeat2} label="Repost" />
        <ActionButton icon={Send} label="Send" />
      </div>

      {/* Generate comments button */}
      {post.status === "generated" ? (
        <div
          onClick={onClick}
          className="mx-4 mb-3 mt-1 py-2 bg-green-50 border border-green-200 text-green-700 rounded-lg text-[13px] font-medium text-center cursor-pointer hover:bg-green-100 transition-colors"
        >
          View Generated Comments →
        </div>
      ) : (
        <button
          onClick={(e) => {
            e.stopPropagation();
            onGenerateClick?.();
          }}
          disabled={isProcessing}
          className="mx-4 mb-3 mt-1 w-[calc(100%-2rem)] py-2 bg-blue-600 text-white rounded-lg text-[13px] font-medium hover:bg-blue-700 disabled:opacity-50 transition-colors flex items-center justify-center gap-2"
        >
          <Sparkles className="h-3.5 w-3.5" />
          {isProcessing ? "Analyzing & Generating..." : "Generate AI Comments"}
        </button>
      )}
    </div>
  );
}

function ActionButton({
  icon: Icon,
  label,
}: {
  icon: any;
  label: string;
}) {
  return (
    <button className="flex-1 flex items-center justify-center gap-1.5 py-2.5 hover:bg-gray-100 rounded-md transition-colors">
      <Icon className="h-4 w-4 text-gray-600" />
      <span className="text-[12px] font-medium text-gray-600">{label}</span>
    </button>
  );
}

function formatNumber(n: number): string {
  if (n >= 1000000) return (n / 1000000).toFixed(1) + "M";
  if (n >= 1000) return (n / 1000).toFixed(1) + "K";
  return String(n);
}

function formatTimeAgo(dateStr: string): string {
  if (!dateStr) return "";
  try {
    const date = new Date(dateStr);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffH = Math.floor(diffMs / (1000 * 60 * 60));
    if (diffH < 1) return "Just now";
    if (diffH < 24) return `${diffH}h`;
    const diffD = Math.floor(diffH / 24);
    if (diffD < 7) return `${diffD}d`;
    const diffW = Math.floor(diffD / 7);
    if (diffW < 4) return `${diffW}w`;
    const diffM = Math.floor(diffD / 30);
    if (diffM < 12) return `${diffM}mo`;
    return `${Math.floor(diffD / 365)}yr`;
  } catch {
    return dateStr;
  }
}
