---
created: 2026-09-30
ttl: task_bound
title: 提交链路全流通·E5 git 核心操作（挖矿）
session: M3
---

# E5 — git 核心操作（Gateway 持锁段：add → commit → 孤魂验证）

> 挖矿代理 M3 ｜ 2026-09-30 盘面实测行号（本日逐锚点核实，较种子行号整体漂移 +50~80 行，冲突以本文为准）。
> 真源文件：`src/zephyr/gov_enforcement/rule_bridge/git_commit_gateway.py`（4690 行，本日 git status=clean 无占用）。

## §0 自审闸三态

| 段 | 状态 | 依据 |
|---|---|---|
| 全局锁 + 持锁主流程 `_commit_locked` | 【挖干】 | 六向齐，file:line 本日逐一核实 |
| gitignored 分离 / pathspec 临时文件 / rename 检测 / 孤魂 merge-base 验证 | 【挖干】 | 锚点+缺陷史+耗时账齐 |
| pre-commit 通道（`_run_precommit_channel`） | 【不可挖】→ E4 | 属 E4（pre-commit hook 通道）环节，本文只记调用点与计时装表 |
| L2 门禁链本体（`_check_gates_with_drift_watch`） | 【不可挖】→ E3 | 属 E3 环节，本文只记 drift-watch 外壳与 own/foreign 连坐降级 |

## §1 组件全清单

| 组件/功能 | 锚点 file:line | 触发时机 | 耗时账 | 自动化属性 |
|---|---|---|---|---|
| 全局提交锁 `_GlobalCommitLock` | git_commit_gateway.py:242-244（`git_commit_global.lock`，TTL=1800s，timeout 缺省 60s）、:599（`<主仓根>/.ailocks/`） | 每笔直提 commit() 进锁即抢 | 锁等待计入 `_commit_t0`（:2562）→`_total_ms`（:2817）；LOCK_TIMEOUT 走队列改道（宪法 §2） | 事件触发，跨进程串行 |
| 慢提交阈值与审计 | :347（`_SLOW_COMMIT_THRESHOLD_S=60.0`）、:2817-2819（`_audit_commit_slow_event`） | OK 且 total>60s | commit_slow 实测 112/112/799 s（med/med/max，n=269，b0_readme 表）；快样 85/56/354（ok_sample n=52） | 自动；ok 采样 :2822-2836（sha 尾 ≥0xE=12.5%） |
| 持锁主流程 `_commit_locked` | :3278-3313 | 锁内，门禁链放行后（调用点 :2815） | 每笔锁内 git 子进程 ≈8-12 个（分解见下） | 全自动，五步串行 |
| 步1 gitignored 分离 `_stage_gitignored_tracked` | :2926-2961；`_filter_gitignored` :2881-2897（`check-ignore --no-index` 每批 300 防 WinError 206）；`_is_staged_delete` :2861-2872（`cat-file -e HEAD:`）；`is_git_tracked` :2843+ | 每笔（清单含 gitignored-tracked 时） | 病根：git add 对 gitignored 整批拒绝（:2927 docstring）；deleted→`git rm --cached --ignore-unmatch` :2940-2944，existing→`git add -f` :2954-2958 | 自动分离，失败即 COMMIT_FAILED |
| 步2 pathspec 临时文件 `_write_pathspec_file` | :4409-4420（OS temp dir `gw_pathspec_*.txt`，`:(icase)` 前缀） | 每笔 | 零 git 子进程；`#ARCH-ROOT-TEMP-FILE-ENFORCEMENT-001`（项目根零临时文件） | 自动，finally 清理 :3902-3906 |
| 步3 add/rm `_add_and_remove_normal_files` | :3315-3373（add :3338，rm :3354-3357，均 `--pathspec-from-file`） | 每笔 | 治本 ARCH-030：delete 文件 git add 报 pathspec did not match → git rm 替代 | 自动 |
| 步4 staged 检查 | :3812（`diff --cached --quiet`） | 每笔 | rc=0 → NOTHING_TO_COMMIT :3815-3818 | 自动 |
| 步5.5 pre-commit 通道调用点 | :3819-3829（计时 `_pc_ms` A1 装表 :3821-3825） | 每笔 | "本通道常是全链最贵一段（实测单件 ≥6 分钟）"（:3823 注释原文） | 阻断即 `_audit_commit_block_event` |
| 步6 commit `_commit_with_file_message` | :4007-4083 | 每笔 | 见下列子件 | 统一入口 |
| ├ merge 中间态检测 `_is_merge_in_progress` | :4422-4441（`rev-parse --git-path MERGE_HEAD`，worktree 感知）；拒绝响应 :4443-4457 | 每笔 | AI-R1-003 红队治本：`.git/MERGE_HEAD` 硬编码在 linked worktree 恒 False | MERGE_HEAD 晾置拒绝；merge finalize 显式放行转全量 |
| ├ rename 检测 `_has_staged_renames` | :3957-3968（`diff --cached --name-status -M` 命中目标 R 态）；fallback 切换 :4027-4028 | pathspec 模式每笔 | pathspec 会拆分 rename → 自动切无 pathspec | 自动 fallback |
| ├ 无 pathspec 安全阀 `_verify_staged_is_clean`/`_unstage_non_target_files` | :3970-3987 / :3989-4005（自动 reset HEAD 清并发污染后复验 :4047-4056） | 仅无 pathspec 笔 | 多 session 共享 index 污染治本（此前手动清理反复卡死） | 自动 unstage |
| ├ commit 本体 | :4062-4071（msg 临时文件 `gw_commit_msg_*.txt` :4062；`in_commit_flow` 守卫 :4064 红攻1治本；`git commit --no-verify -F <msg> [--pathspec-from-file]` :4067-4070） | 每笔 | merge finalize 全量收编非目标 staged=机制不可避免，可见性兜底 :4034-4045（#ARCH-MERGE-PATH-GAP-001②④） | `--no-verify` 有意（post-commit 链兜底= E6） |
| 孤魂验证（merge-base） | :3841-3859（`merge-base --is-ancestor <hash> HEAD`）；异常留痕 `_append_commit_anomaly_jsonl`（`orphan_commit_detected` + cherry-pick 处方 :3849-3857） | 每笔 commit 成功后 | fail-open（检测异常不改 OK 判定 :3858-3859）；W4 孤魂 301a6ee82a 治本（双锁互不排他→61s gate 窗口内 dev 被抢先） | 自动，error 日志+jsonl |
| finalize `_commit_locked_finalize` | :3873-3907：红蓝触发 :3882-3887（`_post_commit_red_blue_trigger` :3909-3938）、session_shutdown :3888-3895、index-HEAD 一致性校验 `_verify_post_commit_index` :3896-3901（本体 :4575，ita 复扫 B2 治本③）、pathspec/env 清理 :3902-3907 | 每笔（finally） | ita 条目对 `diff --cached` 不可见盲区（`ls-files --debug` flags 0x20000000 位，:4463-4472） | 全部 warn-only 不掩盖 commit 成功 |
| gate 链外壳 drift-watch | :3180-3276（A1 读缓存 :3198；S1 不可变树视图 :3213；TRACKED-DRIFT-READONLY own/foreign 连坐降级 :3231-3248） | 每笔门禁链前后 | 三连阻断整链白跑 19-58s（重试放大 4-6×，:3237 注释）→ foreign drift 降级 warn | 门禁本体归 E3 |

锁内 git 子进程典型分解（无 gitignored、有 pathspec 的普通笔）：check-ignore(1) + add(1) + diff --cached --quiet(1) + rev-parse --git-path(1) + diff --name-status -M(1) + commit(1) + rev-parse HEAD(1) + merge-base(1) = **8 个**；含 gitignored/deleted/无 pathspec 笔加 rm/staged-clean/ita 复扫至 ≈12。与种子"每笔 5-10 个"吻合。

## §2 六向台账

- **上游触发源**：E2 gateway 锁外前置（claim/probe/快照）放行后 :2815 调入；队列落地路径经各工独立 gateway（E7 `_get_gateway`，`_GlobalCommitLock` 按 project_root 键控）。
- **下游消费方**：E6 post-commit 钩链（git commit 进程返回前同步跑完）；E7 serializer CAS 重放 `_commit_tree_same_message`（landing:3118）绕本段但同吃 ref-tx 钩。
- **输入面**：files 绝对路径清单 + full_message + gw_marker；暂存区现势（多 session 共享 index=并发污染源，:3990-3994）。
- **输出面**：CommitResult（OK/NOTHING_TO_COMMIT/COMMIT_FAILED/LOCK_TIMEOUT/MERGE_IN_PROGRESS）；新 commit 对象+dev ref 前移；审计三账（commit_slow/commit_block/commit_anomaly jsonl）；env `ZEPHYR_COMMIT_GATEWAY=1` 窗口（:3860 置、:3907 复位）= E6 guard warn-only 分流信号。
- **真源锚**：本文 §1 所列 git_commit_gateway.py 锚点；msg/pathspec 临时文件真源=OS temp dir（:4411-4413 注释裁定）。
- **耗时账**：单条 commit 墙钟（锁等待+门禁+钩链）112/112/799s med/med/max（n=269，>60s 才记上偏）；快样 85/56/354（n=52，12.5% 采样）——b0_readme 表；锁内 git 段本身秒级，大头在 E3/E4。

## §3 缺陷与已修（本段在案）

| # | 缺陷 | 治本 | 锚点 |
|---|---|---|---|
| 1 | W4 孤魂提交 301a6ee82a：直提全局锁与队列 CAS 互不排他，61s 门禁窗内 dev 被抢先 | commit 后 merge-base 祖先链验证（fail-open）+ 队列 CAS 前抢同一把 `_GlobalCommitLock`（双锁统一） | :3838-3859；landing :2240-2245 |
| 2 | Windows CLI 超长 WinError 206（大批量 pathspec） | 一律 `--pathspec-from-file` | :3287、:3338、:4068 |
| 3 | gitignored-tracked 整批 add 被拒 | 分离三态（deleted→rm --cached / existing→add -f / 未跟踪跳过） | :2926-2961 |
| 4 | delete 文件 git add 报错中断全流程（ARCH-030） | git rm --cached --ignore-unmatch 替代 | :3319-3322、:3354 |
| 5 | staged rename 被 pathspec 拆分 | R 态检测自动切无 pathspec + staged-clean 验证 + 自动 unstage | :4027-4028、:3970-4005 |
| 6 | worktree 内 MERGE_HEAD 检测恒 False（.git=指针文件，AI-R1-003） | `rev-parse --git-path MERGE_HEAD` | :4422-4441 |
| 7 | merge 期 partial commit 被 git 拒 + 全量收编张冠李戴（AI-FILL-14） | MERGE_HEAD 晾置拒绝 + `--merge-finalize` 显式全量 + 收编可见性 | :4443-4457、:4034-4045 |
| 8 | intent-to-add 残留对 diff --cached 不可见但 merge 被拒（09 分支两文件实证） | `ls-files --debug` 0x20000000 扫描 + commit 后 index-HEAD 校验（B2 治本②③） | :4463-4472、:3896-3901 |
| 9 | gate 窗口 TOCTOU 无差别连坐硬阻断（三连白跑 19-58s×4-6 重试） | own/foreign 分流：own 未归因写入才硬阻断，foreign 降级 warn（pathspec 构造性排除搭便车） | :3231-3275 |
| 10 | `_GlobalCommitLock` 收到 str 参数静默降级裸 CAS（#ARCH-327） | 异常类型进 warning 正文 | landing :2258-2267（同机理记此备查） |

## §4 待办移交

1. **无开放缺陷**。本段 10 项在案缺陷均有治本锚点；行号随码漂移须以 S1 视图/replay 判等守护（:3208 出厂判据）。
2. 移交 E4：pre-commit 通道（:3819-3829）计时已在 A1 装表，E4 挖矿直接消费 `_pc_ms`。
3. 移交 E9：commit 三账（slow/block/anomaly）+ ok 采样口径（:2822-2836）。
4. 观察项：锁内 git 子进程 8-12 个/笔——A 段 GIT-CALL-BUDGET（骨架 §三 A1）读账代自扫时以本清单为基线分解。
