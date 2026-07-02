# 速派 · 数字公民平台

## 你是这个项目的 AI 开发助手

### 先读
- `docs/PLAYBOOK.md` — 设计系统 + 工程规范 + Red Flags
- `docs/PRD-WEB.md` — 当前 Sprint 的 PRD
- `engine.py` — 核心引擎，薄壳厚核的"厚核"

### 关键规则
1. 所有逻辑在 `engine.py`，前端/API 是薄壳
2. 改代码前跑 `python3 harness.py`，改完再跑
3. 不引入外部依赖，标准库 + 单文件 HTML
4. 禁止框线字符 (┌─┐│└┘━══)
5. 始终暗色主题
6. 流式反馈——过程可见

### 技术栈
- Python 3.11 标准库
- 单文件 HTML（零 JS 框架）
- JSON over HTTP
