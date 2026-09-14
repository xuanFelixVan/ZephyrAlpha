# [BLUEPRINT] MOD-REGIME-001 | docs/03_modules/_domain_regime/regime_detector/blueprint.md
# [MODULE] zephyr.regime.core.anchored_state_machine
# [DOMAIN] D_REGIME
# [DEPENDENCIES] pandas; numpy; zephyr.data.ch_reader; zephyr.data.provider_base
# [CONSUMERS] scripts/ch/build_anchored_state_history.py（历史构建 CLI）;
#             scripts/backtest/validate_p0_discrimination.py --prob-table（冻结验收输入源）
# [STARTUP] imported
# [MATURITY] design
# [INVARIANTS] 态身份锚定（裁定#229 约束①）：四态由固定 vol_pct 结构阈值（0.30/0.60/0.80）定义，
#              零拟合零重估——同一特征输入永远同一态，HMM label switching 结构性不可能；
#              风险分档语义（约束③定稿）：态层只承担风险判别（探针实证 vol→fwd20 回撤关系
#              IS/OOS 双段同向 -2.06/-2.93，而趋势→收益方向两段相反——方向判别无稳定解）；
#              链假设低风险→高风险（r3>r2>r1>r4），冻结链字母序原样适配；
#              死态清理（约束②）：四态按构造可达（阈值全覆盖 [0,1]）；
#              PIT 严格：vol_pct 为 rolling 分位（t 及以前），判定 t 日态不用 t 之后任何数据
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 行情不可达->RuntimeError；阈值/窗口=结构常数（本文件常量区），调整须语义复核留痕
# [TESTS] tests/zephyr/regime/test_anchored_state_machine.py
# [TTL] permanent
"""anchored_state_machine — 特征锚定风险四档状态机（P0-002 重印批，裁定#229）。

语义复核（docs/_working/2026-09-13-p002-semantic-review.md）实锤：现行 HMM 4 态
walk-forward 季度重拟合——态编号跨期无锚（label switching），"牛市"态 OOS 反转最亏。
本模块是重印批第②步产出。**设计迭代史（有界三版，全部留痕）**：

    v1 趋势双确认版（MA120×MA20/60）：全样本 spread=-0.82——"牛市态"968 日 fwd20
       仅 +0.06%（追确认=追晚），趋势→收益方向两段相反，否决；
    探针（四特征×双段）：唯一双段稳定轴=波动率风险轴（vol_pct 高→fwd20 收益更差+
       回撤更深，IS/OOS 同向），趋势/动量→收益方向不稳定，dd250 翻转；
    v2（定稿）=波动率风险四档，纯锚定阈值，无趋势项。

四态（风险分档语义，约束③）：
    r3 低风险：vol_pct <= 0.30（波动后 30% 分位）
    r2 中风险：0.30 < vol_pct <= 0.60
    r1 中高风险：0.60 < vol_pct <= 0.80
    r4 高风险：vol_pct > 0.80

验收实况（2026-09-14 冻结判据如实记录）：
    方向稳定达成——spread(r3−r4) IS +0.26 / OOS +1.73 双段同正（HMM 版 OOS -2.37 反转）；
    全样本 spread +0.49 未达冻结线 1.0，相邻链显著性不足（诚实 pending）。
    与 L1 谨慎度轴同源（vol→RiskSignal），合流即约束③本意；判据契约变更
    （收益判别→风险判别，数值阈值同样冻结）留 Owner 门位裁定。

特征（全 rolling，PIT 严格，与 market_features.py F1 同口径）：
    hv20    = log 收益 20 日标准差 × √252
    vol_pct = hv20 在滚动 250 日内的分位 ∈ [0,1]
    ma20/ma60/ma120 = 收盘价均线（仅作表内审计列，不入判定）

用法：
    build_states(close_series) -> DataFrame[trade_date, dominant, ...]（纯函数核）
    run_compute() -> Iterator[FetchResult]（行情加载+全量重算，BufferedWriter 消费）
"""

from __future__ import annotations

import logging
from collections.abc import Iterator

import numpy as np
import pandas as pd

from zephyr.data.provider_base import FetchResult

log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# 结构常数区（裁定#229 约束①：锚定阈值，禁静默调整；调整须语义复核留痕）
# ---------------------------------------------------------------------------
_MA_SHORT = 20
_MA_MID = 60
_MA_LONG = 120
_HV_WINDOW = 20
_VOL_PCT_WINDOW = 250
# 风险四档锚定阈值（v2 定稿）：低→高风险 = r3→r2→r1→r4
_VOL_PCT_T_LOW = 0.30      # r3 上界（低风险）
_VOL_PCT_T_MID = 0.60      # r2 上界（中风险）
_VOL_PCT_T_HIGH = 0.80     # r1 上界（中高风险）；>0.80 = r4 高风险
_WARMUP = max(_MA_LONG, _VOL_PCT_WINDOW + _HV_WINDOW)  # 首个有效态所需最短历史

DATA_SOURCE = "anchored_state_machine"
_TABLE = "c1_backtest.regime_state_anchored"

STATE_NAMES = {
    "r3": "低风险",
    "r2": "中风险",
    "r1": "中高风险",
    "r4": "高风险",
}


# ---------------------------------------------------------------------------
# 纯函数核（无 IO；tests/zephyr/regime/test_anchored_state_machine.py 直测）
# ---------------------------------------------------------------------------

def classify_state(vol_pct: float) -> str:
    """单日锚定态判定（纯函数；同输入永远同输出——锚定性质本身）。

    风险四档：低(r3) / 中(r2) / 中高(r1) / 高(r4)，阈值 0.30/0.60/0.80。
    """
    if vol_pct <= _VOL_PCT_T_LOW:
        return "r3"
    if vol_pct <= _VOL_PCT_T_MID:
        return "r2"
    if vol_pct <= _VOL_PCT_T_HIGH:
        return "r1"
    return "r4"


def compute_features(close: pd.Series) -> pd.DataFrame:
    """收盘价序列 → 特征帧（全 rolling，PIT 严格：t 行只含 ≤t 信息）。

    Args:
        close: 按 trade_date 升序的收盘价序列（index=DatetimeIndex）。

    Returns:
        DataFrame[close, ma20, ma60, ma120, hv20, vol_pct]；热身期（前 _WARMUP 行）
        vol_pct 为 NaN。
    """
    close = close.astype(float)
    ret = np.log(close).diff()
    hv20 = ret.rolling(_HV_WINDOW).std() * np.sqrt(252.0)
    vol_pct = hv20.rolling(_VOL_PCT_WINDOW).rank(pct=True)
    return pd.DataFrame({
        "close": close,
        "ma20": close.rolling(_MA_SHORT).mean(),
        "ma60": close.rolling(_MA_MID).mean(),
        "ma120": close.rolling(_MA_LONG).mean(),
        "hv20": hv20,
        "vol_pct": vol_pct,
    })


def build_states(close: pd.Series) -> pd.DataFrame:
    """收盘价序列 → 锚定态历史（纯函数核）。

    Args:
        close: 升序收盘价序列（DatetimeIndex）。

    Returns:
        DataFrame[trade_date, dominant, vol_pct, close, ma20, ma60, ma120]，
        热身期剔除（vol_pct NaN 行不产出），按日期升序。
    """
    if close.empty or not isinstance(close.index, pd.DatetimeIndex):
        return pd.DataFrame(columns=["trade_date", "dominant", "vol_pct", "close", "ma20", "ma60", "ma120"])
    feat = compute_features(close)
    out = feat.dropna(subset=["vol_pct"]).copy()
    out["trade_date"] = out.index.strftime("%Y-%m-%d")
    out["dominant"] = [classify_state(v) for v in out["vol_pct"]]
    out["vol_pct"] = out["vol_pct"].round(6)
    return out[["trade_date", "dominant", "vol_pct", "close", "ma20", "ma60", "ma120"]].reset_index(drop=True)


# ---------------------------------------------------------------------------
# IO 边缘（行情加载 / 写批）
# ---------------------------------------------------------------------------

INSERT_COLUMNS = (
    "(trade_date, dominant, vol_pct, close, ma20, ma60, ma120, data_source)"
)


def load_close(start: str = "2016-06-01") -> pd.Series:
    """000300 收盘价（验收同一标的；start 默认留足 250+20 日热身缓冲到 2019-04）。"""
    from zephyr.data import ch_reader

    tsv = ch_reader.query(
        f"SELECT trade_date, toFloat64(close) AS close FROM c1_market.kline_index "
        f"WHERE symbol = '000300' AND trade_date >= '{start}' ORDER BY trade_date"
    )
    if not tsv or not tsv.strip():
        raise RuntimeError("000300 行情不可达（kline_index 空）")
    rows = [line.split("\t") for line in tsv.strip().split("\n")]
    s = pd.Series(
        [float(r[1]) for r in rows],
        index=pd.DatetimeIndex([r[0] for r in rows]),
        name="close",
    )
    log.info("000300 收盘 %d 日（%s~%s）", len(s), s.index.min().date(), s.index.max().date())
    return s


def run_compute(start: str = "2016-06-01") -> Iterator[FetchResult]:
    """全量重算主流程：加载行情 → 锚定态 → FetchResult 单批（全量重建幂等）。"""
    close = load_close(start)
    states = build_states(close)
    if states.empty:
        raise RuntimeError("锚定态计算结果为空（热身期不足或行情异常），拒绝产出")
    counts = states["dominant"].value_counts().to_dict()
    log.info("锚定态分布：%s", {k: int(v) for k, v in sorted(counts.items())})
    rows = [
        (r.trade_date, r.dominant,
         None if pd.isna(r.vol_pct) else float(r.vol_pct),
         None if pd.isna(r.close) else float(r.close),
         None if pd.isna(r.ma20) else float(r.ma20),
         None if pd.isna(r.ma60) else float(r.ma60),
         None if pd.isna(r.ma120) else float(r.ma120),
         DATA_SOURCE)
        for r in states.itertuples(index=False)
    ]
    yield FetchResult(table=_TABLE, columns=[c.strip() for c in INSERT_COLUMNS.strip("()").split(",")],
                      rows=rows, last_key="", elapsed_sec=0.0)
