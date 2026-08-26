---
blueprint_id: MOD-INF-082
module_name: observability_triad
domain: D_INFRA_TELEMETRY
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
domain_id: D_INFRA_TELEMETRY
path: src/zephyr/infrastructure/system_telemetry/observability_triad.py
granularity: file
---

# MOD-INF-082 observability_triad 蓝图（可观测性三支柱整合）

> **module_id**: MOD-INF-082 | **域**: D_INFRA_TELEMETRY | **优先级**: P2
> **来源**: B11-02678（AUD-DRAFT-001-DIGEST P2 波 P2-W01，CAND-INFRATEL-002，A7-Agent架构）
> 代码：`src/zephyr/infrastructure/system_telemetry/observability_triad.py`

## 0. 定位

三支柱整合门面：Traces(OTel SDK+W3C TraceContext跨Agent贯通)/Metrics(Prometheus格式文本导出+Redis时序注入)/Logs(JSON结构化不可变追加)，统一TriadSink入口+热数据7天/冷数据Parquet归档指针策略+审计链对接回调。不重启OTel，复用tracing.py。

## 1. 规则（确定性）

- 纯内存/DI 设计：外部副作用（OS 调用/网络/进程控制）全部经注入回调，默认空操作或内存记录。
- 非法输入 Fail-Closed 抛专用 Error（占位错误码，波末统一转正）。
- 同输入必同输出（确定性）；时钟/随机源全注入。

## 2. 接口

见代码 `__all__` 与 docstring。消费方=运行时装配批（统一注入点装配）。

## 3. 测试

`tests/infrastructure/test_observability_triad.py` —— 内存替身全覆盖：正常路径 + 边界 + Fail-Closed 分支 + 确定性。
