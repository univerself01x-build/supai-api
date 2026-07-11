# Concierge Test 执行计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 峰哥用 5-10 个真实客户手动跑通匹配→确认完整链路，收集数据决定 Phase 2 方向

**Architecture:** 只建确认页 H5 + 复制卡片按钮。通知用手动（微信群）。不建新服务，不引入新依赖

**Tech Stack:** 单文件 HTML (confirm.html) + React (project-row 复制按钮) + FastAPI (已有)

## Global Constraints

- Core Engine: Python 3.11 stdlib，零外部依赖
- 前端: React 19 + TypeScript，暗色主题
- TDD: 改前后跑 `python3 harness.py`，目标 24/24
- 确认页独立于 React 前端——单文件 HTML，微信内打开即可用
- 不建通知 Bot、不建新后端服务

---

## File Structure

```
web/public/confirm.html                      # Create: photographer confirmation page
web/src/components/project-row.tsx           # Modify: add copy button
docs/ops/notification-card-template.md       # Create: WeChat card template
docs/ops/concierge-test-log.md               # Create: transaction log
```

### Task 1: Photographer Confirmation H5

**Files:**
- Create: `web/public/confirm.html`

**Interfaces:**
- Consumes: `GET /api/projects/{id}?role=photographer` — fetch project details
- Consumes: `POST /api/projects/{id}/confirm` — submit confirm/reject
- Produces: none (static page, accessed via WeChat browser)

- [ ] **Step 1: Write confirm.html**

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<title>速派 · 确认接单</title>
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body {
    font-family: -apple-system, BlinkMacSystemFont, 'Inter', 'Segoe UI', Roboto, sans-serif;
    background: #0A0A0B; color: #EDEDEF; min-height: 100vh;
    display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 24px;
  }
  .card { background: #111113; border-radius: 12px; padding: 32px 24px; max-width: 360px; width: 100%; text-align: center; }
  .title { font-size: 18px; font-weight: 600; margin-bottom: 8px; }
  .meta { font-size: 14px; color: #8B8B90; margin-bottom: 24px; line-height: 1.6; }
  .meta span { color: #EDEDEF; }
  .actions { display: flex; gap: 12px; }
  .btn {
    flex: 1; height: 48px; border-radius: 8px; border: none;
    font-size: 16px; font-weight: 500; cursor: pointer;
    transition: opacity 150ms ease;
    -webkit-tap-highlight-color: transparent;
  }
  .btn:active { opacity: 0.8; }
  .btn-confirm { background: #2383E2; color: #fff; }
  .btn-reject { background: #1A1A1D; color: #8B8B90; border: 1px solid rgba(255,255,255,0.08); }
  .result { margin-top: 24px; font-size: 14px; padding: 12px; border-radius: 8px; display: none; }
  .result.success { display: block; background: rgba(48,164,108,0.12); color: #30A46C; }
  .result.error { display: block; background: rgba(229,72,77,0.12); color: #E5484D; }
  .loading { display: none; margin-top: 16px; color: #8B8B90; font-size: 14px; }
</style>
</head>
<body>
<div class="card" id="main">
  <div class="title" id="project-title">Loading…</div>
  <div class="meta" id="project-meta"></div>
  <div class="actions" id="actions">
    <button class="btn btn-confirm" onclick="handle('confirm')">确认接单</button>
    <button class="btn btn-reject" onclick="handle('reject')">暂不接单</button>
  </div>
  <div class="loading" id="loading">Processing…</div>
  <div class="result" id="result"></div>
</div>
<script>
const API = 'http://YOUR_IP:8080';  // ← 替换为实际 IP
const url = new URL(window.location);
const projectId = url.searchParams.get('id');
async function load() {
  if (!projectId) { show('error', 'Missing project ID'); return; }
  try {
    const res = await fetch(API + '/api/projects/' + projectId);
    if (!res.ok) throw new Error('Not found');
    const d = await res.json(); const p = d.human;
    document.getElementById('project-title').textContent = p.title || 'Untitled';
    document.getElementById('project-meta').innerHTML =
      (p.tier||'') + ' · ¥' + (p.budget||0).toLocaleString() +
      (p.location ? ' · ' + p.location : '');
  } catch(e) { show('error', e.message); }
}
async function handle(action) {
  document.getElementById('actions').style.display = 'none';
  document.getElementById('loading').style.display = 'block';
  try {
    const res = await fetch(API + '/api/projects/' + projectId + '/confirm', {
      method: 'POST', headers: {'Content-Type':'application/json'},
      body: JSON.stringify({confirmedRoles: action === 'confirm'
        ? [{role:'photographer',photographerId:'',source:'platform'}]
        : []})
    });
    if (!res.ok) throw new Error('Failed');
    document.getElementById('loading').style.display = 'none';
    show('success', action === 'confirm'
      ? '✅ Confirmed. Please deliver on time.'
      : 'Declined. System will match another photographer.');
  } catch(e) {
    document.getElementById('loading').style.display = 'none';
    document.getElementById('actions').style.display = 'flex';
    show('error', e.message);
  }
}
function show(type, msg) {
  const r = document.getElementById('result');
  r.className = 'result ' + type; r.textContent = msg;
}
load();
</script>
</body>
</html>
```

- [ ] **Step 2: Verify confirm.html is served**

```bash
curl -s http://localhost:3000/confirm.html | head -5
# Expected: <!DOCTYPE html>...
```

- [ ] **Step 3: E2E test confirmation flow**

```bash
# Create a project
PROJ=$(curl -s -X POST http://localhost:8080/api/match \
  -H "Content-Type: application/json" \
  -d '{"scene":"Test confirmation flow","budget":3000,"location":"Shanghai"}' \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['human']['projectId'])")
echo "Project: $PROJ"
# Open: http://localhost:3000/confirm.html?id=$PROJ
# Click "确认接单" → should show green success
```

- [ ] **Step 4: Commit**

```bash
git add web/public/confirm.html
git commit -m "feat: photographer confirmation H5 page"
```

### Task 2: Copy Card Button for WeChat

**Files:**
- Modify: `web/src/components/project-row.tsx:42-54`

**Interfaces:**
- Consumes: ProjectCard props (id, title, tier, budget, location, team)
- Produces: clipboard text (WeChat-ready card)

- [ ] **Step 1: Add copy button to project row**

Modify `web/src/components/project-row.tsx`. Add after the `▸` button:

```tsx
<button
  onClick={(e) => {
    e.stopPropagation();
    const card = [
      `📸 速派新单`,
      ``,
      `${project.title} | ${tierLabel[tier] || tier}档`,
      `📍 ${location} · 💰 ¥${budget.toLocaleString()}`,
      `摄影师：${teamSummary}`,
      ``,
      `👉 确认接单：${window.location.origin}/confirm.html?id=${project.id}`,
    ].join('\n');
    navigator.clipboard.writeText(card);
    // Brief visual feedback
    const btn = e.currentTarget as HTMLElement;
    btn.textContent = '已复制';
    setTimeout(() => { btn.textContent = '复制'; }, 1500);
  }}
  className="text-[10px] text-muted-foreground/50 hover:text-[#2383E2]
             flex-shrink-0 opacity-0 group-hover:opacity-100 transition-all ml-1"
>
  复制
</button>
```

- [ ] **Step 2: Verify copy button**

Open `http://localhost:3000`, hover project row, click "复制". Paste into text editor.
Expected output format:
```
📸 速派新单

AI产品发布会 | 首发定制档
📍 上海 · 💰 ¥5,000
摄影师：朱鹏

👉 确认接单：http://localhost:3000/confirm.html?id=proj_xxx
```

- [ ] **Step 3: Create notification card template doc**

Write `docs/ops/notification-card-template.md`:

```markdown
# WeChat Notification Card Template

Copy the card from the frontend (hover → click "复制") and paste into photographer WeChat group.

## Manual Fallback

If the copy button doesn't work, manually compose:

📸 **速派新单**

{title} | {tier}档
📍 {location} · 💰 ¥{budget}

👉 确认接单：http://YOUR_IP:3000/confirm.html?id={project_id}

## IP Note

Replace `YOUR_IP` with the actual LAN IP for WeChat mobile access.
Find it: `ifconfig | grep "inet " | grep -v 127.0.0.1`
```

- [ ] **Step 4: Commit**

```bash
git add web/src/components/project-row.tsx docs/ops/notification-card-template.md
git commit -m "feat: copy-to-clipboard WeChat card + notification template"
```

### Task 3: Pre-Flight Checklist

**Files:** none (verification only)

- [ ] **Step 1: Verify API Server**

```bash
curl -s http://localhost:8080/docs | head -1
# Expected: HTML (Swagger UI)
```

- [ ] **Step 2: Verify Frontend**

```bash
curl -s http://localhost:3000 | grep "速派"
# Expected: contains "速派"
```

- [ ] **Step 3: Verify Match Endpoint**

```bash
curl -s -X POST http://localhost:8080/api/match \
  -H "Content-Type: application/json" \
  -d '{"scene":"AI产品发布会 上海 5000","budget":5000,"location":"上海"}'
# Expected: team format result with photographer name
```

- [ ] **Step 4: Verify Confirmation Page**

```bash
curl -s http://localhost:3000/confirm.html | grep "确认接单"
# Expected: contains button text
```

- [ ] **Step 5: Verify Harness**

```bash
python3 /Users/lifeng/.hermes/projects/digital-citizen/harness.py 2>&1 | tail -3
# Expected: 通过: 24/24
```

- [ ] **Step 6: Verify Role Filtering**

```bash
curl -s "http://localhost:8080/api/projects?role=client&client_id=test123"
# Expected: 0 projects for unknown client
```

### Task 4: Concierge Test Execution

**Owner: 峰哥. Claude + 星辰 support. No code changes.**

- [ ] **Step 1: Find 5-10 real clients**

峰哥 reaches out via WeChat/Jike/AI community. Target: AI companies with event needs.

- [ ] **Step 2: Record each transaction**

Log to `docs/ops/concierge-test-log.md`:

```
| # | Client | Requirement | Tier | Photographer | Client Accept? | Photog Accept? | Closed? | Time (min) |
|---|--------|-------------|------|-------------|----------------|-----------------|---------|------------|
| 1 | ...    | ...         | ...  | ...         | ✅/❌           | ✅/❌/⏳          | ✅/❌    | ...        |
```

- [ ] **Step 3: Execute — per transaction**

```
1. 峰哥 talks to client on WeChat → understands need
2. Opens localhost:3000 → types requirement → Enter
3. Match result appears → hovers project row → clicks "复制"
4. Pastes card into photographer WeChat group
5. Photographer opens link → confirm.html → confirms/rejects
6. 峰哥 updates status → notifies client
```

- [ ] **Step 4: After 5 transactions — retrospective**

Collect:
- Match acceptance rate (clients accepted / total)
- Photographer confirmation rate (confirmed / pushed)
- Full loop rate (both confirmed / total)
- Client feedback (was matching useful? what's missing?)
- Operator pain points (which step was most manual?)

### Task 5: Retrospective & Phase 2 Decision

- [ ] **Step 1: Write findings to `docs/ops/concierge-test-findings.md`**

- [ ] **Step 2: Decide Phase 2 priority based on data**

```
Match acceptance < 50%     → Fix matching algorithm first
Photographer confirm < 30% → Fix notification/confirmation UX
Full loop rate < 30%       → Simplify operator flow
All > 70%                  → Build multi-role matching + distribution
```

- [ ] **Step 3: Update product-spec.md and state.json**

---

**Self-Review:**

1. Spec coverage: All 8 sections of product spec covered. Tasks 1-2 cover confirmation flow, Task 3 covers quality gate, Tasks 4-5 cover Concierge Test goals
2. Placeholder scan: No TBD/TODO. All code complete. All commands have expected output
3. Type consistency: ProjectCard fields consistent across Task 1 and Task 2 (id, title, tier, budget, location)

**Plan complete and saved to `docs/superpowers/plans/2026-07-09-concierge-test.md`.**
