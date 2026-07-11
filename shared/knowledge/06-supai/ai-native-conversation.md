---
title: AI Native 对话流
date: 2026-07-11
tags: [ui, conversation, ai-native, paradigm]
project: supai
phase: 1
status: applied
parent: "[[03-design/设计层 MOC]]"
---

# AI Native 对话流

> **核心洞见：AI 产品的交互不是表单+列表，是底部输入框+对话气泡+状态条。用户说一句话，Agent 回应。这是 2026 年所有 AI 产品的共同范式。**

## 是什么

- 底部固定输入框，Enter 发送，无按钮
- 对话历史以气泡形式在上方滚动
- 2px 状态条在输入框上方：空闲透明、匹配中蓝色呼吸、完成绿闪
- 参考：ChatGPT / Claude / Cursor / v0.dev / Bolt.new

## 为什么不是顶部搜索框

顶部输入框 + 下方卡片列表是搜索工具模式（Google/飞书搜索）。AI 产品是对话模式——用户和 Agent 持续交互，不是一次性查询。

## 在速派怎么用的

- 输入框固定在页面底部，placeholder: "描述你的需求，AI 帮你匹配摄影师"
- 用户回车 → 状态条蓝色呼吸 → 匹配完成绿闪
- 结果以对话气泡形式出现在上方，AI 头像 + 时间戳
- localStorage 持久化对话历史

## 关键决策

输入框从顶部移到底部经历了三轮迭代：
1. Phase 1.0: 顶部输入框 + 卡片列表（搜索工具模式）
2. Phase 1.1: 底部输入框 + 对话气泡（AI 产品模式）
3. Phase 1.2: + 语音输入 + 状态条绿闪动效

## 相关

- [[03-design/状态条设计]]
- [[05-frontier/2026 AI 产品交互范式]]
