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

- [x] tick 主链路：tick_subscriber bridge 模式（TICK_SOURCE 环境变量，9/7 已闭环，93 §14.7）（✅09-08 复核加固：TICK_SOURCE=bridge 已持久化 User 级 + guard 子进程实测读 ticks3.csv 入 CH；含 #BRIDGE-WRONG-FILE 修复 ENV_CONFIG→ticks3.csv，commit 待提交，见 §8）
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
- [ ] margin_trading_qmt_placeholder（表不存在）→ 禁用或改 akshare 主源
- [ ] dragon_tiger_qmt_placeholder（表不存在）→ 同上
- [ ] block_trade_qmt_placeholder（表不存在）→ 同上
- [ ] l2_tick_snapshot（CH 空表 0 行 + fallback 循环引用自己 `fallback: miniqmt`）→ 清理循环引用

### §2.5 miniqmt 仅作 fallback 的 6 个【主源仍在，退役后 fallback 死→自动跳过，低优先】
- [ ] futures_position_incremental
- [ ] audit_opinion_incremental
- [ ] futures_term_structure_incremental
- [ ] daily_valuation_full_refresh
- [ ] option_kline_incremental
- [ ] option_kline_full_refresh

## §3 后端代码层

- [ ] scheduler.py：provider 工厂注册 `qmt_bridge` 源（L1099 工厂表/L1104 路径表/L1180 分支）
- [ ] scheduler.py：非交易日守卫 miniqmt 拼写防护（L335-363）扩桥任务语义
- [ ] market_breadth_collector.py：8 处 miniqmt 直连 → 桥数据聚合（依赖 §2.2-D 宽度快照方案裁定）
- [ ] speed_tester.py：32 处——数据源测速器加 qmt_bridge 通道
- [ ] source_health_check.py：miniqmt 探活 → 桥探活（4 处）
- [ ] policy_registry.py / capability_symbol_gate.py / backfill_checker.py / cli.py / capability_validator.py：源登记与门禁里的 miniqmt 语义更新
- [ ] P0-2 钱路：paper_session/intraday_main 下单链切 BrokerInterface 注入（接口已抽象，93 §13 定级"小"）
- [ ] P0-3 对账：recon_runner/broker_settlement_adapter 切桥（同上）
- [ ] miniqmt_channel_manager.py：退役后状态机 dormant/归档策略（保留接口禁真连）
- [ ] ex_core/adapters/__init__.py：adapter 导出与默认装配更新（7 处 miniqmt 字样）
- [ ] reference_data_manager.py / multi_timeframe_fusion.py / corporate_action_adjuster.py / board_lot.py：散点 miniqmt 依赖逐个核查（2/2/2/2 处）
- [ ] 回测域核查：event_driven_engine.py / matching_logic.py 的 miniqmt 字样（疑为注释/常量，确认无运行时依赖即勾）

## §4 前端 7 点

- [ ] F1 components/trade_panel.py：`broker_id="miniqmt"` 默认值 → `qmt_bridge`（L92/L452 两处）
- [ ] F2 components/position_monitor.py：MiniQmtBroker.get_positions() 注入 → 桥文件持仓
- [ ] F3 components/order_book.py：MiniQmtQuoteProvider → QmtFileBridgeQuoteProvider
- [ ] F4 services_registry.py L91：QMT 客户端进程探测 pattern `xtminiqmt|xiadan|qmt` → 实测大QMT 客户端进程名后更新（否则服务总闸假死）
- [ ] F5 web/services/api.js fetchBridgeStatus："miniqmt 存活"信号退役后 UI 语义改"已退役"
- [ ] F6 tick/行情统计页：行数/延迟统计按 `data_source` 分组（miniqmt/qmt_bridge 并存→只剩 bridge，防退役日数字跳水）
- [ ] F7 服务总闸：心跳 `mode` 字段（xtdata/bridge）上屏（tmp/tick_subscriber_biz.heartbeat）

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
| 1 | 2026-09-08 | 闪窗根治：10 个计划任务 wscript+launch_hidden.vbs 包装（含 vbs 参数透传）、register_guard_tasks.ps1 模板防回退、AI-Wrapper-Inject 僵尸实例清理、DataScheduler 补启用、死任务 TickVerify_1306 删除 | 待提交 | 元凶=AI-Wrapper-Inject 每 1 分钟直连 powershell 闪窗；#ARCH-OPS-001 |
| 2 | 2026-09-08 | guard TICK_SOURCE=bridge 持久化（User 级）+ #BRIDGE-WRONG-FILE 修复（ENV_CONFIG sim/real→ticks3.csv，93/93 测试过）+ 误灌 166 万行 9/7 污染数据 ALTER DELETE 清理（9/7 恢复 308,657 行）+ 下午真积压回补（9/8 = 739,952 行） | 待提交 | 事故根因：env 默认路径未随 v19 升级，早间 --bridge-file 覆盖掩盖漂移；事故记录已注释进 tick_subscriber.py |
| 3 | 2026-09-08 | 口径对齐全链实测（持仓 row[7]/[9]/[15]/[18] ✅、五档 dump 25 列 ✅、CH 1 档+Redis 完整 5 档 ✅）+ 本台账更新（§1 勾 2 项/§2.2-D 与 §5 标注进度/新增 §8） | （本提交） | PositionStatics.csv 13 天未更新红旗转 §8 |

## §8 2026-09-08 增量待办（桥切换过渡期，按优先级）

### §8.1 明早（9/9）盘前/盘中观察【P0，bridge 独挑第一个完整交易日】

- [ ] 09:15 跨天轮转三连观察：① ticks3.csv 是否被沙箱重建（size 归零/仅表头）② ticks3.csv.offset 越界自愈是否归零（115,620,192 > 新文件 size → 应重置 0 从头读）③ 09:30 后 CH qmt_bridge 行恢复增长（`SELECT count() FROM c1_market.tick_data WHERE trade_date=today() AND data_source='qmt_bridge'`）
- [ ] 盘中抽查：CH 新行 timestamp 与 wall clock 偏差 <1min（防再吃陈旧 timetag）；桥子进程 biz.heartbeat mode=bridge、errors 无持续增长
- [ ] Redis `tick:*:latest`（db0，现存 147 键为旧 xtdata child 昨日残留）确认被 bridge child 盘中刷新（低优，仅观察）

### §8.2 Owner 动作【P0，9/18 前 MUST】

- [ ] 打开真实大QMT 终端一次，验证 `E:\qmt_bridge\Stock\PositionStatics.csv`/`Account.csv` 自动导出恢复（已 13 天未更新，mtime 停在 08-26 20:50；持仓 API/前端全靠它）

### §8.3 记录与提交【P1】

- [ ] 93 号备忘补 §14.10：#BRIDGE-WRONG-FILE 事故（根因/影响/修复/教训）+ 闪窗根治（#ARCH-OPS-001（历史标签 ARCH-BOOT-WINDOW-FLASH） 全量落地记录）+ 9/9 观察清单
- [ ] commit 待提交清单：tick_subscriber.py（ENV_CONFIG 修复+事故注释）、launch_hidden.vbs（参数透传）、register_guard_tasks.ps1（vbs 模板 ×2）、scripts/run_ttl_rejudge_daily.ps1（新）、scripts/ch/run_optimize_merge_hidden.ps1（新）、本台账

### §8.4 独立小问题【P2，与桥无关】

- [ ] TTLRejudgeDaily 计划任务 9/7 18:05 退出码 1（python 层面，backfill_ttl_metadata.py；每日 18:05 会重复闪红）
- [ ] QUOTE_V17 并入 TICKDUMP3 检查点：9/15 开评（93 §14.9 已落盘 v20 方案路径 A/B）；可选加速路径已呈报 Owner 裁定——明晚出 v20（dump+200ms 热线程照写 quote.csv）→ v20/v17 并行对拍 2-3 天 → 一致则退役 v17，9/18 只剩 TICK_SOURCE 一个切换变量
- [ ] §2.2-B 前置确认项的连带提醒：convertible_bond_list 的 max list_date 停在 09-03 已定性为 monthly_static 月频设计（非故障），10/1 正档观察项（93 备忘已记录）
