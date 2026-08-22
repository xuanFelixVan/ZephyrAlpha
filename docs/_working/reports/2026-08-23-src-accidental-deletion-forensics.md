---
ttl: task_bound
---

# src/zephyr 误删事故取证报告（2026-08-23，P0 安全事件）

> **事件**：2026-08-23 凌晨 ~01:37–01:43，主仓 `src/zephyr/` 下 2936 个 .py 文件被物理删除（磁盘清空），tests/scripts/docs 未受影响，git HEAD 完整。已从 HEAD 完整恢复（零损失，import 验证正常）。
> **性质**：P0 安全事件——肇事指令走未仪表化通道，绕过全部治理护栏。
> **本报告只取证不定罪**；防复发方案登记 candidate_module_registry（CAND）。

## 1. 时间线（盘上实证）

| 时刻 | 事件 | 证据 |
|---|---|---|
| 01:23:53 | session `ai-60260-...` 主仓 `git reset -q`（mixed，不动工作区，同 sha） | ~/.zephyr_audit/ 审计日志 |
| 01:31–01:37 | 提交 405be2ec（蓝图批）/b777479a（派生批）落盘，各触发 reconcile worker A/B | .git/logs/HEAD |
| 01:37:06 | worker B 启动，与 worker A **并发重叠 61 秒** | reconcile_status_b777479a.json |
| ~01:37–01:43 | **渐进式 FS 删除进行中**：worker B 报 `No module named '...session_worktree'`（该文件先没、父包尚在=逐文件推进） | worker 日志 |
| 01:38:43 | GATE-GHOST 报告 ghost_count=37、deleted_files=[]——此刻磁盘尚无大规模缺失 | ghost_1787420323.json |
| 01:42–01:44 | ai-60260 密集 status 监视→ls-tree→reflog→fsck 取证 | 审计日志 |

## 2. 排除项（护栏零触发，均非肇事者）

| 嫌疑 | 排除依据 |
|---|---|
| `git reset --hard` | 证据是 **mixed-reset 误报**——git_guard_bypass_reconciler 已知局限（same-sha reset 误计）；wrapper 审计全窗口无 --hard/clean 放行 |
| commit_queue_landing 专用 worktree | 逐项审查：所有危险操作锚定 `.runtime/commit_queue/worktree`，reflog 完整指向 dev，无逃逸主仓前提 |
| 各 reconciler | ops_guard_audit_stats：judge_calls 9735/9648、**block=0**；src 属 PROTECTED_PREFIXES，经 guard 的删除必被拦计数 |
| deprecated_directory / ghost_autoclean | 仅涉 data/databases/backups、37 ghost nodes，`removed_dirs:[]` / `deleted_files:[]` |
| session task:SRC-081 | 是 pytest 测试夹具 session 名（tests/gate/...），非肇事主体 |

## 3. 肇事路径裁定

**所有仪表化通道均无肇事记录**——核心 forensic 事实。肇事指令走的是**完全未仪表化的通道**：最大嫌疑是主仓活跃 session `ai-60260-20260821194527` 经 `python <一次性脚本>`/`python -c` 形态执行的渐进式删除（PS wrapper 不审计 python 进程内部行为；ops_guard 的 in-process 补丁只装在 reconcile_worker 进程）。该 session 是事故窗口唯一活跃主体，事后行为（密集 status→ls-tree→reflog→fsck）与"操作者目睹删除蔓延"高度吻合。证据强度：中（通道排除法+行为吻合，无直接命令记录）。

## 4. 同型代码级隐患（具备删主仓 src 能力，按危险度排序）

1. **`worktree_manager.py:310-312`** `_wt_path()` 对 session_id 零消毒直接 `_drafts_dir / session_id`；`create_session_worktree` L437 与 `_remove_worktree` L568 对该路径 `_force_rmtree`——session_id 为 `../src` 即等价 `rmtree(src)`。同属：`session_worktree.py:2078/2086`、`worktree_pool.py:322` 对枚举目录无 junction/reparse-point 检测（Windows 下 `shutil.rmtree` 穿透 junction 删目标内容）。
2. **`commit_queue_landing.py:247`** `shutil.rmtree(str(wt), ignore_errors=True)` 的 wt 由 queue_root 派生，无"必须落在 .runtime/commit_queue 内"硬断言。
3. **GATE-WORKTREE-LIFECYCLE**（reconciliation_registry.py:8682-8784）→ session_worktree_sweep：session_id 链全程无路径合法性校验。
4. **worker 并发缝隙**：MAX_CONCURRENT_WORKERS 未拦住 A/B 重叠（fallback spawn 缝隙）。

## 5. 防复发建议（转 CAND 登记）

1. **补仪表化盲区（最高优先）**：ops_guard.install_inprocess_enforcement() 从仅 reconcile_worker 推广到全部治理入口进程（git_commit.py、session_worktree CLI、commit_queue drain、pytest conftest）。
2. **删除前三件套硬断言**（`_force_rmtree`/`_cleanup_pool_worktree`/`ensure_worktree`/sweep 全量）：resolve 后必须 `is_relative_to` 预期前缀；拒绝 reparse point（Windows 查 FILE_ATTRIBUTE_REPARSE_POINT）；session_id 白名单字符集校验（拒 `..`/路径分隔符/冒号）。
3. **修 GATE-GIT-GUARD-BYPASS 误报**：same-sha `reset: moving to HEAD` 不计入 reflog_count。
4. **遥测前置**：sweep 的 `_force_rmtree(d)` 删除发起前即落 worktree_ops_log.jsonl（含调用栈），非成功后才记。
5. **worker 全局限速**：并发闸门改文件锁互斥，堵 fallback spawn 缝隙。
6. **凌晨主仓直跑收权**：00:00–06:00 主仓写操作强制 worktree 或人工确认。

## 6. 恢复记录

- 恢复方式：`git checkout HEAD -- src/zephyr`（版本库完整）
- 验证：.py 文件数 2936 = HEAD 完整数；`import var_calculator` 正常；无遗留删除项
- 结论：**零数据损失**
