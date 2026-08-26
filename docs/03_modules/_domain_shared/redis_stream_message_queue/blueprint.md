---
blueprint_id: MOD-SHARED-004
module_name: redis_stream_message_queue
domain: D_SHARED
doc_type: blueprint
ttl: permanent
design_maturity: design
stability: evolving
safety_level: M
ai_autonomy: human_gated
version: "0.1.0"
created: 2026-08-26
last_updated: 2026-08-26
owner: ZephyrAlpha-Owner
priority: P2
blueprint_level: module
domain_id: D_SHARED
path: src/zephyr/shared/redis_stream_message_queue.py
granularity: file
---

# MOD-SHARED-004 redis_stream_message_queue 蓝图（Redis Streams可靠消息队列）

> **module_id**: MOD-SHARED-004 | **域**: D_SHARED | **优先级**: P2
> **来源**: B1-00341（AUD-DRAFT-001-DIGEST P2 波 P2-W02，CAND-SHARED-002，C2 D-INT-12）
> 代码：`src/zephyr/shared/redis_stream_message_queue.py`

## 0. 定位

Redis Streams承载事件总线语义：stream+consumer group+ACK重试（pending超期重投）+DLQ对接（注入dlq_sink回调），保留进程内快路径（inproc与stream双通道路由表），严禁Kafka。Redis客户端全注入（测试用内存fake stream实现），不连真Redis。

## 1. 规则（确定性）

- 纯内存/DI 设计：外部副作用（OS 调用/网络/进程控制）全部经注入回调，默认空操作或内存记录。
- 非法输入 Fail-Closed 抛专用 Error（占位错误码，波末统一转正）。
- 同输入必同输出（确定性）；时钟/随机源全注入。

## 2. 接口

见代码 `__all__` 与 docstring。消费方=运行时装配批（统一注入点装配）。

## 3. 测试

`tests/shared/test_redis_stream_message_queue.py` —— 内存替身全覆盖：正常路径 + 边界 + Fail-Closed 分支 + 确定性。
