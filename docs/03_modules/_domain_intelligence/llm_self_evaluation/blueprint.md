---
blueprint_id: MOD-INT-LLM-SELFEVAL
module_name: llm_self_evaluation
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
path: src/zephyr/intelligence/llm_self_evaluation.py
granularity: file
---

# MOD-INT-LLM-SELFEVAL llm_self_evaluation 蓝图（LLM自评估与交叉验证）

> **module_id**: MOD-INT-LLM-SELFEVAL | **域**: D_INTELLIGENCE | **优先级**: P2
> **来源**: B10-01883（AUD-DRAFT-001-DIGEST P2 波 P2-W04，CAND-AISA-013，A1 §29.37）
> 代码：`src/zephyr/intelligence/llm_self_evaluation.py`

## 0. 定位

LLM-as-Judge三维评分（事实/逻辑/风险，judge注入）+CoT推理链反向自校验（逐步重验标记不一致）+三模型独立分析投票（模型回调注入，一致性度量）+低一致性标争议降权或人工审核+结论不可直接触发交易硬约束（输出标注advisory）+CoT链写审计。canonical承接AISA-010归并。

## 1. 规则（确定性）

- 纯内存/DI 设计：外部副作用（OS 调用/网络/进程控制）全部经注入回调，默认空操作或内存记录。
- 非法输入 Fail-Closed 抛专用 Error（占位错误码，波末统一转正）。
- 同输入必同输出（确定性）；时钟/随机源全注入。

## 2. 接口

见代码 `__all__` 与 docstring。消费方=运行时装配批（统一注入点装配）。

## 3. 测试

`tests/intelligence/test_llm_self_evaluation.py` —— 内存替身全覆盖：正常路径 + 边界 + Fail-Closed 分支 + 确定性。
