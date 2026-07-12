---
title: Evals
zh_title: 评估体系
ipa: /ɪˈvælz/ (short for evaluations: /ɪˌvæljuˈeɪʃənz/)
created: 2026-07-12
updated: 2026-07-12
type: concept
tags: [evaluation, methodology, agent]
sources: [chip-huyen-ai-engineering-2025, eugene-yan-llm-patterns-2024, anthropic-building-effective-agents-2024]
confidence: high
---

# Evals

**评估体系** · Evals · /ɪˈvælz/

Evals-Driven Development（评估驱动开发）。AI 工程的核心实践：先建评估体系，再写功能代码。

## 为什么 Evals 是"盲飞"的分界线

> "没有 Evals 就是在盲飞。" — Eugene Yan

传统软件：测试测的是"对/错"（assert）。
AI 系统：输出是概率性的——需要评估"好不好"（质量）。

## Evals 的三个层次

| 层次 | 测什么 | 工具示例 |
|------|--------|---------|
| 单元级 | 单次 LLM 调用质量 | BLEU, ROUGE, BERTScore |
| 链路级 | RAG/Agent 端到端质量 | 人工标注 + 自动评分 |
| 生产级 | 线上真实用户反馈 | 隐式（点击/停留）+ 显式（👍👎） |

## 为什么这对 AI Agent 工程师重要

速派当前 harness.py 测的是 API 正确性，不是 Agent 行为质量。在加 Agent 协作功能之前，需要建立 eval pipeline：
- Agent 推荐匹配是否合理？
- Agent 拒绝不匹配请求是否准确？
- Context Engineering 调整后，输出质量变好还是变差？

这是 Chip Huyen 在《AI Engineering》中反复强调的核心瓶颈——"90% 的团队忽视评估体系"。

## 相关概念

- [[agent]] — Agent 行为质量评估是 Evals 的主要场景
- [[context-engineering]] — 每次上下文调整需要 Evals 验证
- [[chip-huyen]] — 评估体系的权威倡导者
- [[data-flywheel]] — 用户反馈 → Evals 数据 → 模型改进

## 来源

- Chip Huyen, "AI Engineering" ch.6 (O'Reilly, 2025)
- Eugene Yan, "Patterns for Building LLM-based Systems" — Evals section
- Anthropic, "Building Effective Agents" — 评估 Agent 性能的方法
