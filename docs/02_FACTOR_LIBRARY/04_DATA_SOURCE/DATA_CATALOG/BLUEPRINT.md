---
module_id: FACTOR_DATA_CATALOG_BP_001
version: 1.0.1
status: Blueprint
created_date: 2026-04-06
last_updated: 2026-04-06
owner: 首席架构师
standard_type: 模块蓝图
applicable_scope: 数据目录系统
compliance_level: 专业标准
parent_document: ../DATA_SOURCE_LAYER_GAP_ANALYSIS.md
dependencies:
- DataHub
- OpenLineage
- Docker
responsibility: 数据目录管理与元数据组织
---
---

# 数据目录系统蓝图

> **核心职责**: 数据目录系统蓝图的蓝图设计和架构规划
> **职责边界**: 
> - ✅ 本文档负责：蓝图设计和架构规划相关内容
> - ❌ 本文档不负责：其他模块内容


## 文档职责说明

**本文档职责**: 数据目录系统设计蓝图
- 定义数据目录系统架构
- 说明数据资产发现和元数据管理方案
- 提供数据血缘集成和治理支持方案

**相关文档引用**:
| 文档 | 路径 | 关系 | 说明 |
|------|------|------|------|
| 差距分析 | [../DATA_SOURCE_LAYER_GAP_ANALYSIS.md](02_FACTOR_LIBRARY\04_DATA_SOURCE\DATA_SOURCE_LAYER_GAP_ANALYSIS.md) | 上层分析 | 架构缺失分析 |
| 数据源索引 | [../INDEX.md](../INDEX.md) | 上级索引 | 数据源模块总索引 |
| 数据血缘追踪 | [../DATA_LINEAGE_TRACKING/](01_FRAMEWORK/DATA_LINEAGE_TRACKING_BLUEPRINT.md) | 协同模块 | 数据血缘关系 |
| 数据权限管理 | [../DATA_PERMISSION_MANAGEMENT/](../DATA_PERMISSION_MANAGEMENT/) | 协同模块 | 数据权限控制 |

**职责边界**:
- ✅ 本文档负责: 数据目录系统架构设计
- ✅ 本文档负责: 数据资产发现、元数据管理、血缘集成方案
- ❌ 本文档不负责: 数据血缘追踪实施（由 DATA_LINEAGE_TRACKING 负责）
- ❌ 本文档不负责: 数据权限管理（由 DATA_PERMISSION_MANAGEMENT 负责）
- ❌ 本文档不负责: 数据备份恢复（由 DATA_BACKUP_RECOVERY 负责）

> 清风量化系统 v5.4 - 数据目录模块
> **优先级**: 🟡 P1级（短期实施）
> **实施周期**: 2周
> **开源方案**: DataHub（轻量版）

---

## 📋 模块概述

### 核心职责

数据目录系统负责统一管理数据资产，实现：
- 数据资产发现和搜索
- 元数据管理
- 数据血缘集成
- 数据治理支持

### 职责边界

| 本模块负责 | 本模块不负责 |
|-----------|-------------|
| ✅ 数据资产目录 | ❌ 数据质量检查 |
| ✅ 元数据管理 | ❌ 数据版本控制 |
| ✅ 数据搜索发现 | ❌ 数据备份恢复 |
| ✅ 血缘集成 | ❌ 数据监控告警 |

---

## 🎯 功能需求

### 核心功能

| 功能 | 描述 | 优先级 |
|------|------|--------|
| **数据资产目录** | 统一管理所有数据资产 | 🟡 P1 |
| **元数据管理** | 管理数据元信息 | 🟡 P1 |
| **数据搜索** | 搜索和发现数据 | 🟡 P1 |
| **血缘集成** | 集成数据血缘 | 🟢 P2 |
| **数据治理** | 数据访问策略 | 🟢 P2 |

### 技术指标

| 指标 | 目标值 | 测量方法 |
|------|--------|----------|
| **数据覆盖率** | 100% | 已编目数据/总数据 |
| **搜索响应时间** | < 1秒 | 单次搜索时间 |
| **元数据更新延迟** | < 5分钟 | 变更到更新 |
| **系统可用性** | > 99.9% | 运行时间百分比 |

---

## 🏗️ 架构设计

### 系统架构

```
┌─────────────────────────────────────────────────────────────┐
│                   数据目录系统                                │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │                   API层                              │  │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐          │  │
│  │  │REST API  │  │ GraphQL  │  │ Web UI   │          │  │
│  │  │          │  │          │  │          │          │  │
│  │  └──────────┘  └──────────┘  └──────────┘          │  │
│  └──────────────────────────────────────────────────────┘  │
│                          │                                  │
│                          ▼                                  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │                   元数据层                            │  │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐          │  │
│  │  │数据集    │  │数据源    │  │数据管道   │          │  │
│  │  │元数据   │  │元数据   │  │元数据    │          │  │
│  │  └──────────┘  └──────────┘  └──────────────┘      │  │
│  └──────────────────────────────────────────────────────┘  │
│                          │                                  │
│                          ▼                                  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │                   存储层                              │  │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐          │  │
│  │  │PostgreSQL│  │Elastic   │  │MySQL     │          │  │
│  │  │(元数据)  │  │Search    │  │(关系)    │          │  │
│  │  └──────────┘  └──────────┘  └──────────┘          │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 💻 技术实现

### 技术栈选择

| 组件 | 技术选型 | 选择理由 |
|------|----------|----------|
| **目录平台** | DataHub | 功能完整，开源免费 |
| **搜索** | Elasticsearch | 高性能搜索 |
| **存储** | PostgreSQL | 稳定可靠 |
| **部署** | Docker | 快速部署 |

### 核心代码实现

#### 1. DataHub Python SDK集成

```python
"""
数据目录管理器
"""
from datahub.emitter.mce_builder import make_dataset_urn
from datahub.emitter.rest_emitter import DatahubRestEmitter
from datahub.metadata.schema_classes import (
    DatasetPropertiesClass,
    OwnershipClass,
    OwnerClass,
    DatasetLineageTypeClass,
    UpstreamLineageClass,
    AuditStampClass,
)
from datahub.api.graph.serde import ser
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class DataCatalogManager:
    """数据目录管理器"""
    
    def __init__(self, gms_url: str = "http://localhost:8080"):
        """
        初始化数据目录管理器
        
        Args:
            gms_url: DataHub GMS服务地址
        """
        self.gms_url = gms_url
        self.emitter = DatahubRestEmitter(gms_server=gms_url)
        self.platform = "quant_system"
    
    def register_dataset(
        self,
        dataset_name: str,
        description: str,
        platform: str = "clickhouse",
        owners: Optional[List[str]] = None,
        tags: Optional[List[str]] = None
    ):
        """
        注册数据集
        
        Args:
            dataset_name: 数据集名称
            description: 数据集描述
            platform: 数据平台
            owners: 所有者列表
            tags: 标签列表
        """
        dataset_urn = make_dataset_urn(
            platform=platform,
            name=dataset_name,
            env="PROD"
        )
        
        owners_list = []
        if owners:
            owners_list = [
                OwnerClass(
                    owner=make_dataset_urn("user", owner),
                    type=OwnerClass.OwnerType.DATA_OWNER,
                    AuditStampClass(
                        time=int(datetime.now().timestamp() * 1000),
                        actor="urn:li:corpuser:system"
                    )
                )
                for owner in owners
            ]
        
        dataset_properties = DatasetPropertiesClass(
            description=description,
            customProperties={
                "created_at": datetime.now().isoformat(),
                "platform": platform,
                "environment": "production"
            },
            owners=owners_list,
            tags=tags or []
        )
        
        from datahub.metadata.com.linkedin.pegasus2avro.metadata.snapshot import DatasetSnapshot
        snapshot = DatasetSnapshot(
            urn=dataset_urn,
            aspects=[dataset_properties]
        )
        
        self.emitter.emit(snapshot)
        
        logger.info(f"Registered dataset: {dataset_name}")
    
    def register_clickhouse_dataset(
        self,
        database: str,
        table: str,
        description: str,
        columns: List[Dict[str, Any]],
        owners: Optional[List[str]] = None
    ):
        """
        注册ClickHouse数据集
        
        Args:
            database: 数据库名
            table: 表名
            description: 表描述
            columns: 列定义
            owners: 所有者
        """
        dataset_name = f"{database}.{table}"
        
        self.register_dataset(
            dataset_name=dataset_name,
            description=description,
            platform="clickhouse",
            owners=owners,
            tags=["clickhouse", "database", database]
        )
        
        # 注册列级元数据
        self._register_column_metadata(
            database=database,
            table=table,
            columns=columns
        )
    
    def _register_column_metadata(
        self,
        database: str,
        table: str,
        columns: List[Dict[str, Any]]
    ):
        """注册列级元数据"""
        dataset_urn = make_dataset_urn(
            platform="clickhouse",
            name=f"{database}.{table}",
            env="PROD"
        )
        
        from datahub.metadata.schema_classes import SchemaMetadataClass, SchemaFieldClass, SchemaFieldDataTypeClass
        
        schema_fields = []
        for col in columns:
            schema_fields.append(
                SchemaFieldClass(
                    fieldName=col["name"],
                    fieldType=SchemaFieldDataTypeClass(
                        type=SchemaFieldDataTypeClass.MapType(
                            stringType=SchemaFieldDataTypeClass.StringType()
                        )
                    ),
                    description=col.get("description", ""),
                    nativeDataType=col.get("type", "string"),
                    nullable=col.get("nullable", True),
                    isPartOfKey=col.get("is_primary_key", False)
                )
            )
        
        schema_metadata = SchemaMetadataClass(
            schemaName=f"{database}.{table}",
            version=0,
            hash="",
            platform=f"urn:li:dataPlatform:clickhouse",
            fields=schema_fields,
            primaryKeys=[col["name"] for col in columns if col.get("is_primary_key", False)]
        )
        
        from datahub.metadata.com.linkedin.pegasus2avro.metadata.snapshot import DatasetSnapshot
        snapshot = DatasetSnapshot(
            urn=dataset_urn,
            aspects=[schema_metadata]
        )
        
        self.emitter.emit(snapshot)
        
        logger.info(f"Registered column metadata for {database}.{table}")
    
    def register_upstream_lineage(
        self,
        downstream_dataset: str,
        upstream_datasets: List[str],
        platform: str = "clickhouse"
    ):
        """
        注册上游血缘关系
        
        Args:
            downstream_dataset: 下游数据集
            upstream_datasets: 上游数据集列表
            platform: 数据平台
        """
        downstream_urn = make_dataset_urn(
            platform=platform,
            name=downstream_dataset,
            env="PROD"
        )
        
        upstream_urns = [
            make_dataset_urn(platform=platform, name=upstream, env="PROD")
            for upstream in upstream_datasets
        ]
        
        lineage = UpstreamLineageClass(
            upstreams=[
                {
                    "auditStamp": AuditStampClass(
                        time=int(datetime.now().timestamp() * 1000),
                        actor="urn:li:corpuser:system"
                    ),
                    "dataset": upstream_urn,
                    "type": DatasetLineageTypeClass.TRANSFORMED
                }
                for upstream_urn in upstream_urns
            ]
        )
        
        from datahub.metadata.com.linkedin.pegasus2avro.metadata.snapshot import DatasetSnapshot
        snapshot = DatasetSnapshot(
            urn=downstream_urn,
            aspects=[lineage]
        )
        
        self.emitter.emit(snapshot)
        
        logger.info(f"Registered lineage: {upstream_datasets} -> {downstream_dataset}")
    
    def update_dataset_description(
        self,
        dataset_name: str,
        description: str,
        platform: str = "clickhouse"
    ):
        """
        更新数据集描述
        
        Args:
            dataset_name: 数据集名称
            description: 新描述
            platform: 数据平台
        """
        dataset_urn = make_dataset_urn(
            platform=platform,
            name=dataset_name,
            env="PROD"
        )
        
        dataset_properties = DatasetPropertiesClass(
            description=description,
            lastModified=AuditStampClass(
                time=int(datetime.now().timestamp() * 1000),
                actor="urn:li:corpuser:system"
            )
        )
        
        from datahub.metadata.com.linkedin.pegasus2avro.metadata.snapshot import DatasetSnapshot
        snapshot = DatasetSnapshot(
            urn=dataset_urn,
            aspects=[dataset_properties]
        )
        
        self.emitter.emit(snapshot)
        
        logger.info(f"Updated dataset description: {dataset_name}")
    
    def search_datasets(
        self,
        query: str,
        platform: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        搜索数据集
        
        Args:
            query: 搜索关键词
            platform: 数据平台过滤
            limit: 返回结果数量限制
        
        Returns:
            搜索结果列表
        """
        import requests
        
        search_url = f"{self.gms_url}/api/v2/search"
        
        params = {
            "type": "dataset",
            "query": query,
            "limit": limit
        }
        
        if platform:
            params["platform"] = platform
        
        response = requests.get(search_url, params=params)
        
        if response.status_code == 200:
            results = response.json()
            return results.get("hits", {}).get("hits", [])
        else:
            logger.error(f"Search failed: {response.text}")
            return []
```

#### 2. 元数据自动采集

```python
"""
元数据自动采集器
"""
import requests
from typing import List, Dict, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class MetadataCollector:
    """元数据采集器"""
    
    def __init__(self, catalog_manager: DataCatalogManager):
        self.catalog = catalog_manager
    
    def collect_clickhouse_metadata(self, host: str, port: int = 8123):
        """
        采集ClickHouse元数据
        
        Args:
            host: ClickHouse主机
            port: ClickHouse端口
        """
        # 获取数据库列表
        query = "SHOW DATABASES"
        databases = self._execute_query(host, port, query)
        
        for db in databases:
            database_name = db["name"]
            
            # 获取表列表
            query = f"SHOW TABLES FROM {database_name}"
            tables = self._execute_query(host, port, query)
            
            for table in tables:
                table_name = table["name"]
                
                # 获取列信息
                query = f"DESCRIBE TABLE {database_name}.{table_name}"
                columns = self._execute_query(host, port, query)
                
                # 注册到DataHub
                column_defs = [
                    {
                        "name": col["name"],
                        "type": col["type"],
                        "nullable": "Nullable" in col["type"],
                        "description": col.get("default_type", "")
                    }
                    for col in columns
                ]
                
                self.catalog.register_clickhouse_dataset(
                    database=database_name,
                    table=table_name,
                    description=f"{database_name}.{table_name}",
                    columns=column_defs
                )
                
                logger.info(f"Collected metadata: {database_name}.{table_name}")
    
    def _execute_query(self, host: str, port: int, query: str) -> List[Dict[str, Any]]:
        """执行ClickHouse查询"""
        import pandas as pd
        
        url = f"http://{host}:{port}/?query={requests.utils.quote(query)}"
        
        response = requests.get(url)
        
        if response.status_code == 200:
            return response.json()
        else:
            logger.error(f"Query failed: {response.text}")
            return []
```

---

## 🚀 部署方案

### 环境要求

| 组件 | 版本要求 | 说明 |
|------|----------|------|
| **Docker** | >= 20.0 | 容器化部署 |
| **DataHub** | >= 0.10.0 | 数据目录平台 |
| **PostgreSQL** | >= 13.0 | 元数据存储 |
| **Elasticsearch** | >= 7.0 | 搜索索引 |

### 部署步骤

#### 1. 快速部署DataHub

```bash
# 克隆DataHub仓库
git clone https://github.com/datahub-project/datahub.git
cd datahub/docker/quickstart

# 启动DataHub
docker-compose -f docker-compose.quickstart.yml up -d

# 访问Web UI
# http://localhost:9002

# 访问API
# http://localhost:8080
```

#### 2. 配置Python SDK

```bash
# 安装DataHub Python SDK
pip install datahub

# 配置环境变量
export DATAHUB_GMS_URL=http://localhost:8080
export DATAHUB_WEB_HOST=http://localhost:9002
```

---

## 📊 监控指标

### 关键指标

| 指标 | 目标值 | 告警阈值 |
|------|--------|----------|
| **数据覆盖率** | 100% | < 80% |
| **搜索响应时间** | < 1秒 | > 3秒 |
| **元数据更新延迟** | < 5分钟 | > 30分钟 |
| **DataHub可用性** | > 99.9% | < 99% |

---

## 📝 使用指南

### 快速开始

```python
# 1. 初始化目录管理器
from data_catalog import DataCatalogManager

catalog = DataCatalogManager(gms_url="http://localhost:8080")

# 2. 注册数据集
catalog.register_clickhouse_dataset(
    database="quant_system",
    table="stock_prices",
    description="A股股票价格数据",
    columns=[
        {"name": "symbol", "type": "String", "nullable": False, "is_primary_key": True},
        {"name": "date", "type": "Date", "nullable": False},
        {"name": "close", "type": "Float64", "nullable": False},
    ],
    owners=["admin"]
)

# 3. 注册血缘
catalog.register_upstream_lineage(
    downstream_dataset="quant_system.stock_prices_agg",
    upstream_datasets=["quant_system.stock_prices"]
)

# 4. 搜索数据
results = catalog.search_datasets("stock")
for result in results:
    print(result["_source"]["name"])
```

---

## 🔗 相关文档

- [DataHub官方文档](https://datahubproject.io/docs/)
- [数据源层架构缺失分析](02_FACTOR_LIBRARY\04_DATA_SOURCE\DATA_SOURCE_LAYER_GAP_ANALYSIS.md)

---

**文档版本**: v1.0.0 | **创建日期**: 2026-04-06 | **状态**: ✅ 蓝图完成 | **作者**: 首席架构师

---

## 变更记录

| 版本 | 日期 | 变更内容 | 变更人 |
|------|------|----------|--------|
| v1.0.0 | 2026-04-06 | 初始版本，补充职责描述和变更记录 | 首席文档架构师 |
---

## 1. 文档治理

### 1.1 System_Manifest.md索引

```markdown
#### Layer 0: 系统架构
##### 0.001. Factor Data Catalog Bp
- **模块ID**: FACTOR_DATA_CATALOG_BP_001
- **蓝图文档**: [BLUEPRINT.md](02_FACTOR_LIBRARY\04_DATA_SOURCE\DATA_CATALOG\BLUEPRINT.md)
- **技术规格书**: 待创建
- **职责**: 数据目录系统
- **状态**: Blueprint
```

### 1.2 模块职责边界

| 模块 | 职责 | 边界 |
|------|------|------|
| **Factor Data Catalog Bp** | 数据目录系统 | **核心模块** |

### 1.3 版本管理

| 版本 | 日期 | 变更内容 | 变更人 |
|------|------|----------|--------|
| v1.0.0 | 2026-04-06 | 初始版本创建 | 首席蓝图架构师 |

---

**蓝图版本**: v1.0.0 | **创建日期**: 2026-04-06 | **状态**: Blueprint
