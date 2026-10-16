---
ttl: permanent  # st-docconsol-20261014 改：原 task_bound 随 _working 搬迁落 _archive permanent zone 按 DCR-003 转 permanent（正文字节零改动）
session: st-infoaxis-20261013
date: 2026-10-13
title: 信息供给轴 P0 作业簿·日内做T·Tick 域（第六域·Q9 追批）
status: mining_sealed_pending_gate
goal_block:
  goal_statement: 持有中增效——做T资格门＋做T信号集＋增厚读数（逐笔期望增益跟踪）
  output_contract: 做T资格判定＋三策略信号集＋逐笔期望增益读数面（增厚判据=逐笔期望增益口径，成本后）
  exam_ref: 增厚判据（逐笔期望增益，成本模型双边佣金＋印花税＋冲击≈0.1%/次；样本外历史窗＋模拟盘实检两段）；condaxis T0 条件矩阵互引
  campaign_ref: st-infoaxis-20261013（裁定#516 Q9 做T第六域；Q10 L2 不开采集）
---

# 日内做T·Tick 域作业簿（15_intraday_workbook.md）

## §1 问题定义（它出什么）

持仓期间用日内波动增厚收益：**资格门（哪些票/哪些天可做T）→ 信号集（何时买回/卖出）→
闭环读数（每笔做T的期望增益跟踪）**。日终净持仓不变（buy-first/sell-first 标准 D41，
正T/反T 词禁用）。输出挂 TDM-P-P2-01/02/03 与 L3-11-1/2 接线。

## §2 输出契约 v0

```
做T资格门（P2-01）：每票每日 资格判定{状态门/振幅门/成本门/时段准入}（t1_sellable 五道门装配）
做T信号集（P2-02）：三策略（冲高回落/盘口失衡/VWAP 回归）各出 {方向, 触发时刻, 目标股数, 预期增益分}
增厚读数（P2-03）：逐笔做T记录 {entry_ts, exit_ts, 股数, 毛增益, 成本, 净增益}→
  滚动逐笔期望增益（E[gain|策略,状态]）＋增厚年化读数；14:50 强平核对＋股数不变成本降判定
```

## §3 外部对标（2026-10-13 全网搜）

| 来源 | 可借鉴点 |
|---|---|
| 财联社/证券日报/36kr（券商 T0 算法实践） | 增厚现实锚定年化 6-10%、震荡市更优；成本≈0.1%/次设净收益门槛 |
| 海通"海量"专题 131 | 竞价量比分组日收益 0.27/0.19/0.12%——竞价特征有信号但只用 9:20-9:25 不可撤段（规避 9:15-9:20 可撤单诱多污染，与 MOD-SIG-089 BAIT 族呼应） |
| Cont-Kukanov-Stoikov OFI (SSRN 1712822) | 一档 OFI 与中间价变动线性——tick_data 仅一档也能先做盘口失衡特征 |
| Stoikov Micro-Price (SSRN 2970694) | imbalance 加权公允价＝短周期估计器，特征带时衰（秒-分钟级） |
| hftbacktest (GitHub nkaz001) | tick 回测防前视标杆：排队位置＋feed/order 延迟显式建模，禁"价格触即成交"——QMT 桥 3-5 秒延迟进回测的同族纪律 |
| 掘金/知乎 miniQMT 实盘经验 | 模拟盘即时成交无排队、实盘以交易所回报为准——上线路径=回测→模拟盘实时验证→小资金实盘三步校准 |

## §4 仓内四层盘点（六向台账·前四向）

### 4.1 数据面（审计第一优先，live 实查）
- **主表 c1_market.tick_data（DS-195，data_asset_registry.yaml:8346-8375）＝3 秒快照仅买卖
  一档**（非逐笔、非五档；Owner 2026-09-12 勘正），15 字段，注册面 84.2 亿行/实测 38.8 亿
  （f30 记 89.5 亿口径差在册），分区 2025-01-01 起；列契约=ch_tick_replay.py:59
  （timestamp,price,volume,amount,bid_price,ask_price,bid_volume,ask_volume；一档，2-5 档填 0）。
- **五档在旁路表 c1_market.tick_depth_5**（30 列，tick_subscriber.py:515-542），9/18 桥流起
  逐日自积。写链：tick_subscriber.py（xtdata subscribe_quote 回调→queue→WalWriter→CH；
  心跳 tmp/tick_subscriber_biz.heartbeat:89）。
- **QMT 桥 tick 路径**（c351_migration_plan.md:18-19,76,118）：桥 tick 全表止于 2026-09-15、
  仅 140 万行，比 miniQMT 日均 2100-3000 万行薄 5-100 倍＝覆盖洞；分钟 K 族 16 任务留登不切；
  tick_data_snapshot 桥 capability=no-op 零行防双写。
- **Owner Q10 口径（裁定#516）**：miniQMT 模拟盘常挂在跑=实时源；QMT 桥可取 tick 五档、
  慢 3-5 秒——**桥数据进回测必须计入 3-5 秒延迟（防前视红线）**；旧"清退后无在跑源"作废。
- **断档缺口清单**：A02 PIT 登记=l9_readiness:114（TDX 分笔仅近交易日，历史断档不可补）；
  known_data_gaps.yaml:56（tick 2026-06 录制中断＋5204 万指数坏行）、:887（auction 202606
  前缺口）、:1345（09-18 清退过渡日竞价真空）。
- **竞价表**：auction_snapshot（窗口末态每股一行）＋auction_book（逐拍五档），由
  ch_auction_derive.py 从 tick_depth_5/tick_data 派生窗口 [09:15,09:26)，现势 47 密集日
  （2026-06-01~09-16，25.16 万行）；**9:15-9:25 挂撤单过程史任何渠道不存在，只能桥流自积**。
- **断线监测读数面现状**：tick_subscriber_biz.heartbeat＋tick-biz-watchdog 盘中无 tick 周期
  重订阅（tick_subscriber.py:8）；supply_sentinel.py:58 心跳腿＋盲点显性声明（min_rows/
  fill_ratio 三腿）；前端 qmt_bridge_health.py:95；#ARCH-352：health 跳过路径无 failure json
  ＝静默断供隐患，23:00 integrity 聚合是唯一兜底——**读数面设计须补 failure json 落盘**。

### 4.2 模块面
- MOD-DATA-063=intraday_sentiment_loop.py（单拍 run_once 读 market_breadth_snapshot 分钟
  快照→情绪分析→prediction_log 落库＋板块聚合，fail-open，调度族挂 P0-5 SOP 未注册）。
- MOD-SIG-089=auction_microstructure_analyzer.py（纯函数七族特征→GRAB/BAIT/PRESS/NEUTRAL
  四族；**候选消费方盘前计划/打板监控未接线** wiring_status:exempt）。
- MOD-SIG-093=intraday_volume_orderflow.py（日内 VP/CVD 背离/VPIN 纯函数）。
- D_EXEC_SIM=almgren_chriss_impact_model.py（MOD-EXSIM-001 临时＋永久冲击＋参数估计器），
  **已被 backtest matching_engine.py:778-804 消费为冲击真源**。
- TDM-P-P2 四节点（yaml:3319/3360/3405/3445）：P2-01 资格三道门（注释升级五道门＋绝对金额
  制成本门 s(N)＋时段准入矩阵 D58/D111，module_ref=t1_sellable.py MOD-POS-028）；P2-02 三策略
  调度（module_ref=t_trade_coordinator.py MOD-SELL-018 已落码 proposed）；P2-03 闭环判定
  （5 分钟核对＋14:50 强平＋股数不变成本降=成功，module_ref=t0_trading_pipeline.py
  MOD-SIG-090）；P2-04 减仓优先级＞做T。

### 4.3 接线面
- 现状＝**纯函数库互不接线**：wiring_registry.yaml:123-146 C-012 做T/CAND-TESTB-008 均
  exempt。t0_trading_pipeline 复用 MOD-SIG-068 信号、executor 注入契约"生产接线 MOD-SELL-018
  留集成批"（t0_trading_pipeline.py:4,20）；t_trade_coordinator 唯一上游消费者=
  core_satellite_allocator.py:46（注释级）。执行仿真产出（Almgren 冲击）消费方=回测撮合引擎
  而非做T链。竞价侧真实链=plan_engine/auction_hit_recorder（MOD-PLAN-015）＋
  scenario_planner 消费 auction 表。做T Agent t0_trader_agent.py 在 autonomy_core
  （wiring_registry.yaml:430）。
- 考卡 L3-11-1（竞价量比）blocked_on_data：缺 2019-2026-05 auction_snapshot；L3-11-2（5 分钟
  涨速）blocked：缺 2019-2021-08 kline_5min。

### 4.4 词表面
- terminology_glossary.yaml:1003-1014：buy-first/sell-first 系统标准（D41），正T/反T 禁用；
  做T=PT-06 purpose_tag＋排班表（#388）。「增厚」非做T域专词（EPS/样本/夏普语境复用——
  读数面命名须消歧，做T语境用"逐笔期望增益"）。
- grid_t0_conditional_v1＝T0 条件矩阵数据包（t0_condition_matrix_v1.meta.yaml）：1,816 日×
  18 列（2019-04-01~2026-09-21），轴=t1_six_phase×t1_amp_bucket3×情绪/宏观门，闭卷窗
  2019-01-04~2025-09-09，20 条件胞 15 胞过 30 日地板——**condaxis 侧资产，本域消费非重建**。

## §5 六向台账（后两向）

### 5.5 判据面
- 增厚判据=逐笔期望增益口径（裁定#516）：每笔净增益（成本后）滚动 E[gain|策略×状态胞]，
  阈值看数前冻结呈批；测量纪律同 Q1 四条（成本后/全期连续/样本外/双达标防类现金）。
- 回测窗分层：一档窗（tick_data 2025-01 起）＋五档窗（tick_depth_5 2026-09-18 起，桥延迟
  3-5 秒计入撮合）；断档窗声明（2026-06/09-18 两窗剔除）；竞价特征只用现势窗＋自积，
  L3-11-1 考卡改现势窗重立（blocked_on_data 解除路径=窗改窄而非补史）。
- 撮合防前视：禁价格触即成交（hftbacktest 纪律），到达时点后簿态＋排队消耗；一档窗用
  bid/ask 一档＋价差惩罚近似。

### 5.6 消费面
- 挂条件轴：T0 条件矩阵（grid_t0_conditional_v1）条件胞=做T调度的状态输入（condaxis 侧
  定条件，本域执行）；信息轴事件=标注不占格。
- 挂持仓流：P2-01 资格门→P2-02 信号→P2-03 闭环读数（TDM 级联边在案 yaml:6287-6308，
  legacy-unaudited 待升）。
- 挂执行仿真：Almgren 冲击模型接做T撮合成本（复用真源不重建）。
- 断线读数面：挂 l9_readiness A02 行＋supply_sentinel 心跳腿（failure json 补丁=本域
  P2 数据面施工项）。

## §6 病灶诊断（自审闸输入）

| # | 病灶 | 定级 | 处置走向 |
|---|---|---|---|
| T1 | 纯函数库互不接线（P2-01/02/03 模块全落码、wiring exempt、executor 留集成批） | 阻断级 | P2 主施工：三模块接线＋级联边 audit 升级 |
| T2 | tick_data 仅一档 3 秒快照（五档 9/18 起自积）——盘口类策略历史窗受限 | 结构级 | 分层窗设计：一档窗先行（OFI/微价格一档可算），五档窗自积滚动扩 |
| T3 | 竞价史 9:15-9:25 过程不可补（任何渠道不存在） | 结构级 | 现势窗＋自积；L3-11-1 考卡改窗重立 |
| T4 | #ARCH-352 health 跳过路径无 failure json=静默断供 | 阻断级 | P2 读数面施工：failure json 落盘＋supply_sentinel 三腿补全（模拟盘挂机属脆弱源，Owner 口径） |
| T5 | 桥延迟 3-5 秒未进撮合模型 | 红线级 | P2：五档窗撮合强制加 3-5s 延迟（防前视红线，裁定#516 Q10） |
| T6 | 增厚读数面缺失（逐笔期望增益零读数） | 缺口级 | P2 新建 goal_readiness 同族读数表（Q6 联动） |
| T7 | 做T语境"增厚"词与 EPS/夏普语境撞名 | 卫生级 | 词表登记：做T语境统一"逐笔期望增益" |

## §7 待裁项（进 P1 总表）

| # | 项 | 选项 | 建议默认 |
|---|---|---|---|
| T-A | 增厚判据阈值（逐笔期望增益门槛＋样本外窗长） | 看数前冻结呈批 | 成本后逐笔期望增益>0 且 95%CI 下界>0；窗=滚动 60 交易日 |
| T-B | L3-11-1/2 考卡解除路径 | A 改现势窗重立；B 等历史自积 | A（窗改窄即刻可考，B 作滚动增强） |
| T-C | 一档近似撮合的滑点惩罚系数 | 看数前冻结呈批 | 按一档价差分布分位数预注册 |
| T-D | 做T Agent（autonomy_core t0_trader_agent）上线时机 | 回测绿后模拟盘；直接模拟盘 | 回测绿后模拟盘（三步校准纪律） |

## §8 车道回报存档

- 仓内四层审计：agent_73844398（2026-10-14 00:0x，live 实查行数/列/断档/读数面全锚点）
- 外部对标：agent_c0b387b6（券商 T0 实践/竞价异象/OFI·micro-price/hftbacktest/miniQMT 社区经验）

## §9 自审闸三态裁定（封矿）

- [x] 六向台账齐（数据/模块/接线/词表/判据/消费）
- [x] 数据面审计第一优先完成（双源口径/延迟/断档清单/读数面现状全钉死）
- [x] 病灶七条全定级（含两条红线级：T4 静默断供、T5 桥延迟防前视）
- [x] 与 condaxis T0 条件矩阵互引不重建；与 Q6 goal_readiness 读数面联动
- 状态：**过闸·封矿**
