# [BLUEPRINT] MOD-ORCH-002 | docs/03_modules/_domain_orchestrator/global_state_aggregator/blueprint.md
# [MODULE] zephyr.orchestrator.global_state_aggregator
# [DOMAIN] D_ORCHESTRATOR
# [DEPENDENCIES] 无（只读聚合核心纯内存；collectors/clock 全注入）；L-4 默认适配器=函数体内**延迟** import 四执行体公共只读面（采样器/孵化池/gpu_monitor/reaper），核心导入零耦合
# [CONSUMERS] 运行时装配批（状态面板数据源 / 告警路由快照供给 / 六域采集器绑定）；build_system_health_collector=system_health 域 L-4 四源绑定件
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 域词表闭合(position|capital|risk|strategy|market|system_health); 采集器返回值须为 Mapping 否则按降级处理; 单域采集异常不阻断他域(降级标记); snapshot 域序按枚举序确定性排列; to_json 键排序确定性; 同输入必同输出
# [MODIFY-GUARD] docs/03_modules/_domain_orchestrator/global_state_aggregator/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] GlobalStateError(ZA-ORCH-0002)——未知域/空采集器/重复注册/无快照可查询时抛
# [TESTS] tests/orchestrator/test_global_state_aggregator.py
# [A_module] module_id=MOD-ORCH-002 | layer=module | stability=evolving | safety=M | ai_autonomy=human_gated
# [TTL] permanent
"""
GlobalStateAggregator — 全局状态聚合器（MOD-ORCH-002）。

B1-00201（AUD-DRAFT-001-DIGEST P2 波 P2-W13，CAND-ORCH-002，C2）：只读聚合
服务——定时采集**持仓/资金/风控/策略/市场/系统健康**六域（采集器注入）→
统一 StateSnapshot JSON（域词表闭合 + 采集失败降级标记）供面板与告警消费。

查重分工（蓝图 §0）：status_dashboard=面板渲染消费方（本件=其上游只读数据
源，不渲染）；state_synchronizer=运行时状态传播（写向，本件零写入纯只读）。

L-4 系统健康域绑定（排班表 v2 施工方案 §2.2 L-4 / 期次 P2-d，2026-09-17）：
`build_system_health_collector()` 把四个**已在跑**的执行体的现成公共只读接口
（资源采样摘要 / 孵化池水位 / gpu_monitor / reaper 幽灵战果）灌进
`StateDomain.SYSTEM_HEALTH` 采集域——纯采集零写入零新数据源（四源皆被他人
读写，本件只读其观测面），任一源探测失败=该源降级标记、绝不炸他域。
输出 `status` 词表与 `zephyr.infrastructure.system_telemetry.health.HealthStatus`
逐字一致（HEALTHY/DEGRADED/UNHEALTHY/UNKNOWN），新增字段全部带默认值
（键集恒定闭合）防下游 KeyError。

# [ALGO_FLOW] external: docs/03_modules/_domain_orchestrator/algo_flow/global_state_aggregator.yaml
"""

from __future__ import annotations

import datetime
import json
import logging
from collections.abc import Mapping
from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable, Final

_log = logging.getLogger(__name__)

__all__: Final = [
    "DomainReading",
    "GlobalStateAggregator",
    "GlobalStateError",
    "HEALTH_STATUS_DEGRADED",
    "HEALTH_STATUS_HEALTHY",
    "HEALTH_STATUS_UNHEALTHY",
    "HEALTH_STATUS_UNKNOWN",
    "SYSTEM_HEALTH_SOURCE_NAMES",
    "StateDomain",
    "StateSnapshot",
    "build_system_health_collector",
]


class GlobalStateError(Exception):
    """全局状态聚合输入/状态非法（Fail-Closed）。

    错误码 ZA-ORCH-0002 已登记转正（2026-09-06 Owner 批准批）。
    """

    error_code = "ZA-ORCH-0002"


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
                domain=domain,
                ok=False,
                payload={},
                error=f"{type(exc).__name__}: {exc}",
                collected_at=now,
            )
        if not isinstance(payload, Mapping):
            _log.warning("域采集返回非 Mapping(降级): %s", domain.value)
            return DomainReading(
                domain=domain,
                ok=False,
                payload={},
                error="collector 返回值非 Mapping",
                collected_at=now,
            )
        return DomainReading(
            domain=domain,
            ok=True,
            payload=dict(payload),
            error=None,
            collected_at=now,
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


# ══════════════════════════════════════════════════════════════════════════════
# L-4 系统健康域四源绑定（排班表 v2 施工方案 §2.2 L-4，期次 P2-d）
#
# 只读纪律（本节的宪法）：
#   1. 四源皆 import 其**现成公共只读接口**，不改对方一行代码、不复制对方路径常量；
#   2. 被观测者的写路径一律不接（采样器 scan_once()/writeback() 会被观测者代跑=越权）；
#   3. 单源探测炸 → 该源 UNHEALTHY + error 可见，绝不外抛（沿用本件"降级不阻断"不变量）。
# ══════════════════════════════════════════════════════════════════════════════

#: 四源名闭合词表（输出 ``sources`` 键序按此序确定性排列）
SYSTEM_HEALTH_SOURCE_NAMES: Final = (
    "resource_sampler",
    "incubator",
    "gpu_monitor",
    "reaper",
)

# 健康态词表——字面量与 zephyr.infrastructure.system_telemetry.health.HealthStatus
# （HEALTHY/DEGRADED/UNHEALTHY/UNKNOWN）逐字一致。此处**不**顶层 import 该模块：
# 本件核心"零依赖"不变量优先，字面量对齐即可，无运行时耦合（改词表须双侧同步）。
HEALTH_STATUS_HEALTHY: Final = "HEALTHY"
HEALTH_STATUS_DEGRADED: Final = "DEGRADED"
HEALTH_STATUS_UNHEALTHY: Final = "UNHEALTHY"
HEALTH_STATUS_UNKNOWN: Final = "UNKNOWN"

#: 严重度序（越大越差；overall = 各源最坏）
_HEALTH_SEVERITY: Final = {
    HEALTH_STATUS_HEALTHY: 0,
    HEALTH_STATUS_UNKNOWN: 1,
    HEALTH_STATUS_DEGRADED: 2,
    HEALTH_STATUS_UNHEALTHY: 3,
}

_SourceMetrics = dict[str, Any]


# ── 默认适配器（四源各一，全部延迟 import + 只读） ──────────────────────────────


def _default_resource_sampler_summary() -> _SourceMetrics:
    """源①资源采样摘要：注册表实体面 + 样本流证据面（实测 vs 申报对账口径）。

    只接 lifetime_deviation_report()——采样器自订"函数级 API 供 P5 校准器复用"的
    读面；scan_once()/writeback() 是写路径，本件绝不触发。
    """
    from zephyr.infrastructure.system_telemetry.resource_sampler import ResourceSampler

    sampler = ResourceSampler()
    entities = sampler.load_entities()
    patterns, host_shared = sampler.derive_patterns(entities)
    rows = sampler.lifetime_deviation_report()
    directions: dict[str, int] = {}
    for row in rows:
        key = str(row.get("direction") or "no_evidence")
        directions[key] = directions.get(key, 0) + 1
    return {
        "entities_total": len(entities),
        "observable_tasks": len(patterns),
        "host_shared_skipped": len(host_shared),
        "evidence_rows": len(rows),
        "direction_counts": dict(sorted(directions.items())),
    }


def _default_incubator_water() -> _SourceMetrics:
    """源②孵化池水位：commit charge 现值 vs queue/reject 两线 + 台账水位计数。

    阈值经 load_*_threshold() 取（真源=config/resource_optimization.yaml），本件
    不硬编码数值；stats() 只读 ledger（无写副作用）。
    """
    from zephyr.shared.infra.process_incubator import (
        get_incubator,
        load_queue_threshold,
        load_reject_threshold,
        memory_water_percent,
    )

    return {
        "water_percent": round(float(memory_water_percent()), 2),
        "queue_line_percent": float(load_queue_threshold()),
        "reject_line_percent": float(load_reject_threshold()),
        "ledger_stats": dict(get_incubator().stats()),
    }


def _default_gpu_stats() -> _SourceMetrics:
    """源③GPU：gpu_monitor.collect_gpu_stats()（nvidia-smi 缺失自带优雅降级）。"""
    from zephyr.trading.gpu_monitor import collect_gpu_stats

    return dict(collect_gpu_stats())


def _default_reaper_outcome() -> _SourceMetrics:
    """源④reaper 战果：scan_ghost_windows()——reaper 自证"零副作用（只读），纯 psutil"。

    口径说明：本轮**击杀账目**落在 reaper 私有落盘面（其 _STATUS_FILE，非公共面），
    本件不复制他人私有路径（第二真源风险）；要看击杀明细走
    ``python -m zephyr.trading.process_reaper --status``。此处取的是"当前还在册的
    幽灵嫌疑数"=收割未完成度，语义更贴健康域。
    """
    from zephyr.trading.process_reaper import scan_ghost_windows

    suspects = list(scan_ghost_windows())
    return {
        "ghost_suspects": len(suspects),
        "suspect_pids": [int(s.get("pid", -1)) for s in suspects[:20]],
    }


#: 源名 → 默认适配器（闭合）
_DEFAULT_SOURCE_ADAPTERS: Final = {
    "resource_sampler": _default_resource_sampler_summary,
    "incubator": _default_incubator_water,
    "gpu_monitor": _default_gpu_stats,
    "reaper": _default_reaper_outcome,
}


# ── 判定：原始读数 → 该源健康态 ────────────────────────────────────────────────


def _judge_resource_sampler(metrics: _SourceMetrics) -> tuple[str, str]:
    observable = int(metrics.get("observable_tasks") or 0)
    evidence = int(metrics.get("evidence_rows") or 0)
    if observable == 0:
        return HEALTH_STATUS_DEGRADED, "采样器零可观测实体（模式推导空集）"
    if evidence == 0:
        return HEALTH_STATUS_DEGRADED, "有可观测实体但样本流零证据（采样腿未落地）"
    return HEALTH_STATUS_HEALTHY, ""


def _judge_incubator(metrics: _SourceMetrics) -> tuple[str, str]:
    water = float(metrics.get("water_percent") or 0.0)
    if water >= float(metrics.get("reject_line_percent") or float("inf")):
        return HEALTH_STATUS_UNHEALTHY, f"内存水位 {water:.1f}% 触拒绝线"
    if water >= float(metrics.get("queue_line_percent") or float("inf")):
        return HEALTH_STATUS_DEGRADED, f"内存水位 {water:.1f}% 触排队线"
    ledger = metrics.get("ledger_stats") or {}
    if int(ledger.get("expired_active") or 0) > 0:
        return HEALTH_STATUS_DEGRADED, "存在超期仍活的孵化登记（等 reaper 收割）"
    return HEALTH_STATUS_HEALTHY, ""


def _judge_gpu_monitor(metrics: _SourceMetrics) -> tuple[str, str]:
    if not metrics.get("available"):
        return HEALTH_STATUS_DEGRADED, "GPU 遥测不可用（nvidia-smi 缺失/超时）"
    return HEALTH_STATUS_HEALTHY, ""


def _judge_reaper(metrics: _SourceMetrics) -> tuple[str, str]:
    if int(metrics.get("ghost_suspects") or 0) > 0:
        return HEALTH_STATUS_DEGRADED, "存在在册幽灵嫌疑进程（收割进行中）"
    return HEALTH_STATUS_HEALTHY, ""


_SOURCE_JUDGES: Final = {
    "resource_sampler": _judge_resource_sampler,
    "incubator": _judge_incubator,
    "gpu_monitor": _judge_gpu_monitor,
    "reaper": _judge_reaper,
}


def _empty_section() -> dict[str, Any]:
    """单源段（键集恒定闭合——下游按固定键读，永不 KeyError）。"""
    return {"status": HEALTH_STATUS_UNKNOWN, "available": False, "note": "", "error": None, "metrics": {}}


def build_system_health_collector(
    *,
    resource_sampler_summary: Callable[[], Mapping] | None = None,
    incubator_water_level: Callable[[], Mapping] | None = None,
    gpu_stats: Callable[[], Mapping] | None = None,
    reaper_outcome: Callable[[], Mapping] | None = None,
) -> Callable[[], dict[str, Any]]:
    """构造 system_health 域采集器（L-4 四源只读绑定，返回体即 DomainReading.payload）。

    Args:
        resource_sampler_summary / incubator_water_level / gpu_stats / reaper_outcome:
            四源探针，缺省=各执行体现成公共只读接口的适配器；单测注入替身即可
            完全脱离真实进程/GPU 探测（沿用本件"采集器全注入"设计不变量）。

    Returns:
        采集器（无参 → Mapping）：``status`` 取四源最坏值，``sources`` 逐源给
        status/available/note/error/metrics，``*_count`` 与 ``*_sources`` 为派生
        汇总——所有键恒在（缺测=None/空表），下游零 KeyError。

    注：本函数**不**自动注册；装配方自行
    ``GlobalStateAggregator(collectors={..., StateDomain.SYSTEM_HEALTH: build_system_health_collector()})``
    或 ``register_collector`` ——保持"谁装配谁负责"的注入语义。

    成本口径（2026-09-17 本机实测，装配方据此定频）：冷首调 ≈14s（四源首次
    import + reaper 全进程表 + 采样器读 72 实体注册表/样本流），暖调 ≈1.3-1.8s
    ——只适合分钟级周期采集，禁入盘中热路径。另外 ``incubator`` 源的
    ``expired_active>0`` 判降级吃的是孵化台账"未标退出且未标收割"记录数，台账
    历史欠账（L-1 pid join/收割端回写未收敛前）会使其长期 DEGRADED=如实读数，
    本件不替对方洗账。
    """
    probes: dict[str, Callable[[], Mapping]] = {
        "resource_sampler": resource_sampler_summary or _DEFAULT_SOURCE_ADAPTERS["resource_sampler"],
        "incubator": incubator_water_level or _DEFAULT_SOURCE_ADAPTERS["incubator"],
        "gpu_monitor": gpu_stats or _DEFAULT_SOURCE_ADAPTERS["gpu_monitor"],
        "reaper": reaper_outcome or _DEFAULT_SOURCE_ADAPTERS["reaper"],
    }

    def _collect() -> dict[str, Any]:
        sources: dict[str, dict[str, Any]] = {}
        for name in SYSTEM_HEALTH_SOURCE_NAMES:
            section = _empty_section()
            try:
                raw = probes[name]()
            except Exception as exc:  # noqa: BLE001 — 单源探测失败降级，不外抛
                _log.warning("system_health 源探测失败: %s (%s)", name, exc)
                section["error"] = f"{type(exc).__name__}: {exc}"
                section["status"] = HEALTH_STATUS_UNHEALTHY
                sources[name] = section
                continue
            if not isinstance(raw, Mapping):
                section["error"] = "源返回非 Mapping"
                section["status"] = HEALTH_STATUS_UNHEALTHY
                sources[name] = section
                continue
            metrics = dict(raw)
            status, note = _SOURCE_JUDGES[name](metrics)
            section.update(
                {
                    "status": status,
                    "available": True,
                    "note": note,
                    "metrics": metrics,
                }
            )
            sources[name] = section

        statuses = {name: sources[name]["status"] for name in SYSTEM_HEALTH_SOURCE_NAMES}
        overall = max(statuses.values(), key=lambda s: _HEALTH_SEVERITY.get(s, 1))
        payload: dict[str, Any] = {
            "status": overall,
            "sources": sources,
            "sources_total": len(SYSTEM_HEALTH_SOURCE_NAMES),
            "healthy_count": sum(1 for s in statuses.values() if s == HEALTH_STATUS_HEALTHY),
            "degraded_sources": [n for n in SYSTEM_HEALTH_SOURCE_NAMES if statuses[n] == HEALTH_STATUS_DEGRADED],
            "unhealthy_sources": [n for n in SYSTEM_HEALTH_SOURCE_NAMES if statuses[n] == HEALTH_STATUS_UNHEALTHY],
            "unknown_sources": [n for n in SYSTEM_HEALTH_SOURCE_NAMES if statuses[n] == HEALTH_STATUS_UNKNOWN],
            # 扁平便捷位（全部带默认值；源不可用时保持默认，不省略键）
            "water_percent": sources["incubator"]["metrics"].get("water_percent"),
            "incubator_active": (sources["incubator"]["metrics"].get("ledger_stats") or {}).get("active"),
            "gpu_available": bool(sources["gpu_monitor"]["metrics"].get("available", False)),
            "gpu_percent": sources["gpu_monitor"]["metrics"].get("gpu_percent"),
            "ghost_suspects": sources["reaper"]["metrics"].get("ghost_suspects"),
            "sampler_evidence_rows": sources["resource_sampler"]["metrics"].get("evidence_rows"),
        }
        return payload

    return _collect
