# [BLUEPRINT] MOD-BT-188 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] tests.strategy_pipeline.test_lifecycle_fsm
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] zephyr.strategy_pipeline.lifecycle_fsm
# [CONSUMERS] MOD-BT-188 循环验收
# [STARTUP] manual
# [MATURITY] experimental
# [INVARIANTS] 测试隔离零 IO；红蓝=非法直跳必抛/无 context 必拒/机器流程不可能碰 Owner 门
# [MODIFY-GUARD] src/zephyr/strategy_pipeline/lifecycle_fsm.py
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 断言失败即红
# [TESTS] 本文件
# [A_module] module_id=MOD-BT-188 | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""策略生命周期 FSM 测试——验收④条款（candidate→production 直跳必拒）+ A 方案治理边界。"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from zephyr.shared.lifecycle.state_machine import InvalidTransitionError, TransitionGuardError  # noqa: E402
from zephyr.strategy_pipeline.lifecycle_fsm import (  # noqa: E402
    CANDIDATE,
    PRODUCTION,
    REGISTRY_LIFECYCLE_ALIASES,
    RETIRED,
    SHELVED,
    SIM,
    SimPromotionContext,
    build_strategy_fsm,
)


def _ctx(dual=True, fdr=True, no_decay=True, owner=None):
    ctx: dict = {}
    if dual or fdr or not no_decay:
        ctx["sim_promotion"] = SimPromotionContext(
            dual_window_pass=dual, bh_fdr_pass=fdr, no_pending_decay_alert=no_decay
        )
    if owner:
        ctx["owner_token"] = owner
    return ctx


class TestLifecycleFsm:
    def test_auto_promotion_to_sim(self):
        fsm = build_strategy_fsm("STR-X-001")
        fsm.transition(SIM, _ctx())
        assert fsm.current_state == SIM

    def test_shelved_path_and_recovery(self):
        fsm = build_strategy_fsm("STR-X-002")
        fsm.transition(SHELVED, _ctx())  # candidate→shelved 无 guard
        fsm.transition(CANDIDATE, _ctx())  # 家族替身回补
        assert fsm.current_state == CANDIDATE

    def test_candidate_to_production_direct_jump_rejected(self):
        # 验收④红蓝：无 sim 中转的直跳必须非法
        fsm = build_strategy_fsm("STR-X-003")
        with pytest.raises(InvalidTransitionError):
            fsm.transition(PRODUCTION, _ctx(owner="OWNER"))

    def test_sim_to_production_requires_owner_token(self, monkeypatch):
        # A 方案核心：机器流程（无 owner_token）停门；token 校验=secrets 绑定（C4 生产化），
        # 未配置 ZEPHYR_OWNER_APPROVAL_TOKEN 时任何 token 都拒（fail-closed，旧"非空即真"已废）。
        monkeypatch.delenv("ZEPHYR_OWNER_APPROVAL_TOKEN", raising=False)
        fsm = build_strategy_fsm("STR-X-004")
        fsm.transition(SIM, _ctx())
        with pytest.raises(TransitionGuardError):
            fsm.transition(PRODUCTION, _ctx())  # 机器调用：不带 token
        with pytest.raises(TransitionGuardError):
            fsm.transition(PRODUCTION, {"owner_token": ""})  # 空 token 也拒
        with pytest.raises(TransitionGuardError):
            fsm.transition(PRODUCTION, _ctx(owner="OWNER"))  # 键未配置：fail-closed
        monkeypatch.setenv("ZEPHYR_OWNER_APPROVAL_TOKEN", "OWNER")  # 测试假值注入（禁读真实密钥）
        fsm.transition(PRODUCTION, _ctx(owner="OWNER"))  # Owner 签字放行（比对通过）
        assert fsm.current_state == PRODUCTION

    def test_guard_triple_conditions(self):
        # 预授权三条件逐项红
        for kwargs in ({"dual": False}, {"fdr": False}, {"no_decay": False}):
            fsm = build_strategy_fsm("STR-X-005")
            with pytest.raises(TransitionGuardError):
                fsm.transition(SIM, _ctx(**kwargs))
        # 三条件齐→过
        fsm = build_strategy_fsm("STR-X-006")
        fsm.transition(SIM, _ctx())
        assert fsm.current_state == SIM

    def test_no_context_fails_closed(self):
        fsm = build_strategy_fsm("STR-X-007")
        with pytest.raises(TransitionGuardError):
            fsm.transition(SIM, None)

    def test_production_retire_owner_gate(self, monkeypatch):
        # C4 生产化：门过=token 与 secrets 键比对一致（测试假值注入，禁读真实密钥）
        monkeypatch.setenv("ZEPHYR_OWNER_APPROVAL_TOKEN", "OWNER")
        fsm = build_strategy_fsm("STR-X-008")
        fsm.transition(SIM, _ctx())
        fsm.transition(PRODUCTION, _ctx(owner="OWNER"))
        with pytest.raises(TransitionGuardError):
            fsm.transition(RETIRED, _ctx())
        with pytest.raises(TransitionGuardError):
            fsm.transition(RETIRED, _ctx(owner="WRONG"))
        fsm.transition(RETIRED, _ctx(owner="OWNER"))
        assert fsm.current_state == RETIRED

    def test_shelved_to_retired_auto(self):
        fsm = build_strategy_fsm("STR-X-009")
        fsm.transition(SHELVED, _ctx())
        fsm.transition(RETIRED, _ctx())
        assert fsm.current_state == RETIRED


# ---------------------------------------------------------------------------
# 词表对齐层（Owner 2026-09-27 定稿：FSM 词→注册表八态词，F75 缺口 3.6 销案）
# ---------------------------------------------------------------------------


class TestRegistryVocabAlignment:
    """FSM 内部五态词不变；写注册表经 REGISTRY_LIFECYCLE_ALIASES 映射（production→live）。"""

    def test_production_maps_to_live(self):
        assert REGISTRY_LIFECYCLE_ALIASES == {PRODUCTION: "live"}

    def test_other_states_identity(self):
        for state in (CANDIDATE, SIM, SHELVED, RETIRED):
            assert REGISTRY_LIFECYCLE_ALIASES.get(state, state) == state

    def test_fsm_internal_words_unchanged(self, monkeypatch):
        """流转回执仍记 FSM 词（审计面不换词，只有注册表面换）——防映射层越界改 FSM 语义。"""
        monkeypatch.setenv("ZEPHYR_OWNER_APPROVAL_TOKEN", "OWNER")  # 测试假值注入（禁读真实密钥）
        fsm = build_strategy_fsm("STR-X-010")
        fsm.transition(SIM, _ctx())
        fsm.transition(PRODUCTION, _ctx(owner="OWNER"))
        assert fsm.current_state == "production"  # FSM 态词恒 production（注册表落 live 是映射层职责）


def test_build_strategy_fsm_initial_state_validation():
    """F75 缺口2：initial_state 参数非法值 fail-closed；sim 起步可直接走 sim→shelved。"""
    import pytest as _pytest

    from zephyr.strategy_pipeline.lifecycle_fsm import build_strategy_fsm

    with _pytest.raises(ValueError, match="initial_state"):
        build_strategy_fsm("S-X", initial_state="bogus")
    fsm = build_strategy_fsm("S-X", initial_state="sim")
    assert fsm.current_state == "sim"
