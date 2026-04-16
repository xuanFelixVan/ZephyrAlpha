# ZephyrAlpha 项目通用 AI 治理约束

> **适用范围**：所有 AI 工具（Cursor、Trae、GitHub Copilot、Claude API 等）。本文件是跨工具的基准约束文件。
>
> **版本**：v1.2.0 | 创建日期：2026-04-16 | 状态：Active

---

## 本文件的写入原则（元规则）

> **AGENTS.md 只写永久有效的规则。**

判断标准：一条规则在项目存续期间是否始终成立，与当前阶段、当前文件数量、当前波次进度无关。

| 属于本文件的内容 | 不属于本文件的内容（写哪里）|
|----------------|--------------------------|
| 操作边界与禁止行为（永久约束） | 当前文件数量、wave进度（→ `elimination-pipeline-tracker.yaml`）|
| 锚点文件列表（结构不变时永久有效） | 当前断链数量、扫描结果（→ `SENTINEL_L1_SCAN_LATEST.md`）|
| 启动协议、格式标准、路径约定 | 某次事故的具体数字（→ `docs/08_KNOWLEDGE/BEST_PRACTICES/`）|
| 工具权限层级（工具选型不变则永久有效） | 特定蓝图的处置计划（→ 对应 Playbook）|

**修改本文件时**：每条新增内容必须通过"永久性测试"——问：这条规则在 6 个月后还有效吗？无效则不应写入。

---

## 零、工具权限层级（Tool Authority Hierarchy）

本项目采用双编辑器分工，权限层级如下：

```
┌─────────────────────────────────────────────────────────────┐
│  Level 1（最高）：Cursor 专用规则                              │
│  文件：.cursor/rules/project-conventions.mdc                 │
│         .cursor/rules/audit-system.mdc                      │
│         .cursor/rules/code-conventions.mdc                  │
│  权限：可修改所有文件，包括 AGENTS.md 和 .roomodes             │
├─────────────────────────────────────────────────────────────┤
│  Level 2（次高）：Trae 专用规则                               │
│  文件：.roomodes（slug: zephyr-gov 模式）                     │
│  权限：可修改 docs/、scripts/、src/                           │
│  ❌ 禁止修改：.cursor/rules/ 下任何文件                        │
│  ❌ 禁止修改：AGENTS.md、.roomodes（只有 Owner 可改）           │
├─────────────────────────────────────────────────────────────┤
│  Level 3（基准）：本文件 AGENTS.md                            │
│  文件：AGENTS.md                                             │
│  权限：只读基准，所有工具共同遵守                               │
└─────────────────────────────────────────────────────────────┘
```

**Trae 入职模式**：在 Trae 中工作时，必须切换到 `.roomodes` 中的 `zephyr-gov` 模式，该模式包含完整的项目约束和 Write Gate 规则。

---

---

## 一、项目背景（30 秒快速定向）

ZephyrAlpha 是一个**个人量化交易系统**，当前处于 **Phase 2（施工图纸阶段）**。

- **源代码**：`src/`（Python）
- **核心文档**：`docs/`（Markdown 为主）
- **治理脚本**：`scripts/`（Python）

> 文件数量、当前 wave 进度等运行时状态，见 `docs/09_AUDIT/STATE/elimination-pipeline-tracker.yaml`，不在本文件维护。

**当前 Phase 计划**：读取 `docs/04_CONSTRUCTION/PLANS/MASTER_DEVELOPMENT_PLAN.md` 获取最新状态。

---

## 二、不可触碰的锚点文件（Immutable Anchors）

以下文件是整个治理系统的基座，**任何情况下不得删除、重命名或移动**：

```
docs/subsystem-registry.yaml
docs/01_GOVERNANCE/governance-asset-inventory.yaml
docs/02_ARCHITECTURE/EXECUTABLE_ASSET_REGISTRY.md
docs/02_ARCHITECTURE/BLUEPRINT_DOMAIN_INVENTORY.yaml
docs/02_ARCHITECTURE/MODULE_INVENTORY.md
docs/02_ARCHITECTURE/TECH_DECISION_RECORDS.md
docs/04_CONSTRUCTION/PLANS/MASTER_DEVELOPMENT_PLAN.md
docs/01_GOVERNANCE/REGISTERS/controlled-documents-register.md
docs/01_GOVERNANCE/REGISTERS/scripts-canonical-tier1.yaml
docs/01_GOVERNANCE/REGISTERS/lessons-learned-register.md
docs/09_AUDIT/STANDARDS/INDEX.md
docs/09_AUDIT/STATE/elimination-pipeline-tracker.yaml
docs/09_AUDIT/STATE/module_id_registry.json
.cursor/rules/project-conventions.mdc
.cursor/rules/audit-system.mdc
.cursor/rules/code-conventions.mdc
.pre-commit-config.yaml
AGENTS.md（本文件）
```

---

## 三、会话启动强制协议

**每次会话开始，在执行任何操作之前，必须按顺序完成以下步骤**：

1. 读取 `AGENTS.md`（本文件）—— 了解操作边界
2. 读取 `docs/04_CONSTRUCTION/PLANS/MASTER_DEVELOPMENT_PLAN.md` —— 找到当前 Phase 和下一个待完成任务
3. 读取 `docs/01_GOVERNANCE/governance-asset-inventory.yaml` —— 确认治理资产状态
4. 报告：当前处于 Phase X，本次任务是 Y，属于流水线 Wave Z

> 此协议防止 AI 跳跃执行、破坏施工顺序。任何模型均不得跳过。

### 条件性必读（按任务类型）

> 以下文件不要求每次会话都读，但在特定任务开始前必须先查阅：

| 任务类型 | 必须先读 | 原因 |
|---------|---------|------|
| 引入新技术/框架/库 | `docs/02_ARCHITECTURE/TECH_DECISION_RECORDS.md` | 避免与已有 ADR 冲突；复用已有技术选型理由 |
| 修改架构设计（模块边界/接口/依赖） | `docs/02_ARCHITECTURE/TECH_DECISION_RECORDS.md` | 新决策须参考历史决策上下文，并追加 ADR 条目 |
| 首次进入项目 / 对系统演化历史有疑问 | `docs/02_ARCHITECTURE/TECH_DECISION_RECORDS.md` § 架构演化时间线 | 了解项目从何处来、当前所处阶段，以及重要的结构性变化历史 |
| 在某领域首次工作（因子/回测/执行层等） | `docs/08_KNOWLEDGE/BEST_PRACTICES/` 对应条目 | 避免重蹈已记录的坑；复用已验证的最佳实践 |
| 编辑 `docs/09_AUDIT/STANDARDS/` 中的标准文档 | `docs/08_KNOWLEDGE/BEST_PRACTICES/KE-025-encoding-corruption-and-dead-links-postmortem.md` | 标准文档历史上有编码损坏问题，修复前必须了解正确流程 |
| 删除或移动任何文件 | `docs/01_GOVERNANCE/PLAYBOOKS/dead-link-repair-playbook.md` § 链接维护契约 | 避免产生孤立断链 |

---

## 三-B、施工图格式强制标准（Phase 2 专用）

> **适用对象**：所有 AI 模型在编写或审核 `docs/04_CONSTRUCTION/PLANS/construction-plan-*.md`（及历史遗留的 CONSTRUCTION_PLAN_L00_DATA_SOURCE.md）时必须遵守。

### 施工图 7 点格式（验收门禁）

**施工图缺少任何一个章节，视为 Draft 状态，不得进入 Phase 3 实施。**

| 章节 | 必含内容 | 验收要求 |
|------|---------|---------|
| 1. 前置条件 | 依赖蓝图路径、输入数据契约、运行环境 | 明确列出依赖文件路径 |
| 2. 模块分解 | 模块 ID + 名称 + 职责（3-8 个单元） | 每个模块职责不重叠 |
| 3. 公共 API | 函数签名（Python type hints）+ 异常类型 | mypy 可静态通过 |
| 4. 数据流 | Mermaid 图，覆盖输入→处理→输出全链路 | 无孤立节点 |
| 5. 测试 | 每模块至少 3 条 P0 用例（含边界/异常） | 覆盖主路径+异常路径 |
| 6. 技术选型与 TDR | 引用 ADR 编号；未决策项标 TBD+ADR ID | 无未引用的技术选型 |
| 7. 已知风险与缓解 | 至少 2 条风险 + 缓解策略 | 含 P0 级风险分析 |

### 施工图命名与存放规范

- **命名格式**：`construction-plan-{layer-code}-{layer-name}.md`（全小写 kebab-case，见 doc-naming-standard.md v2.0.0）
- **强制存放路径**：`docs/04_CONSTRUCTION/PLANS/`（禁止放在其他位置）
- **建立后必须同步**：
  1. 更新 `docs/04_CONSTRUCTION/PLANS/INDEX.md`（加入新条目并标记状态）
  2. 在 `docs/02_ARCHITECTURE/MODULE_INVENTORY.md` 对应层行添加施工图链接
  3. 在 `docs/01_GOVERNANCE/REGISTERS/controlled-documents-register.md` 注册
  4. 将 `docs/04_CONSTRUCTION/PLANS/MASTER_DEVELOPMENT_PLAN.md` 中对应任务标记为 `[x]`

---

## 四、操作边界（强制约束）

### 4.1 文件操作限制

| 约束 | 规则 |
|------|------|
| 单次处理文件数 | **≤ 20 个文件**（文件消除流水线每 session 上限） |
| 单次处理蓝图数 | **≤ 10 个蓝图**（蓝图安全流水线每 session 上限） |
| 新建顶级目录 | **禁止**（必须先在 `docs/subsystem-registry.yaml` 登记并获得批准） |
| 修改 `.cursor/rules/` | **禁止**（Trae 等非 Cursor 工具不得修改 Cursor 规则文件） |
| 修改 `AGENTS.md` | **禁止**（只有项目 Owner 可修改） |
| 写入废弃目录 | **禁止**（见第六节废弃路径表） |
|| **在项目根目录创建新文件** | **禁止**。根目录只允许白名单文件（AGENTS.md, README.md, LICENSE, CONTRIBUTING.md, SECURITY.md, pyproject.toml, requirements*.txt, .pre-commit-config.yaml, .env*, .gitignore, .editorconfig, .roomodes）。其他 .py/.txt/.json/.md 必须放入对应子目录（审计脚本→scripts/audit/, 工具→scripts/, 设计文档→docs/）。 |
| **单次 session 新建文件数** | **≤ 5 个**（不含 SESSION_LOG 和流水线已规划的批量操作）超出必须先删除等量旧文件 |
| **文件名禁止带版本号** | **禁止** `-v2`、`-v3`、`-round2` 等后缀；版本历史用 `git log` 查询 |
| **状态文件写入方式** | **必须覆盖写入**（LATEST 模式）；不得按日期新建文件（`SENTINEL_L1_SCAN_LATEST.json`，而非带日期的文件名） |
| **AI 生成产物写入位置** | **必须写入 `.audit_cache/`**（已 gitignored），禁止写入 `docs/09_AUDIT/REPORTS/ARCHIVE/` 等受版本控制目录 |
| **AI 生成文件 frontmatter** | 必须包含 `type: generated` 和 `ttl: 7d\|30d\|permanent` 字段 |

### 4.2 删除操作的安全门禁

删除任何文件前，必须通过以下三问：

1. **是否在不可触碰锚点列表中？** 是 → 停止，禁止删除
2. **是否已提取知识/价值？** 否且文件包含设计决策/策略/代码 → 必须先提取到知识库
3. **是否有其他文件引用它？** 是 → 必须先更新所有引用（Change Propagation Map）

### 4.3 文件搬迁协议

对任何文件执行移动、重命名、删除前：

```bash
# Step 1: 查询搬迁历史（强制）
git log --follow --diff-filter=R --name-status --oneline -- "{path}"
```

- 若搬迁次数 **≥ 2**：**停止**，报告给用户确认后继续
- 搬迁 commit message 必须包含：`moved: old/path -> new/path | reason: 一句话原因`

### 4.4 Git 历史操作安全规则（Pipeline C 专用）

> Pipeline C 是只读挖掘流水线，**绝对不修改 git 历史本身**。

| 约束 | 规则 |
|------|------|
| **只读命令** | Pipeline C 只允许 `git log`、`git show`、`git diff`、`git cat-file` 等只读操作 |
| **禁止历史改写** | **绝对禁止** `git rebase`、`git filter-branch`、`git replace`、`BFG Repo Cleaner` 等任何改写历史的操作 |
| **禁止强制推送** | **绝对禁止** `git push --force` 或 `git push --force-with-lease` |
| **禁止在 Pipeline C session 中删除文件** | Pipeline C session 唯一允许的写操作是在 `docs/08_KNOWLEDGE/` 下新增知识条目 |
| **每 session 限量** | 每个 Pipeline C session 最多读取 **20 个**历史文件，提取 **≤10 个**知识条目 |
| **commit 格式** | `feat(knowledge): GH-Wave-X extract KE-XXX~KE-YYY from git history` |

**读取被删文件的标准命令（PowerShell）**：
```powershell
# Step 1: 找到删除该文件的 commit hash
$commit = git log --diff-filter=D --no-renames --pretty=format:"%H" -- "被删文件路径" | Select-Object -First 1
# Step 2: 读取被删时的文件内容（父 commit 中的版本）
git show "${commit}^:被删文件路径"
```

---

## 五、文件消除流水线操作规范

> 本节用于 **Trae 免费模型** 长期执行的文件消除任务

### 5.1 每次 Session 必读文件（Trae 执行前）

```
1. AGENTS.md（本文件）
2. docs/09_AUDIT/STATE/elimination-pipeline-tracker.yaml — 当前波次进度
3. docs/01_GOVERNANCE/governance-asset-inventory.yaml — 治理资产总清单
4. docs/subsystem-registry.yaml — 目录注册表
```

### 5.2 分类打标规范

处理每个文件时，必须打上以下之一的分类标签：

| 标签 | 含义 | 处置规则 |
|------|------|---------|
| `BLUEPRINT` | 模块设计蓝图 | 提取设计决策到 `docs/08_KNOWLEDGE/` 后删除/归档 |
| `MODULE_SPEC` | 模块技术规格 | 提取接口定义到 `MODULE_INVENTORY.md` 后合并 |
| `STRATEGY` | 交易/因子策略 | 提取策略逻辑到 `docs/03_TRADING_TACTICS/` 后保留精华 |
| `AUDIT_REPORT` | 审计/扫描报告 | 保留最新 3 个版本，删除旧版本 |
| `STATE_SNAPSHOT` | 状态快照/JSON | TTL 清理（30 天），不入知识库 |
| `GOVERNANCE_STD` | 治理标准文档 | 保留，合并同类后精简 |
| `KNOWLEDGE_ENTRY` | 已是知识条目 | 保留，无需处理 |
| `TEMP_ARTIFACT` | 临时产出物 | TTL 清理（7 天），不入知识库 |
| `ORPHAN_SHELL` | 空壳/孤儿文件（无实质内容） | 直接删除 |
| `ENCODING_BROKEN` | 编码损坏文件 | 尝试修复后重新分类，无法修复则删除 |

### 5.3 知识入库子目录对照表

从文件中提取的知识条目，根据分类写入 `docs/08_KNOWLEDGE/` 的对应子目录：

| 知识类别 | 写入子目录 | 示例文件名 |
|---------|----------|----------|
| `blueprint_decision`（蓝图设计决策）| `docs/08_KNOWLEDGE/BEST_PRACTICES/` | `KE-021-data-layer-design.md` |
| `strategy`（交易策略）| `docs/08_KNOWLEDGE/STRATEGY_LIBRARY/` | `KE-022-momentum-strategy.md` |
| `factor`（因子设计）| `docs/08_KNOWLEDGE/FACTOR_LIBRARY/` | `KE-023-alpha-factor.md` |
| `best_practice`（最佳实践）| `docs/08_KNOWLEDGE/BEST_PRACTICES/` | `KE-024-backtest-practice.md` |
| `lesson_learned`（教训记录）| `docs/08_KNOWLEDGE/BEST_PRACTICES/` | `KE-025-encoding-lesson.md` |

**KE 编号分配规则**：每次 session 开始前，执行以下命令获取当前最大编号：
```bash
# PowerShell（Windows）
Get-ChildItem -Path docs/08_KNOWLEDGE -Recurse -Filter "KE-*.md" | Select-Object Name | Sort-Object Name -Descending | Select-Object -First 5
```
从当前最大编号 +1 开始分配（若无 KE- 格式文件，从 KE-001 开始）。

### 5.4 安全删除前的引用检查命令

删除文件前，必须执行以下命令检查引用：

```powershell
# 检查某文件被哪些 INDEX.md 或其他文件引用（PowerShell）
$target = "被删文件名（不含路径）"
Select-String -Path "docs/**/*.md" -Pattern $target -Recurse | Select-Object Filename, LineNumber, Line
```

- 若找到引用 → 先更新所有引用文件，再执行删除
- `pre-commit hook` 会在提交时再次检验，确保无断链
- **绝对不能** 用 `--no-verify` 跳过此检查

### 5.5 知识入库格式

从文件中提取的知识条目，写入 `docs/08_KNOWLEDGE/` 时必须使用标准 frontmatter：

```yaml
---
module_id: KE-{三位数序号}
title: "条目标题"
category: blueprint_decision | strategy | factor | best_practice | lesson_learned
source_file: "原始文件路径（用于溯源）"
extracted_date: "YYYY-MM-DD"
version: "1.0.0"
status: Active
layer: L{层编号}
owner: ZephyrAlpha-Owner
---
```

### 5.4 Commit 格式（文件消除专用）

```
chore(cleanup): eliminate N files from {area}, extracted K knowledge entries

- Wave {波次编号}: {目标区域描述}
- Files removed: N
- Knowledge entries added: K
- Tracker updated: docs/09_AUDIT/STATE/elimination-pipeline-tracker.yaml
```

### 5.5 波次执行顺序

> **波次详情（目标区域、预估文件数、当前进度）属于运行状态，不在本文件维护。**
>
> 见：docs/09_AUDIT/STATE/elimination-pipeline-tracker.yaml
>
> 本节只记录永久性的执行原则：

- 按「从易到难」推进：无唯一价值的批量产物 → 过期状态快照 → 空壳目录 → 有价值需提取知识的蓝图
- 每个 wave 完成后必须运行 Sentinel 扫描，确认断链增量符合预期（见 §十一 链接维护契约）
- 高价值文件（P0/P1 蓝图、设计决策）须先提取知识条目再处置

---

## 六、蓝图安全流水线操作规范

> 本节用于 **Trae 免费模型** 长期执行的蓝图治理任务

### 6.1 每次 Session 必读文件（Trae 执行前）

```
1. AGENTS.md（本文件）
2. docs/02_ARCHITECTURE/BLUEPRINT_DOMAIN_INVENTORY.yaml — 蓝图注册表
3. docs/subsystem-registry.yaml — 目录注册表
4. docs/09_AUDIT/STATE/elimination-pipeline-tracker.yaml — 流水线进度（确认当前 BP Wave）
```

### 6.2 蓝图价值评估矩阵

| 维度 | P0（必须保留） | P1（应该保留） | P2（可以精简） | P3（可以删除） |
|------|--------------|--------------|--------------|--------------|
| Phase 2 施工需要？ | 是，直接使用 | 是，需改造 | 否，未来可能 | 否，永远不会 |
| 有唯一设计决策？ | 是 | 部分 | 无 | 无 |
| 有可执行的技术规格？ | 是 | 部分 | 无 | 无 |

### 6.3 蓝图处置规则

- **P0/P1**：修正 frontmatter → 迁移到 `docs/03_BLUEPRINTS/{layer}/`
- **P2**：提取知识条目 → 归档到 `docs/09_AUDIT/REPORTS/ARCHIVE/`（注明 reason: p2-archive）
- **P3**：提取知识条目（如有）→ **不直接删除**，写入 `docs/09_AUDIT/STATE/p3-deletion-report-{YYYYMMDD}.md`，进入三阶段裁决：Trae 生成报告 → Kimi 双轮独立复查 → Claude 最终裁决执行

### 6.4 Commit 格式（蓝图安全流水线专用）

```
chore(blueprint): process N blueprints in {wave}, migrated M to 03_BLUEPRINTS

- Wave {波次编号}: {目标区域描述}
- Migrated (P0/P1): M files -> docs/03_BLUEPRINTS/{layer}/
- Archived (P2): A files -> docs/09_AUDIT/REPORTS/ARCHIVE/
- Deleted (P3): D files
- Registry updated: BLUEPRINT_DOMAIN_INVENTORY.yaml
```

---

## 六-C、Git 历史知识挖掘流水线操作规范（Pipeline C）

> 本节用于 **Trae 免费模型** 长期执行的 Git 历史知识挖掘任务。
> **Prompt 模板**：`docs/04_CONSTRUCTION/PLANS/trae-prompt-git-history-pipeline.md`

### C.1 每次 Session 必读文件

```
1. AGENTS.md（本文件，尤其是 4.4 节 Git 安全规则）
2. docs/09_AUDIT/STATE/elimination-pipeline-tracker.yaml — 确认当前 GH Wave 和已处理索引
3. docs/08_KNOWLEDGE/INDEX.md — 获取当前最大 KE 编号
```

### C.2 生成待挖掘文件列表的命令

```powershell
# GH Wave 1：挖掘 .audit_fix_backup 被删蓝图
git log --diff-filter=D --no-renames --name-only --pretty=format:"" |
  Where-Object { $_ -match "audit_fix_backup" -and $_ -match "\.md$" } |
  Sort-Object -Unique |
  Select-Object -Skip {已处理数量} -First 20

# GH Wave 2：挖掘 docs/01_FRAMEWORK 被删或大改的历史版本
git log --diff-filter=D --no-renames --name-only --pretty=format:"" |
  Where-Object { $_ -match "docs/01_FRAMEWORK" -and $_ -match "\.md$" } |
  Sort-Object -Unique |
  Select-Object -Skip {已处理数量} -First 20

# GH Wave 3：挖掘全仓库 strategy/factor/design 相关被删文件
git log --diff-filter=D --no-renames --name-only --pretty=format:"" |
  Where-Object { $_ -match "(strategy|factor|design|module|blueprint)" -and $_ -match "\.md$" } |
  Where-Object { $_ -notmatch "audit_fix_backup" -and $_ -notmatch "01_FRAMEWORK" } |
  Sort-Object -Unique |
  Select-Object -Skip {已处理数量} -First 20
```

### C.3 价值评估标准（三问快速判断）

| 问题 | 回答 | 处置 |
|------|------|------|
| 是否包含独立的设计决策/算法规格/参数配置？ | 是 | → **高价值**，提取知识条目 |
| 是否是另一现存文件的逐字复制？ | 是 | → **跳过**，记录为 duplicate |
| 是否是一次性扫描产物（openclaw-l2、deep-audit）？ | 是 | → **跳过**，记录为 scan_artifact |

### C.4 知识条目的特殊 frontmatter 字段

Pipeline C 提取的知识条目，在标准 frontmatter 基础上，**必须额外包含**：

```yaml
source_git_deleted: true
original_path: "docs/01_FRAMEWORK/xxx-blueprint.md"   # 被删前的路径
deleted_in_commit: "abc1234"                           # 删除该文件的 commit hash
recovery_date: "YYYY-MM-DD"                            # 本次挖掘日期
```

### C.5 Commit 格式（Pipeline C 专用）

```
feat(knowledge): GH-Wave-X extract KE-XXX~KE-YYY from git history

- Source files scanned: N
- High-value files found: M
- Knowledge entries created: K
- Tracker updated: docs/09_AUDIT/STATE/elimination-pipeline-tracker.yaml
```

### C.6 执行顺序建议

| Wave | 优先级 | 原因 |
|------|:------:|------|
| GH Wave 1（.audit_fix_backup 被删蓝图） | **最高** | 文件已物理删除，仅存于 git，且密度最高（约 300 个蓝图） |
| GH Wave 2（01_FRAMEWORK 历史版本） | 高 | 与当前 Pipeline B 蓝图整理并行，可互相印证 |
| GH Wave 3（全仓库 strategy/factor）| 中 | 范围最广，建议在 Wave 1-2 完成后执行 |

---

## 七、路径约定

### 7.1 强制写入路径

| 操作类型 | 强制路径 |
|---------|---------|
| 新蓝图（当前过渡期） | `docs/01_FRAMEWORK/` |
| 新蓝图（长期目标） | `docs/03_BLUEPRINTS/L{XX}_{LAYER}/` |
| 知识条目 | `docs/08_KNOWLEDGE/` 对应分区 |
| 审计报告 | `docs/09_AUDIT/STATE/` |
| 治理标准 | `docs/09_AUDIT/STANDARDS/` |
| 施工图纸 | `docs/04_CONSTRUCTION/PLANS/` |
| 业务代码 | `src/zephyr/{layer_id}/` |
| 治理脚本 | `scripts/governance/` |
| 审计脚本 | `scripts/audit/` |
| Session Log | `docs/09_AUDIT/STATE/SESSION_LOGS/` |

### 7.2 废弃路径（禁止写入）

| 废弃路径 | 替代路径 |
|---------|---------|
| `docs/07_AUDIT/` | `docs/09_AUDIT/` |
| `docs/06_KNOWLEDGE_BASE/` | `docs/08_KNOWLEDGE/` |
| `docs/05_IMPLEMENTATION/04_OPERATIONS/audit_state/` | `docs/09_AUDIT/STATE/` |
| `docs/08_KNOWLEDGE_BASE/` | `docs/08_KNOWLEDGE/` |
| `docs/07_GOVERNANCE_COMPLIANCE/` | `docs/10_GOVERNANCE_COMPLIANCE/` |
| `docs/07_ARCHIVED/` | `docs/06_ARCHIVE/` |
| `docs/ARCHIVE/` | `docs/06_ARCHIVE/` |

---

## 八、编码安全规则（强制）

> **根因**：Trae 的 `files.autoGuessEncoding` 选项将 UTF-8 文件误判为 GBK/Latin-1，
> 保存时以错误编码写回，产生双重编码乱码（表现为文件末尾出现阿拉伯文/西里尔文/
> 波斯文字符）。Cursor 以 UTF-8 重新读取后，乱码字节暴露。

### 根因机制

```
正常 UTF-8 文件
    ↓ Trae autoGuessEncoding=true 误判为 GBK/Latin-1
    ↓ 以错误编码写入磁盘
    ↓ Cursor 以 UTF-8 读取
显示乱码（文件末尾出现阿拉伯/西里尔字符）
```

### 必须遵守的规则

- **切换编辑器前**：确保当前编辑器所有文件已保存并关闭
- **切换编辑器后第一步**：运行 `python scripts/hooks/doc_guard_pre_commit.py --scan-encoding`
- **禁止**在两个编辑器中同时打开同一文件进行编辑
- **Trae 必须确认** `files.autoGuessEncoding` = `false`，`files.encoding` = `utf8`
- **禁止**使用 `echo` 重定向或 PowerShell `Out-File` 默认参数创建 `.md` 文件（Windows 默认 UTF-16 LE 或 GBK）
- 所有 Python 脚本创建文件时必须显式指定 `encoding='utf-8'`

### 发现编码损坏后的修复流程（唯一正确方式）

```bash
# 1. 确认损坏范围
python scripts/hooks/doc_guard_pre_commit.py --scan-encoding

# 2. 从 git 历史恢复（推荐，不要手动修改乱码字符）
git checkout HEAD -- <损坏文件路径>

# 3. 若 HEAD 也已损坏，找干净版本
git log --oneline -- <损坏文件路径>
git show <干净commit>:<损坏文件路径> > temp.md
# 对比确认后替换

# 4. 确认修复
python scripts/hooks/doc_guard_pre_commit.py --scan-encoding
```

### 绝对禁止操作

| 禁止操作 | 替代方案 |
|---------|---------|
| 用文本编辑器逐字修改乱码字符 | `git checkout -- <file>` 整文件还原 |
| PowerShell `echo` / `Out-File` 默认参数写 `.md` | `Python Path(f).write_text(content, encoding='utf-8')` |
| Python `open(f, 'w')` 不指定 encoding | 必须加 `encoding='utf-8'` |
| 两个编辑器同时打开同一文件编辑 | 同一时刻只用一个编辑器 |

---

## 九、Git 操作规范

- **禁止** `git add .` 或 `git add -A`（必须精确指定路径）
- **禁止** `--no-verify`（不得跳过 pre-commit hooks）
- **禁止** `--force` push
- 不 push 到远程，除非用户明确要求
- 搬迁 commit 必须包含：`moved: {old} -> {new} | reason: {原因}`

---

## 十、会话结束必做

每次 session 结束前，必须写入 Session Log：

**存放位置**：`docs/09_AUDIT/STATE/SESSION_LOGS/`
**命名格式**：`session-YYYYMMDD-NNN.md`（NNN 为当日序号）

**Session Log 必须包含**：
1. 本次完成的任务列表
2. 变更的文件（含操作类型：创建/编辑/移动/删除）
3. 提取的知识条目数量
4. 关键决策（如有）
5. 未完成事项（交接给下一个 session）
6. 更新 `docs/09_AUDIT/STATE/elimination-pipeline-tracker.yaml`（如有文件消除操作）

---

## 十一、链接维护契约（强制）

> **根因**：AI 工具执行"直接任务"（删除/移动文件）时，常遗漏"完整性副作用"（更新所有引用），
> 导致断链在流水线操作后批量积累。

### 删除文件的强制三步

```bash
# 第一步：找到所有指向目标文件的引用
rg "目标文件名（不含扩展名）" docs/ --include="*.md" -l

# 第二步：在同一 commit 内更新或移除所有引用
# （不允许分两次 commit：先删文件、后清引用）

# 第三步：删除后运行 Sentinel 扫描确认断链增量符合预期
python scripts/audit/sentinel_l1_governance_scan.py
```

### 移动/归档文件的强制两步

```bash
# 第一步：git mv 后立即搜索旧路径的所有引用
rg "旧文件路径或文件名" docs/ --include="*.md" -l

# 第二步：批量替换旧路径为新路径，与 git mv 在同一 commit 提交
```

### 规划链接的写法规范

尚不存在的文件若需要被引用，必须使用注释格式，禁止使用普通 Markdown 链接：

```markdown
<!-- PLANNED: ../04_CONSTRUCTION/PLANS/construction-plan-l01-data-processing.md -->
```

普通 Markdown 链接 `[文字](不存在的路径)` 会被检测器计为断链，推高阈值，影响治理信号可信度。

### 断链阈值

| 状态 | 目标阈值 |
|------|---------|
| 正常生产 | ≤ 100 条 |
| 流水线重构过渡期 | ≤ 500 条（临时，需明确注释） |
| 超出 500 | pre-commit 直接阻断 commit |

---

## 十二、标准文档完整性规则（强制）

> **根因**：编码损坏后若对损坏文件进行"局部修补"（切除尾部、追加块、混合中英文段落），
> 会产生混合编码文件，比全损文件更难处理，且内容真实性存疑。

### 标准文档损坏时的唯一合法修复路径

```
检测损坏
    │
    ▼ git checkout HEAD -- <file>   ← 首选：从 HEAD 恢复
    │   成功？→ 完成
    │   失败（HEAD 也已损坏）？
    │
    ▼ git log --oneline -- <file>   ← 找到最近的干净版本
       git show <commit>:<file> > temp.md
       确认内容 → 覆盖替换
       找不到干净版本？
    │
    ▼ 用健康同类文件为模板 + 按文件名/用途 人工重写全文  ← 最后手段
```

### 绝对禁止

- **禁止**在损坏文件上追加"修复块"或混合段落（会产生混合编码）
- **禁止**手动逐字替换乱码字符（字节层面无法对齐）
- **禁止**将损坏标准文档当作参考资料使用（内容不可信）

### 标准文档损坏的识别信号

| 信号 | 含义 |
|------|------|
| frontmatter 字段值出现阿拉伯文/西里尔文字符 | 主体可能全部损坏 |
| 正文标题出现非中英文字符 | 至少局部损坏 |
| 尾部出现重复 frontmatter 块 | 双重编码追加导致 |
| `python scripts/hooks/doc_guard_pre_commit.py --scan-encoding` 报告此文件 | 确认损坏 |

---

## 十三、禁止行为汇总

| 禁止行为 | 原因 |
|---------|------|
| 删除锚点文件 | 治理系统崩溃风险 |
| 写入废弃路径 | 导致路径分裂，破坏治理索引 |
| `git commit --trailer "Made-with: Cursor" --no-verify` | 绕过 24 个 pre-commit 钩子（19 个本地 + 5 个社区）|
| 单次处理 >20 个文件 | 超出免费模型上下文窗口，容易出错 |
| 创建新的顶级目录 | 未经注册，破坏 subsystem-registry |
| 修改 `.cursor/rules/` | Trae 无权修改 Cursor 专有规则 |
| 同时在 Cursor 和 Trae 打开同一文件 | 编码损坏风险 |
| 不写 Session Log 直接退出 | 丢失工作记录，下一个 session 无法续接 |
| 重新创建已存在功能的脚本 | 造成脚本重复（现有 50+ 个治理脚本） |
|| `git rebase` / `git filter-branch` / `git replace` | 改写 git 历史，永久丢失被删内容（Pipeline C 知识金矿） |
|| `git push --force` 或 `--force-with-lease` | 强制覆盖远端历史，不可恢复 |
|| Pipeline C session 中执行 `git rm` 或删除任何文件 | Pipeline C 是只读挖掘流水线，不得修改工作区 |
| **文件名加版本号（-v2/-v3/-round2）** | git 已提供版本历史，文件名版本号是纯粹重复且破坏目录预算 |
| **批量扫描结果直接写入 docs/** | 扫描产物必须写入 `.audit_cache/`（已 gitignored），禁止入库污染版本历史 |
| **每日新建状态快照文件** | 必须覆盖 LATEST 文件；历史通过 `git log` 查询，不得在目录中堆积日期文件 |
| **单次 session 新建 >5 个文件** | 超出写入预算；必须先删等量旧文件再建新文件，或在流水线 session 中申请豁免 |

---

*本文件由 ZephyrAlpha Owner 维护。如需修改，必须同时更新 `.cursor/rules/project-conventions.mdc` 中的对应条目。*
