---
ttl: task_bound
title: "策略13张实弹滚上执行计划"
owner: st-datasop-20260930
language: zh
status: active
version: "1.0.0"
date: 2026-10-04
---

# EXEC-D4 策略 13 张实弹滚上执行计划

> **依据**：Owner 已批 13 张实弹转正（6 挂载卡=L13 §三 + 7 新 verified 卡=AUDIT_D 0-5 附注）。本计划只做排期与步骤设计；卡状态翻转/实弹开关由执行队按本计划持 Owner 批件操作。红线执行器（4h 熔断/日黄红线，`daily_pnl < -0.03*aum → reduce_only`，trading_kill_switch.py L83 实证）为总闸，全程在岗。
> **数据源**：strategy_registry.yaml（13 卡字段全核）｜CH c1_backtest.strategy_screen（CAND 键桥，L13 §七法）｜sim_pocket_daily/sim_trade_log｜C5 聚类对质报告（日净收益 |ρ|>0.6 实测聚类，2026-09-13/15）。

## 1. 相关性分组矩阵（数据说话）

实测与推断依据：①同台账键=同一收益序列 ρ≈1；②C5 首批实测（35 策略日净收益聚类）；③因子暴露推断（标注"推断"）。**同组=禁止同波**。

| 组 | 卡 | ρ 证据 | 域/周期 |
|---|---|---|---|
| A 恐慌反弹（指数超跌反转择时） | E-TIMING-001 / VREV-001 / VREV-025 | **ρ≈1.0（同键 CAND-e3da6fa71af1，同序列）** | 反转·指数·波段20日 |
| B 指数趋势跟踪 | MOMTREND-002 / MOMTREND-033 | **ρ=0.75（C5 实测：DMI 对 300ETF 双均线替身）** | 动量·指数·波段信号驱动 |
| C 蓝筹多头/超卖回归 | VREV-026 / VREV-027 | **ρ=0.713（C5 报告 L321：bluechip_ma 标 redundant_of=VREV-026）** | 反转/动量·蓝筹·波段 |
| D 小市值多因子 | TSMALL-001 / MF-098 / MF-099 | 高（推断：small_cap_hl/snake_cap/小市值段同暴露，无实测 ρ） | 多因子·小市值·月频 |
| E 月频价值 | VAL-001 | 中（推断：与 D 同月频选股但 PB×ROE 因子独立；小市值↔低PB 在 A 股中高相关，跨波错峰处理） | 价值·全市场·月频 |
| F 个股突破 | MOMTREND-019 | 低（C5：替身 a4543012b464 单成员簇） | 动量·个股·尾盘竞价 |
| G 日内打板 | DABAN-023 | 低（单成员簇，日内-次日，换手 0.37） | 打板·个股·日内 |

跨组残余相关：A↔C 均为指数级反转（C5 中 e3da 单成员簇=ρ<0.6，允许异波同场，联合回撤并账监控）；B 与 A 部分时段对冲（趋势门 vs 超跌反弹）。

## 2. 三波排期（滚上矩阵）

核心解：**恐慌族 A 三卡恰好铺满三波各 1 张、小市值族 D 三卡恰好铺满三波各 1 张**，配合信号级额度合并闸（§4），同族暴露任一时刻只计 1 份预算。

| 波 | 卡（域组） | 上线前置 | 观察期出场→升级条件 | 降级/回滚条件 |
|---|---|---|---|---|
| 波 1 | E-TIMING-001（A）、TSMALL-001（D）、DABAN-023（G） | 三域正交（指数择时/月频选股/日内打板）；三证/双窗成绩最硬 | 观察 **5 个交易日**：零熔断、卡级回撤<阈值（§5）、滑点<模型 1.5 倍 → 升满额定仓 | 任一破→该卡 suspended，波 1 延长至补足 5 个达标日 |
| 波 2 | VREV-001（A）*、MOMTREND-002（B）*、MOMTREND-019（F）*、VREV-026（C）、MF-098（D） | * 三卡 status=candidate 且 code_path 空：**前置 gate=代码化 quantized + frozen 写死 + 卡级考试过**；未过则当波顺延、空位不递补 | 同波 1 条件；VREV-001 与波 1 E-TIMING-001 同键——启用信号级额度合并闸，双卡合计暴露≤1 份预算 | 同波 1 |
| 波 3 | MOMTREND-033（B）、VREV-027（C）、MF-099（D）、VREV-025（A）、VAL-001（E） | 波 2 全员出观察期；VREV-025 同键合并闸生效（与 E-TIMING-001/VREV-001 合计≤1 份预算） | 同前；A 族三卡三波全部在场后，合并预算回撤超单卡阈值 1.2 倍即全组降档 | 同波 1 |

排期节奏：波 N+1 在波 N 观察 5 交易日达标（或达标升满）后启动；单波内 5 卡同日上线、首笔试单错时 15 分钟。全程预计 3 周（3 波×5 交易日+缓冲）。

## 3. 每卡一览（考试成绩与 sim 实证，CH 2026-10-04 读数）

| 卡 | status/lifecycle/algo | IS Sharpe | OOS Sharpe | maxDD | 台账键 | sim 实证 |
|---|---|---|---|---|---|---|
| E-TIMING-001 | active/sim/quantized | 1.15 | 0.83（S3=0.98 三窗全绿） | -0.086 | e3da6fa71af1 | sim_trade_log 19 笔至 10-04 在考 |
| TSMALL-001 | active/candidate/quantized | 1.066 | 0.802 | -0.232/-0.370 | dc5b80aa3614 | sim 5 行（9/15-9/24） |
| DABAN-023 | active/candidate/quantized | 0.070 | 0.795 | -0.317 | 4440d07f973f | sim 3 笔+5 行 |
| VREV-001 | candidate/candidate/**pending_backtest** | （家族替身）1.15 | 同键 0.983 | -0.086 | e3da6fa71af1 | 同键 |
| MOMTREND-002 | candidate/candidate/**pending_backtest** | （替身）1.08 | —（screened_in） | -0.45 | b1ab42050d68 | 无 |
| MOMTREND-019 | candidate/candidate/**pending_backtest** | 替身 -0.308→CH 复考 0.795 | 0.795 | -0.478 | a4543012b464 | sim 1 笔 |
| VREV-026 | active/candidate/quantized | 0.160 | 0.526 | -0.183 | c72318f2da1c | sim 1 笔+5 行（+84.9 万） |
| MF-098 | active/candidate/quantized | 0.518 | 0.156（BH-FDR 未过，留观） | -0.305/-0.452 | 5301c5d9d7c8 | sim 1 笔+5 行（+380 万） |
| MOMTREND-033 | active/candidate/quantized | 0.204 | 0.552（OOS 反超） | -0.189 | 7f7e5f935dfc | sim 5 行 |
| VREV-027 | active/candidate/quantized | 分段 +2.89/+2.90 | 0.537 | -0.180 | 9ce75aa27ce5 | sim 1 笔+5 行（-48.2 万⚠） |
| MF-099 | active/candidate/quantized | 0.397 | 0.404（BH-FDR 未过，留观） | -0.240/-0.408 | 8664521af1a0 | sim 2 笔 |
| VREV-025 | active/sim/quantized | 1.15 | 0.83（三窗全绿，81 格 77 正） | -0.086 | e3da6fa71af1 | sim_pocket 59 日（7-9 月，+7.37 万） |
| VAL-001 | active/candidate/quantized | 0.563 | 1.173（OOS 反超） | -0.347/-0.447 | 8d000bf3ccc3 | sim 5 行 |

注：VREV-027 sim 期 -48.2 万为 13 卡唯一 sim 负值——波 3 观察期阈值对该卡收紧 20%；MF-098/099 BH-FDR 未过与 L13 §4 P3 留观承诺一致，转正以 Owner 本批批件为准，观察期从严。

## 4. 仓位与总闸

1. **起步仓**=每卡额定 1/3；观察 5 个交易日达标 → 升满额定。升满动作需记录 CH decision_daily 台账行。
2. **信号级额度合并闸**：同台账键卡（A 族三卡同键 e3da6fa71af1）在 risk 层按 signal_group 合并限仓——三卡任一在场，恐慌信号合计暴露≤1 份额定预算，禁止叠仓。
3. **总闸**=红线执行器在岗（4h 熔断/日黄红线；daily_pnl<-0.03*aum → reduce_only 全降）。各波上线前必查 `python -m zephyr.trading.process_reaper --status`（reaper 存活=写操作前提）+ kill_switch emergency_track_state=normal。
4. 单卡回撤阈值（观察期熔断线）：指数择时族（A/B/C）日回撤>1.5% 或 5 日>3%；月频选股族（D/E）5 日>4%；日内族（G）单日>2%；F 个股突破 5 日>3.5%。

## 5. 机械步骤清单（每卡同构 7 步）

按 card_state_vocabulary.yaml 13 态契约（REG-CARDSTATE-VOCAB-001）。策略卡此前 0/161 携带 card_state（L13 盲点 B4），本计划首次把契约挂到策略卡，全用 safe_write_text 复核式写入。

1. **前置校验**：reaper 存活｜kill_switch normal｜卡 status/lifecycle/algorithm_status 与 §3 表一致｜candidate+pending_backtest 卡确认代码化与卡级考试已完成（波 2* 三卡）。
2. **card_state→`frozen`**：上线日写死考窗/阈值/桶边界（参数自卡 evidence 与翻译件 build 契约取，禁止现场调参）；credential 台账行开立。
3. **TDM 挂点确认**：`config/trading_decision_map.yaml` 对应节点 strategy_mounts 含本卡 ref（6 挂载卡 9 处挂点 L13 已落；7 新卡按域挂 E-L1/E-L3/F-FLOW/P-FLOW 对应点）→ `python -m zephyr.trading.decision_map validate` 过 → unwired→wired。
4. **实弹通道确认**：AutoRuntime Core（`python -m zephyr.trading`）加载决策图；sim→实盘桥切 segment flag（**Owner 北极星门位，执行队持本批件操作并留痕**）；确认成本模型/滑点参数与卡 cost_model 绑定。
5. **首笔小仓试单**：起步仓（额定 1/3）再取 1/2 首笔；T+1 核对成交、滑点 vs 模型（<1.5 倍）、CH sim_pocket_daily 同构实弹台账行落库。
6. **监控挂点**：实弹台账行日更（对齐 sim 表结构）｜crisis_gate_log 注册卡级熔断线（§4.4）｜kill_switch trigger 清单含本卡 signal_group｜decacy 监控挂 last_decay_scan_at。
7. **观察期结转**：5 个交易日达标 → card_state→`green`（credential_required，附 DSR 复核数）+ 升满额定；任一破线 → §6 回滚。

## 6. 回滚预案（每卡熔断动作序）

1. **触发即撤**：kill_switch/reaper 侧 reduce_only 撤清本卡持仓（日内族当日清，月频族 T+1 清）。
2. **停信号**：decision_map 对应 mounts 摘除（或 flag off），`decision_map validate` 复验，防信号继续生成。
3. **卡状态回退**：观察期内破线 → card_state→`suspended`（挂起，必带显式 re-entry 触发条件，如"同域模拟盘连续 10 日正收益+滑点回归模型"）；机制性证伪（滑点持续 3 日>模型 3 倍/信号源数据断供）→ `red` 判红走重考队，禁直接复上。
4. **合并闸联动**：A 族任一卡熔断，signal_group 合并预算整体冻结，另两卡禁止递补开仓。
5. **留痕**：CH 台账行+`.runtime/sessions/<sid>/staging/` 复盘包；72h 内出回滚报告交 Owner（转正批复的对账面）。
6. **波级熔断**：单波内 ≥2 卡同触发 → 该波全体 suspended，滚上暂停，总闸复核后 Owner 决定是否继续波 3。

## 7. 关键风险与边界

- **VREV-027 sim 期负值**（-48.2 万）与 **MF-098 OOS 0.156**：两卡为 13 卡中最弱环，波次已靠后+观察从严；若 Owner 允许，可降格为"sim 延长观察、暂缓实弹"（不影响其余 11 张排期）。
- **三卡无码**（VREV-001/MOMTREND-002/MOMTREND-019）：pending_backtest+code_path 空，实弹前提=先代码化 quantized+卡级考试（L13 §4 P2 同判）；未完成则波 2 缺额滚上（4 张而非 5 张），不为凑数放松前置。
- **BH-FDR 未过双卡**（MF-098/099）：registry 自承诺"后续批次重检"仍有效，本批转正不豁免 P3 复检义务。
- 本计划不含任何 flag 出厂翻转/注册表净删；卡状态翻转以 Owner 已批的 13 张转正批件为唯一授权面。
