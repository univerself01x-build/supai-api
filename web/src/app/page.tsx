"use client";

import { useState, useRef, useEffect } from "react";
import { matchRequest } from "@/lib/api";
import { ComposableInput } from "@/components/composable-input";

interface Message {
  type: "user" | "system" | "error";
  text: string;
  id: string;
  time: string;
}

const SUGGESTIONS = ["AI产品发布会 上海", "技术沙龙 北京", "Demo Day 深圳", "Hackathon 杭州"];

function loadMessages(): Message[] {
  if (typeof window === "undefined") return [];
  try {
    const raw = localStorage.getItem("supai-messages");
    return raw ? JSON.parse(raw) : [];
  } catch { return []; }
}

function saveMessages(msgs: Message[]) {
  try { localStorage.setItem("supai-messages", JSON.stringify(msgs.slice(-50))); } catch {}
}

export default function Home() {
  const [barStatus, setBarStatus] = useState<"idle" | "matching" | "done" | "error">("idle");
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState<Message[]>(loadMessages);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const match = async (scene: string) => {
    if (!scene.trim()) return;
    const now = new Date().toLocaleTimeString("zh-CN", { hour: "2-digit", minute: "2-digit" });
    const userMsg: Message = { type: "user", text: scene, id: "u_" + Date.now(), time: now };
    const start = [...messages, userMsg];
    setMessages(start); saveMessages(start); setInput("");
    setBarStatus("matching");
    try {
      const result = await matchRequest({ scene, budget: 5000, location: "上海", roles: ["photographer"] });
      setBarStatus("done");
      const sysMsg: Message = { type: "system", text: result.summary, id: result.projectId,
        time: new Date().toLocaleTimeString("zh-CN", { hour: "2-digit", minute: "2-digit" }) };
      const final = [...start, sysMsg];
      setMessages(final); saveMessages(final);
      setTimeout(() => setBarStatus("idle"), 800);
    } catch {
      setBarStatus("error");
      const errMsg: Message = { type: "error", text: "匹配失败，请重试", id: "e_" + Date.now(),
        time: new Date().toLocaleTimeString("zh-CN", { hour: "2-digit", minute: "2-digit" }) };
      const final = [...start, errMsg];
      setMessages(final); saveMessages(final);
      setTimeout(() => setBarStatus("idle"), 2000);
    }
  };

  const clearHistory = () => { setMessages([]); localStorage.removeItem("supai-messages"); };

  return (
    <div className="flex flex-col h-screen max-w-2xl lg:max-w-4xl mx-auto">
      {/* Header — terminal style, minimal */}
      <div className="px-4 pt-3 pb-2 flex items-center justify-between">
        <h1 className="text-[15px] font-bold tracking-[-0.01em] bg-gradient-to-r from-[#F5C542] via-[#E8A820] to-[#F5C542] bg-[length:200%_100%] bg-clip-text text-transparent animate-[shimmer_3s_ease-in-out_infinite]">SUPAI</h1>
        {messages.length > 0 && (
          <button onClick={clearHistory} className="text-[10px] text-muted-foreground/20 hover:text-muted-foreground/50 transition-colors">清空</button>
        )}
      </div>

      {/* Conversation */}
      <div className="flex-1 overflow-y-auto">
        {messages.length === 0 ? (
          /* Empty state */
          <div className="flex flex-col items-center justify-center pt-16 pb-8 text-center px-4">
            <div className="text-2xl mb-3 opacity-30">☼</div>
            <p className="text-[17px] font-semibold text-foreground mb-1 tracking-[0.01em]">描述需求，AI 组队</p>
            <p className="text-xs text-muted-foreground/40 mb-8">一句话，一支视觉 Team</p>
            <div className="flex flex-wrap gap-2 justify-center max-w-sm">
              {SUGGESTIONS.map((s) => (
                <button
                  key={s}
                  onClick={() => { setInput(s); match(s); }}
                  className="px-4 py-2.5 rounded-full border border-border/50 bg-[#111113] text-[13px] text-muted-foreground
                             hover:border-[#2383E2] hover:text-foreground transition-all active:bg-[#1A1A1D]"
                >
                  {s}
                </button>
              ))}
            </div>
          </div>
        ) : (
          /* Messages */
          <div>
            {messages.map((msg) => (
              <div key={msg.id} className="px-4 py-3 flex gap-3">
                <div className={`w-6 h-6 rounded-full flex items-center justify-center text-[10px] flex-shrink-0 mt-0.5
                  ${msg.type === "user"  ? "bg-[#2383E2]/15 text-[#70B8FF]" :
                    msg.type === "error" ? "bg-[#E5484D]/15 text-[#E5484D]" :
                    "bg-[#8B5CF6]/15 text-[#A78BFA]"}`}>
                  {msg.type === "user" ? "你" : msg.type === "error" ? "!" : "AI"}
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-0.5">
                    <span className="text-[11px] font-medium text-foreground/60">
                      {msg.type === "user" ? "你" : msg.type === "error" ? "系统" : "速派 AI"}
                    </span>
                    <span className="text-[10px] text-muted-foreground/20">{msg.time}</span>
                  </div>
                  <div className={`text-sm leading-relaxed ${msg.type === "error" ? "text-[#E5484D]/80" : "text-foreground/80"}`}>
                    {msg.text}
                  </div>
                </div>
              </div>
            ))}
            <div ref={bottomRef} />
          </div>
        )}
      </div>

      {/* Bottom bar */}
      <div className="px-4 pb-4 pt-2 border-t border-border/15">
        <p className="text-center text-[10px] text-muted-foreground/20 font-mono mb-1">20 位摄影师在线 · 上海 北京 深圳</p>
        <StatusBar status={barStatus} />
        <ComposableInput
          value={input}
          onChange={setInput}
          onSubmit={match}
          placeholder="描述你的需求…"
        />
      </div>
    </div>
  );
}

function StatusBar({ status }: { status: "idle" | "matching" | "done" | "error" }) {
  const base = "h-[2px] w-full transition-all duration-300";
  const map: Record<string, string> = {
    idle:    `${base} bg-transparent`,
    matching:`${base} bg-gradient-to-r from-[#6366F1] via-[#8B5CF6] to-[#6366F1] animate-pulse`,
    done:    `${base} bg-[#30A46C] animate-[flash-green_0.6s_ease-out_forwards]`,
    error:   `${base} bg-[#E5484D]`,
  };
  return <div className={map[status] || map.idle} />;
}
