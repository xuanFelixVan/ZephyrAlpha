# [A_module] module_id=MOD-RES_escalation_smoke_tests | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain-autonomy_perm/escalation-protocol/blueprint.md

# [MODULE] zephyr.governance.escalation_smoke_tests

# [INVARIANTS] 烟雾测试必须全部通过;9条SMOKE用例不可删减

# [MODIFY-GUARD] docs/03_modules/_domain-autonomy_perm/escalation-protocol/blueprint.md

# [CONSUMERS] zephyr.infrastructure.escalation

# [STABILITY] evolving

# [SAFETY] M

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT] 异常必须包含 context 和 rule_id

# [TESTS] tests/test_escalation_engine.py

"""

Escalation Smoke Tests — v0.11.0 升级协议烟雾测试。
"""

from __future__ import annotations

def test_smoke_engine_init():
    from zephyr.governance.escalation_engine import EscalationEngine
    return True

def test_smoke_delegation_init():
    from zephyr.governance.delegation_manager import DelegationManager
    return True

SMOKE_TESTS=[test_smoke_engine_init, test_smoke_delegation_init]

def run_smoke()->dict:
    results={}
    for t in SMOKE_TESTS:
        try:
            results[t.__name__]=t()
        except Exception as e:
            results[t.__name__]=str(e)
    return results
