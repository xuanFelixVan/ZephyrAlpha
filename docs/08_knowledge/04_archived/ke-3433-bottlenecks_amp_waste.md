---
module_id: KE-3305
title: 4.4 Bottlenecks &amp; waste / 瓶颈与浪费点
category: documentation
ttl: permanent
doc_type: knowledge_entry
---

# 4.4 Bottlenecks &amp; waste / 瓶颈与浪费点

4.4 Bottlenecks &amp; waste / 瓶颈与浪费点

按精益七大浪费（等待 / 返工 / 过度加工 / 传输 / 库存 / 动作 / 缺陷）识别：

| # | 类型 | 瓶颈 / 浪费 | 影响阶段 | 当前状况 | 改进方向（deferred 到具体 sprint）|
|---|------|------------|---------|---------|--------------------------------|
| **B1** | **等待**（Wait）| 市场数据上游窗口（iFinD EOD 推送延迟，下游结算数据 T+1 到齐）| ① ② ⑥ | 单 Vendor 单链路；无备份源 | 接入 AKShare / Tushare 作 fallback（OSS Catalog X3）|
| **B2** | **等待**（Wait）| 回测任务排队（单机资源、无任务调度器）| ② | `backtest TAT p95 ≤ 30min`（§5 H3 SLO）可能因串行回测超时 | H14 Observability 后加 job queue；或引入 Airflow / Prefect |
| **B3** | **等待 / 返工**（Rework）| 合规审批等待（当前合规 S5 deferred 由 you 手工兜底）| ④ ⑤ ⑦ | 手工，无规则引擎 | S5 激活后引入 policy-as-code（`16_compliance_and_legal/`）|
| **B4** | **返工**（Rework）| 因子重算（PIT 一致性失败触发全量回补）| ② | F21-F25 fitness function 会拦截；但"拦截后回补"本身是返工 | 增量回补（只回补被 corporate action 污染的 partition）|
| **B5** | **传输 / 动作**（Motion）| 人-AI 协作往返（prompt → 草稿 → 审核 → 修订）在 ⑦ 反馈回路中占 LT 60%+ | ⑦ | 每次 AI 协作 round-trip 15-60 min | VIB-1 Session 治理 + prompt 资产库（VIB-4）沉淀复用 |
| **B6** | **缺陷**（Defect）| 信号失效未及时发现（factor decay / concept drift）| ② ③ ⑥ | 归因只 T+1 看结果，drift 监控缺失 | L13 experiment_pipeline 激活后 champion-challenger 在线对照 |
