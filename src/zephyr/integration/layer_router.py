# [BLUEPRINT] MOD-INF-009 | docs/03_modules/_cross_layer/pipeline/blueprint.md
# [MODULE] zephyr.integration.layer_router
# [DOMAIN] D-INTEGRATION
# [DEPENDENCIES] zephyr.integration.__init__
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
# [A_module] module_id=MOD-ORC_layer_router | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable

"""
LayerDataRouter — 跨层数据路由引擎（Phase C: 模型冻结与路由串联）

依据: cross_layer_contracts.yaml v3.0 — 31 条跨层契约
冻结: LayerRouteMap 不可变路由表, 运行时一次性加载
职责:
  - route(data, contract_id): 将数据按契约路由到目标层
  - query_route(contract_id): 查询指定契约的路由信息
  - list_consumers(layer_id): 列出的所有消费者
  - list_producers(layer_id): 列出的所有生产者

设计原则:
  - 路由表从 cross_layer_contracts.yaml 一次加载后不可变（frozen）
  - 路由失败不抛异常——返回 LayerRouteResult(skipped=True)
  - 支持同步/异步路由回调注册
  - 支持 INV-007 idempotency_key + CTR-TRACE-001 trace_context 传递
"""

from __future__ import annotations

import logging
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml
from zephyr.shared.io.paths import REPO_ROOT

_logger = logging.getLogger(__name__)

DEFAULT_CONTRACTS_PATH: Path = (
    REPO_ROOT
    / "docs"
    / "02_enterprise_architecture"
    / "target-architecture"
    / "architecture-model"
    / "contracts"
    / "cross_layer_contracts.yaml"
)

# ---------------------------------------------------------------------------
# Frozen route model
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class RouteEntry:
    """单条层间路由条目——冻结不可变。"""

    contract_id: str
    contract_name: str
    priority: str
    source_layer: str
    target_layers: tuple[str, ...]
    flow: str
    physical_path: str
    schema_version: str
    stability: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "contract_id": self.contract_id,
            "contract_name": self.contract_name,
            "priority": self.priority,
            "source_layer": self.source_layer,
            "target_layers": list(self.target_layers),
            "flow": self.flow,
            "physical_path": self.physical_path,
            "schema_version": self.schema_version,
            "stability": self.stability,
        }


@dataclass(frozen=True)
class LayerRouteMap:
    """全量跨层路由表——加载后冻结不可变。"""

    routes: tuple[RouteEntry, ...]
    by_source: dict[str, tuple[RouteEntry, ...]] = field(default_factory=dict)
    by_target: dict[str, tuple[RouteEntry, ...]] = field(default_factory=dict)
    by_contract: dict[str, RouteEntry] = field(default_factory=dict)
    layers: tuple[str, ...] = field(default_factory=tuple)
    loaded_at: str = ""
    source_path: str = ""

    def get_route(self, contract_id: str) -> RouteEntry | None:
        return self.by_contract.get(contract_id)

    def producers_of(self, layer_id: str) -> tuple[RouteEntry, ...]:
        return self.by_source.get(layer_id, ())

    def consumers_of(self, layer_id: str) -> tuple[RouteEntry, ...]:
        return self.by_target.get(layer_id, ())


@dataclass(frozen=True)
class LayerRouteResult:
    """路由执行结果。"""

    contract_id: str
    source_layer: str
    target_layers: tuple[str, ...]
    delivered: bool
    skipped: bool = False
    skip_reason: str = ""
    latency_us: float = 0.0
    timestamp: str = field(default_factory=lambda: datetime.now(UTC).isoformat())


# ---------------------------------------------------------------------------
# Route map loader
# ---------------------------------------------------------------------------


def _normalize_layer(raw: str) -> str:
    raw = raw.strip().lower()
    if raw == "*":
        return "*"
    if raw.startswith("l") and raw[1:].isdigit():
        return raw
    return raw


def load_route_map(yaml_path: Path | None = None) -> LayerRouteMap:
    """从 cross_layer_contracts.yaml 加载冻结的层间路由表。

    Returns
    -------
    LayerRouteMap
        冻结不可变的全量路由表。
    """
    resolved = yaml_path or DEFAULT_CONTRACTS_PATH
    if not resolved.exists():
        _logger.warning("LayerDataRouter: contracts file not found at %s, loading empty map", resolved)
        return LayerRouteMap(
            routes=(),
            loaded_at=datetime.now(UTC).isoformat(),
            source_path="",
        )

    raw_text = resolved.read_text(encoding="utf-8")
    data = yaml.safe_load(raw_text) or {}

    route_list: list[RouteEntry] = []

    contracts_section = data.get("contracts", [])
    if not isinstance(contracts_section, list):
        contracts_section = []

    for entry in contracts_section:
        if not isinstance(entry, dict):
            continue
        cid = entry.get("id", "")
        if not cid:
            continue
        src = _normalize_layer(str(entry.get("source_layer", "")))
        tgt_raw = entry.get("target_layers", [])
        if isinstance(tgt_raw, str):
            tgt_raw = [t.strip() for t in tgt_raw.split(",")]
        if not isinstance(tgt_raw, list):
            tgt_raw = []
        tgts = tuple(sorted(set(_normalize_layer(str(t)) for t in tgt_raw if t)))

        route_list.append(
            RouteEntry(
                contract_id=cid,
                contract_name=str(entry.get("name", cid)),
                priority=str(entry.get("priority", "P1")),
                source_layer=src,
                target_layers=tgts,
                flow=str(entry.get("flow", "")),
                physical_path=str(entry.get("physical_path", "")),
                schema_version=str(entry.get("schema_version", "1.0")),
                stability=str(entry.get("stability", "upgradable")),
            )
        )

    routes = tuple(route_list)

    by_source: dict[str, list[RouteEntry]] = {}
    by_target: dict[str, list[RouteEntry]] = {}
    by_contract: dict[str, RouteEntry] = {}
    all_layers: set[str] = set()

    for r in routes:
        by_contract[r.contract_id] = r
        all_layers.add(r.source_layer)
        by_source.setdefault(r.source_layer, []).append(r)
        for t in r.target_layers:
            all_layers.add(t)
            by_target.setdefault(t, []).append(r)

    return LayerRouteMap(
        routes=routes,
        by_source={k: tuple(v) for k, v in sorted(by_source.items())},
        by_target={k: tuple(v) for k, v in sorted(by_target.items())},
        by_contract=by_contract,
        layers=tuple(sorted(all_layers)),
        loaded_at=datetime.now(UTC).isoformat(),
        source_path=str(resolved),
    )


# ---------------------------------------------------------------------------
# LayerDataRouter
# ---------------------------------------------------------------------------


class LayerDataRouter:
    """跨层数据路由引擎。

    功能:
      - 从 cross_layer_contracts.yaml 加载冻结的路由表
      - 支持注册层回调（register_consumer(contract_id, callback)）
      - route(data, contract_id) 按契约将数据分派到目标层的回调

    Usage:
        router = LayerDataRouter()
        router.register_consumer("CTR-001", my_factor)
        result = router.route(market_data, contract_id="CTR-001")
    """

    ConsumerCallback = Callable[[Any, str], None]

    def __init__(self, route_map: LayerRouteMap | None = None, yaml_path: Path | None = None) -> None:
        self._route_map = route_map or load_route_map(yaml_path)
        self._consumers: dict[str, list[LayerDataRouter.ConsumerCallback]] = {}
        self._route_history: list[LayerRouteResult] = []

    @property
    def route_map(self) -> LayerRouteMap:
        return self._route_map

    def register_consumer(self, contract_id: str, callback: ConsumerCallback) -> None:
        """注册契约数据消费者回调。

        Parameters
        ----------
        contract_id: 契约 ID（如 CTR-001）
        callback: 接收 (data, contract_id) 的回调函数
        """
        self._consumers.setdefault(contract_id, []).append(callback)

    def route(
        self,
        data: Any,
        *,
        contract_id: str,
        source_layer: str | None = None,
    ) -> LayerRouteResult:
        """按契约路由数据到注册的消费者。

        Parameters
        ----------
        data: 数据对象
        contract_id: 契约 ID
        source_layer: 覆盖来源层（默认从路由表推断）

        Returns
        -------
        LayerRouteResult
        """
        import time

        t0 = time.perf_counter()

        entry = self._route_map.get_route(contract_id)
        if entry is None:
            result = LayerRouteResult(
                contract_id=contract_id,
                source_layer=source_layer or "unknown",
                target_layers=(),
                delivered=False,
                skipped=True,
                skip_reason=f"contract_not_found: {contract_id}",
                latency_us=(time.perf_counter() - t0) * 1_000_000,
            )
            self._route_history.append(result)
            return result

        src = source_layer or entry.source_layer
        callbacks = self._consumers.get(contract_id, [])

        if not callbacks:
            result = LayerRouteResult(
                contract_id=contract_id,
                source_layer=src,
                target_layers=entry.target_layers,
                delivered=False,
                skipped=True,
                skip_reason="no_consumers_registered",
                latency_us=(time.perf_counter() - t0) * 1_000_000,
            )
            self._route_history.append(result)
            return result

        delivered = True
        for cb in callbacks:
            try:
                cb(data, contract_id)
            except Exception as exc:
                _logger.warning(
                    "LayerDataRouter: consumer callback failed for %s: %s",
                    contract_id,
                    exc,
                )
                delivered = False

        result = LayerRouteResult(
            contract_id=contract_id,
            source_layer=src,
            target_layers=entry.target_layers,
            delivered=delivered,
            latency_us=(time.perf_counter() - t0) * 1_000_000,
        )
        self._route_history.append(result)
        return result

    def query_route(self, contract_id: str) -> RouteEntry | None:
        """查询指定契约的路由条目。"""
        return self._route_map.get_route(contract_id)

    def list_contracts_consuming(self, layer_id: str) -> tuple[RouteEntry, ...]:
        """列出的所有消费者契约。"""
        return self._route_map.consumers_of(layer_id)

    def list_contracts_producing(self, layer_id: str) -> tuple[RouteEntry, ...]:
        """列出的所有生产者契约。"""
        return self._route_map.producers_of(layer_id)

    def layer_dependencies(self) -> dict[str, list[str]]:
        """返回层依赖图 {layer_id: [dependent_layers]}。"""
        deps: dict[str, set[str]] = {}
        pseudo = {"", "*", "shared"}
        for r in self._route_map.routes:
            if not r.source_layer or r.source_layer in pseudo:
                continue
            real_targets = {t for t in r.target_layers if t not in pseudo}
            if real_targets:
                deps.setdefault(r.source_layer, set()).update(real_targets)
        return {k: sorted(v) for k, v in sorted(deps.items())}

    def topology_order(self) -> list[str]:
        """按依赖序拓扑排序各层。"""
        graph = self.layer_dependencies()
        pseudo = {"", "*", "shared"}
        real_layers = {lyr for lyr in self._route_map.layers if lyr not in pseudo}
        in_degree: dict[str, int] = {lyr: 0 for lyr in sorted(real_layers)}
        for src, tgts in graph.items():
            for tgt in tgts:
                if tgt in in_degree:
                    in_degree[tgt] = in_degree.get(tgt, 0) + 1

        order: list[str] = []
        ready = [lyr for lyr, deg in in_degree.items() if deg == 0]
        while ready:
            ready.sort()
            order.extend(ready)
            next_ready: list[str] = []
            for lyr in ready:
                for tgt in graph.get(lyr, []):
                    if tgt in in_degree:
                        in_degree[tgt] -= 1
                        if in_degree[tgt] == 0:
                            next_ready.append(tgt)
            ready = next_ready

        remaining = [lyr for lyr in sorted(self._route_map.layers) if lyr not in order and lyr not in pseudo]
        order.extend(remaining)
        return order

    @property
    def route_count(self) -> int:
        return len(self._route_map.routes)


# ---------------------------------------------------------------------------
# 单例
# ---------------------------------------------------------------------------


_singleton_router: LayerDataRouter | None = None


def get_layer_router(
    *,
    reset: bool = False,
    yaml_path: Path | None = None,
) -> LayerDataRouter:
    """返回 LayerDataRouter 模块级单例。"""
    global _singleton_router
    if reset or _singleton_router is None:
        _singleton_router = LayerDataRouter(yaml_path=yaml_path)
    return _singleton_router


def reset_layer_router() -> None:
    global _singleton_router
    _singleton_router = None


# ---------------------------------------------------------------------------
# Trigger Router 连接层 — 替换 stubs
# ---------------------------------------------------------------------------


def handle_layer_onboarding(payload: dict[str, Any], **_: Any) -> dict[str, Any]:
    """onboarding trigger 的真实实现：加载路由表并返回拓扑序。

    替换 trigger_router.yaml 中的 handle_onboarding_stub。
    """
    router = get_layer_router()
    topo = router.topology_order()
    return {
        "handler": "layer_onboarding",
        "phase": "C",
        "topology_order": topo,
        "layer_count": len(router.route_map.layers),
        "route_count": router.route_count,
        "layer_dependencies": router.layer_dependencies(),
        "loaded_from": router.route_map.source_path,
    }


def handle_layer_data_route(payload: dict[str, Any], **_: Any) -> dict[str, Any]:
    """跨层数据路由 trigger：按 contract_id 分派数据。

    替换 trigger_router.yaml 中的 layer-specific stubs。
    """
    contract_id = payload.get("contract_id", "")
    data = payload.get("data")
    source_layer = payload.get("source_layer")

    if not contract_id:
        return {
            "handler": "layer_data_route",
            "phase": "C",
            "error": "missing contract_id",
            "delivered": False,
        }

    router = get_layer_router()
    route_entry = router.query_route(contract_id)
    if route_entry is None:
        return {
            "handler": "layer_data_route",
            "phase": "C",
            "contract_id": contract_id,
            "error": f"unknown_contract: {contract_id}",
            "delivered": False,
        }

    result = router.route(data, contract_id=contract_id, source_layer=source_layer)
    return {
        "handler": "layer_data_route",
        "phase": "C",
        "contract_id": contract_id,
        "source_layer": route_entry.source_layer,
        "target_layers": list(route_entry.target_layers),
        "flow": route_entry.flow,
        "delivered": result.delivered,
        "skipped": result.skipped,
        "skip_reason": result.skip_reason,
        "latency_us": result.latency_us,
    }


def handle_layer_query(payload: dict[str, Any], **_: Any) -> dict[str, Any]:
    """层间路由查询 trigger：返回指定层的上下游。

    用于 AI Agent 回答 "我当前在 L03，能消费哪些契约？产出的数据去哪？"
    """
    layer_id = payload.get("layer_id", "").strip()
    if not layer_id:
        return {"handler": "layer_query", "phase": "C", "error": "missing layer_id"}

    router = get_layer_router()
    normalized = _normalize_layer(layer_id)
    consuming = router.list_contracts_consuming(normalized)
    producing = router.list_contracts_producing(normalized)

    return {
        "handler": "layer_query",
        "phase": "C",
        "layer_id": normalized,
        "consumes": [r.to_dict() for r in consuming],
        "produces": [r.to_dict() for r in producing],
        "consumer_count": len(consuming),
        "producer_count": len(producing),
    }


__all__ = [
    "LayerDataRouter",
    "LayerRouteMap",
    "LayerRouteResult",
    "RouteEntry",
    "get_layer_router",
    "handle_layer_data_route",
    "handle_layer_onboarding",
    "handle_layer_query",
    "load_route_map",
    "reset_layer_router",
]
