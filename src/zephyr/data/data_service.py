# [BLUEPRINT] MOD-L00-004 | docs/03_modules/_domain_data/data_source_integrator_blueprint.md
# [MODULE] zephyr.data.data_service
# [DOMAIN] D_DATA
# [DEPENDENCIES] zephyr.data.pit_query; zephyr.data.tick_redis_cache; zephyr.data_governance.core.lineage_tracker; zephyr.shared.contracts.selection_result; zephyr.shared.contracts.factor_signal
# [CONSUMERS] zephyr.backtest.core.data_handler; L3 策略层 sleeve
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 四能力一口径(实时/PIT/决策输入/审计追溯); 实时SLA<5ms; PIT认知截止不超前; 缺后端fail-closed; 无效信号不打包
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 实时/PIT后端未配置→DataServiceError; 键缺失→RealtimeResult(ok=False)(合法miss非异常)
# [TESTS] tests/zephyr/data/test_data_service.py
# [A_module] module_id=MOD-L00-004 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
"""数据服务接口层——统一数据服务门面（CAND-DAT-008 / B13-04033）。

min_build_spec 对齐（深挖裁定=做 P0，B1-00645 门户重复裁定亦归并本入口）：
  四能力统一入口与 SLA：
    1. 实时查询 get_realtime        — Redis 读端（tick:{symbol}:latest Hash），SLA <5ms
    2. PIT 回测 query_pit*          — 委派 FinancialPITQuery AS OF JOIN；双时态
                                      （认知截止 knowledge_time × 业务时点 valid_time）
    3. 决策输入打包 pack_decision_input — 因子+信号 → L3 策略层 SignalInput 契约
                                      （is_valid=False 信号剔除，universe 缺省按标的派生）
    4. 审计追溯 audit_trail         — 血缘上下游（LineageTracker）+ 事件 → 合规报告

后端全部注入式（redis_client / pit / lineage_tracker / event_reader / clock），
本模块只做口径统一、契约适配与 SLA 计量，不重建 Redis/CH/血缘存储。
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass
from datetime import date, datetime, timezone
from typing import Any, Callable, Iterable, Protocol

from zephyr.data.pit_query import tsv_to_records
from zephyr.shared.contracts.selection_result import SignalInput

log = logging.getLogger(__name__)

__all__ = [
    "SLA_TARGETS",
    "DataService",
    "DataServiceError",
    "RealtimeResult",
]

UTC = timezone.utc

# 四能力 SLA（毫秒）。realtime 对齐候选注册表 Redis GET <5ms 硬口径；
# 其余三档为门面默认考核线（PIT 走 CH 秒级以内、打包/追溯为内存操作）。
SLA_TARGETS: dict[str, float] = {
    "realtime": 5.0,
    "pit": 1000.0,
    "decision_input": 50.0,
    "audit_trail": 2000.0,
}


class DataServiceError(Exception):
    """数据服务门面违规：后端未配置或调用参数非法（fail-closed）。"""


class _PITBackend(Protocol):
    """PIT 后端协议（FinancialPITQuery 子集）。"""

    def as_of(self, table: str, symbol: str, query_time: Any, columns: str = "*") -> str: ...


class _LineageBackend(Protocol):
    """血缘后端协议（LineageTracker 子集）。"""

    def get_upstream(self, node: str) -> list[str]: ...

    def get_downstream(self, node: str) -> list[str]: ...


@dataclass(frozen=True)
class RealtimeResult:
    """实时查询结果。ok=False+value=None 为合法 miss（键不存在），非异常。"""

    symbol: str
    value: Any
    ok: bool
    latency_ms: float
    sla_met: bool


class DataService:
    """统一数据服务门面（四能力一口径 + SLA 计量）。

    Usage:
        svc = DataService(redis_client=r, pit=FinancialPITQuery(), lineage_tracker=lt)
        svc.get_realtime("000001.SZ")
        svc.query_pit("balance_sheet", "000001.SZ", date(2026, 8, 25), columns="symbol,report_period")
        svc.pack_decision_input(signals, as_of_date=day, regime_budget=0.6)
        svc.audit_trail("signal.x")
        svc.sla_report()
    """

    def __init__(
        self,
        redis_client: Any | None = None,
        pit: _PITBackend | None = None,
        lineage_tracker: _LineageBackend | None = None,
        event_reader: Callable[[str], Iterable[dict[str, Any]]] | None = None,
        clock: Callable[[], float] | None = None,
    ) -> None:
        self._redis = redis_client
        self._pit = pit
        self._lineage = lineage_tracker
        self._event_reader = event_reader
        self._clock = clock if clock is not None else time.perf_counter
        # capability -> [(latency_ms, sla_met), ...]
        self._sla: dict[str, list[tuple[float, bool]]] = {k: [] for k in SLA_TARGETS}

    # ── SLA 计量 ──
    def _record(self, capability: str, started: float) -> float:
        latency_ms = (self._clock() - started) * 1000.0
        sla_met = latency_ms <= SLA_TARGETS[capability]
        self._sla[capability].append((latency_ms, sla_met))
        return latency_ms

    def sla_report(self) -> dict[str, dict[str, float | int]]:
        """各能力 SLA 汇总：调用数/违约数/最坏延迟/目标线。"""
        report: dict[str, dict[str, float | int]] = {}
        for cap, samples in self._sla.items():
            report[cap] = {
                "calls": len(samples),
                "violations": sum(1 for _lat, met in samples if not met),
                "max_latency_ms": max((lat for lat, _met in samples), default=0.0),
                "sla_ms": SLA_TARGETS[cap],
            }
        return report

    # ── 能力1：实时查询（Redis GET <5ms）──
    def get_realtime(self, symbol: str) -> RealtimeResult:
        """读 tick:{symbol}:latest 热键（H1 读端物化视图），SLA <5ms。

        Raises:
            DataServiceError: 实时后端（redis_client）未配置
        """
        if self._redis is None:
            raise DataServiceError("实时查询后端未配置（redis_client=None），fail-closed")
        started = self._clock()
        key = f"tick:{symbol}:latest"
        if hasattr(self._redis, "hgetall"):
            value = self._redis.hgetall(key) or None
        else:
            value = self._redis.get(key)
        latency_ms = self._record("realtime", started)
        sla_met = latency_ms <= SLA_TARGETS["realtime"]
        if not sla_met:
            log.warning("实时查询 SLA 违约: %s %.3fms > %.1fms", symbol, latency_ms, SLA_TARGETS["realtime"])
        return RealtimeResult(
            symbol=symbol,
            value=value,
            ok=value is not None,
            latency_ms=latency_ms,
            sla_met=sla_met,
        )

    # ── 能力2：PIT 回测（AS OF JOIN + 双时态）──
    def query_pit(
        self,
        table: str,
        symbol: str,
        as_of_date: date | datetime | str,
        columns: str = "*",
    ) -> list[dict[str, Any]]:
        """AS OF JOIN：返回 symbol 在 as_of_date（认知截止）可见的最新版本记录。

        委派 FinancialPITQuery.as_of（announce_date <= 认知截止，LIMIT 1 BY 版本对齐）。
        columns 显式给出时兼作 TSV 解析 schema；'*' 时按 col_i 整数键返回。

        Raises:
            DataServiceError: PIT 后端未配置
        """
        if self._pit is None:
            raise DataServiceError("PIT 查询后端未配置（pit=None），fail-closed")
        started = self._clock()
        tsv = self._pit.as_of(table, symbol, as_of_date, columns)
        column_names = [c.strip() for c in columns.split(",")] if columns != "*" else None
        records = tsv_to_records(tsv, column_names)
        self._record("pit", started)
        return records

    def query_pit_bitemporal(
        self,
        table: str,
        symbol: str,
        valid_time: date,
        knowledge_time: date | datetime | str,
        columns: str = "*",
    ) -> list[dict[str, Any]]:
        """双时态 PIT：认知截止 knowledge_time 取版本，业务时点 valid_time 过滤报告期。

        第一时态（认知/事务时间）：announce_date <= knowledge_time（as_of 委派完成）；
        第二时态（业务/有效时间）：report_period <= valid_time（本层过滤）。
        记录无 report_period 列时不做业务时点过滤（保守全量返回）。
        """
        records = self.query_pit(table, symbol, knowledge_time, columns)
        vt = valid_time.isoformat()
        return [r for r in records if "report_period" not in r or str(r["report_period"]) <= vt]

    # ── 能力3：决策输入打包（因子+信号 → L3 契约）──
    def pack_decision_input(
        self,
        signals: list[Any],
        as_of_date: date,
        universe: list[str] | None = None,
        regime_budget: float = 0.0,
        metadata: dict[str, Any] | None = None,
    ) -> SignalInput:
        """因子+信号打包为 L3 策略层标准入参 SignalInput。

        is_valid=False 的信号剔除（CTR-002 语义：下游 MUST 跳过）；
        universe 缺省按有效信号 symbol 去重排序派生。
        """
        started = self._clock()
        kept = [s for s in signals if getattr(s, "is_valid", True)]
        derived = universe if universe is not None else sorted({s.symbol for s in kept})
        packed = SignalInput(
            as_of_date=as_of_date,
            universe=list(derived),
            regime_budget=regime_budget,
            signals=kept,
            metadata=metadata or {},
        )
        self._record("decision_input", started)
        return packed

    # ── 能力4：审计追溯（血缘+事件 → 合规报告）──
    def audit_trail(self, node: str) -> dict[str, Any]:
        """合成节点合规报告：血缘上下游 + 事件轨迹 + 生成时点。"""
        started = self._clock()
        upstream = self._lineage.get_upstream(node) if self._lineage is not None else []
        downstream = self._lineage.get_downstream(node) if self._lineage is not None else []
        events = list(self._event_reader(node)) if self._event_reader is not None else []
        self._record("audit_trail", started)
        return {
            "node": node,
            "upstream": list(upstream),
            "downstream": list(downstream),
            "events": events,
            "generated_at": datetime.now(UTC).isoformat(),
        }


def main() -> None:
    """入口——待实现。"""


if __name__ == "__main__":
    main()
