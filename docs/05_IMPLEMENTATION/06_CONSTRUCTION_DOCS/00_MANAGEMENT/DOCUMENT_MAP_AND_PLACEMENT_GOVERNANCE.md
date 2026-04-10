---
module_id: DOCUMENT_MAP_PLACEMENT_GOVERNANCE_001
version: 1.0.0
status: Active
created_date: 2026-04-10
last_updated: '2026-04-10'
owner: 文档负责人（可指定）
responsibility:
  - 将「文档地图 + 放置规则」与扫描、任务清单、办公室流程显式对齐（衔接真源，不复制目录学全文）
standard_type: 操作规程
applicable_scope: 全仓库 Markdown/实施文档的路径决策；与整仓尽治、蓝图终稿、卫生批次并列使用
---

# 文档地图与放置规则 — 办公室规程

> **本文件做什么**：把机构常用的 **「先定地图与放置规则，再盘点与搬迁」** 落实为**可执行衔接**——说明**真源在哪**、**与哪些任务/脚本联动**、**一批文件怎么从扫描走到归位**。  
> **本文件不做什么**：**不**替代 [`DOCUMENT_REPOSITORY_LAYOUT_STANDARD.md`](../../../09_AUDIT/STANDARDS/DOCUMENT_REPOSITORY_LAYOUT_STANDARD.md) 中的目录职责表全文；表内细节以该标准为 **single source of truth**。

---

## 1. 真源层级（发生冲突时的查阅顺序）

| 优先级 | 主题 | 真源路径 |
|--------|------|-----------|
| **A** | **`docs/` 一级目录、`05_IMPLEMENTATION` 关键子目录、阶段默认落盘** | [`docs/09_AUDIT/STANDARDS/DOCUMENT_REPOSITORY_LAYOUT_STANDARD.md`](../../../09_AUDIT/STANDARDS/DOCUMENT_REPOSITORY_LAYOUT_STANDARD.md) |
| **B** | **正式图纸柜 `01_BLUEPRINTS` 根目录允许项、过程稿去向** | [`01_BLUEPRINTS_REPOSITORY_RULES.md`](./01_BLUEPRINTS_REPOSITORY_RULES.md) |
| **C** | **路径格式、代码与文档路径习惯** | [`PATH_STANDARD.md`](../../02_DEVELOPMENT/PATH_STANDARD.md)（代码部分）、[`FILE_NAMING_STANDARD.md`](../../../09_AUDIT/STANDARDS/FILE_NAMING_STANDARD.md) |
| **D** | **蓝图阶段放行前与「放置」相关的完成项** | [施工门禁 §0.1a](./CANON/CONSTRUCTION_GATE_CRITERIA_20260408.md) |
| **E** | **删稿 / 保留 / stub**（与「放错」不同，但搬迁批次常同时遇到） | [`FILE_DELETION_OR_RETENTION_PLAYBOOK.md`](./FILE_DELETION_OR_RETENTION_PLAYBOOK.md) |

**新类型文档、标准表尚未覆盖的目录**：须先更新 **LAYOUT 标准 §6** 或在技术决策记录中**书面增行**，再创建新文件夹（与门禁 §0.1a 一致）。

---

## 2. 「文档地图」在本仓库指什么

| 地图形态 | 用途 | 典型入口 |
|----------|------|----------|
| **物理树（路径前缀）** | 拆队列、看哪棵子树最大 | [`REPO_DIRECTORY_ROLLUP_*.md`](../../../09_AUDIT/STATE/REPO_DIRECTORY_ROLLUP_20260410.md) / `.json`（脚本见 [治理工具总索引](./GOVERNANCE_TOOLS_INDEX.md)） |
| **逻辑/叙事入口** | 理解域边界与总账 | [`docs/SITEMAP.md`](../../../SITEMAP.md)、[`docs/System_Manifest.md`](../../../System_Manifest.md)、[`docs/INDEX.md`](../../../INDEX.md)、建设文档 [`INDEX.md`](../INDEX.md) |
| **蓝图与能力总览** | 正式稿导航、任务 1 闭合 | [`BLUEPRINT_STAGE_COMPLETE_SUMMARY.md`](../../../01_FRAMEWORK/BLUEPRINT_STAGE_COMPLETE_SUMMARY.md)、[`01_BLUEPRINTS/INDEX.md`](../01_BLUEPRINTS/INDEX.md) |
| **架构服务视图（代码侧）** | API/组件与根目录机构缺口 | [`ARCHITECTURE_SERVICE_CATALOG_*.md`](../../../09_AUDIT/STATE/ARCHITECTURE_SERVICE_CATALOG_20260410.md) |

**放置决策**时：先用 **LAYOUT 标准**定「这类内容应落在哪棵树」，再用 **rollup** 看当前文件实际堆在哪棵前缀下，二者不一致即形成**搬迁候选**（须 PR + 链接替换 + 门禁）。

---

## 3. 扫描途中：从报表到归位（推荐固定顺序）

适用于 [全仓库文件治理任务清单](./REPO_WIDE_FILE_GOVERNANCE_TASK_LIST.md) **§7** 前缀批次或与 **§2.3** 并行的小步 PR。

1. **出图**：`export_repo_directory_rollup.py`（可选 `--include-untracked`）→ 选定本批要处理的前缀或子队列。  
2. **打开标准**：对照 **LAYOUT 标准 §2～§4**，写下本批「目标目录类型」（一句话即可，贴在 PR 描述）。  
3. **逐文件/子簇**：判断应归 **哪一格**；若涉及 **图纸柜**，叠加 **01_BLUEPRINTS_REPOSITORY_RULES**。  
4. **搬迁前**：涉及删或合并时走 [删稿裁决 Playbook](./FILE_DELETION_OR_RETENTION_PLAYBOOK.md)；涉及重复内容走 REPO_WIDE **§3**（C1/C2/D）。  
5. **搬迁后**：`sentinel_l1_governance_scan.py`；若动蓝图路径则 `verify_*` + 按需 `generate_01_blueprints_index.py`。  
6. **收口**：重跑 rollup（同日期戳或新日期）便于 JSON diff 证明该前缀「变薄」或达标。

---

## 4. 与任务清单的联动（一览）

| 任务/章节 | 与本文关系 |
|-----------|------------|
| [蓝图终稿任务清单](./BLUEPRINT_PHASE_CLOSURE_TASK_LIST.md) **机构顺序 3～5**、**任务 3～5**、**W0～W4** | 清点与归位、摆放与卫生阶段须**显式对照 LAYOUT + 图纸柜规则**；W2/W4 与根目录误放见 [仓库根治理 Playbook](./REPO_ROOT_GOVERNANCE_PLAYBOOK.md)。 |
| [全仓库文件治理任务清单](./REPO_WIDE_FILE_GOVERNANCE_TASK_LIST.md) **§2.3、§7** | **§7.2** 退出标准中含 **「摆放」** 勾选；§2.3 总表含 **文档地图与放置** 行。 |
| [蓝图卫生总案](./CANON/BLUEPRINT_PHASE_DOCUMENT_HYGIENE_MASTER_PLAN_20260408.md) | 清洁批次与「先定摆放再合并」互补；不与此文冲突时**优先满足 LAYOUT**。 |

---

## 5. 版本记录

| 版本 | 日期 | 说明 |
|------|------|------|
| 1.0.0 | 2026-04-10 | 首版：真源层级、地图含义、扫描→归位步骤、与蓝图/整仓任务联动 |
