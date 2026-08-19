# [A_test] module_id: MOD-TEST-CROSS-E2E-NIGHT001 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-L05-001 | docs/03_modules/_domain_portfolio_core/blueprint.md | §test
# [MODULE] tests.cross.test_e2e_redblue_night001
# [INVARIANTS] tests_must_pass;no_todo_no_pass_no_fixme;非 mock 红队实证（仅 broker 外部边界为测试替身）
# [MODIFY-GUARD] only_add_tests;do_not_modify_source
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest exit 0 on pass, non-zero on fail
# [TESTS] tests/cross/test_e2e_redblue_night001.py
# [TTL] permanent
# [ARCH-REF] AI-NIGHT-001 阶段2 端到端红蓝对抗（真实 CH 数据全链连通/区间烟感/红队向量）
"""AI-NIGHT-001 阶段2 — Layer 2/3/4 跨层红蓝对抗测试（非 mock）。

真实 ClickHouse 数据（c1_market.kline_daily，9.66M 行实证在库）驱动：
  - Layer 2 全链连通: CH 数据 → load_history → momentum_20d 因子 → synthesize →
    TopNMomentumStrategy 权重 → DefaultBacktestEngine 执行 → ConstraintSolver 组合约束 →
    RiskLayerOrchestrator.evaluate_intraday 风控（仅 broker 为测试替身——外部边界，
    对齐 tests/ex_core/test_risk_layer_orchestrator.py 既定模式；各层内部逻辑全真）
  - Layer 3 区间烟感: 近 6 个月 10 只沪深300成分大盘股的动量回测，
    夏普/年化/换手/最大回撤判经验区间；与等权买入持有基准交叉对照（离谱=前视嫌疑）
  - Layer 4 红队向量:
    ① 除权日信号收益核算（#197 修复后 10送10 不再产生虚假 −50%）——真实
       _adjusted_close_panel/_compute_forward_returns 路径 + 真实 CH evaluate_factor；
    ② 满仓信号零成交 warning 显化（#210）——见 tests/backtest/test_toy_reconciliation_night001.py；
    ③ Σ=1 不变量极端输入（RegimeMetaAllocator 全策略越界 / ConstraintSolver 坍缩场景）

CH 不可达时整文件 skip（不阻断无 CH 环境的 CI 轨）。
"""
from __future__ import annotations

import math
from datetime import UTC, datetime
from decimal import Decimal

import numpy as np
import pandas as pd
import pytest

from zephyr.backtest.core.engine_base import BacktestResult
from zephyr.data import ch_reader
from zephyr.factor.core.evaluation import backtest as factor_bt
from zephyr.factor.core.evaluation.backtest import load_history
from zephyr.factor.factor_base import FactorRegistry
from zephyr.pf_core.strategy_engine.strategy_runner import (
    StrategyRunner,
    StrategyRunnerConfig,
)
from zephyr.pf_core.topn_momentum_strategy import TopNMomentumStrategy
from zephyr.governance.strategies.strategy_base import StrategyRegistry

# ── 测试常量：沪深300成分内 10 只大盘蓝筹（2026-02-02..2026-08-18 实证 131 个交易日在库）──
SYMBOLS = [
    "600519.SH", "000858.SZ", "601318.SH", "600036.SH", "000333.SZ",
    "600900.SH", "601899.SH", "600030.SH", "002594.SZ", "000651.SZ",
]
START = "2026-02-02"
END = "2026-08-18"

_runner_config = StrategyRunnerConfig(
    strategy_id="topn-momentum",
    factor_ids=("momentum_20d",),
    synthesis_method="equal_weight",
    rebalance_freq="W-FRI",
    pit_shift=1,
    top_n=5,
    max_single=0.20,
    initial_capital=1_000_000.0,
)


def _ch_available() -> bool:
    try:
        return ch_reader.count("c1_market.kline_daily", timeout=15) > 0
    except Exception:  # noqa: BLE001 — 探测性调用，任何失败都按不可达处理
        return False


pytestmark = pytest.mark.skipif(not _ch_available(), reason="ClickHouse 不可达（需 c1_market.kline_daily）")


@pytest.fixture(scope="module", autouse=True)
def _ensure_registered():
    """因子/策略注册（import 即注册；被他文件 clear 后补登，对齐 MVP 测试模式）。"""
    from zephyr.factor.momentum_factor import Momentum20d

    if "momentum_20d" not in FactorRegistry._registry:
        FactorRegistry.register(Momentum20d)
    if StrategyRegistry.get("topn-momentum") is None:
        StrategyRegistry.register(TopNMomentumStrategy)
    yield


@pytest.fixture(scope="module")
def e2e_result():
    """全链回测（模块级复用——真实 CH 查询只跑一次）。"""
    result = StrategyRunner().run_backtest(
        symbols=SYMBOLS, start=START, end=END, config=_runner_config
    )
    return result


@pytest.fixture(scope="module")
def weight_panel():
    _, panel = StrategyRunner().build_weight_panel(
        SYMBOLS, START, END, _runner_config
    )
    return panel


@pytest.fixture(scope="module")
def real_history():
    return load_history(SYMBOLS, START, END)


# ─────────────────────────────────────────────────────────────────────────────
# Layer 2 全链连通实证
# ─────────────────────────────────────────────────────────────────────────────


class TestFullChainConnectivity:
    """数据→信号→组合→执行→风控 全链非 mock 连通。"""

    def test_real_data_loaded(self, real_history):
        """数据层：真实 CH 日 K 加载（10 标的 × ≥120 交易日）。"""
        assert not real_history.empty
        assert real_history.index.names == ["symbol", "trade_date"]
        n_symbols = real_history.index.get_level_values("symbol").nunique()
        n_days = real_history.index.get_level_values("trade_date").nunique()
        assert n_symbols == 10
        assert n_days >= 120

    def test_engine_e2e_produces_coherent_result(self, e2e_result):
        """执行层：BacktestResult 全字段填充且自洽。"""
        r = e2e_result
        assert isinstance(r, BacktestResult)
        assert r.strategy_id == "topn-momentum"
        assert r.idempotency_key.startswith("bt-")
        assert r.trades_count > 0, "真实数据动量轮动应产生交易"
        assert r.start_date < r.end_date
        assert math.isfinite(r.total_return)
        assert math.isfinite(r.sharpe_ratio)
        assert 0.0 <= r.win_rate <= 1.0

    def test_rotation_sells_actually_happen(self, e2e_result):
        """P0-2 实盘级回归：周频轮动必须产生 SELL（跌出 top5 的持仓被清仓）。"""
        from zephyr.backtest.implementations.vectorized_engine import DefaultBacktestEngine

        engine = DefaultBacktestEngine()
        data, panel = StrategyRunner().build_weight_panel(SYMBOLS, START, END, _runner_config)
        if isinstance(data.index, pd.MultiIndex) and "trade_date" in (data.index.names or []):
            data.index = data.index.rename({"trade_date": "date"})
        engine.run(data=data, signals=panel, strategy_name="redblue-rotate")
        pf = engine.last_portfolio
        sells = [t for t in pf.trades_log if t["side"] == "SELL"]
        assert len(sells) > 0, "周频轮动 28 周一笔卖出都没有 → 清仓链断裂（P0-2 回归）"

    def test_weight_panel_pit_no_lookahead(self, weight_panel):
        """PIT 铁律：momentum_20d 需 20 日 warmup + pit_shift=1 → 前 ≥20 行权重全零。"""
        assert not weight_panel.empty
        row_sums = weight_panel.sum(axis=1)
        nonzero_idx = int((row_sums > 0).to_numpy().argmax())
        assert nonzero_idx >= 20, (
            f"首个非零权重出现在第 {nonzero_idx} 行（<20）→ 因子 warmup 期内出信号，前视嫌疑"
        )
        # 权重面板不变量：非负、Σ≤1
        assert (weight_panel.to_numpy() >= -1e-12).all()
        assert (row_sums <= 1.0 + 1e-9).all()

    def test_constraint_solver_consumes_real_weights(self, weight_panel):
        """组合层：真实权重面板最后一期 → ConstraintSolver 7 约束链（CTR-003）。"""
        from zephyr.pf_core.core.constraint_solver import ConstraintSolver
        from zephyr.shared.contracts.risk_limits import RiskLimits

        row_sums = weight_panel.sum(axis=1)
        last_day = row_sums[row_sums > 0].index[-1]
        weights = {s: float(w) for s, w in weight_panel.loc[last_day].items() if w > 0}
        assert weights, "最后一期应有非零权重"

        limits = RiskLimits(
            as_of_date=datetime.now(UTC),
            idempotency_key="redblue-e2e",
            max_gross_leverage=1.0,
            max_single_position=0.10,  # 严于策略 max_single=0.20 → 必触发 C7 裁剪
        )
        result = ConstraintSolver().solve(weights, limits)
        out_sum = float(np.sum(result.weights))
        assert out_sum <= 1.0 + 1e-9, "Σw 必须 ≤ max_gross_leverage"
        assert (result.weights <= 0.10 + 1e-9).all(), "单标的必须 ≤ max_single_position"
        c7 = [v for v in result.violations if v.constraint_id == "C7"]
        assert c7, "策略 0.20 权重触 0.10 上限应记 C7 违规"
        assert result.converged, "常规输入应收敛"

    def test_risk_layer_consumes_real_nav_series(self, e2e_result):
        """风控层：真实 NAV 序列逐日喂 evaluate_intraday（全真实组件，仅 broker 替身）。"""
        from zephyr.backtest.implementations.vectorized_engine import DefaultBacktestEngine
        from zephyr.ex_core.risk_layer_orchestrator import RiskLayerOrchestrator
        from zephyr.position.core.drawdown_controller import DrawdownController
        from zephyr.risk.core.drawdown_tracker import DrawdownTracker
        from zephyr.risk.core.tail_risk_monitor import TailRiskMonitor
        from zephyr.risk.core.var_calculator import VaRCalculator

        engine = DefaultBacktestEngine()
        data, panel = StrategyRunner().build_weight_panel(SYMBOLS, START, END, _runner_config)
        if isinstance(data.index, pd.MultiIndex) and "trade_date" in (data.index.names or []):
            data.index = data.index.rename({"trade_date": "date"})
        engine.run(data=data, signals=panel, strategy_name="redblue-risk")
        nav_series = engine.last_portfolio.nav_series.dropna()
        assert len(nav_series) >= 120

        orch = RiskLayerOrchestrator(
            drawdown_controller=DrawdownController(),
            drawdown_tracker=DrawdownTracker(initial_net_value=float(nav_series.iloc[0])),
            var_calculator=VaRCalculator(),
            tail_risk_monitor=TailRiskMonitor(),
            broker=_NavProbeBroker(),
        )
        snapshots = [orch.evaluate_intraday(nav=float(v)) for v in nav_series.iloc[1:]]
        assert len(snapshots) == len(nav_series) - 1
        for snap in snapshots:
            assert 0.0 < snap.position_cap <= 1.0 + 1e-9
            assert math.isfinite(snap.nav)
        # 样本充足后 VaR/尾部链应脱离 degraded（min_samples_for_var=30）
        late = snapshots[-1]
        assert not late.degraded, "130 点 NAV 序列下 VaR/尾部评估不应降级"


class _NavProbeBroker:
    """broker 外部边界测试替身（evaluate_intraday 不触 broker 调用，仅满足构造契约）。"""

    @property
    def broker_id(self) -> str:
        return "nav-probe"

    def get_positions(self):  # pragma: no cover - 本链路不调用
        raise NotImplementedError


# ─────────────────────────────────────────────────────────────────────────────
# Layer 3 区间合理性烟感
# ─────────────────────────────────────────────────────────────────────────────


class TestSmokeRanges:
    """近 6 个月大盘股动量回测——离谱区间即前视/成本漏算嫌疑（不离谱≠正确）。"""

    def test_metrics_within_empirical_ranges(self, e2e_result):
        r = e2e_result
        # 6 个月大盘蓝筹组合：|总收益| 超 60% 离谱
        assert -0.60 < r.total_return < 0.60, f"total_return={r.total_return:.4f} 离谱"
        # 年化对应区间（约 2 倍放大）：|年化| 超 150% 离谱
        assert -1.5 < r.annual_return < 1.5, f"annual_return={r.annual_return:.4f} 离谱"
        # 夏普：普通日频动量 |Sharpe|>4 离谱（前视/未来函数典型征兆）
        assert abs(r.sharpe_ratio) < 4.0, f"sharpe={r.sharpe_ratio:.4f} 离谱"
        # 最大回撤：大盘蓝筹组合 MDD>40% 离谱
        assert 0.0 <= r.max_drawdown < 0.40, f"mdd={r.max_drawdown:.4f} 离谱"
        # 胜率（正收益日占比）：长期 <20% 或 >80% 离谱
        assert 0.20 <= r.win_rate <= 0.80, f"win_rate={r.win_rate:.4f} 离谱"

    def test_turnover_sanity(self, e2e_result):
        """换手 sanity：28 周 W-FRI 调仓 + top5 轮动 → 至少个位数交易，至多几百笔。"""
        assert 5 <= e2e_result.trades_count <= 500, (
            f"trades_count={e2e_result.trades_count} 离谱（0=信号死链;>500=每日全换）"
        )

    def test_vs_equal_weight_buyhold_band(self, e2e_result, real_history):
        """与同池等权买入持有对照：|策略收益 − EW收益| > 35pp 即前视/成本漏算嫌疑。"""
        close = real_history["close"].unstack(level="symbol")
        first = close.iloc[0]
        last = close.iloc[-1]
        ew_return = float(((last - first) / first).mean())
        diff = abs(e2e_result.total_return - ew_return)
        assert diff <= 0.35, (
            f"策略 {e2e_result.total_return:.4f} vs 等权持有 {ew_return:.4f} "
            f"偏差 {diff:.4f} > 35pp → 需归因（前视/未来函数/成本漏算嫌疑）"
        )


# ─────────────────────────────────────────────────────────────────────────────
# Layer 4 红队攻击向量
# ─────────────────────────────────────────────────────────────────────────────


class TestRedTeamDividend:
    """向量①：除权日附近信号收益核算（#197 修复后不再产生虚假 −50%）。"""

    @staticmethod
    def _make_split_history() -> pd.DataFrame:
        """10送10 除权 toy 序列（真实函数消费的真实结构，非 mock）：

        除权前 3 日 close=20/adj=1；除权日 close=10（腰斩）/adj=2；后 3 日 close=10/adj=2。
        真实经济含义：持有者股数翻倍、总市值不变 → 跨除权日真实收益 ≈ 0%。
        """
        dates = pd.bdate_range("2026-06-01", periods=7)
        closes = [20.0, 20.0, 20.0, 10.0, 10.0, 10.0, 10.0]
        adj = [1.0, 1.0, 1.0, 2.0, 2.0, 2.0, 2.0]
        rows = [
            {"symbol": "600000", "trade_date": d, "close": c, "adj_factor": a}
            for d, c, a in zip(dates, closes, adj, strict=True)
        ]
        df = pd.DataFrame(rows).set_index(["symbol", "trade_date"])
        return df

    def test_forward_return_across_ex_date_not_phantom_half_loss(self):
        """#197 回归：复权面板下跨除权日前向收益 ≈ 0%（非 −50% 虚假亏损）。"""
        history = self._make_split_history()
        adj_panel = factor_bt._adjusted_close_panel(history)
        fwd = factor_bt._compute_forward_returns(adj_panel, horizon=1)
        # 除权前一日 (index 2) 的 1 日前向收益：adj_close 20→20（10×2）→ 0%
        ex_minus_1 = fwd.iloc[2, 0]
        assert ex_minus_1 == pytest.approx(0.0, abs=1e-12), (
            f"跨除权日前向收益={ex_minus_1}，#197 修复应消除 −50% 虚假亏损"
        )
        # 全序列无 |ret|>30% 的虚假跳变
        valid = fwd.dropna().to_numpy().ravel()
        assert (np.abs(valid) < 0.30).all(), "复权后不应存在除权跳变"

    def test_raw_close_would_show_phantom_loss_proving_fix_matters(self):
        """对照实验：raw close 面板下同一除权日确是 −50%（证 #197 修复必要性）。"""
        history = self._make_split_history()
        raw_panel = history["close"].unstack(level="symbol")
        fwd_raw = factor_bt._compute_forward_returns(raw_panel, horizon=1)
        assert fwd_raw.iloc[2, 0] == pytest.approx(-0.5, abs=1e-12)

    def test_adj_factor_defense_fallback(self):
        """防御口径：adj_factor NULL/0/负 → 回退 1.0（裁定#ARCH-ADJFACTOR-NULL-001）。"""
        dates = pd.bdate_range("2026-06-01", periods=3)
        rows = [
            {"symbol": "600000", "trade_date": dates[0], "close": 10.0, "adj_factor": None},
            {"symbol": "600000", "trade_date": dates[1], "close": 10.0, "adj_factor": 0.0},
            {"symbol": "600000", "trade_date": dates[2], "close": 10.0, "adj_factor": -1.0},
        ]
        df = pd.DataFrame(rows).set_index(["symbol", "trade_date"])
        panel = factor_bt._adjusted_close_panel(df)
        # 全部回退 1.0 → 复权价 == raw close，无 NaN 污染
        assert panel.notna().all().all()
        assert (panel == 10.0).all().all()

    def test_real_ch_adj_factor_uniformly_one_registered_limitation(self):
        """实证登记：当前 CH 主表 adj_factor 全表=1（#209② 遗留，本测试固化该事实）。

        含义：真实数据下复权面板退化为 raw close，真实除息缺口（如茅台年度分红
        约 −1.5%~−2.5% 跳空）会被计入策略盈亏——属已登记 P2 数据层遗留，
        非本阶段修复对象；本断言若因 adj_factor 接入真实值而失败，应改写为
        真实除权事件验证（届时 #209② 已治理）。
        """
        tsv = ch_reader.query(
            "SELECT countIf(adj_factor != 1) FROM c1_market.kline_daily"
        )
        n_non_one = int(tsv.strip().split()[0]) if tsv.strip() else -1
        assert n_non_one == 0, "adj_factor 已接入真实值（#209② 已治理）——请升级本测试为真实除权事件验证"

    def test_evaluate_factor_on_real_data_no_extreme_ic(self, _ensure_registered=None):
        """真实数据因子评估：momentum_20d IC 不应出现 |IC|>0.5 的离谱值（前视征兆）。"""
        result = factor_bt.evaluate_factor(
            "momentum_20d", SYMBOLS, START, END, horizon=5
        )
        assert result.sample_size > 10, "真实数据 IC 序列样本不足"
        assert abs(result.ic_mean) < 0.5, f"ic_mean={result.ic_mean} 离谱（前视嫌疑）"


class TestRedTeamSigma1Invariant:
    """向量③：Σ=1 硬不变量在极端输入下保持（全策略越界场景）。"""

    def test_allocator_n2_cap_infeasible_still_sigma1(self):
        """N=2 全贴 cap（0.4×2=0.8<1）→ 兜底归一化，Σ=1 硬不变量优先于 floor/cap。"""
        from zephyr.pf_alloc.core.regime_meta_allocator import RegimeMetaAllocator

        alloc = RegimeMetaAllocator(
            base_weights={"s1": 0.5, "s2": 0.5}, shrinkage_enabled=False
        )
        budget = alloc.allocate(
            regime_probabilities=[0.9, 0.1],
            performance_scores={"s1": 1.5, "s2": 1.5},  # 同分 → 等权 → 双双贴 cap
            risk_signal_inputs={"risk_base": 1.0},
        )
        total = sum(budget.allocations.values())
        assert total == pytest.approx(1.0, abs=1e-9), (
            f"N=2 cap 不可行场景 Σ={total}，Σ=1 硬不变量被破坏（#206 回归）"
        )

    def test_allocator_n25_all_floor_still_sigma1(self):
        """N=25 全贴 floor（25×0.05=1.25>1）→ 兜底归一化，Σ=1 保持。"""
        from zephyr.pf_alloc.core.regime_meta_allocator import RegimeMetaAllocator

        strategies = {f"s{i}": 1.0 for i in range(25)}
        alloc = RegimeMetaAllocator(shrinkage_enabled=False)
        budget = alloc.allocate(
            regime_probabilities=[0.5, 0.5],
            performance_scores=strategies,
            risk_signal_inputs={"risk_base": 1.0},
        )
        total = sum(budget.allocations.values())
        assert total == pytest.approx(1.0, abs=1e-9), (
            f"N=25 floor 不可行场景 Σ={total}，Σ=1 硬不变量被破坏（#206 回归）"
        )
        assert all(w > 0 for w in budget.allocations.values())

    def test_allocator_extreme_perf_dispersion_sigma1(self):
        """极端绩效离散（max×1.5/min×0.5）+ shrinkage 启用 → Σ=1 且 effective=alloc×shrinkage。"""
        from zephyr.pf_alloc.core.regime_meta_allocator import RegimeMetaAllocator

        alloc = RegimeMetaAllocator(shrinkage_enabled=True)
        scores = {f"s{i}": (1.5 if i % 2 == 0 else 0.5) for i in range(7)}
        budget = alloc.allocate(
            regime_probabilities=[0.97, 0.03],  # 高确信 → shrinkage≈1
            performance_scores=scores,
            risk_signal_inputs={"risk_base": 0.9, "resonance_penalty": 1.0},
        )
        total = sum(budget.allocations.values())
        assert total == pytest.approx(1.0, abs=1e-9)
        # effective_budget = allocation × global_shrinkage（两层一致性）
        for sid, eb in budget.effective_budgets.items():
            assert eb == pytest.approx(
                budget.allocations[sid] * budget.global_shrinkage, rel=1e-9
            )

    def test_constraint_solver_soft_crowding_one_shot_no_collapse(self):
        """#205 回归：ρ=0.85 软拥挤一次性减半（原 0.5^n 几何坍缩 → Σw≈8e-7）。

        max_correlation 提到 0.9 隔离 C5（专注拥挤链单变量验证）。
        """
        from zephyr.pf_core.core.constraint_solver import (
            ConstraintSolver,
            ConstraintSolverConfig,
        )
        from zephyr.shared.contracts.risk_limits import RiskLimits

        limits = RiskLimits(
            as_of_date=datetime.now(UTC), idempotency_key="rt-crowd",
            max_gross_leverage=1.0, max_single_position=0.6,
        )
        corr = np.array([[1.0, 0.85], [0.85, 1.0]])
        solver = ConstraintSolver(ConstraintSolverConfig(max_correlation=0.9))
        result = solver.solve(
            {"A": 0.5, "B": 0.5}, limits,
            assets=["A", "B"], correlation_matrix=corr,
        )
        out_sum = float(np.sum(result.weights))
        assert result.converged, "软拥挤一次性响应后应正常收敛"
        assert out_sum == pytest.approx(0.5, abs=1e-9), (
            f"软拥挤应一次性减半至 Σw=0.5，实际 {out_sum}（#205 坍缩回归）"
        )
        assert not [v for v in result.violations if v.constraint_id == "COLLAPSE"]

    def test_constraint_solver_hard_crowding_keeps_one(self):
        """ρ=0.95 硬拥挤：仅保留权重较大者。"""
        from zephyr.pf_core.core.constraint_solver import ConstraintSolver
        from zephyr.shared.contracts.risk_limits import RiskLimits

        limits = RiskLimits(
            as_of_date=datetime.now(UTC), idempotency_key="rt-hard",
            max_gross_leverage=1.0, max_single_position=0.9,
        )
        corr = np.array([[1.0, 0.95], [0.95, 1.0]])
        result = ConstraintSolver().solve(
            {"A": 0.6, "B": 0.4}, limits,
            assets=["A", "B"], correlation_matrix=corr,
        )
        w = dict(zip(["A", "B"], result.weights, strict=True))
        assert w["B"] == pytest.approx(0.0, abs=1e-12), "硬拥挤应清零权重较小者"
        assert w["A"] > 0

    def test_constraint_solver_same_sign_exposure_infeasible_not_collapse(self):
        """#207 回归：全同号市值暴露 → 标 infeasible 不缩放（原迭代缩放必坍缩）。"""
        from zephyr.pf_core.core.constraint_solver import ConstraintSolver
        from zephyr.shared.contracts.risk_limits import RiskLimits

        limits = RiskLimits(
            as_of_date=datetime.now(UTC), idempotency_key="rt-exp",
            max_gross_leverage=1.0, max_single_position=0.6,
        )
        result = ConstraintSolver().solve(
            {"A": 0.5, "B": 0.5}, limits,
            market_cap_exposures={"A": 1.0, "B": 1.0},  # 全同号且 |加权|>0.3σ
        )
        infeasible = [v for v in result.violations if v.constraint_name == "market_cap_exposure_infeasible"]
        assert infeasible, "全同号暴露必须标 infeasible（fail-visible）"
        out_sum = float(np.sum(result.weights))
        assert out_sum == pytest.approx(1.0, abs=1e-9), (
            f"不可达场景权重不应被缩放（Σw={out_sum}，#207 坍缩回归）"
        )
        assert result.converged

    def test_constraint_solver_extreme_leverage_clip(self):
        """极端输入 Σw=10 → 杠杆投影裁到 ≤1.0，不变量保持。"""
        from zephyr.pf_core.core.constraint_solver import ConstraintSolver
        from zephyr.shared.contracts.risk_limits import RiskLimits

        limits = RiskLimits(
            as_of_date=datetime.now(UTC), idempotency_key="rt-lev",
            max_gross_leverage=1.0, max_single_position=1.0,
        )
        result = ConstraintSolver().solve({"A": 5.0, "B": 5.0}, limits)
        assert float(np.sum(result.weights)) <= 1.0 + 1e-9
