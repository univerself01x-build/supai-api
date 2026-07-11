#!/usr/bin/env python3
"""速派 API 测试套件 — Python stdlib only"""
import urllib.request, urllib.error, json, sys, os

BASE = "http://localhost:8081/api"
PASS = 0
FAIL = 0

def req(method, path, data=None):
    url = f"{BASE}{path}"
    body = json.dumps(data).encode() if data else None
    r = urllib.request.Request(url, data=body, method=method,
        headers={"Content-Type": "application/json"} if body else {})
    try:
        with urllib.request.urlopen(r, timeout=5) as resp:
            return resp.status, json.loads(resp.read())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read())

def check(name, status, key, expected, actual):
    global PASS, FAIL
    if expected == actual:
        PASS += 1
        print(f"  PASS {name}: {key}={actual}")
    else:
        FAIL += 1
        print(f"  FAIL {name}: {key} expected={expected} got={actual}")

def test(name, fn):
    try:
        fn()
    except Exception as e:
        global FAIL
        FAIL += 1
        print(f"  FAIL {name}: {e}")

print("=== API Test Suite ===")

# 1. Status
code, d = req("GET", "/status")
check("status", code, "status", 200, code)
check("status.ok", code, "ok", "ok", d.get("status"))

# 2. Project list
code, d = req("GET", "/projects")
check("projects", code, "code", 200, code)
check("projects.human", code, "human", True, isinstance(d.get("human"), list))

# 3. Project detail
code, d = req("GET", "/projects/task_003")
check("detail", code, "code", 200, code)
check("detail.title", code, "title", "发布会拍摄", d["human"]["title"])

# 4. 404
code, d = req("GET", "/projects/nonexist")
check("404", code, "code", 404, code)

# 5. Match enterprise
code, d = req("POST", "/match", {"scene":"AI产品发布会","budget":8000})
check("match.ent.code", code, "200", True, code==200)
check("match.ent.tier", code, "enterprise", True, d["human"]["tier"]=="enterprise")

# 6. Match pool
code, d = req("POST", "/match", {"scene":"生日派对跟拍","budget":800})
check("match.pool.code", code, "200", True, code==200)

# 7. Confirm endpoint (creates project first, then confirms)
code, d = req("POST", "/match", {"scene":"团建拍摄","budget":3000})
project_id = d["human"]["projectId"]
code, d2 = req("POST", f"/projects/{project_id}/confirm", {"confirmedRoles":[]})
check("confirm.code", code, "200", True, code==200)

print(f"\nResult: {PASS} pass, {FAIL} fail")
sys.exit(0 if FAIL == 0 else 1)
