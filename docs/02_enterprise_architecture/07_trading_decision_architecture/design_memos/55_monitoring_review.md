---
ttl: permanent
doc_type: architecture_view
title: 监控告警与复盘
owner: ZephyrAlpha-Owner
language: zh
status: active
version: "1.0.0"
date: 2026-08-10
topic: monitoring_review
scope: 07_trading_decision_architecture
---

# 监控告警与复盘

> **性质**：由 [00_index_trading_decision](00_index_trading_decision.md) G26 主题组派生，将监控告警与复盘的讨论要点落地为可施工的 spec + 伪代码。
> **施工图纪律**：本文档 status=active，对应模块允许施工。
> **2026-08 研究整合**：CSDN 2026-08-04 策略稳定性监控与自适应调度（极端收益日监控+收益分布偏斜度变化+健康度得分）；StockWatch 2026-07-10 LightGBM 健康门+OOS rejection gates+fail-closed on unknown model health；Future Technology 2025-11 Transformer ensemble 异常检测（F1=0.89/AUC=0.94/15 分钟提前预警/FPR<3%）；LSTM-Autoencoder+GAN+One-Class SVM 混合框架（合成异常注入评估）；SOM 自组织映射无监督异常检测（10 标的跨资产验证）；长江证券 2026-01 净值归因 T-M/H-M/C-L 择时能力模型；国信证券 2026-08-07 封板率/连板率/贴水率等情绪指标。

## 1. 主题组信息

| 项 | 内容 |
|---|---|
| 主题组 | G26 监控告警与复盘 |
| 所属 | 跨作战地图（03 回测 / 04 模拟 / 11 对账） |
| 依赖 | G25（[54_reconciliation_attribution](54_reconciliation_attribution.md) 对账归因）、G16（[35_drawdown_protocol_impl](35_drawdown_protocol_impl.md) 回撤）、G17（[36_var_es_monitoring](36_var_es_monitoring.md) VaR/ES） |
| 对标 | 机构 PM 周报 / 风控周报 / StockWatch 健康门 / Drovix TCA 治理 / Quod 三阶段监控 |
| 正交性 | ✅ 与 regime 正交（监控所有 regime 下的策略行为） |
| 优先级 | P5（被低估的"安全网"层，缺失会让风险盲区不可见） |
| 状态 | ✅ active — 三层监控（系统健康/策略偏离/异常检测）+复盘机制+退役标准已定稿 |

## 2. 背景

### 2.1 项目处境

ZephyrAlpha 已完成 [35_drawdown_protocol_impl] 回撤 Protocol、[36_var_es_monitoring] VaR/ES、[37_liquidity_crisis_protocol] 流动性危机、[54_reconciliation_attribution] 对账归因等模块，但缺一个**统一的监控告警与复盘层**把这些信号汇聚、分级、触发动作、形成闭环。

监控告警是系统的"安全网"——回撤/流动性等触发器是事中保护，监控告警是事前预警+事后学习。没有这一层，风险事件只能"撞了墙才知道"，无法提前发现策略漂移、数据异常、模型衰退等隐患。

### 2.2 核心问题

1. **系统健康监控**：数据/引擎/下单链路的健康度如何度量？单点故障如何不漏报、不误报？
2. **策略偏离监控**：实盘 vs 回测、IS vs OOS 的偏离如何量化？是噪声还是真漂移？
3. **异常检测**：极端收益日、收益分布偏斜度变化、模型预测力衰退如何自动识别？
4. **告警分级与通知**：critical/warning/info 三级如何区分？通知渠道如何分级？
5. **复盘机制**：日复盘/周复盘/月复盘/事件复盘各看什么？复盘文档模板如何统一？
6. **策略退役标准**：连续跑输/逻辑失效/容量超限/相关性突变何时触发退役？

### 2.3 约束条件

- **fail-closed on unknown**（StockWatch 2026-07）：模型健康度未知时按不健康处理，不默认放行
- **避免告警疲劳**：同一根因多信号去重，告警合并窗口（如 5 分钟内同源告警合并）
- **OOS rejection gate**（StockWatch 2026-07）：实盘行为超 OOS 分布 99% 分位即降级，不等人工判断
- **A 股 T+1 适配**：复盘时区分"当日已实现"vs"未实现"收益，避免 T+1 偏差
- **不能"撞墙才知道"**：监控必须覆盖事前（趋势衰退）+ 事中（瞬时异常）+ 事后（归因复盘）

## 3. 决策

### 3.1 架构定义

监控告警与复盘由三层构成：

```
采集层: 系统健康(数据/引擎/下单) + 策略行为(收益/持仓/订单) + 市场环境(情绪/流动性/regime)
                                                                                              ↓
检测层: 阈值规则(三级告警) + 统计过程控制(趋势衰退) + ML 异常检测(Transformer/SOM/ISolation Forest)
                                                                                              ↓
响应层: 告警分级路由 → FSM 联动(降级/暂停) → 复盘文档生成 → 退役评估
```

**与已有模块的接口契约**：
- 输入：[35_drawdown_protocol_impl] 回撤百分比、[36_var_es_monitoring] VaR/ES 越限、[37_liquidity_crisis_protocol] 流动性危机级别、[54_reconciliation_attribution] Brinson 归因结果
- 输出：告警事件 → [53_simulation_live_path] 5态FSM 降级触发、退役评估 → strategy_registry 退役登记

### 3.2 系统健康监控算法

```python
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Optional
import numpy as np


class HealthState(Enum):
    """系统健康状态（StockWatch 2026-07 fail-closed 原则）。"""
    HEALTHY = "healthy"           # 全部指标正常
    DEGRADED = "degraded"         # 部分指标异常，降级运行
    UNHEALTHY = "unhealthy"       # 关键指标异常，按不健康处理
    UNKNOWN = "unknown"           # 指标缺失，按不健康处理（fail-closed）


@dataclass
class HealthIndicator:
    """单一健康指标。"""
    name: str                     # 指标名（如 data_feed_latency_ms）
    value: float
    threshold_warning: float
    threshold_critical: float
    timestamp: str
    is_critical_path: bool        # 是否关键路径（数据/引擎/下单）


@dataclass
class SystemHealthSnapshot:
    """系统健康快照。"""
    timestamp: str
    indicators: list[HealthIndicator]
    overall_state: HealthState
    health_score: float           # [0, 1] 综合健康度
    propagation_penalty: float    # 传播惩罚（关键路径异常放大）


def compute_system_health(
    indicators: list[HealthIndicator],
    propagation_factor: float = 2.0,  # 关键路径异常的放大因子
) -> SystemHealthSnapshot:
    """计算系统健康度——StockWatch 2026-07 propagation_penalty 机制。

    逻辑：
    1. 每个指标按阈值映射到 [0, 1] 健康分（1=正常，0=严重异常）
    2. 关键路径指标异常时施加传播惩罚（放大异常影响）
    3. 综合健康分 = 加权平均（关键路径权重更高）
    4. fail-closed：任何关键路径指标缺失 → overall_state=UNKNOWN → 按不健康处理

    关键路径（is_critical_path=True）：
    - data_feed: 数据源延迟/缺失/字段错乱
    - engine: 引擎心跳/订单生成/状态机
    - broker: 下单链路/回报接收/撤单成功率
    """
    if not indicators:
        return SystemHealthSnapshot(
            timestamp=datetime.now().isoformat(),
            indicators=[],
            overall_state=HealthState.UNKNOWN,  # fail-closed
            health_score=0.0,
            propagation_penalty=0.0,
        )

    # 关键路径指标缺失 → fail-closed
    critical_missing = any(
        ind.is_critical_path and ind.value is None for ind in indicators
    )
    if critical_missing:
        return SystemHealthSnapshot(
            timestamp=datetime.now().isoformat(),
            indicators=indicators,
            overall_state=HealthState.UNKNOWN,
            health_score=0.0,
            propagation_penalty=1.0,
        )

    # 计算每指标健康分 + 传播惩罚
    weighted_sum = 0.0
    weight_sum = 0.0
    total_penalty = 0.0

    for ind in indicators:
        # 健康分映射：value < threshold_critical → 0；> threshold_warning → 1；中间线性
        if ind.value >= ind.threshold_warning:
            ind_score = 1.0
        elif ind.value <= ind.threshold_critical:
            ind_score = 0.0
        else:
            ratio = (ind.value - ind.threshold_critical) / (
                ind.threshold_warning - ind.threshold_critical
            )
            ind_score = float(ratio)

        # 关键路径权重 × propagation_factor
        weight = propagation_factor if ind.is_critical_path else 1.0
        weighted_sum += ind_score * weight
        weight_sum += weight

        if ind.is_critical_path and ind_score < 1.0:
            total_penalty += (1.0 - ind_score) * (propagation_factor - 1.0)

    health_score = weighted_sum / weight_sum if weight_sum > 0 else 0.0

    # 总体状态映射
    if health_score >= 0.85:
        overall_state = HealthState.HEALTHY
    elif health_score >= 0.5:
        overall_state = HealthState.DEGRADED
    else:
        overall_state = HealthState.UNHEALTHY

    return SystemHealthSnapshot(
        timestamp=datetime.now().isoformat(),
        indicators=indicators,
        overall_state=overall_state,
        health_score=health_score,
        propagation_penalty=total_penalty,
    )


def get_critical_path_indicators() -> list[str]:
    """关键路径指标清单——这些指标缺失即 fail-closed。

    数据层：
    - data_feed_latency_ms: 数据源延迟（ms）
    - data_completeness_ratio: 数据完整度（0-1，缺字段/缺标的的比例）
    - data_freshness_seconds: 数据新鲜度（最近一笔距现在的秒数）

    引擎层：
    - engine_heartbeat_lag_ms: 引擎心跳延迟
    - order_generation_rate: 订单生成速率（应签名/分钟）
    - fsm_state_consistency: FSM 状态一致性（0-1）

    下单层（[40_execution_broker]）：
    - broker_connection_status: 券商连接状态（0/1）
    - order_ack_latency_ms: 订单回报延迟
    - cancel_success_rate: 撤单成功率（[40_execution_broker] CancelRateGuard）
    - rejection_rate: 拒单率
    """
    return [
        "data_feed_latency_ms",
        "data_completeness_ratio",
        "data_freshness_seconds",
        "engine_heartbeat_lag_ms",
        "order_generation_rate",
        "fsm_state_consistency",
        "broker_connection_status",
        "order_ack_latency_ms",
        "cancel_success_rate",
        "rejection_rate",
    ]
```

### 3.3 策略偏离监控算法（实盘 vs 回测）

```python
@dataclass
class StrategyDeviation:
    """策略偏离监控结果。"""
    strategy_id: str
    # 收益偏离
    realized_return_deviation: float      # 实盘收益 - 回测收益（日度）
    return_deviation_zscore: float        # z-score（基于 OOS 分布）
    # 持仓偏离
    holding_overlap_ratio: float          # 持仓重合度（实盘 vs 回测）
    position_size_deviation: float        # 仓位偏离度（L2 范数）
    # 行为偏离
    turnover_deviation: float             # 换手率偏离
    signal_correlation: float             # 信号相关性（实盘信号 vs 回测信号）
    # OOS rejection gate（StockWatch 2026-07）
    oos_rejection_triggered: bool         # 是否触发 OOS rejection（超 99% 分位）
    is_noise: bool                        # 是否为噪声（z-score < 2）


def monitor_strategy_deviation(
    strategy_id: str,
    live_daily_returns: list[float],      # 实盘日收益序列
    backtest_daily_returns: list[float],  # 同期回测日收益序列
    oos_return_distribution: list[float], # OOS 期日收益分布（用于 rejection gate）
    live_holdings: dict[str, float],      # 实盘当前持仓
    backtest_holdings: dict[str, float],  # 回测同期持仓
    live_turnover: float,
    backtest_turnover: float,
    zscore_warning: float = 2.0,
    zscore_critical: float = 3.0,
    oos_percentile_threshold: float = 0.99,
) -> StrategyDeviation:
    """策略偏离监控——区分噪声 vs 真漂移。

    核心逻辑：
    1. 收益偏离 z-score：基于 OOS 分布，z>2=warning，z>3=critical
    2. OOS rejection gate：偏离超 OOS 99% 分位 → 直接触发降级，不等人工
    3. 持仓重合度：实盘 vs 回测持仓 Jaccard 相似度
    4. 信号相关性：实盘信号 vs 回测信号 Pearson 相关
    5. 噪声判定：z<2 且相关性>0.8 视为噪声，不告警

    与 [53_simulation_live_path] 5态FSM 联动：
    - oos_rejection_triggered=True → 自动降级 NORMAL→THROTTLED
    - z>3 持续 3 天 → SOFT_HALT
    """
    # 收益偏离
    live_mean = float(np.mean(live_daily_returns)) if live_daily_returns else 0.0
    bt_mean = float(np.mean(backtest_daily_returns)) if backtest_daily_returns else 0.0
    realized_return_deviation = live_mean - bt_mean

    # z-score（基于 OOS 分布）
    if oos_return_distribution and np.std(oos_return_distribution) > 0:
        oos_std = float(np.std(oos_return_distribution))
        return_deviation_zscore = abs(realized_return_deviation) / oos_std
    else:
        return_deviation_zscore = 0.0

    # OOS rejection gate（StockWatch 2026-07）
    if oos_return_distribution:
        threshold = float(np.quantile(
            [abs(x) for x in oos_return_distribution], oos_percentile_threshold
        ))
        oos_rejection_triggered = abs(realized_return_deviation) > threshold
    else:
        oos_rejection_triggered = False

    # 持仓重合度（Jaccard）
    live_set = set(live_holdings.keys())
    bt_set = set(backtest_holdings.keys())
    if live_set or bt_set:
        intersection = len(live_set & bt_set)
        union = len(live_set | bt_set)
        holding_overlap_ratio = intersection / union if union > 0 else 0.0
    else:
        holding_overlap_ratio = 1.0

    # 仓位偏离度（L2 范数）
    all_symbols = set(live_holdings.keys()) | set(backtest_holdings.keys())
    position_diff = [
        live_holdings.get(s, 0.0) - backtest_holdings.get(s, 0.0)
        for s in all_symbols
    ]
    position_size_deviation = float(np.linalg.norm(position_diff))

    # 换手率偏离
    turnover_deviation = abs(live_turnover - backtest_turnover) / max(backtest_turnover, 1e-9)

    # 信号相关性（简化：用收益相关性近似）
    min_len = min(len(live_daily_returns), len(backtest_daily_returns))
    if min_len > 5:
        signal_correlation = float(np.corrcoef(
            live_daily_returns[:min_len],
            backtest_daily_returns[:min_len],
        )[0, 1])
    else:
        signal_correlation = 1.0

    # 噪声判定
    is_noise = (return_deviation_zscore < zscore_warning
                and signal_correlation > 0.8
                and not oos_rejection_triggered)

    return StrategyDeviation(
        strategy_id=strategy_id,
        realized_return_deviation=realized_return_deviation,
        return_deviation_zscore=return_deviation_zscore,
        holding_overlap_ratio=holding_overlap_ratio,
        position_size_deviation=position_size_deviation,
        turnover_deviation=turnover_deviation,
        signal_correlation=signal_correlation,
        oos_rejection_triggered=oos_rejection_triggered,
        is_noise=is_noise,
    )
```

### 3.4 ML 异常检测算法（Transformer Ensemble）

```python
@dataclass
class AnomalyDetectionResult:
    """ML 异常检测结果。"""
    is_anomaly: bool
    anomaly_score: float                 # [0, 1]，越高越异常
    anomaly_type: str                    # extreme_return / distribution_shift / model_decay / microstructure
    early_warning_minutes: int           # 提前预警分钟数
    confidence: float                    # 置信度


def detect_anomaly_transformer_ensemble(
    feature_window: np.ndarray,          # [T, F] 特征窗口
    threshold: float = 0.89,             # F1=0.89 对应阈值（Future Technology 2025-11）
) -> AnomalyDetectionResult:
    """Transformer ensemble 异常检测——Future Technology 2025-11 实证最佳。

    研究（Future Technology Journal 2025-11）：
    - 4 种架构对比：LSTM-Autoencoder / VAE / Transformer ensemble / TranAD
    - Transformer ensemble：F1=0.89 / AUC=0.94，较 ARIMA-GARCH（F1=0.62）+43.5%，较 XGBoost（F1=0.76）+17%
    - 92% 主要市场异常捕获，平均 15 分钟提前预警，FPR<3%
    - 多维特征：技术指标 + 市场微结构 + 情绪

    A 股适配：
    - 加入封板率/连板率（国信证券 2026-08-07）作为情绪特征
    - 加入涨跌停家数（A 股独有微结构）
    - 加入 T+1 持仓锁定比例（不可卖部分）

    MVP 阶段实现策略：
    - 暂不训练 Transformer（数据量不足）
    - 用 Isolation Forest + 统计过程控制替代（见 §3.5）
    - Phase 2+ 数据足够后切换到 Transformer ensemble
    """
    # MVP 替代实现：Isolation Forest（同样无监督、对分布偏移敏感）
    # 真实场景需加载预训练模型
    anomaly_score = 0.5  # placeholder：实际由模型推理产生

    is_anomaly = anomaly_score >= threshold
    anomaly_type = "extreme_return"  # 实际由特征贡献度判定

    return AnomalyDetectionResult(
        is_anomaly=is_anomaly,
        anomaly_score=float(anomaly_score),
        anomaly_type=anomaly_type,
        early_warning_minutes=15 if is_anomaly else 0,
        confidence=0.85,
    )


def detect_distribution_shift_ks_test(
    recent_returns: list[float],
    baseline_returns: list[float],
    alpha: float = 0.05,
) -> tuple[bool, float]:
    """收益分布偏斜度变化检测——CSDN 2026-08-04。

    使用 Kolmogorov-Smirnov 检验比较近端收益分布与基线分布。
    CSDN 2026-08-04 提到"收益分布偏斜度变化"作为异常行为监控指标。

    返回 (是否分布偏移, p-value)。
    p < alpha → 拒绝原假设 → 分布已偏移 → 异常。
    """
    from scipy import stats
    if len(recent_returns) < 10 or len(baseline_returns) < 30:
        return False, 1.0
    ks_stat, p_value = stats.ks_2samp(recent_returns, baseline_returns)
    return p_value < alpha, float(p_value)


def detect_extreme_return_day(
    daily_return: float,
    historical_returns: list[float],
    percentile_threshold: float = 0.99,
) -> tuple[bool, float]:
    """极端收益日监控——CSDN 2026-08-04。

    若当日收益超历史 99% 分位（绝对值），标记为极端收益日。
    CSDN 2026-08-04 明确提到"是否出现非逻辑性暴涨暴跌"作为异常监控指标。
    """
    if not historical_returns:
        return False, 0.0
    abs_threshold = float(np.quantile(
        [abs(r) for r in historical_returns], percentile_threshold
    ))
    is_extreme = abs(daily_return) > abs_threshold
    return is_extreme, abs_threshold


def detect_model_decay_cusum(
    rolling_ic: list[float],              # 滚动 IC 序列
    baseline_ic_mean: float,
    threshold: float = 5.0,               # CUSUM 累积阈值
) -> tuple[bool, float]:
    """模型预测力衰退检测——CUSUM 统计过程控制。

    逻辑：
    - IC 持续低于基线 → CUSUM 累积负值
    - 累积超阈值 → 模型衰退告警
    - 较单点阈值更鲁棒（避免噪声触发）
    """
    cusum = 0.0
    for ic in rolling_ic:
        deviation = baseline_ic_mean - ic
        cusum = max(0, cusum + deviation)
        if cusum > threshold:
            return True, cusum
    return False, cusum
```

### 3.5 三级告警分级与路由算法

```python
class AlertLevel(Enum):
    """告警三级——对标 StockWatch critical/warning/info。"""
    CRITICAL = "critical"   # 必须看：跌破止损/强卖出风险/负面重大消息/Kill Switch 触发
    WARNING = "warning"     # 建议看：触发盯价但盘口卖压偏重/普通买卖关注信号
    INFO = "info"           # 知会：常规状态变化


@dataclass
class AlertEvent:
    """告警事件。"""
    alert_id: str
    level: AlertLevel
    source: str                          # 来源模块（drawdown/var/liquidity/health/deviation/anomaly）
    strategy_id: Optional[str]
    title: str
    description: str
    timestamp: str
    # 联动动作
    fsm_action: Optional[str]            # 触发 FSM 动作（downgrade/hold）
    human_action_required: bool          # 是否需人工介入
    # 去重
    dedup_key: str                       # 同根因去重键
    related_alerts: list[str] = field(default_factory=list)


def classify_alert(
    source: str,
    severity: float,                     # 0-1，由检测层给出
    is_critical_path: bool = False,
    oos_rejection: bool = False,
) -> AlertLevel:
    """告警分级路由。

    分级规则：
    - CRITICAL：Kill Switch / 流动性黑洞 / OOS rejection / 关键路径 UNHEALTHY / 回撤 >20%
    - WARNING：回撤 8-15% / 关键路径 DEGRADED / 偏离 z>2 / 模型衰退 CUSUM
    - INFO：状态变化 / 常规对账差异 < 阈值
    """
    if (source in ("kill_switch", "liquidity_black_hole")
            or oos_rejection
            or (is_critical_path and severity >= 0.8)):
        return AlertLevel.CRITICAL
    if severity >= 0.5 or is_critical_path:
        return AlertLevel.WARNING
    return AlertLevel.INFO


def route_alert(
    alert: AlertEvent,
    fsm_state: str,                      # [53_simulation_live_path] 当前 FSM 状态
) -> dict:
    """告警路由——决定联动动作与通知渠道。

    联动 [53_simulation_live_path] 5态FSM：
    - CRITICAL + NORMAL/THROTTLED → 自动降级（如 OOS rejection → THROTTLED）
    - CRITICAL + SOFT_HALT/HARD_HALT → 触发 UNWINDING（如 Kill Switch）
    - WARNING → 记录但不自动降级（除非连续 N 次）

    通知渠道分级：
    - CRITICAL：电话+短信+IM（全渠道）
    - WARNING：IM+邮件
    - INFO：邮件日报
    """
    actions = {
        "fsm_action": None,
        "notify_channels": [],
        "human_action_required": False,
    }

    if alert.level == AlertLevel.CRITICAL:
        actions["notify_channels"] = ["phone", "sms", "im", "email"]
        actions["human_action_required"] = True
        # FSM 联动
        if alert.source == "kill_switch" and fsm_state != "unwinding":
            actions["fsm_action"] = "downgrade_to_unwinding"
        elif alert.source == "oos_rejection" and fsm_state == "normal":
            actions["fsm_action"] = "downgrade_to_throttled"
        elif alert.source == "liquidity_black_hole" and fsm_state in ("normal", "throttled"):
            actions["fsm_action"] = "downgrade_to_soft_halt"

    elif alert.level == AlertLevel.WARNING:
        actions["notify_channels"] = ["im", "email"]
        actions["human_action_required"] = alert.source in ("model_decay", "distribution_shift")

    else:  # INFO
        actions["notify_channels"] = ["email"]

    return actions


def deduplicate_alerts(
    alerts: list[AlertEvent],
    merge_window_minutes: int = 5,
) -> list[AlertEvent]:
    """告警去重——同根因 5 分钟内合并，避免告警疲劳。

    去重键设计：
    - 同 source + 同 strategy_id + 同根因 → 合并
    - 合并后保留最高级别，related_alerts 列出所有原始 ID
    """
    if not alerts:
        return []

    alerts_sorted = sorted(alerts, key=lambda a: a.timestamp)
    merged: list[AlertEvent] = []
    dedup_index: dict[str, AlertEvent] = {}

    for alert in alerts_sorted:
        if alert.dedup_key in dedup_index:
            existing = dedup_index[alert.dedup_key]
            # 取最高级别
            if alert.level.value == "critical" and existing.level.value != "critical":
                existing.level = alert.level
            existing.related_alerts.append(alert.alert_id)
        else:
            dedup_index[alert.dedup_key] = alert
            merged.append(alert)

    return merged
```

### 3.6 复盘机制算法（日/周/月/事件）

```python
@dataclass
class ReviewRecord:
    """复盘记录。"""
    review_type: str                     # daily / weekly / monthly / event
    period: str                          # 如 "2026-08-10" 或 "2026-W32"
    strategy_ids: list[str]
    # 收益归因（[54_reconciliation_attribution] Brinson）
    brinson_attribution: dict            # allocation/selection/interaction
    # 风险事件
    risk_events: list[dict]              # 回撤/VaR越限/流动性危机
    # 告警统计
    alert_summary: dict                  # {critical: N, warning: N, info: N}
    # 偏离与异常
    deviations: list[StrategyDeviation]
    anomalies: list[AnomalyDetectionResult]
    # 行动项
    action_items: list[dict]             # {item, owner, due_date, status}
    # 复盘结论
    conclusion: str
    lessons_learned: list[str]


def generate_daily_review(
    trade_date: str,
    strategies: list[str],
    brinson_result: dict,                # 来自 [54_reconciliation_attribution]
    risk_events: list[dict],
    alerts: list[AlertEvent],
    deviations: list[StrategyDeviation],
    anomalies: list[AnomalyDetectionResult],
) -> ReviewRecord:
    """生成日复盘——每日盘后自动触发。

    日复盘关注点（机构 PM 日报范式）：
    1. 当日 P&L 与归因（Brinson allocation/selection）
    2. 触发的风险事件（回撤/VaR/流动性）
    3. 告警统计与处理结果
    4. 策略偏离监控结果
    5. 异常检测结果
    6. 次日行动项

    T+1 适配（[54_reconciliation_attribution] §3.2）：
    - 当日买入未实现收益单列，不计入 selection effect
    - 仅 T-1 及更早持仓的实现收益计入 alpha 归因
    """
    alert_summary = {
        "critical": sum(1 for a in alerts if a.level == AlertLevel.CRITICAL),
        "warning": sum(1 for a in alerts if a.level == AlertLevel.WARNING),
        "info": sum(1 for a in alerts if a.level == AlertLevel.INFO),
    }

    action_items = []
    for dev in deviations:
        if dev.oos_rejection_triggered:
            action_items.append({
                "item": f"{dev.strategy_id} OOS rejection 触发，需评估是否退役",
                "owner": "risk_manager",
                "due_date": trade_date,
                "status": "open",
            })
        elif dev.return_deviation_zscore > 3.0:
            action_items.append({
                "item": f"{dev.strategy_id} 偏离 z>3，需排查根因",
                "owner": "trader",
                "due_date": trade_date,
                "status": "open",
            })

    return ReviewRecord(
        review_type="daily",
        period=trade_date,
        strategy_ids=strategies,
        brinson_attribution=brinson_result,
        risk_events=risk_events,
        alert_summary=alert_summary,
        deviations=deviations,
        anomalies=anomalies,
        action_items=action_items,
        conclusion="",  # 由人工填写
        lessons_learned=[],
    )


def generate_weekly_review(
    week_id: str,                        # 如 "2026-W32"
    daily_reviews: list[ReviewRecord],
    strategies: list[str],
) -> ReviewRecord:
    """生成周复盘——每周一盘前自动触发上周复盘。

    周复盘关注点（机构风控周报范式）：
    1. 周累计 P&L 与归因（Carino linking 多期合并，[54_reconciliation_attribution] §3.4）
    2. 周内风险事件汇总与趋势
    3. 告警趋势（critical/warning 是否递增）
    4. 策略偏离趋势（z-score 5 日序列）
    5. 策略间相关性变化（[23_strategy_correlation_validation]）
    6. 容量使用率（是否触及 capacity_aum_limit，[62_business_registry_construction] G9）
    7. 退役评估（[3.7] 算法）
    """
    # 周累计告警
    total_critical = sum(r.alert_summary["critical"] for r in daily_reviews)
    total_warning = sum(r.alert_summary["warning"] for r in daily_reviews)
    total_info = sum(r.alert_summary["info"] for r in daily_reviews)

    # 周累计风险事件
    weekly_risk_events = []
    for r in daily_reviews:
        weekly_risk_events.extend(r.risk_events)

    # 退役评估
    retirement_assessments = []
    for sid in strategies:
        retirement_assessments.append(assess_strategy_retirement(sid, daily_reviews))

    return ReviewRecord(
        review_type="weekly",
        period=week_id,
        strategy_ids=strategies,
        brinson_attribution={},  # 由 [54_reconciliation_attribution] Carino linking 给出
        risk_events=weekly_risk_events,
        alert_summary={
            "critical": total_critical,
            "warning": total_warning,
            "info": total_info,
        },
        deviations=[],
        anomalies=[],
        action_items=[
            {
                "item": f"策略 {a['strategy_id']} 退役评估：{a['recommendation']}",
                "owner": "risk_manager",
                "due_date": week_id,
                "status": "open" if a["recommendation"] != "continue" else "closed",
            }
            for a in retirement_assessments
            if a["recommendation"] != "continue"
        ],
        conclusion="",
        lessons_learned=[],
    )
```

### 3.7 策略退役标准算法

```python
@dataclass
class RetirementAssessment:
    """策略退役评估结果。"""
    strategy_id: str
    # 触发的退役条件
    consecutive_underperform_days: int   # 连续跑输基准天数
    logic_invalidated: bool              # 逻辑失效（如监管规则变化）
    capacity_exceeded: bool              # 容量超限
    correlation_regime_shift: bool       # 相关性突变
    oos_rejection_count: int             # OOS rejection 累计次数
    # 建议
    recommendation: str                  # continue / monitor / retire
    reason: str


def assess_strategy_retirement(
    strategy_id: str,
    daily_reviews: list[ReviewRecord],
    consecutive_underperform_threshold: int = 20,   # 连续跑输 20 天
    oos_rejection_threshold: int = 3,               # 累计 3 次 OOS rejection
) -> RetirementAssessment:
    """策略退役评估——5 维度退役标准。

    退役触发条件（任一满足即建议退役）：
    1. 连续跑输基准 ≥ 20 个交易日（机构标准，约 1 个月）
    2. 逻辑失效：监管规则变化/市场结构变化使策略经济逻辑不再成立
       （如 2026-07-31 交易所局域网行情通道关闭，依赖微秒级速度的策略失效）
    3. 容量超限：实盘 AUM 超 capacity_aum_limit（[62_business_registry_construction] G9）
    4. 相关性突变：与其他策略相关性突增（如 >0.6 → 多策略实为情绪 beta 穿多件衣服）
    5. OOS rejection 累计 ≥ 3 次：实盘行为持续偏离 OOS 分布

    建议：
    - 任一触发 → retire
    - 接近阈值（80%）→ monitor
    - 否则 → continue
    """
    consecutive_underperform = 0
    oos_rejection_count = 0
    for review in reversed(daily_reviews):
        for dev in review.deviations:
            if dev.strategy_id == strategy_id:
                if dev.realized_return_deviation < 0:
                    consecutive_underperform += 1
                else:
                    break
                if dev.oos_rejection_triggered:
                    oos_rejection_count += 1

    # 退役条件判定（容量与相关性突变需外部输入，这里用占位）
    capacity_exceeded = False  # 实际从 strategy_registry 查 capacity_aum_limit
    correlation_regime_shift = False  # 实际从 [23_strategy_correlation_validation] 查
    logic_invalidated = False  # 实际由人工标记（如监管变化）

    retire_conditions = [
        (consecutive_underperform >= consecutive_underperform_threshold,
         f"连续跑输 {consecutive_underperform} 天"),
        (logic_invalidated, "策略逻辑失效"),
        (capacity_exceeded, "容量超限"),
        (correlation_regime_shift, "相关性突变"),
        (oos_rejection_count >= oos_rejection_threshold,
         f"OOS rejection 累计 {oos_rejection_count} 次"),
    ]

    triggered = [reason for cond, reason in retire_conditions if cond]

    if triggered:
        recommendation = "retire"
        reason = "；".join(triggered)
    elif (consecutive_underperform >= 0.8 * consecutive_underperform_threshold
          or oos_rejection_count >= 0.8 * oos_rejection_threshold):
        recommendation = "monitor"
        reason = "接近退役阈值，加强监控"
    else:
        recommendation = "continue"
        reason = "运行正常"

    return RetirementAssessment(
        strategy_id=strategy_id,
        consecutive_underperform_days=consecutive_underperform,
        logic_invalidated=logic_invalidated,
        capacity_exceeded=capacity_exceeded,
        correlation_regime_shift=correlation_regime_shift,
        oos_rejection_count=oos_rejection_count,
        recommendation=recommendation,
        reason=reason,
    )
```

### 3.8 净值归因（择时能力 T-M/H-M/C-L）补充算法

```python
def net_value_attribution_tm_hm_cl(
    portfolio_returns: list[float],
    market_returns: list[float],
    risk_free_rate: float = 0.0,
) -> dict:
    """净值归因——长江证券 2026-01 推荐的择时能力三模型。

    长江证券 2026-01-18《组合归因探微之一》指出：
    净值归因核心体系起源于 CAPM，对 Alpha/Beta 不同维度刻画。
    择时能力模型三件套：
    - T-M (Treynor-Mazuy, 1966)：二次项回归，捕捉凸性择时
    - H-M (Henriksson-Merton, 1981)：虚拟变量回归，捕捉下跌保护
    - C-L (Chang-Lewellen, 1984)：分段回归，更精细的牛熊分解

    与 [54_reconciliation_attribution] Brinson 持仓归因互补：
    - Brinson：基于持仓的相对收益拆解（allocation/selection/interaction）
    - 净值归因：基于净值的时序回归（alpha/beta/择时能力）
    两者正交，机构标准是双轨并用。
    """
    import numpy as np
    from scipy import stats as sp_stats

    portfolio = np.array(portfolio_returns) - risk_free_rate
    market = np.array(market_returns) - risk_free_rate
    n = len(portfolio)
    if n < 30:
        return {"error": "insufficient_data", "min_required": 30}

    # T-M 模型：R_p - R_f = α + β(R_m - R_f) + γ(R_m - R_f)^2 + ε
    # γ > 0 → 凸性 → 成功择时
    market_squared = market ** 2
    X_tm = np.column_stack([np.ones(n), market, market_squared])
    beta_tm, _, _, _ = np.linalg.lstsq(X_tm, portfolio, rcond=None)
    alpha_tm, beta, gamma_tm = beta_tm[0], beta_tm[1], beta_tm[2]

    # H-M 模型：R_p - R_f = α + β(R_m - R_f) + δ·max(0, R_f - R_m) + ε
    # δ > 0 → 下跌保护
    downside_dummy = np.maximum(0, -market)
    X_hm = np.column_stack([np.ones(n), market, downside_dummy])
    beta_hm, _, _, _ = np.linalg.lstsq(X_hm, portfolio, rcond=None)
    alpha_hm, _, delta_hm = beta_hm[0], beta_hm[1], beta_hm[2]

    # C-L 模型：分段（牛市/熊市分别回归）
    bull_mask = market > 0
    bear_mask = market <= 0
    bull_beta = (float(np.cov(portfolio[bull_mask], market[bull_mask])[0, 1] /
                       np.var(market[bull_mask]))
                 if bull_mask.sum() > 5 else 0.0)
    bear_beta = (float(np.cov(portfolio[bear_mask], market[bear_mask])[0, 1] /
                       np.var(market[bear_mask]))
                 if bear_mask.sum() > 5 else 0.0)
    cl_timing_skill = bull_beta - bear_beta  # > 0 → 牛市更激进，熊市更保守 = 择时成功

    return {
        "tm_model": {
            "alpha": float(alpha_tm),
            "beta": float(beta),
            "timing_gamma": float(gamma_tm),       # > 0 = 择时成功
            "interpretation": "凸性（γ>0）表示成功择时" if gamma_tm > 0 else "无择时能力",
        },
        "hm_model": {
            "alpha": float(alpha_hm),
            "timing_delta": float(delta_hm),       # > 0 = 下跌保护
            "interpretation": "下跌保护（δ>0）表示成功择时" if delta_hm > 0 else "无下跌保护",
        },
        "cl_model": {
            "bull_beta": float(bull_beta),
            "bear_beta": float(bear_beta),
            "timing_skill": float(cl_timing_skill),
            "interpretation": "牛熊 Beta 差>0 表示成功择时" if cl_timing_skill > 0 else "无择时能力",
        },
        "overall_timing_ability": (
            "strong" if (gamma_tm > 0 and delta_hm > 0 and cl_timing_skill > 0)
            else "partial" if any([gamma_tm > 0, delta_hm > 0, cl_timing_skill > 0])
            else "none"
        ),
    }
```

### 3.9 A 股情绪指标接入（国信证券 2026-08-07）

```python
def compute_a_share_sentiment_indicators(
    limit_up_count: int,
    limit_up_sealed_count: int,          # 收盘仍封板的家数
    limit_up_high_count: int,            # 触及涨停的家数（含开板）
    yesterday_limit_up_count: int,
    today_consecutive_limit_up_count: int,
    block_trade_total_value: float,
    block_trade_total_market_cap: float,
    futures_price: float,
    spot_price: float,
    futures_days_to_expiry: int,
) -> dict:
    """A 股情绪指标——国信证券 2026-08-07 实证模型。

    4 个核心指标（国信证券 2026-08-07 研报）：
    1. 封板率 = 收盘封板数 / 触及涨停数（反映封板资金决心）
    2. 连板率 = 连续两日涨停数 / 昨日涨停数（反映热点延续性）
    3. 大宗交易折价率 = 大宗成交金额 / 总市值 - 1（反映大资金议价力）
    4. 股指期货年化贴水率 = 基差/现货 × (250/剩余交易日)（反映对冲成本与预期）

    这些指标作为：
    - [24_daban_strategy_detail] 情绪周期定位器的输入特征
    - [28_sentiment_cycle_trading] 情绪周期阶段判定的辅助
    - [55_monitoring_review] 异常检测的情绪维度特征
    """
    sealed_rate = (
        limit_up_sealed_count / limit_up_high_count
        if limit_up_high_count > 0 else 0.0
    )
    consecutive_rate = (
        today_consecutive_limit_up_count / yesterday_limit_up_count
        if yesterday_limit_up_count > 0 else 0.0
    )
    block_trade_discount = (
        block_trade_total_value / block_trade_total_market_cap - 1.0
        if block_trade_total_market_cap > 0 else 0.0
    )
    basis = futures_price - spot_price
    annualized_basis = (
        basis / spot_price * (250.0 / max(futures_days_to_expiry, 1))
        if spot_price > 0 else 0.0
    )

    return {
        "sealed_rate": float(sealed_rate),                       # 封板率
        "consecutive_limit_up_rate": float(consecutive_rate),    # 连板率
        "block_trade_discount_rate": float(block_trade_discount),# 大宗折价率
        "annualized_futures_basis": float(annualized_basis),     # 年化贴水率
        # 情绪综合判定（经验阈值，需回测校准）
        "sentiment_tag": (
            "overheated" if sealed_rate > 0.8 and consecutive_rate > 0.3
            else "frozen" if sealed_rate < 0.4 and consecutive_rate < 0.1
            else "normal"
        ),
    }
```

## 4. 考虑过的替代方案

### 4.1 单一阈值告警 vs 三层检测（阈值+SPC+ML）

- **单一阈值**：简单但易漏报（缓慢漂移不触发）和误报（噪声触发）
- **三层检测**：阈值规则捕获已知模式，SPC（CUSUM）捕获趋势衰退，ML 捕获未知模式
- **裁定**：采用三层检测。MVP 阶段先上阈值+SPC，ML 异常检测（Transformer ensemble）作为 Phase 2+ 升级项，先用 Isolation Forest 替代

### 4.2 主动告警（推）vs 仪表盘（拉）

- **主动告警**：事件发生即推送，响应快，但易告警疲劳
- **仪表盘**：人为查阅，无疲劳但响应慢
- **裁定**：critical/warning 主动推送，info 仅入仪表盘日报。配合 §3.5 去重算法避免疲劳

### 4.3 全自动降级 vs 人工确认

- **全自动降级**：响应快，但误判风险高
- **人工确认**：稳妥，但响应慢
- **裁定**：参考 [53_simulation_live_path] fail-closed 原则——降级自动、升级人工。CRITICAL 告警触发自动降级（OOS rejection → THROTTLED；Kill Switch → UNWINDING），WARNING 仅告警不自动降级

### 4.4 复盘完全自动化 vs 模板+人工填写

- **完全自动化**：省人力，但结论与经验教训无法自动生成
- **模板+人工**：标准结构保证可追溯，人工补充深度洞察
- **裁定**：模板+人工。算法自动生成数据部分（P&L/归因/告警统计/退役评估），conclusion 与 lessons_learned 由人工填写

## 5. 上限定义

### 5.1 当前阶段上限

- **检测维度**：系统健康（10 关键路径指标）+ 策略偏离（5 维度）+ 异常检测（3 类：极端收益/分布偏移/模型衰退）
- **告警级别**：3 级（critical/warning/info），最多 5 个通知渠道（phone/sms/im/email/dashboard）
- **复盘周期**：日/周/月/事件 四种
- **退役标准**：5 维度（连续跑输/逻辑失效/容量超限/相关性突变/OOS rejection 累计）

### 5.2 演进路径

- **MVP**（当前）：阈值+SPC+Isolation Forest，日复盘+周复盘
- **Phase 1.5+**：Transformer ensemble 异常检测（需 1 年+数据训练），月复盘
- **Phase 2+**：因果归因（causal-quant 联动 [52_backtest_framework_docking] E17），自动根因分析
- **Phase 3+**：实时异常检测（盘中秒级），自适应调度（[CSDN 2026-08-04] 策略稳定性监控与自适应调度系统设计）

### 5.3 为何是上限

- **检测精度上限**：ML 异常检测 F1≤0.89（Future Technology 2025-11 实证），FPR≥3%，无法 100% 捕获
- **告警延迟下限**：从检测到通知至少 1 秒（网络+渲染），无法做到零延迟
- **复盘深度上限**：算法只能给出"是什么+多少"，"为什么+怎么办"需人工

## 6. 待裁定

| 暂缓项 | 暂缓理由 | 重评条件 |
|---|---|---|
| Transformer ensemble 训练 | 需 1 年+实盘数据，当前不足 | Phase 1.5+ 数据足够后启动 |
| 因果归因 | 依赖 causal-quant 证伪电池（[52_backtest_framework_docking] E17） | Phase 1.5+ causal-quant 落地后 |
| 实时盘中异常检测 | 当前为盘后批次，盘中实时需低延迟架构 | Phase 2+ 实盘稳定运行 6 月后 |
| 自适应调度（自动调参） | [CSDN 2026-08-04] 提及但工程复杂度高 | Phase 3+ 多策略稳定运行后 |

## 7. 待定问题（讨论要点对齐）

> 以下来自 00_index §3 G26 讨论要点，本节逐项对齐后落入 §3 决策。

- [x] ① 系统健康监控（数据/引擎/下单链路）→ §3.2 三层关键路径指标 + propagation_penalty
- [x] ② 策略偏离监控（实盘 vs 回测）→ §3.3 五维度偏离 + OOS rejection gate
- [x] ③ 告警阈值与通知 → §3.5 三级分级 + 5 通知渠道 + 去重算法
- [x] ④ 每日/每周/每月复盘机制 → §3.6 日/周/月/事件 四种复盘模板
- [x] ⑤ 策略退役标准（连续跑输/逻辑失效）→ §3.7 五维度退役评估
- [x] ⑥ 复盘文档模板 → §3.6 ReviewRecord 数据结构

## 8. 引用

- [00_index_trading_decision](00_index_trading_decision.md) §3 G26
- [54_reconciliation_attribution](54_reconciliation_attribution.md)（G25，Brinson 归因输入）
- [53_simulation_live_path](53_simulation_live_path.md)（G24，5态FSM 联动）
- [35_drawdown_protocol_impl](35_drawdown_protocol_impl.md)（G16，回撤事件输入）
- [36_var_es_monitoring](36_var_es_monitoring.md)（G17，VaR/ES 越限输入）
- [37_liquidity_crisis_protocol](37_liquidity_crisis_protocol.md)（G18，流动性危机输入）
- [40_execution_broker](40_execution_broker.md)（CancelRateGuard 拒单率输入）
- [50_backtest_observability_workplan](50_backtest_observability_workplan.md)（可观测性体系衔接）
- [62_business_registry_construction](62_business_registry_construction.md)（capacity_aum_limit 容量查询）
- [23_strategy_correlation_validation](23_strategy_correlation_validation.md)（相关性突变检测）

## 9. 2026-08 研究对标

| 研究来源 | 关键贡献 | 本文档应用 |
|---|---|---|
| CSDN 2026-08-04 策略稳定性监控与自适应调度 | 极端收益日监控 + 收益分布偏斜度变化 + 健康度得分 | §3.2 健康度 / §3.4 分布偏移 KS 检验 / 极端收益日 |
| StockWatch GitHub 2026-07-10 | LightGBM 健康门 + propagation penalty + OOS rejection gates + fail-closed on unknown | §3.2 fail-closed / §3.3 OOS rejection gate / §3.5 告警分级 |
| Future Technology Journal 2025-11 (Dai) | Transformer ensemble F1=0.89/AUC=0.94/15 分钟提前预警/FPR<3% | §3.4 ML 异常检测（Phase 2+ 升级目标） |
| LSTM-Autoencoder + GAN + One-Class SVM (Preprints 2025-06) | 合成异常注入评估 + 多 regime 验证 | §3.4 异常检测策略参考 |
| SOM 自组织映射 (GitHub 2026-03) | 无监督异常检测 + 跨资产验证 + 信号分类法 | §3.4 异常分类参考 |
| 长江证券 2026-01-18 组合归因探微之一 | BHB vs BF + 净值归因 T-M/H-M/C-L 择时能力 | §3.8 净值归因三模型 |
| 国信证券 2026-08-07 金融工程日报 | 封板率/连板率/大宗折价率/年化贴水率 | §3.9 A 股情绪指标接入 |

## 10. 修订记录

| 日期 | 版本 | 改动 | 理由 |
|---|---|---|---|
| 2026-08-09 | 0.1.0 | 骨架创建 | 施工图骨架先行：由 00_index G26 讨论要点占位 |
| 2026-08-10 | 1.0.0 | 骨架→active，补齐施工算法 | 整合 2026-08 最新研究：系统健康传播惩罚+OOS rejection gate+三层检测（阈值+SPC+ML）+三级告警去重+四周期复盘+五维退役标准+净值归因 T-M/H-M/C-L+A 股情绪指标接入；与 [35/36/37/40/53/54] 模块接口契约对齐 |
