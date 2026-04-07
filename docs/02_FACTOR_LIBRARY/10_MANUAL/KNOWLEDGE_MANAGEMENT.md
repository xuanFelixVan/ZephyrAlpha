﻿---
module_id: KNOWLEDGE_MANAGEMENT_FACTOR_001
version: 1.0.0
status: Active
created_date: 2026-04-07
last_updated: 2026-04-07
owner: 因子工程团队
standard_type: 通用文档
applicable_scope: 全系统
compliance_level: 专业标准
responsibility:
  - 因子计算、因子库管理

---
---



# 知识管理蓝图
> **核心职责**: 知识管理体系和方法论，涉及知识管理蓝图
> **职责边界**: 
> - ✅ 本文档负责：知识管理体系和方法论相关内容
> - ❌ 本文档不负责：具体实现细节、其他模块内容


> 清风量化系统 v5.0 - AI知识管理系统
> **索引**: `KNOWLEDGE.001`
> **开发时?*: 25h
> **优先?*: P1
> **核心定位**: AI自动提取和更新研究知识，实现"AI研究 ?自动入库 ?可查询复?


## 1. 设计原则

| 原则 | 说明 |
|------|------|
| **Obsidian + AI** | Obsidian手工 + AI自动提取，混合模?|
| **向量检?* | 使用向量数据库实现语义检?|
| **自动入库** | 实验完成后自动提取关键信息入?|
| **可追?* | 完整记录知识来源和血?|


## 2. 知识管理架构

### 2.1 知识来源

```
┌─────────────────────────────────────────────────────────────?
?                   知识来源                                  ?
├─────────────────────────────────────────────────────────────?
? wandb实验报告 ──?AI自动提取 ──?知识?                ?
? 研究笔记 ───────?AI辅助整理 ──?知识?                ?
? 策略代码 ──────?AI自动注释 ──?知识?                  ?
? 回测报告 ──────?AI自动总结 ──?知识?                  ?
? 人工整理 ──────────────────────?知识?Obsidian)       ?
└─────────────────────────────────────────────────────────────?
```

### 2.2 知识类型

| 知识类型 | 说明 | 入库方式 |
|----------|------|----------|
| 因子知识 | 因子定义、IC表现、适用场景 | AI自动提取 |
| 策略知识 | 策略逻辑、参数、表?| AI自动提取 |
| 教训知识 | 失败原因、注意事?| 人工整理+AI辅助 |
| 市场知识 | 市场状态、季节性、事?| AI自动提取 |
| 代码知识 | 代码片段、最佳实?| AI自动注释 |


## 3. 知识库实?

### 3.1 向量数据库选型

| 方案 | 说明 | 推荐?|
|------|------|--------|
| **Chroma** | 轻量级，易用，免?| ⭐⭐⭐⭐?|
| FAISS | Facebook开源，高性能 | ⭐⭐⭐⭐ |
| Milvus | 功能强大，需要运?| ⭐⭐?|

**选择**: Chroma (个人使用足够简?

### 3.2 知识库核心类

```python
from chromadb import Client
from chromadb.config import Settings

class KnowledgeBase:
    """知识?

    索引: KNOWLEDGE.001-M01
    上游: wandb, ResearchPipeline
    下游: ResearchAgent
    """

    def __init__(self, persist_dir: str = "./data/knowledge"):
        self.client = Client(Settings(
            persist_directory=persist_dir,
            anonymized_telemetry=False
        ))
        self.collection = self.client.get_or_create_collection(
            name="quant_knowledge",
            metadata={"description": "量化研究知识?}
        )

    def add_knowledge(
        self,
        content: str,
        metadata: dict,
        category: str
    ):
        """添加知识

        参数:
            content: 知识内容
            metadata: 元数?(来源、时间、标签等)
            category: 知识类别 (factor/strategy/lesson/market)
        """
        self.collection.add(
            documents=[content],
            metadatas=[{
                **metadata,
                'category': category
            }],
            ids=[f"{category}_{metadata.get('id', uuid.uuid4())}"]
        )

    def query(self, query: str, n_results: int = 5) -> list:
        """语义检?

        参数:
            query: 查询文本
            n_results: 返回数量

        返回:
            相似知识列表
        """
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results
        )
        return results

    def add_factor_knowledge(self, factor_data: dict):
        """添加因子知识

        参数:
            factor_data: {
                'name': 'momentum_20',
                'definition': '20日动量因?,
                'ic_mean': 0.045,
                'ic_ir': 0.52,
                'best_params': {'period': 20},
                'notes': '适用于趋势市?
            }
        """
        content = f"""
        因子名称: {factor_data['name']}
        因子定义: {factor_data['definition']}
        IC均? {factor_data.get('ic_mean', 'N/A')}
        IC_IR: {factor_data.get('ic_ir', 'N/A')}
        最优参? {factor_data.get('best_params', {})}
        使用注意: {factor_data.get('notes', '')}
        """

        self.add_knowledge(
            content=content,
            metadata={
                'source': 'wandb',
                'id': factor_data['id'],
                'created_at': datetime.now().isoformat()
            },
            category='factor'
        )

    def add_strategy_knowledge(self, strategy_data: dict):
        """添加策略知识"""
        content = f"""
        策略名称: {strategy_data['name']}
        策略类型: {strategy_data.get('type', 'N/A')}
        核心逻辑: {strategy_data.get('logic', 'N/A')}
        夏普比率: {strategy_data.get('sharpe', 'N/A')}
        最大回? {strategy_data.get('max_drawdown', 'N/A')}
        适用场景: {strategy_data.get('scenario', 'N/A')}
        """

        self.add_knowledge(
            content=content,
            metadata={
                'source': 'wandb',
                'id': strategy_data['id'],
                'created_at': datetime.now().isoformat()
            },
            category='strategy'
        )
```


## 4. AI自动提取

### 4.1 实验报告自动提取

```python
class ExperimentExtractor:
    """实验报告自动提取

    索引: KNOWLEDGE.001-M02
    """

    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4")

    def extract_from_wandb(self, run_id: str) -> dict:
        """从wandb实验提取知识

        参数:
            run_id: wandb run ID

        返回:
            提取的知?
        """
        # 获取实验数据
        run = wandb.Api().run(run_id)

        # AI提取关键信息
        prompt = f"""
        从以下实验数据中提取关键知识:

        实验名称: {run.name}
        实验配置: {run.config}
        实验指标: {run.summaryMetrics}

        请提?
        1. 核心发现
        2. 成功要素
        3. 失败教训
        4. 适用场景
        """

        response = self.llm.invoke(prompt)
        knowledge = self._parse_response(response)

        return knowledge

    def extract_from_report(self, report_text: str) -> dict:
        """从研究报告中提取知识"""
        prompt = f"""
        从以下研究报告中提取关键知识:

        {report_text}

        请提?
        1. 核心发现
        2. 方法?
        3. 适用条件
        4. 注意事项
        """

        response = self.llm.invoke(prompt)
        return self._parse_response(response)
```

### 4.2 知识入库流程

```python
class KnowledgeIngestion:
    """知识入库流程

    索引: KNOWLEDGE.001-M03
    """

    def __init__(self):
        self.kb = KnowledgeBase()
        self.extractor = ExperimentExtractor()

    def on_experiment_complete(self, experiment_id: str):
        """实验完成回调

        实验完成后自动提取知识入?
        """
        # 1. 从wandb提取知识
        knowledge = self.extractor.extract_from_wandb(experiment_id)

        # 2. 根据类型入库
        if knowledge['type'] == 'factor':
            self.kb.add_factor_knowledge(knowledge)
        elif knowledge['type'] == 'strategy':
            self.kb.add_strategy_knowledge(knowledge)

        # 3. 更新Obsidian
        self._update_obsidian(knowledge)
```


## 5. 知识查询

### 5.1 Agent查询接口

```python
class KnowledgeQuery:
    """知识查询

    索引: KNOWLEDGE.001-M04
    Tool: query_knowledge_base
    """

    def __init__(self):
        self.kb = KnowledgeBase()

    def query_for_research(self, objective: str) -> list:
        """为研究查询相关知?

        参数:
            objective: 研究目标

        返回:
            相关知识列表
        """
        # 语义检?
        results = self.kb.query(objective, n_results=10)

        # 格式化输?
        return [
            {
                'content': r['document'],
                'category': r['metadata']['category'],
                'source': r['metadata']['source'],
                'relevance': r.get('distance', 1.0)
            }
            for r in results['results'][0]
        ]

    def get_related_factors(self, factor_name: str) -> list:
        """获取相关因子

        参数:
            factor_name: 因子名称

        返回:
            相关因子列表
        """
        return self.kb.query(f"相关因子 {factor_name}", n_results=5)

    def get_strategy_lessons(self, strategy_type: str) -> list:
        """获取策略教训

        参数:
            strategy_type: 策略类型

        返回:
            教训列表
        """
        return self.kb.query(f"{strategy_type} 策略 教训 失败", n_results=5)
```


## 6. Obsidian集成

### 6.1 Obsidian配置

```
vault/
├── 00_知识?
?  ├── 因子/
?  ?  ├── momentum_20.md
?  ?  └── value_factor.md
?  ├── 策略/
?  ?  ├── trend_following.md
?  ?  └── mean_reversion.md
?  └── 教训/
?      └── common_mistakes.md
```

### 6.2 AI自动更新Obsidian

```python
class ObsidianUpdater:
    """Obsidian自动更新

    索引: KNOWLEDGE.001-M05
    """

    def __init__(self, vault_path: str):
        self.vault_path = vault_path

    def update_factor_note(self, factor_data: dict):
        """更新因子笔记

        参数:
            factor_data: 因子数据
        """
        note_path = f"{self.vault_path}/00_知识?因子/{factor_data['name']}.md"

        content = f"""---
type: factor
created: {datetime.now().isoformat()}
tags: [{', '.join(factor_data.get('tags', []))}]

# {factor_data['name']}

## 定义
{factor_data.get('definition', '')}

## 表现
| 指标 | ?|
|------|-----|
| IC均?| {factor_data.get('ic_mean', 'N/A')} |
| IC_IR | {factor_data.get('ic_ir', 'N/A')} |

## 最优参?
```json
{factor_data.get('best_params', {})}
```

## 使用注意
{factor_data.get('notes', '')}

## 来源
- 实验ID: {factor_data.get('experiment_id', 'N/A')}
- wandb: {factor_data.get('wandb_url', 'N/A')}
"""

        with open(note_path, 'w', encoding='utf-8') as f:
            f.write(content)
```


## 7. API接口

### 7.1 知识库API

```python
# API: /api/v1/knowledge

class KnowledgeAPI:
    """知识库API

    索引: API_KNOWLEDGE_001
    """

    @router.get("/query")
    def query_knowledge(
        q: str,
        category: str = None,
        n_results: int = 5
    ) -> List[KnowledgeItem]:
        """查询知识

        参数:
            q: 查询文本
            category: 知识类别过滤
            n_results: 返回数量
        """

    @router.post("/add")
    def add_knowledge(
        content: str,
        category: str,
        metadata: dict
    ) -> str:
        """添加知识"""

    @router.get("/factors")
    def list_factors() -> List[FactorSummary]:
        """列出所有因?""

    @router.get("/strategies")
    def list_strategies() -> List[StrategySummary]:
        """列出所有策?""

    @router.post("/sync/obsidian")
    def sync_obsidian() -> SyncResult:
        """同步Obsidian"""
```


## 8. 开发任务分?

### 8.1 任务分解 (25h)

| 任务 | 时间 | 说明 |
|------|------|------|
| Chroma环境搭建 | 2h | Chroma安装+配置 |
| 知识库核心类 | 6h | KnowledgeBase实现 |
| 向量提取?| 6h | ExperimentExtractor |
| 知识入库流程 | 4h | KnowledgeIngestion |
| 查询接口 | 4h | KnowledgeQuery |
| Obsidian集成 | 3h | ObsidianUpdater |
| API?| 2h | REST API |
| 测试 | 2h | 集成测试 |


## 9. 监控指标

### 9.1 关键指标

| 指标 | 说明 | 阈?|
|------|------|------|
| knowledge_count | 知识条目?| - |
| query_count | 查询次数/?| - |
| query_hit_rate | 查询命中?| >70% |
| auto_ingest_rate | 自动入库?| >80% |


## 10. 测试策略

### 10.1 测试分层

```
单元测试 (KnowledgeBase类测?
    ?
集成测试 (Chroma API测试)
    ?
端到端测?(完整知识管理流程)
```

### 10.2 单元测试

```python
# tests/unit/test_knowledge_management.py

import pytest
from unittest.mock import Mock, patch, MagicMock
from src.knowledge.base import KnowledgeBase
from src.knowledge.extractor import KnowledgeExtractor

class TestKnowledgeBase:
    """知识库单元测?""

    def setup_method(self):
        """测试前准?""
        with patch('src.knowledge.base.Client') as mock_client:
            self.mock_collection = MagicMock()
            mock_client.return_value.get_or_create_collection.return_value = self.mock_collection
            self.kb = KnowledgeBase(persist_dir="/tmp/test_kb")

    def test_add_knowledge(self):
        """测试添加知识"""
        self.kb.add_knowledge(
            content="MACD因子?024年表现良?,
            category="factor",
            metadata={"factor_name": "MACD"}
        )
        self.mock_collection.add.assert_called_once()

    def test_query_knowledge(self):
        """测试查询知识"""
        self.mock_collection.query.return_value = {
            'documents': [["MACD因子表现良好"]],
            'metadatas': [[{"category": "factor"}]],
            'distances': [[0.1]]
        }

        results = self.kb.query("MACD因子怎么?, n_results=5)
        assert len(results) == 1
        assert results[0]['content'] == "MACD因子表现良好"

    def test_query_with_filter(self):
        """测试带过滤的查询"""
        self.mock_collection.query.return_value = {
            'documents': [["动量因子"]],
            'metadatas': [[{"category": "factor"}]],
            'distances': [[0.2]]
        }

        results = self.kb.query(
            "动量因子",
            filter={"category": "factor"}
        )
        assert results[0]['category'] == "factor"

    def test_delete_knowledge(self):
        """测试删除知识"""
        self.kb.delete_knowledge("test_id")
        self.mock_collection.delete.assert_called_with(ids=["test_id"])

    def test_update_knowledge(self):
        """测试更新知识"""
        self.kb.update_knowledge(
            "test_id",
            content="更新后的内容"
        )
        self.mock_collection.update.assert_called_once()

class TestKnowledgeExtractor:
    """知识提取器测?""

    def setup_method(self):
        self.extractor = KnowledgeExtractor()

    def test_extract_from_factor_result(self):
        """测试从因子结果提取知?""
        factor_result = {
            'factor_name': 'momentum_20',
            'ic_mean': 0.045,
            'ic_ir': 1.2,
            'decay_5d': 0.85,
            'experiment_id': 'exp_001'
        }

        knowledge = self.extractor.extract_from_factor_result(factor_result)

        assert knowledge.category == "factor"
        assert "momentum_20" in knowledge.content
        assert "0.045" in knowledge.content
        assert knowledge.metadata['ic_mean'] == 0.045

    def test_extract_from_strategy_result(self):
        """测试从策略结果提取知?""
        strategy_result = {
            'strategy_name': 'trend_following',
            'annual_return': 0.15,
            'sharpe_ratio': 1.8,
            'max_drawdown': 0.12
        }

        knowledge = self.extractor.extract_from_strategy_result(strategy_result)

        assert knowledge.category == "strategy"
        assert "trend_following" in knowledge.content
        assert knowledge.metadata['sharpe_ratio'] == 1.8

    def test_extract_failure_case(self):
        """测试从失败案例提取知?""
        failure_result = {
            'experiment_id': 'exp_002',
            'reason': '过拟?,
            'ic_train': 0.08,
            'ic_test': 0.02
        }

        knowledge = self.extractor.extract_failure_case(failure_result)

        assert knowledge.category == "failure"
        assert "过拟? in knowledge.content
        assert knowledge.metadata['experiment_id'] == 'exp_002'
```

### 10.3 集成测试

```python
# tests/integration/test_knowledge_integration.py

import pytest
from src.knowledge.base import KnowledgeBase
from src.knowledge.ingestion import KnowledgeIngestion

class TestKnowledgeIntegration:
    """知识库集成测?""

    @pytest.fixture
    def kb(self):
        return KnowledgeBase(persist_dir="/tmp/test_kb")

    @pytest.fixture
    def ingestion(self, kb):
        return KnowledgeIngestion(kb)

    def test_full_ingestion_flow(self, kb, ingestion):
        """测试完整入库流程"""
        # 1. 模拟实验结果
        experiment_result = {
            'experiment_id': 'exp_001',
            'type': 'factor_research',
            'factor_name': 'momentum_20',
            'ic_mean': 0.045,
            'ic_ir': 1.2,
            'status': 'completed'
        }

        # 2. 提取知识
        knowledge = ingestion.extract_from_experiment(experiment_result)

        # 3. 入库
        ingestion.ingest(knowledge)

        # 4. 验证查询
        results = kb.query("动量因子表现")
        assert len(results) > 0

    def test_obsidian_sync(self, kb, ingestion):
        """测试Obsidian同步"""
        # 1. 添加知识
        kb.add_knowledge(
            content="# 动量因子\n\nIC=0.045",
            category="factor",
            metadata={"source": "experiment"}
        )

        # 2. 同步到Obsidian
        ingestion.sync_to_obsidian(
            vault_path="/tmp/test_vault"
        )

        # 3. 验证文件已创?
        note_path = Path("/tmp/test_vault/factors/momentum_20.md")
        assert note_path.exists()

### 10.4 端到端测?

```python
# tests/e2e/test_knowledge_e2e.py

class TestKnowledgeE2E:
    """知识管理端到端测?""

    def test_research_to_knowledge_flow(self):
        """测试从研究到知识的完整流?""
        # 1. 提交研究任务
        response = client.post("/api/v1/agent/research", json={
            "objective": "研究MACD因子"
        })
        task_id = response.json()["task_id"]

        # 2. 等待研究完成
        for _ in range(600):
            status = client.get(f"/api/v1/agent/research/{task_id}")
            if status.json()["status"] == "completed":
                break
            time.sleep(1)

        # 3. 验证知识已入?
        response = client.get("/api/v1/knowledge/query", params={
            "q": "MACD因子"
        })
        assert len(response.json()) > 0

        # 4. 验证Obsidian笔记已创?
        note_path = Path("/tmp/obsidian/MACD因子.md")
        assert note_path.exists()
```

### 11. 性能优化

### 11.1 批量操作

```python
class KnowledgeBase:
    """知识?- 批量优化"""

    def add_knowledge_batch(self, knowledge_list: list):
        """批量添加知识"""
        # 批量操作减少API调用
        self.collection.add(
            ids=[k.id for k in knowledge_list],
            documents=[k.content for k in knowledge_list],
            metadatas=[k.metadata for k in knowledge_list]
        )

    def query_batch(self, queries: list, n_results: int = 5):
        """批量查询"""
        results = []
        for query in queries:
            results.append(self.query(query, n_results))
        return results
```

### 11.2 缓存策略

```python
class KnowledgeCache:
    """知识缓存"""

    def __init__(self, kb: KnowledgeBase):
        self.kb = kb
        self.cache = {}  # LRU Cache

    def query_with_cache(self, query: str, ttl: int = 3600):
        """带缓存的查询"""
        cache_key = hash(query)

        if cache_key in self.cache:
            cached, timestamp = self.cache[cache_key]
            if time.time() - timestamp < ttl:
                return cached

        # 缓存未命中，查询数据?
        results = self.kb.query(query)
        self.cache[cache_key] = (results, time.time())
        return results
```


## 12. 更新记录

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| v1.0 | 2026-03-29 | 初始版本 |
| v1.1 | 2026-03-29 | 补充测试策略、性能优化 |


**维护?*: 清风量化系统
**索引**: `KNOWLEDGE.001`

---

## 变更记录

| 版本 | 日期 | 变更内容 | 变更人 |
|------|------|----------|--------|
| v1.0.0 | 2026-04-06 | 初始版本，补充职责描述和变更记录 | 首席文档架构师 |
