---
ttl: task_bound
completes_when: "波 4 灾备链四包（4.1 身份复验 / 4.2 只读位与汇总判据 / 4.3 hardlinked 定性 / 4.4 P-26 分组事实表）改码+红证+登记需求三件齐"
---

# 波 4 · 灾备与冷存链案卷（dr_chain_report）

- **turn_budget**：本包预算 ≤45 工具轮；实测约 40 轮（含 3 次红蓝重跑），明细见文末「执行流水」。
- **verified（实测，命令原文+输出在对应小节）**
  - P-28 缺陷面：`_reap_incubated_expired()` 杀前只验 PID 在进程表存在（HEAD 版 L1004
    `pid not in live_pids`），登记侧 name/cmd 只用于白名单比对，`create_time` 从未参与身份判定。
  - 内收对象在册：HEAD 版 `kill_ghost_windows()` L717-736 **已有** kill 前复查机制
    （重取现场快照 + 重跑判据 + 不符赦免）⇒ 4.1 复用该判据思路，未另造第二套复查框架。
  - 平台事实：PowerShell 5.1.26100.6899 `New-Item -ItemType HardLink` **可用**（建链后
    `fsutil hardlink list` 计数=3）；`[System.IO.File]::CreateHardLink` 在本机 .NET 侧不存在。
  - 现网读数：370 份 `logs/backup_report_*.json` 最近 14 轮普查——Mode A 轮（prev≠day）
    **hardlinked=234,299**，13 个 Mode B 轮（prev==day）全部为 0。
  - P-26 现树实测（只读 17.4s）：全树条目 1,607,337 / 文件 1,390,160；`.worktrees` 文件
    677,208；生效排除清单确无 `.worktrees`（命中排除的是 `.aidrafts`/`.runtime`/`.git`/`tmp`/
    `.ruff_cache`）。
- **assumed（未实测，标假设）**
  - `spawned_at`（孵化登记时刻）与子进程真实 create_time 偏差在秒级——incubator 先 spawn
    后 `time.time()`（process_incubator.py L322-336 代码读得，未做时序实测），故容差取 5s。
  - 案卷 B 3.1/3.2 的 06:00 轮读数未被本包逐字复核（本包只普查 code_backup 关键字段）。
- **input_set_disjoint_with**：同车道兄弟包 4.5（演练库/DR 可恢复性）、4.6（keep 卫生 +
  shadow 记账后半）、4.7（六图防回退锚）；本包仅写 `src/zephyr/trading/process_reaper.py`、
  `scripts/backup/backup.ps1`、`tests/infrastructure/`、`tests/backup/`、本目录两份文件
  （+ `.runtime/tmp/` 临时探针，非交付面）。未触 config/、未触 F:/G:、未触热册与规则册。
- **evidence_ref.cmd**：每节「命令原文」块＝可复跑凭据；未落盘输出＝判据未跑。

---

## 4.1 P-28 收割器杀前身份复验（Z-23）

**改了什么**（`src/zephyr/trading/process_reaper.py`）

1. `identity_mismatch_reason(rec_name, rec_cmd, rec_born_at, live, slack_s=5.0)` 纯函数判据，
   拆为三个模块级 helper（各 cc≤7、参数≤3）：`_born_mismatch`（create_time 第三要素，
   PID 复用主判据）/ `_image_mismatch`（镜像名）/ `_cmd_mismatch`（命令行），另加两个归一器
   `_norm_cmd_for_compare`、`_norm_image_name`。
2. `_incubation_prekill_skip_reason` + `_spare_incubated_mismatch`：闸门→命中即写
   `report.identity_mismatches` shadow 记账 + WARN，**不回写 reaped**（收敛仍归孵化方）。
3. `_reap_incubated_expired(..., recheck=None)` 新增 recheck 形参；`_reap_cycle` 在动杀前
   传入 `_snapshot_all_processes()`（本轮唯一一次额外进程枚举）。缺 recheck 时退化为
   改前语义（单测/降级路径），故兄弟包既有测试零连坐。
4. `ReapReport.identity_mismatches` 字段（自动进 `.runtime/process_reaper/last_run.json`）。

**实测中改判的一处**（内收纪律要求，非臆造）：登记侧 `name` 按 process_incubator 语义是
**孵化名（人读标签）**而非镜像名（现证：`tests/trading/runtime/test_process_reaper_incubation.py`
登记 `name="sleeper"` 而活体是 python），直比会误赦真垃圾/误杀无辜。故镜像维度取
「登记标签 ∪ cmd[0] 镜像」任一命中即认定相符，两侧同尺度归一（去引号 / basename / 去 `.exe` / 小写）。

**三例红蓝对撞（含改前红证）**

命令原文：

```
export PYTHONPATH=D:/ZephyrAlpha/.aidrafts/st-final-build-20260926/src
git show HEAD:src/zephyr/trading/process_reaper.py > .runtime/tmp/dr_old_head/src/zephyr/trading/process_reaper.py
python .runtime/tmp/dr_p28_probe.py     # 零真杀：_kill_pid_tree/_mark_incubation_reaped 全 stub
```

实测输出（VERDICT 段原文，全文 `.runtime/tmp/dr_p28_probe_out.txt`）：

```
A(PID 复用) 改前真走杀路径 = True [4321]
A(PID 复用) 改后赦免        = True [{'pid': 4321, 'reason': 'identity_mismatch:born_after_registration:+3100.0s>slack=5.0s'}]
B(换皮)     改前真走杀路径 = True 改后赦免 = True
C(正常命中) 改前杀=[7777]   = True 改后仍杀(无回归) = True
```

即：**旧实现在 PID 复用场景确实走到 kill(4321)**（该 PID 活体已是 svchost，登记时是 python），
正是案卷 X-08 的形态；改后同场景赦免并记账。B 例 reason=
`image_diverged:live=bash registered=['python']`；C 例改后仍杀（防"改到永不杀"的反向回归）。

回归网：`tests/infrastructure/test_process_reaper_identity_recheck.py`（6 例，含空活体条目
弃权、PID 不在复查表赦免）。命令与输出：

```
python -m pytest tests/infrastructure/test_process_reaper_identity_recheck.py \
  tests/zephyr/trading/test_process_reaper.py \
  tests/trading/runtime/test_process_reaper_incubation.py \
  tests/shared/test_process_incubator.py -q
============================= 96 passed in 11.44s =============================
```

**内收声明**：新增 8 个模块级 helper，替代对象=无（纯新增判据通道）；被吸收的旧路径=
「杀前仅验 PID 存在」这一隐式假设，未删除任何既有函数。复杂度：新 helper 最高 cc=7；
`_reap_incubated_expired` 由 HEAD 的 cc=22 升到 24（改前已 >15，属既有债，登 P2 需求）。

---

## 4.2 P-27 vault 旧副本只读位 + 单件失败一票否决改判据

**改了什么**（`scripts/backup/backup.ps1` STAGE 3 / STAGE 4；纯 ASCII、LF 行尾、ParseErrors=0）

1. 新增 shipped 函数 `Set-VaultMtime($Path,$WhenUtc)`：直赋失败时**仅清快照副本**的只读位后
   重试；仍失败则 `$script:MtimeFail++` + `$script:errors3` 逐件记账，绝不抛出中断本轮。
   两处 `(Get-Item ...).LastWriteTimeUtc = $srcMtime` 均改走该 helper。
2. 汇总判据替换 `$vaultOk = ($rcCode -lt 8) -and ($linkFail -eq 0)`（一票否决）为三态：
   - `failed` = `robocopy_exit>=8` 或 `itemTotal>0 且 linkFail>=itemTotal`（整轮零交付）
   - `partial` = 有交付但存在逐件失败（copy/link 或 mtime），逐件计数入档
   - `ok` = 零逐件失败
3. `codeResult` 新增解释字段 `snapshot_mode` / `item_total` / `mtime_failures` /
   `readonly_bits_cleared`；STAGE 4 另写 state 键 `last_backup_partial_items`、
   `last_code_backup_status`、`last_code_backup_snapshot_mode`、`last_code_backup_hardlinked`
   （加键，不改 `last_backup_status` 取值域 ⇒ 消费侧无连坐）。

**before/after 双证**（沙箱复刻，绝不触 F:/G:，零删除；被测码从 backup.ps1 原文抽取）

命令原文：

```
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .runtime/tmp/dr_stage3_sandbox.ps1
python -m pytest tests/backup/test_stage3_vault_mtime_and_verdict.py -q
```

实测输出（节选原文，全文 `.runtime/tmp/dr_stage3_sandbox_out.txt`）：

```
BEFORE copy.IsReadOnly=True copy.mtimeUtc=2026-09-26T13:10:07.0040725Z
DIRECT_ASSIGN_THREW=True :: 设置"LastWriteTimeUtc"时发生异常:…访问被拒绝
AFTER_DIRECT mtimeUtc=2026-09-26T13:10:07.0040725Z (unchanged => stamp lost)
HELPER_RETURNED=True RoCleared=1 MtimeFail=0
AFTER_HELPER copy.IsReadOnly=False copy.mtimeUtc=2026-09-26T10:10:07.0040725Z want=2026-09-26T10:10:07.0040725Z
SOURCE_STILL_READONLY=True (must stay True: only the copy is defrosted)
HEALTHY_ITEM ok=True RoCleared=0 MtimeFail=0 (must be 0/0)
```

汇总判据真值表（跑在抽取的 shipped 表达式上）：

```
measured 06:00 round (rc=0,total=336678,copyFail=0,mtimeFail=1) -> partial   [old code said: failed]
clean round                       -> ok
robocopy hard error               -> failed
every item failed                 -> failed
5 of 100 items failed             -> partial
full-copy branch, rc=0, 1 fail     -> partial   (itemTotal=0 => not vetoed as total-loss)
```

→ 台账可分离：`code_backup.status=partial` 且 `failures=0 / mtime_failures=1`，既不再一票
否决 336,678 件，也不静默忽略。测试：`9 passed in 3.69s`。

**未做（越权面）**：真实 vault 件（`G:\backup\working_vault\...`）与源侧只读件
`docs/01_policies_and_standards/sop/audit_prompts_20_ai.md` 本包**一律未改位**（禁写备份盘 +
禁写热区）。处置建议三段式（只在案卷列，不动手）：
① 标记：Owner 裁定该源件是否清只读位（或改由上游提交清位），登记入 ⚑-3 事实面；
② 物理隔离：如需保真留档，先复制为只读检疫副本再谈清位；
③ 等批文：批文后备份腿已保证只解冻快照副本、源件位不动（本次代码已具备该性质）。

---

## 4.3 X-17 `hardlinked` 恒 0 定性

**定论：不是"配置没接上"，不是"平台不支持"，是读数采样口径病——硬链接去重通道真实在产出。
声明保留（不退役），补 `snapshot_mode` 字段使 0 可解释。**

四重证据：

1. 平台：PS 5.1.26100 `New-Item -ItemType HardLink` 成功，`fsutil hardlink list` 计数=3
   （`.runtime/tmp/dr_hardlink_probe.ps1`）；vault 与 prev 快照同在 `G:\backup\working_vault`
   同卷 ⇒ 无跨卷硬链限制（NTFS 跨卷不支持是常见真相，本例不适用）。
2. 现网普查（只读）：命令 `python .runtime/tmp/dr_x17_census.py`

```
file                          status  hardlinked copied failures robocopy_exit prev==day(ModeB)
backup_report_20260925_060007 failed      234299 187513        1             0  False   <- Mode A
backup_report_20260926_060003 failed           0 336678        1             0  True    <- Mode B
backup_report_20260926_091502 ok              0    705        0             0  True
backup_report_20260926_100018 ok              0     49        0             0  True
backup_report_20260926_105457 ok              0     22        0             0  True
backup_report_20260926_120348 ok              0     19        0             0  True
backup_report_20260926_133822 ok              0     63        0             0  True
（近 14 轮汇总：TOTAL_ROUNDS_WITH_hardlinked_gt0= 1；MODE_B_rounds=13；MODE_A_rounds=1）
```

3. 机理：Stage 3 循环里 `$dstExists -and $isUnchanged -> continue` 早于建链分支；Mode B 的
   `prev_snapshot` 就是 `day_target`，未变更件必然已在当日快照内 ⇒ 建链分支**结构不可达**
   ⇒ hardlinked 恒 0。跨日首轮（Mode A）从未变更件走 `New-Item -ItemType HardLink` ⇒ 234,299。
   案卷"近 5 轮恒 0"的样本恰好全是同日轮。
4. 沙箱实测 >0 复核：`HARDLINK_COUNT=2`（同一份 seed 内容经 `New-Item -ItemType HardLink`
   挂两个路径，`fsutil hardlink list` 列出两条）。

**判据副作用（已落码）**：报告与 state 双键 `snapshot_mode` + `last_code_backup_hardlinked`，
审计应读「Mode A 轮 hardlinked 是否 >0」，而非任意轮——否则"写了就当有"换成"读了就当没有"。

---

## 4.4 P-26 定性：顶层目录分组复制清单（只出事实表，禁改排除清单）

命令原文：`python .runtime/tmp/dr_p26_census.py`（只读遍历 `D:\ZephyrAlpha`，17.4s；输出
`.runtime/tmp/dr_p26_out.txt`）。口径＝复刻 `Get-SourceFileIndex`：按名在任意深度跳
`exclude_dirs`、跳 reparse point、按模式跳 `exclude_files`。

生效清单原文（`scripts/backup/backup_config.yaml` L34，**本包未改**）：
`['.git','node_modules','__pycache__','.pytest_cache','.mypy_cache','.ruff_cache','.runtime','.aidrafts','tmp','.venv']`
⇒ `.worktrees` 不在清单内（与案卷 X-09 一致）。

分组事实表（按在备文件数降序，条目=含目录的全部文件系统项）：

| 顶层项 | 全树条目 | 文件 | 目录 | GiB | 在备文件 | 是否被排除清单命中 |
|---|---|---|---|---|---|---|
| `.worktrees` | 780,085 | 677,208 | 102,877 | 7.524 | **676,784** | 否（未列） |
| `.aidrafts` | 612,631 | 538,079 | 74,552 | 5.856 | 0 | 是 |
| `.runtime` | 160,271 | 125,001 | 35,270 | 7.053 | 0 | 是 |
| `data` | 21,700 | 21,128 | 571 | 5.066 | 21,114 | 否 |
| `docs` | 9,895 | 8,509 | 1,386 | 0.184 | 8,509 | 否 |
| `.git` | 8,287 | 7,664 | 623 | 1.309 | 0 | 是 |
| `src` | 4,995 | 4,042 | 953 | 0.039 | 4,040 | 否 |
| `tests` | 4,394 | 3,872 | 522 | 0.032 | 3,872 | 否 |
| `scripts` | 1,539 | 1,372 | 167 | 0.018 | 1,372 | 否 |
| `tmp` | 1,165 | 1,098 | 67 | 1.006 | 0 | 是 |
| `logs` | 624 | 557 | 67 | 0.058 | 557 | 否 |
| `models` | 76 | 69 | 7 | 14.288 | 69 | 否 |
| `vendor` | 126 | 102 | 24 | 0.322 | 102 | 否 |
| 其余（顶层零散件/目录） | ~550 | ~500 | — | <0.05 | ~500 | 否 |

汇总读数（口径全部注明，禁裸数）：

- 全树：条目 1,607,337／文件 1,390,160／42.84 GiB。
- 在备口径（生效排除清单后）：文件 717,647／27.608 GiB。
- `.worktrees` 占**全树文件** 48.71%（677,208/1,390,160）、占**全树条目** 48.53%
  （780,085/1,607,337）、占**在备文件** **94.31%**（676,784/717,647）。
- 反事实（仅供 ⚑-3 拍板，本包未改清单）：若 `.worktrees` 入排除清单 ⇒ 在备文件
  717,647 → 40,863（**−94.31%**），在备 GiB 27.608 → 20.084（−27.3%）。
- 两个"目录数"口径必须分开写：`.worktrees` 一级目录 **62**（磁盘项）vs
  `git worktree list --porcelain` **84**（注册项）——与案卷 X-09 的 52/73 同族病，
  一切统计须注明取哪一侧。
- 06:00 轮 `copied=336678` 与本案相符性：Mode B 同日轮出现全量级 copied ⇒ 当日 day 目录
  起跑时缺内容（`$dayHasContent` 判假），故 336,678 是"当日快照首次填充"的增量计数而非
  二次抖动；`.worktrees` 在备文件 676,784 与 336,678 同数量级（其半）——两者是否同一集合，
  本包未逐件比对（登记 P2，需 diff 采样才可定论）。

**结论喂 ⚑-3 的事实面（不含建议改写）**：备份条目压力 94.31% 来自 `.worktrees`，
字节压力仅 27.3%（条目多而碎）；`.aidrafts`/`.runtime`/`tmp` 已在排除清单内。

---

## 执行流水与未做项

- 工具轮（约 34）：环境/文档 6 → 代码定位 4 → 4.1 改码+探针+测试迭代 9 → 4.2/4.3 改码+沙箱 6
  → 4.4 普查 3 → 落盘 4。
- 本包**未做**（越权或超预算，已入 `registration_needs.yaml`）：
  1. 4.5/4.6/4.7 三包（演练库、keep 卫生、六图防回退锚）不属本包路径，未触碰；
  2. 真实 vault / F:/G: 侧任何写操作与清位（禁）；`git worktree` 注册面与快照件的逐件 diff 比对；
  3. `_reap_incubated_expired` 既有 cc=22 的拆解（改前既有债，动它=侵兄弟包面）；
  4. 热册登记（depgraph 节点、module_translation、gate 注册）——本包只出
     `registration_needs.yaml` 需求清单，未直写 `docs/01_policies_and_standards/**`；
  5. 任何删除/杀进程/停任务动作：全程零 kill、零删除、零 schtasks。
- 案卷件自身：`tests/infrastructure/test_process_reaper_identity_recheck.py`、
  `tests/backup/test_stage3_vault_mtime_and_verdict.py`（新建，tests/ 豁免 CREATE-GUARD，
  但需 module_translation 登记——已列 P1）。
