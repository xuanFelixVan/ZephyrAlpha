# [BLUEPRINT] MOD-CONTEXT_ENGINE | docs/03_modules/_cross_layer/context_engine/blueprint.md
# [MODULE] zephyr.autonomy_core.context.ce_vibe_shortcuts
# [DOMAIN] D_AUTONOMY_CORE
# [DEPENDENCIES] zephyr.autonomy_core.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-CONTEXT_ENGINE | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
ce_vibe_shortcuts.py — Vibe/Strict 模式切换 (TASK-016)

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: ce_vibe_shortcuts.py
# 层: 算法
# - id: A1
#   name_zh: ① ce_vibe
#   name_en: ce_vibe
#   intro: Switch to vibe mode: expand top_k + lower threshold.
#   desc: Switch to vibe mode: expand top_k + lower threshold.；源码 L79-L81
#   inputs: 无参数
#   outputs: ModeConfig
# - id: A2
#   name_zh: ② ce_strict
#   name_en: ce_strict
#   intro: Switch to strict mode: restore conservative params.
#   desc: Switch to strict mode: restore conservative params.；源码 L84-L86
#   inputs: 无参数
#   outputs: ModeConfig
#   （注：A2 之后另有 2 个公共定义未列入（含 2 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: ModeConfig
#   name_en: ModeConfig
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> A2
# A2 --> O1
"""

from dataclasses import dataclass
from enum import Enum


class CEMode(Enum):
    VIBE = "vibe"
    STRICT = "strict"


@dataclass
class ModeConfig:
    mode: CEMode
    top_k: int
    similarity_threshold: float


_MODE_CONFIGS: dict[CEMode, ModeConfig] = {
    CEMode.VIBE: ModeConfig(mode=CEMode.VIBE, top_k=8, similarity_threshold=0.6),
    CEMode.STRICT: ModeConfig(mode=CEMode.STRICT, top_k=3, similarity_threshold=0.8),
}


def ce_vibe() -> ModeConfig:
    """Switch to vibe mode: expand top_k + lower threshold."""
    return _MODE_CONFIGS[CEMode.VIBE]


def ce_strict() -> ModeConfig:
    """Switch to strict mode: restore conservative params."""
    return _MODE_CONFIGS[CEMode.STRICT]
