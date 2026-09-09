---
ttl: task_bound
---

> **doc_type**: 施工台账（miniQMT→文件桥全面替换）
> **created**: 2026-09-08 | **owner**: Owner 授权 AI 施工
> **真源**: 93 号备忘 v1.8.6（`docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/93_qmt_file_bridge_playbook.md`）
> **摸排基线**: 2026-09-08 全量扫描（tasks.yaml 66 处 source 引用 + 代码 grep + CH 实测数据量）
> **退役日**: 2026-09-18（券商关停 miniQMT 通道）
> **使用规则**: 做完一项勾一项（`- [ ]`→`- [x]`），勾选时在行尾补 `（✅MM-DD commit哈希）`；本台账 = 本迁移工程唯一进度真源，禁止删档（同 frontend-backend-gap-ledger 规则）；全部勾完且退役日验证过 → 归档 _archive

# miniQMT → QMT 文件桥 替换施工台账

## §0 关键背景（防遗忘速查）

- 替代方案 = 大QMT 沙箱 3 策略（EXEC_V16.4 下单 / QUOTE_V17 取价 / TICKDUMP3_v19 全市场 tick）+ 文件桥/HTTP 桥
- 桥三通道已实盘验证：tick（TICK_SOURCE=bridge 一键切）、下单（HTTP 32ms+文件兜底）、取价（quote.csv）
- **最大盲区**: 93 备忘 P0 清单只覆盖 tick/下单/对账；tasks.yaml 另有 59 个主源 miniqmt 数据任务，其中 **31 个无 fallback**——本台账 §2 主体
- 环境分区铁律：sim=`E:\qmt_bridge_sim\` / real=`E:\qmt_bridge\`，消费类按 env 隔离

## §1 已就绪项（确认即勾）

- [x] tick 主链路：tick_subscriber bridge 模式（TICK_SOURCE 环境变量，9/7 已闭环，93 §14.7）（✅09-08 复核加固：TICK_SOURCE=bridge 已持久化 User 级 + guard 子进程实测读 ticks3.csv 入 CH；含 #BRIDGE-WRONG-FILE 修复 ENV_CONFIG→ticks3.csv，✅09-09 核实已提交 75aae01b11）
- [ ] 下单链路：QmtFileBridgeBroker（HTTP 127.0.0.1:18901 + orders_sim.csv 兜底）
- [ ] 执行取价：QmtFileBridgeQuoteProvider（quote.csv 尾读+新鲜度闸门）
- [x] 持仓/资金 API：api_server 直读 `E:\qmt_bridge\Stock\`（GBK，row[7]/[9]/[15]/[18] 列序）（✅09-08 实盘 CSV 逐列核对一致；⚠️ 红旗转 §8：PositionStatics.csv 已 13 天未更新——真实 QMT 终端疑似未开，9/18 前 MUST 验证）
- [ ] 交易通道监控：web/services/api.js `fetchBridgeStatus`（HTTP 桥探活+桥文件族活性）
- [ ] 健康面板组件：components/qmt_bridge_health.py（3 秒自刷）

## §2 tasks.yaml 数据任务（59 主源 + 6 fallback + 清理项）

### §2.1 档 1——有 fallback 的 26 个（退役日自动 failover，零改动保命）

> 策略：9/18 不动 → 自动切 akshare/baostock；事后逐表评估是否升 fallback 为主源（字段口径/深度降级评估）
> 勾选语义：`[x]`=已评估并作出"保持 fallback 主源 / 升级主源 / 换桥"裁定

- [ ] adj_factor_incremental（fallback: akshare）
- [ ] kline_daily_incremental（baostock）
- [ ] kline_daily_full_refresh（baostock）
- [ ] kline_daily_hfq_incremental（akshare）
- [ ] kline_weekly_hfq_incremental（akshare）
- [ ] kline_monthly_hfq_incremental（akshare）
- [ ] kline_index_incremental（akshare）
- [ ] kline_futures_incremental（akshare）
- [ ] kline_hk_daily_incremental（akshare）
- [ ] kline_us_daily_qmt_incremental（akshare）
- [ ] balance_sheet_incremental（akshare）
- [ ] income_statement_incremental（akshare）
- [ ] cashflow_statement_incremental（akshare）
- [ ] financial_indicator_incremental（akshare）
- [ ] stock_list_refresh（akshare）
- [ ] index_weight_refresh（akshare）
- [ ] kline_cb_full_refresh（akshare）
- [ ] 其余 9 个（完成时补登实际清单——摸排时按 yaml 顺序核对）

### §2.2 档 2——无 fallback 且 CH 真在产（17 个，断流=真损失）

#### A. 分钟K线族 ×13【最大缺口：桥无 K 线 dump 通道，需三选一立项】
> 方案候选：a) 沙箱策略扩 K 线 dump（TICKDUMP 模式复用） b) BridgeTickSource 聚合合成分钟K c) akshare 分钟线兜底（质量差）——**先立项摸底再动**

- [ ] kline_1min_incremental
- [ ] kline_5min_incremental
- [ ] kline_15min_incremental
- [ ] kline_30min_incremental
- [ ] kline_60min_incremental
- [ ] kline_etf_1min_incremental
- [ ] kline_etf_5min_incremental
- [ ] kline_etf_15min_incremental
- [ ] kline_etf_30min_incremental
- [ ] kline_etf_60min_incremental
- [ ] kline_lof_1min_incremental
- [ ] kline_lof_5min_incremental
- [ ] kline_lof_15min_incremental
- [ ] kline_lof_30min_incremental
- [ ] kline_lof_60min_incremental
- [ ] kline_etf_daily_incremental
- [ ] kline_weekly_incremental（无 fallback）
- [ ] kline_monthly_incremental（无 fallback）
- [ ] kline_5min_history_backfill（月频回填，无 fallback）

#### B. L2/期权族 ×5【前置：确认大QMT 沙箱行情权限是否含 L2】
> ⚠ **09-09 上午勘误（Owner 质询触发，代码实话实查）**：本节五任务**没有一个真依赖付费 L2**——
> auction_snapshot/auction_book=`get_full_tick` 实时快照（9:15-9:25 竞价时段轮询，含五档）；
> option_greeks/option_iv_surface/convertible_bond_iv=标准期权合约要素+行情价，**希腊字母/IV 全是我们自己用 BS 公式算的**（miniqmt_provider `_compute_greeks_for_option`/`_solve_iv`，r=0.03）。
> 全库唯一真 L2 任务=l2_tick_snapshot（get_l2_quote），**本就 disabled、CH 空表**。
> → 真实前置不是"L2 权限"而是：①桥 dump 在 9:15-9:25 竞价时段是否照常出行（待交易日早晨验证，并入 §8.1 观察）②桥 universe（现 8394=A股/基金/指数/转债）**不含期权合约**，期权族续命需扩 universe（9/18 后动沙箱一次）。
- [ ] auction_snapshot（4.7 万行，auction_highfreq 时段）
- [ ] auction_book（191 万行）
- [ ] option_greeks（9/7 在产）
- [ ] option_iv_surface（9/7 在产）
- [ ] convertible_bond_iv（9/8 在产）

#### C. 财报族 ×4【miniQMT 财务接口独有，akshare 同类字段口径不同，逐表评估】
- [ ] shareholder_incremental（c3_fundamental.shareholder_count，50 万行）
- [ ] earnings_forecast_incremental（12.6 万行）
- [ ] express_report_incremental（2.9 万行）
- [ ] main_business_incremental（209 万行）

#### D. 其他真在产 ×3
- [ ] index_quote_snapshot（quote.csv 只覆盖订阅标的 → 需扩 QUOTE_V17 订阅清单或降频 akshare）
- [ ] market_breadth_snapshot_minute（market_breadth_collector.py miniqmt 直连 → 桥数据聚合改造）
- [ ] tick_data_snapshot 主源切换确认（TICK_SOURCE 切 bridge 后本任务语义=桥，tasks.yaml source 字段同步更新）

### §2.3 档 3——无 fallback 周边任务 ×6【前置：确认大QMT 沙箱市场覆盖（港/美/期货）】
- [ ] hk_kline_incremental（4582 行在产）
- [ ] hk_kline_full_refresh
- [ ] kline_us_daily_qmt_incremental（385 行）
- [ ] futures_kline_qmt_incremental（870 行）
- [ ] kline_cb_incremental（可转债 K 线）
- [ ] futures_tick_intraday（股指期货 tick → TICK_SOURCE=bridge 后 BridgeTickSource 覆盖评估）

### §2.4 档 4——占位任务清理 ×4【表不存在/空表，直接清】
- [x] margin_trading_qmt_placeholder（表不存在）→ 已加"退役冻结 2026-09-18：miniQMT 独有源，表从未产出，待 Owner 裁定替代源后重建"注释（disabled 原有，source 值不切——红线 1）（✅09-09 8981a53f29）
- [x] dragon_tiger_qmt_placeholder（表不存在）→ 同上（✅09-09 8981a53f29）
- [x] block_trade_qmt_placeholder（表不存在）→ 同上（✅09-09 8981a53f29）
- [x] l2_tick_snapshot（CH 空表 0 行 + fallback 循环引用自己 `fallback: miniqmt`）→ 已清 `fallback_sources: []`+注释（循环自引用无 failover 语义；L2 降级重建随 §2.2-B 裁定）（✅09-09 8981a53f29）

### §2.5 miniqmt 仅作 fallback 的 6 个【主源仍在，退役后 fallback 死→自动跳过，低优先】
- [ ] futures_position_incremental
- [ ] audit_opinion_incremental
- [ ] futures_term_structure_incremental
- [ ] daily_valuation_full_refresh
- [ ] option_kline_incremental
- [ ] option_kline_full_refresh

## §3 后端代码层

- [x] scheduler.py：provider 工厂注册 `qmt_bridge` 源（source_to_meta/source_to_path/create_provider 三表+分支，参照 miniqmt 条目；新 Provider depgraph 节点 12118065 已转 production）（✅09-09 8981a53f29）
- [x] scheduler.py：非交易日守卫 miniqmt 拼写防护（L335-363）扩桥任务语义（qmt_bridge 同语义：沙箱非交易时段冻结，桥文件不增长）（✅09-09 8981a53f29）
- [ ] market_breadth_collector.py：8 处 miniqmt 直连 → 桥数据聚合（依赖 §2.2-D 宽度快照方案裁定）
- [x] speed_tester.py：数据源测速器加 qmt_bridge 通道——专用桥口径（ticks3/quote.csv 尾读延迟+HTTP 18901 RTT），`run_speed_tests` 全量跑附带，bridge_probe 结果入 fetch_perf 同 schema（✅09-09 8981a53f29）
- [x] source_health_check.py：miniqmt 探活旁并列 qmt_bridge 登记项+_probe_qmt_bridge 探针（桥文件族 mtime 新鲜度含交易时段判定+HTTP 18901 探活，语义对齐 api_server fetchBridgeStatus）（✅09-09 8981a53f29）
- [x] policy_registry.py / capability_symbol_gate.py / backfill_checker.py / cli.py / capability_validator.py：源登记与门禁里的 miniqmt 语义更新——policy_registry 增 qmt_bridge DEFAULT_POLICIES（配套 test_policy_registry 断言同步）；cli 帮助文案补桥源示例；capability_symbol_gate/capability_validator **判读=通用 AST 门禁无源登记点，不需改**（新 provider 走 capability=="x" 通用路由形态，两门禁原生覆盖）；backfill_checker **判读不改**（TSV 内 miniqmt=历史回填数据 source 列，囤货语义 9/18 前仍有效，桥无历史回补通道）（✅09-09 8981a53f29）
- [x] miniqmt_channel_manager.py：退役 dormant 策略——MINIQMT_CHANNEL_RETIRED_DATE=2026-09-18 + MINIQMT_CHANNEL_REPLACEMENT 常量与 fail-closed 注释落码（状态机逻辑不动，接口保留=测试消费+桥重连参照实现）（✅09-09 8981a53f29）
- [x] ex_core/adapters/__init__.py（7 处）+ reference_data_manager / multi_timeframe_fusion / corporate_action_adjuster / board_lot 各 2 处判读：adapters/__init__=**活跃依赖**（MiniQmtBroker 统一导入枢纽，保留至 9/17 切换窗口）；其余 4 文件 8 处全为 [CONSUMERS]/[ALGO_FLOW] 注释元数据（无运行时 import，且描述的消费者关系属实——board_lot 已同时列桥 broker），措辞已一致无需统一；无"待裁定"新增项（✅09-09 8981a53f29）
- [x] 回测域核查：event_driven_engine.py / matching_logic.py 的 miniqmt 字样——matching_logic=**活跃依赖**（回测-实盘撮合一致性 B 方案：MiniQmtBroker.submit_order 复用预校验，保留至切换窗口）；event_driven_engine=**活跃依赖，需裁定**（L139/219 MiniQmtQuoteProvider.fetch_historical(tick) 回测 tick 回放，9/18 后 xtquant 历史缓存断供）→ 已登记 §8.3"留 Owner 裁定"（✅09-09 8981a53f29）
- [ ] P0-2 钱路：paper_session/intraday_main 下单链切 BrokerInterface 注入（接口已抽象，93 §13 定级"小"）
- [ ] P0-3 对账：recon_runner/broker_settlement_adapter 切桥（同上）

## §4 前端 7 点

- [ ] F1 components/trade_panel.py：`broker_id="miniqmt"` 默认值 → `qmt_bridge`（L92/L452 两处）【9/17 收盘后窗口——红线 2】
- [x] F2 components/position_monitor.py：MiniQmtBroker.get_positions() 注入点旁并列 QmtFileBridgeBroker——新增 create_position_broker(source/env) 工厂（桥读 E:\qmt_bridge[_sim]\Stock\PositionStatics.csv GBK row[7]/[9]/[15]/[18]，duck-typed PositionSnapshot 同构注入）+ app_panel 注入参数（默认 miniqmt 不切——红线 2）（✅09-09 3b25f73aed）
- [x] F3 components/order_book.py：MiniQmtQuoteProvider 旁并列 QmtFileBridgeQuoteProvider——create_quote_provider(source/env) 工厂（quote.csv 尾读+新鲜度闸门）+ app_panel 注入参数（默认 miniqmt）（✅09-09 3b25f73aed）
- [x] F4 services_registry.py L91：QMT 客户端进程探测 pattern `xtminiqmt|xiadan|qmt` → 补 `xtitclient`（大QMT 主程序 XtItClient.exe=93 备忘 §2.3 实地辨识名，9/18 后 pattern 命中全靠它）。⚠ 实测待复核：夜班 Get-Process 仅见 XtMiniQmt（PID 29720）在跑，大QMT 客户端未开（与 §8.2 PositionStatics 13 天未更新红旗互证）——Owner 开真实终端后核对进程名，不符则更新 pattern（✅09-09 3b25f73aed，复核留 §8.2）
- [x] F5 web/services/api.js fetchBridgeStatus：注释标注 miniqmt 信号 9/18 退役语义 + bridge.js miniQMT 基线卡片与探活实测行退役日后显"已退役"占位（非"已停"，防误读为故障；判定=retire_date 本地日期比较）（✅09-09 3b25f73aed）
- [x] F6 tick/行情统计页：下载监管页 tick_data 今日新增按 data_source 分组——后端 download_status 增 today_rows_by_source（CH 按日 GROUP BY data_source）+ 前端 download.js dlTodayCell 两段式渲染（mini/桥 并存+合计），9/18 后 mini 段归零、桥段独立可见，防合计 30 倍缩水被误读为断更（✅09-09 3b25f73aed）
- [x] F7 服务总闸：services_registry 心跳分支读 biz 心跳 mode 字段（bridge→"桥模式"/xtdata→"miniQMT推送"）拼入 detail 上屏 + st.mode 结构化字段（✅09-09 3b25f73aed）

## §5 退役日操作 SOP（9/18）

- [ ] 前置：确认沙箱 3 策略活着（EXEC_V16.4 / QUOTE_V17 / TICKDUMP3_v19）
- [ ] `[Environment]::SetEnvironmentVariable("TICK_SOURCE", "bridge", "User")` + `schtasks /run /tn ZephyrAlpha_TickSubscriber`【9/8 已预执行并验证（env 持久化 + guard 重启实测子进程 --bridge --bridge-env sim）；9/18 复跑仅为确认】
- [ ] api_server 重启（registry 中文名快照更新，DS-221 类新表 name_zh 生效）
- [ ] 观察 26 个 fallback 任务首日 failover 日志（akshare/baostock 接管是否成功）
- [ ] 监控页 data_source 分组数字核验（F6 验证）
- [ ] 沙箱侧：miniQMT 客户端卸载确认；大QMT 客户端进程名记录（反馈 F4）

## §6 验证标准（全部完成才算闭环）

- [ ] tasks.yaml `source: miniqmt` 归零或全部带"退役冻结"标注（grep 实测）
- [ ] 代码库 `rg miniqmt src/ scripts/` 残留逐条归类（真源历史/退役标注/活跃引用=0）
- [ ] CH 全部在产表 9/18 后每日增量正常（下载监管页四态灯无新增红）
- [ ] 前端 7 点全部上屏验证（浏览器实测）
- [ ] 退役周对拍：桥数据 vs miniqmt 最后一周冻结数据抽样一致率（tick ±5s 对拍口径）

## §7 施工轮次记录

| 轮次 | 日期 | 完成项 | commit | 备注 |
|---|---|---|---|---|
| 0 | 2026-09-08 | 全量摸排+本台账建立 | （本提交） | 摸排数据：59 主源/6 fallback/CH 实测行数 |
| 1 | 2026-09-08 | 闪窗根治：10 个计划任务 wscript+launch_hidden.vbs 包装（含 vbs 参数透传）、register_guard_tasks.ps1 模板防回退、AI-Wrapper-Inject 僵尸实例清理、DataScheduler 补启用、死任务 TickVerify_1306 删除 | 75aae01b11 | 元凶=AI-Wrapper-Inject 每 1 分钟直连 powershell 闪窗；#ARCH-OPS-001；09-09 夜班核实补登哈希 |
| 2 | 2026-09-08 | guard TICK_SOURCE=bridge 持久化（User 级）+ #BRIDGE-WRONG-FILE 修复（ENV_CONFIG sim/real→ticks3.csv，93/93 测试过）+ 误灌 166 万行 9/7 污染数据 ALTER DELETE 清理（9/7 恢复 308,657 行）+ 下午真积压回补（9/8 = 739,952 行） | 75aae01b11 | 事故根因：env 默认路径未随 v19 升级，早间 --bridge-file 覆盖掩盖漂移；事故记录已注释进 tick_subscriber.py；09-09 夜班核实补登哈希 |
| 3 | 2026-09-08 | 口径对齐全链实测（持仓 row[7]/[9]/[15]/[18] ✅、五档 dump 25 列 ✅、CH 1 档+Redis 完整 5 档 ✅）+ 本台账更新（§1 勾 2 项/§2.2-D 与 §5 标注进度/新增 §8） | 75aae01b11 | PositionStatics.csv 13 天未更新红旗转 §8 |
| 4 | 2026-09-09 夜班 | §2.4 占位清理 ×4 + §3 桥能力注册主体（scheduler 四点注册/QmtBridgeIngestProvider 新建/六文件源登记/speed_tester 桥通道/channel_manager dormant 常量/ex_core+回测域判读）+ §4 前端 F2-F7 + §8.3 核实勾选 + §8.5 摸底报告 | 8981a53f29（第三批）/ 3b25f73aed（第四批） | 只增桥不删 miniqmt；tasks.yaml 零 source 切换（红线 1）；F1 未动（红线 2）；TICK_SOURCE 链未动（红线 3）；夜班遇 3 并发会话（st-nodebt/greatwall-0020/本会话）锁竞争与门禁竞争，全部走合规通道解决 |

## §8 2026-09-08 增量待办（桥切换过渡期，按优先级）

### §8.1 明早（9/9）盘前/盘中观察【P0，bridge 独挑第一个完整交易日】

- [ ] 09:15 跨天轮转三连观察：① ticks3.csv 是否被沙箱重建（size 归零/仅表头）② ticks3.csv.offset 越界自愈是否归零（115,620,192 > 新文件 size → 应重置 0 从头读）③ 09:30 后 CH qmt_bridge 行恢复增长（`SELECT count() FROM c1_market.tick_data WHERE trade_date=today() AND data_source='qmt_bridge'`）
- [ ] 盘中抽查：CH 新行 timestamp 与 wall clock 偏差 <1min（防再吃陈旧 timetag）；桥子进程 biz.heartbeat mode=bridge、errors 无持续增长
- [ ] Redis `tick:*:latest`（db0，现存 147 键为旧 xtdata child 昨日残留）确认被 bridge child 盘中刷新（低优，仅观察）

### §8.2 Owner 动作【P0，9/18 前 MUST】

- [ ] 打开真实大QMT 终端一次，验证 `E:\qmt_bridge\Stock\PositionStatics.csv`/`Account.csv` 自动导出恢复（已 13 天未更新，mtime 停在 08-26 20:50；持仓 API/前端全靠它）

### §8.3 记录与提交【P1】

- [x] 93 号备忘补 §14.10：#BRIDGE-WRONG-FILE 事故（根因 env 默认路径未随 v19 升级/影响 166 万行污染已 ALTER DELETE 清理/修复 ENV_CONFIG→ticks3.csv/教训三条）+ 闪窗根治（#ARCH-OPS-001 全量落地记录）+ 9/9 观察清单——09-09 夜班核实：前序会话已于 9/8 21:21 完成（§14.10.1-14.10.5 五小节+changelog v1.8.8），无需重做（✅09-09 75aae01b11 核实）
- [x] commit 待提交清单：tick_subscriber.py（ENV_CONFIG 修复+事故注释）、launch_hidden.vbs（参数透传）、register_guard_tasks.ps1（vbs 模板 ×2）、scripts/run_ttl_rejudge_daily.ps1（新）、scripts/ch/run_optimize_merge_hidden.ps1（新）、本台账——09-09 夜班核实：六文件全部已由 75aae01b11（2026-09-08 21:21）提交，工作区无残留；台账 §7 轮次 1/2/3 的"待提交"哈希已补登（✅09-09 75aae01b11 核实，台账簿记更新随本轮 8981a53f29 后续 docs 提交）

#### §8.3.1 四项裁定（09-09 夜班 AI 依授权自裁，Owner 可否决）

1. **✅ 已裁定：回测 tick 回放源 → 切 CH tick_data（方案 a）**。event_driven_engine 的回测 tick 回放从 MiniQmtQuoteProvider.fetch_historical（xtquant 本地缓存，9/18 断供）切为读 CH `c1_market.tick_data`（miniqmt 囤货 + qmt_bridge 双源同表，SQL 直取、无 SDK 依赖）。**已知降级（如实登记）**：tick_data 表 schema 为 1 档（tick_to_row 取 [0] 设计），价格/成交量回放全覆盖，5 档盘口深度回放降级——若后续做T 回测需要盘口深度，再启用 QMT【收盘清盘】逐日累积缓存通道（93 §11.5a，即 §8.5.1 方案 a 变体）。**执行**：新建 CH 回放 adapter（保持 provider 注入接口不变）列入 9/17 窗口施工单，1 人日。
2. **✅ 已裁定：F4 进程名 pattern 维持现状**（`xtminiqmt|xtitclient|xiadan|qmt`，xtitclient 依据=93 §2.3 实地辨识，非猜测）。复核动作与 §8.2 开真实终端绑定（那本来就是 9/18 前 MUST——PositionStatics 已 13 天未更新）；开终端后 1 分钟核对，若不符改 1 行 pattern。**无前置阻塞**：pattern 错的最坏后果=服务总闸 QMT 灯假灰，不误伤数据链。
3. **✅ 已裁定：分钟K线族按 §8.5.1 推荐排序执行——b 立项 + c 同批 + a 缓议**。b（CH tick 聚合合成分钟K，复用 kline_resampler 幂等模式）9/17 窗口前完成开发+口径单测，9/18 起随桥独跑自然累积（无历史回补，切换前历史靠囤货+CH 存量——已接受）；c（akshare）同批挂校验兜底；a（沙箱扩 K 线 dump）触发条件量化：b 上线后前 5 个交易日对拍 akshare，价格 ±0.01 外偏差 >2% 或 bar 缺口 >1% 则 10 月立项。**执行**：列入 9/17 窗口施工单，b 约 1 人日。
4. **✅ 已裁定（09-09 上午按 Owner 质询勘误修订）：L2/期权族——勘误后口径大幅放松**。代码实查证实五任务均不依赖付费 L2（详见 §2.2-B 勘误注）：auction 族=get_full_tick 竞价快照，桥同源可续（唯一待验证=沙箱 dump 在 9:15-9:25 是否照常出行，并入 §8.1 早晨观察）；option 族=自算 greeks/IV，输入=期权合约要素+行情价，桥扩 universe 期权标的后续命（9/18 后动沙箱一次，列入退役日施工单）。真 L2 任务（l2_tick_snapshot）本就 disabled，无续命需求。
5. **✅ 已裁定（09-09 上午，Owner 提议采纳）：五档盘口落库立项**。现状=CH tick_data 按表结构只存 1 档（tick_to_row 取 [0]，设计如此），但**数据流里五档全在**（miniqmt 推送与桥 v19 25 列 dump 都带完整 bid1-5/ask1-5/bidVol1-5/askVol1-5，Redis 热缓存已存完整五档，仅 CH 落库时丢弃）。执行=新表 c1_market.tick_depth_5（同键 3 秒快照×五档 20 列）+ tick_subscriber 桥模式加落盘分支 + 近期历史回填（get_market_data_ex(period='tick') 返回 19 列含五档：miniqmt 9/18 前可回填近期若干天，9/18 后大QMT 沙箱同 API 可用【§11.5a 已实证】+【收盘清盘】已勾逐日累积）。**边界（如实）**：更早的深史五档任何渠道都不存在；回测五档精细撮合自切换日起有数据。列入 9/17 窗口施工单（约 1-1.5 人日）。

### §8.4 独立小问题【P2，与桥无关】

- [ ] TTLRejudgeDaily 计划任务 9/7 18:05 退出码 1（python 层面，backfill_ttl_metadata.py；每日 18:05 会重复闪红）
- [ ] QUOTE_V17 并入 TICKDUMP3 检查点：9/15 开评（93 §14.9 已落盘 v20 方案路径 A/B）；可选加速路径已呈报 Owner 裁定——明晚出 v20（dump+200ms 热线程照写 quote.csv）→ v20/v17 并行对拍 2-3 天 → 一致则退役 v17，9/18 只剩 TICK_SOURCE 一个切换变量
- [ ] §2.2-B 前置确认项的连带提醒：convertible_bond_list 的 max list_date 停在 09-03 已定性为 monthly_static 月频设计（非故障），10/1 正档观察项（93 备忘已记录）

### §8.5 分钟K线族三选一摸底报告（09-09 夜班，只出报告不实施，供 Owner 裁定）

> 范围=§2.2-A：1/5/15/30/60min × 股票/ETF/LOF + kline_etf_daily + 周月线 + 5min 历史回填。核心约束：桥无 K 线 dump 通道。

**方案 a）沙箱扩 K 线 dump（TICKDUMP 模式复用）**
- 机制：沙箱策略内 `get_market_data_ex(period='1m'/'5m')` 增量轮询追加写 CSV（复用 TICKDUMP3_v19 分批轮询+追加写+去重骨架）
- 工作量：~2-3 人日（沙箱 v21 策略 1 天开发+2 交易日验证；项目侧 provider kline capability 映射 0.5 天）
- 数据前提：QMT 本地 K 线缓存（【补充数据】UI 实证支持日线/5分钟/1分钟下载；【收盘清盘】已勾 1/5 分钟逐日累积——93 §11.5a）
- 体量：全市场 1min ≈ 5400 只×240 根/日 ≈ 130 万根/日（CSV 60-100MB/日，可缩 universe）
- 优点：**官方 bar 口径**（QMT 聚合，与交易所一致）；有近期历史（UI 补下载+清盘累积）
- 风险：中——bar 闭合与轮询相位差（半根 bar 剔除逻辑）；动沙箱=重开策略验证窗口（9/15 检查点已排 v20 合并评估，不宜并行加变量）

**方案 b）BridgeTickSource tick 聚合合成分钟K【推荐首选】**
- 机制：桥 tick 流（ticks3.csv，3-9 秒快照，8394 只全板块，已在产入 CH `data_source='qmt_bridge'`）→ CH SQL 聚合合成 bar——**复用 kline_resampler.py 的 argMin/argMax/toStartOfInterval 幂等模式**（15/30/60min 合成已有真源，只缺 tick→1min/5min 一段 SQL）
- 工作量：~1 人日（聚合模块+tasks.yaml capability 挂接+口径单测），9/17 窗口前可就绪
- OHLC 合成口径（铁律）：open=bar 内首 tick 价 / close=末 tick 价 / high=极值 / low=极值 / volume=Δvolume 累加 / amount=Δamount 累加；symbol×bar 窗口 GROUP BY；跨 09:30/13:00 半根 bar 按窗口裁剪
- 品种/周期：股票/ETF/LOF 全覆盖（桥 universe 含基金 2270 只），1/5/15/30/60min 全可合成
- 历史回补：**无**——只能从切换日起累积；切换前历史靠 miniQMT 囤货纪律（§10.3）+CH 存量
- 风险：低-中——3 秒快照粒度可能漏 bar 内极端瞬时价（快照语义 vs 逐笔，偏差需对拍量化）；集合竞价成交量归属口径需裁定（建议归当日首 bar）
- 决定性优势：**零沙箱改动=9/18 退役日零新增变量**（与 §14.9 路径 B"只剩 TICK_SOURCE 单变量"纪律一致）

**方案 c）akshare 分钟线兜底**
- 机制：`ak.stock_zh_a_hist_min_em`（东财源）；1min 深度仅近 5 交易日、5/15/30/60 近月
- 质量：官方 bar 口径 ✅，但东财反爬先例在案（push2 大请求断连，akshare 探针实证 0/5）+ 全市场 5400 只×5 周期调用量=限流高危
- 定位：**不宜作主源**；适合作 b 的对拍校验源（抽样 ±1 价位容差）与应急兜底
- 工作量：0.5 天（挂接既有 akshare 通道）

**推荐排序：b 立即立项（9/17 窗口前就绪）> c 同批挂校验兜底 > a 视 b 上线后对拍偏差再议（偏差率阈值建议：价格 ±0.01 外偏差 >2% 或 bar 缺口 >1% 则 10 月立项 a）**
理由：退役日纪律优先（b 不新增切换变量）；a 的官方口径优势等 b 的偏差数据说话；c 免费但深度/反爬撑不起主源。

### §8.5.2 L2/期权族摸底（§2.2-B 前置材料，任务 19）

**数据接口来源实证（rg 核实）**：auction_snapshot / auction_book / option_greeks / option_iv_surface / convertible_bond_iv 五任务全部路由至 `MiniQmtIngestProvider`（miniqmt_provider.py meta.capabilities 显式声明+fetch 专用方法 `_fetch_option_iv_surface`/`_compute_iv_rows`/`_fetch_convertible_bond_iv`/`_get_option_detail_safe` 等），数据源=xtquant SDK（L2 接口需权限，#ARCH-DATA-014 探测机制已有）。

**桥现状缺口**：桥文件族（ticks3.csv/quote.csv 均为免费 L1 口径 5 档快照）**无 L2 逐笔委托/逐笔成交，无期权 greek 字段链**。

**大QMT 沙箱同等权限验证步骤（待 Owner 开终端执行，9/18 前完成）**：
1. Owner 登录大QMT 终端（XtItClient.exe），核对账户行情权限等级（免费 L1 / 是否含期权行情）
2. 沙箱探针策略打印 `get_full_tick('510300.SH')` 完整 5 档字段（对照现 quote.csv 口径一致性）
3. 若曾开通 L2：沙箱内验证 L2 逐笔接口可用性（大QMT 沙箱权限随终端账户走 vs miniQMT 独立授权——需券商客户经理确认，即 93 §11.5"Level-2 权限确认"伏笔的落地动作）
4. 期权链：沙箱内订阅期权合约快照（如沪深300ETF 期权主力），确认 greek 字段（delta/gamma/vega/theta/iv）是否随行情产出
5. 结论回填 §2.2-B：有权限→桥扩期权/L2 dump 立项；无权限→五任务逐表评估 fallback（akshare iv 源/退役停更裁定）
