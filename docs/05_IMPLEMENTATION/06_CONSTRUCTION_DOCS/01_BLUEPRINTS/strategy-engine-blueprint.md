---
module_id: STRATEGY_ENGINE_001
version: 1.0.0
status: Active
priority: P0
created_date: 2026-04-07
last_updated: 2026-04-10
owner: 首席文档架构师
responsibility:
  - 策略执行
  - 信号生成
  - 策略调度
  - 策略生命周期管理
standard_type: 专业量化机构蓝图
compliance_level: 专业标准
layer: layer_05
audit_status: EXTRACT_TO_L0_REQUIRED
---

# 策略引擎蓝图

> **核心职责**: 提供策略执行的核心引擎，负责策略逻辑的执行、信号生成、策略调度和生命周期管理
> **职责边界**: 
> - ✅ 本文档负责：策略执行、信号生成、策略调度、策略生命周期管理
> - ❌ 本文档不负责：订单管理（由订单管理模块负责）、风控（由风控模块负责）、数据获取（由数据模块负责）
> 
> **下游模块**: 
> - 智能执行引擎（SMART_EXECUTION_ENGINE_001）：负责订单的智能执行和成本优化
> - 风险控制模块（RISK_CONTROL_001）：负责风险管理和控制
> - 订单管理模块：负责订单的生成和管理

## 核心定位

负责策略引擎模块的设计与构建，提供策略执行的核心能力，支持策略逻辑的执行、信号生成、策略调度和生命周期管理，是Layer 5策略执行层的核心模块。

## 设计目标

### 主要目标

1. **策略执行**: 执行策略逻辑，生成交易信号
2. **信号生成**: 根据策略逻辑生成买卖信号
3. **策略调度**: 调度多个策略的执行
4. **生命周期管理**: 管理策略的启动、停止、暂停等生命周期

### 质量目标

- 策略执行延迟: < 100ms
- 信号生成准确率: ≥ 95%
- 策略调度可靠性: ≥ 99.9%
- 系统可用性: ≥ 99.5%

## 开源方案选型

### 推荐方案: Backtrader

| 属性 | 详情 |
|------|------|
| **GitHub** | https://github.com/mementum/backtrader |
| **Stars** | 12,000+ |
| **License** | GPL 3.0 |
| **语言** | Python |
| **特点** | 功能全面的量化回测和实盘交易框架 |

**选择理由**:
1. **功能全面**: 支持回测、模拟、实盘交易
2. **易于使用**: Python语法简单，文档完善
3. **社区活跃**: 12k+ Stars，社区支持好
4. **可扩展**: 支持自定义策略、指标、分析器
5. **个人友好**: 免费开源，适合个人使用
6. **实盘支持**: 支持多种券商接口

**对比其他方案**:

| 方案 | Stars | 优点 | 缺点 | 推荐度 |
|------|-------|------|------|--------|
| **Backtrader** | 12k+ | 功能全面、支持实盘 | GPL 3.0协议 | ⭐⭐⭐⭐⭐ |
| **Zipline** | 17k+ | Quantopian出品、功能强大 | 不支持实盘、维护较少 | ⭐⭐⭐⭐ |
| **Vnpy** | 25k+ | 国内开源、功能全面 | 学习曲线陡峭 | ⭐⭐⭐⭐⭐ |
| **VectorBT** | 4k+ | 向量化、速度快 | 功能相对简单 | ⭐⭐⭐⭐ |

**最终选择**: Backtrader（功能全面、支持实盘、社区活跃）

## 核心功能设计

### 1. 策略执行引擎

```python
import backtrader as bt
from typing import Dict, List, Optional
from datetime import datetime
import logging

class StrategyEngine:
    """策略执行引擎"""
    
    def __init__(
        self,
        initial_cash: float = 1000000,
        commission: float = 0.001,
        slippage: float = 0.0001
    ):
        self.cerebro = bt.Cerebro()
        self.cerebro.broker.setcash(initial_cash)
        self.cerebro.broker.setcommission(commission=commission)
        self.cerebro.broker.set_slippage_perc(perc=slippage)
        
        self.strategies = {}
        self.data_feeds = {}
        self.analyzers = {}
        
        self.logger = logging.getLogger(__name__)
    
    def add_strategy(
        self,
        strategy_class: bt.Strategy,
        name: str,
        params: Optional[Dict] = None
    ):
        """添加策略"""
        params = params or {}
        
        self.strategies[name] = {
            "class": strategy_class,
            "params": params
        }
        
        self.cerebro.addstrategy(strategy_class, **params)
        
        self.logger.info(f"Added strategy: {name}")
    
    def add_data(
        self,
        data_feed: bt.feeds.DataBase,
        name: str
    ):
        """添加数据源"""
        self.data_feeds[name] = data_feed
        self.cerebro.adddata(data_feed, name=name)
        
        self.logger.info(f"Added data feed: {name}")
    
    def add_analyzer(
        self,
        analyzer_class: bt.Analyzer,
        name: str,
        params: Optional[Dict] = None
    ):
        """添加分析器"""
        params = params or {}
        
        self.analyzers[name] = {
            "class": analyzer_class,
            "params": params
        }
        
        self.cerebro.addanalyzer(analyzer_class, **params, _name=name)
        
        self.logger.info(f"Added analyzer: {name}")
    
    def run_backtest(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict:
        """运行回测"""
        self.logger.info("Starting backtest...")
        
        start_time = datetime.now()
        
        results = self.cerebro.run()
        
        end_time = datetime.now()
        
        duration = (end_time - start_time).total_seconds()
        
        final_value = self.cerebro.broker.getvalue()
        initial_cash = self.cerebro.broker.startingcash
        
        pnl = final_value - initial_cash
        pnl_pct = (pnl / initial_cash) * 100
        
        analysis_results = {}
        
        for name, analyzer_info in self.analyzers.items():
            analysis_results[name] = results[0].analyzers.getbyname(name).get_analysis()
        
        return {
            "initial_cash": initial_cash,
            "final_value": final_value,
            "pnl": pnl,
            "pnl_pct": pnl_pct,
            "duration_seconds": duration,
            "analyzers": analysis_results
        }
    
    def run_live(
        self,
        store: bt.stores.Store,
        strategy_name: str
    ):
        """运行实盘"""
        self.logger.info(f"Starting live trading for strategy: {strategy_name}")
        
        broker = store.getbroker()
        self.cerebro.setbroker(broker)
        
        data = store.getdata()
        self.cerebro.adddata(data)
        
        self.cerebro.run()
```

### 2. 策略基类设计

```python
import backtrader as bt
from typing import Dict, List

class BaseStrategy(bt.Strategy):
    """策略基类"""
    
    params = (
        ('stop_loss', 0.05),
        ('take_profit', 0.10),
        ('position_size', 0.1),
    )
    
    def __init__(self):
        self.dataclose = self.datas[0].close
        
        self.order = None
        self.buyprice = None
        self.buycomm = None
        
        self.signals = []
        
        self.indicators = {}
        
        self._init_indicators()
    
    def _init_indicators(self):
        """初始化指标"""
        self.indicators['sma_fast'] = bt.indicators.SimpleMovingAverage(
            self.datas[0],
            period=10
        )
        
        self.indicators['sma_slow'] = bt.indicators.SimpleMovingAverage(
            self.datas[0],
            period=30
        )
        
        self.indicators['rsi'] = bt.indicators.RSI(
            self.datas[0],
            period=14
        )
        
        self.indicators['macd'] = bt.indicators.MACD(
            self.datas[0]
        )
    
    def notify_order(self, order):
        """订单状态通知"""
        if order.status in [order.Submitted, order.Accepted]:
            return
        
        if order.status in [order.Completed]:
            if order.isbuy():
                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
                self.log(f'BUY EXECUTED, Price: {order.executed.price:.2f}, Cost: {order.executed.value:.2f}, Comm: {order.executed.comm:.2f}')
            else:
                self.log(f'SELL EXECUTED, Price: {order.executed.price:.2f}, Cost: {order.executed.value:.2f}, Comm: {order.executed.comm:.2f}')
        
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')
        
        self.order = None
    
    def notify_trade(self, trade):
        """交易通知"""
        if not trade.isclosed:
            return
        
        self.log(f'TRADE PROFIT, Gross: {trade.pnl:.2f}, Net: {trade.pnlcomm:.2f}')
    
    def next(self):
        """策略主逻辑"""
        if self.order:
            return
        
        if not self.position:
            if self._should_buy():
                self._execute_buy()
        
        else:
            if self._should_sell():
                self._execute_sell()
    
    def _should_buy(self) -> bool:
        """判断是否买入"""
        raise NotImplementedError("Subclass must implement _should_buy()")
    
    def _should_sell(self) -> bool:
        """判断是否卖出"""
        raise NotImplementedError("Subclass must implement _should_sell()")
    
    def _execute_buy(self):
        """执行买入"""
        cash = self.broker.getcash()
        price = self.datas[0].close[0]
        
        size = int((cash * self.params.position_size) / price)
        
        self.log(f'BUY CREATE, Size: {size}, Price: {price:.2f}')
        
        self.order = self.buy(size=size)
        
        self.signals.append({
            "type": "BUY",
            "price": price,
            "size": size,
            "timestamp": self.datas[0].datetime.datetime(0)
        })
    
    def _execute_sell(self):
        """执行卖出"""
        self.log(f'SELL CREATE, Size: {self.position.size}')
        
        self.order = self.sell(size=self.position.size)
        
        self.signals.append({
            "type": "SELL",
            "price": self.datas[0].close[0],
            "size": self.position.size,
            "timestamp": self.datas[0].datetime.datetime(0)
        })
    
    def log(self, txt, dt=None):
        """日志记录"""
        dt = dt or self.datas[0].datetime.date(0)
        print(f'{dt.isoformat()}, {txt}')
```

### 3. 策略调度器

```python
from apscheduler.schedulers.background import BackgroundScheduler
from typing import Dict, List, Callable
from datetime import datetime, time
import logging

class StrategyScheduler:
    """策略调度器"""
    
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.strategies = {}
        self.logger = logging.getLogger(__name__)
    
    def add_strategy(
        self,
        name: str,
        strategy_func: Callable,
        schedule_type: str = "interval",
        **schedule_params
    ):
        """添加策略到调度器"""
        job_id = f"strategy_{name}"
        
        if schedule_type == "interval":
            job = self.scheduler.add_job(
                strategy_func,
                'interval',
                id=job_id,
                **schedule_params
            )
        elif schedule_type == "cron":
            job = self.scheduler.add_job(
                strategy_func,
                'cron',
                id=job_id,
                **schedule_params
            )
        elif schedule_type == "date":
            job = self.scheduler.add_job(
                strategy_func,
                'date',
                id=job_id,
                **schedule_params
            )
        else:
            raise ValueError(f"Unknown schedule type: {schedule_type}")
        
        self.strategies[name] = {
            "job": job,
            "func": strategy_func,
            "schedule_type": schedule_type,
            "schedule_params": schedule_params
        }
        
        self.logger.info(f"Added strategy to scheduler: {name}")
    
    def remove_strategy(self, name: str):
        """移除策略"""
        if name in self.strategies:
            job_id = f"strategy_{name}"
            self.scheduler.remove_job(job_id)
            del self.strategies[name]
            
            self.logger.info(f"Removed strategy from scheduler: {name}")
    
    def start(self):
        """启动调度器"""
        self.scheduler.start()
        self.logger.info("Strategy scheduler started")
    
    def stop(self):
        """停止调度器"""
        self.scheduler.shutdown()
        self.logger.info("Strategy scheduler stopped")
    
    def pause_strategy(self, name: str):
        """暂停策略"""
        if name in self.strategies:
            job_id = f"strategy_{name}"
            self.scheduler.pause_job(job_id)
            self.logger.info(f"Paused strategy: {name}")
    
    def resume_strategy(self, name: str):
        """恢复策略"""
        if name in self.strategies:
            job_id = f"strategy_{name}"
            self.scheduler.resume_job(job_id)
            self.logger.info(f"Resumed strategy: {name}")
    
    def get_strategy_status(self, name: str) -> Dict:
        """获取策略状态"""
        if name not in self.strategies:
            return {"error": f"Strategy {name} not found"}
        
        job = self.strategies[name]["job"]
        
        return {
            "name": name,
            "next_run_time": job.next_run_time,
            "trigger": str(job.trigger),
            "status": "running" if job.next_run_time else "paused"
        }
```

### 4. 策略生命周期管理

```python
from enum import Enum
from typing import Dict, List
from datetime import datetime
import json

class StrategyStatus(Enum):
    """策略状态"""
    CREATED = "created"
    RUNNING = "running"
    PAUSED = "paused"
    STOPPED = "stopped"
    ERROR = "error"

class StrategyLifecycleManager:
    """策略生命周期管理器"""
    
    def __init__(self):
        self.strategies = {}
        self.history = []
    
    def create_strategy(
        self,
        name: str,
        strategy_class: str,
        params: Dict
    ):
        """创建策略"""
        strategy_id = f"strategy_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        self.strategies[strategy_id] = {
            "id": strategy_id,
            "name": name,
            "class": strategy_class,
            "params": params,
            "status": StrategyStatus.CREATED,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "metrics": {}
        }
        
        self._add_history(strategy_id, "created", f"Strategy {name} created")
        
        return strategy_id
    
    def start_strategy(self, strategy_id: str):
        """启动策略"""
        if strategy_id not in self.strategies:
            return {"error": f"Strategy {strategy_id} not found"}
        
        strategy = self.strategies[strategy_id]
        
        if strategy["status"] not in [StrategyStatus.CREATED, StrategyStatus.PAUSED, StrategyStatus.STOPPED]:
            return {"error": f"Cannot start strategy in status {strategy['status']}"}
        
        strategy["status"] = StrategyStatus.RUNNING
        strategy["updated_at"] = datetime.now().isoformat()
        
        self._add_history(strategy_id, "started", f"Strategy {strategy['name']} started")
        
        return {"success": True, "status": "running"}
    
    def pause_strategy(self, strategy_id: str):
        """暂停策略"""
        if strategy_id not in self.strategies:
            return {"error": f"Strategy {strategy_id} not found"}
        
        strategy = self.strategies[strategy_id]
        
        if strategy["status"] != StrategyStatus.RUNNING:
            return {"error": f"Cannot pause strategy in status {strategy['status']}"}
        
        strategy["status"] = StrategyStatus.PAUSED
        strategy["updated_at"] = datetime.now().isoformat()
        
        self._add_history(strategy_id, "paused", f"Strategy {strategy['name']} paused")
        
        return {"success": True, "status": "paused"}
    
    def stop_strategy(self, strategy_id: str):
        """停止策略"""
        if strategy_id not in self.strategies:
            return {"error": f"Strategy {strategy_id} not found"}
        
        strategy = self.strategies[strategy_id]
        
        if strategy["status"] not in [StrategyStatus.RUNNING, StrategyStatus.PAUSED]:
            return {"error": f"Cannot stop strategy in status {strategy['status']}"}
        
        strategy["status"] = StrategyStatus.STOPPED
        strategy["updated_at"] = datetime.now().isoformat()
        
        self._add_history(strategy_id, "stopped", f"Strategy {strategy['name']} stopped")
        
        return {"success": True, "status": "stopped"}
    
    def update_strategy_metrics(
        self,
        strategy_id: str,
        metrics: Dict
    ):
        """更新策略指标"""
        if strategy_id not in self.strategies:
            return {"error": f"Strategy {strategy_id} not found"}
        
        strategy = self.strategies[strategy_id]
        strategy["metrics"].update(metrics)
        strategy["updated_at"] = datetime.now().isoformat()
        
        return {"success": True}
    
    def get_strategy(self, strategy_id: str) -> Dict:
        """获取策略信息"""
        if strategy_id not in self.strategies:
            return {"error": f"Strategy {strategy_id} not found"}
        
        return self.strategies[strategy_id]
    
    def list_strategies(self, status: Optional[StrategyStatus] = None) -> List[Dict]:
        """列出策略"""
        strategies = list(self.strategies.values())
        
        if status:
            strategies = [s for s in strategies if s["status"] == status]
        
        return strategies
    
    def _add_history(self, strategy_id: str, action: str, message: str):
        """添加历史记录"""
        self.history.append({
            "strategy_id": strategy_id,
            "action": action,
            "message": message,
            "timestamp": datetime.now().isoformat()
        })
```

## 技术实现

### 1. 策略示例

```python
class MomentumStrategy(BaseStrategy):
    """动量策略"""
    
    params = (
        ('stop_loss', 0.05),
        ('take_profit', 0.10),
        ('position_size', 0.1),
        ('momentum_period', 14),
    )
    
    def _init_indicators(self):
        """初始化指标"""
        super()._init_indicators()
        
        self.indicators['momentum'] = bt.indicators.Momentum(
            self.datas[0],
            period=self.params.momentum_period
        )
    
    def _should_buy(self) -> bool:
        """判断是否买入"""
        momentum = self.indicators['momentum'][0]
        sma_fast = self.indicators['sma_fast'][0]
        sma_slow = self.indicators['sma_slow'][0]
        rsi = self.indicators['rsi'][0]
        
        return (
            momentum > 0 and
            sma_fast > sma_slow and
            rsi < 70
        )
    
    def _should_sell(self) -> bool:
        """判断是否卖出"""
        momentum = self.indicators['momentum'][0]
        sma_fast = self.indicators['sma_fast'][0]
        sma_slow = self.indicators['sma_slow'][0]
        rsi = self.indicators['rsi'][0]
        
        return (
            momentum < 0 or
            sma_fast < sma_slow or
            rsi > 80
        )
```

### 2. 运行策略

```python
if __name__ == "__main__":
    engine = StrategyEngine(
        initial_cash=1000000,
        commission=0.001,
        slippage=0.0001
    )
    
    data = bt.feeds.YahooFinanceData(
        dataname='AAPL',
        fromdate=datetime(2023, 1, 1),
        todate=datetime(2024, 1, 1)
    )
    
    engine.add_data(data, 'AAPL')
    
    engine.add_strategy(MomentumStrategy, 'momentum_strategy', {
        'stop_loss': 0.05,
        'take_profit': 0.10,
        'position_size': 0.1,
        'momentum_period': 14
    })
    
    engine.add_analyzer(bt.analyzers.SharpeRatio, 'sharpe')
    engine.add_analyzer(bt.analyzers.DrawDown, 'drawdown')
    engine.add_analyzer(bt.analyzers.Returns, 'returns')
    
    results = engine.run_backtest()
    
    print(f"Initial Cash: {results['initial_cash']}")
    print(f"Final Value: {results['final_value']}")
    print(f"PnL: {results['pnl']}")
    print(f"PnL %: {results['pnl_pct']:.2f}%")
    print(f"Sharpe Ratio: {results['analyzers']['sharpe']['sharperatio']}")
    print(f"Max Drawdown: {results['analyzers']['drawdown']['max']['drawdown']:.2f}%")
```

## 实施路径

### Phase 1: 核心功能（Week 1）

**目标**: 实现基础策略执行

**任务清单**:
- [ ] 安装和配置Backtrader
- [ ] 实现策略执行引擎
- [ ] 实现策略基类
- [ ] 实现策略调度器
- [ ] 编写单元测试

**交付物**:
- StrategyEngine类
- BaseStrategy类
- StrategyScheduler类
- 单元测试覆盖率≥80%

### Phase 2: 高级功能（Week 2）

**目标**: 实现生命周期管理和监控

**任务清单**:
- [ ] 实现策略生命周期管理
- [ ] 实现策略监控
- [ ] 实现策略性能分析
- [ ] 集成到系统
- [ ] 编写集成测试

**交付物**:
- StrategyLifecycleManager类
- 监控集成
- 性能分析报告
- 集成测试覆盖率≥70%

```
```---
```

**文档版本**: v1.0.0
**创建日期**: 2026-04-07
**最后更新**: 2026-04-07
**状态**: Active

## 接口与契约（蓝图终稿）

- **契约真源**：`API_Contract.md`
- **对外接口边界**：本模块对外提供策略调度、执行与信号产出的能力（含运行状态/事件可查询）；不负责订单撮合与下单执行，不替代风控对交易约束的最终裁决。
- **上游入口（策略配置生成）**：`STRATEGY_AUTHORING_ASSISTANT_BLUEPRINT.md`（`STRATEGY_AUTHORING_ASSISTANT_001`）负责将用户“文字/对话”转为可校验的 `StrategyConfig`，并将通过校验的配置交由本模块执行/调度。

## 验收标准（可检查）

- 在测试环境中至少完成 1 条策略从启动→调度→产出信号→记录运行事件的闭环，并可在日志/事件存储中按时间与策略 ID 检索追溯。

## 已知限制

- 策略执行延迟与可用性指标依赖基础设施与下游执行链路；实施阶段需在契约真源或子契约中固化 SLA 口径、监控指标与降级策略。
