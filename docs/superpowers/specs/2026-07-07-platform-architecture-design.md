# 速派 · 整体架构设计 v1.0

> 2026-07-07 · Claude + 星辰联合设计 · 峰哥确认
> 硅谷 AI Native 产品构建范式对齐

---

## 一、产品定位

**速派 = 智能视觉协同平台**

为创意行业（摄影 → KOL 分发）打造的轻量协调层。不是 ERP，不是 SaaS 后台，而是"视觉行业的 Notion"——一个共享工作区，人、摄影师、KOL、Agent 在同一块画布上协作。

**AI Native 检验（CRV "Remove the AI Test"）：**

| 功能 | 删掉 AI | 结论 |
|------|--------|------|
| 四档匹配 + 多维度评分 | 人工翻列表 | AI Native ✅ |
| 摄影师可用性推断 | 手动打电话问 | AI Native ✅ |
| 分发路径推荐 | 自己找 KOL | AI Native ✅ |
| 项目看板 | 静态页面仍可看 | 壳（非核） |

**不做的事：**
- 不建 KOL 数据库（KOL/MCN 通过 API 接入）
- 不做内容生产（CodeX 做，平台不碰）
- 不做 CRM/财务系统
- 不做注册登录（v1）

---

## 二、三层架构

```
┌──────────────────────────────────────────────────┐
│          Experience Layer（薄壳）                  │
│                                                    │
│   One Workspace + Role Filters                     │
│   峰哥滤镜：全项目 + 运营面板 + Agent 状态          │
│   客户滤镜：我的项目 + 分发数据 + 匹配结果          │
│   摄影师滤镜：我的任务 + 接单交付 + 收益            │
│                                                    │
│   技术：单文件 HTML + Conversational Canvas        │
│   交互：侧栏 Chat/Command + 中央画布 + 数据面板     │
├──────────────────────────────────────────────────┤
│          Action Layer（共享动作）                   │
│                                                    │
│   一个动作 = 一次定义 = 所有入口共用                │
│                                                    │
│   dispatch(project, photographer)                   │
│     → 峰哥点按钮                                   │
│     → 客户点确认                                   │
│     → 星辰自动调                                   │
│     → Claude API 调                                │
│     → KOL MCP 调                                   │
│                                                    │
│   每个 Action = Python func + JSON schema + endpoint│
├──────────────────────────────────────────────────┤
│          Core Engine（厚核）                        │
│                                                    │
│   ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐   │
│   │ match  │ │  task  │ │distrib │ │ avail  │   │
│   │ 匹配   │ │ 任务   │ │ 分发   │ │ 可用性 │   │
│   └────────┘ └────────┘ └────────┘ └────────┘   │
│   ┌────────┐                                      │
│   │  data  │  统一数据层                           │
│   └────────┘                                      │
│                                                    │
│   纯 Python 3.11 stdlib · 零外部依赖 · 模块独立    │
└──────────────────────────────────────────────────┘
```

---

## 三、Core Engine — 模块设计

### 3.1 模块划分

| 模块 | 文件 | 职责 | 对外接口 |
|------|------|------|---------|
| **match** | `engine/match.py` | 四档匹配 + 多维度评分 | `match(requirement) → [Photographer]` |
| **task** | `engine/task.py` | 任务创建/状态流转/通知触发 | `create_task()`, `update_status()` |
| **distribution** | `engine/distribution.py` | 分发路径管理 + adapter 路由 | `distribute(project, channels)` |
| **availability** | `engine/availability.py` | 摄影师可用性状态机 | `check_available()`, `update_status()` |
| **data** | `engine/data.py` | 统一数据读写 + schema 验证 | `load()`, `save()`, `migrate()` |

### 3.2 模块接口契约

每个模块暴露统一签名的函数：

```python
# engine/match.py
def match(requirement: dict) -> dict:
    """
    input:  {"tier": "express", "scene": "发布会", "location": "上海", "budget": 5000}
    output: {"matches": [...], "verdict": "ok|review|reject", "issues": []}
    """
```

```python
# engine/task.py
def create_task(project_id: str, photographer_id: str, details: dict) -> dict:
    """
    input:  project_id, photographer_id, {time, location, requirements}
    output: {"task_id": "...", "status": "created", "timeline": []}
    """
```

```python
# engine/distribution.py
def distribute(project_id: str, channels: list) -> dict:
    """
    input:  project_id, ["client_owned_douyin", "kol_xiaohongshu_001"]
    output: {"dispatch_id": "...", "channels": [{"name": "...", "status": "sent", "tracking_url": "..."}]}
    
    channels 是 adapter 名称列表。新增分发路径 = 新增 adapter 实现同一接口。
    不改 distribute() 逻辑。
    """
```

```python
# engine/availability.py
def check_available(photographer_id: str, time_slot: dict) -> dict:
    """
    input:  "photographer_001", {"start": "2026-07-08T14:00", "end": "2026-07-08T18:00"}
    output: {"available": true, "confidence": 0.92, "source": "calendar|learned|default"}
    """
```

### 3.3 模块独立性规则

1. **每个模块只 import data 模块和标准库**，不跨模块 import
2. **新增模块不修改已有模块**——加 `distribution.py` 时不改 `match.py`
3. **模块间通过 data 层共享状态**，不直接调用对方函数
4. **每个模块有自己的 harness 测试**，改前改后都跑

---

## 四、Action Layer — 共享动作模型

### 4.1 核心原则

> 一个动作，定义一次。所有入口（UI/Agent/API/MCP）调用同一个函数。

```
         ┌─────────────────────────┐
         │     Action Definition    │
         │                         │
         │  dispatch(project, p)    │
         │  ├─ Python function      │
         │  ├─ JSON schema          │
         │  └─ HTTP endpoint        │
         └──────────┬──────────────┘
                    │
    ┌───────────────┼───────────────┐
    │               │               │
  峰哥UI         客户UI         Agent API
  (点按钮)       (点确认)       (星辰/Claude)
                    │
              KOL MCP
              (外部接入)
```

### 4.2 Action 列表与流转

**正常流（95% 自动，无人介入）：**

| Action | 触发 | 执行 |
|--------|------|------|
| `match_request` | 客户下单 | 星辰自动匹配 → 推送摄影师 |
| `confirm_photographer` | 摄影师回 1 | 自动确认 → 创建任务 |
| `submit_delivery` | 摄影师上传 | 自动入库 |
| `approve_delivery` | 交付完成 | Claude 自动审查通过 |
| `distribute_content` | 客户选路径 | 自动推送分发 |

**异常流（5%，分级处理）：**

| 异常 | Level 1（客服） | Level 2（峰哥） |
|------|----------------|-----------------|
| Top 2 分差 < 10 | 客服确认偏好 → 决策 | — |
| 摄影师超时未交付 | 客服联系确认 | 升级 → 峰哥处理 |
| 客户修改需求 | 客服手动调整 | — |
| 摄影师临时请假 | 客服标记 + 重新匹配 | — |
| 匹配分数 < 阈值 | Claude 审查 → 客服判断 | 疑难 → 峰哥 |
| 新品类/新策略 | — | 峰哥 + Claude 讨论 |
| 重大投诉 | — | 峰哥处理 |

**峰哥定位**：决策者，不是客服。只看 Level 2 升级和系统决策。

### 4.3 扩展 Action 的规则

新增 Action 只需：1) 在对应 Core 模块加函数 2) 注册到 Action 表 3) 自动获得所有入口支持。不需要改 UI 层或 Agent 层代码。

---

## 五、Experience Layer — 工作区与角色滤镜

### 5.1 交互模型：Conversational Canvas

```
┌─────────────────────────────────────────────┐
│  ┌─ 侧栏 ───────────────────────────────┐   │
│  │                                      │   │
│  │  💬 @Claude 审查上周匹配质量          │   │
│  │  📊 生成 express 档拒绝率图表          │   │
│  │  🔔 星辰：LuckLee 交付完成，请审查     │   │
│  │  ───────────────────────────────     │   │
│  │  ⌨️ 输入意图或指令...                 │   │
│  │                                      │   │
│  └──────────────────────────────────────┘   │
│                                             │
│  ┌─ 中央画布 ─────────────────────────┐     │
│  │                                      │     │
│  │  项目卡片             项目卡片        │     │
│  │  ┌────────────────┐ ┌────────────┐  │     │
│  │  │ 某品牌发布会    │ │ 某司年会   │  │     │
│  │  │ 📸 LuckLee     │ │ 📸 待匹配  │  │     │
│  │  │ 📦 20张已交付  │ │ ⏳ 进行中  │  │     │
│  │  │ 📢 抖音已发布  │ │            │  │     │
│  │  └────────────────┘ └────────────┘  │     │
│  │                                      │     │
│  └──────────────────────────────────────┘     │
│                                             │
│  ┌─ 数据面板（可折叠）──────────────────┐    │
│  │  📊 本周匹配: 12单                    │    │
│  │  📈 express档拒绝率: 40% → 28%       │    │
│  │  👤 在线摄影师: 8/20                 │    │
│  └──────────────────────────────────────┘    │
└─────────────────────────────────────────────┘
```

### 5.2 角色权限

同一份数据，四种视图：

| 角色 | 能看到 | 能操作 |
|------|--------|--------|
| **峰哥** | 全部项目、全部摄影师、Agent 状态、运营数据 | 所有 Action + 系统配置 + 匹配规则 |
| **人工客服**（1人） | 分配给自己处理的项目 + 摄影师库 | 操作项目、管摄影师信息、升级给峰哥 |
| **客服 Agent**（官方账号） | 全部项目 + 摄影师库 | 自动处理 Level 1 异常，无法处理 → 转人工客服 |
| **客户** | 自己项目的进度、匹配结果、分发数据 | 下单、确认、选分发路径 |
| **摄影师** | 分配给自己的任务、自己的收益 | 接单、上传交付、标记状态 |

**异常流分级**：

```
Level 0（客服 Agent 自动处理，60%）：
  Top 2 分差 < 10 → Agent 按规则自动选偏好
  摄影师超时 < 2h → Agent 自动提醒
  常见客户咨询 → Agent 自动回复

Level 1（人工客服，30%）：
  Agent 无法判断 → 转人工客服
  摄影师超时 > 2h → 人工联系
  客户修改需求 → 人工调整
  摄影师临时请假 → 人工标记 + 重匹配

Level 2（峰哥，10%）：
  新品类/新策略 → 峰哥决定
  重大投诉 → 峰哥处理
  匹配算法调整 → 峰哥 + Claude
```

实现方式：**后端权限过滤**。API 返回数据前按 `role` 字段裁剪。

### 5.3 技术选型

| 选择 | 理由 |
|------|------|
| React 19 + TypeScript | 2026 硅谷前端标准，Zod schema → Agent tool 自动生成 |
| Vercel AI SDK v6 | `useChat`/`streamText`/`tool()` 100行内完成 streaming + 工具调用 |
| shadcn/ui + Tailwind CSS 4 | 暗色主题开箱即用，Linear 级审美 |
| Python 3.11 标准库（后端） | Core Engine 零外部依赖，薄壳厚核 |
| JSON over HTTP + SSE | REST 操作 + AI SDK 流式反馈 |
| 暗色主题 | AGENTS.md 规则 |
| 无框线字符 | AGENTS.md Red Flag |

---

## 六、延展设计

### 6.1 分发路径 Adapter 模式

```
engine/distribution.py
  └── adapters/
      ├── owned_media.py     # 客户自有抖音/小红书/微博
      ├── kol.py             # 单个 KOL
      ├── mcn.py             # MCN 打包
      └── custom.py          # 自定义（任何实现同一接口的外部服务）

每个 adapter 实现：
  class DistributionAdapter:
      def send(project, channel_config) -> TrackingResult
      def status(tracking_id) -> ChannelStatus
```

新增分发路径 = 新增一个 adapter 文件。不改 `distribution.py` 逻辑。

### 6.2 KOL/MCN 接入

```
KOL/MCN 接入方式（三选一）：

1. API Key（简单）
   KOL 在平台生成 API Key → 调用 /api/distribute → 接收 Brief + 素材 → 发布 → 回传数据

2. MCP Server（标准）
   KOL/MCN 部署 MCP Server → 声明 Agent Card → 平台发现 → A2A 通信 → 自动分发

3. Discord/微信 Bot（轻量）
   KOL 加入频道 → 收到分发通知 → 回复确认 → Bot 追踪发布
```

### 6.3 新模块插拔

加一个新功能模块的标准流程（不改已有代码）：

```
1. 在 engine/ 下新建 module.py，实现接口
2. 在 data.py 加对应的 schema（如果是新数据类型）
3. 在 Action Layer 注册新 Action
4. Experience Layer 可选加对应的画布组件
5. 写 harness 测试
```

**设计保证**：已有模块的接口不变，已有 Action 的签名不变，已有数据的 schema 只增不减。

---

## 七、数据模型

### 7.1 核心实体

```
Project（项目）
  ├── id, client_id, requirement, status, created_at
  ├── match: {photographer_id, score, tier}
  ├── task: {task_id, status, timeline[]}
  └── distribution: [{channel, status, tracking_url, metrics}]

Photographer（摄影师）
  ├── id, name, tier, skills[]
  ├── availability: {status, source, current_task, learned_patterns}
  ├── stats: {completed, on_time_rate, avg_delivery_hours}
  └── calendar: {source, last_sync} (optional)

Client（客户）
  ├── id, name, contact
  └── owned_channels: [{platform, account_id}]
```

### 7.2 存储

| 阶段 | 方案 | 理由 |
|------|------|------|
| 当前（Phase 0） | `store.json` | 够用，5 个假数据 |
| 20 人上线（Phase 1） | SQLite (`store.db`) | 查询性能 + 并发安全 |
| 100+（Phase 3） | PostgreSQL | 多实例 + 全文搜索 |

**当前不迁**。等峰哥拉来 20 个真实摄影师 + 10 单匹配后触发 Phase 1。

---

## 八、开发阶段

| Phase | 内容 | 触发条件 |
|-------|------|---------|
| **Phase 0** | 当前：假数据 + 验证匹配算法 | ✅ 已完成 |
| **Phase 1** | 模块拆分（engine/*.py）+ 单文件 HTML 工作区 | 峰哥确认架构后启动 |
| **Phase 2** | 真实摄影师入 store + 匹配跑通 + 通知 Bot | 20 个摄影师就位 |
| **Phase 3** | distribution adapter + KOL API 接入 | 首次分发需求 |
| **Phase 4** | store.json → SQLite + 运营面板上线 | 日匹配 > 10 单 |
| **Phase 5** | Agent Mesh 全链路自动化 | 平台稳定运行后 |

---

## 九、技术约束

| 约束 | 来源 |
|------|------|
| Core Engine: Python 3.11 标准库，零外部依赖 | AGENTS.md |
| Frontend: React 19 + TypeScript + AI SDK v6 + shadcn/ui | 峰哥决策 2026-07-08 |
| 暗色主题，无框线字符 | AGENTS.md |
| 所有业务逻辑在 Core Engine，前端薄壳 | AGENTS.md |
| 改前改后跑 harness | AGENTS.md |
| 增量开发——模块可插拔，不重构已有代码 | 本设计 |
| Agent 和人类共用同一套 Action | Builder.io Agent-Native |

---

## 十、参考范式

| 来源 | 借鉴 |
|------|------|
| Probook (a16z) | Dispatch 是核心神经系统 |
| Builder.io | Agent-Native: 一个 action 所有入口共用 |
| OpenClaw Nerve | 多 Agent 驾驶舱，非聊天窗口 |
| Salesforce 6-Layer | Data→Security→Logic→Trust→AI→Experience |
| CRV AI-Native | Remove the AI Test |
| UXmatters Composable UX | 输出带 source/timestamp/confidence |
| Modular Monolith ADR | 先模块化单体，需要时再拆微服务 |

---

*峰哥确认：2026-07-07 · 星辰 acknowledge：2026-07-07*
*下一步：Phase 1 模块拆分 + 工作区 HTML*
