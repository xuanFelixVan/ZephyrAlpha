# MOD-POS-029 仓位配方编译器测试
# 验收锚：立项稿 §十 数字断言（362,880 / 11,612,160）+ 折叠/确定性/fail-closed 三铁律
import importlib.util
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[2]
_SCHEMA = _REPO / "config" / "position_recipe_grid_schema.yaml"
_spec = importlib.util.spec_from_file_location(
    "position_recipe_compiler",
    _REPO / "src" / "zephyr" / "position" / "core" / "position_recipe_compiler.py",
)
_mod = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = _mod
_spec.loader.exec_module(_mod)

GridCompiler = _mod.GridCompiler
InvalidGridSchemaError = _mod.InvalidGridSchemaError

DEFAULT_CONTEXT = {"strategy_pool": ["primary"], "phase": 1, "capital_ramp_enabled": False}


def _small(**overrides) -> GridCompiler:
    specs = [
        {"id": "s", "values": ["a", "b"], "baseline": "a", "cost_tier": "signal_side"},
        {"id": "w", "values": ["u", "v", "t"], "baseline": "u"},
        {
            "id": "F",
            "values": ["single", "eq_cap", "eq_risk", "additive"],
            "baseline": "single",
            "active_if": "len(strategy_pool) > 1",
        },
    ]
    for spec in specs:
        spec.update(overrides)
    return GridCompiler.from_dimensions(specs)


def test_full_active_expansion_counts_cartesian() -> None:
    exp = _small().compile({"strategy_pool": ["x", "y"]})
    assert exp.n_raw == 2 * 3 * 4
    assert exp.folded_dimensions == {}


def test_inactive_dimension_folds_to_baseline_and_counts_one() -> None:
    exp = _small().compile({"strategy_pool": ["only"]})
    assert exp.n_raw == 2 * 3  # F 失活 → 贡献 1，不贡献 4
    assert all(r.values["F"] == "single" for r in exp.recipes)
    assert exp.folded_dimensions == {"F": "single"}
    assert all(r.folded_dimensions["F"] == "single" for r in exp.recipes)
    assert "F" not in exp.active_dimensions


def test_recipe_id_is_content_addressed_and_deterministic() -> None:
    c = _small()
    ids_a = {r.recipe_id for r in c.compile({"strategy_pool": ["only"]}).recipes}
    ids_b = {r.recipe_id for r in c.compile({"strategy_pool": ["only"]}).recipes}
    assert ids_a == ids_b and len(ids_a) == 6
    # 同取值不同折叠路径不产生同 id 冲突（F 展开时 single 取值独立成行）
    ids_c = {r.recipe_id for r in c.compile({"strategy_pool": ["p", "q"]}).recipes}
    assert len(ids_c) == 24


def test_predicate_unknown_variable_fails_closed() -> None:
    with pytest.raises(InvalidGridSchemaError, match="求值失败"):
        _small().compile({})  # 谓词引用 strategy_pool，context 未提供


def test_baseline_must_be_in_values() -> None:
    with pytest.raises(InvalidGridSchemaError, match="baseline"):
        GridCompiler.from_dimensions(
            [{"id": "x", "values": ["a"], "baseline": "ghost"}]
        )


def test_dependency_cycle_rejected() -> None:
    with pytest.raises(InvalidGridSchemaError, match="成环"):
        GridCompiler.from_dimensions(
            [
                {"id": "x", "values": ["a", "b"], "baseline": "a", "depends_on": ["y"]},
                {"id": "y", "values": ["a", "b"], "baseline": "a", "depends_on": ["x"]},
            ]
        )


def test_undeclared_dependency_rejected() -> None:
    with pytest.raises(InvalidGridSchemaError, match="依赖未声明维"):
        GridCompiler.from_dimensions(
            [{"id": "x", "values": ["a"], "baseline": "a", "depends_on": ["ghost"]}]
        )


def test_prefix_key_groups_signal_side_only() -> None:
    c = _small()
    exp = c.compile({"strategy_pool": ["p", "q"]})
    by_id = {r.values["s"] + r.values["w"] + r.values["F"]: r for r in exp.recipes}
    # 同 signal 侧（s）不同 weight 侧（w）→ prefix_key 相同
    assert by_id["a" + "u" + "single"].prefix_key == by_id["a" + "v" + "single"].prefix_key
    # signal 侧不同 → prefix_key 不同
    assert by_id["a" + "u" + "single"].prefix_key != by_id["b" + "u" + "single"].prefix_key


def test_count_n_raw_matches_expansion() -> None:
    c = _small()
    assert c.count_n_raw({"strategy_pool": ["only"]}) == len(
        c.compile({"strategy_pool": ["only"]}).recipes
    )
    assert c.count_n_raw({"strategy_pool": ["a", "b", "c"]}) == len(
        c.compile({"strategy_pool": ["a", "b", "c"]}).recipes
    )


def test_estimate_max_z_matches_official_calculator() -> None:
    from zephyr.simulation.deflated_sharpe_calculator import (
        DeflatedSharpeCalculator,
        DSRResult,  # noqa: F401 保证模块可导入
    )

    calc = DeflatedSharpeCalculator()
    for n in (2, 35, 362880):
        official = calc.calculate([0.01, -0.01, 0.02], num_trials=n).expected_max
        assert abs(_mod.GridCompiler.from_dimensions(
            [{"id": "x", "values": ["a"], "baseline": "a"}]
        ).estimate_max_z(n) - official) < 1e-12


def test_charter_v2_schema_nominal_counts() -> None:
    """立项稿 §十 验收锚：默认 context 折叠 F/J/K = 362,880；全激活 = 11,612,160。"""
    assert _SCHEMA.exists(), f"schema 真源缺失: {_SCHEMA}"
    c = GridCompiler.from_yaml(_SCHEMA)
    n_folded = c.count_n_raw(DEFAULT_CONTEXT)
    assert n_folded == 362880, f"立项稿 §十 名义 N 不符: {n_folded}"
    full = dict(DEFAULT_CONTEXT, strategy_pool=["a", "b"], phase=2, capital_ramp_enabled=True)
    n_full = c.count_n_raw(full)
    assert n_full == 362880 * 4 * 2 * 4, f"全激活 N 不符: {n_full}"
    exp = c.compile(DEFAULT_CONTEXT)
    assert exp.n_raw == n_folded
    assert set(exp.folded_dimensions) == {
        "F_merge_policy",
        "I_cost_tier",
        "J_regime_switch",
        "K_capital_ramp",
    }


def test_yaml_missing_dimensions_key_rejected(tmp_path) -> None:
    p = tmp_path / "bad.yaml"
    p.write_text("schema_id: x\n", encoding="utf-8")
    with pytest.raises(InvalidGridSchemaError):
        GridCompiler.from_yaml(p)
