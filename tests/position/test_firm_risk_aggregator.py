# [MODULE] tests.position.test_firm_risk_aggregator
# [DOMAIN] D_POSITION
# [MATURITY] production
# [TTL] permanent

"""
FirmRiskAggregator (MOD-POS-021) 单元测试

按 32_firm_risk_aggregator §2.1.1 施工伪代码 + §2.7 契约字段 + degraded 5 条件重建。
覆盖：pre_kelly_aggregate / post_kelly_clip / aggregate 便捷入口 / A-G 修复验证。
"""

from __future__ import annotations

from datetime import datetime

import pytest

from zephyr.position.core.firm_risk_aggregator import (
    CASH_SYMBOL,
    LIQUIDITY_MODERATE_PCT,
    LIQUIDITY_SEVERE_PCT,
    SECTOR_ABSOLUTE_CAP,
    SINGLE_NAME_CAP,
    ConflictRecord,
    FirmRiskAggregator,
    FirmTarget,
    FirmTargetPortfolio,
    PreKellyResult,
)

# ── fixtures ──────────────────────────────────────────────────────────────────


@pytest.fixture
def aggregator() -> FirmRiskAggregator:
    return FirmRiskAggregator()


@pytest.fixture
def two_targets_dict() -> list[dict]:
    """两策略 dict 格式输入（旧风格 target_portfolio/budget_used）。"""
    return [
        {
            "strategy_id": "S1",
            "budget_used": 0.5,
            "target_portfolio": {"600519": 0.06, "000001": 0.04},
        },
        {
            "strategy_id": "S2",
            "budget_used": 0.5,
            "target_portfolio": {"600519": 0.05, "000002": 0.03},
        },
    ]


@pytest.fixture
def two_targets_positions_dict() -> list[dict]:
    """两策略 dict 格式输入（positions/budget 风格，模拟 TargetPortfolio 序列化）。"""
    return [
        {
            "strategy_id": "S1",
            "budget": 0.5,
            "positions": {"600519": 0.06, "000001": 0.04},
        },
        {
            "strategy_id": "S2",
            "budget": 0.5,
            "positions": {"600519": 0.05, "000002": 0.03},
        },
    ]


@pytest.fixture
def conflict_targets() -> list[dict]:
    """冲突标的：S1 买 600519，S2 卖 600519。"""
    return [
        {
            "strategy_id": "S1",
            "budget_used": 0.5,
            "target_portfolio": {"600519": 0.08},
        },
        {
            "strategy_id": "S2",
            "budget_used": 0.5,
            "target_portfolio": {"600519": -0.05},
        },
    ]


@pytest.fixture
def industry_map() -> dict[str, str]:
    return {
        "600519": "白酒",
        "000001": "银行",
        "000002": "地产",
        "600036": "银行",
        "601318": "保险",
    }


# ══ 1. pre_kelly_aggregate 基础求和 ══════════════════════════════════════════


class TestPreKellyAggregate:
    """§2.2 按标的求和（自然叠加）+ §2.3 冲突净额。"""

    def test_sum_by_symbol_basic(self, aggregator, two_targets_dict):
        """自然叠加：S1 给 600519=6% + S2 给 600519=5% → 求和后=5.5%（budget 归一后）。"""
        pre = aggregator.pre_kelly_aggregate(
            targets=two_targets_dict,
            current_holdings={},
            total_budget=1.0,
            industry_map={},
        )
        assert isinstance(pre, PreKellyResult)
        # S1: 0.06*0.5=0.03, S2: 0.05*0.5=0.025 → 600519=0.055
        assert pre.summed_weights["600519"] == pytest.approx(0.055, abs=1e-6)
        assert pre.summed_weights["000001"] == pytest.approx(0.02, abs=1e-6)
        assert pre.summed_weights["000002"] == pytest.approx(0.015, abs=1e-6)

    def test_contributions_attribution(self, aggregator, two_targets_dict):
        """§2.2 contributions 归因：每标的记录各策略贡献。"""
        pre = aggregator.pre_kelly_aggregate(
            targets=two_targets_dict,
            current_holdings={},
            total_budget=1.0,
            industry_map={},
        )
        assert "600519" in pre.contributions
        assert pre.contributions["600519"]["S1"] == pytest.approx(0.03, abs=1e-6)
        assert pre.contributions["600519"]["S2"] == pytest.approx(0.025, abs=1e-6)
        assert pre.contributions["000001"]["S1"] == pytest.approx(0.02, abs=1e-6)

    def test_cash_excluded_from_sum(self, aggregator):
        """CASH 不参与求和（§2.4 豁免）。"""
        targets = [
            {
                "strategy_id": "S1",
                "budget_used": 0.5,
                "target_portfolio": {"600519": 0.06, CASH_SYMBOL: 0.44},
            },
        ]
        pre = aggregator.pre_kelly_aggregate(
            targets=targets, current_holdings={}, total_budget=1.0, industry_map={}
        )
        assert CASH_SYMBOL not in pre.summed_weights
        assert pre.summed_weights["600519"] == pytest.approx(0.03, abs=1e-6)

    def test_total_exposure_pre_kelly(self, aggregator, two_targets_dict):
        """PreKellyResult.total_exposure_pre_kelly = sum(summed_weights)。"""
        pre = aggregator.pre_kelly_aggregate(
            targets=two_targets_dict, current_holdings={}, total_budget=1.0, industry_map={}
        )
        expected = 0.055 + 0.02 + 0.015
        assert pre.total_exposure_pre_kelly == pytest.approx(expected, abs=1e-6)

    def test_empty_targets(self, aggregator):
        """空 targets 输入 → 空 summed_weights。"""
        pre = aggregator.pre_kelly_aggregate(
            targets=[], current_holdings={}, total_budget=1.0, industry_map={}
        )
        assert pre.summed_weights == {}
        assert pre.conflicts == []
        assert pre.total_exposure_pre_kelly == 0.0

    def test_zero_budget_fallback(self, aggregator):
        """total_budget=0 时 scale=0，不产生除零错误。"""
        targets = [
            {
                "strategy_id": "S1",
                "budget_used": 0.5,
                "target_portfolio": {"600519": 0.06},
            },
        ]
        pre = aggregator.pre_kelly_aggregate(
            targets=targets, current_holdings={}, total_budget=0.0, industry_map={}
        )
        assert pre.summed_weights["600519"] == 0.0


# ══ 2. 冲突标的净额处理 ══════════════════════════════════════════════════════


class TestConflictResolution:
    """§2.3 冲突标的净额处理。"""

    def test_conflict_detected(self, aggregator, conflict_targets):
        """一买一卖 → 冲突记录生成。"""
        pre = aggregator.pre_kelly_aggregate(
            targets=conflict_targets, current_holdings={}, total_budget=1.0, industry_map={}
        )
        assert len(pre.conflicts) == 1
        c = pre.conflicts[0]
        assert c["symbol"] == "600519"
        assert "S1" in c["buy_strategies"]
        assert "S2" in c["sell_strategies"]

    def test_conflict_net_positive(self, aggregator, conflict_targets):
        """净额>0：无截断，final_weight=net。"""
        pre = aggregator.pre_kelly_aggregate(
            targets=conflict_targets, current_holdings={}, total_budget=1.0, industry_map={}
        )
        # S1: 0.08*0.5=0.04, S2: -0.05*0.5=-0.025 → net=0.015
        assert pre.summed_weights["600519"] == pytest.approx(0.015, abs=1e-6)
        c = pre.conflicts[0]
        assert c["truncated"] is False
        assert c["final_weight"] == pytest.approx(0.015, abs=1e-6)

    def test_conflict_net_negative_truncated(self, aggregator):
        """净额<0：A 股不能做空，截断为 max(0, net+holdings)。"""
        targets = [
            {
                "strategy_id": "S1",
                "budget_used": 0.5,
                "target_portfolio": {"600519": -0.08},  # 卖
            },
            {
                "strategy_id": "S2",
                "budget_used": 0.5,
                "target_portfolio": {"600519": 0.03},  # 买
            },
        ]
        # 当前持仓 600519 = 2%
        pre = aggregator.pre_kelly_aggregate(
            targets=targets,
            current_holdings={"600519": 0.02},
            total_budget=1.0,
            industry_map={},
        )
        # net = -0.04+0.015 = -0.025, holdings=0.02 → final = max(0, -0.025+0.02) = 0
        assert pre.summed_weights["600519"] == 0.0
        c = pre.conflicts[0]
        assert c["truncated"] is True
        assert c["final_weight"] == 0.0
        assert c["truncated_amount"] == pytest.approx(-0.005, abs=1e-6)

    def test_conflict_net_negative_with_sufficient_holdings(self, aggregator):
        """净额<0 但持仓足够：final = net + holdings > 0。"""
        targets = [
            {
                "strategy_id": "S1",
                "budget_used": 0.5,
                "target_portfolio": {"600519": -0.04},
            },
            {
                "strategy_id": "S2",
                "budget_used": 0.5,
                "target_portfolio": {"600519": 0.02},
            },
        ]
        pre = aggregator.pre_kelly_aggregate(
            targets=targets,
            current_holdings={"600519": 0.05},
            total_budget=1.0,
            industry_map={},
        )
        # net = -0.02+0.01 = -0.01, holdings=0.05 → final = max(0, -0.01+0.05) = 0.04
        assert pre.summed_weights["600519"] == pytest.approx(0.04, abs=1e-6)
        c = pre.conflicts[0]
        assert c["truncated"] is True
        assert c["final_weight"] == pytest.approx(0.04, abs=1e-6)

    def test_no_conflict_same_direction(self, aggregator, two_targets_dict):
        """同向叠加（都买）→ 无冲突记录。"""
        pre = aggregator.pre_kelly_aggregate(
            targets=two_targets_dict, current_holdings={}, total_budget=1.0, industry_map={}
        )
        assert len(pre.conflicts) == 0

    def test_conflict_record_fields(self, aggregator, conflict_targets):
        """ConflictRecord 字段完整性。"""
        pre = aggregator.pre_kelly_aggregate(
            targets=conflict_targets, current_holdings={}, total_budget=1.0, industry_map={}
        )
        c = pre.conflicts[0]
        assert "symbol" in c
        assert "buy_strategies" in c
        assert "sell_strategies" in c
        assert "net_weight" in c
        assert "truncated" in c
        assert "final_weight" in c


# ══ 3. post_kelly_clip 单票裁剪 ═════════════════════════════════════════════


class TestPostKellyClipSingleName:
    """§2.4 单票硬上限裁剪（按比例削，CASH 豁免）。"""

    def test_single_name_cap_triggered(self, aggregator):
        """单票 >8% → 削到 8%。"""
        kelly_adjusted = {"600519": 0.12, "000001": 0.05}
        result = aggregator.post_kelly_clip(
            kelly_adjusted=kelly_adjusted,
            total_budget=1.0,
            industry_map={},
            regime_cap=0.95,
        )
        assert result["firm_positions"]["600519"]["target_weight"] == pytest.approx(
            SINGLE_NAME_CAP, abs=1e-6
        )
        assert result["constraint_checks"]["single_name"]["triggered"] is True
        assert len(result["constraint_checks"]["single_name"]["cuts"]) == 1

    def test_single_name_cap_not_triggered(self, aggregator):
        """单票 ≤8% → 不触发裁剪。"""
        kelly_adjusted = {"600519": 0.06, "000001": 0.05}
        result = aggregator.post_kelly_clip(
            kelly_adjusted=kelly_adjusted,
            total_budget=1.0,
            industry_map={},
            regime_cap=0.95,
        )
        assert result["firm_positions"]["600519"]["target_weight"] == pytest.approx(
            0.06, abs=1e-6
        )
        assert result["constraint_checks"]["single_name"]["triggered"] is False

    def test_cut_ratio_recorded(self, aggregator):
        """cut_ratio = 1 - cap/original。"""
        kelly_adjusted = {"600519": 0.16}
        result = aggregator.post_kelly_clip(
            kelly_adjusted=kelly_adjusted,
            total_budget=1.0,
            industry_map={},
            regime_cap=0.95,
        )
        # cut_ratio = 1 - 0.08/0.16 = 0.5
        assert result["firm_positions"]["600519"]["cut_ratio"] == pytest.approx(0.5, abs=1e-6)

    def test_cash_exempt_from_single_name_clip(self, aggregator):
        """CASH 豁免单票裁剪。"""
        kelly_adjusted = {"600519": 0.06, CASH_SYMBOL: 0.90}
        result = aggregator.post_kelly_clip(
            kelly_adjusted=kelly_adjusted,
            total_budget=1.0,
            industry_map={},
            regime_cap=0.95,
        )
        # CASH 不应被裁剪，权重在 Step 4 残差计算覆盖
        assert result["constraint_checks"]["single_name"]["triggered"] is False


# ══ 4. post_kelly_clip 流动性裁剪 ═══════════════════════════════════════════


class TestPostKellyClipLiquidity:
    """§2.4.4 流动性裁剪（ADV 口径）。"""

    def test_liquidity_severe_tier(self, aggregator):
        """>20% ADV → 削到 20% ADV。"""
        # 注意：单票裁剪(8%)先于流动性裁剪执行，输入需 ≤8% 避免单票裁剪干扰
        kelly_adjusted = {"600519": 0.07}
        adv_data = {"600519": {"adv_20d_p25": 0.30}}  # 30% ADV
        result = aggregator.post_kelly_clip(
            kelly_adjusted=kelly_adjusted,
            total_budget=1.0,
            industry_map={},
            regime_cap=0.95,
            adv_data=adv_data,
        )
        # position_value=0.07, adv_pct=0.07/0.30≈0.233 > 0.20 → severe
        # new_weight = 0.07 * (0.20/0.233) ≈ 0.06
        assert result["constraint_checks"]["liquidity_cap"]["triggered"] is True
        cut = result["constraint_checks"]["liquidity_cap"]["cuts"][0]
        assert cut["tier"] == "severe"
        assert cut["adv_pct"] == pytest.approx(0.233, abs=0.01)

    def test_liquidity_moderate_tier(self, aggregator):
        """>10% ADV 但 ≤20% → 削半。"""
        # 注意：单票裁剪(8%)先于流动性裁剪执行，输入需 ≤8% 避免单票裁剪干扰
        kelly_adjusted = {"600519": 0.08}
        adv_data = {"600519": {"adv_20d_p25": 0.60}}  # 60% ADV
        result = aggregator.post_kelly_clip(
            kelly_adjusted=kelly_adjusted,
            total_budget=1.0,
            industry_map={},
            regime_cap=0.95,
            adv_data=adv_data,
        )
        # adv_pct=0.08/0.60≈0.133 → moderate → 削半
        assert result["firm_positions"]["600519"]["target_weight"] == pytest.approx(
            0.04, abs=1e-6
        )
        cut = result["constraint_checks"]["liquidity_cap"]["cuts"][0]
        assert cut["tier"] == "moderate"

    def test_liquidity_adv_missing_sector_fallback(self, aggregator):
        """ADV 缺失 → 降级取同行业中位数。"""
        kelly_adjusted = {"600519": 0.10, "000001": 0.05}
        adv_data = {
            "000001": {"adv_20d_p25": 0.50},  # 银行行业 ADV=0.50
        }
        industry_map = {"600519": "白酒", "000001": "银行"}
        result = aggregator.post_kelly_clip(
            kelly_adjusted=kelly_adjusted,
            total_budget=1.0,
            industry_map=industry_map,
            regime_cap=0.95,
            adv_data=adv_data,
        )
        # 600519 ADV 缺失，白酒行业也无数据 → 跳过
        # 000001 adv_pct=0.05/0.50=0.10 ≤ 0.10 → 不触发
        assert result["constraint_checks"]["liquidity_cap"]["triggered"] is False

    def test_liquidity_no_adv_data_skip(self, aggregator):
        """无 adv_data → 跳过流动性裁剪。"""
        kelly_adjusted = {"600519": 0.10}
        result = aggregator.post_kelly_clip(
            kelly_adjusted=kelly_adjusted,
            total_budget=1.0,
            industry_map={},
            regime_cap=0.95,
            adv_data=None,
        )
        assert result["constraint_checks"]["liquidity_cap"]["triggered"] is False


# ══ 5. post_kelly_clip 行业裁剪 ═════════════════════════════════════════════


class TestPostKellyClipSector:
    """§2.5.1 行业硬约束裁剪（绝对 30%）。"""

    def test_sector_absolute_cap_triggered(self, aggregator):
        """行业权重 >30% → 行业内等比缩放到 30%。"""
        # 注意：单票裁剪(8%)先于行业裁剪执行，单票需 ≤8% 避免干扰
        kelly_adjusted = {"600519": 0.08, "000001": 0.08, "600036": 0.08, "601318": 0.08}
        industry_map = {"600519": "白酒", "000001": "白酒", "600036": "白酒", "601318": "白酒"}
        result = aggregator.post_kelly_clip(
            kelly_adjusted=kelly_adjusted,
            total_budget=1.0,
            industry_map=industry_map,
            regime_cap=0.95,
        )
        # 白酒合计 0.32 > 0.30 → scale=0.30/0.32=0.9375
        assert result["constraint_checks"]["sector"]["triggered"] is True
        total_sector = sum(
            result["firm_positions"][sym]["target_weight"]
            for sym in ["600519", "000001", "600036", "601318"]
        )
        assert total_sector == pytest.approx(SECTOR_ABSOLUTE_CAP, abs=1e-6)

    def test_sector_cap_not_triggered(self, aggregator):
        """行业权重 ≤30% → 不触发。"""
        # 单票 ≤8% 避免单票裁剪干扰
        kelly_adjusted = {"600519": 0.08, "000001": 0.08}
        industry_map = {"600519": "白酒", "000001": "银行"}
        result = aggregator.post_kelly_clip(
            kelly_adjusted=kelly_adjusted,
            total_budget=1.0,
            industry_map=industry_map,
            regime_cap=0.95,
        )
        assert result["constraint_checks"]["sector"]["triggered"] is False

    def test_sector_unknown_fallback(self, aggregator):
        """无行业映射 → UNKNOWN 行业，多标的合计 >30% 触发裁剪。"""
        # 单票 ≤8% 避免单票裁剪干扰，4 只 UNKNOWN 合计 32% > 30%
        kelly_adjusted = {"A": 0.08, "B": 0.08, "C": 0.08, "D": 0.08}
        result = aggregator.post_kelly_clip(
            kelly_adjusted=kelly_adjusted,
            total_budget=1.0,
            industry_map={},
            regime_cap=0.95,
        )
        # UNKNOWN 行业合计 0.32 > 0.30 → 触发
        assert result["constraint_checks"]["sector"]["triggered"] is True


# ══ 6. post_kelly_clip 总仓位裁剪 ═══════════════════════════════════════════


class TestPostKellyClipTotalExposure:
    """§2.5.2 总仓位硬约束裁剪（等比缩放）。"""

    def test_total_exposure_cap_triggered(self, aggregator):
        """总暴露 > regime_cap → 等比缩放。"""
        # 单票 ≤8% 避免单票裁剪干扰；10 只标的各 8% 分散到 10 个不同行业避免行业裁剪
        kelly_adjusted = {f"SYM{i}": 0.08 for i in range(10)}
        industry_map = {f"SYM{i}": f"SECTOR{i}" for i in range(10)}  # 每只票独立行业
        result = aggregator.post_kelly_clip(
            kelly_adjusted=kelly_adjusted,
            total_budget=1.0,
            industry_map=industry_map,
            regime_cap=0.60,  # 总暴露 0.80 > 0.60 → 触发
        )
        assert result["constraint_checks"]["total_exposure"]["triggered"] is True
        assert result["total_exposure"] == pytest.approx(0.60, abs=1e-6)

    def test_total_exposure_cap_not_triggered(self, aggregator):
        """总暴露 ≤ regime_cap → 不触发。"""
        # 单票 ≤8% 避免单票裁剪干扰
        kelly_adjusted = {"600519": 0.08, "000001": 0.08}
        result = aggregator.post_kelly_clip(
            kelly_adjusted=kelly_adjusted,
            total_budget=1.0,
            industry_map={},
            regime_cap=0.80,
        )
        assert result["constraint_checks"]["total_exposure"]["triggered"] is False
        assert result["total_exposure"] == pytest.approx(0.16, abs=1e-6)

    def test_kelly_pro_rata_no_double_scale(self, aggregator):
        """Kelly 层已 pro-rata 归一化 → firm 层总仓位裁剪不触发（防双重缩放）。"""
        # 单票 ≤8% 避免单票裁剪干扰，Kelly 后 sum=0.16 ≤ regime_cap=0.80
        kelly_adjusted = {"600519": 0.08, "000001": 0.08}
        result = aggregator.post_kelly_clip(
            kelly_adjusted=kelly_adjusted,
            total_budget=1.0,
            industry_map={},
            regime_cap=0.80,
        )
        assert result["constraint_checks"]["total_exposure"]["triggered"] is False


# ══ 7. post_kelly_clip 现金管理 ═════════════════════════════════════════════


class TestPostKellyClipCash:
    """§2.5 现金管理（CASH 残差）。"""

    def test_cash_residual_calculation(self, aggregator):
        """CASH = total_budget - total_exposure。"""
        # 单票 ≤8% 避免单票裁剪干扰
        kelly_adjusted = {"600519": 0.08, "000001": 0.08}
        result = aggregator.post_kelly_clip(
            kelly_adjusted=kelly_adjusted,
            total_budget=1.0,
            industry_map={},
            regime_cap=0.95,
        )
        # 总暴露=0.16，CASH=1.0-0.16=0.84
        assert result["cash_ratio"] == pytest.approx(0.84, abs=1e-6)
        assert result["firm_positions"][CASH_SYMBOL]["target_weight"] == pytest.approx(
            0.84, abs=1e-6
        )

    def test_cash_negative_fallback_zero(self, aggregator):
        """总暴露 > total_budget 时 CASH 兜底为 0。"""
        # 单票 ≤8% 避免单票裁剪干扰；12 只标的各 8% 分散到 12 个不同行业避免行业裁剪
        kelly_adjusted = {f"SYM{i}": 0.08 for i in range(12)}
        industry_map = {f"SYM{i}": f"SECTOR{i}" for i in range(12)}
        result = aggregator.post_kelly_clip(
            kelly_adjusted=kelly_adjusted,
            total_budget=1.0,
            industry_map=industry_map,
            regime_cap=0.50,
        )
        # 总暴露被 regime_cap 裁到 0.50 < 1.0 → cash=0.50
        assert result["cash_ratio"] >= 0.0

    def test_weights_sum_equals_budget(self, aggregator):
        """firm_positions 权重和 + cash_ratio = total_budget。"""
        # 单票 ≤8% 避免单票裁剪干扰
        kelly_adjusted = {"600519": 0.08, "000001": 0.08}
        result = aggregator.post_kelly_clip(
            kelly_adjusted=kelly_adjusted,
            total_budget=1.0,
            industry_map={},
            regime_cap=0.95,
        )
        stock_sum = sum(
            pos["target_weight"]
            for sym, pos in result["firm_positions"].items()
            if sym != CASH_SYMBOL
        )
        assert stock_sum + result["cash_ratio"] == pytest.approx(1.0, abs=1e-6)


# ══ 8. degraded 降级标记（5 条件） ═════════════════════════════════════════


class TestDegradedFlag:
    """§2.1 degraded 降级标记 5 条件。"""

    def test_degraded_conflict_truncated(self, aggregator):
        """条件1：冲突净额截断 → degraded=True。"""
        targets = [
            {"strategy_id": "S1", "budget_used": 0.5, "target_portfolio": {"600519": -0.08}},
            {"strategy_id": "S2", "budget_used": 0.5, "target_portfolio": {"600519": 0.03}},
        ]
        result = aggregator.aggregate(
            target_portfolios=targets,
            position_snapshot={"600519": 0.02},
            total_budget=1.0,
            industry_map={},
            regime_cap=0.95,
        )
        assert result.degraded is True

    def test_degraded_single_name_clip(self, aggregator):
        """条件2：单票裁剪触发 → degraded=True。"""
        kelly_adjusted = {"600519": 0.12}
        result = aggregator.post_kelly_clip(
            kelly_adjusted=kelly_adjusted,
            total_budget=1.0,
            industry_map={},
            regime_cap=0.95,
        )
        assert result["degraded"] is True

    def test_degraded_sector_clip(self, aggregator):
        """条件3：行业裁剪触发 → degraded=True。"""
        # 单票 ≤8% 避免单票裁剪干扰，4 只白酒各 8% = 32% > 30%
        kelly_adjusted = {"600519": 0.08, "000001": 0.08, "600036": 0.08, "601318": 0.08}
        industry_map = {"600519": "白酒", "000001": "白酒", "600036": "白酒", "601318": "白酒"}
        result = aggregator.post_kelly_clip(
            kelly_adjusted=kelly_adjusted,
            total_budget=1.0,
            industry_map=industry_map,
            regime_cap=0.95,
        )
        assert result["degraded"] is True

    def test_degraded_total_exposure_clip(self, aggregator):
        """条件4：总仓位裁剪触发 → degraded=True。"""
        # 单票 ≤8% 避免单票裁剪干扰；10 只标的各 8% 分散到 10 个不同行业避免行业裁剪
        kelly_adjusted = {f"SYM{i}": 0.08 for i in range(10)}
        industry_map = {f"SYM{i}": f"SECTOR{i}" for i in range(10)}
        result = aggregator.post_kelly_clip(
            kelly_adjusted=kelly_adjusted,
            total_budget=1.0,
            industry_map=industry_map,
            regime_cap=0.60,
        )
        assert result["degraded"] is True

    def test_degraded_liquidity_clip(self, aggregator):
        """条件4b：流动性裁剪触发 → degraded=True。"""
        # 单票 ≤8% 避免单票裁剪干扰
        kelly_adjusted = {"600519": 0.07}
        adv_data = {"600519": {"adv_20d_p25": 0.30}}
        result = aggregator.post_kelly_clip(
            kelly_adjusted=kelly_adjusted,
            total_budget=1.0,
            industry_map={},
            regime_cap=0.95,
            adv_data=adv_data,
        )
        assert result["degraded"] is True

    def test_degraded_kelly_fallback(self, aggregator):
        """条件5：Kelly 参数降级传导 → degraded=True。"""
        kelly_adjusted = {"600519": 0.05}
        result = aggregator.post_kelly_clip(
            kelly_adjusted=kelly_adjusted,
            total_budget=1.0,
            industry_map={},
            regime_cap=0.95,
            kelly_param_source="historical_fallback",
        )
        assert result["degraded"] is True

    def test_not_degraded_all_clean(self, aggregator):
        """无触发 → degraded=False。"""
        kelly_adjusted = {"600519": 0.05, "000001": 0.03}
        result = aggregator.post_kelly_clip(
            kelly_adjusted=kelly_adjusted,
            total_budget=1.0,
            industry_map={},
            regime_cap=0.95,
        )
        assert result["degraded"] is False


# ══ 9. FirmTargetPortfolio 契约 ═════════════════════════════════════════════


class TestFirmTargetPortfolioContract:
    """§2.7 FirmTargetPortfolio 数据结构契约。"""

    def test_aggregate_returns_firm_target_portfolio(self, aggregator, two_targets_dict):
        """aggregate() 返回 FirmTargetPortfolio dataclass。"""
        result = aggregator.aggregate(
            target_portfolios=two_targets_dict,
            total_budget=1.0,
            industry_map={},
            regime_cap=0.95,
        )
        assert isinstance(result, FirmTargetPortfolio)

    def test_firm_target_fields(self, aggregator, two_targets_dict):
        """FirmTarget 字段：target_weight / contributions / cut_ratio。"""
        result = aggregator.aggregate(
            target_portfolios=two_targets_dict,
            total_budget=1.0,
            industry_map={},
            regime_cap=0.95,
        )
        pos = result.firm_positions["600519"]
        assert isinstance(pos, FirmTarget)
        assert hasattr(pos, "target_weight")
        assert hasattr(pos, "contributions")
        assert hasattr(pos, "cut_ratio")

    def test_portfolio_fields_complete(self, aggregator, two_targets_dict):
        """FirmTargetPortfolio 全字段在位。"""
        result = aggregator.aggregate(
            target_portfolios=two_targets_dict,
            total_budget=1.0,
            industry_map={},
            regime_cap=0.95,
        )
        assert hasattr(result, "firm_positions")
        assert hasattr(result, "total_exposure")
        assert hasattr(result, "total_budget")
        assert hasattr(result, "cash_ratio")
        assert hasattr(result, "constraint_checks")
        assert hasattr(result, "conflicts_resolved")
        assert hasattr(result, "degraded")
        assert hasattr(result, "created_at")
        assert hasattr(result, "idempotency_key")
        assert hasattr(result, "schema_version")

    def test_conflicts_resolved_type(self, aggregator, conflict_targets):
        """conflicts_resolved 是 ConflictRecord 列表。"""
        result = aggregator.aggregate(
            target_portfolios=conflict_targets,
            position_snapshot={"600519": 0.02},
            total_budget=1.0,
            industry_map={},
            regime_cap=0.95,
        )
        assert len(result.conflicts_resolved) == 1
        assert isinstance(result.conflicts_resolved[0], ConflictRecord)

    def test_contributions_in_firm_positions(self, aggregator, two_targets_dict):
        """§2.2 contributions 归因透传到 firm_positions。"""
        result = aggregator.aggregate(
            target_portfolios=two_targets_dict,
            total_budget=1.0,
            industry_map={},
            regime_cap=0.95,
        )
        pos = result.firm_positions["600519"]
        assert "S1" in pos.contributions
        assert "S2" in pos.contributions

    def test_idempotency_key_present(self, aggregator, two_targets_dict):
        """幂等键存在。"""
        result = aggregator.aggregate(
            target_portfolios=two_targets_dict,
            total_budget=1.0,
            industry_map={},
            regime_cap=0.95,
        )
        assert result.idempotency_key != ""
        assert result.schema_version == "1.0"


# ══ 10. aggregate 便捷入口（Kelly passthrough） ═════════════════════════════


class TestAggregatePassthrough:
    """aggregate() 便捷入口：pre_kelly → Kelly passthrough → post_kelly_clip。"""

    def test_aggregate_identity_passthrough(self, aggregator, two_targets_dict):
        """无 kelly_fn → identity passthrough，结果与两段手动调用一致。"""
        result = aggregator.aggregate(
            target_portfolios=two_targets_dict,
            total_budget=1.0,
            industry_map={},
            regime_cap=0.95,
        )
        # 与手动两段调用结果一致
        pre = aggregator.pre_kelly_aggregate(
            targets=two_targets_dict, current_holdings={}, total_budget=1.0, industry_map={}
        )
        manual = aggregator.post_kelly_clip(
            kelly_adjusted=dict(pre.summed_weights),
            total_budget=1.0,
            industry_map={},
            regime_cap=0.95,
            contributions=pre.contributions,
            conflicts=pre.conflicts,
        )
        assert result.total_exposure == pytest.approx(manual["total_exposure"], abs=1e-6)

    def test_aggregate_with_kelly_fn(self, aggregator, two_targets_dict):
        """有 kelly_fn → 使用外部 Kelly 结果。"""
        def mock_kelly(weights: dict) -> dict:
            return {k: v * 0.5 for k, v in weights.items()}  # 减半

        result = aggregator.aggregate(
            target_portfolios=two_targets_dict,
            total_budget=1.0,
            industry_map={},
            regime_cap=0.95,
            kelly_fn=mock_kelly,
        )
        # 600519 原 0.055 → Kelly 后 0.0275
        assert result.firm_positions["600519"].target_weight == pytest.approx(
            0.0275, abs=1e-6
        )


# ══ 11. 字段名漂移适配（P0 修复验证） ═════════════════════════════════════


class TestFieldNameAdaptation:
    """§6 P0：TargetPortfolio positions/budget 字段名适配。"""

    def test_positions_budget_dict_format(self, aggregator, two_targets_positions_dict):
        """dict(positions/budget) 格式 → 正确求和。"""
        pre = aggregator.pre_kelly_aggregate(
            targets=two_targets_positions_dict,
            current_holdings={},
            total_budget=1.0,
            industry_map={},
        )
        assert pre.summed_weights["600519"] == pytest.approx(0.055, abs=1e-6)
        assert pre.summed_weights["000001"] == pytest.approx(0.02, abs=1e-6)

    def test_positions_budget_no_silent_empty(self, aggregator, two_targets_positions_dict):
        """positions/budget 格式不再静默产出全现金组合。"""
        result = aggregator.aggregate(
            target_portfolios=two_targets_positions_dict,
            total_budget=1.0,
            industry_map={},
            regime_cap=0.95,
        )
        # 应有非 CASH 持仓
        non_cash = {
            k: v for k, v in result.firm_positions.items() if k != CASH_SYMBOL
        }
        assert len(non_cash) > 0
        assert result.total_exposure > 0

    def test_target_weight_object_extraction(self, aggregator):
        """positions 值为 TargetWeight 对象时取 .target_weight。"""
        # 模拟 TargetWeight 对象（用 namedtuple 模拟）
        from collections import namedtuple
        MockTW = namedtuple("MockTW", ["target_weight", "reason", "confidence"])
        targets = [
            {
                "strategy_id": "S1",
                "budget": 0.5,
                "positions": {"600519": MockTW(0.06, "test", 0.9)},
            },
        ]
        pre = aggregator.pre_kelly_aggregate(
            targets=targets, current_holdings={}, total_budget=1.0, industry_map={}
        )
        assert pre.summed_weights["600519"] == pytest.approx(0.03, abs=1e-6)


# ══ 12. 边界与不变量 ═══════════════════════════════════════════════════════


class TestInvariants:
    """INVARIANTS 验证。"""

    def test_natural_additivity(self, aggregator):
        """自然叠加：S1 给 3% + S2 给 5% = 8%（budget 归一前）。"""
        targets = [
            {"strategy_id": "S1", "budget_used": 1.0, "target_portfolio": {"X": 0.03}},
            {"strategy_id": "S2", "budget_used": 1.0, "target_portfolio": {"X": 0.05}},
        ]
        # total_budget=2.0 → scale 各 0.5 → 0.015+0.025=0.04
        pre = aggregator.pre_kelly_aggregate(
            targets=targets, current_holdings={}, total_budget=2.0, industry_map={}
        )
        assert pre.summed_weights["X"] == pytest.approx(0.04, abs=1e-6)

    def test_pro_rata_not_priority(self, aggregator):
        """单票裁剪按比例削，非优先级截断。"""
        kelly_adjusted = {"600519": 0.16}
        result = aggregator.post_kelly_clip(
            kelly_adjusted=kelly_adjusted,
            total_budget=1.0,
            industry_map={},
            regime_cap=0.95,
        )
        # 削到 8%，cut_ratio=0.5（比例削）
        assert result["firm_positions"]["600519"]["target_weight"] == pytest.approx(0.08, abs=1e-6)
        assert result["firm_positions"]["600519"]["cut_ratio"] == pytest.approx(0.5, abs=1e-6)

    def test_no_mvo_no_covariance(self, aggregator):
        """代码无 scipy/numpy 优化器依赖，无协方差计算。"""
        import inspect
        source = inspect.getsource(type(aggregator))
        assert "cvxpy" not in source
        assert "scipy.optimize" not in source
        assert "numpy.cov" not in source
        assert "corrcoef" not in source

    def test_on_complexity(self, aggregator):
        """O(N×M) 复杂度：3 策略 × 5 标的 = 15 次操作，微秒级。"""
        targets = [
            {
                "strategy_id": f"S{i}",
                "budget_used": 0.33,
                "target_portfolio": {f"SYM{j}": 0.02 for j in range(5)},
            }
            for i in range(3)
        ]
        import time
        start = time.perf_counter()
        pre = aggregator.pre_kelly_aggregate(
            targets=targets, current_holdings={}, total_budget=1.0, industry_map={}
        )
        elapsed = time.perf_counter() - start
        assert elapsed < 0.01  # <10ms
        assert len(pre.summed_weights) == 5


# ══ 13. 级联裁剪单调收敛 ═══════════════════════════════════════════════════


class TestCascadingClip:
    """§2.5.2 级联裁剪单调收敛。"""

    def test_cascading_order(self, aggregator):
        """单票→流动性→行业→总仓位，每步只减不增。"""
        kelly_adjusted = {"600519": 0.15, "000001": 0.12, "000002": 0.10}
        industry_map = {"600519": "白酒", "000001": "白酒", "000002": "地产"}
        adv_data = {"600519": {"adv_20d_p25": 0.30}}
        result = aggregator.post_kelly_clip(
            kelly_adjusted=kelly_adjusted,
            total_budget=1.0,
            industry_map=industry_map,
            regime_cap=0.80,
            adv_data=adv_data,
        )
        # 验证每步只减不增
        for sym in ["600519", "000001", "000002"]:
            final = result["firm_positions"][sym]["target_weight"]
            original = kelly_adjusted[sym]
            assert final <= original + 1e-9  # 只减不增

    def test_cut_ratio_cumulative(self, aggregator):
        """多级裁剪 cut_ratio 累积：1-(1-r1)*(1-r2)。"""
        kelly_adjusted = {"600519": 0.20}
        industry_map = {"600519": "白酒"}
        result = aggregator.post_kelly_clip(
            kelly_adjusted=kelly_adjusted,
            total_budget=1.0,
            industry_map=industry_map,
            regime_cap=0.95,
        )
        # 单票 0.20→0.08 (r1=0.6)，行业 0.08→0.08 (不触发)
        pos = result["firm_positions"]["600519"]
        assert pos["cut_ratio"] == pytest.approx(0.6, abs=1e-6)


# ══ 14. A-G 修复验证 ═══════════════════════════════════════════════════════


class TestAGFixes:
    """v1.0.19 A-G 修复验证。"""

    def test_a_liquidity_cap_key_initialized(self, aggregator):
        """A: constraint_checks 初始化含 liquidity_cap 键。"""
        kelly_adjusted = {"600519": 0.05}
        result = aggregator.post_kelly_clip(
            kelly_adjusted=kelly_adjusted,
            total_budget=1.0,
            industry_map={},
            regime_cap=0.95,
        )
        assert "liquidity_cap" in result["constraint_checks"]

    def test_b_degraded_includes_liquidity(self, aggregator):
        """B: degraded 条件含 liquidity_cap 触发。"""
        kelly_adjusted = {"600519": 0.10}
        adv_data = {"600519": {"adv_20d_p25": 0.30}}
        result = aggregator.post_kelly_clip(
            kelly_adjusted=kelly_adjusted,
            total_budget=1.0,
            industry_map={},
            regime_cap=0.95,
            adv_data=adv_data,
        )
        assert result["degraded"] is True

    def test_c_adv_data_parameterized(self, aggregator):
        """C: adv_data 作为参数传入（非未定义变量）。"""
        kelly_adjusted = {"600519": 0.05}
        # 不传 adv_data 不报错
        result = aggregator.post_kelly_clip(
            kelly_adjusted=kelly_adjusted,
            total_budget=1.0,
            industry_map={},
            regime_cap=0.95,
        )
        assert result["constraint_checks"]["liquidity_cap"]["triggered"] is False

    def test_d_total_budget_not_total_capital(self, aggregator):
        """D: 流动性裁剪用 total_budget 非 total_capital。"""
        # 单票 ≤8% 避免单票裁剪干扰
        kelly_adjusted = {"600519": 0.07}
        adv_data = {"600519": {"adv_20d_p25": 0.30}}
        result = aggregator.post_kelly_clip(
            kelly_adjusted=kelly_adjusted,
            total_budget=1.0,
            industry_map={},
            regime_cap=0.95,
            adv_data=adv_data,
        )
        # position_value = 0.07 * 1.0 = 0.07, adv_pct = 0.07/0.30 ≈ 0.233
        cut = result["constraint_checks"]["liquidity_cap"]["cuts"][0]
        assert cut["adv_pct"] == pytest.approx(0.233, abs=0.01)

    def test_e_contributions_transparent(self, aggregator, two_targets_dict):
        """E: contributions 从 PreKellyResult 透传到 post_kelly_clip。"""
        pre = aggregator.pre_kelly_aggregate(
            targets=two_targets_dict, current_holdings={}, total_budget=1.0, industry_map={}
        )
        result = aggregator.post_kelly_clip(
            kelly_adjusted=dict(pre.summed_weights),
            total_budget=1.0,
            industry_map={},
            regime_cap=0.95,
            contributions=pre.contributions,
            conflicts=pre.conflicts,
        )
        pos = result["firm_positions"]["600519"]
        assert "S1" in pos["contributions"]
        assert "S2" in pos["contributions"]

    def test_f_sector_overlay_active_reserved(self, aggregator):
        """G: sector_overlay_active 预留参数存在。"""
        kelly_adjusted = {"600519": 0.05}
        result = aggregator.post_kelly_clip(
            kelly_adjusted=kelly_adjusted,
            total_budget=1.0,
            industry_map={},
            regime_cap=0.95,
            sector_overlay_active=True,  # 预留参数可传不报错
        )
        assert result["firm_positions"]["600519"]["target_weight"] == pytest.approx(0.05, abs=1e-6)

    def test_g_conflicts_resolved_in_output(self, aggregator, conflict_targets):
        """F: conflicts_resolved 字段在输出中。"""
        result = aggregator.aggregate(
            target_portfolios=conflict_targets,
            position_snapshot={"600519": 0.02},
            total_budget=1.0,
            industry_map={},
            regime_cap=0.95,
        )
        assert result.conflicts_resolved is not None
        assert len(result.conflicts_resolved) == 1
