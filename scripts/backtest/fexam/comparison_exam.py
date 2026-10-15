# [BLUEPRINT] MOD-BT-CAPEXAM | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] scripts.backtest.fexam.comparison_exam
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] numpy; pandas; yaml; scripts/backtest/fexam/calibration_exam;
#   scripts/backtest/fexam/card_binding; zephyr/backtest/core/n_trial_ledger(经 run_card)
# [CONSUMERS] OD-1 生产线对照/消融考试车道（人工 CLI --card 逐卡开考）；绑定册 02_binding_book.yaml 已批 arms 格；
#   W5 writeback_exam_confidence（分数册消费方上游，经 exam_scores_v1.yaml）
# [STARTUP] manual
# [MATURITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [INVARIANTS] OD-1（Owner 已批，05_owner_decisions.yaml:11）：对照/消融族执行器缺位=98 卡零可考面。
#   本件是族驱动器，判据面零新写：判分/出分/翻卡全经 calibration_exam.run_card（pillars_route 按卡面
#   冻结键集分派，一票否决；分数册 only-add；双文档 register 兼容；卡翻 examined；试次入 n_trial_ledger）。
#   族闸：只考 family∈{comparison,ablation}（两族卡 schema 同构，同文件支持；其余族归各自执行器，误入即拒）。
#   双腿装载梯子（每级都是既有在册装载口，零新取数路径）：R1 注入（CLI csv/kwargs，与 calibration_exam
#   main 同契约，测试零 CH）→ R2 绑定册 arms 格（card_binding.run_one 双臂通道原函数装配：
#   ARM_BASE_SOURCES 底座 + arms_from_binding_book + arm_context_for_judge + 反挪门柱自闸）→
#   R3 绑定册单信号格（series 路由卡冠军腿，run_binding_book）。
#   fail-closed：任一腿装载不出 → verdict=blocked 行如实入分数册（带 route/binding_class/拒因），
#   禁编造指标；blocked 不翻卡（examined=已出分）、不记试次（零数据消费=零试验，DSR 分母不虚增）。
#   分数册追加与 run_card 同一双文档 safe_load_all 形态（取含 rows 的 doc 写回保结构，裁定#536）；
#   本件绝不改判据数值/门柱/冻结值（G4-5：事后挪门柱=作废）。
# [MODIFY-GUARD] tests/backtest/test_comparison_exam.py
# [STABILITY] experimental
# [ERROR_CONTRACT] RuntimeError(经 _ToolError): 卡不可解析/缺 card_id/族外卡误入/状态非 preregistered
#   （重考带 --force）/--family 与卡面不符；blocked 行: 双腿装载不出（machine reason 随行）
# [TESTS] tests/backtest/test_comparison_exam.py
# [A_module] module_id=MOD-BT-CAPEXAM | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# [not-trading: 回测研究面工具（对照/消融考试卡族驱动器），不在实盘交易决策路径上]
"""对照/消融卡考试执行器（OD-1）——族闸 + 双腿装载 + blocked fail-closed → 复用校准执行核出分。

净零声明（宪法 §4.1）：本件不替代任何在册件——calibration_exam（判分核）与 card_binding（绑定层）
职能原样保留；本件合并的是"对照/消融族单卡驱动入口 + blocked 出分面"这一缺口，使 98 张族卡
从"零可考面"变为"可考/可 blocked 分诊"，并替代此后各战役本会再写的一次性族驱动器。

两族同构：comparison 与 ablation 卡同 schema（arms/buckets/pillars/pillars_numeric/data_binding），
判官按 pillars_route 的键集路由（族面无关，统筹 03:3x 裁定①），故同文件支持两族。
分数行沿用 run_card 单行含双腿指标面（metrics.arm_open/arm_base/配对差），另加 verdict=blocked 形态。
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date as _date
from pathlib import Path

import yaml

from zephyr.shared.io.paths import REPO_ROOT

sys.path.insert(0, str(REPO_ROOT / "scripts" / "backtest"))

try:  # 导入次序＝先包内相对再包名绝对（同 calibration_exam._declared_local_faces 的在册教训：
    # 两个包名各导一次＝模块对象分裂；本件统一先相对，跑批侧 sys.path 只挂 scripts/backtest 时退绝对）
    from . import card_binding as _cb
    from .calibration_exam import (
        _CALIBRATION_JUDGED_KEYS,
        _EVENT_KNOWN_KEYS,
        _UNION_PILLAR_KEYS,
        _ToolError,
        _unjudged_pillars,
        pillars_route,
        run_card,
    )
except ImportError:  # noqa: F811 — 跑批侧（sys.path=scripts/backtest）走这条
    from fexam import card_binding as _cb  # type: ignore[no-redef]
    from fexam.calibration_exam import (  # type: ignore[no-redef]
        _CALIBRATION_JUDGED_KEYS,
        _EVENT_KNOWN_KEYS,
        _UNION_PILLAR_KEYS,
        _ToolError,
        _unjudged_pillars,
        pillars_route,
        run_card,
    )

SCORES_PATH = REPO_ROOT / "docs" / "04_research_records" / "backtest" / "scores" / "2026" / "exam_scores_v1.yaml"

#: 本件考族（OD-1 面）；calibration/event 族卡误入即拒（各归其执行器，禁越族代考）
_FAMILIES = ("comparison", "ablation")

_ROUTE_VOCAB = {"dual_arm": _UNION_PILLAR_KEYS, "event": _EVENT_KNOWN_KEYS, "series": _CALIBRATION_JUDGED_KEYS}


def _vocab_of(route: str) -> frozenset:
    return _ROUTE_VOCAB.get(route, _CALIBRATION_JUDGED_KEYS)


def _route_vocab(card: dict) -> dict:
    """分诊三元组（blocked 行自带）：判官路由 + 绑定分类 + 词汇覆盖，给生产线指出"缺什么才可考"。"""
    route = pillars_route(card)
    cls = _cb.classify_card(card)
    pn = set(card.get("pillars_numeric") or {})
    return {
        "route": route,
        "binding_class": cls.get("cls"),
        "binding_reason": cls.get("reason"),
        "pillars_outside_vocab": sorted(pn - _vocab_of(route)) if pn else [],
    }


def _append_row(scores_path: Path, row: dict) -> dict:
    """分数册 only-add 追加（与 run_card 同一双文档 register 形态：doc0=register 头，
    含 rows 的 doc 为账本本体；safe_dump_all 写回保结构，裁定#536 迁移形态）。"""
    sp = Path(scores_path)
    if sp.exists():
        docs = [d for d in yaml.safe_load_all(sp.read_text(encoding="utf-8")) if isinstance(d, dict)] or [{}]
        reg = next((d for d in docs if d.get("rows") is not None), docs[-1])
        rows = reg.get("rows") or []
    else:
        reg = {"schema_version": "1.0", "title": "考试卡分数册（成绩汇总面，方案 §6 D4）", "rows": []}
        docs = [reg]
        rows = reg["rows"]
    rows.append(row)
    reg["rows"] = rows
    sp.parent.mkdir(parents=True, exist_ok=True)
    dump = (
        yaml.safe_dump_all(docs, allow_unicode=True, sort_keys=False, width=140)
        if len(docs) > 1
        else yaml.safe_dump(reg, allow_unicode=True, sort_keys=False, width=140)
    )
    sp.write_text(dump, encoding="utf-8", newline="\n")
    return row


def _blocked_row(card: dict, scores_path: Path, run_id: str, reason: str, triage: dict) -> dict:
    """blocked 出分面（fail-closed 禁编）：任一腿装载不出时的如实分数行。

    不翻卡（examined=已出分，blocked 不是分）；不记试次（零数据消费=零试验，DSR 分母不虚增，
    同 card_binding.run_one 绑定失败不记账先例）；行自带 route/binding_class/拒因给生产线分诊。"""
    route = triage.get("route") or pillars_route(card)
    row = {
        "card_id": card["card_id"],
        "node_id": card.get("node_id"),
        "run_id": run_id,
        "kind": "exam",
        "verdict": "blocked",
        "pillars_all_pass": False,
        "oos_ok": False,
        "regimes": [],
        "date": _date.today().isoformat(),
        "metrics": {},
        "blocked": {
            "reason": str(reason)[:400],
            "family": card.get("family"),
            "route": route,
            "binding_class": triage.get("binding_class"),
            "binding_reason": triage.get("binding_reason"),
            "note": "双腿装载不出=如实记 blocked（禁编造指标）；卡面不翻 examined；试次零消费不记账",
        },
        "unjudged": _unjudged_pillars(card, {}, _vocab_of(route)),
        "fails": [f"blocked: {reason}"[:400]],
    }
    return _append_row(Path(scores_path), row)


def _read_back_row(scores_path: Path, card_id: str) -> dict:
    """写后核实：从分数册读回本卡最新一行（book 通道由 run_one→run_card 落行，本件不重写它的返回面）。"""
    sp = Path(scores_path)
    docs = [d for d in yaml.safe_load_all(sp.read_text(encoding="utf-8")) if isinstance(d, dict)]
    for reg in (d for d in docs if d.get("rows") is not None):
        hits = [r for r in (reg.get("rows") or []) if isinstance(r, dict) and str(r.get("card_id")) == card_id]
        if hits:
            return hits[-1]
    return {
        "card_id": card_id,
        "verdict": None,
        "note": "score_row_readback_missed（run_one 报成但读回未中，须人工核册）",
    }


def run_card_comparison(
    card_path: str | Path,
    *,
    signal=None,
    signal_b=None,
    target=None,
    binding_book_path: str | Path | None = None,
    arms_variant: str | None = None,
    expected_family: str | None = None,
    force: bool = False,
    run_id: str | None = None,
    run_tag: str = "",
    recorded_by: str = "comparison_exam",
    scores_path: Path = SCORES_PATH,
    ledger_registry_path: Path | None = None,
    dry: bool = False,
) -> dict:
    """对照/消融卡逐卡开考入口：族闸 → 状态闸 → 双腿装载（R1 注入 / R2 绑定册 arms / R3 绑定册单信号）
    → calibration_exam.run_card 出分（一票否决/only-add/翻卡/台账），装载不出=blocked 行如实入册。"""
    card_path = Path(card_path)
    card = yaml.safe_load(card_path.read_text(encoding="utf-8"))
    if not isinstance(card, dict) or not card.get("card_id"):
        raise _ToolError("卡件不可解析或缺 card_id（族驱动器拒考病卡）", {"path": str(card_path)})
    cid = str(card["card_id"])
    family = str(card.get("family") or "")
    if family not in _FAMILIES:
        raise _ToolError(
            f"family={family!r} 非对照/消融族——本件只考 {list(_FAMILIES)}（其余族走各自执行器，禁越族代考）",
            {"card_id": cid},
        )
    if expected_family and expected_family != family:
        raise _ToolError(
            f"--family={expected_family!r} 与卡面 family={family!r} 不符（防考错族，拒）", {"card_id": cid}
        )
    triage = _route_vocab(card)
    route = triage["route"]
    run_id_eff = run_id or f"examcard-{_date.today().isoformat()}"
    status = card.get("status")
    if dry:
        # 分诊=只读面，先于状态闸（examined/blocked 卡同样可分诊；状态闸拦的是出分不是看诊）
        entry = None
        if binding_book_path:
            entry = _cb.load_binding_book(Path(binding_book_path), arms_variant=arms_variant).get(cid)
        return {
            "card_id": cid,
            "dry_run": True,
            "family": family,
            "status": status,
            "book_entry": bool(entry),
            **triage,
        }
    if status != "preregistered" and not force:
        raise _ToolError("卡状态非 preregistered：只考 preregistered 卡（重考带 --force）", {"status": status})

    # R1 注入通道（与 calibration_exam.main 同契约；测试零 CH）
    if any(v is not None for v in (signal, signal_b, target)):
        if route == "dual_arm" and signal_b is None:
            return _blocked_row(
                card, scores_path, run_id_eff, "dual_arm_route_needs_signal_b（配对判据缺第二腿）", triage
            )
        if signal is None or target is None:
            return _blocked_row(card, scores_path, run_id_eff, "injected_leg_missing（signal/target 注入不全）", triage)
        return run_card(
            card_path,
            signal=signal,
            signal_b=signal_b,
            target=target,
            force=force,
            run_id=run_id_eff,
            recorded_by=recorded_by,
            scores_path=Path(scores_path),
            ledger_registry_path=ledger_registry_path,
        )

    # R2/R3 绑定册通道（双腿装配/判分/出分/反挪门柱自闸全在 run_one 原函数，本件不复制装配代码）
    if not binding_book_path:
        return _blocked_row(
            card, scores_path, run_id_eff, "binding_book_absent（--binding-book 必填：双腿接线面唯一在册来源）", triage
        )
    book = _cb.load_binding_book(Path(binding_book_path), arms_variant=arms_variant)
    if cid not in book:
        return _blocked_row(
            card,
            scores_path,
            run_id_eff,
            f"binding_book_entry_absent（卡未在册双腿接线；route={route}，先落绑定册 arms 格）",
            triage,
        )
    try:
        res = _cb.run_one(card_path, {cid}, Path(scores_path), run_tag or recorded_by, False, book, force, recorded_by)
    except _cb.BindingIntegrityError:
        raise  # 反挪门柱自闸=报警不降级（blocked 不是它的正确去向）
    except Exception as exc:  # noqa: BLE001 — CH 不可达/底座装配失败等 → blocked 如实记因
        return _blocked_row(
            card, scores_path, run_id_eff, f"book_channel_raise:{type(exc).__name__}:{str(exc)[:160]}", triage
        )
    if "verdict" in res:
        return _read_back_row(Path(scores_path), cid)
    reason = res.get("error") or res.get("skipped") or f"book_channel_unknown:{res}"
    if reason == "already_examined_needs_force":
        raise _ToolError("卡状态非 preregistered：只考 preregistered 卡（重考带 --force）", {"status": status})
    return _blocked_row(card, scores_path, run_id_eff, f"book_channel:{reason}", triage)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--card", required=True, help="对照/消融卡 yaml 路径")
    ap.add_argument("--family", choices=_FAMILIES, help="族面复核（与卡面 family 不符即拒）")
    ap.add_argument("--binding-book", help="绑定册 yaml（双腿接线面唯一在册来源；R2/R3 通道必填）")
    ap.add_argument("--arms-variant", default="", help="一卡多对臂时指名本跑配对档（册格 arms_variants 键）")
    ap.add_argument("--signal-csv", help="开臂信号 csv（index=date；series 用 value 列）")
    ap.add_argument("--signal-b-csv", help="基臂/消融臂信号 csv（配对判据卡必带）")
    ap.add_argument("--target-csv", help="目标 csv（index=date，value 列）")
    ap.add_argument("--scores", default=str(SCORES_PATH), help="分数册路径（缺省=生产真源）")
    ap.add_argument("--force", action="store_true", help="已考卡重考：分数册 only-add 追加，禁改旧行")
    ap.add_argument("--run-id", default="", help="分数行 run_id（缺省=examcard-<日>）")
    ap.add_argument("--run-tag", default="", help="book 通道 run_tag（行 run_id=mineloop-<tag>-<卡尾>）")
    ap.add_argument("--recorded-by", default="comparison_exam", help="试次台账归属 sid（建议显式传本班 sid）")
    ap.add_argument("--dry-run", action="store_true", help="只出分诊（route/binding_class/在册与否），零写")
    ap.add_argument(
        "--override-ch-window-with-reason", default="", help="CH 让路窗（21:00-22:30/01:00-04:00）显式留痕越窗"
    )
    args = ap.parse_args()

    def _csv_col(p: str | None):
        if not p:
            return None
        import pandas as pd

        df = pd.read_csv(p, index_col=0, parse_dates=True)
        return df.iloc[:, 0] if df.shape[1] == 1 else df

    win = _cb._in_ch_yield_window(__import__("datetime").datetime.now())
    ch_free = not args.binding_book  # 注入通道零 CH
    if win and not ch_free and not args.override_ch_window_with_reason:
        print(json.dumps({"refused": win}, ensure_ascii=False))
        return 3
    row = run_card_comparison(
        args.card,
        signal=_csv_col(args.signal_csv),
        signal_b=_csv_col(args.signal_b_csv),
        target=_csv_col(args.target_csv),
        binding_book_path=args.binding_book,
        arms_variant=args.arms_variant or None,
        expected_family=args.family,
        force=args.force,
        run_id=args.run_id or None,
        run_tag=args.run_tag,
        recorded_by=args.recorded_by,
        scores_path=Path(args.scores),
        dry=args.dry_run,
    )
    print(json.dumps(row, ensure_ascii=False, indent=2, default=str))
    return 0 if row.get("verdict") == "pass" else 1


# 人工CLI设计如此（同域MOD-BT-197/243先例）：按TDM变更/分数册更新/逐卡开考人工触发，非永久自动系统面
if __name__ == "__main__":  # noqa: m11-perm-manual-legitimate  人工CLI（同域先例），非永久自动系统
    sys.exit(main())
