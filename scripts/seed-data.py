#!/usr/bin/env python3
"""Seed Railway store.json with mock photographer data"""
import json, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from engine import load_store, register_citizen, save_store

store = load_store()
citizens = store.get("citizens", {})

# Remove old test data (citizen_xxx format without platform_id)
to_remove = []
for cid, c in citizens.items():
    if not c.get("platform_id") or c.get("platform_id", "").startswith("test"):
        to_remove.append(cid)
for cid in to_remove:
    del citizens[cid]

# 20 mock photographers — 上海为主，四档覆盖，技能混搭
MOCK = [
    {"name":"朱鹏","skills":["活动摄影","商业摄影","产品拍摄","纪录片"],"tier":"enterprise","rating":4.9,"completed_tasks":42,"price_range":[3000,5000],"location":"上海","equipment":["Sony A7M4","DJI RS4"],"languages":["中文","英文"]},
    {"name":"李娜","skills":["产品拍摄","电商摄影","短视频"],"tier":"enterprise","rating":4.8,"completed_tasks":38,"price_range":[3000,5000],"location":"上海","equipment":["Canon R5"],"languages":["中文"]},
    {"name":"赵峰","skills":["商业摄影","活动摄影","产品拍摄","纪录片"],"tier":"enterprise","rating":4.8,"completed_tasks":35,"price_range":[2500,5000],"location":"上海","equipment":["Sony A7M4"],"languages":["中文"]},
    {"name":"马骏","skills":["发布会拍摄","商务会议摄影","短视频"],"tier":"premier","rating":4.7,"completed_tasks":25,"price_range":[2000,4000],"location":"上海","equipment":["Nikon Z8"],"languages":["中文","英文"]},
    {"name":"Lee","skills":["人像摄影","产品拍摄","数码后期"],"tier":"premier","rating":4.6,"completed_tasks":22,"price_range":[2000,4000],"location":"北京","equipment":["Sony A7M3"],"languages":["中文","英文"]},
    {"name":"刘德华","skills":["活动摄影","展会摄影","视频剪辑"],"tier":"premier","rating":4.6,"completed_tasks":20,"price_range":[2000,3500],"location":"上海","equipment":["Canon R6"],"languages":["中文"]},
    {"name":"周杰","skills":["门店拍摄","产品拍摄","电商摄影"],"tier":"premier","rating":4.5,"completed_tasks":18,"price_range":[1500,3500],"location":"上海","equipment":["Sony A7M3"],"languages":["中文"]},
    {"name":"陈摄影师","skills":["商务会议摄影","活动摄影","短视频"],"tier":"premier","rating":4.5,"completed_tasks":16,"price_range":[1500,3000],"location":"上海","equipment":["Fujifilm XT-5"],"languages":["中文"]},
    {"name":"王思","skills":["产品拍摄","数码后期","人像摄影"],"tier":"express","rating":4.4,"completed_tasks":12,"price_range":[1200,2500],"location":"上海","equipment":["Sony A6400"],"languages":["中文"]},
    {"name":"LuckLee","skills":["活动摄影","产品拍摄","短视频"],"tier":"express","rating":4.3,"completed_tasks":10,"price_range":[1200,2500],"location":"上海","equipment":["Canon R6"],"languages":["中文"]},
    {"name":"赵六","skills":["人像摄影","写真","数码后期"],"tier":"express","rating":4.3,"completed_tasks":8,"price_range":[1000,2000],"location":"上海","equipment":["Nikon Z6"],"languages":["中文"]},
    {"name":"小李","skills":["短视频","活动摄影","视频剪辑"],"tier":"express","rating":4.2,"completed_tasks":7,"price_range":[1000,2000],"location":"北京","equipment":["Sony A7M3"],"languages":["中文"]},
    {"name":"张伟","skills":["产品拍摄","门店拍摄"],"tier":"express","rating":4.2,"completed_tasks":6,"price_range":[1000,2000],"location":"上海","equipment":["Canon R5"],"languages":["中文"]},
    {"name":"林某","skills":["商务会议摄影","活动摄影"],"tier":"express","rating":4.1,"completed_tasks":5,"price_range":[1000,1800],"location":"深圳","equipment":["Sony A7M4"],"languages":["中文","粤语"]},
    {"name":"孙阳","skills":["短视频","活动摄影"],"tier":"express","rating":4.0,"completed_tasks":5,"price_range":[800,1800],"location":"上海","equipment":["DJI Pocket 3"],"languages":["中文"]},
    {"name":"黄摄影师","skills":["产品拍摄","电商摄影"],"tier":"pool","rating":4.0,"completed_tasks":3,"price_range":[800,1500],"location":"上海","equipment":["Sony A6400"],"languages":["中文"]},
    {"name":"周星","skills":["人像摄影","写真"],"tier":"pool","rating":3.9,"completed_tasks":2,"price_range":[800,1200],"location":"上海","equipment":["Canon R6"],"languages":["中文"]},
    {"name":"吴某","skills":["短视频","活动摄影"],"tier":"pool","rating":3.8,"completed_tasks":2,"price_range":[800,1200],"location":"北京","equipment":["iPhone 15 Pro"],"languages":["中文"]},
    {"name":"李强","skills":["人像摄影","商业摄影","产品拍摄","活动摄影"],"tier":"pool","rating":4.2,"completed_tasks":1,"price_range":[800,1500],"location":"上海","equipment":["Sony A7M3"],"languages":["中文"]},
    {"name":"郑某","skills":["门店拍摄","产品拍摄"],"tier":"pool","rating":4.0,"completed_tasks":0,"price_range":[800,1000],"location":"上海","equipment":["Canon R5"],"languages":["中文"]},
]

for i, m in enumerate(MOCK):
    pid = f"photographer_{i+1:03d}"
    if any(c.get("platform_id") == pid for c in citizens.values()):
        continue
    c = register_citizen(
        name=m["name"], skills=m["skills"], platform="platform", pid=pid,
        location=m["location"], languages=m.get("languages", ["中文"]),
        tier=m["tier"], rating=m["rating"], completed_tasks=m["completed_tasks"],
        price_range=m["price_range"], equipment=m.get("equipment", []),
    )
    if isinstance(c, dict) and "error" in c:
        print(f"SKIP {m['name']}: {c['error']}")
    else:
        print(f"OK {m['name']} ({m['tier']})")

print(f"\nTotal citizens: {len(load_store()['citizens'])}")
