"use client";

const COLORS: Record<string, string> = {
  green: "bg-green-100 text-green-800",
  blue: "bg-blue-100 text-blue-800",
  orange: "bg-orange-100 text-orange-800",
  red: "bg-red-100 text-red-800",
  gray: "bg-gray-100 text-gray-800",
  purple: "bg-purple-100 text-purple-800",
  yellow: "bg-yellow-100 text-yellow-800",
};

// Map angles to color categories
const ANGLE_COLORS: Record<string, string> = {
  WHISPERED_TRUTH: "orange",
  HIDDEN_COST: "orange",
  SECRET_NOBODY_ASKED: "orange",
  REAL_RISK: "red",
  ME_TOO_DEEPER: "blue",
  LIVED_IT_DEEPER: "blue",
  MINDSET_SHIFT: "purple",
  INEVITABLE_NOT_SURPRISING: "green",
  CALL_OUT_VALUE: "green",
  VALIDATION: "green",
  ASK_QUESTION: "yellow",
  SHARE_EXPERIENCE: "blue",
  ADD_DATA: "purple",
  EARNED_INSIGHT: "blue",
  FAILURE_AS_CURRICULUM: "orange",
  INTENSIFY_SURGICAL: "red",
  SEE_WHOLE_GAME: "purple",
  REFRAME_SMARTER: "purple",
};

export function Badge({
  text,
  color,
}: {
  text: string;
  color?: string;
}) {
  const colorClass = COLORS[color || "gray"] || COLORS.gray;
  return (
    <span
      className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${colorClass}`}
    >
      {text}
    </span>
  );
}

export function AngleBadge({ angle }: { angle: string }) {
  const color = ANGLE_COLORS[angle] || "gray";
  const label = angle.replace(/_/g, " ").toLowerCase();
  return <Badge text={label} color={color} />;
}

export function StatusBadge({ status }: { status: string }) {
  const colorMap: Record<string, string> = {
    scraped: "gray",
    analyzed: "blue",
    generated: "green",
    error: "red",
  };
  return <Badge text={status} color={colorMap[status] || "gray"} />;
}
