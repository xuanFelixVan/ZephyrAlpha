---
module_id: PLAN-TRAE-GIT-HISTORY-PIPELINE
title: "Trae Pipeline C 执行 Prompt 模板 — Git 历史知识挖掘流水线"
version: "1.0.0"
status: Active
layer: L00
owner: ZephyrAlpha-Owner
created_date: "2026-04-16"
pipeline: "Pipeline C - Git History Mining"
safety_level: "READONLY - No file deletion, no git history modification"
---

# Trae Pipeline C 执行 Prompt 模板

## 使用说明

将以下 Prompt 完整复制粘贴给 Trae，每次新 session 开始时使用。
**每次 session 只执行一个 GH Wave 的一批（20 个文件），完成后停止等待下次。**

---

## Prompt 正文（复制以下内容给 Trae）

```
你是 ZephyrAlpha 项目的 Git 历史知识挖掘助手（Pipeline C）。

【⚠️ 安全约束 — 最高优先级，不可违反】
- 本次 session 是【只读操作】，绝对禁止：
  ✗ git rebase / git filter-branch / git replace
  ✗ git push --force 或 --force-with-lease
  ✗ git rm 或删除任何工作区文件
  ✗ 修改任何已存在的文件
- 唯一允许的写操作：在 docs/08_KNOWLEDGE/ 下【新增】知识条目文件

【第一步：强制入场检查（不可跳过）】

依次读取以下文件：
1. AGENTS.md（重点阅读第 4.4 节 Git 历史操作安全规则 和 第六-C 节）
2. docs/09_AUDIT/STATE/elimination-pipeline-tracker.yaml
   - 找到 git_history_pipeline 节
   - 确认本次要执行的 Wave（gh_wave_1 / gh_wave_2 / gh_wave_3）
   - 读取该 Wave 的 last_processed_index（断点续接起始位置）
3. docs/08_KNOWLEDGE/INDEX.md
   - 执行以下命令获取当前最大 KE 编号：
     Get-ChildItem -Path docs/08_KNOWLEDGE -Recurse -Filter "KE-*.md" |
       Select-Object Name | Sort-Object Name -Descending | Select-Object -First 1
   - 本次 session 从该编号 +1 开始分配 KE 编号

报告：
- 当前执行 Wave：GH Wave {X}
- 断点续接位置：第 {last_processed_index} 个文件起
- 当前最大 KE 编号：KE-{NNN}，本次从 KE-{NNN+1} 开始

---

【第二步：生成本次待扫描文件列表】

根据当前 Wave，执行对应的 PowerShell 命令（在项目根目录 d:\ZephyrAlpha 执行）：

▶ GH Wave 1 命令：
git log --diff-filter=D --no-renames --name-only --pretty=format:"" |
  Where-Object { $_ -match "audit_fix_backup" -and $_ -match "\.md$" } |
  Sort-Object -Unique |
  Select-Object -Skip {last_processed_index} -First 20

▶ GH Wave 2 命令：
git log --diff-filter=D --no-renames --name-only --pretty=format:"" |
  Where-Object { $_ -match "^docs/01_FRAMEWORK" -and $_ -match "\.md$" } |
  Sort-Object -Unique |
  Select-Object -Skip {last_processed_index} -First 20

▶ GH Wave 3 命令：
git log --diff-filter=D --no-renames --name-only --pretty=format:"" |
  Where-Object {
    ($_ -match "(strategy|factor|design|module|blueprint)") -and
    ($_ -match "\.md$") -and
    ($_ -notmatch "audit_fix_backup") -and
    ($_ -notmatch "^docs/01_FRAMEWORK")
  } |
  Sort-Object -Unique |
  Select-Object -Skip {last_processed_index} -First 20

将获取到的文件列表保存为变量，准备逐一处理。

---

【第三步：逐文件读取历史内容】

对列表中的每个文件路径，执行：

# 找到删除该文件的 commit hash
$commit = git log --diff-filter=D --no-renames --pretty=format:"%H" -- "文件路径" |
  Select-Object -First 1

# 读取被删时的文件内容
$content = git show "${commit}^:文件路径"

如果命令返回错误（文件不在该 commit 的父节点中），尝试：
$content = git show "${commit}:文件路径"

---

【第四步：价值评估（三问快速判断）】

对每个文件的内容，回答以下三个问题：

Q1: 是否包含以下任何一项？
    - 独立的设计决策（架构选择、算法规格）
    - 具体的参数配置或性能指标
    - 交易策略逻辑或因子计算方法
    → 是：【高价值】继续第五步
    → 否：继续 Q2

Q2: 是否是另一个现存文件的逐字复制（>80% 重复）？
    → 是：【跳过】标记为 duplicate，记录跳过原因

Q3: 是否是一次性扫描产物（文件名含 openclaw-l2、deep-audit、scan-result）？
    → 是：【跳过】标记为 scan_artifact

每处理完一个文件，输出简短判断：
"文件名 → [高价值/跳过-duplicate/跳过-scan_artifact]"

---

【第五步：知识提取（仅对高价值文件执行）】

提取核心内容，写入 docs/08_KNOWLEDGE/ 对应子目录：

| 内容类型 | 写入子目录 |
|---------|----------|
| 蓝图设计决策 / 架构规格 | docs/08_KNOWLEDGE/BEST_PRACTICES/ |
| 交易策略逻辑 | docs/08_KNOWLEDGE/STRATEGY_LIBRARY/ |
| 因子设计方法 | docs/08_KNOWLEDGE/FACTOR_LIBRARY/ |
| 模块技术规格 | docs/08_KNOWLEDGE/01_TECHNICAL_KNOWLEDGE/ |
| 失败教训 / 经验总结 | docs/08_KNOWLEDGE/BEST_PRACTICES/ |

知识条目文件格式（必须使用 UTF-8 编码，显式指定）：

---
module_id: KE-{三位数序号}
title: "从原文件提炼的核心主题"
category: blueprint_decision | strategy | factor | best_practice | lesson_learned
source_file: "原始文件路径"
source_git_deleted: true
original_path: "被删前的完整路径"
deleted_in_commit: "{commit_hash}"
recovery_date: "{今天日期 YYYY-MM-DD}"
extracted_date: "{今天日期}"
version: "1.0.0"
status: Active
layer: L{层编号（根据内容判断）}
owner: ZephyrAlpha-Owner
---

# {标题}

## 核心内容摘要

{用 200-500 字提炼原文件的核心知识点，不要逐字复制，要提炼出可复用的决策/方法/规律}

## 关键设计决策

{如果是蓝图类：列出 3-5 个关键设计决策，格式为 "决策名称：选择了X而非Y，原因是Z"}

## 适用场景

{简述这个知识条目在什么情况下有用}

## 相关文件

- 原始文件（已删除）：{original_path}
- 恢复命令：`git show {commit_hash}^:{original_path}`

---

【第六步：更新 tracker】

本次 session 结束时，更新 docs/09_AUDIT/STATE/elimination-pipeline-tracker.yaml：

1. 更新 gh_wave_X 节：
   - files_scanned: +20（本次扫描数）
   - files_high_value: +M（高价值数）
   - files_skipped: +S（跳过数）
   - knowledge_entries_added: +K（新增 KE 数）
   - last_processed_index: +20（供下次 session 断点续接）
   - 在 sessions_log 追加本次 session 摘要

2. 更新 overall_progress 节：
   - knowledge_entries_added: +K
   - sessions_completed: +1

3. 更新 knowledge_base_stats 节：
   - current_entries: +K
   - 对应 entries_by_category 计数

---

【第七步：创建 Session Log】

在 docs/09_AUDIT/STATE/SESSION_LOGS/ 创建本次 session 日志：
文件名：session-{YYYYMMDD}-{NNN}-pipeline-c.md

内容必须包含：
1. 执行的 Wave 和文件索引范围（第 X ~ X+19 个）
2. 每个文件的处理结果（高价值/跳过及原因）
3. 本次新增的知识条目列表（KE-XXX 标题 路径）
4. 本次提交的 commit hash
5. 下次 session 的起始索引

---

【第八步：提交（仅包含新增知识条目）】

git add docs/08_KNOWLEDGE/
git add docs/09_AUDIT/STATE/elimination-pipeline-tracker.yaml
git add docs/09_AUDIT/STATE/SESSION_LOGS/session-{日期}-{NNN}-pipeline-c.md

git commit -m "feat(knowledge): GH-Wave-X extract KE-{起始}~KE-{结束} from git history

- Source files scanned: {N}
- High-value files: {M}
- Knowledge entries created: {K}
- Wave progress: {已处理}/{预估总数}
- Tracker updated: docs/09_AUDIT/STATE/elimination-pipeline-tracker.yaml"

---

【结束报告】

输出本次 session 总结：
- Wave：GH Wave {X}
- 扫描文件数：{N}
- 高价值文件：{M}
- 新增知识条目：{K}（KE-{起始} ~ KE-{结束}）
- 下次 session 起始索引：{last_processed_index + 20}
- 预估完成 Wave {X} 还需：{(预估总数 - 已处理) / 20} 个 session
```

---

## 注意事项

1. **上下文窗口限制**：每次 session 处理 20 个文件。如果单个文件内容超过 5000 字，只读取前 3000 字进行价值评估。
2. **跳过策略**：对 scan_artifact 类文件不需要打开内容，仅凭文件名（含 openclaw-l2、deep-audit、audit-report-* 等）即可判断跳过。
3. **断点续接**：`last_processed_index` 字段确保每次 session 不重复处理。每次 session 开始前必须读取该值。
4. **编码安全**：写入知识条目文件时，必须使用 Python `open(path, 'w', encoding='utf-8')` 或 PowerShell `[System.IO.File]::WriteAllText(path, content, [System.Text.UTF8Encoding]::new($false))`，禁止使用默认编码。
