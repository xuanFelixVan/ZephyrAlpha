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
  增量 IS 批:  … --auto-only            （只考 IS 台账没有的翻译件）
  自动 OOS 批: … --auto-oos-pending     （只考「IS 已落账 ∩ 无 oos_tested 行」，S06-G1）
  双窗编排:    IS 步骤加 --defer-emit，c4_batch_completed 由 OOS 步骤统一发（intake 依赖双窗行齐）
"""

from __future__ import annotations

import argparse
import csv
import importlib.util
import json
import logging
import sys
import warnings
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

warnings.filterwarnings("ignore", category=FutureWarning)

_ROOT = Path(__file__).resolve().parents[2]
_TRANSLATED_DIR = _ROOT / "scripts" / "backtest" / "translated"
_DEFERRAL_CSV = _ROOT / "data" / "strategy_intake" / "c4_deferrals.csv"
_TABLE = "c1_backtest.strategy_screen"
_BATCH = "C4-translated-20260912"


def _translated_dedup_key(batch: str, result: dict, verdict: str) -> tuple:
    """translated 行幂等键：同 sid 多版本翻译件按 source_file 区分各留一行（族取舍归 C5）。"""
    return (batch, result["strategy_id"], verdict, f"scripts/backtest/translated/{result['module']}")


def _deferred_dedup_key(batch: str, sid: str, orig_name: str) -> tuple:
    return (batch, sid, "deferred_c4", orig_name)


_INSERT_COLUMNS = (
    "(run_id, screen_batch, strategy_id, source_file, translated, is_sharpe, deflated_sharpe,"
    " max_drawdown, turnover, oos_years_decay, cluster_id, verdict, verdict_reason, screened_at,"
    " notes, num_trials)"
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
              include_pilots: bool = True, only: str | None = None) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    sys.path.insert(0, str(_TRANSLATED_DIR))
    from _c4_engine import batch_deflated_sharpe, daily_net_returns, run_backtest, window_for

    results: list[dict[str, Any]] = []
    failures: list[dict[str, Any]] = []
    mods = discover()
    if only:
        pats = [x.strip() for x in only.split(",") if x.strip()]
        mods = [m for m in mods if any(x in m.name for x in pats)]
        if not mods:
            raise RuntimeError(f"--only 过滤后零模块: {only}")
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


def _auto_only_names() -> list[str]:
    """--auto-only：discover() 中不在冻结 IS 批台账的翻译件（交接清单⑦ 执行体）。"""
    from zephyr.data.ch_writer import get_client_strict

    rows = get_client_strict().execute(
        f"SELECT DISTINCT source_file FROM {_TABLE} "
        f"WHERE screen_batch = '{_BATCH}' AND verdict = 'translated_c4'")
    known = {str(r[0]).replace("\\", "/").rsplit("/", 1)[-1] for r in rows}
    return sorted(p.name for p in discover() if p.name not in known)


def _oos_pending_names(
    is_rows: list[tuple[str, str]], oos_done: set[tuple[str, str]],
    discovered: list[str] | None = None,
) -> list[str]:
    """OOS 待测名单纯函数（S06-G1）：口径=「IS 批已落账(translated_c4) ∩ 尚无 oos_tested 行」。

    判重按 (strategy_id, source_file_basename) 对——兼容同 sid 多版本翻译件各需一次 OOS
    （bothwin 及格集按 (sid, source_file) 对接，screen_source.fetch_bothwin 同构）。
    再 ∩ discover() 现存件（IS 台账含 pilot 特载行/已删件，此处自然过滤，pilot OOS 另批补）。
    四象限：IS有+OOS无=考；IS有+OOS有=跳；IS无(无论OOS)=不归 OOS 批（IS 批先考）。
    """
    if discovered is None:
        discovered = [p.name for p in discover()]
    is_files = {
        str(sf).replace("\\", "/").rsplit("/", 1)[-1]
        for sid, sf in is_rows
        if (str(sid), str(sf).replace("\\", "/").rsplit("/", 1)[-1]) not in oos_done
    }
    return sorted(name for name in discovered if name in is_files)


def _oos_pending_names_from_db() -> list[str]:
    """DB 查询侧：IS 批 translated_c4 行 ∩ 全表 oos_tested 行的 (sid, 文件名) 对。"""
    from zephyr.data.ch_writer import get_client_strict

    c = get_client_strict()
    is_rows = [(str(sid), str(sf)) for sid, sf in c.execute(
        f"SELECT strategy_id, source_file FROM {_TABLE} "
        f"WHERE screen_batch = '{_BATCH}' AND verdict = 'translated_c4'")]
    oos_done = {
        (str(sid), str(sf).replace("\\", "/").rsplit("/", 1)[-1])
        for sid, sf in c.execute(
            f"SELECT DISTINCT strategy_id, source_file FROM {_TABLE} WHERE verdict = 'oos_tested'")
    }
    return _oos_pending_names(is_rows, oos_done)


def _default_oos_window(today: datetime | None = None) -> tuple[str, str]:
    """OOS 默认窗：起点=IS 冻结窗次日 2024-01-01；终点=最近一个周六（周考节奏对齐；
    当日无行情亦无害——日线按交易日取数）。"""
    d = (today or datetime.now()).date()
    offset = (d.weekday() - 5) % 7  # 距上个周六天数（周六=0）
    return "2024-01-01", (d - timedelta(days=offset)).strftime("%Y-%m-%d")


def _emit_pipeline_hook(run_id: str, batch: str, inserted: int) -> None:
    """落账成功→C6 管线事件（MOD-BT-190 写侧钩子；任何故障不反噬批测进程）。"""
    if inserted <= 0:
        return
    try:
        from zephyr.strategy_pipeline.pipeline_events import emit_c4_batch_completed
        out = emit_c4_batch_completed(batch=batch, run_id=run_id, inserted=inserted)
        logger.info("pipeline 钩子: %s", out.get("event"))
    except Exception as exc:  # noqa: BLE001——事件留 journal 能力已内置；这里兜 import 级故障
        logger.warning("pipeline 事件通知失败（不影响批测结果）: %s", exc)


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    parser = argparse.ArgumentParser(description="C4 快筛批测（translated 全量+pilot 特载）")
    parser.add_argument("--limit", type=int, default=None, help="只跑前 N 个模块（冒烟用）")
    parser.add_argument("--dry-run", action="store_true", help="不落库不写档案，只打印汇总")
    parser.add_argument("--start", default=None, help="复测窗口起点（如 2024-01-01；给出即 OOS 复测批）")
    parser.add_argument("--end", default=None, help="复测窗口终点（如 2026-06-30）")
    parser.add_argument("--batch", default=_BATCH, help="落库批次标签（默认=冻结 IS 批）")
    parser.add_argument("--verdict", default="translated_c4", help="落库判定（OOS 批用 oos_tested）")
    parser.add_argument("--only", default=None, help="模块名子串过滤（逗号分隔，如 rsrs,panic）")
    parser.add_argument("--auto-only", action="store_true",
                        help="自动发现未批测翻译件并只测它们（C6 管线交接清单⑦；零新件即退出）")
    parser.add_argument("--subset-batch", action="store_true",
                        help="子集补测批：跳过挂起行登记与 pilot 特载（二者已被冻结 IS 批承载，避免新批次重复登记）")
    parser.add_argument("--auto-oos-pending", action="store_true",
                        help="自动 OOS 复测批（S06-G1）：只测「IS 批已落账 ∩ 尚无 oos_tested 行」的策略，"
                             "零待测即退出；窗口缺省=2024-01-01..上个周六（--start/--end 可覆盖）")
    parser.add_argument("--defer-emit", action="store_true",
                        help="抑制 c4_batch_completed 事件（双窗编排：IS 步骤置位，由后续 OOS 步骤落账后统一 emit）")
    args = parser.parse_args()
    if args.auto_only:
        names = _auto_only_names()
        if not names:
            print(json.dumps({"auto_only": "zero_new_modules", "batch": _BATCH}, ensure_ascii=False))
            return
        args.only = ",".join(names)
        print(f"[AUTO-ONLY] {len(names)} 个未批测翻译件: {names[:5]}{' …' if len(names) > 5 else ''}")
    if args.auto_oos_pending:
        names = _oos_pending_names_from_db()
        if not names:
            print(json.dumps({"auto_oos_pending": "zero_pending", "batch": _BATCH}, ensure_ascii=False))
            return
        if not (args.start and args.end):
            args.start, args.end = _default_oos_window()
        args.only = ",".join(names)
        print(f"[AUTO-OOS-PENDING] {len(names)} 个待复测策略: {names[:5]}{' …' if len(names) > 5 else ''}"
              f" window={args.start}..{args.end}")
    oos_mode = bool(args.start and args.end)
    if oos_mode:
        args.batch = args.batch if args.batch != _BATCH else f"C4-OOS-{args.start[:4]}-{args.end[:4].replace('-', '')}"
        args.verdict = "oos_tested"

    # S3 知识生效日哨兵预检（备忘 96 批 3）：翻译件写成日晚于回测窗口起点=知识漂移，
    # D120 声明制——不阻断，但 verdict 必须打印并随 run 档案 summary 留证。
    win = (args.start, args.end) if oos_mode else ("2020-01-01", "2023-12-31")
    if str(_TRANSLATED_DIR) not in sys.path:
        sys.path.insert(0, str(_TRANSLATED_DIR))
    from _c4_engine import knowledge_drift_report

    s3_drift = knowledge_drift_report(win[0], win[1], root=_TRANSLATED_DIR)
    print(f"[S3] 知识生效日预检 verdict={s3_drift['verdict']} scanned={s3_drift['scanned']}"
          f" drift_count={s3_drift.get('drift_count', 0)} window={win[0]}..{win[1]}"
          + ("（声明制放行，详情见 run 档案 summary）" if s3_drift["verdict"] == "drift" else ""))

    results, failures = run_batch(args.limit, window=(args.start, args.end) if oos_mode else None,
                                  include_pilots=not (oos_mode or args.subset_batch), only=args.only)
    if not results:
        raise RuntimeError("批测零结果（模块发现/加载全失败）")

    now = datetime.now()
    run_id = f"SCR-C4-{now.strftime('%Y%m%d-%H%M%S')}"
    sr_dist = [r["stats"]["sharpe"] for r in results]
    # num_trials=本批实际参考策略数（批级属性，DSR 多重比较 N 口径；pilot 特载不计入）
    num_trials = len(results) - sum(1 for r in results if r.get("pilot"))
    summary = {
        "s3_knowledge_drift": s3_drift,
        "total_modules": num_trials,
        "pilots": sum(1 for r in results if r.get("pilot")),
        "num_trials": num_trials,
        "failures": failures,
        "sharpe": {"min": min(sr_dist), "max": max(sr_dist),
                   "mean": round(sum(sr_dist) / len(sr_dist), 3)},
        "top5_by_sharpe": sorted(
            [{"strategy_id": r["strategy_id"], "sharpe": r["stats"]["sharpe"],
              "deflated_sharpe": r.get("deflated_sharpe")} for r in results],
            key=lambda x: -x["sharpe"])[:5],
    }

    # 挂起行（子集补测批跳过：挂起清单已在冻结 IS 批全量登记，见 --subset-batch）
    deferrals = [] if (oos_mode or args.subset_batch) else load_deferrals()
    if not args.dry_run:
        from zephyr.backtest.run_archive import create_run, finalize_run, write_step

        create_run(
            run_id=run_id, object_id="", kind="SCREEN",
            window={"start": win[0], "end": win[1]},
            cost_mode="frozen_l0", created_by="ai-session:c4-batch-screen",
        )
        write_step(run_id, "03", (
            "# 数据清单\n\n- name: C4 批测行情\n"
            "  source: c1_market.kline_daily_hfq / kline_index / stk_limit / index_constituent\n"
            f"  window: {win[0]}..{win[1]}"
            + ("（OOS 复测窗）\n" if oos_mode else "（IS 冻结窗；ETF 族 2021-04 起）\n")
            + "  pit_note: '信号 T-1，T+1 收盘起算收益；成本=冻结土规(2.5bp+10bp+5bp)'\n  proxy: false\n"
        ))
        write_step(run_id, "04", json.dumps(summary, ensure_ascii=False, indent=1),
                   filename="c4_batch_summary.json")
        write_step(run_id, "verdict", (
            f"# 判定书：{run_id}\n\n对象：C4 快筛批测（策略入库线）｜ kind=SCREEN ｜ batch={args.batch}\n"
            f"结论：verdict=done（批测完成 {len(results)} 行，verdict={args.verdict}）｜ "
            "verdict_reason=c4_batch_screen_complete\n"
            f"口径：{'OOS 复测窗 ' if oos_mode else 'IS 2020-2023 冻结窗口'}{win[0]}..{win[1]}、"
            "冻结土规成本、Deflated Sharpe 批内折减；"
            "台账只增不改（追加新 batch 行，C2 原行零触碰）；无通过线（C5 差异化再甄别）\n"
            f"台账回执：strategy_screen screen_batch={args.batch}\n"
        ))
        finalize_run(run_id, verdict_ref={"table": _TABLE, "run_id": run_id})

    # 落库（幂等：同 (batch, strategy_id) 跳过）
    from zephyr.data.ch_writer import get_client_strict

    c = get_client_strict()
    # 幂等按 (batch, strategy_id, verdict) 判重：同 sid 的 deferred 行不挡 translated 行（2026-09-14 估值批教训）
    # 幂等按 (batch, strategy_id, verdict, source_file) 四键判重：deferred 行不挡 translated 行；
    # 同 sid 多版本翻译件（族变体重构）各留一行可溯，族内取舍归 C5 聚类去重（2026-09-14 裁定）
    existing = {tuple(r) for r in c.execute(
        f"SELECT screen_batch, strategy_id, verdict, source_file FROM {_TABLE} WHERE screen_batch = '{args.batch}'")}
    ts = now.strftime("%Y-%m-%d %H:%M:%S")
    rows: list[list[Any]] = []
    is_sharpe_map: dict[str, Any] = {}
    if oos_mode:
        for sid, isv in c.execute(
            f"SELECT strategy_id, is_sharpe FROM {_TABLE} "
            f"WHERE screen_batch = '{_BATCH}' AND verdict = 'translated_c4'"
        ):
            is_sharpe_map[sid] = isv
        # 子集补测批（--only/--subset-batch 产物）的 IS 参照不在冻结批——回退取该 sid
        # 最新 translated_c4 行（冻结批命中优先，setdefault 不覆盖；notes 的 is_sharpe_ref 留痕出处）
        for sid, isv in c.execute(
            f"SELECT strategy_id, argMax(is_sharpe, screened_at) FROM {_TABLE} "
            f"WHERE verdict = 'translated_c4' AND is_sharpe IS NOT NULL GROUP BY strategy_id"
        ):
            is_sharpe_map.setdefault(sid, isv)
    for r in results:
        if _translated_dedup_key(args.batch, r, args.verdict) in existing:
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
            num_trials,
        ])
    for d in deferrals:
        sid = f"CAND-{d['md5_12']}"
        if _deferred_dedup_key(args.batch, sid, d.get("orig_name", "")) in existing:
            continue
        rows.append([
            run_id, args.batch, sid, d.get("orig_name", ""), 0, None, None, None, None, None, "",
            "deferred_c4", f"deferred_{d.get('defer_reason', 'unknown')}", ts,
            d.get("note", "")[:160], num_trials,
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
    if not args.dry_run and not args.defer_emit:
        _emit_pipeline_hook(run_id, args.batch, inserted)


if __name__ == "__main__":
    sys.exit(main())
