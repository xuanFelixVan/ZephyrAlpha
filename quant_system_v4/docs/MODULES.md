# MODULES.md - 核心模块规格

> **版本**：v4.0
> **日期**：2026-03-28
> **状态**：规格阶段

---

## 1. 模块概览

| 编号 | 模块 | 层级 | 优先级 | 依赖模块 |
|------|------|------|--------|----------|
| 1 | data_collector | Layer 0 | P0 | 无 |
| 2 | data_cleaner | Layer 0 | P0 | data_collector |
| 3 | data_storage | Layer 0 | P0 | data_cleaner |
| 4 | factor_registry | Layer 2 | P0 | data_storage |
| 5 | factor_calculator | Layer 2 | P0 | factor_registry |
| 6 | strategy_engine | Layer 2 | P0 | factor_calculator |
| 7 | risk_manager | Layer 3 | P0 | strategy_engine |
| 8 | backtest_framework | Layer 5 | P1 | risk_manager |
| 9 | trade_executor | Layer 5 | P1 | risk_manager |
| 10 | monitoring_system | Layer 6 | P1 | trade_executor |
| 11 | config_manager | 支撑 | P0 | 无 |
| 12 | task_scheduler | 支撑 | P1 | config_manager |
| 13 | logger | 支撑 | P1 | 无 |
| 14 | exception_handler | 支撑 | P2 | logger |
| 15 | performance_monitor | 支撑 | P2 | logger |

---

## 2. Layer 0 模块

### 2.1 data_collector

```python
class DataCollector:
    """数据采集模块"""

    def collect(self, data_type: str, symbols: list, start_date: str, end_date: str) -> Result:
        """
        采集数据
        Returns: Result[pd.DataFrame]
        """
        pass

    def collect_all(self, date: str) -> Result:
        """采集全市场数据"""
        pass

    def collect_realtime(self, symbols: list) -> Result:
        """采集实时数据"""
        pass
```

### 2.2 data_cleaner

```python
class DataCleaner:
    """数据清洗模块"""

    def clean(self, df: pd.DataFrame, rules: dict) -> Result:
        """清洗数据"""
        pass

    def handle_missing(self, df: pd.DataFrame, method: str) -> Result:
        """处理缺失值"""
        pass

    def detect_outliers(self, df: pd.DataFrame, method: str, threshold: float) -> Result:
        """检测异常值"""
        pass
```

### 2.3 data_storage

```python
class DataStorage:
    """数据存储模块"""

    def save_raw(self, df: pd.DataFrame, data_type: str, date: str) -> Result:
        """保存原始数据"""
        pass

    def save_processed(self, df: pd.DataFrame, table: str) -> Result:
        """保存处理后数据"""
        pass

    def load(self, table: str, start_date: str = None, end_date: str = None) -> Result:
        """加载数据"""
        pass

    def query(self, sql: str) -> Result:
        """SQL查询"""
        pass
```

---

## 3. Layer 2 模块

### 3.1 factor_registry

```python
class FactorRegistry:
    """因子注册中心"""

    def register(self, factor: dict) -> Result:
        """注册因子"""
        pass

    def get(self, factor_id: str) -> Result:
        """获取因子信息"""
        pass

    def list_by_category(self, category: str) -> Result:
        """按类别列出因子"""
        pass

    def list_by_performance(self, start_date: str, end_date: str, top_n: int) -> Result:
        """按绩效列出因子"""
        pass
```

### 3.2 factor_calculator

```python
class FactorCalculator:
    """因子计算引擎"""

    def calculate(self, factor_id: str, date: str, params: dict = None) -> Result:
        """计算单个因子"""
        pass

    def calculate_batch(self, factor_ids: list, start_date: str, end_date: str) -> Result:
        """批量计算因子"""
        pass

    def calculate_selected(self, date: str, top_n: int = 50) -> Result:
        """计算选中的因子"""
        pass

    def analyze_performance(self, factor_id: str, start_date: str, end_date: str) -> Result:
        """分析因子绩效"""
        pass
```

### 3.3 strategy_engine

```python
class StrategyEngine:
    """策略引擎"""

    def load_strategy(self, strategy_config: dict) -> Result:
        """加载策略"""
        pass

    def run(self, strategy_id: str, date: str) -> Result:
        """运行单个策略"""
        pass

    def run_all(self, date: str) -> Result:
        """运行所有活跃策略"""
        pass

    def optimize(self, strategy_id: str, param_space: dict, objective: str) -> Result:
        """参数优化"""
        pass
```

---

## 4. Layer 3 模块

### 4.1 risk_manager

```python
class RiskManager:
    """风险管理系统"""

    def validate_signal(self, signal: Signal, current_positions: list) -> Result:
        """验证信号风险"""
        pass

    def calculate_position_size(self, signal: Signal, account_value: float) -> float:
        """计算仓位大小"""
        pass

    def check_stop_loss(self, position: Position, current_price: float) -> Result:
        """检查止损"""
        pass

    def check_take_profit(self, position: Position, current_price: float) -> Result:
        """检查止盈"""
        pass

    def check_risk_limits(self, portfolio: dict) -> Result:
        """检查风险限制"""
        pass
```

---

## 5. Layer 5-7 模块

### 5.1 backtest_framework

```python
class BacktestFramework:
    """回测框架"""

    def run(self, strategy_id: str, start_date: str, end_date: str,
             initial_capital: float) -> Result:
        """运行回测"""
        pass

    def run_batch(self, strategy_ids: list, start_date: str, end_date: str) -> Result:
        """批量回测"""
        pass

    def optimize(self, strategy_id: str, param_space: dict, metric: str) -> Result:
        """参数优化"""
        pass

    def walk_forward(self, strategy_id: str, train_period: int, test_period: int) -> Result:
        """Walk-Forward分析"""
        pass
```

### 5.2 trade_executor

```python
class TradeExecutor:
    """交易执行模块"""

    def submit_order(self, order: Order) -> Result:
        """提交订单"""
        pass

    def cancel_order(self, order_id: str) -> Result:
        """撤销订单"""
        pass

    def modify_order(self, order_id: str, new_order: Order) -> Result:
        """修改订单"""
        pass

    def get_positions(self) -> Result:
        """获取当前持仓"""
        pass

    def get_account(self) -> Result:
        """获取账户信息"""
        pass
```

### 5.3 monitoring_system

```python
class MonitoringSystem:
    """监控告警系统"""

    def monitor_positions(self, positions: list):
        """监控持仓"""
        pass

    def monitor_pnl(self, daily_pnl: float):
        """监控盈亏"""
        pass

    def monitor_risk(self, portfolio: dict):
        """监控风险"""
        pass

    def send_alert(self, level: str, message: str):
        """发送告警"""
        pass
```

---

## 6. 支撑模块

### 6.1 config_manager

```python
class ConfigManager:
    """配置管理模块"""

    def load(self, name: str) -> dict:
        """加载配置"""
        pass

    def save(self, name: str, config: dict) -> Result:
        """保存配置"""
        pass

    def get(self, name: str, key: str, default=None) -> Any:
        """获取配置项"""
        pass

    def set(self, name: str, key: str, value: Any) -> Result:
        """设置配置项"""
        pass

    def reload(self, name: str = None) -> Result:
        """热重载配置"""
        pass
```

### 6.2 task_scheduler

```python
class TaskScheduler:
    """任务调度模块"""

    def add_task(self, task: dict) -> Result:
        """添加任务"""
        pass

    def remove_task(self, task_id: str) -> Result:
        """移除任务"""
        pass

    def run_now(self, task_id: str) -> Result:
        """立即运行任务"""
        pass

    def get_task_status(self, task_id: str) -> Result:
        """获取任务状态"""
        pass
```

### 6.3 logger

```python
class Logger:
    """日志系统"""

    def info(self, message: str, **kwargs):
        """普通信息"""
        pass

    def debug(self, message: str, **kwargs):
        """调试信息"""
        pass

    def warning(self, message: str, **kwargs):
        """警告信息"""
        pass

    def error(self, message: str, **kwargs):
        """错误信息"""
        pass
```

### 6.4 exception_handler

```python
class ExceptionHandler:
    """异常处理模块"""

    def handle(self, exception: Exception, context: dict) -> Result:
        """处理异常"""
        pass

    def retry(self, func: Callable, max_retries: int = 3, backoff: float = 1.0) -> Any:
        """重试装饰器"""
        pass

    def circuit_breaker(self, func: Callable, threshold: int = 5, timeout: int = 60) -> Callable:
        """熔断装饰器"""
        pass
```

### 6.5 performance_monitor

```python
class PerformanceMonitor:
    """性能监控模块"""

    def record(self, metric_name: str, value: float):
        """记录指标"""
        pass

    def get_metrics(self, time_range: str = '1h') -> dict:
        """获取指标"""
        pass

    def check_bottleneck(self) -> list:
        """检查瓶颈"""
        pass
```

---

## 7. 统一返回格式

```python
@dataclass
class Result:
    success: bool
    data: Any = None
    error: Optional[str] = None
    metadata: dict = None
```

---

## 8. 更新记录

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| v4.0 | 2026-03-28 | 简化版，移除冗余代码示例，只保留接口规格 |
