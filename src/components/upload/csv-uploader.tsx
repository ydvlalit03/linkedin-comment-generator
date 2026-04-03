"use client";

import { useState, useCallback } from "react";
import { Upload, FileText, X } from "lucide-react";

interface CsvUploaderProps {
  onUpload: (profiles: any[], batchId: string) => void;
  isLoading?: boolean;
}

export function CsvUploader({ onUpload, isLoading }: CsvUploaderProps) {
  const [file, setFile] = useState<File | null>(null);
  const [dragActive, setDragActive] = useState(false);
  const [error, setError] = useState("");
  const [uploading, setUploading] = useState(false);

  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    const droppedFile = e.dataTransfer.files?.[0];
    if (droppedFile && droppedFile.name.endsWith(".csv")) {
      setFile(droppedFile);
      setError("");
    } else {
      setError("Please upload a .csv file");
    }
  }, []);

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selected = e.target.files?.[0];
    if (selected) {
      setFile(selected);
      setError("");
    }
  };

  const handleUpload = async () => {
    if (!file) return;

    setUploading(true);
    setError("");

    try {
      const formData = new FormData();
      formData.append("file", file);

      const res = await fetch("/api/upload-csv", { method: "POST", body: formData });
      const data = await res.json();

      if (!res.ok) {
        setError(data.error || "Upload failed");
        return;
      }

      onUpload(data.profiles, data.batchId);
    } catch (err) {
      setError("Network error. Please try again.");
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="w-full max-w-xl mx-auto">
      <div
        className={`relative border-2 border-dashed rounded-xl p-8 text-center transition-colors ${
          dragActive
            ? "border-blue-500 bg-blue-50"
            : "border-gray-300 hover:border-gray-400"
        }`}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
      >
        {file ? (
          <div className="flex items-center justify-center gap-3">
            <FileText className="h-8 w-8 text-blue-600" />
            <div className="text-left">
              <p className="font-medium text-gray-900">{file.name}</p>
              <p className="text-sm text-gray-500">
                {(file.size / 1024).toFixed(1)} KB
              </p>
            </div>
            <button
              onClick={() => setFile(null)}
              className="ml-4 p-1 hover:bg-gray-100 rounded"
            >
              <X className="h-4 w-4 text-gray-500" />
            </button>
          </div>
        ) : (
          <>
            <Upload className="mx-auto h-10 w-10 text-gray-400 mb-3" />
            <p className="text-gray-600 mb-1">
              Drag & drop your CSV file here
            </p>
            <p className="text-sm text-gray-400 mb-4">
              CSV should contain LinkedIn profile URLs
            </p>
            <label className="inline-flex items-center px-4 py-2 bg-white border border-gray-300 rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-50 cursor-pointer transition-colors">
              Browse Files
              <input
                type="file"
                accept=".csv"
                onChange={handleFileSelect}
                className="hidden"
              />
            </label>
          </>
        )}
      </div>

      {error && (
        <p className="mt-3 text-sm text-red-600 text-center">{error}</p>
      )}

      {file && (
        <button
          onClick={handleUpload}
          disabled={uploading || isLoading}
          className="mt-4 w-full py-2.5 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          {uploading ? "Parsing CSV..." : "Upload & Extract URLs"}
        </button>
      )}
    </div>
  );
}
