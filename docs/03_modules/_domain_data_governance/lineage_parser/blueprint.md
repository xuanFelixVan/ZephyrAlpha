---
blueprint_id: MOD-DATA_GOV-004
module_name: lineage_parser
domain: D_DATA_GOV
doc_type: blueprint
ttl: permanent
design_maturity: design
stability: evolving
safety_level: L
ai_autonomy: ai_modifiable
version: "0.1.0"
created: 2026-08-25
last_updated: 2026-08-25
owner: ZephyrAlpha-Owner
priority: P1
blueprint_level: module
domain_id: D_DATA_GOV
path: src/zephyr/data_governance/core/lineage_parser.py
granularity: file
---

# MOD-DATA_GOV-004 lineage_parser 蓝图（M8-S01 血缘解析器）

> **module_id**: MOD-DATA_GOV-004 | **域**: D_DATA_GOV | **优先级**: P1
> **来源**: B10-02313（AUD-DRAFT-001-DIGEST P1 波 W-P1-17，CAND-DATGOV-001，A1 交易决策架构 §30.4.3）
> 代码：`src/zephyr/data_governance/core/lineage_parser.py`

## 0. 定位

M8-S01 血缘解析器——从契约定义与模块头注解**自动解析提取数据流转关系**，
产出 source→transformation→target 边入 lineage_tracker。TSV 现状注记：血缘边
注册/上下游查询底座（MOD-DATA_GOV-002）在，自动解析提取缺口未补。

查重分工（W-P1-17 探查结论，均不复制）：

| 既有件 | module_id | 职责 | 与本模块边界 |
|---|---|---|---|
| lineage_tracker | MOD-DATA_GOV-002 | 血缘边注册/上下游查询/环检测/幂等 | 本模块只做**解析与抽取**，幂等与环检测复用其实现不重造 |
| auto_backfiller | MOD-DAT-AUTO-BACKFILLER | 回填报告 lineage_sink 回调字段 | 血缘**字段**通道已建，契约/注解**解析**缺口归本模块 |
| schema_registry / metadata_registry | MOD-DATA_GOV-001/003 | 模式/元数据注册 | 不管流转边抽取 |

不做什么：不重造图算法（add_edge/环检测/上下游查询复用 MOD-DATA_GOV-002）、
不改 CTR 契约真源（cross_layer_contracts.yaml 只读解析）、不扫描全仓代码
（M8-S02 静态分析器职责，本模块只解析给定文本/结构）。

## 1. 解析规则（确定性，纯函数）

- **CTR 契约解析**：`parse_ctr_contract(contract: Mapping)` → 边集：
  source_domain →CTR-id（transformation="produces"）+ CTR-id →各 target_domains
  （transformation="consumed_by"）；缺 id/source_domain Fail-Closed。
- **模块头注解解析**：`parse_module_header(text)` → `# [MODULE]` 当前模块路径、
  `# [DEPENDENCIES]`（`;` 分隔，仅 zephyr.* 内部件成边，外部库略过记 skipped）
  → 边 dep→module（transformation="imports"）；`# [CONSUMERS]` 括号内模块名/
  MOD-id 令牌 → 边 module→consumer（transformation="consumed_by"）。
- **入图**：`ingest_into_tracker(edges, tracker)` → LineageParseReport：
  批内 (source,target) 去重（首条胜出）；tracker 幂等重加计 updated；
  环 ValueError 捕获记 rejected（不中断批）；added/updated/rejected/skipped 计数。
- 自环与非法节点名（空/空白）Fail-Closed（LineageParseError）。

## 2. 接口

```python
@dataclass(frozen=True)
class ModuleHeaderAnnotations: module / dependencies / consumers / skipped_external
@dataclass(frozen=True)
class LineageParseReport: edges / added / updated / rejected / skipped / sources
parse_ctr_contract(contract: Mapping) -> list[LineageEdge]
parse_module_header(text: str) -> ModuleHeaderAnnotations (+ edges_of(annotations))
ingest_into_tracker(edges, tracker) -> LineageParseReport
class LineageParseError(ValueError)
```

## 3. 依赖前置

- MOD-DATA_GOV-002 lineage_tracker（LineageEdge/add_edge/环检测/幂等唯一真源）。

## 4. 验收标准

- 单测全绿（CTR 双向边抽取/模块头三注解解析/外部依赖略过/批内去重/幂等重加
  /环拒记不中断/畸形输入 Fail-Closed）；相关域集成零回归。
