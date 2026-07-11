# 速派 · 产品规格书 v1.0

> 整合自：架构设计、设计方向、API 契约、PRD、Glossary
> 2026-07-09 · Claude + 星辰 + 峰哥

---

## 一、产品定位

**速派 = AI 行业数字活动视觉 Team 协作平台**

客户描述需求 → AI 匹配视觉 Team → 确认 → 交付。
不是摄影派单平台，不是 SaaS 后台，是"视觉行业的 Notion"。

**目标用户**：AI 公司/AI 从业者（AI 产品发布、Demo Day、Hackathon、AI 峰会）
**不做**：泛企业活动、KOL 数据库、内容生产、注册登录

## 二、当前状态

**Phase 1 已完成：**
- Core Engine：`engine/{__init__,core,schema}.py`，Python 3.11 stdlib
- API Server：FastAPI + Pydantic，`:8080`，`/docs` 在线
- React 前端：Next.js 16 + shadcn/ui + AI SDK v6，`:3000`
- 数据：20 条模拟摄影师数据（摄影为主，上海 75%，四档覆盖）
- Harness：24/24
- SSOT 流水线：`scripts/gen-openapi.py` → `openapi-typescript` → 前端类型

**Phase 1 未完成/近期补的：**
- 审美审查未正式做
- Concierge Test 未执行（0 真实交易）

## 三、核心交互

```
用户打开 → 底部输入框 → 输入"AI产品发布会，上海，5000"
→ 2px 状态条蓝紫渐变呼吸 → 匹配结果以对话气泡出现在上方
→ 项目卡片（标题 + 档位 badge + 城市 + 预算 + 摄影师 + 时间）
→ 点击卡片展开 Team 详情面板
```

**关键规则**：
- 底部输入框（AI 产品范式），不是顶部搜索框
- 客户视角：`?role=client&client_id=X` 只看到自己的项目
- 峰哥视角：默认看到全部
- 2px 状态条在输入框上方：空闲透明、匹配蓝紫渐变、完成绿闪、异常红
- 暗色主题，系统字体栈，8px 栅格

## 四、技术栈

| 层 | 技术 | 约束 |
|----|------|------|
| Core Engine | Python 3.11 stdlib | 零外部依赖 |
| API Server | FastAPI + Pydantic | SSOT → OpenAPI → TypeScript |
| Frontend | React 19 + TypeScript + Next.js 16 + shadcn/ui + Tailwind CSS 4 | 暗色主题，无框线字符 |
| Agent 通信 | A2A v0.3（inbox/outbox 文件通道） | TextPart + DataPart |
| 数据 | `store.json`（JSON 文件） | Phase 3 迁 SQLite |

## 五、数据模型

**Citizen（摄影师）：** name, platform_id（唯一）, skills（数组）, tier, rating, completed_tasks, price_range, location, equipment, languages, available

**Task（项目）：** id, title, description, client_id, budget, location, tier, status, matched_citizens（数组）, accepted_by, created_at

**角色权限：** 峰哥（全部）、客服 Agent（Level 0 自动）、人工客服（Level 1）、客户（自己的项目）、摄影师（自己的任务）

## 六、API Endpoints

| Method | Path | 用途 |
|--------|------|------|
| GET | `/api/projects?role=&client_id=` | 项目列表（角色过滤） |
| GET | `/api/projects/{id}?role=` | 项目详情 |
| POST | `/api/match` | 提交需求 → 匹配 Team |
| POST | `/api/projects/{id}/confirm` | 确认团队成员 |

## 七、Concierge Test 目标

**测什么：** 5-10 个真实客户，手动跑完匹配→确认链路
**不建什么：** H5 确认页、通知 Bot、多角色匹配、distribution adapter
**操作方式：** 峰哥微信聊客户 → 系统输入需求 → 复制匹配结果发微信群 → 摄影师回复 → 系统确认

**验收标准：**
- 客户愿意描述需求：5/5
- 匹配结果有用（客户接受率 > 70%）
- 摄影师愿意接（确认率 > 50%）
- 完整闭环：至少 3 单
- 决定 Phase 2 做什么

## 八、关键决策记录

| 日期 | 决策 |
|------|------|
| 07-04 | Peer-to-Peer 架构（非 Orchestrator） |
| 07-06 | A2A v0.3 — TextPart + DataPart 双通道 |
| 07-07 | 三层架构：Core Engine → Action Layer → Experience Layer |
| 07-08 | 技术栈确定：React 19 + TS + FastAPI + Pydantic + SSOT 流水线 |
| 07-08 | Design Direction — Linear/Vercel/Stripe/Raycast 参考 |
| 07-09 | 通知通道：微信群手动，不建 Bot/Discord/短信 |
| 07-09 | Concierge Test 优先于 Phase 2 开发 |
