---
module_id: TACTICS_README_001
version: 1.0.0
status: Active
created_date: 2026-04-01
last_updated: 2026-04-01
owner: 首席文档架构师
standard_type: 专业量化机构文档
applicable_scope: 全系统
compliance_level: 初始标准
parent_document: ../INDEX.md
implementation_status: 进行中
---

# 仓位管理系统

> 固定分数、凯利公式、风险平价

**版本**: v1.0
**更新**: 2026-03-29
**Layer**: Layer 3 (策略层)
**索引**: 03_TRADING_TACTICS/06_POSITION_MANAGEMENT

---

## 1. 仓位管理概述

仓位管理是人(决策)与AI(执行)的核心接口：

| 角色 | 职责 |
|------|------|
| **人** | 风控规则设计（你能承受多大风险） |
| **AI** | 计算具体仓位、执行交易 |

---

## 2. 仓位管理方法

### 2.1 固定分数法 (Fixed Fraction)

```python
class FixedFractionSizer:
    """固定分数仓位管理"""

    def __init__(self, fraction: float = 0.02):
        self.fraction = fraction  # 每笔交易风险比例

    def calculate_position(self, account_value: float,
                          stop_loss_pct: float) -> int:
        """计算仓位股数"""
        risk_amount = account_value * self.fraction
        shares = int(risk_amount / (stop_loss_pct * account_value))
        return shares
```

### 2.2 凯利公式 (Kelly Criterion)

```python
class KellySizer:
    """凯利公式仓位管理"""

    def __init__(self, max_kelly_fraction: float = 0.25):
        self.max_kelly = max_kelly_fraction  # 防止过曝

    def calculate_kelly(self, win_rate: float, avg_win: float,
                       avg_loss: float) -> float:
        """计算凯利比例"""
        if avg_loss == 0:
            return 0
        b = avg_win / avg_loss  # 盈亏比
        q = 1 - win_rate
        kelly = (b * win_rate - q) / b

        # 限制最大仓位
        return max(0, min(kelly, self.max_kelly))

    def calculate_position(self, account_value: float,
                          win_rate: float, avg_win: float,
                          avg_loss: float) -> int:
        """计算仓位"""
        kelly = self.calculate_kelly(win_rate, avg_win, avg_loss)
        return int(account_value * kelly / avg_win)
```

### 2.3 风险平价 (Risk Parity)

```python
class RiskParitySizer:
    """风险平价仓位管理"""

    def __init__(self, target_volatility: float = 0.15):
        self.target_vol = target_volatility

    def calculate_weights(self, positions: Dict[str, float],
                        volatilities: Dict[str, float]) -> Dict[str, float]:
        """计算风险平价权重"""
        # 等风险贡献权重
        inv_vol = {k: 1/v for k, v in volatilities.items()}
        total_inv_vol = sum(inv_vol.values())
        weights = {k: v/total_inv_vol for k, v in inv_vol.items()}

        # 调整到目标波动率
        current_vol = self._calculate_portfolio_vol(weights, volatilities)
        adjustment = self.target_vol / current_vol if current_vol > 0 else 1

        return {k: v * adjustment for k, v in weights.items()}

    def _calculate_portfolio_vol(self, weights: Dict[str, float],
                                  volatilities: Dict[str, float]) -> float:
        """计算组合波动率"""
        import numpy as np
        w = np.array(list(weights.values()))
        v = np.array(list(volatilities.values()))
        return np.sqrt(np.dot(w**2, v**2))
```

### 2.4 金字塔加码

```python
class PyramidSizer:
    """金字塔加码/减码策略"""

    def __init__(self, base_position: int, max_layers: int = 3,
                 increment: float = 0.5):
        self.base_position = base_position
        self.max_layers = max_layers
        self.increment = increment

    def calculate_pyramid(self, layer: int, direction: str) -> int:
        """计算某层的仓位"""
        if direction == 'add':
            return int(self.base_position * (1 + self.increment) ** layer)
        else:  # reduce
            return int(self.base_position * (1 - self.increment) ** layer)
```

---

## 3. 风控规则配置

```yaml
# config/risk_rules.yaml
risk_management:
  position_sizing:
    method: "kelly"  # fixed_fraction / kelly / risk_parity
    params:
      kelly_fraction: 0.25
      target_volatility: 0.15

  max_positions:
    total: 10
    single_stock: 0.15  # 最大单只股票仓位占比

  stop_loss:
    fixed: 0.05  # 固定止损5%
    trailing: true  # 跟踪止损

  drawdown_control:
    max_drawdown: 0.20  # 最大回撤20%
    reduce_ratio: 0.50  # 触发后仓位减半
```

---

## 4. 层级关系

```
Layer 3 (策略层)
    ↓ 上游
Layer 2 (因子层) → 提供信号
Layer 4 (执行层) → 执行订单
    ↓ 下游
Layer 5 (监控层) → 监控风险
```

---

## 索引

- 父目录: [03_TRADING_TACTICS/README.md](../README.md)
- 上游: [STRATEGY_TEMPLATES.md](../01_STRATEGY_FRAMEWORK/STRATEGY_TEMPLATES.md)
- 下游: [07_ORDER_GENERATION/README.md](../07_ORDER_GENERATION/README.md)
