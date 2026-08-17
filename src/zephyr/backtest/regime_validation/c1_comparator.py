# [BLUEPRINT] MOD-BT-001 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] zephyr.backtest.regime_validation.c1_comparator
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] zephyr.backtest.core.engine_base; zephyr.backtest.core.portfolio; zephyr.backtest.implementations.shrinkage_engine; zephyr.backtest.implementations.vectorized_engine; zephyr.backtest.regime_validation.shrinkage_provider
# [CONSUMERS] 人工审查 ; 11_regime_backtest_validation_plan Phase 1 验证
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 基准/实验组除 Shrinkage 外全等(同config/数据/信号); 一票否决(C1不过=regime不部署); MaxDD存负值(更高=更好); 不修改输入
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] C1ShrinkageComparatorError(ZA-BT-0017)
# [TESTS] tests/backtest/test_c1_comparator.py
# [A_module] module_id=MOD-BT-001 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# [ARCH-REF] #11_regime_backtest_validation_plan #C1-shrinkage-comparator #MOD-REGIME-001

"""L_BACKTEST — C1 Shrinkage 开/关对比器 (C1: 一票否决裁定)

11_regime_backtest_validation_plan §4.3 C1 核心验证——Shrinkage 开 vs 关两组回测对比，判定 regime
风险节流是否"不伤害 Sharpe 且改善回撤"。**一票否决：C1 不通过 = regime 不部署**
（回退静态等权）。

实验设计（11_regime_backtest_validation_plan §4.3 + §5）:
  - 基准组（关）: ShrinkageBacktestEngine + ConstShrinkageProvider(1.0)  → 满部署
  - 实验组（开）: ShrinkageBacktestEngine + 真实/mock shrinkage_provider  → 节流
  - 同一批策略、同一历史区间、同一交易成本（除 Shrinkage 外全等，可溯源对比）

对比指标 + 通过门槛（§5 汇总表，行业基准对照 Morwane OOS 2013-2026）:
  | 指标     | 判定                                            | 行业基准         |
  |----------|-------------------------------------------------|------------------|
  | Sharpe   | S_开 ≥ S_关 − 0.1（不显著伤害）                 | 1.43→1.43 不变   |
  | MaxDD    | DD_开 − DD_关 ≥ 3pp（改善，存负值更高=更好）    | −14.2%→−10.3%    |
  | Calmar   | C_开 ≥ C_关 × 1.2（提升 ≥ 20%）                 | 1.04→1.43 +38%   |
  | Turnover | T_开 ≤ T_关 × 2（换手不爆）                     | 1.7×/yr          |

  四项全过 → passed=True；任一不过 → passed=False + veto_reason（一票否决）。

Calmar = annual_return / |max_drawdown|（MaxDD 存负值，取绝对值）。
Turnover = Σ(|fill.quantity × fill.price|) / (avg_nav × num_years)（年化单向换手）。

依据: 11_regime_backtest_validation_plan §4.3/§5（C1 一票否决）+ 30_multi_strategy_concurrency §2.2
SSoT: depgraph MOD-BT-001 / MOD-REGIME-001
Version: 0.1.0
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Optional

import pandas as pd

from zephyr.backtest.core.engine_base import BacktestResult
from zephyr.backtest.core.portfolio import Portfolio
from zephyr.backtest.implementations.shrinkage_engine import (
    ShrinkageBacktestEngine,
    ShrinkageProvider,
)
from zephyr.backtest.implementations.vectorized_engine import BacktestConfig
from zephyr.backtest.regime_validation.shrinkage_provider import (
    ConstShrinkageProvider,
    clamp_shrinkage,
)

try:  # 治理基类缺失时降级为 Exception，保证模块可独立 import
    from zephyr.shared.foundation.errors import ZephyrBaseError
except Exception:  # pragma: no cover
    ZephyrBaseError = Exception  # type: ignore[assignment,misc]

_logger = logging.getLogger(__name__)


class C1ShrinkageComparatorError(ZephyrBaseError):
    """ZA-BT-0017: C1 对比器错误（回测失败/输入非法）。

    改号留痕：原 ZA-BT-0011 与 result_repository.ArtifactNotFoundError 重码，
    #ARCH-ERRCODE-001 裁定 git 首引入者保留 canonical，本类后引入（2026-08-06）改号。
    """

    error_code = "ZA-BT-0017"


# ──────────────────────────────────────────────────────────────────────────────
# 配置（C 类可调参数，默认值来自 11_regime_backtest_validation_plan §5）
# ──────────────────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class C1Config:
    """C1 开/关对比门槛配置——不可变。

    默认值取自 11_regime_backtest_validation_plan §5 验证标准汇总表（行业基准 Morwane OOS 2013-2026）。
    """

    sharpe_tolerance: float = 0.1           # S_开 ≥ S_关 − tol（不显著伤害）
    maxdd_improvement_pp: float = 0.03      # DD_开 − DD_关 ≥ 此值（3pp，存负值更高=更好）
    calmar_improvement_ratio: float = 1.2   # C_开 ≥ C_关 × ratio（提升 ≥20%）
    turnover_max_ratio: float = 2.0         # T_开 ≤ T_关 × ratio（换手不爆）
    trading_days_per_year: int = 252        # 年化交易日数（Turnover/Calmar 年化用）

    def __post_init__(self) -> None:
        if self.calmar_improvement_ratio <= 0:
            raise C1ShrinkageComparatorError(
                f"calmar_improvement_ratio must be > 0, got {self.calmar_improvement_ratio}"
            )
        if self.turnover_max_ratio <= 0:
            raise C1ShrinkageComparatorError(
                f"turnover_max_ratio must be > 0, got {self.turnover_max_ratio}"
            )
        if self.trading_days_per_year <= 0:
            raise C1ShrinkageComparatorError(
                f"trading_days_per_year must be > 0, got {self.trading_days_per_year}"
            )


# ──────────────────────────────────────────────────────────────────────────────
# 数据模型（frozen 不可变）
# ──────────────────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class C1MetricVerdict:
    """单项指标的开/关对比判定——不可变。"""

    name: str               # Sharpe / MaxDD / Calmar / Turnover
    baseline_value: float   # 关（基准组）
    experiment_value: float # 开（实验组）
    threshold_desc: str     # 门槛描述（人类可读）
    passed: bool            # 是否通过
    detail: str             # 判定细节（含差值/比例）


@dataclass(frozen=True)
class C1ComparisonResult:
    """C1 开/关对比结果——不可变。

    passed=False 即一票否决：regime 检测器不部署（回退静态等权）。
    """

    baseline_result: BacktestResult
    experiment_result: BacktestResult
    baseline_turnover: float
    experiment_turnover: float
    baseline_calmar: float
    experiment_calmar: float
    metric_verdicts: list[C1MetricVerdict]
    passed: bool                       # 四项全过=True
    veto_reason: Optional[str]         # None=通过；否则=首个失败指标说明
    summary: str                       # 人类可读总结


# ──────────────────────────────────────────────────────────────────────────────
# 对比器
# ──────────────────────────────────────────────────────────────────────────────


class C1ShrinkageComparator:
    """Shrinkage 开/关对比器（C1 一票否决裁定）。

    Usage（11_regime_backtest_validation_plan Phase 1 核心验证）:
        comparator = C1ShrinkageComparator()
        result = comparator.compare(
            data=data_df,
            signals=signals_df,
            shrinkage_provider=schedule_provider,  # 开：regime 预计算序列
            backtest_config=BacktestConfig(...),
        )
        if not result.passed:
            print(f"一票否决: {result.veto_reason}")  # regime 不部署
        else:
            print("C1 通过，进入 Phase 2 模型质量验证")

    不变量:
      - 基准组与实验组除 Shrinkage 外完全一致（同 config/数据/信号）
      - 基准组 = ConstShrinkageProvider(1.0)（满部署，等价 DefaultBacktestEngine）
      - 一票否决：四项指标任一不过 → passed=False
    """

    def __init__(self, config: C1Config | None = None) -> None:
        self._config = config or C1Config()
        # 供 experiment_tracking.c1_adapter 取 nav_series 用（不改 compare 返回值，向后兼容）
        self.last_baseline_portfolio: Optional[Portfolio] = None
        self.last_experiment_portfolio: Optional[Portfolio] = None

    @property
    def config(self) -> C1Config:
        return self._config

    # ── 公开 API：编排模式 ──

    def compare(
        self,
        data: pd.DataFrame,
        signals: pd.DataFrame,
        shrinkage_provider: ShrinkageProvider,
        backtest_config: BacktestConfig | None = None,
        strategy_name: str = "c1-shrinkage",
        initial_capital: float | None = None,
    ) -> C1ComparisonResult:
        """编排开/关两组回测并裁定（C1 主入口）。

        Args:
            data: OHLCV 数据（同 DefaultBacktestEngine.run）。
            signals: 信号 DataFrame（date × symbol，目标权重）。
            shrinkage_provider: 实验组（开）的 Shrinkage 供给方。
            backtest_config: 回测配置（两组共用，确保除 Shrinkage 外全等）。
            strategy_name: 策略名（两组共用）。
            initial_capital: 初始资金（两组共用）。

        Returns:
            C1ComparisonResult（含四项指标判定 + 一票否决裁定）。

        Raises:
            C1ShrinkageComparatorError: 任一组回测异常。
        """
        cfg = backtest_config or BacktestConfig()
        # 关闭过拟合门控阻断（C1 对比不应被过拟合门控中断，需完整跑完两组）
        safe_cfg = self._ensure_gate_off(cfg)

        # 基准组（关）：ConstShrinkageProvider(1.0)
        baseline_engine = ShrinkageBacktestEngine(
            config=safe_cfg, shrinkage_provider=ConstShrinkageProvider(1.0)
        )
        # 实验组（开）：传入的 shrinkage_provider
        experiment_engine = ShrinkageBacktestEngine(
            config=safe_cfg, shrinkage_provider=shrinkage_provider
        )

        try:
            baseline_result = baseline_engine.run(
                data=data, signals=signals,
                initial_capital=initial_capital,
                strategy_name=strategy_name,
            )
            experiment_result = experiment_engine.run(
                data=data, signals=signals,
                initial_capital=initial_capital,
                strategy_name=strategy_name,
            )
        except Exception as exc:
            raise C1ShrinkageComparatorError(
                f"C1 回测执行失败: {exc}"
            ) from exc

        # 暴露 portfolio 引用供 experiment_tracking.c1_adapter 序列化 nav 曲线
        self.last_baseline_portfolio = baseline_engine.last_portfolio
        self.last_experiment_portfolio = experiment_engine.last_portfolio
        return self.evaluate(
            baseline_result=baseline_result,
            experiment_result=experiment_result,
            baseline_portfolio=baseline_engine.last_portfolio,
            experiment_portfolio=experiment_engine.last_portfolio,
        )

    # ── 公开 API：评估模式（已跑完两组回测，仅裁定）──

    def evaluate(
        self,
        baseline_result: BacktestResult,
        experiment_result: BacktestResult,
        baseline_portfolio: Optional[Portfolio] = None,
        experiment_portfolio: Optional[Portfolio] = None,
    ) -> C1ComparisonResult:
        """对已跑完的开/关两组回测结果做裁定。

        compare() 内部调用此方法；外部已自行跑回测时可直接用此方法。

        Args:
            baseline_result: 关（基准组）回测结果。
            experiment_result: 开（实验组）回测结果。
            baseline_portfolio: 基准组 Portfolio（算 Turnover 用，None→Turnover=0）。
            experiment_portfolio: 实验组 Portfolio（同上）。
        """
        cfg = self._config

        base_calmar = _compute_calmar(
            baseline_result.annual_return, baseline_result.max_drawdown
        )
        exp_calmar = _compute_calmar(
            experiment_result.annual_return, experiment_result.max_drawdown
        )
        base_turnover = _compute_turnover(
            baseline_portfolio, cfg.trading_days_per_year
        )
        exp_turnover = _compute_turnover(
            experiment_portfolio, cfg.trading_days_per_year
        )

        verdicts: list[C1MetricVerdict] = [
            self._verdict_sharpe(
                baseline_result.sharpe_ratio, experiment_result.sharpe_ratio
            ),
            self._verdict_maxdd(
                baseline_result.max_drawdown, experiment_result.max_drawdown
            ),
            self._verdict_calmar(base_calmar, exp_calmar),
            self._verdict_turnover(base_turnover, exp_turnover),
        ]

        failed = [v for v in verdicts if not v.passed]
        passed = not failed
        veto_reason: Optional[str] = failed[0].detail if failed else None
        summary = self._build_summary(
            baseline_result, experiment_result,
            base_calmar, exp_calmar,
            base_turnover, exp_turnover,
            passed, veto_reason,
        )

        return C1ComparisonResult(
            baseline_result=baseline_result,
            experiment_result=experiment_result,
            baseline_turnover=base_turnover,
            experiment_turnover=exp_turnover,
            baseline_calmar=base_calmar,
            experiment_calmar=exp_calmar,
            metric_verdicts=verdicts,
            passed=passed,
            veto_reason=veto_reason,
            summary=summary,
        )

    # ── 单指标判定 ──

    def _verdict_sharpe(self, base: float, exp: float) -> C1MetricVerdict:
        tol = self._config.sharpe_tolerance
        passed = exp >= base - tol
        diff = exp - base
        return C1MetricVerdict(
            name="Sharpe",
            baseline_value=base,
            experiment_value=exp,
            threshold_desc=f"S_开 ≥ S_关 − {tol}",
            passed=passed,
            detail=(
                f"Sharpe 关={base:.4f} 开={exp:.4f} 差={diff:+.4f} "
                f"门槛≥{base - tol:.4f} → {'通过' if passed else '否决'}"
            ),
        )

    def _verdict_maxdd(self, base: float, exp: float) -> C1MetricVerdict:
        # MaxDD 回撤减小 = 改善。metrics._calculate_max_drawdown 返回正值
        # （如 0.142 = 14.2% 回撤），越小越好；若上游存负值（-0.142）则越高越好。
        # 两种约定统一为绝对值：改善 = |DD_关| − |DD_开| ≥ improvement_pp
        # （修正：原 exp-base 在正值约定下误判，2026-08-06 C1 验证发现）
        imp = self._config.maxdd_improvement_pp
        diff = abs(base) - abs(exp)
        passed = diff >= imp
        return C1MetricVerdict(
            name="MaxDD",
            baseline_value=base,
            experiment_value=exp,
            threshold_desc=f"|DD_关| − |DD_开| ≥ {imp:.2%}（回撤减小=改善）",
            passed=passed,
            detail=(
                f"MaxDD 关={base:.4f} 开={exp:.4f} 改善={diff:+.4f} "
                f"门槛≥{imp:.4f} → {'通过' if passed else '否决'}"
            ),
        )

    def _verdict_calmar(self, base: float, exp: float) -> C1MetricVerdict:
        ratio = self._config.calmar_improvement_ratio
        # 基线 Calmar 为正：要求 exp ≥ base × ratio（提升 ≥20%）
        # 基线 Calmar 非正（亏损）：退化为 exp ≥ base（不变差），并标注
        if base > 0:
            threshold = base * ratio
            passed = exp >= threshold
            desc = f"C_开 ≥ C_关 × {ratio}"
        else:
            threshold = base
            passed = exp >= threshold
            desc = f"C_开 ≥ C_关（基线非正，退化为不变差判定）"
        return C1MetricVerdict(
            name="Calmar",
            baseline_value=base,
            experiment_value=exp,
            threshold_desc=desc,
            passed=passed,
            detail=(
                f"Calmar 关={base:.4f} 开={exp:.4f} 门槛≥{threshold:.4f} "
                f"→ {'通过' if passed else '否决'}"
            ),
        )

    def _verdict_turnover(self, base: float, exp: float) -> C1MetricVerdict:
        max_ratio = self._config.turnover_max_ratio
        threshold = base * max_ratio
        # 基线无换手（base=0）：开组也不应有换手爆炸，门槛=0
        if base <= 0:
            passed = exp <= 0
            desc = "T_开 = 0（基线无换手）"
            threshold = 0.0
        else:
            passed = exp <= threshold
            desc = f"T_开 ≤ T_关 × {max_ratio}"
        return C1MetricVerdict(
            name="Turnover",
            baseline_value=base,
            experiment_value=exp,
            threshold_desc=desc,
            passed=passed,
            detail=(
                f"Turnover 关={base:.4f}/yr 开={exp:.4f}/yr 门槛≤{threshold:.4f} "
                f"→ {'通过' if passed else '否决'}"
            ),
        )

    # ── 辅助 ──

    @staticmethod
    def _ensure_gate_off(cfg: BacktestConfig) -> BacktestConfig:
        """强制 strict_overfitting_gate=False，避免过拟合门控中断 C1 对比。

        C1 焦点是 Shrinkage 节流效果对比，过拟合检测另有 A2/E1 验证项负责。
        """
        if getattr(cfg, "strict_overfitting_gate", False):
            # frozen dataclass → 用 dataclasses.replace 生成新实例
            from dataclasses import replace
            return replace(cfg, strict_overfitting_gate=False)
        return cfg

    @staticmethod
    def _build_summary(
        baseline: BacktestResult,
        experiment: BacktestResult,
        base_calmar: float,
        exp_calmar: float,
        base_turnover: float,
        exp_turnover: float,
        passed: bool,
        veto_reason: Optional[str],
    ) -> str:
        verdict = "通过" if passed else "一票否决"
        lines = [
            f"C1 Shrinkage 开/关对比——{verdict}",
            f"  Sharpe   关={baseline.sharpe_ratio:.4f}  开={experiment.sharpe_ratio:.4f}",
            f"  MaxDD    关={baseline.max_drawdown:.4f}  开={experiment.max_drawdown:.4f}",
            f"  Calmar   关={base_calmar:.4f}  开={exp_calmar:.4f}",
            f"  Turnover 关={base_turnover:.4f}/yr  开={exp_turnover:.4f}/yr",
        ]
        if not passed and veto_reason:
            lines.append(f"  否决原因: {veto_reason}")
        return "\n".join(lines)


# ──────────────────────────────────────────────────────────────────────────────
# 指标计算工具
# ──────────────────────────────────────────────────────────────────────────────


def _compute_calmar(annual_return: float, max_drawdown: float) -> float:
    """Calmar = annual_return / |max_drawdown|。

    MaxDD 存负值（如 -0.142），取绝对值。无回撤（|MaxDD|≈0）时：
      - annual_return ≥ 0 → 返回 +inf（无回撤的正收益，Calmar 极佳）
      - annual_return < 0 → 返回 -inf（无回撤却亏损，异常）
    """
    abs_dd = abs(max_drawdown)
    if abs_dd < 1e-12:
        return float("inf") if annual_return >= 0 else float("-inf")
    return float(annual_return) / abs_dd


def _compute_turnover(
    portfolio: Optional[Portfolio], trading_days_per_year: int
) -> float:
    """年化单向换手率 = Σ(|qty × price|) / (avg_nav × num_years)。

    Args:
        portfolio: 回测引擎的 last_portfolio（含 trades_log + nav_series）。
        trading_days_per_year: 年化交易日数（默认 252）。

    Returns:
        年化换手率（次/年）。portfolio=None 或无交易 → 0.0。
    """
    if portfolio is None:
        return 0.0
    trades_log = portfolio.trades_log
    if not trades_log:
        return 0.0

    total_traded_value = 0.0
    for t in trades_log:
        qty = float(t.get("quantity", 0.0) or 0.0)
        price = float(t.get("price", 0.0) or 0.0)
        total_traded_value += abs(qty * price)

    nav_series = portfolio.nav_series
    if nav_series is None or len(nav_series) == 0:
        return 0.0
    avg_nav = float(nav_series.mean())
    if avg_nav <= 0:
        return 0.0
    # num_years = 交易日数 / 年化天数；至少 1 个交易日避免除零
    num_years = max(len(nav_series) - 1, 1) / float(trading_days_per_year)
    if num_years <= 0:
        return 0.0
    return total_traded_value / (avg_nav * num_years)


__all__ = [
    "C1Config",
    "C1MetricVerdict",
    "C1ComparisonResult",
    "C1ShrinkageComparator",
    "C1ShrinkageComparatorError",
]
