---
module_id: FULL_PROCESS_DATA_PERSISTENCE_001
version: 1.0.0
status: Active
created_date: 2026-04-02
last_updated: 2026-04-02
owner: 首席架构师
layer: Layer 4 (机器学习层)
standard_type: 专业机构级蓝图
applicable_scope: 全流程数据保存与追踪
compliance_level: 专业标准
parent_document: INDEX.md
implementation_status: 设计阶段
reference_models:
  - MLflow Tracking Server
  - Data Lineage System
  - Experiment Management
related_documents:
  - AI_WORKFLOW_LOGGER_BLUEPRINT.md
  - POST_TRADE_REVIEW_BLUEPRINT.md
  - OPEN_SOURCE_INTEGRATION_BLUEPRINT.md
responsibility:
  - 数据质量 (Layer 1)
---


## 文档职责说明

**本文档职责**: 全流程数据保存机制蓝图
- 实验追踪、数据血缘、版本控制、数据治理

# 全流程数据保存机制蓝

> **版本**: v1.0
> **创建日期**: 2026-04-02
> **实施周期**: 1
> **核心定位**: 系统数据持久化的基础设施
> **技术栈**: MLflow + SQLite + Parquet

---

## 一、概

### 1.1 蓝图定位

本文档是清风量化系统*全流程数据保存机制蓝*,旨在实现:

- ✅ **因子实验追踪**: 追踪因子计算、IC分析、回测全过程
- ✅ **策略回测追踪**: 追踪策略开发、参数优化、回测执行全过程
- ✅ **AI工作追踪**: 追踪AI会话、决策、效果评估全过程
- ✅ **数据血缘追*: 追踪数据从源头到使用的完整链
- ✅ **版本控制**: 管理所有数据和模型的版

### 1.2 核心价值

**对个人开发者的价值:
1. **实验可复现: 任何实验都可以完整复现
2. **数据可追溯: 数据来源和处理过程清晰可查
3. **版本可管*: 轻松管理数据和模型的版本
4. **协作更高*: 为未来团队协作打下基础

**对系统的价值:
1. **数据治理**: 建立完善的数据治理体
2. **质量控制**: 通过数据追踪提升数据质量
3. **审计合规**: 满足专业机构的审计要
4. **AI训练**: 为AI提供高质量训练数

### 1.3 Layer定位

```
Layer 0: 数据(Data Layer)
    ├── 数据持久化子系统
    ├── 数据血缘子系统
    ├── 版本控制子系
    └── 数据治理子系
```

**架构位置**: 位于Layer 0(数据,是整个系统的数据基础设施

---

## 二、架构设

### 2.1 整体架构

```
┌─────────────────────────────────────────────────────────────
             全流程数据保存机制架                          
├─────────────────────────────────────────────────────────────
                                                            
 ┌─────────────────────────────────────────────────────  
          实验追踪(Experiment Tracking)              
  ├─ 因子实验追踪                                       
  ├─ 策略实验追踪                                       
  ├─ AI工作追踪                                         
  └─ 参数优化追踪                                       
 └─────────────────────────────────────────────────────  
                                                          
 ┌─────────────────────────────────────────────────────  
          数据血缘层 (Data Lineage)                     
  ├─ 数据源追                                        
  ├─ 数据处理追踪                                       
  ├─ 数据使用追踪                                       
  └─ 数据质量追踪                                       
 └─────────────────────────────────────────────────────  
                                                          
 ┌─────────────────────────────────────────────────────  
          版本控制(Version Control)                  
  ├─ 数据版本管理                                       
  ├─ 模型版本管理                                       
  ├─ 配置版本管理                                       
  └─ 代码版本管理                                       
 └─────────────────────────────────────────────────────  
                                                          
 ┌─────────────────────────────────────────────────────  
          数据治理(Data Governance)                  
  ├─ 数据质量监控                                       
  ├─ 数据访问控制                                       
  ├─ 数据生命周期管理                                   
  └─ 数据合规审计                                       
 └─────────────────────────────────────────────────────  
                                                            
└─────────────────────────────────────────────────────────────
```

### 2.2 数据流设

```
数据产生 数据追踪 数据存储 数据血数据版本 数据治理
                                                           
    └────────────────── 数据复用 ←───────────────────────────
```

**数据流说*:
1. **数据产生**: 系统各模块产生数
2. **数据追踪**: MLflow自动追踪数据产生过程
3. **数据存储**: 数据持久化到存储系统
4. **数据血*: 记录数据的来源和处理过程
5. **数据版本**: 管理数据的版本信
6. **数据治理**: 监控数据质量和合规
7. **数据复用**: 在新实验中复用历史数

### 2.3 核心组件设计

#### 组件1: ExperimentTracker (实验追踪

**职责**: 追踪所有实验的全过

**输入**:
- experiment_name: 实验名称
- experiment_type: 实验类型

**输出**:
- experiment_id: 实验ID

**接口**:
```python
def track_experiment(experiment_name: str, experiment_type: str) -> str:
    """追踪实验"""
    pass
```

#### 组件2: DataLineageTracker (数据血缘追踪器)

**职责**: 追踪数据的完整血缘关

**输入**:
- data_id: 数据ID
- source: 数据
- transformations: 数据处理过程

**输出**:
- lineage_record: 血缘记

**接口**:
```python
def track_lineage(data_id: str, source: str, transformations: list) -> dict:
    """追踪数据血""
    pass
```

#### 组件3: VersionController (版本控制

**职责**: 管理数据和模型的版本

**输入**:
- artifact_path: 文件路径
- version_tag: 版本标签

**输出**:
- version_id: 版本ID

**接口**:
```python
def create_version(artifact_path: str, version_tag: str) -> str:
    """创建版本"""
    pass
```

#### 组件4: DataGovernanceManager (数据治理管理

**职责**: 管理数据质量和合规

**输入**:
- data_id: 数据ID

**输出**:
- governance_report: 治理报告

**接口**:
```python
def check_governance(data_id: str) -> dict:
    """检查数据治""
    pass
```

---

## 三、数据模

### 3.1 实验(experiments)

| 字段| 类型 | 说明 | 示例 |
|--------|------|------|------|
| experiment_id | VARCHAR(64) | 实验ID (主键) | exp_20260402_001 |
| experiment_name | VARCHAR(256) | 实验名称 | momentum_factor_optimization |
| experiment_type | VARCHAR(32) | 实验类型 | factor_experiment |
| status | VARCHAR(16) | 状| running |
| start_time | DATETIME | 开始时| 2026-04-02 10:00:00 |
| end_time | DATETIME | 结束时间 | NULL |
| artifact_uri | VARCHAR(512) | 文件存储路径 | mlruns/0/.../artifacts |
| metrics | JSON | 指标 | {"sharpe": 1.5, "ic": 0.05} |
| params | JSON | 参数 | {"period": 20, "threshold": 0.02} |
| tags | JSON | 标签 | {"version": "v1.0", "author": "AI"} |

**索引**:
- PRIMARY KEY: experiment_id
- INDEX: experiment_type
- INDEX: status

### 3.2 数据血缘表 (data_lineage)

| 字段| 类型 | 说明 | 示例 |
|--------|------|------|------|
| lineage_id | VARCHAR(64) | 血缘ID (主键) | lineage_20260402_001 |
| data_id | VARCHAR(64) | 数据ID | data_20260402_001 |
| source | VARCHAR(256) | 数据| tushare |
| source_type | VARCHAR(32) | 数据源类| api |
| transformations | JSON | 数据处理过程 | [...] |
| created_at | DATETIME | 创建时间 | 2026-04-02 10:00:00 |
| quality_score | FLOAT | 质量评分 | 0.95 |

**索引**:
- PRIMARY KEY: lineage_id
- INDEX: data_id
- INDEX: source

### 3.3 版本(versions)

| 字段| 类型 | 说明 | 示例 |
|--------|------|------|------|
| version_id | VARCHAR(64) | 版本ID (主键) | ver_20260402_001 |
| artifact_path | VARCHAR(512) | 文件路径 | models/momentum_v1.pkl |
| version_tag | VARCHAR(32) | 版本标签 | v1.0.0 |
| artifact_type | VARCHAR(32) | 文件类型 | model |
| size_bytes | INTEGER | 文件大小 | 1024000 |
| checksum | VARCHAR(64) | 校验| abc123... |
| created_at | DATETIME | 创建时间 | 2026-04-02 10:00:00 |
| created_by | VARCHAR(64) | 创建| AI |

**索引**:
- PRIMARY KEY: version_id
- INDEX: version_tag
- INDEX: artifact_type

---

## 四、技术实

### 4.1 技术栈选择

| 技术组| 选择方案 | 理由 |
|---------|---------|------|
| **追踪引擎** | MLflow | 行业标准,功能强大 |
| **存储后端** | SQLite + Parquet | 轻量高效存储 |
| **数据格式** | Parquet + JSON | 列式存储,高效查询 |
| **可视* | MLflow UI | 专业级可视化,开箱即|
| **编程语言** | Python 3.10+ | 与现有系统一|

### 4.2 核心代码实现

#### 4.2.1 ExperimentTracker

```python
import mlflow
import mlflow.sklearn
import mlflow.pytorch
import sqlite3
import json
import pandas as pd
from datetime import datetime
from typing import Dict, List, Optional
import os

class ExperimentTracker:
    """实验追踪""
    
    def __init__(self, mlflow_uri: str = "http://localhost:5000", db_path: str = "data/experiments.db"):
        self.mlflow_uri = mlflow_uri
        self.db_path = db_path
        self._init_mlflow()
        self._init_database()
    
    def _init_mlflow(self):
        """初始化MLflow"""
        mlflow.set_tracking_uri(self.mlflow_uri)
    
    def _init_database(self):
        """初始化数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS experiments (
                experiment_id TEXT PRIMARY KEY,
                experiment_name TEXT,
                experiment_type TEXT,
                status TEXT,
                start_time DATETIME,
                end_time DATETIME,
                artifact_uri TEXT,
                metrics TEXT,
                params TEXT,
                tags TEXT
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS data_lineage (
                lineage_id TEXT PRIMARY KEY,
                data_id TEXT,
                source TEXT,
                source_type TEXT,
                transformations TEXT,
                created_at DATETIME,
                quality_score REAL
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS versions (
                version_id TEXT PRIMARY KEY,
                artifact_path TEXT,
                version_tag TEXT,
                artifact_type TEXT,
                size_bytes INTEGER,
                checksum TEXT,
                created_at DATETIME,
                created_by TEXT
            )
        """)
        
        conn.commit()
        conn.close()
    
    def track_factor_experiment(self, factor_name: str, params: dict, metrics: dict) -> str:
        """追踪因子实验"""
        
        mlflow.set_experiment("factor_experiments")
        
        with mlflow.start_run(run_name=f"factor_{factor_name}"):
            mlflow.log_params(params)
            mlflow.log_metrics(metrics)
            
            experiment_id = mlflow.active_run().info.run_id
            
            self._save_experiment(
                experiment_id=experiment_id,
                experiment_name=f"factor_{factor_name}",
                experiment_type="factor_experiment",
                params=params,
                metrics=metrics
            )
            
            return experiment_id
    
    def track_strategy_backtest(self, strategy_name: str, config: dict, result: dict) -> str:
        """追踪策略回测"""
        
        mlflow.set_experiment("strategy_backtests")
        
        with mlflow.start_run(run_name=f"strategy_{strategy_name}"):
            mlflow.log_params(config)
            mlflow.log_metrics(result.get('metrics', {}))
            mlflow.log_dict(result, "backtest_result.json")
            
            if 'model' in result:
                mlflow.sklearn.log_model(result['model'], "model")
            
            experiment_id = mlflow.active_run().info.run_id
            
            self._save_experiment(
                experiment_id=experiment_id,
                experiment_name=f"strategy_{strategy_name}",
                experiment_type="strategy_backtest",
                params=config,
                metrics=result.get('metrics', {})
            )
            
            return experiment_id
    
    def track_ai_workflow(self, session_id: str, context: dict, result: dict) -> str:
        """追踪AI工作""
        
        mlflow.set_experiment("ai_workflows")
        
        with mlflow.start_run(run_name=f"ai_session_{session_id}"):
            mlflow.log_dict(context, "context.json")
            mlflow.log_dict(result, "result.json")
            
            if 'effectiveness' in result:
                mlflow.log_metric("effectiveness", result['effectiveness'])
            
            experiment_id = mlflow.active_run().info.run_id
            
            self._save_experiment(
                experiment_id=experiment_id,
                experiment_name=f"ai_session_{session_id}",
                experiment_type="ai_workflow",
                params=context,
                metrics={'effectiveness': result.get('effectiveness', 0)}
            )
            
            return experiment_id
    
    def track_lineage(self, data_id: str, source: str, transformations: list) -> str:
        """追踪数据血""
        
        lineage_id = f"lineage_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        quality_score = self._calculate_quality_score(transformations)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO data_lineage 
            (lineage_id, data_id, source, source_type, transformations, created_at, quality_score)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            lineage_id, data_id, source, 'api',
            json.dumps(transformations, ensure_ascii=False),
            datetime.now(), quality_score
        ))
        
        conn.commit()
        conn.close()
        
        return lineage_id
    
    def create_version(self, artifact_path: str, version_tag: str, artifact_type: str = "data") -> str:
        """创建版本"""
        
        version_id = f"ver_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        size_bytes = os.path.getsize(artifact_path) if os.path.exists(artifact_path) else 0
        
        checksum = self._calculate_checksum(artifact_path)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO versions 
            (version_id, artifact_path, version_tag, artifact_type, size_bytes, checksum, created_at, created_by)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            version_id, artifact_path, version_tag, artifact_type,
            size_bytes, checksum, datetime.now(), 'AI'
        ))
        
        conn.commit()
        conn.close()
        
        return version_id
    
    def check_governance(self, data_id: str) -> dict:
        """检查数据治""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT quality_score, transformations FROM data_lineage WHERE data_id = ?
        """, (data_id,))
        
        result = cursor.fetchone()
        conn.close()
        
        if not result:
            return {
                "status": "not_found",
                "quality_score": 0,
                "issues": ["数据不存]
            }
        
        quality_score, transformations_str = result
        transformations = json.loads(transformations_str) if transformations_str else []
        
        issues = []
        if quality_score < 0.8:
            issues.append("数据质量评分过低")
        
        if len(transformations) > 10:
            issues.append("数据处理步骤过多")
        
        return {
            "status": "pass" if len(issues) == 0 else "warning",
            "quality_score": quality_score,
            "issues": issues
        }
    
    def _save_experiment(self, experiment_id: str, experiment_name: str, experiment_type: str, params: dict, metrics: dict):
        """保存实验"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO experiments 
            (experiment_id, experiment_name, experiment_type, status, start_time, metrics, params)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            experiment_id, experiment_name, experiment_type, 'running',
            datetime.now(),
            json.dumps(metrics, ensure_ascii=False),
            json.dumps(params, ensure_ascii=False)
        ))
        
        conn.commit()
        conn.close()
    
    def _calculate_quality_score(self, transformations: list) -> float:
        """计算质量评分"""
        if not transformations:
            return 0.5
        
        score = 1.0
        
        for transform in transformations:
            if transform.get('type') == 'cleaning':
                score *= 0.95
            elif transform.get('type') == 'normalization':
                score *= 0.98
        
        return round(score, 2)
    
    def _calculate_checksum(self, file_path: str) -> str:
        """计算文件校验""
        import hashlib
        
        if not os.path.exists(file_path):
            return ""
        
        with open(file_path, 'rb') as f:
            return hashlib.md5(f.read()).hexdigest()
```

---

## 五、实施路径

### 5.1 Phase 1: MLflow部署与集(Week 1前半)

**目标**: 部署MLflow服务器并集成到系

**任务清单**:
- [ ] 安装MLflow
- [ ] 启动MLflow Tracking Server
- [ ] 配置存储后端
- [ ] 集成到现有系
- [ ] 编写使用文档

**验收标准**:
- MLflow服务器正常运
- 能够追踪实验
- 能够查看实验结果

### 5.2 Phase 2: 数据血缘与版本控制 (Week 1后半)

**目标**: 实现数据血缘追踪和版本控制

**任务清单**:
- [ ] 实现DataLineageTracker组件
- [ ] 实现VersionController组件
- [ ] 实现DataGovernanceManager组件
- [ ] 集成到现有系
- [ ] 编写单元测试

**验收标准**:
- 能够追踪数据血
- 能够管理数据版本
- 能够检查数据治

---

## 六、文档治理

### 6.1 System_Manifest.md索引

```markdown
| 蓝图文档 | 路径 | 模块ID | 版本 | 状| 职责概要 |
|----------|------|--------|------|------|----------|
| [全流程数据保存机制蓝图](../10_AI_WORKFLOW/FULL_PROCESS_DATA_PERSISTENCE_BLUEPRINT.md) | `docs/10_AI_WORKFLOW/FULL_PROCESS_DATA_PERSISTENCE_BLUEPRINT.md` | FULL_PROCESS_DATA_PERSISTENCE_001 | 1.0 | Active | 实验追踪、数据血缘、版本控制、数据治|
```

### 6.2 模块职责边界

**核心职责**:
- 实验追踪
- 数据血缘追
- 版本控制
- 数据治理

**非职*:
- AI工作记录 (由AI_WORKFLOW_LOGGER模块负责)
- AI工作汇报 (由AI_WORK_REPORTER模块负责)
- 复盘分析 (由POST_TRADE_REVIEW模块负责)

### 6.3 版本管理策略

- **v1.0**: 初始版本,实现核心功能
- **v1.1**: 增强数据血缘追
- **v1.2**: 增加数据质量监控
- **v2.0**: 集成分布式存

---

## 七、风险评

### 7.1 技术风

| 风险 | 影响 | 概率 | 缓解措施 |
|------|------|------|----------|
| **存储空间不足** | | | 实施数据分层存储,定期归档 |
| **MLflow性能瓶颈** | | | 使用分布式存优化查询 |
| **数据血缘复* | | | 建立血缘追踪规简化流|

### 7.2 实施风险

| 风险 | 影响 | 概率 | 缓解措施 |
|------|------|------|----------|
| **学习曲线陡峭** | | | 编写详细文档,提供示例代码 |
| **集成复杂度高** | | | 分阶段实逐步集成 |

---

## 八、相关文档

| 文档 | 说明 |
|------|------|
| [AI工作记录与优化模块蓝图](./AI_WORKFLOW_LOGGER_BLUEPRINT.md) | AI工作记录数据|
| [复盘模块蓝图](./POST_TRADE_REVIEW_BLUEPRINT.md) | 复盘分析机制 |
| [开源项目集成方案蓝图](./OPEN_SOURCE_INTEGRATION_BLUEPRINT.md) | 开源项目集成方|
| [MLflow官方文档](https://mlflow.org/docs/latest/index.html) | MLflow使用指南 |

---

**版本**: v1.0 | **更新**: 2026-04-02 | **状*: 活跃
