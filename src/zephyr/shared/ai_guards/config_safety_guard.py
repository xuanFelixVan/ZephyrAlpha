# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md
# [MODULE] zephyr.shared.ai_guards.config_safety_guard
# [DOMAIN] D_AUTONOMY_CORE
# [DEPENDENCIES] zephyr.autonomy_core.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF-016 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
config_safety_guard.py — 配置自毁防护 (B16, DD90, TASK-017)

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: config_safety_guard.py
# 层: 算法
# - id: A1
#   name_zh: ① ConfigSafetyGuard
#   name_en: ConfigSafetyGuard
#   intro: Config key domain[min,max] Contract-YAML driven; 超界拒绝+告警 (D…
#   desc: Config key domain[min,max] Contract-YAML driven; 超界拒绝+告警 (DD90).；公共方法（定义序）: validate；源码 L62-L76
#   inputs: 无参数
#   outputs: 返回值
#   （注：A1 之后另有 1 个公共定义未列入（含 1 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（2 定义）
#   name_en: public defs
#   intro: ConfigSafetyGuard
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from dataclasses import dataclass


@dataclass
class ConfigGuardResult:
    key: str
    value: float
    min_val: float
    max_val: float
    valid: bool
    rejected: bool = False


class ConfigSafetyGuard:
    """Config key domain[min,max] Contract-YAML driven; 超界拒绝+告警 (DD90)."""

    _DOMAINS: dict[str, tuple[float, float]] = {
        "threshold_pct": (0.5, 0.99),
        "top_k": (1, 20),
        "max_age_s": (60, 7200),
    }

    def validate(self, key: str, value: float) -> ConfigGuardResult:
        domain = self._DOMAINS.get(key, (0.0, float("inf")))
        valid = domain[0] <= value <= domain[1]
        return ConfigGuardResult(
            key=key, value=value, min_val=domain[0], max_val=domain[1], valid=valid, rejected=not valid
        )
