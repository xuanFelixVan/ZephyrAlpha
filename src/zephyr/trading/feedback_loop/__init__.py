# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md
# [MODULE] zephyr.trading.feedback_loop
# [DOMAIN] D_FEEDBACK_LOOP
# [A_module] module_id=MOD-FEEDBACK_LOOP | layer=cross_layer | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""Feedback Loop Engine — MOD-FEEDBACK_LOOP.

Migrated from src/zephyr/ops/ to src/zephyr/trading/feedback_loop/ by ARCH-032.
Blueprint: docs/03_modules/_cross_layer/feedback_loop/blueprint.md
"""

# 重新导出核心类（原 feedback_loop.py 迁入包内，解决包/文件同名覆盖）
from .core import EvolutionProposal, FeedbackLoop

__all__ = [
    "EvolutionProposal",
    "FeedbackLoop",
'_gen_inherited', 'alert_dispatcher', 'auto_evolution', 'backpressure_bridge', 'config', 'core', 'db_bridge', 'db_writer', 'decision_engine', 'error_budget', 'eval_harness', 'evolution_engine', 'exceptions', 'feedback_collector', 'fitness_functions', 'generator', 'metrics_collector', 'protocols', 'scheduler', 'scheduler_act', 'scheduler_collect_detect', 'scheduler_health', 'scheduler_safety', 'self_diagnosis', 'session_learner', 'slo_manager', 'template', 'validator']
