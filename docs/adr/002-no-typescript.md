# ADR 002: 前端不使用 TypeScript/React

## 状态
已采纳 (2026-07-02)

## 背景
需要为客户搭建任务发布和匹配结果查看页面。

## 决策
使用单文件 HTML + 原生 JavaScript，零构建。

## 替代方案
- TypeScript + React + Next.js：Vercel 推荐，但对单页面过度
- Vue/Svelte：好方案但仍是额外依赖层
- htmx：理念一致但增加一个依赖

## 后果
✅ 0 dependency，iPhone SE 秒开
✅ 改一行刷新浏览器就行
✅ 任何 AI Agent 都能直接编辑（不用懂框架）
❌ 页面 > 3 个时需要重构（到时再做 ADR）
