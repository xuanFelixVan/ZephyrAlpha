---
module_id: KE-155---togaf-001
status: active
title: 2. TOGAF four layers / TOGAF 四层结构
category: documentation
ttl: permanent
---

# 2. TOGAF four layers / TOGAF 四层结构

2. TOGAF four layers / TOGAF 四层结构

```
┌────────────────────────────────────────────────────────────┐
│  01. Business Architecture (BA) / 业务架构                  │
│      Who we serve, what we do, core processes, NFR         │
│      为谁服务、做什么业务、核心流程、非功能需求               │
└────────────────────────────────────────────────────────────┘
                        ↓ drives / 驱动
┌────────────────────────────────────────────────────────────┐
│  02. Information Architecture (IA) / 信息架构               │
│      What information assets exist, how organized          │
│      有哪些信息资产、如何组织、文档生命周期                   │
└────────────────────────────────────────────────────────────┘
                        ↓ drives / 驱动
┌────────────────────────────────────────────────────────────┐
│  03. Application Architecture (AA) / 应用架构               │
│      What modules/services exist, how they interact        │
│      有哪些应用/模块/服务、如何交互                          │
└────────────────────────────────────────────────────────────┘
                        ↓ drives / 驱动
┌────────────────────────────────────────────────────────────┐
│  04. Technology Architecture (TA) / 技术架构                │
│      What technology stack underpins everything            │
│      用什么技术栈支撑上述一切                                │
└────────────────────────────────────────────────────────────┘
```

**Driving relationships / 驱动关系**：

- BA drives IA: business capabilities determine what data/documents/knowledge to accumulate.
- IA drives AA: data distribution determines application boundaries.
- AA drives TA: application characteristics (batch/realtime/AI) determine technology choices.
- Reverse constraint: TA cost limits constrain AA → IA → BA ambition.

- BA 驱动 IA：业务能力决定要沉淀什么数据/文档/知识。
- IA 驱动 AA：数据分布决定应用边界。
- AA 驱动 TA：应用特性（批量/实时/AI）决定技术选型。
- 反向约束：TA 的成本上限反向约束 AA → IA → BA 的野心。

> **📊 TOGAF 架构层次图**：见 [`diagrams/togaf_layer_stack.mmd`](diagrams/togaf_layer_stack.mmd) — TOGAF 四层（Business→Information→Application→Technology）映射

---
