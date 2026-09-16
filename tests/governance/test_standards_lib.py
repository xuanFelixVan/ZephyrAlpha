# [BLUEPRINT] MOD-AUTO-L5-001(暂编号) | docs/_working/automation/campaign/blueprints/standards_lib_blueprint.md | §测试
# [MODULE] tests.governance.test_standards_lib
# [DOMAIN] D_GOV_SCRIPTS
# [INVARIANTS] fixture 注入，不触碰真源 standards.yaml
# [TTL] permanent
"""standards_lib 测试：frozen 门禁+重考历史翻转清单。"""
from __future__ import annotations

import pytest

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT / "scripts" / "governance" / "standards") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "scripts" / "governance" / "standards"))

import standards_lib as sl  # noqa: E402

get_frozen_thresholds = sl.get_frozen_thresholds
load_standards = sl.load_standards
regrade_diff = sl.regrade_diff

_STDS = {
    "STD-A": {"std_id": "STD-A", "status": "frozen", "_frozen": True,
              "thresholds": {"oos_sharpe_min": 1.5}},
    "STD-B": {"std_id": "STD-B", "status": "draft", "_frozen": False,
              "thresholds": {"oos_sharpe_min": 1.0}},
}


def test_get_frozen_thresholds_ok():
    th = get_frozen_thresholds("STD-A", _STDS)
    assert th == {"oos_sharpe_min": 1.5}


def test_draft_standard_rejected_as_active_gauge():
    with pytest.raises(ValueError):
        get_frozen_thresholds("STD-B", _STDS)
    with pytest.raises(KeyError):
        get_frozen_thresholds("STD-X", _STDS)


def test_regrade_diff_detects_flips():
    old = {"oos_sharpe_min": 1.5, "max_drawdown_max": 0.15, "min_trades": 30, "dsr_min": 0.0}
    new = {"oos_sharpe_min": 1.0, "max_drawdown_max": 0.15, "min_trades": 30, "dsr_min": 0.0}
    cands = [
        {"id": "A", "oos_sharpe": 1.8, "max_drawdown": 0.10, "trades": 40, "dsr": 0.4},
        {"id": "B", "oos_sharpe": 1.3, "max_drawdown": 0.12, "trades": 35, "dsr": 0.2},
        {"id": "C", "oos_sharpe": 0.5, "max_drawdown": 0.30, "trades": 5, "dsr": -0.1},
    ]
    flips = regrade_diff(old, new, cands)
    assert {f["id"] for f in flips} == {"B"}  # 只 B 被放宽尺子捞上来
    assert flips[0]["old"] == "reject" and flips[0]["new"] == "promote_ready"


def test_regrade_diff_same_gauge_zero_flips():
    th = {"oos_sharpe_min": 1.5, "max_drawdown_max": 0.15, "min_trades": 30, "dsr_min": 0.0}
    cands = [{"id": "A", "oos_sharpe": 1.8, "max_drawdown": 0.10, "trades": 40, "dsr": 0.4}]
    assert regrade_diff(th, th, cands) == []
