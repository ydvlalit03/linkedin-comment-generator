"use client";

import { useState, useEffect, use } from "react";
import { PostCard } from "@/components/post/post-card";
import { PostMedia } from "@/components/post/post-media";
import { CommentCard } from "@/components/comments/comment-card";
import { FullPageLoader } from "@/components/shared/loading-spinner";
import { Badge, AngleBadge } from "@/components/shared/badge";
import { Sparkles, ArrowLeft } from "lucide-react";
import { toast } from "sonner";
import Link from "next/link";

interface PostDetail {
  post: any;
  analysis: any;
  comments: any[];
  media: any[];
}

export default function PostDetailPage({
  params,
}: {
  params: Promise<{ postId: string }>;
}) {
  const { postId } = use(params);
  const [data, setData] = useState<PostDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [regenerating, setRegenerating] = useState(false);

  useEffect(() => {
    loadPost();
  }, [postId]);

  const loadPost = async () => {
    try {
      const res = await fetch(`/api/post/${postId}`);
      if (res.ok) {
        const json = await res.json();
        setData(json);
      }
    } catch {
      toast.error("Failed to load post");
    } finally {
      setLoading(false);
    }
  };

  const handleRegenerate = async () => {
    setRegenerating(true);
    try {
      // Re-analyze
      const analyzeRes = await fetch("/api/analyze-post", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ postId: Number(postId) }),
      });
      const analyzeData = await analyzeRes.json();

      // Re-generate
      const genRes = await fetch("/api/generate-comments", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          postId: Number(postId),
          ragContext: analyzeData.ragContext || "",
          webContext: analyzeData.webContext || "",
        }),
      });

      if (genRes.ok) {
        toast.success("Comments regenerated!");
        loadPost();
      }
    } catch {
      toast.error("Regeneration failed");
    } finally {
      setRegenerating(false);
    }
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

      {/* Generated Comments */}
      <div className="mt-8">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-bold text-gray-900">
            Generated Comments ({comments.length})
          </h2>
          <button
            onClick={handleRegenerate}
            disabled={regenerating}
            className="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700 disabled:opacity-50 transition-colors"
          >
            <Sparkles className="h-4 w-4" />
            {regenerating ? "Regenerating..." : "Regenerate All"}
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
                key={idx}
                comment={comment}
                commentId={comment.id}
                onRegenerate={handleRegenerate}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
