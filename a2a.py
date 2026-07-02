"""
数字公民平台 · A2A 接口
Agent-to-Agent Protocol

三种调用方式:
1. Python import — 本地 Agent 直接调用
2. stdio JSON — 子进程 Agent 通过 stdin/stdout
3. CLI — 终端命令
"""

import json, sys
from pathlib import Path
from engine import (
    register_citizen, match_task, load_store,
    extract_skills, extract_all, missing_fields,
    card_match, card_register_done,
    handle_message,
)

# ═══════════════════════════════════════════
# 1. 纯函数接口 (Python import)
# ═══════════════════════════════════════════

def a2a_register(name: str, skills: list, platform: str = "agent", pid: str = None) -> dict:
    """Agent 注册人才"""
    c = register_citizen(name, ",".join(skills), platform, pid or f"a2a_{name}")
    return {"status": "ok", "citizen": c}

def a2a_match(required_skills: list, tier: str = "pool") -> dict:
    """Agent 请求匹配，支持分档"""
    matched = match_task(required_skills, tier)
    return card_match(matched)["agent"]

def a2a_status(citizen_id: str = None) -> dict:
    """查询数据状态"""
    store = load_store()
    if citizen_id:
        c = store["citizens"].get(citizen_id)
        return {"status": "ok", "citizen": c} if c else {"status": "not_found"}
    return {
        "status": "ok",
        "citizen_count": len(store.get("citizens", {})),
        "task_count": len(store.get("tasks", {})),
    }

# ═══════════════════════════════════════════
# 2. JSON stdio 协议 (子进程 Agent)
# ═══════════════════════════════════════════

ACTIONS = {
    "register": lambda p: a2a_register(p["name"], p["skills"], p.get("platform","agent"), p.get("pid")),
    "match": lambda p: a2a_match(p["skills"]),
    "status": lambda p: a2a_status(p.get("citizen_id")),
    "chat": lambda p: handle_message(p.get("platform","agent"), p.get("user_id","a2a"), p["message"]),
}

def stdio_serve():
    """从 stdin 读 JSON，写 JSON 到 stdout。一行一个请求。"""
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
            action = req.get("action")
            params = req.get("params", {})
            if action not in ACTIONS:
                resp = {"status": "error", "error": f"unknown action: {action}"}
            else:
                resp = ACTIONS[action](params)
        except Exception as e:
            resp = {"status": "error", "error": str(e)}
        print(json.dumps(resp, ensure_ascii=False), flush=True)

# ═══════════════════════════════════════════
# 3. CLI
# ═══════════════════════════════════════════

if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description="数字公民 A2A 接口")
    ap.add_argument("action", choices=["register","match","status","serve"])
    ap.add_argument("--name", help="姓名")
    ap.add_argument("--skills", help="技能，逗号分隔")
    ap.add_argument("--id", help="公民ID")
    args = ap.parse_args()

    if args.action == "serve":
        stdio_serve()
    elif args.action == "register":
        r = a2a_register(args.name, args.skills.split(","))
        print(json.dumps(r, ensure_ascii=False, indent=2))
    elif args.action == "match":
        r = a2a_match(args.skills.split(","))
        print(json.dumps(r, ensure_ascii=False, indent=2))
    elif args.action == "status":
        r = a2a_status(args.id)
        print(json.dumps(r, ensure_ascii=False, indent=2))
