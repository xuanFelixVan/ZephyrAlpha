---
module_id: AUDIT_FIX_DEAD_LINKS_20260416
standard_type: audit_state
generated_by: scripts/audit/fix_dead_links.py
---

# 断链修复报告（dry-run）

> **生成时间**: 20260416
> **断链总数**: 2483

## 操作统计

| 操作 | 数量 |
|------|------|
| REPLACE | 1321 |
| REMOVE_LINK | 1162 |

## 策略命中分布

| 策略 | 数量 |
|------|------|
| global_unique_basename | 1182 |
| directory_guided_nav | 124 |
| global_closest_basename | 15 |

## 置信度分布（仅 REPLACE）

| 置信度 | 数量 |
|--------|------|
| medium | 1306 |
| low | 15 |

## 高置信修复样本（共 0 条，展示前 30）


## 无法自动修复（REMOVE_LINK，共 1162 条，展示前 30）

- `data/assessments/INDEX.md`: `../../docs/05_IMPLEMENTATION/04_OPERATIONS/audit_state/`
- `docs/00_OVERVIEW/INDEX.md`: `../01_FRAMEWORK/blueprint-stage-complete-supplement-plan.md`
- `docs/01_FRAMEWORK/integrated_from_Layer_1_数据源层/INDEX.md`: `../../06_ARCHIVE/reports/overlap-deep-review-report-20260407-20260407-190203.md`
- `docs/01_GOVERNANCE/REGISTERS/folder-charters/01_FRAMEWORK_CHARTER.md`: `../../02_ARCHITECTURE/BLUEPRINT_DOMAIN_INVENTORY.yaml`
- `docs/01_GOVERNANCE/REGISTERS/folder-charters/01_FRAMEWORK_CHARTER.md`: `../../subsystem-registry.yaml`
- `docs/01_GOVERNANCE/REGISTERS/folder-charters/02_FACTOR_LIBRARY_CHARTER.md`: `../../08_KNOWLEDGE/FACTOR_LIBRARY/`
- `docs/01_GOVERNANCE/REGISTERS/folder-charters/05_IMPLEMENTATION_CHARTER.md`: `../../subsystem-registry.yaml`
- `docs/01_GOVERNANCE/REGISTERS/folder-charters/09_AUDIT_CHARTER.md`: `../../../scripts/audit/purge_expired_state.py`
- `docs/01_GOVERNANCE/REGISTERS/folder-charters/09_AUDIT_CHARTER.md`: `../../../scripts/governance/generate_project_health_dashboard.py`
- `docs/01_GOVERNANCE/REGISTERS/folder-charters/INDEX.md`: `../../subsystem-registry.yaml`
- `docs/03_TRADING_TACTICS/integrated_from_Layer_3_策略层/INDEX.md`: `../../06_ARCHIVE/reports/overlap-batch-fix-progress-report-20260407-20260407-190203.md`
- `docs/03_TRADING_TACTICS/integrated_from_Layer_3_策略层/INDEX.md`: `../../05_IMPLEMENTATION/04_OPERATIONS/audit_state/portfolio-optimization-deep-audit-round2-report-20260407.md`
- `docs/03_TRADING_TACTICS/integrated_from_Layer_3_舆情分析层/INDEX.md`: `../../05_IMPLEMENTATION/04_OPERATIONS/audit_state/sentiment-analysis-deep-audit-report-v16-20260407.md`
- `docs/04_EXECUTION/INDEX.md`: `../06_ARCHIVE/blueprints/data-version-control-blueprint-legacy-layer4-ml.md`
- `docs/04_EXECUTION/INDEX.md`: `../06_ARCHIVE/01_FRAMEWORK/LAYER4_ML/deep-audit-report-v3-20260407.md`
- `docs/04_EXECUTION/INDEX.md`: `../06_ARCHIVE/blueprints/overlap-missing-modules-blueprint-20260407-190202.md`
- `docs/04_EXECUTION/INDEX.md`: `../06_ARCHIVE/blueprints/overlap-p1-p2-modules-blueprint-collection-20260407-190203.md`
- `docs/04_EXECUTION/integrated_from_layer_4/INDEX.md`: `../../05_IMPLEMENTATION/04_OPERATIONS/audit_state/deep-audit-report-v2-20260407.md`
- `docs/04_EXECUTION/integrated_from_Layer_6_组合优化层/INDEX.md`: `../../06_ARCHIVE/blueprints/benchmark-management-blueprint-legacy-11-strategic-decision.md`
- `docs/04_EXECUTION/integrated_from_Layer_6_组合优化层/INDEX.md`: `../../06_ARCHIVE/reports/overlap-p0-p1-fix-report-20260407-20260407-190203.md`
- `docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/00_MANAGEMENT/CANON/ARCHIVE/repo-wide-file-governance-task-list.md`: `../../../../../09_AUDIT/STATE/INDEX_HEALTH_ORPHAN_20260410.json`
- `docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/INDEX.md`: `../../../../.audit_fix_backup/docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/strategy-selection-blueprint.md`
- `docs/07_AI_REPORTING/INDEX.md`: `../01_FRAMEWORK/ai-memory-architecture-completeness-analysis.md`
- `docs/07_AI_REPORTING/INDEX.md`: `../01_FRAMEWORK/ai-memory-supplement-completion-report.md`
- `docs/07_AI_REPORTING/integrated_from_layer_6/INDEX.md`: `../../06_ARCHIVE/audit_reports/layer6-deep-audit-report-20260407-legacy-layer6-reports-archive.md`
- `docs/07_AI_REPORTING/integrated_from_Layer_7_AI报告层/INDEX.md`: `../../06_ARCHIVE/blueprints/market-regime-detection-blueprint-legacy-10-ai-workflow.md`
- `docs/07_AI_REPORTING/integrated_from_Layer_7_AI报告层/INDEX.md`: `../../06_ARCHIVE/blueprints/strategy-lifecycle-management-blueprint-legacy-p1-cleanup-archive.md`
- `docs/08_HUMAN_AI_INTERFACE/index.md`: `../01_FRAMEWORK/human-ai-interface-layer-gap-analysis-blueprint.md`
- `docs/08_HUMAN_AI_INTERFACE/integrated_from_Layer_8_人机交互层/INDEX.md`: `../../06_ARCHIVE/blueprints/disaster-recovery-blueprint-legacy-01-framework.md`
- `docs/08_HUMAN_AI_INTERFACE/integrated_from_Layer_8_人机交互层/INDEX.md`: `../../05_IMPLEMENTATION/04_OPERATIONS/audit_state/optimization-report-20260407.md`