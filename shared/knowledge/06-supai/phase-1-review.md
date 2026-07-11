---
title: Phase 1 复盘
date: 2026-07-11
tags: [phase-review, match-engine, deploy]
project: supai
phase: 1
status: applied
parent: "[[06-supai/速派 MOC]]"
---

# Phase 1 复盘

## 做了什么

- Contract-First: API 契约 → OpenAPI → SSOT
- Schema-First: CitizenInput dataclass 入口校验
- 匹配引擎: 四档匹配 + 零技能重叠硬过滤 + 同义词映射 + 地域加成
- 前端: React 19 + TS + AI SDK v6，底部对话流
- 确认页: H5 一键确认接单

## 踩过的坑

- skills 存成字符串 → 匹配算法按单字拆解
- platform_id 重复 5 条 → 加唯一性校验
- 零技能重叠打出 36.4 假分 → 硬过滤基线分

## 产出的知识卡片

- [[06-supai/Schema-First|Schema-First]]
- [[06-supai/Contract-First|Contract-First]]
- [[06-supai/AI Native 对话流|AI Native 对话流]]
