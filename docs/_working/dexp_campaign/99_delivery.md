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
| `04_ti_dup_quantified.md` | 发现三定量：三把尺／消费者清单／影响面评估＋第三条路（二轮新增） |
| `05_worktree_handoff_zongdui.md` | 两枚 initializing 死锁棚移交总队（二轮新增） |
| `scripts/data_ops/audit_ti_row_versions.py` | TI 行版本重复尺本体（常驻只读，fail-loud） |
| `data/audit-trail/vhdx_growth_series.jsonl` | vhdx 体积／D 剩余日序列（新增） |

## 8. 二次收工（总统筹裁定后复工，2026-10-09 午后）

Owner 裁定按 3/4 复工。执行结果：

### 8.1 发现三·TI 定量（三件产出齐）

- 尺本体＝`scripts/data_ops/audit_ti_row_versions.py`（只读、fail-loud、三把尺同出、日序列）。
  **双向自证过**：`--periods daily` 2026-09-15 退出码 **2（红）**，`--periods 15min,120min` 同日 **0（绿）**；
  空返回一律当故障而非"无数据"。
- 三件产出见 **`04_ti_dup_quantified.md`**。核心更正两条：
  1. **我上一版的机制描述错了**——不是"reader 无 FINAL"，而是
     `ch_reader.inject_final()` **有条件**注入，条件探针 `get_table_engine()`
     失败时返回 `""` 且**无条件写入进程级缓存**（`ch_writer.py:805`）
     ⇒ 一次探针失败＝该进程此后永久静默失去 FINAL。已实测两条方向证实。
  2. **缺陷有两种，只有 B 型威胁正确性**：分钟级是**等值重复**（会随合并自愈），
     `daily` 是**异值重复**——2026 全年 **383,272 个键（38.4%）同键存着不同指标值，最多 6 版**，
     且**贯穿 202601-202609 每一个采样日**，不是 9 月局部事故。
- **正面发现**：表里已有 `ingest_ts` 列且实测**能 100% 裁决**异值重复
  ⇒ 存在"A/B 之外的第三条路"（读侧按最新入库去重，成本远小于重建 220 GiB 表）。
  另测得 `FINAL` 与"最新入库"当日**零分歧**，但这个一致**无机制保证**，随合并次序漂移。
- **我明确没做**：任何 INSERT/DELETE/DROP/ALTER/OPTIMIZE、任何 TTL/表结构、任何对 reader 的擅改。

### 8.2 仪表四处修对

| # | 修的内容 | 证据 |
|---|---|---|
| 1 | `days_since_last_compaction` 原读 `rolling_archive_state.json`（无该键）⇒ 恒 null、`due` 恒真、90 天触发从未生效。改读真源 `backup_state.json` 且要求 `result=ok` | 今日实测出**真值 9.4 天**（原为 null） |
| 2 | 预检不再用"整轮旗/节律 skip"当 CH 链判据；新增 `ch_chain_fresh()` 锚在 CH 服务端 `system.backups`，**采集失败一律判红（fail-closed）**；预检单改列**全部**红项（原实现只回填第一个红串，把 CH 项一起藏掉） | 新探针报 **新鲜 1.2h**，而旧判据同刻仍报 `failed` ⇒ 证明确是仪表假红 |
| 3 | `capacity_guard.min_free_gb` 补 `D: 50 / E: 50`（注释 §一.1 声明的红线原本只有 F/G 两键＝**D 线零读者**），并给它真读者 `d_drive_red_line_gb()` 写进日序列 | D 现 59.75G ＞ 50 ⇒ `d_below_red_line=false` |
| 4 | 新增 **vhdx 日增速哨兵** `record_vhdx_growth()`：逐日记 vhdx 体积/D 剩余/日差/红线判定。`due` 只 gate 成文、**不 gate 采集**（否则 <90 天的年份序列整段断掉） | 顺带**证伪了我自己的"3.9G/天"**：既有 10-03→10-09 序列六天几乎持平（584.7→586.5），而压缩后头两天曾 +13~16 GiB/天 ⇒ 增速**非常数**，不可用单点斜率外推 |

- **我没动的东西（重要）**：归档**安全阀#1**（`_backup_fresh`，供 :329 删分区判定）**语义原样保留**。
  理由＝"只在 CH 刚备份完才允许删分区"是刻意保守，改它会**静默提高删除频率**，
  属数据操作门位而非仪表问题。我只把被它误标的**预检显示面**修对了。
- 测试：`tests/meta/scripts/ch/test_rolling_archive_reconciler.py` 12 例全绿（6 旧+6 新）。
  **变异测试证其有牙**：把 fail-closed 故意改成 fail-open 注入源码后，
  `test_ch_chain_fresh_fail_closed_on_probe_failure` 立即 FAILED（1 failed/11 passed），
  随后按 sha256 逐字节还原（`RESTORED_OK`）。
- 预检单文案一并纠偏：页脚不再写"停机 60-120 分钟"，改为实测口径 **4.3-4.8 小时**＋
  "回收量 5.5~42 GiB、勿用 guest 空闲倒推"。

### 8.3 两件卡死 worktree

按裁定 #6 移交总队，见 **`05_worktree_handoff_zongdui.md`**（含 git 官方处方命令、
我为什么不自己按下去的三条理由、佐证材料位置）。**本战役未对它们做任何写操作。**

### 8.4 二次收工过程中撞到并处置的两件事

1. **新脚本一开始放进了 `scripts/data/`，而 `.gitignore:610` 是 `scripts/data/*`**
   （该目录默认忽略、逐个靠 `!` 豁免入库）。表现为"文件存在但 `git status` 毫无输出"。
   ⇒ 按在册先例（同族只读探针住 `scripts/data_ops/`）迁到该目录，未硬闯 `.gitignore`。
2. **热册归属吸收第二次复现＋工具的路径锚定坑**：
   `add_module_translation.py` 在**车道内**调用时，实际写的是**主区**那本册
   （车道文件 mtime 仍是 checkout 时刻 11:14，工具却自报"更新 … 8093 条"）。
   同时主区两本热册已含**他会话 staged 条目**（`st-chiefc` 的 3 条 token、`ruling_precedent` 的翻译条）。
   ⇒ 处置＝**不搬主区整档**，只把"属于我的那一条"原样重放进车道副本，
   并做**条目级**键集合差自证：translation `8091→8092`、唯一增量=我那条、零丢失、零改动他人条目；
   token 册 +5 行/0 删；`git diff` 里 `chiefc|ruling_precedent` 泄漏计数=0。
   （行集合差量不出 8 行增量，因为 `desc_en: ""` 等 3 行与册内既有行字面重复——
   这也是为什么热册必须按**条目**而不是按**行**对账，见 [[hot-registry-superset-delta-recipe]]。）
3. **我自己造成的一次生产数据污染并清除**：手测 `record_vhdx_growth()` 时未走 tmp_path，
   把两行假值写进了生产序列 `data/audit-trail/vhdx_growth_series.jsonl`
   （后果＝第三行的 `delta_vs_prev_gb` 算成 -3.5 假信号）。已 CAS 重写为"仅首条真观测"，
   并在文件内留 note 说明清污；重跑后日差归真（0.0）。教训＝**单元测试用 tmp_path，
   手测同样必须 tmp_path**，否则"验真"这一步本身就在造脏数据。

### 8.6 【紧急上报】二轮收工时撞到的热册三件事

1. **【自我更正】我上一版在这里写"主区该册比 HEAD 少 56 条、净删 294 行，谁提交就删 56 条"——
   该结论已作废。** 按总统筹令做三向对账（HEAD / index / 盘面 / 在途袋）后实测：

   | 面 | token 条目数 | 相对 HEAD |
   |---|---|---|
   | HEAD | 14,201 | — |
   | git index | 14,203 | **缺 0，多 2** |
   | 盘面工作副本 | 14,203 | **缺 0，多 2** |

   盘上多出的 2 条**全部可归属到在活会话**：`st-chiefc-20261009-rb1`(1)、
   `st-tdm-examcard-20261009`(1)；且有 **2 个 `st-chiefc` 在途袋正引用该册**。
   ⇒ **没有任何条目丢失，我不做任何复原**（"无法归属残留行只报不动"这一类＝空集）。

   我的错因（记下来供后续班避坑）：我在 16:31 与 17:4x 各拍过一次**单张快照**，
   正撞在别的会话对该册做整档写的中途，于是把"写一半"读成了"被抹 56 条"。
   **热册判缺必须做键集合差对账，不能凭单次阅读；更要避开发写窗口**——
   这正是总统筹要求 triage-first 的理由：当时若照我建议的
   `git checkout HEAD -- <该册>` 盲复原，会**当场删掉那 2 条活会话在途 token**。
   （我上一版建议了这条命令，一并更正。）
2. **`batch_creation_tokens.py` 自报成功而盘上无物**：16:31 那次报
   `落盘: True (CAS attempt 1)`，但随后 `grep -c 04_ti_dup_quantified` 在主区册里＝**0**。
   ⇒ 回执不可信，**必须外部复算**（本仓"假回执"第 N 次复现，见
   [[landing-pipeline-death-modes-20260927]] 第 11 式）。
3. **`add_module_translation.py` 与 `batch_creation_tokens.py` 在车道内调用仍写主区**：
   车道内跑，工具自报"更新 8093 条"，但**车道那本册 mtime 停在 checkout 时刻 11:14、内容零差**，
   主区册反而多了我的条目 ⇒ **这两个工具的项目根解析锚在主仓，不认 worktree**。
   与 [[worktree-local-queue-trap]] 同族（路径按脚本自身/主仓解析而非 cwd）。
   ⇒ 车道内登记不可用；我改为"以新 dev 为基、把只属我的条目重放进车道副本"，
   并做**条目级**键集合差自证（token 13,925→13,927 / translation 8,091→8,092，**丢失=0、改动他人=0**）。

另：我的 7 条 `dexp_disk_triage` token 与 1 条 `ti_row_version_audit` token，
**两次都是被他会话的袋吸进入库的**（署名非我）。同一根因＝主区 index 是多会话混合池。
这已是本班第二次实测复现，值得单独立题（不是我的袋能解决的）。

### 8.7 二轮交付物清单

| 件 | 类型 |
|---|---|
| `scripts/data_ops/audit_ti_row_versions.py` | 新增（尺本体，fail-loud） |
| `scripts/ch/rolling_archive_reconciler.py` | 改（仪表四处） |
| `scripts/backup/backup_config.yaml` | 改（D/E 红线机读键） |
| `tests/meta/scripts/ch/test_rolling_archive_reconciler.py` | 改（+6 例，含变异测试自证） |
| `docs/_working/dexp_campaign/04/05/99` | 新增/改 |
| `docs/_working/disk_reorg_campaign/vhdx_precheck_20261009.md` | 生成器重出（纠旧文案） |
| `data/audit-trail/vhdx_growth_series.jsonl` | 新增日序列 |
| 两本热册（token/translation） | 只增我 3 条，条目级自证 |

### 8.9 【三轮】P0 与「第三条路」实施结果（总统筹 1/2 批复）

**第三条路（读侧去重）已实现并实测**：`indicator_reader.py` 由"直读＋依赖 FINAL"
改为 `GROUP BY symbol, period, trade_time` ＋ `argMax(col, ingest_ts)`。

- 实测效果（000001 × daily × 2026-09，1 只票 21 个交易日）：**旧读法 63 行 → 新读法 21 行**（膨胀 3.0×）。
- 关键性质：**FINAL 注不注入，结果都确定性等于"最新入库版"** ⇒ 读取侧不再依赖那把会失败的探针。
- 踩到并记下的一条 CH 语义：投影写 `argMax(trade_date, ingest_ts) AS trade_date`
  会被 WHERE 里的同名列解析成聚合 ⇒ `Code 184 ILLEGAL_AGGREGATION`；本通道 TSV 无表头按序映射，
  别名本属多余，已去除并加防回归测试。

**P0（探针缓存污染）已修，且比初报更严重**：严格通道 `_final_suffix_strict()`
读的**是同一本被污染的缓存**，而缓存里的 `""` 是合法值不是异常 ⇒
一次非严格探测失败会**把严格契约一起变成静默不注入**（`:213` 自己警告的"FINAL 缺失⇒计数虚高"由此兑现）。

修法：① 失败**不写**权威缓存（下次自动重试＝自愈）；② 新增 `get_table_engine_strict()`，
"未知"必抛，绝不把未知当"确证非 Replacing"；③ 非严格 `inject_final` 不注入时必发
`GATE-P0-ENGINE-PROBE` 告警并计入 `engine_probe_failures`。

**红证（Owner 要求"注入必须仍生效或显式红"）**：新增 5＋3 例契约测试；
**变异测试**＝把"失败也写缓存"注回源码，2 条用例立即红（`RESTORED_OK` 按 sha 还原）。

**顺带抓出两条在册假绿/假事实**：
① `test_ch_archiver` 拿 `tick_data` 当"非 Replacing"例子——实测 `system.tables` 里
`tick_data = ReplacingMergeTree`，它长期绿只是因为 stub 了不在路径上的旧接缝；
已改用真 `MergeTree` 表并把 stub 迁到实际接缝。
② `ch_writer` 头部 `[TESTS] tests/zephyr/data/test_ch_writer.py` **该文件不存在**（在册测试指针悬空，未自改，登记待属主处理）。

**回归**：跨文件合跑 **149 passed**（首轮曾因跨文件顺序致 caplog 空捕获，已把捕获级别钉到具体 logger）。
另有 2 例"顺序相关"教训：`caplog.at_level("WARNING")` 依赖 root 级别，被先导入模块配置影响 ⇒
判据类断言应 `caplog.set_level(..., logger=具体名)`。

### 8.10 现状与待办

- 排队中：袋 `0017`（9 件：P0 三源文件＋尺＋翻译条＋3 文档＋仪表测试）、`0021`（4 件 P0 测试）。
  keeper 在岗保护（不停则不判死）；**未落地前我不自称交付**。
- 待 Owner：P0 修好后是否要把 `count()` / `query_table()`（在册"存量静默"legacy，
  docstring 已标判据禁用）也一并改成未知即抛——我**没动**它们，那是存量契约变更。
- 压缩窗按裁定继续挂起，等日增速哨兵数据（增速非常数已证，见 §8.2 #4）。

### 8.11 状态快照（数字随队列推进而陈旧，最新值见 §8.10 与终报口播）

- D 剩余 **59.986 G**（起点 33.601，+26.4G）；`data/audit-trail/vhdx_growth_series.jsonl` 起每日记录。
  ※ 本行采集于二轮收尾时；三轮当前 D=**57.3 G**（别队在持续写入，故我"删一件即涨一件"的说法
  在并发窗口内不成立，见 §5 与 [[landing-pipeline-death-modes-20260927]] 第 17 式）。
- 压缩窗按裁定**挂起，等哨兵数据**；加盘已呈 Owner。
- 待 Owner 的只剩两件：**TI 的 A/B（现含第三条路）** 与 **压缩窗点名**。

## 9. 落袋经过（死信全记录，勿美化）

| 袋 | 结果 | 死因（原文级） | 修法 |
|---|---|---|---|
| `q-...-0001`（8 件，含热册） | **dead** | `ghost_session: 属主会话已死（heartbeat=exited/注册表无在册）` | 根因＝会话注册条目 60 分钟 TTL 过期且无心跳守护（宪法 §0 冷启动只要求注册一次，长跑必须有 keeper）。已按在册模板起 `session_keeper.py`（`pid=self`+`logical=True`+heartbeat_daemon 30s）修复活性 |
| `q-...-0002`（7 件文档） | **dead** | `DOC-HEADER-SUITE [EXEMPT-ZONE-FM]: 2 exempt-zone file(s) with frontmatter doc_type — docs/_working/dexp_campaign/index.md, lanes/index.md` | 这两件是 12:06 **自动接链进程**为我目录生成的索引，带 `doc_type`，而 `docs/_working/` 免检区禁 `doc_type`（与 [[working-zone-doc-frontmatter-rules]] 一致）。**不是我 authored 的件，从袋中剔除**，交回该进程的属主落地 |
| 热册归属事故（附带发现） | — | 我的 7 条 `creation_tokens` 被他会话袋 `dbfb6e4cfc (st-libfront-20261009)` 吸收落地 dev——因主区 index 是多会话混合池、我那次 `git add` 的热册改动被其整档快照带走（[[main-index-auto-staged-mixed-pool]]／[[queue-attribution-when-hotregistry-dirty]] 同型复现） | 逐行比对确认 dev 里我的 28 行 token 与我完全一致（零差异）⇒ 不再重复投递热册，只投文档；**署名非我**已在本袋 message 中留痕 |

另记：`ghost_session` 这一签名的死信在本仓已累计 **404 次**（requeue 熔断报出的计数）——
说明"注册了会话但没起 keeper"是全仓反复踩的坑，不是本班独有。
