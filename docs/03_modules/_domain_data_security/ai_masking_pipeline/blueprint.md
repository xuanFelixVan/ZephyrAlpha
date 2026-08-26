---
blueprint_id: MOD-DATSEC-001
module_name: ai_masking_pipeline
domain: D_DATA_SEC
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
domain_id: D_DATA_SEC
path: src/zephyr/data_security/ai_masking_pipeline.py
granularity: file
---

# MOD-DATSEC-001 ai_masking_pipeline 蓝图（AI分级脱敏管道）

> **module_id**: MOD-DATSEC-001 | **域**: D_DATA_SEC | **优先级**: P2
> **来源**: B13-04183（AUD-DRAFT-001-DIGEST P2 波 P2-W02，CAND-DATSEC-001，A3数据架构）
> 代码：`src/zephyr/data_security/ai_masking_pipeline.py`

## 0. 定位

L1-L4分级脱敏管道：L4禁发仅统计摘要/L3金额标的泛化（大额/标的A）/L2因子定义+统计禁发原值序列/L1无要求，策略表驱动（与MOD-DATSEC-003共用策略schema），每次LLM调用记录脱敏前后对比入审计回调。Presidio分级思想。

## 1. 规则（确定性）

- 纯内存/DI 设计：外部副作用（OS 调用/网络/进程控制）全部经注入回调，默认空操作或内存记录。
- 非法输入 Fail-Closed 抛专用 Error（占位错误码，波末统一转正）。
- 同输入必同输出（确定性）；时钟/随机源全注入。

## 2. 接口

见代码 `__all__` 与 docstring。消费方=运行时装配批（统一注入点装配）。

## 3. 测试

`tests/data_security/test_ai_masking_pipeline.py` —— 内存替身全覆盖：正常路径 + 边界 + Fail-Closed 分支 + 确定性。
