---
ttl: task_bound
---

# 叶簿 W-41 · P-28 收割器孵化腿杀前身份复验（PID 复用防误杀）

> 族 4（灾备与冷存）· 骨架行锚=`00_master_skeleton.md` L93（态 ⬜「P-28 收割器孵化腿杀前身份复验（PID 复用可误杀 svchost，实测今日 7 条）」，案卷 B）
> 编译：2026-09-28，会话 st-zcloseout-20260928（Agent-H），lane HEAD=`325b69a193`。
> 状态标记：🔨→✅ 待复验——**复验腿已在本会话 HEAD 实读到落地码**（M1），史基线「无复验」已成旧态；残余缺口转 §4-2/3。
> 素材真源：`dossier_B_backup_and_cold_storage.md` §一 2.1-2.5、§二 N-10、§三 G-7。

## 1. 六向台账（对象=孵化腿 `_reap_incubated_expired` 的杀前判据）

| 向 | 内容 | 锚 |
|---|---|---|
| 上游供数 | 孵化台账 `.runtime/process_incubator/ledger.jsonl`（HEAD 代码 L924 定义路径）：登记 child_pid/cmd/child_create_time/spawned_at/expected_lifetime_s | dossier_B §一 6.3（台账实测 1515 行）+ 本会话 HEAD 直读该函数读字段集 |
| 下游消费 | `killed=_kill_pid_tree(pid)` 按 PID 树杀；杀前白名单/keep 免死 | dossier_B §一 2.1；本会话直读 `killed = _kill_pid_tree(pid)` 仍在 |
| 名册声明 | 免死名单 `data/runtime/process_reaper_keep.txt`（167 有效条目）+ whitelist 正则 | dossier_B §一 6.1 |
| 读声明的代码 | 史基线：仅验 `pid in live_pids`（存在性）→ 寿命 → 白名单匹配用**台账 `rec["cmd"]`**（L1005/L1011），活体 cmdline/create_time 从未比对；对照腿 `kill_ghost_windows` L717-737 有 recheck+classify 赦免 | dossier_B §一 2.1 |
| 覆盖测试 | `tests/dr/test_backup_lock_semantics.py` 在 HEAD（5 例）属锁语义；孵化腿复验的专项测试在锚面未见 | dossier_B §一 1.8（该测试属 P-19 面） |
| 执法门禁 | 落痕审计：`data/runtime/reaper_kill.log` 逐行 name/cmd/tag；PID 复用后「实际被打断的是什么」在旧日志设计下不可事后判定（活体 cmdline 不入日志） | dossier_B §三 G-7 + §二 N-12 |

## 2. 现状实测（史基线 → 本会话 HEAD=`325b69a193` 直读）

| # | 断言 | 史基线（锚=dossier_B） | 本会话复读 |
|---|---|---|---|
| M1 | **杀前身份复验已落地** | 2.1：无复验（「不符」判） | ✅ HEAD `process_reaper.py` `_reap_incubated_expired` 内实读：`rec_ct=child_create_time` vs `live_ct=活体 create_time`，`abs(rec_ct-live_ct) > _PID_REUSE_TOLERANCE_S` → `incubation_expired_pid_reuse_skip` 跳过+reported 留痕；源码自标「PID 复用身份复核（wave7.3 缺陷②，st-zc8-lane-rb2）」；docstring「身份复核（child_create_time 快照与活体一致——PID 复用疑似则跳过不杀）」 |
| M2 | 病史（为何要复验） | 2.4：KILLED 且活体名非 python 18 行，其中 11 行 `killed=True` 活体是 backgroundTaskHost/conhost/bash（PID 认人直接后果读数）；2.3：svchost.exe 5 行 KILLED 全带 [FAILED]+15 行 DRY-RUN | dossier_B §一 2.3/2.4（log 面，G-7 注明「真杀 vs 目标自退」日志面不可分辨） |
| M3 | 治本后仍复发段 | 2.5：dc1c66e651（AccessDenied 治本）后 svchost [FAILED] 仍现 2 条（07:17:33/09:01:37） | dossier_B §一 2.5（证明 AccessDenied 修复不覆盖 PID 复用，复验腿是正解） |
| M4 | **白名单腿仍用台账 cmd** | 2.1/N-10：keep 匹配 `rec["cmd"]` 非活体 cmdline | ⚠ 本会话直读复验腿之后仍是 `cmdline = str(rec.get("cmd", ""))` → `_is_whitelisted(cmdline,…)`——台账 cmd 口径**未改**（N-14：正斜杠/反斜杠形态差使豁免不稳定） |
| M5 | 台账僵尸堆积 | 6.3：1515 行中 1324 未收口，其中 1300 条 PID 已死（98.2%）；豁免分支 continue 不写 reaped_ids=永不收口 | dossier_B §一 6.3 + §二 N-10；本会话未重读台账（IO 纪律），现值待施工班复跑 |
| M6 | 骨架「实测今日 7 条」 | 2.2：今日（09-26）KILLED 33/DRY-RUN 31/FAILED 7；「7 条」对应 FAILED 面 | dossier_B §一 2.2（骨架行数字的出处对齐） |

## 3. 缺口与根因（转述）

- 根因（史）：孵化腿与对照腿（kill_ghost_windows）判据不同源——对照有 recheck+classify，孵化腿没有（dossier_B §一 2.1 括注）；已由 M1 闭合。
- 残余一：白名单免死匹配面=台账 cmd 任意位置子串（6.2：`sub in cmdline` 朴素子串、大小写敏感、不切分 argv）——活体身份复核只防「杀错」，不防「该豁免的被杀/该杀的被豁免」。
- 残余二：豁免不收口 → 台账单调膨胀（M5），复核逻辑每次要背 1300+ 死记录扫描。

## 4. 施工项（带锚）

1. 复验 M1 落地质量：确认 `_PID_REUSE_TOLERANCE_S` 常量位与容差值、单测覆盖（若 tests 侧无专项用例，补「create_time 不符→skip」红证用例；候选宿主=tests/dr/ 既有件，禁新建无 token 件）。
2. 白名单腿改喂活体 cmdline 或双源匹配（dossier_B §一 6.2 的调用面两处：L1086 主腿+L1011 孵化腿）——净零：改匹配源=收紧 P-23 免死判据的相邻面，与骨架 W-47（🌑 P-23 收紧）**同域不同对象，不并**（内收判据铁律 w5_1）。
3. 豁免分支补收口标记（N-10），台账加轮转/清扫口径（与 W-46 keep 名单卫生联动，骨架 L98）。

## 5. 复验命令（可重跑）

```bash
cd /d/ZephyrAlpha/.worktrees/st-zcloseout-leaves
git show HEAD:src/zephyr/trading/process_reaper.py | grep -n "身份复核\|child_create_time\|_PID_REUSE_TOLERANCE_S\|pid_reuse_skip"
# 期望：命中复核块（本会话读数：L1015 起注释「PID 复用身份复核（wave7.3 缺陷②…）」+ skip 分支）。
# 若零命中=复验腿被回退，本叶簿 M1 失效、W-41 退回 ⬜，须按 dossier_B §一 2.1 处方重施工。
```

## 6. 自审闸三态

- **挖干**：已干——史基线六向（dossier_B 2.1-2.5/6.2/6.3/G-7）+ 本会话 HEAD 复验腿直读（M1/M4）两面闭合，无未读矿脉。
- **施工中**：复验腿本体=已落地待复验（🔨→✅ 态，M1）；其质量闸（容差值/单测）未见锚，标待验。
- **未开工**：§4-2 白名单活体化、§4-3 台账收口——证据=M4 复读台账 cmd 口径未变 + N-10 机制在册。
