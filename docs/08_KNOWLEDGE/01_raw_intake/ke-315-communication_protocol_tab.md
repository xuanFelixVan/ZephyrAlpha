---
module_id: KE-290
title: 3.4 Communication protocol table / 通信协议表
category: documentation
ttl: permanent
---

# 3.4 Communication protocol table / 通信协议表

3.4 Communication protocol table / 通信协议表

| From → To / 从→到 | Protocol / 协议 | Sync/Async | Notes / 说明 |
|------------------|----------------|-----------|-------------|
| Data Pipeline → Storage | Direct write / 直接写入 | Sync | 行情落库 |
| Data Pipeline → Factor Engine | In-process call / 进程内调用 | Sync | 当前单进程；未来可拆分为消息队列 |
| Factor Engine → Risk Engine | In-process call | Sync | 风控前置 |
| Factor Engine → Portfolio Engine | In-process call | Sync | 因子信号驱动组合构建 |
| Risk Engine → Portfolio Engine | In-process call | Sync | 限额约束注入 |
| Portfolio Engine → Execution Engine | In-process call | Sync | 目标权重→委托指令 |
| Execution Engine → Broker API | REST / FIX | Sync | 委托发送 |
| Broker API → Execution Engine | Callback / Push | Async | 成交回报 |
| AI Agent Ops → LLM Providers | REST | Async | AI 推理调用 |
| Market Data → Data Pipeline | REST / WebSocket | Pull + Push | 历史拉取 + 实时推送 |
