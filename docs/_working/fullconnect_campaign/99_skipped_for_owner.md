---
ttl: task_bound
title: "Owner 门位登记台账（宪法 §5 high 域，只登记不代裁）"
session: zc-chief-20260927
---

# Owner 门位登记（99_skipped_for_owner）

> Owner 令"不留待裁"与宪法 §5 冲突，依裁-03 全部登记跳过。本台账随战役推进追加。

| # | 事项 | 来源 | 状态 |
|---|---|---|---|
| 1 | DDL：kline_weekly_hfq/kline_monthly_hfq 补 lineage_version | M3 §8.1 | 登记跳过 |
| 2 | 空壳表 9 张建腿 vs 退役（含 l2_tick） | M3 §8.2 | 登记跳过 |
| 3 | 真源收敛三处（recon/consensus/news_sentiment_score） | M3 §8.3 | 登记跳过 |
| 4 | Ollama 11434 恢复（重启提案封矿） | M3 C12 | 登记跳过 |
| 5 | heartbeat 计划任务兜底 | M4 C6 | 登记跳过 |
| 6 | 门禁 diff 化批门位确认+恒绿贵门处置窗 | M4 C3/C5/C9 | 登记跳过 |
| 7 | dead 系 2397 件归档净删 | M4 §11.4 | 登记跳过 |
| 8 | M2 候选 A 见证层并案出厂（含候选 C） | M2 §10.1 | 登记跳过（Q 线只做 W17 补填与预检封旁路的代码准备，出厂 flag 归 Owner）→[Owner 2026-09-30 夜批]批（翻转发令面随 flag 轮转窗执行） |
| 9 | requires-sync"宁停勿吃"适用交互正门 | M2 §10.2 | 登记跳过 |
| 10 | --base-head 契约二选一 | M2 §10.3 | 登记跳过（代码按"补 base_blobs"准备，flag 默认不启用） |
| 11 | [GW:] 归属去文本化 | M2 §10.4 | 登记跳过 |
| 12 | gate_registry 174≠180 归位+自洽台双锚 | M2 §10.5 | 登记跳过 |
| 13 | single-writer 检测器提为 reconciler | M2 §10.6 | 登记跳过 |
| 14 | commit_queue_interactive 出厂翻转 | M1 O-1 | 登记跳过→[Owner 2026-09-30 夜批]E10 归口：维持默认不翻转 |
| 15 | 预检原则改册净零声明 | M1 O-2 | 登记跳过（随施工批呈） |
| 16 | 热册三向合并策略变更 | M1 O-3 | 登记跳过 |
| 17 | M5 三件：四停用定性/三悬空方向/43 红样排期 | M5 §8 | 登记跳过（43 红样采集若日班带宽许可由矿道卷登记） |
| 18 | 挖矿新发现门位项 | W1 产出 | 待追加 |
| 19 | etf_benchmark 数据源_stub 重写：`akshare_provider._fetch_etf_benchmark` 现为恒空 yield（rows=[] 永远 0 行=SUCCESS 假绿），且实调 `index_stock_info(symbol="000300")` 与 tasks.yaml 声明 `fund_etf_fund_info_em` 不符；修复须实弹验证 akshare 通道后选定真源接口重写（date_col: publish_date 已修，P3） | P 线 census :106 | 登记跳过（禁实弹） →[Owner 2026-09-30 夜批]zc9 已落销账（3c01517bb2 index_csindex_all 重写+tasks.yaml 声明修正，833af2d022 同窗） |
| 20 | realtime_snapshot 换源决策+suspend 双源反爬持续性观察：112 个降级件（08-26~09-21）全数 realtime_snapshot_incremental，错误=`Can not decode value starting with character '<'`（新浪 stock_zh_a_spot 反爬返 HTML；原东财源因 #ARCH-AKSHARE-ANTICRAWLER-001 IP 封锁弃用）——换源三候选（东财冷却复用/腾讯源/qmt_bridge）选定与验证须实弹；suspend 三腿 census 时点 0 行=东财 stop_em+百度双源反爬暂态（09-27 复测 36 行 max=09-23），持续观察归哨兵（P4 修后尺不再被骗） | P 线只读诊断（lane_p_notes.md §P5） | 登记跳过（禁实弹） →[Owner 2026-09-30 夜批]zc9 已落销账（8479b8b7ce 换源腾讯 qt.gtimg 批量直连） |
| 21 | F34 L9 聚合器收尾三步（DDL --apply+首跑+pf_alloc 消费）涉生产 DDL | 00_workorders §五（09-27 合入，09-28 补登） | 登记跳过（Owner 门） →[Owner 2026-09-30 夜批]已落（L9 消费接线 082d4591e79+833af2d0220 在 HEAD；DDL --apply 残腿归 C41 销账复核留痕） |
| 22 | F88 usercustomize 运行时网启用（本战役只做仓内安全子集=no usercustomize） | 00_workorders §五（09-27 合入，09-28 补登） | 登记跳过 |
| 23 | F76 schtasks 写操作与 N/A 清理（计划任务注册/变更=任务级 Owner） | 00_workorders §五（09-27 合入，09-28 补登） | 登记跳过 |
| 24 | F68 T1 判卷三阻断处置 | 00_workorders §五（09-27 合入，09-28 补登） | 登记跳过 |
| 25 | F51 币圈空壳去留 | 00_workorders §五（09-27 合入，09-28 补登） | 登记跳过 →[Owner 2026-09-30 夜批]批退役（执行窗遵同日币圈专项挂起令 st-finaldel-crypto-20260930：物理净删待 Owner 通知窗，先归档后删不代执行） |
| 26 | F111 宪法入口三方冲突 | 00_workorders §五（09-27 合入，09-28 补登） | 登记跳过 |
| 27 | F119 双引擎真源二选一（10-08 继任窗） | 00_workorders §五（09-27 合入，09-28 补登） | 登记跳过 |
| 28 | F120/F121/F122 收编与边界三裁 | 00_workorders §五（09-27 合入，09-28 补登） | 登记跳过 |
| 29 | F56 TRD-A10 Owner-gate 半腿：沙箱 v16→v17 换版重启／实盘 env=real 兜底启用／30 交易日零静默丢弃验收窗／缺陷②撤单暂缓窗撞 sim cancel_order 在册契约待协调（376105ce64 提交信息声明登记本行而 diff 实误删旧 #21-25，本行补登） | st-c7-f56-20260927 提交信息（09-28 补登） | 登记跳过（仅登记不代裁） →[Owner 2026-09-30 夜批]A2 归口：沙箱窗 v16→v17 换版批；实盘 env=real 兜底启用等人工通知 |
| 30 | 1A.5 0 字节死库 data/zalpha_metadata.db 真删（净删=Owner 门；trae_034:40/212/560 点名空壳；6d0be14e4c 已落死指针尺与 fail-closed 预检） | 1A.5 车道（09-28） | 登记待裁 |
| 31 | 1A.5 ADR-KB DIM-3 决策（HEAD 暂无留档面，待 1A.5 案卷落地挂锚） | 总筹分道令（09-28） | 登记待裁 |
| 32 | 1A.5 FMS 棘轮盲区处置 | 总筹分道令（09-28） | 登记待裁 |
| 33 | 1A.5 construction_workflow_policy.md:388 让位（该行现指 data/zalpha_metadata.db 死库，trae_034 落地时须让位改指活库） | 1A.5 车道（09-28） | 登记待裁 |
| 34 | 裁-13 decision_timestamp 增列（15→16 字段）：E8E9 袋 a349ddc1fe 已随袋留痕，正式注册待正册通道空闲（ruling_registry 今夜 chiefzc-docsB3 在落 #415-417，避让不碰正册） | lane-gov3（09-28） | 登记待正式注册 →[Owner 2026-09-30 夜批]D2 已落销账（nightclean 3f75191285 FLD-EXEC-011 decision_timestamp 已入 field_dictionary 正式注册） |
| 35 | trae_034_task_card_standard.yaml 三处死指针（改指 data/databases/governance.db）：PROTECTED-PATHS 拦截待裁定通道；关联代码件已落 6d0be14e4c（死指针尺 2 例待 trae_034 落地转绿） | lane-dbr defer-2（09-28） | 登记待裁定通道；终局注记（2026-09-29）：指针已改 governance.db（1cf01067f5+7f9de37b2a），真删仍待 Owner →[Owner 2026-09-30 夜批]销账（指针改指 governance.db 1cf01067f5+7f9de37b2a 终局注记成立，真删残面归退役批） |
| 36 | F56 内核 defer 三选一处方：B7 78982c4c81 已取代袋版适配器（自含 phantom_grace_s/cancel_hold_s+18 测超集），kernel bridge_instruction_kernel.py 仓内零消费者=ORPHAN-MODULE 硬拦无逃生；a/B7 判定核心改委托 kernel／b/Owner 裁 ORPHAN 例外面／c/沙箱写侧进仓携带真实消费边（处方全文=.runtime/tmp/st-zchief8-20260928/defers/lane-dbr.md defer-1） | lane-dbr defer-1（09-28） | 登记缓议（归 Owner/TRD-A10 归属线）；终局注记（2026-09-29）：选 c 墓碑已落地（edf0788dfb 墓碑收编+dd3b17f9fd 断腿重建），Owner 无需再裁 →[Owner 2026-09-30 夜批]B13 已销（选 c 墓碑 edf0788dfb+dd3b17f9fd 终局注记成立，Owner 无需再裁） |
| 37 | F85 `src/zephyr/trading/windows_service.py` 退役候选（净删=Owner 门位，本道未动一字）：复核确证零运行时消费者——HEAD 内仅 4 处非消费提及（trading/__init__.py:45 与 speed_baseline_checker.py:43 为字符串清单字面量、process_supervisor.py:22/runtime_config.py:5 为注释头）；本机 SCM 服务未装（sc query ZephyrAlpha→1060），开机链实归 ZephyrAlpha_* 计划任务群+桌面壳自启动（.lnk 在盘）；其 install_service() 若接线=再装一个包装 AutoRuntimeCore 的竞争启动脑，触实盘四禁与生产流转，禁本道擅动。判据依据：宪法 §4.2 零触发零消费→退役；如 Owner 判留，应补运维手册引用面并定性"手动 boot 入口"（F112 同族豁免） | st-c7-wire-20260927 接线复核；原#21（376105ce64 误删，09-28 回复） | 登记退役候选（待裁） |
| 38 | F85 `scripts/register_desktop_shell_startup.ps1` 定性=已接线（入口即角色，F112/F118 同族豁免，勿再入死件账）：产品态实测在盘——用户 Startup 目录 "ZephyrAlpha Dashboard.lnk" 存在（09-27 ls 验证），用户登录自动触发，拉起 Electron 壳→api_server 8890+serve_docs 8765；本道不改不动 | st-c7-wire-20260927 接线复核；原#22（376105ce64 误删，09-28 回复） | 更正定性（无需动作） |
| 39 | F89 拆分定性：(a) 三张卡 embedding_router/local_model_scheduler/ollama_chat.yaml=已接线（尺假阳性）：真实消费者 src/zephyr/trading/auto_runtime_core.py:135 `CapabilityRegistry(config.capability_card_dir)`，供数=runtime_config.py:126/142 实时读 capability_card_dir，触发=AutoRuntimeCore 启动序 lifecycle_manager.py:116 步骤 04_registry_load→capability_registry.load_from_dir() 全目录 yaml 装载；dir4 尺漏判因路径为动态参数非字面量。(b) `scripts/governance/meta/mutation_test_reconciliation_registry.py`=半接线且当前坏：SSoT 路径漂移（:84 指向 src/zephyr/governance/reconciliation_registry.py，真源在 governance/audit/ 子目录，从零跑实测 `[FATAL] SSoT 真源不存在` 退出）；分发面仅 scripts/governance/run_all.py manifest（D1/Quick 在册），但 run_all 无自动触发者——.github/workflows/governance.yml:327 调 `run_all.py --ci` 而 run_all argparse 无 --ci 旗（CI 面为名义存在）；模块头自带契约"GATE-MUT 达标后事件驱动"而 GATE-MUT 册查无。请裁：①一行修 :84 路径（修复配方本道已备未动码）；②GATE-MUT 事件面立项或整族（含 mutation_test_post_sync_validator）退役——净删=Owner | st-c7-wire-20260927 接线复核；原#23（376105ce64 误删，09-28 回复） | 登记待裁（(b) 项） |
| 40 | F83/F97 六向尺校准项（doc-only 环节被 decl-path 粒度假判"实现无消费者"）：F83 dir3 命中两件皆为政策册（sop/automation_sop/automation_crew_policy.md、_working/cmd_ledger/automation_master_plan.md），F97 dir3 命中 commit_speedup_campaign/00_skeleton/ 三册（总册 K 段明示引用态不重挖）；HEAD 内两环境零代码文件，"接线/退役"二选一在代码面不成立——政策册消费者=班次与桥册（02_f83 案卷§三"册面已接线/执行面借道 F76/F82"，F97 案卷§三"被引真源三件在盘可达"）。禁按死代码退役政策册；建议六向尺对 doc 粒度环节改判 N/A 而非记缺口 | st-c7-wire-20260927 接线复核；原#24（376105ce64 误删，09-28 回复） | 登记更正（无需动码） |
| 41 | F132 ConfigCheck 计划任务三件待裁（自动化假绿战役 st-c7-autofix-20260927 当班实测；读取腿已治本入 deadman_switch.ps1 config_effect 段+配对测试 tests/governance/test_deadman_config_effect_alert.py）：①任务级 action 变更（pythonw→python、exit-1 后挂动作）=计划任务注册/变更类=Owner 门位，本道只实测不改——Get-ScheduledTaskInfo 读数 LastTaskResult=1 @09-27 08:05，ACTION=pythonw -m zephyr.infra_ops.config_effect_checker；②scheduled_task_reconcile.py（三色对账，ConfigCheck 判红尺）宿主任务挂靠=任务级动作=Owner（其头 CONSUMERS 本注『挂靠待 Owner』，本道不新注任务）；③日红根因=schedule.yaml/tasks.yaml 无 reload 路径而热更新本体已裁搁置（config_effect_checker 头记 2026-09-17 Owner 裁定），磁盘漂移在下次调度器重启前必日红，安全窗重启=运维动作非本道判决；09-27 现状实测：11:10 调度器重启后 checker exit 0 回绿 | st-c7-autofix-20260927 实测；原#25（376105ce64 误删，09-28 回复） | 登记待裁（三项均任务级/运维） |

（追加规则：矿道/施工线报来"涉生产流转/净删/flag/资金"项一律入此表并回填 91_progress。）
| 42 | F127 `src/zephyr/data_eng/` 全包（9 实体件+7 骨架空层）物理净删候选+冷储双实现收敛方向：依 16_f127 案卷定罪生产面零 import（AST PROD=0）、零触发、头注三条假声明（[MATURITY] production/[STARTUP] imported/[CONSUMERS] 挂 auto_archive 均与实盘相反）；`cold_data_archive_manager.py` 与现役 F08 `scripts/ch/archiver.py`（920 行四命令，F:/zephyr_cold 链）构成并行第二实现/潜在第二索引真源。已落 [DEPRECATED]+successor 注记于包 __init__（376105ce64 语义沿例，只标记未删）；请裁：①保 F08 删本包／②本包取代 F08／③保留待接线（则按 F127 缺1 逐件红样） | SW5 夜战（st-nightsweep-sw5-20260929，09-29） | 登记净删候选（待裁） |
| 43 | F128 `src/zephyr/data_security/` 三件（data_masking_engine/data_access_auditor/ai_masking_pipeline）物理净删或补接线二选一：依 12_f128 案卷定罪纯装饰（AST PROD=0 且无 TYPE_CHECKING 腿、零动态挂载、零计划任务；M1 SourceType 消费腿=同名假阳性，l1_input 自有枚举）；与 F88 LSG/F105 密钥经实核异域不并，故无现成继任——若净删则列级脱敏/访问审计能力空缺须 known-gap 登记兜底。已落 [DEPRECATED]+successor 注记于包 __init__（只标记未删）；请裁：①净删+空缺登记／②按缺1 定接入点（数据出口+LSG l1_input 前置）红样后接线 | SW5 夜战（st-nightsweep-sw5-20260929，09-29） | 登记净删候选（待裁） |
| 44 | F130 `src/zephyr/ml_serve/` 四件物理净删候选+model_drift_monitor 双同名 clone 判定：依 13_f130 案卷定罪纯装饰（AST PROD=0/TC=0、无反射装配、唯一文本命中在 _archive/）；serve 层现役=F129 ml_train（default_inference_engine 被 intelligence/model_evaluation 实消费），本包=并行未启用第二实现族。已落 [DEPRECATED]+successor 注记于包 __init__（只标记未删）；另 `model_drift_monitor.py` 双份并存（gov_drift 68 行 vs ml_serve 269 行，运维地图 :409/:727 各一条）请裁 clone_guard 判定归属——clone 定性与净删均涉注册表净删=Owner 门位 | SW5 夜战（st-nightsweep-sw5-20260929，09-29） | 登记净删候选+clone 判定（待裁） →**已执行（2026-09-30 st-finaldel-retire，Owner 批先归档后删）**：净删面勘误 TC=0→实为 4 tests 在册实消费，净删=4 src+4 tests=8 件；8 件 sha256 归档 G:/zephyr_cold/retire_c267_20260930/F130_ml_serve/ 后 git rm；ml_serve 侧 model_drift_monitor 归档留证、gov_drift 68 行侧存活=clone 双同名事实消解；登记面 5 册 dangling 清理移交维护班 |
| 45 | F62 SettlementReconciler 违宪整改收尾：事件触发腿已落（post_settlement_pipeline subscribe_eventbus+run_daily_end_sweep 幂等日终去重+register_sweep_deps 装配口+boot_hooks 消费方挂载，14 测试绿含事件注入触发一次+幂等重放零副作用）；**ZephyrAlpha_PostSettlement 计划任务（-Weekly Mon-Fri 15:30 时钟触发，宪法 §9.3 禁 cron/Timer）退役=schtasks 任务级变更=Owner 门位**（#23 同类先例）——过渡期时钟腿与事件腿并存安全（CLI 幂等+sweep 进程内去重双保险）；退役动作=unregister 计划任务或保留只读观察，请裁；另 boot_hooks 消费方装配需 AutoRuntime 重启生效（运维窗） | SW5 夜战（st-nightsweep-sw5-20260929，09-29） | 登记任务退役（待裁） |
