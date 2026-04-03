"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { PostCard } from "@/components/post/post-card";
import { FullPageLoader } from "@/components/shared/loading-spinner";
import { toast } from "sonner";
import { Filter, Rss } from "lucide-react";

interface PostRow {
  id: number;
  authorName: string;
  authorHeadline: string;
  authorProfilePic: string;
  postText: string;
  likesCount: number;
  commentsCount: number;
  sharesCount: number;
  mediaType: string;
  mediaUrls: string;
  status: string;
  postedAt: string;
  postUrn: string;
}

export default function DashboardPage() {
  const router = useRouter();
  const [posts, setPosts] = useState<PostRow[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<string>("all");
  const [processing, setProcessing] = useState<Set<number>>(new Set());

  useEffect(() => {
    loadPosts();
  }, []);

  const loadPosts = async () => {
    try {
      const res = await fetch("/api/posts");
      if (res.ok) {
        const data = await res.json();
        setPosts(data.posts || []);
      }
    } catch {
      // DB might not exist yet
    } finally {
      setLoading(false);
    }
  };

  const handleAnalyzeAndGenerate = async (postId: number) => {
    setProcessing((prev) => new Set([...prev, postId]));

    try {
      toast.info("Analyzing & generating comments...");
      const genRes = await fetch("/api/generate-comments", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ post_id: postId }),
      });
      const genData = await genRes.json();

      if (!genRes.ok) {
        toast.error(genData.error || "Generation failed");
        return;
      }

      toast.success(`Generated ${genData.count} comments!`);

      // Update post status locally
      setPosts((prev) =>
        prev.map((p) =>
          p.id === postId ? { ...p, status: "generated" } : p
        )
      );
    } catch {
      toast.error("Something went wrong");
    } finally {
      setProcessing((prev) => {
        const next = new Set(prev);
        next.delete(postId);
        return next;
      });
    }
  };

  const filteredPosts =
    filter === "all" ? posts : posts.filter((p) => p.status === filter);

  const statusCounts = {
    all: posts.length,
    scraped: posts.filter((p) => p.status === "scraped").length,
    analyzed: posts.filter((p) => p.status === "analyzed").length,
    generated: posts.filter((p) => p.status === "generated").length,
  };

  if (loading) return <FullPageLoader text="Loading feed..." />;

  return (
    <div className="min-h-screen bg-[#f4f2ee]">
      <div className="max-w-[600px] mx-auto px-4 py-6">
        {/* Feed header */}
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <Rss className="h-5 w-5 text-gray-600" />
            <h1 className="text-lg font-semibold text-gray-900">Feed</h1>
            <span className="text-sm text-gray-500">
              · {posts.length} posts
            </span>
          </div>
        </div>

        {/* Filter pills */}
        <div className="flex items-center gap-2 mb-4 overflow-x-auto pb-1">
          {(["all", "scraped", "analyzed", "generated"] as const).map((f) => (
            <button
              key={f}
              onClick={() => setFilter(f)}
              className={`px-3 py-1 rounded-full text-[13px] font-medium whitespace-nowrap transition-colors ${
                filter === f
                  ? "bg-green-800 text-white"
                  : "bg-white text-gray-700 border border-gray-300 hover:bg-gray-50"
              }`}
            >
              {f === "all" ? "All" : f.charAt(0).toUpperCase() + f.slice(1)}
              {statusCounts[f] > 0 && (
                <span className="ml-1 text-[11px] opacity-80">
                  ({statusCounts[f]})
                </span>
              )}
            </button>
          ))}
        </div>

        {/* Sort line */}
        <div className="flex items-center gap-2 mb-3 text-[13px]">
          <div className="flex-1 border-t border-gray-300" />
          <span className="text-gray-500">
            Sort by: <span className="font-medium text-gray-700">Most recent</span>
          </span>
          <div className="flex-1 border-t border-gray-300" />
        </div>

        {/* Posts feed */}
        {filteredPosts.length === 0 ? (
          <div className="bg-white rounded-lg border border-gray-200 p-12 text-center">
            <p className="text-gray-500 mb-4">No posts in your feed yet.</p>
            <a
              href="/"
              className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-full text-sm font-medium hover:bg-blue-700"
            >
              Upload CSV to get started
            </a>
          </div>
        ) : (
          <div className="space-y-2">
            {filteredPosts.map((post) => (
              <PostCard
                key={post.id}
                post={post}
                isProcessing={processing.has(post.id)}
                onGenerateClick={() => handleAnalyzeAndGenerate(post.id)}
                onClick={() => router.push(`/post/${post.id}`)}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
