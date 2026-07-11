#!/usr/bin/env python3
"""
速派 Web App · API Server v2.0
──────────────────────────────
FastAPI + Pydantic — SSOT。
SSOT: api_models.py → FastAPI 自动 /docs → openapi-typescript → TS 类型

python3 server.py → http://localhost:8080
"""

import sys, re, json, uuid
from pathlib import Path
from datetime import datetime
from typing import Optional

sys.path.insert(0, str(Path(__file__).parent))

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

from engine import load_store, match_task, review_match, register_citizen
from engine import get_tier_name, get_commission, detect_tier, save_store
from api_models import (
    MatchRequest, ConfirmRequest,
    ProjectCard, ProjectDetail, MatchResult, ConfirmResult,
    TeamSlot, TeamSlotSummary, PhotographerInfo, TimelineEntry,
    ProjectListResponse, ProjectDetailResponse, MatchResponse,
)

app = FastAPI(
    title="速派 API",
    version="0.2.0",
    docs_url="/docs",
    description="AI 行业数字活动视觉 Team 协作平台",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── 辅助函数 ──

CITIES = ["北京","上海","深圳","广州","杭州","成都","武汉","南京","苏州","西安","重庆","厦门","长沙"]

def _extract_location_from_scene(scene: str) -> str:
    """从场景描述提取城市名"""
    for city in CITIES:
        if city in scene:
            return city
    return ""

def _extract_skills_from_scene(scene: str) -> list:
    """从活动场景描述提取技能关键词"""
    from engine.schema import SKILLS
    skills = []
    scene_lower = scene.lower()
    for s in SKILLS:
        if s.lower() in scene_lower:
            skills.append(s)
    if not skills:
        if any(w in scene_lower for w in ["发布","活动","会议","论坛","年会"]):
            skills = ["活动摄影"]
        elif any(w in scene_lower for w in ["产品","电商","门店","探店"]):
            skills = ["产品拍摄"]
        else:
            skills = ["活动摄影"]
    return skills

def _wrap_match_as_team(matches: list, tier: str, project_id: str) -> MatchResult:
    """将引擎匹配结果包装为 Team 格式"""
    recommended = []
    alternatives: dict[str, list] = {}
    seen_photographers = []

    for i, (cid, c, sc) in enumerate(matches):
        slot = TeamSlot(
            role="photographer",
            status="matched" if i == 0 else "matched",
            photographer=PhotographerInfo(
                id=cid,
                name=c.get("name", "?"),
                tier=c.get("tier", "pool"),
                score=sc,
                skills=c.get("skills", []),
                completedTasks=c.get("completed_tasks", 0),
                avgRating=c.get("rating", 0),
            ),
            source="platform",
        )
        if i == 0:
            recommended.append(slot)
        else:
            seen_photographers.append(slot)

    if seen_photographers:
        alternatives["photographer"] = seen_photographers

    return MatchResult(
        projectId=project_id,
        tier=tier,
        recommendedTeam=recommended,
        alternativeOptions=alternatives,
        summary=f"匹配到 {tier} 档视觉 Team。摄影师 {recommended[0].photographer.name if recommended else '待定'}。",
    )

# ── API Routes ──

@app.get("/api/projects", response_model=ProjectListResponse)
async def list_projects(role: str = Query(default="fengge"), client_id: str = Query(default="")):
    """项目卡片列表。role=client 时按 client_id 过滤"""
    store = load_store()
    cards = []
    for tid, task in store.get("tasks", {}).items():
        # 客户只看自己的项目
        if role == "client" and client_id and task.get("client_id") != client_id:
            continue
        # 摄影师只看分配给自己的
        if role == "photographer" and client_id and client_id not in task.get("matched_citizens", []):
            continue
        team_slots = []
        for cid in task.get("matched_citizens", []):
            c = store.get("citizens", {}).get(cid, {})
            team_slots.append(TeamSlotSummary(
                role="photographer",
                status=task.get("status", "matching"),
                assignee=c.get("name", ""),
            ))
        cards.append(ProjectCard(
            id=tid,
            title=task.get("title", "未命名"),
            status=task.get("status", "matching"),
            tier=task.get("tier", "pool"),
            budget=task.get("budget", 0),
            location=task.get("location", "上海"),
            team=team_slots,
            createdAt=task.get("created_at", datetime.now().isoformat()),
        ))

    return ProjectListResponse(human=cards, agent=[])


@app.get("/api/projects/{project_id}", response_model=ProjectDetailResponse)
async def get_project(project_id: str, role: str = Query(default="fengge")):
    """项目详情"""
    store = load_store()
    task = store.get("tasks", {}).get(project_id)
    if not task:
        raise HTTPException(status_code=404, detail="project not found")

    team = []
    for cid in task.get("matched_citizens", []):
        c = store.get("citizens", {}).get(cid, {})
        team.append(TeamSlot(
            role="photographer",
            status="confirmed" if task.get("accepted_by") == cid else "matched",
            photographer=PhotographerInfo(
                id=cid,
                name=c.get("name", "?"),
                tier=c.get("tier", "pool"),
                score=0,
                skills=c.get("skills", []),
                completedTasks=c.get("completed_tasks", 0),
                avgRating=c.get("rating", 0),
            ),
            source="platform",
        ))

    detail = ProjectDetail(
        id=project_id,
        title=task.get("title", "未命名"),
        clientName=task.get("client_id", ""),
        requirement=task.get("description", ""),
        location="上海",
        budget=task.get("budget", 0),
        status=task.get("status", "matching"),
        tier=task.get("tier", "pool"),
        team=team,
        timeline=[
            TimelineEntry(
                timestamp=datetime.now(),
                event=f"项目创建 — {task.get('tier', '')} 档",
                by="系统",
            )
        ],
    )
    return ProjectDetailResponse(human=detail, agent={})


@app.post("/api/match", response_model=MatchResponse)
async def match(req: MatchRequest):
    """提交需求 → 匹配 Team"""
    tier = detect_tier(req.scene)
    skills = _extract_skills_from_scene(req.scene)
    location = _extract_location_from_scene(req.scene) or req.location

    # 从场景描述提取技能关键词
    from engine.schema import SKILLS as _SKILLS
    extracted_skills = skills
    if not extracted_skills:
        extracted_skills = ["活动摄影", "产品拍摄"]  # 默认

    matches = match_task(extracted_skills, tier, location=location)
    # fallback: 档位过滤无结果时降到 pool
    if not matches and tier != "pool":
        matches = match_task(extracted_skills, "pool")
        tier = "pool"
    review = review_match(matches, extracted_skills)

    project_id = f"proj_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    # 保存任务到 store
    store = load_store()
    store["tasks"][project_id] = {
        "id": project_id,
        "title": req.scene,
        "description": req.scene,
        "client_id": "client_default",
        "budget": req.budget,
        "location": location,
        "tier": tier,
        "status": "matching",
        "matched_citizens": [cid for cid, _, _ in matches[:3]],
        "created_at": datetime.now().isoformat(),
    }
    save_store(store)

    result = _wrap_match_as_team(matches, tier, project_id)
    return MatchResponse(human=result, agent={
        "status": "ok",
        "tier": tier,
        "commission": get_commission(tier),
        "review": review,
    })


@app.post("/api/projects/{project_id}/confirm", response_model=ConfirmResult)
async def confirm_project(project_id: str, req: ConfirmRequest):
    """确认 Team 成员"""
    store = load_store()
    task = store.get("tasks", {}).get(project_id)
    if not task:
        raise HTTPException(status_code=404, detail="project not found")

    confirmed = []
    for cr in req.confirmedRoles:
        cid = cr.get("photographerId", "")
        if cid in task.get("matched_citizens", []):
            task["status"] = "confirmed"
            task["accepted_by"] = cid
            confirmed.append(cr["role"])

    pending = [cid for cid in task.get("matched_citizens", [])
               if cid != task.get("accepted_by")]
    save_store(store)

    return ConfirmResult(
        projectId=project_id,
        status="confirmed" if confirmed else "partially_confirmed",
        confirmed=confirmed,
        pending=pending,
        nextStep=f"已通知摄影师。待Team到齐。" if confirmed else "仍需确认角色。",
    )


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080, log_level="info")
