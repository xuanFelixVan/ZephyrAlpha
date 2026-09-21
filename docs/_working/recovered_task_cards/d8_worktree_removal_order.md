---
ttl: task_bound
completes_when: Owner 手动执行删除且回执后转 archived
---

# D-8 五棚删除命令呈报（Owner 手办，裁定#392（D-8））

> 打包归档已完成（前置达成），删除动作=OPS-GUARD 禁会话内执行，**以下命令请 Owner 手动执行**
> （或授权任一会话持 Owner 批文执行）。执行后本文件补记日期即闭案。

## 1. 打包归档凭证（已完成 2026-09-21）

- 归档位：`G:\zephyr_cold\50_archive\by_project\zephyralpha\worktree_remnants_20260921\`
- 五包+哈希清单：AI-GOVA-001.tar.gz / AI-TD2-GOV-001.tar.gz / AI-TD2-SEC-001.tar.gz /
  AI-VCFIX-001.tar.gz / st-auditdoc-v4-20260918.tar.gz + SHA256SUMS.txt（压缩后合计 58MB；
  SHA256 见该目录清单文件，恢复=tar -xzf 解包即原目录）。

## 2. Owner 手删命令（PowerShell 管理员或资源管理器均可）

```powershell
Remove-Item -Recurse -Force "D:\ZephyrAlpha\.worktrees\AI-GOVA-001"
Remove-Item -Recurse -Force "D:\ZephyrAlpha\.worktrees\AI-TD2-GOV-001"
Remove-Item -Recurse -Force "D:\ZephyrAlpha\.worktrees\AI-TD2-SEC-001"
Remove-Item -Recurse -Force "D:\ZephyrAlpha\.worktrees\AI-VCFIX-001"
Remove-Item -Recurse -Force "D:\ZephyrAlpha\.worktrees\st-auditdoc-v4-20260918"
```

- 五棚均已核实：git worktree list 零注册、无 .git 指针、纯磁盘残骸（tc_09 卡 A 级取证）。
- 删除后 `git worktree prune` 可选（无注册无需）；git 层零影响。

## 3. 证据链

- git 层收口=final3 W9-6（分支删除+四证 ALLOWED 存档 .runtime/gate_audit/worktree_abort.jsonl 09-18 20:51）。
- 磁盘取证=tc_09 卡任务一行（st-auditdoc-v4 15,533 文件等）。
