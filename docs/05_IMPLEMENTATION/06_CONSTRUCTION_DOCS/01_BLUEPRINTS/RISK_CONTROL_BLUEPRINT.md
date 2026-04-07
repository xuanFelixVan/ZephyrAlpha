---
responsibility:
  - 实施指南、部署文档
  - 风险预算
  - 数据质量

module_id: RISK_CONTROL_001
version: 1.0.0
status: Active
created_date: 2026-04-07
last_updated: 2026-04-07
owner: 实施团队
standard_type: 专业量化机构蓝图
applicable_scope: Layer 6 组合优化层
compliance_level: 专业标准
layer: "Layer 6 (组合优化层)"
---

# 风险控制蓝图

> **核心职责**: 微观执行层实时风险控制
> **职责边界**: 
> - ✅ 本文档负责：实时监控、风险预警、风险控制
> - ❌ 本文档不负责：因子计算（由因子模块负责） |
| **风险处置** | 执行风险处置措施 | 处置记录 |
| **风险报告** | 生成风险报告 | 风险报告 |

---
## 🏗️ 架构设计

### 风险控制维度

| 风险维度 | 风险指标 | 阈值 | 处置措施 |
|---------|---------|------|---------|
| **价格风险** | 单股票亏损 | > 5% | 减仓50% |
| **价格风险** | 组合亏损 | > 3% | 全部平仓 |
| **仓位风险** | 单股票仓位 | > 10% | 限制开仓 |
| **仓位风险** | 总仓位 | > 95% | 限制开仓 |
| **流动性风险** | 成交量萎缩 | < 50% | 暂停交易 |
| **波动率风险** | 波动率飙升 | > 3σ | 降低仓位 |

---

## 🔧 关键组件设计

### 1. 实时风险监控器

```python
from typing import Dict, Any
import pandas as pd
import numpy as np
import redis

class RealtimeRiskMonitor:
    """实时风险监控器"""
    
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.risk_thresholds = {
            'single_stock_loss': 0.05,
            'portfolio_loss': 0.03,
            'single_stock_position': 0.10,
            'total_position': 0.95,
            'volume_drop': 0.50,
            'volatility_spike': 3.0
        }
        
    def monitor(self, 
                positions: Dict[str, float],
                market_data: pd.DataFrame) -> Dict[str, Any]:
        """实时监控风险"""
        risk_status = {}
        
        # 监控价格风险
        price_risk = self._monitor_price_risk(positions, market_data)
        risk_status['price_risk'] = price_risk
        
        # 监控仓位风险
        position_risk = self._monitor_position_risk(positions)
        risk_status['position_risk'] = position_risk
        
        # 监控流动性风险
        liquidity_risk = self._monitor_liquidity_risk(market_data)
        risk_status['liquidity_risk'] = liquidity_risk
        
        # 监控波动率风险
        volatility_risk = self._monitor_volatility_risk(market_data)
        risk_status['volatility_risk'] = volatility_risk
        
        # 综合风险评估
        overall_risk = self._calculate_overall_risk(risk_status)
        risk_status['overall_risk'] = overall_risk
        
        # 存储到Redis
        self.redis.setex('risk_status', 60, str(risk_status))
        
        return risk_status
    
    def _monitor_price_risk(self,
                           positions: Dict[str, float],
                           market_data: pd.DataFrame) -> Dict[str, Any]:
        """监控价格风险"""
        # 计算单股票亏损
        single_stock_losses = {}
        for symbol, position in positions.items():
            if symbol in market_data.columns:
                current_price = market_data[symbol].iloc[-1]
                cost_price = position['cost_price']
                loss = (current_price - cost_price) / cost_price
                single_stock_losses[symbol] = loss
        
        # 计算组合亏损
        portfolio_loss = np.mean(list(single_stock_losses.values()))
        
        # 判断风险等级
        risk_level = 'LOW'
        if portfolio_loss < -self.risk_thresholds['portfolio_loss']:
            risk_level = 'HIGH'
        elif portfolio_loss < -self.risk_thresholds['portfolio_loss'] * 0.5:
            risk_level = 'MEDIUM'
        
        return {
            'risk_level': risk_level,
            'single_stock_losses': single_stock_losses,
            'portfolio_loss': portfolio_loss
        }
    
    def _monitor_position_risk(self, positions: Dict[str, float]) -> Dict[str, Any]:
        """监控仓位风险"""
        # 计算单股票仓位
        total_value = sum(p['market_value'] for p in positions.values())
        single_stock_positions = {
            symbol: p['market_value'] / total_value
            for symbol, p in positions.items()
        }
        
        # 计算总仓位
        total_position = sum(single_stock_positions.values())
        
        # 判断风险等级
        risk_level = 'LOW'
        if total_position > self.risk_thresholds['total_position']:
            risk_level = 'HIGH'
        elif total_position > self.risk_thresholds['total_position'] * 0.9:
            risk_level = 'MEDIUM'
        
        return {
            'risk_level': risk_level,
            'single_stock_positions': single_stock_positions,
            'total_position': total_position
        }
    
    def _monitor_liquidity_risk(self, market_data: pd.DataFrame) -> Dict[str, Any]:
        """监控流动性风险"""
        # 计算成交量变化
        volume_ma = market_data['volume'].rolling(20).mean()
        current_volume = market_data['volume'].iloc[-1]
        volume_ratio = current_volume / volume_ma.iloc[-1]
        
        # 判断风险等级
        risk_level = 'LOW'
        if volume_ratio < self.risk_thresholds['volume_drop']:
            risk_level = 'HIGH'
        elif volume_ratio < self.risk_thresholds['volume_drop'] * 1.5:
            risk_level = 'MEDIUM'
        
        return {
            'risk_level': risk_level,
            'volume_ratio': volume_ratio
        }
    
    def _monitor_volatility_risk(self, market_data: pd.DataFrame) -> Dict[str, Any]:
        """监控波动率风险"""
        # 计算波动率
        returns = market_data['close'].pct_change()
        volatility = returns.rolling(20).std() * np.sqrt(252 * 240)
        
        # 计算波动率Z-Score
        current_vol = volatility.iloc[-1]
        vol_ma = volatility.mean()
        vol_std = volatility.std()
        vol_z_score = (current_vol - vol_ma) / vol_std
        
        # 判断风险等级
        risk_level = 'LOW'
        if vol_z_score > self.risk_thresholds['volatility_spike']:
            risk_level = 'HIGH'
        elif vol_z_score > self.risk_thresholds['volatility_spike'] * 0.7:
            risk_level = 'MEDIUM'
        
        return {
            'risk_level': risk_level,
            'volatility': current_vol,
            'vol_z_score': vol_z_score
        }
    
    def _calculate_overall_risk(self, risk_status: Dict[str, Any]) -> Dict[str, Any]:
        """计算综合风险"""
        risk_levels = [r['risk_level'] for r in risk_status.values()]
        
        # 综合风险等级
        if 'HIGH' in risk_levels:
            overall_level = 'HIGH'
        elif 'MEDIUM' in risk_levels:
            overall_level = 'MEDIUM'
        else:
            overall_level = 'LOW'
        
        # 风险评分
        risk_score = risk_levels.count('HIGH') * 3 + \
                    risk_levels.count('MEDIUM') * 2 + \
                    risk_levels.count('LOW') * 1
        risk_score = risk_score / len(risk_levels)
        
        return {
            'overall_level': overall_level,
            'risk_score': risk_score
        }
```

### 2. 风险预警器

```python
class RiskAlerter:
    """风险预警器"""
    
    def __init__(self):
        self.alert_channels = []
        
    def check_and_alert(self, risk_status: Dict[str, Any]) -> List[Dict[str, Any]]:
        """检查并发送预警"""
        alerts = []
        
        # 检查价格风险
        if risk_status['price_risk']['risk_level'] == 'HIGH':
            alerts.append({
                'alert_type': 'PRICE_RISK',
                'severity': 'HIGH',
                'message': f"组合亏损达到{risk_status['price_risk']['portfolio_loss']:.2%}",
                'timestamp': pd.Timestamp.now()
            })
        
        # 检查仓位风险
        if risk_status['position_risk']['risk_level'] == 'HIGH':
            alerts.append({
                'alert_type': 'POSITION_RISK',
                'severity': 'HIGH',
                'message': f"总仓位达到{risk_status['position_risk']['total_position']:.2%}",
                'timestamp': pd.Timestamp.now()
            })
        
        # 检查流动性风险
        if risk_status['liquidity_risk']['risk_level'] == 'HIGH':
            alerts.append({
                'alert_type': 'LIQUIDITY_RISK',
                'severity': 'HIGH',
                'message': f"成交量萎缩至{risk_status['liquidity_risk']['volume_ratio']:.2%}",
                'timestamp': pd.Timestamp.now()
            })
        
        # 检查波动率风险
        if risk_status['volatility_risk']['risk_level'] == 'HIGH':
            alerts.append({
                'alert_type': 'VOLATILITY_RISK',
                'severity': 'HIGH',
                'message': f"波动率飙升，Z-Score={risk_status['volatility_risk']['vol_z_score']:.2f}",
                'timestamp': pd.Timestamp.now()
            })
        
        # 发送预警
        for alert in alerts:
            self._send_alert(alert)
        
        return alerts
    
    def _send_alert(self, alert: Dict[str, Any]) -> None:
        """发送预警"""
        for channel in self.alert_channels:
            channel.send(alert)
```

### 3. 风险处置器

```python
class RiskHandler:
    """风险处置器"""
    
    def __init__(self, order_executor):
        self.order_executor = order_executor
        self.handlers = {
            'PRICE_RISK': self._handle_price_risk,
            'POSITION_RISK': self._handle_position_risk,
            'LIQUIDITY_RISK': self._handle_liquidity_risk,
            'VOLATILITY_RISK': self._handle_volatility_risk
        }
        
    def handle(self, alert: Dict[str, Any], positions: Dict[str, float]) -> None:
        """处置风险"""
        alert_type = alert['alert_type']
        
        if alert_type in self.handlers:
            self.handlersalert_type
    
    def _handle_price_risk(self, alert: Dict[str, Any], positions: Dict[str, float]) -> None:
        """处置价格风险"""
        # 减仓50%
        for symbol, position in positions.items():
            reduce_amount = position['quantity'] * 0.5
            self.order_executor.sell(symbol, reduce_amount)
    
    def _handle_position_risk(self, alert: Dict[str, Any], positions: Dict[str, float]) -> None:
        """处置仓位风险"""
        # 限制开仓
        self.order_executor.set_max_position(0.90)
    
    def _handle_liquidity_risk(self, alert: Dict[str, Any], positions: Dict[str, float]) -> None:
        """处置流动性风险"""
        # 暂停交易
        self.order_executor.pause()
    
    def _handle_volatility_risk(self, alert: Dict[str, Any], positions: Dict[str, float]) -> None:
        """处置波动率风险"""
        # 降低仓位
        for symbol, position in positions.items():
            reduce_amount = position['quantity'] * 0.3
            self.order_executor.sell(symbol, reduce_amount)
```

---

## 📋 风险控制机制详解

### 1. 风险控制层次架构

```
┌─────────────────────────────────────────────────────────────┐
│                   风险控制三层架构                           │
├─────────────────────────────────────────────────────────────┤
│                                                            │
│  ┌──────────────────────────────────────────────────────┐  │
│  │       第一层：事前风险控制                            │  │
│  │ - 仓位限制检查                                        │  │
│  │ - 集中度限制                                          │  │
│  │ - 行业暴露限制                                        │  │
│  │ - 因子暴露限制                                        │  │
│  └──────────────────────────────────────────────────────┘  │
│                          ↓                                 │
│  ┌──────────────────────────────────────────────────────┐  │
│  │       第二层：事中风险控制                            │  │
│  │ - 实时风险监控                                        │  │
│  │ - 动态止损检查                                        │  │
│  │ - 异常交易检测                                        │  │
│  │ - 流动性监控                                          │  │
│  └──────────────────────────────────────────────────────┘  │
│                          ↓                                 │
│  ┌──────────────────────────────────────────────────────┐  │
│  │       第三层：事后风险控制                            │  │
│  │ - 风险报告生成                                        │  │
│  │ - 风险归因分析                                        │  │
│  │ - 风险事件复盘                                        │  │
│  │ - 风险模型优化                                        │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                            │
└─────────────────────────────────────────────────────────────┘
```

### 2. 风险阈值配置体系

#### 2.1 风险阈值分类

| 阈值类型 | 阈值名称 | 默认值 | 触发条件 | 处置措施 |
|----------|----------|--------|----------|----------|
| **价格风险** | 单股票止损 | -5% | 单股票亏损超过阈值 | 减仓50% |
| **价格风险** | 组合止损 | -3% | 组合亏损超过阈值 | 全部平仓 |
| **价格风险** | 单日最大亏损 | -2% | 单日亏损超过阈值 | 暂停交易 |
| **仓位风险** | 单股票上限 | 10% | 单股票仓位超过阈值 | 限制开仓 |
| **仓位风险** | 总仓位上限 | 95% | 总仓位超过阈值 | 限制开仓 |
| **仓位风险** | 行业上限 | 30% | 行业仓位超过阈值 | 限制开仓 |
| **流动性风险** | 成交量萎缩 | 50% | 成交量低于阈值 | 暂停交易 |
| **流动性风险** | 换手率异常 | 3σ | 换手率异常 | 风险预警 |
| **波动率风险** | 波动率飙升 | 3σ | 波动率超过阈值 | 降低仓位 |
| **波动率风险** | 相关性突变 | 0.8 | 相关性超过阈值 | 风险预警 |

#### 2.2 风险阈值配置文件

```yaml
# risk_thresholds.yaml
risk_thresholds:
  price_risk:
    single_stock_loss:
      warning: -0.03
      critical: -0.05
      action: "reduce_position_50%"
      
    portfolio_loss:
      warning: -0.02
      critical: -0.03
      action: "close_all_positions"
      
    daily_max_loss:
      warning: -0.015
      critical: -0.02
      action: "pause_trading"
      
  position_risk:
    single_stock_position:
      warning: 0.08
      critical: 0.10
      action: "limit_open"
      
    total_position:
      warning: 0.90
      critical: 0.95
      action: "limit_open"
      
    sector_position:
      warning: 0.25
      critical: 0.30
      action: "limit_open"
      
  liquidity_risk:
    volume_drop:
      warning: 0.70
      critical: 0.50
      action: "pause_trading"
      
    turnover_anomaly:
      warning: 2.0
      critical: 3.0
      action: "alert"
      
  volatility_risk:
    volatility_spike:
      warning: 2.0
      critical: 3.0
      action: "reduce_position_30%"
      
    correlation_spike:
      warning: 0.6
      critical: 0.8
      action: "alert"
```

### 3. 风险处置流程

#### 3.1 风险处置决策树

```
风险事件触发
    │
    ├── 价格风险
    │   ├── 单股票亏损 > 5%
    │   │   └── 执行：减仓50%
    │   ├── 组合亏损 > 3%
    │   │   └── 执行：全部平仓
    │   └── 单日亏损 > 2%
    │       └── 执行：暂停交易
    │
    ├── 仓位风险
    │   ├── 单股票仓位 > 10%
    │   │   └── 执行：限制开仓
    │   ├── 总仓位 > 95%
    │   │   └── 执行：限制开仓
    │   └── 行业仓位 > 30%
    │       └── 执行：限制开仓
    │
    ├── 流动性风险
    │   ├── 成交量萎缩 < 50%
    │   │   └── 执行：暂停交易
    │   └── 换手率异常 > 3σ
    │       └── 执行：风险预警
    │
    └── 波动率风险
        ├── 波动率飙升 > 3σ
        │   └── 执行：降低仓位30%
        └── 相关性突变 > 0.8
            └── 执行：风险预警
```

#### 3.2 风险处置执行器

```python
class RiskActionExecutor:
    """风险处置执行器"""
    
    def __init__(self, order_manager, position_manager):
        self.order_manager = order_manager
        self.position_manager = position_manager
        self.action_handlers = {
            "reduce_position_50%": self._reduce_position_50,
            "reduce_position_30%": self._reduce_position_30,
            "close_all_positions": self._close_all_positions,
            "limit_open": self._limit_open,
            "pause_trading": self._pause_trading,
            "alert": self._send_alert
        }
    
    def execute(self, action: str, context: Dict[str, Any]) -> bool:
        """执行风险处置动作"""
        if action in self.action_handlers:
            return self.action_handlers[action](context)
        return False
    
    def _reduce_position_50(self, context: Dict[str, Any]) -> bool:
        """减仓50%"""
        symbol = context.get("symbol")
        position = self.position_manager.get_position(symbol)
        reduce_quantity = position.quantity * 0.5
        return self.order_manager.sell(symbol, reduce_quantity)
    
    def _reduce_position_30(self, context: Dict[str, Any]) -> bool:
        """减仓30%"""
        for symbol, position in self.position_manager.get_all_positions().items():
            reduce_quantity = position.quantity * 0.3
            self.order_manager.sell(symbol, reduce_quantity)
        return True
    
    def _close_all_positions(self, context: Dict[str, Any]) -> bool:
        """全部平仓"""
        for symbol, position in self.position_manager.get_all_positions().items():
            self.order_manager.sell(symbol, position.quantity)
        return True
    
    def _limit_open(self, context: Dict[str, Any]) -> bool:
        """限制开仓"""
        self.order_manager.set_open_limit(True)
        return True
    
    def _pause_trading(self, context: Dict[str, Any]) -> bool:
        """暂停交易"""
        self.order_manager.pause()
        return True
    
    def _send_alert(self, context: Dict[str, Any]) -> bool:
        """发送预警"""
        alert_manager = AlertManager()
        return alert_manager.send(context)
```

### 4. 风险监控指标体系

#### 4.1 实时监控指标

| 指标类别 | 指标名称 | 计算方法 | 监控频率 | 预警阈值 |
|----------|----------|----------|----------|----------|
| **价格风险** | 单股票亏损 | (当前价-成本价)/成本价 | 实时 | -5% |
| **价格风险** | 组合亏损 | Σ(单股票亏损×权重) | 实时 | -3% |
| **价格风险** | 最大回撤 | (峰值-当前)/峰值 | 每分钟 | -10% |
| **仓位风险** | 单股票仓位 | 市值/总资产 | 实时 | 10% |
| **仓位风险** | 总仓位 | 股票市值/总资产 | 实时 | 95% |
| **仓位风险** | 行业集中度 | 行业市值/总资产 | 每分钟 | 30% |
| **流动性风险** | 成交量比率 | 当前成交量/20日均值 | 实时 | 50% |
| **流动性风险** | 换手率 | 成交量/流通股本 | 每分钟 | 3σ |
| **波动率风险** | 波动率 | 收益率标准差×√252 | 每分钟 | 3σ |
| **波动率风险** | 相关性 | 股票间相关系数 | 每分钟 | 0.8 |

#### 4.2 监控指标计算器

```python
class RiskMetricsCalculator:
    """风险指标计算器"""
    
    def calculate_price_risk_metrics(
        self,
        positions: Dict[str, Position],
        market_data: pd.DataFrame
    ) -> Dict[str, float]:
        """计算价格风险指标"""
        metrics = {}
        
        total_value = sum(p.market_value for p in positions.values())
        
        single_stock_losses = {}
        for symbol, position in positions.items():
            if symbol in market_data.columns:
                current_price = market_data[symbol].iloc[-1]
                loss = (current_price - position.cost_price) / position.cost_price
                single_stock_losses[symbol] = loss
        
        metrics["single_stock_losses"] = single_stock_losses
        metrics["max_single_loss"] = min(single_stock_losses.values())
        metrics["portfolio_loss"] = sum(
            loss * positions[symbol].market_value / total_value
            for symbol, loss in single_stock_losses.items()
        )
        
        return metrics
    
    def calculate_position_risk_metrics(
        self,
        positions: Dict[str, Position]
    ) -> Dict[str, float]:
        """计算仓位风险指标"""
        metrics = {}
        
        total_value = sum(p.market_value for p in positions.values())
        
        single_positions = {
            symbol: p.market_value / total_value
            for symbol, p in positions.items()
        }
        
        metrics["single_positions"] = single_positions
        metrics["max_single_position"] = max(single_positions.values())
        metrics["total_position"] = sum(single_positions.values())
        
        return metrics
    
    def calculate_liquidity_risk_metrics(
        self,
        market_data: pd.DataFrame
    ) -> Dict[str, float]:
        """计算流动性风险指标"""
        metrics = {}
        
        volume_ma = market_data["volume"].rolling(20).mean()
        current_volume = market_data["volume"].iloc[-1]
        
        metrics["volume_ratio"] = current_volume / volume_ma.iloc[-1]
        
        turnover = market_data["volume"] / market_data["shares_outstanding"]
        turnover_ma = turnover.rolling(20).mean()
        turnover_std = turnover.rolling(20).std()
        
        metrics["turnover_zscore"] = (
            turnover.iloc[-1] - turnover_ma.iloc[-1]
        ) / turnover_std.iloc[-1]
        
        return metrics
    
    def calculate_volatility_risk_metrics(
        self,
        market_data: pd.DataFrame
    ) -> Dict[str, float]:
        """计算波动率风险指标"""
        metrics = {}
        
        returns = market_data["close"].pct_change()
        volatility = returns.rolling(20).std() * np.sqrt(252 * 240)
        
        vol_ma = volatility.mean()
        vol_std = volatility.std()
        
        metrics["volatility"] = volatility.iloc[-1]
        metrics["vol_zscore"] = (volatility.iloc[-1] - vol_ma) / vol_std
        
        returns_df = market_data.pct_change()
        correlation_matrix = returns_df.rolling(20).corr()
        
        metrics["max_correlation"] = correlation_matrix.max().max()
        
        return metrics
```

### 5. 风险报告模板

#### 5.1 日报模板

```markdown
# 风险控制日报

## 1. 风险概况
- **日期**: {date}
- **整体风险等级**: {overall_risk_level}
- **风险评分**: {risk_score}

## 2. 风险指标
| 指标 | 当前值 | 阈值 | 状态 |
|------|--------|------|------|
| 组合亏损 | {portfolio_loss:.2%} | -3% | {status} |
| 最大回撤 | {max_drawdown:.2%} | -10% | {status} |
| 总仓位 | {total_position:.2%} | 95% | {status} |
| 波动率 | {volatility:.2%} | 3σ | {status} |

## 3. 风险事件
{risk_events}

## 4. 处置记录
{action_records}

## 5. 建议
{recommendations}
```

---

## 🚀 实施要点

### 阶段1：实时风险监控器开发（第1周）

**任务**:
1. ✅ 实现价格风险监控
2. ✅ 实现仓位风险监控
3. ✅ 实现流动性风险监控
4. ✅ 实现波动率风险监控
5. ✅ 编写单元测试

---

### 阶段2：风险预警器开发（第1-2周）

**任务**:
1. ✅ 实现风险预警逻辑
2. ✅ 实现多通道预警
3. ✅ 实现预警历史记录
4. ✅ 编写单元测试

---

### 阶段3：风险处置器开发（第2-3周）

**任务**:
1. ✅ 实现价格风险处置
2. ✅ 实现仓位风险处置
3. ✅ 实现流动性风险处置
4. ✅ 实现波动率风险处置
5. ✅ 集成测试

---

## 📈 性能指标

### 风控性能要求

| 指标 | 目标值 |
|------|--------|
| **监控延迟** | < 1秒 |
| **预警准确率** | ≥ 90% |
| **处置响应时间** | < 5秒 |
| **误报率** | < 5% |

---

## 🔗 相关文档

- [开盘策略模块蓝图](./OPENING_STRATEGY_BLUEPRINT.md)
- [盘中策略模块蓝图](./INTRADAY_STRATEGY_BLUEPRINT.md)
- 专业多时间框架策略架构

---

## 📝 变更历史

| 版本 | 日期 | 变更内容 | 作者 |
|------|------|---------|------|
| v1.0.0 | 2026-04-06 | 初始版本创建 | 首席架构师 |

---

**蓝图状态**: ✅ 设计完成
**下一步**: 开始实施阶段1 - 实时风险监控器开发
---

## 1. 文档治理

### 1.1 System_Manifest.md索引

```markdown
#### Layer 1: 微观执行层
##### 6.001. Risk Control
- **模块ID**: RISK_CONTROL_001
- **蓝图文档**: RISK_CONTROL_BLUEPRINT.md
- **技术规格书**: 待创建
- **职责**: 微观执行层实时风控
- **状态**: Active
```

### 1.2 模块职责边界

| 模块 | 职责 | 边界 |
|------|------|------|
| **Risk Control** | 微观执行层实时风控 | **核心模块** |

### 1.3 版本管理

| 版本 | 日期 | 变更内容 | 变更人 |
|------|------|----------|--------|
| v1.0.0 | 2026-04-06 | 初始版本创建 | 首席蓝图架构师 |

---

**蓝图版本**: v1.0.0 | **创建日期**: 2026-04-06 | **状态**: Active
