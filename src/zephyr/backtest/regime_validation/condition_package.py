# [BLUEPRINT] MOD-BT-COND-PACKAGE | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] zephyr.backtest.regime_validation.condition_package
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] numpy; pandas; zephyr.data.ch_reader; zephyr.data.table_registry
# [CONSUMERS] scripts/backtest/factory_grid_executor.py（T1 条件维分层键/E0 输入包闭卷验收）；scripts/backtest/f06_e4_wfa_exam.py（条件胞分段判读预留）；GPU 点火前输入包验收（w3_w5_precheck §2.4·甲/§二·五）
# [STARTUP] imported
# [MATURITY] experimental
# [INVARIANTS] 公式冻结禁回改：情绪值消费 c1_market.emotion_index v0.1.0 冻结公式产出（本件只分档不改值，改公式=作废重开卡，st-emoreplay 纪律）；灰度五档边界冻结 (0.2,0.4,0.6,0.8]=冰点/降温/温和/升温/沸点，闭卷窗内空档如实剔除（实测冰点 0 日→四档）；状态轴真源=c1_market.alt_regime_signal 键列 signal_date（与情绪轴 trade_date 不同名，实测 Code 47 坑），选族铁规=signal_id='F4_BDI_MOMENTUM_Z20'（本班自纠：uniqExact=5 系三族混合，F11 猪周期/F14 BTC 非市场状态）；闭卷窗内 state 去重>5 即 fail-closed（选族失败或映射册前置件缺失）；条件胞=灰度档×状态档，30 交易日地板，不达地板日期一律下沉 conditional-free（禁凑 n，禁当独立样本）；搜索窗=闭卷窗 [2019-01-04, 2025-09-09]，窗外数据禁入（closed_book 纪律：禁校正/调参/定档）；板块轴 observational-only 禁入统计判据（实测仅 17 交易日），columns_forbidden=[capital_score, net_inflow_pct] 以"不加载"执行；fail-closed：任一轴数据缺失/行数异常即抛异常，禁静默降级
# [MODIFY-GUARD] tests/backtest/test_condition_package.py
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ValueError(闭卷窗内 state 字面量>5 / 情绪值越界 [0,1] / 闭卷窗行数<地板总数)；IO 失败向上抛（ch_reader 失败禁吞）
# [TESTS] tests/backtest/test_condition_package.py
# [TTL] permanent
# [A_module] module_id=MOD-BT-COND-PACKAGE | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
"""GPU 网格条件轴输入包（情绪灰度 × 大盘状态，Owner 2026-09-23 夜裁决①分层口径）。

统计可用层 = 情绪档 × 大盘状态（两轴全史），30 日地板达标胞才可作 IS/OOS 条件轴、
可计 n、可进判据；观察标注层 = 板块腿（sector_state 仅 17 交易日）只做行级标注，
禁入统计判据、禁当独立样本计 n（precheck §2.4·甲）。

数字真源 = docs/_working/e2e_integration/w3_w5_precheck_20260923.md（实测，勿重测）：
闭卷窗 1,622 交易日；band5 窗内分布 cooling 120 / mild 594 / warming 655 / boiling 253
（冰点 0 日空层）。

状态轴选族自纠（本班实测，修正 precheck "uniqExact(state)=5" 口径）：窗内 5 种字面量实为
三族信号混合——市场状态真身=F4_BDI_MOMENTUM_Z20（neutral/risk_on/risk_off 三态，
1,676 行=1,676 日零重复全覆盖）；F11_HOG_CYCLE_PHASE（扩张/收缩，猪周期稀疏 327 行）与
F14_BTC_MOMENTUM_30D（尾部 3 行）非市场状态轴，本件按 signal_id=F4 定族过滤。
# [ALGO_FLOW] external: docs/03_modules/_domain_backtest/algo_flow/condition_package.yaml
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Final

import pandas as pd

from zephyr.data import ch_reader
from zephyr.data.table_registry import get_registry

_BAND_EDGES: Final = (0.2, 0.4, 0.6, 0.8)
_BAND_LABELS: Final = ("ice", "cooling", "mild", "warming", "boiling")
_CLOSED_BOOK_START: Final = "2019-01-04"
_CLOSED_BOOK_END: Final = "2025-09-09"  # cutoff：闭卷纪律（窗外禁校正/调参/定档）
_CELL_FLOOR_DAYS: Final = 30
_MAX_STATES_IN_WINDOW: Final = 5  # F4 族实测 3 态；>5 = 混入他族信号或窗口越界，映射册/选族规则未建
_STATE_FAMILY: Final = "F4_BDI_MOMENTUM_Z20"  # 市场状态轴唯一真身族（本班选族自纠，见模块 docstring）
_EMOTION_TABLE: Final = "market_emotion_index"  # 逻辑品类名 → c1_market.emotion_index
_STATE_TABLE: Final = "market_alt_regime_signal"  # 逻辑品类名 → c1_market.alt_regime_signal


def grey_band(value: float) -> str:
    """情绪值 → 五档灰度标签（边界冻结 band5：≤0.2/≤0.4/≤0.6/≤0.8/>0.8）。"""
    if not 0.0 <= value <= 1.0:
        raise ValueError(f"emotion_index 越界 [0,1]: {value!r}")
    for edge, label in zip(_BAND_EDGES, _BAND_LABELS, strict=False):  # 4 edges × 5 labels：末档沸点走 fallback
        if value <= edge:
            return label
    return _BAND_LABELS[-1]


@dataclass(frozen=True)
class ConditionPack:
    """条件轴输入包：逐日 (灰度档, 状态档, 条件胞, 达地板) + 胞级台账。

    cell_eligible=False 的日期 = 所在胞未达 30 日地板，下沉 conditional-free
    （禁入统计判据、禁当独立样本计 n）。
    """

    frame: pd.DataFrame  # columns=[date, grey_band, state, cell_id, cell_eligible]
    cells: pd.DataFrame  # columns=[cell_id, grey_band, state, days, eligible]
    closed_book_window: tuple[str, str]
    dropped_bands: tuple[str, ...]  # 窗内 0 日的灰度档（实测应=('ice',)）
    states: tuple[str, ...]  # 窗内实际状态字面量（实测 5 个）
    provenance: dict = field(default_factory=dict)

    def lookup(self, date: str) -> tuple[str, str, str | None]:
        """O(1) 逐日查表：返回 (灰度档, 状态档, cell_id)。未达标胞 cell_id=None。"""
        row = self.frame.loc[self.frame["date"] == pd.Timestamp(date)]
        if row.empty:
            raise KeyError(f"日期 {date} 不在条件包搜索窗内（闭卷窗 {_CLOSED_BOOK_START}..{_CLOSED_BOOK_END}）")
        r = row.iloc[0]
        return str(r["grey_band"]), str(r["state"]), (None if pd.isna(r["cell_id"]) else str(r["cell_id"]))

    def eligible_cells(self) -> list[str]:
        """达 30 日地板的条件胞清单（=T1 分层键论域，Owner 上限 18 格）。"""
        return self.cells.loc[self.cells["eligible"], "cell_id"].tolist()

    def to_frame(self) -> pd.DataFrame:
        return self.frame.copy()


def _tsv_to_frame(tsv: str, columns: list[str]) -> pd.DataFrame:
    if not tsv.strip():
        raise RuntimeError(f"条件轴查询空结果（列期望 {columns}）——数据缺失 fail-closed")
    df = pd.read_csv(pd.io.common.StringIO(tsv), sep="\t", names=columns, dtype=str)
    return df


_SQL_EMOTION = (
    "SELECT toString(trade_date) AS d, toFloat64(emotion_index) AS v "
    "FROM {table} FINAL WHERE trade_date >= toDate('{start}') AND trade_date <= toDate('{end}') "
    "ORDER BY d"
)
_SQL_STATE = (
    "SELECT toString(signal_date) AS d, state FROM {table} FINAL "
    "WHERE signal_id = '{family}' AND signal_date >= toDate('{start}') AND signal_date <= toDate('{end}') "
    "ORDER BY d"
)


def load_condition_pack(
    start: str = _CLOSED_BOOK_START,
    end: str = _CLOSED_BOOK_END,
    floor_days: int = _CELL_FLOOR_DAYS,
) -> ConditionPack:
    """从 CH 加载两轴、闭卷窗内组装条件包。任一轴缺失即抛（fail-closed）。"""
    reg = get_registry()
    emo_t, st_t = reg.table(_EMOTION_TABLE), reg.table(_STATE_TABLE)
    emo = _tsv_to_frame(
        ch_reader.query(_SQL_EMOTION.format(table=emo_t, start=start, end=end)),
        ["date", "value"],
    )
    st = _tsv_to_frame(
        ch_reader.query(_SQL_STATE.format(table=st_t, family=_STATE_FAMILY, start=start, end=end)),
        ["date", "state"],
    )
    emo["date"] = pd.to_datetime(emo["date"])
    st["date"] = pd.to_datetime(st["date"])
    merged = emo.merge(st, on="date", how="inner", validate="one_to_one")
    if merged.empty:
        raise RuntimeError("情绪轴与状态轴在闭卷窗内零重叠日——输入包不可用")
    return build_condition_pack(merged, start=start, end=end, floor_days=floor_days)


def build_condition_pack(
    daily: pd.DataFrame,
    start: str = _CLOSED_BOOK_START,
    end: str = _CLOSED_BOOK_END,
    floor_days: int = _CELL_FLOOR_DAYS,
) -> ConditionPack:
    """纯函数：逐日 [date, value, state] → ConditionPack（测试直供面板）。

    状态字面量守卫：窗内去重 >5 抛 ValueError（precheck §2.4——全史 17 种中英混排，
    映射册只在把窗拉到窗外时才建，此处 fail-closed 防静默扩窗）。
    """
    states = tuple(sorted(daily["state"].astype(str).unique()))
    if len(states) > _MAX_STATES_IN_WINDOW:
        raise ValueError(
            f"闭卷窗内 state 去重={len(states)} >{_MAX_STATES_IN_WINDOW}：窗口越界或映射册缺失，"
            f"禁组装（字面量={states}）"
        )
    bands = daily["value"].map(lambda v: grey_band(float(v)))
    frame = pd.DataFrame(
        {
            "date": daily["date"].reset_index(drop=True),
            "grey_band": bands.reset_index(drop=True),
            "state": daily["state"].astype(str).reset_index(drop=True),
        }
    )
    counts = frame.groupby(["grey_band", "state"], sort=True).size()
    dropped = tuple(b for b in _BAND_LABELS if b not in set(frame["grey_band"]))
    cell_of = {k: f"g{k[0]}|s{k[1]}" for k in counts.index}
    eligible_of = {k: int(v) >= floor_days for k, v in counts.items()}
    frame["cell_id"] = [
        cell_of[(g, s)] if eligible_of[(g, s)] else None
        for g, s in zip(frame["grey_band"], frame["state"], strict=True)
    ]
    frame["cell_eligible"] = [eligible_of[(g, s)] for g, s in zip(frame["grey_band"], frame["state"], strict=True)]
    cells = pd.DataFrame(
        [
            {"cell_id": cell_of[k], "grey_band": k[0], "state": k[1], "days": int(n), "eligible": eligible_of[k]}
            for k, n in counts.items()
        ]
    )
    provenance = {
        "emotion_table": _EMOTION_TABLE,
        "state_table": _STATE_TABLE,
        "formula_version": "emotion_index v0.1.0 冻结（禁回改）",
        "closed_book_window": [start, end],
        "days": int(len(frame)),
        "cell_floor_days": floor_days,
        "cells_total": int(len(cells)),
        "cells_eligible": int(cells["eligible"].sum()),
        "band_distribution": {k: int(v) for k, v in frame["grey_band"].value_counts().items()},
        "observational_layer_note": "sector_state 仅 17 交易日=观察层禁入统计（ Owner 裁决①）；"
        "columns_forbidden=[capital_score, net_inflow_pct] 以不加载执行",
    }
    return ConditionPack(
        frame=frame,
        cells=cells,
        closed_book_window=(start, end),
        dropped_bands=dropped,
        states=states,
        provenance=provenance,
    )


def save_pack(pack: ConditionPack, out_dir: str | Path) -> Path:
    """落档（csv.gz 双表 + provenance json），供执行器离线消费（GPU 路零 CH 依赖）。"""
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    fp = out / "condition_pack_daily.csv.gz"
    pack.frame.to_csv(fp, index=False, compression="gzip")
    pack.cells.to_csv(out / "condition_pack_cells.csv", index=False)
    import json

    (out / "condition_pack_provenance.json").write_text(
        json.dumps(pack.provenance, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return fp


def load_pack(out_dir: str | Path) -> ConditionPack:
    """离线回读（GPU 跑批前验收用：结构 + provenance 双核对）。"""
    import json

    out = Path(out_dir)
    frame = pd.read_csv(out / "condition_pack_daily.csv.gz", parse_dates=["date"])
    cells = pd.read_csv(out / "condition_pack_cells.csv")
    prov = json.loads((out / "condition_pack_provenance.json").read_text(encoding="utf-8"))
    dropped = tuple(b for b in _BAND_LABELS if b not in set(frame["grey_band"]))
    return ConditionPack(
        frame=frame,
        cells=cells,
        closed_book_window=tuple(prov["closed_book_window"]),
        dropped_bands=dropped,
        states=tuple(sorted(frame["state"].astype(str).unique())),
        provenance=prov,
    )
