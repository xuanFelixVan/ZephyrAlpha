# [BLUEPRINT] MOD-SIM-028 | docs/03_modules/_domain_simulation/overfitting_protection_gate/blueprint.md | §test
# [TTL] permanent
# [A_test] module_id: MOD-SIM-028 | layer=test | stability=volatile | safety=M | ai_autonomy=human_gated
# [MODULE] tests.simulation.test_overfitting_protection_gate
# [TESTS] src/zephyr/simulation/overfitting_protection_gate.py
"""MOD-SIM-028 单元测试：overfitting_protection_gate 过拟合系统性防护门禁。

蓝图验收（B1-00261/CAND-SIM-009，C2 C-033）：
因子（IC衰减+多重检验校正）/策略（deflated SR+PBO）/信号（walkforward
折叠一致性）/ML（OOS退化+对抗）四层检查项注册表 + 统一裁决（任一层失败
即拦截上线）+ 防护报告。检查器/时钟全注入内存替身，不触网。
"""

from __future__ import annotations

import datetime

import pytest

pytest.importorskip(
    "zephyr.simulation.overfitting_protection_gate",
    reason="overfitting_protection_gate not importable",
)

from zephyr.simulation.overfitting_protection_gate import (  # noqa: E402
    CheckOutcome,
    CheckStatus,
    GateDecision,
    OverfittingGateError,
    OverfittingProtectionGate,
    ProtectionLayer,
)

_T0 = datetime.datetime(2026, 8, 26, 9, 30, 0)

_OK = lambda ctx: CheckOutcome(passed=True, metrics={"ok": 1})  # noqa: E731


def _gate(clock=_T0) -> OverfittingProtectionGate:
    return OverfittingProtectionGate(clock=(lambda: clock) if clock is not None else None)


def _fill(gate: OverfittingProtectionGate, checker=_OK) -> None:
    """四层各注册一个通过检查项（凑齐裁决前提）。"""
    for layer in ProtectionLayer:
        gate.register_check(layer, f"{layer.value}-chk", checker)


# ──────────────────────────────────────────────────────────────────────────────
# 检查项注册表
# ──────────────────────────────────────────────────────────────────────────────


class TestRegisterCheck:
    def test_register_ok_four_layers(self) -> None:
        gate = _gate()
        _fill(gate)
        for layer in ProtectionLayer:
            assert gate.checks_of(layer) == (f"{layer.value}-chk",)

    def test_register_empty_check_id_raises(self) -> None:
        gate = _gate()
        with pytest.raises(OverfittingGateError):
            gate.register_check(ProtectionLayer.FACTOR, "", _OK)

    def test_register_invalid_layer_raises(self) -> None:
        gate = _gate()
        with pytest.raises(OverfittingGateError):
            gate.register_check("factor", "chk-1", _OK)  # 字符串非枚举

    def test_register_duplicate_raises(self) -> None:
        gate = _gate()
        gate.register_check(ProtectionLayer.FACTOR, "chk-1", _OK)
        with pytest.raises(OverfittingGateError):
            gate.register_check(ProtectionLayer.FACTOR, "chk-1", _OK)

    def test_register_non_callable_raises(self) -> None:
        gate = _gate()
        with pytest.raises(OverfittingGateError):
            gate.register_check(ProtectionLayer.ML, "chk-1", 42)

    def test_checks_of_sorted(self) -> None:
        gate = _gate()
        gate.register_check(ProtectionLayer.SIGNAL, "wf-b", _OK)
        gate.register_check(ProtectionLayer.SIGNAL, "wf-a", _OK)
        assert gate.checks_of(ProtectionLayer.SIGNAL) == ("wf-a", "wf-b")

    def test_checks_of_invalid_layer_raises(self) -> None:
        gate = _gate()
        with pytest.raises(OverfittingGateError):
            gate.checks_of("ml")


# ──────────────────────────────────────────────────────────────────────────────
# 统一裁决（任一层失败即拦截）
# ──────────────────────────────────────────────────────────────────────────────


class TestEvaluate:
    def test_all_pass_approved(self) -> None:
        gate = _gate()
        _fill(gate)
        report = gate.evaluate("subj-1")
        assert report.decision is GateDecision.APPROVED
        assert report.blocked_by == ()
        assert len(report.layer_verdicts) == 4
        assert all(v.passed for v in report.layer_verdicts)
        assert report.generated_at == _T0

    @pytest.mark.parametrize("layer", list(ProtectionLayer))
    def test_any_layer_fail_blocked(self, layer: ProtectionLayer) -> None:
        gate = _gate()
        _fill(gate)
        gate.register_check(layer, "bad-chk", lambda ctx: CheckOutcome(passed=False, detail="退化"))
        report = gate.evaluate("subj-1")
        assert report.decision is GateDecision.BLOCKED
        assert report.blocked_by == ("bad-chk",)
        verdict = {v.layer: v for v in report.layer_verdicts}[layer]
        assert not verdict.passed

    def test_multi_layer_fail_blocked_by_sorted(self) -> None:
        gate = _gate()
        _fill(gate)
        gate.register_check(ProtectionLayer.ML, "zz-oos", lambda ctx: CheckOutcome(passed=False))
        gate.register_check(ProtectionLayer.FACTOR, "aa-ic", lambda ctx: CheckOutcome(passed=False))
        report = gate.evaluate("subj-1")
        assert report.decision is GateDecision.BLOCKED
        assert report.blocked_by == ("aa-ic", "zz-oos")  # 确定性排序

    def test_results_sorted_by_check_id(self) -> None:
        gate = _gate()
        _fill(gate)
        gate.register_check(ProtectionLayer.FACTOR, "ic-2", _OK)
        gate.register_check(ProtectionLayer.FACTOR, "ic-1", _OK)
        report = gate.evaluate("subj-1")
        factor = report.layer_verdicts[0]
        assert [r.check_id for r in factor.results] == ["factor-chk", "ic-1", "ic-2"]

    def test_missing_layer_fail_closed(self) -> None:
        gate = _gate()
        gate.register_check(ProtectionLayer.FACTOR, "ic", _OK)  # 缺 strategy/signal/ml
        with pytest.raises(OverfittingGateError):
            gate.evaluate("subj-1")

    @pytest.mark.parametrize("skipped", list(ProtectionLayer))
    def test_each_missing_layer_fail_closed(self, skipped: ProtectionLayer) -> None:
        gate = _gate()
        for layer in ProtectionLayer:
            if layer is not skipped:
                gate.register_check(layer, "chk", _OK)
        with pytest.raises(OverfittingGateError):
            gate.evaluate("subj-1")

    def test_empty_subject_raises(self) -> None:
        gate = _gate()
        _fill(gate)
        with pytest.raises(OverfittingGateError):
            gate.evaluate("")

    def test_checker_exception_fail_closed(self) -> None:
        def _boom(ctx):
            raise RuntimeError("指标源缺失")

        gate = _gate()
        _fill(gate)
        gate.register_check(ProtectionLayer.STRATEGY, "dsr-boom", _boom)
        report = gate.evaluate("subj-1")
        assert report.decision is GateDecision.BLOCKED
        assert report.blocked_by == ("dsr-boom",)
        result = [r for v in report.layer_verdicts for r in v.results if r.check_id == "dsr-boom"][0]
        assert result.status is CheckStatus.FAILED
        assert "检查器异常" in result.detail

    def test_payload_passed_to_checkers(self) -> None:
        seen: list[dict] = []
        gate = _gate()
        _fill(gate, lambda ctx: seen.append(dict(ctx)) or CheckOutcome(passed=True))
        gate.evaluate("subj-1", {"dsr": 0.97})
        assert seen and all(s == {"dsr": 0.97} for s in seen)

    def test_clock_injected(self) -> None:
        t1 = datetime.datetime(2030, 1, 1, 0, 0, 0)
        gate = _gate(clock=t1)
        _fill(gate)
        assert gate.evaluate("subj-1").generated_at == t1

    def test_deterministic_same_input_same_output(self) -> None:
        def _build() -> OverfittingProtectionGate:
            gate = _gate()
            _fill(gate)
            gate.register_check(
                ProtectionLayer.ML, "adv",
                lambda ctx: CheckOutcome(passed=ctx["adv"] >= 0.5, metrics={"adv": ctx["adv"]}),
            )
            return gate

        r1 = _build().evaluate("subj-1", {"adv": 0.8})
        r2 = _build().evaluate("subj-1", {"adv": 0.8})
        assert r1 == r2


# ──────────────────────────────────────────────────────────────────────────────
# 四层语义检查器示例（注入式，指标真源在检查器内）
# ──────────────────────────────────────────────────────────────────────────────


class TestSemanticCheckers:
    @staticmethod
    def _semantic_gate() -> OverfittingProtectionGate:
        gate = _gate()
        # 因子层：IC 衰减 + 多重检验校正（BHY FDR 后显著数）
        gate.register_check(
            ProtectionLayer.FACTOR, "ic-decay",
            lambda ctx: CheckOutcome(
                passed=ctx["ic_tail"] >= ctx["ic_head"] * 0.5,
                metrics={"ic_head": ctx["ic_head"], "ic_tail": ctx["ic_tail"]},
                detail="IC 衰减过半" if ctx["ic_tail"] < ctx["ic_head"] * 0.5 else "",
            ),
        )
        gate.register_check(
            ProtectionLayer.FACTOR, "multi-test",
            lambda ctx: CheckOutcome(passed=ctx["fdr_significant"] > 0),
        )
        # 策略层：deflated SR + PBO
        gate.register_check(
            ProtectionLayer.STRATEGY, "deflated-sr",
            lambda ctx: CheckOutcome(passed=ctx["dsr"] >= 0.95, metrics={"dsr": ctx["dsr"]}),
        )
        gate.register_check(
            ProtectionLayer.STRATEGY, "pbo",
            lambda ctx: CheckOutcome(passed=ctx["pbo"] < 0.5, metrics={"pbo": ctx["pbo"]}),
        )
        # 信号层：walkforward 折叠一致性（OOS Sharpe 符号一致率）
        gate.register_check(
            ProtectionLayer.SIGNAL, "wf-consistency",
            lambda ctx: CheckOutcome(
                passed=sum(1 for s in ctx["fold_sharpes"] if s > 0) / len(ctx["fold_sharpes"]) >= 0.8,
            ),
        )
        # ML 层：OOS 退化 + 对抗稳健
        gate.register_check(
            ProtectionLayer.ML, "oos-degradation",
            lambda ctx: CheckOutcome(passed=ctx["oos_auc"] >= ctx["is_auc"] * 0.7),
        )
        gate.register_check(
            ProtectionLayer.ML, "adversarial",
            lambda ctx: CheckOutcome(passed=ctx["adv_robust"] >= 0.6),
        )
        return gate

    _GOOD = {
        "ic_head": 0.08, "ic_tail": 0.05, "fdr_significant": 3,
        "dsr": 0.97, "pbo": 0.2, "fold_sharpes": [1.2, 0.9, 1.5, 0.8, -0.1],
        "is_auc": 0.80, "oos_auc": 0.72, "adv_robust": 0.75,
    }

    def test_semantic_all_pass(self) -> None:
        report = self._semantic_gate().evaluate("alpha-x", dict(self._GOOD))
        assert report.decision is GateDecision.APPROVED

    def test_semantic_ic_decay_blocks(self) -> None:
        payload = dict(self._GOOD, ic_tail=0.02)  # IC 衰减过半
        report = self._semantic_gate().evaluate("alpha-x", payload)
        assert report.decision is GateDecision.BLOCKED
        assert "ic-decay" in report.blocked_by

    def test_semantic_dsr_pbo_block(self) -> None:
        payload = dict(self._GOOD, dsr=0.60, pbo=0.9)  # DSR 不显著 + PBO 过高
        report = self._semantic_gate().evaluate("alpha-x", payload)
        assert report.decision is GateDecision.BLOCKED
        assert report.blocked_by == ("deflated-sr", "pbo")

    def test_semantic_wf_and_ml_block(self) -> None:
        payload = dict(self._GOOD, fold_sharpes=[-1.0, -0.5, 0.2, -0.3, 0.1], oos_auc=0.40)
        report = self._semantic_gate().evaluate("alpha-x", payload)
        assert report.decision is GateDecision.BLOCKED
        assert report.blocked_by == ("oos-degradation", "wf-consistency")
