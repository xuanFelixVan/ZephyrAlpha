# [BLUEPRINT] MOD-BT-FEXAM | docs/03_modules/MOD-BT-FEXAM/ | 抢救证据件（st-matrix-20261007 P0-1 抢救面，st-govfix-g3-20261007 治理入库）
# [not-trading: 抢救证据件（st-matrix-20261007 P0-1 考试现场快照原样转正），非交易运行面，零生产消费链，不挂 TDM 决策图]
# [MODULE] scripts.matrix_rescued_tmp.probes.emo_explore2
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
# emo_explore2.py — O道 PIT/结构深探（CH 只读）：stage/版本分布、同键修订、ts 时点、asof 越界、kline_index
from __future__ import annotations

import io
import json
import sys
from functools import partial
from pathlib import Path
from urllib import request

import pandas as pd
from emo_pit import q_df as _q_df_pit  # noqa: E402  同目录证据件 sibling import（scripts 直跑语义）

from zephyr.data.table_registry import get_registry as _get_tbl_registry

# TABLE-NAME-REGISTRY 合规：表名走 TableRegistry 真源（#ARCH-CH-024 Phase 5），抢救证据件同规
_TBL_KLINE_INDEX = _get_tbl_registry().table("market_index_kline")
_TBL_EMO_INDEX = _get_tbl_registry().table("market_emotion_index")
_TBL_TECH_IND = _get_tbl_registry().table("market_technical_indicator")

CH_BASE = "http://172.24.30.100:8123/"
_OPENER = request.build_opener(request.ProxyHandler({}))

W0, W1 = "2019-04-01", "2026-08-31"


# CloneGuard extract 级去重（CAPABILITY-OVERLAP 门禁处方 import_suggestion）：
# 原 q_df 与 emo_pit.q_df 同构（唯一差异 timeout 120/180），改由 emo_pit 导入并
# 以 partial 固化本卷原 timeout=120，运行语义与证据面输出不变。
q_df = partial(_q_df_pit, timeout=120)


def main() -> None:
    win = f"trade_date >= '{W0}' AND trade_date <= '{W1}'"

    print("== stage x version x source 分布（全表 / 考窗） ==")
    print(
        q_df(
            "SELECT stage, version, source, count() AS n_all,"
            f" countIf({win}) AS n_window FROM {_TBL_EMO_INDEX}"
            " GROUP BY stage, version, source ORDER BY stage, source FORMAT TSVWithNames"
        ).to_string(index=False)
    )

    print("\n== 考窗 close_final 日期范围 ==")
    print(
        q_df(
            "SELECT count() AS n, min(trade_date) AS dmin, max(trade_date) AS dmax"
            f" FROM {_TBL_EMO_INDEX} WHERE stage='close_final' AND {win} FORMAT TSVWithNames"
        ).to_string(index=False)
    )

    print("\n== 同键 (trade_date,stage) 多行：全表 vs 考窗 close_final ==")
    print(
        q_df(
            "SELECT stage, count() AS dup_keys, sum(n) AS extra_rows, countIf(n > 1 AND versions > 1) AS keys_with_diff_values"
            " FROM (SELECT trade_date, stage, count() AS n, uniqExact(emotion_index) AS versions"
            f" FROM {_TBL_EMO_INDEX} GROUP BY trade_date, stage)"
            " GROUP BY stage ORDER BY stage FORMAT TSVWithNames"
        ).to_string(index=False)
    )
    print("-- 考窗 close_final 同键多行样本 --")
    print(
        q_df(
            "SELECT trade_date, count() AS n, uniqExact(emotion_index) AS versions,"
            " groupArray(DISTINCT ingest_ts) AS ingest_list"
            f" FROM {_TBL_EMO_INDEX} WHERE stage='close_final' AND {win}"
            " GROUP BY trade_date HAVING n > 1 ORDER BY trade_date LIMIT 8 FORMAT TSVWithNames"
        ).to_string(index=False)
    )

    print("\n== ts 时点违规（考窗 close_final 应=当日 15:10；pre_open 应=当日 09:15） ==")
    print(
        q_df(
            "SELECT stage,"
            f" countIf({win} AND stage='close_final' AND toTime(ts) != toTime('15:10:00')) AS cf_bad_ts,"
            f" countIf({win} AND stage='pre_open' AND toTime(ts) != toTime('09:15:00')) AS po_bad_ts,"
            f" countIf({win} AND stage='close_final' AND toDate(ts) != trade_date) AS cf_ts_date_mismatch,"
            f" countIf({win} AND stage='pre_open' AND toDate(ts) != trade_date) AS po_ts_date_mismatch"
            f" FROM {_TBL_EMO_INDEX} FORMAT TSVWithNames"
        ).to_string(index=False)
    )

    print("\n== components asof 越界检查（考窗 close_final：某成分 asof > trade_date 即前视） ==")
    df = q_df(
        "SELECT trade_date, components FROM {_TBL_EMO_INDEX}"  # noqa: bare-sql  抢救证据件SQL原样保留不改写（12字理由）
        f" WHERE stage='close_final' AND {win} ORDER BY trade_date FORMAT TSV"
    )
    bad = 0
    bad_rows: list[str] = []
    asof_future_components: dict[str, int] = {}
    for _, row in df.iterrows():
        td = str(row["trade_date"])
        try:
            comps = json.loads(row["components"])
        except Exception:  # noqa: BLE001 — 抢救证据件原样保留（零行为变更）
            bad_rows.append(td + " JSON_PARSE_FAIL")
            continue
        for c in comps:
            asof = str(c.get("asof", "") or "")
            if asof and asof > td:
                bad += 1
                name = str(c.get("name", "?"))
                asof_future_components[name] = asof_future_components.get(name, 0) + 1
                if len(bad_rows) < 6:
                    bad_rows.append(f"{td} {name} asof={asof}")
    print(f"考窗 close_final 行数={len(df)}，asof>trade_date 违例成分次数={bad}")
    print("按成分:", asof_future_components or "无")
    print("样本:", bad_rows or "无")

    print("\n== DESCRIBE {_TBL_KLINE_INDEX} ==")
    print(q_df(f"DESCRIBE TABLE {_TBL_KLINE_INDEX} FORMAT TSVWithNames").to_string(index=False))
    print(
        q_df(
            "SELECT count() AS n, min(trade_date) AS dmin, max(trade_date) AS dmax,"
            " countIf(close IS NULL OR close=0) AS bad_close"
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


if __name__ == "__main__":
    main()
