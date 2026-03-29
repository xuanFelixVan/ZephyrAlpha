---
module_id: RESEARCH_PIPELINE_001
version: 1.0
status: Active
parent_doc: INDEX.md
last_updated: 2026-03-29
layer: Layer 0 (基础设施层)
index: RES.PIPELINE.001
estimated_hours: 40h
---

# 研究Pipeline蓝图

> 清风量化系统 v5.0 - 研究流程自动化Pipeline
> **索引**: `RES.PIPELINE.001`
> **开发时间**: 40h
> **核心定位**: 将因子研究流程自动化，实现"数据→因子→回测→优化→入库"的闭环

---

## 1. 设计原则

| 原则 | 说明 |
|------|------|
| **Prefect Native** | 使用Prefect编排Pipeline，不重复造轮子 |
| **节点即Tool** | Pipeline每个节点对应一个AI Tool |
| **可观测性** | 完整记录每个节点的输入输出 |
| **断点可续** | Pipeline失败后可从断点继续 |

---

## 2. Pipeline架构

### 2.1 Pipeline类型

```
┌─────────────────────────────────────────────────────────────┐
│                    研究Pipeline (ResearchPipeline)            │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  数据采集 ──▶ 数据清洗 ──▶ 因子计算 ──▶ 因子验证            │
│       │                                              │        │
│       ▼                                              ▼        │
│  报告生成 ◀── 参数优化 ◀── 策略回测 ◀── 因子入库          │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 Pipeline与Agent关系

```
┌─────────────────────────────────────────────────────────────┐
│                    AI研究Agent                                │
│  ┌───────────────────────────────────────────────────────┐ │
│  │  人(策略方向)                                          │ │
│  │       │                                                │ │
│  │       ▼                                                │ │
│  │  ResearchAgent.research_factor()                      │ │
│  │       │                                                │ │
│  │       ▼                                                │ │
│  │  ResearchPipeline.run(objective="研究动量因子")       │ │
│  │       │                                                │ │
│  │       ▼                                                │ │
│  │  人(审批结果)                                          │ │
│  └───────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

---

## 3. Pipeline核心实现

### 3.1 Pipeline定义

```python
from prefect import flow, task
from prefect.task_runners import SequentialTaskRunner

@flow(
    name="因子研究Pipeline",
    task_runner=SequentialTaskRunner()
)
def research_pipeline(objective: str, constraints: dict) -> ResearchResult:
    """因子研究Pipeline

    索引: RES.PIPELINE.001-M01
    上游: ResearchAgent
    下游: FactorLibrary, wandb

    参数:
        objective: 研究目标
        constraints: 约束条件

    返回:
        ResearchResult
    """
    # 1. 数据采集
    raw_data = fetch_stock_data(objective['symbols'], objective['date_range'])

    # 2. 数据清洗
    cleaned_data = clean_data(raw_data)

    # 3. 因子计算
    factor_values = calculate_factor(cleaned_data, objective['factor_type'])

    # 4. 因子验证
    validation_result = validate_factor(factor_values, constraints)

    if not validation_result.passed:
        return ResearchResult(
            status='rejected',
            reason=validation_result.reason
        )

    # 5. 策略回测
    backtest_result = run_backtest(factor_values, objective['strategy'])

    # 6. 参数优化
    optimized_params = optimize_parameters(
        backtest_result,
        objective['optimize_target']
    )

    # 7. 生成报告
    report = generate_report({
        'objective': objective,
        'validation': validation_result,
        'backtest': backtest_result,
        'optimized': optimized_params
    })

    # 8. 因子入库
    factor_id = save_factor({
        'factor_type': objective['factor_type'],
        'definition': objective['factor_definition'],
        'validation': validation_result,
        'params': optimized_params
    })

    return ResearchResult(
        status='completed',
        factor_id=factor_id,
        report=report
    )
```

### 3.2 Task节点定义

```python
@task(name="数据采集", tags=["data"])
def fetch_stock_data(symbols: List[str], date_range: tuple) -> pd.DataFrame:
    """采集股票数据

    索引: RES.PIPELINE.001-T01
    Tool: get_stock_data
    """
    data = DataHub.get_ohlcv(symbols, date_range)
    return data

@task(name="数据清洗", tags=["data"])
def clean_data(raw_data: pd.DataFrame) -> pd.DataFrame:
    """清洗数据

    索引: RES.PIPELINE.001-T02
    Tool: clean_data
    """
    # 缺失值处理
    data = raw_data.fillna(method='ffill')

    # 异常值处理
    data = data.clip(lower=data.quantile(0.01), upper=data.quantile(0.99))

    return data

@task(name="因子计算", tags=["factor"])
def calculate_factor(data: pd.DataFrame, factor_type: str) -> pd.DataFrame:
    """计算因子

    索引: RES.PIPELINE.001-T03
    Tool: calculate_factor
    """
    if factor_type == 'momentum':
        return momentum_factor(data, period=20)
    elif factor_type == 'value':
        return value_factor(data)
    # ... 其他因子
    return factor_values

@task(name="因子验证", tags=["factor"])
def validate_factor(factor_values: pd.DataFrame, constraints: dict) -> ValidationResult:
    """验证因子

    索引: RES.PIPELINE.001-T04
    Tool: validate_factor

    约束条件:
        - ic_threshold: IC均值门槛
        - ir_threshold: IR门槛
        - decay_threshold: IC衰减门槛
    """
    ic_metrics = calculate_ic(factor_values)

    if ic_metrics['ic_mean'] < constraints.get('ic_threshold', 0.03):
        return ValidationResult(passed=False, reason='IC不达标')

    if ic_metrics['ic_ir'] < constraints.get('ir_threshold', 0.3):
        return ValidationResult(passed=False, reason='IR不达标')

    return ValidationResult(passed=True, metrics=ic_metrics)

@task(name="策略回测", tags=["backtest"])
def run_backtest(factor_values: pd.DataFrame, strategy_config: dict) -> BacktestResult:
    """回测策略

    索引: RES.PIPELINE.001-T05
    Tool: run_backtest
    """
    result = BacktestEngine.run(
        factors=factor_values,
        strategy=strategy_config['type'],
        params=strategy_config.get('params', {})
    )
    return result

@task(name="参数优化", tags=["optimize"])
def optimize_parameters(backtest_result: BacktestResult, objective: str) -> dict:
    """优化参数

    索引: RES.PIPELINE.001-T06
    Tool: optimize_parameters
    """
    study = optuna.create_study(direction='maximize')
    study.optimize(
        lambda trial: objective_function(trial, backtest_result),
        n_trials=100
    )
    return study.best_params

@task(name="报告生成", tags=["report"])
def generate_report(research_data: dict) -> str:
    """生成研究报告

    索引: RES.PIPELINE.001-T07
    Tool: generate_report
    """
    template = load_template('factor_research_report.md')
    return template.render(**research_data)
```

---

## 4. Pipeline配置

### 4.1 Pipeline定义

```python
# pipelines/factor_research.py

from prefect.pipeline import Pipeline

FACTOR_RESEARCH_PIPELINE = Pipeline(
    name="因子研究",
    description="数据→因子→验证→回测→优化→入库",
    flow=research_pipeline,
    parameters={
        'objective': {
            'type': 'string',
            'description': '研究目标'
        },
        'constraints': {
            'type': 'dict',
            'description': '约束条件',
            'default': {
                'ic_threshold': 0.03,
                'ir_threshold': 0.3,
                'decay_threshold': 0.3
            }
        }
    },
    retry_policy={
        'max_attempts': 3,
        'retry_delay': 60
    }
)
```

### 4.2 调度配置

```yaml
# config/pipeline/schedule.yaml

schedules:
  - name: "日线因子更新"
    pipeline: "因子研究"
    cron: "0 18 * * 1-5"  # 收盘后18:00
    params:
      factor_type: "daily_momentum"

  - name: "分钟因子更新"
    pipeline: "因子研究"
    cron: "*/30 9-15 * * 1-5"  # 交易时段每30分钟
    params:
      factor_type: "intraday_momentum"
```

---

## 5. 监控与日志

### 5.1 Pipeline监控指标

| 指标 | 说明 | 阈值 |
|------|------|------|
| pipeline_run_count | Pipeline运行次数/日 | - |
| pipeline_success_rate | 成功率 | >95% |
| pipeline_avg_time | 平均运行时间 | <30min |
| node_failure_count | 节点失败次数 | - |
| data_quality_score | 数据质量评分 | >90% |

### 5.2 Prefect Dashboard

```
┌─────────────────────────────────────────────────────────────┐
│                    Pipeline监控面板                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Pipeline: 因子研究Pipeline                                  │
│  Status: ✅ Running                                         │
│  Duration: 12m 34s                                          │
│                                                             │
│  节点进度:                                                  │
│  ✅ 数据采集     ───  ✅ 数据清洗     ───  🔄 因子计算      │
│        │                 │                 │                 │
│        2m 15s            1m 03s            5m 12s          │
│                                                             │
│  待执行:                                                     │
│  ⬜ 因子验证   ⬜ 策略回测   ⬜ 参数优化   ⬜ 报告生成       │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 6. 错误处理与恢复

### 6.1 错误处理策略

```python
@task(name="数据采集", tags=["data"], retry_policy=RetryPolicy(max_attempts=3))
def fetch_stock_data(symbols: List[str], date_range: tuple) -> pd.DataFrame:
    """采集股票数据 - 带重试"""
    try:
        data = DataHub.get_ohlcv(symbols, date_range)
    except DataSourceError as e:
        logger.warning(f"数据源错误: {e}, 尝试备用数据源")
        data = BackupDataSource.get_ohlcv(symbols, date_range)
    return data
```

### 6.2 断点续传

```python
# Pipeline支持从失败的节点继续
@flow(name="因子研究Pipeline")
def research_pipeline(objective: str, resume_from: str = None):
    """因子研究Pipeline - 支持断点续传

    参数:
        resume_from: 从哪个节点恢复 (如"因子计算")
    """
    state = load_pipeline_state()

    if resume_from:
        # 从断点恢复
        start_node = resume_from
    else:
        # 从头开始
        start_node = "数据采集"

    # 执行Pipeline
    execute_pipeline(start_node=start_node)
```

---

## 7. 集成接口

### 7.1 上游接口

| 模块 | 接口 | 说明 |
|------|------|------|
| ResearchAgent | run() | Agent调用Pipeline |
| Scheduler | trigger() | 定时触发Pipeline |

### 7.2 下游接口

| 模块 | 接口 | 说明 |
|------|------|------|
| DataHub | get_ohlcv() | 数据采集 |
| FactorLibrary | save_factor() | 因子入库 |
| BacktestEngine | run() | 回测执行 |
| Optuna | optimize() | 参数优化 |
| wandb | log() | 实验记录 |
| Apprise | notify() | 告警通知 |

---

## 8. 开发任务分解

### 8.1 任务分解 (40h)

| 任务 | 时间 | 说明 |
|------|------|------|
| Prefect环境搭建 | 4h | Prefect Server + Agent |
| Task节点开发 | 12h | 8个核心Task |
| Pipeline编排 | 8h | Pipeline定义+配置 |
| 错误处理 | 6h | 重试+断点续传 |
| 监控面板 | 4h | Prefect Dashboard |
| API集成 | 4h | 与Agent集成 |
| 测试 | 2h | 单元测试 |

---

## 9. 测试策略

### 9.1 测试分层

```
单元测试 (每个Task独立测试)
    ↓
集成测试 (Pipeline串联测试)
    ↓
端到端测试 (完整流程测试)
```

### 9.2 单元测试

```python
# tests/unit/test_pipeline_tasks.py

import pytest
from unittest.mock import Mock, patch
from pipelines.factor_research import (
    fetch_stock_data,
    clean_data,
    calculate_factor,
    validate_factor
)

class TestPipelineTasks:
    """Pipeline Task单元测试"""

    # 数据采集测试
    def test_fetch_stock_data_success(self):
        """测试成功获取股票数据"""
        with patch('pipelines.factor_research.DataHub') as mock:
            mock.get_ohlcv.return_value = pd.DataFrame({
                'open': [100, 101, 102],
                'high': [105, 106, 107],
                'low': [95, 96, 97],
                'close': [102, 103, 104],
                'volume': [1000, 1100, 1200]
            })
            result = fetch_stock_data(['000001.XSHE'], ('2024-01-01', '2024-12-31'))
            assert not result.empty
            assert len(result) == 3

    def test_fetch_stock_data_empty(self):
        """测试获取空数据"""
        with patch('pipelines.factor_research.DataHub') as mock:
            mock.get_ohlcv.return_value = pd.DataFrame()
            result = fetch_stock_data(['INVALID'], ('2024-01-01', '2024-12-31'))
            assert result.empty

    # 数据清洗测试
    def test_clean_data_missing_values(self):
        """测试缺失值处理"""
        raw_data = pd.DataFrame({
            'close': [100, None, 102, None, 104]
        })
        result = clean_data(raw_data)
        assert result['close'].isna().sum() == 0

    def test_clean_data_outliers(self):
        """测试异常值处理"""
        raw_data = pd.DataFrame({
            'close': [100, 1000, 102, 50, 103]  # 1000和50是异常值
        })
        result = clean_data(raw_data)
        assert result['close'].max() < 500
        assert result['close'].min() > 75

    # 因子计算测试
    def test_calculate_momentum_factor(self):
        """测试动量因子计算"""
        data = pd.DataFrame({
            'close': [100, 101, 102, 103, 104, 105, 106, 107, 108, 109]
        })
        result = calculate_factor(data, 'momentum', period=5)
        assert 'momentum' in result.columns
        assert not result['momentum'].isna().all()

    def test_calculate_value_factor(self):
        """测试价值因子计算"""
        data = pd.DataFrame({
            'pe': [10, 15, 20, 25, 30],
            'pb': [1, 1.5, 2, 2.5, 3]
        })
        result = calculate_factor(data, 'value')
        assert 'value' in result.columns

    # 因子验证测试
    def test_validate_factor_pass(self):
        """测试因子验证通过"""
        factor_data = pd.DataFrame({'factor': [0.05, 0.04, 0.06, 0.05]})
        result = validate_factor(
            factor_data,
            {'ic_threshold': 0.03, 'ir_threshold': 0.3}
        )
        assert result.passed == True

    def test_validate_factor_ic_fail(self):
        """测试IC不达标"""
        factor_data = pd.DataFrame({'factor': [0.01, 0.02, 0.01, 0.02]})
        result = validate_factor(
            factor_data,
            {'ic_threshold': 0.03, 'ir_threshold': 0.3}
        )
        assert result.passed == False
        assert 'IC' in result.reason

    def test_validate_factor_ir_fail(self):
        """测试IR不达标"""
        factor_data = pd.DataFrame({'factor': [0.05, 0.01, 0.05, 0.01, 0.05]})
        result = validate_factor(
            factor_data,
            {'ic_threshold': 0.03, 'ir_threshold': 0.5}
        )
        assert result.passed == False
        assert 'IR' in result.reason
```

### 9.3 集成测试

```python
# tests/integration/test_pipeline_integration.py

import pytest
from pipelines.factor_research import research_pipeline

class TestPipelineIntegration:
    """Pipeline集成测试"""

    def test_full_pipeline_success(self):
        """测试完整Pipeline成功"""
        result = research_pipeline(
            objective={
                'symbols': ['000001.XSHE', '000002.XSHE'],
                'date_range': ('2024-01-01', '2024-06-30'),
                'factor_type': 'momentum',
                'period': 20
            },
            constraints={
                'ic_threshold': 0.02,
                'ir_threshold': 0.2
            }
        )

        assert result.status == 'completed'
        assert result.factor_id is not None
        assert result.report is not None

    def test_pipeline_factor_rejected(self):
        """测试因子被拒绝"""
        result = research_pipeline(
            objective={
                'symbols': ['000001.XSHE'],
                'date_range': ('2024-01-01', '2024-06-30'),
                'factor_type': 'momentum',
                'period': 5
            },
            constraints={
                'ic_threshold': 0.1,  # 设置过高的阈值
                'ir_threshold': 1.0
            }
        )

        assert result.status == 'rejected'

    def test_pipeline_with_resume(self):
        """测试断点续传"""
        # 先运行
        result1 = research_pipeline(
            objective={'factor_type': 'momentum'},
            constraints={}
        )

        # 模拟失败后恢复
        result2 = research_pipeline(
            objective={'factor_type': 'momentum'},
            constraints={},
            resume_from='因子计算'
        )

        assert result2.status == 'completed'
```

### 9.4 端到端测试

```python
# tests/e2e/test_pipeline_e2e.py

class TestPipelineE2E:
    """Pipeline端到端测试"""

    def test_daily_pipeline_schedule(self):
        """测试日线Pipeline调度"""
        # 1. 触发日线Pipeline
        response = client.post("/api/v1/pipeline/trigger", json={
            "pipeline_name": "因子研究",
            "params": {
                "factor_type": "daily_momentum"
            }
        })
        assert response.status_code == 200
        run_id = response.json()["run_id"]

        # 2. 等待完成
        for _ in range(600):  # 最多10分钟
            status = client.get(f"/api/v1/pipeline/run/{run_id}")
            if status.json()["status"] in ['completed', 'failed']:
                break
            time.sleep(1)

        # 3. 验证结果
        result = client.get(f"/api/v1/pipeline/run/{run_id}/result")
        assert result.json()["status"] == 'completed'
        assert "factor_id" in result.json()
```

---

## 10. 数据模型

### 10.1 Pipeline State

```python
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime
from enum import Enum

class PipelineStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class NodeStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"

class PipelineRun(BaseModel):
    """Pipeline运行记录"""
    id: str
    pipeline_name: str
    status: PipelineStatus
    started_at: datetime
    completed_at: Optional[datetime] = None
    current_node: Optional[str] = None

    # 节点状态
    nodes: List[Dict] = Field(default_factory=list)

    # 参数和结果
    input_params: Dict
    output_result: Optional[Dict] = None

    # 错误信息
    error: Optional[str] = None
    failed_node: Optional[str] = None

class NodeExecution(BaseModel):
    """节点执行记录"""
    id: str
    pipeline_run_id: str
    node_name: str
    status: NodeStatus
    started_at: datetime
    completed_at: Optional[datetime] = None

    # 输入输出
    input_data: Optional[Dict] = None
    output_data: Optional[Dict] = None

    # 性能指标
    duration_seconds: Optional[float] = None
    memory_mb: Optional[float] = None

    # 错误信息
    error: Optional[str] = None
    retry_count: int = Field(default=0)
```

---

## 11. API详细定义

### 11.1 请求/响应模型

```python
# api/models/pipeline.py

from pydantic import BaseModel, Field
from typing import Optional, List, Dict

class TriggerPipelineRequest(BaseModel):
    """触发Pipeline请求"""
    pipeline_name: str
    params: Dict = Field(default_factory=dict)
    run_id: Optional[str] = None  # 如果指定，则恢复运行

class TriggerPipelineResponse(BaseModel):
    """触发Pipeline响应"""
    run_id: str
    status: str
    message: str

class GetPipelineRunResponse(BaseModel):
    """获取Pipeline运行状态"""
    run_id: str
    pipeline_name: str
    status: str
    current_node: Optional[str]
    nodes: List[Dict]
    progress: float = Field(ge=0, le=1)
    started_at: str
    duration_seconds: Optional[float]

class GetPipelineResultResponse(BaseModel):
    """获取Pipeline结果"""
    run_id: str
    status: str
    factor_id: Optional[str]
    report: Optional[str]
    execution_summary: Dict
```

### 11.2 API端点

```python
# api/routes/pipeline.py

@router.post("/pipeline/trigger", response_model=TriggerPipelineResponse)
async def trigger_pipeline(request: TriggerPipelineRequest):
    """触发Pipeline"""
    pass

@router.get("/pipeline/run/{run_id}", response_model=GetPipelineRunResponse)
async def get_pipeline_run(run_id: str):
    """获取Pipeline运行状态"""
    pass

@router.get("/pipeline/run/{run_id}/result", response_model=GetPipelineResultResponse)
async def get_pipeline_result(run_id: str):
    """获取Pipeline结果"""
    pass

@router.post("/pipeline/run/{run_id}/cancel")
async def cancel_pipeline_run(run_id: str):
    """取消Pipeline运行"""
    pass

@router.post("/pipeline/run/{run_id}/resume")
async def resume_pipeline_run(run_id: str, from_node: str):
    """从断点恢复Pipeline"""
    pass

@router.get("/pipeline/{pipeline_name}/history")
async def get_pipeline_history(pipeline_name: str, limit: int = 50):
    """获取Pipeline历史运行"""
    pass
```

---

## 12. 性能优化

### 12.1 并行化策略

```python
# Pipeline支持并行执行的节点

from prefect import flow, task
from prefect.task_runners import ConcurrentTaskRunner

@flow(
    name="因子研究Pipeline",
    task_runner=ConcurrentTaskRunner()  # 并行执行
)
def research_pipeline_parallel(objective: dict):
    # 可以并行执行的节点
    with task_group():
        data_fetch = fetch_stock_data.submit(objective['symbols'])
        market_data = fetch_market_data.submit(objective['date_range'])

    # 等待并行任务完成后继续
    combined_data = combine_data(data_fetch.result(), market_data.result())
    # ...
```

### 12.2 缓存策略

```python
# Task结果缓存

@task(name="数据采集", cache_key_fn=lambda args, kwargs: f"{args[0]}_{kwargs['date_range']}")
def fetch_stock_data(symbols: List[str], date_range: tuple) -> pd.DataFrame:
    """采集股票数据 - 带缓存"""
    # 相同参数的结果会被缓存
    return DataHub.get_ohlcv(symbols, date_range)
```

---

## 13. 更新记录

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| v1.0 | 2026-03-29 | 初始版本 |
| v1.1 | 2026-03-29 | 补充测试策略、API定义、性能优化 |

---

**维护者**: 清风量化系统
**索引**: `RES.PIPELINE.001`
