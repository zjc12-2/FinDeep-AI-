"use client";

import { useEffect, useState } from "react";
import { TimelineEvent } from "@/lib/types";
import { api } from "@/lib/api";
import { Calendar, ChevronRight } from "lucide-react";

interface Props {
  taskId: string;
}

export function EventTimeline({ taskId }: Props) {
  const [events, setEvents] = useState<TimelineEvent[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.getTimeline(taskId).then((data) => {
      setEvents(data.events || []);
      setLoading(false);
    }).catch(() => setLoading(false));
  }, [taskId]);

  if (loading) {
    return <p className="text-sm text-muted-foreground text-center py-8">加载时间轴中...</p>;
  }

  if (events.length === 0) {
    return <p className="text-sm text-muted-foreground text-center py-8">暂无事件链数据</p>;
  }

  const typeColors: Record<string, string> = {
    financial: "bg-blue-100 text-blue-700",
    management: "bg-purple-100 text-purple-700",
    market: "bg-green-100 text-green-700",
    other: "bg-gray-100 text-gray-700",
  };

  return (
    <div className="relative pl-6 border-l-2 border-border space-y-6">
      {events.map((event, i) => (
        <div key={i} className="relative">
          <div className="absolute -left-[25px] top-1 w-3 h-3 rounded-full bg-primary border-2 border-white" />
          <div className="flex items-center gap-2 mb-1">
            <Calendar className="w-3 h-3 text-muted-foreground" />
            <span className="text-xs font-medium text-muted-foreground">{event.date}</span>
            <span className={`text-xs px-1.5 py-0.5 rounded ${typeColors[event.type] || typeColors.other}`}>
              {event.type}
            </span>
          </div>
          <p className="text-sm font-medium">{event.event}</p>
          {event.causes.length > 0 && (
            <p className="text-xs text-muted-foreground mt-1">
              原因: {event.causes.join(", ")}
            </p>
          )}
          {event.effects.length > 0 && (
            <div className="flex items-start gap-1 mt-1">
              <ChevronRight className="w-3 h-3 text-muted-foreground mt-0.5" />
              <p className="text-xs text-muted-foreground">
                导致: {event.effects.join(", ")}
              </p>
            </div>
          )}
          {event.source_ref && (
            <span className="text-xs font-mono text-primary mt-1 inline-block">
              [{event.source_ref}]
            </span>
          )}
        </div>
      ))}
    </div>
  );
}
