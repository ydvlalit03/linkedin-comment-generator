"use client";

import { Play } from "lucide-react";

interface PostMediaProps {
  media: Array<{
    type: string;
    url: string;
    thumbnailUrl?: string;
    width?: number;
    height?: number;
  }>;
}

export function PostMedia({ media }: PostMediaProps) {
  if (!media || media.length === 0) return null;

  return (
    <div className="space-y-2">
      {media.map((item, idx) => (
        <div key={idx} className="relative rounded-lg overflow-hidden bg-gray-100">
          {item.type === "video" ? (
            <div className="relative">
              <img
                src={item.thumbnailUrl || item.url}
                alt="Video thumbnail"
                className="w-full h-48 object-cover"
              />
              <div className="absolute inset-0 flex items-center justify-center">
                <div className="w-12 h-12 bg-black/60 rounded-full flex items-center justify-center">
                  <Play className="h-5 w-5 text-white ml-0.5" />
                </div>
              </div>
            </div>
          ) : (
            <img
              src={item.url}
              alt="Post media"
              className="w-full h-48 object-cover"
            />
          )}
        </div>
      ))}
    </div>
  );
}
