---
module_id: KE-095
title: 1.5.1 Tier 1：硬编码枚举值（变更必须同步）
category: documentation
---

# 1.5.1 Tier 1：硬编码枚举值（变更必须同步）

1.5.1 Tier 1：硬编码枚举值（变更必须同步）

以下文件**硬编码了本注册表的枚举值**，注册表任何枚举变更都必须同步更新：

| 文件 | 依赖内容 | 同步要求 |
|------|---------|---------|
| `scripts/governance/check_frontmatter_metadata.py` | 全部枚举（doc_type 27值、status 3值、ttl 5值、safety_level 3值、evolution_policy 3值、governance_family 4值、ai_capability_slot 4值、category 10值、domain 10值、review_status 4值）+ 分阶段必填闸门 + 路径映射规则 | **最高优先级**：枚举变更必须同 commit 更新 |
| `src/zephyr/shared/schemas.py` | TaskStatus 10 值、SafetyLevel 3 值、Classification 3 值、EvolutionPolicy 3 值、TaskNamespace 7 值、AuditSeverity 3 值 | **高优先级**：域 B 枚举变更必须同 commit 更新 |
| `src/zephyr/db/sqlite_schema.py` | DDL CHECK 约束硬编码了 status 10值、namespace 7值、safety_level 3值、classification 3值、evolution_policy 3值 | **高优先级**：DDL 变更需要数据库迁移脚本 |
| `src/zephyr/mcp/knowledge_base_server.py` | `_VALID_CATEGORIES` 10值 | **中优先级**：category 枚举变更必须同步 |
| `src/zephyr/mcp/tool-contracts.yaml` | category enum 10值、task_id 格式引用 §7.2 | **中优先级**：category 枚举变更必须同步 |
| `src/zephyr/kb/kb_repo.py` | KeStatus 10值 + 状态转换表 | **高优先级**：域 C 知识条目状态变更必须同步 |
| `schemas/frontmatter-schema.json` | 全部字段的 JSON Schema 定义（本注册表的自动生成产物） | **自动**：本注册表变更后重新生成 |
