---
module_id: KE-185
title: 2.2 ZephyrAlpha 各集成风格采用情况
category: documentation
ttl: permanent
doc_type: knowledge_entry
---

# 2.2 ZephyrAlpha 各集成风格采用情况

2.2 ZephyrAlpha 各集成风格采用情况

| 风格 | ZephyrAlpha 采用情况 | 落地位置 |
|------|---------------------|---------|
| Batch | ✅ 主力风格（当前阶段） | 每日 EOD 数据拉取；因子值计算批次；日报生成 |
| Streaming | 🔶 部分启用（dev 环境） | LLM Provider WebSocket；行情 WebSocket（EI-002，planned） |
| Request-Reply | ✅ 活跃使用 | LLM API（EI-003）；Feishu API（EI-004）；Broker REST（EI-001，planned）|
| Event-Driven | 🔶 内部约定，未用 MQ | 层间通过 Python 函数调用 + `shared/contracts/` 传递事件对象（轻量事件驱动）|
| File-based | ✅ 主力存储中间层 | Parquet / HDF5 存历史行情；CSV 存回测结果 |
| Shared-DB | ⚠️ 极限约束使用 | 本地 SQLite（L07 结算分析）；禁止跨层直接写 |

**当前阶段策略**：以 **Batch + File-based** 为主体（适合单人开发、量化研究阶段），Request-Reply 用于外部服务，Event-Driven 以**轻量内部协议**（Python dataclass + 函数调用）代替消息队列（MQ）——MQ 引入时机见 §6。

---
