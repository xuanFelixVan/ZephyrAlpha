---
module_id: KNOWLEDGE_MANAGEMENT
version: 1.0.0
status: Active
created_date: 2026-04-13
last_updated: 2026-04-13
owner: 首席文档架构师
layer: layer_00
responsibility: duplicates
> **核心职责**: 知识管理体系和方法论，涉及知识管理蓝图
> **索引**: `KNOWLEDGE.001`
> **开发时?*: 25h
> **优先?*: P1
> **核心定位**: AI自动提取和更新研究知识，实现"AI研究 ?自动入库 ?可查询复?
|responsibility:
  - 管理知识库
**选择**: Chroma (个人使用足够简?
索引: API_KNOWLEDGE_001
上游: wandb, ResearchPipeline
下游: ResearchAgent
def __init__(self, persist_dir: "str = "./data/knowledge"):"
metadata={"description": "量化研究知识?}
content: str,
metadata: dict
category: str,
'category': r['metadata']['category'],
def query(self, query: "str, n_results: int = 5) -> list:"
query: 查询文本
n_results: 返回数量
def add_factor_knowledge(self, factor_data: "dict):"
factor_data: 因子数据
'name': 'momentum_20',
'definition': '20日动量因?,
'ic_mean': 0.045,
'ic_ir': 1.2,
'best_params': "{'period': 20},"
'notes': '适用于趋势市?
因子名称: {factor_data['name']}
因子定义: {factor_data['definition']}
IC_IR: {factor_data.get('ic_ir', 'N/A')}
使用注意: {factor_data.get('notes', '')}
'source': r['metadata']['source'],
'id': strategy_data['id'],
'created_at': datetime.now().isoformat()
def add_strategy_knowledge(self, strategy_data: "dict):"
策略名称: {strategy_data['name']}
策略类型: {strategy_data.get('type', 'N/A')}
核心逻辑: {strategy_data.get('logic', 'N/A')}
夏普比率: {strategy_data.get('sharpe', 'N/A')}
适用场景: {strategy_data.get('scenario', 'N/A')}
def extract_from_wandb(self, run_id: "str) -> dict:"
run_id: wandb run ID
实验名称: {run.name}
实验配置: {run.config}
实验指标: {run.summaryMetrics}
def extract_from_report(self, report_text: "str) -> dict:"
def on_experiment_complete(self, experiment_id: "str):"
Tool: query_knowledge_base
def query_for_research(self, objective: "str) -> list:"
objective: 研究目标
'content': r['document'],
'relevance': r.get('distance', 1.0)
def get_related_factors(self, factor_name: "str) -> list:"
factor_name: 因子名称
def get_strategy_lessons(self, strategy_type: "str) -> list:"
strategy_type: 策略类型
def __init__(self, vault_path: "str):"
def update_factor_note(self, factor_data: "dict):"
type: factor
created: {datetime.now().isoformat()}
tags: [{', '.join(factor_data.get('tags', []))}]
参数:
  - 实验ID: {factor_data.get('experiment_id', 'N/A')}
  - wandb: {factor_data.get('wandb_url', 'N/A')}
q: 查询文本
metadata={"factor_name": "MACD"}
'documents': [["动量因子"]],
'metadatas': "[[{"category": "factor"}]],"
'distances': [[0.2]]
filter={"category": "factor"}
'factor_name': 'momentum_20',
'decay_5d': 0.85,
'experiment_id': 'exp_001',
'strategy_name': 'trend_following',
'annual_return': 0.15,
'sharpe_ratio': 1.8,
'max_drawdown': 0.12
'reason': '过拟?,
'ic_train': 0.08,
'ic_test': 0.02
'type': 'factor_research',
'status': completed
metadata={"source": "experiment"}
"objective": 研究MACD因子
"q": MACD因子
def add_knowledge_batch(self, knowledge_list: "list):"
def query_batch(self, queries: "list, n_results: int = 5):"
def __init__(self, kb: "KnowledgeBase):"
def query_with_cache(self, query: "str, ttl: int = 3600):"
**维护?*: 清风量化系统
**索引**: `KNOWLEDGE.001`
---
## 变更记录



| 版本 | 日期 | 变更内容 | 变更人 |

|------|------|----------|--------|

| v1.0.0 | 2026-04-06 | 初始版本，补充职责描述和变更记录 | 首席文档架构师 |

```

