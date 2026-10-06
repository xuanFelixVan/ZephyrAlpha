---
campaign: matrix-20261006
lane: S-skeleton
status: draft
ttl: task_bound
---

# st_l0_l1_premarket —— TDM 盘前计划与大盘总闸（LROOT+L0+L1 cn_a，15 节点）

- 真源: `config/trading_decision_map.yaml`；行号=TDM:L*。类别=H9 判定（证据指针见 H9 §1.0~§1.2，本册不重复证据行号）。
- 计数: 15 = LROOT 1 + L0 5 + L1 cn_a 9（crypto C-L1 归 st_crypto）。四类: A1/B2/C7/D5。

## 1. 族内节点全清单与接线现状

| node_id | 名称 | 类别 | 接线级 | 引擎旋钮/模块 | 行 |
|---|---|---|---|---|---|
| TDM-E-FLOW | 输出建仓信号 | A | L1 | 考卷每日权重宽表=建仓清单（evaluate_recipe 返回 weights） | TDM:L82 |
| TDM-E-L0 | 盘前作战计划 | D | ND | plan_engine/daily_warroom_pipeline；mounts MOD-EX-063+PLAN×5+RK×2 | TDM:L192 |
| TDM-E-L0-01 | 计划生成 | D | ND | plan_engine/daily_trade_plan（MOD-PLAN-020） | TDM:L219 |
| TDM-E-L0-02 | 偏离监控与修订 | D | ND | plan_engine/plan_deviation_monitor（MOD-PLAN-006） | TDM:L247 |
| TDM-E-L0-03 | 收盘复盘与明日边界 | D | ND | plan_engine/tomorrow_boundary_planner（4 mounts） | TDM:L275 |
| TDM-E-L0-04 | 明日情绪盘中滚动预测 | D | ND | plan_engine/intraday_tomorrow_forecast（MOD-SIG-128）；plan-bridge 实证：计划姿态仅防御态可机械执行（H9 §4.5） | TDM:L307 |
| TDM-E-L1 | 大盘总闸 | B | L2 | 旋钮 J_regime_switch=[off,on]（schema:64-68，phase>=2）+ regime 三件套 c1/c2/c3 在册 | TDM:L344 |
| TDM-E-L1-S1 | 大盘指数传感器 | C | L3 | regime/features/index_sensor；mounts MOD-MKT-001~007；考卷 load_index 在册不消费 | TDM:L407 |
| TDM-E-L1-S2 | 市场内部结构传感器 | C | L3 | limit_up/limit_up_followthrough（MOD-REGIME-007,MOD-SIG-114）；涨停在考卷只作封板掩码 | TDM:L436 |
| TDM-E-L1-S3 | 赚钱效应传感器 | C | L3 | limit_up/lhb_premium_analyzer（live 域）；无 mounts | TDM:L463 |
| TDM-E-L1-S4 | 波动率传感器 | C | L3 | regime/features/synthetic_vix（MOD-REGIME-011/013）；考卷 f_lowvol20 是个股截面非市场 VIX | TDM:L488 |
| TDM-E-L1-S0 | 宏观环境传感器 | C | L3 | alt_data/policy_expectation_analyzer；无 mounts | TDM:L538 |
| TDM-E-L1-S0-1 | 新闻情绪语义分析 | C | L3 | intelligence/news_sentiment_analyzer；断供史见 chief 02 §2（news_sentiment_score 断 13 月） | TDM:L566 |
| TDM-E-L1-S5 | 日级市场条件传感器 | C | L3 | signal_ashare/core/daily_condition_sensor；无 mounts | TDM:L596 |
| TDM-E-L1-AGG | 市场状态判定（六态状态机, critical） | B | L2 | owner_regime_switcher（switcher.py:96-243 build_schedule/hysteresis；engine.py:167 冻结考试引擎）；state_matrix 24 cells | TDM:L620 |

## 2. 缺口与可考性判定

- L0 全族 D=设计边界不是缺口（H9 §4.5：回测"计划节点"实现=编造）；可考性转 sim 平面（plan-bridge 已实证 unexecutable 记录语义）。
- L1 的 B（总闸+状态判定）=T3a 首选开闸位：J=on 属 context 翻转非增删轴（H9 §3.3 预注册要点 1）。
- 传感器族 C（6 枚）全 live 在岗：S 级接线即可考的是 S1（load_index 已在考卷引擎，H9 S 级表未单列 S1 但 J 开闸隐含消费面）；其余传感器进考卷=新因子工程（M 级起）。

## 3. 一句话修复建议

T3a 开 J_regime_switch=on（S1）并钉死"日级帽调度≠六态挂载矩阵"的失真披露；传感器族按 S1→S4→S2 顺序逐个立项（各需新因子面）。

## 4. 交叉验证

- H9 §1.0~§1.2 判定全转录对平；§3.2 T3a 配置形态、§4.6 regime 近似失真声明。
- chief B1 ENV-08（L0+L1=15）计数一致；state_matrix 六态+24 cells 计数一致（00 §4）。
- census §3 图13 盘前段（L0.5 元数据 08:34→paper 09:25）=本族 L0 的运营时序面，两图分工（TDM 管决策逻辑/图13 管运营时序）与 census §3 注一致。
