---
blueprint_id: MOD-INF-019
---

# L3 Reference: Test Patterns

> Belongs to: implementer (SKILL-ROL-IMP-001)
> Rule: "Write tests alongside implementation" (implementer CRITICAL Rule #4)

## Test File Placement

```
tests/
├── unit/           # pytest, one file per module, no external dependencies
├── integration/    # pytest, cross-module interaction tests
├── adversarial/    # 红白对抗: attack surface tests, prompt injection, adversarial inputs
└── e2e/            # End-to-end cross-system simulation, use markers for slow tests
```

## Test Naming Convention

- Unit: `test_{module_name}.py` → class `Test{Feature}` → method `test_{scenario_description}`
- Integration: `test_{component1}_{component2}_integration.py`
- Adversarial: `test_{target}_adversarial.py` with attack vector documentation

## Minimum Test Patterns

```python
import pytest

class TestNewFeature:
    def test_happy_path(self):
        """正常输入 → 预期输出."""
        result = function_under_test(valid_input)
        assert result.status == "success"

    def test_empty_input(self):
        """空输入 → 应有明确行为（拒绝或默认）."""
        with pytest.raises(ValueError):
            function_under_test("")

    def test_malformed_input(self):
        """畸形输入 → 不应崩溃."""
        result = function_under_test("\\x00\\x01\\xFF")
        assert result is not None  # 至少不崩
```

## Required Coverage per Module

| Module Type | Min Coverage | Required Test Types |
|------------|-------------|--------------------|
| Data model | 90% | happy_path, validation, serialization |
| Service/Engine | 75% | happy_path, error_path, empty_input |
| Integration bridge | 60% | happy_path, graceful_degradation |
| Stub | 30% | import_check (at minimum) |
