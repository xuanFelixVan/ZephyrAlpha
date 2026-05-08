---
module_id: KE-module_blu-4_4______c-003
title: 4.4 触发条件 C：结构缺失
category: module_blueprint
---

# 4.4 触发条件 C：结构缺失

4.4 触发条件 C：结构缺失

| 属性 | 值 |
|------|-----|
| **确定性** | **~97%** — ID 匹配是确定性的，但"该不该有"需要推断 |
| **检测逻辑** | 规则引用的 gate_id → 注册表查找 → 找不到完全匹配 = 触发 |
| **严重度** | RED |
| **可自动修复** | ❌ |

```python
def detect_structural_gaps(refs: ExtractedReferences, registries: RegistryProvider) -> list[GapIssue]:
    """
    核心逻辑：规则说 X，系统有没有 X？
    """
    issues = []

    # Gate ID 缺失
    for gate_id in refs.gate_ids:
        if gate_id not in registries.gate_registry.all_ids():
            # 尝试模糊匹配
            near_matches = registries.gate_registry.fuzzy_search(gate_id)
            issues.append(GapIssue(
                missing_id=gate_id,
                category="gate",
                near_matches=near_matches,
                severity=Severity.RED,
                suggestion=f"规则引用 {gate_id}，未在 _registry.yaml 中注册。可能的匹配：{near_matches}"
            ))

    return issues
```
