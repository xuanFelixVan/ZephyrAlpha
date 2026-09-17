---
ttl: task_bound
title: E2E 链路挖干作业簿 st-cleanexam-20260918/C——信号→决策→下单→成交→台账 环节骨架
owner: ZephyrAlpha-Owner
session: st-cleanexam-20260918/C
date: 2026-09-18
status: mining_done_design_ready
safety: 本批纯只读勘察+设计，零真实委托；下单 API 执行路径零触碰
---

# E2E 链路挖干作业簿（行情→桥→决策→执行→回报→台账）

> **一句话结论**：全链路共盘点 **24 环**；骨架同构、件大多在，但有 **6 处断点/半成品**——其中"决策→执行"之间断（编排器 BT-P1-031 未施工，蓝图明文 S7"首版不驱动执行单"=v1 只出声不出手的成文证据）、"回报→台账"半断（execution_report 表+builder 全在但零生产调用方）。
> **真单通道已换代**：miniQMT（xtquant/XtMiniQmt）**2026-09-18（今日）退役**；唯一真单通道=**QmtFileBridgeBroker**（大QMT 沙箱文件桥，HTTP 18901 快路径 + orders_sim.csv 文件兜底，双实例物理隔离 sim/real）。93 号备忘+迁移台账为真源。
> **配套产物**：[smoke_test_design.md](smoke_test_design.md)（100 股模拟盘冒烟设计，只设计未执行）+ [chain_envs.csv](chain_envs.csv)（逐环节机读版）。

## 0. 挖矿日志

| 轮 | 矿脉 | 动作 | 判定 | 关键产出 |
|---|---|---|---|---|
| R1 | 桥与执行层内部反查 | grep passorder/order_stock/xtquant 全仓；读 miniqmt_broker/qmt_file_bridge_broker/integration/qmt_trading_session 全文 | signal | 唯一下单 API 调用点=旧 miniqmt_broker.py:417（今日退役）；新通道 qmt_file_bridge_broker（无 xtquant 依赖） |
| R2 | 退役换代线索 | 读 miniqmt_channel_manager 头注 + 迁移台账 + 93 备忘目录 | signal | RETIRED_DATE=2026-09-18；替代通道 HTTP 18901+文件桥；台账红线 1-3 与 9/17 切换窗口现状 |
| R3 | 决策层骨架 | 读 trading_vision 视觉映射+日度编排器蓝图+plan_engine/judgment_ledger+pipeline_events 接线 | signal | decision_daily 表**不存在**（蓝图 schema 草案 §四.1）；判决三表真落库（c1_market.judgment_*） |
| R4 | 回报与台账段 | 读 fill_handler/G3 测试/execution_report schema+builder/recon_runner/sim_paper_ledger/sim_trade_log schema | signal | execution_report 无生产调用方（半成品）；sim_trade_log=虚拟钱包账本（非券商模拟账户，勿混淆） |
| R5 | 连接状态只读实测 | Get-Process + Test-NetConnection 18901 + E:\qmt_bridge_sim\ 文件 mtime | signal | 模拟大QMT 终端在跑（XtItClient PID 26196）、18901 活、ticks3.csv/quote.csv 02:49 新鲜 |
| R6 | 既有先例 | 读 scripts/tests/smoke_test_qmt_broker.py + scripts/construction/test_qmt_file_bridge_e2e.py + test_qmt_file_bridge_full.py | signal | E2E 先例完整在盘（510300.SH 100 股限价远价）；跌停价申报先例（闭市合法+不成交+可撤） |
| R7 | 外网动作 | 未出网（本批为内部链路普查，无外部引文诉求） | — | 长尾 M-E2E-1 记档（见 §6） |

## 1. 链路环节骨架表（24 环）

> 状态三态：**通电**=生产链路在跑/装配即可用；**半成品**=件在但关键接线缺失；**断电**=未施工/已退役。逐环机读版见 chain_envs.csv。

### A. 行情接入段

| # | 环节 | 入口（文件:行） | 状态 | 数据落点 |
|---|---|---|---|---|
| A1 | 沙箱行情 dump（tick/quote 两策略） | 沙箱侧 TICKDUMP3_v19/QUOTE_V17（E:\qmt_bridge_sim\，93 备忘 §11/§14） | 通电（实测 09-18 02:49 仍在写） | E:\qmt_bridge_sim\ticks3.csv / quote.csv（29 列 5 档） |
| A2 | 桥尾读采集 | src/zephyr/data/tick_subscriber.py:1453（BridgeTickSource）；start_bridge :1785-1789；_on_backup_tick :366 | 通电（TICK_SOURCE=bridge 用户级 env 已设，9/18 退役日 SOP 复跑确认） | WAL→CH c1_market.tick_data（1 档）+ tick_depth_5（五档，TICK_DEPTH5 旁路） |
| A3 | 桥数据源 Provider（能力注册） | src/zephyr/data/implementations/qmt_bridge_provider.py:202 connect/:223 health_check/:261 probe | 通电 | tick=no-op 防双写；kline 族=ch_tick_kline tick 聚合合成（c1_market.kline_1min~60min）；auction=ch_auction_derive 派生（c1_market.auction_snapshot/book） |
| A4 | 旧 miniqmt 行情通道 | src/zephyr/data/implementations/miniqmt_provider.py（xtquant） | **今日退役**（tasks.yaml 仍 64 个 source: miniqmt，靠 fallback 自动 failover+退役日 SOP，如实记档） | （历史囤货 c1_market.tick_data 等） |

### B. 决策层（信号→决策）

| # | 环节 | 入口（文件:行） | 状态 | 数据落点 |
|---|---|---|---|---|
| B1 | 信号生产者（打板负载） | src/zephyr/ex_core/daban_load_producer.py（盘后批产，事件驱动非周期） | 通电 | c1_market.market_daban_engine_load |
| B2 | 判决账本链（发射器） | src/zephyr/plan_engine/judgment_ledger.py:81-89 + pipeline_events.py:747-786/:835-851（60min bar/daily_kline 唤醒） | 通电 | c1_market.judgment_daily_plan / judgment_intraday_market_state / judgment_next_day_forecast |
| B3 | 日度编排器（decision_daily 一库） | 蓝图=docs/_working/trading_vision/2026-09-16-daily-orchestrator-blueprint.md（BT-P1-031，S1-S7 序列 §二） | **断电（蓝图草案未施工）**——S7 成文"首版不驱动执行单" | c1_backtest.decision_daily（**表不存在**，schema 草案） |
| B4 | L4 组合层 | pf_alloc（alloc_budget_daily 经 pipeline_events maybe_emit_pf_alloc_daily 在跑）；总闸语义=TDM-E-L1 | 半成品（有件未全面接电，裁定#257②挂触发） | c1_backtest.alloc_budget_daily |
| B5 | "只出声不出手"安全态 | 蓝图 S7 分发面=播报前缀+仪表盘+留痕，不产执行单 | 成文设计（非事故） | 播报/告警面 |

### C. 执行层

| # | 环节 | 入口（文件:行） | 状态 | 数据落点 |
|---|---|---|---|---|
| C1 | 会话一键装配 | src/zephyr/ex_core/qmt_trading_session.py:56（_VALID_ENVS real/sim，构造期校验） | 半成品（draft，消费=construction 脚本） | — |
| C2 | 装配件（双实例隔离） | src/zephyr/ex_core/adapters/qmt_file_bridge_integration.py:46（enable_real 默认 False/enable_sim 默认 True） | 通电 | — |
| C3 | 订单管理器 | src/zephyr/ex_core/order_manager.py:131（create_order :229/submit_order :285/cancel_order :381/_on_fill :493） | 通电 | 内存聚合+Fill 回调 |
| C4 | **文件桥 Broker（唯一真单通道）** | src/zephyr/ex_core/adapters/qmt_file_bridge_broker.py:319（ENV_CONFIG :338-351；connect :405；submit_order :456；_append_instruction :605=HTTP 快路径+文件兜底；_http_post_order :619 POST 127.0.0.1:18901；cancel :508；query :523） | 通电（HTTP 实测 32ms 中位；文件兜底 5.7s） | E:\qmt_bridge_sim\orders_sim.csv（指令）/ ack_sim.csv（回执）/ Stock\*.csv（柜台官方导出） |
| C5 | 柜台全量镜像 | 同上 :115（CounterStateMirror：挂单/持仓/资金/当日成交全量，含手动单） | 通电 | 内存镜像←Stock\Order.csv/PositionStatics.csv/Account.csv/Deal.csv（GBK） |
| C6 | 旧 miniqmt 下单通道 | src/zephyr/ex_core/adapters/miniqmt_broker.py:149（order_stock 调用 :417） | **今日退役**（代码保留 dormant 作契约参照，禁真连） | — |
| C7 | 通道状态机（Fail-Closed） | src/zephyr/ex_core/miniqmt_channel_manager.py:66（RETIRED_DATE :72-75；五态状态机） | dormant（接口保留=测试消费+桥重连参照实现） | — |
| C8 | 模拟/实盘模式门 | src/zephyr/ex_core/live_simulation_switcher.py（MOD-EX-035：构造即 SIMULATION；sim→live 需 Owner 一次性令牌，Fail-Closed） | 通电 | SwitchRecord 留痕（令牌只存 sha256 指纹） |
| C9 | 执行引擎（TWAP/VWAP/SOR） | src/zephyr/ex_core/execution_engine.py + ex_sor | 半成品（件在，未见生产接线） | — |
| C10 | 订单 Saga（超时补偿） | src/zephyr/ex_core/order_execution_saga.py:115/136 | 件在（未见生产接线） | — |

### D. 安全件

| # | 环节 | 入口（文件:行） | 状态 | 说明 |
|---|---|---|---|---|
| D1 | 交易侧五级熔断 | src/zephyr/trading/trading_contracts/risk/trading_kill_switch.py:52（五级）/:119 trigger/:127 reset | 通电（数据模型+触发） | **交易资金安全真源**（非 agent 级） |
| D2 | Agent 行为熔断 | src/zephyr/security/access_control/kill_switch.py（MOD-INF-018） | 通电 | **纯进程内存态，与交易资金无关**（头注 P1-2 澄清）——冒烟断言用 D1 不用 D2 |
| D3 | 下单前校验链 | ex_core/board_lot.py（整手真源）+ price_cage.py（笼子夹边）+ pre_execution_checker | 通电（broker 内置） | 桥 broker 无盘口→笼子降级 UNKNOWN 通过 |
| D4 | 盘中风控编排 | src/zephyr/ex_core/risk_layer_orchestrator.py（回撤级联/VaR） | 件在 | 交易侧纵深 |

### E. 回报段（成交→报告）

| # | 环节 | 入口（文件:行） | 状态 | 数据落点 |
|---|---|---|---|---|
| E1 | 回报双源 | 沙箱 EXEC v16.4 写 ack_sim.csv + QMT 官方导出 Stock\Deal.csv | 通电 | ack 回执 + 柜台镜像 |
| E2 | 成交回调→订单聚合 | register_fill_callback → order_manager._on_fill :493 → src/zephyr/ex_core/fill_handler.py（fill_id 幂等/JSONL 落盘 fills_dir） | 通电（进程内） | **JSONL 文件（G3），非 CH** |
| E3 | 盘后成交兜底 | 旧通道 miniqmt_broker.query_trades_today :580；桥通道=CounterStateMirror._deals（Deal.csv） | 通电 | 40 号戒律：禁回调内同步查询（死锁） |
| E4 | 执行报告 CH 表 | 表=schemas/categories/intraday/market_execution_report.py:91（c1_market.execution_report）；builder=src/zephyr/ex_core/execution_report.py:65 build_execution_report | **半成品**：全仓 grep 零生产调用方——表/契约（CTR-P1-007）/消费侧（TCA、ExecutionReportSource）全在，产出侧无人写 | c1_market.execution_report（空转） |

### F. 台账段（对账/账本）

| # | 环节 | 入口（文件:行） | 状态 | 数据落点 |
|---|---|---|---|---|
| F1 | 日终对账 runner | src/zephyr/trading/recon_runner.py:125（ReconBrokerSource 协议：query_trades_today+get_positions）+ ex_core/eod_reconciliation.py + position_reconciler.py | 件在（runner 就绪） | 对账结果/归因 |
| F2 | 模拟盘虚拟钱包账本（**独立于券商桥，勿与券商模拟账户混淆**） | scripts/backtest/sim_paper_ledger.py（方案 C 钱包引擎，crisis 闸 L3 复用 pf_alloc.crisis_gate） | 通电（pipeline_events :69-70/:114-118 事件接线 sim_ledger_daily→sim_journal_daily） | c1_backtest.sim_trade_log（事件溯源真源）/ sim_pocket_daily / sim_platform_journal / sim_attribution_daily / sim_pocket_daily 族 |
| F3 | 决策快照表 | 蓝图 §四.1 | **不存在**（=B3 断点的落点面） | c1_backtest.decision_daily（草案） |

## 2. 六向台账

### ①上游（喂给链路的信息实底）
- 行情三通道实测活：ticks3.csv/quote.csv（02:49）、HTTP 18901、Stock\ 官方导出（09-17 收盘后 15:39，正常节奏）。
- 判决链上游：60min bar/daily_kline SUCCESS 唤醒（pipeline_events SIM_DAILY_WAKE_TASKS 子串机制）——血管已通。
- 缺口：tasks.yaml 64 个任务主源仍挂 miniqmt（今日退役日）——26 个有 fallback 自动保命、17 个真在产无 fallback（K 线族已由桥合成 ch_tick_kline 续命，裁定③方案 b 已批）、其余按台账分档处置。

### ②下游（链路输出喂给谁）
- 判决三表 → judgment_settler 结算 → brier 校准。桥执行面 → CounterStateMirror → 持仓监控 Tab（position_monitor create_position_broker 工厂已并列两通道）。
- execution_report 表下游（TCA/归因）在等 E4 生产者接线——下游齐、上游断，半成品定性依据。
- sim_trade_log → sim_pocket_daily/sim_platform_journal/偏离月报（sim_deviation_report）。

### ③算法/机制
- 双通道容错（93 §12.2/§12.5 实证）：HTTP 快路径（32ms）失败 fail-open 降级文件桥（5.7s）；午休/收盘沙箱冻结期 HTTP 成功不响应→broker 2s 超时降级写文件，沙箱复活后补消费（12:04-13:00 实证 4 笔）；HTTP 偶发丢请求（1/5 无 ack）→客户端 8s 无回执重写文件通道。
- 幂等三件：broker _idempotency_map（idempotency_key→order_id）、EXEC 侧两阶段 #SENDING→#DONE 3 重试、FillHandler fill_id 去重。
- 环境辨识权威法：TCP 配对（tick_subscriber.py:979 _identify_qmt_peer_via_tcp）>进程路径>LISTEN 端口（二义禁用）。

### ④后端
- 断点件施工单（本批只登记不施工）：①BT-P1-031 编排器+decision_daily 表（蓝图齐，待过审施工）②build_execution_report 生产接线（挂点=E2 回调链完成后聚合写 CH）③Fill CH 持久化（现 JSONL）。
- 冒烟测试已可施工（设计见 smoke_test_design.md，前置条件今日实测满足）。

### ⑤前端（只登记）
- qmt_bridge_health.py 组件 + position_monitor（F2 工厂）+ api.js bridgeStatus（9/18 后 miniQMT 卡片显"已退役"占位）——已在迁移台账 §4 覆盖，无新增。

### ⑥数据字段
- 桥文件契约字段核对：orders_sim.csv 7 列（order_id,action,symbol,side,qty,pricetype,price，ASCII）；ack 状态机 SENT/CONFIRMED/FAIL/CANCEL_SENT/RETRY；柜台状态中文枚举 已报/已报待撤/部成/已成/已撤/废单（_COUNTER_STATUS_MAP 全量映射在 broker）。
- sim_trade_log 13 列（signal_reason 判据快照列=AI 复核位）。

## 3. 模拟/实盘鉴别（一句话+机制）

**一句话**：账户 `8886156677`=模拟盘（目录 E:\国金QMT交易端模拟 / E:\qmt_bridge_sim\），`8887871993`=实盘（E:\国金证券QMT交易端 / E:\qmt_bridge\）；结构化真源=config/qmt_environments.yaml（#ARCH-QMT-ENV-DISAMBIG-001），连接参数=config/.env.qmt（QMT_SIM_*/QMT_REAL_*）。

机制三层：①**静态**——qmt_environments.yaml 双槽位（sim safety_level=L blocks_live_trading=false / live 槽 safety_level=H blocks_live_trading=true，live 槽 account 字段留空未启）；②**运行时**——进程路径含"模拟"→sim；双终端在线用 TCP 配对法（LISTEN 58610 二义禁用）；③**代码内**——QmtFileBridgeBroker.ENV_CONFIG 双实例物理隔离（broker_id=qmt_sim/qmt_real）+ QmtFileBridgeAssembly enable_real 默认 False + LiveSimulationSwitcher sim→live 需 Owner 一次性令牌 Fail-Closed。冒烟双重保险设计见 smoke_test_design.md §5。

## 4. 冒烟测试 tonight 可行性判定（诚实口径，实测 2026-09-18 02:52-02:57）

| 前提 | 实测 | 判定 |
|---|---|---|
| 模拟终端在跑 | XtItClient.exe PID 26196，Path=E:\国金QMT交易端模拟\bin.x64\XtItClient.exe；**无 XtMiniQmt 进程**（已退役，无双终端二义） | 满足 |
| HTTP 桥活 | Test-NetConnection 127.0.0.1:18901 = True | 满足 |
| 桥文件族 | E:\qmt_bridge_sim\ 存在；ticks3.csv/quote.csv mtime=09-18 02:49（活）；orders_sim.csv=表头（09-04）；ack_sim.csv 末次 09-15 15:18；Stock\ 官方导出 09-17 15:39 | 满足 |
| 交易时段 | 当前 02:57，非交易时段（今日周五 2026-09-18 为交易日，集合竞价 09:15 起） | **不满足**——影响终态验证段 |

**结论**：tonight 可执行"连接→断言→资金持仓查询→下单受理（HTTP/文件双路径择一实测）→回执链验证"；**成交/废单终态与撤单确认必须等 09:15 后**（沙箱 handlebar 冻结期行为=93 §12.5 已实证：下单会排队补消费，非丢失）。故设计为两段式：今晚跑段一（零下单开关），明早开盘跑段二（下单→终态→台账→清理）。**本批只交设计，执行留施工阶段。**

## 5. 断点清单（哪几环断、断因）

| # | 断点 | 断因定性 | 处置建议 |
|---|---|---|---|
| 1 | B3/F3 决策→执行（decision_daily 不存在） | **有意设计**：v1 只出声不出手（蓝图 S7 成文），非事故 | 挂起排期：BT-P1-031 按蓝图施工解锁 |
| 2 | E4 execution_report 零生产调用方 | 施工缺口：契约/表/消费侧齐，产出接线漏 | 挂起排期：E2 回调链后聚合写（1 会话级） |
| 3 | E2 Fill 落 CH 缺失 | 现仅 JSONL+柜台镜像，CH 无成交流水 | 同上，可与 2 同批 |
| 4 | A4/C6 miniqmt 通道退役 | 外部政策（券商 9/18 关停），替代件已就位 | 已裁定封存（93 备忘），今日按退役日 SOP 复跑切换 |
| 5 | B4 L4 组合层未全面接电 | 裁定#257②触发条件未满足 | 挂起（有明确解锁条件） |
| 6 | C9/C10 执行引擎/Saga 无生产接线 | 上游 B3 断导致无调用方 | 随 B3 通电自然接通 |

## 6. 长尾矿脉

- **M-E2E-1**：EXEC v16.4 沙箱策略本身（E:\qmt_bridge_sim\ZEPHYR_EXEC_v16.txt）与 v21 期权扩桥草稿——沙箱侧代码不入 repo，契约漂移风险靠运行时探针兜（miniqmt_order_link_probe 已有），暂不挖。
- **M-E2E-2**：93 备忘 §13 长期路线图（miniQMT 退役后三层预案/迪雅备胎）——已归档在 93 备忘内，不重复挖。
- **M-E2E-3**：qmt_trading_session（C1）与 BT-P1-031 编排器的对接形态（策略层 Session 化 vs 编排器直驱）——B3 施工时必答题，本批只登记。

## 7. 挖后自审闸（三态裁定）

- **北极星**：终局=Owner 一人+100% AI 自制全自动交易链路；本批把"链路到底通到哪一环"从模糊直觉变成 24 环逐环实名状态表，并交付模拟盘冒烟设计——消灭"链路是否真通"的人工排查环节，且冒烟是执行面通电（策略转正审批前）的必要验证件。
- **过度工程三问**：①收益=断点清单直接给出施工排序（execution_report 接线→编排器），避免 Owner 盲批工时；②已有产物覆盖=否——迁移台账管数据源换代、93 备忘管桥操作、vision 映射管决策层，**无任何一份文档管"E2E 全链逐环通电状态"**，本簿补位；③成本=本批 1 会话纯只读，零代码零配置变更。
- **三态出口**：
  - **施工**：smoke_test_design.md（设计已成，施工阶段执行段一/段二）。
  - **挂起排期**：断点 1/2/3/5（各有解锁条件，见 §5 处置列，入库待 Owner 排期）。
  - **封矿确认（既定裁定的追认，非新封）**：miniqmt 通道（断点 4，93 备忘+迁移台账已裁定，本批仅核实状态一致性）。
- **红蓝预登记**：本簿所有"通电"判定基于代码静态读+文件 mtime+进程/端口只读探测，**未做任何真实委托与回报回放**——冒烟施工阶段的段二才是链路活体证明；若段二失败，本簿 §1 状态表以冒烟日志为准修订。
