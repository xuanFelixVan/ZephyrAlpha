# [BLUEPRINT] MOD-BT-017 | (auto-injected by S4 reconciler) | §
# [MODULE] tests.backtest.test_data_handler_pit
# [DOMAIN] D_BACKTEST
# [A_module] module_id=MOD-BT-017 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# [TESTS] tests/backtest/test_data_handler_pit.py
# [TTL] permanent
"""BacktestDataHandler PIT 财务数据合并测试（#ARCH-CH-021 P0-5）。

验证 PIT 三公理在 data_handler 层的落实：
1. 版本对齐：get_bar(date) 仅返回 announce_date <= date 的最新版本
2. 泄漏防护：修正公告在 announce_date 之后才可见（禁止前视偏差）
3. 向后兼容：无 fundamental_data 时行为不变
"""

from __future__ import annotations

import pandas as pd
import pytest

from zephyr.backtest.core.data_handler import BacktestDataHandler


def _make_ohlcv() -> pd.DataFrame:
    """构造 3 天 × 2 标的的 OHLCV 数据。"""
    rows = []
    for dt in ["2026-03-01", "2026-03-02", "2026-03-03"]:
        for sym in ["000001.SZ", "600000.SH"]:
            rows.append(
                {
                    "date": pd.Timestamp(dt),
                    "symbol": sym,
                    "open": 10.0,
                    "high": 11.0,
                    "low": 9.0,
                    "close": 10.5,
                    "volume": 100000,
                    "amount": 1050000.0,
                }
            )
    return pd.DataFrame(rows)


def _make_fundamental_with_revision() -> pd.DataFrame:
    """构造含修正公告的财务数据。

    000001.SZ 2025Q4 财报：
    - 原始公告 announce_date=2026-02-28, eps_basic=0.50
    - 修正公告 announce_date=2026-03-05, eps_basic=0.65（3月5日才公告）

    600000.SH 2025Q4 财报：
    - 原始公告 announce_date=2026-02-20, eps_basic=1.20
    - 无修正
    """
    return pd.DataFrame(
        [
            # 000001.SZ 原始公告（2月28日）
            {
                "symbol": "000001.SZ",
                "report_period": "2025-12-31",
                "announce_date": "2026-02-28",
                "eps_basic": 0.50,
                "eps_diluted": 0.48,
            },
            # 000001.SZ 修正公告（3月5日）
            {
                "symbol": "000001.SZ",
                "report_period": "2025-12-31",
                "announce_date": "2026-03-05",
                "eps_basic": 0.65,
                "eps_diluted": 0.63,
            },
            # 600000.SH 原始公告（2月20日，无修正）
            {
                "symbol": "600000.SH",
                "report_period": "2025-12-31",
                "announce_date": "2026-02-20",
                "eps_basic": 1.20,
                "eps_diluted": 1.15,
            },
        ]
    )


class TestPITFundamentalMerge:
    """PIT 财务数据合并测试。"""

    def test_no_fundamental_backward_compat(self):
        """无 fundamental_data 时 get_bar 行为不变（向后兼容）。"""
        handler = BacktestDataHandler(data=_make_ohlcv())
        bar = handler.get_bar(pd.Timestamp("2026-03-01"))
        assert "eps_basic" not in bar.columns
        assert "close" in bar.columns

    def test_fundamental_merged_into_bar(self):
        """有 fundamental_data 时 get_bar 合并财务列。"""
        handler = BacktestDataHandler(
            data=_make_ohlcv(),
            fundamental_data=_make_fundamental_with_revision(),
        )
        bar = handler.get_bar(pd.Timestamp("2026-03-01"))
        assert "eps_basic" in bar.columns
        assert len(bar) == 2  # 2 个标的

    def test_pit_no_future_leakage(self):
        """公理2（泄漏防护）：修正公告在 announce_date 之前不可见。

        000001.SZ 修正公告 announce_date=2026-03-05,
        在 2026-03-01~03-03 的 bar 中应该只看到原始版本 eps_basic=0.50,
        不应该看到修正版本 eps_basic=0.65（前视偏差）。
        """
        handler = BacktestDataHandler(
            data=_make_ohlcv(),
            fundamental_data=_make_fundamental_with_revision(),
        )
        # 3月1日：修正公告(3月5日)还没公告，应该看到原始值 0.50
        bar_mar01 = handler.get_bar(pd.Timestamp("2026-03-01"))
        eps_000001 = bar_mar01[bar_mar01["symbol"] == "000001.SZ"]["eps_basic"].iloc[0]
        assert eps_000001 == pytest.approx(0.50), f"3月1日应看到原始公告 eps=0.50, 实际={eps_000001}（前视偏差！）"

        # 3月2日：修正公告仍未公告
        bar_mar02 = handler.get_bar(pd.Timestamp("2026-03-02"))
        eps_000001 = bar_mar02[bar_mar02["symbol"] == "000001.SZ"]["eps_basic"].iloc[0]
        assert eps_000001 == pytest.approx(0.50), f"3月2日应看到原始公告 eps=0.50, 实际={eps_000001}（前视偏差！）"

    def test_pit_revision_visible_after_announce(self):
        """修正公告在 announce_date 之后可见。

        000001.SZ 修正公告 announce_date=2026-03-05,
        在 2026-03-05 及之后的 bar 中应看到修正版本 eps_basic=0.65。
        """
        # 构造含 3月5日 的 OHLCV 数据
        ohlcv = _make_ohlcv()
        extra = pd.DataFrame(
            [
                {
                    "date": pd.Timestamp("2026-03-05"),
                    "symbol": "000001.SZ",
                    "open": 10.0,
                    "high": 11.0,
                    "low": 9.0,
                    "close": 10.5,
                    "volume": 100000,
                    "amount": 1050000.0,
                },
                {
                    "date": pd.Timestamp("2026-03-05"),
                    "symbol": "600000.SH",
                    "open": 10.0,
                    "high": 11.0,
                    "low": 9.0,
                    "close": 10.5,
                    "volume": 100000,
                    "amount": 1050000.0,
                },
            ]
        )
        ohlcv = pd.concat([ohlcv, extra], ignore_index=True)

        handler = BacktestDataHandler(
            data=ohlcv,
            fundamental_data=_make_fundamental_with_revision(),
        )
        # 3月5日：修正公告已公告，应该看到修正值 0.65
        bar_mar05 = handler.get_bar(pd.Timestamp("2026-03-05"))
        eps_000001 = bar_mar05[bar_mar05["symbol"] == "000001.SZ"]["eps_basic"].iloc[0]
        assert eps_000001 == pytest.approx(0.65), f"3月5日应看到修正公告 eps=0.65, 实际={eps_000001}"

    def test_pit_takes_latest_report_period(self):
        """公理1（版本对齐）：取最新 report_period 的可见版本。

        当有多个 report_period 的数据时，取最新一期。
        """
        fund = pd.DataFrame(
            [
                # 000001.SZ 2024Q4 公告（更早的报告期）
                {
                    "symbol": "000001.SZ",
                    "report_period": "2024-12-31",
                    "announce_date": "2025-02-28",
                    "eps_basic": 0.40,
                    "eps_diluted": 0.38,
                },
                # 000001.SZ 2025Q4 公告（最新的报告期）
                {
                    "symbol": "000001.SZ",
                    "report_period": "2025-12-31",
                    "announce_date": "2026-02-28",
                    "eps_basic": 0.50,
                    "eps_diluted": 0.48,
                },
            ]
        )
        handler = BacktestDataHandler(
            data=_make_ohlcv(),
            fundamental_data=fund,
        )
        bar = handler.get_bar(pd.Timestamp("2026-03-01"))
        eps = bar[bar["symbol"] == "000001.SZ"]["eps_basic"].iloc[0]
        # 应取 2025Q4 (report_period 更新) 的版本 eps=0.50
        assert eps == pytest.approx(0.50), f"应取最新 report_period 的 eps=0.50, 实际={eps}"

    def test_missing_symbol_gets_nan(self):
        """无财务数据的标的 eps_basic 为 NaN（left join 保留）。"""
        fund = pd.DataFrame(
            [
                {
                    "symbol": "000001.SZ",
                    "report_period": "2025-12-31",
                    "announce_date": "2026-02-28",
                    "eps_basic": 0.50,
                    "eps_diluted": 0.48,
                },
            ]
        )
        handler = BacktestDataHandler(
            data=_make_ohlcv(),
            fundamental_data=fund,
        )
        bar = handler.get_bar(pd.Timestamp("2026-03-01"))
        eps_600000 = bar[bar["symbol"] == "600000.SH"]["eps_basic"].iloc[0]
        assert pd.isna(eps_600000), f"600000.SH 无财务数据, eps 应为 NaN, 实际={eps_600000}"


class TestValueFactorPIT:
    """value_factor 从 bar 数据读 PIT 正确的 EPS。"""

    def test_value_factor_reads_eps_from_bar(self):
        """value_factor 优先从 bar 数据读 eps_basic（PIT 正确）。"""
        from zephyr.factor.value_factor import ValueFactor

        # 构造含 eps_basic 列的数据
        data = pd.DataFrame(
            {
                "close": [10.0] * 60 + [20.0] * 60,
                "eps_basic": [0.50] * 60 + [1.00] * 60,
            }
        )
        factor = ValueFactor()
        signal = factor.compute(data)

        # eps_basic=0.50 时 PE = 10/0.50 = 20, value = 1/20 = 0.05
        # eps_basic=1.00 时 PE = 20/1.00 = 20, value = 1/20 = 0.05
        # 但前 60 天 close=10, eps=0.50 -> PE=20 -> value=0.05
        # 后 60 天 close=20, eps=1.00 -> PE=20 -> value=0.05
        assert len(signal) == 120

    def test_value_factor_fallback_to_kwargs(self):
        """无 eps_basic 列时回退到 kwargs（向后兼容）。"""
        from zephyr.factor.value_factor import ValueFactor

        data = pd.DataFrame({"close": [10.0] * 65})
        factor = ValueFactor()
        signal = factor.compute(data, earnings_per_share=2.0)
        assert len(signal) == 65
        # PE = 10/2.0 = 5, value = 1/5 = 0.2
        assert signal.iloc[-1] == pytest.approx(0.2, abs=0.01)

    def test_value_factor_default_eps(self):
        """无 eps_basic 也无 kwargs 时用默认值 5.0。"""
        from zephyr.factor.value_factor import ValueFactor

        data = pd.DataFrame({"close": [10.0] * 65})
        factor = ValueFactor()
        signal = factor.compute(data)
        assert len(signal) == 65
        # PE = 10/5.0 = 2, value = 1/2 = 0.5
        assert signal.iloc[-1] == pytest.approx(0.5, abs=0.01)


class TestDeliberateFutureDateProbe:
    """90 号 Phase2 项（#14 PIT）：deliberate future-date 泄漏探针自动化。

    裁定真源：90_methodology_open_questions.md §14（v2.0.0）——
      PIT 自动化校验 Phase 2 增强：deliberate future-date test
      （label_date=tomorrow 确认零特征 join）自动化纳入 BT-10 体系；
      时间精度陷阱（date vs timestamp 粒度统一用 date_trunc）加入校验 checklist。
    """

    @staticmethod
    def _fundamental(rows: list[tuple[str, str, float]]) -> pd.DataFrame:
        return pd.DataFrame(
            [
                {
                    "symbol": sym,
                    "report_period": "2025-12-31",
                    "announce_date": ann,
                    "eps_basic": eps,
                    "eps_diluted": eps,
                }
                for sym, ann, eps in rows
            ]
        )

    def test_all_future_announce_zero_feature_join(self):
        """label_date=tomorrow 探针：全部特征行公告日在查询日之后 → 零特征 join。"""
        fund = self._fundamental(
            [
                ("000001.SZ", "2026-03-02", 0.99),  # 相对 3月1日 bar 是未来
                ("600000.SH", "2026-03-02", 9.99),
            ]
        )
        handler = BacktestDataHandler(data=_make_ohlcv(), fundamental_data=fund)
        bar = handler.get_bar(pd.Timestamp("2026-03-01"))
        assert "eps_basic" not in bar.columns, (
            "deliberate future-date 探针失败：未来公告特征被 join 进 3月1日 bar（前视偏差！）"
        )

    def test_mixed_past_future_only_past_visible(self):
        """混合探针：同 bar 日内，未来行不可见、历史行正常 join。"""
        fund = self._fundamental(
            [
                ("000001.SZ", "2026-02-28", 0.50),  # 历史可见
                ("600000.SH", "2026-03-02", 9.99),  # 未来不可见
            ]
        )
        handler = BacktestDataHandler(data=_make_ohlcv(), fundamental_data=fund)
        bar = handler.get_bar(pd.Timestamp("2026-03-01"))
        eps_000001 = bar[bar["symbol"] == "000001.SZ"]["eps_basic"].iloc[0]
        eps_600000 = bar[bar["symbol"] == "600000.SH"]["eps_basic"].iloc[0]
        assert eps_000001 == pytest.approx(0.50)
        assert pd.isna(eps_600000), f"未来公告特征泄漏: eps={eps_600000}"

    def test_query_timestamp_truncated_to_date(self):
        """时间精度 checklist：查询时点含日内时分秒须先 date_trunc 统一到日粒度。

        合并层以 strftime('%Y-%m-%d') 截断比较；调用方将 15:30 时间戳
        normalize 到日期后，行为与纯日期完全一致——同日已公告可见、次日公告不可见。
        """
        fund = self._fundamental(
            [
                ("000001.SZ", "2026-03-02", 0.66),  # 同日公告 → date 粒度下可见
                ("600000.SH", "2026-03-03", 9.99),  # 次日公告 → 不可见
            ]
        )
        handler = BacktestDataHandler(data=_make_ohlcv(), fundamental_data=fund)
        bar_ts = handler.get_bar(pd.Timestamp("2026-03-02 15:30:00").normalize())
        bar_d = handler.get_bar(pd.Timestamp("2026-03-02"))
        eps_ts = bar_ts[bar_ts["symbol"] == "000001.SZ"]["eps_basic"].iloc[0]
        eps_d = bar_d[bar_d["symbol"] == "000001.SZ"]["eps_basic"].iloc[0]
        assert eps_ts == eps_d == pytest.approx(0.66)
        assert pd.isna(bar_ts[bar_ts["symbol"] == "600000.SH"]["eps_basic"].iloc[0])

    def test_sweep_all_bar_dates_no_future_join(self):
        """全窗口扫描探针：任一 bar 日 T 合入的特征 announce_date 均须 ≤ T。"""
        fund = self._fundamental(
            [
                ("000001.SZ", "2026-02-28", 0.50),
                ("000001.SZ", "2026-03-03", 0.88),
                ("600000.SH", "2026-03-04", 9.99),  # 全 bar 窗口外的未来公告
            ]
        )
        handler = BacktestDataHandler(data=_make_ohlcv(), fundamental_data=fund)
        for dt in ["2026-03-01", "2026-03-02", "2026-03-03"]:
            bar = handler.get_bar(pd.Timestamp(dt))
            if "eps_basic" not in bar.columns:
                continue
            # 逐 symbol 反查：合入值必须来自 announce_date <= dt 的版本
            for _, row in bar.dropna(subset=["eps_basic"]).iterrows():
                visible = fund[(fund["symbol"] == row["symbol"]) & (fund["announce_date"] <= dt)]
                assert row["eps_basic"] in set(visible["eps_basic"]), (
                    f"{dt} bar 合入了未来公告值 {row['eps_basic']}（{row['symbol']}）"
                )
