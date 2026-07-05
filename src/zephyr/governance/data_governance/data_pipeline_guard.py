# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md
# [MODULE] zephyr.governance.data_governance.data_pipeline_guard
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS] zephyr.infrastructure.escalation
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] 数据管道完整性检查不可跳过;陈旧数据必须检测
# [MODIFY-GUARD] docs/03_modules/_domain-autonomy_perm/escalation-protocol/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 异常必须包含 context 和 rule_id
# [TESTS] tests/test_escalation_engine.py
# [A_module] module_id=MOD-RES_data_pipeline_guard | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""

Data Pipeline Guard — v0.10.0 数据管道完整性防护: schema validation+row count check+checksum verify。
"""

from __future__ import annotations

import hashlib


class DataPipelineGuard:
    def validate_schema(self, actual_columns: list[str], expected_columns: list[str]) -> list[str]:
        return list(set(expected_columns) - set(actual_columns))

    def verify_checksum(self, data: str, expected: str) -> bool:
        actual = hashlib.sha256(data.encode()).hexdigest()[:8]
        return actual == expected

    def check_row_count(self, actual: int, expected: int, tolerance_pct: int = 5) -> bool:
        if expected == 0:
            return actual == 0
        diff = abs(actual - expected) / expected * 100
        return diff <= tolerance_pct
