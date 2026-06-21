---
module_id: TPL-DEPGRAPH-001
title: "依赖图模板"
doc_type: template
status: Draft
version: "5.2.0"
layer: cross_layer
owner: ZephyrAlpha-Owner
classification: confidential
language: zh
created_by: human_plus_agent
date: "2026-05-13"
ttl: permanent
summary: "依赖图数据结构模板——19 大结构 + 10 组受控词表 + 计算规则 + 约束验证 + 蓝图双向链接 + 四层路径对齐 + AI优化阅读顺序"
completeness: "unknown"
tags: [template, dependency-graph, architecture]
rule_form: structural
scope: global
stability: evolving
verifiability: automated
depends_on:
  - PS-REG-007
  - PS-REG-012
references:
  - CycloneDX v1.7 (OWASP/ECMA-424)
  - C4 Model (Simon Brown)
  - Clean Architecture (Robert C. Martin)
  - DDD Context Mapping (Eric Evans)
  - system-dependency-map.md v3.0.0
  - business-domain-dependency-map-draft.md v4.3.0
  - system-dependency-map-场外讨论草稿.md v6
---

<!--
COMPLIANCE_CHECKLIST — 机器可解析合规清单
依赖图模板 MUST 包含以下所有标题（精确匹配关键词）。缺一 = 不合规。
脚本：python scripts/governance/d3_metadata/check_template_compliance.py <文档路径> --template dependency-graph
-->
<!--
REQUIRED_SECTIONS:
  overview: "概述"
  s1: "1. 目的与范围"
  s2: "2. 依赖图 YAML Schema"
  s3: "3. 受控词表"
  s4: "4. 计算规则与约束验证"
  s5: "5. 蓝图双向链接"
  s6: "6. 与现有资产映射"
  s7: "7. AI 自治权限"
  s8: "8. TTL 与生命周期"
  s9: "9. 四层路径对齐"
  s10: "10. 变更记录"
END_REQUIRED_SECTIONS
-->

# 依赖图模板

> module_id: TPL-DEPGRAPH-001 | version: 5.2.0 | status: draft | layer: cross_layer

---

## 概述

> ⚠️ **必填**。AI 阅读本文档的第一段——3~5 句话建立心理模型。
> 写清楚：本文档是什么、管什么范围、谁用、为什么存在。

{本文档定义 ZephyrAlpha 依赖图数据结构的标准格式——所有依赖图产出物（系统依赖图、业务域依赖图、治理域依赖图）必须符合此模板。核心功能：19 大数据结构定义 + 10 组受控词表 + 计算规则 + 约束验证 + 蓝图双向链接规范 + 四层路径对齐。使用对象：AI Agent 生成依赖图 / 人类 Owner 审计依赖关系。核心定位：依赖图是真源核对和对齐文档，不是施工指导。施工链路：依赖图 → 蓝图 → 任务卡 → 施工。}

---

## 1. 目的与范围

### 1.1 模板元数据

| 字段 | 值 |
|------|-----|
| 模板用途 | 定义依赖图数据结构的标准格式——所有依赖图产出物必须符合此模板 |
| 使用对象 | AI Agent / 人类 Owner |
| 适用场景 | 模块依赖图、子系统依赖图、治理域依赖图、跨模块依赖登记、业务域依赖图 |
| 对标 | CycloneDX v1.7 + C4 Model + Clean Architecture + DDD Context Mapping |
| 维护方式 | 手动维护模板，依赖图数据由脚本自动生成 |
| 核心定位 | 依赖图是真源核对和对齐文档，不是施工指导。施工链路：依赖图 → 蓝图 → 任务卡 → 施工 |

### 1.2 责任边界

| # | 类型 | 内容 | 说明 |
|---|:----:|------|------|
| 1 | ✅ 包含 | 19 大结构定义 | 元数据、节点、边、邻接表、图属性、完整性声明、约束规则、价值流、交叉点、依赖矩阵、事件流、因果链、激活序列、覆盖度、设计决策、蓝图链接、分片策略、多粒度聚合、路径映射规则 |
| 2 | ✅ 包含 | 10 组受控词表 | 节点类型、层级、依赖类型、完整性、依赖强度、安全边界、上下文映射、故障模式、生命周期、分片策略、许可证 |
| 3 | ✅ 包含 | 计算规则与约束验证 | 图属性计算规则 + 约束验证标准 |
| 4 | ✅ 包含 | 蓝图双向链接规范 | 依赖图与蓝图的双向对齐 |
| 5 | ❌ 排除 | 生成逻辑 | 本模板只定义数据结构格式，生成逻辑见各蓝图 |
| 6 | ❌ 排除 | 可视化渲染 | Mermaid/Graphviz 不在本模板范围内 |
| 7 | ❌ 排除 | SBOM（软件物料清单） | 见 CycloneDX 规范 |
| 8 | ❌ 排除 | AI 运行时信息 | 自愈路由/会话连续性/可观测性/Token 预算属于各模块蓝图 |

---

## 2. 依赖图 YAML Schema

```yaml
# ============================================================================
# 依赖图数据结构 — 完整模板 v4.0
# 对标: CycloneDX v1.7 / C4 Model / Clean Architecture / DDD Context Mapping
# 定位: 真源核对和对齐文档，非施工指导
# ============================================================================

# ---- §1 元数据 (Metadata) ------------------------------------------------
graph_id: "DEP-GRAPH-{domain}-{NNN}"
version: 1
scope: "system"                          # 枚举: system | subsystem | module | file | domain
generated_at: "2026-01-01T00:00:00+08:00"
generated_by: ""
source_hash: ""
ssot_hierarchy: ""                       # 选填。SSoT层级声明

# ---- §2 节点定义 (Nodes) --------------------------------------------------
nodes:
  - node_id: "{scope_prefix}:{module_id}:{path}"
    type: "module"                        # 枚举见 §3.1
    name: ""
    layer: "L1_foundation"                # 枚举见 §3.2
    stability: "stable"                   # 枚举: frozen | stable | evolving | volatile
    safety_level: "M"                     # 枚举: H | M | L
    version: ""
    purl: ""
    owner: ""
    tags: []
    code_path: ""
    blueprint_path: ""
    management: ""
    decision: ""
    lifecycle: "stable"                   # 枚举见 §3.9
    maturity: ""
    domain_id: ""
    value_stream: ""
    role_in_stream: ""
    security_boundary: ""                 # 枚举见 §3.6
    capacity_baseline:
      sli: ""
      slo: ""
      hardware: ""
      gpu: ""
    vulnerability_refs: []              # [{cve_id, severity, affected_versions, patch_status}]
    license: ""                         # 枚举见 §3.11

# ---- §3 边定义 (Edges) ----------------------------------------------------
edges:
  - edge_id: "E-001"
    from: ""
    to: ""
    dep_type: "import_depends"            # 枚举见 §3.3
    strength: "hard"                      # 枚举见 §3.4
    direction: "inward"                   # 枚举见 §3.5
    interface: ""
    protocol: "import"                    # 枚举: import | HTTP | gRPC | CLI | file_read | event | shared_kernel
    description: ""
    contract_ref: ""
    event_ref: ""
    context_mapping_pattern: ""           # 枚举见 §3.7
    failure_mode: ""                      # 枚举见 §3.8
    fallback: ""
    trigger_condition: ""
    data_flow: ""
    capacity_impact: ""
    cardinality: "1:N"                   # 枚举: 1:1 | 1:N | N:1 | N:M

# ---- §4 依赖邻接表 (Adjacency) --------------------------------------------
adjacency:
  forward: {}
  reverse: {}

# ---- §5 图属性 (Graph Properties) -----------------------------------------
properties:
  node_count: 0
  edge_count: 0
  is_dag: true
  cycles: []
  topological_order: []
  most_depended_upon: []
  orphan_nodes: []
  max_depth: 0
  layer_violations: 0
  amplification_factor: {}
  depth_heat_map: []
  blast_radius: {}                      # {node_id: transitive_closure_size}
  risk_propagation_paths: []            # [{from, to, path, risk_weight}]
  dead_dependency_count: 0

# ---- §6 完整性声明 (Compositions) -----------------------------------------
compositions:
  completeness: "unknown"                 # 枚举见 §3.3
  missing_scopes: []
  last_verified: ""
  coverage_dimensions: []

# ---- §7 约束规则 (Constraints) --------------------------------------------
constraints:
  acyclic: true
  max_chain_depth: 3
  layer_direction_rule: "inward_only"     # 枚举: inward_only | any
  forbidden_edges: []
  required_coverage: 0.95

# ---- §8 价值流 (Value Streams) --------------------------------------------
value_streams:
  - stream_id: "VS-001"
    name: ""
    goal: ""
    input: ""
    output: ""
    runtime_plane: ""
    nodes: []
    cross_points: []

# ---- §9 交叉点 (Intersection Points) --------------------------------------
intersection_points:
  - point_id: "X-001"
    name: ""
    source_stream: ""
    target_stream: ""
    trigger_condition: ""
    data_flow: ""
    capacity_impact: ""

# ---- §10 依赖矩阵 (Dependency Matrix) ------------------------------------
dependency_matrix:
  row_headers: []
  col_headers: []
  cells: []

# ---- §11 事件流 (Event Flow) ----------------------------------------------
event_flows:
  - event_id: "E-SG-01"
    name: ""
    source_domain: ""
    target_domain: ""
    frequency: ""
    contract_ref: ""

# ---- §12 因果链 (Causal Chains) -------------------------------------------
causal_chains:
  - chain_id: "CC-001"
    name: ""
    chain_type: ""
    event_sequence: []
    domains_involved: []

# ---- §13 激活序列 (Activation Sequence) -----------------------------------
activation_sequence:
  - node_id: ""
    readiness_prerequisites: []
    arb_ref: ""
    phase: ""

# ---- §14 覆盖度评估 (Coverage Assessment) ---------------------------------
coverage_assessment:
  - dimension: ""
    current_pct: 0
    target_pct: 100
    key_modules: []

# ---- §15 设计决策记录 (Design Decisions) -----------------------------------
design_decisions:
  - date: ""
    decision: ""
    rationale: ""
    status: "active"

# ---- §16 蓝图链接 (Blueprint Links) ---------------------------------------
# 依赖图与蓝图的双向链接。集中表格形式。
# 依赖图 → 蓝图：此依赖图产生了哪些蓝图
# 蓝图 → 依赖图：蓝图的 [BLUEPRINT] 字段反向引用依赖图

blueprint_links:
  - blueprint_id: ""                      # 必填。蓝图 module_id（如 MOD-INF-026）
    blueprint_path: ""                    # 必填。蓝图文件绝对路径
    blueprint_status: ""                  # 必填。蓝图状态: draft | active | deprecated
    source_section: ""                    # 选填。依赖图中哪个章节/子图产生了此蓝图
    alignment_verified: false             # 选填。双向对齐是否已验证
    last_aligned_at: ""                   # 选填。上次对齐验证时间 ISO 8601

# ---- §17 分片目录 (Document Index) -----------------------------------------
# 1500+ 模块下依赖图按功能域拆分为多个 MD 文件。本节描述分片目录。
# 拆分规则见 GOV-ENG-001 §2.5（code-construction-standards.md）
# 核心原则：能不拆就不拆。拆 = 多一个文件 = 漂移风险 +1。
# 警告阈值: 40K tokens | 强制拆分阈值: 60K tokens
document_index:
  strategy: "by_domain"                   # 枚举见 §3.10
  overview_file: ""                       # 总览索引文件路径（如 00-总览与索引.md）
  trigger_reason: ""                      # 拆分触发原因（如"单文件 > 60K tokens"）
  files:
    - file_path: ""                       # 子文件相对路径
      domain_id: ""                       # 对应域 ID（如 D-DATA）
      description: ""                     # 一句话
      token_estimate: 0                   # 选填，默认 0。供 AutoRuntime L1/L2/L3 调度
      node_count: 0                       # 该文件包含的节点数
      status: "active"                    # active | deprecated | draft

# ---- §18 多粒度聚合 (Hierarchical Aggregation) ----------------------------
# 支持缩放：域级 → 子系统级 → 模块级 → 文件级
hierarchy:
  parent_graph_id: ""                     # 上级依赖图 ID（空 = 顶层）
  sub_graph_ids: []                       # 下级依赖图 ID 列表
  aggregation_rules:
    - from_scope: "domain"                # 源粒度
      to_scope: "subsystem"               # 目标粒度
      method: "collapse"                  # 枚举: collapse | abstract | filter
      description: ""

# ---- §19 路径映射规则 (Path Mapping) ----------------------------------------
# 依赖图是路径映射的 SSoT。蓝图 §11 / 任务卡 / 代码物理路径必须符合此规则。
# 四层对齐链路：依赖图 §19 → 蓝图 §11 → 任务卡 downstream_outputs → 代码物理路径
# 路径树快照: docs/01_policies_and_standards/_registry/catalogs/project-path-tree.yaml
# 路径归属声明: docs/03_modules/path-ownership-map.yaml
path_mappings:
  - pattern: ""                           # 节点 ID 匹配模式（glob）
    code_root: ""                         # 代码根目录绝对路径
    blueprint_root: ""                    # 蓝图根目录绝对路径
    test_root: ""                         # 测试根目录绝对路径
    script_root: ""                       # 脚本根目录绝对路径（仅 scripts/ 类型）
    naming_rule: ""                       # 命名规则说明
    examples: []                          # 路径示例列表
```

---

## 3. 受控词表

### 3.1 节点类型 (node.type)

| type | 说明 | 示例 |
|------|------|------|
| `application` | 独立应用 | zephyr.runtime |
| `module` | 内部模块 | zephyr.asset_inventory |
| `package` | Python 包 | zephyr.core |
| `script` | 治理脚本 | scripts/governance/dependency_graph.py |
| `service` | 外部服务 | Ollama, DeepSeek API |
| `library` | 第三方库 | pydantic, networkx |
| `config` | 配置文件 | YAML 契约 |
| `data` | 数据资产 | dependency_graph.json |
| `gate` | 门禁检查 | EN-001 |
| `domain` | 业务域 | D-DATA, D-RISK |
| `aggregate` | DDD聚合 | AGG-007 MarketDataBatch |

### 3.2 层级 (node.layer)

| layer | 说明 | 依赖方向 |
|-------|------|---------|
| `L0_infrastructure` | 基础设施层 | 被所有层依赖 |
| `L1_foundation` | 基础服务层 | 依赖 L0 |
| `L2_domain` | 领域层 | 依赖 L0/L1 |
| `L3_application` | 应用层 | 依赖 L0/L1/L2 |
| `shared` | 跨层共享 | 可被任意层依赖 |
| `contracts` | 契约定义 | 可被任意层依赖 |
| `meta` | 元层 | 全局约束，不被依赖 |
| `domain_integration` | 域集成层 | 跨域协调 |

### 3.3 依赖类型 (edge.dep_type)

| dep_type | 说明 | 示例 |
|----------|------|------|
| `import_depends` | Python import 依赖 | `from zephyr.core import X` |
| `blueprint_depends` | 蓝图契约依赖 | blueprint §4 引用另一个蓝图 |
| `script_depends` | 脚本调用依赖 | 脚本 import 另一个脚本 |
| `data_depends` | 数据文件依赖 | 脚本读取 YAML 注册表 |
| `runtime_depends` | 运行时服务依赖 | 调用 Ollama API |
| `config_depends` | 配置引用依赖 | gate 引用 rule-registry |
| `test_depends` | 测试依赖 | test 引用被测模块 |
| `event_depends` | 事件驱动依赖 | D-SIGNAL 订阅 E-RS-01 |
| `contract_depends` | 契约消费依赖 | D-FACTOR 消费 CTR-001 |
| `shared_kernel` | 共享内核依赖 | D-EXECUTION + D-RISK 共享 Position |

### 3.4 完整性 (compositions.completeness)

| completeness | 说明 |
|-------------|------|
| `complete` | 所有依赖已完整记录 |
| `incomplete` | 已知有缺失 |
| `incomplete_first_party_only` | 仅内部依赖完整，第三方缺失 |
| `incomplete_third_party_only` | 仅第三方依赖完整，内部缺失 |
| `unknown` | 完整性未知（默认值，新图必须用此值直到验证） |

### 3.5 依赖强度 (edge.strength)

| strength | 说明 | 缺失后果 |
|----------|------|---------|
| `hard` | 强依赖 | 运行时崩溃 / 编译失败 |
| `soft` | 弱依赖 | 功能降级但仍可运行 |
| `optional` | 可选依赖 | 无影响，仅增强功能 |
| `event_driven` | 事件驱动 | 异步解耦，发布方不依赖消费方 |
| `conditional` | 条件依赖 | 仅特定条件下激活 |

### 3.6 安全边界 (node.security_boundary)

| boundary | 说明 |
|----------|------|
| `trusted_core` | 核心信任域——系统内部 |
| `controlled_edge` | 受控边界——API网关/认证层 |
| `external_service` | 外部服务——第三方API |
| `untrusted_input` | 不受信输入——用户输入/外部数据 |

### 3.7 上下文映射模式 (edge.context_mapping_pattern)

| pattern | 说明 | DDD 标准名 |
|---------|------|-----------|
| `upstream_downstream` | 上游发布，下游消费 | U/D |
| `customer_supplier` | 下游需求驱动上游 | C/S |
| `conformist` | 下游无条件遵从上游模型 | CF |
| `open_host_service` | 上游发布标准协议 | OHS |
| `published_language` | 上游发布标准语言 | PL |
| `anticorruption_layer` | 下游防腐层隔离 | ACL |
| `shared_kernel` | 双方共享子集 | SK |
| `separate_ways` | 无依赖，独立演进 | SW |

### 3.8 故障模式 (edge.failure_mode)

| failure_mode | 说明 | 典型 fallback |
|-------------|------|-------------|
| `service_down` | 被依赖服务不可用 | 重试 / 降级 / 熔断 |
| `timeout` | 调用超时 | 降级 / 缓存 / 异步重试 |
| `data_corruption` | 数据损坏 | 校验 / 回滚 / 人工介入 |
| `version_mismatch` | 接口版本不兼容 | 兼容层 / 降级 / 锁定版本 |
| `circuit_break` | 熔断触发 | 降级 / 排队 / 通知 |
| `cascade_failure` | 级联失效 | 舱壁隔离 / 限流 / 熔断 |

### 3.9 生命周期 (node.lifecycle)

| lifecycle | 说明 |
|----------|------|
| `stable` | 稳定运行 |
| `beta` | 测试中 |
| `T0-active` | Tier 0 已激活 |
| `T1-active` | Tier 1 已激活 |
| `T2-deferred` | Tier 2 延期 |
| `design_only` | 仅设计，未实现 |
| `not_started` | 未启动 |
| `deprecated` | 已废弃 |
| `end_of_life` | 终止维护 |

### 3.10 文档拆分策略 (document_index.strategy)

| strategy | 说明 | 适用场景 |
|----------|------|---------|
| `by_domain` | 按功能域拆分（推荐） | 域驱动设计系统——ZephyrAlpha 默认策略 |
| `by_layer` | 按架构层拆分 | 层级清晰的系统 |
| `by_depth` | 按依赖深度拆分 | 扁平依赖结构 |
| `by_critical_path` | 按关键路径拆分 | 高风险核心链路 |
| `custom` | 自定义拆分 | 混合策略——需在 trigger_reason 中说明 |

### 3.11 许可证类型 (node.license)

| license | 说明 |
|---------|------|
| `MIT` | MIT 许可证 |
| `Apache-2.0` | Apache 2.0 许可证 |
| `GPL-3.0` | GPL 3.0 许可证 |
| `BSD-3-Clause` | BSD 3 条款许可证 |
| `Proprietary` | 专有许可证 |
| `Internal` | 内部使用——不对外分发 |
| `Unknown` | 许可证未知（默认值，必须尽快确认） |

---

## 4. 计算规则与约束验证

> "属性"=图属性的计算方法，"约束"=属性值的验证标准。计算和验证天然配对——算完就验。

### 4.1 邻接表构建

```
forward[A] = [B, C]  →  A 依赖 B 和 C
reverse[B] = [A]      →  B 被 A 依赖
reverse[C] = [A]      →  C 被 A 依赖
```

### 4.2 图属性计算与约束验证

| # | 项目 | 类型 | 算法/验证方法 | 说明/不通过处置 |
|---|------|:----:|-------------|---------------|
| 1 | `is_dag` | 属性 | Kahn 拓扑排序 | 排序成功 = DAG |
| 2 | `cycles` | 属性 | DFS 回溯 | 返回所有环路径 |
| 3 | `topological_order` | 属性 | Kahn 算法 | 仅 is_dag=true 时有效 |
| 4 | `most_depended_upon` | 属性 | 入度排序 | 入度 Top-10 |
| 5 | `orphan_nodes` | 属性 | 入度=0 且 出度=0 | 对标 RULE-TWO 反孤儿 |
| 6 | `max_depth` | 属性 | 最长路径 DFS | 对标 audit_depends_on_chain_depth |
| 7 | `layer_violations` | 属性 | direction=outward 计数 | 对标 Clean Architecture |
| 8 | `amplification_factor` | 属性 | 传递依赖计数 / 直接依赖计数 | 放大倍数 > 10× 为高风险 |
| 9 | `depth_heat_map` | 属性 | 每节点最长链 DFS + 风险评级 | 🟩≤2 / 🟧=3 / 🔴≥4 |
| 10 | `blast_radius` | 属性 | 每节点传递闭包大小 BFS | 闭包 > 20 = 高风险，修改此节点影响范围大 |
| 11 | `risk_propagation_paths` | 属性 | BFS + 风险权重累积 | safety_level=H 的节点传播路径必须标记 |
| 12 | `dead_dependency_count` | 属性 | 声明但无运行时引用的边计数 | > 0 = 存在死依赖，需清理 |
| 13 | `acyclic` | 约束 | Kahn 拓扑排序 | 环必须拆解 |
| 14 | `max_chain_depth` | 约束 | 最长路径 DFS | 链超深必须重构 |
| 15 | `layer_direction_rule` | 约束 | 边 direction 字段 | outward 边必须消除或标记例外 |
| 16 | `forbidden_edges` | 约束 | 模式匹配 | 禁止模式必须移除 |
| 17 | `required_coverage` | 约束 | node_count / 总模块数 | 不足必须补充节点 |
| 18 | `amplification_threshold` | 约束 | amplification_factor > 10× | 高放大节点必须拆分或扁平化 |
| 19 | `blueprint_alignment` | 约束 | §16 blueprint_links 双向验证 | 蓝图缺失或未对齐必须补充 |
| 20 | `blast_radius_threshold` | 约束 | blast_radius > 20 | 高影响节点必须拆分或标记为 human_gated |
| 21 | `path_mapping_compliance` | 约束 | 节点 code_path ∈ §19 path_mappings 匹配结果 | 不符合映射规则 = 路径漂移，必须修正 |
| 22 | `license_compliance` | 约束 | 第三方库 license ≠ Unknown | Unknown 许可证必须确认后更新 |
| 23 | `vulnerability_tracking` | 约束 | vulnerability_refs 中 severity=Critical/High 的必须有 patch_status | 未修补的高危漏洞必须标记 |

---

## 5. 蓝图双向链接规范

### 5.1 设计原则

依赖图是真源核对文档，蓝图是施工指导文档。两者必须双向对齐：

```
依赖图 §16 blueprint_links  ──→  蓝图 [BLUEPRINT] 字段
蓝图 §4 文件清单             ──→  依赖图节点
```

### 5.2 链接方式

采用**集中表格**（§16 blueprint_links），理由：

| 方案 | 优点 | 缺点 |
|------|------|------|
| 集中表格 | 一目了然所有蓝图、便于验证对齐、便于扫描 | 需要维护 source_section 字段关联子图 |
| 内联（每个子图下面加） | 上下文紧密 | 分散难找、不便全量验证、容易遗漏 |

### 5.3 双向验证规则

| 验证方向 | 规则 | 不通过处置 |
|---------|------|-----------|
| 依赖图 → 蓝图 | §16 每个 blueprint_path 必须存在且包含 `[BLUEPRINT]` 字段 | 蓝图缺失或格式不对 → 必须补充 |
| 蓝图 → 依赖图 | 蓝图 `[BLUEPRINT]` 字段引用的依赖图必须存在且包含对应节点 | 依赖图缺失节点 → 必须补充 |
| 对齐验证 | 蓝图 §4 文件清单 ↔ 依赖图节点 code_path 双向匹配 | 不匹配 → 漂移，必须修正 |

---

## 6. 与现有资产映射

| 现有资产 | 对应模板结构 | 差距 |
|---------|-------------|------|
| `dependency.py` Pydantic 模型 | §2 Nodes + §3 Edges + §5 Properties | 缺 direction/strength/compositions/constraints 及 §8-§16 |
| `cross-module-dependency-registry.yaml` (PS-REG-007) | §4 Adjacency + §10 Dependency Matrix | 缺 §5-§16 |
| `system-dependency-map.md` | §8 Value Streams + §9 Intersection Points + §5 Depth Heat Map | 纯文档，不可计算 |
| `business-domain-dependency-map-draft.md` | §10 Matrix + §11 Event Flows + §12 Causal Chains + §13 Activation | 纯文档，不可计算 |
| `EN-001` 门禁 | §7 Constraints.acyclic | 只检测环，不检测方向/深度/覆盖率/放大/蓝图对齐 |
| 蓝图-代码双向对齐 | §16 blueprint_links | 当前无结构化链接 |

---

## 7. AI 自治权限标注

| 操作 | AI 自治权限 | 说明 |
|------|:---:|------|
| 使用模板创建依赖图 | ai_modifiable | AI 可按模板格式生成依赖图数据 |
| 修改受控词表 | human_gated | 词表变更影响所有依赖图 |
| 修改约束规则 | human_gated | 约束变更影响门禁验证 |
| 修改 schema 结构 | human_gated | Schema 变更影响所有消费者 |
| 更新蓝图链接 | ai_modifiable | AI 可更新 blueprint_links 的对齐验证状态 |

---

## 8. TTL 与生命周期

| 字段 | 值 |
|------|-----|
| TTL | permanent |
| 审查周期 | 每 90 天 |
| 过期处理 | 如被新标准取代，按废弃流程标记 deprecated |
| 最后审查日期 | 2026-05-12 |

---

## 9. 四层路径对齐规范

### 9.1 对齐链路

```
依赖图 §19 path_mappings (规则SSoT)
  ↓ 规则验证
依赖图节点 code_path ←→ 蓝图 §11 产出物路径 ←→ 代码 [BLUEPRINT] 头部 ←→ 代码物理路径
                                              ↕
                                         任务卡 downstream_outputs
```

### 9.2 对齐验证与漂移处置

| 层级 | 漂移类型 | 验证规则 | 处置 | 审批 |
|------|---------|---------|------|------|
| L1 依赖图→规则 | 路径漂移 | 节点 code_path → §19 path_mappings，必须匹配某条规则 | 移动代码到正确位置 或 更新 §19 规则 | 更新规则需 Owner 批准 |
| L2 依赖图→蓝图 | 蓝图漂移 | 节点 code_path ↔ 蓝图 §11 路径，必须一致 | 同步蓝图 §11 或 依赖图节点 | AI 可自主同步 |
| L3 蓝图→任务卡 | 任务卡漂移 | 蓝图 §11 路径 → 任务卡 downstream_outputs，必须一致 | 更新任务卡 downstream_outputs | AI 可自主更新 |
| L4 蓝图→代码 | 代码漂移 | 蓝图 §0 文件清单 ↔ 代码 [BLUEPRINT] 头部，必须双向匹配 | 更新代码 [BLUEPRINT] 头部 | AI 可自主更新 |
| L5 代码→物理路径 | 物理漂移 | [BLUEPRINT] 头部 ↔ 实际文件位置，必须一致 | 移动文件到声明位置 | 需确认移动不影响其他引用 |

### 9.3 自动对齐验证命令

| 验证范围 | 命令 |
|---------|------|
| 全链路验证 | `python scripts/governance/d5_architecture/validators/validate_path_alignment.py --all` |
| 单蓝图验证 | `python scripts/governance/d5_architecture/validators/validate_path_alignment.py --blueprint <module_id>` |
| 单节点验证 | `python scripts/governance/d5_architecture/validators/validate_path_alignment.py --node <node_id>` |
| 仅路径映射合规 | `python scripts/governance/d5_architecture/validators/validate_path_alignment.py --mapping-only` |

---

## 10. 变更记录

| 日期 | 版本 | 变更内容 |
|------|------|---------|
| 2026-05-15 | 5.2.0 | 表格合并：§1.2责任范围+§1.3责任边界→§1.2责任边界（类型列✅/❌）；§4.1图属性计算+§5约束验证→§4计算规则与约束验证（类型列属性/约束）；§10.2四层对齐验证+§11.4漂移处置→§9.2对齐验证与漂移处置（5列合并表）。章节重编号：§6→§5, §7→§6, §8→§7, §9→§8, §10→§9, §11→§10 |
| 2026-05-13 | 5.1.0 | AI阅读优化：新增概述段（## 概述）；章节编号修正（四层路径对齐 §11→§10，变更记录 §10→§11）；新增 REQUIRED_SECTIONS overview 项 |
| 2026-05-13 | 5.0.0 | 新增 §17 分片策略（1000+ 模块 LLM 上下文窗口适配）。新增 §18 多粒度聚合（域级→子系统→模块→文件缩放）。新增 §19 路径映射规则（四层路径对齐 SSoT）。新增 §10 四层路径对齐规范。新增节点字段 vulnerability_refs/license。新增边字段 cardinality。新增 §5 图属性 blast_radius/risk_propagation_paths/dead_dependency_count。新增 §5 约束 blast_radius_threshold/path_mapping_compliance/license_compliance/vulnerability_tracking。新增受控词表 §3.10 分片策略、§3.11 许可证类型。§3.9 生命周期新增 deprecated/end_of_life。结构数 16→19，受控词表 9→10 |
| 2026-05-12 | 4.0.0 | 定位修正：依赖图是真源核对和对齐文档，不是施工指导。移除 §16-§19（AI Agent 依赖、自愈路由、会话连续性、AI 可观测性）——这些属于蓝图范畴。移除节点 AI 字段（ai_autonomy/hallucination_risk/prompt_deps/context_requirements/model_requirement/skill_ids/gate_ids/degradation_level/self_healing_capable）。移除边 AI 字段（ai_verifiable/confidence/self_healing_path/degradation_path/session_boundary/escalation_level）。移除 AI 原生图属性和约束。移除受控词表 §3.11-§3.14。移除节点类型 prompt/skill/context_bundle/bridge。移除依赖类型 prompt/context/skill/gate/bridge_depends。移除故障模式 hallucination/context_overflow。新增 §16 蓝图链接（集中表格 + 双向验证规范）。新增约束 blueprint_alignment。结构数 19→16，受控词表 13→9 |
| 2026-05-12 | 3.0.0 | AI 原生扩展（后因定位修正回退） |
| 2026-05-12 | 2.0.0 | 从 3 个依赖图文档提取 8 个新结构（§8-§15） |
| 2026-05-12 | 1.0.0 | 初始版本——7 大结构 + 6 组受控词表 |
