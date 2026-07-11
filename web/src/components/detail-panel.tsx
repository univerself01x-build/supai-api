"use client";

import { useEffect, useState } from "react";
import type { ProjectDetail } from "@/lib/api";
import { fetchProject } from "@/lib/api";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";

const roleIcon: Record<string, string> = {
  photographer: "📸",
  videographer: "🎥",
  editor: "✂️",
  designer: "🎨",
  live_stream: "📡",
};

const statusBadge: Record<string, { label: string; variant: "default" | "secondary" | "outline" }> = {
  matched: { label: "已匹配", variant: "secondary" },
  confirmed: { label: "已确认", variant: "default" },
  pending: { label: "待匹配", variant: "outline" },
  custom: { label: "客户自备", variant: "outline" },
};

export function DetailPanel({
  projectId,
  open,
  onClose,
}: {
  projectId: string | null;
  open: boolean;
  onClose: () => void;
}) {
  const [data, setData] = useState<ProjectDetail | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (projectId && open) {
      setLoading(true);
      fetchProject(projectId)
        .then(setData)
        .finally(() => setLoading(false));
    }
  }, [projectId, open]);

  if (!projectId) return null;

  return (
    <Dialog open={open} onOpenChange={(v) => !v && onClose()}>
      <DialogContent className="sm:max-w-lg bg-[#111113] border-border/50">
        <DialogHeader>
          <DialogTitle className="text-base font-medium">
            {data?.title || "加载中…"}
          </DialogTitle>
          {data && (
            <p className="text-xs text-muted-foreground mt-1">
              {data.tier} 档 · ¥{data.budget?.toLocaleString()} · {data.location}
            </p>
          )}
        </DialogHeader>

        {loading ? (
          <div className="space-y-3 py-4">
            {[1, 2, 3].map((i) => (
              <div key={i} className="h-12 rounded bg-[#1A1A1D] animate-pulse" />
            ))}
          </div>
        ) : data ? (
          <ScrollArea className="max-h-[60vh]">
            <div className="space-y-4 pr-2">
              {/* Team */}
              <div>
                <h4 className="text-xs font-medium text-muted-foreground mb-2">Team</h4>
                <div className="space-y-2">
                  {data.team.map((slot) => {
                    const badge = statusBadge[slot.status] || statusBadge.pending;
                    return (
                      <div
                        key={slot.role}
                        className="flex items-center justify-between py-2 px-3 rounded bg-[#1A1A1D]"
                      >
                        <div className="flex items-center gap-2">
                          <span>{roleIcon[slot.role] || "👤"}</span>
                          <span className="text-sm">{slot.role}</span>
                          {slot.photographer && (
                            <span className="text-sm text-foreground ml-1">
                              {slot.photographer.name}
                            </span>
                          )}
                        </div>
                        <div className="flex items-center gap-2">
                          {slot.photographer && (
                            <span className="text-[11px] font-mono text-muted-foreground">
                              ★{slot.photographer.avgRating} · {slot.photographer.completedTasks}单
                            </span>
                          )}
                          <Badge variant={badge.variant} className="text-[10px]">
                            {badge.label}
                          </Badge>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>

              {/* Timeline */}
              {data.timeline.length > 0 && (
                <div>
                  <h4 className="text-xs font-medium text-muted-foreground mb-2">时间线</h4>
                  <div className="space-y-1">
                    {data.timeline.map((entry, i) => (
                      <div key={i} className="flex gap-3 text-xs py-1">
                        <span className="font-mono text-muted-foreground/60 flex-shrink-0">
                          {new Date(entry.timestamp).toLocaleTimeString("zh-CN", {
                            hour: "2-digit",
                            minute: "2-digit",
                          })}
                        </span>
                        <span>{entry.event}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </ScrollArea>
        ) : null}
      </DialogContent>
    </Dialog>
  );
}
