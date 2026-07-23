---
module_id: GOV-037
title: ZephyrAlpha SSoT 权威图 (Single Source of Truth Authority Map)
version: 2.7.0
status: Active
date: "2026-06-23"
owner: ZephyrAlpha-Owner
layer: cross_layer
classification: confidential
language: zh
created_by: human_plus_agent
valid_from: "2026-04-24"
ttl: permanent
summary: 定义跨文件受保护字段的权威来源（Authority Source）与合法值集合，作为 validate_ssot.py 校验规则配置
tags:
  - ssot
  - authority-map
  - governance
  - validation
  - enterprise-architecture
  - contradiction-tracking
---

# ZephyrAlpha SSoT 权威图 (Single Source of Truth Authority Map)

> **用途**：定义跨文件受保护字段的权威来源（Authority Source）与合法值集合。
> `scripts/governance/d5_architecture/validate_ssot.py` 使用本文件作为校验规则配置。
> 每次修改本文件需同步更新上述脚本并重新运行验收测试。
> **Stage H（2026-04-25）路径对齐完成**：全部 6 处旧体系 `docs/02_ARCHITECTURE/*` / `docs/_working/audit/state/module_id_registry.json` 引用已替换为项目真源；`module_id` 从 `ARCH_SSOT_AUTHORITY_MAP` 迁移为 `STD-SSOT-AUTHORITY-MAP`（符合 file-naming-standard v2.0.1 §四 `STD-*` 命名空间）。
> **v2.0（2026-05-03）**：`docs/_working/audit/state/` 已废弃——SQLite DB 迁移至 `data/databases/governance.db`（KBG-0030 §4.1）。上述 Stage H 引用中的 `docs/_working/audit/state/module_id_registry.json` 的历史上下文保留于此作为审计追踪。

---

## 一、层架构权威 (Layer Authority)

> **🔷 单树声明（2026-06-30 治本，双树已合并）**：仓库中仅存在一棵 `architecture_model/`（仓库根），是架构模型唯一存储位置（canonical SSoT，纯 YAML 数据树）。原 EA 树 `docs/02_enterprise_architecture/target_architecture/architecture_model/` 已合并至根树：artifacts（contracts/cross_cutting/domain/events/technology/module_id_registry）迁入根树顶层子目录，`index.yaml` 与根树 v2.0.0 融合为 v3.0.2（53域 + 12 partitions + b_track 12 模块）。
>
> | 树 | 路径 | SSoT 角色 |
> |----|------|-----------|
> | **架构模型树（合并后单树）** | 仓库根 `architecture_model/` | 全部架构模型 YAML SSoT：53域清单（depgraph 派生）、跨层契约（`contracts/`）、不变量（`cross_cutting/invariants.yaml`）、能力热力图（`cross_cutting/capability_heatmap.yaml`）、`module_id_registry.yaml`、技术选型（`technology/`）、领域事件（`events/`）、DDD 模型（`domain/`）、b_track 12 模块施工视图（`layers/b_*.yaml`）。**人读视图在 `docs/02_enterprise_architecture/` 树，本树只允许 .yaml**（`directory_contract.yaml` 强制）。 |
>
> **`AGENTS.md` §6** 中的 `architecture_model/` 统一指根树（合并后无歧义）。`scope.yaml` 已删除（双树分工声明失效）。layers YAML 默认指根树 `layers/b_*.yaml`（b_track 施工视图）。

> **⚠️ §2.1 裁定（2026-06-22）**：52 域是唯一物理分类体系，14 层（L00-L13）降级为域的 `layer_id` 属性，不再作为并行分类体系。本节 `layer` 字段的 `valid_values`（L00-L13 + shared + cross_layer）保留作为**域的属性枚举**，不是分类体系。物理分类由 `depgraph` 的 `domains` 表（52 域）定义。AI 找模块只有一条路：按域找。

**权威来源（层 ID / frontmatter `layer` 合法值）**：根树 `architecture_model/index.yaml`（v3.0.2，domains 列表的 `layer_id` 字段）+ `depgraph.db` domains 表（layer_id 列）。14 层（L00~L13 + shared + cross_layer）作为域属性枚举保留，物理分类由 53 域定义。原 EA 树 `layers/l{00..13}-*.yaml` + `layers/shared.yaml` 已随 c_track 删除（Phase 0+1 治本，14 层降级为域属性，不再需要独立 layers 文件）。

> **大小写约定**：本节 `valid_values` 使用大写 `L00`~`L13`（架构标识符惯例）。`_index.yaml` 分区 `id` 使用小写 `l00`~`l13`（文件系统标识符惯例）。两者指代同一事物，大小写差异是有意设计：大写用于架构层 ID（受保护字段），小写用于 YAML 分区 id（文件系统路径组件）。（注：`_schema.yaml` v3.0.0 已移除 `layer` 字段——模块级 layer 冗余，层归属由 partition id 承载。此大小写约定仍适用于 frontmatter `layer` 字段。）

> 本节 Layer 列表为 14 层（L00-L13 + shared + cross_layer）属性枚举，L12 (system-telemetry) / L13 (experiment-pipeline) / shared 已增补。原 Stage J 升级任务已完成。**注意**：14 层是域的 `layer_id` 属性，不是物理分类体系。物理分类由 52 域定义。

| 层 ID     | 层名（英文）              | 层名（中文）   | 权威状态 |
|-----------|--------------------------|--------------|---------|
| L00       | Data Source Layer        | 数据源层       | Active  |
| L01       | Infrastructure Layer     | 基础设施层     | Active  |
| L02       | Alpha Factor Layer       | Alpha 因子层  | Active  |
| L03       | Signal Generation Layer  | 信号生成层     | Active  |
| L04       | Risk Management Layer    | 风险管理层     | Active  |
| L05       | Portfolio Construction   | 组合构建层     | Active  |
| L06       | Trade Execution Layer    | 交易执行层     | Active  |
| L07       | Post-Trade Analytics     | 交易后分析层   | Active  |
| L08       | Human-AI Interface       | 人机接口层     | Active  |
| L09       | Research & Innovation    | 研究创新层     | Active  |
| L10       | Governance & Compliance  | 治理合规层     | Active  |
| L11       | ML Platform              | ML 平台层     | Active  |
| L12       | System Telemetry         | 系统遥测层     | Active  |
| L13       | Experiment Pipeline      | 实验管线层     | Active  |
| shared    | Shared Concerns          | 共享关注点     | Active  |
| cross_layer | Cross-Layer Concerns   | 跨层关注点     | Active  |

### 受保护字段

```yaml
protected_field: layer
authority_file: architecture_model/index.yaml
authority_file_layers_dir: architecture_model/layers/
valid_values:
  - L00
  - L01
  - L02
  - L03
  - L04
  - L05
  - L06
  - L07
  - L08
  - L09
  - L10
  - L11
  - L12
  - L13
  - shared
  - cross_layer
violation_severity: P0  # 层 ID 不在有效集合中
```

> **派生规则**：此 `valid_values` 列表从 `_index.yaml` → `partitions` 自动派生。
> 映射关系：`l00`→`L00` ... `l13`→`L13` + `shared`→`shared`。
> `cross_layer` 为架构级概念（非 partitions 直接条目），作为合法层值单独保留。
> **新增层时**：先在 `_index.yaml` partitions 中添加条目 → 再据此更新本列表。
> 禁止仅更新本列表而不更新 `_index.yaml`。

---

## 二、状态字段权威 (Status Authority) — 文档生命周期状态

> ⚠️ **scope 声明**：本节定义的是【文档生命周期状态】（Markdown/YAML 文件的 frontmatter 元数据），适用于 `docs/` 下所有文档。
> 这与 `architecture_model/layers/schema.yaml` 定义的【代码模块实现状态】（planned/candidate/approved/in_development/active/completed/deprecated）
> 是两套完全不同的枚举。字段名都叫 `status`，但适用对象不同——混淆会导致 CI 误报或不报。
> 判断标准：看你读的文件是"文档本身"还是"描述代码模块的数据条目"。前者用本节枚举，后者用 `_schema.yaml`。

**权威来源**：`docs/01_policies_and_standards/` 目录下各 standard 文件（status 枚举由各标准文档自带分散定义；Stage J 建议合并至单独 `status-lifecycle-standard.md`）

| 状态值       | 含义                          | 允许场景         |
|-------------|-------------------------------|----------------|
| Draft       | 草稿，未经审核                  | 施工前期         |
| Review      | 审核中                        | 等待 Owner 批准  |
| Active      | 已批准并生效                   | 正式使用         |
| Superseded  | 已被更新版本替代                | 保留历史         |
| Deprecated  | 废弃，不应引用                  | 淘汰中           |
| Retired     | 已归档，不再维护                | 历史存档         |
| proposed    | 提议阶段（注册表专用）           | 注册表           |

### 受保护字段

```yaml
protected_field: status
authority_file: docs/01_policies_and_standards/  # 待落地：Stage J 合并为 status-lifecycle-standard.md 后更新为具体文件路径
valid_values:
  - Draft
  - Review
  - Active
  - Superseded
  - Deprecated
  - Retired
  - proposed
violation_severity: P1  # 无效状态值

adr_status_mapping: |
  KB 决策记录（doc_type: audit_report）使用独立生命周期：proposed → accepted → superseded → deprecated → skipped/reserved。
  在 KB 决策记录 frontmatter 中，status: active 语义等价于 accepted（已批准且为当前决策依据），允许混用。
  推荐：新 KB 决策记录使用 accepted，已存在的 active 声明无需批量迁移。

registry_status_mapping: |
  注册表文件（doc_type: register）允许小写状态值（active/deprecated/planned），
  语义等价于对应大写值。此为注册表惯用约定，非独立枚举。
```

---

## 三、优先级字段权威 (Priority Authority)

**权威来源**：本文件 §七 优先级严重性定义（P0/P1/P2/P3 四级）。

| 值  | 含义                     |
|-----|--------------------------|
| P0  | 必须（beta 施工必需）  |
| P1  | 重要（应该完成）          |
| P2  | 可以（将来完成）          |
| P3  | 可删除（永不会用）        |

### 受保护字段

```yaml
protected_field: priority
valid_values: [P0, P1, P2, P3]
violation_severity: P1
```

---

## 四、技术决策权威 (KB 决策记录 Authority)

**权威来源**：KB:decisions namespace（SQLite `knowledge` 表，category="architecture_decision"）
- **编号空间**：KBG-0001 ~ KBG-0041（33 个 VERIFIED entries，已从物理 adr/ 目录迁入）
- 41 个编号 ≠ 33 条 entry——前者是编号范围，后者是实际登记条目。8 个差值 = KBG-0006 (skipped) + KBG-0023~0029 (7 reserved)

### 受保护字段

```yaml
protected_field: kb_reference
authority_file: KB:namespace=decisions
check_rule: >
  任何文件引用 ADR-XXX 时，该 KB 决策记录的 status 必须与权威来源一致。
  不得引用 Deprecated KB 决策记录作为当前决策依据。
violation_severity: P1
```

---

## 五、Module ID 跨文件一致性

**权威来源**：根树 `architecture_model/module_id_registry.yaml`（Stage D 后统一到 YAML SSoT，替代旧体系 JSON 注册表；2026-06-30 从 EA 树迁入根树）

```yaml
protected_field: module_id
authority_file: architecture_model/module_id_registry.yaml
check_rules:
  - rule: no_duplicate_active   # 同一 module_id 不得在两个 Active 文件中出现
    severity: P0
  - rule: consistent_layer      # 同一 module_id 在多文件中 layer 字段必须一致
    severity: P1
  - rule: consistent_status     # 同一 module_id 在多文件中 status 不得矛盾
    severity: P1
```

---

## 六、版本字段格式

**权威格式**：语义版本（Semantic Versioning）`MAJOR.MINOR.PATCH`

```yaml
protected_field: version
format_regex: "^[0-9]+\\.[0-9]+\\.[0-9]+$"
also_accept:
  - "'1.0.0'"   # YAML 字符串引号包裹形式
  - "N/A"       # 非版本化文件
violation_severity: P2
```

---

## 七、矛盾严重性定义

| 级别 | 含义                               | 处置                              |
|------|----------------------------------|----------------------------------|
| P0   | 严重矛盾——阻塞 beta 完成门禁     | `--ci` 模式 exit(1)；必须立即修复  |
| P1   | 重要矛盾——影响可信度，需尽快修复     | 报告并创建修复任务                 |
| P2   | 建议改进——不影响功能，可按优先级处理  | 报告，低优先级处理                 |

---

## 八、活跃 SSoT 矛盾追踪清单

> ⚠️ **scope 声明**：本节是【临时审计追踪】——记录尚未解决的矛盾，便于日常施工时快速查找。本文件的 canonical 职责是"定义受保护字段的权威来源与合法值"，矛盾追踪是附加功能。矛盾解决后应移入 §八（附）已解决归档，不应长期驻留活跃清单。
>
> 📋 **矛盾追踪已归档**：原 `ssot_contradiction_tracker.yaml` 已删除，内容归档至 `architecture_upgrade_discussion.md` §22.13.4。

> 仅列出**未解决**的矛盾。已解决的条目见 §八（附）"已解决的矛盾（历史归档）"。
> 来源：`ssot-contradiction-fix-workorder.md`（已融入本文件后删除）

| ID | 矛盾描述 | 权威来源 | 修复方案 | 状态 | 执行阶段 | 负责人 |
|:---|:---|:---|:---|:---:|:---|:---:|
| SSoT-001 | 层编号双轨制（旧体系 T.XX.XXXX vs 当前项目 L00-L13） | 当前项目 L00-L13 编号系统（§2.1 裁定后降级为域属性） | beta 统一迁移，旧体系编号标记 deprecated alias；14 层降级为域的 `layer_id` 属性，52 域为唯一物理分类 | 🔧 | §2.1 裁定 | Owner |
| SSoT-002 | 模块数量不一致（MODULE_INVENTORY vs 候选池清单） | module_id_registry.yaml | experimental 填充时统一注册 | ⏳ | experimental | Owner |
| SSoT-004 | pre-commit hooks 冗余（12→5） | 简化后 5 个核心 hooks | P0C5 执行简化 | 🔧 | scaffold | AI |
| SSoT-006 | 依赖关系未声明 | _schema.yaml depends_on | experimental 填充时声明 | 🔧 | experimental | AI |
| SSoT-007 | OSS 候选信息分散 | _schema.yaml oss_candidate | experimental 填充时关联 | 🔧 | experimental | AI |

### 八（附）已解决的矛盾（历史归档）

> 以下条目已确认修复并验证通过，保留在此作为审计轨迹。不再作为活跃问题追踪。

| ID | 矛盾描述 | 修复方案 | 解决日期 | 执行阶段 |
|:---|:---|:---|:---|:---|
| SSoT-003 | 架构层定义分散 | v1.0 已归档到 archive/reorg-2026-04-24/；当前统一在 `_index.yaml` v2.0 + `layers/*.yaml` | 2026-04-25 | Stage D-d |
| SSoT-005 | 文档命名大小写混用 | 新文件强制小写 snake_case(命名规则真源见trae_028_doc_structure_naming.yaml gov_doc_003_naming_ssot)，老文件搬迁时重命名；由 `scripts/governance/d3_metadata/check_naming_convention.py` 自动检查 | 2026-06-19+ | 持续 |

---
## 变更历史

| 版本  | 日期       | 变更                          |
|-------|------------|------------------------------|
| 1.0.0 | 2026-04-24 | 初版；覆盖 Layer/Status/Priority/KB 决策记录/ModuleID/Version 六类检查 |
| 2.0.0 | 2026-04-25 | **Stage H 路径对齐大版本**：(1) `module_id` `ARCH_SSOT_AUTHORITY_MAP` → `STD-SSOT-AUTHORITY-MAP`（符合 file-naming-standard v2.0.1 §四 合法命名空间）；(2) Layer Authority 真源 `docs/02_ARCHITECTURE/module-inventory.md` → `architecture_model/index.yaml` + `layers/*.yaml`；(3) KB 决策记录 Authority 真源 `docs/02_ARCHITECTURE/tech-decision-records.md` → `docs/02_enterprise_architecture/adr/index.md`（41 条 KB 决策记录 扁平编号）；(4) Module ID Registry 真源 `docs/_working/audit/state/module_id_registry.json` → `architecture_model/module_id_registry.yaml`（YAML SSoT 替代 JSON）；(5) Status 与 Priority 权威节点明确标注旧体系路径已归档 + Stage J 合并议程；(6) 第四节加入过渡说明，KBG-001~005 旧快照转为历史遗留表格，当前权威指向新索引。 |
| 2.1.0 | 2026-04-28 | **14 层升级**：Layer 列表从 12 层（L00-L11 + cross_layer）升级到 14 层（L00-L13 + shared + cross_layer）；增补 L12 (System Telemetry)、L13 (Experiment Pipeline)、shared (Shared Concerns)；`valid_values` 同步更新；与 `validate_ssot.py` 的 `VALID_LAYERS` 对齐。原 Stage J 升级任务已完成。 |
| 2.2.0 | 2026-05-01 | **融入清理**：§八 新增"已知 SSoT 矛盾追踪清单"，融入 `ssot-contradiction-fix-workorder.md` 的 7 条矛盾记录后删除该文件。 |
| 2.3.0 | 2026-05-02 | **审计修复批次**：(1) §一 移除 `layer_01` 历史误标（旧体系过渡期已结束，不再需要保留错误值）；(2) §八 拆分为"活跃矛盾清单"（5 条未解决）+ "已解决归档"（2 条已修复），解决权威定义与审计报告混合的责任漂移问题；(3) frontmatter `date` 同步更新至 2026-05-02。 |
| 2.4.0 | 2026-05-02 | **审计修复批次 2**：(1) §二 新增 scope 声明——文档生命周期状态 ≠ 代码模块实现状态（_schema.yaml），消除字段名相同但枚举不同的歧义隐患；(2) §四 KB 决策记录 计数从模糊的"共 41 个编号"改为显式分解"41 编号 = 33 entry + 1 skipped + 7 reserved"，消除两个数字导致的困惑；(3) §八 新增 scope 声明——矛盾追踪是临时附加功能，非本文件 canonical 职责。 |
| 2.5.0 | 2026-05-03 | **审计修复批次 3**：(1) §一 新增 `valid_values` 派生规则声明——明确此列表从 `_index.yaml` partitions 派生，新增层时必须先更新 `_index.yaml` 再据此更新本列表，消除独立维护导致的漂移风险；(2) 标记 `cross_layer` 为"架构级概念（非 partitions 直接条目）"，解释其为何不直接从 partitions 派生。 |
| 2.6.0 | 2026-05-06 | **AUDIT-04 全量修复**：§一 增补双树（EA 树 vs 施工树）权威表 + 与 `scope.yaml` / `AGENTS.md` §6.9 的读法约定，消除「单一路径」误读。 |
| 2.7.0 | 2026-06-23 | **§2.1 裁定对齐**：§一 增补 §2.1 裁定声明——52 域为唯一物理分类体系，14 层（L00-L13）降级为域的 `layer_id` 属性；`valid_values` 保留作为域属性枚举；§八 SSoT-001 状态更新为 🔧（修复中），反映 14 层降级。 |
