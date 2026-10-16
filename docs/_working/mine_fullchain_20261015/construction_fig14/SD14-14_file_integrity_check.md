---
gate_selfdoc: GIT-DANGEROUS
ttl: task_bound
doc_type: mining_segment
campaign: mine_fullchain_20261015
segment_id: D14-14
figure: fig14 施工升级流（construction_workflow_map）
created: 2026-10-15
ssot: docs/01_policies_and_standards/sop/construction_sop/construction_workflow_policy.md#step-9-文件完整性检查 + 附录 D 锚块
---

# SD14-14 文件完整性检查（policy Step 9）

## 1. 定义

Step 8 流转完成后、提交前的完整性自证段：git status 确认无回退/无清理+对比施工前后 staged 文件清单+验证 worktree 修改已 merge 到主树+held_files 检查。铁律=所有新建/修改文件必须立即 git add（project_memory #ARCH-GIT-CLEAN-GUARD-FIX 教训——git clean -fd 物理删除 untracked 不进回收站）。丢失恢复=git reflog/dangling blob（65_git_safety_governance §灾难恢复）。role=handoff：三条判据里两条实体在图11（对账/pre-merge/claim 快照），本域只剩"本任务改动清单与 staged 差集为空"且无阈值判据。handoff_to=D11-C11/D11-S07/D11-S04。

## 2. 六向台账

| 向 | 内容 | 路径证据 |
|---|---|---|
| 输入面 | 施工前后改动清单；worktree 状态；held_files 名册 | 政策 L570-604；`scripts/lock_files.py status`（本批实跑 CLEAN） |
| 输出面 | 完整性确认（无结构凭据面）；stash_notice 检查点 | `.runtime/workspace_alerts/stash_notice.json`（宪法 §2.8：编辑"消失"先查此件）；图 YAML #D14-14 exec_source=null |
| SSOT 真源 | 政策 Step 9 锚+`docs/01_policies_and_standards/policies/workspace_governance_policy.md`+65_git_safety_governance（归档侧）+图11 D11-C11/D11-S07（机制真源引用不重述） | 图 doc_refs 四件 |
| 代码模块 | `scripts/lock_files.py`（status 可跑）；`scripts/session_worktree.py`——政策所指 `status` 子命令**不存在**（invalid choice，实测子命令集=create/exec/merge/abort/list/archive，D14-G07 实证；本批进一步实证 archive 为后续新增第 6 子命令）；`scripts/rollback.py`（full_revert/partial_revert/discard/hard_reset/preview/preflight 等在册子命令，在盘） | 三件在盘 |
| 门禁约束 | 本域零 gate（gates:[]）；WORKSPACE-CLEAN-CHECK/PRE-MERGE-TOPO-CHECK 归图11 | 图 YAML #D14-14 |
| 自动化触发 | 无自动触发面（handoff role）；REAPER live 巡检 warn worktree_changes=5010>50（本批实跑——并行 session 漂移风险是本段现实背景） | `python -m zephyr.trading.process_reaper --status` 实跑输出 |

## 3. 自审闸三态

| 向 | 态 | 依据 |
|---|---|---|
| 输入面 | pass | 改动清单/锁名册可查 |
| 输出面 | warn | "本任务改动清单与 staged 差集为空"无工具无阈值判据（图 note 原文）；确认动作无凭据 |
| SSOT 真源 | pass | workspace_governance_policy 在册；机制真源正确外指图11 |
| 代码模块 | fail | 政策 Step 9 命令块所引 `session_worktree.py status` 子命令不存在（D14-G07，四条幽灵子命令之一）——照政策抄命令必失败 |
| 门禁约束 | warn | 本域零 gate，判据实体全在图11（引用不重述是合法边界，但本域自身无拦截面） |
| 自动化触发 | warn | 无自动触发；依赖人工记忆执行 |

## 4. 缺口与建议

- 缺口1（D14-G07）：政策 Step 9/10/12 三处共四条幽灵子命令（status/commit/mark-completed/cleanup）。建议：政策按 R-06 更正注记（L588-589/L619-620/L727-730 已有注记但正文命令块未改）彻底改版——正文命令块与注记并存本身是矛盾（宪法 §4.4）。
- 缺口2：差集判据无工具。建议：低成本落一个只读脚本（git diff --name-only vs 任务卡 files_in_scope 差集），或先以 handoff 包自报留痕。
- 缺口3：本批实测 worktree_changes=5010>50 的 reaper 告警提示：多会话并行下"完整性"已是系统级问题，单会话自证不够。建议：D14-14 与图11 D11-C11 对账面的联动检查列入收班序列强制项（宪法 §2.9 已有，核对执行率即可）。
