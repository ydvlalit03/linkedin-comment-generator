"use client";

import { useState, useEffect } from "react";
import { toast } from "sonner";
import { Save, User } from "lucide-react";

export default function SettingsPage() {
  const [profile, setProfile] = useState({
    name: "",
    username: "",
    headline: "",
    expertise: "",
    tone: "professional, direct",
    avgCommentLength: 45,
    commonPhrases: "",
    realCommentExamples: "",
  });
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    loadProfile();
  }, []);

  const loadProfile = async () => {
    try {
      const res = await fetch("/api/profile");
      if (res.ok) {
        const data = await res.json();
        if (data.profile) {
          const p = data.profile;
          const pd = JSON.parse(p.profileData || "{}");
          setProfile({
            name: p.name || "",
            username: p.username || "",
            headline: p.headline || "",
            expertise: (pd.expertise || []).join(", "),
            tone: pd.tone || "professional, direct",
            avgCommentLength: pd.avgCommentLength || 45,
            commonPhrases: (pd.commonPhrases || []).join("\n"),
            realCommentExamples: (pd.realCommentExamples || []).join("\n"),
          });
        }
      }
    } catch {
      // No profile yet
    }
  };

  const handleSave = async () => {
    setSaving(true);
    try {
      const res = await fetch("/api/profile", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          name: profile.name,
          username: profile.username,
          headline: profile.headline,
          profileData: {
            expertise: profile.expertise
              .split(",")
              .map((s) => s.trim())
              .filter(Boolean),
            tone: profile.tone,
            avgCommentLength: profile.avgCommentLength,
            commonPhrases: profile.commonPhrases
              .split("\n")
              .map((s) => s.trim())
              .filter(Boolean),
            realCommentExamples: profile.realCommentExamples
              .split("\n")
              .map((s) => s.trim())
              .filter(Boolean),
          },
        }),
      });

      if (res.ok) {
        toast.success("Profile saved!");
      } else {
        toast.error("Failed to save");
      }
    } catch {
      toast.error("Network error");
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold text-gray-900 mb-2">Settings</h1>
      <p className="text-sm text-gray-500 mb-8">
        Configure your commenter profile. This determines how generated comments
        sound.
      </p>

      {/* API Keys Info */}
      <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-8">
        <p className="text-sm text-yellow-800">
          API keys are configured via <code className="font-mono">.env.local</code>.
          Set <code>GROQ_API_KEY</code>, <code>RAPIDAPI_KEY</code>,
          and optionally <code>GOOGLE_SEARCH_API_KEY</code> +{" "}
          <code>GOOGLE_SEARCH_ENGINE_ID</code>.
        </p>
      </div>

      {/* Profile Form */}
      <div className="bg-white rounded-xl border border-gray-200 p-6 space-y-5">
        <div className="flex items-center gap-2 mb-2">
          <User className="h-5 w-5 text-blue-600" />
          <h2 className="font-semibold text-gray-900">Commenter Profile</h2>
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Name
            </label>
            <input
              type="text"
              value={profile.name}
              onChange={(e) =>
                setProfile({ ...profile, name: e.target.value })
              }
              placeholder="Vidhant Jain"
              className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              LinkedIn Username
            </label>
            <input
              type="text"
              value={profile.username}
              onChange={(e) =>
                setProfile({ ...profile, username: e.target.value })
              }
              placeholder="vidhantjain"
              className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Headline
          </label>
          <input
            type="text"
            value={profile.headline}
            onChange={(e) =>
              setProfile({ ...profile, headline: e.target.value })
            }
            placeholder="SDE @ Company | AI/ML Enthusiast"
            className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Expertise (comma-separated)
          </label>
          <input
            type="text"
            value={profile.expertise}
            onChange={(e) =>
              setProfile({ ...profile, expertise: e.target.value })
            }
            placeholder="AI/ML, full-stack development, product management"
            className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          />
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Tone
            </label>
            <select
              value={profile.tone}
              onChange={(e) =>
                setProfile({ ...profile, tone: e.target.value })
              }
              className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="professional, direct">Professional & Direct</option>
              <option value="casual, friendly">Casual & Friendly</option>
              <option value="witty, sharp">Witty & Sharp</option>
              <option value="thoughtful, analytical">Thoughtful & Analytical</option>
              <option value="empathetic, supportive">Empathetic & Supportive</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Avg Comment Length (words)
            </label>
            <input
              type="number"
              value={profile.avgCommentLength}
              onChange={(e) =>
                setProfile({
                  ...profile,
                  avgCommentLength: Number(e.target.value),
                })
              }
              min={15}
              max={100}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Common Phrases (one per line)
          </label>
          <textarea
            value={profile.commonPhrases}
            onChange={(e) =>
              setProfile({ ...profile, commonPhrases: e.target.value })
            }
            rows={3}
            placeholder={"the real question is\nhonestly though\nthis hits different"}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Real Comment Examples (one per line)
          </label>
          <textarea
            value={profile.realCommentExamples}
            onChange={(e) =>
              setProfile({ ...profile, realCommentExamples: e.target.value })
            }
            rows={4}
            placeholder="Paste your actual LinkedIn comments here, one per line. These help match your voice."
            className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          />
        </div>

        <button
          onClick={handleSave}
          disabled={saving || !profile.name || !profile.username}
          className="w-full py-2.5 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 disabled:opacity-50 transition-colors flex items-center justify-center gap-2"
        >
          <Save className="h-4 w-4" />
          {saving ? "Saving..." : "Save Profile"}
        </button>
      </div>
    </div>
  );
}
