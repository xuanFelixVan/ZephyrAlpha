---
module_id: HYPERPARAMETER_OPTIMIZATION_ML_001
version: 1.0.0
status: Active
created_date: 2026-04-07
last_updated: 2026-04-07
owner: 系统架构师
responsibility:
  - 提供超参数优化的完整架构设计和技术选型
layer: Layer 4 (机器学习层)
standard_type: 专业量化机构蓝图文档
priority: P0核心
estimated_hours: 25
---

# 超参数优化蓝图

> **核心职责**: 提供超参数优化的完整架构设计，实现自动调参、贝叶斯优化和分布式优化能力
> **职责边界**: 
> - ✅ 本文档负责：超参数搜索、优化算法、实验管理
> - ❌ 本文档不负责：模型训练逻辑、数据处理

---

## 1. 概述

### 1.1 设计背景

**业务需求**:
- 模型超参数调优耗时耗力
- 需要系统化的调参方法
- 支持分布式并行优化

**技术痛点**:
- 手动调参效率低
- 网格搜索计算成本高
- 难以追踪调参历史

**预期价值**:
- 调参效率提升80%
- 模型性能提升10-20%
- 自动化程度提升100%

### 1.2 开源方案选型

| 项目 | 推荐度 | Stars | 许可证 | 特点 |
|------|--------|-------|--------|------|
| **Optuna** | ⭐⭐⭐⭐⭐ | 10k+ | MIT | 剪枝算法、易用、可视化 |
| Ray Tune | ⭐⭐⭐⭐⭐ | 32k+ | Apache 2.0 | 分布式、可扩展 |
| Hyperopt | ⭐⭐⭐⭐ | 7k+ | BSD | 经典方案、TPE算法 |
| Nevergrad | ⭐⭐⭐⭐ | 1k+ | BSD | 无梯度优化 |

**推荐方案**: **Optuna (首选) + Ray Tune (分布式)**

### 1.3 为什么选择Optuna

| 优势 | 说明 |
|------|------|
| 剪枝算法 | 自动剪枝低效试验，节省计算资源 |
| 易用性 | Define-by-run风格，灵活定义搜索空间 |
| 可视化 | 内置丰富的可视化工具 |
| 采样算法 | TPE、CMA-ES、Grid等多种算法 |
| 分布式 | 支持多进程、多节点并行 |

---

## 2. 系统架构

### 2.1 整体架构

```
┌─────────────────────────────────────────────────────────────┐
│                    超参数优化系统架构                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                  优化引擎层                          │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐          │   │
│  │  │  Optuna  │  │ Ray Tune │  │ Hyperopt │          │   │
│  │  │ 本地优化 │  │ 分布式   │  │ 经典算法 │          │   │
│  │  └──────────┘  └──────────┘  └──────────┘          │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                  采样算法层                          │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐          │   │
│  │  │   TPE    │  │  CMA-ES  │  │  Grid    │          │   │
│  │  │ 贝叶斯   │  │ 进化策略│  │ 网格搜索 │          │   │
│  │  └──────────┘  └──────────┘  └──────────┘          │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                  剪枝策略层                          │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐          │   │
│  │  │ Median   │  │ Percentile│  │  Custom  │          │   │
│  │  │ Stopping │  │  Stopping │  │  Pruner  │          │   │
│  │  └──────────┘  └──────────┘  └──────────┘          │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                  存储与可视化层                      │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐          │   │
│  │  │  SQLite  │  │  MySQL   │  │ Dashboard│          │   │
│  │  │ 本地存储 │  │ 远程存储 │  │ 可视化   │          │   │
│  │  └──────────┘  └──────────┘  └──────────┘          │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 核心组件

| 组件 | 职责 | 技术选型 |
|------|------|---------|
| **优化引擎** | 超参数搜索 | Optuna |
| **采样算法** | 参数采样策略 | TPE/CMA-ES |
| **剪枝策略** | 提前终止低效试验 | MedianPruner |
| **存储后端** | 试验结果存储 | SQLite/MySQL |
| **可视化** | 优化过程可视化 | Optuna Dashboard |

---

## 3. 详细设计

### 3.1 基础优化器

```python
import optuna
from optuna.samplers import TPESampler, CmaEsSampler
from optuna.pruners import MedianPruner, PercentilePruner
import numpy as np
from typing import Dict, Any, Callable
import mlflow

class HyperparameterOptimizer:
    """超参数优化器"""
    
    def __init__(
        self,
        study_name: str,
        storage: str = "sqlite:///optuna.db",
        sampler: str = "tpe",
        pruner: str = "median"
    ):
        self.study_name = study_name
        self.storage = storage
        
        # 选择采样器
        self.sampler = self._get_sampler(sampler)
        
        # 选择剪枝器
        self.pruner = self._get_pruner(pruner)
        
    def _get_sampler(self, sampler: str):
        """获取采样器"""
        samplers = {
            "tpe": TPESampler(seed=42),
            "cma_es": CmaEsSampler(seed=42),
            "random": optuna.samplers.RandomSampler(seed=42),
            "grid": optuna.samplers.GridSampler()
        }
        return samplers.get(sampler, TPESampler(seed=42))
    
    def _get_pruner(self, pruner: str):
        """获取剪枝器"""
        pruners = {
            "median": MedianPruner(n_startup_trials=5),
            "percentile": PercentilePruner(25.0, n_startup_trials=5),
            "none": optuna.pruners.NopPruner()
        }
        return pruners.get(pruner, MedianPruner())
    
    def create_study(self, direction: str = "maximize"):
        """创建优化研究"""
        return optuna.create_study(
            study_name=self.study_name,
            storage=self.storage,
            sampler=self.sampler,
            pruner=self.pruner,
            direction=direction,
            load_if_exists=True
        )
    
    def optimize(
        self,
        objective: Callable,
        n_trials: int = 100,
        timeout: int = None,
        n_jobs: int = 1
    ):
        """执行优化"""
        study = self.create_study()
        
        study.optimize(
            objective,
            n_trials=n_trials,
            timeout=timeout,
            n_jobs=n_jobs,
            show_progress_bar=True
        )
        
        return study
```

### 3.2 量化模型优化示例

```python
class QuantModelOptimizer(HyperparameterOptimizer):
    """量化模型超参数优化器"""
    
    def define_search_space(self, trial: optuna.Trial) -> Dict[str, Any]:
        """定义搜索空间"""
        params = {
            # 学习率
            "learning_rate": trial.suggest_float(
                "learning_rate", 1e-5, 1e-1, log=True
            ),
            
            # 批次大小
            "batch_size": trial.suggest_categorical(
                "batch_size", [16, 32, 64, 128, 256]
            ),
            
            # 隐藏层维度
            "hidden_dim": trial.suggest_categorical(
                "hidden_dim", [64, 128, 256, 512]
            ),
            
            # 层数
            "num_layers": trial.suggest_int("num_layers", 1, 4),
            
            # Dropout
            "dropout": trial.suggest_float("dropout", 0.0, 0.5),
            
            # 优化器
            "optimizer": trial.suggest_categorical(
                "optimizer", ["adam", "adamw", "sgd"]
            ),
            
            # 权重衰减
            "weight_decay": trial.suggest_float(
                "weight_decay", 1e-6, 1e-2, log=True
            ),
            
            # 时序窗口
            "lookback_window": trial.suggest_int("lookback_window", 10, 100),
            
            # 预测步长
            "prediction_horizon": trial.suggest_int("prediction_horizon", 1, 20)
        }
        
        return params
    
    def objective(self, trial: optuna.Trial) -> float:
        """优化目标函数"""
        # 获取超参数
        params = self.define_search_space(trial)
        
        # 训练模型
        with mlflow.start_run(nested=True):
            # 记录参数
            mlflow.log_params(params)
            
            # 训练和验证
            model = self.train_model(params)
            
            # 剪枝检查
            for epoch in range(params["num_epochs"]):
                train_loss = self.train_epoch(model, epoch)
                val_loss = self.validate_epoch(model, epoch)
                
                # 记录指标
                mlflow.log_metric("train_loss", train_loss, step=epoch)
                mlflow.log_metric("val_loss", val_loss, step=epoch)
                
                # 报告中间结果用于剪枝
                trial.report(val_loss, epoch)
                
                # 检查是否应该剪枝
                if trial.should_prune():
                    raise optuna.TrialPruned()
            
            # 最终评估
            sharpe_ratio = self.evaluate_model(model)
            mlflow.log_metric("sharpe_ratio", sharpe_ratio)
            
        return sharpe_ratio
```

### 3.3 分布式优化

```python
from ray import tune
from ray.tune.search.optuna import OptunaSearch
from ray.tune.schedulers import ASHAScheduler

class DistributedOptimizer:
    """分布式超参数优化器"""
    
    def __init__(self, num_samples: int = 100, max_concurrent: int = 4):
        self.num_samples = num_samples
        self.max_concurrent = max_concurrent
        
    def define_config(self):
        """定义配置空间"""
        return {
            "learning_rate": tune.loguniform(1e-5, 1e-1),
            "batch_size": tune.choice([16, 32, 64, 128, 256]),
            "hidden_dim": tune.choice([64, 128, 256, 512]),
            "dropout": tune.uniform(0.0, 0.5),
            "optimizer": tune.choice(["adam", "adamw", "sgd"])
        }
    
    def trainable(self, config):
        """可训练函数"""
        import torch
        
        model = self.build_model(config)
        optimizer = self.get_optimizer(model, config)
        
        for epoch in range(config["num_epochs"]):
            train_loss = self.train_epoch(model, optimizer, config)
            val_loss = self.validate_epoch(model, config)
            
            # 报告结果
            tune.report(
                train_loss=train_loss,
                val_loss=val_loss,
                sharpe_ratio=self.calculate_sharpe(model)
            )
    
    def optimize(self):
        """执行分布式优化"""
        # 配置调度器
        scheduler = ASHAScheduler(
            metric="sharpe_ratio",
            mode="max",
            max_t=100,
            grace_period=10,
            reduction_factor=2
        )
        
        # 配置搜索算法
        search_alg = OptunaSearch(
            metric="sharpe_ratio",
            mode="max"
        )
        
        # 执行优化
        result = tune.run(
            self.trainable,
            config=self.define_config(),
            num_samples=self.num_samples,
            scheduler=scheduler,
            search_alg=search_alg,
            resources_per_trial={
                "cpu": 2,
                "gpu": 0.5
            },
            max_concurrent_trials=self.max_concurrent
        )
        
        return result
```

### 3.4 多目标优化

```python
class MultiObjectiveOptimizer:
    """多目标优化器"""
    
    def __init__(self, study_name: str):
        self.study_name = study_name
        
    def create_multi_objective_study(self):
        """创建多目标研究"""
        return optuna.create_study(
            study_name=self.study_name,
            directions=["maximize", "minimize"],  # 收益最大化，风险最小化
            sampler=TPESampler(seed=42)
        )
    
    def multi_objective_objective(self, trial: optuna.Trial):
        """多目标优化函数"""
        params = self.define_search_space(trial)
        
        model = self.train_model(params)
        
        # 计算多个目标
        returns = self.calculate_returns(model)
        risk = self.calculate_risk(model)
        
        return returns, risk  # 返回多个目标值
    
    def optimize(self, n_trials: int = 100):
        """执行多目标优化"""
        study = self.create_multi_objective_study()
        
        study.optimize(
            self.multi_objective_objective,
            n_trials=n_trials
        )
        
        # 获取Pareto前沿
        pareto_front = study.best_trials
        
        return pareto_front
```

---

## 4. 使用示例

### 4.1 基本使用

```python
# 创建优化器
optimizer = HyperparameterOptimizer(
    study_name="quant_model_optimization",
    storage="sqlite:///optuna.db",
    sampler="tpe",
    pruner="median"
)

# 执行优化
study = optimizer.optimize(
    objective=objective_function,
    n_trials=100,
    n_jobs=4
)

# 获取最佳参数
best_params = study.best_params
best_value = study.best_value

print(f"最佳参数: {best_params}")
print(f"最佳值: {best_value}")
```

### 4.2 可视化

```python
import optuna.visualization as vis

# 参数重要性图
fig = vis.plot_param_importances(study)
fig.show()

# 优化历史图
fig = vis.plot_optimization_history(study)
fig.show()

# 切片图
fig = vis.plot_slice(study)
fig.show()

# 等高线图
fig = vis.plot_contour(study)
fig.show()

# Pareto前沿（多目标）
fig = vis.plot_pareto_front(study)
fig.show()
```

### 4.3 与MLflow集成

```python
class MLflowOptunaCallback:
    """MLflow回调函数"""
    
    def __call__(self, study, trial):
        with mlflow.start_run(run_name=f"trial_{trial.number}"):
            # 记录参数
            mlflow.log_params(trial.params)
            
            # 记录指标
            mlflow.log_metric("value", trial.value)
            
            # 记录状态
            mlflow.set_tag("state", trial.state.name)
            
            # 如果是最佳试验，记录标签
            if trial.number == study.best_trial.number:
                mlflow.set_tag("best", True)

# 使用回调
study.optimize(
    objective,
    n_trials=100,
    callbacks=[MLflowOptunaCallback()]
)
```

---

## 5. 搜索空间定义

### 5.1 常用参数类型

```python
def define_search_space(trial: optuna.Trial):
    """完整的搜索空间定义示例"""
    
    params = {
        # 浮点数参数
        "learning_rate": trial.suggest_float(
            "learning_rate", 1e-5, 1e-1, log=True
        ),
        
        # 整数参数
        "num_layers": trial.suggest_int("num_layers", 1, 6),
        
        # 类别参数
        "optimizer": trial.suggest_categorical(
            "optimizer", ["adam", "adamw", "sgd", "rmsprop"]
        ),
        
        # 条件参数
        "hidden_dim": trial.suggest_categorical(
            "hidden_dim", [64, 128, 256, 512]
        ),
        
        # 条件逻辑
        "use_batch_norm": trial.suggest_categorical(
            "use_batch_norm", [True, False]
        ),
        
        # 嵌套条件
        "batch_norm_momentum": trial.suggest_float(
            "batch_norm_momentum", 0.9, 0.99
        ) if trial.params.get("use_batch_norm") else None
    }
    
    return params
```

### 5.2 量化专用参数

```python
def define_quant_search_space(trial: optuna.Trial):
    """量化模型专用搜索空间"""
    
    return {
        # 模型架构
        "model_type": trial.suggest_categorical(
            "model_type", ["lstm", "gru", "transformer", "tcn"]
        ),
        
        # 时序参数
        "lookback_window": trial.suggest_int("lookback_window", 20, 200),
        "prediction_horizon": trial.suggest_int("prediction_horizon", 1, 30),
        
        # 特征参数
        "num_features": trial.suggest_int("num_features", 10, 100),
        "feature_selection_threshold": trial.suggest_float(
            "feature_selection_threshold", 0.01, 0.1
        ),
        
        # 训练参数
        "learning_rate": trial.suggest_float(
            "learning_rate", 1e-5, 1e-2, log=True
        ),
        "batch_size": trial.suggest_categorical(
            "batch_size", [32, 64, 128, 256]
        ),
        
        # 正则化
        "dropout": trial.suggest_float("dropout", 0.0, 0.5),
        "weight_decay": trial.suggest_float(
            "weight_decay", 1e-6, 1e-2, log=True
        ),
        
        # 损失函数
        "loss_function": trial.suggest_categorical(
            "loss_function", ["mse", "mae", "huber", "quantile"]
        )
    }
```

---

## 6. 高级功能

### 6.1 集成优化

```python
class EnsembleOptimizer:
    """集成模型优化器"""
    
    def optimize_ensemble(self, trial: optuna.Trial):
        """优化集成模型"""
        # 选择基础模型
        model_types = trial.suggest_categorical(
            "model_types",
            [["lstm", "gru"], ["lstm", "transformer"], ["gru", "transformer"]]
        )
        
        # 为每个模型优化权重
        weights = []
        for i, model_type in enumerate(model_types):
            weight = trial.suggest_float(f"weight_{model_type}", 0.0, 1.0)
            weights.append(weight)
        
        # 归一化权重
        total_weight = sum(weights)
        weights = [w / total_weight for w in weights]
        
        # 训练集成模型
        ensemble = self.train_ensemble(model_types, weights)
        
        return self.evaluate_ensemble(ensemble)
```

### 6.2 约束优化

```python
def constrained_objective(trial: optuna.Trial):
    """带约束的优化目标"""
    params = define_search_space(trial)
    
    model = train_model(params)
    
    # 主目标
    sharpe_ratio = calculate_sharpe(model)
    
    # 约束条件
    max_drawdown = calculate_max_drawdown(model)
    
    # 如果约束不满足，返回惩罚值
    if max_drawdown > 0.2:  # 最大回撤不超过20%
        return -1e6  # 惩罚值
    
    return sharpe_ratio
```

---

## 7. 监控与可视化

### 7.1 Optuna Dashboard

```bash
# 安装
pip install optuna-dashboard

# 启动
optuna-dashboard sqlite:///optuna.db

# 访问
http://localhost:8080
```

### 7.2 监控指标

| 指标 | 说明 | 告警阈值 |
|------|------|---------|
| 试验完成率 | 完成试验/总试验 | < 80% |
| 剪枝率 | 被剪枝试验/总试验 | > 60% |
| 最佳值改进 | 连续N试验无改进 | N > 20 |
| 计算时间 | 平均试验时间 | > 1小时 |

---

## 8. 成本估算

### 8.1 开发成本

| 阶段 | 工作量 | 说明 |
|------|--------|------|
| 环境搭建 | 4h | Optuna + Ray配置 |
| 搜索空间定义 | 6h | 参数空间设计 |
| 集成开发 | 8h | MLflow集成 |
| 测试验证 | 4h | 功能测试 |
| 文档编写 | 3h | 使用文档 |
| **总计** | **25h** | |

### 8.2 计算成本

| 项目 | 成本 | 说明 |
|------|------|------|
| 本地优化 | $0 | 使用本地GPU |
| 云端优化 | $50-200/月 | 按需使用 |
| 存储 | $5/月 | SQLite/MySQL |

---

## 9. 总结

### 9.1 核心价值

| 价值点 | 说明 |
|--------|------|
| 效率提升 | 自动调参，效率提升80% |
| 性能提升 | 找到最优参数，性能提升10-20% |
| 资源节省 | 剪枝算法节省50%计算资源 |
| 可复现 | 完整记录调参历史 |

### 9.2 最佳实践

1. ✅ 从粗粒度搜索开始，逐步细化
2. ✅ 使用剪枝算法节省计算资源
3. ✅ 与MLflow集成记录完整历史
4. ✅ 使用可视化工具分析结果
5. ✅ 分布式优化加速大规模搜索

---

**蓝图版本**: v1.0.0
**创建日期**: 2026-04-07
**维护者**: 系统架构师
