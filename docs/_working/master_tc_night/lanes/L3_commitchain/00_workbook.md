---
ttl: task_bound
---
# L3 提交链车道作业簿（session=st-mastertc-l3）

> 总包夜战 master_tc_night · 车道卡：C02 C05 C147 C152 C248 C300 C330
> 模板=00_orchestration.md §四（六向台账+自审闸+施工记录）。每卡一节。

## C02 死信终局处置

**六向台账**
- ①卡面处方：dead 队列已涨至 1556+（health 03:40 快照 1556；观察期内净 +7=1563；分诊=item 1009/env 266/other 280）。按已落地机制干：dead_letter_doctor + commit_queue dead-archive 官方子命令，分批 ≤10 封/批内容驱动处置（已复活→归档/可回队→裁剪恢复/需属主→登记）。禁真删；只允许官方归档子命令+登记。目标=把"明确已复活/已被取代"的前 3-5 批处置掉并留台账。
- ②HEAD 现状实证：
  - `python scripts/commit_queue.py health` → dead=1556（item 1009/env 266/other 280），max_session_death_chain=160（st-tests-chief-20261004）。
  - doctor --scan → 1556 总袋（已重投 1129，待分诊 427）；手续五族可治愈 21（creation_token 6[自动]/plain_zh 4[自动]/r5_suffix 9[仅处方]/vocab 1/depgraph 1）；env（requeue 即愈）64；不治 342。
  - dead_at 年龄分布：≥14.2 天=1 封、≥14.0=3 封、09-23 05 时簇密集（~21 封 combine/nightfix，LandingEnvironmentError/注册表三件套）。
  - dead-archive 三闸实证（scripts/commit_queue.py:3176 dead_archive_letters）：年龄门槛+revival 互斥（后继在途留）+落地校验（modify=dev 树在/delete=树无，fail-closed 判不了不归档）；同卷 os.replace mv 非删可逆+manifest.jsonl 逐件留痕；blob 引用 B→D 类保全。
  - 抽样 10 封定性：最老袋 q-20260922-st-chainpile-0031（TRANSLATION-COVERAGE 阻断，缺 plain_zh 的三件 src/zephyr/governance/meta_question/* 已在 dev 树=已复活）；st-combine/st-nightfix 簇=9-23 landing 环境异常（注册表三向合并失败/LandingEnvironmentError，属主会话均已死两周+）。
- ③上游依赖：serializer 租约空闲窗（活体持有=整体拒绝，DeadArchiveError 设计行为）；dev HEAD 树（落地判据）。
- ④下游消费者：blob_gc D 类引用集（dead_archive* 前缀识别）；coordination_state_board retired_dirs；health 死信积压读数。
- ⑤冲突面：serializer 租约被 belt daemon（pid=25644，活体+心跳续租）持续持有——夜战 cure 车道群持续入队（pending 19+），drain 近乎连续，归档窗口极窄。三次 dry-run 尝试（03:47/03:55/04:02）均整体拒绝。
- ⑥残余与移交：427 待分诊中不治 342 归 session_takeover_ledger 属主面；env 64 留非夜战窗 requeue（夜战快照会吸收他会话 WIP，禁）。分批窗口已设计好（--days 14.2→14.0→细分 13.8~13.2），租约一空即可执行。

**自审闸：WAIT→（租约空窗内转 GREEN 执行）**——机制/抽样/窗口全就绪，唯一阻塞=serializer 租约活体（设计闸，禁抢）。

**施工记录**（批次台账，≤10 封/批）

| 批 | 窗口(--days) | 计划/实归 | 内容定性 | 结果 |
|---|---|---|---|---|
| 1 | 14.2 | 1/未执行 | st-chainpile-0031 meta_question 三件已复活 | 租约活体拒绝×3，等窗 |
| 2 | 14.0 | +2/未执行 | chainpile-0041 GATE-PRECOMMIT；xhs-full-0043 landing 环境异常 | 同上 |
| 3-5 | 细分 13.8~13.2 | 各≤10/未执行 | 09-23 05 时簇 combine/nightfix（landing 环境异常，属主已死） | 同上 |

## C05 R2 复测（提交提速 deep dive 二轮）

**六向台账**
- ①卡面处方：找 .runtime/tmp 下 csx_deep_01..09 留存脚本；若无按 deep_dive_r1.md 清单重放核心 3 项（锁等待/序列化耗时/门禁链耗时），产 DEEP_DIVE_R2.md 对照 R1 结论（无可回收>5min/天=达标），落 docs/_working/commit_speedup_campaign/60_deep_dive/。
- ②HEAD 现状实证：
  - csx_deep_01..09 原脚本已被 tmp 清理（不存在）；R1 中间数据随归档留存（docs/_working/archive/2026-10/commit_speedup_campaign/60_deep_dive/r1_data/ 10 yaml）。
  - 按 R1 清单重写重放脚本（.runtime/tmp/csx_deep_r2_replay.py，只读；留档副本=r2_data/）：窗口 2026-10-05T00:00+08:00→10-07T03:51（2.16 天）。
  - **锁等待**（R1 未尽事项②插桩已落地=.runtime/audit/lock_wait_events.jsonl）：窗内 711 次/14206s ≈ **110min/天**（main 274 次/14204s 全部在主网关全局锁；四工 worktree 侧≈0=租约分账正常；>60s 事件 53 笔；10-06 夜战日 181min）。R1 估算 ~120min/天获实证。
  - **序列化耗时**：183 笔/84.7 笔每天，间隔 p50=433s mean=1022s p90=2191s（R1: 343/725/1794）——被喂料率混淆，非机制退化。
  - **门禁链**（precommit 通道 total_ms，与 R1 A1 同口径）：w0 mean 302.5s/med 151.0s/p90 1022.8s（R1: 230.7/96.8）——A4 结构问题（hook 成本与件大小脱钩）仍在；**rc=-1 infra 超时全工位=0**（R1 3×1200s/天=60min/天白烧已消）。
  - **可回收对照**：喂料饥饿仍 96.7% claim_none（R1 #1 未修复，窗尾现 no_slot=开始喂料）；重试环 712 次/天阻断（R1 191/天，夜战 11 车道放大）；死信官方归档通道已建成（RB2）；四工重复已被 serializer 租约互斥消除；integrity 基线 head 翻转（09-30）消灭 46.1s/件同步税。
- ③上游依赖：deep_dive_r1.md（已归档）；四工 audit 分账册。
- ④下游消费者：C147（前置未满足）；W5 交付报告。
- ⑤冲突面：docs/_working/commit_speedup_campaign/ 旧位置有他会话在途归档删除（worktree " D"，HEAD 仍有原件）——新文件只加不改不碰其删除；新文件已 batch_creation_tokens 登记（capability=commit_speedup_r2，2 条幂等确认）。
- ⑥残余与移交：残余 3 项（喂料饥饿/重试环/锁等待处置）量化留档 DEEP_DIVE_R2.md §4；R1 未尽事项①（"-" 无门号埋点）未复测留 R3。

**自审闸：RED（判据裁决=未达标）**——锁等待单项 ~110min/天>5min/天阈；已修复 3 项如实记册，残余移交。非冲突 RED，是判据 RED。

**施工记录**：DEEP_DIVE_R2.md 落 docs/_working/commit_speedup_campaign/60_deep_dive/；token 已登记（capability=commit_speedup_r2）。重放脚本因 DIRECTORY-CONTRACT（docs/_working 禁 .py）撤出落点、留 .runtime/tmp（方法内嵌 R2 册 §1）；其 token 条目（r2_data 路径）已入共享注册表 staged 面，成为 inert 残条（追加册不可安全回撤，留 OPEN_QUESTIONS 3）。

## C147 R3 第二轮确认

**六向台账**
- ①卡面处方：依赖 C05；C05 达标后把 R3 第二轮结论写入 decisions_log.md（docs/_working/commit_speedup_campaign/90_verification/，热文件 safe_write_text+CAS）。
- ②HEAD 现状实证：C05 R2 判据裁决=**未达标**（§C05）；decisions_log.md 现存于归档（docs/_working/archive/2026-10/commit_speedup_campaign/90_verification/decisions_log.md），活目录 90_verification/ 不存在（随 campaign 归档，他会话在途搬移）。
- ③上游依赖：C05 达标（不满足）。
- ④下游消费者：campaign 验证链。
- ⑤冲突面：无（未动笔）。
- ⑥残余与移交：R3 第二轮"确认达标"的前置不成立；如总包要落"未达标"结论入 decisions_log.md 须改判授权（本车道按卡面纪律不写）。R2 完整结论已在本作业簿 C05 节+DEEP_DIVE_R2.md 可直接引用。

**自审闸：RED（前置未达标，按卡面不落册）**——非施工失败，是判据链忠实执行。

**施工记录**：无落册动作（设计使然）。

## C152 scheduled_task_reconcile InvariantCulture

**六向台账**
- ①卡面处方：工单曾记 BLOCKED 待属主字节。重查 git show HEAD:scripts/governance/scheduled_task_reconcile.py 时区处理；确无问题→销账；有 bug→最小修+单测。
- ②HEAD 现状实证：
  - Python 侧时区处理**正确**：L111 `_parse_last_run` naive（PS 本地面）→ `ts.astimezone()` 本地 aware；L241 `datetime.now().astimezone()` 同坐标系——与"InvariantCulture 时区 bug"指控无关，无 bug。
  - PS 侧发现真雷（文化敏感格式化）：`_PS_QUERY` 用 `$i.LastRunTime.ToString('yyyy-MM-dd HH:mm:ss')` 未钉 culture——.NET 格式串中 `-`/`:` 是文化敏感分隔符位，异 locale（分隔符非字面）渲染漂移 → Python 侧 strptime 解析失败 → `_parse_last_run` 返回 None → 假"从未运行/哨兵"（优雅退化非崩溃，本机 zh-CN 恰好按字面渲染故未爆）。
- ③上游依赖：无。
- ④下游消费者：schtasks 三色对账日常面（48 任务实测）。
- ⑤冲突面：scripts/governance/scheduled_task_reconcile.py 与 tests/governance/test_scheduled_task_reconcile.py 均 claim 成功（st-mastertc-l3）。
- ⑥残余与移交：无。

**自审闸：GREEN→DONE**

**施工记录**：最小修=ToString 追加第二参 `[System.Globalization.CultureInfo]::InvariantCulture`（1 行）；新增回归测试 `test_last_run_format_pins_invariant_culture`（断言 culture 钉死+格式串成对）；pytest 17/17 过（3.33s）；活体验证 collect_system_tasks() 实采 48 任务日期解析正常。

## C248 W-177 m1_data 两车道同名文件合并

**六向台账**
- ①卡面处方：总包裁定=HEAD 版为真源。若两车道版本仍并存逐一 diff，字节同则销账；异则以 HEAD 为准、另一版本归档登记。
- ②HEAD 现状实证：
  - 溯源：W-177=total_command_closeout/00_master_skeleton.md:237（m1_data/01_ingest.md + pending_rulings.md 两车道同名合并，验收=同名文件单真源+合并段 `git show HEAD:` 命中）。
  - 主区 worktree 对 m1_data/ 零未提交改动；HEAD 最后触这两件=30505c93f6（09-24 大批）。
  - 全仓同名扫描：.aidrafts/st-bt-fast-w5-20261006/ 下的 m1_data/01_ingest.md 与 pending_rulings.md 与 HEAD **逐字节相同**（diff -q 双双通过）；st-wm1-mineB/mineC/buildA/buildB 四车道 staging 目录均无 m1_data 残留（已 promote 或清理）。
  - pending_rulings.md 为单源连贯册（2026-09-25 快照，R-M1-01~08 一行一案+三态汇总）——两车道版本早已收敛入 HEAD。
- ③上游依赖：无（收敛已发生）。
- ④下游消费者：m1_data 消费面（M1 数据链）。
- ⑤冲突面：无。
- ⑥残余与移交：无。

**自审闸：GREEN→DONE（销账）**——单真源已成立，无需施工。

**施工记录**：证据链如上；零文件改动。

## C300 R6 commit_queue_interactive

**六向台账**
- ①卡面处方：裁定=维持现状（已 enabled）+窗口=下维护窗，登记销账（写入 workbook+若 flags.yaml 有注释位且无锁则补一行注记）。总包代裁基准（orchestration §六）同文。
- ②HEAD 现状实证：config/flags.yaml `commit_queue_interactive: enabled: true`，implementation_status=production（2026-09-12 Owner 批在册，回滚通道=flag OFF）。
- ③上游依赖：L10 代裁基准已给（无需再裁）。
- ④下游消费者：commit_queue 锁忙改道语义（LOCK_TIMEOUT 自动入队）。
- ⑤冲突面：config/flags.yaml claim 成功；safe_write_text+CAS 写入（expected_base_sha256 校验过）。
- ⑥残余与移交：下维护窗复核翻转点（回滚=flag OFF 存量 drain 完毕后关闭）。

**自审闸：GREEN→DONE（销账）**

**施工记录**：flags.yaml 注记 1 行已落（`# [C300 销账 2026-10-07·总包夜战 master_tc_night §六代裁基准] 维持现状…复核窗口=下维护窗`），写后 sed 进程外核实+git status 确认 M 态在册。

## C330 QMine 收尾汇总卡

**六向台账**
- ①卡面处方：逐项核对 ①CAND-GOVTEST 撞号（应已修）②api_server 心跳（已修）③snapself+EV（L11 在办，标依赖）⑤blob_gc（L5 在办）——汇总销账或转依赖，不重复施工。
- ②HEAD 现状实证：
  - ①CAND-GOVTEST 撞号：candidate_module_registry.yaml 现为 001..007 连号，Counter 逐 id 校验**零重复**（HANDOVER.md:35 所记 005 撞号重编号 007 已落 HEAD）→**销账**。
  - ②api_server 心跳：src/zephyr/frontend/dashboard/api_server.py L5105-5121 `_write_heartbeat`+HEARTBEAT_PATH（tmp/dashboard.heartbeat，管道格式 ISO8601|pid|pid）在 HEAD，带 M10 豁免注（QMine F 批 PERM-TRIGGER 实弹裁定 st-qmine-20260925）→**销账**。
  - ③snapself+EV：HANDOVER.md:48-50 记 dbf5ee8a6c 护栏族重放（10 红测试：test_commit_queue_snapshot_selfconsistency 6 红+test_evaporation_cure_lane_ev 4 红），处方=按原样重放——**L11 测试重收编在办，转依赖**（本车道不重复施工）。
  - ⑤blob_gc：qmine_campaign/04_blobs_gc/ 由 L5 数据库车道在办（其 workbook 本夜在册）→**转依赖**。
- ③上游依赖：qmine_campaign/HANDOVER.md+00_skeleton_overview.md。
- ④下游消费者：99_delivery 交付报告。
- ⑤冲突面：无（只核对不修）。
- ⑥残余与移交：③⑤两项依赖 L11/L5 落地，验收口径=对应红测试转绿/blob_gc 官方通道执行记录。

**自审闸：GREEN→DONE（两项销账+两项转依赖）**

**施工记录**：零文件改动，纯核验。

---

## OPEN_QUESTIONS

1. **C147 改判授权**：R3 第二轮"确认达标"前置不成立（C05 R2 判据 RED）。如总包要把"未达标"结论正式落 decisions_log.md（而非仅作业簿留痕），须总包改判授权后由授权车道 safe_write_text 落册。
2. **C02 租约窗口**：belt daemon 活体持有 serializer 租约且 cure 车道群持续入队，归档窗口极窄。批次窗口（--days 14.2/14.0/细分 13.8~13.2）已设计好，建议 W5 收尾队列清空后由任意车道按本簿台账执行（每批 ≤10、--execute 前先 dry-run 复核）。
3. **capability_canonical_file_registry.yaml 巨量 staged 面待归属**：该共享册 staged 层有 ~59k 行级重写（他会话批量面），本车道 token 2 条已入 index 随其落地；建议总包核归属车道提交时序。

## CONFLICT_LEDGER

| 时间 | 对象 | 冲突 | 处置 |
|---|---|---|---|
| 03:47/03:55/04:02 | serializer 租约（pid=25644 活体） | dead-archive 整体拒绝×3 | 设计闸禁抢，C02 转 WAIT 等窗 |
| 03:41 | lock_files cleanup | registry 互斥锁超时 DENIED×1 | 03:42 重试成功（清 1 死锁：qmine_campaign/04_blobs_gc/workbook.md 他队残留） |
| 持续 | docs/_working/commit_speedup_campaign/ 旧位置 | 他会话在途归档删除（worktree " D"，HEAD 仍有原件） | 只新增不碰删除，新文件 token 已登记 |

## DONE_SUMMARY

- C152 **DONE**：InvariantCulture 最小修+单测（17 过）+活体验证。
- C248 **DONE（销账）**：m1_data 单真源已成立（字节级证据链）。
- C300 **DONE（销账）**：维持现状+下维护窗，flags 注记已落。
- C330 **DONE**：①②销账+③⑤转依赖（L11/L5）。
- C05 **DONE（判据 RED）**：R2 重放三核心项实测，DEEP_DIVE_R2.md 落册，未达标结论+残余量化移交。
- C147 **RED（前置未达标，不落册）**：卡面条件忠实执行，改判权交总包。
- C02 **WAIT（租约窗口）**：机制/抽样/批次窗口全就绪，三次执行尝试被活体租约拒绝（设计闸），台账留全。


---

# 接手班续（session=st-mastertc-l3b · 2026-10-07 08:12-08:5x）

> 前任 st-mastertc-l3 超时，本班按"续写勿重做"接手：前任七卡结论全盘维持，本班动作=落地收口+C02 抢窗。
> 环境变更记册：08:3x 战役树由他会话改名 master_tc_20261006→master_tc_night（本簿随迁，头行 Orchestrator 已更新）；旧路径索引面随之清空。

## 本班卡况总览

| 卡 | 前任结论 | 本班动作 | 本班状态 |
|---|---|---|---|
| C02 | WAIT（租约活体×3 拒） | 判据修正+精细窗切批+后台 watcher 长轮询 | 见 §C02-R2 |
| C05 | DONE（判据 RED） | 核实：DEEP_DIVE_R2.md 在册（83 行，staged，随本班 docs 袋落地）；csx_deep_r2_replay.py 留存 .runtime/tmp（与前任 DIRECTORY-CONTRACT 撤出记录相符） | 维持 DONE（83 行超卡面 ≤80 上限 3 行，前任成品内容完整优先，记注不重做） |
| C147 | RED（前置未达标不落册） | 核实：C05 R2 未达标结论成立；90_verification/decisions_log.md 已随战役归档，活目录无此文件 | 维持 WAIT（卡面=达标才落册，忠实不写） |
| C152 | DONE（施工毕未落地） | 定向 pytest 17/17 绿复验（1.20s）+入队 | **已落地 4e43d191a3** |
| C248 | DONE（销账） | 无新证据 | 维持 DONE |
| C300 | DONE（销账未落地） | flags 注记在途核实+入队 | **已落地 bb6a03f5c1** |
| C330 | DONE（2 销账+2 转依赖） | 无新证据 | 维持 DONE |

## C02-R2 执行台账（本班）

- **机制确认**：dead_archive_letters 三闸（年龄≥--days／revival 互斥／落地校验 fail-closed）+租约存活整体拒绝；CLI `dead-archive [--days N] [--execute] [--json]` **无单批上限参数**→每批 ≤10 用精细 --days 窗实现（批界=名单相邻年龄中点）。
- **窗口实证**（08:2x 扫描）：dead=1631；≥14.42d=1（q-20260922-st-chainpile-0031）｜14.24/14.21=2（chainpile-0041/xhs-full-0043）｜14.13~14.06 密集簇 21 封（st-combine-20260923-0001..0018+st-nightfix-0006..0009，landing 环境异常簇，属主会话均已死两周+）。
- **批切计划**：dry-run pass 名单（三闸全过）按年龄降序切 3 片各≤10 合计≤30；kept.unlanded/revival 留原位附处方=分诊"需属主/已被取代"自动留册；已过落地校验=分诊"已复活"。目标减量 20-30，不求清零。
- **尝试史**：08:14-08:27 探窗全拒（pid=25824→39120→47072 连续 drain；lease renewed_at==acquired_at 实证真实排空非僵尸）；**判据修正=前任脚本把 dry-run exit 1（有 kept 留封）误判为 busy 白烧开窗瞬间**——exit 码不作 busy 判据，JSON 有 archived 即有效。08:40 起 watcher 后台长轮询（等窗与施工并行，不空转）。
- **本班自伤认知**：08:31-08:32 本班入队两袋使列车延长≈2 个 drain 周期——提交落地优先于归档抢窗，如实记册。
- **RESULT**：见文末补记（watcher 收尾后回填；若本班窗内未开，脚本移交下班一条命令续跑）。
- **移交**：脚本=.runtime/tmp/c02_archive_r2.py（探窗→dry-run 取 pass 名单→切 3 批→execute 全自动幂等可重入）。

## L7 移交代管袋（禁代改，移交收尾班）

- **q-20261007-st-mastertc-l10-0001**：属主 st-mastertc-l10（已死 heartbeat=exited/注册表无在册）；08:2x 实证 state=**dead**（非 pending）；dead_reason=ghost_session（裁定#459 存活闸拒自动重投；CLI 手动 requeue 不受闸限，人工可强制）。
- 内容清单（1 文件）：**docs/01_policies_and_standards/_registry/catalogs/ruling_registry.yaml**；message=[st-mastertc-l10][裁定#488]总包夜战全量⏳处置一次落册：A 段 Owner 保留七项登记关账（C63/C287 实盘资金；C109/C410/C267 物理删除三段式；C36/C37/C45 VM 依赖）+B 段代裁基准分项表（C81 收编唯一/C82 接线/C398 并存至 10-08 复核/C102 TTL+PG 镜像/C103 quarantine/C19 warn 维持/C21 封存/C24 su…（截断）。
- 处置路径（收尾班择一）：①属主复活 requeue；②内容仍有效则人工 `commit_queue.py requeue q-20261007-st-mastertc-l10-0001` 强制；③内容已被他 commit 覆盖则 dead-archive 官方归档。**本班按禁代改纪律未动。**

## 本班入队袋

| qid | 卡 | 文件 | 终态 |
|---|---|---|---|
| q-20261007-st-mastertc-l3b-0001 | C152 | scripts/governance/scheduled_task_reconcile.py + tests/governance/test_scheduled_task_reconcile.py | **落地 4e43d191a3** |
| q-20261007-st-mastertc-l3b-0002 | C300 | config/flags.yaml | **落地 bb6a03f5c1** |
| （docs 袋） | C05/C02 | 60_deep_dive/DEEP_DIVE_R2.md + master_tc_night/lanes/L3_commitchain/00_workbook.md | 收尾入队 |


### C02-R2 RESULT 回填（10-07 08:53）

- **执行结果**：批 1 归档 **1 封**=q-20260923-st-chainpile-20260922-0041（spot_check identical=1=逐字节复活实证）→ 袋 dead_archive_20261007/+manifest.jsonl 留痕（mv 非删可逆）。批 2/3=零封可归（三闸 pass 名单耗尽，无强归对象）；落地尝试 1/3 预算。
- **分诊台账**（≥13.4d 全样本 **45 封**，判定=官方三闸+HEAD 树逐文件落地校验同法）：**已复活（全件落地）=1**（上者，已归档）；**需属主（部分落地，fail-closed 留原位附处方）=44**；**已被取代（revival 在途后继）=0**。
- **结论**：目标"减量 20-30"未达（机制性不可能——该年代死信 100% 为部分落地集，官方闸按设计拒绝归档未全落者；前任"已复活"定性仅对 0041 一封成立）。死信清淤的真路径=逐封处方修复重投（属主面），非批量归档。台账移交 session_takeover_ledger 属主面。
- **分诊明细**（45 封，landed=HEAD 树命中/总件数）：

| 年龄d | qid | 属主会话 | landed |
|---|---|---|---|
| 14.44 | 0922-st-chainpile-20260922-0031 | st-chainpile-20260922 | 4/7 |
| 14.24 | 0923-st-xhs-full-20260922-0043 | st-xhs-full-20260922 | 9/16 |
| 14.15 | 0923-st-combine-20260923-0001 | st-combine-20260923 | 5/9 |
| 14.15 | 0923-st-combine-20260923-0002 | st-combine-20260923 | 5/9 |
| 14.15 | 0923-st-combine-20260923-0003 | st-combine-20260923 | 5/9 |
| 14.14 | 0923-st-combine-20260923-0004 | st-combine-20260923 | 5/9 |
| 14.14 | 0923-st-combine-20260923-0005 | st-combine-20260923 | 5/9 |
| 14.14 | 0923-st-nightfix-20260923-0006 | st-nightfix-20260923 | 10/13 |
| 14.13 | 0923-st-nightfix-20260923-0007 | st-nightfix-20260923 | 9/12 |
| 14.13 | 0923-st-combine-20260923-0006 | st-combine-20260923 | 5/9 |
| 14.13 | 0923-st-nightfix-20260923-0008 | st-nightfix-20260923 | 10/13 |
| 14.13 | 0923-st-combine-20260923-0007 | st-combine-20260923 | 5/9 |
| 14.12 | 0923-st-combine-20260923-0008 | st-combine-20260923 | 4/8 |
| 14.12 | 0923-st-nightfix-20260923-0009 | st-nightfix-20260923 | 1/3 |
| 14.12 | 0923-st-combine-20260923-0009 | st-combine-20260923 | 4/8 |
| 14.11 | 0923-st-combine-20260923-0010 | st-combine-20260923 | 4/8 |
| 14.11 | 0923-st-combine-20260923-0011 | st-combine-20260923 | 4/8 |
| 14.11 | 0923-st-combine-20260923-0012 | st-combine-20260923 | 5/9 |
| 14.10 | 0923-st-combine-20260923-0013 | st-combine-20260923 | 5/9 |
| 14.10 | 0923-st-combine-20260923-0014 | st-combine-20260923 | 7/12 |
| 14.09 | 0923-st-combine-20260923-0015 | st-combine-20260923 | 7/12 |
| 14.08 | 0923-st-combine-20260923-0016 | st-combine-20260923 | 7/12 |
| 14.08 | 0923-st-combine-20260923-0017 | st-combine-20260923 | 7/12 |
| 13.72 | 0923-st-deepclean-20260923-0001 | st-deepclean-20260923 | 2/4 |
| 13.71 | 0923-st-regfix-lane0b-20260923-0015 | st-regfix-lane0b-20260923 | 2/4 |
| 13.68 | 0923-st-wm1-buildB-20260923-0001 | st-wm1-buildB-20260923 | 10/13 |
| 13.64 | 0923-st-chainpile-20260922-0055 | st-chainpile-20260922 | 4/7 |
| 13.64 | 0923-st-combine-20260923-0018 | st-combine-20260923 | 7/12 |
| 13.64 | 0923-st-xhs-full-20260922-0053 | st-xhs-full-20260922 | 9/16 |
| 13.62 | 0923-st-nightdata-20260923-0001 | st-nightdata-20260923 | 1/2 |
| 13.56 | 0923-st-chainpile-20260922-0058 | st-chainpile-20260922 | 4/7 |
| 13.55 | 0923-st-regfix-lane0b-20260923-0017 | st-regfix-lane0b-20260923 | 1/2 |
| 13.54 | 0923-st-chainpile-20260922-0059 | st-chainpile-20260922 | 4/7 |
| 13.52 | 0923-st-emoreplay-20260923-0001 | st-emoreplay-20260923 | 8/11 |
| 13.52 | 0923-st-chainpile-20260922-0060 | st-chainpile-20260922 | 4/7 |
| 13.49 | 0923-st-emoreplay-20260923-0002 | st-emoreplay-20260923 | 9/11 |
| 13.46 | 0923-st-chainpile-20260922-0061 | st-chainpile-20260922 | 4/7 |
| 13.46 | 0923-st-k4-20260923-0006 | st-k4-20260923 | 7/10 |
| 13.45 | 0923-st-chainpile-20260922-0062 | st-chainpile-20260922 | 4/7 |
| 13.45 | 0923-st-chainpile-20260922-0065 | st-chainpile-20260922 | 4/7 |
| 13.45 | 0923-st-k4-20260923-0007 | st-k4-20260923 | 7/10 |
| 13.45 | 0923-st-chainpile-20260922-0066 | st-chainpile-20260922 | 1/1 |
| 13.45 | 0923-st-e2e-20260924-0008 | st-e2e-20260924 | 13/17 |
| 13.43 | 0923-st-chainpile-20260922-0067 | st-chainpile-20260922 | 5/8 |
| 13.40 | 0923-st-chainpile-20260922-0069 | st-chainpile-20260922 | 5/8 |
