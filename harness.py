#!/usr/bin/env python3
"""
数字公民平台 · Harness 测试套件
─────────────────────────────
Agent 时代的 CI/CD。每次改引擎就跑一遍。
"""

import sys
sys.path.insert(0, '/Users/lifeng/.hermes/digital-citizen')
from engine import (
    parse_intent, extract_skills, extract_all,
    match_task, review_match, deliver_if_approved,
    handle_message, register_citizen, load_store,
    extract_budget, extract_deadline,
)

PASS = 0
FAIL = 0

def t(name, fn):
    global PASS, FAIL
    try:
        fn()
        print(f"  ✅ {name}")
        PASS += 1
    except Exception as e:
        print(f"  ❌ {name}: {e}")
        FAIL += 1

def assert_eq(a, b, msg=""):
    assert a == b, f"{msg} expected={b!r} got={a!r}"

def assert_true(x, msg=""):
    assert x, msg

# ═══════════════════════════════════════════
# 1. 意图解析
# ═══════════════════════════════════════════

print("\n── 意图解析 ──")

t("找设计师 → post_task",
  lambda: assert_eq(parse_intent("找UI设计师"), "post_task"))

t("我是开发者 → register_citizen",
  lambda: assert_eq(parse_intent("我是全栈开发者"), "register_citizen"))

t("注册 → register_citizen",
  lambda: assert_eq(parse_intent("我要注册"), "register_citizen"))

t("帮助 → help",
  lambda: assert_eq(parse_intent("帮助"), "help"))

t("接 → accept_task",
  lambda: assert_eq(parse_intent("接"), "accept_task"))

t("过 → decline_task",
  lambda: assert_eq(parse_intent("过"), "decline_task"))

t("你好 → greeting",
  lambda: assert_eq(parse_intent("你好"), "greeting"))

t("随便 → unknown",
  lambda: assert_eq(parse_intent("今天天气真好"), "unknown"))

# ═══════════════════════════════════════════
# 2. 信息抽取
# ═══════════════════════════════════════════

print("\n── 信息抽取 ──")

t("提取UI设计+Figma",
  lambda: assert_true("UI设计" in extract_skills("需要UI设计师，会Figma")))

t("提取预算3000",
  lambda: assert_eq(extract_budget("预算3000"), 3000))

t("提取预算2万",
  lambda: assert_eq(extract_budget("预算2万"), 20000))

t("提取截止时间",
  lambda: assert_true(extract_deadline("周五前") is not None))

t("一句话全提取",
  lambda: (
    (info := extract_all("找UI设计师，Figma，3000元，周五前")),
    assert_true(len(info["skills"]) >= 1),
    assert_eq(info["budget"], 3000),
    assert_true(info["deadline"] is not None),
  ))

# ═══════════════════════════════════════════
# 3. 匹配质量
# ═══════════════════════════════════════════

print("\n── 匹配质量 ──")

t("UI设计匹配有人才",
  lambda: (
    (m := match_task(["UI设计", "Figma"])),
    assert_true(len(m) >= 1, f"got {len(m)} matches"),
  ))

t("React匹配有人才",
  lambda: (
    (m := match_task(["React", "TypeScript"])),
    assert_true(len(m) >= 1, f"got {len(m)} matches"),
  ))

t("匹配含审查字段",
  lambda: (
    (r := handle_message("feishu", "h_c2", "找UI设计师，Figma，3000，周五前")),
    assert_true("review" in r["agent"], str(list(r["agent"].keys()))),
  ))

# ═══════════════════════════════════════════
# 4. 审查
# ═══════════════════════════════════════════

print("\n── 审查 ──")

t("好匹配通过审查",
  lambda: (
    (m := match_task(["UI设计", "Figma"])),
    (rev := review_match(m, ["UI设计", "Figma"])),
    assert_true(deliver_if_approved(rev), f"issues: {rev['issues']}"),
  ))

t("空匹配拒绝审查",
  lambda: (
    (rev := review_match([], ["核物理"])),
    assert_eq(rev["verdict"], "reject"),
    assert_true(not deliver_if_approved(rev)),
  ))

t("审查未通过有issues",
  lambda: (
    (rev := review_match([], ["核物理"])),
    assert_true(len(rev["issues"]) > 0),
  ))

# ═══════════════════════════════════════════
# 5. 端到端 (注册→匹配)
# ═══════════════════════════════════════════

print("\n── 端到端 ──")

t("注册新人才",
  lambda: (
    (r := handle_message("feishu", "h_test_1", "我是摄影师，会PS和剪辑")),
    assert_true("记住了" in r["human"] or "已创建" in r["human"]),
    assert_eq(r["agent"]["status"], "ok"),
  ))

t("发布任务→匹配→审查",
  lambda: (
    (r := handle_message("feishu", "h_client_1", "找摄影师，3000，周五前")),
    assert_true("review" in r["agent"]),
    assert_true(r["agent"]["review"]["verdict"] in ("deliver", "review", "reject")),
  ))

t("欢迎消息格式干净",
  lambda: (
    (r := handle_message("feishu", "h_new", "你好")),
    assert_true("━" not in r["human"]),  # 无框线
    assert_true("┌" not in r["human"]),
    assert_true("└" not in r["human"]),
    assert_true("══" not in r["human"]),
    assert_true("🔹" not in r["human"]), # 无装饰堆砌
  ))

# ═══════════════════════════════════════════
# 6. A2A 一致性
# ═══════════════════════════════════════════

print("\n── A2A 一致性 ──")

t("双通道都返回",
  lambda: (
    (r := handle_message("feishu", "h_a2a", "帮助")),
    assert_true("human" in r),
    assert_true("agent" in r),
    assert_true(len(r["human"]) > 0),
    assert_eq(r["agent"]["status"], "ok"),
  ))

t("匹配含审查字段",
  lambda: (
    (r := handle_message("feishu", "h_a2a3", "找UI设计师，Figma，3000，周五前")),
    assert_true("review" in r["agent"], f"agent keys: {list(r['agent'].keys())}"),
  ))

# ═══════════════════════════════════════════
# 结果
# ═══════════════════════════════════════════

print(f"\n{'='*40}")
total = PASS + FAIL
print(f" 通过: {PASS}/{total}")
if FAIL:
    print(f" 失败: {FAIL}/{total}")
    sys.exit(1)
else:
    print(f" 🎉 全部通过!")
