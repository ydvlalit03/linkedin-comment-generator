"use client";

export function LoadingSpinner({ size = "md" }: { size?: "sm" | "md" | "lg" }) {
  const sizeClasses = {
    sm: "h-4 w-4 border-2",
    md: "h-6 w-6 border-2",
    lg: "h-10 w-10 border-3",
  };

  return (
    <div
      className={`${sizeClasses[size]} rounded-full border-gray-300 border-t-blue-600 animate-spin`}
    />
  );
}

export function FullPageLoader({ text = "Loading..." }: { text?: string }) {
  return (
    <div className="flex flex-col items-center justify-center py-20 gap-3">
      <LoadingSpinner size="lg" />
      <p className="text-sm text-gray-500">{text}</p>
    </div>
  );
}
