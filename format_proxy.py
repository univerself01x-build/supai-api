#!/usr/bin/env python3
"""
数字公民 Bot · 格式化代理 v0.5
截获飞书/微信消息，直调引擎，绕过模型排版。
v0.5: + 跨平台通知 — agent.notify_client 自动触发 hermes send
"""
import sys, subprocess, json

sys.path.insert(0, '/Users/lifeng/.hermes/digital-citizen')
from engine import handle_message


def process(platform: str, user_id: str, message: str) -> str:
    """处理用户消息，返回格式化好的回复。100% 控制排版。"""
    result = handle_message(platform, user_id, message)
    human = result.get("human", "")
    agent = result.get("agent", {})

    # 跨平台通知：agent 返回 notify_client 时自动执行 hermes send
    notify = agent.get("notify_client")
    if notify:
        target = f"{notify['platform']}:{notify['user_id']}"
        msg = notify["message"]
        try:
            subprocess.run(
                ["hermes", "send", "--to", target, msg],
                capture_output=True, timeout=10
            )
        except Exception as e:
            # 通知失败不影响主流程
            pass

    return human


if __name__ == "__main__":
    # stdin JSON 协议，供 gateway hook 调用
    for line in sys.stdin:
        req = json.loads(line.strip())
        reply = process(req["platform"], req["user_id"], req["message"])
        print(json.dumps({"reply": reply}, ensure_ascii=False), flush=True)
