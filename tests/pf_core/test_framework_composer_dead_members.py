# [BLUEPRINT] MOD-FWCOMP-001 | docs/03_modules/_domain_portfolio_core/framework_composer_blueprint.md
# [MODULE] tests.pf_core.test_framework_composer_dead_members
# [DOMAIN] D_PF_CORE
# [DEPENDENCIES] zephyr.pf_core.strategy_engine.framework_composer; zephyr.pf_core.strategy_engine.event_sentiment_adapter; pandas; pytest; yaml
# [CONSUMERS] pytest（S11 车道 A T1A 验收）
# [STARTUP] manual
# [MATURITY] design
# [INVARIANTS] 测试禁写生产路径（YAML/产物走 tmp_path，ARCH-BENCH-LEAK-001）; 不触 ClickHouse（load_history / build_event_weight_panel 打桩）; 死成员必进 skipped 带显式 reason，禁静默摊派
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 断言失败即红
# [TESTS] pytest tests/pf_core/test_framework_composer_dead_members.py
# [A_module] module_id=MOD-FWCOMP-001-tests-dead | layer=test | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""死成员假组合治本单测（MOD-FWCOMP-001 · 矿脉 S11 decision_kernel_mining §4 T1A-1/2/3）。

矿脉实证（bt-fw-823d7fd7，2026-09-15）: 方案里 44.1% 的权重质量来自"面板形状正常但
整表为零"的死成员，其 α 被行归一 **静默** 摊派给幸存成员（notes 只留
"行级 Σw 偏差 8.746e-01 已归一至 1.0" 一个数字）。覆盖面:

    - T1A-2 判死四分类: 全零面板 → skipped(all-zero weight rows) + dead_weight_disclosed；
      部分日死 → member_zero_row_counts + material 点名（不再靠行归一暗示）
    - T1A-3 权重合法域含 0（weight: 0 = 显式剔除）+ activation 闸在动态模式真实生效
      （strict/lenient 双口径、``__base__#<phase>`` 分组、全期失活成员移出 participants）
    - T1A-1 载荷路由与契约披露（eventdriven=情绪分适配层 / multifactor=嵌套因子载荷
      降级如实披露 / daban=批产源已落但 compose 面板路未接入）
    - 合成与独立复算（verify_weight_panel_identity）在死成员+激活闸下仍同判据 1e-9
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd
import pytest
import yaml

from zephyr.pf_core.strategy_engine.framework_composer import (
    ACTIVATION_POLICY_LENIENT,
    ACTIVATION_POLICY_STRICT,
    MEMBER_PAYLOAD_ROUTES,
    REASON_ACTIVATION_OFF,
    REASON_ALL_ZERO_ROWS,
    REASON_PANEL_MISSING,
    REASON_TICK_ONLY,
    REASON_ZERO_WEIGHT,
    ROUTE_EVENT_PANEL,
    ROUTE_FLAT,
    ROUTE_NESTED_FACTOR,
    ROUTE_NO_DAILY_SOURCE,
    ROUTE_TRANSLATED,
    FrameworkBacktestConfig,
    FrameworkPlan,
    FrameworkPlanError,
    FrameworkValidationError,
    PlanWeight,
    _build_member_panels,
    _member_route_id,
    _member_signal_contracts,
    compose_weight_panels,
    load_framework_plans,
    verify_weight_panel_identity,
)

IDX = pd.to_datetime(["2026-08-03", "2026-08-04", "2026-08-05"])


def _plan(
    weights: list[PlanWeight],
    *,
    regime_overrides: tuple[tuple[str, tuple[PlanWeight, ...]], ...] = (),
    activation_source: str = "",
) -> FrameworkPlan:
    return FrameworkPlan(
        plan_id="fw-dead",
        name="死成员治本",
        risk_profile="balanced",
        description="",
        weights=tuple(weights),
        regime_overrides=regime_overrides,
        activation_source=activation_source,
    )


def _panel(values: dict[str, list[float]], index=None, columns=None) -> pd.DataFrame:
    return pd.DataFrame(values, index=index if index is not None else IDX, columns=columns or list(values))


def _all_600519(index=None) -> pd.DataFrame:
    """满仓 600519 的活面板（行和=1，真出权重的参照成员）。"""
    idx = index if index is not None else IDX
    return _panel({"600519": [1.0] * len(idx), "000858": [0.0] * len(idx)}, idx)


def _all_000858(index=None) -> pd.DataFrame:
    idx = index if index is not None else IDX
    return _panel({"600519": [0.0] * len(idx), "000858": [1.0] * len(idx)}, idx)


def _zero_panel(index=None) -> pd.DataFrame:
    """形状正常、整表为零的面板——矿脉里"死成员假组合"的原始形态。"""
    idx = index if index is not None else IDX
    return pd.DataFrame(0.0, index=idx, columns=["000001", "600519", "000858"])


def _write_plans(tmp_path: Path, plans: list[dict[str, Any]]) -> Path:
    """方案 YAML 落 tmp_path（ARCH-BENCH-LEAK-001: 测试禁写 config/ 生产真源）。"""
    p = tmp_path / "framework_plans.yaml"
    p.write_text(yaml.safe_dump({"plans": plans}, allow_unicode=True), encoding="utf-8")
    return p


# ---------------------------------------------------------------------------
# T1A-2 判死：全零面板不再是参与成员
# ---------------------------------------------------------------------------


def test_all_zero_panel_member_is_dead_not_participant():
    plan = _plan([PlanWeight("a", 0.5), PlanWeight("dead", 0.3), PlanWeight("c", 0.2)])
    pa = _panel({"600519": [0.7, 0.6, 0.5], "000858": [0.3, 0.4, 0.5]})
    pc = _panel({"600519": [0.5, 0.5, 0.5], "000858": [0.5, 0.5, 0.5]})

    report = compose_weight_panels(plan, {"a": pa, "dead": _zero_panel(), "c": pc})

    assert report.participants == ["a", "c"]
    assert ("dead", REASON_ALL_ZERO_ROWS) in report.skipped
    assert report.alpha_total == pytest.approx(0.7)
    assert report.rescale_factor == pytest.approx(1.0 / 0.7)

    d = report.dead_weight_disclosed
    assert d["schema"] == 1 and d["plan_id"] == "fw-dead"
    assert d["skipped_alpha_base"] == pytest.approx(0.3)
    assert d["dead_member_alpha_base"] == pytest.approx(0.3)
    assert d["skipped_alpha_share_of_plan"] == pytest.approx(0.3)
    assert {e["strategy_id"]: e["kind"] for e in d["skipped_members"]}["dead"] == "dead-member"
    assert [p["strategy_id"] for p in d["participants"]] == ["a", "c"]

    # 治本核心：死成员质量在 α 层被点名，行归一不再承担静默摊派（≈数值噪声）
    assert d["row_normalization"]["max_deviation"] == pytest.approx(0.0, abs=1e-12)
    assert d["row_normalization"]["material"] is False
    assert "行级 Σw 偏差" not in report.notes
    assert "死成员 α 合计 0.300000＝方案 30.0%" in report.notes

    # 数值锚：幸存成员按其 α 占比分得死成员让出的仓位
    assert report.panel.loc[IDX[0], "600519"] == pytest.approx((0.5 * 0.7 + 0.2 * 0.5) / 0.7)
    assert (report.panel.sum(axis=1) - 1.0).abs().max() < 1e-9


def test_dead_vs_missing_vs_upstream_skip_reasons_stay_distinct():
    """三类跳过原因不互相吞没（上游 tick-only reason 不得降级成 panel missing）。"""
    plan = _plan(
        [
            PlanWeight("dead", 0.25),
            PlanWeight("missing", 0.25),
            PlanWeight("tick", 0.25),
            PlanWeight("a", 0.25),
        ]
    )
    report = compose_weight_panels(
        plan,
        {"dead": _zero_panel(), "a": _all_600519()},
        prior_skipped=[("tick", REASON_TICK_ONLY)],
    )
    reasons = dict(report.skipped)
    assert reasons["dead"] == REASON_ALL_ZERO_ROWS
    assert reasons["missing"] == REASON_PANEL_MISSING
    assert reasons["tick"] == REASON_TICK_ONLY
    assert report.participants == ["a"]
    kinds = {e["strategy_id"]: e["kind"] for e in report.dead_weight_disclosed["skipped_members"]}
    assert kinds == {
        "dead": "dead-member",
        "missing": "panel-missing-or-empty",
        "tick": "upstream-skipped",
    }


def test_all_zero_rows_member_rejects_strict_mode():
    plan = _plan([PlanWeight("a", 0.5), PlanWeight("dead", 0.5)])
    with pytest.raises(FrameworkValidationError, match="严格模式"):
        compose_weight_panels(
            plan, {"a": _all_600519(), "dead": _zero_panel()}, allow_partial=False
        )


def test_partially_dead_member_discloses_zero_rows_and_material_gap():
    """部分日死（当日无信号）: 成员仍在 participants，但缺口以 material 行归一点名。"""
    plan = _plan([PlanWeight("a", 0.5), PlanWeight("b", 0.5)])
    pb = _panel({"600519": [0.0, 0.5, 0.5], "000858": [0.0, 0.5, 0.5]})  # 首日整行零

    report = compose_weight_panels(plan, {"a": _all_600519(), "b": pb})
    assert report.participants == ["a", "b"]  # 非全表零→真出过权重，不算死成员
    d = report.dead_weight_disclosed
    assert d["member_zero_row_counts"] == {"a": 0, "b": 1}
    assert [p["zero_signal_rows"] for p in d["participants"]] == [0, 1]
    assert d["row_normalization"]["max_deviation"] == pytest.approx(0.5)
    assert d["row_normalization"]["material"] is True
    assert "幸存成员按 α 摊派" in report.notes
    # 缺口日 a 吃满（引擎口径：行和=1），但披露层说清了"这 50% 是摊派来的"
    assert report.panel.loc[IDX[0], "600519"] == pytest.approx(1.0)
    assert report.panel.loc[IDX[1], "600519"] == pytest.approx(0.75)


# ---------------------------------------------------------------------------
# T1A-3 权重合法域含 0：weight: 0 = 显式剔除（可停用成员）
# ---------------------------------------------------------------------------


def test_weight_zero_is_legal_and_retires_member(tmp_path: Path):
    """停用机制=**声明 weight: 0 本身**（T1A-3 合法域含 0）。

    为何基准表还要一个 0.4 的死成员：方案基准 Σ=1 是 loader 硬不变量（权重合计≠1
    即 FrameworkPlanError，见 tests/pf_core/test_framework_composer.py），所以
    "被剔除成员的声明权重" 必然就是 0——它不带任何质量，explicit_zero_weight_alpha
    因此为 0；要让"两笔账分开"可验证，须同表放一个真死成员（0.4 全零面板）做对照。
    """
    plan = load_framework_plans(
        _write_plans(
            tmp_path,
            [
                {
                    "plan_id": "fw-zero",
                    "name_zh": "含停用成员",
                    "risk_profile": "balanced",
                    "weights": [
                        {"strategy_id": "a", "weight": 0.6},
                        {"strategy_id": "off", "weight": 0.0, "role": "停用（0=显式剔除）"},
                        {"strategy_id": "dead", "weight": 0.4},
                    ],
                }
            ],
        )
    )[0]
    assert plan.weight_map["off"] == 0.0

    report = compose_weight_panels(
        plan,
        {
            "a": _all_600519(),
            "off": _all_000858(),  # 停用成员面板有真值也不得参与
            "dead": _zero_panel(),
        },
    )
    assert report.participants == ["a"]
    assert ("off", REASON_ZERO_WEIGHT) in report.skipped
    assert ("dead", REASON_ALL_ZERO_ROWS) in report.skipped
    assert report.alpha_total == pytest.approx(0.6)
    assert report.rescale_factor == pytest.approx(1.0 / 0.6)
    d = report.dead_weight_disclosed
    assert d["explicit_zero_weight_alpha"] == pytest.approx(0.0)  # 0 权重不占任何质量
    assert d["dead_member_alpha_base"] == pytest.approx(0.4)  # 剔除≠死成员，两笔账分开
    entry = next(e for e in d["skipped_members"] if e["strategy_id"] == "off")
    assert entry["kind"] == "explicit-zero-weight"
    assert entry["alpha"] == pytest.approx(0.0)
    assert report.panel["600519"].abs().max() == pytest.approx(1.0, abs=1e-9)


def test_weight_negative_still_rejected(tmp_path: Path):
    with pytest.raises(FrameworkPlanError, match=r"越界.*合法 \[0,1\]"):
        load_framework_plans(
            _write_plans(
                tmp_path,
                [
                    {
                        "plan_id": "fw-neg",
                        "name_zh": "越界",
                        "risk_profile": "balanced",
                        "weights": [{"strategy_id": "a", "weight": -0.1}],
                    }
                ],
            )
        )


def test_weight_zero_override_table_cannot_revive_but_can_enable():
    """基准 0 + 覆盖表非 0 → max_alpha_across_tables>0（动态某 regime 下该员仍可参与）。"""
    plan = _plan(
        [PlanWeight("a", 0.5), PlanWeight("off", 0.0), PlanWeight("c", 0.5)],
        regime_overrides=(("r3", (PlanWeight("a", 0.0), PlanWeight("off", 1.0))),),
    )
    assert plan.max_alpha_across_tables("off") == 1.0
    # 静态模式只查基准 α → off 显式剔除
    static = compose_weight_panels(plan, {"a": _all_600519(), "off": _all_000858(), "c": _all_600519()})
    assert static.participants == ["a", "c"]
    # 动态模式 r3 日 off 吃满 1.0 → 静态判死不得沿用
    dyn = compose_weight_panels(
        plan,
        {"a": _all_600519(), "off": _all_000858(), "c": _all_600519()},
        regime_by_date={"2026-08-03": "r3", "2026-08-04": "r10", "2026-08-05": "r10"},
    )
    assert dyn.regime_day_counts == {"r3": 1, "__base__": 2}
    assert dyn.panel.loc[IDX[0], "000858"] == pytest.approx(1.0)
    assert dyn.panel.loc[IDX[1], "000858"] == pytest.approx(0.0)


# ---------------------------------------------------------------------------
# T1A-3 activation 闸：动态模式真实生效
# ---------------------------------------------------------------------------


def test_activation_gate_zeroes_alpha_outside_declared_phase():
    plan = _plan(
        [
            PlanWeight("always", 0.5, activation=None),
            PlanWeight("expansion-only", 0.5, activation=("expansion",)),
        ],
        activation_source="weights",
    )
    regime = {"2026-08-03": "r3", "2026-08-04": "r10", "2026-08-05": "r3"}

    report = compose_weight_panels(
        plan,
        {"always": _all_600519(), "expansion-only": _all_000858()},
        regime_by_date=regime,
    )

    # 同一基准权重表，仍按六段态拆组（否则闸语义会被组内平均掉）
    assert report.regime_day_counts == {"__base__#expansion": 2, "__base__#capitulation": 1}
    assert report.participants == ["always", "expansion-only"]
    assert report.panel.loc[IDX[0], "600519"] == pytest.approx(0.5)  # expansion: 五五开
    assert report.panel.loc[IDX[1], "600519"] == pytest.approx(1.0)  # capitulation: 只剩 always
    assert report.panel.loc[IDX[1], "000858"] == pytest.approx(0.0)

    groups = {g["group"]: g for g in report.dead_weight_disclosed["activation"]["groups"]}
    assert groups["__base__#expansion"]["alpha_total"] == pytest.approx(1.0)
    assert groups["__base__#expansion"]["six_phase"] == "expansion"
    assert groups["__base__#capitulation"]["alpha_total"] == pytest.approx(0.5)
    assert groups["__base__#capitulation"]["rescale_factor"] == pytest.approx(2.0)
    assert [g["strategy_id"] for g in groups["__base__#capitulation"]["gated_off"]] == [
        "expansion-only"
    ]
    assert report.regime_rescale_factors == {"__base__#capitulation": pytest.approx(2.0)}
    assert "activation 闸生效" in report.notes


def test_activation_strict_zeroes_on_unmapped_regime_lenient_keeps():
    plan = _plan(
        [
            PlanWeight("always", 0.5),
            PlanWeight("euphoria-only", 0.5, activation=("euphoria",)),
        ],
        activation_source="weights",
    )
    panels = {"always": _all_600519(IDX[:1]), "euphoria-only": _all_000858(IDX[:1])}
    regime = {"2026-08-03": "r1"}  # r1 低波震荡=无六段对应（auto_mount 同口径"不路由"）

    strict = compose_weight_panels(
        plan, panels, regime_by_date=regime, activation_policy=ACTIVATION_POLICY_STRICT
    )
    assert strict.regime_day_counts == {"__base__#no-phase": 1}
    assert strict.skipped == [("euphoria-only", REASON_ACTIVATION_OFF)]
    assert strict.participants == ["always"]
    assert strict.panel.loc[IDX[0], "600519"] == pytest.approx(1.0)
    assert "activation 全期失活成员" in strict.notes

    lenient = compose_weight_panels(
        plan, panels, regime_by_date=regime, activation_policy=ACTIVATION_POLICY_LENIENT
    )
    assert lenient.skipped == []
    assert lenient.participants == ["always", "euphoria-only"]
    assert lenient.panel.loc[IDX[0], "000858"] == pytest.approx(0.5)
    assert lenient.dead_weight_disclosed["activation"]["policy"] == ACTIVATION_POLICY_LENIENT


def test_activation_declared_empty_set_means_never_active():
    plan = _plan(
        [PlanWeight("always", 0.5), PlanWeight("retired", 0.5, activation=())],
        activation_source="weights",
    )
    report = compose_weight_panels(
        plan,
        {"always": _all_600519(IDX[:2]), "retired": _all_000858(IDX[:2])},
        regime_by_date={"2026-08-03": "r3", "2026-08-04": "r10"},
    )
    assert report.participants == ["always"]
    assert ("retired", REASON_ACTIVATION_OFF) in report.skipped
    entry = next(
        e
        for e in report.dead_weight_disclosed["skipped_members"]
        if e["strategy_id"] == "retired"
    )
    assert entry["kind"] == "activation-gated-off"
    assert report.dead_weight_disclosed["activation"]["always_inactive_members"] == ["retired"]


def test_activation_all_groups_zero_alpha_raises():
    plan = _plan([PlanWeight("euphoria-only", 1.0, activation=("euphoria",))])
    with pytest.raises(FrameworkValidationError, match="α 合计均为 0"):
        compose_weight_panels(
            plan,
            {"euphoria-only": _all_000858(IDX[:2])},
            regime_by_date={"2026-08-03": "r3", "2026-08-04": "r10"},
        )


def test_activation_empty_position_group_is_legitimate_not_error():
    """各组只吃到自己那员的 α＝合法低仓组（禁误判为错误，也禁被静默放大成满仓）。"""
    plan = _plan(
        [
            PlanWeight("expansion-only", 0.5, activation=("expansion",)),
            PlanWeight("capitulation-only", 0.5, activation=("capitulation",)),
        ],
        activation_source="weights",
    )
    report = compose_weight_panels(
        plan,
        {"expansion-only": _all_600519(IDX[:2]), "capitulation-only": _all_000858(IDX[:2])},
        regime_by_date={"2026-08-03": "r3", "2026-08-04": "r10"},
    )
    groups = report.dead_weight_disclosed["activation"]["groups"]
    assert [g["group"] for g in groups] == ["__base__#expansion", "__base__#capitulation"]
    assert [g["alpha_total"] for g in groups] == pytest.approx([0.5, 0.5])
    assert report.dead_weight_disclosed["activation"]["zero_alpha_groups"] == []
    assert report.panel.loc[IDX[0], "600519"] == pytest.approx(1.0)
    assert report.panel.loc[IDX[1], "000858"] == pytest.approx(1.0)


def test_activation_not_applied_in_static_mode():
    """静态模式（无 regime 序）不套 activation——二期逐位一致锚。"""
    plan = _plan(
        [
            PlanWeight("always", 0.5),
            PlanWeight("euphoria-only", 0.5, activation=("euphoria",)),
        ],
        activation_source="weights",
    )
    report = compose_weight_panels(
        plan, {"always": _all_600519(IDX[:1]), "euphoria-only": _all_000858(IDX[:1])}
    )
    assert report.participants == ["always", "euphoria-only"]
    assert report.skipped == []
    assert report.dead_weight_disclosed["activation"]["applied"] is False
    assert report.panel.loc[IDX[0], "000858"] == pytest.approx(0.5)


def test_activation_policy_invalid_rejected():
    plan = _plan([PlanWeight("a", 1.0)])
    with pytest.raises(FrameworkValidationError, match="activation_policy 非法"):
        compose_weight_panels(
            plan,
            {"a": _all_600519()},
            regime_by_date={"2026-08-03": "r3"},
            activation_policy="whatever",
        )


def test_override_table_cannot_declare_activation(tmp_path: Path):
    """activation 唯一声明位=基准 weights（覆盖表再声明=两个真源，fail-closed）。"""
    with pytest.raises(FrameworkPlanError, match="不得声明 activation"):
        load_framework_plans(
            _write_plans(
                tmp_path,
                [
                    {
                        "plan_id": "fw-two-src",
                        "name_zh": "双真源",
                        "risk_profile": "balanced",
                        "weights": [{"strategy_id": "a", "weight": 1.0}],
                        "regime_overrides": {
                            "r3": [{"strategy_id": "a", "weight": 1.0, "activation": ["expansion"]}]
                        },
                    }
                ],
            )
        )


def test_activation_illegal_phase_word_rejected(tmp_path: Path):
    with pytest.raises(FrameworkPlanError, match="activation"):
        load_framework_plans(
            _write_plans(
                tmp_path,
                [
                    {
                        "plan_id": "fw-bad-act",
                        "name_zh": "错词",
                        "risk_profile": "balanced",
                        "weights": [{"strategy_id": "a", "weight": 1.0, "activation": ["expanshn"]}],
                    }
                ],
            )
        )


def test_x_tdm_provenance_activation_state_is_consumed(tmp_path: Path):
    """生成器产物 activation_state 兜底（fw-tdm-current 现状口径，零 YAML 改动即生效）。"""
    plan = load_framework_plans(
        _write_plans(
            tmp_path,
            [
                {
                    "plan_id": "fw-prov",
                    "name_zh": "生成器产物",
                    "risk_profile": "balanced",
                    "weights": [{"strategy_id": "a", "weight": 1.0}],
                    "x_tdm_provenance": {
                        "activation_state": [{"strategy_ref": "a", "activation": ["expansion"]}]
                    },
                }
            ],
        )
    )[0]
    assert plan.activation_map["a"] == ("expansion",)
    assert plan.activation_source == "x_tdm_provenance"
    assert plan.has_activation_rules is True
    report = compose_weight_panels(
        plan, {"a": _all_600519()}, regime_by_date={"2026-08-03": "r3", "2026-08-04": "r10"}
    )
    assert report.dead_weight_disclosed["activation"]["declaration_source"] == "x_tdm_provenance"
    assert report.dead_weight_disclosed["activation"]["declared"] == {"a": ["expansion"]}


# ---------------------------------------------------------------------------
# 合成 vs 独立复算：死成员+激活闸下同判据 1e-9
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "weights,panels,regime",
    [
        pytest.param(
            [PlanWeight("a", 0.5), PlanWeight("dead", 0.3), PlanWeight("c", 0.2)],
            None,
            None,
            id="static-dead-member",
        ),
        pytest.param(
            [
                PlanWeight("always", 0.4),
                PlanWeight("expansion-only", 0.35, activation=("expansion",)),
                PlanWeight("dead", 0.25),
            ],
            None,
            {"2026-08-03": "r3", "2026-08-04": "r10", "2026-08-05": "r12"},
            id="dynamic-activation-and-dead",
        ),
        pytest.param(
            [
                PlanWeight("a", 0.5),
                PlanWeight("off", 0.5),
                PlanWeight("euphoria-only", 0.0, activation=("euphoria",)),
            ],
            None,
            {"2026-08-03": "r3", "2026-08-04": "r11", "2026-08-05": "r4"},
            id="dynamic-zero-weight-and-unmapped-phase",
        ),
    ],
)
def test_verify_identity_shares_dead_and_activation_judgement(weights, panels, regime):
    plan = _plan(weights, activation_source="weights")
    panels = panels or {
        "a": _all_600519(),
        "always": _all_600519(),
        "c": _all_600519(),
        "off": _zero_panel(),
        "dead": _zero_panel(),
        "expansion-only": _all_000858(),
        "euphoria-only": _all_000858(),
    }
    report = compose_weight_panels(plan, panels, regime_by_date=regime)
    recon = verify_weight_panel_identity(plan, panels, report.panel, regime_by_date=regime)
    assert recon["within_tolerance"] is True, recon
    assert recon["max_abs_diff"] <= 1e-9
    assert recon["over_tolerance_cells"] == 0
    assert "同源" in recon["note"]
    # 面板全行归一（现金行除外）——行和只能来自真出权重的成员
    live = report.panel[~(report.panel.abs().sum(axis=1) <= 1e-15)]
    assert (live.sum(axis=1) - 1.0).abs().max() < 1e-9


def test_verify_identity_still_detects_tampering():
    """判据同源不等于放弃独立复算（真违规仍能检出）。"""
    plan = _plan([PlanWeight("a", 0.5), PlanWeight("b", 0.5)])
    panels = {"a": _all_600519(), "b": _all_000858()}
    report = compose_weight_panels(plan, panels)
    tampered = report.panel.copy()
    tampered.iloc[0, 0] += 1e-3
    recon = verify_weight_panel_identity(plan, panels, tampered)
    assert recon["within_tolerance"] is False
    assert recon["max_abs_diff"] > 1e-4


# ---------------------------------------------------------------------------
# T1A-1 载荷路由与契约披露
# ---------------------------------------------------------------------------


def test_member_payload_routes_cover_all_rich_payload_members():
    assert set(MEMBER_PAYLOAD_ROUTES) == {"eventdriven-sleeve", "multifactor-sleeve", "daban-sleeve"}
    assert _member_route_id("eventdriven-sleeve") == ROUTE_EVENT_PANEL
    assert _member_route_id("multifactor-sleeve") == ROUTE_NESTED_FACTOR
    assert _member_route_id("daban-sleeve") == ROUTE_NO_DAILY_SOURCE
    assert _member_route_id("STR-VREV-025") == ROUTE_TRANSLATED
    assert _member_route_id("topn-momentum") == ROUTE_FLAT


def test_contracts_disclose_single_factor_degradation():
    plan = _plan(
        [
            PlanWeight("multifactor-sleeve", 0.3),
            PlanWeight("eventdriven-sleeve", 0.2),
            PlanWeight("daban-sleeve", 0.2),
            PlanWeight("STR-VREV-025", 0.15),
            PlanWeight("topn-momentum", 0.15),
        ]
    )
    cfg = FrameworkBacktestConfig(factor_ids=("momentum_20d",), top_n=20)
    contracts = _member_signal_contracts(
        plan, cfg, {"multifactor-sleeve": _all_600519(IDX[:1])}
    )

    mf = contracts["multifactor-sleeve"]
    assert mf["route"] == ROUTE_NESTED_FACTOR
    assert mf["payload_contract"] == "{symbol: {factor_id: value}}"
    assert "momentum_20d" in mf["disclosure"]  # 占位符按实际喂入因子替换，禁空话
    assert "退化为单因子" in mf["disclosure"] and "不是真多因子合成" in mf["disclosure"]
    assert mf["panel_built"] is True

    ev = contracts["eventdriven-sleeve"]
    assert ev["route"] == ROUTE_EVENT_PANEL
    assert "build_event_weight_panel" in ev["disclosure"]
    assert "T-1 18:00" in ev["disclosure"]  # PIT 窗随契约留痕

    db = contracts["daban-sleeve"]
    assert db["route"] == ROUTE_NO_DAILY_SOURCE and db["panel_built"] is False
    assert "本 compose 面板路尚未接入" in db["disclosure"] and "weight: 0" in db["disclosure"]

    assert contracts["STR-VREV-025"]["route"] == ROUTE_TRANSLATED
    assert contracts["topn-momentum"]["route"] == ROUTE_FLAT
    assert contracts["topn-momentum"]["panel_built"] is False


def test_event_route_builds_panel_from_adapter_and_names_failure(monkeypatch, tmp_path: Path):
    """eventdriven 走情绪分适配层（不再喂扁平标量→不再恒返回 {}）。"""
    from zephyr.factor.core.evaluation import backtest as bt_mod
    from zephyr.pf_core.strategy_engine import event_sentiment_adapter as esa

    hist = pd.DataFrame(
        {"close": [10.0, 11.0, 12.0, 13.0]},
        index=pd.MultiIndex.from_tuples(
            [
                (pd.Timestamp("2026-08-03"), "000001"),
                (pd.Timestamp("2026-08-03"), "600519"),
                (pd.Timestamp("2026-08-04"), "000001"),
                (pd.Timestamp("2026-08-04"), "600519"),
            ],
            names=["trade_date", "symbol"],
        ),
    )
    monkeypatch.setattr(bt_mod, "load_history", lambda *a, **k: hist, raising=True)

    seen: dict[str, Any] = {}

    def fake_build(dates, universe, **kw):
        seen["dates"] = [pd.Timestamp(d) for d in dates]
        seen["universe"] = list(universe)
        seen["kw"] = kw
        return pd.DataFrame(0.5, index=pd.DatetimeIndex(seen["dates"]), columns=list(universe))

    monkeypatch.setattr(esa, "build_event_weight_panel", fake_build, raising=True)

    plan = _plan([PlanWeight("eventdriven-sleeve", 1.0)])
    cfg = FrameworkBacktestConfig(top_n=7, max_single=0.2)
    data, panels, skipped = _build_member_panels(
        plan, ["000001", "600519"], "2026-08-03", "2026-08-04", cfg
    )
    assert skipped == []
    assert "eventdriven-sleeve" in panels
    assert data is hist  # 复用行情历史，不重复取数
    assert seen["universe"] == ["000001", "600519"]  # 纯数字轴（与 load_history 同源）
    assert seen["kw"]["top_n"] == 7 and seen["kw"]["max_single"] == 0.2

    def boom(*a, **k):
        raise RuntimeError("CH 无表")

    monkeypatch.setattr(esa, "build_event_weight_panel", boom, raising=True)
    data2, panels2, skipped2 = _build_member_panels(
        plan, ["000001", "600519"], "2026-08-03", "2026-08-04", cfg
    )
    assert panels2 == {} and data2 is hist
    assert skipped2 and skipped2[0][0] == "eventdriven-sleeve"
    assert skipped2[0][1].startswith("event panel build failed:")  # 失败原因具体到路


def test_event_route_names_empty_history(monkeypatch):
    from zephyr.factor.core.evaluation import backtest as bt_mod

    monkeypatch.setattr(
        bt_mod, "load_history", lambda *a, **k: pd.DataFrame(), raising=True
    )
    plan = _plan([PlanWeight("eventdriven-sleeve", 1.0)])
    _data, panels, skipped = _build_member_panels(
        plan, ["000001"], "2026-08-03", "2026-08-04", FrameworkBacktestConfig()
    )
    assert panels == {}
    assert skipped[0][1].startswith("event route: 行情历史为空")


def test_explicit_zero_weight_member_skipped_without_data_access(monkeypatch):
    """α 全表 0 → 构建面板阶段就跳过，不浪费一次 CH 取数。"""
    plan = _plan([PlanWeight("daban-sleeve", 0.0)])
    _data, panels, skipped = _build_member_panels(
        plan, ["000001"], "2026-08-03", "2026-08-04", FrameworkBacktestConfig()
    )
    assert panels == {}
    assert skipped == [("daban-sleeve", REASON_ZERO_WEIGHT)]
