# ADR 001: 前端技术栈选型

**日期**: 2026-07-06  
**决策者**: 峰哥  
**状态**: 已确认

## 决策

前端使用 **React 19 + TypeScript + Vercel AI SDK v6**。

## 背景

Phase 1 前端需求：项目卡片列表 + 详情面板 + Agent 交互。之前 AGENTS.md 规定"单文件 HTML 零 JS 框架"——该约束是针对单页面场景，不适用于需要持续演进的完整前端。

## 选项

| 选项 | 理由 |
|------|------|
| A: 单文件 HTML + Vanilla JS | Phase 0 够用，但无法支撑长期演进 |
| B: Python 全栈 (FastHTML/FastUI) | 不符合硅谷主流范式 |
| **C: React 19 + TS + AI SDK v6** | **硅谷 2026 AI Agent 前端主流方案** |

## 影响

- 需要 npm/构建工具链
- AI SDK v6 原生支持 Agent 流式输出渲染
- TypeScript 提供类型安全（弥补 Python 后端无类型检查的问题）
- 后端保持不变：Python 3.11 标准库零外部依赖
