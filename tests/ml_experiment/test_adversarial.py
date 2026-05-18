# [BLUEPRINT] DOM-GOV-001 | docs/03_modules/_domain-governance/blueprint.md | §
# [MODULE] tests.ml_experiment.test_adversarial
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
"""ML-Experiment Domain 红白对抗测试 (canonical entry point)
=====================================================
Delegates to test_adversarial_ml.py for actual test logic.
This file exists to match the session manifest path convention.
"""
from .test_adversarial_ml import *  # noqa: F401,F403
from .test_adversarial_ml import run_all_attacks  # noqa: F401

__all__ = ["run_all_attacks"]
