---
module_id: KE-documentat-8_4-001
title: 8.4 幂等设计 — 资金安全一级红线
category: documentation
---

# 8.4 幂等设计 — 资金安全一级红线

8.4 幂等设计 — 资金安全一级红线

**目标语义**：At-Least-Once + Idempotent Guard → **Effectively Exactly-Once**（业界标准：Stripe / AWS DynamoDB / 支付宝同款）。

**Idempotency Key 生成**：
```
idempotency_key = "ORD-" + SHA256(order_id + broker + price + quantity + timestamp[:19])
```
保证同一订单内容重发产生相同的 key。

**实现架构**：
```
订单请求 → Idempotency Guard (SETNX key + TTL 24h)
    ├── key 不存在 → 正常处理 + 写入结果 → 返回 success
    └── key 已存在 → 返回初始结果（幂等返回）→ 写入幂等命中 event
```

**关键约束**：
- TTL 24 小时（覆盖券商对账周期 + broker timeout）
- Key collision 检测：不同订单内容产生相同 key → 立即告警（P0）
- L06 所有 Retry 必须经过 Idempotency Guard
- Idempotency Guard 失败 → **Order NOT submitted**（宁可延迟不可重复）

> **📊 异常处理时序图**：见 [`seq-exception-handling.mmd`](./diagrams/seq-exception-handling.mmd) — 跨层异常传播与降级处理完整时序

---
