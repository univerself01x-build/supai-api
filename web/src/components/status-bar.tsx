"use client";

type StatusType = "idle" | "matching" | "done" | "review" | "error";

const statusClass: Record<StatusType, string> = {
  idle: "status-bar-idle",
  matching: "status-bar-matching",
  done: "status-bar-done",
  review: "status-bar-review",
  error: "status-bar-error",
};

const statusLabel: Record<StatusType, string> = {
  idle: "",
  matching: "matching…",
  done: "done",
  review: "review needed",
  error: "error",
};

export function StatusBar({ status }: { status: StatusType }) {
  return (
    <div className="relative">
      <div className={`w-full ${statusClass[status]}`} />
      {status !== "idle" && (
        <span className="absolute right-0 -top-[1px] text-[10px] font-mono text-muted-foreground/60 pr-2 leading-none">
          {statusLabel[status]}
        </span>
      )}
    </div>
  );
}
