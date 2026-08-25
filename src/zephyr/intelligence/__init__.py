# [A_module] module_id=MOD-INF-036 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-036 | docs/03_modules/_cross_layer/model-capability-exam/blueprint.md
# [MODULE] zephyr.intelligence
# [INVARIANTS] pending_review
# [MODIFY-GUARD] no structural changes without owner approval
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [CONSUMERS]
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] permanent
"""


Intelligence Domain

模型评估、推理、知识库统一域。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: Python 包导入请求
#   fields: 无数据字段（解释器 import 机制触发，不读任何数据表）
#   code: import zephyr.intelligence
# 层: 算法
# - id: A1
#   name_zh: ① 模块命名空间声明
#   name_en: zephyr.intelligence.__init__
#   intro: Intelligence Domain
#   desc: MOD-INF-036 包入口，模块命名空间声明并声明 __all__（2项）
#   inputs: I1
#   outputs: zephyr.intelligence 包级公共命名空间
#   invariant: 包级导出以 __all__ 声明为准（2项）
# 层: 输出
# - id: O1
#   name_zh: zephyr.intelligence 包公共 API
#   name_en: __all__ 2项
#   intro: Intelligence Domain——对外统一出口
#   downstream: 见蓝图头 [CONSUMERS] 声明
# [/ALGO_FLOW]
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations

# NOTE(P1W10 2026-08-25): scaffold 注册器写入悬空类级 import（stub 期炸全包，
# #ARCH-228/#ARCH-235 同款 bug 复发），按本包"纯模块名导出"约定归一为模块名
# 条目；待各模块实现后从模块 import 类名自然生效，不修改本行。
# NOTE(P1W11 2026-08-25): 同态归一 api_llm_pool / model_drift_detector。
# NOTE(P1W09 2026-08-25): 同态归一 llm_market_interpreter。
__all__: list[str] = [
    "api_llm_pool",
    "llm_market_interpreter",
    "model_drift_detector",
    "llm_fundamental_analysis",
    "agent_memory_architecture",
    "llm_agent_router",
    "episodic_memory_store",
    "local_llm_pool",
]
