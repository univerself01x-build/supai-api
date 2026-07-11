"""
星辰 · 数字公民引擎 v0.4 — AI Native
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

三个核心原则：
1. 声明式 — 用户一句话讲完，Agent 自动提取，只问缺失
2. 双通道 — 同一个调用，人看卡片 / Agent 看 JSON
3. 可编排 — 标准函数签名，Codex/Claude 可直接调用
"""

from __future__ import annotations
import json, re, math
from pathlib import Path
from datetime import datetime
from typing import Optional

# ── Schema-First（v0.3 → v1.0 数据模型对齐 API 契约）──
from engine.schema import (
    SKILLS, SKILL_SYNONYMS,
    TIER_CONFIG, TIER_EVENTS,
    CitizenInput, validate_store,
)

_ROOT = Path(__file__).parent.parent  # engine/ → project root
DATA_DIR = _ROOT / "data"
STATE_DIR = _ROOT / "state"
LEDGER_DIR = _ROOT / "ledger"
CONTEXT_DIR = Path.home() / ".hermes/context"
INBOX_DIR = CONTEXT_DIR / "hermes" / "inbox"           # 发给星辰的消息
HERMES_OUTBOX_DIR = CONTEXT_DIR / "hermes" / "outbox" # 星辰发出的响应（预埋）
OUTBOX_DIR = CONTEXT_DIR / "claude" / "outbox"         # Claude 发出的响应
CLAUDE_INBOX_DIR = CONTEXT_DIR / "claude" / "inbox"    # 发给 Claude 的消息
CODEX_INBOX_DIR = CONTEXT_DIR / "codex" / "inbox"      # 发给 CodeX 的消息（预埋）
CODEX_OUTBOX_DIR = CONTEXT_DIR / "codex" / "outbox"    # CodeX 发出的响应（预埋）
ARCHIVE_DIR = CONTEXT_DIR / "hermes" / "archive"
STORE_PATH = DATA_DIR / "store.json"

DATA_DIR.mkdir(parents=True, exist_ok=True)
STATE_DIR.mkdir(parents=True, exist_ok=True)
LEDGER_DIR.mkdir(parents=True, exist_ok=True)
INBOX_DIR.mkdir(parents=True, exist_ok=True)
HERMES_OUTBOX_DIR.mkdir(parents=True, exist_ok=True)
OUTBOX_DIR.mkdir(parents=True, exist_ok=True)
CLAUDE_INBOX_DIR.mkdir(parents=True, exist_ok=True)
CODEX_INBOX_DIR.mkdir(parents=True, exist_ok=True)
CODEX_OUTBOX_DIR.mkdir(parents=True, exist_ok=True)
ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
SHARED_DIR = CONTEXT_DIR / "shared"
SHARED_DIR.mkdir(parents=True, exist_ok=True)

sep = "━━━━━━━━━━━━━━━━━━"

# ═══════════════════════════════════════════
# 1. 数据层
# ═══════════════════════════════════════════

def load_store(): 
    return json.loads(STORE_PATH.read_text()) if STORE_PATH.exists() else {"citizens": {}, "tasks": {}}

def save_store(d): 
    STORE_PATH.write_text(json.dumps(d, ensure_ascii=False, indent=2))

# ── 技能库、档位配置、Citizen Schema 已迁至 schema.py ──
# SKILLS, SKILL_SYNONYMS, TIER_CONFIG, TIER_EVENTS, CitizenInput, validate_store
# 均从 schema import

def extract_skills(msg):
    """从消息提取技能。直接匹配技能库 + 常见口语词映射"""
    found = [s for s in SKILLS if s.lower() in msg.lower()]
    # 常见口语词 → 技能映射（用户说"摄影"→匹配到摄影相关技能）
    spoken_map = {
        "摄影": ["产品拍摄", "活动摄影", "商业摄影"],
        "摄像": ["短视频", "纪录片"],
        "剪辑": ["视频剪辑"],
        "修图": ["数码后期"],
        "设计": ["UI设计", "平面设计"],
        "写代码": ["前端开发", "后端开发"],
    }
    for spoken, mapped in spoken_map.items():
        if spoken in msg.lower():
            found.extend([v for v in mapped if v not in found])
    return found

def extract_budget(msg):
    m = re.search(r'(\d+)\s*(元|块|k|w|万)?', msg)
    if m:
        n = int(m.group(1))
        u = m.group(2) or "元"
        if u in ('w','万'): n *= 10000
        elif u == 'k': n *= 1000
        return n
    return None

def extract_deadline(msg):
    patterns = [
        r'(\d+)月(\d+)日?前',
        r'(\d+)天(?:之)?内',
        r'周([一二三四五六日])前',
        r'(?:by|before)\s*(\d+)[/-](\d+)',
    ]
    for p in patterns:
        m = re.search(p, msg, re.IGNORECASE)
        if m: return m.group(0)
    return None

# ═══════════════════════════════════════════
# 2. 核心：信息抽取 + 缺失判断
# ═══════════════════════════════════════════

def extract_all(message: str) -> dict:
    """从用户一句话中提取所有可用信息"""
    return {
        "skills": extract_skills(message),
        "budget": extract_budget(message),
        "deadline": extract_deadline(message),
        "name": _extract_name(message),
    }

def _extract_name(msg):
    m = re.search(r'(?:我是|我叫|名字[：:]?\s*)([\u4e00-\u9fa5a-zA-Z0-9]{2,6})', msg)
    return m.group(1) if m else None

def missing_fields(info: dict, intent: str) -> list:
    """返回还缺什么信息"""
    required = {
        "register": ["name", "skills"],
        "post_task": ["skills", "budget", "deadline"],
        "match": ["skills"],
    }
    return [k for k in required.get(intent, []) if not info.get(k) or (isinstance(info[k], list) and len(info[k]) == 0)]

# ═══════════════════════════════════════════
# 3. 意图解析（AI Native — 一句话识别意图）
# ═══════════════════════════════════════════

def parse_intent(msg: str) -> str:
    m = msg.lower()
    if re.search(r"(帮助|help|功能|能做什么|菜单|指令)", m): return "help"
    if re.search(r"(找|求|需要|推荐|匹配).*(设计师|开发者|工程师|翻译|运营|编辑|文案|摄影|剪辑)", m): return "post_task"
    if re.search(r"(我(?:想|要)注册|注册.*人才|我是.*(?:设计师|开发者|工程师|自由职业|翻译|运营|摄影|剪辑|写手|全栈))", m): return "register_citizen"
    # 单独"注册"也识别
    if re.search(r"^注册$|^我要注册$|^我想注册$", m): return "register_citizen"
    if re.search(r"^(接|接单|接受|确认|ok|yes|可以|好的|行|好|要得|拿下)\b", m): return "accept_task"
    if re.search(r"^(过|跳过|拒绝|不接|no|算了|不要|pass)\b", m): return "decline_task"
    if re.search(r"(状态|进度|我的任务|进行中)", m): return "check_status"
    if re.search(r"(你好|hi|hello|在吗|嗨|hey)", m): return "greeting"
    # Claude 协作通道 — req_ / claude_ 前缀 或 审查/分析/outbox 关键词
    if re.search(r"\b(req_|claude_)\w*|\[\[outbox\]\]|审查.*(完成|已|结果)|分析.*(完毕|好|完)", m): return "claude_response"
    return "unknown"

# ── TIER_EVENTS, TIER_CONFIG 已迁至 engine/schema.py ──

def detect_tier(message: str) -> str:
    """根据事件类型+预算自动分档"""
    m = message.lower()
    for tier in ["enterprise","premier","express","pool"]:
        for kw in TIER_EVENTS[tier]:
            if kw in m:
                return tier
    # 按预算分
    budget = extract_budget(message)
    if budget and budget >= 5000: return "premier"
    if budget and budget >= 2000: return "express"
    return "pool"

def filter_by_tier(citizens: dict, tier: str) -> dict:
    """按档位过滤摄影师"""
    cfg = TIER_CONFIG[tier]
    return {
        cid: c for cid, c in citizens.items()
        if c.get("rating",0) >= cfg["min_rating"]
        and c.get("completed_tasks",0) >= cfg["min_tasks"]
        and c.get("available", True)
    }

def get_commission(tier: str) -> float:
    return TIER_CONFIG[tier]["commission"]

def get_tier_name(tier: str) -> str:
    return TIER_CONFIG[tier]["name"]

def _find_pending_tasks_for_citizen(store: dict, citizen_id: str) -> list:
    """查找该公民被匹配但未确认的任务"""
    pending = []
    for tid, t in store.get("tasks", {}).items():
        if citizen_id in t.get("matched_citizens", []):
            if t.get("status") in ("open", "matched"):
                pending.append((tid, t))
    return pending

def accept_task(platform: str, user_id: str, citizen_id: str) -> dict:
    """公民确认接单 → 更新任务状态 + 返回跨平台通知指令"""
    s = load_store()
    pending = _find_pending_tasks_for_citizen(s, citizen_id)
    
    if not pending:
        return {
            "human": "你当前没有待确认的任务",
            "agent": {"status": "no_pending", "action": "accept_task"}
        }
    
    # 接受第一个待确认任务
    tid, task = pending[0]
    task["status"] = "accepted"
    task["accepted_by"] = citizen_id
    task["accepted_at"] = datetime.now().isoformat()
    
    # 更新公民统计数据
    if citizen_id in s["citizens"]:
        s["citizens"][citizen_id]["completed_tasks"] = \
            s["citizens"][citizen_id].get("completed_tasks", 0) + 1
    
    save_store(s)
    
    # 构建通知指令
    client_platform = task.get("client_platform", "")
    client_id = task.get("client_id", "")
    title = task.get("title", "未命名任务")
    
    human = f"✅ 已接单: {title}\\n\\n客户会收到通知，请按时交付。"
    agent = {
        "status": "accepted",
        "action": "accept_task",
        "task_id": tid,
        "task_title": title,
        "notify_client": {
            "platform": client_platform,
            "user_id": client_id,
            "message": f"🎉 {title} — 已确认接单！\\n\\n摄影师已就位，请等待交付。"
        }
    }
    
    return {"human": human, "agent": agent}

def decline_task(platform: str, user_id: str, citizen_id: str) -> dict:
    """公民拒单"""
    s = load_store()
    pending = _find_pending_tasks_for_citizen(s, citizen_id)
    
    if not pending:
        return {
            "human": "你当前没有待确认的任务",
            "agent": {"status": "no_pending", "action": "decline_task"}
        }
    
    tid, task = pending[0]
    task["status"] = "declined"
    task["declined_by"] = citizen_id
    task["declined_at"] = datetime.now().isoformat()
    save_store(s)
    
    return {
        "human": f"已跳过: {task.get('title', '未命名任务')}",
        "agent": {"status": "declined", "action": "decline_task", "task_id": tid}
    }

def _find_citizen_by_platform_id(store: dict, platform: str, user_id: str) -> str | None:
    """通过平台ID查找公民ID"""
    for cid, c in store.get("citizens", {}).items():
        if c.get("platform") == platform and c.get("platform_id") == user_id:
            return cid
    return None

def register_citizen(name, skills, platform, pid,
                     location="上海", languages=None, tier="pool",
                     rating=5.0, completed_tasks=0, price_range=None,
                     equipment=None, available=True) -> dict:
    """注册服务者 — Schema-First 校验。数据模型对齐 API 契约"""
    import re as _re

    # ── 强制 skills 存为数组 ──
    if isinstance(skills, str):
        skills = [s.strip() for s in skills.split(",") if s.strip()]

    # ── 自动推断 tier（如果未指定或默认值）──
    if tier == "pool":
        if rating >= 4.8 and completed_tasks >= 30:
            tier = "enterprise"
        elif rating >= 4.5 and completed_tasks >= 15:
            tier = "premier"
        elif rating >= 4.0 and completed_tasks >= 5:
            tier = "express"

    # ── Schema 校验 ──
    if price_range is None:
        price_range = [800, 3000]
    if languages is None:
        languages = ["中文"]
    if equipment is None:
        equipment = []

    citizen_input = CitizenInput(
        name=name, platform_id=pid, skills=skills,
        location=location, languages=languages, tier=tier,
        rating=rating, completed_tasks=completed_tasks,
        price_range=price_range, equipment=equipment,
        available=available, platform=platform,
    )

    s = load_store()
    # ── platform_id 唯一性检查 ──
    for existing in s["citizens"].values():
        if existing.get("platform_id") == pid:
            return {"error": "duplicate_platform_id", "detail": f"{pid} already registered"}

    cid = f"citizen_{len(s['citizens'])+1:03d}"
    c = citizen_input.to_dict()
    c["id"] = cid
    c["registered_at"] = datetime.now().isoformat()[:10]

    s["citizens"][cid] = c
    save_store(s)
    return c

def match_task(skills: list, tier: str = "pool", location: str = "") -> list:
    s = load_store()
    # 按档位过滤
    eligible = filter_by_tier(s.get("citizens", {}), tier)
    r = [sk.lower().strip() for sk in skills]
    # 展开同义词：用户搜"摄影"也要能匹配到 citizen 的"产品拍摄"
    expanded = list(r)
    for sk in r:
        expanded.extend([s.lower() for s in SKILL_SYNONYMS.get(sk, [])])
    scored = []
    for cid, c in eligible.items():
        if not c.get("available", True):
            continue
        cs = [x.lower() for x in c.get("skills", [])]
        # —— 技能匹配得分 ——
        skill_score = 0
        for sk in expanded:
            for x in cs:
                if sk in x or x in sk:
                    skill_score += 50
                elif any(w in x for w in sk.split()):
                    skill_score += 25
        # 零技能重叠 → 硬过滤，不参与排名
        if skill_score == 0:
            continue
        # —— 基线分（仅在技能匹配存在时计算）——
        baseline = 0
        baseline += (10 if "中文" in c.get("languages", []) else 0)
        baseline += c.get("rating", 0) * 3
        baseline += min(c.get("completed_tasks", 0), 20)
        # 同城加成（地域匹配）
        if location and c.get("location", "") == location:
            baseline += 15
        score = skill_score + baseline
        scored.append((cid, c, score))
    scored.sort(key=lambda x: x[2], reverse=True)
    return scored[:5]

# ═══════════════════════════════════════════
# 4b. 子代理审查 — 匹配质量双维度判定
# ═══════════════════════════════════════════

def review_match(matched: list, required_skills: list) -> dict:
    """审查匹配结果。返回 {verdict, spec_pass, quality_pass, issues, score}"""
    if not matched:
        return {"verdict": "reject", "spec_pass": False, "quality_pass": False,
                "issues": ["no_candidates"], "score": 0}

    issues = []
    top_score = matched[0][2]
    top_skills = [s.lower() for s in matched[0][1].get("skills", [])]
    required_lower = [s.lower() for s in required_skills]

    # Spec 审查：是否满足技能要求
    skill_hit = any(
        any(rs in cs or cs in rs for cs in top_skills)
        for rs in required_lower
    )
    if not skill_hit:
        issues.append("top_match_skill_mismatch")

    # Quality 审查：分数和分布
    if top_score < 30:
        issues.append("score_below_threshold_30")

    if len(matched) > 1 and (matched[0][2] - matched[1][2]) < 10:
        issues.append("tiebreaker_needed_top2_too_close")

    if len(matched) == 1 and top_score < 50:
        issues.append("single_candidate_low_confidence")

    spec_pass = "top_match_skill_mismatch" not in issues
    quality_pass = all(
        i not in issues for i in
        ["score_below_threshold_30", "tiebreaker_needed_top2_too_close",
         "single_candidate_low_confidence"]
    )

    verdict = "deliver" if spec_pass and quality_pass else "review"
    return {
        "verdict": verdict,
        "spec_pass": spec_pass,
        "quality_pass": quality_pass,
        "issues": issues,
        "top_score": top_score,
    }


def deliver_if_approved(review: dict) -> bool:
    """硬性门槛：审查未通过禁止交付"""
    return review.get("verdict") == "deliver"


def escalate_to_claude(review: dict, matches: list, required_skills: list, tier: str = "pool") -> dict:
    """审查不通过时，自动写求助请求到共享 inbox。

    Claude/峰哥 轮询 context/hermes/inbox/ 发现请求后，
    写入 context/claude/outbox/ 响应。
    """
    req_id = f"req_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    # 提取匹配摘要（最多3条，脱敏）
    match_summary = []
    for i, (cid, c, score) in enumerate(matches[:3]):
        match_summary.append({
            "rank": i + 1,
            "name": c.get("name", "?"),
            "id": cid,
            "score": score,
            "skills": c.get("skills", []) if isinstance(c.get("skills"), list) else [c.get("skills", "")]
        })

    # 问题 → 自然语言
    issue_map = {
        "no_candidates": "零匹配结果，是否需要扩大搜索或降低档位？",
        "top_match_skill_mismatch": f"第一名技能与 {required_skills} 不匹配，需求描述是否准确？",
        "score_below_threshold_30": f"最高分 {review.get('top_score', 0)} 低于阈值 30，匹配质量存疑。",
        "tiebreaker_needed_top2_too_close": "前两名分数过于接近，需要人工判断。",
        "single_candidate_low_confidence": "仅一个候选人且分数偏低，是否接受？",
    }
    questions = [issue_map.get(i, i) for i in review.get("issues", [])]

    request = {
        "id": req_id,
        "timestamp": datetime.now().isoformat(),
        "from": "hermes",
        "to": "claude",
        "task": "review",
        "target": f"匹配结果 — {', '.join(required_skills)} [{tier}]",
        "context": {
            "tier": tier,
            "tier_name": get_tier_name(tier),
            "top_score": review.get("top_score", 0),
            "issues": review.get("issues", []),
            "verdict": review.get("verdict"),
            "match_count": len(matches),
            "top_matches": match_summary
        },
        "question": " · ".join(questions),
        "urgency": "high" if review.get("verdict") == "reject" else "normal",
        "status": "pending"
    }

    inbox_file = CLAUDE_INBOX_DIR / f"{req_id}.json"
    inbox_file.write_text(json.dumps(request, ensure_ascii=False, indent=2))
    return request

def dispatch_to_codex(task_spec: str, task_type: str = "generate", deadline: Optional[str] = None) -> dict:
    """向 CodeX 分发任务 — 写入 CFP 后直接调用 codex exec 执行。

    流程: 写 CFP → codex exec → 结果写入 outbox → 返回

    Args:
        task_spec: 任务描述（自然语言或结构化 spec）
        task_type: generate|code|test|render|batch
        deadline: ISO 8601 截止时间（可选）

    Returns:
        dict with task_id, status, output, outbox file path
    """
    import subprocess, shutil

    task_id = f"task_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    timestamp = datetime.now().isoformat()

    # ── 1. 写 CFP 到 codex/inbox/（审计追踪）──
    msg = {
        "id": task_id,
        "timestamp": timestamp,
        "from": "hermes",
        "to": "codex",
        "type": "cfp",
        "intent": "task",
        "payload": {
            "task_id": task_id,
            "spec": task_spec,
            "task_type": task_type,
            "deadline": deadline,
            "state": "executing",
            "assigned_to": None,
            "bidders": [],
        },
        "thinking": f"星辰分发 {task_type} 任务给 CodeX，直接执行",
        "status": "executing",
    }

    inbox_file = CODEX_INBOX_DIR / f"{task_id}.json"
    inbox_file.write_text(json.dumps(msg, ensure_ascii=False, indent=2))

    # ── 2. 直接调 codex exec ──
    codex_bin = shutil.which("codex") or Path.home() / ".npm-global/bin/codex"
    if not codex_bin or not Path(str(codex_bin)).exists():
        return {
            "task_id": task_id,
            "status": "error",
            "error": "codex binary not found",
        }

    # 动态沙箱：generate/batch/code → danger-full-access，review/test → read-only
    sandbox_mode = "read-only" if task_type in ("review", "test") else "danger-full-access"

    try:
        result = subprocess.run(
            [str(codex_bin), "exec", "--skip-git-repo-check", "-s", sandbox_mode, task_spec],
            capture_output=True, text=True,
            timeout=300,  # 5分钟超时
            cwd=str(CONTEXT_DIR.parent),
        )
        output = result.stdout.strip()
        stderr = result.stderr.strip()
        success = result.returncode == 0
    except subprocess.TimeoutExpired:
        output = ""
        stderr = "timeout after 300s"
        success = False
    except Exception as e:
        output = ""
        stderr = str(e)
        success = False

    # ── 3. 结果写入 codex/outbox/ ──
    resp = {
        "id": f"resp_{task_id}",
        "timestamp": datetime.now().isoformat(),
        "from": "codex",
        "to": "hermes",
        "ref": task_id,
        "type": "inform",
        "intent": "task",
        "payload": {
            "task_id": task_id,
            "state": "completed" if success else "failed",
            "output": output[:5000],
            "stderr": stderr[:1000],
            "returncode": 0 if success else 1,
        },
        "thinking": f"CodeX exec 完成: {'success' if success else 'failed'}",
        "status": "done",
    }

    outbox_file = CODEX_OUTBOX_DIR / f"resp_{task_id}.json"
    outbox_file.write_text(json.dumps(resp, ensure_ascii=False, indent=2))

    # ── 4. 更新 inbox CFP 状态 ──
    msg["status"] = "completed" if success else "failed"
    msg["payload"]["state"] = "completed" if success else "failed"
    inbox_file.write_text(json.dumps(msg, ensure_ascii=False, indent=2))

    return {
        "task_id": task_id,
        "status": "completed" if success else "failed",
        "output": output[:500],
        "outbox": str(outbox_file),
        "error": stderr[:500] if not success else None,
    }

def dispatch_to_claude(task_spec: str) -> dict:
    """向 Claude 同步分发任务 — 对标 dispatch_to_codex()。
    
    流程: 写 request → claude -p headless 执行 → 结果写入 outbox → 返回
    
    Args:
        task_spec: 任务描述或审查请求
    
    Returns:
        dict with task_id, status, output, outbox file path
    """
    import subprocess, shutil
    
    task_id = f"review_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    timestamp = datetime.now().isoformat()
    
    # ── 1. 写 request 到 claude/inbox/（审计追踪）──
    msg = {
        "id": task_id,
        "timestamp": timestamp,
        "from": "hermes",
        "to": "claude",
        "type": "request",
        "intent": "review",
        "payload": {"task_id": task_id, "spec": task_spec, "state": "executing"},
        "thinking": f"星辰分发审查任务给 Claude: {task_spec[:80]}",
        "status": "executing",
    }
    inbox_file = CLAUDE_INBOX_DIR / f"{task_id}.json"
    inbox_file.write_text(json.dumps(msg, ensure_ascii=False, indent=2))
    
    # ── 2. 直接调 claude -p headless ──
    claude_bin = shutil.which("claude")
    if not claude_bin:
        return {"task_id": task_id, "status": "error", "error": "claude binary not found"}
    
    try:
        result = subprocess.run(
            [claude_bin, "-p", "--output-format", "json", task_spec],
            capture_output=True, text=True, timeout=300,
            cwd=str(CONTEXT_DIR.parent),
        )
        output = result.stdout.strip()
        stderr = result.stderr.strip()
        success = result.returncode == 0
    except subprocess.TimeoutExpired:
        output = ""
        stderr = "timeout after 300s"
        success = False
    except Exception as e:
        output = ""
        stderr = str(e)
        success = False
    
    # ── 3. 结果写入 claude/outbox/ ──
    resp = {
        "id": f"resp_{task_id}",
        "timestamp": datetime.now().isoformat(),
        "from": "claude", "to": "hermes", "ref": task_id,
        "type": "inform", "intent": "review",
        "payload": {"task_id": task_id, "state": "completed" if success else "failed",
                     "output": output[:5000], "stderr": stderr[:1000], "returncode": 0 if success else 1},
        "thinking": f"Claude headless 完成: {'success' if success else 'failed'}",
        "status": "done",
    }
    outbox_file = OUTBOX_DIR / f"resp_{task_id}.json"
    outbox_file.write_text(json.dumps(resp, ensure_ascii=False, indent=2))
    
    # ── 4. 更新 inbox 状态 ──
    msg["status"] = "completed" if success else "failed"
    msg["payload"]["state"] = "completed" if success else "failed"
    inbox_file.write_text(json.dumps(msg, ensure_ascii=False, indent=2))
    
    return {
        "task_id": task_id,
        "status": "completed" if success else "failed",
        "output": output[:500],
        "outbox": str(outbox_file),
        "error": stderr[:500] if not success else None,
    }

def poll_outbox() -> list:
    """主动扫描 outbox，匹配 inbox 请求 → 处理 → 归档。
    
    按 v0.2 协议:
    - 扫描 claude/outbox/resp_*.json（Claude 的响应）
    - 扫描 codex/outbox/resp_*.json（CodeX 的响应，预埋）
    - 匹配对应 inbox 请求 → 归档 → 标记 acknowledged
    
    每次 handle_message 入口调用，保持轻量。
    """
    processed = []
    # 扫描所有已知 agent 的 outbox + hermes/inbox/（v0.3 直接消息）
    scan_targets = [
        (OUTBOX_DIR, CLAUDE_INBOX_DIR, "resp_*.json"),
        (CODEX_OUTBOX_DIR, CODEX_INBOX_DIR, "resp_*.json"),
        (INBOX_DIR, CLAUDE_INBOX_DIR, "*claude_*.json"),  # v0.3: Claude 直接写 hermes/inbox/
    ]
    for outbox_dir, inbox_dir, glob_pattern in scan_targets:
        for outbox_file in sorted(outbox_dir.glob(glob_pattern)):
            try:
                resp = json.loads(outbox_file.read_text())
                if resp.get("status") == "acknowledged":
                    continue  # 已处理，跳过
                
                req_id = resp.get("in_response_to", "")
                inbox_file = inbox_dir / f"{req_id}.json"
                
                # 归档原始请求
                if inbox_file.exists():
                    inbox_file.rename(ARCHIVE_DIR / f"{req_id}.json")
                
                # 标记已确认
                resp["status"] = "acknowledged"
                outbox_file.write_text(json.dumps(resp, ensure_ascii=False, indent=2))
                
                processed.append({
                    "req_id": req_id,
                    "verdict": resp.get("payload", {}).get("verdict", "?"),
                    "summary": resp.get("thinking", "")[:100],
                })
            except Exception:
                pass
    
    # ── 持久化：关键发现写入共享记忆队列 ──
    if processed:
        findings_file = SHARED_DIR / "claude-findings.json"
        existing = []
        if findings_file.exists():
            try:
                existing = json.loads(findings_file.read_text())
            except Exception:
                pass
        
        for p in processed:
            entry = {
                "timestamp": datetime.now().isoformat()[:19],
                "req_id": p["req_id"],
                "verdict": p["verdict"],
                "summary": p["summary"],
            }
            # 去重
            if not any(e.get("req_id") == p["req_id"] for e in existing):
                existing.append(entry)
        
        findings_file.write_text(json.dumps(existing, ensure_ascii=False, indent=2))
    
    return processed

# ═══════════════════════════════════════════
# 5. 输出 — 对话式美学
#    每一条消息都是一句话，不是一页纸
# ═══════════════════════════════════════════

def card_welcome():
    return """我是数字公民网络的匹配助手

帮你找到合适的自由职业者，或者帮你接到合适的项目。

直接告诉我就行——_找UI设计师_ 或者 _我是开发者_"""

def card_register_need(missing: list):
    qs = {"name": "怎么称呼你", "skills": "你擅长什么技能"}
    items = "  ".join(f"·{qs[k]}" for k in missing if k in qs)
    return f"还差一点点 {items}"

def card_register_done(c: dict) -> dict:
    skills = " · ".join(c.get("skills", []))
    human = f"好的，记住了。\n\n{c.get('name', '')}\n{skills}\n\n有新项目我会通知你。"
    return {"human": human, "agent": {"status": "ok", "action": "registered", "citizen": c}}

def card_post_need(missing: list):
    qs = {"skills": "需要什么技能", "budget": "预算多少", "deadline": "什么时候要"}
    items = "  ".join(f"·{qs[k]}" for k in missing if k in qs)
    return f"还差一点信息 {items}"

def card_match(matched: list) -> dict:
    if not matched:
        return {
            "human": "暂时没有完全匹配的人选。需求已保存，有合适的人我会通知你。",
            "agent": {"status": "ok", "matches": [], "suggestion": "try_broader"},
        }
    lines = []
    for i, (_, c, _) in enumerate(matched):
        name = c.get("name", "?")
        sk = " · ".join(c.get("skills", ["?"])[:3])
        rt = c.get("rated", c.get("rating", 0))
        ct = c.get("completed_tasks", 0)
        rate = c.get("rate", "协商")
        stars = "★" * min(int(rt), 5) + "☆" * (5 - min(int(rt), 5))
        lines.append(f"{i+1}. {name}\n   {sk}\n   {stars}  {ct}单  {rate}")
    human = f"找到 {len(matched)} 位\n\n" + "\n\n".join(lines) + "\n\n回复数字查看详情"
    agent = {
        "status": "ok",
        "matches": [
            {"rank": i + 1, "name": c["name"], "id": cid, "score": sc, "skills": c["skills"]}
            for i, (cid, c, sc) in enumerate(matched)
        ],
    }
    return {"human": human, "agent": agent}

def card_help():
    return """我能帮你三件事

找人才 — 说说你需要什么样的自由职业者
接任务 — 告诉我你的技能，有项目推给你
查进度 — 随时了解进行中的任务

直接说就行"""

def card_unknown():
    return """你可以这样跟我说

_找UI设计师 Figma 预算3000_
_我是开发者 Python React_
_状态_ — 看看进行中的任务"""

def card_claude_response(req_id: str, response: dict):
    """星辰确认收到 Claude 的审查响应"""
    analysis = response.get("payload", {})
    root = analysis.get("root_cause", "?")
    rec = analysis.get("recommendation", "?")
    thinking = response.get("thinking", "")
    human = f"📬 收到 Claude 响应\n\n请求: {req_id}\n原因: {root}\n建议: {rec}"
    if thinking:
        human += f"\n\n💭 Claude: {thinking[:200]}"
    return {
        "human": human,
        "agent": {
            "status": "acknowledged",
            "request_id": req_id,
            "claude_decision": response.get("payload", {}).get("verdict"),
            "action": "archive_request"
        }
    }


def _handle_claude_response(msg: str) -> dict:
    """处理 Claude 的协作响应。
    从消息中提取 request ID → 读 outbox → 确认 → 归档原始请求。
    """
    import re as _re

    # 从消息中提取 ID
    m = _re.search(r'(?:req_|claude_)\w+', msg)
    req_id = m.group(0) if m else None

    # 匹配 outbox 中的响应
    response = None
    if req_id:
        # 精确匹配 resp_<req_id>.json（按 v0.2 命名规范）
        resp_file = OUTBOX_DIR / f"resp_{req_id}.json"
        if resp_file.exists():
            response = json.loads(resp_file.read_text())
    if not response:
        # 取最新
        files = sorted(OUTBOX_DIR.glob("*.json"), key=lambda f: f.stat().st_mtime, reverse=True)
        if files:
            response = json.loads(files[0].read_text())
            req_id = response.get("in_response_to") or response.get("id")

    if not response:
        return {
            "human": "没找到 Claude 的响应文件。请确认 outbox/ 里有对应的回复。",
            "agent": {"status": "no_response_found"}
        }

    # 归档原始请求（请求在 claude/inbox/，由星辰发出）
    inbox_file = CLAUDE_INBOX_DIR / f"{req_id}.json"
    if inbox_file.exists():
        inbox_file.rename(ARCHIVE_DIR / f"{req_id}.json")

    # 标记 outbox 响应为已确认
    outbox_file = OUTBOX_DIR / f"{response.get('id', req_id)}.json"
    if not outbox_file.exists():
        for f in OUTBOX_DIR.glob("*.json"):
            data = json.loads(f.read_text())
            if data.get("id") == response.get("id"):
                outbox_file = f
                break

    return card_claude_response(req_id, response)

def card_progress(step: str, detail: str = ""):
    if not detail:
        return step
    return f"{step}\n{detail}"

# ═══════════════════════════════════════════
# 6. 会话状态
# ═══════════════════════════════════════════

def _sp(platform, uid):
    return STATE_DIR / f"{platform}_{uid.replace('/','_').replace('@','_')}.json"

def get_state(platform, uid) -> dict:
    p = _sp(platform, uid)
    return json.loads(p.read_text()) if p.exists() else {"flow":None,"collect":{}}

def set_state(platform, uid, flow, **kw):
    s = get_state(platform, uid)
    s["flow"] = flow
    s["collect"].update(kw)
    _sp(platform, uid).write_text(json.dumps(s, ensure_ascii=False))

def clear_state(platform, uid):
    p = _sp(platform, uid)
    if p.exists(): p.unlink()

# ═══════════════════════════════════════════
# 7. 主调度 — 一个函数，双通道输出
# ═══════════════════════════════════════════

def handle_message(platform: str, user_id: str, message: str) -> dict:
    """
    核心入口。人说话 → 这个函数 → 给回复。
    A2A：Agent 调用同样的函数，取 .agent 字段。
    """
    msg = message.strip()
    
    # ── Agent 通道：主动扫描 outbox 待办 ──
    poll_outbox()
    
    # ── 继续未完成的流程 ──
    state = get_state(platform, user_id)
    flow = state.get("flow")
    coll = state.get("collect", {})
    
    if flow == "register":
        return _continue_register(platform, user_id, msg, coll)
    if flow == "post_task":
        return _continue_post(platform, user_id, msg, coll)
    
    # ── 新意图 ──
    intent = parse_intent(msg)
    info = extract_all(msg)
    missing = missing_fields(info, intent)
    
    if intent == "greeting":
        return {"human": card_welcome(), "agent": {"status":"ok","action":"welcome"}}

    if intent == "claude_response":
        return _handle_claude_response(msg)

    if intent == "help":
        return {"human": card_help(), "agent": {"status":"ok","action":"help"}}
    
    if intent == "register_citizen":
        if not missing:
            name = info.get("name") or coll.get("name") or user_id[:8]
            skills = info.get("skills", [])
            c = register_citizen(name, skills, platform, user_id)
            clear_state(platform, user_id)
            return card_register_done(c)
        set_state(platform, user_id, "register", name=info.get("name"), skills=info.get("skills",[]))
        return {"human": card_register_need(missing), "agent": {"status":"need_info","missing":missing}}
    
    if intent == "post_task":
        if not missing:
            tier = detect_tier(msg)
            matches = match_task(info["skills"], tier)
            review = review_match(matches, info["skills"])
            r = card_match(matches)
            # 显示档位+佣金
            tier_name = get_tier_name(tier)
            comm = get_commission(tier)
            r["human"] = f"[{tier_name}] · 佣金{int(comm*100)}%\n\n" + r["human"]
            if not deliver_if_approved(review):
                r["human"] += f"\n\n⚠️ 审查未通过：{' · '.join(review['issues'])}"
                r["agent"]["escalation"] = escalate_to_claude(review, matches, info["skills"], tier)
            r["agent"]["review"] = review
            r["agent"]["tier"] = tier
            r["agent"]["commission"] = comm
            # 附加通知指令给 Agent
            notif = []
            for _, c, _ in matches:
                if c.get("platform_id"):
                    notif.append({
                        "name": c["name"],
                        "platform": c.get("platform", "feishu"),
                        "user_id": c["platform_id"],
                        "skills": c.get("skills", []),
                    })
            r["agent"]["extracted"] = info
            r["agent"]["notify_candidates"] = notif
            r["agent"]["instructions"] = "Send notification to each candidate using the platform's send tool. Message: '🔔 新任务匹配: {title} | 预算:{budget} | 截止:{deadline} 回复\"接\"接收，回复\"过\"跳过'"
            return r
        set_state(platform, user_id, "post_task",
                  skills=info.get("skills",[]), budget=info.get("budget"),
                  deadline=info.get("deadline"))
        return {"human": card_post_need(missing), "agent": {"status":"need_info","missing":missing}}
    
    if intent == "accept_task":
        s = load_store()
        cid = _find_citizen_by_platform_id(s, platform, user_id)
        if not cid:
            return {"human": "你还未注册。说「我是摄影师」来注册。", "agent": {"status": "not_registered"}}
        return accept_task(platform, user_id, cid)
    
    if intent == "decline_task":
        s = load_store()
        cid = _find_citizen_by_platform_id(s, platform, user_id)
        if not cid:
            return {"human": "你还未注册。说「我是摄影师」来注册。", "agent": {"status": "not_registered"}}
        return decline_task(platform, user_id, cid)
    
    return {"human": card_unknown(), "agent": {"status":"unknown"}}

def _continue_register(platform, uid, msg, coll):
    info = extract_all(msg)
    name = info.get("name") or coll.get("name") or msg
    skills = info.get("skills") or extract_skills(msg)
    missing = missing_fields({"name":name,"skills":skills}, "register")
    if not missing:
        c = register_citizen(name, skills, platform, uid)
        clear_state(platform, uid)
        return card_register_done(c)
    set_state(platform, uid, "register", name=name, skills=skills)
    return {"human": card_register_need(missing), "agent": {"status":"need_info","missing":missing}}

def _continue_post(platform, uid, msg, coll):
    info = extract_all(msg)
    skills = info.get("skills") or coll.get("skills",[])
    budget = info.get("budget") or coll.get("budget")
    deadline = info.get("deadline") or coll.get("deadline")
    missing = missing_fields({"skills":skills,"budget":budget,"deadline":deadline}, "post_task")
    if not missing:
        tier = detect_tier(msg)
        matches = match_task(skills, tier)
        review = review_match(matches, skills)
        r = card_match(matches)
        tier_name = get_tier_name(tier)
        comm = get_commission(tier)
        r["human"] = f"[{tier_name}] · 佣金{int(comm*100)}%\n\n" + r["human"]
        if not deliver_if_approved(review):
            r["human"] += f"\n\n⚠️ 审查未通过：{' · '.join(review['issues'])}"
            r["agent"]["escalation"] = escalate_to_claude(review, matches, skills, tier)
        r["agent"]["review"] = review
        r["agent"]["tier"] = tier
        r["agent"]["commission"] = comm
        clear_state(platform, uid)
        return r
    set_state(platform, uid, "post_task", skills=skills, budget=budget, deadline=deadline)
    return {"human": card_post_need(missing), "agent": {"status":"need_info","missing":missing}}
