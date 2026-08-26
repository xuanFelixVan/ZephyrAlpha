---
blueprint_id: MOD-FAC-006
module_name: llm_evolutionary_search
domain: D_FACTOR
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
domain_id: D_FACTOR
path: src/zephyr/research/llm_evolutionary_search.py
granularity: file
---

# MOD-FAC-006 llm_evolutionary_search 蓝图（LLM进化式策略搜索）

> **module_id**: MOD-FAC-006 | **域**: D_FACTOR | **优先级**: P2
> **来源**: B10-01877（AUD-DRAFT-001-DIGEST P2 波 P2-W07，CAND-FAC-021，A1 §29.32）
> 代码：`src/zephyr/research/llm_evolutionary_search.py`

## 0. 定位

LLM变异三角色（Exploit保守/Explore激进/Crossover-Genesis合并或从零生成，LLM回调注入）+种群≤20+精英保留+多样性注入+仅盘后运行语义+进化输出必经三重门禁+p-hacking概率评估（注入评估器）+人工裁决队列，严禁全自动上线硬约束。

## 1. 规则（确定性）

- 纯内存/DI 设计：外部副作用（OS 调用/网络/进程控制）全部经注入回调，默认空操作或内存记录。
- 非法输入 Fail-Closed 抛专用 Error（占位错误码，波末统一转正）。
- 同输入必同输出（确定性）；时钟/随机源全注入。

## 2. 接口

见代码 `__all__` 与 docstring。消费方=运行时装配批（统一注入点装配）。

## 3. 测试

`tests/research/test_llm_evolutionary_search.py` —— 内存替身全覆盖：正常路径 + 边界 + Fail-Closed 分支 + 确定性。
