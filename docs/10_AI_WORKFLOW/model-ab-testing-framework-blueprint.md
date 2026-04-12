---

module_id: MODEL_AB_TESTING_FRAMEWORK_BLUEPRINT_001

version: 1.0.0

status: Active

created_date: 2026-04-07

last_updated: 2026-04-07

owner: 首席架构师

responsibility:

  - 模型A/B测试框架蓝图设计

  - MLflow集成方案

  - 统计显著性检验流程

standard_type: 专业量化机构蓝图

applicable_scope: 舆情分析层（Layer 3）

compliance_level: 专业标准

priority: P0

estimated_effort: 50h

layer: layer_00
---




# 模型A/B测试框架蓝图 (Model A/B Testing Framework Blueprint)



> **核心职责**: 模型A/B测试框架设计和架构规划

> **职责边界**: 

> - ✅ 本文档负责：模型A/B测试框架设计和架构规划相关内容

> - ❌ 本文档不负责：其他模块内容



> **模块ID**: MATF_001

> **版本**: v1.0.0

> **创建日期**: 2026-04-07

> **Layer定位**: Layer 3 - 舆情分析层

> **优先级**: P0（阻断性）

> **预计工作量**: 50小时



---



## 📋 执行摘要



### 模块概述



模型A/B测试框架是舆情分析层的核心基础设施，为模型对比评估提供科学的测试环境。本模块使用**MLflow**作为核心实验跟踪工具，结合**Grafana**实现实时监控。



### 核心价值



- **科学评估**: 使用统计检验确保模型对比结果可靠

- **实验跟踪**: 自动记录所有实验参数和结果

- **可视化对比**: 直观展示模型性能差异

- **流量分配**: 支持灰度发布和流量分配



### 技术选型



| 技术组件 | 选型 | Stars | 说明 |

|---------|------|-------|------|

| **实验跟踪** | MLflow | 17k+ | 开源实验跟踪平台 |

| **可视化监控** | Grafana | 60k+ | 开源可视化平台 |

| **统计检验** | SciPy | - | 统计分析库 |

| **数据存储** | PostgreSQL | - | 实验数据存储 |



---



## 一、模块概述



### 1.1 设计背景



**业务需求**:

- 科学评估模型改进效果

- 支持多模型并行对比

- 建立模型版本管理机制

- 提供模型性能可视化



**技术痛点**:

- 当前缺少模型对比测试能力

- 无法科学评估模型改进效果

- 缺少统计显著性检验

- 缺少实验结果可视化



**预期价值**:

- 模型评估效率提升50%+

- 实验结果可追溯

- 支持多模型并行对比

- 提供统计显著性保证



### 1.2 模块定位



**Layer归属**: Layer 3 - 舆情分析层

**模块类别**: 模型评估模块

**架构角色**: 模型测试基础设施，为模型选择提供科学依据



---



## 二、详细架构设计



### 2.1 系统架构图



```

┌─────────────────────────────────────────────────────────────────────┐

│                    模型A/B测试框架架构                               │

├─────────────────────────────────────────────────────────────────────┤

│                                                                      │

│  ┌──────────────────────────────────────────────────────────────┐   │

│  │         MLflow (实验跟踪核心)                                 │   │

│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐          │   │

│  │  │ 实验管理    │  │ 模型注册    │  │ 模型部署    │          │   │

│  │  │ - 参数记录  │  │ - 版本控制  │  │ - 模型服务  │          │   │

│  │  │ - 指标记录  │  │ - 模型存储  │  │ - A/B测试   │          │   │

│  │  └─────────────┘  └─────────────┘  └─────────────┘          │   │

│  └──────────────────────────────────────────────────────────────┘   │

│                          ↓                                           │

│  ┌──────────────────────────────────────────────────────────────┐   │

│  │         统计检验层 (Statistical Testing)                      │   │

│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐          │   │

│  │  │ t检验       │  │ 卡方检验    │  │ 置信区间    │          │   │

│  │  │ - 均值对比  │  │ - 分布对比  │  │ - 效应量    │          │   │

│  │  └─────────────┘  └─────────────┘  └─────────────┘          │   │

│  └──────────────────────────────────────────────────────────────┘   │

│                          ↓                                           │

│  ┌──────────────────────────────────────────────────────────────┐   │

│  │         可视化层 (Visualization)                              │   │

│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐          │   │

│  │  │ Grafana     │  │ MLflow UI   │  │ 自定义报表  │          │   │

│  │  │ - 实时监控  │  │ - 实验对比  │  │ - 统计报告  │          │   │

│  │  └─────────────┘  └─────────────┘  └─────────────┘          │   │

│  └──────────────────────────────────────────────────────────────┘   │

│                          ↓                                           │

│  ┌──────────────────────────────────────────────────────────────┐   │

│  │         流量分配层 (Traffic Allocation)                       │   │

│  │  ┌─────────────────────────────────────────────────────────┐ │   │

│  │  │ Traffic Splitter                                         │ │   │

│  │  │ - 随机分配、分层分配、灰度发布                            │ │   │

│  │  └─────────────────────────────────────────────────────────┘ │   │

│  └──────────────────────────────────────────────────────────────┘   │

│                                                                      │

└─────────────────────────────────────────────────────────────────────┘

```



### 2.2 核心组件设计



#### 组件1: MLflow实验跟踪



**功能描述**:

- 记录实验参数和指标

- 管理模型版本

- 对比实验结果

- 部署模型服务



**技术实现**:

```python

import mlflow

import mlflow.sklearn



# 配置MLflow

mlflow.set_tracking_uri("http://localhost:5000")

mlflow.set_experiment("sentiment_model_ab_test")



# 开始实验

with mlflow.start_run(run_name="model_a"):

    # 记录参数

    mlflow.log_param("model_type", "BERT")

    mlflow.log_param("learning_rate", 2e-5)

    mlflow.log_param("batch_size", 32)

    

    # 训练模型

    model_a = train_model()

    

    # 记录指标

    mlflow.log_metric("accuracy", 0.92)

    mlflow.log_metric("f1_score", 0.91)

    

    # 保存模型

    mlflow.sklearn.log_model(model_a, "model")



# 对比实验

with mlflow.start_run(run_name="model_b"):

    mlflow.log_param("model_type", "FinBERT")

    mlflow.log_param("learning_rate", 1e-5)

    mlflow.log_param("batch_size", 16)

    

    model_b = train_model()

    

    mlflow.log_metric("accuracy", 0.95)

    mlflow.log_metric("f1_score", 0.94)

    

    mlflow.sklearn.log_model(model_b, "model")

```



#### 组件2: 统计显著性检验



**t检验实现**:

```python

from scipy import stats

import numpy as np



def statistical_significance_test(

    results_a: np.ndarray,

    results_b: np.ndarray,

    alpha: float = 0.05

) -> Dict:

    """统计显著性检验

    

    Args:

        results_a: 模型A的结果

        results_b: 模型B的结果

        alpha: 显著性水平

        

    Returns:

        检验结果

    """

    # t检验

    t_stat, p_value = stats.ttest_ind(results_a, results_b)

    

    # 效应量 (Cohen's d)

    pooled_std = np.sqrt(

        (np.std(results_a)**2 + np.std(results_b)**2) / 2

    )

    cohens_d = (np.mean(results_a) - np.mean(results_b)) / pooled_std

    

    # 置信区间

    mean_diff = np.mean(results_a) - np.mean(results_b)

    se = np.sqrt(np.var(results_a)/len(results_a) + np.var(results_b)/len(results_b))

    ci_low = mean_diff - 1.96 * se

    ci_high = mean_diff + 1.96 * se

    

    return {

        't_statistic': t_stat,

        'p_value': p_value,

        'is_significant': p_value < alpha,

        'cohens_d': cohens_d,

        'confidence_interval': (ci_low, ci_high),

        'mean_difference': mean_diff

    }

```



#### 组件3: 流量分配器



**流量分配实现**:

```python

import hashlib

from typing import Dict



class TrafficSplitter:

    """流量分配器"""

    

    def __init__(self, traffic_split: Dict[str, float]):

        """

        Args:

            traffic_split: 流量分配比例 {'model_a': 0.5, 'model_b': 0.5}

        """

        self.traffic_split = traffic_split

        

    def assign_model(self, user_id: str) -> str:

        """为用户分配模型

        

        Args:

            user_id: 用户ID

            

        Returns:

            分配的模型名称

        """

        # 使用哈希确保一致性

        hash_value = int(hashlib.md5(user_id.encode()).hexdigest(), 16)

        hash_percent = (hash_value % 10000) / 10000

        

        # 根据流量分配比例选择模型

        cumulative = 0

        for model, ratio in self.traffic_split.items():

            cumulative += ratio

            if hash_percent < cumulative:

                return model

                

        return list(self.traffic_split.keys())[-1]

```



---



## 三、核心功能设计



### 3.1 A/B测试流程



```

┌─────────────┐

│ 定义实验    │

│ - 目标指标  │

│ - 流量分配  │

└─────────────┘

      ↓

┌─────────────┐

│ 训练模型    │

│ - 模型A     │

│ - 模型B     │

└─────────────┘

      ↓

┌─────────────┐

│ 部署模型    │

│ - 流量分配  │

│ - 灰度发布  │

└─────────────┘

      ↓

┌─────────────┐

│ 收集数据    │

│ - 性能指标  │

│ - 用户反馈  │

└─────────────┘

      ↓

┌─────────────┐

│ 统计检验    │

│ - t检验     │

│ - 效应量    │

└─────────────┘

      ↓

┌─────────────┐

│ 决策发布    │

│ - 选择模型  │

│ - 全量发布  │

└─────────────┘

```



### 3.2 实验对比可视化



```python

import plotly.graph_objects as go

from plotly.subplots import make_subplots



def visualize_ab_test_results(results_a: Dict, results_b: Dict):

    """可视化A/B测试结果

    

    Args:

        results_a: 模型A的结果

        results_b: 模型B的结果

    """

    fig = make_subplots(

        rows=2, cols=2,

        subplot_titles=('准确率对比', 'F1分数对比', '响应时间对比', '统计显著性')

    )

    

    # 准确率对比

    fig.add_trace(

        go.Bar(name='Model A', x=['Accuracy'], y=[results_a['accuracy']]),

        row=1, col=1

    )

    fig.add_trace(

        go.Bar(name='Model B', x=['Accuracy'], y=[results_b['accuracy']]),

        row=1, col=1

    )

    

    # F1分数对比

    fig.add_trace(

        go.Bar(name='Model A', x=['F1'], y=[results_a['f1']]),

        row=1, col=2

    )

    fig.add_trace(

        go.Bar(name='Model B', x=['F1'], y=[results_b['f1']]),

        row=1, col=2

    )

    

    fig.update_layout(height=600, showlegend=True)

    fig.show()

```



---



## 四、接口设计



### 4.1 实验管理API



```python

from fastapi import FastAPI

from pydantic import BaseModel

from typing import Dict, Optional



app = FastAPI()



class Experiment(BaseModel):

    experiment_id: str

    name: str

    model_a: str

    model_b: str

    traffic_split: Dict[str, float]

    status: str  # 'running', 'completed', 'stopped'



@app.post("/api/experiments")

async def create_experiment(experiment: Experiment):

    """创建A/B测试实验"""

    # 实现创建实验逻辑

    pass



@app.get("/api/experiments/{experiment_id}")

async def get_experiment(experiment_id: str):

    """获取实验详情"""

    # 实现获取实验逻辑

    pass



@app.post("/api/experiments/{experiment_id}/start")

async def start_experiment(experiment_id: str):

    """启动实验"""

    # 实现启动实验逻辑

    pass



@app.get("/api/experiments/{experiment_id}/results")

async def get_experiment_results(experiment_id: str):

    """获取实验结果"""

    # 实现获取结果逻辑

    pass

```



---



## 五、部署方案



### 5.1 Docker部署



```yaml

version: '3.8'



services:

  mlflow:

    image: ghcr.io/mlflow/mlflow:v2.9.0

    container_name: mlflow-server

    ports:

      - "5000:5000"

    environment:

      - MLFLOW_BACKEND_STORE_URI=postgresql://mlflow:mlflow@postgres:5432/mlflow

      - MLFLOW_ARTIFACT_ROOT=/mlflow/artifacts

    volumes:

      - ./mlflow-artifacts:/mlflow/artifacts

    depends_on:

      - postgres

      

  postgres:

    image: postgres:13

    container_name: mlflow-postgres

    environment:

      - POSTGRES_DB=mlflow

      - POSTGRES_USER=mlflow

      - POSTGRES_PASSWORD=mlflow

    volumes:

      - ./postgres-data:/var/lib/postgresql/data

      

  grafana:

    image: grafana/grafana:latest

    container_name: grafana

    ports:

      - "3000:3000"

    environment:

      - GF_SECURITY_ADMIN_PASSWORD=admin

    volumes:

      - ./grafana-data:/var/lib/grafana

```



---



## 六、监控与运维



### 6.1 监控指标



| 指标名称 | 说明 | 告警阈值 |

|---------|------|---------|

| **实验数量** | 运行中的实验数量 | > 10 |

| **样本量** | 每个实验的样本量 | < 1000 |

| **显著性** | 统计显著性p值 | < 0.05 |

| **效应量** | Cohen's d效应量 | < 0.2 |

| **系统可用性** | MLflow可用性 | < 99% |



---



## 七、成本估算



### 7.1 开发成本



| 项目 | 工作量 | 说明 |

|------|--------|------|

| **MLflow部署** | 8小时 | Docker部署、配置 |

| **统计检验实现** | 12小时 | t检验、卡方检验 |

| **可视化开发** | 12小时 | Grafana仪表盘 |

| **流量分配器** | 10小时 | 流量分配逻辑 |

| **API接口开发** | 8小时 | 实验管理API |

| **总计** | **50小时** | - |



### 7.2 运维成本



| 项目 | 月度成本 | 说明 |

|------|---------|------|

| **服务器** | 200元 | 2核4G云服务器 |

| **存储** | 50元 | 100GB SSD |

| **总计** | **250元/月** | - |



---



## 八、总结与建议



### 8.1 核心优势



1. **开源免费**: MLflow和Grafana完全开源

2. **功能全面**: 支持实验跟踪、模型管理、可视化

3. **易于部署**: Docker一键部署

4. **社区活跃**: MLflow 17k+ stars，社区支持完善



### 8.2 实施建议



1. **第一阶段（1周）**: 部署MLflow和Grafana

2. **第二阶段（1-2周）**: 实现统计检验和可视化

3. **第三阶段（1周）**: 完成流量分配器和API



---



**蓝图创建时间**: 2026-04-07

**架构师**: 首席架构师

**下次更新建议**: 实施后1个月

**最终状态**: ✅ 完整蓝图已生成

