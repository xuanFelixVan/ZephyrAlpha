# [BLUEPRINT] MOD-DATA_GOV-009 | docs/03_modules/_domain_data_governance/market_data_aggregates/blueprint.md
# [MODULE] zephyr.data_governance.market_data_aggregates
# [DOMAIN] D_DATA_GOV
# [DEPENDENCIES] 无（协议核心纯内存；clock/ch_reader/pit_query 语义全注入）
# [CONSUMERS] 运行时装配批（行情仓储绑定 CH 读取 / PIT 查询注入 / 保留策略与演练登记）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 值对象 Bar/OHLCV/FinancialReport frozen 不可变; 聚合根版本单调+1(expected_version 乐观并发不符拒绝); 仓储 get/save/snapshot 语义闭合; 保留策略 domain 唯一; 演练记录按 (started_at,drill_id) 确定性排序; 同输入必同输出
# [MODIFY-GUARD] docs/03_modules/_domain_data_governance/market_data_aggregates/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] MarketDataAggregateError(占位 ZA-DATA-UNREGISTERED-MKT-AGGREGATE)——空ID/负版本/版本过期/重复策略/未知domain/非法演练记录时抛
# [TESTS] tests/data_governance/test_market_data_aggregates.py
# [A_module] module_id=MOD-DATA_GOV-009 | layer=module | stability=evolving | safety=M | ai_autonomy=human_gated
# [TTL] permanent
"""
market_data_aggregates — MarketData/Instrument 轻量聚合根与生命周期（MOD-DATA_GOV-009）。

B1-00648（AUD-DRAFT-001-DIGEST P2 波 P2-W02，CAND-DATGOV-006，C2 130~136）：
MarketData/Instrument **轻量聚合**（值对象 Bar/OHLCV/FinancialReport 为
frozen dataclass + 聚合根**版本不变量**）+ 仓储接口协议（get/save/snapshot
语义，对齐 ch_reader/pit_query 注入点）+ 跨域**保留归档策略协调表**
（TTL/归档目标/演练频次登记）+ **恢复演练记录**，不建完整 DDD 分层。

查重分工（蓝图 §0）：ex_core/aggregate_root_manager=通用聚合根框架（本件=行
情域专用轻量聚合，不重建框架）；ch_reader/pit_query=读取实现（本件仅定义仓
储协议语义，实现全注入）。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: instrument_id 参数
#   fields: 参数 instrument_id（无注解）
#   code: market_data_aggregates.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: bars 参数
#   fields: 参数 bars（无注解）
#   code: market_data_aggregates.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: reports 参数
#   fields: 参数 reports（无注解）
#   code: market_data_aggregates.py 顶层公共函数形参（AST 提取）
# - id: I4
#   name: version 参数
#   fields: 参数 version（无注解）
#   code: market_data_aggregates.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① MarketData
#   name_en: MarketData
#   intro: MarketData 聚合根：单标的行情集合（bars/reports）+ 版本不变量。
#   desc: MarketData 聚合根：单标的行情集合（bars/reports）+ 版本不变量。 不可变演进：append_* 返回 version+1 的新实例，原实例不变（确定性）。；公共方法（定义序）: instrume…
#   inputs: instrument_id bars reports version
#   outputs: 返回值
# - id: A2
#   name_zh: ② Instrument
#   name_en: Instrument
#   intro: Instrument 聚合根：标的主档 + 版本不变量。
#   desc: Instrument 聚合根：标的主档 + 版本不变量。；公共方法（定义序）: instrument_id, symbol, exchange, version, update_profile；源码 L253-L294
#   inputs: instrument_id symbol exchange version
#   outputs: 返回值
# - id: A3
#   name_zh: ③ MarketDataRepository
#   name_en: MarketDataRepository
#   intro: MarketData 仓储协议。
#   desc: MarketData 仓储协议。 语义约定： - get: 未知标的返回 None；空 instrument_id → MarketDataAggregateError。 - s…；公共方法（定义序）: get, sa…
#   inputs: 无参数
#   outputs: 返回值
# - id: A4
#   name_zh: ④ InMemoryMarketDataRepository
#   name_en: InMemoryMarketDataRepository
#   intro: 内存参考实现（运行时装配批可替换为 ch_reader/pit_query 注入实现）。
#   desc: 内存参考实现（运行时装配批可替换为 ch_reader/pit_query 注入实现）。；公共方法（定义序）: get, save, snapshot；源码 L319-L348
#   inputs: 无参数
#   outputs: 返回值
# - id: A5
#   name_zh: ⑤ RetentionPolicyRegistry
#   name_en: RetentionPolicyRegistry
#   intro: 保留策略协调表（domain 唯一登记）。
#   desc: 保留策略协调表（domain 唯一登记）。；公共方法（定义序）: register, get, list_all；源码 L366-L395
#   inputs: 无参数
#   outputs: 返回值
# - id: A6
#   name_zh: ⑥ RecoveryDrillLog
#   name_en: RecoveryDrillLog
#   intro: 恢复演练记录簿（与 RetentionPolicyRegistry 联动判定演练逾期）。
#   desc: 恢复演练记录簿（与 RetentionPolicyRegistry 联动判定演练逾期）。；公共方法（定义序）: record, drills_for, last_drill, overdue_domains…
#   inputs: registry clock
#   outputs: 返回值
#   （注：A6 之后另有 6 个公共定义未列入（含 6 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（12 定义）
#   name_en: public defs
#   intro: MarketData, Instrument, MarketDataRepository, InMemoryMarketDataRepository, Ret…
#   downstream: 运行时装配批（行情仓储绑定 CH 读取 / PIT 查询注入 / 保留策略与演练登记）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# I4 --> A1
# A1 --> A2
# A2 --> A3
# A3 --> A4
# A4 --> A5
# A5 --> A6
# A6 --> O1
"""

from __future__ import annotations

import datetime
import logging
from dataclasses import dataclass
from typing import Callable, Final, Protocol

_log = logging.getLogger(__name__)

__all__: Final = [
    "Bar",
    "FinancialReport",
    "InMemoryMarketDataRepository",
    "Instrument",
    "MarketData",
    "MarketDataAggregateError",
    "MarketDataRepository",
    "RecoveryDrillLog",
    "RecoveryDrillRecord",
    "RetentionPolicy",
    "RetentionPolicyRegistry",
]


class MarketDataAggregateError(Exception):
    """行情聚合/仓储/保留策略/演练记录输入非法（Fail-Closed）。

    未登记错误码-申请中：占位 ZA-DATA-UNREGISTERED-MKT-AGGREGATE。
    """


# ──────────────────────────────────────────────────────────────────────────────
# 值对象（frozen）
# ──────────────────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class OHLCV:
    """OHLCV 五价量值对象（frozen）。"""

    open: float
    high: float
    low: float
    close: float
    volume: float


@dataclass(frozen=True)
class Bar:
    """单根 K 线 Bar 值对象（frozen）。"""

    instrument_id: str
    ts: datetime.datetime
    ohlcv: OHLCV


@dataclass(frozen=True)
class FinancialReport:
    """财报值对象（frozen）。"""

    instrument_id: str
    period: str
    revenue: float
    net_profit: float
    published_at: datetime.datetime


# ──────────────────────────────────────────────────────────────────────────────
# 聚合根（版本不变量：version 从 0 起，每次变更恰 +1，返回新实例）
# ──────────────────────────────────────────────────────────────────────────────


def _check_id_version(owner_id: str, version: int) -> None:
    if not owner_id:
        raise MarketDataAggregateError("instrument_id 为空")
    if version < 0:
        raise MarketDataAggregateError(f"version 为负: {version}")


class MarketData:
    """MarketData 聚合根：单标的行情集合（bars/reports）+ 版本不变量。

    不可变演进：append_* 返回 version+1 的新实例，原实例不变（确定性）。
    """

    __slots__ = ("_bars", "_instrument_id", "_reports", "_version")

    def __init__(
        self,
        instrument_id: str,
        *,
        bars: tuple[Bar, ...] = (),
        reports: tuple[FinancialReport, ...] = (),
        version: int = 0,
    ) -> None:
        _check_id_version(instrument_id, version)
        self._instrument_id = instrument_id
        self._bars = tuple(bars)
        self._reports = tuple(reports)
        self._version = int(version)

    @property
    def instrument_id(self) -> str:
        return self._instrument_id

    @property
    def bars(self) -> tuple[Bar, ...]:
        return self._bars

    @property
    def reports(self) -> tuple[FinancialReport, ...]:
        return self._reports

    @property
    def version(self) -> int:
        return self._version

    def append_bar(self, bar: Bar) -> MarketData:
        """追加 Bar：标的须一致，返回 version+1 新实例。"""
        if bar.instrument_id != self._instrument_id:
            raise MarketDataAggregateError(f"Bar 标的不符: {bar.instrument_id!r} 非聚合 {self._instrument_id!r}")
        return MarketData(
            self._instrument_id,
            bars=self._bars + (bar,),
            reports=self._reports,
            version=self._version + 1,
        )

    def append_report(self, report: FinancialReport) -> MarketData:
        """追加财报：标的须一致，返回 version+1 新实例。"""
        if report.instrument_id != self._instrument_id:
            raise MarketDataAggregateError(f"财报标的不符: {report.instrument_id!r} 非聚合 {self._instrument_id!r}")
        return MarketData(
            self._instrument_id,
            bars=self._bars,
            reports=self._reports + (report,),
            version=self._version + 1,
        )


class Instrument:
    """Instrument 聚合根：标的主档 + 版本不变量。"""

    __slots__ = ("_exchange", "_instrument_id", "_symbol", "_version")

    def __init__(
        self,
        instrument_id: str,
        *,
        symbol: str,
        exchange: str,
        version: int = 0,
    ) -> None:
        _check_id_version(instrument_id, version)
        if not symbol:
            raise MarketDataAggregateError("symbol 为空")
        if not exchange:
            raise MarketDataAggregateError("exchange 为空")
        self._instrument_id = instrument_id
        self._symbol = symbol
        self._exchange = exchange
        self._version = int(version)

    @property
    def instrument_id(self) -> str:
        return self._instrument_id

    @property
    def symbol(self) -> str:
        return self._symbol

    @property
    def exchange(self) -> str:
        return self._exchange

    @property
    def version(self) -> int:
        return self._version

    def update_profile(self, *, symbol: str, exchange: str) -> Instrument:
        """更新主档：返回 version+1 新实例。"""
        return Instrument(self._instrument_id, symbol=symbol, exchange=exchange, version=self._version + 1)


# ──────────────────────────────────────────────────────────────────────────────
# 仓储协议（get/save/snapshot 语义；对齐 ch_reader/pit_query 注入点）
# ──────────────────────────────────────────────────────────────────────────────


class MarketDataRepository(Protocol):
    """MarketData 仓储协议。

    语义约定：
    - get: 未知标的返回 None；空 instrument_id → MarketDataAggregateError。
    - save: 乐观并发——expected_version 须等于已存版本（新建为 0），且
      aggregate.version 须恰为 expected_version+1，否则 Fail-Closed。
    - snapshot: 返回全部聚合的确定性快照（按 instrument_id 排序）。
    """

    def get(self, instrument_id: str) -> MarketData | None: ...

    def save(self, aggregate: MarketData, *, expected_version: int) -> None: ...

    def snapshot(self) -> dict[str, MarketData]: ...


class InMemoryMarketDataRepository:
    """内存参考实现（运行时装配批可替换为 ch_reader/pit_query 注入实现）。"""

    def __init__(self) -> None:
        self._store: dict[str, MarketData] = {}

    def get(self, instrument_id: str) -> MarketData | None:
        if not instrument_id:
            raise MarketDataAggregateError("instrument_id 为空")
        return self._store.get(instrument_id)

    def save(self, aggregate: MarketData, *, expected_version: int) -> None:
        stored = self._store.get(aggregate.instrument_id)
        if stored is None:
            if expected_version != 0:
                raise MarketDataAggregateError(f"新建聚合 expected_version 须为 0，实收 {expected_version}")
        elif stored.version != expected_version:
            raise MarketDataAggregateError(
                f"版本过期(乐观并发): {aggregate.instrument_id!r} 已存 v{stored.version}，"
                f"实收 expected_version={expected_version}"
            )
        if aggregate.version != expected_version + 1:
            raise MarketDataAggregateError(
                f"版本不变量违反: aggregate.version={aggregate.version} 须为 expected_version+1={expected_version + 1}"
            )
        self._store[aggregate.instrument_id] = aggregate
        _log.debug("仓储保存: %s v%d", aggregate.instrument_id, aggregate.version)

    def snapshot(self) -> dict[str, MarketData]:
        return {k: self._store[k] for k in sorted(self._store)}


# ──────────────────────────────────────────────────────────────────────────────
# 跨域保留归档策略协调表
# ──────────────────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class RetentionPolicy:
    """保留归档策略（TTL/归档目标/演练频次，frozen）。"""

    domain: str
    ttl_days: int
    archive_target: str
    drill_interval_days: int


class RetentionPolicyRegistry:
    """保留策略协调表（domain 唯一登记）。"""

    def __init__(self) -> None:
        self._policies: dict[str, RetentionPolicy] = {}

    def register(self, policy: RetentionPolicy) -> None:
        """登记策略：domain 非空唯一，TTL/演练频次为正，归档目标非空。"""
        if not policy.domain:
            raise MarketDataAggregateError("策略 domain 为空")
        if policy.domain in self._policies:
            raise MarketDataAggregateError(f"策略 domain 重复登记: {policy.domain!r}")
        if policy.ttl_days <= 0:
            raise MarketDataAggregateError(f"ttl_days 非正: {policy.ttl_days}")
        if policy.drill_interval_days <= 0:
            raise MarketDataAggregateError(f"drill_interval_days 非正: {policy.drill_interval_days}")
        if not policy.archive_target:
            raise MarketDataAggregateError("archive_target 为空")
        self._policies[policy.domain] = policy

    def get(self, domain: str) -> RetentionPolicy:
        """按 domain 取策略（未知 → Fail-Closed）。"""
        policy = self._policies.get(domain)
        if policy is None:
            raise MarketDataAggregateError(f"未知策略 domain: {domain!r}")
        return policy

    def list_all(self) -> tuple[RetentionPolicy, ...]:
        """全部策略（按 domain 确定性排序）。"""
        return tuple(self._policies[k] for k in sorted(self._policies))


# ──────────────────────────────────────────────────────────────────────────────
# 恢复演练记录
# ──────────────────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class RecoveryDrillRecord:
    """恢复演练记录（frozen）。"""

    drill_id: str
    domain: str
    started_at: datetime.datetime
    finished_at: datetime.datetime
    success: bool
    notes: str = ""


class RecoveryDrillLog:
    """恢复演练记录簿（与 RetentionPolicyRegistry 联动判定演练逾期）。"""

    def __init__(
        self,
        *,
        registry: RetentionPolicyRegistry,
        clock: Callable[[], datetime.datetime] | None = None,
    ) -> None:
        self._registry = registry
        self._clock = clock or datetime.datetime.now
        self._records: dict[str, RecoveryDrillRecord] = {}

    def record(self, rec: RecoveryDrillRecord) -> None:
        """登记演练：domain 须已注册策略；finished_at 不早于 started_at。"""
        if not rec.drill_id:
            raise MarketDataAggregateError("drill_id 为空")
        if rec.drill_id in self._records:
            raise MarketDataAggregateError(f"drill_id 重复: {rec.drill_id!r}")
        self._registry.get(rec.domain)  # 未知 domain → Fail-Closed
        if rec.finished_at < rec.started_at:
            raise MarketDataAggregateError(f"演练时间倒置: finished_at {rec.finished_at} < started_at {rec.started_at}")
        self._records[rec.drill_id] = rec
        _log.info("恢复演练登记: %s domain=%s success=%s", rec.drill_id, rec.domain, rec.success)

    def drills_for(self, domain: str) -> tuple[RecoveryDrillRecord, ...]:
        """单 domain 演练序列（按 (started_at, drill_id) 确定性排序）。"""
        self._registry.get(domain)
        out = [r for r in self._records.values() if r.domain == domain]
        out.sort(key=lambda r: (r.started_at, r.drill_id))
        return tuple(out)

    def last_drill(self, domain: str) -> RecoveryDrillRecord | None:
        """最近一次演练（按 (finished_at, drill_id) 取尾）。"""
        drills = self.drills_for(domain)
        if not drills:
            return None
        return max(drills, key=lambda r: (r.finished_at, r.drill_id))

    def overdue_domains(self) -> tuple[str, ...]:
        """演练逾期 domain：从未演练或距上次完成超过 drill_interval_days。"""
        now = self._clock()
        overdue: list[str] = []
        for policy in self._registry.list_all():
            last = self.last_drill(policy.domain)
            if last is None:
                overdue.append(policy.domain)
                continue
            if now - last.finished_at > datetime.timedelta(days=policy.drill_interval_days):
                overdue.append(policy.domain)
        return tuple(overdue)  # list_all 已按 domain 排序，天然确定
