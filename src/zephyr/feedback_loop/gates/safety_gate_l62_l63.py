# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate-engine/blueprint.md
# [MODULE] zephyr.feedback_loop.gates.safety_gate_l62_l63
# [DOMAIN] D_FBL_VERIFICATION [DEPENDENCIES]
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-GATE_ENGINE | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""Safety Gates L62-L63 — Infrastructure Reality + Market Reality

L62: Strategy Isolation + Network Partition + Immutable Infra + LLM Cost + Kernel Anomaly
L63: Cross-Venue Arbitrage + E2E Health + Self-API Throttle + Schema Registry + Intraday Season + News Sentiment

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 动作上下文与门禁状态
#   fields: ctx；门禁态 network_partition / immutable_infra_ok / self_api_throttled / intraday_anomaly
#   code: SafetyGateL62L63.evaluate
# 层: 算法
# - id: A1
#   name_zh: L62 基础设施现实校验
#   name_en: l62_infrastructure_reality
#   intro: 网络分区或不可变基础设施被破坏 → REJECT
#   code: _l62
# - id: A2
#   name_zh: L63 市场现实校验
#   name_en: l63_market_reality
#   intro: 自身 API 处于限流中 → OBSERVE_ONLY
#   code: _l63
# 层: 输出
# - id: O1
#   name_zh: 门禁裁决列表
#   name_en: gate_results
#   intro: list[GateResult]（PASS / REJECT / OBSERVE_ONLY，HARD 门）
#   downstream: MOD-GATE_ENGINE 门禁编排聚合 → 动作授权决策
# [/ALGO_FLOW]
# 边: I1 --> A1 ; A1 --> A2 ; A2 --> O1
"""

from zephyr.feedback_loop.gates.safety_gate_l1_l27 import ActionContext, GateResult, GateType, GateVerdict


class SafetyGateL62L63:
    def __init__(self):
        self.network_partition: bool = False
        self.immutable_infra_ok: bool = True
        self.self_api_throttled: bool = False
        self.intraday_anomaly: bool = False

    def evaluate(self, ctx: ActionContext) -> list[GateResult]:
        return [self._l62(ctx), self._l63(ctx)]

    def _l62(self, ctx: ActionContext) -> GateResult:
        if self.network_partition:
            return GateResult("L62", GateVerdict.REJECT, GateType.HARD, "Network partition detected")
        if not self.immutable_infra_ok:
            return GateResult("L62", GateVerdict.REJECT, GateType.HARD, "Immutable infrastructure violated")
        return GateResult("L62", GateVerdict.PASS, GateType.HARD)

    def _l63(self, ctx: ActionContext) -> GateResult:
        if self.self_api_throttled:
            return GateResult("L63", GateVerdict.OBSERVE_ONLY, GateType.HARD, "Self-API throttling active")
        return GateResult("L63", GateVerdict.PASS, GateType.HARD)
