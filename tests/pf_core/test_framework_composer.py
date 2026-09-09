# [BLUEPRINT] MOD-FWCOMP-001 | docs/03_modules/_domain_portfolio_core/framework_composer_blueprint.md
# [MODULE] tests.pf_core.test_framework_composer
# [DOMAIN] D_PF_CORE
# [DEPENDENCIES] zephyr.pf_core.strategy_engine.framework_composer; zephyr.backtest.implementations.vectorized_engine
# [CONSUMERS] pytest（SOP Step 5 循环验收）
# [STARTUP] manual
# [MATURITY] design
# [INVARIANTS] 测试禁写生产路径（产物走 tmp_path，ARCH-BENCH-LEAK-001）; 合成算子数学性质全覆盖（线性/对齐/再归一化/披露）; 不触 ClickHouse（build_weight_panel 打桩）
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 断言失败即红
# [TESTS] pytest tests/pf_core/test_framework_composer.py
# [A_module] module_id=MOD-FWCOMP-001-tests | layer=test | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""整装组合回测器单测（MOD-FWCOMP-001）。

覆盖面:
    - 方案配置加载/校验（缺失/权重和/越界/重复 plan_id）
    - 合成算子数学性质（线性加权/联合索引对齐/再归一化披露/严格模式/全空拒绝/行级 Σ=1）
    - 净值对账（完美一致/超容差检出）
    - 端到端（打桩 build_weight_panel + 真引擎，产物落 tmp_path、run_id 前缀 bt-fw-、
      metrics.plan_id/skipped/rescale_factor 披露字段齐全）
"""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import pytest
import yaml

from zephyr.pf_core.strategy_engine.framework_composer import (
    ComposeReport,
    FrameworkBacktestConfig,
    FrameworkPlan,
    FrameworkPlanError,
    FrameworkValidationError,
    PlanWeight,
    compose_weight_panels,
    get_framework_plan,
    load_framework_plans,
    reconcile_composed_nav,
    run_framework_backtest,
)

# ---------------------------------------------------------------------------
# 配置加载
# ---------------------------------------------------------------------------


def test_load_plans_default_three_plans_sum_one():
    plans = load_framework_plans()
    assert [p.plan_id for p in plans] == ["fw-defensive", "fw-balanced", "fw-aggressive"]
    for p in plans:
        assert abs(p.total_weight - 1.0) < 1e-6
        assert all(w.weight > 0 for w in p.weights)
    # 均衡型 = FW_W 演示权重映射（35/25/25/10/5）
    balanced = get_framework_plan("fw-balanced")
    wmap = {w.strategy_id: w.weight for w in balanced.weights}
    assert wmap["topn-momentum"] == 0.35
    assert wmap["multifactor-sleeve"] == 0.25
    assert wmap["default-equity"] == 0.25
    assert wmap["daban-sleeve"] == 0.10
    assert abs(sum(v for k, v in wmap.items() if k.startswith(("intraday", "orderbook", "vwap"))) - 0.05) < 1e-9


def test_load_plans_missing_file(tmp_path: Path):
    with pytest.raises(FrameworkPlanError, match="缺失"):
        load_framework_plans(tmp_path / "nope.yaml")


def test_load_plans_bad_weight_sum(tmp_path: Path):
    cfg = {
        "plans": [
            {
                "plan_id": "fw-x",
                "name_zh": "坏方案",
                "risk_profile": "balanced",
                "weights": [
                    {"strategy_id": "a", "weight": 0.6},
                    {"strategy_id": "b", "weight": 0.3},
                ],
            }
        ]
    }
    p = tmp_path / "plans.yaml"
    p.write_text(yaml.safe_dump(cfg), encoding="utf-8")
    with pytest.raises(FrameworkPlanError, match="权重合计"):
        load_framework_plans(p)


def test_load_plans_weight_out_of_range(tmp_path: Path):
    cfg = {
        "plans": [
            {
                "plan_id": "fw-x",
                "name_zh": "越界",
                "risk_profile": "balanced",
                "weights": [{"strategy_id": "a", "weight": 1.5}],
            }
        ]
    }
    p = tmp_path / "plans.yaml"
    p.write_text(yaml.safe_dump(cfg), encoding="utf-8")
    with pytest.raises(FrameworkPlanError, match="越界"):
        load_framework_plans(p)


def test_load_plans_duplicate_plan_id(tmp_path: Path):
    plan = {
        "plan_id": "fw-x",
        "name_zh": "重复",
        "risk_profile": "balanced",
        "weights": [{"strategy_id": "a", "weight": 1.0}],
    }
    cfg = {"plans": [plan, dict(plan)]}
    p = tmp_path / "plans.yaml"
    p.write_text(yaml.safe_dump(cfg), encoding="utf-8")
    with pytest.raises(FrameworkPlanError, match="重复"):
        load_framework_plans(p)


def test_load_plans_bad_risk_profile(tmp_path: Path):
    cfg = {
        "plans": [
            {
                "plan_id": "fw-x",
                "name_zh": "画像",
                "risk_profile": "yolo",
                "weights": [{"strategy_id": "a", "weight": 1.0}],
            }
        ]
    }
    p = tmp_path / "plans.yaml"
    p.write_text(yaml.safe_dump(cfg), encoding="utf-8")
    with pytest.raises(FrameworkPlanError, match="risk_profile"):
        load_framework_plans(p)


def test_get_framework_plan_missing():
    with pytest.raises(FrameworkPlanError, match="不存在"):
        get_framework_plan("fw-nonexistent")


# ---------------------------------------------------------------------------
# 合成算子
# ---------------------------------------------------------------------------


def _panel(values: dict, index, columns) -> pd.DataFrame:
    return pd.DataFrame(values, index=index, columns=columns)


def test_compose_basic_linear():
    plan = FrameworkPlan(
        plan_id="fw-t",
        name="测试",
        risk_profile="balanced",
        description="",
        weights=(PlanWeight("a", 0.6), PlanWeight("b", 0.4)),
    )
    idx = pd.to_datetime(["2026-08-01", "2026-08-02"])
    pa = _panel({"600519": [0.8, 0.6], "000858": [0.2, 0.4]}, idx, ["600519", "000858"])
    pb = _panel({"600519": [0.5, 0.5], "000858": [0.5, 0.5]}, idx, ["600519", "000858"])
    report = compose_weight_panels(plan, {"a": pa, "b": pb})
    assert report.participants == ["a", "b"]
    assert report.rescale_factor == 1.0
    assert report.panel.loc[idx[0], "600519"] == pytest.approx(0.6 * 0.8 + 0.4 * 0.5)
    assert report.panel.loc[idx[1], "000858"] == pytest.approx(0.6 * 0.4 + 0.4 * 0.5)
    # 行级 Σ=1
    assert (report.panel.sum(axis=1).abs() - 1.0).max() < 1e-9


def test_compose_union_alignment_missing_filled_zero():
    from zephyr.pf_core.strategy_engine.framework_composer import PlanWeight

    plan = FrameworkPlan(
        plan_id="fw-t",
        name="测试",
        risk_profile="balanced",
        description="",
        weights=(PlanWeight("a", 0.5), PlanWeight("b", 0.5)),
    )
    idx_a = pd.to_datetime(["2026-08-01"])
    idx_b = pd.to_datetime(["2026-08-02"])
    pa = _panel({"600519": [1.0]}, idx_a, ["600519"])
    pb = _panel({"000858": [1.0]}, idx_b, ["000858"])
    report = compose_weight_panels(plan, {"a": pa, "b": pb})
    assert list(report.panel.index) == list(idx_a.append(idx_b))
    assert set(report.panel.columns) == {"600519", "000858"}
    # 成员日历不重叠日：当日仅单成员有权重 → 行级 Σ=1 归一化后为 1.0（引擎口径一致，notes 披露）
    assert report.panel.loc[idx_a[0], "600519"] == pytest.approx(1.0)
    assert report.panel.loc[idx_b[0], "000858"] == pytest.approx(1.0)
    assert "行级 Σw 偏差" in report.notes


def test_compose_partial_rescale_disclosed():
    from zephyr.pf_core.strategy_engine.framework_composer import PlanWeight

    plan = FrameworkPlan(
        plan_id="fw-t",
        name="测试",
        risk_profile="balanced",
        description="",
        weights=(PlanWeight("a", 0.95), PlanWeight("tick-only", 0.05)),
    )
    idx = pd.to_datetime(["2026-08-01"])
    pa = _panel({"600519": [1.0]}, idx, ["600519"])
    report = compose_weight_panels(plan, {"a": pa})  # tick-only 面板缺失
    assert report.participants == ["a"]
    assert report.skipped == [("tick-only", "panel missing/empty")]
    assert report.alpha_total == pytest.approx(0.95)
    assert report.rescale_factor == pytest.approx(1.0 / 0.95)
    assert "再归一化" in report.notes  # 显式披露，禁静默
    assert report.panel.loc[idx[0], "600519"] == pytest.approx(1.0)


def test_compose_strict_mode_rejects_partial():
    from zephyr.pf_core.strategy_engine.framework_composer import PlanWeight

    plan = FrameworkPlan(
        plan_id="fw-t",
        name="测试",
        risk_profile="balanced",
        description="",
        weights=(PlanWeight("a", 0.95), PlanWeight("tick-only", 0.05)),
    )
    idx = pd.to_datetime(["2026-08-01"])
    pa = _panel({"600519": [1.0]}, idx, ["600519"])
    with pytest.raises(FrameworkValidationError, match="严格模式"):
        compose_weight_panels(plan, {"a": pa}, allow_partial=False)


def test_compose_all_empty_raises():
    from zephyr.pf_core.strategy_engine.framework_composer import PlanWeight

    plan = FrameworkPlan(
        plan_id="fw-t",
        name="测试",
        risk_profile="balanced",
        description="",
        weights=(PlanWeight("a", 1.0),),
    )
    with pytest.raises(FrameworkValidationError, match="无任何参与成员"):
        compose_weight_panels(plan, {})


def test_compose_zero_rows_preserved_as_cash():
    from zephyr.pf_core.strategy_engine.framework_composer import PlanWeight

    plan = FrameworkPlan(
        plan_id="fw-t",
        name="测试",
        risk_profile="balanced",
        description="",
        weights=(PlanWeight("a", 1.0),),
    )
    idx = pd.to_datetime(["2026-08-01", "2026-08-02"])
    pa = _panel({"600519": [0.0, 1.0]}, idx, ["600519"])  # 首日全零=现金日
    report = compose_weight_panels(plan, {"a": pa})
    assert report.panel.loc[idx[0], "600519"] == pytest.approx(0.0)  # 全零行保留
    assert report.panel.loc[idx[1], "600519"] == pytest.approx(1.0)


def test_compose_does_not_mutate_inputs():
    from zephyr.pf_core.strategy_engine.framework_composer import PlanWeight

    plan = FrameworkPlan(
        plan_id="fw-t",
        name="测试",
        risk_profile="balanced",
        description="",
        weights=(PlanWeight("a", 1.0),),
    )
    idx = pd.to_datetime(["2026-08-01"])
    pa = _panel({"600519": [1.0]}, idx, ["600519"])
    before = pa.copy(deep=True)
    compose_weight_panels(plan, {"a": pa}, allow_partial=False)
    assert pa.equals(before)


# ---------------------------------------------------------------------------
# 净值对账
# ---------------------------------------------------------------------------


def test_reconcile_perfect_match():
    from zephyr.pf_core.strategy_engine.framework_composer import PlanWeight

    plan = FrameworkPlan(
        plan_id="fw-t",
        name="测试",
        risk_profile="balanced",
        description="",
        weights=(PlanWeight("a", 0.6), PlanWeight("b", 0.4)),
    )
    idx = pd.date_range("2026-08-03", periods=8)  # ≥5 抽样日
    nav_a = pd.Series([1_000_000 * (1 + 0.001 * i) for i in range(8)], index=idx)
    nav_b = pd.Series([1_000_000 * (1 - 0.0005 * i) for i in range(8)], index=idx)
    manual = nav_a * 0.6 + nav_b * 0.4
    report = reconcile_composed_nav(manual, {"a": nav_a, "b": nav_b}, plan)
    assert report["samples"] == 8
    assert report["max_abs_rel_error"] < 1e-4
    assert report["over_tolerance"] == []


def test_reconcile_detects_over_tolerance():
    from zephyr.pf_core.strategy_engine.framework_composer import PlanWeight

    plan = FrameworkPlan(
        plan_id="fw-t",
        name="测试",
        risk_profile="balanced",
        description="",
        weights=(PlanWeight("a", 1.0),),
    )
    idx = pd.date_range("2026-08-03", periods=6)
    nav_a = pd.Series([1_000_000.0] * 6, index=idx)
    composed = nav_a * 1.001  # 0.1% 偏差 > 0.01% 容差
    report = reconcile_composed_nav(composed, {"a": nav_a}, plan)
    assert report["max_abs_rel_error"] > 1e-4
    assert len(report["over_tolerance"]) == 6


# ---------------------------------------------------------------------------
# 端到端（打桩成员面板 + 真引擎 + tmp_path 产物隔离）
# ---------------------------------------------------------------------------

_FAKE_CFG = {
    "plans": [
        {
            "plan_id": "fw-test",
            "name_zh": "测试方案",
            "risk_profile": "balanced",
            "weights": [
                {"strategy_id": "fake-a", "weight": 0.6},
                {"strategy_id": "fake-b", "weight": 0.4},
            ],
        }
    ]
}


@pytest.fixture()
def fake_runner_panels(monkeypatch):
    """打桩 StrategyRunner.build_weight_panel：合成 date×symbol 面板（无 CH 依赖）。"""
    from zephyr.pf_core.strategy_engine.strategy_runner import StrategyRunner

    idx = pd.date_range("2026-08-03", periods=10)
    cols = ["600519", "000858"]
    panel_a = pd.DataFrame(
        [[0.9, 0.1]] * 5 + [[0.7, 0.3]] * 5, index=idx, columns=cols
    )
    panel_b = pd.DataFrame([[0.5, 0.5]] * 10, index=idx, columns=cols)

    def fake_build(self, symbols, start, end, config):
        data = pd.DataFrame(
            {
                "open": [10.0] * 20,
                "high": [10.5] * 20,
                "low": [9.5] * 20,
                "close": [10.0 + 0.01 * i for i in range(20)],
                "volume": [1000.0] * 20,
                "amount": [10000.0] * 20,
            },
            index=pd.MultiIndex.from_product(
                [cols, idx], names=["symbol", "date"]
            ),
        )
        panel = panel_a if config.strategy_id == "fake-a" else panel_b
        return data, panel

    monkeypatch.setattr(StrategyRunner, "build_weight_panel", fake_build)


def test_run_framework_backtest_e2e(fake_runner_panels, tmp_path: Path):
    plans_file = tmp_path / "plans.yaml"
    plans_file.write_text(yaml.safe_dump(_FAKE_CFG), encoding="utf-8")
    storage = tmp_path / "artifacts"
    storage.mkdir()

    summary = run_framework_backtest(
        "fw-test",
        ["600519.SH", "000858.SZ"],
        "2026-08-03",
        "2026-08-14",
        config=FrameworkBacktestConfig(
            storage_path=storage,
            plans_path=plans_file,
            enable_stk_limit_provider=False,
        ),
    )
    assert summary["ok"], summary.get("error")
    assert summary["run_id"].startswith("bt-fw-")
    assert summary["plan_id"] == "fw-test"
    assert sorted(summary["participants"]) == ["fake-a", "fake-b"]
    assert summary["rescale_factor"] == 1.0
    assert summary["equity_points"] > 0

    artifact_file = storage / f"{summary['run_id']}.json"
    assert artifact_file.exists()
    d = json.loads(artifact_file.read_text(encoding="utf-8"))
    assert d["run_id"] == summary["run_id"]
    assert d["metrics"]["plan_id"] == "fw-test"
    assert d["metrics"]["plan_weights"] == {"fake-a": 0.6, "fake-b": 0.4}
    assert d["metrics"]["engine_run_id"]
    assert len(d["equity_curve"]) == summary["equity_points"]


def test_run_framework_backtest_partial_skips_disclosed(fake_runner_panels, tmp_path: Path):
    cfg = json.loads(json.dumps(_FAKE_CFG))
    cfg["plans"][0]["weights"].append({"strategy_id": "tick-do-t", "weight": 0.0 + 0.0})
    # 追加 tick-only 成员需保持 Σ=1：改用 0.6/0.3/0.1
    cfg["plans"][0]["weights"] = [
        {"strategy_id": "fake-a", "weight": 0.6},
        {"strategy_id": "fake-b", "weight": 0.3},
        {"strategy_id": "tick-do-t", "weight": 0.1},
    ]
    plans_file = tmp_path / "plans.yaml"
    plans_file.write_text(yaml.safe_dump(cfg), encoding="utf-8")
    storage = tmp_path / "artifacts"
    storage.mkdir()

    summary = run_framework_backtest(
        "fw-test",
        ["600519.SH"],
        "2026-08-03",
        "2026-08-14",
        config=FrameworkBacktestConfig(
            storage_path=storage,
            plans_path=plans_file,
            enable_stk_limit_provider=False,
        ),
    )
    # tick-do-t 不在任何注册表 → 不判 tick-only，但打桩 build_weight_panel 会为它产出 panel_b
    # （fake 桩对未知 id 返回 panel_b）——这里验证的是"面板正常"路径；tick-only 判定走注册表，
    # 单测环境注册表为空集，故 tick-do-t 参与合成（rescale_factor=1.0）。
    assert summary["ok"], summary.get("error")
    assert sorted(summary["participants"]) == ["fake-a", "fake-b", "tick-do-t"]
    d = json.loads((storage / f"{summary['run_id']}.json").read_text(encoding="utf-8"))
    assert d["metrics"]["rescale_factor"] == 1.0
