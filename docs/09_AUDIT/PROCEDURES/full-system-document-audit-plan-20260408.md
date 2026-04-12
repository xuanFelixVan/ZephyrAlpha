---

module_id: AUDIT_PLAN_FULL_SYSTEM_20260408

version: 1.1.0

status: Active

created_date: 2026-04-08

last_updated: 2026-04-08

owner: 系统维护者

related_documents:

  - ./FULL_SYSTEM_AUDIT_COMPLETE_CASE_20260408.md

  - ../STATE/MD_FILES_BY_SUBDIRECTORY_20260408.md

standard_type: 审计方案

applicable_scope: 全仓库文档与文档治理流程

compliance_level: 个人/小团队可执行

parent_document: ./INDEX.md

responsibility:

  - 基于当前仓库规模的完整文档审计路线

  - 分批目录、阶段目标与交付物定义

layer: layer_09
---




# ZephyrAlpha 全系统文档审计方案



> **核心职责**：在「个人开发、AI 维护、个人使用」前提下，对全库 Markdown 文档进行可分批、可续跑、可回溯的治理审计。  

> **职责边界**：本方案描述**流程与批次**；具体审计结论写入 `docs/09_AUDIT/REPORTS/` 与各阶段 `STATE` 文件，不替代单篇蓝图正文。



**姊妹文档（必读）**



- **审计全案**（重复内容处理办法、清单用法）  

- **按子目录的完整 `*.md` 文件列表**（机器生成；更新命令：`python scripts/generate_md_inventory_by_dir.py`）



**数据统计快照（生成于 2026-04-08，以本机 `D:\ZephyrAlpha` 为准）**



| 指标 | 数值 | 说明 |

|------|------|------|

| 全仓库 `*.md` 数量 | **2769**（清单口径） | 见 `MD_FILES_BY_SUBDIRECTORY_20260408.md`；已排除 `.venv/`、`.pytest_cache/` |

| `docs/` 下 `*.md` | **约 2708** | 文档体系主体 |

| `docs/INDEX.md` 等根级入口 | 若干 | 与 `System_Manifest.md`、`SITEMAP.md` 形成导航三角 |

| `INDEX.md` 导航文件数量 | **约 293** | 需与分批审计联动更新 |

| `scripts/*.py` | **约 633** | 含大量文档治理、链接、YAML、分层审计脚本，可作为 L1/L3 自动化辅助 |

| 当前 Git 分支（快照时） | `backup/layer25-deep-audit-20260407` | 执行新轮审计前请切到你将用于整改的分支并打新 tag |



---



## 一、仓库文件结构结论（审计设计依据）



### 1.1 `docs/` 一级目录文档量（批次的「权重」）



| 一级目录 | 约文档数 | 审计优先级 | 备注 |

|----------|----------|------------|------|

| `05_IMPLEMENTATION/` | **791** | **P0 活跃真源** | 实施、施工、运维、规格集中，易与代码交叉验证 |

| `06_ARCHIVE/` | **587** | **P1 归档治理** | 体量大；重点查重复迁入、与活跃目录重复真理、根目录散落 `(root)` 约 236 篇 |

| `09_AUDIT/` | **406** | **P0 元审计** | 报告与状态极多；需防与 `06_ARCHIVE`、历史报告重复 |

| `01_FRAMEWORK/` | **333** | **P0 架构真源** | 根目录约 287 篇，与 `LAYER4_ML/` 等子目录需边界清晰 |

| `02_FACTOR_LIBRARY/` | **129** | **P1** | `04_DATA_SOURCE/` 子树最重（约 81），与数据源蓝图交叉多 |

| `08_HUMAN_AI_INTERFACE/` | **96** | **P1** | 子目录多、单目录约 3 篇模式为主，适合按子目录微批 |

| `10_AI_WORKFLOW/` | **69** | **P1** | AI 工作流与 `01_FRAMEWORK`、`09_AUDIT` 可能职责重叠 |

| `09_ARCHIVE/`（注意与 `09_AUDIT` 区分） | **57** | **P2** | 历史 duplicate 等，与 `06_ARCHIVE` 统一策略 |

| `03_TRADING_TACTICS/` | **56** | **P1** | 战术与执行、因子库边界 |

| `11_STRATEGIC_DECISION/` | **51** | **P1** | 与风险预算、宏观配置文档对齐 |

| 其余（`04_EXECUTION`、`07_*`、`00_*`、`10_GOVERNANCE_COMPLIANCE` 等） | 见下表分批 | **按依赖顺序插入** | — |



### 1.2 `05_IMPLEMENTATION/` 二级热点（细分批次用）



| 二级路径 | 约文档数 | 说明 |

|----------|----------|------|

| `04_OPERATIONS/` | **242** | 含 `audit_state/`，与 `09_AUDIT` 报告易重复 |

| `06_CONSTRUCTION_DOCS/` | **233** | 含 `01_BLUEPRINTS/` 等，蓝图密集 |

| `07_OPERATIONS/` | **168** | 运维手册与监控 |

| `05_TECHNICAL_SPECIFICATIONS/` | **97** | 与代码接口强相关，适合抽样做 doc-code |

| 其他 | 若干 | `02_DEVELOPMENT`、`04_INFRASTRUCTURE`、`99_ARCHIVE` 等 |



### 1.3 `06_ARCHIVE/` 二级热点



| 二级路径 | 约文档数 | 说明 |

|----------|----------|------|

| `(root)` 散落 | **236** | 优先做「归类 / 二次归档 / 索引」专项，否则导航成本极高 |

| `20260404_audit_reports_archive/` | **183** | 历史审计报告堆叠，与 `09_AUDIT/REPORTS` 查重 |

| `20260407_old_layer_audit_reports/` | **40** | 旧 Layer 审计，与当前架构叙事一致性 |

| 其他日期子目录 | 若干 | 按「日期 + 主题」批处理 |



### 1.4 仓库内非 `docs/` 的 Markdown



| 区域 | 约数量 | 建议 |

|------|--------|------|

| `notebooks/` | **8** | 纳入 L2 抽样或「实验记录」单批 |

| `data/` | **5** | 评估报告类，可与实施/运维结论交叉 |

| `review_materials_package/` | **11** | 外部评审材料，单独一批，避免与内部真源混淆 |

| 根目录 `README.md` 等 | **少量** | P0：与 `docs/INDEX.md` 链接与架构描述一致性 |



### 1.5 已有自动化资产（建议审计时「复用不重复造轮子」）



`scripts/` 下存在大量与文档治理相关的脚本（链接检查、YAML、`layer*_deep_audit`、`document_governance_auto_check`、`verify_document_code_correspondence` 等）。**完整审计方案应优先调用或对照这些脚本输出**，再在 GLM 等模型中做职责与重复的深度判断。



---



## 二、审计目标与三层标准（与你既有清单对齐）



- **L1 文件系统层**：目录、命名、链接、路径、空/稀/深目录。  

- **L2 文档内容层**：职责单一、重叠/分散/越界/缺失、索引、版本与重复、文档—代码（抽样）。  

- **L3 专业标准层**：YAML、`module_id` 唯一、分类与编号、五大原则、结构质量。



**本轮重点（你已强调）**：



1. **重复**：跨目录同主题、复制粘贴段、多份「最终报告」。  

2. **职责不清**：一篇多核、边界与 `INDEX` 声明不一致、与邻域文档抢活。  

3. **删除前**：必须 Git 备份；误删价值在阶段 F 对照 tag 复核。



---



## 三、Git 与备份（任何删改前强制执行）



在审计周期**开始首日**执行一次即可；后续每大轮整改可再打 tag。



```powershell

Set-Location D:\ZephyrAlpha

git status

git checkout -b audit/backup-YYYYMMDD

git add -A

git commit -m "chore: pre-audit snapshot YYYY-MM-DD"

git tag audit-snapshot-YYYYMMDD

git checkout -

# 回到你日常开发分支（如 main 或当前功能分支）

```



**删除或大量移动文档时**：优先 `git mv` 至 `docs/06_ARCHIVE/...` 并保留索引说明，避免工作区直接删除。



---



## 四、上下文有限时的总策略（不让模型一次读全库）



1. **机器先行**：生成全量 `*.md` 清单 CSV（路径、大小、mtime）；可选 SHA256。  

2. **分层**：L1 尽量脚本；L2 按下面「批次」投喂；L3 只对 YAML/编号异常与 P0 目录精读。  

3. ** handoff 摘要**：每批结束后产出 200～800 字「目录职责摘要」，下一批仅带摘要 + 本批文件列表，避免重复推理。  

4. **长文拆分**：单文件按章节或行号段分批，最后做「合并结论」一轮（只读各段摘要）。  

5. **进度文件**：建议在 `docs/09_AUDIT/STATE/` 或 `docs/05_IMPLEMENTATION/04_OPERATIONS/audit_state/` 维护 `AUDIT_PROGRESS_YYYYMMDD.json`（已审路径、待审、重复对、P0 清单）。



---



## 五、分批审计目录与建议顺序



原则：**先 P0 活跃真源与导航 → 再因子/执行/战术 → 再 AI 工作流与人机界面 → 再归档与历史审计 → 最后杂项与仓库外 md**。



下列「批次」每次只选 **一个子树** 交给模型 Deep Audit；人力紧张时可将「批次 N」再拆成「N-a / N-b」。



### 阶段 A — 入口与架构真源（P0）



| 批次 ID | 路径 | 约文档数 | 重点 |

|---------|------|----------|------|

| **A1** | `docs/INDEX.md`、`docs/System_Manifest.md`、`docs/SITEMAP.md`、`docs/API_README.md` | 少量 | 导航三角一致、与一级目录说明一致 |

| **A2** | `docs/01_FRAMEWORK/` 根目录大量蓝图 | **~287** | 架构叙事、Layer 术语、与 `ARCHITECTURE.md` 是否冲突 |

| **A3** | `docs/01_FRAMEWORK/LAYER4_ML/` | **~40** | ML 规格与 `05_IMPLEMENTATION` 规格边界 |

| **A4** | `docs/01_FRAMEWORK/AI_VIRTUAL_RESEARCH_TEAM/`、`ARCHITECTURE_DECISIONS/` | 少量 | 与 `10_AI_WORKFLOW` 分工 |



### 阶段 B — 实施与施工（P0，最大块，需再拆子批）



| 批次 ID | 路径 | 约文档数 | 重点 |

|---------|------|----------|------|

| **B1** | `docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/` | 视目录 | 蓝图间重复、与 `01_FRAMEWORK` 重叠 |

| **B2** | `docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/` 其余（`02_IMPLEMENTATION_GUIDES`、`05_DESIGN_DOCS` 等） | 合并计 **233** 内 | 指南与设计文档职责 |

| **B3** | `docs/05_IMPLEMENTATION/04_OPERATIONS/`（含 `audit_state`） | **~242** | 与 `09_AUDIT` 报告重复；运维 vs 审计记录边界 |

| **B4** | `docs/05_IMPLEMENTATION/07_OPERATIONS/` | **~168** | 运维手册与监控 |

| **B5** | `docs/05_IMPLEMENTATION/05_TECHNICAL_SPECIFICATIONS/` | **~97** | doc-code 抽样 |

| **B6** | `docs/05_IMPLEMENTATION/02_DEVELOPMENT`、`01_QUICKSTART`、`03_DEPLOYMENT`、`04_INFRASTRUCTURE`、`99_ARCHIVE` | 余量 | 入口与基础设施 |



### 阶段 C — 审计体系自身（P0）



| 批次 ID | 路径 | 约文档数 | 重点 |

|---------|------|----------|------|

| **C1** | `docs/09_AUDIT/REPORTS/` | **~175** | 报告间是否重复「最终」「V24」类；保留规则 |

| **C2** | `docs/09_AUDIT/STATE/` | **~130** | 状态与报告是否同步 |

| **C3** | `docs/09_AUDIT/STANDARDS/`、`TEMPLATES/`、`PROCEDURES/`（含本文） | **~30+16+** | 标准唯一真源 |

| **C4** | `docs/09_AUDIT/` 其余（`TOOLS`、`CONFIG`、`WORKFLOWS` 等） | 余量 | 与 `scripts/` 命名对应 |



### 阶段 D — 因子库与数据（P1）



| 批次 ID | 路径 | 约文档数 | 重点 |

|---------|------|----------|------|

| **D1** | `docs/02_FACTOR_LIBRARY/04_DATA_SOURCE/` | **~81** | 数据源模块与 `01_FRAMEWORK` 数据层蓝图交叉 |

| **D2** | `docs/02_FACTOR_LIBRARY/00_GOVERNANCE`、`01_STANDARDS`、`02_ALPHA_FACTORS_INDEX`、`03_RISK_FACTORS` | 各约 3 | 治理与索引 |

| **D3** | `docs/02_FACTOR_LIBRARY/` 其余编号子目录（`05_BACKTEST`…`28_*`） | 分散 | 单目录 1 篇类文档的元数据一致性 |



### 阶段 E — 执行、战术、战略、研究（P1）



| 批次 ID | 路径 | 约文档数 | 重点 |

|---------|------|----------|------|

| **E1** | `docs/04_EXECUTION/` | **~30** | 与 `03_TRADING_TACTICS`、执行监控边界 |

| **E2** | `docs/03_TRADING_TACTICS/` | **~56** | 战术 vs 策略规格 |

| **E3** | `docs/11_STRATEGIC_DECISION/` | **~51** | 与 `PROFESSIONAL_MULTI_TIMEFRAME_ARCHITECTURE` 等对齐 |

| **E4** | `docs/07_RESEARCH/`、`docs/09_RESEARCH_INNOVATION/` | **~18+30** | 研究记录与主架构 |



### 阶段 F — 人机界面、AI 工作流、合规（P1）



| 批次 ID | 路径 | 约文档数 | 重点 |

|---------|------|----------|------|

| **F1** | `docs/08_HUMAN_AI_INTERFACE/`（可按子目录 01、05… 微批） | **~96** | 大量子目录、易模板化重复 |

| **F2** | `docs/10_AI_WORKFLOW/` | **~69** | 与 `01_FRAMEWORK`、`09_AUDIT` 重叠 |

| **F3** | `docs/10_GOVERNANCE_COMPLIANCE/` | **~21** | 合规与审计术语 |



### 阶段 G — 归档与历史（P1～P2，易重复）



| 批次 ID | 路径 | 约文档数 | 重点 |

|---------|------|----------|------|

| **G1** | `docs/06_ARCHIVE/(root)` 散落 | **~236** | 归类、去重、是否应并入子文件夹 |

| **G2** | `docs/06_ARCHIVE/20260404_audit_reports_archive/` | **~183** | 与 `09_AUDIT/REPORTS` 重复检测 |

| **G3** | `docs/06_ARCHIVE/20260407_*` 及其他日期归档 | 余量 | 版本线索与索引 |

| **G4** | `docs/09_ARCHIVE/` | **~57** | 与 `06_ARCHIVE`、`09_AUDIT` 三角关系 |



### 阶段 H — 其余 docs 与仓库外 md（P2）



| 批次 ID | 路径 | 说明 |

|---------|------|------|

| **H1** | `docs/00_OVERVIEW/`、`docs/00_RESOURCES/`、`docs/08_KNOWLEDGE/`、`docs/08_KNOWLEDGE_BASE/`、`docs/07_AI_REPORTING/` | 体量小，可合并一批 |

| **H2** | `notebooks/**/*.md` | 实验与文档交叉引用 |

| **H3** | `data/**/*.md`、`review_materials_package/**/*.md` | 外置评估材料与内部真源区分 |

| **H4** | 根目录 `README.md` | 与 `docs/INDEX.md` 链接修正（当前根 README 部分链可能陈旧） |



### 阶段 I — Git 误删与备份价值审计（依赖阶段三 tag）



| 步骤 | 操作 |

|------|------|

| I1 | `git diff --name-status audit-snapshot-YYYYMMDD HEAD`，筛 `D` 删除项 |

| I2 | 对每个删除路径评估：恢复 / 归档引用即可 / 确认为重复清理 |

| I3 | 需要时用 `git show <tag>:path` 查看旧内容 |



---



## 六、每批统一输出格式（交给 GLM / 自填）



**单篇五问**（每文件）：一句核心职责；不负责什么；与 INDEX 是否一致；重复嫌疑路径；版本/归档建议。



**批次汇总表**：



| 文件 | 核心职责(1句) | 职责问题 | 重叠文档 | 重复/版本 | YAML/链接 | 严重度 | 建议动作 |



**批次结束**：目录级职责地图；必须合并组；必须归档组；索引更新清单。



---



## 七、建议交付物路径



| 交付物 | 建议路径 |

|--------|----------|

| 全量清单 CSV | `docs/09_AUDIT/STATE/inventory_md_YYYYMMDD.csv` |

| L1 报告 | `docs/09_AUDIT/REPORTS/L1_FILESYSTEM_AUDIT_YYYYMMDD.md` |

| L2 分批汇总 | `docs/09_AUDIT/REPORTS/L2_BATCH_<批次ID>_YYYYMMDD.md` |

| L3 元数据冲突表 | `docs/09_AUDIT/STATE/L3_YAML_CONFLICTS_YYYYMMDD.md` |

| 总整改 backlog | `docs/09_AUDIT/STATE/REMEDIATION_BACKLOG_YYYYMMDD.md` |

| 进度状态机 | `docs/09_AUDIT/STATE/AUDIT_PROGRESS_YYYYMMDD.json` |

| 删除文件复核 | `docs/09_AUDIT/REPORTS/DELETED_FILES_REVIEW_YYYYMMDD.md` |



---



## 八、推荐日程（可按周调整）



| 周次 | 阶段 | 内容 |

|------|------|------|

| 第 1 周 | A + B1～B2 + C1 | 入口、框架、施工蓝图、审计报告主堆 |

| 第 2 周 | B3～B6 + D1 | 实施运维、因子数据源 |

| 第 3 周 | E + F | 执行链、人机、AI 工作流 |

| 第 4 周 | G + H + I | 归档治理、杂项、Git 删除复核 |



---



## 九、完整审计 Master Prompt（粘贴到 AI 会话）



将 `{REPO_ROOT}` 换为 `D:\ZephyrAlpha`，并指定当前批次 ID（如 `B1`）：



```text

你是文档治理审计员。仓库根目录：{REPO_ROOT}。用户为个人开发者，AI 维护文档，个人使用。



要求：中文输出；路径/module_id 保留英文；分阶段；不得无 Git 备份建议删除；不得编造未读内容。



本轮仅审计批次：【填写 BATCH_ID 与路径】。



对清单内每个 *.md 完成五问，并输出批次汇总表与目录级职责地图。严重度 P0/P1/P2。重点：重复、职责不清。



审计标准：L1 文件系统；L2 职责/索引/版本；L3 YAML/编号/五大原则。



结束输出：INDEX 更新清单、REMEDIATION_BACKLOG 条目、下一批依赖。

```



---



## 十、附录：生成 inventory 的 PowerShell 示例



```powershell

Set-Location D:\ZephyrAlpha

Get-ChildItem -Recurse -Filter "*.md" -File |

  Where-Object { $_.FullName -notmatch '\\\.git\\' } |

  Select-Object @{N='RelativePath';E={$_.FullName.Substring((Get-Location).Path.Length+1)}}, Length, LastWriteTime |

  Export-Csv -Path "docs\09_AUDIT\STATE\inventory_md_20260408.csv" -NoTypeInformation -Encoding UTF8

```



---



## 十一、扩展项：Git 历史、编码、联动更新、目录治理、机构对照



以下内容已在 **审计全案**（v1.1.0） 中展开，本方案与之一一对应，避免重复粘贴：



| 主题 | 在全案中位置 |

|------|----------------|

| Git 历史与误删价值（`diff`/`reflog`/未合并分支） | **第七部分** |

| 编码、文件名、联动更新、重归类、稀疏/双轨目录、路径深度 | **第八部分** |

| 与专业机构审计方式的差距及可落地补齐（独立复核、变更编号、CI、复审日历等） | **第九部分** |



**阶段 I（Git 删除复核）** 与第七部分合并执行；**第八部分** 问题可嵌入 L1/L2 检查表；**第九部分** 用于年度/季度改进规划。



---



**文档结束。** 若目录内文件增删导致「约文档数」变化，重新运行第一节统计命令即可更新本方案数字；**批次划分逻辑不必随数字小幅波动而改变**。

