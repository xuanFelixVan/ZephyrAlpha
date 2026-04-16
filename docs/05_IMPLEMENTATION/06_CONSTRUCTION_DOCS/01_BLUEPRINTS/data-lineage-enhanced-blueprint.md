---
module_id: DATA_LINEAGE_ENHANCED_001_1675
version: 1.0.0
status: Active
priority: P0
created_date: 2026-04-07
last_updated: 2026-04-07
owner: 首席文档架构师
responsibility:
- 数据血缘追踪
standard_type: 专业量化机构蓝图
compliance_level: 专业标准
layer: layer_05
---



# 数据血缘增强蓝图



> **核心职责**: 提供全面的数据血缘追踪能力，支持数据流向分析、影响分析、数据溯源

> **职责边界**: 

> - ✅ 本文档负责：数据血缘追踪、数据流向分析、影响分析、数据溯源

> - ❌ 本文档不负责：数据质量管理（由数据质量模块负责）、元数据管理（由元数据管理模块负责）



## 核心定位



负责数据血缘增强模块的设计与构建，提供全面的数据血缘追踪能力，支持数据流向分析、影响分析、数据溯源，确保数据资产的可追溯性和透明度。



## 设计目标



### 主要目标



1. **数据血缘追踪**: 自动追踪数据的来源和去向

2. **数据流向分析**: 分析数据在系统中的流动路径

3. **影响分析**: 分析数据变更对下游的影响

4. **数据溯源**: 支持数据问题的溯源和定位



### 质量目标



- 血缘追踪准确率: ≥ 99%

- 血缘追踪覆盖率: 100%

- 影响分析准确率: ≥ 95%

- 查询响应时间: < 2秒



## 开源方案选型



### 推荐方案: OpenLineage



| 属性 | 详情 |

|------|------|

| **GitHub** | https://github.com/OpenLineage/OpenLineage |

| **Stars** | 1,800+ |

| **License** | Apache 2.0 |

| **语言** | Java/Python |

| **特点** | 开放的数据血缘标准，支持多种数据工具 |



**选择理由**:

1. **开放标准**: 行业开放标准，避免厂商锁定

2. **生态完善**: 支持Spark、Airflow、dbt等主流工具

3. **易于集成**: 提供多种客户端库

4. **可视化支持**: 支持Marquez等可视化工具

5. **个人友好**: 免费开源，适合个人使用

6. **社区活跃**: Linux基金会项目，社区支持好



## 核心功能设计



### 1. 数据血缘追踪模块



```python

from openlineage.client import OpenLineageClient

from openlineage.client.run import RunEvent, RunState, Run

from openlineage.client.facet import SourceCodeJobFacet

from datetime import datetime

from typing import Dict, List, Any, Optional

import uuid



class DataLineageTracker:

    """数据血缘追踪器"""

    

    def __init__(

        self,

        lineage_url: str = "http://localhost:5000",

        namespace: str = "zephyr-alpha"

    ):

        self.client = OpenLineageClient(url=lineage_url)

        self.namespace = namespace

    

    def track_job_execution(

        self,

        job_name: str,

        inputs: List[Dict],

        outputs: List[Dict],

        job_type: str = "ETL"

    ):

        """追踪作业执行"""

        run_id = str(uuid.uuid4())

        

        run_event = RunEvent(

            eventType=RunState.START,

            eventTime=datetime.now().isoformat(),

            run=Run(runId=run_id),

            job={

                "namespace": self.namespace,

                "name": job_name,

                "facets": {

                    "jobType": job_type

                }

            },

            inputs=self._build_datasets(inputs),

            outputs=self._build_datasets(outputs)

        )

        

        self.client.emit(run_event)

        

        return run_id

    

    def _build_datasets(self, datasets: List[Dict]) -> List[Dict]:

        """构建数据集信息"""

        return [

            {

                "namespace": self.namespace,

                "name": dataset.get("name"),

                "facets": {

                    "schema": dataset.get("schema"),

                    "dataSource": {

                        "name": dataset.get("source"),

                        "uri": dataset.get("uri")

                    }

                }

            }

            for dataset in datasets

        ]

    

    def track_data_transformation(

        self,

        source_table: str,

        target_table: str,

        transformation_logic: str,

        job_name: str = None

    ):

        """追踪数据转换"""

        job_name = job_name or f"transform_{source_table}_to_{target_table}"

        

        inputs = [{

            "name": source_table,

            "source": "database",

            "uri": f"postgresql://localhost:5432/zephyr/{source_table}"

        }]

        

        outputs = [{

            "name": target_table,

            "source": "database",

            "uri": f"postgresql://localhost:5432/zephyr/{target_table}"

        }]

        

        return self.track_job_execution(

            job_name=job_name,

            inputs=inputs,

            outputs=outputs,

            job_type="TRANSFORMATION"

        )

    

    def track_factor_calculation(

        self,

        factor_name: str,

        input_factors: List[str],

        output_table: str

    ):

        """追踪因子计算"""

        inputs = [

            {

                "name": f"factor_{factor}",

                "source": "factor_library",

                "uri": f"factor://library/{factor}"

            }

            for factor in input_factors

        ]

        

        outputs = [{

            "name": output_table,

            "source": "database",

            "uri": f"postgresql://localhost:5432/zephyr/{output_table}"

        }]

        

        return self.track_job_execution(

            job_name=f"calculate_factor_{factor_name}",

            inputs=inputs,

            outputs=outputs,

            job_type="FACTOR_CALCULATION"

        )

```



### 2. 数据流向分析模块



```python

import requests

from collections import defaultdict



class DataFlowAnalyzer:

    """数据流向分析器"""

    

    def __init__(self, marquez_url: str = "http://localhost:5000"):

        self.marquez_url = marquez_url

    

    def analyze_data_flow(

        self,

        dataset_name: str,

        direction: str = "downstream"

    ) -> Dict:

        """分析数据流向"""

        if direction == "downstream":

            return self._get_downstream_datasets(dataset_name)

        else:

            return self._get_upstream_datasets(dataset_name)

    

    def _get_downstream_datasets(

        self,

        dataset_name: str

    ) -> Dict:

        """获取下游数据集"""

        response = requests.get(

            f"{self.marquez_url}/api/v1/namespaces/zephyr-alpha/datasets/{dataset_name}"

        )

        

        if response.status_code != 200:

            raise Exception(f"Failed to get dataset: {response.text}")

        

        dataset = response.json()

        

        downstream = {

            "dataset": dataset_name,

            "downstream_datasets": [],

            "jobs": []

        }

        

        for job in dataset.get("fields", []):

            downstream["jobs"].append(job.get("name"))

        

        return downstream

    

    def _get_upstream_datasets(

        self,

        dataset_name: str

    ) -> Dict:

        """获取上游数据集"""

        response = requests.get(

            f"{self.marquez_url}/api/v1/namespaces/zephyr-alpha/datasets/{dataset_name}"

        )

        

        if response.status_code != 200:

            raise Exception(f"Failed to get dataset: {response.text}")

        

        dataset = response.json()

        

        upstream = {

            "dataset": dataset_name,

            "upstream_datasets": [],

            "jobs": []

        }

        

        for job in dataset.get("fields", []):

            upstream["jobs"].append(job.get("name"))

        

        return upstream

    

    def get_lineage_graph(

        self,

        dataset_name: str,

        depth: int = 3

    ) -> Dict:

        """获取血缘图谱"""

        graph = {

            "nodes": [],

            "edges": []

        }

        

        visited = set()

        

        self._build_graph_recursive(

            dataset_name,

            graph,

            visited,

            depth,

            0

        )

        

        return graph

    

    def _build_graph_recursive(

        self,

        dataset_name: str,

        graph: Dict,

        visited: set,

        max_depth: int,

        current_depth: int

    ):

        """递归构建图谱"""

        if current_depth >= max_depth or dataset_name in visited:

            return

        

        visited.add(dataset_name)

        

        graph["nodes"].append({

            "id": dataset_name,

            "type": "dataset",

            "depth": current_depth

        })

        

        downstream = self._get_downstream_datasets(dataset_name)

        

        for job in downstream.get("jobs", []):

            graph["edges"].append({

                "source": dataset_name,

                "target": job,

                "type": "job"

            })

```



### 3. 影响分析模块



```python

class ImpactAnalyzer:

    """影响分析器"""

    

    def __init__(self, flow_analyzer: DataFlowAnalyzer):

        self.flow_analyzer = flow_analyzer

    

    def analyze_change_impact(

        self,

        dataset_name: str,

        change_type: str = "schema_change"

    ) -> Dict:

        """分析变更影响"""

        impact = {

            "dataset": dataset_name,

            "change_type": change_type,

            "affected_datasets": [],

            "affected_jobs": [],

            "risk_level": "low",

            "recommendations": []

        }

        

        downstream = self.flow_analyzer.analyze_data_flow(

            dataset_name,

            direction="downstream"

        )

        

        impact["affected_datasets"] = downstream.get("downstream_datasets", [])

        impact["affected_jobs"] = downstream.get("jobs", [])

        

        if len(impact["affected_jobs"]) > 10:

            impact["risk_level"] = "high"

            impact["recommendations"].append("变更影响范围大，建议分阶段实施")

        elif len(impact["affected_jobs"]) > 5:

            impact["risk_level"] = "medium"

            impact["recommendations"].append("变更影响范围中等，需要充分测试")

        else:

            impact["recommendations"].append("变更影响范围小，可以正常实施")

        

        return impact

    

    def analyze_deletion_impact(

        self,

        dataset_name: str

    ) -> Dict:

        """分析删除影响"""

        impact = self.analyze_change_impact(

            dataset_name,

            change_type="deletion"

        )

        

        if impact["affected_jobs"]:

            impact["risk_level"] = "critical"

            impact["recommendations"].insert(

                0,

                f"删除操作会影响{len(impact['affected_jobs'])}个作业，强烈不建议删除"

            )

        

        return impact

    

    def analyze_schema_change_impact(

        self,

        dataset_name: str,

        old_schema: Dict,

        new_schema: Dict

    ) -> Dict:

        """分析Schema变更影响"""

        impact = self.analyze_change_impact(

            dataset_name,

            change_type="schema_change"

        )

        

        schema_changes = self._compare_schemas(old_schema, new_schema)

        

        impact["schema_changes"] = schema_changes

        

        if schema_changes.get("breaking_changes"):

            impact["risk_level"] = "high"

            impact["recommendations"].append(

                "存在破坏性变更，需要更新所有下游作业"

            )

        

        return impact

    

    def _compare_schemas(

        self,

        old_schema: Dict,

        new_schema: Dict

    ) -> Dict:

        """比较Schema差异"""

        changes = {

            "added_columns": [],

            "removed_columns": [],

            "modified_columns": [],

            "breaking_changes": []

        }

        

        old_columns = {col["name"]: col for col in old_schema.get("columns", [])}

        new_columns = {col["name"]: col for col in new_schema.get("columns", [])}

        

        for col_name in old_columns:

            if col_name not in new_columns:

                changes["removed_columns"].append(col_name)

                changes["breaking_changes"].append(f"删除列: {col_name}")

        

        for col_name in new_columns:

            if col_name not in old_columns:

                changes["added_columns"].append(col_name)

        

        for col_name in old_columns:

            if col_name in new_columns:

                if old_columns[col_name] != new_columns[col_name]:

                    changes["modified_columns"].append({

                        "name": col_name,

                        "old": old_columns[col_name],

                        "new": new_columns[col_name]

                    })

        

        return changes

```



## 技术实现



### 1. Marquez部署配置



```yaml

version: '3.8'



services:

  marquez:

    image: marquezproject/marquez:0.40.0

    container_name: zephyr-marquez

    ports:

      - "5000:5000"

      - "5001:5001"

    environment:

      - MARQUEZ_PORT=5000

      - MARQUEZ_ADMIN_PORT=5001

      - MARQUEZ_CONFIG=marquez.yml

    volumes:

      - ./marquez.yml:/opt/marquez/config/marquez.yml

      - marquez_data:/var/lib/marquez

    networks:

      - zephyr-network

    healthcheck:

      test: ["CMD", "wget", "-q", "--spider", "http://localhost:5000/health"]

      interval: 10s

      timeout: 5s

      retries: 3



  postgres:

    image: postgres:15

    container_name: zephyr-marquez-postgres

    environment:

      - POSTGRES_DB=marquez

      - POSTGRES_USER=marquez

      - POSTGRES_PASSWORD=marquez

    volumes:

      - postgres_data:/var/lib/postgresql/data

    networks:

      - zephyr-network



volumes:

  marquez_data:

  postgres_data:



networks:

  zephyr-network:

    external: true

```



### 2. Marquez配置文件



```yaml

server:

  applicationConnectors:

    - type: http

      port: 5000

  adminConnectors:

    - type: http

      port: 5001



database:

  driverClass: org.postgresql.Driver

  url: jdbc:postgresql://postgres:5432/marquez

  user: marquez

  password: marquez



migrations:

  tableName: marquez_migrations

```



## 实施路径



### Phase 1: 核心功能（Week 1）



**目标**: 实现基础数据血缘追踪



**任务清单**:

- [ ] 部署Marquez服务

- [ ] 实现数据血缘追踪

- [ ] 集成到ETL流程

- [ ] 实现血缘可视化

- [ ] 编写单元测试



**交付物**:

- Marquez部署配置

- DataLineageTracker类

- 单元测试覆盖率≥80%



### Phase 2: 高级功能（Week 2）



**目标**: 实现数据流向分析和影响分析



**任务清单**:

- [ ] 实现数据流向分析

- [ ] 实现影响分析

- [ ] 实现血缘图谱

- [ ] 配置Web UI

- [ ] 编写集成测试



**交付物**:

- DataFlowAnalyzer类

- ImpactAnalyzer类

- Web UI配置

- 集成测试覆盖率≥70%



```
```---
```



**文档版本**: v1.0.0

**创建日期**: 2026-04-07

**最后更新**: 2026-04-07

**状态**: Active



## 接口与契约（蓝图终稿）



- 全库 API 与事件约定真源：`API_Contract.md`。血缘采集、血缘查询、影响分析与变更事件等对外约定需以该真源或其子契约为准。

- 邻层协同边界：与 **Layer 0（数据源）**、**Layer 1（预处理/ETL）**、**Layer 10（治理与合规）** 的交互以契约为准（避免血缘口径与治理口径冲突）。



## 验收标准（可检查）



- 能采集并展示至少一条数据血缘关系（上游→下游），并可追溯到变换步骤或作业信息。

- 能对指定数据资产执行影响分析（列出下游消费者/报表/策略任一）并可复核。

- 能记录血缘变更事件（新增/变更/删除任一）并留痕（时间、范围、版本）。

- 在采集失败或元数据缺失时，能输出降级策略与告警记录。



## 已知限制



- 字段级血缘、事件载荷与采集适配器细化将在施工阶段固化到 `API_Contract.md` 子契约；本蓝图先确保边界、接口闭合点与验收闭环清晰。

