---
module_id: KE-668------single-s-006
status: active
title: ZephyrAlpha SSoT 权威图 (Single Source of Truth Authority Map)
category: documentation
ttl: permanent
doc_type: knowledge_entry
---

# ZephyrAlpha SSoT 权威图 (Single Source of Truth Authority Map)

ZephyrAlpha SSoT 权威图 (Single Source of Truth Authority Map)

> **用途**：定义跨文件受保护字段的权威来源（Authority Source）与合法值集合。
> `scripts/governance/d5_architecture/validate_ssot.py` 使用本文件作为校验规则配置。
> 每次修改本文件需同步更新上述脚本并重新运行验收测试。
> **Stage H（2026-04-25）路径对齐完成**：全部 6 处旧体系 `docs/02_ARCHITECTURE/*` / `docs/_working/audit/state/module_id_registry.json` 引用已替换为项目真源；`module_id` 从 `ARCH_SSOT_AUTHORITY_MAP` 迁移为 `STD-SSOT-AUTHORITY-MAP`（符合 file-naming-standard v2.0.1 §四 `STD-*` 命名空间）。
> **v2.0（2026-05-03）**：`docs/_working/audit/state/` 已废弃——SQLite DB 迁移至 `data/databases/governance.db`（KBG-0030 §4.1）。上述 Stage H 引用中的 `docs/_working/audit/state/module_id_registry.json` 的历史上下文保留于此作为审计追踪。

---
