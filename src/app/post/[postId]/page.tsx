"use client";

import { useState, useEffect, use } from "react";
import { PostCard } from "@/components/post/post-card";
import { PostMedia } from "@/components/post/post-media";
import { CommentCard } from "@/components/comments/comment-card";
import { FullPageLoader } from "@/components/shared/loading-spinner";
import { Badge, AngleBadge } from "@/components/shared/badge";
import { Sparkles, ArrowLeft, Mic2 } from "lucide-react";
import { toast } from "sonner";
import Link from "next/link";

interface PostDetail {
  post: any;
  analysis: any;
  comments: any[];
  media: any[];
  suggestedCommentTone: string;
  usedCommentTone: string;
}

const TONES = [
  { value: "humorous",     label: "Humorous",     emoji: "😄" },
  { value: "empathetic",   label: "Empathetic",   emoji: "🤝" },
  { value: "inspirational",label: "Inspirational",emoji: "✨" },
  { value: "provocative",  label: "Provocative",  emoji: "🔥" },
  { value: "analytical",   label: "Analytical",   emoji: "🧠" },
  { value: "celebratory",  label: "Celebratory",  emoji: "🎉" },
  { value: "direct",       label: "Direct",       emoji: "⚡" },
  { value: "storytelling", label: "Storytelling", emoji: "📖" },
];

export default function PostDetailPage({
  params,
}: {
  params: Promise<{ postId: string }>;
}) {
  const { postId } = use(params);
  const [data, setData] = useState<PostDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [regenerating, setRegenerating] = useState(false);
  const [selectedTone, setSelectedTone] = useState<string>("");
  const [toneChanged, setToneChanged] = useState(false);

  useEffect(() => {
    loadPost();
  }, [postId]);

  const loadPost = async () => {
    try {
      const res = await fetch(`/api/post/${postId}`);
      if (res.ok) {
        const json = await res.json();
        setData(json);
        // Set tone: prefer last-used tone, fallback to LLM suggestion
        const tone = json.usedCommentTone || json.suggestedCommentTone || "direct";
        setSelectedTone(tone);
        setToneChanged(false);
      }
    } catch {
      toast.error("Failed to load post");
    } finally {
      setLoading(false);
    }
  };

  const handleRegenerate = async (toneOverride?: string) => {
    setRegenerating(true);
    try {
      const tone = toneOverride ?? selectedTone;
      const genRes = await fetch("/api/generate-comments", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ post_id: Number(postId), comment_tone: tone }),
      });

      if (genRes.ok) {
        toast.success(`Comments regenerated with ${tone} tone!`);
        await loadPost();
        setToneChanged(false);
      } else {
        toast.error("Regeneration failed");
      }
    } catch {
      toast.error("Regeneration failed");
    } finally {
      setRegenerating(false);
    }
  };

  const handleToneChange = (tone: string) => {
    setSelectedTone(tone);
    setToneChanged(tone !== (data?.usedCommentTone || data?.suggestedCommentTone || "direct"));
  };

  if (loading) return <FullPageLoader text="Loading post..." />;
  if (!data) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-16 text-center">
        <p className="text-gray-500">Post not found</p>
      </div>
    );
  }

  const { post, analysis, comments, media } = data;
  const currentToneObj = TONES.find((t) => t.value === selectedTone);

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      {/* Back link */}
      <Link
        href="/dashboard"
        className="inline-flex items-center gap-1.5 text-sm text-gray-500 hover:text-gray-700 mb-6"
      >
        <ArrowLeft className="h-4 w-4" />
        Back to Dashboard
      </Link>

      {/* Post */}
      <PostCard post={post} />

      {/* Media */}
      {media && media.length > 0 && (
        <div className="mt-4">
          <PostMedia media={media} />
        </div>
      )}

      {/* Analysis */}
      {analysis && (
        <div className="mt-6 bg-white rounded-xl border border-gray-200 p-4">
          <h3 className="font-medium text-gray-900 mb-3">Post Analysis</h3>
          <div className="flex flex-wrap gap-2 mb-3">
            <Badge text={analysis.postType} color="blue" />
            <Badge text={analysis.sentiment} color="green" />
            <Badge text={analysis.emotionalTone} color="purple" />
          </div>
          <p className="text-sm text-gray-600 mb-2">
            <span className="font-medium">Topic:</span> {analysis.mainTopic}
          </p>
          {analysis.specificDetails?.length > 0 && (
            <div className="text-sm text-gray-600">
              <span className="font-medium">Key details:</span>{" "}
              {analysis.specificDetails.join(", ")}
            </div>
          )}
          {analysis.bestResponseAngles?.length > 0 && (
            <div className="flex flex-wrap gap-1.5 mt-3">
              <span className="text-xs text-gray-500">Recommended angles:</span>
              {analysis.bestResponseAngles.map((angle: string) => (
                <AngleBadge key={angle} angle={angle} />
              ))}
            </div>
          )}
        </div>
      )}

      {/* Comment Tone Selector */}
      <div className="mt-4 bg-white rounded-xl border border-gray-200 p-4">
        <div className="flex items-center gap-2 mb-3">
          <Mic2 className="h-4 w-4 text-gray-500" />
          <h3 className="font-medium text-gray-900 text-sm">Comment Tone</h3>
          {data.suggestedCommentTone && (
            <span className="text-xs text-gray-400 bg-gray-100 px-2 py-0.5 rounded-full">
              AI suggested: {data.suggestedCommentTone}
            </span>
          )}
        </div>
        <div className="flex flex-wrap gap-2">
          {TONES.map((tone) => (
            <button
              key={tone.value}
              onClick={() => handleToneChange(tone.value)}
              className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-medium transition-all border ${
                selectedTone === tone.value
                  ? "bg-blue-600 text-white border-blue-600"
                  : "bg-white text-gray-600 border-gray-200 hover:border-blue-300 hover:text-blue-600"
              }`}
            >
              <span>{tone.emoji}</span>
              {tone.label}
            </button>
          ))}
        </div>
        {toneChanged && (
          <p className="text-xs text-blue-600 mt-2">
            Tone changed — regenerate to apply.
          </p>
        )}
      </div>

      {/* Generated Comments */}
      <div className="mt-8">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-bold text-gray-900">
            Generated Comments ({comments.length})
            {currentToneObj && (
              <span className="ml-2 text-sm font-normal text-gray-500">
                · {currentToneObj.emoji} {currentToneObj.label}
              </span>
            )}
          </h2>
          <button
            onClick={() => handleRegenerate()}
            disabled={regenerating}
            className={`inline-flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors disabled:opacity-50 ${
              toneChanged
                ? "bg-blue-600 text-white hover:bg-blue-700 ring-2 ring-blue-300"
                : "bg-blue-600 text-white hover:bg-blue-700"
            }`}
          >
            <Sparkles className="h-4 w-4" />
            {regenerating
              ? "Regenerating..."
              : toneChanged
              ? `Regenerate as ${currentToneObj?.label}`
              : "Regenerate All"}
          </button>
        </div>

        {comments.length === 0 ? (
          <p className="text-gray-500 text-center py-8">
            No comments generated yet.
          </p>
        ) : (
          <div className="grid grid-cols-1 gap-4">
            {comments.map((comment: any, idx: number) => (
              <CommentCard
                key={comment.id ?? idx}
                comment={comment}
                commentId={comment.id}
                onRegenerate={() => handleRegenerate()}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
