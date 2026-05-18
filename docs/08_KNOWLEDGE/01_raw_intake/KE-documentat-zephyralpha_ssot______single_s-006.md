---
module_id: KE-documentat-zephyralpha_ssot______single_s-006
title: ZephyrAlpha SSoT 权威图 (Single Source of Truth Authority Map)
category: documentation
---

# ZephyrAlpha SSoT 权威图 (Single Source of Truth Authority Map)

ZephyrAlpha SSoT 权威图 (Single Source of Truth Authority Map)

> **用途**：定义跨文件受保护字段的权威来源（Authority Source）与合法值集合。
> `scripts/governance/d5_architecture/validate_ssot.py` 使用本文件作为校验规则配置。
> 每次修改本文件需同步更新上述脚本并重新运行验收测试。
> **Stage H（2026-04-25）路径对齐完成**：全部 6 处旧体系 `docs/02_ARCHITECTURE/*` / `docs/09_audit/state/module_id_registry.json` 引用已替换为项目真源；`module_id` 从 `ARCH_SSOT_AUTHORITY_MAP` 迁移为 `STD-SSOT-AUTHORITY-MAP`（符合 file-naming-standard v2.0.1 §四 `STD-*` 命名空间）。
> **v2.0（2026-05-03）**：`docs/09_audit/state/` 已废弃——SQLite DB 迁移至 `data/zalpha_metadata.db`（ADR-0030 §4.1）。上述 Stage H 引用中的 `docs/09_audit/state/module_id_registry.json` 的历史上下文保留于此作为审计追踪。

---
