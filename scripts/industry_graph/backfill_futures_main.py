# [BLUEPRINT] MOD-DATA-FUTBF
# [BLUEPRINT-NOTE] 研究件无蓝图正本, 登记见 depgraph 设计节点
# [MODULE] scripts.industry_graph.backfill_futures_main
# [DOMAIN] D_DATA
# [DEPENDENCIES] akshare
# [CONSUMERS] 线B 期货回补子块(B-1/B-5); 生产接入(tasks.yaml/DDL)的 staged 数据源
# [STARTUP] manual
# [MATURITY] research
# [INVARIANTS] 只写 .runtime/tmp/chain_alpha/futures_backfill/; 每品种一个 CSV; 断点续拉(已有文件跳过除非 --force); 429/网络失败记 FAILED 清单不中断; 接口=futures_main_sina(2026-09-17 实锤 lc/si/ps/lh/cu 可用)
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 全品种失败->退出码2; 部分失败打印清单退出码0(断点重跑)
# [TESTS] 断点续拉自证(重跑 cached 跳过)+FAILED 清单(数据回补件, 独立 pytest 待生产接线批)
# [TTL-PROMOTE] 因子入库晋升 permanent 走正门
# [TTL] task_bound
"""期货主力连续历史回补（staged，生产落库待 tasks.yaml/DDL 排期）。

按品种清单拉 akshare futures_main_sina 全历史，落 CSV 到
.runtime/tmp/chain_alpha/futures_backfill/{symbol}.csv。
默认清单=T0 锚卡首批：生猪 lh / 碳酸锂 lc / 工业硅 si / 多晶硅 ps / 豆粕 m /
玉米 c / 鸡蛋 jd / 铜 cu / 铝 al。

用法::
    python scripts/industry_graph/backfill_futures_main.py [--force] [--symbols lh0,lc0]
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from datetime import date
from pathlib import Path

import akshare as ak

OUT_DIR = Path(".runtime/tmp/chain_alpha/futures_backfill")
DEFAULT_SYMBOLS = ["lh0", "lc0", "si0", "ps0", "m0", "c0", "jd0", "cu0", "al0"]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--symbols", default=",".join(DEFAULT_SYMBOLS))
    ap.add_argument("--start", default="20150101")
    ap.add_argument("--end", default=date.today().strftime("%Y%m%d"))
    ap.add_argument("--force", action="store_true", help="重拉已存在品种")
    args = ap.parse_args()
    symbols = [s.strip() for s in args.symbols.split(",") if s.strip()]
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    ok, failed = [], []
    for sym in symbols:
        out = OUT_DIR / f"{sym}.csv"
        if out.exists() and not args.force:
            ok.append({"symbol": sym, "status": "cached"})
            continue
        try:
            df = ak.futures_main_sina(
                symbol=sym, start_date=args.start, end_date=args.end
            )
            if df is None or len(df) == 0:
                failed.append({"symbol": sym, "error": "empty"})
                continue
            tmp = out.with_suffix(".csv.tmp")
            df.to_csv(tmp, index=False, encoding="utf-8")
            os.replace(tmp, out)
            dcol = df.columns[0]
            dfs = df.sort_values(dcol)
            ok.append(
                {
                    "symbol": sym,
                    "rows": len(dfs),
                    "range": f"{dfs.iloc[0][dcol]}~{dfs.iloc[-1][dcol]}",
                }
            )
        except Exception as e:  # noqa: BLE001 — 断点续拉语义
            failed.append({"symbol": sym, "error": f"{type(e).__name__}: {e}"[:120]})
    time.sleep(1)
    report = {"ok": ok, "failed": failed, "out_dir": str(OUT_DIR)}
    print(json.dumps(report, ensure_ascii=False, indent=1))
    if len(ok) == 0 and failed:
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
