---
ttl: task_bound
completes_when: 战役收尾（99_final_delivery 落账）后随役归档 archive/2026-10
---

# [BLUEPRINT] | docs/_working/chief_fullchain_20261006/env_mining/env_07_source_lines.md |
<!-- [MODULE]  -->
<!-- [STABILITY] evolving -->
<!-- [SAFETY] L -->

# ENV-07 源线与知识供给 挖矿作业簿（B1 批次，2026-10-06）

## §0 环节档案

- **真源锚**：config/trading_decision_map.yaml nodes[layer=L9]（182 节点中 44 个，entry_flow 知识供给层）；骨架=01_skeleton_environments.md §2-丙
- **职责一句话**：44 条异构"源线→图谱→状态快照→决策假设→验证→治理"知识供给，经 AGG 汇聚喂 L0-L4 全部决策层（TDM 里唯一"横向供全图"的层）
- **节点代表（44，代表非穷举）**：A01 日线/分钟行情(critical)｜A02 Tick分笔(critical)｜A03 板块/概念指数(critical)｜A06 资金流(critical)｜A09 财经快讯情绪(critical)｜A04 估值｜A08 BDI｜A15 加密费率｜B01 卫星影像｜B06 社媒舆情｜B07 雪球股吧｜C01 门店客流｜G1 Zephyr产业链｜G3 实体股权穿透｜V1/V3 状态快照·大盘/板块｜V2 情绪快照｜AGG 知识供给汇聚｜D1 因子组合挖掘｜E1 一问一考考试链｜Z2 净零对账
- **图面状态**：confidence untested=37 / proposed=7；activation premarket22/intraday7/continuous8/postmarket7；red_reason：by_ref_design=16（引用式不落原始数据）/ not_built=15 / structural=5 / pending_gate=1 / 空=7；materiality critical=5（A01/A02/A03/A06/A09）

## §1 六向台账

| 向 | 内部反查发现（带路径证据） | 外部 | 判定 |
|---|---|---|---|
| ①上游 | 图内 IN 仅 3 边且全是决策层回喂：L1-S0→V1、L1-AGG→V2、L2-04→V3（config/trading_decision_map.yaml edges）；物质上游=ENV-01 采集 23 家源承接（16 条 A/B/C 系 by_ref_design=引用采集面不重复落库） | 业界=alpha 挖掘层独立于执行决策层（多经理平台 research pod 形态），本层 G/V/D/E 分族同构 | signal |
| ②下游 | 图内 OUT 19 边：V1→L0-01 计划生成+X-S1、V2→L2-05 水温+X-S1-04、V3→L2-01、G1→L2-06/L3-01、G3→L3-12-2 龙虎榜、G4→L1-AGG、G5→L1-S0。grep 消费方：src/zephyr/plan_engine/ 全家七件（daily_plan/close_verifier/intraday_l1_tracker/next_day_forecaster/scenario_classifier/judgment_settler 均引 judgment_ledger）、scripts/backtest/sim_daily_runner.py、tests/pf_alloc/test_l9_readiness_gate.py（AGG 出口有 gate 面） | — | signal |
| ③算法机制 | AGG=l9 就绪度汇聚（src/zephyr/data/l9_readiness_aggregator.py）；V1/V3=判断台账假设→结算闭环（judgment_ledger.py+judgment_settler）；D1=MCTS 表达式挖掘（scripts/backtest/mcts_expression_search.py）；E1=一问一考考试链（src/zephyr/trading/validation/runner.py）；Z2=链引用对账（scripts/governance/reconcile_chain_refs.py）；G3=股权穿透（scripts/entity_graph/equity_penetration.py） | 知识供给就绪度门控（readiness gate）属仓内合规设计，外部无同名物 | signal |
| ④后端代码 | 44 节点仅 6 个有 module_ref 且全部在盘（上列五件+judgment_ledger）；tests/：tests/data/data/test_l9_readiness_aggregator.py、tests/pf_alloc/test_l9_readiness_gate.py、tests/plan_engine/test_judgment_ledger.py、tests/infra/frontend/test_chainmap_equity_graph.py；scripts/ch/apply_l9_readiness_ddl.py（CH DDL 在册）。V2 情绪快照/G2/G4/G5 图谱/D2/E2/Z1 无 module_ref（已查无） | — | 半实现 |
| ⑤前端呈现（只登记） | src/zephyr/frontend/dashboard/web/features/tdm.js（TDM 图面）；chainmap 股权图谱前端（test_chainmap_equity_graph.py 佐证 renderer 链） | — | signal（登记） |
| ⑥数据字段 | data_refs=DS-001/002/016/057/059/104/107/117/119/123/141/208/230/231/232 等 DS 码族（16 表经 DSC 承接，config/data_supply_chain_map.yaml:316 "TDM:DS-150等16表/约64点"）；L9 专属产物=l9_readiness 就绪度表（apply_l9_readiness_ddl.py 建面） | — | signal |

## §2 挖干自评

- **三扫收敛?** 收敛。图字段轮→代码轮→消费方轮，第三轮新增仅 pf_alloc readiness gate 消费一处，边际归零。
- **未挖长尾**：(a) B01-B10/C01-C03 共 13 条另类/实时源线逐源可得性与成本档案（💰 门位项）；(b) G2 事实层/G4 概念题材/G5 投入产出三图谱节点的既有资产（industry_chain_alpha、同花顺资料）与新图语义的对位；(c) D2 考试方案登记面。
- **🌑不可得**：①44 节点中 38 个语义节点无实现且无失败痕迹（not_built 是"未做"非"做败"）；②by_ref_design 16 条的引用完整性无运行时校验证据（AGG 未跑生产打卡——读数待施工批）。

## §3 挖后自审闸三态裁定

**挂起排期（整层）——图语义→代码施工令缺口**

- 理由：44 节点仅 6 件有码（AGG/V1/V3/D1/E1/Z2 件在盘），其余 38 节点停在语义层；全层 confidence 无一 verified，AGG 出口虽有 gate 测试但无生产运行证据。这不是"实现坏了"而是"图先于码"——按本批纪律=挂起排期，不无码硬施工。
- 已实现 6 件维持现状不扩面（内收）。施工令候选排序（解锁后）：V2 情绪快照（下游 L2-05 水温/X-S1-04 退潮信号在等）> G4 概念题材图谱（下游 L1-AGG）> D2/E2 考试闭环收口。
- 解锁条件：Owner 对 L9 知识供给层立项发施工令 + ENV-01 采集面新鲜度打卡可查（a 项长尾降为按需）。

## §4 挖矿日志

| 轮 | 矿脉 | 判定 | 关键产出 |
|---|---|---|---|
| 1 | 图字段轮：44 节点 conf/act/red_reason/materiality 全分布切片（yaml 解析，未整读贴出） | signal | by_ref_design16/not_built15/structural5/pending1 分型；critical5 名单 |
| 2 | 代码轮：6 个 module_ref 存在性核验 + l9/judgment/mcts/runner 真身读 | signal | 6/6 在盘零失踪；V2/G2/G4/G5/D2/E2/Z1 已查无实现 |
| 3 | 消费方轮：judgment_ledger/l9_readiness 全 src+scripts+tests 反查 | signal | plan_engine 七件消费簇、sim_daily_runner、pf_alloc gate 测试面 |
