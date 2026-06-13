"use client";

import { AgentCard } from "./AgentCard";

interface Props {
  phase: string;
  agentOutputs: Record<string, string>;
}

const AGENTS = [
  { key: "bull", label: "多方分析师", icon: "🐂" },
  { key: "bear", label: "空方分析师", icon: "🐻" },
  { key: "factcheck", label: "事实核查员", icon: "🔍" },
  { key: "synthesizer", label: "综合编辑", icon: "📝" },
];

export function ProgressPanel({ phase, agentOutputs }: Props) {
  const getStatus = (agentKey: string) => {
    if (agentOutputs[agentKey] && phase === "done") return "done";
    if (phase === agentKey) return "running";
    const order = ["bull", "bear", "factcheck", "synthesizer"];
    const phaseIdx = order.indexOf(phase);
    const agentIdx = order.indexOf(agentKey);
    if (agentIdx < phaseIdx) return "done";
    if (agentIdx === phaseIdx) return "running";
    return "idle";
  };

  return (
    <div className="grid grid-cols-2 gap-3 mb-6">
      {AGENTS.map((a) => (
        <AgentCard
          key={a.key}
          agent={a.key}
          label={a.label}
          icon={a.icon}
          status={getStatus(a.key)}
          output={agentOutputs[a.key] || ""}
        />
      ))}
    </div>
  );
}
