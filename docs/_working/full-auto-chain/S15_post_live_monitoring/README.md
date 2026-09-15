---
ttl: task_bound
title: S15 实盘后监控与衰减挖矿文档
session: st-fullauto-20260915
date: 2026-09-15
---
# S15 实盘后监控与衰减（E6 判死/E9 归因/衰减回灌——轻挖登记）

> 骨架定位：转正后闭环，本班**轻挖**=登记现状+欠账即可，边际施工。核心对象：策略衰减
> 认证、绩效归因、实盘后监控回路、E6→E1 反馈回灌。

## 1 现状盘点（自动化状态+file:line 证据）

### 1.1 策略衰减侧认证器——阈值预注册，产出台账不翻册

- `src/zephyr/signal_ashare/strategy_signal/strategy_decay_certifier.py`（**MOD-SIG-150**，
  注意：任务线索写作 MOD-BT-078，经查 MOD-BT-078 实为 `scripts/backtest/
  strategy_screen_query.py` 的策略筛查查询件，本件头注=self 声明 MOD-SIG-150——引用时以
  MOD-SIG-150 为准）：
  - 只读 `c1_backtest.backtest_strategy_screen`（FINAL 每策略最新行的 deflated_sharpe）；
  - 阈值预注册（改动=裁定）：DS≥0.5 且有 OOS→certified / 0≤DS<0.5→probation / DS<0→
    failed / 连续 FAILED_WINDOWS=8 个周扫 failed→retired 建议 / retired 后 DS≥0.5→
    resurrected；
  - 产出=衰减建议台账 JSON（safe_write_text），**不翻转策略域注册表状态**（晋升侧 E0-E9
    归属域管线，边界清晰）；
  - `[STARTUP] imported（周末校准档事件触发；禁 cron 自轮询）`，`[MATURITY] design`；
  - 消费方登记=trading_lifecycle_weekly 任务（capability 分支，
    `src/zephyr/data/implementations/internal_compute_provider.py` L137/L506-507 已登记
    capability 契约）——**但消费执行器/调度接线未落地**（design 成熟度实锤）。
- 相邻件：`scripts/backtest/strategy_lifecycle_advisor.py`（MOD-BT-187）decay_watch 台账
  扫描（decay≥0.5→冻结晋级资格进观察；双窗皆负→reject），manual（S10 §1.2 已挖）；
  sim_deviation_report 连续 breach→decay_proposal（S10 §1.1，判定史存量=0 期）。

### 1.2 绩效归因引擎——实盘运行时侧生产库，未接监控回路

- `src/zephyr/pf_core/core/performance_attribution_engine.py`（MOD-PF-007 / PC-10）：
  Brinson 归因（BrinsonResult L253，total_attribution/is_consistent 自检）+策略降级检测
  （DegradationDetection L279）+拥挤度检测（CrowdingLevel/CrowdingDetection L197/297，
  warn/severe 双阈值）+IC 衰减检测（ICDecayDetectionError L222，ic_decay_threshold L394）
  +风险分解不可用降级（RiskDecompositionUnavailable L216）。AttributionDataIncomplete
  fail-closed。
- 消费边界（S11 §1.5 已定性）：D-PF-CORE/PC-01 实盘运行时生产库——**无调度、无周期触发、
  无报告产出链**，转正前只登记不接线。

### 1.3 实盘后监控现存件盘点

- TradingSession 内：KillSwitchLite 策略级熔断（43 号 §4.3）+C-004 合规闸
  （trading_session.py L701-707，见 S14 §1.4）——**单日止损/熔断在链上**；
- recon_runner（对账）+ async_fill_dispatcher（成交派发）+ qmt_watchdog.ps1（终端看门狗，
  services_registry 8010 看门狗同款模式）；
- warroom 页（web/features/warroom/）：预案→走势匹配→昨日验证，人的监控视图；
- sim 侧日刊/偏离/治理三件（S09/S10 挖过）——**转正后同口径套 live 的监控件不存在**，
  E6/E9 在蓝图层有位、在代码层无件。

### 1.4 E6→E1 反馈回灌——声明未接线

- `config/strategy_production_map.yaml` feedback_loops L383-385：E9→E2 归因回灌、
  E6→E1 衰减反馈**两条均为声明未接线**（S04 挖矿实证，本档确认仍闭环欠账）；
- 衰减侧的"回灌起点"已备：decay_certifier 台账（retired/resurrected 建议）+
  decay_watch 冻结行——缺的是"台账行→E1 假说库标记该因子族衰减"的消费件。

## 2 六向挖矿日志表

| 轮 | 矿脉（方向） | 动作与证据 | 判定 |
|----|-------------|-----------|------|
| R1 | ④后端：衰减认证器 | MOD-SIG-150 阈值预注册+台账边界+design 成熟度；MOD-BT-078 归属澄清（=strategy_screen_query） | **signal** |
| R2 | ④后端：归因引擎 | MOD-PF-007 类面（Brinson/降级/拥挤/IC 衰减 L197-312）；无调度无触发（S11 边界复核） | **signal** |
| R3 | ②下游：建议消费链 | trading_lifecycle_weekly capability 已登记（internal_compute_provider L137/506）但执行器未落地；E6→E1 回灌 strategy_production_map L383-385 声明未接线（S04 实证） | **signal** |
| R4 | ①上游：监控现存件 | KillSwitchLite+recon_runner+warroom+qmt_watchdog；live 口径监控件不存在；S10 判定史存量 0 期 | **signal** |

轮次判定：4 signal / 0 noise（轻挖符合预期——本环节矿脉窄，四向已覆盖衰减/归因/回灌/
监控全对象）。封批。

## 3 业界与开源对照

- **晋升-退役对称门**：业界晋升门=固定观察窗+量化门+人工终裁（S10 §3 已引 quantpedia/
  quantconnect），退役门同构=滚动样本外衰减阈值+连续确认窗+复活机制——本件 DS 三态+
  8 周连续+resurrected 设计与之一致，无需改。
- **归因标准**：Brinson 模型=多策略组合归因业界标准件（MOD-PF-007 已实现+is_consistent
  自检）；拥挤度/降级双检测属同类商业平台（如 AlphaLens 式因子拥挤监测）同款口径，
  实现层已领先于接线层。

## 4 堵点与欠账清单（登记性质，转正后闭环）

| # | 欠账 | 证据 | 边际 |
|---|------|------|------|
| 1 | decay_certifier 无周扫接线 | MATURITY=design；消费执行器缺 | 转正后必还 |
| 2 | E6/E9→E1/E2 回灌未接线 | strategy_production_map.yaml:383-385 | 终局有位，时序未到 |
| 3 | live 口径监控件不存在 | §1.3 | 转正后建（先跑通 S09-S12 同构件到 live 侧） |
| 4 | retired 建议无消费执行器 | 台账产出→注册表翻转的执行件缺 | 需 Owner 门（production→retired=FSM Owner 门） |
| 5 | 判定史存量 0 期 | S10 §4.3 | C2 落地后自然解决 |

## 5 施工项建议（本班边际；主体=转正后闭环）

1. **本班唯一边际件（可选）**：decay_certifier 周扫事件接线——pipeline_events 增
   `strategy_decay_weekly` kind，复用 S10 月度 marker 同款机制挂周窗（30 天线改 7 天），
   handler 子进程跑 `run_strategy_decay_certify`，台账入 `.runtime`→docs/_working 归档；
   验收=周末档触发+台账文件可检索+重放幂等。**若时序紧张可整件后移**（当前判定史为 0，
   早接线也无输入）。
2. **转正后闭环路线图（登记，不在本班）**：①C2 四件套跑熟→S10 判定史累积→decay_certifier
   有输入；②拍板链（C4/C5）稳定→建 live 侧日刊/偏离/治理同构三件；③MOD-PF-007 接入
   月度整装例跑（归因章）；④retired/复活建议消费执行器（FSM production→retired Owner 门
   复用拍板通道）。

## 6 封矿结论

- 矿脉层面：4 signal/0 noise，衰减/归因/回灌/监控四对象现状+欠账登记完毕，封批。
- 方案层面：本班**零必施工项**（骨架定位=轻挖登记）；唯一可选边际=周扫接线（可后移）；
  其余全部**挂起排期**，解锁条件=转正链（C1-C6）跑通且判定史开始累积。按挖后自审闸
  （SOP §6）：现建 live 监控回路属"在错误层位提前建将被覆盖的中间件"——转正未发生，
  监控对象不存在，不施工即是不过度工程。
- 一句话结论：**衰减认证阈值与复活机制已预注册（MOD-SIG-150），归因引擎已生产级
  （MOD-PF-007），缺的全是"转正后才有输入"的接线——本班登记欠账五条，转正后按路线图
  逐件闭环。**

## 7 施工班状态回填（2026-09-15）

- 堵点 5（判定史 0 期）状态更新：C2 已落地（sim_deviation_monthly 月度档挂 30 天 marker），首期判定史将由月度档自动产出，无需人工首跑。
- 其余欠账（decay_certifier 周扫接线/E6E9 回灌/live 监控件/retired 消费执行器）状态不变，维持转正后闭环路线图。
