# [BLUEPRINT] MOD-CONTEXT_ENGINE | docs/03_modules/_cross_layer/context_engine/blueprint.md
# [MODULE] zephyr.autonomy_core.context.domain_decay_config
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
domain_decay_config.py — 每领域半衰期 (DD105, TASK-019)

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: domain_decay_config.py
# 层: 算法
# - id: A1
#   name_zh: ① DomainDecayConfig
#   name_en: DomainDecayConfig
#   intro: Per-domain halflife table + TTL (DD105).
#   desc: Per-domain halflife table + TTL (DD105).；公共方法（定义序）: get；源码 L60-L70
#   inputs: 无参数
#   outputs: 返回值
#   （注：A1 之后另有 1 个公共定义未列入（含 1 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（2 定义）
#   name_en: public defs
#   intro: DomainDecayConfig
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from dataclasses import dataclass


@dataclass
class DomainDecay:
    domain: str
    halflife_days: float
    ttl_days: float
    decay_mode: str  # "exponential" | "linear"


class DomainDecayConfig:
    """Per-domain halflife table + TTL (DD105)."""

    _HALFLIFE: dict[str, DomainDecay] = {
        "CODE_GEN": DomainDecay("CODE_GEN", halflife_days=60, ttl_days=180, decay_mode="exponential"),
        "OPS_FIX": DomainDecay("OPS_FIX", halflife_days=90, ttl_days=270, decay_mode="exponential"),
        "SECURITY": DomainDecay("SECURITY", halflife_days=30, ttl_days=90, decay_mode="exponential"),
    }

    def get(self, domain: str) -> DomainDecay:
        return self._HALFLIFE.get(domain, DomainDecay(domain, halflife_days=90, ttl_days=365, decay_mode="exponential"))
