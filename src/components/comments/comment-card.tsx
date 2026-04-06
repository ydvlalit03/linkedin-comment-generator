"use client";

import { useState } from "react";
import { Copy, Check, ThumbsUp, ThumbsDown, Pencil, X, Save } from "lucide-react";
import { AngleBadge } from "../shared/badge";
import { toast } from "sonner";

interface CommentCardProps {
  comment: {
    text: string;
    angle: string;
    variationNumber: number;
    confidence: number;
    commentTone?: string;
    validation: {
      qualityScore: number;
      wordCount: number;
    };
  };
  commentId?: number;
  onRegenerate?: () => void;
}

const TONE_EMOJI: Record<string, string> = {
  humorous: "😄",
  empathetic: "🤝",
  inspirational: "✨",
  provocative: "🔥",
  analytical: "🧠",
  celebratory: "🎉",
  direct: "⚡",
  storytelling: "📖",
};

export function CommentCard({ comment, commentId, onRegenerate }: CommentCardProps) {
  const [copied, setCopied] = useState(false);
  const [feedback, setFeedback] = useState<number | null>(null);
  const [editing, setEditing] = useState(false);
  const [editText, setEditText] = useState(comment.text);
  const [displayText, setDisplayText] = useState(comment.text);
  const [saving, setSaving] = useState(false);

  const wordCount = displayText.trim().split(/\s+/).filter(Boolean).length;
  const editWordCount = editText.trim().split(/\s+/).filter(Boolean).length;

  const handleCopy = async () => {
    await navigator.clipboard.writeText(displayText);
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

  const handleEditStart = () => {
    setEditText(displayText);
    setEditing(true);
  };

  const handleEditCancel = () => {
    setEditText(displayText);
    setEditing(false);
  };

  const handleEditSave = async () => {
    const trimmed = editText.trim();
    if (!trimmed) return;
    setSaving(true);
    try {
      if (commentId) {
        const res = await fetch(`/api/comments/${commentId}`, {
          method: "PUT",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ text: trimmed }),
        });
        if (!res.ok) throw new Error("Save failed");
      }
      setDisplayText(trimmed);
      setEditing(false);
      toast.success("Comment saved!");
    } catch {
      toast.error("Failed to save");
    } finally {
      setSaving(false);
    }
  };

  const confidenceColor =
    comment.confidence >= 0.8
      ? "text-green-600"
      : comment.confidence >= 0.6
        ? "text-yellow-600"
        : "text-red-600";

  const toneEmoji = comment.commentTone ? TONE_EMOJI[comment.commentTone] : null;

  return (
    <div className="bg-white rounded-xl border border-gray-200 p-4">
      {/* Header */}
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <span className="text-xs font-medium text-gray-500">
            #{comment.variationNumber}
          </span>
          <AngleBadge angle={comment.angle} />
          {toneEmoji && (
            <span
              className="text-xs text-gray-500 bg-gray-100 px-1.5 py-0.5 rounded-full"
              title={comment.commentTone}
            >
              {toneEmoji} {comment.commentTone}
            </span>
          )}
        </div>
        <div className="flex items-center gap-3 text-xs">
          <span className={`font-medium ${confidenceColor}`}>
            {(comment.confidence * 100).toFixed(0)}%
          </span>
          <span className="text-gray-400">{wordCount} words</span>
        </div>
      </div>

      {/* Comment text or edit textarea */}
      {editing ? (
        <div className="mb-3">
          <textarea
            value={editText}
            onChange={(e) => setEditText(e.target.value)}
            className="w-full text-sm text-gray-800 leading-relaxed border border-blue-300 rounded-lg p-2.5 resize-none focus:outline-none focus:ring-2 focus:ring-blue-400 min-h-[80px]"
            rows={4}
            autoFocus
          />
          <div className="flex items-center justify-between mt-1">
            <span className={`text-xs ${editWordCount > 80 ? "text-red-500" : "text-gray-400"}`}>
              {editWordCount} words
            </span>
            <span className="text-xs text-gray-400">{editText.length} chars</span>
          </div>
        </div>
      ) : (
        <p className="text-sm text-gray-800 leading-relaxed mb-4">{displayText}</p>
      )}

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
          {!editing && (
            <>
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
            </>
          )}
        </div>

        <div className="flex items-center gap-1">
          {editing ? (
            <>
              <button
                onClick={handleEditCancel}
                className="p-1.5 rounded-lg hover:bg-gray-100 text-gray-400 transition-colors"
                title="Cancel"
              >
                <X className="h-4 w-4" />
              </button>
              <button
                onClick={handleEditSave}
                disabled={saving || !editText.trim()}
                className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-green-600 text-white rounded-lg text-xs font-medium hover:bg-green-700 disabled:opacity-50 transition-colors"
              >
                <Save className="h-3.5 w-3.5" />
                {saving ? "Saving..." : "Save"}
              </button>
            </>
          ) : (
            <>
              <button
                onClick={handleEditStart}
                className="p-1.5 rounded-lg hover:bg-gray-100 text-gray-400 transition-colors"
                title="Edit comment"
              >
                <Pencil className="h-4 w-4" />
              </button>
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
            </>
          )}
        </div>
      </div>
    </div>
  );
}
