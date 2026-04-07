---
module_id: IMPL_INFRA_DAILY_PIPELINE_001
version: 1.0.1
status: Active
created_date: 2026-04-01
last_updated: 2026-04-01
owner: 首席文档架构�?
standard_type: 专业量化机构实施标准
applicable_scope: 系统实施与部�?
compliance_level: 初始标准
parent_document: ../INDEX.md
implementation_status: 进行�?
responsibility:
  - 实施指南、部署文档

---
---

# 每日数据流水�?
> **核心职责**: 文档内容说明
> **职责边界**: 
> - ✅ 本文档负责：文档内容说明相关内容
> - ❌ 本文档不负责：其他模块内容


> 自动化数据采集、清洗、存储的完整流水�?
>
> **版本**: v1.0
> **更新**: 2026-03-28
> **优先�?*: P0 - 核心系统

---

## 1. 设计原则

| 原则 | 说明 |
|------|------|
| **自动�?* | 全自动执行，无需人工干预 |
| **容错�?* | 单点故障不影响整�?|
| **可追�?* | 每一步都有日志记�?|
| **可回�?* | 失败可重试，数据可回�?|

---

## 2. 流水线阶�?

```
┌─────────────────────────────────────────────────────────────�?
�?                   每日数据流水�?                           �?
├─────────────────────────────────────────────────────────────�?
�? 阶段1: 盘前准备    06:00-09:00   下载前日数据、更新基础数据   �?
�? 阶段2: 交易时段    09:00-15:00   实时行情监控、分钟线采集   �?
�? 阶段3: 盘后处理    15:00-20:00   下载当日数据、数据清�?    �?
�? 阶段4: 夜间处理    20:00-06:00   因子计算、数据备�?        �?
└─────────────────────────────────────────────────────────────�?
```

---

## 3. 阶段详解

### 阶段1: 盘前准备 (06:00-09:00)

| 时间 | 任务 | 超时 | 重试 | 依赖 |
|------|------|------|------|------|
| 06:00 | 下载前日收盘数据 | 30min | 3 | - |
| 06:30 | 更新财务数据和基本面 | 60min | 2 | 前日数据 |
| 07:30 | 更新概念板块数据 | 30min | 2 | - |
| 08:00 | 更新行业分类数据 | 20min | 2 | - |
| 08:30 | 生成盘前数据报告 | 15min | 1 | 以上全部 |

**盘前任务代码示例**�?

```python
class MorningPipeline:
    """盘前数据准备流水�?""

    def __init__(self):
        self.tasks = [
            {'time': '06:00', 'name': '下载前日收盘', 'timeout': 1800, 'retry': 3},
            {'time': '06:30', 'name': '更新财务数据', 'timeout': 3600, 'retry': 2},
            {'time': '07:30', 'name': '更新概念板块', 'timeout': 1800, 'retry': 2},
            {'time': '08:00', 'name': '更新行业分类', 'timeout': 1200, 'retry': 2},
            {'time': '08:30', 'name': '生成盘前报告', 'timeout': 900, 'retry': 1},
        ]

    def run(self):
        """执行盘前流水�?""
        for task in self.tasks:
            self._execute_with_retry(task)
```

---

### 阶段2: 交易时段 (09:00-15:00)

| 时间 | 任务 | 类型 | 重试 |
|------|------|------|------|
| 09:00 | 启动实时行情监控 | 实时 | 无限 |
| 09:15 | 开始分钟线数据采集 | 实时 | 无限 |
| 11:30 | 上午数据初步汇�?| 定时 | 1 |
| 13:00 | 继续实时数据更新 | 实时 | 无限 |
| 14:55 | 准备收盘数据处理 | 定时 | 2 |

**交易时段监控代码示例**�?

```python
class TradingSessionMonitor:
    """交易时段实时监控"""

    def __init__(self):
        self.realtime_tasks = ['行情监控', '分钟线采�?]
        self.scheduled_tasks = [
            {'time': '11:30', 'name': '上午汇�?, 'timeout': 600},
            {'time': '14:55', 'name': '收盘准备', 'timeout': 300},
        ]

    def start_realtime(self):
        """启动实时任务"""
        for task in self.realtime_tasks:
            self._start_background_task(task)

    def check_scheduled(self):
        """检查定时任�?""
        current_time = datetime.now().strftime('%H:%M')
        for task in self.scheduled_tasks:
            if current_time == task['time']:
                self._execute(task)
```

---

### 阶段3: 盘后处理 (15:00-20:00)

| 时间 | 任务 | 超时 | 重试 | 优先�?|
|------|------|------|------|--------|
| 15:05 | 下载当日完整行情 | 30min | 3 | �?|
| 15:45 | 更新资金流向数据 | 45min | 2 | �?|
| 16:30 | 下载龙虎榜数�?| 30min | 2 | �?|
| 17:30 | 更新融资融券数据 | 30min | 2 | �?|
| 18:30 | 数据质量校验 | 60min | 1 | �?|

**盘后任务代码示例**�?

```python
class AfterHoursPipeline:
    """盘后数据处理流水�?""

    def __init__(self):
        self.tasks = [
            {'time': '15:05', 'name': '当日完整行情', 'priority': 'HIGH', 'timeout': 1800, 'retry': 3},
            {'time': '15:45', 'name': '资金流向', 'priority': 'MED', 'timeout': 2700, 'retry': 2},
            {'time': '16:30', 'name': '龙虎�?, 'priority': 'MED', 'timeout': 1800, 'retry': 2},
            {'time': '17:30', 'name': '融资融券', 'priority': 'MED', 'timeout': 1800, 'retry': 2},
            {'time': '18:30', 'name': '数据校验', 'priority': 'HIGH', 'timeout': 3600, 'retry': 1},
        ]
```

---

### 阶段4: 夜间处理 (20:00-06:00)

| 时间 | 任务 | 超时 | 重试 |
|------|------|------|------|
| 20:00 | 生成数据质量报告 | 30min | 1 |
| 21:00 | 执行数据备份 | 120min | 2 |
| 23:00 | 系统维护和优�?| 60min | 1 |
| 02:00 | 历史数据归档 | 180min | 1 |

---

## 4. 智能调度�?

```python
from queue import PriorityQueue
from datetime import datetime

class DataScheduler:
    """基于时间优先级的智能下载调度"""

    PRIORITY_LEVELS = {
        'REALTIME': 0,
        'HIGH': 1,
        'MEDIUM': 2,
        'LOW': 3
    }

    def __init__(self):
        self.task_queue = PriorityQueue()
        self.execution_history = []

    def add_task(self, task_type: str, params: dict, priority: str = 'MEDIUM'):
        """添加下载任务到调度队�?""
        task = {
            'id': self._generate_task_id(),
            'type': task_type,
            'params': params,
            'priority': self.PRIORITY_LEVELS[priority],
            'status': 'PENDING',
            'created_at': datetime.now(),
            'retry_count': 0,
            'max_retries': 3
        }
        self.task_queue.put((task['priority'], task))

    def _execute_with_retry(self, task: dict) -> bool:
        """带重试的任务执行"""
        while task['retry_count'] < task['max_retries']:
            try:
                result = self._execute_task(task)
                self.execution_history.append({
                    'task_id': task['id'],
                    'status': 'SUCCESS',
                    'timestamp': datetime.now()
                })
                return True
            except Exception as e:
                task['retry_count'] += 1
                self._log_error(task, str(e))

        self.execution_history.append({
            'task_id': task['id'],
            'status': 'FAILED',
            'timestamp': datetime.now()
        })
        return False

    def _execute_task(self, task: dict):
        """执行单个任务"""
        # 根据任务类型调用对应的数据获取函�?
        task_handlers = {
            'DAILY_OHLCV': self._fetch_daily_ohlcv,
            'MINUTE_BAR': self._fetch_minute_bar,
            'FUNDAMENTAL': self._fetch_fundamental,
            'MONEY_FLOW': self._fetch_money_flow,
            'MARGIN': self._fetch_margin,
            'TOPLIST': self._fetch_toplist,
        }

        handler = task_handlers.get(task['type'])
        if handler:
            return handler(task['params'])
        else:
            raise ValueError(f"Unknown task type: {task['type']}")
```

---

## 5. 数据质量控制

### 5.1 质量检查规�?

```python
class DataQualityChecker:
    """数据质量检查器"""

    def check_ohlcv(self, df: pd.DataFrame) -> dict:
        """检查OHLCV数据质量"""
        issues = []

        # 检查缺失�?
        if df.isnull().any().any():
            issues.append({'type': 'MISSING_VALUE', 'count': df.isnull().sum().sum()})

        # 检查价格异�?
        if (df['close'] <= 0).any():
            issues.append({'type': 'INVALID_PRICE', 'count': (df['close'] <= 0).sum()})

        # 检查成交量异常
        if (df['volume'] < 0).any():
            issues.append({'type': 'INVALID_VOLUME', 'count': (df['volume'] < 0).sum()})

        # 检查价格连续�?
        if (df['high'] < df['low']).any():
            issues.append({'type': 'HIGH_LOW_INVERSION', 'count': (df['high'] < df['low']).sum()})

        # 检查涨跌停
        if (df['pct_change'].abs() > 0.11).any():
            issues.append({'type': 'LIMIT_MOVE', 'count': (df['pct_change'].abs() > 0.11).sum()})

        return {
            'passed': len(issues) == 0,
            'issues': issues
        }
```

### 5.2 清洗规则

```python
class DataCleaner:
    """数据清洗引擎"""

    CLEANING_RULES = {
        'OHLCV': {
            'fill_missing': {'close': 'ffill', 'volume': 0},
            'fix_anomalies': ['price_inversion', 'negative_volume'],
            'convert_types': {'date': 'datetime'}
        },
        'FUNDAMENTAL': {
            'fill_missing': {'value': 'industry_mean'},
            'fix_anomalies': ['negative_value', 'extreme_outlier'],
            'convert_types': {'report_date': 'datetime'}
        },
        'MONEY_FLOW': {
            'fill_missing': {'value': 0},
            'fix_anomalies': [],
            'convert_types': {}
        }
    }

    def clean(self, df: pd.DataFrame, data_type: str) -> pd.DataFrame:
        """执行数据清洗"""
        rules = self.CLEANING_RULES.get(data_type, {})

        # 去重
        df = self._remove_duplicates(df)

        # 填充缺失�?
        if 'fill_missing' in rules:
            df = self._fill_missing(df, rules['fill_missing'])

        # 修正异常�?
        if 'fix_anomalies' in rules:
            df = self._fix_anomalies(df, rules['fix_anomalies'])

        return df
```

---

## 6. 容错与恢�?

### 6.1 错误恢复策略

| 错误类型 | 检测方�?| 恢复策略 | 降级方案 |
|----------|----------|----------|----------|
| 网络中断 | 超时检�?| 自动重试+切换数据�?| 使用缓存数据 |
| 数据缺失 | 完整性校�?| 多源补全 | 标记并跳�?|
| 格式错误 | Schema校验 | 自动修正 | 人工审核 |
| 存储异常 | 磁盘监控 | 冗余备份 | 切换存储 |

### 6.2 重试配置

```python
RETRY_CONFIG = {
    'network_error': {
        'max_retries': 5,
        'backoff': [1, 5, 10, 30, 60],  # �?
        'fallback': 'use_cache'
    },
    'data_missing': {
        'max_retries': 3,
        'backoff': [5, 10, 30],
        'fallback': 'multi_source_fill'
    },
    'format_error': {
        'max_retries': 2,
        'backoff': [1, 5],
        'fallback': 'manual_review'
    }
}
```

---

## 7. 配置模板

```yaml
# config/pipelines.yaml
pipelines:
  morning:
    enabled: true
    start_time: "06:00"
    tasks:
      - name: download_previous_day
        timeout: 1800
        retry: 3
      - name: update_fundamental
        timeout: 3600
        retry: 2
      - name: update_concept
        timeout: 1800
        retry: 2

  trading_session:
    enabled: true
    realtime_tasks:
      - name: market_monitor
      - name: minute_bar_collection

  after_hours:
    enabled: true
    start_time: "15:05"
    tasks:
      - name: download_today_ohlcv
        priority: HIGH
      - name: update_money_flow
        priority: MEDIUM
      - name: data_quality_check
        priority: HIGH

  night:
    enabled: true
    start_time: "20:00"
    tasks:
      - name: quality_report
      - name: backup
      - name: archival
```

---

## 8. 监控与告�?

### 8.1 监控指标

| 指标 | 正常范围 | 告警阈�?|
|------|----------|----------|
| 任务成功�?| > 99% | < 95% |
| 数据完整�?| = 100% | < 98% |
| 任务延迟 | < 超时�?0% | > 超时�?0% |
| 重试次数 | < 1�?任务 | > 2�?任务 |

### 8.2 告警规则

```python
ALERT_RULES = [
    {'condition': 'success_rate < 0.95', 'level': 'WARNING', 'message': '任务成功率低�?5%'},
    {'condition': 'success_rate < 0.90', 'level': 'CRITICAL', 'message': '任务成功率低�?0%'},
    {'condition': 'data_completeness < 0.98', 'level': 'WARNING', 'message': '数据完整性低�?8%'},
    {'condition': 'consecutive_failures >= 3', 'level': 'CRITICAL', 'message': '连续失败超过3�?},
]
```

---

## 9. 目录结构

```
05_IMPLEMENTATION/04_INFRASTRUCTURE/
├── STORAGE_ARCHITECTURE.md    # 存储架构
├── DAILY_PIPELINE.md          # 本文�?
└── DATA_QUALITY_CONTROL.md    # 数据质量控制(待创�?
```

---

## 更新记录

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| v1.0 | 2026-03-28 | 初始版本 |
