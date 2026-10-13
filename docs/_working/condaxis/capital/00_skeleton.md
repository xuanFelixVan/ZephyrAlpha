---
ttl: task_bound
title: 资金行为线骨架总册——契约四件套 A/B/C/D→环节映射＋封顶声明（CONDAXIS-CAMPAIGN 资金域挖矿车道）
created: '2026-10-13'
session: st-condaxis-20261013
status: mining_workbook
family_id: CONDAXIS-CAMPAIGN
completes_when: 资金行为线各环节施工完成且随 CONDAXIS-CAMPAIGN 归档
---

# 资金行为线骨架总册（00）

> **上游真源**：输入研究册=[`00_inputs/2026-10-13-capital-behavior-research-dossier.md`](../00_inputs/2026-10-13-capital-behavior-research-dossier.md)（CAPFLOW-RESEARCH，含 2026-10-13 总包核验更正记录）；方法论=[mining_sop_policy](../../../01_policies_and_standards/sop/mining_sop/mining_sop_policy.md)＋[skeleton_mining_policy](../../../01_policies_and_standards/sop/mining_sop/skeleton_mining_policy.md)。本册=资金域施工前挖矿作业簿的骨架层：只做路由/计分/防腐三职责，**判据面零冻结、数值零自拟、零考试**（对齐研究册纪律声明）。
> **本车道边界**：只写本目录；不改代码/配置/注册表；不 git commit（只 git add）。施工裁决走 CONDAXIS-CAMPAIGN P1 统一呈批包。

## §1 输出契约四件套 → 环节映射（路由表）

研究册 §2.2 输出契约四件套（候选草案，待 Owner 呈批 10.1）映射到本目录六件环节作业簿：

| 契约件 | 环节作业簿 | 回答的问题 | 核心仓内资产 | 状态计分 |
|---|---|---|---|---|
| **A 筹码结构快照**（存量体检） | [1_A_structure.md](1_A_structure.md) | 还剩谁没卖、上面压着谁 | chips.py CYQ 内核（production）＋ chip_distribution_engine winner 剖面（trial）＋ shareholder_count（✅在产） | ✅×2 🔨×1 ⬜×3 |
| **B 流量性质判定**（增量诊断） | [2_B_flow_nature.md](2_B_flow_nature.md) | 今天的量是什么性质 | volume.py 17 指标（production）；LM2002 ⬜零实现；wyckoff_engine **证伪态**（本次挖矿新发现） | ✅×1 🌑×1（wyckoff）⬜×2 |
| **C 主体画像**（行为归因） | [3_C_actor_profile.md](3_C_actor_profile.md) | 谁在买谁在卖 | money_flow/margin/block_trade/dragon_tiger(+seat)/shareholder_count/northbound_hold/etf_share/share_unlock 八源＋ MOD-SIG-056（design） | ✅×7 ⬜×1 🌑×1（北向日频） |
| **D 合成状态＋拐点信号集** | [4_D_synthesis.md](4_D_synthesis.md) | 合力方向＋拐点长什么样 | MOD-SIG-088 CapitalConsensus（testing，零消费）＋ condition_package 条件轴挂点 | 🔨×1 ⬜×2 |
| （横切）四模块收口 | [5_module_consolidation.md](5_module_consolidation.md) | 同域重复簇谁吞谁（w5_1） | SIG-021/022（production，下游=短线选股→打板 sleeve）＋SIG-088（testing）＋MOD-SIG-113（production，零 import 消费） | 🔨×1（方案矿） |
| （横切）数据面审计 | [6_data_audit.md](6_data_audit.md) | 数据会不会骗我们 | 15 张表 CH 行数实查（2026-10-13）＋披露制度漂移案例库 | 详见该册 |

**计分板口径**（骨架 SOP §5）：✅=实查在产（附查询/行号证据）；🔨=已定调在建或有设计文档；⬜=空白候选入口；💰=花钱可解；🌑=不可得/已死（点名留档）。逐格证据在各环节册 §1 台账。

## §2 骨架分层（大类→环节→件→施工产物）

- **大类（MECE 分域，对齐契约四件套）**：A 存量结构 ／ B 增量性质 ／ C 主体归因 ／ D 合成与拐点。横切两大类：模块收口（治理面）＋数据审计（供给面）——非信号件，是 A-D 的前置约束。
- **环节（完整性检查单元）**＝六件作业簿，每件内含"件"级台账（A1/A2/…/C1/C2/…）。
- **件（挖矿入口）**：每件一行台账，六向定位指明下一步往哪挖。
- **施工产物**：考试卡/指标列/观测适配器/合并工单——全部待 P1 呈批后进 construction_workflow 闭环，本作业簿不开施工令。

## §3 本次挖矿日志（mining SOP §7 纪律：无日志=没挖过）

矿脉母节点=资金行为层输出契约。轮次记录（内部反查为主，外部调研已由上游研究册完成，本车道不重复外挖）：

| 轮 | 矿脉 | 动作（内部实读/实查） | 判定 | 关键产出 |
|---|---|---|---|---|
| R1 | 筹码内核 | 实读 chips.py 493 行全文＋chip_distribution_engine.py 130 行＋winner 剖面 | signal | chips_winner 已落 c1_market.technical_indicator（daily，2019-01-02 起，日均 ~5.5k 标的非空）——A1 考试卡可直绑宽表列 |
| R2 | 量族 | 实读 volume.py 结构（17 指标类逐一确认）＋wyckoff_engine 全文级读 | signal | **wyckoff_engine=WYF-3 证伪态**（wyckoff_score 恒 0＋一次性告警，裁定#285）——研究册"在册"表述需更正；B2 不能建在它上面 |
| R3 | 主体数据面 | CH 只读实查 15 表（min/max date/count＋分日分布） | signal | 四个新发现：ETF 份额快照仅 2 个交易日有数（供给缺口）；tick_depth_5 停在 2026-09-30（竞价派生链断）；money_flow count()=ReplacingMergeTree 未合并版本虚高（uniqExact≈5,573/日才是真值）；block_trade/dragon_tiger 主表历史仅自 2026-08-07 |
| R4 | 四模块 | 实读 SIG-021/022/088/113 四文件头注＋方法清单＋全 src import 反查 | signal | SIG-021/022 经 short_term_stock_selector（字段级）→daban_sleeve_strategy（production sleeve 资格门）真实触达产线；SIG-088/113 零 import 消费——收口方案的事实底座 |
| R5 | 考试卡机制 | 实读 card_binding.py（1481 行）头注＋结构＋calibration_exam.py 头注＋两融 07 卡全文 | signal | A1 接入通道=exam_cards 目录+data_binding 段+card_binding RECIPES 配方表；两融 07 卡=同域已开考先例（status=examined） |
| R6 | 条件轴挂点 | 实读 condition_package.py 头注 | signal | 条件轴现为情绪灰度×大盘状态两轴；板块腿 observational-only 且 columns_forbidden=[capital_score, net_inflow_pct]——资金腿的挂接位与禁列先例都在 |
| R7 | 负存在断言（SOP §7.5） | grep LM2002/llorente、CGO/grinblatt、逐笔委托/entrust 全 src＋tasks.yaml | 查无（有效结论） | LM2002 零实现（复认）；CGO 零实现（仅除权参考价假阳性）；L2 唯一在册任务 l2_tick_snapshot 已退役冻结（tasks.yaml:1818-1831）——"未采集"实为"曾立项已冻" |

**矿脉清单长尾**（未挖/移交）：逐笔委托数据源商务可得性（💰，属 P1 呈批 10.4）；判据数值面全部（属 P2 预冻结，本作业簿禁碰）；ETF 申赎差分工程立项（P1 呈批 10.6）。

## §4 封顶声明（骨架 SOP §6）

1. **封顶**：本骨架 A/B/C/D 四大类＋两横切类封顶。此后增长只允许"件→施工产物"的实现（考试卡、指标列、适配器、合并工单），**不再增枝**；增枝须过骨架 SOP §3 停止判据三问（生产者变/验证口径变→拆；仅标签参数变→不拆）并在本册留理由。
2. **状态变更纪律**：每次实查后改标，改标留日期与证据指针；本目录作业簿随施工进展回写状态列。
3. **封顶≠死亡**：披露制度变更（类北向案）或新数据源接入可触发对应环节册重开，须留批次理由。

## §5 自审闸三态汇总（各环节册 §4 的总表）

| 环节册 | 三态裁定 | 一句话理由 |
|---|---|---|
| 1_A_structure | 施工（A1 考试卡先行）；挂起（A2/A3 待流通股本与判据冻结）；施工（A4 低频台账） | A1 是筹码引擎转正唯一通道（#257④），数据已就位 |
| 2_B_flow_nature | 施工（B1 LM2002 自实现＝先立卡）；方案封矿（B2 建在 wyckoff_score 上的一切变体）；施工（B2' effort/result 独立小指标另立卡） | wyckoff FSM 已证伪恒零，终局不再要它 |
| 3_C_actor_profile | 施工（证据链台账＋观测适配器骨架）；挂起（重定标级证据逐笔委托 💰 待 P1 10.4） | 七源数据在产，归因层零实现 |
| 4_D_synthesis | 挂起排期（strength 标定＝P2 判据面，解锁条件=C 适配器在产）；施工（CapitalConsensus 挂条件轴 observational 腿） | 骨架在、标定不在，先 observational 再统计 |
| 5_module_consolidation | 施工（合并方案呈批件——本作业簿即产物）；施工迁移=呈批后工单 | w5_1 同域重复簇，方案已到接口级 |
| 6_data_audit | 施工（三处供给缺口上报＋披露漂移监测候选设计）；挂起（L2 采集 💰） | ETF 快照/tick 断链/竞价派生断供是活着的火 |

## §6 边界声明

- 与**大盘两态形态班**（st-formreg-20261013）输入-输出关系不重叠：本线管"谁在做"，不管"价在做什么"；拐点信号池向其 P1 单边启动信号供料（研究册 §2.3）。
- 与**情绪线/条件轴现有两轴**：condition_package 情绪灰度×大盘状态为既有真源，资金行为腿=第三腿候选（挂接设计在 4_D_synthesis §3），禁本轮直接改 condition_package。
- 判据数值、考试门柱、阈值＝P2 预冻结领地，本作业簿全部以"待冻结"标注，零数值自拟。
