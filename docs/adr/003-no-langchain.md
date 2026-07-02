# ADR 003: 不使用 LangChain

## 状态
已采纳 (2026-07-02)

## 背景
需要让 AI 模型调用匹配引擎。

## 决策
直接调 DeepSeek API + 自定义 system prompt。不使用 LangChain 或任何 AI 框架。

## 替代方案
- LangChain：2023年标准，2025-2026年社区大规模退场
- LlamaIndex：专注 RAG，不适用于我们的场景
- CrewAI：多 Agent 框架，过度抽象

## 后果
✅ 代码量 = 我们实际需要的行数，不是框架要求的行数
✅ 升级模型 = 换一个 API key
✅ 出 bug 在 500 行 engine.py 里找，不在框架的黑盒里
❌ 没有内置的 tool definition schema（自己写了几行）
