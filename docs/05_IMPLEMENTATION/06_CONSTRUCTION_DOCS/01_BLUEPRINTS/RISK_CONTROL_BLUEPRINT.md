---
responsibility:
  - é£é©æ§å¶
  - é£é©éé¢ç®¡ç
  - é£é©çæ§
  - é£é©é¢è­¦

module_id: RISK_CONTROL_001
version: 1.0.0
status: Active
created_date: 2026-04-07
last_updated: 2026-04-07
owner: å®æ½å¢é
standard_type: ä¸ä¸éåæºæèå¾
applicable_scope: Layer 6 ç»åä¼åå±?
compliance_level: ä¸ä¸æ å
layer: Layer 5.3 (风险管理)
---


## 核心定位

负责风险控制的设计与实现，定义风险限额和控制规则，提供风险监控和预警功能，支持风险管理。

# é£é©æ§å¶èå¾

> **æ ¸å¿èè´£**: ç»åä¼åå±å®æ¶é£é©æ§å?
> **èè´£è¾¹ç**: 
> - â?æ¬ææ¡£è´è´£ï¼å®æ¶çæ§ãé£é©é¢è­¦ãé£é©æ§å?
> - â?æ¬ææ¡£ä¸è´è´£ï¼å å­è®¡ç®ï¼ç±å å­æ¨¡åè´è´£ï¼
| **é£é©å¤ç½®** | æ§è¡é£é©å¤ç½®æªæ½ | å¤ç½®è®°å½ |
| **é£é©æ¥å** | çæé£é©æ¥å | é£é©æ¥å |

---
## 设计目标

### 主要目标

1. **功能完整性**: 确保RISK CONTROL功能完整，满足业务需求
2. **性能优化**: 提升系统性能，降低资源消耗
3. **可维护性**: 提高代码质量，便于后续维护
4. **可扩展性**: 支持功能扩展，适应业务变化

### 质量目标

- 代码覆盖率: ≥80%
- 性能指标: 满足设计要求
- 文档完整性: 100%


## 核心功能

### 功能清单

1. **数据管理**: 提供数据存储、查询、更新功能
2. **业务逻辑**: 实现核心业务逻辑处理
3. **接口服务**: 提供标准化的API接口
4. **监控告警**: 实时监控系统状态

### 功能特性

- 高可用性设计
- 自动故障恢复
- 灵活配置管理


## 实现方案

### 技术架构

采用RISK CONTROL化设计，分层架构实现。

### 关键技术

- 数据处理: 使用高效的数据处理框架
- 接口实现: RESTful API设计
- 性能优化: 缓存、异步处理

### 实施步骤

1. 需求分析与设计
2. 核心功能开发
3. 测试与优化
4. 部署与监控


## æ ¸å¿å®ä½

å¼åRISK CONTROLçè®¾è®¡ä¸å®ç°ï¼åºäºRiskMetricsææ¯ï¼çæ§æ ¸å¿åè½ï¼ä¿éèµäº§å®å¨ã?

## ðï¸?æ¶æè®¾è®¡

### é£é©æ§å¶ç»´åº¦

| é£é©ç»´åº¦ | é£é©ææ  | éå?| å¤ç½®æªæ½ |
|---------|---------|------|---------|
| **ä»·æ ¼é£é©** | åè¡ç¥¨äºæ?| > 5% | åä»50% |
| **ä»·æ ¼é£é©** | ç»åäºæ | > 3% | å¨é¨å¹³ä» |
| **ä»ä½é£é©** | åè¡ç¥¨ä»ä½?| > 10% | éå¶å¼ä»?|
| **ä»ä½é£é©** | æ»ä»ä½?| > 95% | éå¶å¼ä»?|
| **æµå¨æ§é£é?* | æäº¤éèç¼?| < 50% | æåäº¤æ |
| **æ³¢å¨çé£é?* | æ³¢å¨çé£å?| > 3Ï | éä½ä»ä½ |

---

## ð§ å³é®ç»ä»¶è®¾è®¡

### 1. å®æ¶é£é©çæ§å?

```python
from typing import Dict, Any
import pandas as pd
import numpy as np
import redis

class RealtimeRiskMonitor:
    """å®æ¶é£é©çæ§å?""
    
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
        """å®æ¶çæ§é£é©"""
        risk_status = {}
        
        # çæ§ä»·æ ¼é£é©
        price_risk = self._monitor_price_risk(positions, market_data)
        risk_status['price_risk'] = price_risk
        
        # çæ§ä»ä½é£é©
        position_risk = self._monitor_position_risk(positions)
        risk_status['position_risk'] = position_risk
        
        # çæ§æµå¨æ§é£é?
        liquidity_risk = self._monitor_liquidity_risk(market_data)
        risk_status['liquidity_risk'] = liquidity_risk
        
        # çæ§æ³¢å¨çé£é?
        volatility_risk = self._monitor_volatility_risk(market_data)
        risk_status['volatility_risk'] = volatility_risk
        
        # ç»¼åé£é©è¯ä¼°
        overall_risk = self._calculate_overall_risk(risk_status)
        risk_status['overall_risk'] = overall_risk
        
        # å­å¨å°Redis
        self.redis.setex('risk_status', 60, str(risk_status))
        
        return risk_status
    
    def _monitor_price_risk(self,
                           positions: Dict[str, float],
                           market_data: pd.DataFrame) -> Dict[str, Any]:
        """çæ§ä»·æ ¼é£é©"""
        # è®¡ç®åè¡ç¥¨äºæ?
        single_stock_losses = {}
        for symbol, position in positions.items():
            if symbol in market_data.columns:
                current_price = market_data[symbol].iloc[-1]
                cost_price = position['cost_price']
                loss = (current_price - cost_price) / cost_price
                single_stock_losses[symbol] = loss
        
        # è®¡ç®ç»åäºæ
        portfolio_loss = np.mean(list(single_stock_losses.values()))
        
        # å¤æ­é£é©ç­çº§
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
        """çæ§ä»ä½é£é©"""
        # è®¡ç®åè¡ç¥¨ä»ä½?
        total_value = sum(p['market_value'] for p in positions.values())
        single_stock_positions = {
            symbol: p['market_value'] / total_value
            for symbol, p in positions.items()
        }
        
        # è®¡ç®æ»ä»ä½?
        total_position = sum(single_stock_positions.values())
        
        # å¤æ­é£é©ç­çº§
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
        """çæ§æµå¨æ§é£é?""
        # è®¡ç®æäº¤éåå?
        volume_ma = market_data['volume'].rolling(20).mean()
        current_volume = market_data['volume'].iloc[-1]
        volume_ratio = current_volume / volume_ma.iloc[-1]
        
        # å¤æ­é£é©ç­çº§
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
        """çæ§æ³¢å¨çé£é?""
        # è®¡ç®æ³¢å¨ç?
        returns = market_data['close'].pct_change()
        volatility = returns.rolling(20).std() * np.sqrt(252 * 240)
        
        # è®¡ç®æ³¢å¨çZ-Score
        current_vol = volatility.iloc[-1]
        vol_ma = volatility.mean()
        vol_std = volatility.std()
        vol_z_score = (current_vol - vol_ma) / vol_std
        
        # å¤æ­é£é©ç­çº§
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
        """è®¡ç®ç»¼åé£é©"""
        risk_levels = [r['risk_level'] for r in risk_status.values()]
        
        # ç»¼åé£é©ç­çº§
        if 'HIGH' in risk_levels:
            overall_level = 'HIGH'
        elif 'MEDIUM' in risk_levels:
            overall_level = 'MEDIUM'
        else:
            overall_level = 'LOW'
        
        # é£é©è¯å
        risk_score = risk_levels.count('HIGH') * 3 + \
                    risk_levels.count('MEDIUM') * 2 + \
                    risk_levels.count('LOW') * 1
        risk_score = risk_score / len(risk_levels)
        
        return {
            'overall_level': overall_level,
            'risk_score': risk_score
        }
```

### 2. é£é©é¢è­¦å?

```python
class RiskAlerter:
    """é£é©é¢è­¦å?""
    
    def __init__(self):
        self.alert_channels = []
        
    def check_and_alert(self, risk_status: Dict[str, Any]) -> List[Dict[str, Any]]:
        """æ£æ¥å¹¶åéé¢è­?""
        alerts = []
        
        # æ£æ¥ä»·æ ¼é£é?
        if risk_status['price_risk']['risk_level'] == 'HIGH':
            alerts.append({
                'alert_type': 'PRICE_RISK',
                'severity': 'HIGH',
                'message': f"ç»åäºæè¾¾å°{risk_status['price_risk']['portfolio_loss']:.2%}",
                'timestamp': pd.Timestamp.now()
            })
        
        # æ£æ¥ä»ä½é£é?
        if risk_status['position_risk']['risk_level'] == 'HIGH':
            alerts.append({
                'alert_type': 'POSITION_RISK',
                'severity': 'HIGH',
                'message': f"æ»ä»ä½è¾¾å°{risk_status['position_risk']['total_position']:.2%}",
                'timestamp': pd.Timestamp.now()
            })
        
        # æ£æ¥æµå¨æ§é£é?
        if risk_status['liquidity_risk']['risk_level'] == 'HIGH':
            alerts.append({
                'alert_type': 'LIQUIDITY_RISK',
                'severity': 'HIGH',
                'message': f"æäº¤éèç¼©è³{risk_status['liquidity_risk']['volume_ratio']:.2%}",
                'timestamp': pd.Timestamp.now()
            })
        
        # æ£æ¥æ³¢å¨çé£é©
        if risk_status['volatility_risk']['risk_level'] == 'HIGH':
            alerts.append({
                'alert_type': 'VOLATILITY_RISK',
                'severity': 'HIGH',
                'message': f"æ³¢å¨çé£åï¼Z-Score={risk_status['volatility_risk']['vol_z_score']:.2f}",
                'timestamp': pd.Timestamp.now()
            })
        
        # åéé¢è­?
        for alert in alerts:
            self._send_alert(alert)
        
        return alerts
    
    def _send_alert(self, alert: Dict[str, Any]) -> None:
        """åéé¢è­?""
        for channel in self.alert_channels:
            channel.send(alert)
```

### 3. é£é©å¤ç½®å?

```python
class RiskHandler:
    """é£é©å¤ç½®å?""
    
    def __init__(self, order_executor):
        self.order_executor = order_executor
        self.handlers = {
            'PRICE_RISK': self._handle_price_risk,
            'POSITION_RISK': self._handle_position_risk,
            'LIQUIDITY_RISK': self._handle_liquidity_risk,
            'VOLATILITY_RISK': self._handle_volatility_risk
        }
        
    def handle(self, alert: Dict[str, Any], positions: Dict[str, float]) -> None:
        """å¤ç½®é£é©"""
        alert_type = alert['alert_type']
        
        if alert_type in self.handlers:
            self.handlersalert_type
    
    def _handle_price_risk(self, alert: Dict[str, Any], positions: Dict[str, float]) -> None:
        """å¤ç½®ä»·æ ¼é£é©"""
        # åä»50%
        for symbol, position in positions.items():
            reduce_amount = position['quantity'] * 0.5
            self.order_executor.sell(symbol, reduce_amount)
    
    def _handle_position_risk(self, alert: Dict[str, Any], positions: Dict[str, float]) -> None:
        """å¤ç½®ä»ä½é£é©"""
        # éå¶å¼ä»?
        self.order_executor.set_max_position(0.90)
    
    def _handle_liquidity_risk(self, alert: Dict[str, Any], positions: Dict[str, float]) -> None:
        """å¤ç½®æµå¨æ§é£é?""
        # æåäº¤æ
        self.order_executor.pause()
    
    def _handle_volatility_risk(self, alert: Dict[str, Any], positions: Dict[str, float]) -> None:
        """å¤ç½®æ³¢å¨çé£é?""
        # éä½ä»ä½
        for symbol, position in positions.items():
            reduce_amount = position['quantity'] * 0.3
            self.order_executor.sell(symbol, reduce_amount)
```

---

## ð é£é©æ§å¶æºå¶è¯¦è§£

### 1. é£é©æ§å¶å±æ¬¡æ¶æ

```
âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ?
â?                  é£é©æ§å¶ä¸å±æ¶æ                           â?
âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ?
â?                                                           â?
â? ââââââââââââââââââââââââââââââââââââââââââââââââââââââââ? â?
â? â?      ç¬¬ä¸å±ï¼äºåé£é©æ§å¶                            â? â?
â? â?- ä»ä½éå¶æ£æ?                                       â? â?
â? â?- éä¸­åº¦éå?                                         â? â?
â? â?- è¡ä¸æ´é²éå¶                                        â? â?
â? â?- å å­æ´é²éå¶                                        â? â?
â? ââââââââââââââââââââââââââââââââââââââââââââââââââââââââ? â?
â?                         â?                                â?
â? ââââââââââââââââââââââââââââââââââââââââââââââââââââââââ? â?
â? â?      ç¬¬äºå±ï¼äºä¸­é£é©æ§å¶                            â? â?
â? â?- å®æ¶é£é©çæ§                                        â? â?
â? â?- å¨ææ­¢ææ£æ?                                       â? â?
â? â?- å¼å¸¸äº¤ææ£æµ?                                       â? â?
â? â?- æµå¨æ§çæ?                                         â? â?
â? ââââââââââââââââââââââââââââââââââââââââââââââââââââââââ? â?
â?                         â?                                â?
â? ââââââââââââââââââââââââââââââââââââââââââââââââââââââââ? â?
â? â?      ç¬¬ä¸å±ï¼äºåé£é©æ§å¶                            â? â?
â? â?- é£é©æ¥åçæ                                        â? â?
â? â?- é£é©å½å åæ                                        â? â?
â? â?- é£é©äºä»¶å¤ç                                        â? â?
â? â?- é£é©æ¨¡åä¼å                                        â? â?
â? ââââââââââââââââââââââââââââââââââââââââââââââââââââââââ? â?
â?                                                           â?
âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ?
```

### 2. é£é©éå¼éç½®ä½ç³?

#### 2.1 é£é©éå¼åç±?

| éå¼ç±»å?| éå¼åç§?| é»è®¤å?| è§¦åæ¡ä»¶ | å¤ç½®æªæ½ |
|----------|----------|--------|----------|----------|
| **ä»·æ ¼é£é©** | åè¡ç¥¨æ­¢æ?| -5% | åè¡ç¥¨äºæè¶è¿éå?| åä»50% |
| **ä»·æ ¼é£é©** | ç»åæ­¢æ | -3% | ç»åäºæè¶è¿éå?| å¨é¨å¹³ä» |
| **ä»·æ ¼é£é©** | åæ¥æå¤§äºæ?| -2% | åæ¥äºæè¶è¿éå?| æåäº¤æ |
| **ä»ä½é£é©** | åè¡ç¥¨ä¸é?| 10% | åè¡ç¥¨ä»ä½è¶è¿éå?| éå¶å¼ä»?|
| **ä»ä½é£é©** | æ»ä»ä½ä¸é?| 95% | æ»ä»ä½è¶è¿éå?| éå¶å¼ä»?|
| **ä»ä½é£é©** | è¡ä¸ä¸é | 30% | è¡ä¸ä»ä½è¶è¿éå?| éå¶å¼ä»?|
| **æµå¨æ§é£é?* | æäº¤éèç¼?| 50% | æäº¤éä½äºéå?| æåäº¤æ |
| **æµå¨æ§é£é?* | æ¢æçå¼å¸?| 3Ï | æ¢æçå¼å¸?| é£é©é¢è­¦ |
| **æ³¢å¨çé£é?* | æ³¢å¨çé£å?| 3Ï | æ³¢å¨çè¶è¿éå?| éä½ä»ä½ |
| **æ³¢å¨çé£é?* | ç¸å³æ§çªå?| 0.8 | ç¸å³æ§è¶è¿éå?| é£é©é¢è­¦ |

#### 2.2 é£é©éå¼éç½®æä»?

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

### 3. é£é©å¤ç½®æµç¨

#### 3.1 é£é©å¤ç½®å³ç­æ ?

```
é£é©äºä»¶è§¦å
    â?
    âââ ä»·æ ¼é£é©
    â?  âââ åè¡ç¥¨äºæ?> 5%
    â?  â?  âââ æ§è¡ï¼åä»?0%
    â?  âââ ç»åäºæ > 3%
    â?  â?  âââ æ§è¡ï¼å¨é¨å¹³ä»?
    â?  âââ åæ¥äºæ > 2%
    â?      âââ æ§è¡ï¼æåäº¤æ?
    â?
    âââ ä»ä½é£é©
    â?  âââ åè¡ç¥¨ä»ä½?> 10%
    â?  â?  âââ æ§è¡ï¼éå¶å¼ä»?
    â?  âââ æ»ä»ä½?> 95%
    â?  â?  âââ æ§è¡ï¼éå¶å¼ä»?
    â?  âââ è¡ä¸ä»ä½ > 30%
    â?      âââ æ§è¡ï¼éå¶å¼ä»?
    â?
    âââ æµå¨æ§é£é?
    â?  âââ æäº¤éèç¼?< 50%
    â?  â?  âââ æ§è¡ï¼æåäº¤æ?
    â?  âââ æ¢æçå¼å¸?> 3Ï
    â?      âââ æ§è¡ï¼é£é©é¢è­?
    â?
    âââ æ³¢å¨çé£é?
        âââ æ³¢å¨çé£å?> 3Ï
        â?  âââ æ§è¡ï¼éä½ä»ä½?0%
        âââ ç¸å³æ§çªå?> 0.8
            âââ æ§è¡ï¼é£é©é¢è­?
```

#### 3.2 é£é©å¤ç½®æ§è¡å?

```python
class RiskActionExecutor:
    """é£é©å¤ç½®æ§è¡å?""
    
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
        """æ§è¡é£é©å¤ç½®å¨ä½"""
        if action in self.action_handlers:
            return self.action_handlers[action](context)
        return False
    
    def _reduce_position_50(self, context: Dict[str, Any]) -> bool:
        """åä»50%"""
        symbol = context.get("symbol")
        position = self.position_manager.get_position(symbol)
        reduce_quantity = position.quantity * 0.5
        return self.order_manager.sell(symbol, reduce_quantity)
    
    def _reduce_position_30(self, context: Dict[str, Any]) -> bool:
        """åä»30%"""
        for symbol, position in self.position_manager.get_all_positions().items():
            reduce_quantity = position.quantity * 0.3
            self.order_manager.sell(symbol, reduce_quantity)
        return True
    
    def _close_all_positions(self, context: Dict[str, Any]) -> bool:
        """å¨é¨å¹³ä»"""
        for symbol, position in self.position_manager.get_all_positions().items():
            self.order_manager.sell(symbol, position.quantity)
        return True
    
    def _limit_open(self, context: Dict[str, Any]) -> bool:
        """éå¶å¼ä»?""
        self.order_manager.set_open_limit(True)
        return True
    
    def _pause_trading(self, context: Dict[str, Any]) -> bool:
        """æåäº¤æ"""
        self.order_manager.pause()
        return True
    
    def _send_alert(self, context: Dict[str, Any]) -> bool:
        """åéé¢è­?""
        alert_manager = AlertManager()
        return alert_manager.send(context)
```

### 4. é£é©çæ§ææ ä½ç³»

#### 4.1 å®æ¶çæ§ææ 

| ææ ç±»å« | ææ åç§° | è®¡ç®æ¹æ³ | çæ§é¢ç | é¢è­¦éå?|
|----------|----------|----------|----------|----------|
| **ä»·æ ¼é£é©** | åè¡ç¥¨äºæ?| (å½åä»?ææ¬ä»?/ææ¬ä»?| å®æ¶ | -5% |
| **ä»·æ ¼é£é©** | ç»åäºæ | Î£(åè¡ç¥¨äºæÃæé? | å®æ¶ | -3% |
| **ä»·æ ¼é£é©** | æå¤§åæ?| (å³°å?å½å)/å³°å?| æ¯åé?| -10% |
| **ä»ä½é£é©** | åè¡ç¥¨ä»ä½?| å¸å?æ»èµäº?| å®æ¶ | 10% |
| **ä»ä½é£é©** | æ»ä»ä½?| è¡ç¥¨å¸å?æ»èµäº?| å®æ¶ | 95% |
| **ä»ä½é£é©** | è¡ä¸éä¸­åº?| è¡ä¸å¸å?æ»èµäº?| æ¯åé?| 30% |
| **æµå¨æ§é£é?* | æäº¤éæ¯ç?| å½åæäº¤é?20æ¥åå?| å®æ¶ | 50% |
| **æµå¨æ§é£é?* | æ¢æç?| æäº¤é?æµéè¡æ?| æ¯åé?| 3Ï |
| **æ³¢å¨çé£é?* | æ³¢å¨ç?| æ¶ççæ åå·®Ãâ?52 | æ¯åé?| 3Ï |
| **æ³¢å¨çé£é?* | ç¸å³æ?| è¡ç¥¨é´ç¸å³ç³»æ?| æ¯åé?| 0.8 |

#### 4.2 çæ§ææ è®¡ç®å?

```python
class RiskMetricsCalculator:
    """é£é©ææ è®¡ç®å?""
    
    def calculate_price_risk_metrics(
        self,
        positions: Dict[str, Position],
        market_data: pd.DataFrame
    ) -> Dict[str, float]:
        """è®¡ç®ä»·æ ¼é£é©ææ """
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
        """è®¡ç®ä»ä½é£é©ææ """
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
        """è®¡ç®æµå¨æ§é£é©ææ ?""
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
        """è®¡ç®æ³¢å¨çé£é©ææ ?""
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

### 5. é£é©æ¥åæ¨¡æ¿

#### 5.1 æ¥æ¥æ¨¡æ¿

```markdown
# é£é©æ§å¶æ¥æ¥

## 1. é£é©æ¦åµ
- **æ¥æ**: {date}
- **æ´ä½é£é©ç­çº§**: {overall_risk_level}
- **é£é©è¯å**: {risk_score}

## 2. é£é©ææ 
| ææ  | å½åå?| éå?| ç¶æ?|
|------|--------|------|------|
| ç»åäºæ | {portfolio_loss:.2%} | -3% | {status} |
| æå¤§åæ?| {max_drawdown:.2%} | -10% | {status} |
| æ»ä»ä½?| {total_position:.2%} | 95% | {status} |
| æ³¢å¨ç?| {volatility:.2%} | 3Ï | {status} |

## 3. é£é©äºä»¶
{risk_events}

## 4. å¤ç½®è®°å½
{action_records}

## 5. å»ºè®®
{recommendations}
```

---

## ð å®æ½è¦ç¹

### é¶æ®µ1ï¼å®æ¶é£é©çæ§å¨å¼åï¼ç¬?å¨ï¼

**ä»»å¡**:
1. â?å®ç°ä»·æ ¼é£é©çæ§
2. â?å®ç°ä»ä½é£é©çæ§
3. â?å®ç°æµå¨æ§é£é©çæ?
4. â?å®ç°æ³¢å¨çé£é©çæ?
5. â?ç¼åååæµè¯

---

### é¶æ®µ2ï¼é£é©é¢è­¦å¨å¼åï¼ç¬?-2å¨ï¼

**ä»»å¡**:
1. â?å®ç°é£é©é¢è­¦é»è¾
2. â?å®ç°å¤ééé¢è­¦
3. â?å®ç°é¢è­¦åå²è®°å½
4. â?ç¼åååæµè¯

---

### é¶æ®µ3ï¼é£é©å¤ç½®å¨å¼åï¼ç¬?-3å¨ï¼

**ä»»å¡**:
1. â?å®ç°ä»·æ ¼é£é©å¤ç½®
2. â?å®ç°ä»ä½é£é©å¤ç½®
3. â?å®ç°æµå¨æ§é£é©å¤ç½?
4. â?å®ç°æ³¢å¨çé£é©å¤ç½?
5. â?éææµè¯

---

## ð æ§è½ææ 

### é£æ§æ§è½è¦æ±

| ææ  | ç®æ å?|
|------|--------|
| **çæ§å»¶è¿** | < 1ç§?|
| **é¢è­¦åç¡®ç?* | â?90% |
| **å¤ç½®ååºæ¶é´** | < 5ç§?|
| **è¯¯æ¥ç?* | < 5% |

---

## ð ç¸å³ææ¡£

- [å¼çç­ç¥æ¨¡åèå¾](./OPENING_STRATEGY_BLUEPRINT.md)
- [çä¸­ç­ç¥æ¨¡åèå¾](./INTRADAY_STRATEGY_BLUEPRINT.md)
- ä¸ä¸å¤æ¶é´æ¡æ¶ç­ç¥æ¶æ?

---

## ð åæ´åå²

| çæ¬ | æ¥æ | åæ´åå®¹ | ä½è?|
|------|------|---------|------|
| v1.0.0 | 2026-04-06 | åå§çæ¬åå»º | é¦å¸­æ¶æå¸?|

---

**èå¾ç¶æ?*: â?è®¾è®¡å®æ
**ä¸ä¸æ­?*: å¼å§å®æ½é¶æ®? - å®æ¶é£é©çæ§å¨å¼å?
---

## 1. ææ¡£æ²»ç

### 1.1 System_Manifest.mdç´¢å¼

```markdown
#### Layer 1: å¾®è§æ§è¡å±?
##### 6.001. Risk Control
- **æ¨¡åID**: RISK_CONTROL_001
- **èå¾ææ¡£**: RISK_CONTROL_BLUEPRINT.md
- **ææ¯è§æ ¼ä¹¦**: å¾åå»?
- **èè´£**: å¾®è§æ§è¡å±å®æ¶é£æ?
- **ç¶æ?*: Active
```

### 1.2 æ¨¡åèè´£è¾¹ç

| æ¨¡å | èè´£ | è¾¹ç |
|------|------|------|
| **Risk Control** | å¾®è§æ§è¡å±å®æ¶é£æ?| **æ ¸å¿æ¨¡å** |

### 1.3 çæ¬ç®¡ç

| çæ¬ | æ¥æ | åæ´åå®¹ | åæ´äº?|
|------|------|----------|--------|
| v1.0.0 | 2026-04-06 | åå§çæ¬åå»º | é¦å¸­èå¾æ¶æå¸?|

---

**èå¾çæ¬**: v1.0.0 | **åå»ºæ¥æ**: 2026-04-06 | **ç¶æ?*: Active
