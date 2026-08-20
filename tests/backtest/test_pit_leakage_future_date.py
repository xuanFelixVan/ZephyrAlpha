# [BLUEPRINT] MOD-BT-001 | (auto-injected by S4 reconciler) | §
# [TTL] permanent
# [A_test] module_id: MOD-GOV_test_pit_leakage_future_date | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [MODULE] tests.backtest.test_pit_leakage_future_date
# [TESTS] src/zephyr/backtest/core/pit_manager.py（90 号 Phase2 泄漏测试自动化）
# [TTL] task_bound
"""90 号 Phase2 项（#14 PIT 一致性）：deliberate future-date 泄漏测试自动化。

裁定真源：90_methodology_open_questions.md §14（v2.0.0）——
  PIT 自动化校验 Phase 2 增强：deliberate future-date test（label_date=tomorrow
  确认零特征 join）自动化纳入 BT-10 体系；时间精度陷阱（date vs timestamp 粒度）
  加入 PIT 校验 checklist。
"""

from __future__ import annotations

from datetime import datetime, timedelta

import pandas as pd
import pytest

from zephyr.backtest.core.pit_manager import PITManager

_TODAY = datetime(2024, 6, 3)
_TOMORROW = _TODAY + timedelta(days=1)


def _feature_df(available_at: datetime, value: float = 1.0) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "date": [_TODAY],
            "symbol": ["600000.SH"],
            "available_at": [available_at],
            "factor_x": [value],
        }
    )


class TestDeliberateFutureDate:
    """故意未来日期样本必须零 join（泄漏探针）。"""

    def test_tomorrow_available_feature_not_joined(self):
        """available_at=tomorrow 的特征行，today 查询必须零命中。"""
        mgr = PITManager()
        df = _feature_df(available_at=_TOMORROW)
        visible = mgr.as_of_join(df, query_time=_TODAY, available_time_col="available_at")
        assert len(visible) == 0

    def test_today_available_feature_joined(self):
        """对照组：available_at=today 的特征行正常 join（探针灵敏度证明）。"""
        mgr = PITManager()
        df = _feature_df(available_at=_TODAY, value=3.0)
        visible = mgr.as_of_join(df, query_time=_TODAY, available_time_col="available_at")
        assert len(visible) == 1
        assert visible.iloc[0]["factor_x"] == 3.0

    def test_mixed_batch_only_past_visible(self):
        """混合批次：仅过去可见行被 join，未来行全部拦截。"""
        mgr = PITManager()
        df = pd.concat(
            [_feature_df(_TODAY, 1.0), _feature_df(_TOMORROW, 2.0)],
            ignore_index=True,
        )
        visible = mgr.as_of_join(df, query_time=_TODAY, available_time_col="available_at")
        assert visible["factor_x"].tolist() == [1.0]


class TestVersionAlignment:
    """重述泄漏双版本：查询时点只见当时已知最新版本。"""

    def test_restatement_future_version_invisible(self):
        mgr = PITManager()
        original = pd.DataFrame(
            {
                "date": [datetime(2024, 1, 2)],
                "symbol": ["600000.SH"],
                "available_at": [datetime(2024, 1, 2)],
                "net_profit": [1.0],
            }
        )
        restated = pd.DataFrame(
            {
                "date": [datetime(2024, 1, 2)],
                "symbol": ["600000.SH"],
                "available_at": [datetime(2024, 6, 1)],  # 后续修订版本
                "net_profit": [2.0],
            }
        )
        df = pd.concat([original, restated], ignore_index=True)

        # 修订前查询：只见 original
        v1 = mgr.as_of_join(df, query_time=datetime(2024, 3, 1), available_time_col="available_at")
        assert v1["net_profit"].tolist() == [1.0]
        # 修订后查询：版本对齐取最新可用
        v2 = mgr.as_of_join(df, query_time=datetime(2024, 6, 1), available_time_col="available_at")
        assert v2["net_profit"].tolist() == [2.0]


class TestEmbargoFutureLabel:
    """Embargo 窗口内标签（前瞻窗口未闭合）必须剔除。"""

    def test_recent_label_embargoed(self):
        mgr = PITManager()  # 默认 embargo 5 个交易日
        labels = pd.DataFrame(
            {
                "date": [datetime(2024, 5, 31), datetime(2024, 6, 7)],
                "forward_return": [0.01, 0.02],
            }
        )
        safe = mgr.apply_embargo(labels, current_time=datetime(2024, 6, 10))
        # 6/7 距 6/10 不足 5 个交易日→剔除；5/31 已超窗口→保留
        assert safe["date"].tolist() == [pd.Timestamp(2024, 5, 31)]


class TestGranularityChecklist:
    """时间精度陷阱（date vs timestamp 粒度）checklist 项：字符串日期与 datetime 混用一致拦截。"""

    def test_string_date_granularity_future_blocked(self):
        mgr = PITManager()
        df = pd.DataFrame(
            {
                "date": ["2024-06-04"],  # date 粒度字符串
                "symbol": ["600000.SH"],
                "available_at": ["2024-06-04"],
                "factor_x": [9.9],
            }
        )
        visible = mgr.as_of_join(df, query_time=_TODAY, available_time_col="available_at")
        assert len(visible) == 0
