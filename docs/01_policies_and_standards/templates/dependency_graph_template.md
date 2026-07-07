---
module_id: GOV-029
title: "依赖图统一模板"
doc_type: template
status: Active
version: "6.0.0"
layer: cross_layer
owner: ZephyrAlpha-Owner
classification: confidential
language: zh
created_by: human_plus_agent
date: "2026-06-06"
ttl: permanent
summary: "依赖图统一格式模板——第一性原理定义。节点20核心字段+按类型差异字段。边16字段。21种节点类型（15文件级+6域级）。12种边类型。23顶层段（含§0硬边界8条+§5功能域注册表）。design_maturity+deployment_lifecycle+drive_direction三维度。can_build+hard_boundary硬边界。字段命名零歧义。100%AI开发防幻觉防漂移。"
completeness: "complete"
tags: [template, dependency-graph, architecture, unified-format]
rule_form: structural
scope: global
stability: stable
verifiability: automated
depends_on:
  - {target: PS-REG-007, at: "$TODO", why: "TODO -- auto-converted"}
  - {target: PS-REG-012, at: "$TODO", why: "TODO -- auto-converted"}
  - {target: REG-FUNC-DOMAIN-001, at: "$TODO", why: "TODO -- auto-converted"}
references:
  - CycloneDX v1.7 (OWASP/ECMA-424)
  - C4 Model (Simon Brown)
  - Clean Architecture (Robert C. Martin)
  - DDD Context Mapping (Eric Evans)
  - generate_project_depgraph.py
  - diagnose_depgraph.py
---

<!--
COMPLIANCE_CHECKLIST — 机器可解析合规清单
依赖图模板 MUST 包含以下所有标题（精确匹配关键词）。缺一 = 不合规。
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
  s11: "11. AI Agent 自检协议"
END_REQUIRED_SECTIONS
-->

# 依赖图统一模板

> module_id: TPL-DEPGRAPH-001 | version: 6.0.0 | status: active | layer: cross_layer

---

## 概述

本文档定义依赖图的唯一数据格式。**模板定义好的标准**——AI防幻觉防漂移需要什么字段，模板就定义什么字段。字段命名零歧义——全新AI第一眼即精确理解。

**核心理念**：100% AI 开发，每次 AI 进项目都是全新状态。字段 = AI 不产生幻觉/漂移的必要信息。缺字段 = AI 猜 = 幻觉。字段名歧义 = AI 误解 = 幻觉。

| 事实 | 值 |
|------|-----|
| 顶层段 | 23段（含 §0 硬边界 + §5 功能域注册表） |
| 硬边界 | 8条（hardware×3 + capital×1 + external_interface×2 + regulation×2） |
| 节点类型 | 21种（15文件级 + 6域级） |
| 边类型 | 12种（4必须 + 6应该有 + 2可选） |
| 节点字段 | 20核心字段（全类型统一）+ 按类型差异字段 |
| 边字段 | 5必填 + 11应该有 = 16字段 |
| 生成器 | `generate_project_depgraph.py`（唯一产出入口） |
| 产出物 | `depgraph (PostgreSQL)` |
| 设计态/运营态 | `design_maturity`（设计成熟度）+ `deployment_lifecycle`（部署生命周期）+ `drive_direction`（驱动方向）三维度区分 |

---

## 1. 目的与范围

### 1.1 模板元数据

| 字段 | 值 |
|------|-----|
| 模板用途 | 定义依赖图数据结构的唯一标准格式——AI防幻觉防漂移的最高标准 |
| 使用对象 | AI Agent（100% AI 开发，每次全新状态）/ 人类 Owner / 依赖分析器 / 漂移检测器 |
| 适用场景 | 全项目文件级依赖图（自动生成）+ 域级依赖图（设计态） |
| 核心定位 | 依赖图是**全项目唯一依赖真源**。AI 施工读此文件定位一切依赖关系 |
| 产出物 | `depgraph (PostgreSQL)` |
| 对标 | CycloneDX v1.7 + C4 Model + Clean Architecture + DDD Context Mapping |

### 1.2 责任边界

| # | 类型 | 内容 | 说明 |
|---|:----:|------|------|
| 1 | ✅ 包含 | 21 种节点类型 | 15文件级 + 6域级 |
| 2 | ✅ 包含 | 12 种边类型 | 4必须 + 6应该有 + 2可选 |
| 3 | ✅ 包含 | 节点20核心字段 + 按类型差异字段 | 全类型统一基础 + 类型特有字段 |
| 4 | ✅ 包含 | 边16字段 | 5必填 + 11应该有 |
| 5 | ✅ 包含 | 设计态/运营态区分 | design_maturity + deployment_lifecycle + drive_direction 三维度 |
| 6 | ✅ 包含 | 图指标 + 架构约束 | 含依赖放大/爆炸半径/风险传播 |
| 7 | ✅ 包含 | 完整性声明 | completeness_declaration 段 |
| 8 | ✅ 包含 | 业务域依赖分析 | 业务流/事件流/因果链/交叉点/启动序列/依赖覆盖/设计决策 |
| 9 | ✅ 包含 | 蓝图→文件映射 | blueprint_file_map 段 |
| 10 | ✅ 包含 | 路径映射规则 | path_mappings 段 |
| 11 | ❌ 排除 | 生成逻辑 | 本模板只定义数据结构格式 |
| 12 | ❌ 排除 | 可视化渲染 | Mermaid/Graphviz 由生成器单独产出 |

---

## 2. 依赖图 YAML Schema

```yaml
# ============================================================================
# 依赖图数据结构 — 统一格式 v6.0.0
# 核心原则：模板定义好的标准。字段 = AI防幻觉防漂移的必要信息。
# 命名原则：零歧义。全新AI第一眼即精确理解。
# 生成器: generate_project_depgraph.py（唯一产出入口）
# 产出物: depgraph (PostgreSQL)
# ============================================================================

# ---- §0 硬边界 (Hard Boundaries) ------------------------------------------
# AI 冷启动第一眼必须看到。违反任何一条 = 系统设计前提被打破。
# 硬边界 = 想改也改不了的客观限制。设计选择不在此列。
# 来源: 能力定位书 §2 精简版
hard_boundaries:
  - id: "HB-HW-01"
    category: "hardware"
    constraint: "单台PC工作站，无集群/K8s"
    parameters: "CPU i7-12700KF(12核20线程); GPU RTX 3090 24GB; RAM 64GB DDR4; 存储 D:731GB+E:931GB SSD"
    impact: "所有并发/分布式/集群方案不可用"

  - id: "HB-HW-02"
    category: "hardware"
    constraint: "GPU显存硬上限"
    parameters: "<90%=21.6GB可用; 盘中~8-10GB(33%-42%), 盘前~10GB(42%)"
    impact: "模型推理显存超限=OOM崩溃; 多模型并发必须做显存预算"

  - id: "HB-NET-01"
    category: "hardware"
    constraint: "网络带宽上限"
    parameters: "30Mbps"
    impact: "大批量数据拉取/多源并发请求必须限速"

  - id: "HB-FUND-01"
    category: "capital"
    constraint: "初始AUM"
    parameters: "50万"
    impact: "策略容量/仓位/做T底仓均受此约束; 融券受限"

  - id: "HB-IFIND-01"
    category: "external_interface"
    constraint: "iFind数据源QPS限制"
    parameters: "QPS=20（账号总上限）"
    impact: "批量数据拉取必须分页限速; 并发请求不可超20"

  - id: "HB-QMT-01"
    category: "external_interface"
    constraint: "miniQMT交易接口限制"
    parameters: "下单10笔/秒; Tick=3秒; 模拟盘延迟~1分钟"
    impact: "高频策略不可用; 信号触发到下单存在3秒Tick延迟"

  - id: "HB-TRADE-01"
    category: "regulation"
    constraint: "T+1交割制度"
    parameters: "当日买入不可卖出"
    impact: "日内平仓策略不可用; 做T必须有底仓"

  - id: "HB-TRADE-02"
    category: "regulation"
    constraint: "涨跌停限制"
    parameters: "主板±10%; 科创创业板±20%; ST±5%; 北交所±30%"
    impact: "涨跌停价位无法成交; 风控必须考虑涨跌停无法卖出场景"

# ---- §1 元数据 (Metadata) ------------------------------------------------
metadata:
  graph_id: "PROJECT-ENTITY-DEPGRAPH-001"
  version: "3.0.0"
  granularity: "system"                 # 枚举: system | domain | subsystem
  generated_at: ""                       # [AUTO] ISO 8601，空串=未生成
  generated_by: "generate_project_depgraph.py"
  source_hash: ""                       # 源码树 hash，变更触发全量重建
  ssot_hierarchy: ""                    # SSoT层级声明
  total_nodes: 0                        # [AUTO] 节点总数
  total_edges: 0                        # [AUTO] 边总数
  total_blueprint_file_map: 0           # [AUTO] 蓝图→文件映射总条目数
  total_functional_domains: 0           # [AUTO] 功能域注册表条目总数
  scope: ""                             # [AUTO] 覆盖范围描述（含排除项）
  nodes_by_type: {}                     # [AUTO] {type: count} 聚合统计
  edges_by_type: {}                     # [AUTO] {dep_type: count} 聚合统计

# ---- §2 节点定义 (Nodes) --------------------------------------------------
# 20核心字段（全类型统一）+ 按类型差异字段
# 详细字段→类型映射见 §2.1
nodes:
  # === 20核心字段（所有类型必填）===
  - id: ""                              # [AUTO] path→safe_id / blueprint_id / D-{NAME}
    path: ""                            # [AUTO] 相对路径 / 域标识
    type: "module"                      # 枚举见 §3.1（21种）
    granularity: "file"                 # file | domain — 节点粒度
    blueprint_id: ""                    # [AUTO] 从代码头部 [BLUEPRINT] 解析 / 蓝图 module_id
    domain_id: ""                       # [AUTO] 从路径推导
    subdomain_id: ""                    # [AUTO] 从蓝图或路径推导
    belongs_to: ""                      # [AUTO] file→blueprint_id; domain→空 — 归属上级节点
    owner: ""                           # [AUTO] 从蓝图owner / git blame推导 — 负责人
    change_policy: "evolving"           # frozen | stable | evolving | volatile [AUTO] — 修改策略
    impact_level: "M"                   # H | M | L [AUTO] — 修改影响级别
    modification_permission: "ai_modifiable"  # immutable_core | human_gated | ai_modifiable [AUTO] — 修改权限
    file_header_score: 0                # [AUTO] 防幻觉10头部完整度计数（0-10）
    tags: []                            # [AUTO] 蓝图tags > 路径关键词 > 文件名关键词；全空=搜索盲区
    architecture_layer: ""              # 枚举见 §3.9 [AUTO] — 架构层级
    design_maturity: "production"       # 枚举见 §3.10 [AUTO] — 设计成熟度（设计态/运营态维度1）
    deployment_lifecycle: "stable"      # 枚举见 §3.11 [AUTO] — 部署生命周期（设计态/运营态维度2）
    trust_zone: "trusted_core"          # 枚举见 §3.12 [AUTO] — 信任域
    license: "Internal"                 # 枚举见 §3.15 [AUTO] — 许可证类型
    drive_direction: "bottom_up"          # 枚举见 §3.17 [AUTO] — 驱动方向（由上至下设计驱动 / 由下至上实现回写）

  # === 按类型差异字段 ===
  # 代码类（module/script/test）额外字段:
    imports: []                         # [AUTO] Python import 列表
    vulnerability_refs: []              # [{cve_id, severity, affected_versions, patch_status}]

  # 配置类（config/registry/data/contract/schema/gate）额外字段:
    yaml_references: []                 # [AUTO] YAML/JSON 中引用 ID 列表

  # 文档类（doc/blueprint/policy/standard/template/diagram）额外字段:
    doc_references: []                  # [AUTO] MD 中引用 ID 列表

  # blueprint 类型额外字段:
    module_id: ""                       # [AUTO] 蓝图 module_id（与 blueprint_id 相同值）

  # 域级类型额外字段:
    business_stream: ""                 # [AUTO] 业务流归属
    stream_role: ""                     # [AUTO] gateway|enforcement|consumer|producer|pool|registry|unknown
    build_status: "unbuilt"             # 枚举见 §3.18 [AUTO] — 实现状态（能不能造的维度1）
    can_build: false                    # [AUTO] ✅/❌ 二元裁定——能不能造（源:交易决策架构.md §30）
    gate_reason: ""                     # [AUTO] 不能造的原因（can_build=false时必填）
    hard_boundary_ref: ""               # [AUTO] 卡住的硬边界ID（如HB-SEC-05）
    module_lifecycle_state: ""          # 枚举见 §3.19 [AUTO] — 模块生命周期
    runtime_plane: ""                   # [AUTO] scheduled | event_driven | both — 运行平面
    ddd_aggregate: ""                   # [AUTO] 所属DDD聚合根
    consumed_interfaces: []             # [AUTO] 消费的接口契约ID列表
    provided_interfaces: []             # [AUTO] 提供的接口契约ID列表

# ---- §3 边定义 (Edges) ----------------------------------------------------
# 5必填 + 11应该有 = 16字段
edges:
  # === 必填字段（5个）===
  - from: ""                            # [AUTO] 源节点 id
    to: ""                              # [AUTO] 目标节点 id
    dep_type: "import_depends"          # 枚举见 §3.2（12种）
    architecture_direction: "downstream"  # 枚举见 §3.3 — 架构方向
    coupling_strength: "critical"       # 枚举见 §3.4 — 耦合强度
  # === 应该有字段（11个，生成器升级后产出）===
    used_symbol: ""                     # [AUTO] 具体使用的函数/类名
    invocation_method: "import"         # import | HTTP | gRPC | CLI | file_read | event | shared_kernel
    api_contract_refs: []               # API契约引用链
    event_ref: ""                       # 事件引用ID
    ddd_integration_pattern: ""         # 枚举见 §3.6（DDD跨域集成模式）
    failure_mode: ""                    # 枚举见 §3.5
    fallback: ""                        # [AUTO] try/except分析: return_none|log_and_continue|re_raise
    activation_condition: ""            # [AUTO] 依赖激活条件
    data_transfer_description: ""       # [AUTO] 数据传输描述（入参→出参→格式）
    resource_impact: ""                 # [AUTO] 资源影响描述
    relationship_type: "one_to_many"    # one_to_one | one_to_many | many_to_one | many_to_many

# ---- §4 邻接表 (Adjacency Lists) -----------------------------------------
# 正反向邻接表，避免每次从 edges 重建。12K+ 边重建 = 浪费。
adjacency_lists:
  forward: {}                           # [AUTO] {node_id: [dep_node_ids]} — 我依赖谁
  reverse: {}                           # [AUTO] {node_id: [dependent_node_ids]} — 谁依赖我

# ---- §5 功能域注册表 (Functional Domain Registry) -------------------------
# AI 看到节点 domain_id 必须知道这个域是什么。不知道 = 无法判断跨域修改影响。
# 真源: docs/01_policies_and_standards/_registry/catalogs/functional-domain-registry.yaml
functional_domains:
  - domain: ""                           # 顶级功能域（如 governance, security, data）
    subdomain: ""                        # 子域（如 rule_enforcement, access_control）
    domain_id: ""                        # depgraph 中的域ID（如 D-ALT-DATA, D_AUTONOMY）
    ssot_module: ""                      # 域的 SSoT 模块ID（如 MOD-GATE_ENGINE）
    ssot_path: ""                        # 域的代码根路径（如 src/zephyr/governance/rule_enforcement/）
    covers: []                           # 域覆盖的功能列表
    aliases: []                          # 域的别名/搜索关键词
    change_policy: ""                     # frozen | stable | evolving | volatile
    modification_permission: ""          # immutable_core | human_gated | ai_modifiable

# ---- §6 蓝图→文件映射 (Blueprint File Map) --------------------------------
# 设计态核心数据：蓝图→文件列表。AI 修改蓝图时必须知道影响哪些文件。
blueprint_file_map:
  MOD-XXX-001:
    - src/zephyr/xxx/file1.py
    - src/zephyr/xxx/file2.py
    - tests/test_xxx.py

# ---- §7 孤儿节点 (Orphan Nodes) -------------------------------------------
# 无入边无出边的节点。RULE-TWO 反孤儿核心数据。
orphan_nodes:
  - node_id_here

# ---- §8 完整性声明 (Completeness Declaration) -----------------------------
# AI 必须知道当前依赖图是否完整。基于不完整数据做决策 = 幻觉。
completeness_declaration:
  completeness: "unknown"               # 枚举见 §3.7
  missing_scopes: []                    # 缺失的 granularity 列表
  last_verified: ""                     # ISO 8601
  coverage_dimensions:                  # [AUTO] 按 node.type 分组统计
    - dimension: ""                     # internal_modules | external_libraries | docs | scripts | gates | data_assets
      covered: 0
      total: 0
      pct: 0.0

# ---- §9 图指标 (Graph Metrics) --------------------------------------------
graph_metrics:
  node_count: 0                         # [AUTO]
  edge_count: 0                         # [AUTO]
  is_dag: true                          # [AUTO]
  cycles: []                            # [AUTO]
  topological_order: []                 # [AUTO] 拓扑排序结果（编译/加载顺序）
  orphan_nodes_count: 0                 # [AUTO]
  floating_nodes_count: 0               # [AUTO] domain_id="" AND blueprint_id="" 但有依赖链
  most_depended_upon: []                # [AUTO] 入度 Top-20
  max_depth: 0                          # [AUTO] 最长依赖链深度
  layer_violations: 0                   # [AUTO] architecture_direction=upstream 计数
  amplification_factor: {}              # [AUTO] {node_id: ratio} 传递依赖/直接依赖，>10x=高风险
  depth_heat_map: []                    # [AUTO] [{node_id, depth, risk: green|orange|red}]
  blast_radius: {}                      # [AUTO] {node_id: transitive_closure_size} >20=高风险
  risk_propagation_paths: []            # [AUTO] [{from, to, path, risk_weight}]
  dead_dependency_count: 0              # [AUTO] 声明但无运行时引用的边

# ---- §10 架构约束 (Architecture Constraints) --------------------------------
architecture_constraints:
  acyclic: true
  max_chain_depth: 3
  layer_direction_rule: "downstream_only"  # 枚举: downstream_only | any
  forbidden_edges: []                   # 禁止的依赖模式
  required_coverage: 0.95               # 最低覆盖率
  amplification_threshold: 10           # 放大倍数阈值
  blast_radius_threshold: 20            # 爆炸半径阈值
  blueprint_alignment: true             # 蓝图双向对齐验证
  license_compliance: true              # 第三方库 license ≠ Unknown
  vulnerability_tracking: true          # 高危漏洞必须有 patch_status

# ---- §11 业务流 (Business Streams) ----------------------------------------
# AI 改模块必须知道影响哪条业务线。没有业务流 = 只看代码级看不到业务级。
business_streams:
  - stream_id: "VS-001"
    name: ""
    goal: ""
    input: ""
    output: ""
    runtime_plane: ""
    nodes: []
    cross_points: []

# ---- §12 业务流交叉点 (Stream Cross Points) --------------------------------
# 两条业务流交叉的节点 = 修改风险最高的点。AI 不知道交叉点 = 盲目修改。
stream_cross_points:
  - point_id: "X-001"
    name: ""
    source_stream: ""
    target_stream: ""
    activation_condition: ""
    data_transfer_description: ""
    resource_impact: ""

# ---- §13 依赖矩阵 (Dependency Matrix) ------------------------------------
# 跨域影响速查表。矩阵 = 一眼看出哪些域之间有依赖。
dependency_matrix:
  row_headers: []                       # 域 ID 列表
  col_headers: []                       # 域 ID 列表
  cells: []                             # [{row, col, dep_count, dep_types[]}]

# ---- §14 事件流 (Event Flows) ----------------------------------------------
# AI 改事件发布方必须知道哪些消费方受影响。
event_flows:
  - event_id: "E-SG-01"
    name: ""
    source_domain: ""
    target_domain: ""
    frequency: ""
    contract_ref: ""

# ---- §15 因果链 (Causal Chains) -------------------------------------------
# AI 改上游事件必须知道下游连锁反应。
causal_chains:
  - chain_id: "CC-001"
    name: ""
    chain_type: ""
    event_sequence: []
    domains_involved: []

# ---- §16 启动序列 (Startup Sequence) --------------------------------------
# AI 改前置条件必须知道谁会启动失败。
startup_sequence:
  - node_id: ""
    readiness_prerequisites: []
    arb_ref: ""
    phase: ""

# ---- §17 依赖覆盖度 (Dependency Coverage) ---------------------------------
# AI 必须知道依赖图覆盖了哪些维度。不完整 = 决策基于半份数据。
dependency_coverage:
  - dimension: ""
    current_pct: 0
    target_pct: 100
    key_modules: []

# ---- §18 设计决策记录 (Design Decisions) -----------------------------------
# AI 必须知道为什么这样设计。不知道 = 可能推翻已有决策。
design_decisions:
  - date: ""
    decision: ""
    rationale: ""
    status: "active"                    # active | superseded | deprecated

# ---- §19 蓝图链接 (Blueprint Links) ----------------------------------------
blueprint_links:
  - blueprint_id: ""                    # 蓝图 module_id
    blueprint_path: ""                  # 蓝图文件路径
    blueprint_status: ""                # draft | active | deprecated
    source_section: ""                  # 依赖图中哪个子图产生了此蓝图
    alignment_verified: false
    last_aligned_at: ""                 # ISO 8601

# ---- §20 路径映射规则 (Path Mappings) ----------------------------------------
# 依赖图是路径映射的 SSoT。创建新文件必须先查此节。
path_mappings:
  - pattern: ""                         # 节点 ID 匹配模式（glob）
    code_root: ""                       # 代码根目录绝对路径
    blueprint_root: ""                  # 蓝图根目录绝对路径
    test_root: ""                       # 测试根目录绝对路径
    script_root: ""                     # 脚本根目录绝对路径
    naming_rule: ""                     # 命名规则说明
    examples: []                        # 路径示例列表

# ---- §21 分片索引 (Shard Index) --------------------------------------------
# 依赖图超过 LLM 上下文窗口时的拆分方案。
# 警告阈值: 40K tokens | 强制拆分阈值: 60K tokens
shard_index:
  strategy: "by_domain"                 # 枚举见 §3.13
  overview_file: ""                     # 总览索引文件路径
  trigger_reason: ""                    # 拆分触发原因
  files:
    - file_path: ""                     # 子文件相对路径
      domain_id: ""                     # 对应域 ID
      description: ""                   # 一句话
      token_estimate: 0                 # 供 AutoRuntime 调度
      node_count: 0
      status: "active"                  # active | deprecated | draft

# ---- §22 粒度层级 (Granularity Hierarchy) ----------------------------------
# 支持缩放：域级 → 子系统级 → 模块级 → 文件级
granularity_hierarchy:
  parent_graph_id: ""                   # 上级依赖图 ID（空 = 顶层）
  sub_graph_ids: []                     # 下级依赖图 ID 列表
  aggregation_rules:
    - from_granularity: "domain"        # 源粒度
      to_granularity: "subsystem"       # 目标粒度
      method: "collapse"                # 枚举: collapse | abstract | filter
      description: ""
```

### 2.1 节点字段按类型标准

**20核心字段（所有类型统一）**：

| # | 字段 | 推导方式 | 防幻觉价值 |
|---|------|---------|-----------|
| 1 | id | path→safe_id | 找不到节点 |
| 2 | path | 相对路径 | 不知道文件在哪 |
| 3 | type | 扩展名+路径规则 | 不知道文件类型 |
| 4 | granularity | file/domain | 不知道节点粒度 |
| 5 | blueprint_id | [BLUEPRINT]头部 | 不知道归属蓝图 |
| 6 | domain_id | 路径→域映射 | 不知道在哪个功能域 |
| 7 | subdomain_id | 蓝图→子域映射 | 只知大域不知子域 |
| 8 | belongs_to | file→blueprint_id | 不知道归属上级 |
| 9 | owner | 蓝图owner/git blame | 不知道谁负责 |
| 10 | change_policy | [STABILITY]头部 | 不知道修改策略 |
| 11 | impact_level | [SAFETY]头部 | 不知道修改影响级别 |
| 12 | modification_permission | [AI_AUTONOMY]头部 | 不知道修改权限 |
| 13 | file_header_score | AST扫描0-10 | 不知道防幻觉头部缺多少 |
| 14 | tags | 蓝图>路径>文件名 | 搜索发现节点的入口 |
| 15 | architecture_layer | 蓝图frontmatter | 不知道架构层级 |
| 16 | design_maturity | 蓝图status+代码分析 | 不知道设计成熟度 |
| 17 | deployment_lifecycle | 蓝图status+代码分析 | 不知道部署生命周期 |
| 18 | trust_zone | 蓝图frontmatter | 不知道在哪个信任域 |
| 19 | license | 依赖分析 | 不知道许可证类型 |
| 20 | drive_direction | 蓝图有无+代码有无 | 不知道是设计驱动还是实现回写，可能对设计态模块直接改代码 |

**按类型完整字段清单**（AI 直接查此表，不需要自己拼）：

| 字段 | module | script | test | config | registry | data | contract | schema | gate | doc | blueprint | policy | standard | template | diagram | application | package | domain | aggregate | service | library |
|------|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **20核心字段** | | | | | | | | | | | | | | | | | | | | | |
| id | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| path | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| type | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| granularity | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| blueprint_id | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| domain_id | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| subdomain_id | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| belongs_to | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| owner | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| change_policy | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| impact_level | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| modification_permission | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| file_header_score | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| tags | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| architecture_layer | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| design_maturity | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| deployment_lifecycle | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| trust_zone | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| license | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| drive_direction | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **差异字段** | | | | | | | | | | | | | | | | | | | | | |
| imports | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| vulnerability_refs | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| yaml_references | ❌ | ❌ | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| doc_references | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| module_id | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| business_stream | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| stream_role | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| build_status | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| can_build | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| gate_reason | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| hard_boundary_ref | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| module_lifecycle_state | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| runtime_plane | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| ddd_aggregate | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| consumed_interfaces | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| provided_interfaces | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **字段总数** | **22** | **22** | **22** | **21** | **21** | **21** | **21** | **21** | **21** | **21** | **22** | **21** | **21** | **21** | **21** | **29** | **29** | **29** | **29** | **29** | **29** |

> **速查**: module/script/test = 22字段; config/registry/data/contract/schema/gate = 21字段; doc/policy/standard/template/diagram = 21字段; blueprint = 22字段; 域级 = 29字段。

> **代码类**: module / script / test
> **配置类**: config / registry / data / contract / schema / gate
> **文档类**: doc / blueprint / policy / standard / template / diagram
> **域级**: application / package / domain / aggregate / service / library

---

## 3. 受控词表

### 3.1 节点类型 (node.type)

21 种节点类型，分为文件级（15种）和域级（6种）。

### 3.1a 节点粒度 (node.granularity)

| granularity | 说明 | 包含的 type |
|------------|------|-----------|
| `file` | 文件级节点 | module, script, test, config, registry, data, contract, schema, gate, doc, blueprint, policy, standard, template, diagram |
| `domain` | 域级节点 | application, package, domain, aggregate, service, library |

### 3.1b 元数据粒度 (metadata.granularity)

| granularity | 说明 |
|------------|------|
| `system` | 全项目系统级 |
| `domain` | 单域级 |
| `subsystem` | 子系统级 |

**文件级（granularity=file）**：

| type | 字段标准 | 说明 | 示例 |
|------|:---:|------|------|
| `module` | 代码类 | 内部模块 .py | zephyr/core/schemas.py |
| `script` | 代码类 | 治理/运维脚本 | scripts/governance/generate_project_depgraph.py |
| `test` | 代码类 | 测试文件 | tests/test_depgraph.py |
| `config` | 配置类 | 配置文件 YAML/TOML | gate YAML, pyproject.toml |
| `registry` | 配置类 | 注册表 YAML | gate_registry.yaml |
| `data` | 配置类 | 数据资产 JSON/YAML | dependency-graph.json |
| `contract` | 配置类 | 契约定义 | contracts/*.yaml |
| `schema` | 配置类 | Schema 文件 | schemas/*.json |
| `gate` | 配置类 | 门禁检查 YAML | EN-001, MAD-005 |
| `doc` | 文档类 | 文档文件 | docs/*.md（非蓝图/非模板） |
| `blueprint` | 文档类 | 蓝图文件 | docs/03_modules/.../blueprint.md |
| `policy` | 文档类 | 策略文件 | docs/.../governance/*.md |
| `standard` | 文档类 | 标准文件 | docs/.../engineering/*.md |
| `template` | 文档类 | 模板文件 | docs/.../templates/*.md |
| `diagram` | 文档类 | 图表文件 | docs/.../*.mmd |

**域级（granularity=domain）**：

| type | 说明 | 示例 |
|------|------|------|
| `application` | 独立应用 | zephyr.runtime |
| `package` | Python 包 | zephyr.core |
| `domain` | 业务域 | D-DATA, D_RISK |
| `aggregate` | DDD 聚合 | AGG-007 MarketDataBatch |
| `service` | 外部服务 | Ollama, DeepSeek API |
| `library` | 第三方库 | pydantic, networkx |

### 3.2 依赖类型 (edge.dep_type)

| 级别 | dep_type | 说明 | 示例 |
|:---:|----------|------|------|
| 必须 | `import_depends` | Python import 依赖 | `from zephyr.core import X` |
| 必须 | `references` | 引用依赖 | 脚本读取 YAML 注册表 |
| 必须 | `test_depends` | 测试依赖 | test 引用被测模块 |
| 必须 | `owned_by` | 归属依赖 | 文件→蓝图归属 |
| 应该有 | `config_depends` | 配置引用依赖 | gate 引用 rule-registry |
| 应该有 | `data_depends` | 数据文件依赖 | 脚本读取 YAML 注册表 |
| 应该有 | `blueprint_depends` | 蓝图契约依赖 | blueprint §4 引用另一个蓝图 |
| 应该有 | `event_depends` | 事件驱动依赖 | D_SIGLEGACY 订阅 E-RS-01 |
| 应该有 | `contract_depends` | 契约消费依赖 | D_FACTOR 消费 CTR-001 |
| 应该有 | `shared_kernel` | 共享内核依赖 | D-EXECUTION + D_RISK 共享 Position |
| 可选 | `script_depends` | 脚本调用依赖 | 脚本 import 另一个脚本 |
| 可选 | `runtime_depends` | 运行时服务依赖 | 调用 Ollama API |

### 3.3 架构方向 (edge.architecture_direction)

| architecture_direction | 说明 | 含义 |
|----------------------|------|------|
| `downstream` | 下游依赖 | 外层→内层（符合 Clean Architecture） |
| `upstream` | 上游依赖 | 内层→外层（架构违规，必须标记例外） |
| `bidirectional` | 双向依赖 | 两个模块相互依赖（高耦合，需要审视） |
| `decoupled` | 解耦依赖 | 无方向性依赖（事件驱动/共享内核等解耦模式） |

### 3.4 耦合强度 (edge.coupling_strength)

| coupling_strength | 说明 | 缺失后果 |
|------------------|------|---------|
| `critical` | 关键依赖 | 运行时崩溃 / 编译失败 |
| `degradable` | 可降级依赖 | 功能降级但仍可运行 |
| `optional` | 可选依赖 | 无影响，仅增强功能 |
| `event_driven` | 事件驱动 | 异步解耦，发布方不依赖消费方 |
| `conditional` | 条件依赖 | 仅特定条件下激活 |

### 3.5 故障模式 (edge.failure_mode)

| failure_mode | 说明 | 典型 fallback |
|-------------|------|-------------|
| `service_down` | 被依赖服务不可用 | 重试 / 降级 / 熔断 |
| `timeout` | 调用超时 | 降级 / 缓存 / 异步重试 |
| `data_corruption` | 数据损坏 | 校验 / 回滚 / 人工介入 |
| `version_mismatch` | 接口版本不兼容 | 兼容层 / 降级 / 锁定版本 |
| `circuit_break` | 熔断触发 | 降级 / 排队 / 通知 |
| `cascade_failure` | 级联失效 | 舱壁隔离 / 限流 / 熔断 |

### 3.6 DDD跨域集成模式 (edge.ddd_integration_pattern)

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

### 3.7 完整性 (completeness_declaration.completeness)

| completeness | 说明 |
|-------------|------|
| `complete` | 所有依赖已完整记录 |
| `incomplete` | 已知有缺失 |
| `incomplete_first_party_only` | 仅内部依赖完整，第三方缺失 |
| `incomplete_third_party_only` | 仅第三方依赖完整，内部缺失 |
| `unknown` | 完整性未知（默认值，新图必须用此值直到验证） |

### 3.8 修改策略 (node.change_policy)

| change_policy | 说明 | 修改策略 |
|--------------|------|---------|
| `frozen` | 禁止修改 | 修改 = 破坏不变量 |
| `stable` | 需变更门控 | 跳过门控 = 漂移 |
| `evolving` | 可频繁修改 | — |
| `volatile` | AI 可自主调整 | — |

### 3.9 架构层级 (node.architecture_layer)

| architecture_layer | 说明 | 依赖方向 |
|-------------------|------|---------|
| `L0_infrastructure` | 基础设施层 | 被所有层依赖 |
| `L1_foundation` | 基础服务层 | 依赖 L0 |
| `L2_domain` | 领域层 | 依赖 L0/L1 |
| `L3_application` | 应用层 | 依赖 L0/L1/L2 |
| `shared` | 跨层共享 | 可被任意层依赖 |
| `contracts` | 契约定义 | 可被任意层依赖 |
| `meta` | 元层 | 全局约束，不被依赖 |
| `domain_integration` | 域集成层 | 跨域协调 |

### 3.10 设计成熟度 (node.design_maturity) — 设计态/运营态维度1

| design_maturity | 态 | 说明 | 生成器推导方式 |
|----------------|:---:|------|-------------|
| `design` | 设计态 | 仅有蓝图/设计，尚无代码实现 | 有 blueprint 无 .py 文件 |
| `prototype` | 运营态 | 快速原型，设计不牢固 | 有 .py 无 test 文件 |
| `production` | 运营态 | 生产级 | 有 .py + test 文件 |

### 3.11 部署生命周期 (node.deployment_lifecycle) — 设计态/运营态维度2

> deployment_lifecycle 与 design_maturity 正交：design_maturity 回答"设计有多成熟"，deployment_lifecycle 回答"代码部署在什么阶段"。

| deployment_lifecycle | 说明 |
|---------------------|------|
| `stable` | 稳定运行 |
| `beta` | 测试中 |
| `T0_active` | Tier 0 已激活（核心功能，必须可用） |
| `T1_active` | Tier 1 已激活（重要功能，应该可用） |
| `T2_deferred` | Tier 2 延期（增强功能，可以延期） |
| `design_only` | 仅设计，未实现 |
| `not_started` | 未启动 |
| `deprecated` | 已废弃 |
| `end_of_life` | 终止维护 |

### 3.12 信任域 (node.trust_zone)

| trust_zone | 说明 |
|-----------|------|
| `trusted_core` | 核心信任域——系统内部 |
| `api_gateway` | API网关层——认证/鉴权/限流 |
| `external_service` | 外部服务——第三方API |
| `untrusted_input` | 不受信输入——用户输入/外部数据 |

### 3.13 分片策略 (shard_index.strategy)

| strategy | 说明 | 适用场景 |
|----------|------|---------|
| `by_domain` | 按功能域拆分（推荐） | 域驱动设计系统 |
| `by_layer` | 按架构层拆分 | 层级清晰的系统 |
| `by_depth` | 按依赖深度拆分 | 扁平依赖结构 |
| `by_critical_path` | 按关键路径拆分 | 高风险核心链路 |
| `custom` | 自定义拆分 | 混合策略 |

### 3.14 修改权限 (node.modification_permission)

| modification_permission | 说明 | AI 行为 |
|------------------------|------|---------|
| `immutable_core` | 核心不变量 | 只读，禁止任何修改 |
| `human_gated` | 需人类审批 | 可提议修改，需 Owner 批准 |
| `ai_modifiable` | AI 可修改 | 可直接修改 |

### 3.15 许可证类型 (node.license)

| license | 说明 |
|---------|------|
| `MIT` | MIT 许可证 |
| `Apache-2.0` | Apache 2.0 许可证 |
| `GPL-3.0` | GPL 3.0 许可证 |
| `BSD-3-Clause` | BSD 3 条款许可证 |
| `Proprietary` | 专有许可证 |
| `Internal` | 内部使用——不对外分发 |
| `Unknown` | 许可证未知（默认值，必须尽快确认） |

### 3.16 关系类型 (edge.relationship_type)

| relationship_type | 说明 | 示例 |
|------------------|------|------|
| `one_to_one` | 一对一 | 一个配置对应一个模块 |
| `one_to_many` | 一对多 | 一个模块被多个测试依赖 |
| `many_to_one` | 多对一 | 多个模块依赖一个共享库 |
| `many_to_many` | 多对多 | 多个模块与多个服务互依赖 |

### 3.17 驱动方向 (node.drive_direction)

| drive_direction | 说明 | 生成器推导方式 |
|-----------------|------|-------------|
| `top_down` | 由上至下设计驱动——先有蓝图/设计，尚无代码 | 有 blueprint 无 .py 文件 |
| `bottom_up` | 由下至上实现回写——先有代码，回写到蓝图 | 有 .py 文件 |

> **drive_direction 与 design_maturity 的关系**：drive_direction 回答"这个节点是怎么来的"，design_maturity 回答"设计有多成熟"。top_down 节点的 design_maturity 通常是 design，bottom_up 节点通常是 prototype/production。但不是 1:1 映射——一个 bottom_up 节点也可能 design_maturity=design（代码写了但设计还不成熟）。

### 3.18 实现状态 (node.build_status)

| build_status | 说明 | can_build |
|-------------|------|:---:|
| `built` | 已完整实现 | ✅ |
| `partial` | 部分实现 | ✅（继续完成）或 ❌（有硬边界卡住） |
| `unbuilt` | 未实现 | ✅（可以开工）或 ❌（有硬边界卡住） |

> **can_build=false 的典型原因**：硬边界卡住（hard_boundary_ref）、依赖未就绪、安全审查未通过、Owner 未批准。

### 3.19 模块生命周期 (node.module_lifecycle_state)

| module_lifecycle_state | 说明 |
|----------------------|------|
| `planned` | 已规划，未启动 |
| `in_dev` | 开发中 |
| `active` | 已上线运行 |
| `in_review` | 审查中 |
| `beta` | 灰度测试中 |
| `maintenance` | 维护模式（只修bug不加功能） |
| `deprecated` | 已废弃，待下线 |
| `retired` | 已下线 |


---

## 4. 计算规则与约束验证

> §8 图指标自动计算脚本：`scripts/governance/diagnose_depgraph.py`

### 4.1 邻接表构建

```
forward[A] = [B, C, ...]  →  A 依赖 B, C, ...
reverse[B] = [A, ...]      →  B 被 A 依赖
```

邻接表从 §3 边列表派生：遍历所有边，对每条 `(from=A, to=B)`，将 B 加入 `forward[A]`，将 A 加入 `reverse[B]`。自动生成器必须同时产出 forward 和 reverse 两个方向。

### 4.2 图指标计算与架构约束验证

| # | 项目 | 类型 | 算法/验证方法 | 说明/不通过处置 |
|---|------|:----:|-------------|---------------|
| 1 | `is_dag` | 指标 | Kahn 拓扑排序 | 排序成功 = DAG |
| 2 | `cycles` | 指标 | DFS 回溯 | 返回所有环路径 |
| 3 | `topological_order` | 指标 | Kahn 算法 | 仅 is_dag=true 时有效 |
| 4 | `orphan_nodes_count` | 指标 | 入度=0 且 出度=0 | 对标 RULE-TWO 反孤儿 |
| 5 | `floating_nodes_count` | 指标 | domain_id="" AND blueprint_id="" AND (入度>0 OR 出度>0) | 必须分配域/蓝图 |
| 6 | `most_depended_upon` | 指标 | 入度排序 | 入度 Top-20 |
| 7 | `max_depth` | 指标 | 最长路径 DFS | 对标 audit_depends_on_chain_depth |
| 8 | `layer_violations` | 指标 | architecture_direction=upstream 计数 | 对标 Clean Architecture |
| 9 | `amplification_factor` | 指标 | 传递依赖计数 / 直接依赖计数 | 放大倍数 > 10x 为高风险 |
| 10 | `depth_heat_map` | 指标 | 每节点最长链 DFS + 风险评级 | 绿<=2 / 橙=3 / 红>=4 |
| 11 | `blast_radius` | 指标 | 每节点传递闭包大小 BFS | 闭包 > 20 = 高风险 |
| 12 | `risk_propagation_paths` | 指标 | BFS + 风险权重累积 | impact_level=H 的节点传播路径必须标记 |
| 13 | `dead_dependency_count` | 指标 | 声明但无运行时引用的边计数 | > 0 = 存在死依赖，需清理 |
| 14 | `acyclic` | 约束 | Kahn 拓扑排序 | 环必须拆解 |
| 15 | `max_chain_depth` | 约束 | 最长路径 DFS | 链超深必须重构 |
| 16 | `layer_direction_rule` | 约束 | 边 architecture_direction 字段 | upstream 边必须消除或标记例外 |
| 17 | `forbidden_edges` | 约束 | 模式匹配 | 禁止模式必须移除 |
| 18 | `required_coverage` | 约束 | node_count / 总模块数 | 不足必须补充节点 |
| 19 | `amplification_threshold` | 约束 | amplification_factor > 10x | 高放大节点必须拆分或扁平化 |
| 20 | `blast_radius_threshold` | 约束 | blast_radius > 20 | 高影响节点必须拆分或标记为 human_gated |
| 21 | `blueprint_alignment` | 约束 | §18 blueprint_links 双向验证 | 蓝图缺失或未对齐必须补充 |
| 22 | `path_mapping_compliance` | 约束 | 节点 path ∈ §19 path_mappings 匹配结果 | 不符合映射规则 = 路径漂移 |
| 23 | `license_compliance` | 约束 | 第三方库 license ≠ Unknown | Unknown 许可证必须确认后更新 |
| 24 | `vulnerability_tracking` | 约束 | vulnerability_refs 中 severity=Critical/High 的必须有 patch_status | 未修补的高危漏洞必须标记 |

---

## 5. 蓝图双向链接规范

### 5.1 设计原则

依赖图是真源核对文档，蓝图是施工指导文档。两者必须双向对齐：

```
依赖图 §18 blueprint_links  ──→  蓝图 [BLUEPRINT] 字段
蓝图 §4 文件清单             ──→  依赖图节点
```

### 5.2 链接方式

采用**集中表格**（§18 blueprint_links），理由：

| 方案 | 优点 | 缺点 |
|------|------|------|
| 集中表格 | 一目了然所有蓝图、便于验证对齐、便于扫描 | 需要维护 source_section 字段关联子图 |
| 内联（每个子图下面加） | 上下文紧密 | 分散难找、不便全量验证、容易遗漏 |

### 5.3 双向验证规则

| 验证方向 | 规则 | 不通过处置 |
|---------|------|-----------|
| 依赖图 → 蓝图 | §18 每个 blueprint_path 必须存在且包含 [BLUEPRINT] 字段 | 蓝图缺失或格式不对 → 必须补充 |
| 蓝图 → 依赖图 | 蓝图 [BLUEPRINT] 字段引用的依赖图必须存在且包含对应节点 | 依赖图缺失节点 → 必须补充 |
| 对齐验证 | 蓝图 §4 文件清单 ↔ 依赖图节点 path 双向匹配 | 不匹配 → 漂移，必须修正 |

---

## 6. 与现有资产映射

| 现有资产 | 对应模板结构 | 差距 |
|---------|-------------|------|
| `generate_project_depgraph.py` | §2 Nodes + §3 Edges + §8-§9 | 字段名需对齐受控词表，边类型需从 2 种映射到 §3.2 的 12 种 |
| `diagnose_depgraph.py` | §4 计算规则 | 缺 amplification/blast_radius/risk_propagation/dead_dependency |
| `depgraph` | 全 23 段 | 唯一真源文件 |
| `dependency.py` Pydantic 模型 | §2 Nodes + §3 Edges + §8 Graph Metrics | 缺 architecture_direction/coupling_strength/completeness_declaration/architecture_constraints 及 §4-§21 |
| `cross-module-dependency-registry.yaml` (PS-REG-007) | 已废弃（PostgreSQL depgraph 替代） | 文件已删除 |
| `system-dependency-map.md` | 已废弃（dependency_path_panorama.md 替代） | 文件已删除 |
| `business-domain-dependency-map-draft.md` | §12 Matrix + §13 Event Flows + §14 Causal Chains + §15 Startup Sequence | 纯文档，不可计算 |
| `EN-001` 门禁 | §9 Architecture Constraints.acyclic | 只检测环，不检测方向/深度/覆盖率/放大/蓝图对齐 |
| 蓝图-代码双向对齐 | §18 blueprint_links | 当前无结构化链接 |

---

## 7. AI 自治权限标注

| 操作 | 修改权限 | 说明 |
|------|:---:|------|
| 使用模板创建依赖图 | ai_modifiable | AI 可按模板格式生成依赖图数据 |
| 修改受控词表 | human_gated | 词表变更影响所有依赖图 |
| 修改架构约束 | human_gated | 约束变更影响门禁验证 |
| 修改 schema 结构 | human_gated | Schema 变更影响所有消费者 |
| 更新蓝图链接 | ai_modifiable | AI 可更新 blueprint_links 的对齐验证状态 |

---

## 8. TTL 与生命周期

| 字段 | 值 |
|------|-----|
| TTL | permanent |
| 审查周期 | 每 90 天 |
| 过期处理 | 如被新标准取代，按废弃流程标记 deprecated |
| 最后审查日期 | 2026-06-06 |

---

## 9. 四层路径对齐规范

### 9.1 对齐链路

```
依赖图 §19 path_mappings (规则SSoT)
  ↓ 规则验证
依赖图节点 path ←→ 蓝图 §4 文件清单 ←→ 代码 [BLUEPRINT] 头部 ←→ 代码物理路径
                                              ↕
                                         任务卡 downstream_outputs
```

### 9.2 对齐验证与漂移处置

| 层级 | 漂移类型 | 验证规则 | 处置 | 审批 |
|------|---------|---------|------|------|
| L1 依赖图→规则 | 路径漂移 | 节点 path → §19 path_mappings | 移动代码或更新规则 | 更新规则需 Owner 批准 |
| L2 依赖图→蓝图 | 蓝图漂移 | 节点 path ↔ 蓝图 §4 路径 | 同步蓝图或依赖图 | AI 可自主同步 |
| L3 蓝图→任务卡 | 任务卡漂移 | 蓝图 §4 路径 → 任务卡 downstream_outputs | 更新任务卡 downstream_outputs | AI 可自主更新 |
| L4 蓝图→代码 | 代码漂移 | 蓝图 §0 文件清单 ↔ 代码 [BLUEPRINT] 头部 | 更新代码头部 | AI 可自主更新 |
| L5 代码→物理路径 | 物理漂移 | [BLUEPRINT] 头部 ↔ 实际文件位置 | 移动文件到声明位置 | 需确认移动不影响其他引用 |

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
| 2026-06-06 | 6.0.0 | 第一性原理重写+字段零歧义重命名。①节点20核心字段+按类型差异字段；②边16字段；③21种节点类型；④12种边类型；⑤23顶层段（含§0硬边界+§5功能域注册表）；⑥design_maturity+deployment_lifecycle+drive_direction三维度；⑦字段重命名消除歧义：scope→granularity, parent_node_id→belongs_to, stability→change_policy, safety_level→impact_level, ai_autonomy→modification_permission, header_completeness→file_header_score, layer→architecture_layer, maturity→design_maturity, lifecycle→deployment_lifecycle, security_boundary→trust_zone, direction→architecture_direction, strength→coupling_strength, interface→used_symbol, protocol→invocation_method, contract_refs→api_contract_refs, context_mapping_pattern→ddd_integration_pattern, trigger_condition→activation_condition, data_flow→data_transfer_description, capacity_impact→resource_impact, cardinality→relationship_type, compositions→completeness_declaration, properties→graph_metrics, constraints→architecture_constraints, value_streams→business_streams, intersection_points→stream_cross_points, activation_sequence→startup_sequence, coverage_assessment→dependency_coverage, document_index→shard_index, hierarchy→granularity_hierarchy；⑧枚举值重命名：inward/outward→downstream/upstream, hard/soft→critical/degradable, controlled_edge→api_gateway, 1:1/1:N/N:1/N:M→one_to_one/one_to_many/many_to_one/many_to_many；⑨受控词表21组（新增granularity×2/relationship_type/drive_direction/build_status/module_lifecycle_state）；⑩新增drive_direction驱动方向字段（由上至下设计驱动/由下至上实现回写）；⑪新增域级硬边界字段：build_status/can_build/gate_reason/hard_boundary_ref/module_lifecycle_state/runtime_plane/ddd_aggregate/consumed_interfaces/provided_interfaces；⑫新增§0硬边界段（8条：hardware×3+capital×1+external_interface×2+regulation×2），AI冷启动第0步必读；⑬新增§5功能域注册表段（domain/subdomain/domain_id/ssot_module/ssot_path/covers/aliases/change_policy/modification_permission），AI冷启动第1步必读，解决domain_id两套ID体系映射问题。 |
| 2026-05-20 | 5.8.1 | 修复 v5.4.0 预存 Bug |
| 2026-05-12 | 1.0.0 | 初始版本 |

---

## 11. AI Agent 自检协议

> AI 生成/更新依赖图后 **MUST** 执行以下自检。全部通过 = 可声明完成。

### 11.1 格式合规自检

| # | 自检项 | 命令/方法 | 通过标准 | 失败处置 |
|---|--------|----------|---------|---------|
| 1 | 语法检查 | `python -c "from zephyr.governance.depgraph_schema import get_depgraph_pg_connection; c=get_depgraph_pg_connection(); c.close(); print('PG OK')"` | 无异常 | 修复 DB 结构 |
| 2 | 节点类型合规 | 检查每个 node.type ∈ §3.1（21 种） | 100% 合规 | 修正到词表值 |
| 3 | 边类型合规 | 检查每个 edge.dep_type ∈ §3.2（12 种） | 100% 合规 | 修正到词表值 |
| 4 | 蓝图双向对齐 | `python scripts/governance/d5_architecture/validators/validate_path_alignment.py --all` | 无 missing | 补充 blueprint_link |
| 5 | 设计态/运营态标记 | 检查每个节点 design_maturity ∈ §3.10 + deployment_lifecycle ∈ §3.11 | 100% 合规 | 补充字段 |

### 11.2 质量自检

| # | 自检项 | 通过标准 | 失败处置 |
|---|--------|---------|---------|
| 6 | 环形依赖 | graph_metrics.is_dag == True | 拆环或在 cycles 中标记已识别 |
| 7 | 孤儿节点 | orphan_nodes_count 合理（doc/policy/config 类孤儿正常） | 非文档类孤儿需补连接 |
| 8 | 浮动节点 | floating_nodes_count = 0 | 每个浮动节点必须分配 domain_id 或 blueprint_id |
| 9 | 增量安全 | 若已有旧版：diff 新增/删除边 ≤ 预期变更范围 | 超出预期 → 标记 [ASSUMPTION] |
| 10 | 完整性声明 | completeness_declaration.completeness ≠ unknown | 验证后更新 completeness |
| 11 | 许可证合规 | 所有第三方库 license ≠ Unknown | Unknown 许可证必须确认 |
| 12 | 漏洞追踪 | vulnerability_refs 中 Critical/High 必须有 patch_status | 未修补漏洞必须标记 |

### 11.3 字段填充等级

| 等级 | 标注 | AI 行为 | 字段 |
|:---:|------|------|------|
| L1 | `[REQUIRED]` | 必须填充，不能空值 | id, path, type, granularity, blueprint_id, domain_id, change_policy, impact_level, modification_permission, file_header_score, drive_direction, dep_type, from, to, architecture_direction, coupling_strength |
| L2 | `[AUTO]` | 从代码/路径/头部推导，推断失败填空串 | subdomain_id, belongs_to, owner, tags, architecture_layer, design_maturity, deployment_lifecycle, trust_zone, license, imports, yaml_references, doc_references, module_id, used_symbol, invocation_method, api_contract_refs, event_ref, ddd_integration_pattern, failure_mode, fallback, activation_condition, data_transfer_description, resource_impact, relationship_type, business_stream, stream_role, vulnerability_refs, build_status, can_build, gate_reason, hard_boundary_ref, module_lifecycle_state, runtime_plane, ddd_aggregate, consumed_interfaces, provided_interfaces |
| L3 | `[HUMAN]` | 填空串或默认值，不猜测 | blueprint_links.last_aligned_at, path_mappings, completeness_declaration, business_streams, event_flows, causal_chains, design_decisions |

### 11.4 AI 冷启动阅读顺序

> 新 AI 进入项目后，MUST 按以下顺序读取依赖图。跳步 = 幻觉。

| 顺序 | 读什么 | 为什么 |
|:---:|------|------|
| 0 | **hard_boundaries** | 硬边界——想改也改不了的客观限制。不知道 = 设计违反物理/法规/外部限制 |
| 1 | **functional_domains** | 功能域注册表——节点 domain_id 对应的域定义。不知道 = 无法判断跨域修改影响 |
| 2 | **metadata** | 确认版本、新鲜度、覆盖范围。过时 → 请求重新生成 |
| 3 | **completeness_declaration** | 依赖图是否完整？不完整 = 决策可能基于半份数据 |
| 4 | **graph_metrics** | 全图健康度：有环吗？有孤儿吗？爆炸半径多大？ |
| 5 | **architecture_constraints** | 全局护栏：最大链深？方向规则？ |
| 6 | **目标节点字段** | change_policy / impact_level / modification_permission / design_maturity / deployment_lifecycle / trust_zone / license → 决定能不能改、是设计态还是运营态、在哪个信任域 |
| 7 | **blueprint_file_map** | 目标蓝图下有哪些文件？改蓝图影响谁？ |
| 8 | **adjacency_lists.reverse** | "谁依赖我？"——改之前必须知道下游消费者 |
| 9 | **business_streams** | 改这个模块影响哪条业务线？ |
| 10 | **event_flows** | 改这个事件发布方，哪些消费方受影响？ |
| 11 | **path_mappings** | 创建新文件必须先查此节——文件放哪里？ |

> **关键原则**: 永远先读 hard_boundaries（什么不能做），再读 functional_domains（域是什么），再读 completeness_declaration 和 architecture_constraints（数据可不可信），再读节点自身字段（能不能改），再读业务域分析（改了影响什么业务），最后读路径映射（新文件放哪里）。
