"use client";

import { useState, useRef, useEffect, useCallback } from "react";
import { Input } from "@/components/ui/input";

interface SpeechRecognitionEvent extends Event {
  results: SpeechRecognitionResultList;
  resultIndex: number;
}

interface SpeechRecognitionErrorEvent extends Event {
  error: string;
  message: string;
}

interface SpeechRecognition extends EventTarget {
  continuous: boolean;
  interimResults: boolean;
  lang: string;
  onresult: ((event: SpeechRecognitionEvent) => void) | null;
  onerror: ((event: SpeechRecognitionErrorEvent) => void) | null;
  onend: (() => void) | null;
  start(): void;
  stop(): void;
  abort(): void;
}

declare global {
  interface Window {
    SpeechRecognition?: new () => SpeechRecognition;
    webkitSpeechRecognition?: new () => SpeechRecognition;
  }
}

interface Props {
  value: string;
  onChange: (text: string) => void;
  onSubmit: (text: string) => void;
  placeholder?: string;
}

export function ComposableInput({ value, onChange, onSubmit, placeholder }: Props) {
  const [listening, setListening] = useState(false);
  const recognitionRef = useRef<SpeechRecognition | null>(null);

  const [supported] = useState(() =>
    typeof window !== "undefined" && !!(window.SpeechRecognition || window.webkitSpeechRecognition)
  );

  const getRecognition = useCallback(() => {
    if (recognitionRef.current) return recognitionRef.current;
    const Ctor = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!Ctor) return null;
    const r = new Ctor();
    r.continuous = false;
    r.interimResults = false;
    r.lang = "zh-CN";
    r.onresult = (event: SpeechRecognitionEvent) => {
      const transcript = event.results[0][0].transcript;
      onChange(transcript);
      setTimeout(() => onSubmit(transcript), 300);
    };
    r.onerror = () => setListening(false);
    r.onend = () => setListening(false);
    recognitionRef.current = r;
    return r;
  }, [onChange, onSubmit]);

  const toggleVoice = () => {
    const r = getRecognition();
    if (!r) return;
    if (listening) {
      r.stop();
      setListening(false);
    } else {
      try {
        r.start();
        setListening(true);
      } catch {
        setListening(false);
      }
    }
  };

  return (
    <div className="relative">
      <Input
        value={value}
        onChange={(e) => onChange(e.target.value)}
        onKeyDown={(e) => { if (e.key === "Enter") onSubmit(value); }}
        placeholder={listening ? "正在聆听…" : (placeholder || "描述你的需求…")}
        className="h-12 rounded-xl bg-[#111113] border-border/50 text-[15px] placeholder:text-muted-foreground/40
                   focus-visible:ring-1 focus-visible:ring-[#2383E2] pr-10"
      />
      {supported && (
        <button
          onClick={toggleVoice}
          className={`absolute right-2 top-1/2 -translate-y-1/2 w-8 h-8 rounded-lg flex items-center justify-center transition-all
            ${listening
              ? "bg-[#E5484D]/15 text-[#E5484D] animate-pulse"
              : "text-muted-foreground/40 hover:text-[#2383E2] hover:bg-[#2383E2]/10"}`}
          aria-label={listening ? "停止" : "语音输入"}
        >
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3Z"/>
            <path d="M19 10v2a7 7 0 0 1-14 0v-2"/>
            <line x1="12" x2="12" y1="19" y2="22"/>
          </svg>
        </button>
      )}
    </div>
  );
}
