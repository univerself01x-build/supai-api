"""
速派 · API Models v1.0
━━━━━━━━━━━━━━━━━━━━
Pydantic models — 唯一真相源（SSOT）。

FastAPI 自动生成 OpenAPI (/docs)
openapi-typescript 自动生成 TypeScript 类型

改一个字段 → 改这里 → 其余自动同步。
"""

from __future__ import annotations
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

# ═══════════════════════════════════════════
# 请求
# ═══════════════════════════════════════════

class MatchRequest(BaseModel):
    scene: str = Field(..., example="AI产品发布会", description="活动场景描述")
    budget: int = Field(..., ge=500, le=100000, example=5000, description="预算（元）")
    location: str = Field(default="上海", example="上海")
    roles: list[str] = Field(
        default=["photographer"],
        example=["photographer", "editor"],
        description="需要的角色"
    )
    customRoles: list[str] = Field(
        default=[],
        example=["designer"],
        description="客户自备的角色"
    )

class ConfirmRequest(BaseModel):
    confirmedRoles: list[dict] = Field(
        ...,
        example=[{"role": "photographer", "photographerId": "citizen_018", "source": "platform"}],
        description="客户确认的角色列表"
    )
    note: Optional[str] = Field(default=None, description="客户备注")

# ═══════════════════════════════════════════
# 响应
# ═══════════════════════════════════════════

class PhotographerInfo(BaseModel):
    id: str
    name: str
    tier: str
    score: float
    skills: list[str]
    completedTasks: int
    avgRating: float

class TeamSlot(BaseModel):
    role: str
    status: str = "matched"  # matched | confirmed | pending | custom
    photographer: Optional[PhotographerInfo] = None
    source: str = "platform"  # platform | custom

class TeamSlotSummary(BaseModel):
    role: str
    status: str
    assignee: Optional[str] = None

class ProjectCard(BaseModel):
    id: str
    title: str
    status: str
    tier: str = "pool"
    budget: int = 0
    location: str = "上海"
    team: list[TeamSlotSummary]
    createdAt: datetime

class TimelineEntry(BaseModel):
    timestamp: datetime
    event: str
    by: str

class ProjectDetail(BaseModel):
    id: str
    title: str
    clientName: str = ""
    requirement: str = ""
    location: str = ""
    budget: int = 0
    status: str = "matching"
    tier: str = "pool"
    team: list[TeamSlot] = []
    timeline: list[TimelineEntry] = []

class MatchResult(BaseModel):
    projectId: str
    tier: str
    recommendedTeam: list[TeamSlot]
    alternativeOptions: dict[str, list[TeamSlot]] = {}
    summary: str

class ConfirmResult(BaseModel):
    projectId: str
    status: str
    confirmed: list[str] = []
    pending: list[str] = []
    nextStep: str = ""

# ═══════════════════════════════════════════
# 列表响应（双通道）
# ═══════════════════════════════════════════

class ProjectListResponse(BaseModel):
    human: list[ProjectCard]
    agent: list[dict] = []

class ProjectDetailResponse(BaseModel):
    human: ProjectDetail
    agent: dict = {}

class MatchResponse(BaseModel):
    human: MatchResult
    agent: dict = {}

class ErrorResponse(BaseModel):
    error: str
    detail: str = ""
    suggestion: str = ""
