# [BLUEPRINT] MOD-BT-FEXAM | docs/03_modules/MOD-BT-FEXAM/ | 抢救证据件（st-matrix-20261007 P0-1 抢救面，st-govfix-g3-20261007 治理入库）
# [not-trading: 抢救证据件（st-matrix-20261007 P0-1 考试现场快照原样转正），非交易运行面，零生产消费链，不挂 TDM 决策图]
# [MODULE] scripts.matrix_rescued_tmp.probes.emo_adequacy
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] 见文件内 import
# [CONSUMERS] 无（一次性考卷/对拍/计时证据件；随附数据在 docs/_working/matrix_campaign/rescued_tmp_20261007/）
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
# emo_adequacy.py — 冻结前样本充分性检查（只看边际分布/覆盖，不算任何前向收益）
from __future__ import annotations

import io
import sys
from pathlib import Path
from urllib import request

import pandas as pd

from zephyr.data.table_registry import get_registry as _get_tbl_registry

# TABLE-NAME-REGISTRY 合规：表名走 TableRegistry 真源（#ARCH-CH-024 Phase 5），抢救证据件同规
_TBL_KLINE_INDEX = _get_tbl_registry().table("market_index_kline")
_TBL_EMO_INDEX = _get_tbl_registry().table("market_emotion_index")
_TBL_TECH_IND = _get_tbl_registry().table("market_technical_indicator")

CH_BASE = "http://172.24.30.100:8123/"
_OPENER = request.build_opener(request.ProxyHandler({}))
W0, W1 = "2019-04-01", "2026-08-31"


def q_df(sql: str) -> pd.DataFrame:
    if not sql.lstrip().lower().startswith(("select", "with", "describe")):
        raise RuntimeError("非只读")
    req = request.Request(CH_BASE, data=sql.encode("utf-8"), method="POST")
    raw = _OPENER.open(req, timeout=180).read().decode("utf-8", errors="replace")
    if not raw.strip():
        return pd.DataFrame()
    return pd.read_csv(io.StringIO(raw), sep="\t", dtype=str)


def main() -> None:
    win = f"trade_date >= '{W0}' AND trade_date <= '{W1}'"
    emo = q_df(
        "SELECT trade_date, emotion_index FROM {_TBL_EMO_INDEX}"  # noqa: bare-sql  抢救证据件SQL原样保留不改写（12字理由）
        f" WHERE stage='close_final' AND {win} ORDER BY trade_date FORMAT TSVWithNames"
    )
    emo["e"] = emo["emotion_index"].astype(float)
    print(
        f"考窗 close_final n={len(emo)}  min={emo['e'].min():.4f} max={emo['e'].max():.4f} mean={emo['e'].mean():.4f}"
    )
    print("分位:", {p: round(emo["e"].quantile(p / 100), 4) for p in (1, 5, 10, 25, 50, 75, 90, 95, 99)})
    print(
        f"n(e>=0.90)={int((emo['e'] >= 0.90).sum())}  n(e<=0.10)={int((emo['e'] <= 0.10).sum())}  n(0.10<e<0.90)={int(((emo['e'] > 0.10) & (emo['e'] < 0.90)).sum())}"
    )

    k = q_df(
        f"SELECT trade_date, close FROM {_TBL_KLINE_INDEX} WHERE symbol='000300'"  # noqa: bare-sql  抢救证据件SQL原样保留不改写（12字理由）
        f" AND {win} ORDER BY trade_date FORMAT TSVWithNames"
    )
    k["close"] = k["close"].astype(float)
    print(
        f"\n考窗 000300 n={len(k)}  {k['trade_date'].min()}..{k['trade_date'].max()}  close 缺失={int(k['close'].isna().sum())}"
    )
    emos, ks = set(emo["trade_date"]), set(k["trade_date"])
    print(f"情绪日∩K线日={len(emos & ks)}  情绪独有={sorted(emos - ks)[:10]}  K线独有={len(ks - emos)}")

    k_all = k["close"]
    sma200 = k_all.rolling(200, min_periods=200).mean()
    in_win_sma = sma200.notna().sum()
    print(f"SMA200 考窗内可得={in_win_sma}/{len(k)}（2005 起算应全覆盖）")


if __name__ == "__main__":
    main()
