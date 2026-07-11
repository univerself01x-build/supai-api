---
title: Contract-First
date: 2026-07-11
tags: [api, contract, ssoT, openapi]
project: supai
phase: 1
status: applied
parent: "[[02-engineering/构建层 MOC]]"
---

# Contract-First

> **核心洞见：API 契约是前后端和 Agent 三者之间的唯一真相源。先定契约再写代码，不是写完再补文档。**

## 是什么

API 契约定义接口的输入输出格式。Pydantic models 是 SSOT（Single Source of Truth）——FastAPI 自动生成 OpenAPI，openapi-typescript 自动生成 TypeScript 类型。改一处，其余自动同步。

## 怎么来的

速派 Phase 1 最初手写了三份定义——YAML + Python + TypeScript。Contract-First 修正后改为 Pydantic 唯一真相源流水线。

## 在速派怎么用的

```python
# api_models.py — 唯一真相源
class MatchRequest(BaseModel):
    scene: str
    budget: int
    location: str = "上海"

class MatchResult(BaseModel):
    projectId: str
    tier: str
    recommendedTeam: list[TeamSlot]
    summary: str
```

```bash
# SSOT 流水线
scripts/gen-openapi.py  →  docs/openapi.json  →  openapi-typescript  →  api.generated.ts
```

## 对比

| | 手写 | Contract-First |
|--|------|---------------|
| 改一处 | 改三个文件 | 改 api_models.py |
| Agent 可读 | 需人工解释 | OpenAPI spec 直接可用 |
| 类型安全 | 靠记忆 | 编译时检查 |

## 相关

- [[Schema-First]]
- [[02-engineering/SSOT 流水线]]
