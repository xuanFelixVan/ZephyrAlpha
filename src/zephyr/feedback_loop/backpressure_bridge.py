# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.feedback_loop.backpressure_bridge
# [DOMAIN] D_FEEDBACK_LOOP
# [DEPENDENCIES] zephyr.integration.__init__; zephyr.feedback_loop.__init__
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
# [A_module] module_id=MOD-FEEDBACK_LOOP | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""FLE -> Pipeline 背压桥接（CTR-BP-001~003）

AUDIT-08：在 EvolutionEngine 产出含 CRITICAL 提案时，对 BackpressureManager
发出 THROTTLE，便于 D_DATA->D_FACTOR 数据扇区与「系统 stress」协同降速。

设计
----
- 延迟 import ``zephyr.infrastructure.pipeline.backpressure_manager``，避免 feedback-loop 包被
  import 时强依赖 pipeline（运行时仍单向：FLE -> pipeline）。
- 仅 **CRITICAL** 触发；HIGH/MEDIUM 不扰动全局吞吐（可后续按 signal 类型扩展）。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 进化提案列表与背压管理器
#   fields: proposals（duck-typing 需 severity 属性）；backpressure_manager；symbol
#   code: sync_evolution_proposals_to_backpressure
# 层: 算法
# - id: A1
#   name_zh: CRITICAL 提案过滤
#   name_en: critical_proposal_filter
#   intro: 仅保留 severity is Severity.CRITICAL 的提案；为空或管理器 None 则 skipped 短路
#   code: sync_evolution_proposals_to_backpressure 内列表推导
# - id: A2
#   name_zh: 节流速率换算与下发
#   name_en: throttle_rate_emission
#   intro: rate=clamp(20//critical_count, 1, 50)，延迟 import 后 emit_throttle 到 BackpressureManager
#   code: sync_evolution_proposals_to_backpressure 尾部 emit_throttle 调用
# 层: 输出
# - id: O1
#   name_zh: 桥接结果
#   name_en: bridge_result
#   intro: {"throttled": bool, "critical_count": int, "skipped": bool} dict
#   downstream: zephyr.infrastructure.pipeline.backpressure_manager（D_DATA→D_FACTOR 降速）
# [/ALGO_FLOW]
# 边: I1 --> A1 ; A1 --> A2 ; A2 --> O1
"""

from __future__ import annotations

from typing import Any

__all__ = ["sync_evolution_proposals_to_backpressure"]


def sync_evolution_proposals_to_backpressure(
    proposals: list[Any],
    backpressure_manager: object | None,
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
        from zephyr.feedback_loop.evolution_engine import Severity
    except Exception:  # noqa: BLE001 — 5.135治标: broad exception catch
        return {"skipped": True, "throttled": False, "critical_count": 0}

    critical = [p for p in proposals if getattr(p, "severity", None) is Severity.CRITICAL]
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
