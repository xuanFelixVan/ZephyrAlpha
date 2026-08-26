---
blueprint_id: MOD-INF-078
module_name: ml_pipeline_process
domain: D_INFRA_RUNTIME
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
domain_id: D_INFRA_RUNTIME
path: src/zephyr/infra_runtime/ml_pipeline_process.py
granularity: file
---

# MOD-INF-078 ml_pipeline_process 蓝图（P5 ML管线进程）

> **module_id**: MOD-INF-078 | **域**: D_INFRA_RUNTIME | **优先级**: P2
> **来源**: B14-04526（AUD-DRAFT-001-DIGEST P2 波 P2-W01，CAND-H1FS-011，A9运维架构 §进程拓扑）
> 代码：`src/zephyr/infra_runtime/ml_pipeline_process.py`

## 0. 定位

ml_pipeline独立进程spec与编排：推理调度/离线训练/显存管理/模型版本四职责任务队列，核16-19+20GB预算声明，优先级40最低交易时段资源退让（trading_hours注入判定），GPU夜间时分互斥（时段表注入）。纯编排逻辑+注入执行器。

## 1. 规则（确定性）

- 纯内存/DI 设计：外部副作用（OS 调用/网络/进程控制）全部经注入回调，默认空操作或内存记录。
- 非法输入 Fail-Closed 抛专用 Error（占位错误码，波末统一转正）。
- 同输入必同输出（确定性）；时钟/随机源全注入。

## 2. 接口

见代码 `__all__` 与 docstring。消费方=运行时装配批（统一注入点装配）。

## 3. 测试

`tests/infra_runtime/test_ml_pipeline_process.py` —— 内存替身全覆盖：正常路径 + 边界 + Fail-Closed 分支 + 确定性。
