---
title: MAP · 知识地图
date: 2026-07-06
tags: [map, architecture, knowledge-base]
status: accepted
owner: claude
---

# MAP · 知识地图 /mæp/

> 按硅谷范式组织的 Obsidian 知识体系架构。Claude 设计架构，星辰填充内容，峰哥主导方向。
> 最后更新：2026-07-06

---

## 一、目录结构

```
shared/knowledge/
├── MAP.md                          ← 本文件（知识地图总纲）
├── home.md                         ← 入口面板（星辰已建 ✅）
│
├── ai-fundamentals/                ← Domain: AI 基础理论
│   ├── AI 基础.md                  ← 星辰已建 ✅（AIMA §2.4/§26/§17.6）
│   ├── agent-types.md              ← 五层 Agent 演化深度版
│   ├── peas-framework.md           ← PEAS 多 Agent 扩展
│   ├── value-alignment.md          ← AI Safety vs 分布式可靠性
│   └── communication-protocols.md  ← FIPA / A2A / MCP 对比
│
├── agent-engineering/              ← Domain: Agent 研发实战
│   ├── Agent 研发.md               ← 星辰已建 ✅（四Agent架构）
│   ├── communication/              ← 子域：通信协议
│   │   ├── a2a-protocol-v0.3.md    ← 当前协议快照（从 context/shared/ 引用）
│   │   └── protocol-evolution.md   ← v0.1 → v0.2 → v0.3 演进史
│   ├── security/                   ← 子域：安全检查
│   │   ├── triple-critic.md        ← 三层 Critic 检查点
│   │   └── failure-modes.md        ← 已知失败模式 + 回退策略
│   └── limitations.md              ← 已知架构限制 + 升级触发条件
│
├── silicon-valley/                 ← Domain: 硅谷范式
│   ├── 硅谷范式.md                 ← 星辰已建 ✅
│   ├── build-principles/           ← 子域：构建原则
│   │   ├── thin-shell-thick-core.md
│   │   ├── declarative-systems.md
│   │   └── error-as-product.md
│   ├── engineering-standards/      ← 子域：工程规范
│   │   ├── prd-template.md
│   │   ├── api-contract-first.md
│   │   └── red-flags-checklist.md
│   └── reference-companies/        ← 子域：参考公司
│       ├── stripe-api-design.md
│       ├── linear-design-system.md
│       └── vercel-platform.md
│
├── decisions/                      ← Domain: 架构决策（ADR）
│   ├── 架构决策.md                 ← 星辰已建 ✅
│   └── adr-template.md             ← ADR 模板
│
├── workflows/                      ← Domain: 工作流（Owner: 星辰）
│   ├── daily-startup.md            ← 每日启动流程
│   ├── code-review-flow.md         ← 代码审查流程
│   ├── task-dispatch-flow.md       ← 任务分发流程
│   └── incident-response.md        ← 故障响应流程
│
├── toolchain/                      ← Domain: 工具链（Owner: 星辰）
│   ├── claude-code.md
│   ├── hermes-agent.md
│   ├── codex-cli.md
│   ├── cc-switch.md
│   └── obsidian.md
│
├── shared/daily/                   ← 每日面板（星辰已建 ✅）
│   ├── README.md                   ← 每日面板说明
│   └── 2026-07-XX.md               ← 每日记录（模板驱动）
│
└── templates/                      ← 模板库
    ├── note-template.md            ← 通用笔记模板
    ├── adr-template.md             ← ADR 模板
    ├── daily-template.md           ← 每日记录模板
    └── review-template.md          ← 代码审查模板
```

**设计原则**：
- **最多 3 层深度** — 超过 3 层就拍平（Obsidian 用 wikilinks 做逻辑分组，不靠目录层级）
- **已建文件不移动** — 星辰建的 5 个文件位置不变，新增子域文件放在同目录下
- **子域拆分时机** — 单个文件超过 200 行或包含 ≥ 3 个独立概念时，拆为子域目录

---

## 二、文件命名规范

| 规则 | 示例 | 原因 |
|------|------|------|
| 中文名用于 Obsidian 显示 | `AI 基础.md` | 峰哥浏览时直觉可读 |
| 子域用英文 kebab-case | `thin-shell-thick-core.md` | wikilink 无空格、无大小写歧义 |
| 模板以 `-template` 结尾 | `adr-template.md` | 一目了然 |
| 每日记录 `YYYY-MM-DD.md` | `2026-07-06.md` | Obsidian 日记插件兼容 |
| 版本快照带版本号 | `a2a-protocol-v0.3.md` | 历史追溯 |

---

## 三、模板

### 通用笔记模板（`templates/note-template.md`）

```markdown
---
title: <标题>
date: <YYYY-MM-DD>
tags: [<领域>, <类型>]
parent: "[[<父页面>]]"
status: draft | reviewed | accepted
owner: claude | hermes | both
---

# <标题> · <英文> /<IPA 音标>/

> <一句话摘要>

## <第一节>

<内容——关键认知用 > 标注>

## 来源

- <AIMA §X.Y> | <Stripe API 文档链接> | <实战踩坑>

---
*创建: <日期> · 最后审查: <日期> · 下次审查: <日期+90天>*
```

### ADR 模板（`templates/adr-template.md`）

```markdown
---
title: <简短动词短语>
date: <YYYY-MM-DD>
tags: [decisions, adr]
status: proposed → accepted → deprecated → superseded
---

# ADR: <标题>

- **状态**: proposed / accepted / deprecated / superseded
- **上下文**: 为什么需要这个决策
- **决策**: 做了什么选择
- **替代方案**: 考虑过但没选的方案及原因
- **后果**: 
  - ✅ 正面影响
  - ⚠️ 负面影响 / 风险
  - 🔗 影响哪些系统/Agent
- **相关**: [[相关 ADR]] | [[相关概念]]
```

### 每日记录模板（`templates/daily-template.md`）

```markdown
---
title: <YYYY-MM-DD>
date: <YYYY-MM-DD>
tags: [daily]
---

# <YYYY-MM-DD> · 每日面板 /ˈdeɪli/

## 今日学习

| 概念 | 来源 | 一句话理解 |
|------|------|-----------|
| ... | ... | ... |

## 知识更新

- [ ] 新术语加入 glossary.md
- [ ] 关键决策写入 decision-log.md
- [ ] 新概念写入对应 domain 文件

## 待归档

- [ ] ...
```

---

## 四、每日知识沉淀流程

```
每日交互结束 →
  ├── 1. 识别值得留存的知识（新概念/踩坑/范式确认）
  ├── 2. 判断归属 domain
  │     ├── AI 理论 → ai-fundamentals/
  │     ├── Agent 实战 → agent-engineering/
  │     ├── 硅谷范式 → silicon-valley/
  │     ├── 工作流 → workflows/（星辰主导）
  │     └── 工具 → toolchain/（星辰主导）
  ├── 3. 判断粒度
  │     ├── 术语定义 → glossary.md（一行）
  │     ├── 一句话认知 → domain 文件加一条 > 引用
  │     ├── 独立概念 → 新建子域文件
  │     └── 重大决策 → ADR
  ├── 4. 写 daily 面板（今日学习表格 + 待归档清单）
  └── 5. 峰哥 Obsidian 打开 → 图谱视图 → 看到新节点
```

**规则**：
- **不追求每天都有产出** — 没学到新东西就不写，不为了填面板而填面板
- **一条 > 标注就够了** — 不用每个概念都开新文件，一句话洞察塞进对应 domain 文件即可
- **每周日回顾** — 星辰扫一遍本周 daily，把临时笔记归档到对应 domain

---

## 五、硅谷同频迭代机制

### 触发源

| 来源 | 频率 | 行动 |
|------|------|------|
| Anthropic Changelog | 每次发布 | Claude 读了 → 判断是否需要更新 `silicon-valley/` |
| Google A2A Spec | 版本升级 | 星辰 监控 → 更新 `a2a-protocol-vX.X.md` |
| Stripe/Linear/Vercel 文档 | 大改版时 | 星辰 或 Claude 发现 → 更新对应 reference 文件 |
| Hacker News / 论文 | 出现新范式时 | Claude 分析 → 写 critical-insight，标记 `status: draft` |
| AIMA 新版 | 发布时 | Claude 对比旧版 → 更新 `ai-fundamentals/` 相关章节 |
| 我们自己踩的坑 | 每次踩坑 | 星辰 记录到 `workflows/` → Claude 审查是否有通用范式 |

### 更新流程

```
外部触发 →
  1. 星辰或 Claude 写 draft → 放入对应 domain
  2. 对方审查（互审）
  3. 标注 status: reviewed
  4. 通知峰哥（summary 一句话：学了什么、为什么重要）
```

### 版本追踪

- `glossary.md` 头部维护 `last_sync: <日期>`
- 每个 domain 文件 frontmatter 加 `last_reviewed: <日期>` 和 `next_review: <日期+90天>`
- 超过 90 天未审查的文件，星辰自动标记为 `status: stale`

---

## 六、所有权矩阵

| Domain | Owner（写） | Reviewer（审） | 模板 |
|--------|------------|---------------|------|
| `ai-fundamentals/` | Claude | 星辰 | note-template |
| `agent-engineering/` | Claude（架构）/ 星辰（实现） | 互审 | note-template |
| `silicon-valley/` | Claude | 星辰 | note-template |
| `decisions/` | 双方 | 双方 | adr-template |
| `workflows/` | 星辰 | Claude | note-template |
| `toolchain/` | 星辰 | Claude | note-template |
| `shared/daily/` | 星辰 | — | daily-template |
| `MAP.md` | Claude | 星辰 | — |
| `home.md` | 星辰 | Claude | — |

---

## 变更记录

| 版本 | 日期 | 变更 |
|------|------|------|
| v1.0 | 2026-07-06 | Claude 设计初始架构。5 个文件已建（星辰），MAP.md 上线 |
