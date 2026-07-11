"use client";

import type { ProjectCard } from "@/lib/api";
import { Badge } from "@/components/ui/badge";

const statusDot: Record<string, string> = {
  matching: "○",
  confirmed: "◉",
  in_progress: "●",
  delivered: "◉",
  distributed: "◎",
};

const statusDotColor: Record<string, string> = {
  matching: "text-amber-400/70",
  confirmed: "text-blue-400",
  in_progress: "text-emerald-400",
  delivered: "text-emerald-400/70",
  distributed: "text-violet-400",
};

const tierLabel: Record<string, string> = {
  enterprise: "首发定制",
  premier: "资深",
  express: "专业",
  pool: "速拍",
};

export function ProjectRow({
  project,
  onOpen,
}: {
  project: ProjectCard;
  onOpen: (id: string) => void;
}) {
  const dot = statusDot[project.status] || "○";
  const dotColor = statusDotColor[project.status] || "text-muted-foreground/40";
  const tier = (project as any).tier || "pool";
  const budget = (project as any).budget || 0;
  const location = (project as any).location || "";
  const teamSummary = project.team
    .map((t) => t.assignee)
    .filter(Boolean)
    .join(" · ") || "待匹配";

  const time = project.createdAt
    ? new Date(project.createdAt).toLocaleDateString("zh-CN")
    : "";

  return (
    <div
      role="button"
      tabIndex={0}
      onClick={() => onOpen(project.id)}
      onKeyDown={(e) => e.key === 'Enter' && onOpen(project.id)}
      className="w-full text-left group flex items-center gap-3 px-4 py-3
                 border-b border-border/50 hover:bg-[#111113] transition-colors duration-150 cursor-pointer"
    >
      <span className={`text-xs ${dotColor} w-4 flex-shrink-0`}>{dot}</span>

      <div className="flex-1 min-w-0 flex items-center gap-3">
        <span className="text-sm font-medium text-foreground truncate">
          {project.title}
        </span>
        <Badge variant="secondary" className="text-[10px] px-1.5 py-0 flex-shrink-0">
          {tierLabel[tier] || tier}
        </Badge>
      </div>

      <div className="hidden sm:flex items-center gap-3 text-xs text-muted-foreground flex-shrink-0">
        <span>{location}</span>
        <span className="font-mono">¥{budget.toLocaleString()}</span>
        <span className="truncate max-w-[120px]">{teamSummary}</span>
        <span className="text-[10px] text-muted-foreground/50">{time}</span>
      </div>

      <span className="text-[10px] font-mono text-muted-foreground/50 flex-shrink-0 opacity-0 group-hover:opacity-100 transition-opacity">
        ▸
      </span>
      <button
        onClick={(e) => {
          e.stopPropagation();
          const card = [
            `📸 速派新单`,
            ``,
            `${project.title} | ${tierLabel[tier] || tier}档`,
            `📍 ${location} · 💰 ¥${budget.toLocaleString()}`,
            `摄影师：${teamSummary}`,
            ``,
            `👉 确认接单：${typeof window !== 'undefined' ? window.location.origin : ''}/confirm.html?id=${project.id}`,
          ].join('\n');
          navigator.clipboard.writeText(card);
          const btn = e.currentTarget as HTMLElement;
          btn.textContent = '✓';
          setTimeout(() => { btn.textContent = '复制'; }, 1500);
        }}
        className="text-[10px] text-muted-foreground/50 hover:text-[#2383E2]
                   flex-shrink-0 opacity-0 group-hover:opacity-100 transition-all ml-1"
      >
        复制
      </button>
    </div>
  );
}
