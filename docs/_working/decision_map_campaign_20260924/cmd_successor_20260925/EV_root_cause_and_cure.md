---
ttl: task_bound
campaign: decision_map_campaign_20260924
title: LANE-EV 蒸发案根治：20:55 复发锁窗、根因定性、EV-01~06 核账与治本施工
date: 2026-09-25
author: 蒸发案根治车道 LANE-EV（总筹 st-qmine-20260925 统筹；本车道只施工本案）
status: delivered
---

# EV_root_cause_and_cure.md — LANE-EV 案卷

> 一句话：**本轮（09-25 16:12-16:16 主区 `docs/_working/decision_map_campaign_20260924/` 整目录蒸发）
> 不是 10 号文点名的"落地链 clean 打穿主仓"，而是仓内删除护栏 `ops_guard` 对
> POSIX sh/MSYS `rm -rf` 的识别盲区**——同一把刀已经砍了三个夜班。EV-02 的 TOCTOU 另经
> 受控复现证实为**独立且仍然敞口**的第二个洞，本卷一并给出补丁与证尺。

## §1 时区对表（先做，否则一切先后判断作废）

| 证据面 | 时区口径 | 实测校准 |
|---|---|---|
| `.runtime/evaporation_blackbox/blackbox.jsonl` `ts` / `ts_local` | ts=UTC，ts_local=+08:00 | 末帧 ts=2026-09-25T12:56:01Z ↔ ts_local=20:56:01+08:00 ✓ |
| `.runtime/audit/worktree_drift_watchdog.jsonl`、`safe_write.jsonl`、`hook_tracked_drift.jsonl` | ISO 带 `+00:00` = **UTC** | watchdog 12:56:25Z 记 HANDOVER.md，与黑匣子 20:56:01 本地同秒族 ✓ |
| `.runtime/commit_queue/main_workspace_sync.jsonl`、`write_audit.jsonl` | **epoch 秒**（本地时钟解释） | 1790336223 → 2026-09-25 19:37:03 本地 ✓ |
| `.runtime/quarantine/drift_<ts>` 目录名 | UTC（10 号文 §① 口径复证） | drift_20260925T123415 目录 mtime=20:34 本地 ✓ |
| NTFS creation/mtime（python `os.stat`） | 本地 | 27 件回填出生时间 20:52:19 本地 ✓ |

结论：**报"某事在几分发生"前一律折到本地**；下文全部用本地时刻（括注 UTC）。

## §2 锁窗口：16:12:11 → 16:16:02（本地，=08:12:11→08:16:02Z），宽度 3 分 51 秒

黑匣子 EV-01 只有聚合计数，**这一轮它没能锁窗**（见 §3 假绿面）；窗口由三方交叉夹逼：

| 时刻(本地) | 证据 | 含义 |
|---|---|---|
| 16:02:53 | 主 reflog + `git log --diff-filter=A`：`8b8f494465` "watchdog 派生缓存自动收敛 44 件" | 27 件经 B2 护盾 `auto_staged` 后由 watchdog A2 自融入 HEAD（战役目录第一次"在册"） |
| 16:11:02 | 黑匣子帧：modified=791，untracked=152 | 蒸发前基线 |
| **16:12:11–16:12:27** | watchdog `verdict=healed` ×25（战役件）+ COVERAGE.md/cmd_ledger 各 1 | healed 的判据是"本轮不再出现在 dirty 集" ⇒ **此刻 27 件仍在盘上且与 HEAD 一致** |
| **16:16:02** | 黑匣子帧：modified 791→**833**（+42），untracked 152，HEAD 未变（8b8f4944） | ~40 件 ` D/AD` 行进入 porcelain ⇒ **此刻已经没了** |
| 16:19:10–16:19:22 | watchdog `deletion_observed` ×40（首见容忍，不告警） | 下轮仍缺 |
| 16:31:01–16:31:33 | watchdog `deletion_alerted` ×40 + 批量删除汇总 | 升级为 critical_warn（值守无人接） |
| 19:24:00 | 战役目录 NTFS 出生时间 | 整目录被抹后由新 19 号文**重建目录**（不是只删文件） |
| 20:52:19 | 27 件 + `links/` 及其全部 L0x 子目录出生时间 | 总筹 `cp -rn` 回填（LEDGER 写 20:55，实为 20:52:19；差 3 分，勿据 LEDGER 断言先后） |

**机制判据（决定性）**：`links/L01..L09` 等**目录本体**出生时间=20:52:19 ⇒ 被删的是**目录子树**，
不是逐文件删除；且同目录内 19 号文（19:24 建）与 HANDOVER.md（20:45 建）在 27 件蒸发后仍存在
⇒ 删除动作发生在它们出现之前、且一次性带走整棵 `decision_map_campaign_20260924/`。

## §3 假绿面：EV-01 黑匣子为什么这次没锁住窗（已治，见 §6.2）

1. **无 per-path 见证**：只记 untracked/modified/porcelain 计数。16:12→16:16 那 +42 与同期
   commit/暂存变动互相抵消，16:21-20:46 段 modified 稳在 824——40 件蒸发在计数里就是噪声。
2. **既有实现有静默错计**（本卷单测打红后修复）：`_git_ok()` 对 stdout 做 `.strip()`，
   吃掉 porcelain **首行的前导空格**；XY 状态位全靠首字符，首行恰为 ` D`/`??` 时
   被错归为 modified ⇒ `untracked_count` 少算、新加的 `tracked_deleted_count` 恒 0。
   红证：`test_snapshot_records_tracked_deleted_paths` 修复前 `tracked_deleted_count==0`。
3. 因此"EV-01 已上线"≠"EV-01 能锁窗"——15 号文 EV-01 验收行写的是"精确定位分钟级现场"，
   本轮实测**未达标**，已按验收行补齐（per-path 三字段 + `--lock-window` 模式）。

## §4 嫌疑排除与定性（逐条给反证，不给印象分）

| 嫌疑 | 判定 | 依据 |
|---|---|---|
| 落地链 `_sync_worktree` 的 `clean -fd` 打穿主仓（10 号文 S1，65%） | **本轮证伪** | ① 27 件自 16:02:53 起在 HEAD+index 在册，`git clean` 永不删 tracked 件；② 15:52:56→16:21:14 无袋落地（done/ 无 landed_at、`main_workspace_sync.jsonl` 该窗零记录）；③ pool_wave.log 16:1x 只有 `claim_none` 空转；④ `.git` 侧零写入、主 reflog 该窗零 reset/checkout 条目 |
| session worktree merge 流 `_pre_merge_auto_clean`（S2） | **本轮排除** | `.runtime/worktree_ops_log.jsonl` 15:50–16:40 **零记录**（worktree_delete/file_stash/file_quarantine 三个删除点全部有遥测）；`.runtime/orphan_quarantine/` 为空 |
| drift watchdog A1 死会话卸 staged（S3） | 非删除者，但是**"13 件从此 invisible"的成因** | 19:2x 本地该 13 件 verdict=healed ⇒ 它们脱离 dirty 集 = index 条目被卸（`git reset HEAD --`），此后 HEAD 无、index 无、盘上无 ⇒ git 视野里根本不存在，LEDGER N-1 的"不在 HEAD"即此形态 |
| reconciler 清扫 gate 族（S4） | 本轮排除 | 该窗无 `reconcile_worker_*.log` 新件；清扫作用域 tmp/.runtime staging |
| **`ops_guard` 删除护栏的 POSIX sh/MSYS `rm -rf` 盲区** | **判定为本轮根因，置信 ~80%** | 见 §5；唯一同时满足"git 侧零痕迹 + 护栏零审计 + 目录子树整删 + 只删目录不挑 tracked/untracked"的机制 |

> 未达 90%+ 的原因（如实）：**没有进程级证据**。本机 AI 执行面是 Git Bash，shell 级 `rm`
> 不经任何仓内代理，无 PID/cmdline 落痕；能把"谁在 16:1x 执行了 rm"钉死的只有 Windows
> 文件系统审计（4660/4663 未开审计策略，`fsutil usn` 需管理员）。缺什么见 §8。

## §5 实测根因：护栏认识 `Remove-Item -Recurse`，不认识 `rm -rf`

对 `analyze_delete_command()` 直接跑现场命令族（修复前实测）：

| 命令 | 修复前判定 | 应为 |
|---|---|---|
| `rm -rf docs/_working/decision_map_campaign_20260924` | **allowed=True**，primitive=powershell_recurse，is_recursive=**False**，targets=`['-rf', 'docs/...']` | 拦 |
| `rm -r` / `rm -fr` / `rm --recursive --force` / `rm -rf ./docs/...` / `rm -rf docs/_working` / `rm -rf src` / `rm -rf tests/governance` / `rm -rf .worktrees` | **allowed=True**（同族 12 条全通） | 拦 |
| `rm -rf /d/ZephyrAlpha/docs/_working/...`（MSYS 绝对路径） | allowed=True（`/d/…` 被当相对路径拼 cwd ⇒ 解析成 `D:/d/ZephyrAlpha/…`，任何仓内前缀都不命中） | 拦 |
| `find docs/_working/<战役> -type f -delete` | allowed=True，primitive=unknown | 拦 |
| `Remove-Item -Recurse -Force docs/...` / `del /s /q` / `git clean -fd` / `shutil.rmtree('docs')` | allowed=False ✓ | 拦 |

病根两条（都在 `scripts/ops_guard.py`，唯一真源，未另起炉灶）：
1. `_detect_primitive` 把行首 `rm` 一律当 **PowerShell 别名**走 `_extract_ps_targets`；
   该解析器只认 PS 开关，`-rf` 被当"未知 `-` 前缀 token=目标"吞掉 ⇒ 递归标志恒 False
   ⇒ `_judge_protected` 对非递归直接放行 ⇒ `docs` 是保护区却根本没被判定。
2. `_normalize_path` 不认 MSYS 盘符 ⇒ `/d/ZephyrAlpha/...` 逃出仓内前缀匹配。

红队既有 INVARIANTS 写的是"攻击向量 100% 被拦"，但向量清单里**没有一条 POSIX sh `rm`**
（只有 `rm -Recurse -Force` 这种 PS 拼写），所以盲区带着"100% 达标"的绿章活到今天。

## §6 治本施工（本轮落地清单）

### 6.1 EV-07（新增项，实测根因面；内收进 `ops_guard`，零新脚本/零新 gate）

`scripts/ops_guard.py`：
- `_normalize_path`：`/([a-z])/…` → `X:/…`（MSYS/Git Bash 盘符）。
- 新增 `_extract_sh_targets` / `_extract_find_delete_targets` / `_PS_STYLE_SWITCH_RE`；
  `_detect_primitive` 前置 sh 分支（`rm|unlink` 且非 PS 拼写）与 `find … -delete` 分支；
  开关不可解析 ⇒ **fail-closed 按递归处置**。
- 新增 `_fail_closed_protected_hits`：原语解析不出但"删除动词 + 递归开关 + 点名保护区"
  三条件同时命中 ⇒ 拦（`primitive=delete_unparsed_failclosed`）。杜绝"新增一种 shell
  写法就再开一个洞"的猫鼠结构。
- 新增 `_tracked_in_head_count`：**任务书硬约束的机械落实**——保护区批量删除的判定
  必附 `tracked_in_head=<n>`（`git ls-files` 计数）写入 `reason` 并随
  `audit_delete` 落 `.runtime/gate_audit/ops_guard_delete.jsonl`；阻断面记证据，
  授权放行面（`ZEPHYR_FORCE_DELETE=1`）同样留证。
- 头 `[INVARIANTS]`/`[MODIFY-GUARD]` 同步（护栏字段面与红队向量族联动）。

**内收声明**：本项**不新增** gate/脚本/注册册；它替换的是"新增一条 `GATE-SHELL-RM-WATCH`
独立门禁"的方案（该方案违 §4 全资产净零）。它合并的旧条目=
`PROTECTED_PREFIXES` 已有的 docs/src/tests/.worktrees 保护区判定（同一判定面，只补
原语识别，不建第二真源）。

### 6.2 EV-01 强化：黑匣子补 per-path 删除见证

`scripts/governance/evaporation_blackbox.py`：
- 新字段 `tracked_deleted_count` / `tracked_deleted_paths`（封顶 200 + `truncated` 标志）
  / `tracked_deleted_sig`（sha1 全集指纹，不受封顶影响）；零新增 git 调用（复用同一次
  `status --porcelain`），只读不变量与 fail-soft 不变。
- 修 §3-2 的 `.strip()` 错计（首行前导空格被吃）。
- 新 CLI `--lock-window <path片段>`：对命中路径打印"存在→缺失 / 缺失→回填"的帧区间，
  即本卷 §2 手工拼的东西，今后一条命令出结果。参数面板抽成 `_add_args` 便于装配测试。
- 头 `[BLUEPRINT]` 由 `MOD-GOV` 改 **`MOD-GOV_SCRIPTS`**（与 `[DOMAIN] D_GOV_SCRIPTS`
  对齐；42 个同目录脚本与 `scripts_registry.yaml` owner_module 均此值，N-17 写入自检实证）。

### 6.3 EV-02：落地器 `_git_wt` 破坏性动词护栏（check-then-act → check-act-verify）

先给**受控复现**（未打补丁的真实 `_git_wt`，tmp 仓）：校验通过后摘掉 worktree 的 `.git`
指针，再执行 `_sync_worktree()`：

```
RESULT: _sync_worktree 未报错（守卫未拦住）
AFTER   main staged-new exists: False   ← 他会话在飞成果被物理抹除
AFTER   base.txt 被还原? True            ← 他会话未提交修改被回滚
AFTER   main index lines: 1（原 2）      ← 正是 10 号文"index 条目蒸发"形态
AFTER   main reflog: … reset: moving to refs/heads/dev
```

补丁（`scripts/governance/commit_queue_landing.py`，只动 `_git_wt`/`_sync_worktree`/
新增两常量+一异常类，不碰他车道在改的 registry family/_pool_process_item 区）：
- `_wt_gitdir()` + `_wt_pin_args()`：破坏性动词 MUST 显式带 `--git-dir/--work-tree`
  ⇒ **结构性关闭 walk-up 通道**（不再依赖"检查时链接还在"）。
- `_main_fingerprint()`：主仓 HEAD sha + 在册件存在性抽样（`ls-tree -r` 实测 0.083s，
  按 HEAD 缓存，≤60 件纯 stat）。
- `_verify_no_punchthrough()`：执行后三判据（钉死参数下 toplevel/gitdir 仍回本 worktree、
  主仓 HEAD 未动、抽样在册件未成片消失≥2 件、`.git` 指针仍在）⇒ 违任一即
  `WorktreePunchThroughError` + 审计 `.runtime/audit/landing_guard.jsonl`
  （`event=gitwt_punchthrough`，含 verb/gitdir/HEAD/问题清单）。
- `_sync_worktree` 的 clean 容错分支加 `except WorktreePunchThroughError: raise`
  ⇒ 打穿告警不再被"瞬态竞态降级 warning"洗掉（旧口径的静默通道）。
- 阈值取"≥2 件成片消失"而非 ≥1：他会话并发删单件是常态，宁可漏判单件也不制造落地器
  误闸，漏判面由 §6.2 的 per-path 见证 + watchdog 兜住。

**内收声明**：EV-02 不新建 gate/脚本，落在 15 号文指定落点；`WorktreePunchThroughError`
替换的是"继续用裸 RuntimeError + 日志降级"的旧口径。

## §7 证尺（每条都先红后绿，禁自我盖章）

| 尺 | 红（缺陷存在时） | 绿（修复后） | 复核命令 |
|---|---|---|---|
| 红队向量族扩 POSIX sh 14 条 | **15 failed / 101 passed**，拦截率 75.0%（42/56） | **116 passed**，拦截率 100% | `python -m pytest tests/governance/test_ops_guard_red_team.py -q` |
| 端到端 CLI：`ops_guard check "rm -rf docs/_working/decision_map_campaign_20260924"` | rc=0 放行 | rc=1 阻断（primitive=sh_rm_recurse） | 同上文件 `TestGuardCliUsable` |
| EV-01 per-path 见证（含 `.strip()` 错计） | `tracked_deleted_count==0`（字段缺失/首行错归） | 4 passed | `python -m pytest tests/governance/test_evaporation_cure_lane_ev.py -q` |
| EV-02 argv 钉死 + TOCTOU + 打穿审计 | 修复前 `_sync_worktree` 不报错且主区 staged-new 被抹（§6.3 实录） | 7 passed（含 `--git-dir/--work-tree` 断言、竞态后主区零损失、审计行落盘） | 同上 |
| 落地链回归 | — | `test_commit_queue_landing.py` 69 passed / 1 failed；`test_commit_queue_pool.py` 15 passed（141s，默认 120s/件超时会被慢件撞，非死锁） | 见 §9 |

唯一失败件归因：`TestRegistryMergeCompoundIdentity::test_true_duplicate_compound_key_still_deadletters`
——其判据函数 `_index_family_blocks`/`_scalar_family_keys`/`"身份不唯一"` 全部在
**他车道在途 diff**（`git diff` 该文件 325 insertions，命中 394–921 与 2821–2887 两段，
不含 `_git_wt`/`_sync_worktree`），与本车道改动无交集，不代修（宪法 §3.4 owner 责任制）。

## §8 EV-02~06 核账（读代码现状，不采信"已批＝已做"）

| 项 | HEAD/盘上现状 | 本车道处置 |
|---|---|---|
| EV-01 黑匣子 | 已上线（`scripts/governance/evaporation_blackbox.py` + schtasks 5min），但**锁窗能力不达标**且有 `.strip()` 错计 | §6.2 已治 |
| EV-02 `_git_wt` 执行后验证 | **未落地**（原为纯 check-then-act），已实证可被打穿 | §6.3 已落地 |
| EV-03 landing 守恒断言（落地前后 `git diff --cached` 对账） | **未落地**（全文件无 `diff --cached` 对账面；`main_workspace_sync.jsonl` 只有 `skipped_dirty`/`error` 两态，无差集校验） | **未做**——理由：本轮实测删除者不是落地链，且该文件他车道在飞；处方保留见 §10 |
| EV-04 worktree `.git` 链接守卫 | **部分已落地**：GATE-ROOT-TEMP-SWEEP 侧已把 worktree 的 `.git` 指针文件排除扫描面（`reconciliation_registry.py` 10784-10787 注释与白名单实装）；serializer 启动四 worktree 链接自检**未见** | 自检面并入 §6.3（`_wt_gitdir` 每次破坏性调用即校验指针与 gitdir 存在性），不另建 bootstrap 探针（避免第二真源） |
| EV-05 `_pre_merge_auto_clean` 场景2 物理删除改保全 | **已落地**（早于本方案：`session_worktree.py:5275-5280` 走 `_quarantine_file` → `.runtime/orphan_quarantine/<sid>/`，72h 可恢复，且有 `worktree_ops_log` 遥测）；"merge abort 自动回搬"仍缺 | 未做回搬；现口径下 abort 后件在隔离区可取，且本轮 15:50-16:40 该三删除点零记录（不是本轮凶手） |
| EV-06 死会话清扫"只卸 index 不喂 clean" | **未落地**：A1 仍 `git reset HEAD -- <to_unstage>` 后 `snap.unlink()`，无回收站/refs 双存证；R3.4b 只补了 reset 前重查 claim | **未做**——但它确是"13 件从此 invisible"的成因（§4），处方见 §10，需与 watch 面一起改判据，本车道无权改判据口径 |

## §9 复核命令（任何人可照跑）

```bash
# 1) 锁窗（新 CLI，本案例应报出 16:12:11 → 16:16:02 族区间；旧帧无 per-path 见证会显式声明）
python scripts/governance/evaporation_blackbox.py --lock-window docs/_working/decision_map_campaign_20260924
# 2) 护栏盲区是否真堵住（期望 rc=1 + primitive=sh_rm_recurse）
python scripts/ops_guard.py check "rm -rf docs/_working/decision_map_campaign_20260924"; echo rc=$?
python -m pytest tests/governance/test_ops_guard_red_team.py -q
python -m pytest tests/governance/test_evaporation_cure_lane_ev.py -q
# 3) 落地链回归（逐目录跑，勿一次全量）
python -m pytest tests/governance/test_commit_queue_landing.py -q
python -m pytest tests/governance/test_commit_queue_pool.py -q --timeout=600
# 4) 本卷事实复核
git log --format='%h %ad %s' --date=iso --diff-filter=A -- docs/_working/decision_map_campaign_20260924
python - <<'PY'   # 目录子树出生时间（判"整目录被删"而非逐文件）
import os,datetime
for dp,dn,fn in os.walk('docs/_working/decision_map_campaign_20260924'):
    print(dp, datetime.datetime.fromtimestamp(os.stat(dp).st_ctime).isoformat(timespec='seconds'))
PY
```

## §10 未达标与处方（不粉饰）

1. **执行者未钉到 PID**：shell 级 `rm` 在仓内任何代理之外，本仓现有遥测抓不到。可落地
   处方（需总筹排期，非本车道权限）：开 Windows 对象访问审计（4660/4663 对
   `D:\ZephyrAlpha\docs`）或 `fsutil usn readjournal` 周期采集进 `.runtime/audit/`——
   10 号文 §④-6"计划任务审计"的同一族欠账。**判据口径与阈值本卷未改**。
2. **护栏只能拦"被送到分析器的命令"**：`analyze_delete_command` 的消费面是
   `guard_rmtree/guard_remove/guard_move` + CLI `check/exec` + 红队测试，**AI 的 Bash
   工具执行链不经过它**。本轮修复让"一旦有人问就必拦"，但"没人问"仍是敞口——真正封口
   需要 shell 前置钩子（IDE/hook 层调 `ops_guard.py check`），属提交链/工具链接入面，
   建议与 EV-03 同批改判据面，需 Owner 门位（改执行链=flag/接入面变更）。
3. **EV-03/EV-06 未做**（理由见 §8），EV-05 的"abort 自动回搬"未做。
4. **`mv <保护区> <仓外>` 仍判 unknown→放行**（`guard_move` 只覆盖 Python API 面）；
   本轮证据里没有 mv 形态，故未扩判据以免误伤，登记为已知残余。
5. **黑匣子 5 分钟粒度**：锁到的是 ≤5 分钟区间（本案 3′51″）；1 分钟需改 schtasks
   周期（计划任务变更，未擅动）。

## §11 与 15 号文的偏离（以实测为准，写清理由）

| 15 号文 | 本卷偏离 | 理由 |
|---|---|---|
| 头号嫌疑人=落地链 `clean -fd` 打穿主仓 | 本轮**证伪**，根因改判 `ops_guard` POSIX rm 盲区 | 27 件 16:02:53 起 tracked（clean 不删 tracked）；该窗无袋落地、无 .git 写入、无 reflog reset、worktree 三删除点遥测零记录 |
| EV-02~04 为治本主线 | 主线改判为 **EV-07（rm 盲区）+ EV-01 强化**；EV-02 仍做（洞经复现证实，但非本轮凶手） | "以实测为准"授权；EV-02 的价值是他会话 WIP 防护（§6.3 复现即证），不是本案止损 |
| EV-01 已达标 | 判**未达标**（无 per-path 见证 + `.strip()` 错计） | 15 号文验收行原文要求"精确定位分钟级现场"，本轮做不到 |
| 13 件"不在 HEAD 需重建"（LEDGER N-1） | 定性为 **watchdog A1 卸 index 条目**造成的不可见，非从未入库 | §4 表 + `git log` 该目录全史仅 2  commit（8b8f494465 增、610f7da6d8 改），从无删除件 |

> 取证纪律声明：本车道全程零 `git add`/`git commit`/`git push`/`enqueue`，未触碰主区
> 396 件在飞暂存；临时探针一律在 `.runtime/tmp/`（本卷 §9 的 heredoc 除外，不落盘）；
> 改前已 `lock_files.py acquire`（`commit_queue_landing.py`、`evaporation_blackbox.py`；
> 误 claim 的 `thresholds.yaml` 因它车道在飞 ` M` 已即时 release，本卷未改阈值 SSoT）。
