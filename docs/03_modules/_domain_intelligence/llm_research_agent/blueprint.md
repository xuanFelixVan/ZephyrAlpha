---
blueprint_id: MOD-INT-RESEARCH-AGENT
module_name: llm_research_agent
domain: D_INTELLIGENCE
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
domain_id: D_INTELLIGENCE
path: src/zephyr/intelligence/llm_research_agent.py
granularity: file
---

# MOD-INT-RESEARCH-AGENT llm_research_agent 蓝图（LLM研究助手）

> **module_id**: MOD-INT-RESEARCH-AGENT | **域**: D_INTELLIGENCE | **优先级**: P2
> **来源**: B6-08553（AUD-DRAFT-001-DIGEST P2 波 P2-W14，CAND-AISA-017，B6 D-RESEARCH-11）
> 代码：`src/zephyr/intelligence/llm_research_agent.py`

## 0. 定位

LLM研究助手：规划器（任务→步骤计划）+工具白名单（检索/计算/数据库工具注册表注入，白名单外拒绝）+ReAct反思循环（思考-行动-观察-反思轮次护栏）+记忆写KB回调+本地模型优先语义+关键数字/标的强制事实回查（注入fact_checker）+仅辅助研究不直连交易硬标注。W04波漏处理补施工。

## 1. 规则（确定性）

- 纯内存/DI 设计：外部副作用（OS 调用/网络/进程控制）全部经注入回调，默认空操作或内存记录。
- 非法输入 Fail-Closed 抛专用 Error（占位错误码，波末统一转正）。
- 同输入必同输出（确定性）；时钟/随机源全注入。

## 2. 接口

见代码 `__all__` 与 docstring。消费方=运行时装配批（统一注入点装配）。

## 3. 测试

`tests/intelligence/test_llm_research_agent.py` —— 内存替身全覆盖：正常路径 + 边界 + Fail-Closed 分支 + 确定性。
