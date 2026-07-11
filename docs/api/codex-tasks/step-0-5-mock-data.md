# Step 0.5: 生成模拟摄影师数据

## 任务

生成 20 个摄影师的 JSON 数据，写入 `data/store.json`。

## 数据质量标准

| 维度 | 要求 |
|------|------|
| **技能混搭** | 每人 2-4 个技能，有区分度。例如"产品拍摄+活动摄影+短视频" ≠ "证件照+写真+基础修图" |
| **评分分布** | 4.2-5.0，正态分布。不要全 5.0，不要全 4.2 |
| **四档覆盖** | enterprise(≥4.8/≥30单) 3人, premier(≥4.5/≥15单) 5人, express(≥4.0/≥5单) 7人, pool(≥0) 5人 |
| **价格区间** | ¥800（pool）到 ¥5000（enterprise），按档位分布 |
| **地域** | 70% 上海，20% 北京，10% 深圳 |
| **platform_id** | 20 个唯一 ID，不重复 |

## 输出格式

```json
{
  "citizens": {
    "platform_001": {
      "name": "LuckLee",
      "tier": "enterprise",
      "skills": ["产品拍摄", "活动摄影", "短视频"],
      "rating": 4.8,
      "completed_tasks": 42,
      "price_range": [3000, 5000],
      "location": "上海",
      "platform_id": "platform_001",
      "available": true,
      "languages": ["中文", "英文"],
      "equipment": ["Sony A7M4", "DJI RS4"]
    }
  },
  "tasks": {}
}
```

## Schema 校验

生成后自检：
- 评分在 4.2-5.0 区间
- platform_id 全部唯一（20 个不重复）
- 每档人数符合分配
- 技能列表每人不为空
