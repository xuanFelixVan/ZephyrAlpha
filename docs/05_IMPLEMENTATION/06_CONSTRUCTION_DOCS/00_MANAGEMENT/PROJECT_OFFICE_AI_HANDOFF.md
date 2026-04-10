---
module_id: PROJECT_OFFICE_AI_HANDOFF_001
version: 1.2.8
status: Active
created_date: 2026-04-10
last_updated: '2026-04-10'
owner: 文档负责人（可指定）
responsibility:
  - 向 AI 或新协作者交接「项目办公室」与蓝图治理上下文时的必读说明
standard_type: 交接说明
applicable_scope: 任意 AI 模型 / 人类接手本仓库文档与蓝图相关工作
---

# 项目办公室 — AI / 协作者交接说明

> **你把这份文件发给任意 AI 时，请同时说明**：工作区根目录是 ZephyrAlpha 仓库；若任务与「蓝图、建设文档、文档整理」有关，先读本节再动文件。

---

## 1. 项目办公室是什么、在哪里

- **文件夹路径**（从仓库根算）：`docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/00_MANAGEMENT/`
- **职责**：放**规章、任务清单、终稿门禁、登记表、本交接说明**；**不**放具体模块的蓝图正文。
- **蓝图正文**在：`docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/`（俗称「正式图纸柜」）。
- **建设文档整棵树**的根说明与大门索引：`docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/README.md`、`INDEX.md`。

---

## 1.5 文档治理原则（与专业机构常见做法对齐 · 摘要）

本仓库以**个人 Owner + AI 协作**为主，下列原则与常见「受控文档 / 设计基线」实践**同构**，但不引入多余签字流程：

1. **单一真源（single source of truth）**：总清单、对外链接、[登记表](./CONTROLLED_DOCUMENTS_REGISTER.md) 指向同一 **canonical**；禁止静默新建「第二套平行真源」。  
2. **可追溯（traceability）**：正式稿路径变更、实质设计变更须留下可查找记录（文件头 `version` / `last_updated`、[终稿定义](./BLUEPRINT_FINAL_SIGNOFF.md) 第 4 节、登记表、或 commit 说明**至少一种**）。  
3. **受控集合**：`00_MANAGEMENT/` 内规章、**CANON** 门禁与卫生总案、[任务清单](./BLUEPRINT_PHASE_CLOSURE_TASK_LIST.md) 视为受控文档；改动前对照下文**真源优先级**。  
4. **证据导向**：「已终稿」「已放行」须能指回仓库内证据（勾选清单、扫描报告路径、契约/TDR 链接），禁止仅以对话结论代替。  
5. **不明则停**：与真源冲突、范围不清或需裁决 canonical 时，登记 gap 或询问 Owner；**不擅自**合并、删除或指定新真源。  
6. **总清单链接核对（Owner 口径）**：**100% 全量**逐条验证「应有蓝图」链接与 canonical（见 [任务清单](./BLUEPRINT_PHASE_CLOSURE_TASK_LIST.md) 任务 1）；**抽检仅在有 Owner 书面豁免时**采用，并须留下豁免依据。

更完整的全库流程（含孤儿/重复）见 [办公室 README](./README.md) 文中 **「全库文档治理流程（摘要）」** 小节。

---

## 2. 接手后建议阅读顺序（首读约 10～20 分钟；含整理图纸柜时更长）

**若任务包含「整理 01_BLUEPRINTS」**：必须先读 [图纸柜执行协议](./BLUEPRINT_CABINET_EXECUTION_PROTOCOL.md)（内含**可复制给任意 AI 的一段话**，防忘、防幻觉）。

按顺序打开，避免和现有约定冲突：

| 顺序 | 文件 | 你要搞懂的事 |
|------|------|----------------|
| ① | [本文件夹 README](./README.md) | 办公室内有哪些文档、外链到哪 |
| ①″（工具查询） | [治理工具总索引](./GOVERNANCE_TOOLS_INDEX.md) | 链检查、rollup、verify、架构目录、**内容重复扫描**等**一条表** |
| ①′ | [DOCUMENT_GOVERNANCE_ARCHITECTURE.md](./DOCUMENT_GOVERNANCE_ARCHITECTURE.md) | **机构式分层架构**（L0～L5）、控制流、与 `09_AUDIT` 边界；首读 README 后建议接着读 |
| ② | [01_BLUEPRINTS_REPOSITORY_RULES.md](./01_BLUEPRINTS_REPOSITORY_RULES.md) | 图纸柜根目录**允许/禁止**什么文件；过程稿应放哪 |
| ③ | [BLUEPRINT_CABINET_EXECUTION_PROTOCOL.md](./BLUEPRINT_CABINET_EXECUTION_PROTOCOL.md) | 整理图纸柜时的执行纪律、自检命令；**用户可复制指令**在文首 |
| ④ | [BLUEPRINT_FINAL_SIGNOFF.md](./BLUEPRINT_FINAL_SIGNOFF.md) | **什么叫蓝图终稿**、谁算认可、终稿后怎么改 |
| ④′ | [BLUEPRINT_DELIVERY_STANDARD_INSTITUTIONAL_LITE.md](./BLUEPRINT_DELIVERY_STANDARD_INSTITUTIONAL_LITE.md) | **机构精华版交付目标态**（四支柱 + 三阶段 + **§1.5 全仓库分层 R0～R4** + 合并自检）；与门禁 §0～§3 对照 |
| ⑤ | [BLUEPRINT_PHASE_CLOSURE_TASK_LIST.md](./BLUEPRINT_PHASE_CLOSURE_TASK_LIST.md) | 蓝图任务 1～6 进度 + **扩展轨 W0～W4**（整仓分层）；总清单链接默认 **100% 全量** |
| ⑤′ | [全仓库文件治理任务清单](./REPO_WIDE_FILE_GOVERNANCE_TASK_LIST.md) | **整仓一次尽治**：§2.3 与扫描/合并并行项、§3 合并重复、**§7 深度前缀队列与退出标准**、§8 办公室自查、**P5**；rollup 见下路径速查 |
| ⑥（按需） | [CONTROLLED_DOCUMENTS_REGISTER.md](./CONTROLLED_DOCUMENTS_REGISTER.md) | 易混淆主题的唯一正式稿登记 |
| ⑦（按需） | [办公室 README](./README.md) →「全库文档治理流程」+ [孤儿与重复 Playbook](../../../09_AUDIT/STANDARDS/DOC_ORPHAN_AND_DUPLICATE_GOVERNANCE_PLAYBOOK.md) + [重复文档处理标准](../../../09_AUDIT/STANDARDS/DUPLICATE_DOCUMENT_HANDLING_STANDARD.md) | 处理**同题多稿、孤儿、重复簇**时必读；与任务清单任务 1～2 联动 |

若用户要你**改代码**而非文档，仍建议至少读完 ②；若动 `01_BLUEPRINTS`，再读 ③。若任务涉及**重复/归档/ canonical 裁决**，再读 ⑦。若任务为**整仓文件一次尽治、按目录拆队列、合并重复**，读 **⑤′** 并对照 [办公室 README](./README.md)「办公室文件一览」。

---

## 3. 真源优先级（发生冲突时听谁的）

1. **图纸柜摆放**：以 [01_BLUEPRINTS_REPOSITORY_RULES.md](./01_BLUEPRINTS_REPOSITORY_RULES.md) 为准。  
2. **终稿含义与变更原则**：以 [BLUEPRINT_FINAL_SIGNOFF.md](./BLUEPRINT_FINAL_SIGNOFF.md) 为准；**机构级目标态一页纸**以 [蓝图交付标准（机构精华版）](./BLUEPRINT_DELIVERY_STANDARD_INSTITUTIONAL_LITE.md) 为准。  
3. **全库有哪些蓝图、总清单口径**：以 [蓝图阶段完整总结](../../../01_FRAMEWORK/BLUEPRINT_STAGE_COMPLETE_SUMMARY.md) 为**当前入口之一**（若用户指定了更新的总清单，以用户指定为准）。  
4. **施工门禁与蓝图卫生真源**：均在 [CANON](./CANON/README.md)——[施工门禁](./CANON/CONSTRUCTION_GATE_CRITERIA_20260408.md)、[卫生总案](./CANON/BLUEPRINT_PHASE_DOCUMENT_HYGIENE_MASTER_PLAN_20260408.md)；勿再使用已废弃的 `09_AUDIT/STATE` 或 `PROCEDURES` 旧路径。  
5. **`docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/` 与 `docs/06_CONSTRUCTION_DOCS/`**：建设文档以 **前者为 canonical**；遗留树见 [建设文档 INDEX](../INDEX.md) 中的「遗留路径」说明；**不要**在未核对总清单的情况下删除遗留副本。  
6. **孤儿与重复 / 重叠**：以 [孤儿与重复治理 Playbook](../../../09_AUDIT/STANDARDS/DOC_ORPHAN_AND_DUPLICATE_GOVERNANCE_PLAYBOOK.md) 与 [重复文档处理标准](../../../09_AUDIT/STANDARDS/DUPLICATE_DOCUMENT_HANDLING_STANDARD.md) 为程序真源；台账见 [`docs/09_ARCHIVE/duplicates/CANONICAL_POINTERS.md`](../../../09_ARCHIVE/duplicates/CANONICAL_POINTERS.md)。与蓝图总清单冲突时，**先裁决 canonical** 再改链接。  
7. **全库治理入口索引**：其余审计、标准、合规路径以 [全库治理文档导航](./GOVERNANCE_DOCUMENTS_NAVIGATION.md) 为准（本交接说明**不**复制其正文）。

### 3.1 架构真源（分层模型）

**L0～L5 分层**、控制流及与 `09_AUDIT` 边界以 [文档治理架构](./DOCUMENT_GOVERNANCE_ARCHITECTURE.md) 为准。上列 **1.～7.** 为**冲突时裁决顺序**；若与该架构 §4 表述不一致，**以上列为准**并回写架构文档。

---

## 4. 常见任务 → 怎么做

| 用户要你做的事 | 建议动作 |
|----------------|----------|
| 整理 `01_BLUEPRINTS` 根目录 | 对照 [图纸柜规则](./01_BLUEPRINTS_REPOSITORY_RULES.md)：仅保留 `*BLUEPRINT.md` 与 `INDEX.md`；带日期的报告、分析进 `01_BLUEPRINTS/REPORTS/`（若尚无则创建）。 |
| 更新蓝图文件列表 | 在仓库根执行：`python scripts/generate_01_blueprints_index.py`（更新 `01_BLUEPRINTS/INDEX.md`）。 |
| 核对「蓝图阶段是否终稿」 | 对照 [交付标准（机构精华版）](./BLUEPRINT_DELIVERY_STANDARD_INSTITUTIONAL_LITE.md) + [终稿定义](./BLUEPRINT_FINAL_SIGNOFF.md) + [任务清单](./BLUEPRINT_PHASE_CLOSURE_TASK_LIST.md) 逐项勾选；总清单链接须 **100% 全量**核对（见任务 1，抽检须 Owner 书面豁免）。 |
| 登记「哪份才是正式稿」 | 在 [登记表](./CONTROLLED_DOCUMENTS_REGISTER.md) 增行，并确保总清单链接一致。 |
| 修正建设文档「大门口」描述 | 改 `docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/INDEX.md`，使子目录表与**磁盘真实文件夹**一致。 |
| 处理同题多稿 / 重复 / 重叠 | 按 §1.5 与 [任务清单](./BLUEPRINT_PHASE_CLOSURE_TASK_LIST.md) 任务 1～2；程序与模板见 Playbook、[重复标准](../../../09_AUDIT/STANDARDS/DUPLICATE_DOCUMENT_HANDLING_STANDARD.md)、[`CANONICAL_POINTERS`](../../../09_ARCHIVE/duplicates/CANONICAL_POINTERS.md)。 |
| 全库 Markdown 内链健康检查 | 在仓库根执行：`python scripts/sentinel_l1_governance_scan.py`；治理习惯上要求**无效内链为 0**（报告路径见脚本输出，通常于 `docs/09_AUDIT/STATE/`）。**注意**：L1 扫描工作区 `*.md`，与 **`git ls-files` 仅已跟踪** 可能不一致，见 [任务清单](./REPO_WIDE_FILE_GOVERNANCE_TASK_LIST.md) **§1.1**。 |
| 整仓分层治理（非仅蓝图） | 先读 [交付标准](./BLUEPRINT_DELIVERY_STANDARD_INSTITUTIONAL_LITE.md) **§1.5**，再按 [任务清单](./BLUEPRINT_PHASE_CLOSURE_TASK_LIST.md) **W0→W4** 勾选并留证据；与任务 1～6 **并列、不替代**。 |
| 整仓「深度尽治」+ 合并重复 + 不想只做表面统计 | 打开 [全仓库文件治理任务清单](./REPO_WIDE_FILE_GOVERNANCE_TASK_LIST.md)：跑 `python scripts/export_repo_directory_rollup.py` 得深度 3～6 队列；按 **§7** 前缀退出标准推进，**§2.3** 与扫描/合并并行；**W 轨勾完 ≠ 尽治完毕**。 |
| 要三级/四级「模块全景」+ 索引、对标机构做法 | 先读同一清单 **§2.4**；已落地 **架构服务目录 + C4**：`python scripts/generate_architecture_service_catalog.py` → [`ARCHITECTURE_SERVICE_CATALOG_*`](../../../09_AUDIT/STATE/ARCHITECTURE_SERVICE_CATALOG_20260410.md)；可选再实现 `MODULE_PANORAMA_*`，与 rollup **同频**更新。 |
| 仓库根出现怪文件 / 密钥误入库 / 运行时数据进库 | 按 [仓库根治理 Playbook](./REPO_ROOT_GOVERNANCE_PLAYBOOK.md) 分类处理（A 垃圾 / B 密钥 / C 运行时）；衔接 **W2、W4**。 |

---

## 5. 与用户协作时的默认约定（若用户未另说明）

- **语言**：用户偏好中文说明；代码与文档中的**专有名词、文件名、API 名**可保留英文。  
- **改动范围**：只改任务需要的文件；不要顺带大段重写无关文档。  
- **用户未要求的新增文档**：不要随意新建 README/总结类文件；**本交接说明**与办公室内既有文件已足够定位。  
- **执行**：能在工作区完成的命令与文件操作应**由助手实际执行**，不要只给用户口令清单。  
- **记录**：受控文档或 CANON 正文的**实质修改**，应能通过版本记录、登记表或 commit 之一追溯到「改了什么、何时」；避免仅存在于聊天窗口的「隐性基线」。

---

## 6. 路径速查（复制用）

```
仓库根:     <ZephyrAlpha>/
项目办公室: docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/00_MANAGEMENT/
图纸柜:     docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/
建设文档根: docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/
索引脚本:   scripts/generate_01_blueprints_index.py
目录聚合:   scripts/export_repo_directory_rollup.py  → docs/09_AUDIT/STATE/REPO_DIRECTORY_ROLLUP_*.md|.json
架构目录:   scripts/generate_architecture_service_catalog.py → docs/09_AUDIT/STATE/ARCHITECTURE_SERVICE_CATALOG_*.md|.json
内容重复:   scripts/scan_duplicate_file_content.py --ext md → docs/09_AUDIT/STATE/DUPLICATE_CONTENT_BY_HASH_*.md|.json
工具总表:   docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/00_MANAGEMENT/GOVERNANCE_TOOLS_INDEX.md
```

---

## 7. 版本记录

| 版本 | 日期 | 说明 |
|------|------|------|
| 1.2.8 | 2026-04-10 | 阅读顺序增 ①″ [治理工具总索引](./GOVERNANCE_TOOLS_INDEX.md)；路径速查增内容重复与工具总表 |
| 1.2.7 | 2026-04-10 | 常见任务「L1」互指任务清单 **§1.1**（扫描边界、非全格式语义） |
| 1.2.6 | 2026-04-10 | 路径速查增 `generate_architecture_service_catalog`；常见任务互指 **ARCHITECTURE_SERVICE_CATALOG** |
| 1.2.5 | 2026-04-10 | 常见任务增「模块全景 / §2.4 / MODULE_PANORAMA」与机构对标说明 |
| 1.2.4 | 2026-04-10 | 阅读顺序增 ⑤′ [全仓库文件治理任务清单](./REPO_WIDE_FILE_GOVERNANCE_TASK_LIST.md)；常见任务增「深度尽治」；路径速查增 `export_repo_directory_rollup.py` |
| 1.2.3 | 2026-04-10 | 常见任务增仓库根治理；链至 [REPO_ROOT_GOVERNANCE_PLAYBOOK](./REPO_ROOT_GOVERNANCE_PLAYBOOK.md) |
| 1.2.2 | 2026-04-10 | 交付标准增 §1.5 / 任务清单增 W 轨；阅读顺序 ④′⑤ 与常见任务表同步 |
| 1.2.1 | 2026-04-10 | 阅读顺序增 ①′ [文档治理架构](./DOCUMENT_GOVERNANCE_ARCHITECTURE.md)；真源优先级下增 §3.1 与架构互指 |
| 1.2.0 | 2026-04-10 | §1.5 治理原则（机构对齐）；真源优先级增孤儿/重复与全库导航；常见任务增重复处置与 L1 扫描；明确总清单 100% 全量核对；阅读顺序增 ⑦ |
| 1.0.1 | 2026-04-10 | 增加机构精华版交付标准阅读项与真源优先级、常见任务对照 |
| 1.0.0 | 2026-04-10 | 首版：阅读顺序、真源、常见任务、协作约定 |
