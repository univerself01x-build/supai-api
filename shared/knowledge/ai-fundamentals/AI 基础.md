---
title: AI 基础
date: 2026-07-05
tags: [ai, fundamentals]
parent: "[[home]]"
---

# AI 基础 · AI Fundamentals /ˌfʌndəˈmentlz/

## Agent 演化（AIMA §2.4）

| 类型 | 英文 | IPA | 能力 |
|------|------|-----|------|
| 简单反射 | Simple Reflex | /ˈsɪmpl ˈriːflɛks/ | 规则匹配 |
| 基于模型 | Model-based | /ˈmɑːdl beɪst/ | 维护世界状态 |
| 基于目标 | Goal-based | /ɡoʊl beɪst/ | 搜索实现路径 |
| 基于效用 | Utility-based | /juːˈtɪləti beɪst/ | 权衡多个目标 |
| 学习型 | Learning | /ˈlɜːrnɪŋ/ | 从经验改进 |

> 关键认知（2026-07-04 AIMA辩论）：五层是累积演化，不是劳动分工。
> 每个 Agent 内部应自成闭环（§2.4.7 学习型模板），Agent 之间用消息协议协同。

## PEAS 框架

- **P**erformance /pərˈfɔːrməns/ — 绩效度量
- **E**nvironment /ɪnˈvaɪrənmənt/ — 环境
- **A**ctuators /ˈæktʃueɪtərz/ — 执行器
- **S**ensors /ˈsɛnsərz/ — 传感器

> 关键认知：PEAS 为单 Agent 设计。多 Agent 系统中各 Agent 互为 Environment，需额外建模。


## 价值对齐（AIMA §26）

- 工具性收敛目标 / Instrumental Convergence /ˌɪnstrəˈmɛntl kənˈvɜːrdʒəns/
- 可纠正性 / Corrigibility /ˌkɔːrɪdʒəˈbɪləti/

> 关键认知：AI Safety ≠ 分布式系统可靠性。四个安全规则来自数据库回滚、Erlang 哲学、
> Human-in-the-loop，不是原生的 AI Safety 概念。

## 合同网协议（AIMA §17.6）

- CFP / Call for Proposals /kɔːl fɔːr prəˈpoʊzlz/ — 公告
- 状态机: announced → bidding /ˈbɪdɪŋ/ → awarded /əˈwɔːrdɪd/ → executing → completed/failed

## 黑板架构 vs FIPA 消息路由

- **黑板** / Blackboard /ˈblækbɔːrd/: Agent 写数据不指定接收方（Hearsay-II）
- **FIPA ACL**: sender/receiver/communicative-act-type（inform/request/cfp/propose…）

> 关键认知：我们用的是 FIPA 风格消息路由，不是黑板。诚实命名。
