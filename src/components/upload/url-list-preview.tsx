"use client";

import { useState } from "react";
import { User, FileText } from "lucide-react";

interface Profile {
  url: string;
  username: string;
  row: number;
  type?: "profile" | "post";
  postUrl?: string;
}

interface UrlListPreviewProps {
  profiles: Profile[];
  onStartScraping: (selectedProfiles: Profile[]) => void;
  isLoading?: boolean;
}

export function UrlListPreview({
  profiles,
  onStartScraping,
  isLoading,
}: UrlListPreviewProps) {
  const [selected, setSelected] = useState<Set<number>>(
    new Set(profiles.map((_, i) => i))
  );

  const toggle = (idx: number) => {
    const next = new Set(selected);
    if (next.has(idx)) next.delete(idx);
    else next.add(idx);
    setSelected(next);
  };

  const selectAll = () => setSelected(new Set(profiles.map((_, i) => i)));
  const deselectAll = () => setSelected(new Set());

  const handleStart = () => {
    const selectedProfiles = profiles.filter((_, i) => selected.has(i));
    onStartScraping(selectedProfiles);
  };

  return (
    <div className="w-full max-w-2xl mx-auto">
      <div className="flex items-center justify-between mb-3">
        <h3 className="font-medium text-gray-900">
          Found {profiles.length} LinkedIn {profiles.some(p => p.type === "post") ? "posts" : "profiles"}
        </h3>
        <div className="flex gap-2 text-sm">
          <button
            onClick={selectAll}
            className="text-blue-600 hover:underline"
          >
            Select all
          </button>
          <span className="text-gray-300">|</span>
          <button
            onClick={deselectAll}
            className="text-blue-600 hover:underline"
          >
            Deselect all
          </button>
        </div>
      </div>

      <div className="bg-white rounded-lg border border-gray-200 divide-y divide-gray-100 max-h-80 overflow-y-auto">
        {profiles.map((profile, idx) => (
          <label
            key={idx}
            className="flex items-center gap-3 px-4 py-3 hover:bg-gray-50 cursor-pointer"
          >
            <input
              type="checkbox"
              checked={selected.has(idx)}
              onChange={() => toggle(idx)}
              className="h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
            />
            {profile.type === "post" ? (
              <FileText className="h-5 w-5 text-orange-400 flex-shrink-0" />
            ) : (
              <User className="h-5 w-5 text-gray-400 flex-shrink-0" />
            )}
            <div className="min-w-0 flex-1">
              <div className="flex items-center gap-2">
                <p className="text-sm font-medium text-gray-900 truncate">
                  {profile.username}
                </p>
                {profile.type === "post" && (
                  <span className="text-[10px] px-1.5 py-0.5 bg-orange-100 text-orange-700 rounded font-medium">
                    POST
                  </span>
                )}
              </div>
              <p className="text-xs text-gray-500 truncate">
                {profile.postUrl?.slice(0, 80) || profile.url}
              </p>
            </div>
          </label>
        ))}
      </div>

      <button
        onClick={handleStart}
        disabled={selected.size === 0 || isLoading}
        className="mt-4 w-full py-2.5 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
      >
        {isLoading
          ? "Scraping posts..."
          : `Scrape Posts (${selected.size} selected)`}
      </button>
    </div>
  );
}
