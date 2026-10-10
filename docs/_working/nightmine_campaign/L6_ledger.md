---
ttl: task_bound
title: L6 挖矿车道台账 — portfolio_flow 全流（组合层 16 节点）
created: "2026-10-10"
sid: st-nightmine-20261010
lane: L6
---

# L6 台账（portfolio_flow 组合层，16 节点）

权威名册：`docs/_working/nightmine_campaign/00_lane_roster.yaml` lane=L6（nodes: 16）。

| node_id | 六向结论(每向一句) | 新卡数 | 族分布 | mined_out? | blocked 原因 |
|---------|-------------------|--------|--------|-----------|-------------|

## 基建真源（读码后录，禁虚构接口）

- **影子考引擎**：`scripts/backtest/fexam/allocator_shadow.py`
  - 入口：`run_shadow(roster: dict, out_path: Path, factor_book_path: Path | None, *, session_id: str = "st-matrix-20261006") -> dict`
  - 产出：`out_path`（yaml 册，`doc_type: fexam_allocator_shadow`）+ 同名 `allocator_shadow_report_v1.md`（五套对比表：分配器/IS Sharpe/OOS Sharpe/OOS MaxDD/OOS 收益/判定）
  - 五套分配器（prereg 冻结，roster.ALLOCATORS 同源）：`ALC-THREELAYER-001`(champion=0.5*等权+0.3*逆波+0.2*动量，SIG-131 钳制、RK-08 地板≥0)、`ALC-EQUAL-001`、`ALC-RK08-001`(逆波)、`ALC-PA015-001`(体制倾斜)、`ALC-SIG131-001`(±50%钳制)
  - 证据面：`_evidence_report` = champion vs 各 challenger 配对日收益差（`n_days`/`ann_diff`=年化差/`t_stat`=配对 t）；mSPRT 不可用降级配对 t 留痕；**只报当前证据量不判终胜负**（MOD-PF-008 序贯统计口径）
  - 同窗：批2策略考同窗 `WINDOW_RUN`/`WINDOW_IS`（strategy_exam）+ OOS=`ch_data.WINDOW_HOLDOUT`
  - 简化声明：五套=权重变换向量化和（非 pf_alloc 逐行复用）；MOD 锚 RK-08=risk/core/risk_budget、PA-015=regime_bma_weighting、SIG-131=signal_weight_adjuster
- **数据层**：`ch_data.py` 表名经 TableRegistry（`_REG.table(...)`）；`regime_series(start,end,use_hmm=False)` 默认 SMA200 帘子（`sma200_default`，裁定#489②）；HMM 走 `c1_backtest.regime_snapshot_history`（未过考禁回用）
- **执行器**：`calibration_exam.py:run_card` 机械读 `pillars_numeric`（mono_spearman_min/ic_mean_min/ic_ir_min/regime_same_sign/oos_same_sign）；组合族影子/对比卡由 `allocator_shadow.run_shadow` 侧消费（族门柱：sharpe_vs_baseline_min/maxdd_delta_max/turnover_cost_gate/oos_same_sign/tracking_diff_max），非 run_card 直跑——data_binding 已写清接线，开工接线属考试车道。
- **影子三档假设成交**：最坏/基准/乐观（本车道题型）。
- **基准 v0=fw-tdm-current**：组合层静态权重 Sharpe 0.963（裁定 D8 版本化）。状态断言待 library.lookup 摘录补齐（见文末）。

## 数据可得性实测（本车道探针，命令原文见各卡 data_binding）

- `c1_market.kline_daily_hfq`（T_KLINE_DAILY_HFQ，后复权日线）WINDOW_RUN 2018-01-02..2026-09-30：**9,061,473 行 / 5822 标的**（IS+OOS 全覆盖，组合 NAV/value_panel 底料）。**无 period 列**（加 `period='daily'` 报 404，load_panel 已按缺 period 处理）。
- `c1_market.kline_index` symbol='000300'：**2005-01-04..2026-10-09 / 5284 行**（代理指数→next_day_return/体制带插值）。
- `c1_backtest.regime_snapshot_history`：**2019-04-01..2026-10-09 / 3635 行**（HMM 四态 p_r1..p_r4；裁定#489② 默认走 SMA200 帘子，HMM 仅 use_hmm=True opt-in，未过考）。
- fexam prereg v1 冻结窗：`WINDOW_IS`=2018-01-02..2025-09-30，`WINDOW_HOLDOUT`(OOS)=2025-10-09..2026-09-30；top_n=20 月频等权底仓（roster PREREG_V1.strategy_device）。

## 负存在断言证据（library.lookup state + 手工阶梯，§7.5）

`python -m zephyr.library.lookup state` 四词全部零命中（输出=仅表头 143 字节，馆查零命中≠不存在，场外区边界）：
`"策略路由 state_matrix"` / `"regime_meta_allocator 调权接线"` / `"传感器可靠度加权"` / `"灰度切换 weight_band"`。
降级手工阶梯正查（读码/读图真源，逐条已入台账各卡 data_window_evidence）：
- `allocator_shadow.py` 存在（git ls-files 命中，读全文 378 行）——五套影子考基建**真实**，`allocator_shadow_report_v1.yaml/.md` 尚未产出（本车道只出卡不开考）。
- TDM-F-C1-01/02/03 `module_ref: null` / `red_reason: by_ref_design` → 路由/爬坡切换编排未落码（blocked_on_impl 直证，非本车道新断言）。
- TDM-F-C3-03 `algo_note_zh` 在案："编排未接线——MOD-PA-007 无生产调用方（PFA-1 实证）；base_weights 无来源/月度调权无调度体/PerfScore 无生产者三缺口"→ blocked_on_impl。
- TDM-F-C3-05 `algo_note_zh`："红节点 D7-D13 历史判准率加权 src 零实现，c3_throttle_attribution 仅 design 态"→ blocked_on_impl。
- GC001 逆回购日利率：c1_market 内未查到在册表→C1 预备金现金贡献门柱标 blocked_on_data。

## 逐节点挖矿

| node_id | 六向结论(每向一句) | 新卡数 | 族分布 | mined_out? | blocked 原因 |
|---|---|---|---|---|---|
| TDM-F-C1 | ①上游=预算带六档/预备金/过渡带降仓三判据 ②下游=C2 聚合(sequence 边) ③算法=Millennium pod 单体版+带内插值 ④后端=MOD-PA-003 存在,插值臂影子口径 ⑤呈现=月报现金贡献行(登记) ⑥数据=kline_daily_hfq/index 全覆盖,GC001 缺 | 2 | shadow1/comparison1 | 否(留预备金档长尾) | C1-03 现金贡献 blocked_on_data(GC001) |
| TDM-F-C1-01 | ①上游=L1-AGG 态+state_matrix+fitness ②下游=C1-02(激活集喂权重) ③算法=D125 路由查表 ④后端=module_ref null by_ref_design ⑤呈现=今日激活集卡(登记) ⑥数据=regime_snapshot+kline_index 全覆盖 | 1 | shadow1 | 否(路由体未落码,长尾待接) | blocked_on_impl(路由查表体无落码) |
| TDM-F-C1-02 | ①上游=置信度配比 5:1:1:1:2 ②下游=C2 净指令 ③算法=冠军三层栈 vs 4 挑战者(PF-008 序贯) ④后端=allocator_shadow.run_shadow **真实存在**(读码确认) ⑤呈现=allocator_shadow_report_v1.md ⑥数据=kline_daily_hfq 合成列 ch_backed | 1 | shadow1 | 是(六向齐,旗舰卡绑实基建) | 无 |
| TDM-F-C1-03 | ①上游=A/B 稳态权重 ②下游=执行(E-L4/X-S2) ③算法=双向 weight_band 爬坡 step_cap0.2 ④后端=module_ref null,爬坡器未落码 ⑤呈现=切换事件日志(登记) ⑥数据=kline_daily_hfq 全覆盖 | 1 | shadow1 | 否(爬坡器未落码,长尾) | blocked_on_impl;**owner_gate_required(灰度切换触 production 流转)** |

## 新卡清单（C1，绝对路径）

1. `.../portfolio_flow/C1/TDM-F-C1-02__shadow__02_三层栈冠军挑战.yaml`
2. `.../portfolio_flow/C1/TDM-F-C1__shadow__02_预算带灰度插值.yaml`
3. `.../portfolio_flow/C1/TDM-F-C1__comparison__03_预备金现金贡献.yaml`
4. `.../portfolio_flow/C1/TDM-F-C1-01__shadow__02_激活集路由影子.yaml`
5. `.../portfolio_flow/C1/TDM-F-C1-03__shadow__02_双向渐变vs硬切.yaml`

| node_id | 六向结论(每向一句) | 新卡数 | 族分布 | mined_out? | blocked 原因 |
|---|---|---|---|---|---|
| TDM-F-C2 | ①上游=各 sleeve 净指令(隐式订阅) ②下游=C3 归因(feedback) ③算法=聚合四步(净额→约束→相关性→净流) Millennium pod 同构 ④后端=module_ref 空 red_reason=structural,端到端编排未落地 ⑤呈现=组合净指令(登记) ⑥数据=kline_daily_hfq 全覆盖 | 1 | comparison1 | 否(聚合子件分属他节点,长尾) | blocked_on_impl(structural 聚合器无单件) |
| TDM-F-C2-01 | ①上游=sleeve intent ②下游=执行/归因分摊 ③算法=intent netting 三步+贡献比例分摊 ④后端=MOD-POS-021 firm_risk_aggregator 存在 ⑤呈现=净差单(登记) ⑥数据=kline_daily_hfq 全覆盖 | 1 | comparison1 | 是(六向齐) | 无 |
| TDM-F-C2-02 | ①上游=组合净头寸 ②下游=执行前裁剪 ③算法=六层约束栈顺序过(总仓→回撤→波动→集中→流动→相关) ④后端=MOD-POS-021 存在 ⑤呈现=过哪层裁哪层(登记) ⑥数据=kline_daily_hfq close/volume 齐 | 1 | shadow1 | 是(六向齐) | 无 |
| TDM-F-C2-03 | ①上游=60 日滚动 PnL 相关矩阵 ②下游=C2-02 约束/cluster 上限 ③算法=层次聚类+Ledoit-Wolf 收缩(MOD-POS-011) ④后端=MOD-POS-012 存在 ⑤呈现=cluster heat 表(登记) ⑥数据=kline_daily_hfq 日频截面相关可算 | 1 | comparison1 | 是(六向齐) | 无 |
| TDM-F-C2-04 | ①上游=预算变动/超限事件 ②下游=各 sleeve 收敛窗 ③算法=Tier1/2/3 分层响应+双层防抖 ④后端=MOD-POS-022 存在但 BudgetChanged 事件链未接线 ⑤呈现=交易日志(登记) ⑥数据=kline_daily_hfq 全覆盖(事件需合成) | 1 | shadow1 | 否(事件链未接,长尾) | blocked_on_impl(BudgetChanged 事件链未接线) |

## 新卡清单（C2，绝对路径）

6. `.../portfolio_flow/C2/TDM-F-C2-02__shadow__02_约束栈有vs无.yaml`
7. `.../portfolio_flow/C2/TDM-F-C2-01__comparison__02_净额轧平省成本.yaml`
8. `.../portfolio_flow/C2/TDM-F-C2-03__comparison__02_相关性cluster上限.yaml`
9. `.../portfolio_flow/C2/TDM-F-C2-04__shadow__02_三级响应vs即时强裁.yaml`
10. `.../portfolio_flow/C2/TDM-F-C2__comparison__02_组合聚合vs各自为战.yaml`

| node_id | 六向结论(每向一句) | 新卡数 | 族分布 | mined_out? | blocked 原因 |
|---|---|---|---|---|---|
| TDM-F-C3 | ①上游=各 sleeve 收益/持仓 ②下游=C1 预算倾斜+L1 可靠度反馈 ③算法=归因五路闭环(自我进化发动机) ④后端=module_ref 空 red_reason=structural,编排端到端未接线 ⑤呈现=月报(登记) ⑥数据=kline_daily_hfq 全覆盖 | 1 | comparison1 | 否(子路分属 C3-01..05,父卡全链长尾) | blocked_on_impl(structural 闭环编排未接线) |
| TDM-F-C3-01 | ①上游=逐笔 decision/fill price+账本复权因子 ②下游=C3-02 升降级评审 ③算法=几何 Brinson 三因子+T+1 隔夜漂移切账+TWR/ModifiedDietz 双轨 ④后端=MOD-PF-007 PerformanceAttributionEngine **已落码**(BrinsonResult/is_consistent) ⑤呈现=归因报告(登记) ⑥数据=kline_daily_hfq close+open 齐 | 1 | comparison1 | 是(六向齐,绑真实引擎) | 无 |
| TDM-F-C3-02 | ①上游=composite 60/120 双窗+THD-RETIRE 三线+滚动回撤 ②下游=调权/清退 ③算法=5% 减半/7.5% 冻结自动线+滞回带+四选一 verdict ④后端=MOD-L02-013 lifecycle_state_machine 存在 ⑤呈现=观察名单/verdict(登记) ⑥数据=kline_daily_hfq 回撤可算 | 1 | shadow1 | 否(清退提案链长尾) | **owner_gate_required(清退归零=Owner 保留面)**;可逆减动作 AI 自主 |
| TDM-F-C3-03 | ①上游=PerfScore(C3-01)+base_weights+Shrinkage ②下游=C1 预算带 ③算法=normalize(Base×PerfScore×Shrinkage) floor5/cap40/±10pp+成本闸 ④后端=MOD-PA-007 regime_meta_allocator 文件存在但纯库无调用方(PFA-1)三缺口 ⑤呈现=月报错配双列表(登记) ⑥数据=kline_daily_hfq 齐,PerfScore 生产者未接 | 1 | comparison1 | 否(调度体/PerfScore 生产者缺,长尾) | blocked_on_impl(编排未接线,裁定#257② 在案) |
| TDM-F-C3-04 | ①上游=归因诊断→参数候选组 ②下游=参数真源 registry 工单 ③算法=CPCV+DSR+PBO<30%+WFE>60%/<40% 四道 gate+embargo≥5 日 ④后端=MOD-BT-001 walk_forward 存在(split/whites_reality_check),闭环未转(红节点 G04) ⑤呈现=校准报告(登记) ⑥数据=近 9 年窗支持多切分 | 1 | shadow1 | 否(端到端闭环未接,长尾) | blocked_on_impl(红节点 G04 闭环未转) |
| TDM-F-C3-05 | ①上游=各传感器滚动 IC/判准率 ②下游=E-L1-AGG 降权反馈 ③算法=可靠度三档(等权→判准率加权下限10%→粒子滤波)+hyperbolic 半衰期衰减>50% 报警 ④后端=MOD-SIGQC-004 signal_degradation_monitor 存在,判准率加权器 src 零实现(红节点) ⑤呈现=可靠度表(登记) ⑥数据=index+kline 齐 | 1 | shadow1 | 否(加权聚合器零实现,长尾) | blocked_on_impl(D7-D13 加权 src 零实现) |
| TDM-F-FLOW | ①上游=C1+C2+C3 全流产物 ②下游=无(终点) ③算法=全链目标权重合成 vs 静态基准 v0 ④后端=module_ref 空 red_reason=terminal,全链编排待装配,分配器段 allocator_shadow 真实 ⑤呈现=组合信号(登记) ⑥数据=kline_daily_hfq 全覆盖 | 1 | comparison1 | 否(全链端到端待装配,长尾) | blocked_on_impl(terminal 聚合器为结构指向件);挂载 STR-098/099 BH-FDR 未过 candidate 留观,本卡不判上线 |

## 新卡清单（C3+CFLOW，绝对路径）

11. `.../portfolio_flow/C3/TDM-F-C3__comparison__02_归因反馈闭环开vs关.yaml`
12. `.../portfolio_flow/C3/TDM-F-C3-01__comparison__02_隔夜漂移切账失真.yaml`
13. `.../portfolio_flow/C3/TDM-F-C3-02__shadow__02_减半冻结线有效性.yaml`
14. `.../portfolio_flow/C3/TDM-F-C3-03__comparison__02_月度调权vs静态基准.yaml`
15. `.../portfolio_flow/C3/TDM-F-C3-04__shadow__02_四道gate过拟合防线.yaml`
16. `.../portfolio_flow/C3/TDM-F-C3-05__shadow__02_判准率加权vs等权.yaml`
17. `.../portfolio_flow/CFLOW/TDM-F-FLOW__comparison__02_终产目标组合vs基准.yaml`

---

## L6 车道收尾（MUST 全项）

**节点总数 / 已挖数**：16 / 16（全 16 节点逐一六向挖矿并出卡；名册 L6 nodes:16 全达）。
**新卡总数**：17（TDM-F-C1 出 2 张，其余 15 节点各 1 张）。
**族分布**：shadow 9 张（C1、C1-01、C1-02、C1-03、C2-02、C2-04、C3-02、C3-04、C3-05）；comparison 8 张（C1-comp、C2、C2-01、C2-03、C3、C3-01、C3-03、FLOW）。
**卡可运行核验**：`yaml.safe_load` 全 17 张通过；必填面（schema_version/card_id/node_id/family/status/signal_kind/pillars_numeric/window/buckets/pillars/target/lineage/data_binding/preregistered_by/at）全在；均无 `generated:true`；status 全 `preregistered`；data_binding.data_window_evidence 全带实测覆盖窗+行数+命令原文。

**mined_out=是（六向齐、无未挖长尾）5 个**：TDM-F-C1-02、C2-01、C2-02、C2-03、C3-01。
（C2-01/02/03 绑真实落码件 MOD-POS-021/012；C3-01 绑 MOD-PF-007 已落码引擎；C1-02 绑 allocator_shadow 五套影子考——均"缺什么"已穷尽。）

**blocked 名单与原因（8 个节点）**：
- blocked_on_impl：
  - TDM-F-C1-01（策略路由查表体 module_ref null / by_ref_design，路由引擎未落码）
  - TDM-F-C1-03（双向 weight_band 爬坡器未落码；且 owner_gate 灰度切换）
  - TDM-F-C2（组合聚合端到端件空 / structural）
  - TDM-F-C2-04（BudgetChanged 事件链未接线，33 号复核在案）
  - TDM-F-C3（归因反馈闭环编排空 / structural）
  - TDM-F-C3-03（MOD-PA-007 纯库无调用方，三缺口 base_weights/调度体/PerfScore 生产者，裁定#257② 在案）
  - TDM-F-C3-04（红节点 G04 校准闭环未转；walk_forward 件存在但端到端未接）
  - TDM-F-C3-05（红节点，D7-D13 判准率加权 src 零实现）
  - TDM-F-FLOW（terminal 聚合器结构指向件，全链待装配；allocator 段真实）
- blocked_on_data：
  - TDM-F-C1__comparison__03_预备金现金贡献（cash_contrib 门柱缺 GC001 逆回购日收益率在册 CH 表；组合 NAV/MaxDD 两臂不受影响可跑）
- CH 数据本身无断供（kline_daily_hfq/kline_index/regime_snapshot 全覆盖至 2026-09/10），除上列 GC001 外无缺基建表。

**未挖长尾清单（明列，供交叉复挖/续挖）**：
1. 预备金存放分层三档利率（当日逆回购 GC001 / T+1 短债）与"14:00 后利率高 38%"日内季节性——需日内级现金收益率数据源（现无）。
2. C1-03 切换事件样本稀少（min_obs=5），A 股实际策略间切换历史事件簿未建，长尾待事件积累。
3. C2-02 六层约束"过哪层裁哪层"逐层贡献分解需 sleeve 级 intent 明细（当前只有净值面板），逐层归因属施工面。
4. C2-03 危机期相关性趋于 1 的压测版需危机日期定义真源（crisis_gate θ），本卡引 config/crisis_gate.yaml 未展开逐日压测。
5. C3-01 逐笔 TCA（decision→fill 滑点归因，A 股隐性成本 5-10× 佣金）与孤儿成交 suspense 桶——需 tick 级成交回报，日频面板不及。
6. C3-02 观察名单"半仓缓刑 3 个月"中间态 + 升档参考输入（paper 样本笔数/时长/回测偏差阈）属编排长尾。
7. C3-04 DSR/PBO 的 CPCV 配置项"待 P1-18 实现"（walk_forward.py 注释），四道 gate 中 CPCV 面尚未落地。
8. C3-05 粒子滤波时变档（三档递进第三档，远期）与币圈 funding/basis schema 预留（A 股恒 0）——终局有位现在挂起。
9. 全链 F 流端到端（FLOW）串接需 C1→C2→C3 全接线，当前仅分配器段可跑。

**交叉复挖建议（约 20% 节点）**：TDM-F-C1-02（五套影子考可直接开 allocator 子命令验，绑最实基建，优先复挖/开考）、TDM-F-C3-01（MOD-PF-007 已落码，切账判据可即时校准）、TDM-F-C1（预算带六档数值全 proposed，待 Owner 校准后复挖）、TDM-F-C3-03（三缺口任一补齐即可解锁调权全链）。

**需 Owner 拍板项（灰度晋升类，单列——本车道禁执行，仅出卡与判据）**：
- **TDM-F-C1-03**（`owner_gate_required: true`）：双向 weight_band 灰度切换 = 策略间 production 流转，触根宪法 §5 Owner 保留面；卡已冻结判据，切换/晋升动作一律待 Owner 签字。
- **TDM-F-C3-02**（`owner_gate_required: true`）：sleeve 清退归零 = 业务资产概念级退役（轨 B）+ production 流转，需 Owner 签字；减半/冻结等可逆减动作 AI 可自主，退役提案交 Owner。
- 附：**TDM-F-FLOW** 挂载 STR-MULTIFACTOR-098/099 双窗及格但 BH-FDR 未过、candidate 留观——晋升上线属 Owner 门（本卡不判上线，仅全链净效果考）。
- 综合：组合层任何"首次转 production / 灰度切换 / 退役"均须走晋升门（宪法 §5 非交易核心域可回退晋升/交易核心域 production 流转 Owner 保留），本车道全程只出卡未执行任何切换或晋升。

**诚实负结果**：allocator_shadow_report_v1.yaml/.md **尚未产出**（影子考未开跑），本车道据 allocator_shadow.py 源码（读全文）如实描述其入口/产出形态，未虚构任何已跑结果；基准 v0 Sharpe 0.963 引自任务令与裁定 D8 版本化，未在本车道独立复算（考试车道开考时校准）。library.lookup state 四词零命中已作负存在断言证据指针登记，降级手工阶梯（读图真源 + 读码）佐证。
