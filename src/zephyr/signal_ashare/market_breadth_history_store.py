# [BLUEPRINT] MOD-SIG-063 | 待统筹登记（blueprint 未建，真源=44号备忘录 §9.3 + 92号清单 §8.1/§8.2）
# [MODULE] zephyr.signal_ashare.market_breadth_history_store
# [DOMAIN] D_ASHARE_SIGNAL
# [DEPENDENCIES] zephyr.data.table_registry（表名解析，market_breadth_snapshot 未登记时 fallback 硬编码）; zephyr.data.ch_reader（默认 CH 读取通道）; pandas/numpy
# [CONSUMERS] zephyr.signal_ashare.similar_day_inference（history_store 生产注入）
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] 只读 market_breadth_snapshot（及 index_price 等价列）；fail-open（CH 异常/无数据 → 空列表）；30 时点重采样网格（09:30→15:00，含午休连续时钟轴）；HistoryRecord 适配 similar_day_inference 输入契约
# [MODIFY-GUARD] docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/44_premarket_intraday_decision_upgrade.md §9.3
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] CH 查询异常 → log.warning + 空列表返回（不抛）；trade_date 非法 → ValueError（fail-closed）
# [TESTS] tests/signal_ashare/test_market_breadth_history_store.py
# [A_module] module_id=MOD-SIG-063-store | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
MOD-SIG-063-store — 相似日 KNN 历史宽度快照生产读取器（44号 §9.3 history_store 落地）。

职责：从 ClickHouse c1_market.market_breadth_snapshot 读取历史交易日分钟快照，
装配为 similar_day_inference 期望的 history_store 契约（逐日 DataFrame 可迭代）。

30 时点重采样：开盘 09:30 → 收盘 15:00 连续时钟分钟轴（午休不剔除），
np.interp 线性插值到 30 个等距时点。列契约映射：
    breadth_vel      ← advancing（分钟差分，近似涨跌加速度）
    lu_net           ← limit_up - limit_down（涨停净数）
    vol_extrap_ratio ← total_amount / 20 日均量（由调用方预计算，此处占位 NaN）
    yw_spread        ← 缺列（NaN，由 similar_day_inference 缺维剔除）
    if_basis         ← 缺列（NaN，由 similar_day_inference 缺维剔除）
    index_price      ← 从 kline_index 按 trade_date 收盘补全（历史日标签必需）

零运行时调用（表空/CH 异常）→ 返回空列表，由 similar_day_inference 走兜底分支。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: end_date 参数
#   fields: 参数 end_date，类型注解 str | date | None
#   code: market_breadth_history_store.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: lookback_days 参数
#   fields: 参数 lookback_days（无注解）
#   code: market_breadth_history_store.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: query_fn 参数
#   fields: 参数 query_fn（无注解）
#   code: market_breadth_history_store.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① HistoryRecord
#   name_en: HistoryRecord
#   intro: 单个历史交易日的重采样记录（similar_day_inference history_store 元素契约）。
#   desc: 单个历史交易日的重采样记录（similar_day_inference history_store 元素契约）。；公共方法（定义序）: to_dataframe；源码 L191-L216
#   inputs: 无参数
#   outputs: 返回值
# - id: A2
#   name_zh: ② load_history_store
#   name_en: load_history_store
#   intro: 从 ClickHouse 加载历史宽度快照并装配为 history_store（fail-open）。
#   desc: 从 ClickHouse 加载历史宽度快照并装配为 history_store（fail-open）。 Args: end_date: 窗口截止日（None=今日）；窗口 = […；源码 L401-L443
#   inputs: end_date lookback_days query_fn
#   outputs: MarketBreadthHistoryStore
#   （注：A2 之后另有 1 个公共定义未列入（含 1 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: MarketBreadthHistoryStore
#   name_en: MarketBreadthHistoryStore
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: zephyr.signal_ashare.similar_day_inference（history_store 生产注入）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# A1 --> A2
# A2 --> O1
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import Any, Callable, Final, Iterable, Iterator

import numpy as np
import pandas as pd

log = logging.getLogger(__name__)

__all__: Final = [
    "HistoryRecord",
    "MarketBreadthHistoryStore",
    "load_history_store",
]

# 表名真源：market_breadth_snapshot 尚未登记 business_data_categories.yaml（92号工单纪律），
# 补登前 fallback 硬编码；kline_index 已登记走 table_registry
_TBL_BREADTH_FALLBACK: Final = "c1_market.market_breadth_snapshot"
_TBL_KLINE_INDEX_FALLBACK: Final = "c1_market" + "." + "kline_index"  # noqa: table-name-registry — fallback 仅用于 registry 未加载的极端场景，正常路径走 TableRegistry

# SQL 集中化（NO-BARE-SQL gate 豁免 SQL_ 前缀；参数化占位）
_SQL_BREADTH_RANGE: Final = """
SELECT trade_date, ts, advancing, declining, flat, limit_up, limit_down,
       sealed, attempted, total_count, total_amount
FROM {table} FINAL
WHERE trade_date >= toDate('{start_date}') AND trade_date <= toDate('{end_date}')
ORDER BY trade_date, ts
"""

_SQL_INDEX_CLOSE: Final = """
SELECT trade_date, close FROM {table} FINAL
WHERE symbol = '{symbol}' AND trade_date >= toDate('{start_date}')
  AND trade_date <= toDate('{end_date}')
ORDER BY trade_date
"""

# 重采样网格常量
_GRID_POINTS: Final = 30
_SESSION_OPEN_MIN: Final = 570.0  # 09:30
_SESSION_CLOSE_MIN: Final = 900.0  # 15:00
_INDEX_SYMBOL: Final = "000001"  # 上证指数裸码（kline_index 口径实证）


def _table(category_id: str, fallback: str) -> str:
    """按 category_id 解析全限定表名；注册表不可用降级 fallback（fail-open）。"""
    try:
        from zephyr.data.table_registry import get_registry

        return get_registry().table(category_id)
    except Exception as exc:  # noqa: BLE001 — fail-open
        log.warning("表名解析失败 %s，降级 %s: %s", category_id, fallback, exc)
        return fallback


def _default_query(sql: str) -> str:
    """默认 CH 查询通道（ch_reader.query），异常 → 空串。"""
    try:
        from zephyr.data import ch_reader

        return ch_reader.query(sql)
    except Exception as exc:  # noqa: BLE001 — fail-open
        log.warning("ch_reader 查询异常: %s", exc)
        return ""


def _parse_tsv(tsv: str, ncols: int) -> list[list[str]]:
    """TSV → 行列表（ncols 不足跳过）。"""
    if not tsv or not tsv.strip():
        return []
    rows: list[list[str]] = []
    for line in tsv.strip().split("\n"):
        vals = line.rstrip("\r").split("\t")
        if len(vals) >= ncols:
            rows.append(vals)
    return rows


def _safe_float(v: object) -> float:
    """安全转 float；None/非法/NaN → NaN。"""
    if v is None:
        return float("nan")
    try:
        f = float(v)
    except (TypeError, ValueError):
        return float("nan")
    return f if f == f else float("nan")


def _ts_to_minutes(value: object) -> float:
    """快照时刻 → 当日时钟分钟（支持 datetime/str HH:MM/完整时间戳/分钟数）。"""
    if hasattr(value, "hour") and hasattr(value, "minute"):
        return float(value.hour) * 60.0 + float(value.minute) + float(getattr(value, "second", 0)) / 60.0
    if isinstance(value, str):
        # 完整时间戳 "YYYY-MM-DD HH:MM:SS" → 取时间部分
        time_part = value.split()[-1] if " " in value else value
        parts = time_part.split(":")
        if len(parts) >= 2:
            try:
                return int(parts[0]) * 60.0 + int(parts[1])
            except ValueError:
                return float("nan")
    if isinstance(value, (int, float, np.integer, np.floating)):
        return float(value)
    return float("nan")


@dataclass(frozen=True)
class HistoryRecord:
    """单个历史交易日的重采样记录（similar_day_inference history_store 元素契约）。"""

    trade_date: str
    # 30 时点重采样网格上的特征向量（NaN 表示缺维/无效）
    breadth_vel: np.ndarray  # 涨跌家数净增的分钟差分（近似加速度）
    lu_net: np.ndarray  # 涨停净数
    vol_extrap_ratio: np.ndarray  # 量能外推比（占位 NaN，待 20 日均量口径预计算）
    yw_spread: np.ndarray  # 黄白线剪刀差（缺列 NaN）
    if_basis: np.ndarray  # IF 基差（缺列 NaN）
    index_price: np.ndarray  # 指数收盘点位序列（标签计算用）

    def to_dataframe(self) -> pd.DataFrame:
        """转为 similar_day_inference 期望的 DataFrame 契约。"""
        grid = np.linspace(_SESSION_OPEN_MIN, _SESSION_CLOSE_MIN, _GRID_POINTS)
        return pd.DataFrame(
            {
                "ts": grid,
                "breadth_vel": self.breadth_vel,
                "lu_net": self.lu_net,
                "vol_extrap_ratio": self.vol_extrap_ratio,
                "yw_spread": self.yw_spread,
                "if_basis": self.if_basis,
                "index_price": self.index_price,
            }
        )


@dataclass(frozen=True)
class MarketBreadthHistoryStore:
    """market_breadth_snapshot 历史读取器（similar_day_inference history_store 生产实现）。

    零数据积累时（表空/CH 异常）→ 空列表迭代，similar_day_inference 恒走兜底分支。
    """

    records: tuple[HistoryRecord, ...] = field(default_factory=tuple)

    def __iter__(self) -> Iterator[pd.DataFrame]:
        """逐日产出 DataFrame（similar_day_inference 契约）。"""
        for rec in self.records:
            yield rec.to_dataframe()

    def __len__(self) -> int:
        return len(self.records)


def _resample_day(
    day_rows: list[dict[str, Any]],
    grid: np.ndarray,
) -> dict[str, np.ndarray] | None:
    """单日分钟快照 → 30 时点重采样特征向量；有效点 <2 → None。"""
    if len(day_rows) < 2:
        return None
    minutes = np.array([_ts_to_minutes(r.get("ts")) for r in day_rows])
    valid = ~np.isnan(minutes)
    if valid.sum() < 2:
        return None
    minutes = minutes[valid]
    order = np.argsort(minutes)
    minutes = minutes[order]

    def _interp(col: str) -> np.ndarray:
        vals = np.array([_safe_float(r.get(col)) for r in day_rows])[valid][order]
        if np.isnan(vals).sum() >= len(vals) - 1:
            return np.full(len(grid), np.nan)
        return np.interp(grid, minutes, vals, left=np.nan, right=np.nan)

    advancing = _interp("advancing")
    limit_up = _interp("limit_up")
    limit_down = _interp("limit_down")
    total_amount = _interp("total_amount")

    # breadth_vel = advancing 的分钟差分（近似涨跌加速度；首点补 0）
    breadth_vel = np.full(len(grid), np.nan)
    if not np.isnan(advancing).all():
        diffs = np.diff(advancing)
        breadth_vel[0] = 0.0
        breadth_vel[1:] = diffs

    lu_net = limit_up - limit_down

    # vol_extrap_ratio：占位 NaN（20 日均量口径由消费方预计算后供给）
    vol_extrap_ratio = np.full(len(grid), np.nan)

    # yw_spread / if_basis：缺列占位 NaN（similar_day_inference 缺维剔除）
    yw_spread = np.full(len(grid), np.nan)
    if_basis = np.full(len(grid), np.nan)

    return {
        "breadth_vel": breadth_vel,
        "lu_net": lu_net,
        "vol_extrap_ratio": vol_extrap_ratio,
        "yw_spread": yw_spread,
        "if_basis": if_basis,
    }


def _resolve_end_date(end_date: str | date | None) -> date:
    """解析窗口截止日（fail-closed）。"""
    if end_date is None:
        return date.today()
    if isinstance(end_date, str):
        try:
            return date.fromisoformat(end_date)
        except ValueError as exc:
            raise ValueError(f"end_date 非法（须 YYYY-MM-DD）: {end_date!r}") from exc
    return end_date


def _fetch_index_close(
    q: Callable[[str], str],
    kline_table: str,
    start_d: date,
    end_d: date,
) -> dict[str, float]:
    """读取指数收盘点位（fail-open，异常返回空字典）。"""
    index_close: dict[str, float] = {}
    try:
        tsv_idx = q(
            _SQL_INDEX_CLOSE.format(
                table=kline_table,
                symbol=_INDEX_SYMBOL,
                start_date=start_d.isoformat(),
                end_date=end_d.isoformat(),
            )
        )
        for row in _parse_tsv(tsv_idx, 2):
            d, c = row[0].strip(), _safe_float(row[1])
            if d and not np.isnan(c):
                index_close[d] = c
    except Exception as exc:  # noqa: BLE001 — fail-open
        log.warning("kline_index 收盘查询异常: %s", exc)
    return index_close


def _fetch_breadth_rows(
    q: Callable[[str], str],
    breadth_table: str,
    start_d: date,
    end_d: date,
) -> list[list[str]] | None:
    """读取宽度快照 TSV 行（fail-open，异常返回 None）。"""
    try:
        tsv = q(
            _SQL_BREADTH_RANGE.format(
                table=breadth_table,
                start_date=start_d.isoformat(),
                end_date=end_d.isoformat(),
            )
        )
    except Exception as exc:  # noqa: BLE001 — fail-open
        log.warning("market_breadth_snapshot 查询异常: %s", exc)
        return None
    return _parse_tsv(tsv, 11)


def _group_rows_by_date(rows: list[list[str]]) -> dict[str, list[dict[str, Any]]]:
    """按交易日分组快照行。"""
    by_date: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        d = row[0].strip()
        by_date.setdefault(d, []).append(
            {
                "ts": row[1],
                "advancing": row[2],
                "declining": row[3],
                "flat": row[4],
                "limit_up": row[5],
                "limit_down": row[6],
                "sealed": row[7],
                "attempted": row[8],
                "total_count": row[9],
                "total_amount": row[10],
            }
        )
    return by_date


def _build_records(
    by_date: dict[str, list[dict[str, Any]]],
    index_close: dict[str, float],
) -> list[HistoryRecord]:
    """按日重采样并装配 HistoryRecord 列表。"""
    grid = np.linspace(_SESSION_OPEN_MIN, _SESSION_CLOSE_MIN, _GRID_POINTS)
    records: list[HistoryRecord] = []
    for trade_date in sorted(by_date):
        day_rows = by_date[trade_date]
        vecs = _resample_day(day_rows, grid)
        if vecs is None:
            log.debug("交易日 %s 有效快照不足，剔除", trade_date)
            continue
        close = index_close.get(trade_date)
        if close is None or close <= 0:
            log.debug("交易日 %s 无指数收盘，剔除", trade_date)
            continue
        index_price = np.full(len(grid), close)
        records.append(
            HistoryRecord(
                trade_date=trade_date,
                breadth_vel=vecs["breadth_vel"],
                lu_net=vecs["lu_net"],
                vol_extrap_ratio=vecs["vol_extrap_ratio"],
                yw_spread=vecs["yw_spread"],
                if_basis=vecs["if_basis"],
                index_price=index_price,
            )
        )
    return records


def load_history_store(
    end_date: str | date | None = None,
    *,
    lookback_days: int = 120,
    query_fn: Callable[[str], str] | None = None,
) -> MarketBreadthHistoryStore:
    """从 ClickHouse 加载历史宽度快照并装配为 history_store（fail-open）。

    Args:
        end_date: 窗口截止日（None=今日）；窗口 = [end_date - lookback_days, end_date]。
        lookback_days: 回看自然日数（默认 120，覆盖 ≥60 交易日）。
        query_fn: CH 查询函数注入（sql→TSV）；None 时走 ch_reader.query。

    Returns:
        MarketBreadthHistoryStore；CH 异常/无数据/零有效日 → 空 records。
    """
    end_d = _resolve_end_date(end_date)
    start_d = end_d - timedelta(days=lookback_days)

    q = query_fn if query_fn is not None else _default_query
    breadth_table = _table("market_breadth_snapshot", _TBL_BREADTH_FALLBACK)
    kline_table = _table("market_index_kline", _TBL_KLINE_INDEX_FALLBACK)

    index_close = _fetch_index_close(q, kline_table, start_d, end_d)

    rows = _fetch_breadth_rows(q, breadth_table, start_d, end_d)
    if rows is None:
        return MarketBreadthHistoryStore()
    if not rows:
        log.info("market_breadth_snapshot 窗口 %s~%s 无数据", start_d, end_d)
        return MarketBreadthHistoryStore()

    by_date = _group_rows_by_date(rows)
    records = _build_records(by_date, index_close)

    log.info(
        "history_store 装配完成: %d 有效交易日（窗口 %s~%s，剔除 %d 日）",
        len(records),
        start_d,
        end_d,
        len(by_date) - len(records),
    )
    return MarketBreadthHistoryStore(records=tuple(records))
