---
title: Transformer
zh_title: Transformer 架构
ipa: /trænsˈfɔːmə/
created: 2026-07-12
updated: 2026-07-12
type: concept
tags: [transformer, attention, language-model, neural-network]
sources: [attention-is-all-you-need-2017, karpathy-nn-zero-to-hero]
confidence: high
---

# Transformer

**Transformer 架构** · Transformer · /trænsˈfɔːmə/

现代 LLM（GPT、Claude 等）的底层神经网络架构。由 Google 在 2017 年论文《Attention is All You Need》中提出。核心创新：用 **Self-Attention** 机制取代 RNN 的序列处理，实现并行训练。

## 核心组件

1. **Self-Attention** /sɛlf əˈtɛnʃən/ — 每个 token 关注序列中所有其他 token
2. **Multi-Head Attention** — 多组并行的注意力，捕捉不同维度的关系
3. **Positional Encoding** — 注入位置信息（Transformer 本身不感知顺序）
4. **Feed-Forward Networks** — 每个位置的非线性变换
5. **Layer Normalization** — 稳定训练的归一化层

## 为什么这对 AI Agent 工程师重要

不需要手写 Transformer，但需要理解：
- **上下文窗口**（Context Window）的本质是 Self-Attention 的计算范围
- **Token 预算**的根源是 Attention 的 O(n²) 复杂度
- 为什么 prompt 长度影响延迟和成本
- GPT 生成文本的原理（autoregressive /ˌɔːtəʊrɪˈɡrɛsɪv/）

## 入门资源

- Karpathy nn-zero-to-hero Lecture 7：从零构建 GPT（计划 Phase 2 后学）
- 原论文（可选）："Attention is All You Need" (Vaswani et al., 2017)
- 可视化工具：The Illustrated Transformer (Jay Alammar)

## 相关概念

- [[attention]] — Transformer 的核心机制
- [[tokenizer]] — 文本到 token 的转换，Transformer 的输入预处理
- [[gpt]] — 基于 Transformer 的具体实现
- [[software-2.0]] — Transformer 是 Software 2.0 的代表架构
- [[andrej-karpathy]] — nn-zero-to-hero Lecture 7 从头构建 GPT

## 来源

- Vaswani et al., "Attention is All You Need" (2017)
- Karpathy, "Let's build GPT: from scratch, in code, spelled out" (nn-zero-to-hero Lecture 7)
