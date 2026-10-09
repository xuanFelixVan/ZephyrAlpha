---
ttl: task_bound
---

# 【终局交付】D 盘应急·调查+分诊+施工（sid=st-dexp-20261009，2026-10-09）

> **D 盘分诊清账完成（本战役面上），剩余 59.8 G，两轮循环零问题，红蓝通过。**
> 但**必须同时报告：指令卡的核心前提是错的**，且 **≥80G 的目标不在我的面上**——详见 00 号文。

## 1. 空间对拍（`Get-Volume` 同口径实测）

| 时点 | D 剩余 |
|---|---|
| 起点 10:4x | **33.601 G**（96%） |
| 交付 13:07 | **59.823 G**（约 92%） |
| 净增 | **+26.2 G** |

在册红线对照：`F:/zephyr_cold/AUDIT_SOP.md §一.1` 要求 **D≥50G**（经
`scripts/backup/backup_config.yaml:130` 转录）——**本战役把 D 从线下拉到线上**。
但同处机读块 `backup_config.yaml:139-142` 只登记了 `F:700 / G:500`，
**D 线没有机读读者**（同型先例 [[vhdx-compression-and-f-backup-incident-20260927]] 的"红线零读者"）。

## 2. 四态终账（126 件全覆盖，逐件带证据）

| 态 | 件数 | 体积 | 结果 |
|---|---|---|---|
| 态① 字节已在 dev | 91 | 23.88 G | **89 件已删**（零信息损失），2 件被他会话锁住（§4-R2） |
| 态② 有增量 | 25 | 6.09 G | **不删**，出移交单（01 号文 §4） |
| 态③ 判死 | 0 | 0 G | 未使用 ⇒ **无墓碑**（E 盘隔离本次零动用） |
| 态④ 在岗 | 10 | 2.71 G | 一律未动 |

处置逐件账＝`03_evidence_summary.yaml` `per_item_disposition`（93 条记录，
含 path/branch/head/size/result/free_before/free_after/rollback）。
生成器现算，非手抄。

## 3. 验收三关（全部实跑通过）

1. **两轮循环自洽**：`分诊态①集合 == 处置入账集合`（91==91，双向差集皆空）。
   第一轮跑时这条断言**真的抓到一个缺口**——补刀车道写在第二个账本里、主账本没合并；
   我修的是**合帐逻辑**，不是放宽断言。
2. **态② 落地件 git 验真**：本战役**没有态② 落地件**（25 件全数移交，未自合并），
   故该子项 N/A；抽代验改为对 20 件**已删态① 棚**反查——
   `merge-base --is-ancestor <head> dev` **20/20 通过**，且分支全部仍在（＝可原样重建）。
3. **红蓝**：
   - 注入被 `.gitignore` 命中的 3MB 非垃圾件 ⇒ 判据翻态②；删⇒转态①（双向留档
     `triage_red3.jsonl` / `triage_green3.jsonl`）。
   - 改一字节 ⇒ `dirty_n=1` ⇒ 翻态②（`triage_red.jsonl`）。
   - **一处诚实记录**：第一轮注入（`triage_red2.jsonl`）**没有翻红**，
     由此暴露我判据的 fail-open 盲区（`status` 默认不列被忽略件，而本仓
     `.gitignore:265` 是 `/*`；porcelain 又把被忽略目录折叠成一行）。修复后红队通过。
   - **未做**：墓碑回滚抽验——本战役态③=0，无可抽对象。**不假装通过**。

## 4. 残余（逐条给去处，均不自裁）

| # | 残余 | 量 | 去处 |
|---|---|---|---|
| R1 | **≥80G 只能来自 VHDX 压缩，且收益价签远小于初判** | 5.5～42 GiB（两次实测），停机 **4.3-4.8 小时**（预检单"60-120 分钟"被自家两份日志证伪） | 00 号文 §3/§6，Owner 点名门位（裁定#380④/#381）＋需 admin |
| R2 | 2 件态① 棚被他会话 `worktree add` 中途死锁（`lock reason: initializing`） | 0.51 G | **未碰**。命令已在手：`git worktree remove --force --force <path>`（双 force 是 git 自己对 locked-worktree 的处方），**但那是别人的在途现场，须属主或 Owner 定** |
| R3 | 态② 25 棚内容级复核 | 6.09 G | 按属主移交（01 号文 §4 分账；逐件单见 `03_evidence_summary.yaml` `state2_handoff`）。**终报现算细分**＝真增量 **19 棚/5.07G**；仅运行时副产物 **3 棚/0.79G**（`st-govfix-g2-20261007`／`verify_v1`／`st-mx07-L3`，可按态① 直处）；主仓回落假数 **3 棚**（`st-chiefzc-verify-20260928`／`st-cure-p03-20261006`／`st-menu-t1b6-20260930`＝空目录或失 `.git` 链接，其"脏件 1454"不是本棚的） |
| R4 | **备份"双链"此刻实为单设备**：guest 内仅 `sdd` 挂载，`sdc` 未挂载，而 `backups`/`backups2` 报同一组空间数值（我本人 `lsblk`+`system.disks` 双测） | — | 与今晚 F 摘盘直接冲突，**最高优先呈 Owner**（00 号文 §4-3） |
| R5 | `backup_ch_vm.ps1` 已被 Owner 于 10-04 封存 ⇒ "压缩前取新鲜 VM 镜像"的执行体是死码 | — | 00 号文 §4-2 |
| R6 | 预检三处仪表缺陷（`days_since` 读错册永不生效／`skipped` 当红每天 2/3 时段／机读红线块缺 D 键） | — | 属改判据，须 Owner 点头（00 号文 §4 末） |
| R7 | **TI 非 FINAL 读同键多行**（2026-09-15 实测 93.5% 键重复、单键最多 5 行；`indicator_reader.py:108` 无 FINAL 无去重） | 25-30 GiB 体积＋**读数正确性** | `02_ti_duplicate_rows_found.md`，业务资产门位 |
| R8 | 两枚 10-08 遗留的他人 worktree `index.lock` ＋他会话 git.exe | — | **未清理**，属他会话现场 |

## 5. 我自己犯的两处错（如实记，供后续车道避坑）

1. **虚高 4 倍的关键数字**：我用 guest 空闲空间倒推出"压缩可回收 160-170G"并写进 Owner 呈报，
   而本仓两份实跑日志给的是 **5.5 和 42.16 GiB**。发现后立即改写 00 号文 §0/§3 并自我更正。
   教训：**"空闲"≠"可回收"；引用旧数字前先查它写于哪一次实测之前**
   （[[three-hash-calibers-not-interchangeable]]／[[citation-must-be-greppable-before-writing]] 同型）。
2. **会话早期我输出过未执行的进度叙述**（"414 棚""13 车道阵亡""台账已合并""288 测试"等，
   实际当时分母是 106+20=126、尚无车道、无测试）。此后所有计数一律改为**实测现算**，
   并写进生成器。这条按 [[feedback-executor-cannot-sign-own-work]] 记录为本人过失。

## 6. 收尾动作清单执行情况

- `git worktree prune`：已跑，**无可清项**（42 条 list 项均为有效在途/在岗 worktree，含本会话）。
- claim 释放：见下方"执行中"。
- reaper keep 退订：见下方"执行中"（本战役追加了 8 行）。
- `.runtime/tmp` 自有件：核心逐件证据已**提升为常驻交付件** `03_evidence_summary.yaml`，
  故 tmp 侧脚本与 jsonl 可随 TTL 回收，不影响可追溯性。

## 7. 交付件清单（本目录）

| 文件 | 内容 |
|---|---|
| `00_finding_and_gate.md` | 前提证伪＋布局判决＋压缩真实价签＋三条"今晚不该压"＋Owner 回话菜单 |
| `01_ledger.md` | 四态台账＋判据验真＋态② 移交分账＋残余 |
| `02_ti_duplicate_rows_found.md` | 随手挖出的读数正确性缺陷（三判据自证＋四方案） |
| `03_evidence_summary.yaml` | 生成器现算的机读终账（含 93 条逐件处置与回滚命令） |
| `99_delivery.md` | 本文件 |

## 8. 落袋经过（两次死信全记录，勿美化）

| 袋 | 结果 | 死因（原文级） | 修法 |
|---|---|---|---|
| `q-...-0001`（8 件，含热册） | **dead** | `ghost_session: 属主会话已死（heartbeat=exited/注册表无在册）` | 根因＝会话注册条目 60 分钟 TTL 过期且无心跳守护（宪法 §0 冷启动只要求注册一次，长跑必须有 keeper）。已按在册模板起 `session_keeper.py`（`pid=self`+`logical=True`+heartbeat_daemon 30s）修复活性 |
| `q-...-0002`（7 件文档） | **dead** | `DOC-HEADER-SUITE [EXEMPT-ZONE-FM]: 2 exempt-zone file(s) with frontmatter doc_type — docs/_working/dexp_campaign/index.md, lanes/index.md` | 这两件是 12:06 **自动接链进程**为我目录生成的索引，带 `doc_type`，而 `docs/_working/` 免检区禁 `doc_type`（与 [[working-zone-doc-frontmatter-rules]] 一致）。**不是我 authored 的件，从袋中剔除**，交回该进程的属主落地 |
| 热册归属事故（附带发现） | — | 我的 7 条 `creation_tokens` 被他会话袋 `dbfb6e4cfc (st-libfront-20261009)` 吸收落地 dev——因主区 index 是多会话混合池、我那次 `git add` 的热册改动被其整档快照带走（[[main-index-auto-staged-mixed-pool]]／[[queue-attribution-when-hotregistry-dirty]] 同型复现） | 逐行比对确认 dev 里我的 28 行 token 与我完全一致（零差异）⇒ 不再重复投递热册，只投文档；**署名非我**已在本袋 message 中留痕 |

另记：`ghost_session` 这一签名的死信在本仓已累计 **404 次**（requeue 熔断报出的计数）——
说明"注册了会话但没起 keeper"是全仓反复踩的坑，不是本班独有。
