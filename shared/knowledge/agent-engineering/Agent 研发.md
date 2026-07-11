---
title: Agent 研发
date: 2026-07-05
tags: [agent, engineering, multi-agent]
parent: "[[home]]"
---

# Agent 研发 · Agent Engineering /ˌendʒɪˈnɪrɪŋ/

## 四 Agent 架构（速派实战）

| Agent | 类型 | 核心能力 | 禁止 |
|-------|------|---------|------|
| Claude | Utility-based /juːˈtɪləti/ | 架构决策、代码审查、审美 | 批量执行、内容生产 |
| 星辰 | Model-based + Critic /ˈkrɪtɪk/ | 调度、消息路由、验证、记忆 | 代码生成、架构决策 |
| CodeX | Goal-based /ɡoʊl/ | 并行批量执行（代码/视频/图文） | 架构决策、价值判断 |
| 峰哥 | Ultimate Critic | 最终决策、价值对齐、品味 | — |

## 通信协议 — FIPA v0.2

```json
{
  "from": "claude|hermes|codex|fengge",
  "to": "...",
  "type": "inform|request|query|cfp|propose|accept|reject",
  "payload": {},
  "status": "pending|processing|done|blocked|error"
}
```

- 目录语义: `inbox/` = 该 Agent 接收的消息，`outbox/` = 该 Agent 发出的响应
- [[../decisions/架构决策#2026-07-04-FIPA-v02|决策记录]]

## 安全检查

三重 Critic /ˈkrɪtɪk/ 检查点:

```
CodeX 产出 → harness 自动验证 → Claude 审查 → 峰哥最终确认
```

可靠性规则:
1. 破坏性操作必须有 Critic 检查点
2. Agent 失败 → 回退安全状态
3. 不静默失败 / Silent Failure /ˈsaɪlənt ˈfeɪljər/
4. 峰哥 Human-in-the-loop /ˈhjuːmən ɪn ðə luːp/

## 已知架构限制

- Claude Code 是交互式 CLI，非 server 模式 → 不能常驻
- 文件通道是松耦合异步通信，非实时
- 决策：当前规模够了。等日活 20+ 摄影师 + 10 单匹配时再升级
