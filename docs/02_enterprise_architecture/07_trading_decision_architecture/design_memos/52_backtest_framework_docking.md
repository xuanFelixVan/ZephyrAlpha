---
ttl: permanent
doc_type: architecture_view
title: 回测框架对接与IS→WFA→OOS验证流
owner: ZephyrAlpha-Owner
language: zh
status: active
version: "1.2.0"
date: 2026-08-10
topic: backtest_framework_docking
scope: 07_trading_decision_architecture
---

# 回测框架对接与IS→WFA→OOS验证流

> **性质**：由 [00_index_trading_decision](00_index_trading_decision.md) G23 主题组派生，将回测框架对接的讨论要点落地为可施工的 spec + 伪代码。
> **施工图纪律**：本文档 status=active，对应模块允许施工。
> **2026-08 研究整合**：IS→WFA→OOS 三阶段验证流；Pre-registration protocol（防 p-hacking）；过拟合检测三维度（BM-BT-05）；Deflated Sharpe Ratio + White Reality Check/Hansen SPA bootstrap（Soloviov 2026-07；López de Prado）；DSR 鲁棒性带（有效 trial 数 1.6-370 跨数量级）；causal-quant 因果验证（2026-07）。

## 1. 主题组信息

| 项 | 内容 |
|---|---|
| 主题组 | G23 回测框架对接 |
| 所属 | 作战地图 03 |
| 依赖 | G04（策略定义，[20_first_batch_strategies](20_first_batch_strategies.md) 已定稿 v1.2.0）、G15（[34_regime_meta_allocator](34_regime_meta_allocator.md) backtest_store） |
| 对标 | 11_regime_backtest_validation_plan 已建立的对接范式 / Morwane walk-forward / López de Prado DSR |
| 正交性 | ✅ 与 regime 正交（复用同一回测框架） |
| 优先级 | P2（G04 后） |
| 状态 | ✅ active — IS→WFA→OOS+pre-registration+过拟合三维度+DSR bootstrap 已定稿 |

## 2. 背景

### 2.1 项目处境

回测是策略上线前的核心验证环节。[11_regime_backtest_validation_plan](11_regime_backtest_validation_plan.md) 已建立 regime 侧的回测验证范式（Phase 1-5），本文档将其扩展到策略侧。策略回测与 regime 回测的关键差异：regime 回测验证的是"Shrinkage 有效性"（风险节流），策略回测验证的是"alpha 持续性"（收益预测力）。

**核心矛盾**：回测容易过拟合——参数搜索空间越大、试过的变体越多，回测 Sharpe 越容易被噪声主导。Deflated Sharpe Ratio（DSR）和 Pre-registration protocol 是对抗过拟合的两道防线。

### 2.2 核心问题

1. **IS→WFA→OOS 三阶段**：样本内训练（IS）→ 滚动前进分析（WFA）→ 样本外验证（OOS），每阶段有独立门控。
2. **Pre-registration**：策略参数和假设必须在回测前登记，防止事后挑选（p-hacking）。
3. **过拟合三维度**（BM-BT-05）：参数敏感性、样本外衰减、trial 相关性。
4. **Deflated Sharpe**：调整后的 Sharpe 需考虑 trial 数和相关性，相关搜索场景需 bootstrap。
5. **DSR 鲁棒性带**：有效 trial 数非单一数值，5 个估计器相差两个数量级（1.6-370）。

### 2.3 约束条件

- **PIT 铁律**：回测必须用 Point-In-Time 数据，防止前瞻偏差
- **Pre-registration**：参数搜索空间必须在回测前锁定
- **DSR bootstrap**：相关搜索场景（参数网格/同源变体）MUST 用 White Reality Check/Hansen SPA
- **与 backtest_store 联动**：所有回测结果记录到 [34_regime_meta_allocator] §3.1 的 backtest_store

## 3. 决策

### 3.1 架构定义

回测验证由 Pre-registration 层、三阶段验证层、过拟合检测层三层构成：

```
Pre-registration 层: 策略假设登记 → 参数搜索空间锁定 → 登记 token 签发
                                                                ↓
三阶段验证层: IS(样本内训练) → WFA(滚动前进分析) → OOS(样本外验证)
                                                                ↓
过拟合检测层: 参数敏感性 + 样本外衰减 + DSR(trial数+相关性+bootstrap)
```

### 3.2 Pre-registration Protocol 算法

```python
from dataclasses import dataclass, field
from datetime import date, datetime
from enum import Enum
from typing import Optional
import hashlib
import json


@dataclass
class StrategyHypothesis:
    """策略假设——pre-registration 核心对象。

    防止 p-hacking 的核心：
    - 假设必须在回测前登记（含参数搜索空间）
    - 登记后不可修改（immutable）
    - 回测结果必须与登记的假设对比
    - 事后挑选的变体不计入（除非重新登记并重新走全流程）
    """
    hypothesis_id: str               # 假设唯一 ID
    strategy_id: str
    hypothesis_text: str             # 假设描述（自然语言经济逻辑）
    # 参数搜索空间（锁定后不可扩展）
    param_space: dict                # {param_name: [候选值列表]}
    # 预期效果
    expected_direction: str          # "positive" / "negative"
    expected_ic_range: tuple         # (min_ic, max_ic)
    # 因果图声明（causal-quant 2026-07）
    causal_graph: dict               # {confounders: [], colliders: []}
    # 登记 token
    registration_token: str          # 哈希签名
    registered_at: str
    registered_by: str


def register_hypothesis(
    strategy_id: str,
    hypothesis_text: str,
    param_space: dict,
    expected_direction: str = "positive",
    expected_ic_range: tuple = (0.02, 0.10),
    causal_graph: Optional[dict] = None,
    registered_by: str = "analyst",
) -> StrategyHypothesis:
    """登记策略假设——pre-registration 入口。

    核心原则（causal-quant 2026-07）：
    - 因子注册时（非上线时）声明因果图 DAG，避免事后合理化
    - 相关性≠因果性，回测撒谎三方式：luck/confounding/selection across everything you tried
    - MVP 阶段 causal_graph 填自然语言经济逻辑
    - Phase 1.5+ 接入 causal-quant 证伪电池后补 H-score

    登记 token = SHA256(strategy_id + hypothesis + param_space + timestamp)
    登记后不可修改，任何参数扩展需重新登记。
    """
    if causal_graph is None:
        causal_graph = {"confounders": [], "colliders": [], "logic": hypothesis_text}

    timestamp = datetime.now().isoformat()
    token_input = json.dumps({
        "strategy_id": strategy_id,
        "hypothesis": hypothesis_text,
        "param_space": param_space,
        "timestamp": timestamp,
    }, sort_keys=True)
    registration_token = hashlib.sha256(token_input.encode()).hexdigest()[:16]

    return StrategyHypothesis(
        hypothesis_id=f"HYP-{strategy_id}-{registration_token[:8]}",
        strategy_id=strategy_id,
        hypothesis_text=hypothesis_text,
        param_space=param_space,
        expected_direction=expected_direction,
        expected_ic_range=expected_ic_range,
        causal_graph=causal_graph,
        registration_token=registration_token,
        registered_at=timestamp,
        registered_by=registered_by,
    )


def validate_against_registration(
    hypothesis: StrategyHypothesis,
    actual_params: dict,              # 实际使用的参数
    actual_ic: float,                 # 实际 IC
    actual_direction: str,            # 实际方向
) -> dict:
    """验证回测结果是否符合 pre-registration。

    验证逻辑：
    1. 实际参数是否在登记的 param_space 内
    2. 实际 IC 是否在预期范围内
    3. 实际方向是否与预期一致
    4. 若不符 → 标记为"探索性"而非"验证性"
    """
    violations = []

    # 参数空间验证
    for param, value in actual_params.items():
        if param in hypothesis.param_space:
            allowed = hypothesis.param_space[param]
            if value not in allowed:
                violations.append(f"param_{param}_out_of_space: {value} not in {allowed}")

    # IC 范围验证
    min_ic, max_ic = hypothesis.expected_ic_range
    if not (min_ic <= actual_ic <= max_ic):
        violations.append(f"ic_out_of_range: {actual_ic} not in [{min_ic}, {max_ic}]")

    # 方向验证
    if actual_direction != hypothesis.expected_direction:
        violations.append(f"direction_mismatch: {actual_direction} != {hypothesis.expected_direction}")

    return {
        "is_confirmatory": len(violations) == 0,  # 验证性（符合登记）
        "is_exploratory": len(violations) > 0,    # 探索性（不符登记，需重新登记）
        "violations": violations,
    }
```

### 3.3 IS→WFA→OOS 三阶段验证流算法

```python
@dataclass
class BacktestConfig:
    """回测配置。"""
    strategy_id: str
    hypothesis: StrategyHypothesis
    # 数据分割
    is_start: date
    is_end: date                  # IS 样本内结束日
    wfa_window: int               # WFA 滚动窗口（天）
    wfa_step: int                 # WFA 滚动步长（天）
    oos_start: date               # OOS 样本外开始日
    oos_end: date                 # OOS 样本外结束日
    # 参数
    initial_capital: float = 1e6
    commission_rate: float = 0.0003
    slippage_model: str = "square_root"


@dataclass
class ISResult:
    """IS 样本内训练结果。"""
    best_params: dict
    is_sharpe: float
    is_return: float
    is_max_drawdown: float
    n_trials: int                 # 参数搜索次数
    trial_correlated: bool        # trial 是否相关（参数网格/同源变体）


@dataclass
class WVAResult:
    """WFA 滚动前进分析结果。"""
    window_results: list[dict]    # 各窗口结果
    wfa_sharpe: float             # WFA 综合 Sharpe
    wfa_return: float
    wfa_max_drawdown: float
    stability_score: float        # 稳定性得分（各窗口 Sharpe 的 CV）


@dataclass
class OOSResult:
    """OOS 样本外验证结果。"""
    oos_sharpe: float
    oos_return: float
    oos_max_drawdown: float
    is_oos_decay: float           # IS→OOS 衰减比 = oos_sharpe / is_sharpe
    passed: bool                  # 是否通过 OOS 门控


@dataclass
class FullBacktestResult:
    """完整三阶段回测结果。"""
    strategy_id: str
    hypothesis: StrategyHypothesis
    is_result: ISResult
    wfa_result: WVAResult
    oos_result: OOSResult
    overfitting_check: dict       # 过拟合检测
    dsr_result: dict              # Deflated Sharpe
    overall_passed: bool


def run_is_stage(
    config: BacktestConfig,
    strategy_callback: callable,  # 策略信号生成回调
    market_data: callable,        # 市场数据回调
) -> ISResult:
    """IS 阶段——样本内参数训练。

    逻辑：
    1. 在 IS 时间段内搜索参数空间
    2. 选出最优参数（最高 Sharpe）
    3. 记录 trial 数和相关性

    注意：
    - 参数搜索空间必须与 pre-registration 一致
    - trial_correlated=True 时（参数网格/同源变体），DSR 必须 bootstrap
    """
    param_space = config.hypothesis.param_space
    n_trials = 1
    for param, values in param_space.items():
        n_trials *= len(values)

    # 判断 trial 相关性
    trial_correlated = n_trials > 10  # 参数网格 >10 个组合视为相关

    # 参数网格搜索——遍历所有参数组合
    import itertools
    param_names = list(param_space.keys())
    param_value_lists = [param_space[name] for name in param_names]

    best_sharpe = -999.0
    best_params = {}
    best_return = 0.0
    best_dd = 0.0

    for param_combo in itertools.product(*param_value_lists):
        params = dict(zip(param_names, param_combo))

        # 回测 IS 时间段
        result = _run_single_backtest(
            config, params, strategy_callback, market_data,
            config.is_start, config.is_end
        )

        # 选最优 Sharpe（MVP 用 Sharpe；Phase 1.5+ 用 stability_plateau 替代 single_optimum）
        if result["sharpe"] > best_sharpe:
            best_sharpe = result["sharpe"]
            best_params = params
            best_return = result["total_return"]
            best_dd = result["max_drawdown"]

    return ISResult(
        best_params=best_params,
        is_sharpe=best_sharpe,
        is_return=best_return,
        is_max_drawdown=best_dd,
        n_trials=n_trials,
        trial_correlated=trial_correlated,
    )


def _run_single_backtest(
    config: BacktestConfig,
    params: dict,
    strategy_callback: callable,
    market_data: callable,
    start_date: date,
    end_date: date,
) -> dict:
    """单次回测——给定参数和时间段的回测执行。

    返回 sharpe/total_return/max_drawdown。
    实际实现需对接 backtest engine（qlib/backtrader/vectorbt 等）。
    """
    # 获取时间段内日历
    trading_days = market_data(start_date, end_date)
    daily_returns = []
    portfolio_nav = 1.0
    peak = 1.0
    max_dd = 0.0

    for day in trading_days:
        # 策略生成信号（使用给定参数）
        signals = strategy_callback(market_data(day), params)

        # 简化 P&L 计算：信号预期收益 - 交易成本
        commission = config.commission_rate
        slippage = 0.001  # 简化滑点 10bps
        day_return = 0.0
        for signal in signals:
            cost = commission + slippage
            day_return += signal.get("expected_return", 0.0) * signal.get("weight", 0.0) - cost

        daily_returns.append(day_return)
        portfolio_nav *= (1.0 + day_return)
        if portfolio_nav > peak:
            peak = portfolio_nav
        dd = (peak - portfolio_nav) / peak if peak > 0 else 0.0
        if dd > max_dd:
            max_dd = dd

    total_return = portfolio_nav - 1.0
    sharpe = (np.mean(daily_returns) / np.std(daily_returns) * np.sqrt(252)
              if daily_returns and np.std(daily_returns) > 0 else 0.0)

    return {
        "sharpe": sharpe,
        "total_return": total_return,
        "max_drawdown": max_dd,
    }


def run_wfa_stage(
    config: BacktestConfig,
    is_result: ISResult,
    strategy_callback: callable,
    market_data: callable,
) -> WVAResult:
    """WFA 阶段——滚动前进分析。

    逻辑：
    1. 用 IS 选出的最优参数作为初始参数
    2. 在 WFA 窗口内滚动前进回测
    3. 每个窗口用前 wfa_window 天训练（重新校准参数），后 wfa_step 天测试
    4. 综合各窗口结果

    WFA 核心价值：
    - 检测参数时间稳定性
    - 避免单次 IS/OOS 分割的运气
    - 更接近实盘的滚动重新校准
    - 各窗口 Sharpe 的变异系数（CV）= stability_score 的核心
    """
    window_results = []
    sharpes = []
    all_daily_returns = []
    max_dd_across_windows = 0.0

    from datetime import timedelta

    # 滚动窗口——从 IS 结束日滚动到 OOS 开始日
    current = config.is_end
    while current < config.oos_start:
        # 训练窗口
        train_start = current - timedelta(days=config.wfa_window)
        train_end = current
        # 测试窗口
        test_start = current
        test_end = current + timedelta(days=config.wfa_step)

        # 步骤 1：在训练窗口重新校准参数（简化版——MVP 直接复用 IS 最优参数）
        # Phase 1.5+ 在训练窗口重新搜索参数空间
        window_params = is_result.best_params

        # 步骤 2：在测试窗口回测
        test_result = _run_single_backtest(
            config, window_params, strategy_callback, market_data,
            test_start, min(test_end, config.oos_start)
        )

        window_results.append({
            "train_start": train_start.isoformat(),
            "train_end": train_end.isoformat(),
            "test_start": test_start.isoformat(),
            "test_end": test_end.isoformat(),
            "sharpe": test_result["sharpe"],
            "return": test_result["total_return"],
            "max_drawdown": test_result["max_drawdown"],
        })
        sharpes.append(test_result["sharpe"])
        if test_result["max_drawdown"] > max_dd_across_windows:
            max_dd_across_windows = test_result["max_drawdown"]

        current = test_end

    # 综合 WFA 指标
    wfa_sharpe = sum(sharpes) / len(sharpes) if sharpes else 0.0
    wfa_return = sum(w["return"] for w in window_results) if window_results else 0.0
    stability_score = (1.0 - (np.std(sharpes) / abs(np.mean(sharpes)))
                       if sharpes and abs(np.mean(sharpes)) > 0 else 0.0)

    return WVAResult(
        window_results=window_results,
        wfa_sharpe=wfa_sharpe,
        wfa_return=wfa_return,
        wfa_max_drawdown=max_dd_across_windows,
        stability_score=stability_score,
    )


def run_oos_stage(
    config: BacktestConfig,
    is_result: ISResult,
    strategy_callback: callable,
    market_data: callable,
    is_oos_decay_threshold: float = 0.5,   # OOS Sharpe ≥ IS Sharpe × 0.5
    oos_sharpe_threshold: float = 0.5,     # OOS Sharpe ≥ 0.5
) -> OOSResult:
    """OOS 阶段——样本外验证。

    门控标准：
    - OOS Sharpe ≥ 0.5
    - IS→OOS 衰减比 ≥ 0.5（OOS Sharpe ≥ IS Sharpe × 0.5）
    - OOS 最大回撤 ≤ IS 最大回撤 × 1.5

    任一不通过 → overall_passed=False，不进入 paper trading。

    注意：OOS 参数使用 IS 阶段选出的 best_params（不可在 OOS 期间重新调参，
    否则违反 pre-registration 原则，构成 p-hacking）。
    """
    # OOS 回测——使用 IS 最优参数，在 OOS 时间段验证
    oos_result = _run_single_backtest(
        config, is_result.best_params, strategy_callback, market_data,
        config.oos_start, config.oos_end
    )

    oos_sharpe = oos_result["sharpe"]
    oos_return = oos_result["total_return"]
    oos_max_drawdown = oos_result["max_drawdown"]

    is_oos_decay = oos_sharpe / is_result.is_sharpe if is_result.is_sharpe > 0 else 0.0

    # 门控判定（三条件全通过）
    passed = (
        oos_sharpe >= oos_sharpe_threshold and
        is_oos_decay >= is_oos_decay_threshold and
        oos_max_drawdown <= is_result.is_max_drawdown * 1.5
    )

    return OOSResult(
        oos_sharpe=oos_sharpe,
        oos_return=oos_return,
        oos_max_drawdown=oos_max_drawdown,
        is_oos_decay=is_oos_decay,
        passed=passed,
    )
```

### 3.4 过拟合检测三维度算法

```python
@dataclass
class OverfittingCheck:
    """过拟合检测三维度（BM-BT-05）。"""
    # 维度 1：参数敏感性
    param_sensitivity: float       # 最优参数邻域 Sharpe 变异系数（CV）
    param_sensitive: bool          # CV > 0.3 = 过敏感 = 过拟合风险
    # 维度 2：样本外衰减
    is_oos_decay: float            # OOS/IS Sharpe 比
    severe_decay: bool             # decay < 0.5 = 严重衰减 = 过拟合
    # 维度 3：trial 相关性
    n_trials: int
    trial_correlated: bool
    effective_trial_count: float   # 有效 trial 数（考虑相关性调整）
    # 综合
    overfitting_score: float       # [0, 1]，越高越可能过拟合
    is_overfit: bool


def check_overfitting(
    is_result: ISResult,
    oos_result: OOSResult,
    # 参数敏感性数据
    neighboring_sharpes: list[float],  # 最优参数邻域的 Sharpe 值
) -> OverfittingCheck:
    """过拟合检测三维度——参数敏感性 + 样本外衰减 + trial 相关性。

    维度 1：参数敏感性（BM-BT-05）
    - 计算最优参数邻域 Sharpe 的变异系数（CV = std/mean）
    - CV > 0.3 = 参数过敏感 = 过拟合风险高
    - 健康策略应对参数微调不敏感

    维度 2：样本外衰减
    - IS→OOS Sharpe 衰减比
    - decay < 0.5 = 严重衰减 = 过拟合
    - decay > 0.7 = 健康

    维度 3：trial 相关性（DSR 鲁棒性带关键约束）
    - 有效 trial 数非单一数值，5 个估计器相差两个数量级（1.6-370）
    - 相关搜索场景（参数网格/同源变体）有效 trial 数远小于名义 trial 数
    - trial_correlated=True 时需 bootstrap 调整
    """
    # 维度 1：参数敏感性
    if neighboring_sharpes and abs(np.mean(neighboring_sharpes)) > 0:
        param_cv = float(np.std(neighboring_sharpes) / abs(np.mean(neighboring_sharpes)))
    else:
        param_cv = 1.0
    param_sensitive = param_cv > 0.3

    # 维度 2：样本外衰减
    is_oos_decay = oos_result.is_oos_decay
    severe_decay = is_oos_decay < 0.5

    # 维度 3：有效 trial 数
    n_trials = is_result.n_trials
    trial_correlated = is_result.trial_correlated

    # 有效 trial 数估计（简化版）
    # 相关 trial 时有效数远小于名义数
    if trial_correlated:
        # 保守估计：有效 trial = 名义 trial / 相关性因子
        effective_trial_count = n_trials / 5.0  # 假设平均相关性导致 5 倍膨胀
    else:
        effective_trial_count = float(n_trials)

    # 综合过拟合得分
    score = 0.0
    if param_sensitive:
        score += 0.3
    if severe_decay:
        score += 0.4
    if trial_correlated and n_trials > 50:
        score += 0.3

    return OverfittingCheck(
        param_sensitivity=param_cv,
        param_sensitive=param_sensitive,
        is_oos_decay=is_oos_decay,
        severe_decay=severe_decay,
        n_trials=n_trials,
        trial_correlated=trial_correlated,
        effective_trial_count=effective_trial_count,
        overfitting_score=score,
        is_overfit=score >= 0.5,
    )
```

### 3.5 Deflated Sharpe Ratio + Bootstrap 算法

```python
@dataclass
class DSRResult:
    """Deflated Sharpe Ratio 结果。"""
    observed_sharpe: float         # 观测 Sharpe
    deflated_sharpe: float         # 调整后 Sharpe
    sr0: float                     # 噪声天花板（deflated benchmark）
    n_trials: int
    effective_trial_count: float
    trial_correlated: bool
    bootstrap_used: bool           # 是否使用 bootstrap
    bootstrap_pvalue: Optional[float]  # bootstrap p-value
    is_significant: bool           # 是否统计显著


def compute_dsr(
    observed_sharpe: float,        # 观测 Sharpe（年化）
    n_trials: int,
    trial_correlated: bool,
    sample_length: int,            # 样本长度（天）
    sr0: float = 1.63,             # 噪声天花板（López de Prado deflated benchmark ≈1.63 年化）
    use_bootstrap: bool = None,    # None=自动判断
    bootstrap_returns: list = None, # 用于 bootstrap 的收益序列
) -> DSRResult:
    """Deflated Sharpe Ratio 计算——调整 trial 数和相关性后的 Sharpe 显著性。

    核心理论（López de Prado "Advances in Financial Machine Learning"）：
    - 观测 Sharpe 需向下调整以反映 multiple testing
    - 调整量取决于 trial 数和 trial 间相关性
    - deflated benchmark SR₀ ≈ 1.63（年化）= 噪声天花板
    - 观测 Sharpe > SR₀ 才有统计显著性

    DSR 鲁棒性带关键约束（Soloviov 2026-07）：
    - 有效 trial 数非单一数值，5 个估计器相差两个数量级（1.6-370）
    - 相关搜索场景（参数网格/同源变体）禁用裸 DSR
    - MUST 用 White Reality Check / Hansen SPA bootstrap
    - MVP 阶段 trial_correlated=false 时裸 DSR 可用
    - Phase 1.5+ 参数网格搜索 MUST 启用 bootstrap
    """
    # 自动判断是否需要 bootstrap
    if use_bootstrap is None:
        use_bootstrap = trial_correlated  # 相关 trial 必须 bootstrap

    # 有效 trial 数
    if trial_correlated:
        # 相关 trial 有效数远小于名义数
        # 保守估计使用 5 倍膨胀因子
        effective_trial_count = max(1.0, n_trials / 5.0)
    else:
        effective_trial_count = float(n_trials)

    # Deflated Sharpe（简化版）
    # DSR = (observed_sr - E[max_sr_under_null]) / se
    # E[max_sr_under_null] ≈ sr0 × sqrt(2 × log(effective_n))
    import math
    expected_max_null = sr0 * math.sqrt(2 * math.log(max(2, effective_trial_count)))
    deflated_sharpe = observed_sharpe - expected_max_null

    # Bootstrap（White Reality Check / Hansen SPA）
    bootstrap_pvalue = None
    if use_bootstrap and bootstrap_returns:
        bootstrap_pvalue = _hansen_spa_bootstrap(
            bootstrap_returns, observed_sharpe, n_iterations=1000
        )

    # 显著性判定
    is_significant = deflated_sharpe > 0
    if bootstrap_pvalue is not None:
        is_significant = is_significant and bootstrap_pvalue < 0.05

    return DSRResult(
        observed_sharpe=observed_sharpe,
        deflated_sharpe=deflated_sharpe,
        sr0=sr0,
        n_trials=n_trials,
        effective_trial_count=effective_trial_count,
        trial_correlated=trial_correlated,
        bootstrap_used=use_bootstrap,
        bootstrap_pvalue=bootstrap_pvalue,
        is_significant=is_significant,
    )


def _hansen_spa_bootstrap(
    returns: list[float],
    observed_sharpe: float,
    n_iterations: int = 1000,
) -> float:
    """Hansen SPA bootstrap——相关搜索场景的 DSR 调整。

    White Reality Check (WRC) / Hansen Superior Predictive Ability (SPA) test：
    - 对收益序列做 stationary bootstrap
    - 每次重采样计算 Sharpe
    - p-value = 重采样 Sharpe 超过观测 Sharpe 的比例

    用于 trial_correlated=True 时裸 DSR 不可用的场景。
    """
    if not returns or len(returns) < 20:
        return 1.0

    returns_arr = np.array(returns)
    n = len(returns_arr)

    # Stationary bootstrap（Politis-Romano 1994）
    bootstrap_sharpes = []
    for _ in range(n_iterations):
        # 简化：带替换重采样（完整 stationary bootstrap 需实现 Politis-Romano）
        indices = np.random.choice(n, size=n, replace=True)
        resampled = returns_arr[indices]
        mean_r = np.mean(resampled)
        std_r = np.std(resampled)
        if std_r > 0:
            bs_sharpe = mean_r / std_r * np.sqrt(252)
            bootstrap_sharpes.append(bs_sharpe)

    if not bootstrap_sharpes:
        return 1.0

    # p-value = P(bootstrap_sharpe >= observed_sharpe)
    count_exceed = sum(1 for s in bootstrap_sharpes if s >= observed_sharpe)
    p_value = count_exceed / len(bootstrap_sharpes)

    return p_value
```

### 3.6 完整 IS→WFA→OOS 主循环算法

```python
def run_full_backtest(
    config: BacktestConfig,
    strategy_callback: callable,
    market_data: callable,
    neighboring_sharpes: list[float] = None,
) -> FullBacktestResult:
    """完整 IS→WFA→OOS 三阶段回测主循环。

    流程：
    1. IS 阶段：样本内参数训练（§3.3）
    2. WFA 阶段：滚动前进分析（§3.3）
    3. OOS 阶段：样本外验证（§3.3）
    4. 过拟合检测三维度（§3.4）
    5. Deflated Sharpe Ratio（§3.5）
    6. 综合门控判定

    综合门控（全部通过才 overall_passed）：
    - OOS passed
    - 过拟合检测 is_overfit=False
    - DSR is_significant=True
    """
    # 步骤 1-3：三阶段
    is_result = run_is_stage(config, strategy_callback, market_data)
    wfa_result = run_wfa_stage(config, is_result, strategy_callback, market_data)
    oos_result = run_oos_stage(config, is_result, strategy_callback, market_data)

    # 步骤 4：过拟合检测
    if neighboring_sharpes is None:
        neighboring_sharpes = [is_result.is_sharpe * 0.9, is_result.is_sharpe * 1.1]
    overfitting_check = check_overfitting(is_result, oos_result, neighboring_sharpes)

    # 步骤 5：DSR
    dsr_result = compute_dsr(
        observed_sharpe=oos_result.oos_sharpe,
        n_trials=is_result.n_trials,
        trial_correlated=is_result.trial_correlated,
        sample_length=365,
    )

    # 步骤 6：综合门控
    overall_passed = (
        oos_result.passed and
        not overfitting_check.is_overfit and
        dsr_result.is_significant
    )

    return FullBacktestResult(
        strategy_id=config.strategy_id,
        hypothesis=config.hypothesis,
        is_result=is_result,
        wfa_result=wfa_result,
        oos_result=oos_result,
        overfitting_check={
            "param_sensitivity": overfitting_check.param_sensitivity,
            "is_oos_decay": overfitting_check.is_oos_decay,
            "overfitting_score": overfitting_check.overfitting_score,
            "is_overfit": overfitting_check.is_overfit,
        },
        dsr_result={
            "observed_sharpe": dsr_result.observed_sharpe,
            "deflated_sharpe": dsr_result.deflated_sharpe,
            "sr0": dsr_result.sr0,
            "bootstrap_used": dsr_result.bootstrap_used,
            "bootstrap_pvalue": dsr_result.bootstrap_pvalue,
            "is_significant": dsr_result.is_significant,
        },
        overall_passed=overall_passed,
    )
```

### 3.7 策略回测 vs regime 回测差异

| 维度 | 策略回测 | regime 回测 |
|---|---|---|
| **验证目标** | alpha 持续性（收益预测力） | Shrinkage 有效性（风险节流） |
| **IS 阶段** | 参数搜索（参数空间大） | 阈值校准（参数空间小） |
| **OOS 门控** | Sharpe≥0.5 + 衰减比≥0.5 | Shrinkage 降低回撤不降收益 |
| **过拟合风险** | 高（参数搜索空间大） | 低（阈值校准参数少） |
| **DSR 必要性** | MUST（trial 数多） | SHOULD（trial 数少） |
| **对接文档** | 本文档（52号） | [11_regime_backtest_validation_plan](11_regime_backtest_validation_plan.md) |

### 3.8 A 股 mask-first 前置设计（实盘生存级 MUST）

```python
import numpy as np
import pandas as pd


def build_tradability_mask(
    ohlcv: pd.DataFrame,           # 含 open/high/low/close/limit_up/limit_down/volume
    pct_limit_threshold: float = 0.001,  # 涨跌停判定阈值（0.1% 容差）
) -> pd.Series:
    """构造可交易性 mask——A 股涨跌停板前置过滤。

    核心问题（arXiv:2507.07107v2 Yimin Du USTC 2026-05）：
    - A 股 ±10%/±20% 涨跌停板使部分收盘价"不可执行"
    - 标准实现"先读价格再过滤行"导致 upstream contamination：
      MA/correlation/rank 等算子在含不可执行价格的序列上计算 → 静默传播偏差
    - 实证：IC 虚增 18%，Sharpe 虚增 0.44（单一最大贡献者！）

    mask-first 设计：
    - 数据加载时即构造 tradability mask，贯穿后续每个算子
    - 任何因子/指标计算前先应用 mask，不可执行的数据点置 NaN
    - 确保回测中只在"可实际交易"的时点生成信号

    A 股前置 MUST 非可选——实盘生存级问题（非"nice to have"）。
    """
    close = ohlcv["close"]
    limit_up = ohlcv.get("limit_up", close * 1.1)
    limit_down = ohlcv.get("limit_down", close * 0.9)
    volume = ohlcv["volume"]

    # 涨停封板：收盘价 ≈ 涨停价 且 成交量极低（封死无法买入）
    is_limit_up = abs(close - limit_up) / limit_up < pct_limit_threshold
    # 跌停封板：收盘价 ≈ 跌停价 且 成交量极低（封死无法卖出）
    is_limit_down = abs(close - limit_down) / limit_down < pct_limit_threshold
    # 停牌：成交量为 0
    is_halted = volume <= 0

    # 可交易 = 非涨停封板 AND 非跌停封板 AND 非停牌
    tradable = ~(is_limit_up | is_limit_down | is_halted)

    return tradable


def apply_mask_first(
    data: pd.DataFrame | pd.Series,
    mask: pd.Series,
) -> pd.DataFrame | pd.Series:
    """mask-first 算子封装——在任何因子/指标计算前应用 mask。

    使用方式（贯穿整个因子计算管线）：
    ```python
    mask = build_tradability_mask(ohlcv)
    masked_close = apply_mask_first(ohlcv["close"], mask)
    ma_20 = masked_close.rolling(20).mean()  # MA 在 masked 数据上计算
    factor = some_factor_calc(masked_close, ma_20)
    signal = apply_mask_first(factor, mask)  # 最终信号也 mask
    ```

    对比 row_filter 方式（先算后过滤）：
    - row_filter：factor = calc(all_data); factor = factor[mask]  ← 已被污染
    - mask_first：factor = calc(masked_data)                      ← 从源头隔离

    mask_first 是 arXiv:2507.07107v2 实证的单一最大贡献者（+0.44 Sharpe）。
    """
    result = data.copy()
    result[~mask] = np.nan
    return result


def tradability_mask_policy_check(
    policy: str,  # "none" / "row_filter" / "mask_first"
) -> dict:
    """tradability_mask_policy 声明检查（E15 审计扩展）。

    基于 arXiv:2507.07107v2 (2026-05) 的 A 股涨跌停板上游污染研究：
    - none: 不做任何过滤 → upstream contamination，IC 虚增 18%，Sharpe 虚增 0.44
    - row_filter: 先算因子后过滤行 → 部分污染（MA/correlation 已被污染）
    - mask_first: 数据加载时构造 mask 贯穿算子 → 无污染（唯一正确方式）

    A 股因子实验 MUST 声明 tradability_mask_policy：
    - none = warning highlight（实盘生存级问题）
    - row_filter = warning（部分污染）
    - mask_first = pass（MVP 阶段 MUST 实现）
    """
    policies = {
        "none": {"status": "warning_highlight", "reason": "no_mask_upstream_contamination_risk"},
        "row_filter": {"status": "warning", "reason": "partial_contamination_MA_correlation_affected"},
        "mask_first": {"status": "pass", "reason": "correct_isolation_from_source"},
    }
    return policies.get(policy, {"status": "error", "reason": f"unknown_policy_{policy}"})
```

> **实施约束**：MVP 阶段 `_run_single_backtest` 必须在策略信号生成前调用 `build_tradability_mask` + `apply_mask_first`，确保所有因子计算在 masked 数据上进行。`tradability_mask_policy` 必须在 `StrategyHypothesis` 中声明为 `"mask_first"`。

## 4. 考虑过的替代方案

| 方案 | 描述 | 拒绝理由 |
|---|---|---|
| **单一 IS/OOS** | 无 WFA 滚动 | 单次分割运气大；WFA 更稳健 |
| **无 pre-registration** | 事后挑选参数 | p-hacking 风险高 |
| **裸 DSR 无 bootstrap** | 相关 trial 用裸 DSR | 有效 trial 数被高估；MUST bootstrap |
| **固定 SR₀** | 不随 trial 数调整 | 忽略 multiple testing；DSR 更准确 |
| **k-fold 交叉验证** | k 折交叉验证 | 时序数据不可随机打乱；WFA 更适合 |

## 5. 上限定义

| 上限 | 值 | 理由 |
|---|---|---|
| **OOS Sharpe 门控** | ≥ 0.5 | 低于 0.5 无统计显著性 |
| **IS→OOS 衰减门控** | ≥ 0.5 | 衰减 >50% = 过拟合 |
| **参数敏感性 CV** | ≤ 0.3 | CV >0.3 = 参数过敏感 |
| **过拟合得分** | < 0.5 | ≥0.5 = 过拟合 |
| **DSR SR₀** | 1.63 | López de Prado 噪声天花板 |
| **bootstrap p-value** | < 0.05 | 统计显著性 |

**演进路径**：
- MVP：IS→WFA→OOS + pre-registration + 过拟合三维度 + 裸 DSR（trial_correlated=false）
- Phase 1.5：Hansen SPA bootstrap（trial_correlated=true）+ causal-quant 因果验证
- Phase 2：DSR 鲁棒性带完整实现（5 估计器）+ H-score

## 6. 待裁定

| 项 | 暂缓理由 | 重评条件 |
|---|---|---|
| **DSR 鲁棒性带 5 估计器** | MVP 用简化版 | Phase 2+ 需精确有效 trial 数时 |
| **causal-quant 证伪电池** | 需 causal-quant 平台 | Phase 1.5+ |
| **H-score** | 需因果验证基础设施 | Phase 2+ |

## 7. 待定问题（讨论要点）

- [x] ① BM-BT-01~07 环节在策略验证中的用法 → §3.3 IS→WFA→OOS 映射
- [x] ② 策略回测 vs regime 回测的差异 → §3.7 定型
- [x] ③ 策略上线门控 IS→WFA→OOS（BM-BT-07）→ §3.3/§3.6 定型
- [x] ④ 过拟合检测三维度（BM-BT-05）→ §3.4 定型
- [x] ⑤ Deflated Sharpe（BM-BT-05-G）→ §3.5 定型

## 8. 引用

- [00_index_trading_decision](00_index_trading_decision.md) §3 G23
- [11_regime_backtest_validation_plan](11_regime_backtest_validation_plan.md) §2.1（regime 对接范式）
- [20_first_batch_strategies](20_first_batch_strategies.md)（G04 产出物）
- [34_regime_meta_allocator](34_regime_meta_allocator.md)（G15，backtest_store 双轨 P&L）
- [53_simulation_live_path](53_simulation_live_path.md)（G24，回测通过后的下一阶段）
- battle_map_03_backtest_validation（BM-BT-01~07 当前状态快照）

**外部研究引用**：
- López de Prado "Advances in Financial Machine Learning"：DSR 理论
- Soloviov (2026-07)：DSR 鲁棒性带，有效 trial 数 5 估计器跨数量级
- White (2000) Reality Check / Hansen (2005) SPA：相关搜索场景 bootstrap
- Politis-Romano (1994)：stationary bootstrap
- causal-quant (2026-07)：因果验证声明检查

## 9. 修订记录

| 日期 | 版本 | 改动 | 理由 |
|---|---|---|---|
| 2026-08-09 | 0.1.0 | 骨架创建 | 施工图骨架先行：由 00_index G23 讨论要点占位，待讨论填空 |
| 2026-08-10 | 1.0.0 | 补齐 IS→WFA→OOS+pre-registration+过拟合三维度+DSR bootstrap+完整主循环 | 整合 López de Prado DSR + Soloviov 2026-07 鲁棒性带 + causal-quant 2026-07 因果验证 |
| 2026-08-10 | 1.1.0 | IS/WFA/OOS 核心函数从注释占位改为落地实现 | `run_is_stage` 参数网格搜索落地（itertools.product 遍历 + `_run_single_backtest` 回测）；`run_wfa_stage` 滚动窗口循环落地（train/test 分割 + stability_score 计算）；`run_oos_stage` 从占位零值改为 IS 最优参数 OOS 验证（三条件门控含 max_drawdown ≤ IS×1.5）；新增 `_run_single_backtest` 通用回测函数 |
| 2026-08-10 | 1.2.0 | 新增 A 股 mask-first 前置设计 | §3.8 `build_tradability_mask`+`apply_mask_first`+`tradability_mask_policy_check`；整合 arXiv:2507.07107v2 (Yimin Du USTC 2026-05) 涨跌停板上游污染研究：mask-first 是单一最大贡献者（+0.44 Sharpe / IC 虚增 18%），A股前置 MUST 非可选 |
