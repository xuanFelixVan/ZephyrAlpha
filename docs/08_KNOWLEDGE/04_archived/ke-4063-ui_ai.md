---
module_id: KE-3910----------ai-000
title: 14.4 UI 策略——人看什么、AI看什么
category: module_blueprint
ttl: permanent
---

# 14.4 UI 策略——人看什么、AI看什么

14.4 UI 策略——人看什么、AI看什么

| 消费者 | 界面 | 内容 | 更新频率 |
|--------|------|------|:--:|
| **AI Agent** | `unified_asset_index.yaml`（结构化 YAML） | 全量资产 + 分类 + 状态 + 依赖 | 每小时 |
| **AI Agent** | `reconciliation_report.md`（结构化 Markdown） | 孤儿/幽灵/漂移清单 + 自愈结果 | 每次对账 |
| **Owner（人类）** | Dashboard 摘要（写在 session handoff 中） | 总数 / 健康评分 / Top 3 异常 | 每次 session 结束 |
| **Owner（人类）** | Gate 门禁状态 | 健康评分 + 孤儿率是否超标 | CI 构建时 |
| **CI/CD** | Gate exit code | 0=GREEN / 1=RED + 具体超标字段 | 每次检查 |
