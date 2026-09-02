# [BLUEPRINT] MOD-INF-073 | docs/03_modules/_domain_integration/external_system_connector/blueprint.md
# [MODULE] zephyr.integration.external_system_connector
# [DOMAIN] D_INTEGRATION
# [DEPENDENCIES] 无（契约核心纯内存；health_probe/breaker_factory/clock 全注入）
# [CONSUMERS] 运行时装配批（miniQMT 通道/各数据源 connector 实例登记 / health_probe 真实绑定 / 配额参数 config 加载）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] connector_id 唯一; operations 非空; 配额 rate/daily 双维计数(注入时钟分桶)超限 Fail-Closed; 每连接器登记即挂接熔断器(factory 注入不重建); probe 异常映射 UNHEALTHY 不抛; callable=健康非UNHEALTHY 且熔断非OPEN 且配额未触顶; callable_connectors 按 connector_id 确定性排序
# [MODIFY-GUARD] docs/03_modules/_domain_integration/external_system_connector/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ExternalConnectorError/ConnectorAlreadyRegisteredError/ConnectorNotFoundError/QuotaExceeded(占位 ZA-INT-UNREGISTERED-EXT-CONNECTOR)——空id/重复注册/未知连接器/非法配额/超限时抛
# [TESTS] tests/integration/test_external_system_connector.py
# [A_module] module_id=MOD-INF-073 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
"""ExternalSystemConnector — 统一外部系统连接器契约（MOD-INF-073）。

B1-00326（AUD-DRAFT-001-DIGEST P1 波 W-P1-25，CAND-BACL-003，跨域元文档
§功能域模块·D-INTEGRATION）：券商（miniQMT 通道）与数据源的**统一外部
连接器契约层**——能力声明（行情/交易/另类）+ 健康检查 + 配额管理 +
source_circuit_breaker 挂接 + 统一登记注册表。

查重分工（蓝图 §0）：vendor_registry=行情域内注册（不替代）；
failover_coordinator=运行时选源切换（本件=登记与契约，选源归 failover）；
source_circuit_breaker=单源熔断器（本件挂接复用，DI 工厂注入）；
broker_api_connector=券商执行通道（本件=契约登记面，不直接下单）。
"""

from __future__ import annotations

import datetime
import logging
from dataclasses import dataclass, replace
from enum import Enum
from typing import Any, Callable, Final, Protocol

_log = logging.getLogger(__name__)

__all__: Final = [
    "ConnectorAlreadyRegisteredError",
    "ConnectorCapability",
    "ConnectorKind",
    "ConnectorNotFoundError",
    "ConnectorProfile",
    "ExternalConnectorError",
    "ExternalSystemConnector",
    "HealthStatus",
    "QuotaExceeded",
    "QuotaPolicy",
]


class ExternalConnectorError(Exception):
    """外部连接器契约输入非法（Fail-Closed）。

    未登记错误码-申请中：占位 ZA-INT-UNREGISTERED-EXT-CONNECTOR。
    """


class ConnectorAlreadyRegisteredError(ExternalConnectorError):
    """connector_id 重复注册。"""


class ConnectorNotFoundError(ExternalConnectorError):
    """未知 connector_id。"""


class QuotaExceeded(ExternalConnectorError):
    """配额超限（rate/daily 任一触顶）。"""


class ConnectorKind(str, Enum):
    """连接器类别（能力声明一维）。"""

    MARKET_DATA = "market_data"
    TRADING = "trading"
    ALT_DATA = "alt_data"


class HealthStatus(str, Enum):
    """健康状态。"""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class ConnectorCapability:
    """能力声明：类别 + 操作集 + vendor 标识。"""

    kind: ConnectorKind
    operations: frozenset[str]
    vendor: str

    def __post_init__(self) -> None:
        if not isinstance(self.kind, ConnectorKind):
            raise ExternalConnectorError(f"非法连接器类别: {self.kind!r}")
        if not self.operations:
            raise ExternalConnectorError("operations 为空（能力声明须非空）")
        if not self.vendor:
            raise ExternalConnectorError("vendor 标识为空")


@dataclass(frozen=True)
class QuotaPolicy:
    """配额策略：每秒速率 + 日累计上限（None=不限）。"""

    rate_per_sec: float | None = None
    daily_cap: int | None = None

    def __post_init__(self) -> None:
        if self.rate_per_sec is not None and self.rate_per_sec <= 0:
            raise ExternalConnectorError("rate_per_sec 须为正")
        if self.daily_cap is not None and self.daily_cap <= 0:
            raise ExternalConnectorError("daily_cap 须为正")


@dataclass(frozen=True)
class ConnectorProfile:
    """连接器档案（注册表对外只读视图）。"""

    connector_id: str
    capability: ConnectorCapability
    quota: QuotaPolicy | None
    health: HealthStatus
    registered_at: datetime.datetime


class _BreakerLike(Protocol):
    """source_circuit_breaker 最小外观（DI 工厂产物契约）。"""

    is_open: bool

    def record(self, ok: bool) -> Any: ...


@dataclass
class _Entry:
    """注册表内部条目（配额计数可变）。"""

    profile: ConnectorProfile
    breaker: _BreakerLike | None
    sec_bucket: int = -1  # 当前秒桶（epoch 秒）
    sec_used: float = 0.0
    day_bucket: str = ""  # 当前日桶（ISO 日期）
    day_used: int = 0


class ExternalSystemConnector:
    """统一外部连接器注册表（契约+健康+配额+熔断挂接）。"""

    def __init__(
        self,
        *,
        clock: Callable[[], datetime.datetime] | None = None,
        health_probe: Callable[[str], HealthStatus] | None = None,
        breaker_factory: Callable[[str], _BreakerLike] | None = None,
    ) -> None:
        self._clock = clock or datetime.datetime.now
        self._health_probe = health_probe
        self._breaker_factory = breaker_factory
        self._entries: dict[str, _Entry] = {}

    # ── 登记 ─────────────────────────────────────────────────────────────

    def register(
        self,
        connector_id: str,
        capability: ConnectorCapability,
        quota: QuotaPolicy | None = None,
    ) -> ConnectorProfile:
        """统一登记（connector_id 唯一；登记即挂接熔断器）。"""
        if not connector_id:
            raise ExternalConnectorError("connector_id 为空")
        if connector_id in self._entries:
            raise ConnectorAlreadyRegisteredError(f"connector_id 重复注册: {connector_id!r}")
        breaker = self._breaker_factory(connector_id) if self._breaker_factory else None
        profile = ConnectorProfile(
            connector_id=connector_id,
            capability=capability,
            quota=quota,
            health=HealthStatus.UNKNOWN,
            registered_at=self._clock(),
        )
        self._entries[connector_id] = _Entry(profile=profile, breaker=breaker)
        _log.info("连接器登记: %s kind=%s vendor=%s", connector_id, capability.kind, capability.vendor)
        return profile

    def unregister(self, connector_id: str) -> None:
        """摘除登记（未知 → ConnectorNotFoundError）。"""
        entry = self._entries.pop(connector_id, None)
        if entry is None:
            raise ConnectorNotFoundError(f"未知连接器: {connector_id!r}")

    def _entry(self, connector_id: str) -> _Entry:
        entry = self._entries.get(connector_id)
        if entry is None:
            raise ConnectorNotFoundError(f"未知连接器: {connector_id!r}")
        return entry

    # ── 健康检查 ──────────────────────────────────────────────────────────

    def health_check(self, connector_id: str) -> HealthStatus:
        """经注入 probe 健康检查；未配置→UNKNOWN；probe 异常→UNHEALTHY（不抛）。"""
        entry = self._entry(connector_id)
        if self._health_probe is None:
            return HealthStatus.UNKNOWN
        try:
            status = self._health_probe(connector_id)
        except Exception:  # noqa: BLE001 — probe 异常映射 UNHEALTHY（蓝图 §1）
            _log.exception("健康检查 probe 异常: %s", connector_id)
            status = HealthStatus.UNHEALTHY
        if not isinstance(status, HealthStatus):
            _log.error("probe 返回非法状态 %r，按 UNHEALTHY 处理", status)
            status = HealthStatus.UNHEALTHY
        entry.profile = replace(entry.profile, health=status)
        return status

    # ── 配额管理 ──────────────────────────────────────────────────────────

    def acquire(self, connector_id: str, n: int = 1) -> None:
        """配额获取（rate/daily 双维计数，超限 Fail-Closed 抛 QuotaExceeded）。"""
        if n <= 0:
            raise ExternalConnectorError("acquire n 须为正")
        entry = self._entry(connector_id)
        quota = entry.profile.quota
        if quota is None:
            return
        now = self._clock()
        if quota.rate_per_sec is not None:
            sec = int(now.timestamp())
            if sec != entry.sec_bucket:
                entry.sec_bucket = sec
                entry.sec_used = 0.0
            if entry.sec_used + n > quota.rate_per_sec:
                raise QuotaExceeded(f"{connector_id} 每秒配额超限: {entry.sec_used}+{n} > {quota.rate_per_sec}")
        if quota.daily_cap is not None:
            day = now.date().isoformat()
            if day != entry.day_bucket:
                entry.day_bucket = day
                entry.day_used = 0
            if entry.day_used + n > quota.daily_cap:
                raise QuotaExceeded(f"{connector_id} 日累计配额超限: {entry.day_used}+{n} > {quota.daily_cap}")
        entry.sec_used += n
        entry.day_used += n

    # ── 熔断挂接 ──────────────────────────────────────────────────────────

    def report_result(self, connector_id: str, ok: bool) -> None:
        """调用结果透传熔断器（无熔断器 noop 不抛）。"""
        entry = self._entry(connector_id)
        if entry.breaker is not None:
            entry.breaker.record(ok)

    def is_callable(self, connector_id: str) -> bool:
        """可调判定：健康非 UNHEALTHY 且熔断非 OPEN 且配额未触顶。"""
        entry = self._entry(connector_id)
        if entry.profile.health is HealthStatus.UNHEALTHY:
            return False
        if entry.breaker is not None and entry.breaker.is_open:
            return False
        quota = entry.profile.quota
        if quota is not None:
            now = self._clock()
            if quota.rate_per_sec is not None:
                sec = int(now.timestamp())
                used = entry.sec_used if sec == entry.sec_bucket else 0.0
                if used + 1 > quota.rate_per_sec:
                    return False
            if quota.daily_cap is not None:
                day = now.date().isoformat()
                used = entry.day_used if day == entry.day_bucket else 0
                if used + 1 > quota.daily_cap:
                    return False
        return True

    def callable_connectors(self, kind: ConnectorKind | None = None) -> list[ConnectorProfile]:
        """可用连接器列表（connector_id 确定性排序；可按类别过滤）。"""
        out = [
            e.profile
            for e in self._entries.values()
            if (kind is None or e.profile.capability.kind is kind) and self.is_callable(e.profile.connector_id)
        ]
        out.sort(key=lambda p: p.connector_id)
        return out
