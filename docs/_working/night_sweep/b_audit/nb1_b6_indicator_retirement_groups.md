---
ttl: task_bound
title: "NB1 B6 裁定卡：指标退役候选群——CHIPS 5 条单独卡+零引用残差 61+宏观空转 15 三档分层"
session: st-nightsweep2-nb1-20260930
updated: 2026-09-30
---

# B6 指标退役候选群 · 分层裁定卡（CHIPS / residual 61 / macro zero 15）

## 事项

分层处理：CHIPS 5 条（获利盘族）单独论证；"族⑩ residual 61"+"族⑤ macro zero 15"按**设计完成度×数据持续性×融合空间**粗分三档。本车道零执行，只产裁定。

## 一、CHIPS 5 条（IND-CHIPS-001~005，获利盘/筹码族）——价值高，建议接线

**六向快照**：通道=technical_indicator_registry.yaml:4619-4800（v1.1.0，2026-09-21 批10 新建）；原料=c1_market.kline_daily（high/low/close/volume/turnover_rate；volume 手→股量纲已治本，裁定#398/#399）；状态=**已量化+已验收**（chips.py 493 行 MOD-L02-031，CYQ 独立实现复算 000852 近 20 日 0 偏差对表；142 在产指标机读对齐 REG-IND-001）；消费方=**零下游**（used_by_factors 空，decisions_map_campaign 14_consumption_census.md:57 "批 10 新产…零下游（未入机账）"）；缺口=消费未接；处方=下。
**三审**：①价值——获利盘（chips_winner）/单峰密集度是 TDM-E-L3-12-3 筹码分布分析节点（trading_decision_map.yaml:2089-2114）**明文挂起的核心语义**（"获利盘占比/单峰密集度 语义未实现挂起（需流通股本数据工程）"，裁定#257④=D21）；而 CYQ 的 chips_winner 基于**换手率衰减迭代分布**，**不依赖流通股本**即可先行出数——即 D21 最重的数据工程未落地前，CHIPS 族已能把"获利盘"半语义先通。②真源唯一——chips.py 是全仓唯一筹码实现；TDM 消费端 chip_distribution_engine（MOD-REGIME-005，464 行）输出 4 指标（long_term_bottom_ratio 等）**不含 winner**，两者是"同节点不同剖面"互补非重复（chip_conc_90 与 SCR 同公式双条目 overlap 已在册登记，消费端择一）。③数据持续性——日 K 活源，持续供数成立。
**三态裁定：保留+接线（转绿路径=D21）**。处方：①P1 接线=chip_distribution_engine 增补 winner 剖面时直接调 factor/technical_indicators/chips.py::CYQ（禁第二套分布实现），TDM-E-L3-12-3 算法注补"获利盘占比由 CHIPS-001 供给"；②trial 期信号不进决策（沿用#257④ 回 trial 纪律），先回测出 IC 证据回填 evidence 字段；③D21 流通股本到位后升级"单峰密集度"全语义；④CHIP_CONC_90/SCR 双条目在消费端二选一并登记选择。

## 二、"族⑤ macro zero 15"——宏观零消费 15 条 → 并入 B5 卡，不独立退役

**判读**：macro_indicator_registry entry_count=15（实 16）与"macro zero 15"数吻合——指 MAC 族 15/16 条 status=candidate+数值消费零接线（唯一 TDM 声明挂 8 条亦无代码消费）。其数值数据源（macro_data akshare 291K 行）**活着**，缺的只是映射与消费两根线 → 按 Owner 三审属"建好了还没引用"，处置全权归 **NB1_B5 卡（保留+接线，R1-R5 处方）**。本档**零退役零储备**，仅一条连带：c1_market.edb_data 空壳表（iFind 断供、known_data_gaps accepted）随 B15 空壳表通道走"归档留 DDL"，**禁止**把 16 条注册表条目连同 edb 死表一起葬。

## 三、"族⑩ residual 61"——零引用数据表残差 61 → 三档分层

**口径说明（可复算）**：63 号审计（docs/_audit/data_utilization_audit_2026-08-24.csv，106 表）zero_ref=59，加 l2_tick+edb_data 两张审计外空壳=61。**注意：zero_ref≠空表≠垃圾**，CH 本夜不可达无法 live 验行数，以下分档以文档真源为准，DROP 前必须补行数+代表性取样三步验证（CH 复活后）。

| 档 | 判据 | 成员（代表例证） | 处置 |
|---|---|---|---|
| **A 直接可退**（≈20 张，死工具的伴生结果表） | 上游实现已判装饰/退役（F127/B12 族）且无独立数据价值 | DS-060 data_lake_manager（F127 自伴表）、DS-061 knowledge_cleaning、DS-062 stream_processing、DS-063 synthetic_data、DS-064 training_data_manager、DS-045~055（anomaly_diagnoser_result/mining_agent/causal_validator/feature_store 等 B12 运行时装配批 32 模块的 result 表群）、DS-041~044 barra 四件（风险模型未上马） | 归档 DDL+权限样例 → G:/zephyr_cold/retire_c267_20260930 同构目录扩册 → CH 复活后 DROP（走 C 道三步验证+Owner 门：注册表净删=§5 high 域） |
| **B 需储备**（≈35 张，有源可灌、无当下消费） | 上游免费活源存在、设计完成但消费未到 | ashare_* 14 张（DS-015~028，akshare 宽源快照）、fin_* 7 张（DS-087~093 财务三表+指标+预告，基本面线原料）、DS-095 share_float（**D21 流通股本正主！**）、DS-096 holder_trade、DS-080 lhb_detail（L2 情绪原料）、DS-085 st_status、DS-102 sw_daily（板块线）、DS-077~079 renko/point_figure/kagi（图形族）、DS-070 portfolio_aggregate、DS-073/074 | **只储备不删**：DDL+字段字典+源映射卡入 G:/zephyr_cold 储备册；share_float 单独标"优先复活"（喂 D21/CHIPS 全语义） |
| **C 值得接线/需数据复核**（≈6 张） | 疑似假零引用或与活链强相关 | **DS-002 ohlc_bar**（零引用但名疑似 kline_daily 前身——若有存量行情数据=资产非垃圾，DROP 前必须行数+对 kline_daily 覆盖比对，重叠则归档后退役、不重叠则升级为储备）；DS-086 daily_basic（stock_daily_basic 活表兄弟，疑似审计漏计消费）；DS-040 turnover_analyzer（CHIPS 族换手率原料相关）；DS-075 drawdown_metric、DS-056/057 push/tick manager（回测/实时链近邻） | CH 复活后逐一 live 复数+消费重扫（import 面+memo 面），按实况改判 A 或 B；**禁止凭本卡 A/B 档直接动 C 档** |

**三态裁定（61 张整族）**：**分层处置**——A 档"删除（归档后）"、B 档"储备（G:/zephyr_cold 储备册）"、C 档"挂起待 live 复核"。执行全部归 NB2/C 道，本卡只交分层与判据。

## 自审闸三态

**挖干（置信度=中高）**。可复算：CHIPS 五条注册表原文+chips.py/chip_distribution_engine 现读+TDM:2089-2114 挂起注+consumption_census:57/89+63 号审计 CSV 全量分档明细（本卡存档口径）。未干残余：①"61"口径系 59+2 推导，若 Owner 手册另有原生清单以原生为准；②全部行数判读基于 2026-08-24 CSV+文档，**非 live**（CH VM 不可达），A/B 档任何 DROP 动作前必须补 live 三步验证；③DS-002 ohlc_bar 与 kline_daily 的覆盖关系未核（C 档头号）。
