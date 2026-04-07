﻿---
module_id: TACTICS_ARCH_MANAGER_001
version: 1.0.1
status: Active
created_date: 2026-04-01
last_updated: 2026-04-01
owner: 首席文档架构?
standard_type: 专业量化机构文档
applicable_scope: 全系?
compliance_level: 初始标准
parent_document: ../INDEX.md
implementation_status: 进行?
responsibility:
  - 市场状态识别 (Layer 4)
---

# 策略池管理器
> **核心职责**: 文档内容说明
> **职责边界**: 
> - ✅ 本文档负责：文档内容说明相关内容
> - ❌ 本文档不负责：其他模块内容


> 策略池核心管理器
>
> **配套文档**?
> - 主文档：[../../INDEX.md](../INDEX.md)
> - 策略接口标准：
***

## 1. 策略池管理器?

```python
class StrategyPool:
    """策略池管理器"""

    def __init__(self, max_strategies: int = 50):
        self.strategies: Dict[str, BaseStrategy] = {}
        self.strategy_weights: Dict[str, float] = {}
        self.max_strategies = max_strategies
        self.market_state = MarketState.VOLATILE
        self.enabled_strategies: Set[str] = set()

    def register_strategy(self, strategy: BaseStrategy) -> bool:
        """
        注册策略到策略池
        """
        if len(self.strategies) >= self.max_strategies:
            return False

        if strategy.strategy_id in self.strategies:
            return False

        self.strategies[strategy.strategy_id] = strategy
        self.enabled_strategies.add(strategy.strategy_id)
        return True

    def unregister_strategy(self, strategy_id: str) -> bool:
        """注销策略"""
        if strategy_id in self.strategies:
            del self.strategies[strategy_id]
            self.enabled_strategies.discard(strategy_id)
            return True
        return False

    def set_market_state(self, market_state: MarketState):
        """设置市场状?""
        self.market_state = market_state

    def select_strategies(self,
                         min_sharpe: float = 0.5,
                         max_strategies: int = 10) -> List[BaseStrategy]:
        """
        根据市场状态选择策略

        参数:
            min_sharpe: 最小夏普比率要?
            max_strategies: 最多选择的策略数?

        返回:
            符合条件的策略列表，按夏普比率降序排?
        """
        candidates = []

        for strategy_id in self.enabled_strategies:
            strategy = self.strategies[strategy_id]

            # 检查是否适用于当前市场状?
            if self.market_state not in strategy.get_applicable_states():
                continue

            # 检查绩?
            perf = strategy.get_performance()
            if perf.sharpe_ratio < min_sharpe:
                continue

            candidates.append((strategy, perf.sharpe_ratio))

        # 按夏普比率降序排?
        candidates.sort(key=lambda x: x[1], reverse=True)

        return [s[0] for s in candidates[:max_strategies]]

    def allocate_weights(self, selected_strategies: List[BaseStrategy]) -> Dict[str, float]:
        """
        策略权重分配

        方法: 基于夏普比率的，风险平价分配

        返回:
            策略ID -> 权重 的字?
        """
        if not selected_strategies:
            return {}

        # 计算总夏普比?
        total_sharpe = sum(
            s.get_performance().sharpe_ratio
            for s in selected_strategies
        )

        if total_sharpe == 0:
            return {s.strategy_id: 1.0/len(selected_strategies)
                   for s in selected_strategies}

        # 基于夏普比率分配权重
        weights = {}
        for strategy in selected_strategies:
            sharpe = strategy.get_performance().sharpe_ratio
            weights[strategy.strategy_id] = sharpe / total_sharpe

        return weights

    def generate_composite_signal(self,
                                  stock_code: str,
                                  market_data: pd.DataFrame,
                                  stock_data: pd.DataFrame) -> List[TradingSignal]:
        """
        生成复合信号

        流程:
        1. 选择适合当前市场状态的策略
        2. 分配策略权重
        3. 各策略分别生成信?
        4. 按权重聚合信?
        """
        # 选择策略
        selected = self.select_strategies(max_strategies=10)
        if not selected:
            return []

        # 分配权重
        self.strategy_weights = self.allocate_weights(selected)

        # 生成各策略信?
        all_signals = []
        for strategy in selected:
            signal = strategy.generate_signal(
                market_data, stock_data, self.market_state
            )
            if signal:
                signal.confidence *= self.strategy_weights[strategy.strategy_id]
                all_signals.append(signal)

        # 按置信度排序
        all_signals.sort(key=lambda x: x.confidence, reverse=True)

        return all_signals
```

***

## 2. 策略池管理器配置

```python
# 策略池配?
STRATEGY_POOL_CONFIG = {
    'max_strategies': 50,
    'default_selection': 10,
    'min_sharpe_for_selection': 0.3,
    'min_confidence_threshold': 0.4,
    'max_position_per_strategy': 0.2,
    'market_state_update_freq': 'daily'
}

# 策略参数配置模板
STRATEGY_PARAM_TEMPLATES = {
    'T001': {
        'ma_short': 5,
        'ma_medium': 20,
        'ma_long': 60,
        'min_volume_ratio': 1.5
    },
    'S001': {
        'min_limit_up_amount': 1e8,
        'max_float_market_cap': 100e8,
        'max_turnover_rate': 15,
        'max_open_times': 2
    },
    'M001': {
        'rsi_period': 14,
        'rsi_oversold': 30,
        'rsi_threshold': 40
    }
}
```

***

## 更新记录

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| v1.0 | 2026-03-26 | 初始版本 |
