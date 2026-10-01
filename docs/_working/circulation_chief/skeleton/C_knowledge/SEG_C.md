---
ttl: task_bound
title: C 段·知识供给线 TDM L9 8 环节六向挖矿档（S3 W3-1）
session: st-ffchief-20261001
date: 2026-10-01
status: mined
creation_token: seg-c-knowledge-l9-w31-20261001
---

# SEG_C · 知识供给线（TDM L9，C-01..C-08，8 环节）代码级核验

> 基线深核：TDM-E-L9* 节点 yaml.safe_load 实跑 **44 节点，module_ref null=37，非 null=7**：G3/V1/V3/AGG/D1/E1/Z2（与 skeleton C 段行完全吻合；skeleton"44"未写、null=37 吻合）。

## 六向台账

| 环节 | 上游 | 下游 | 生产者代码(路径:行) | 消费者代码 | 自动化态 | 运行态 | 三态复核 |
|------|------|------|---------------------|------------|----------|--------|----------|
| C-01(F30) L9 源线·行情基本面族 | A 段 | F34 | TDM-E-L9-A01..A16 **16/16 全 null**；生产面仅 generators 引用：scripts/governance/d5_architecture/generators/generate_trading_day_cycle_map.py:957-964 | l9_readiness_aggregator.py（**就绪度读数，非内容消费**：头注"源线数据已在 CH/PG，禁在汇聚点采集"） | 无内容消费（登记态） | 红 | **维持盲区**（详 F30.md） |
| C-02(F31) L9 源线·另类数据族 | 外部 | F34/F96 | TDM-E-L9-B01..B10/C01..C03 null；但 **src/zephyr/alt_data/ 29 py**（skeleton 写 28=漂移） | **src/zephyr/data/scheduler.py:1622**（AltRegimeSignalProvider）+tasks.yaml:2761"C-1 消费端首批"+:3451 cohort_daily_writer+:3467 emotion_index_builder；api_server 消费 | **部分定时已接**（tasks.yaml 消费端首批在册） | 黄（TDM 登记面 null vs 代码面已接调度=两层面背离） | **盲区→存疑（变迁）**（详 F31.md） |
| C-03(F32) L9 图谱谱系 | F12 | F34/F18 | TDM-E-L9-G3=scripts/entity_graph/equity_penetration.py（MATURITY=production）；G1/G2/G4/G5 null | "信号侧(牛散跨票/同实控人联动/质押链传导)"=设计 §5 声明态；reconcile_chain_refs 图谱判据同源 | 机生+手动 | 黄（G3 production、余 4 谱系登记态） | **维持存疑** |
| C-04(F33) L9 状态变量快照 | F38 | F34 | TDM-E-L9-V1/V3=src/zephyr/plan_engine/judgment_ledger.py；**V2 null**（aggregator INVARIANTS 自证"V2 定案挂起"） | plan_engine 族 5 件：close_verifier/daily_plan/intraday_l1_tracker/judgment_settler+l9_readiness_aggregator | 事件（盘中） | 黄（V1/V3 有真实消费链；V2 挂起留因） | **维持存疑** |
| C-05(F34) L9 知识供给汇聚 | F30-F33 | F35/D 段 | src/zephyr/data/l9_readiness_aggregator.py（MOD-DATA-L9AGG，"TDM-E-L9-AGG 的实件"）+scripts/ch/apply_l9_readiness_ddl.py | **scheduler.py:35**"F34 消费接线（2026-09-29）⑤ L9 知识供给就绪度闸"+**src/zephyr/pf_alloc/allocation_inputs.py:798-816**（L9_READINESS 表消费+DISABLE_FLAG）+pipeline_events task_completed 唤醒+晨报读表 | 事件（daily_kline SUCCESS 唤醒，60min DB 侧节流） | 绿（**翻绿深核通过**：生产+DDL+调度闸+分配链消费四段全闭） | **维持挖干(翻绿，深核确认)** |
| C-06(F35) L9 决策假设与一问一考 | F34 | F23/回灌 | TDM-E-L9-D1=scripts/backtest/mcts_expression_search.py；E1=src/zephyr/trading/validation/runner.py；**D2/E2 null** | mcts→backtest/core/closed_book_gate.py+validation 族（ablation/decay_watch/__init__） | 事件 | 黄（D1/E1 有消费链，D2/E2 登记态） | **维持存疑** |
| C-07(F36) L9 治理横切 | 全 L9 | 治理层 | TDM-E-L9-Z2=scripts/governance/reconcile_chain_refs.py；**Z1 null** | generate_chain_registry.py+governance/meta_question/wo007/build_ckg_prior_tier.py+l9_readiness_aggregator（"图谱侧判据同源禁另立第三套"） | 事件 | 黄（Z2 三消费方在，Z1 登记态） | **维持存疑** |
| C-08(F131) nlp 文本情报线 | C 段 | F96/F16 | src/zephyr/nlp/ **7 py** | **4 外部消费方**：data/news_taxonomy.py、intelligence/news_llm_scorer.py、intelligence/news_sentiment_analyzer.py、ml_train/implementations/sentiment_sft_trainer.py | 静态库+被动调用 | 黄 | **盲区→存疑（变迁）**（详 F131.md） |

## 本段三态变迁

| 环节 | 原判 | 复核判 | 关键证据 |
|------|------|--------|----------|
| C-02(F31) | 盲区（无消费登记态） | **存疑** | alt_data 已接 tasks.yaml C-1 消费端首批+scheduler.py:1622；TDM null=登记面欠账非无消费 |
| C-08(F131) | 盲区 | **存疑** | 7 py+4 外部消费方 |
| C-05(F34) | 挖干(翻绿待深核) | 挖干（深核通过，待深核解除） | scheduler.py:35+allocation_inputs.py:798 四段闭环 |
