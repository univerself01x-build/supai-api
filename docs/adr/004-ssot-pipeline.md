# ADR 004: SSOT Pipeline — Pydantic → OpenAPI → TypeScript 自动生成

- **状态**: accepted
- **日期**: 2026-07-09
- **上下文**: Phase 1 初期手写了三份 API 定义（OpenAPI YAML + Python dataclass + TypeScript interface）。峰哥指出应遵循 2026 年 Contract-First 范式
- **决策**: api_models.py (Pydantic) 作为唯一真相源。FastAPI 自动生成 OpenAPI。openapi-typescript 自动生成 TypeScript 类型。不再手写同步
- **替代方案**: 
  - 手写三份（√ 最初做法，峰哥否决）
  - 只用 stdlib dataclass（功能不足，无法自动生成 OpenAPI）
- **后果**: 
  - ✅ 改一个字段只改 api_models.py，其余自动同步
  - ✅ 前端类型安全，编译时捕获不匹配
  - ⚠️ 引入 Pydantic 依赖（仅 API 层，Core Engine 仍 stdlib）
  - 🔗 关联：001-python-stdlib（Core Engine 零依赖准则）
