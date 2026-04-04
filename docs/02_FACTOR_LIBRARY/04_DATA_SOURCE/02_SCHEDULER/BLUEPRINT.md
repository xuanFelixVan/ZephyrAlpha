---
---
module_id: DATA_SCHEDULER_001
version: 1.0.0
status: Active
created_date: 2026-04-01
last_updated: 2026-04-03
owner: 首席文档架构�?standard_type: 数据处理文档
applicable_scope: 数据调度系统
compliance_level: 专业标准
parent_document: ../INDEX.md
implementation_status: 设计阶段
implementation_progress: 0%
---
---


# 智能下载调度器蓝�?

> 清风量化系统 v5.0 - 智能数据下载调度�?
> **索引**: `DATA.SCH.001`
> **开发时�?*: 8h
> **核心定位**: 基于时间和优先级的智能调度，确保数据在正确时间获�?


## 1. 设计原则

| 原则 | 说明 |
|------|------|
| **时间驱动** | 盘前、盘中、盘后差异化调度 |
| **优先级队�?* | 紧急任务优先执�?|
| **自动重试** | 失败任务自动重试，指数退�?|
| **依赖管理** | 支持任务间依赖关�?|


## 2. 系统架构

### 2.1 调度器架�?

```
┌─────────────────────────────────────────────────────────────�?
�?                   智能下载调度�?                             �?
├─────────────────────────────────────────────────────────────�?
�?                                                            �?
�? ┌─────────────�?   ┌─────────────�?   ┌─────────────�?    �?
�? �? 任务队列   │───▶│  调度�?   │───▶│  执行�?    �?    �?
�? �? PriorityQ  �?   �?Scheduler  �?   �?Executor   �?    �?
�? └─────────────�?   └─────────────�?   └─────────────�?    �?
�?        �?                 �?                 �?             �?
�?        �?                 �?                 �?             �?
�? ┌─────────────�?   ┌─────────────�?   ┌─────────────�?    �?
�? �? 任务注册   �?   �? 时间窗口   �?   �? 结果回调   �?    �?
�? �? TaskReg   �?   �?TimeWindow �?   �? Callback  �?    �?
�? └─────────────�?   └─────────────�?   └─────────────�?    �?
�?                                                            �?
└─────────────────────────────────────────────────────────────�?
```

### 2.2 时间窗口定义

| 时段 | 时间范围 | 任务类型 | 优先�?|
|------|----------|----------|--------|
| **盘前** | 07:00-09:00 | 日线数据、财经日历、隔夜外�?| P0 |
| **早盘** | 09:15-09:30 | 分钟线、Level2快照 | P1 |
| **盘中** | 09:30-11:30 | 实时行情、异动监�?| P0 |
| **午盘** | 13:00-15:00 | 分钟线、盘后数�?| P2 |
| **盘后** | 15:30-22:00 | 日线归档、财务数据、因子计�?| P3 |


## 3. 核心实现

### 3.1 任务定义

```python
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Callable
from datetime import datetime, time
import heapq

class Priority(Enum):
    P0_CRITICAL = 0  # 必须立即执行
    P1_HIGH = 1      # 高优先级
    P2_NORMAL = 2    # 普�?
    P3_LOW = 3       # 低优先级

class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"

@dataclass(order=True)
class DownloadTask:
    """下载任务定义

    索引: DATA.SCH.001-T01
    """
    priority: int = field(compare=True)
    created_at: datetime = field(compare=True)
    task_id: str = field(compare=False)
    task_type: str = field(compare=False)
    params: dict = field(compare=False)
    dependencies: List[str] = field(default_factory=list, compare=False)
    retry_count: int = field(default=0, compare=False)
    max_retries: int = field(default=3, compare=False)
    callback: Optional[Callable] = field(default=None, compare=False)
    status: TaskStatus = field(default=TaskStatus.PENDING, compare=False)

    def __post_init__(self):
        if isinstance(self.priority, Priority):
            self.priority = self.priority.value
```

### 3.2 调度器核�?

```python
class IntelligentScheduler:
    """智能下载调度�?

    索引: DATA.SCH.001-M01
    上游: DataHub, FactorCalculator
    下游: DataSourceAdapter, DataCleaner
    """

    def __init__(self):
        self.task_queue: List[DownloadTask] = []
        self.running_tasks: Dict[str, DownloadTask] = {}
        self.completed_tasks: Dict[str, DownloadTask] = {}
        self.failed_tasks: Dict[str, DownloadTask] = {}
        self.time_windows = self._init_time_windows()
        self.executor = DownloadExecutor()

    def _init_time_windows(self) -> Dict[str, TimeWindow]:
        """初始化时间窗�?""
        return {
            'pre_market': TimeWindow(time(7, 0), time(9, 0), [Priority.P0_CRITICAL]),
            'morning': TimeWindow(time(9, 15), time(9, 30), [Priority.P1_HIGH]),
            'trading': TimeWindow(time(9, 30), time(11, 30), [Priority.P0_CRITICAL, Priority.P1_HIGH]),
            'afternoon': TimeWindow(time(13, 0), time(15, 0), [Priority.P2_NORMAL]),
            'after_close': TimeWindow(time(15, 30), time(22, 0), [Priority.P3_LOW])
        }

    def add_task(self, task: DownloadTask) -> str:
        """添加任务到调度队�?

        参数:
            task: 下载任务

        返回:
            task_id: 任务ID
        """
        task.created_at = datetime.now()
        heapq.heappush(self.task_queue, task)
        logger.info(f"Task {task.task_id} added to queue, priority={task.priority}")
        return task.task_id

    def schedule(self) -> Optional[DownloadTask]:
        """调度下一个任�?

        返回:
            下一个要执行的任务，None表示队列为空
        """
        if not self.task_queue:
            return None

        current_time = datetime.now().time()
        current_window = self._get_current_time_window(current_time)

        while self.task_queue:
            task = heapq.heappop(self.task_queue)

            if self._can_execute_in_window(task, current_window):
                task.status = TaskStatus.RUNNING
                self.running_tasks[task.task_id] = task
                return task

            if task in self.task_queue:
                heapq.heappush(self.task_queue, task)
                break

        return None

    def _get_current_time_window(self, current_time: time) -> str:
        """获取当前时间窗口"""
        for window_name, window in self.time_windows.items():
            if window.start <= current_time <= window.end:
                return window_name
        return 'after_close'

    def _can_execute_in_window(self, task: DownloadTask, window: str) -> bool:
        """检查任务是否可以在当前时间窗口执行"""
        window_config = self.time_windows[window]
        return Priority(task.priority) in window_config.allowed_priorities

    def on_task_completed(self, task_id: str, result: any) -> None:
        """任务完成回调

        参数:
            task_id: 任务ID
            result: 执行结果
        """
        task = self.running_tasks.pop(task_id)
        task.status = TaskStatus.COMPLETED
        self.completed_tasks[task_id] = task

        if task.callback:
            task.callback(result)

        logger.info(f"Task {task_id} completed successfully")

    def on_task_failed(self, task_id: str, error: Exception) -> None:
        """任务失败回调

        参数:
            task_id: 任务ID
            error: 异常信息
        """
        task = self.running_tasks.get(task_id)

        if not task:
            return

        if task.retry_count < task.max_retries:
            task.retry_count += 1
            task.status = TaskStatus.RETRYING
            delay = 2 ** task.retry_count
            logger.warning(f"Task {task_id} failed, retrying in {delay}s (attempt {task.retry_count})")
            self._schedule_retry(task, delay)
        else:
            task.status = TaskStatus.FAILED
            self.failed_tasks[task_id] = task
            logger.error(f"Task {task_id} failed after {task.max_retries} retries: {error}")
```

### 3.3 执行�?

```python
class DownloadExecutor:
    """下载执行�?

    索引: DATA.SCH.001-M02
    上游: IntelligentScheduler
    下游: DataSourceAdapter
    """

    def __init__(self):
        self.adapter_registry = DataSourceAdapterRegistry()

    async def execute(self, task: DownloadTask) -> any:
        """执行下载任务

        参数:
            task: 下载任务

        返回:
            下载结果
        """
        adapter = self.adapter_registry.get_adapter(task.task_type)

        try:
            logger.info(f"Executing task {task.task_id} with {adapter.__class__.__name__}")
            result = await adapter.fetch(**task.params)
            return result
        except Exception as e:
            logger.error(f"Task {task.task_id} execution failed: {e}")
            raise

    async def execute_batch(self, tasks: List[DownloadTask]) -> List[any]:
        """批量执行任务

        参数:
            tasks: 任务列表

        返回:
            结果列表
        """
        results = await asyncio.gather(
            *[self.execute(task) for task in tasks],
            return_exceptions=True
        )
        return results
```


## 4. 任务类型定义

### 4.1 盘前任务

```python
class PreMarketTasks:
    """盘前任务定义

    执行时间: 07:00-09:00
    """

    DAILY_BAR = {
        'task_type': 'daily_bar',
        'params': {
            'symbols': 'all_a_share',
            'fields': ['open', 'high', 'low', 'close', 'volume'],
            'retry_count': 3
        },
        'priority': Priority.P0_CRITICAL,
        'time_window': 'pre_market'
    }

    FINANCIAL_CALENDAR = {
        'task_type': 'financial_calendar',
        'params': {
            'start_date': 'today',
            'end_date': 'today+7'
        },
        'priority': Priority.P1_HIGH,
        'time_window': 'pre_market'
    }

    OVERNIGHT_MARKET = {
        'task_type': 'overnight_market',
        'params': {
            'markets': ['us', 'hk', 'futures']
        },
        'priority': Priority.P1_HIGH,
        'time_window': 'pre_market'
    }
```

### 4.2 盘中任务

```python
class InTradingTasks:
    """盘中任务定义

    执行时间: 09:30-15:00
    """

    REALTIME_QUOTE = {
        'task_type': 'realtime_quote',
        'params': {
            'symbols': 'watchlist',
            'fields': ['last', 'bid', 'ask', 'volume']
        },
        'priority': Priority.P0_CRITICAL,
        'interval': 60
    }

    MINUTE_BAR = {
        'task_type': 'minute_bar',
        'params': {
            'symbols': 'holding_positions',
            'period': 5
        },
        'priority': Priority.P1_HIGH,
        'interval': 300
    }

    UNUSUAL_VOLUME = {
        'task_type': 'unusual_volume_monitor',
        'params': {
            'threshold': 2.0,
            'lookback': 20
        },
        'priority': Priority.P2_NORMAL,
        'interval': 600
    }
```

### 4.3 盘后任务

```python
class AfterCloseTasks:
    """盘后任务定义

    执行时间: 15:30-22:00
    """

    DAILY_ARCHIVE = {
        'task_type': 'daily_bar_archive',
        'params': {
            'date': 'today',
            'storage': 'parquet'
        },
        'priority': Priority.P2_NORMAL,
        'time_window': 'after_close'
    }

    FINANCIAL_DATA = {
        'task_type': 'financial_data_update',
        'params': {
            'data_types': ['income', 'balance', 'cashflow']
        },
        'priority': Priority.P3_LOW,
        'time_window': 'after_close',
        'dependencies': ['DAILY_BAR']
    }

    FACTOR_CALCULATION = {
        'task_type': 'factor_batch_calculation',
        'params': {
            'factors': 'all_active',
            'date': 'today'
        },
        'priority': Priority.P3_LOW,
        'time_window': 'after_close',
        'dependencies': ['DAILY_BAR']
    }
```


## 5. 调度配置

### 5.1 YAML配置

```yaml
# config/scheduler.yaml

scheduler:
  enabled: true
  max_concurrent_tasks: 5
  default_retry_count: 3
  retry_backoff_base: 2

time_windows:
  pre_market:
    start: "07:00"
    end: "09:00"
    allowed_priorities: [0, 1]

  morning:
    start: "09:15"
    end: "09:30"
    allowed_priorities: [1]

  trading:
    start: "09:30"
    end: "11:30"
    allowed_priorities: [0, 1]

  afternoon:
    start: "13:00"
    end: "15:00"
    allowed_priorities: [1, 2]

  after_close:
    start: "15:30"
    end: "22:00"
    allowed_priorities: [2, 3]

task_defaults:
  daily_bar:
    priority: 0
    max_retries: 3
    timeout: 300

  realtime_quote:
    priority: 0
    max_retries: 5
    timeout: 10
    interval: 60

  minute_bar:
    priority: 1
    max_retries: 3
    timeout: 60
    interval: 300
```


## 6. 集成接口

### 6.1 上游接口

| 模块 | 接口 | 说明 |
|------|------|------|
| DataHub | request_data_download() | 请求数据下载 |
| FactorCalculator | request_factor_data() | 请求因子数据 |
| MonitoringSystem | get_schedule_status() | 获取调度状�?|

### 6.2 下游接口

| 模块 | 接口 | 说明 |
|------|------|------|
| DataSourceAdapter | fetch() | 执行数据获取 |
| DataCleaner | clean() | 数据清洗 |
| DataStorage | save() | 数据存储 |


## 7. 监控指标

| 指标 | 说明 | 阈�?|
|------|------|------|
| scheduler_queue_size | 队列任务�?| <100 |
| scheduler_task_latency | 任务调度延迟 | <1s |
| scheduler_retry_rate | 重试�?| <5% |
| scheduler_failure_rate | 失败�?| <1% |


## 8. 开发任务分�?8h)

| 任务 | 时间 | 交付�?|
|------|------|--------|
| 任务队列实现 | 2h | PriorityQ, DownloadTask |
| 时间窗口调度 | 2h | TimeWindow, Scheduler |
| 执行器框�?| 1.5h | DownloadExecutor |
| 任务类型定义 | 1h | PreMarket/InTrading/AfterClose Tasks |
| 配置集成 | 0.5h | scheduler.yaml |
| 单元测试 | 1h | test_scheduler.py |


**维护�?*: 清风量化系统
**索引**: `DATA.SCH.001`
**最后更�?*: 2026-03-29
