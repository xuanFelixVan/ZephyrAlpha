# [BLUEPRINT] MOD-BT-090 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] scripts.backtest.three_high_screen
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] numpy; pandas; zephyr.governance.depgraph_schema; zephyr.data.ch_config; zephyr.data.ch_writer
# [CONSUMERS] 策略生产全景图 FAC-E1D 车道D（产业链三高）；FAC-E2 假说预审（候选想法供给方）；
#   data/strategy_intake/three_high_candidates.csv（进货台账）
# [STARTUP] manual
# [MATURITY] experimental
# [MODIFY-GUARD] none
# [INVARIANTS] 出生证字段（birth_channel/birth_batch/birth_source）由本模块代码机器写入，AI 禁手填；
#   本车道只产出候选想法（描述性排序），考试权只在 E4（运动员不兼任裁判）；
#   候选 id=CAND-md5_12('E1D:'+环节名) 稳定可重跑；台账只追加；零 LLM 依赖；
#   财务列只取 announce_date 最新行（PIT 口径）
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] RuntimeError(PG/CH 不可达或聚合结果为空); SystemExit(2)(参数错)
# [TESTS] tests/backtest/test_three_high_screen.py
# [A_module] module_id=MOD-BT-090 | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# noqa: m11-perm-manual-legitimate  手动 CLI 筛选器非常驻服务：由工厂编排批次调用（E1 进货编排接线前由人工/会话触发），无常驻循环
"""FAC-E1D 产业链三高车道——ig_fact 图谱 BOM 拆解 + 三高筛选（高增长/高壁垒/高利润）。

原理（讨论稿 §五：产业链三高拆解法，Capponi 供应链图谱多跳验证）：
  环节 = ig_fact belongs_to_sector 的板块（申万口径，335 个）。
  高增长 = 成员股营收/净利 YoY 中位数（c3_fundamental.financial_indicator，announce_date PIT）；
  高利润 = 成员股毛利率/净利率中位数（同上）；
  高壁垒 = 成员股前五大客户集中度/客户 HHI 中位数（ig_company_metric，客户粘性=转换成本）；
  咽喉度 = 成员股产品（produces）在 supplies_to 供给网的下游依赖广度 − 供给替代压力
          （被多环节依赖且替代源少 = 产业链咽喉，ig_fact BOM 网络）。
四支柱 winsorized z 分加权合成，产出候选想法（带出生证）卸到 data/strategy_intake/。
零 LLM 依赖；本模块不打分不及格线，排序只供 E2 预审排产。

用法:
  python scripts/backtest/three_high_screen.py screen --top 20 --dry-run
  python scripts/backtest/three_high_screen.py screen --top 20 --min-members 5
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd

_ROOT = Path(__file__).resolve().parents[2]
_INTAKE_CSV = _ROOT / "data" / "strategy_intake" / "three_high_candidates.csv"

PILLAR_WEIGHTS = {"growth": 0.30, "margin": 0.25, "barrier": 0.25, "chokepoint": 0.20}
FLAG_THRESHOLD = 0.5  # 支柱 z 分 ≥ +0.5 记该"高"
BIRTH_CHANNEL = "D"
BIRTH_SOURCE = ("ig_fact(belongs_to_sector+produces+supplies_to) + "
                "ig_company_metric + TableRegistry:fund_financial_indicator")

# SQL 常量集中化（§5.160.2）；CH 表名走 TableRegistry 真源（#ARCH-CH-024）
_FIN_TABLE = "{fin_table}"  # 运行时由 TableRegistry.table('fund_financial_indicator') 注入
SQL_MEMBER = (
    "SELECT object AS sector, subject AS symbol, count(*) AS n "
    "FROM ig_fact WHERE relation='belongs_to_sector' GROUP BY 1, 2"
)
SQL_BARRIER = (
    "SELECT DISTINCT symbol, metric, value FROM ig_company_metric "
    "WHERE metric IN ('customer_top5_ratio','customer_hhi') AND year = "
    "(SELECT max(year) FROM ig_company_metric)"
)
SQL_CHOKEPOINT = (
    "WITH prod AS (SELECT DISTINCT subject AS symbol, object AS product "
    "  FROM ig_fact WHERE relation='produces'), "
    "down AS (SELECT f.subject AS product, count(DISTINCT f.object) AS breadth "
    "  FROM ig_fact f WHERE f.relation='supplies_to' GROUP BY 1), "
    "up AS (SELECT f.object AS product, count(DISTINCT f.subject) AS pressure "
    "  FROM ig_fact f WHERE f.relation='supplies_to' GROUP BY 1) "
    "SELECT p.symbol, avg(d.breadth) AS downstream_breadth, "
    "       avg(u.pressure) AS supply_pressure "
    "FROM prod p JOIN down d ON d.product = p.product "
    "JOIN up u ON u.product = p.product GROUP BY 1"
)
SQL_FINANCIAL_TMPL = (
    "SELECT symbol_canonical, announce_date, revenue_yoy, net_profit_yoy, "
    "gross_margin, net_margin FROM " + _FIN_TABLE + " "
    "WHERE symbol_canonical != ''"
)


def _fin_sql() -> str:
    from zephyr.data.table_registry import get_registry

    return SQL_FINANCIAL_TMPL.format(fin_table=get_registry().table("fund_financial_indicator"))


def winsor_z(s: pd.Series, pct_clip: float = 0.05) -> pd.Series:
    """winsorize 到分位 [5,95] 后 z 标准化（防环节样本极值绑架排序；返回有界 z，NaN 记 0）。"""
    x = pd.to_numeric(s, errors="coerce").astype(float)
    lo, hi = x.quantile(pct_clip), x.quantile(1 - pct_clip)
    x = x.clip(lo, hi)
    sd = x.std()
    if not sd or np.isnan(sd):
        return pd.Series(0.0, index=s.index)
    return ((x - x.mean()) / sd).fillna(0.0)


def score_three_high(stats: pd.DataFrame, weights: dict | None = None) -> pd.DataFrame:
    """环节级三高评分（纯函数）。输入每环节一行聚合统计，输出含四支柱 z 分+总分+三高标签。"""
    w = {**PILLAR_WEIGHTS, **(weights or {})}
    out = stats.copy()
    out["growth_z"] = (winsor_z(stats["rev_yoy_med"]) + winsor_z(stats["profit_yoy_med"])) / 2**0.5
    out["margin_z"] = (winsor_z(stats["gross_margin_med"]) + winsor_z(stats["net_margin_med"])) / 2**0.5
    out["barrier_z"] = (winsor_z(stats["cust_top5_med"]) + winsor_z(stats["hhi_med"])) / 2**0.5
    out["choke_z"] = winsor_z(stats["downstream_breadth"]) - winsor_z(stats["supply_pressure"])
    out["total_z"] = (out["growth_z"] * w["growth"] + out["margin_z"] * w["margin"]
                      + out["barrier_z"] * w["barrier"] + out["choke_z"] * w["chokepoint"])

    def _flags(r: pd.Series) -> str:
        tags = [("高增长", r["growth_z"]), ("高利润", r["margin_z"]),
                ("高壁垒", r["barrier_z"]), ("咽喉", r["choke_z"])]
        return "+".join(t for t, z in tags if z >= FLAG_THRESHOLD) or "none"

    out["three_high_flags"] = out.apply(_flags, axis=1)
    out = out.sort_values("total_z", ascending=False).reset_index(drop=True)
    out["rank"] = range(1, len(out) + 1)
    return out


def make_candidate_id(sector: str) -> str:
    """候选 id：CAND-<md5_12>，对环节名稳定（重跑同环节不换 id，台账按批追加）。"""
    digest = hashlib.md5(f"E1D:{sector}".encode("utf-8")).hexdigest()[:12]
    return f"CAND-{digest}"


def build_hypothesis(r: pd.Series) -> str:
    """确定性假说文本（同一行输入必产出同一句，禁随机性）。"""
    d = float(r["downstream_breadth"])
    if d > 0:
        choke = f"图谱咽喉：产品供给 {d:.0f} 个下游环节、替代供给源 {float(r['supply_pressure']):.0f} 个"
    else:
        choke = "图谱咽喉：成员产品暂无供给网证据（不参与咽喉加分）"
    return (
        f"做多[{r['sector']}]环节（产业链三高共振候选：{r['three_high_flags']}）——"
        f"高增长：营收YoY中位 {r['rev_yoy_med']:.1f}%/净利YoY中位 {r['profit_yoy_med']:.1f}%；"
        f"高壁垒：前五客户集中 {r['cust_top5_med']:.1f}%/客户HHI {r['hhi_med']:.0f}；"
        f"高利润：毛利率 {r['gross_margin_med']:.1f}%/净利率 {r['net_margin_med']:.1f}%；"
        f"{choke}；成员 {r['members']:.0f} 只（财务覆盖 {r['fin_coverage']:.0%}）"
    )


def attach_birth_certificate(df: pd.DataFrame, batch_id: str) -> pd.DataFrame:
    """出生证三件套由代码机器写入（v9 防幻觉块：AI 禁手填溯源元数据）。"""
    out = df.copy()
    out["birth_channel"] = BIRTH_CHANNEL
    out["birth_batch"] = batch_id
    out["birth_source"] = BIRTH_SOURCE
    return out


def _latest_per_symbol(df: pd.DataFrame, key: str, value_cols: list[str]) -> pd.DataFrame:
    """每 symbol 取 key 列（announce_date/year）最新一行（PIT/最新口径）。"""
    d = df.dropna(subset=value_cols, how="all").sort_values(key).groupby("symbol").tail(1)
    return d[["symbol"] + value_cols]


def fetch_ch_financial_stats() -> pd.DataFrame:
    """CH c3_fundamental.financial_indicator：每股最新 announce 行的增长/利润四列。"""
    from zephyr.data.ch_writer import get_client_strict

    cli = get_client_strict()
    rows = cli.execute(_fin_sql())
    df = pd.DataFrame(rows, columns=["symbol", "announce_date", "rev_yoy", "profit_yoy",
                                     "gross_margin", "net_margin"])
    return _latest_per_symbol(df, "announce_date", ["rev_yoy", "profit_yoy", "gross_margin", "net_margin"])


def fetch_pg_sector_stats() -> pd.DataFrame:
    """PG ig_fact 三表聚合：环节成员 + 客户集中度壁垒 + supplies_to 咽喉度。"""
    from zephyr.governance.depgraph_schema import get_depgraph_pg_connection

    conn = get_depgraph_pg_connection(read_only=True)
    cur = conn.cursor()
    cur.execute(SQL_MEMBER)
    member = pd.DataFrame(cur.fetchall(), columns=["sector", "symbol", "n"])
    cur.execute(SQL_BARRIER)
    barrier = cur.fetchall()
    conn.close()
    bar_df = pd.DataFrame(barrier, columns=["symbol", "metric", "value"]).pivot_table(
        index="symbol", columns="metric", values="value", aggfunc="mean").reset_index()
    bar_df.columns.name = None
    return member.merge(bar_df, on="symbol", how="left")


def fetch_pg_chokepoint_stats() -> pd.DataFrame:
    """PG 供给网咽喉度：公司产品(produces)在 supplies_to 的下游广度与替代供给压力。"""
    from zephyr.governance.depgraph_schema import get_depgraph_pg_connection

    conn = get_depgraph_pg_connection(read_only=True)
    cur = conn.cursor()
    cur.execute(SQL_CHOKEPOINT)
    rows = cur.fetchall()
    conn.close()
    return pd.DataFrame(rows, columns=["symbol", "downstream_breadth", "supply_pressure"])


def aggregate_sector_stats(member: pd.DataFrame, fin: pd.DataFrame,
                           choke: pd.DataFrame, min_members: int = 5,
                           min_coverage: float = 0.6) -> pd.DataFrame:
    """环节聚合（纯函数）：成员财务中位数 + 壁垒中位数 + 咽喉度均值 + 覆盖过滤。"""
    m = member.merge(fin, on="symbol", how="left").merge(choke, on="symbol", how="left")
    for c in ("customer_top5_ratio", "customer_hhi"):
        if c not in m.columns:
            m[c] = np.nan  # 壁垒列缺失自愈（纯函数不依赖 IO 层拼装完整性）
    m["has_fin"] = m["rev_yoy"].notna() | m["gross_margin"].notna()

    def _med(g: pd.DataFrame, col: str) -> float:
        vals = g[col].dropna()
        return float(vals.median()) if len(vals) else float("nan")

    def _agg(g: pd.DataFrame) -> pd.Series:
        return pd.Series({
            "members": len(g),
            "fin_coverage": g["has_fin"].mean(),
            "rev_yoy_med": _med(g, "rev_yoy"),
            "profit_yoy_med": _med(g, "profit_yoy"),
            "gross_margin_med": _med(g, "gross_margin"),
            "net_margin_med": _med(g, "net_margin"),
            "cust_top5_med": _med(g, "customer_top5_ratio"),
            "hhi_med": _med(g, "customer_hhi"),
            "downstream_breadth": g["downstream_breadth"].dropna().mean(),
            "supply_pressure": g["supply_pressure"].dropna().mean(),
        })

    stats = m.groupby("sector").apply(_agg, include_groups=False).reset_index()
    stats = stats[(stats["members"] >= min_members) & (stats["fin_coverage"] >= min_coverage)]
    num = ["rev_yoy_med", "profit_yoy_med", "gross_margin_med", "net_margin_med",
           "cust_top5_med", "hhi_med", "downstream_breadth"]
    stats[num] = stats[num].fillna(0.0)
    stats["supply_pressure"] = stats["supply_pressure"].fillna(stats["downstream_breadth"])
    return stats


def run_screen(top_n: int = 20, min_members: int = 5, min_coverage: float = 0.6,
               dry_run: bool = False) -> dict:
    """主流程：三库聚合→评分→出生证→卸货 data/strategy_intake/（dry-run 只回看不写）。"""
    member = fetch_pg_sector_stats()
    fin = fetch_ch_financial_stats()
    choke = fetch_pg_chokepoint_stats()
    stats = aggregate_sector_stats(member, fin, choke, min_members, min_coverage)
    if stats.empty:
        raise RuntimeError("环节聚合结果为空——检查三库数据通道")
    scored = score_three_high(stats)
    batch_id = datetime.now(ZoneInfo("Asia/Shanghai")).strftime("E1D-%Y%m%d-%H%M%S")
    top = scored.head(top_n).copy()
    top["candidate_id"] = top["sector"].map(make_candidate_id)
    top["hypothesis_zh"] = top.apply(build_hypothesis, axis=1)
    top = attach_birth_certificate(top, batch_id)
    record = {
        "batch": batch_id, "screened_sectors": int(len(scored)),
        "returned": int(len(top)),
        "items": top[["candidate_id", "sector", "three_high_flags", "total_z",
                      "hypothesis_zh"]].to_dict("records"),
    }
    if not dry_run:
        cols = ["candidate_id", "sector", "members", "fin_coverage", "rev_yoy_med",
                "profit_yoy_med", "gross_margin_med", "net_margin_med", "cust_top5_med",
                "hhi_med", "downstream_breadth", "supply_pressure", "growth_z", "margin_z",
                "barrier_z", "choke_z", "total_z", "three_high_flags", "hypothesis_zh",
                "birth_channel", "birth_batch", "birth_source"]
        header = not _INTAKE_CSV.exists()
        _INTAKE_CSV.parent.mkdir(parents=True, exist_ok=True)
        top[cols].to_csv(_INTAKE_CSV, mode="a", header=header, index=False, encoding="utf-8-sig")
        record["written_to"] = str(_INTAKE_CSV.relative_to(_ROOT))
    return record


def main() -> int:
    ap = argparse.ArgumentParser(description="FAC-E1D 产业链三高筛选（ig_fact BOM 拆解，零 LLM）")
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("screen", help="三高筛选并卸货候选想法")
    s.add_argument("--top", type=int, default=20, help="取总分前 N 环节")
    s.add_argument("--min-members", type=int, default=5, help="环节最少成员股数")
    s.add_argument("--min-coverage", type=float, default=0.6, help="财务覆盖下限")
    s.add_argument("--dry-run", action="store_true", help="只回看不写台账")
    args = ap.parse_args()
    try:
        record = run_screen(args.top, args.min_members, args.min_coverage, args.dry_run)
    except RuntimeError as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(record, ensure_ascii=False, indent=1, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main())
