# [A_test] module_id: MOD-GOV_adversarial_ml_experiment | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-339 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.ml_experiment.test_adversarial
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""ML-Experiment Domain 红白对抗测试 (canonical entry point)
=====================================================
Delegates to test_adversarial_ml.py for actual test logic.
This file exists to match the session manifest path convention.
"""

from .test_adversarial_ml import *  # noqa: F403
from .test_adversarial_ml import run_all_attacks

__all__ = ["run_all_attacks"]


def test_delegation_import():
    """验证委托导入成功——确保 test_adversarial_ml 可被访问。"""
    assert run_all_attacks is not None
