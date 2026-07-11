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
from fastapi.staticfiles import StaticFiles
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

# ── Static files (H5 pages served directly by FastAPI) ──
STATIC_DIR = Path(__file__).parent / "static"
STATIC_DIR.mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

from fastapi.responses import FileResponse

@app.get("/order.html")
async def serve_order():
    return FileResponse(str(STATIC_DIR / "order.html"))

@app.get("/confirm.html")
async def serve_confirm():
    return FileResponse(str(STATIC_DIR / "confirm.html"))

@app.get("/")
async def serve_index():
    return FileResponse(str(STATIC_DIR / "order.html"))

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

# ── 健康检查 ──

@app.get("/api/health")
async def health():
    from engine.core import load_store
    s = load_store()
    return {
        "status": "ok",
        "version": "0.2.0",
        "photographers": len(s.get("citizens", {})),
        "projects": len(s.get("tasks", {})),
    }

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


@app.post("/api/seed")
async def seed_photographers():
    """一次性灌入模拟摄影师数据"""
    from engine import load_store, register_citizen, save_store

    MOCK = [
        ["朱鹏",["活动摄影","商业摄影","产品拍摄","纪录片"],"enterprise",4.9,42,[3000,5000],"上海",["Sony A7M4","DJI RS4"],["中文","英文"]],
        ["李娜",["产品拍摄","电商拍摄","短视频"],"enterprise",4.8,38,[3000,5000],"上海",["Canon R5"],["中文"]],
        ["赵峰",["商业摄影","活动摄影","产品拍摄","纪录片"],"enterprise",4.8,35,[2500,5000],"上海",["Sony A7M4"],["中文"]],
        ["马骏",["发布会拍摄","商务会议摄影","短视频"],"premier",4.7,25,[2000,4000],"上海",["Nikon Z8"],["中文","英文"]],
        ["Lee",["人像摄影","产品拍摄","数码后期"],"premier",4.6,22,[2000,4000],"北京",["Sony A7M3"],["中文","英文"]],
        ["刘德华",["活动摄影","展会摄影","视频剪辑"],"premier",4.6,20,[2000,3500],"上海",["Canon R6"],["中文"]],
        ["周杰",["门店拍摄","产品拍摄","电商摄影"],"premier",4.5,18,[1500,3500],"上海",["Sony A7M3"],["中文"]],
        ["陈摄影师",["商务会议摄影","活动摄影","短视频"],"premier",4.5,16,[1500,3000],"上海",["Fujifilm XT-5"],["中文"]],
        ["王思",["产品拍摄","数码后期","人像摄影"],"express",4.4,12,[1200,2500],"上海",["Sony A6400"],["中文"]],
        ["LuckLee",["活动摄影","产品拍摄","短视频"],"express",4.3,10,[1200,2500],"上海",["Canon R6"],["中文"]],
        ["赵六",["人像摄影","写真","数码后期"],"express",4.3,8,[1000,2000],"上海",["Nikon Z6"],["中文"]],
        ["小李",["短视频","活动摄影","视频剪辑"],"express",4.2,7,[1000,2000],"北京",["Sony A7M3"],["中文"]],
        ["张伟",["产品拍摄","门店拍摄"],"express",4.2,6,[1000,2000],"上海",["Canon R5"],["中文"]],
        ["林某",["商务会议摄影","活动摄影"],"express",4.1,5,[1000,1800],"深圳",["Sony A7M4"],["中文","粤语"]],
        ["孙阳",["短视频","活动摄影"],"express",4.0,5,[800,1800],"上海",["DJI Pocket 3"],["中文"]],
        ["黄摄影师",["产品拍摄","电商摄影"],"pool",4.0,3,[800,1500],"上海",["Sony A6400"],["中文"]],
        ["周星",["人像摄影","写真"],"pool",3.9,2,[800,1200],"上海",["Canon R6"],["中文"]],
        ["吴某",["短视频","活动摄影"],"pool",3.8,2,[800,1200],"北京",["iPhone 15 Pro"],["中文"]],
        ["李强",["人像摄影","商业摄影","产品拍摄","活动摄影"],"pool",4.2,1,[800,1500],"上海",["Sony A7M3"],["中文"]],
        ["郑某",["门店拍摄","产品拍摄"],"pool",4.0,0,[800,1000],"上海",["Canon R5"],["中文"]],
    ]

    store = load_store()
    count = 0
    for name, skills, tier, rating, completed, price, location, equip, langs in MOCK:
        pid = f"photographer_{count+1:03d}"
        if any(c.get("platform_id") == pid for c in store.get("citizens", {}).values()):
            count += 1; continue
        r = register_citizen(name, skills, "platform", pid, location=location,
                            languages=langs, tier=tier, rating=rating,
                            completed_tasks=completed, price_range=price, equipment=equip)
        if not isinstance(r, dict) or "error" not in r:
            count += 1
    return {"status": "ok", "seeded": count, "total": len(load_store()["citizens"])}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080, log_level="info")
