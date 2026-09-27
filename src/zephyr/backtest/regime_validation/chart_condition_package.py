# [BLUEPRINT] MOD-BT-COND-PACKAGE | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] zephyr.backtest.regime_validation.chart_condition_package
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] numpy; pandas; zephyr.backtest.regime_validation.condition_package; zephyr.data.table_registry; zephyr.infrastructure.database_service
# [CONSUMERS] scripts/backtest/condition_attribution.py（load_pack 目录契约不变即消费本包产物）; scripts/governance/chart_wiring/generate_chart_wiring_inventory.py（接线盘点读轴声明）; tests/backtest/test_chart_condition_package.py; docs/_working/three_piece_infra/p0_chart/CASE.md
# [STARTUP] imported
# [MATURITY] experimental
# [TTL] permanent
# [INVARIANTS] 图形信号=考试条件轴，禁作独立交易信号（学术证伪基线 Marshall 2006 + 波 10 硬约束，10_wave_plan 波 10 段）；
#   零下单/零生产写：本件只产条件包与逐胞统计，不写 CH、不写 n_trial_ledger、不发信号；
#   轴复用不重建：灰度档/状态轴/地板口径全部 import 自 condition_package（单一真源，禁第二套边界）；
#   形态真源=c1_market.market_pattern_event（裁定#233 起蜡烛唯一真源在图形域，market_technical_indicator.candle_pattern 列已停产）；
#   regime 口径分治：本包状态轴=F4_BDI_MOMENTUM_Z20 三态；事件表 regime_tag=regime_detector 七态（r1..r12），
#   两者无在册映射（本道实测 config/src/scripts 零命中）→ 禁混用，混用即轴污染；
#   PIT：跨周期对齐只允许 merge_asof(direction="backward")+allow_exact_matches=False，高周期值只在该 bar 收盘时刻之后可见；
#   逐日图形状态=横截面广度（同日 向上/向下 事件去重标的计数比），非任何个股触发；
#   30 日地板不达 ⇒ cell_id=None 下沉 conditional-free（禁凑 n、禁当独立样本）；
#   无统计=None 不是 0（沿用 PatternWinRateProvider 契约）；
#   fail-closed：未知状态字面量 / 事件空框 / 轴零重叠日 / 计数为负 一律抛，禁静默降级
# [MODIFY-GUARD] tests/backtest/test_chart_condition_package.py
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ValueError(未知 grey_band/state/chart_state 字面量、负计数、越界比例)；
#   RuntimeError(CH reader 不可得 / 事件查询空结果 / 轴零重叠日)；KeyError(必需列缺失)
# [TESTS] tests/backtest/test_chart_condition_package.py
"""图形条件轴输入包（波 10 · G-A.2 接线——把已在库的图形信号接成考试条件轴）。

照 `condition_package.py`（MOD-BT-COND-PACKAGE，9 胞先例）的模式建第三轴：

    图形信号状态化（逐日 × 逐族）→ 条件胞 = 图形档 × 情绪灰度档 × 大盘状态档

缺口是"接线"不是"建库"：83 条蜡烛目录（PAT-CANDLE-001..083）与 34,338,780 条
图形事件（实测 2026-09-26，只读计数）在库，事件→条件轴这一段没有。本件补这一段：

1. `load_market_pattern_events` 用**会抛错**的读通道（DatabaseService reader 角色）
   读 market_pattern_event 有界窗口（禁 ch_reader.query 下标直取，TSV 字符串陷阱）；
2. `build_chart_daily_state` 把逐标的逐日事件压成**市场级广度标签**
   （chart_bull/chart_bear/chart_mixed/chart_none，边界冻结 ±0.2）——图形信号在此
   只作为"当天市场处于什么图形状态"的条件轴，不构成任何买卖信号；
3. `build_chart_condition_pack` 与 condition_package 的两轴交叉、复用其 30 日地板；
4. `align_backward` 是 G-C.1 的 PIT 口径件（多周期对齐唯一合法姿势 + 前视红证）；
5. `cell_win_rate` 是 G-A.3 的接线桥：事件×前视收益 → 胞级命中率，
   样本不足返回 None（不返回 0），并产 `__baseline__` 对照行。

产物文件名与 condition_package.save_pack 同构（condition_pack_*.csv.gz/.csv/.json），
因此 `scripts/backtest/condition_attribution.py` 的 load_pack 消费面零改动即可
归因本包（真消费而非装饰：判读端读 cell_id/cell_eligible 出胞级主效应表）。

# [ALGO_FLOW] external: docs/03_modules/_domain_backtest/algo_flow/chart_condition_package.yaml
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date as _date
from pathlib import Path
from typing import Any, Final, Iterable

import pandas as pd

from zephyr.backtest.regime_validation.condition_package import (
    _BAND_LABELS,
    _CELL_FLOOR_DAYS,
    ConditionPack,
    # 落盘实现唯一真源=condition_package.save_pack（FUNCTION-DUP/net-zero：
    # 同行为禁第二实现，本件按同构文件名直接复用，import 即对外再导出）
    save_pack,
)
from zephyr.data.table_registry import get_registry

# ── 冻结口径（新增即改语义，须过波 12 统一窗口，禁在本道调参）────────────
_CHART_RATIO_EDGES: Final = (-0.2, 0.2)  # 广度比=(n_up-n_down)/(n_up+n_down)；±0.2 双侧含入（红证测试钉）
_CHART_STATE_LABELS: Final = ("chart_bear", "chart_mixed", "chart_bull", "chart_none")
_MIN_CELL_EVENTS_FOR_STATE: Final = 1  # 当日该族 0 事件=chart_none（不是"弱空"）
_FWD_WINDOWS: Final = (1, 5, 10, 20)  # 与 market_pattern_win_rate.fwd_window 同口径
_BASELINE_ID: Final = "__baseline__"  # 与 provider/物化表同键名
_MIN_SAMPLE: Final = 30  # 与 schema low_sample(n<30) 同口径

# 事件表 pattern_class 封闭集 + 目录 REG-PAT-001 pattern_class 双词表 → 考试轴族标签
# （真源：schemas market_pattern_event 注释 / chart_pattern_registry.yaml pattern_classes 节）
_FAMILY_BY_CLASS: Final = {
    "K线": "candle",
    "candlestick_pattern": "candle",
    "缠论": "chanlun",
    "chanlun": "chanlun",
    "波浪": "chanlun",  # 波浪与缠论同族观察（本道实测波浪零事件，见 CASE.md）
    "elliott_wave": "chanlun",
}
# 族名兜底 token（pattern_class 不在册时用事件名/pattern_id 词元分类）
_FALSE_BREAKOUT_TOKENS: Final = ("假突破", "陷阱", "反杀", "busted", "2b", "trap", "hikkake")
_MANIPULATOR_TOKENS: Final = ("庄", "吸筹", "派发", "弹簧", "出货", "wyckoff", "spring", "accumul")
# Owner 点名四族 + 其余归 other（other 仍是合法条件轴，只是族名未细化）
CHART_AXIS_FAMILIES: Final = ("candle", "chanlun", "false_breakout", "manipulator", "other")
_FAMILY_ZH: Final = {  # 展示层标签（非判据；三层翻译在册义务见 register_manifest）
    "candle": "蜡烛形态",
    "chanlun": "缠论结构",
    "false_breakout": "假突破",
    "manipulator": "庄股行为",
    "other": "其它图形族",
}

_EVENT_CATEGORY: Final = (
    "market_pattern_event"  # 逻辑品类名 → c1_market.market_pattern_event（TableRegistry 真源，禁表名字面量）
)
_REQUIRED_EVENT_COLUMNS = ("anchor_trade_date", "direction", "pattern_id", "pattern_class", "symbol")


def event_table() -> str:
    """事件表全名——唯一合法取法=TableRegistry 按品类解析（fail-closed，禁凭记忆编表名）。"""
    return get_registry().table(_EVENT_CATEGORY)


# ── 族分类 ────────────────────────────────────────────────────
def classify_chart_family(pattern_id: str, name: str, pattern_class: str) -> str:
    """事件三列 → 考试轴族标签（封闭集，未知字面量归 other 不抛）。"""
    if pattern_class in _FAMILY_BY_CLASS:
        return _FAMILY_BY_CLASS[pattern_class]
    blob = f"{pattern_id} {name}".lower()
    if any(tok.lower() in blob for tok in _FALSE_BREAKOUT_TOKENS):
        return "false_breakout"
    if any(tok.lower() in blob for tok in _MANIPULATOR_TOKENS):
        return "manipulator"
    if pattern_class in ("反转", "持续", "趋势", "支撑阻力"):
        return "other"
    return "other"


# ── 图形状态化（逐日逐族）──────────────────────────────────────
def chart_state_from_breadth(n_up: int, n_down: int) -> str:
    """同日同族 向上/向下 去重标的数 → 市场级图形状态标签（边界冻结）。

    红证口径：喂错计数（负数）必抛，不静默纠正。
    """
    if n_up < 0 or n_down < 0:
        raise ValueError(f"事件计数为负：n_up={n_up} n_down={n_down}（数据越界即停，禁纠正后继续）")
    total = n_up + n_down
    if total < _MIN_CELL_EVENTS_FOR_STATE:
        return "chart_none"
    ratio = (n_up - n_down) / total
    if not -1.0 <= ratio <= 1.0:  # pragma: no cover - 数学上不可达，护栏
        raise ValueError(f"广度比越界: {ratio!r}")
    lo, hi = _CHART_RATIO_EDGES
    if ratio <= lo:
        return "chart_bear"
    if ratio >= hi:
        return "chart_bull"
    return "chart_mixed"


def build_chart_daily_state(events: pd.DataFrame) -> pd.DataFrame:
    """事件明细 → [date, family, chart_state, n_up, n_down, n_events] 长表。

    方向口径与 market_pattern_win_rate 一致：向上/向下 为引擎封闭集原文，
    中性不入广度分子（既不算多也不算空）。
    """
    missing = [c for c in _REQUIRED_EVENT_COLUMNS if c not in events.columns]
    if missing:
        raise KeyError(f"事件框缺列 {missing}（期望 {list(_REQUIRED_EVENT_COLUMNS)}）")
    if events.empty:
        raise RuntimeError("事件框为空——禁从空读数下'无数据'结论（读数通道失败≠无数据）")
    ev = events.copy()
    ev["family"] = [
        classify_chart_family(str(pid), str(nm), str(pc))
        for pid, nm, pc in zip(
            ev["pattern_id"], ev.get("name", pd.Series([""] * len(ev))), ev["pattern_class"], strict=False
        )
    ]
    ev["date"] = pd.to_datetime(ev["anchor_trade_date"])
    up = ev[ev["direction"] == "向上"].groupby(["date", "family"])["symbol"].nunique()
    down = ev[ev["direction"] == "向下"].groupby(["date", "family"])["symbol"].nunique()
    total = ev.groupby(["date", "family"])["symbol"].nunique()
    idx = total.index
    n_up = up.reindex(idx).fillna(0).astype(int)
    n_down = down.reindex(idx).fillna(0).astype(int)
    frame = pd.DataFrame(
        {
            "date": [k[0] for k in idx],
            "family": [k[1] for k in idx],
            "n_up": n_up.to_numpy(),
            "n_down": n_down.to_numpy(),
            "n_symbols": total.to_numpy().astype(int),
        }
    )
    frame["chart_state"] = [
        chart_state_from_breadth(int(u), int(d)) for u, d in zip(frame["n_up"], frame["n_down"], strict=True)
    ]
    return frame.sort_values(["family", "date"]).reset_index(drop=True)


# ── 条件包组装 ────────────────────────────────────────────────
@dataclass(frozen=True)
class ChartConditionPack:
    """三轴条件包：逐日 (family, grey_band, state, chart_state, cell_id, eligible) + 胞台账。"""

    frame: pd.DataFrame
    cells: pd.DataFrame
    closed_book_window: tuple[str, str]
    families: tuple[str, ...]
    chart_states: tuple[str, ...]
    provenance: dict = field(default_factory=dict)

    def eligible_cells(self) -> list[str]:
        return self.cells.loc[self.cells["eligible"], "cell_id"].tolist()

    def to_frame(self) -> pd.DataFrame:
        return self.frame.copy()


def _validate_band_state(band: str, state: str, chart_state: str) -> None:
    """喂错状态标签必红（G-A.2 出口判据的红证面）。"""
    if band not in _BAND_LABELS:
        raise ValueError(f"未知灰度档 {band!r}（合法={_BAND_LABELS}，真源 condition_package._BAND_LABELS）")
    if chart_state not in _CHART_STATE_LABELS:
        raise ValueError(f"未知图形档 {chart_state!r}（合法={_CHART_STATE_LABELS}）")
    if not state or state == "nan":
        raise ValueError(f"状态轴空字面量 {state!r}——禁静默补值")


def build_chart_condition_pack(
    chart_daily: pd.DataFrame,
    base_pack: ConditionPack,
    *,
    floor_days: int = _CELL_FLOOR_DAYS,
    keep_families: Iterable[str] | None = None,
) -> ChartConditionPack:
    """图形逐日状态 × condition_package 两轴 → 三轴条件胞（同 30 日地板）。

    keep_families=None=全族；指定族时只保留该族行（一胞一族的论域，禁跨族混算）。
    chart_none 不入胞（当日该族无事件=无信息，不是信息；下沉 conditional-free）。
    """
    need = {"date", "family", "chart_state"}
    miss = need - set(chart_daily.columns)
    if miss:
        raise KeyError(f"图形日框缺列 {sorted(miss)}")
    base = base_pack.frame[["date", "grey_band", "state"]].copy()
    if base.empty:
        raise RuntimeError("基准条件包日框为空——三轴不可组装")
    kept = chart_daily if keep_families is None else chart_daily[chart_daily["family"].isin(set(keep_families))]
    if kept.empty:
        raise RuntimeError("keep_families 过滤后无图形事件日——三轴不可组装（禁降级为两轴出绿）")
    merged = kept.merge(base, on="date", how="inner")
    if merged.empty:
        raise RuntimeError("图形日与两轴包零重叠日——窗口口径不一致，禁组装")
    merged = merged[merged["chart_state"] != "chart_none"]
    if merged.empty:
        raise RuntimeError("重叠窗内全为 chart_none——无有效图形档，禁组装")

    rows = []
    for r in merged.itertuples(index=False):
        _validate_band_state(str(r.grey_band), str(r.state), str(r.chart_state))
        rows.append(
            {
                "date": r.date,
                "family": str(r.family),
                "grey_band": str(r.grey_band),
                "state": str(r.state),
                "chart_state": str(r.chart_state),
            }
        )
    frame = pd.DataFrame(rows).sort_values(["family", "date"]).reset_index(drop=True)
    counts = frame.groupby(["family", "chart_state", "grey_band", "state"], sort=True).size()
    cell_of = {k: f"c{k[1]}|g{k[2]}|s{k[3]}|f{k[0]}" for k in counts.index}
    eligible_of = {k: int(v) >= floor_days for k, v in counts.items()}
    key = list(zip(frame["family"], frame["chart_state"], frame["grey_band"], frame["state"], strict=True))
    frame["cell_id"] = [cell_of[k] if eligible_of[k] else None for k in key]
    frame["cell_eligible"] = [eligible_of[k] for k in key]
    # 兼容既有判读端列名（condition_attribution 读 cell_id/cell_eligible）
    cells = (
        pd.DataFrame(
            [
                {
                    "cell_id": cell_of[k],
                    "family": k[0],
                    "chart_state": k[1],
                    "grey_band": k[2],
                    "state": k[3],
                    "days": int(n),
                    "eligible": eligible_of[k],
                }
                for k, n in counts.items()
            ]
        )
        .sort_values("cell_id")
        .reset_index(drop=True)
    )
    start = str(frame["date"].min().date())
    end = str(frame["date"].max().date())
    provenance = {
        "axis_families": sorted(set(frame["family"])),
        "axis_family_labels_zh": {_FAMILY_ZH[f]: f for f in sorted(set(frame["family"]))},
        "chart_ratio_edges": list(_CHART_RATIO_EDGES),
        "cell_floor_days": int(floor_days),
        "cells_total": int(len(cells)),
        "cells_eligible": int(cells["eligible"].sum()),
        "days": int(len(frame)),
        "closed_book_window": [start, end],  # 键名与基准包同构（cp.load_pack 契约）
        "event_table": _EVENT_CATEGORY,  # 记品类名（表全名经 TableRegistry 解析，同源纪律）
        "role_note": "图形信号=条件轴非独立信号（波 10 硬约束）；状态轴=F4 三态，"
        "事件表 regime_tag=regime_detector 七态，两口径无在册映射故不混用",
    }
    return ChartConditionPack(
        frame=frame,
        cells=cells,
        closed_book_window=(start, end),
        families=tuple(sorted(set(frame["family"]))),
        chart_states=tuple(s for s in _CHART_STATE_LABELS if s in set(frame["chart_state"])),
        provenance=provenance,
    )


# ── CH 读数（会抛错的通道）────────────────────────────────────
# 纯 format 模板（禁 f-string 混用：段间 f 前缀只作用于首段，
# {{end}} 在非 f 段里会退化成字面 {end} —— 本道实弹冒烟实测炸出 Code 38）
_SQL_EVENTS = (
    "SELECT anchor_trade_date, direction, pattern_id, pattern_class, symbol, name, timeframe "
    "FROM {table} FINAL WHERE anchor_trade_date >= toDate('{start}') "
    "AND anchor_trade_date <= toDate('{end}') "
    "AND direction IN ('向上','向下') {sample} "
    "ORDER BY anchor_trade_date LIMIT {limit}"
)


def _default_reader():
    from zephyr.infrastructure.database_service import DatabaseService

    return DatabaseService().get_clickhouse_conn(role="reader")


def load_market_pattern_events(
    start: str,
    end: str,
    *,
    limit: int = 2_000_000,
    symbol_prefix: str | None = None,
    conn: Any | None = None,  # noqa: any-abuse -- DI 读通道缝位（DatabaseService reader，测试注入替身；具体类型耦合服务内部句柄）
) -> pd.DataFrame:
    """有界读 market_pattern_event（唯一合法读通道=DatabaseService reader，失败即抛）。

    禁 ch_reader.query() 下标直取（TSV 字符串首位数字陷阱，W-180 定性）。
    """
    c = conn if conn is not None else _default_reader()
    sample = f"AND symbol LIKE '{symbol_prefix}%'" if symbol_prefix else ""
    sql = _SQL_EVENTS.format(table=event_table(), start=start, end=end, limit=int(limit), sample=sample)
    rows = c.execute(sql)  # 连接/SQL 失败向上抛，不吞
    cols = ["anchor_trade_date", "direction", "pattern_id", "pattern_class", "symbol", "name", "timeframe"]
    if not rows:
        raise RuntimeError(f"事件查询空结果 [{start},{end}]——查询失败与无数据不可混判，先复核通道")
    return pd.DataFrame(list(rows), columns=cols)


@dataclass(frozen=True)
class ChartPackRequest:
    """端到端装配入参对象（NO-LONG-PARAM-LIST：8 元参数列表收敫成一个显式请求）。

    默认值与本件既有口径同源：地板天数=condition_package._CELL_FLOOR_DAYS，
    事件读数上界=2_000_000（有界读数纪律），keep_families=None=全族论域。
    """

    start: str
    end: str
    floor_days: int = _CELL_FLOOR_DAYS
    keep_families: Iterable[str] | None = None
    event_limit: int = 2_000_000
    symbol_prefix: str | None = None
    base_pack: ConditionPack | None = None


def load_chart_condition_pack(req: ChartPackRequest, *, conn: Any | None = None) -> ChartConditionPack:  # noqa: any-abuse -- DI 读通道缝位（同 load_market_pattern_events）
    """端到端：事件读数 + 基准两轴包 → 三轴图形条件包。"""
    events = load_market_pattern_events(
        req.start, req.end, limit=req.event_limit, symbol_prefix=req.symbol_prefix, conn=conn
    )
    base_pack = req.base_pack
    if base_pack is None:
        from zephyr.backtest.regime_validation.condition_package import load_condition_pack

        base_pack = load_condition_pack(req.start, req.end, floor_days=req.floor_days)
    chart_daily = build_chart_daily_state(events)
    pack = build_chart_condition_pack(
        chart_daily, base_pack, floor_days=req.floor_days, keep_families=req.keep_families
    )
    prov = dict(pack.provenance)
    prov["event_sample_prefix"] = req.symbol_prefix or "FULL_UNIVERSE"
    prov["event_rows_read"] = int(len(events))
    return ChartConditionPack(
        frame=pack.frame,
        cells=pack.cells,
        closed_book_window=pack.closed_book_window,
        families=pack.families,
        chart_states=pack.chart_states,
        provenance=prov,
    )


# ── G-C.1 多周期 PIT 对齐（唯一合法姿势）─────────────────────────
def align_backward(
    low: pd.DataFrame,
    high: pd.DataFrame,
    *,
    low_ts: str = "bar_close_ts",
    high_ts: str = "bar_close_ts",
    columns: Iterable[str] | None = None,
) -> pd.DataFrame:
    """高周期信号列贴低周期行：merge_asof backward + allow_exact_matches=False。

    语义：低周期行只看得见**已收盘**的高周期 bar——高周期 bar 的收盘时刻严格晚于
    低周期行时刻才可见（等号=同刻，禁：那根高周期 bar 尚未定盘）。
    这是前视安全的判据件，红证在 tests/backtest/test_chart_condition_package.py。
    """
    for df, col, who in ((low, low_ts, "low"), (high, high_ts, "high")):
        if col not in df.columns:
            raise KeyError(f"{who} 框缺时间列 {col!r}")
    hi = high.sort_values(high_ts)
    cols = list(columns) if columns else [c for c in hi.columns if c != high_ts]
    right = hi[[high_ts, *cols]].sort_values(high_ts).rename(columns={high_ts: low_ts})
    left = low.sort_values(low_ts).reset_index(drop=False).rename(columns={"index": "_row_key"})
    out = pd.merge_asof(
        left,
        right[[low_ts, *cols]],
        on=low_ts,
        direction="backward",
        allow_exact_matches=False,
    )
    return out.sort_values(low_ts).reset_index(drop=True)


# ── G-A.3 胜率接线桥（胞级命中率，无统计=None）────────────────────
def _hit_of(fwd_ret: float, direction: str) -> float:
    """单次事件命中判定：向上赌正收益、向下赌负收益（其余一律 0，不给部分分）。

    这是接线桥唯一的判据谓词——红证=tests/backtest/test_chart_condition_package.py
    ::TestCellWinRateBridge.test_downward_direction_hit_definition_is_mirror。
    """
    if direction == "向上":
        return 1.0 if fwd_ret > 0 else 0.0
    return 1.0 if fwd_ret < 0 else 0.0


def _fwd_series_map(fwd_returns: dict[int, pd.Series] | pd.Series) -> dict[int, pd.Series]:
    """入参归一：单 Series 视作窗口 5；空读数必抛（读数失败≠无数据）。"""
    if isinstance(fwd_returns, pd.Series):
        series_map: dict[int, pd.Series] = {5: fwd_returns}
    else:
        series_map = dict(fwd_returns or {})
    if not series_map:
        raise RuntimeError("前视收益序列为空——读数失败与无数据不可混判")
    return series_map


def _join_window_returns(ev: pd.DataFrame, ret: pd.Series, fwd: int) -> pd.DataFrame:
    """单窗口：事件 × 前视收益 → 成熟行 + hit 列；未成熟自然丢弃（不补 0、不外推）。"""
    if fwd not in _FWD_WINDOWS:
        raise ValueError(f"前视窗 {fwd} 不在册 {list(_FWD_WINDOWS)}（禁自造窗口）")
    joined = ev.copy()
    joined["fwd_ret"] = joined["fwd_ret_key"].map(ret)
    joined = joined.dropna(subset=["fwd_ret"])
    if joined.empty:
        return joined
    joined["hit"] = [_hit_of(r, d) for r, d in zip(joined["fwd_ret"], joined["direction"], strict=True)]
    return joined


def _cell_rows(joined: pd.DataFrame, fwd: int, min_sample: int) -> list[dict[str, Any]]:
    """(family, cell_id, direction) 分组行：样本 < min_sample ⇒ hit_rate=None。

    样本不足=无统计（None），不给数值：与 30 日地板同源纪律（禁凑 n），
    亦与 PatternWinRateProvider 契约一致（low_sample 消费方按无统计处理）。
    """
    rows: list[dict[str, Any]] = []
    for (fam, cell, direction), sub in joined.groupby(["family", "cell_id", "direction"], dropna=False):
        n = int(len(sub))
        enough = n >= min_sample
        rows.append(
            {
                "family": fam,
                "cell_id": cell,
                "direction": direction,
                "fwd_window": fwd,
                "n_events": n,
                "hit_rate": float(sub["hit"].mean()) if enough else None,
                "avg_fwd_ret": float(sub["fwd_ret"].mean()) if enough else None,
                "low_sample": not enough,
            }
        )
    return rows


def _baseline_row(joined: pd.DataFrame, fwd: int, min_sample: int) -> dict[str, Any]:
    """`__baseline__` 池化对照行（与 provider/物化表同键名）。"""
    pooled = joined.groupby("fwd_ret_key", as_index=False).agg(
        hit=("hit", "mean"), n=("hit", "size"), r=("fwd_ret", "mean")
    )
    pooled_n = int(pooled["n"].sum())
    enough = pooled_n >= min_sample
    return {
        "family": _BASELINE_ID,
        "cell_id": _BASELINE_ID,
        "direction": "池化",
        "fwd_window": fwd,
        "n_events": pooled_n,
        "hit_rate": float((pooled["hit"] * pooled["n"]).sum() / pooled_n) if enough else None,
        "avg_fwd_ret": float((pooled["r"] * pooled["n"]).sum() / pooled_n) if pooled_n else None,
        "low_sample": not enough,
    }


def cell_win_rate(
    events: pd.DataFrame,
    fwd_returns: dict[int, pd.Series] | pd.Series,
    *,
    min_sample: int = _MIN_SAMPLE,
) -> pd.DataFrame:
    """事件 × 前视收益 → (family, cell_id, direction, fwd_window) 命中率 + baseline 行。

    fwd_returns：
      - dict{fwd_window: Series(index=symbol|date 键, value=前视收益)}，或
      - Series（单窗口，视作 fwd_window=5）。
    未成熟事件（键查不到）自然不参与，不补 0、不外推。
    样本 < min_sample ⇒ hit_rate=None + low_sample=True（消费方按无统计处理）。
    纯函数：不写库、不点火（波 12 统一窗口才跑），READY_NOT_FIRED。
    """
    miss = {"fwd_ret_key"} - set(events.columns)
    if miss:
        raise KeyError(f"事件框缺列 {sorted(miss)}（需 fwd_ret_key=前视收益查表键）")
    series_map = _fwd_series_map(fwd_returns)

    rows: list[dict[str, Any]] = []
    ev = events.dropna(subset=["cell_id"]).copy()
    for fwd, ret in sorted(series_map.items()):
        joined = _join_window_returns(ev, ret, fwd)
        if joined.empty:
            continue
        rows.extend(_cell_rows(joined, fwd, min_sample))
        rows.append(_baseline_row(joined, fwd, min_sample))
    if not rows:
        raise RuntimeError("零达标事件参与统计——返回空表而非 0（禁把无统计读成 0 胜率）")
    return pd.DataFrame(rows).sort_values(["fwd_window", "family", "cell_id", "direction"]).reset_index(drop=True)


def make_fwd_key(symbol: str, trade_date: Any) -> str:  # noqa: any-abuse -- 入参容忍 str/datetime/Timestamp 三态，函数内 pd.Timestamp 统一归一
    """前视收益查表键（与 kline_daily 同口径的 symbol+日）。"""
    return f"{symbol}|{pd.Timestamp(trade_date).date().isoformat()}"


# ── 落盘/回读（与 condition_package 文件名同构 ⇒ 判读端零改动）────────
# 落盘不另起实现：`save_pack` 自 condition_package 直接 import 复用（见文件头 import 段），
# 本包 frame/cells/provenance 三件套与基准包同构，故同一函数体对两类 pack 均成立。


def load_pack(out_dir: str | Path) -> ChartConditionPack:
    """离线回读（判读端消费面）。"""
    import json

    out = Path(out_dir)
    frame = pd.read_csv(out / "condition_pack_daily.csv.gz", parse_dates=["date"])
    cells = pd.read_csv(out / "condition_pack_cells.csv")
    prov = json.loads((out / "condition_pack_provenance.json").read_text(encoding="utf-8"))
    return ChartConditionPack(
        frame=frame,
        cells=cells,
        closed_book_window=tuple(prov["closed_book_window"]),
        families=tuple(prov["axis_families"]),
        chart_states=tuple(s for s in _CHART_STATE_LABELS if s in set(frame["chart_state"])),
        provenance=prov,
    )


def today_safe() -> _date:  # pragma: no cover - 供盘点器显式取日，禁在本件跑批内用
    """显式隔离：本包不自行取当前日期（生成器禁 datetime.now 口径）。"""
    raise NotImplementedError("波 10 接线件禁内建时钟——调用方显式传窗")
