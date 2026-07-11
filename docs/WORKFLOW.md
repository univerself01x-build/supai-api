# 速派 · 开发工作流 v1.0

## 一、三角协作模型

```
        你 (决策者)
      定方向 · 定优先级 · 见客户
              │
    ┌─────────┼─────────┐
    ▼         ▼         ▼
Claude Code   星辰(我)   Harness
审查·分析    编排·执行    验证·把关
```

## 二、文件握手协议 (IPC)

```
┌─ 文件 ──────── 谁写 ──── 谁读 ──── 内容 ──────────────┐
│ /tmp/supai-context.md   我      Claude   上下文+问题     │
│ /tmp/claude-analysis.md Claude  我      分析+建议        │
│ /tmp/supai-response.md  我      Claude  数据回应        │
│ /tmp/claude-decision.md  Claude  你      最终建议        │
│ harness.py 输出          我      你      测试结果         │
└─────────────────────────────────────────────────────────┘

规则:
  - 最多 2 轮握手，不无限循环
  - 每一轮有明确的完成标准
  - 你在最后一轮做决策
```

## 三、工具栈

| 层 | 工具 | 版本 | 用途 |
|------|------|------|------|
| **Agent 核心** | Hermes (星辰) | — | 编排 · 写代码 · 跑命令 |
| **深度推理** | Claude Code | 2.1.191 | 审查 · 分析 · 挑战假设 |
| **方法论** | Superpowers | 13 skills | 头脑风暴 · SDD · TDD |
| **测试** | Harness | 24/24 | 每次改动验证 |
| **代码** | engine.py | 500行 | 匹配引擎 |
| **前端** | index.html | 1文件 | Web App |
| **API** | server.py | 70行 | HTTP 接口 |
| **A2A** | a2a.py | — | Agent-to-Agent |
| **Bot** | QQ/微信/飞书 | Gateway | 用户入口 |
| **版本控制** | Git | — | 已初始化 |
| **文档** | Obsidian + Markdown | — | 知识库 + 规范 |
| **终端** | iTerm2 + JetBrains Mono | — | 开发环境 |

## 四、Claude Superpowers (13 Skills)

| Skill | 何时触发 | 我们怎么用 |
|-------|---------|-----------|
| brainstorming | 新想法/新需求 | 商业模式分析 ✅ 刚用过 |
| writing-plans | 明确需求后 | 功能开发计划 |
| subagent-driven-dev | 编码阶段 | 复杂功能拆分 |
| systematic-debugging | Bug修复 | 根因分析 |
| test-driven-development | 新功能 | TDD 红绿重构 |
| requesting-code-review | 改完后 | 代码审查 |
| verification-before-completion | 交付前 | 确认完成标准 |

## 五、当前缺失

| 缺失 | 重要性 | 阻塞什么 |
|------|:--:|------|
| **代理/科学上网** | 🔴 | GitHub push · 网络研究 |
| **GitHub 远程仓库** | 🟡 | 代码备份 · 版本历史 |
| **CI/CD** | 🟡 | 自动跑 Harness |
| **Web App 上线** | 🟡 | 客户自助下单 |
| **错误监控** | 🟢 | 生产环境问题感知 |

## 六、标准开发流

```
1. 你说: "做 X"
         │
2. 我判断复杂度
   简单  ──→ 直接写代码 → Harness
   复杂  ──→ 写 /tmp/supai-context.md → Claude 分析
                  │
3. Claude 输出分析到 /tmp/claude-analysis.md
                  │
4. 我读 → 修代码 → Harness
                  │
5. 你看 Harness 结果 → 通过 = 完成 / 失败 = 回到 4
```
