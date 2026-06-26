---
module_id: KE-293---component-dia-001
status: active
title: 3.5 C4 Level 3 — Component diagrams for critical layers / 关键层组件图
category: documentation
ttl: permanent
doc_type: knowledge_entry
---

# 3.5 C4 Level 3 — Component diagrams for critical layers / 关键层组件图

3.5 C4 Level 3 — Component diagrams for critical layers / 关键层组件图

> C4-L3 展开**三个关键层**的内部组件结构——选择依据 = 业务风险最高（L00 数据源头 + L06 资金执行）或架构复杂度最高（L11 ML 平台组件交错）。

| 图 ID | 目标层 | 文件 | 阅读重点 |
|------|-------|------|---------|
| **C4-L3 / L00** | L00 Data Source | `diagrams/c4_l3_l00_data_source.mmd` | Vendor Registry + ACL 三段 + 多 Vendor 故障转移 |
| **C4-L3 / L11-ML** | L11 ML Platform | `diagrams/c4_l3_l11_ml_platform.mmd` | Feature Store + PIT + Training → Registry → Inference |
| **C4-L3 / L06** | L06 Trade Execution | `diagrams/c4_l3_l06_trade_execution.mmd` | OMS + Idempotency Guard + SOR + Broker Adapters |

**推荐阅读路径**：
- **数据入口视角**：C4-L1 → C4-L2 → C4-L3/L00 → `src-domain/ocp-extension-points.md`
- **资金安全视角**：C4-L2 → C4-L3/L06 → §8 幂等设计 → `src-domain/idempotency-design.md`
- **ML 生命周期视角**：C4-L2 → C4-L3/L11-ML → OQ-063 AI Operator 激活路线

---
