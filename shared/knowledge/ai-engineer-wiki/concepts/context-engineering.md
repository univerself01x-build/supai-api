---
title: Context Engineering
zh_title: 上下文工程
ipa: /ˈkɒntɛkst ˌɛndʒɪˈnɪərɪŋ/
created: 2026-07-12
updated: 2026-07-12
type: concept
tags: [context-engineering, prompt-engineering, agent]
sources: [stanford-cs224g-2026]
confidence: medium
---

# Context Engineering

**上下文工程** · Context Engineering · /ˈkɒntɛkst ˌɛndʒɪˈnɪərɪŋ/

系统性管理模型接收的全部上下文——取代零散的 Prompt Engineering。由 Stanford CS 224G（2026 Winter）提出。

## 完整上下文栈

Context Engineering 管理的不仅是 prompt 文本，而是：

1. **System Prompt** — 角色定义、行为约束
2. **Conversation History** — 对话历史
3. **Tool Definitions** — 可用工具的 JSON Schema
4. **Parameters** — temperature、max_tokens 等
5. **RAG Injections** — 检索到的外部知识
6. **Token Budget Economy** — 上下文窗口成本管理

## Context Engineering vs Prompt Engineering

| | Prompt Engineering | Context Engineering |
|---|-------------------|---------------------|
| 范围 | 单条 prompt 文案优化 | 全部上下文栈的系统管理 |
| 思维 | 手工艺 | 系统工程 |
| 关注点 | 措辞 | Token 预算、信息密度、优先级排序 |

## 为什么这对 AI Agent 工程师重要

当 Agent 需要同时管理 system prompt + 工具定义 + 检索结果 + 对话历史时，单靠"写好 prompt"不够。Token 预算是真实成本——每次 LLM 调用都在烧钱。Context Engineering 是 AI Engineer 区别于"会写 prompt 的人"的核心能力。

## 相关概念

- [[agent]] — Context Engineering 的主要应用场景
- [[prompt-engineering]] — 被 Context Engineering 取代的旧范式
- [[rag]] — RAG 注入是上下文栈的一层
- [[stanford-cs224g]] — 来源课程

## 来源

- Stanford CS 224G W3: Context Engineering & RAG (2026 Winter), https://web.stanford.edu/class/cs224g/
