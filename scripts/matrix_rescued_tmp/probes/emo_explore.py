# [BLUEPRINT] MOD-BT-FEXAM | docs/03_modules/MOD-BT-FEXAM/ | 抢救证据件（st-matrix-20261007 P0-1 抢救面，st-govfix-g3-20261007 治理入库）
# [not-trading: 抢救证据件（st-matrix-20261007 P0-1 考试现场快照原样转正），非交易运行面，零生产消费链，不挂 TDM 决策图]
# [MODULE] scripts.matrix_rescued_tmp.probes.emo_explore
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
# emo_explore.py — O道情绪指数首考·数据探查（CH 只读，DESCRIBE/样本行，不跑考卷）
# 纪律：只读 SELECT；fail-closed。
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

RUN_ROOT = Path(__file__).resolve().parents[3]
_SRC = RUN_ROOT / "src"
if _SRC.exists() and str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

CH_BASE = "http://172.24.30.100:8123/"
_OPENER = request.build_opener(request.ProxyHandler({}))  # 绕系统代理，同 ch_data.py


def q_raw(sql: str) -> str:
    lowered = sql.lstrip().lower()
    if not lowered.startswith(("select", "with", "describe", "exists")):
        raise RuntimeError(f"拒绝非只读查询: {sql[:80]}")
    try:
        req = request.Request(CH_BASE, data=sql.encode("utf-8"), method="POST")
        return _OPENER.open(req, timeout=60).read().decode("utf-8", errors="replace")
    except Exception as exc:  # fail-closed
        raise RuntimeError(f"CH query failed: {exc}") from exc


def q(sql: str) -> pd.DataFrame:
    raw = q_raw(sql)
    if not raw.strip():
        return pd.DataFrame()
    return pd.read_csv(io.StringIO(raw), sep="\t", dtype=str)


def main() -> None:
    print(f"== DESCRIBE {_TBL_EMO_INDEX} ==")
    print(q_raw(f"DESCRIBE TABLE {_TBL_EMO_INDEX} FORMAT TSVWithNames"))

    print("\n== emotion_index head/tail 样本 ==")
    print(q_raw(f"SELECT * FROM {_TBL_EMO_INDEX} ORDER BY trade_date LIMIT 5 FORMAT Vertical"))  # noqa: bare-sql  抢救证据件SQL原样保留不改写（12字理由）
    print(q_raw(f"SELECT * FROM {_TBL_EMO_INDEX} ORDER BY trade_date DESC LIMIT 5 FORMAT Vertical"))  # noqa: bare-sql  抢救证据件SQL原样保留不改写（12字理由）

    print("\n== emotion_index 全行数/日期范围 ==")
    print(
        q(
            "SELECT count() AS n, min(trade_date) AS dmin, max(trade_date) AS dmax"
            f" FROM {_TBL_EMO_INDEX} FORMAT TSVWithNames"
        ).to_string(index=False)
    )

    print("\n== emotion_index 版本/状态分布（若列存在） ==")
    desc = q(f"DESCRIBE TABLE {_TBL_EMO_INDEX}")
    cols = desc["name"].tolist()
    for cand in ("value_status", "status", "version", "schema_version", "data_status"):
        if cand in cols:
            print(
                q(f"SELECT {cand}, count() AS n FROM {_TBL_EMO_INDEX} GROUP BY {cand} FORMAT TSVWithNames").to_string(  # noqa: bare-sql  抢救证据件SQL原样保留不改写（12字理由）
                    index=False
                )
            )

    print("\n== 同日多行检查（快照/修订语义） ==")
    dup = q(
        "SELECT trade_date, count() AS n FROM {_TBL_EMO_INDEX}"  # noqa: bare-sql  抢救证据件SQL原样保留不改写（12字理由）
        " GROUP BY trade_date HAVING n > 1 ORDER BY trade_date DESC LIMIT 10 FORMAT TSVWithNames"
    )
    print(dup.to_string(index=False) if not dup.empty else "无同日多行")

    print("\n== DESCRIBE {_TBL_KLINE_INDEX} ==")
    print(q_raw(f"DESCRIBE TABLE {_TBL_KLINE_INDEX} FORMAT TSVWithNames"))
    print(
        q(
            "SELECT count() AS n, min(trade_date) AS dmin, max(trade_date) AS dmax"
            f" FROM {_TBL_KLINE_INDEX} WHERE symbol='000300' FORMAT TSVWithNames"
        ).to_string(index=False)
    )
    print(
        q_raw(
            f"SELECT * FROM {_TBL_KLINE_INDEX} WHERE symbol='000300' ORDER BY trade_date DESC LIMIT 3 FORMAT Vertical"  # noqa: bare-sql  抢救证据件SQL原样保留不改写（12字理由）
        )
    )


if __name__ == "__main__":
    main()
