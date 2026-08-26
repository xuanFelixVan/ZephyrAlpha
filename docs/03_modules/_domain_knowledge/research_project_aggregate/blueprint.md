---
blueprint_id: MOD-KNW-011
module_name: research_project_aggregate
domain: D_KNOWLEDGE
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
domain_id: D_KNOWLEDGE
path: src/zephyr/knowledge/research_project_aggregate.py
granularity: file
---

# MOD-KNW-011 research_project_aggregate 蓝图（研究项目聚合根）

> **module_id**: MOD-KNW-011 | **域**: D_KNOWLEDGE | **优先级**: P2
> **来源**: B6-08533（AUD-DRAFT-001-DIGEST P2 波 P2-W03，CAND-KNW-014，B6）
> 代码：`src/zephyr/knowledge/research_project_aggregate.py`

## 0. 定位

ResearchProject聚合根：project_id+状态机（draft→active→review→archived四态闭合）+关联假设/证据/实验/因子产出四类子实体挂载（版本不变量）+SQLite持久化（注入连接）+与hypothesis_registry/evidence_chain/experiment_tracking联动接口。

## 1. 规则（确定性）

- 纯内存/DI 设计：外部副作用（OS 调用/网络/进程控制）全部经注入回调，默认空操作或内存记录。
- 非法输入 Fail-Closed 抛专用 Error（占位错误码，波末统一转正）。
- 同输入必同输出（确定性）；时钟/随机源全注入。

## 2. 接口

见代码 `__all__` 与 docstring。消费方=运行时装配批（统一注入点装配）。

## 3. 测试

`tests/knowledge/test_research_project_aggregate.py` —— 内存替身全覆盖：正常路径 + 边界 + Fail-Closed 分支 + 确定性。
