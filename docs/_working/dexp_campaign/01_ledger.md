---
ttl: task_bound
---

# D 盘应急·四态台账（sid=st-dexp-20261009，2026-10-09）

> 机读件同目录：`.yaml`（本仓 `docs/_working` 禁 `.json`，见 [[working-zone-no-json-suffix]]）。
> 逐件明细真源＝`.runtime/tmp/dexp/lanes/*.jsonl`（本文件只汇总，计数不手抄）。

## 1. 处置面分母（实测，非估计）

| 面 | 数量 | 体积 | 归属 |
|---|---|---|---|
| `.aidrafts` 工棚 | 106 | 27.73 G | **本战役** |
| `.worktrees` | 20 | 4.53 G | **本战役** |
| `.runtime/tmp` | 68.5 万件 | 34.37 G | 总队 H 批（未碰） |
| `.runtime/commit_queue` | — | 7.93 G | 死信专车（红线禁碰） |
| `data/` | — | 5.33 G | 生产库（红线禁碰） |
| `D:\HyperV\...\data.vhdx` | 1 | **586.5 G** | 态④ 生产库本体（见 00 号文） |

## 2. 四态计数（126 件全覆盖，逐件带证据）

| 态 | 件数 | 体积 | 判据（逐件落证据） | 处置 |
|---|---|---|---|---|
| **态①** 字节已在 dev | **91** | **23.88 G** | HEAD 是 `dev` 祖先（`merge-base --is-ancestor` rc=0）＋`status` 零脏件零未跟踪＋`--ignored=matching` 递归展开后非垃圾增量件=0＋属主心跳死 | `git worktree remove`（非 force，**保留分支**），每件记 `worktree add <path> <branch>` 回滚 |
| **态②** 有增量 | **25** | **6.09 G** | 上列任一不满足（ahead>0 / dirty / untracked / 有非垃圾增量件） | **不删**，出移交单（§4） |
| **态③** 判死 | **0** | 0 G | 未使用 | 无墓碑（本战役无需 E 盘隔离） |
| **态④** 在岗 | **10** | **2.71 G** | `SessionRegistry.get_session(sid)` 返回活体（与执法层同判据，非自造阈值） | 一律不动 |

态④ 十件全清单（证判据有判别力，非 blanket 放行）：
`st-deadcure-chief-20261009`、`st-deadcure-g1-chief`、`st-deadcure-g2-chief`、
`st-deadcure-promote-chief`、`st-deadcure-restore-chief`、`st-chiefc-20261009`、
`st-chiefc-20261009-D`、`st-libfront-20261009`、`st-fullflow2-20261008`、`st-dexp-20261009`（本会话）。

## 3. 判据本身的验真（三件，防"装饰件"）

1. **能红**：向 `.aidrafts/AI-PROBE-001` 注入一枚 3MB、被 `.gitignore` 命中的非垃圾件
   ⇒ 判据翻 `STATE2_INCREMENT`；删除后 ⇒ 回 `STATE1_CLEAN_MERGED`。双向复测通过。
2. **查出并修掉一处 fail-open**：初版只用 `git status --untracked-files=all`，
   而本仓 `.gitignore:265` 是 `/*`（顶层默认全忽略）⇒ 被忽略件根本不出现在列表里；
   且 porcelain 把被忽略**目录**折叠成 `!! output/` 一行，`is_file()` 判定会整目录漏掉。
   两处都曾让"棚内藏数 G 非 dev 内容"被判成可删。**修复＝`--ignored=matching` ＋目录递归展开。**
   该缺陷由上面第 1 条红队暴露，非推理得出。
3. **第二道闸**（防我自定义"垃圾"桶夹带真数据）：91 个态① 棚逐件反查 ≥20MB 非 tracked 件，
   8 分片并发跑完 ⇒ **0 命中**（`.runtime/tmp/dexp/state1_audit_*.json`）。

另记一处**安全方向的测量污染**（不影响删除安全）：3 个 `.worktrees` 目录实为**空目录或失
`.git` 链接的搁浅副本**，`git -C` 会向上回落到主仓，于是把主仓里他会话的 721 A / 454 M 在途件
误算进棚的脏件数 ⇒ 它们被判态②（**过保守**，不是过松）。已单列 §4。

## 4. 态② 移交分账（按属主车道，未自行处置）

| 属主线索 | 棚数 | 体积 | 备注 |
|---|---|---|---|
| `st-fc-*`（FC 线） | 3 | 0.79 G | landing/spm/tdm |
| `st-gomap-*` | 2 | 0.54 G | 含 2 件 ahead>0（有未并入提交） |
| `st-fflow-*` | 2 | 0.52 G | |
| `*-cure-*` | 3 | 0.49 G | bcure/cure-p0/cure-p03 |
| `st-bt-fast-w5-*` | 1 | 0.37 G | 310 件忽略增量＋20 脏件 |
| `st-deadcure-20261009` | 1 | 0.27 G | 死信专车在途，**未碰** |
| `st-mx07/matrix` | 1 | 0.26 G | |
| 其他 | 12 | 2.85 G | 含 3 件空目录/失链接（0.46 G，机械可清但要 owner 车道确认） |

`ahead>0` 的 4 件是唯一有"真未并入 commit"的棚（`st-gomap-b-20261006`=2、
`st-entrance-gate-20261007`=2、`st-mastertc-mine`=1 等），**tests 类增量按指令应移交总队 F-1b**；
本战役态② 总量仅 6.09 G，性价比低于 23.88 G 的态①，故**优先把态① 吃干净、态② 全数移交**。

## 5. 处置进度与空间对拍

- 起点 D 剩余 **33.601 G**（`Get-Volume` 实测）。
- 试点 1 件（`.aidrafts/AI-PROBE-001`）：`git worktree remove` rc=0，目录消失，
  但同分钟 `Get-Volume` 读数未变 ⇒ 当时误判"未回收"。后续逐件对拍显示**每件稳定 +0.29~0.31 G**。
  教训记入 [[three-hash-calibers-not-interchangeable]] 同型：**单件体积小于测量抖动时不能同分钟定性**。
- 逐件账本＝`.runtime/tmp/dexp/lanes/dispose_state1.jsonl`（含 free_before/free_after/rc/
  dir_gone/still_in_list/rollback/elapsed_s）。
- 终值与对账见 `99_delivery.md`。

## 6. 已知残余（不自裁，逐条给去处）

| # | 残余 | 去处 |
|---|---|---|
| R-1 | `git worktree list` 残留 2 条"目录已删但条目在"的记录 | 收尾 `git worktree prune`（安全：仅清 admin 元数据） |
| R-2 | 两枚 10-08 遗留的**他人** worktree `index.lock`（`st-entrance-gate-20261007`/`st-tclose-20261004`）＋ 3 个他会话 git.exe | **不清**，属他会话现场（[[predecessor-session-alive-check]]） |
| R-3 | `prune --dry-run` 报 `st-vm12ops-20261007` gitdir 指向不存在 | 随 R-1 一并 prune |
| R-4 | 态② 25 棚内容级复核 | 移交属主车道（§4） |
| R-5 | TI 重复行缺陷（非本战役） | 见 `02_ti_duplicate_rows_found.md`，业务资产门位 |
| R-6 | VHDX 压缩门位 | 见 `00_finding_and_gate.md` §6 选项表 |
