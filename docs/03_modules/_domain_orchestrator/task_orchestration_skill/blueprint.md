---
blueprint_id: MOD-ORCH-003
module_name: task_orchestration_skill
domain: D_ORCHESTRATOR
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
domain_id: D_ORCHESTRATOR
path: src/zephyr/orchestrator/task_orchestration_skill.py
granularity: file
---

# MOD-ORCH-003 task_orchestration_skill 蓝图（任务编排技能）

> **module_id**: MOD-ORCH-003 | **域**: D_ORCHESTRATOR | **优先级**: P2
> **来源**: B11-02579（AUD-DRAFT-001-DIGEST P2 波 P2-W13，CAND-ORCH-003，A7）
> 代码：`src/zephyr/orchestrator/task_orchestration_skill.py`

## 0. 定位

task-orchestration技能封装：任务分解→DAG生成（复用work_dag语义）→波次调度→失败重试/DLQ+技能契约（输入输出Schema登记）+产出编排计划需human_gated确认。

## 1. 规则（确定性）

- 纯内存/DI 设计：外部副作用（OS 调用/网络/进程控制）全部经注入回调，默认空操作或内存记录。
- 非法输入 Fail-Closed 抛专用 Error（占位错误码，波末统一转正）。
- 同输入必同输出（确定性）；时钟/随机源全注入。

## 2. 接口

见代码 `__all__` 与 docstring。消费方=运行时装配批（统一注入点装配）。

## 3. 测试

`tests/orchestrator/test_task_orchestration_skill.py` —— 内存替身全覆盖：正常路径 + 边界 + Fail-Closed 分支 + 确定性。
