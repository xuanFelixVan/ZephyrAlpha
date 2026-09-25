"""S2 criteria 验收测试：真 YAML 可载+DESIGN 原值/canonical sha256 可验/fail-closed。

生产 YAML 只读不写；形状变更测试写 tmp_path 副本（测试隔离铁律）。
"""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from zephyr.intelligence.switch_engine.criteria import (
    CRITERIA_ROOT_KEY,
    SwitchCriteriaError,
    criteria_sha256,
    freeze,
    load_criteria,
    original_trigger_values,
    verify_frozen,
)


def test_real_yaml_loads_and_matches_design_originals() -> None:
    """真 config/switch_criteria.yaml 只读核对：T1-T6 原值=DESIGN §②-C 提案值。"""
    payload = load_criteria()
    triggers = payload[CRITERIA_ROOT_KEY]["triggers"]
    originals = original_trigger_values()
    assert triggers["t2_disagreement_rate_max"] == originals["t2_disagreement_rate_max"]
    assert triggers["t3_perf_delta_pct_max"] == originals["t3_perf_delta_pct_max"]
    assert triggers["t3_consecutive_trading_days"] == originals["t3_consecutive_trading_days"]
    assert triggers["t4_cost_increase_pct_max"] == originals["t4_cost_increase_pct_max"]
    families = payload[CRITERIA_ROOT_KEY]["families"]
    assert families["code_module_low_medium"]["shadow_min_months"] == 1
    assert families["code_module_high"]["canary_min_months"] == 2  # high 域跨 2 结算周期


def test_sha256_deterministic_and_order_insensitive() -> None:
    a = {"x": 1, "y": {"b": 2, "a": 3}}
    b = {"y": {"a": 3, "b": 2}, "x": 1}
    assert criteria_sha256(a) == criteria_sha256(b)
    assert criteria_sha256(a) != criteria_sha256({"x": 2, "y": {"b": 2, "a": 3}})
    assert len(criteria_sha256(a)) == 64


def test_freeze_returns_registry_shape() -> None:
    frozen = freeze()
    assert set(frozen) == {"criteria_yaml_ref", "criteria_hash"}
    assert frozen["criteria_yaml_ref"].endswith("switch_criteria.yaml")
    assert verify_frozen(frozen["criteria_hash"]) is True


def test_verify_frozen_detects_drift(tmp_path: Path) -> None:
    base: dict = {
        "meta": {"criteria_version": "1.0"},
        CRITERIA_ROOT_KEY: {"t2_disagreement_rate_max": 0.05},
    }
    file_a = tmp_path / "a.yaml"
    file_a.write_text(yaml.safe_dump(base), encoding="utf-8")
    frozen = freeze(file_a)
    drifted = dict(base)
    drifted[CRITERIA_ROOT_KEY] = {"t2_disagreement_rate_max": 0.06}  # 判据改动
    file_b = tmp_path / "b.yaml"
    file_b.write_text(yaml.safe_dump(drifted), encoding="utf-8")
    assert verify_frozen(frozen["criteria_hash"], file_a) is True
    assert verify_frozen(frozen["criteria_hash"], file_b) is False


def test_missing_file_fails_closed(tmp_path: Path) -> None:
    with pytest.raises(SwitchCriteriaError, match="缺失"):
        load_criteria(tmp_path / "nope.yaml")


def test_bad_shape_fails_closed(tmp_path: Path) -> None:
    bad = tmp_path / "bad.yaml"
    bad.write_text(yaml.safe_dump({"meta": {}}), encoding="utf-8")
    with pytest.raises(SwitchCriteriaError, match="形状非法"):
        load_criteria(bad)
