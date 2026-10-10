---
ttl: task_bound
title: L4 挖矿车道台账（position_flow 仓位/风控族，st-nightmine-20261010）
created: "2026-10-10"
sid: st-nightmine-20261010
lane: L4
flow: position_flow
family_id: NIGHTMINE-CAMPAIGN
---

# L4 台账：position_flow 全流 18 节点

真源指针：作业簿=`docs/_working/nightmine_campaign/01_mining_brief.md`；SOP=`docs/01_policies_and_standards/sop/mining_sop/mining_sop_policy.md` v1.7.0（§2 六向/§3 枯竭/§6 自审闸/§7.5 断言纪律）；卡模板=`docs/03_modules/_domain_backtest/exam_cards/entry_flow/L1/TDM-E-L1-S2__calibration__02_涨停家数.yaml`。

节点全集（18）：TDM-P-FLOW, TDM-P-P1, TDM-P-P1-01..06, TDM-P-P2, TDM-P-P2-01..04, TDM-P-P3, TDM-P-P3-01..04。
卡输出目录：`docs/03_modules/_domain_backtest/exam_cards/position_flow/{PFLOW,P1,P2,P3}/`。

## 一、基建账（本车道题型=comparison 对照卡为主，机判面必须绑真实跑批件——逐件实读，非凭记忆）

| 件（绝对路径） | 真实能力（读码所得） | 本车道用法 |
|---|---|---|
| `D:/ZephyrAlpha/scripts/backtest/fexam/exit_sim/exit_simulator.py` | 日收盘粒度 ATR 止损路径依赖仿真器；同一 `simulate(..., stop_enabled)` 双臂同码对照；Wilder ATR14（`atr14_wilder`/`wilder_atr_one`）、月频 top20 权重（复用 `strategy_exam.monthly_topn_signals`）、成本=万0.854 双边（`matching_logic.COMMISSION_RATE` 同源）、窗 IS=2018-01-02..2025-09-30 / OOS=2025-10-09..2026-09-30 | 止损/离场叠层类对照卡的原型装置（满分先例：无止损→有止损 MaxDD +16.5pp） |
| `D:/ZephyrAlpha/scripts/backtest/fexam/exit_sim/prereg_frozen.yaml` | 冻结件范本：`device`（信号源/列 cap24/execution/stop_rules/atr/costs）+ `judge_frozen`（maxdd_improve_pp、verdict_gain=MaxDD 改善≥5pp 且 Sharpe 降≤0.2）+ `recalibration_duty` | 本车道对照卡 `pillars`/`frozen_note` 的写法与判据口径真源 |
| `D:/ZephyrAlpha/scripts/backtest/factory_grid_executor.py` | 考维引擎：`_apply_exit_overlay`(X_stop off/atr3x/trail20, L892/838 已接线)、`_apply_dd_breaker_overlay`(X_breaker off/dd20, L1204/841 已接线)、`_apply_capital_ramp_overlay`(K off→lump/linear_20d/linear_60d/**pyramid** 三档 1/3+1/3×armed(≥×1.03)+1/3×armed(≥×1.06), L1058)、`_apply_thesis_survival_overlay`(M5 逻辑存活, thesis_decay=0.30, L1034 **定义无调用点=未接维**)、`_apply_sector_overlay`、`_apply_industry_topk_overlay`；DEFAULT_CONTEXT={strategy_pool,phase,capital_ramp_enabled=False} | 全部仓位/风控叠层对照卡的跑批正门：双臂=同 recipe 只换 dim 值 |
| `D:/ZephyrAlpha/config/position_recipe_grid_schema.yaml` | 维真源：C_sizing 7 档(equal_weight/mkt_cap/inv_vol/risk_parity/kelly_025/kelly_050/signal_strength)、D1 频率 4 值、D2_rebalance_trigger(periodic/**drift_band**)、E_single_cap(cap5/cap10/cap20)、H_turnover_lambda(0/5bp/15bp)、X_stop、X_breaker、K_capital_ramp(active_if capital_ramp_enabled)、J_regime_switch；industry_anchor=c1_market.industry_class.industry_sw(L1, sws2021_l1) | 单票上限/漂移带/定尺寸/换手惩罚四类约束对照的合法取值面（禁自造档名） |
| `D:/ZephyrAlpha/scripts/backtest/fexam/allocator_shadow.py` | 批4 五套分配器影子考（champion=0.5 等权+0.3 逆波+0.2 动量倾斜；equal_weight/rk08_solo/pa015_solo/sig131_solo）；mSPRT 序贯内核可降级配对 t；只报证据量不判终胜负 | 组合层/仓位档候选的 shadow 族卡装置 |
| `D:/ZephyrAlpha/scripts/backtest/calibrate_cost_tier_redblue.py` | 同格复算多档成本 sharpe（轻档 5bp vs 全档 40bp + 0bp 对照），`run_cost_tier_scan` | 成本门类卡（碰钱面必过成本门）的判据装置 |
| `D:/ZephyrAlpha/scripts/backtest/condition_attribution.py` | 只读归因：grid run net_returns × 条件包 → 达标胞分层 sharpe/年化（胞级仅观察，判据仍=全窗成本门） | 情绪段/条件权限类卡（P3-01 段权限）的分层归因装置 |
| `D:/ZephyrAlpha/scripts/audit/t0_conditional_e4_v3_exam.py`（+ `t0_conditional_e4_exam.py`/`_v2_`） | 做T 条件化双门考试：宏观门 `load_regime_states`/`t1_state`、情绪门 `emotion_state_for`、成本 31.2bp、前置率 0.30、土规 30 对、五态判定 `_verdict_for`；材料资格 M-1 日内粒度/M-2 往返同体/M-3 哈希去重/M-4 涨跌停可行性硬门；输入=`data/backtest_artifacts/bt-*.json` | 做T 族（P2 全段）唯一在册考试件；**日频做T=伪造（H9 §4.2），本族卡一律绑 tick/1min 材料面** |
| `D:/ZephyrAlpha/src/zephyr/signal_ashare/intraday_t0/day_trade_pnl_estimator.py` | MOD-SIG-132：做T 成本模型净盈亏预估（价差−双边佣金−印花税−冲击四要素）+历史相似价差实现率置信度+成交回写校准 | P2-01 成本门（预期价差≥0.3%=CST-T0-001）卡的算法锚 |
| `D:/ZephyrAlpha/src/zephyr/signal_ashare/intraday_t0/t0_point_analyzer.py` / `t0_trading_pipeline.py` | 做T 买卖点识别 / 流水线编排（live 件） | P2-02/03 卡的后端锚（回测化未立项=如实标 blocked_on_impl） |
| `D:/ZephyrAlpha/scripts/backtest/ibt/ibt_runner.py` | 整装回测首跑（IBT-A 等权 / IBT-B 四层联动 regime shrinkage），`--window W_IS\|W_OOS\|W_HOLDOUT\|W_POSTD`+`--sensitivity` 成本敏感性扫描 | 多窗（IS/OOS）+ 牛熊两段判据的执行面 |
| `D:/ZephyrAlpha/scripts/backtest/fexam/calibration_exam.py` | `run_card` 硬读 `status==preregistered`/`signal_kind∈{panel,series}`/`pillars_numeric`；`judge()` 机判面只认 mono_spearman_min/ic_mean_min/ic_ir_min/regime_same_sign/oos_same_sign | calibration 族卡走此正门；comparison/ablation/shadow 族卡 `executor` 字段写明走 grid/exit_sim/shadow 件（禁假称 calibration_exam 能跑对照臂） |

**CH 实测覆盖（ch_data.ch_query 原文，禁裸 duckdb；临时件 `D:/ZephyrAlpha/.runtime/tmp/st-nightmine-20261010/tables.txt`）**

| 表 | 实测覆盖/行数 | 备注 |
|---|---|---|
| `c1_market.kline_daily_hfq` | 1990-12-19..2026-09-30，10,098,785 行；列含 open/high/low/close/volume/amount/**amplitude**/pct_change/**turnover** | 振幅门/止损/ATR 族主轴 |
| `c1_market.kline_1min` | 2021-09-01..2026-10-09，1,493,285,247 行，8,706 符号 | 做T 日内平面（尾盘 14:45/14:50 面可测） |
| `c1_market.kline_5min` | 2021-09-01 09:35..2026-10-09 15:00，296,122,159 行，8,706 符号；时间列=`trade_time`（**非 trade_date**，首探 404=列名错非无数据） | 做T/VWAP 族 |
| `c1_market.tick_depth_5` | 2026-07-24..2026-09-30，130,146,982 行 | 盘口失衡族**仅 ~2 个月**⇒ 断供风险写进卡 |
| `c1_market.emotion_index` | 1991-06-10..2026-10-09，8,661 行；列 stage/emotion_index/components | 情绪段权限门（P3-01/P2-01 状态门） |
| `c1_market.sentiment_panel` | 2026-09-01..2026-10-09，52 行 | 极短，禁作 IS/OOS 主轴 |
| `c1_market.limit_up_pool` | 2026-09-01..2026-10-09，1,426 行 | 梯队面短窗 |
| `c1_market.stk_limit` | 在册（列 limit_up/limit_down/limit_pct/st_flag/board，valid_from/to PIT） | M-4 涨跌停可行性硬门口径源 |
| `c1_market.industry_class` | L1 快照 10,472 行（schema §2.1 已知问题：符号格式混用/坏行 1/新旧冲突 1） | 同题材扎堆帽（P1-05） |

**DS 反查（`docs/01_policies_and_standards/_registry/catalogs/data_asset_registry.yaml` 原文行号）**：DS-009=`position.snapshot`(L1081 契约件非 CH 表)、DS-067=`execution.position_tracker`(L3144 本地目录)、DS-082=`market_data.stk_limit`(L3695)、DS-107=`event.news_sentiment_window`(L4661)、DS-150=`c1_market.kline_daily`(L6459)。
⇒ **P1-01/P1-05/P2-04 的 DS-009/DS-067 = 本地账务件，不在 CH**——回测面持仓台账只能取合成/仿真态，此事实逐卡如实披露。

**同族先例（负结果与满分卷都在册）**：`docs/_working/matrix_campaign/mining/st_p_daytrade_mining.md`（18 节点接线级 A3/B4/C8/D3；P2 做T "日频必伪造禁做"；K 维=金字塔族最近路径）；`docs/_working/fexam/strategy_exam_scores_v1.yaml`；`docs/_working/t0_matrix/t0_conditional_e4_v3_verdict.md`。

## 二、逐节点六向台账

| node_id | 六向结论(每向一句) | 新卡数 | 族分布 | mined_out? | blocked 原因 |
|---------|-------------------|--------|--------|-----------|-------------|
| TDM-P-FLOW | ①上游=TDM 原文仅结构指向（terminal 聚合，无 data_refs/factor_refs），判据性陈述=“持仓半边是否有增益”→整链消融卡；②下游=git grep TDM-P-FLOW 仅 TDM/battle_map(BM-BUY-03) 命中，无回测消费方（台账 §2 先例记“已在考卷行使”=weights ffill 语义）；③算法=同族先例 exit_sim 双臂（prereg_frozen judge_frozen 口径逐字承）+ 机构三件套映射为“响应(叠层增量)/时滞(触发滞后收盘失真)/条件稳定(牛熊两段)”；④后端=三 overlay 均有调用点（L838/841）+K 维 L1058 折叠待开闸；⑤呈现=持仓动作清单已在 live 仪表盘，只登记；⑥数据=kline_daily_hfq 1990-12-19..2026-09-30/10,098,785 行足覆 IS+OOS，DS-009/DS-067=本地账务件非 CH（已在卡内披露） | 1 | ablation×1 | 是（六向齐，长尾=本流“日频做T 平面”归 P2，无他漏） | — |
| TDM-P-P1 | ①上游=枢纽六子环（对账/分级/逻辑/风险/组合/结论）判据=“汇总层比单腿多什么”→四臂增量卡；②下游=P1-05→P2-04 减仓指令、P1-04→X 流离场（TDM 原文），edges 反查确认消费方；③算法=先例=prereg_frozen.yaml 二臂，本卡增量=补单腿与并开的**交互项**（枢纽层存在性判据）；④后端=position_checkup_orchestrator 是 live 只编排零下单观察态件（TDM algo_note_zh 原文），回测等价物=两 overlay（已接线实读 L838/841）；⑤呈现=动作清单呈现只登记；⑥数据=同 PFLOW 面，无新增缺表 | 1 | comparison×1 | 是（六子环各自单腿已下探 P1-0x 节点，枢纽层增量已入卡；长尾=“盘中持续跑一遍”平面需 tick 装置，已归 P2 族卡） | — |
| TDM-P-P1-01 | ①上游=QMT 桥 Stock.csv × 本地 strategy_book 逐笔核对，DS-009=position.snapshot 契约件、DS-067=execution.position_tracker 目录件（registry L1081/L3144 实读）——**均非 CH 表，回测平面无真实台账**；②下游=P1-02/04/05 全依赖台账（股数/成本/六态），失真沿链放大→改立“成本口径”对照考法；③算法=复权口径对照（后复权 vs 原始价）在机构侧是常识性 Pitfall，内部锚=adj_factor 表在册 + kline_daily/kline_daily_hfq 双表并存；④后端=对账件是运维件（st_p_daytrade_mining.md 判 D 类“账务运维，天然不进回测”），回测侧需“同一持仓两套成本口径”双臂件——缺；⑤呈现=不平账标红人工核对，只登记；⑥数据=adj_factor/kline_daily 在册，覆盖待探针。结论=立 1 卡标 blocked_on_impl（不凑 preregistered） | 1 | comparison×1 | 是（D 类可考面已榨取：口径失真面已入卡，台账本体无回测平面） | blocked_on_impl：缺“双复权口径持仓成本/止损触发”双臂统计件 |
| TDM-P-P1-02 | ①上游=data_refs=DS-150(c1_market.kline_daily)+IND-VOL-001(ATR)，判据陈述“WATCH<1.5×ATR / HOLD>3×ATR / 浮亏>3%”逐条拆卡；②下游=分级→监控频率→告警量，消费方=盘中告警（live），无回测消费方；③算法=三件套映射=响应曲线（带宽 vs 未来下行单调）+条件稳定（牛熊同号）+**告警膨胀代价**（碰钱面判据成组）；④后端=position_triage._triage_atr 实读 L126-163（前置支 current<=stop→WATCH，L151-153 注释=旧 abs 对称化误判 MONITOR 的案底），双臂对照件缺；⑤呈现=三档颜色，只登记；⑥数据=hfq 表 high/low/close 齐备可算 ATR；DS-150 与考用 hfq 表口径差已入卡披露 | 2 | calibration×1 + comparison×1 | 是（阈值面/案底面均已入卡；长尾=threshold_delta 双向反馈 BM-POS-09 面——属 P2-04→P1-02 反馈环，列入交叉复挖名单） | 其中 comparison/03 blocked_on_impl（缺双臂分级统计件） |
| TDM-P-P1-03 | ①上游=data_refs=DS-082(stk_limit)+DS-107(news_sentiment_window)，factor_refs=FCT-SENT-012/FCT-MOM-022；algo_note 四腿（打板梯队/因子漂移/事件衰减/趋势不破）+三态输出，常数实读 thesis_survival.py:67-70（0.30/0.60/0.50/0.80）；②下游=失效→转离场评估（消费方=X 流），edges 反查成立；③算法=引擎已把“入场理由=因子秩”回测化（_apply_thesis_survival_overlay L1034-1055，docstring 自称 P1-03 回测化），阈值与 live 侧 0.30 同源——两卡互为机制/落地闭环；④后端=**函数零调用点+schema 无维**（grep 实读，已作证据指针入卡）；⑤呈现=三态标签，只登记；⑥数据=因子面 technical_indicator 在册、事件衰减面 DS-107 短（news_sentiment_window 属事件族另探）。四腿中“多因子漂移”腿已入 2 卡；打板/事件/趋势三腿另见长尾 | 2 | calibration×1 + comparison×1 | 否——长尾未清：打板仓“情绪梯队还在不在”腿（六段 CSV 可用但 ignition 仅 2 天，样本先证）、事件仓“利好兑现”腿（需 DS-107 覆盖探针）、做T底仓“趋势不破”腿（归 X/趋势族边界） | comparison/03 blocked_on_impl（M5 维未注册未接线） |
| TDM-P-P1-04 | ①上游=TDM 原文四类否决线（生死线-7%/时间止损 盈利5日不涨·亏损3日不回/财报前1日·解禁前3日禁区/板块退潮）；live 侧常数实读 ashare_stop_loss_engine.py:86-146（FIXED_PCT 0.07、daily/weekly/monthly loss limit 0.02/0.05/0.10、halt 1/2/3、auction 0.02、intraday_vwap_break 0.01、sector_momentum −0.02，六类触发枚举 SUPPORT_BREAK/LOGIC_INVALIDATION/AUCTION_DISAPPOINT/INTRADAY_BREAK/SECTOR_EBB/LOSS_LIMIT）；②下游=触发即转 X 流离场+冻结做T/加仓资格（消费方=P2-01/P3-01 资格门，跨流硬约束）；③算法=先例满分卷（ATR 止损 无止损→有止损 MaxDD +16.5pp）+四臂扩展（atr3x/trail20/tp20 引擎全现成）+按 ATR% 三分位的自适应-vs-固定分层检验；④后端=X_stop 已接线 L838；固定 -7% 档引擎缺（L910 合法值实读）；⑤呈现=否决红标，只登记；⑥数据=板块退潮面 **kline_sector 仅 2025-07-18..2026-09-30(86,033 行) 不可用，kline_sector_880 有 2020-03-17..2026-10-08/785,204 行（改用后者）**；事件禁区面 CH 无个股级财报/解禁表（system.tables LIKE unlock/restrict/disclos/report/holder 仅命中 execution_report）⇒该卡 blocked_on_data | 4 | comparison×2 + calibration×2 | 否——事件禁区腿卡未写（缺表）、亏损限额腿（daily/weekly/monthly limit + halt days 递进）尚未立卡 | comparison/03 blocked_on_impl；禁区腿将 blocked_on_data |
| TDM-P-P1-05 | ①上游=data_refs=DS-009（契约件非 CH，仿真权重替代已披露）；三查原文逐条拆卡（单票>20%/偏离>25% 越带/同题材>3 只）；②下游=越带者下发 P2-04 减仓指令（TDM 原文，edges 实读）；③算法=约束类三件套=binding 率（约束是否真的咬到）+剂量-响应（cap5/10/20、3/5 只）+“真实竞品对照”（drift 必须对更密周期调仓比而非稀疏调仓，否则对照失真）；④后端=cap/drift 两维引擎现成（L683/812、L697-722 实读），同题材只数帽无 overlay（近亲 _apply_industry_topk_overlay L1119 语义不同，禁张冠李戴）；⑤呈现=三查红标只登记；⑥数据=industry_class L1 锚 + schema industry_anchor 已知缺陷（符号混用 5534/4938、坏行 1、冲突 1）已写进卡的分层前置。★**挖出口径冲突**：TDM 写“偏离>25% 越带”，引擎实装 `thr=0.10*2.0`（即平均偏离 10%），差 2.5 倍——须由卡产出 binding 判定后提请纠口径 | 3 | comparison×2 + ablation×1 + shadow×1（共 4 件） | 是（三查逐条入卡，影子面另立；长尾=相关性扎堆的“相关系数”口径替代只数帽，属 T3b 扩档） | ablation/04 blocked_on_impl（缺只数帽 overlay） |
| TDM-P-P1-06 | ①上游=汇总五路体检结论（判据性陈述=“仲裁有没有价值”而非“每条线准不准”）；②下游=动作清单→P2-01 资格/P2-04 减仓/X 流离场（消费方反查成立）；③算法=全因子 2^3+腿序开关（机构“信号组合与优先级”检验=响应/交互/条件稳定三件套的仲裁版）；④后端=position_adjudication_center 为 live 裁定中心，回测侧三腿中 thesis 未接线（P1-03 同一施工位），无腿序 runner；⑤呈现=“人工确认默认态”属 live 运维面，登记不施工（st_p_daytrade_mining.md 判 D 类）；⑥数据=同 P1 面，无新增缺表 | 1 | comparison×1 | 是（回测平面可考面=仲裁有效性已入卡；人工确认/审计面明确判为不可回测平面，非“未挖”） | blocked_on_impl（缺三腿全因子 runner+序开关） |
| TDM-P-P2 | ①上游=factor_refs=FCT-INTRADAY-025/015、battle=BM-SELL-08；原文纪律“做T 不改变底仓股数、与加减仓是三件事”=可判不变量；②下游=P2-01→02→03 链与 C3 归因（TDM 原文“成功/失败/损耗统计喂 C3 归因”）；③算法=同族在册先例逐字继承（t0_conditional_e4_v3 五态判定与四判据）；④后端=V3 考试件+cost_trio build_pairs+t0_cost_model+day_trade_pnl_estimator（MOD-SIG-132）四件齐备可跑；⑤呈现=图13 盘中段时序（先例 §4），只登记；⑥数据=1min 表 2021-09-01..2026-10-09/14.9 亿行、材料 66 条目、tick_depth_5 仅 2 个月。★先例负结果如实继承：V3 主考 0 对、禁做侧 26 对净均 −36.26bp、n<30 禁出方向（裁定#325 禁全绿） | 1 | comparison×1 | 是（枢纽层“底仓恒等不变量+腿有无”已入卡；三策略/闭环/优先级分别归 P2-02/03 与 P2-04） | — |
| TDM-P-P2-01 | ①上游=data_refs=DS-150(kline_daily，amplitude 列实测在册)+FCT-INTRADAY-028；三道门常数逐条实读（3% 振幅/0.3% 价差 T0_MIN_EDGE_RATE=Decimal("0.003")/0.15% 双边成本/MACRO_TREND_STATES={'r3','r12'}/MACRO_VOL_H=0.700/PRECONDITION_HIT_RATE_MIN=0.30/PAIR_GATE=30）；②下游=过门才进 P2-02 调度（TDM 原文），否决即冻结做T 资格还由 P1-04 触发；③算法=六向对照设计=逐腿开闭+**互斥诊断**（在册主考 n=0 的真因是两门系统性互斥而非门无效）；④后端=V3/V2/V1 三件 import 复用链齐（宏观门+情绪门+四判据）；⑤呈现=资格红绿标只登记；⑥数据=六段史 CSV 实测 1,822 行但 **ignition 仅 2 天、euphoria 40 天、空白 762 天**——“点火段才加仓/做T”的段权限腿样本先证极稀，已写入卡 buckets/pillars 的样本门 | 1 | comparison×1 | 是（三道门逐腿+互斥诊断已入卡；长尾=振幅门阈 3% 的分位扫描属扩档另卡，已列未挖长尾） | — |
| TDM-P-P2-02 | ①上游=factor_refs 四个日内因子+algo_refs EXA-VWAP/TWAP-001+module_mounts MOD-AU-011；原文三策略名逐条（intraday-surge-fall/orderbook-imbalance/vwap-reversion）；②下游=P2-03 闭环判定；③算法=约束类消融（30% 帽）+策略适配度分状态对照；④后端=t_trade_coordinator（live 编排）无回测重放入口=消融卡缺件；⑤呈现=只登记；⑥数据=**盘口失衡腿 tick_depth_5 仅 2026-07-24..2026-09-30（1.3 亿行，约 2 个月）**⇒该腿策略级对照必须 blocked_on_data（已列在途，禁拿日线冒充）；H9 §4.2 日频做T 伪造禁令逐卡继承 | 1 | ablation×1 | 否——三策略并发-vs-单策略、适配度仲裁-vs-先到先得两卡在途（其中盘口腿受料限） | ablation/02 blocked_on_impl（缺做T 重放件体量开关） |
| TDM-P-P2-03 | ①上游=原文三判据（5 分钟核对/14:50 无条件平仓/股数不变+总成本降=成功）+algo_refs DAL-T0-CLOSE；②下游=“成功/失败/损耗统计喂 C3 归因”（消费方=C3 归因，跨流）；③算法=过夜敞口对照=跳空尾部双臂（机构“日内策略不留隔夜”标准检验）；④后端=闭环核对在 t0_trading_pipeline（live），配对识别可 import V3 件；⑤呈现=只登记；⑥数据=1min 表 14:50/09:30 两点可取（覆盖实测），日开盘第二口径用 kline_daily_hfq.open 复核 | 1 | comparison×1 | 否——C3 归因污染面（混算 vs 分算两口径的底层策略指标差）与“盘中核对频率 5 分钟”敏感性在途 | — |
| TDM-P-P2-04 | ①上游=data_refs=DS-009、battle=BM-POS-09；原文三判据（漂移越带减回/置换 1.5×/改善>2×成本/风控优先于做T）；②下游=减仓指令的执行流（E/X 流）；③算法=再平衡节奏六臂（在册 D1×H 维真实可用）+门槛消融+优先权冲突集；④后端=rebalance_engine 三字段实读（expected_improvement/transaction_cost/improvement_ratio，L126-128）但回测侧无按改善比裁剪动作的 overlay=施工位；⑤呈现=只登记；⑥数据=全在 hfq/technical_indicator 面，无缺表 | 2 | comparison×1 + ablation×1 | 是（四条判据逐条入卡，其中两条落 blocked_on_impl；无剩余长尾） | ablation/03 blocked_on_impl（缺改善比裁剪 overlay+优先权开关） |
| TDM-P-P3 | ①上游=枢纽四步原文（资格门→金字塔→量级→时点）+核心纪律“只加浮盈”；②下游=P3-01..04 四子环（edges 实读）；③算法=“分批动因分离”对照（价格触发分批 pyramid vs 时间触发分批 linear_20d/60d——若时间爬坡全面更优则“浮盈才加”的机制叙事被证伪，这是本枢纽最硬的可证伪点）；④后端=K 维在册且函数完整（L1058-1116），仅 context 折叠（DEFAULT_CONTEXT L122 false、t3b 预注册亦 false）⇒开闸=配置位非代码位；⑤呈现=只登记；⑥数据=hfq close 足。★挖出口径冲突：引擎等额三档 vs live 递减 1/2（详见 P3-02 卡） | 1 | comparison×1 | 是（枢纽层“有无爬坡+分批动因”已入卡，四子环各归其节点） | — |
| TDM-P-P3-01 | ①上游=factor_refs=FCT-MOM-022；四重门逐条（浮盈/段权限/亲和度>0/熔断禁加），live 常数实读 pyramiding_rules.py:76-81（_PHASES_ALLOW={IGNITION,EXPANSION}、_CIRCUIT_BAN_LEVELS={L2,L3,L4}）；②下游=全过才进 P3-02 规则层（TDM 原文）；③算法=红线双臂（浮盈加仓 vs 摊平）+段权限分层归因；④后端=引擎 pyramid 隐含浮盈条件（armed 需 ≥×1.03）但**无段门/无熔断门/无亲和度门**（全文实读只有价格档）⇒①②腿各需施工；⑤呈现=只登记；⑥数据=六段史 CSV 实测 1,822 行且 **ignition 仅 2 天、euphoria 40 天**——段权限腿的“点火”子集原理上不可判，已在卡内把可判子集改写为 expansion-vs-distribution/capitulation 并列样本门。正查留痕：`library.lookup state "金字塔加仓"` 命中 2026-09-04 讨论 L633（“P3 金字塔加仓规则…全网+全项目核查均无承载”）与 2026-09-09 blueprint L203（“禁补亏损仓 在码 | MOD-POS-027”）——两说并存，本车道以更晚的码内实读为准并如实附两条 | 2 | comparison×2 | 否——③亲和度腿与④熔断禁加腿未立卡（亲和度无在册计算件、熔断级 L2-L4 与 X_breaker 帽带不同层） | comparison/02 blocked_on_impl（缺向下摊平 mode） |
| TDM-P-P3-02 | ①上游=三规则原文（递减/阶梯 2.5-3%/限次 3）+live 常数实读 PyramidingConfig L85-91（max_tranches=3、halving 1/2、ladder_min_pct=0.025）；②下游=量级核算 P3-03；③算法=档序三臂对照（递减/等额/递增=反金字塔）+阶梯阈值扫描+“跌破上次加仓价停止计划”的语义核对；④后端=引擎 tranche 权重硬编码 1/3（L1114）⇒递减/递增臂需参数化；⑤呈现=只登记；⑥数据=hfq close+entry 锚足用。★**在册口径冲突（本车道最重要发现之一）**：live=递减 50% 减半 vs 引擎=等额三档，且阶梯 live 取下限 2.5% vs 引擎 3%/6%——两者不能同时“正确”，须由考试产出 binding 证据后提请纠口径 | 2 | comparison×1 + calibration×1 | 否——阶梯阈值扫描臂（2.5/3/5%）与“限次 3”消融卡在长尾 | comparison/02 blocked_on_impl（tranche 权重与阶梯阈值需入参） |
| TDM-P-P3-03 | ①上游=四轨融合原文+实读 position_sizing_engine.py:104-182（MARKET_REGIME_CAPS、SIZING_BASIS_* 十枚举、vol_sigma_multiplier=2.0、var 0.025/cvar 0.04、max_participation_rate=0.15、exit_days_hard=3/soft=1、capacity_warn_ratio=0.80）；②下游=加仓量级→P3-04 执行与 P1-05 组合体检；③算法=C 维七档在册对照（回测等价物）+风险恒定消融+“等权不被任何风险档击败则 sizing 引擎=过度工程”的反向允许；④后端=mkt_cap/kelly 两臂需 run_batch 预加载宽表（件内显式抛错 L650/667，未加载判 DATA_NOT_LOADED 非 FAIL）；⑤呈现=只登记；⑥数据=daily_valuation（ch_data.T_DAILY_VALUATION 在册）与 60 日收益矩须实探，已把缺料判据写进卡；无缺表 | 2 | comparison×1 + ablation×1 | 否——SIZING_BASIS 十枚举逐个/风险帽档位/ADV 规模维在长尾 | ablation/03 blocked_on_impl（缺“随加仓档重算止损线”保本腿；引擎 entry 锚不随加仓重置=L913-915 实读） |
| TDM-P-P3-04 | ①上游=时点二选一原文+algo_refs EXA-TWAP-001/EXA-IS-001+module_ref position_limit_enforcer；②下游=下单复用建仓执行件（E 流边界，只登记不越界）；③算法=把“明日高开概率>70%”这句承诺直接证伪（BM-PLAN-02 口径），强制同报无条件基础高开率防条件概率自欺；执行时点三臂（即时/14:45/次日开盘）；④后端=1min 取数件 ch_data 现成，VWAP/TWAP 切片未考（长尾）；⑤呈现=只登记；⑥数据=1min 2021-09-01..2026-10-09（14.9 亿行）/5min 296,122,159 行/kline_daily_hfq 含 volume+low ⇒ 缩量回踩形态可日频构造，覆盖实测通过。★内部先例（2026-09-04 讨论 L711：缺口当日回补 75%、跳空负向因子年化 -25%）与本卡方向部分冲突⇒已按“允许承诺失实”写成治理产出卡而非策略判负卡 | 3 | calibration×2 + comparison×1 | 否——“未成交不追价次日重走资格门”与 TWAP/IS 执行切片在长尾 | — |

### 2.1 补记与自纠（禁让台账自相矛盾）

- P1-04 实际新卡数=5（comparison×2 + calibration×3，含 blocked_on_data 的事件禁区卡），上表原记 4，以本行为准。
- P1-05 实际新卡数=4（comparison×2 + ablation×1 + shadow×1），上表原记 3（括号已注“共 4 件”），以本行为准。
- P2-02 第 2 卡已补：三策略并发-vs-先到先得（主判据=仲裁信息量 A vs E，而非 A vs 单策略——防“并发必然更好”的默认叙事）⇒ P2-02 新卡数=2，其中 comparison/03 标 blocked_on_data（tick_depth_5 仅约 2 个月 + 分腿样本必破 30 对土规线）。
- P2-03 追加内部在册实证可引：`docs/_working/2026-09-04-trading-decision-map-discussion.md` L711“缺口当日回补 75%/极端低开 -6% 以下史上 3 次 5 日后平均 +7.19%/跳空负向因子年化 -25%”⇒ 过夜双臂的符号方向已被部分预答，卡面仍按“允许反向结论”写死。
- **P1-02 封矿判定收回**：threshold_delta 双向反馈（BM-POS-09；码内 _MAX_THRESHOLD_DELTA=0.10 与 L145-149 的 delta 扣阈）是新的候选考法（反馈环对分级稳定性与告警膨胀的影响），非扩档 ⇒ 改判“未封矿”。
- **P1-05 封矿判定收回**：相关性扎堆帽与只数帽约束对象不同（一个是共因权重、一个是持仓只数），属新候选 ⇒ 改判“未封矿”。

## 三、探针账（mining_sop §7.5 资产状态断言纪律：负存在断言必挂三源指针）

工具=`python -m zephyr.library.lookup state "<关键词>"`（三源=馆索引+git log 近 90 天+工棚面），全文落
`D:/ZephyrAlpha/.runtime/tmp/st-nightmine-20261010/lookup_state.txt`。摘录：

| 关键词 | 命中摘录（指针） | 本车道用法 |
|---|---|---|
| 金字塔加仓 | `docs/_working/2026-09-04-trading-decision-map-discussion.md` L633“三处真正空白=…P3 金字塔加仓规则（全网+全项目核查均无承载）”；`docs/_working/2026-09-09-tdm-growth-blueprint.md` L203“| 7 | 金字塔加仓（资格门+递减）| C9+C10 | 4105b58e / MOD-POS-027 | ‘禁补亏损仓’红线在码；总加仓≤首仓” | 两说并存（09-04 说无承载 / 09-09 说已在码）——本车道以**码内实读**裁定：live 侧 pyramiding_rules.py 存在且带 PyramidingConfig，回测侧 _apply_capital_ramp_overlay 存在但 K 维折叠未开闸。该对撞已附进 P3/P3-01/P3-02 三卡的 data_window_evidence |
| 做T 回测 | `docs/_working/archive/2026-09/c_class_scattered/2026-09-07-tdm-backtest-protocol.md` L36“G4 D50 棘轮+做T配对核算器 | B-04 | ⛔ 未施工…回填前回测报告强制标注‘无棘轮/无配对’覆盖折扣” | P2 族四张卡全部继承“无棘轮/无配对覆盖折扣”标注位；支撑 P2-02/P2-03 缺件判定非臆断 |
| 摊平 亏损仓 | `docs/_working/fullflow_mining/02_tdm_decision/11_f44_p3_pyramiding.md`、`fullconnect_campaign/e_decision_chain/08_f44_p3_pyramiding.md` 等 12 处命中 | “向下摊平双臂”在馆内=被讨论过但未成考法 ⇒ P3-01/comparison/02 作净新增考法（净零声明：不替代任何既有卡） |
| 尾盘 加仓 | `docs/_working/archive/2026-09/design_memos/69_trading_decision_map.md` L448（P3 四步原文含“04 时点与执行（缩量回调/尾盘窗口 BM-PLAN-02）”）；`2026-09-04-trading-decision-map-discussion.md` L711 隔夜实证三条 | ①BM-PLAN-02 承诺原文位置核实；②P3-04/calibration/02 与 P2-03/comparison/02 的内部先验对撞已写进判据（允许“70% 承诺失实”这一产出） |
| 加仓 消融 考卷 | `docs/_working/2026-10-09-tdm-exam-card-system-plan.md`、`fullcirc_closeout_chief/t3_fullflow_exam_mining.md`、`2026-09-13-strategy-factory-pipeline-discussion.md` | 消融族已有制度位 ⇒ 本车道 ablation 卡族口径不与既有体系冲突，未另立族 |
| 缺表断言（财报/解禁日历） | `system.tables` LIKE 探针（unlock/restrict/disclos/report/express/holder）仅命中 `execution_report`；`calendar_event` 列结构实读=宏观发布类（event_date/event_type/pub_value/exp_value/prev_value），无 symbol 维 | P1-04/calibration/06 标 blocked_on_data，附命令原文与列结构双证据（空结果先判静默失败：本次为列结构确证，非查询失败） |
| 缺件断言（固定-7% 臂/只数帽/保本上移腿/向下摊平臂/做T 体量帽/腿序仲裁） | 逐条 grep 实读：`factory_grid_executor.py:910`（合法 stop_mode 仅 off/atr3x/trail20/tp20）、`:1076-1077`（ramp_mode 仅 lump/linear_20d/linear_60d/pyramid）、`:1112-1116`（tranche 硬编码 1/3 且档成交不回传）、`:913-915`（entry 锚不随加仓重置）、`_apply_thesis_survival_overlay` L1034 零调用点、行业族仅有 `_apply_industry_topk_overlay`（动量 Top-K，非只数帽） | 11 张 blocked_on_impl 卡的“缺件”全部挂代码行号指针，无一条凭记忆 |

念想引擎（LSG 云 qwen）本车道**未调用**（0/8 次），如实登记为“未使用该通道”，不作“查无”。

## 四、车道收尾（作业簿 §五 MUST 项，逐条可核）

- **节点总数**：18（position_flow 全集，逐节点从 `config/trading_decision_map.yaml` 读全字段，无遗漏；
  节点明细快照=`D:/ZephyrAlpha/.runtime/tmp/st-nightmine-20261010/pos_nodes.json`）。
- **已挖数（六向全部留痕）**：18/18。
- **新卡总数**：34（全部另建新文件，NN 从 02 起；零触碰 `generated: true` 骨架件）。
  机器校验（本车道实跑）：34/34 YAML 可解析，且必填面齐
  （status/signal_kind/pillars_numeric/window 三件/buckets/pillars/target/
  lineage.confidence_writeback/preregistered_by=st-nightmine-20261010-L4/preregistered_at/discipline/
  data_binding 四子项含 data_window_evidence 命令原文）。
  - status 分布：preregistered 21 / blocked_on_impl 11 / blocked_on_data 2。
  - **族分布**：comparison 20 / calibration 8 / ablation 5 / shadow 1（碰钱面以对照为主，符合车道设计）。
  - 每节点卡数：PFLOW 1、P1 1、P1-01 1、P1-02 2、P1-03 2、P1-04 5、P1-05 4、P1-06 1、P2 1、P2-01 1、
    P2-02 2、P2-03 1、P2-04 2、P3 1、P3-01 2、P3-02 2、P3-03 2、P3-04 3（合计 34）。
- **mined_out（封矿；结构判据=六向全部“已查无/已入卡”且无未挖长尾）名单 8 个**：
  TDM-P-FLOW、TDM-P-P1、TDM-P-P1-01、TDM-P-P1-06、TDM-P-P2、TDM-P-P2-01、TDM-P-P2-04、TDM-P-P3。
- **未封矿（有明列长尾，见下）名单 10 个**：TDM-P-P1-02、TDM-P-P1-03、TDM-P-P1-04、TDM-P-P1-05、
  TDM-P-P2-02、TDM-P-P2-03、TDM-P-P3-01、TDM-P-P3-02、TDM-P-P3-03、TDM-P-P3-04。
- **blocked 名单与原因**：
  - blocked_on_impl 11 张：P1-01/02（缺复权口径可切换的双臂失真件）、P1-02/03（缺双臂分级统计件）、
    P1-03/03（M5 维未注册未接线，函数零调用点）、P1-04/03（缺固定比例止损档）、
    P1-05/04（缺同题材只数帽 overlay）、P1-06/02（缺三腿全因子 runner+腿序开关）、
    P2-02/02（缺做T 重放件体量开关）、P2-04/03（缺按 improvement_ratio 裁剪动作+优先权开关）、
    P3-01/02（缺向下摊平 mode）、P3-02/02（缺 tranche 权重与阶梯阈值入参）、
    P3-03/03（缺随加仓档重算止损线的保本腿）。
  - blocked_on_data 2 张：P1-04/06（CH 无个股级财报披露日/解禁日历表）、
    P2-02/03（tick_depth_5 仅 2026-07-24..2026-09-30 约 2 个月，且做T 材料全库仅 26 对 <30 土规线）。
  - 每张 blocked 卡都写了解锁条件与所需接口签名（禁“缺件”两字交差）。
- **未挖长尾清单（明列，逐条可续挖，不作封矿）**：
  1. P1-02：threshold_delta 双向反馈环（BM-POS-09，|delta|≤0.10 扣阈）对分级稳定性与告警膨胀的影响。
  2. P1-03：打板仓“情绪梯队还在不在”腿（六段 CSV 可映射但 ignition=2 天需先证样本）；
     事件仓“利好兑现”腿（event_decay 0.50/0.80，需 DS-107 news_sentiment_window 覆盖探针）；
     做T 底仓“趋势不破”腿（与 X/趋势族边界，只登记不越界）。
  3. P1-04：亏损限额腿（daily 0.02/weekly 0.05/monthly 0.10 + halt 1/2/3 递进约束，现码实存零考法）；
     竞价不及预期腿（auction_discount_threshold=0.02，auction_snapshot/auction_book 在册可探）；
     分时破位腿（intraday_vwap_break_threshold=0.01，1min 可算 VWAP，考法未立）。
  4. P1-05：相关性扎堆帽（与只数帽不同对象）；概念板口径（concept_sector+sector_constituent）稳健性复跑。
  5. P2-02：三策略各自适配段（surge-fall/vwap-reversion/orderbook × 六段）——待补料后开。
  6. P2-03：C3 归因污染面（做T 腿混算 vs 分算的底层策略指标差）；盘中 5 分钟核对频率敏感性。
  7. P3-01：策略亲和度>0 腿（全项目无在册亲和度计算件，需先定位或立项）；熔断禁加期腿
     （_CIRCUIT_BAN_LEVELS={L2,L3,L4} 与 X_breaker 帽带的层位映射未考）。
  8. P3-02：阶梯阈值扫描（2.5%/3%/5%）；限次 3 消融（max_tranches 放开）。
  9. P3-03：SIZING_BASIS 十枚举逐个考（VaR 0.025/CVaR 0.04/流动性削半/退出时间帽/降级等权）；
     MARKET_REGIME_CAPS 档位表；max_participation_rate=0.15 的 ADV 规模维 binding 面
     （`cost_accounting_ruler.py:28` 已自述“成本线无 participation/ADV 规模维”=缺口在册）。
  10. P3-04：“未成交不追价、次日重走资格门”策略面；TWAP/IS 执行切片与真实滑点分档
      （`90_methodology_open_questions.md` L259 裁定“滑点按策略分档：高流动 0.05-0.1%/打板事件 0.15-0.3%”
      未入任何考卷）。
  11. 跨节点：P1-04 触发即“冻结做T/加仓资格”的跨流硬约束联合后果（否决日同时禁 T/禁加的开闭对照）——
      需 P1/P2/P3 三族同 recipe 联跑，属装置工单非本车道可独立闭合。
- **建议交叉复挖 20%（18×20%≈4 个节点，交他人复挖）**：
  1. **TDM-P-P1-04**（否决线族）——与 exit_flow/X 族重叠面最大：固定生死线 vs ATR 之争、
     保本上移与 trail20/Chandelier 的语义差（prereg_frozen.yaml stop_rules 与引擎 L913-915 两处实现不同）；
     建议 X 族复挖者裁“同一止损语义两处实现”是否收敛唯一。
  2. **TDM-P-P3-01**（红线族）——“只加浮盈”在回测侧由引擎 armed 条件（≥×1.03）隐式实现，
     建议 E 流与 P3 复挖者共同判该隐式实现是否等价于显式红线（潜在静默失效点）。
  3. **TDM-P-P2-04 + TDM-P-P1-05**（再平衡双子）——TDM 25% vs 引擎 10% 漂移带口径冲突横跨两节点，
     建议 portfolio_flow 车道复挖并出纠偏裁定材料（本车道已把 binding 判定写进 P1-05/comparison/03）。
  4. **TDM-P-P3-04 + TDM-P-P2-03**（跳空双子）——“尾盘加仓付更高价差”与“未闭环敞口过夜代价”共用同一
     跳空变量，且与内部先例（缺口当日回补 75%、跳空负向因子年化 -25%）方向冲突，建议交叉定死口径。
- **本车道三项非卡类产出（供总报告）**：
  1. **在册口径冲突两处**：漂移带 25%（TDM）vs 10%（引擎 `thr=0.10*2.0`，factory_grid_executor.py:717）；
     金字塔档序 递减 1/2（live PyramidingConfig）vs 等额 1/3（引擎 L1114），阶梯 2.5% vs 3%/6%。
     两处均属“同一约束两处实现不一致”，任一方对都须纠正另一方（治理项，非本车道权限，已留证据行号）。
  2. **做T 族的材料结构性不足**（是“门与窗互斥”不是“无信号”）：V3 在册实测主考 0 对、全材料 26 对、
     净均 −36.26bp、前置命中率 0.2308；宏观放行 20 对被情绪门 100% 否决；材料窗 dominant 无 r3/r12。
     ⇒ P2 族每张卡都自带 DEVICE_INCOMPATIBLE / INSUFFICIENT_SAMPLE 三态出口，禁把“无料”判成“无信号”。
  3. **六段历史 CSV 的段样本现实**：ignition 2 天、euphoria 40 天、空白 762 天（1,822 行全表实测）
     ⇒ 一切“点火段才加仓/做T”类段权限考法必须先挂样本门，P3-01/comparison/03 已按此改写可判子集。
| TDM-P-P1-01 | （同前，六向已记）补记：卡已落 `P1/TDM-P-P1-01__comparison__02_复权口径对成本与生死线触发对照.yaml`，三臂（hfq/raw/raw×adj_factor）+除权事件集+级联到 P3-01 资格判定，判据成组；缺件=口径可切换的双臂失真统计件（既有件全锁 hfq 单口径：prereg_frozen.yaml atr.price_basis 与 exit_simulator.load_kline 实读） | 1 | comparison×1 | 是 | blocked_on_impl |
