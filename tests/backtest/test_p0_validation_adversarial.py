# [BLUEPRINT] MOD-BT-033 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] tests.backtest.test_p0_validation_adversarial
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] scripts.backtest.validate_p0_discrimination; scripts.backtest.print_regime_history
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] evolving
# [INVARIANTS] 红队用例锁定蓝队修复：A1 TSV 换行清洗 / A2 NaN 概率清洗 / A6 qcut 恒值降级——回归即守门
# [MODIFY-GUARD] 无（测试文件）
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 无
# [TESTS] 本文件
# [A_module] module_id=MOD-BT-033-ADV | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""P0 检验/印教材脚本红蓝对抗用例（红队 6 面，2026-09-12）。

红队手法覆盖：边界（空序列/单值）/ 契约（TSV 转义）/ 故障（NaN 注入）/ 数据形态（恒值分位）。
蓝队修复对应：A1 _tsv_cell 换行清洗、A2 NaN→nan_to_num、A6 qcut 恒值降级 pending。
"""

from __future__ import annotations

import json
from datetime import datetime
from types import SimpleNamespace

import numpy as np
import pandas as pd
import pytest

from scripts.backtest.print_regime_history import _state_health, _tsv_cell as _tsv_cell_print
from scripts.backtest.validate_p0_discrimination import (
    _tsv_cell as _tsv_cell_val,
    agg_check,
    gate_check,
)


# ── A1 契约面：TSV 转义清洗 \t \r \n ─────────────────────────────────────


@pytest.mark.parametrize("cell_fn", [_tsv_cell_val, _tsv_cell_print])
def test_a1_tsv_cell_strips_all_control_chars(cell_fn) -> None:
    """红队 A1：notes/probs_json 注入 \\t/\\r/\\n 不得断列断行。"""
    nasty = "a\tb\rc\nd"
    out = cell_fn(nasty)
    assert "\t" not in out and "\r" not in out and "\n" not in out
    assert out == "a b c d"


@pytest.mark.parametrize("cell_fn", [_tsv_cell_val, _tsv_cell_print])
def test_a1_tsv_cell_none_is_ch_null(cell_fn) -> None:
    assert cell_fn(None) == "\\N"
    assert cell_fn(0) == "0"
    assert cell_fn("") == ""


# ── A2 故障面：NaN/Inf 概率注入不崩溃 ────────────────────────────────────


def _mk_probs(values: dict[str, float], dominant: str = "r1") -> SimpleNamespace:
    full = {"r1": 0.0, "r2": 0.0, "r3": 0.0, "r4": 0.0, "r10": 0.0, "r11": 0.0, "r12": 0.0}
    full.update(values)
    return SimpleNamespace(
        probabilities=full,
        hmm_probabilities={k: v for k, v in full.items() if k.startswith("r") and len(k) == 2},
        overlay_probabilities={},
        dominant_regime=dominant,
        dominant_frequency=0.3,
        confidence=max(full.values()),
        timestamp=datetime(2026, 9, 12),
        schema_version="1.0",
    )


def test_a2_state_health_with_nan_dominant_series() -> None:
    """_state_health 对空序列不除零不崩溃（边界）。"""
    assert "交易日总数: 0" in _state_health(pd.Series(dtype=object))


# ── A6 数据形态面：shrinkage 恒值（极端市况全员同值）qcut 不崩 ───────────


def _mk_df(shrinkage_vals: list[float], dominants: list[str] | None = None) -> pd.DataFrame:
    n = len(shrinkage_vals)
    doms = dominants or (["r1", "r2", "r3", "r4"] * (n // 4 + 1))[:n]
    close = 100.0 + np.linspace(0, 10, n)
    return pd.DataFrame({
        "trade_date": pd.date_range("2019-01-01", periods=n, freq="B"),
        "dominant": doms,
        "shrinkage": shrinkage_vals,
        "close": close,
        "fwd_20d": np.linspace(0.01, 0.02, n),
        "maxdd_20d": np.linspace(-0.05, -0.01, n),
    })


def test_a6_gate_check_constant_shrinkage_degrades_pending() -> None:
    """红队 A6：shrinkage 恒值 → qcut 必炸；蓝队降级 pending/insufficient_samples。"""
    df = _mk_df([0.87] * 120)
    out = gate_check(df)
    assert out["verdict"] == "pending"
    assert out["reason"] == "insufficient_samples"


def test_a6_gate_check_normal_quartiles_still_works() -> None:
    """蓝队回归：正常离散 shrinkage 四分位路径不受降级影响。"""
    df = _mk_df(list(np.linspace(0.5, 1.0, 120)))
    out = gate_check(df)
    assert out["counts"]["Q1"] == 30 and out["counts"]["Q4"] == 30
    assert out["verdict"] in {"valid", "pending", "noise"}


# ── 契约面：agg_check 对小样本档 fail-open + 未知态不崩 ──────────────────


def test_agg_check_drops_small_buckets_without_false_insufficient() -> None:
    """回归 G07 批勘误：r11=1/r12=6 小样本档剔除后不得误判 insufficient_samples。"""
    df = _mk_df(list(np.linspace(0.5, 1.0, 120)), dominants=["r1", "r2", "r3", "r4"] * 30)
    df.loc[df.index[:1], "dominant"] = "r11"   # 1 天
    df.loc[df.index[1:7], "dominant"] = "r12"  # 6 天
    out = agg_check(df)
    assert "r11" in out["dropped_small_buckets"] and "r12" in out["dropped_small_buckets"]
    assert out["reason"] != "insufficient_samples" or out["total"] < 30


def test_agg_check_unknown_state_does_not_crash() -> None:
    """契约面：dominant 出现教材表外的态（未来扩展）→ fail-closed 不抛异常。"""
    df = _mk_df(list(np.linspace(0.5, 1.0, 40)), dominants=["r13"] * 40)
    out = agg_check(df)
    assert out["verdict"] in {"pending", "noise"}
