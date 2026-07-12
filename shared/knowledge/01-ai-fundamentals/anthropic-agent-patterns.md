---
title: Anthropic 五种 Agent 设计模式
date: 2026-07-12
tags: [agent, architecture, anthropic, design-pattern]
parent: "[[01-ai-fundamentals]]"
status: learning
project: supai
phase: 2
---

# Anthropic 五种 Agent 设计模式

**Anthropic Agent 设计模式** · Anthropic Agent Patterns · /ænˈθrɑːpɪk ˈeɪdʒənt ˈpætərnz/

Anthropic 在 2024 年 12 月发布的 Agent 设计指南。核心原则：**从简单开始，只在必要时增加复杂度。**

## 五种模式

### 1. Prompt Chaining /prɑːmpt ˈtʃeɪnɪŋ/ — 提示链

顺序执行，每步有 gate 检查。适用于：任务可分解为固定子步骤。

```
输入 → [Step 1] → gate → [Step 2] → gate → [Step 3] → 输出
```

### 2. Routing /ˈruːtɪŋ/ — 路由

分类输入，导向专门处理。适用于：不同类别输入需要不同处理方式。

```
          ┌→ [Handler A]
输入 → [Router] → [Handler B]
          └→ [Handler C]
```

### 3. Parallelization /ˌpærəˌlɛlaɪˈzeɪʃən/ — 并行化

同时执行，合并结果。适用于：多视角分析或独立子任务。

```
          ┌→ [Worker A] ─┐
输入 → [Split] → [Worker B] → [Merge] → 输出
          └→ [Worker C] ─┘
```

### 4. Orchestrator-Workers /ˈɔːrkɪstreɪtər ˈwɜːrkərz/ — 编排-工作者

中央 LLM 动态委派任务给专门 worker。适用于：复杂任务无法预知所有子步骤。

```
[Orchestrator] ⇄ [Worker A]
       ⇄ [Worker B]
       ⇄ [Worker C]
```

### 5. Evaluator-Optimizer /ɪˈvæljueɪtər ˈɑːptɪmaɪzər/ — 评估-优化

一个 LLM 生成，另一个 LLM 评估并反馈，循环迭代。适用于：需要高质量输出的场景。

```
[Generator] → 输出 → [Evaluator] → 反馈 → [Generator] → 改进输出
```

## 对速派的指导

核心原则"简单优先"直接对应峰哥的 Engine-Not-First 和 Agent-Not-First：

> 先用单次 LLM 调用。不够再加 workflow（Prompt Chaining / Routing）。再不够才上全 Agent（Orchestrator-Workers）。

速派 Phase 1：单次 LLM 调用（匹配推荐）。Phase 2 协作功能：考虑从 Routing 模式开始，不直接跳到 Multi-Agent。

## 参考

- Anthropic: Building Effective Agents (2024.12) — https://www.anthropic.com/engineering/building-effective-agents
- 能力图谱节点: [[cap-anthropic-agent-patterns]]
