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

DATA_DIR = Path("/Users/lifeng/.hermes/digital-citizen/data")
STATE_DIR = Path("/Users/lifeng/.hermes/digital-citizen/state")
LEDGER_DIR = Path("/Users/lifeng/.hermes/digital-citizen/ledger")
STORE_PATH = DATA_DIR / "store.json"

DATA_DIR.mkdir(parents=True, exist_ok=True)
STATE_DIR.mkdir(parents=True, exist_ok=True)
LEDGER_DIR.mkdir(parents=True, exist_ok=True)

sep = "━━━━━━━━━━━━━━━━━━"

# ═══════════════════════════════════════════
# 1. 数据层
# ═══════════════════════════════════════════

def load_store(): 
    return json.loads(STORE_PATH.read_text()) if STORE_PATH.exists() else {"citizens": {}, "tasks": {}}

def save_store(d): 
    STORE_PATH.write_text(json.dumps(d, ensure_ascii=False, indent=2))

SKILLS = ["UI设计","UX设计","平面设计","品牌设计","网页设计",
          "前端开发","后端开发","全栈开发","移动开发","小程序开发",
          "Python","JavaScript","TypeScript","React","Vue","Node.js",
          "Figma","Sketch","Photoshop","Illustrator","After Effects",
          "文案写作","翻译","中英翻译","英中翻译",
          "数据分析","运营","社交媒体运营","SEO","SEM",
          "视频剪辑","音频处理","动画制作","摄影",
          "产品经理","项目管理","法律咨询","财务","税务"]

def extract_skills(msg): 
    return [s for s in SKILLS if s.lower() in msg.lower()]

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
    return "unknown"

# ═══════════════════════════════════════════
# 3b. 四档服务体系 — 滴滴模式
# ═══════════════════════════════════════════

TIER_EVENTS = {
    "enterprise": ["发布会","新品首发","品牌活动","时装周","车展","晚宴","颁奖典礼","开业","KOL","达人"],
    "premier":    ["商务会议","论坛","路演","沙龙","培训","签约仪式","公司年会","晚宴"],
    "express":    ["团建","运动会","门店","产品照","探店","会议","展厅","工地"],
    "pool":       ["写真","毕业照","生日","派对","跟拍","证件照","全家福","活动跟拍"],
}

TIER_CONFIG = {
    "enterprise": {"name":"首发定制","min_rating":4.8,"min_tasks":30,"commission":0.25,"need_portfolio":True},
    "premier":    {"name":"资深",    "min_rating":4.5,"min_tasks":15,"commission":0.20},
    "express":    {"name":"专业",    "min_rating":4.0,"min_tasks":5, "commission":0.15},
    "pool":       {"name":"速拍",    "min_rating":0.0,"min_tasks":0, "commission":0.10},
}

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

def register_citizen(name, skills, platform, pid) -> dict:
    s = load_store()
    cid = f"citizen_{len(s['citizens'])+1:03d}"
    c = {
        "id":cid,"name":name,"platform":platform,"platform_id":pid,
        "skills":skills,"languages":["中文"],"timezone":"Asia/Shanghai",
        "rate":"协商","available":True,"rating":5.0,"completed_tasks":0,
        "registered_at":datetime.now().isoformat()[:10],"tags":[]
    }
    s["citizens"][cid] = c
    save_store(s)
    return c

def match_task(skills: list, tier: str = "pool") -> list:
    s = load_store()
    # 按档位过滤
    eligible = filter_by_tier(s.get("citizens", {}), tier)
    r = [sk.lower().strip() for sk in skills]
    scored = []
    for cid, c in eligible.items():
        if not c.get("available", True): continue
        score = 0
        cs = [x.lower() for x in c.get("skills",[])]
        for sk in r:
            for x in cs:
                if sk in x or x in sk: score += 50
                elif any(w in x for w in sk.split()): score += 25
        score += (10 if "中文" in c.get("languages",[]) else 0)
        score += c.get("rating",0) * 3
        score += min(c.get("completed_tasks",0), 20)
        if score > 0: scored.append((cid, c, score))
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
    
    if intent == "help":
        return {"human": card_help(), "agent": {"status":"ok","action":"help"}}
    
    if intent == "register_citizen":
        if not missing:
            name = info.get("name") or coll.get("name") or user_id[:8]
            skills = info.get("skills", [])
            c = register_citizen(name, ",".join(skills), platform, user_id)
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
        c = register_citizen(name, ",".join(skills), platform, uid)
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
        r["agent"]["review"] = review
        r["agent"]["tier"] = tier
        r["agent"]["commission"] = comm
        clear_state(platform, uid)
        return r
    set_state(platform, uid, "post_task", skills=skills, budget=budget, deadline=deadline)
    return {"human": card_post_need(missing), "agent": {"status":"need_info","missing":missing}}
