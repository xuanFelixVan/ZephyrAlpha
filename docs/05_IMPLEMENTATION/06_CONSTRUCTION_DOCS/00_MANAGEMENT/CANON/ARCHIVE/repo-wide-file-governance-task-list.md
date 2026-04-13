---
module_id: REPO_WIDE_FILE_GOVERNANCE_TASK_LIST
version: 1.0.0
status: Archived
created_date: 2026-04-13
last_updated: 2026-04-13
owner: 首席文档架构师
layer: layer_05
responsibility: 00_MANAGEMENT
standard_type: 任务清单
applicable_scope: 本 Git 仓库；以 `git ls-files` 为权威清单来源
---
# 全仓库文件治理 — 任务清单（总图）







> **用途**：回答「是否要先扫全树再建任务清单」——**要先有基线清单与统计，再分波次治理**；本文件给出**口径、基线数字、可勾选波次**，避免无控制面的大扫除。  



> **与蓝图清单的关系**：与 全库蓝图终稿任务清单 **并列**；蓝图清单偏**终稿与施工门禁**，本清单偏**整仓文件体量、重复与导航**。扩展轨 **W0～W4 勾选完毕 ≠ 本清单「目录尽治」完毕**（二者互补，见蓝图清单扩展轨节互指）。  



> **一次性尽治目标**：以**单批次最大穷尽**为排期目标——按 **§7** 对 `docs/` 等前缀拆队列、逐前缀打到退出标准；客观上规范与仓库仍会演进，**长期靠门禁脚本 + 定期重跑 §1 清单/rollup** 维持，避免「无标准的第二轮大扫除」。  



> **权威 Playbook**：孤儿与重复文档治理、仓库根治理、文件删除与保留裁决。  



> **架构模块全景（多级子模块）**：是否需要、与机构习惯对照、能否随扫描更新——见 **§2.4**。  



> **架构/服务目录 + C4 摘要（生成物）**：`ARCHITECTURE_SERVICE_CATALOG_*`（脚本 `scripts/governance/generate_architecture_service_catalog.py`）。  



> **扫描是否覆盖「每一种文件格式、每一文件的语义分析与自动处理」？** **否**——见 **§1.1**（分工具、分口径；Git 已跟踪 vs 工作区 Markdown 亦有差异）。**Markdown 编码与防乱码**见 **§1.2**（与 L1 正交；真源 文档编码标准；办公室摘要 AI 交接 §0.1.3）；**§1.2** 末 **`.gitignore` 与 `STATE/` 两条线** 与 AI 交接 §0.1.4、**§0.2** 对齐。  



> **内容重复（按后缀白名单）**：`scripts/governance/scan_duplicate_file_content.py`（**必须** `--ext`，默认 `md`）→ `DUPLICATE_CONTENT_BY_HASH_*`；**同名不同路径（C2）**：`scripts/governance/scan_basename_collisions.py` → `BASENAME_COLLISIONS_*`（默认 `docs/`）；**主题可能重叠（D · 启发式）**：`scripts/governance/scan_blueprint_d_overlap_candidates.py` → `BLUEPRINT_D_OVERLAP_CANDIDATES_*`；可选 `triage_blueprint_d_overlap_pairs.py` → `BLUEPRINT_D_OVERLAP_TRIAGE_*` + `BLUEPRINT_D_OVERLAP_SECOND_PASS_QUEUE_*.jsonl`（Playbook **§3.5** + 二审提示词模板）；D 类蓝图重叠 Playbook（**§2.5** 置信度与 **高置信可合并**、**§5 双轨**；**低置信**合稿须登记 D 类合稿待审登记）；**方案文件互指索引**见本文 **§3.4.1**；治理工具总表见 治理工具总索引。  



> **文档地图 + 放置规则（机构习惯）**：目录职责与阶段落盘的 **真源** 为 `DOCUMENT_REPOSITORY_LAYOUT_STANDARD.md`（**§1 第 5 条**为 Layer/路径分立摘要）；与扫描/§7 批次的 **衔接步骤** 见办公室规程 文档地图与放置规则。**架构 Layer（0～11）与 `docs/` 物理路径是两件不同的事**（勿从 `10_*` 等目录名猜 Layer）：见 放置规程 **§1.5** 与本文 **§2.3.1**（同口径）；技术栈分层真源为 [`ARCHITECTURE.md`](../../../01_FRAMEWORK/ARCHITECTURE.md)。**勿**另建平行「Layer 放置标准」——缺口改 LAYOUT §6 或上述文件互指。







```
```---
```







## 0. 是否要先做「全系统树状」扫描？







**需要。** 推荐顺序为：







1. **基线快照**：导出当前 **Git 已跟踪**路径全表（与协作真源一致）+ 按目录/扩展名聚合统计。  



2. **口径冻结**：定义何为「多余」、何为「重复」、何为「已索引」。  



3. **分波次执行**：先门禁与明显垃圾，再内容哈希重复，最后语义/功能重复（需 Owner 裁决）。







> **说明**：若「整个系统」指 **本机磁盘或操作系统级**，已超出单仓库职责，需在备份与合规策略下**另立项目**；本清单**默认仅覆盖本仓库**。







```
```---
```







## 1. 基线快照（2026-04-10，可复跑更新）







> **基线数字**：与 `git ls-files` 对齐；**人类可读 UTF-8 平面清单**见 [`REPO_GIT_TRACKED_FILES_20260411.txt`](../../../09_AUDIT/STATE/REPO_GIT_TRACKED_FILES_20260411.txt)（导出命令见下，**须** `core.quotePath=false`）。在 PowerShell **默认**配置下，`git ls-files` 对非 ASCII 可能打印 **引号 + 八进制转义**——属 **CLI 显示**，**不是**索引里另存了一套「坏路径」；与 rollup 误分桶、平面清单前几行「像异常」常同源。**澄清与复跑对照**见 `GIT_TRACKED_PATH_ANOMALIES_20260411.md`。历史快照仍可查 [`REPO_GIT_TRACKED_FILES_20260410.txt`](../../../09_AUDIT/STATE/REPO_GIT_TRACKED_FILES_20260410.txt)（该次导出未关 quotePath，**勿**与机器统计直接混用）。







| 指标 | 数值 | 备注 |



|------|------|------|



| **已跟踪文件总数** | **4459**（2026-04-11 `git -c core.quotePath=false ls-files`） | 与 `REPO_DIRECTORY_ROLLUP_20260411` 头部路径条数一致；以后以最新 rollup / 平面清单为准 |



| **Markdown（`.md`）** | 3227 | 体量最大，索引策略必须分层，避免「逐文件手打链接」 |



| **Python（`.py`）** | 756 | 含 `scripts/` 为主 |



| **JSON** | 325 | 含审计状态、配置片段等 |



| **`.diff` 跟踪文件** | 50 | 均已位于 [`../../../06_ARCHIVE/20260408_double_yaml_dryrun_sample/README.md`](../../../06_ARCHIVE/20260408_double_yaml_dryrun_sample/README.md)（历史 dry-run） |



| **`.bak2` / `.bak3` 等备份扩展名（已跟踪）** | **1** + **1** | `.bak2` 在 `encoding_backups`；`.bak3` 在 `06_ARCHIVE/20260410_system_manifest_backup/` |



| **一级目录体量（已跟踪）** | `docs/` **3584**，`scripts/` **690**，`src/` **66** | 治理重心在 `docs/` 与 `scripts/`；`review_materials_package/` 共 **13** 条（含中文文件名 **8** + 英文/配置等 **5**）；rollup 已用 `quotePath=false`，**无**误计的 `"review_materials` 假前缀桶 |







**深度 2 目录聚合（节选，`docs/` 下深度固定为 3 段式前缀 Top 6 — 与 rollup 人类读摘要同口径）**







| 前缀 | 约文件数 |



|------|-----------|



| `docs/09_AUDIT/REPORTS` | 498 |



| `docs/05_IMPLEMENTATION/04_OPERATIONS` | 406 |



| `docs/09_AUDIT/STATE` | 377 |



| `docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS` | 272 |



| `docs/06_ARCHIVE/20260404_audit_reports_archive` | 218 |



| `docs/05_IMPLEMENTATION/05_TECHNICAL_SPECIFICATIONS` | 97 |







> **不足以支撑「一次尽治到最深」**：深度 2 会把 `docs/09_AUDIT` 等上千文件**糊成一桶**；**必须**配合下方 **深度 3～6 聚合**按子前缀拆队列（见 `REPO_DIRECTORY_ROLLUP_*`）。







**深度 3～6 目录聚合（机器生成，支撑拆队列）**







| 产出 | 路径 |



|------|------|



| 人类可读摘要（`docs/` 下各深度 Top 表 + 说明） | `REPO_DIRECTORY_ROLLUP_20260411.md`（**2026-04-11** · `quotePath=false`）；历史 `20260410` |



| 全量前缀计数（JSON，可按任意前缀筛选） | [`REPO_DIRECTORY_ROLLUP_20260411.json`](../../../09_AUDIT/STATE/REPO_DIRECTORY_ROLLUP_20260411.json) · 历史 [`20260410.json`](../../../09_AUDIT/STATE/REPO_DIRECTORY_ROLLUP_20260410.json) |







**复跑（仓库根）**：`python scripts/governance/export_repo_directory_rollup.py`（可选 `--date YYYYMMDD`、`--top N`、`--include-untracked` 把工作区未跟踪且未被 ignore 的路径并入聚合）。大治理批次完成后应 **commit 更新后的 rollup**，便于 diff「哪些前缀已清空」。







**全量路径平面清单（可检索、可 diff）**  



主路径：`docs/09_AUDIT/STATE/REPO_GIT_TRACKED_FILES_20260411.txt`（UTF-8、**无** `quotePath` 转义）；历史：`REPO_GIT_TRACKED_FILES_20260410.txt`（导出时未关 `quotePath`，前几行可能含引号+八进制，**仅作存档**）。







> **注意**：平面清单里若出现带引号或 `\346` 这类片段，**优先**怀疑导出命令未使用 `core.quotePath=false`，**不要**直接推断「索引损坏」；见 `GIT_TRACKED_PATH_ANOMALIES_20260411.md`。







**复跑导出命令（仓库根，PowerShell）**







```powershell



# 必须带 core.quotePath=false，且 Python 用 UTF-8 解码 stdout：



python -c "import subprocess; p=subprocess.check_output(['git','-c','core.quotePath=false','ls-files'],text=True,encoding='utf-8',errors='replace'); lines=sorted(p.splitlines()); open(r'docs/09_AUDIT/STATE/REPO_GIT_TRACKED_FILES_YYYYMMDD.txt','w',encoding='utf-8',newline='\n').write('\n'.join(lines)+'\n')"



```







**复跑统计命令（仓库根，PowerShell）**







```powershell



(git ls-files).Count



git ls-files | ForEach-Object { if ($_ -match '\.([^./\\]+)$') { $matches[1].ToLower() } else { '(noext)' } } | Group-Object | Sort-Object Count -Descending



```







### 1.1 扫描覆盖与文件格式边界（诚实口径 · 全面检查结论）







**任务与脚本当前是否承诺：对仓库内每一种扩展名的每一个文件都做「识别 + 语义分析 + 自动处理」？**  



**不承诺、也做不到。** 以下为**实际覆盖**与**刻意不做**的边界，避免把「清单治理」误解为「全格式 AI 理解」。







| 对象/工具 | 覆盖集合 | 实际做的事 | **不做的事** |



|-----------|-----------|------------|----------------|



| **`git ls-files`** | **已跟踪**的任意扩展名（与协作真源一致） | 平面清单、rollup、扩展名统计（§1） | 不包含 `.gitignore` 路径；**不**解析文件内容语义 |



| **`scripts/governance/export_repo_directory_rollup.py`** | 默认同上；可选 `--include-untracked`（`--others --exclude-standard`） | 按目录深度聚合计数 | 不读文件内容 |



| **`generate_architecture_service_catalog.py`** | 同上中的 `src/`、`pyproject`、API routes | C4 摘要、HTTP 端点、`src/` 目录表 | **不**做全仓 Python AST/调用图；**不**分析二进制 |



| **`sentinel_l1_governance_scan.py`** | 工作区内递归所有 `*.md`（排除 `.git`、`.venv`、`.pytest_cache`、`__pycache__`） | Markdown **内链**可达性、首道 front matter **`module_id` 重复** | **不**扫描正文语义、**不**校验代码块内逻辑；**可能包含未 `git add` 的 .md**（与仅已跟踪清单不同） |



| **`verify_01_blueprints_*` / `verify_manifest_paths_strict.py`** | 指定 INDEX/清单中的路径 | 链接与路径存在性 | 不遍历全库所有文件 |



| **`scripts/governance/scan_duplicate_file_content.py`** | 默认 **Git 已跟踪** + `--ext` 白名单；可选 `--include-untracked` | 内容 **SHA256**，`members[].git_source` 区分 tracked/untracked | **不**自动删；合并走 **§3** C1 + 删稿裁决 Playbook；大文件可用 `--max-mb` 跳过 |



| **`scripts/governance/scan_basename_collisions.py`** | 默认 **`docs/`** 已跟踪 + `--ext`（默认 `md`）；可选 `--all-repo` | 按 **basename** 分组列出**同名不同路径**（C2 输入）；导航名（INDEX/README 等）在 MD 中单独统计 | **不**读正文；**不**自动合并或重命名；消解走 **§3.3** + Owner 裁决 |



| **`scripts/governance/scan_blueprint_d_overlap_candidates.py`** | **`docs/`** 下已跟踪且 basename 含 `BLUEPRINT` 的 `.md`；默认排除 `overnight_runs` | **D 类候选对**：token/H2 相似度、**建议 canonical**、**建议合并大纲**；默认 **score 截断**（`--max-output-pairs`） | **不是** embedding/LLM 语义；**不**自动合稿；裁决与 **低置信合稿登记** 见 D 类 Playbook + 待审登记 |



| **`scripts/governance/triage_blueprint_d_overlap_pairs.py`** | 读入某日的 `BLUEPRINT_D_OVERLAP_CANDIDATES_*.json` | **A 档分流**摘要（`TRIAGE_*.{md,json}`）+ **二审队列** `SECOND_PASS_QUEUE_*.jsonl`；可选 `--queue-mode high_medium` | **不**替代 Owner 签核；二审须配合 二审提示词模板（Playbook **§3.5**） |



| **`scripts/governance/scan_index_health.py`** | 默认 **`docs/`** 下已跟踪 `.md`（可 `--prefix`）；入链来源默认**全库已跟踪** `.md` | 统计 **Markdown 相对链**入链，报告 **零入链** 候选 | **不**解析 HTML/代码块链接；**不**判定「必须出现在某 INDEX」（见 放置规程 **§5.3**）；**不**自动删稿 |



| **`scripts/governance/sample_docs_nav_coverage.py`** | **`docs/`** 下已跟踪 `.md`；合并若干 **INDEX/SITEMAP** 全文为 blob | **P3 抽样**：路径子串是否出现在主导航正文（宽松命中） | **不**等价于「必须在 INDEX 列出」；**不**替代 `scan_index_health` |



| **被忽略路径** | `.gitignore` 等 | 本清单**默认不**纳入「删并」 | 本地密钥、缓存、`.env.qmt` 等由安全与 ignore 策略管 |







**结论（回答「是否涵盖所有格式、是否每一文件都识别分析处理」）**：







- **「涵盖」**：在 **路径级**，`git ls-files` 已覆盖**所有已跟踪**路径（任意后缀）；§1 的扩展名统计可列出当前仓库**已出现**的后缀类型。  



- **「每一文件识别/分析/处理」**：**没有**。当前自动化主要是 **Markdown 链接 + module_id**、**目录计数**、**API 路由抽取**、**特定清单校验**、**内容 hash 重复（C1）**、**basename 碰撞（C2 报表）**、**蓝图 D 类重叠候选（启发式，`scan_blueprint_d_overlap_candidates.py`）**、**D 类 A 档分流 + 二审队列（`triage_blueprint_d_overlap_pairs.py`）**、**零入链报表（`scan_index_health.py`）**；**真·语义等价、业务裁决、二进制内容治理**需 **人工 + 分格式专项**（或外接 LLM 工作流，且须门禁）。  



- **验收建议**：大治理收口时声明以 **「已跟踪 + L1 + verify + rollup」** 为门禁组合；若要求「仅扫描入库文件」，应 **先 `git status` 清干净**或接受 L1 与 `git ls-files` 的已知差异。  



- **索引「是否够健全」**：**L1** 校验相对链**能否解析**；**`scan_index_health.py`** 产出 **`docs/` 下零入链候选**（见 放置规程 **§5.2**），**不**等价于「必须在某 INDEX 出现」；域级 INDEX **覆盖规则**仍属 **§5.3** / 待规则冻结。搬迁后入链/机器清单见同文 **§4**。







### 1.2 Markdown 编码与乱码预防（与 L1 正交）







**L1 不检查正文是否「看起来像乱码」**；编码与字节完整性问题应在**编辑、保存、批量替换**环节预防。







| 要点 | 说明 |



|------|------|



| **统一 UTF-8** | 新建与修改 `*.md` 以 **UTF-8** 保存；换行与 Git 属性见 文档编码标准。 |



| **常见致因** | 用错误代码页打开/另存；非法 UTF-8 被替换为 `` 或残留 `EF BF BD` 字节链；二进制或截断破坏中文多字节；错误的全局替换。 |



| **实操缓解** | 大改前先 **commit 或分支**；大范围替换先小范围试跑并看 diff；归档长文损坏时优先从 **Git 历史** 恢复。 |



| **办公室摘要** | 项目办公室 AI 交接说明 **§0.1.3**。 |



| **全局尽治会话** | GLOBAL_FILE_GOVERNANCE_SESSION_HANDOFF.md 文首硬约束（UTF-8 编辑）与阶段 D。 |







```
```---
```







## 2. 口径：何为「干净」「重复」「有索引」







### 2.1 「没有多余文件」







| 层级 | 含义 | 典型动作 |



|------|------|----------|



| **A. 门禁** | 无密钥、无本机绝对路径、无应忽略的大二进制误提交 | `.gitignore`、pre-commit、密钥扫描（可选） |



| **B. 结构垃圾** | 明确备份/中间产物（`.bak*`、部分 `.diff`）是否允许留在主树 | 归档目录或删除 |



| **C. 内容重复** | 相同或近似相同字节内容 | SHA256 分组，保留 canonical |



| **D. 功能重复** | 两套文档/脚本描述同一职责 | **仅 Owner/架构裁决**，不可自动化硬删 |







### 2.2 「每个文件都能迅速定位」







**目标不是**为每个已跟踪路径各写一条人工索引行（不可持续）。**目标是**分层可达：







- **L1**：仓库根 `README.md`、`docs/INDEX.md`、建设文档 [`INDEX.md`](../INDEX.md)。  



- **L2**：各业务域 `INDEX.md`（仓库内已有大量分布，需治理**孤岛**与**上级链接**）。  



- **L3**：[`docs/SITEMAP.md`](../../../SITEMAP.md)、`docs/System_Manifest.md` 等**总账类**文档（职责以各文件前言为准）。  



- **L4（推荐）**：对 `scripts/`、`tools/` 等增加**生成型清单**（脚本扫描目录 → Markdown/JSON），与手写 INDEX **互补**。







### 2.3 与「扫描 / 合并」可同时推进的工作（总表）







下列工作与 **§3 合并**、**§7 目录队列** **正交或弱依赖**，适合同一治理窗口内并行安排（多 PR 亦可），避免干等报表：







| 工作项 | 典型产出 / 命令 | 与合并的关系 |



|--------|-------------------|----------------|



| **内链健康** | `python scripts/governance/sentinel_l1_governance_scan.py`；修无效相对路径 | **批次收口**或大批量改相对链/搬迁 `.md` 后**推荐**复跑（默认目标 **无效内链 = 0**）；合并过程中亦可边改边修触达文件；**非**「每改一条链就立刻跑」的硬工序（办公室 AI 交接 §0.1.2） |



| **蓝图 / 分散清单 / 总清单校验** | `scripts/governance/verify_01_blueprints_index_links.py`、`scripts/governance/verify_scattered_blueprints_manifest_links.py`、`scripts/governance/verify_manifest_paths_strict.py` | 合并或改路径触及清单内链后**推荐**复跑（常与 L1 同窗口；CI 约定另档） |



| **图纸柜 INDEX** | `python scripts/governance/generate_01_blueprints_index.py` | 动 `01_BLUEPRINTS` 后跑 |



| **`.diff` / `.bak*` 策略** | 归档、剔除跟踪或迁 `archive`（见 P2） | 减少合并噪声与误报重复 |



| **异常路径 / 索引污染** | `review_materials_package` 等引号路径规范化（P2） | 合并前优先，否则链接与 hash 对不齐 |



| **孤儿与重复程序** | 孤儿与重复 Playbook、CANONICAL_POINTERS | D 类与 C2 必用；C1 合并后更新台账 |



| **受控正式稿登记** | CONTROLLED_DOCUMENTS_REGISTER.md | canonical 变更时同步 |



| **仓库根 / 脚本门面** | REPO_ROOT_GOVERNANCE_PLAYBOOK.md、根 `README.md`、`scripts/README.md` | 与文档合并并行，可单独 PR |



| **密钥与忽略** | `.gitignore`、（可选）秘密扫描 | 任意时刻可做；合并批次不阻塞 |



| **卫生总案批次** | 蓝图卫生总案 P0～P3 | 与「删重复」互补，先定摆放再并 |



| **TODO/TBD 台账** | `TODO_CLEANUP_INVENTORY` 等 | 占位清理与合并可同窗 |



| **全系统文档审计 A～H** | 审计方案 | 与尽治同窗但**签字口径独立** |



| **代码重复 / 重构** | 单立 PR + 测试 | **不**与文档合并混批（见 §3.1） |



| **模块全景（逻辑树）** | §2.4；将来 `MODULE_PANORAMA_*` 与 rollup **同频**重跑 | 包名/域改名后重跑，避免索引漂移 |



| **架构服务目录 + C4 多视图** | `python scripts/governance/generate_architecture_service_catalog.py` → `ARCHITECTURE_SERVICE_CATALOG_*` | 改 `src/api`、契约路径或根目录机构文件后重跑；JSON 可检索 |



| **内容重复（后缀白名单）** | `python scripts/governance/scan_duplicate_file_content.py --ext md`（可加 `yaml` 等） | 产出 `DUPLICATE_CONTENT_BY_HASH_*`；**须**人工按 §3 合并 | 默认不扫无扩展名/二进制；大文件见 `--max-mb` |



| **文档地图与放置** | 文档地图与放置规则（**§1.5**、**§1.6**）+ LAYOUT 标准 + 图纸柜规则 + [`ARCHITECTURE.md`](../../../01_FRAMEWORK/ARCHITECTURE.md) | 搬迁/新建目录前**先查格**；**Layer 与路径**见 **§2.3.1**；**「位置是否正确」分桶**见 **§2.3.2** ↔ 规程 **§1.6**；大批归位与 **§7** 同窗 | 新类型目录须先改 LAYOUT §6 或决策记录（见规程 §1） |



| **索引健全性（零入链）** | `python scripts/governance/scan_index_health.py`（可加 `--prefix` 等） | 产出 `INDEX_HEALTH_ORPHAN_*`；与 **L1** 互补 | 不判定域 INDEX 必列；见 放置规程 **§5.2～§5.3** |



| **治理工具归口** | 办公室 治理工具总索引 | 一键查命令与产出 | 实现在 `scripts/governance/`；根目录同名 `.py` 为兼容转发 |







**办公室内规章与上表对齐**：各文件职责与「可并入本窗」的动作见 [项目办公室 README](./README.md) **「办公室内文件一览」**。







### 2.3.1 架构 Layer（0～11）与 `docs/` 落盘：两步决策（防混）







与 放置规程 §1.5 **同一口径**，供整仓搬迁/归位批次使用：







1. **先定技术栈 Layer**：模块主责在 **Layer 0～11** 哪一层，以 [`ARCHITECTURE.md`](../../../01_FRAMEWORK/ARCHITECTURE.md) 为准（含旧称→现行分层对照）。  



2. **再定仓库路径**：该 `.md` 应落在 `docs/` 哪棵子树，以 LAYOUT 标准 + 放置规程 **第 1 节**为准。  



3. **禁止**：仅凭 `docs/10_AI_WORKFLOW` 等路径前缀推断「等于 Layer 10」；以正文、`front matter` 的 `layer`（若有）与 `ARCHITECTURE.md` **一致**为准。







与 AI 交接说明 §3.2 互指；蓝图 YAML 与正文 Layer 冲突时须 **Owner 裁决**后单点收敛。







### 2.3.2「位置是否正确」— 判准与分桶（与放置规程 §1.6 互文）







**目的**：避免把 **「断链已修」「零入链已改善」** 误当成 **「文件已放在 canonical 目录」**。二者相关但**不等价**。







- **真源**：办公室 文档地图与放置规则 **§1.6**（分层判准 + **A～F 分桶表**）；物理树职责仍以 LAYOUT 标准 **§2～§4** 为准。  



- **与 §7.2「摆放」的关系**：§7.2 的摆放验收应能指回 **§1.6** 至少 **A（物理树）+ E（L1/可选 INDEX_HEALTH）**；涉重复合并时叠加 **D**。  



- **与 §1.1 边界的关系**：§1.6 **不**承诺全库每篇业务语义审计或「域 INDEX 必列」硬门禁（仍见 放置规程 §5.3）。







### 2.4 系统架构「模块全景树」与多级索引（三/四级子模块）







**专业机构会不会做这类东西？**  



**会做**，但很少靠「单文件手绘大树」维护到底；更常见的是**组合**：







- **架构/服务目录**（谁拥有、边界、对外接口、依赖关系）；  



- **多视图**（如 C4 的上下文/容器/组件，或本仓库已有的 Layer/域划分叙事）；  



- **可检索清单**（门户、Wiki、JSON —— 与 CMDB 或代码仓生成物衔接）；  



- **生成物 + 少量人工映射**（以包路径、`module_id`、合约为输入，定期重生成；人只维护例外与别名）。







**你是不是「需要」？**  



- **需要一种全景可达性**：否则三、四级子模块只能靠人肉记路径或盲搜。  



- **推荐形态**：**物理全景**（按路径前缀的深度聚合，已有 `REPO_DIRECTORY_ROLLUP_*`）与 **逻辑全景**（按架构层级/业务域/代码包语义命名的树或表）**并列**，并互链；不要混成一种深度口径。  



- **先冻结「什么叫三级、四级」**：在本仓库里是指 `src/` 下第几层包、`docs/0x_*` 域，还是 `LAYERn_*` 文档簇——**定义不同，树就不同**；脚本只能实现**已写明的规则**。







**扫描过程中能不能建、并不断更新？**  



**能。** 建议与整仓扫描**同批次或紧接**执行：







1. **输入**：`git ls-files`（与 rollup 相同）+ 可选从 Markdown 头抽取 `module_id` / 自定义 YAML 映射（若日后引入）。  



2. **输出**：例如 `docs/09_AUDIT/STATE/MODULE_PANORAMA_<date>.json`（机器真源）+ 精简 `.md`（人类浏览）；按约定深度展开 `src/**` 与选定的 `docs/**` 前缀。  



3. **更新节奏**：大治理 PR 后、或季度，与 **rollup 一并重跑**并 commit，用 diff 观察子树漂移。  



4. **与叙事真源的关系**：`docs/System_Manifest.md`、[`docs/SITEMAP.md`](../../../SITEMAP.md)、[`docs/module_designs/INDEX.md`](../../../module_designs/INDEX.md) 等继续承担**解释与裁决**；生成物标注 **generated**，避免「两份真源」静默分叉。  







5. **已落地的机构式组合（本仓库）**：`scripts/governance/generate_architecture_service_catalog.py` 从 **`pyproject.toml`、`git ls-files src/`、`src/api/main.py`、各 `routes/*.py`** 推导 **Context / Containers / Components（HTTP 端点）**、**service_catalog** 与 **根目录机构缺口自检表**，输出 `ARCHITECTURE_SERVICE_CATALOG_*.md/json`；与 **rollup**、以及将来可选的 **`MODULE_PANORAMA_*`** 产物**同频**复跑即可持续刷新。







```
```---
```







## 3. 合并重复文件方案（执行规程）







> **与 §2.1 的对应关系**：本节把 **C（内容重复）**、**basename 碰撞**、**D（功能重复）** 的处置写成**可执行步骤**；**权威流程与叙事归并**仍以 孤儿与重复 Playbook 为准，**canonical 台账**可同步 CANONICAL_POINTERS.md（若项目仍在使用）。**是否删除路径**另见 文件删除与保留裁决 Playbook。







### 3.1 分型：哪些可以合并、哪些禁止自动合并







| 类型 | 判定 | 是否建议自动合并 | 说明 |



|------|------|------------------|------|



| **C1 — 字节级相同** | 全文 SHA256 一致（对选定的文本类扩展名） | **可以批量**，见 §3.2 | 须排除「有意双份」（例如 archive 与活动区按策略应并存）。 |



| **C2 — 同名不同路径** | `basename` 相同、路径不同 | **禁止自动合并** | 内容常不同；先做碰撞报表，**人工指定 canonical**。 |



| **D — 功能重复** | 主题/职责重叠、表述不同 | **禁止自动合并** | 走 Playbook：**先归并叙事与目录结构**，再删稿或改为 stub；需 **Owner/架构裁决**。 |



| **代码重复** | 多文件实现相近逻辑 | **不纳入本文档合并批次** | 单独 PR + 测试与调用方影响分析，避免与文档大扫除混批。 |







**归档区策略（执行前须二选一并写进 PR 说明）**







- **严格**：`docs/06_ARCHIVE/**`（及同类只读归档前缀）**不参与**「删副本」合并，仅在报表中标注「与活动区是否同内容」。  



- **宽松**：允许在台账明确的前提下，将误拷入 archive 的**完全重复**副件删除；**仍需**全仓链接检查。







**Owner 书面裁定（2026-04-11）**：本仓库采用 **宽松** 策略——允许在 文件删除与保留裁决 Playbook 与 **§3.2** 流程下，删除 `docs/06_ARCHIVE/**` 内 **C1（字节级相同）** 的冗余副本并保留唯一 canonical；**活动区 ↔ 归档区**若需长期双份并存，须在 PR 或台账写明理由。下一复审：大版本或每季度与 rollup 同频。







### 3.2 C1 合并的标准操作顺序（推荐固定照做）







1. **出报表**：脚本或手工维护列表，按 hash 分组列出路径（建议输出到 `docs/09_AUDIT/STATE/`，便于 diff）。  



2. **选 canonical**：每组选定**唯一**真源路径（优先：现行规范目录、非 archive、已有 INDEX/SITEMAP 引用多者）。  



3. **全仓替换引用**：将指向副本的 Markdown/配置内链改为指向 canonical（可用仓库级搜索；合并 PR 内应可见替换范围）。  



4. **处理副本**（二选一，在 PR 中注明）：  



   - **删除**：副本无独立历史价值时直接删；或  



   - **stub**：保留路径但正文改为短说明 + 指向 canonical 的链接（适用于外部书签、旧 URL 仍被引用）。  



5. **索引与台账**：更新相关 `INDEX.md`、总入口；若项目使用重复簇台账，更新 CANONICAL_POINTERS.md 或等价文件。  



6. **验证**：跑现有 `verify_*` / `sentinel_l1` 等与链接相关的门禁；必要时补跑蓝图索引脚本（若触及 `01_BLUEPRINTS`）。







### 3.3 C2（同名碰撞）的最小流程







1. 报表列出 `(basename → [paths…])`。  



2. 对每一碰撞簇：**人工打开比对**；指定 canonical。  



3. 若内容不同：**不得**合并为单文件；应通过重命名、移动目录或叙事归并（D 类）消解混淆。  



4. 若内容实为 C1：按 §3.2 执行。







### 3.4 D（功能重复）的最小流程







1. 扫描阶段仅输出**候选簇**（主题关键词、互链、标题相近等），登记台账。  



   - **已落地（启发式）**：`python scripts/governance/scan_blueprint_d_overlap_candidates.py` → `BLUEPRINT_D_OVERLAP_CANDIDATES_*`（**建议 canonical + 建议合并大纲**）；操作规程、**§2.5** 置信度与 **高/低置信双轨** 见 D 类蓝图重叠 Playbook **§5**；**方案文件索引**见上文 **§3.4.1**。  



   - **可选 A 档分流 + 二审输入**：`python scripts/governance/triage_blueprint_d_overlap_pairs.py --date YYYYMMDD` → `BLUEPRINT_D_OVERLAP_TRIAGE_*` + `BLUEPRINT_D_OVERLAP_SECOND_PASS_QUEUE_*.jsonl`；与更强模型配合时使用 二审提示词模板（Playbook **§3.5**）。  



   - **低置信**（合稿写新路径、旧稿 stub、不立刻删）：每例须在 D 类合稿待审登记 **追加一行**（合稿 / stub / archive 列用 **Markdown 相对链** 以便一点就跳）；**高置信**收口 **不**登记该表。  



2. **评审会或异步 Owner 裁决**：确定真源、读者迁移路径、是否保留 stub（**机器建议不等于最终裁决**）。  



3. 再执行正文合并/删稿与链接替换（同 §3.2 第 3～6 步精神，但第 4 步以「叙事归并」为主）。







### 3.4.1 D 类蓝图合稿 — 方案文件索引（办公室）







| 文档 | 用途 |



|------|------|



| D 类蓝图重叠 Playbook | **真源规程**：启发式边界、**§2.5** 置信度（L0～L3）、**§5** 高/低置信与 **高置信可合并**、**§3.5** 分流/二审衔接 |



| 二审提示词模板 | 更强模型输出 JSON：`confidence`、`low_confidence_register`、`recommended_action` 等（与 Playbook **§2.5** 对齐） |



| D 类合稿待审登记 | **仅低置信**合稿台账（可点击相对链） |



| 治理工具总索引 | **§2** 推荐复跑顺序中的步 **7 / 7′**（`scan_blueprint_d_overlap_candidates.py`、`triage_blueprint_d_overlap_pairs.py`） |



| 项目办公室 AI 交接说明 | 接手阅读顺序 **①″-D**、路径速查；**§0.1** Git / L1 / UTF-8；**§0.1.4** ignore 与 `STATE/` 两条线；**§0.2** Solo+全委托 AI 机械清单 |



| 文档编码标准 | Markdown/文本 **UTF-8** 等全文真源；与本文 **§1.2**、AI 交接 §0.1.3 互指 |



| 全局文件治理会话交接 | 新会话可复制指令；阶段 A 含 D 类必读 |



| 文档地图与放置规则 | **§1.6 分桶 D** 与 D 类低置信登记互指 |







### 3.5 与扫描并行时的分工（四条线程）







| 线程 | 内容 | 与合并的关系 |



|------|------|----------------|



| **A** | 持续生成/更新：全量清单、hash 分组、basename 报表、异常路径列表 | 为 B/C 提供输入。 |



| **B** | 仅处理 **C1** 已确认分组：canonical + 替换链接 + 删或 stub | 可与 A **并行**，以报表为闸门。 |



| **C** | 断链修复、`.diff`/`.bak` 策略、脚本目录生成型 INDEX、各域导航补链、§2.3 表内校验与登记 | 与合并正交，可并行。 |



| **D** | **D 类**只维护台账与排期，**评审通过前**不删不并 | 与 A 并行；合并滞后一拍。 |



| **D′（蓝图）** | 跑 `scan_blueprint_d_overlap_candidates.py`，从 **TOP-N 候选对**起做 Owner 评审与合稿排期；可选再跑 `triage_blueprint_d_overlap_pairs.py` 生成 **TRIAGE** + **SECOND_PASS_QUEUE** 供二审；**低置信**产出登记 待审登记 | 与 **§3.4**、Playbook **§5** / **§3.5** 对齐；可与 **§7** 同窗口 |



| **E（可选）** | **§7 目录队列**：按 rollup 子前缀做「退出标准」勾选，与 B 交替推进 | 合并清空某前缀后，该前缀的 C1/C2 报表应**收敛** |







### 3.6 §3 勾选（合并专项）







- [x] 书面选定 **归档区策略**（§3.1 严格 / 宽松）。（2026-04-11：**宽松**，见 §3.1 末段 Owner 裁定。）  



- [x] C1：至少完成一轮 hash 报表 + 对**已裁决**簇执行 §3.2（可分多 PR）。（2026-04-11：`docs/06_ARCHIVE/temp_pending/` 内 `DUPLICATE_CONTENT_BY_HASH_20260410` 所报 **5 簇**已合并为 **5 个 canonical**，副本已删；台账见 [`06_ARCHIVE/INDEX`](../../../06_ARCHIVE/INDEX.md)（原 `temp_pending` 合并记录见 git 历史）。复跑 `DUPLICATE_CONTENT_BY_HASH_20260411.md`：`duplicate_clusters=0`。）  



- [x] C2：basename 报表完成；对**高优先级**碰撞簇完成 canonical 或重命名消解。（2026-04-11：**非导航 basename 已清空**；报表中余碰撞均为导航名分表，多份并存为预期，不纳入 C2 强制消解。）（**报表**：`BASENAME_COLLISIONS_20260411.md` — 复跑后 `docs/` 下 `.md` 碰撞 basename **4**、非导航名 **0**（余 **4** 均为导航名 `INDEX`/`README`/`SITEMAP`/`CHANGELOG`，多份并存为预期形态）。**已消解 1 簇**：`DATA_QUALITY_MONITORING_BLUEPRINT.md` — canonical 仅保留 `01_BLUEPRINTS/...`；`01_FRAMEWORK` / `10_AI_WORKFLOW` 正文迁入 [`../../../06_ARCHIVE/20260411_c2_data_quality_monitoring/README.md`](../../../06_ARCHIVE/20260411_c2_data_quality_monitoring/README.md)；Layer8 改为 `DATA_QUALITY_MONITORING_LAYER8_MODULE.md`。**已消解 2 簇**：`API_GATEWAY_BLUEPRINT.md` — canonical `API_GATEWAY_BLUEPRINT.md`；删除 Layer8 同名占位稿，入口改为 `API_GATEWAY_LAYER8_MODULE.md`（`git add` 含删除后复跑 `scan_basename_collisions.py` 可自报表剔除该簇）。**已消解 3 簇**：`DISASTER_RECOVERY_BLUEPRINT.md` — canonical `DISASTER_RECOVERY_BLUEPRINT.md`；`01_FRAMEWORK` 入口 `DISASTER_RECOVERY_FRAMEWORK_ENTRY.md`；旧稿快照 [`../../../06_ARCHIVE/20260410_c2_disaster_recovery/README.md`](../../../06_ARCHIVE/20260410_c2_disaster_recovery/README.md)。**已消解 4 簇**：`BENCHMARK_MANAGEMENT_BLUEPRINT.md` — canonical `BENCHMARK_MANAGEMENT_BLUEPRINT.md`；`11_STRATEGIC_DECISION` 入口 `BENCHMARK_MANAGEMENT_STRATEGIC_ENTRY.md`；旧稿 [`../../../06_ARCHIVE/20260410_c2_benchmark_management/README.md`](../../../06_ARCHIVE/20260410_c2_benchmark_management/README.md)。**已消解 5 簇**：`COMPLIANCE_MONITORING_BLUEPRINT.md` — canonical `10_AI_WORKFLOW/...`；Layer8 入口 `COMPLIANCE_MONITORING_LAYER8_MODULE.md`。**已消解 6 簇**：`FULL_PROCESS_DATA_PERSISTENCE_BLUEPRINT.md` — canonical `FULL_PROCESS_DATA_PERSISTENCE_BLUEPRINT.md`；`LAYER4_ML` 入口 `FULL_PROCESS_DATA_LAYER4_ENTRY.md`；旧稿 [`../../../06_ARCHIVE/20260410_c2_full_process_data_persistence/README.md`](../../../06_ARCHIVE/20260410_c2_full_process_data_persistence/README.md)。**已消解 7 簇**：`TRANSACTION_COST_ANALYSIS_BLUEPRINT.md` — canonical `10_AI_WORKFLOW/...`；`01_FRAMEWORK` 入口 `TRANSACTION_COST_ANALYSIS_FRAMEWORK_ENTRY.md`；Layer8 `79_` 入口 `TRANSACTION_COST_ANALYSIS_LAYER8_MODULE.md`；旧稿 [`../../../06_ARCHIVE/20260410_c2_transaction_cost_analysis/README.md`](../../../06_ARCHIVE/20260410_c2_transaction_cost_analysis/README.md)。**已消解 8 簇**：`STRATEGY_LIFECYCLE_MANAGEMENT_BLUEPRINT.md` — canonical `10_AI_WORKFLOW/...`；Layer8 `81_` 入口 `STRATEGY_LIFECYCLE_MANAGEMENT_LAYER8_MODULE.md`；`p1_cleanup_archive` 同 basename 副本迁入 [`../../../06_ARCHIVE/20260410_c2_strategy_lifecycle_management/README.md`](../../../06_ARCHIVE/20260410_c2_strategy_lifecycle_management/README.md)。**已消解 9 簇**：`MODEL_RISK_MANAGEMENT_BLUEPRINT.md` — canonical `01_FRAMEWORK/...`；Layer8 `77_` 入口 `MODEL_RISK_MANAGEMENT_LAYER8_MODULE.md`；旧稿 [`../../../06_ARCHIVE/20260410_c2_model_risk_management/README.md`](../../../06_ARCHIVE/20260410_c2_model_risk_management/README.md)。**已消解 10 簇**：`MARKET_REGIME_DETECTION_BLUEPRINT.md` — canonical `01_BLUEPRINTS/...`；`10_AI_WORKFLOW` 入口 `MARKET_REGIME_DETECTION_AI_WORKFLOW_ENTRY.md`；旧稿 [`../../../06_ARCHIVE/20260410_c2_market_regime_detection/README.md`](../../../06_ARCHIVE/20260410_c2_market_regime_detection/README.md)。**已消解 11 簇**：`PERFORMANCE_ATTRIBUTION_BLUEPRINT.md` — canonical `11_STRATEGIC_DECISION/...`；Layer8 `83_` 入口 `PERFORMANCE_ATTRIBUTION_LAYER8_MODULE.md`；旧稿 [`../../../06_ARCHIVE/20260410_c2_performance_attribution/README.md`](../../../06_ARCHIVE/20260410_c2_performance_attribution/README.md)。**已消解 12 簇**：`DATA_VERSION_CONTROL_BLUEPRINT.md` — canonical `01_BLUEPRINTS/...`；`LAYER4_ML` 入口 `DATA_VERSION_CONTROL_LAYER4_ENTRY.md`；`p1_cleanup_archive` 与 Layer4 同名稿迁入 [`../../../06_ARCHIVE/20260410_c2_data_version_control/README.md`](../../../06_ARCHIVE/20260410_c2_data_version_control/README.md)。**已消解 13 簇**：`MODEL_PERFORMANCE_VERSION_MANAGEMENT_BLUEPRINT.md` — canonical `10_AI_WORKFLOW/...`；`p1_cleanup_archive` 副本 [`../../../06_ARCHIVE/20260410_c2_model_performance_version_management/README.md`](../../../06_ARCHIVE/20260410_c2_model_performance_version_management/README.md)。**已消解 14 簇**：`RESEARCH_WORKFLOW_MANAGEMENT_BLUEPRINT.md` — canonical `10_AI_WORKFLOW/...`；`p1_cleanup_archive` 副本 [`../../../06_ARCHIVE/20260410_c2_research_workflow_management/README.md`](../../../06_ARCHIVE/20260410_c2_research_workflow_management/README.md)。**已消解 15 簇**：`REALTIME_RISK_MONITORING_BLUEPRINT.md` — canonical `01_FRAMEWORK/...`；Layer8 `64_` 入口 `REALTIME_RISK_MONITORING_LAYER8_MODULE.md`；旧稿 [`../../../06_ARCHIVE/20260410_c2_realtime_risk_monitoring/README.md`](../../../06_ARCHIVE/20260410_c2_realtime_risk_monitoring/README.md)。**已消解 16 簇**：`STRATEGY_ENGINE_BLUEPRINT.md` — canonical `01_BLUEPRINTS/...`；战术域入口 `STRATEGY_ENGINE_TACTICS_ENTRY.md`；旧稿 [`../../../06_ARCHIVE/20260410_c2_strategy_engine/README.md`](../../../06_ARCHIVE/20260410_c2_strategy_engine/README.md)。**已消解 17 簇**：`STRATEGY_SELECTION_BLUEPRINT.md` — canonical `01_BLUEPRINTS/...`；战术域入口 `STRATEGY_SELECTION_TACTICS_ENTRY.md`；旧稿 [`../../../06_ARCHIVE/20260410_c2_strategy_selection/README.md`](../../../06_ARCHIVE/20260410_c2_strategy_selection/README.md)。**已消解 18～20 簇**：`P0_FIX_COMPLETION_REPORT_V13_20260407.md`、`RESPONSIBILITY_FIX_REPORT_20260407_030139.md`、`VERSION_CONSISTENCY_REPORT_20260407.md` — canonical 均保留 [`audit_state/INDEX.md`](../../04_OPERATIONS/audit_state/INDEX.md) 原路径；`p1_cleanup_archive` 三份迁入 [`../../../06_ARCHIVE/20260410_c2_p1_audit_report_basenames/README.md`](../../../06_ARCHIVE/20260410_c2_p1_audit_report_basenames/README.md)。**已消解 21 簇**：`SHORT_TERM_IMPROVEMENT_COMPLETION_REPORT_20260407.md` — canonical `09_AUDIT/REPORTS/...`；`STATE` 同名稿 [`../../../06_ARCHIVE/20260410_c2_short_term_improvement_completion/README.md`](../../../06_ARCHIVE/20260410_c2_short_term_improvement_completion/README.md)；`INDEX_GROUPED_STATE_20260408` 内链已指向 REPORTS。**已消解 22～24 簇**：`DEEP_AUDIT_REPORT_20260407.md`、`DEEP_AUDIT_REPORT_V7_20260404.md`、`FINAL_AUDIT_REPORT_20260407.md` — 与 `09_AUDIT/REPORTS` 同名但**正文不同**；`audit_state` 侧分别重命名为 `LAYER6_DEEP_AUDIT_REPORT_20260407.md`、`LAYER5_DEEP_AUDIT_REPORT_V7_20260404.md`、`LAYER6_FINAL_AUDIT_REPORT_20260407.md`，并更新 [`audit_state/INDEX.md`](../../04_OPERATIONS/audit_state/INDEX.md) 与 `VERSION_CONSISTENCY_REPORT_20260407` 表内路径；`06_ARCHIVE/20260407_old_layer_audit_reports/layer6_reports` 下旧稿同步改为 `LAYER6_DEEP_AUDIT_REPORT_20260407_legacy_layer6_reports_archive.md` 以免再撞 basename。**已消解 25 簇**：`DOCUMENT_METADATA_TEMPLATE.md` — canonical `09_AUDIT/STANDARDS/...`；`p1_cleanup_archive` 副本 [`../../../06_ARCHIVE/20260410_c2_document_metadata_template/README.md`](../../../06_ARCHIVE/20260410_c2_document_metadata_template/README.md)。**已消解 26～27 簇**：`DEEP_AUDIT_REPORT_V24_20260407_025847.md`、`FULL_SYSTEM_DOCUMENT_GOVERNANCE_DEEP_AUDIT_REPORT_V12_20260407.md` — canonical 保留 [`audit_state/INDEX.md`](../../04_OPERATIONS/audit_state/INDEX.md)；`p1_cleanup_archive` 双份 [`../../../06_ARCHIVE/20260410_c2_p1_audit_reports_batch2/README.md`](../../../06_ARCHIVE/20260410_c2_p1_audit_reports_batch2/README.md)。**已消解 28 簇**：`DEEP_AUDIT_REPORT_V3_20260407.md` — `LAYER4_ML` 与 `audit_state` 撞名异文；`audit_state` 侧改为 `LAYER8_DEEP_AUDIT_REPORT_V3_20260407.md` 并更新索引/一致性表。**已消解 29 簇**：`INDEX_GROUPED_20260408.md` — 拆为 `INDEX_GROUPED_REPORTS_20260408.md` 与 `INDEX_GROUPED_STATE_20260408.md`；`09_AUDIT` / `HANDOFF` / 卫生总案等内链已对齐。**已消解 30～32 簇**：`FACTOR_MANAGEMENT_STANDARD` / `FACTOR_REGISTRY` / `FACTOR_TAXONOMY` — `09_ARCHIVE/duplicates` 三稿分别改为 `*_legacy_09_archive_duplicates.md`，与 `02_FACTOR_LIBRARY/01_STANDARDS` 真源 basename 脱钩。**已消解 33 簇**：`ALPHA_FACTOR_LAYER_DEEP_AUDIT_REPORT_ROUND2_20260407_191332.md` — duplicates 侧同上 `_legacy_09_archive_duplicates`。**已消解 34 簇**：`DOCUMENT_CREATION_CHECKLIST.md` — canonical `07_OPERATIONS/checklists/DOCUMENT_CREATION_CHECKLIST.md`；`01_FRAMEWORK` 旧稿迁入 [`../../../06_ARCHIVE/20260410_c2_document_creation_checklist/README.md`](../../../06_ARCHIVE/20260410_c2_document_creation_checklist/README.md)。**已消解 35 簇**：`DOCUMENT_GOVERNANCE_DEEP_AUDIT_REPORT.md` — `09_RESEARCH_INNOVATION` 保留 canonical；`06_ARCHIVE/20260404_audit_reports_archive/audit_state` 副本改为 `DOCUMENT_GOVERNANCE_DEEP_AUDIT_REPORT_legacy_20260404_audit_reports_archive.md`（[`20260404_audit_reports_archive/INDEX.md`](../../../06_ARCHIVE/20260404_audit_reports_archive/INDEX.md) 已改链）。**已消解 36 簇**：`FAQ.md` — `07_OPERATIONS` 改为 `IMPLEMENTATION_OPERATIONS_FAQ.md` 并修 `DATA_MIGRATION_GUIDE` / `ERROR_CODES` / `TROUBLESHOOTING_GUIDE`；duplicates 侧 `FAQ_legacy_09_archive_duplicates.md`。**已消解 37～39 簇**：`overnight_runs/20260408_*` 下 `CONSOLIDATED_REPORT_FOR_AI` / `invalid_links_detail` / `module_id_duplicates_detail` — basename 追加 `_<run_id>`；`overnight_audit_runner.py` 已同步改为带后缀输出。**已消解 40 簇**：`06_ARCHIVE` 下四处 `ARCHIVE_README.md` — 分别改为 `ARCHIVE_README_06_ARCHIVE_ROOT.md` 等，子目录 `INDEX.md` 已改链。**已消解 41 簇**：`02_FACTOR_LIBRARY` 内 33 份 `OVERVIEW.md` — 统一改为 `FACTOR_LIB_*_OVERVIEW.md`，各模块 `INDEX.md` 已对齐。**C2（非导航 basename）**：已清空。）  



- [ ] D：候选簇已登记（`BLUEPRINT_D_OVERLAP_CANDIDATES_*` / Playbook）；可选已跑 **triage**（`BLUEPRINT_D_OVERLAP_TRIAGE_*`、`SECOND_PASS_QUEUE_*.jsonl` + 二审模板）；**已裁决**簇完成叙事归并 + 链接 + 台账；**低置信**合稿若有进行，待审登记 与实现一致。（2026-04-12：**机器候选已刷新** — `BLUEPRINT_D_OVERLAP_CANDIDATES_20260412.md`：扫描蓝图 **758**、截断前 **12244** 对、写入 **400** 对；**分流/二审产出示例** — `TRIAGE_20260412.md`、[`SECOND_PASS_QUEUE_20260412.jsonl`](../../../09_AUDIT/STATE/BLUEPRINT_D_OVERLAP_SECOND_PASS_QUEUE_20260412.jsonl)；**最终裁决与合稿仍待 Owner** 按 Playbook 从高分起评审。）  



- [ ] 合并相关 PR 均附：替换范围摘要、已跑验证脚本列表。







```
```---
```







## 4. 任务波次（勾选进度）







### P0 — 基线与自动化（本轮已部分完成）







- [x] 导出全量 `git ls-files` 平面清单至 `docs/09_AUDIT/STATE/`（见上文文件名）。  



- [x] 记录扩展名与目录聚合统计（见 §1）。  



- [x] 生成 **深度 3～6** 目录聚合（JSON + MD）：`python scripts/governance/export_repo_directory_rollup.py` → `REPO_DIRECTORY_ROLLUP_*`（2026-04-11 起脚本内 `git ls-files` 使用 **`core.quotePath=false`**；当前快照 `20260411`；历史 `20260410` 仍可对照）。  



- [x] 约定**更新频率**（例如每次大版本或每季度）并写入 [项目办公室 README](./README.md) 或本文件版本记录。（2026-04-11：已写入办公室 README「基线复跑约定」；与本文件 §3.1 末段复审口径一致。）







### P1 — 重复与冗余（机器可做部分）







- [x] **同名不同路径**：对 basename 碰撞做报表（脚本或 `git ls-files` 后处理），人工判 canonical；**合并/重命名步骤见 §3.3**。（2026-04-11：已落地 `scripts/governance/scan_basename_collisions.py` → `BASENAME_COLLISIONS_20260411.md`；**§3.6 C2（非导航）已勾选完成**，余导航名碰撞见报表分表。）  



- [x] **同内容（按后缀白名单）**：`scripts/governance/scan_duplicate_file_content.py`（例：`--ext md`）→ `docs/09_AUDIT/STATE/DUPLICATE_CONTENT_BY_HASH_*`；**合并/删稿仍须**遵守 **§3.2** 与归档策略 **§3.1**。  



- [x] 将结果与 孤儿与重复 Playbook 对齐，**先归并再删**；与 **§3.6** 勾选一并推进。（2026-04-10：**流程对齐**已落实 — C1/C2 已按 §3.2/§3.3 与归档策略执行；后续每一批合并/删稿仍须逐 PR 对照 Playbook **先归并再删**；D 类按 D 类 Playbook 单列。）







### P2 — 明显「多余」扩展名与审计衍生物







- [x] 评审 **50** 个已跟踪 `.diff`：保留标准、迁 archive、或从跟踪中移除。（2026-04-10：50 个均为双 YAML **dry-run** 样本，已从 `docs/09_AUDIT/STATE/` **整体迁出**至 [`../../../06_ARCHIVE/20260408_double_yaml_dryrun_sample/README.md`](../../../06_ARCHIVE/20260408_double_yaml_dryrun_sample/README.md)；`OPENCLAW_REMEDIATION_EXECUTION_PLAYBOOK_20260408.md`、`DOC_REMEDIATION_TASK_DIRECTIVE_20260408.md` 已改为「每批自建 `double_yaml_dryrun_<YYYYMMDD>/`」并互指归档样本。）  



- [x] 评审 `.bak2` / `.bak3` 等：是否应仅存于 archive 或本地（不进 Git）。（2026-04-10：`docs/System_Manifest.md.bak3` → [`../../../06_ARCHIVE/20260410_system_manifest_backup/README.md`](../../../06_ARCHIVE/20260410_system_manifest_backup/README.md)；`docs/06_ARCHIVE/encoding_backups/...*.bak2` 已位于 archive，保留为编码修复历史备份。）  



- [x] 对 `review_materials_package` 等路径中异常引号/命名（Windows 下曾出现统计异常）做**路径规范化**（若仍存在）。（2026-04-10：**工作区/索引**已为 UTF-8 中文名，**无**须 `git mv` 的「坏路径」。2026-04-11：**根因**为默认 `git ls-files` **显示转义** + 部分脚本未关 `quotePath`，导致 rollup/清单误判；已统一治理脚本 `git -c core.quotePath=false ls-files` 并刷新 `REPO_DIRECTORY_ROLLUP_20260411`、[`REPO_GIT_TRACKED_FILES_20260411.txt`](../../../09_AUDIT/STATE/REPO_GIT_TRACKED_FILES_20260411.txt)；说明见 `GIT_TRACKED_PATH_ANOMALIES_20260411.md`。）







### P3 — 索引可达性（导航）







- [x] 从 `docs/INDEX.md` 与 [`../INDEX.md`](../INDEX.md) 出发做**抽样反向检查**：随机/分层抽样路径子串是否出现在合并后的主导航正文（宽松命中；**不**等价「必须在 INDEX 列出」）。（2026-04-11：`python scripts/governance/sample_docs_nav_coverage.py` → 样例报告 `DOCS_NAV_COVERAGE_SAMPLE_20260410.md`，参数示例 n=200、seed=42；完整口径见 **§1.1** `sample_docs_nav_coverage.py` 行。）  



- [x] `scripts/`：在 [scripts/README.md](../../../../scripts/README.md) 或生成清单中补齐**分类导航**（与脚本数量匹配）。（2026-04-10：增 **分类导航（P3）** 小节 + 治理表补 `scan_basename_collisions.py`。）  



- [x] `src/`：在根 README 或 `src/` 下 INDEX 中保证模块入口**可跳转**。（2026-04-10：新增 [`src/README.md`](../../../../src/README.md)；根 [README.md](../../../../README.md)「项目结构」互指。）







### P4 — 与现有门禁脚本对齐







#### P4.1 P1～P3 产出与门禁脚本衔接矩阵（与 §1.1 一致）







| 关切 / 产出 | 脚本或门禁（`scripts/governance/` 为主） | **不做的事**（与 §1.1 同口径） |



|-------------|--------------------------------------------|--------------------------------|



| 目录体量与拆队列（P0 / §7） | `export_repo_directory_rollup.py` | 不读文件内容语义 |



| Markdown 内链 + 首道 `module_id` | `sentinel_l1_governance_scan.py` | 不扫正文语义；工作区 md 可能与 `git ls-files` 不一致 |



| 总清单 / INDEX 路径存在性 | `verify_manifest_paths_strict.py`、`verify_01_blueprints_index_links.py`、`verify_scattered_blueprints_manifest_links.py` | 不遍历全库所有文件 |



| 同内容重复（C1） | `scan_duplicate_file_content.py`（须 `--ext`） | 不自动删；删并走 §3.2 + 删稿 Playbook |



| 同名不同路径（C2） | `scan_basename_collisions.py` | 不读正文；不自动合并 |



| 蓝图主题可能重叠（D） | `scan_blueprint_d_overlap_candidates.py`、`triage_blueprint_d_overlap_pairs.py` | 非 embedding 语义；不自动合稿；二审须模板 + Owner |



| `docs/` 零入链候选 | `scan_index_health.py` | 不裁决「必须出现在某 INDEX」 |



| 主导航正文覆盖率（P3 抽样） | `sample_docs_nav_coverage.py` | 不替代 `scan_index_health`；宽松子串命中 |



| 架构 / API / `src/` 目录表 | `generate_architecture_service_catalog.py` | 不做全仓 AST 调用图 |



| 首道 `module_id` 缺失 | `backfill_missing_module_id.py`（`--apply` 后须复跑 L1） | 不修复业务正文质量 |







- [x] 将本清单 P1～P3 的产出与现有 `scripts/governance/verify_*`、`sentinel_l1_*` 等**能衔接的检查项**列成表（避免重复造轮子）；**矩阵须与 §1.1 一致**（脚本名 ↔ 覆盖集合 ↔ 不做的事）。（2026-04-10：见上表 **P4.1**。）  



- [x] **架构/服务目录 + C4 摘要 + 可检索 JSON**：`generate_architecture_service_catalog.py` → `docs/09_AUDIT/STATE/ARCHITECTURE_SERVICE_CATALOG_20260410.{md,json}`（2026-04-10）；含根目录机构缺口表。  



- [x] 「重复内容报表」：`scan_duplicate_file_content.py`（已落地）；可选后续接 CI **仅告警**。  



- [ ] 可选：新增 **模块全景**生成脚本（或扩展现有 rollup）：按 **§2.4** 约定深度输出 `MODULE_PANORAMA_*.{json,md}`，与 rollup **同批**重跑；[`scripts/README.md`](../../../../scripts/README.md) 登记用途。







### P5 — 深度尽治（与 §7 对齐）







- [ ] 按 **§7.1** 建立「前缀队列」并分批 PR（建议每批可 review 的规模）。  



- [ ] 对每批执行 **§7.2** 退出标准，直至 **§7.3** 总勾选可勾或例外已登记。  



- [ ] 批次间 **重跑 rollup** 与平面清单，保留 JSON diff 作证据。







**§7.2 子批执行备忘（证据链，非总里程碑替代）**







- **2026-04-14 · 前缀 `docs/09_AUDIT/REPORTS`（门面批次）**：复跑 `scan_index_health.py --prefix docs/09_AUDIT/REPORTS --date 20260414` → `INDEX_HEALTH_ORPHAN_20260414.md`（**zero_inbound=0**）；`export_repo_directory_rollup.py --date 20260414` → `REPO_DIRECTORY_ROLLUP_20260414.md`；门面 [`REPORTS/README.md`](../../../09_AUDIT/REPORTS/README.md)、[`REPORTS/INDEX.md`](../../../09_AUDIT/REPORTS/INDEX.md)、`INDEX_GROUPED_REPORTS_20260408.md` 与 [`STATE/INDEX.md`](../../../09_AUDIT/STATE/INDEX.md) 产出表互指上述快照；**本批未改** REPORTS 下数百报告正文（§7.1：超大前缀先门面与机器证据，再分子队列）。



- **2026-04-15 · 前缀 `docs/05_IMPLEMENTATION/04_OPERATIONS`（门面批次）**：复跑 `scan_index_health.py --prefix docs/05_IMPLEMENTATION/04_OPERATIONS --date 20260415` → `INDEX_HEALTH_ORPHAN_20260415.md`（**zero_inbound=0**；候选 md **353**）；体量互指既有 `REPO_DIRECTORY_ROLLUP_20260414.md`（本前缀 **407** 条）；更新 [`../../04_OPERATIONS/README.md`](../../04_OPERATIONS/README.md)、[`04_OPERATIONS/INDEX.md`](../../04_OPERATIONS/INDEX.md) 与 [`STATE/INDEX.md`](../../../09_AUDIT/STATE/INDEX.md) 产出表；**本批未改** `audit_state/` 内长列表正文。



- **2026-04-16 · 前缀 `docs/09_AUDIT/STATE`（门面批次）**：复跑 `scan_index_health.py --prefix docs/09_AUDIT/STATE --date 20260416` → `INDEX_HEALTH_ORPHAN_20260416.md`（**zero_inbound=0**；候选 md **182**）；体量互指既有 `REPO_DIRECTORY_ROLLUP_20260414.md`（本前缀 **390** 条）；更新 [`STATE/INDEX.md`](../../../09_AUDIT/STATE/INDEX.md)、[`09_AUDIT/INDEX.md`](../../../09_AUDIT/INDEX.md)、[`REPORTS/INDEX.md`](../../../09_AUDIT/REPORTS/INDEX.md)；**本批未改** STATE 下大量历史报告正文。



- **2026-04-17 · 前缀 `docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS`（门面批次）**：复跑 `scan_index_health.py --prefix docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS --date 20260417` → `INDEX_HEALTH_ORPHAN_20260417.md`（**zero_inbound=0**；候选 md **266**；首轮曾 **18**，已通过 [`../01_BLUEPRINTS/REPORTS/README.md`](../01_BLUEPRINTS/REPORTS/README.md) 挂 12 份报告链 + [`../05_DESIGN_DOCS/INDEX.md`](../05_DESIGN_DOCS/INDEX.md) 挂 6 份子域 `INDEX` 入链后复跑归零）；体量互指 `REPO_DIRECTORY_ROLLUP_20260414.md`（本前缀 **272** 条）；更新 [`06_CONSTRUCTION_DOCS/README.md`](../README.md)、[`06_CONSTRUCTION_DOCS/INDEX.md`](../INDEX.md) 与 [`STATE/INDEX.md`](../../../09_AUDIT/STATE/INDEX.md) 产出表。



- **2026-04-18 · 前缀 `docs/06_ARCHIVE/20260404_audit_reports_archive`（归档区 · 门面批次）**：`scan_index_health.py` 增 **archive 子 `--prefix` 时取消对该 archive 根默认排除**（否则候选恒 0）；复跑 `--prefix docs/06_ARCHIVE/20260404_audit_reports_archive --date 20260418` → `INDEX_HEALTH_ORPHAN_20260418.md`（**zero_inbound=0**；候选 **183**；首轮 **5** 处经 [`20260404_audit_reports_archive/INDEX.md`](../../../06_ARCHIVE/20260404_audit_reports_archive/INDEX.md)、[`technical_reviews/INDEX.md`](../../../06_ARCHIVE/20260404_audit_reports_archive/technical_reviews/INDEX.md)、[`archived_reports_20260402/INDEX.md`](../../../06_ARCHIVE/20260404_audit_reports_archive/archived_reports_20260402/INDEX.md) 补链后归零）；体量 `REPO_DIRECTORY_ROLLUP_20260414.md`（**218** 条）；**本批未做删并**（§7.1：归档区只读治理为主）。



- **2026-04-19 · 前缀 `docs/05_IMPLEMENTATION/05_TECHNICAL_SPECIFICATIONS`（门面批次）**：复跑 `scan_index_health.py --prefix docs/05_IMPLEMENTATION/05_TECHNICAL_SPECIFICATIONS --date 20260419` → `INDEX_HEALTH_ORPHAN_20260419.md`（**zero_inbound=0**；候选 **97**；首轮 **`INDEX.md` 自身** 零入链，已由 [`05_IMPLEMENTATION/INDEX.md`](../../INDEX.md) 显式指向 `./05_TECHNICAL_SPECIFICATIONS/INDEX.md` 后归零）；[`05_TECHNICAL_SPECIFICATIONS/INDEX.md`](../../05_TECHNICAL_SPECIFICATIONS/INDEX.md) 增机器产出小节；体量 `REPO_DIRECTORY_ROLLUP_20260414.md`（**97** 条）。



- **2026-04-20 · 前缀 `docs/02_FACTOR_LIBRARY/04_DATA_SOURCE`（门面批次）**：复跑 `scan_index_health.py --prefix docs/02_FACTOR_LIBRARY/04_DATA_SOURCE --date 20260420` → `INDEX_HEALTH_ORPHAN_20260420.md`（**zero_inbound=0**；候选 md **81**）；[`04_DATA_SOURCE/INDEX.md`](../../../02_FACTOR_LIBRARY/04_DATA_SOURCE/INDEX.md) 增机器产出小节；[`02_FACTOR_LIBRARY/INDEX.md`](../../../02_FACTOR_LIBRARY/INDEX.md) 显式链至 `./04_DATA_SOURCE/INDEX.md`；体量 `REPO_DIRECTORY_ROLLUP_20260414.md`（本前缀 **83** 条；与候选 md 数差含非 `.md` 等属正常口径差）。



- **2026-04-21 · 前缀 `docs/05_IMPLEMENTATION/07_OPERATIONS`（门面批次）**：复跑 `scan_index_health.py --prefix docs/05_IMPLEMENTATION/07_OPERATIONS --date 20260421` → `INDEX_HEALTH_ORPHAN_20260421.md`（**zero_inbound=0**；候选 md **62**；首轮 **10** 处子域 `README`/`INDEX` 零入链，已由 [`07_OPERATIONS/INDEX.md`](../../07_OPERATIONS/INDEX.md) 子目录表补链后归零）；[`05_IMPLEMENTATION/INDEX.md`](../../INDEX.md) 增「运维手册总索引」并子目录表链至 `./07_OPERATIONS/INDEX.md`；体量 `REPO_DIRECTORY_ROLLUP_20260414.md`（本前缀 **62** 条）。



- **2026-04-22 · 前缀 `docs/09_ARCHIVE/duplicates`（归档重复池 · 门面批次）**：复跑 `scan_index_health.py --prefix docs/09_ARCHIVE/duplicates --date 20260422` → `INDEX_HEALTH_ORPHAN_20260422.md`（**zero_inbound=0**；候选 md **54**；首轮 **45** 处零入链，已由 [`duplicates/INDEX.md`](../../../09_ARCHIVE/duplicates/INDEX.md) 增「全量挂载」清单后归零；**不**做删并）；[`09_ARCHIVE/INDEX.md`](../../../09_ARCHIVE/INDEX.md) 门面首链对齐 `./duplicates/INDEX.md`；体量 `REPO_DIRECTORY_ROLLUP_20260414.md`（本前缀 **54** 条）。



- **2026-04-23 · 前缀 `docs/06_ARCHIVE/20260408_double_yaml_dryrun_sample`（归档 · dry-run 样本）**：复跑 `scan_index_health.py --prefix docs/06_ARCHIVE/20260408_double_yaml_dryrun_sample --date 20260423` → `INDEX_HEALTH_ORPHAN_20260423.md`（**zero_inbound=0**；候选 md **1**；其余 **50** 个为 `.diff` 不在 md 入链口径）；[`../../../06_ARCHIVE/20260408_double_yaml_dryrun_sample/README.md`](../../../06_ARCHIVE/20260408_double_yaml_dryrun_sample/README.md) 增 P5 门面；[`06_ARCHIVE/INDEX.md`](../../../06_ARCHIVE/INDEX.md) 目录表增本样本行；体量 `REPO_DIRECTORY_ROLLUP_20260414.md`（本前缀 **51** 条）。



- **2026-04-24 · 前缀 `docs/01_FRAMEWORK/LAYER4_ML`（门面批次）**：复跑 `scan_index_health.py --prefix docs/01_FRAMEWORK/LAYER4_ML --date 20260424` → `INDEX_HEALTH_ORPHAN_20260424.md`（**zero_inbound=0**；候选 md **40**；首轮 **`INDEX`/`README`** 零入链，已由 [`01_FRAMEWORK/INDEX.md`](../../../01_FRAMEWORK/INDEX.md) 显式链 `./LAYER4_ML/INDEX.md` 与 `./LAYER4_ML/README.md` 后归零）；[`LAYER4_ML/INDEX.md`](../../../01_FRAMEWORK/LAYER4_ML/INDEX.md) 增 P5 门面；体量 `REPO_DIRECTORY_ROLLUP_20260414.md`（本前缀 **40** 条）。



- **2026-04-25 · 前缀 `docs/06_ARCHIVE/20260407_old_layer_audit_reports`（归档 · 门面批次）**：复跑 `scan_index_health.py --prefix docs/06_ARCHIVE/20260407_old_layer_audit_reports --date 20260425` → `INDEX_HEALTH_ORPHAN_20260425.md`（**zero_inbound=0**；候选 md **40**；首轮 **8** 处子域 `INDEX` + `layer25` 单报告零入链，已由 [`20260407_old_layer_audit_reports/INDEX.md`](../../../06_ARCHIVE/20260407_old_layer_audit_reports/INDEX.md) 增「子目录索引」+ [`06_ARCHIVE/INDEX.md`](../../../06_ARCHIVE/INDEX.md) 表增门面行后归零）；体量 `REPO_DIRECTORY_ROLLUP_20260414.md`（本前缀 **40** 条）。



- **2026-04-26 · 前缀 `docs/09_AUDIT/STANDARDS`（门面批次）**：复跑 `scan_index_health.py --prefix docs/09_AUDIT/STANDARDS --date 20260426` → `INDEX_HEALTH_ORPHAN_20260426.md`（**zero_inbound=0**；候选 md **33**）；[`STANDARDS/INDEX.md`](../../../09_AUDIT/STANDARDS/INDEX.md) 增 P5 门面；[`09_AUDIT/INDEX.md`](../../../09_AUDIT/INDEX.md) 审计标准表显式链 `./STANDARDS/INDEX.md`；体量 `REPO_DIRECTORY_ROLLUP_20260414.md`（本前缀 **33** 条）。



- **2026-04-27 · 前缀 `docs/06_ARCHIVE/20260407_p1_cleanup_archive`（归档 · 门面批次）**：复跑 `scan_index_health.py --prefix docs/06_ARCHIVE/20260407_p1_cleanup_archive --date 20260427` → `INDEX_HEALTH_ORPHAN_20260427.md`（**zero_inbound=0**；候选 md **23**；首轮 **21** 处零入链，已由 [`20260407_p1_cleanup_archive/INDEX.md`](../../../06_ARCHIVE/20260407_p1_cleanup_archive/INDEX.md) 增「全量挂载」+ [`06_ARCHIVE/INDEX.md`](../../../06_ARCHIVE/INDEX.md) 表增门面行后归零；**不**做删并）；体量 `REPO_DIRECTORY_ROLLUP_20260414.md`（本前缀 **23** 条）。



- **2026-04-28 · 前缀 `docs/05_IMPLEMENTATION/02_DEVELOPMENT`（门面批次）**：复跑 `scan_index_health.py --prefix docs/05_IMPLEMENTATION/02_DEVELOPMENT --date 20260428` → `INDEX_HEALTH_ORPHAN_20260428.md`（**zero_inbound=0**；候选 md **21**；首轮 **`INDEX`/`README`** 零入链，已由 [`05_IMPLEMENTATION/INDEX.md`](../../INDEX.md) 显式链 `./02_DEVELOPMENT/INDEX.md` 与 `./02_DEVELOPMENT/README.md` 后归零）；[`02_DEVELOPMENT/INDEX.md`](../../02_DEVELOPMENT/INDEX.md) 增 P5 门面；体量 `REPO_DIRECTORY_ROLLUP_20260414.md`（本前缀 **21** 条）。



- **2026-04-29 · 前缀 `docs/05_IMPLEMENTATION/03_DEPLOYMENT`（门面批次）**：复跑 `scan_index_health.py --prefix docs/05_IMPLEMENTATION/03_DEPLOYMENT --date 20260429` → `INDEX_HEALTH_ORPHAN_20260429.md`（**zero_inbound=0**；候选 md **6**；首轮 **`INDEX`/`README`** 零入链，已由 [`05_IMPLEMENTATION/INDEX.md`](../../INDEX.md) 显式链 `./03_DEPLOYMENT/INDEX.md` 与 `./03_DEPLOYMENT/README.md` 后归零）；[`03_DEPLOYMENT/INDEX.md`](../../03_DEPLOYMENT/INDEX.md) 增 P5 门面与全量清单；体量 `REPO_DIRECTORY_ROLLUP_20260414.md`（本前缀 **6** 条）。



- **2026-04-30 · 前缀 `docs/05_IMPLEMENTATION/04_INFRASTRUCTURE`（门面批次）**：复跑 `scan_index_health.py --prefix docs/05_IMPLEMENTATION/04_INFRASTRUCTURE --date 20260430` → `INDEX_HEALTH_ORPHAN_20260430.md`（**zero_inbound=0**；候选 md **4**；首轮 **`INDEX`/`README`** 零入链，已由 [`05_IMPLEMENTATION/INDEX.md`](../../INDEX.md) 显式链 `./04_INFRASTRUCTURE/INDEX.md` 与 `./04_INFRASTRUCTURE/README.md` 等后归零）；[`04_INFRASTRUCTURE/INDEX.md`](../../04_INFRASTRUCTURE/INDEX.md) 增 P5 门面；体量 `REPO_DIRECTORY_ROLLUP_20260414.md`（本前缀 **4** 条）。



- **2026-05-01 · 前缀 `docs/05_IMPLEMENTATION/01_QUICKSTART`（门面批次）**：复跑 `scan_index_health.py --prefix docs/05_IMPLEMENTATION/01_QUICKSTART --date 20260501` → `INDEX_HEALTH_ORPHAN_20260501.md`（**zero_inbound=0**；候选 md **7**；首轮 **`INDEX.md`** 零入链，已由 [`05_IMPLEMENTATION/INDEX.md`](../../INDEX.md) 显式链 `./01_QUICKSTART/INDEX.md` 并扩严格孤儿挂载后归零）；[`01_QUICKSTART/INDEX.md`](../../01_QUICKSTART/INDEX.md) 重写为 P5 门面（本目录无 `README.md`，实施层索引误链已改）；体量 `REPO_DIRECTORY_ROLLUP_20260414.md`（本前缀 **7** 条）。



- **2026-05-02 · 前缀 `docs/05_IMPLEMENTATION/99_ARCHIVE`（门面批次）**：复跑 `scan_index_health.py --prefix docs/05_IMPLEMENTATION/99_ARCHIVE --date 20260502` → `INDEX_HEALTH_ORPHAN_20260502.md`（**zero_inbound=0**；候选 md **4**；首轮 **`INDEX.md`** 零入链，已由 [`05_IMPLEMENTATION/INDEX.md`](../../INDEX.md) 增 `99_ARCHIVE` 挂载后归零）；[`99_ARCHIVE/INDEX.md`](../../99_ARCHIVE/INDEX.md) 增 P5 门面；体量 `REPO_DIRECTORY_ROLLUP_20260414.md`（本前缀 **4** 条）。



- **2026-05-03 · 前缀 `docs/07_RESEARCH`（门面批次）**：复跑 `scan_index_health.py --prefix docs/07_RESEARCH --date 20260503` → `INDEX_HEALTH_ORPHAN_20260503.md`（**zero_inbound=0**；候选 md **18**；首轮 **9** 处子域门面 + 根 `INDEX` 零入链，已由 [`docs/INDEX.md`](../../../INDEX.md) 与本前缀 [`INDEX.md`](../../../07_RESEARCH/INDEX.md) 子域门面表补链后归零）；体量 `REPO_DIRECTORY_ROLLUP_20260414.md`（JSON 键 `docs/07_RESEARCH` **18** 条）。



- **2026-05-04 · 前缀 `docs/07_AI_REPORTING`（门面批次）**：复跑 `scan_index_health.py --prefix docs/07_AI_REPORTING --date 20260504` → `INDEX_HEALTH_ORPHAN_20260504.md`（**zero_inbound=0**；候选 md **2**；首轮 **`README.md`** 零入链，已由 [`docs/INDEX.md`](../../../INDEX.md) Layer 7 行与本前缀 [`INDEX.md`](../../../07_AI_REPORTING/INDEX.md) 链 `README` 后归零）；体量 `REPO_DIRECTORY_ROLLUP_20260414.md`（JSON 键 `docs/07_AI_REPORTING` **2** 条）。



- **2026-05-05 · 前缀 `docs/04_EXECUTION`（门面批次）**：复跑 `scan_index_health.py --prefix docs/04_EXECUTION --date 20260505` → `INDEX_HEALTH_ORPHAN_20260505.md`（**zero_inbound=0**；候选 md **30**；首轮 **10** 处子域 `INDEX`/`README` 零入链，已由 [`04_EXECUTION/INDEX.md`](../../../04_EXECUTION/INDEX.md) 子域门面表 + [`docs/INDEX.md`](../../../INDEX.md) Layer 5 补 `README` 后归零）；体量 `REPO_DIRECTORY_ROLLUP_20260414.md`（JSON 键 `docs/04_EXECUTION` **35** 条）。



- **2026-05-06 · 前缀 `docs/10_GOVERNANCE_COMPLIANCE`（门面批次）**：复跑 `scan_index_health.py --prefix docs/10_GOVERNANCE_COMPLIANCE --date 20260506` → `INDEX_HEALTH_ORPHAN_20260506.md`（**zero_inbound=0**；候选 md **21**；首轮 **6** 处子域门面零入链，已由 [`10_GOVERNANCE_COMPLIANCE/INDEX.md`](../../../10_GOVERNANCE_COMPLIANCE/INDEX.md) 子域门面表后归零）；体量 `REPO_DIRECTORY_ROLLUP_20260414.md`（JSON 键 `docs/10_GOVERNANCE_COMPLIANCE` **21** 条）。



- **2026-05-07 · 前缀 `docs/08_HUMAN_AI_INTERFACE`（门面批次）**：复跑 `scan_index_health.py --prefix docs/08_HUMAN_AI_INTERFACE --date 20260507` → `INDEX_HEALTH_ORPHAN_20260507.md`（**zero_inbound=0**；候选 md **107**；首轮 **39** 处原有模块子域门面零入链，已由 [`08_HUMAN_AI_INTERFACE/index.md`](../../../08_HUMAN_AI_INTERFACE/index.md) 门面表 + [`docs/INDEX.md`](../../../INDEX.md) Layer 8 链对齐 `index.md` 后归零）；体量 `REPO_DIRECTORY_ROLLUP_20260414.md`（JSON 键 `docs/08_HUMAN_AI_INTERFACE` **107** 条）。



- **2026-05-08 · 前缀 `docs/11_STRATEGIC_DECISION`（门面批次）**：复跑 `scan_index_health.py --prefix docs/11_STRATEGIC_DECISION --date 20260508` → `INDEX_HEALTH_ORPHAN_20260508.md`（**zero_inbound=0**；候选 md **51**；首轮 **5** 处子域 `INDEX.md` 零入链，已由 [`11_STRATEGIC_DECISION/INDEX.md`](../../../11_STRATEGIC_DECISION/INDEX.md) 子域索引表 + YAML 修复后归零）；体量 `REPO_DIRECTORY_ROLLUP_20260414.md`（JSON 键 `docs/11_STRATEGIC_DECISION` **51** 条）。



- **2026-05-09 · 前缀 `docs/09_RESEARCH_INNOVATION`（门面批次）**：复跑 `scan_index_health.py --prefix docs/09_RESEARCH_INNOVATION --date 20260509` → `INDEX_HEALTH_ORPHAN_20260509.md`（**zero_inbound=0**；候选 md **30**；首轮 **3** 处 `_archive/INDEX`、`maintenance_records/INDEX` 与 `README` 零入链，已由 [`09_RESEARCH_INNOVATION/INDEX.md`](../../../09_RESEARCH_INNOVATION/INDEX.md) 子域门面表后归零）；体量 `REPO_DIRECTORY_ROLLUP_20260414.md`（JSON 键 `docs/09_RESEARCH_INNOVATION` **48** 条）。



- **2026-05-10 · 前缀 `docs/10_AI_WORKFLOW`（门面批次）**：复跑 `scan_index_health.py --prefix docs/10_AI_WORKFLOW --date 20260510` → `INDEX_HEALTH_ORPHAN_20260510.md`（**zero_inbound=0**；候选 md **68**；首轮即零入链）；[`10_AI_WORKFLOW/INDEX.md`](../../../10_AI_WORKFLOW/INDEX.md) 增上级接力 + P5 门面；[`STATE/INDEX.md`](../../../09_AUDIT/STATE/INDEX.md) 产出表增本行；体量 `REPO_DIRECTORY_ROLLUP_20260414.md`（JSON 键 `docs/10_AI_WORKFLOW` **68** 条）。



- **2026-05-11 · 前缀 `docs/03_TRADING_TACTICS`（门面批次）**：复跑 `scan_index_health.py --prefix docs/03_TRADING_TACTICS --date 20260511` → `INDEX_HEALTH_ORPHAN_20260511.md`（**zero_inbound=0**；候选 md **56**；首轮 **8** 处子域 `INDEX`/`README` 零入链，已由 [`03_TRADING_TACTICS/INDEX.md`](../../../03_TRADING_TACTICS/INDEX.md) 子域总索引表补链后归零）；[`STATE/INDEX.md`](../../../09_AUDIT/STATE/INDEX.md) 产出表增本行；体量 `REPO_DIRECTORY_ROLLUP_20260414.md`（JSON 键 `docs/03_TRADING_TACTICS` **56** 条）。



- **2026-05-12 · 前缀 `docs/01_FRAMEWORK`（门面批次）**：复跑 `scan_index_health.py --prefix docs/01_FRAMEWORK --date 20260512` → `INDEX_HEALTH_ORPHAN_20260512.md`（**zero_inbound=0**；候选 md **336**；首轮 **3** 处子域门面零入链，已由 [`01_FRAMEWORK/INDEX.md`](../../../01_FRAMEWORK/INDEX.md) 子域门面链补后归零）；[`STATE/INDEX.md`](../../../09_AUDIT/STATE/INDEX.md) 产出表增本行；体量 `REPO_DIRECTORY_ROLLUP_20260414.md`（JSON 键 `docs/01_FRAMEWORK` **336** 条）。



- **2026-05-13 · 前缀 `docs/02_FACTOR_LIBRARY`（门面批次）**：复跑 `scan_index_health.py --prefix docs/02_FACTOR_LIBRARY --date 20260513` → `INDEX_HEALTH_ORPHAN_20260513.md`（**zero_inbound=0**；候选 md **142**；首轮 **`README.md`** 零入链，已由 [`02_FACTOR_LIBRARY/INDEX.md`](../../../02_FACTOR_LIBRARY/INDEX.md) 门面链与文档列表补链后归零）；[`STATE/INDEX.md`](../../../09_AUDIT/STATE/INDEX.md) 产出表增本行；体量 `REPO_DIRECTORY_ROLLUP_20260414.md`（JSON 键 `docs/02_FACTOR_LIBRARY` **144** 条）。



- **2026-05-14 · 前缀 `docs/00_OVERVIEW`（门面批次）**：复跑 `scan_index_health.py --prefix docs/00_OVERVIEW --date 20260514` → `INDEX_HEALTH_ORPHAN_20260514.md`（**zero_inbound=0**；候选 md **3**；首轮 **`README.md`** 零入链，已由 [`00_OVERVIEW/INDEX.md`](../../../00_OVERVIEW/INDEX.md) 门面链补入后归零）；[`STATE/INDEX.md`](../../../09_AUDIT/STATE/INDEX.md) 产出表增本行；体量 `REPO_DIRECTORY_ROLLUP_20260414.md`（JSON 键 `docs/00_OVERVIEW` **3** 条）。



- **2026-05-15 · 前缀 `docs/00_RESOURCES`（门面批次）**：复跑 `scan_index_health.py --prefix docs/00_RESOURCES --date 20260515` → `INDEX_HEALTH_ORPHAN_20260515.md`（**zero_inbound=0**；候选 md **4**；首轮 **4** 处门面零入链，已由 [`00_RESOURCES/INDEX.md`](../../../00_RESOURCES/INDEX.md) 子域链 + [`docs/INDEX.md`](../../../INDEX.md) 总入口补链后归零）；[`STATE/INDEX.md`](../../../09_AUDIT/STATE/INDEX.md) 产出表增本行；体量 `REPO_DIRECTORY_ROLLUP_20260414.md`（JSON 键 `docs/00_RESOURCES` **6** 条）。



- **2026-05-16 · 前缀 `docs/module_designs`（门面批次）**：复跑 `scan_index_health.py --prefix docs/module_designs --date 20260516` → `INDEX_HEALTH_ORPHAN_20260516.md`（**zero_inbound=0**；候选 md **2**；首轮即零入链）；[`module_designs/INDEX.md`](../../../module_designs/INDEX.md) 增 P5 门面；[`docs/INDEX.md`](../../../INDEX.md) 总入口增 `./module_designs/INDEX.md` 链；[`STATE/INDEX.md`](../../../09_AUDIT/STATE/INDEX.md) 产出表增本行；体量 `REPO_DIRECTORY_ROLLUP_20260414.md`（JSON 键 `docs/module_designs` **2** 条）。



- **2026-05-17 · 前缀 `docs/09_AUDIT/PROCEDURES`（门面批次）**：复跑 `scan_index_health.py --prefix docs/09_AUDIT/PROCEDURES --date 20260517` → `INDEX_HEALTH_ORPHAN_20260517.md`（**zero_inbound=0**；候选 md **10**；首轮即零入链）；[`09_AUDIT/PROCEDURES/INDEX.md`](../../../09_AUDIT/PROCEDURES/INDEX.md) 增上级接力 + P5；[`STATE/INDEX.md`](../../../09_AUDIT/STATE/INDEX.md) 产出表增本行；体量 `REPO_DIRECTORY_ROLLUP_20260414.md`（JSON 键 `docs/09_AUDIT/PROCEDURES` **10** 条）。



- **2026-05-18 · 前缀 `docs/09_AUDIT/TEMPLATES`（门面批次）**：复跑 `scan_index_health.py --prefix docs/09_AUDIT/TEMPLATES --date 20260518` → `INDEX_HEALTH_ORPHAN_20260518.md`（**zero_inbound=0**；候选 md **16**；首轮 **`TEMPLATES/INDEX.md`** 零入链，已由 [`09_AUDIT/INDEX.md`](../../../09_AUDIT/INDEX.md) 审计模板表补 `./TEMPLATES/INDEX.md` + [`TEMPLATES/INDEX.md`](../../../09_AUDIT/TEMPLATES/INDEX.md) P5 后归零）；[`STATE/INDEX.md`](../../../09_AUDIT/STATE/INDEX.md) 产出表增本行；体量 `REPO_DIRECTORY_ROLLUP_20260414.md`（JSON 键 `docs/09_AUDIT/TEMPLATES` **16** 条）。



- **2026-05-19 · 前缀 `docs/09_AUDIT/AUTOMATION`（门面批次）**：复跑 `scan_index_health.py --prefix docs/09_AUDIT/AUTOMATION --date 20260519` → `INDEX_HEALTH_ORPHAN_20260519.md`（**zero_inbound=0**；候选 md **3**；首轮 **`INDEX`/`README`** 零入链，已由 [`09_AUDIT/INDEX.md`](../../../09_AUDIT/INDEX.md) Playbook 补链 + [`AUTOMATION/INDEX.md`](../../../09_AUDIT/AUTOMATION/INDEX.md) 门面后归零）；[`STATE/INDEX.md`](../../../09_AUDIT/STATE/INDEX.md) 产出表增本行；体量 `REPO_DIRECTORY_ROLLUP_20260414.md`（JSON 键 `docs/09_AUDIT/AUTOMATION` **6** 条）。



- **2026-05-20 · 前缀 `docs/09_AUDIT/GUIDES`（门面批次）**：复跑 `scan_index_health.py --prefix docs/09_AUDIT/GUIDES --date 20260520` → `INDEX_HEALTH_ORPHAN_20260520.md`（**zero_inbound=0**；候选 md **4**；首轮 **`GUIDES/INDEX.md`** 零入链，已由 [`09_AUDIT/INDEX.md`](../../../09_AUDIT/INDEX.md) 显式链 `./GUIDES/INDEX.md` + [`GUIDES/INDEX.md`](../../../09_AUDIT/GUIDES/INDEX.md) P5 与 YAML 修正后归零）；[`STATE/INDEX.md`](../../../09_AUDIT/STATE/INDEX.md) 产出表增本行；体量 `REPO_DIRECTORY_ROLLUP_20260414.md`（JSON 键 `docs/09_AUDIT/GUIDES` **4** 条）。



- **2026-05-21 · 前缀 `docs/09_AUDIT/CONFIG`（门面批次）**：复跑 `scan_index_health.py --prefix docs/09_AUDIT/CONFIG --date 20260521` → `INDEX_HEALTH_ORPHAN_20260521.md`（**zero_inbound=0**；候选 md **6**；首轮 **`CONFIG/INDEX.md`** 零入链，已由 [`09_AUDIT/INDEX.md`](../../../09_AUDIT/INDEX.md) Playbook 与子目录表链 `./CONFIG/INDEX.md` + [`CONFIG/INDEX.md`](../../../09_AUDIT/CONFIG/INDEX.md) P5 门面后归零）；[`STATE/INDEX.md`](../../../09_AUDIT/STATE/INDEX.md) 产出表增本行；体量 `REPO_DIRECTORY_ROLLUP_20260414.md`（JSON 键 `docs/09_AUDIT/CONFIG` **6** 条）。







```
```---
```







## 5. 版本记录







| 版本 | 日期 | 说明 |



|------|------|------|



| 1.4.72 | 2026-04-11 | **§1.2** 末增「ignore 与 `STATE/` 两条线」块quote；**§7.2** 末增 Solo+AI 与 §0.1.4 互指；§3.4.1 / §8 AI 交接行同步 **§0.1.4 / §0.2** |

| 1.4.73 | 2026-04-13 | 批量修正错误占位链接（`10_GOVERNANCE_COMPLIANCE/...`、`12_MODULE_DESIGNS/...`）为仓库内真实相对路径；C2 长段中 `06_ARCHIVE/*` 与 `audit_state` 等链接可点击 |

| 1.4.70 | 2026-04-11 | 新增 **§1.2**（Markdown 编码/乱码预防，与 L1 正交）；文首块互指 §1.2；**§2.3** 表「内链/verify」改为**推荐**复跑口径并互指 AI 交接 **§0.1.2**；§8 AI 交接自查条含 **§0.1** / **§1.2** |



| 1.4.69 | 2026-04-11 | 增 **§3.4.1** D 类方案文件索引（办公室互指）；文首与 **§3.4** 对齐 **§2.5** 置信度；**§7** 跨会话说明去「当前指针」依赖；**§7.2** L1 为推荐+默认目标；§8 办公室自查条同步 D 类 |



| 1.4.68 | 2026-04-11 | **P5 §7 子批**：`docs/09_AUDIT/CONFIG` — `INDEX_HEALTH_20260521`（CONFIG/INDEX → 0）；`09_AUDIT/INDEX` + `CONFIG/INDEX` |



| 1.4.67 | 2026-04-11 | **P5 §7 子批**：`docs/09_AUDIT/GUIDES` — `INDEX_HEALTH_20260520`（GUIDES/INDEX → 0）；`09_AUDIT/INDEX` + `GUIDES/INDEX` |



| 1.4.66 | 2026-04-11 | **P5 §7 子批**：`docs/09_AUDIT/AUTOMATION` — `INDEX_HEALTH_20260519`（首轮 2 → 0）；`09_AUDIT/INDEX` + `AUTOMATION/INDEX` |



| 1.4.65 | 2026-04-11 | **P5 §7 子批**：`docs/09_AUDIT/TEMPLATES` — `INDEX_HEALTH_20260518`（INDEX 零入链 → 0）；`09_AUDIT/INDEX` + `TEMPLATES/INDEX` |



| 1.4.64 | 2026-04-11 | **P5 §7 子批**：`docs/09_AUDIT/PROCEDURES` — `INDEX_HEALTH_20260517`（零入链 0）；`PROCEDURES/INDEX` P5 门面 |



| 1.4.63 | 2026-04-11 | **P5 §7 子批**：`docs/module_designs` — `INDEX_HEALTH_20260516`（零入链 0）；`module_designs/INDEX` P5 + `docs/INDEX` 链 |



| 1.4.62 | 2026-04-11 | **P5 §7 子批**：`docs/00_RESOURCES` — `INDEX_HEALTH_20260515`（首轮 4 → 0）；`00_RESOURCES/INDEX` + `docs/INDEX` 总入口 |



| 1.4.61 | 2026-04-11 | **P5 §7 子批**：`docs/00_OVERVIEW` — `INDEX_HEALTH_20260514`（README 零入链 → 0）；`00_OVERVIEW/INDEX` P5 门面 |



| 1.4.60 | 2026-04-11 | **P5 §7 子批**：`docs/02_FACTOR_LIBRARY` — `INDEX_HEALTH_20260513`（README 零入链 → 0）；`02_FACTOR_LIBRARY/INDEX` P5 + 文档列表 |



| 1.4.59 | 2026-04-11 | **P5 §7 子批**：`docs/01_FRAMEWORK` — `INDEX_HEALTH_20260512`（首轮 3 → 零入链 0）；`01_FRAMEWORK/INDEX` 子域门面 + P5 |



| 1.4.58 | 2026-04-11 | **P5 §7 子批**：`docs/03_TRADING_TACTICS` — `INDEX_HEALTH_20260511`（首轮 8 → 零入链 0）；`03_TRADING_TACTICS/INDEX` 子域表 + P5 |



| 1.4.57 | 2026-04-11 | **P5 §7 子批**：`docs/10_AI_WORKFLOW` — `INDEX_HEALTH_20260510`（零入链 0）；`10_AI_WORKFLOW/INDEX` P5 门面 + `STATE/INDEX` 产出表 |



| 1.4.56 | 2026-04-11 | **P5 §7 子批**：`docs/09_RESEARCH_INNOVATION` — `INDEX_HEALTH_20260509`（零入链 0）；`09_RESEARCH_INNOVATION/INDEX` 子域门面 + P5 |



| 1.4.55 | 2026-04-11 | **P5 §7 子批**：`docs/11_STRATEGIC_DECISION` — `INDEX_HEALTH_20260508`（零入链 0）；`11_STRATEGIC_DECISION/INDEX` 子域索引表 + YAML |



| 1.4.54 | 2026-04-11 | **P5 §7 子批**：`docs/08_HUMAN_AI_INTERFACE` — `INDEX_HEALTH_20260507`（零入链 0）；`index` 门面表 01–39；`docs/INDEX` Layer 8 链 `index.md` |



| 1.4.53 | 2026-04-11 | **P5 §7 子批**：`docs/10_GOVERNANCE_COMPLIANCE` — `INDEX_HEALTH_20260506`（零入链 0）；`10_GOVERNANCE_COMPLIANCE/INDEX` 子域门面 + P5 |



| 1.4.52 | 2026-04-11 | **P5 §7 子批**：`docs/04_EXECUTION` — `INDEX_HEALTH_20260505`（零入链 0）；`docs/INDEX` Layer 5 补 README；`04_EXECUTION/INDEX` 子域门面表 |



| 1.4.51 | 2026-04-11 | **P5 §7 子批**：`docs/07_AI_REPORTING` — `INDEX_HEALTH_20260504`（零入链 0）；`docs/INDEX` Layer 7 补 README；`07_AI_REPORTING/INDEX` P5 门面 |



| 1.4.50 | 2026-04-11 | **P5 §7 子批**：`docs/07_RESEARCH` — `INDEX_HEALTH_20260503`（零入链 0）；`docs/INDEX` 研究支持入口；`07_RESEARCH/INDEX` 子域门面 + P5 |



| 1.4.49 | 2026-04-11 | **P5 §7 子批**：`docs/05_IMPLEMENTATION/99_ARCHIVE` — `INDEX_HEALTH_20260502`（零入链 0）；`05_IMPLEMENTATION/INDEX` 挂载实施层归档；`99_ARCHIVE/INDEX` P5 门面 |



| 1.4.48 | 2026-04-11 | **P5 §7 子批**：`docs/05_IMPLEMENTATION/01_QUICKSTART` — `INDEX_HEALTH_20260501`（零入链 0）；`05_IMPLEMENTATION/INDEX` 链快速开始总索引 + 全量挂载；`01_QUICKSTART/INDEX` 门面重写 |



| 1.4.47 | 2026-04-11 | **P5 §7 子批**：`docs/05_IMPLEMENTATION/04_INFRASTRUCTURE` — `INDEX_HEALTH_20260430`（零入链 0）；`05_IMPLEMENTATION/INDEX` 链基础设施总索引 + README 等；`04_INFRASTRUCTURE/INDEX` P5 门面 |



| 1.4.46 | 2026-04-11 | **P5 §7 子批**：`docs/05_IMPLEMENTATION/03_DEPLOYMENT` — `INDEX_HEALTH_20260429`（零入链 0）；`05_IMPLEMENTATION/INDEX` 链部署总索引 + README；`03_DEPLOYMENT/INDEX` P5 门面与清单 |



| 1.4.45 | 2026-04-11 | **P5 §7 子批**：`docs/05_IMPLEMENTATION/02_DEVELOPMENT` — `INDEX_HEALTH_20260428`（零入链 0）；`05_IMPLEMENTATION/INDEX` 链开发总索引 + README；`02_DEVELOPMENT/INDEX` P5 门面 |



| 1.4.44 | 2026-04-11 | **P5 §7 子批**：`docs/06_ARCHIVE/20260407_p1_cleanup_archive` — `INDEX_HEALTH_20260427`（零入链 0）；归档 `INDEX` 全量挂载 + `06_ARCHIVE/INDEX` 门面 |



| 1.4.43 | 2026-04-11 | **P5 §7 子批**：`docs/09_AUDIT/STANDARDS` — `INDEX_HEALTH_20260426`（零入链 0）；`STANDARDS/INDEX` P5 门面 + `09_AUDIT/INDEX` 链标准总索引 |



| 1.4.42 | 2026-04-11 | **P5 §7 子批**：`docs/06_ARCHIVE/20260407_old_layer_audit_reports` — `INDEX_HEALTH_20260425`（零入链 0）；归档根 `INDEX` 子目录链 + `06_ARCHIVE/INDEX` 门面 |



| 1.4.41 | 2026-04-11 | **P5 §7 子批**：`docs/01_FRAMEWORK/LAYER4_ML` — `INDEX_HEALTH_20260424`（零入链 0）；`01_FRAMEWORK/INDEX` 链 L4 总索引 + README；`LAYER4_ML/INDEX` P5 门面 |



| 1.4.40 | 2026-04-11 | **P5 §7 子批**：`docs/06_ARCHIVE/20260408_double_yaml_dryrun_sample` — `INDEX_HEALTH_20260423`（零入链 0）；dry-run `README` P5 门面 + `06_ARCHIVE/INDEX` 表增行 |



| 1.4.39 | 2026-04-11 | **P5 §7 子批**：`docs/09_ARCHIVE/duplicates` — `INDEX_HEALTH_20260422`（零入链 0）；`duplicates/INDEX` 全量挂载 + `09_ARCHIVE/INDEX` 门面 |



| 1.4.38 | 2026-04-11 | **P5 §7 子批**：`docs/05_IMPLEMENTATION/07_OPERATIONS` — `INDEX_HEALTH_20260421`（零入链 0）；`07_OPERATIONS/INDEX` 补子域入口 + `05_IMPLEMENTATION/INDEX` 链至运维总索引 |



| 1.4.37 | 2026-04-11 | **P5 §7 子批**：`docs/02_FACTOR_LIBRARY/04_DATA_SOURCE` — `INDEX_HEALTH_20260420`（零入链 0）；数据源 `INDEX` 门面 + `02_FACTOR_LIBRARY/INDEX` 显式入口 |



| 1.4.36 | 2026-04-19 | **P5 §7 子批**：`docs/05_IMPLEMENTATION/05_TECHNICAL_SPECIFICATIONS` — `INDEX_HEALTH_20260419`（零入链 0）；`05_IMPLEMENTATION/INDEX` 链至技术规格 `INDEX.md` |



| 1.4.35 | 2026-04-18 | **P5 §7 子批**：`docs/06_ARCHIVE/20260404_audit_reports_archive` + `scan_index_health` archive 子前缀行为；`INDEX_HEALTH_20260418`（零入链 0）；归档根/子 `INDEX` 补链 |



| 1.4.34 | 2026-04-17 | **P5 §7 子批**：`docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS` — `INDEX_HEALTH_20260417`（零入链 0）；补 `REPORTS/README`、`05_DESIGN_DOCS/INDEX` 入链；门面 README/INDEX + `STATE/INDEX` 产出表 |



| 1.4.33 | 2026-04-16 | **§2.3.2** 新增「位置是否正确」判准互文（↔ 放置规程 **§1.6**）；§2.3 总表「文档地图与放置」行补 **§1.6** |



| 1.4.32 | 2026-04-16 | **P5 §7 子批**：`docs/09_AUDIT/STATE` — `INDEX_HEALTH_20260416`（零入链 0）；`09_AUDIT/INDEX`、`REPORTS/INDEX` 与 `STATE/INDEX` 互指最新快照 |



| 1.4.31 | 2026-04-15 | **P5 §7 子批**：`docs/05_IMPLEMENTATION/04_OPERATIONS` — `INDEX_HEALTH_20260415`（零入链 0）；门面 README/INDEX 与 `STATE/INDEX` 表对齐 `rollup_20260414` 体量 |



| 1.4.30 | 2026-04-14 | **P5 §7 子批**：`docs/09_AUDIT/REPORTS` 门面 — `INDEX_HEALTH_20260414`（零入链 0）+ `rollup_20260414`；修正 `STATE/INDEX` 表内 REPORTS/04_OPERATIONS 健全性行混排；P5 总勾未替代 |



| 1.4.29 | 2026-04-11 | 移除根目录 `AGENTS.md`、`.cursor/rules/zephyr-governance-agent.mdc` 等「长程接力」附件；§7.1 去掉第 0 步；办公室 README / GLOBAL 阶段 C 恢复三步口径 |



| 1.4.28 | 2026-04-12 | 废止独立「运行队列」文件；§7.1 曾增第 0 步（接力口径，见 1.4.29 撤回附件后收敛） |



| 1.4.27 | 2026-04-11 | §7.1 曾互指运行队列（已废止，见 1.4.28） |



| 1.4.26 | 2026-04-11 | 治理脚本统一 `quotePath=false` + UTF-8；刷新 `REPO_DIRECTORY_ROLLUP_20260411`、`REPO_GIT_TRACKED_FILES_20260411`；§1/§6/§7/§8 与 `GIT_TRACKED_PATH_ANOMALIES` 改写为「显示转义 ≠ 索引损坏」 |



| 1.4.25 | 2026-04-11 | §1 澄清「8+8」为同一批 8 条 Git 异常路径；§6 链 `GIT_TRACKED_PATH_ANOMALIES_20260411`；与 STATE 索引整仓产出表互指 |



| 1.4.24 | 2026-04-11 | P3：勾选「抽样反向检查」并链 `DOCS_NAV_COVERAGE_SAMPLE_20260410`；§6 推荐阅读增主导航抽样与 `W2_SECRET_PATTERN_SPOTCHECK`；P4.1 矩阵增 `sample_docs_nav_coverage.py`；§8「§1 数字」与当前 `git ls-files` 4454 对齐勾选 |



| 1.4.22 | 2026-04-10 | P2：50×`.diff` 迁 `06_ARCHIVE/20260408_double_yaml_dryrun_sample`；`System_Manifest.md.bak3` 迁 archive；程序文档改 dry-run 路径；P1 Playbook 流程对齐勾选；P3：`scripts/README` 分类导航 + `src/README`；P4.1 门禁矩阵；§8 部分勾选；复跑 `rollup` + `REPO_GIT_TRACKED_FILES_20260410.txt` |



| 1.4.21 | 2026-04-10 | D 类：`triage_blueprint_d_overlap_pairs.py` + TRIAGE / SECOND_PASS_QUEUE / 二审模板 写入文首、§1.1、§3.4～§3.6、§6 推荐阅读 |



| 1.4.20 | 2026-04-10 | L1：落地 `backfill_missing_module_id.py`，全库首道 FM **无 `module_id` → 0**（131 篇：结构修复 15 + 补 id 116）；`sentinel_l1_governance_scan.py` 产出 MD 增 FM + 统计排除自指；`scan_blueprint_d_overlap_candidates.py` 产出 MD 增稳定 `module_id`；复跑 L1 **判定无效 0、重复 id 0** |



| 1.4.19 | 2026-04-12 | D 类：复跑 `scan_blueprint_d_overlap_candidates.py` → `BLUEPRINT_D_OVERLAP_CANDIDATES_20260412`；§3.6 D 附机器基线数字；§6 推荐阅读主链改 20260412 并保留 20260411 快照 |



| 1.4.18 | 2026-04-11 | L1：消解首道 `module_id` 跨文件重复 2 组（`README`×2、`INDEX`×2）→ `DOCS_01_FRAMEWORK_README_001` 等；复跑 **重复 id 数 0** |



| 1.4.17 | 2026-04-11 | L1：`sentinel_l1_governance_scan.py` 复跑 **判定无效 0**（修 D 类登记表示例链、归档稿相对链、`BLUEPRINT_VALIDATION_REPORT` 中 `STRATEGY_ENGINE` 指向图纸柜） |



| 1.4.16 | 2026-04-11 | §3.6 **C2 勾选完成**（非导航 basename 0；导航名多份并存不强制）；P1 basename 行与 C2 验收口径互指 |



| 1.4.15 | 2026-04-11 | §3.6 C2 第三十七～四十一簇：`overnight_runs` 三稿带 run_id、`ARCHIVE_README` 四处消歧、因子库 `OVERVIEW`→`FACTOR_LIB_*_OVERVIEW`；C2 非导航 basename **0**；`overnight_audit_runner.py` 输出命名对齐 |



| 1.4.14 | 2026-04-11 | §3.6 C2 第三十～三十六簇：`duplicates` 因子三稿 + ALPHA 轮次2 + `DOCUMENT_CREATION_CHECKLIST` 归档 + `DOCUMENT_GOVERNANCE` 归档 basename + `IMPLEMENTATION_OPERATIONS_FAQ`；basename 报表 **9 / 非导航 5** |



| 1.4.13 | 2026-04-10 | §3.6 C2 第二十六～二十九簇：`p1` 审计报告双份归档 + `DEEP_AUDIT_REPORT_V3` Layer8 重命名 + `INDEX_GROUPED` REPORTS/STATE 分文件 |



| 1.4.12 | 2026-04-10 | §3.6 C2 第二十二～二十五簇：三份 `audit_state` 与 REPORTS 撞名异文重命名 + `DOCUMENT_METADATA_TEMPLATE`（STANDARD canonical，`p1` 归档） |



| 1.4.11 | 2026-04-10 | §3.6 C2 第十八～二十一簇：三份 `audit_state` vs `p1_cleanup_archive` 报告 + `SHORT_TERM_IMPROVEMENT_COMPLETION_REPORT`（REPORTS canonical，`STATE` 归档，`INDEX_GROUPED` 修链） |



| 1.4.10 | 2026-04-10 | §3.6 C2 第十六、十七簇：`STRATEGY_ENGINE_BLUEPRINT` + `STRATEGY_SELECTION_BLUEPRINT`（`01_BLUEPRINTS` canonical + `03_TRADING_TACTICS` tactics entry + archive） |



| 1.4.9 | 2026-04-10 | §3.6 C2 第十五簇：`REALTIME_RISK_MONITORING_BLUEPRINT`（`01_FRAMEWORK` canonical + Layer8 `64_` stub + archive） |



| 1.4.8 | 2026-04-10 | §3.6 C2 第十三、十四簇：`MODEL_PERFORMANCE_VERSION_MANAGEMENT_BLUEPRINT` + `RESEARCH_WORKFLOW_MANAGEMENT_BLUEPRINT`（`10_AI_WORKFLOW` canonical，迁出 `p1_cleanup_archive` 副本） |



| 1.4.7 | 2026-04-10 | §3.6 C2 第十二簇：`DATA_VERSION_CONTROL_BLUEPRINT`（`01_BLUEPRINTS` canonical + `LAYER4_ML` entry + 迁出 `p1_cleanup_archive` 副本） |



| 1.4.6 | 2026-04-10 | §3.6 C2 第十一簇：`PERFORMANCE_ATTRIBUTION_BLUEPRINT`（`11_STRATEGIC_DECISION` canonical + Layer8 `83_` stub + archive） |



| 1.4.5 | 2026-04-10 | §3.6 C2 第十簇：`MARKET_REGIME_DETECTION_BLUEPRINT`（`01_BLUEPRINTS` canonical + `10_AI_WORKFLOW` entry + archive） |



| 1.4.4 | 2026-04-10 | §3.6 C2 第九簇：`MODEL_RISK_MANAGEMENT_BLUEPRINT`（`01_FRAMEWORK` canonical + Layer8 `77_` stub + archive） |



| 1.4.3 | 2026-04-10 | §3.6 C2 第八簇：`STRATEGY_LIFECYCLE_MANAGEMENT_BLUEPRINT`（`10_AI_WORKFLOW` canonical + Layer8 `81_` stub + 迁出 `p1_cleanup_archive` 副本） |



| 1.4.2 | 2026-04-10 | §3.6 C2 第七簇：`TRANSACTION_COST_ANALYSIS_BLUEPRINT`（`10_AI_WORKFLOW` canonical + 框架 entry + Layer8 `79_` stub + archive） |



| 1.4.1 | 2026-04-10 | 文首与 §8 自查对齐 LAYOUT **§1 第 5 条**；禁平行 Layer 放置真源 |



| 1.4.0 | 2026-04-10 | 文首与 **§2.3.1** 固化「Layer 0～11 vs `docs/` 路径」防混；§6 / §7.2 / §8 与 放置规程 §1.5、AI 交接 §3.2 互指 |



| 1.3.9 | 2026-04-10 | §3.6 C2 第六簇：`FULL_PROCESS_DATA_PERSISTENCE_BLUEPRINT`（`10_AI_WORKFLOW` canonical + `LAYER4_ML` `FULL_PROCESS_DATA_LAYER4_ENTRY` + archive） |



| 1.3.8 | 2026-04-10 | §3.6 C2 第五簇：`COMPLIANCE_MONITORING_BLUEPRINT`（`10_AI_WORKFLOW` canonical + Layer8 `COMPLIANCE_MONITORING_LAYER8_MODULE`） |



| 1.3.7 | 2026-04-10 | §3.6 C2 第四簇：`BENCHMARK_MANAGEMENT_BLUEPRINT`（图纸柜 + `BENCHMARK_MANAGEMENT_STRATEGIC_ENTRY` + archive） |



| 1.3.6 | 2026-04-10 | §3.6 C2 第三簇：`DISASTER_RECOVERY_BLUEPRINT`（图纸柜 canonical + `DISASTER_RECOVERY_FRAMEWORK_ENTRY` + archive） |



| 1.3.5 | 2026-04-10 | §3.6 C2 记录第二簇消解：`API_GATEWAY_BLUEPRINT`（图纸柜 canonical + Layer8 `API_GATEWAY_LAYER8_MODULE`） |



| 1.3.4 | 2026-04-10 | D 类 **低置信**合稿互指 D_CLASS_CONSOLIDATION_PENDING_REVIEW_REGISTER；§3.4 / §3.5 D′ / §6 / §8 |



| 1.3.3 | 2026-04-11 | D 类流水线：`scan_blueprint_d_overlap_candidates.py` + D_CLASS_BLUEPRINT_OVERLAP_PLAYBOOK；§1.1 / §3.4 / §3.5 / §6 互指 |



| 1.3.2 | 2026-04-11 | C2 推进：`DATA_QUALITY_MONITORING_BLUEPRINT` 同名簇消解 + 归档 README；分散蓝图清单重生成；§3.6 C2 附进展 |



| 1.3.1 | 2026-04-11 | 新增 `scan_basename_collisions.py`；P1 basename 报表 ✅；§1.1 / 文首互指；§3.6 C2 附报表链接 |



| 1.3.0 | 2026-04-11 | §3.1 **宽松**归档裁定；§3.6 归档策略 + C1（temp_pending 五簇）；P0 基线复跑约定闭环 |



| 1.2.9 | 2026-04-10 | §6 推荐阅读增 全局文件治理会话交接 |



| 1.2.8 | 2026-04-10 | 落地 **`scan_index_health.py`**；§1.1 表与结论、§6 推荐阅读增 `INDEX_HEALTH_ORPHAN_*` |



| 1.2.7 | 2026-04-10 | §1.1 **结论** 增「索引健全性」边界：L1/verify 能做什么；搬迁后索引同步与可选孤儿报表互指 文档地图与放置规则 **§4～§5** |



| 1.2.6 | 2026-04-10 | 纳入 **文档地图 + 放置规则**：文首与 §6 互指；§2.3 增「文档地图与放置」行；§7.2 增 **摆放** 退出项；§8 办公室自查增 DOCUMENT_MAP_AND_PLACEMENT_GOVERNANCE 与 AI 交接 **①‴** |



| 1.2.5 | 2026-04-10 | 治理脚本归口 `scripts/governance/`；`rollup`/`scan_duplicate` 支持 `--include-untracked`；互指 删稿裁决 Playbook；§1.1 与 §2.3 命令路径更新 |



| 1.2.4 | 2026-04-10 | **P1** 落地 `scan_duplicate_file_content.py`；§2.3 增内容重复与工具索引；互指 治理工具总索引；§1.1 表更新 |



| 1.2.3 | 2026-04-10 | 新增 **§1.1** 扫描覆盖/格式边界（Git vs L1、全格式语义不承诺）；**§8** 增自查项；**P4** 矩阵与 §1.1 对齐 |



| 1.2.2 | 2026-04-10 | **§2.4** 增架构服务目录生成物说明；§2.3 增 C4/服务目录行；**P4** 勾选 `ARCHITECTURE_SERVICE_CATALOG_*`；§6 增入口；根目录补 **LICENSE / CONTRIBUTING / SECURITY** |



| 1.2.1 | 2026-04-10 | 新增 **§2.4** 架构模块全景与机构做法；§2.3 增「模块全景」行；**P4** 可选全景脚本；文首互指 §2.4 |



| 1.2.0 | 2026-04-10 | **§2.3** 可并行工作总表；**§7** 深度目录队列与退出标准；**§8** 办公室二次自查；**P5**；rollup 脚本与 `REPO_DIRECTORY_ROLLUP_20260410.*`；§1 明确深度 2 不足尽治 |



| 1.1.0 | 2026-04-10 | 新增 **§3 合并重复文件方案**（分型、C1/C2/D 流程、并行线程、§3.6 勾选）；P1 互指 §3 |



| 1.0.0 | 2026-04-10 | 首版：基线统计、口径、P0～P4 波次；附全量路径导出文件 |







```
```---
```







## 6. 推荐阅读入口







| 说明 | 路径 |



|------|------|



| 全量已跟踪路径清单（UTF-8 · `quotePath=false`） | [`REPO_GIT_TRACKED_FILES_20260411.txt`](../../../09_AUDIT/STATE/REPO_GIT_TRACKED_FILES_20260411.txt) · 历史 [`20260410`](../../../09_AUDIT/STATE/REPO_GIT_TRACKED_FILES_20260410.txt) |



| 目录深度聚合（3～6） | `REPO_DIRECTORY_ROLLUP_20260411.md` / [`.json`](../../../09_AUDIT/STATE/REPO_DIRECTORY_ROLLUP_20260411.json) · 历史 `20260410` |



| 架构服务目录 + C4 摘要（生成） | `ARCHITECTURE_SERVICE_CATALOG_20260410.md` / [`.json`](../../../09_AUDIT/STATE/ARCHITECTURE_SERVICE_CATALOG_20260410.json) |



| 内容重复（SHA256 · 后缀白名单） | `DUPLICATE_CONTENT_BY_HASH_20260411.md` / [`.json`](../../../09_AUDIT/STATE/DUPLICATE_CONTENT_BY_HASH_20260411.json) |



| 同名不同路径（basename · C2 · `scan_basename_collisions.py`） | `BASENAME_COLLISIONS_20260411.md` / [`.json`](../../../09_AUDIT/STATE/BASENAME_COLLISIONS_20260411.json) |



| 蓝图 D 类重叠候选（启发式 · `scan_blueprint_d_overlap_candidates.py`） | `BLUEPRINT_D_OVERLAP_CANDIDATES_20260412.md` / [`.json`](../../../09_AUDIT/STATE/BLUEPRINT_D_OVERLAP_CANDIDATES_20260412.json) · 历史快照 `20260411` · Playbook · **低置信合稿台账** D_CLASS_CONSOLIDATION_PENDING_REVIEW_REGISTER |



| 蓝图 D 类 A 档分流 + 二审队列（`triage_blueprint_d_overlap_pairs.py`） | `BLUEPRINT_D_OVERLAP_TRIAGE_20260412.md` / [`.json`](../../../09_AUDIT/STATE/BLUEPRINT_D_OVERLAP_TRIAGE_20260412.json) · [`BLUEPRINT_D_OVERLAP_SECOND_PASS_QUEUE_20260412.jsonl`](../../../09_AUDIT/STATE/BLUEPRINT_D_OVERLAP_SECOND_PASS_QUEUE_20260412.jsonl) · 二审提示词模板 |



| 索引健全性（零入链候选 · `scan_index_health.py`） | `INDEX_HEALTH_ORPHAN_20260410.md` / [`.json`](../../../09_AUDIT/STATE/INDEX_HEALTH_ORPHAN_20260410.json) |



| P3 主导航覆盖率抽样（`sample_docs_nav_coverage.py` · 样例） | `DOCS_NAV_COVERAGE_SAMPLE_20260410.md` |



| W2 可选密钥型字面量抽查（Python 模式 · 等价抽检记录） | `W2_SECRET_PATTERN_SPOTCHECK_20260410.md`（与 蓝图任务清单 W2 互指） |



| Git 路径 quotePath / 显示转义澄清（**非**索引损坏） | `GIT_TRACKED_PATH_ANOMALIES_20260411.md` · [STATE 索引汇总表](../../../09_AUDIT/STATE/INDEX.md) |



| 治理工具总索引（办公室） | GOVERNANCE_TOOLS_INDEX.md |



| 全局文件治理会话交接（新对话粘贴） | GLOBAL_FILE_GOVERNANCE_SESSION_HANDOFF.md |



| 文档地图与放置（办公室规程 · 与扫描/§7 衔接） | DOCUMENT_MAP_AND_PLACEMENT_GOVERNANCE.md（**§1.5** Layer 与路径防混） |



| `docs/` 目录职责与阶段落盘（标准真源） | `DOCUMENT_REPOSITORY_LAYOUT_STANDARD.md` |



| 技术栈分层 Layer 0～11（与目录名分立） | [`ARCHITECTURE.md`](../../../01_FRAMEWORK/ARCHITECTURE.md) · 办公室 AI 交接 §3.2 |



| 叙事层模块/总账入口（与 §2.4 生成物互补） | `docs/System_Manifest.md`、[`docs/SITEMAP.md`](../../../SITEMAP.md)、[`docs/module_designs/INDEX.md`](../../../module_designs/INDEX.md) |



| 蓝图阶段任务（并列） | BLUEPRINT_PHASE_CLOSURE_TASK_LIST.md |



| 孤儿与重复治理 | DOC_ORPHAN_AND_DUPLICATE_GOVERNANCE_PLAYBOOK.md |



| 双 YAML dry-run 历史样本（50×`.diff`，已迁出 STATE） | [`../../../06_ARCHIVE/20260408_double_yaml_dryrun_sample/README.md`](../../../06_ARCHIVE/20260408_double_yaml_dryrun_sample/README.md) |







```
```---
```







## 7. 一次性深度治理：目录队列与退出标准







> **目的**：把「整仓一次弄干净」落实为**可打勾的目录前缀队列**，避免只盯着深度 2 的粗桶。队列来源：`REPO_DIRECTORY_ROLLUP_*.json`（全量前缀）+ MD 中 Top 表（优先啃大块）。  



> **跨会话衔接**：以 **本文件 §7 勾选 + commit/PR 说明** 记录进度即可；**不**再维护独立的「当前指针」类接力附件（历史版本记录中如提及「运行队列」仅作沿革说明）。







### 7.1 怎么从「最深」起排







1. 打开 `REPO_DIRECTORY_ROLLUP_20260411.md` 中 **深度 5、6** 表，找出仍很大的子树；再回退到深度 3～4 看其父链是否整枝可一起收口。



2. 对 **`docs/09_AUDIT/REPORTS`、`docs/09_AUDIT/STATE`** 等超高计数前缀：在批次内再按**子文件夹**细分为子队列（rollup 深度加一或手工列目录）。  



3. **`docs/06_ARCHIVE/**`**：默认 **只读治理**（摆放、索引、与活动区重复标注），删并须符合 **§3.1 归档区策略**。  



4. **`scripts/`、`src/`、`notebooks/`**：以「入口可读 + 重复脚本/模块报表」为主，不单套用文档 C1 流程；**`src/` 或 API 变更**后复跑 `generate_architecture_service_catalog.py` 刷新服务目录。







### 7.2 单个目录前缀（或子队列）「退出标准」勾选模板







Owner 对每个待收口前缀打勾（可复制到 PR 描述或台账）：







- [ ] **重复**：该前缀下 **C1** 已按 §3.2 处理或确认无组；**C2** 已报表且无未决高优先级碰撞；**D 类**已登记或已裁决。  



- [ ] **摆放**：本批新增或错放文件已按 LAYOUT 标准（及 办公室放置规程，含 **Layer 与路径分立 §1.5**）归到约定目录，或已在 PR 中登记**例外理由**与复审方式；动 `01_BLUEPRINTS` 时尚须符合 图纸柜规则。  



- [ ] **导航**：父级或本级具备 **INDEX / README / 上级入口** 之一（归档区至少 **archive 内 INDEX** 或父级说明）。  



- [ ] **内链**：本批次改动涉及路径**推荐**复跑 **L1**；全库 **无效内链 = 0** 为默认目标或已登记 Owner 书面例外。  



- [ ] **衍生物**：按 P2 策略无应迁走的 `.diff`/`.bak`（或已归档）。  



- [ ] **路径健全**：平面清单/rollup 使用 `quotePath=false` 或 `-z` 导出；无**真实**错误路径（默认可读 `git ls-files` 的引号显示**不算**索引损坏，见 §1 与 `GIT_TRACKED_PATH_ANOMALIES`）。  



- [ ] **证据**：rollup 重跑已提交或报告路径可指认。







### 7.3 §7 总勾选（尽治里程碑）







- [ ] 已对 **`docs/`** 下深度 3 Top 前缀（或 JSON 中全部超过阈值的前缀）**逐一**达到 §7.2 或登记**书面例外**（含例外原因与复审日）。  



- [ ] `scripts/`、`src/` 已按 P3 + §2.3 达到「可查入口」标准。  



- [ ] 大批次结束后已 **重跑 rollup** 并 commit，便于与上一版 JSON diff。







```
```---
```







## 8. 办公室与本文档的二次自查（优化循环）







大改办公室或本清单后，维护者快速过一遍：







- [x] [办公室 README](./README.md)：**治理流程编号**仍覆盖蓝图、孤儿/重复、扩展轨、根卫生、**整仓文件尽治**、**文档地图与放置**；**办公室文件一览**表与磁盘一致（含 **D 类** Playbook / 二审模板 / **待审登记** / `triage_blueprint_d_overlap_pairs.py` 及 **§3.4.1** 互指）；治理工具总索引 与 `scripts/` 实际脚本同步；文档地图与放置规程 **§1.5** 与 LAYOUT 标准 **§1 第 5 条**互指无断链、无第二套 Layer 放置真源。（2026-04-10 批次核对；2026-04-11 增补 D 类 §3.4.1 与 §2.5 口径。）  



- [x] AI 交接说明：阅读顺序与**常见任务**含「深度尽治 / rollup / 本清单 §7」、文档地图与放置规则（①‴，**§1.5**）与 LAYOUT 真源优先级；**§0.1**（Git 暂存、L1 时机、UTF-8/防乱码）、**§0.1.4**（ignore 与 `STATE/` 两条线）、**§0.2**（Solo+全委托 AI）与本文 **§1.2** 末段、**§7.2** 末、编码标准互指；**§3.2**（Layer 0～11 vs 路径）与 放置规程 §1.5、本文 **§2.3.1** 三处表述一致。（2026-04-10 批次核对；2026-04-11 起 §0.1.4 / §0.2 / §7.2 末对齐。）  



- [x] [scripts/README.md](../../../../scripts/README.md)：治理相关脚本表含 **rollup**、`generate_architecture_service_catalog` 与既有 `verify_*` / `sentinel_l1`；若已落地 **§2.4** `MODULE_PANORAMA_*` 脚本，表中已登记。（2026-04-10：`scan_basename_collisions`、分类导航已补；`MODULE_PANORAMA_*` 仍未落地 — 表中无该项为预期。）  



- [x] 本文件 **§1 数字**（文件总数等）与 `git ls-files` / 最新 rollup **无矛盾**（或已注明「快照日期」）。（2026-04-11：**已跟踪文件总数** `git -c core.quotePath=false ls-files` = **4459**，与 §1 表及 `REPO_DIRECTORY_ROLLUP_20260411` 头部 **4459** 一致；深度 3 Top6 已与 **20260411** rollup 对齐；`review_materials_package` 引号显示问题已澄清为 **CLI quotePath**，见 `GIT_TRACKED_PATH_ANOMALIES_20260411`。）  



- [x] 与 蓝图任务清单 **无冲突表述**（并列、互补、W 轨 ≠ 尽治）。（2026-04-10 批次核对。）  



- [x] **§1.1** 已与 `scripts/` 内实际行为一致；对外未再暗示「全格式、全文件语义扫描」。（2026-04-10：与 **P4.1** 矩阵一致。）











### P6 — 文件夹结构与命名合规性（结构治理）







> **专业机构顺序**：在 **P0～P5**（基础 + 内容治理 + 深度尽治）完成后，执行结构治理。先确保内容稳定，再调整结构，避免重复搬迁。



> **与 §1.6 分桶表的关系**：P6 聚焦 **A（物理树职责）**、**B（Layer 与路径分立）**、**C（文件名）** 三个分桶。



> **推荐插件**：**File System**（目录遍历）、**Qdrant**（搜索标准）、**SequentialThinking**（分析合规性）、**Knowledge Graph**（记录关系）。







- [x] **P6.1 目录命名合规性扫描**：检查是否有中文目录名、空格、特殊字符；对照 PATH_STANDARD.md §1.1（编号前缀、英文命名、禁止中文和空格）。



- [x] **P6.2 编号前缀一致性检查**：检查 `docs/` 下目录是否使用 2 位数字前缀（`00_`、`01_` 等）；例外须在 LAYOUT 标准 §6 登记。



- [x] **P6.3 目录放置位置验证**：对照 LAYOUT 标准 §2～§4，检查文件夹是否在正确位置；错位者按 文档地图与放置规则 §3 步骤搬迁。



- [x] **P6.4 新目录登记验证**：检查新目录是否已在 LAYOUT 标准 §6 或 `TECH_DECISION_RECORDS` 登记；未登记者补登记或裁决删除。



- [x] **P6.5 INDEX/README 存在性检查**：检查主要目录是否有 `INDEX.md` / `README.md`；缺失者按 P5 门面批次模式补充。



- [x] **P6.6 归档目录关系梳理**：梳理 `docs/06_ARCHIVE/` 与 `docs/09_ARCHIVE/` 的关系，明确职责边界；在 LAYOUT 标准 §6 或本文件备注中记录结论。



- [x] **P6.7 研究目录关系梳理**：梳理 `docs/07_RESEARCH/` 与 `docs/09_RESEARCH_INNOVATION/` 的关系，明确职责边界；同上记录结论。







**P6 执行备忘（证据链）**







- **2026-04-11 · P6.1 目录命名合规性扫描**：运行 `python scripts/governance/scan_directory_naming_compliance.py --date 20260411 --prefix docs/` → `DIRECTORY_NAMING_COMPLIANCE_20260411.md`：**总目录 313**；包含中文 **0**；包含空格 **0**；包含特殊字符 **0**；缺少编号前缀 **145**（需人工裁决是否为例外）；合规 **168**。







### P7 — 施工门禁验收（达成蓝图终稿交付标准）



> **专业机构顺序**：在 **P0～P6**（基础 + 内容治理 + 深度尽治 + 结构治理）完成后，执行施工门禁验收，确保达成蓝图终稿交付标准。



> **与施工门禁的关系**：本节为 施工门禁 **§0.1a** 和 **§3** 的验收勾选，两者互指。



> **与蓝图交付标准的关系**：本节对应 蓝图交付标准（机构精华版） **§4 自检清单** 的执行验收。



> **推荐插件**：**File System**（验证脚本存在）、**Qdrant**（搜索相关文档）、**SequentialThinking**（分析验收结果）、**Knowledge Graph**（记录契约关系）。







#### P7.1 §0.1a 文档放置与目录标准



- [x] **P7.1.1** `DOCUMENT_REPOSITORY_LAYOUT_STANDARD` 已阅读并确认无与 Owner 意图冲突（冲突则改标准或登记豁免）。



- [x] **P7.1.2** `03_CONSTRUCTION_PLANS/` 已存在且含 `INDEX.md`（可与蓝图终稿并行创建）。



- [x] **P7.1.3** 蓝图终稿范围内各篇路径与链接符合 LAYOUT 表（或已在篇内说明例外理由）。







#### P7.2 §3 A 元数据风险验收



- [x] **P7.2.1 (A1)** 当前仓库 L1：Markdown 内链判定无效 = 0（报告已存档）。



- [x] **P7.2.2 (A2)** 双 YAML：`merge_double_yaml_frontmatter.py --list` → 0，或仅剩 `DOUBLE_YAML_EXCEPTIONS.md` 登记豁免。



- [x] **P7.2.3 (A3)** 首道 FM 重复 `module_id` 组 = 0（与 L1 / `dedupe_module_id_frontmatter.py` 口径一致）。



- [x] **P7.2.4 (A4)** `audit_state` 仅 `04_OPERATIONS/audit_state` 为权威工作区；`07_.../audit_state` 仅为跳转说明。







#### P7.3 §3 B 架构/模块审核验收



- [x] **P7.3.1 (B1)** `ARCH_MODULE_GAP_REGISTER_20260408.md` 内登记项均为已修正或已 defer 并注明理由。



- [x] **P7.3.2 (B2)** Layer 11：`LAYER11_CAPABILITY_TO_BLUEPRINT_MAP_20260408.md` 与 `ARCHITECTURE.md` Layer 11 表一致且无 TBD。



- [x] **P7.3.3 (B3)** `01_BLUEPRINTS` 全量对账：`generate_01_blueprints_index.py` 产物与目录一致，且与 `BLUEPRINT_ARCHITECTURE_MAPPING.md` 无未解释的孤儿挂载。



- [x] **P7.3.4 (B4)** `docs/module_designs/` 已与选定垂直切片绑定并完成阶段 1 对照审（未绑定则本项记「N/A」须 Owner 签字）。







#### P7.4 §3 C 审计阶段 A～H 验收



- [x] **P7.4.1 (C1)** 阶段 A（入口与架构真源 A1–A4）已完成。



- [x] **P7.4.2 (C2)** 阶段 B（实施与施工 B1–B6）已完成。



- [x] **P7.4.3 (C3)** 阶段 C（审计体系 C1–C4）已完成。



- [x] **P7.4.4 (C4)** 阶段 D（因子库与数据）已完成。



- [x] **P7.4.5 (C5)** 阶段 E（执行、战术、战略、研究）已完成。



- [x] **P7.4.6 (C6)** 阶段 F（人机、AI 工作流、合规）已完成。



- [x] **P7.4.7 (C7)** 阶段 G（归档与历史）已完成。



- [x] **P7.4.8 (C8)** 阶段 H（其他 docs 与仓库外 md）已完成。



- [x] **P7.4.9 (C9)** 阶段 I（Git 误删与备份价值审计）— 可选。







#### P7.5 §3 D 归档与历史验收



- [x] **P7.5.1 (D1)** `docs/06_ARCHIVE/` 根散落约 236 篇已分主题子目录或已登记分期计划与完成日期。



- [x] **P7.5.2 (D2)** `docs/09_ARCHIVE/duplicates` 与 `06_ARCHIVE` 交叉引用或合并策略已写清并落实索引。



- [x] **P7.5.3 (D3)** `docs/09_AUDIT/REPORTS/` 版本链收敛（保留现行入口 + 归档旧版）。



- [x] **P7.5.4 (D4)** 缺失 `module_id` 的文档已逐批补全或已登记「非标准文档」豁免集合。



- [x] **P7.5.5 (D5)** `review_materials_package` 内链与不参与内链检查的说明已落地。



- [x] **P7.5.6 (D6)** 全库检索旧 Layer8 / 旧文件名链接，历史报告内按需修正或标注「历史引用」。







#### P7.6 §3 E 技术审批验收



- [x] **P7.6.1 (E1)** 拟施工涉及的公共接口 / 数据契约已在 `API_Contract.md` 或子契约中有条目，且 `TECH_DECISION_RECORDS.md` 中有对应 TDR/ADR 或明确「沿用既有决策」的引用。



- [x] **P7.6.2 (E2)** pre-commit：按 ADR-OC-004，已安排修钩子或收窄规则的跟踪项（不要求整改期内一次解决，但施工前须有结论或豁免）。







#### P7.7 §3 F P2 Backlog 验收



- [x] **P7.7.1 (F1)** P2（Backlog）已执行完毕或 Owner 在施工门禁 §4 声明「P2 不阻塞施工」并注明复审频率。







#### P7.8 卫生总案退出标准验收



- [x] **P7.8.1** 主干 INDEX：P0 目录均已挂接 Playbook 所述入口或专项目录索引。



- [x] **P7.8.2** L1：默认分支 Invalid links = 0。



- [x] **P7.8.3** duplicates：`CANONICAL_POINTERS.md` 无悬空 TBD（或已全部指派）。



- [x] **P7.8.4** overlap：`overlap_*` 无「裸奔」缺指针（或已登记豁免）。



- [x] **P7.8.5** 孤儿趋势：重跑 `REGEN` 清单较基线明显减少。







**P7 执行备忘（证据链）**







- **2026-04-11 · P7.2.2 (A2) 双 YAML 修复**：运行 `python scripts/merge_double_yaml_frontmatter.py --apply` → 14 个双 YAML 文件已合并为 0。



- **2026-04-11 · P7.2.1 (A1) L1 验证**：`sentinel_l1_governance_scan.py` → 无效内链 = 0 ✅。



- **2026-04-11 · P7.2.3 (A3) module_id 验证**：`dedupe_module_id_frontmatter.py --dry-run` → 重复组数 = 0 ✅。



- **2026-04-11 · P7.3.1 (B1) GAP_REGISTER 验证**：G-001～G-016 全部状态为「已修正」✅。



- **2026-04-11 · P7.3.2 (B2) Layer11 映射验证**：22/22 行已链到蓝图，TBD = 0 ✅。



- **2026-04-11 · P7.3.3 (B3) 蓝图全量对账**：`verify_01_blueprints_index_links.py` → valid 164, missing 0 ✅；`verify_manifest_paths_strict.py` → unique 29, missing 0 ✅。



- **2026-04-11 · P7.1.2 03_CONSTRUCTION_PLANS 验证**：目录存在 + `INDEX.md` 存在 ✅。



- **2026-04-11 · P7.3.4 (B4) Owner 签字**：`module_designs` 当前阶段无垂直切片绑定需求，记 **N/A** — **Owner 签字：2026-04-11**。



- **2026-04-11 · P7.4 (C1-C9) Owner 签字**：审计阶段 A～H 验收 **通过** — **Owner 签字:2026-04-11**。



- **2026-04-11 · P7.5 (D1-D6) Owner 签字**：归档与历史验收 **通过** — **Owner 签字:2026-04-11**。



- **2026-04-11 · P7.6 (E1-E2) Owner 签字**：技术审批验收 **通过** — **Owner 签字:2026-04-11**。



- **2026-04-11 · P7.7 (F1) Owner 签字**：P2 Backlog **不阻塞施工**（复审频率：每季度） — **Owner 签字:2026-04-11**。



- **2026-04-11 · P6.2 Owner 签字**：缺少编号前缀的 145 个目录中，65 个归档目录为合理例外，80 个当前命名可接受 — **Owner 签字:2026-04-11**。



- **2026-04-12 · P7.6 (E1-E2) 编码修复**：`API_Contract.md` 和 `TECH_DECISION_RECORDS.md` 从 git 原始提交恢复正确中文，修复双 YAML + 乱码问题；L1=0, 双YAML=0 ✅。







```
```---
```







## 5. 版本记录



| 版本 | 日期 | 说明 |



|------|------|------|



| 1.4.75 | 2026-04-12 | **编码修复**：从 git 历史恢复正确 UTF-8 内容（原文件 1885 处编码损坏）；P7.7 (F1) 补充复审频率（每季度）；P6.2 签字数字修正（65 归档例外 + 80 可接受）；P7.6 (E1-E2) 编码修复记录 |



| 1.4.74 | 2026-04-11 | **新增 P7（施工门禁验收）**：按专业机构顺序，在 P0～P6 后执行施工门禁验收，确保达成蓝图终稿交付标准；含 P7.1～P7.8 八项勾选；互指施工门禁 §0.1a 和 §3、蓝图交付标准 §4 自检清单；推荐插件：File System、Qdrant、SequentialThinking、Knowledge Graph |



| 1.4.73 | 2026-04-11 | **新增 P6（文件夹结构与命名合规性）**：按专业机构顺序，在 P0～P5 后执行结构治理；含 P6.1～P6.7 七项勾选；互指 PATH_STANDARD、LAYOUT 标准、文档地图与放置规则；推荐插件：File System、Qdrant、SequentialThinking、Knowledge Graph |



| 1.4.70 | 2026-04-11 | **§1.2** 末增「ignore 与 `STATE/` 两条线」blockquote；**§7.2** 末增 Solo+AI 与 §0.1.4 互指；§2.4.1 / §8 AI 交接行同步 **§0.1.4 / §0.2** |



