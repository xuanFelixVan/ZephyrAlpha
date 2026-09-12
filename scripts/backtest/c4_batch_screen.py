# [BLUEPRINT] MOD-BT-076 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] scripts.backtest.c4_batch_screen
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] zephyr.backtest.run_archive; zephyr.data.ch_writer; scripts.backtest.translated._c4_engine
# [CONSUMERS] c1_backtest.strategy_screen（C4 批次追加行）；C5 聚类/差异化
# [STARTUP] manual
# [MATURITY] experimental
# [INVARIANTS] 台账只增不改（C4 结果以新 screen_batch 追加，C2 原行零触碰）；
#   run 档案走 API（SCREEN kind：03/04/verdict 必选）；窗口 IS 2020-2023 冻结（ETF 族声明短窗）；
#   成本=冻结土规（引擎常量）；Deflated Sharpe 批内折减；幂等（同 batch+strategy_id 跳过）
# [MODIFY-GUARD] tests/backtest/test_c4_batch_smoke.py
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] RuntimeError(落库未确认/模块缺契约)
# [TESTS] tests/backtest/test_c4_batch_smoke.py
# [A_module] module_id=MOD-BT-076 | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""C4 快筛批测——translated/ 下 c4_*.py 全量批跑 + pilot 两件特载，成绩追加 strategy_screen。

模块契约（c4_*.py）: STRATEGY_ID / WINDOW_KIND / build(start, end)->(weights, closes)。
窗口: 股票/指数=2020-01-01..2023-12-31；ETF=2021-04-01 起（kline_etf_daily 覆盖声明）。
产出: run 档案 SCR-C4-<ts>（03 数据清单/04 批测汇总/verdict 判定书）+
  strategy_screen 追加行（verdict=translated_c4 / deferred_c4，附录挂起登记 CSV）。
用法: python scripts/backtest/c4_batch_screen.py [--limit N] [--dry-run]
"""

from __future__ import annotations

import argparse
import csv
import importlib.util
import json
import logging
import sys
import warnings
from datetime import datetime
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

warnings.filterwarnings("ignore", category=FutureWarning)

_ROOT = Path(__file__).resolve().parents[2]
_TRANSLATED_DIR = _ROOT / "scripts" / "backtest" / "translated"
_DEFERRAL_CSV = _ROOT / "data" / "strategy_intake" / "c4_deferrals.csv"
_TABLE = "c1_backtest.strategy_screen"
_BATCH = "C4-translated-20260912"
_INSERT_COLUMNS = (
    "(run_id, screen_batch, strategy_id, source_file, translated, is_sharpe, deflated_sharpe,"
    " max_drawdown, turnover, oos_years_decay, cluster_id, verdict, verdict_reason, screened_at, notes)"
)

# pilot 两件（C3 试点，同窗口已跑，特载回填；成绩出自其 run 档案/脚本输出）
_PILOTS: dict[str, dict[str, Any]] = {
    "CAND-b1ab42050d68": {"name": "pilot_002_ma_cross", "stats": {
        "sharpe": 1.08, "ann_return": 0.45, "max_drawdown": -0.45, "avg_turnover_1side": 0.099}},
    "CAND-097532e34002": {"name": "pilot_003_zscore_meanrev", "stats": {
        "sharpe": -0.06, "max_drawdown": None, "avg_turnover_1side": None}},
}


def _load_module(path: Path):
    spec = importlib.util.spec_from_file_location(f"c4dyn_{path.stem}", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"模块加载失败: {path.name}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    for attr in ("STRATEGY_ID", "WINDOW_KIND", "build"):
        if not hasattr(mod, attr):
            raise RuntimeError(f"模块缺契约字段 {attr}: {path.name}")
    return mod


def discover() -> list[Path]:
    return sorted(_TRANSLATED_DIR.glob("c4_*.py"))


def run_batch(limit: int | None, window: tuple[str, str] | None = None,
              include_pilots: bool = True) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    sys.path.insert(0, str(_TRANSLATED_DIR))
    from _c4_engine import batch_deflated_sharpe, daily_net_returns, run_backtest, window_for

    results: list[dict[str, Any]] = []
    failures: list[dict[str, Any]] = []
    mods = discover()
    if limit:
        mods = mods[:limit]
    for path in mods:
        try:
            mod = _load_module(path)
            start, end = window if window else window_for(mod.WINDOW_KIND)
            weights, closes = mod.build(start, end)
            stats = run_backtest(weights, closes)
            net = daily_net_returns(weights, closes)
            results.append({
                "strategy_id": mod.STRATEGY_ID, "module": path.name,
                "window_kind": mod.WINDOW_KIND, "window": [start, end],
                "stats": stats, "net": net, "days": int(len(net)),
            })
            logger.info("OK %s sharpe=%s", mod.STRATEGY_ID, stats["sharpe"])
        except Exception as exc:  # noqa: BLE001 单件失败不阻断批测
            failures.append({"module": path.name, "error": f"{type(exc).__name__}: {exc}"})
            logger.warning("FAIL %s: %s", path.name, exc)
    # pilot 特载（仅默认 IS 批；OOS 复测批不含——pilot OOS 另批补）
    pilots = _PILOTS.items() if include_pilots else ()
    for sid, meta in pilots:
        results.append({
            "strategy_id": sid, "module": meta["name"], "window_kind": "stock",
            "window": ["2020-01-01", "2023-12-31"], "stats": meta["stats"],
            "net": None, "days": 0, "pilot": True,
        })
    # Deflated Sharpe——官方件批内折减（SSOT：zephyr.backtest.regime_validation.c4_deflated_sharpe_runner）
    nets_main = {r["strategy_id"]: r["net"] for r in results
                 if r["net"] is not None and r["window_kind"] != "etf"}
    dsr_map = batch_deflated_sharpe(nets_main)
    for r in results:
        r["deflated_sharpe"] = dsr_map.get(r["strategy_id"]) if r["net"] is not None else None
    return results, failures


def load_deferrals() -> list[dict[str, str]]:
    if not _DEFERRAL_CSV.exists():
        logger.warning("挂起登记 CSV 缺失，跳过挂起行: %s", _DEFERRAL_CSV)
        return []
    with _DEFERRAL_CSV.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def _tsv_cell(v: Any) -> str:
    if v is None:
        return "\\N"
    return str(v).replace("\t", " ").replace("\r", " ").replace("\n", " ")


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    parser = argparse.ArgumentParser(description="C4 快筛批测（translated 全量+pilot 特载）")
    parser.add_argument("--limit", type=int, default=None, help="只跑前 N 个模块（冒烟用）")
    parser.add_argument("--dry-run", action="store_true", help="不落库不写档案，只打印汇总")
    parser.add_argument("--start", default=None, help="复测窗口起点（如 2024-01-01；给出即 OOS 复测批）")
    parser.add_argument("--end", default=None, help="复测窗口终点（如 2026-06-30）")
    parser.add_argument("--batch", default=_BATCH, help="落库批次标签（默认=冻结 IS 批）")
    parser.add_argument("--verdict", default="translated_c4", help="落库判定（OOS 批用 oos_tested）")
    args = parser.parse_args()
    oos_mode = bool(args.start and args.end)
    if oos_mode:
        args.batch = args.batch if args.batch != _BATCH else f"C4-OOS-{args.start[:4]}-{args.end[:4].replace('-', '')}"
        args.verdict = "oos_tested"

    results, failures = run_batch(args.limit, window=(args.start, args.end) if oos_mode else None,
                                  include_pilots=not oos_mode)
    if not results:
        raise RuntimeError("批测零结果（模块发现/加载全失败）")

    now = datetime.now()
    run_id = f"SCR-C4-{now.strftime('%Y%m%d-%H%M%S')}"
    sr_dist = [r["stats"]["sharpe"] for r in results]
    summary = {
        "total_modules": len(results) - len(_PILOTS),
        "pilots": len(_PILOTS),
        "failures": failures,
        "sharpe": {"min": min(sr_dist), "max": max(sr_dist),
                   "mean": round(sum(sr_dist) / len(sr_dist), 3)},
        "top5_by_sharpe": sorted(
            [{"strategy_id": r["strategy_id"], "sharpe": r["stats"]["sharpe"],
              "deflated_sharpe": r.get("deflated_sharpe")} for r in results],
            key=lambda x: -x["sharpe"])[:5],
    }

    # 挂起行
    deferrals = [] if oos_mode else load_deferrals()
    if not args.dry_run:
        from zephyr.backtest.run_archive import create_run, finalize_run, write_step

        create_run(
            run_id=run_id, object_id="", kind="SCREEN",
            window={"start": "2020-01-01", "end": "2023-12-31"},
            cost_mode="frozen_l0", created_by="ai-session:c4-batch-screen",
        )
        write_step(run_id, "03", (
            "# 数据清单\n\n- name: C4 批测行情\n"
            "  source: c1_market.kline_daily_hfq / kline_index / stk_limit / index_constituent\n"
            f"  window_is: 2020-01-01..2023-12-31（ETF 族 2021-04 起）\n"
            "  pit_note: '信号 T-1，T+1 收盘起算收益；成本=冻结土规(2.5bp+10bp+5bp)'\n  proxy: false\n"
        ))
        write_step(run_id, "04", json.dumps(summary, ensure_ascii=False, indent=1),
                   filename="c4_batch_summary.json")
        write_step(run_id, "verdict", (
            f"# 判定书：{run_id}\n\n对象：C4 快筛批测（策略入库线）｜ kind=SCREEN ｜ batch={_BATCH}\n"
            f"结论：verdict=done（批测完成 {len(results)} 行=translated_c4 + deferred_c4 挂起登记）｜ "
            "verdict_reason=c4_batch_screen_complete\n"
            "口径：IS 2020-2023 冻结窗口、冻结土规成本、Deflated Sharpe 批内折减；"
            "台账只增不改（追加新 batch 行，C2 原行零触碰）；无通过线（C5 差异化再甄别）\n"
            f"台账回执：strategy_screen screen_batch={_BATCH}\n"
        ))
        finalize_run(run_id, verdict_ref={"table": _TABLE, "run_id": run_id})

    # 落库（幂等：同 (batch, strategy_id) 跳过）
    from zephyr.data.ch_config import ensure_ch_env_loaded, load_ch_reader_config

    ensure_ch_env_loaded()
    cfg = load_ch_reader_config()
    from clickhouse_driver import Client

    c = Client(host=cfg["host"], port=int(cfg.get("port", 9000)), user=cfg.get("user", "default"),
               password=cfg.get("password", ""), connect_timeout=5)
    existing = {tuple(r) for r in c.execute(
        f"SELECT screen_batch, strategy_id FROM {_TABLE} WHERE screen_batch = '{_BATCH}'")}
    ts = now.strftime("%Y-%m-%d %H:%M:%S")
    rows: list[list[Any]] = []
    is_sharpe_map: dict[str, Any] = {}
    if oos_mode:
        for sid, isv in c.execute(
            f"SELECT strategy_id, is_sharpe FROM {_TABLE} "
            f"WHERE screen_batch = '{_BATCH}' AND verdict = 'translated_c4'"
        ):
            is_sharpe_map[sid] = isv
    for r in results:
        if (args.batch, r["strategy_id"]) in existing:
            continue
        decay = None
        if oos_mode:
            isv = is_sharpe_map.get(r["strategy_id"])
            oos_years = 2.5
            if isv:
                decay = round(min(1.0, max(0.0, (float(isv) - r["stats"]["sharpe"])
                           / max(abs(float(isv)), 1e-9) / oos_years)), 4)
        rows.append([
            run_id, args.batch, r["strategy_id"],
            f"scripts/backtest/translated/{r['module']}",
            1, r["stats"]["sharpe"], r.get("deflated_sharpe"),
            r["stats"].get("max_drawdown"), r["stats"].get("avg_turnover_1side"), decay, "",
            args.verdict, "c4_batch_screen", ts,
            f"window={'/'.join(r['window'])}; kind={r['window_kind']}"
            + (f"; is_sharpe_ref={is_sharpe_map.get(r['strategy_id'])}" if oos_mode else ""),
        ])
    for d in deferrals:
        sid = f"CAND-{d['md5_12']}"
        if (args.batch, sid) in existing:
            continue
        rows.append([
            run_id, args.batch, sid, d.get("orig_name", ""), 0, None, None, None, None, None, "",
            "deferred_c4", f"deferred_{d.get('defer_reason', 'unknown')}", ts,
            d.get("note", "")[:160],
        ])
    inserted = 0
    if rows and not args.dry_run:
        from zephyr.data import ch_writer

        tsv = "\n".join("\t".join(_tsv_cell(v) for v in r) for r in rows) + "\n"
        if not ch_writer.write_tsv(_TABLE, _INSERT_COLUMNS, tsv.encode("utf-8")):
            raise RuntimeError(f"strategy_screen 落库未确认（run_id={run_id}）——fail-closed")
        inserted = len(rows)
    print(json.dumps({
        "run_id": run_id, "results": len(results), "failures": len(failures),
        "deferral_rows": len(deferrals), "inserted": inserted,
        "dry_run": args.dry_run, "summary": summary,
    }, ensure_ascii=False, indent=1, default=str))


if __name__ == "__main__":
    sys.exit(main())
