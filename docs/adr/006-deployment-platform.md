# ADR 006: 部署平台选型 — Vercel (前端) + Railway (后端)

- **状态**: accepted
- **日期**: 2026-07-11
- **上下文**: Phase 1 完成，需要线上闭环。Render 需海外信用卡被卡
- **决策**: 前端 Vercel（Next.js 原生支持）· 后端 Railway（Git auto deploy + 支付宝）。ECS 留 Phase 2+ 当国内优化
- **替代方案**: 
  - Render（最佳 DX，被支付渠道阻塞）
  - 阿里云 ECS（长期对但 Phase 1 运维太重）
  - Zeabur（备选，如果 Railway 支付也不通）
- **后果**: 
  - ✅ 零运维 auto deploy，和 Vercel 一致体验
  - ✅ 支持支付宝/微信支付
  - ⚠️ 国内访问速度待验证（慢则迁 ECS）
  - ⚠️ store.json 持久化需验证（Railway 文件系统支持）
