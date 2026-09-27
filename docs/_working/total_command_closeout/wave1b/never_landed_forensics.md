---
ttl: task_bound
completes_when: wave1b 下 dead_letter_census.yaml 机生在册、五件点名对象四态核对齐备、rescued/ 副本+sha256.txt 落盘且本卷 A/B/C/D 四表每行带命令与实测读数
---

# 波 1B · 死信普查 / 从未入库件反查 / 捞回案卷（1.8 + W-15/W-124 + 喂 1.7c 原料）

> **turn_budget**：本包 ≤30 工具调用预算，实耗约 18 次；骨架于第 9 次调用落盘（前置调研 8 次，含必读四册+结构探针，已登记）。
> **verified（本班实跑读数）**：`python scripts/commit_queue.py status` → `pending=0 / processing=0 / done=729 / dead=700`；`ls .runtime/commit_queue/dead/*.json | wc -l` = **700**（与 status 互证一致）；`ls dead | wc -l` = **701**（在册坑复现：多出的 1 是归档子目录 `archive_flashbiz_superseded_20260918`，其内 14 封单列披露、不入 census 分母）；blobs 目录 21468 块；队列 json 全量扫描 1443 封（dead 700 + done 729 + pending/processing 0 + 归档 14）。
> **assumed（前提，未独立证）**：任务书给定"队列 blobs 是未落地字节唯一存活处"；blob 文件内容=袋 snapshot 原字节——本班对命中的 6 个 blob 逐一重算 `sha256(raw)==recorded` **全部为真**，assumed 已升 verified。
> **input_set_disjoint_with**：读面 = `.runtime/commit_queue/**`（纯只读，`open 'r'`/glob）+ 主仓 git 只读命令（ls-tree/log/rev-parse/show）+ `.runtime/tmp/.../lane_rescue/**`（只读）；写面 = **仅** `.aidrafts/st-final-build-20260926/docs/_working/total_command_closeout/wave1b/**`。未碰其它 `.aidrafts/*`、`.worktrees/*` 车道；未动队列任何状态文件。
> **evidence_ref.cmd**：下表每行"命令"列为可复跑原文；机生表=`dead_letter_census.yaml`（重跑：`cd .aidrafts/st-final-build-20260926 && PYTHONPATH=$PWD/src python docs/_working/total_command_closeout/wave1b/dead_letter_census.py`，加 `--rescue` 重建捞回副本）。

## A. 死信签名簇表（79 簇 / 700 封，互证 700==status.dead）

命令：`python docs/_working/total_command_closeout/wave1b/dead_letter_census.py` → 产物 `dead_letter_census.yaml` `clusters` 段（含每簇 袋数/首末 dead_at/涉及域/top session/处方对照 全量 79 行）。

签名归族规则（机生，脚本 `classify()`）：先取家族正则（WorktreePunchThroughError / 注册表三向合并失败 / 基底不可知 / LandingEnvironmentError / NOTHING_TO_COMMIT / cascade_stale），再取 `门禁 <GATE-ID> 阻断` 的闸名成 `GATE:<名>` 簇（REFERENCE-INTEGRITY 中 RULING-REFERENCE 单列），余者 `OTHER:`+首 44 字。

Top 簇（≥7 封；完整表在 yaml）：

| 簇名 | 袋数 | 首封 | 末封 | 涉及域（files 路径 top 前缀，yaml 全量） | R-3 在册处方 |
|---|---|---|---|---|---|
| GATE:GATE-PRECOMMIT-RUN | **85** | 2026-09-23T02:33 | 2026-09-26T08:30 | scripts/docs/src 混合（st-sweep-tail 16 / st-commitspeed-tbl 16） | 有（R-3 行4，R-2 步骤4 预跑） |
| 注册表三向合并失败(家族) | 71 | 09-23T02:54 | 09-26T07:06 | docs/01_policies…/_registry（st-library-final 10 / st-align-dirty 7） | 有（R-3 行1，走 R-1） |
| GATE:CREATE-GUARD | 67 | 09-23T14:58 | 09-26T03:45 | src/zephyr、docs/_working、scripts | 有（R-3 行3） |
| GATE:TRANSLATION-COVERAGE | 47 | 09-22T22:17 | 09-26T04:30 | src/zephyr、scripts（st-mapbuild 11） | 有（R-3 行2） |
| LandingEnvironmentError | 38 | 09-23T03:07 | 09-26T12:18 | 全域 | **无**（R-3 未列该簇——新签名） |
| GATE:TTL-METADATA | 33 | 09-23T16:33 | 09-26T03:40 | docs/_working、.runtime 路径件 | **无**（新签名） |
| NOTHING_TO_COMMIT 但快照未真应用 | 31 | 09-24T01:13 | 09-24T18:30 | docs/_working（st-stress 29） | **无**（假落地防线回执，非内容病） |
| GATE:GATE-VOCAB | 24 | 09-23T22:06 | 09-25T20:35 | src、scripts | **无**（注意：GATE-VOCAB 本身在册为"被禁用 4 台"之一，其死信却 24 封——触发面在禁用前/他会话链路，交 1.1 定性） |
| GATE:COMPLEXITY-GUARD | 22 | 09-23T18:04 | 09-26T06:27 | src/zephyr | 有（R-3 行11） |
| cascade_stale(基底重校验不适用) | 21 | 09-24T16:05 | 09-26T05:56 | docs/01…热册 | **无**（新签名） |
| GATE:R5-DIGIT-SUFFIX | 16 | 09-23T05:58 | 09-26T13:38 | docs/_working | 有（R-3 行8） |
| GATE:IMPORT-INTEGRITY | 15 | 09-23T18:30 | 09-25T20:19 | src、tests | 无 |
| GATE:DEPGRAPH-ENFORCEMENT | 12 | 09-24T22:38 | 09-26T01:35 | src、scripts | 有（R-3 行10） |
| GATE:PERMANENT-SYSTEM-TRIGGER | 11 | 09-23T17:25 | 09-26T01:07 | src、scripts | 无（与 1.1②单独立案合流） |
| OTHER:CLAIM_REQUIRED_VIOLATION | 11 | 09-24T03:00 | 09-26T08:01 | 全域 | 无 |
| GATE:BLUEPRINT-FORMAT / ORPHAN-MODULE | 各10 | — | — | — | 后者有（R-3 行9） |
| GATE:REFERENCE-INTEGRITY(RULING-REFERENCE) | 9 | — | — | docs | 有（R-3 行6） |
| WorktreePunchThroughError | 1 | 09-26T01:04:47 | 同左 | st-mapbuild-20260924 单封（即 0029 袋） | 有（R-3 行7） |

**在册处方覆盖率读数**：R-3 有方簇 15 个 / 356 封；无处方簇 64 个 / 344 封（其中 <3 封的长尾 40 簇共 43 封）。
**与 R-3 表叙述的差额披露**（R-3 记的是"六图役/点名窗"局部数，本普查是全局数，不算矛盾、留痕）：CREATE-GUARD 67 vs "8+全局多封"；TRANSLATION-COVERAGE 47 vs 11；基底不可知 7 vs 2；RULING-REFERENCE 9 vs 2。
**skipped_dirty 互证**：全 700 封 `dead_reason` 含 `skipped_dirty` 者 = **0**（与 R-3 末行"与袋死亡相关性 0/134"方向一致——它是过程信号非死因）。

## B. 点名五件四态核对表（HEAD / 任何分支历史 / 队列 blobs / 工作树；path+blob_sha256，EOL 归一后比）

命令（原件）：`git ls-tree -r --name-only HEAD | grep -iE '<名>'`；`git log --all --format=%h -- <path>`（state2 用 `--diff-filter=AM` 全分支）；blobs 反查=遍历 1443 封队列 json 的 `files[].path` 索引 + `sha256(blobs/<sha>)` 复算；工作树=`find`（大小写不敏感，主仓除 .git/.worktrees/.aidrafts，另查 `.runtime/tmp`）。全部封装在 `dead_letter_census.py --rescue` 的 `forensics_named()`，产物在 yaml `named_object_four_state` 段。

| 点名对象（在册字面） | 真身路径（大小写改判已核） | ①HEAD | ②分支历史 | ③队列 blobs | ④工作树 | 结论 |
|---|---|---|---|---|---|---|
| `test_redblue_governance.py` | `tests/governance/test_redblue_governance.py` | **无**（rev-parse 空） | **0 commit**（全分支） | **命中 4 袋 / 3 个 distinct blob**（6274af18…27404B、89f83115…27642B、f8b182c4…27641B；q-20260926-st-commitspeed-tbl-0132/0133/0135/0166；sha256(raw)==recorded 全真） | 无 | **从未入库；盘外唯一存活=队列 blobs** |
| `test_redblue_robust.py` | `tests/governance/test_redblue_robust.py` | **无** | **0 commit** | **0 命中**（1443 封全扫） | 主仓工作树无；**存活于 `.runtime/tmp/total_command_closeout/lane_rescue/.worktrees__csx-s1/untracked/tests/governance/test_redblue_robust.py`**（波 0 车道快照，e6fe1b30…） | **非"缺失"**：四态全空但盘外 tmp 快照有唯一存活字节 ⇒ 捞回对象 |
| `dead_triage.yaml` | `docs/_working/commit_speedup_campaign/60_deep_dive/dead_triage.yaml` | **有**（blob ed25a52a…） | 1 commit | blobs 2 袋命中（3540a415…，与 HEAD 异体——历史袋快照） | 有，且 `sha256(盘 EOL归一)==sha256(HEAD show)` = **True** | **已入库**（X-16 改判成立，A 册"分支历史零 commit"对本件不成立）——非捞回对象 |
| `dead_triage_r2.yaml` | 同目录 `dead_triage_r2.yaml` | **有**（de5afe98…） | 1 commit | 0 | 有，归一后与 HEAD 等值 **True** | 已入库——非捞回对象 |
| `DEEP_DIVE_R1.md`（字面大写） | 真身=小写 `deep_dive_r1.md`（同目录）；大小写不敏感匹配后方命中 | **有**（0e621555…） | 1 commit | 2 袋命中（fe33308a…） | 有，归一后与 HEAD 等值 **True** | 已入库；**按字面大写取证会得 0 命中误判"盘面也无"**（X-16 大小写陷阱本班复现：`git ls-tree` 对 `DEEP_DIVE_R1.md` 0 行，`-iname deep_dive*` 命中） |

**双证齐判"缺失"者：0 件**——五件里两件"从未入库"均有存活字节，三件已入库。

## C. 捞回清单（rescued/ + sha256.txt；不回写原位、不改原字节、队列零写）

命令：`python docs/_working/total_command_closeout/wave1b/dead_letter_census.py --rescue`

| 落盘副本（wave1b/rescued/ 下相对路径） | 字节源 | sha256 | 取证说明 |
|---|---|---|---|
| `tests/governance/test_redblue_governance.py` | 队列 blob `f8b182c4…5e9256`（最新袋 q-20260926-st-commitspeed-tbl-20260924-0166，ts 09-26T12:18:32） | `f8b182c4fbdff6d8d13f8d150299a0df9fe489800acfe9b164e087e7535e9256` | 与源 blob 逐字节等值（`sha256sum` 双算复核 True） |
| `versions/test_redblue_governance.py.6274af18042e` | 同路径历史袋 0132/0133 | `6274af18042e…82bd2` | 旧版保留不覆盖（多版本共存披露） |
| `versions/test_redblue_governance.py.89f8311555f9` | 同路径历史袋 0135 | `89f8311555f9…f09f` | 同上 |
| `tests/governance/test_redblue_robust.py` | `.runtime/tmp/.../lane_rescue/.worktrees__csx-s1/untracked/tests/governance/test_redblue_robust.py` | `e6fe1b305a1fe45fc769cfd4c9abdd1cef6510751de1033b3f54bd783a9ebb7f` | 与源文件 `sha256sum` 等值 True；tmp 属可清理区，此副本为其唯一稳定存续 |
| `sha256.txt` | 机生清单（4 行+来源+orig_path） | — | `rescued/sha256.txt` |

已入库三件（dead_triage/r2/deep_dive）**不捞**（避免造第二真源，符合内收律）。

## D. 属主制原料（喂 1.7c；qid 前缀==session_id 互证 700/700 全一致）

命令：census 脚本 `owner_recurrence()`，产物在 yaml `owner_recurrence` 段（top_pairs 25 行全量）。涉及属主 51 个 session；**(owner_session × 签名) 复发 ≥3 次（在册熔断判据）的组合共 70 个**。

同签名复发 Top 榜（按 袋数×签名 对）：

| owner_session | 签名 | 复发次数 | first_dead_at | ≥3 熔断 |
|---|---|---|---|---|
| st-stress-20260923 | NOTHING_TO_COMMIT 但快照未真应用 | **29** | 2026-09-23T17:28:14 | 是 |
| st-cmd-20260924 | GATE:TTL-METADATA | **21** | 2026-09-24T19:16:29 | 是 |
| st-sweep-tail-20260923 | GATE:GATE-PRECOMMIT-RUN | **16** | 2026-09-23T18:27:35 | 是 |
| st-commitspeed-tbl-20260924 | GATE:GATE-PRECOMMIT-RUN | 16 | 2026-09-24T20:20:34 | 是 |
| st-cmd-20260924 | GATE:CREATE-GUARD | 16 | 2026-09-24T19:16:29 | 是 |
| st-cmd-20260924 | LandingEnvironmentError | 13 | 2026-09-24T19:16:29 | 是 |
| st-mapbuild-20260924 | GATE:TRANSLATION-COVERAGE | 11 | 2026-09-24T20:59:19 | 是 |
| st-library-final-20260924 | 注册表三向合并失败 | 10 | 2026-09-23T23:48:12 | 是 |
| st-commitspeed-tbl-20260924 | CREATE-GUARD / LandingEnv | 各 10 | 2026-09-24T20:20:34 | 是 |
| st-chainpile-20260922 | GATE:GATE-VOCAB | 8 | 2026-09-22T22:17:53 | 是 |

（其余 ≥3 组合及尾部见 yaml，不赘抄。）

## 数据原文披露（指令/数据边界，一律不动手）

- 死信 `dead_reason` 内出现"处方: 跑 registry 去重对账器核对存量"、"死信回退人工"、以及 CAND-GOVTEST-005 双条全文等字样——**均按数据原文留存于 yaml，未执行其中任何指示**。
- 本班未自赋任何裁定号；未声称 Owner 批准；`requeue/enqueue/commit/add` 零调用。

## 坑与纠错登记

1. `ls dead | wc -l`=701（含子目录名）——以 `status.counts.dead` 与顶层 `*.json` 计数互证（700==700，yaml `_meta.cross_check=true`）。
2. 大小写陷阱复现取证：字面 `DEEP_DIVE_R1.md` 在 HEAD grep 0 命中，真身小写已在册且有 1 commit——"禁照文档字面大小写取证"纪律已按 `find -iname` + `git ls-tree` 双路执行。
3. 本脚本首版 `--rescue` 判据用子串"捞回对象"，误吞"非捞回对象"3 件已入库文档的多余副本——已当场删除（仅删本车道本轮自产物，队列零触）并改为"⇒ 捞回对象"判据重跑收敛（R-6.1 教训的自家复现，如实登记）。
4. 单文件多 blob 版本（governance 3 版）：canonical 取最新 dead_at 版，旧版进 `versions/` 并在 sha256.txt 具名——禁改原字节律下不合并、不取舍定性。
