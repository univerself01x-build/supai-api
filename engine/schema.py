"""
速派 · 数据模型 v1.0
━━━━━━━━━━━━━━━━━━━━━━━━
Schema-First — 数据入口校验。Python dataclass + __post_init__，零外部依赖。
对齐 API 契约：docs/api/openapi.yaml
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional


# ═══════════════════════════════════════════
# 技能库 — 对齐 AI 行业数字活动场景
# ═══════════════════════════════════════════

SKILLS = [
    # 摄影摄像
    "产品拍摄", "活动摄影", "发布会拍摄", "商务会议摄影", "短视频", "人像摄影",
    "数码后期", "商业摄影", "电商摄影", "门店拍摄", "展会摄影", "纪录片",
    "活动跟拍", "探店拍摄", "航拍",
    # 设计
    "UI设计", "UX设计", "平面设计", "品牌设计", "Keynote设计", "活动物料设计",
    # 开发
    "前端开发", "后端开发", "全栈开发", "移动开发", "Python", "JavaScript",
    "TypeScript", "React", "Vue", "Node.js",
    # 后期/内容
    "视频剪辑", "音频处理", "动画制作", "文案写作", "翻译",
    # 运营
    "数据分析", "社交媒体运营", "SEO", "SEM",
    # 其他
    "产品经理", "项目管理", "直播", "同传",
]

SKILL_SYNONYMS = {
    "摄影": ["产品拍摄", "活动摄影", "发布会拍摄", "商务会议摄影", "商业摄影",
             "电商摄影", "门店拍摄", "展会摄影", "数码后期", "人像摄影", "活动跟拍"],
    "摄像": ["短视频", "纪录片", "发布会拍摄", "活动摄影", "航拍"],
    "设计": ["UI设计", "UX设计", "平面设计", "品牌设计", "Keynote设计", "活动物料设计"],
    "剪辑": ["视频剪辑", "短视频", "后期制作", "数码后期"],
    "开发": ["前端开发", "后端开发", "全栈开发", "Python", "JavaScript", "TypeScript"],
    "航拍": ["航拍"],
    "探店": ["探店拍摄", "门店拍摄", "产品拍摄"],
}


# ═══════════════════════════════════════════
# 四档服务体系
# ═══════════════════════════════════════════

TIER_CONFIG = {
    "enterprise": {"name":"首发定制","min_rating":4.8,"min_tasks":30,"commission":0.25},
    "premier":    {"name":"资深",    "min_rating":4.5,"min_tasks":15,"commission":0.20},
    "express":    {"name":"专业",    "min_rating":4.0,"min_tasks":5, "commission":0.15},
    "pool":       {"name":"速拍",    "min_rating":0.0,"min_tasks":0, "commission":0.10},
}

TIER_EVENTS = {
    "enterprise": ["发布会","新品首发","品牌活动","时装周","车展","晚宴","颁奖典礼","开业","KOL","达人","AI峰会","Demo Day"],
    "premier":    ["商务会议","论坛","路演","沙龙","培训","签约仪式","公司年会","晚宴","Hackathon","技术沙龙"],
    "express":    ["团建","运动会","门店","产品照","探店","会议","展厅","工地","播客录制","活动","拍摄"],
    "pool":       ["写真","毕业照","生日","派对","跟拍","证件照","全家福","活动跟拍"],
}


# ═══════════════════════════════════════════
# Citizen Schema（摄影师/视觉服务者）
# ═══════════════════════════════════════════

@dataclass
class CitizenInput:
    """注册入口校验。失败 → ValueError"""
    name: str
    platform_id: str
    skills: list[str]
    location: str = "上海"
    languages: list[str] = field(default_factory=lambda: ["中文"])
    tier: str = "pool"
    rating: float = 5.0
    completed_tasks: int = 0
    price_range: list[int] = field(default_factory=lambda: [800, 3000])
    equipment: list[str] = field(default_factory=list)
    available: bool = True
    platform: str = "platform"
    timezone: str = "Asia/Shanghai"
    rate: str = "协商"

    VALID_TIERS = {"enterprise", "premier", "express", "pool"}

    def __post_init__(self):
        if not self.name.strip():
            raise ValueError("name required")
        if not self.platform_id.strip():
            raise ValueError("platform_id required")
        if not self.skills or not isinstance(self.skills, list):
            raise ValueError("skills must be a non-empty list")
        if self.tier not in self.VALID_TIERS:
            raise ValueError(f"Invalid tier: {self.tier}. Must be one of {self.VALID_TIERS}")
        if self.rating < 0 or self.rating > 5.0:
            raise ValueError(f"rating {self.rating} out of range (0-5.0)")
        if len(self.price_range) != 2 or self.price_range[0] < 0:
            raise ValueError(f"invalid price_range: {self.price_range}")

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "platform": self.platform,
            "platform_id": self.platform_id,
            "skills": self.skills,
            "location": self.location,
            "languages": self.languages,
            "tier": self.tier,
            "rating": self.rating,
            "completed_tasks": self.completed_tasks,
            "price_range": self.price_range,
            "equipment": self.equipment,
            "available": self.available,
            "timezone": self.timezone,
            "rate": self.rate,
        }


# ═══════════════════════════════════════════
# 存储结构校验
# ═══════════════════════════════════════════

def validate_store(store: dict) -> dict:
    """校验 store.json 结构完整性。返回 issues 列表"""
    issues = []
    if "citizens" not in store:
        issues.append("missing 'citizens' key")
    if "tasks" not in store:
        issues.append("missing 'tasks' key")

    for cid, c in store.get("citizens", {}).items():
        if not c.get("platform_id"):
            issues.append(f"{cid}: missing platform_id")
        if not c.get("skills") or not isinstance(c.get("skills"), list):
            issues.append(f"{cid}: skills must be a non-empty list")
        if c.get("rating", 0) < 0 or c.get("rating", 0) > 5.0:
            issues.append(f"{cid}: rating out of range")

    # platform_id 唯一性
    ids = [c.get("platform_id") for c in store.get("citizens", {}).values()]
    if len(ids) != len(set(ids)):
        issues.append("duplicate platform_id detected")

    return {"valid": len(issues) == 0, "issues": issues}
