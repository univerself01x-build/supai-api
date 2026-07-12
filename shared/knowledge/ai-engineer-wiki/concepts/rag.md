---
title: RAG
zh_title: 检索增强生成
ipa: /ræɡ/ (acronym: /ɑːr eɪ dʒiː/)
created: 2026-07-12
updated: 2026-07-12
type: concept
tags: [rag, language-model, context-engineering]
sources: [chip-huyen-genai-platform-2024, eugene-yan-llm-patterns-2024]
confidence: high
---

# RAG

**检索增强生成** · Retrieval-Augmented Generation · /rɪˈtriːvəl ɔːɡˈmɛntɪd ˌdʒɛnəˈreɪʃən/

为 LLM 注入外部知识的技术模式。在生成回答前，先从知识库检索相关文档，将其注入上下文窗口，让模型基于检索到的信息生成回答。

## RAG 的类型

| 类型 | 方法 | 适用场景 |
|------|------|---------|
| 术语检索 | BM25 / TF-IDF 关键词匹配 | 精确术语查询 |
| 向量检索 | Embedding + 向量相似度搜索 | 语义相似查询 |
| 混合搜索 | 术语 + 向量组合 | 生产环境推荐方案 |

## 为什么这对 AI Agent 工程师重要

速派的匹配引擎本质上是一个 RAG 变体——检索匹配的公民/技能，注入 Agent 上下文，生成推荐。理解 RAG 的三种检索方式和混合搜索策略，直接关系到匹配质量。

## 相关概念

- [[context-engineering]] — RAG 注入是上下文栈的一层
- [[agent]] — Agentic RAG：Agent 自主决策检索策略
- [[evals]] — RAG 质量评估（检索精度 + 生成质量）
- [[embedding]] — 向量检索的数学基础
- [[fine-tuning]] — RAG vs Fine-tuning 是 AI Engineer 的基础决策

## 来源

- Chip Huyen, "Building A Generative AI Platform" (2024.7), https://huyenchip.com/2024/07/25/genai-platform.html
- Eugene Yan, "Patterns for Building LLM-based Systems" (2024), https://eugeneyan.com/writing/llm-patterns/
