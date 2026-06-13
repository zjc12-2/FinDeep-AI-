"use client";

import { Citation, TimelineEvent } from "@/lib/types";
import { SourceTracing } from "./SourceTracing";
import { EventTimeline } from "./EventTimeline";

interface Props {
  activeTab: "sources" | "timeline";
  onTabChange: (tab: "sources" | "timeline") => void;
  citations: Record<string, Citation>;
  selectedRef: string | null;
  taskId: string;
}

export function SidePanel({ activeTab, onTabChange, citations, selectedRef, taskId }: Props) {
  return (
    <div className="w-96 shrink-0 border border-border rounded-xl bg-white overflow-hidden">
      <div className="flex border-b border-border">
        <button
          onClick={() => onTabChange("sources")}
          className={`flex-1 py-3 text-sm font-medium transition-colors ${
            activeTab === "sources"
              ? "text-primary border-b-2 border-primary"
              : "text-muted-foreground hover:text-foreground"
          }`}
        >
          溯源面板
        </button>
        <button
          onClick={() => onTabChange("timeline")}
          className={`flex-1 py-3 text-sm font-medium transition-colors ${
            activeTab === "timeline"
              ? "text-primary border-b-2 border-primary"
              : "text-muted-foreground hover:text-foreground"
          }`}
        >
          事件时间轴
        </button>
      </div>
      <div className="p-4 h-[calc(100vh-280px)] overflow-y-auto">
        {activeTab === "sources" ? (
          <SourceTracing citations={citations} selectedRef={selectedRef} />
        ) : (
          <EventTimeline taskId={taskId} />
        )}
      </div>
    </div>
  );
}
