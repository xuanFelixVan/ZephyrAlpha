---
module_id: AUDIT_BLUEPRINT_D_OVERLAP_TRIAGE_20260413
standard_type: audit_state
generated_by: scripts/audit/triage_blueprint_d_overlap_pairs.py
---

# D 类蓝图重叠 A 档分流报告（F5）

> **生成时间**: 20260413
> **候选对总数**: 400
> **评分阈值**: TIER_A ≥ 0.85，TIER_B ≥ 0.5

## 档位分布

| 档位 | 数量 | 说明 |
|------|------|------|
| TIER_A_AUTO | 12 | score ≥ 0.85，建议 auto-merge / stub（需 Owner 签核） |
| TIER_B_SECOND | 388 | 中等相似，输入二审队列 |
| TIER_C_LOW | 0 | 低相似，暂缓备查 |

## 二审优先级分布

| 优先级 | 数量 |
|--------|------|
| MEDIUM | 356 |
| HIGH | 42 |
| LOW | 2 |

## TIER_A_AUTO（12 对，score ≥ 0.85）

| # | Score | Path A | Path B | Canonical | Priority |
|---|-------|--------|--------|-----------|----------|
| 1 | 0.996 | `…/06_ARCHIVE/human-ai-interface-layer-technical-blueprint.md` | `…/06_ARCHIVE/overlap-human-ai-interface-layer-technical-blueprint-20260407-190203.md` | `overlap-human-ai-interface-layer-technical-blueprint-20260407-190203.md` | LOW |
| 2 | 0.994 | `docs/01_FRAMEWORK/model-registry-blueprint.md` | `…/06_ARCHIVE/overlap-model-registry-blueprint-20260407-190203.md` | `model-registry-blueprint.md` | HIGH |
| 3 | 0.990 | `docs/06_ARCHIVE/reports/overlap-incomplete-blueprint-archive-report-20260404-20260407-190203.md` | `docs/09_AUDIT/REPORTS/incomplete-blueprint-archive-report-20260404.md` | `incomplete-blueprint-archive-report-20260404.md` | HIGH |
| 4 | 0.989 | `…/06_ARCHIVE/overlap-complete-blueprint-20260407-190203.md` | `docs/09_RESEARCH_INNOVATION/_archive/complete-blueprint.md` | `complete-blueprint.md` | HIGH |
| 5 | 0.986 | `docs/06_ARCHIVE/audit_reports/research-workflow-management-blueprint-legacy-p1-cleanup-archive.md` | `docs/10_AI_WORKFLOW/research-workflow-management-blueprint.md` | `research-workflow-management-blueprint.md` | HIGH |
| 6 | 0.969 | `…/06_ARCHIVE/model-performance-version-management-blueprint-legacy-p1-cleanup-archive.md` | `docs/10_AI_WORKFLOW/model-performance-version-management-blueprint.md` | `model-performance-version-management-blueprint.md` | HIGH |
| 7 | 0.931 | `docs/09_AUDIT/STATE/blueprint-d-overlap-candidates-20260411.md` | `docs/09_AUDIT/STATE/blueprint-d-overlap-candidates-20260412.md` | `blueprint-d-overlap-candidates-20260412.md` | HIGH |
| 8 | 0.920 | `docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/data-version-control-blueprint.md` | `…/06_ARCHIVE/data-version-control-blueprint-legacy-p1-cleanup-archive.md` | `data-version-control-blueprint.md` | HIGH |
| 9 | 0.919 | `docs/06_ARCHIVE/duplicates/complete-blueprint-overview-merged.md` | `docs/11_STRATEGIC_DECISION/complete-blueprint-overview.md` | `complete-blueprint-overview.md` | HIGH |
| 10 | 0.900 | `…/06_ARCHIVE/overlap-investment-committee-support-blueprint-20260407-190203.md` | `docs/11_STRATEGIC_DECISION/investment-committee-support-blueprint.md` | `investment-committee-support-blueprint.md` | HIGH |
| 11 | 0.861 | `docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/data-governance-platform-blueprint.md` | `…/06_ARCHIVE/overlap-data-governance-platform-blueprint-20260407-190203.md` | `data-governance-platform-blueprint.md` | HIGH |
| 12 | 0.854 | `docs/01_FRAMEWORK/algorithm-deployment-control-blueprint.md` | `docs/06_ARCHIVE/audit_reports/overlap-algorithm-deployment-control-blueprint-20260407-190202.md` | `algorithm-deployment-control-blueprint.md` | HIGH |

## TIER_B_SECOND（388 对，仅展示 HIGH 优先级 31 条）

| # | Score | Path A | Path B | Canonical | A_arch | B_arch |
|---|-------|--------|--------|-----------|--------|--------|
| 14 | 0.781 | `…/01_FRAMEWORK/mlops-platform-blueprint.md` | `…/blueprints/overlap-mlops-platform-blueprint-20260407-190203.md` | `mlops-platform-blueprint.md` | ✗ | ✓ |
| 40 | 0.687 | `…/01_BLUEPRINTS/risk-contribution-analysis-blueprint.md` | `…/01_BLUEPRINTS/strategy-portfolio-optimization-blueprint.md` | `risk-contribution-analysis-blueprint.md` | ✗ | ✗ |
| 46 | 0.683 | `…/01_BLUEPRINTS/portfolio-attribution-blueprint.md` | `…/01_BLUEPRINTS/portfolio-constraint-management-blueprint.md` | `portfolio-attribution-blueprint.md` | ✗ | ✗ |
| 57 | 0.677 | `…/01_BLUEPRINTS/liquidity-constrained-optimization-blueprint.md` | `…/01_BLUEPRINTS/portfolio-diversification-metric-blueprint.md` | `liquidity-constrained-optimization-blueprint.md` | ✗ | ✗ |
| 79 | 0.670 | `…/01_BLUEPRINTS/multi-objective-optimization-blueprint.md` | `…/01_BLUEPRINTS/portfolio-constraint-management-blueprint.md` | `multi-objective-optimization-blueprint.md` | ✗ | ✗ |
| 85 | 0.668 | `…/01_BLUEPRINTS/data-governance-platform-blueprint.md` | `…/01_BLUEPRINTS/data-mesh-blueprint.md` | `data-governance-platform-blueprint.md` | ✗ | ✗ |
| 100 | 0.663 | `…/01_BLUEPRINTS/multi-period-dynamic-optimization-blueprint.md` | `…/01_BLUEPRINTS/portfolio-optimization-diagnostics-blueprint.md` | `multi-period-dynamic-optimization-blueprint.md` | ✗ | ✗ |
| 127 | 0.653 | `…/01_BLUEPRINTS/multi-objective-optimization-blueprint.md` | `…/01_BLUEPRINTS/portfolio-attribution-blueprint.md` | `portfolio-attribution-blueprint.md` | ✗ | ✗ |
| 145 | 0.649 | `…/01_BLUEPRINTS/portfolio-constraint-management-blueprint.md` | `…/01_BLUEPRINTS/portfolio-optimizer-integration-blueprint.md` | `portfolio-optimizer-integration-blueprint.md` | ✗ | ✗ |
| 168 | 0.645 | `…/01_BLUEPRINTS/execution-strategy-backtester-blueprint.md` | `…/01_BLUEPRINTS/transaction-cost-analysis-engine-blueprint.md` | `transaction-cost-analysis-engine-blueprint.md` | ✗ | ✗ |
| 173 | 0.644 | `…/01_BLUEPRINTS/financing-optimization-blueprint.md` | `…/01_BLUEPRINTS/portfolio-insurance-strategy-blueprint.md` | `financing-optimization-blueprint.md` | ✗ | ✗ |
| 216 | 0.638 | `…/REPORTS/p1-blueprints-batch1-completion-report-20260407.md` | `…/REPORTS/p1-blueprints-batch2-completion-report-20260407.md` | `p1-blueprints-batch2-completion-report-20260407.md` | ✗ | ✗ |
| 223 | 0.638 | `…/blueprints/realtime-risk-monitoring-blueprint-legacy-layer8-64.md` | `…/66_DATA_MANAGEMENT_PLATFORM/data-management-platform-blueprint.md` | `data-management-platform-blueprint.md` | ✓ | ✗ |
| 228 | 0.638 | `…/01_BLUEPRINTS/trading-signal-validator-blueprint.md` | `…/01_BLUEPRINTS/transaction-cost-analysis-engine-blueprint.md` | `transaction-cost-analysis-engine-blueprint.md` | ✗ | ✗ |
| 303 | 0.627 | `…/01_BLUEPRINTS/black-litterman-model-blueprint.md` | `…/01_BLUEPRINTS/risk-parity-strategy-blueprint.md` | `black-litterman-model-blueprint.md` | ✗ | ✗ |
| 306 | 0.626 | `…/01_BLUEPRINTS/portfolio-optimizer-integration-blueprint.md` | `…/01_BLUEPRINTS/portfolio-scenario-analysis-blueprint.md` | `portfolio-optimizer-integration-blueprint.md` | ✗ | ✗ |
| 315 | 0.625 | `…/01_BLUEPRINTS/data-cost-management-blueprint.md` | `…/01_BLUEPRINTS/data-lifecycle-management-blueprint.md` | `data-cost-management-blueprint.md` | ✗ | ✗ |
| 318 | 0.624 | `…/01_BLUEPRINTS/data-governance-platform-blueprint.md` | `…/01_BLUEPRINTS/data-observability-blueprint.md` | `data-governance-platform-blueprint.md` | ✗ | ✗ |
| 323 | 0.624 | `…/01_BLUEPRINTS/data-source-management-blueprint.md` | `…/01_BLUEPRINTS/data-version-control-blueprint.md` | `data-version-control-blueprint.md` | ✗ | ✗ |
| 331 | 0.622 | `…/01_BLUEPRINTS/portfolio-insurance-strategy-blueprint.md` | `…/01_BLUEPRINTS/tail-risk-hedging-blueprint.md` | `portfolio-insurance-strategy-blueprint.md` | ✗ | ✗ |
| 334 | 0.622 | `…/01_BLUEPRINTS/data-governance-platform-blueprint.md` | `…/01_BLUEPRINTS/data-lifecycle-management-blueprint.md` | `data-governance-platform-blueprint.md` | ✗ | ✗ |
| 335 | 0.622 | `…/blueprints/realtime-risk-monitoring-blueprint-legacy-layer8-64.md` | `…/71_AUDIT_LOG_SYSTEM/audit-log-system-blueprint.md` | `audit-log-system-blueprint.md` | ✓ | ✗ |
| 340 | 0.621 | `…/01_BLUEPRINTS/portfolio-attribution-blueprint.md` | `…/01_BLUEPRINTS/portfolio-optimizer-integration-blueprint.md` | `portfolio-optimizer-integration-blueprint.md` | ✗ | ✗ |
| 341 | 0.621 | `…/01_BLUEPRINTS/financing-optimization-blueprint.md` | `…/01_BLUEPRINTS/tail-risk-hedging-blueprint.md` | `financing-optimization-blueprint.md` | ✗ | ✗ |
| 354 | 0.620 | `…/01_BLUEPRINTS/data-source-management-blueprint.md` | `…/blueprints/overlap-data-governance-platform-blueprint-20260407-190203.md` | `data-source-management-blueprint.md` | ✗ | ✓ |
| 355 | 0.620 | `…/01_BLUEPRINTS/algorithmic-trading-optimizer-blueprint.md` | `…/01_BLUEPRINTS/execution-strategy-backtester-blueprint.md` | `algorithmic-trading-optimizer-blueprint.md` | ✗ | ✗ |
| 367 | 0.618 | `…/01_BLUEPRINTS/hierarchical-risk-budget-blueprint.md` | `…/01_BLUEPRINTS/intraday-strategy-blueprint.md` | `intraday-strategy-blueprint.md` | ✗ | ✗ |
| 368 | 0.618 | `…/01_BLUEPRINTS/multi-objective-optimization-blueprint.md` | `…/01_BLUEPRINTS/portfolio-optimizer-integration-blueprint.md` | `portfolio-optimizer-integration-blueprint.md` | ✗ | ✗ |
| 377 | 0.616 | `…/01_BLUEPRINTS/performance-testing-blueprint.md` | `…/01_BLUEPRINTS/stress-testing-blueprint.md` | `performance-testing-blueprint.md` | ✗ | ✗ |
| 391 | 0.613 | `…/01_BLUEPRINTS/portfolio-scenario-analysis-blueprint.md` | `…/01_BLUEPRINTS/transaction-cost-aware-rebalancing-blueprint.md` | `transaction-cost-aware-rebalancing-blueprint.md` | ✗ | ✗ |

_完整列表见 `BLUEPRINT_D_OVERLAP_TRIAGE_20260413.json` 和 `SECOND_PASS_QUEUE_20260413.jsonl`_
