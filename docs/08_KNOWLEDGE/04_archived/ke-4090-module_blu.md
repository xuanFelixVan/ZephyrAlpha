---
module_id: KE-3936
title: 16.2 各组件恢复策略
category: module_blueprint
ttl: permanent
doc_type: knowledge_entry
---

# 16.2 各组件恢复策略

16.2 各组件恢复策略

| 组件 | 数据特性 | 备份策略 | 恢复方式 | 校验方式 |
|------|---------|---------|---------|---------|
| `ai_provenance` 表 | Immutable Core，只追加 | 每日全量备份到 `_audit_cache_backups/` | 从最新备份恢复 + Hash 链完整性校验 | `SELECT curr_hash, prev_hash` 逐行验证 |
| `capacity_metrics` 表 | AI-Modifiable，7 天 TTL | 无需备份（2 天内数据可由 EMA 重算恢复） | 删除重建表 → EMA 冷启动重算 | 对比重建前后 EMA 值误差 < 5% |
| `error_budget` 表 | AI-Modifiable | 每日增量备份 | 从备份恢复 + 重新计算 budget_remaining | 对比恢复前后 response_tier 一致 |
| `token_budget_usage` 表 | AI-Modifiable，7 天 TTL | 无需备份 | 删除重建表 | 无（统计数据，丢失可接受） |
| `.audit_cache/` 目录 | AI-Modifiable | 每日压缩快照到 `.audit_cache_backups/` | 解压最新快照 | `validate_blueprint_provenance.py` |
| 源码树 | Git 管理 | Git + 每 tag 打一个完整快照 | `git checkout` | `mypy` + `ruff` + 全量测试 |
| 蓝图文件 | Git 管理 | Git | `git checkout` | `validate_ssot.py` |
