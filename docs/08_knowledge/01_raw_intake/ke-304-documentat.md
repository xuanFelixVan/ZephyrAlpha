---
module_id: KE-282
status: active
title: 3.3 内部层间数据流（事件驱动轨迹）
category: documentation
ttl: permanent
doc_type: knowledge_entry
---

# 3.3 内部层间数据流（事件驱动轨迹）

3.3 内部层间数据流（事件驱动轨迹）

量化系统的核心事件流，标注 P0 跨层数据契约 ID（CTR-001~CTR-006）作为架构承重墙：

```
MarketDataTick (raw)
    → [L00 connectors/ ACL 规范化]
    → CTR-001: NormalizedMarketData 🔒
    → [L02 Alpha Factor 计算]
    → CTR-002: FactorSignal 🔒
    → [L04 Risk Management 检查]  [L05 Portfolio Construction 优化]
    → CTR-003: RiskLimits 🔒 + CTR-004: Order 🔓
    → [L06 Trade Execution]
    → CTR-005: Fill 🔒 + CTR-006: PositionSnapshot 🔒
    → [L07 Post-Trade Analytics]
    → PnL Report / Risk Metrics
    → [L12 System Telemetry 监控]
```

**图例**：🔒 = frozen（不可变契约） | 🔓 = mutable（可变契约，含状态机）

所有层间数据对象均在 `src/zephyr/shared/contracts/` 定义（frozen dataclass），见 `architecture_model/contracts/cross_layer_contracts.yaml` 完整规格。

> **📊 跨层契约可视化图表**：
> - [`diagrams/data_flow.mmd`](diagrams/data_flow.mmd) — 核心数据流全景图（14 层体系 + CTR 标注）
> - [`diagrams/integration_topology.mmd`](diagrams/integration_topology.mmd) — 集成拓扑图（含 CTR 标注）
> - [`diagrams/c4_l2_containers.mmd`](diagrams/c4_l2_containers.mmd) — C4-L2 容器图（含 CTR 标注）

> **📊 核心业务时序图**：
> - [`diagrams/seq_order_submit.mmd`](diagrams/seq_order_submit.mmd) — 订单提交端到端时序（含幂等+ACL+熔断）
> - [`diagrams/seq_fill_received.mmd`](diagrams/seq_fill_received.mmd) — 成交回报处理时序
> - [`diagrams/seq_rebalance.mmd`](diagrams/seq_rebalance.mmd) — 组合再平衡时序
> - [`diagrams/seq_risk_trigger.mmd`](diagrams/seq_risk_trigger.mmd) — 风控触发与止损时序

---
