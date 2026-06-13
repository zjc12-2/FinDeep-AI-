"use client";

import { cn } from "@/lib/utils";

interface Props {
  active: "balanced" | "bull" | "bear";
  onChange: (mode: "balanced" | "bull" | "bear") => void;
}

const OPTIONS = [
  { key: "bull" as const, label: "🐂 多方", desc: "投资机会视角" },
  { key: "balanced" as const, label: "⚖ 均衡", desc: "综合报告" },
  { key: "bear" as const, label: "🐻 空方", desc: "风险警示视角" },
];

export function ViewToggle({ active, onChange }: Props) {
  return (
    <div className="flex gap-1 bg-muted p-1 rounded-xl shadow-lg">
      {OPTIONS.map((opt) => (
        <button
          key={opt.key}
          onClick={() => onChange(opt.key)}
          className={cn(
            "px-4 py-2 rounded-lg text-sm font-medium transition-all",
            active === opt.key
              ? "bg-white text-foreground shadow-sm"
              : "text-muted-foreground hover:text-foreground"
          )}
          title={opt.desc}
        >
          {opt.label}
        </button>
      ))}
    </div>
  );
}
