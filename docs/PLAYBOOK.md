# 速派 · 产品工程 Playbook v1.0

> 活的文档。每次学到新东西、犯过错、改过架构，都更新这里。
> 不是写出来给人看的——是写出来照着做的。

---

## 一、设计系统

### 色彩
```
底色   #0a0a0a | 卡片   #1a1a2e | 强调   #6366f1
文字   #f8fafc (90%) | 副文字 #94a3b8 | 成功 #22c55e
错误   #ef4444 | 边框   #334155 | 
```

### 字体
```
系统默认字体栈，不加载 Web Font
移动端 14px 正文，16px 标题
```

### 间距
```
卡片间距 12px | 区块间距 24px | 页面边距 16px
只用 4 的倍数
```

### 动效
```
流式输出用 typing indicator（三个点跳动）
匹配进度用进度文字，不用进度条
过渡动画 ≤ 200ms
```

---

## 二、AI 原生交互原则

| # | 原则 | 来源 |
|:--:|------|------|
| 1 | 声明式输入 — 用户一句话说完，不问多余问题 | 源点AI Intent层 |
| 2 | 流式反馈 — 过程可见，不是黑盒 | Cursor / Vercel |
| 3 | 空状态有引导 — 新页面不空白 | Stripe / Linear |
| 4 | 错误当产品 — 出错时用户不慌 | Stripe |
| 5 | 格式不经过模型 — 引擎直接渲染 | 我们的教训 |
| 6 | 暗色优先 — 所有产品统一暗色主题 | Linear / Cursor |

---

## 三、工程规范

### 开发流程
```
PRD (1页) → API契约 → 写代码 → Harness → Red Flags审查 → 发布
```

### 代码结构
```
薄壳 + 厚核 (mattpocock)
  薄壳：HTML / API endpoint — 参数校验 + 调引擎
  厚核：engine.py — 全部业务逻辑
```

### Harness 标准
```
每个 API endpoint ≥ 3 个测试
每个 engine 函数 ≥ 1 个测试
修改 engine 后跑 python3 harness.py
```

### Red Flags（发布前全 ✅）
- [ ] 手机端不横向滚动
- [ ] 无框线/分隔线字符
- [ ] 引擎输出直达用户，不经模型
- [ ] 空状态有引导
- [ ] 错误状态有解释
- [ ] Harness 全部通过
- [ ] API 响应 < 2s

---

## 四、架构原则

### 三层分离
```
入口层   QQ/微信/飞书/Web — 只管收发
引擎层   engine.py — 只管业务逻辑
输出层   card_*() / a2a — 只管格式
入口挂了不影响引擎，引擎挂了有 A2A 兜底
```

### 双通道
```
人 → handle_message() → {human: 卡片}      ← 飞书/Web
Agent → a2a_*() → {agent: JSON}         ← Codex/Claude
同一套引擎，两种输出格式
```

### Boil the Ocean (gstack)
```
每次功能做完整：成功态 + 失败态 + 空态 + 加载态
不遗留"以后再补"
```

---

## 五、子代理审查 (superpowers SDD)

```
匹配流程：match_task() → review_match() → deliver_if_approved()
审查维度：Spec(技能是否匹配) + Quality(分数分布是否合理)
未通过审查 → 带 ⚠️ 标记交付给用户
```

---

## 六、产品档位

```
首发定制 · 25% · 新品发布 + KOL宣发 · 独立运营
资深     · 20% · 4.5+ / 15单+
专业     · 15% · 4.0+ / 5单+
速拍     · 10% · 无门槛
```

---

## 七、多 Agent 架构（v1.1 新增）

### Agent 闭环（AIMA §2.4.7）
```
每个 Agent 内部自成闭环:
  Claude — Utility-based: 架构决策、代码审查、审美判断
  CodeX  — Goal-based: 并行批量执行（代码/视频/图文/测试）
  星辰   — Model-based + Critic: 状态追踪、消息路由、harness 验证
  峰哥   — Ultimate Critic: 价值对齐、最终决策
```

### 通信协议（FIPA 风格消息路由）
```
统一消息格式 → 所有 Agent 对等接入
  context/claude/inbox/  — 发给 Claude 的消息
  context/claude/outbox/ — Claude 发出的响应
  context/hermes/inbox/  — 发给星辰的消息
  context/hermes/outbox/ — 星辰发出的响应
  context/codex/inbox/   — 发给 CodeX 的消息（预埋）
  context/codex/outbox/  — CodeX 发出的响应（预埋）

语义: inbox = 该 agent 接收，outbox = 该 agent 发出
协议规范: context/shared/a2a-protocol.md v0.2
```

### 合同网（预埋，Phase 2）
```
任务状态机: announced → bidding → awarded → executing → completed/failed
cfp/propose/accept/reject 原语已定义，当前规模不需要全量启用
```

### 安全检查
```
三层 Critic: harness 自动验证 → Claude 审查 → 峰哥确认
可靠性: 不静默失败、回退安全状态、峰哥兜底
AI Safety: 目标误对齐审查、路由质量权重 ≥ 效率权重、星辰定位为 agent 非平台
```

### 架构决策
```
决策记录: shared/decision-log.md
协议规范: shared/a2a-protocol.md
消息格式: 统一 {from, to, type, intent, payload, thinking, status, ref}
```

```
每次版本升级更新 Playbook
每发现一个生产 bug → 加一条 Red Flag
每学到一个新模式 → 加一条原则
每 2 周回顾一次，删掉不再适用的条目
```

---

## 版本历史
| 版本 | 日期 | 变更 |
|------|------|------|
| 1.0 | 2026-07-02 | 初版。合并 PRD + DEV-STANDARDS + UX-DESIGN + 3Git + 硅谷体验 |
| 1.1 | 2026-07-04 | 多 Agent 架构共识：Agent 闭环 + FIPA 消息路由 + 合同网预埋 + AI Safety |
