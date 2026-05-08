---
module_id: KE-documentat-7_3_external_interface_contrac-000
title: 7.3 External interface contracts / 外部接口契约
category: documentation
---

# 7.3 External interface contracts / 外部接口契约

7.3 External interface contracts / 外部接口契约

| 契约 ID | 外部系统 | 方向 | 协议 | 关键约束 |
|---------|---------|------|------|---------|
| EXT-001 | Broker API | 双向 | REST/FIX | 发单前必须通过 `l06/pre_trade/` 风控 |
| EXT-002 | Market Data | 入站 | REST/WS | 入站数据必须经 `l00/quality/` 质量门禁 |
| EXT-003 | LLM Providers | 出站 | REST | 支持降级；L02-L07 不允许直接调用，必须经 L08 |
| EXT-004 | Feishu | 出站 | REST Webhook | 非关键路径；发送失败不影响主流程 |
