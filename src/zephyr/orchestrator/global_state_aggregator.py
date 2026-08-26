# [BLUEPRINT] MOD-ORCH-002 | docs/03_modules/_domain_orchestrator/global_state_aggregator/blueprint.md
# [MODULE] zephyr.orchestrator.global_state_aggregator
# [DOMAIN] D_ORCHESTRATOR
# [DEPENDENCIES] 无（只读聚合核心纯内存；collectors/clock 全注入）
# [CONSUMERS] 运行时装配批（状态面板数据源 / 告警路由快照供给 / 六域采集器绑定）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 域词表闭合(position|capital|risk|strategy|market|system_health); 采集器返回值须为 Mapping 否则按降级处理; 单域采集异常不阻断他域(降级标记); snapshot 域序按枚举序确定性排列; to_json 键排序确定性; 同输入必同输出
# [MODIFY-GUARD] docs/03_modules/_domain_orchestrator/global_state_aggregator/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] GlobalStateError(占位 ZA-ORCH-UNREGISTERED-GLOBAL-STATE)——未知域/空采集器/重复注册/无快照可查询时抛
# [TESTS] tests/orchestrator/test_global_state_aggregator.py
# [A_module] module_id=MOD-ORCH-002 | layer=module | stability=evolving | safety=M | ai_autonomy=human_gated
# [TTL] permanent
"""GlobalStateAggregator — 全局状态聚合器（MOD-ORCH-002）。

B1-00201（AUD-DRAFT-001-DIGEST P2 波 P2-W13，CAND-ORCH-002，C2）：只读聚合
服务——定时采集**持仓/资金/风控/策略/市场/系统健康**六域（采集器注入）→
统一 StateSnapshot JSON（域词表闭合 + 采集失败降级标记）供面板与告警消费。

查重分工（蓝图 §0）：status_dashboard=面板渲染消费方（本件=其上游只读数据
源，不渲染）；agent_health_monitor=Agent 维度 SLO（本件=系统域采集目标之一，
不重建监控）；state_synchronizer=运行时状态传播（写向，本件零写入纯只读）。
"""

from __future__ import annotations

import datetime
import json
import logging
from collections.abc import Mapping
from dataclasses import dataclass
from enum import Enum
from typing import Callable, Final

_log = logging.getLogger(__name__)

__all__: Final = [
    "DomainReading",
    "GlobalStateAggregator",
    "GlobalStateError",
    "StateDomain",
    "StateSnapshot",
]


class GlobalStateError(Exception):
    """全局状态聚合输入/状态非法（Fail-Closed）。

    未登记错误码-申请中：占位 ZA-ORCH-UNREGISTERED-GLOBAL-STATE。
    """


class StateDomain(str, Enum):
    """六域词表（闭合）。"""

    POSITION = "position"
    CAPITAL = "capital"
    RISK = "risk"
    STRATEGY = "strategy"
    MARKET = "market"
    SYSTEM_HEALTH = "system_health"


@dataclass(frozen=True)
class DomainReading:
    """单域采集读数（frozen；ok=False 即降级标记）。"""

    domain: StateDomain
    ok: bool
    payload: Mapping
    error: str | None
    collected_at: datetime.datetime


@dataclass(frozen=True)
class StateSnapshot:
    """统一全局状态快照（frozen；readings 按枚举序确定性排列）。"""

    snapshot_id: str
    collected_at: datetime.datetime
    readings: tuple[DomainReading, ...]
    degraded_domains: tuple[StateDomain, ...]

    @property
    def healthy(self) -> bool:
        """全域采集成功（无降级）。"""
        return not self.degraded_domains

    def reading_of(self, domain: StateDomain) -> DomainReading:
        """单域读数查询（未知域 → Fail-Closed）。"""
        if not isinstance(domain, StateDomain):
            raise GlobalStateError(f"未知域: {domain!r}（域词表闭合）")
        for reading in self.readings:
            if reading.domain is domain:
                return reading
        raise GlobalStateError(f"域未采集: {domain.value!r}（采集器未注册）")

    def to_dict(self) -> dict:
        """确定性字典视图（供 JSON 序列化）。"""
        return {
            "snapshot_id": self.snapshot_id,
            "collected_at": self.collected_at.isoformat(),
            "healthy": self.healthy,
            "degraded_domains": [d.value for d in self.degraded_domains],
            "domains": {
                r.domain.value: {
                    "ok": r.ok,
                    "payload": dict(r.payload),
                    "error": r.error,
                    "collected_at": r.collected_at.isoformat(),
                }
                for r in self.readings
            },
        }

    def to_json(self) -> str:
        """确定性 JSON（键排序 + UTF-8 不转义）。"""
        return json.dumps(self.to_dict(), sort_keys=True, ensure_ascii=False, default=str)


class GlobalStateAggregator:
    """六域只读聚合器（采集器注入 + 降级标记 + 快照查询）。"""

    def __init__(
        self,
        *,
        collectors: Mapping[StateDomain, Callable[[], Mapping]],
        clock: Callable[[], datetime.datetime] | None = None,
    ) -> None:
        if not collectors:
            raise GlobalStateError("collectors 为空（至少注册一域采集器）")
        self._collectors: dict[StateDomain, Callable[[], Mapping]] = {}
        for domain, fn in collectors.items():
            self._validate(domain, fn)
            self._collectors[domain] = fn
        self._clock = clock or datetime.datetime.now
        self._latest: StateSnapshot | None = None
        self._seq = 0

    # ── 内部 ─────────────────────────────────────────────────────────────

    @staticmethod
    def _validate(domain: StateDomain, fn: Callable[[], Mapping]) -> None:
        if not isinstance(domain, StateDomain):
            raise GlobalStateError(f"未知域: {domain!r}（域词表闭合）")
        if not callable(fn):
            raise GlobalStateError(f"采集器不可调用: {domain.value!r}")

    def _collect_one(self, domain: StateDomain) -> DomainReading:
        now = self._clock()
        try:
            payload = self._collectors[domain]()
        except Exception as exc:  # noqa: BLE001 — 单域采集失败降级不阻断他域
            _log.warning("域采集失败(降级): %s (%s)", domain.value, exc)
            return DomainReading(
                domain=domain, ok=False, payload={}, error=f"{type(exc).__name__}: {exc}",
                collected_at=now,
            )
        if not isinstance(payload, Mapping):
            _log.warning("域采集返回非 Mapping(降级): %s", domain.value)
            return DomainReading(
                domain=domain, ok=False, payload={}, error="collector 返回值非 Mapping",
                collected_at=now,
            )
        return DomainReading(
            domain=domain, ok=True, payload=dict(payload), error=None, collected_at=now,
        )

    # ── 采集器注册 ────────────────────────────────────────────────────────

    def register_collector(self, domain: StateDomain, fn: Callable[[], Mapping]) -> None:
        """补注册单域采集器（重复注册 → Fail-Closed）。"""
        self._validate(domain, fn)
        if domain in self._collectors:
            raise GlobalStateError(f"采集器重复注册: {domain.value!r}")
        self._collectors[domain] = fn

    def registered_domains(self) -> tuple[StateDomain, ...]:
        """已注册域视图（按枚举序确定性排列）。"""
        return tuple(d for d in StateDomain if d in self._collectors)

    # ── 采集 ─────────────────────────────────────────────────────────────

    def collect(self, snapshot_id: str | None = None) -> StateSnapshot:
        """全量采集一次：逐域调用采集器 → StateSnapshot（失败域降级标记）。"""
        now = self._clock()
        readings = tuple(self._collect_one(d) for d in self.registered_domains())
        degraded = tuple(r.domain for r in readings if not r.ok)
        if snapshot_id is None:
            self._seq += 1
            snapshot_id = f"snap-{self._seq:06d}"
        if not snapshot_id:
            raise GlobalStateError("snapshot_id 为空")
        snapshot = StateSnapshot(
            snapshot_id=snapshot_id,
            collected_at=now,
            readings=readings,
            degraded_domains=degraded,
        )
        self._latest = snapshot
        return snapshot

    # ── 查询 ─────────────────────────────────────────────────────────────

    def latest(self) -> StateSnapshot:
        """最近一次快照（尚无快照 → Fail-Closed）。"""
        if self._latest is None:
            raise GlobalStateError("尚无快照（未执行 collect）")
        return self._latest
