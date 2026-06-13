"use client";

import { useEffect, useState, useCallback } from "react";
import { useParams } from "next/navigation";
import { api } from "@/lib/api";
import { createSSEConnection } from "@/lib/sse";
import { ResearchReport, Citation, SSEEvent } from "@/lib/types";
import { ProgressPanel } from "@/components/ProgressPanel";
import { ReportContent } from "@/components/ReportContent";
import { SidePanel } from "@/components/SidePanel";
import { AskFollowUp } from "@/components/AskFollowUp";
import { ViewToggle } from "@/components/ViewToggle";

export default function ReportPage() {
  const { taskId } = useParams<{ taskId: string }>();
  const [phase, setPhase] = useState<string>("bull");
  const [agentOutputs, setAgentOutputs] = useState<Record<string, string>>({});
  const [citations, setCitations] = useState<Record<string, Citation>>({});
  const [report, setReport] = useState<ResearchReport | null>(null);
  const [error, setError] = useState("");
  const [activeTab, setActiveTab] = useState<"sources" | "timeline">("sources");
  const [selectedRef, setSelectedRef] = useState<string | null>(null);
  const [viewMode, setViewMode] = useState<"balanced" | "bull" | "bear">("balanced");
  const [followUpAnswer, setFollowUpAnswer] = useState("");

  useEffect(() => {
    const close = createSSEConnection(api.streamUrl(taskId), (event: SSEEvent) => {
      switch (event.type) {
        case "phase":
          setPhase(event.phase);
          break;
        case "agent_progress":
          setAgentOutputs((prev) => ({
            ...prev,
            [event.agent]: (prev[event.agent] || "") + event.chunk,
          }));
          break;
        case "citation":
          setCitations((prev) => ({ ...prev, [event.ref_id]: event.source }));
          break;
        case "warning":
          // Warnings are embedded in the factcheck output
          break;
        case "error":
          setError(event.message);
          break;
        case "complete":
          setPhase("done");
          loadReport();
          break;
      }
    });
    return close;
  }, [taskId]);

  const loadReport = async () => {
    try {
      const r = await api.getReport(taskId);
      setReport(r);
    } catch (err: any) {
      setError(err.message);
    }
  };

  const handleCitationClick = (refId: string) => {
    setSelectedRef(refId);
    setActiveTab("sources");
  };

  const handleFollowUp = async (question: string) => {
    try {
      const { answer } = await api.askFollowUp(taskId, question);
      setFollowUpAnswer(answer);
    } catch (err: any) {
      setError(err.message);
    }
  };

  const handleViewChange = (mode: "balanced" | "bull" | "bear") => {
    setViewMode(mode);
  };

  if (error && !report) {
    return (
      <div className="max-w-4xl mx-auto px-6 py-20 text-center">
        <p className="text-red-500">{error}</p>
      </div>
    );
  }

  const displayContent = (() => {
    if (!report) return "";
    switch (viewMode) {
      case "bull": return report.bull_view || "Bull分析生成中...";
      case "bear": return report.bear_view || "Bear分析生成中...";
      default: return report.markdown;
    }
  })();

  return (
    <div className="max-w-7xl mx-auto px-6 py-8">
      <div className="mb-6">
        <h1 className="text-2xl font-bold">研究报告：{report?.query || "..."}</h1>
      </div>

      {phase !== "done" && (
        <ProgressPanel phase={phase} agentOutputs={agentOutputs} />
      )}

      <div className="flex gap-6">
        <div className="flex-1 min-w-0">
          <ReportContent
            markdown={displayContent}
            citations={citations}
            onCitationClick={handleCitationClick}
          />
          {followUpAnswer && (
            <div className="mt-6 p-4 bg-blue-50 rounded-xl border border-blue-100">
              <h3 className="font-semibold mb-2">💬 追问回复</h3>
              <div className="text-sm whitespace-pre-wrap">{followUpAnswer}</div>
            </div>
          )}
          <div className="mt-6">
            <AskFollowUp onSubmit={handleFollowUp} loading={false} />
          </div>
        </div>

        <SidePanel
          activeTab={activeTab}
          onTabChange={setActiveTab}
          citations={citations}
          selectedRef={selectedRef}
          taskId={taskId}
        />
      </div>

      <div className="fixed bottom-6 right-6">
        <ViewToggle active={viewMode} onChange={handleViewChange} />
      </div>
    </div>
  );
}
