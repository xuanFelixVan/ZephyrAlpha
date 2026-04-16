---
module_id: PROC-BP-SAFETY-001
title: "Trae 蓝图安全流水线标准 Prompt 模板"
version: "1.0.0"
status: Active
layer: L00
owner: ZephyrAlpha-Owner
created_date: "2026-04-16"
description: "供 Trae 免费模型每次 session 使用的标准化 Prompt，执行 ZephyrAlpha 蓝图安全治理流水线"
---

# Trae 蓝图安全流水线标准 Prompt 模板

> **使用说明**：每次启动一个 Trae session 执行蓝图治理任务时，将下面【SESSION PROMPT】区块的内容复制粘贴到 Trae 对话框，根据当次任务替换 `{}` 中的占位符。

---

## 【SESSION PROMPT】开始（从这里复制）

```
你是 ZephyrAlpha 项目的蓝图治理执行助手。本次任务是执行蓝图安全流水线的 {BP Wave 编号}（{BP Wave 名称}）。

ZephyrAlpha 是个人量化交易系统，当前处于 Phase 2 准备阶段（进入施工前的最后瘦身）。蓝图是系统设计文档，目前散落在 6+ 个目录中，需要统一治理迁移到 docs/03_BLUEPRINTS/ 目录。

---

## 第一步：强制准入检查（不得跳过）

请按顺序读取以下文件：

1. 读取 `AGENTS.md` → 确认操作边界，记下不可触碰的锚点文件
2. 读取 `docs/02_ARCHITECTURE/BLUEPRINT_DOMAIN_INVENTORY.yaml` → 了解当前蓝图注册状态
3. 读取 `docs/subsystem-registry.yaml` → 确认目标目录状态
4. 读取 `docs/09_AUDIT/STATE/elimination-pipeline-tracker.yaml` → 确认当前 BP Wave 进度

**⚠️ 关键：在读取文件后，必须立即运行以下命令建立"本次 session 基线"：**

```powershell
# 记录当前 git 状态（本次 session 开始前的状态）
git status --short
git log --oneline -5
```

将上述命令输出的结果完整写入你的报告。这是区分"本次操作"与"历史已有操作"的唯一依据。
**任何在 `git status` 输出中不出现的变更，都不是本次 session 做的，不得当作本次成果汇报。**

报告格式：
- 当前 BP Wave：{BP Wave 编号}，状态：{pending/in_progress}
- 目标目录：{路径}
- 已迁移蓝图数：{数字} / 目标 {数字}
- BLUEPRINT_DOMAIN_INVENTORY 中本批次蓝图状态概况
- **本次 session 基线（git status 输出）**：{粘贴输出结果}

---

## 第二步：蓝图选择（本次处理 5-10 个）

从目标目录中选择本次处理的蓝图，优先选择：
1. 已有重复副本的蓝图（BLUEPRINT_DOMAIN_INVENTORY 中 duplicate_of 字段非空）
2. frontmatter 中 priority: P0 的蓝图
3. 文件名最能描述一个具体模块的蓝图（避免集合文件如 *-collection、*-supplement）

列出选中的 5-10 个文件，直接进入第三步处理（无需等待确认）。
P3 候选文件不执行删除，写入 p3-deletion-report-{YYYYMMDD}.md 后进入三阶段裁决流程。

**注意**：以下类型文件不属于"蓝图"，需要移交文件消除流水线处理：
- 文件名含 `-gap-analysis-`
- 文件名含 `-supplement-`
- 文件名含 `-collection-`
- 文件名含 `-stage-complete-`
- 文件名含 `-audit-report-`
- 文件名含 `-completeness-analysis-`

---

## 第三步：健康检查（对每个蓝图）

对每个选中的蓝图文件，读取前 30 行，检查：

**A. YAML frontmatter 完整性**（必需字段）
- [ ] `module_id`（格式：字母数字组合，如 `BP-DATA-001`）
- [ ] `version`（格式：`x.y.z`）
- [ ] `status`（值：`Active` / `Draft` / `Deprecated`）
- [ ] `priority`（值：`P0` / `P1` / `P2`）
- [ ] `layer`（值：`L00` 到 `L11` 之一）
- [ ] `owner`

**B. 编码健康检查**
- frontmatter 是否含有乱码（阿拉伯文、俄文字母等）
- 文件是否为 UTF-8 编码

**C. 身份验证**（这真的是一个蓝图吗？）
- 正文是否包含：架构图/接口定义/数据模型/技术规格中的至少一项？
- 是否有明确的"系统描述某个功能模块"的主题？

对每个文件输出检查结果表格：
| 文件 | module_id | version | priority | layer | 编码 | 身份验证 | 问题 |
|------|-----------|---------|---------|-------|------|---------|------|

---

## 第四步：层级纠正（修正 layer 误标）

ZephyrAlpha 系统层级对照表：

| Layer 代码 | 层级名称 | 典型模块 |
|-----------|---------|---------|
| L00 | 基础设施层 | 数据库、消息队列、服务注册 |
| L01 | 数据采集层 | 行情数据源、历史数据下载 |
| L02 | 数据预处理层 | 清洗、对齐、填充缺失 |
| L03 | 因子计算层 | 技术指标、基本面因子 |
| L04 | ML/AI 模型层 | 预测模型、异常检测 |
| L05 | 信号生成层 | Alpha 信号、因子合成 |
| L06 | 组合构建层 | 组合优化、权重分配 |
| L07 | 风险管理层 | 风险敞口、止损规则 |
| L08 | 执行层 | 订单管理、交易路由 |
| L09 | 监控告警层 | 性能监控、异常告警 |
| L10 | 人机界面层 | 仪表盘、API、报表 |
| L11 | 治理合规层 | 审计、合规检查 |

对 layer 字段值为 `layer_01`（已知误标模式）或其他不符合 L00-L11 格式的文件，根据文件内容推断正确层级并修正。

---

## 第五步：价值评估

对每个蓝图，填写以下评估表（用于决定处置方式）：

| 维度 | 评分（是/否/部分）|
|------|-----------------|
| Phase 2 施工直接需要？ | |
| 有唯一的设计决策（其他文件没有的）？ | |
| 有可执行的技术规格（接口定义/数据模型）？ | |
| 与已存在的其他文件完全重复？ | |

**评级规则：**
- P0：3 个"是" → 必须保留，优先迁移到 `docs/03_BLUEPRINTS/`
- P1：2 个"是" → 应该保留，迁移到 `docs/03_BLUEPRINTS/`
- P2：1 个"是" → 提取知识条目后可归档
- P3：全部"否"或完全重复 → 提取知识条目（如有）后删除

---

## 第六步：处置执行

### 对 P0/P1 蓝图（当场迁移）

> **理由**：P0/P1 是"搬家"不是"删除"，git 完全可回滚，立即执行让系统越来越整洁。

1. 修正 frontmatter（补全缺失字段，修正 layer 为 L00-L11 格式）
2. 确认目标目录存在：`docs/03_BLUEPRINTS/L{XX}_{LAYER_NAME}/`
3. 执行迁移：
   ```powershell
   git mv "旧路径/文件.md" "docs/03_BLUEPRINTS/L{XX}_{LAYER}/文件.md"
   ```
4. **⚠️ 立即验证（每步操作后必须执行）**：
   ```powershell
   Test-Path "旧路径/文件.md"                          # 必须输出 False
   Test-Path "docs/03_BLUEPRINTS/L{XX}.../文件.md"     # 必须输出 True
   git status --short | Select-String "文件名"          # 必须出现 R 重命名记录
   ```
   验证失败 → 立即停止，报告给用户，不处理下一个文件。

---

### 对 P2/P3 蓝图（登记决策表，延迟执行）

> **理由**：P2 归档和 P3 删除都是"丢弃"决策，需要人工复查后统一执行。

**决策表文件**：`docs/09_AUDIT/STATE/blueprint-decision-table.md`

如果文件不存在，先创建：

```markdown
---
title: "蓝图决策表 - P2/P3 待裁决"
status: collecting
created_date: {今天日期}
note: "P2（归档）和 P3（删除）候选文件。所有 wave 扫描完成后，经 Kimi×2 复查 + Claude 裁决后统一执行。"
---

# Blueprint Decision Table

| 序号 | 文件路径 | module_id | Layer | P级 | 处置方式 | 目标路径 | 判定理由 | 重复文件 | 知识条目 | 波次 | 日期 |
|------|---------|----------|-------|-----|---------|---------|---------|---------|---------|------|------|
```

每个 P2/P3 蓝图追加一行：

| 字段 | 填写规则 |
|------|---------|
| 序号 | 全局递增，读取当前表中最大序号 +1 |
| 文件路径 | 完整相对路径 |
| module_id | frontmatter 中的值，无则填 `-` |
| Layer | 判定后的正确 Layer |
| P级 | `P2` 或 `P3` |
| 处置方式 | P2: `archive` / P3: `delete` |
| 目标路径 | P2: `docs/06_ARCHIVE/bp-archived-{YYYYMMDD}-{文件名}` / P3: `-` |
| 判定理由 | 一句话说明为什么 P2 或 P3 |
| 重复文件 | P3 必填（重复文件的完整路径）；P2 填 `-` |
| 知识条目 | 已提取填 `KE-{编号}`，否则填 `-` |
| 波次 | BP Wave 编号 |
| 日期 | 今天日期 |

**⚠️ P3 条目额外要求**：在表格行后追加详情块（供 Kimi 复查用）：

```markdown
### P3 详情 - {序号}: {文件名}
- 重复度估算：{百分比}（与哪个文件重复）
- 引用检查：`Select-String -Path "docs" -Filter "*.md" -Pattern "{文件名不含路径}" -Recurse | Measure-Object` 结果：{N 个引用}
- 是否有独立设计价值：{是/否，说明}
- Trae 建议：删除 / 建议再次确认
```

### 知识条目格式

```yaml
---
module_id: KE-{三位数序号}
title: "{简洁标题}"
category: blueprint_decision
source_file: "{原始蓝图路径}"
extracted_date: "{今天日期}"
version: "1.0.0"
status: Active
layer: L{层编号}
owner: ZephyrAlpha-Owner
---

## 核心设计决策

{1-3 条具体的设计决策，每条一行}

## 关键接口/数据模型（如有）

{简洁描述关键接口或数据结构}

## 技术选型理由（如有）

{为什么选择这个方案而不是其他方案}

## 参考来源

- 原始蓝图：{路径}
```

---

## 第七步：注册表更新

更新 `docs/02_ARCHITECTURE/BLUEPRINT_DOMAIN_INVENTORY.yaml`：
- 将已迁移的蓝图状态改为 `migrated`，并填写 `migrated_to` 字段
- 将已删除的蓝图状态改为 `deleted`，并填写 `deleted_date` 和 `deletion_reason`
- 将已归档的蓝图状态改为 `archived`，并填写 `archived_to` 字段

---

## 第八步：Commit 前核对 + Commit

**⚠️ 在执行 `git commit` 之前，必须先运行以下核对命令：**

```powershell
# 核对 1：确认本次 session 实际产生的变更（与第一步基线对比）
git status --short

# 核对 2：确认每个声称已操作的文件确实出现在 git status 中
# 如果某个文件"不在 git status 中"，则该操作未完成，不得写入汇报成果
```

**只有在 `git status` 中实际出现的变更，才能写入汇报成果和 Session Log。**

**本 session 允许 commit 的文件类型**：
- `docs/03_BLUEPRINTS/` 下新增文件（P0/P1 迁移）
- `docs/08_KNOWLEDGE/KE-*.md`（新增知识条目）
- `docs/09_AUDIT/STATE/blueprint-decision-table.md`（P2/P3 决策登记）
- `docs/09_AUDIT/STATE/elimination-pipeline-tracker.yaml`（进度更新）
- `docs/09_AUDIT/STATE/SESSION_LOGS/session-*.md`（session 日志）

**⚠️ 不允许出现的变更（出现则停止报告）**：
- `docs/06_ARCHIVE/` 下新增文件（P2 归档在 Phase 2 才执行）
- 任何蓝图文件的 `D`（删除）记录（P3 删除在 Phase 2 才执行）

每处理完 5-10 个蓝图执行一次 commit：

```powershell
git add -A
git commit -m "chore(blueprint): {BP Wave} - migrate P0/P1, register P2/P3 for review

- Migrated (P0/P1): M files -> docs/03_BLUEPRINTS/
- Registered for review (P2): A files in decision table
- Registered for review (P3): D files in decision table
- Knowledge entries extracted: K"
```

---

## 第九步：更新追踪文件和 Session Log

1. 更新 `docs/09_AUDIT/STATE/elimination-pipeline-tracker.yaml`：
   - 对应 BP Wave 的进度数字
   - sessions 列表追加本次记录

2. 创建 Session Log（`docs/09_AUDIT/STATE/SESSION_LOGS/session-{YYYYMMDD}-bp-{NNN}.md`）：

```markdown
---
session_id: "{YYYYMMDD}-bp-{NNN}"
pipeline: "blueprint_safety"
wave: "{BP Wave编号}"
model: "{使用的模型}"
date: "{今天日期}"
---

## 本次完成
- 扫描蓝图数：N
- 迁移执行（P0/P1）：M 个 → docs/03_BLUEPRINTS/
- 登记待裁决（P2）：A 个 → decision table
- 登记待裁决（P3）：D 个 → decision table
- 提取知识条目：K 个

## 已迁移文件（P0/P1，本次已执行）
| 原路径 | 目标路径 | P级 | 理由 |
|--------|---------|-----|------|
| ... | docs/03_BLUEPRINTS/... | P0 | ... |

## 登记待裁决文件（P2/P3，等待 Phase 2）
| 序号 | 文件路径 | P级 | 判定理由 |
|------|---------|-----|---------|

## 提取的知识条目
| KE-ID | 来源蓝图 | 知识类别 |
|-------|---------|---------|

## 未完成（继续点）
- 下一次从文件 {文件名} 开始
- 剩余蓝图数：{数字}
- 决策表当前 P2/P3 行数：{数字}
```

---

## 异常处理规则

**遇到以下情况时，立即停止并报告给用户：**
1. 蓝图在锚点文件列表中
2. 蓝图有 >3 次搬迁历史
3. 蓝图的 `module_id` 与现有代码 (`src/`) 中的模块直接对应（删除可能导致施工图断链）
4. 两个重复副本内容差异 >30%（无法确定保留哪个时）
5. 编码损坏无法读取内容

**⚠️ pre-commit hook 失败的处理规则（必须遵守）：**

- 如果 `git commit` 失败，错误信息是"断链数超过阈值" → **直接用 `--no-verify` 重新提交，在 message 末尾加 `PRECOMMIT-SKIP: pre-existing broken links`，绝对不要运行 `fix_dead_links.py`**
- 如果失败原因是"重复 module_id 超过阈值" → 停止，报告给用户处理
- PowerShell 没有 `head` 命令，用 `Select-Object -First N` 代替
- PowerShell 没有 `grep` 命令，用 `Select-String -Pattern "..." -Path "..."` 代替

**报告格式：**
"BLOCKER：发现异常情况，停止本次处理。
原因：{具体原因}
影响蓝图：{文件路径}
建议操作：{给用户的建议}"
```

## 【SESSION PROMPT】结束（复制到这里）

---

## 使用指南

### 如何填写占位符

| 占位符 | 填写内容 | 示例 |
|--------|---------|------|
| `{BP Wave 编号}` | 当前执行的蓝图波次 | `BP Wave 1` |
| `{BP Wave 名称}` | 波次名称 | `01_FRAMEWORK 中非蓝图文件分流` |
| `{目标目录路径}` | 要处理的目录 | `docs/01_FRAMEWORK/` |
| `{YYYYMMDD}` | 今天日期 | `20260417` |
| `{NNN}` | 当日 session 序号 | `001` |

### 快速参考：各 BP Wave 的关键参数

| BP Wave | 目标目录 | 文件数 | 核心操作 |
|---------|---------|--------|---------|
| BP Wave 1 | `docs/01_FRAMEWORK/` | ~40 | 识别非蓝图文件，移交文件消除流水线 |
| BP Wave 2 | `docs/01_FRAMEWORK/` + `docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/` | ~163 | 重叠蓝图去重合并 |
| BP Wave 3 | `docs/01_FRAMEWORK/` | ~130 | 修正 layer 字段，迁移到 `docs/03_BLUEPRINTS/` |
| BP Wave 4 | `docs/10_AI_WORKFLOW/` + `docs/08_HUMAN_AI_INTERFACE/` + 其他 | ~100 | 评估是否需要迁移 |

### 建议执行顺序

- **BP Wave 1** 应与文件消除流水线 **Wave 5** 同步执行
- **BP Wave 2** 应与文件消除流水线 **Wave 6** 同步执行
- **BP Wave 3** 可独立执行，是纯迁移操作
- **BP Wave 4** 最后执行，工作量最小

### 知识条目 module_id 分配

每次 session 开始前，**执行以下命令**获取当前最大编号（不要假设起始值）：

```powershell
Get-ChildItem -Path docs/08_KNOWLEDGE -Recurse -Filter "KE-*.md" | Select-Object Name | Sort-Object Name -Descending | Select-Object -First 5
```

从当前最大编号 +1 开始分配。若无 KE- 格式文件，从 `KE-001` 开始。

### 知识入库子目录对照

| 知识类别 | 写入子目录 |
|---------|----------|
| `blueprint_decision` | `docs/08_KNOWLEDGE/BEST_PRACTICES/` |
| `strategy` | `docs/08_KNOWLEDGE/STRATEGY_LIBRARY/` |
| `factor` | `docs/08_KNOWLEDGE/FACTOR_LIBRARY/` |
| `best_practice` | `docs/08_KNOWLEDGE/BEST_PRACTICES/` |
| `lesson_learned` | `docs/08_KNOWLEDGE/BEST_PRACTICES/` |

---

---

## Phase 2：P2/P3 全量裁决流程

> **设计原则**：P0/P1 当场迁移（可 git 回滚）。P2 归档和 P3 删除都是"丢弃"决策，需要人工复查后统一执行。

```
【触发条件】：所有 BP Wave 的 Phase 1 扫描全部完成
             → elimination-pipeline-tracker.yaml 中所有 bp_wave 状态均为 in_progress 或 completed
             → blueprint-decision-table.md 中已收集全部 P2/P3 条目

阶段一：Kimi 第一轮复查（使用下方 Kimi-Review-1 Prompt）
  ↓ 读取 blueprint-decision-table.md
  ↓ 逐条审核 P2（归档是否合理？）和 P3（删除是否安全？）
  ↓ 在文件中追加 [KIMI-REVIEW-1] 标记

阶段二：Kimi 第二轮复查（新对话，不看第一轮结论）
  ↓ 独立审核原始决策表（忽略 KIMI-REVIEW-1 标记）
  ↓ 在文件中追加 [KIMI-REVIEW-2] 标记

阶段三：Claude 最终裁决（在 Cursor 中执行）
  P2 归档：
    两轮均同意 → 执行 git mv 到 docs/06_ARCHIVE/
    有分歧    → 标记 [DISPUTED-P2]，提示用户手动决定
    两轮均反对 → 保留原文件，标记 [KEEP]

  P3 删除：
    两轮均同意 → 执行 git rm（最后安全检查：引用数 = 0）
    有分歧    → 降级为 P2，执行归档
    两轮均反对 → 降级为 P2，执行归档
```

---

### Kimi 第一轮复查 Prompt（Kimi-Review-1）

```
你是 ZephyrAlpha 项目蓝图安全审核员（第一轮复查）。

ZephyrAlpha 是个人量化交易系统，目前处于 Phase 2 施工前准备阶段（进行系统瘦身）。

请读取文件：docs/09_AUDIT/STATE/blueprint-decision-table.md

对其中每一条 P2（归档）和 P3（删除）条目，独立审核：

**P2 归档审核标准**：
1. 该文件真的是"低价值，可归档"吗？还是它其实含有 Phase 2 施工需要的设计细节？
2. 判定理由是否具体充分？（"仅有高层概念无技术规格"是具体理由；"不重要"不是）
3. 归档后如果将来发现有用，找回成本低吗？（docs/06_ARCHIVE/ 仍在 git 中，成本低）

**P3 删除审核标准**：
1. 判定理由是否充分？（"完全重复"需要有重复文件路径；"空壳"需要内容确实为空）
2. 列出的重复文件是否真实存在于当前仓库？（替代文件不存在 → 必须反对删除）
3. 引用检查结果是否为 0？（有引用未处理 → 必须反对删除）
4. 这个蓝图的 module_id 是否在 src/ 代码中被引用？

对每条条目，在文件的对应行后追加审核标注：

[KIMI-REVIEW-1]
P级: P2 / P3
结论: ✓ 同意执行 / ✗ 反对执行
理由: {一句话说明}

最后输出统计：
- P2 同意归档：N 条 / 反对：N 条
- P3 同意删除：N 条 / 反对：N 条（列出文件名）
- 需要用户确认：N 条
```

---

### Kimi 第二轮复查 Prompt（Kimi-Review-2）

```
你是 ZephyrAlpha 项目蓝图安全审核员（第二轮独立复查）。

ZephyrAlpha 是个人量化交易系统，目前处于 Phase 2 施工前准备阶段。

请读取文件：docs/09_AUDIT/STATE/blueprint-decision-table.md

⚠️ 重要：忽略文件中已有的 [KIMI-REVIEW-1] 标记，完全独立作出判断。

**第二轮审核的不同视角**：
1. 这个蓝图在未来 6-12 个月内（Phase 2 施工期）是否可能被重新需要？
2. P2 文件：归档后如有 5% 的独特内容，是否会影响施工决策？
3. P3 文件：重复文件是否"完全覆盖"了该蓝图？还是有 10-20% 独立内容？
4. 如果将来发现判断错误，恢复的代价是多少？

对每条条目追加：

[KIMI-REVIEW-2]
P级: P2 / P3
结论: ✓ 同意执行 / ✗ 反对执行
理由: {一句话说明}
风险: 低 / 中 / 高

最后统计并与第一轮对比：
- P2 两轮均同意归档：N 条 → 建议 Claude 执行归档
- P2 有分歧：N 条 → 建议 Claude 提交用户裁决
- P3 两轮均同意删除：N 条 → 建议 Claude 执行删除
- P3 有分歧或两轮均反对：N 条 → 建议降级为 P2 归档
```

---

### Claude 最终裁决 Prompt（在 Cursor 中使用）

```
你是 ZephyrAlpha 项目蓝图最终裁决者。

请读取文件：docs/09_AUDIT/STATE/blueprint-decision-table.md

根据 [KIMI-REVIEW-1] 和 [KIMI-REVIEW-2] 标记，按以下规则执行：

**P2 归档裁决**：
- 两轮均 ✓ → 执行 git mv 到 docs/06_ARCHIVE/bp-archived-{YYYYMMDD}-{文件名}
  验证：Test-Path "原路径" 必须输出 False
- 有分歧 → 标记 [DISPUTED-P2]，输出给用户手动决定，不执行
- 两轮均 ✗ → 标记 [KEEP]，不归档，原文件保留

**P3 删除裁决**：
- 两轮均 ✓ → 执行最后安全检查，再执行 git rm：
  Select-String -Path "docs" -Filter "*.md" -Pattern "{文件名不含路径}" -Recurse | Measure-Object
  引用数 > 0 → 降级为 [DISPUTED-P3]
  引用数 = 0 → 执行 git rm，验证 Test-Path 输出 False
- 有分歧 → 降级为 P2，执行归档（git mv 到 docs/06_ARCHIVE/）
- 两轮均 ✗ → 降级为 P2，执行归档

执行完成后：
1. 在 blueprint-decision-table.md 末尾追加 [CLAUDE-FINAL] 执行摘要
2. 更新 docs/09_AUDIT/STATE/elimination-pipeline-tracker.yaml
3. 将 blueprint-decision-table.md 的 status 改为 completed
4. 执行统一 commit：
   git commit -m "chore(blueprint): Phase 2 execution - archive P2, delete P3 after dual Kimi review

- Archived (P2): A files -> docs/06_ARCHIVE/
- Deleted (P3): D files
- Disputed (manual): N files
- Kept (both Kimi rejected): N files"
```

---

### 裁决文件位置

**Phase 1 收集期**（所有 BP Wave 扫描期间持续追加）：
```
docs/09_AUDIT/STATE/blueprint-decision-table.md
```

**Phase 2 完成后**，该文件归档到：
```
docs/09_AUDIT/REPORTS/ARCHIVE/blueprint-decision-table-{YYYYMMDD}-final.md
```

*本 Prompt 模板由 ZephyrAlpha Owner 维护。如需修改，更新本文件并同步 AGENTS.md 第六章。*
