---
module_id: KE-module_blu-4_3______b-003
title: 4.3 触发条件 B：系统超越
category: module_blueprint
---

# 4.3 触发条件 B：系统超越

4.3 触发条件 B：系统超越

| 属性 | 值 |
|------|-----|
| **确定性** | **100%** — 数值比较是确定性的 |
| **检测逻辑** | 规则声明 N → 查询当前系统实际值 M → M > N = 触发 |
| **严重度** | YELLOW（系统超越不一定是"规则错了"——可能是系统冗余） |
| **可自动修复** | ❌（需要判断"该改规则还是该裁撤冗余"） |

```python
def detect_system_surpassed(refs: ExtractedReferences, system_state: SystemStateProvider) -> list[SurpassIssue]:
    """
    核心逻辑：规则中的数值 vs 系统当前数值。
    """
    issues = []
    for claim in refs.numeric_claims:
        actual_value = system_state.get_current_value(claim.field_name)
        if actual_value is None:
            continue  # 无法验证 → 跳过
        if actual_value > claim.stated_value:
            issues.append(SurpassIssue(
                field=claim.field_name,
                rule_stated=claim.stated_value,
                actual=actual_value,
                delta=actual_value - claim.stated_value,
                severity=Severity.YELLOW,
                suggestion=f"{claim.field_name}: 规则 {claim.stated_value} → 实际 {actual_value}（增加 {actual_value - claim.stated_value}）"
            ))
    return issues
```

**系统状态注册表**（`system_state_registry.yaml`）——告诉引擎"找什么字段对比"：

```yaml
comparable_fields:
  - field_name: "Phase 0 check count"
    source_module: MOD-INF-027
    query: "len(phase_manager.phase_0_checks)"
  - field_name: "Gate count"
    source_file: "src/zephyr/gates/_registry.yaml"
    query: "count_registry_entries()"
  - field_name: "Script count"
    source_file: "scripts/script_manifest.yaml"
    query: "len(manifest_entries)"
```
