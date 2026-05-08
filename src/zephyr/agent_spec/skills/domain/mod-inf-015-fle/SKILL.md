---
skill_id: SKILL-DOM-{{MODULE_ABBR}}-{{NUMBER}}
name: "MOD-INF-015；FLE"
description: ""
allowed-tools: [Read, Grep, Glob, Edit, Write, Bash]
model_hint: DeepSeek
freshness_score: 100.0
last_validated: 2026-05-06
version: "0.1.0"
token_budget_l1: 50
token_budget_l2: 500
author: factory-agent
---

# Domain Skill: MOD-INF-015；FLE

## CRITICAL Rules

### Core Operations
# 🆕 L44: Operational Excellence Gate — FLE必须满足自身SLO才允许自主操作
def _check_operational_excellence(self, diagnosis, action_type) -> bool:
    slo = self.fle_self_slo_monitor.evaluate_fle_slo()
    breached = [o for o in slo.objectives if o.status == "BREACHED"]
    if breached and len(breached) >= 2:
        self._log_rejected("L44_OPERATIONAL_EXCELLENCE",
            f"FLE has {len(breached)} breached SLOs: "
            f"{', '.join(o.metric for o in breached[:3])}. "
            f"FLE is not meeting its own service level. All autonomous actions SUSPENDED "
            f"until SLOs recover. Manual override required.")
        return action_type in ("NOTIFY_OWNER",)
    # Check API contract drift: any CRITICAL internal API violations → block self_upgrade
    api_drift = self.fle_internal_api_versioning.verify_all_internal_contracts()
    if api_drift.critical_count > 0 and action_type in ("SELF_UPGRADE",):
        self._log_rejected("L44_OPERATIONAL_EXCELLENCE",
            f"Internal API contract violations ({api_drift.critical_count} CRITICAL). "
            f"Self-upgrade blocked until contracts are re-verified.")
        return False
    # Check chain amplification: recent decisions show >5x cumulative deviation
    recent_amplifications = await self.prompt_chain_amplification.get_recent_amplifications(hours=24)
    if recent_amplifications.halt_count > 0:
        self._log_rejected("L44_OPERATIONAL_EXCELLENCE",
            f"{recent_amplifications.halt_count} decision chains halted due to amplification. "
            f"FLE diagnostic chain reliability compromised. Only NOTIFY_OWNER permitted.")
        return action_type in ("NOTIFY_OWNER",)
    return True

### Unique Constraints
### 2.191 Configuration Complexity Budget Enforcer - config_complexity_budget.py (🆕 v0.17.0 - 盲点239 — 1人可维护性硬约束)

**致命问题**：FLE经过16代进化，configuration surface area（配置项总数、配置间依赖边数、per-tier config组合数）随功能线性/超线性增长。但1人维护者能"心理建模"的配置复杂度存在硬上限（Bus Factor=1的版本）。若无复杂度预算→FLE逐步自行退化到Owner无法理解的"黑箱配置"状态→出问题时Owner无力诊断。
**对标**：Meta Config Complexity Management (paper: "Config Validation at Scale") + AWS Well-Architected Operational Excellence + Unix哲学"Do One Thing Well"

```python
class ConfigComplexityBudgetEnforcer:
    MAX_CONFIG_ITEMS: int = 80  # 1人可理解的配置项硬上限
    MAX_CONFIG_DEPENDENCY_EDGES: int = 120
    MAX_PER_TIER_COMBOS: int = 20
    COMPLEXITY_WARNING_RATIO: float = 0.75  # 达到75%→警告

    async def audit_configuration_surface(self) -> ComplexityReport:
        items = await self._count_config_items()
        edges = await self._count_dependency_edges()
        combos = await self._count_tier_combinations()
        report = ComplexityReport(
            items=items, max_items=self.MAX_CONFIG_ITEMS,
            edges=edges, max_edges=self.MAX_CONFIG_DEPENDENCY_EDGES,
            combos=combos, max_combos=self.MAX_PER_TIER_COMBOS,
            items_ratio=items/self.MAX_CONFIG_ITEMS,
            edges_ratio=edges/self.MAX_CONFIG_DEPENDENCY_EDGES)
        # 预警区
        if report.items_ratio > self.COMPLEXITY_WARNING_RATIO:
            self.FLE.notify_owner("CONFIG_COMPLEXITY_WARNING",
                f"Config items={items}/{self.MAX_CONFIG_ITEMS} ({report.items_ratio:.0%}). "
                f"Approaching 1-human maintainability limit. Consider: config consolidation, "
                f"auto-derived settings (remove manual config), or splitting into simpler subsystems.")
        # 硬上限
        if report.items_ratio >= 1.0 or report.edges_ratio >= 1.0:
            self.FLE.notify_owner("CONFIG_COMPLEXITY_CEILING",
                f"Config complexity ceiling reached. New configuration options BLOCKED "
                f"until old options are consolidated or removed. Items={items}/{self.MAX_CONFIG_ITEMS}, "
                f"Edges={edges}/{self.MAX_CONFIG_DEPENDENCY_EDGES}.")
            self.FLE.lock_new_config_options()
        return report
```

### Common Error Patterns
待填写

## Checklist

- [ ] Verify blueprint before implementation
- [ ] Check upstream dependencies
- [ ] Validate against acceptance criteria
- [ ] Run gate engine checks (G0-G9)

## Key Constants

| Constant | Value | Description |
|----------|-------|-------------|
| DEFAULT_TIMEOUT | 30 | Default operation timeout (seconds) |

## References (L3, on-demand)

- module_blueprint.md
- integration_guide.md
- troubleshooting.md
