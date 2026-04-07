﻿---
module_id: DATA_SCHEDULER_API_001
version: 1.0.0
status: Active
created_date: 2026-04-04
last_updated: 2026-04-04
owner: 首席文档架构师
responsibility: 调度器API接口定义与使用说明
standard_type: API参考文档
applicable_scope: 智能下载调度器API
compliance_level: 专业标准
parent_document: ./INDEX.md
implementation_status: 已完成
---


# 智能下载调度器API参考

> **核心职责**: 数据调度器API接口和任务调度管理，涉及智能下载调度器 参考
> **职责边界**: 
> - ✅ 本文档负责：数据调度器API接口和任务调度管理
> - ❌ 本文档不负责：其他模块内容


## 文档职责说明

**本文档职责**: 调度器API接口文档
- 提供完整的调度器API接口说明
- 说明任务调度和执行流程
- 提供API使用示例和最佳实践

**相关文档引用**:
| 文档 | 路径 | 关系 | 说明 |
|------|------|------|------|
| 调度蓝图 | [BLUEPRINT.md](01_FRAMEWORK/ACCEPTANCE_CRITERIA_BLUEPRINT.md) | 架构层 | 调度器详细设计 |
| 调度索引 | [INDEX.md](./INDEX.md) | 上级索引 | 调度器模块索引 |

**职责边界**:
- ✅ 本文档负责: API接口定义和使用说明
- ❌ 本文档不负责: 调度器架构设计（由 BLUEPRINT.md 负责）

> 清风量化系统 - 智能下载调度器API文档
> **核心定位**: 提供完整的调度器API接口说明，指导开发和使用

---

## 1. API概述

### 1.1 核心类

| 类名 | 说明 | 主要功能 |
|------|------|----------|
| **DataScheduler** | 主调度器 | 任务调度、执行、监控 |
| **TaskQueue** | 任务队列 | 优先级队列管理 |
| **TaskExecutor** | 任务执行器 | 并发执行任务 |
| **TaskMonitor** | 任务监控器 | 状态监控、统计 |

### 1.2 快速开始

```python
from zephyr.data.scheduler import DataScheduler

# 创建调度器实例
scheduler = DataScheduler(
    max_workers=5,
    task_timeout=300,
    retry_count=3
)

# 添加任务
task_id = scheduler.add_task(
    task_type='download',
    data_source='akshare',
    symbols=['000001.SZ', '000002.SZ'],
    start_date='2024-01-01',
    end_date='2024-12-31'
)

# 启动调度器
scheduler.start()

# 查询任务状态
status = scheduler.get_task_status(task_id)
print(f"任务状态: {status['status']}")
print(f"进度: {status['progress']}%")

# 停止调度器
scheduler.stop()
```

---

## 2. DataScheduler类

### 2.1 初始化参数

```python
DataScheduler(
    max_workers: int = 5,              # 最大工作线程数
    task_timeout: int = 300,           # 任务超时时间（秒）
    retry_count: int = 3,              # 失败重试次数
    queue_size: int = 1000,            # 队列最大容量
    log_level: str = 'INFO'            # 日志级别
)
```

**参数说明**:

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| max_workers | int | 5 | 并发执行的最大线程数 |
| task_timeout | int | 300 | 单个任务的超时时间（秒） |
| retry_count | int | 3 | 任务失败后的重试次数 |
| queue_size | int | 1000 | 任务队列的最大容量 |
| log_level | str | 'INFO' | 日志级别（DEBUG/INFO/WARNING/ERROR） |

### 2.2 核心方法

#### add_task()

添加任务到调度队列。

```python
def add_task(
    task_type: str,                    # 任务类型
    data_source: str,                  # 数据源
    symbols: List[str],                # 股票代码列表
    start_date: str,                   # 开始日期
    end_date: str,                     # 结束日期
    priority: int = 1,                 # 优先级（0-2）
    callback: Optional[Callable] = None # 回调函数
) -> str:
    """
    添加任务到调度队列
    
    Args:
        task_type: 任务类型（download/realtime/financial/factor）
        data_source: 数据源（akshare/baostock/tushare/ifind）
        symbols: 股票代码列表
        start_date: 开始日期（YYYY-MM-DD）
        end_date: 结束日期（YYYY-MM-DD）
        priority: 优先级（0=高，1=中，2=低）
        callback: 任务完成回调函数
        
    Returns:
        str: 任务ID
        
    Raises:
        QueueFullError: 队列已满
        InvalidTaskError: 任务参数无效
    """
```

**示例**:

```python
# 添加下载任务
task_id = scheduler.add_task(
    task_type='download',
    data_source='akshare',
    symbols=['000001.SZ', '000002.SZ'],
    start_date='2024-01-01',
    end_date='2024-12-31',
    priority=0  # 高优先级
)

# 添加实时数据任务
task_id = scheduler.add_task(
    task_type='realtime',
    data_source='akshare',
    symbols=['000001.SZ'],
    priority=1
)
```

#### start()

启动调度器。

```python
def start(
    mode: str = 'background',          # 运行模式
    block: bool = False                # 是否阻塞主线程
) -> None:
    """
    启动调度器
    
    Args:
        mode: 运行模式
            - background: 后台运行（守护线程）
            - foreground: 前台运行
        block: 是否阻塞主线程（仅在foreground模式下有效）
    """
```

**示例**:

```python
# 后台运行
scheduler.start()

# 前台运行并阻塞
scheduler.start(mode='foreground', block=True)
```

#### stop()

停止调度器。

```python
def stop(
    wait: bool = True,                 # 是否等待当前任务完成
    timeout: int = 300                 # 等待超时时间（秒）
) -> None:
    """
    停止调度器
    
    Args:
        wait: 是否等待当前任务完成
        timeout: 等待超时时间
    """
```

**示例**:

```python
# 等待当前任务完成后停止
scheduler.stop(wait=True, timeout=300)

# 立即停止
scheduler.stop(wait=False)
```

#### get_task_status()

获取任务状态。

```python
def get_task_status(task_id: str) -> Dict:
    """
    获取任务状态
    
    Args:
        task_id: 任务ID
        
    Returns:
        Dict: 任务状态信息
            - status: pending/running/completed/failed
            - progress: 进度百分比（0-100）
            - start_time: 开始时间
            - end_time: 结束时间
            - error: 错误信息（如果失败）
            - result: 执行结果（如果完成）
    """
```

**示例**:

```python
status = scheduler.get_task_status(task_id)
print(f"状态: {status['status']}")
print(f"进度: {status['progress']}%")

if status['status'] == 'completed':
    print(f"结果: {status['result']}")
elif status['status'] == 'failed':
    print(f"错误: {status['error']}")
```

#### cancel_task()

取消任务。

```python
def cancel_task(task_id: str) -> bool:
    """
    取消任务
    
    Args:
        task_id: 任务ID
        
    Returns:
        bool: 是否成功取消
        
    Note:
        只能取消pending状态的任务
    """
```

**示例**:

```python
# 取消任务
success = scheduler.cancel_task(task_id)
if success:
    print("任务已取消")
else:
    print("无法取消（任务可能已在运行）")
```

#### get_statistics()

获取调度器统计信息。

```python
def get_statistics() -> Dict:
    """
    获取调度器统计信息
    
    Returns:
        Dict: 统计信息
            - total_tasks: 总任务数
            - pending_tasks: 等待中任务数
            - running_tasks: 运行中任务数
            - completed_tasks: 已完成任务数
            - failed_tasks: 失败任务数
            - avg_execution_time: 平均执行时间（秒）
            - success_rate: 成功率（%）
    """
```

**示例**:

```python
stats = scheduler.get_statistics()
print(f"总任务数: {stats['total_tasks']}")
print(f"成功率: {stats['success_rate']:.2f}%")
print(f"平均执行时间: {stats['avg_execution_time']:.2f}秒")
```

---

## 3. TaskQueue类

### 3.1 初始化

```python
TaskQueue(
    max_size: int = 1000,              # 队列最大容量
    priority_levels: int = 3           # 优先级数量
)
```

### 3.2 核心方法

#### put()

添加任务到队列。

```python
def put(
    task: Dict,                        # 任务字典
    priority: int = 1                  # 优先级（0-2）
) -> None:
    """
    添加任务到队列
    
    Args:
        task: 任务字典
        priority: 优先级（0=高，1=中，2=低）
        
    Raises:
        QueueFullError: 队列已满
    """
```

#### get()

从队列获取任务。

```python
def get(timeout: Optional[float] = None) -> Dict:
    """
    从队列获取任务（按优先级）
    
    Args:
        timeout: 超时时间（秒），None表示永久等待
        
    Returns:
        Dict: 任务字典
        
    Raises:
        EmptyError: 队列为空
    """
```

#### size()

获取队列大小。

```python
def size() -> Tuple[int, int, int]:
    """
    获取队列大小
    
    Returns:
        Tuple[int, int, int]: (高优先级数量, 中优先级数量, 低优先级数量)
    """
```

---

## 4. TaskExecutor类

### 4.1 初始化

```python
TaskExecutor(
    scheduler: DataScheduler,          # 调度器实例
    max_workers: int = 5               # 最大工作线程数
)
```

### 4.2 核心方法

#### execute()

执行任务。

```python
def execute(task: Dict) -> Dict:
    """
    执行任务
    
    Args:
        task: 任务字典
        
    Returns:
        Dict: 执行结果
            - success: 是否成功
            - data: 返回数据
            - error: 错误信息
            - execution_time: 执行时间
    """
```

---

## 5. TaskMonitor类

### 5.1 初始化

```python
TaskMonitor(
    scheduler: DataScheduler,          # 调度器实例
    check_interval: int = 10           # 检查间隔（秒）
)
```

### 5.2 核心方法

#### get_statistics()

获取统计信息。

```python
def get_statistics() -> Dict:
    """
    获取统计信息
    
    Returns:
        Dict: 统计信息
    """
```

#### get_task_history()

获取任务历史。

```python
def get_task_history(
    limit: int = 100,                  # 返回记录数
    status: Optional[str] = None       # 筛选状态
) -> List[Dict]:
    """
    获取任务历史
    
    Args:
        limit: 返回记录数
        status: 筛选状态（pending/running/completed/failed）
        
    Returns:
        List[Dict]: 任务历史列表
    """
```

---

## 6. 任务配置

### 6.1 任务类型

| 任务类型 | 说明 | 数据源 |
|----------|------|--------|
| **download** | 下载历史数据 | akshare/baostock/tushare/ifind |
| **realtime** | 实时数据订阅 | akshare/sina/tencent |
| **financial** | 财务数据下载 | baostock/tushare/ifind |
| **factor** | 因子数据计算 | 内部计算 |

### 6.2 任务优先级

| 优先级 | 值 | 说明 | 使用场景 |
|--------|----|------|----------|
| **高** | 0 | 高优先级 | 实时数据、紧急任务 |
| **中** | 1 | 普通优先级 | 日常下载任务 |
| **低** | 2 | 低优先级 | 补充数据、非紧急任务 |

### 6.3 任务状态

| 状态 | 说明 |
|------|------|
| **pending** | 等待执行 |
| **running** | 正在执行 |
| **completed** | 执行完成 |
| **failed** | 执行失败 |
| **cancelled** | 已取消 |

---

## 7. 高级用法

### 7.1 定时任务

```python
from zephyr.data.scheduler import DataScheduler
from datetime import datetime

scheduler = DataScheduler()

# 添加定时任务（每日盘后下载）
scheduler.add_scheduled_task(
    task_type='download',
    data_source='akshare',
    symbols=['000001.SZ'],
    schedule='0 18 * * 1-5',  # 每周一到周五18:00
    priority='high'
)

scheduler.start()
```

### 7.2 任务依赖

```python
# 任务A：下载行情数据
task_a = scheduler.add_task(
    task_type='download',
    data_source='akshare',
    symbols=['000001.SZ'],
    start_date='2024-01-01',
    end_date='2024-12-31'
)

# 任务B：计算因子（依赖任务A）
task_b = scheduler.add_task(
    task_type='factor',
    factor_name='momentum',
    symbols=['000001.SZ'],
    depends_on=[task_a]  # 依赖任务A
)
```

### 7.3 回调函数

```python
def on_task_complete(task_id: str, result: Dict):
    """任务完成回调"""
    print(f"任务 {task_id} 完成")
    print(f"结果: {result}")

# 添加任务时指定回调
task_id = scheduler.add_task(
    task_type='download',
    data_source='akshare',
    symbols=['000001.SZ'],
    start_date='2024-01-01',
    end_date='2024-12-31',
    callback=on_task_complete
)
```

### 7.4 错误处理

```python
from zephyr.data.scheduler.exceptions import (
    SchedulerError,
    TaskNotFoundError,
    TaskExecutionError
)

scheduler = DataScheduler()

try:
    task_id = scheduler.add_task(
        task_type='download',
        data_source='akshare',
        symbols=['000001.SZ'],
        start_date='2024-01-01',
        end_date='2024-12-31'
    )
    
    scheduler.start()
    
    # 等待任务完成
    while True:
        status = scheduler.get_task_status(task_id)
        if status['status'] in ['completed', 'failed']:
            break
        time.sleep(1)
    
    if status['status'] == 'failed':
        print(f"任务失败: {status['error']}")
        
except TaskExecutionError as e:
    print(f"任务执行错误: {e}")
except Exception as e:
    print(f"未知错误: {e}")
finally:
    scheduler.stop()
```

---

## 8. 性能优化

### 8.1 并发控制

```python
# 根据机器性能调整并发数
scheduler = DataScheduler(
    max_workers=10,  # 增加并发数
    task_timeout=600  # 增加超时时间
)
```

### 8.2 批量任务

```python
# 批量添加任务（减少队列操作）
symbols = ['000001.SZ', '000002.SZ', '000003.SZ']
task_ids = []

for symbol in symbols:
    task_id = scheduler.add_task(
        task_type='download',
        data_source='akshare',
        symbols=[symbol],
        start_date='2024-01-01',
        end_date='2024-12-31',
        priority=1
    )
    task_ids.append(task_id)
```

### 8.3 内存优化

```python
# 分批处理大量数据
batch_size = 100
for i in range(0, len(all_symbols), batch_size):
    batch = all_symbols[i:i+batch_size]
    scheduler.add_task(
        task_type='download',
        data_source='akshare',
        symbols=batch,
        start_date='2024-01-01',
        end_date='2024-12-31'
    )
```

---

## 9. 监控与日志

### 9.1 日志配置

```python
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scheduler.log'),
        logging.StreamHandler()
    ]
)

scheduler = DataScheduler(log_level='DEBUG')
```

### 9.2 性能监控

```python
import time

# 监控调度器性能
while True:
    stats = scheduler.get_statistics()
    print(f"运行中任务: {stats['running_tasks']}")
    print(f"等待中任务: {stats['pending_tasks']}")
    print(f"成功率: {stats['success_rate']:.2f}%")
    time.sleep(10)
```

---

## 10. 异常处理

### 10.1 异常类

| 异常类 | 说明 |
|--------|------|
| **SchedulerError** | 调度器基础异常 |
| **QueueFullError** | 队列已满 |
| **TaskNotFoundError** | 任务不存在 |
| **TaskExecutionError** | 任务执行错误 |
| **InvalidTaskError** | 任务参数无效 |
| **TimeoutError** | 任务超时 |

### 10.2 异常处理示例

```python
from zephyr.data.scheduler.exceptions import *

try:
    # 添加任务
    task_id = scheduler.add_task(...)
    
except QueueFullError:
    print("队列已满，请等待任务完成")
    
except InvalidTaskError as e:
    print(f"任务参数无效: {e}")
    
except TaskExecutionError as e:
    print(f"任务执行失败: {e}")
    
except Exception as e:
    print(f"未知错误: {e}")
```

---

## 11. 相关文档

- [INDEX.md](INDEX.md): 调度器目录索引
- [BLUEPRINT.md](01_FRAMEWORK/ACCEPTANCE_CRITERIA_BLUEPRINT.md): 调度器蓝图设计
- [../DATA_ACQUISITION.md](02_FACTOR_LIBRARY/04_DATA_SOURCE/DATA_ACQUISITION.md): 数据采集系统

---

**文档版本**: v1.0.0 | **创建日期**: 2026-04-04 | **维护者**: 首席文档架构师

---

## 变更记录

| 版本 | 日期 | 变更内容 | 变更人 |
|------|------|----------|--------|
| v1.0.0 | 2026-04-06 | 初始版本，补充职责描述和变更记录 | 首席文档架构师 |
