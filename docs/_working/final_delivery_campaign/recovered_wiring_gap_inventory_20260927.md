---
created: 2026-09-27
asset_id: "DOC:docs/_working/final_delivery_campaign/recovered_wiring_gap_inventory_20260927.md"
ttl: "task_bound"
title: "未接线总清单与待处理行动清单（2026-09-27 实测汇编）"
session: st-finaldel-cdead-20260929
recovered_from: "DOC:docs/_working/wiring_gap_inventory_20260927.md"
recovered_blob_sha256: "75549c3400f807b739a85ff3c11d175f5ea2e18d6f4d4de189d2ac6b4d967785"
recovered_at: "2026-09-29"
completes_when: "Owner 消费完本清单并裁定各门位事项后归档"
---
> **捞回件，原载体蒸发，时效判定：仍是活账（2026-09-29 复测）**。原 `docs/_working/wiring_gap_inventory_20260927.md`（编制会话 zcode-wiring-inv-20260927，2026-09-27）从未入 git 历史；字节由 commit_queue blob 库残骸捞回（sha256 见 recovered_blob_sha256，字节完整自洽）。复测证据：①总册四态 built81/partial30/design5/missing6 与本文 §1.4 完全一致；②TDM `module_ref: null` 实测 37（本文记 38，仅闭合 1）；③HEAD 现存 ≥9 处引用原路径悬空（capability_canonical_file_registry.yaml、final_delivery_campaign 工单族、fullconnect_campaign HANDOFF/90_rulings、night_sweep/00_skeleton_nightsweep.md 等）。asset_id 已换绑本路径，正文原样未动。捞回车道＝st-finaldel-cdead-20260929。


# 未接线总清单与待处理行动清单（2026-09-27 实测汇编）

- 编制：zcode 会话（Owner 问"图书馆查出来没接管线的有多少"的完整盘点交付件）
- 汇编源：63 号数据利用审计 CSV｜90 交叉验证普查｜00_全环节总册（本日复数）｜TDM 地图（本日复数）｜M5 接线普查机判产物｜chain_fullflow_20260926 五案卷+收口卷（行动项已逐卷榨取）｜本会话新发现
- 原则：每条带锚点；机判名单注明生成物；所有数字当日实测可复跑（§三）

---

## 一、没接线的（按层，四层判据）

### 1.1 数据表层：59/106 张零引用（63 号审计，docs/_audit/data_utilization_audit_2026-08-24.csv）

分母 106 = covered 40 / **zero_ref 59** / code_only 7。零引用全名单（按族）：

| 族 | 张数 | 成员 |
|---|---|---|
| factor.ashare_* | 14 | alpha87, capital_flow, cross_market, fundamental, institutional, intraday, irl, market_structure, microstructure, pattern_signal, ps_liquidity, sector, smc, technical_indicator |
| backtest *_result | 8 | anomaly_diagnoser, data_quality_checker, decay_monitor, nan_processor, param_analyzer, report_generator, result_comparator, result_deployer |
| fundamental | 5 | daily_basic, fin_income, fin_balancesheet, fin_cashflow, fin_indicator |
| event | 5 | disclosure_date, fin_forecast, fin_express, share_float, holder_trade |
| data_eng | 5 | data_lake_manager, knowledge_cleaning, stream_processing, synthetic_data, training_data_manager |
| market_data | 5 | ohlc_bar, renko, point_figure, kagi, lhb_detail |
| factor.barra_* | 4 | esg, exposure_calculator, risk_budget_allocator, risk_model |
| factor 其他 | 3 | turnover_analyzer(factor_analysis), causal_validator, mining_agent(factor_mining) |
| data | 3 | feature_store, realtime_push_manager, tick_data_manager |
| ml | 2 | ai_operator_decisions, training_dataset |
| 宏观/行业 | 2 | macro.cn_macro, industry.sw_daily（整域零） |
| 单张 | 3 | portfolio.portfolio_aggregate, risk.drawdown_metric, meta.st_status |

### 1.2 业务代码域：13 个顶层域在 122 环节骨架无落位（90 普查 §三·D）

alt_data(P1)、data_eng(P1)、**data_governance(P0)**、data_security(P1)、market_data(P1 双真源嫌疑)、ml_train(P1)、ml_serve(P1)、nlp(P2)、intelligence(P2)、knowledge(待裁)、infra_ops(P1)、infra_runtime(待裁)、gov_rule(P2)。
另有环节内缺口 2 条：L02 大盘情绪（已定桩独立状态变量，总册未落位）、L04 板块→个股传导（跨 F39/F40 无线）。

### 1.3 ROOR 注册表：15 项无环节落位（90 普查 §三·B）

B-1 技术指标册(P1)、B-2 图表形态册(P2)、B-3 执行算法册(P2)、B-4 席位册(P1)、B-5 事件日历册(P1)、B-6 宏观指标册(P1)、B-7 字段字典(P1)、B-8 数据资产册(P1)、**B-9 迁移册(P0)**、B-10 架构问题册(P1)、B-11 接口契约册(P1)、**B-12 状态词表册(P0，GATE-VOCAB 真在拦却无环节)**、B-13 任务卡元数据册(P1)、B-14 模板/头册/脚本族(P2)、B-15 跨模块依赖/master_index/状态机册(P2)。
另有登记面欠账 40 项（环节在、册内未点 REG 号，机检不可达）。

### 1.4 全流通环节层：41/122 未完全接线（总册本日复数：built 81 / partial 30 / design 5 / missing 6）

| 态 | F 号（名） |
|---|---|
| **missing 6** | F26 E7 模拟盘前哨(P0)｜F30 L9 行情基本面族｜F31 L9 另类数据族｜F34 L9 知识汇聚(P0)｜F51 币圈骨架｜F74 转正建议书汇总器（**全流通最大单点**） |
| **design 5** | F73 A/B 联赛与分仓（晋升判据执行器未写）｜F94 AI 七段循环设计面｜F95 OBJ 四对象线（31 项待 Owner）｜F120 业务层四轴+底板（工单队列在案）｜F121 研究性三域（M0 待裁挂起） |
| **partial 30** | F02 数据源接入（流水线串接=工段③最大空地）｜F04 清洗校验（**清洗三引擎零接线**）｜F13 E0 算力心跳｜F14 E1 想法进货（待 E1C）｜F16 车道B AI 生成｜F17 车道C 公式挖掘｜F18 车道D 产业链三高（LLM 增补未建）｜F19 车道E 模型基线｜F20 车道G 全网搜索（事件接线未挂）｜F21 E2 假说预审｜F22 E3 构造翻译｜F27 E8 组装资金分配（sleeve/TDM 未闭环）｜F28 E9 实盘归因（IS FIELD-GAP/影子组合未建）｜F29 进货台账｜F32 L9 图谱谱系｜F33 L9 状态快照｜F35 L9 一问一考（D2/E2 null）｜F36 L9 治理横切｜F58 执行成本反馈｜F72 模拟盘日跑四件（SimBridge 静默断链嫌疑）｜F75 策略生命周期状态机｜F82 订单结算常驻｜F84 反馈循环 FBL｜F85 环境启动链｜F86 AI 六族管线（DDL 未部署）｜F87 AI 红线｜F92 原问题账本（**entry_count=0 空转**）｜F96 胃·全网消化（v0 待升 AI 层）｜F115 报告生成｜F122 管线路由（M4/M5 边界待裁） |

### 1.5 TDM 节点层：38 个 `module_ref: null`（全部 L9 源线族，本日 awk 复数）

TDM-E-L9-A01..A16＋AGG（17）｜B01..B10（10）｜C01..C03（3）｜D2、E2、G1、G2、G4、G5、V2、Z1（8）。

### 1.6 门禁/守护面（M5 接线普查，治理面非业务；机判产物 `.runtime/tmp/mine_dossiers_20260926/`）

- **疑似判据失效 43 门**（装载√无配对测试，不判可删，Owner 令只合并/降档/diff 化）：DOC-HEADER-SUITE, GATE-12/13/14/16/17/22, GATE-ADM, GATE-ANY-ABUSE, GATE-BP-PLACE, GATE-C2, GATE-CODEGEN-IDEMPOTENT, GATE-DEBT-BRIDGE, GATE-DEDUP, GATE-DOC-NODE-ID, GATE-ENCODING, GATE-FRONTMATTER, GATE-FRONTMATTER-AUDIT, GATE-GEN-NO-REALTIME-TIME, GATE-ID-UNIQ, GATE-MCP, GATE-NAMING, GATE-NAMING-AUDIT, GATE-NESTED-FLAT-PREFIX, GATE-NO-COMMIT-DERIVED, GATE-NO-TESTS-UNIT, GATE-NODE-LABEL-QUALITY, GATE-PROTECTED-PATHS, GATE-PYTEST-CONFIG-DRIFT, GATE-REG-BL, GATE-RETURN-CONTRACT, GATE-SCHEMA-TRUTH, GATE-SCRIPT-Q, GATE-SILENT-DEGRADATION, GATE-SRC-NO-DATA, GATE-SSOT-CODE, GATE-SYMBOL-CONVENTION, GATE-TEST-SYMBOL, GATE-TRIPLE-ALIGN, GATE-VMS-SSOT, GATE-WORKTREE-OPS-TELEMETRY, RECONCILER-FILE-OPS, STASH-ACCUMULATION
- **装饰/悬空 9**：停用链 4（ALGO-FLOW-LINK、CAPABILITY-OVERLAP、PERMANENT-SYSTEM-TRIGGER＋子目 MANUAL-ONLY-PERMANENT，前三者名册 claim active 但 manifest enabled=false=**停用虚报**）＋悬空 4（COMMIT-CRITICAL-SECTION-LOCK、GATE-ZR、GATE-DRIFT、GATE-ERRCODE——无钩子无启动器承接）
- **半接线 2**：GATE-ERRCODE（仅单一脚本顺带调）、VOCAB-CHAIN（in-process 宿主停用、pre-commit 同族 hook 在，两面等价性未证）
- **C 类守护件 28**：装饰 2（alert_aggregator 零调用方、session_env_guard 仅 noqa 静态 import）；疑似判据失效 3（check_tick_duplication、batched_auto_committer、session_claim——有调用方零测试）；其余 23 件真执法面（初判未过反事实闸）
- **D 类**：heartbeat_daemon 无对应计划任务、会话拉起型=半接线（队列/会话一停即饿死）
- **名册三账漂移**：gate_registry.active ↔ in_process.enabled ↔ pre-commit hooks 三份账可漂移（3 停用虚报+in_process total_gates 字段 102≠103）；反向差集长尾 6-10 个"有钩子无名册"件（retire_tmp_artifacts、detect_direct_llm_calls、validate_commit_message、auto_handoff_log、scan_debt、serve_docs 等，待字段化重跑）
- 宪法 17 条映射：RULE-SSOT / RULE-DATA-OPS / RULE-SCHEMA-TZ / RULE-RULING 四条执法件落"疑似判据失效/半接线"（GATE-SSOT-CODE、check_tick_duplication、GATE-GEN-NO-REALTIME-TIME、RULING-REFERENCE 零配对红证）

### 1.7 图书馆自身供数轴：potential_consumers 全空（🚨本日新发现回归，见 2.6）

---

## 二、发现要处理的（行动清单）

### 2.1 提交链施工队列（收口卷定序 C1-C5＋1 条 P0 新缺陷）

| # | 事项 | 要点 | 锚 |
|---|---|---|---|
| ⚠P0 | **gate_auto_registrar priority=77 撞号 FAIL-CLOSED** | DOC-HEADER-SUITE 与 BLUEPRINT-FORMAT 同 priority=77 ⇒ 入队预检**整体 disable**、带病袋直入队列；先例=后到者让位（RULING-COMMIT-VERIFIED 77→109） | 收口卷 §四 |
| C1 | 封旁路：requeue 通道+enqueue_item 直调第 4 入口挂入队预检 | 部署后三登记族仍新死 47 件/窗；E-2 requeue 无预检、E-3 API 层无强制、E-4 TOCTOU 窗 | M1 §3.7/§8 |
| C2 | 快照自洽见证出厂 | 候选 A（码在 `.aidrafts/lane_ff_snapself`）**必须同批** W17（--base-head 不填 base_blobs=按官方处方操作反而关掉见证）、W18 池化重放腿无见证、W19 剥除无痕；同批候选 C 生产侧新鲜性（A 单独出厂=已装见证错觉）、候选 D 基底自证链 | M2 §8/§10 |
| C3 | CREATE-GUARD 触发面 diff 化/own-scope | 提交链最大单项耗时 4488 次×mean 23.4s=累计 105,154s；R5-DIGIT-SUFFIX 触发率 0.94 同批；须重放 100 笔自证 | M4 §3 |
| C4 | 假绿灯交叉尺 | task_runs 回执×目标表真行数互证；rows_written 记回执；ch_writer 失败态/空态分离（C11）；str⧸date 共因修复（C1） | 收口卷 C4、M3 §7 |
| C5 | 装饰件接线 | 名单=§1.6 装饰 9+半接线 2+C 类装饰 2+heartbeat | M5 §3 |

### 2.2 管线数据面施工项（M3 两卷）

- **FALSE_GREEN 5 腿**（SUCCESS 但目标表 0 行）：realtime_snapshot_incremental、etf_benchmark_refresh、suspend_status_premarket/postclose/derive_weekend
- **STALE 13 腿**：process_reaper_keep 白名单逐腿核对防误杀循环（daily_valuation、index_member_postclose、kline_sector_15min/1min/30min/5min/60min、restricted_shares、share_change、stock_basic_postclose/premarket、technical_indicator_full_refresh、top10_circulating_shareholders）
- **FAILED 8 腿**：2 腿共因 str⧸date（consensus_daily_build、financial_derived_build→C1 一处 _norm_date 覆三实例，反例护栏：pattern_win_rate 不同根勿打包）＋6 腿待裁修接口/换源/退役（audit_opinion 停 05-29、etf_share_snapshot 停 09-18、l2_tick_snapshot 未知 capability、news_tushare 接口名、pattern_win_rate exit1、rights_issue 缺接口）
- **NEVER_RUN 10 腿**：逐腿核"冗余注册 vs 应跑未跑"（factor_decay_monitor_weekly、global_*×4、ir_activity、irm_interactive_qa、kline_5min_history_backfill、kline_us_daily_qmt、tick_backfill_weekly）
- **NO_TARGET_TABLE 4 腿**：QMT 占位死腿×3＋trading_lifecycle_weekly（注销 vs 补登记待裁）
- **值级假绿**：news_sentiment_score 冻结 2025-09-09（Owner 门，见 2.3-3）；restricted_shares 前瞻值 2035 污染新鲜度尺（施工）
- **观测补强**：reconciliation_differences 心跳元表（C6）；pattern_win_rate updated_at 尺＋exit-1 取栈（C5）；告警尺缺失（两 build 崩停更 8-12 天无人知）；l2_tick/etf_benchmark/suspend 三例"schema 在数据零"DESC 定点（etf_benchmark date 列 ALL_NULL）；骨架 stock_valuation 库名修订
- **任务面**：tasks.yaml 270 vs 骨架 271 分母差 1（L-1）；recon_runner 是否被真触发未证（L-3）

### 2.3 Owner 门位事项（跨案卷去重 17 条）

1. DDL：kline_weekly_hfq / kline_monthly_hfq 补 lineage_version 列（同族独占版本不变量破口）
2. 空壳表 9 张建腿 vs 退役：ipo_schedule、msci_adjustment、stock_valuation、stock_candidate_pool、market_index_meta、margin_target_adjustment（6 张未登记 known_data_gaps.yaml，补登记为前置）＋suspend、etf_benchmark＋**第 9 张=l2_tick（本日 census.json 复核补齐）**
3. 真源收敛三处：reconciliation_differences（governance.db 写 vs c1_market 读）；consensus_daily 主表 vs _repaired；news_sentiment_score vs window（涉退役=净删域）
4. Ollama 11434 恢复=仅凭 Owner 显令；重启提案已封矿勿重提
5. heartbeat 计划任务兜底（解锁=held_overlap 放行事件计数账先落地）
6. 门禁 diff 化施工批门位确认＋恒绿贵门白天审计窗（M4 C3/C5/C9）
7. dead 系 2397 件归档净删（M4 §11.4）
8. M2 候选 A 见证层并案出厂（死信会变多；必须与候选 C 同批，W17/W18/W19 缺一未收口）
9. 入袋 requires-sync"宁停勿吃"是否适用交互正门（首波可能批量拦）
10. --base-head 旗 CLI 契约：补 base_blobs 或禁旗，二选一
11. [GW:] 归属证据去文本化（牵动宪法 §9.8 提交工具红线）
12. gate_registry 在册 174≠180 归位＋自洽台双锚化（邻班重述）
13. assert_single_writer_dev_history 零运行时调用点是否提为事件触发 reconciler（#ARCH-317 强制面）
14. commit_queue_interactive 出厂 OFF 翻转窗口
15. 预检设计原则改册净零声明（C1/C2 触及在册文字时按宪法 §4）
16. 热册三向合并策略变更（与 M2 候选 B′ 派生件让路相关）
17. M5 遗留：①PERMANENT-SYSTEM-TRIGGER/GATE-VOCAB(in-proc)/ALGO-FLOW-LINK/CAPABILITY-OVERLAP 四停用是否有意或名册改 status；②COMMIT-CRITICAL-SECTION-LOCK/GATE-ZR/GATE-DRIFT 三悬空件合并/降档方向；③43 无配对件红样采集排期（日班 20 门抽样过 replay harness）

### 2.4 待裁 6 条（90 普查 §六）

裁-1 ROOR 76 vs 77 收敛（建议补 summary=77）；裁-2 双编号收敛（建议 F 册唯一真源+L 降级视图+M0 编号退役）；裁-3 F111 入口口径（app_panel vs api_server，随 M6 退役裁）；裁-4 F62 合规门接线前置=人工报送（保持 fail-closed）；裁-5 环节总数 122→~151 改写授权（建议先开 29 候选漏项确认册）；裁-6 infra_runtime/knowledge 域边界归属。

### 2.5 挂起项（主要，解锁条件见各案卷自审闸）

派生件让路重算（M2 B′，解锁=死信占比 ≥5% 或静默吃件实证）｜[GW:] 去文本化（M2 E）｜时间基底兜底对无标记提交失明（M2 G，先补可达性计数）｜直提面未实测（M2 W7，需授权环境）｜pool 工棚重放树残留=未挖最大单点（M2 §9③）｜同秒并列亚秒序号（M4 C1）｜machine 车道 aging 扩 lane=null（M4 C4）｜心跳三套机制重叠内收（M4 L5）｜skipped_dirty 主区漂移 1802 行消费方（M4 C7，先定"谁有权清"）｜NOTHING_TO_COMMIT 假死 62/31 件并案归因（M4 L1+M1 C-9/L-2）｜入队口自动补登（M1 C-3，解锁=热册合并死 69 件/窗先降）｜落地侧纯格式自动修袋重投（M1 C-4，解锁=修后重算 blob 原语）｜死信 health 面板化（M1 C-5，先修 lane 打标）｜dead 长尾 9 条 L-1..L-9｜etf_benchmark date 列定点（M3 L-7）｜C 类 23 件"返回值进分支"逐件读码（M5 §4）｜一次性 schtasks N/A 任务清理（Owner 门，schtasks 写禁）

### 2.6 本日新发现（本会话实测）

1. **🚨 potential_consumers 二次清零回归**：#410② 09-24 回填 68 资产的消费方记录已被 09-25~27 多轮全量重采集清空（lib_assets 44,773 行该字段全空；--feeds 恒空；抽查 TBL:ch:c1_backtest.sim_platform_journal 证实）。HEAD upsert 有 COALESCE 保护、采集器不携字段 ⇒ 元凶疑似某轮 ingest 进程吃启动时刻旧代码（回填后首轮=st-wm1-wave0 09-25 全量 169,734 register）。处置：**定位清零元凶与机械重放 68 条（lib_events 有存证）同袋**，否则重放后再被清。
2. 第 9 张空壳表=l2_tick（census.json 复核，补 M3 §8.2 之缺）。
3. wave13_chief3/inbox 两件待消费：CAND-GOVTEST-005 注册表撞号案卷（candidate_module_registry 双 id，在途修 L20231→007 未落，注释行未同步）＋byte_ledger 三件（01_byte_ledger/byte_matrix/register_manifest）待登记落地。

---

## 三、分母与复跑命令

```bash
# 1.1 零引用分布：python -c "import csv;rows=list(csv.DictReader(open('docs/_audit/data_utilization_audit_2026-08-24.csv',encoding='utf-8-sig')));from collections import Counter;print(Counter(r['status'] for r in rows))"
# 1.4 环节状态：grep -oE "\| (built|partial|design|missing)" docs/_working/fullflow_mining/00_skeleton/00_全环节总册.md | sort | uniq -c（注：带括号注记的行需逐行读，总册 122 行逐行判为准）
# 1.5 TDM null：awk '/^- node_id:/{id=$3} /module_ref: null/{print id}' config/trading_decision_map.yaml | wc -l   # =38
# 1.6 门禁四态：python -c "import json;raw=json.load(open('.runtime/tmp/mine_dossiers_20260926/census_raw.json',encoding='utf-8'));from collections import Counter;print(Counter(r['state0'] for r in raw['gates']))"
# 2.6 清零核验：SELECT count(*) FROM lib_assets WHERE cardinality(potential_consumers)>0   # 09-27 实测=0（#410② 回填存证在 lib_events 68 条）
```

分母口径备注：dead 死信=682 件/5 自然日窗（09-22..09-26，M1 卷口径为准，收口卷"3 日窗"为旧口径）；270 任务全扫基准日=2026-09-24（09-25 中秋休市）。
