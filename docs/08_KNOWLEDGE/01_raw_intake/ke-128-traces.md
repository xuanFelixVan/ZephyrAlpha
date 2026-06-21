---
module_id: KE-115
status: active
title: 10.3 Traces / 分布式追踪
category: documentation
---

# 10.3 Traces / 分布式追踪

10.3 Traces / 分布式追踪

端到端链路：L02 → L03 → L04 → L05 → L06 → [Broker API] → L07

**采样策略**：Dev/UAT 100% | Staging 20% + 错误 100% | Prod 尾部采样 10% + 错误/慢请求 100%
