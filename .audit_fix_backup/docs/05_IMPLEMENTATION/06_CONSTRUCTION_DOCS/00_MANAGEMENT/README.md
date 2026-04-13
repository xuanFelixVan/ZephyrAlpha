---
module_id: 00_MANAGEMENT_README_001
version: 1.1.24
status: Active
created_date: 2026-04-10
last_updated: '2026-04-11'
owner: 文档负责人（可指定）
responsibility:
  - 项目办公室（00_MANAGEMENT）总入口与外链索引
standard_type: 导航说明
applicable_scope: docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/00_MANAGEMENT
layer: layer_05
---


# 项目办公室（00_MANAGEMENT）

本文件夹放**规章、清单、终稿门禁、登记表**，不放具体模块的蓝图正文（蓝图在 `../01_BLUEPRINTS/`）。

**给任意 AI / 新协作者交接时**：请先读 项目办公室 AI 交接说明（阅读顺序、真源优先级、常见任务；**§0.1** Git / L1 / UTF-8；**§0.1.4** `.gitignore` 与 `docs/09_AUDIT/STATE/` **两条线**；**§0.2** Solo+全委托 AI 机械清单；**§3.2** 区分 **文档治理 L0～L5** 与 **系统技术栈 Layer 0～11**）。**机构式分层总览**见 文档治理架构（L0～L5、与审计边界）。**运行架构分层（Layer 0～11）真源**为 [`ARCHITECTURE.md`](../../../01_FRAMEWORK/ARCHITECTURE.md)；**勿**用 `docs/10_AI_WORKFLOW` 等路径前缀代替 Layer 编号（见 放置规程 §1.5）。编码与乱码预防全文见 文档编码标准；任务清单 **§1.2 末**、**§7.2 末** 与 **§0.1.4 / §0.2** 同口径。

**全库治理文档**（`09_AUDIT`、`10_GOVERNANCE_COMPLIANCE` 等）**真源仍在原目录**；办公室只提供一张总地图： 全库治理文档导航（说明为何不整体搬进办公室、为何不放进图纸柜）。

**例外（已定）**：**施工门禁**与**蓝图卫生总案**正文已迁入 [CANON/](10_GOVERNANCE_COMPLIANCE/TRAINING_SYSTEM/README.md)，作为蓝图终稿 / 放行的**唯一受控路径**；全库链接已指向该目录。

**文档地图 + 放置规则（机构习惯）**：**「这类文档应放哪」** 的标准真源为 `DOCUMENT_REPOSITORY_LAYOUT_STANDARD.md`；**正式图纸柜**摆放以 图纸柜规则 为准。扫描/rollup 途中要把文件归到合理位置时，按办公室规程 文档地图与放置规则 执行——含 **§1.5**（**架构 Layer 与 `docs/` 路径分立**；与 全仓库文件治理任务清单 **§2.3.1**、**§7.2「摆放」** 对齐）与 **§1.6**（**「位置是否正确」A～F 分桶**，与入链/L1 分立；互指 REPO_WIDE **§2.3.2**）。

**整仓「一次尽治」主清单**：以 全仓库文件治理任务清单 为准——**§2.3**、**§2.3.1**（Layer 与路径防混）、**§2.4**（**架构模块全景 / 三～四级子模块**索引要不要做、机构常见做法、能否随扫描增量更新）、**§3**（合并重复）、**§7**（按深度 3～6 前缀队列打到退出标准）、**§8**（办公室二次自查）。深度 2 目录统计**不够**拆队列时，用 `docs/09_AUDIT/STATE/REPO_DIRECTORY_ROLLUP_*.md` 与 **JSON 全量前缀**（脚本 `scripts/governance/export_repo_directory_rollup.py`）。**物理树**（rollup）与 **逻辑模块树**（待选实现的 `MODULE_PANORAMA_*`，见任务清单 **P4**）建议并列、互链。

**整仓按目录尽治（§7）**：以 全仓库文件治理任务清单 **§7** 与最新 `REPO_DIRECTORY_ROLLUP_*` 拆前缀批次；跨会话靠 **REPO_WIDE 勾选 + commit/PR 批次说明** 记录进度即可。

**STATE / L1 / 审计域 / 建设文档区（显式入口）**：[STATE 子域索引](../../../09_AUDIT/STATE/INDEX.md) ｜ L1 治理快照（20260408） ｜ [09_AUDIT 域总索引](../../../09_AUDIT/INDEX.md) ｜ [建设文档区门面（06/README）](../README.md)

**治理工具一键查**：`GOVERNANCE_TOOLS_INDEX.md`（链检查、rollup、verify、架构目录、**内容重复**、**索引健全性（零入链）**、**蓝图 D 类重叠扫描 + A 档分流 + 二审 JSONL**等命令与产出表；实现在 `scripts/governance/`，根目录同名入口为兼容转发）。

**机构式架构/服务目录（已生成，可检索）**：`docs/09_AUDIT/STATE/ARCHITECTURE_SERVICE_CATALOG_20260410.md`（及同主文件名 `.json`）——含 **C4 类 Context/Containers/Components**、从 **FastAPI routes** 抽取的 **HTTP 端点**、`src/` 组件平面表、**根目录相对机构常见缺口**；复跑 `python scripts/governance/generate_architecture_service_catalog.py`。叙事真源仍以 `docs/01_FRAMEWORK/ARCHITECTURE.md`、`System_Manifest` 等为准。

### 扫描覆盖：还能优化什么？（诚实口径）

- **已写清**：任务清单 REPO_WIDE_FILE_GOVERNANCE_TASK_LIST.md **§1.1** —— **Git 已跟踪路径**可被清单/rollup **全覆盖（路径级）**；**不等于**对每一种格式做语义分析或自动处理。  
- **L1 注意**：`sentinel_l1` 扫的是工作区 **`*.md`**（排除常见缓存目录），与 **`git ls-files` 仅已跟踪** 可能不一致；收口验收前宜保持工作区干净或书面接受差异。  
- **`.gitignore` vs `STATE/`**：真·临时文件与缓存靠 **ignore（线 A）**；扫描报表进历史的节奏靠 **STATE 分提交（线 B）** —— 见 AI 交接 §0.1.4、任务清单 §1.2 末。  
- **仍可选的优化**（未默认可跑）：**域 INDEX 必列规则**（须先写标准再写脚本，见 文档地图与放置规则 **§5.3**）、二进制 **体积/LFS 门禁**、CI 中 **全量治理脚本门禁 + 秘密扫描**、根目录 **Docker/CODEOWNERS**（见 `ARCHITECTURE_SERVICE_CATALOG` 缺口表）、**记录管理类保留策略/法律 hold**（本仓库未单独立标，需 Owner 外规接入时另档）。

### 全库文档治理流程（摘要）

与「蓝图终稿任务」**交叉**：重复 / 同题多稿须在任务清单 **任务 1** 内闭环，方法不在此重复发明。**总清单链接核对**：Owner 默认 **100% 全量**逐条验证（见任务清单任务 1；抽检仅书面豁免）。

1. **蓝图与建设文档收口**：全库蓝图终稿任务清单（分解真源；**机构治理顺序**见该文首节对照表）+ 蓝图交付标准（机构精华版）（合并视角）。
2. **孤儿与重复 / 重叠**：孤儿与重复治理 Playbook + 重复文档处理标准；重复簇台账：CANONICAL_POINTERS.md。蓝图 **D 类**：**置信度 / 高置信可合并** 见 D 类 Playbook **§2.5、§5.1**；**低置信**合稿（新路径 + 旧稿 stub、不立刻删）须在 D 类合稿待审登记 追加行（可点击相对链）。**方案文件互指索引**：全仓库文件治理任务清单 **§3.4.1**。
3. **审计区其余入口**：全库治理文档导航。蓝图 **D 类**在跑完 `scan_blueprint_d_overlap_candidates.py` 后，可再跑 `triage_blueprint_d_overlap_pairs.py`，用 二审提示词模板 交给更强模型辅助裁决（详见 D 类 Playbook **§3.5**；与 **§2.5** 同读）。
4. **全仓库分层治理（整仓）**：交付标准 **§1.5**（R0～R4）+ 任务清单 **扩展轨 W0～W4**；与「蓝图终稿」并列，**不替代**任务 1～6。  
5. **仓库根卫生与误提交**：仓库根治理 Playbook（垃圾文件名、密钥进库、运行时数据、误放根下的正式稿归位）。
6. **整仓文件体量、合并与深度尽治（与蓝图并列）**：全仓库文件治理任务清单（**§1.1** 扫描边界、平面清单、**深度 3～6 rollup**、§2.3 并行项、§3 合并、**§7**、**§8**、**P5**）。**说明**：蓝图扩展轨 **W0～W4 勾完 ≠ 文件已尽治**；**全格式逐文件语义处理**不在当前门禁范围内。
7. **文档地图与放置（扫描途中归位）**：文档地图与放置规则（**§1.5**、**§1.6**）+ LAYOUT 标准（**§1 第 6 条**）+ [`ARCHITECTURE.md`](../../../01_FRAMEWORK/ARCHITECTURE.md)（Layer 0～11）；搬迁/新建目录后按 治理工具总索引 复跑相关 `verify_*` 与 `sentinel_l1`。

```---

## 办公室内文件一览（与整仓治理可并行的动作）

> **磁盘范围**：`00_MANAGEMENT/` 平层下列文件 + [CANON/](10_GOVERNANCE_COMPLIANCE/TRAINING_SYSTEM/README.md) 子目录（施工门禁、卫生总案）。**并行**指与 全仓库文件治理任务清单 **§2.3** 同一治理窗口内可安排，不必等扫描结束。

| 文档 | 职责摘要 | 可并入同一治理窗口的典型动作 |
|------|----------|--------------------------------|
| [README.md](10_GOVERNANCE_COMPLIANCE/TRAINING_SYSTEM/README.md)（本文） | 办公室总入口、流程摘要 | §8：改完规章后核对流程编号与下表；**文档地图与放置**与 LAYOUT 互指无断链 |
| 治理工具总索引 | 治理脚本**总表**（命令、产出、顺序）；**不**决定废脚本删否 | 新增脚本时同步更新本表 |
| 文件删除与保留裁决 | 删稿/保留决策树与 PR 检查项 | 出重复报表或清脚本时随 PR 引用 |
| D 类蓝图重叠 Playbook | **主题可能重叠**（非 C1/C2）的机器建议 + 人工收口；**§2.5** 置信度与 **高置信可合并**；**§3.5** A 档分流 + 二审；**§5 双轨**（高/低置信） | 跑 `scan_blueprint_d_overlap_candidates.py` → 可选 `triage_blueprint_d_overlap_pairs.py`；二审配合 D 类二审提示词模板；与 REPO_WIDE **§3.4.1** 对表 |
| D 类重叠二审提示词模板 | 供 GLM/Claude 等输出**固定 JSON Schema**；含模板自优化 `prompt_template_patch_proposal` | 与 `BLUEPRINT_D_OVERLAP_SECOND_PASS_QUEUE_*.jsonl` 同批使用；不替代 Owner 签核 |
| D 类合稿待审登记 | **低置信** D 类合稿台账（新稿 / stub / archive 的 **Markdown 可点击链**） | 每做一例低置信合稿追加一行；高置信 **不**登记 |
| 文档地图与放置规则 | **地图 + LAYOUT 真源衔接**；**§1.5** Layer 0～11 与 `docs/` 路径分立；**§1.6**「位置是否正确」分桶；扫描→查格→搬迁→验证 | 与 REPO_WIDE **§7**、**§2.3.1**、**§2.3.2**、蓝图任务 **3～5** / **W** 轨同窗 |
| 全局文件治理会话交接 | **新开对话可复制**的尽治指令：从全库扫描到深度清洁 | 大扫除窗口启动时发给 AI；与 REPO_WIDE **§7**、工具总表对齐 |
| 文档治理架构 | L0～L5、与 `09_AUDIT` 边界 | 与「尽治」表述冲突时优先回写架构或本 README |
| AI 交接说明 | 接手顺序、真源、常见任务 | 增补「rollup / §7」后自检阅读顺序表 |
| 全库治理文档导航 | 审计/合规入口地图 | 大挪移目录后补外链 |
| 仓库根治理 Playbook | 根目录误提交、密钥、运行时 | 与 §2.3「根门面」并行 |
| 全仓库文件治理任务清单 | **整仓尽治主真源**（合并 + 深度队列 + §2.4 + **ARCHITECTURE_SERVICE_CATALOG** + **P6 文件夹结构与命名合规性** + **P7 施工门禁验收**） | 滚动勾选 P0～P7、§3.6、§7.3；**P4** 已含架构目录生成物，可选 `MODULE_PANORAMA_*`；**P6** 目录命名合规性扫描；**P7** 达成蓝图终稿交付标准 |
| MCP 插件使用手册 | **文档治理与蓝图终稿任务的插件整合方案**；效率/精准度提升矩阵、防幻觉措施、工作流程图 | 与任务清单 **§2.3 并行工作表**、**P6 文件夹结构与命名合规性**、**P7 施工门禁验收** 互指 |
| 全库蓝图终稿任务清单 | 蓝图 1～6 + **W0～W4** | 与尽治**并列**；总清单与重复口径闭合 |
| 蓝图交付标准（机构精华版） | 目标态、§1.5 分层 | 对照 §7 退出标准是否需增删 |
| 蓝图终稿定义 | 终稿含义与变更 | canonical 变更时可追溯 |
| 图纸柜执行协议 | 整理 `01_BLUEPRINTS` 纪律 | 与 C1 合并、INDEX 刷新同窗 |
| 图纸柜规则 | 摆放真源 | 迁文件时必对照 |
| 受控文档登记表 | 易混主题正式稿 | canonical 合并后增行 |
| MCP 插件管理文档 | MCP 插件功能、使用方法和相互索引 | 插件配置与使用指南 |
| 蓝图终稿施工准入验收证 | 蓝图终稿7级29项验证任务的验收证书 | 施工准入前必须通过验证 |
| [CANON/README.md](10_GOVERNANCE_COMPLIANCE/TRAINING_SYSTEM/README.md) 及内文 | 施工门禁 + 卫生总案 **真源** | 卫生批次 P0～P3 与删并互补 |

```---

## 本文件夹内（优先打开）

| 文档 | 说明 |
|------|------|
| 治理工具总索引 | **链检查 / rollup / verify / 架构目录 / 内容重复**等脚本：命令、产出、复跑顺序 |
| 文件删除与保留裁决 | 删稿/保留：决策树 + PR 检查项（与重复报表、§3 配套） |
| D 类蓝图重叠 Playbook | 蓝图主题可能重叠：机器建议 + **§3.5** 分流/二审 + 人工裁决与合稿（**§5 双轨**） |
| D 类重叠二审提示词模板 | 更强模型二审：任务说明、枚举、**JSON Schema**、模板升级 proposal |
| D 类合稿待审登记 | 低置信 D 类合稿：**一点就跳**的相对链 + 批次 / 状态 |
| 文档地图与放置规则 | **文档地图 + 放置规则** 与任务/扫描的衔接；**§1.5** 与 LAYOUT **§1 第 5 条**同口径；真源链指 LAYOUT + 图纸柜规则 |
| 全局文件治理会话交接 | **新会话工作指令**：全局扫描 → 深度清洁队列与硬约束 |
| 文档治理架构 | 专业机构式 **L0～L5 分层**、控制流、与 `09_AUDIT` 边界 |
| [CANON 目录说明](10_GOVERNANCE_COMPLIANCE/TRAINING_SYSTEM/README.md) | 施工门禁 + 蓝图卫生总案（**真源**） |
| 施工门禁 | 三阶段、蓝图终稿五条、§3 总清单 |
| 蓝图卫生总案 | P0–P3 清洁与退出标准 |
| 项目办公室 AI 交接说明 | 接手文档/蓝图治理时的必读顺序与约定 |
| 图纸柜执行协议（防幻觉 · 可复制指令） | 整理图纸柜时必须遵守；内含发给 AI 的一段话 |
| 01_BLUEPRINTS 图纸柜文件治理规则 | 图纸柜根目录能放什么、过程稿放哪、指示牌分层 |
| 蓝图交付标准（机构精华版） | 目标态：四支柱 + 三阶段 + **§1.5 全仓库分层治理（R0～R4）** + 合并自检 |
| 蓝图终稿定义与认可 | 什么叫终稿、谁认可、终稿后怎么改 |
| 全库蓝图终稿任务清单 | 蓝图任务 1～6 + **扩展轨 W0～W4**（整仓分层）；含机构治理顺序与执行勾选 |
| 全仓库文件治理任务清单 | **整仓**尽治 + **ARCHITECTURE_SERVICE_CATALOG**（C4/服务目录）；平面清单、rollup、§2.3～§2.4、§3、§7、§8、P4/P5 |
| 受控文档登记表 | 易混淆/跨目录正式稿台账（按需填行） |
| MCP 插件管理文档 | MCP 插件功能、使用方法和相互索引 |
| MCP 插件使用手册 | **文档治理与蓝图终稿任务的插件整合方案**；效率/精准度提升矩阵、防幻觉措施、工作流程图 |
| 全库治理文档导航 | 审计/标准/合规入口汇总（链接到真源，不搬迁正文） |
| 仓库根治理 Playbook | 根目录正常清单、垃圾文件/密钥/队列误入库的处置；衔接 §1.5 与 W2/W4 |

```---

## 建设文档根目录（同级 `../`）

与施工、规范、模板相关的文件若在仓库中位于 `06_CONSTRUCTION_DOCS/` 根目录，从这里进入：

| 文档 | 说明 |
|------|------|
| [建设文档总索引](../INDEX.md) | 档案室大门（须与真实子目录一致） |
| [建设文档说明](../README.md) | 整棵建设文档树的说明 |
| 施工规范 | 施工层规范 |
| 版本管理指南 | Git / 版本与发布习惯 |
| 蓝图空白模板 | 新建蓝图时套用 |
| AI 施工速查 | AI 协作速查 |
| 新员工入职指南 | 上手路径 |
| 实施进度 | 进度黑板（阶段切换时记得更新） |

```---

## 全库级（仓库其他路径）

| 文档 | 说明 |
|------|------|
| 蓝图阶段完整总结 | 全库蓝图内容清单与口径（总清单入口之一） |
| 蓝图阶段文档卫生总计划 | 文档收拾批次与要求（**CANON** 真源） |
| TODO/TBD 清理清单 | 占位符清理台账（若仍使用） |

```---

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
- **同名不同路径 / basename 碰撞（C2 报表）**：  
  `python scripts/governance/scan_basename_collisions.py`（默认 `docs/` + `.md`；可加 `--all-repo`）  
  （输出 `docs/09_AUDIT/STATE/BASENAME_COLLISIONS_*`）  
- **蓝图 D 类重叠候选（启发式 + 建议 canonical/合并大纲）**：  
  `python scripts/governance/scan_blueprint_d_overlap_candidates.py`（见 D 类蓝图重叠 Playbook；**低置信合稿**须登记 D 类合稿待审登记）  
  （输出 `docs/09_AUDIT/STATE/BLUEPRINT_D_OVERLAP_CANDIDATES_*`）  
- **蓝图 D 类 A 档分流 + 二审队列（JSONL）**：  
  `python scripts/governance/triage_blueprint_d_overlap_pairs.py --date YYYYMMDD`（可选 `--queue-mode high_medium`；见 Playbook **§3.5** 与 二审提示词模板）  
  （输出 `docs/09_AUDIT/STATE/BLUEPRINT_D_OVERLAP_TRIAGE_*`、`BLUEPRINT_D_OVERLAP_SECOND_PASS_QUEUE_*.jsonl`）  
- **索引健全性（零入链候选，默认扫 `docs/`）**：  
  `python scripts/governance/scan_index_health.py`  
  （输出 `docs/09_AUDIT/STATE/INDEX_HEALTH_ORPHAN_*`；说明见 文档地图与放置规则 **§5.2**）  
- **全部治理命令一张表**：治理工具总索引

### 基线复跑约定（与 REPO_WIDE P0、§3.1 复审口径一致）

- **最低频率**：每个**大版本**或至少**每季度**复跑：`export_repo_directory_rollup.py`（建议带 `--date YYYYMMDD`）、`REPO_GIT_TRACKED_FILES_*.txt`（§1 内 PowerShell/Python 片段）。  
- **大治理批次收口**：同一窗口内建议复跑 `scan_duplicate_file_content.py --ext md`、`scan_index_health.py`、`sentinel_l1_governance_scan.py`；若本轮含 **D 类**，在 `scan_blueprint_d_overlap_candidates.py` 之后可再跑 `triage_blueprint_d_overlap_pairs.py` 生成二审 JSONL。产出更新至 `docs/09_AUDIT/STATE/` 后 **commit**，便于 JSON/报表 diff。  
- **归档区 C1 合并**：须符合 全仓库文件治理任务清单 **§3**；当前 Owner 裁定为 **宽松**（见该文 §3.1 末段）。

```---

## 版本记录

| 版本 | 日期 | 说明 |
|------|------|------|
| 1.1.22 | 2026-04-11 | 文首与「扫描覆盖」增 **§0.1.4** 两条线、**§0.2**；互指 REPO_WIDE **§1.2 末**、**§7.2 末** |
| 1.1.20 | 2026-04-11 | 文首互指 AI 交接 **§0.1**、编码标准、REPO_WIDE §1.2（Git/L1/UTF-8 与尽治任务对齐） |
| 1.1.19 | 2026-04-11 | D 类：互指 Playbook **§2.5、§5.1** 与 REPO_WIDE §3.4.1 方案索引；办公室表与孤儿/重复流程第 2 条对齐 |
| 1.1.18 | 2026-04-16 | 文首/流程第 7 条/办公室表互指放置规程 **§1.6**、REPO_WIDE **§2.3.2**、LAYOUT **§1 第 6 条**（「位置是否正确」分桶与入链分立） |
| 1.1.13 | 2026-04-10 | 互指 `triage_blueprint_d_overlap_pairs.py`、二审提示词模板、Playbook **§3.5**；办公室表增二审模板行；常用脚本与基线复跑约定补 D 档分流 |
| 1.1.12 | 2026-04-10 | 办公室内文件表「文档地图」行与 LAYOUT **§1 第 5 条** / 放置规程 **§1.5** 对齐 |
| 1.1.11 | 2026-04-10 | 文首/流程/办公室表互指 放置规程 §1.5、REPO_WIDE **§2.3.1**、AI **§3.2**、`ARCHITECTURE.md`（Layer 0～11 与 `docs/` 路径分立） |
| 1.1.10 | 2026-04-10 | 增 D 类合稿待审登记 双表入口；流程第 2 条与常用脚本互指低置信登记 |
| 1.1.9 | 2026-04-11 | 办公室表增 D 类 Playbook；常用脚本增 `scan_blueprint_d_overlap_candidates.py` |
| 1.1.8 | 2026-04-11 | 常用脚本增 `scan_basename_collisions.py`（C2 basename 报表） |
| 1.1.7 | 2026-04-11 | 新增「基线复跑约定」；互指 REPO_WIDE P0 / §3.1 **宽松**归档裁定 |
| 1.1.6 | 2026-04-10 | 增 全局文件治理会话交接；工具总表口径补索引健全性；扫描优化项补 §5.3/合规外规 |
| 1.1.5 | 2026-04-10 | 常用脚本增 `scan_index_health.py`（索引健全性 / 零入链） |
| 1.1.4 | 2026-04-10 | 新增 文档地图与放置规则；文首与治理流程第 7 条；办公室两表互指；联动 REPO_WIDE §7、蓝图任务清单 |
| 1.1.3 | 2026-04-10 | 新增 治理工具总索引；常用脚本增内容重复扫描；文首一键入口 |
| 1.1.2 | 2026-04-10 | 增 **扫描覆盖诚实口径**小节（互指任务清单 §1.1）；流程第 6 条写明非「全格式语义处理」 |
| 1.1.1 | 2026-04-10 | 增 **ARCHITECTURE_SERVICE_CATALOG** 说明与常用脚本；根目录 **LICENSE/CONTRIBUTING/SECURITY** 与任务清单 **1.2.2** 对齐 |
| 1.1.0 | 2026-04-10 | 尽治主清单互指 **§2.4** 模块全景与 **P4** 可选脚本；物理 rollup 与逻辑 `MODULE_PANORAMA_*` 并列说明 |
| 1.0.9 | 2026-04-10 | 尽治主清单互指 **§7/§8/P5/rollup**；新增「办公室文件一览」表；流程第 6 条扩写；常用脚本增 `export_repo_directory_rollup.py` |
| 1.0.8 | 2026-04-10 | 新增 全仓库文件治理任务清单 与治理流程第 6 条 |
| 1.0.7 | 2026-04-10 | 任务清单表说明同步（机构顺序执行批次后） |
| 1.0.6 | 2026-04-10 | 治理流程第 1 条互指任务清单「专业机构治理顺序」 |
| 1.0.5 | 2026-04-10 | 新增 仓库根治理 Playbook 入口；治理流程增第 5 条 |
| 1.0.4 | 2026-04-10 | 治理流程增第 4 条（全仓库分层）；表内交付标准/任务清单说明同步 §1.5 与 W 轨 |
| 1.0.3 | 2026-04-10 | 增加 文档治理架构 入口 |
| 1.0.2 | 2026-04-10 | 治理流程摘要：总清单链接默认全量核对（100%） |
| 1.0.1 | 2026-04-10 | 增加全库文档治理流程摘要（含孤儿/重复真源链） |
| 1.0.0 | 2026-04-10 | 首版：办公室总入口 + 外链表 |
