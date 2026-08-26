---
blueprint_id: MOD-INF-088
module_name: loki_log_pipeline
domain: D_INFRA_OPS
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
domain_id: D_INFRA_OPS
path: src/zephyr/infra_ops/loki_log_pipeline.py
granularity: file
---

# MOD-INF-088 loki_log_pipeline 蓝图（Loki日志聚合管道）

> **module_id**: MOD-INF-088 | **域**: D_INFRA_OPS | **优先级**: P2
> **来源**: B8-10662（AUD-DRAFT-001-DIGEST P2 波 P2-W01，CAND-INFRAOPS-006，A8集成架构）
> 代码：`src/zephyr/infra_ops/loki_log_pipeline.py`

## 0. 定位

Loki本地单实例对接面：JSON结构化日志（Agent决策/自治边界检查/风控否决/异常事件）推送管道（Loki push API client注入，不真发HTTP），LogQL查询构建器，热30天保留+冷数据导出Parquet策略裁决，日志脱敏钩子注入。docker-compose部署面归Owner窗口。

## 1. 规则（确定性）

- 纯内存/DI 设计：外部副作用（OS 调用/网络/进程控制）全部经注入回调，默认空操作或内存记录。
- 非法输入 Fail-Closed 抛专用 Error（占位错误码，波末统一转正）。
- 同输入必同输出（确定性）；时钟/随机源全注入。

## 2. 接口

见代码 `__all__` 与 docstring。消费方=运行时装配批（统一注入点装配）。

## 3. 测试

`tests/infra_ops/test_loki_log_pipeline.py` —— 内存替身全覆盖：正常路径 + 边界 + Fail-Closed 分支 + 确定性。
