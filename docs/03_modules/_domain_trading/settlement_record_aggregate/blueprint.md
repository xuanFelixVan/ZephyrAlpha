---
blueprint_id: MOD-TRADING-010
module_name: settlement_record_aggregate
domain: D_TRADING
doc_type: blueprint
ttl: permanent
design_maturity: design
stability: evolving
safety_level: M
ai_autonomy: ai_modifiable
version: "0.1.0"
created: 2026-08-25
last_updated: 2026-08-25
owner: ZephyrAlpha-Owner
priority: P1
blueprint_level: module
domain_id: D_TRADING
path: src/zephyr/trading/settlement_record_aggregate.py
granularity: file
---

# MOD-TRADING-010 settlement_record_aggregate 蓝图（核心聚合 AGG-TRD-02 SettlementRecord）

> **module_id**: MOD-TRADING-010 | **域**: D_TRADING | **优先级**: P1
> **来源**: B6-08088（AUD-DRAFT-001-DIGEST P1 波 W-P1-23，CAND-TRD-010，D-TRADING §0）
> 代码：`src/zephyr/trading/settlement_record_aggregate.py`

## 0. 定位

交易运营域结算记录核心聚合（DDD 聚合根）。TSV 现状注记
"部分:src/zephyr/trading/settlement_reconciliation.py"——对账逻辑已有，
SettlementRecord 聚合与差异事件未成形。

| 既有件 | module_id | 职责 | 与本模块边界 |
|---|---|---|---|
| settlement_reconciliation | MOD-TRADING-003 | 纯对账引擎：逐笔比对+SettlementDrift+ReconciliationResult+告警回调（无生命周期、无工单） | 本件消费其差异结果建聚合，不重复比对逻辑 |
| broker_settlement_adapter | MOD-TRADING-005 | 券商结算单适配（记录源） | 数据流上游 |
| recon_runner | MOD-TRADING-007 | 回测 vs 模拟盘三层对账编排（写库） | 场景互补，非结算记录聚合 |

不做什么：不重建对账比对（委托 MOD-TRADING-003）、不查券商（委托
MOD-TRADING-005）、不写库（工单事件经 event_sink 发布，落库留装配批）。

## 1. 规则（确定性，Fail-Closed）

- **聚合根 SettlementRecord**：settlement_id 唯一 + idempotency_key 幂等
  （同键重复注册返回既有聚合）。
- **结算状态机**：PENDING→MATCHED / DISCREPANT→RESOLVED→CONFIRMED；
  非法转换 Fail-Closed 抛 InvalidSettlementTransitionError。
- **差异分类**：将对账差异归三档——PRICE_QTY_MISMATCH（价格/数量类）、
  MISSING_RECORD（缺失类）、FEE_REFERENCE（费用参考类，仅参考不升级工单）。
- **差异处理工单事件**：DISCREPANT 迁移产出 DiscrepancyTicket（ticket_id/
  category/drift_ids/status=OPEN），经注入式 event_sink 发布；
  工单关闭（RESOLVED）同步产出事件；event_sink 缺失仅落聚合内日志。
