# [BLUEPRINT] MOD-BT-FEXAM | docs/03_modules/MOD-BT-FEXAM/ | 抢救证据件（st-matrix-20261007 P0-1 抢救面，st-govfix-g3-20261007 治理入库）
# [not-trading: 抢救证据件（st-matrix-20261007 P0-1 考试现场快照原样转正），非交易运行面，零生产消费链，不挂 TDM 决策图]
# [MODULE] scripts.matrix_rescued_tmp.probes.emo_pit
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
# emo_pit.py — O道 PIT 实测核查（CH 只读，pandas 判定）：ts 时点、asof 越界、kline_index 概览
from __future__ import annotations

import io
import json
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


def q_df(sql: str, timeout: int = 180) -> pd.DataFrame:
    lowered = sql.lstrip().lower()
    if not lowered.startswith(("select", "with", "describe", "exists")):
        raise RuntimeError(f"拒绝非只读查询: {sql[:80]}")
    req = request.Request(CH_BASE, data=sql.encode("utf-8"), method="POST")
    raw = _OPENER.open(req, timeout=timeout).read().decode("utf-8", errors="replace")
    if not raw.strip():
        return pd.DataFrame()
    return pd.read_csv(io.StringIO(raw), sep="\t", dtype=str)


def asof_scan(df: pd.DataFrame, stage: str) -> None:
    bad = 0
    per_comp: dict[str, int] = {}
    samples: list[str] = []
    for _, row in df.iterrows():
        td = str(row["trade_date"])
        try:
            comps = json.loads(str(row["components"]).replace("\\'", "'"))
        except Exception:  # noqa: BLE001 — 抢救证据件原样保留（零行为变更）
            samples.append(f"{td} JSON_PARSE_FAIL")
            continue
        for c in comps:
            asof = str(c.get("asof", "") or "")
            if asof and asof > td:
                bad += 1
                name = str(c.get("name", "?"))
                per_comp[name] = per_comp.get(name, 0) + 1
                if len(samples) < 4:
                    samples.append(f"{td} {name} asof={asof}")
    print(f"[{stage}] n={len(df)} asof>trade_date 违例={bad} 按成分={per_comp or '无'}")
    if samples:
        print("  样本:", samples)


def main() -> None:
    win = f"trade_date >= '{W0}' AND trade_date <= '{W1}'"
    df = q_df(
        "SELECT trade_date, stage, ts, emotion_index, ingest_ts, source, components"
        " FROM {_TBL_EMO_INDEX} ORDER BY trade_date, stage, ingest_ts FORMAT TSVWithNames"
    )
    df["td"] = df["trade_date"].astype(str)

    for stage, want in (("close_final", " 15:10:00.000"), ("pre_open", " 09:15:00.000")):
        sub = df[df["stage"] == stage]
        inwin = sub[(sub["td"] >= W0) & (sub["td"] <= W1)]
        bad_all = int((~sub["ts"].astype(str).str.endswith(want)).sum())
        bad_win = int((~inwin["ts"].astype(str).str.endswith(want)).sum())
        bad_date = int((sub["ts"].astype(str).str[:10] != sub["td"]).sum())
        print(
            f"[{stage}] 全表 n={len(sub)} ts时点≠{want.strip()}: {bad_all}  考窗内 n={len(inwin)} 违例: {bad_win}  ts日期≠trade_date(全表): {bad_date}"
        )
        if bad_win:
            print(
                "  窗内违例样本:",
                inwin.loc[~inwin["ts"].astype(str).str.endswith(want), ["trade_date", "ts"]].head(5).values.tolist(),
            )
        if bad_all:
            vc = sub.loc[~sub["ts"].astype(str).str.endswith(want), "ts"].str[11:19].value_counts().to_dict()
            yr = sorted(sub.loc[~sub["ts"].astype(str).str.endswith(want), "td"].str[:4].unique())
            print("  窗外违例时点分布:", vc, " 涉及年份:", yr)

    print("\n-- asof 越界扫描（asof > trade_date = 前视） --")
    asof_scan(df[(df["stage"] == "close_final") & (df["td"] >= W0) & (df["td"] <= W1)], "close_final@考窗")
    asof_scan(df[(df["stage"] == "pre_open") & (df["td"] >= W0) & (df["td"] <= W1)], "pre_open@考窗")

    # replay 批次 ingest_ts 分布（考窗 close_final）
    sub = df[(df["stage"] == "close_final") & (df["td"] >= W0) & (df["td"] <= W1)]
    print("\n考窗 close_final ingest_ts 分布:", sub["ingest_ts"].value_counts().to_dict())

    print("\n== {_TBL_KLINE_INDEX}（000300） ==")
    print(q_df(f"DESCRIBE TABLE {_TBL_KLINE_INDEX} FORMAT TSVWithNames").to_string(index=False))
    print(
        q_df(
            "SELECT count() AS n, min(trade_date) AS dmin, max(trade_date) AS dmax"
            f" FROM {_TBL_KLINE_INDEX} WHERE symbol='000300' FORMAT TSVWithNames"
        ).to_string(index=False)
    )
    print(
        q_df(
            "SELECT count() AS n, min(trade_date) AS dmin, max(trade_date) AS dmax"
            f" FROM {_TBL_KLINE_INDEX} WHERE symbol='000300' AND trade_date >= '{W0}' AND trade_date <= '{W1}'"
            " FORMAT TSVWithNames"
        ).to_string(index=False)
    )
    print(
        q_df(
            f"SELECT trade_date, close FROM {_TBL_KLINE_INDEX} WHERE symbol='000300'"  # noqa: bare-sql  抢救证据件SQL原样保留不改写（12字理由）
            " ORDER BY trade_date DESC LIMIT 3 FORMAT TSVWithNames"
        ).to_string(index=False)
    )


if __name__ == "__main__":
    main()
