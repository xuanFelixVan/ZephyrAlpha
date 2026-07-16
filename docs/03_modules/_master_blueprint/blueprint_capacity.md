---
module_id: MOD-MASTER-003
title: "Capacity 蓝图 — 容量升级设计·十个升级章+12缺口审计"
doc_type: blueprint
status: Active
version: "1.3.0"
layer: L1_foundation
layer_name: cross_layer
blueprint_level: domain
owner: ZephyrAlpha-Owner
classification: confidential
language: zh
created_by: human_plus_agent
date: "2026-05-03"
ttl: permanent
last_updated: "2026-05-15"
last_verified: "2026-05-15"
construction_progress: partially_implemented
actual_disk_path: "D:\\ZephyrAlpha\\docs\\03_modules\\_master_blueprint\\blueprint_capacity.md"
template_for: blueprint
generation: 3
functional_domain: infrastructure
parent_module: "MOD-MASTER_BLUEPRINT"
belongs_to: "MOD-MASTER_BLUEPRINT"
rule_form: structural
scope: global
stability: evolving
verifiability: automated
priority: P0
summary: "容量升级设计蓝图。§-2二次容量审计识别12个体系级缺口（GAP-M01~M12），§-1十个升级章完整设计方案。设计上限：10,000治理脚本/1,500模块/100AI并发。"
codification_level: L1
codification_at: "2026-05-15"
depends_on:
  - target: "MOD-MASTER-002"
    at: "全篇"
    why: "基线蓝图——容量升级基于v0.9.2现存设计"
references:
  - path: "D:\\ZephyrAlpha\\docs\\03_modules\\_master_blueprint\\blueprint_baseline.md"
    section: "全篇"
    why: "基线蓝图"
  - path: "D:\\ZephyrAlpha\\docs\\01_policies_and_standards\\templates\\blueprint-template.md"
    section: "全篇"
    why: "蓝图模板v3.5/v3.6"
  - path: "D:\\ZephyrAlpha\\docs\\01_policies_and_standards\\governance\\document\\trae_030_doc_numbering_metadata.yaml"
    section: "全篇"
    why: "压缩工作流标准"
tags:
  - master-blueprint
  - capacity-upgrade
  - scale-plane
  - incremental-scan
  - multi-agent-concurrency
  - 10000-scripts
responsibility_domain: 
build_status: planned
design_maturity: design
---

# Capacity 蓝图 — 容量升级设计·十个升级章+12缺口审计

> module_id: MOD-MASTER-003 | version: 1.3.0 | status: active | layer: cross_layer | blueprint_level: domain
> actual_disk_path: D:\ZephyrAlpha\docs\03_modules\_master_blueprint\blueprint_capacity.md | generation: 3 | construction_progress: partially_implemented

## 概述

本蓝图是 MOD-MASTER_BLUEPRINT 的容量升级设计文件。核心职责：§-2 二次容量审计识别 v1.0.0 的 12 个体系级缺口（GAP-M01~M12），§-1 给出十个升级章的完整设计方案（规模平面/增量扫描/多AI并发/注册发现v2/脚本执行v2/容量调度/可观测性/水平扩展/迁移路径/施工序列）。设计上限 10,000 治理脚本 / 1,500 模块 / 100 AI 并发。上游依赖 baseline（v0.9.2 现存设计），下游被 Agent Spec 蓝图和 Circuit Breaker 消费。

### 2.2 不包含的职责

| # | 排除项 | 由谁负责 |
|---|--------|---------|
| 1 | 独立模块拓扑与职责边界 | SYS-MASTER-001 (blueprint.md) |
| 2 | CT-*集成契约定义 | MOD-MASTER-002 (blueprint_baseline.md §二) |
| 3 | 各模块实现代码 | MOD-INF-001~038 各模块蓝图 |

>
> **标准锚点（防幻觉）**——本蓝图必须严格遵循以下标准：
> - 蓝图+施工图模板：[blueprint-template.md](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/templates/blueprint-template.md)
> - 压缩工作流标准：[trae_030_doc_numbering_metadata.yaml](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_030_doc_numbering_metadata.yaml)
> - 代码头部标准：[code-construction-standards.md §7](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/governance/engineering/code-construction-standards.md)
> - 依赖图：[dependency_path_panorama.md](file:///d:/ZephyrAlpha/docs/02_enterprise_architecture/04_architecture_principles_decisions/dependency_path_panorama.md)
> - 优化规则：先 Layer 1（蓝图+施工图模板合规）→ 后 Layer 2（规格化砍削）
> - 基线蓝图：[blueprint_baseline.md](file:///d:/ZephyrAlpha/docs/03_modules/_master_blueprint/blueprint_baseline.md)

---

## 模板章节映射表

> 本文件为 MOD-MASTER_BLUEPRINT 拆分蓝图，内容按容量升级逻辑组织（§-2/§-1）。
> 以下映射表说明现有章节与蓝图模板 v3.5/v3.6 必需章节的对应关系。

| 模板必需章节 | 本文件对应章节 | 状态 |
|------------|-------------|:---:|
| §0 代码对齐验证 | 见基线蓝图 §零 | 基线覆盖 |
| §1 设计背景与目标 | §-2.1 容量审计总结论 | ✅ |
| §2 模块边界 | §-2.2~§-2.13 缺口分析 | ✅ |
| §3 架构设计 | §-1 升级章架构 | ✅ |
| §4 接口契约 | §-1 各升级章接口定义 | ✅ |
| §5 约束条件 | §-1 规模平面约束 | ✅ |
| §6 错误处理 | §-1 各升级章错误处理 | ✅ |
| §7 备选方案 | 已删除→§18决策记录覆盖 | v3.6删除 |
| §8 安全考量 | 见基线蓝图 §二十三 | 基线覆盖 |
| §9 测试策略 | §-1 施工序列验证 | ✅ |
| §10 依赖关系 | frontmatter depends_on | ✅ |
| §11 产出物 | §-1 施工序列产出物 | ✅ |
| §12 集成目标 | 见基线蓝图 §七 | 基线覆盖 |
| §13 需要更新 | §-1 迁移路径 | ✅ |
| §14 风险 | §-2 各缺口风险（含"类型"列：风险/负面后果） | ✅ |
| §15 后果 | 已删除→正面在§1，负面在§14 | v3.6删除 |
| §16 施工指引 | §-1 施工序列 | ✅ |
| §17 容量升级 | **本文件主体** | ✅ |
| §18 决策记录 | 见基线蓝图 §三 | 基线覆盖 |
| 治理信息 | 见文件末尾 | ✅ |

---

## §-2 蓝图设计升级方案 — MOD-MASTER_BLUEPRINT v1.0.0 → v1.1.0 容量二次审计

> **阅读指南**：本章是施工前的必读前置章节。读完本章 → 向下滚动到"容量升级总蓝图"十个升级章（v1.0.0 新增设计）→ 继续向下到 §零起（v0.9.2 现存 37 节集成治理体系）。施工时参考本缺口清单逐项落地。

---

## -2.1 容量审计总结论

| 维度 | v1.0.0 十个升级章覆盖度 | 是否可以支撑目标规模 | 结论 |
|------|-----------|:---:|------|
| **脚本增量扫描** | 升级章二：Change→Script DAG ✅ | ✅ 方向正确 | Impact graph 设计完备——缺的是与 Gate Engine 的运行时段耦合 |
| **多AI并发** | 升级章三：ConcurrencyLicense + Agent Session ✅ | ✅ 框架完备 | 80 slot 许可证是正确模型 |
| **脚本执行吞吐** | 升级章五：SubprocessPool 动态扩缩 ✅ | ✅ 框架完备 | 四池 + min/max 动态扩缩方向对 |
| **容量调度** | 升级章六：Capacity-Aware Scheduler ✅ | ⚠️ 部分缺失 | 四级优先级队列有，但缺与升级章三 License 池的联合调度 |
| **注册与发现** | 升级章四：自动发现 + SQLite 索引 ✅ | ⚠️ 部分缺失 | 覆盖了模块/脚本注册，但缺**蓝图注册表**本身的缩放设计 |
| **可观测性** | 升级章七：事件驱动 + 分级采集 ✅ | ⚠️ 部分缺失 | 指标定义有，缺**容量预测**和**数字孪生** |
| **水平扩展** | 升级章八：多机分片预留 ✅ | ✅ 方向正确 | 预留设计完备 |
| **迁移路径** | 升级章九：4 phase 渐进迁移 ✅ | ✅ 方向正确 | 阶段性验证策略正确 |
| **模块间依赖** | ❌ 未覆盖 | ❌ 缺失 | 升级章二覆盖 file→script，但 1,500 模块间的 module→module 依赖图谱完全空白 |
| **蓝图体系缩放** | ❌ 未覆盖 | ❌ 缺失 | 1,500 个模块蓝图的注册、索引、一致性校验无设计 |
| **知识库缩放** | ❌ 未覆盖 | ❌ 缺失 | ChromaDB 10M 向量下的查询性能、索引管理无设计 |
| **上下文引擎缩放** | ❌ 未覆盖 | ❌ 缺失 | 1,500 蓝图时 CE 如何选择性注入——token 预算内精准命中无设计 |
| **脚本生命周期** | ❌ 未覆盖 | ❌ 缺失 | 10,000 脚本的版本化、废弃、归档、质量分级无设计 |
| **跨系统事务** | ❌ 未覆盖 | ❌ 缺失 | Orc + Script + Gate + DB 四系统的原子性操作无保障 |
| **契约演化** | ❌ 未覆盖 | ❌ 缺失 | 54→可能 100+ CT-* 契约的版本管理无设计 |
| **系统冷启动** | ❌ 未覆盖 | ❌ 缺失 | 12 系统 + 10,000 脚本的启动顺序和超时预算无设计 |
| **LLM 成本模型** | ❌ 未覆盖 | ❌ 缺失 | 100 AI 同时消耗 token 的成本追踪和预算硬强制无设计 |

---

## -2.2 缺口全景 — 12 项 v1.0.0 设计缺失

### -2.2.1 缺口分类总表

| # | 缺口名称 | 严重度 | v1.0.0 升级章覆盖 | 缺失什么 |
|---|---------|:---:|:---:|---------|
| GAP-M01 | **模块间依赖图谱（Module→Module DAG）** | 🔴 P0 | 升级章二有 file→script DAG，但无 module→module | 模块 A 的 API 变更→影响哪些其他模块？1,500 模块间依赖不可手工维护 |
| GAP-M02 | **蓝图注册表缩放（1,500 蓝图索引）** | 🔴 P0 | 升级章四有模块/脚本自动发现，但缺蓝图注册表本身的缩放 | blueprint_registry.yaml 现在已有 38 条，1,500 条如何管理？索引、缓存、分片？ |
| GAP-M03 | **知识库大规模查询性能保障** | 🔴 P0 | 完全缺失——升级章未涉及 KB/VMS 缩放 | ChromaDB 10M 向量→查询延迟、索引策略、collection 分区 |
| GAP-M04 | **上下文引擎大规模选择性注入** | 🔴 P0 | 完全缺失——升级章未涉及 CE 缩放 | 1,500 蓝图→CE 如何在 20K token 预算内精准注入相关蓝图？ |
| GAP-M05 | **治理脚本生命周期管理** | 🟡 P1 | 完全缺失 | 10,000 脚本的版本化、废弃标记、归档策略、质量分级（S0-S3） |
| GAP-M06 | **系统级冷启动与依赖编排** | 🟡 P1 | 完全缺失 | 12 系统 + 10,000 脚本→启动顺序 DAG + 启动超时预算 + 可用性探针链 |
| GAP-M07 | **LLM API 成本模型与预算硬强制** | 🟡 P1 | 升级章一提到 token 预算 2M，但无成本追踪 | 100 AI→每月 LLM API 费用？预算超支硬阻断？成本归因到模块/Agent？ |
| GAP-M08 | **蓝图自身体系膨胀管控** | 🟡 P1 | 完全缺失 | MOD-MASTER_BLUEPRINT 本身已 ~4000 行，1,500 模块后多长？分章策略？自动摘要？ |
| GAP-M09 | **跨系统操作事务一致性** | 🟡 P1 | 完全缺失 | Orc 创建任务 + Gate 评估 + Script 执行 + DB 写入→四者需要原子性保障 |
| GAP-M10 | **容量数字孪生与预测** | 🟢 P2 | 升级章七有实时监控，但无预测 | 在模块数到达 800 之前，能否预测 1,500 时的瓶颈？需要仿真模型 |
| GAP-M11 | **契约版本化与演化管理** | 🟢 P2 | 完全缺失 | 63 CT-* 契约已定义，1,500 模块后可能 100+ 契约→semver + 废弃流程 |
| GAP-M12 | **多AI输出质量一致性审计** | 🟢 P2 | 完全缺失 | 100 AI 产出代码→风格一致性？跨 session 设计一致性？需要自动化审计 |

---

## -2.3 缺口逐一设计

### GAP-M01：模块间依赖图谱（Module→Module DAG）🔴 P0

**问题场景**：
```
T=0: AI 修改 module_A 的公开 API（__init__.py 导出接口）
T=1: module_B/C/D（依赖 module_A）的治理脚本全部失效但没人知道
T=2: 三天后 module_B 的增量扫描才暴露问题——但已与 module_A 的变更脱节
→ 1,500 模块时，这种级联影响将频繁发生且难以追溯
```

**当前状态**：升级章二定义了 file→script 的 Impact Graph，但完全未涉及 module→module 级别的依赖关系。升级章四的自动发现只扫描模块存在性，不分析模块间依赖。

**设计**：

```yaml
contract: CT-MODULE-DEPS-001
title: "模块间依赖图谱——1,500模块级联影响分析"
owner: MOD-MASTER_BLUEPRINT
status: NEW
priority: P0

module_dependency_graph:
  storage: "SQLite 表 `module_deps` + 内存邻接表"
  vertices: "1,500 模块节点——每个模块一个 node_id"

  edge_types:
    IMPORT_DEPENDS:
      detection: "Python AST 静态分析——src/zephyr/ 下所有 .py 文件的 import 语句"
      semantics: "模块 A import 了模块 B → B 的 API 变更影响 A"
      weight: 1.0
      count_estimate: "1,500 模块 × 平均 3 个模块内 import = ~4,500 边"

    BLUEPRINT_DEPENDS:
      detection: "解析每个 blueprint.md 的 depends_on 字段"
      semantics: "蓝图 A 声明依赖蓝图 B → 逻辑依赖"
      weight: 0.8
      count_estimate: "1,500 模块 × 平均 2 依赖 = ~3,000 边"

    SCRIPT_DEPENDS:
      detection: "从升级章二的 impact_graph 反向推导——脚本 S 关联模块 A 和 B → 间接模块依赖"
      semantics: "模块 A 和 B 被同一脚本覆盖 → 脚本执行时两者必须一致"
      weight: 0.5
      count_estimate: "~10,000 边（从 impact_graph 聚合）"

  query_interface:
    affected_modules:
      input: "list[changed_module_id]"
      output: "list[(module_id, impact_weight, distance, affected_scripts_count)]"
      algorithm: |
        1. 从变更模块出发 BFS/DFS 遍历 module_deps 图
        2. 限制深度 ≤ 3（超过 3 层间接依赖→人工判断）
        3. 对每个受影响模块→查升级章二的 impact_graph→得到受影响的脚本数
        4. 按 impact_weight × distance × affected_scripts 排序
      latency_target: "< 100ms（内存邻接表）+ < 500ms（含 impact_graph 交叉查询）"

  integration_with_gate_engine:
    trigger: "任一模块蓝图 approval 或 src/ 目录 __init__.py 变更"
    action: "G0 任务准入时→自动查询 affected_modules →
            若受影响模块的 affected_scripts > 0 → Gate 判定 WARN →
            提示 AI:'你的变更影响 {n} 个其他模块的 {m} 个治理脚本——建议先跑 {module_list} 的增量扫描'"

  build_strategy:
    full_rebuild: "每日 03:00 全量重建（与升级章二 impact_graph 同步）"
    incremental: "模块新增/删除/__init__.py 变更时→增量更新该模块的出入边"
    auto_discovery: "升级章四的 ModuleOnboardingScanner 新发现模块 → 立即分析其 import 依赖 → 插入 module_deps"
```

---

### GAP-M02：蓝图注册表缩放（1,500 蓝图索引）🔴 P0

**问题场景**：
```
当前 blueprint_registry.yaml：38 条注册记录，手工维护
1,500 模块后：
- 单个 YAML 文件 ~8MB——Git 每次变更都重写整个文件
- AI session 读取注册表→注入全部 1,500 条→token 预算爆炸
- 注册表与 1,500 个蓝图文件的一致性校验→O(1,500) 扫描
```

**当前状态**：升级章四覆盖了模块/脚本的自动发现→SQLite 索引，但 `blueprint_registry.yaml` 本身的缩放完全没有设计。

**设计**：

```yaml
contract: CT-BLUEPRINT-REGISTRY-002
title: "蓝图注册表 v2.0——1,500 蓝图的分片索引与一致性保障"
status: UPGRADE
priority: P0

blueprint_registry_v2:
  storage_backend: "SQLite `blueprint_index` 表 + 每日 YAML 导出（人类可读快照）"
  migration: "当前 blueprint_registry.yaml → 导入 SQLite → YAML 保留为只读历史快照"

  sqlite_schema:
    blueprint_index:
      columns:
        - module_id: "TEXT PK"
        - file_path: "TEXT UNIQUE NOT NULL"
        - title: "TEXT"
        - version: "TEXT"
        - status: "TEXT"           # Active | Draft | Deprecated | Archived
        - layer: "TEXT"
        - priority: "TEXT"         # P0 | P1 | P2
        - last_updated: "TEXT"
        - blueprint_hash: "TEXT"   # SHA-256 of the blueprint.md content
        - depends_on: "JSON"       # ["MOD-INF-005", "MOD-KB-001", ...]
        - tags: "JSON"
        - construction_progress: "TEXT"
        - completeness_score: "REAL"  # 蓝图完备度评分 (0.0-1.0)
      indexes:
        - "idx_blueprint_layer ON blueprint_index(layer)"
        - "idx_blueprint_status ON blueprint_index(status)"
        - "idx_blueprint_priority ON blueprint_index(priority)"

    blueprint_reconciliation_log:
      columns:
        - check_time: "TEXT PK"     # ISO8601
        - module_id: "TEXT PK"
        - registry_hash: "TEXT"
        - actual_file_hash: "TEXT"
        - drift_detected: "BOOLEAN"
        - resolution: "TEXT"        # AUTO_FIXED | MANUAL | PENDING

  auto_indexing:
    scanner: "BlueprintAutoIndexer——继承升级章四的 ModuleOnboardingScanner"
    trigger: ["新 blueprint.md 创建", "blueprint.md 内容变更（SHA-256 变化）"]
    action: |
      1. 解析 blueprint.md 的 YAML frontmatter
      2. 提取所有字段→写入/更新 blueprint_index 行
      3. 计算 completeness_score（基于 depends_on 引用的蓝图是否存在）
      4. 每日 02:00 全量校验——遍历 docs/03_modules/ 下所有 blueprint.md
         → 对比 blueprint_index → 写入 reconciliation_log

  query_interface:
    by_layer: "SELECT * FROM blueprint_index WHERE layer = ? AND status != 'Archived'"
    by_dependency: |
      WITH RECURSIVE dep_chain AS (
        SELECT module_id, depends_on FROM blueprint_index WHERE module_id = ?
        UNION ALL
        SELECT b.module_id, b.depends_on
        FROM blueprint_index b JOIN dep_chain d
        ON b.module_id IN (SELECT value FROM json_each(d.depends_on))
      )
      SELECT DISTINCT module_id FROM dep_chain
    by_completeness: "SELECT * FROM blueprint_index WHERE completeness_score < 0.5 ORDER BY completeness_score ASC"

  per_layer_sharding:
    trigger: "blueprint_index 单表行数 > 500 → 启用 layer-level 分表"
    tables: "blueprint_idx_{layer}——每个 C-track 层一张表"
    cross_layer: "blueprint_idx_cross_layer——_cross_layer/ 和 _master_blueprint/ 共用"
    benefits: "减少单表行数 → 查询延迟降低 → WAL 写入竞争降低"

  consistency_guarantees:
    daily_reconciliation: "每日 02:00 自动对账——发现不一致 → P2 Finding"
    stale_detection: "blueprint_index.last_updated < 30d ago AND status='Active' → 蓝图可能僵尸化 → P1 告警"
    orphan_detection: "blueprint_index 中有条目但对应 blueprint.md 文件不存在 → P0 告警（注册表被篡改或文件误删）"
```

---

### GAP-M03：知识库大规模查询性能保障 🔴 P0

**问题场景**：
```
1,500 模块 × 每个模块 200 条 KE = 300,000 条 KE
每条 KE embedding = 1024d BGE-M3 → 10M vectors in ChromaDB
当前 ChromaDB 单 collection 1M 上限在 v1.0.0 设计里已经提到→需要 10M
但查询性能呢？
- 全量相似度搜索 10M vectors：~500ms（当前 1M = ~50ms）
- 10 个 AI 同时查询→SQLite 锁竞争 + ChromaDB HNSW 索引竞争
- 每次 CE build 需要查 50 条相关 KE→10M 中找 Top-K
```

**当前状态**：v1.0.0 升级章一提到 ChromaDB 10M vectors，但没有任何关于查询性能保障的设计。CT-KB-VMS-001 目前是 CAUTION_STUB。

**设计**：

```yaml
contract: CT-KB-SCALE-001
title: "知识库大规模查询性能保障——10M vectors 下的延迟 SLO"
status: NEW
priority: P0

kb_scaling:
  indexing_strategy:
    hnsw_parameters:
      M: 64               # HNSW 每个节点的最大连接数（默认 16→10M 需 64）
      ef_construction: 200 # 构建时搜索深度
      ef_search: 100       # 查询时搜索深度
    index_type: "HNSW（内存） + SQLite metadata（磁盘）"
    build_time: "10M vectors × 1024d → ~30min 初始构建（一次性）"
    memory_estimate: "10M × 1024d × 4 bytes(float32) = ~40GB + HNSW 索引 ~8GB = ~48GB（超出 64GB 单机内存预算）"

  partitioning:
    trigger: "单 collection > 2M vectors → 按 layer 分区"
    partitions:
      - "kb_partition_l00_l03: 数据源 + 信号层 KE（预估 2M vectors）"
      - "kb_partition_l04_l08: 风控 + 执行 + 组合层 KE（预估 3M vectors）"
      - "kb_partition_l09_l15: 展示 + 安全 + 运维层 KE（预估 2M vectors）"
      - "kb_partition_infra: 12 系统运维 KE + 蓝图 KE（预估 3M vectors）"
    partition_router: |
      CE build 时根据 task.target_layer → 路由到对应 partition
      跨层任务 → 最多查询 2 个 partition（延迟 ×2 可接受）
    memory_per_partition: "~12GB——可接受（64GB 总内存的 19%）"

  query_optimization:
    metadata_prefilter: |
      查询前先用 SQLite metadata 缩小候选集：
        1. layer ∈ {target_layer, adjacent_layers}
        2. ke_type ∈ {BLUEPRINT, FINDING, DECISION, KNOWLEDGE}
        3. freshness_score > 0.3（排除过期 KE）
      候选集从 10M 缩小到 ~500K → 再 embedding search
    hybrid_search:
      keyword_filter: "SQLite FTS5 全文索引预筛选 → 缩小到 10K → embedding search"
      embedding_search: "在 10K 候选集上做精确相似度 → 返回 Top-K"
    cache:
      l1: "LRU 内存缓存——最近 1,000 次查询结果（key=query_hash + target_layer）"
      l2: "SQLite query_cache 表——TTL=600s"
      hit_ratio_target: "> 50%（同一 target_layer 的查询高度重复）"

  slo:
    single_query_p50: "< 100ms"
    single_query_p99: "< 500ms"
    concurrent_10_queries_p99: "< 1000ms"
    index_refresh_interval: "每 100 条新 KE → 触发增量索引更新（非全量重建）"
```

---

### GAP-M04：上下文引擎大规模选择性注入 🔴 P0

**问题场景**：
```
1,500 模块蓝图：每个 blueprint.md ~3,000-15,000 tokens
如果 CE 注入所有相关蓝图→远超 20K token 预算
当前 v0.9.2 §五："单次 session 蓝图注入数 ≤ 5 blueprints"
但 1,500 模块时，target_layer 内就有 ~107 个模块蓝图
→ 选哪 5 个？按什么标准选？
```

**当前状态**：v1.0.0 升级章提到 `token_budget_per_session: 20000`，但未设计 1,500 蓝图场景下 CE 如何做选择性注入。v0.9.2 §五的"按 target_layer 相关性排序"是模糊指令。

**设计**：

```yaml
contract: CT-CE-SCALE-001
title: "上下文引擎选择性注入——1,500 蓝图下的精准上下文构建"
status: NEW
priority: P0

ce_selective_injection:
  blueprint_relevance_scoring:
    factors:
      - factor: layer_match
        weight: 0.30
        description: "蓝图的 layer == task.target_layer → 满分；相邻层 → 0.5；跨层 → 0.1"

      - factor: dependency_closure
        weight: 0.25
        description: "task.related_files 所属模块的依赖链上所有模块蓝图→分数随距离衰减"
        source: "GAP-M01 module_deps 表"

      - factor: script_governance
        weight: 0.20
        description: "task.related_files 触发的脚本所属模块的蓝图→需了解为何这些脚本要跑"
        source: "升级章二 impact_graph"

      - factor: recency
        weight: 0.10
        description: "最近被读取/更新的蓝图优先→热度加权"

      - factor: maturity_context
        weight: 0.15
        description: "M1/M2 模块施工时需要更多蓝图（规范+参考）→ M3/M4 只需目标蓝图"
        source: "§十五 M1-M4 成熟度定义"

    scoring_formula: |
      relevance_score = Σ(weight_i × factor_score_i)
      分数归一化到 [0, 1]
      取 top_k 蓝图注入——k 由剩余 token 预算决定

  blueprint_tiering:
    tiers:
      tier_0_full: "完整 blueprint.md 全文注入——仅限 task.target_module 的蓝图（必注入）"
      tier_1_summary: "注入 blueprint.md 的 summary 字段 + depends_on 列表 + §优先章节——相邻层依赖模块"
      tier_2_header: "仅注入 YAML frontmatter（module_id + title + status + depends_on）——间接依赖模块"
      tier_3_skip: "不注入——score < 0.3 的模块（跨层无关联）"

  token_budget_allocator:
    total_budget: 20000
    allocation:
      task_card: "固定 500 tokens"
      rules_and_policies: "固定 1500 tokens"
      target_blueprint_tier0: "动态——至少保留 5000 tokens"
      dependency_blueprints_tier1: "动态——至少保留 3000 tokens"
      context_blueprints_tier2: "动态——至少保留 1000 tokens"
      kb_results: "动态——剩余预算全部给 KE"
      safety_margin: "500 tokens 预留"
    eviction: "预算不足时→先降级 tier1→tier2→最后缩减 tier0（仅删示例代码保留核心声明）"

  injection_format:
    structured: |
      每个注入的蓝图包裹在 `<blueprint module_id="X" tier="Y">...</blueprint>` 标签中
      → AI 明确知道这些内容的来源和可信度
      → 跨 blueprint 引用时可通过 module_id 精确定位
    header_metadata: |
      注入前附加元数据行：
      `[BLUEPRINT: MOD-INF-005 | tier:0 | score:0.95 | hash:abc123]`
      → AI 可据此判断信息的时效性和完整性

  feedback_loop:
    injection_effectiveness:
      metric: "注入的蓝图被 AI 在 session 中实际引用的比例"
      target: "> 60% 的注入 token 被引用"
      optimization: "连续 10 个 session 引用率 < 50% → 调整 relevance_scoring 权重"
```

---

### GAP-M05：治理脚本生命周期管理 🟡 P1

**问题场景**：
```
10,000 脚本：
- 哪些脚本已被淘汰但未删除？（死脚本）
- 哪些脚本是实验性的不该在生产中跑？（标记缺失）
- 脚本 v1 和 v2 同时存在→AI 不知道用哪个
- 脚本质量如何分级？所有脚本同等对待→长尾脚本拖慢一切
```

**当前状态**：升级章二有 script_manifest，升级章四有 ScriptAutoIndexer，但都只覆盖脚本的"注册"——不覆盖"生命周期"。

**设计**：

```yaml
contract: CT-SCRIPT-LIFECYCLE-001
title: "治理脚本生命周期管理——10,000 脚本的版本化、废弃、质量分级"
status: NEW
priority: P1

script_lifecycle:
  states:
    EXPERIMENTAL:
      description: "新创建的脚本——仅运行在 shadow 模式（不阻断，只记录）"
      duration: "≥ 10 次执行 AND ≥ 7 天 → 自动晋升为 STABLE"
      gate_behavior: "G7 WARN（不阻断）"

    STABLE:
      description: "已验证的脚本——正常参与门禁判定"
      gate_behavior: "正常执行——exit 0/1/2/3 按门禁契约"

    DEPRECATED:
      description: "计划废弃的脚本——仍运行但 AI 收到提醒"
      trigger: "连续 30 天零触发 OR Owner 显式标记"
      gate_behavior: "exit code 降权——0→WARN, 1→FAIL(可被下一个STABLE脚本覆盖)"
      migration_hint: "提示 AI：'{successor_script_path}' 替代了此脚本"

    ARCHIVED:
      description: "已废弃——不运行，仅保留源码供参考"
      trigger: "DEPRECATED 状态 > 90 天 → 自动归档"
      gate_behavior: "跳过——不计入门禁评估"
      retention: "源码保留在 scripts/governance/_archived/ + 历史执行记录保留 365 天"

  quality_grading:
    S0_instant:
      criteria: "P50 执行时间 < 10s AND 近 100 次执行 FAIL 率 < 1%"
      pool: "quick 池——最高优先级"

    S1_fast:
      criteria: "P50 执行时间 10-60s AND FAIL 率 < 3%"
      pool: "quick 池"

    S2_medium:
      criteria: "P50 执行时间 60-180s AND FAIL 率 < 5%"
      pool: "long_tail 池（参考 Gate Engine GAP-C07）"

    S3_heavy:
      criteria: "P50 执行时间 > 180s OR FAIL 率 > 5%"
      pool: "disruptive 池——需 Owner 审批"
      review_required: "每月自动生成 S3 脚本优化建议"

  versioning:
    format: "{script_name}_v{major}.{minor}.py"
    major_bump: "exit code 语义变更 OR depends_on 结构变更"
    minor_bump: "内部逻辑优化——不影响外部契约"
    co_existence: "v1 和 v2 可同时注册→v1 标记 DEPRECATED→90 天后 ARCHIVED"
    rollback: "v2 连续 10 次 FAIL → 自动回退到 v1 STABLE + P1 告警"

  dead_script_detection:
    trigger: "script_manifest 条目连续 90 天零执行"
    action: "自动标记 DEPRECATED + 通知 Owner → 30 天后无异议 → ARCHIVED"
    exception: "标注 `keep_forever: true` 的脚本永不过期（框架核心脚本）"
```

---

### GAP-M06：系统级冷启动与依赖编排 🟡 P1

**问题场景**：
```
ZephyrAlpha 启动：
- 12 个系统以什么顺序启动？
- Gate Engine 启动需要 DependencyGraph（依赖 Script System 的 script_manifest）
- Script System 启动需要 Gate Engine 的健康检查（循环依赖！）
- DB 必须先于所有系统启动
- 10,000 脚本的索引预热需要多久？
- 总冷启动时间预算？超时怎么办？
```

**当前状态**：CT-STARTUP-001 在 v0.9.2 中定义为 `DO_NOT_CALL`——冷启动协议完全空白。

**设计**：

```yaml
contract: CT-STARTUP-002
title: "系统级冷启动编排——12 系统的启动 DAG + 10,000 脚本预热预算"
status: UPGRADE
priority: P1

startup_dag:
  tiers:
    tier_0_bare_metal:  # 无依赖——最先启动
      - {system: Database, timeout_s: 5, description: "SQLite 连接池 + WAL 启用"}
      - {system: MCP_Servers, timeout_s: 10, description: "stdio 服务启动——先于任何业务系统"}

    tier_1_core:  # 依赖 tier_0
      - {system: Vector_Memory, timeout_s: 15, depends_on: [Database], description: "ChromaDB 初始化 + collection 加载"}
      - {system: LLM_Security, timeout_s: 5, depends_on: [], description: "安全策略加载——无数据依赖"}
      - {system: System_Telemetry, timeout_s: 5, depends_on: [Database], description: "metrics 端点注册"}

    tier_2_engines:  # 依赖 tier_1
      - {system: Knowledge_Base, timeout_s: 20, depends_on: [Vector_Memory, Database]}
      - {system: Script_System, timeout_s: 30, depends_on: [Database], description: "script_manifest 加载 + 脚本索引预热"}
      - {system: Context_Engine, timeout_s: 15, depends_on: [Knowledge_Base, Vector_Memory]}

    tier_3_business:  # 依赖 tier_2
      - {system: Gate_Engine, timeout_s: 10, depends_on: [Script_System, Database],
         description: "冷启动协议 phase_0→phase_2（参考 Gate Engine GAP-C01）"}
      - {system: Task_Pipeline, timeout_s: 10, depends_on: [Context_Engine]}
      - {system: Feedback_Loop, timeout_s: 15, depends_on: [System_Telemetry, Database]}

    tier_4_front:  # 依赖 tier_3
      - {system: Orchestrator, timeout_s: 20, depends_on: [Gate_Engine, Task_Pipeline, Context_Engine, Script_System, Knowledge_Base]}

  total_startup_budget:
    tier_0: "max(5,10) = 15s（DB + MCP 并行）"
    tier_1: "max(15,5,5) = 15s（VMS + LSG + Telemetry 并行）"
    tier_2: "max(20,30,15) = 30s（KB + Script + CE 并行）"
    tier_3: "max(10,10,15) = 15s（Gate + Pipeline + FLE 并行）"
    tier_4: "20s（Orc 串行——依赖 tier_3 全部）"
    total: "~95s"  # < 2 分钟总冷启动时间
    hard_timeout: 180s  # 3 分钟硬超时→任一 tier 超时→尝试降级启动

  pre_warming:
    dependency_graph: "Script System 启动后后台异步构建（不阻塞 Orc 的就绪状态）"
    blueprint_index: "BlueprintAutoIndexer 全量扫描→SQLite（~30s，后台执行）"
    kb_vectors: "ChromaDB collection 延迟加载——首次查询时才加载 HNSW 索引"

  circular_dependency_resolution:
    problem: "Gate Engine 需要 Script System 的 manifest，Script System 的治理脚本需要 Gate Engine 判定"
    resolution: |
      启动时：Script System 先于 Gate Engine 启动
      Script System 启动后→先加载本地缓存的 script_manifest→不依赖 Gate
      Gate Engine 启动后→从 Script System 的 manifest 缓存重建 DependencyGraph
      运行时：两者通过 CT-SCRIPT-GATE-001 契约交互→不存在启动循环

  health_probe_chain:
    endpoint: "GET /health/readyz——系统级聚合就绪探针"
    logic: |
      Orchestrator 聚合所有系统→任意 tier_4 系统未就绪→返回 503
      前端（IDE/Agent）等待 readyz 返回 200 后才开始提交任务
    degraded_start: |
      若 tier_2 中 Script System 未就绪但其他就绪 →
      返回 200_degraded：'script_system: warming_up; other_systems: ready'
      → AI 可提交非治理任务（知识查询、文档编写等）
```

---

### GAP-M07：LLM API 成本模型与预算硬强制 🟡 P1

**问题场景**：
```
100 AI 同时工作：
- 每个 AI 每 session 消耗 ~20K tokens
- 每天 10 session × 100 AI = 20M tokens/day
- API 价格（qwen3:8b 本地）= 零，但外部模型（如 deepseek）≈ ¥2/1M tokens
- 如果 AI 错误使用了外部昂贵模型→¥40/day→¥1200/month
- 没有成本追踪→不知道钱花在哪→无法预算管控
```

**当前状态**：v1.0.0 升级章一提到 token 预算 2M 全局 + 20K/session，但没有成本追踪。v0.9.2 有 CT-COST-BUDGET-001（DO_NOT_CALL）。

**设计**：

```yaml
contract: CT-COST-BUDGET-002
title: "LLM API 成本模型与预算硬强制——100 AI 的财务管控"
status: UPGRADE
priority: P1

cost_model:
  backends:
    local_qwen3_8b:
      cost_per_1k_tokens: 0.0     # 本地模型免费
      rate_limit: "无限制（受 GPU VRAM 限制）"
      preference: "默认选择——除非任务复杂度 > M3"

    external_deepseek:
      cost_per_1M_input_tokens: 2.0   # ¥2/1M input
      cost_per_1M_output_tokens: 8.0  # ¥8/1M output
      rate_limit: "200K tokens/min"
      use_case: "仅限 M3/M4 模块的复杂分析任务"
      require_approval: "单次 > 50K tokens → 需 Owner 确认"

    external_claude:
      cost_per_1M_input_tokens: 15.0
      cost_per_1M_output_tokens: 75.0
      rate_limit: "50K tokens/min"
      use_case: "仅限 M4 模块的最终代码审查归档"
      require_approval: "任何时候都需 Owner 确认"

  budget_enforcement:
    monthly_budget: 500.0  # ¥500/月硬上限
    weekly_budget: 150.0   # ¥150/周软上限（超过→P1 告警，不硬阻断）
    daily_budget: 30.0     # ¥30/天硬上限

    enforcement:
      daily_exceeded: "硬阻断外部模型调用→降级为本地模型→通知 Owner"
      weekly_exceeded: "P1 告警 + 暂停所有外部模型→仅本地模型可用"
      monthly_exceeded: "P0 告警 + 全部外部模型永久拒绝直到 Owner 手动恢复"

  cost_attribution:
    tracking:
      per_agent: "每个 AI session 的 token 消耗按 agent_session_id 归因"
      per_module: "按 task.target_module 归因→哪些模块最烧钱"
      per_task_type: "MODEL_BUILD vs AUDIT vs REFACTOR 的成本对比"

    dashboard:
      real_time: "当前小时的成本 burn rate + 今日累计"
      trends: "7天/30天成本趋势→识别异常增长"
      cost_efficiency: "¥/有效代码行数（需 B-MOD-307 Token 产出度量配合）"

  model_selection_rules:
    auto_select:
      M1_module: "always local_qwen3_8b"
      M2_module: "local_qwen3_8b (90%) / external_deepseek (10%)"
      M3_module: "local_qwen3_8b (70%) / external_deepseek (30%)"
      M4_module: "external_deepseek (80%) / external_claude (20%)"
    override: "AI 可提议使用更高级模型→需 Gate Engine G5（决策门禁）评估批准"
```

---

### GAP-M08：蓝图自身体系膨胀管控 🟡 P1

**问题场景**：
```
MOD-MASTER_BLUEPRINT 当前版本：~4,000 行 / ~150KB
1,500 模块后：
- 升级章 + §-2 容量二次审计 + 章一~三十七 = 预估 ~8,000 行
- AI session 冷启动读 §零分派表→需要遍历全文结构
- 蓝图变更 Git diff 巨大→Code Review 困难
- 本蓝图自身也需要一致性校验（谁校验总蓝图？）
```

**当前状态**：v0.9.2 §三十四有 CT-BLUEPRINT-HEALTH-001 蓝图自健康诊断，但那是针对模块蓝图的——不是针对 MOD-MASTER_BLUEPRINT 自身的。

**设计**：

```yaml
contract: CT-MASTER-BLUEPRINT-HEALTH-001
title: "MOD-MASTER_BLUEPRINT 自身健康诊断——总蓝图的缩放管控"
status: NEW
priority: P1

master_blueprint_governance:
  size_limits:
    max_total_lines: 6000        # 超过→P1 告警→需考虑分拆
    max_single_section_lines: 500 # 单节超过→P2 建议拆分
    current: "~4000 行——v1.0.0 升级章新增 ~600 行，§-2 新增 ~800 行"
    projected_v1_1: "~5500 行——仍在限制内"

  chapter_management:
    structure:
      §-2: "容量二次审计（本章）——容量缺口清单"
      §升级章一~十: "v1.0.0 新增设计——核心容量架构"
      §零~三十七: "v0.9.2 现存设计——集成契约与治理体系"

    auto_toc: |
      每次蓝图更新后自动生成目录树→写入本文件头部（YAML frontmatter 后）
      AI session 冷启动时→先读目录树→再按需跳转→节省 token

  self_integrity:
    depends_on_self_check: |
      本蓝图的 depends_on 列表中引用了 16 个外部文件
      每日自动验证这些文件是否存在 + 内容未漂移
      方法：本蓝图 SHA-256 × 所有 depends_on 文件 SHA-256 = 完整性指纹

    cross_reference_validator: |
      本蓝图中所有 "详见 §X" 引用→自动验证 §X 确实存在
      本蓝图中所有 CT-* 契约编号→自动验证在 §二契约总表中已登记

  split_threshold:
    condition: "MOD-MASTER_BLUEPRINT > 8000 行 OR 单节 > 800 行"
    action: |
      拆分方案：
        MOD-MASTER_BLUEPRINT: 保留 frontmatter + §-2 + 升级章 + §零~§十二（核心集成契约）
        MOD-MASTER-002: §十三~§二十五（可观测性 + 健康检查 + CDC + 部署）
        MOD-MASTER-003: §二十六~§三十七（高级治理 + 盲点审计）
      三个蓝图通过 depends_on 链保持集成一致性
      拆分后：每个蓝图 < 4000 行 → AI session 冷启动成本降低
```

---

### GAP-M09：跨系统操作事务一致性 🟡 P1

**问题场景**：
```
Orc 创建任务→Gate 评估→Script 执行→DB 写入 Finding
这四个操作分属四个系统——如果第 3 步失败：
- 任务已创建（Orc）
- 门禁已评估（Gate）
- 脚本执行崩溃（Script）
- Finding 未写入（DB）
→ 系统状态不一致：任务存在但没有对应 Finding
→ 1,500 模块时这种不一致会快速累积
```

**当前状态**：v0.9.2 有 CT-ORC-DB（SAFE）作为 DB 事务层，但没有跨系统的分布式事务设计。

**设计**：

```yaml
contract: CT-TRANSACTION-001
title: "跨系统操作事务一致性——Saga 模式的轻量实现"
status: NEW
priority: P1

cross_system_transaction:
  model: "Saga（补偿事务）——不要求 ACID，要求最终一致性"
  rationale: |
    12 系统跨 4 个 SQLite 文件→无法用单一数据库事务
    Saga 模式：每个步骤有一个对应的补偿操作（compensating action）
    步骤失败→执行已成功步骤的补偿→回到一致状态

  task_lifecycle_saga:
    steps:
      step_1:
        system: Orchestrator
        action: "创建 TaskCard→status=TODO"
        compensation: "TaskCard→status=CANCELLED, reason='saga_rollback'"

      step_2:
        system: Gate_Engine
        action: "评估 G0-G7 门禁→判定 PASS/FAIL"
        compensation: "删除 GateEvaluation 记录（仅保留审计日志）"
        idempotency: "task_id 已评估过→返回缓存结果（不重复评估）"

      step_3:
        system: Script_System
        action: "执行治理脚本→收集 Findings"
        compensation: "标记 Findings 为 ROLLED_BACK（不删除——保留审计踪迹）"
        retry: "失败时最多重试 3 次→3 次后触发 saga 回滚"

      step_4:
        system: Database
        action: "写入 Findings + 更新 TaskCard.status→BLOCKED/COMPLETED"
        compensation: "回滚 TaskCard.status→TODO + Findings→ROLLED_BACK"

    saga_coordinator:
      location: "Orchestrator 内部的 SagaCoordinator 类"
      state_tracking: "SQLite `saga_state` 表——记录每个 saga 的当前步骤和状态"
      recovery:
        crash_during_saga: |
          Orchestrator 重启后扫描 saga_state 表中的 IN_PROGRESS saga
          → 从上次成功的步骤后重试
          → 最多重试 3 次→仍失败→P0 告警 + 人工介入

  isolation:
    conflict_detection: |
      两个 saga 同时操作同一个 task_id→第二个 saga 发现 task_id 已有 IN_PROGRESS saga
      → 返回 409 Conflict → 排队等待
    timeout: "单个 saga 最长执行时间 300s→超时触发回滚"
```

---

### GAP-M10：容量数字孪生与预测 🟢 P2

**问题场景**：
```
当前：模块数 51→升级章一预测 1,500 时资源够用（纸面推算）
问题：从 51→100→500→1000→1500 的过程中，瓶颈何时出现？
- 模块 800 时 DB 写入延迟开始飙升？
- 模块 1200 时 CE token 预算开始溢出？
这些需要预测——而不是等到真的出问题才发现。
```

**当前状态**：`src/zephyr/shared/capacity_digital_twin.py` 文件存在但内容未知。升级章七有实时监控但无预测。

**设计**：

```yaml
contract: CT-CAPACITY-TWIN-001
title: "容量数字孪生——从纸面推算到数据驱动的瓶颈预测"
status: NEW
priority: P2

capacity_digital_twin:
  model:
    type: "linear_regression_with_knee_detection"
    inputs:
      - module_count: "模块数（自变量）"
      - script_count: "脚本数（派生变量 = module_count × 6.7）"
      - ai_session_count: "并发 AI 数"
    predictions:
      - dep_graph_query_latency_p99: "随 script_count 增长→预计在 ~8000 脚本时触及 500ms SLO"
      - sqlite_write_contention_p99: "随 ai_session_count 增长→预计在 ~80 AI 时 WAL busy > 10%"
      - chromadb_query_latency_p99: "随 vector_count 增长→预计在 ~6M vectors 时需要分区"
      - ce_token_overflow_rate: "随 module_count 增长→预计在 ~1000 模块时 20K 预算不足"
      - memory_usage_gb: "线性增长→预计在 ~1200 模块时接近 64GB 上限"

  calibration:
    data_source: "历史容量指标（来自升级章七的 Prometheus metrics）"
    calibration_points: "[51, 100, 200, 400, 800] 模块规模时的实测数据"
    method: "用 51→400 的数据训练模型→预测 800 和 1500 的值→与实际对比→修正模型"

  early_warning:
    trigger: "预测值触及 SLO 阈值的 80% → P1 告警：'N 模块后将出现瓶颈'"
    action: "自动生成瓶颈缓解建议→通知 Owner→建议扩容/优化/分区"

  what_if_simulation:
    scenarios:
      - "如果 100 AI 同时跑全量扫描（非增量）→系统表现？"
      - "如果 ChromaDB 单 collection 不做分区→查询延迟曲线？"
      - "如果关闭脚本结果缓存→CPU 利用率曲线？"
    output: "交互式报告→JSON + 控制台可视化"
```

---

### GAP-M11：契约版本化与演化管理 🟢 P2

**问题场景**：
```
CT-* 契约从 54 条增长到可能的 100+ 条（1,500 模块后新系统接入）
- 契约变更是 breaking 还是 backward-compatible？不知道
- 消费方如何知道契约升级了？没有通知机制
- 契约废弃后如何平滑迁移？没有过渡期策略
```

**当前状态**：v0.9.2 的 CT-CDC-001（DO_NOT_CALL）覆盖了契约测试但未覆盖契约演化。

**设计**：

```yaml
contract: CT-CONTRACT-EVOLUTION-001
title: "集成契约版本化与演化管理——semver + deprecation window"
status: NEW
priority: P2

contract_versioning:
  format: "CT-{A}-{B}-v{major}.{minor}.{patch}"
  semver_rules:
    MAJOR: "breaking change——消费方 MUST 更新代码才能正常工作"
    MINOR: "backward-compatible 新增字段/功能——消费方可选升级"
    PATCH: "文档修正/示例更新——不影响契约语义"

  breaking_change_catalog:
    - "删除已有字段"
    - "修改字段类型（str→int）"
    - "修改枚举值集合（新增 OK，删除是 breaking）"
    - "修改 circuit_breaker 阈值（降低）"
    - "修改 ai_read_only_hint（SAFE→DO_NOT_CALL）"

  deprecation_policy:
    window: "MAJOR 版本前至少保留 1 个 MINOR 版本的过渡期"
    signaling: "旧版本标记 @deprecated——输出 WARNING 日志而非拒绝调用"
    migration_guide: "每条废弃契约附带 migration_guide 字段→消费方 AI 可直接执行迁移"

  consumer_notification:
    mechanism: "升级章四的 BlueprintAutoIndexer + depends_on 解析"
    flow: |
      1. 契约 A→B 版本升级
      2. 扫描所有蓝图→找到 depends_on 中包含契约 A→B 消费方的模块
      3. 自动创建 Finding: 'CONTRACT_UPGRADE_REQUIRED' → 分配给消费方模块 Owner
      4. CI 检查：消费方是否已适配新版本→未适配→WARN
```

---

### GAP-M12：多AI输出质量一致性审计 🟢 P2

**问题场景**：
```
100 AI 同时施工 1,500 模块：
- Agent #17 用 dataclass，Agent #23 用 NamedTuple
- Agent #5 的代码风格偏函数式，Agent #89 偏面向对象
- Agent #42 修复了 module_X 但修改了 module_Y 的全局状态
→ 没有跨 AI 输出质量一致性审计→代码库风格碎片化
```

**当前状态**：v0.9.2 §三十七 E 维度（氛围编程特有盲点）提到了跨 session 设计一致性，但未形成契约。

**设计**：

```yaml
contract: CT-AI-QUALITY-AUDIT-001
title: "多AI输出质量一致性审计——100 AI 的代码风格统一保障"
status: NEW
priority: P2

cross_ai_consistency:
  audit_dimensions:
    code_style:
      enforcement: "预提交 pre-commit hook——ruff + mypy + black 统一格式化"
      auto_fix: "CI 自动运行 black --check→不通过→拒绝 merge"

    architectural_pattern:
      detection: "AST 分析——检测是否使用项目禁止的模式"
      banned_patterns: ["直接 import 其他系统的内部模块（违反 AP1）", "裸 except:", "os.system()"]
      severity: "P0——直接阻断（GATE-18 pre-commit）"

    design_decision_consistency:
      mechanism: |
        每次 AI session 结束时→自动提取本 session 中做出的设计决策
        → 与同一模块的历史设计决策对比
        → 冲突检测：AI #42 的决策是否与 AI #17 3 天前的决策矛盾？
        → 矛盾则生成 DESIGN_CONFLICT Finding → 分配 Owner 裁决

    naming_convention:
      enforcement: "基于 AI 自动学习的项目命名约定（从现有代码中提取 pattern）"
      tolerance: "允许 5% 的新变异——防止过度僵化"

  audit_report:
    frequency: "每周自动生成 Cross-AI Consistency Report"
    content:
      - "本周 100 AI 产出的代码中："
      - "风格一致率（XX%——目标 > 90%）"
      - "设计决策冲突数（N 个——已解决 M 个）"
      - "Top 5 违规模式（最常出现的 Anti-Pattern）"
      - "质量趋势图（本周 vs 上周 vs 上月）"
```

---

## -2.4 新增设计决策（DD43-DD54）

> **时态属性**：决策记录属于**永久时态**——AI 修改设计时必读。没有它，AI 会重复犯已排除的错误。

| ID | 决策 | 理由 | 对应缺口 |
|----|------|------|:---:|
| DD43 | **模块依赖用 BFS depth≤3 而非全图遍历** | 超过 3 层间接依赖的影响已不可靠→应人工判断而非自动阻断 | GAP-M01 |
| DD44 | **蓝图注册表 SQLite 为主 + YAML 每日导出为快照，而非双写** | SQLite 是运行时真源，YAML 是人类可读归档——双写增加一致性风险 | GAP-M02 |
| DD45 | **KB 按 layer 分区而非按 ke_type 分区** | layer 是查询的首要过滤条件→跨 layer 查询少见→分区最有效 | GAP-M03 |
| DD46 | **CE 注入用 blueprint tiering（全文/摘要/头部），而非纯缩减** | 纯缩减丢失结构信息→tiering 保留语义层次 | GAP-M04 |
| DD47 | **脚本生命周期状态机 4 态而非 2 态（active/archived）** | EXPERIMENTAL + STABLE + DEPRECATED + ARCHIVED 提供渐进过渡→避免误删 | GAP-M05 |
| DD48 | **启动 DAG 用 tier 分层并行，而非全串行或全并行** | 全串行太慢（> 5min），全并行有循环依赖风险→分层并行是最优 | GAP-M06 |
| DD49 | **LLM 成本管控分层：daily 硬阻断 + weekly 软告警 + monthly 硬上限** | 单层阻断要么太松要么太严→分层提供渐进约束 | GAP-M07 |
| DD50 | **总蓝图自身 > 8000 行触发分拆而非永远加长** | AI 冷启动成本与蓝图长度线性相关→保持每个蓝图 < 4000 行 | GAP-M08 |
| DD51 | **跨系统事务用 Saga 补偿而非 2PC** | 2PC 需要协调者 100% 可用→Saga 允许最终一致性→更适合单机多 SQLite | GAP-M09 |
| DD52 | **数字孪生模型用线性回归 + knee detection，而非复杂 ML** | 容量曲线在该规模下近似线性→复杂 ML 过拟合且不可解释 | GAP-M10 |
| DD53 | **契约版本化用 semver 而非日期版本** | 日期版本无法传达 breaking change 信息→semver 是行业标准 | GAP-M11 |
| DD54 | **AI 输出一致性用 pre-commit 硬阻断 + 周报告软审计，而非实时阻断** | 实时阻断降低 AI 产出效率→pre-commit 是黄金平衡点 | GAP-M12 |

---

## -2.5 新增容量 SLO（GATE-M-001~008）

```yaml
master_capacity_slos_v1_1:
  - id: GATE-M-001-module-dep-query
    description: "模块依赖图谱查询（BFS depth≤3）延迟 P99"
    target_ms: 500
    relates_to: "GAP-M01"

  - id: GATE-M-002-blueprint-reconciliation
    description: "蓝图注册表与文件系统每日对账——漂移条目数上限"
    target: "< 5 条目/日"
    relates_to: "GAP-M02"

  - id: GATE-M-003-kb-partition-query
    description: "KB 分区查询延迟 P99（含 metadata 预过滤 + embedding search）"
    target_ms: 1000
    relates_to: "GAP-M03"

  - id: GATE-M-004-ce-injection-effectiveness
    description: "CE 注入蓝图的 AI 实际引用率（rolling 24h）"
    target: "> 60%"
    relates_to: "GAP-M04"

  - id: GATE-M-005-system-cold-start
    description: "12 系统全量冷启动至 readyz=200 耗时上限"
    target_ms: 180000      # 3 分钟
    relates_to: "GAP-M06"

  - id: GATE-M-006-llm-cost-burn-rate
    description: "LLM API 单日成本上限（硬阻断）"
    target: "¥30/day"
    relates_to: "GAP-M07"

  - id: GATE-M-007-master-blueprint-size
    description: "MOD-MASTER_BLUEPRINT 总行数上限（超过触发分拆评估）"
    target: 8000
    relates_to: "GAP-M08"

  - id: GATE-M-008-cross-system-saga-recovery
    description: "Saga 崩溃恢复成功率（非人工介入）"
    target: "> 95%"
    relates_to: "GAP-M09"
```

---

## -2.6 新增容量 Anti-Patterns（AP25-AP36）

| # | Anti-Pattern | 违反后果 | 正确做法 | 对应缺口 |
|---|-------------|---------|---------|:---:|
| AP25 | **忽略模块间依赖——只分析文件→脚本，不管模块→模块** | 模块 API 变更→下游模块静默失效→3天后才发现 | Module DAG BFS depth≤3 查询→G0 门禁自动提示影响范围 | GAP-M01 |
| AP26 | **blueprint_registry.yaml 手工维护到 1,500 条** | YAML 文件 ~8MB→Git 每次重写→Merge Conflict 地狱 | SQLite auto-index + YAML 每日导出 | GAP-M02 |
| AP27 | **ChromaDB 单 collection 10M vectors——不分区不优化** | 查询延迟从 50ms 飙到 500ms→CE build 超时 | 按 layer 分区 + metadata 预过滤 + FTS5 混合搜索 | GAP-M03 |
| AP28 | **CE 注入所有相关蓝图——token 预算永远不足** | 1,500 蓝图场景下 20K 预算被无关蓝图淹没 | blueprint tiering 四层分级→相关性排序→预算分配 | GAP-M04 |
| AP29 | **脚本永远 active——从不废弃、从不归档** | 10,000 脚本中 30% 已是死脚本→全量扫描白跑 3,000 次 | 生命周期状态机→90 天零触发自动 DEPRECATED→再 90 天 ARCHIVED | GAP-M05 |
| AP30 | **12 系统启动顺序靠"感觉"——无 DAG 无超时预算** | 启动时循环依赖→hang 住→只能 kill -9 重启 | 启动 DAG 四层并行→总预算 180s→超时降级启动 | GAP-M06 |
| AP31 | **LLM 成本无追踪无预算——月底收到 ¥5000 账单** | AI 用了昂贵模型但无人知晓→成本失控 | Daily ¥30 硬阻断 + weekly ¥150 软告警 + per-agent 归因 | GAP-M07 |
| AP32 | **总蓝图无限膨胀——从 4K 行到 15K 行** | AI 冷启动读分派表→token 消耗从 500 涨到 2000 | 8000 行触发分拆→保持每蓝图 < 4000 行 | GAP-M08 |
| AP33 | **Orc+Gate+Script+DB 四步操作无事务保障** | 任务创建了但 Finding 没写入→状态不一致累积 | Saga 补偿事务→步骤失败自动回滚→最终一致性 | GAP-M09 |
| AP34 | **靠直觉判断"系统还能撑多久"——无数据驱动预测** | 模块 800 时突然 DB 延迟飙升→紧急重构 | 数字孪生定期校准→瓶颈预测→提前告警 | GAP-M10 |
| AP35 | **契约随意修改——消费方不知道** | 改了一个字段→下游 5 个系统 break→CI 红灯但不知原因 | semver + deprecation window + 自动通知消费方 | GAP-M11 |
| AP36 | **100 AI 各写各的——无跨 session 质量审计** | 代码库风格碎片化→dataclass/NamedTuple/dict 混用 | pre-commit 硬阻断 + 周 Cross-AI Consistency Report | GAP-M12 |

---

## -2.7 与现有设计的关系 — 三层分界线

| 层 | 内容 | 目标 |
|---|------|------|
| §-2（本章） | 12 缺口 + 12 DD + 8 SLO + 12 AP | v1.1.0 体系完备 |
| 升级章一~十 | 10 章容量架构 + 54 CT-* 契约参数升级 | v1.0.0 核心链路 |
| §零~三十七 | 37 章集成契约 + 63 CT-* 治理体系 | v0.9.2 基准能力 |

施工顺序：§-2（知道 v1.0.0 缺什么）→ 升级章一~十（知道 v1.0.0 加了什么）→ §零起（知道 v0.9.2 有什么）
施工优先级：P0 地基（M01-M04）→ P1 稳定（M05-M09）→ P2 保障（M10-M12）
本章不覆盖升级章的内容——升级章保持不动。

### -2.7.1 缺口与现有升级章的映射

| 缺口 | 关联 v1.0.0 升级章 | 增强还是新增 | 说明 |
|:---:|------|:---:|------|
| GAP-M01 | 升级章二（增量扫描引擎） | 增强 | file→script DAG 升级为两层图谱：module→module + file→script |
| GAP-M02 | 升级章四（注册与发现 v2.0） | 增强 | 模块/脚本自动发现 → 扩展覆盖蓝图注册表 |
| GAP-M03 | 升级章一（Scale Plane） | 新增 | Scale Plane 声明了 10M vectors 但未设计查询性能保障 |
| GAP-M04 | 升级章一（Scale Plane） | 新增 | CE token 预算放大但未设计选择性注入策略 |
| GAP-M05 | 升级章四（注册与发现 v2.0） | 新增 | 注册覆盖存在性——生命周期覆盖时间维度 |
| GAP-M06 | — | 新增 | 全新维度——v1.0.0 未涉及系统启动 |
| GAP-M07 | 升级章一（Scale Plane） | 增强 | 从 token 预算声明 → 财务成本硬强制 |
| GAP-M08 | — | 新增 | 全新维度——总蓝图自身的健康 |
| GAP-M09 | 升级章三（多AI并发） | 新增 | 并发架构覆盖隔离——事务覆盖原子性 |
| GAP-M10 | 升级章七（可观测性） | 增强 | 从实时监控 → 预测性监控 |
| GAP-M11 | — | 新增 | 全新维度——63 CT-* 的演化管理 |
| GAP-M12 | 升级章七（可观测性） | 新增 | 全新维度——跨 AI 质量审计 |

---

## -2.8 三阶段施工路线图

> **时态属性**：施工步骤属于**临时时态**——执行完毕后可删除，但 MUST 先通过运行验证。
> **删除前置条件**（缺一不可）：
> 1. 代码文件存在且非空
> 2. `python -m pytest tests/` 对应测试 exit 0
> 3. `mypy` 类型检查通过
> 4. `ruff` lint 通过
> 5. 以上 4 项全部通过后，该步骤的详细内容可从蓝图删除，只保留"步骤 N: 已完成"

### Phase A：体系缺口补齐（必须先做） — 目标 v1.1.0-alpha

| 缺口 | 施工内容 | 产出 | 验证方式 |
|:---:|---------|------|------|
| GAP-M01 | Module DAG：AST import 分析 + SQLite 表 + BFS 查询接口 | `src/zephyr/shared/module_deps.py` | 修改 module_A 的 __init__.py → 查询返回受影响的 module_B/C/D |
| GAP-M02 | 蓝图注册表 v2.0：BlueprintAutoIndexer + SQLite 迁移 + 每日对账 | `scripts/governance/registry/blueprint_auto_indexer.py` | 新增 1 个蓝图 → SQLite 自动索引 → YAML 导出不变 |
| GAP-M03 | KB 分区：按 layer 拆 ChromaDB collection + metadata 预过滤 + 混合搜索 | `src/zephyr/data/knowledge_management/kb/partition_router.py` | 8M vectors 查询 P99 < 1s |
| GAP-M04 | CE tiering：blueprint relevance scoring + 四级注入 + 预算分配器 | `src/zephyr/orchestration/context_management/blueprint_ranker.py` | 1,500 蓝图场景 → token 预算内注入 → AI 引用率 > 60% |

### Phase B：运维稳定加固 — 目标 v1.1.0-beta

| 缺口 | 施工内容 | 产出 | 验证方式 |
|:---:|---------|------|------|
| GAP-M05 | 脚本生命周期：状态机 + SQLite 表 + 90 天自动流转 + 质量分级 cron | `src/zephyr/infrastructure/runtime_integration/script_system/script_lifecycle.py` | 标记 30% 脚本为 DEPRECATED → 验证 ARCHIVED 不参与全量扫描 |
| GAP-M06 | 冷启动编排：四层 DAG + health probe 链 + warm-up 策略 | `src/zephyr/infrastructure/runtime_integration/runtime/startup_orchestrator.py` | 冷启动 → 95s 内 readyz=200 |
| GAP-M07 | LLM 成本管控：cost tracker + daily/weekly/monthly 预算强制 + 归因 | `src/zephyr/shared/cost_enforcer.py` | 模拟超预算 → daily 硬阻断生效 |
| GAP-M08 | 总蓝图自健康：行数监控 + 自引用校验 + 拆分阈值告警 | `scripts/governance/master_blueprint_health.py` | MOD-MASTER_BLUEPRINT > 6000 行 → P1 告警 |
| GAP-M09 | Saga 协调器：SagaCoordinator + saga_state 表 + 崩溃恢复 | `src/zephyr/orchestration/runtime_core/orchestrator/saga_coordinator.py` | 模拟 step_3 崩溃 → 自动回滚 step_1+2 → 最终一致 |

### Phase C：生产级保障 — 目标 v1.1.0-rc

| 缺口 | 施工内容 | 产出 | 验证方式 |
|:---:|---------|------|------|
| GAP-M10 | 数字孪生：数据采集→模型训练→瓶颈预测→what-if 模拟 | `src/zephyr/shared/capacity_digital_twin.py` | 用 51→400 数据训练→预测 800→与实际误差 < 20% |
| GAP-M11 | 契约演化管理：semver 校验 + deprecation window + 消费方自动通知 | `scripts/governance/contract_evolution.py` | 契约 MAJOR 升级 → CI 检测到 incompatible consumer → WARN |
| GAP-M12 | 跨 AI 质量审计：pre-commit 硬阻断 + 周报告 + 设计冲突检测 | `scripts/governance/cross_ai_audit.py` | 100 AI 产出 → 风格一致率 > 90% → 设计冲突自动发现 |

---

## -2.9 版本升级声明

| 属性 | v1.0.0（现存） | v1.1.0（目标） |
|------|--------|--------|
| 容量设计章节 | 升级章一~十（10 章） | §-2（9 小节）+ 升级章一~十（10 章） |
| 设计决策 | DD1-DD12（v0.9.2 10条 + 升级章未编号但实际有） | **+DD43-DD54（12 条新增）** |
| Anti-Patterns | AP1-AP8（v0.9.2 8条 + v1.0.0 升级章未明确编号） | **+AP25-AP36（12 条新增）** |
| 容量 SLO | 升级章未系统定义新的 SLO 条目 | **+GATE-M-001~008（8 条新增）** |
| 容量缺口 | 0（v1.0.0 认为已闭环） | **12 项（体系级缺口）** |
| 施工阶段 | 升级章九/十定义了 4-phase + P0-P4 序列 | **Phase A（体系缺口）→ B（运维稳定）→ C（生产保障）** |
| 规模声明 | 10,000 脚本 / 1,500 模块 / 100 AI 并发 | 同左——不改变设计上限 |


# 容量升级总蓝图 — 从 51 模块→1,500 模块的架构升级设计

> **定位**：本章是对 MOD-MASTER_BLUEPRINT v0.9.2 的容量升级设计。v0.9.2 的定义了 12 系统间的集成关系（方向正确），
> 但其规模参数（24 workers、全局进程锁、L1=1 slot、手动 YAML 注册表）是针对 51 模块 / 268 脚本设计的。
> 本章提供 **不改变架构骨架**的前提下，将容量从 51 模块扩展到 1,500 模块的完整设计方案。


---

## 升级章：一、规模平面（Scale Plane）—— 一切容量参数的 SSoT

> **新增 §。** v0.9.2 §五"全局容量预算"是当前规模的快照——本章替换它，成为未来的容量 SSoT。

### 1.1 设计上限声明

| 维度 | 当前 (v0.9.2) | 设计上限 (v1.0.0) | 安全系数 |
|:---|---:|---:|:---:|
| 模块数 | 51 | **1,500** | — |
| 治理脚本 | 268 | **10,000** | 1.27x (vs 7,875 推导) |
| 并发 AI Agent | 1 (全局锁) | **100** | — |
| 并发脚本执行 | 24 workers | **80~96 workers** | 调节范围 40-100 |
| 增量扫描脚本数 | — (无增量) | **15~30 / 次变更** | — |
| 增量扫描耗时 | — | **< 60s** | — |
| 全量扫描耗时 | ~3.5h | **< 2h (4分片并行)** | — |
| 最大并发扫描数 | 1 (全局锁) | **100 (每AI独立)** | — |
| Token 预算 | 200,000 全局 | **2,000,000 全局 + 20,000/session** | 10x |
| SQLite 写入并发 | 5 WAL writers | **20 WAL writers** | — |
| ChromaDB 向量上限 | 1M / collection | **10M / collection** | 10x |
| DLQ 容量 | 10,000 条上限 | **100,000 条上限** | 10x |

### 1.2 规模参数对照表（每系统升级前后）

```yaml
scale_plane:
  orchestrator:
    v092: {max_parallel_l1: 1, max_parallel_l2: 3, max_parallel_l3: 2}
    v100: {max_parallel_l1: 20, max_parallel_l2: 10, max_parallel_l3: 5}
    rationale: "100 AI → 至少20个L1通道。L2/L3按比例放大"

  script_system:
    v092: {bulkhead_workers: 24, subprocess_limit: 5, concurrency_mode: "single_process_lock"}
    v100: {bulkhead_workers: 96, subprocess_limit: 60, concurrency_mode: "multi_agent_license"}
    rationale: "四池 quick:48 + content_analysis:24 + ai_generated:16 + disruptive:8 = 96"

  context_engine:
    v092: {token_budget_per_session: 8000, ce_timeout_s: 10}
    v100: {token_budget_per_session: 20000, ce_timeout_s: 15}
    rationale: "更多模块=更多蓝图注入需求 → token预算翻倍"

  feedback_loop:
    v092: {poll_interval_s: 30, component_count: 99, mode: "full_poll"}
    v100: {poll_interval_s: 300, component_count: 99_lazy, mode: "event_driven"}
    rationale: "99组件→按需实例化；30s→5min健康基线；增量检测→事件驱动"

  database:
    v092: {wal_connections: 5, checkpoint_interval: "auto"}
    v100: {wal_connections: 20, checkpoint_interval: 60s}
    rationale: "100 AI同时写入 → WAL需要更多并发连接"

  vector_memory:
    v092: {max_vectors_per_collection: 1_000_000}
    v100: {max_vectors_per_collection: 10_000_000}
    rationale: "1,500模块×百条KE/模块 × 10 = 预留10M"

  dlq:
    v092: {max_queue_depth: 10_000, max_age_hours: 72}
    v100: {max_queue_depth: 100_000, max_age_hours: 72}
    rationale: "更多系统=更多故障=更多DLQ消息"
```

### 1.3 硬件容量验证表

| 资源 | i7-12700KF 规格 | v1.0.0 峰值需求 | 利用率 | 结论 |
|:---|---:|---:|:---:|:---:|
| CPU 核心 | 12C/20T | 60~80 subprocess workers | 75-100% | ✅ 够用（需合理调度） |
| 内存 | 64GB | ~38GB (100 session×200MB + 缓存10GB + OS 8GB) | 59% | ✅ 宽裕 |
| NVMe SSD | 1TB | ~100GB (日志 + SQLite + ChromaDB) | 10% | ✅ 宽裕 |
| GPU VRAM | 24GB (3090) | BGE-M3(2GB) + qwen3:8b(6GB) = 8GB | 33% | ✅ 宽裕 |
| 磁盘 IOPS | ~500K (NVMe) | 100 AI × 30脚本 × 平均10次IO = 30K IOPS | 6% | ✅ 宽裕 |
| 网络带宽 | 1Gbps | 100 AI × 5K tokens/session × 4 tokens/KB ≈ 2MB/s | 2% | ✅ 宽裕 |

---

## 升级章：二、增量扫描引擎（Incremental Scan Engine）—— 最重要的缺失组件

> **新增 §。** 这是整个升级中最重要的基础设施。当前系统没有"知道哪些脚本受这次改动影响"的机制。
> 这是实现"增量扫描 < 1 分钟"的前提。

### 2.1 核心问题

```
当前模式：AI 改了一个文件 → 跑全量 268 个脚本（或按维度全跑）→ 3.5h
目标模式：AI 改了一个文件 → 只跑受影响的 15-30 个脚本 → < 60s
```

### 2.2 设计：变更→脚本依赖图（Change→Script DAG）

```yaml
contract: CT-IMPACT-001
title: "变更影响分析——文件改动→受影响脚本的DAG"
owner: MOD-MASTER_BLUEPRINT
status: NEW

architecture:
  impact_graph:
    storage: "SQLite 表 `impact_graph` + 内存 LRU 缓存"
    structure: "有向图 G = (V_files, V_scripts, E_depends)"

    vertices:
      V_files:
        - type: "源文件节点"
        - key: "file_path_hash"
        - attributes: [glob_pattern, module_id, last_modified]
        - count_estimate: "1,500 模块 × 平均 10 文件/模块 = 15,000 节点"

      V_scripts:
        - type: "脚本节点"
        - key: "script_path_hash"
        - attributes: [dimension, phase, avg_runtime_ms, dependencies]
        - count_estimate: "10,000 节点"

    edges:
      E_depends:
        - type: "file → script 依赖边"
        - semantics: "脚本 S 读取了文件 F → F 变更时 S 需要重跑"
        - weight: "1.0 (默认) / 0.5 (弱依赖——如仅读取import引用)"
        - count_estimate: "10,000 脚本 × 平均 8 文件/脚本 = 80,000 边"

      E_before:
        - type: "script → script 前置依赖边"
        - semantics: "S1 必须在 S2 之前执行"
        - weight: "N/A"
        - count_estimate: "~2,000 边 (维度间少量前置关系)"

  build_strategy:
    static_analysis:
      description: "Python AST 静态分析——解析每个脚本的 import / open() / Path.read() 调用"
      trigger: "脚本新增或修改时 → 自动重建该脚本的 file→script 边"
      tool: "scripts/governance/impact/build_dependency_graph.py"
      format: "每个脚本输出一个 .deps.yaml 到 scripts/governance/_deps/"

    glob_expansion:
      description: "脚本中的 glob 模式（如 '**/*.py'）展开到具体文件路径"
      trigger: "新文件创建时 → 重新评估所有包含 glob 的脚本"
      cache: "glob → file_list 映射缓存，TTL=600s"

  query_interface:
    input: "list[changed_file_path]"
    output: "list[(script_path, priority, estimated_runtime_ms)]"
    algorithm: |
      1. 对每个 changed_file → 查 impact_graph 的出边 → 得到 {受影响的脚本}
      2. 合并去重 → 按 priority 排序 (P0→P1→P2→P3)
      3. 对排序结果做拓扑排序 (满足 E_before 约束)
      4. 返回排好序的脚本列表 → 提交到 BulkheadExecutor
    latency_target: "< 50ms (内存LRU命中) / < 200ms (SQLite回源)"

  cache_strategy:
    l1_cache: "内存 LRU, max_size=10,000 entries, TTL=300s"
    l2_cache: "SQLite impact_graph 表, 全量"
    invalidation: "脚本文件 md5 变更时 → 清除该脚本的所有 L1 依赖边 → 触发静态分析重建"
```

### 2.3 增量扫描完整流程

```
[触发] AI Agent 提交代码变更 (git commit / 文件保存)
    ↓
[Step 1] FileChangeDetector: diff HEAD → 得到 changed_files = [a.py, b.yaml, c.toml]
    ↓
[Step 2] ImpactAnalyzer: 查询 impact_graph
    → a.py → [D1_env_check, D3_structure_lint, D5_architecture, D11_telemetry]
    → b.yaml → [D5_architecture, D7_config_schema]
    → c.toml → [D7_config_schema]
    → 去重合集: [D1, D3, D5, D7, D11] 维度 × 对应 C1-C4 阶段 = 18 个脚本
    ↓
[Step 3] TopologicalSorter: 拓扑排序 → 执行队列 (D1_C1→D1_C2→...→D11_C4)
    ↓
[Step 4] ConcurrencyLicense: 申请 AI session 的执行许可 (80 并发许可证之一)
    ↓
[Step 5] BulkheadExecutor: 脚本按类型路由到四个池 → 并行执行
    ↓
[Step 6] ResultCollector: 聚合 Findings → Gate 判定 → FLE 记录
    ↓
[Step 7] CacheUpdater: 更新 ScanCache → 标记本次扫描的文件版本
    ↓
总耗时: 18 脚本 × 平均 2s/脚本 / 8 并发 = ~5-10s (远 < 60s 目标)
```

### 2.4 全量扫描保留设计

```yaml
full_scan:
  mode: "optional_weekly"
  schedule: "每周日 03:00 (低峰期)"
  parallelism: "4分片 (hash(script_id) % 4)"
  expected_duration: "10,000 脚本 / 4分片 / 25并发/分片 = ~100s/分片 × 串行因子 = < 2h"
  fallback: "分片失败 → 自动降级为 2分片 → 仍失败 → 通知 Owner"
  result: "生成 Weekly Health Report → 存档到 knowledge_base (KE type=WEEKLY_HEALTH)"
```

---

## 升级章：三、多 AI 并发架构（Multi-Agent Concurrency Architecture）

> **新增 §。** v0.9.2 的 ProcessLock 只允许单实例运行。本章提供 100 AI 同时工作的完整设计。

### 3.1 并发许可证系统（替换 ProcessLock）

```yaml
contract: CT-CONCURRENCY-001
title: "多AI并发许可证系统——替换全局进程锁"
owner: MOD-MASTER_BLUEPRINT
status: NEW
priority: P0

design:
  license_pool:
    total_slots: 80
    allocation: "先到先得 + 优先级抢占"
    slot_timeout_s: 300  # AI session 最长持有时间
    renewal_interval_s: 30  # 心跳续约间隔

  license_lifecycle:
    acquire:
      preconditions: ["AI session 有效", "不超过该AI的max_concurrent_scans=3"]
      timeout: "30s 内未获取 → 排队等待 → 超时返回 BUSY"
      response: "{granted: bool, license_id: uuid, expires_at: ISO8601}"

    hold:
      heartbeat: "每30s发送 /_license/{id}/heartbeat → 续约TTL=300s"
      active_scans: "每个license下最多3个并发扫描 (对应3个文件变更批次)"

    release:
      trigger: ["扫描完成", "AI session 结束", "心跳超时300s未续约"]
      action: "归还slot → 通知等待队列 → 清理ScanCache关联"

  priority_preemption:
    levels: {P0_CRITICAL: 0, P1_HIGH: 1, P2_NORMAL: 2, P3_LOW: 3}
    preempt_rule: "P0 可抢占 P2/P3 的 license → 被抢占者进入队列头部等待"
    max_preemptions: "同一 session 最多被抢占 3 次 → 超过则通知 Owner"

  implementation:
    backend: "SQLite `concurrency_licenses` 表 + 内存信号量"
    table_schema:
      - {name: license_id, type: TEXT PK, format: uuid7}
      - {name: agent_session_id, type: TEXT, indexed: true}
      - {name: status, type: TEXT, enum: [ACTIVE, QUEUED, EXPIRED]}
      - {name: priority, type: TEXT, enum: [P0, P1, P2, P3]}
      - {name: acquired_at, type: TEXT, format: ISO8601}
      - {name: expires_at, type: TEXT, format: ISO8601}
      - {name: active_scan_count, type: INTEGER, max: 3}
      - {name: preempt_count, type: INTEGER, default: 0}
```

### 3.2 Agent Session 模型

```yaml
contract: CT-AGENT-SESSION-001
title: "AI Agent 会话生命周期——多AI并发的会话管理"
status: NEW

session_model:
  lifecycle: [CREATED, CONTEXT_BUILDING, WORKING, SCANNING, IDLE, COMPLETED, TIMED_OUT]

  isolation:
    workspace: "每个AI session 独立工作目录 (git worktree 或文件锁范围)"
    file_conflict: "两个AI修改同一文件 → 后提交者收到 CONFLICT 通知 → 进入冲突解决流程"
    token_budget: "每 session 20,000 tokens (使用完需申请追加)"
    max_duration: "单 session 最长 2h → 超时自动 TIMED_OUT → 释放所有资源"

  registration:
    on_start: "向 SQLite agent_sessions 表注册 → 获得 session_id + license slot"
    on_end: "释放 license → 更新 session 状态 → 记录 audit_log"
    max_per_agent: "同一 agent_identity 最多 3 个并发 session"
```

### 3.3 冲突检测与解决

```yaml
contract: CT-SESSION-CONFLICT-002
title: "多AI并发冲突检测与解决——升级 CT-SESSION-CONFLICT-001"
status: UPGRADE

conflict_types:
  FILE_CONFLICT:
    detection: "Orc 维护 active_file_locks 表 → AI提交前检查"
    resolution: |
      后提交者:
        1. 收到 CONFLICT 通知 + diff 预览
        2. 自动 rebase (简单冲突) 或 请求Owner裁决 (复杂冲突)
        3. 最多retry 3次 → 仍冲突则任务 BLOCKED
    proactive: "AI 开始编辑文件前 → 申请 file_lock (乐观锁)"

  RESOURCE_STARVATION:
    detection: "某AI 30s内无法获取 license → 触发"
    action: "FLE 检测→通知Owner→提高该AI优先级→必要时抢占低优先级license"

  KNOWLEDGE_CONFLICT:
    detection: "两个AI同时向KB写入同一KE → content_hash碰撞"
    resolution: "先入者胜 → 后入者标记 DUPLICATE → 通知后入AI"
```

---

## 升级章：四、注册与发现系统 v2.0 — 从手工 YAML 到自动 SQLite

> **升级 §。** 1,500 个模块的 YAML 注册表无法手工维护。需要自动发现 + SQLite 索引。

```yaml
contract: CT-REGISTRY-002
title: "注册与发现系统 v2.0——模块/脚本/蓝图的自动注册"
status: UPGRADE

auto_discovery:
  module_scanner:
    name: "ModuleOnboardingScanner"
    trigger: ["新目录创建在 src/zephyr/ 下", "新 blueprint.md 出现在 docs/03_modules/ 下"]
    scan_patterns:
      - "src/zephyr/**/__init__.py → 识别为模块"
      - "docs/03_modules/**/blueprint.md → 识别为蓝图模块"
      - "scripts/governance/**/*.py → 识别为治理脚本"
    auto_register: true  # 无需人工确认
    dedup: "按 module_path 去重"

  script_indexer:
    name: "ScriptAutoIndexer"
    trigger: ["新脚本创建", "脚本内容修改 (md5变更)"]
    action: "静态分析 → 提取依赖 → 写入 script_index 表 + 重建 impact_graph 边"
    fields_indexed:
      - script_path: "TEXT UNIQUE"
      - dimension: "ENUM[D1-D12]"
      - phase: "ENUM[C1-C5]"
      - depends_on_files: "JSON[TEXT]"   # AST分析结果
      - depends_on_scripts: "JSON[TEXT]"  # 前置脚本
      - avg_runtime_ms: "INTEGER"
      - last_run_result: "ENUM[PASS, WARN, FAIL, CRITICAL]"
      - last_run_at: "ISO8601"
      - md5_hash: "TEXT"

  registry_cache:
    l1: "内存 dict, 全量加载启动时 → 每60s check SQLite for updates"
    l2: "SQLite module_index + script_index 表"
    export: "YAML 文件每日 02:00 自动导出 (人类可读快照)"
```

---

## 升级章：五、脚本执行平台 v2.0 — 从线程池到子进程池

> **升级 §。** Python GIL 在 I/O 密集型脚本中影响不大，但在 96 并发下会暴露。子进程池是更稳健的方案。

```yaml
contract: CT-EXEC-002
title: "脚本执行平台 v2.0——subprocess pool + 动态扩缩"
status: UPGRADE

execution_pool:
  v092: {type: ThreadPoolExecutor, workers: 24, mode: static}
  v100:
    type: "SubprocessPool (每个脚本独立子进程)"
    workers:
      min: 12
      max: 80
      scale_up_threshold: "队列深度 > 50 → +16 workers (最多到80)"
      scale_down_threshold: "队列深度 < 10 持续60s → -8 workers (最少到12)"
      cooldown_s: 120  # 两次扩缩之间最少间隔

  pool_routing:
    quick_pool: {max_workers: 48, target_scripts: "D1-D4 C1-C3 快速检查"}
    content_pool: {max_workers: 24, target_scripts: "D5-D8 内容分析"}
    ai_pool: {max_workers: 16, target_scripts: "D9-D12 AI专项检测"}
    disruptive_pool: {max_workers: 8, target_scripts: "文件修改、git操作"}

  process_isolation:
    per_script: {timeout_s: 120, memory_limit_mb: 256, cpu_affinity: "auto"}
    sandbox: "--no-verify 应急通道除外 → 其余均在 restricted sandbox 执行"

  result_storage:
    format: "JSONL 追加写入 scripts/governance/_results/{script_hash[:8]}/{date}.jsonl"
    retention: "30天热数据 + 365天冷归档"
    query: "SQLite 索引表 result_index → 按 script_id + date_range 秒查"
```

---

## 升级章：六、容量感知调度器（Capacity-Aware Scheduler）

> **新增 §。** 当 100 AI 同时提交 1,500 个脚本执行请求时，需要优先级调度以避免饿死。

```yaml
contract: CT-SCHEDULER-001
title: "容量感知调度器——多优先级队列 + 公平分配"
status: NEW

scheduling_model:
  queues:
    P0_CRITICAL: {max_concurrent: 20, preemptive: true, timeout_s: 60}
    P1_HIGH: {max_concurrent: 30, preemptive: false, timeout_s: 120}
    P2_NORMAL: {max_concurrent: 40, preemptive: false, timeout_s: 300}
    P3_LOW: {max_concurrent: 10, preemptive: false, timeout_s: 600}

  fair_share:
    per_agent_limit: "每个AI agent最多同时占用 8 个执行槽"
    per_module_limit: "每个模块最多同时占用 4 个执行槽"
    starvation_prevention: "P3 任务在队列中超过 600s → 自动升级到 P2"

  backpressure:
    queue_depth_limit: 5000
    overload_action: "拒绝新的P3请求 → 返回 BUSY → AI 应稍后重试"
    graceful_degradation: "队列深度 > 3000 → P2/P3 合并到一个池 → P0/P1 不受影响"
```

---

## 升级章：七、大规模可观测性（Scale-Aware Observability）

> **升级 §。** v0.9.2 的 30s 全量 poll + 99 组件全部实例化，在 10,000 脚本规模下不可用。

```yaml
contract: CT-OBSERVABILITY-002
title: "大规模可观测性——事件驱动 + 分级采集"
status: UPGRADE

event_driven_monitoring:
  triggers:
    - "脚本执行完成 → FLE.on_script_complete() 而非 30s poll"
    - "AI session 状态变更 → FLE.on_session_change()"
    - "license 池水位变化 → FLE.on_license_pool_change()"
    - "队列深度告警 → FLE.on_queue_pressure()"

  baseline_poll:
    interval: 300s  # 5分钟全量健康基线 (替代30s)
    scope: "系统级指标 (CPU/内存/磁盘/连接数)"
    components: "仅实例化 global_health 组件 → 其余按事件触发"

  per_agent_metrics:
    dashboard_fields:
      - "agent_id + session_count + active_scans"
      - "license_acquire_latency_p50/p95/p99"
      - "script_execution_success_rate"
      - "conflict_rate (文件冲突次数/总提交次数)"
      - "token_consumed / token_budget_remaining"

  scale_dashboards:
    "AI Agent 实时面板": "100个agent各自的状态、扫描数、资源占用 → 热力图"
    "脚本执行热图": "10,000个脚本的执行频率热图 → 发现冷脚本 (可归档)"
    "License 池水位": "80个slot的占用率时间线 → 峰值预警"
    "Impact Graph 健康": "80,000条依赖边的覆盖率 → 发现无主脚本 / 无脚本文件"
```

---

## 升级章：八、水平扩展设计（多机场景预留）

> **新增 §。** 当前单机足够，但设计上预留水平扩展路径——不等到需要时再考虑。

```yaml
contract: CT-SHARD-001
title: "水平分片扩展设计——多机场景预留"
status: NEW
when: "单机 CPU 利用率持续 > 85% 超过 1h 时触发迁移评估"

shard_design:
  shard_count: "从 1 → N (N≤8)"
  shard_key: "hash(module_id) % N"

  shard_responsibilities:
    shard_0: "modules 0-187 → 约1,250个脚本"
    shard_1: "modules 188-375"
    shard_2-7: "同理"

  coordination:
    type: "当前 SQLite 单文件 → 未来 Redis cluster"
    distributed_lock: "当前 文件锁 → 未来 Redis Redlock"
    event_bus: "当前 内存Observer → 未来 Redis Pub/Sub 或 NATS"

  data_partitioning:
    sqlite: "每分片独立 sqlite 文件 → shared-nothing"
    chromadb: "每分片独立 collection → shard_{id}_{collection_name}"
    backup: "每分片独立备份 → backup/shard_{id}/"
```

---

## 升级章：九、渐进迁移路径

> **新增 §。** 从 51→1,500 模块是跨越式增长，需要分阶段验证每个阶段的设计假设。

```yaml
migration_phases:
  phase_1:
    name: "参数解锁 (当前→100模块级)"
    target: "100 模块 / 600 脚本 / 20 AI 并发"
    actions:
      - "ProcessLock → ConcurrencyLicense (80 slots)"
      - "BulkheadExecutor 24→80 workers"
      - "WorkOrchestrator L1:1→10, L2:3→8, L3:2→5"
      - "Token budget 200K→1M 全局"
      - "L1/L2级锁保留不变（细粒度控制仍有效）"
    validation: "20 AI 同时工作，增量扫描 < 60s"
    rollback: "恢复 ProcessLock + 原worker数"

  phase_2:
    name: "增量引擎 + 注册升级 (100→500模块级)"
    target: "500 模块 / 2,500 脚本 / 50 AI 并发"
    actions:
      - "实现 impact_graph + ChangeDetector (CT-IMPACT-001)"
      - "实现 ModuleOnboardingScanner + ScriptAutoIndexer (CT-REGISTRY-002)"
      - "实现 ConcurrencyLicense 优先级抢占"
      - "注册表 YAML→SQLite 迁移"
    validation: "50 AI 同时工作，增量扫描 < 60s，全量扫描 < 2h"
    rollback: "保留 YAML 导出 → 可回退到手工注册"

  phase_3:
    name: "多AI并发 + 调度 (500→1,000模块级)"
    target: "1,000 模块 / 5,500 脚本 / 80 AI 并发"
    actions:
      - "实现 CapacityAwareScheduler (CT-SCHEDULER-001)"
      - "事件驱动 FLE (CT-OBSERVABILITY-002)"
      - "SubprocessPool 动态扩缩 (CT-EXEC-002)"
      - "Agent Session 冲突解决 (CT-SESSION-CONFLICT-002)"
    validation: "80 AI 同时工作，无资源饿死，冲突率 < 5%"
    rollback: "保留 ThreadPool 模式 → 可降级"

  phase_4:
    name: "全面加固 (1,000→1,500模块级)"
    target: "1,500 模块 / 10,000 脚本 / 100 AI 并发"
    actions:
      - "全量压力测试 (100 AI × 30 脚本/AI = 3,000 脚本并发)"
      - "FLE 99组件按需懒加载 + 5min基线poll"
      - "DLQ 100,000容量验证"
      - "全量扫描 4分片 2h 验证"
      - "90天持续运行稳定性验证"
    validation: "全部 SLO 达标 + 7×24 稳定 + 资源利用率 < 85%"
    rollback: "回退到 phase_3 + 扩容到多机 (CT-SHARD-001)"
```

---

## 升级章：十、施工序列 — 文件级施工地图

> **时态属性**：施工步骤属于**临时时态**——执行完毕后可删除，但 MUST 先通过运行验证。
> **删除前置条件**同 §-2.8。

> **施工优先级**：先改参数（零风险）→ 补增量引擎（核心价值）→ 改并发架构（解锁规模）。

```yaml
construction_sequence:
  P0_emergency:
    - {file: "scripts/governance/_concurrency.py", change: "ProcessLock→ConcurrencyLicense", hours: 4}
    - {file: "scripts/governance/_concurrency.py", change: "BulkheadExecutorV2 pools: 24→96 workers", hours: 1}
    - {file: "src/zephyr/orchestration/runtime_core/runtime_config.py", change: "max_parallel_l1:1→20, l2:3→10, l3:2→5", hours: 0.5}
    - {file: "src/zephyr/infrastructure/runtime_integration/pipeline/pipeline_orchestrator.py", change: "token_budget:200K→2M", hours: 0.5}
    - {task: "运行 20 AI 并发压力测试", hours: 2}

  P1_incremental_engine:
    - {file: "scripts/governance/impact/build_dependency_graph.py", change: "新建——AST静态分析→构建file→script DAG", hours: 12}
    - {file: "scripts/governance/impact/change_detector.py", change: "新建——git diff → changed_files", hours: 4}
    - {file: "scripts/governance/impact/impact_analyzer.py", change: "新建——DAG查询→受影响脚本列表", hours: 6}
    - {file: "scripts/governance/impact/topological_sorter.py", change: "新建——拓扑排序+优先级排序", hours: 4}
    - {file: "scripts/governance/impact/scan_cache.py", change: "新建——文件版本→扫描结果缓存", hours: 4}
    - {file: "scripts/governance/_concurrency.py", change: "run_all.py 集成 impact analyzer → 增量路径", hours: 6}
    - {task: "验证：单文件变更→仅触发15-30脚本→<60s完成", hours: 2}

  P2_multi_agent:
    - {file: "src/zephyr/orchestration/runtime_core/orchestrator/agent_session.py", change: "新建——Agent Session生命周期管理", hours: 8}
    - {file: "src/zephyr/orchestration/runtime_core/orchestrator/concurrency_license.py", change: "新建——80slot许可证+优先级抢占", hours: 8}
    - {file: "src/zephyr/orchestration/runtime_core/orchestrator/capacity_scheduler.py", change: "新建——4级优先级队列+公平分配", hours: 10}
    - {file: "src/zephyr/orchestration/runtime_core/orchestrator/session_conflict.py", change: "新建——文件锁+乐观锁+冲突解决", hours: 6}
    - {file: "src/zephyr/observability/feedback_loop/event_driver.py", change: "新建——事件驱动替换30s poll", hours: 8}
    - {task: "验证：50 AI 同时工作→无死锁→冲突率<5%→增量<60s", hours: 4}

  P3_registry_upgrade:
    - {file: "scripts/governance/registry/module_onboarding_scanner.py", change: "新建——自动扫描新模块→SQLite写入", hours: 6}
    - {file: "scripts/governance/registry/script_auto_indexer.py", change: "新建——AST分析新脚本→索引+依赖边", hours: 8}
    - {file: "scripts/governance/registry/yaml_exporter.py", change: "新建——每日SQLite→YAML导出", hours: 3}
    - {task: "迁移：现有51模块手工注册→SQLite→验证一致性", hours: 4}

  P4_production_hardening:
    - {file: "scripts/governance/_concurrency.py", change: "BulkheadExecutor 改 subprocess pool + 动态扩缩", hours: 8}
    - {file: "src/zephyr/observability/feedback_loop/scheduler.py", change: "99组件→懒加载+5min基线poll", hours: 6}
    - {file: "src/zephyr/orchestration/runtime_core/orchestrator/deferred_queue.py", change: "内存EventBus→Redis Pub/Sub适配层(可插拔)", hours: 6}
    - {task: "全量压力测试：100 AI×30脚本→全链路验证→SLO达标", hours: 8}
    - {task: "7×24 稳定性运行→资源监控→无memory leak→无磁盘爆满", hours: 168}
```

---

# 集成闭环总蓝图 — 任务系统·脚本系统·知识库及全部基础设施系统

> **module_id**: MOD-MASTER_BLUEPRINT | **version**: 1.0.0 | **status**: active | **layer**: cross_layer

> **真源声明**：本蓝图是 ZephyrAlpha 全部基础设施系统之间集成关系的 canonical SSoT。
> 各模块蓝图（MOD-INF-005/006、MOD-KB-001、以及即将创建的 Gates/CE/Pipeline/FLE/VMS/db/MCP/LSG/Telemetry 蓝图）引用本蓝图中的集成契约编号——
> 模块蓝图定义"内部怎么干"，本蓝图定义"之间怎么连"。

---

## 治理信息

### SSoT 声明

| 内容 | 真源 | 非真源 |
|------|------|--------|
| 容量升级设计 | **本文档 §-1/§-2** | — |
| CT-* 契约定义 | MOD-MASTER-002 §二 | — |
| 基线集成设计 | MOD-MASTER-002 | — |

**任何与本蓝图冲突的容量定义，以本蓝图为准。**

### 消费者注册表

| Tier | 消费者 | 依赖内容 |
|:----:|--------|---------|
| Tier 1 | MOD-MASTER-002 | 容量约束 |
| Tier 1 | INF-007 Gate Engine | 容量调度 |
| Tier 1 | INF-019 Agent Spec | 并发许可证 |

### 变更同步规则

| 变更类型 | Tier 1（下游蓝图） | Tier 2（集成系统） |
|---------|------------------|------------------|
| 容量约束变更 | 通知 baseline | 更新调度器 |
| 升级章设计变更 | 更新施工序列 | 更新脚本 |

### 修改条件

| 变更类型 | 审批要求 |
|---------|---------|
| 容量约束变更 | 需 Owner 审批 |
| 升级章设计变更 | AI 可自主 |
| 规模平面变更 | 需 Owner 审批 + 通知所有消费者 |

### 负向责任

| # | 本蓝图不涉及 | 由谁负责 |
|---|-------------|---------|
| 1 | 独立的模块拓扑 | SYS-MASTER-001 §一 负责 |
| 2 | CT-* 契约定义 | MOD-MASTER-002 §二 负责 |
| 3 | 具体的模块实现代码 | 各模块蓝图 (MOD-INF-*) 负责 |

### 触发条件

| 场景 | AI 应读取本蓝图 |
|------|---------------|
| 系统规模接近或超过当前容量预算 | 读 §-2 缺口清单 |
| 容量相关 CI 告警触发 | 读 §-1 对应升级章 |
| 新增模块需要容量评估 | 读 §-1 规模平面 |
| 瓶颈优化施工 | 读 §-1 增量扫描引擎 + 施工序列 |

### 导航路径

| 步骤 | 操作 |
|:---:|------|
| 1 | 读本蓝图 §-2 缺口清单 → 确认你面对的缺口 |
| 2 | 读本蓝图 §-1 相关升级章 → 找设计方案 |
| 3 | 对照 baseline 中的现有设计 → 确保兼容 |
| 4 | 按施工序列执行 → 逐个升级章落地 |

### 漂移防护

| 修改本文件 | 必须同步更新 |
|-----------|------------|
| 容量约束变更 | SYS-MASTER-001 §〇 容量预算 |
| 升级章设计变更 | MOD-MASTER-002 对应章节 |
| 规模平面变更 | 本蓝图所有引用规模数字的章节 |
| construction_progress 变更 | blueprint_registry.yaml |

---

## ⚠️ Vibe Coding 蓝图编写铁律

| # | 铁律 | 违反后果 |
|---|------|---------|
| 1 | 所有路径必须是绝对路径 | 文件创建到错误位置 |
| 2 | 必备链接不可省略 | AI 跳过不读，施工时缺少关键信息 |
| 3 | 蓝图必须是最终设计结果 | 蓝图过厚，关键信息被噪音淹没 |
| 4 | 产出物路径必须与 GOV-DOC-002 一致 | 路径幻觉 |
| 5 | construction_progress 必须与代码实际状态一致 | 重复造轮子或跳过施工 |
| 6 | actual_disk_path 必须与 §11 产出物路径一致 | 搜索失败、导入错误 |
| 7 | 已实现代码不在蓝图中重复——§0.1 标记`已实现`的模块，蓝图只保留接口签名（§4），不复制实现代码 | AI 改蓝图忘改代码，或改代码忘改蓝图 |
| 8 | 临时时态内容执行完毕后从蓝图删除——迁移方案、升级执行计划等临时时态内容，一旦执行完毕即成为历史，从蓝图删除 | 蓝图膨胀，关键信息被历史噪音淹没 |
| 9 | 蓝图内容拆分判定——职责不同→拆分独立蓝图；职责相同→原地升级。判定标准见"蓝图拆分判定标准" | AI 不知道该读哪个蓝图，跨模块影响无法追踪 |

---

## 蓝图拆分判定标准

> 铁律 #9 的操作定义——当蓝图内容超过 ~800 行或包含多个独立职责域时，MUST 执行拆分判定。

### 判定流程

```
STEP 1: 识别职责域
  蓝图中的内容是否属于同一职责域？
  判定标准：该内容的服务对象、变更频率、依赖关系是否与蓝图主体一致？

STEP 2: 职责域判定
  ├ 职责相同（同一模块的升级/扩展）→ 原地升级
  │   条件：服务对象相同 + 变更频率同步 + 依赖关系重叠
  │   操作：在 §17 容量升级附录中增量记录
  │
  └ 职责不同（独立子系统/独立能力域）→ 拆分独立蓝图
      条件（满足任一即触发）：
      a) 有独立的 module_id 前缀（如 CAP-G vs CAP）
      b) 有独立的 Phase 路线图和交付节奏
      c) 有独立的依赖关系图（与蓝图主体的 depends_on 交集 <50%）
      d) 内容超过 100 行且与蓝图主体无直接数据流
      操作：创建子蓝图，本蓝图 §10 依赖关系引用子蓝图

STEP 3: 拆分后验证
  - 拆分出的蓝图 MUST 有独立 frontmatter + 概述 + §0~§18
  - 拆分出的蓝图 belongs_to = 本蓝图 module_id
  - 本蓝图 §10 依赖关系新增子蓝图引用
  - blueprint_registry.yaml 同步更新
```

### 判定示例

| 场景 | 判定 | 理由 |
|------|------|------|
| 容量升级蓝图中"§-2 缺口审计" | **原地** | 服务对象相同（容量升级）+ 变更频率同步 + 依赖关系完全重叠 |
| 容量升级蓝图中"升级章一~十" | **原地** | 升级章是容量升级的核心设计，不是独立子系统 |
| 容量升级蓝图中"跨系统事务Saga" | **拆分评估** | 独立CT-TRANSACTION-001 + 与Orc/Script/Gate多系统交互 + depends_on交集<50% |

---

## ⚠️ 安全删除协议

本蓝图不涉及文件删除。容量升级为纯新增设计。

---

## 必备链接

| # | 文件 | module_id | 版本 | 完整绝对路径 | 编写时用途 |
|---|------|-----------|------|------------|----------|
| 1 | 元数据注册表 | PS-STD-001 | — | `D:\ZephyrAlpha\docs\01_policies_and_standards\rules\trae_043_meta_rule_metadata.yaml` | 编号规则 |
| 2 | 目录结构标准 | GOV-DOC-002 | — | `D:\ZephyrAlpha\docs\01_policies_and_standards\rules\trae_028_doc_structure_naming.yaml` | 路径映射 |
| 3 | 治理方法论 | PS-STD-011 | — | `D:\ZephyrAlpha\docs\01_policies_and_standards\rules\trae_024_methodology_diagnosis.yaml` | MTH-012/013 |
| 4 | 模块 ID 注册表 | — | — | `D:\ZephyrAlpha\docs\02_enterprise_architecture\target-architecture\architecture_model\module_id_registry.yaml` | 编号注册 |
| 5 | 基线蓝图 | MOD-MASTER-002 | — | `D:\ZephyrAlpha\docs\03_modules\_master_blueprint\blueprint_baseline.md` | 现存设计 |
| 6 | 索引蓝图 | MOD-MASTER_BLUEPRINT | — | `D:\ZephyrAlpha\docs\03_modules\_master_blueprint\blueprint.md` | 导航索引 |

---

## 项目中已有类似功能

| # | 已有模块 | 完整绝对路径 | 功能重叠点 | 为什么不能复用 |
|---|---------|------------|----------|-------------|
| 1 | SYS-MASTER-001 §〇 | `D:\ZephyrAlpha\docs\03_modules\_system_master\blueprint.md` | 容量升级方案 | SYS-MASTER §〇 定义系统级容量预算，本蓝图定义集成闭环的容量升级设计 |

---

## 涉及的文件范围

| # | 文件/目录 | 完整绝对路径 | 关系 | 变更类型 |
|---|---------|------------|------|---------|
| 1 | 容量蓝图 | `D:\ZephyrAlpha\docs\03_modules\_master_blueprint\blueprint_capacity.md` | 修改 | 本文件 |
| 2 | 基线蓝图 | `D:\ZephyrAlpha\docs\03_modules\_master_blueprint\blueprint_baseline.md` | 读取 | 依赖 |
| 3 | 索引蓝图 | `D:\ZephyrAlpha\docs\03_modules\_master_blueprint\blueprint.md` | 读取 | 导航 |

### §0.6 四图对齐视图

<!-- AUTOGEN: source=depgraph+dataflow+decision, generator=generate_blueprint_panorama.py, reconciler=sync_panorama_module.py -->

> **自动生成**：本节由 generate_blueprint_panorama.py 从四图真源派生，禁止手写。
> 生成命令：`python scripts/governance/d5_architecture/generators/generate_blueprint_panorama.py MOD-MASTER-003`

#### 四图位置

| 图 | 位置 | 状态 | 链接 |
|----|------|------|------|
| 依赖图 (depgraph) | `blueprint_id=MOD-MASTER-003` 的 1 个 file 节点 | design | `extract_depgraph.py --modules MOD-MASTER-003` |
| 数据流图 (dataflow) | （无节点） | N/A | `apply_dataflowgraph.py --list-datasets` |
| 决策架构图 (decision) | 0 个决策节点 / 1 个决策层 | N/A | `generate_decision_diagram.py` |
| 蓝图 (blueprint) | 本文件 | Active | — |

#### 四核心字段

| 字段 | depgraph 值（真源） | 蓝图 frontmatter 值（声明） | 是否一致 |
|------|-------------------|--------------------------|:-------:|
| module_id | MOD-MASTER-003 | MOD-MASTER-003 | ✅ |
| domain_id | N/A | N/A | ✅ |
| build_status | planned | planned | ✅ |
| file_count | 1 文件 | N/A | — |

> 冲突时以 depgraph 为准（ARCH-056 + ARCH-MM-001 声明 vs 验证框架）。
