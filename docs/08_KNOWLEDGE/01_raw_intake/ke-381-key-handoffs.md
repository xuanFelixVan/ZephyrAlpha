---
module_id: KE-345
title: 4.3 Key handoffs / 关键交接点
category: documentation
---

# 4.3 Key handoffs / 关键交接点

4.3 Key handoffs / 关键交接点

Handoff 是 VSM 中最易产生**信息损失 + 责任真空 + 数据污染**的点，必须显式标注契约。

| # | Handoff | 上游 → 下游 | 交接物 | 风险 | 治理手段 |
|---|---------|------------|-------|------|---------|
| **HO-1** | **Vendor → Data Lake**（市场数据入仓）| S10 → S6 | 原始 tick / bar / reference data | 字段漂移、survivorship、迟到数据覆盖历史 | ACL（`03-AA H8`）+ PIT 三字段（`05-DA §4`）+ immutable append |
| **HO-2** | **Research → Factor Library**（研究→生产）| S2 → (S2+S6) | 因子代码 + metadata + 断言 | 研究环境灰带代码进生产、look-ahead bias | H8 ACL 隔离 + F21-F25 fitness functions + `OQ-075` 三断言 |
| **HO-3** | **Signal → Pre-trade Risk**（信号→风控）| S2 → S4 | signal payload + metadata | 信号绕过风控、限额不同步 | 强制性 Pre-trade gate（A09）+ Idempotency Key（`03-AA H10`）|
| **HO-4** | **Portfolio → Broker**（组合→券商）| S3 → S10 | 委托单 + client_order_id | **订单重发重复**（量化红线）| H10 幂等设计 + broker ACK 回执持久化 |
| **HO-5** | **Fill → Attribution / Feedback**（成交→归因→研究）| (S3+S6) → S2 → S1 | 成交记录 + PnL 分解 + 结论 | 反馈断链（归因洞察没回到因子库）| Decision log 七维度（`OQ-063`）+ `08_knowledge/` 沉淀 |
