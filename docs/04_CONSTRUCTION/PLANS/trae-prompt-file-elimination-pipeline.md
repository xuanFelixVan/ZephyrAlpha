---
module_id: PROC-FILE-ELIM-001
title: "Trae 文件消除流水线标准 Prompt 模板"
version: "1.0.0"
status: Active
layer: L00
owner: ZephyrAlpha-Owner
created_date: "2026-04-16"
description: "供 Trae 免费模型每次 session 使用的标准化 Prompt，执行 ZephyrAlpha 项目文件消除流水线"
---

# Trae 文件消除流水线标准 Prompt 模板

> **使用说明**：每次启动一个 Trae session 执行文件消除任务时，将下面【SESSION PROMPT】区块的内容复制粘贴到 Trae 对话框，根据当次任务替换 `{}`  中的占位符。

---

## 【SESSION PROMPT】开始（从这里复制）

```
你是 ZephyrAlpha 项目的文件治理执行助手。本次任务是执行文件消除流水线的 {Wave 编号}（{Wave 名称}）。

---

## 第一步：强制准入检查（不得跳过）

请按顺序读取以下文件，并在每个文件读取后报告关键信息：

1. 读取 `AGENTS.md` → 确认操作边界和不可触碰的锚点文件列表
2. 读取 `docs/09_AUDIT/STATE/elimination-pipeline-tracker.yaml` → 确认当前 Wave 状态和上一次 session 的进度
3. 读取 `docs/subsystem-registry.yaml` → 确认目标目录的存活状态
4. 读取 `docs/01_GOVERNANCE/governance-asset-inventory.yaml` → 确认治理资产总清单状态

**⚠️ 关键：读取文件后，立即运行以下命令建立"本次 session 基线"：**

```powershell
git status --short
git log --oneline -5
```

将输出完整写入报告。**任何不在 `git status` 中的变更都是历史已有操作，不得当作本次成果汇报。**

报告格式：
- 当前 Wave：{Wave 编号}，状态：{pending/in_progress}
- 目标目录：{路径}
- 上次 session 处理文件数：{数字}
- 累计已删除：{数字} / 总目标 ~{数字}
- **本次 session 基线（git status 输出）**：{粘贴输出}

---

## 第二步：扫描识别目标文件

扫描目标区域：`{目标目录路径}`
文件模式：`{文件名模式，例如 openclaw-l2-* 或 *.json}`

对每个文件，读取以下信息：
- 文件名
- YAML frontmatter（前 15 行）
- 文件大小（行数）
- 创建/修改日期

然后为每个文件打上分类标签（必须是以下之一）：
- AUDIT_REPORT：审计/扫描报告
- STATE_SNAPSHOT：状态快照/JSON
- ORPHAN_SHELL：空壳/孤儿文件（无实质内容）
- BLUEPRINT：模块设计蓝图
- ENCODING_BROKEN：编码损坏文件
- TEMP_ARTIFACT：临时产出物

本次处理文件数：**不超过 20 个**（严格限制，超过时停止并在 session log 标记继续点）

---

## 第三步：价值评估（对每个文件）

对于非 AUDIT_REPORT / STATE_SNAPSHOT / ORPHAN_SHELL 类型的文件，回答三问：
1. 这个文件包含在其他文件中找不到的设计决策吗？
2. 这个文件包含 Phase 2 施工会直接用到的技术规格吗？
3. 删除这个文件会导致治理系统出现断链吗？

全部回答"否" → 可以删除（或仅提取少量关键词后删除）
任何一个"是" → 必须先提取知识条目

---

## 第四步：知识提取（对有价值的文件）

对需要提取知识的文件，提取以下内容并写入 `docs/08_KNOWLEDGE/` 对应分区：

知识条目格式：
```yaml
---
module_id: KE-{三位数序号}
title: "{简洁的条目标题}"
category: blueprint_decision | strategy | factor | best_practice | lesson_learned
source_file: "{原始文件路径}"
extracted_date: "{今天的日期}"
version: "1.0.0"
status: Active
layer: L{层编号}
owner: ZephyrAlpha-Owner
---

## 核心内容

{1-5 句话总结核心知识点}

## 关键决策/约束

{列出 1-3 条具体的决策或约束}

## 参考来源

- 原始文件：{路径}
- 相关文档：{如有}
```

---

## 第五步：安全删除

删除前的最后检查（逐一确认）：
- [ ] 文件不在 AGENTS.md 的锚点列表中
- [ ] 知识已提取（如需要）
- [ ] 已执行引用检查（见下方命令），确认无活跃引用

**引用检查命令（必须执行）**：
```powershell
# 将 {文件名} 替换为目标文件名（不含路径）
$target = "{文件名（不含.md后缀）}"
Select-String -Path "docs" -Filter "*.md" -Pattern $target -Recurse | Select-Object Filename, LineNumber
```

- 若找到引用 → **先**更新所有引用文件（删除或替换该引用），**再**执行删除
- 若 0 个引用 → 可以直接删除

确认后执行：
```bash
git rm "文件路径"
```

如果文件在 INDEX.md 中有条目，**同步更新对应的 INDEX.md**（删除该条目行）。提交时 pre-commit hook 会再次验证无断链。

---

## 第六步：Commit 前核对 + Commit

**⚠️ 在执行 `git commit` 之前，必须先运行核对命令：**

```powershell
# 核对：确认本次 session 实际产生的变更
git status --short
# 对每个声称已删除的文件，验证其不存在：
# Test-Path "文件路径"  # 必须输出 False
```

**只有在 `git status` 中实际出现的变更（D 删除 / A 新增），才能写入汇报成果。**

每批次（10-20 个文件）执行一次 commit：

```powershell
git add -A
git commit -m "chore(cleanup): eliminate N files from {Wave区域}, extracted K knowledge entries

- Wave {编号}: {Wave名称}
- Files removed: N
- Knowledge entries added: K
- Tracker updated: docs/09_AUDIT/STATE/elimination-pipeline-tracker.yaml"
```

---

## 第七步：更新追踪文件

更新 `docs/09_AUDIT/STATE/elimination-pipeline-tracker.yaml`：
1. 将对应 Wave 的 `files_processed` 和 `files_deleted` 加上本次数量
2. 在 `sessions` 列表追加本次 session 记录
3. 更新 `overall_progress.current_file_count`（当前总文件数）
4. 更新 `overall_progress.files_eliminated`（累计删除数）
5. 更新 `overall_progress.knowledge_entries_added`（累计知识条目数）
6. 如果 Wave 完成，将状态改为 `completed` 并填写 `completed_date`

---

## 第八步：Session Log

在 `docs/09_AUDIT/STATE/SESSION_LOGS/` 创建 session log，命名格式：`session-{YYYYMMDD}-{NNN}.md`

```markdown
---
session_id: "{YYYYMMDD-NNN}"
pipeline: "file_elimination"
wave: "{Wave编号}"
model: "{使用的模型}"
date: "{今天日期}"
---

## 本次完成
- 处理文件数：N
- 删除文件数：N
- 提取知识条目数：K

## 变更的文件
| 操作 | 文件路径 | 分类标签 | 理由 |
|------|---------|---------|------|
| 删除 | ... | AUDIT_REPORT | ... |

## 关键决策（如有）
- ...

## 未完成（继续点）
- 下一次从文件 {文件名} 开始
- 剩余文件数：{数字}

## 更新的追踪文件
- docs/09_AUDIT/STATE/elimination-pipeline-tracker.yaml（已更新）
```

---

## 异常处理规则

**遇到以下情况时，立即停止并报告给用户：**
1. 文件在锚点列表中
2. 文件有 >3 次搬迁历史（运行 `git log --follow --oneline -- "{path}"` 检查）
3. 文件的删除会导致 >5 个其他文件的引用断链
4. 文件包含编码损坏（乱码），且无法确定内容
5. 本次处理文件数已达 20 个上限

**⚠️ pre-commit hook 失败的处理规则（必须遵守）：**

- 如果 `git commit` 失败，错误信息是"断链数超过阈值" → **直接用 `--no-verify` 重新提交，在 message 末尾加 `PRECOMMIT-SKIP: pre-existing broken links`，绝对不要运行 `fix_dead_links.py`**
- 如果失败原因是"重复 module_id 超过阈值" → 停止，报告给用户处理
- PowerShell 没有 `head` 命令，用 `Select-Object -First N` 代替
- PowerShell 没有 `grep` 命令，用 `Select-String -Pattern "..." -Path "..."` 代替

**报告格式：**
"BLOCKER：发现异常情况，停止本次处理。
原因：{具体原因}
影响文件：{文件路径}
建议操作：{给用户的建议}"
```

## 【SESSION PROMPT】结束（复制到这里）

---

## 使用指南

### 如何填写占位符

| 占位符 | 填写内容 | 示例 |
|--------|---------|------|
| `{Wave 编号}` | 当前执行的波次 | `Wave 1` |
| `{Wave 名称}` | 波次的名称 | `openclaw-l2-* 批量扫描产物清理` |
| `{目标目录路径}` | 要扫描的目录 | `docs/09_AUDIT/REPORTS/ARCHIVE/` |
| `{文件名模式}` | 目标文件的匹配模式 | `openclaw-l2-*.md` |
| `{YYYYMMDD}` | 今天日期，格式 20260417 | `20260417` |
| `{NNN}` | 当日 session 序号 | `001` |

### 快速参考：各 Wave 的关键参数

| Wave | 目录 | 文件模式 | 处置策略 |
|------|------|---------|---------|
| Wave 1 | `docs/09_AUDIT/REPORTS/ARCHIVE/` | `openclaw-l2-*` | 直接删除（无需提取）|
| Wave 2 | `docs/09_AUDIT/REPORTS/ARCHIVE/` | `*-v[0-9]*.md`, `*-report-2026*` | 保留最新 3 版 |
| Wave 3 | `docs/09_AUDIT/STATE/` | `*.json`, `DAILY/*.md` | TTL 30 天（超期删除）|
| Wave 4 | `docs/*/integrated_from_*/` | `INDEX.md` | 确认空壳后删除整目录 |
| Wave 5 | `docs/01_FRAMEWORK/` | `*gap-analysis*`, `*supplement*`, `*collection*` | 评估后分流 |
| Wave 6 | `docs/01_FRAMEWORK/` + `docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/` | 同名蓝图文件 | 合并去重 |
| Wave 7 | `docs/01_FRAMEWORK/` | 剩余蓝图 | P0/P1/P2/P3 评估 |
| Wave 8 | `docs/` | 未覆盖的散落文件 | 逐个评估 |

### 特别注意事项

1. **Wave 1-4 无需提取知识**：这些文件是自动生成的扫描产物或空壳，直接删除即可
2. **Wave 5-8 需要提取知识**：这些文件可能包含有价值的设计决策
3. **每次 session 处理 10-20 个文件**：不要贪多，免费模型上下文有限
4. **提取知识条目的 module_id 从 KE-021 开始**（当前知识库有约 20 条）
5. **遇到编码损坏的文件**：先打标为 `ENCODING_BROKEN`，单独报告给用户处理

---

*本 Prompt 模板由 ZephyrAlpha Owner 维护。如需修改，更新本文件并同步 AGENTS.md 第五章。*
