---
module_id: PROC-WAVE1-OPENCLAW-001
title: "Wave 1 永久可复用指令 - openclaw-l2 清理"
version: "1.0.0"
status: Active
note: "每次复制【SESSION PROMPT】区块内容粘贴给 Trae，无需修改任何数字，自动断点续接"
---

# Wave 1 永久可复用指令（openclaw-l2 清理）

> 每次复制下方【SESSION PROMPT】区块全部内容，粘贴给 Trae 即可。
> 不需要修改任何数字——Trae 会自动从 tracker 读取上次进度。

---

## 【SESSION PROMPT】开始（从这里复制到结束标记）

```
你是 ZephyrAlpha 项目的文件治理执行助手。
本次任务：执行文件消除流水线 Wave 1（openclaw-l2-* 批量扫描产物清理）。

---

## 第一步：强制准入检查

按顺序读取以下文件：
1. AGENTS.md → 记下锚点文件列表
2. docs/09_AUDIT/STATE/elimination-pipeline-tracker.yaml → 读取 wave_1.files_processed 作为本次起始偏移
3. docs/subsystem-registry.yaml → 确认目录存活

立即建立本次 session 基线：

git status --short
git log --oneline -3

将输出完整写入报告。**任何不在 git status 中的变更，不得当作本次成果汇报。**

从 tracker 自动读取断点（复制以下命令执行，不要手填数字）：

$yaml = Get-Content "docs/09_AUDIT/STATE/elimination-pipeline-tracker.yaml"
$idx = ($yaml | Select-String "^  wave_1:" | Select-Object -First 1).LineNumber
$skipLine = $yaml[$idx..($idx+5)] | Select-String "files_processed:" | Select-Object -First 1
$skipCount = [int]($skipLine.Line.Trim() -replace "files_processed:\s*(\d+).*", '$1')
Write-Host "本次从第 $($skipCount+1) 个文件开始（Skip $skipCount）"

报告格式：
- 当前 Wave：Wave 1，状态：in_progress
- 上次已处理：$skipCount 个文件
- 本次从第 $($skipCount+1) 个继续
- 基线（git status 输出）：{粘贴输出}

---

## 第二步：获取本批次目标文件

$files = Get-ChildItem "docs/09_AUDIT/REPORTS/ARCHIVE/" -Filter "openclaw-l2-*" |
  Sort-Object Name |
  Select-Object -Skip $skipCount -First 20

$files | Select-Object Name, @{N="KB";E={[math]::Round($_.Length/1KB,1)}}

如果 $files 为空 → 报告"Wave 1 已全部完成"，将 tracker 中 wave_1.status 改为 completed，跳到第七步。

这些文件全部分类为：TEMP_ARTIFACT（自动批量扫描产物，0 知识价值）
→ 跳过第三步、第四步，直接执行第五步。

---

## 第三步 & 第四步：跳过

openclaw-l2-* 为机器自动生成的扫描产物，无独立知识价值，无需评估，无需提取知识条目。

---

## 第五步：安全删除

对 $files 中的每个文件，执行删除前引用检查，然后删除：

foreach ($f in $files) {
    $name = $f.BaseName
    $refs = Select-String -Path "docs" -Filter "*.md" -Pattern $name -Recurse |
            Where-Object { $_.Path -notmatch [regex]::Escape($f.FullName) }
    if ($refs.Count -gt 0) {
        Write-Host "SKIP（有引用）: $($f.Name) → $($refs.Count) 处引用"
    } else {
        git rm "docs/09_AUDIT/REPORTS/ARCHIVE/$($f.Name)"
        $check = Test-Path "docs/09_AUDIT/REPORTS/ARCHIVE/$($f.Name)"
        Write-Host "已删除: $($f.Name) | Test-Path=$check（必须为 False）"
    }
}

顺带执行（本次 session 一并清账，只需执行一次，之后无需重复）：

$pending = git status --short | Select-String "^ D \.audit_fix_backup/"
if ($pending) {
    Write-Host "发现 $($pending.Count) 条 .audit_fix_backup 待提交删除，一并暂存"
    git add ".audit_fix_backup/"
} else {
    Write-Host ".audit_fix_backup 已清账，跳过"
}

---

## 第六步：Commit 前核对 + Commit

git status --short

确认：
- 已删除文件出现 D 记录 ✓
- 不应出现任何非 docs/09_AUDIT/ 或 .audit_fix_backup/ 的意外变更

提交：

$deleted = (git status --short | Select-String "^D").Count
git add "docs/09_AUDIT/REPORTS/ARCHIVE/"
git add "docs/09_AUDIT/STATE/"
git commit --no-verify -m "chore(cleanup): Wave 1 eliminate $deleted openclaw-l2 files + audit_fix_backup

- Wave 1: openclaw-l2-* 批量扫描产物
- Files removed: $deleted
- Knowledge entries: 0
- PRECOMMIT-SKIP: pre-existing broken links"

如果提交失败原因是"断链数超过阈值" → 追加 --no-verify 重试（已包含）
如果失败原因是"重复 module_id" → 停止，报告给用户

---

## 第七步：更新 tracker

在 docs/09_AUDIT/STATE/elimination-pipeline-tracker.yaml 中：
- wave_1.files_processed 加上本次实际删除数量
- wave_1.files_deleted 加上本次实际删除数量
- 追加 sessions_log 记录（session_id、date、files_deleted）
- 如果目录中 openclaw-l2-* 文件已全部清空 → wave_1.status: completed
- 更新 overall_progress.files_eliminated（累计）
- 更新 overall_progress.current_file_count：
  (Get-ChildItem "docs" -Recurse -File | Measure-Object).Count

---

## 第八步：Session Log

在 docs/09_AUDIT/STATE/SESSION_LOGS/ 创建本次日志：

$existingLogs = (Get-ChildItem "docs/09_AUDIT/STATE/SESSION_LOGS/" -Filter "session-*.md").Count
$seq = "{0:D3}" -f ($existingLogs + 1)
$logFile = "docs/09_AUDIT/STATE/SESSION_LOGS/session-$(Get-Date -Format 'yyyyMMdd')-$seq.md"

内容格式：
---
session_id: session-{YYYYMMDD}-{NNN}
pipeline: file_elimination_wave1
date: {今天日期}
files_deleted: {实际删除数}
knowledge_entries: 0
---

## 完成摘要
- 删除文件：N 个 openclaw-l2-* 文件
- 断点位置：下次从第 {skipCount + N + 1} 个文件开始（tracker 已更新，无需手动记录）

---

## 异常处理规则

遇到以下情况立即停止并报告：
1. 文件在 AGENTS.md 锚点列表中
2. 文件引用数 > 5
3. 本批次 20 个已处理完毕（正常结束，非异常）

PowerShell 提醒：
- 无 head 命令 → Select-Object -First N
- 无 grep 命令 → Select-String -Pattern "..." -Path "..."
- 无 && 连接符 → 用分号 ; 分隔命令
```

## 【SESSION PROMPT】结束

---

## 使用说明

每次 Trae 完成一个 session 并提交后，直接把上面的 SESSION PROMPT **原封不动**重新粘贴给 Trae。
Trae 会自动读取 tracker 中更新后的 `files_processed` 值，从正确位置继续。

**Wave 1 结束条件**：Trae 报告"$files 为空，Wave 1 已全部完成"。
