---
campaign: matrix-20261006
lane: S-skeleton
status: draft
ttl: task_bound
---

# st_l3_stock —— TDM 个股选择（L3 cn_a，25 节点——现行考卷主干所在层）

- 真源: `config/trading_decision_map.yaml`；行号=TDM:L*。类别=H9 §1.4。
- 计数: 25 = A5 / B2 / C13 / 组骨架 L4 5。crypto C-L3 归 st_crypto。

## 1. 族内节点全清单与接线现状

| node_id | 名称 | 类别 | 接线级 | 引擎旋钮/模块 | 行 |
|---|---|---|---|---|---|
| TDM-E-L3 | 个股选择（组骨架） | C | L4 | 无（strat mounts 6 sleeve=daban/multifactor/eventdriven/topn-momentum/default-equity/STR-VREV-001） | TDM:L1579 |
| TDM-E-L3-01 | Universe构建与剔除 | A | L1 | G_universe=[hs300,zz500,all_a_ex_st]（schema:50-54）+filter_st（executor:198-232；_c4_engine:318-341） | TDM:L1611 |
| TDM-E-L3-02 | 九阶段选票主链 | C | L3 | signal_fundamental/selection_funnel；strat STR-MULTIFACTOR-042；考卷 fin 载荷在册不消费 | TDM:L1646 |
| TDM-E-L3-03 | 双池评分（组骨架） | C | L4 | 无 | TDM:L1676 |
| TDM-E-L3-03-1 | 短线池5分制 | C | L3 | fine_scoring_engine；strat STR-MOMTREND-008 | TDM:L1704 |
| TDM-E-L3-03-2 | 波段池5分制 | C | L3 | quant_short_term_strength_engine；strat STR-MOMTREND-009 | TDM:L1735 |
| TDM-E-L3-03-3 | 双策略合流体检 | B | L2 | F_merge_policy=[single,equal_capital,equal_risk,signal_additive]（schema:44-48）；引擎不读 F 键（executor:590-663） | TDM:L1767 |
| TDM-E-L3-04 | 负面否决器 | C | L3 | signal_fundamental/negative_veto；strat STR-MULTIFACTOR-034~041 六挂 | TDM:L1799 |
| TDM-E-L3-05 | 顺位排序 | A | L1 | 截面 rank+Top-N（executor:644-651） | TDM:L1838 |
| TDM-E-L3-06 | 环境开关 | B | L2 | 同 L1 的 J 维+regime 三件套 | TDM:L1867 |
| TDM-E-L3-07 | 策略专属链（组骨架） | C | L4 | 无 | TDM:L1898 |
| TDM-E-L3-07-1 | 打板选股链 | C | L3 | pf_core/strategies/daban_sleeve_strategy；strat STR-DABAN-001/STR-MULTIFACTOR-048 | TDM:L1926 |
| TDM-E-L3-07-2 | 多因子打分链 | A | L1 | A1 标准化 6 值×A2 合成 8 值全维精确实现（executor 头注 v1/T2a/T2b；schema:13-27） | TDM:L1963 |
| TDM-E-L3-07-3 | 其余sleeve选股链 | C | L3 | event_driven_sleeve_strategy；strat STR-TSMALL-001/STR-VAL-001 | TDM:L1995 |
| TDM-E-L3-08 | 候选池输出 | A | L1 | Top-N 权重宽表=每日候选池（executor:644-663） | TDM:L2037 |
| TDM-E-L3-09 | 股票池分层维护 | C | L3 | core/pool_tier_maintenance；MOD-SIG-126；strat STR-MULTIFACTOR-033 | TDM:L2071 |
| TDM-E-L3-10 | 可交易性预检 | A | L1 | 涨跌停封板可成交性闸（_c4_engine:453-497 apply_fillability_gate） | TDM:L2107 |
| TDM-E-L3-11 | 日内动态选股（组骨架） | C | L4 | 无 | TDM:L2145 |
| TDM-E-L3-11-1 | 竞价选股 | C | L3 | auction_microstructure_analyzer；框架 tick 引擎在册无竞价段考卷 | TDM:L2174 |
| TDM-E-L3-11-2 | 盘中涨速异动扫描 | C | L3 | intraday_t0/intraday_volume_orderflow；strat STR-MULTIFACTOR-031 | TDM:L2202 |
| TDM-E-L3-12 | 个股多维验证（组骨架） | C | L4 | mounts MOD-SIG-092/096/103/127 | TDM:L2233 |
| TDM-E-L3-12-1 | 个股资金面分析 | C | L3 | capital_flow_pattern_analyzer；考卷无资金流因子 | TDM:L2262 |
| TDM-E-L3-12-2 | 龙虎榜席位追踪 | C | L3 | limit_up/seat_pattern_analyzer | TDM:L2292 |
| TDM-E-L3-12-3 | 筹码分布分析 | C | L3 | regime/features/chip_distribution_engine；MOD-SIG-124 | TDM:L2326 |
| TDM-E-L3-12-4 | 形态结构识别（缠论） | C | L3 | chanlun_structure；MOD-SIG-091/115/145/146/148/149 | TDM:L2366 |

## 2. 缺口与可考性判定

- A5 枚=现行考卷主干（宇宙/顺位/多因子/候选池/可交易性）——Owner 命题"T1/T2 考的是因子选股主干"在本层的机械证据。
- B2 枚：L3-06 随 T3a 开 J 即考；L3-03-3 需 F 维执行器消费（H9 §1.4：接口在、执行器零实现）。
- C13 枚分层：基本面漏斗（02）、双池（03-1/03-2）、打板（07-1）、其余 sleeve（07-3）、池分层（09）、日内（11-1/11-2）、多维验证四件（12-1~12-4）——M8（双池最简版）是 H9 给出的最近考卷化路径；日内两枚归 L1 级（tick 考卷，H9 §4.2 做T 同判）。
- 池分层维护（09）是有状态日频维护，考卷无状态——半结构性缺口（H9 §1.4"考卷无此层"）。

## 3. 一句话修复建议

按 H9 M8 落双池最简版（动量池/低波池双 5 分制+F 维 signal_additive 搭桥），并把 STR-* 挂载的六 sleeve 中 event_driven/tsmall/val 三链列为第二轮考卷化候选。

## 4. 交叉验证

- H9 §1.4 判定全转录对平（A5/B2/C18 含组 5——H9 将组节点计入 C，本册拆 L4 展示）。
- chief B1 ENV-10（TDM L3=26 含 C-L3）计数一致。
- TDM-E-L3-01 的 strat mounts STR-MULTIFACTOR-043/044 与 03-3 的 045/046：图上策略挂载集中在 L3——策略卡域（图15）与 TDM 的挂接面，登记备矩阵考试。
