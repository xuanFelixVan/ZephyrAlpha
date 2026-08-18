# [BLUEPRINT] gap-7 cancel_rate_guard | (auto-injected) |
# [TTL] permanent
"""CancelRateGuard 单元测试（40_execution_broker §决策⑫ gap 7 施工）。

覆盖：滚动撤单率计算、12% 预警降级、15% 冻结、15 笔/秒限频。
"""

from __future__ import annotations

import time
from datetime import date, timedelta

import pytest

from zephyr.ex_core.cancel_rate_guard import (
    CancelRateGuard,
    CancelRateStatus,
    DailyDeclarationStatus,
)

# ── 撤单率计算 ────────────────────────────────────────────────────────────────


class TestCancelRate:
    def test_empty_window_zero_rate(self):
        guard = CancelRateGuard()
        assert guard.cancel_rate == 0.0
        assert guard.status is CancelRateStatus.NORMAL

    def test_all_fills_zero_rate(self):
        guard = CancelRateGuard()
        for _ in range(100):
            guard.record_fill()
        assert guard.cancel_rate == 0.0
        assert guard.status is CancelRateStatus.NORMAL

    def test_all_cancels_100pct_rate(self):
        guard = CancelRateGuard()
        for _ in range(100):
            guard.record_cancel()
        assert guard.cancel_rate == 1.0
        assert guard.status is CancelRateStatus.FROZEN

    def test_mixed_10pct_rate(self):
        guard = CancelRateGuard()
        # 90 成交 + 10 撤单 = 10%
        for _ in range(90):
            guard.record_fill()
        for _ in range(10):
            guard.record_cancel()
        assert guard.cancel_rate == pytest.approx(0.10)
        assert guard.status is CancelRateStatus.NORMAL  # 10% < 12%

    def test_mixed_15pct_rate_warn(self):
        guard = CancelRateGuard()
        # 88 成交 + 12 撤单 = 12% → WARN（>12%）
        for _ in range(88):
            guard.record_fill()
        for _ in range(12):
            guard.record_cancel()
        assert guard.cancel_rate == pytest.approx(0.12)
        # 12% 不 > 12%，需超过才预警
        assert guard.status is CancelRateStatus.NORMAL

    def test_mixed_above_12pct_warn(self):
        guard = CancelRateGuard()
        # 87 成交 + 13 撤单 ≈ 13% > 12% → WARN
        for _ in range(87):
            guard.record_fill()
        for _ in range(13):
            guard.record_cancel()
        assert guard.cancel_rate == pytest.approx(0.13, abs=0.001)
        assert guard.status is CancelRateStatus.WARN_ONLY_PLACE

    def test_mixed_above_15pct_frozen(self):
        guard = CancelRateGuard()
        # 84 成交 + 16 撤单 = 16% > 15% → FROZEN
        for _ in range(84):
            guard.record_fill()
        for _ in range(16):
            guard.record_cancel()
        assert guard.cancel_rate == pytest.approx(0.16, abs=0.001)
        assert guard.status is CancelRateStatus.FROZEN

    def test_rolling_window_evicts_old(self):
        """窗口滚动：旧记录被挤出，撤单率随新记录更新。"""
        guard = CancelRateGuard(window_size=100)
        # 初始 60 撤单 + 40 成交 = 60%（FROZEN）
        for _ in range(60):
            guard.record_cancel()
        for _ in range(40):
            guard.record_fill()
        assert guard.status is CancelRateStatus.FROZEN
        # 再补 100 成交，挤出旧的 60 撤单 → 100 成交 = 0%
        for _ in range(100):
            guard.record_fill()
        assert guard.cancel_rate == 0.0
        assert guard.status is CancelRateStatus.NORMAL

    def test_total_counts(self):
        guard = CancelRateGuard(window_size=500)
        for _ in range(80):
            guard.record_fill()
        for _ in range(20):
            guard.record_cancel()
        assert guard.total_resolved == 100
        assert guard.total_cancels == 20


# ── 决策接口 ──────────────────────────────────────────────────────────────────


class TestCanPlaceCancel:
    def test_normal_allows_place_and_cancel(self):
        guard = CancelRateGuard()
        for _ in range(100):
            guard.record_fill()  # 0% 撤单率
        assert guard.can_place_order() is True
        assert guard.can_cancel_order() is True

    def test_warn_blocks_cancel_allows_place(self):
        guard = CancelRateGuard()
        # 13% 撤单率 → WARN
        for _ in range(87):
            guard.record_fill()
        for _ in range(13):
            guard.record_cancel()
        assert guard.status is CancelRateStatus.WARN_ONLY_PLACE
        assert guard.can_place_order() is True   # 预警仍可挂单
        assert guard.can_cancel_order() is False  # 但禁止撤单

    def test_frozen_blocks_both(self):
        guard = CancelRateGuard()
        # 16% 撤单率 → FROZEN
        for _ in range(84):
            guard.record_fill()
        for _ in range(16):
            guard.record_cancel()
        assert guard.status is CancelRateStatus.FROZEN
        assert guard.can_place_order() is False   # 冻结禁止新下单
        assert guard.can_cancel_order() is False  # 冻结禁止撤单


# ── 限频 15 笔/秒 ─────────────────────────────────────────────────────────────


class TestRateLimit:
    def test_under_limit_allowed(self):
        guard = CancelRateGuard(rate_limit_per_sec=15)
        for _ in range(10):
            guard.record_submit()
        assert guard.can_submit_now() is True

    def test_at_limit_blocked(self):
        guard = CancelRateGuard(rate_limit_per_sec=15)
        for _ in range(15):
            guard.record_submit()
        assert guard.can_submit_now() is False

    def test_over_limit_blocked(self):
        guard = CancelRateGuard(rate_limit_per_sec=15)
        for _ in range(20):
            guard.record_submit()
        assert guard.can_submit_now() is False

    def test_limit_resets_after_one_second(self):
        """1 秒后限频窗口清空，恢复提交。"""
        guard = CancelRateGuard(rate_limit_per_sec=5)
        for _ in range(5):
            guard.record_submit()
        assert guard.can_submit_now() is False
        # 等待 1.1 秒（略大于 1 秒确保窗口清理）
        time.sleep(1.1)
        assert guard.can_submit_now() is True

    def test_cancel_consumes_rate_limit(self):
        """撤单也消耗限频额度。"""
        guard = CancelRateGuard(rate_limit_per_sec=15)
        for _ in range(15):
            guard.record_cancel()
        assert guard.can_submit_now() is False


# ── 重置 ──────────────────────────────────────────────────────────────────────


class TestReset:
    def test_reset_clears_window(self):
        guard = CancelRateGuard()
        for _ in range(84):
            guard.record_fill()
        for _ in range(16):
            guard.record_cancel()
        assert guard.status is CancelRateStatus.FROZEN
        guard.reset()
        assert guard.cancel_rate == 0.0
        assert guard.status is CancelRateStatus.NORMAL
        assert guard.total_resolved == 0

    def test_reset_clears_rate_limit(self):
        guard = CancelRateGuard(rate_limit_per_sec=5)
        for _ in range(5):
            guard.record_submit()
        assert guard.can_submit_now() is False
        guard.reset()
        assert guard.can_submit_now() is True


# ── 边界场景 ──────────────────────────────────────────────────────────────────


class TestEdgeCases:
    def test_small_window_cold_start_no_statistical_hallucination(self):
        """冷启动统计幻觉（AI-R2 红队 ATK-4）：样本不足时 100% 撤单率不触发冻结。

        原行为：8 成交 + 2 撤单 = 20% → FROZEN（开盘首单废单重挂即全账户冻结）。
        修复后：样本 < min_samples_for_status（默认 20）一律 NORMAL。
        """
        guard = CancelRateGuard(window_size=10)
        # 8 成交 + 2 撤单 = 20%（样本 10 < 20 → 统计幻觉门禁）
        for _ in range(8):
            guard.record_fill()
        for _ in range(2):
            guard.record_cancel()
        assert guard.cancel_rate == pytest.approx(0.20)
        assert guard.status is CancelRateStatus.NORMAL

    def test_cold_start_single_cancel_not_frozen(self):
        """开盘首笔撤单 1/1=100% 撤单率 → 不冻结（AI-R2 红队 ATK-4）。"""
        guard = CancelRateGuard()
        guard.record_cancel()
        assert guard.cancel_rate == 1.0
        assert guard.status is CancelRateStatus.NORMAL
        assert guard.can_place_order() is True
        assert guard.can_cancel_order() is True

    def test_min_samples_threshold_boundary(self):
        """样本达 min_samples_for_status 即恢复统计判定（19→20 边界）。"""
        guard = CancelRateGuard(min_samples_for_status=20)
        # 19 笔样本（85 成交 + 15 撤单 = 78.9% 撤单率）→ 样本不足 → NORMAL
        for _ in range(4):
            guard.record_fill()
        for _ in range(15):
            guard.record_cancel()
        assert guard.cancel_rate == pytest.approx(15 / 19, abs=0.001)
        assert guard.status is CancelRateStatus.NORMAL
        # 补 1 笔成交 → 20 笔样本（15/20=75% 撤单率）→ 超 15% → FROZEN
        guard.record_fill()
        assert guard.status is CancelRateStatus.FROZEN

    def test_threshold_boundary_12pct(self):
        """恰好 12% 不触发预警（>12% 才触发）。"""
        guard = CancelRateGuard(window_size=100)
        # 88 成交 + 12 撤单 = 12.0%，不 > 12%
        for _ in range(88):
            guard.record_fill()
        for _ in range(12):
            guard.record_cancel()
        assert guard.cancel_rate == pytest.approx(0.12)
        assert guard.status is CancelRateStatus.NORMAL

    def test_threshold_boundary_15pct(self):
        """恰好 15% 不触发冻结（>15% 才触发）。"""
        guard = CancelRateGuard(window_size=100)
        # 85 成交 + 15 撤单 = 15.0%，不 > 15% → WARN
        for _ in range(85):
            guard.record_fill()
        for _ in range(15):
            guard.record_cancel()
        assert guard.cancel_rate == pytest.approx(0.15)
        assert guard.status is CancelRateStatus.WARN_ONLY_PLACE

    def test_custom_thresholds(self):
        """自定义阈值（更保守或更宽松）。"""
        guard = CancelRateGuard(
            warn_threshold=0.05, freeze_threshold=0.10
        )
        for _ in range(90):
            guard.record_fill()
        for _ in range(10):
            guard.record_cancel()
        # 10% > 5% warn, 10% 不 > 10% freeze → WARN
        assert guard.status is CancelRateStatus.WARN_ONLY_PLACE


# ── 日申报笔数硬计数器（43 号 §8 方案 A：5000 预警 / 1 万阻断，AI-ASM-001 装配批）──


class TestDailyDeclarationCounter:
    """日申报笔数=报单+撤单合计（24 号 §3.7 申报口径），自然日自动清零。"""

    def test_submit_counts_declaration(self):
        guard = CancelRateGuard()
        guard.record_submit()
        assert guard.daily_declaration_count == 1

    def test_cancel_counts_declaration(self):
        """撤单同属申报口径。"""
        guard = CancelRateGuard()
        guard.record_cancel()
        assert guard.daily_declaration_count == 1

    def test_fill_not_counted(self):
        """成交不是申报，不计数。"""
        guard = CancelRateGuard()
        guard.record_fill()
        assert guard.daily_declaration_count == 0

    def test_submit_and_cancel_sum(self):
        guard = CancelRateGuard()
        for _ in range(3):
            guard.record_submit()
        for _ in range(2):
            guard.record_cancel()
        assert guard.daily_declaration_count == 5

    def test_default_thresholds_normal_below_5000(self):
        guard = CancelRateGuard()
        for _ in range(4999):
            guard.record_submit()
        assert guard.daily_declaration_count == 4999
        assert guard.daily_declaration_status is DailyDeclarationStatus.NORMAL

    def test_default_thresholds_warning_at_5000(self):
        """5000 笔整即预警（>= 口径）。"""
        guard = CancelRateGuard()
        for _ in range(5000):
            guard.record_submit()
        assert guard.daily_declaration_status is DailyDeclarationStatus.WARNING

    def test_default_thresholds_blocked_at_10000(self):
        """1 万笔整即阻断（>= 口径），第 10001 笔起 C-002 拒单。"""
        guard = CancelRateGuard()
        for _ in range(10000):
            guard.record_submit()
        assert guard.daily_declaration_status is DailyDeclarationStatus.BLOCKED

    def test_warning_not_blocked_between(self):
        guard = CancelRateGuard()
        for _ in range(9999):
            guard.record_submit()
        assert guard.daily_declaration_status is DailyDeclarationStatus.WARNING

    def test_custom_daily_thresholds(self):
        guard = CancelRateGuard(daily_warn_threshold=3, daily_block_threshold=5)
        assert guard.daily_declaration_status is DailyDeclarationStatus.NORMAL
        for _ in range(3):
            guard.record_submit()
        assert guard.daily_declaration_status is DailyDeclarationStatus.WARNING
        for _ in range(2):
            guard.record_submit()
        assert guard.daily_declaration_status is DailyDeclarationStatus.BLOCKED

    def test_rollover_new_day_resets(self):
        """跨自然日自动清零（申报笔数为交易日口径）。"""
        guard = CancelRateGuard(daily_warn_threshold=3, daily_block_threshold=5)
        for _ in range(4):
            guard.record_submit()
        assert guard.daily_declaration_count == 4
        # 模拟跨日：把计数所属日改为昨天
        guard._daily_date = date.today() - timedelta(days=1)
        assert guard.daily_declaration_count == 0
        assert guard.daily_declaration_status is DailyDeclarationStatus.NORMAL
        # 新一日重新计数
        guard.record_submit()
        assert guard.daily_declaration_count == 1

    def test_reset_clears_daily_counter(self):
        guard = CancelRateGuard()
        guard.record_submit()
        guard.record_cancel()
        assert guard.daily_declaration_count == 2
        guard.reset()
        assert guard.daily_declaration_count == 0
        assert guard.daily_declaration_status is DailyDeclarationStatus.NORMAL

    def test_threshold_crossing_logs_once(self, caplog):
        """预警/阻断日志仅阈值穿越瞬间各一次，不逐笔刷日志。"""
        guard = CancelRateGuard(daily_warn_threshold=2, daily_block_threshold=4)
        with caplog.at_level("WARNING"):
            guard.record_submit()  # 1
            guard.record_submit()  # 2 → 穿越预警线
            guard.record_submit()  # 3（仍预警，不再刷）
            guard.record_submit()  # 4 → 穿越阻断线
            guard.record_submit()  # 5（仍阻断，不再刷）
        warn_msgs = [r for r in caplog.records if "日申报笔数预警" in r.message]
        block_msgs = [r for r in caplog.records if "日申报笔数阻断" in r.message]
        assert len(warn_msgs) == 1
        assert len(block_msgs) == 1
