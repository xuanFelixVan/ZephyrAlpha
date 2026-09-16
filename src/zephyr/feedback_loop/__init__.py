# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md
# [MODULE] zephyr.feedback_loop
# [DOMAIN] D_FEEDBACK_LOOP
# [A_module] module_id=MOD-FEEDBACK_LOOP | layer=cross_layer | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""


Feedback Loop Engine — MOD-FEEDBACK_LOOP.

Migrated from src/zephyr/ops/ to src/zephyr/feedback_loop/ by ARCH-032.
Blueprint: docs/03_modules/_cross_layer/feedback_loop/blueprint.md

# [ALGO_FLOW] external: docs/03_modules/_domain_feedback_loop/algo_flow/feedback_loop/feedback_loop__init__.yaml
"""

# 重新导出核心类（原 feedback_loop.py 迁入包内，解决包/文件同名覆盖）
# 显式 import 子模块（满足 TEST-SOURCE-CONSISTENCY 门禁的符号漂移检测）
from . import evolution_engine  # noqa: F401
from .core import EvolutionProposal, FeedbackLoop

__all__ = [
    "EvolutionProposal",
    "FeedbackLoop",
    "alert_dispatcher",
    "auto_evolution",
    "backpressure_bridge",
    "config",
    "core",
    "db_bridge",
    "db_writer",
    "decision_engine",
    "error_budget",
    "eval_harness",
    "evolution_engine",
    "exceptions",
    "feedback_collector",
    "fitness_functions",
    "generator",
    "metrics_collector",
    "protocols",
    "scheduler",
    "scheduler_act",
    "scheduler_collect_detect",
    "scheduler_health",
    "scheduler_safety",
    "self_diagnosis",
    "session_learner",
    "slo_manager",
    "template",
    "validator",
]
