---
ttl: task_bound
rule_form: data
verifiability: manual
title: 存量状态/情绪词表逐套映射登记册（词表 SSOT 第一步·W2 收编件，裁定#398五①+#399四）
owner: ZephyrAlpha-Owner
language: zh
created: 2026-09-22
session: st-t0-revival-20260922
---

# 存量词表映射登记册（逐套，全量收编）

> 官方词表本体=同目录 `01_official_state_vocabulary.md`；常量真源=src/zephyr/shared/vocab/market_state.py（SH-VOCAB-001）。
> 普查口径：src/ 全仓实测（2026-09-22 行号锚）；行号漂移时以符号名+成员拼写定位为准。
> **数量对账（如实披露）**：09-21 普查口径"28 套"（02 决策卡）；本册实测登记 **34 套存量 + 4 件官方本体 + 1 份官方归一表**。差异来源=①普查后 W1 常量模块新建（不计存量）②本班普查把"补充收录"的映射键集/状态机/盘中五态归一表逐套入册（当时未单列）。本册以仓库实物为准，为后续唯一登记面。

## A. 官方本体（不计存量，收编锚点）

| # | 名称 | 位置 | 成员 |
|---|---|---|---|
| A1 | MacroRegime（轴 M 本体） | shared/vocab/market_state.py:47-60 | R1 低波震荡/R2 中波/R3 牛市趋势/R4 熊市阴跌/R10 危机/R11 复苏/R12 突破 |
| A2 | EmotionCycleSix（轴 E 本体） | market_state.py:63-75 | CAPITULATION 投降/ACCUMULATION 蓄势/IGNITION 点火/EXPANSION 主升/EUPHORIA 亢奋/DISTRIBUTION 退潮 |
| A3 | IntradayFive（盘中五态伴生） | market_state.py:78-89 | LOW/DEFENSE/OSCILLATION/ATTACK/EUPHORIC（+INTRADAY_TO_SIX 官方映射 :95-101） |
| A4 | AnchoredTier（轴 S 本体，C1 消歧件） | market_state.py:104-123 | ANCHORED_R1 中高/R2 中/R3 低/R4 高风险 |
| A5 | EXTREME_STATE_ALIASES（C11 官方归一表） | market_state.py:129-139 | 九键→MacroRegime.R10（§C11 行） |

## B. 宏观 regime 轴存量（8 套）

| # | 词表 | 位置 | 形态 | 成员→官方映射 | 撞名注记 | 消费方 | 处置 |
|---|---|---|---|---|---|---|---|
| M1 | REGIME_STATES（HMM 七态） | regime/core/regime_detector.py:107 | list | r1-r4+r10-r12→m.regime.*（拼写即官方 token 源） | C1 主语源 | framework_composer:203/index_regime_panel:82/phase2_runner:386/api_server:1128/decision_gate:230/switcher.py:41 | 原位保留=官方数据面（#304 锚定） |
| M2 | HMM_STATES+OVERLAY_STATES | regime_detector.py:108-109 | list×2 | 核心四态+覆盖三态拆分 | C1 | 同上 | 原位保留 |
| M3 | REGIME_STATES_12（旧 12 态） | signal_ashare/sentiment/sentiment_cycle.py:678-691 | list | 9 状态×3 轴（Bull/Neutral/Bear×Low/Med/High）+CRISIS/RECOVERY/BREAKOUT→m.regime.*（九格按语义归 r1-r4，CRISIS→r10，RECOVERY→r11，BREAKOUT→r12） | 与水温 S0-S4、转换 S 系撞号面 | 同文件 SENTIMENT_TO_REGIME_MAP:669 | 原位保留+映射 |
| M4 | SizingMarketRegime（仓位 12 态） | position/core/position_sizing_engine.py:89-100 | 枚举 | CALM_BULL…BREAKOUT→m.regime.*（CALM_BULL/MOMENTUM_BULL→r3 面；PANIC_CRASH/CRISIS→r10；RECOVERY→r11；BREAKOUT→r12） | 与 M5/M6/M7 同名异义类（MarketRegime 三胞胎） | 同文件 MARKET_REGIME_CAPS:104 | 原位保留+映射 |
| M5 | MarketRegime（牛熊 2 态） | signal_ashare/ml_forecast/regime_change_detector.py:90-94 | 枚举 | BULL→{r3,r11,r12} 面；BEAR→{r4,r10} 面（粗粒度，映射声明） | 三胞胎之一（ARCH-034） | BM-BUY-02-A-1-d | 原位保留+映射 |
| M6 | MarketRegime（ML 3 态） | gov_drift/detector_core/ml_engineering.py:47-50 | 枚举 | BULL/RANGE_BOUND/BEAR→同 M5 粗粒度面 | 三胞胎之二，与 position_sizing 注释互指 | ml_engineering | 原位保留+映射 |
| M7 | MarketRegime（增益调度 4 态） | feedback_loop/diagnosers/reliability/regime_gain_scheduling.py:38-42 | 枚举 | CALM→r1 面；NORMAL→r2 面；VOLATILE→r2/r4 面；CRISIS→r10 | 三胞胎之三 | 增益调度 | 原位保留+映射 |
| M8 | TrendDirection+VolatilityLevel（正交分解） | signal_ashare/market_state_sensor.py:94-107 | 枚举×2 | BULL/NEUTRAL/BEAR×LOW/MEDIUM/HIGH→m.regime.* 笛卡尔面 | 与情绪轴无涉（正交分解语义） | market_state_sensor | 原位保留+映射 |

## C. 情绪周期轴存量（11 套）

| # | 词表 | 位置 | 形态 | 成员→官方映射（e.cycle.*） | 撞名注记 | 消费方 | 处置 |
|---|---|---|---|---|---|---|---|
| E1 | SentimentPhase（28 号 memo 五段） | signal_ashare/sentiment/sentiment_cycle.py:52-63 | 枚举 | FREEZING 冰点→capitulation；STARTING 反核→accumulation+ignition 过渡（声明为蓄势→点火间过渡，映射取 ignition）；FERMENTING 主升→expansion；CONSENSUS 疯狂→euphoria；EBING 退潮→distribution | **C2 之三套之一**；docstring :30-33 明示三套勿混 import | sentiment_cycle_evaluator:47/similar_day_inference:67 | 原位保留+映射 |
| E2 | SentimentPhase（4+1 硬标签） | signal_ashare/sentiment/market_sentiment_analyzer.py:89-96 | 枚举 | FREEZING→capitulation；REVERSAL→accumulation/ignition 过渡；MAIN_RALLY→expansion；EUPHORIA→euphoria；RETREATING→distribution | **C2 之二**；**方向陷阱本尊：最热(≥80)→RETREATING（:989-1000，阶段中心 :435=90.0）**——官方裁定见立法件 §3 | intraday_sentiment_loop:68/llm_premarket_analysis:135/boundary_revision_engine:87/价格背离/极值反转检测 | 原位保留+映射+方向注记（跨引擎禁直传） |
| E3 | EmotionPhase（4+1 阶段） | signal_ashare/limit_up/youzi_relay_emotion_engine.py:60-68 | 枚举 | FREEZING→capitulation；REVERSAL→过渡；MAIN_RISE→expansion；MANIA→euphoria；RETREAT→distribution；UNKNOWN=豁免 | **C2 之三**；**方向陷阱对照面：最热→MANIA（:450-453）**，仅广度<0.4（:457）或高连板频繁开板（:461）才改判 RETREAT | daban_sleeve_strategy:75/dual_engine_fusion:57 | 原位保留+映射+方向注记 |
| E4 | TDM state_matrix.states（六段 v1.2） | config/trading_decision_map.yaml:4474-4475 | yaml list | capitulation…distribution=官方 token 拼写源（**轴 E 官方语义的 Owner 批准真源**） | 与 M 轴降维映射混用见 F4 | decision_map.py:230/daily_decision_orchestrator:100-118/daily_gate_snapshot:183-190 | 原位保留=官方数据面 |
| E5 | MarketMode（事件模式） | feedback_loop/collectors/market_event_integrator.py:36-40 | 枚举 | NORMAL/CAUTION/HOLIDAY 豁免；EMERGENCY→m.regime.r10（C11 归一） | EMERGENCY 与风控 EMERGENCY 多处同名（见 C11 行） | event_score.py:353（熔断停开仓） | 原位保留+映射 |
| E6 | WaterTempTier（日级水温五档） | signal_ashare/core/daily_condition_sensor.py:45-52 | 枚举 | S0_ICE→capitulation 面（水温语义）；S1_COOL/S2_NEUTRAL/S3_WARM→accumulation 面；S4_HOT→ignition/euphoria 面声明 | **S0-S4 与预案/转换事件撞号**；S0_ICE 在 C11 九写法之列 | signal_ashare/__init__.py:120 | 原位保留+映射 |
| E7 | WaterTemp（情绪→板块门桥接五档） | signal_ashare/sector/sector_gate.py:54-61 | 枚举 | NEUTRAL/RISK_ON/PANIC_REPAIR/RISK_OFF 豁免（板块门语义）；CRASH→m.regime.r10（C11 归一） | CRASH 在 C11 九写法之列 | daily_gate_snapshot:184 | 原位保留+映射 |
| E8 | SentimentState（历史分位三态） | alt_data/sentiment_engine.py:68-74 | 枚举 | ICE→capitulation 面+R10 候补（C11 归一按语境：ICE 为情绪冰点→e.cycle.capitulation）；OVERHEAT→euphoria 面；NORMAL/INSUFFICIENT_HISTORY 豁免 | ICE 在 C11 九写法之列 | alt_data | 原位保留+映射 |
| E9 | 六段降维映射（REGIME_TO_SEGMENT） | strategy_pipeline/daily_decision_orchestrator.py:110-118 | 映射键 | r10→capitulation/r4→distribution/r1,r11→accumulation/r2,r12→ignition/r3→expansion（M→E 降维，属预测用途） | **与 framework_composer 版不一致（r4 归属相反/缺 r1）——收编注记：两版差异如实登记，收敛待②专项** | daily_decision_orchestrator | 原位保留+差异披露 |
| E10 | 六段降维映射（_DOMINANT_TO_WATER_TEMP） | strategy_pipeline/daily_gate_snapshot.py:183-190 | 映射键 | capitulation→CRASH 等（E→E7 桥接） | 桥接层 | daily_gate_snapshot | 原位保留+映射 |
| E11 | PHASE_DISCIPLINES/STRATEGY_DEPLOYMENT 组合键 | sentiment_cycle.py:594-1087 | 映射键集 | ("daban"/"multifactor"/"event_driven", 五段) 组合键→官方六段经 E1 映射 | 键值域=五段（经 E1） | sentiment_cycle_evaluator/作战室 | 原位保留+映射 |

## D. 预测/预案轴存量（6 套，轴 F=登记豁免轴，但存量逐套登记）

| # | 词表 | 位置 | 形态 | 成员→官方映射（f.plan.*） | 撞名注记 | 消费方 | 处置 |
|---|---|---|---|---|---|---|---|
| F1 | S1_attack/S2_defense/S3_oscillation（N=3 预案） | plan_engine/daily_plan.py:401-428 | dict list | 高开放量进攻/低开防御/平开震荡+action→f.plan.s1_attack 等（token 带轴前缀消解 S 撞号） | S1-S3 与水温/转换事件撞号 | plan_engine | 原位保留+映射 |
| F2 | SCENARIO_LIST 9 情景格 | plan_engine/scenario_attribution_stats.py:26 | 注释声明 | 情景归因维度→f.plan.*（明细展开时逐格登记） | — | 作战室 W0/W6、GAP-F-01 | 原位保留+映射 |
| F3 | HoldingAction+PlaybookStatus | plan_engine/scenario_playbook.py:83-100 | 枚举×2 | HOLD/ADD/REDUCE/EXIT/WATCH+PROPOSED/CONFIRMED/EXECUTED/REJECTED/EXPIRED→f.plan.*（流程态，登记豁免语义但入册） | — | C-005 对策模板 | 原位保留+映射 |
| F4 | regime→六段降维键（两版） | daily_decision_orchestrator:110-118+framework_composer 版 | 映射键 | M→E 降维（见 E9 差异披露） | 两版 r4 归属相反 | 同 E9 | 原位保留+差异披露（收敛挂②） |
| F5 | TRANSITIONS（状态转换事件） | regime/core/regime_detector.py:185 | list | T1-T6+S1/S2→f.trans.*（T1=r1/r2→BREAKOUT，S1=Any→CRISIS :304-373，S2=CRISIS→RECOVERY） | S 系与水温/预案撞号 | regime 转换事件消费方 | 原位保留+映射 |
| F6 | ChangePhase | signal_ashare/ml_forecast/regime_change_detector.py:97 | 枚举 | 转换相位→f.trans.* | — | regime_change_detector | 原位保留+映射 |

## E. 个股行为轴存量（4 套）

| # | 词表 | 位置 | 形态 | 成员→官方映射（s.*） | 撞名注记 | 消费方 | 处置 |
|---|---|---|---|---|---|---|---|
| S1 | STATE_NAMES（锚定四档，C1 主语源②） | regime/core/anchored_state_machine.py:86-91 | dict | r3 低风险/r2 中/r1 中高/r4 高→s.anchored.*（阈值 0.30/0.60/0.80 :98-109） | **C1 主语源②：r3=最安全 vs 轴 M r3=牛市趋势，语义近镜像** | anchored_state_machine | 原位保留+映射（禁裸字符串跨轴） |
| S2 | StockCategory（个股七类） | signal_ashare/quant_short_term_strength_engine.py:63-79 | 枚举 | MAIN_LEADER/SECOND_TO_THIRD/FOLLOWER/RECOVERY/FAKE_STRONG/INVERSE_BOARD/NEUTRAL→s.category.*（官方拼写源） | RECOVERY 与 m.regime.r11/风控 RECOVERY 同词异轴（跨轴禁直传） | quant_short_term_strength_engine | 原位保留=官方拼写源 |
| S3 | FusionDecision+SignalDirection | signal_ashare/strategy_signal/dual_engine_fusion_decision_engine.py:70-88 | 枚举×2 | 与 StockCategory 同词异源→官方=StockCategory（成员逐字相同）；SignalDirection LONG/SHORT/NEUTRAL→s.direction.* | 同词异源双胞胎 | dual_engine_fusion | 原位保留+映射指向官方 |
| S4 | 强度五档 A-E | quant_short_term_strength_engine.py:63-79 | 枚举 | 80-100/65-80/50-65/35-50/0-35→s.strength.* | — | 同 S2 | 原位保留+映射 |

## F. 补充收编（封闭状态集/状态机，5 套）

| # | 词表 | 位置 | 形态 | 成员→官方映射 | 撞名注记 | 处置 |
|---|---|---|---|---|---|---|
| X1 | KNOWN_REGIME_STATES | backtest/core/decision_gate.py:230 | frozenset | r1-r4+r10-r12→m.regime.*（回测门消费面） | C1 消费面 | 原位保留+映射 |
| X2 | ALL_SEVEN_STATES+trend_up_states | strategy_factory/owner_regime_switcher/switcher.py:41,55 | 常量 | 七态→m.regime.*；trend_up={r3,r11,r12} | — | Owner 切换器 | 原位保留+映射 |
| X3 | TREND_UP_STATES（band-T 门） | strategy_factory/owner_band_t/regime_gate.py:29 | 常量 | {r3,r12}→m.regime.* | 与 switcher 版 trend_up 不同值（{r3,r12} vs {r3,r11,r12}）——**差异如实披露，收敛挂②** | band-T 门 | 原位保留+差异披露 |
| X4 | normal/warning/crisis 三态 | pf_alloc/crisis_gate.py:106-108 | 常量 | crisis→m.regime.r10（C11 归一；小写拼写） | crisis 在 C11 九写法之列 | risk/paper_hedge_leg.py:397,538 | 原位保留+映射 |
| X5 | 风控状态机 RECOVERY 族 | risk/core/drawdown_state_machine.py:102、var_breach_state_machine.py:87 | 状态机态 | RECOVERY→语义=风控恢复相位，**非** m.regime.r11（异轴同名，映射声明为"同名不同轴"，禁互转） | RECOVERY 三轴同名（HMM/风控/StockCategory） | 风控链路 | 原位保留+异轴声明 |

## G. C11 专项：九种"最坏状态"写法归一总表（官方=A5 EXTREME_STATE_ALIASES 执行，全部→m.regime.r10）

| 写法 | 实物锚点 | 归一 |
|---|---|---|
| r10 CRISIS 本尊 | regime_detector.py:107,286 | =m.regime.r10 |
| crisis（小写） | pf_alloc/crisis_gate.py:108 | →m.regime.r10 |
| CRISIS(vol>0.9) | 仅登记于 market_state.py:132（src 无第二实物，文档/历史口径） | →m.regime.r10 |
| EMERGENCY | market_event_integrator.py:39；ex_core/risk_layer_orchestrator.py:263（DrawdownAlertLevel）；trading/resource_optimization.py:117（PressureLevel） | →m.regime.r10（EMERGENCY 同名三处异形，归一同向） |
| CRASH | sector_gate.py:61；daily_gate_snapshot.py:184；strategy_abnormal_exit_orchestrator.py:83（ExitTrigger，退出触发语义单列） | →m.regime.r10（ExitTrigger.CRASH=触发器语义，异轴声明） |
| S0_ICE | daily_condition_sensor.py:48 | →e.cycle.capitulation 面（情绪水温）/r10 候补，按语境，映射声明 |
| ICE | alt_data/sentiment_engine.py:71 | →e.cycle.capitulation 面 |
| 冰点 | sentiment_cycle.py:59/market_sentiment_analyzer.py:92/youzi_relay_emotion_engine.py:63；TDM=capitulation | →e.cycle.capitulation |
| 退潮 | 同上三处 :63/:96/:67；TDM=distribution | →e.cycle.distribution |

## H. 出厂纪律（执法点登记）

1. 新模块出厂验收清单新增一问（construction_workflow_policy.md 同步追加，随批登记面动作）：**"状态输出是否引用官方词表或在 state_vocabulary 映射登记册登记映射？"**
2. W3 执法门（启发式扫描新定义状态枚举类，观察期 warn→硬阻断）按 03 自裁书节奏另行施工；本册=其白名单/比对基底。
3. 本册维护=生成器化候选（宪法 §9.5 静态清单禁手工维护）：登记册日后由 symbol 扫描器生成，本班首册为人工普查实物锚点版，生成器上线后交接。
