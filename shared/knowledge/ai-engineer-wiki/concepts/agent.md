---
title: Agent
zh_title: 智能体
ipa: /ˈeɪdʒənt/
created: 2026-07-12
updated: 2026-07-12
type: concept
tags: [agent, tool-use, orchestration]
sources: [anthropic-building-effective-agents-2024, lilian-weng-agent-2023]
confidence: high
---

# Agent

**智能体** · Agent · /ˈeɪdʒənt/

最简洁的定义（Anthropic）：**Agent = Model + Tools in a Loop**。LLM 动态指导自己的流程和工具使用，而非按预定义代码路径执行。

## Agent vs Workflow

| | Workflow | Agent |
|---|---------|-------|
| 控制流 | 预定义代码路径 | LLM 动态决策 |
| 适用场景 | 流程明确的任务 | 开放式的、需要灵活决策的任务 |
| 实现复杂度 | 低 | 高 |

## Anthropic 五种 Agent 模式

1. **Prompt Chaining** — 顺序执行，每步有 gate 检查
2. **Routing** — 分类输入，导向专门处理
3. **Parallelization** — 同时执行，合并结果
4. **Orchestrator-Workers** — 中央 LLM 动态委派任务
5. **Evaluator-Optimizer** — 一个 LLM 生成，另一个评估反馈

## Agent 系统三组件（Lilian Weng）

1. **Planning** /ˈplænɪŋ/ — 任务分解（CoT, Tree-of-Thoughts）+ 自我反思（ReAct, Reflexion）
2. **Memory** /ˈmɛməri/ — 短期（上下文）+ 长期（向量存储）
3. **Tool Use** /tuːl juːz/ — 外部 API 调用、代码执行

## 为什么这对 AI Agent 工程师重要

速派的核心架构就是 Agent——匹配引擎 + 协作功能。设计原则：从简单开始（Anthropic 警告：不要过度工程化 Agent）。先用单次 LLM 调用，不够再加 workflow，再不够才上全 Agent。

## 相关概念

- [[ai-engineer]] — Agent 是 AI Engineer 的主要构建对象
- [[tool-use]] — Agent 的三大组件之一
- [[multi-agent]] — 多 Agent 协作系统
- [[evals]] — Agent 行为质量评估
- [[anthropic]] — 《Building Effective Agents》的作者

## 来源

- Anthropic, "Building Effective Agents" (2024.12), https://www.anthropic.com/engineering/building-effective-agents
- Lilian Weng, "LLM Powered Autonomous Agents" (2023.6), https://lilianweng.github.io/posts/2023-06-23-agent/
