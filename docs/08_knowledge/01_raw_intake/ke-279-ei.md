---
module_id: KE-257---------ei-003
title: 3.2 外部集成点清单（EI 系列）
category: documentation
ttl: permanent
doc_type: knowledge_entry
---

# 3.2 外部集成点清单（EI 系列）

3.2 外部集成点清单（EI 系列）

| ID | Integration / 集成点 | Type / 类型 | Direction / 方向 | Protocol / 协议 | Status / 状态 | ACL 落盘位置 | Notes / 说明 |
|----|---------------------|------------|-----------------|----------------|--------------|-------------|-------------|
| EI-001 | Broker API / 券商 API | Trade execution / 交易执行 | Bidirectional / 双向 | REST / FIX | planned | `l06_trade_execution/adapters/` | 接入真实资金时激活 |
| EI-002 | Market data provider / 行情数据源 | Historical + realtime market data / 历史+实时行情 | Inbound / 入站 | REST / WebSocket | planned | `l00_data_source/connectors/` | 首次数据接入时 |
| EI-003 | LLM providers / LLM 服务商 | AI inference / AI 推理 | Outbound / 出站 | REST (OpenAI-compatible) | in use (dev) | `l08_human_ai_interface/` | Cursor/Trae 已接入；生产接入待 OQ-011 |
| EI-004 | Feishu / 飞书 | Notification & report distribution / 通知与报告分发 | Outbound / 出站 | REST (Feishu API) | partial | `l08_human_ai_interface/notifications/` | 手动推送已有；自动分发 planned |
| EI-005 | Alternative data providers / 另类数据源 | Sentiment, news, events / 舆情、新闻、事件 | Inbound / 入站 | REST / file | planned | `l00_data_source/connectors/` | 因子研究阶段激活 |
