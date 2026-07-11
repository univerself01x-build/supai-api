# 速派 · Phase Gate 标准 v1.0

> 每个 Phase 必须通过 Gate Review 才能进入下一 Phase。
> 参考：eBay Mercury Pipeline——每阶段有硬性验收标准，不"差不多就行"。

## Phase 1 Gate

**进入条件：** 产品规格书确认 + 技术栈选定 + 团队分工明确

**退出标准：**
- [ ] Harness 24/24
- [ ] API 4 端点全部可调用
- [ ] 前端 order.html + page.tsx 渲染正常
- [ ] 匹配链路：输入需求→返回 Team→确认 跑通
- [ ] 设计方向确认（Step D Gate 通过）
- [ ] 20 条模拟数据符合质量标准

**当前状态：** ✅ 全部通过

## Phase 2 Gate

**进入条件：** Phase 1 Gate 全部 ✅ + Concierge Test 至少 1 单真实闭环

**退出标准：**
- [ ] 多角色 Team 匹配（photographer + 至少 1 个其他角色）
- [ ] 通知机制跑通（卡片复制 → 微信群 → 摄影师确认）
- [ ] 至少 3 单真实交易完整闭环
- [ ] L3 指标达标（接受率>70%, 确认率>50%）
- [ ] Phase 2 复盘 → 3-5 张知识卡片写入 Obsidian

## Phase 3 Gate

**进入条件：** Phase 2 Gate 全部 ✅

**退出标准：**
- [ ] distribution adapter 至少 1 条路径跑通
- [ ] KOL/MCN API 接入（至少 1 个外部接入）
- [ ] 客服 Agent Level 0 自动处理 60% 异常
- [ ] store.json → SQLite 迁移
- [ ] L2 指标达标（匹配准确率>80%, 空匹配率<10%）

## Phase 4 Gate

**进入条件：** Phase 3 Gate 全部 ✅

**退出标准：**
- [ ] 运营面板上线（峰哥视图）
- [ ] 每日数据自动汇总
- [ ] 日匹配 >10 单
- [ ] Agent Mesh 全链路自动化（Claude 定期审查+CodeX 内容分发）
- [ ] 知识体系自动沉淀（Phase 复盘→Obsidian 卡片）

## Gate Review 流程

```
Phase 完成 → Claude/星辰 分别自检 Gate 清单
→ 双方对齐 → 峰哥最终确认
→ state.json 更新 gate_status
→ 进入下一 Phase
```
