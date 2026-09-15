# [BLUEPRINT] MOD-BT-154 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] scripts.backtest.factory_intake_pipeline
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] scripts.backtest.three_high_screen; scripts.backtest.lane_b_idea_generator; scripts.backtest.hypothesis_precheck; scripts.backtest.compute_window_gate
# [CONSUMERS] 策略生产全景图 FAC-E1 想法进货（编排层）；FAC-E2 预审（自动接续下游）；
#   Owner 夜批（单一命令跑"进货→预审→排产清单"）
# [STARTUP] manual
# [MATURITY] experimental
# [MODIFY-GUARD] none
# [INVARIANTS] 薄编排层（学讨论稿 v4 结论"自研薄调度层"）：只做函数级接续与汇总，
#   不复制各车道业务逻辑；事件语义=本命令被触发即一次进货事件，无常驻循环/定时器；
#   车道干完活即卸台账，E2 幂等消费新增候选；运动员不兼任裁判——编排层不评分；
#   重算力车道（未来 E1C）开工前必经 E0 问闸（MOD-BT-151），本编排接线点已在
#   _LANE_SPECS 声明
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] RuntimeError(车道函数缺位); SystemExit(1)(编排失败);
#   SystemExit(2)(参数错)
# [TESTS] tests/backtest/test_factory_intake_pipeline.py
# [A_module] module_id=MOD-BT-154 | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# noqa: m11-perm-manual-legitimate  手动 CLI 编排器非常驻服务：由夜批/会话进货事件触发，无常驻循环
"""FAC-E1 想法进货编排——车道并发进货→统一卸台账→E2 预审自动接续（一条命令）。

原理（图9 FAC-E1 节点 + 讨论稿 §二）：五车道并发进货，所有货统一卸到进货台账并带
出生证；E2 预审幂等消费新增候选，passed 清单即 E3 构造排产输入。本编排 = 车道函数
级接续（E1D 三高筛选 → E1B AI 生成（可选）→ E2 预审），产出夜批汇总。

用法:
  python scripts/backtest/factory_intake_pipeline.py run --top-sectors 20 --limit-precheck 10
  python scripts/backtest/factory_intake_pipeline.py run --with-lane-b --n-per-theme 2
  python scripts/backtest/factory_intake_pipeline.py run --dry-run
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))  # scripts.* 命名空间导入在 CLI 直跑场景（车道函数级接续）

# 车道规格表：进货函数 + 出生车道 + 算力档（重车道开工前必须 E0 问闸——接线点声明）
_LANE_SPECS = [
    {"lane": "D", "name": "e1d_three_high", "compute_class": "local",
     "intake": "data/strategy_intake/three_high_candidates.csv"},
    {"lane": "B", "name": "e1b_idea_gen", "compute_class": "api",
     "intake": "data/strategy_intake/lane_b_candidates.csv"},
    {"lane": None, "name": "e1c_formula_mine", "compute_class": "local_gpu",
     "intake": "待 E1C 施工（设计稿 docs/_working/2026-09-14-fac-e1c-formula-mining-design.md）"},
    # F-06 组合层网格（2.4 接线，2026-09-15）：intake=最新 grid 批次 manifest（执行器 MOD-BT-196 落盘）。
    # recipe 行非因子假说——E2 消费器需按 recipe_id/values_json 解析（跨线协作项，E2 侧适配器待挂）。
    {"lane": "F", "name": "f06_grid_recipes", "compute_class": "local",
     "intake": "data/strategy_intake/grid_latest_manifest.csv"},
]


def latest_grid_manifest() -> Path | None:
    """F 车道 intake 解析：返回最新 grid_<ts>/manifest.csv（无批次时 None，诚实缺）。"""
    base = _ROOT / "data" / "strategy_intake"
    runs = sorted(base.glob("grid_*/manifest.csv"))
    return runs[-1] if runs else None


def preflight_compute_gate(lane_specs: list[dict] | None = None) -> list[dict]:
    """E0 问闸预检（当前批只含轻车道 → 全放行；重车道登记在案自动受闸）。"""
    from scripts.backtest.compute_window_gate import check_gate

    specs = lane_specs if lane_specs is not None else _LANE_SPECS
    now = datetime.now(ZoneInfo("Asia/Shanghai"))
    results = []
    for spec in specs:
        if spec["lane"] is None:
            continue  # 未施工车道跳过
        decision = check_gate(f"intake_{spec['name']}", spec["compute_class"], now)
        results.append({"lane": spec["lane"], "purpose": f"intake_{spec['name']}",
                        "allowed": decision["allowed"],
                        "reason_code": decision["reason_code"]})
    return results


def run_pipeline(top_sectors: int = 20, with_lane_b: bool = False,
                 n_per_theme: int = 2, limit_precheck: int | None = 10,
                 dry_run: bool = False) -> dict:
    """主编排：E1D 进货 →（可选）E1B 进货 → E2 预审 → 排产汇总。"""
    started = datetime.now(ZoneInfo("Asia/Shanghai")).isoformat(timespec="seconds")
    gates = preflight_compute_gate()

    from scripts.backtest import hypothesis_precheck, lane_b_idea_generator, three_high_screen

    report: dict = {"started_at": started, "compute_gates": gates, "lanes": {}}

    # 1) 车道 D：三高筛选（零 LLM，本地轻）
    e1d = three_high_screen.run_screen(top_n=top_sectors, dry_run=dry_run)
    report["lanes"]["D_three_high"] = {
        "batch": e1d.get("batch"), "candidates": e1d.get("returned"),
        "intake": three_high_screen._INTAKE_CSV.name}

    # 2) 车道 B：AI 生成（可选，本地 LLM 轻）
    if with_lane_b:
        e1b = lane_b_idea_generator.run_generation(
            themes=list(lane_b_idea_generator.SEED_THEMES), n_per_theme=n_per_theme,
            dry_run=dry_run)
        report["lanes"]["B_idea_gen"] = {
            "batch": e1b.get("batch"), "candidates": e1b.get("generated"),
            "failed_themes": e1b.get("failed_themes"),
            "intake": lane_b_idea_generator._INTAKE_CSV.name}

    # 3) E2 预审：幂等消费全部车道台账新增候选（四车道常态化）
    e2_funnel: dict = {"batch": None, "prechecked": 0, "passed": 0,
                       "rejected": 0, "deferred": 0}
    passed_ids: list[str] = []
    intake_sources = {
        "D": three_high_screen._INTAKE_CSV,
        "B": lane_b_idea_generator._INTAKE_CSV,
    }
    try:
        from scripts.backtest import lane_c_formula_miner, lane_c2_agentic_miner
        intake_sources["C"] = lane_c_formula_miner._INTAKE_CSV
        intake_sources["C2"] = lane_c2_agentic_miner._INTAKE_CSV
    except Exception:  # noqa: BLE001 — 车道模块缺位不阻断其余车道
        pass
    for lane, src in intake_sources.items():
        if not Path(src).exists():
            continue
        e2 = hypothesis_precheck.run(source=str(src), limit=limit_precheck,
                                     dry_run=dry_run)
        if e2.get("batch") is None:
            continue  # 该台账无新增候选（幂等跳过）
        for k in ("prechecked", "passed", "rejected", "deferred"):
            e2_funnel[k] += e2.get(k) or 0
        passed_ids += [i["candidate_id"] for i in e2.get("items", [])
                       if i["verdict"] == hypothesis_precheck.VERDICT_PASS]
        report["lanes"][f"E2_{lane}"] = {
            "batch": e2.get("batch"), "prechecked": e2.get("prechecked"),
            "passed": e2.get("passed"), "rejected": e2.get("rejected"),
            "deferred": e2.get("deferred")}
    report["e2_precheck"] = {**e2_funnel, "e3_ready_candidates": sorted(set(passed_ids))}
    report["finished_at"] = datetime.now(ZoneInfo("Asia/Shanghai")).isoformat(timespec="seconds")
    return report


_MANIFEST_CSV = _ROOT / "data" / "strategy_intake" / "constructed_manifest.csv"
_CONSTRUCT_LANES = ("C", "C2")  # 公式轨：表达式可直接机械翻译成考卷件


def auto_construct(lanes: tuple[str, ...] = _CONSTRUCT_LANES,
                   register_tokens: bool = True, dry_run: bool = False) -> dict:
    """E2→E3 排产自动流转：过审公式候选 → E4 考卷件（机械翻译桥）+ 台账清单。

    只处理公式轨（C/C2——台账含 expression 列）；假说轨（D/B）走 C3 翻译专项
    （MOD-BT-190 hypothesis_translator）。幂等：manifest 已登记的候选跳过。
    """
    import pandas as pd

    manifest_cols = ["candidate_id", "birth_channel", "strategy_id", "exam_file",
                     "constructed_at"]
    done: set[str] = set()
    if _MANIFEST_CSV.exists():
        try:
            done = set(pd.read_csv(_MANIFEST_CSV, encoding="utf-8-sig")["candidate_id"])
        except Exception:  # noqa: BLE001 — 清单损坏重建
            done = set()

    from scripts.backtest.factor_strategy_template import generate_strategy_file
    from scripts.backtest.lane_c2_agentic_miner import (
        OP_ARITY,
        validate_expr,
    )
    from scripts.backtest.lane_c_formula_miner import FEATURES

    passed = _e2_passed_by_channel()
    report: dict = {"constructed": [], "skipped_no_expr": [], "skipped_invalid": [],
                    "skipped_done": [], "dry_run": dry_run}
    for lane in lanes:
        src = _ROOT / "data" / "strategy_intake" / {
            "C": "lane_c_candidates.csv", "C2": "lane_c2_candidates.csv"}[lane]
        if not src.exists():
            continue
        df = pd.read_csv(src, encoding="utf-8-sig")
        expr_col = "expression" if "expression" in df.columns else "formula"
        for _, row in df.iterrows():
            cid = str(row["candidate_id"])
            if cid not in passed:
                continue  # 只构造 E2 过审者
            if cid in done:
                report["skipped_done"].append(cid)
                continue
            expr = str(row.get(expr_col, "")).strip()
            if not expr:
                report["skipped_no_expr"].append(cid)
                continue
            ok, why = validate_expr(expr, list(FEATURES), set(OP_ARITY))
            if not ok:
                report["skipped_invalid"].append(f"{cid}:{why[:40]}")
                continue
            if dry_run:
                report["constructed"].append({"candidate_id": cid, "dry": True})
                continue
            out = generate_strategy_file(expr, src_cand=cid)
            if register_tokens:
                import subprocess
                subprocess.run([sys.executable,
                                str(_ROOT / "scripts" / "governance" / "d3_metadata"
                                    / "batch_creation_tokens.py"),
                                "--prefix", str(out.relative_to(_ROOT)),
                                "--created-by", os.environ.get("ZEPHYR_SESSION_ID") or "factory_intake_pipeline(auto)",
                                "--capability", "factory_backend"],
                               capture_output=True)
            rec = {"candidate_id": cid, "birth_channel": lane,
                   "strategy_id": f"FACT-{cid.split('-')[1][:8]}",
                   "exam_file": str(out.relative_to(_ROOT)),
                   "constructed_at": datetime.now(
                       ZoneInfo("Asia/Shanghai")).isoformat(timespec="seconds")}
            report["constructed"].append(rec)
            pd.DataFrame([rec])[manifest_cols].to_csv(
                _MANIFEST_CSV, mode="a", header=not _MANIFEST_CSV.exists(),
                index=False, encoding="utf-8-sig")
            done.add(cid)
    report["total_constructed"] = len(report["constructed"])
    return report


def _e2_passed_by_channel() -> set[str]:
    """E2 台账过审候选 id 集（全通道；台账不可达=空集→无构造）。"""
    try:
        from zephyr.data.ch_config import ensure_ch_env_loaded, load_ch_reader_config
        from clickhouse_driver import Client
        from schemas.categories.backtest.backtest_hypothesis_precheck import (
            DATABASE,
            TABLE_NAME,
        )

        ensure_ch_env_loaded()
        cfg = load_ch_reader_config()
        cli = Client(host=cfg["host"], port=int(cfg.get("port", 9000)),
                     user=cfg.get("user", "default"), password=cfg.get("password", ""),
                     connect_timeout=5)
        rows = cli.execute(
            f"SELECT candidate_id FROM {DATABASE}.{TABLE_NAME} "
            f"WHERE verdict = 'precheck_passed'")
        return {r[0] for r in rows}
    except Exception:  # noqa: BLE001 — 台账不可达 fail-closed（不构造）
        return set()


def race_scoreboard(ledger_rows: list[dict], ledger_counts: dict[str, int]) -> dict:
    """P2 赛马计分板（纯函数）：按出生车道聚合预审漏斗。

    两轨同卷同及格线（宪法铁律：运动员不兼任裁判）——本计分板只汇总 E2 层漏斗；
    E4 层赛马待首批候选进入考试后自动可比（同一判定权）。
    """
    out: dict = {}
    for lane, total in ledger_counts.items():
        rows = [r for r in ledger_rows if r.get("birth_channel") == lane]
        passed = sum(1 for r in rows if r.get("verdict") == "precheck_passed")
        rejected = sum(1 for r in rows if r.get("verdict") == "precheck_rejected")
        deferred = sum(1 for r in rows if r.get("verdict") == "precheck_deferred")
        out[lane] = {
            "ledger_candidates": total, "prechecked": len(rows),
            "passed": passed, "rejected": rejected, "deferred": deferred,
            "pass_rate": round(passed / len(rows), 4) if rows else None,
        }
    return out


def cmd_race() -> int:
    """赛马计分板 CLI：各车道台账存量 + E2 预审漏斗按 birth_channel 聚合。"""
    import pandas as pd

    from scripts.backtest import hypothesis_precheck

    intakes = {
        "D": _ROOT / "data" / "strategy_intake" / "three_high_candidates.csv",
        "B": _ROOT / "data" / "strategy_intake" / "lane_b_candidates.csv",
        "C": _ROOT / "data" / "strategy_intake" / "lane_c_candidates.csv",
        "C2": _ROOT / "data" / "strategy_intake" / "lane_c2_candidates.csv",
    }
    counts = {lane: (len(pd.read_csv(p, encoding="utf-8-sig")) if p.exists() else 0)
              for lane, p in intakes.items()}
    try:
        from zephyr.data.ch_config import ensure_ch_env_loaded, load_ch_reader_config
        from clickhouse_driver import Client

        ensure_ch_env_loaded()
        cfg = load_ch_reader_config()
        cli = Client(host=cfg["host"], port=int(cfg.get("port", 9000)),
                     user=cfg.get("user", "default"), password=cfg.get("password", ""),
                     connect_timeout=5)
        rows = [{"birth_channel": r[0], "verdict": r[1]} for r in cli.execute(
            f"SELECT birth_channel, verdict FROM {hypothesis_precheck._table()}")]
    except Exception as exc:  # noqa: BLE001 — 台账不可达时降级为纯台账计数
        rows = []
        print(f"WARN: E2 台账不可达（{exc}），仅台账计数", file=sys.stderr)
    print(json.dumps({"race": race_scoreboard(rows, counts)}, ensure_ascii=False,
                     indent=1))
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="FAC-E1 进货编排（车道→卸货→E2 预审一条命令）")
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run", help="跑一次进货事件")
    r.add_argument("--top-sectors", type=int, default=20, help="E1D 取三高总分前 N 环节")
    r.add_argument("--with-lane-b", action="store_true", help="附带车道 B AI 生成")
    r.add_argument("--n-per-theme", type=int, default=2, help="E1B 每主题生成条数")
    r.add_argument("--limit-precheck", type=int, default=10, help="E2 本批最多预审条数")
    r.add_argument("--dry-run", action="store_true", help="全链只看不写")
    sub.add_parser("race", help="P2 赛马计分板（各车道×E2 预审漏斗）")
    c = sub.add_parser("construct", help="E2→E3 排产流转：过审公式候选自动生成考卷件")
    c.add_argument("--lanes", default="C,C2", help="公式轨车道（缺省 C,C2）")
    c.add_argument("--no-register-tokens", action="store_true")
    c.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    if args.cmd == "race":
        return cmd_race()
    if args.cmd == "construct":
        lanes = tuple(x.strip() for x in args.lanes.split(",") if x.strip())
        rep = auto_construct(lanes=lanes, register_tokens=not args.no_register_tokens,
                             dry_run=args.dry_run)
        print(json.dumps(rep, ensure_ascii=False, indent=1))
        return 0
    try:
        report = run_pipeline(args.top_sectors, args.with_lane_b, args.n_per_theme,
                              args.limit_precheck, args.dry_run)
    except RuntimeError as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(report, ensure_ascii=False, indent=1, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main())
