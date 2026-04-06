---
module_id: DATA_LINEAGE_TRACKING_001
version: 1.0.0
status: Blueprint
created_date: 2026-04-06
last_updated: 2026-04-06
owner: 首席架构师
standard_type: 模块蓝图
applicable_scope: 数据血缘追踪系统
compliance_level: 专业标准
parent_document: ../DATA_SOURCE_LAYER_GAP_ANALYSIS.md
dependencies:
  - OpenLineage
  - Marquez
  - Prefect
---

# 数据血缘追踪系统蓝图

## 文档职责说明

**本文档职责**: 数据血缘追踪系统设计蓝图
- 定义数据血缘追踪系统架构
- 说明血缘采集和可视化方案
- 提供影响分析和合规支持方案

**相关文档引用**:
| 文档 | 路径 | 关系 | 说明 |
|------|------|------|------|
| 差距分析 | [../DATA_SOURCE_LAYER_GAP_ANALYSIS.md](../DATA_SOURCE_LAYER_GAP_ANALYSIS.md) | 上层分析 | 架构缺失分析 |
| 数据源索引 | [../INDEX.md](../INDEX.md) | 上级索引 | 数据源模块总索引 |

**职责边界**:
- ✅ 本文档负责: 数据血缘追踪系统架构设计
- ❌ 本文档不负责: 具体实现代码（由开发团队负责）

> 清风量化系统 v5.4 - 数据血缘追踪模块
> **优先级**: 🔴 P0级（立即实施）
> **实施周期**: 1周
> **开源方案**: OpenLineage + Marquez

---

## 📋 模块概述

### 核心职责

数据血缘追踪系统负责追踪数据从源头到消费的完整路径，实现：
- 数据来源追踪
- 数据变换记录
- 影响范围分析
- 数据合规支持

### 职责边界

| 本模块负责 | 本模块不负责 |
|-----------|-------------|
| ✅ 追踪数据血缘关系 | ❌ 数据质量管理 |
| ✅ 可视化血缘图谱 | ❌ 数据版本控制 |
| ✅ 影响分析 | ❌ 数据备份恢复 |
| ✅ 血缘查询API | ❌ 数据监控告警 |

---

## 🎯 功能需求

### 核心功能

| 功能 | 描述 | 优先级 |
|------|------|--------|
| **自动血缘采集** | 自动采集数据流经路径 | 🔴 P0 |
| **血缘可视化** | 图形化展示血缘关系 | 🔴 P0 |
| **影响分析** | 分析数据变更影响范围 | 🟡 P1 |
| **血缘查询** | 提供血缘查询API | 🟡 P1 |
| **血缘告警** | 血缘异常告警 | 🟢 P2 |

### 技术指标

| 指标 | 目标值 | 测量方法 |
|------|--------|----------|
| **血缘采集延迟** | < 5秒 | 从数据产生到血缘记录 |
| **血缘查询响应** | < 1秒 | 单次血缘查询时间 |
| **血缘覆盖率** | 100% | 已追踪数据/总数据 |
| **血缘准确率** | > 99% | 正确血缘/总血缘 |

---

## 🏗️ 架构设计

### 系统架构

```
┌─────────────────────────────────────────────────────────────┐
│                   数据血缘追踪系统                            │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │                   血缘采集层                          │  │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐          │  │
│  │  │Prefect   │  │ dbt      │  │ SQL      │          │  │
│  │  │集成      │  │ 集成     │  │ 解析     │          │  │
│  │  └──────────┘  └──────────┘  └──────────┘          │  │
│  └──────────────────────────────────────────────────────┘  │
│                          │                                  │
│                          ▼                                  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │                   OpenLineage层                       │  │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐          │  │
│  │  │事件生成  │  │事件传输  │  │事件存储  │          │  │
│  │  └──────────┘  └──────────┘  └──────────┘          │  │
│  └──────────────────────────────────────────────────────┘  │
│                          │                                  │
│                          ▼                                  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │                   Marquez层                           │  │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐          │  │
│  │  │血缘存储  │  │血缘API   │  │血缘UI    │          │  │
│  │  └──────────┘  └──────────┘  └──────────┘          │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 数据流设计

```
数据源 → 数据采集 → 数据清洗 → 数据存储 → 数据服务
   │         │          │          │          │
   └─────────┴──────────┴──────────┴──────────┘
                        │
                        ▼
                  OpenLineage事件
                        │
                        ▼
                   Marquez存储
                        │
                        ▼
                  血缘图谱可视化
```

---

## 💻 技术实现

### 技术栈选择

| 组件 | 技术选型 | 选择理由 |
|------|----------|----------|
| **血缘标准** | OpenLineage | 行业标准，社区活跃 |
| **血缘存储** | Marquez | 开源免费，功能完整 |
| **血缘采集** | Python SDK | 易于集成，灵活可控 |
| **可视化** | Marquez UI | 开箱即用，交互友好 |

### 核心代码实现

#### 1. OpenLineage客户端配置

```python
"""
数据血缘追踪客户端
"""
from openlineage.client import OpenLineageClient
from openlineage.client.run import RunEvent, RunState, Run, Job
from openlineage.client.dataset import Dataset
from datetime import datetime
import uuid
from typing import List, Optional

class LineageTracker:
    """血缘追踪器"""
    
    def __init__(self, marquez_url: str = "http://localhost:5000"):
        """
        初始化血缘追踪器
        
        Args:
            marquez_url: Marquez服务地址
        """
        self.client = OpenLineageClient(url=marquez_url)
        self.namespace = "quant_system"
    
    def emit_start_event(
        self,
        job_name: str,
        inputs: List[Dataset],
        outputs: List[Dataset],
        run_id: Optional[str] = None
    ):
        """
        发送任务开始事件
        
        Args:
            job_name: 任务名称
            inputs: 输入数据集列表
            outputs: 输出数据集列表
            run_id: 运行ID（可选）
        """
        run_event = RunEvent(
            eventType=RunState.START,
            eventTime=datetime.now().isoformat(),
            run=Run(runId=run_id or str(uuid.uuid4())),
            job=Job(namespace=self.namespace, name=job_name),
            inputs=inputs,
            outputs=outputs
        )
        
        self.client.emit(run_event)
    
    def emit_complete_event(
        self,
        job_name: str,
        inputs: List[Dataset],
        outputs: List[Dataset],
        run_id: str
    ):
        """
        发送任务完成事件
        
        Args:
            job_name: 任务名称
            inputs: 输入数据集列表
            outputs: 输出数据集列表
            run_id: 运行ID
        """
        run_event = RunEvent(
            eventType=RunState.COMPLETE,
            eventTime=datetime.now().isoformat(),
            run=Run(runId=run_id),
            job=Job(namespace=self.namespace, name=job_name),
            inputs=inputs,
            outputs=outputs
        )
        
        self.client.emit(run_event)
    
    def emit_fail_event(
        self,
        job_name: str,
        run_id: str,
        error_message: str
    ):
        """
        发送任务失败事件
        
        Args:
            job_name: 任务名称
            run_id: 运行ID
            error_message: 错误信息
        """
        run_event = RunEvent(
            eventType=RunState.FAIL,
            eventTime=datetime.now().isoformat(),
            run=Run(runId=run_id),
            job=Job(namespace=self.namespace, name=job_name),
            inputs=[],
            outputs=[]
        )
        
        self.client.emit(run_event)
```

#### 2. Prefect集成

```python
"""
Prefect血缘追踪集成
"""
from prefect import task, flow
from openlineage.client.dataset import Dataset
from typing import List, Dict, Any
import pandas as pd

# 全局血缘追踪器
lineage_tracker = LineageTracker()

def with_lineage(
    job_name: str,
    input_datasets: List[str],
    output_datasets: List[str]
):
    """
    血缘追踪装饰器
    
    Args:
        job_name: 任务名称
        input_datasets: 输入数据集名称列表
        output_datasets: 输出数据集名称列表
    
    Returns:
        装饰器函数
    """
    def decorator(func):
        @task(name=job_name)
        def wrapper(*args, **kwargs):
            # 构造数据集对象
            inputs = [
                Dataset(namespace="quant_system", name=name)
                for name in input_datasets
            ]
            outputs = [
                Dataset(namespace="quant_system", name=name)
                for name in output_datasets
            ]
            
            # 生成运行ID
            run_id = str(uuid.uuid4())
            
            try:
                # 发送开始事件
                lineage_tracker.emit_start_event(
                    job_name=job_name,
                    inputs=inputs,
                    outputs=outputs,
                    run_id=run_id
                )
                
                # 执行任务
                result = func(*args, **kwargs)
                
                # 发送完成事件
                lineage_tracker.emit_complete_event(
                    job_name=job_name,
                    inputs=inputs,
                    outputs=outputs,
                    run_id=run_id
                )
                
                return result
                
            except Exception as e:
                # 发送失败事件
                lineage_tracker.emit_fail_event(
                    job_name=job_name,
                    run_id=run_id,
                    error_message=str(e)
                )
                raise
        
        return wrapper
    return decorator

# 使用示例
@with_lineage(
    job_name="fetch_stock_data",
    input_datasets=["external:akshare"],
    output_datasets=["clickhouse:stock_prices"]
)
def fetch_stock_data(symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
    """获取股票数据"""
    import akshare as ak
    
    df = ak.stock_zh_a_hist(
        symbol=symbol,
        start_date=start_date,
        end_date=end_date,
        adjust="qfq"
    )
    
    return df

@with_lineage(
    job_name="clean_stock_data",
    input_datasets=["clickhouse:stock_prices"],
    output_datasets=["clickhouse:stock_prices_cleaned"]
)
def clean_stock_data(df: pd.DataFrame) -> pd.DataFrame:
    """清洗股票数据"""
    df = df.dropna()
    df = df.drop_duplicates()
    return df

@flow(name="stock_data_pipeline")
def stock_data_pipeline(symbol: str):
    """股票数据流水线"""
    raw_data = fetch_stock_data(symbol, "20240101", "20241231")
    clean_data = clean_stock_data(raw_data)
    return clean_data
```

#### 3. SQL血缘解析

```python
"""
SQL血缘解析器
"""
import sqlparse
from sqlparse.sql import IdentifierList, Identifier
from sqlparse.tokens import Keyword, DML
from typing import List, Tuple

class SQLLineageParser:
    """SQL血缘解析器"""
    
    def extract_lineage(self, sql: str) -> Tuple[List[str], List[str]]:
        """
        从SQL语句中提取血缘关系
        
        Args:
            sql: SQL语句
        
        Returns:
            (输入表列表, 输出表列表)
        """
        parsed = sqlparse.parse(sql)[0]
        
        input_tables = []
        output_tables = []
        
        # 提取FROM和JOIN后的表名
        from_seen = False
        join_seen = False
        insert_seen = False
        
        for token in parsed.tokens:
            if token.ttype is Keyword and token.value.upper() in ['FROM', 'JOIN']:
                from_seen = True
                join_seen = True
                continue
            
            if token.ttype is Keyword and token.value.upper() == 'INSERT':
                insert_seen = True
                continue
            
            if token.ttype is Keyword and token.value.upper() == 'INTO':
                continue
            
            if from_seen or join_seen:
                if isinstance(token, IdentifierList):
                    for identifier in token.get_identifiers():
                        input_tables.append(identifier.get_real_name())
                elif isinstance(token, Identifier):
                    input_tables.append(token.get_real_name())
                from_seen = False
                join_seen = False
            
            if insert_seen:
                if isinstance(token, Identifier):
                    output_tables.append(token.get_real_name())
                insert_seen = False
        
        return input_tables, output_tables

# 使用示例
parser = SQLLineageParser()

sql = """
INSERT INTO stock_prices_cleaned
SELECT symbol, date, close
FROM stock_prices
WHERE close > 0
"""

input_tables, output_tables = parser.extract_lineage(sql)
print(f"输入表: {input_tables}")  # ['stock_prices']
print(f"输出表: {output_tables}")  # ['stock_prices_cleaned']
```

#### 4. 血缘查询API

```python
"""
血缘查询API
"""
from fastapi import FastAPI, HTTPException
from typing import List, Dict, Any
import requests

app = FastAPI(title="Lineage Query API")

class LineageQueryService:
    """血缘查询服务"""
    
    def __init__(self, marquez_url: str = "http://localhost:5000"):
        self.marquez_url = marquez_url
    
    def get_upstream_lineage(
        self,
        dataset_name: str,
        depth: int = 3
    ) -> Dict[str, Any]:
        """
        获取上游血缘
        
        Args:
            dataset_name: 数据集名称
            depth: 血缘深度
        
        Returns:
            上游血缘图谱
        """
        url = f"{self.marquez_url}/api/v1/namespaces/quant_system/datasets/{dataset_name}/lineage"
        params = {"depth": depth}
        
        response = requests.get(url, params=params)
        
        if response.status_code != 200:
            raise HTTPException(status_code=404, detail="Dataset not found")
        
        return response.json()
    
    def get_downstream_lineage(
        self,
        dataset_name: str,
        depth: int = 3
    ) -> Dict[str, Any]:
        """
        获取下游血缘
        
        Args:
            dataset_name: 数据集名称
            depth: 血缘深度
        
        Returns:
            下游血缘图谱
        """
        url = f"{self.marquez_url}/api/v1/namespaces/quant_system/datasets/{dataset_name}/lineage"
        params = {"depth": depth, "direction": "downstream"}
        
        response = requests.get(url, params=params)
        
        if response.status_code != 200:
            raise HTTPException(status_code=404, detail="Dataset not found")
        
        return response.json()
    
    def get_impact_analysis(
        self,
        dataset_name: str
    ) -> Dict[str, Any]:
        """
        影响分析
        
        Args:
            dataset_name: 数据集名称
        
        Returns:
            影响范围分析结果
        """
        downstream = self.get_downstream_lineage(dataset_name)
        
        affected_datasets = []
        affected_jobs = []
        
        for node in downstream.get("graph", {}).get("nodes", []):
            if node["type"] == "DATASET":
                affected_datasets.append(node["name"])
            elif node["type"] == "JOB":
                affected_jobs.append(node["name"])
        
        return {
            "source_dataset": dataset_name,
            "affected_datasets": affected_datasets,
            "affected_jobs": affected_jobs,
            "total_impact": len(affected_datasets) + len(affected_jobs)
        }

# API端点
@app.get("/api/v1/lineage/{dataset_name}/upstream")
async def get_upstream(dataset_name: str, depth: int = 3):
    """获取上游血缘"""
    service = LineageQueryService()
    return service.get_upstream_lineage(dataset_name, depth)

@app.get("/api/v1/lineage/{dataset_name}/downstream")
async def get_downstream(dataset_name: str, depth: int = 3):
    """获取下游血缘"""
    service = LineageQueryService()
    return service.get_downstream_lineage(dataset_name, depth)

@app.get("/api/v1/lineage/{dataset_name}/impact")
async def get_impact(dataset_name: str):
    """影响分析"""
    service = LineageQueryService()
    return service.get_impact_analysis(dataset_name)
```

---

## 🚀 部署方案

### 环境要求

| 组件 | 版本要求 | 说明 |
|------|----------|------|
| **Python** | >= 3.9 | 运行环境 |
| **Docker** | >= 20.0 | 容器化部署 |
| **Marquez** | >= 0.30.0 | 血缘存储 |
| **PostgreSQL** | >= 13.0 | 元数据存储 |

### 部署步骤

#### 1. 部署Marquez

```bash
# 克隆Marquez仓库
git clone https://github.com/MarquezProject/marquez.git
cd marquez

# 启动Marquez
docker-compose up -d

# 访问Web UI
# http://localhost:3000
```

#### 2. 配置OpenLineage

```bash
# 安装依赖
pip install openlineage-python prefect

# 配置环境变量
export MARQUEZ_URL=http://localhost:5000
export OPENLINEAGE_NAMESPACE=quant_system
```

#### 3. 集成到现有系统

```python
# 在Prefect配置中添加OpenLineage
# ~/.prefect/profile.toml

[openlineage]
url = "http://localhost:5000"
namespace = "quant_system"
```

---

## 📊 监控指标

### 关键指标

| 指标 | 目标值 | 告警阈值 |
|------|--------|----------|
| **血缘采集成功率** | > 99% | < 95% |
| **血缘查询延迟** | < 1秒 | > 3秒 |
| **血缘存储大小** | < 10GB | > 50GB |
| **Marquez可用性** | > 99.9% | < 99% |

### 监控脚本

```python
"""
血缘系统监控脚本
"""
import requests
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class LineageMonitor:
    """血缘系统监控器"""
    
    def __init__(self, marquez_url: str):
        self.marquez_url = marquez_url
    
    def check_health(self) -> bool:
        """检查Marquez健康状态"""
        try:
            response = requests.get(f"{self.marquez_url}/health")
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Marquez health check failed: {e}")
            return False
    
    def check_lineage_coverage(self) -> float:
        """检查血缘覆盖率"""
        # 获取所有数据集
        response = requests.get(f"{self.marquez_url}/api/v1/namespaces/quant_system/datasets")
        datasets = response.json()
        
        # 计算覆盖率
        total_datasets = len(datasets.get("datasets", []))
        datasets_with_lineage = sum(
            1 for ds in datasets.get("datasets", [])
            if ds.get("fields") and len(ds.get("fields")) > 0
        )
        
        coverage = datasets_with_lineage / total_datasets if total_datasets > 0 else 0
        
        logger.info(f"Lineage coverage: {coverage:.2%}")
        return coverage
    
    def run_monitoring(self):
        """运行监控"""
        health = self.check_health()
        coverage = self.check_lineage_coverage()
        
        if not health:
            self.send_alert("Marquez服务不可用")
        
        if coverage < 0.95:
            self.send_alert(f"血缘覆盖率过低: {coverage:.2%}")
    
    def send_alert(self, message: str):
        """发送告警"""
        logger.warning(f"ALERT: {message}")
        # TODO: 集成告警系统（邮件、钉钉等）
```

---

## 📝 使用指南

### 快速开始

```python
# 1. 初始化血缘追踪器
from lineage_tracker import LineageTracker

tracker = LineageTracker(marquez_url="http://localhost:5000")

# 2. 在数据任务中添加血缘追踪
@with_lineage(
    job_name="my_data_job",
    input_datasets=["source_table"],
    output_datasets=["target_table"]
)
def my_data_job():
    # 数据处理逻辑
    pass

# 3. 查询血缘
service = LineageQueryService()
upstream = service.get_upstream_lineage("stock_prices")
downstream = service.get_downstream_lineage("stock_prices")
impact = service.get_impact_analysis("stock_prices")
```

### 最佳实践

1. **命名规范**
   - 数据集命名: `{database}.{table}`
   - 任务命名: `{action}_{target}`
   - 命名空间: `quant_system`

2. **血缘采集**
   - 所有数据任务都应添加血缘追踪
   - 及时发送开始、完成、失败事件
   - 确保输入输出数据集准确

3. **血缘查询**
   - 定期检查血缘覆盖率
   - 重要变更前进行影响分析
   - 保留血缘历史记录

---

## 🔗 相关文档

- [OpenLineage官方文档](https://openlineage.io/docs/)
- [Marquez官方文档](https://marquezproject.github.io/marquez/)
- [数据源层架构缺失分析](../DATA_SOURCE_LAYER_GAP_ANALYSIS.md)

---

**文档版本**: v1.0.0 | **创建日期**: 2026-04-06 | **状态**: ✅ 蓝图完成 | **作者**: 首席架构师
