---
ttl: task_bound
session: st-maint3-20261011
lane: readonly_archaeology
status: first_edition
created: 2026-10-11
---

# 池面回退弹 · 根因案卷（维护三班考古车道）

> 性质：**案卷**（证据 + 分档论断），非裁定、非判词。每条论断标【实测】（本车道亲自读到/跑到，附命令与摘录）／【推断】（合理但未证实）／【查无】（找过但没有）。
> 纪律：全程只读 git（status/log/show/rev-parse/rev-list/ls-files/cat-file/merge-base/hash-object/reflog/worktree list）；未执行任何写 index 或写工作树的 git 命令；未杀停/重启任何进程；除本案卷与本班临时区 `.runtime/tmp/maint3_pool_rc/` 外零写盘。
> 引用根宪法用"根宪法 §N"。所有路径与行号均为本车道实际 grep/read 命中，未凭记忆书写。

## ① 事件窗与输入

【实测】存证目录 `.runtime/tmp/pool_rollbackbomb_20261011/`（目录 mtime Oct 11 21:43）：

| 文件 | 内容 | 实测大小/行数 | mtime |
|------|------|------|--------|
| `MANIFEST.md` | 定窗与处置记录，含 23:0x 第二击追记 | 35 行 | Oct 11 22:37 |
| `head_at_repair.txt` | `01513460c279c00860c23a7ca76a838a825637e0`（单行） | 41 B | Oct 11 21:37 |
| `staged_D_list.txt` | 28 件"盘面缺失、HEAD 完好" + 第二击 1 件追记 | 29 行 | Oct 11 22:37 |
| `status_excerpt_before.txt` | 处置前 git status 摘录 | 48078 B | Oct 11 21:37 |
| `code_drift/` | 双面字节归档 56 个文件 = 28 件 × (`DISK__*`/`INDEX__*`) | — | Oct 11 21:41 |

【实测】受害件面覆盖（`ls code_drift/` 全量命中，路径为归档名反解）：
码/测试面 24+3 件含 `scripts/commit_queue.py`、`scripts/git_guard.py`、`scripts/governance/{apply_depgraph,audit_worktree_ops_telemetry,reconcile_generators,session_takeover_ledger}.py`、`scripts/governance/d3_metadata/add_module_translation.py`、`scripts/governance/wave1b/dead_letter_prescriptions.py`、`src/zephyr/gov_enforcement/commit_gates/{__diff_helpers,translation_coverage_gate}.py`、`src/zephyr/gov_enforcement/rule_bridge/{commit_belt_daemon,git_commit_gateway,heartbeat_daemon,worktree_drift_watchdog}.py`、`src/zephyr/governance/registry_projection/projection_generator.py`、`src/zephyr/infrastructure/rollback/forward_fix_runner.py`、`src/zephyr/security/access_control/session_concurrency.py`、`src/zephyr/shared/io/audit_jsonl_writer.py`、`src/zephyr/trading/process_reaper.py`、`src/zephyr/ai_layer/scheduling/order_daemon.py`、`src/zephyr/frontend/dashboard/web/features/resourceweek/rw-data.js`，测试件 `tests/gov/git/test_git_commit_extreme.py`、`tests/gov/governance/audit/test_stash_lifecycle.py`、`tests/gov/governance/rule_bridge/{test_commit_belt_daemon,test_worktree_drift_watchdog_redteam_audit}.py`、`tests/gov/session/test_session_concurrency.py`、`tests/legacy_zephyr/trading/test_process_reaper.py`、`tests/meta/shared/test_audit_jsonl_writer.py`。
`staged_D_list.txt` 另含 28 件（docs/_working/maint2_campaign/{00,14,16,18,19}、7 张 exam_cards yaml、`tests/gov/**` 8 支测试、`scripts/governance/generators/generate_collection_shard_manifest.py` 等）。

【实测】事件窗 = **(2026-10-11 20:35:58, 21:05)**（定窗依据见 §③ 的 20:36:01 落地与 20:40:05 独立目击）。

## ② 代码路径清单（能对主区工作树/index 做批量写或复位的全部命中点）

真源文件：`scripts/governance/commit_queue_landing.py`（267461 B，落地器实现）、`scripts/commit_queue.py`（4973 行，队列本体）、`src/zephyr/gov_enforcement/rule_bridge/git_commit_gateway.py`、`src/zephyr/infrastructure/git_batcher.py`、`src/zephyr/governance/audit/workspace_hygiene_reconciler.py`、`scripts/git_guard.py`、`src/zephyr/gov_enforcement/rule_bridge/worktree_drift_watchdog.py`。

### A. 队列落地器内部

| # | 位置 | 它做什么 | 选的"源" | 方向性检查 |
|---|------|---------|---------|-----------|
| A1 | `scripts/governance/commit_queue_landing.py:1871-1903` `_sync_worktree` | 每项处理前 `reset --hard refs/heads/<target_branch>` + `clean -fd`（1889/1892 两处 `_git_wt`） | `refs/heads/dev`（实时 tip） | **无"禁止回退"判据**（源=dev tip，靠 target 新鲜度）；作用域=专用 worktree |
| A2 | 同文件 `:1732-1752` `_git_wt` | 所有危险命令的唯一出口；执行前硬校验 worktree `.git` 链接存在 + `rev-parse --show-toplevel` 解析回自身 | — | 防"walk-up 打穿主仓"的**入口闸**（docstring 1736 行原话：链接丢失时"git 以 cwd 向上查找会命中主仓 .git——reset --hard/clean 直接打穿主工作区（当日 reflog 实证 6 次成对 reset）"，2026-08-29 事故治本） |
| A3 | 同文件 `:1841-1903` `_verify_wt_integrity_post` | A1 两条危险命令**执行后**各复测一次（EV-02，2026-09-30 补），关 A2 与命令在飞之间的 TOCTOU 窗 | — | 同上，属"打穿防护"非"回退方向防护" |
| A4 | 同文件 `:2484-2563` `_apply_snapshot` | 把袋 blob 字节整文件写盘：`abs_path = self.worktree_path / rel`（2484 起）→ `abs_path.write_bytes(content)`（2527） | **袋内 `blob_ref` 快照字节**（入队时刻捕获） | 注册表族走 `_merge_registry_file` 三向合并（2520-2530，注释点名"fb5a7821d 陈旧快照 blob 一写抹掉 103 条已提交身份的病灶在此封死"）；**普通文件无"是否早于 HEAD"判据**，只有 M5.1 写后读回 sha 自验（2533-2556，验的是"写没写对"，不是"该不该写"） |
| A5 | 同文件 `:2566-2626` `_prestage_snapshot` | `git add --pathspec-from-file` / `git rm --cached` 预暂存袋内文件（gate 依赖 staged diff） | 袋快照 | 无方向判据（作用域=worktree index） |
| A6 | 同文件 `:2627-2674` `_advance_dev` | `update-ref refs/heads/dev <new> <old>` CAS 推进 dev | 新提交 | **有**：CAS 期望旧值，败则 CasConflict；唯一的前进方向闸 |
| A7 | 同文件 `:2720-2748` `_converge_one`（由 `:2816-2895` `_converge_main_workspace` 逐项调用，**写主区工作树**） | 仅当主工作区文件逐字节 == `old_sha` 版才写入 `new_sha` 字节（`tmp.write_bytes` + `os.replace` 原子替换，2743-2746）；脏/缺失/untracked 一律 `skipped_*` | `new_sha`（落地后的 dev tip） | **有**：前置 `_worktree_matches(old_sha, rel)` 逐字节相等；`_tree_has_path` 补 untracked 盲（2739）。方向=只能 old→new，代码形态上写不出旧字节 |
| A8 | 同文件 `:2769-2814` `_converge_index_one`（**写主区 index**） | 条件式清"落地残影"：`git restore --staged --source=<new_sha> -- <rel>`（2804/2810） | `new_sha` | 三态判据（==new 跳过／==old 清／两者皆非则先验"staged blob 在某历史提交可达"才清，2795-2807，裁定#480 C-3）；**开关面**：`_index_convergence_mode`（2756-2767）读 `data/runtime/main_index_convergence.{off,live}`，缺省 **shadow=只判不动** |
| A9 | 同文件 `:3526-3566` `_replay_commit_without_gates` | CAS 冲突重放：`self._git_wt("read-tree", f"refs/heads/{self.target_branch}")`（3562，注释"纯 index 置换，不触工作区"）+ write-tree/commit-tree | `refs/heads/dev` 实时 tip | 无回退判据；危险 plumbing 走 A2/A3 同一出口 |
| A10 | 同文件 `:2933` `_refresh_integrity_baseline_main_repo` / `:2897` `_integrity_baseline_mode` | 基线面刷新（在主仓根执行，`_git_repo` 系） | HEAD | 读为主，未见整树写回形态 |

【实测】`scripts/commit_queue.py` 侧对主区池面的命中点只有：`:3196`/`:4764` 的**报文文案**（"或先 `git checkout dev -- <件>` 重基本袋再投"）与 `:1373`/`:1412`/`:2310` 的**注释**（描述 A1 的 `clean -fd` 会删掉受害方已物化未提交的新文件）。即队列本体不直接写主区池面；写主区池面的只有 A7/A8。

### B. 队列之外、能批量写主区池面的在册件

| # | 位置 | 它做什么 | 源 | 方向性检查 |
|---|------|---------|----|-----------|
| B1 | `src/zephyr/gov_enforcement/rule_bridge/git_commit_gateway.py:3642`、`:3863`、`:4040-4064` | 临时索引全生命周期：`GIT_INDEX_FILE` + `read-tree HEAD` + 仅 add 本提交文件 | 主区 HEAD | plumbing 只作用于**临时索引**，不碰共享 index；`:5248` 注释暴露一个旗："还原置位前值——过授权方向泄漏（git_guard 认旗放行 reset --hard/clean/stash）止血" |
| B2 | `scripts/git_guard.py:95` `DANGEROUS_SUBCOMMANDS={reset,checkout,stash,revert,restore,mv,clean}`、`:98-100` `PLUMBING_BLOCKED_SUBCOMMANDS={read-tree,update-index,write-tree,hash-object}`、`:436-487` reset --hard 自伤检测、`:1071` "66 号事故 6 根因：read-tree 曾隐形重置共享 index，清空全部 staged 元数据"、`:1097` `_is_fast_path_authorized()` 命中即**透传** checkout/reset/restore/revert | 危险 git 的进程外闸（hook/包装） | — | 全是"是否允许执行"的闸，**没有一条判"执行后池面是否相对 HEAD 后退"**；且 fast-path 授权旗一命中即整体透传 |
| B3 | `src/zephyr/infrastructure/git_batcher.py:190-270` `git_restore_batch` | 单次 `git restore [--staged] -- <files>` 批量还原（`--staged=False` 默认还原工作树到 HEAD） | 主区 HEAD | 无回退判据；fail-open；`:245-262` 每次成功都落 `worktree_ops_log.jsonl` 遥测（op=`git_restore_batch`，source=`git_batcher.git_restore_batch`，含 pre-hash） |
| B4 | `src/zephyr/governance/audit/workspace_hygiene_reconciler.py:205`、`:509-523` | post-commit 事件触发的"工作区卫生"收敛：把 `modified ∩ auto-sync 产物清单`（`:223-270` 路径前缀册）批量 `git restore` 回 HEAD；`[INVARIANTS] :15` 声明"只自动 restore auto-sync 产物，不触碰真实代码修改" | 主区 HEAD | 清单白名单是唯一作用域闸；**方向闸=无**（还原目标恰是"HEAD 版"，故对被拍件的旧字节形态无能为力） |
| B5 | `src/zephyr/gov_enforcement/rule_bridge/worktree_drift_watchdog.py:111-114` 常量（`_AUTO_STAGE_DIR="docs/_working"`、`_AUTO_STAGE_MAX_BYTES=10MB`、`_AUTO_STAGE_MIN_AGE_SECONDS=120`、`_AUTO_STAGE_STATE_CAP=2000`）、`:151-172` `_auto_stage_candidates`（`git ls-files --others --exclude-standard -z -- docs/_working`）、`:175-215` `_auto_stage_working_docs`（**分块 `git add -- <chunk>` 直写主区共享 index**，逐件审计 `verdict=auto_staged`）、`:443-463` `_snapshot`（`dest.write_bytes(src.read_bytes())`）、`:714+` `_sweep_dead_sessions` | 漂移哨兵：扫 tracked 文件 work≠index、自动把 `docs/_working` 下 untracked 新件 stage 进主区 index（"B2 护盾：误删后 `git checkout -- <path>` 一条命令拉回"）、隔离快照、清死会话 | 主区 work/index | **无方向闸**：它 stage 的是"当下盘上字节"，若池面已被拍旧，它就是**把旧字节固化进共享 index 的放大通道**；实测审计记录 `session_id` 常空串，owner 归属缺（根宪法 §3.4 落不了地） |

【查无】全仓 grep 未命中任何"把主区工作树/index 显式同步到某个**旧** ref 或旧快照"的在册函数（`git checkout <old_ref> -- <paths>`／`git restore --source=<old>`／主区 `reset --hard <old>` 形态均无命中）。命中的整树级危险形态只有 A1（源=实时 dev tip）与 A9（同）。

## ③ 时间线对账（实测日志摘录）

【实测】主区 git 指针面（`git reflog show dev --date=iso`，摘录）：

```
92b69f0178 dev@{2026-10-11 20:17:07}
01513460c2 dev@{2026-10-11 20:36:01}     <-- 事件窗起点后 2 秒的落地
a0e27b1ac3 dev@{2026-10-11 21:57:12}     <-- 下一个落地，中间 81 分钟无推进
b942162936 dev@{2026-10-11 22:03:15}
12bebcfdf4 dev@{2026-10-11 22:10:30}
85f83c3463 dev@{2026-10-11 22:18:11}
94aeb152cc dev@{2026-10-11 22:25:44}     <-- 第二击受害件的落地
```
同窗 `git reflog --date=iso` 内 HEAD 无任何 reset/stash/checkout 条目；10-11 全天的 `reset: moving to HEAD~1` 只出现在 00:06/00:15/00:18/02:55（窗口外）。【实测】`git stash list` 为空、`git reflog show stash` 报 "unknown revision"（refs/stash 不存在）；`.runtime/workspace_alerts/stash_notice.json` 最后一条 mtime=2026-10-10 17:23，记的是 10-10 的在飞清点，与本窗无关。

【实测】队列侧账本（四路交叉）：

1. `.runtime/commit_queue/done/q-20261011-st-maint2-20261011-0015.json`：`base_head=aca29fd5573896455e24685a6573324edc9d72c0`、`created_at=2026-10-11T20:31:25+08:00`、`landed_at=2026-10-11T20:36:01+08:00`、`landed_id=01513460c279…`、3 件：
   `modify src/zephyr/security/access_control/session_concurrency.py`（blob_sha256 14e7a92f…）、`modify tests/gov/session/test_takeover_ledger_kwarg_and_mark_logical.py`（212602647f…）、`modify tests/gov/session/test_session_concurrency.py`（d035e1f29e…）。
   **这 3 件全部在受害名单内**（前者在 `code_drift/`，后两分别在 `staged_D_list.txt`、`code_drift/`）。
2. 事件窗内队列零活动：`.runtime/commit_queue/pool_wave.log` 中 `2026-10-11T2[01]:` 行共 493583 条 `exit=claim_none` 抽样，**非 claim_none 行数 = 0**（`grep -v claim_none | wc -l` → 0）；全量 token 分布只有 `claim_none` 493583 / `no_slot` 1248，且 `no_slot` 最后一条是 2026-10-10T07:41。
3. `find .runtime/commit_queue/{pending,processing,dead} -name '*.json' -newerct "2026-10-11 20:30" ! -newerct "2026-10-11 21:15"` → **空**。
4. `.runtime/commit_queue/main_workspace_sync.jsonl`（A7/A8 的跳过留痕册，1615597 B，mtime Oct 11 22:18）内 `20:30–21:10` 区间条目数 = **0**。

【实测】独立目击（`.runtime/worktree_ops_log.jsonl` 14235 行，ts 为 **UTC**，+8 才是本地）：

```
12:45:33.696Z (=20:45:33 本地，窗内) op=git_restore_batch source=git_batcher.git_restore_batch file=data/architecture_health/latest.json
12:45:33.697Z (=20:45:33 本地，窗内) 同上 file=data/runtime_violation_snapshot/latest.json
```
窗内 `git_restore_batch` 只这 2 条，且两条都是 B4 的 auto-sync 产物（`data/**/latest.json`），**没有一条打在 28 件受害路径上**。

【实测】漂移哨兵目击（`.runtime/drift_watchdog/watchdog.jsonl`，ts UTC）：

```
2026-10-11T12:40:05.415Z  status=alerted scanned=531 drifted=531 alerted=1 healed=0 claimed=0 auto_claimed=0 deletion_observed=0 merge_suppressed=0
2026-10-11T14:40:47.511Z  status=alerted drifted=482 alerted=3 healed=0
```
即 **20:40:05 本地（落地 01513460c2 之后 4 分 4 秒）哨兵首次看到 531 个 tracked 文件 work≠index**；22:40:47 再次看到 482（第二击后）。两笔 `healed=0` → 哨兵没做恢复动作。窗内其余记录全是 `status=skipped reason="another instance already running (#99 single-instance lock)"`。

【实测】窗后活体观测（本车道在场期间，非事件窗内，但直接验证了 B5 的作用面）：本案卷第一次落盘后约 2 分钟，被 B5 的 auto-stage 护盾**未经本车道任何 git 动作**自动 stage 进主区共享 index——`git status --porcelain docs/_working/maint3_campaign/` 呈 `AM`（index 有 blob / 工作树已再次改动），`git ls-files -s` 得 staged blob `77494f3a46ef0ae1ab289bfeea211b7032af9155`（= 骨架首版），`git hash-object` 盘上现值 `1a4be3e4497fadb64eb22e4abbc35d13e442062f`（= 后续修订版），且 `.runtime/drift_watchdog/state.json` 内命中 `maint3_campaign` 登记 1 条。⇒ **daemon 能在会话不点的时机写主区 index** 这一通道，本车道亲眼见其活着；它 stage 的是"当下盘上字节"，故池面一旦被拍旧，该通道会把旧字节**固化进共享 index**（放大，非肇事的证据）。
同窗哨兵摘要另见 `13:57:33Z`（21:57:33 本地，恰在 21:57:12 落地后 21 秒）一条 `status=alerted drifted=480 healed=1`——本车道未追 `healed` 的处置细节（越出只读授权的动作面，留 §⑦）。

【实测】第二击账本：`done/q-20261011-st-maint2-20261011-0017.json` `base_head=b942162936…`、`created_at=22:23:53`、`landed_at=22:25:45`、`landed_id=94aeb152cc…`，4 件含 `docs/_working/maint2_campaign/20_handoff_to_maint3.md`、`00_ledger.md`、`19_chief_ruling_receipt.md`、`tests/gov/session/test_session_keepalive_ghost_gate.py` —— **4 件全部出现在 `staged_D_list.txt` 末行/正文**（`staged_D_list.txt` 末行明记 "strike2 22:37 … (landed 94aeb152cc 22:25, wiped within minutes)"）。

### 本段结论（对头号嫌疑的判定）

【实测】**头号嫌疑的"字面版"被证伪**：20:36:01 之后到 21:57:12 之间，提交队列**没有跑任何 drain/落地**（`pool_wave.log` 非 claim_none=0、done/pending/dead 无窗内 mtime、dev reflog 无推进），因此"某个袋真落地之后队列又做了一次主区池面同步"中的"同步步骤"在窗内不存在；A7/A8 的留痕册窗内零条目；B3/B4 窗内只还原了 2 个 `data/**/latest.json`。
【实测】**但嫌疑的"形态版"未被证伪，反而被加强**：肇事窗的**左端点**恰是 20:36:01 的落地（受害 3 件正是该袋 payload），**右端** 4 分 4 秒即有 531 件漂移目击；第二击同样落在"落地后数分钟"。两次都是**紧跟队列落地的后续动作**，队列确实是唯一已知的"落地后仍持有 old/new 两个基线并会写主区池面"的进程（A7/A8）。

【推断】替代嫌疑（按证据强度排序，本车道未能证实到写者名字）：
1. **会话车道/在飞面被物化进主区池**：见 §④ 的第三态字节——`tests/gov/session/test_session_concurrency.py` 的盘旧字节既非 HEAD 版也非该袋 `base_head` 版，唯一能同时给出"每件各自不同旧版本 + 一个不属于任何提交版本"的来源，是把某个车道（`.aidrafts/<sid>`，`git worktree list` 实测 10+ 支车道就挂在主仓树内）的文件面整体搬进主区。在册能"把别处字节写进主区池"的出口只有 A7（`os.replace`）、A4/B5（`write_bytes`）。
2. **A2/A3 双闸之间的另一条 `_git_wt` 旁路**（如 A9 的 `read-tree`）在某种 `.git` 链接"存在但指向另一处"的形态下漏检——【查无】直接证据；哨兵 `healed=0`、无 reset/stash reflog，方向不支持。
3. **B2 授权旗泄漏**（`git_guard.py:1097` fast-path 命中即透传 reset/checkout/restore/revert；`git_commit_gateway.py:5248` 自述"过授权方向泄漏……止血"）：旗一旦置位，环境内**任何子进程**都能在主区跑 `reset --hard`／`checkout <old> -- .` 而不被拦——【推断】这是"没有任何闸检查回退方向"最省事的实现路径；窗内 reflog 无 reset 条目使本项**减弱但不消**（`checkout <ref> -- <paths>` 与 `restore --source` 不留 reflog 痕迹，`read-tree`/`update-index` 亦不留）。

## ④ 字节级定性（量化）

方法：`git hash-object` 取归档字节 blob id，与 `git rev-parse HEAD:<path>` 比；再 `git log --format=%H dev -n 40 -- <path>` 逐 commit 反查"盘旧字节等于该件在哪一笔提交的版本"；行集用 `comm -13/-23 <(sort 盘旧) <(sort HEAD)` 计独有行数。

【实测】双面一致性（`code_drift/` 抽样 4 件）：**`DISK__*` 与 `INDEX__*` 字节逐位相同**（同一 `git hash-object` 输出）——

| 受害件 | DISK==INDEX blob | HEAD blob | 盘/暂存行数 | HEAD 行数 |
|--------|------------------|-----------|------------|-----------|
| `src/zephyr/security/access_control/session_concurrency.py` | `b9adc3e97598e8fee28cc1eb1a7d33cad027b455` | `ababcc299c661d39dbf0b9201a88e8d2a3f4b9ff` | 2266 / 2266 | 2297 |
| `scripts/commit_queue.py` | `264553c9b5c92601d38a11080f278fe997d3068b` | `15e69e9008c101fa4685e882c54285b13e272518` | 4631 / 4631 | 4973 |
| `scripts/governance/session_takeover_ledger.py` | `2056834b274b6eccc31b73caecec4b145ac2da46` | `f7e7002e5cb92b39f98081380aa123de8454d485` | 1251 / 1251 | 1262 |
| `src/zephyr/infrastructure/rollback/forward_fix_runner.py` | `877251140a6110ba5bb617a0eb3be019e2b3c845` | `f8f2ff56b25479e77602846d7f7113b320a7423a` | 117 / 117 | 156 |

⇒ **不是"index 与 worktree 分别来自两个不同基线"**，而是同一个基线被同时贴到两面（或先贴一面再被另一面吸收）。

【实测】盘旧字节对应的"出处提交"各不相同：

| 受害件 | 盘旧字节 == 哪一笔提交里该件的版本 | 该提交时间 |
|--------|-----------------------------------|-----------|
| `session_concurrency.py` | `f87bfa8bf7e4869634a16b26688b1d66babea613`（且**同时**等于袋 0015 `base_head=aca29fd557` 的该件版本——两说一致，`git rev-parse aca29fd557:<path>` 输出同为 `b9adc3e97…`） | 2026-10-10T21:26:21 |
| `scripts/commit_queue.py` | `1d5c0d36c4a9b85aa70b1820db8e209fc77217d2` | 2026-10-10T09:53:46 |
| `session_takeover_ledger.py` | `351411772584e9cbd91bc57187ce835075f6a954` | 2026-10-03T05:27:38 |
| `forward_fix_runner.py` | `git log --all --find-object=877251140a…` → 命中 `a9402f5510b470173c279f629da7891bb4f9a2f3`（2026-09-16）与 `d69abf352307…`（10-11 07:34，即"被这笔记提交换掉的那版"） | — |

⇒ **四个件来自四个不同提交**，故"整树拍到某一个旧 commit"的形态被**否证**（一次整树操作不可能让四个件分别停在 09-16／10-03／10-10T09:53／10-10T21:26）。判定＝**逐件拍到"该件自己的旧版本"**（per-path 陈旧基线，各件不同）。

【实测】决定性反例：`tests/gov/session/test_session_concurrency.py` 的盘旧字节 = `3fd5c015bf412079aab04d0e731c75d7a9198bd9`，而该袋 `base_head=aca29fd557` 的该件版本 = `7f04c19864b0820b769774ea743ed6a1075e51cd`，HEAD 版 = 又另一值。⇒ 这批旧字节**不是**"某一次 reset/read-tree 到 `base_head` 的整树产物"，而是**某个车道自己那份陈旧工作树**（比 base_head 还旧的一支），进一步支持 §③ 替代嫌疑 1。

【实测】行集合法量化（`lines_only_in_head` = HEAD 独有行数，即被吞掉的内容量；`only_in_disk` = 旧字节里 HEAD 没有的行，即"回退是否真子集"）：

| 受害件 | only_in_head（被吞行） | only_in_disk（非子集行） |
|--------|----------------------|------------------------|
| `session_concurrency.py` | 33 | 2 |
| `scripts/commit_queue.py` | 375 | 33 |
| `session_takeover_ledger.py` | **11** | **0**（严格真子集） |
| `forward_fix_runner.py` | 42 | 3 |

⇒ 4 件中 1 件为**纯真子集**回退（旧字节 0 行独有，11 行被吞），其余 3 件近似真子集（独有行 2–33，来自旧版本自身的改写残留）。**结论：回退形态 = 逐件写回该件的旧基线整文件；对 HEAD 而言几乎总是"内容子集"，因而"独有行数=0 或极小"是可机械识别的强判据。**

## ⑤ 结论分档

1. 【实测】处置时 HEAD = `01513460c2…` = 20:36:01 落地笔 = 袋 0015 的 `landed_id`；当前 HEAD=dev=`dce5ae9d2c…`，`git rev-list --count 01513460c2..HEAD` = 8。
2. 【实测】受害件落地的六笔（`ed5e59c289`/`d69abf3523`/`4cc45d7f07`/`e9534bf202`/`c869c0a3b5`/`01513460c2`）**全部是 HEAD 与 dev 的祖先**（逐笔 `git merge-base --is-ancestor` 均为 IS-ancestor）。⇒ **不存在"某 worktree/serializer 用旧 HEAD 做完 merge 后把主区指针拍回去"**：指针面全天单调前进，dev reflog 窗内零条目、无 reset/stash；损伤只在**池面（worktree + index）**，不在 ref。
3. 【实测】`head_at_repair.txt` 与"某袋 base_head"的关系：池面被拍的基线之一（`session_concurrency.py`）恰等于袋 0015 的 `base_head=aca29fd557`；但另三件各等于更早的不同提交，且有一件不属于 base_head 的任何版本 ⇒ 基线**不是单一提交**，而是**逐件陈旧副本**。
4. 【实测】窗内队列零落地（三条独立账本相互印证：`pool_wave.log` 非 claim_none=0 / `find pending|processing|dead` 空 / dev reflog 81 分钟无推进）⇒ **头号嫌疑的字面表述被证伪**。
5. 【实测】窗内唯一命中主区池面的在册写者 = B4→B3 的 `git_restore_batch`（20:45:33，作用域 2 个 `data/**/latest.json`），其还原目标是 **HEAD**，无法解释"退回旧字节"；B5 哨兵 `healed=0`，只观测未写。⇒ **本车道未能在窗内定位到确定的肇事代码行**（诚实陈述，不冒充已裁）。
6. 【推断】最可能的肇事通道：一次 **per-path 的陈旧面物化**（把某车道/暂存面的整文件复制进主区池并顺带 staged），触发时机紧跟队列落地；能承载它的在册出口只有 A7（`os.replace` 原子写）、A4/B5（`write_bytes`），或 B2 授权旗泄漏下的一次性 `checkout <old> -- <paths>`/`restore --source=<old>`（不留 reflog）。
7. 【实测】"顺带 staged"这一步的通道已在场证明：B5 的 auto-stage 护盾会在本会话零 git 动作的情况下把主区池面的当下字节写进**共享 index**（见 §③ 窗后活体观测）。⇒ 任何回退型写入只要落在 `docs/_working` 之外的 tracked 件，index 侧仍需一个同批写者；本案双面（work+index）字节一致说明"写 index"这一步同样发生了，B5 覆盖不到 tracked 件（它只 `ls-files --others` 取 untracked）——故 B5 是**放大/固化通道**，不是 tracked 受害件的 index 写入者。该缺口点名了下一步要查的第二类写者（能 `git add` tracked 件的 daemon：commit_belt_daemon / heartbeat_daemon / gateway 的 `_GlobalCommitLock` 邻接面，本车道未展开）。
8. 【推断】在册候件"池面回退方向无闸"成立且**与本案同根**：§② A1–A9 的方向性判据全部服务于"前进正确性"（CAS 期望旧值、逐字节等于 old 才快进、blob sha 读回自验），**没有一处**检查"写入结果是否是其 HEAD 版的真子集/旧版本"。`git_guard.py` 的闸面（`:95`/`:100`/`:436`/`:1097`）同理——只问"能不能跑这条命令"，不问"跑完池面是否后退"。
9. 【查无】`.runtime/sessions/*/` 在 20:35–21:10 区间无 mtime 命中（`find .runtime/sessions -maxdepth 2 -newerct …` → 空）；未找到任何"池面同步"专用日志（`.runtime` 下 queue 相关只有 `pool_wave.log`/`main_workspace_sync.jsonl`/`dead_triage_*.jsonl`/`doctor_audit.jsonl`）。

## ⑥ gate 提案（提案，非裁定）

**名称（暂定）**：GATE-POOL-REGRESSION-DIRECTION（池面回退方向闸）。

- **装在哪一层**：三层，缺一不可（对应 §④ 的形态结论）。
  1. **写者层（首选，成本最低）**：在 A7 `_converge_one` 与 A4 `_apply_snapshot` 的写盘点（`scripts/governance/commit_queue_landing.py:2527`、`:2743-2746`）加**写入前方向判据**——待写字节的行集若相对 `HEAD:<rel>`（或相对本次 `new_sha`）为"真子集且独有行 < 阈值"即拒绝写、转 skip + 审计。**不依赖 git 命令**，故 `read-tree`/`update-index`/`checkout -- <paths>` 这类不留 reflog 的旁路全都被同一把尺覆盖。
  2. **池面快照层（兜底，防未知写者）**：在册 `worktree_drift_watchdog`（已 60s 心跳、已扫 tracked work≠index、已写 `.runtime/drift_watchdog/watchdog.jsonl`）的扫描里增加一条**方向分量**：对每个 drifted tracked 文件比 `work blob` vs `HEAD blob`，若 work 是 HEAD 的真子集（`lines_only_in_head>0 且 only_in_work==0`，或行数下降 ≥N）则从 `warn` 升 `hard alert + 快照留存`。§③ 实测该哨本已在 20:40:05 看见 531 drifted，只是没有方向尺。**同一把尺必须先装在 B5 的 `git add` 之前**（`:175-215`）——实测该护盾会在会话零动作时把池面当下字节写进共享 index（§③ 窗后活体观测），即它今天已具备"把回退固化到 index"的能力，只是覆盖面限于 untracked 的 `docs/_working`。
  3. **提交前门禁层（own-scope）**：pre-commit 对**本袋 own-diff 路径**复用 `_snapshot_head_regressions` 尺（见下），拦"把已落地件写成子集"的袋。
- **判据（量化）**：必须用**三方**尺，不能用两方。在册真源已把这条钉死——`scripts/commit_queue.py:2967` 的 docstring 原话：`regress = (dev_lines − bag_base_lines) − snapshot_lines`，并注明"若写成两方 `dev_lines − snapshot_lines`，则本袋自己正当删改的行也全数计成回归——**实测 26 件里误报 17 件，闸就废了**"；`item_base_head` 取不到时保守取全量并打 `base_compared=False`（方向＝只收紧不放宽）。
  §④ 本车道为定性而用的两方数（`only_in_head`/`only_in_disk`）**只适用于池面**（盘/暂存面相对 HEAD 没有"本袋正当删改"这一维），照抄到袋侧就会复现那 17 件误报。池面侧建议判据：`only_in_head > 0 且 only_in_work == 0`（严格真子集，本案 1/4 件）或 `only_in_work / only_in_head < ε`（近似子集，本案 3/4 件）；袋侧一律走 `_snapshot_head_regressions` 的三方口径。
- **own-scope 与否**：写者层与哨兵层 = **全池扫描**（池面回退天然是跨会话现象，own-diff 看不见别的写者干的坏事），须按根宪法 §3.3 在 `gate_registry.yaml` 登记"全仓扫描"理由 + perf 分级；提交前门禁层 = **own-scope**（只查本袋路径），他会话 staged 违规走 warn+审计（根宪法 §3.1）。
- **会不会误伤合法的"真源回退"场景**：会，且必须留正门。已识别的合法方向性场景至少四类——① 轨 B 概念级退役/治理资产墓碑制（根宪法 §5.2）带来的文件级删除与收缩；② YAML 注册表三向合并后的**合法减行**（本案 A4 的 registry 族已有合并保护，不应重复拦）；③ 生成器再生产物（`data/**/latest.json`、投影册、机生门牌）字节抖动；④ 显式申请制的降级直改 / `requeue` 重放旧袋（`scripts/commit_queue.py:3191` 正是为这条留的通道）。⇒ 判据必须带**白名单逃生**：显式 `[pool-regression-ack:<reason>]` 标记 + 裁定号或 Owner 授权旗，且留痕进审计册。
- **可复用在册零件**（§⑤ 已实测存在）：
  - `scripts/commit_queue.py:2967` `def _snapshot_head_regressions(wt, payload, *, base_ref="dev", item_base_head=None)` ——三方 `lines_only_in_head` 尺的**现成实现**；全仓 grep 命中仅 `:2967`（定义）+ `:3191`（唯一调用点，在 **requeue 路径**，配套报文 `:3196`/`:4759-4768` 提示"或先 `git checkout dev -- <件>` 重基本袋再投"、清单随 `snapshot_regressions` 披露）。**缺口三条**：① 入队（enqueue）与落地（landing）两侧**零接线**（§② A4/A7 的写盘点都不调它）；② 输入面是"袋 payload vs dev"，**不读主区池面**（既不读 `repo_root/rel` 的 work 字节，也不读 index 字节）——本案 damage 恰在"池面 vs HEAD"这一维，复用需把 payload 换成 (work_bytes, index_bytes) 双读；③ `base_ref` 缺省硬编码 `"dev"`，而实测主区当前 `HEAD=dev=dce5ae9d2c…`（`branch --show-current`=dev）只是巧合成立，各车道 worktree 的 HEAD 是 `session/*` 分支（`git worktree list` 实测 10+ 支，如 `.aidrafts/st-mineloop-20261010` @ `7f8bb84fe5`），任何在车道内跑的调用都会拿错基底。
  - `scripts/commit_queue.py:1916` `ghost_gate_counts()`（只读快照，返回存活闸各出口累计计数）与 `:1922` `reset_ghost_gate_counts()`（**测试隔离接缝，生产不清零——累计数即幽灵闸账**）——可复用作方向闸的**"出口是否真被走到"体检面**（防新闸成幽灵闸），不是回退尺；同文件 `:1930` `_ghost_liveness_audit` 提供 JSONL 追加的"裁决不得静默"留痕通道。
  - `src/zephyr/shared/io/audit_jsonl_writer.py` + `.runtime/worktree_ops_log.jsonl` 遥测面（B3 `:245-262` 的 pre-hash 落盘模式）——方向闸的**证据面**可沿用同一 op/session_id/source/content_hash 结构；注意实测缺陷：窗内两条遥测的 `session_id` 都是**空串**（`os.environ.get("ZEPHYR_SESSION_ID","")` 未置位），gate 提案需同时要求写者把 sid 填上，否则"owner 责任制"（根宪法 §3.4）落不了地。
- **门位**：**AI 可放**（判据机械、纯只读观测 + 拒绝写，不改真源、不删资产），符合根宪法 §5.3"medium/low 全自动，分级不放松 gate"。仅两处须 **Owner 门位**：① 逃生白名单里"允许池面相对 HEAD 后退"的**规则册/裁定册例外**（触及根宪法 §5.1 保留面的规则数据）；② 若把闸做成**硬阻断主区历史写操作**（涉及不可逆拦截面）。本车道不下裁定。

## ⑦ 残余与下一步

1. 【查无】肇事写者仍未点名。下一步唯一能定名的三条证据面（本车道权限内做不了或需新窗）：
   - Windows 侧文件审计（SACL/4663）或磁盘级 mtime 序列：对 `code_drift/DISK__*` 的 28 件反查 20:36–21:05 的**写入进程**；
   - `.git/objects` mtime 分布：`git add`/`read-tree` 会在对象库留新对象，按 mtime 切窗可判"窗内是否有 blob 写入"；
   - `git fsck --lost-found`/dangling blob 普查：可判定盘旧字节 `3fd5c015…`（第三态）到底来自哪个车道的一次性物化。【实测】本车道**未执行**这三项（fsck 会写 `.git`，超出只读授权）。
2. 【实测】已知残余红与本窗无关：`MANIFEST.md` 记 `test_resource_schedule_mem_ceiling_invariant.py` 5 failed（T7 真源未落 + config 新生代未提交 + 常驻体口径），且 `config/resource_profile_registry.yaml`、`src/zephyr/frontend/dashboard/web/features/resourceweek/rw-data.js`、`scripts/backtest/factory_grid_executor.py` 三处被判定"非回退"未触碰——但 `rw-data.js` **同时**出现在 `code_drift/` 双面归档里（判"一度误复位、已从归档原样放回"），该项归类请复核班再验。
3. 【实测】本案卷自身即在被拍面之内：`docs/_working/maint3_campaign/` 目录此前不存在（`ls` 报 No such file or directory），由本车道随本案卷创建；该目录属 `.runtime` 之外的 `docs/_working/`（TTL 临时区），在哨兵未装方向尺前，本案卷同样可被"逐件拍旧"而不被任何闸看见——这是"门吃自己文档"（根宪法 §1 补充铁律 GATE-SELFDOC）的又一例。
4. 【实测】写盘情况：本案卷的 `Write` 调用**成功落盘**，未遇 CREATE-GUARD / 门拦截（门在提交时评估，本车道不提交，故无 `creation_token` 可依）；若后续总包提交本案卷被 CREATE-GUARD 拦，需按在册正门补登 `creation_token`（`tests/` 之外无豁免），本车道**未伪造**任何 token 或 `[TTL]` 标记。
5. 【推断】建议下一步（不在本车道权限内）：把 §② 的 A7/A4 写入点与 §⑥ 的写者层判据合到同一施工袋（同域、gate+自家测试同批，根宪法 §2.4），并顺手补 `snapshot_regressions` 尺的 **enqueue 侧接线**（现仅 requeue 跑，实测调用点唯一 = `scripts/commit_queue.py:3191`）。

## 落盘受阻

【实测】无。本案卷两次 `Write`/多次 `Edit` 全部成功；未遇 CREATE-GUARD、TTL 标记、`creation_token`、GATE-SELFDOC 或任何门的拦截报文（写盘路径 = `docs/_working/maint3_campaign/30_pool_rollback_rootcause_casefile.md`，frontmatter 含 `ttl: task_bound`，无 `doc_type` 字段，文件名纯 ASCII，非 `.json`）。本车道未伪造任何 token 或豁免标记。临时工作区仅 `.runtime/tmp/maint3_pool_rc/`（一度写 `head_side.tmp` 供行集比对，已删）。
