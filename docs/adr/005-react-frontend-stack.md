# ADR 005: React 19 + TypeScript + AI SDK v6 前端技术栈

- **状态**: accepted
- **日期**: 2026-07-08
- **上下文**: 前端技术选型。AGENTS.md 原规定单文件 HTML + Vanilla JS。但产品需要 AI Native 交互（流式反馈、对话流、语音输入）
- **决策**: React 19 + TypeScript + Vercel AI SDK v6 + shadcn/ui + Tailwind CSS 4。AGENTS.md 约束针对 Core Engine（薄壳厚核），壳层可以用主流工具
- **替代方案**: 
  - 单文件 HTML/Vanilla JS（AGENTS.md 原规定。复杂交互时手工造轮子）
  - Alpine.js/Htmx（轻量但到复杂交互撞墙）
- **后果**: 
  - ✅ 2026 硅谷前端标准栈，流式/工具调用/类型安全开箱即用
  - ✅ shadcn/ui 暗色主题开箱匹配设计方向
  - ⚠️ 引入 Node.js 构建链，破坏"零依赖"原则（但该原则针对 Core Engine）
