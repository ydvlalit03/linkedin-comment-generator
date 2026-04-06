"use client";

import { useState, useEffect } from "react";
import { FullPageLoader } from "@/components/shared/loading-spinner";
import { BarChart2, MessageSquare, FileText, Star, ThumbsUp, ThumbsDown } from "lucide-react";

interface AnalyticsData {
  totals: {
    posts: number;
    comments: number;
    feedback: number;
    avgConfidence: number;
  };
  angles: { angle: string; count: number; avgConfidence: number; avgQuality: number }[];
  postTypes: { postType: string; count: number }[];
  qualityDistribution: { excellent: number; good: number; fair: number; poor: number };
  tones: { tone: string; count: number }[];
  feedback: { positive: number; negative: number; neutral: number };
}

const TONE_EMOJI: Record<string, string> = {
  humorous: "😄", empathetic: "🤝", inspirational: "✨",
  provocative: "🔥", analytical: "🧠", celebratory: "🎉",
  direct: "⚡", storytelling: "📖",
};

const ANGLE_LABELS: Record<string, string> = {
  WHISPERED_TRUTH: "Whispered Truth", HIDDEN_COST: "Hidden Cost",
  SECRET_NOBODY_ASKED: "Secret Nobody Asked", LIVED_IT_DEEPER: "Lived It Deeper",
  ME_TOO_DEEPER: "Me Too Deeper", MINDSET_SHIFT: "Mindset Shift",
  INEVITABLE_NOT_SURPRISING: "Inevitable", CALL_OUT_VALUE: "Call Out Value",
  ASK_QUESTION: "Ask Question", SHARE_EXPERIENCE: "Share Experience",
  ADD_DATA: "Add Data", INTENSIFY_SURGICAL: "Intensify",
  REFRAME_SMARTER: "Reframe", EARNED_INSIGHT: "Earned Insight",
  REAL_RISK: "Real Risk", FAILURE_AS_CURRICULUM: "Failure Lesson",
  SEE_WHOLE_GAME: "See Whole Game", VALIDATION: "Validation",
  GENERAL_ENGAGEMENT: "General",
};

function StatCard({
  icon: Icon, label, value, sub, color,
}: {
  icon: any; label: string; value: string | number; sub?: string; color: string;
}) {
  return (
    <div className="bg-white rounded-xl border border-gray-200 p-5">
      <div className={`inline-flex items-center justify-center w-10 h-10 rounded-lg mb-3 ${color}`}>
        <Icon className="h-5 w-5" />
      </div>
      <div className="text-2xl font-bold text-gray-900">{value}</div>
      <div className="text-sm text-gray-500 mt-0.5">{label}</div>
      {sub && <div className="text-xs text-gray-400 mt-1">{sub}</div>}
    </div>
  );
}

function HBar({ value, max, color }: { value: number; max: number; color: string }) {
  const pct = max > 0 ? Math.round((value / max) * 100) : 0;
  return (
    <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
      <div className={`h-full rounded-full transition-all ${color}`} style={{ width: `${pct}%` }} />
    </div>
  );
}

export default function AnalyticsPage() {
  const [data, setData] = useState<AnalyticsData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch("/api/analytics")
      .then((r) => r.json())
      .then(setData)
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <FullPageLoader text="Loading analytics..." />;

  if (!data || data.totals.comments === 0) {
    return (
      <div className="max-w-5xl mx-auto px-4 py-16 text-center">
        <BarChart2 className="h-12 w-12 text-gray-300 mx-auto mb-4" />
        <p className="text-gray-500 font-medium">No data yet</p>
        <p className="text-sm text-gray-400 mt-1">Generate some comments first to see analytics.</p>
      </div>
    );
  }

  const maxAngleCount = Math.max(...data.angles.map((a) => a.count), 1);
  const maxTypeCount = Math.max(...data.postTypes.map((p) => p.count), 1);
  const maxToneCount = Math.max(...data.tones.map((t) => t.count), 1);
  const totalFeedback = data.feedback.positive + data.feedback.negative + data.feedback.neutral;
  const qualTotal = Object.values(data.qualityDistribution).reduce((a, b) => a + b, 0);

  return (
    <div className="max-w-5xl mx-auto px-4 py-8">
      <div className="flex items-center gap-3 mb-6">
        <BarChart2 className="h-6 w-6 text-gray-700" />
        <h1 className="text-xl font-bold text-gray-900">Analytics</h1>
      </div>

      {/* Summary cards */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-8">
        <StatCard
          icon={FileText} label="Posts Scraped"
          value={data.totals.posts} color="bg-blue-50 text-blue-600"
        />
        <StatCard
          icon={MessageSquare} label="Comments Generated"
          value={data.totals.comments} color="bg-purple-50 text-purple-600"
        />
        <StatCard
          icon={Star} label="Avg Confidence"
          value={`${Math.round((data.totals.avgConfidence || 0) * 100)}%`}
          color="bg-yellow-50 text-yellow-600"
        />
        <StatCard
          icon={ThumbsUp} label="Feedback Received"
          value={data.totals.feedback}
          sub={totalFeedback > 0 ? `${Math.round((data.feedback.positive / totalFeedback) * 100)}% positive` : undefined}
          color="bg-green-50 text-green-600"
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Angle performance */}
        <div className="bg-white rounded-xl border border-gray-200 p-5">
          <h2 className="font-semibold text-gray-900 mb-4 text-sm">Angle Performance</h2>
          <div className="space-y-3">
            {data.angles.slice(0, 10).map((a) => (
              <div key={a.angle}>
                <div className="flex items-center justify-between text-xs mb-1">
                  <span className="text-gray-700 font-medium">
                    {ANGLE_LABELS[a.angle] || a.angle}
                  </span>
                  <div className="flex items-center gap-3 text-gray-400">
                    <span>{a.count}x</span>
                    <span className="text-green-600 font-medium">
                      {Math.round(a.avgConfidence * 100)}%
                    </span>
                  </div>
                </div>
                <HBar value={a.count} max={maxAngleCount} color="bg-blue-500" />
              </div>
            ))}
          </div>
        </div>

        {/* Post type distribution */}
        <div className="bg-white rounded-xl border border-gray-200 p-5">
          <h2 className="font-semibold text-gray-900 mb-4 text-sm">Post Types</h2>
          <div className="space-y-3">
            {data.postTypes.map((p) => (
              <div key={p.postType}>
                <div className="flex items-center justify-between text-xs mb-1">
                  <span className="text-gray-700 font-medium capitalize">
                    {p.postType.replace(/_/g, " ")}
                  </span>
                  <span className="text-gray-400">{p.count}</span>
                </div>
                <HBar value={p.count} max={maxTypeCount} color="bg-purple-500" />
              </div>
            ))}
          </div>
        </div>

        {/* Quality distribution */}
        <div className="bg-white rounded-xl border border-gray-200 p-5">
          <h2 className="font-semibold text-gray-900 mb-4 text-sm">Quality Distribution</h2>
          <div className="space-y-3">
            {[
              { label: "Excellent (80-100)", key: "excellent", color: "bg-green-500" },
              { label: "Good (60-79)", key: "good", color: "bg-blue-500" },
              { label: "Fair (40-59)", key: "fair", color: "bg-yellow-500" },
              { label: "Poor (<40)", key: "poor", color: "bg-red-400" },
            ].map(({ label, key, color }) => {
              const val = data.qualityDistribution[key as keyof typeof data.qualityDistribution];
              const pct = qualTotal > 0 ? Math.round((val / qualTotal) * 100) : 0;
              return (
                <div key={key}>
                  <div className="flex items-center justify-between text-xs mb-1">
                    <span className="text-gray-700 font-medium">{label}</span>
                    <span className="text-gray-400">{val} ({pct}%)</span>
                  </div>
                  <HBar value={val} max={qualTotal} color={color} />
                </div>
              );
            })}
          </div>
        </div>

        {/* Tone & Feedback */}
        <div className="flex flex-col gap-6">
          {/* Tone distribution */}
          {data.tones.length > 0 && (
            <div className="bg-white rounded-xl border border-gray-200 p-5">
              <h2 className="font-semibold text-gray-900 mb-4 text-sm">Comment Tones Used</h2>
              <div className="space-y-3">
                {data.tones.map((t) => (
                  <div key={t.tone}>
                    <div className="flex items-center justify-between text-xs mb-1">
                      <span className="text-gray-700 font-medium flex items-center gap-1.5">
                        <span>{TONE_EMOJI[t.tone] || ""}</span>
                        <span className="capitalize">{t.tone}</span>
                      </span>
                      <span className="text-gray-400">{t.count}</span>
                    </div>
                    <HBar value={t.count} max={maxToneCount} color="bg-indigo-500" />
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Feedback */}
          {data.totals.feedback > 0 && (
            <div className="bg-white rounded-xl border border-gray-200 p-5">
              <h2 className="font-semibold text-gray-900 mb-4 text-sm">User Feedback</h2>
              <div className="flex items-center gap-4">
                <div className="flex-1 text-center">
                  <div className="text-2xl font-bold text-green-600">{data.feedback.positive}</div>
                  <div className="text-xs text-gray-500 mt-1 flex items-center justify-center gap-1">
                    <ThumbsUp className="h-3 w-3" /> Liked
                  </div>
                </div>
                <div className="flex-1 text-center">
                  <div className="text-2xl font-bold text-red-500">{data.feedback.negative}</div>
                  <div className="text-xs text-gray-500 mt-1 flex items-center justify-center gap-1">
                    <ThumbsDown className="h-3 w-3" /> Disliked
                  </div>
                </div>
                <div className="flex-1 text-center">
                  <div className="text-2xl font-bold text-gray-500">{data.feedback.neutral}</div>
                  <div className="text-xs text-gray-500 mt-1">Skipped</div>
                </div>
              </div>
              {totalFeedback > 0 && (
                <div className="mt-4 h-2 bg-gray-100 rounded-full overflow-hidden flex">
                  <div
                    className="h-full bg-green-500"
                    style={{ width: `${(data.feedback.positive / totalFeedback) * 100}%` }}
                  />
                  <div
                    className="h-full bg-red-400"
                    style={{ width: `${(data.feedback.negative / totalFeedback) * 100}%` }}
                  />
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
