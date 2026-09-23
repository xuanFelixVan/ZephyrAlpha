---
asset_id: "DOC:docs/library/regulations.md"
ttl: "permanent"
doc_type: "index"
---

# 藏书规程（生成视图；真源=directory_contract.yaml + 08 字段词典）

- 本页由 generate_library_index.py 从目录契约真源机械生成，禁手写。
- 资产身份：asset_id（KIND:派生键）永不复用；注销走死亡证明（08 §3.1）。
- 查询总口：`python -m zephyr.library.lookup <关键词>`（T5 支持 kind/owner_domain/tags/status/home 前缀过滤）。

## 目录契约（DCR 约束摘录）

| 目录 | 约束 |
|---|---|
| docs/01_policies_and_standards/ | （doc_type: policy, register, index, template, vocabulary, gate） |
| docs/02_enterprise_architecture/ | （doc_type: architecture_view, blueprint, audit_report, gate, register, index） |
| docs/03_modules/ | （doc_type: blueprint, architecture_view, register, index） |
| docs/08_knowledge/ | （doc_type: vocabulary, index） |
| docs/_archive/ |  |
| architecture_model/ | （doc_type: register） |
| src/zephyr/ |  |
| src/zephyr/data/ | runtime_data_guard |
| scripts/ | （doc_type: policy, index） |
| schemas/ |  |
| config/ |  |
| config/data/ | data_policy_config |
| config/governance/ | governance_tooling_config |
| config/infra/ | deployment_orchestration_config |
| config/runtime/ | runtime_state_file |
| config/system_configs/ | system_native_config |
| tests/ |  |
| session_logs/ | （doc_type: audit_report, index） |
| tools/ |  |
| src/config/ |  |
| docs/02_enterprise_architecture/10_trading_map/ | generated_panorama（doc_type: architecture_view, index） |
| docs/_working/ | task_document |
| docs/_working/audit/ | audit_work_doc |
| docs/_working/research_notes/ | research_note |
| docs/_working/ttl_content_audit/ | ttl_content_audit |
| .runtime/ | runtime_root |
| .runtime/tmp/ | runtime_aux_script |
| .runtime/logs/ | runtime_log |
| .runtime/lookup_audit/ | capability_lookup_audit |
| .runtime/claim_snapshots/ | commit_claim_snapshot |
| .trae/ | ide_tool_root |
| .trae/rules/ | ide_rule_doc |
| docs/ | （doc_type: index） |
| src/ |  |
| data/ |  |
| data/budget/ |  |
| data/circadian_tasks/ |  |
| data/classified/ |  |
| data/governance/ |  |
| data/health_snapshots/ |  |
| data/model_learning/ |  |
| data/security_baselines/ |  |
| data/snapshots/ |  |
| data/architecture_health/ |  |
| data/audit_logs/ |  |
| data/metrics/ |  |
| data/model_profiles/ |  |
| data/test_audit_bridge/ |  |
| data/capability_cards/ |  |
| data/contracts/ |  |
| data/cleanup_log/ |  |
| data/feedback_proposals/ |  |
| data/work_dags/ |  |
| data/databases/ |  |
| data/databases/backups/ |  |
| data/databases/governance_metadata/ |  |
| data/vector_db/ |  |
| data/semantic_test/ |  |
| data/vector_db_e2e_test/ |  |
| data/reports/ |  |
| data/archive/ |  |
| data/cache/ |  |
| data/raw/ |  |
| data/telemetry/ |  |
| data/asset_index/ |  |
| data/asset_index/archive/ |  |
| data/auto_fix/ |  |
| data/backups/ |  |
| data/dream_archive/ |  |
| data/brain/ |  |
| data/models/ |  |
| data/drift_audit/ |  |
| data/drift_baselines/ |  |
| data/drift_checkpoints/ |  |
| data/drift_handoffs/ |  |
| data/drift_runbooks/ |  |
| scripts/_archive/ |  |
| .github/ |  |

## 索书号规范（08 §7）

- .md/.yaml：frontmatter 一行 `asset_id: FILE:docs/...`；.py：头部 `# asset: MOD:...`；二进制不嵌表头（哈希反查）。
- 双向查找：馆→文件=home 字段；文件→馆=表头 asset_id；皆无=blind（编外）。

## 盘数据面流程配方（G15 增补令，Owner 2026-09-23）

- **盘数据面第一步=图书馆双语概念词查询**（`python -m zephyr.library.lookup <概念词>`，中英皆可——别名轴自动归一：融资融券→杠杆→margin_trading）；CH 反向扫只作兜底非替代（R7 轮实证：跳过本步=漏网主因）。
- 标签只用标准词库 REG-TAGVOCAB-001 枚举（zh+en 双语；施工 AI 只能选不能造）；词表 match_tokens 桥接概念词↔表名。

## 血肉编目（ulib3 T8）

- 新资产必填 title_zh（中文名）+plain_zh（大白话）+tags（标准词库 REG-TAGVOCAB-001 枚举）。
- SOP：docs/01_policies_and_standards/sop/library_sop/blood_flesh_cataloging_sop.md。

