---
module_id: KE-182
title: 2.2 External system list / 外部系统清单
category: documentation
---

# 2.2 External system list / 外部系统清单

2.2 External system list / 外部系统清单

| External System / 外部系统 | Direction / 方向 | Protocol / 协议 | Purpose / 用途 |
|--------------------------|----------------|----------------|---------------|
| **Broker API** 券商 API | Bidirectional / 双向 | REST / FIX | 发送交易委托；接收成交回报与持仓 |
| **Market Data Provider** 行情数据源 | Inbound / 入向 | REST / WebSocket | 提供历史与实时行情数据 |
| **LLM Providers** LLM 服务商 | Outbound / 出向 | REST | AI 推理调用（OpenAI / Anthropic 等） |
| **Feishu** 飞书 | Outbound / 出向 | REST (Webhook) | 通知与报告分发 |
