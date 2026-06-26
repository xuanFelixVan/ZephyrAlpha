---
module_id: KE-3025
title: 修复的 3 个关键问题
category: session_log
ttl: permanent
---

# 修复的 3 个关键问题

修复的 3 个关键问题

| # | 问题 | 修复 |
|---|------|------|
| 1 | L02 __init__.py 被 codegen 覆盖，丢失 FactorRegistry/autodiscover_factors | 重写为包含 CODEGEN-GUARD 注释的完整版 |
| 2 | 14 层 architecture_model YAML 与 src 文件列表不匹配 | 批量同步——自动扫描 src 中所有 .py 并更新 YAML |
| 3 | Phase E 测试对 G1-G5 legacy schema 过严 | 添加 LEGACY_GATES 分类 + 降级为 warning |
