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
| 8 | M2 候选 A 见证层并案出厂（含候选 C） | M2 §10.1 | 登记跳过（Q 线只做 W17 补填与预检封旁路的代码准备，出厂 flag 归 Owner） |
| 9 | requires-sync"宁停勿吃"适用交互正门 | M2 §10.2 | 登记跳过 |
| 10 | --base-head 契约二选一 | M2 §10.3 | 登记跳过（代码按"补 base_blobs"准备，flag 默认不启用） |
| 11 | [GW:] 归属去文本化 | M2 §10.4 | 登记跳过 |
| 12 | gate_registry 174≠180 归位+自洽台双锚 | M2 §10.5 | 登记跳过 |
| 13 | single-writer 检测器提为 reconciler | M2 §10.6 | 登记跳过 |
| 14 | commit_queue_interactive 出厂翻转 | M1 O-1 | 登记跳过 |
| 15 | 预检原则改册净零声明 | M1 O-2 | 登记跳过（随施工批呈） |
| 16 | 热册三向合并策略变更 | M1 O-3 | 登记跳过 |
| 17 | M5 三件：四停用定性/三悬空方向/43 红样排期 | M5 §8 | 登记跳过（43 红样采集若日班带宽许可由矿道卷登记） |
| 18 | 挖矿新发现门位项 | W1 产出 | 待追加 |
| 19 | etf_benchmark 数据源_stub 重写：`akshare_provider._fetch_etf_benchmark` 现为恒空 yield（rows=[] 永远 0 行=SUCCESS 假绿），且实调 `index_stock_info(symbol="000300")` 与 tasks.yaml 声明 `fund_etf_fund_info_em` 不符；修复须实弹验证 akshare 通道后选定真源接口重写（date_col: publish_date 已修，P3） | P 线 census :106 | 登记跳过（禁实弹） |
| 20 | realtime_snapshot 换源决策+suspend 双源反爬持续性观察：112 个降级件（08-26~09-21）全数 realtime_snapshot_incremental，错误=`Can not decode value starting with character '<'`（新浪 stock_zh_a_spot 反爬返 HTML；原东财源因 #ARCH-AKSHARE-ANTICRAWLER-001 IP 封锁弃用）——换源三候选（东财冷却复用/腾讯源/qmt_bridge）选定与验证须实弹；suspend 三腿 census 时点 0 行=东财 stop_em+百度双源反爬暂态（09-27 复测 36 行 max=09-23），持续观察归哨兵（P4 修后尺不再被骗） | P 线只读诊断（lane_p_notes.md §P5） | 登记跳过（禁实弹） |
| 21 | F85 `src/zephyr/trading/windows_service.py` 退役候选（净删=Owner 门位，本道未动一字）：复核确证零运行时消费者——HEAD 内仅 4 处非消费提及（trading/__init__.py:45 与 speed_baseline_checker.py:43 为字符串清单字面量、process_supervisor.py:22/runtime_config.py:5 为注释头）；本机 SCM 服务未装（sc query ZephyrAlpha→1060），开机链实归 ZephyrAlpha_* 计划任务群+桌面壳自启动（.lnk 在盘）；其 install_service() 若接线=再装一个包装 AutoRuntimeCore 的竞争启动脑，触实盘四禁与生产流转，禁本道擅动。判据依据：宪法 §4.2 零触发零消费→退役；如 Owner 判留，应补运维手册引用面并定性"手动 boot 入口"（F112 同族豁免） | st-c7-wire-20260927 接线复核 | 登记退役候选（待裁） |
| 22 | F85 `scripts/register_desktop_shell_startup.ps1` 定性=已接线（入口即角色，F112/F118 同族豁免，勿再入死件账）：产品态实测在盘——用户 Startup 目录 "ZephyrAlpha Dashboard.lnk" 存在（09-27 ls 验证），用户登录自动触发，拉起 Electron 壳→api_server 8890+serve_docs 8765；本道不改不动 | st-c7-wire-20260927 接线复核 | 更正定性（无需动作） |
| 23 | F89 拆分定性：(a) 三张卡 embedding_router/local_model_scheduler/ollama_chat.yaml=已接线（尺假阳性）：真实消费者 src/zephyr/trading/auto_runtime_core.py:135 `CapabilityRegistry(config.capability_card_dir)`，供数=runtime_config.py:126/142 实时读 capability_card_dir，触发=AutoRuntimeCore 启动序 lifecycle_manager.py:116 步骤 04_registry_load→capability_registry.load_from_dir() 全目录 yaml 装载；dir4 尺漏判因路径为动态参数非字面量。(b) `scripts/governance/meta/mutation_test_reconciliation_registry.py`=半接线且当前坏：SSoT 路径漂移（:84 指向 src/zephyr/governance/reconciliation_registry.py，真源在 governance/audit/ 子目录，从零跑实测 `[FATAL] SSoT 真源不存在` 退出）；分发面仅 scripts/governance/run_all.py manifest（D1/Quick 在册），但 run_all 无自动触发者——.github/workflows/governance.yml:327 调 `run_all.py --ci` 而 run_all argparse 无 --ci 旗（CI 面为名义存在）；模块头自带契约"GATE-MUT 达标后事件驱动"而 GATE-MUT 册查无。请裁：①一行修 :84 路径（修复配方本道已备未动码）；②GATE-MUT 事件面立项或整族（含 mutation_test_post_sync_validator）退役——净删=Owner | st-c7-wire-20260927 接线复核 | 登记待裁（(b) 项） |
| 24 | F83/F97 六向尺校准项（doc-only 环节被 decl-path 粒度假判"实现无消费者"）：F83 dir3 命中两件皆为政策册（sop/automation_sop/automation_crew_policy.md、_working/cmd_ledger/automation_master_plan.md），F97 dir3 命中 commit_speedup_campaign/00_skeleton/ 三册（总册 K 段明示引用态不重挖）；HEAD 内两环境零代码文件，"接线/退役"二选一在代码面不成立——政策册消费者=班次与桥册（02_f83 案卷§三"册面已接线/执行面借道 F76/F82"，F97 案卷§三"被引真源三件在盘可达"）。禁按死代码退役政策册；建议六向尺对 doc 粒度环节改判 N/A 而非记缺口 | st-c7-wire-20260927 接线复核 | 登记更正（无需动码） |

（追加规则：矿道/施工线报来"涉生产流转/净删/flag/资金"项一律入此表并回填 91_progress。）
