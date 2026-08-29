---
blueprint_id: MOD-FACTORY-002
module_name: module_mapper
domain: D_AUTONOMY_CORE
doc_type: blueprint
ttl: permanent
design_maturity: testing
stability: evolving
safety_level: M
ai_autonomy: human_gated
version: "0.1.0"
created: 2026-08-29
last_updated: 2026-08-29
owner: ZephyrAlpha-Owner
priority: P1
blueprint_level: module
domain_id: D_AUTONOMY_CORE
path: src/zephyr/autonomy_core/module_factory/module_mapper.py
granularity: file
---

# MOD-FACTORY-002 module_mapper 蓝图（知识→模块映射引擎）

> **module_id**: MOD-FACTORY-002 | **域**: D_AUTONOMY_CORE | **优先级**: P1
> **设计真源**: 13号文 `docs/02_enterprise_architecture/09_ai_architecture/implementation_plans/13_module_factory.md` §3.3（知识→模块映射设计，核心独创环节）+ §3.6（入库设计·输出侧）
> **裁定**: #ARCH-286（归域 D_AUTONOMY_CORE；编号 MOD-FACTORY-002）
> 代码：`src/zephyr/autonomy_core/module_factory/module_mapper.py`

## 0. 定位

模块工厂六环节之"知识→模块映射"（13号文 §3.0 处理 2，核心独创）。与外部系统
"想法→直接生成代码"不同：知识经 schema_plan 语义抽象后，先用既有库做检索，
**重复/变体在写代码前就被裁决**（省 GPU、省人审、防库膨胀）。产出 ModuleSpec
100% 为建议草稿（human_gated，B-007 成熟度 testing 封顶），注册表 YAML 一律只读。

查重分工：知识分类归 MOD-FACTORY-001；代码生成归 Phase 2 module_generator；
技能复用检索归 11号文技能库既有设施（不建新索引）；embedding 归
MOD-INF-042 EmbeddingRouter（经 EmbedderProtocol 注入复用，不自建向量设施）。

## 1. 三段映射

`map_knowledge(KnowledgeItem, ClassificationResult, *, schema_plan=None) -> ModuleSpec`：

1. **语义抽象**：schema_plan={event, context, qualities, direction, output}
   （62号文 v1.19.0 预留字段，对标 AlphaSchema）。调用方可直供；缺省经 LLM
   网关生成（严格 JSON 校验：恰好五键、非空字符串；失败 -> verdict="error"
   fail-closed）。
2. **双通道检索**：embedding 通道（注入兼容 `embed(text, collection_name)` 的
   对象，如 EmbeddingRouter）+ SQLite FTS5 通道（进程内 :memory: 索引，
   CJK 单字+双字 tokenize，bm25 归一化）。embedding 缺失/异常 -> 降级
   FTS5-only，ModuleSpec.degraded=True + degradation_reason 显式标注。
   检索范围=factor_registry.yaml + strategy_registry.yaml（catalogs 只读加载，
   含已退役条目=失效墓园，命中即告警防重新发明已失效因子）。
3. **四选一裁决**（阈值全配置化 MapperThresholds）：
   - top.score ≥ duplicate(0.90) -> reject_duplicate
   - variant(0.70) ≤ top.score < duplicate -> variant_of（parent=top）
   - top < variant 且 ≥min_components(2) 条 ≥ combination(0.45) -> combination
   - 其余 -> new_entry
   组合对应 62号文 combination_strategy 字段，避免"旧因子新组合"误判新建。

## 2. 接口

```python
DEFAULT_CATALOGS_DIR  # catalogs 落盘目录（REPO_ROOT 派生，只读）
DEFAULT_VERIFICATION_PLAN  # L1~L4 验证计划（L4=62号文 G8 人审不可降级）
class ModuleMapperError(Exception)
class EmbedderProtocol(Protocol): .embed(text, collection_name)
@dataclass(frozen=True) MapperThresholds: duplicate=0.90/variant=0.70/
    combination=0.45/combination_min_components=2/embedding_weight=0.6/
    fts_weight=0.4/max_candidates=5
@dataclass(frozen=True) RegistryEntryDoc: entry_id/registry/name/status/retired/text
@dataclass(frozen=True) MatchCandidate: +score/fts_score/embedding_score
@dataclass(frozen=True) ModuleSpec: verdict/target_registry/schema_plan/entry_draft/
    code_skeleton/verification_plan/candidates/draft_notes/rationale/
    retrieval_channel/degraded/degradation_reason；human_gate_required 恒 True
load_registry_entries(catalogs_dir=None) -> tuple[RegistryEntryDoc, ...]  # 只读
class ModuleMapper(llm=None, embedder=None, catalogs_dir=None, entries=None,
                   thresholds=..., fts_connection=None, max_tokens=1024,
                   temperature=0.1):
    .map_knowledge(item, classification, *, schema_plan=None) -> ModuleSpec
```

## 3. 不变量

- verdict ∈ {new_entry, variant_of, reject_duplicate, combination, routed, error}，
  无隐式第五态；routed=其他分流（13号文 §3.2 主分类 3，不经 factor/strategy 检索）。
- classification.verdict!="classified" 强行映射 -> ModuleMapperError
  （REJECT 知识不进映射，13号文 §3.1 门禁串联）。
- reject_duplicate 不产 entry_draft；variant_of 的 entry_draft.variant_of=parent。
- entry_draft 只含 registry schema 字段：status=candidate +
  algorithm_status=pending_backtest + evidence="" + discovery_agent=module_factory
  （#ARCH-286 Q5 批准扩展枚举）；人审待办进 draft_notes，不污染 schema。
- 裁决理由 rationale 全留痕（阈值/候选分数/墓园告警/降级原因，人审可读）。
- 注册表 YAML 只读（load_registry_entries 只读加载；本模块无写路径）。

## 4. 依赖

- MOD-FACTORY-001 knowledge_classifier（ClassificationResult/KnowledgeItem 类型）
- MOD-INF-051 llm_runtime_gateway（**只消费既有 `infer` 签名**；schema_plan 生成）
- MOD-INF-042 EmbeddingRouter（经 EmbedderProtocol 注入复用；可缺省降级）
- catalogs/factor_registry.yaml + strategy_registry.yaml（**只读**，检索语料真源）
- pyyaml（YAML 加载）+ sqlite3 FTS5（进程内检索索引，C6 单机轻量）

## 5. MVP 边界（Phase 1）

- 验收：对既有库自检重复检出有效、不误杀变体（13号文 §4.2 P1-S3）。
- 不做：知识图谱/向量数据库集群（C6）；语义去重的 LLM 经济逻辑等价判定
  （13号文 §3.2 第 3 条，Phase 2 候选）；surrogate 收益模型（Phase 3 登记）；
  自动入库/自动晋升（62号文 PROMOTE_ENTRY 职责，本模块止步于建议草稿）。
