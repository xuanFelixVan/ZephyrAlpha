# [BLUEPRINT] MOD-L02-001 | docs/03_modules/_domain_factor/blueprint.md
# [MODULE] tests.factor.test_factor_factory
# [DOMAIN] D_FACTOR
# [DEPENDENCIES] zephyr.factor.factor_factory
# [CONSUMERS] none
# [STARTUP] pytest
# [MATURITY] production
# [INVARIANTS] 纯内存编排测试，registry/validator/gate/mining_hook 注入式，不触网不触库
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 测试失败=9阶段编排/双重验证/回测门禁/注册入库逻辑缺陷
# [TESTS] 本文件
# [TTL] permanent
"""FactorFactory 单元测试（CAND-FAC-008 / B1-00143，C-027 因子工厂）。

覆盖（min_build_spec）：
- 9 阶段（候选立项/假设/生成/验证/入库/监控/迭代/废弃/退役）流水线编排
- 产出必经 C-003 回测门禁与 IC/因果双重验证（未过验证禁入库）
- 注册表入库委托 FactorRegistry（注入式）
- 底层生命周期复用 lifecycle_state_machine FSM（不重造状态机）
- FactorMAD 挖掘为 mining_hook 扩展点（CAND-FAC-020 未来件，委托不实现）
"""

from __future__ import annotations

import pytest

from zephyr.factor.factor_factory import (
    FactorCandidate,
    FactorFactory,
    FactorFactoryError,
    FactoryStage,
)


def _candidate(cid: str = "cand-1") -> FactorCandidate:
    return FactorCandidate(
        candidate_id=cid,
        hypothesis="20日动量与次日收益正相关",
        expression="close.pct_change(20)",
        factor_id="momentum_20d_test",
    )


def _factory(**overrides) -> FactorFactory:
    kwargs = {
        "ic_validator": lambda c: True,
        "causal_validator": lambda c: True,
        "backtest_gate": lambda c: True,
        "registry": _StubRegistry(),
    }
    kwargs.update(overrides)
    return FactorFactory(**kwargs)


class _StubRegistry:
    """FactorRegistry 最小替身（register/get 语义）。"""

    def __init__(self) -> None:
        self.registered: list[str] = []

    def register_factor(self, factor_id: str, payload: dict) -> None:
        if factor_id in self.registered:
            raise ValueError(f"重复注册: {factor_id}")
        self.registered.append(factor_id)


class TestNineStages:
    """9 阶段枚举与全流程。"""

    def test_nine_stages_defined(self) -> None:
        assert [s.value for s in FactoryStage] == [
            "candidate",
            "hypothesis",
            "generation",
            "validation",
            "registration",
            "monitoring",
            "iteration",
            "deprecation",
            "retirement",
        ]

    def test_full_lifecycle_happy_path(self) -> None:
        reg = _StubRegistry()
        factory = _factory(registry=reg)
        factory.submit(_candidate())
        for stage in (
            FactoryStage.HYPOTHESIS,
            FactoryStage.GENERATION,
            FactoryStage.VALIDATION,
            FactoryStage.REGISTRATION,
            FactoryStage.MONITORING,
            FactoryStage.ITERATION,
            FactoryStage.DEPRECATION,
            FactoryStage.RETIREMENT,
        ):
            verdict = factory.advance("cand-1", stage)
            assert verdict.passed is True, f"{stage}: {verdict.reason}"
        assert factory.stage_of("cand-1") == FactoryStage.RETIREMENT
        assert reg.registered == ["momentum_20d_test"]

    def test_initial_stage_is_candidate(self) -> None:
        factory = _factory()
        factory.submit(_candidate())
        assert factory.stage_of("cand-1") == FactoryStage.CANDIDATE


class TestValidationGates:
    """IC/因果双重验证 + C-003 回测门禁。"""

    def _reach_generation(self, factory: FactorFactory) -> None:
        factory.submit(_candidate())
        factory.advance("cand-1", FactoryStage.HYPOTHESIS)
        factory.advance("cand-1", FactoryStage.GENERATION)

    def test_ic_failure_blocks_validation(self) -> None:
        factory = _factory(ic_validator=lambda c: False)
        self._reach_generation(factory)
        verdict = factory.advance("cand-1", FactoryStage.VALIDATION)
        assert verdict.passed is False
        assert "IC" in verdict.reason
        assert factory.stage_of("cand-1") == FactoryStage.GENERATION

    def test_causal_failure_blocks_validation(self) -> None:
        factory = _factory(causal_validator=lambda c: False)
        self._reach_generation(factory)
        verdict = factory.advance("cand-1", FactoryStage.VALIDATION)
        assert verdict.passed is False
        assert "因果" in verdict.reason

    def test_backtest_gate_failure_blocks_validation(self) -> None:
        factory = _factory(backtest_gate=lambda c: False)
        self._reach_generation(factory)
        verdict = factory.advance("cand-1", FactoryStage.VALIDATION)
        assert verdict.passed is False
        assert "回测" in verdict.reason

    def test_registration_requires_passed_validation(self) -> None:
        factory = _factory(ic_validator=lambda c: False)
        self._reach_generation(factory)
        factory.advance("cand-1", FactoryStage.VALIDATION)  # 未过
        verdict = factory.advance("cand-1", FactoryStage.REGISTRATION)
        assert verdict.passed is False
        assert "验证" in verdict.reason

    def test_validation_not_rechecked_once_passed(self) -> None:
        calls = {"n": 0}

        def _ic(c: FactorCandidate) -> bool:
            calls["n"] += 1
            return True

        factory = _factory(ic_validator=_ic)
        self._reach_generation(factory)
        factory.advance("cand-1", FactoryStage.VALIDATION)
        factory.advance("cand-1", FactoryStage.REGISTRATION)
        factory.advance("cand-1", FactoryStage.MONITORING)
        assert calls["n"] == 1  # 双重验证只在验证关执行一次


class TestTransitionDiscipline:
    """阶段跳转纪律。"""

    def test_skip_stage_rejected(self) -> None:
        factory = _factory()
        factory.submit(_candidate())
        verdict = factory.advance("cand-1", FactoryStage.VALIDATION)
        assert verdict.passed is False
        assert "跳转" in verdict.reason or "顺序" in verdict.reason

    def test_backward_jump_rejected_except_iteration(self) -> None:
        factory = _factory()
        factory.submit(_candidate())
        for s in (FactoryStage.HYPOTHESIS, FactoryStage.GENERATION, FactoryStage.VALIDATION):
            factory.advance("cand-1", s)
        verdict = factory.advance("cand-1", FactoryStage.HYPOTHESIS)
        assert verdict.passed is False

    def test_iteration_re_entry_allowed_from_monitoring(self) -> None:
        factory = _factory()
        factory.submit(_candidate())
        for s in (
            FactoryStage.HYPOTHESIS,
            FactoryStage.GENERATION,
            FactoryStage.VALIDATION,
            FactoryStage.REGISTRATION,
            FactoryStage.MONITORING,
        ):
            factory.advance("cand-1", s)
        assert factory.advance("cand-1", FactoryStage.ITERATION).passed is True
        # 迭代后再回监控（重走验证+入库？——迭代后直接回监控：工厂裁定需重过验证）
        assert factory.advance("cand-1", FactoryStage.VALIDATION).passed is True

    def test_unknown_candidate_raises(self) -> None:
        factory = _factory()
        with pytest.raises(FactorFactoryError, match="未立项"):
            factory.advance("ghost", FactoryStage.HYPOTHESIS)

    def test_retirement_is_terminal(self) -> None:
        factory = _factory()
        factory.submit(_candidate())
        for s in (
            FactoryStage.HYPOTHESIS,
            FactoryStage.GENERATION,
            FactoryStage.VALIDATION,
            FactoryStage.REGISTRATION,
            FactoryStage.MONITORING,
            FactoryStage.DEPRECATION,
            FactoryStage.RETIREMENT,
        ):
            factory.advance("cand-1", s)
        verdict = factory.advance("cand-1", FactoryStage.ITERATION)
        assert verdict.passed is False


class TestMiningHookAndAudit:
    """FactorMAD 挖掘扩展点与审计。"""

    def test_mining_hook_delegates(self) -> None:
        seen: list[str] = []

        def _mine(prompt: str) -> list[FactorCandidate]:
            seen.append(prompt)
            return [_candidate("mined-1")]

        factory = _factory(mining_hook=_mine)
        mined = factory.mine("动量类因子挖掘")
        assert seen == ["动量类因子挖掘"]
        assert len(mined) == 1
        assert factory.stage_of("mined-1") == FactoryStage.CANDIDATE

    def test_mine_without_hook_raises(self) -> None:
        factory = _factory()
        with pytest.raises(FactorFactoryError, match="mining_hook"):
            factory.mine("x")

    def test_audit_trail_recorded(self) -> None:
        sink: list[dict] = []
        factory = _factory(audit_sink=sink.append)
        factory.submit(_candidate())
        factory.advance("cand-1", FactoryStage.HYPOTHESIS)
        factory.advance("cand-1", FactoryStage.GENERATION)
        factory.advance("cand-1", FactoryStage.VALIDATION)
        assert len(sink) == 4  # submit + 3 advance
        assert sink[-1]["to_stage"] == "validation"
        assert sink[-1]["passed"] is True

    def test_underlying_lifecycle_fsm_aligned(self) -> None:
        factory = _factory()
        factory.submit(_candidate())
        for s in (FactoryStage.HYPOTHESIS, FactoryStage.GENERATION, FactoryStage.VALIDATION):
            factory.advance("cand-1", s)
        assert factory.lifecycle_state_of("cand-1") == "backtest"
        factory.advance("cand-1", FactoryStage.REGISTRATION)
        assert factory.lifecycle_state_of("cand-1") == "paper"

    def test_pipeline_snapshot_immutable(self) -> None:
        factory = _factory()
        factory.submit(_candidate())
        snap = factory.pipeline_snapshot()
        assert snap["cand-1"] == "candidate"
        with pytest.raises(TypeError):
            snap["cand-1"] = "retirement"  # type: ignore[index]
