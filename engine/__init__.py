"""
速派 · Core Engine v1.0
━━━━━━━━━━━━━━━━━━━━
模块化引擎包。所有公开接口从此文件 re-export。
"""

from engine.schema import (
    SKILLS, SKILL_SYNONYMS,
    TIER_CONFIG, TIER_EVENTS,
    CitizenInput, validate_store,
)

from engine.core import (
    # ── 数据层 ──
    load_store, save_store, register_citizen,
    # ── 技能/意图 ──
    extract_skills, extract_budget, extract_deadline,
    extract_all, missing_fields, parse_intent,
    # ── 档位/匹配 ──
    detect_tier, filter_by_tier,
    get_commission, get_tier_name,
    match_task, review_match,
    deliver_if_approved, escalate_to_claude,
    # ── 任务管理 ──
    accept_task, decline_task,
    # ── Agent 调度 ──
    dispatch_to_codex, dispatch_to_claude, poll_outbox,
    # ── 主入口 ──
    handle_message,
)
