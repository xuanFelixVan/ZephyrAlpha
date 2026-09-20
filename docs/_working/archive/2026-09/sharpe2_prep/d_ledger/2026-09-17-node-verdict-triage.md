---
ttl: task_bound
---

# TDM 节点回测台账 pending 行三态分诊报告（Sharpe2 决赛准备·分包D）

> 日期：2026-09-17 ｜ 分包：st-sharpe2d-20260917 ｜ 性质：100% 只读分析，未写任何表/注册表/配置
> 台账真源：ClickHouse `c1_backtest.node_verdict`（append-only，禁删改）
> 设计真源：docs/_working/2026-09-09-node-backtest-governance.md（§七裁定+§八施工）+ docs/_working/2026-09-10-nodebt-night-report.md
> 机读版：同目录 node_triage.csv

---

## 一、口径核实：41 pending vs Owner 任务书"42"

### 1.1 实测数（2026-09-17 查询）

| 指标 | 实测值 |
|---|---|
| 总行数 | **43** |
| verdict=pending 行 | **41** |
| verdict=valid 行 | **2**（TDM-E-L1、TDM-E-L1-AGG 各 1 行） |
| distinct node_id | 38 个（36 个节点最新态仍 pending，2 个已 valid） |

### 1.2 与"42"的差异解释（已核实，含台账移送证据）

台账为 **append-only**（runner 铁律：不改写不删除，每次验证追加新 run 行）。按 run_id 重建时间线：

| 时点（ingest_ts 序） | run | 动作 | 表内累计 pending / valid |
|---|---|---|---|
| 09-12 07:06 | VAL-20260912-070605 | L4 首批 15 行（E-L4+01..14）全 pending | 15 / 0 |
| 09-12 07:06 | VAL-20260912-070622 | X 流 19 行（X-FLOW/R1/S1/S2 族）全 pending | 34 / 0 |
| 09-12 16:37~16:41 | VAL-P0-20260912-163755/163855/164116 | L1 总闸与 L1-AGG 三连跑，L1 出**首个 valid**，L1-AGG 两行 pending | 36 / 1 |
| 09-12 17:08 | VAL-P0-20260912-170843-003 | 成本模型三件套 4 行 pending（E-L4-09/P-P2-01/P-P2-03/X-S2-01） | 40 / 1 |
| 09-14 00:18 | VAL-P0-20260914-001859-002 | L1-AGG 收益口径复跑 1 行 pending | **41 / 1（总 42）** |
| 09-14 00:40 | VAL-P0-20260914-004029-002 | **TDM-E-L1-AGG 按裁定#230（判据改 fwd20 maxdd 风险判别）移送 valid** | **41 / 2（总 43）** |

**结论**：Owner 任务书"42 行 pending"写于 09-14 00:18 与 00:40 之间（或按当时口径盘点）——当时总行数恰为 42（41 pending + 1 valid）。此后 **TDM-E-L1-AGG 经裁定#230 移送 valid**（run VAL-P0-20260914-004029-002，主判据 risk_discrimination，p=1.76e-28），即任务书猜测的"台账移送过 1 行到 valid"**成立**。当前真实 pending=41 行。

⚠️ 附带口径披露（row vs node）：因 append-only，TDM-E-L1-AGG 的 3 条历史 pending 行仍留在表内（未删）。故：
- **行级 pending = 41**（含 3 条已被 valid 覆盖的历史行）
- **节点级 pending = 36**（36 个节点最新 verdict 仍 pending；本报告分诊以此为行动对象，行级状态同步给出）

---

## 二、分诊规则（判定标准，先于结论写死）

| 态 | 定义（本报告操作化） | 判据 |
|---|---|---|
| **可考** | 依赖数据已就绪且回测管线可表达，跑批即出结论 | ①数据源存在且样本量≥土规 30 触发；②时间覆盖满足 holdout 纪律（定稿锚点 D=2026-09-09 之后可考，D 前全锁）；③runner/专项脚本已存在 |
| **缺数据** | 依赖数据表/产物缺失或覆盖不足 | 写明缺哪张表/哪段时间 |
| **需裁定** | 图状/关系型/无历史数据/口径争议等工程无法自决 | 写明裁定问题本身与前置 |
| 已闭合 | 历史 pending 行已被该节点更新的 valid 覆盖（append-only 残留） | 不再行动，仅登记 |

关键事实基础（全部实测，详见附录 A）：
1. **成交流水真源是文件产物** `data/backtest_artifacts/bt-*.json` 的 trade_log（runner.load_fills），**不是 CH 表**——CH 侧 sim_trade_log 仅 9 行（sim 平台）、execution_report 0 行、account_nav_daily 0 行，均非台账数据源。
2. 产物共 52 个、128,341 笔 fill，时间覆盖 2025-04-03 → 2026-09-15；**D 锚点（2026-09-09）后可考 fill=1,467 笔**（4 个交易日：09-10/11/14/15，来自 11 个 bt-fw-* walk-forward 产物，OOS 折），其中卖出 858 笔；**1,467 笔全部携带 decision_price+commission**（T1 字段已落地），order_type 全部='market'。
3. holdout 纪律 runner 默认**定稿锚点模式**（finalized_at=2026-09-09：D 前全锁/D 后可考），非滚动 12 月锁——D 后 fill 天然可考。
4. 土规：触发<30 → pending(insufficient_samples)；滑点≤20bp→valid、≤40bp→pending、>40bp→noise。
5. 消融对照器已施工（src/zephyr/trading/validation/ablation.py，MATURITY=testing），但 **上游 sell_decision 信号 provider 零实现**（模块 docstring 自述）且 **消融实弹回放受协议备忘录 §12 约束须 Owner 放行**——runner 对 exit_counterfactual 对照缺失硬编码 pending（counterfactual_missing）。
6. 行情侧底座齐：kline_daily 1000 万行（1990→2026-09-15）、stk_limit(DS-082) 917 万行（2015→2026-09-15）、kline_1min 14.7 亿行（2021-09→2026-09-16）。

---

## 三、41 行逐行分诊表

> triage 列=本报告三态；节点最新态=该 node_id 在台账的最新行 verdict。行序=ingest 顺序。
> "可考(代理口径)"=数据与管线就绪、可出结论，但结论为流水全量代理（无节点归因），已在台账 notes 披露。

### 3.1 L4 首批（run VAL-20260912-070605，15 行）——全部可考

| # | node_id | 节点名 | method | 触发(当期) | 三态 | 节点最新态 | 证据与理由 |
|---|---|---|---|---|---|---|---|
| 1 | TDM-E-L4 | 买卖点与执行(容器) | exec_quality | 4→1467 | **可考(代理口径)** | pending | 容器节点，随子节点同批聚合出数；bt-fw 产物 D 后 1467 fill≥30；runner batch=L4 现成 |
| 2 | TDM-E-L4-01 | 分批建仓 | exec_quality | 4→1467 | **可考(代理口径)** | pending | 同上；module order_splitter.py，滑点按 decision_price 实价可算 |
| 3 | TDM-E-L4-02 | 买入时序 | exec_quality | 4→1467 | **可考(代理口径)** | pending | 同上 |
| 4 | TDM-E-L4-03 | 价格锚定 | exec_quality | 4→1467 | **可考** | pending | 语义=限价/市价选择直接决定滑点；decision_price 基准已就绪，本批最有信息量 |
| 5 | TDM-E-L4-04 | 资金分配多标的 | exec_quality | 4→1467 | **可考(代理口径)** | pending | 同批可出数 |
| 6 | TDM-E-L4-05 | 打板执行专项 | exec_quality | 4→1467 | **可考(代理口径，受限)** | pending | D 后 fill order_type 全='market'，排板单不可分桶——专项判据降级为全量代理；真分桶需排板归因（缺数据项见 §五） |
| 7 | TDM-E-L4-06 | 执行算法(TWAP/VWAP等) | exec_quality | 4→1467 | **可考(代理口径，受限)** | pending | fill 无 algo 归因字段，6 个 EXA 算法不可逐算法判——同降级代理；algo_id 字段缺失登记 §五 |
| 8 | TDM-E-L4-07 | 条件触发队列 | exec_quality | 4→1467 | **可考(代理口径)** | pending | 可出数 |
| 9 | TDM-E-L4-08 | 突破失败降级 | exec_quality | 4→1467 | **可考(代理口径)** | pending | 可出数 |
| 10 | TDM-E-L4-09 | 执行硬约束 | exec_quality | 4→1467 | **可考** | pending | 成本模型三件套成员，阈值已冻结（20/40bp 土规线），BT-P0-003 交叉引用 |
| 11 | TDM-E-L4-10 | 订单生命周期状态机 | exec_quality | 4→1467 | **可考(代理口径)** | pending | 可出数；未成交/撤改环节 fill 不可见（流水只含成交），成交率单轴判 |
| 12 | TDM-E-L4-11 | 部分成交与撤改处理 | exec_quality | 4→1467 | **可考(代理口径)** | pending | 同上限制 |
| 13 | TDM-E-L4-12 | 订单级预检 | exec_quality | 4→1467 | **可考(代理口径)** | pending | 可出数 |
| 14 | TDM-E-L4-13 | 执行容灾对账 | exec_quality | 4→1467 | **可考(代理口径)** | pending | 可出数；可增强判据=c1_market.reconciliation_differences（实测 0 行，空表不阻断） |
| 15 | TDM-E-L4-14 | 执行成本反馈与选型回写 | exec_quality | 4→1467 | **可考** | pending | fill 已带 commission（1467/1467），成本反馈闭环可实算；DS-008 成交回报挂点 |

### 3.2 X 流批（run VAL-20260912-070622，19 行）——18 行需裁定，1 行被后续覆盖

| # | node_id | 节点名 | method | 触发(当期2/D后858) | 三态 | 节点最新态 | 证据与理由 |
|---|---|---|---|---|---|---|---|
| 16 | TDM-X-FLOW | 输出离场信号(容器) | exit_counterfactual | 2→858 | **需裁定** | pending | 对照数据（双净值差额序列）不存在：sell provider 零实现+消融回放须 §12 Owner 放行。裁定问题=**是否放行消融回放实弹运行** |
| 17 | TDM-X-R1 | 应急保命(容器) | exit_counterfactual | 2→858 | **需裁定** | pending | 同上 |
| 18 | TDM-X-R1-01 | 熔断分级判定 | exit_counterfactual | 2→858 | **需裁定** | pending | 同上；另熔断五级状态机在回测窗口内是否触发过=无历史触发记录（D 后卖出含风控归因不可分），裁定需连带确认回放窗口覆盖 L2+ 熔断日 |
| 19 | TDM-X-R1-02 | 熔断期减仓与持仓处置 | exit_counterfactual | 2→858 | **需裁定** | pending | 同上 |
| 20 | TDM-X-R1-03 | 护盘资产定向加仓白名单 | exit_counterfactual | 2→858 | **需裁定** | pending | 加仓动作的消融语义（剥离=不加仓）与回滚式剥离算子语义需先对齐——口径裁定 |
| 21 | TDM-X-S1 | 卖出信号收集评分(容器) | exit_counterfactual | 2→858 | **需裁定** | pending | 同 16 |
| 22 | TDM-X-S1-01 | 信号收集与六桶分类 | exit_counterfactual | 2→858 | **需裁定** | pending | 同 16；六桶归因无流水字段 |
| 23 | TDM-X-S1-02 | 止损族判定 | exit_counterfactual | 2→858 | **需裁定** | pending | 同 16（止损"救了多少"是反事实经典对象） |
| 24 | TDM-X-S1-03 | 止盈族判定 | exit_counterfactual | 2→858 | **需裁定** | pending | 同 16 |
| 25 | TDM-X-S1-04 | 破位与情绪退潮信号 | exit_counterfactual | 2→858 | **需裁定** | pending | 同 16 |
| 26 | TDM-X-S1-05 | 信号融合与紧迫度评分 | exit_counterfactual | 2→858 | **需裁定** | pending | 同 16；紧迫度三档分桶需信号级日志（无） |
| 27 | TDM-X-S1-06 | 强制清仓绕过通道 | exit_counterfactual | 2→858 | **需裁定** | pending | 同 16；触发极稀疏，即使放行也大概率 insufficient_samples |
| 28 | TDM-X-S2 | 离场执行(容器) | exit_counterfactual | 2→858 | **需裁定** | pending | 同 16 |
| 29 | TDM-X-S2-01 | 执行方式路由 | exit_counterfactual | 2→858 | **需裁定（本行）/可考（节点）** | pending(最新行=成本批) | 本行(070622)为 X 批口径；同日 17:08 成本批已按 exec_quality 重写（BT-P0-003），节点以成本批为准=可考 |
| 30 | TDM-X-S2-02 | T+1与涨跌停约束 | exit_counterfactual | 2→858 | **需裁定（口径可解）** | pending | 本节点语义=约束正确性（可执行性），非反事实；exec_quality 口径（卖出滑点/拒单率）即可考——**裁定问题=方法分配是否从 exit_counterfactual 改 exec_quality**（registry exec_quality applies_to 本就含 X 流执行节点，derive_method 代码现把全部 exit_flow 归反事实） |
| 31 | TDM-X-S2-03 | 执行时段路由 | exit_counterfactual | 2→858 | **需裁定（口径可解）** | pending | 同 30——卖出滑点按时段分桶即数据可考 |
| 32 | TDM-X-S2-04 | 本地条件单管理 | exit_counterfactual | 2→858 | **需裁定（口径可解）** | pending | 同 30（触发价 vs 成交价可算）；条件单未成交数流水不可见 |
| 33 | TDM-X-S2-05 | 分批止盈执行 | exit_counterfactual | 2→858 | **需裁定（口径可解）** | pending | 同 30 |
| 34 | TDM-X-S2-06 | 卖出闭环与退出效率 | exit_counterfactual | 2→858 | **需裁定（口径可解）** | pending | 同 30；退出效率=信号→成交时延需信号时间戳字段（缺，登记 §五） |

### 3.3 成本模型三件套补录（run VAL-P0-20260912-170843-003，4 行）——全部可考

| # | node_id | 节点名 | method | 触发(当期4/D后1467) | 三态 | 节点最新态 | 证据与理由 |
|---|---|---|---|---|---|---|---|
| 35 | TDM-E-L4-09 | 执行硬约束(成本批行) | exec_quality | 4→1467 | **可考** | pending | 阈值冻结（BT-P0-003）：佣金+印花税+滑点+市场冲击+做T成本，费率真源 CST-ASTOCK-001(active)/CST-T0-001(candidate)；fill 全带 commission 可实算 |
| 36 | TDM-P-P2-01 | 做T资格与成本前置 | exec_quality | 4→1467 | **可考** | pending | 做T往返成本判据 CST-T0-001 已量化（含最低佣金 5 元实证）；D 后 fill 可按 symbol/day 配对估做T成本 |
| 37 | TDM-P-P2-03 | 做T闭环与成功判定 | exec_quality | 4→1467 | **可考** | pending | "股数不变+总成本降"判据可由流水 symbol+side+date 聚合表达；DAL-T0-CLOSE 已登记 |
| 38 | TDM-X-S2-01 | 执行方式路由(成本批行) | exec_quality | 4→1467 | **可考** | pending | 节点最新行；重跑即与 L4 批同步出结论 |

### 3.4 L1-AGG 历史 pending 行（3 行）——已闭合

| # | run | node_id | 三态 | 说明 |
|---|---|---|---|---|
| 39 | VAL-P0-20260912-163755-002 | TDM-E-L1-AGG | **已闭合** | 收益口径首跑判据不足；同节点已被 09-14 风险口径行覆盖 |
| 40 | VAL-P0-20260912-164116-002 | TDM-E-L1-AGG | **已闭合** | discrimination_below_threshold（收益口径 p=0.0017 但档差 0.46%<1.0%）；裁定#230 改风险判据后出 valid |
| 41 | VAL-P0-20260914-001859-002 | TDM-E-L1-AGG | **已闭合** | 收益口径复跑行；同 run 序列 00:40 的 risk_discrimination 行（valid）已覆盖节点最新态 |

---

## 四、统计与批次排期

### 4.1 三态分布

| 口径 | 可考 | 缺数据 | 需裁定 | 已闭合 |
|---|---|---|---|---|
| **行级（41 pending 行）** | **19**（L4 批 15+成本批 4） | 0 | 19（X 批） | 3（L1-AGG 历史） |
| **节点级（36 个 pending 节点）** | **18** | 0 | 18 | —（2 个节点已 valid） |

说明：本批 pending 无纯"缺数据"行——执行类数据（fill）已就绪，离场类卡在"对照数据需放行才能生产"（归入需裁定）；fill 的字段级缺口（algo 归因/未成交记录/信号时间戳）作为**可考批的质量限制**登记在 §五，不改变三态。

### 4.2 可考节点建议考试批次（按依赖就绪度排序）

| 批次 | 内容 | 前置 | 工程量 | 说明 |
|---|---|---|---|---|
| **D1（决赛前，立即可跑）** | L4 批 15 节点重跑：`run_validation(batch='L4')`——D 后 1467 fill（带 decision_price+commission）按冻结土规线出 verdict | 无（runner v2 现成，finalized_at 锚点默认启用） | S（0.5 人日：跑批+复核台账） | 滑点口径=真决策价，非 VWAP 代理；结论窗口仅 4 个交易日，notes 须如实披露窗口敏感性 |
| **D2（决赛前，+1 人日）** | 成本三件套复跑（E-L4-09/P-P2-01/P-P2-03/X-S2-01）：按 CST-ASTOCK-001/CST-T0-001 费率实算成本项 | D1 同源数据；做T配对统计约 0.5 人日脚本 | S-M（1 人日） | BT-P0-003 阈值已冻结，禁跳过 SOP-B 护栏③（决策点确认冻结清单后跑） |
| **D3（决赛前可选/决赛后第一批）** | X-S2 执行族 5 节点（S2-02/03/04/05/06）改 exec_quality 口径考试 | **Owner 裁定**：方法分配从 exit_counterfactual 改挂 exec_quality（registry applies_to 已支持，derive_method 需 1 行改动+回归） | S（0.5 人日）+1 项裁定 | 卖出 fill 858 笔≥30 土规可考；不改口径则维持 pending |
| **D4（决赛后第一批）** | X-S1/X-R1 反事实 13 节点 | ①sell_decision 信号 provider 施工（M，2-3 人日）；②消融回放 §12 Owner 放行；③R1-03 加仓剥离口径对齐 | M-L（3-5 人日） | ablation.py 机制已就绪，缺上游与放行 |

### 4.3 可考节点里最值得先考的前 5（一句话理由）

1. **TDM-E-L4-03 价格锚定**——限价/市价选择直接写进滑点，decision_price 真基准首次可算，离钱最近且信息量最大。
2. **TDM-E-L4-09 执行硬约束**——成本三件套核心，阈值已冻结（20/40bp），跑批即出首个有冻结判据的执行类 verdict。
3. **TDM-E-L4-01 分批建仓**——order_splitter 决定 fill 笔数与滑点分布形态，是 D1 批结论的代表节点。
4. **TDM-P-P2-03 做T闭环与成功判定**——materiality=critical，CST-T0-001 费率已实证，"总成本降没降"直接回答 Owner 做T是否有正贡献。
5. **TDM-E-L4-14 执行成本反馈与选型回写**——fill 已全带 commission，成本反馈闭环可实算，结论直接喂 L4-06 算法选型改进。

### 4.4 需裁定清单（给 Owner 的裁定问题，逐条）

| # | 裁定问题 | 涉及节点 | 建议 |
|---|---|---|---|
| R-A | X-S2 执行族 5 节点方法分配：exit_counterfactual（现状，阻塞）还是 exec_quality（数据可考）？ | X-S2-02/03/04/05/06 | 改 exec_quality——registry applies_to 本就含 X 流执行节点 |
| R-B | 消融回放实弹运行 §12 放行：sell provider 施工完成后是否放行对在验窗口跑对照回放？ | X-S1/X-R1 13 节点 | 按 PB-12 排序（风控第二顺位），provider 建成后放行 |
| R-C | R1-03 加仓动作的消融剥离语义（回滚式算子只支持 clear/reduce） | TDM-X-R1-03 | 加仓剥离=权重不回补，需 ablate_weight_panel 扩一个算子（工程 S）+口径确认 |
| R-D | 3 条 L1-AGG 历史 pending 行处置：append-only 原则下保留至自然滚动（现状），还是加"superseded"标记机制？ | 台账治理 | 保留不删（破坏性纪律），可由前端只按"节点最新行"渲染规避误导（工程 S） |

---

## 五、他会在途缺陷/缺口登记（只登记不修）

1. **fill 无 algo 归因字段**（影响 E-L4-06 执行算法真验证）——order_type 已落地但 algo_id 未落地；归属=X 流验证批 TradeRecord 扩展的后续项（晨报裁定③只加了 decision_price+order_type）。
2. **流水只含成交记录**——未成交/撤单数不可得，成交率判据（registry exec_quality 的 95% 线）全批不可评，hit_ratio 列空置；与晨报裁定 4 披露一致，非新缺陷。
3. **信号→成交时延无时间戳**（影响 X-S2-06 退出效率真判据）——信号侧时间戳未入流水。
4. **c1_market.reconciliation_differences 空表**（0 行，min/max=1970）——E-L4-13 容灾对账的增强判据暂无数据。
5. **面板 API 8890 旧实例 wedge**（09-01 实例半开连接，晨报已报）——未复查，Owner 窗口事项。
6. 老产物（D 前 bt-*.json）无 decision_price/order_type 字段——按设计（T1 起携带），非缺陷，但意味着 locked 段永远无法补算真滑点（符合 holdout 纪律，无须修）。

---

## 附录 A：可复现命令与判定规则

### A.1 台账状态核实

```bash
export PATH="/c/Users/fanzi/AppData/Local/Programs/Python/Python312:...:$PATH"
python -c "
from zephyr.infrastructure.database_service import DatabaseService
conn = DatabaseService().get_clickhouse_conn()
print(conn.execute('SELECT verdict, count() FROM c1_backtest.node_verdict GROUP BY verdict'))
print(conn.execute('SELECT run_id, verdict, count() FROM c1_backtest.node_verdict GROUP BY run_id, verdict ORDER BY run_id'))
print(conn.execute('''SELECT node_id, argMax(verdict, ingest_ts) FROM c1_backtest.node_verdict GROUP BY node_id'''))
"
```
实测（2026-09-17）：total=43；pending=41、valid=2；valid 节点=TDM-E-L1、TDM-E-L1-AGG。

### A.2 fill 数据盘点（成交流水真源=文件产物）

```python
# data/backtest_artifacts/bt-*.json 的 trade_log；D=2026-09-09
# 实测：52 文件 / 128,341 fill / 2025-04-03→2026-09-15
# D 后可考 1,467（buy 609 / sell 858），4 个交易日（09-10/11/14/15），11 个 bt-fw-* 产物
# D 后 fill 字段：decision_price 1467/1467 非空，commission 1467/1467 非空，order_type 全部 'market'
```

### A.3 holdout 判定规则

- runner 默认 `finalized_at=2026-09-09`（定稿锚点模式）：fill timestamp ≤ D → locked（不可考），> D → inside（可考）；脏时间戳从严入 locked。
- 土规：`triggers < 30` → verdict=pending / significance=insufficient_samples。
- exec_quality：slip_mean ≤20bp → valid；≤40bp → pending；>40bp → noise。slip=方向×(成交价−decision_price)/decision_price×10⁴ bp。

### A.4 三态判定规则（本报告）

```
可考   = D 后 fill 触发数 ≥30 且 runner/专项脚本存在且判据可由现有字段表达
缺数据 = 依赖表/产物不存在或时间覆盖不足（需写明缺哪张表/哪段）
需裁定 = 出结论前存在 Owner 门位（§12 放行/方法分配/口径语义）或工程无法自决项
已闭合 = 该行 verdict=pending 但同节点存在更晚 valid 行（append-only 残留）
```

### A.5 关键依赖表覆盖实测（2026-09-17）

| 表 | 行数 | 时间覆盖 | 用途 |
|---|---|---|---|
| c1_backtest.node_verdict | 43 | 2026-09-12 起 | 台账本体 |
| c1_backtest.sim_trade_log | 9 | 2026-07-17→09-17 | sim 平台（非台账数据源） |
| c1_market.execution_report | 0 | — | 空 |
| c1_market.kline_daily | 10,074,722 | 1990-12-19→2026-09-15 | 行情底座 |
| c1_market.stk_limit (DS-082) | 9,177,311 | 2015-01-05→2026-09-15 | 涨跌停 |
| c1_market.kline_1min | 1,477,410,355 | 2021-09-01→2026-09-16 | 分钟线 |
| c1_market.reconciliation_differences | 0 | — | 空（E-L4-13 增强判据缺） |

---

*报告完。本分包全程只读：未写 CH 任何表、未改任何注册表/配置/文档，产物仅本目录三件。*
