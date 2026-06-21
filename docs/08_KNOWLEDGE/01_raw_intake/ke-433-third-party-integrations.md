---
module_id: KE-392
status: active
title: 5. Third-party integrations / 第三方集成
category: documentation
---

# 5. Third-party integrations / 第三方集成

5. Third-party integrations / 第三方集成

| 契约 ID | 集成点 | 接入层 | 协议 | 状态 | 关键约束 |
|---------|--------|-------|------|------|---------|
| EXT-001 | **Broker API** | L06 `adapters/` | REST / FIX 4.2+ | planned | 须实现 `BrokerInterface`；发单前必过 `pre_trade/` |
| EXT-002 | **Market Data** | L00 `connectors/` | REST / WS | planned | 须经 `l00/quality/` 质量门禁 |
| EXT-003 | **LLM Providers** | L08 | REST (OpenAI-compatible) | in use | L02-L07 禁止直接调用；支持降级 |
| EXT-004 | **Feishu** | L08 `notifications/` | REST Webhook | partial | 非关键路径；失败重试 3 次 |

**候选 Broker**：SimulationAdapter (P0) → Interactive Brokers (P1) → Futu (P1) → Longport (P2)
**候选数据源**：AKShare (P0, 免费) → Tushare (P1) → Wind (P2) → 实时 Tick (P2)
**LLM 降级顺序**：Opus → Sonnet → Haiku/Kimi → Qwen-local

---
