# [BLUEPRINT] MOD-BT-FEXAM | docs/03_modules/MOD-BT-FEXAM/ | 抢救证据件（st-matrix-20261007 P0-1 抢救面，st-govfix-g3-20261007 治理入库）
# [not-trading: 抢救证据件（st-matrix-20261007 P0-1 考试现场快照原样转正），非交易运行面，零生产消费链，不挂 TDM 决策图]
# [MODULE] scripts.matrix_rescued_tmp.hmm_retrain.prep_data
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] 见文件内 import
# [CONSUMERS] 无（一次性考卷/对拍/计时证据件；随附数据在 docs/04_research_records/data/matrix_campaign/rescued_tmp_20261007）
# [STARTUP] manual
# [MATURITY] new
# [INVARIANTS] 抢救证据件原样保留，判定面不入核；表名走 TableRegistry 真源
# [MODIFY-GUARD] freeze——抢救证据件禁改写业务逻辑（门禁合规头/noqa 除外）
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 运行期异常如实抛出（证据件不吞错不改判）
# [TESTS] 无独立测试（一次性证据件，输出随件入册）
# [TTL] task_bound
# T道 P2-8 HMM重训回炉 — 数据准备（CH 只读，零既有文件改动）
# 考窗口径与 J 道 state_recognizer_exam_v1 prereg 对齐：
#   训练窗 2019-04-01..2024-12-31 | 验证窗 2025-01-01..2026-08-31 | 前向缓冲 2026-09-30
# 数据源: c1_market.kline_index symbol=000300（close/volume/amount/advance/decline）
#         c1_backtest.regime_snapshot_history（旧模型对照态）
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
RUN_ROOT = HERE.parents[3]
sys.path.insert(0, str(RUN_ROOT / "scripts" / "backtest" / "fexam"))
sys.path.insert(0, str(RUN_ROOT / "src"))

from ch_data import ch_query_df, load_regime_states  # noqa: E402

from zephyr.data.table_registry import get_registry as _get_tbl_registry

# TABLE-NAME-REGISTRY 合规：表名走 TableRegistry 真源（#ARCH-CH-024 Phase 5），抢救证据件同规
_TBL_KLINE_INDEX = _get_tbl_registry().table("market_index_kline")
_TBL_EMO_INDEX = _get_tbl_registry().table("market_emotion_index")
_TBL_TECH_IND = _get_tbl_registry().table("market_technical_indicator")

OUT = HERE
TRAIN = ("2019-04-01", "2024-12-31")
VALID = ("2025-01-01", "2026-08-31")
LOAD_START = "2005-01-01"  # SMA200/250d 分位 warmup
BUFFER_END = "2026-09-30"

SQL_KLINE = (
    "SELECT trade_date, close, volume, amount, advance_count, decline_count "
    f"FROM {_TBL_KLINE_INDEX} WHERE symbol='000300' "
    f"AND trade_date >= '{LOAD_START}' AND trade_date <= '{BUFFER_END}' "
    "ORDER BY trade_date FORMAT TSV"
)

# 涨跌家数真源=399106（生产 MOD-REGIME-002 BREADTH_INDEX 同口径）
SQL_BREADTH = (
    "SELECT trade_date, advance_count, decline_count "
    f"FROM {_TBL_KLINE_INDEX} WHERE symbol='399106' "
    f"AND trade_date >= '{LOAD_START}' AND trade_date <= '{BUFFER_END}' "
    "ORDER BY trade_date FORMAT TSV"
)


def build_features(df: pd.DataFrame) -> pd.DataFrame:
    """PIT 特征：全部只用 ≤ t 数据。返回含 fwd/rv 标签原料的完整帧。"""
    out = pd.DataFrame(index=df.index)
    close = df["close"]
    ret = close.pct_change()
    # ── 趋势族 ──
    out["ret_20d"] = close.pct_change(20)
    out["ret_60d"] = close.pct_change(60)
    sma200 = close.rolling(200, min_periods=200).mean()
    vol20 = ret.rolling(20).std()
    # SMA200 距离按波动单位归一（把 SMA200 基线信号显式喂给 HMM）
    out["sma_dist_z"] = (close / sma200 - 1.0) / (vol20 * np.sqrt(252))
    # ── 波动族（含波动聚类）──
    out["vol20"] = vol20 * np.sqrt(252)
    vol5 = ret.rolling(5).std()
    vol60 = ret.rolling(60).std()
    out["vol_ratio"] = vol5 / vol60  # 短长波比=波动聚集度
    # ── 量能族 ──
    v_mean = df["volume"].rolling(20).mean()
    v_std = df["volume"].rolling(20).std()
    out["volume_z"] = (df["volume"] - v_mean) / v_std.replace(0.0, np.nan)
    adv, dec = df["advance_count"].astype(float), df["decline_count"].astype(float)
    ad = ((adv - dec) / (adv + dec).replace(0.0, np.nan)).rolling(5).mean()
    out["ad_smooth"] = ad.ffill()  # 399106 涨跌家数 2026-07 起断供，ffill 只用过去值（PIT 安全），如实标注
    # ── realized 标签原料（J 道 prereg 逐字口径）──
    out["fwd20"] = close.shift(-20) / close - 1.0
    out["fwd5"] = close.shift(-5) / close - 1.0
    out["fwd60"] = close.shift(-60) / close - 1.0
    out["rv20"] = ret.rolling(20).std()
    out["close"] = close
    return out


def realized_states(f: pd.DataFrame, start: str, end: str) -> pd.Series:
    """J 道 prereg 冻结定义：窗内截面 rv_pct，tercile 边界 1/3、2/3。"""
    w = f.loc[start:end]
    rv_pct = w["rv20"].rank(pct=True)
    fwd = w["fwd20"]
    lab = pd.Series(index=w.index, dtype="object")
    is_tu = (fwd > 0) & (rv_pct <= 2 / 3)
    is_td = fwd < 0
    rest = fwd.notna() & ~(is_tu | is_td)  # 其余 = fwd20≥0 残差档（含 fwd20==0）
    lab[is_tu] = "trend_up"
    lab[is_td] = "trend_down"
    lab[rest & (rv_pct > 1 / 3)] = "ranging_mid_vol"
    lab[rest & (rv_pct <= 1 / 3)] = "ranging_low_vol"
    lab[fwd.isna()] = None
    return lab.rename("realized")


def main() -> None:
    raw = ch_query_df(SQL_KLINE)
    raw.columns = ["trade_date", "close", "volume", "amount", "advance_count", "decline_count"]
    raw["trade_date"] = pd.to_datetime(raw["trade_date"])
    for c in raw.columns[1:]:
        raw[c] = pd.to_numeric(raw[c], errors="coerce")
    raw = raw.dropna(subset=["close"]).set_index("trade_date").sort_index()
    br = ch_query_df(SQL_BREADTH)
    br.columns = ["trade_date", "advance_count", "decline_count"]
    br["trade_date"] = pd.to_datetime(br["trade_date"])
    for c in br.columns[1:]:
        br[c] = pd.to_numeric(br[c], errors="coerce")
    br = br.dropna().set_index("trade_date").sort_index()
    raw["advance_count"] = br["advance_count"].reindex(raw.index)
    raw["decline_count"] = br["decline_count"].reindex(raw.index)
    print(f"kline_index 000300: {len(raw)} rows {raw.index.min().date()}..{raw.index.max().date()}")
    print(f"breadth 399106: {len(br)} rows (ad 覆盖 {br.index.min().date()}..{br.index.max().date()})")

    feats = build_features(raw)
    feats.to_csv(OUT / "features_full.csv")

    realized = realized_states(feats, VALID[0], VALID[1])
    n_nan = int(realized.isna().sum())
    print(f"validation realized rows={len(realized)} fwd20_nan_dropped={n_nan}")
    print(realized.value_counts(dropna=True).to_string())

    old_states = load_regime_states(VALID[0], VALID[1])
    old_states.to_csv(OUT / "old_hmm_states_valid.csv")
    print("old HMM states:", len(old_states), dict(old_states.value_counts()))

    # SMA200 基线（exam 口径: close>sma200→trend_up 否则 trend_down）
    sma200 = feats["close"].rolling(200, min_periods=200).mean()
    baseline = (feats["close"] > sma200).map({True: "trend_up", False: "trend_down"})
    baseline.loc[sma200.isna()] = None
    baseline.loc[VALID[0] : VALID[1]].to_csv(OUT / "sma200_baseline_valid.csv")

    tr_idx = feats.loc[TRAIN[0] : TRAIN[1]].dropna(subset=["ret_60d", "sma_dist_z", "vol_ratio"]).index
    va_idx = feats.loc[VALID[0] : VALID[1]].index
    print(f"train feature rows={len(tr_idx)} ({tr_idx.min().date()}..{tr_idx.max().date()})")
    print(f"valid rows={len(va_idx)}")
    pd.Series(tr_idx).to_csv(OUT / "train_idx.csv", index=False)
    pd.Series(va_idx).to_csv(OUT / "valid_idx.csv", index=False)


if __name__ == "__main__":
    main()
