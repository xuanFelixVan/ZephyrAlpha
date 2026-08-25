# [BLUEPRINT] MOD-INF-069 | docs/03_modules/_domain_infrastructure_operations/gpu_hot_swap_model/blueprint.md | §test
# [MODULE] tests.infrastructure.test_gpu_hot_swap_model
# [DOMAIN] D_INFRA_OPS
# [DEPENDENCIES] zephyr.infrastructure.gpu_hot_swap_model
# [STARTUP] imported
# [MATURITY] evolving
# [INVARIANTS] tests_must_pass;no_todo_no_pass_no_fixme
# [MODIFY-GUARD] only_add_tests;do_not_modify_source
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError->skip_module
# [TESTS] test_gpu_hot_swap_model.py
# [A_test] module_id: MOD-INF-069 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""MOD-INF-069 单元测试: GPU 上岗热交换模型 — 两档显存画像/热交换契约/四件套收口引用。

覆盖: 盘中(8-10GB)/盘后(16-18GB)两档上岗画像真源值、热备恢复<5s目标、
显存预算 Fail-Closed 校验、热交换计划步骤、gpu:allocation 状态草稿与
MOD-INF-063 gpu 命名空间契约一致性（引用不重复建）、四件套 SSOT 收口映射。
"""

from __future__ import annotations

import pytest

from zephyr.infrastructure.gpu_hot_swap_model import (
    CROSS_CUTTING_CONTRACT,
    GPU_DUTY_PROFILES,
    HOT_SWAP_CONTRACT,
    GpuHotSwapContractError,
    GpuHotSwapModel,
)


class TestDutyProfiles:
    def test_two_sessions_registered(self):
        assert set(GPU_DUTY_PROFILES) == {"intraday_inference", "postmarket_training"}

    def test_intraday_vram_budget_8_to_10gb(self):
        p = GPU_DUTY_PROFILES["intraday_inference"]
        assert p.vram_budget_min_gb == 8
        assert p.vram_budget_max_gb == 10

    def test_postmarket_vram_budget_16_to_18gb(self):
        p = GPU_DUTY_PROFILES["postmarket_training"]
        assert p.vram_budget_min_gb == 16
        assert p.vram_budget_max_gb == 18

    def test_standby_restore_target_under_5s(self):
        assert HOT_SWAP_CONTRACT.standby_restore_target_seconds < 5.0


class TestAllocationValidation:
    def test_within_budget_accepted(self):
        model = GpuHotSwapModel()
        model.validate_allocation(9.0, "intraday_inference")  # 不抛错

    def test_over_budget_fail_closed(self):
        model = GpuHotSwapModel()
        with pytest.raises(GpuHotSwapContractError, match="显存预算"):
            model.validate_allocation(12.0, "intraday_inference")

    def test_unknown_session_fail_closed(self):
        model = GpuHotSwapModel()
        with pytest.raises(GpuHotSwapContractError, match="未知上岗会话"):
            model.validate_allocation(1.0, "weekend_backtest")


class TestSwapPlan:
    def test_swap_plan_steps_ordered(self):
        model = GpuHotSwapModel()
        plan = model.plan_swap("intraday_inference", "postmarket_training")
        kinds = [s.kind for s in plan.steps]
        assert kinds[0] == "release"  # 先释放盘中画像
        assert "load" in kinds and "verify" in kinds
        assert kinds[-1] == "verify"  # 末步校验

    def test_swap_plan_carries_target_profile(self):
        model = GpuHotSwapModel()
        plan = model.plan_swap("intraday_inference", "postmarket_training")
        assert plan.target_profile.session == "postmarket_training"
        assert plan.target_profile.vram_budget_max_gb == 18

    def test_same_session_swap_rejected(self):
        model = GpuHotSwapModel()
        with pytest.raises(GpuHotSwapContractError):
            model.plan_swap("intraday_inference", "intraday_inference")


class TestAllocationStateDraft:
    def test_render_uses_mod_inf_063_gpu_namespace(self):
        """gpu:allocation Hash 契约引用既有 SSOT（MOD-INF-063），禁止重复建。"""
        model = GpuHotSwapModel()
        draft = model.render_gpu_allocation_state("postmarket_training", allocated_gb=17.0)
        assert draft["key"] == "gpu:allocation"
        assert draft["structure"] == "Hash"
        assert draft["ttl_seconds"] is None  # gpu 命名空间永不过期（A9 §1.2）
        assert draft["fields"]["session"] == "postmarket_training"
        assert draft["fields"]["allocated_gb"] == "17.0"

    def test_render_over_budget_fail_closed(self):
        model = GpuHotSwapModel()
        with pytest.raises(GpuHotSwapContractError):
            model.render_gpu_allocation_state("intraday_inference", allocated_gb=11.0)


class TestFourPieceClosure:
    def test_contract_maps_four_pieces_to_ssot(self):
        """四件套收口：redis=MOD-INF-063 / gpu=MOD-INF-069 / 监控 / 灾备各有真源。"""
        assert set(CROSS_CUTTING_CONTRACT) == {"redis_state", "gpu_duty", "monitoring", "disaster_recovery"}
        assert CROSS_CUTTING_CONTRACT["redis_state"].owner_module_id == "MOD-INF-063"
        assert CROSS_CUTTING_CONTRACT["gpu_duty"].owner_module_id == "MOD-INF-069"

    def test_closure_check_passes(self):
        model = GpuHotSwapModel()
        report = model.check_four_piece_closure()
        assert report["closed"] is True
        assert all(report["pieces"].values())
