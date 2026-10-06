---
campaign: matrix-20261006
lane: S-skeleton
status: draft
ttl: task_bound
---

# st_l9_alt —— TDM 数据与知识供给（entry_flow L9，44 节点）

- 真源: `config/trading_decision_map.yaml`；行号=TDM:L*。类别=H9 §1.9（本族判定为组级转录+逐组点名）。
- 计数: 44 = A3 / B3 / C30 / D8。接线级: L1 3 / L2 3 / L3 1（G3）/ L4 29 / ND 8。

## 1. 族内节点全清单与接线现状

源线 A 系（16）：

| node_id | 名称 | 类别 | 接线级 | 现状 | 行 |
|---|---|---|---|---|---|
| TDM-E-L9-A01 | 源线·日线/分钟行情 | A | L1 | load_px←c1_market.kline_daily（_c4_engine:135-149） | TDM:L4681 |
| TDM-E-L9-A02 | 源线·Tick分笔 | B | L2 | ch_tick_replay+event_driven tick 引擎在册，网格不消费 | TDM:L4706 |
| TDM-E-L9-A03 | 源线·板块/概念指数 | C | L4 | 图纸源线（live 有 sector 数据面，考卷零消费） | TDM:L4732 |
| TDM-E-L9-A04 | 源线·估值 | B | L2 | load_valuation 在考卷引擎自身（_c4_engine:189-229），网格因子不消费 | TDM:L4757 |
| TDM-E-L9-A05 | 源线·财务 | B | L2 | fin_snapshot/fin_history 同上（_c4_engine:231-268） | TDM:L4782 |
| TDM-E-L9-A06 | 源线·资金流 | C | L4 | 图纸；考卷无资金流因子 | TDM:L4807 |
| TDM-E-L9-A07 | 源线·千股千评 | C | L4 | 图纸 | TDM:L4832 |
| TDM-E-L9-A08 | 源线·航运运价BDI | C | L4 | 图纸 | TDM:L4857 |
| TDM-E-L9-A09 | 源线·财经快讯情绪 | C | L4 | 图纸（live 有 news 面；断供史 chief 02 §2） | TDM:L4882 |
| TDM-E-L9-A10 | 源线·国际宏观 | C | L4 | 图纸 | TDM:L4908 |
| TDM-E-L9-A11 | 源线·能源库存 | C | L4 | 图纸 | TDM:L4933 |
| TDM-E-L9-A12 | 源线·天气 | C | L4 | 图纸（台风 F7 断供见 chief 02 §2） | TDM:L4958 |
| TDM-E-L9-A13 | 源线·股东户数 | C | L4 | 图纸 | TDM:L4984 |
| TDM-E-L9-A14 | 源线·互动易问答 | C | L4 | 图纸 | TDM:L5009 |
| TDM-E-L9-A15 | 源线·加密永续/费率 | C | L4 | crypto 域（另见 st_crypto） | TDM:L5035 |
| TDM-E-L9-A16 | 源线·投入产出 | C | L4 | 图谱邻接（G5 同源） | TDM:L5061 |

源线 B 系另类（10，全 C/L4 图纸）：TDM-E-L9-B01 卫星影像（L5086）/TDM-E-L9-B02 美国官方天气海洋（L5111）/TDM-E-L9-B03 招聘JD（L5136）/TDM-E-L9-B04 电商价格（L5161）/TDM-E-L9-B05 招投标（L5186）/TDM-E-L9-B06 社媒舆情X/Reddit（L5211）/TDM-E-L9-B07 雪球股吧散户情绪（L5236）/TDM-E-L9-B08 APP榜单（L5261）/TDM-E-L9-B09 进出口贸易（L5286）/TDM-E-L9-B10 信用卡支付消费（L5311）。

源线 C 系实时另类（3，全 C/L4）：TDM-E-L9-C01 实时门店客流（L5336）/TDM-E-L9-C02 银行网点信贷活跃（L5361）/TDM-E-L9-C03 直播电商实时成交（L5386）。

图谱 G 系（5）：TDM-E-L9-G1 Zephyr产业链（C/L4，L5411）/TDM-E-L9-G2 ChainKnowledgeGraph事实层（C/L4，L5439）/**TDM-E-L9-G3 实体股权穿透（C/L3，mod=scripts/entity_graph/equity_penetration.py，L5465——本族唯一 live 在岗的 C）**/TDM-E-L9-G4 概念题材（C/L4，L5492）/TDM-E-L9-G5 投入产出传导（C/L4，L5518）。

状态变量/治理/假设/验证（10）：

| node_id | 名称 | 类别 | 接线级 | 现状 | 行 |
|---|---|---|---|---|---|
| TDM-E-L9-V1 | 状态变量快照·大盘 | D | ND | plan_engine/judgment_ledger（sim plan-bridge 只读消费） | TDM:L5544 |
| TDM-E-L9-V2 | 状态变量快照·情绪 | D | ND | 无 module_ref | TDM:L5569 |
| TDM-E-L9-V3 | 状态变量快照·板块 | D | ND | judgment_ledger | TDM:L5594 |
| TDM-E-L9-AGG | 知识供给汇聚 | D | ND | l9_readiness_aggregator；2 mounts——数据就绪运维 | TDM:L5619 |
| TDM-E-L9-D1 | 决策假设·因子组合挖掘 | A | L1 | scripts/backtest/mcts_expression_search.py（D_BACKTEST 域） | TDM:L5646 |
| TDM-E-L9-D2 | 决策假设·登记与考试方案 | D | ND | 预注册治理（search_space_prereg 册）；MOD-AU-008 | TDM:L5670 |
| TDM-E-L9-E1 | 验证·一问一考考试链 | A | L1 | trading/validation/runner.py+框架 layered/strategy 验证管线 | TDM:L5695 |
| TDM-E-L9-E2 | 验证·结论回传与修正 | D | ND | 治理闭环 | TDM:L5719 |
| TDM-E-L9-Z1 | 治理·问题治理与状态机 | D | ND | 治理域 | TDM:L5743 |
| TDM-E-L9-Z2 | 治理·净零与资产对账 | D | ND | scripts/governance/reconcile_chain_refs.py | TDM:L5768 |

段计数：16+10+3+5+10 = 44 ✓。

## 2. 缺口与可考性判定

- A3 枚（A01 行情/D1 挖掘/E1 考试链）=考卷消费面全部家底（与 H9 §0"考卷载荷仅 close/index/breadth/etf/valuation/fin/ST/成分/limit 表"一致——注意 index/breadth/etf 在 TDM 无独立源线节点，属 A01/A03 邻域，登记为口径注记）。
- B3 枚（A02/A04/A05）=S 级接线位（H9 S3：估值/财务载荷函数已在考卷引擎自身，接入因子面即考）。
- C30（另类 29+G3）：H9 L3 判"每条=数据工程+因子工程，破净零纪律风险高，逐条立项替代声明"——本车道维持同判，并补充：C30 中 29 枚连 live 模块面都未挂（L4 图纸），仅 G3 有 live 脚本。
- D8=治理/台账/快照域，天然不进回测。

## 3. 一句话修复建议

先落 S3（估值/财务两线进因子面，S 级）；另类 30 条按"净零替代声明+Owner 立项"逐条排队，禁批量铺线（数据工程每线都要过 PIT 哨兵，H9 §4.7）。

## 4. 交叉验证

- H9 §1.9 组级判定转录+本车道逐节点接线级拆分（H9 表为节点组粒度，本册拆到单节点=补充挖矿）。
- chief B1 ENV-07（L9=44）计数一致；chief 02 §2 数据断供组（新闻/期权/台风/reservoir 等）是本族 live 侧的运行态账，归 st_data_legs 转抄。
- census 图12（数据供给链）与 L9 分工：L9 是"决策消费面源线目录"，图12 是"采集入库运维链"——census §2.3 判"数据管线不进 TDM 也不进工厂"与此一致。
