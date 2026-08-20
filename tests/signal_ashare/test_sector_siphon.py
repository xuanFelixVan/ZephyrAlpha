"""虹吸态 HHI 识别 单元测试（22 号 spec §3.1⑤）"""

import pytest

from zephyr.signal_ashare.sector_siphon import (
    SectorFlowSnapshot,
    detect_siphon_state,
    rolling_zscore,
)


def _sectors(n: int, turnover: float = 100.0, inflow: float = 1.0) -> list[SectorFlowSnapshot]:
    return [SectorFlowSnapshot(name=f"板块{i}", turnover=turnover, net_inflow=inflow) for i in range(n)]


def _flat_history(value: float, n: int = 20, jitter: float = 0.005) -> list[float]:
    """构造低波动历史序列（σ>0 以产生有效 z-score）"""
    return [value + (jitter if i % 2 == 0 else -jitter) for i in range(n)]


class TestRollingZscore:
    def test_insufficient_history_returns_zero(self):
        assert rolling_zscore(1.0, []) == 0.0
        assert rolling_zscore(1.0, [0.5]) == 0.0

    def test_zero_std_returns_zero(self):
        assert rolling_zscore(1.0, [0.5, 0.5, 0.5]) == 0.0

    def test_value_above_history_positive_z(self):
        z = rolling_zscore(3.0, [1.0, 1.1, 0.9, 1.0, 1.05])
        assert z > 2.0

    def test_value_at_mean_near_zero(self):
        z = rolling_zscore(1.0, [1.0, 1.1, 0.9, 1.0, 1.05])
        assert abs(z) < 1.0


class TestDetectSiphonState:
    def test_empty_sectors_not_siphon(self):
        result = detect_siphon_state([], [], [], [])
        assert result.is_siphon is False
        assert result.siphon_score == 0.0
        assert result.siphon_sectors == []

    def test_no_history_degrades_to_not_siphon(self):
        """历史窗口样本不足 → z 全 0 → 不触发（降级不误报）"""
        sectors = _sectors(10)
        result = detect_siphon_state(sectors, [], [], [])
        assert result.is_siphon is False
        assert result.siphon_score == 0.0

    def test_extreme_concentration_triggers_siphon(self):
        """当日极端集中 + 历史常态低集中 → 三信号 z 全部冲高 → 虹吸态"""
        # 头部 2 板块占 96% 成交额，且大额净流入；其余 18 家全部净流出
        sectors = [
            SectorFlowSnapshot("AI算力", turnover=4800.0, net_inflow=50.0),
            SectorFlowSnapshot("半导体", turnover=4800.0, net_inflow=40.0),
        ] + _sectors(18, turnover=22.0, inflow=-2.0)
        result = detect_siphon_state(
            sectors,
            hhi_history=_flat_history(0.10),
            conc_history=_flat_history(0.05),
            outflow_history=_flat_history(0.40),
            n_top=2,
        )
        assert result.is_siphon is True
        assert result.siphon_score > 1.5
        assert set(result.siphon_sectors) == {"AI算力", "半导体"}
        assert result.z_hhi > 2.0
        assert result.z_conc > 0.0
        assert result.z_outflow > 2.0

    def test_normal_day_not_siphon(self):
        """当日指标与历史常态持平 → score≈0 → 非虹吸态"""
        sectors = _sectors(20, turnover=100.0, inflow=1.0)
        # 20 家等额成交额 → top5 份额各 0.05，hhi=5×0.05²=0.0125
        # top5 净流入和=5，total_abs=20 → conc=0.25；rest 全净流入 → outflow=0
        result = detect_siphon_state(
            sectors,
            hhi_history=_flat_history(0.0125),
            conc_history=_flat_history(0.25),
            outflow_history=_flat_history(0.0),
        )
        assert result.is_siphon is False
        assert result.siphon_sectors == []

    def test_hhi_signal_math(self):
        """信号① HHI = Σ(头部N份额)² 手工核验：4 家 100/200/300/400，top2"""
        sectors = [
            SectorFlowSnapshot("A", 100.0, -1.0),
            SectorFlowSnapshot("B", 200.0, -1.0),
            SectorFlowSnapshot("C", 300.0, 1.0),
            SectorFlowSnapshot("D", 400.0, 1.0),
        ]
        # top2 = D,C → 份额 0.4+0.3 → hhi = 0.16+0.09 = 0.25（历史 0.15 → z 高正）
        # conc = 2.0/4.0 = 0.5（历史 0.30 → z 高正）
        # rest = A,B 全净流出 → outflow_ratio = 1.0（历史 0.50 → z 高正）→ 必触发
        result = detect_siphon_state(
            sectors,
            hhi_history=_flat_history(0.15),
            conc_history=_flat_history(0.30),
            outflow_history=_flat_history(0.50),
            n_top=2,
        )
        assert result.is_siphon is True
        assert result.siphon_sectors == ["D", "C"]

    def test_outflow_ratio_only_rest_sectors(self):
        """信号③ 只统计头部 N 之外的板块净流出比例"""
        sectors = [
            SectorFlowSnapshot("TOP", 1000.0, -5.0),  # 头部自身净流出不计入信号③
        ] + _sectors(9, turnover=10.0, inflow=1.0)
        # top1=TOP；rest 9 家全净流入 → outflow_ratio=0
        result = detect_siphon_state(
            sectors,
            hhi_history=_flat_history(0.5),
            conc_history=_flat_history(-0.05),
            outflow_history=_flat_history(0.30),
            n_top=1,
        )
        # z_outflow = (0-0.30)/σ < 0，拉低总分 → 不触发
        assert result.z_outflow < 0.0
        assert result.is_siphon is False

    def test_zero_turnover_and_inflow_safe(self):
        """全零成交额/净流入不除零崩溃"""
        sectors = _sectors(10, turnover=0.0, inflow=0.0)
        result = detect_siphon_state(
            sectors,
            hhi_history=_flat_history(0.1),
            conc_history=_flat_history(0.1),
            outflow_history=_flat_history(0.1),
        )
        assert result.is_siphon is False

    def test_all_top_n_leaves_empty_rest(self):
        """n_top ≥ 板块总数 → 其余板块为空，流出比例 0（不除零崩溃）"""
        sectors = _sectors(3)
        result = detect_siphon_state(
            sectors,
            hhi_history=_flat_history(0.5),
            conc_history=_flat_history(0.5),
            outflow_history=_flat_history(0.0),
            n_top=5,
        )
        # 当日 outflow_ratio=0 与历史常态 0 持平 → z≈0
        assert result.z_outflow == pytest.approx(0.0)
