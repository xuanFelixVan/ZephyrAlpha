# [A_test] module_id: MOD-PA-007 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-PA-007 | docs/03_modules/_domain_portfolio_alloc/regime_meta_allocator/blueprint.md | §
# [MODULE] tests.pf_alloc.test_regime_meta_allocator
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self
# [TTL] permanent
"""RegimeMetaAllocator 单元测试 (MOD-PA-007)。

重建说明：原 55 用例在 2026-08-11 git 灾难中丢失（从未提交，git clean -fd 删除）。
本套件按 34_regime_meta_allocator §3.4 施工要点 16 条 + 代码本体（v1.0.0 production）
重建，组织保持原结构：TestConfidenceSignal(8) / TestRiskSignal(4) / TestShrinkage(7) /
TestNormalizeAndClip(8) / TestRawAllocation(3) / TestAllocate(9) /
TestComputePerformanceScore(8) / TestEdgeCases(8) = 55 用例。
"""

from __future__ import annotations

import math

import numpy as np
import pytest

import zephyr.pf_alloc.core.regime_meta_allocator as rma_module
from zephyr.pf_alloc.core.regime_meta_allocator import (
    CAP,
    COLD_START_MIN_DAYS,
    CRISIS_SHRINKAGE_FLOOR,
    DOWNSIDE_MIN_OBSERVATIONS,
    FLOOR,
    MAR_ANNUAL,
    SHRINKAGE_FLOOR,
    TRADING_DAYS,
    AllocationError,
    BudgetAllocation,
    RegimeMetaAllocator,
    SensitivityScenario,
    ShrinkageDetail,
)

MAR_DAILY = MAR_ANNUAL / TRADING_DAYS


def _risk(risk_base: float = 1.0, resonance: float = 1.0, recovery: float = 0.0) -> dict:
    return {
        "risk_base": risk_base,
        "resonance_penalty": resonance,
        "opportunity_recovery": recovery,
    }


# ── ConfidenceSignal 四档映射（§3.2.3）────────────────────────────────────────


class TestConfidenceSignal:
    """max(P) 四档：<60%→0.30 / 60-80%→0.60 / 80-95%→0.85 / ≥95%→1.00。"""

    def setup_method(self) -> None:
        self.alloc = RegimeMetaAllocator()

    def test_low_confidence_strong_shrink(self) -> None:
        # max(P)=0.50 < 0.60 → 0.30（强收缩，不确定时别赌方向）
        assert self.alloc._compute_confidence_signal([0.50, 0.30, 0.20]) == pytest.approx(0.30)

    def test_mid_confidence_moderate_shrink(self) -> None:
        # 0.60 ≤ max(P)=0.70 < 0.80 → 0.60（中度收缩）
        assert self.alloc._compute_confidence_signal([0.70, 0.20, 0.10]) == pytest.approx(0.60)

    def test_high_confidence_light_shrink(self) -> None:
        # 0.80 ≤ max(P)=0.90 < 0.95 → 0.85（轻度收缩）
        assert self.alloc._compute_confidence_signal([0.90, 0.05, 0.05]) == pytest.approx(0.85)

    def test_very_high_confidence_full_deploy(self) -> None:
        # max(P)=0.97 ≥ 0.95 → 1.00（满部署）
        assert self.alloc._compute_confidence_signal([0.97, 0.02, 0.01]) == pytest.approx(1.00)

    def test_boundary_060_maps_to_060(self) -> None:
        # 边界：max(P)=0.60 不小于 0.60 → 落入第二档 0.60
        assert self.alloc._compute_confidence_signal([0.60, 0.40]) == pytest.approx(0.60)

    def test_boundary_080_maps_to_085(self) -> None:
        # 边界：max(P)=0.80 不小于 0.80 → 落入第三档 0.85
        assert self.alloc._compute_confidence_signal([0.80, 0.20]) == pytest.approx(0.85)

    def test_boundary_095_maps_to_100(self) -> None:
        # 边界：max(P)=0.95 不小于 0.95 → 落入第四档 1.00
        assert self.alloc._compute_confidence_signal([0.95, 0.05]) == pytest.approx(1.00)

    def test_accepts_list_and_ndarray(self) -> None:
        # list 与 np.ndarray 输入等价（np.asarray 转换）
        probs_list = [0.10, 0.85, 0.05]
        probs_arr = np.array(probs_list)
        assert self.alloc._compute_confidence_signal(probs_list) == pytest.approx(
            self.alloc._compute_confidence_signal(probs_arr)
        )


# ── RiskSignal 聚合裁剪（§3.2.3，clamp[0.30, 1.00]）───────────────────────────


class TestRiskSignal:
    """RiskSignal = clamp[0.30, risk_base × resonance_penalty + opportunity_recovery, 1.00]。"""

    def setup_method(self) -> None:
        self.alloc = RegimeMetaAllocator()

    def test_default_empty_params_full_signal(self) -> None:
        # 缺省 risk_base=1.0 / resonance=1.0 / recovery=0.0 → 1.0
        assert self.alloc._compute_risk_signal({}) == pytest.approx(1.00)

    def test_normal_aggregation(self) -> None:
        # 0.8 × 0.9 + 0.05 = 0.77
        assert self.alloc._compute_risk_signal(_risk(0.8, 0.9, 0.05)) == pytest.approx(0.77)

    def test_clamp_floor_030(self) -> None:
        # 0.2 × 1.0 + 0.0 = 0.2 → clamp 到 0.30
        assert self.alloc._compute_risk_signal(_risk(0.2, 1.0, 0.0)) == pytest.approx(0.30)

    def test_clamp_ceiling_100(self) -> None:
        # 1.0 × 1.0 + 0.25 = 1.25 → clamp 到 1.00
        assert self.alloc._compute_risk_signal(_risk(1.0, 1.0, 0.25)) == pytest.approx(1.00)


# ── Shrinkage 二维公式 + CRISIS floor（§3.2.2/§3.2.3）────────────────────────


class TestShrinkage:
    """global_shrinkage = ConfidenceSignal × RiskSignal，floor 0.09 / CRISIS 0.05。"""

    def test_disabled_returns_all_one(self) -> None:
        # shrinkage_enabled=False → 全 1.0 回退（C1 一票否决机制）
        alloc = RegimeMetaAllocator(shrinkage_enabled=False)
        detail = alloc._compute_shrinkage([0.50, 0.50], _risk(0.3, 0.3))
        assert isinstance(detail, ShrinkageDetail)
        assert detail.final_shrinkage == pytest.approx(1.0)
        assert detail.confidence_signal == pytest.approx(1.0)
        assert detail.risk_signal == pytest.approx(1.0)
        assert detail.shrinkage_enabled is False

    def test_two_factor_multiplication(self) -> None:
        # conf 0.85（max(P)=0.9）× risk 0.77 = 0.6545
        alloc = RegimeMetaAllocator()
        detail = alloc._compute_shrinkage([0.10, 0.90], _risk(0.8, 0.9, 0.05))
        assert detail.confidence_signal == pytest.approx(0.85)
        assert detail.risk_signal == pytest.approx(0.77)
        assert detail.raw_shrinkage == pytest.approx(0.85 * 0.77)
        assert detail.final_shrinkage == pytest.approx(0.6545)

    def test_never_exceeds_one(self) -> None:
        # Shrinkage 只减不增：conf 1.0 × risk 1.0（recovery 超界被 clamp）→ 1.0
        alloc = RegimeMetaAllocator()
        detail = alloc._compute_shrinkage([0.99, 0.01], _risk(1.0, 1.0, 0.25))
        assert detail.final_shrinkage == pytest.approx(1.0)
        assert detail.final_shrinkage <= 1.0

    def test_floor_corner_holds_at_009(self) -> None:
        # 极端收缩角点：conf 0.30 × risk 0.30 = 0.09 = SHRINKAGE_FLOOR（恰好在 floor 上）
        alloc = RegimeMetaAllocator()
        detail = alloc._compute_shrinkage([0.50, 0.50], _risk(0.2, 1.0, 0.0))
        assert detail.raw_shrinkage == pytest.approx(0.09)
        assert detail.final_shrinkage == pytest.approx(SHRINKAGE_FLOOR)

    def test_crisis_floor_lowers_to_005(self, monkeypatch: pytest.MonkeyPatch) -> None:
        # CRISIS 态 floor 0.09→0.05（§3.4 施工要点 #12）。
        # 当前参数域 conf≥0.3 且 risk≥0.30 → raw≥0.09，crisis floor 常规不触发；
        # monkeypatch RISK_SIGNAL_MIN=0.10 模拟未来参数域 raw<0.09，验证分支逻辑。
        monkeypatch.setattr(rma_module, "RISK_SIGNAL_MIN", 0.10)
        alloc = RegimeMetaAllocator()
        normal = alloc._compute_shrinkage([0.50, 0.50], _risk(0.10), is_crisis=False)
        crisis = alloc._compute_shrinkage([0.50, 0.50], _risk(0.10), is_crisis=True)
        assert normal.raw_shrinkage == pytest.approx(0.03)
        assert normal.final_shrinkage == pytest.approx(SHRINKAGE_FLOOR)  # 0.09 兜底
        assert crisis.final_shrinkage == pytest.approx(CRISIS_SHRINKAGE_FLOOR)  # 0.05 降级
        assert crisis.is_crisis is True

    def test_crisis_floor_005_unreachable_in_current_param_domain(self) -> None:
        # AI-NIGHT-001 #208-①：CRISIS floor 0.05 在当前参数域数学不可达——
        # conf 最小档 0.30 × risk clamp 下界 0.30 → raw≥0.09>0.05，
        # max(floor=0.05, raw) 永不选中 0.05。极端收缩角点下 crisis 与常规态输出
        # 一致（均为数学下界 0.09）。该 floor 系对齐 31号 §2.4.3 的前瞻口径保留
        # （参数域放宽时生效，由上一用例 monkeypatch 验证分支可达），非误删死代码。
        alloc = RegimeMetaAllocator()
        normal = alloc._compute_shrinkage([0.50, 0.50], _risk(0.2, 1.0, 0.0), is_crisis=False)
        crisis = alloc._compute_shrinkage([0.50, 0.50], _risk(0.2, 1.0, 0.0), is_crisis=True)
        assert normal.raw_shrinkage == pytest.approx(0.09)  # 数学下界 0.30×0.30
        assert crisis.final_shrinkage == pytest.approx(SHRINKAGE_FLOOR)  # 0.09 而非 0.05
        assert crisis.final_shrinkage > CRISIS_SHRINKAGE_FLOOR
        assert crisis.final_shrinkage == pytest.approx(normal.final_shrinkage)
        assert crisis.is_crisis is True

    def test_detail_fields_populated(self) -> None:
        # ShrinkageDetail 审计字段齐全（归因用）
        alloc = RegimeMetaAllocator()
        detail = alloc._compute_shrinkage([0.10, 0.90], _risk(0.8, 0.9, 0.05), is_crisis=False)
        assert detail.confidence_signal == pytest.approx(0.85)
        assert detail.risk_signal == pytest.approx(0.77)
        assert detail.raw_shrinkage == pytest.approx(detail.final_shrinkage)
        assert detail.shrinkage_enabled is True
        assert detail.is_crisis is False

    def test_crisis_flag_propagates_when_disabled(self) -> None:
        # 边界：shrinkage_enabled=False + is_crisis=True → 仍全 1.0，但 is_crisis 标志透传
        alloc = RegimeMetaAllocator(shrinkage_enabled=False)
        detail = alloc._compute_shrinkage([0.50, 0.50], _risk(0.3), is_crisis=True)
        assert detail.final_shrinkage == pytest.approx(1.0)
        assert detail.is_crisis is True


# ── 归一化 + floor/cap water-filling 投影（§3.2.4）────────────────────────────


class TestNormalizeAndClip:
    """Σ=1.0 + floor 5% 防饿死 + cap 40% 防集中 + N=2 无解兜底。"""

    def setup_method(self) -> None:
        self.alloc = RegimeMetaAllocator()

    def _clip(self, raw: dict[str, float]) -> dict[str, float]:
        return self.alloc._normalize_and_clip(raw, list(raw.keys()))

    def test_proportional_passthrough(self) -> None:
        # 无越界 → 原比例通过（0.40 恰在 cap 边界不裁剪）
        out = self._clip({"A": 0.3, "B": 0.4, "C": 0.3})
        assert out == {"A": pytest.approx(0.3), "B": pytest.approx(0.4), "C": pytest.approx(0.3)}

    def test_normalize_scales_to_sum_one(self) -> None:
        # 非归一输入 → 缩放到 Σ=1.0
        out = self._clip({"A": 3.0, "B": 4.0, "C": 3.0})
        assert sum(out.values()) == pytest.approx(1.0)
        assert out["A"] == pytest.approx(0.3)
        assert out["B"] == pytest.approx(0.4)

    def test_floor_enforcement(self) -> None:
        # A=0.01 < floor → 固定 0.05；B/C/D（均 <cap）按比例重分剩余 0.95
        # （N=4 纯 floor 场景：N=3 时单策略过低必致他策略超 cap，floor/cap 联动非纯 floor）
        out = self._clip({"A": 0.01, "B": 0.33, "C": 0.33, "D": 0.33})
        assert out["A"] == pytest.approx(FLOOR)
        for sid in ("B", "C", "D"):
            assert out[sid] == pytest.approx(0.95 / 3)
        assert sum(out.values()) == pytest.approx(1.0)

    def test_cap_enforcement(self) -> None:
        # A=0.60 > cap → 固定 0.40；B/C 按比例放大到剩余 0.60
        out = self._clip({"A": 0.60, "B": 0.25, "C": 0.15})
        assert out["A"] == pytest.approx(CAP)
        assert out["B"] == pytest.approx(0.375)
        assert out["C"] == pytest.approx(0.225)
        assert sum(out.values()) == pytest.approx(1.0)

    def test_water_filling_preserves_free_ratio(self) -> None:
        # water-filling：越界固定后只按比例重分未越界部分（B:C=3:2 保持）
        out = self._clip({"A": 0.80, "B": 0.12, "C": 0.08})
        assert out["A"] == pytest.approx(CAP)
        assert out["B"] == pytest.approx(0.36)
        assert out["C"] == pytest.approx(0.24)
        assert out["B"] / out["C"] == pytest.approx(1.5)

    def test_n2_infeasible_cap_relaxed(self) -> None:
        # N=2 无解兜底：N×cap=0.8<1.0 → 放宽 cap 到 1-(N-1)×floor=0.95，
        # 0.75/0.25 原样保留（§9 v2.7.0：naive 再归一化会扭曲到 0.5/0.5）
        out = self._clip({"A": 3.0, "B": 1.0})
        assert out["A"] == pytest.approx(0.75)
        assert out["B"] == pytest.approx(0.25)
        assert sum(out.values()) == pytest.approx(1.0)

    def test_all_zero_raw_fallback_equal(self) -> None:
        # raw 全零 → 回退等权 1/N（log warning）
        out = self._clip({"A": 0.0, "B": 0.0, "C": 0.0})
        for sid in ("A", "B", "C"):
            assert out[sid] == pytest.approx(1.0 / 3)

    def test_multi_violation_converges(self) -> None:
        # N=5 混合越界（A 超 cap + E 低于 floor）→ ≤5 轮迭代收敛，全在界内且 Σ=1.0
        out = self._clip({"A": 0.50, "B": 0.30, "C": 0.10, "D": 0.07, "E": 0.03})
        assert out["A"] == pytest.approx(CAP)
        assert out["E"] == pytest.approx(FLOOR)
        for sid in ("B", "C", "D"):
            assert FLOOR <= out[sid] <= CAP
        assert sum(out.values()) == pytest.approx(1.0)


# ── Base×Perf 后验乘法（§3.4 施工要点 #4）─────────────────────────────────────


class TestRawAllocation:
    """raw_i = Base_i × PerformanceScore_i；Shrinkage 全局归一化约掉不参与。"""

    def test_base_times_perf_exact(self) -> None:
        alloc = RegimeMetaAllocator(base_weights={"A": 0.5, "B": 0.5})
        raw = alloc._compute_raw_allocation({"A": 1.2, "B": 0.8}, {"A": 0.5, "B": 0.5}, ["A", "B"])
        assert raw["A"] == pytest.approx(0.6)
        assert raw["B"] == pytest.approx(0.4)

    def test_missing_base_filled_equal_weight(self) -> None:
        # 未提供 base_weights → 等权 1/N 补齐（§3.2.1 冷启动无信息先验）
        alloc = RegimeMetaAllocator()
        base = alloc._resolve_base_weights(["A", "B", "C"])
        for sid in ("A", "B", "C"):
            assert base[sid] == pytest.approx(1.0 / 3)

    def test_allocations_invariant_to_shrinkage_toggle(self) -> None:
        # allocation/global_shrinkage 解耦：开关 Shrinkage 只改 global_shrinkage，
        # allocations（相对占比）完全一致——regime 只回答"多谨慎"不回答"偏向谁"
        kwargs = dict(
            regime_probabilities=[0.50, 0.50],
            performance_scores={"A": 1.2, "B": 0.8, "C": 1.0},
            risk_signal_inputs=_risk(0.5, 1.0, 0.0),
        )
        on = RegimeMetaAllocator(shrinkage_enabled=True).allocate(**kwargs)
        off = RegimeMetaAllocator(shrinkage_enabled=False).allocate(**kwargs)
        assert on.allocations == off.allocations
        assert on.global_shrinkage != off.global_shrinkage


# ── allocate() 主入口 5 步流程（§3.4）─────────────────────────────────────────


class TestAllocate:
    """PerformanceScore → global_shrinkage → raw_allocation → normalize+clip → effective。"""

    def test_happy_path_three_strategies(self) -> None:
        # 等权 + 全中性 perf + max(P)=0.9（conf 0.85）+ 无风险 → alloc 1/3，eff=1/3×0.85
        alloc = RegimeMetaAllocator()
        budget = alloc.allocate([0.05, 0.90, 0.05], {"A": 1.0, "B": 1.0, "C": 1.0}, {})
        assert isinstance(budget, BudgetAllocation)
        for sid in ("A", "B", "C"):
            assert budget.allocations[sid] == pytest.approx(1.0 / 3)
            assert budget.effective_budgets[sid] == pytest.approx(1.0 / 3 * 0.85)
        assert budget.global_shrinkage == pytest.approx(0.85)
        assert sum(budget.effective_budgets.values()) == pytest.approx(0.85)

    def test_allocations_sum_to_one_invariant(self) -> None:
        # Σ allocations = 1.0 不变量（常规输入域）
        alloc = RegimeMetaAllocator(base_weights={"A": 0.5, "B": 0.3, "C": 0.2})
        budget = alloc.allocate([0.70, 0.30], {"A": 1.4, "B": 0.6, "C": 1.0}, _risk(0.7))
        assert sum(budget.allocations.values()) == pytest.approx(1.0)

    def test_effective_budget_identity(self) -> None:
        # effective_budget_i = allocation_i × global_shrinkage（§3.1 两个层次）
        alloc = RegimeMetaAllocator()
        budget = alloc.allocate([0.97, 0.03], {"A": 1.1, "B": 0.9}, _risk(0.85, 1.0, 0.0))
        for sid in ("A", "B"):
            assert budget.effective_budgets[sid] == pytest.approx(budget.allocations[sid] * budget.global_shrinkage)

    def test_empty_strategies_raises(self) -> None:
        # ZA-PA-0007：策略列表为空 → AllocationError
        alloc = RegimeMetaAllocator()
        with pytest.raises(AllocationError):
            alloc.allocate([0.90, 0.10], {}, {})

    def test_shrinkage_disabled_full_effective(self) -> None:
        # shrinkage_enabled=False → global_shrinkage=1.0，effective=allocation
        alloc = RegimeMetaAllocator(shrinkage_enabled=False)
        budget = alloc.allocate([0.50, 0.50], {"A": 1.0, "B": 1.0}, _risk(0.3))
        assert budget.global_shrinkage == pytest.approx(1.0)
        assert budget.shrinkage_detail.shrinkage_enabled is False
        for sid in ("A", "B"):
            assert budget.effective_budgets[sid] == pytest.approx(budget.allocations[sid])

    def test_cold_start_forces_neutral(self) -> None:
        # 样本 10 天 < 30 → perf 1.5 被强制 1.0 中性（防上游误传，§3.4 施工要点 #6）
        alloc = RegimeMetaAllocator(base_weights={"A": 0.34, "B": 0.33, "C": 0.33})
        budget = alloc.allocate(
            [0.90, 0.10],
            {"A": 1.5, "B": 1.0, "C": 1.0},
            {},
            strategy_sample_days={"A": 10, "B": 100, "C": 100},
        )
        assert budget.perf_scores["A"] == pytest.approx(1.0)
        # 强制中性后 raw=0.34/0.33/0.33 无越界原样通过（未强制会 cap 裁剪 A→0.40）
        assert budget.allocations["A"] == pytest.approx(0.34)

    def test_crisis_propagates_to_detail(self) -> None:
        # is_crisis=True → ShrinkageDetail.is_crisis=True（CRISIS floor 分支，施工要点 #12）
        alloc = RegimeMetaAllocator()
        budget = alloc.allocate([0.50, 0.50], {"A": 1.0, "B": 1.0}, _risk(0.5), is_crisis=True)
        assert budget.shrinkage_detail.is_crisis is True
        assert budget.global_shrinkage >= CRISIS_SHRINKAGE_FLOOR

    def test_audit_fields_populated(self) -> None:
        # BudgetAllocation 审计字段：perf_scores 回显 + shrinkage_detail + schema_version
        alloc = RegimeMetaAllocator()
        budget = alloc.allocate([0.90, 0.10], {"A": 1.2, "B": 0.8}, _risk(0.9))
        assert budget.perf_scores == {"A": pytest.approx(1.2), "B": pytest.approx(0.8)}
        assert budget.shrinkage_detail.confidence_signal == pytest.approx(0.85)
        assert budget.shrinkage_detail.risk_signal == pytest.approx(0.9)
        assert budget.schema_version == "1.0"
        assert budget.created_at is not None

    def test_custom_base_weights_preserved(self) -> None:
        # 人工先验（打板 0.3/多因子 0.4/事件 0.3，§3.2.1）+ 全中性 perf → 比例保留
        alloc = RegimeMetaAllocator(base_weights={"daban": 0.3, "multi_factor": 0.4, "event": 0.3})
        budget = alloc.allocate([0.97, 0.03], {"daban": 1.0, "multi_factor": 1.0, "event": 1.0}, {})
        assert budget.allocations["daban"] == pytest.approx(0.3)
        assert budget.allocations["multi_factor"] == pytest.approx(0.4)
        assert budget.allocations["event"] == pytest.approx(0.3)


# ── compute_performance_score 静态方法（§3.2.2 + 施工要点 #9/#10/#13）─────────


class TestComputePerformanceScore:
    """60 日 Sortino → [0.5,1.5]；MAR=Rf=2%；downside≥15 门槛；冷启动 30 日。"""

    def test_cold_start_below_30_days_neutral(self) -> None:
        # 上线 10 交易日 < 30 → (1.0, 1.0, 1.0) 中性（交易日口径，施工要点 #9）
        perf, sortino, sharpe = RegimeMetaAllocator.compute_performance_score([0.01] * 10, trading_days_live=10)
        assert perf == pytest.approx(1.0)
        assert sortino == pytest.approx(1.0)
        assert sharpe == pytest.approx(1.0)

    def test_empty_returns_neutral(self) -> None:
        # 空收益序列（days_live≥30）→ 中性兜底
        perf, _, _ = RegimeMetaAllocator.compute_performance_score([], trading_days_live=45)
        assert perf == pytest.approx(1.0)

    def test_insufficient_downside_forced_neutral(self) -> None:
        # downside=10 < 15 → Sortino 统计不可靠，强制 1.0 中性（四件套 #1）
        returns = [0.01] * 50 + [-0.002] * 10
        perf, sortino, sharpe = RegimeMetaAllocator.compute_performance_score(returns)
        assert perf == pytest.approx(1.0)
        assert sortino == pytest.approx(1.0)
        assert sharpe == pytest.approx(1.0)

    def test_negative_sortino_maps_to_floor(self) -> None:
        # 60 日全亏（每日 -0.5%，downside=60≥15）→ Sortino<0 → perf=0.5
        perf, sortino, _ = RegimeMetaAllocator.compute_performance_score([-0.005] * 60)
        assert sortino < 0.0
        assert perf == pytest.approx(0.5)

    def test_high_sortino_maps_to_ceiling(self) -> None:
        # 强正漂移 + 小下行波动（45 涨 2% / 15 跌 0.5%）→ Sortino≥2 → perf=1.5
        returns = [0.02] * 45 + [-0.005] * 15
        perf, sortino, _ = RegimeMetaAllocator.compute_performance_score(returns)
        assert sortino >= 2.0
        assert perf == pytest.approx(1.5)

    def test_linear_mapping_midpoint(self) -> None:
        # 0<Sortino<2 区间线性映射：perf = 0.5 + sortino/2（构造 sortino≈1.0 → perf≈1.0）
        # 30 涨 u + 30 跌 d，d=0.01、u≈0.0110644 使年化超额/年化下行偏差≈1.0
        u, d = 0.0110644, 0.01
        returns = [u] * 30 + [-d] * 30
        perf, sortino, _ = RegimeMetaAllocator.compute_performance_score(returns)
        assert 0.0 < sortino < 2.0
        assert sortino == pytest.approx(1.0, abs=0.02)
        assert perf == pytest.approx(0.5 + sortino / 2.0, abs=1e-6)

    def test_downside_deviation_denominator_n_minus_1(self) -> None:
        # CRITICAL 回归（施工要点 #13）：下行偏差分母 = n-1（总样本量），
        # 非 n_downside-1（仅下行观测数，CFA 2026 共识的常见实现错误）。
        # 30 日（15 跌 1% / 15 涨 2%）：正确 sortino≈10.7764，错误版≈7.4867。
        returns = [0.02] * 15 + [-0.01] * 15
        n = len(returns)
        sum_sq_downside = 15 * (-0.01 - MAR_DAILY) ** 2
        expected_dev = math.sqrt(sum_sq_downside / (n - 1)) * math.sqrt(TRADING_DAYS)
        r_p_annual = (15 * 0.02 - 15 * 0.01) / n * TRADING_DAYS
        expected_sortino = (r_p_annual - MAR_ANNUAL) / expected_dev
        buggy_dev = math.sqrt(sum_sq_downside / (15 - 1)) * math.sqrt(TRADING_DAYS)
        buggy_sortino = (r_p_annual - MAR_ANNUAL) / buggy_dev

        _, sortino, _ = RegimeMetaAllocator.compute_performance_score(returns)
        assert sortino == pytest.approx(expected_sortino, rel=1e-3)
        assert sortino != pytest.approx(buggy_sortino, rel=1e-3)

    def test_upside_volatility_sortino_exceeds_sharpe(self) -> None:
        # 涨停型 upside 波动（10 日 +5%）→ Sortino >> Sharpe（gap 监控语义，四件套 #3）
        returns = [0.01] * 30 + [0.05] * 10 + [-0.005] * 20
        _, sortino, sharpe = RegimeMetaAllocator.compute_performance_score(returns)
        assert sortino > sharpe


# ── 边界与异常 ────────────────────────────────────────────────────────────────


class TestEdgeCases:
    """N=1/N=2/列表输入/4 态·7 态向量/缺省参数/全冷启动/退化输入。"""

    def test_single_strategy_full_allocation(self) -> None:
        # N=1：cap 放宽到 1.0（N×cap<1 兜底），单策略拿全部占比
        alloc = RegimeMetaAllocator()
        budget = alloc.allocate([0.90, 0.10], {"ONLY": 1.3}, {})
        assert budget.allocations["ONLY"] == pytest.approx(1.0)
        assert budget.effective_budgets["ONLY"] == pytest.approx(budget.global_shrinkage)

    def test_two_strategies_passthrough(self) -> None:
        # N=2 常规比例 0.6/0.4 在放宽 cap=0.95 下无裁剪通过
        alloc = RegimeMetaAllocator()
        budget = alloc.allocate([0.90, 0.10], {"A": 1.2, "B": 0.8}, {})
        assert budget.allocations["A"] == pytest.approx(0.6)
        assert budget.allocations["B"] == pytest.approx(0.4)

    def test_list_input_regime_probabilities(self) -> None:
        # regime_probabilities 传 Python list（非 ndarray）正常工作
        alloc = RegimeMetaAllocator()
        budget = alloc.allocate([0.60, 0.40], {"A": 1.0, "B": 1.0}, {})
        assert budget.shrinkage_detail.confidence_signal == pytest.approx(0.60)

    def test_four_state_hmm_realistic_vector(self) -> None:
        # 实测 4 态频率（11 号 §0.5.2：r1 27.6%/r2 37.4%/r3 14.9%/r4 20.2%）
        # max(P)=0.374 < 0.60 → conf 0.30（4 态均衡分布天然低确信）
        alloc = RegimeMetaAllocator()
        budget = alloc.allocate([0.276, 0.374, 0.149, 0.202], {"A": 1.0, "B": 1.0}, {})
        assert budget.shrinkage_detail.confidence_signal == pytest.approx(0.30)

    def test_seven_dim_with_overlay_states(self) -> None:
        # 7 维向量（4 HMM 基态 + 3 overlay 特殊态，MOD-REGIME-001 输出形态）
        alloc = RegimeMetaAllocator()
        budget = alloc.allocate([0.10, 0.70, 0.05, 0.05, 0.05, 0.03, 0.02], {"A": 1.0, "B": 1.0}, {})
        assert budget.shrinkage_detail.confidence_signal == pytest.approx(0.60)

    def test_missing_risk_param_keys_defaults(self) -> None:
        # risk_signal_inputs 缺键 → 默认 1.0/1.0/0.0 → risk=1.0
        alloc = RegimeMetaAllocator()
        budget = alloc.allocate([0.97, 0.03], {"A": 1.0, "B": 1.0}, {"unexpected_key": 0.1})
        assert budget.shrinkage_detail.risk_signal == pytest.approx(1.0)

    def test_all_strategies_cold_start_keeps_base_prior(self) -> None:
        # 全策略 <30 日冷启动 → perf 全强制 1.0，allocations ∝ Base 先验
        # （先验取 cap 内值 0.35/0.35/0.30；未强制中性 raw=0.525/0.175/0.36 会触发 cap 裁剪）
        alloc = RegimeMetaAllocator(base_weights={"A": 0.35, "B": 0.35, "C": 0.30})
        budget = alloc.allocate(
            [0.90, 0.10],
            {"A": 1.5, "B": 0.5, "C": 1.2},
            {},
            strategy_sample_days={"A": 5, "B": 12, "C": 0},
        )
        assert budget.allocations["A"] == pytest.approx(0.35)
        assert budget.allocations["B"] == pytest.approx(0.35)
        assert budget.allocations["C"] == pytest.approx(0.30)

    def test_all_breached_water_filling_sum_equals_one(self) -> None:
        # AI-NIGHT-001 #206：全策略同轮越界时 water-filling 提前 break（free_sids 空），
        # 原实现裁剪后 Σ≠1（实证 base={0.98,0.01,0.01} → Σ=0.5；N=25 全贴 floor →
        # Σ=1.25）——Σ=1.0 硬不变量兜底：按比例归一化，floor/cap 让位。
        alloc = RegimeMetaAllocator()
        # 场景1：单极偏斜（0.98 超 cap=0.40，其余低于 floor=0.05）→ 全越界
        result = alloc._normalize_and_clip({"A": 0.98, "B": 0.01, "C": 0.01}, ["A", "B", "C"])
        assert sum(result.values()) == pytest.approx(1.0), f"Σ={sum(result.values())} 必须为 1.0"
        # 场景2：N=25 全贴 floor（25×0.05=1.25>1）→ floor 不可行，兜底归一化
        sids = [f"S{i}" for i in range(25)]
        result2 = alloc._normalize_and_clip({sid: 1.0 for sid in sids}, sids)
        assert sum(result2.values()) == pytest.approx(1.0), f"N=25 Σ={sum(result2.values())} 必须为 1.0"

    def test_degenerate_all_violate_bounds(self) -> None:
        # 退化输入（极端人工先验 0.98/0.01/0.01）：三策略同时越界全部固定，
        # water-filling 无 free 策略可重分 → 输出 0.40/0.05/0.05。
        # 代码本体行为：防饿死/防集中硬约束优先于 Σ=1.0（退化输入下两者数学不可兼得）。
        # 2026-08-19 AI-NIGHT-001 #206 裁定反转：Σ=1.0 是头注 INVARIANTS 硬不变量，
        # 破产时按比例归一化（floor/cap 让位）——0.40/0.05/0.05 → 0.80/0.10/0.10，
        # Σ=1.0（原"Σ=0.5 闲置 50% 资金"静默失效形态消除）。
        alloc = RegimeMetaAllocator(base_weights={"A": 0.98, "B": 0.01, "C": 0.01})
        budget = alloc.allocate([0.90, 0.10], {"A": 1.0, "B": 1.0, "C": 1.0}, {})
        assert budget.allocations["A"] == pytest.approx(0.80)
        assert budget.allocations["B"] == pytest.approx(0.10)
        assert budget.allocations["C"] == pytest.approx(0.10)
        assert sum(budget.allocations.values()) == pytest.approx(1.0)


# ── 冷启动执行比例（30号 §6.7 施工指导：allocate() cold_start_ratios 参数）─────


class TestColdStartRatios:
    """cold_start_ratios：effective_budget 层缩放（只缩不放，不参与归一化）。"""

    def test_default_none_zero_scaling(self) -> None:
        """None（默认）→ 零缩放，与不传参数行为完全一致（零回归）。"""
        alloc = RegimeMetaAllocator()
        b1 = alloc.allocate([0.97, 0.03], {"A": 1.0, "B": 1.0}, _risk())
        assert b1.cold_start_ratios == {}
        assert b1.effective_budgets["A"] == pytest.approx(b1.allocations["A"] * b1.global_shrinkage)

    def test_cold_start_scales_effective_budget(self) -> None:
        """×0.30 只缩 effective_budget，不动 allocations 归一化（31号 §2.4.1 执行时机）。"""
        alloc = RegimeMetaAllocator()
        budget = alloc.allocate(
            [0.97, 0.03],
            {"A": 1.0, "B": 1.0},
            _risk(),
            cold_start_ratios={"A": 0.30},
        )
        # allocations 不受冷启动影响（Σ=1.0 硬不变量不受侵蚀）
        assert sum(budget.allocations.values()) == pytest.approx(1.0)
        # A 实收 = allocation × shrinkage × 0.30；B 未传 → ×1.0
        assert budget.effective_budgets["A"] == pytest.approx(budget.allocations["A"] * budget.global_shrinkage * 0.30)
        assert budget.effective_budgets["B"] == pytest.approx(budget.allocations["B"] * budget.global_shrinkage)
        # 审计留痕
        assert budget.cold_start_ratios == {"A": 0.30}

    def test_ratio_boundary_one_and_invalid(self) -> None:
        """ratio=1.0 边界合法；0 / 负 / >1 → AllocationError（只缩不放）。"""
        alloc = RegimeMetaAllocator()
        budget = alloc.allocate([0.97, 0.03], {"A": 1.0}, _risk(), cold_start_ratios={"A": 1.0})
        assert budget.effective_budgets["A"] == pytest.approx(budget.global_shrinkage)
        for bad in (0.0, -0.1, 1.5):
            with pytest.raises(AllocationError, match="cold_start_ratio"):
                alloc.allocate([0.97, 0.03], {"A": 1.0}, _risk(), cold_start_ratios={"A": bad})

    def test_unknown_strategy_ratio_ignored_safely(self) -> None:
        """cold_start_ratios 含非本轮策略的键 → 不影响本轮输出（防御性）。"""
        alloc = RegimeMetaAllocator()
        budget = alloc.allocate(
            [0.97, 0.03],
            {"A": 1.0},
            _risk(),
            cold_start_ratios={"GHOST": 0.3},
        )
        assert budget.effective_budgets["A"] == pytest.approx(budget.global_shrinkage)


# ── D1 ±20% 敏感性网格（11号 §0.5.7 / 34号 §3.2.7 四档阈值校准）───────────────


class TestConfidenceThresholdSensitivityGrid:
    """confidence_threshold_sensitivity_grid：阈值 ±20% 扰动的分配敏感性分析。"""

    def _scenarios(self) -> list:
        return [
            SensitivityScenario(
                name="mid_confidence",
                regime_probabilities=[0.70, 0.20, 0.10],  # max(P)=0.70 落第二档
                performance_scores={"A": 1.0, "B": 1.0},
                risk_signal_inputs=_risk(),
            )
        ]

    def test_grid_shape_and_baseline(self) -> None:
        """网格 5 档（-20%/-10%/0/+10%/+20%），δ=0 档与 baseline 一致。"""
        alloc = RegimeMetaAllocator()
        results = alloc.confidence_threshold_sensitivity_grid(self._scenarios())
        assert len(results) == 1
        res = results[0]
        assert len(res.grid) == 5
        deltas = [g.perturbation for g in res.grid]
        assert deltas[2] == pytest.approx(0.0)
        assert deltas[0] == pytest.approx(-0.20)
        assert deltas[-1] == pytest.approx(0.20)
        # δ=0 档与 baseline 零变化
        assert res.grid[2].max_rel_change == pytest.approx(0.0)
        assert res.grid[2].global_shrinkage == pytest.approx(res.baseline_shrinkage)

    def test_mid_confidence_scenario_is_sensitive(self) -> None:
        """max(P)=0.70 居二档中段：阈值扰动 ±20% 会跨档（0.48/0.56/0.64/0.72 边界移动）
        → effective_budget 变化显著，verdict 反映敏感性（悬崖型疑似由 34号 §3.2.7 登记调阈值）。"""
        alloc = RegimeMetaAllocator()
        res = alloc.confidence_threshold_sensitivity_grid(self._scenarios())[0]
        # 阈值 -20% 扰动：0.60→0.48，max(P)=0.70 仍二档；+20%：0.80→0.96，0.70 跌一档
        # 至少一档跨档 → max_rel_change > 0
        assert res.max_rel_change > 0
        assert res.verdict in ("robust", "cliff_suspect")

    def test_extreme_confidence_scenario_robust(self) -> None:
        """max(P)=0.50 远低于所有扰动后阈值（最低 0.48）→ 部分档位仍变（0.50 vs 0.48 跨档），
        max(P)=0.30 则全档位同档 → 完全稳健。"""
        alloc = RegimeMetaAllocator()
        res = alloc.confidence_threshold_sensitivity_grid(
            [
                SensitivityScenario(
                    name="deep_low",
                    regime_probabilities=[0.30, 0.30, 0.40 - 0.0],  # max(P)=0.40
                    performance_scores={"A": 1.0},
                    risk_signal_inputs=_risk(),
                )
            ]
        )[0]
        # max(P)=0.40：扰动后一档边界 ∈[0.48,0.72]，全部 > 0.40 → 恒一档 → 零变化
        assert res.max_rel_change == pytest.approx(0.0)
        assert res.verdict == "robust"

    def test_invalid_grid_params_raise(self) -> None:
        """steps 偶数/<3、perturbation 越界 → AllocationError。"""
        alloc = RegimeMetaAllocator()
        with pytest.raises(AllocationError):
            alloc.confidence_threshold_sensitivity_grid(self._scenarios(), steps=4)
        with pytest.raises(AllocationError):
            alloc.confidence_threshold_sensitivity_grid(self._scenarios(), steps=2)
        with pytest.raises(AllocationError):
            alloc.confidence_threshold_sensitivity_grid(self._scenarios(), perturbation=1.5)

    def test_grid_does_not_mutate_self(self) -> None:
        """网格分析不改动本实例阈值表（探针克隆模式）。"""
        alloc = RegimeMetaAllocator()
        before = list(alloc._confidence_thresholds)
        alloc.confidence_threshold_sensitivity_grid(self._scenarios())
        assert alloc._confidence_thresholds == before

    def test_perturbed_thresholds_clamped(self) -> None:
        """扰动后边界钳制 [0.01,0.99]，sentinel 末位（1.01）不动。"""
        alloc = RegimeMetaAllocator()
        perturbed = alloc._perturbed_thresholds(0.20)
        # 0.95×1.2=1.14 → 钳到 0.99；sentinel 1.01 不动
        assert perturbed[2][0] == pytest.approx(0.99)
        assert perturbed[-1][0] == pytest.approx(1.01)
        perturbed_down = alloc._perturbed_thresholds(-0.20)
        assert perturbed_down[0][0] == pytest.approx(0.48)  # 0.60×0.8
