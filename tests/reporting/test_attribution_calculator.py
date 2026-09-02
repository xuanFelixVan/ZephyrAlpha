# [BLUEPRINT] MOD-RPT-036 | 待统筹登记（54号 BM-REC-02-B 绩效归因计算器，§3.2 施工算法落码） | §test
# [MODULE] tests.reporting.test_attribution_calculator
# [DOMAIN] D_REPORTING
# [INVARIANTS] BHB守恒（三效应之和=超额收益）; Carino恒等（Σlinked=几何超额收益, residual浮点精度级）; T+1拆分恒等（realized+unrealized=selection总）; 非法输入fail-closed(ValueError); 纯计算零DB零IO
# [MODIFY-GUARD] none
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ValueError
# [TESTS] self
# [A_test] module_id: MOD-RPT-036 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""绩效归因计算器单元测试（54 号 BM-REC-02-B，memo §3.2/§5.1 施工算法）。

覆盖：
- calc_single_period_brinson：手算黄金数 / BHB 守恒 / 负权重与空分段 fail-closed；
- carino_link_periods：恒等式 Σ linked == 几何超额收益（residual < 1e-6 门禁）
  / 零超额退化（k_t 洛必达极限）/ 单期 / 长度不齐 fail-closed；
- get_sector / set_sector_map：命中 / 缺失降级 "未知板块"；
- calc_brinson_with_t1_settlement：无新仓退化 / realized+unrealized==selection 总
  / t1_warning >50% 浮盈触发 / t1_locked_weight 汇总；
- build_linked_attribution_report：产出 CTR-P1-009（linked 三效应 + total_return
  = G − transaction_cost_drag）/ residual 硬门禁 strict 拒发 / 非法输入拒收。
全内存计算，零 DB 零网络。
"""

from __future__ import annotations

import math

import pytest

from zephyr.reporting.attribution_calculator import (
    SW_UNKNOWN_SECTOR,
    build_linked_attribution_report,
    calc_brinson_with_t1_settlement,
    calc_single_period_brinson,
    carino_link_periods,
    get_sector,
    set_sector_map,
)

# ── 手算黄金数夹具（两板块）──
# 科技: wp=0.6 wb=0.5 rp=0.10 rb=0.04 → alloc +0.004 / sel +0.030 / inter +0.006
# 银行: wp=0.4 wb=0.5 rp=0.02 rb=0.02 → alloc -0.002 / sel 0     / inter 0
# 合计: alloc=0.002 sel=0.030 inter=0.006 active=0.038
# 守恒: R_p=0.068, R_b=0.030, R_p-R_b=0.038
_P_W = {"科技": 0.6, "银行": 0.4}
_B_W = {"科技": 0.5, "银行": 0.5}
_P_R = {"科技": 0.10, "银行": 0.02}
_B_R = {"科技": 0.04, "银行": 0.02}


@pytest.fixture(autouse=True)
def _reset_sector_map():
    """每个用例前后清空板块映射，防模块级缓存串扰。"""
    set_sector_map(None)
    yield
    set_sector_map(None)


class TestSinglePeriodBrinson:
    def test_golden_numbers(self):
        r = calc_single_period_brinson(_P_W, _B_W, _P_R, _B_R, 0.03)
        assert r["allocation_effect"] == pytest.approx(0.002, abs=1e-12)
        assert r["selection_effect"] == pytest.approx(0.030, abs=1e-12)
        assert r["interaction_effect"] == pytest.approx(0.006, abs=1e-12)
        assert r["single_period_active_return"] == pytest.approx(0.038, abs=1e-12)

    def test_conservation_equals_rp_minus_rb(self):
        r = calc_single_period_brinson(_P_W, _B_W, _P_R, _B_R, 0.03)
        rp = sum(_P_W[s] * _P_R[s] for s in _P_W)
        rb = sum(_B_W[s] * _B_R[s] for s in _B_W)
        total = r["allocation_effect"] + r["selection_effect"] + r["interaction_effect"]
        assert total == pytest.approx(rp - rb, abs=1e-12)

    def test_disjoint_sectors_union(self):
        # 组合独有/基准独有板块按权重 0 补位（memo：sectors = 两侧并集）
        r = calc_single_period_brinson({"科技": 1.0}, {"银行": 1.0}, {"科技": 0.05}, {"银行": 0.01}, 0.01)
        # alloc = (1-0)*0 + (0-1)*0.01 = -0.01；sel = 0*... + 1*(0-0.01) = -0.01
        # inter = (1-0)*(0.05-0) + (0-1)*(0-0.01) = 0.05+0.01=0.06；active = 0.05-0.01=0.04
        assert r["single_period_active_return"] == pytest.approx(0.04, abs=1e-12)
        assert r["interaction_effect"] == pytest.approx(0.06, abs=1e-12)

    def test_negative_weight_rejected(self):
        with pytest.raises(ValueError, match="负"):
            calc_single_period_brinson({"科技": -0.1}, {}, {}, {})

    def test_empty_segments_rejected(self):
        with pytest.raises(ValueError, match="空"):
            calc_single_period_brinson({}, {}, {}, {})


class TestCarinoLinkPeriods:
    @staticmethod
    def _two_period_inputs():
        # 单板块 wp=wb=1 → alloc=inter=0，sel=active，便于手算
        p_rets = [0.02, -0.01]
        b_rets = [0.01, 0.00]
        effects = [
            calc_single_period_brinson({"X": 1.0}, {"X": 1.0}, {"X": rp}, {"X": rb}, rb)
            for rp, rb in zip(p_rets, b_rets, strict=True)
        ]
        return effects, p_rets, b_rets

    def test_identity_residual_near_zero(self):
        effects, p_rets, b_rets = self._two_period_inputs()
        r = carino_link_periods(effects, p_rets, b_rets)
        g = (1.02 * 0.99) / (1.01 * 1.00) - 1.0
        assert r["geometric_active_return"] == pytest.approx(g, abs=1e-15)
        assert abs(r["carino_residual"]) < 1e-9
        assert r["residual_quality"] == "PASS"
        # alloc/inter 恒 0，全部超额归入 selection
        assert r["linked_allocation_effect"] == pytest.approx(0.0, abs=1e-12)
        assert r["linked_interaction_effect"] == pytest.approx(0.0, abs=1e-12)
        assert r["linked_selection_effect"] == pytest.approx(g, abs=1e-9)

    def test_zero_active_degenerates(self):
        # R_p≡R_b → G=0、A→1、k_t→1/(1+R_p) 洛必达退化路径
        effects = [{"allocation_effect": 0.0, "selection_effect": 0.0, "interaction_effect": 0.0} for _ in range(3)]
        r = carino_link_periods(effects, [0.01, 0.02, -0.01], [0.01, 0.02, -0.01])
        assert r["geometric_active_return"] == pytest.approx(0.0, abs=1e-15)
        assert r["residual_quality"] == "PASS"

    def test_single_period(self):
        effects = [{"allocation_effect": 0.001, "selection_effect": 0.002, "interaction_effect": 0.0}]
        r = carino_link_periods(effects, [0.013], [0.010])
        assert abs(r["carino_residual"]) < 1e-9
        assert (
            r["linked_allocation_effect"] + r["linked_selection_effect"] + r["linked_interaction_effect"]
        ) == pytest.approx(r["geometric_active_return"], abs=1e-9)

    def test_length_mismatch_rejected(self):
        with pytest.raises(ValueError, match="长度"):
            carino_link_periods([{"allocation_effect": 0.0}], [0.01, 0.02], [0.01])

    def test_empty_periods_rejected(self):
        with pytest.raises(ValueError, match="空"):
            carino_link_periods([], [], [])


class TestSectorMap:
    def test_hit_and_miss(self):
        set_sector_map({"000001": "银行", "600519": "食品饮料"})
        assert get_sector("000001") == "银行"
        assert get_sector("999999") == SW_UNKNOWN_SECTOR

    def test_reset_with_none(self):
        set_sector_map({"000001": "银行"})
        set_sector_map(None)
        assert get_sector("000001") == SW_UNKNOWN_SECTOR


class TestT1SettlementSplit:
    _PW = {"科技": 0.5, "银行": 0.5}
    _BW = {"科技": 0.5, "银行": 0.5}
    _PR = {"科技": 0.10, "银行": 0.0}
    _BR = {"科技": 0.02, "银行": 0.0}

    def test_no_new_positions_degenerates(self):
        r = calc_brinson_with_t1_settlement(self._PW, self._BW, self._PR, self._BR, 0.01)
        # base sel = 0.5*(0.10-0.02) + 0.5*0 = 0.04
        assert r["selection_effect_total"] == pytest.approx(0.04, abs=1e-12)
        assert r["unrealized_selection_effect"] == pytest.approx(0.0, abs=1e-12)
        assert r["realized_selection_effect"] == pytest.approx(0.04, abs=1e-12)
        assert r["t1_locked_weight"] == 0.0
        assert r["t1_warning"] is False

    def test_split_identity_and_warning(self):
        set_sector_map({"000001": "科技"})
        new_pos = {"000001": {"weight": 0.25, "day_return": 0.12}}
        r = calc_brinson_with_t1_settlement(self._PW, self._BW, self._PR, self._BR, 0.01, new_positions_today=new_pos)
        # λ=0.25/0.5=0.5；unrealized = 0.5 * 0.5 * (0.12-0.02) = 0.025
        assert r["unrealized_selection_effect"] == pytest.approx(0.025, abs=1e-12)
        # 拆分恒等：realized + unrealized == selection 总
        assert (r["realized_selection_effect"] + r["unrealized_selection_effect"]) == pytest.approx(
            r["selection_effect_total"], abs=1e-12
        )
        assert r["t1_locked_weight"] == pytest.approx(0.25, abs=1e-12)
        # 0.025/0.04 = 62.5% > 50% → 警示
        assert r["t1_warning"] is True
        # allocation/interaction 不受 T+1 影响
        base = calc_single_period_brinson(self._PW, self._BW, self._PR, self._BR, 0.01)
        assert r["allocation_effect"] == pytest.approx(base["allocation_effect"], abs=1e-12)
        assert r["interaction_effect"] == pytest.approx(base["interaction_effect"], abs=1e-12)


class TestBuildLinkedAttributionReport:
    @staticmethod
    def _period_inputs():
        return [
            {  # T1：科技超配且跑赢
                "portfolio_weights": {"科技": 0.6, "银行": 0.4},
                "benchmark_weights": {"科技": 0.5, "银行": 0.5},
                "portfolio_returns": {"科技": 0.02, "银行": 0.01},
                "benchmark_returns": {"科技": 0.01, "银行": 0.01},
            },
            {  # T2：小幅回撤
                "portfolio_weights": {"科技": 0.6, "银行": 0.4},
                "benchmark_weights": {"科技": 0.5, "银行": 0.5},
                "portfolio_returns": {"科技": -0.01, "银行": 0.00},
                "benchmark_returns": {"科技": 0.00, "银行": 0.00},
            },
        ]

    def test_produces_ctr_p1_009_with_linked_effects(self):
        out = build_linked_attribution_report(
            portfolio_id="PF-001",
            period_start="2026-08-01",
            period_end="2026-08-02",
            idempotency_key="attr-20260801-001",
            period_inputs=self._period_inputs(),
            transaction_cost_drag=0.001,
        )
        rep = out.report
        assert rep.portfolio_id == "PF-001"
        assert rep.idempotency_key == "attr-20260801-001"
        assert rep.factor_contributions == {}  # 因子维度暂缓（54号 §3.4）
        assert rep.transaction_cost_drag == 0.001
        # total_return = 几何超额收益 − 成本拖拽（对齐 pf_core 守恒口径）
        assert rep.total_return == pytest.approx(out.geometric_active_return - 0.001, abs=1e-12)
        # 链接三效应 = 报告三效应，且求和 == 几何超额收益
        assert rep.allocation_effect + rep.selection_effect + rep.interaction_effect == pytest.approx(
            out.geometric_active_return, abs=1e-9
        )
        assert out.residual_quality == "PASS"
        assert abs(out.carino_residual) < 1e-9

    def test_residual_gate_strict_rejects(self):
        # 容差设为负 → 任何 residual（含 0）都越门禁，验证 strict 拒发语义
        with pytest.raises(ValueError, match="residual"):
            build_linked_attribution_report(
                portfolio_id="PF-001",
                period_start="2026-08-01",
                period_end="2026-08-01",
                idempotency_key="k",
                period_inputs=self._period_inputs()[:1],
                residual_tolerance=-1.0,
            )

    def test_residual_gate_non_strict_marks_fail(self):
        out = build_linked_attribution_report(
            portfolio_id="PF-001",
            period_start="2026-08-01",
            period_end="2026-08-01",
            idempotency_key="k",
            period_inputs=self._period_inputs()[:1],
            residual_tolerance=-1.0,
            strict=False,
        )
        assert out.residual_quality == "FAIL"

    def test_negative_drag_rejected(self):
        with pytest.raises(ValueError, match="transaction_cost_drag"):
            build_linked_attribution_report(
                portfolio_id="PF-001",
                period_start="2026-08-01",
                period_end="2026-08-01",
                idempotency_key="k",
                period_inputs=self._period_inputs()[:1],
                transaction_cost_drag=-0.1,
            )

    def test_empty_inputs_rejected(self):
        with pytest.raises(ValueError, match="空"):
            build_linked_attribution_report(
                portfolio_id="PF-001",
                period_start="2026-08-01",
                period_end="2026-08-01",
                idempotency_key="k",
                period_inputs=[],
            )
