---

module_id: DATA_CATALOG_001_ARCHIVED_1

version: 1.0.0

status: Active

created_date: 2026-04-07

last_updated: 2026-04-07

owner: 首席文档架构师

responsibility:

  - 数据目录管理

  - 元数据管理

  - 数据发现

  - 数据血缘可视化

standard_type: 专业量化机构蓝图

compliance_level: 专业标准

layer: layer_05

---



# 数据目录蓝图



> **核心职责**: 提供统一的数据资产目录，支持数据发现、元数据管理、数据血缘可视化

> **职责边界**: 

> - ✅ 本文档负责：数据目录、元数据管理、数据发现、数据血缘

> - ❌ 本文档不负责：数据存储（由数据湖负责）、数据质量（由质量监控负责）



## 核心定位



负责数据目录模块的设计与构建，提供统一的数据资产发现入口，管理数据元信息，可视化数据血缘关系，支持数据治理和合规审计。



## 设计目标



### 主要目标



1. **数据发现**: 提供快速的数据资产搜索和发现能力

2. **元数据管理**: 统一管理数据表、字段、所有者等元信息

3. **数据血缘**: 可视化数据流转和依赖关系

4. **数据治理**: 支持数据分类、敏感标记、生命周期管理



### 质量目标



- 数据资产覆盖率: 100%

- 元数据准确性: 99%

- 血缘关系完整性: 95%

- 搜索响应时间: <500ms



## 开源方案选型



### 推荐方案: OpenMetadata



| 属性 | 详情 |

|------|------|

| **GitHub** | https://github.com/open-metadata/OpenMetadata |

| **Stars** | 5,000+ |

| **License** | Apache 2.0 |

| **语言** | Java/Python |

| **特点** | 一体化元数据平台，开箱即用 |



**选择理由**:

1. **功能完整**: 数据发现、元数据管理、血缘、质量、治理一体化

2. **易于部署**: Docker一键部署，无需复杂配置

3. **界面美观**: 现代化Web UI，用户体验好

4. **社区活跃**: 持续更新，文档完善

5. **个人友好**: 适合个人开发者使用



### 备选方案



| 项目 | Stars | 特点 | 推荐度 |

|------|-------|------|--------|

| **DataHub** | 10k+ | LinkedIn开源，功能强大 | ⭐⭐⭐⭐⭐ |

| **Amundsen** | 4k+ | Lyft开源，简单易用 | ⭐⭐⭐⭐ |



## 核心功能设计



### 1. 数据发现模块



```python

from metadata.ingestion.api.parser import MetadataServerConfig

from metadata.ingestion.source.database import DatabaseSource



class DataCatalog:

    """数据目录核心类"""

    

    def __init__(self, server_url: str):

        self.server_url = server_url

        self.client = OpenMetadataClient(server_url)

    

    def search_tables(self, query: str, filters: dict = None):

        """搜索数据表"""

        results = self.client.search(

            query=query,

            resource_type="table",

            filters=filters

        )

        return results

    

    def get_table_details(self, table_id: str):

        """获取表详情"""

        table = self.client.get_table(table_id)

        return {

            "name": table.name,

            "database": table.database.name,

            "schema": table.schema.name,

            "columns": [

                {

                    "name": col.name,

                    "type": col.dataType,

                    "description": col.description

                } for col in table.columns

            ],

            "tags": [tag.name for tag in table.tags],

            "owner": table.owner.name if table.owner else None

        }

    

    def get_table_lineage(self, table_id: str):

        """获取表血缘关系"""

        lineage = self.client.get_lineage(table_id)

        return {

            "upstream": lineage.upstream_nodes,

            "downstream": lineage.downstream_nodes

        }

```



### 2. 元数据管理模块



```python

class MetadataManager:

    """元数据管理器"""

    

    def __init__(self, catalog: DataCatalog):

        self.catalog = catalog

    

    def register_table(

        self,

        database: str,

        schema: str,

        table_name: str,

        columns: list,

        description: str = None,

        tags: list = None,

        owner: str = None

    ):

        """注册数据表"""

        table_metadata = {

            "name": table_name,

            "database": database,

            "schema": schema,

            "columns": columns,

            "description": description,

            "tags": tags or [],

            "owner": owner

        }

        

        return self.catalog.client.create_or_update_table(table_metadata)

    

    def update_column_description(

        self,

        table_id: str,

        column_name: str,

        description: str

    ):

        """更新字段描述"""

        return self.catalog.client.update_column(

            table_id=table_id,

            column_name=column_name,

            description=description

        )

    

    def add_tag_to_table(self, table_id: str, tag_name: str):

        """为表添加标签"""

        return self.catalog.client.add_tag(

            entity_id=table_id,

            entity_type="table",

            tag_name=tag_name

        )

```



### 3. 数据血缘模块



```python

class LineageTracker:

    """数据血缘追踪器"""

    

    def __init__(self, catalog: DataCatalog):

        self.catalog = catalog

    

    def add_lineage(

        self,

        from_table: str,

        to_table: str,

        lineage_type: str = "TRANSFORMS"

    ):

        """添加血缘关系"""

        lineage_edge = {

            "fromEntity": {"id": from_table, "type": "table"},

            "toEntity": {"id": to_table, "type": "table"},

            "lineageType": lineage_type

        }

        

        return self.catalog.client.add_lineage(lineage_edge)

    

    def get_upstream_tables(self, table_id: str, depth: int = 5):

        """获取上游表"""

        lineage = self.catalog.get_table_lineage(table_id)

        upstream = []

        

        for node in lineage["upstream"]:

            if depth > 0:

                upstream.append({

                    "table": node,

                    "upstream": self.get_upstream_tables(node["id"], depth - 1)

                })

        

        return upstream

    

    def get_downstream_tables(self, table_id: str, depth: int = 5):

        """获取下游表"""

        lineage = self.catalog.get_table_lineage(table_id)

        downstream = []

        

        for node in lineage["downstream"]:

            if depth > 0:

                downstream.append({

                    "table": node,

                    "downstream": self.get_downstream_tables(node["id"], depth - 1)

                })

        

        return downstream

    

    def visualize_lineage(self, table_id: str):

        """可视化血缘关系"""

        import networkx as nx

        import matplotlib.pyplot as plt

        

        G = nx.DiGraph()

        

        def add_nodes(table_id, direction, depth=0):

            if depth > 3:

                return

            

            if direction == "upstream":

                upstream = self.get_upstream_tables(table_id, 1)

                for node in upstream:

                    G.add_edge(node["table"]["name"], table_id)

                    add_nodes(node["table"]["id"], direction, depth + 1)

            else:

                downstream = self.get_downstream_tables(table_id, 1)

                for node in downstream:

                    G.add_edge(table_id, node["table"]["name"])

                    add_nodes(node["table"]["id"], direction, depth + 1)

        

        add_nodes(table_id, "upstream")

        add_nodes(table_id, "downstream")

        

        nx.draw(G, with_labels=True, node_color='lightblue', 

                node_size=1500, font_size=10)

        plt.savefig(f"lineage_{table_id}.png")

```



### 4. 数据治理模块



```python

class DataGovernance:

    """数据治理管理器"""

    

    def __init__(self, catalog: DataCatalog):

        self.catalog = catalog

    

    def classify_sensitive_data(self, table_id: str, column_name: str):

        """标记敏感数据"""

        return self.catalog.client.add_tag(

            entity_id=table_id,

            entity_type="table",

            tag_name="PII",

            column_name=column_name

        )

    

    def set_data_retention_policy(

        self,

        table_id: str,

        retention_days: int

    ):

        """设置数据保留策略"""

        policy = {

            "table_id": table_id,

            "retention_days": retention_days,

            "created_at": datetime.now().isoformat()

        }

        

        return self.catalog.client.set_custom_property(

            table_id=table_id,

            property_name="retention_policy",

            property_value=policy

        )

    

    def get_data_quality_score(self, table_id: str):

        """获取数据质量评分"""

        quality = self.catalog.client.get_data_quality(table_id)

        

        return {

            "overall_score": quality.overall_score,

            "completeness": quality.completeness,

            "accuracy": quality.accuracy,

            "timeliness": quality.timeliness

        }

```



## 部署架构



### Docker Compose部署



```yaml

version: '3.8'



services:

  openmetadata-server:

    image: openmetadata/server:1.3.0

    ports:

      - "8585:8585"

    environment:

      - OPENMETADATA_MYSQL_HOST=mysql

      - OPENMETADATA_MYSQL_PORT=3306

      - OPENMETADATA_MYSQL_USER=openmetadata_user

      - OPENMETADATA_MYSQL_PASSWORD=${MYSQL_PASSWORD}

      - OPENMETADATA_MYSQL_DATABASE=openmetadata_db

      - ELASTICSEARCH_HOST=elasticsearch

      - ELASTICSEARCH_PORT=9200

    depends_on:

      - mysql

      - elasticsearch

    volumes:

      - openmetadata_data:/openmetadata

    restart: unless-stopped

  

  openmetadata-ingestion:

    image: openmetadata/ingestion:1.3.0

    environment:

      - OPENMETADATA_SERVER_URL=http://openmetadata-server:8585

    depends_on:

      - openmetadata-server

    restart: unless-stopped

  

  mysql:

    image: mysql:8.0

    environment:

      - MYSQL_ROOT_PASSWORD=${MYSQL_ROOT_PASSWORD}

      - MYSQL_USER=openmetadata_user

      - MYSQL_PASSWORD=${MYSQL_PASSWORD}

      - MYSQL_DATABASE=openmetadata_db

    volumes:

      - mysql_data:/var/lib/mysql

    restart: unless-stopped

  

  elasticsearch:

    image: elasticsearch:8.11.0

    environment:

      - discovery.type=single-node

      - xpack.security.enabled=false

      - "ES_JAVA_OPTS=-Xms512m -Xmx512m"

    volumes:

      - es_data:/usr/share/elasticsearch/data

    restart: unless-stopped



volumes:

  openmetadata_data:

  mysql_data:

  es_data:

```



## 与现有系统集成



### 1. 与数据血缘追踪集成



```python

# 在DATA_LINEAGE_TRACKING_BLUEPRINT中使用OpenMetadata

from openmetadata.lineage import LineageClient



class EnhancedLineageTracker:

    """增强版血缘追踪器"""

    

    def __init__(self, openmetadata_url: str):

        self.client = LineageClient(openmetadata_url)

    

    def track_transformation(

        self,

        source_table: str,

        target_table: str,

        transformation_sql: str

    ):

        """追踪转换血缘"""

        lineage = {

            "source": source_table,

            "target": target_table,

            "transformation": transformation_sql,

            "timestamp": datetime.now()

        }

        

        self.client.add_lineage(lineage)

```



### 2. 与数据质量监控集成



```python

# 在REALTIME_QUALITY_MONITOR_BLUEPRINT中集成

class QualityAwareCatalog:

    """集成质量监控的数据目录"""

    

    def __init__(self, catalog: DataCatalog, quality_monitor):

        self.catalog = catalog

        self.quality_monitor = quality_monitor

    

    def get_table_with_quality(self, table_id: str):

        """获取表信息及质量状态"""

        table = self.catalog.get_table_details(table_id)

        quality = self.quality_monitor.get_latest_quality(table_id)

        

        return {

            **table,

            "quality_status": quality.status,

            "quality_score": quality.score,

            "last_quality_check": quality.timestamp

        }

```



## 实施计划



### 阶段1: 基础部署 (Week 1-2)



| 任务 | 工时 | 负责人 | 交付物 |

|------|------|--------|--------|

| Docker环境搭建 | 4h | 开发者 | Docker Compose配置 |

| OpenMetadata部署 | 8h | 开发者 | 运行中的数据目录 |

| 基础配置 | 4h | 开发者 | 配置文件 |

| 测试验证 | 4h | 开发者 | 测试报告 |



### 阶段2: 数据接入 (Week 3-4)



| 任务 | 工时 | 负责人 | 交付物 |

|------|------|--------|--------|

| MySQL数据源接入 | 8h | 开发者 | MySQL元数据同步 |

| ClickHouse数据源接入 | 8h | 开发者 | ClickHouse元数据同步 |

| 文件系统数据源接入 | 4h | 开发者 | 文件元数据同步 |

| 自定义数据源接入 | 8h | 开发者 | 自定义数据源配置 |



### 阶段3: 功能增强 (Week 5-6)



| 任务 | 工时 | 负责人 | 交付物 |

|------|------|--------|--------|

| 血缘可视化增强 | 8h | 开发者 | 血缘图表 |

| 数据质量集成 | 8h | 开发者 | 质量监控集成 |

| 告警通知集成 | 4h | 开发者 | 告警配置 |

| 用户培训 | 4h | 开发者 | 使用文档 |



## 性能指标



| 指标 | 目标值 | 测量方法 |

|------|--------|---------|

| **搜索响应时间** | <500ms | 平均搜索延迟 |

| **元数据同步延迟** | <5min | 数据变更到目录更新时间 |

| **血缘查询时间** | <1s | 血缘关系查询延迟 |

| **系统可用性** | 99.9% | 月度可用性统计 |



## 成本估算



| 项目 | 开源方案成本 | 商业方案成本 |

|------|-------------|-------------|

| **软件许可** | $0 | $50k+/年 |

| **部署运维** | 自行维护 | 供应商支持 |

| **硬件资源** | 4核8G | 云服务费用 |

| **总成本** | $0 + 运维时间 | $50k+/年 |



## 接口与契约（蓝图终稿）



- 全库 API 与事件约定真源：`API_Contract.md`。数据目录涉及的元数据模型、搜索查询、血缘关联、质量状态联动与变更事件等对外约定需以该真源或其子契约为准。

- 邻层协同边界：与 **Layer 0（数据源）**、**Layer 1（数据层/预处理）**、**Layer 10（治理与合规）** 的交互以契约为准（避免元数据口径与治理口径冲突）。



## 验收标准（可检查）



- 能注册并查询至少一个数据资产（表/数据集任一），并返回可复核的元数据字段（所有者、更新频率、敏感级别任一）。

- 能在 <500ms 级别完成一次搜索查询（基于文档既定指标），并能说明测量口径。

- 能展示至少一条血缘关系（上游/下游任一），并可追溯到变换说明或记录。

- 能关联并展示质量状态（来自质量监控模块的最新评分/状态任一），并可追溯来源。



## 已知限制



- 元数据字段字典、事件载荷与权限模型细化将在施工阶段固化到 `API_Contract.md` 子契约；本蓝图先确保边界、接口闭合点与验收闭环清晰。



```---



**文档版本**: v1.0.0

**创建日期**: 2026-04-07

**最后更新**: 2026-04-07

**状态**: Active

