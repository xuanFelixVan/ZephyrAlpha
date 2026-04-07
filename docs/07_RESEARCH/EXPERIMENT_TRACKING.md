---
module_id: EXPERIMENT_TRACKING
version: 1.0.0
status: Active
created_date: 2026-04-07
last_updated: 2026-04-07
owner: 首席文档架构师
responsibility:
  - 实验追踪蓝图文档
---

﻿---
module_id: RESEARCH_EXPERIMENT_TRACKING_001
version: 1.0.1
status: Active
created_date: 2026-04-01
last_updated: 2026-04-07
owner: 首席文档架构师
responsibility:
  - 07 RESEARCH模块文档管理与维护
standard_type: 专业量化机构文档
applicable_scope: 全系统
compliance_level: 初始标准
parent_document: INDEX.md
implementation_status: 进行中
responsibility_boundary: |
  本文档负责Layer 7研究层的轻量级实验追踪设计，包括：
  
  生产级实验追踪（MLflow方案）请参考：docs/01_FRAMEWORK/EXPERIMENT_TRACKING_BLUEPRINT.md
---
---
 进行?
---


# 实验追踪蓝图
> **核心职责**: 蓝图设计和规划
> **职责边界**: 
> - ✅ 本文档负责：蓝图设计和规划相关内容
> - ❌ 本文档不负责：其他模块内容


> 清风量化系统 v5.0 - AI实验追踪系统
> **索引**: `EXP.TRACK.001`
> **开发时?*: 30h
> **核心定位**: 使用wandb.ai自动追踪所有AI研究实验，实?一次调用，全自动记?


## 1. 设计原则

| 原则 | 说明 |
|------|------|
| **wandb Native** | 使用wandb.ai，不自研实验追踪 |
| **零代码侵?* | 通过decorator自动追踪，无需修改业务代码 |
| **一次调?* | `wandb.init()` 一行代码开始追?|
| **AI原生** | 专为AI/LLM实验设计 |


## 2. wandb集成架构

### 2.1 wandb vs 自研对比

| 方案 | 开发时?| 功能 | 维护成本 |
|------|----------|------|----------|
| **wandb.ai** | 30分钟 | ⭐⭐⭐⭐?| ?(云端托管) |
| 自研实验追踪 | 2-3个月 | ⭐⭐?| ⭐⭐⭐⭐?|

### 2.2 wandb能力

```
wandb能力:
├── 实验自动记录 (代码/参数/指标/文件)
├── 超参数搜?(贝叶斯优?
├── 实验对比看板 (一键对?
├── 模型版本管理
├── 实验协作与分?
└── 云端存储 (100GB免费)
```


## 3. wandb快速集?

### 3.1 环境配置

```bash
# 安装
pip install wandb

# 登录 (免费注册)
wandb login
```

### 3.2 基础集成

```python
import wandb

# 初始?(一行代码开始追?
wandb.init(
    project="qingfeng-quant",
    entity="your_username",
    name="momentum_factor_v1",
    tags=["factor", "momentum"],
    notes="测试动量因子20日窗?
)

# 记录指标 (自动追踪)
for epoch in range(100):
    wandb.log({
        "epoch": epoch,
        "loss": loss,
        "ic": ic,
        "sharpe": sharpe
    })

# 保存 artifacts
wandb.save("model.pt")
wandb.log_artifact("model.pt", name="model")
```


## 4. AI研究场景集成

### 4.1 因子研究实验

```python
import wandb
from wandb.sdk.wandb_run import Run

class FactorResearchExperiment:
    """因子研究实验追踪

    索引: EXP.TRACK.001-M01
    上游: ResearchPipeline
    下游: wandb云端
    """

    def __init__(self, config: dict):
        self.config = config
        self.run = None

    def __enter__(self):
        """上下文管理器入口"""
        self.run = wandb.init(
            project="qingfeng-quant-factor",
            entity="your_username",
            name=f"factor_{self.config['factor_type']}_{self.config['version']}",
            tags=[self.config['factor_type'], "factor_research"],
            config=self.config,
            notes=f"因子研究实验: {self.config.get('description', '')}"
        )
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        if self.run:
            self.run.finish()

    def log_factor_metrics(self, metrics: dict):
        """记录因子指标

        参数:
            metrics: {
                'ic_mean': 0.045,
                'ic_ir': 0.52,
                'ic_decay_5d': 0.15,
                'annual_return': 0.12
            }
        """
        wandb.log(metrics)

    def log_artifact(self, name: str, path: str, type: str = "model"):
        """保存实验产物

        参数:
            name: artifact名称
            path: 文件路径
            type: artifact类型
        """
        artifact = wandb.Artifact(name, type=type)
        artifact.add_file(path)
        wandb.log_artifact(artifact)

    def log_table(self, name: str, data: pd.DataFrame):
        """记录数据?

        参数:
            name: 表名
            data: DataFrame
        """
        wandb.log({name: wandb.Table(dataframe=data)})

# 使用示例
with FactorResearchExperiment({
    'factor_type': 'momentum',
    'period': 20,
    'version': 'v1',
    'description': '测试20日动量因?
}) as exp:
    # 计算因子
    factor_values = calculate_momentum(data, period=20)

    # 验证因子
    metrics = validate_factor(factor_values)

    # 自动记录到wandb
    exp.log_factor_metrics(metrics)

    # 保存数据
    exp.log_table('factor_values', factor_values)
```

### 4.2 策略回测实验

```python
class StrategyBacktestExperiment:
    """策略回测实验追踪

    索引: EXP.TRACK.001-M02
    """

    def run(self, strategy_config: dict, factor_data: pd.DataFrame):
        """运行回测实验

        参数:
            strategy_config: 策略配置
            factor_data: 因子数据
        """
        with wandb.init(
            project="qingfeng-quant-strategy",
            entity="your_username",
            name=f"strategy_{strategy_config['name']}_{wandb.run.id}",
            tags=["strategy", strategy_config['type']],
            config=strategy_config
        ) as run:
            # 运行回测
            result = BacktestEngine.run(strategy_config, factor_data)

            # 记录核心指标
            wandb.log({
                "total_return": result['total_return'],
                "sharpe_ratio": result['sharpe'],
                "max_drawdown": result['max_drawdown'],
                "win_rate": result['win_rate'],
                "trade_count": result['trade_count']
            })

            # 记录权益曲线
            wandb.log({
                "equity_curve": wandb.plot.line(
                    pd.Series(result['cumulative_returns']),
                    title="权益曲线"
                )
            })

            # 保存回测数据
            trades_df = pd.DataFrame(result['trades'])
            wandb.log({"trades": wandb.Table(dataframe=trades_df)})

            return result
```

### 4.3 参数优化实验

```python
import optuna
from optuna.integration import wandb as wandb_optuna

def objective(trial: optuna.Trial) -> float:
    """Optuna优化目标函数

    与wandb自动集成
    """
    params = {
        'period': trial.suggest_int('period', 5, 60),
        'threshold': trial.suggest_float('threshold', 0.01, 0.1),
        'stop_loss': trial.suggest_float('stop_loss', 0.02, 0.1)
    }

    with wandb.init(
        project="qingfeng-quant-optimize",
        entity="your_username",
        name=f"optuna_{wandb.run.id}",
        tags=["optimization"],
        config=params
    ):
        # 运行回测
        result = run_backtest(params)

        # 记录指标
        wandb.log({
            'sharpe': result['sharpe'],
            'return': result['return'],
            'drawdown': result['drawdown']
        })

        return result['sharpe']

# 使用wandb追踪Optuna优化
wandb_kwargs = {
    "project": "qingfeng-quant-optimize",
    "entity": "your_username",
    "tags": ["optuna", "optimization"]
}

study = optuna.create_study(
    direction='maximize',
    study_name='strategy_optimization'
)

study.optimize(
    objective,
    n_trials=100,
    callbacks=[wandb_optuna.integration_wandb_callback(wandb_kwargs)]
)
```


## 5. wandb看板设计

### 5.1 因子研究看板

wandb自动生成:
- IC_IR散点?
- 超参数相关性热力图
- 最佳实验对比表
- 实验历史时间?

### 5.2 策略回测看板

wandb自动生成:
- Sharpe比率分布
- 回测权益曲线对比
- 收益-回撤散点?
- 交易频率分析

### 5.3 自定义看板配?

```yaml
# wandb-config.yaml
dashboards:
  factor_research:
    title: "因子研究看板"
    panels:
      - type: "scatter"
        x: "ic_ir"
        y: "ic_mean"
        color: "factor_type"

      - type: "line"
        metric: "ic_mean"
        group: "factor_type"

      - type: "table"
        columns: ["name", "ic_mean", "ic_ir", "decay_5d"]

  strategy_backtest:
    title: "策略回测看板"
    panels:
      - type: "line"
        metric: "equity_curve"

      - type: "scatter"
        x: "sharpe"
        y: "max_drawdown"
        color: "strategy_type"
```


## 6. API接口

### 6.1 wandb API

```python
import wandb

# 获取实验历史
api = wandb.Api()
runs = api.runs("your_username/qingfeng-quant-factor")

for run in runs:
    print(run.name, run.config, run.summaryMetrics)

# 下载artifact
artifact = api.artifact('your_username/qingfeng-quant-factor/model:v0')
artifact.download()
```


## 7. 与现有系统集?

### 7.1 与ResearchPipeline集成

```python
@task(name="实验追踪", tags=["experiment"])
def track_experiment(objective: dict, result: dict):
    """追踪实验

    Pipeline节点，自动记录实验结果到wandb
    """
    wandb.init(
        project="qingfeng-quant-pipeline",
        name=f"pipeline_{objective['id']}",
        config=objective,
        notes=f"Pipeline执行: {objective['name']}"
    )

    wandb.log(result)
```

### 7.2 与知识库集成

```python
# 实验完成后自动保存到知识?
def on_experiment_complete(experiment_id: str):
    """实验完成回调

    索引: EXP.TRACK.001-M03
    """
    # 从wandb获取实验结果
    run = wandb.Api().run(f"your_username/qingfeng-quant/{experiment_id}")

    # 保存到知识库
    save_to_knowledge_base({
        'experiment_id': experiment_id,
        'config': run.config,
        'metrics': run.summaryMetrics,
        'notes': run.notes,
        'artifacts': [a.name for a in run.logged_artifacts()]
    })
```


## 8. 开发任务分?

### 8.1 任务分解 (30h)

| 任务 | 时间 | 说明 |
|------|------|------|
| wandb账号配置 | 1h | 注册+配置 |
| Python SDK集成 | 4h | wandb.init/log |
| 因子实验类封?| 6h | FactorResearchExperiment |
| 策略实验类封?| 6h | StrategyBacktestExperiment |
| Optuna集成 | 4h | wandb_optuna_callback |
| 看板设计 | 4h | wandb dashboard配置 |
| 知识库集?| 3h | on_experiment_complete |
| 测试 | 2h | 集成测试 |


## 9. 监控指标

### 9.1 关键指标

| 指标 | 说明 | 阈?|
|------|------|------|
| experiment_count | 实验??| - |
| experiment_success_rate | 实验成功?| >70% |
| avg_experiment_duration | 平均实验时长 | <30min |


## 10. 测试策略

### 10.1 测试分层

```
单元测试 (Experiment类测?
    ?
集成测试 (wandb API测试)
    ?
端到端测?(完整实验追踪流程)
```

### 10.2 单元测试

```python
# tests/unit/test_experiment_tracking.py

import pytest
from unittest.mock import Mock, patch, MagicMock
from src.experiment.tracking import (
    FactorResearchExperiment,
    StrategyBacktestExperiment,
    ExperimentTracker
)

class TestFactorResearchExperiment:
    """因子研究实验测试"""

    def setup_method(self):
        """测试前准?""
        self.mock_wandb = MagicMock()
        self.patch_wandb = patch('src.experiment.tracking.wandb', self.mock_wandb)
        self.patch_wandb.start()

    def teardown_method(self):
        """测试后清?""
        self.patch_wandb.stop()

    def test_init_experiment(self):
        """测试实验初始?""
        experiment = FactorResearchExperiment(
            project="test_project",
            name="test_factor",
            config={'factor_type': 'momentum', 'period': 20}
        )

        assert experiment.config['factor_type'] == 'momentum'
        assert experiment.config['period'] == 20
        self.mock_wandb.init.assert_called_once()

    def test_log_metrics(self):
        """测试指标记录"""
        experiment = FactorResearchExperiment(
            project="test_project",
            name="test_factor"
        )

        experiment.log_metrics({
            'ic_mean': 0.045,
            'ic_ir': 1.2,
            'decay_5d': 0.85
        })

        self.mock_wandb.log.assert_called_with({
            'ic_mean': 0.045,
            'ic_ir': 1.2,
            'decay_5d': 0.85
        })

    def test_log_parameters(self):
        """测试参数记录"""
        experiment = FactorResearchExperiment(
            project="test_project",
            name="test_factor"
        )

        experiment.log_parameters({
            'lookback_period': 20,
            'rebalance_frequency': 'daily'
        })

        self.mock_wandb.config.update.assert_called()

    def test_add_tags(self):
        """测试添加标签"""
        experiment = FactorResearchExperiment(
            project="test_project",
            name="test_factor"
        )

        experiment.add_tags(['momentum', 'daily', 'hs300'])

        self.mock_wandb.run.add_tag.assert_called_with('momentum')

    def test_finish_experiment(self):
        """测试结束实验"""
        experiment = FactorResearchExperiment(
            project="test_project",
            name="test_factor"
        )

        experiment.finish()

        self.mock_wandb.finish.assert_called_once()

class TestStrategyBacktestExperiment:
    """策略回测实验测试"""

    def setup_method(self):
        self.mock_wandb = MagicMock()
        self.patch_wandb = patch('src.experiment.tracking.wandb', self.mock_wandb)
        self.patch_wandb.start()

    def teardown_method(self):
        self.patch_wandb.stop()

    def test_init_strategy_experiment(self):
        """测试策略实验初始?""
        experiment = StrategyBacktestExperiment(
            project="test_project",
            name="test_strategy",
            config={
                'strategy_type': 'momentum',
                'initial_capital': 1000000,
                'commission': 0.0003
            }
        )

        assert experiment.config['strategy_type'] == 'momentum'
        assert experiment.config['initial_capital'] == 1000000

    def test_log_equity_curve(self):
        """测试权益曲线记录"""
        experiment = StrategyBacktestExperiment(
            project="test_project",
            name="test_strategy"
        )

        equity_curve = [1000000, 1020000, 1050000, 1030000]
        experiment.log_equity_curve(equity_curve)

        self.mock_wandb.log.assert_called()

    def test_log_trade(self):
        """测试交易记录"""
        experiment = StrategyBacktestExperiment(
            project="test_project",
            name="test_strategy"
        )

        experiment.log_trade({
            'symbol': '000001.XSHE',
            'action': 'buy',
            'price': 10.5,
            'quantity': 1000
        })

        self.mock_wandb.log.assert_called()

    def test_log_summary_metrics(self):
        """测试汇总指?""
        experiment = StrategyBacktestExperiment(
            project="test_project",
            name="test_strategy"
        )

        experiment.log_summary_metrics({
            'annual_return': 0.15,
            'sharpe_ratio': 1.8,
            'max_drawdown': 0.12
        })

        self.mock_wandb.run.summary.update.assert_called()
```

### 10.3 集成测试

```python
# tests/integration/test_wandb_integration.py

import pytest
from src.experiment.tracking import (
    FactorResearchExperiment,
    ExperimentTracker
)

class TestWandbIntegration:
    """wandb集成测试"""

    @pytest.fixture
    def tracker(self):
        """创建实验追踪?""
        return ExperimentTracker(
            project="test_qingfeng_quant",
            entity="test_user"
        )

    def test_create_factor_experiment(self, tracker):
        """测试创建因子实验"""
        experiment = tracker.create_factor_experiment(
            name="test_momentum",
            config={
                'factor_type': 'momentum',
                'period': 20,
                'universe': 'hs300'
            }
        )

        assert experiment is not None
        assert experiment.name == "test_momentum"

    def test_create_strategy_experiment(self, tracker):
        """测试创建策略实验"""
        experiment = tracker.create_strategy_experiment(
            name="test_strategy",
            config={
                'strategy_type': 'momentum',
                'initial_capital': 1000000
            }
        )

        assert experiment is not None
        assert experiment.config['strategy_type'] == 'momentum'

    def test_optuna_integration(self, tracker):
        """测试Optuna集成"""
        import optuna

        def objective(trial):
            period = trial.suggest_int('period', 5, 60)
            # 模拟计算
            ic = 0.05 - abs(period - 20) * 0.001
            return ic

        study = tracker.integrate_optuna(
            study_name="test_optimization",
            objective=objective,
            n_trials=10
        )

        assert study.best_value > 0
```

### 10.4 端到端测?

```python
# tests/e2e/test_experiment_e2e.py

class TestExperimentE2E:
    """端到端测?""

    def test_full_research_to_tracking(self):
        """测试从研究到追踪的完整流?""
        # 1. 创建实验
        response = client.post("/api/v1/experiment/create", json={
            "project": "qingfeng-quant",
            "name": "momentum_factor_test",
            "type": "factor_research",
            "config": {
                "factor_type": "momentum",
                "period": 20
            }
        })
        assert response.status_code == 200
        experiment_id = response.json()["experiment_id"]

        # 2. 记录指标
        client.post(f"/api/v1/experiment/{experiment_id}/log", json={
            "metrics": {
                "ic_mean": 0.045,
                "ic_ir": 1.2
            }
        })

        # 3. 完成实验
        client.post(f"/api/v1/experiment/{experiment_id}/finish", json={
            "status": "completed"
        })

        # 4. 验证wandb中已记录
        run = wandb.Api().run(f"test_user/qingfeng-quant/momentum_factor_test")
        assert run is not None
        assert 'ic_mean' in run.summaryMetrics
```


## 11. 数据模型

### 11.1 实验配置

```python
# src/experiment/models.py

from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime
from enum import Enum

class ExperimentType(str, Enum):
    FACTOR_RESEARCH = "factor_research"
    STRATEGY_BACKTEST = "strategy_backtest"
    PARAMETER_OPTIMIZATION = "parameter_optimization"

class ExperimentConfig(BaseModel):
    """实验配置"""
    id: str
    name: str
    type: ExperimentType
    project: str
    entity: Optional[str] = None

    # 配置参数
    config: Dict = Field(default_factory=dict)

    # 元数?
    tags: List[str] = Field(default_factory=list)
    notes: Optional[str] = None

    # 时间
    created_at: datetime = Field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None

    # 状?
    status: str = "pending"

class FactorExperimentConfig(ExperimentConfig):
    """因子实验配置"""
    type: ExperimentType = ExperimentType.FACTOR_RESEARCH

    class Config:
        frozen = True

    config: Dict = Field(default_factory=dict, exclude=True)

    # 因子特有配置
    factor_type: str = Field(..., description="因子类型: momentum, value, quality...")
    universe: str = Field(default="hs300", description="股票?)
    period: int = Field(default=20, description="回望?)
    date_range: tuple = Field(..., description="回测日期范围")

class StrategyExperimentConfig(ExperimentConfig):
    """策略实验配置"""
    type: ExperimentType = ExperimentType.STRATEGY_BACKTEST

    strategy_type: str
    initial_capital: float = Field(default=1000000)
    commission: float = Field(default=0.0003)
    slippage: float = Field(default=0.0001)

class MetricRecord(BaseModel):
    """指标记录"""
    timestamp: datetime = Field(default_factory=datetime.now)
    step: Optional[int] = None
    metrics: Dict
```


## 12. wandb最佳实?

### 12.1 项目组织

```
wandb项目结构:
├── qingfeng-quant-factor      # 因子研究项目
?  ├── momentum_*             # 动量因子实验
?  ├── value_*                # 价值因子实?
?  └── quality_*               # 质量因子实验
?
├── qingfeng-quant-strategy   # 策略回测项目
?  ├── trend_*                 # 趋势策略
?  ├── mean_reversion_*        # 均值回归策?
?  └── arbitrage_*             # 套利策略
?
└── qingfeng-quant-optimization # 参数优化项目
    ├── optuna_*                # Optuna优化
    └── grid_search_*           # 网格搜索
```

### 12.2 命名规范

```python
# 实验命名规范
EXPERIMENT_NAME_FORMAT = {
    'factor': '{factor_type}_{universe}_{period}d_{timestamp}',
    'strategy': '{strategy_type}_{capital}_{timestamp}',
    'optimization': '{objective}_{n_trials}_{timestamp}'
}

# 示例
# momentum_hs300_20d_20260329
# trend_1M_20260329
# sharpe_opt_100trials_20260329
```

### 12.3 配置管理

```python
# config/wandb.yaml

wandb:
  entity: "your_username"
  projects:
    factor: "qingfeng-quant-factor"
    strategy: "qingfeng-quant-strategy"
    optimization: "qingfeng-quant-optimization"

  defaults:
    factor:
      tags: ["factor"]
      notes: "因子研究实验"
    strategy:
      tags: ["strategy"]
      notes: "策略回测实验"

  api:
    key: "${WANDB_API_KEY}"
    host: "https://api.wandb.ai"
```


## 13. 更新记录

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| v1.0 | 2026-03-29 | 初始版本 |
| v1.1 | 2026-03-29 | 补充测试策略、数据模型、最佳实?|


**维护?*: 清风量化系统
**索引**: `EXP.TRACK.001`
