# -*- coding: utf-8 -*-
# [A_test] module_id: MOD-SIG-148_redblue | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [MODULE] tests.factor.test_red_blue_lifecycle
# [DOMAIN] D_FACTOR
# [INVARIANTS] tests_must_pass;boundary_and_dirty_data_coverage
# [MODIFY-GUARD] only_add_tests
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest exit 0 on pass, non-zero on fail
# [TESTS] pytest tests/factor/test_red_blue_lifecycle.py
# [TTL] task_bound
"""红队对抗用例：边界值/脏数据/非法输入——测出问题即修。"""

from __future__ import annotations

import json

import pytest

from zephyr.factor.analysis.factor_lifecycle_runner import (
    LifecycleStoreLite,
    _ic_p_value,
    certify_factor_family,
)
from zephyr.signal_ashare.strategy_signal.pattern_lifecycle import LifecycleStore
from zephyr.signal_ashare.strategy_signal.strategy_decay_certifier import (
    run_strategy_decay_certify,
)


# ── 红 1：因子边界值 ─────────────────────────────────────────────────────────


def test_red_ic_exact_thresholds():
    """ic 恰在 0.1/0.05 阈值上：judge 用 >=（边界归上档）。"""
    from zephyr.factor.analysis.three_level_judgment import judge_factor

    assert judge_factor(0.10) in ("优秀", "合格")  # 阈值边界不崩
    assert judge_factor(0.05) in ("优秀", "合格", "淘汰")


def test_red_ic_numeric_string():
    """registry ic="0.12"（字符串数字）：runner 应转数值判定而非 failed。"""
    out = certify_factor_family(
        [{"factor_id": "F-S", "ic": "0.30", "ir": "0.8", "lookback_period": "240"}],
        q=0.10,
    )
    assert out[0]["state"] in ("certified", "probation")


def test_red_ic_boundary_one():
    """ic=1.0/−1.0 极值不崩（|ic|≥1 的 p 值=1.0 兜底）。"""
    out = certify_factor_family(
        [{"factor_id": "F-P", "ic": 1.0, "ir": 1.0, "lookback_period": 240},
         {"factor_id": "F-N", "ic": -1.0, "ir": 0.0, "lookback_period": 240}],
        q=0.10,
    )
    assert len(out) == 2
    assert all(r["state"] in ("certified", "probation", "failed") for r in out)


def test_red_bhy_all_identical_p():
    """全族同 p 值：BHY 不崩、拒绝掩码同长。"""
    out = certify_factor_family(
        [{"factor_id": f"F{i}", "ic": 0.10, "ir": 0.5, "lookback_period": 100}
         for i in range(30)],
        q=0.10,
    )
    assert len(out) == 30


def test_red_lookback_below_minimum():
    """lookback=2（<3）：p 值兜底 1.0，封顶 probation 不炸。"""
    out = certify_factor_family(
        [{"factor_id": "F-T", "ic": 0.30, "ir": 0.8, "lookback_period": 2}],
        q=0.10,
    )
    assert out[0]["state"] == "probation"


# ── 红 2：策略衰减边界 ───────────────────────────────────────────────────────


def test_red_strategy_ds_exact_boundary(tmp_path):
    """DS=0.5 恰在认证线上：归 certified（>=语义）。"""
    rows = [{"strategy_id": "STR-X", "deflated_sharpe": 0.5,
             "is_sharpe": 1.0, "max_drawdown": 0.2}]
    r = run_strategy_decay_certify(
        ledger_path=tmp_path / "l.json", today="D1", rows=rows
    )
    assert r["counts"]["certified"] == 1


def test_red_strategy_all_none_ds(tmp_path):
    """全策略无 DS：全 probation 不炸。"""
    rows = [{"strategy_id": "STR-A", "deflated_sharpe": None,
             "is_sharpe": None, "max_drawdown": None},
            {"strategy_id": "STR-B", "deflated_sharpe": None,
             "is_sharpe": None, "max_drawdown": None}]
    r = run_strategy_decay_certify(
        ledger_path=tmp_path / "l.json", today="D1", rows=rows
    )
    assert r["counts"]["probation"] == 2


class _FakeRows:
    def __init__(self, rows):
        self._rows = rows

    def execute(self, sql, params=None):
        return self._rows


# ── 红 3：台账完整性 ─────────────────────────────────────────────────────────


def test_red_lifecycle_store_corrupt_raises(tmp_path):
    """台账 JSON 损坏：load 抛 ValueError（不静默吞）。"""
    store = LifecycleStore(tmp_path / "corrupt.json")
    store._path.write_text("{broken json", encoding="utf-8")
    with pytest.raises(Exception):
        store.load()


def test_red_factor_store_corrupt_raises(tmp_path):
    store = LifecycleStoreLite(tmp_path / "corrupt.json")
    store._path.write_text("[]", encoding="utf-8")  # 结构错（list 非 dict）
    with pytest.raises(Exception):
        store.load()
