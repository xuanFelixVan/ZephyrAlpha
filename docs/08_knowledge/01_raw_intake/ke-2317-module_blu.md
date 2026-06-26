---
module_id: KE-2223--------8-003
title: 4.2 结构审计维度（8 个核心维度）
category: module_blueprint
ttl: permanent
doc_type: knowledge_entry
---

# 4.2 结构审计维度（8 个核心维度）

4.2 结构审计维度（8 个核心维度）

结构审计是确定性的——规则引擎直接判定 PASS/FAIL，不涉及 AI。

| dim_id | 名称 | 切法 | 审什么 | 核心检查器 | 收敛 |
|--------|------|------|--------|-----------|:---:|
| DIM-TYPE-001 | 脚本文件类型审计 | **横切** | 所有 .py 脚本注册/去重/文档 | audit_registration + code_dedup | 2 |
| DIM-TYPE-002 | 门禁文件类型审计 | **横切** | 所有 gate .yaml 注册/无僵尸 | audit_registration + gate_selfcheck | 2 |
| DIM-TYPE-003 | 规则文件类型审计 | **横切** | 所有规则文件被落实/不过时 | rule_implementation + rule_staleness | 2 |
| DIM-DIR-001 | Governance 目录审计 | **竖切** | scripts/governance/ 结构合规 | dir_structure + cross_file_consistency | 1 |
| DIM-FIELD-001 | Owner 字段唯一性审计 | **字段切** | 所有 YAML 中 owner 有效性 | owner_uniqueness + owner_validity | 1 |
| DIM-RULE-001 | 规则交叉引用审计 | **斜切** | project_rules.md 中每条 RULE 落实证据 | rule_implementation + cross_reference | 2 |
| DIM-DUP-001 | 全量功能重复审计 | **交叉切** | 功能级语义重复 | code_dedup_engine.cluster_analysis | 2 |
| DIM-SSoT-001 | 唯一真源一致性审计 | **交叉切** | 注册表一致性/无冲突 | registry_consistency + ssot_conflict | 2 |
