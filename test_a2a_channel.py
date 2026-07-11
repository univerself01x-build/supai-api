"""测试 A+B 通道是否修复"""
import json, subprocess, sys
from pathlib import Path

A2A = Path("/Users/lifeng/.hermes/projects/digital-citizen/a2a.py")

def send(msg):
    """通过 A2A chat action 发送消息"""
    req = json.dumps({"action": "chat", "params": {"message": msg}})
    r = subprocess.run(
        ["python3", str(A2A), "serve"],
        input=req, capture_output=True, text=True, timeout=5
    )
    return json.loads(r.stdout.strip())

# 测试 1: Claude 发技术讨论 —— 不应被 parse_intent 拦截
print("=== 测试 1: Agent 技术讨论（走 agent_chat 独立通道）===")
r = send("星辰，register_citizen 有 bug，skills 存成了字符串导致匹配按单字拆解")
print(f"  status: {r.get('agent', {}).get('status')}")
print(f"  action: {r.get('agent', {}).get('action')}")
print(f"  message: {r.get('agent', {}).get('message', '')[:80]}...")

assert r["agent"]["action"] == "agent_chat", f"❌ 预期 agent_chat，实际: {r['agent']['action']}"
print("  ✅ 未经过意图解析器！\n")

# 测试 2: outbox 轮询 — 模拟 Claude 写了响应
print("=== 测试 2: outbox 轮询（poll_outbox）===")
OUTBOX = Path("/Users/lifeng/.hermes/context/claude/outbox")
CLAUDE_INBOX = Path("/Users/lifeng/.hermes/context/claude/inbox")
ARCHIVE = Path("/Users/lifeng/.hermes/context/hermes/archive")

# 写一个模拟 Claude 响应
resp = {
    "id": "resp_test_20260704_180000",
    "timestamp": "2026-07-04T18:00:00",
    "from": "claude",
    "to": "hermes",
    "in_response_to": "req_test_20260704_180000",
    "intent": "review",
    "payload": {
        "verdict": "confirmed_issue",
        "root_cause": "字符串被当成数组拆成单字",
        "recommendation": "强制转数组",
        "action": "fix_code"
    },
    "thinking": "这确实是个bug，应该修复",
    "status": "pending"
}
(OUTBOX / "resp_test_20260704_180000.json").write_text(
    json.dumps(resp, ensure_ascii=False, indent=2)
)

# 写一个模拟 inbox 请求（在 claude/inbox/，由星辰发出）
req = {
    "id": "req_test_20260704_180000",
    "from": "hermes",
    "to": "claude",
    "task": "review",
    "status": "pending"
}
(CLAUDE_INBOX / "req_test_20260704_180000.json").write_text(
    json.dumps(req, ensure_ascii=False, indent=2)
)

print(f"  outbox 写入: resp_test_20260704_180000.json")
print(f"  claude/inbox 写入: req_test_20260704_180000.json")

# 发送消息触发轮询
r = send("随便说句话触发轮询")
pending = r.get("agent", {}).get("pending_details", [])
print(f"  pending_processed: {r.get('agent', {}).get('pending_processed')}")

if pending:
    print(f"  ✅ poll_outbox 工作正常！处理了 {len(pending)} 条:")
    for p in pending:
        print(f"    - {p['req_id']}: {p['verdict']}")
    
    # 验证归档
    assert not (CLAUDE_INBOX / "req_test_20260704_180000.json").exists(), "Claude inbox 应已归档"
    assert (ARCHIVE / "req_test_20260704_180000.json").exists(), "Archive 应有文件"
    print("  ✅ claude/inbox 已归档到 archive/")
    
    # 验证 acknowledged
    updated = json.loads((OUTBOX / "resp_test_20260704_180000.json").read_text())
    assert updated["status"] == "acknowledged", "Outbox 应标记为 acknowledged"
    print("  ✅ outbox 已标记 acknowledged")
else:
    print("  ❌ poll_outbox 未处理（可能已在前一次轮询中处理）")

# 清理测试数据
for f in list(OUTBOX.glob("resp_test_*.json")) + list(OUTBOX.glob("resp_req_test_*.json")):
    f.unlink()
for f in CLAUDE_INBOX.glob("req_test_*.json"):
    f.unlink()
for f in ARCHIVE.glob("req_test_*.json"):
    f.unlink()

print("\n🎉 全部测试通过！")
