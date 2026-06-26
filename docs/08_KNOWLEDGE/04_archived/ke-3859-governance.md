---
module_id: KE-3708
title: 强制集成清单（每项新功能产出后 MUST 执行）
category: governance_rule
ttl: permanent
doc_type: knowledge_entry
---

# 强制集成清单（每项新功能产出后 MUST 执行）

强制集成清单（每项新功能产出后 MUST 执行）

| 产出类型 | 必须集成到 |
|----------|-----------|
| 新 `.py` 脚本（`scripts/` 下） | `script-manifest.yaml` 注册 + `phase_manager` gate 引用 |
| 新 `.py` 模块（`src/zephyr/` 下） | 对应 `__init__.py` 导出 + 至少一个 import 引用点 |
| 新门禁/gate | `phase_manager.py` PHASE_SEQUENCE 注册 + `task-card-template.md` 文档 |
| 新设计模式/方法论 | `project_rules.md` 或 `AGENTS.md` + **`_index.yaml` TRAE 域** | 人工 review |
| 新增 RULE-* 到 `project_rules.md` | **`_index.yaml` TRAE 域强制登记** — 不登记 = 违规 | `python scripts/governance/sync_rule_registry.py` 自动校验 |
| 新配置/数据文件 | 使用方代码中的显式路径引用 |
| 新 CLI 工具 | `script-manifest.yaml` + 用法写入相关 blueprint |
