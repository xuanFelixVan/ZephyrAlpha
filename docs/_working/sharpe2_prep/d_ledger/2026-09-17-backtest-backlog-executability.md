---
ttl: task_bound
---

# backtest_backlog 全量条目可执行化报告（Sharpe2 决赛准备·分包D②）

> 日期：2026-09-17 ｜ 分包：st-sharpe2d-20260917 ｜ 性质：只读分析，backlog 真源未动
> 真源：docs/01_policies_and_standards/_registry/catalogs/backtest_backlog.yaml（REG-BTB-001，generated_at=2026-09-12，140 objects）
> 姊妹篇：同目录 2026-09-17-node-verdict-triage.md（台账 41 行分诊）+ node_triage.csv

---

## 〇、总口径

- backlog 实测 **140 条**（118 testable + 22 容器/结构点 testable=false；3 条已有冻结 plan：BT-P0-001/002/003；4 条 crypto 另册）。
- 每条给四件事：**做什么（含验收判据）/ 依赖 / 工程量（S≤0.5 人日，M=0.5~3 人日，L>3 人日）/ 批次**。
- 验收判据一律引用 validation_method_registry.yaml（REG-VALM-001）五类方法既定线，不另造门柱：
  - **sensor_monotonicity**：分档 vs 后续 N 日收益/波动 Spearman≥0.8 且方向对→valid；|rho|<0.5 或反向→noise；总触发<30→pending。
  - **agg_discrimination**：相邻档后续 N 日收益 Welch t 检验 p<0.05 且高低档差>冻结阈值→valid；p<0.10→pending。
  - **exec_quality**：滑点（decision_price 基准）≤20bp→valid、≤40bp→pending、>40bp→noise；触发≥30。
  - **exit_counterfactual**：触发组后续 N 日损失显著小于无风控对照→valid；对照样本≥30；对照未建保持 pending。
  - **portfolio_attribution**：归因分解残差<1bp 且符号全一致→valid；对账≥30 交易日。
- 全部批次默认受 SOP-B 护栏③约束：验收阈值在批次决策点填写并冻结前**禁跑**；holdout 纪律（定稿锚点 D=2026-09-09，D 前全锁）全局生效。

## 一、批次定义与分布

| 批次 | 定义 | 条数 | 说明 |
|---|---|---|---|
| **DONE** | 已考完，台账 verdict=valid | 2 | BT-P0-001、BT-P0-002 |
| **B0 决赛前可做** | 数据已就绪+管线现成+阈值已冻结，无需新裁定 | 15 | 全部是 L4 执行族+成本三件套，与台账分诊 D1/D2 批同源同批 |
| **B1 决赛后第一批** | 依赖一次轻裁定或一个 S-M 施工件，无数据缺口 | 11 | X-S2 口径改挂（裁定 R-A）、L1 三传感器（数据齐，缺 sensor 计算脚本）、两个晋升批次登记 |
| **B2 排期** | 存在数据缺口/覆盖不足/方法学施工/需裁定 | 109 | 主体：L2 板块族、L3 选股族、P 流、X-S1/R1 反事实族、F 流归因、L0 计划族、crypto、薄数据传感器 |
| **B3 愿景模板件** | 对象本身尚不存在（策略包/编排器/执行模板未建） | 3 | BT-P1-030、BT-P1-031、BT-P2-055 |

---

## 二、逐条四件事

### 2.1 DONE（2 条）

| object_id | 节点 | 做什么/验收 | 依赖 | 量 | 批次 |
|---|---|---|---|---|---|
| BT-P0-001 | TDM-E-L1 谨慎度总闸 | agg_discrimination：高谨慎档后续 20 日 maxdd 显著更深（p<0.05 且档差≥2.0%）→valid | regime_snapshot_history（3621 行，2019-04→2026-09） | — | **DONE**（valid@2026-09-12，与分包D①台账一致） |
| BT-P0-002 | TDM-E-L1-AGG 状态聚合 | 同族判据；裁定#230 改 fwd20 maxdd 风险判别后 valid | 同上 | — | **DONE**（valid@2026-09-14，VAL-P0-20260914-004029-002） |

### 2.2 B0 决赛前可做（15 条）——与台账 D1/D2 批同源，零新裁定

通用依赖：`data/backtest_artifacts/bt-*.json` D 后 fill=1467 笔（4 个交易日，全带 decision_price+commission，order_type 全 market）；runner v2（batch=L4）现成。通用限制（如实披露进 notes）：结论窗口仅 4 个交易日；fill 混含 11 个 walk-forward run；无节点归因=全量代理口径；成交率判据不可评（流水只含成交）。

| object_id | 节点 | 做什么/验收 | 依赖 | 量 | 批次 |
|---|---|---|---|---|---|
| BT-P1-027 | E-L4-01 分批建仓 | exec_quality：D 后 fill 滑点均值≤20bp→valid | runner batch=L4 | S | **B0**（台账 D1） |
| BT-P1-028 | E-L4-02 买入时序 | exec_quality 同上 | 同上 | S | **B0** |
| BT-P2-043 | E-L4-03 价格锚定 | exec_quality 同上；信息量最大（限价/市价选择直接写进滑点） | 同上 | S | **B0** |
| BT-P2-044 | E-L4-04 资金分配 | exec_quality 同上 | 同上 | S | **B0** |
| BT-P2-045 | E-L4-05 打板执行专项 | exec_quality 全量代理（排板单不可分桶，order_type 全 market） | 同上+algo 归因字段（缺，见§三） | S | **B0**（代理口径） |
| BT-P2-046 | E-L4-06 执行算法 | exec_quality 全量代理（6 个 EXA 无 algo 归因不可逐算法判） | 同上+algo_id 字段（缺） | S | **B0**（代理口径） |
| BT-P2-047 | E-L4-07 条件触发队列 | exec_quality 同上 | 同上 | S | **B0** |
| BT-P2-048 | E-L4-08 突破失败降级 | exec_quality 同上 | 同上 | S | **B0** |
| BT-P2-049 | E-L4-10 订单生命周期 | exec_quality 同上（未成交/撤改不可见） | 同上 | S | **B0** |
| BT-P2-050 | E-L4-11 部分成交处理 | exec_quality 同上 | 同上 | S | **B0** |
| BT-P2-051 | E-L4-12 订单预检 | exec_quality 同上 | 同上 | S | **B0** |
| BT-P2-052 | E-L4-13 执行容灾对账 | exec_quality 同上；可增强=c1_market.reconciliation_differences（现 0 行，不阻断） | 同上 | S | **B0** |
| BT-P2-053 | E-L4-14 成本反馈回写 | exec_quality：commission 1467/1467 在，成本反馈可实算 | 同上 | S | **B0** |
| BT-P2-042 | E-L4 容器 | 不独立开考（D108）；随子节点批聚合出数 | 子节点 B0 | S | **B0**（随批） |
| BT-P0-003 | 成本三件套（E-L4-09/P-P2-01/P-P2-03/X-S2-01） | exec_quality+成本项实算（CST-ASTOCK-001 active/CST-T0-001 candidate 费率）；阈值已冻结 20/40bp | 同上 fill 源+费率表 | S-M（做T配对 0.5 人日） | **B0**（台账 D2；跨引分包D①可考#35-38） |

### 2.3 B1 决赛后第一批（11 条）——每次一个轻前置

| object_id | 节点 | 做什么/验收 | 依赖 | 量 | 批次与理由 |
|---|---|---|---|---|---|
| BT-P3-031 | X-S2-02 T+1与涨跌停约束 | **改挂 exec_quality**（裁定 R-A）：卖出滑点+约束违规率≤阈值→valid | 卖出 fill 858 笔≥30；derive_method 1 行改动+回归 | S+裁定 | **B1**：数据已在，只欠方法分配裁定 |
| BT-P3-032 | X-S2-03 执行时段路由 | 改挂 exec_quality：卖出滑点按时段分桶达标 | 同上 | S | **B1** |
| BT-P3-033 | X-S2-04 本地条件单 | 改挂 exec_quality：触发价 vs 成交价滑点（未成交数不可见） | 同上 | S | **B1** |
| BT-P3-034 | X-S2-05 分批止盈执行 | 改挂 exec_quality：分批卖滑点达标 | 同上 | S | **B1** |
| BT-P3-035 | X-S2-06 卖出闭环退出效率 | 改挂 exec_quality（真判据=信号→成交时延，缺信号时间戳，先滑点代理） | 同上 | S | **B1**（代理） |
| BT-P3-020 | X-S2 容器 | 随子节点聚合 | 上 5 条 | S | **B1**（随批） |
| BT-P1-001 | L1-S1 大盘指数传感器 | sensor_monotonicity：分档 vs 后续 N 日收益 Spearman≥0.8 | kline_index 310 万行（1990→2026-09）数据齐；**缺 sensor 批计算脚本**（runner 现只支持 L4/XFLOW 两批） | M（1-2 人日：sensor_monotonicity 计算实现+批入口） | **B1** |
| BT-P1-005 | L1-S0 宏观环境传感器 | sensor_monotonicity 同上 | news_data 820 万行（2010→2026-09）数据齐；同上脚本 | M | **B1** |
| BT-P1-006 | L1-S0-1 新闻情绪语义 | sensor_monotonicity 同上 | news_data+news_sentiment_window 在库；同上脚本 | M | **B1** |
| BT-P1-029 | E-FLOW 执行链晋升批次登记 | 21 个 depgraph planned 节点批量 planned→production 的回测前置登记；验收=逐节点验收阈值冻结+禁跳 SOP-B 护栏③ | depgraph planned 集合实查；exec 土规线 20/40bp 起议 | S（登记）+决策点 | **B1**：晋升动作本身是决赛后事项，登记先行 |
| BT-P2-054 | model_registry 8 candidate 晋升批次 | 8 模型批量 candidate→serving 前置登记；验收=逐模型 OOS 判据（对比基线/最小样本按 validation_method_registry 推导）冻结 | model_registry candidate 实查 | S（登记）+决策点 | **B1** |

### 2.4 B2 排期（109 条）——按缺口类型分四组

#### B2-a 数据覆盖不足/缺表（先回补数据再考）

| object_id | 节点 | 做什么/验收 | 缺口（缺哪张表/哪段） | 量 | 批次 |
|---|---|---|---|---|---|
| BT-P1-002 | L1-S2 市场内部结构传感器 | sensor_monotonicity | limit_up_pool **0 行**；limit_up_down 仅 2026-07-20 起（2 个月）——缺历史涨停池/涨跌停全景 ≥2 年 | M+数据回补 | B2 |
| BT-P1-003 | L1-S3 赚钱效应传感器 | sensor_monotonicity | dragon_tiger 仅 2026-08-07 起（1.4 个月）——缺龙虎榜历史 | M+数据回补 | B2 |
| BT-P1-004 | L1-S4 波动率传感器 | sensor_monotonicity | option_iv_surface 仅 2026-01-29 起（7.5 月）、convertible_bond_iv 仅 1.4 个月——合成 VIX 历史段不足 | M+数据回补 | B2 |
| BT-P1-007 | L1-S5 日级市场条件传感器 | sensor_monotonicity（复合源） | 依赖 S1-S4 各源，margin_trading 2 个月/hk_connect_flow 止于 2024-08/stock_hot_rank 1 个月——多源历史不齐 | M+数据回补 | B2 |
| BT-P2-035 | L3-11-1 竞价选股 | sensor_monotonicity/自定判据 | auction_snapshot 仅 2026-08-12 起、auction_book 需核——竞价历史段缺 | M+数据回补 | B2 |
| BT-P2-038 | L3-12-1 个股资金面 | agg_discrimination | money_flow 仅 2026-06-01 起（3.5 月）、sector_fund_flow 仅 2 天——资金流历史缺 | M+数据回补 | B2 |
| BT-P2-039 | L3-12-2 龙虎榜席位 | agg_discrimination | dragon_tiger+dragon_tiger_seat 仅 1.4 个月 | M+数据回补 | B2 |
| BT-P3-040 | F-C2-02 组合约束栈 | 自定判据（约束违反率） | 需组合日度快照历史（account_nav_daily 0 行/sim_pocket_daily 60 行） | M | B2 |

#### B2-b 反事实/风控族（与台账 D4 同源：sell provider + §12 放行）

通用依赖：sell_decision 信号 provider 施工（M，2-3 人日）+ 消融回放 §12 Owner 放行（裁定 R-B）+ ablation.py（机制已在）。验收一律 exit_counterfactual：触发组后续 N 日损失显著小于无风控对照→valid，对照样本≥30。

| object_id | 节点 | 做什么 | 特别依赖 | 量 | 批次 |
|---|---|---|---|---|---|
| BT-P3-021 | X-R1 熔断判定(kill_switch) | 反事实：熔断救了多少 | 同通用+回放窗口须覆盖 L2+ 熔断日 | M | B2 |
| BT-P3-022 | X-R1-01 熔断分级 | 反事实（五级状态机逐级） | 同上 | M | B2 |
| BT-P3-023 | X-R1-02 熔断期减仓 | 反事实 | 同上 | M | B2 |
| BT-P3-024 | X-R1-03 护盘白名单 | 反事实（**加仓剥离语义需先对齐**，裁定 R-C） | 同上+ablate 算子扩展 | M | B2 |
| BT-P3-025 | X-S1-01 六桶分类 | 反事实+桶归因（桶字段缺，代理） | 通用 | M | B2 |
| BT-P3-026 | X-S1-02 止损族 | 反事实经典对象 | 通用 | M | B2 |
| BT-P3-027 | X-S1-03 止盈族 | 反事实 | 通用 | M | B2 |
| BT-P3-028 | X-S1-04 破位退潮 | 反事实 | 通用 | M | B2 |
| BT-P3-029 | X-S1-05 融合紧迫度 | 反事实+紧迫度分桶（信号级日志缺） | 通用 | M | B2 |
| BT-P3-030 | X-S1-06 强制清仓 | 反事实（触发稀疏，大概率 insufficient_samples） | 通用 | M | B2 |
| BT-P3-019 | X-S1 容器 | 随子节点聚合 | 上 6 条 | S | B2 |
| BT-P3-008 | P-P1-02 持仓分级 | 反事实（减仓触发救损） | 通用+持仓快照历史 | M | B2 |
| BT-P3-010 | P-P1-04 风险否决体检 | 反事实 | 通用 | M | B2 |

#### B2-c 信号/判定族（数据大体在，缺各层批计算脚本与判据冻结）

通用依赖：按层扩 runner 批入口（L2/L3/P 流批，每层 M）；判据按 agg_discrimination/sensor_monotonicity 冻结后跑。

| object_id | 节点 | 做什么/验收 | 依赖 | 量 | 批次 |
|---|---|---|---|---|---|
| BT-P1-008 | L2-01 板块强度综合 | agg_discrimination：强度分档 vs 后续板块收益区分度 | kline_sector_880 6.5 年齐；L2 批脚本 | M | B2 |
| BT-P1-009 | L2-01-1 结构强度 | 同上 | 同上 | S | B2 |
| BT-P1-010 | L2-01-2 动量排名 | sensor_monotonicity：排名分档单调 | 同上 | S | B2 |
| BT-P1-011 | L2-01-3 多周期动量 | 同上 | 同上 | S | B2 |
| BT-P1-012 | L2-01-4 板块资金流聚合 | agg_discrimination | **sector_fund_flow 2 天/money_flow 3.5 月——资金流源薄，先回补** | M | B2 |
| BT-P1-013 | L2-01-5 市场级调节注入 | agg_discrimination | kline_index 齐+L2 批脚本 | M | B2 |
| BT-P2-008 | L2-02 轮动序列追踪 | agg_discrimination：轮动状态分档区分度 | kline_sector_880+L2 批脚本 | M | B2 |
| BT-P2-009 | L2-02-1 RRG 轮动 | 同上 | 同上 | S | B2 |
| BT-P2-010 | L2-02-2 单板块预警 | 同上 | 同上 | S | B2 |
| BT-P2-011 | L2-03 调整周期进度 | 同上 | 同上 | S | B2 |
| BT-P2-012 | L2-03-1 扩散指标 | sensor_monotonicity | 同上 | S | B2 |
| BT-P2-013 | L2-04 板块级市场状态 | agg_discrimination | 同上 | S | B2 |
| BT-P2-014 | L2-04-1 轮动五分类 | 同上 | 同上 | S | B2 |
| BT-P2-015 | L2-04-2 虹吸态识别 | 同上+触发次数土规 | 同上 | S | B2 |
| BT-P2-017 | L2-05-1 水温档推导 | sensor_monotonicity（水温六段单调性） | 同上 | S | B2 |
| BT-P2-018 | L2-05-2 信号响应三件套 | agg_discrimination | 同上 | S | B2 |
| BT-P2-019 | L2-06 板块个股传导 | agg_discrimination：传导后个股超额 | 880+个股 kline_daily 齐 | M | B2 |
| BT-P2-020 | L2-06-1 三级放行门槛 | 同上（门通过/拒绝后续收益差） | 同上 | S | B2 |
| BT-P2-021 | L2-06-2 龙头识别 | 同上（龙头 vs 板块超额） | 同上 | S | B2 |
| BT-P2-022 | L2-06-3 强度加权传导 | 同上 | 同上 | S | B2 |
| BT-P2-023 | L2-07 回踩质量分级 | sensor_monotonicity：回踩质量分档 vs 反弹收益 | 同上 | S | B2 |
| BT-P2-024 | L2-07-1 回踩ABC | 同上 | 同上 | S | B2 |
| BT-P2-025 | L2-08 板块生命周期 | agg_discrimination：生命周期阶段区分度 | 同上 | S | B2 |
| BT-P2-026 | L2-09 催化剂识别 | agg_discrimination：催化后超额 | news_data 齐+事件链表需核 | M | B2 |
| BT-P2-027 | L2-09-1 事件图谱传导 | 同上 | 同上 | M | B2 |
| BT-P2-028 | L2-09-2 冲击标的生成 | 同上 | 同上 | S | B2 |
| BT-P2-029 | L2-10 同源补涨比价 | sensor_monotonicity：比价信号单调 | kline_daily 齐 | S | B2 |
| BT-P1-014 | L3-02 九阶段选票主链 | agg_discrimination：九阶段 vs 后续收益 | fundamental 全套在库（c3_fundamental 35 表）+L3 批脚本 | L | B2 |
| BT-P1-016 | L3-03-1 短线池5分制 | sensor_monotonicity：分数 vs 后续收益单调 | 同上 | M | B2 |
| BT-P1-017 | L3-03-2 波段池5分制 | 同上 | 同上 | M | B2 |
| BT-P1-018 | L3-03-3 双策略合流体检 | agg_discrimination：合流 vs 单流 | 同上 | M | B2 |
| BT-P1-019 | L3-04 负面否决器 | exec_quality 变体：否决后避损（反事实代理）或否决命中率 | 同上 | M | B2 |
| BT-P1-020 | L3-05 顺位排序 | sensor_monotonicity：顺位 vs 后续收益 | 同上 | S | B2 |
| BT-P1-021 | L3-06 环境开关 | agg_discrimination：开/关状态后收益差 | 同上 | S | B2 |
| BT-P1-023 | L3-07-1 打板选股链 | sensor_monotonicity | limit_up 历史薄（B2-a 回补） | M | B2 |
| BT-P1-024 | L3-07-2 多因子打分链 | sensor_monotonicity：因子分 vs 收益 | factor_registry 在库+factor_feature_value 表（设计态未执行，verify_schema_truth 既有漂移项） | M | B2 |
| BT-P1-025 | L3-07-3 其余sleeve链 | 同上 | 同上 | M | B2 |
| BT-P1-026 | L3-08 候选池输出 | agg_discrimination：入池 vs 落池后续收益差 | 同上 | M | B2 |
| BT-P2-031 | L3-01 Universe构建剔除 | agg_discrimination：剔除规则避损 | kline_daily+stock_basic 齐 | S | B2 |
| BT-P2-032 | L3-09 股票池分层维护 | agg_discrimination：层间迁移收益差 | 同上 | M | B2 |
| BT-P2-033 | L3-10 可交易性预检 | exec_quality 变体：预检拦截 vs 实际不可交易对账 | st_stock_list/suspend/kline 齐 | S | B2 |
| BT-P2-036 | L3-11-2 盘中涨速扫描 | sensor_monotonicity | kline_1min 14.7 亿行（2021-09 起）齐 | M | B2 |
| BT-P2-040 | L3-12-3 筹码分布 | agg_discrimination | kline_daily 齐（筹码为推算量） | M | B2 |
| BT-P2-041 | L3-12-4 形态结构识别(缠论) | sensor_monotonicity：形态信号 vs 后续走势 | kline_daily 齐 | M | B2 |
| BT-P3-007 | P-P1-01 持仓对账快照 | portfolio_attribution：台账快照 vs 实仓残差<1bp | **account_nav_daily 0 行——缺生产持仓快照落库** | M | B2 |
| BT-P3-009 | P-P1-03 逻辑存活判定 | agg_discrimination：存活/破位后续差 | 买入理由历史（signal_reason 字段在 sim_trade_log 仅 9 行——薄） | M | B2 |
| BT-P3-011 | P-P1-05 组合持仓体检 | agg_discrimination | 持仓快照缺（同 BT-P3-007） | M | B2 |
| BT-P3-012 | P-P1-06 体检结论清单 | agg_discrimination | 同上 | S | B2 |
| BT-P3-013 | P-P2-02 做T策略调度 | exec_quality+做T成本（CST-T0-001） | D 后 fill+做T配对脚本（与 BT-P0-003 共用） | M | B2（紧随 B0 D2 批） |
| BT-P3-014 | P-P2-04 减仓再平衡 | exit_counterfactual 代理/归因对账 | 通用反事实依赖 | M | B2 |
| BT-P3-015 | P-P3-01 加仓资格门 | agg_discrimination：加仓 vs 不加仓后续差 | kline 齐+加仓动作历史缺（无生产加仓流水表） | M | B2 |
| BT-P3-016 | P-P3-02 金字塔加仓 | 同上 | 同上 | M | B2 |
| BT-P3-017 | P-P3-03 加仓量级核算 | 同上 | 同上 | M | B2 |
| BT-P3-018 | P-P3-04 加仓时点执行 | exec_quality（加仓单滑点） | D 后 fill 无加仓标记——需动作归因 | S | B2 |
| BT-P3-036 | F-C1 预算切分 | portfolio_attribution：切分后各 sleeve 归因对账 | **account_nav_daily 0 行+alloc_budget_daily 在库（行数未核）** | M | B2 |
| BT-P3-039 | F-C2-01 目标聚合轧平 | portfolio_attribution | 同上 | M | B2 |
| BT-P3-041 | F-C2-03 相关性聚类 | agg_discrimination：cluster 上限干预效果 | 收益历史齐+调仓历史缺 | M | B2 |
| BT-P3-042 | F-C2-04 budget变动升级 | agg_discrimination | alloc_budget_change_log 在库（行数未核） | S | B2 |
| BT-P3-043 | F-C3-01 多维归因引擎 | portfolio_attribution：归因残差<1bp 且符号一致，≥30 交易日 | **归因=对账账本，account_nav_daily 空——先落账本** | L | B2 |
| BT-P3-044 | F-C3-02 升降级管线 | agg_discrimination：升降级判据 vs 后续表现 | factor lifecycle 状态历史 | M | B2 |
| BT-P3-045 | F-C3-03 sleeve调权 | portfolio_attribution | 同 F-C1 | M | B2 |
| BT-P3-046 | F-C3-04 参数校准闭环(walk_forward) | 自判据：WFA OOS 稳定性（bt-fw-* 产物已有 11 支可复用） | bt-fw 产物在库 | M | B2（产物可即用，判据须冻结） |
| BT-P3-047 | F-C3-05 信号健康可靠度 | sensor_monotonicity：滚动 IC 衰减 | 信号历史表（factor_feature_value 设计态未执行） | M | B2 |
| BT-P3-048 | C-L1 币圈大盘总闸 | agg_discrimination（crypto 分档） | crypto_kline_daily 13 个月（2025-08→2026-09）——窗口短可先跑但结论弱；TDM-C 节点 pending_build | M | B2（尾部） |

**L0 计划族（5 条）——先裁定方法学归属（新裁定 R-E：五类方法学不含"计划编排质量"，建议增"计划质量"判据=计划 vs 次日实际偏差分布，或挂 agg_discrimination 兜底）**

| object_id | 节点 | 做什么/验收 | 依赖 | 量 | 批次 |
|---|---|---|---|---|---|
| BT-P2-002 | E-L0 盘前作战计划 | 计划质量：计划动作 vs 当日实际偏差达标 | 每日计划历史产物无 CH 表（散落文件）；regime_snapshot_history 齐 | M+裁定 | B2 |
| BT-P2-003 | E-L0-01 计划生成 | 同上（生成质量） | 同上 | M | B2 |
| BT-P2-004 | E-L0-02 偏离监控 | 偏离检出率/误报率 | 同上 | S | B2 |
| BT-P2-005 | E-L0-03 收盘复盘边界 | 复盘结论 vs 次日实际 | 同上 | S | B2 |
| BT-P2-006 | E-L0-04 明日情绪预测 | sensor_monotonicity：预测分档 vs 次日情绪 | 同上 | S | B2 |

#### B2-d 容器/结构点（testable=false，16 条 B2 组；B0/B1 组的容器 BT-P2-042、BT-P3-020 已列前）——不独立开考，随子节点批聚合出数

BT-P2-001（E-FLOW）、BT-P3-001（P-FLOW）、BT-P3-002（X-FLOW）、BT-P3-003（F-FLOW）、BT-P2-007（E-L2）、BT-P2-016（E-L2-05）、BT-P2-030（E-L3）、BT-P1-015（E-L3-03）、BT-P1-022（E-L3-07）、BT-P2-034（E-L3-11）、BT-P2-037（E-L3-12）、BT-P3-004（P-P1）、BT-P3-005（P-P2）、BT-P3-006（P-P3）、BT-P3-037（F-C2）、BT-P3-038（F-C3）、BT-P3-049（C-L2）、BT-P3-050（C-L3）、BT-P3-051（C-L4）。
四件事统一：做什么=不独立开考（D108 合并判据），容器行随子节点最新 verdict 聚合；依赖=各自子节点批次；工程量=S（runner 写行已含容器，前端按子节点聚合渲染）；批次=随子节点（多数 B2；BT-P3-049/050/051 三条 crypto 容器随 BT-P3-048 尾部）。

### 2.5 B3 愿景模板件（3 条）——对象本身未建，先建后考

| object_id | 对象 | 做什么/验收 | 依赖 | 量 | 批次与理由 |
|---|---|---|---|---|---|
| BT-P1-030 | 板块轮动策略包模板 | 先建策略包（策略假设+考试规格预注册冻结）→按 sensor/agg 判据考 | kline_sector_880（6.5 年）+分钟线在库；**缺=策略包本体** | L | **B3**：Owner 愿景映射 L2 薄层件，E4 考前须批次决策点冻结 |
| BT-P1-031 | 组合日度编排闭环 | 先落编排器蓝图过审→pf_alloc production 接线（裁定#257②触发条件）→闭环 vs 手动对照 | pf_alloc production 接线 | L | **B3**：L4 缺电件，依赖生产接线裁定 |
| BT-P2-055 | 底仓+日内回转执行模板 | 先建模板（日回转额度≤前收盘持仓显式建模）→做T成本联调（H2）验收 | CST-T0-001+t0_cost_model.py 在库；**缺=模板本体** | L | **B3**：S-OWNER-001 做T臂执行底座 |

---

## 三、与分包D①台账分诊的交叉引用与冲突对齐

| 交叉点 | backlog 条目 | 台账状态（分包D①） | 对齐判定 | 冲突 |
|---|---|---|---|---|
| L4 执行族 14 节点 | BT-P1-027/028、BT-P2-043..053 | 15 行 pending，全判**可考**（D1 批） | 一致：backlog 无冻结 plan（"验收阈值未预注册"），但 runner 土规线 20/40bp 已冻结在代码+BT-P0-001/002/003 同族冻结记录中——**按 B0 跑前须批次决策点对 L4 批阈值清单补一次冻结留痕**（SOP-B 护栏③），非冲突 | 无（补一道冻结手续） |
| 成本三件套 | BT-P0-003（plan frozen） | 4 行 pending，全判**可考**（D2 批） | 一致：阈值已冻结，直接排 D2 | 无 |
| E-L4 容器 | BT-P2-042 testable=**false**（不独立开考） | 台账有 TDM-E-L4 的 pending 行（runner batch=L4 把容器一并写行） | **口径噪声**：backlog 说不独立开考，台账却写了行。处置建议：容器行按子节点聚合语义解读（前端按节点最新行渲染即可），不必删行（append-only 纪律）；登记为观察项，与裁定 R-D（superseded 标记）合并处理 | 轻微（已给处置） |
| X 流族 | BT-P3-019/021..030（S1/R1 族）、BT-P3-031..035（S2 族） | 19 行 pending：18 节点**需裁定**、X-S2-01 节点可考 | 一致：S1/R1 族=反事实依赖（§12 放行+provider）→B2；S2 族=backlog 判据未注册 vs 台账已判"改挂 exec_quality 即可考"→B1（一次裁定 R-A） | 无 |
| X-S2-01 执行方式路由 | **无独立 backlog 条目**——归属 BT-P0-003 成本三件套（exec_quality） | X 批给了 exit_counterfactual 行+成本批给了 exec_quality 行 | 一致：backlog 归属（exec_quality）与台账最新行口径一致；X 批旧行为口径噪声 | 无（backlog 归属为准） |
| L1 总闸/聚合 | BT-P0-001/002（plan frozen） | 两节点 valid（09-12/09-14） | 一致：DONE；裁定#230 的 amendments 已回写 BT-P0-002 plan | 无 |
| 做T族 | BT-P3-013（P-P2-02）、BT-P0-003 含 P-P2-01/03 | P-P2-01/03 在台账 pending（可考，D2） | 一致：BT-P3-013 排 B2 紧随 D2，共用做T配对脚本与 CST-T0-001 | 无 |

## 四、诚实清单

1. 覆盖度核查时点=2026-09-17，CH 行数为当日快照；alloc_budget_daily/alloc_budget_change_log 等少数表"在库但行数未核"已逐条标注，未核者不作为就绪证据。
2. D 后 fill 的 4 个交易日窗口全部来自 bt-fw-* walk-forward 产物（OOS 折）；不同 run 覆盖同窗口，全量聚合口径混 run，逐 run 拆分未做（runner 现无 run 维度参数）。
3. news_data/news_sentiment_window 对 S0/S0-1 的就绪判定基于表覆盖（2010 起 820 万行），未验证新闻情绪打分产物列的 PIT 质量。
4. 工程量 S/M/L 为分包代理经验估计（±50%），非排产承诺。
5. B0 批"零新裁定"以"20/40bp 土规线冻结记录可平移到 L4 批清单"为前提；若批次决策点认为 L4 批需独立阈值清单，则 B0 增加一次冻结手续（仍属决策点例行，非新裁定项）。
6. 本报告未改任何真源；backlog 的 plan/threshold 冻结动作全部留给批次决策点。

---

*报告完。可复现查询见姊妹篇 2026-09-17-node-verdict-triage.md 附录 A。*
