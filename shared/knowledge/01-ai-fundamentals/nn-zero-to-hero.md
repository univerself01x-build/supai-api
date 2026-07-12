---
title: nn-zero-to-hero 课程评估
date: 2026-07-12
tags: [neural-network, learning-path, course, karpathy]
parent: "[[01-ai-fundamentals]]"
status: reference
project: supai
phase: 1
---

# nn-zero-to-hero 课程评估

**神经网络从零到英雄** · Neural Networks: Zero to Hero · /ˈnjʊərəl ˈnɛtwɜːks frɒm ˈzɪərəʊ tuː ˈhɪərəʊ/

Andrej Karpathy（前 Tesla AI 总监 / OpenAI 联合创始人）的 8 讲免费课程。23.5k GitHub star。从手写 autograd 引擎到完整 GPT 模型。

## 课程结构

| # | 内容 | Agent 开发相关度 |
|---|------|:---:|
| 1 | 手写**反向传播** /ˌbækprɒpəˈɡeɪʃən/ 引擎（micrograd） | 低 |
| 2 | 字符级语言模型，torch.Tensor 入门 | 中 |
| 3 | MLP + ML 基础（train/dev/test、过拟合） | 中 |
| 4 | 激活值/梯度统计、BatchNorm 原理 | 低 |
| 5 | 手算反向传播（Backprop Ninja） | 低 |
| 6 | WaveNet 架构（CNN 变体） | 低 |
| **7** | **从零构建 GPT**（Attention is All You Need） | **高** |
| **8** | **GPT Tokenizer** /ˈtəʊkənaɪzə/（BPE from scratch） | **高** |

## 学习决策（2026-07-12）

**当前不学。** 理由：

1. 速派 MVP 是第一优先级，用现成 LLM API，不需要训练模型
2. 学习方法论是实战驱动，Phase 完成 → 复盘，不是先学完理论
3. 40-60 小时投入，当前 ROI 不高
4. Lecture 1-6 对 Agent 应用层开发无直接帮助

**后续计划：**
- Lecture 7 + 8 列入学习队列，速派 Phase 2 结束后安排（约 8-10 小时）
- Lecture 1-6 暂不列入——除非转向模型训练方向

## 意义

不是教你用 LLM，是教你理解 LLM 怎么造出来的。Karpathy 风格是"spelled-out"——逐行解释代码，工程师给工程师讲。

对 Agent 开发的价值：
- Tokenizer 原理（Lecture 8）直接解释 prompt 截断、特殊字符等常见问题
- Transformer 注意力机制 /əˈtɛnʃən ˈmɛkənɪzəm/（Lecture 7）帮助精准设计 prompt 结构
- AI 从业者的内功——就像开车不需要懂发动机，但 F1 车手一定懂

## 参考

- 仓库：https://github.com/karpathy/nn-zero-to-hero
- Karpathy's LLM Wiki pattern：[[llm-wiki]]
