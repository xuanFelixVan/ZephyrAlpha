# [BLUEPRINT] MOD-PLAN-012 | 待统筹登记（缺口总账 GAP-F-02 + 45号 §4 W2/W2b）
# [MODULE] zephyr.plan_engine.batch_boundary_runner
# [DOMAIN] D_PLAN
# [DEPENDENCIES] zephyr.plan_engine.tomorrow_boundary_planner(TomorrowBoundaryPlanner/TomorrowBoundary); zephyr.reporting.prediction_log_writer(log_prediction/ensure_prediction_log_table); zephyr.data.ch_reader（默认 CH 读取通道）; zephyr.data.table_registry（表名解析）
# [CONSUMERS] 作战室 W2 格内个股方案/W2b 持仓股明日边界（批量边界消费）; 盘后批量管线（候选清单 → 批量边界调度）
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] 单件计算复用 MOD-PLAN-001（本模块零边界算法）; 并发上限 ≤8（RULE-SEVEN）; 单符号失败不炸批量（失败留痕 error/no_data 分桶）; 落库 append-only 经 prediction_log_writer 公共 API（零裸 SQL 写库）; 落库失败 fail-open 不翻转计算结果; 输入校验 fail-closed（symbol 字符白名单防注入）; 错误消息不含 session_id
# [MODIFY-GUARD] blueprint.md
# [STABILITY] testing
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ValueError（trade_date/target_date/symbols/config 非法 fail-closed）; 单符号计算异常→item.status=error 留痕; CH/落库异常 fail-open（trace 留痕不外抛）
# [TESTS] tests/plan_engine/test_batch_boundary_runner.py
# [A_module] module_id=MOD-PLAN-012 | layer=module | stability=testing | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent

"""

BatchBoundaryRunner — 候选股边界批量调度管线 (MOD-PLAN-012)

缺口总账 GAP-F-02 落码：MOD-PLAN-001 TomorrowBoundary 单 symbol 已 production，
本模块补"主线候选股批量跑边界"的调度管线+结果落库（45号 §4 W2 格内方案/
W2b 持仓股边界的批量数据底座）。

管线口径（写清）：
    - 行情供给：kline_daily 当日 close + amplitude（%→小数折算；缺失/≤0 →
      MOD-PLAN-001 默认 3% 口径），单条 SQL 批量取数（IN 白名单字符校验）。
    - 并发：ThreadPoolExecutor（max_workers 默认 4，上限 8，RULE-SEVEN）——
      TomorrowBoundaryPlanner 无状态纯计算，线程安全；输出按输入符号顺序
      还原（确定性输出，与并发完成序无关）。
    - 失败留痕：kline 缺行 → no_data；计算异常（如非法收盘价
      BoundaryComputeError）→ error + 消息留痕；单符号失败不炸批量。
    - 落库：prediction_log "tomorrow_boundary" 族（复用 92号 §7.13 既有表，
      优先复用既有表不新建 DDL）；module="plan_engine.tomorrow_boundary_planner"
      （语义产出方口径，供 W2b 按产出模块回查），trade_date=target_date（边界
      生效日，默认=数据日，调用方应传次交易日）；payload 为确定性内容（不含
      时间戳）——同输入重跑=同内容 hash 幂等保首条，修正性重跑因内容变化
      自然产生新行（prediction_log append-only 语义）。

不做什么：不改 MOD-PLAN-001 单件算法/不做候选股挑选（候选清单由上游
         MOD-SIG-061/作战池供给）/不做盘中实时刷新（盘后批量管线）。

依据: 缺口总账 GAP-F-02；45_warroom_playbook §4 W2/W2b + §5（MOD-PLAN-001 契约）
SSoT: depgraph MOD-PLAN-012（待统筹登记）
Version: 0.1.0

# [ALGO_FLOW]
# 输入: 候选 symbol 清单 + 数据日 trade_date + 边界生效日 target_date
# 特征: kline_daily close/amplitude（批量单 SQL 取数）
# 算法: 符号白名单校验+去重 → 批量取行情 → 线程池并发单件计算 → 失败分桶留痕 → 落库
# 输出: BatchBoundaryResult（逐符号 ok/error/no_data + 边界 + 落库行 id + trace）

"""

from __future__ import annotations

import datetime
import logging
import math
import re
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Final, Sequence

from zephyr.plan_engine.tomorrow_boundary_planner import (
    TomorrowBoundary,
    TomorrowBoundaryPlanner,
)
from zephyr.reporting.prediction_log_writer import (
    ensure_prediction_log_table,
    log_prediction,
)

log = logging.getLogger(__name__)

__all__: Final = [
    "BOUNDARY_MODULE_LOG_NAME",
    "BOUNDARY_PREDICTION_TYPE",
    "BatchBoundaryConfig",
    "BatchBoundaryResult",
    "BatchBoundaryRunner",
    "BoundaryItemResult",
    "run_batch_boundaries",
]

# ── 口径常量 ──

BOUNDARY_MODULE_LOG_NAME: Final = "plan_engine.tomorrow_boundary_planner"  # prediction_log.module（语义产出方口径）
BOUNDARY_PREDICTION_TYPE: Final = "tomorrow_boundary"  # 边界落库族

DEFAULT_MAX_WORKERS: Final = 4  # 默认并发数
MAX_WORKERS_LIMIT: Final = 8  # 并发上限（RULE-SEVEN）
DEFAULT_AMPLITUDE: Final = 0.03  # 振幅缺省口径（与 MOD-PLAN-001 默认对齐）

_SYMBOL_RE: Final = re.compile(r"^[0-9A-Za-z._-]+$")  # symbol 白名单（防注入，fail-closed）

# SQL 模板常量（NO-BARE-SQL gate 豁免：_SQL_* 前缀，与 scenario_planner 同约定）
_SQL_KLINE_BATCH: Final = (
    "SELECT symbol_canonical, toFloat64(close) AS c, toFloat64(amplitude) AS amp "
    "FROM {table} FINAL WHERE trade_date = toDate('{trade_date}') "
    "AND symbol_canonical IN ({symbols})"
)


def _parse_tsv(tsv: str, ncols: int) -> list[list[str]]:
    """把 ch_reader.query 返回的 TSV 字符串解析成行列表（ncols 不足跳过该行）。"""
    if not tsv or not tsv.strip():
        return []
    rows: list[list[str]] = []
    for line in tsv.strip().split("\n"):
        vals = line.rstrip("\r").split("\t")
        if len(vals) >= ncols:
            rows.append(vals)
    return rows


def _safe_float(v: Any) -> float | None:
    """安全转 float；失败/NaN/Inf 返回 None。"""
    if v is None:
        return None
    try:
        f = float(v)
    except (TypeError, ValueError):
        return None
    return f if math.isfinite(f) else None


def _validate_iso_date(value: object, field: str) -> str:
    """ISO 交易日校验：YYYY-MM-DD 且为真实日期（fail-closed）。"""
    if not isinstance(value, str):
        raise ValueError(f"{field} 非法（须 YYYY-MM-DD 字符串）: {value!r}")
    try:
        datetime.date.fromisoformat(value)
    except ValueError as exc:
        raise ValueError(f"{field} 非真实日期: {value!r}") from exc
    return value


def _validate_symbol(symbol: object) -> str:
    """symbol 校验：非空+白名单字符（防 SQL 注入，fail-closed）。"""
    if not isinstance(symbol, str) or not symbol.strip():
        raise ValueError(f"symbol 非法（须非空字符串）: {symbol!r}")
    s = symbol.strip()
    if not _SYMBOL_RE.match(s):
        raise ValueError(f"symbol 含非法字符（白名单 [0-9A-Za-z._-]）: {symbol!r}")
    return s


# ── 配置契约 ──


@dataclass(frozen=True)
class BatchBoundaryConfig:
    """批量管线配置（默认值=设计口径）。"""

    max_workers: int = DEFAULT_MAX_WORKERS  # 并发数（≤8，RULE-SEVEN）
    default_amplitude: float = DEFAULT_AMPLITUDE  # 振幅缺省口径
    persist: bool = True  # 是否落库 prediction_log

    def __post_init__(self) -> None:
        if (
            isinstance(self.max_workers, bool)
            or not isinstance(self.max_workers, int)
            or not 1 <= self.max_workers <= MAX_WORKERS_LIMIT
        ):
            raise ValueError(
                f"max_workers 非法（须 1~{MAX_WORKERS_LIMIT} 整数，RULE-SEVEN 上限）: {self.max_workers!r}"
            )
        amp = _safe_float(self.default_amplitude)
        if amp is None or amp <= 0:
            raise ValueError(f"default_amplitude 非法（须正有限实数）: {self.default_amplitude!r}")
        if not isinstance(self.persist, bool):
            raise ValueError(f"persist 非法（须 bool）: {self.persist!r}")


DEFAULT_CONFIG: Final = BatchBoundaryConfig()


# ── 输出契约 ──


@dataclass(frozen=True)
class BoundaryItemResult:
    """单符号批量结果（留痕单元）。"""

    symbol: str
    status: str  # ok / no_data / error
    boundary: TomorrowBoundary | None
    error: str | None = None


@dataclass(frozen=True)
class BatchBoundaryResult:
    """批量边界结果（MOD-PLAN-012 输出契约，JSON 可序列化）。"""

    trade_date: str  # 数据日（行情取值日）
    target_date: str  # 边界生效日（落库 trade_date 口径）
    total: int  # 去重后符号数
    ok_count: int
    error_count: int
    no_data_count: int
    items: tuple[BoundaryItemResult, ...]  # 按输入符号顺序
    persisted_row_ids: tuple[int, ...]  # 落库行 id（仅 ok 且 persist=True）
    trace: dict[str, Any] = field(default_factory=dict)  # 通道/并发/落库留痕

    def to_dict(self) -> dict[str, Any]:
        """JSON 可序列化字典（computed_at 转 ISO 字符串）。"""
        return {
            "trade_date": self.trade_date,
            "target_date": self.target_date,
            "total": self.total,
            "ok_count": self.ok_count,
            "error_count": self.error_count,
            "no_data_count": self.no_data_count,
            "items": [
                {
                    "symbol": i.symbol,
                    "status": i.status,
                    "error": i.error,
                    "boundary": (
                        {
                            "symbol": i.boundary.symbol,
                            "box_upper": i.boundary.box_upper,
                            "box_lower": i.boundary.box_lower,
                            "max_add_position": i.boundary.max_add_position,
                            "no_add_price": i.boundary.no_add_price,
                            "must_exit_price": i.boundary.must_exit_price,
                            "breakout_confirm": i.boundary.breakout_confirm,
                            "computed_at": (
                                i.boundary.computed_at.isoformat()
                                if hasattr(i.boundary.computed_at, "isoformat")
                                else i.boundary.computed_at
                            ),
                        }
                        if i.boundary is not None
                        else None
                    ),
                }
                for i in self.items
            ],
            "persisted_row_ids": list(self.persisted_row_ids),
            "trace": dict(self.trace),
        }


# ── 批量调度器 ──


class BatchBoundaryRunner:
    """候选股边界批量调度器（MOD-PLAN-012）。

    CH 数据经 ch_client 注入（测试 mock/离线）；未注入走项目默认 CH 通道。
    库路径经 db_path 注入（None=DB_PATH SSoT，测试注入临时库）。
    """

    def __init__(
        self,
        ch_client: Callable[[str], str] | None = None,
        db_path: str | Path | None = None,
        config: BatchBoundaryConfig | None = None,
        planner: TomorrowBoundaryPlanner | None = None,
    ) -> None:
        self._config = config or DEFAULT_CONFIG
        self._ch = ch_client
        self._db_path = db_path
        self._planner = planner or TomorrowBoundaryPlanner()

    @staticmethod
    def _table(category_id: str, fallback: str) -> str:
        """按 category_id 解析全限定表名；注册表不可用降级 fallback（fail-open）。"""
        try:
            from zephyr.data.table_registry import get_registry

            return get_registry().table(category_id)
        except Exception as exc:  # noqa: BLE001 — fail-open：表名解析失败不阻塞主流程
            log.warning("表名解析失败 %s，降级 %s: %s", category_id, fallback, exc)
            return fallback

    def _load_market_states(
        self,
        trade_date: str,
        symbols: list[str],
        trace: dict[str, Any],
    ) -> dict[str, dict[str, float]]:
        """批量取行情：symbol_canonical → {close, amplitude}（单条 SQL）。

        CH 异常 → 空 dict + trace 留痕（fail-open，调用方全量 no_data 分桶）。
        """
        table = self._table("market_kline_daily", "c1_market.kline_daily")
        quoted = ",".join(f"'{s}'" for s in symbols)  # symbol 已过白名单校验
        sql = _SQL_KLINE_BATCH.format(table=table, trade_date=trade_date, symbols=quoted)
        try:
            if self._ch is not None:
                tsv = self._ch(sql)
            else:
                from zephyr.data import ch_reader

                tsv = ch_reader.query(sql)
        except Exception as exc:  # noqa: BLE001 — fail-open：通道异常不炸批量
            log.warning("kline_daily 批量取数异常 fail-open: %s", exc)
            trace["channels"]["kline_daily"] = f"error:{type(exc).__name__}:{exc}"
            return {}
        trace["channels"]["kline_daily"] = "ok"
        states: dict[str, dict[str, float]] = {}
        for sym, close, amp in _parse_tsv(tsv, 3):
            close_f = _safe_float(close)
            if close_f is None:
                continue
            state: dict[str, float] = {"close": close_f}
            amp_f = _safe_float(amp)
            # kline_daily amplitude 单位 % → 小数折算；缺失/≤0 → 缺省口径
            state["amplitude"] = amp_f / 100.0 if amp_f is not None and amp_f > 0 else self._config.default_amplitude
            states[sym] = state
        return states

    def _compute_one(self, symbol: str, state: dict[str, float]) -> BoundaryItemResult:
        """单件计算（线程池任务）：异常→error 留痕不抛。"""
        try:
            boundary = self._planner.compute_boundary(symbol, state)
            return BoundaryItemResult(symbol=symbol, status="ok", boundary=boundary)
        except Exception as exc:  # noqa: BLE001 — 单符号失败不炸批量，留痕分桶
            log.warning("边界计算失败留痕（symbol=%s）: %s: %s", symbol, type(exc).__name__, exc)
            return BoundaryItemResult(
                symbol=symbol,
                status="error",
                boundary=None,
                error=f"{type(exc).__name__}: {exc}",
            )

    def _persist(self, target_date: str, trade_date: str, items: list[BoundaryItemResult]) -> tuple[list[int], int]:
        """落库 prediction_log（ok 项）；返回 (行 id 列表, 失败计数)——fail-open。"""
        row_ids: list[int] = []
        errors = 0
        try:
            ensure_prediction_log_table(self._db_path)
        except Exception as exc:  # noqa: BLE001 — fail-open：建表失败后续写入必败，直接计数
            log.warning("prediction_log 建表失败 fail-open: %s: %s", type(exc).__name__, exc)
            return row_ids, sum(1 for i in items if i.status == "ok")
        for item in items:
            if item.status != "ok" or item.boundary is None:
                continue
            b = item.boundary
            try:
                row_ids.append(
                    log_prediction(
                        trade_date=target_date,
                        module=BOUNDARY_MODULE_LOG_NAME,
                        prediction_type=BOUNDARY_PREDICTION_TYPE,
                        payload={
                            "symbol": b.symbol,
                            "box_upper": b.box_upper,
                            "box_lower": b.box_lower,
                            "max_add_position": b.max_add_position,
                            "no_add_price": b.no_add_price,
                            "must_exit_price": b.must_exit_price,
                            "breakout_confirm": b.breakout_confirm,
                            "source_trade_date": trade_date,
                            "target_date": target_date,
                            "producer": "MOD-PLAN-012.batch_boundary_runner",
                        },
                        db_path=self._db_path,
                    )
                )
            except Exception as exc:  # noqa: BLE001 — fail-open：单行落库失败不翻转计算结果
                errors += 1
                log.warning("边界落库失败 fail-open（symbol=%s）: %s: %s", item.symbol, type(exc).__name__, exc)
        return row_ids, errors

    def run(
        self,
        trade_date: str,
        symbols: Sequence[str],
        target_date: str | None = None,
    ) -> BatchBoundaryResult:
        """批量调度主入口：候选清单 → 批量边界 + 失败留痕 + 结果落库。

        Args:
            trade_date: 数据日（行情取值日，fail-closed）。
            symbols: 候选 symbol 清单（去重保序；空清单合法→total=0）。
            target_date: 边界生效日（落库 trade_date 口径；None=数据日，
                生产调用方应传次交易日）。

        Returns:
            BatchBoundaryResult（逐符号留痕；任何单符号/通道/落库异常不炸）。

        Raises:
            ValueError: trade_date/target_date/symbols 非法（fail-closed）。
        """
        v_date = _validate_iso_date(trade_date, "trade_date")
        v_target = _validate_iso_date(target_date, "target_date") if target_date is not None else v_date
        seen: set[str] = set()
        uniq: list[str] = []
        for s in symbols:
            v_s = _validate_symbol(s)
            if v_s not in seen:
                seen.add(v_s)
                uniq.append(v_s)

        trace: dict[str, Any] = {"channels": {}, "max_workers": self._config.max_workers, "persist_errors": 0}
        if not uniq:
            return BatchBoundaryResult(
                trade_date=v_date,
                target_date=v_target,
                total=0,
                ok_count=0,
                error_count=0,
                no_data_count=0,
                items=(),
                persisted_row_ids=(),
                trace=trace,
            )

        states = self._load_market_states(v_date, uniq, trace)

        def _task(sym: str) -> BoundaryItemResult:
            state = states.get(sym)
            if state is None:
                return BoundaryItemResult(symbol=sym, status="no_data", boundary=None, error=None)
            return self._compute_one(sym, state)

        with ThreadPoolExecutor(max_workers=self._config.max_workers) as pool:
            computed = list(pool.map(_task, uniq))  # map 保输入序（确定性输出）

        items = list(computed)
        ok_count = sum(1 for i in items if i.status == "ok")
        error_count = sum(1 for i in items if i.status == "error")
        no_data_count = sum(1 for i in items if i.status == "no_data")

        row_ids: list[int] = []
        if self._config.persist and ok_count > 0:
            row_ids, persist_errors = self._persist(v_target, v_date, items)
            trace["persist_errors"] = persist_errors

        return BatchBoundaryResult(
            trade_date=v_date,
            target_date=v_target,
            total=len(uniq),
            ok_count=ok_count,
            error_count=error_count,
            no_data_count=no_data_count,
            items=tuple(items),
            persisted_row_ids=tuple(row_ids),
            trace=trace,
        )


# ── 主入口 ──


def run_batch_boundaries(
    trade_date: str,
    symbols: Sequence[str],
    ch_client: Callable[[str], str] | None = None,
    db_path: str | Path | None = None,
    config: BatchBoundaryConfig | None = None,
    target_date: str | None = None,
) -> BatchBoundaryResult:
    """候选股边界批量计算主入口（MOD-PLAN-012）。

    Args:
        trade_date: 数据日（行情取值日）。
        symbols: 候选 symbol 清单（主线候选/作战池/持仓股）。
        ch_client: CH 查询客户端（sql→TSV），可注入（测试 mock/离线）；
            None 时走项目默认 CH 通道。
        db_path: 库路径；None=DB_PATH SSoT（测试注入临时库）。
        config: 管线配置（None=默认 BatchBoundaryConfig()）。
        target_date: 边界生效日（None=数据日；生产应传次交易日）。

    Returns:
        BatchBoundaryResult（JSON 可序列化，落库经 prediction_log 既有表）。
    """
    return BatchBoundaryRunner(ch_client=ch_client, db_path=db_path, config=config).run(
        trade_date,
        symbols,
        target_date=target_date,
    )
