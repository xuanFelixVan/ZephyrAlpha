# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md
# [MODULE] zephyr.feedback_loop
# [DOMAIN] D_FEEDBACK_LOOP
# [A_module] module_id=MOD-FEEDBACK_LOOP | layer=cross_layer | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""


Feedback Loop Engine — MOD-FEEDBACK_LOOP.

Migrated from src/zephyr/ops/ to src/zephyr/feedback_loop/ by ARCH-032.
Blueprint: docs/03_modules/_cross_layer/feedback_loop/blueprint.md

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: core 子模块符号 2个
#   fields: EvolutionProposal / FeedbackLoop
#   code: core
# 层: 算法
# - id: A1
#   name_zh: ① 包级聚合再导出
#   name_en: zephyr.feedback_loop.__init__
#   intro: Feedback Loop Engine — MOD-FEEDBACK_LOOP.
#   desc: MOD-FEEDBACK_LOOP 包入口，包级聚合再导出并声明 __all__（30项）
#   inputs: I1
#   outputs: zephyr.feedback_loop 包级公共命名空间
#   invariant: 包级导出以 __all__ 声明为准（30项）
# 层: 输出
# - id: O1
#   name_zh: zephyr.feedback_loop 包公共 API
#   name_en: __all__ 30项
#   intro: Feedback Loop Engine — MOD-FEEDBACK_LOOP.——对外统一出口
#   downstream: 见蓝图头 [CONSUMERS] 声明
# [/ALGO_FLOW]
# 边:
# I1 --> A1
# A1 --> O1
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
