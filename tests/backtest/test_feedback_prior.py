# [BLUEPRINT] MOD-BT-223 | docs/03_modules/_domain_backtest/blueprint.md | §回灌边消费端测试
# [MODULE] tests.backtest.test_feedback_prior
# [DOMAIN] D_BACKTEST
# [INVARIANTS] 零 CH/网络/生产路径触碰——query 函数注入、台账走 tmp_path（宪法 §9.6）
# [TTL] permanent
"""feedback_prior 回灌边消费端测试——FL1（E9→E2）/FL2（E6→E1）读数纯函数+fail-open 边界。"""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT / "scripts" / "backtest") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "scripts" / "backtest"))

import feedback_prior as fp  # noqa: E402
import hypothesis_precheck as hp  # noqa: E402


def _ledger(tmp_path: Path, strategies: dict) -> Path:
    p = tmp_path / "strategy_decay_ledger.json"
    p.write_text(
        json.dumps(
            {"schema": "strategy_decay/2", "updated_at": "2026-09-21", "strategies": strategies}, ensure_ascii=False
        ),
        encoding="utf-8",
    )
    return p


def test_decay_digest_counts_states_and_suspect(tmp_path):
    p = _ledger(
        tmp_path,
        {
            "CAND-a": {"state": "probation", "failed_streak": 0},
            "CAND-b": {"state": "probation"},
            "CAND-c": {"state": "decayed", "oos_years_decay": 0.7},
        },
    )
    d = fp.decay_prior_digest(p)
    assert d["total"] == 3 and d["updated_at"] == "2026-09-21"
    assert d["states"] == {"probation": 2, "decayed": 1}
    assert d["suspect"] == ["CAND-c"]


def test_decay_digest_fail_open(tmp_path):
    assert fp.decay_prior_digest(tmp_path / "missing.json") is None
    bad = tmp_path / "bad.json"
    bad.write_text("{not json", encoding="utf-8")
    assert fp.decay_prior_digest(bad) is None
    empty = tmp_path / "empty.json"
    empty.write_text(json.dumps({"schema": "strategy_decay/2", "strategies": {}}), encoding="utf-8")
    assert fp.decay_prior_digest(empty) is None


def test_attribution_digest_with_injected_query():
    rows = [{"trade_date": "2026-09-24", "n": 2, "net_sum": 123.5}]
    d = fp.attribution_prior_digest(query=lambda sql: rows)
    assert d == {"trade_date": "2026-09-24", "strategies": 2, "pnl_net_sum": 123.5}


def test_attribution_digest_fail_open():
    def boom(sql):
        raise RuntimeError("CH down")

    assert fp.attribution_prior_digest(query=boom) is None
    assert fp.attribution_prior_digest(query=lambda sql: []) is None


def test_intake_direction_readonly_not_decision():
    d = fp.intake_direction(
        {
            "schema": "strategy_decay/2",
            "updated_at": "2026-09-21",
            "total": 2,
            "states": {"probation": 1, "decayed": 1},
            "suspect": ["CAND-c"],
        },
        {"trade_date": "2026-09-24", "strategies": 2, "pnl_net_sum": -3.5},
    )
    assert d["loops"]["FL2"] == "FAC-E6→FAC-E1"  # 声明边对齐骨架 feedback_loops
    assert "在考 2 只" in d["direction_note"] and "存疑/判死 1 只" in d["direction_note"]
    assert "归因日账（E9）2026-09-24" in d["direction_note"]
    assert d["sources"]["decay_ledger"]["total"] == 2


def test_intake_direction_missing_decay_honest_gap():
    d = fp.intake_direction(None)
    assert "缺证" in d["direction_note"] and "decay_ledger" not in d["sources"]


def test_precheck_prior_note_empty_when_no_sources():
    assert fp.precheck_prior_note(None, None) == ""


def test_precheck_prior_note_carries_background_disclaimer():
    note = fp.precheck_prior_note(
        {
            "schema": "strategy_decay/2",
            "updated_at": "2026-09-21",
            "total": 574,
            "states": {"probation": 574},
            "suspect": [],
        }
    )
    assert "E6" in note and "只作背景不作判据" in note


def test_build_prompt_prior_note_injection_boundary():
    base = hp.build_prompt("假说H", "D")
    assert "回灌先验" not in base  # 空先验=prompt 字节级不变（确定性回溯）
    injected = hp.build_prompt("假说H", "D", prior_note="衰减台账在考 574 只（背景）")
    assert "回灌先验（只作背景不作判据）" in injected and "574" in injected
    assert injected.startswith(hp.build_prompt("假说H", "D").split("\n\n")[0])
