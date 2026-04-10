---
module_id: DOCUMENT_MAP_PLACEMENT_GOVERNANCE_001
version: 1.3.1
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
> **本文件不做什么**：**不**替代 [`DOCUMENT_REPOSITORY_LAYOUT_STANDARD.md`](../../../09_AUDIT/STANDARDS/DOCUMENT_REPOSITORY_LAYOUT_STANDARD.md) 中的目录职责表全文；表内细节以该标准为 **single source of truth**。**Layer 0～11 与 `docs/` 路径分立**在 LAYOUT **§1 第 5 条**有摘要，**§1.5** 为展开与同口径操作说明；**勿**再单立新文件重复该口径。

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

## 1.5 架构 Layer（0～11）与 `docs/` 落盘：勿混淆

与 LAYOUT 标准 **§1 第 5 条**同口径（该处为摘要，本节为步骤与例外说明）。**这是两个不同维度**（人类与 AI 均易混）；搬迁、新建或写 `front matter` 时按顺序各定一次：

1. **先定架构 Layer（技术栈分层）**：模块在 **Layer 0～11** 中主责在哪一层，以 [`docs/01_FRAMEWORK/ARCHITECTURE.md`](../../../01_FRAMEWORK/ARCHITECTURE.md) 的分层表与栈说明为真源。  
2. **再定 `docs/` 物理落盘**：该 Markdown 应落在哪棵目录树，以 [**LAYOUT 标准**](../../../09_AUDIT/STANDARDS/DOCUMENT_REPOSITORY_LAYOUT_STANDARD.md) 与本文 **第 1 节真源表**为准。  
3. **防混规则**：路径段中的数字前缀（例如 `10_AI_WORKFLOW`、`11_STRATEGIC_DECISION`）**不等于** Layer 10 / Layer 11；模块 Layer 以正文、`front matter` 的 `layer`（若有）与 `ARCHITECTURE.md` **对照一致**为准，**不得**仅从路径推断。

若蓝图 **YAML `layer` 与正文「Layer 定位」冲突**，以 **`ARCHITECTURE.md` + Owner 裁决**收敛为单一表述，并在同一 PR 内改完。

> **与办公室其他「分层」表述的区别**：[`DOCUMENT_GOVERNANCE_ARCHITECTURE.md`](./DOCUMENT_GOVERNANCE_ARCHITECTURE.md) 中的 **L0～L5** 描述的是**文档治理控制面**（机构式办公室分层），**不是**本节所述 **Layer 0～11 技术栈**；二者可并存，禁止混名混用。

---

## 2. 「文档地图」在本仓库指什么

| 地图形态 | 用途 | 典型入口 |
|----------|------|----------|
| **物理树（路径前缀）** | 拆队列、看哪棵子树最大 | [`REPO_DIRECTORY_ROLLUP_*.md`](../../../09_AUDIT/STATE/REPO_DIRECTORY_ROLLUP_20260410.md) / `.json`（脚本见 [治理工具总索引](./GOVERNANCE_TOOLS_INDEX.md)） |
| **技术栈分层（Layer 0～11）** | 模块在运行架构中主责哪一层 | [`ARCHITECTURE.md`](../../../01_FRAMEWORK/ARCHITECTURE.md)（与 **§1.5** 配合使用） |
| **逻辑/叙事入口** | 理解域边界与总账 | [`docs/SITEMAP.md`](../../../SITEMAP.md)、[`docs/System_Manifest.md`](../../../System_Manifest.md)、[`docs/INDEX.md`](../../../INDEX.md)、建设文档 [`INDEX.md`](../INDEX.md) |
| **蓝图与能力总览** | 正式稿导航、任务 1 闭合 | [`BLUEPRINT_STAGE_COMPLETE_SUMMARY.md`](../../../01_FRAMEWORK/BLUEPRINT_STAGE_COMPLETE_SUMMARY.md)、[`01_BLUEPRINTS/INDEX.md`](../01_BLUEPRINTS/INDEX.md) |
| **架构服务视图（代码侧）** | API/组件与根目录机构缺口 | [`ARCHITECTURE_SERVICE_CATALOG_*.md`](../../../09_AUDIT/STATE/ARCHITECTURE_SERVICE_CATALOG_20260410.md) |

**放置决策**时：先用 **LAYOUT 标准**定「这类内容应落在哪棵树」（**§1.5**：与 Layer 编号分开想），再用 **rollup** 看当前文件实际堆在哪棵前缀下，二者不一致即形成**搬迁候选**（须 PR + 链接替换 + 门禁）。

---

## 3. 扫描途中：从报表到归位（推荐固定顺序）

适用于 [全仓库文件治理任务清单](./REPO_WIDE_FILE_GOVERNANCE_TASK_LIST.md) **§7** 前缀批次或与 **§2.3** 并行的小步 PR。

1. **出图**：`export_repo_directory_rollup.py`（可选 `--include-untracked`）→ 选定本批要处理的前缀或子队列。  
2. **打开标准**：对照 **LAYOUT 标准 §2～§4** 与本文 **§1.5**（Layer 与路径分立），写下本批「目标目录类型」（一句话即可，贴在 PR 描述）。  
3. **逐文件/子簇**：判断应归 **哪一格**；若涉及 **图纸柜**，叠加 **01_BLUEPRINTS_REPOSITORY_RULES**。  
4. **搬迁前**：涉及删或合并时走 [删稿裁决 Playbook](./FILE_DELETION_OR_RETENTION_PLAYBOOK.md)；涉及重复内容走 REPO_WIDE **§3**（C1/C2/D）。  
5. **搬迁后**：`sentinel_l1_governance_scan.py`；若动蓝图路径则 `verify_*` + 按需 `generate_01_blueprints_index.py`。  
6. **收口**：重跑 rollup（同日期戳或新日期）便于 JSON diff 证明该前缀「变薄」或达标。  
7. **索引与互链（见下文 §4）**：路径变更后，**凡引用旧路径之处**须替换或 stub；按需更新域内 `INDEX.md` / 登记表 / 机器清单；再跑 **L1** 与相关 **verify_***。

---

## 4. 搬迁后索引与互链：必须做什么、不必做什么

### 4.1 路径变了，索引跟不跟？

**要跟。** 「索引」在这里泛指：**一切仍写着旧路径的地方**，不限于名为 `INDEX.md` 的文件。

| 类别 | 搬迁后通常要做的事 |
|------|---------------------|
| **入链（别文指向该文件）** | 全仓搜索旧路径，批量改为新路径（或保留 stub 路径则改 stub 正文）。 |
| **出链（该文件指向别文）** | 若相对层级变了，修正本文内相对链接；跑 `sentinel_l1_governance_scan.py` 直至 **Invalid links = 0**（团队约定）。 |
| **机器维护清单** | 动 `01_BLUEPRINTS/` 内蓝图文件名或位置 → `generate_01_blueprints_index.py`；总清单/分散清单若含路径字面量 → 相应 `verify_*` 与正文同步。 |
| **登记表 / 台账** | [受控文档登记表](./CONTROLLED_DOCUMENTS_REGISTER.md)、[`CANONICAL_POINTERS`](../../../09_ARCHIVE/duplicates/CANONICAL_POINTERS.md) 等若登记了路径 → 同一 PR 内更新。 |
| **叙事总入口（按需）** | `docs/SITEMAP.md`、`docs/INDEX.md`、建设文档 [`INDEX.md`](../INDEX.md) 等**若**出现该文件固定入口 → 同步；**未**列入者不必为单篇搬迁硬塞。 |

### 4.2 是否要求「每个文件都写进某份总索引」？

**不要求。** 本仓库索引策略是 **分层可达**（与 [全仓库文件治理任务清单](./REPO_WIDE_FILE_GOVERNANCE_TASK_LIST.md) **§2.2** 一致）：**L1～L4** 组合即可，目标是「从门口几步能走到」，而不是「每个 `.md` 在全局 INDEX 里各占一行」。

### 4.3 是否要「互相索引」？

**不强制全库双向互链。** 常见足够形态是：**父级 INDEX / README → 子文档** 单向可达；跨域引用用 **少量 hub 文档**（总清单、SITEMAP、域 INDEX）即可。**双向**仅在「易混淆的一对 canonical / 副本说明」等场景按需维护。

---

## 5. 扫描途中要不要扫「索引是否足够健全」？

### 5.1 现有能力（已落地）

| 能力 | 回答的问题 | 工具/文档 |
|------|------------|-----------|
| **链接能否解析** | 文内 Markdown 相对链是否断 | `sentinel_l1_governance_scan.py`（工作区 `*.md`） |
| **特定清单是否自洽** | INDEX/总清单里列出的路径是否存在 | `verify_01_*`、`verify_scattered_*`、`verify_manifest_paths_strict.py` |
| **目录体量** | 哪棵前缀文件多、便于排期 | `export_repo_directory_rollup.py` |

以上**不自动**回答：「这篇文件**应当**出现在哪几个 INDEX 里」——这需要 **Owner 策略**（哪些目录必须维护域内 INDEX、哪些靠搜索与上级入口）。

### 5.2 已落地：零入链报表（索引健全性 · v1）

- **脚本**：`scripts/governance/scan_index_health.py`（仓库根 `scripts/scan_index_health.py` 转发）。  
- **默认**：候选 = `docs/` 下已跟踪 `.md`（排除 `docs/06_ARCHIVE/`、`docs/09_ARCHIVE/`、`docs/09_AUDIT/STATE/overnight_runs/`）；入链来源 = **全库已跟踪** `.md` 正文中的 Markdown 相对链接。  
- **产出**：`docs/09_AUDIT/STATE/INDEX_HEALTH_ORPHAN_<date>.{md,json}`。  
- **参数**：`--prefix`（可多次缩小候选树）、`--link-source same-as-candidates`、`--ignore-path` / `--ignore-glob`、`--exclude-prefix` 等（见 `python scripts/governance/scan_index_health.py --help`）。  
- **不做**：HTML 链接、代码块内路径、「必须在某 INDEX 出现」的规则校验（后者仍属 **§5.3**）。

### 5.3 仍属可选 / 待规则冻结

- **域 INDEX 覆盖规则**：例如「某前缀下正式稿必须出现在域内 `INDEX.md`」——须先写成标准条款，再单独立项脚本。  
- **与 rollup 同窗**：大治理批次可先 rollup 再跑 `scan_index_health`，优先啃**大前缀**下的零入链。

**结论**：**搬迁批次内**至少应做 **§4.1 + L1 + 相关 verify**；**零入链报表**作**健全性信号**，与 §2.2「分层可达」兼容（门脸路径默认 `--ignore-path` 排除）。

---

## 6. 与任务清单的联动（一览）

| 任务/章节 | 与本文关系 |
|-----------|------------|
| [蓝图终稿任务清单](./BLUEPRINT_PHASE_CLOSURE_TASK_LIST.md) **机构顺序 3～5**、**任务 3～5**、**W0～W4** | 清点与归位、摆放与卫生阶段须**显式对照 LAYOUT + 图纸柜规则**；W2/W4 与根目录误放见 [仓库根治理 Playbook](./REPO_ROOT_GOVERNANCE_PLAYBOOK.md)。 |
| [全仓库文件治理任务清单](./REPO_WIDE_FILE_GOVERNANCE_TASK_LIST.md) **§2.3、§2.3.1、§7** | **§7.2** 含 **「摆放」「导航」「内链」**（摆放与 **§1.5** 一致）；搬迁后索引同步见本文 **§4** 与 §7.2 **内链** 项；§2.3 总表含 **文档地图与放置** 行；**§2.3.1** 与本文 **§1.5** 互文。 |
| [蓝图卫生总案](./CANON/BLUEPRINT_PHASE_DOCUMENT_HYGIENE_MASTER_PLAN_20260408.md) | 清洁批次与「先定摆放再合并」互补；不与此文冲突时**优先满足 LAYOUT**。 |

---

## 7. 版本记录

| 版本 | 日期 | 说明 |
|------|------|------|
| 1.3.1 | 2026-04-10 | 文首与 **§1.5** 互指 LAYOUT **§1 第 5 条**（禁重复造平行真源） |
| 1.3.0 | 2026-04-10 | 新增 **§1.5**（Layer 0～11 与 `docs/` 路径分立 + 与 `DOCUMENT_GOVERNANCE_ARCHITECTURE` L0～L5 区分）；§2 地图表增 **技术栈分层**行；§6 联动 REPO_WIDE **§2.3.1** |
| 1.2.0 | 2026-04-10 | **§5.2** 落地 `scan_index_health.py`（零入链报表）；原「可选增强」拆为 §5.2 / §5.3 |
| 1.1.0 | 2026-04-10 | 增 **§4 搬迁与索引**、**§5 索引健全性**（现有工具边界与可选增强）；§3 增第 7 步互指 |
| 1.0.0 | 2026-04-10 | 首版：真源层级、地图含义、扫描→归位步骤、与蓝图/整仓任务联动 |
