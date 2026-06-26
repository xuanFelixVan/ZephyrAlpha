---
module_id: KE-3464
title: 5.1 当前 ACL 落盘位置
category: documentation
ttl: permanent
---

# 5.1 当前 ACL 落盘位置

5.1 当前 ACL 落盘位置

| ACL 位置 | 隔离的外部系统 | 规范输出 |
|---------|--------------|---------|
| `data/connectors/` | 行情 Vendor（AKShare / Tushare / Wind / Bloomberg）| `NormalizedMarketData` canonical schema |
| `ex_core/adapters/` | 券商 API（Broker REST / FIX）| 内部 `Order` / `Fill` 协议 |
| `frontend/` | LLM Provider（OpenAI-compatible REST）| 内部 LLM 调用抽象 |

详细设计见 `application_architecture.md §4.1 L00 connectors/` — 已确立 ACL 的三项职责（格式隔离 / Connector 协议统一 / 格式转换在边界处）。
