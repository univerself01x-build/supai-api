# 速派 Web App · PRD v1.0

## 目标
搭建客户自助下单页面。客户打开链接 → 描述需求 → 看匹配结果 → 确认摄影师。

## 用户
企业活动负责人。非技术人员。用手机打开。

## 核心流程
1. 客户输入需求（一句话描述）
2. 后端调用引擎 `handle_message()`
3. 前端展示匹配结果（卡片式）
4. 客户点确认 → 通知摄影师

## 非目标（v1 不做）
- 注册登录
- 支付
- 历史记录
- 多语言

## API 契约
```
POST /api/match
Body: {"message": "拍发布会，上海，5000"}
Response: {
  "human": "格式化的匹配结果",
  "agent": {"matches": [...], "tier": "enterprise", "commission": 0.25}
}
```

## 技术选型
- 后端：Python HTTP Server（标准库，零依赖）
- 前端：单文件 HTML（零依赖，移动端优先）
- 通信：JSON over POST

## 开发规范
- 代码量：< 300 行
- Harness：API 覆盖 3 个测试用例
- 风格：参照 gstack Builder Ethos（Boil the Ocean）
- 审查：参照 superpowers Red Flags（永不跳过 Harness）
- 架构：参照 mattpocock（薄壳厚核：HTML薄壳 → engine厚核）

## 验收标准
- ✅ 手机打开不横向滚动
- ✅ 输入需求 → 2秒内出结果
- ✅ 格式无框线、无模型劫持
- ✅ Harness 3/3 通过
