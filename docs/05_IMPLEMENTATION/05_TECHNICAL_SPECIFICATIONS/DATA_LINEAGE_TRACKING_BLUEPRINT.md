---
module_id: DATA_LINEAGE_001
version: 1.0.0
status: Active
created_date: 2026-04-02
last_updated: 2026-04-02
owner: 首席技术评审官
standard_type: 专业量化机构蓝图
applicable_scope: Layer 0数据源层 | 业务架构: 三级时间框架融合架构
compliance_level: 专业标准
parent_document: ../INDEX.md
implementation_status: 设计阶段
implementation_progress: 0%
---

# 数据血缘追踪系统蓝�?
> 清风量化系统 v5.2 - 数据血缘追踪系统详细设�?> **模块ID**: `DATA_LINEAGE_001`
> **实施周期**: Week 1-2�?周）
> **优先�?*: P0（核心）
> **预期收益**: 提高数据可追溯�?0%，减少问题排查时�?0%


## 一、设计背景与目标

### 1.1 业务需�?
**当前痛点**:
- �?数据来源不清晰，无法追溯数据来源和处理历�?- �?数据问题排查困难，需要人工逐层追溯
- �?缺少数据依赖关系分析，无法评估数据变更影响范�?- �?无法满足数据审计和合规要�?
**业务目标**:
- �?建立完整的数据血缘图谱，可视化展示数据流�?- �?每个数据点都有完整的来源记录和处理历�?- �?自动分析数据依赖关系，识别影响范�?- �?支持数据审计和合规要�?
### 1.2 技术目�?
| 指标 | 目标�?| 说明 |
|------|--------|------|
| **血缘覆盖率** | �?5% | 95%以上的数据有完整血缘记�?|
| **血缘查询性能** | <1�?| 血缘关系查询响应时�?1�?|
| **血缘图谱可视化** | 支持 | 提供可视化界面展示血缘关�?|
| **血缘追溯深�?* | 无限�?| 支持追溯任意深度的血缘关�?|

---

## 二、系统架构设�?
### 2.1 整体架构�?
```
┌─────────────────────────────────────────────────────────────�?�?                数据血缘追踪系统架�?                         �?├─────────────────────────────────────────────────────────────�?�?                                                            �?�? ┌──────────────────────────────────────────────────────�? �?�? �?           血缘采集层 (Lineage Collection)            �? �?�? �? ┌─────────────�? ┌─────────────�? ┌─────────────�? �? �?�? �? �?数据源采�?  �? �?处理过程采集 �? �?数据流采�?  �? �? �?�? �? └─────────────�? └─────────────�? └─────────────�? �? �?�? └──────────────────────────────────────────────────────�? �?�?                          �?                                 �?�? ┌──────────────────────────────────────────────────────�? �?�? �?           血缘存储层 (Lineage Storage)               �? �?�? �? ┌─────────────�? ┌─────────────�? ┌─────────────�? �? �?�? �? �?血缘图谱存�?�? �?血缘元数据   �? �?血缘历�?    �? �? �?�? �? �?(Neo4j)     �? �?(PostgreSQL)�? �?(PostgreSQL)�? �? �?�? �? └─────────────�? └─────────────�? └─────────────�? �? �?�? └──────────────────────────────────────────────────────�? �?�?                          �?                                 �?�? ┌──────────────────────────────────────────────────────�? �?�? �?           血缘分析层 (Lineage Analysis)              �? �?�? �? ┌─────────────�? ┌─────────────�? ┌─────────────�? �? �?�? �? �?依赖关系分析 �? �?影响范围分析 �? �?血缘路径查�?�? �? �?�? �? └─────────────�? └─────────────�? └─────────────�? �? �?�? └──────────────────────────────────────────────────────�? �?�?                          �?                                 �?�? ┌──────────────────────────────────────────────────────�? �?�? �?           血缘服务层 (Lineage Service)               �? �?�? �? ┌─────────────�? ┌─────────────�? ┌─────────────�? �? �?�? �? �?血缘查询API  �? �?血缘可视化   �? �?血缘报�?    �? �? �?�? �? └─────────────�? └─────────────�? └─────────────�? �? �?�? └──────────────────────────────────────────────────────�? �?�?                                                            �?└─────────────────────────────────────────────────────────────�?```

### 2.2 技术选型

| 组件 | 技术方�?| 版本要求 | 选型理由 |
|------|---------|---------|---------|
| **血缘图谱存�?* | Neo4j | �?.4.0 | 图数据库，适合存储血缘关�?|
| **血缘元数据存储** | PostgreSQL | �?3.0 | 关系型数据库，存储元数据 |
| **血缘采集框�?* | OpenLineage | �?.20.0 | 开源血缘采集标�?|
| **可视化界�?* | Marquez | �?.20.0 | 开源血缘可视化工具 |
| **Python客户�?* | marquez-python | �?.20.0 | Python SDK |

### 2.3 Layer定位

- **Layer归属**: Layer 1 - 数据预处理层
- **职责范围**: 数据血缘采集、存储、分析、查询、可视化
- **上下层接�?*:
  - 上层依赖: Layer 2-8（提供血缘查询服务）
  - 下层依赖: Layer 0数据源层（采集血缘信息）

---

## 三、核心模块设�?
### 3.1 血缘采集器 (LineageCollector)

**职责**: 自动采集数据血缘信�?
```python
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum
import json

class SourceType(Enum):
    """数据源类�?""
    QMT = "qmt"                    # 🆓 免费交易接口
    IFIND = "ifind"                # �?已有主数据源
    TUSHARE = "tushare"            # 🆓 免费补充数据�?    AKSHARE = "akshare"            # 🆓 免费补充数据�?    BAOSTOCK = "baostock"          # 🆓 免费A股历史数�?    EFINANCE = "efinance"          # 🆓 免费东方财富数据
    YFINANCE = "yfinance"          # 🆓 免费美股数据�?    QLIB = "qlib"                  # 🆓 免费微软量化数据
    CUSTOM = "custom"              # 自建数据�?    SUPERCOMMAND = "supercommand"
    BAOSTOCK = "baostock"
    DATABASE = "database"
    FILE = "file"

class TransformationType(Enum):
    """转换类型"""
    CLEAN = "clean"
    NORMALIZE = "normalize"
    VALIDATE = "validate"
    TRANSFORM = "transform"
    AGGREGATE = "aggregate"

@dataclass
class DataSource:
    """数据�?""
    source_id: str
    source_type: DataSourceType
    source_name: str
    connection_info: Dict[str, Any]
    created_at: datetime = field(default_factory=datetime.now)

@dataclass
class DataField:
    """数据字段"""
    field_id: str
    field_name: str
    field_type: str
    description: str
    source_id: str

@dataclass
class Transformation:
    """数据转换"""
    transformation_id: str
    transformation_type: TransformationType
    input_fields: List[str]
    output_fields: List[str]
    transformation_logic: str
    parameters: Dict[str, Any]
    created_at: datetime = field(default_factory=datetime.now)

@dataclass
class LineageNode:
    """血缘节�?""
    node_id: str
    node_type: str  # source, transformation, output
    node_name: str
    metadata: Dict[str, Any]
    created_at: datetime = field(default_factory=datetime.now)

@dataclass
class LineageEdge:
    """血缘边"""
    edge_id: str
    source_node_id: str
    target_node_id: str
    edge_type: str  # data_flow, transformation
    metadata: Dict[str, Any]
    created_at: datetime = field(default_factory=datetime.now)

class LineageCollector:
    """血缘采集器"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化血缘采集器
        
        Args:
            config: 配置信息
                - neo4j_uri: Neo4j连接URI
                - neo4j_user: Neo4j用户�?                - neo4j_password: Neo4j密码
                - postgres_uri: PostgreSQL连接URI
        """
        self.config = config
        self.neo4j_driver = None
        self.postgres_conn = None
        
    def collect_source_lineage(
        self,
        source: DataSource
    ) -> str:
        """
        采集数据源血�?        
        Args:
            source: 数据源信�?            
        Returns:
            str: 数据源节点ID
        """
        pass
    
    def collect_transformation_lineage(
        self,
        transformation: Transformation
    ) -> str:
        """
        采集转换血�?        
        Args:
            transformation: 数据转换信息
            
        Returns:
            str: 转换节点ID
        """
        pass
    
    def collect_field_lineage(
        self,
        field: DataField
    ) -> str:
        """
        采集字段血�?        
        Args:
            field: 数据字段信息
            
        Returns:
            str: 字段节点ID
        """
        pass
    
    def build_lineage_graph(
        self,
        nodes: List[LineageNode],
        edges: List[LineageEdge]
    ) -> Dict[str, Any]:
        """
        构建血缘图�?        
        Args:
            nodes: 血缘节点列�?            edges: 血缘边列表
            
        Returns:
            Dict: 血缘图�?        """
        pass
```

### 3.2 血缘存储器 (LineageStorage)

**职责**: 存储血缘信息到Neo4j和PostgreSQL

```python
from neo4j import GraphDatabase
import psycopg2
from typing import Dict, List, Any

class LineageStorage:
    """血缘存储器"""
    
    def __init__(self, neo4j_uri: str, neo4j_user: str, neo4j_password: str,
                 postgres_uri: str):
        """
        初始化血缘存储器
        
        Args:
            neo4j_uri: Neo4j连接URI
            neo4j_user: Neo4j用户�?            neo4j_password: Neo4j密码
            postgres_uri: PostgreSQL连接URI
        """
        self.neo4j_driver = GraphDatabase.driver(
            neo4j_uri,
            auth=(neo4j_user, neo4j_password)
        )
        self.postgres_conn = psycopg2.connect(postgres_uri)
        
    def store_node(self, node: LineageNode) -> bool:
        """
        存储血缘节点到Neo4j
        
        Args:
            node: 血缘节�?            
        Returns:
            bool: 是否成功
        """
        with self.neo4j_driver.session() as session:
            query = """
            CREATE (n:LineageNode {
                node_id: $node_id,
                node_type: $node_type,
                node_name: $node_name,
                metadata: $metadata,
                created_at: $created_at
            })
            RETURN n
            """
            result = session.run(
                query,
                node_id=node.node_id,
                node_type=node.node_type,
                node_name=node.node_name,
                metadata=json.dumps(node.metadata),
                created_at=node.created_at.isoformat()
            )
            return result.single() is not None
    
    def store_edge(self, edge: LineageEdge) -> bool:
        """
        存储血缘边到Neo4j
        
        Args:
            edge: 血缘边
            
        Returns:
            bool: 是否成功
        """
        with self.neo4j_driver.session() as session:
            query = """
            MATCH (source:LineageNode {node_id: $source_node_id})
            MATCH (target:LineageNode {node_id: $target_node_id})
            CREATE (source)-[r:LINEAGE_EDGE {
                edge_id: $edge_id,
                edge_type: $edge_type,
                metadata: $metadata,
                created_at: $created_at
            }]->(target)
            RETURN r
            """
            result = session.run(
                query,
                source_node_id=edge.source_node_id,
                target_node_id=edge.target_node_id,
                edge_id=edge.edge_id,
                edge_type=edge.edge_type,
                metadata=json.dumps(edge.metadata),
                created_at=edge.created_at.isoformat()
            )
            return result.single() is not None
    
    def store_metadata(self, metadata: Dict[str, Any]) -> bool:
        """
        存储血缘元数据到PostgreSQL
        
        Args:
            metadata: 元数据信�?            
        Returns:
            bool: 是否成功
        """
        cursor = self.postgres_conn.cursor()
        query = """
        INSERT INTO lineage_metadata (
            node_id, node_type, node_name, metadata, created_at
        ) VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(
            query,
            (
                metadata['node_id'],
                metadata['node_type'],
                metadata['node_name'],
                json.dumps(metadata['metadata']),
                metadata['created_at']
            )
        )
        self.postgres_conn.commit()
        return True
```

### 3.3 血缘分析器 (LineageAnalyzer)

**职责**: 分析血缘关系和影响范围

```python
from typing import List, Dict, Any, Set

class LineageAnalyzer:
    """血缘分析器"""
    
    def __init__(self, neo4j_driver):
        """
        初始化血缘分析器
        
        Args:
            neo4j_driver: Neo4j驱动
        """
        self.neo4j_driver = neo4j_driver
        
    def get_upstream_lineage(
        self,
        node_id: str,
        max_depth: int = 10
    ) -> List[Dict[str, Any]]:
        """
        获取上游血�?        
        Args:
            node_id: 节点ID
            max_depth: 最大追溯深�?            
        Returns:
            List[Dict]: 上游血缘节点列�?        """
        with self.neo4j_driver.session() as session:
            query = """
            MATCH path = (n:LineageNode {node_id: $node_id})<-[:LINEAGE_EDGE*1..{max_depth}]-(upstream)
            RETURN upstream.node_id as node_id,
                   upstream.node_type as node_type,
                   upstream.node_name as node_name,
                   length(path) as depth
            ORDER BY depth
            """.format(max_depth=max_depth)
            
            result = session.run(query, node_id=node_id)
            return [record.data() for record in result]
    
    def get_downstream_lineage(
        self,
        node_id: str,
        max_depth: int = 10
    ) -> List[Dict[str, Any]]:
        """
        获取下游血�?        
        Args:
            node_id: 节点ID
            max_depth: 最大追溯深�?            
        Returns:
            List[Dict]: 下游血缘节点列�?        """
        with self.neo4j_driver.session() as session:
            query = """
            MATCH path = (n:LineageNode {node_id: $node_id})-[:LINEAGE_EDGE*1..{max_depth}]->(downstream)
            RETURN downstream.node_id as node_id,
                   downstream.node_type as node_type,
                   downstream.node_name as node_name,
                   length(path) as depth
            ORDER BY depth
            """.format(max_depth=max_depth)
            
            result = session.run(query, node_id=node_id)
            return [record.data() for record in result]
    
    def get_impact_scope(
        self,
        node_id: str
    ) -> Dict[str, Any]:
        """
        获取影响范围
        
        Args:
            node_id: 节点ID
            
        Returns:
            Dict: 影响范围信息
        """
        downstream = self.get_downstream_lineage(node_id)
        
        impact_nodes = set()
        impact_layers = {}
        
        for node in downstream:
            impact_nodes.add(node['node_id'])
            depth = node['depth']
            if depth not in impact_layers:
                impact_layers[depth] = []
            impact_layers[depth].append(node)
        
        return {
            'node_id': node_id,
            'impact_node_count': len(impact_nodes),
            'impact_nodes': list(impact_nodes),
            'impact_layers': impact_layers
        }
    
    def find_lineage_path(
        self,
        source_node_id: str,
        target_node_id: str
    ) -> List[Dict[str, Any]]:
        """
        查找血缘路�?        
        Args:
            source_node_id: 源节点ID
            target_node_id: 目标节点ID
            
        Returns:
            List[Dict]: 血缘路�?        """
        with self.neo4j_driver.session() as session:
            query = """
            MATCH path = shortestPath(
                (source:LineageNode {node_id: $source_node_id})
                -[:LINEAGE_EDGE*]->
                (target:LineageNode {node_id: $target_node_id})
            )
            RETURN [node in nodes(path) | {
                node_id: node.node_id,
                node_type: node.node_type,
                node_name: node.node_name
            }] as path
            """
            
            result = session.run(
                query,
                source_node_id=source_node_id,
                target_node_id=target_node_id
            )
            record = result.single()
            if record:
                return record['path']
            return []
```

### 3.4 血缘服务API (LineageService)

**职责**: 提供血缘查询API

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

app = FastAPI(title="数据血缘追踪系统API")

class LineageQuery(BaseModel):
    """血缘查询请�?""
    node_id: str
    query_type: str  # upstream, downstream, impact, path
    max_depth: Optional[int] = 10
    target_node_id: Optional[str] = None

class LineageResponse(BaseModel):
    """血缘查询响�?""
    success: bool
    data: Any
    message: str

@app.get("/lineage/node/{node_id}")
async def get_node_info(node_id: str):
    """
    获取节点信息
    
    Args:
        node_id: 节点ID
        
    Returns:
        节点信息
    """
    pass

@app.post("/lineage/query")
async def query_lineage(query: LineageQuery):
    """
    查询血缘关�?    
    Args:
        query: 查询请求
        
    Returns:
        血缘关�?    """
    pass

@app.get("/lineage/graph")
async def get_lineage_graph(
    node_id: Optional[str] = None,
    depth: int = 3
):
    """
    获取血缘图�?    
    Args:
        node_id: 节点ID（可选，不提供则返回全图�?        depth: 图谱深度
        
    Returns:
        血缘图�?    """
    pass

@app.get("/lineage/impact/{node_id}")
async def get_impact_scope(node_id: str):
    """
    获取影响范围
    
    Args:
        node_id: 节点ID
        
    Returns:
        影响范围
    """
    pass
```

---

## 四、数据库设计

### 4.1 PostgreSQL表结�?
```sql
-- 血缘元数据�?CREATE TABLE lineage_metadata (
    id SERIAL PRIMARY KEY,
    node_id VARCHAR(255) UNIQUE NOT NULL,
    node_type VARCHAR(50) NOT NULL,
    node_name VARCHAR(255) NOT NULL,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 血缘历史表
CREATE TABLE lineage_history (
    id SERIAL PRIMARY KEY,
    node_id VARCHAR(255) NOT NULL,
    operation VARCHAR(50) NOT NULL,
    old_value JSONB,
    new_value JSONB,
    operated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    operated_by VARCHAR(255)
);

-- 血缘质量表
CREATE TABLE lineage_quality (
    id SERIAL PRIMARY KEY,
    node_id VARCHAR(255) NOT NULL,
    quality_score DECIMAL(5, 2),
    completeness DECIMAL(5, 2),
    accuracy DECIMAL(5, 2),
    checked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建索引
CREATE INDEX idx_lineage_metadata_node_id ON lineage_metadata(node_id);
CREATE INDEX idx_lineage_metadata_node_type ON lineage_metadata(node_type);
CREATE INDEX idx_lineage_history_node_id ON lineage_history(node_id);
CREATE INDEX idx_lineage_quality_node_id ON lineage_quality(node_id);
```

### 4.2 Neo4j图结�?
```cypher
-- 创建节点索引
CREATE INDEX lineage_node_id_index FOR (n:LineageNode) ON (n.node_id);
CREATE INDEX lineage_node_type_index FOR (n:LineageNode) ON (n.node_type);

-- 创建边索�?CREATE INDEX lineage_edge_id_index FOR ()-[r:LINEAGE_EDGE]-() ON (r.edge_id);
```

---

## 五、自动化血缘更�?
### 5.1 设计背景

**传统血缘更新的局限�?*:
- �?血缘更新依赖人工配置，效率�?- �?数据变更后血缘关系不及时更新
- �?血缘关系容易过时，准确性低
- �?维护成本高，难以持续

**自动化血缘更新的优势**:
- �?实时捕获数据变更，自动更新血�?- �?血缘关系始终保持最新状�?- �?减少人工干预90%
- �?提高血缘准确�?0%

### 5.2 自动化血缘更新机�?
#### 5.2.1 基于CDC的血缘更�?
```python
from debezium import DebeziumConnector
from typing import Dict, List
import json

class CDCLineageUpdater:
    """基于CDC的血缘更新器"""
    
    def __init__(self, neo4j_client):
        self.neo4j_client = neo4j_client
        self.debezium = DebeziumConnector()
        
        # CDC配置
        self.cdc_config = {
            'connector.class': 'io.debezium.connector.postgresql.PostgresConnector',
            'database.hostname': 'localhost',
            'database.port': '5432',
            'database.user': 'postgres',
            'database.password': 'password',
            'database.dbname': 'zephyr_alpha',
            'table.include.list': 'public.stock_daily,public.factor_data'
        }
    
    def start_cdc_monitoring(self):
        """
        启动CDC监控
        
        监控数据变更:
        - INSERT: 新增数据
        - UPDATE: 更新数据
        - DELETE: 删除数据
        """
        # 启动Debezium连接�?        self.debezium.start(
            config=self.cdc_config,
            callback=self._handle_change_event
        )
    
    def _handle_change_event(self, event: Dict):
        """
        处理变更事件
        
        Args:
            event: Debezium变更事件
                {
                    'payload': {
                        'op': 'c',  # c=create, u=update, d=delete
                        'before': {...},
                        'after': {...},
                        'source': {
                            'table': 'stock_daily',
                            'db': 'zephyr_alpha'
                        }
                    }
                }
        """
        payload = event['payload']
        operation = payload['op']
        source = payload['source']
        
        table_name = f"{source['db']}.{source['table']}"
        
        if operation == 'c':
            # 新增数据，创建血缘节�?            self._create_lineage_node(table_name, payload['after'])
        
        elif operation == 'u':
            # 更新数据，更新血缘关�?            self._update_lineage_node(table_name, payload['before'], payload['after'])
        
        elif operation == 'd':
            # 删除数据，标记血缘节点为失效
            self._delete_lineage_node(table_name, payload['before'])
    
    def _create_lineage_node(self, table_name: str, data: Dict):
        """创建血缘节�?""
        # 提取数据来源信息
        source_info = self._extract_source_info(data)
        
        # 创建Cypher查询
        cypher = f"""
        MERGE (n:LineageNode {{node_id: $node_id}})
        SET n.table_name = $table_name,
            n.source = $source,
            n.timestamp = datetime(),
            n.status = 'active'
        """
        
        params = {
            'node_id': f"{table_name}_{data.get('id', '')}",
            'table_name': table_name,
            'source': source_info
        }
        
        self.neo4j_client.run(cypher, params)
    
    def _update_lineage_node(self, table_name: str, before: Dict, after: Dict):
        """更新血缘节�?""
        # 检查关键字段是否变�?        changed_fields = self._detect_changed_fields(before, after)
        
        if changed_fields:
            # 更新血缘关�?            cypher = f"""
            MATCH (n:LineageNode {{node_id: $node_id}})
            SET n.timestamp = datetime(),
                n.changed_fields = $changed_fields,
                n.status = 'updated'
            """
            
            params = {
                'node_id': f"{table_name}_{after.get('id', '')}",
                'changed_fields': list(changed_fields)
            }
            
            self.neo4j_client.run(cypher, params)
    
    def _delete_lineage_node(self, table_name: str, data: Dict):
        """删除血缘节�?""
        cypher = f"""
        MATCH (n:LineageNode {{node_id: $node_id}})
        SET n.status = 'deleted',
            n.deleted_at = datetime()
        """
        
        params = {
            'node_id': f"{table_name}_{data.get('id', '')}"
        }
        
        self.neo4j_client.run(cypher, params)
    
    def _extract_source_info(self, data: Dict) -> str:
        """提取数据来源信息"""
        # 从数据中提取来源信息
        if 'source' in data:
            return data['source']
        elif 'data_source' in data:
            return data['data_source']
        else:
            return 'unknown'
    
    def _detect_changed_fields(self, before: Dict, after: Dict) -> set:
        """检测变更字�?""
        changed = set()
        
        for key in set(before.keys()) | set(after.keys()):
            if before.get(key) != after.get(key):
                changed.add(key)
        
        return changed
```

#### 5.2.2 基于SQL解析的血缘更�?
```python
import sqlparse
from sqlparse.sql import Statement, IdentifierList, Identifier
from sqlparse.tokens import Keyword, DML
import re

class SQLLineageParser:
    """SQL血缘解析器"""
    
    def __init__(self):
        self.parsed_lineage = []
    
    def parse_sql(self, sql: str) -> Dict:
        """
        解析SQL语句，提取血缘关�?        
        Args:
            sql: SQL语句
        
        Returns:
            {
                'operation': 'INSERT',
                'source_tables': ['table_a', 'table_b'],
                'target_table': 'table_c',
                'column_mapping': {
                    'col1': 'table_a.col1',
                    'col2': 'table_b.col2'
                }
            }
        """
        # 解析SQL
        parsed = sqlparse.parse(sql)[0]
        
        # 识别操作类型
        operation = self._identify_operation(parsed)
        
        # 提取源表和目标表
        if operation == 'INSERT':
            lineage = self._parse_insert(parsed)
        elif operation == 'UPDATE':
            lineage = self._parse_update(parsed)
        elif operation == 'CREATE':
            lineage = self._parse_create_table_as(parsed)
        else:
            lineage = {
                'operation': operation,
                'source_tables': [],
                'target_table': None
            }
        
        self.parsed_lineage.append(lineage)
        return lineage
    
    def _identify_operation(self, parsed: Statement) -> str:
        """识别SQL操作类型"""
        first_token = parsed.token_first(skip_ws=True, skip_cm=True)
        
        if first_token:
            token_value = first_token.value.upper()
            
            if token_value == 'INSERT':
                return 'INSERT'
            elif token_value == 'UPDATE':
                return 'UPDATE'
            elif token_value == 'CREATE':
                return 'CREATE'
            elif token_value == 'SELECT':
                return 'SELECT'
        
        return 'UNKNOWN'
    
    def _parse_insert(self, parsed: Statement) -> Dict:
        """解析INSERT语句"""
        lineage = {
            'operation': 'INSERT',
            'source_tables': [],
            'target_table': None,
            'column_mapping': {}
        }
        
        # 提取目标�?        # INSERT INTO table_name ...
        tokens = parsed.tokens
        
        into_seen = False
        select_seen = False
        
        for i, token in enumerate(tokens):
            if token.match(Keyword, 'INTO'):
                into_seen = True
                continue
            
            if into_seen and isinstance(token, Identifier):
                lineage['target_table'] = token.get_real_name()
                into_seen = False
            
            if token.match(DML, 'SELECT'):
                select_seen = True
            
            if select_seen and isinstance(token, IdentifierList):
                # 提取源表
                for identifier in token.get_identifiers():
                    table_name = identifier.get_real_name()
                    if table_name:
                        lineage['source_tables'].append(table_name)
        
        return lineage
    
    def _parse_update(self, parsed: Statement) -> Dict:
        """解析UPDATE语句"""
        lineage = {
            'operation': 'UPDATE',
            'source_tables': [],
            'target_table': None
        }
        
        tokens = parsed.tokens
        
        update_seen = False
        
        for token in tokens:
            if token.match(DML, 'UPDATE'):
                update_seen = True
                continue
            
            if update_seen and isinstance(token, Identifier):
                lineage['target_table'] = token.get_real_name()
                break
        
        return lineage
    
    def _parse_create_table_as(self, parsed: Statement) -> Dict:
        """解析CREATE TABLE AS语句"""
        lineage = {
            'operation': 'CREATE',
            'source_tables': [],
            'target_table': None
        }
        
        tokens = parsed.tokens
        
        create_seen = False
        as_seen = False
        
        for token in tokens:
            if token.match(DML, 'CREATE'):
                create_seen = True
                continue
            
            if create_seen and isinstance(token, Identifier):
                lineage['target_table'] = token.get_real_name()
            
            if token.match(Keyword, 'AS'):
                as_seen = True
            
            if as_seen and isinstance(token, Identifier):
                table_name = token.get_real_name()
                if table_name:
                    lineage['source_tables'].append(table_name)
        
        return lineage
    
    def update_lineage_from_sql(self, sql: str, neo4j_client):
        """
        从SQL更新血缘关�?        
        Args:
            sql: SQL语句
            neo4j_client: Neo4j客户�?        """
        lineage = self.parse_sql(sql)
        
        if lineage['operation'] in ['INSERT', 'CREATE']:
            # 创建血缘关�?            for source_table in lineage['source_tables']:
                cypher = f"""
                MERGE (source:LineageNode {{table_name: $source_table}})
                MERGE (target:LineageNode {{table_name: $target_table}})
                MERGE (source)-[r:LINEAGE_EDGE]->(target)
                SET r.operation = $operation,
                    r.timestamp = datetime()
                """
                
                params = {
                    'source_table': source_table,
                    'target_table': lineage['target_table'],
                    'operation': lineage['operation']
                }
                
                neo4j_client.run(cypher, params)
```

#### 5.2.3 基于ETL管道的血缘更�?
```python
from typing import Dict, List
from datetime import datetime

class ETLPipelineLineageTracker:
    """ETL管道血缘追踪器"""
    
    def __init__(self, neo4j_client):
        self.neo4j_client = neo4j_client
        self.pipeline_registry = {}
    
    def register_pipeline(self, pipeline_config: Dict):
        """
        注册ETL管道
        
        Args:
            pipeline_config: 管道配置
                {
                    'pipeline_id': 'etl_001',
                    'name': 'Stock Data ETL',
                    'source_tables': ['raw_stock_data'],
                    'target_table': 'clean_stock_data',
                    'transformations': [
                        {
                            'type': 'filter',
                            'description': 'Filter invalid data'
                        },
                        {
                            'type': 'aggregate',
                            'description': 'Aggregate daily data'
                        }
                    ]
                }
        """
        pipeline_id = pipeline_config['pipeline_id']
        self.pipeline_registry[pipeline_id] = pipeline_config
        
        # 创建血缘关�?        self._create_pipeline_lineage(pipeline_config)
    
    def _create_pipeline_lineage(self, pipeline_config: Dict):
        """创建管道血缘关�?""
        cypher = f"""
        // 创建管道节点
        MERGE (p:Pipeline {{pipeline_id: $pipeline_id}})
        SET p.name = $name,
            p.transformations = $transformations,
            p.created_at = datetime()
        
        // 创建源表节点和关�?        WITH p
        UNWIND $source_tables AS source_table
        MERGE (s:LineageNode {{table_name: source_table}})
        MERGE (s)-[:INPUT_TO]->(p)
        
        // 创建目标表节点和关系
        WITH p
        MERGE (t:LineageNode {{table_name: $target_table}})
        MERGE (p)-[:OUTPUT_TO]->(t)
        """
        
        params = {
            'pipeline_id': pipeline_config['pipeline_id'],
            'name': pipeline_config['name'],
            'source_tables': pipeline_config['source_tables'],
            'target_table': pipeline_config['target_table'],
            'transformations': [t['description'] for t in pipeline_config['transformations']]
        }
        
        self.neo4j_client.run(cypher, params)
    
    def track_pipeline_execution(self, pipeline_id: str, execution_info: Dict):
        """
        追踪管道执行
        
        Args:
            pipeline_id: 管道ID
            execution_info: 执行信息
                {
                    'execution_id': 'exec_001',
                    'start_time': '2026-04-03 10:00:00',
                    'end_time': '2026-04-03 10:05:00',
                    'status': 'success',
                    'records_processed': 10000
                }
        """
        cypher = f"""
        MATCH (p:Pipeline {{pipeline_id: $pipeline_id}})
        CREATE (e:Execution {{
            execution_id: $execution_id,
            start_time: datetime($start_time),
            end_time: datetime($end_time),
            status: $status,
            records_processed: $records_processed
        }})
        CREATE (p)-[:HAS_EXECUTION]->(e)
        """
        
        params = {
            'pipeline_id': pipeline_id,
            'execution_id': execution_info['execution_id'],
            'start_time': execution_info['start_time'],
            'end_time': execution_info['end_time'],
            'status': execution_info['status'],
            'records_processed': execution_info['records_processed']
        }
        
        self.neo4j_client.run(cypher, params)
    
    def get_pipeline_lineage(self, pipeline_id: str) -> Dict:
        """
        获取管道血缘关�?        
        Args:
            pipeline_id: 管道ID
        
        Returns:
            {
                'pipeline_id': 'etl_001',
                'source_tables': ['raw_stock_data'],
                'target_table': 'clean_stock_data',
                'transformations': [...],
                'executions': [...]
            }
        """
        cypher = f"""
        MATCH (p:Pipeline {{pipeline_id: $pipeline_id}})
        OPTIONAL MATCH (s:LineageNode)-[:INPUT_TO]->(p)
        OPTIONAL MATCH (p)-[:OUTPUT_TO]->(t:LineageNode)
        OPTIONAL MATCH (p)-[:HAS_EXECUTION]->(e:Execution)
        RETURN p.name as pipeline_name,
               collect(DISTINCT s.table_name) as source_tables,
               t.table_name as target_table,
               p.transformations as transformations,
               collect(DISTINCT e) as executions
        """
        
        result = self.neo4j_client.run(cypher, {'pipeline_id': pipeline_id})
        
        return result[0] if result else None
```

### 5.3 血缘更新调�?
#### 5.3.1 定时更新任务

```python
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime

class LineageUpdateScheduler:
    """血缘更新调度器"""
    
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.cdc_updater = CDCLineageUpdater(None)
        self.sql_parser = SQLLineageParser()
    
    def start_scheduled_updates(self):
        """
        启动定时更新任务
        
        调度策略:
        - 每小时更新一次血缘统�?        - 每天凌晨清理过期血�?        - 每周生成血缘报�?        """
        # 每小时更新血缘统�?        self.scheduler.add_job(
            self._update_lineage_statistics,
            'interval',
            hours=1,
            id='update_lineage_stats'
        )
        
        # 每天凌晨清理过期血�?        self.scheduler.add_job(
            self._cleanup_expired_lineage,
            'cron',
            hour=2,
            minute=0,
            id='cleanup_lineage'
        )
        
        # 每周生成血缘报�?        self.scheduler.add_job(
            self._generate_lineage_report,
            'cron',
            day_of_week='mon',
            hour=8,
            minute=0,
            id='generate_lineage_report'
        )
        
        # 启动调度�?        self.scheduler.start()
    
    def _update_lineage_statistics(self):
        """更新血缘统计信�?""
        # 统计血缘节点数�?        # 统计血缘关系数�?        # 更新血缘覆盖率
        pass
    
    def _cleanup_expired_lineage(self):
        """清理过期血�?""
        # 删除status='deleted'且deleted_at超过30天的节点
        cypher = f"""
        MATCH (n:LineageNode)
        WHERE n.status = 'deleted' 
          AND n.deleted_at < datetime() - duration('P30D')
        DETACH DELETE n
        """
        
        # 执行清理
        pass
    
    def _generate_lineage_report(self):
        """生成血缘报�?""
        # 生成周报
        # 发送给相关人员
        pass
```

### 5.4 血缘变更通知

#### 5.4.1 变更通知服务

```python
from typing import List, Dict
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class LineageChangeNotifier:
    """血缘变更通知服务"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.smtp_server = config['smtp_server']
        self.smtp_port = config['smtp_port']
        self.sender_email = config['sender_email']
        self.sender_password = config['sender_password']
    
    def notify_lineage_change(
        self,
        change_type: str,
        change_details: Dict,
        recipients: List[str]
    ):
        """
        通知血缘变�?        
        Args:
            change_type: 变更类型（create, update, delete�?            change_details: 变更详情
            recipients: 接收者列�?        """
        # 构建邮件内容
        subject = f"[血缘变更通知] {change_type}"
        
        body = self._build_email_body(change_type, change_details)
        
        # 发送邮�?        self._send_email(subject, body, recipients)
    
    def _build_email_body(self, change_type: str, change_details: Dict) -> str:
        """构建邮件内容"""
        body = f"""
        血缘变更通知
        
        变更类型: {change_type}
        变更时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        
        变更详情:
        - 表名: {change_details.get('table_name')}
        - 变更字段: {change_details.get('changed_fields')}
        - 影响范围: {change_details.get('impact_scope')}
        
        请及时查看并确认�?        """
        
        return body
    
    def _send_email(self, subject: str, body: str, recipients: List[str]):
        """发送邮�?""
        msg = MIMEMultipart()
        msg['From'] = self.sender_email
        msg['To'] = ', '.join(recipients)
        msg['Subject'] = subject
        
        msg.attach(MIMEText(body, 'plain'))
        
        # 连接SMTP服务器并发�?        with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
            server.starttls()
            server.login(self.sender_email, self.sender_password)
            server.send_message(msg)
```

### 5.5 实施路线�?
#### 5.5.1 Phase 1: CDC血缘更新（Week 1�?
**任务**:
1. 配置Debezium CDC
2. 实现CDCLineageUpdater
3. 测试CDC血缘更�?
**交付�?*:
- �?Debezium配置
- �?CDCLineageUpdater
- �?测试报告

#### 5.5.2 Phase 2: SQL解析血缘更新（Week 2�?
**任务**:
1. 实现SQLLineageParser
2. 实现ETL管道追踪
3. 测试SQL血缘解�?
**交付�?*:
- �?SQLLineageParser
- �?ETLPipelineLineageTracker
- �?测试报告

#### 5.5.3 Phase 3: 调度与通知（Week 3�?
**任务**:
1. 实现血缘更新调度器
2. 实现变更通知服务
3. 部署上线

**交付�?*:
- �?LineageUpdateScheduler
- �?LineageChangeNotifier
- �?上线报告

### 5.6 预期收益

| 收益�?| 当前状�?| 自动化血缘更新后 | 提升幅度 |
|--------|---------|----------------|---------|
| **血缘更新及时�?* | 24小时 | 实时 | -100% |
| **血缘准确�?* | 70% | 95% | +25% |
| **人工干预时间** | 100% | 10% | -90% |
| **血缘覆盖率** | 80% | 98% | +18% |
| **维护成本** | �?| �?| -80% |

---

## 六、实施步�?
### 6.1 Week 1: 基础架构搭建

#### Day 1-2: 环境准备

**任务**:
1. 安装Neo4j数据库（Docker方式�?2. 安装PostgreSQL数据�?3. 安装Marquez可视化工�?4. 配置Python开发环�?
**命令**:
```bash
# 安装Neo4j
docker run -d \
    --name neo4j \
    -p 7474:7474 -p 7687:7687 \
    -e NEO4J_AUTH=neo4j/password123 \
    neo4j:4.4

# 安装PostgreSQL
docker run -d \
    --name postgres \
    -p 5432:5432 \
    -e POSTGRES_PASSWORD=password123 \
    postgres:13

# 安装Marquez
docker run -d \
    --name marquez \
    -p 5000:5000 \
    -p 3000:3000 \
    marquezproject/marquez:latest
```

#### Day 3-4: 核心模块开�?
**任务**:
1. 实现LineageCollector血缘采集器
2. 实现LineageStorage血缘存储器
3. 编写单元测试

**交付�?*:
```
src/
├── lineage/
�?  ├── __init__.py
�?  ├── collector.py          # LineageCollector
�?  ├── storage.py            # LineageStorage
�?  ├── models.py             # 数据模型
�?  └── tests/
�?      ├── test_collector.py
�?      └── test_storage.py
```

#### Day 5: 集成测试

**任务**:
1. 集成Neo4j和PostgreSQL
2. 测试血缘采集和存储功能
3. 性能测试

### 6.2 Week 2: 功能完善与可视化

#### Day 6-7: 血缘分析器开�?
**任务**:
1. 实现LineageAnalyzer血缘分析器
2. 实现上游/下游血缘查�?3. 实现影响范围分析
4. 实现血缘路径查�?
**交付�?*:
```
src/
├── lineage/
�?  ├── analyzer.py           # LineageAnalyzer
�?  └── tests/
�?      └── test_analyzer.py
```

#### Day 8-9: API服务开�?
**任务**:
1. 实现LineageService API
2. 实现RESTful接口
3. 编写API文档

**交付�?*:
```
src/
├── lineage/
�?  ├── api.py                # FastAPI服务
�?  └── tests/
�?      └── test_api.py
```

#### Day 10: 可视化界面集�?
**任务**:
1. 集成Marquez可视化工�?2. 自定义血缘图谱展�?3. 用户培训文档

---

## 六、验收标�?
### 6.1 功能验收

| 验收�?| 验收标准 | 验收方法 |
|--------|---------|---------|
| **血缘采�?* | �?5%数据有血缘记�?| 随机抽样检�?|
| **血缘存�?* | 血缘信息完整存储到Neo4j和PostgreSQL | 数据库查询验�?|
| **血缘查�?* | 查询响应时间<1�?| 性能测试 |
| **影响范围分析** | 正确识别所有下游影响节�?| 测试用例验证 |
| **可视化展�?* | 血缘图谱可视化展示 | 功能测试 |

### 6.2 性能验收

| 指标 | 目标�?| 测试方法 |
|------|--------|---------|
| **血缘查询延�?* | <1�?| 压力测试 |
| **血缘图谱加载时�?* | <3�?| 功能测试 |
| **血缘采集吞吐量** | >1000�?�?| 性能测试 |
| **系统可用�?* | >99.9% | 监控统计 |

### 6.3 质量验收

| 指标 | 目标�?| 验收方法 |
|------|--------|---------|
| **代码覆盖�?* | �?0% | pytest-cov |
| **文档完整�?* | 100% | 文档审查 |
| **API文档** | 完整 | Swagger UI |

---

## 七、风险评估与缓解

### 7.1 技术风�?
| 风险�?| 风险等级 | 影响 | 缓解措施 |
|--------|---------|------|---------|
| Neo4j学习曲线陡峭 | P2 | 延期2-3�?| 提前学习，参考官方文�?|
| 血缘采集性能问题 | P2 | 采集延迟 | 异步采集，批量处�?|
| 图谱可视化复�?| P2 | 开发延�?| 使用Marquez现成方案 |

### 7.2 资源风险

| 风险�?| 风险等级 | 影响 | 缓解措施 |
|--------|---------|------|---------|
| 开发时间紧�?| P1 | 功能不完�?| 优先实现核心功能，次要功能可延后 |
| 计算资源不足 | P2 | 性能下降 | 使用云服务弹性伸�?|

---

## 八、后续优化方�?
### 8.1 短期优化（Month 2�?
1. **血缘质量评�?*: 建立血缘质量评分机�?2. **血缘告�?*: 血缘缺失或异常时自动告�?3. **血缘报�?*: 自动生成血缘分析报�?
### 8.2 中期优化（Month 3-6�?
1. **智能血缘推�?*: 基于机器学习自动推断血缘关�?2. **血缘变更追�?*: 自动追踪血缘变更历�?3. **血缘合规审�?*: 支持数据合规审计

---

## 九、文档治�?
### 9.1 文档索引

**本文档在系统中的位置**:
- **父文�?*: [LAYER1_GAP_ANALYSIS_REPORT.md](../LAYER1_GAP_ANALYSIS_REPORT.md)
- **关联文档**:
  - [DATACLEANER_TECHNICAL_SPECIFICATION.md](../../05_TECHNICAL_SPECIFICATIONS/DATACLEANER_TECHNICAL_SPECIFICATION.md)
  - [DATA_QUALITY.md](../../../02_FACTOR_LIBRARY/04_DATA_SOURCE/DATA_QUALITY.md)

### 9.2 版本管理

**版本历史**:
- v1.0.0 (2026-04-02): 初始版本，完成数据血缘追踪系统设�?
---

**蓝图版本**: v1.0 | **创建日期**: 2026-04-02 | **状�?*: �?正式 | **维护�?*: ZephyrAlpha技术团�?