# [BLUEPRINT] MOD-AUTO-L2-001(暂编号) | docs/_working/automation/campaign/blueprints/promotion_combo_gate_blueprint.md | §测试
# [MODULE] tests.backtest.test_promotion_combo_gate
# [DOMAIN] D_BACKTEST
# [INVARIANTS] 零 CH/网络触碰——CH 读写函数全部 monkeypatch；临时目录隔离（宪法 §9.6）
# [TTL] permanent
"""promotion_combo_gate 组合门打分器测试——纯函数直喷+IO 降级路径。"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT / "scripts" / "backtest") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "scripts" / "backtest"))

import promotion_combo_gate as pcg  # noqa: E402


def _adv(tmp_path: Path, sid: str, **extra) -> Path:
    p = tmp_path / f"adv-{sid}.json"
    p.write_text(json.dumps({"strategy_id": sid, **extra}, ensure_ascii=False), encoding="utf-8")
    return p


def test_load_advisories_reads_json_and_skips_garbage(tmp_path):
    _adv(tmp_path, "S-1", oos_sharpe=1.8)
    (tmp_path / "broken.json").write_text("{not json", encoding="utf-8")
    out = pcg.load_advisories(tmp_path)
    assert len(out) == 1 and out[0]["strategy_id"] == "S-1"


def test_load_advisories_missing_dir_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        pcg.load_advisories(tmp_path / "nope")


def _screen(oos=1.8, dsr=0.8, turnover=6.0):
    return {"oos_sharpe": oos, "deflated_sharpe": dsr, "num_trials": 100, "turnover": turnover}


def test_v2_thresholds_pinned():
    """v2 frozen 尺钉值（STD-SIM-ACCESS-002，裁定#337；MODIFY-GUARD：阈值变更须同步本钉值）。"""
    assert pcg.THRESHOLDS == {
        "oos_sharpe_min": 1.5,
        "max_drawdown_max": 0.15,
        "min_trades": 30,
        "dsr_min": 0.5,
        "combo_corr_max": 0.7,
        "ann_turnover_1side_max": 12.0,
    }
    assert "STD-SIM-ACCESS-002" in pcg.THRESHOLD_SOURCE
    md = pcg.render_report([pcg.score_candidate({"strategy_id": "S-X"}, None, None)])
    assert "suspect" in md and "裁定#306" in md  # v1 suspect 注记防口径误读（WO-08-04）


def test_score_all_pass_is_promote_ready():
    pocket = {"max_drawdown": 0.08, "trades": 42}
    adv = {"strategy_id": "S-A", "avg_pairwise_corr": 0.3}  # ρ̄ 证据=advisory 携带（F73 未建）
    r = pcg.score_candidate(adv, _screen(), pocket)
    assert r["verdict"] == "promote_ready" and r["evidence_gaps"] == []
    assert all(c["ok"] is True for c in r["checks"])
    assert {c["name"] for c in r["checks"]} == {
        "oos_sharpe",
        "max_drawdown",
        "capacity_trades",
        "dsr",
        "combo_corr",
        "ann_turnover",
    }


def test_score_hard_fail_is_reject_even_with_gaps():
    pocket = {"max_drawdown": 0.35, "trades": 5}
    r = pcg.score_candidate({"strategy_id": "S-B"}, _screen(oos=0.9, dsr=-0.1, turnover=None), pocket)
    assert r["verdict"] == "reject"
    assert {c["name"] for c in r["checks"] if c["ok"] is False} == {
        "oos_sharpe",
        "max_drawdown",
        "capacity_trades",
        "dsr",
    }


def test_score_dsr_v2_boundary():
    """v2 DSR 腿边界：≥0.5 过线（v1 的 >0 口径退役）。"""
    ok_row = pcg.score_candidate(
        {"strategy_id": "S-D1"}, _screen(dsr=0.5, turnover=6.0), {"max_drawdown": 0.08, "trades": 42}
    )
    fail_row = pcg.score_candidate(
        {"strategy_id": "S-D2"}, _screen(dsr=0.49, turnover=6.0), {"max_drawdown": 0.08, "trades": 42}
    )
    by = {r["strategy_id"]: {c["name"]: c["ok"] for c in r["checks"]} for r in (ok_row, fail_row)}
    assert by["S-D1"]["dsr"] is True
    assert by["S-D2"]["dsr"] is False


def test_score_missing_evidence_is_borderline_not_reject():
    r = pcg.score_candidate({"strategy_id": "S-C", "oos_sharpe": 1.8}, None, None)
    assert r["verdict"] == "borderline"
    assert set(r["evidence_gaps"]) == {"max_drawdown", "capacity_trades", "dsr", "combo_corr", "ann_turnover"}


def test_score_advisory_fallback_fields_used_when_screen_none():
    r = pcg.score_candidate(
        {
            "strategy_id": "S-D",
            "oos_sharpe": 1.2,
            "deflated_sharpe": 0.3,
            "avg_pairwise_corr": 0.4,
            "ann_turnover_1side": 8.0,
        },
        None,
        {"max_drawdown": 0.10, "trades": 50},
    )
    checks = {c["name"]: c for c in r["checks"]}
    assert checks["oos_sharpe"]["ok"] is False  # 1.2 < 1.5 硬败
    assert checks["dsr"]["ok"] is False  # 0.3 < 0.5（v2 尺由 v1 >0 提线）
    assert checks["combo_corr"]["ok"] is True and checks["ann_turnover"]["ok"] is True
    assert r["verdict"] == "reject"


def test_max_drawdown_math():
    assert pcg._max_drawdown([100, 120, 90, 110]) == pytest.approx(0.25)
    assert pcg._max_drawdown([100]) is None
    assert pcg._max_drawdown([]) is None


def test_render_report_sections(tmp_path):
    r = pcg.score_candidate(
        {"strategy_id": "S-A", "avg_pairwise_corr": 0.3}, _screen(), {"max_drawdown": 0.08, "trades": 42}
    )
    md = pcg.render_report([r])
    assert "转正建议书" in md and "promote_ready" in md and "Owner 门终裁" in md
    assert pcg.THRESHOLD_SOURCE in md


def test_main_dry_run_degrades_without_ch(tmp_path, capsys, monkeypatch):
    _adv(tmp_path, "S-E", oos_sharpe=1.8)
    monkeypatch.setattr(pcg, "_query_screen", lambda sid: None)
    monkeypatch.setattr(pcg, "_query_pocket", lambda sid: None)
    sys_argv = [
        "promotion_combo_gate.py",
        "--advisory-dir",
        str(tmp_path),
        "--dry-run",
        "--out-dir",
        str(tmp_path / "out"),
    ]
    monkeypatch.setattr(sys, "argv", sys_argv)
    assert pcg.main() == 0
    out = capsys.readouterr().out
    assert "S-E" in out and "borderline" in out


def test_strategy_id_cli_path_survives(tmp_path, capsys, monkeypatch):
    """F821 回归钉：``--strategy-id`` 分支须可跑通——落地版 ``_safe_id`` 用而未定义，
    该分支一按参数就 NameError（无测覆盖所以潜伏，本钉防复发）。"""
    _adv(tmp_path, "S-KEEP", oos_sharpe=1.8)
    _adv(tmp_path, "S-DROP", oos_sharpe=1.8)
    monkeypatch.setattr(pcg, "_query_screen", lambda sid: None)
    monkeypatch.setattr(pcg, "_query_pocket", lambda sid: None)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "promotion_combo_gate.py",
            "--strategy-id",
            " S-KEEP ",
            "--dry-run",
            "--advisory-dir",
            str(tmp_path),
            "--out-dir",
            str(tmp_path / "out"),
        ],
    )
    assert pcg.main() == 0
    out = capsys.readouterr().out
    assert "S-KEEP" in out and "S-DROP" not in out
    assert pcg._safe_id(" a/b\\c ") == "abc"  # 分隔符剥净，入参只作等值匹配不作路径
