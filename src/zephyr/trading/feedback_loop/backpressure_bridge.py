# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.trading.feedback_loop.backpressure_bridge
# [DOMAIN] D_FEEDBACK_LOOP
# [DEPENDENCIES] zephyr.integration.__init__; zephyr.trading.feedback_loop.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-UNK_backpressure_bridge | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""FLE -> Pipeline 背压桥接（CTR-BP-001~003）

AUDIT-08：在 EvolutionEngine 产出含 CRITICAL 提案时，对 BackpressureManager
发出 THROTTLE，便于 D_DATA->D_FACTOR 数据扇区与「系统 stress」协同降速。

设计
----
- 延迟 import ``zephyr.infrastructure.pipeline.backpressure_manager``，避免 feedback-loop 包被
  import 时强依赖 pipeline（运行时仍单向：FLE -> pipeline）。
- 仅 **CRITICAL** 触发；HIGH/MEDIUM 不扰动全局吞吐（可后续按 signal 类型扩展）。
"""

from __future__ import annotations

from typing import Any

__all__ = ["sync_evolution_proposals_to_backpressure"]


def sync_evolution_proposals_to_backpressure(
    proposals: list[Any],
    backpressure_manager: Any | None,
    *,
    symbol: str = "__fle_global__",
) -> dict[str, Any]:
    """若存在严重进化提案，则对 ``symbol`` 触发节流。

    Parameters
    ----------
    proposals
        ``EvolutionProposal`` 列表（duck-typing：仅需 ``severity`` 属性）。
    backpressure_manager
        ``BackpressureManager`` 实例；为 None 时无操作。

    Returns
    -------
    dict
        ``{"throttled": bool, "critical_count": int, "skipped": bool}``
    """
    if backpressure_manager is None or not proposals:
        return {"skipped": True, "throttled": False, "critical_count": 0}

    try:
        from zephyr.trading.feedback_loop.evolution_engine import Severity
    except Exception:
        return {"skipped": True, "throttled": False, "critical_count": 0}

    critical = [p for p in proposals if getattr(p, "severity", None) == Severity.CRITICAL]
    if not critical:
        return {"skipped": False, "throttled": False, "critical_count": 0}

    from zephyr.infrastructure.pipeline.backpressure_manager import emit_throttle

    n = len(critical)
    rate = max(1, min(50, 20 // max(n, 1)))
    emit_throttle(
        backpressure_manager,
        symbol,
        max_rate_per_sec=rate,
        reason=f"FLE:{n}_critical_evolution_proposals",
    )
    return {"skipped": False, "throttled": True, "critical_count": n}
