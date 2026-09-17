# [BLUEPRINT] MOD-BT-159 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] scripts.backtest.factor_strategy_template
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] numpy; pandas; zephyr.data.ch_config; zephyr.data.table_registry; scripts.backtest.lane_c_formula_miner
# [CONSUMERS] 策略生产全景图 FAC-E3→E4 公式轨桥（因子表达式→E4 考卷件）；
#   scripts/backtest/translated/c4_fact_*.py（本模块生成的考卷件）；C4 快筛批测
# [STARTUP] manual
# [MATURITY] experimental
# [MODIFY-GUARD] none
# [INVARIANTS] 生成的考卷件=纯模板填空（表达式/ID/参数为唯一自由度），build() 逻辑由
#   本模块 build_factor_weights 统一承载（真源唯一，生成件零逻辑）；PIT=特征全部 ≤T
#   可得+T+1 收盘执行（引擎侧冻结土规）；因子方向=incr_ic>0 验收已定多头正向；
#   生成的考卷件入 translated/ 前必须过 creation_token 登记+编译自检
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] RuntimeError(表达式非法/数据缺失); ValueError(参数非法)
# [TESTS] tests/backtest/test_factor_strategy_template.py
# [A_module] module_id=MOD-BT-159 | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# noqa: m11-perm-manual-legitimate  手动 CLI 生成器非常驻服务：由 E3 构造排产事件调用，无常驻循环
"""FAC-E3→E4 公式轨桥——白名单 DSL 因子表达式 → E4 考卷件（c4_fact_*.py）生成器。

背景：E2 幸存的公式候选与 E4 考卷（c4_batch_screen 只收 translated/c4_*.py 的
build(s,e)→(weights,closes) 契约）之间缺翻译件。本模块=机械翻译桥：表达式是唯一
自由度，build() 逻辑统一由 build_factor_weights 承载（生成件零逻辑、零漂移）。

策略语义：因子值截面排名 → top_n 等权多头（因子方向由增量 IC>0 验收锁正向），
日频收盘再平衡（引擎侧 T+1 执行+冻结成本）。

用法:
  python scripts/backtest/factor_strategy_template.py generate \
      --expr "ts_zscore_20(ret_5d)" --src-cand CAND-xxxx [--top-n 20]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))  # scripts.* 命名空间导入（CLI 直跑/生成件双场景）
_TRANSLATED_DIR = _ROOT / "scripts" / "backtest" / "translated"
LOOKBACK_DAYS = 140  # 特征预热（vol_20d/close_ma20/ret_20d 需 ≥20 交易日+余量）

TEMPLATE = '''# [BLUEPRINT] MOD-BT-159 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] scripts.backtest.translated.{module_name}
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] scripts.backtest.factor_strategy_template
# [CONSUMERS] C4 快筛批测（E4 考卷件·公式轨桥生成）
# [STARTUP] manual
# [MATURITY] experimental
# [MODIFY-GUARD] schema-change
# [INVARIANTS] 模板生成件零逻辑（build 统一由 factor_strategy_template 承载）；
#   表达式={expr}；PIT+冻结土规由引擎保证；出生候选={src_cand}
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] RuntimeError(数据缺失)
# [TESTS] tests/backtest/test_factor_strategy_template.py
# [A_module] module_id=MOD-BT-159 | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""公式轨考卷件：{expr}

生成=factor_strategy_template（MOD-BT-159 机械翻译桥）；出生候选={src_cand}；
因子方向=多头正向（增量 IC>0 验收锁定）。
[KNOWLEDGE_EFFECTIVE_FROM] {knowledge_date} | 源=公式轨生成件（表达式生成即生效日） | 生成=MOD-BT-159
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))          # _c4_engine 同目录
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))  # 仓库根（scripts.*）

STRATEGY_ID = "{strategy_id}"
WINDOW_KIND = "stock"

EXPR = {expr!r}
TOP_N = {top_n}


def build(s, e):
    from scripts.backtest.factor_strategy_template import build_factor_weights

    return build_factor_weights(s, e, EXPR, top_n=TOP_N)


def main():
    import json
    import logging

    logging.basicConfig(level=logging.INFO)
    from _c4_engine import C4_END, C4_START, emit, run_backtest

    w, c = build(C4_START, C4_END)
    print(json.dumps(emit(STRATEGY_ID, run_backtest(w, c),
        ["D1 HS300口径见面板", "D2 T+1收盘", "D3 公式因子多头正向", "D4 生成件=MOD-BT-159",
         "D5 引擎=MOD-BT-039"]),
        ensure_ascii=False))


if __name__ == "__main__":
    main()
'''


def strategy_id_for(expr: str, src_cand: str = "") -> str:
    """考卷 STRATEGY_ID：FACT-<md5_8>（表达式内容寻址，跨轨可溯源）。"""
    basis = f"{src_cand}:{expr.strip()}"
    return "FACT-" + hashlib.md5(basis.encode("utf-8")).hexdigest()[:8]


def build_factor_weights(s, e, expr: str, top_n: int = 20,
                         universe_n: int = 40, lookback_days: int = LOOKBACK_DAYS):
    """因子→权重（考卷 build 统一承载）：面板求值→截面排名→top_n 等权多头。"""
    from scripts.backtest.lane_c_formula_miner import FEATURES, compute_features
    from scripts.backtest.lane_c2_agentic_miner import (
        OP_ARITY,
        build_eval_ops,
        evaluate_expr,
        validate_expr,
    )
    from zephyr.data.ch_config import ensure_ch_env_loaded, load_ch_reader_config
    from zephyr.data.table_registry import get_registry
    from clickhouse_driver import Client

    ok, why = validate_expr(expr, list(FEATURES), set(OP_ARITY))
    if not ok:
        raise RuntimeError(f"表达式非法: {why}")

    ensure_ch_env_loaded()
    cfg = load_ch_reader_config()
    cli = Client(host=cfg["host"], port=int(cfg.get("port", 9000)),
                 user=cfg.get("user", "default"), password=cfg.get("password", ""),
                 connect_timeout=5)
    import datetime as _dt

    s_d = s if isinstance(s, _dt.date) else _dt.date.fromisoformat(str(s)[:10])
    e_d = e if isinstance(e, _dt.date) else _dt.date.fromisoformat(str(e)[:10])
    start = (s_d - _dt.timedelta(days=int(lookback_days * 1.7))).isoformat()
    k = pd.DataFrame(cli.execute(
        "SELECT trade_date AS date, symbol_canonical AS s, close, turnover, amount "
        "FROM {t} WHERE trade_date >= %(start)s AND trade_date <= %(end)s "
        "AND symbol_canonical IN %(syms)s".format(
            t=get_registry().table("market_kline_daily_hfq")),
        {"start": start, "end": e_d.isoformat(), "syms": tuple(universe_syms(cli, start, universe_n))}),
        columns=["date", "s", "close", "turnover", "amount"])
    for c in ("close", "turnover", "amount"):
        k[c] = pd.to_numeric(k[c], errors="coerce")
    k = k.sort_values(["s", "date"])
    k = _dedup_kline_rows(k)
    feats = compute_features(k)
    feats["close"] = k["close"].values  # 考卷件需要 close 透视（assemble_weights）
    feats = feats.dropna(subset=list(FEATURES))
    feats = feats[(feats["date"] >= s_d) & (feats["date"] <= e_d)]
    if feats.empty:
        raise RuntimeError("考卷窗口内无有效特征行")
    date_codes = pd.factorize(feats["date"])[0]
    symbol_codes = pd.factorize(feats["s"])[0]
    ops = build_eval_ops(date_codes, symbol_codes)
    vals = evaluate_expr(expr, list(FEATURES), ops, feats[list(FEATURES)].to_numpy(float))

    feats = feats.assign(factor=vals)
    return assemble_weights(feats, top_n)


def _dedup_kline_rows(k: pd.DataFrame) -> pd.DataFrame:
    """同 (symbol, trade_date) 重复行保留最后一条——上游双写防御（2026-09-11 实例 5206 对），pivot 前必去重。"""
    return k.drop_duplicates(subset=["s", "date"], keep="last")


def assemble_weights(feats: pd.DataFrame, top_n: int) -> tuple[pd.DataFrame, pd.DataFrame]:
    """因子值→top_n 等权多头宽表（纯函数）：closes 同源透视，供引擎 T+1 执行。

    PIT 修复（S14-3，2026-09-17 kimi-audit 班次）：d 日截面选出的权重必须落在 d+1 行
    （weights[d+1]=selection(factor[d])），引擎 shift(1) 后才符合模块自述"T 日信号用
    ≤T-1 数据，T+1 收盘起算收益"。旧码无此平移=看着 d 收盘按 d 收盘成交（同 bar 前视，
    探针 tests/backtest/test_b1_fact_assemble_samebar_probe.py 实锤）。
    """
    closes = feats.pivot(index="date", columns="s", values="close").sort_index()
    weights = pd.DataFrame(index=closes.index, columns=closes.columns, dtype=float)
    for d, grp in feats.groupby("date"):
        day = grp.dropna(subset=["factor"]).nlargest(top_n, "factor")["s"]
        if day.empty:
            continue
        weights.loc[d, day] = 1.0 / len(day)
    weights = weights.shift(1)  # ≤T-1 平移：d 行权重只含 d-1 及之前的因子截面
    return weights.fillna(0.0), closes


def compute_features_importable() -> bool:
    """单一真源锚：特征工程必须来自 MOD-BT-155（防漂移）。"""
    from scripts.backtest.lane_c_formula_miner import compute_features, FEATURES

    return callable(compute_features) and len(FEATURES) == 7


def universe_syms(cli, start: str, n: int) -> tuple:
    """考卷 universe=成交额 top N（PIT 修复：改为 start 之前 365 自然日的滚动窗均值——
    旧码用全窗均值，未来才流动的股票被回灌选入历史期=前视/幸存者偏差，S14-3 同案）。"""
    from zephyr.data.table_registry import get_registry

    rows = cli.execute(
        "SELECT symbol_canonical FROM (SELECT symbol_canonical, avg(amount) AS a "
        "FROM {t} WHERE trade_date >= toDate(%(start)s) - 365 AND trade_date < %(start)s "
        "GROUP BY 1 ORDER BY a DESC LIMIT %(n)s)".format(
            t=get_registry().table("market_kline_daily_hfq")),
        {"start": start, "n": n})
    return tuple(r[0] for r in rows)


def generate_strategy_file(expr: str, src_cand: str = "", top_n: int = 20,
                           out_path: Path | None = None,
                           knowledge_date: str = "") -> Path:
    """生成考卷件（模板填空；文件名 c4_fact_<md5_8>.py）。

    knowledge_date=知识生效日哨兵（S3 漂移预检依据；缺省=当日=表达式进仓日，
    机器生成件无更早知识时点，如实声明）。
    """
    sid = strategy_id_for(expr, src_cand)
    module_name = "c4_fact_" + sid.split("-", 1)[1].lower()
    content = TEMPLATE.format(module_name=module_name, strategy_id=sid, expr=expr,
                              top_n=top_n, src_cand=src_cand or "未登记",
                              knowledge_date=knowledge_date or date.today().isoformat())
    compile(content, f"{module_name}.py", "exec")  # 生成即编译自检
    out = out_path or (_TRANSLATED_DIR / f"{module_name}.py")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(content, encoding="utf-8", newline="\n")
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description="FAC-E3→E4 公式轨桥：因子表达式→E4 考卷件")
    sub = ap.add_subparsers(dest="cmd", required=True)
    g = sub.add_parser("generate", help="生成考卷件")
    g.add_argument("--expr", required=True, help="白名单 DSL 因子表达式")
    g.add_argument("--src-cand", default="", help="出生候选 id（溯源）")
    g.add_argument("--top-n", type=int, default=20)
    g.add_argument("--out", default=None, help="输出路径（缺省 translated/c4_fact_*.py）")
    args = ap.parse_args()
    try:
        out = generate_strategy_file(args.expr, args.src_cand, args.top_n,
                                     Path(args.out) if args.out else None)
    except (RuntimeError, ValueError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1
    print(json.dumps({"written": str(out), "strategy_id": strategy_id_for(
        args.expr, args.src_cand)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
