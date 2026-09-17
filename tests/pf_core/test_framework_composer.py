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
    per_regime_summary,
    reconcile_composed_nav,
    run_framework_backtest,
    verify_weight_panel_identity,
)

# ---------------------------------------------------------------------------
# 配置加载
# ---------------------------------------------------------------------------


def test_load_plans_default_three_plans_sum_one():
    """三套人工预设钉死在前；fw-tdm-current=生成器产物（S11/C3，scripts/backtest/
    generate_framework_plan_from_tdm.py 管养），允许追加但禁手工改权重。"""
    plans = load_framework_plans()
    assert [p.plan_id for p in plans[:3]] == ["fw-defensive", "fw-balanced", "fw-aggressive"]
    assert all(p.plan_id != "fw-tdm-current" for p in plans[:3])  # 生成块不抢预设位
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


# ---------------------------------------------------------------------------
# 三期 regime 动态权重联动（α_i(t) 查表——配置解析/动态合成/回退锚/摘要）
# ---------------------------------------------------------------------------


def test_load_plans_real_config_regime_overrides():
    """真源配置三套方案 regime_overrides 全量可解析：Σ=1、成员集合=基准、回退语义正确。"""
    for pid in ("fw-defensive", "fw-balanced", "fw-aggressive"):
        plan = get_framework_plan(pid)
        assert plan.regime_overrides, f"{pid} 缺 regime_overrides"
        base_map = {w.strategy_id: w.weight for w in plan.weights}
        for state, oweights in plan.regime_overrides:
            assert abs(sum(w.weight for w in oweights) - 1.0) < 1e-6
            assert {w.strategy_id for w in oweights} == set(base_map)
        # 未覆盖 regime（r1 低波震荡在三套方案均未覆盖）→ 回退基准
        eff = plan.effective_weights("r1")
        assert {w.strategy_id: w.weight for w in eff} == base_map
        # None → 基准
        assert plan.effective_weights(None) == plan.weights
    # 均衡型 r3 覆盖表抽样：打板上调至 0.15
    balanced = get_framework_plan("fw-balanced")
    r3_map = {w.strategy_id: w.weight for w in balanced.effective_weights("r3")}
    assert r3_map["daban-sleeve"] == 0.15
    assert r3_map["topn-momentum"] == 0.40


def test_load_plans_regime_override_bad_state_key(tmp_path: Path):
    cfg = {
        "plans": [
            {
                "plan_id": "fw-x",
                "name_zh": "坏键",
                "risk_profile": "balanced",
                "weights": [{"strategy_id": "a", "weight": 1.0}],
                "regime_overrides": {
                    "r99": [{"strategy_id": "a", "weight": 1.0}],  # r99 不在 7 态
                },
            }
        ]
    }
    p = tmp_path / "plans.yaml"
    p.write_text(yaml.safe_dump(cfg), encoding="utf-8")
    with pytest.raises(FrameworkPlanError, match="键非法"):
        load_framework_plans(p)


def test_load_plans_regime_override_member_mismatch(tmp_path: Path):
    cfg = {
        "plans": [
            {
                "plan_id": "fw-x",
                "name_zh": "成员漂移",
                "risk_profile": "balanced",
                "weights": [{"strategy_id": "a", "weight": 1.0}],
                "regime_overrides": {
                    "r3": [{"strategy_id": "b", "weight": 1.0}],  # 成员≠基准
                },
            }
        ]
    }
    p = tmp_path / "plans.yaml"
    p.write_text(yaml.safe_dump(cfg), encoding="utf-8")
    with pytest.raises(FrameworkPlanError, match="成员集合"):
        load_framework_plans(p)


def test_load_plans_regime_override_bad_sum(tmp_path: Path):
    cfg = {
        "plans": [
            {
                "plan_id": "fw-x",
                "name_zh": "覆盖表Σ≠1",
                "risk_profile": "balanced",
                "weights": [
                    {"strategy_id": "a", "weight": 0.6},
                    {"strategy_id": "b", "weight": 0.4},
                ],
                "regime_overrides": {
                    "r3": [
                        {"strategy_id": "a", "weight": 0.7},
                        {"strategy_id": "b", "weight": 0.2},  # Σ=0.9
                    ],
                },
            }
        ]
    }
    p = tmp_path / "plans.yaml"
    p.write_text(yaml.safe_dump(cfg), encoding="utf-8")
    with pytest.raises(FrameworkPlanError, match="权重合计"):
        load_framework_plans(p)


def _two_regime_plan() -> FrameworkPlan:
    """两 regime 日序验证 α_i(t) 切换的标准方案：基准 a=0.6/b=0.4；r3 覆盖 a=0.9/b=0.1。"""
    return FrameworkPlan(
        plan_id="fw-dyn",
        name="动态测试",
        risk_profile="balanced",
        description="",
        weights=(PlanWeight("a", 0.6), PlanWeight("b", 0.4)),
        regime_overrides=(("r3", (PlanWeight("a", 0.9), PlanWeight("b", 0.1))),),
    )


def test_compose_dynamic_alpha_switch_two_regimes():
    """动态查表正确性：两 regime 日序逐日切换 α_i(t)，Σw=1 恒成立。"""
    plan = _two_regime_plan()
    idx = pd.to_datetime(["2026-08-03", "2026-08-04", "2026-08-05"])
    pa = _panel({"600519": [0.8, 0.8, 0.8], "000858": [0.2, 0.2, 0.2]}, idx, ["600519", "000858"])
    pb = _panel({"600519": [0.5, 0.5, 0.5], "000858": [0.5, 0.5, 0.5]}, idx, ["600519", "000858"])
    regime = {"2026-08-03": "r3", "2026-08-04": "r4", "2026-08-05": "r3"}
    report = compose_weight_panels(plan, {"a": pa, "b": pb}, regime_by_date=regime)
    # r3 日: 0.9*0.8+0.1*0.5=0.77；r4 日（未覆盖→基准）: 0.6*0.8+0.4*0.5=0.68
    assert report.panel.loc[idx[0], "600519"] == pytest.approx(0.9 * 0.8 + 0.1 * 0.5)
    assert report.panel.loc[idx[1], "600519"] == pytest.approx(0.6 * 0.8 + 0.4 * 0.5)
    assert report.panel.loc[idx[2], "600519"] == pytest.approx(0.77)
    # Σw=1 恒成立
    assert (report.panel.sum(axis=1).abs() - 1.0).max() < 1e-9
    # 分组披露：r3 两日（r4 未覆盖归 __base__ 一日）
    assert report.regime_day_counts == {"r3": 2, "__base__": 1}
    assert "regime 动态合成" in report.notes


def test_compose_dynamic_fallback_equals_static_bitwise():
    """回退锚：regime 序全为未覆盖状态/缺日期时，动态结果与静态（二期）逐位一致。"""
    plan = _two_regime_plan()
    idx = pd.to_datetime(["2026-08-03", "2026-08-04", "2026-08-05"])
    pa = _panel({"600519": [0.8, 0.6, 0.4], "000858": [0.2, 0.4, 0.6]}, idx, ["600519", "000858"])
    pb = _panel({"600519": [0.5, 0.5, 0.5], "000858": [0.5, 0.5, 0.5]}, idx, ["600519", "000858"])
    static_report = compose_weight_panels(plan, {"a": pa, "b": pb})
    # r1 不在覆盖表 + 08-05 无 regime 条目 → 全部回退基准
    dyn_report = compose_weight_panels(
        plan, {"a": pa, "b": pb}, regime_by_date={"2026-08-03": "r1", "2026-08-04": "r2"}
    )
    pd.testing.assert_frame_equal(dyn_report.panel, static_report.panel)
    assert dyn_report.regime_day_counts == {"__base__": 3}


def test_compose_dynamic_invalid_state_rejected():
    """非法 regime 状态 fail-closed 拒绝（regime 错=权重错，禁静默回退）。"""
    plan = _two_regime_plan()
    idx = pd.to_datetime(["2026-08-03"])
    pa = _panel({"600519": [1.0]}, idx, ["600519"])
    with pytest.raises(FrameworkValidationError, match="状态非法"):
        compose_weight_panels(plan, {"a": pa}, regime_by_date={"2026-08-03": "r99"})


def test_compose_dynamic_empty_series_rejected():
    plan = _two_regime_plan()
    idx = pd.to_datetime(["2026-08-03"])
    pa = _panel({"600519": [1.0]}, idx, ["600519"])
    with pytest.raises(FrameworkValidationError, match="日序为空"):
        compose_weight_panels(plan, {"a": pa}, regime_by_date={})


def test_compose_dynamic_per_group_rescale_disclosed():
    """动态模式 tick-only 跳过后各组独立显式再归一化（禁静默）。"""
    plan = FrameworkPlan(
        plan_id="fw-dyn-partial",
        name="动态部分成员",
        risk_profile="balanced",
        description="",
        weights=(PlanWeight("a", 0.95), PlanWeight("tick-only", 0.05)),
        regime_overrides=(("r3", (PlanWeight("a", 0.90), PlanWeight("tick-only", 0.10))),),
    )
    idx = pd.to_datetime(["2026-08-03", "2026-08-04"])
    pa = _panel({"600519": [1.0, 1.0]}, idx, ["600519"])
    # tick-only 面板缺失 → 参与者仅 a：r3 组 α=0.90（×1/0.9），__base__ 组 α=0.95（×1/0.95）
    report = compose_weight_panels(plan, {"a": pa}, regime_by_date={"2026-08-03": "r3"})
    assert report.panel.loc[idx[0], "600519"] == pytest.approx(1.0)
    assert report.panel.loc[idx[1], "600519"] == pytest.approx(1.0)
    assert report.regime_rescale_factors["r3"] == pytest.approx(1.0 / 0.90)
    assert report.regime_rescale_factors["__base__"] == pytest.approx(1.0 / 0.95)
    assert report.alpha_total == pytest.approx(0.90)  # 最坏组口径
    assert report.regime_day_counts == {"r3": 1, "__base__": 1}


def test_per_regime_summary_math():
    """per-regime 分段摘要手算对账：链式贡献收益 + 段内 running-peak 回撤。"""
    plan = _two_regime_plan()  # 仅覆盖 r3
    equity_curve = [
        {"timestamp": "2026-08-03", "equity": 1_000_000.0},  # r3
        {"timestamp": "2026-08-04", "equity": 1_010_000.0},  # r3
        {"timestamp": "2026-08-05", "equity": 990_000.0},  # r4→__base__
        {"timestamp": "2026-08-06", "equity": 1_002_000.0},  # 无 regime 条目→__base__
    ]
    regime = {"2026-08-03": "r3", "2026-08-04": "r3", "2026-08-05": "r4"}
    rows = per_regime_summary(plan, equity_curve, regime)
    by_regime = {r["regime"]: r for r in rows}
    assert by_regime["r3"]["days"] == 2
    assert by_regime["r3"]["return_pct"] == pytest.approx(1.0)  # ×1.01-1
    assert by_regime["r3"]["max_drawdown_pct"] == 0.0
    assert by_regime["__base__"]["days"] == 2
    # 990000/1010000 × 1002000/990000 = 1002000/1010000 → +1.2121% 链式贡献
    assert by_regime["__base__"]["return_pct"] == pytest.approx((1002000 / 1010000 - 1) * 100, abs=1e-3)
    # 段内回撤: 990000（起点）→1002000（升）无回撤
    assert by_regime["__base__"]["max_drawdown_pct"] == 0.0


def test_run_framework_backtest_dynamic_e2e(fake_runner_panels, tmp_path: Path):
    """端到端动态回测：regime 日序入参 → 产物 metrics 披露 + per-regime 摘要产出。"""
    cfg = json.loads(json.dumps(_FAKE_CFG))
    cfg["plans"][0]["regime_overrides"] = {
        "r3": [
            {"strategy_id": "fake-a", "weight": 0.8},
            {"strategy_id": "fake-b", "weight": 0.2},
        ]
    }
    plans_file = tmp_path / "plans.yaml"
    plans_file.write_text(yaml.safe_dump(cfg), encoding="utf-8")
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
            regime_by_date={"2026-08-04": "r3", "2026-08-05": "r3"},
        ),
    )
    assert summary["ok"], summary.get("error")
    assert summary["dynamic"] is True
    # 面板 10 日（08-03..08-12）：r3 两日 + 回退八日
    assert summary["regime_day_counts"] == {"r3": 2, "__base__": 8}
    assert summary["per_regime"]
    assert {r["regime"] for r in summary["per_regime"]} <= {"r3", "__base__"}
    d = json.loads((storage / f"{summary['run_id']}.json").read_text(encoding="utf-8"))
    assert d["metrics"]["dynamic"] is True
    assert d["metrics"]["regime_day_counts"] == {"r3": 2, "__base__": 8}
    assert d["metrics"]["plan_regime_overrides"]["r3"] == {"fake-a": 0.8, "fake-b": 0.2}


def test_run_framework_backtest_static_backward_compat_keys(fake_runner_panels, tmp_path: Path):
    """向后兼容锚：静态模式响应含三期新键（dynamic=False/空 dict/空 list），二期消费方零漂移。"""
    plans_file = tmp_path / "plans.yaml"
    plans_file.write_text(yaml.safe_dump(_FAKE_CFG), encoding="utf-8")
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
    assert summary["ok"], summary.get("error")
    assert summary["dynamic"] is False
    assert summary["regime_day_counts"] == {}
    assert summary["per_regime"] == []
    d = json.loads((storage / f"{summary['run_id']}.json").read_text(encoding="utf-8"))
    assert "dynamic" not in d["metrics"]  # 静态产物不加键，二期产物 schema 零漂移


# ---------------------------------------------------------------------------
# 面板级对账（tracker #275 定案口径①：独立复算逐位硬验收）
# ---------------------------------------------------------------------------


def test_verify_panel_identity_static_within_tolerance():
    """静态模式：独立复算与合成面板逐位一致（≤1e-9）。"""
    plan = _two_regime_plan()
    idx = pd.to_datetime(["2026-08-03", "2026-08-04"])
    pa = _panel({"600519": [0.8, 0.6], "000858": [0.2, 0.4]}, idx, ["600519", "000858"])
    pb = _panel({"600519": [0.5, 0.5], "000858": [0.5, 0.5]}, idx, ["600519", "000858"])
    report = compose_weight_panels(plan, {"a": pa, "b": pb})
    recon = verify_weight_panel_identity(plan, {"a": pa, "b": pb}, report.panel)
    assert recon["within_tolerance"] is True
    assert recon["max_abs_diff"] <= 1e-9
    assert recon["over_tolerance_cells"] == 0


def test_verify_panel_identity_dynamic_within_tolerance():
    """动态模式：两 regime 切换下独立复算仍逐位一致。"""
    plan = _two_regime_plan()
    idx = pd.to_datetime(["2026-08-03", "2026-08-04", "2026-08-05"])
    pa = _panel({"600519": [0.8, 0.8, 0.4], "000858": [0.2, 0.2, 0.6]}, idx, ["600519", "000858"])
    pb = _panel({"600519": [0.5, 0.5, 0.5], "000858": [0.5, 0.5, 0.5]}, idx, ["600519", "000858"])
    regime = {"2026-08-03": "r3", "2026-08-05": "r4"}
    report = compose_weight_panels(plan, {"a": pa, "b": pb}, regime_by_date=regime)
    recon = verify_weight_panel_identity(plan, {"a": pa, "b": pb}, report.panel, regime_by_date=regime)
    assert recon["within_tolerance"] is True
    assert recon["max_abs_diff"] <= 1e-9


def test_verify_panel_identity_detects_corruption():
    """反例：面板被扰动 0.01 时必须报超容差（证明校验真的能红）。"""
    plan = _two_regime_plan()
    idx = pd.to_datetime(["2026-08-03"])
    pa = _panel({"600519": [0.8], "000858": [0.2]}, idx, ["600519", "000858"])
    pb = _panel({"600519": [0.5], "000858": [0.5]}, idx, ["600519", "000858"])
    report = compose_weight_panels(plan, {"a": pa, "b": pb})
    corrupted = report.panel.copy()
    corrupted.iloc[0, 0] += 0.01
    recon = verify_weight_panel_identity(plan, {"a": pa, "b": pb}, corrupted)
    assert recon["within_tolerance"] is False
    assert recon["over_tolerance_cells"] >= 1


def test_run_framework_backtest_reports_panel_reconciliation(fake_runner_panels, tmp_path: Path):
    """端到端：summary 与产物 metrics 均落 panel_reconciliation 且静态模式也在容差内。"""
    plans_file = tmp_path / "plans.yaml"
    plans_file.write_text(yaml.safe_dump(_FAKE_CFG), encoding="utf-8")
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
    assert summary["ok"], summary.get("error")
    assert summary["panel_reconciliation"]["within_tolerance"] is True
    d = json.loads((storage / f"{summary['run_id']}.json").read_text(encoding="utf-8"))
    assert d["metrics"]["panel_reconciliation"]["within_tolerance"] is True


# ---------------------------------------------------------------------------
# 状态词表唯一加载通道（CloneGuard extract 级克隆治本后新增的契约）
# ---------------------------------------------------------------------------


def test_states_channel_returns_both_true_sources():
    """两条腿各自解析到自家真源，值与顺序逐位一致（不是交集、不是并集）。"""
    from zephyr.pf_core.strategy_engine.framework_composer import (
        STATES_SOURCE_ACTIVATION,
        STATES_SOURCE_REGIME,
        _states_from_source,
    )
    from zephyr.regime.core.regime_detector import REGIME_STATES
    from zephyr.signal_ashare.core.environment_switch import SIX_STATES

    _states_from_source.cache_clear()
    assert _states_from_source(STATES_SOURCE_REGIME) == tuple(REGIME_STATES)
    assert _states_from_source(STATES_SOURCE_ACTIVATION) == tuple(SIX_STATES)
    assert len(set(REGIME_STATES) & set(SIX_STATES)) == 0, "两词表若有交集则分派键失去意义"


def test_states_channel_uses_one_cache_leg_for_both_sources():
    """合并成一条通道后仍须保持进程内缓存语义：两次调用只 miss 两次。"""
    from zephyr.pf_core.strategy_engine.framework_composer import (
        _activation_states,
        _regime_states,
        _states_from_source,
    )

    _states_from_source.cache_clear()
    first = _regime_states()
    _activation_states()
    assert _regime_states() is first, "第二次调用未命中缓存 ⇒ 冷导入成本回来了"
    info = _states_from_source.cache_info()
    assert info.currsize == 2 and info.misses == 2 and info.hits == 1, info


def test_states_channel_unknown_kind_fails_closed():
    from zephyr.pf_core.strategy_engine.framework_composer import _states_from_source

    _states_from_source.cache_clear()
    with pytest.raises(FrameworkPlanError, match="未知状态词表真源键"):
        _states_from_source("not_a_vocabulary")


def test_states_channel_empty_source_fails_closed(monkeypatch):
    """真源为空 = 非法（否则下游"词表校验"退化为全部拒绝或全部放行）。"""
    import zephyr.signal_ashare.core.environment_switch as env_switch
    from zephyr.pf_core.strategy_engine.framework_composer import (
        STATES_SOURCE_ACTIVATION,
        _states_from_source,
    )

    _states_from_source.cache_clear()
    monkeypatch.setattr(env_switch, "SIX_STATES", ())
    with pytest.raises(FrameworkPlanError, match="真源为空"):
        _states_from_source(STATES_SOURCE_ACTIVATION)
    _states_from_source.cache_clear()


def test_states_channel_import_failure_fails_closed():
    """真源模块不可用必须抛 FrameworkPlanError，禁静默放行任意 regime/activation 字符串。

    sys.modules 置 None 必须在同一函数内 try/finally 复原：本仓 #ARCH-107 污染哨兵
    （tests/conftest.py:415）在 monkeypatch 的 undo 之前跑，用 monkeypatch.setitem 会被判置脏。
    """
    import sys

    from zephyr.pf_core.strategy_engine.framework_composer import (
        STATES_SOURCE_REGIME,
        _states_from_source,
    )

    name = "zephyr.regime.core.regime_detector"
    saved = sys.modules.get(name)
    sys.modules[name] = None
    try:
        _states_from_source.cache_clear()
        with pytest.raises(FrameworkPlanError, match="真源不可用"):
            _states_from_source(STATES_SOURCE_REGIME)
    finally:
        if saved is not None:
            sys.modules[name] = saved
        else:
            sys.modules.pop(name, None)
        _states_from_source.cache_clear()
