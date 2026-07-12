# Wiki Schema

## Domain

AI Agent 研发工程师英语术语 Wiki。覆盖 AI 研发、工程、产品、设计、开发、营销语境中出现的英语术语。每条术语包含 IPA 音标、中文译名、定义、相关概念链接。

目标用户：峰哥（AI Agent R&D Engineer, non-native English speaker）。用途：阅读英文资料时快速查阅、积累领域词汇、Obsidian Graph View 可视化知识网络。

## Conventions

- File names: lowercase, hyphens, no spaces (e.g., `context-engineering.md`)
- Every wiki page starts with YAML frontmatter (see below)
- Use `[[wikilinks]]` to link between pages (minimum 2 outbound links per page)
- When updating a page, always bump the `updated` date
- Every new page must be added to `index.md` under the correct section
- Every action must be appended to `log.md`
- **IPA 音标 + 中文译名：** 每页正文第一段必须包含：`**中文译名** · English Term · /aɪ piː eɪ/`
- **Domain context：** 每页包含 "为什么这对 AI Agent 工程师重要" 的实际应用视角

## Frontmatter

```yaml
---
title: English Term
zh_title: 中文译名
ipa: /aɪ piː eɪ/
created: YYYY-MM-DD
updated: YYYY-MM-DD
type: concept | entity | comparison | query
tags: [from taxonomy below]
sources: [raw/articles/source-name.md]
confidence: high | medium | low
---
```

## Tag Taxonomy

| 类别 | Tags |
|------|------|
| 基础 | `neural-network`, `deep-learning`, `language-model` |
| 架构 | `transformer`, `attention`, `tokenizer`, `embedding` |
| Agent | `agent`, `multi-agent`, `tool-use`, `orchestration`, `agent-pattern` |
| 工程 | `rag`, `fine-tuning`, `evaluation`, `deployment`, `guardrails`, `prompt-engineering`, `context-engineering` |
| 范式 | `software-2.0`, `ai-native`, `sdd` (Spec-Driven Development) |
| 方法论 | `methodology`, `learning-path`, `anti-pattern` |
| 人物 | `person` |
| 组织 | `company`, `lab` |
| 模型/产品 | `model`, `product` |
| 课程/资源 | `course`, `book`, `blog` |

Rule: every tag on a page must appear in this taxonomy. If a new tag is needed, add it here first, then use it.

## Page Types

### Concept Pages (`concepts/`)
One page per concept or technique. Include:
- IPA + 中文译名（正文首段）
- Definition / what it is
- Why it matters for AI Agent engineers
- Related concepts ([[wikilinks]], min 2)
- Source references

### Entity Pages (`entities/`)
One page per person, organization, model, product, or course. Include:
- IPA + 中文译名（正文首段）
- Overview / what it is
- Key facts (dates, affiliations, notable works)
- Relationships to other entities/concepts ([[wikilinks]], min 2)
- Source references

### Comparison Pages (`comparisons/`)
Side-by-side analyses. Include:
- What is being compared and why
- Dimensions of comparison (table preferred)
- Practical implications for AI Agent engineers
- Verdict or synthesis

## Page Thresholds

- **Create a page** when a term appears 2+ times across sessions OR is central to understanding a key concept
- **Add to existing page** when new information supplements without requiring structural change
- **DON'T create a page** for one-off mentions or terms with no practical relevance to AI Agent engineering
- **Split a page** when it exceeds ~200 lines
- **Archive** when content is fully superseded

## Update Policy

1. New info supplements → add to existing page, bump `updated`
2. New info contradicts → note both positions with dates, mark `contested: true`
3. Confidence downgrade → single-source claims default to `confidence: medium`
4. Cross-reference check → verify wikilinks are bidirectional after any update

## Obsidian Integration

此 Wiki 是独立的 Obsidian vault（`~/ai-engineer-wiki/`）。用 Obsidian 打开此目录即可：
- `[[wikilinks]]` → 可点击链接
- Graph View → 知识网络可视化
- Dataview → 按 tag/type 查询
