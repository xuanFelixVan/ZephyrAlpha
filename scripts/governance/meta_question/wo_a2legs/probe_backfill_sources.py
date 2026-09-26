# [BLUEPRINT] MOD-METAQ-WO-A2LEGS-P4 | docs/_working/meta_question_answers/01_phase2_plan.md §数据施工需求清单(PQ-0013/0040/0045/0085)
# [MODULE] scripts.governance.meta_question.wo_a2legs.probe_backfill_sources
# [DOMAIN] D_DATA
# [DEPENDENCIES] tushare; zephyr.shared.security.secrets; akshare
# [CONSUMERS] WO-A2LEGS 案卷（板块资金流/成分可回溯性取证结论）
# [STARTUP] manual
# [MATURITY] experimental
# [INVARIANTS] 只读取证零写库；接口 404/权限不足/网络不可达 三类失败分开登记（口径不同：
#              不可达=网络封锁、权限不足=积分面、无该接口=渠道根本不提供）；
#              每个成功接口必须报 最早日期/最晚日期/行数/字段名，作为"窗能否真拿到"的硬证据。
# [MODIFY-GUARD] none
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 单接口异常捕获入 JSON，不中断其余接口。
# [TESTS] 无（一次性取证脚本）
# [A_module] module_id=MOD-METAQ-WO-A2LEGS-P4 | layer=script | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound
"""板块资金流 + 成分映射"可回溯性"源侧取证（2021-01-04~2025-09-09 窗能不能真拿到）。

用法：python .../probe_backfill_sources.py --only ts|ak|both
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import warnings
from pathlib import Path

warnings.filterwarnings("ignore")
_ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(_ROOT / "src"))

from zephyr.shared.security.secrets import get_secret_or_default  # noqa: E402

CUT_START, CUT_END = "20210104", "20250909"
DAY_COL = ("trade_date", "日期", "交易日")


def _date_span(df) -> dict:
    cols = list(df.columns)
    col = next((c for c in cols if c in DAY_COL), None)
    if col is None:
        return {"date_col": None}
    s = df[col].astype(str)
    return {"date_col": col, "min": str(s.min()), "max": str(s.max()), "rows": int(len(df))}


def probe_tushare() -> dict:
    import tushare as ts

    tok = get_secret_or_default("TUSHARE_TOKEN")
    if not tok:
        return {"error": "TUSHARE_TOKEN 未配置"}
    ts.set_token(tok)
    pro = ts.pro_api()
    res: dict = {}
    calls = {
        # 板块/行业级资金流（日频）
        "moneyflow_ind_dc": lambda: pro.moneyflow_ind_dc(trade_date="20240315"),
        "moneyflow_ind_ths": lambda: pro.moneyflow_ind_ths(trade_date="20240315"),
        "moneyflow_cnt_ths": lambda: pro.moneyflow_cnt_ths(trade_date="20240315"),
        "moneyflow_mkt_dc": lambda: pro.moneyflow_mkt_dc(trade_date="20240315"),
        "moneyflow_ind_em(若存在)": lambda: (
            getattr(pro, "moneyflow_ind_em", None) and pro.moneyflow_ind_em(trade_date="20240315")
        ),
        # 深历史单点探针（切点前段/后段各一次，判窗覆盖）
        "moneyflow_ind_dc@20210104": lambda: pro.moneyflow_ind_dc(trade_date="20210104"),
        "moneyflow_ind_dc@20250909": lambda: pro.moneyflow_ind_dc(trade_date="20250909"),
        "moneyflow_ind_ths@20210104": lambda: pro.moneyflow_ind_ths(trade_date="20210104"),
        "moneyflow_ind_ths@20250909": lambda: pro.moneyflow_ind_ths(trade_date="20250909"),
        # 板块指数日线（资金流代理腿）
        "ths_daily@20240315": lambda: pro.ths_daily(trade_date="20240315"),
        "sw_daily@20240315": lambda: pro.sw_daily(ts_code="801010.SI", start_date="20240301", end_date="20240320"),
        # 成分映射（带 in_date/out_date 的 PIT 面）
        "index_classify": lambda: pro.index_classify(level="L1", src="SW2021"),
        "index_member": lambda: pro.index_member(index_code="801010.SI", is_new=""),
        "index_member_all": lambda: pro.index_member_all(l1_code="801010.SI"),
        "ths_index": lambda: pro.ths_index(exchange="A", type="N"),
        "ths_member": lambda: pro.ths_member(ts_code="881101.TI"),
        "ths_member(概念)": lambda: pro.ths_member(ts_code="885500.TI"),
    }
    for name, fn in calls.items():
        try:
            df = fn()
            if df is None:
                res[name] = {"status": "none_returned"}
                continue
            res[name] = {"status": "ok", "cols": list(df.columns)[:24], **_date_span(df), "rows": int(len(df))}
        except Exception as exc:  # noqa: BLE001
            msg = f"{type(exc).__name__}: {str(exc)[:180]}"
            kind = (
                "no_api"
                if "No such" in msg or "has no" in msg or "not exist" in msg
                else "permission_or_rate"
                if ("积分" in msg or "权限" in msg or "抱歉" in msg or "每分钟" in msg or "token" in msg.lower())
                else "other"
            )
            res[name] = {"status": "error", "kind": kind, "msg": msg}
    return res


def probe_akshare() -> dict:
    import akshare as ak

    res: dict = {}
    calls = {
        "stock_sector_fund_flow_hist(同花顺行业历史)": lambda: ak.stock_sector_fund_flow_hist(symbol="煤炭开采"),
        "stock_concept_fund_flow_hist(同花顺概念历史)": lambda: ak.stock_concept_fund_flow_hist(symbol="AI手机"),
        "stock_fund_flow_industry(即时)": lambda: ak.stock_fund_flow_industry(symbol="即时"),
        "stock_board_industry_hist_em(东财行业指数日线)": lambda: ak.stock_board_industry_hist_em(
            symbol="煤炭开采", start_date="20210104", end_date="20250909", period="日k", adjust=""
        ),
        "stock_board_industry_name_em(东财行业列表)": lambda: ak.stock_board_industry_name_em(),
        "stock_board_industry_cons_em(东财行业成分)": lambda: ak.stock_board_industry_cons_em(symbol="煤炭开采"),
        "stock_board_concept_name_ths": lambda: ak.stock_board_concept_name_ths(),
        "stock_board_industry_index_ths(THS行业指数日线)": lambda: ak.stock_board_industry_index_ths(
            symbol="煤炭开采", start_date="20210104", end_date="20250909"
        ),
    }
    for name, fn in calls.items():
        try:
            df = fn()
            res[name] = {
                "status": "ok",
                "rows": int(len(df)),
                "cols": list(df.columns)[:16],
                **_date_span(df),
                "sample": df.head(2).astype(str).to_dict("records"),
            }
        except Exception as exc:  # noqa: BLE001
            msg = f"{type(exc).__name__}: {str(exc)[:160]}"
            kind = (
                "network_blocked"
                if (
                    "RemoteDisconnected" in msg
                    or "Connection" in msg
                    or "Max retries" in msg
                    or "Failed to establish" in msg
                )
                else "parse_or_auth"
                if ("404" in msg or "JSONDecodeError" in msg or "KeyError" in msg)
                else "other"
            )
            res[name] = {"status": "error", "kind": kind, "msg": msg}
    return res


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default="both", choices=["ts", "ak", "both"])
    args = ap.parse_args()
    out = {}
    if args.only in ("ts", "both"):
        out["tushare"] = probe_tushare()
    if args.only in ("ak", "both"):
        out["akshare"] = probe_akshare()
    print(json.dumps(out, ensure_ascii=False, indent=1, default=str))


if __name__ == "__main__":
    main()
