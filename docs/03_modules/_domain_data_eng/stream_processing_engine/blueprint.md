---
blueprint_id: MOD-DATENG-004
module_name: stream_processing_engine
domain: D_DATA_ENG
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
domain_id: D_DATA_ENG
path: src/zephyr/data_eng/stream_processing_engine.py
granularity: file
---

# MOD-DATENG-004 stream_processing_engine 蓝图（单机流处理引擎）

> **module_id**: MOD-DATENG-004 | **域**: D_DATA_ENG | **优先级**: P2
> **来源**: B5-07234（AUD-DRAFT-001-DIGEST P2 波 P2-W02，CAND-DATENG-007，B5）
> 代码：`src/zephyr/data_eng/stream_processing_engine.py`

## 0. 定位

轻量单机流处理：事件时间滚动/会话窗口聚合（窗口注册+触发判定）+水位线与迟到数据处理（迟到策略：丢弃/侧输出）+背压信号（队列水位阈值回调），消费注入事件流，输出实时聚合指标落sink回调。Flink/Bytewax单机化纯内存版。

## 1. 规则（确定性）

- 纯内存/DI 设计：外部副作用（OS 调用/网络/进程控制）全部经注入回调，默认空操作或内存记录。
- 非法输入 Fail-Closed 抛专用 Error（占位错误码，波末统一转正）。
- 同输入必同输出（确定性）；时钟/随机源全注入。

## 2. 接口

见代码 `__all__` 与 docstring。消费方=运行时装配批（统一注入点装配）。

## 3. 测试

`tests/data_eng/test_stream_processing_engine.py` —— 内存替身全覆盖：正常路径 + 边界 + Fail-Closed 分支 + 确定性。
