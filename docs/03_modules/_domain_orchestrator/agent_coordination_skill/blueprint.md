---
blueprint_id: MOD-ORCH-004
module_name: agent_coordination_skill
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
path: src/zephyr/orchestrator/agent_coordination_skill.py
granularity: file
---

# MOD-ORCH-004 agent_coordination_skill 蓝图（Agent协调技能）

> **module_id**: MOD-ORCH-004 | **域**: D_ORCHESTRATOR | **优先级**: P2
> **来源**: B11-02580（AUD-DRAFT-001-DIGEST P2 波 P2-W13，CAND-ORCH-004，A7）
> 代码：`src/zephyr/orchestrator/agent_coordination_skill.py`

## 0. 定位

agent-coordination技能封装：分工协议（按Agent Card能力匹配注入卡片库）+冲突仲裁（投票/优先级两模式）+共识触发（注入consensus回调）+协调记录落审计+跨Agent调用走A2A网关语义。

## 1. 规则（确定性）

- 纯内存/DI 设计：外部副作用（OS 调用/网络/进程控制）全部经注入回调，默认空操作或内存记录。
- 非法输入 Fail-Closed 抛专用 Error（占位错误码，波末统一转正）。
- 同输入必同输出（确定性）；时钟/随机源全注入。

## 2. 接口

见代码 `__all__` 与 docstring。消费方=运行时装配批（统一注入点装配）。

## 3. 测试

`tests/orchestrator/test_agent_coordination_skill.py` —— 内存替身全覆盖：正常路径 + 边界 + Fail-Closed 分支 + 确定性。
