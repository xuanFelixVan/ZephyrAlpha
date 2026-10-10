---
ttl: task_bound
title: L5 挖矿车道台账 — exit_flow 全流 19 节点
created: "2026-10-10"
sid: st-nightmine-20261010
lane: L5
flow: exit_flow
family_id: NIGHTMINE-CAMPAIGN
---

# L5 台账（exit_flow 全流，19 节点 / 20 张新卡）

工作根=`D:/ZephyrAlpha/.aidrafts/st-nightmine-20261010`。卡输出=`docs/03_modules/_domain_backtest/exam_cards/exit_flow/<S1|S2|X1|XFLOW>/`。
性质：Owner 通宵令下的全自动挖矿车道，禁 git 写、禁改 TDM/注册表/分数册、禁跑生成器（本车道全部为新建卡文件+本台账）。

## 一、基建核实（卡的取数与跑法绑定对象，全部实测非凭记忆）

- 对照装置真源：`scripts/backtest/fexam/exit_sim/exit_simulator.py`
  实测函数面=`load_pass_columns(cap=24):74` / `load_kline:103` / `load_indicator:110` / `wilder_atr_one:119` /
  `atr14_wilder:135` / `month_start_rows:146` / `build_signals:158` / `simulate(...,stop_enabled,stop_mult,commission):171` / `run_all:328`。
  **关键实测=simulate() 仅 stop_enabled 一个开关，无 tp/ladder/participation/time_stop/urgency 形参**（:171-181）→ 所有新臂一律如实标 `blocked_on_impl` 并写缺什么。
- 冻结卷真源：`scripts/backtest/fexam/exit_sim/prereg_frozen.yaml`（frozen_at_utc='2026-10-06 10:10:50+00:00'；device.columns_cap24 24 列；
  device.windows run/is/oos_holdout/kline_load；stop_rules 全段；costs=COMMISSION_RATE 万0.854 双边；judge_frozen.verdict_gain=MaxDD 改善≥5pp 且 Sharpe 差≥-0.2；recalibration_duty.per_run_seconds）。
- 满分卷先例：`docs/_working/fexam/exit_sim_report_v1.md`/.yaml（ATR 止损 OOS MaxDD 改善 +16.5pp→「有增益」）；
  反例在册=`docs/_working/fullcirc_closeout_chief/99_delivery.md` §七（T3b stop/breaker CRISIS 窗 0% 过 5pp 线=FAIL）。
  **本车道处置=不代裁冲突，把两案门柱取严并置（OOS+CRISIS 双窗皆须不劣化）写进每张对照卡的 `oos_stability`/`crisis_window` 判据面。**
- 执行口径三档真源（新发现，草稿未记）：`scripts/backtest/translated/_c4_engine.py` 实测 `_VALID_EXEC_CALIBERS=("close","next_open","vwap")`:86、
  `_vwap_from_amount_volume`:100（带 vwap/close 量纲哨兵越界即抛）、形参 `exec_caliber="close"`:610 → X-S2-03 的 vwap 臂**在官方引擎已具备**，仅 fexam 装置侧缺注入点。
- 门柱参数真源（不硬编码）：`config/exam_scale_cost_gate.yaml` 实测 `cost_gate.tiers_bp=[0,5,10,20,40]`、`survival_floor=0.0`、
  `turnover_gate.cap_annual_x=8.0`、`sharpe_annualization.unfillable_at_limit=separate_pool`、`scale_gate.participation_ref=0.05`。
- **事故级发现（供考试车道修）**：`scripts/backtest/fexam/calibration_exam.py:_round_trip_cost_bp()` 读 `net_fee.round_trip_cost_bp`，
  而实测 `config/exam_scale_cost_gate.yaml` **无 net_fee 块**（yaml.safe_load 顶层键=cost_gate/scale_gate/turnover_gate/search_objective/breakeven_cost_gate/cost_gate_active/schema_version/doc_type）
  → 执行器 G1 净费读数当前恒返 nan，`net_bucket_medians` 静默失效。本车道未改配置（禁区），只留痕。

## 二、数据可得性实测（CH 探针形=`scripts/backtest/fexam/ch_data.py`，禁裸 duckdb；全部含命令原文随卡 data_window_evidence）

| 表 | 实测覆盖窗 | 行数 | 用途 |
|---|---|---|---|
| c1_market.kline_daily_hfq | 1990-12-19..2026-09-30 | 10,098,785（nsym 5916） | 全部日频双臂装置的主数据 |
| c1_market.kline_index | 1990-12-19..2026-10-09（000300 子集 2005-01-04..2026-10-09） | 3,104,162（000300=5284） | 基准/超额收益 |
| c1_market.stk_limit | 2015-01-05..2026-10-09 | 9,254,772（nsym 5831；列 board/limit_down/limit_pct/pre_close/st_flag） | 连续跌停开板概率、跌停不可成交掩码、封板掩码 |
| c1_market.kline_1min | 2021-09-01..2026-10-09 | 1,493,285,247（nsym 5858） | 分时/追单/时段面（分钟粒度可考） |
| c1_market.kline_5min | 2021-09-01 09:35..2026-10-09 15:00 | 296,122,159 | 分批切片、VWAP |
| c1_market.tick_data | 2026-01-05..2026-10-08 | 3,943,831,530（nsym 11811） | tick 面（仅 2026 年窗，长窗判据禁用） |
| c1_market.tick_depth_5 | 2026-07-24..2026-09-30 | 130,146,982 | 五档深度（**仅 2 个月→盘口排队面 blocked_on_data**） |
| c1_market.l2_tick | — | **0（空表）** | 不可用 |
| c1_market.auction_snapshot / auction_book | 2026-06-01..2026-09-30 / 2026-07-21..2026-09-30 | 288,909 / 3,690,473 | 竞价逃命单（短窗，仅 pilot） |
| c1_market.dragon_tiger_seat | 2022-01-04..2026-10-09 | 622,365（nsym 5998） | 席位净卖出派发（**可考 4 年窗**） |
| c1_market.dragon_tiger | 2026-08-07..2026-10-09 | 2,534 | 主表仍不可考（旧负结果对主表成立） |
| c1_market.emotion_index | 1991-06-10..2026-10-09 | 8,661 | `stage` 实测枚举=close_final/pre_open/auction → **快照阶段标记，非情绪六段，禁误用** |
| c1_backtest.decision_daily | 2026-09-16..2026-10-12 | 138（market_state 值域=expansion 136/unknown 2） | **六段态无历史→退潮路 blocked_on_data** |
| c1_market.sector_snapshot / market_breadth_snapshot | 2026-08-14.. / 2026-08-24.. | 122,746 / 174 | 短窗，不作长史判据 |
| c1_market.account_nav_daily | 2026-09-28..2026-10-09 | 5 | **实盘净值/持仓面 blocked_on_data**（R1 三卡因此改用仿真组合净值） |
| c1_market.kline_etf_daily | 2021-03-08..2026-10-09 | 110,619 | 宽基 ETF 天量护盘信号面 |
| c1_backtest.sim_trade_log | 在册（列 run_id/trade_date/symbol/action/price/shares/cost_paid/signal_reason） | 未取（未探测行数，禁凭记忆断言其有/无） | 三率反馈真实成交面交叉 |

## 三、逐节点台账（六向=①上游 ②下游 ③算法 ④后端 ⑤呈现 ⑥数据）

| node_id | 六向结论(每向一句) | 新卡 | 族 | mined_out? | blocked 原因 |
|---|---|---|---|---|---|
| TDM-X-FLOW | ①terminal/aggregation 无机制，唯一可考=整链总账 ②下游无（边 X-S2→X-FLOW feed 在册） ③E 道与 T3b 均只考单档、无整链先例=富矿 ④simulate() 可跑两臂 ⑤离场清单呈现属前端另案 ⑥日频数据全覆盖 | 1 | ablation | 否 | 无 |
| TDM-X-R1 | ①kill switch 阈值 25%/-6% 即判据 ②下游=R1-01/02/03 与 S1-06（边在册） ③影子制=根宪法 §5 下放制式，先例零 ④kill_switch.py 456 行在档、回测无适配器 ⑤不施工 ⑥account_nav_daily 仅 5 行→改仿真净值 | 1 | shadow | 否 | 实盘净值面 blocked_on_data（缺 2018..2026 长序列） |
| TDM-X-R1-01 | ①五级表+迟滞解除=三张卡候选（等级表/迟滞带/危机触发不缺席） ②消费方=P3-01 资格门④（TDM 注释在册） ③机构软去杠杆阶梯在册参考 ④drawdown_state_machine.py 773 行在档，fexam 无接入 ⑤另案 ⑥同上 | 1 | comparison | 否 | 状态机与回测装置无适配器（blocked_on_impl） |
| TDM-X-R1-02 | ①减仓顺序三键+恢复规则=两卡候选（顺序/恢复迟滞） ②路由到 P2-04、L4 走 S1-06 ③recover-50% 机构规则在册 ④drawdown_liquidation_guard.py 209 行在档 ⑤另案 ⑥无部分减仓能力 | 1 | comparison | 否 | blocked_on_impl（simulate 全仓进出） |
| TDM-X-R1-03 | ①三重门各一判据（状态门/信号门/金字塔分批） ②喂 S2 买入侧（横切） ③护盘滞后 40 天~半年=可考假说 ④defensive_asset_whitelist.py 327 行在档；sim_daily_runner.py:149-157 已用 510300 代理+no_chase 姿态（新发现） ⑤白名单格内容 Owner 专属 ⑥ETF 日线 2021-03 起 11 万行 | 1 | calibration | 否 | 资金门位=Owner 保留面（不阻卡，判据只考信号面）；国家队持仓明细面待 market_etf_share_snapshot 量窗 |
| TDM-X-S1 | ①组枢纽：六桶+三族并行+融合=整链 vs 单档问题 ②下游 S1-01..06 全覆盖 ③E 道只考"有/无止损"，未考"多规则 vs 最优单规则" ④collector 327 行在档 ⑤另案 ⑥日频齐 | 1 | ablation | 否 | full 臂待接（collector/fusion 无回测适配器） |
| TDM-X-S1-01 | ①六桶词表+确认模式分流=可判（误清率） ②喂 S1-05 融合 ③t3b exit_gain 配对语义转录 ④collector 在档 ⑤标签矩阵呈现另案 ⑥kline 全覆盖 | 1 | comparison | 否 | blocked_on_impl（三臂需注入确认层形参） |
| TDM-X-S1-02 | ①五路止损+棘轮+降级=≥5 张卡候选（生死线/支撑双触发/分时/前瞻 P(跌)/棘轮） ②喂 S1-05/S1-06 ③E 道已考 atr3x/trail20（禁重复） ④stop_loss_strategy.py 在档 ⑤另案 ⑥分时档需 1min（2021-09 起，窗不兼容 2018 IS） | 1 | comparison | 否 | 分时破位档另卡另窗（长窗数据缺） |
| TDM-X-S1-03 | ①止盈三式各一判据+D50 峰值回撤欠账 ②喂 S2-05 阶梯 ③E 道 verdict_gain 语义转录 ④take_profit_strategy.py 在档、装置无 tp 形参 ⑤另案 ⑥close/high/low+stk_limit 齐 | 1 | comparison | 否 | blocked_on_impl（X_tp schema 维未裁定，草稿 §五 B1） |
| TDM-X-S1-04 | ①三路信号（突破失败/情绪退潮/龙虎榜派发）=三卡候选 ②喂 S1-05/S1-06 ③同族校准模板先例（涨停家数卡） ④breakout_failure_detector.py 在档 ⑤告警面板另案（casebooks=CASEBOOK-001#alert） ⑥突破失败长窗可算、席位表 2022 起、六段态无历史 | 2 | calibration×2 | 否 | 情绪退潮路 blocked_on_data（decision_daily 138 行、emotion_index.stage 非六段） |
| TDM-X-S1-05 | ①权重表+共振+去抖三参=四消融面 ②定 S2-01 路由 ③X 族唯一可独立单测件（草稿在册） ④sell_signal_fusion_engine.py 在档、fexam 无 urgency（Grep 零命中） ⑤另案 ⑥周线 kline_weekly_hfq 在册可算共振 | 1 | ablation | 否 | blocked_on_impl（融合层未接入装置） |
| TDM-X-S1-06 | ①四触发=四卡候选（K≥3/黑天鹅/主力弃庄/KillSwitch） ②绕过融合直送 S2 ③M-50 覆盖折扣在册（两分支无代理） ④strategy_abnormal_exit_orchestrator.py 396 行在档 ⑤另案 ⑥K≥3 长窗可算；主力弃庄仅 2022 起 seat 表 | 1 | comparison | 否 | 黑天鹅分支不可考（无可计算代理，如实声明） |
| TDM-X-S2 | ①执行枢纽：约束层"现实性税"是顶层未问问题 ②下游 S2-01..06 ③官方引擎 exec_caliber 三档在册 ④sell_execution_planner.py 在档 ⑤另案 ⑥分钟线+stk_limit 齐 | 1 | ablation | 否 | 参与率帽/时段约束未实现（装置无 volume 入参） |
| TDM-X-S2-01 | ①路由表+三查+IS 急卖/ICEBERG/恐慌拦截=≥4 卡候选 ②喂 S2-02/03/04/05 ③t3b 配对语义转录 ④planner 在档、无分钟切片器 ⑤另案 ⑥5min 2.96 亿行可考 | 1 | comparison | 否 | blocked_on_impl（分钟执行器缺） |
| TDM-X-S2-02 | ①跌停三步+可卖额度+新股/临停/ST 分支=≥4 卡候选 ②喂 S2-04 ③"约 43% 第 3 日开板"是待考数字非真值 ④t1_sellable.py 在档 ⑤另案 ⑥stk_limit 2015 起 925 万行长窗可算 | 1 | calibration | 否 | 排队位次/封单骤减面 blocked_on_data（tick_depth_5 仅 2 月、l2_tick 空表） |
| TDM-X-S2-03 | ①时段通道分裂+竞价即决十行矩阵=≥3 卡候选 ②喂 S2-01/04 ③口径 A/B 是草稿点名的剩余动作 ④sell_session_router.py 在档+_c4_engine exec_caliber 三档已具备 ⑤另案 ⑥分钟 2021-09 起；竞价簿 2026-07 起（短） | 1 | comparison | 否 | 竞价段长窗不可考（auction 表 2026 起）；新开考通道=Owner 批前置 |
| TDM-X-S2-04 | ①本地停止单+cancel 重挂+SellChase+QMT 三坑=≥3 卡候选 ②喂 S2-06 上报 ③**翻案：草稿记"tick 级语义不可考"，实测分钟线 14.9 亿行 2021-09 起可考分钟粒度** ④local_order_queue.py 271 行在档 ⑤另案 ⑥五档深度断供 | 1 | comparison | 否 | 盘口档判据（快照龄闸门/Escape 检查）blocked_on_data |
| TDM-X-S2-05 | ①阶梯 +1R/+2R/尾仓+MFE 自检=三卡候选 ②反馈喂 S1 权重 ③E 道 verdict_gain 语义 ④scaling_out.py 在档、装置全仓进出 ⑤另案 ⑥daily 全覆盖 | 1 | comparison | 否 | blocked_on_impl（X_ladder 维未裁定+无部分平仓） |
| TDM-X-S2-06 | ①三率+六分类复盘+冷却迟滞带=≥3 卡候选 ②喂 F-C3 归因与 E-L4-12（边在册） ③反馈闭环消融是标准动作 ④sell_execution_quality_tracker.py 210 行在档 ⑤另案 ⑥卖后跟踪窗充足、sim_trade_log 可交叉 | 1 | ablation | 否 | blocked_on_impl（无 urgency 反接：Grep scripts/backtest -i "urgency" 零命中） |

## 四、断言留痕（trae_065 v1.1.0 铁律：判"X 未做/不存在"前必跑）

命令原文与实测输出（`cd D:/ZephyrAlpha/.aidrafts/st-nightmine-20261010 && python -m zephyr.library.lookup state "<kw>"`）：

- `state "本地条件单"` → **零输出（无命中）**
- `state "分时破位"` → **零输出（无命中）**
- `state "熔断五级 状态机"` → **零输出（无命中）**
- `state "六段情绪 退潮"` → **零输出（无命中）**

结论纪律：library.lookup 零命中只证"馆内无该状态条目"，不足以断"实现不存在"，故本车道对"存在性"一律另做文件级实测：
`src/zephyr/risk/core/drawdown_state_machine.py`=773 行、`drawdown_liquidation_guard.py`=209、`security/access_control/kill_switch.py`=456、
`position/core/defensive_asset_whitelist.py`=327、`ex_core/local_order_queue.py`=271、`sell_decision/core/sell_execution_quality_tracker.py`=210、
`trading/strategy_abnormal_exit_orchestrator.py`=396、`sell_decision/core/sell_signal_collector.py`=327 —— **八件全部存在**。
"不存在"的断言因此只限于"回测装置无适配器"这一面，证据=Grep 实测：
`scripts/backtest -i "urgency"` 零命中；`-i "chase"` 仅 `sim_daily_runner.py`/`strategy_screen_c2.py` 两处（前者 `trend_follow_no_chase` 建仓不追高语义，非卖单追单状态机）；
`-i "exec_caliber|vwap"` 命中 `factory_grid_executor.py`/`translated/_c4_engine.py`/`translated/c4_6f8aa44abe0e_vrev019_vwap_band.py`/`validate_p0_cost.py`/`t0_rule_engine.py`（**存在**，据此修正了 X-S2-03 卡的初稿断言）。

## 五、新卡清单（20 张，绝对路径）

1. `D:/ZephyrAlpha/.aidrafts/st-nightmine-20261010/docs/03_modules/_domain_backtest/exam_cards/exit_flow/XFLOW/TDM-X-FLOW__ablation__02_离场信号整链消融总账.yaml`
2. `D:/ZephyrAlpha/.aidrafts/st-nightmine-20261010/docs/03_modules/_domain_backtest/exam_cards/exit_flow/X1/TDM-X-R1__shadow__02_拔电源影子运行对照.yaml`
3. `D:/ZephyrAlpha/.aidrafts/st-nightmine-20261010/docs/03_modules/_domain_backtest/exam_cards/exit_flow/X1/TDM-X-R1-01__comparison__02_熔断五级梯度减仓对照.yaml`
4. `D:/ZephyrAlpha/.aidrafts/st-nightmine-20261010/docs/03_modules/_domain_backtest/exam_cards/exit_flow/X1/TDM-X-R1-02__comparison__02_L3减仓顺序三臂对照.yaml`
5. `D:/ZephyrAlpha/.aidrafts/st-nightmine-20261010/docs/03_modules/_domain_backtest/exam_cards/exit_flow/X1/TDM-X-R1-03__calibration__02_宽基ETF天量与护盘滞后结构.yaml`
6. `D:/ZephyrAlpha/.aidrafts/st-nightmine-20261010/docs/03_modules/_domain_backtest/exam_cards/exit_flow/S1/TDM-X-S1__ablation__02_卖出信号段整体消融对照.yaml`
7. `D:/ZephyrAlpha/.aidrafts/st-nightmine-20261010/docs/03_modules/_domain_backtest/exam_cards/exit_flow/S1/TDM-X-S1-01__comparison__02_六桶分类增益对照.yaml`
8. `D:/ZephyrAlpha/.aidrafts/st-nightmine-20261010/docs/03_modules/_domain_backtest/exam_cards/exit_flow/S1/TDM-X-S1-02__comparison__02_时间止损档对照.yaml`
9. `D:/ZephyrAlpha/.aidrafts/st-nightmine-20261010/docs/03_modules/_domain_backtest/exam_cards/exit_flow/S1/TDM-X-S1-03__comparison__02_止盈族三式对照.yaml`
10. `D:/ZephyrAlpha/.aidrafts/st-nightmine-20261010/docs/03_modules/_domain_backtest/exam_cards/exit_flow/S1/TDM-X-S1-04__calibration__02_突破失败连续次数前瞻收益.yaml`
11. `D:/ZephyrAlpha/.aidrafts/st-nightmine-20261010/docs/03_modules/_domain_backtest/exam_cards/exit_flow/S1/TDM-X-S1-04__calibration__03_席位净卖出派发前瞻收益.yaml`
12. `D:/ZephyrAlpha/.aidrafts/st-nightmine-20261010/docs/03_modules/_domain_backtest/exam_cards/exit_flow/S1/TDM-X-S1-05__ablation__02_融合权重与去抖消融.yaml`
13. `D:/ZephyrAlpha/.aidrafts/st-nightmine-20261010/docs/03_modules/_domain_backtest/exam_cards/exit_flow/S1/TDM-X-S1-06__comparison__02_K3连续破位强清对照.yaml`
14. `D:/ZephyrAlpha/.aidrafts/st-nightmine-20261010/docs/03_modules/_domain_backtest/exam_cards/exit_flow/S2/TDM-X-S2__ablation__02_执行约束层现实性税度量.yaml`
15. `D:/ZephyrAlpha/.aidrafts/st-nightmine-20261010/docs/03_modules/_domain_backtest/exam_cards/exit_flow/S2/TDM-X-S2-01__comparison__02_执行方式路由与流动性三查对照.yaml`
16. `D:/ZephyrAlpha/.aidrafts/st-nightmine-20261010/docs/03_modules/_domain_backtest/exam_cards/exit_flow/S2/TDM-X-S2-02__calibration__02_连续跌停开板概率与次日处置.yaml`
17. `D:/ZephyrAlpha/.aidrafts/st-nightmine-20261010/docs/03_modules/_domain_backtest/exam_cards/exit_flow/S2/TDM-X-S2-03__comparison__02_执行口径净收益对照.yaml`
18. `D:/ZephyrAlpha/.aidrafts/st-nightmine-20261010/docs/03_modules/_domain_backtest/exam_cards/exit_flow/S2/TDM-X-S2-04__comparison__02_本地条件单追单闭环对照.yaml`
19. `D:/ZephyrAlpha/.aidrafts/st-nightmine-20261010/docs/03_modules/_domain_backtest/exam_cards/exit_flow/S2/TDM-X-S2-05__comparison__02_分批止盈阶梯对照.yaml`
20. `D:/ZephyrAlpha/.aidrafts/st-nightmine-20261010/docs/03_modules/_domain_backtest/exam_cards/exit_flow/S2/TDM-X-S2-06__ablation__02_卖出闭环三率反馈权重消融.yaml`

机检：`python` 逐件 `yaml.safe_load` 全绿；20/20 含 `status: preregistered` / `signal_kind` / `pillars_numeric` / `window(in_sample+oos+regimes)` / `buckets` / `pillars` / `target` / `lineage.confidence_writeback` / `data_binding.data_window_evidence` / `preregistered_by: st-nightmine-20261010-L5`，且无 `generated: true`。

## 六、车道收尾自证

- 节点总数 **19** ／ 出卡节点 **19**（每节点 ≥1 卡）／ 新卡总数 **20**。
- 族分布：**comparison 10 / calibration 4 / ablation 5 / shadow 1**。
- `mined_out` 名单：**空**。枯竭判据（mining_sop §3）要求"六向全部已查无/已入卡＋无未挖长尾"，本车道每一节点都仍有下列长尾，故无一可封矿。
- blocked 名单与原因（断供不弃卡，判据面已写死缺哪张表哪一段）：
  - `TDM-X-S1-04` 情绪退潮路 = **blocked_on_data**（六段态历史缺：`decision_daily` 仅 2026-09-16 起 138 行；`emotion_index.stage` 实测为快照阶段枚举非六段）。
  - `TDM-X-S2-02` 盘口排队面 = **blocked_on_data**（`tick_depth_5` 仅 2026-07-24..2026-09-30；`l2_tick` 空表）。
  - `TDM-X-S2-04` 五档深度子面 = **blocked_on_data**（同上）；分钟面已解禁（见长尾⑦）。
  - `TDM-X-S2-03` 竞价段（9:15-9:25 / 14:57 前后）长窗 = **blocked_on_data**（`auction_snapshot` 2026-06 起、`auction_book` 2026-07 起）。
  - `TDM-X-R1` / `R1-01` / `R1-02` 实盘净值与持仓面 = **blocked_on_data**（`account_nav_daily` 仅 5 行），故三卡改用仿真组合净值并披露该近似。
  - `TDM-X-S1-02` 分时破位档 = **blocked_on_data（窗不兼容）**：1min 数据 2021-09 起，与本体系冻结 IS 起点 2018-01-02 不可比，须另卡另窗。
  - `blocked_on_impl` 共性：`exit_simulator.simulate()` 只认 `stop_enabled`，X_tp/X_ladder/time_stop/participation/urgency/五档约束全部需装置扩展（各卡 implementation_gap 已逐件写明）。
  - Owner 门位（不阻卡，阻落地）：X_tp/X_ladder/卖出路径切分三维未经裁定（草稿 §五 B1）；X-R1-03 防御格内容与资金预算=Owner 保留面（B5）；新开考通道与预算（B2/B4）。
- 未挖长尾清单（明列，禁含糊）：
  1. X-S1-02：固定 -7% 生死线档单独对照、支撑破位双触发（硬底+软确认 30 分钟观察窗）、止损棘轮（单向 clamp）违规率审计、前瞻概率止损 P(跌)≥0.65 建议通道可考性、ATR 缺失降级锚（4%/8%）触发占比。
  2. X-S1-03：目标位"次日不板走"封板掩码单独臂（stk_limit 可算）、peak_pnl 回落 X% 的 X 敏感性面。
  3. X-S1-04：除权除息日卖出口径（D68 分母改除权参考价，adj_factor 表在册可考）、假破位影线处置、早盘 9:30-10:00 假信号高发窗的时段可靠性系数。
  4. X-S1-05：urgency 三档的实测分布与档位迁移率、confirm_bars/buffer_pct/量能 1.5× 三参各自的单独消融、周线共振加成的独立贡献。
  5. X-S1-06：主力弃庄分支用 seat 表（2022 起）做短窗旁路增益 pilot、天地板个股级规则（D99 终裁后口径）。
  6. X-S2-01：ICEBERG 随机化与释放间隔抖动、枯竭检测（点差突宽/深度秒撤）、恐慌拦截（低开<-3% 等待窗）与三类绕过、板块联动顺序（跟风→补涨→中军→龙头）。
  7. X-S2-02：新股首日状态机、临停复牌 ±10%、风险警示板 2026-07-06 制度切片（按生效日切片，可卡）、碎股/200 股基准。
  8. X-S2-03：竞价即决十行矩阵（溢价×量能）与量能三口径（5-10%/<3%/>15%）校准、跳空 3%/6% 分档预案、除权日溢价分母。
  9. X-S2-04：SellChase 追单预算 15-20 轮敏感性、QMT 三坑（business_id 幂等/保护限价/on_cancel_error）的可测性。
  10. X-S2-05：按信号强度定分批密度（弱一次走完/强留 runner）、MFE 捕获率<50% 自检的反馈闭环。
  11. X-S2-06：六分类 PANIC 占比>10% 告警可考性、冷却迟滞带 A/B 线与连败阶梯（D106 口径）参数标定、30 日避损率斜率降 30% 降档规则。
  12. X-R1 系列：四层止损作用域×节拍（单票/做T/sleeve/组合）交叉、风控心跳失联降级（M-60 挂载点）、影子件落盘 fail-closed 的工程可靠性面。
  13. 跨节点：X-S2-06→E-L4-12 边与 F-C3 归因的消费侧效果（②下游向仅做了边识别，未做端到端接线考）。
- 建议交叉复挖的 20% 节点名单（≈4 个，供其他车道/下轮对挖）：
  `TDM-X-S1-02`（五路止损仅考 1 路，最厚长尾）、`TDM-X-S2-01`（约束细则最多且与 CST-ASTOCK-001 成本册交叉）、
  `TDM-X-S1-05`（与 E-L1-AGG 六段情绪轴跨流交叉，退潮代理可从他道借六段历史表解冻 X-S1-04 阻塞面）、
  `TDM-X-R1-01`（与 C 流预算带跨流交叉：同一减仓量在预算带内的重复计价风险）。
- 治理留痕：本车道 20 个新 .yaml 属 CREATE-GUARD 需 creation_token 面——禁区明令禁改注册表，故 token 未落册，按草稿 §五 B6 先例（token 随批落）由 Owner/批车道统一登记；
  台账与卡均在工棚 `.aidrafts/st-nightmine-20261010/` 内，临时件仅 `D:/ZephyrAlpha/.runtime/tmp/st-nightmine-20261010/l5_add_pillars_numeric.py`；未执行任何 git 写操作。
