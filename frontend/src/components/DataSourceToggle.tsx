"use client";

import { Database, Newspaper } from "lucide-react";
import { cn } from "@/lib/utils";

interface Props {
  akshare: boolean;
  news: boolean;
  onAkshareChange: (v: boolean) => void;
  onNewsChange: (v: boolean) => void;
}

export function DataSourceToggle({ akshare, news, onAkshareChange, onNewsChange }: Props) {
  return (
    <div className="flex gap-4 items-center">
      <span className="text-sm text-muted-foreground">数据源：</span>
      <button
        onClick={() => onAkshareChange(!akshare)}
        className={cn(
          "flex items-center gap-2 px-4 py-2 rounded-lg border text-sm transition-colors",
          akshare
            ? "border-primary bg-primary/5 text-primary"
            : "border-border text-muted-foreground hover:border-primary/30"
        )}
      >
        <Database className="w-4 h-4" />
        金融数据API
        {akshare && <span className="text-green-500">✓</span>}
      </button>
      <button
        onClick={() => onNewsChange(!news)}
        className={cn(
          "flex items-center gap-2 px-4 py-2 rounded-lg border text-sm transition-colors",
          news
            ? "border-primary bg-primary/5 text-primary"
            : "border-border text-muted-foreground hover:border-primary/30"
        )}
      >
        <Newspaper className="w-4 h-4" />
        新闻舆情
        {news && <span className="text-green-500">✓</span>}
      </button>
    </div>
  );
}
