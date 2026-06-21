# [A_module] module_id=MOD-ORC_layer_consumer_registry | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-009 | docs/03_modules/_cross_layer/pipeline/blueprint.md

# [MODULE] zephyr.orchestration.pipeline_routing.layer_consumer_registry

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

"""
LayerConsumerRegistry — Phase D 层消费者注册

为 LayerDataRouter 注册所有 14 层的 contract consumer callbacks。
按拓扑序注册：l13 → l00 → l01 → l02 → l03 → l04 → l05 → l06 → l07 → l08 → l09 → l10 → l11 → l12

P0 主数据流：
  L00源→CTR-001→L02→CTR-002→L03/L04/L05→CTR-003→L05→CTR-004→L06→CTR-005→L07
                                                              ↑CTR-006(反馈)→L04/L11

错误流：     CTR-ERR-001~006 按源→目标层传播
背压流：     CTR-BP-001~003  L02/L03→L00 逆向上游
P1 扩展流： CTR-P1-001~015  跨插各层

注册模式：
  - 每个 callback 接收 (data, contract_id) 并路由到目标层的 handler
  - handler 做最小验证后交给层内部逻辑
  - 未连接的层返回 skipped（Phase E 实现）
"""

from __future__ import annotations

import logging
from typing import Any

from zephyr.integration.layer_router import (
    LayerDataRouter,
    get_layer_router,
    handle_layer_data_route,
    handle_layer_query,
)

_logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Callback 工厂
# ---------------------------------------------------------------------------


def _make_pass_callback(layer_id: str, contract_id: str):
    """生成透传回调——将数据路由到目标层的 handler。"""

    def _callback(data: Any, _contract_id: str) -> None:
        _logger.debug(
            "LayerConsumerRegistry: %s received %s (len=%s)",
            layer_id, contract_id,
            len(str(data)) if data is not None else 0,
        )

    _callback.__name__ = f"_on_{layer_id}_{contract_id.replace('-', '_')}"
    return _callback


def _make_route_forward_callback(target_layer: str, contract_id: str):
    """生成前向路由回调——将数据继续路由到下游层。

    例如：L03 收到 CTR-001 后，可以继续触发 CTR-002 路由。
    """

    def _callback(data: Any, _contract_id: str) -> None:
        router = get_layer_router()
        downstream = _DOWNSTREAM_MAP.get(contract_id)
        if downstream:
            for next_ctr in downstream:
                try:
                    router.route(data, contract_id=next_ctr, source_layer=target_layer)
                except Exception as exc:
                    _logger.warning("Forward route %s -> %s failed: %s", contract_id, next_ctr, exc)

    _callback.__name__ = f"_forward_{target_layer}_{contract_id.replace('-', '_')}"
    return _callback


# ---------------------------------------------------------------------------
# 下游转发映射（contract_id → [下游 contract_ids]）
# 定义主数据流管道
# ---------------------------------------------------------------------------

_DOWNSTREAM_MAP: dict[str, list[str]] = {
    "CTR-001": ["CTR-002"],
    "CTR-002": ["CTR-P1-015"],
    "CTR-P1-015": ["CTR-003", "CTR-004"],
    "CTR-004": ["CTR-005", "CTR-006"],
    "CTR-005": ["CTR-P1-006", "CTR-P1-007"],
    "CTR-006": ["CTR-P1-008"],
}

# ---------------------------------------------------------------------------
# 注册表定义：layer_id → [(contract_id, callback)]
# 按拓扑序排列（l13 无消费者）
# ---------------------------------------------------------------------------

_REGISTRY_DEFINITION: dict[str, list[tuple[str, Any]]] = {
    # L00 — 数据接入层（消费者：背压信号）
    "l00": [
        ("CTR-BP-001", None),
        ("CTR-BP-002", None),
        ("CTR-BP-003", None),
    ],
    # L01 — 基础设施层（消费者：遥测配置）
    "l01": [
        ("CTR-P1-013", None),
    ],
    # L02 — Alpha 因子层（P0 消费者）
    "l02": [
        ("CTR-001", None),
        ("CTR-TRACE-001", None),
        ("CTR-ERR-001", None),
        ("CTR-P1-010", None),
    ],
    # L03 — 信号生成层
    "l03": [
        ("CTR-001", None),
        ("CTR-002", None),
        ("CTR-TRACE-001", None),
        ("CTR-ERR-002", None),
        ("CTR-P1-002", None),
        ("CTR-P1-004", None),
        ("CTR-P1-005", None),
        ("CTR-P1-010", None),
    ],
    # L04 — 风险管理层
    "l04": [
        ("CTR-002", None),
        ("CTR-006", None),
        ("CTR-TRACE-001", None),
        ("CTR-ERR-003", None),
        ("CTR-P1-010", None),
        ("CTR-P1-012", None),
        ("CTR-P1-013", None),
        ("CTR-P1-015", None),
    ],
    # L05 — 组合构建层（最大消费者）
    "l05": [
        ("CTR-002", None),
        ("CTR-003", None),
        ("CTR-TRACE-001", None),
        ("CTR-ERR-003", None),
        ("CTR-ERR-004", None),
        ("CTR-ERR-005", None),
        ("CTR-P1-002", None),
        ("CTR-P1-003", None),
        ("CTR-P1-004", None),
        ("CTR-P1-005", None),
        ("CTR-P1-010", None),
        ("CTR-P1-011", None),
        ("CTR-P1-015", None),
    ],
    # L06 — 交易执行层
    "l06": [
        ("CTR-004", None),
        ("CTR-TRACE-001", None),
        ("CTR-ERR-004", None),
        ("CTR-P1-010", None),
        ("CTR-P1-012", None),
        ("CTR-P1-013", None),
    ],
    # L07 — 盘后分析层
    "l07": [
        ("CTR-005", None),
        ("CTR-006", None),
        ("CTR-TRACE-001", None),
        ("CTR-ERR-005", None),
        ("CTR-P1-001", None),
        ("CTR-P1-006", None),
        ("CTR-P1-007", None),
        ("CTR-P1-010", None),
        ("CTR-P1-011", None),
        ("CTR-P1-013", None),
    ],
    # L08 — 人机交互层
    "l08": [
        ("CTR-P1-008", None),
        ("CTR-P1-009", None),
        ("CTR-P1-010", None),
        ("CTR-P1-011", None),
    ],
    # L09 — 研究创新层
    "l09": [
        ("CTR-001", None),
        ("CTR-P1-010", None),
        ("CTR-P1-014", None),
    ],
    # L10 — 合规层（含自消费 CTR-P1-012）
    "l10": [
        ("CTR-P1-006", None),
        ("CTR-P1-009", None),
        ("CTR-P1-010", None),
        ("CTR-P1-011", None),
        ("CTR-P1-012", None),
        ("CTR-P1-013", None),
    ],
    # L11 — ML 平台层
    "l11": [
        ("CTR-006", None),
        ("CTR-TRACE-001", None),
        ("CTR-P1-010", None),
        ("CTR-P1-014", None),
    ],
    # L12 — 系统遥测层（自消费 CTR-P1-013）
    "l12": [
        ("CTR-P1-010", None),
        ("CTR-P1-013", None),
    ],
    # L13 — 实验管线层（无消费者）
}

# ---------------------------------------------------------------------------
# 注册函数
# ---------------------------------------------------------------------------


def _build_callback(layer_id: str, contract_id: str) -> Any:
    """为层+契约构建合适的回调。

    规则：
      - 数据契约（CTR-001~006, CTR-P1-*）: 使用 _make_pass_callback
      - Trace 契约（CTR-TRACE-001）: 透传
      - 错误契约（CTR-ERR-*）: 使用 _make_pass_callback
      - 背压契约（CTR-BP-*）: 使用 _make_pass_callback（Phase E 实现背推逻辑）
    """
    if contract_id.startswith("CTR-BP-"):
        return _make_pass_callback(layer_id, contract_id)
    return _make_pass_callback(layer_id, contract_id)


def register_all_consumers(router: LayerDataRouter | None = None) -> dict[str, int]:
    """在 LayerDataRouter 上注册所有 14 层的消费者回调。

    按拓扑序注册：l13 → l00 → l01 → l02 → l03 → l04 → l05 → l06 → l07 → l08 → l09 → l10 → l11 → l12

    Returns
    -------
    dict[layer_id, registered_count]
        每层成功注册的消费者数量。
    """
    if router is None:
        router = get_layer_router()

    topo = router.topology_order()
    results: dict[str, int] = {}

    registered_total = 0

    for layer_id in topo:
        if layer_id not in _REGISTRY_DEFINITION:
            continue

        count = 0
        for contract_id, _ in _REGISTRY_DEFINITION[layer_id]:
            callback = _build_callback(layer_id, contract_id)
            router.register_consumer(contract_id, callback)
            count += 1
            registered_total += 1

        results[layer_id] = count

    _logger.info(
        "LayerConsumerRegistry: registered %d consumer callbacks across %d layers",
        registered_total, len(results),
    )
    return results


def register_for_layer(router: LayerDataRouter, layer_id: str) -> int:
    """为指定层注册消费者回调。

    Returns
    -------
    int
        注册的消费者数量。
    """
    if layer_id not in _REGISTRY_DEFINITION:
        _logger.warning("LayerConsumerRegistry: no registry definition for layer %s", layer_id)
        return 0

    count = 0
    for contract_id, _ in _REGISTRY_DEFINITION[layer_id]:
        callback = _build_callback(layer_id, contract_id)
        router.register_consumer(contract_id, callback)
        count += 1

    _logger.info("LayerConsumerRegistry: %s registered %d consumers", layer_id, count)
    return count


def get_registry_summary() -> dict[str, Any]:
    """返回注册表摘要（consumer 数 × 层）。"""
    summary: dict[str, Any] = {
        "total_contracts_registered": sum(len(v) for v in _REGISTRY_DEFINITION.values()),
        "total_layers": len(_REGISTRY_DEFINITION),
        "layers": {},
    }
    for layer_id, entries in _REGISTRY_DEFINITION.items():
        p0_count = sum(1 for cid, _ in entries if cid.startswith("CTR-") and not cid.startswith("CTR-P1-") and not cid.startswith("CTR-BP-") and not cid.startswith("CTR-ERR-"))
        err_count = sum(1 for cid, _ in entries if cid.startswith("CTR-ERR-"))
        bp_count = sum(1 for cid, _ in entries if cid.startswith("CTR-BP-"))
        p1_count = sum(1 for cid, _ in entries if cid.startswith("CTR-P1-"))
        summary["layers"][layer_id] = {
            "total": len(entries),
            "P0_data": p0_count,
            "P1_extension": p1_count,
            "error": err_count,
            "backpressure": bp_count,
        }
    return summary


__all__ = [
    "register_all_consumers",
    "register_for_layer",
    "get_registry_summary",
    "_REGISTRY_DEFINITION",
]
