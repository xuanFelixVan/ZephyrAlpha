---
ttl: task_bound
completes_when: 本册每条改判都被 00/01/10 三册引用为唯一口径且无残留旧叙述
---

# 实测更正与新增案件册（X 册 · 六路案卷回笼后的改判清单）

> **本册是唯一口径**：`00_master_skeleton.md` / `01_adjudication_master.md` / `10_wave_plan.md` 与本册冲突时，**以本册为准**（原册保留不改写，是为留审计面，不是留正确口径）。
> 每条格式：`声称（出处）→ 实测 → 改判`。证据=案卷 A（提交链）/B（灾备）/C（六图）/D（AI 层）/E（GPU 回测）/G（业务链）。

## §一 撤案与改道（把预算从错误的病上撤下来）

| # | 交接书声称 | 实测 | 改判 |
|---|---|---|---|
| X-01 | 六图令 §3-A：「own-scope 治本是卡住全部落地的前置，做完 7 袋一投即合」 | 该役 `pending=0 done=2 dead=33`，声称的 7 袋**全在 dead**，死因 **13 类**（TRANSLATION-COVERAGE 11／CREATE-GUARD 8／GATE-PRECOMMIT-RUN 2／基底不可知 2／RULING-REFERENCE 2…）；被点名的 -0029 实为 `WorktreePunchThroughError`（EV-02 reset 打穿主仓 93e55f2f46→16d58a652d），-0034 实为 CREATE-GUARD 缺 token 且被点文件就在它自己 38 件清单内；全 dead 文本含"外来 staged"仅 **2 封** | **撤下 own-scope 治本作为落地前置**（Z-07 降级为观察项 W-22）；落地通道改走"新建件三件套补齐 + 悬空裁定号清除 + 基底显式"（波 2 配方 R-2）。省下的预算转投 X-02 与 X-08 |
| X-02 | 波2 令 D 项：「门禁 priority 撞号致停摆，已由本役修复（DOC-HEADER-SUITE 77→130 等）」 | HEAD 现态 `BLUEPRINT-FORMAT=130 / DOC-HEADER-SUITE=77` 由**他道**落地；本役 worktree 是 **77/130 互换**；worktree 基底 `f3cac8b95c` 上两者同为 77（即 outage 原状） | 本役的 priority 改动**作废**：落地前必须先剔除该 hunk、以 HEAD 为准（否则=把已修好的停摆改回去）。列入 W-11 前置排雷，不算待裁 |
| X-03 | 波2 令 B 项／记忆：「环节分母定档 122→132」 | HEAD 内 `00_全环节总册.md` 唯一 F 号 = **122**；机生对账尺读数 `covered 66 + uncovered 56 = 122`；"132"与"~151"**只存在于散文** | 定档口径改两级：**122＝在册机生真源**；132＝"6 本真缺实簿落地后"的**预期面**，落地前禁引用；151＝作废。骨架册 §三 的 X-3 行按此改 |
| X-04 | 裁决归总令 裁3：「`cmd_successor_20260925/` 13 件撞 R5 待入库」 | 该目录盘 51 == HEAD 51，双向差集空，仅 `LEDGER.md` 处于 `MM`；首入 HEAD 于 `30505c93f6`，**该 commit 标题自述"四门临时禁用+emergency 通道"** | **撤"待入库"案**（Z-39 作废）；新开审计案 X-11（绕门核查）。R5 判定式实测 `r"_\d+$"`（gate L80，L115-142），**无白名单无逃生标**，"特批豁免"在本仓不存在 ⇒ 当初若真撞门也只有改名一条路，而它已入库 |
| X-05 | 灾备令风险 1：「主区 index 141 件 staged 删除疑为某车道 untrack 清扫，若致测试失跟踪仅重投该一件」 | 删除归属**查不到**（claim_snapshots 0 命中、队列 delete 动作 0 命中、stash 空），131 件盘上仍在；被点名的 `tests/frontend/test_services_registry_backup_probe.py` **仍在 HEAD 跟踪面**（blob `1513f7e5`），porcelain 为 `D` + `??`，磁盘 13627 字节与 HEAD **sha256 同值** | **无需重投、无需代修**：登记为"index 与 HEAD 双态并存"观察项（W-93），列入波 8 前复查；禁对他人 staged 做任何吸收/还原 |
| X-06 | 灾备令／记忆：「CH 一张表攒 >100 零字节破损件致全库 `system.*` 永久失败」 | 本窗实测经 `DatabaseService` reader：`system.macros`/`system.parts`(29053)/`system.databases`(5) 全部返回不抛错；`WHERE bytes=0` 破损件 **0** | 该病**当前未现**；旧结论标"过期"。但处方不变：任何读标度定容差的尺，**探测失败必报红**（P-注-4 关闭，改为常设探针 W-102-4） |
| X-07 | 灾备令：`backup_state.json` 的 `last_backup_status/log_verified` | 真键名是 `last_backup_status`/`last_backup_log_verified`/`last_run_outcome`（**无** `status`/`log_verified`）；现值 `ok` / `False` / `lock_skipped` | 所有引用该件的脚本与台账改按真键名；"failed"是历史轮次读数，当前轮 `ok` 但**可恢复性仍零实证**（W-45 不变） |
| X-08 | 灾备令 P-28：「svchost 被误杀 7 条」 | 今日 33 条 KILLED 中 name/cmd 一致仅 19 条；`name=svchost.exe` 的 KILLED **5 条全部带 [FAILED]**（01:58:34×3、07:17:33、09:01:37），其余 15 条 svchost 是 **DRY-RUN** tag（不可当实杀读）；另有 11 条 KILLED 活体名是 conhost/bash/backgroundTaskHost 而无 [FAILED]。07:17 与 09:01 两条发生在 AccessDenied 治本 `dc1c66e651`（02:30）**之后** | 案成立但**规模与形态要重写**：真缺陷＝`_reap_incubated_expired()` 杀前只验"PID 在进程表存在"，keep/白名单比对的是台账 `rec["cmd"]`（L1005/L1011），快照里现成的 `create_time` **从未参与比对**（而对照腿 `kill_ghost_windows` L717 已有 recheck）。⇒ 处方内收为**复用已有 recheck 判据 + 加 create_time 第三要素**，禁写第二套（W-41 处方升级） |
| X-09 | 灾备令 P-26：「.worktrees 占源树条目 93.8%」 | 全树实测 `.worktrees` 占 **92.42%**（497798/538635，轻 IO 3.2s）；336678 是 Mode B **增量 diff** 计数（同日 prev_snapshot==day_target）；生效排除清单（config L34）确无 `.worktrees`；另有两口径被并谈：`.worktrees` 目录项 **52** vs `git worktree list` **73** | 数字按实测改；两个"52/73"必须在一切统计里注明口径（注册表/清单类计数禁裸写）。⚑-3 的性价比论证换用 92.42% + "Mode B 增量语义" |
| X-10 | 波2 令 M 项：「tests/ai_layer 776 passed/0 failed/0 skipped」与「T5 35 个 HEAD 常红」 | `.runtime/tmp/v_b/red_nodes.txt` **不存在** ⇒ 35 红清单无从逐条验真（仅 pf_alloc 一例根因复现：`sim_paper_ledger.py:426/:428` 幽灵钱包闸 → `not_in_registry_sim` 零写入；其余三面抽样全绿） | W-38 改为**两段**：①先在落地面逐目录重跑出真红清单（波 7 的 7.1 顺带产出）②再逐条修。禁照旧清单施工，禁为凑数跑 |

## §二 新案（交接书没提、实测挖出来的）

| 号 | 新案 | 实测证据 | 定性 | 归位 |
|---|---|---|---|---|
| X-11 | **绕门落地审计**：某 commit 以"四门临时禁用 + emergency 通道"名义把 678 件批量入 HEAD | `30505c93f6` commit 标题自述；宪法第 9 节第 8 条只允许"注册表/锁不可用时"用 emergency，且手写标记判 forged | 治理事故级待核：核该窗四门为何被禁、禁窗内落了什么、是否留批文 | 新 W-5a（波 5.5），只出案卷不擅回滚 |
| X-12 | **实载门数 < 名册门数**：进程内 `auto_register_gates` 实载 99 台 vs 名册 103 条；差集由 `enabled:false` 与装载异常两态混成（波2 worktree 面实测 96＝103−7） | A 册进程内实调 + D 册对照 | **执法洞**（比提速优先）：必须先分诊差集每台属"主动禁用"还是"装载失败"，两态处方相反 | 波 1.1（升级）＋⚑-6-3 |
| X-13 | **热册正在被陈旧快照回退**（施工期活的蒸发事件，非历史案）：HEAD/index 各 11389 条 token，盘上只剩 11374，缺的正是当天 13:42 落地的 16 条战役 token | 本班实跑三态分诊 + 修复（`盘缺HEAD 16→0`，他人 1 条在途保留，YAML 复解析过） | 结构性：任何后续袋都可能把这 16 条再抹一次 | 配方 R-1 已固化；新增常设尺 W-28b（热件盘-HEAD 键集合差自检，事件触发） |
| X-14 | **注册表登记了不存在的脚本**：`scripts/governance/fullflow/generate_fullflow_crosscheck.py` 在 HEAD 与工作区均不存在，却在 `capability_canonical_file_registry.yaml:52534` 有条目（真身只在 `.worktrees/st-ailayer-final-20260924/`） | G 册 + 本班 `find` 双证 | 悬空登记＝`REGISTRY-CODE-ANCHOR`/`DOC-REF-BROKEN` 同族病 | 波 2.2 随件落地即消；落地前禁引用它做终验 |
| X-15 | **审计账本里已有测试夹具污染行**（且已入 HEAD）：`data/audit-trail/rolling_archive_plan_shadow.jsonl` 34 行中含 t0/t1 夹具，本役窗口又追加 4 行（`MM`）；根因常量 `rolling_archive_reconciler.py:70`，测试件只 monkeypatch `STATE_FILE` | D 册 | 判据污染级：审计面不可信 | 波 3.8 首件；处方见 X-20 |
| X-16 | **死信分诊册与红蓝测试从未进过任何分支**：`test_redblue_governance.py`、`test_redblue_robust.py`、`dead_triage.yaml`、`dead_triage_r2.yaml` 在**全部分支历史零 commit**，`DEEP_DIVE_R1.md` 仅盘上未跟踪 | A 册 `git log --all` 反查 | 波 1.8 捞回；同时说明"提交链终局令"的多数交付物**其实不在库里** | 波 1.8 |
| X-17 | **`hardlinked` 恒 0**：近 5 轮备份 `hardlinked=0` ⇒ 声称的硬链去重从未生效；且 `code_backup.status="failed"` 而 `robocopy_exit=0`，**单件（只读位 `0o100444`）拖垮整轮** | B 册 | 装饰性声明 + 一票否决耦合两条病 | 波 4.2/4.3 |
| X-18 | **备份护甲落后 5 小时**：`D:\zephyr_t1_backup` 侧 `strategy_intake` mtime=02:49 早于 T1 产物 07:47（而 `shield.log` 14:26 仍在活动） | E 册 | "10 分钟 robocopy 镜像 T1 产物"的声称对后段不成立 | 波 0.4 登记；根因（增量判据 or 路径错位）交灾备道 |
| X-19 | **保活进程是 sleep-loop 而非工作会话**：PID 37548 每 300s re-register 并持 3 个业务文件 claim，而真身（T1 PID 3584、做T PID 33548）已亡 | E 册 + 本班会话表 | 与宪法第 9 节第 3 条（禁 sleep-loop）对撞；且它会把"避让活会话"的判据带偏 | 波 0.5：避让判据从"活会话"改判"活 claim + 活产物 mtime" |
| X-20 | **夹具污染处置的正确形**（治本，不制造二次事故） | — | ①修根因：把 `STATE_FILE` 由常量改为可注入，测试一律重定向 `tmp_path`；②**不删历史行**（审计面），改为**追加 correction 记录行**声明那 6 行为夹具污染并在台账标注；③加防复发尺：跑完该测试后 `data/audit-trail/rolling_archive_plan_shadow.jsonl` 字节数必须不变 | 波 3.8；配方入 `11_rescue_playbook.md` R-5 |
| X-21 | **`sector_constituent` 已滞后 21 天**：表实存非空（236836 行）但 `max(update_date)=2026-09-03`，而它是三处采集宇宙的唯一读取源 | G 册 | 板块/个股宇宙派生自陈旧成分 ⇒ 下游全链一致性存疑（不属任何交接书待办） | 新 W-35b（波 3，数据线道），P1 |
| X-22 | **业务链三态实际读数与案卷自述不符**：表体逐行复算＝✅29/🟡25/❌8（非 30/23/9）；且"不通 9 条"清单第 9 项指 #43 pattern_win_rate，而表体 #43＝决策日报判 ✅、62 行内**无** pattern_win_rate 行 | G 册 | 案卷自身内部不一致；链路台账要重生成（静态清单禁手工维护） | 新 W-40b：以生成器重出三态表，禁手改 |
| X-23 | **"270/271 差 1"有确定真因**：`tasks.yaml` 列表 271、`task_id` 唯一 270，重复项＝`cohort_ledger_daily`（`:3437` 与 `:3816`）；账本维另给第三分母 266（与配置双向差集 6/10，10 恰等于 NEVER_RUN） | G 册 | 不是枚举口径差，是真重复登记 | 新 W-31b：去重 task_id + 三分母对账尺（配置/账本/执行） |
| X-24 | **假绿灯判据现势已变**：`suspend` 目标表本窗＝36 行／max `trade_date` 2026-09-23，三腿不再满足"表 0 行"；`suspend_status_derive_weekend` 账本 fetched/written＝36/36，连自设判据也不满足 ⇒ "不可分辨集合 4"本窗仅 **1 件**成立；`realtime_snapshot`、`etf_benchmark` 仍 0 行 | G 册 | 尺本身仍必要（这几件是"跑过无差异"型），但**具体名单要现跑现出** | 波 3.2 判据改"现跑现出名单"，禁引旧名单 |
| X-25 | **空壳表张数三处互异 + 跨库重名说不成立**：骨架点名 10 张、`mine_pipe_blockage_substages.md:121` 称"9 张"却只列 8 张、本窗抛错型实读点名 12 张中 **11 张 count=0**（唯 `suspend` 非 0）；`stock_valuation` 全库唯一在 `c1_market` | G 册 | 三套数都要废，以实读集合为准 | 波 3.5 首步＝出实读集合表 |
| X-26 | **跨库 `system.tables WHERE name LIKE '%x%'` 会静默返回 0** 而表实际存在（三次复测同果，带 `database=` 限才正常） | G 册 | 名称探测型判据全部不可信（含既有案卷里 "table_missing_in_ch" 判定） | 立法：一切"表不存在"判定必须带 `database=` 限定 + 双探测；入 W-102 尺族 |
| X-27 | **案卷自身的落库读数走的是会静默返回空的函数**：`business_pipeline_skeleton.md:29` 用 `zephyr.ch_writer.query`，该函数异常时 `return ""`（`ch_writer.py:445/459/483`） | G 册 | 同一战役的两套可信度；案卷证据要分级 | 新增证据分级制（见 §三） |
| X-28 | **ALGO-NOTE-SYNC 结构性半执法**：地图 182 节点仅 121 有 `module_ref`；自测 A（改码未改 yaml）命中，自测 B（`process_reaper`/`tqcenter_provider`）**结构性不触发**；且该门自身在 `fail_open_register.yaml:2354/:5997` 登记为 fail-open | D 册 | "碰实现代码必同步 TDM 说明"这条铁律对 61 个无 ref 节点形同虚设 | 波 5.2：补 `module_ref` 覆盖 + 尺；不改判据数值 |
| X-29 | **波2 役"12 项已批项已实现"的形态修正**：83 件非案卷产物中 **31 件在 dev HEAD 完全不存在**（src 7／tests 17／scripts 6／config 1，含 `shared/vocab/*`、`confirm_gate.py`、`cleaning_rules_hosting.py`、`weight_ssot.py`、`governance/fullflow/*`、`register_ai_l1_scan_task.ps1`）；且**没有**任何测试件"先入 HEAD 而实现为 0" | D 册 | 假绿形态＝"整批未落地 + worktree 盘上自证绿"，不是"测试在册实现被撕"。⇒ W-28 那把尺的方向要对准"自述绿 vs HEAD 在册"，而非只盯测试/实现配对 | 波 2.2 件数口径改为 31+（D 册逐件清单） |
| X-30 | **价格笼子两枚旗标不在 flags.yaml**：`config/flags.yaml`（HEAD 122→129 行）**无任何 cage 键**，两枚只是 `is_enabled(key, default=False)` 的模块常量；HEAD 版词表门 grep `official_ontology|values_locked`=0，两面出厂皆 `warn` | D 册 | "出厂 OFF 已测证"的载体不是 flag 册 ⇒ ⚑-4/⚑-6 里"翻 flag"的动作对象要按真实载体改（模块常量 or 补册键），否则翻了个不存在的东西 | 波 5.3 前置排雷 |
| X-31 | **ROOR 一条三个口径互斥**：`REG-STATE-VOCAB-001` 标量 29／散文 28／实册 63；`functional_domain_registry.yaml:343-356` ssot_path↔covers 错配在场（同 path 实为 2 条，非自述 3 条） | D 册 | 派生计数全手工残留 | 波 5.1 |
| X-32 | **`PostSettlement` 计划任务确为 cmd 直调 python 绕过 ps1**（日志主区实存、worktree 面不存在）；全机**无** AI-L1 外扫任务 | D 册 | ⚑-1 的 ② 事实底座成立且已细化 | 呈报口径按此改 |
| X-33 | **全仓"Owner 批准"字样 4 处全部为 HEAD 既有**，波2 役零新增 | D 册 | 本役无伪造；但那 4 处需逐条比对裁定册是否真有对应批准条目（防伪第一道） | 波 5.2 附带核查 |
| X-34 | **T1 verdict 无 `VERDICT:` 字段**，自报 `all_green:false` + `blocking_criteria:[manifest_points, dead_zero, cost_gate_spot]`；`VERDICT_RED` 是 LEDGER 的**转述**；同文件内 `manifest_points`(==3700) 与 `negatives_discipline`(manifest+negatives==3700) **互斥**；`cost_gate_spot.source: replay`（非五档全真跑） | E 册 | ⚑-2 的两项建议全部改向（见 §三 改判后菜单） | 呈裁口径 |
| X-35 | **2 阴格"零方差"不可直读**：哨兵把 `dropna<60` 与 `std==0` 两分支合并打印 `len(net)=1622`（全窗天数，非有效样本数）；"同配方旧引擎同死"无同窗对拍件（旧引擎 T0 两跑各 200 格**不含**该两格；仅 09-15 旧窗现场评出 sharpe=−0.153 存活负值） | E 册 | **"非引擎故障"这一结论目前缺一件同窗证据** ⇒ 不能再按"建议 A 定稿"呈报 | ⚑-2 改判（下节） |
| X-36 | 成本门口径**可复算**：33%＝`grid_20260924-080309/manifest.csv` 内 66/200 sharpe≤0、min −4.7830；56%＝28/50，原始档在 verdict `cost_replay.rows` + `.runtime/tmp/ddup/handover_dryrun.log`；冻结件近两夜零改动（prereg 最近改动=`102a3748fa`） | E 册 | ⚑-2 第①项证据齐备，可呈；但注意其 `source: replay` 限定 | 呈裁口径 |
| X-37 | 去重改造本体为真：`62898892ed` 验真且为 HEAD 祖先、三源件 disk==HEAD、`EQUIVALENCE_VERDICT_T0_200.md` 在 HEAD；点名单文件 `test_factory_grid_executor.py` **37 passed/28.21s**（但 `-p no:cacheprovider` 首跑 INTERNALERROR，必须成对带 `-W ignore::pytest.PytestConfigWarning`）；"原 628 行"盘面无锚 | E 册 | 引擎面可信；"628 行"数字禁引 | — |
| X-38 | 文档计数三处不符：quant_methodology 实 **10 件**（`16d58a652d` 真，但 message/LEDGER 称 11）；gpu_rewrite 10 件（符）；4 个战役 commit 去重后 decision_map 面 **69 件**（非 97）；**编号号文 01~08、12 至今仍不在 HEAD 且盘上亦无** | E 册 | 新增 W-24c：号文缺失要补或声明退役（N-1 洞）；三处计数按实测改 | 波 2.4 |
| X-39 | 「16 条 token／16 本案卷」在册；旧名 `chain_fullflow_20260926` HEAD 面 0 命中；hfq 族 `lineage_version` 仅 `kline_daily_hfq` 有、weekly/monthly 无，**族内共 11 张含 8 张迁移残留**；`kline_daily.adj_factor` distinct=1（恒 1 死列成立）；sector 881 下限 2021-08-02（128 只/159198 行，名册 CSV 127/128 同值）、8803 段 61 只全同；"469→728"在 HEAD 面**未找到出处**，盘上现值 729 | G 册 | ⚑-5 的 DDL 面积从"2 张"改"**族内 11 张，含 8 张迁移残留**"；"469→728"禁引 | 呈裁口径 |
| X-40 | `'str > date'` 两崩溃点精确：`financial_derived_compute.py:397/399`、`consensus_daily_compute.py:146-147/155/157`，HEAD **无归一**；`financial_derived_build` 最近 FAILED＝09-25T21:32:12Z（新实例）；`reconciliation_differences` **两库皆空**（DuckDB read_only 与 CH 各一） | G 册 | 波 3.1 有精确锚；X-18(三源收敛) 的"双源皆空"复现，判"空即干净=假绿"成立 | 波 3.1/3.6 |

## §三 改判后的 Owner 菜单差异（只列变化项，全文见 `93_owner_menu.md`）

1. **⚑-2 第②项建议从"定稿"改为"先补一件同窗对拍"**（依据 X-35）：诚实标价代价＝多花半天，买到的是"这 2 格确实与引擎无关"的可复算证据；不补就定稿＝把转述当结论。
2. **⚑-2 第①项可以呈**（依据 X-36 证据齐备），但要在单上注明其 `source: replay` 限定，不写成"五档全真跑"。
3. **⚑-5 的 DDL 面积改口径**（依据 X-39）：不是"周/月两张补列"，而是"hfq 族 11 张（含 8 张迁移残留）统一定 lineage 方案"。
4. **⚑-3 的性价比数字换成实测 92.42% + Mode B 增量语义**（依据 X-09）。
5. **⚑-4 里"翻 flag"的动作对象要按真实载体**（依据 X-30）：价格笼子两枚是模块常量不在 flag 册 ⇒ 呈报时把它从"flag 翻转"改列为"新增 flag 键（出厂 OFF→ON）"，否则翻的是不存在的东西。
6. **⚑-6 新增第 12 条默认**：三台被他道禁用的门（X-12）在分诊完成前**不擅自恢复**——先分清"主动禁用"还是"装载失败"，两态处方相反。

## §五 F 案卷（元问题/QMine）回笼后的追加改判（X-41..X-52）

| # | 声称（出处） | 实测 | 改判 |
|---|---|---|---|
| X-41 | metaq 令 §三基线命令 `pytest ... -q --no-header`（188 passed） | **原样跑为 INTERNALERROR（0 跑）**：本仓 pyproject 的 `cache_dir` 与 `-p no:cacheprovider` 互斥；去掉 cacheprovider 旗标才得 188 passed（collect-only 独立 188 互证）；ruff 0 error | 91 册波 7 命令加**回退分支**；配方 R-0/§6 的"两旗成对"补一条"若仍 INTERNALERROR 则去 `-p no:cacheprovider`"（与车道施工纪律册口径冲突时以本条实测为准） |
| X-42 | 元问题 283 问三态守恒（151/46/86） | `redblue_metaq_suite.py --scan` 只读实测＝**pass151/fail46/insufficient86 总 283，掉桶 0，R1~R5 全 0 违规** | 判①已完成且在册，**记核销不重做** |
| X-43 | 裁定 A：「`grep -c wo001_003` 输出 0＝已办结」 | HEAD 与盘各 **3 条悬挂**（非 0），而目录与 HEAD 树里都无对应 .py；`wo_intake_reconcile` 三条在册且文件实存 | 判**未办**且确为账实不符；但净删属注册表门位 ⇒ ⚑-5 第 6 项保留，且**新增一句事实**：删除面只有 3 条 entry，不删也不会坏任何东西（引用它们的脚本已改名） |
| X-44 | 裁定 C：「.runtime/tmp/st-metaq-gc-20260924/ 删了不丢知识」 | 目录 84 文件/12M，且**该路径被 28+ 处已入库脚本硬编码为默认产物/读取路径**（读侧有 `exists()` 守卫）；目录内脚本对外零引用；内含 `session_keeper.py` | **判"删了会伤及已入库脚本的默认路径"** ⇒ 自裁改判为：保留目录 + 在台账标注"仅供回读"；若要清，必须先改 28 处引用（属另一批工程）。从 ⚑-5 的删除单里摘出 |
| X-45 | 裁定 B：VM 两件残留待处置 | VM 可达（ubuntu + `sudo -n`），两件均在盘：760K（188 子项）/4.0K | 未办成立；按三段式只做"清单入台账"，删除等 ⚑-5 |
| X-46 | 「D 盘 93%／blobs 960MB」 | D **95%**、F 盘也 **92%**；blobs 21396 块真实 **3.39 GiB**（960MB 是 5803 块孤儿集，dry-run 现值 5895/966.5MB） | 容量策略要把 **F 盘也算紧**（不能把"全挪去 F"当无限出口）；`blob_gc` 的 `--archive/--restore` 实测在册（`run_archive` 行 240），可逆 ⇒ 波 6 用 |
| X-47 | QMine 令①：candidate 007 重编号待办 | **盘面已改完而 HEAD 未变**（005 双条→005/007 各 1，文件处 `MM`）；007 引用 6 处，其中 **5 处所在件尚未入库** | 判跨袋依赖：必须先落引用方件，或把"册条目 + 6 处引用件"同袋（在册处方：门禁代码+它读的册+本体包同袋）。并入 X-48 的落地序 |
| X-48 | QMine 令③：snapself 层待重放 | snapself **已在 HEAD**（def 行 3308／调用 1496），但其测试实测 **6 红**；`_DESTRUCTIVE_GIT_VERBS` 在 HEAD **零实体**；EV 件未跟踪且 **4 红** | 判"落地了但没达标"——正是最危险的那类假完成。铁尺不变：两组红测转绿才算完；`_DESTRUCTIVE_GIT_VERBS` 要按未实现对待 |
| X-49 | arbiter R1：#410 免检授权到期问题 | #410 `status=active`、`expires 2026-10-08`，但它批准的**三袋全 dead**、`rules/` 自 09-24 起零提交零改动 ⇒ **授权从未被执行** | 呈报口径改为"授权空转"：不是"续不续"，而是"要么把三袋落地后自然到期，要么先撤销"。仍属 Owner 亲裁 |
| X-50 | arbiter R4：三台密钥门"password/api_key 零命中"＝判据失效 | 三台在册且 `enabled=true`，**判据本身能命中**；零命中的真因是 `files_trigger` 为**路径子串匹配**（不存在名为 password/api_key 的路径） | 处方从"改正则"改为"**改触发面**"：把这三台的触发从路径型改成 own-diff 内容型（属加严，Z-49 仍成立，机制换掉） |
| X-51 | 车道施工纪律／本班 R-0：`total_gates` 与门禁台数 | `in_process_gate_registry` 标量 **103==列表实长 103**（自洽）；`gate_registry.yaml` 声明 **181**＝另一本（全目录册，非进程内）；实载 99 | 三本数各自成立但**对象不同**，任何统计必须注明是哪一本；骨架册 §三的"gate 台数"行按此改 |
| X-52 | 其它自述与实测差 | `BLUEPRINT-FORMAT` 代码 priority=130 但**三处散文写 77**；exam_loop 白名单实为 3+dsrhythm 1；ALGO-FLOW 标记在 HEAD 有 **3300 件**（"六件"是车道增量口径）；COMPLEXITY 该班自述 **9 非 35**；N-16 改名已落（残留 1 处注释）；`dead_archive_metaq_gc_20260926/` 在盘 89 件**但 HEAD 不跟踪**；AGENTS.md 行 109"7 子命令"实测 8（漂移仍在），而 `#ARCH-AGENTS-SSOT-DRIFT-001` **已在册 in_progress**（行 22528）；QMine HANDOVER §3 实为 **①~⑦**；`10_d_data.md` 19,037 行未跟踪（该域 77 个 .md 只有 README 入库） | 逐条按实测改引用；Z-35 从"是否已登记"改为"已在册，按金哈希规程走"（引用号可用）；Z-37 的 `10_d_data.md` 分叉判据取"入库"支（该域整体没入库，属真缺） |

**新增待办（回流骨架）**：W-133＝candidate 007 与 5 处引用件同袋序（X-47）；W-134＝snapself/EV 两组红测转绿（X-48，属 W-73 的具体化）；W-135＝密钥门触发面改型（X-50，替换 Z-49 的机制）；W-136＝`dead_archive` 目录 89 件是否入库定策（X-52，它是死信归档唯一实体）。

## §五-B H 案卷（归并去重）回笼后的终批改判（X-53..X-58）

| # | 事项 | 实测/检索 | 改判 |
|---|---|---|---|
| X-53 | **空壳表处置其实早有条件批文**（本班初稿误列进 ⚑-5 请新批） | 裁定册现读：**#311**"空壳表 rename 隔离 7 天再 DROP；CAS tmp 直清；bak 类一律冷存不删除，走 RULE-DATA-OPS 三步验证留证"；**#328**"Owner 附条件批准删除三类零风险件：**10 张空壳 CH 表**、~110 件 CAS tmp 残留、integrator_progress.db.bak 三选一。条件＝逐件三层调查（真安全/真无人用/真无价值）全过才删，任一层不过即保留留档"；#382→#399 是废表/备份表两态制（不同对象） | **撤销"空壳表请 Owner 新批"**：改判为**执行任务**（W-34 直接按 #311/#328 的条件通道走，逐件三层调查留证）；`⚑-5` 第 6 项相应缩小为"退役清单里**未被既有裁定覆盖**的那部分"；`⚑-6` 增一条"空壳表按 #311/#328 既有条件批文执行" |
| X-54 | E 与 H 两份案卷对 `cmd_successor_20260925/` 结论相反（E：盘 51==HEAD 51 差集空；H：盘面独有子目录 `adj/ du881_verdict/ engine_caliber_map/ landing/`） | 本班亲自复跑三态：HEAD tracked=**51**、DISK recursive files=**51**、`git status --untracked-files=all` 只报 `MM LEDGER.md`；H 的"21"是**顶层条目数**（含子目录名），非未跟踪文件数 | **E 对 H 错**（口径混淆：`ls | wc -l` 把子目录当文件）。X-04 维持"撤待入库案"结论；教训入册：**任何"未跟踪 N 件"的读数必须来自 `git status --untracked-files=all` 的 `??` 行，不得用目录列举**（此坑与"行数当条目数"同族，本仓已犯多次） |
| X-55 | 队列读数会漂（本班 14:25 记 dead 701/done 741，A 册 15:0x 记 700/741，H 册 15:1x 记 701/738） | 三次数值不同但**同一事实不变**：`pending=0 processing=0`，链在动但无新袋进入 | 台账与菜单引用队列数时**必须带取数时刻**；施工判据不看这些数，只看"我这袋的 qid 现态 + `git show HEAD:`" |
| X-56 | "六段温度词表已定档""16 库≠13 轴已裁""门禁夜间不退役"三条**在册检索字面查无** | #398/#399 判的是丁线词表三批点与状态选择门（非"六段温度词表定档"字面）；"13 轴/16 库"在两册 0 命中；"不退役/夜间不退役"0 命中（仅名册注释旁证 + #384 判的是文档降档） | 三条**仍按硬约束遵守**（它们来自 Owner 对话指令与本仓记档），但**禁引用为"裁定#NNN 已裁"**；一切"已裁勿再议"清单里的每一项，引用前按本行方法重新现读，查无者改标"口径约束（非裁定）" |
| X-57 | 议题册另有与本战役直接相关的在册件 | `#ARCH-317`（open：serializer 单写者无强制）、`#ARCH-330`（resolved：SerializerLease TTL 抢锁） | 波 1 落地序引用 #ARCH-330 为已解决先例、#ARCH-317 为在办；禁重复立案 |
| X-58 | `lineage_version` 的读写侧其实已部分在场 | `git grep -n lineage_version HEAD` → `scripts/governance/meta_question/redblue_metaq_suite.py:95/96/305/319`、`wo004/recalc_hfq.py:167-176`；weekly/monthly 无补列 DDL | ⚑-5 的 DDL 项描述升级为"读写侧已在，缺的是**族级版本列**"（比"补两列"更准确，也说明这不再是新设计而是收尾） |




## §四 证据分级制（本案卷群自评，防"把案卷当裁定、把叙述当证据"）

| 级 | 定义 | 例 |
|---|---|---|
| **E1 直读** | 命令可复跑、口径写明（文件:行号 / 表+库+时间窗 / `git show HEAD:` 计数） | X-01、X-08、X-13、X-40 |
| **E2 工具自述** | 依赖某工具/门的内部读数，未独立复算 | `gate_prerun` 报的 99 台（已由进程内实调佐证 ⇒ 升 E1） |
| **E3 盘上单一来源** | 只有一处盘面证据，无第二方 | X-18（备份 mtime）、X-19（PID 表） |
| **E4 交接书转述** | 只有叙述，盘面拿不到 | 旧"VERDICT_RED"、"132 定档"、"469→728"、"11 册 quant_methodology" ⇒ **一律禁用作施工依据** |
> 用 `ch_writer.query` 取来的读数（异常返回 `""`）不论如何都**降一级**（X-27）。凡"某物不存在"的判定，必须附**带限定的第二探测**（X-26）。

## §六 红队回流（对抗测试后的处置：X-59..X-66）

> 两路独立红队攻击本班产出（RT1＝命令可执行性/危险动作；RT2＝覆盖率/裁定越界）。**红队每条 P0 我都二次复验**——两路都含假 P0。教训写死：**红队结论也不自证，照抄红队＝新的单点故障**。

| # | 事实 | 处置 |
|---|---|---|
| X-59 | RT1 命中真缺陷 9 条：一键册曾引用 5 个只存在于 `.runtime/tmp`（受 24h TTL）的一次性脚本；`<129 个 tests/ 子目录>` 是假数（实测"含 `test_*.py` 的目录"＝**258**）；`gate_prerun` 要求 message-file **实存**否则直接 FAIL；`commit_queue status` 的 stdout **尾部混一行 `ALERT:{...}`** 令 `json.load` 崩；复核命令写了不存在的模块路径；把脚本输出标签写错（实际打印 `missing=N disk_only=M`） | 已全部改入 91/94/11 册；波 7 的目录枚举改成**自含 find 命令**，并把"比尺寸会漏判等长改动"写进 94 |
| X-60 | **驳回 RT1 假 P0 三条**：①"`--session` 可选/`--adopt-prior-work` 不存在"——`git_commit.py --help` 实测列出 `--session/--files/--enqueue/--allow-non-worktree/--allow-multi-domain/--adopt-prior-work/--no-auto-enqueue/--claim-only/--release-only`（只确无 `--base-head`，那条它说对了）；②"`lane_ff_mine` 不存在"——实存（`.aidrafts/lane_ff_*` 共 10 个）；③"`status --session` 不是 JSON"——stdout 首字节即 `{\r\n"queue_root"`，崩因在**尾部** | 驳回项写死在此，防下一班被红队报告二次误导 |
| X-61 | 实盘合规门"零接线"经**逐闸**反查成立但表述要换：`programmatic_trading_guard`、`regulatory_report_generator` 的非自身引用文件数＝**0**；`manipulation_realtime_monitor` 仅被 `order_manager.py:81` 以 **TYPE_CHECKING 预接线**引用；`compliance_rule_engine` 引用文件数＝1 | ⚑-1 第①项从"12 闸零接线"改**逐闸口径**；新增 **W-140**＝先出"逐闸接线表＋零消费者清单"再据表定序，禁一句"零接线"打包 |
| X-62 | RT2 判"C3 盘后结算双入口分叉不成立"（两区 `run_post_settlement_daily.ps1` 都在） | 本班未能独立复验（`schtasks /query /v` 输出 GBK 化，取不到 ACTION 原文）⇒ ⚑-1 第②项**降为待复验**，新增 **W-141**＝用 `schtasks /query /tn <task> /xml` 取原文；若确为单入口则**撤销该项呈裁** |
| X-63 | RT2 的 12 条"越界"里成立两条：①被他道禁用的门**不得自裁恢复**；②判定书是否入版本控制其实**已有在册裁定覆盖** | ①改判为"只登记零触发归因案卷，不判恢复也不判保持关闭"；②从"我的安全默认"改标"**已裁事项的执行核对项**"，不再当待裁默认条呈现 |
| X-64 | 波2 役 12 项已批项的映射覆盖不足（E/F/G/H/I/J/K/L/M/O 十项无 W 位） | 新增 **W-142..W-151** 逐项映射；并把"逐件映射表"设为波 2.2 的**出口判据**（无表不算完成） |
| X-65 | 真漏 11 类：HMAC 立项文档、红蓝场景⑦、四向对账表、负结果台账落点、孤儿件治理、28 处硬编码引用改道、13 条代裁追认单、15 门 P4 标注、T14 十七条、L18 六册口径互斥、arbiter ④⑥ 项 | 全部成立 → 入 **波 9**（见 `10_wave_plan.md`），编号 W-152..W-162 |
| X-66 | RT2 两条不实：①"图12/13 校验器 `--map` 必死"——本班在该道 `PYTHONPATH` 自证后实跑 **rc=0**；②"上岗规则 v1／图形技术库／CNS／退役重考全缺"——四件在 `00` 册有 W-116..W-119，只是未进波次表 | ①驳回；②改判为"**编目有、排产无**"→ 波 9 显式排产 |

### 结构性结论（红队教给我的）

**我的覆盖体系是"编目完整、排产有洞"**：`00` 册能收进绝大多数环节，但 `10` 册波次表只排了约一半——而 **Flash 只照 `91/10` 动手**。⇒ 已补波 9，并在 `92` 册新增 **G-70**：任何 W-xx 若在波次表无归位，施工队必须停下先登记"未排产"再继续（把"编目≠排产"变成可检出的尺）。

## §七 波 0 由本班代做后的实测结果（15:42 固化，非计划）

- 固化范围：`.aidrafts/*` 与 `.worktrees/*` 共 **76 条车道**，凡有脏项者逐道落 `status.txt / tracked_stat.txt / tracked_names.txt / worktree_vs_HEAD.patch / index_vs_HEAD.patch / untracked_manifest.json / churn_lines.txt / untracked 副本`。
- 体量：本地 `.runtime/tmp/total_command_closeout/lane_rescue/`（约 140MB，含两轮）；**冷库镜像 `G:\zephyr_cold\30_corpus\zmaster_lane_rescue_0926` 文件数 673 == 本地 673**（已双向核）。
- **硬结论（这条改变优先级判断）**：**25 条车道 dirty 数百项而自有 commit 数＝0**，含 `.aidrafts/lane_ff_*` 全部 10 条、`st-mapbuild-20260924`、`st-audit-fix-20260924`、`st-qmine-20260925`、`.worktrees/st-ailayer-final-20260924`（dirty **169**、untracked 0、ahead 0、补丁 2031KB）、`st-wm1-buildA`（230）、`st-combine-2023`（235）、`st-t0-matrix-2024`（254，ahead 4）。
  ⇒ 这些道**一次 `git checkout`/reconciler 还原就全丢**，且丢后无人知道丢了什么。现补丁＋清单已双存，波 2 落地按表逐道销号。
- 附带读数（会漂移，引用带时刻）：`worktree_changes=460`、staged 删除 141、`commit_pct` 56.72%、ram_used 55.6%。
- 工具坑（写进 R-6 族）：把该固化脚本用 `run_in_background` 跑时，**日志与报告全空但退出码 0**（孵化/会话生命周期把子进程收了，stdout 缓冲未落）；改前台 `python -u` 才拿到完整报告 ⇒ **长任务"exit 0"不等于跑完，必须验产出文件实存**。
