# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md | §
# [MODULE] zephyr.shared.capacity_governance.model_capacity_probe
# [DOMAIN] D_SHARED
# [DEPENDENCIES]
# [CONSUMERS] zephyr.trading.resource_optimization
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF-016 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""


# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: model_capacity_probe.py
# 层: 算法
# - id: A1
#   name_zh: ① ModelCapacityProbe
#   name_en: ModelCapacityProbe
#   intro: class ModelCapacityProbe 源码 L62-L77
#   desc: 公共方法（定义序）: probe, get_result, mark_unavailable；源码 L62-L77
#   inputs: 无参数
#   outputs: 返回值
#   （注：A1 之后另有 1 个公共定义未列入（含 1 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（2 定义）
#   name_en: public defs
#   intro: ModelCapacityProbe
#   downstream: zephyr.trading.resource_optimization
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ProbeResult:
    model_id: str
    tokens_per_second: float
    avg_latency_ms: float
    error_rate: float
    available: bool


class ModelCapacityProbe:
    def __init__(self) -> None:
        self._results: dict[str, ProbeResult] = {}

    def probe(self, model_id: str, latency_ms: float, tokens: int) -> ProbeResult:
        tps = tokens / (latency_ms / 1000.0) if latency_ms > 0 else 0.0
        result = ProbeResult(model_id, tps, latency_ms, 0.0, tps > 0)
        self._results[model_id] = result
        return result

    def get_result(self, model_id: str) -> ProbeResult | None:
        return self._results.get(model_id)

    def mark_unavailable(self, model_id: str) -> None:
        if model_id in self._results:
            self._results[model_id] = ProbeResult(model_id, 0.0, 0.0, 1.0, False)
