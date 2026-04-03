"use client";

import { useState } from "react";
import { Copy, Check, ThumbsUp, ThumbsDown, RefreshCw } from "lucide-react";
import { AngleBadge } from "../shared/badge";
import { toast } from "sonner";

interface CommentCardProps {
  comment: {
    text: string;
    angle: string;
    variationNumber: number;
    confidence: number;
    validation: {
      qualityScore: number;
      wordCount: number;
    };
  };
  commentId?: number;
  onRegenerate?: () => void;
}

export function CommentCard({
  comment,
  commentId,
  onRegenerate,
}: CommentCardProps) {
  const [copied, setCopied] = useState(false);
  const [feedback, setFeedback] = useState<number | null>(null);

  const handleCopy = async () => {
    await navigator.clipboard.writeText(comment.text);
    setCopied(true);
    toast.success("Copied to clipboard!");
    setTimeout(() => setCopied(false), 2000);
  };

  const handleFeedback = async (rating: number) => {
    setFeedback(rating);
    if (commentId) {
      try {
        await fetch("/api/feedback", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ commentId, rating }),
        });
      } catch {
        // Silent fail for feedback
      }
    }
  };

  const confidenceColor =
    comment.confidence >= 0.8
      ? "text-green-600"
      : comment.confidence >= 0.6
        ? "text-yellow-600"
        : "text-red-600";

  return (
    <div className="bg-white rounded-xl border border-gray-200 p-4">
      {/* Header */}
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <span className="text-xs font-medium text-gray-500">
            #{comment.variationNumber}
          </span>
          <AngleBadge angle={comment.angle} />
        </div>
        <div className="flex items-center gap-3 text-xs">
          <span className={`font-medium ${confidenceColor}`}>
            {(comment.confidence * 100).toFixed(0)}%
          </span>
          <span className="text-gray-400">
            {comment.validation.wordCount} words
          </span>
        </div>
      </div>

      {/* Comment text */}
      <p className="text-sm text-gray-800 leading-relaxed mb-4">
        {comment.text}
      </p>

      {/* Quality bar */}
      <div className="mb-3">
        <div className="h-1.5 bg-gray-100 rounded-full overflow-hidden">
          <div
            className={`h-full rounded-full transition-all ${
              comment.validation.qualityScore >= 80
                ? "bg-green-500"
                : comment.validation.qualityScore >= 60
                  ? "bg-yellow-500"
                  : "bg-red-500"
            }`}
            style={{ width: `${comment.validation.qualityScore}%` }}
          />
        </div>
      </div>

      {/* Actions */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-1">
          <button
            onClick={() => handleFeedback(1)}
            className={`p-1.5 rounded-lg transition-colors ${
              feedback === 1
                ? "bg-green-100 text-green-600"
                : "hover:bg-gray-100 text-gray-400"
            }`}
          >
            <ThumbsUp className="h-4 w-4" />
          </button>
          <button
            onClick={() => handleFeedback(-1)}
            className={`p-1.5 rounded-lg transition-colors ${
              feedback === -1
                ? "bg-red-100 text-red-600"
                : "hover:bg-gray-100 text-gray-400"
            }`}
          >
            <ThumbsDown className="h-4 w-4" />
          </button>
        </div>

        <div className="flex items-center gap-1">
          {onRegenerate && (
            <button
              onClick={onRegenerate}
              className="p-1.5 rounded-lg hover:bg-gray-100 text-gray-400 transition-colors"
            >
              <RefreshCw className="h-4 w-4" />
            </button>
          )}
          <button
            onClick={handleCopy}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-blue-600 text-white rounded-lg text-xs font-medium hover:bg-blue-700 transition-colors"
          >
            {copied ? (
              <>
                <Check className="h-3.5 w-3.5" />
                Copied
              </>
            ) : (
              <>
                <Copy className="h-3.5 w-3.5" />
                Copy
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
}
