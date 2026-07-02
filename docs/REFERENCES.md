# 外部范式参考

## 仓库研究

### gstack (Garry Tan / YC)
- **来源**: github.com/garrytan/gstack
- **核心**: 23 个 AI 专家的 Sprint 流水线
- **应用**: Boil the Ocean · 双模型审查 · SKILL.md 模板
- **详见**: `/Users/lifeng/gstack-research-summary.md`

### superpowers (Obra)
- **来源**: github.com/obra/superpowers
- **核心**: 子代理驱动开发 (SDD) · 耐久账本 · Red Flags
- **应用**: engine.py review_match() · 硬性门槛
- **详见**: 会话记录 (2026-06-30 研究结果)

### mattpocock/skills
- **来源**: github.com/mattpocock/skills
- **核心**: 薄壳厚核 · User/Model Invoked · 渐进披露
- **应用**: 架构层分离 · card_*() 输出函数
- **详见**: 会话记录 (2026-06-30 研究结果)

---

## 平台指南

### OpenAI
- **来源**: platform.openai.com/docs/guides
- **核心模式**:
  - Start Simple — 单 Agent 跑通再考虑多 Agent
  - Tools First — 函数调用了是 Agent 的手
  - Structured Outputs — JSON mode，不解析文本
  - Streaming — 不等全部生成，边生成边显示
  - Eval Framework — 测量 > 猜测
  - Prompt: 具体 + 约束 + 示例
- **应用**: engine.py 直接调 API · 流式输出 (待加) · Harness 评估
- **状态**: ✅ 已提炼 (2026-07-02)

### Anthropic / Claude Code
- **来源**: docs.anthropic.com · code.claude.com/docs
- **核心模式**:
  - CLAUDE.md — 项目记忆文件，自动注入上下文
  - `/plan` — 先设计再执行，不直接写代码
  - `/review` + `/security-review` — 代码审查 + 安全审查
  - Custom Agents — 专用子代理（如 @security-reviewer）
  - Hooks (8种) — 事件驱动的自动化
  - Print Mode (`-p`) — CI/CD 非交互模式
  - Context Health — `/context` 监控，>70% 主动 compact
- **应用**: AGENTS.md · Harness 审查 · 子代理匹配审查
- **状态**: ✅ 已提炼 (2026-07-02)

### Vercel AI SDK
- **来源**: vercel.com/kb/guide/ai-gateway-and-ai-sdk
- **核心**: AI Gateway · AI SDK · 流式 · Sandbox · Workflow
- **应用**: 模型降级方案 · SSE 流式 · Gateway 模式
- **已提炼**: 2026-07-02

---

## 课程

### 源点AI · The AI-Native Builder
- **来源**: haaboo.com
- **核心**: 六层能力地图 · 六级能力阶梯 · 从 Coding 到 Orchestrating
- **应用**: AI 原生交互原则 · 能力分层思维
- **详见**: 会话记录 (2026-06-30 课程提炼)

---

## 更新规则
新研究 → 更新本文件 → 提炼到 PLAYBOOK/METHODOLOGY
