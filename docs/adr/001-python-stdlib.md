# ADR 001: Python 标准库作为后端

## 状态
已采纳 (2026-07-02)

## 背景
需要为数字公民平台搭建 HTTP API 和 Web 前端。

## 决策
使用 Python 3.11 标准库 (`http.server`)，不引入任何 Web 框架。

## 替代方案
- FastAPI：功能强大，但对 1 个 API 端点过度
- Flask：轻量但仍是额外依赖
- Node.js + Express：需要额外运行时

## 后果
✅ 零依赖，一条命令启动
✅ 和 engine.py 同一语言，直接 import
✅ 部署 = 复制一个文件
❌ 没有自动 API 文档（PRD 里手写了）
❌ 没有异步支持（1个端点不需要）
