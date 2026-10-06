# [TTL] permanent
# [BLUEPRINT] MOD-BT-FEXAM | tests/backtest/fexam/test_roster.py | roster 分类与计数对平单测
"""roster 单测：四册分类机判 + 计数字段（tmp_path 注入，禁写生产路径）。"""

from __future__ import annotations

import sys
from pathlib import Path

import yaml

FEXAM = Path(__file__).resolve().parents[3] / "scripts" / "backtest" / "fexam"
if str(FEXAM) not in sys.path:
    sys.path.insert(0, str(FEXAM))

from roster import (  # noqa: E402
    ALLOCATORS,
    PREREG_V1,
    classify_factor_outputs,
    classify_indicators,
    classify_strategies,
)


def _factor(fid: str, *, outputs=None, code_symbol=None, code_path=None, alg="pending_backtest"):
    return {
        "factor_id": fid,
        "outputs": outputs or [],
        "code_symbol": code_symbol,
        "code_path": code_path,
        "algorithm_status": alg,
        "factor_class": "momentum",
        "regime_valid": [],
        "status": "candidate",
    }


def test_factor_buckets():
    ch_backed = _factor("FCT-A-001", outputs=["ma_5"])
    code_backed = _factor("FCT-A-002", code_symbol="src/x.py::f", code_path="src/x.py")
    text_rule = _factor("FCT-A-003")
    cache: dict[str, set[str]] = {"c1_market.technical_indicator": {"ma_5"}}
    out = {r["object_id"]: r for r in classify_factor_outputs([ch_backed, code_backed, text_rule], cache=cache)}
    assert out["FCT-A-001"]["bucket"] == "ch_backed"
    assert out["FCT-A-001"]["ch_backings"] == ["c1_market.technical_indicator.ma_5"]
    assert out["FCT-A-002"]["bucket"] == "code_backed"
    assert out["FCT-A-003"]["bucket"] == "non_quantified"


def test_indicator_buckets():
    hit = {
        "indicator_id": "IND-TREND-001",
        "outputs": ["ma_5"],
        "indicator_class": "trend",
        "regime_valid": [],
        "regime_invalid": [],
        "status": "active",
    }
    miss = {
        "indicator_id": "IND-TREND-002",
        "outputs": ["no_such_col"],
        "indicator_class": "trend",
        "regime_valid": [],
        "regime_invalid": [],
        "status": "active",
    }
    cache: dict[str, set[str]] = {"c1_market.technical_indicator": {"ma_5"}}
    out = {r["object_id"]: r for r in classify_indicators([hit, miss], cache=cache)}
    assert out["IND-TREND-001"]["bucket"] == "ch_backed"
    assert out["IND-TREND-002"]["bucket"] == "col_missing"


def test_strategy_buckets():
    factor_map = {"FCT-A-001": {"bucket": "ch_backed", "ch_backings": ["c1_market.t.ma_5"]}}
    harness = {
        "strategy_id": "STR-A-001",
        "alpha_sources": ["FCT-A-001"],
        "universe_id": "UNI-1",
        "cost_model_id": "CST-1",
        "code_path": None,
    }
    code_only = {
        "strategy_id": "STR-A-002",
        "alpha_sources": [],
        "universe_id": "UNI-1",
        "cost_model_id": "CST-1",
        "code_path": "src/x.py",
    }
    empty = {
        "strategy_id": "STR-A-003",
        "alpha_sources": [],
        "universe_id": None,
        "cost_model_id": None,
        "code_path": None,
    }
    out = {r["object_id"]: r for r in classify_strategies([harness, code_only, empty], factor_map)}
    assert out["STR-A-001"]["bucket"] == "harness_examinable"
    assert out["STR-A-001"]["missing_recipe_flags"] == []
    assert out["STR-A-002"]["bucket"] == "code_backed"
    assert out["STR-A-003"]["bucket"] == "non_quantified"
    assert set(out["STR-A-003"]["missing_recipe_flags"]) == {
        "alpha_sources_empty",
        "universe_id_missing",
        "cost_model_id_missing",
    }


def test_prereg_frozen_fields():
    """prereg 判据字段存在性（判定器依赖契约，改名即红）。"""
    assert "windows" in PREREG_V1 and len(PREREG_V1["horizons"]) == 3
    assert PREREG_V1["factor_pass_line"]["abs_ic_min"] == 0.02
    assert len(ALLOCATORS) == 5
    variants = {a["variant"] for a in ALLOCATORS}
    assert variants == {"champion_combo", "challenger", "challenger_simplified"}
