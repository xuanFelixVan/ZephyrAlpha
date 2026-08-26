# [BLUEPRINT] MOD-INT-AIROUTE | docs/03_modules/_domain_integration/ai_service_route_matrix/blueprint.md
# [MODULE] zephyr.integration.ai_service_route_matrix
# [DOMAIN] D_INTEGRATION
# [DEPENDENCIES] 无（协议核心纯内存；health_probe/degrade_sink/clock 全注入）
# [CONSUMERS] 运行时装配批（AI 服务分级路由装配 / 成本延迟画像登记 / 故障降级链挂接）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 服务类别词表闭合(local_llm|api|asr|mcp); 服务级别词表闭合(L1|L2|L3); service_id 唯一; 画像单价/延迟非负且 P99≥P50; 路由链非空无重复且服务均已注册; 首选不可用按链降级并标记留痕; 全链不可用 Fail-Closed; 画像查询按 (单价,service_id)/(P50,service_id) 确定性排序; 同输入必同输出
# [MODIFY-GUARD] docs/03_modules/_domain_integration/ai_service_route_matrix/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] AiRouteError(占位 ZA-INT-UNREGISTERED-AI-ROUTE)——空service_id/重复注册/非法画像/未知服务/未知路由/空链/链含未注册服务/全链不可用时抛
# [TESTS] tests/integration/test_ai_service_route_matrix.py
# [A_module] module_id=MOD-INT-AIROUTE | layer=module | stability=evolving | safety=M | ai_autonomy=human_gated
# [TTL] permanent
"""AiServiceRouteMatrix — AI 服务分级路由表（MOD-INT-AIROUTE）。

B14-04762（AUD-DRAFT-001-DIGEST P2 波 P2-W13，CAND-BACL-006，A10）：
AI 服务**分级路由表**（本地 LLM/API/ASR/MCP 四类 + L1/L2/L3 分级）+
**成本延迟画像**（单价/延迟 P50/P99 登记）+ **故障降级链**（首选不可用
→ 按链降级 + 标记留痕，全链不可用 Fail-Closed）。LiteLLM 路由思想——
候选有序、健康注入、降级可观测。

查重分工：llm_bridge=LLM 文本润色桥（本件=多类 AI 服务路由表，不生成文本）；
llm_runtime_gateway=LLM 运行时门禁（本件只做选路不做调用）；local_model/*=
本地模型实现（本件只登记画像不跑模型）。
"""

from __future__ import annotations

import datetime
import logging
from dataclasses import dataclass
from enum import Enum
from typing import Callable, Final

_log = logging.getLogger(__name__)

__all__: Final = [
    "AiRouteError",
    "AiService",
    "AiServiceRouteMatrix",
    "CostProfile",
    "DegradeEvent",
    "RouteDecision",
    "ServiceClass",
    "ServiceLevel",
]


class AiRouteError(Exception):
    """AI 服务路由输入/状态非法（Fail-Closed）。

    未登记错误码-申请中：占位 ZA-INT-UNREGISTERED-AI-ROUTE。
    """


class ServiceClass(str, Enum):
    """AI 服务类别词表（闭合）。"""

    LOCAL_LLM = "local_llm"
    API = "api"
    ASR = "asr"
    MCP = "mcp"


class ServiceLevel(str, Enum):
    """AI 服务级别词表（闭合；L1 首选低延迟，L2 标准，L3 高能力兜底）。"""

    L1 = "L1"
    L2 = "L2"
    L3 = "L3"


@dataclass(frozen=True)
class CostProfile:
    """成本延迟画像（单价/延迟 P50/P99 登记，frozen）。"""

    unit_price_per_1k: float
    latency_p50_ms: float
    latency_p99_ms: float


@dataclass(frozen=True)
class AiService:
    """AI 服务条目（service_id × 类别 × 级别 × 画像，frozen）。"""

    service_id: str
    service_class: ServiceClass
    level: ServiceLevel
    profile: CostProfile


@dataclass(frozen=True)
class RouteDecision:
    """路由决策（首选/降级结果 + 标记，frozen）。"""

    route: str
    service_id: str
    position: int
    degraded: bool
    decided_at: datetime.datetime


@dataclass(frozen=True)
class DegradeEvent:
    """降级留痕事件（告警载荷，frozen）。"""

    route: str
    preferred_id: str
    selected_id: str
    failed_ids: tuple[str, ...]
    raised_at: datetime.datetime


class AiServiceRouteMatrix:
    """AI 服务分级路由表（画像登记 + 健康注入选路 + 降级留痕）。"""

    def __init__(
        self,
        *,
        clock: Callable[[], datetime.datetime] | None = None,
        health_probe: Callable[[str], bool] | None = None,
        degrade_sink: Callable[[DegradeEvent], None] | None = None,
    ) -> None:
        self._clock = clock or datetime.datetime.now
        self._health = health_probe or (lambda _sid: True)  # 缺省全可用
        self._degrade_sink = degrade_sink
        self._services: dict[str, AiService] = {}
        self._routes: dict[str, tuple[str, ...]] = {}

    # ── 内部 ─────────────────────────────────────────────────────────────

    def _service(self, service_id: str) -> AiService:
        svc = self._services.get(service_id)
        if svc is None:
            raise AiRouteError(f"未知服务: {service_id!r}（未注册）")
        return svc

    # ── 服务注册 ──────────────────────────────────────────────────────────

    def register_service(
        self,
        service_id: str,
        service_class: ServiceClass,
        level: ServiceLevel,
        profile: CostProfile,
    ) -> AiService:
        """登记 AI 服务：类别/级别枚举校验 + 画像取值域校验（Fail-Closed）。"""
        if not service_id:
            raise AiRouteError("service_id 为空")
        if service_id in self._services:
            raise AiRouteError(f"service_id 重复: {service_id!r}")
        if not isinstance(service_class, ServiceClass):
            raise AiRouteError(f"非法服务类别: {service_class!r}")
        if not isinstance(level, ServiceLevel):
            raise AiRouteError(f"非法服务级别: {level!r}")
        if profile.unit_price_per_1k < 0:
            raise AiRouteError(f"画像单价为负: {profile.unit_price_per_1k!r}")
        if profile.latency_p50_ms < 0 or profile.latency_p99_ms < 0:
            raise AiRouteError("画像延迟为负")
        if profile.latency_p99_ms < profile.latency_p50_ms:
            raise AiRouteError(
                f"画像 P99({profile.latency_p99_ms}) < P50({profile.latency_p50_ms})"
            )
        svc = AiService(
            service_id=service_id,
            service_class=service_class,
            level=level,
            profile=profile,
        )
        self._services[service_id] = svc
        return svc

    # ── 路由链（故障降级声明） ──────────────────────────────────────────────

    def set_route(self, route: str, chain: tuple[str, ...] | list[str]) -> None:
        """声明路由降级链：链非空、无重复、服务均已注册（Fail-Closed）。"""
        if not route:
            raise AiRouteError("route 名为空")
        chain_t = tuple(chain)
        if not chain_t:
            raise AiRouteError("路由链为空")
        if len(set(chain_t)) != len(chain_t):
            raise AiRouteError(f"路由链含重复服务: {chain_t!r}")
        for sid in chain_t:
            self._service(sid)
        self._routes[route] = chain_t

    def route_chain_of(self, route: str) -> tuple[str, ...]:
        """路由链视图（未知路由 → Fail-Closed）。"""
        chain = self._routes.get(route)
        if chain is None:
            raise AiRouteError(f"未知路由: {route!r}（未声明降级链）")
        return chain

    # ── 选路（健康注入 + 降级标记） ─────────────────────────────────────────

    def select(self, route: str) -> RouteDecision:
        """选路：首选不可用按链降级 + 标记留痕；全链不可用 Fail-Closed。"""
        chain = self.route_chain_of(route)
        failed: list[str] = []
        for position, sid in enumerate(chain):
            try:
                healthy = bool(self._health(sid))
            except Exception:  # noqa: BLE001 — 探针异常按不可用处理不抛
                _log.exception("health_probe 异常: %s（按不可用处理）", sid)
                healthy = False
            if healthy:
                decision = RouteDecision(
                    route=route,
                    service_id=sid,
                    position=position,
                    degraded=position > 0,
                    decided_at=self._clock(),
                )
                if decision.degraded:
                    self._mark_degrade(route, chain[0], sid, tuple(failed))
                return decision
            failed.append(sid)
        raise AiRouteError(
            f"路由 {route!r} 全链不可用: {chain!r}（Fail-Closed 拒绝选路）"
        )

    def _mark_degrade(
        self, route: str, preferred: str, selected: str, failed: tuple[str, ...]
    ) -> None:
        event = DegradeEvent(
            route=route,
            preferred_id=preferred,
            selected_id=selected,
            failed_ids=failed,
            raised_at=self._clock(),
        )
        _log.warning(
            "AI 服务降级: 路由 %s 首选 %s 不可用 -> %s（失败: %s）",
            route, preferred, selected, failed,
        )
        if self._degrade_sink is not None:
            try:
                self._degrade_sink(event)
            except Exception:  # noqa: BLE001 — 留痕不阻断选路
                _log.exception("degrade_sink 留痕失败")

    # ── 画像查询 ──────────────────────────────────────────────────────────

    def services(self, service_class: ServiceClass | None = None) -> tuple[AiService, ...]:
        """服务视图（可按类别过滤；按 service_id 确定性排序）。"""
        if service_class is not None and not isinstance(service_class, ServiceClass):
            raise AiRouteError(f"非法服务类别: {service_class!r}")
        out = [
            s for s in self._services.values()
            if service_class is None or s.service_class is service_class
        ]
        return tuple(sorted(out, key=lambda s: s.service_id))

    def cheapest(self, service_class: ServiceClass) -> AiService:
        """类别内最便宜服务（按 (单价, service_id) 确定性排序）。"""
        candidates = self.services(service_class)
        if not candidates:
            raise AiRouteError(f"类别 {service_class.value!r} 无已注册服务")
        return min(candidates, key=lambda s: (s.profile.unit_price_per_1k, s.service_id))

    def fastest(self, service_class: ServiceClass) -> AiService:
        """类别内延迟最低服务（按 (P50, service_id) 确定性排序）。"""
        candidates = self.services(service_class)
        if not candidates:
            raise AiRouteError(f"类别 {service_class.value!r} 无已注册服务")
        return min(candidates, key=lambda s: (s.profile.latency_p50_ms, s.service_id))
