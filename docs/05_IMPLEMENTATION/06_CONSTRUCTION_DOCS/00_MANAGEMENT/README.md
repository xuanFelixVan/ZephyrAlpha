---
module_id: 00_MANAGEMENT_README_001
version: 1.1.4
status: Active
created_date: 2026-04-10
last_updated: '2026-04-10'
owner: 文档负责人（可指定）
responsibility:
  - 项目办公室（00_MANAGEMENT）总入口与外链索引
standard_type: 导航说明
applicable_scope: docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/00_MANAGEMENT
---

# 项目办公室（00_MANAGEMENT）

本文件夹放**规章、清单、终稿门禁、登记表**，不放具体模块的蓝图正文（蓝图在 `../01_BLUEPRINTS/`）。

**给任意 AI / 新协作者交接时**：请先读 [项目办公室 AI 交接说明](./PROJECT_OFFICE_AI_HANDOFF.md)（阅读顺序、真源优先级、常见任务）。**机构式分层总览**见 [文档治理架构](./DOCUMENT_GOVERNANCE_ARCHITECTURE.md)（L0～L5、与审计边界）。

**全库治理文档**（`09_AUDIT`、`10_GOVERNANCE_COMPLIANCE` 等）**真源仍在原目录**；办公室只提供一张总地图： [全库治理文档导航](./GOVERNANCE_DOCUMENTS_NAVIGATION.md)（说明为何不整体搬进办公室、为何不放进图纸柜）。

**例外（已定）**：**施工门禁**与**蓝图卫生总案**正文已迁入 [CANON/](./CANON/README.md)，作为蓝图终稿 / 放行的**唯一受控路径**；全库链接已指向该目录。

**文档地图 + 放置规则（机构习惯）**：**「这类文档应放哪」** 的标准真源为 [`DOCUMENT_REPOSITORY_LAYOUT_STANDARD.md`](../../../09_AUDIT/STANDARDS/DOCUMENT_REPOSITORY_LAYOUT_STANDARD.md)；**正式图纸柜**摆放以 [图纸柜规则](./01_BLUEPRINTS_REPOSITORY_RULES.md) 为准。扫描/rollup 途中要把文件归到合理位置时，按办公室规程 [文档地图与放置规则](./DOCUMENT_MAP_AND_PLACEMENT_GOVERNANCE.md) 执行（与 [全仓库文件治理任务清单](./REPO_WIDE_FILE_GOVERNANCE_TASK_LIST.md) **§7** 退出标准中的 **「摆放」** 项对齐）。

**整仓「一次尽治」主清单**：以 [全仓库文件治理任务清单](./REPO_WIDE_FILE_GOVERNANCE_TASK_LIST.md) 为准——**§2.3**（可与扫描/合并并行的事）、**§2.4**（**架构模块全景 / 三～四级子模块**索引要不要做、机构常见做法、能否随扫描增量更新）、**§3**（合并重复）、**§7**（按深度 3～6 前缀队列打到退出标准）、**§8**（办公室二次自查）。深度 2 目录统计**不够**拆队列时，用 `docs/09_AUDIT/STATE/REPO_DIRECTORY_ROLLUP_*.md` 与 **JSON 全量前缀**（脚本 `scripts/governance/export_repo_directory_rollup.py`）。**物理树**（rollup）与 **逻辑模块树**（待选实现的 `MODULE_PANORAMA_*`，见任务清单 **P4**）建议并列、互链。

**治理工具一键查**：[`GOVERNANCE_TOOLS_INDEX.md`](./GOVERNANCE_TOOLS_INDEX.md)（链检查、rollup、verify、架构目录、**内容重复扫描**等命令与产出表；实现在 [`scripts/governance/`](../../../../scripts/governance/)，根目录同名入口为兼容转发）。

**机构式架构/服务目录（已生成，可检索）**：[`docs/09_AUDIT/STATE/ARCHITECTURE_SERVICE_CATALOG_20260410.md`](../../../09_AUDIT/STATE/ARCHITECTURE_SERVICE_CATALOG_20260410.md)（及同主文件名 `.json`）——含 **C4 类 Context/Containers/Components**、从 **FastAPI routes** 抽取的 **HTTP 端点**、`src/` 组件平面表、**根目录相对机构常见缺口**；复跑 `python scripts/governance/generate_architecture_service_catalog.py`。叙事真源仍以 `docs/01_FRAMEWORK/ARCHITECTURE.md`、`System_Manifest` 等为准。

### 扫描覆盖：还能优化什么？（诚实口径）

- **已写清**：任务清单 [REPO_WIDE_FILE_GOVERNANCE_TASK_LIST.md](./REPO_WIDE_FILE_GOVERNANCE_TASK_LIST.md) **§1.1** —— **Git 已跟踪路径**可被清单/rollup **全覆盖（路径级）**；**不等于**对每一种格式做语义分析或自动处理。  
- **L1 注意**：`sentinel_l1` 扫的是工作区 **`*.md`**（排除常见缓存目录），与 **`git ls-files` 仅已跟踪** 可能不一致；收口验收前宜保持工作区干净或书面接受差异。  
- **仍可选的优化**（未默认可跑）：P1 **按扩展名白名单的 hash 重复报表**、二进制 **体积/LFS 门禁**、CI 中 **依赖漏洞扫描**、根目录 **Docker/CODEOWNERS**（见 `ARCHITECTURE_SERVICE_CATALOG` 缺口表）。

### 全库文档治理流程（摘要）

与「蓝图终稿任务」**交叉**：重复 / 同题多稿须在任务清单 **任务 1** 内闭环，方法不在此重复发明。**总清单链接核对**：Owner 默认 **100% 全量**逐条验证（见任务清单任务 1；抽检仅书面豁免）。

1. **蓝图与建设文档收口**：[全库蓝图终稿任务清单](./BLUEPRINT_PHASE_CLOSURE_TASK_LIST.md)（分解真源；**机构治理顺序**见该文首节对照表）+ [蓝图交付标准（机构精华版）](./BLUEPRINT_DELIVERY_STANDARD_INSTITUTIONAL_LITE.md)（合并视角）。
2. **孤儿与重复 / 重叠**：[孤儿与重复治理 Playbook](../../../09_AUDIT/STANDARDS/DOC_ORPHAN_AND_DUPLICATE_GOVERNANCE_PLAYBOOK.md) + [重复文档处理标准](../../../09_AUDIT/STANDARDS/DUPLICATE_DOCUMENT_HANDLING_STANDARD.md)；重复簇台账：[CANONICAL_POINTERS.md](../../../09_ARCHIVE/duplicates/CANONICAL_POINTERS.md)。
3. **审计区其余入口**：[全库治理文档导航](./GOVERNANCE_DOCUMENTS_NAVIGATION.md)。
4. **全仓库分层治理（整仓）**：交付标准 **§1.5**（R0～R4）+ 任务清单 **扩展轨 W0～W4**；与「蓝图终稿」并列，**不替代**任务 1～6。  
5. **仓库根卫生与误提交**：[仓库根治理 Playbook](./REPO_ROOT_GOVERNANCE_PLAYBOOK.md)（垃圾文件名、密钥进库、运行时数据、误放根下的正式稿归位）。
6. **整仓文件体量、合并与深度尽治（与蓝图并列）**：[全仓库文件治理任务清单](./REPO_WIDE_FILE_GOVERNANCE_TASK_LIST.md)（**§1.1** 扫描边界、平面清单、**深度 3～6 rollup**、§2.3 并行项、§3 合并、**§7**、**§8**、**P5**）。**说明**：蓝图扩展轨 **W0～W4 勾完 ≠ 文件已尽治**；**全格式逐文件语义处理**不在当前门禁范围内。
7. **文档地图与放置（扫描途中归位）**：[文档地图与放置规则](./DOCUMENT_MAP_AND_PLACEMENT_GOVERNANCE.md) + [LAYOUT 标准](../../../09_AUDIT/STANDARDS/DOCUMENT_REPOSITORY_LAYOUT_STANDARD.md)；搬迁/新建目录后按 [治理工具总索引](./GOVERNANCE_TOOLS_INDEX.md) 复跑相关 `verify_*` 与 `sentinel_l1`。

---

## 办公室内文件一览（与整仓治理可并行的动作）

> **磁盘范围**：`00_MANAGEMENT/` 平层下列文件 + [CANON/](./CANON/README.md) 子目录（施工门禁、卫生总案）。**并行**指与 [全仓库文件治理任务清单](./REPO_WIDE_FILE_GOVERNANCE_TASK_LIST.md) **§2.3** 同一治理窗口内可安排，不必等扫描结束。

| 文档 | 职责摘要 | 可并入同一治理窗口的典型动作 |
|------|----------|--------------------------------|
| [README.md](./README.md)（本文） | 办公室总入口、流程摘要 | §8：改完规章后核对流程编号与下表；**文档地图与放置**与 LAYOUT 互指无断链 |
| [治理工具总索引](./GOVERNANCE_TOOLS_INDEX.md) | 治理脚本**总表**（命令、产出、顺序）；**不**决定废脚本删否 | 新增脚本时同步更新本表 |
| [文件删除与保留裁决](./FILE_DELETION_OR_RETENTION_PLAYBOOK.md) | 删稿/保留决策树与 PR 检查项 | 出重复报表或清脚本时随 PR 引用 |
| [文档地图与放置规则](./DOCUMENT_MAP_AND_PLACEMENT_GOVERNANCE.md) | **地图 + LAYOUT 真源衔接**；扫描→查格→搬迁→验证 | 与 REPO_WIDE **§7**、蓝图任务 **3～5** / **W** 轨同窗 |
| [文档治理架构](./DOCUMENT_GOVERNANCE_ARCHITECTURE.md) | L0～L5、与 `09_AUDIT` 边界 | 与「尽治」表述冲突时优先回写架构或本 README |
| [AI 交接说明](./PROJECT_OFFICE_AI_HANDOFF.md) | 接手顺序、真源、常见任务 | 增补「rollup / §7」后自检阅读顺序表 |
| [全库治理文档导航](./GOVERNANCE_DOCUMENTS_NAVIGATION.md) | 审计/合规入口地图 | 大挪移目录后补外链 |
| [仓库根治理 Playbook](./REPO_ROOT_GOVERNANCE_PLAYBOOK.md) | 根目录误提交、密钥、运行时 | 与 §2.3「根门面」并行 |
| [全仓库文件治理任务清单](./REPO_WIDE_FILE_GOVERNANCE_TASK_LIST.md) | **整仓尽治主真源**（合并 + 深度队列 + §2.4 + **ARCHITECTURE_SERVICE_CATALOG**） | 滚动勾选 P0～P5、§3.6、§7.3；**P4** 已含架构目录生成物，可选 `MODULE_PANORAMA_*` |
| [全库蓝图终稿任务清单](./BLUEPRINT_PHASE_CLOSURE_TASK_LIST.md) | 蓝图 1～6 + **W0～W4** | 与尽治**并列**；总清单与重复口径闭合 |
| [蓝图交付标准（机构精华版）](./BLUEPRINT_DELIVERY_STANDARD_INSTITUTIONAL_LITE.md) | 目标态、§1.5 分层 | 对照 §7 退出标准是否需增删 |
| [蓝图终稿定义](./BLUEPRINT_FINAL_SIGNOFF.md) | 终稿含义与变更 | canonical 变更时可追溯 |
| [图纸柜执行协议](./BLUEPRINT_CABINET_EXECUTION_PROTOCOL.md) | 整理 `01_BLUEPRINTS` 纪律 | 与 C1 合并、INDEX 刷新同窗 |
| [图纸柜规则](./01_BLUEPRINTS_REPOSITORY_RULES.md) | 摆放真源 | 迁文件时必对照 |
| [受控文档登记表](./CONTROLLED_DOCUMENTS_REGISTER.md) | 易混主题正式稿 | canonical 合并后增行 |
| [CANON/README.md](./CANON/README.md) 及内文 | 施工门禁 + 卫生总案 **真源** | 卫生批次 P0～P3 与删并互补 |

---

## 本文件夹内（优先打开）

| 文档 | 说明 |
|------|------|
| [治理工具总索引](./GOVERNANCE_TOOLS_INDEX.md) | **链检查 / rollup / verify / 架构目录 / 内容重复**等脚本：命令、产出、复跑顺序 |
| [文件删除与保留裁决](./FILE_DELETION_OR_RETENTION_PLAYBOOK.md) | 删稿/保留：决策树 + PR 检查项（与重复报表、§3 配套） |
| [文档地图与放置规则](./DOCUMENT_MAP_AND_PLACEMENT_GOVERNANCE.md) | **文档地图 + 放置规则** 与任务/扫描的衔接；真源链指 LAYOUT + 图纸柜规则 |
| [文档治理架构](./DOCUMENT_GOVERNANCE_ARCHITECTURE.md) | 专业机构式 **L0～L5 分层**、控制流、与 `09_AUDIT` 边界 |
| [CANON 目录说明](./CANON/README.md) | 施工门禁 + 蓝图卫生总案（**真源**） |
| [施工门禁](./CANON/CONSTRUCTION_GATE_CRITERIA_20260408.md) | 三阶段、蓝图终稿五条、§3 总清单 |
| [蓝图卫生总案](./CANON/BLUEPRINT_PHASE_DOCUMENT_HYGIENE_MASTER_PLAN_20260408.md) | P0–P3 清洁与退出标准 |
| [项目办公室 AI 交接说明](./PROJECT_OFFICE_AI_HANDOFF.md) | 接手文档/蓝图治理时的必读顺序与约定 |
| [图纸柜执行协议（防幻觉 · 可复制指令）](./BLUEPRINT_CABINET_EXECUTION_PROTOCOL.md) | 整理图纸柜时必须遵守；内含发给 AI 的一段话 |
| [01_BLUEPRINTS 图纸柜文件治理规则](./01_BLUEPRINTS_REPOSITORY_RULES.md) | 图纸柜根目录能放什么、过程稿放哪、指示牌分层 |
| [蓝图交付标准（机构精华版）](./BLUEPRINT_DELIVERY_STANDARD_INSTITUTIONAL_LITE.md) | 目标态：四支柱 + 三阶段 + **§1.5 全仓库分层治理（R0～R4）** + 合并自检 |
| [蓝图终稿定义与认可](./BLUEPRINT_FINAL_SIGNOFF.md) | 什么叫终稿、谁认可、终稿后怎么改 |
| [全库蓝图终稿任务清单](./BLUEPRINT_PHASE_CLOSURE_TASK_LIST.md) | 蓝图任务 1～6 + **扩展轨 W0～W4**（整仓分层）；含机构治理顺序与执行勾选 |
| [全仓库文件治理任务清单](./REPO_WIDE_FILE_GOVERNANCE_TASK_LIST.md) | **整仓**尽治 + **ARCHITECTURE_SERVICE_CATALOG**（C4/服务目录）；平面清单、rollup、§2.3～§2.4、§3、§7、§8、P4/P5 |
| [受控文档登记表](./CONTROLLED_DOCUMENTS_REGISTER.md) | 易混淆/跨目录正式稿台账（按需填行） |
| [全库治理文档导航](./GOVERNANCE_DOCUMENTS_NAVIGATION.md) | 审计/标准/合规入口汇总（链接到真源，不搬迁正文） |
| [仓库根治理 Playbook](./REPO_ROOT_GOVERNANCE_PLAYBOOK.md) | 根目录正常清单、垃圾文件/密钥/队列误入库的处置；衔接 §1.5 与 W2/W4 |

---

## 建设文档根目录（同级 `../`）

与施工、规范、模板相关的文件若在仓库中位于 `06_CONSTRUCTION_DOCS/` 根目录，从这里进入：

| 文档 | 说明 |
|------|------|
| [建设文档总索引](../INDEX.md) | 档案室大门（须与真实子目录一致） |
| [建设文档说明](../README.md) | 整棵建设文档树的说明 |
| [施工规范](../CONSTRUCTION_SPECIFICATION.md) | 施工层规范 |
| [版本管理指南](../VERSION_MANAGEMENT_GUIDE.md) | Git / 版本与发布习惯 |
| [蓝图空白模板](../BLUEPRINT_TEMPLATE.md) | 新建蓝图时套用 |
| [AI 施工速查](../AI_CONSTRUCTION_QUICK_REFERENCE.md) | AI 协作速查 |
| [新员工入职指南](../NEW_EMPLOYEE_ONBOARDING_GUIDE.md) | 上手路径 |
| [实施进度](../IMPLEMENTATION_PROGRESS.md) | 进度黑板（阶段切换时记得更新） |

---

## 全库级（仓库其他路径）

| 文档 | 说明 |
|------|------|
| [蓝图阶段完整总结](../../../01_FRAMEWORK/BLUEPRINT_STAGE_COMPLETE_SUMMARY.md) | 全库蓝图内容清单与口径（总清单入口之一） |
| [蓝图阶段文档卫生总计划](./CANON/BLUEPRINT_PHASE_DOCUMENT_HYGIENE_MASTER_PLAN_20260408.md) | 文档收拾批次与要求（**CANON** 真源） |
| [TODO/TBD 清理清单](../../../09_AUDIT/REPORTS/TODO_CLEANUP_INVENTORY_20260406.md) | 占位符清理台账（若仍使用） |

---

## 常用脚本

- 刷新 `01_BLUEPRINTS/INDEX.md`：在仓库根目录执行  
  `python scripts/governance/generate_01_blueprints_index.py`
- **目录深度聚合**（整仓治理排期、`docs/` 下深度 3～6 Top 表 + JSON）：  
  `python scripts/governance/export_repo_directory_rollup.py`  
  （可选 `--date YYYYMMDD`、`--top N`、`--include-untracked`；输出在 `docs/09_AUDIT/STATE/REPO_DIRECTORY_ROLLUP_*`）
- **架构服务目录 + C4 摘要**（`src/`、`pyproject`、API routes、根目录机构缺口表）：  
  `python scripts/governance/generate_architecture_service_catalog.py`  
  （输出 `docs/09_AUDIT/STATE/ARCHITECTURE_SERVICE_CATALOG_*`）
- **内容重复（须指定后缀，默认 `.md`）**：  
  `python scripts/governance/scan_duplicate_file_content.py --ext md`（可选 `--include-untracked`）  
  （输出 `docs/09_AUDIT/STATE/DUPLICATE_CONTENT_BY_HASH_*`）  
- **全部治理命令一张表**：[治理工具总索引](./GOVERNANCE_TOOLS_INDEX.md)

---

## 版本记录

| 版本 | 日期 | 说明 |
|------|------|------|
| 1.1.4 | 2026-04-10 | 新增 [文档地图与放置规则](./DOCUMENT_MAP_AND_PLACEMENT_GOVERNANCE.md)；文首与治理流程第 7 条；办公室两表互指；联动 REPO_WIDE §7、蓝图任务清单 |
| 1.1.3 | 2026-04-10 | 新增 [治理工具总索引](./GOVERNANCE_TOOLS_INDEX.md)；常用脚本增内容重复扫描；文首一键入口 |
| 1.1.2 | 2026-04-10 | 增 **扫描覆盖诚实口径**小节（互指任务清单 §1.1）；流程第 6 条写明非「全格式语义处理」 |
| 1.1.1 | 2026-04-10 | 增 **ARCHITECTURE_SERVICE_CATALOG** 说明与常用脚本；根目录 **LICENSE/CONTRIBUTING/SECURITY** 与任务清单 **1.2.2** 对齐 |
| 1.1.0 | 2026-04-10 | 尽治主清单互指 **§2.4** 模块全景与 **P4** 可选脚本；物理 rollup 与逻辑 `MODULE_PANORAMA_*` 并列说明 |
| 1.0.9 | 2026-04-10 | 尽治主清单互指 **§7/§8/P5/rollup**；新增「办公室文件一览」表；流程第 6 条扩写；常用脚本增 `export_repo_directory_rollup.py` |
| 1.0.8 | 2026-04-10 | 新增 [全仓库文件治理任务清单](./REPO_WIDE_FILE_GOVERNANCE_TASK_LIST.md) 与治理流程第 6 条 |
| 1.0.7 | 2026-04-10 | 任务清单表说明同步（机构顺序执行批次后） |
| 1.0.6 | 2026-04-10 | 治理流程第 1 条互指任务清单「专业机构治理顺序」 |
| 1.0.5 | 2026-04-10 | 新增 [仓库根治理 Playbook](./REPO_ROOT_GOVERNANCE_PLAYBOOK.md) 入口；治理流程增第 5 条 |
| 1.0.4 | 2026-04-10 | 治理流程增第 4 条（全仓库分层）；表内交付标准/任务清单说明同步 §1.5 与 W 轨 |
| 1.0.3 | 2026-04-10 | 增加 [文档治理架构](./DOCUMENT_GOVERNANCE_ARCHITECTURE.md) 入口 |
| 1.0.2 | 2026-04-10 | 治理流程摘要：总清单链接默认全量核对（100%） |
| 1.0.1 | 2026-04-10 | 增加全库文档治理流程摘要（含孤儿/重复真源链） |
| 1.0.0 | 2026-04-10 | 首版：办公室总入口 + 外链表 |
