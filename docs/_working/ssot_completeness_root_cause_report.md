---
title: SSoT 完整性与改名传播闭环病根调研与裁定报告
doc_type: audit_report
status: active
ttl: task_bound
created_by: agent
created: '2026-06-26'
approved_by: owner
approved_date: '2026-06-26'
module_id: REG-GOV-SSOT-RCA-001
related_adjudication: '#207'
related_rename: '#204 D-SIGNAL* 4 域改名 / #206 派生标识符传播'
related_plan: '.trae/documents/ssot_completeness_rename_propagation_plan.md'
---

# SSoT 完整性与改名传播闭环病根调研与裁定报告

> **文档定位**：裁定#206（blueprint_id/节点路径派生传播）施工规划中，深度调研 apply_depgraph.py / generate_project_depgraph.py / trae_028 时发现 3 个超出#206 范围的架构病根。本报告作为客观架构师调研，从第一性原理出发，对标专业机构与 AI 编程社区，给出裁定#207 与治本施工方案。
>
> **调研方法**：项目内部文档/代码证据挖掘（3 个 Explore agent very thorough，覆盖 onboarding/规则真源/生成器/审计脚本/历史决策）+ 社区实践 WebSearch（数据库 rename 级联最佳实践、CQRS 职责分离模式、ALCOA+ 数据完整性框架、Spec-as-source-of-truth）。所有结论附证据（文件:行号 / 来源 URL / 量化数据）。

---

## 1. 问题陈述

裁定#206 规划阶段，对施工涉及的 3 个核心工具/文档做深度调研时，发现 3 个超出#206 范围的架构病根。用户明确要求：不简单选 A/B/C，要从第一性原理出发做深度调研，对标社区，给裁定与治本方案。

| 问题 | 发现契机 | 核心矛盾 |
|---|---|---|
| 1 改名传播完整性缺口 | 调研 cmd_rename_domain 覆盖范围 | 声明"18步覆盖11表"实际遗漏314行非domain_id命名列 |
| 2 制品生成器破坏性副作用 | 调研 project_entity_depgraph.yaml 重生方式 | 声明"生成器生成制品"实际同时破坏性重建DB |
| 3 SSoT 覆盖范围断裂 | 调研 domain_naming_rules.yaml source_doc 修复 | 声明"trae_028是命名规则SSoT"实际未收录NR-001/003且矛盾 |

3 个问题共享同一深层病根模式：**"声明范围 ≠ 实际覆盖范围，且无机器可执行的完整性校验"**。这是 100% AI 开发项目的头号风险——AI 按"声明"执行，但"声明"与"实际"不符时，AI 无从发现，产生静默数据损坏。

---

## 2. 内部规则真源审计

### 2.1 问题1：改名传播完整性缺口

#### 2.1.1 病根代码证据

[apply_depgraph.py:1302-1321](file:///D:/ZephyrAlpha/scripts/governance/apply_depgraph.py) `cmd_rename_domain` 的 18 步 UPDATE **按列名枚举**——选取标准是"列名含 domain 字样"：

```python
steps = [
    (1, "domains", "domain_id", False),
    (2, "nodes", "domain_id", False),
    (3, "nodes", "subdomain_id", False),
    (4, "nodes", "belongs_to", False),
    ...
    (11, "invariants", "domain_id", False),
    (12, "arch_constraints", "from_domain", False),
    (13, "arch_constraints", "to_domain", False),
    ...
    (18, "rule_bindings", "domain_id", False),
]
```

L1324-1349 执行逻辑只有两种匹配模式：精确等值（`WHERE {col}=?`）和 `REPLACE+LIKE`（仅用于 `domain_events.target_domains` 和 `domain_mapping.subdomain_id`）。**没有任何"扫描全表所有 TEXT 列是否含 old_id 值"的逻辑。**

#### 2.1.2 量化证据：被遗漏列确实承载 domain-id 值（DB 实测）

对 `data/databases/depgraph.db` 只读查询，D-SIGNAL* 4 个旧名改名后的残留：

| 被遗漏的表.列 | 残留行数 | 列性质 | cmd_rename_domain 是否覆盖 |
|---|---|---|---|
| nodes.owner | **114** | 承载 domain-id 值（全表 owner 均为 D-XXX 域ID） | 否 |
| nodes.business_stream | **114** | 承载 domain-id 值 | 否 |
| nodes.tags | **39** | JSON 列表含 domain-id 元素 | 否 |
| invariants.invariant_id | **13** | **PRIMARY KEY**（D-SIGNAL-AP-P0-0） | 否（只覆盖 invariants.domain_id） |
| arch_constraints.constraint_id/name/description | **1+1+1** | PK + 叙事含 domain-id | 否（只覆盖 from/to_domain） |
| domain_events.name/payload_schema | **1+3** | 事件名 + 域列表 | 否（只覆盖 source/target_domains） |
| contracts.schema_definition | **29** | JSON 含 domain-id | 否（只覆盖 provider/consumer_domain） |
| **合计** | **314** | | |

**对照组**（cmd_rename_domain 已覆盖的列，残留均为 0，证明改名本身成功）：
- nodes.domain_id: 0 ✓ ｜ nodes.subdomain_id: 0 ✓ ｜ nodes.belongs_to: 0 ✓ ｜ invariants.domain_id: 0 ✓ ｜ contracts.provider_domain: 0 ✓ ｜ contracts.consumer_domain: 0 ✓

→ 改名成功，但覆盖范围有盲点：314 行残留从未被发现。

#### 2.1.3 项目内已有"值扫描"先例（但未被采用）

同文件 [cmd_cleanup_orphan_edges:975-1021](file:///D:/ZephyrAlpha/scripts/governance/apply_depgraph.py) 是**值扫描先例**——用引用完整性检测孤儿边：

```python
# L1011
OR to_node_id NOT IN (SELECT node_id FROM nodes)
```

即通过"值是否在另一表存在"发现孤儿，而非"列名是否含 node"。这正是 cmd_rename_domain 应采用但未采用的模式。**同一文件内两种检测范式并存，改名命令却选了较弱的列名枚举式。**

#### 2.1.4 验证盲点（为何 314 残留未被发现）

[d_signal_rename_plan.md §4.8](file:///D:/ZephyrAlpha/docs/02_enterprise_architecture/03_governance_reports/d_signal_rename_plan.md) 阶段7 验证步骤原文：

> "7.1 验证 DB 无残留旧 domain_id（**11表需UPDATE全覆盖**，edges为boolean除外）"

验证范围仅限"11 表的 domain_id 命名列"，与 18 步 UPDATE 的盲点**完全重合**。记忆记录的"16 domain columns all CLEAN"正是此盲点的产物——只查了 16 个 domain_id 命名列，314 行非 domain_id 命名列残留从未被检查。

#### 2.1.5 改名传播规则缺失

[blueprint_id_naming_root_cause_report.md:74](file:///D:/ZephyrAlpha/docs/_working/blueprint_id_naming_root_cause_report.md) §2.3 病根#2 已识别：Grep `改名.*传播|传播.*改名|派生.*改名|rename.*propagat` 于 docs/01_policies_and_standards/ → **0 匹配**。项目无任何规则规定改名传播的完整性要求。

AI 改名防护规则方面，trae_007/trae_012 反而是**禁止"顺便重命名"**（防幻觉），与"改名必须完整传播"方向相反——项目有"别乱改名"规则，却无"改名必须改全"规则。

### 2.2 问题2：制品生成器破坏性副作用

#### 2.2.1 破坏性逻辑代码证据

[generate_project_depgraph.py:2634](file:///D:/ZephyrAlpha/scripts/governance/generate_project_depgraph.py) 的 DELETE 是破坏性根源：

```python
# L2632-2636
cursor.execute("DELETE FROM nodes WHERE design_maturity != 'design' OR design_maturity IS NULL")
cursor.execute("DELETE FROM edges WHERE dep_maturity != 'design' OR dep_maturity IS NULL")
```

删除所有**运营态**节点（实测 1428 个 production 节点），仅保留设计态（403 个），然后从磁盘扫描重建。

#### 2.2.2 职责耦合（病根）

generate_project_depgraph.py 在同一脚本中承担两个职责：
- **职责A（制品生成）**：L3503-3558 写 `project_entity_depgraph.yaml`（`yaml.dump(depgraph, f, ...)`）
- **职责B（DB 重建）**：L2601 `write_depgraph_to_db` → L2634 DELETE + INSERT

两者在 main() 流程中顺序执行，**无法单独运行职责A而不触发职责B**。

#### 2.2.3 防护失效

[L3167 PRODUCTION_PROTECTED_FIELDS](file:///D:/ZephyrAlpha/scripts/governance/generate_project_depgraph.py) 只保护 6 字段：

```python
PRODUCTION_PROTECTED_FIELDS = (
    "blueprint_id", "owner", "impact_level", "change_policy",
    "modification_permission", "belongs_to",
)
```

main() L3426-3434 在 DELETE **之前**调用 `load_production_state_from_db` + `apply_production_metadata_protection` 把这 6 个字段恢复到内存，再 INSERT。**时序正确**，但保护范围不足：onboarding STEP 4.15 指出丢失的是 `build_status/module_lifecycle_state`——这两个字段**不在**保护列表中。其他未保护字段还有 business_stream/stream_role/runtime_plane/ddd_aggregate 等。

#### 2.2.4 onboarding STEP 4.15 明令禁止

[onboarding_detail.md:323](file:///D:/ZephyrAlpha/.trae/rules/onboarding_detail.md)：

> "STEP 4.15 — DepMap 依赖图: ⚠️ **禁止运行 generate_project_depgraph.py**（删除运营态节点后重建，但 build_status/module_lifecycle_state 不从文件头部解析，全用默认值 draft/inactive，导致**911个节点手工维护数据丢失**）。用 `python scripts/governance/extract_depgraph.py --summary` 替代"

#### 2.2.5 后果：制品无法安全重生，持续过期，且有真实消费者

制品 project_entity_depgraph.yaml 的 `generated_at: 2026-06-19`，早于裁定#204 改名（06-25），含旧 MOD-SIGNAL*/D-SIGNAL-NN 引用。且有真实代码消费者：

| 消费者 | 位置 | 用途 |
|---|---|---|
| registration_checker.py | [L50](file:///D:/ZephyrAlpha/src/zephyr/security/access_control/orphan_judge/registration_checker.py) | 安全访问控制读取（L75 字符串包含检查判断文件是否注册） |
| audit_trail/pipeline_runner.py | [L99](file:///D:/ZephyrAlpha/src/zephyr/governance/audit_trail/pipeline_runner.py) | 审计链读取 |
| audit_orchestrator/pipeline_runner.py | L98 | 审计编排读取 |

制品过期直接影响安全访问控制的孤儿判定与审计链——"持续过期"是真实风险，不是美观问题。

#### 2.2.6 项目内职责分离先例（但未应用此脚本）

[generate_target_path_tree.py:76](file:///D:/ZephyrAlpha/scripts/governance/generate_target_path_tree.py) 是职责分离范例——**只读** depgraph.db（`SELECT * FROM nodes`），从不 DELETE/写 DB，仅输出 `target_path_tree.yaml`。

[dependency_architecture_panorama.md:1793](file:///D:/ZephyrAlpha/docs/02_enterprise_architecture/dependency_architecture_panorama.md) 已声明职责分离原则：

> "| 生成器内置 parse_arch_tree | 不需要 | **职责分离**：path_tree 独立承担 |"

项目自身已在 path_tree 上践行职责分离，但 project_depgraph 未跟进。

### 2.3 问题3：SSoT 覆盖范围断裂

#### 2.3.1 两个并行 SSoT 互不引用

- [trae_028:1028-1031](file:///D:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_028_doc_structure_naming.yaml) 声明："**所有命名规则以本文件(trae_028)为唯一真源**;其他文件(trae_010/022/030/042)的命名规则段落已删除改为引用本文件"
- [domain_naming_rules.yaml:4](file:///D:/ZephyrAlpha/docs/01_policies_and_standards/_registry/catalogs/domain_naming_rules.yaml) 声明："功能域ID命名规则的**唯一真源（SSoT）**"
- trae_028 `references` 字段（L1105-1109）：`rule_ids: [TRAE-010, TRAE-022, TRAE-030, TRAE-042]`，**不含 domain_naming_rules.yaml，不含 NR-001~NR-005**

两个文件各自声明是命名规则 SSoT，互不引用、互不感知。

#### 2.3.2 SSoT 未收录 NR-001/NR-003

trae_028 gov_doc_003_naming_ssot 的 conditions 共 7 条，**全是格式规则**（域ID格式/模块ID格式/文件名/目录名/Python源文件/代码标识符/YAML字段名）。grep `NR-001|NR-003|无父子|语义独立|domain_naming_rules` 于 trae_028 全文 → **0 匹配**（仅 change_history 命中，非规则正文）。

#### 2.3.3 SSoT 既有规则与 NR-001/NR-003 直接矛盾

trae_028 L1033-1035 "域ID格式"规则原文：

> "pass: **D-XXX_YYY(大写D+大写域缩写+下划线分隔子域)**;示例D-MKT_DATA/D-EX_CORE/D-AUTONOMY_CORE"

"下划线分隔子域"——这**正面允许**子域前缀（D-XXX_YYY），与 NR-001"无父子前缀"（禁 D-SIGNAL_ASHARE）、NR-003"语义独立性"（禁 D-SIGNAL_QUALITY）**直接矛盾**。SSoT 不仅未收录 NR-001/NR-003，其既有规则还与二者冲突。

#### 2.3.4 source_doc 溯源链断裂

domain_naming_rules.yaml 4 处 source_doc（L31/39/47/63）指向 `docs/01_policies_and_standards/rules/trae_011_domain_attribution.yaml`。全项目 Glob `**/trae_011*.yaml` → 只有 `trae_011_code_type_import.yaml`（无关，是代码导入规则），**trae_011_domain_attribution.yaml 从不存在**。

#### 2.3.5 时序证据（SSoT 未随规则演进同步）

trae_028 `gov_doc_change_history_028`（L1010-1011）：

> "GOV-DOC-003 v3.0.0 (2026-06-19): 命名规则唯一真源升级;汇总trae_010/022/030/042命名规则;统一全项目snake_case;**域ID保持大写D-XXX_YYY**;消除12个命名规则矛盾点(C-1~C-12)"

时序：
- 2026-06-19：trae_028 SSoT 升级到 v3.0.0，覆盖格式规则（NR-002 类）
- 2026-06-25：裁定#204 创建 domain_naming_rules.yaml，新增 NR-001（无父子前缀）/NR-003（语义独立性）

SSoT 升级早于 NR-001/NR-003 入库 6 天。**NR-001/NR-003 入库时未回写 trae_028 SSoT**，change_history 也无"新增 NR-001/NR-003"条目——确认从未被收录。

#### 2.3.6 审计机制三重失效

[validate_ssot.py:50-90](file:///D:/ZephyrAlpha/scripts/governance/d5_architecture/validators/validate_ssot.py) 是 SSoT 审计脚本，但**全部检查函数是空桩**：

```python
# L50-51
def validate(self, path=None):
    return ScanReport()        # 返回空报告，不检查任何东西
# L53-54
def check_ssot(self, files=None):
    return []                  # 返回空列表
# L77-90 全部 check_p0_*/check_p1_* 函数均 return []
```

[ssot_issue_tracking.yaml:48-61](file:///D:/ZephyrAlpha/docs/09_audit/state/ssot_issue_tracking.yaml) 显示最后一次扫描 2026-05-05，记录"P0=0, P1=0, P2=0"——**假阴性**，因为 validate_ssot.py 是空桩。[reports/index.md:23](file:///D:/ZephyrAlpha/docs/09_audit/reports/index.md) 确认报告文件"ssot-validation-LATEST.md 从未存在"。

审计机制三重失效：
1. validate_ssot.py 是空桩，不执行任何校验
2. 最后一次扫描 2026-05-05，早于 SSoT 升级(06-19)和 NR-001/NR-003 入库(06-25)
3. 报告文件从未生成

即便 validate_ssot.py 不是空桩，其设计也只查 frontmatter 字段合法性（layer/status/priority），**不查"SSoT 声明覆盖范围 vs 实际规则文件"的一致性**——无法发现 trae_028 漏收 NR-001/NR-003。

---

## 3. 社区实践对标

### 3.1 专业机构：改名完整性 = 依赖地图全扫描

**数据库 rename 最佳实践**（[Linux Code 2026](https://thelinuxcode.com/sql-query-to-rename-a-database-sql-server-postgresql-mysqlmariadb/)）：

> "a rename almost never fails because of the SQL syntax. It fails because you missed one consumer"

改名失败几乎从不因语法，而因漏了一个消费者。强调改名前必须建立"依赖地图"（dependency map）全扫描：
- Writers（写者）：API service, admin UI, background workers, ingestion pipelines, scheduled jobs
- Readers（读者）：BI dashboards, ad-hoc analyst connections, report generators
- Infrastructure layers：connection poolers, proxies, service mesh egress rules
- Operational tooling：backup jobs, restore scripts, schema migration tooling
- External integrations：CDC connectors, replication/subscription tooling

> "The reason this matters: a rename almost never fails because of the SQL syntax. It fails because you missed one consumer."

→ **启示**：cmd_rename_domain 的 18 步列名枚举是"已知消费者"白名单，遗漏了"未知消费者"（列名不含 domain 但值是 domain-id 的列）。治本应补"值扫描兜底"发现所有消费者。

**安全改名策略**（[CSDN 2025](https://ask.csdn.net/questions/8998322)）：

> "阶段一：环境准备与影响评估——扫描所有依赖项：使用SQL查询或自动化脚本分析视图、SP、作业、链接服务器中的数据库引用"

安全改名需"依赖扫描脚本"生成引用报告，而非按已知列名枚举。

### 3.2 AI 编程社区：改名遗漏是头号重构损坏原因

**GitLab 2025 调研**（裁定#206 已引用，1200 团队）：

> **34% AI 辅助重构因"未更新所有重命名实例"而损坏**

正是本项目病根的量化印证——cmd_rename_domain 遗漏 314 行，正是"未更新所有重命名实例"。

**Spec-as-source-of-truth**（[Augment Code 2026](https://www.augmentcode.com/guides/spec-as-source-of-truth-rebuildable-codebase)）：

> "Spec-driven development inverts the traditional workflow by treating specifications as the source of truth and code as a generated or verified secondary artifact."

提出 **Rebuild Test**（重建测试）：删掉 src/，从 spec 能否重生？发散则 spec 有缺口。

> "The rebuild test surfaces a specific category of missing information: implicit decisions."

→ **启示**：同理，删掉 domain_naming_rules.yaml，从 trae_028 SSoT 能否重生 NR-001~NR-005？不能 → SSoT 不完整。这是 SSoT 完整性的可执行验证。

**AuditOwl**（[NeurIPS 2025 agentic code auditing](https://openreview.net/pdf?id=xjCJY8Xxcm)）：

> "We conduct an audit of 100 randomly sampled empirical papers from the NeurIPS 2025 main track... raises 605 discrepancies (averaging 6.1 per paper)... discrepancies we find are heavily dominated by **incompleteness of code and mismatches between what the paper describes and what the code does**."

LLM agent 审计发现"code mismatch paper"是主要问题类别——同理 SSoT mismatch 规则注册表，需自动化审计。

### 3.3 专业框架：CQRS 职责分离 + ALCOA+ 数据完整性

**CQRS 模式**（[Microsoft Azure 架构指南](https://docs.microsoft.com/en-us/azure/architecture/patterns/cqrs)）：

> "**Queries never modify the database.** A query returns a DTO that does not encapsulate domain knowledge."

> "Separate models in different data stores... Separation of the read and write data stores allows you to scale each model to match the load."

CQRS 核心原则：查询（生成制品）不应有副作用（修改源数据）。读模型是写模型的派生投影，重建读模型不应破坏写模型。

> "The read store can be a read-only replica of the write store, or the read and write stores can have a different structure altogether."

→ **启示**：generate_project_depgraph.py 把"只读生成制品"（查询）和"破坏性重建DB"（命令）耦合，违反 CQRS。generate_target_path_tree.py 是正确范例（只读查询无副作用）。

**物化视图模式**（Azure 架构模式）：读模型可独立重建，不影响写模型。制品 = 物化视图 = DB 的只读派生。

**ALCOA+ 框架**（[FDA 数据完整性，IntuitionLabs 2026](https://intuitionlabs.ai/articles/data-integrity-ai-alcoa-framework)）：

| 原则 | 含义 | 对应本项目 |
|---|---|---|
| **Complete** | All necessary data are included (no omissions) | SSoT 必须收录所有规则（NR-001/003 不能遗漏） |
| **Consistent** | Data are recorded uniformly; no unexplained gaps or conflicting entries | SSoT 既有规则不能与 NR-001/003 矛盾 |
| **Traceable** | Records can be traced to their source | source_doc 必须指向存在的源文件 |

ALCOA+ 是受监管行业（制药/生物）的数据完整性金标准，2026 年扩展到 AI/ML。SSoT 作为"规则数据"必须满足 ALCOA+。

### 3.4 业界共识 vs 本项目现状

| 议题 | 业界共识 | 本项目现状 |
|---|---|---|
| 改名完整性 | 依赖地图全扫描，非列名枚举 | 18步列名枚举，遗漏314行 |
| 制品生成 | 查询无副作用（CQRS），读模型独立重建 | 制品生成与DB重建耦合，破坏性 |
| SSoT 完整性 | ALCOA+ Complete/Consistent/Traceable | 未收录NR-001/003且矛盾，source_doc断裂 |
| 完整性校验 | 机器可执行的自动化审计 | validate_ssot.py空桩，假阴性 |
| AI场景防漂移 | 规则机器可读+自动执行（GitLab 2024: -89%违规） | 有声明但无校验，AI按声明执行产生静默损坏 |

---

## 4. 裁定结果

### 4.1 跨问题共同病根

三个问题共享同一深层病根：**"声明范围 ≠ 实际覆盖范围，且无机器可执行的完整性校验"**。

| 问题 | 声明 | 实际 | 缺失的校验 |
|---|---|---|---|
| 1 改名传播 | "18步覆盖11表所有含domain列" | 只覆盖列名含domain的列，遗漏314行 | 无值扫描完整性审计 |
| 2 制品生成 | "生成器生成制品" | 同时破坏性重建DB，制品无法安全重生 | 无职责分离门禁 |
| 3 SSoT | "trae_028是命名规则唯一真源" | 只覆盖7条格式规则，NR-001/003在另一文件且矛盾 | validate_ssot.py是空桩 |

**治本核心**：为每个"声明"建立机器可执行的"覆盖范围完整性校验"。这三项校验都是"机器可执行的闭环"，使 AI 无法再因"声明与实际不符"而产生静默数据损坏——契合 100% AI 开发项目的防幻觉需求。

### 4.2 裁定 #207（已 Owner 拍板 2026-06-26）

#### R1：改名传播完整性

| 裁定项 | 决定 | 依据 |
|---|---|---|
| **R1-1** cmd_rename_domain 新增值扫描兜底 | ✅ 保留18步精确匹配（快），新增全表TEXT列值扫描兜底（全） | 列名枚举是白名单（脆弱），值扫描是黑名单兜底（全） |
| **R1-2** 新增改名完整性审计脚本 | ✅ audit_rename_completeness.py：改名后扫描全表TEXT列残留，0残留才通过 | 业界"依赖地图全扫描"实践 |
| **R1-3** 修复314行存量残留 | ✅ 本次一并修复（裁定#204遗留缺口） | GitLab 34%重构损坏即此问题 |
| **R1-4** WAL/busy_timeout一致性 | ✅ cmd_rename_domain 补 PRAGMA WAL+busy_timeout | 项目铁律：写入脚本必须启用WAL |

#### R2：制品生成器职责分离

| 裁定项 | 决定 | 依据 |
|---|---|---|
| **R2-1** 职责分离 | ✅ 拆为 generate_project_depgraph_artifact.py（只读）+ rebuild_depgraph_from_scan.py（破坏性，默认禁用） | CQRS：Queries never modify DB |
| **R2-2** 制品安全重生 | ✅ 阶段B/C/D后用只读脚本重生制品 | 物化视图模式：读模型独立重建 |
| **R2-3** PRODUCTION_PROTECTED_FIELDS 扩展 | ✅ 扩展至全量手工维护字段 | 防止911节点数据丢失 |
| **R2-4** onboarding STEP 4.15 更新 | ✅ 禁rebuild脚本，允许artifact脚本 | 职责分离后禁令需同步 |

#### R3：SSoT 完整性

| 裁定项 | 决定 | 依据 |
|---|---|---|
| **R3-1** trae_028 补收录 NR-001/NR-003 | ✅ 新增"域ID语义完整性"condition，修正"下划线分隔子域"矛盾 | ALCOA+ Complete+Consistent |
| **R3-2** source_doc 修复 | ✅ 4处失效source_doc指向trae_028（此时已收录，溯源链闭合） | ALCOA+ Traceable |
| **R3-3** validate_ssot.py 修复 | ✅ 修复空桩，新增SSoT覆盖范围一致性校验 | AuditOwl自动化审计 |
| **R3-4** 派生标识符规则入SSoT | ✅ trae_028新增gov_doc_003_derived_identifiers+rename_propagation | 裁定#206 B-5/B-6 |

---

## 5. 治本施工方案

本方案与裁定#206（派生标识符传播）合并施工，统一分阶段（Owner 已确认 A→B→C→D 顺序）：

### 阶段 A：规则治本 + SSoT 完整性（低风险）

| 步骤 | 内容 | 文件 |
|---|---|---|
| A1 | trae_028 补收录 NR-001/NR-003（域ID语义完整性condition），修正"下划线分隔子域"矛盾 | trae_028 L1022-1074 |
| A2 | trae_028 新增 gov_doc_003_derived_identifiers + gov_doc_003_rename_propagation section | trae_028 L1074后 |
| A3 | domain_naming_rules.yaml 4处失效source_doc 修复 → 指向 trae_028 | domain_naming_rules.yaml L31/39/47/63 |
| A4 | 创建 derived_identifier_registry.yaml（派生标识符关系表） | _registry/catalogs/ |
| A5 | sync_yaml_to_depgraph.py 新增 sync_derived_identifier_registry(cur) | sync_yaml_to_depgraph.py L855后 |
| A6 | 修复 check_naming_convention.py N-06（强制数字序号制）+ 新增 N-17（blueprint_id格式校验） | check_naming_convention.py L248-298, L841-859 |
| A7 | 修复 validate_ssot.py 空桩，新增 SSoT 覆盖范围一致性校验 | validate_ssot.py L50-90 |
| A8 | bump trae_028 version 1.1.0→1.2.0 + change_history 追加 | trae_028 L3, L1119, L1121 |
| A9 | 同步 yaml 到 DB | sync_yaml_to_depgraph.py |

### 阶段 B：改名传播完整性修复（中风险）

| 步骤 | 内容 | 文件 |
|---|---|---|
| B1 | cmd_rename_domain 新增"全表TEXT列值扫描兜底"逻辑 | apply_depgraph.py L1302-1321后 |
| B2 | 新增 --propagate-rename 子命令（blueprint_id精确值映射，禁止子串REPLACE） | apply_depgraph.py |
| B3 | cmd_rename_domain 补 WAL/busy_timeout | apply_depgraph.py L1364 |
| B4 | 创建 audit_rename_completeness.py | scripts/governance/ |
| B5 | 修复314行存量残留 | depgraph.db |
| B6 | 执行 blueprint_id 传播（95行+4行） | depgraph.db |
| B7 | 循环审查（CIRCULAR_ACCEPTANCE_ROUNDS=2）至0残留 | audit_rename_completeness.py |

### 阶段 C：制品生成器职责分离（中风险）

| 步骤 | 内容 | 文件 |
|---|---|---|
| C1 | 拆分 generate_project_depgraph.py：提取只读制品生成逻辑为 generate_project_depgraph_artifact.py | 新文件 |
| C2 | 原脚本重命名 rebuild_depgraph_from_scan.py，默认禁用需--force | 重命名 |
| C3 | 扩展 PRODUCTION_PROTECTED_FIELDS 至全量手工维护字段 | rebuild脚本 |
| C4 | 更新 onboarding STEP 4.15 禁令 | onboarding_detail.md L323 |
| C5 | 用新只读脚本重生 project_entity_depgraph.yaml + target_path_tree.yaml | data/asset_index/ |

### 阶段 D：节点路径改名传播（高风险，重新编号，本次执行）

| 步骤 | 内容 |
|---|---|
| D1 | 全量扫描确认：仅 nodes.path(75) + blueprint_links.blueprint_path(1) + alpha_signal_pipeline.py:4 需传播；edges不受影响（用node_id INTEGER） |
| D2 | 建立旧路径→新路径映射表（按域内顺序重新编号 D-XXX-01,-02...），人工核对 |
| D3 | --propagate-rename 扩展支持节点路径重新编号 |
| D4 | dry-run 确认 → 执行 |
| D5 | 更新 src/zephyr/factor/alpha_signal_pipeline.py:4 的 [DEPENDENCIES] 节点路径引用 |
| D6 | 重新生成制品 |
| D7 | 循环审查至0残留 |

### 阶段 E：module_id 立议题（不施工）

登记为 #ARCH-XXX 议题，独立裁定（裁定#206 B-4 已拍板）。

---

## 6. 防再发机制

1. **改名完整性闭环**：apply_depgraph.py `--rename-domain` 执行后自动调用 audit_rename_completeness.py，未通过则阻断 COMPLETED
2. **制品生成器职责分离门禁**：pre-commit 检查 generate_project_depgraph_artifact.py 不含 DELETE/INSERT 语句
3. **SSoT 覆盖范围巡检**：定期运行 validate_ssot.py（修复后），对比 SSoT 声明 vs 规则注册表覆盖范围
4. **AGENTS.md 显式声明**：增加"声明范围 = 实际覆盖范围"完整性原则段落

---

## 7. 回滚预案

- 每阶段前 `git commit` 备份 depgraph.db（项目铁律：改 depgraph 前必备份）
- 阶段B/D 用 apply_depgraph.py 的 dry-run 预览影响范围
- 阶段D 节点路径重新编号若引发引用断裂，通过 audit_rename_completeness.py 检测残留，回滚至备份
- 阶段C 拆分脚本保留原文件 git 历史，可 revert

---

## 8. Owner 确认记录（2026-06-26）

本报告已由 Owner 拍板（status: active），决策如下：

1. **裁定#207 范围**：✅ **合并为裁定#207，与#206配套施工**。3个问题共同病根是"声明≠实际+无完整性校验"，合并治本更系统。
2. **阶段顺序**：✅ **A→B→C→D**。规则先立→改名完整性+blueprint_id传播→制品生成器分离→节点路径改名（重新编号）→用分离后的只读脚本重生制品。逻辑闭环（D6重生制品依赖C的只读脚本）。
3. **正式调研报告**：✅ **本报告即为独立调研报告**（含完整社区对标引文、量化证据），与 plan 文件配套。

→ 施工按 §5 阶段 A→B→C→D 顺序执行，阶段 E 另立议题。

---

## 附录 A：证据索引

| 编号 | 证据 | 位置 |
|---|---|---|
| E1 | cmd_rename_domain 18步列名枚举 | apply_depgraph.py:1302-1321 |
| E2 | 314行残留量化（nodes.owner 114等） | depgraph.db 实测 |
| E3 | cmd_cleanup_orphan_edges 值扫描先例 | apply_depgraph.py:975-1021 |
| E4 | 验证盲点（验证范围=UPDATE范围） | d_signal_rename_plan.md §4.8 |
| E5 | generate_project_depgraph.py DELETE破坏性 | generate_project_depgraph.py:2634 |
| E6 | 职责耦合（制品生成+DB重建） | generate_project_depgraph.py L2601+L3503 |
| E7 | PRODUCTION_PROTECTED_FIELDS 只保护6字段 | generate_project_depgraph.py:3167 |
| E8 | onboarding STEP 4.15 禁令 | onboarding_detail.md:323 |
| E9 | 制品真实消费者 | registration_checker.py:50, pipeline_runner.py:99 |
| E10 | generate_target_path_tree.py 职责分离范例 | generate_target_path_tree.py:76 |
| E11 | 两个并行SSoT互不引用 | trae_028:1028-1031 + domain_naming_rules.yaml:4 |
| E12 | SSoT未收录NR-001/NR-003 | grep 0匹配 |
| E13 | SSoT既有规则与NR-001/003矛盾 | trae_028:1033-1035 vs NR-001/NR-003 |
| E14 | source_doc溯源断裂 | domain_naming_rules.yaml:31/39/47/63 |
| E15 | SSoT未随规则演进同步（时序） | trae_028 change_history L1010 |
| E16 | validate_ssot.py 空桩 | validate_ssot.py:50-90 |
| E17 | 审计三重失效 | ssot_issue_tracking.yaml:48-61 |
| E18 | 数据库rename最佳实践"missed one consumer" | https://thelinuxcode.com/sql-query-to-rename-a-database-sql-server-postgresql-mysqlmariadb/ |
| E19 | CQRS "Queries never modify database" | https://docs.microsoft.com/en-us/azure/architecture/patterns/cqrs |
| E20 | ALCOA+ Complete/Consistent/Traceable | https://intuitionlabs.ai/articles/data-integrity-ai-alcoa-framework |
| E21 | Rebuild Test（SSoT完整性验证） | https://www.augmentcode.com/guides/spec-as-source-of-truth-rebuildable-codebase |
| E22 | AuditOwl agentic code auditing | https://openreview.net/pdf?id=xjCJY8Xxcm |
| E23 | GitLab 34% AI重构损坏 | 裁定#206已引用 |
