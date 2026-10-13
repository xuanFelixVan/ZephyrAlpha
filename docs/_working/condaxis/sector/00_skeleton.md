---
ttl: task_bound
title: 板块线环节骨架总册——五件套输出物→环节映射与封顶声明
created: '2026-10-13'
session: st-condaxis-20261013
status: mining_workbook
family_id: CONDAXIS-CAMPAIGN
completes_when: 板块线五环节施工完成且随 CONDAXIS-CAMPAIGN 归档
---

# 板块线环节骨架总册（st-condaxis-20261013 板块域挖矿车道）

> **令据**：条件轴总包战役（CONDAXIS-CAMPAIGN）板块线施工前挖矿令（2026-10-13）。
> **输入**：`docs/_working/condaxis/00_inputs/sector_problem_definition_2026_10_13.md`（含核验更正记录）；挖矿方法论=mining_sop_policy v1.9.1；骨架判据=skeleton_mining_policy v1.0.0。
> **纪律**：本册为施工前挖矿作业簿，零裁定、零开考、零代码改动；引用式冻结（指真源不抄数值）；研究册已核事实抽验复认，新发现留核验注。
> **边界**：本车道只写 `docs/_working/condaxis/sector/`；资金面/两态线/个股线分别归资本行为册与大盘两态班（00_inputs 另两册），不越界。

---

## §1 板块线在条件轴战役中的位置

研究册 §1.2 给出板块模块的五件套输出物（存在意义=把四个交易问题变成机器可考输出）：

| # | 输出物 | 回答问题 | 归属环节册 |
|---|--------|---------|-----------|
| ⓪ | 板块口径路由（前置基建） | 板块到底指哪套板块 | [1_universe_router.md](1_universe_router.md) |
| ① | 主线名单与梯队 | 现在钱在哪 | [2_mainline.md](2_mainline.md) |
| ② | 板块状态/阶段 | 它处于什么阶段 | [3_lifecycle.md](3_lifecycle.md) |
| ③ | 拐点信号集 | 什么时候进出 | [4_turning.md](4_turning.md) |
| ④ | 传导标的集 | 板块确认后买什么 | [5_conduction.md](5_conduction.md) |
| ⑤ | 环境闸门读数 | 现在能不能做 | [6_env_gate.md](6_env_gate.md) |
| ✦ | 验证班开班矿（横切） | 哪个信号真的有 IC | [7_validation_class.md](7_validation_class.md) |

板块线产品与两态班（st-formreg-20261013）在考试条件轴会合：**大盘态 × 板块态 × 个股传导 = 考试条件轴三段结构**（研究册 §1.4）。⑤ 的水温/大盘输入由两态班与情绪输出契约（00_inputs/2026-10-13-sentiment-output-contract-research.md §7 四层：L1 温度/L2 相位/L3 事件/L4 预测面）供料，对接面见 6_env_gate.md §3。

## §2 环节→仓内挂点速查（TDM 与数据面）

- TDM 挂点：`config/trading_decision_map.yaml` TDM-E-L2 板块选择子树，区段 :714-1669。**本车道实查注**：29 节点（含根 TDM-E-L2 与 stage 容器 TDM-E-L2-05）中，27 个计算节点 module_ref 挂满（yaml 解析逐节点核实，2026-10-13）；根 TDM-E-L2 与 TDM-E-L2-05（水温响应 stage，子节点 L2-05-1/05-2 已挂 sentiment_cycle/sector_gate）两个 stage 容器节点 module_ref 为空——研究册核验记录"29 处无一空挂"应精确为"**27/27 计算节点挂满，2 个 stage 容器空**"（grep 计 30 处 module_ref 键，含 list-form 多行）。此差异不改变结论（无孤儿计算节点），登记防后续误引。
- 数据面：三套口径（通达信 880/881、申万 L1-L3、概念）× 六张实表 + 快照/资金流/状态七表，行数与新鲜度实查见 1_universe_router.md §1。
- 图谱面：PG `ig_*` 14 表（+stock_concept 共 15 CREATE，DDL :54-407）实查规模 vs SQLite 小图零生产实例化，见 5_conduction.md §1-§2。

## §3 骨架计分板（挖矿覆盖度）

| 环节册 | 台账件数 | ✅在产 | 🔨在途(testing/design/new) | ⬜空白 | 💰花钱可解 | 🌑不可得 |
|--------|---------|--------|---------------------------|--------|-----------|----------|
| 1 口径路由 | 11 表+2 采集器 | 8 | 2 | 1（路由规则本体） | 0 | 1（板块分钟资金流） |
| 2 主线梯队 | 10 | 4 | 6 | 2（梯队标签件、IC 重加权数据线） | 1（分析师预期=班外） | 0 |
| 3 生命周期 | 9 | 3 | 6 | 1（统一五态词表映射） | 0 | 0 |
| 4 拐点信号 | 12 信号卡 | 4 | 6 | 2（催化证伪腿、盘中资金腿） | 1（分钟资金流外购=同一🌑） | 1（同上） |
| 5 传导标的 | 12 | 3 | 6 | 3（方向语义、时滞估计、链↔板块路由） | 0 | 0 |
| 6 环境闸门 | 8 | 3 | 4 | 1（两态对接消费端） | 0 | 0 |
| 7 验证班 | ~40 模块普查+判据 6 组 | — | — | 4（判据预冻结件本体未建） | 0 | 1（资金流 29 日样本窗硬约束） |

**覆盖度结论**：识别层骨架面全（研究册 §4.5 判定复认成立——缺的不是"怎么识别板块"），真正空白集中在**验证面**（7 号册）、**口径唯一化**（1 号册）、**方向语义**（5 号册）三处；两处数据硬缺口（分钟资金流=🌑 实测留痕、分析师预期=💰 Owner 门位）与研究册 §6 一致。

## §4 本车道新挖出的矿（研究册未载，2026-10-13 实查）

1. **板块资金流 concept 腿未接线**：`c1_market.sector_fund_flow` 实查 12,110 行**全部 sector_type='industry'**（2026-09-15 起 29 个交易日，日均 ~418 行≈90 行业×多次快照）；采集器（sector_fund_flow_collector.py:21-25）明载可用源含"90 行业+387 概念"，concept 腿零落库——②③ 环节的资金输入实际只有行业面。
2. **资金流历史仅 29 交易日**：min(trade_date)=2026-09-15——验证班对"资金持续净流入"类信号的最短数据腿（7 号册判据约束）。
3. **sector_state 断更 1 交易日**：max(trade_date)=2026-10-09；而 kline_sector_880 有 10-12 行（10-13 亦在）→ 10-12（周一）close_final 未落库，sector_state_pipeline 需巡检（非本车道施工项，登记移交）。
4. **kline_sector 表三源混存**：tqcenter（726 码，2026-06-17~10-13 新鲜）/ tdx（593 码，2025-07-18~2026-07-31 已停）/ tqcenter_880fix（2 码一次性修复）——表内自带历史断代，路由规则必须显式处理。
5. **SQLite 小图零生产实例化**：`IndustryChainGraph(` 全仓非测试零调用（quality_closeout_governance/gen_obj_r_s3 为同名误匹配）——双真源收敛方案的关键事实（5 号册）。
6. **ig_equity_edge DDL 有而 PG 无**：DDL :296 有 CREATE TABLE，PG 实查"关系不存在"——DDL 段未部署或分域差异，施工核（5 号册）。
7. **ig_chain 873 行 vs 前端 61 条主链**：链表含子链层级（level 列），两口径并存（5 号册）。
8. **生命周期词表三套五态并存**：rotation_state（市场级轮动 5 态）/detail_enricher（板块周期 5 态：酝酿/启动/发弹/高潮/退潮）/研究册①的短线 5 态（点火/主升/分歧/退潮/调整）——互不等同，统一映射=3 号册核心缺口。
9. **TDM-E-L2 module_ref 计数精化**（见 §2 实查注）。
10. **炸板信号已有两处实现**：limit_up_pool_collector（open_board_count 源字段）与 daban_exit_decision.py:96-107（T+1 触涨停未封收判定）——口径不同（次数 vs 事件），4 号册立卡区分。

## §5 封顶声明（skeleton_mining_policy §6）

1. 本骨架按五件套+验证横切定格为 **7 个环节册**；此为板块线的最终拓扑，不再增枝。
2. 此后增长=环节册内**件级立卡与施工**（信号卡/判据条目/表路由行），不再增环节；增枝须过 skeleton §3 停止判据（生产者变/验证口径变/仅参数变不拆）并留理由。
3. 板块线内 20+ 模块的增删并转一律经 7 号册验证班三裁（保持现状/降级为特征/退役）出口，不在环节册内私自定夺。
4. 封顶≠死亡：新案例批/考古批（skeleton §4）可触发本册批次重开。

## §6 挖矿日志（mining_sop §7 纪律）

| 轮 | 矿脉 | 判定 | 关键产出 |
|----|------|------|---------|
| R1 | 输入三件+研究册全文 | signal | 问题定义/五件套/红线复认 |
| R2 | sector 模块族头注普查（sector/ 16 件+core/ 4 件+mainline 2 件+IC 2 件+数据底座 9 件+周边 10 件，逐件实读 MATURITY/INVARIANTS） | signal | 7 号册台账根证据；成熟度断层量化（production 9/testing 13/new 6/design 4/experimental 1） |
| R3 | 已核实事实抽验（TDM yaml 解析/IC 红线 :25/10_d_data.md:14038/fund_flow docstring/03_graph_registry.md:19/sell_decision grep=0） | signal | 全部坐实 1 处精化（§4-9） |
| R4 | 口径三套实查（CH 13 表 count+max+uniq，business_data_categories.yaml 品类锚） | signal | 1 号册路由矿+§4-1/2/3/4 新发现 |
| R5 | 链图谱双真源（DDL 15 CREATE 逐表+PG 11 表 count+edge_type 分布+SQLite 调用方反查） | signal | 5 号册收敛方案矿+§4-5/6/7 |
| R6 | 拐点信号族定位（炸板/断层/虹吸/拥挤/回踩逐卡源码定位） | signal | 4 号册 12 信号卡 |
| R7 | 验证先例（sixphase-v1 冻结件/n_trial_ledger/sentiment 契约 §7/formreg 对接面） | signal | 7 号册判据骨架+6 号册对接面 |
| R8 | 长尾清点：板块 ETF 备兑/两融板块腿/期权板块暴露 | noise（本轮不挖） | 长尾登记：ETF 面属个股线弹药、两融按板块聚合属资本行为册邻域——有归属不越界，留档不挖 |

**矿脉枯竭判定**：板块线五环节×验证横切的仓内侧六向（mining §2）全部探测完毕；剩余开放问题全部属 Owner 门位（研究册 §6 七问）或班外车道（数据采购/两态产出），无未挖长尾仓内侧——挖矿侧枯竭，进施工前自审（各册 §4）。

## §7 与亲缘文档的分工

| 文档 | 分工 |
|------|------|
| 00_inputs/sector_problem_definition | 问题定义与全网调研（本册上游，其 §6 七问呈 Owner） |
| 本册+7 环节册 | 板块线施工前挖矿（路由/复用边界/坑/三态裁定） |
| 00_inputs/formreg_survey | 两态线（⑤ 上游供料方之一） |
| 00_inputs/2026-10-13-capital-behavior-research-dossier | 资本行为线（资金面邻域，本线仅取板块聚合腿） |
| 00_inputs/2026-10-13-sentiment-output-contract-research | 情绪输出契约 v0（⑤ 水温档语义供料） |
| docs/_working/chain_piling_campaign/ | 产业链施工战役史（④ 的图谱侧上游） |
