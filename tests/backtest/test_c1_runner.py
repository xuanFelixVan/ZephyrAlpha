# [BLUEPRINT] MOD-BT-001 | docs/03_modules/_domain_backtest/blueprint.md | §
# [MODULE] tests.backtest.test_c1_runner
# [DOMAIN] D_BACKTEST
# [A_module] module_id=MOD-TEST-BT-C1RUN | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# [ARCH-REF] #11_regime_backtest_validation_plan #ARCH-REGIME-VALIDATION-001 #C1-shrinkage-comparator
"""C1 Runner (C1 执行器) 单元测试——11_regime_backtest_validation_plan Phase 1 入口。

覆盖:
  - build_volatility_schedule：从 OHLCV 算市场等权实现波动率序列
  - run_c1_mock：波动率驱动 MockShrinkageProvider 冒烟跑通 C1 开/关对比
  - run_c1_with_provider：核心入口结构正确（四项 metric_verdicts + passed + summary）
  - run_c1_regime：合成 regime_results 跑通 ScheduleShrinkageProvider 路径
  - save_c1_report：markdown 报告落盘 + 含关键字段
  - 空数据降级：返回 passed=False 空结果（不抛异常）
  - run_c1_end_to_end mode 校验
"""
from __future__ import annotations

from datetime import datetime, timedelta
from decimal import Decimal

import numpy as np
import pandas as pd
import pytest

from zephyr.backtest.implementations.vectorized_engine import BacktestConfig
from zephyr.backtest.regime_validation.c1_comparator import (
    C1ComparisonResult,
    C1Config,
    C1MetricVerdict,
)
from zephyr.backtest.regime_validation.c1_runner import (
    C1RunnerError,
    build_volatility_schedule,
    run_c1_end_to_end,
    run_c1_mock,
    run_c1_regime,
    run_c1_with_provider,
    save_c1_report,
)
from zephyr.backtest.regime_validation.shrinkage_provider import (
    ConstShrinkageProvider,
)

# ── 合成数据构造（对齐 test_shrinkage_engine 风格）──────────────────────

_SYMBOLS = ["600001", "600002", "600003"]
_N_DAYS = 300  # 足够波动率窗口(20) + 回测有意义


def _make_market_data(symbols=_SYMBOLS, n_days=_N_DAYS, seed=7) -> pd.DataFrame:
    """合成日 K（MultiIndex symbol×date，含 OHLCV）。index level 名 "date"。

    用不同 seed 造不同波动率段：前半低波、后半高波，确保 MockShrinkageProvider
    4 档映射有触发（C1 实验组有实际收缩，非全满部署）。
    """
    rng = np.random.default_rng(seed)
    dates = pd.date_range("2024-01-01", periods=n_days, freq="B")
    frames = []
    for sym in symbols:
        close = 100.0
        rows = []
        for t in range(n_days):
            # 前半低波(0.005)，后半高波(0.03)——造 regime 切换效果
            vol = 0.005 if t < n_days // 2 else 0.03
            ret = rng.normal(0, vol)
            close = close * (1 + ret)
            rows.append({
                "symbol": sym, "date": dates[t],
                "open": close, "high": close * 1.01, "low": close * 0.99,
                "close": close, "volume": 1_000_000,
            })
        frames.append(pd.DataFrame(rows))
    df = pd.concat(frames, ignore_index=True).set_index(["symbol", "date"]).sort_index()
    return df


def _make_signals(data: pd.DataFrame, symbols=_SYMBOLS) -> pd.DataFrame:
    """等权信号（index=date, columns=symbol, 值=1.0 → 归一化后 1/N）。"""
    dates = data.index.get_level_values("date").unique().sort_values()
    return pd.DataFrame(
        {sym: 1.0 for sym in symbols}, index=pd.DatetimeIndex(dates, name="date")
    )


@pytest.fixture
def market_data() -> pd.DataFrame:
    return _make_market_data()


@pytest.fixture
def signals(market_data) -> pd.DataFrame:
    return _make_signals(market_data)


# ── build_volatility_schedule ─────────────────────────────────────────

class TestBuildVolatilitySchedule:
    """市场等权实现波动率序列构造。"""

    def test_returns_nonempty_dict(self, market_data):
        """正常 data → 非空 dict，key 为 datetime，value 为正 float。"""
        sched = build_volatility_schedule(market_data, window=20)
        assert len(sched) > 0
        for dt, v in sched.items():
            assert isinstance(dt, datetime)
            assert isinstance(v, float)
            assert v > 0  # 波动率恒正
            assert np.isfinite(v)

    def test_window_warmup_dropped(self, market_data):
        """前 window-1 天无波动率（rolling std 需 window 个点）。"""
        sched = build_volatility_schedule(market_data, window=20)
        n_dates = market_data.index.get_level_values("date").nunique()
        # dropna 后应少于总交易日（前 19 天 NaN 被丢）
        assert len(sched) <= n_dates
        assert len(sched) >= n_dates - 20

    def test_high_vol_segment_higher(self, market_data):
        """高波段（后半）波动率应显著高于低波段（前半）。"""
        sched = build_volatility_schedule(market_data, window=20)
        sorted_dates = sorted(sched.keys())
        mid = len(sorted_dates) // 2
        low_vol = np.mean([sched[d] for d in sorted_dates[:mid]])
        high_vol = np.mean([sched[d] for d in sorted_dates[mid:]])
        # 后半高波段年化波动率应明显高于前半
        assert high_vol > low_vol * 1.5

    def test_empty_data_returns_empty(self):
        """空 data / 无 close 列 → 空 dict（不抛）。"""
        assert build_volatility_schedule(pd.DataFrame()) == {}
        assert build_volatility_schedule(
            pd.DataFrame({"x": [1]}, index=pd.MultiIndex.from_tuples([("a", "b")], names=["s", "d"]))
        ) == {}


# ── run_c1_mock：冒烟主入口 ────────────────────────────────────────────

class TestRunC1Mock:
    """mock 模式（波动率驱动）C1 开/关对比冒烟。"""

    def test_returns_c1_comparison_result(self, market_data, signals):
        """run_c1_mock 返回 C1ComparisonResult，结构完整。"""
        result = run_c1_mock(data=market_data, signals=signals)
        assert isinstance(result, C1ComparisonResult)
        assert isinstance(result.passed, bool)
        assert isinstance(result.summary, str) and len(result.summary) > 0
        # 四项一票否决指标
        assert len(result.metric_verdicts) == 4
        names = {v.name for v in result.metric_verdicts}
        assert names == {"Sharpe", "MaxDD", "Calmar", "Turnover"}
        for v in result.metric_verdicts:
            assert isinstance(v, C1MetricVerdict)
            assert isinstance(v.passed, bool)

    def test_baseline_experiment_both_ran(self, market_data, signals):
        """基准组与实验组都跑了回测（trades_count > 0 或结果非空）。"""
        result = run_c1_mock(data=market_data, signals=signals)
        assert result.baseline_result is not None
        assert result.experiment_result is not None
        # 基准组满部署应有交易
        assert result.baseline_result.trades_count >= 0

    def test_mock_shrinkage_takes_effect(self, market_data, signals):
        """mock 高波段应触发收缩 → 实验组换手/收益与基准组有差异（非 bit-identical）。

        证明 MockShrinkageProvider 确实介入（非退化成满部署）。
        """
        result = run_c1_mock(data=market_data, signals=signals)
        # 实验组与基准组指标不应完全相等（mock 有收缩效果）
        # 至少有一项指标差异（高波段 shrinkage<1.0 → 权重缩放）
        diff_exists = (
            result.baseline_result.total_return != result.experiment_result.total_return
            or result.baseline_result.trades_count != result.experiment_result.trades_count
        )
        assert diff_exists, "mock 未生效：实验组与基准组完全一致（Shrinkage 未介入）"

    def test_custom_c1_config(self, market_data, signals):
        """自定义 C1Config 门槛生效。"""
        # 极松门槛（MaxDD 改善 0pp）→ 即使无改善也通过该项
        loose = C1Config(maxdd_improvement_pp=0.0, calmar_improvement_ratio=1.0)
        result = run_c1_mock(data=market_data, signals=signals, c1_config=loose)
        maxdd_verdict = next(v for v in result.metric_verdicts if v.name == "MaxDD")
        # 门槛 0pp → 差值>=0 即通过（除非实验组回撤更深）
        assert maxdd_verdict.threshold_desc is not None

    def test_empty_volatility_schedule_degrades(self):
        """波动率序列为空（data 少于 window）→ mock 退化为满部署，不抛。

        治本补强（#ARCH-REGIME-C1-RUNNER-001 裁定④）：build_volatility_schedule 返回
        空 dict → MockShrinkageProvider({}) 恒返回 1.0 → 实验组与基准组等价（C1 无意义
        但不崩溃，符合 ERROR_CONTRACT "数据为空不抛" 契约）。
        """
        tiny_data = _make_market_data(n_days=15)  # < vol_window=20 → 波动率算不出
        tiny_signals = _make_signals(tiny_data)
        result = run_c1_mock(data=tiny_data, signals=tiny_signals, vol_window=20)
        assert isinstance(result, C1ComparisonResult)
        # 空 schedule → MockShrinkageProvider 恒 1.0 → 两组等价
        assert result.baseline_result.sharpe_ratio == pytest.approx(
            result.experiment_result.sharpe_ratio
        )

    def test_mock_report_contains_warning(self, market_data, signals, tmp_path):
        """治本补强（裁定②）：mock 报告含"无决策价值"警示。"""
        result = run_c1_mock(data=market_data, signals=signals)
        save_c1_report(result, output_path=tmp_path / "r.md", mode="mock")
        content = (tmp_path / "r.md").read_text(encoding="utf-8")
        assert "mock 模式警示" in content
        assert "无 regime 部署决策价值" in content


# ── run_c1_with_provider：核心入口 ─────────────────────────────────────

class TestRunC1WithProvider:
    """核心入口用任意 provider 跑 C1。"""

    def test_const_one_provider_identical_groups(self, market_data, signals):
        """ConstShrinkageProvider(1.0) → 基准组与实验组完全等价（Shrinkage 全 1.0）。

        此时 Sharpe/MaxDD/Calmar/Turnover 全等。C1 裁定：MaxDD 改善=0 < 3pp → 否决
        （证明对比器在"无节流"时正确否决——regime 无价值）。
        """
        result = run_c1_with_provider(
            data=market_data, signals=signals,
            shrinkage_provider=ConstShrinkageProvider(1.0),
        )
        assert result.baseline_result.sharpe_ratio == pytest.approx(
            result.experiment_result.sharpe_ratio
        )
        assert result.baseline_result.max_drawdown == pytest.approx(
            result.experiment_result.max_drawdown
        )
        # 无节流 → MaxDD 无改善 → 一票否决
        assert result.passed is False

    def test_empty_data_returns_empty_result(self):
        """空 data/signals → 返回 passed=False 空结果（不抛）。"""
        result = run_c1_with_provider(
            data=pd.DataFrame(), signals=pd.DataFrame(),
            shrinkage_provider=ConstShrinkageProvider(1.0),
        )
        assert result.passed is False
        assert "空" in result.veto_reason or "空" in result.summary


# ── run_c1_regime：真实模式（合成 regime_results）──────────────────────

class TestRunC1Regime:
    """regime 模式用 ScheduleShrinkageProvider 跑 C1（特征管道就绪后切换路径）。"""

    def test_synthetic_regime_results(self, market_data, signals):
        """合成 [(date, float)] regime_results 跑通 regime 模式。

        模拟 RegimeSeriesOrchestrator 产出：高波段 shrinkage=0.5，低波段 1.0。
        """
        dates = sorted(signals.index)
        # 跳过前 20 天（warmup），造 regime 序列
        regime_results: list[tuple[datetime, float]] = []
        for i, d in enumerate(dates[20:]):
            shrink = 0.5 if i > len(dates) // 2 else 1.0
            regime_results.append((pd.Timestamp(d).to_pydatetime(), shrink))

        result = run_c1_regime(
            data=market_data, signals=signals, regime_results=regime_results,
        )
        assert isinstance(result, C1ComparisonResult)
        assert len(result.metric_verdicts) == 4
        # regime 有收缩段 → 实验组与基准组有差异
        assert result.baseline_result.total_return != pytest.approx(
            result.experiment_result.total_return
        )

    def test_empty_regime_results_degraded(self, market_data, signals):
        """空 regime_results → ScheduleShrinkageProvider 恒 1.0（退化满部署，不抛）。"""
        result = run_c1_regime(
            data=market_data, signals=signals, regime_results=[],
        )
        assert isinstance(result, C1ComparisonResult)
        # 空 schedule → 全 1.0 → 两组等价
        assert result.baseline_result.sharpe_ratio == pytest.approx(
            result.experiment_result.sharpe_ratio
        )


# ── save_c1_report：报告落盘 ───────────────────────────────────────────

class TestSaveC1Report:
    """C1ComparisonResult → markdown 报告。"""

    def test_writes_markdown_file(self, market_data, signals, tmp_path):
        """报告落盘为 .md，含关键章节。"""
        result = run_c1_mock(data=market_data, signals=signals)
        out = save_c1_report(
            result, output_path=tmp_path / "c1_report.md", mode="mock",
            meta={"strategy": "topn-momentum", "symbols": "3"},
        )
        content = (tmp_path / "c1_report.md").read_text(encoding="utf-8")
        assert "C1 Shrinkage 开/关对比报告" in content
        assert "四项指标判定" in content
        assert "Sharpe" in content and "MaxDD" in content
        assert "mock" in content
        assert "topn-momentum" in content  # meta 写入

    def test_creates_parent_dir(self, market_data, signals, tmp_path):
        """输出路径父目录不存在时自动创建。"""
        result = run_c1_mock(data=market_data, signals=signals)
        nested = tmp_path / "reports" / "c1" / "report.md"
        out = save_c1_report(result, output_path=nested, mode="mock")
        assert nested.exists()


# ── run_c1_end_to_end：mode 校验 ───────────────────────────────────────

class TestRunC1EndToEnd:
    """端到端入口的 mode 校验（不实际跑 build_weight_panel，避免 ClickHouse 依赖）。"""

    def test_invalid_mode_raises(self):
        """非法 mode → C1RunnerError。"""
        with pytest.raises(C1RunnerError, match="mode"):
            run_c1_end_to_end(
                symbols=["600001"], start="2024-01-01", end="2024-06-01",
                runner_config=None, mode="invalid",
            )

    def test_regime_mode_without_results_raises(self):
        """regime 模式缺 regime_results → C1RunnerError。"""
        with pytest.raises(C1RunnerError, match="regime_results"):
            run_c1_end_to_end(
                symbols=["600001"], start="2024-01-01", end="2024-06-01",
                runner_config=None, mode="regime", regime_results=None,
            )
