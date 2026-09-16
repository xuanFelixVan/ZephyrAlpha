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


def _screen(oos=1.8, dsr=0.4):
    return {"oos_sharpe": oos, "deflated_sharpe": dsr, "num_trials": 100}


def test_score_all_pass_is_promote_ready():
    pocket = {"max_drawdown": 0.08, "trades": 42}
    r = pcg.score_candidate({"strategy_id": "S-A"}, _screen(), pocket)
    assert r["verdict"] == "promote_ready" and r["evidence_gaps"] == []
    assert all(c["ok"] is True for c in r["checks"])


def test_score_hard_fail_is_reject_even_with_gaps():
    pocket = {"max_drawdown": 0.35, "trades": 5}
    r = pcg.score_candidate({"strategy_id": "S-B"}, _screen(oos=0.9, dsr=-0.1), pocket)
    assert r["verdict"] == "reject"
    assert {c["name"] for c in r["checks"] if c["ok"] is False} == {"oos_sharpe", "max_drawdown", "capacity_trades", "dsr"}


def test_score_missing_evidence_is_borderline_not_reject():
    r = pcg.score_candidate({"strategy_id": "S-C", "oos_sharpe": 1.8}, None, None)
    assert r["verdict"] == "borderline"
    assert set(r["evidence_gaps"]) == {"max_drawdown", "capacity_trades", "dsr"}


def test_score_advisory_fallback_fields_used_when_screen_none():
    r = pcg.score_candidate({"strategy_id": "S-D", "oos_sharpe": 1.2, "deflated_sharpe": 0.3}, None,
                            {"max_drawdown": 0.10, "trades": 50})
    checks = {c["name"]: c for c in r["checks"]}
    assert checks["oos_sharpe"]["ok"] is False  # 1.2 < 1.5 硬败
    assert checks["dsr"]["ok"] is True
    assert r["verdict"] == "reject"


def test_max_drawdown_math():
    assert pcg._max_drawdown([100, 120, 90, 110]) == pytest.approx(0.25)
    assert pcg._max_drawdown([100]) is None
    assert pcg._max_drawdown([]) is None


def test_render_report_sections(tmp_path):
    r = pcg.score_candidate({"strategy_id": "S-A"}, _screen(), {"max_drawdown": 0.08, "trades": 42})
    md = pcg.render_report([r])
    assert "转正建议书" in md and "promote_ready" in md and "Owner 门终裁" in md
    assert pcg.THRESHOLD_SOURCE in md


def test_main_dry_run_degrades_without_ch(tmp_path, capsys, monkeypatch):
    _adv(tmp_path, "S-E", oos_sharpe=1.8)
    monkeypatch.setattr(pcg, "_query_screen", lambda sid: None)
    monkeypatch.setattr(pcg, "_query_pocket", lambda sid: None)
    sys_argv = ["promotion_combo_gate.py", "--advisory-dir", str(tmp_path), "--dry-run",
                "--out-dir", str(tmp_path / "out")]
    monkeypatch.setattr(sys, "argv", sys_argv)
    assert pcg.main() == 0
    out = capsys.readouterr().out
    assert "S-E" in out and "borderline" in out
