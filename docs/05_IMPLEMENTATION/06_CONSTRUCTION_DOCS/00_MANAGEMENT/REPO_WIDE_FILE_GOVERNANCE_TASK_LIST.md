---
module_id: REPO_WIDE_FILE_GOVERNANCE_TASK_LIST_001
version: 1.2.8
status: Active
created_date: 2026-04-10
last_updated: '2026-04-10'
owner: 文档负责人（可指定）
responsibility:
  - 全仓库已跟踪文件的清点、去重与索引可达性（与蓝图任务清单并列，不限于蓝图目录）
standard_type: 任务清单
applicable_scope: 本 Git 仓库；以 `git ls-files` 为权威清单来源
---

# 全仓库文件治理 — 任务清单（总图）

> **用途**：回答「是否要先扫全树再建任务清单」——**要先有基线清单与统计，再分波次治理**；本文件给出**口径、基线数字、可勾选波次**，避免无控制面的大扫除。  
> **与蓝图清单的关系**：与 [全库蓝图终稿任务清单](./BLUEPRINT_PHASE_CLOSURE_TASK_LIST.md) **并列**；蓝图清单偏**终稿与施工门禁**，本清单偏**整仓文件体量、重复与导航**。扩展轨 **W0～W4 勾选完毕 ≠ 本清单「目录尽治」完毕**（二者互补，见蓝图清单扩展轨节互指）。  
> **一次性尽治目标**：以**单批次最大穷尽**为排期目标——按 **§7** 对 `docs/` 等前缀拆队列、逐前缀打到退出标准；客观上规范与仓库仍会演进，**长期靠门禁脚本 + 定期重跑 §1 清单/rollup** 维持，避免「无标准的第二轮大扫除」。  
> **权威 Playbook**：[孤儿与重复文档治理](./../../../09_AUDIT/STANDARDS/DOC_ORPHAN_AND_DUPLICATE_GOVERNANCE_PLAYBOOK.md)、[仓库根治理](./REPO_ROOT_GOVERNANCE_PLAYBOOK.md)、[文件删除与保留裁决](./FILE_DELETION_OR_RETENTION_PLAYBOOK.md)。  
> **架构模块全景（多级子模块）**：是否需要、与机构习惯对照、能否随扫描更新——见 **§2.4**。  
> **架构/服务目录 + C4 摘要（生成物）**：[`ARCHITECTURE_SERVICE_CATALOG_*`](../../../09_AUDIT/STATE/ARCHITECTURE_SERVICE_CATALOG_20260410.md)（脚本 `scripts/governance/generate_architecture_service_catalog.py`）。  
> **扫描是否覆盖「每一种文件格式、每一文件的语义分析与自动处理」？** **否**——见 **§1.1**（分工具、分口径；Git 已跟踪 vs 工作区 Markdown 亦有差异）。  
> **内容重复（按后缀白名单）**：`scripts/governance/scan_duplicate_file_content.py`（**必须** `--ext`，默认 `md`）→ `DUPLICATE_CONTENT_BY_HASH_*`；治理工具总表见 [治理工具总索引](./GOVERNANCE_TOOLS_INDEX.md)。  
> **文档地图 + 放置规则（机构习惯）**：目录职责与阶段落盘的 **真源** 为 [`DOCUMENT_REPOSITORY_LAYOUT_STANDARD.md`](../../../09_AUDIT/STANDARDS/DOCUMENT_REPOSITORY_LAYOUT_STANDARD.md)；与扫描/§7 批次的 **衔接步骤** 见办公室规程 [文档地图与放置规则](./DOCUMENT_MAP_AND_PLACEMENT_GOVERNANCE.md)。

---

## 0. 是否要先做「全系统树状」扫描？

**需要。** 推荐顺序为：

1. **基线快照**：导出当前 **Git 已跟踪**路径全表（与协作真源一致）+ 按目录/扩展名聚合统计。  
2. **口径冻结**：定义何为「多余」、何为「重复」、何为「已索引」。  
3. **分波次执行**：先门禁与明显垃圾，再内容哈希重复，最后语义/功能重复（需 Owner 裁决）。

> **说明**：若「整个系统」指 **本机磁盘或操作系统级**，已超出单仓库职责，需在备份与合规策略下**另立项目**；本清单**默认仅覆盖本仓库**。

---

## 1. 基线快照（2026-04-10，可复跑更新）

| 指标 | 数值 | 备注 |
|------|------|------|
| **已跟踪文件总数** | **4384**（2026-04-10 复跑 rollup） | `git ls-files` 行数；以后以最新 rollup / 平面清单为准 |
| **Markdown** | 3176 | 体量最大，索引策略必须分层，避免「逐文件手打链接」 |
| **Python** | 736 | 含 `scripts/` 为主 |
| **JSON** | 314 | 含审计状态、配置片段等 |
| **`.diff` 跟踪文件** | 50 | 适合统一归档/剔除策略评审 |
| **`.bak2` / `.bak3` 等备份扩展名（已跟踪）** | 至少 2 | 见下文 P2，宜迁出主树或进 archive |
| **一级目录体量（已跟踪）** | `docs/` 3523，`scripts/` 670，`src/` 65 | 治理重心在 `docs/` 与 `scripts/` |

**深度 2 目录聚合（节选，文件数 Top — 仅作一级排期摘要）**

| 前缀 | 约文件数 |
|------|-----------|
| `docs/09_AUDIT` | 1012 |
| `docs/05_IMPLEMENTATION` | 880 |
| `docs/06_ARCHIVE` | 644 |
| `docs/01_FRAMEWORK` | 338 |
| `docs/02_FACTOR_LIBRARY` | 144 |
| `docs/08_HUMAN_AI_INTERFACE` | 107 |

> **不足以支撑「一次尽治到最深」**：深度 2 会把 `docs/09_AUDIT` 等上千文件**糊成一桶**；**必须**配合下方 **深度 3～6 聚合**按子前缀拆队列（见 `REPO_DIRECTORY_ROLLUP_*`）。

**深度 3～6 目录聚合（机器生成，支撑拆队列）**

| 产出 | 路径 |
|------|------|
| 人类可读摘要（`docs/` 下各深度 Top 表 + 说明） | [`docs/09_AUDIT/STATE/REPO_DIRECTORY_ROLLUP_20260410.md`](../../../09_AUDIT/STATE/REPO_DIRECTORY_ROLLUP_20260410.md) |
| 全量前缀计数（JSON，可按任意前缀筛选） | [`docs/09_AUDIT/STATE/REPO_DIRECTORY_ROLLUP_20260410.json`](../../../09_AUDIT/STATE/REPO_DIRECTORY_ROLLUP_20260410.json) |

**复跑（仓库根）**：`python scripts/governance/export_repo_directory_rollup.py`（可选 `--date YYYYMMDD`、`--top N`、`--include-untracked` 把工作区未跟踪且未被 ignore 的路径并入聚合）。大治理批次完成后应 **commit 更新后的 rollup**，便于 diff「哪些前缀已清空」。

**全量路径平面清单（可检索、可 diff）**  
路径：`docs/09_AUDIT/STATE/REPO_GIT_TRACKED_FILES_20260410.txt`  

> **注意**：若清单中出现带引号或 `\346` 这类八进制转义片段，通常表示 **Git 索引里记录了异常/转义形式的路径**（与正常 UTF-8 中文路径并存时尤需警惕）；处置见 **P2** 路径规范化。

**复跑导出命令（仓库根，PowerShell）**

```powershell
# 推荐用 Python 导出 UTF-8，避免 PowerShell 对部分路径的转义差异：
python -c "import subprocess; p=subprocess.check_output(['git','ls-files'],text=True); lines=sorted(p.splitlines()); open(r'docs/09_AUDIT/STATE/REPO_GIT_TRACKED_FILES_YYYYMMDD.txt','w',encoding='utf-8',newline='\n').write('\n'.join(lines)+'\n')"
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
| **`scripts/governance/scan_duplicate_file_content.py`** | 默认 **Git 已跟踪** + `--ext` 白名单；可选 `--include-untracked` | 内容 **SHA256**，`members[].git_source` 区分 tracked/untracked | **不**自动删；合并走 **§3** C1 + [删稿裁决 Playbook](./FILE_DELETION_OR_RETENTION_PLAYBOOK.md)；大文件可用 `--max-mb` 跳过 |
| **`scripts/governance/scan_index_health.py`** | 默认 **`docs/`** 下已跟踪 `.md`（可 `--prefix`）；入链来源默认**全库已跟踪** `.md` | 统计 **Markdown 相对链**入链，报告 **零入链** 候选 | **不**解析 HTML/代码块链接；**不**判定「必须出现在某 INDEX」（见 [放置规程](./DOCUMENT_MAP_AND_PLACEMENT_GOVERNANCE.md) **§5.3**）；**不**自动删稿 |
| **被忽略路径** | `.gitignore` 等 | 本清单**默认不**纳入「删并」 | 本地密钥、缓存、`.env.qmt` 等由安全与 ignore 策略管 |

**结论（回答「是否涵盖所有格式、是否每一文件都识别分析处理」）**：

- **「涵盖」**：在 **路径级**，`git ls-files` 已覆盖**所有已跟踪**路径（任意后缀）；§1 的扩展名统计可列出当前仓库**已出现**的后缀类型。  
- **「每一文件识别/分析/处理」**：**没有**。当前自动化主要是 **Markdown 链接 + module_id**、**目录计数**、**API 路由抽取**、**特定清单校验**、**零入链报表（`scan_index_health.py`）**；**语义理解、业务裁决、二进制内容治理**需 **人工 + 分格式专项**（或未来单独立项脚本）。  
- **验收建议**：大治理收口时声明以 **「已跟踪 + L1 + verify + rollup」** 为门禁组合；若要求「仅扫描入库文件」，应 **先 `git status` 清干净**或接受 L1 与 `git ls-files` 的已知差异。  
- **索引「是否够健全」**：**L1** 校验相对链**能否解析**；**`scan_index_health.py`** 产出 **`docs/` 下零入链候选**（见 [放置规程](./DOCUMENT_MAP_AND_PLACEMENT_GOVERNANCE.md) **§5.2**），**不**等价于「必须在某 INDEX 出现」；域级 INDEX **覆盖规则**仍属 **§5.3** / 待规则冻结。搬迁后入链/机器清单见同文 **§4**。

---

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
- **L3**：[`docs/SITEMAP.md`](../../../SITEMAP.md)、[`docs/System_Manifest.md`](../../../System_Manifest.md) 等**总账类**文档（职责以各文件前言为准）。  
- **L4（推荐）**：对 `scripts/`、`tools/` 等增加**生成型清单**（脚本扫描目录 → Markdown/JSON），与手写 INDEX **互补**。

### 2.3 与「扫描 / 合并」可同时推进的工作（总表）

下列工作与 **§3 合并**、**§7 目录队列** **正交或弱依赖**，适合同一治理窗口内并行安排（多 PR 亦可），避免干等报表：

| 工作项 | 典型产出 / 命令 | 与合并的关系 |
|--------|-------------------|----------------|
| **内链健康** | `python scripts/governance/sentinel_l1_governance_scan.py`；修无效相对路径 | 合并后必跑；也可边合并边修触达文件 |
| **蓝图 / 分散清单 / 总清单校验** | `scripts/governance/verify_01_blueprints_index_links.py`、`scripts/governance/verify_scattered_blueprints_manifest_links.py`、`scripts/governance/verify_manifest_paths_strict.py` | 合并改路径后必跑 |
| **图纸柜 INDEX** | `python scripts/governance/generate_01_blueprints_index.py` | 动 `01_BLUEPRINTS` 后跑 |
| **`.diff` / `.bak*` 策略** | 归档、剔除跟踪或迁 `archive`（见 P2） | 减少合并噪声与误报重复 |
| **异常路径 / 索引污染** | `review_materials_package` 等引号路径规范化（P2） | 合并前优先，否则链接与 hash 对不齐 |
| **孤儿与重复程序** | [孤儿与重复 Playbook](../../../09_AUDIT/STANDARDS/DOC_ORPHAN_AND_DUPLICATE_GOVERNANCE_PLAYBOOK.md)、[CANONICAL_POINTERS](../../../09_ARCHIVE/duplicates/CANONICAL_POINTERS.md) | D 类与 C2 必用；C1 合并后更新台账 |
| **受控正式稿登记** | [CONTROLLED_DOCUMENTS_REGISTER.md](./CONTROLLED_DOCUMENTS_REGISTER.md) | canonical 变更时同步 |
| **仓库根 / 脚本门面** | [REPO_ROOT_GOVERNANCE_PLAYBOOK.md](./REPO_ROOT_GOVERNANCE_PLAYBOOK.md)、根 `README.md`、`scripts/README.md` | 与文档合并并行，可单独 PR |
| **密钥与忽略** | `.gitignore`、（可选）秘密扫描 | 任意时刻可做；合并批次不阻塞 |
| **卫生总案批次** | [蓝图卫生总案](./CANON/BLUEPRINT_PHASE_DOCUMENT_HYGIENE_MASTER_PLAN_20260408.md) P0～P3 | 与「删重复」互补，先定摆放再并 |
| **TODO/TBD 台账** | [`TODO_CLEANUP_INVENTORY`](../../../09_AUDIT/REPORTS/TODO_CLEANUP_INVENTORY_20260406.md) 等 | 占位清理与合并可同窗 |
| **全系统文档审计 A～H** | [审计方案](../../../09_AUDIT/PROCEDURES/FULL_SYSTEM_DOCUMENT_AUDIT_PLAN_20260408.md) | 与尽治同窗但**签字口径独立** |
| **代码重复 / 重构** | 单立 PR + 测试 | **不**与文档合并混批（见 §3.1） |
| **模块全景（逻辑树）** | §2.4；将来 `MODULE_PANORAMA_*` 与 rollup **同频**重跑 | 包名/域改名后重跑，避免索引漂移 |
| **架构服务目录 + C4 多视图** | `python scripts/governance/generate_architecture_service_catalog.py` → `ARCHITECTURE_SERVICE_CATALOG_*` | 改 `src/api`、契约路径或根目录机构文件后重跑；JSON 可检索 |
| **内容重复（后缀白名单）** | `python scripts/governance/scan_duplicate_file_content.py --ext md`（可加 `yaml` 等） | 产出 `DUPLICATE_CONTENT_BY_HASH_*`；**须**人工按 §3 合并 | 默认不扫无扩展名/二进制；大文件见 `--max-mb` |
| **文档地图与放置** | [文档地图与放置规则](./DOCUMENT_MAP_AND_PLACEMENT_GOVERNANCE.md) + [LAYOUT 标准](../../../09_AUDIT/STANDARDS/DOCUMENT_REPOSITORY_LAYOUT_STANDARD.md) + [图纸柜规则](./01_BLUEPRINTS_REPOSITORY_RULES.md) | 搬迁/新建目录前**先查格**；大批归位与 **§7** 同窗 | 新类型目录须先改 LAYOUT §6 或决策记录（见规程 §1） |
| **索引健全性（零入链）** | `python scripts/governance/scan_index_health.py`（可加 `--prefix` 等） | 产出 `INDEX_HEALTH_ORPHAN_*`；与 **L1** 互补 | 不判定域 INDEX 必列；见 [放置规程](./DOCUMENT_MAP_AND_PLACEMENT_GOVERNANCE.md) **§5.2～§5.3** |
| **治理工具归口** | 办公室 [治理工具总索引](./GOVERNANCE_TOOLS_INDEX.md) | 一键查命令与产出 | 实现在 `scripts/governance/`；根目录同名 `.py` 为兼容转发 |

**办公室内规章与上表对齐**：各文件职责与「可并入本窗」的动作见 [项目办公室 README](./README.md) **「办公室内文件一览」**。

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
4. **与叙事真源的关系**：[`docs/System_Manifest.md`](../../../System_Manifest.md)、[`docs/SITEMAP.md`](../../../SITEMAP.md)、[`docs/module_designs/INDEX.md`](../../../module_designs/INDEX.md) 等继续承担**解释与裁决**；生成物标注 **generated**，避免「两份真源」静默分叉。  

5. **已落地的机构式组合（本仓库）**：`scripts/governance/generate_architecture_service_catalog.py` 从 **`pyproject.toml`、`git ls-files src/`、`src/api/main.py`、各 `routes/*.py`** 推导 **Context / Containers / Components（HTTP 端点）**、**service_catalog** 与 **根目录机构缺口自检表**，输出 [`ARCHITECTURE_SERVICE_CATALOG_*.md/json`](../../../09_AUDIT/STATE/ARCHITECTURE_SERVICE_CATALOG_20260410.md)；与 **rollup**、以及将来可选的 **`MODULE_PANORAMA_*`** 产物**同频**复跑即可持续刷新。

---

## 3. 合并重复文件方案（执行规程）

> **与 §2.1 的对应关系**：本节把 **C（内容重复）**、**basename 碰撞**、**D（功能重复）** 的处置写成**可执行步骤**；**权威流程与叙事归并**仍以 [孤儿与重复 Playbook](../../../09_AUDIT/STANDARDS/DOC_ORPHAN_AND_DUPLICATE_GOVERNANCE_PLAYBOOK.md) 为准，**canonical 台账**可同步 [CANONICAL_POINTERS.md](../../../09_ARCHIVE/duplicates/CANONICAL_POINTERS.md)（若项目仍在使用）。**是否删除路径**另见 [文件删除与保留裁决 Playbook](./FILE_DELETION_OR_RETENTION_PLAYBOOK.md)。

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

### 3.2 C1 合并的标准操作顺序（推荐固定照做）

1. **出报表**：脚本或手工维护列表，按 hash 分组列出路径（建议输出到 `docs/09_AUDIT/STATE/`，便于 diff）。  
2. **选 canonical**：每组选定**唯一**真源路径（优先：现行规范目录、非 archive、已有 INDEX/SITEMAP 引用多者）。  
3. **全仓替换引用**：将指向副本的 Markdown/配置内链改为指向 canonical（可用仓库级搜索；合并 PR 内应可见替换范围）。  
4. **处理副本**（二选一，在 PR 中注明）：  
   - **删除**：副本无独立历史价值时直接删；或  
   - **stub**：保留路径但正文改为短说明 + 指向 canonical 的链接（适用于外部书签、旧 URL 仍被引用）。  
5. **索引与台账**：更新相关 `INDEX.md`、总入口；若项目使用重复簇台账，更新 [CANONICAL_POINTERS.md](../../../09_ARCHIVE/duplicates/CANONICAL_POINTERS.md) 或等价文件。  
6. **验证**：跑现有 `verify_*` / `sentinel_l1` 等与链接相关的门禁；必要时补跑蓝图索引脚本（若触及 `01_BLUEPRINTS`）。

### 3.3 C2（同名碰撞）的最小流程

1. 报表列出 `(basename → [paths…])`。  
2. 对每一碰撞簇：**人工打开比对**；指定 canonical。  
3. 若内容不同：**不得**合并为单文件；应通过重命名、移动目录或叙事归并（D 类）消解混淆。  
4. 若内容实为 C1：按 §3.2 执行。

### 3.4 D（功能重复）的最小流程

1. 扫描阶段仅输出**候选簇**（主题关键词、互链、标题相近等），登记台账。  
2. **评审会或异步 Owner 裁决**：确定真源、读者迁移路径、是否保留 stub。  
3. 再执行正文合并/删稿与链接替换（同 §3.2 第 3～6 步精神，但第 4 步以「叙事归并」为主）。

### 3.5 与扫描并行时的分工（四条线程）

| 线程 | 内容 | 与合并的关系 |
|------|------|----------------|
| **A** | 持续生成/更新：全量清单、hash 分组、basename 报表、异常路径列表 | 为 B/C 提供输入。 |
| **B** | 仅处理 **C1** 已确认分组：canonical + 替换链接 + 删或 stub | 可与 A **并行**，以报表为闸门。 |
| **C** | 断链修复、`.diff`/`.bak` 策略、脚本目录生成型 INDEX、各域导航补链、§2.3 表内校验与登记 | 与合并正交，可并行。 |
| **D** | **D 类**只维护台账与排期，**评审通过前**不删不并 | 与 A 并行；合并滞后一拍。 |
| **E（可选）** | **§7 目录队列**：按 rollup 子前缀做「退出标准」勾选，与 B 交替推进 | 合并清空某前缀后，该前缀的 C1/C2 报表应**收敛** |

### 3.6 §3 勾选（合并专项）

- [ ] 书面选定 **归档区策略**（§3.1 严格 / 宽松）。  
- [ ] C1：至少完成一轮 hash 报表 + 对**已裁决**簇执行 §3.2（可分多 PR）。  
- [ ] C2：basename 报表完成；对**高优先级**碰撞簇完成 canonical 或重命名消解。  
- [ ] D：候选簇已登记；**已裁决**簇完成叙事归并 + 链接 + 台账。  
- [ ] 合并相关 PR 均附：替换范围摘要、已跑验证脚本列表。

---

## 4. 任务波次（勾选进度）

### P0 — 基线与自动化（本轮已部分完成）

- [x] 导出全量 `git ls-files` 平面清单至 `docs/09_AUDIT/STATE/`（见上文文件名）。  
- [x] 记录扩展名与目录聚合统计（见 §1）。  
- [x] 生成 **深度 3～6** 目录聚合（JSON + MD）：`python scripts/governance/export_repo_directory_rollup.py` → `REPO_DIRECTORY_ROLLUP_20260410.*`（2026-04-10）。  
- [ ] 约定**更新频率**（例如每次大版本或每季度）并写入 [项目办公室 README](./README.md) 或本文件版本记录。

### P1 — 重复与冗余（机器可做部分）

- [ ] **同名不同路径**：对 basename 碰撞做报表（脚本或 `git ls-files` 后处理），人工判 canonical；**合并/重命名步骤见 §3.3**。  
- [x] **同内容（按后缀白名单）**：`scripts/governance/scan_duplicate_file_content.py`（例：`--ext md`）→ `docs/09_AUDIT/STATE/DUPLICATE_CONTENT_BY_HASH_*`；**合并/删稿仍须**遵守 **§3.2** 与归档策略 **§3.1**。  
- [ ] 将结果与 [孤儿与重复 Playbook](../../../09_AUDIT/STANDARDS/DOC_ORPHAN_AND_DUPLICATE_GOVERNANCE_PLAYBOOK.md) 对齐，**先归并再删**；与 **§3.6** 勾选一并推进。

### P2 — 明显「多余」扩展名与审计衍生物

- [ ] 评审 **50** 个已跟踪 `.diff`：保留标准、迁 archive、或从跟踪中移除。  
- [ ] 评审 `.bak2` / `.bak3` 等：是否应仅存于 archive 或本地（不进 Git）。  
- [ ] 对 `review_materials_package` 等路径中异常引号/命名（Windows 下曾出现统计异常）做**路径规范化**（若仍存在）。

### P3 — 索引可达性（导航）

- [ ] 从 `docs/INDEX.md` 与 [`../INDEX.md`](../INDEX.md) 出发做**抽样反向检查**：随机/分层抽样未出现在任何 INDEX/SITEMAP 的 `docs/` 文件比例（目标：持续下降）。  
- [ ] `scripts/`：在 [scripts/README.md](../../../../scripts/README.md) 或生成清单中补齐**分类导航**（与脚本数量匹配）。  
- [ ] `src/`：在根 README 或 `src/` 下 INDEX 中保证模块入口**可跳转**。

### P4 — 与现有门禁脚本对齐

- [ ] 将本清单 P1～P3 的产出与现有 `scripts/governance/verify_*`、`sentinel_l1_*` 等**能衔接的检查项**列成表（避免重复造轮子）；**矩阵须与 §1.1 一致**（脚本名 ↔ 覆盖集合 ↔ 不做的事）。  
- [x] **架构/服务目录 + C4 摘要 + 可检索 JSON**：`generate_architecture_service_catalog.py` → `docs/09_AUDIT/STATE/ARCHITECTURE_SERVICE_CATALOG_20260410.{md,json}`（2026-04-10）；含根目录机构缺口表。  
- [x] 「重复内容报表」：`scan_duplicate_file_content.py`（已落地）；可选后续接 CI **仅告警**。  
- [ ] 可选：新增 **模块全景**生成脚本（或扩展现有 rollup）：按 **§2.4** 约定深度输出 `MODULE_PANORAMA_*.{json,md}`，与 rollup **同批**重跑；[`scripts/README.md`](../../../../scripts/README.md) 登记用途。

### P5 — 深度尽治（与 §7 对齐）

- [ ] 按 **§7.1** 建立「前缀队列」并分批 PR（建议每批可 review 的规模）。  
- [ ] 对每批执行 **§7.2** 退出标准，直至 **§7.3** 总勾选可勾或例外已登记。  
- [ ] 批次间 **重跑 rollup** 与平面清单，保留 JSON diff 作证据。

---

## 5. 版本记录

| 版本 | 日期 | 说明 |
|------|------|------|
| 1.2.8 | 2026-04-10 | 落地 **`scan_index_health.py`**；§1.1 表与结论、§6 推荐阅读增 `INDEX_HEALTH_ORPHAN_*` |
| 1.2.7 | 2026-04-10 | §1.1 **结论** 增「索引健全性」边界：L1/verify 能做什么；搬迁后索引同步与可选孤儿报表互指 [文档地图与放置规则](./DOCUMENT_MAP_AND_PLACEMENT_GOVERNANCE.md) **§4～§5** |
| 1.2.6 | 2026-04-10 | 纳入 **文档地图 + 放置规则**：文首与 §6 互指；§2.3 增「文档地图与放置」行；§7.2 增 **摆放** 退出项；§8 办公室自查增 [DOCUMENT_MAP_AND_PLACEMENT_GOVERNANCE](./DOCUMENT_MAP_AND_PLACEMENT_GOVERNANCE.md) 与 AI 交接 **①‴** |
| 1.2.5 | 2026-04-10 | 治理脚本归口 `scripts/governance/`；`rollup`/`scan_duplicate` 支持 `--include-untracked`；互指 [删稿裁决 Playbook](./FILE_DELETION_OR_RETENTION_PLAYBOOK.md)；§1.1 与 §2.3 命令路径更新 |
| 1.2.4 | 2026-04-10 | **P1** 落地 `scan_duplicate_file_content.py`；§2.3 增内容重复与工具索引；互指 [治理工具总索引](./GOVERNANCE_TOOLS_INDEX.md)；§1.1 表更新 |
| 1.2.3 | 2026-04-10 | 新增 **§1.1** 扫描覆盖/格式边界（Git vs L1、全格式语义不承诺）；**§8** 增自查项；**P4** 矩阵与 §1.1 对齐 |
| 1.2.2 | 2026-04-10 | **§2.4** 增架构服务目录生成物说明；§2.3 增 C4/服务目录行；**P4** 勾选 `ARCHITECTURE_SERVICE_CATALOG_*`；§6 增入口；根目录补 **LICENSE / CONTRIBUTING / SECURITY** |
| 1.2.1 | 2026-04-10 | 新增 **§2.4** 架构模块全景与机构做法；§2.3 增「模块全景」行；**P4** 可选全景脚本；文首互指 §2.4 |
| 1.2.0 | 2026-04-10 | **§2.3** 可并行工作总表；**§7** 深度目录队列与退出标准；**§8** 办公室二次自查；**P5**；rollup 脚本与 `REPO_DIRECTORY_ROLLUP_20260410.*`；§1 明确深度 2 不足尽治 |
| 1.1.0 | 2026-04-10 | 新增 **§3 合并重复文件方案**（分型、C1/C2/D 流程、并行线程、§3.6 勾选）；P1 互指 §3 |
| 1.0.0 | 2026-04-10 | 首版：基线统计、口径、P0～P4 波次；附全量路径导出文件 |

---

## 6. 推荐阅读入口

| 说明 | 路径 |
|------|------|
| 全量已跟踪路径清单 | [`docs/09_AUDIT/STATE/REPO_GIT_TRACKED_FILES_20260410.txt`](../../../09_AUDIT/STATE/REPO_GIT_TRACKED_FILES_20260410.txt) |
| 目录深度聚合（3～6） | [`REPO_DIRECTORY_ROLLUP_20260410.md`](../../../09_AUDIT/STATE/REPO_DIRECTORY_ROLLUP_20260410.md) / [`.json`](../../../09_AUDIT/STATE/REPO_DIRECTORY_ROLLUP_20260410.json) |
| 架构服务目录 + C4 摘要（生成） | [`ARCHITECTURE_SERVICE_CATALOG_20260410.md`](../../../09_AUDIT/STATE/ARCHITECTURE_SERVICE_CATALOG_20260410.md) / [`.json`](../../../09_AUDIT/STATE/ARCHITECTURE_SERVICE_CATALOG_20260410.json) |
| 内容重复（SHA256 · 后缀白名单） | [`DUPLICATE_CONTENT_BY_HASH_20260410.md`](../../../09_AUDIT/STATE/DUPLICATE_CONTENT_BY_HASH_20260410.md) / [`.json`](../../../09_AUDIT/STATE/DUPLICATE_CONTENT_BY_HASH_20260410.json) |
| 索引健全性（零入链候选 · `scan_index_health.py`） | [`INDEX_HEALTH_ORPHAN_20260410.md`](../../../09_AUDIT/STATE/INDEX_HEALTH_ORPHAN_20260410.md) / [`.json`](../../../09_AUDIT/STATE/INDEX_HEALTH_ORPHAN_20260410.json) |
| 治理工具总索引（办公室） | [GOVERNANCE_TOOLS_INDEX.md](./GOVERNANCE_TOOLS_INDEX.md) |
| 文档地图与放置（办公室规程 · 与扫描/§7 衔接） | [DOCUMENT_MAP_AND_PLACEMENT_GOVERNANCE.md](./DOCUMENT_MAP_AND_PLACEMENT_GOVERNANCE.md) |
| `docs/` 目录职责与阶段落盘（标准真源） | [`DOCUMENT_REPOSITORY_LAYOUT_STANDARD.md`](../../../09_AUDIT/STANDARDS/DOCUMENT_REPOSITORY_LAYOUT_STANDARD.md) |
| 叙事层模块/总账入口（与 §2.4 生成物互补） | [`docs/System_Manifest.md`](../../../System_Manifest.md)、[`docs/SITEMAP.md`](../../../SITEMAP.md)、[`docs/module_designs/INDEX.md`](../../../module_designs/INDEX.md) |
| 蓝图阶段任务（并列） | [BLUEPRINT_PHASE_CLOSURE_TASK_LIST.md](./BLUEPRINT_PHASE_CLOSURE_TASK_LIST.md) |
| 孤儿与重复治理 | [DOC_ORPHAN_AND_DUPLICATE_GOVERNANCE_PLAYBOOK.md](../../../09_AUDIT/STANDARDS/DOC_ORPHAN_AND_DUPLICATE_GOVERNANCE_PLAYBOOK.md) |

---

## 7. 一次性深度治理：目录队列与退出标准

> **目的**：把「整仓一次弄干净」落实为**可打勾的目录前缀队列**，避免只盯着深度 2 的粗桶。队列来源：`REPO_DIRECTORY_ROLLUP_*.json`（全量前缀）+ MD 中 Top 表（优先啃大块）。

### 7.1 怎么从「最深」起排

1. 打开 [`REPO_DIRECTORY_ROLLUP_20260410.md`](../../../09_AUDIT/STATE/REPO_DIRECTORY_ROLLUP_20260410.md) 中 **深度 5、6** 表，找出仍很大的子树；再回退到深度 3～4 看其父链是否整枝可一起收口。  
2. 对 **`docs/09_AUDIT/REPORTS`、`docs/09_AUDIT/STATE`** 等超高计数前缀：在批次内再按**子文件夹**细分为子队列（rollup 深度加一或手工列目录）。  
3. **`docs/06_ARCHIVE/**`**：默认 **只读治理**（摆放、索引、与活动区重复标注），删并须符合 **§3.1 归档区策略**。  
4. **`scripts/`、`src/`、`notebooks/`**：以「入口可读 + 重复脚本/模块报表」为主，不单套用文档 C1 流程；**`src/` 或 API 变更**后复跑 `generate_architecture_service_catalog.py` 刷新服务目录。

### 7.2 单个目录前缀（或子队列）「退出标准」勾选模板

Owner 对每个待收口前缀打勾（可复制到 PR 描述或台账）：

- [ ] **重复**：该前缀下 **C1** 已按 §3.2 处理或确认无组；**C2** 已报表且无未决高优先级碰撞；**D 类**已登记或已裁决。  
- [ ] **摆放**：本批新增或错放文件已按 [LAYOUT 标准](../../../09_AUDIT/STANDARDS/DOCUMENT_REPOSITORY_LAYOUT_STANDARD.md)（及 [办公室放置规程](./DOCUMENT_MAP_AND_PLACEMENT_GOVERNANCE.md)）归到约定目录，或已在 PR 中登记**例外理由**与复审方式；动 `01_BLUEPRINTS` 时尚须符合 [图纸柜规则](./01_BLUEPRINTS_REPOSITORY_RULES.md)。  
- [ ] **导航**：父级或本级具备 **INDEX / README / 上级入口** 之一（归档区至少 **archive 内 INDEX** 或父级说明）。  
- [ ] **内链**：本批次改动涉及路径已跑 **L1**；全库 **0 无效** 或已登记例外。  
- [ ] **衍生物**：按 P2 策略无应迁走的 `.diff`/`.bak`（或已归档）。  
- [ ] **路径健全**：无引号/转义异常路径（见 §1 注意项）。  
- [ ] **证据**：rollup 重跑已提交或报告路径可指认。

### 7.3 §7 总勾选（尽治里程碑）

- [ ] 已对 **`docs/`** 下深度 3 Top 前缀（或 JSON 中全部超过阈值的前缀）**逐一**达到 §7.2 或登记**书面例外**（含例外原因与复审日）。  
- [ ] `scripts/`、`src/` 已按 P3 + §2.3 达到「可查入口」标准。  
- [ ] 大批次结束后已 **重跑 rollup** 并 commit，便于与上一版 JSON diff。

---

## 8. 办公室与本文档的二次自查（优化循环）

大改办公室或本清单后，维护者快速过一遍：

- [ ] [办公室 README](./README.md)：**治理流程编号**仍覆盖蓝图、孤儿/重复、扩展轨、根卫生、**整仓文件尽治**、**文档地图与放置**；**办公室文件一览**表与磁盘一致；[治理工具总索引](./GOVERNANCE_TOOLS_INDEX.md) 与 `scripts/` 实际脚本同步；[文档地图与放置规程](./DOCUMENT_MAP_AND_PLACEMENT_GOVERNANCE.md) 与 LAYOUT 标准互指无断链。  
- [ ] [AI 交接说明](./PROJECT_OFFICE_AI_HANDOFF.md)：阅读顺序与**常见任务**含「深度尽治 / rollup / 本清单 §7」、[文档地图与放置规则](./DOCUMENT_MAP_AND_PLACEMENT_GOVERNANCE.md)（①‴）与 LAYOUT 真源优先级。  
- [ ] [scripts/README.md](../../../../scripts/README.md)：治理相关脚本表含 **rollup**、`generate_architecture_service_catalog` 与既有 `verify_*` / `sentinel_l1`；若已落地 **§2.4** `MODULE_PANORAMA_*` 脚本，表中已登记。  
- [ ] 本文件 **§1 数字**（文件总数等）与 `git ls-files` / 最新 rollup **无矛盾**（或已注明「快照日期」）。  
- [ ] 与 [蓝图任务清单](./BLUEPRINT_PHASE_CLOSURE_TASK_LIST.md) **无冲突表述**（并列、互补、W 轨 ≠ 尽治）。  
- [ ] **§1.1** 已与 `scripts/` 内实际行为一致；对外未再暗示「全格式、全文件语义扫描」。
