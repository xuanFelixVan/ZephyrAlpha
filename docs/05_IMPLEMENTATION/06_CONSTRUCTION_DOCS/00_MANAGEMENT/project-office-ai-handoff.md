---
module_id: PROJECT_OFFICE_AI_HANDOFF
version: 1.3.10
status: Active
created_date: 2026-04-13
last_updated: '2026-04-13'
owner: 首席文档架构师
layer: layer_05
responsibility: 00_MANAGEMENT
standard_type: 交接说明
applicable_scope: 任意 AI 模型 / 人类接手本仓库文档与蓝图相关工作
---
# 项目办公室 — AI / 协作者交接说明



> **你把这份文件发给任意 AI 时，请同时说明**：工作区根目录是 ZephyrAlpha 仓库；若任务与「蓝图、建设文档、文档整理」有关，先读本节再动文件。**人类主要验收结果、由 AI 全权执行命令与提交**时：AI **默认遵守**下文 **§0.2**（机械顺序）；若当轮用户对话中有**明文**相反指示，以用户指示为准。



```
```---
```



## 0. 术语：「接力说明」指什么



- **接力说明**：给**下一轮对话里的 AI** 或**下一位人类协作者**看的**短交代**——上一轮做到哪、**本批建议纳入提交的路径列表**、下一步先读哪份真源、跑哪几条门禁命令。**Git 暂存、何时复跑 L1、Markdown 如何保存避免乱码** 的统一口径见下文 **§0.1**。跨会话进度以 **PR / commit 描述** 与 [施工阶段任务清单](./construction-phase-task-list.md) 勾选为准；**不**再维护「运行队列 / 当前指针」类独立附件。常见载体：全局文件治理会话交接、本文件。  

- **接力说明不是**：把「未裁决的合并 / 删稿」交给下一任默认执行。**D 类**：**置信度与「高置信可合并」** 见 D 类 Playbook **§2.5、§5.1**；**低置信**合稿仍须 待审登记 与 Owner 书面口径。  

- **与「位置是否正确」**：搬迁或尽治批次判断文件是否放对文件夹时，除 **§3.2**（Layer vs 路径）外，请打开 文档地图与放置规则 **§1.6**（分桶表）。



```
```---
```



## 0.1 Git 暂存、L1 与 Markdown 编码（口径摘要）



> **定位**：把「还能不能一锅端 add」「改链要不要立刻跑 L1」「乱码怎么少发生」收成**可执行摘要**；与 **§0「接力说明」**、任务清单 **§1.1 / §1.2 / §7.2**、合规 文档编码标准 **互指**，不另立第二套真源。



### 0.1.1 Git 暂存



- **默认推荐** `git add <一个或多个路径>`，便于审查与回滚。  

- **不推荐**在未看过 `git status`、未确认本批要入库的路径前，就用 `git add -A` / `git add .` 做「一锅端」式暂存：容易把**无关改动**或**本不该进版本库**的文件（误生成的大报表、本地缓存、密钥草稿等）一并塞进提交，**长期让仓库树与历史膨胀**——这与「编辑器是否产生临时文件」不是一回事；后者主要靠 **`.gitignore`**、不把缓存目录提交、以及「只 add 明确路径」的习惯来避免。  

- 若工作区**已核对**、**确仅含本批任务相关改动**且 Owner 已知情，仍可使用 `git add -A` / `git add .`；**commit / PR 说明须写清本批范围**，避免与后续混入的本地改动混提。



### 0.1.2 L1（内链与首道 `module_id`）



- **推荐**在**大批量**修改 Markdown **相对链接**、搬迁 `.md` 路径、合并或删稿影响外链的批次**收口时**复跑：`python scripts/governance/sentinel_l1_governance_scan.py`。**不是**「每改一条链接就立刻跑一次」的硬工序。  

- 团队默认门禁目标：**无效内链 = 0**；首道 front matter **`module_id` 缺失 / 跨文件重复 → 0**（Owner 书面例外可登记）。L1 扫描的是工作区内 `*.md`，与 `git ls-files` 仅已跟踪可能不一致，见 任务清单 §1.1。散稿补 id 见 治理工具总索引。



### 0.1.3 Markdown 编码与防乱码（薄层）



- **全文真源**：文档编码标准。  

- **实操摘要**：`.md` 以 **UTF-8** 保存；不以错误代码页打开/另存；**大范围替换或脚本改写**前先小范围验证，并**先 commit 或开分支**便于回退；从 PDF/网页粘贴时注意隐式错误编码与不可见字符。  

- **任务清单侧**（致因、与 L1 正交）：REPO_WIDE §1.2。**全局尽治会话**中凡批量写 `.md`，编辑端亦应遵守 UTF-8，见 GLOBAL 会话交接 文首硬约束与阶段 D。



```
```---
```



## 1. 项目办公室是什么、在哪里



- **文件夹路径**（从仓库根算）：`docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/00_MANAGEMENT/`

- **职责**：放**规章、任务清单、终稿门禁、登记表、本交接说明**；**不**放具体模块的蓝图正文。

- **蓝图正文**在：`docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/`（俗称「正式图纸柜」）。

- **建设文档整棵树**的根说明与大门索引：`docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/README.md`、`INDEX.md`。



```
```---
```



## 1.5 文档治理原则（与专业机构常见做法对齐 · 摘要）



本仓库以**个人 Owner + AI 协作**为主，下列原则与常见「受控文档 / 设计基线」实践**同构**，但不引入多余签字流程：



1. **单一真源（single source of truth）**：总清单、对外链接、登记表 指向同一 **canonical**；禁止静默新建「第二套平行真源」。  

2. **可追溯（traceability）**：正式稿路径变更、实质设计变更须留下可查找记录（文件头 `version` / `last_updated`、终稿定义 第 4 节、登记表、或 commit 说明**至少一种**）。  

3. **受控集合**：`00_MANAGEMENT/` 内规章、**CANON** 门禁与卫生总案、任务清单 视为受控文档；改动前对照下文**真源优先级**。  

4. **证据导向**：「已终稿」「已放行」须能指回仓库内证据（勾选清单、扫描报告路径、契约/TDR 链接），禁止仅以对话结论代替。  

5. **不明则停**：与真源冲突、范围不清或需裁决 canonical 时，登记 gap 或询问 Owner；**不擅自**合并、删除或指定新真源。  

6. **总清单链接核对（Owner 口径）**：**100% 全量**逐条验证「应有蓝图」链接与 canonical（见 任务清单 任务 1）；**抽检仅在有 Owner 书面豁免时**采用，并须留下豁免依据。



更完整的全库流程（含孤儿/重复）见 [办公室 README](./README.md) 文中 **「全库文档治理流程（摘要）」** 小节。



```
```---
```



## 2. 接手后建议阅读顺序（首读约 10～20 分钟；含整理图纸柜时更长）



**若任务包含「整理 01_BLUEPRINTS」**：必须先读 图纸柜执行协议（内含**可复制给任意 AI 的一段话**，防忘、防幻觉）。



按顺序打开，避免和现有约定冲突：



| 顺序 | 文件 | 你要搞懂的事 |

|------|------|----------------|

| ① | [本文件夹 README](./README.md) | 办公室内有哪些文档、外链到哪 |

| ①-idx | [INDEX.md](./INDEX.md) | 本目录全部 `.md` 的**磁盘对齐索引**；增删文件后先于此核对，防链接与统计漂移 |

| ①″（工具查询） | 治理工具总索引 | 链检查、rollup、verify、架构目录、**内容重复**、**索引健全性（零入链）**等**一条表** |

| ①″-P（插件使用） | MCP 插件使用手册 | **文档治理与蓝图终稿任务的插件整合方案**；效率/精准度提升矩阵、防幻觉措施、工作流程图；与任务清单 **§2.3 并行工作表**、**P6 文件夹结构与命名合规性** 互指 |

| ①″-P6（目录命名合规） | 治理工具总索引 §1 + PATH_STANDARD.md §1.1 | **P6.1 目录命名合规性扫描**：`scan_directory_naming_compliance.py --date YYYYMMDD --prefix docs/` → `DIRECTORY_NAMING_COMPLIANCE_*.md`；检查中文、空格、特殊字符、缺少编号前缀；与 REPO_WIDE P6 互指 |

| ①″-P7（施工门禁验收） | 施工门禁 + 蓝图交付标准 §4 | **P7 施工门禁验收**：达成蓝图终稿交付标准的最后一步；含 §0.1a 文档放置、§3 A～F 元数据/架构/审计/归档/技术审批/Backlog 验收；与 [施工阶段任务清单](./construction-phase-task-list.md) Phase 4 + 归档 REPO_WIDE P7 互指 |

| ①″-D（蓝图 D 类） | D 类蓝图重叠 Playbook + 二审提示词模板 + D 类合稿待审登记 + 治理工具总索引 §2 步 7～7′ | 主题可能重叠（非 C1/C2）：`scan_blueprint_d_overlap_candidates.py` → 可选 `triage_blueprint_d_overlap_pairs.py`（`TRIAGE_*` + `SECOND_PASS_QUEUE_*.jsonl`）+ **§3.5**；**§2.5 置信度** 与 **§5 双轨**（**高置信可合并** / 低置信待审）；**低置信**合稿须在登记表用 **Markdown 相对链**（一点就跳） |

| ①‴（地图与放置） | 文档地图与放置规则 | **全库 `docs/` 该放哪**：真源链（LAYOUT + 图纸柜规则）+ 与 rollup/§7 批次的**扫描→归位**步骤；**含 §1.5**（系统 **Layer 0～11** 与目录名分立，勿从 `10_*` 路径猜 Layer）；**含 §1.6**（「位置是否正确」**A～F 分桶**，避免把断链修好当放对树）；搬迁前优先于「凭感觉 mkdir」 |

| ①′ | DOCUMENT_GOVERNANCE_ARCHITECTURE.md | **机构式分层架构**（L0～L5）、控制流、与 `09_AUDIT` 边界；首读 README 后建议接着读 |

| ② | 01_BLUEPRINTS_REPOSITORY_RULES.md | 图纸柜根目录**允许/禁止**什么文件；过程稿应放哪 |

| ③ | BLUEPRINT_CABINET_EXECUTION_PROTOCOL.md | 整理图纸柜时的执行纪律、自检命令；**用户可复制指令**在文首 |

| ④ | BLUEPRINT_FINAL_SIGNOFF.md | **什么叫蓝图终稿**、谁算认可、终稿后怎么改 |

| ④′ | BLUEPRINT_DELIVERY_STANDARD_INSTITUTIONAL_LITE.md | **机构精华版交付目标态**（四支柱 + 三阶段 + **§1.5 全仓库分层 R0～R4** + 合并自检）；与门禁 §0～§3 对照 |

| ⑤ | BLUEPRINT_PHASE_CLOSURE_TASK_LIST.md | 蓝图任务 1～6 进度 + **扩展轨 W0～W4**（整仓分层）；总清单链接默认 **100% 全量** |

| ⑤′ | [施工阶段统一任务清单](./construction-phase-task-list.md) | **施工阶段主线**：四步 Pipeline（全系统扫描→修复脚本编排→分批原子执行→真源融合与索引重建）；P0~P7 细节追溯见 [REPO_WIDE（已归档）](./CANON/ARCHIVE/repo-wide-file-governance-task-list.md) |

| ⑥（按需） | CONTROLLED_DOCUMENTS_REGISTER.md | 易混淆主题的唯一正式稿登记 |

| ⑦（按需） | [办公室 README](./README.md) →「全库文档治理流程」+ 孤儿与重复 Playbook + 重复文档处理标准 | 处理**同题多稿、孤儿、重复簇**时必读；与任务清单任务 1～2 联动 |



若用户要你**改代码**而非文档，仍建议至少读完 ②；若动 `01_BLUEPRINTS`，再读 ③。若任务涉及**新建/搬迁 `docs/` 下路径、不确定应放哪棵树**，读 **①‴** 并对照 LAYOUT 标准。若任务同时要**核对蓝图 Layer 字段或正文「Layer 定位」**，读 **①‴ §1.5** 与下文 **§3.2**（并对照 `ARCHITECTURE.md`）。若任务涉及**蓝图主题可能重叠（D 类）或低置信合稿**，读 **①″-D**。若任务涉及**重复/归档/ canonical 裁决**，再读 ⑦。若任务为**整仓文件一次尽治、按目录拆队列、合并重复**，读 **⑤′** 并对照 [办公室 README](./README.md)「办公室文件一览」。**凡将批量改 `.md`**：先过 **§0.1**（Git 暂存、L1 收口时复跑、UTF-8/防乱码）再动手。



```
```---
```



## 2.5 创建蓝图前的「先查找、后创建」原则（防臃肿新规 2026-04-13）



> **问题背景**：Layer 11 蓝图终稿任务中，最初标记 11 个蓝图「缺失」，实际全系统搜索后发现 **100% 已存在**，分散在不同子目录中。若直接创建，会导致重复文件、系统臃肿。
>
> **血的教训**：2026-04-13 实际执行中发现：
> - 5 个 P0 级蓝图：2 个已在正确位置，3 个分散在 `01_FRAMEWORK/`、`10_AI_WORKFLOW/`、`05_IMPLEMENTATION/`
> - 8 个 P1/P2 级蓝图：全部已存在，分散在 `11_STRATEGIC_DECISION/` 的 4 个子目录中
> - 直接创建 → 重复文件 → 后续需归档/合并 → 增加技术债务



### 必须执行的搜索流程（标记「缺失」前）



#### 步骤 1：文件名搜索

```powershell
# 在 docs/ 全目录搜索文件名匹配（替换关键词）
Get-ChildItem -Path 'docs' -Recurse -Filter '*.md' |
  Where-Object { $_.Name -match 'blueprint-name-pattern' } |
  Select-Object FullName, Length | Sort-Object Length -Descending
```



#### 步骤 2：内容搜索（搜索文件内的 module_id、title、关键词）

```powershell
# 搜索文件内容中的关键词
Get-ChildItem -Path 'docs' -Recurse -Filter '*.md' |
  Select-String -Pattern 'module_id.*BLUEPRINT_NAME|核心职责.*关键字' |
  Select-Object Filename, Line | Sort-Object Filename
```



#### 步骤 3：必须检查的目录清单

按优先级顺序检查以下位置：

| 优先级 | 检查位置 | 说明 |
|--------|----------|------|
| 🔴 P0 | `docs/11_STRATEGIC_DECISION/` 及其子目录 | 蓝图可能在子目录中 |
| 🔴 P0 | `docs/01_FRAMEWORK/` | Layer 1 框架层可能包含战略蓝图 |
| 🔴 P0 | `docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/` | 施工图纸柜 |
| 🟡 P1 | `docs/10_AI_WORKFLOW/` | AI 工作流层实现 |
| 🟡 P1 | `docs/06_ARCHIVE/` | 归档但未删除 |
| 🟡 P1 | `docs/99_ARCHIVE/` | 归档区历史版本 |
| 🟢 P2 | `.audit_fix_backup/` | 备份目录原始版本 |
| 🟢 P2 | `.trae/`、`.cursor/` | IDE 配置目录可能包含 |



#### 步骤 4：运行治理脚本

```bash
# 扫描重复文件内容
python scripts/governance/scan_duplicate_file_content.py --ext md

# 扫描同名不同路径
python scripts/governance/scan_basename_collisions.py

# 扫描蓝图重叠候选
python scripts/governance/scan_blueprint_d_overlap_candidates.py

# 目录结构分析
python scripts/analyze_and_fix_folder_structure.py --analyze-only
```



#### 步骤 5：Git 历史搜索

```bash
# 搜索 Git 历史中是否曾存在
Git log --all --full-history --oneline -- "*blueprint-name*"
```



### 标记「缺失」的验收标准



只有在**全部**以下条件满足时，才能在清单中标记为「缺失」：

- [ ] 文件名搜索无结果（docs/ 全目录）
- [ ] 关键词搜索无结果（module_id、title、核心职责）
- [ ] 06_ARCHIVE/ 和 99_ARCHIVE/ 检查无结果
- [ ] 子目录（01_asset_allocation/ 等）检查无结果
- [ ] 扫描脚本未发现重复或相似内容
- [ ] Git 历史搜索无结果
- [ ] **Owner 书面确认**（可选但推荐）



### 违规后果



| 违规行为 | 后果 | 修复成本 |
|----------|------|----------|
| 未经搜索直接创建蓝图 | 重复文件 | 需后续归档/合并 |
| 未检查子目录 | 同主题多版本 | 需 canonical 裁决 |
| 未运行扫描脚本 | 未发现重复 | 增加技术债务 |
| 造成系统臃肿 | 目录混乱 | 需大规模清理 |



**核心原则**：**先查找、后创建** —— 宁可多花 5 分钟搜索，不要花 5 小时修复重复。



```
```---
```



## 3. 真源优先级（发生冲突时听谁的）



1. **全库 `docs/` 目录职责与阶段落盘**：以 `DOCUMENT_REPOSITORY_LAYOUT_STANDARD.md` 为准；与扫描/尽治的衔接步骤见 文档地图与放置规则。  

2. **图纸柜摆放**：以 01_BLUEPRINTS_REPOSITORY_RULES.md 为准（仅约束 `01_BLUEPRINTS/`，不替代上条全库 LAYOUT）。  

3. **终稿含义与变更原则**：以 BLUEPRINT_FINAL_SIGNOFF.md 为准；**机构级目标态一页纸**以 蓝图交付标准（机构精华版） 为准。  

4. **全库有哪些蓝图、总清单口径**：以 蓝图阶段完整总结 为**当前入口之一**（若用户指定了更新的总清单，以用户指定为准）。  

5. **施工门禁与蓝图卫生真源**：均在 [CANON](./CANON/README.md)——施工门禁、卫生总案；勿再使用已废弃的 `09_AUDIT/STATE` 或 `PROCEDURES` 旧路径。  

6. **`docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/` 与 `docs/06_CONSTRUCTION_DOCS/`**：建设文档以 **前者为 canonical**；遗留树见 [建设文档 INDEX](../INDEX.md) 中的「遗留路径」说明；**不要**在未核对总清单的情况下删除遗留副本。  

7. **孤儿与重复 / 重叠**：以 孤儿与重复治理 Playbook 与 重复文档处理标准 为程序真源；台账见 `docs/09_ARCHIVE/duplicates/CANONICAL_POINTERS.md`。与蓝图总清单冲突时，**先裁决 canonical** 再改链接。  

8. **全库治理入口索引**：其余审计、标准、合规路径以 全库治理文档导航 为准（本交接说明**不**复制其正文）。



### 3.1 架构真源（分层模型）



**L0～L5 分层**、控制流及与 `09_AUDIT` 边界以 文档治理架构 为准。上列 **1.～8.** 为**冲突时裁决顺序**；若与该架构 §4 表述不一致，**以上列为准**并回写架构文档。



### 3.2 系统技术栈 Layer 0～11 与 `docs/` 目录名（勿混淆）



与 **§3.1 文档治理 L0～L5** 不同：量化系统 **Layer 0～11** 指 [`ARCHITECTURE.md`](../../../01_FRAMEWORK/ARCHITECTURE.md) 中的**运行架构分层**。LAYOUT 标准 **§1 第 5 条**载有同主题摘要；归位或写蓝图时请按 放置规程 §1.5：**先**对照 `ARCHITECTURE.md` 定模块主责 Layer，**再**按 LAYOUT 标准定 `docs/` 路径；**不得**从 `10_AI_WORKFLOW` 等路径前缀推断 Layer 编号。**勿**新建与上述链路并行的「Layer 放置标准」文件。



```
```---
```



## 4. 常见任务 → 怎么做



| 用户要你做的事 | 建议动作 |

|----------------|----------|

| 不知道某份文档应放在 `docs/` 哪棵子树 | 先查 `DOCUMENT_REPOSITORY_LAYOUT_STANDARD.md` §2～§4；再按 文档地图与放置规则（**§1.5**）与 rollup/§7 批次衔接；若仍无格，先走 LAYOUT **§6** 变更再建目录。 |

| 要标「模块在第几层」或核对 Layer 是否写对 | 以 [`ARCHITECTURE.md`](../../../01_FRAMEWORK/ARCHITECTURE.md) 分层表为准；**路径名 ≠ Layer** — 见 放置规程 §1.5 与上文 **§3.2**。 |

| 整理 `01_BLUEPRINTS` 根目录 | 对照 图纸柜规则：仅保留 `*BLUEPRINT.md` 与 `INDEX.md`；带日期的报告、分析进 `01_BLUEPRINTS/REPORTS/`（若尚无则创建）。 |

| 更新蓝图文件列表 | 在仓库根执行：`python scripts/governance/generate_01_blueprints_index.py`（更新 `01_BLUEPRINTS/INDEX.md`）。 |

| 核对「蓝图阶段是否终稿」 | 对照 交付标准（机构精华版） + 终稿定义 + 任务清单 逐项勾选；总清单链接须 **100% 全量**核对（见任务 1，抽检须 Owner 书面豁免）。 |

| 登记「哪份才是正式稿」 | 在 登记表 增行，并确保总清单链接一致。 |

| 修正建设文档「大门口」描述 | 改 `docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/INDEX.md`，使子目录表与**磁盘真实文件夹**一致。 |

| 处理同题多稿 / 重复 / 重叠 | 按 §1.5 与 任务清单 任务 1～2；程序与模板见 Playbook、重复标准、`CANONICAL_POINTERS`。蓝图 **D 类**另见 D 类 Playbook、可选 `triage_blueprint_d_overlap_pairs.py` + 二审模板；**低置信**合稿登记 待审登记。 |

| 全库 Markdown 内链 + 首道 `module_id` | 见上文 **§0.1.2**；命令与补 id 流程：治理工具总索引；边界见 任务清单 **§1.1**。 |

| 整仓分层治理（非仅蓝图） | 先读 交付标准 **§1.5**，再按 任务清单 **W0→W4** 勾选并留证据；与任务 1～6 **并列、不替代**。 |

| 整仓「深度尽治」+ 合并重复 + 不想只做表面统计 | 打开 [施工阶段任务清单](./construction-phase-task-list.md)：按四步 Pipeline（Phase 1 扫描 → Phase 3 分批执行）推进；前缀队列退出标准见 [REPO_WIDE（已归档）](./CANON/ARCHIVE/repo-wide-file-governance-task-list.md) **§7**。 |

| 要三级/四级「模块全景」+ 索引、对标机构做法 | 先读同一清单 **§2.4**；已落地 **架构服务目录 + C4**：`python scripts/governance/generate_architecture_service_catalog.py` → `ARCHITECTURE_SERVICE_CATALOG_*`；可选再实现 `MODULE_PANORAMA_*`，与 rollup **同频**更新。 |

| 仓库根出现怪文件 / 密钥误入库 / 运行时数据进库 | 按 仓库根治理 Playbook 分类处理（A 垃圾 / B 密钥 / C 运行时）；衔接 **W2、W4**。 |



```
```---
```



## 5. 与用户协作时的默认约定（若用户未另说明）



- **语言**：用户偏好中文说明；代码与文档中的**专有名词、文件名、API 名**可保留英文。  

- **改动范围**：只改任务需要的文件；不要顺带大段重写无关文档。  

- **用户未要求的新增文档**：不要随意新建 README/总结类文件；**本交接说明**与办公室内既有文件已足够定位。  

- **执行**：能在工作区完成的命令与文件操作应**由助手实际执行**，不要只给用户口令清单。  

- **记录**：受控文档或 CANON 正文的**实质修改**，应能通过版本记录、登记表或 commit 之一追溯到「改了什么、何时」；避免仅存在于聊天窗口的「隐性基线」。



```
```---
```



## 6. 路径速查（复制用）



```

仓库根:     <ZephyrAlpha>/

项目办公室: docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/00_MANAGEMENT/

图纸柜:     docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/

建设文档根: docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/

索引脚本:   scripts/governance/generate_01_blueprints_index.py（根目录同名入口可转发）

目录聚合:   scripts/governance/export_repo_directory_rollup.py  → docs/09_AUDIT/STATE/REPO_DIRECTORY_ROLLUP_*.md|.json

架构目录:   scripts/governance/generate_architecture_service_catalog.py → docs/09_AUDIT/STATE/ARCHITECTURE_SERVICE_CATALOG_*.md|.json

内容重复:   scripts/governance/scan_duplicate_file_content.py --ext md → docs/09_AUDIT/STATE/DUPLICATE_CONTENT_BY_HASH_*.md|.json

索引健全性: scripts/governance/scan_index_health.py → docs/09_AUDIT/STATE/INDEX_HEALTH_ORPHAN_*.md|.json

L1 / module_id: scripts/governance/sentinel_l1_governance_scan.py；补首道 module_id: scripts/governance/backfill_missing_module_id.py（--apply 后复跑 L1）

蓝图 D 类:   scripts/governance/scan_blueprint_d_overlap_candidates.py → docs/09_AUDIT/STATE/BLUEPRINT_D_OVERLAP_CANDIDATES_*；可选 triage_blueprint_d_overlap_pairs.py → TRIAGE_* + SECOND_PASS_QUEUE_*.jsonl；规程 D_CLASS_BLUEPRINT_OVERLAP_PLAYBOOK.md（§2.5 置信度 / §5 高·低置信）；二审 D_CLASS_OVERLAP_SECOND_PASS_PROMPT_TEMPLATE.md；低置信台账 D_CLASS_CONSOLIDATION_PENDING_REVIEW_REGISTER.md；任务清单 REPO_WIDE §3.4 / §3.4.1

地图与放置: docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/00_MANAGEMENT/DOCUMENT_MAP_AND_PLACEMENT_GOVERNANCE.md

工具总表:   docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/00_MANAGEMENT/GOVERNANCE_TOOLS_INDEX.md

```



```
```---
```



## 7. 版本记录



| 版本 | 日期 | 说明 |

|------|------|------|

| 1.3.10 | 2026-04-13 | 阅读顺序增 **①-idx**（[INDEX.md](./INDEX.md)）；修正办公室 README / CANON 等错误占位链接为 `./README.md`、`./CANON/README.md` |
| 1.3.9 | 2026-04-11 | **§0.1.1**：显式写清「不推荐未核对就一锅端 `git add -A/.`」及与仓库膨胀、`.gitignore` 的关系；保留「已核对后允许全量 + commit 写清范围」 |

| 1.3.8 | 2026-04-11 | 新增 **§0.1**（Git 暂存、L1 时机、UTF-8/防乱码薄层）；§0 接力说明改为互指 §0.1；去 AGENTS/.cursor 附件表述；常见任务 L1 行改为互指 §0.1.2 |

| 1.3.7 | 2026-04-11 | **§0**：Git 暂存改为「推荐分路径 + 允许全量（须写明范围）」；去「一锅端」硬禁令；接力不再依赖「当前指针」附件；D 类互指 **§2.5 / §5.1**；①″-D 与路径速查增工具总索引、REPO_WIDE §3.4.1；L1 表述改为默认门禁目标 + 推荐复跑 |

| 1.3.6 | 2026-04-16 | 新增 **§0 术语**（「接力说明」）；①‴ 行补 **放置规程 §1.6**（位置正确性分桶）；与 GLOBAL 会话交接、REPO_WIDE **§2.3.2** 互指 |

| 1.3.5 | 2026-04-10 | ①″-D / 常见任务 / 路径速查互指 `triage_blueprint_d_overlap_pairs.py`、二审模板、TRIAGE / SECOND_PASS_QUEUE |

| 1.3.4 | 2026-04-10 | 常见任务「L1」扩展为内链 + 首道 `module_id` + `backfill_missing_module_id.py`；路径速查增两行 |

| 1.3.3 | 2026-04-10 | **§3.2** 互指 LAYOUT **§1 第 5 条**；禁平行 Layer 放置真源 |

| 1.3.2 | 2026-04-10 | 新增 **§3.2**（系统 Layer 0～11 vs `docs/` 路径 vs 文档治理 L0～L5）；①‴ / 常见任务 / 阅读顺序末段互指 放置规程 §1.5 |

| 1.3.1 | 2026-04-10 | 阅读顺序增 ①″-D（D 类 Playbook + 合稿待审登记）；常见任务与路径速查互指 D 类 |

| 1.3.0 | 2026-04-10 | 路径速查增 `scan_index_health.py` / `INDEX_HEALTH_ORPHAN_*` |

| 1.2.9 | 2026-04-10 | 阅读顺序增 ①‴ 文档地图与放置规则；真源优先级首位为 LAYOUT + 放置规程；常见任务增「不知放哪」；路径速查统一 `scripts/governance/` 与地图文件 |

| 1.2.8 | 2026-04-10 | 阅读顺序增 ①″ 治理工具总索引；路径速查增内容重复与工具总表 |

| 1.2.7 | 2026-04-10 | 常见任务「L1」互指任务清单 **§1.1**（扫描边界、非全格式语义） |

| 1.2.6 | 2026-04-10 | 路径速查增 `generate_architecture_service_catalog`；常见任务互指 **ARCHITECTURE_SERVICE_CATALOG** |

| 1.2.5 | 2026-04-10 | 常见任务增「模块全景 / §2.4 / MODULE_PANORAMA」与机构对标说明 |

| 1.2.4 | 2026-04-10 | 阅读顺序增 ⑤′ 全仓库文件治理任务清单；常见任务增「深度尽治」；路径速查增 `export_repo_directory_rollup.py` |

| 1.2.3 | 2026-04-10 | 常见任务增仓库根治理；链至 REPO_ROOT_GOVERNANCE_PLAYBOOK |

| 1.2.2 | 2026-04-10 | 交付标准增 §1.5 / 任务清单增 W 轨；阅读顺序 ④′⑤ 与常见任务表同步 |

| 1.2.1 | 2026-04-10 | 阅读顺序增 ①′ 文档治理架构；真源优先级下增 §3.1 与架构互指 |

| 1.2.0 | 2026-04-10 | §1.5 治理原则（机构对齐）；真源优先级增孤儿/重复与全库导航；常见任务增重复处置与 L1 扫描；明确总清单 100% 全量核对；阅读顺序增 ⑦ |

| 1.0.1 | 2026-04-10 | 增加机构精华版交付标准阅读项与真源优先级、常见任务对照 |

| 1.0.0 | 2026-04-10 | 首版：阅读顺序、真源、常见任务、协作约定 |

