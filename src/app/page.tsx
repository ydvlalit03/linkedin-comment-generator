"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { CsvUploader } from "@/components/upload/csv-uploader";
import { UrlListPreview } from "@/components/upload/url-list-preview";
import { LoadingSpinner } from "@/components/shared/loading-spinner";
import { toast } from "sonner";

type Step = "upload" | "preview" | "scraping" | "done";

export default function HomePage() {
  const router = useRouter();
  const [step, setStep] = useState<Step>("upload");
  const [profiles, setProfiles] = useState<any[]>([]);
  const [batchId, setBatchId] = useState("");
  const [progress, setProgress] = useState({ done: 0, total: 0 });

  const handleUpload = (parsedProfiles: any[], newBatchId: string) => {
    setProfiles(parsedProfiles);
    setBatchId(newBatchId);
    setStep("preview");
    toast.success(`Found ${parsedProfiles.length} LinkedIn profiles`);
  };

  const handleStartScraping = async (selectedProfiles: any[]) => {
    setStep("scraping");
    setProgress({ done: 0, total: selectedProfiles.length });

    try {
      const res = await fetch("/api/scrape-profiles", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ profiles: selectedProfiles, batchId }),
      });

      const data = await res.json();

      if (!res.ok) {
        toast.error(data.error || "Scraping failed");
        setStep("preview");
        return;
      }

      const parts = [];
      if (data.scraped > 0) parts.push(`${data.scraped} new`);
      if (data.cached > 0) parts.push(`${data.cached} cached`);
      if (data.failed > 0) parts.push(`${data.failed} failed`);
      toast.success(`Posts: ${parts.join(", ")}`);
      setStep("done");

      setTimeout(() => router.push("/dashboard"), 1500);
    } catch {
      toast.error("Network error. Please try again.");
      setStep("preview");
    }
  };

  return (
    <div className="max-w-4xl mx-auto px-4 py-12">
      {/* Header */}
      <div className="text-center mb-10">
        <h1 className="text-3xl font-bold text-gray-900 mb-3">
          LinkedIn Comment Generator
        </h1>
        <p className="text-gray-500 max-w-lg mx-auto">
          Upload a CSV with LinkedIn profile URLs. We&apos;ll scrape their latest
          posts, analyze content, and generate human-like comments.
        </p>
      </div>

      {/* Steps indicator */}
      <div className="flex items-center justify-center gap-3 mb-10">
        {["Upload CSV", "Select Profiles", "Scrape Posts"].map((label, i) => {
          const stepIdx =
            step === "upload" ? 0 : step === "preview" ? 1 : 2;
          return (
            <div key={label} className="flex items-center gap-3">
              <div
                className={`flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-medium ${
                  i <= stepIdx
                    ? "bg-blue-100 text-blue-700"
                    : "bg-gray-100 text-gray-500"
                }`}
              >
                <span
                  className={`w-5 h-5 rounded-full flex items-center justify-center text-[10px] ${
                    i <= stepIdx
                      ? "bg-blue-600 text-white"
                      : "bg-gray-300 text-white"
                  }`}
                >
                  {i + 1}
                </span>
                {label}
              </div>
              {i < 2 && (
                <div
                  className={`w-8 h-px ${
                    i < stepIdx ? "bg-blue-400" : "bg-gray-300"
                  }`}
                />
              )}
            </div>
          );
        })}
      </div>

      {/* Content */}
      {step === "upload" && <CsvUploader onUpload={handleUpload} />}

      {step === "preview" && (
        <UrlListPreview
          profiles={profiles}
          onStartScraping={handleStartScraping}
        />
      )}

      {step === "scraping" && (
        <div className="flex flex-col items-center py-16 gap-4">
          <LoadingSpinner size="lg" />
          <p className="text-gray-600 font-medium">
            Scraping LinkedIn posts...
          </p>
          <p className="text-sm text-gray-400">
            Processing {progress.total} profiles. This may take a minute.
          </p>
        </div>
      )}

      {step === "done" && (
        <div className="text-center py-16">
          <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <svg
              className="w-8 h-8 text-green-600"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M5 13l4 4L19 7"
              />
            </svg>
          </div>
          <p className="text-lg font-medium text-gray-900 mb-2">
            Posts scraped successfully!
          </p>
          <p className="text-sm text-gray-500">
            Redirecting to dashboard...
          </p>
        </div>
      )}
    </div>
  );
}
