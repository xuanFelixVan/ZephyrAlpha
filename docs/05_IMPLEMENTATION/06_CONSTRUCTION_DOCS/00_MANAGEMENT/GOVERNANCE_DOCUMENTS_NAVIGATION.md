---
module_id: GOVERNANCE_DOCUMENTS_NAVIGATION_001
version: 1.0.7
status: Active
created_date: 2026-04-10
last_updated: '2026-04-11'
owner: 文档负责人（可指定）
responsibility:
  - 汇总全库文档治理类真源路径；项目办公室只做导航，不替代 09_AUDIT 等目录
standard_type: 导航索引
applicable_scope: 施工文档 / 蓝图阶段 / 与 AI 协作时的治理查阅
---

# 全库治理文档导航（真源仍在原目录）

> **本页做什么**：把散落在各处的**治理、审计、标准**入口集中成一张「地图」，方便人类与 AI 一键跳转。  
> **本页不做什么**：**不**把 `docs/09_AUDIT` 等整树搬进 `00_MANAGEMENT`，也**不**把治理正文塞进 `01_BLUEPRINTS`（图纸柜只放 `*BLUEPRINT.md` 模块蓝图，见 [图纸柜规则](./01_BLUEPRINTS_REPOSITORY_RULES.md)）。

---

## 原则（请先读）

| 做法 | 是否推荐 | 原因 |
|------|----------|------|
| **蓝图终稿 / 施工门禁** 受控正文放在 `00_MANAGEMENT/CANON/` | ✅ **已定** | 与项目办公室同区，全库唯一真源；见 [CANON/README](./CANON/README.md) |
| 在 `00_MANAGEMENT` 增加**本导航 + 少量施工专用摘要** | ✅ 推荐 | 办公室负责「找得到、链得对」，不复制海量审计正文 |
| 把 `09_AUDIT` **全体**搬进办公室 | ❌ 不推荐 | 破坏审计分区；仅 **CANON 所列** 已迁出，其余仍在 `09_AUDIT` |
| 把治理标准放进 `01_BLUEPRINTS` | ❌ 禁止 | 与图纸柜规则冲突；类型不同（标准/程序 ≠ 模块蓝图） |
| 需要「一条口径」时 | ✅ | 写**短摘要**在办公室，并标明「详版见某路径」 |

---

## 一、施工与蓝图阶段（高优先级）

| 说明 | 路径 |
|------|------|
| 施工门禁（蓝图终稿 / 阶段模型） | [`CONSTRUCTION_GATE_CRITERIA_20260408.md`](./CANON/CONSTRUCTION_GATE_CRITERIA_20260408.md)（项目办公室 **CANON** 真源） |
| 蓝图交付标准（机构精华版，目标态） | [`BLUEPRINT_DELIVERY_STANDARD_INSTITUTIONAL_LITE.md`](./BLUEPRINT_DELIVERY_STANDARD_INSTITUTIONAL_LITE.md) |
| 文档治理架构（L0～L5 分层与边界） | [`DOCUMENT_GOVERNANCE_ARCHITECTURE.md`](./DOCUMENT_GOVERNANCE_ARCHITECTURE.md) |
| 文档仓库目录与放置标准（§2～§4 目录表；**§1 第 5～6 条** Layer/路径分立 + 位置 vs 入链） | [`docs/09_AUDIT/STANDARDS/DOCUMENT_REPOSITORY_LAYOUT_STANDARD.md`](../../../09_AUDIT/STANDARDS/DOCUMENT_REPOSITORY_LAYOUT_STANDARD.md) |
| 文档地图与放置（办公室规程 · **§1.5** / **§1.6** · 与 REPO_WIDE **§2.3.2** 互文 · 与扫描/§7 衔接） | [`DOCUMENT_MAP_AND_PLACEMENT_GOVERNANCE.md`](./DOCUMENT_MAP_AND_PLACEMENT_GOVERNANCE.md) |
| 全局文件治理会话交接（新对话粘贴） | [`GLOBAL_FILE_GOVERNANCE_SESSION_HANDOFF.md`](./GLOBAL_FILE_GOVERNANCE_SESSION_HANDOFF.md) |
| 已锁定治理裁决 | [`docs/09_AUDIT/STATE/GOVERNANCE_DECISIONS_LOCKED_20260408.md`](../../../09_AUDIT/STATE/GOVERNANCE_DECISIONS_LOCKED_20260408.md) |
| OpenClaw 整改执行手册 | [`docs/09_AUDIT/PROCEDURES/OPENCLAW_REMEDIATION_EXECUTION_PLAYBOOK_20260408.md`](../../../09_AUDIT/PROCEDURES/OPENCLAW_REMEDIATION_EXECUTION_PLAYBOOK_20260408.md) |
| 全系统文档审计方案 | [`docs/09_AUDIT/PROCEDURES/FULL_SYSTEM_DOCUMENT_AUDIT_PLAN_20260408.md`](../../../09_AUDIT/PROCEDURES/FULL_SYSTEM_DOCUMENT_AUDIT_PLAN_20260408.md) |
| 全系统审计全案 | [`docs/09_AUDIT/PROCEDURES/FULL_SYSTEM_AUDIT_COMPLETE_CASE_20260408.md`](../../../09_AUDIT/PROCEDURES/FULL_SYSTEM_AUDIT_COMPLETE_CASE_20260408.md) |
| 蓝图阶段文档清洁总案 | [`BLUEPRINT_PHASE_DOCUMENT_HYGIENE_MASTER_PLAN_20260408.md`](./CANON/BLUEPRINT_PHASE_DOCUMENT_HYGIENE_MASTER_PLAN_20260408.md)（项目办公室 **CANON** 真源） |
| 整改任务指令 | [`docs/09_AUDIT/PROCEDURES/DOC_REMEDIATION_TASK_DIRECTIVE_20260408.md`](../../../09_AUDIT/PROCEDURES/DOC_REMEDIATION_TASK_DIRECTIVE_20260408.md) |
| Trae×Cursor 蓝图任务台账 | [`docs/09_AUDIT/STATE/TRAE_BLUEPRINT_TASK_LEDGER_20260408.md`](../../../09_AUDIT/STATE/TRAE_BLUEPRINT_TASK_LEDGER_20260408.md) |
| 接口契约真源（蓝图常链） | [`docs/03_TRADING_TACTICS/API_Contract.md`](../../../03_TRADING_TACTICS/API_Contract.md) |

### 脚本与扫描产物（勿当正文真源）

| 说明 | 路径 |
|------|------|
| L1 治理扫描脚本 | [`scripts/governance/sentinel_l1_governance_scan.py`](../../../../scripts/governance/sentinel_l1_governance_scan.py)（根目录 [`sentinel_l1_governance_scan.py`](../../../../scripts/sentinel_l1_governance_scan.py) 可转发） |
| L1 扫描产物（运行生成；路径以仓库内实际为准） | `docs/09_AUDIT/STATE/SENTINEL_L1_SCAN_20260408.json`、`SENTINEL_L1_SCAN_20260408.md` 等 |
| 蓝图 D 类重叠候选（启发式） | [`scripts/governance/scan_blueprint_d_overlap_candidates.py`](../../../../scripts/governance/scan_blueprint_d_overlap_candidates.py) → `docs/09_AUDIT/STATE/BLUEPRINT_D_OVERLAP_CANDIDATES_*`；规程见 [D 类 Playbook](./D_CLASS_BLUEPRINT_OVERLAP_PLAYBOOK.md) **§2.5、§5**；**方案文件索引**见 [REPO_WIDE §3.4.1](./REPO_WIDE_FILE_GOVERNANCE_TASK_LIST.md) |
| 蓝图 D 类 A 档分流 + 二审队列 JSONL | [`scripts/governance/triage_blueprint_d_overlap_pairs.py`](../../../../scripts/governance/triage_blueprint_d_overlap_pairs.py) → `BLUEPRINT_D_OVERLAP_TRIAGE_*`、`BLUEPRINT_D_OVERLAP_SECOND_PASS_QUEUE_*.jsonl`；二审配合 [D 类二审提示词模板](./D_CLASS_OVERLAP_SECOND_PASS_PROMPT_TEMPLATE.md)；与上条同读 [D 类 Playbook](./D_CLASS_BLUEPRINT_OVERLAP_PLAYBOOK.md) **§3.5** |

---

## 二、`docs/09_AUDIT` 索引（审计区总入口）

| 说明 | 路径 |
|------|------|
| 审计根索引 | [`docs/09_AUDIT/INDEX.md`](../../../09_AUDIT/INDEX.md) |
| 标准索引 | [`docs/09_AUDIT/STANDARDS/INDEX.md`](../../../09_AUDIT/STANDARDS/INDEX.md) |
| 程序 / 流程索引 | [`docs/09_AUDIT/PROCEDURES/INDEX.md`](../../../09_AUDIT/PROCEDURES/INDEX.md) |

**`STANDARDS/`** 下与治理强相关的标准：**完整列表以** [`STANDARDS/INDEX.md`](../../../09_AUDIT/STANDARDS/INDEX.md) **为准**，常见包括（示例，非穷举）：

- `DOCUMENT_REPOSITORY_LAYOUT_STANDARD.md`、`FILE_NAMING_STANDARD.md`
- `DOCUMENT_CLASSIFICATION_STANDARD.md`、`DOCUMENT_GOVERNANCE_PROCESS_STANDARD.md`
- `DOC_GOVERNANCE_MECHANISM.md`、`DOC_ORPHAN_AND_DUPLICATE_GOVERNANCE_PLAYBOOK.md`
- `DUPLICATE_DOCUMENT_HANDLING_STANDARD.md`、`PATH_REFERENCE_STANDARD.md`
- `DOC_REFERENCE_STANDARD.md`、`DOC_NAMING_STANDARD.md`
- `DOCUMENT_METADATA_TEMPLATE.md`
- `RESPONSIBILITY_DESCRIPTION_STANDARD.md`、`RESPONSIBILITY_DESCRIPTION_STANDARD_V2.md`
- `AUDIT_STANDARDS.md`、`COMPLIANCE_AUDIT_SYSTEM.md`、`PERIODIC_AUDIT_MECHANISM.md`、`PERIODIC_CHECK_PLAN.md`

**`PROCEDURES/`** 下程序性文档：**完整列表以** [`PROCEDURES/INDEX.md`](../../../09_AUDIT/PROCEDURES/INDEX.md) **为准**。

**`STATE/`**：台账、快照、`overnight_runs/` 等；体量随时间增长，适合按需在资源管理器或 `git ls-files docs/09_AUDIT/STATE` 浏览。

**`TEMPLATES/`**：治理/审计模板（如 `DOCUMENT_GOVERNANCE_AUDIT_CHECKLIST.md`、`PROFESSIONAL_DOCUMENT_GOVERNANCE_AUDIT_GUIDE.md`、`BLUEPRINT_STANDARD_TEMPLATE.md` 等）。

**`BEST_PRACTICES/`**：如 `DOCUMENT_GOVERNANCE_BEST_PRACTICES.md`。

**`CASE_STUDIES/`**：如 `DOCUMENT_GOVERNANCE_IMPROVEMENT_CASES.md`。

**`TOOLS/`**：工具说明。

**`REPORTS/`**：体量极大；路径模式 `docs/09_AUDIT/REPORTS/*.md`（示例：`SENTINEL_AUTONOMOUS_GOVERNANCE_RUN_20260408.md`）。

---

## 三、合规与编码（`docs/10_GOVERNANCE_COMPLIANCE`）

| 说明 | 路径 |
|------|------|
| 文档编码标准 | [`docs/10_GOVERNANCE_COMPLIANCE/DOCUMENT_ENCODING_STANDARD.md`](../../../10_GOVERNANCE_COMPLIANCE/DOCUMENT_ENCODING_STANDARD.md) |
| 知识库入口 | [`docs/10_GOVERNANCE_COMPLIANCE/KNOWLEDGE_BASE/INDEX.md`](../../../10_GOVERNANCE_COMPLIANCE/KNOWLEDGE_BASE/INDEX.md) |
| 文档治理知识库 | [`docs/10_GOVERNANCE_COMPLIANCE/KNOWLEDGE_BASE/DOCUMENT_GOVERNANCE_KNOWLEDGE_BASE.md`](../../../10_GOVERNANCE_COMPLIANCE/KNOWLEDGE_BASE/DOCUMENT_GOVERNANCE_KNOWLEDGE_BASE.md) |
| 职责审查机制 | [`docs/10_GOVERNANCE_COMPLIANCE/RESPONSIBILITY_REVIEW_MECHANISM.md`](../../../10_GOVERNANCE_COMPLIANCE/RESPONSIBILITY_REVIEW_MECHANISM.md) |
| CI/CD 与治理 | [`docs/10_GOVERNANCE_COMPLIANCE/CI_CD_INTEGRATION/README.md`](../../../10_GOVERNANCE_COMPLIANCE/CI_CD_INTEGRATION/README.md) 等 |

---

## 四、实施侧（路径 / 质量门）

| 说明 | 路径 |
|------|------|
| 路径标准 | [`docs/05_IMPLEMENTATION/02_DEVELOPMENT/PATH_STANDARD.md`](../../02_DEVELOPMENT/PATH_STANDARD.md) |
| 文档质量门 | [`docs/05_IMPLEMENTATION/02_DEVELOPMENT/DOCUMENT_QUALITY_GATE_STANDARD.md`](../../02_DEVELOPMENT/DOCUMENT_QUALITY_GATE_STANDARD.md) |
| 开发标准总览 | [`docs/05_IMPLEMENTATION/02_DEVELOPMENT/DEVELOPMENT_STANDARDS.md`](../../02_DEVELOPMENT/DEVELOPMENT_STANDARDS.md) |
| 施工文档 README | [`docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/README.md`](../README.md) |
| 项目办公室 README | [`README.md`](./README.md) |

---

## 五、运维侧审计状态（历史报告集中区）

| 说明 | 路径 |
|------|------|
| 运维审计状态目录 | `docs/05_IMPLEMENTATION/04_OPERATIONS/audit_state/`（内含大量 `*_GOVERNANCE*`、`*_AUDIT*` 等；按需检索该目录） |

---

## 六、研究与归档中的治理材料

| 说明 | 路径 |
|------|------|
| 研究侧治理文档 | `docs/09_RESEARCH_INNOVATION/DOCUMENT_GOVERNANCE_*.md`（多份；按需 glob） |
| 归档副本 | `docs/06_ARCHIVE/` 下 `*GOVERNANCE*`、`*audit*`、`20260404_audit_reports_archive`、`20260407_*` 等 |

---

## 与「办公室」内已有文档的关系

| 办公室内文档 | 角色 |
|--------------|------|
| [图纸柜规则](./01_BLUEPRINTS_REPOSITORY_RULES.md) | **仅约束** `01_BLUEPRINTS` 摆放 |
| [蓝图终稿定义](./BLUEPRINT_FINAL_SIGNOFF.md) | 终稿门禁（与施工门禁文档互补） |
| [任务清单](./BLUEPRINT_PHASE_CLOSURE_TASK_LIST.md) | 阶段勾选 |
| [文档治理架构](./DOCUMENT_GOVERNANCE_ARCHITECTURE.md) | L0～L5 分层与审计边界（机构参照模型） |
| [文档地图与放置规则](./DOCUMENT_MAP_AND_PLACEMENT_GOVERNANCE.md) | LAYOUT 真源 + **§1.5** + **§1.6**（位置正确性分桶）+ REPO_WIDE **§2.3.2** + 扫描/§7 批次衔接 |
| [D 类蓝图重叠 Playbook](./D_CLASS_BLUEPRINT_OVERLAP_PLAYBOOK.md) + [REPO_WIDE §3.4.1](./REPO_WIDE_FILE_GOVERNANCE_TASK_LIST.md) | D 类：**§2.5** 置信度、**§5** 双轨与 **高置信可合并**；办公室内 **D 类合稿方案文件** 与工具、待审登记、二审模板的一页索引 |
| [执行协议](./BLUEPRINT_CABINET_EXECUTION_PROTOCOL.md) | 防幻觉与图纸柜操作纪律 |
| **本文** | 全库治理类**导航**；详版仍以各目录真源为准 |

---

## 版本记录

| 版本 | 日期 | 说明 |
|------|------|------|
| 1.0.7 | 2026-04-11 | 「脚本与扫描产物」表 D 类两行补 **§2.5 / §5** 与 [REPO_WIDE §3.4.1](./REPO_WIDE_FILE_GOVERNANCE_TASK_LIST.md)；办公室关系表增 D 类 + §3.4.1 一行 |
| 1.0.6 | 2026-04-16 | 原则表与办公室关系表互指 LAYOUT **§1 第 6 条**、放置规程 **§1.6**、REPO_WIDE **§2.3.2** |
| 1.0.5 | 2026-04-10 | 「脚本与扫描产物」表增 D 类 `scan_blueprint_d_overlap_candidates` / `triage_blueprint_d_overlap_pairs` 与二审模板互指 |
| 1.0.4 | 2026-04-10 | 施工与蓝图表、办公室关系表互指 LAYOUT **§1 第 5 条**与 [放置规程 §1.5](./DOCUMENT_MAP_AND_PLACEMENT_GOVERNANCE.md) 同口径 |
| 1.0.3 | 2026-04-10 | 施工与蓝图表增 [全局文件治理会话交接](./GLOBAL_FILE_GOVERNANCE_SESSION_HANDOFF.md) |
| 1.0.2 | 2026-04-10 | 施工与蓝图表增 [文档地图与放置规则](./DOCUMENT_MAP_AND_PLACEMENT_GOVERNANCE.md)；脚本表 L1 路径改 `scripts/governance/`；办公室关系表增一行 |
| 1.0.1 | 2026-04-10 | 施工与蓝图表增文档治理架构；办公室关系表增一行 |
| 1.0.0 | 2026-04-10 | 首版：收纳用户收集路径为导航表，明确不搬迁、不放入图纸柜 |
