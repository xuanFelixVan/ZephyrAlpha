---
module_id: KE-module_blu-opa_test-003
title: 类似 OPA test——断言路由策略正确性
category: module_blueprint
---

# 类似 OPA test——断言路由策略正确性

类似 OPA test——断言路由策略正确性
POLICY_TESTS: list[PolicyTestCase] = [
    PolicyTestCase(
        input={"task_type": "AUDIT", "priority": "P0"},
        expected_route="M3",
        expected_model="deepseek",
    ),
    PolicyTestCase(
        input={"task_type": "DOC_WRITE", "target_layer": "L00"},
        expected_route="M5",
        expected_model="glm",
    ),
    # ... 覆盖所有7条路由规则+edge cases
]

async def run_policy_tests() -> dict:
    """执行所有策略测试→返回 pass/fail 报告"""
```
