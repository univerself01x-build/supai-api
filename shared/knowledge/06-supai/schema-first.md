---
title: Schema-First
date: 2026-07-11
tags: [schema, data-validation, ai-native]
project: supai
phase: 1
status: applied
parent: "[[02-engineering/构建层 MOC]]"
---

# Schema-First

> **核心洞见：Schema 不是文档，是可执行契约。AI Native 项目没有编译器——Schema 是唯一能拦截格式错误的机制。**

## 是什么

在数据入口校验输入，违反就拒绝执行。不是事后 `isinstance()` 修补，而是在门口拦住。

## 怎么来的

速派 Phase 1 踩坑：
- skills 存成字符串 → 匹配算法按单字拆解（致命 bug）
- platform_id 重复 5 条 → 无人察觉
- 零技能重叠打出 36.4 分 → 算法正确但输入不可信

根因：Python 标准库 + JSON 没有类型检查。调用方可以传任意格式。

## 在速派怎么用的

```python
@dataclass
class CitizenInput:
    skills: list[str]  # 不是 str，必须是 list
    
    def __post_init__(self):
        if not isinstance(self.skills, list):
            raise ValueError("skills must be list")
```

## 对比

| | 传统开发 | AI Native |
|--|---------|-----------|
| 类型检查 | TS 编译器 | Schema 运行时校验 |
| 错误发现 | IDE 红线 | 数据入口抛异常 |
| 代价 | 无（编译时） | 运行时过滤无效请求 |

## 相关

- [[Contract-First]]
- [[02-engineering/Agent-Native 架构]]
