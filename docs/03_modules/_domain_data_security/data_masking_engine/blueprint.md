---
blueprint_id: MOD-DATSEC-003
module_name: data_masking_engine
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
path: src/zephyr/data_security/data_masking_engine.py
granularity: file
---

# MOD-DATSEC-003 data_masking_engine 蓝图（数据脱敏引擎）

> **module_id**: MOD-DATSEC-003 | **域**: D_DATA_SEC | **优先级**: P2
> **来源**: B13-04295（AUD-DRAFT-001-DIGEST P2 波 P2-W02，CAND-DATSEC-003，A3数据架构）
> 代码：`src/zephyr/data_security/data_masking_engine.py`

## 0. 定位

脱敏引擎：格式保留加密FPE（身份证/账号：注入cipher回调，默认确定性伪FPE占位实现标注非密码学安全）+动态脱敏（按查询角色策略表：同字段不同角色不同掩码）+差分隐私噪声（统计输出拉普拉斯噪声ε可配，注入随机源），与MOD-DATSEC-001共用策略表schema。

## 1. 规则（确定性）

- 纯内存/DI 设计：外部副作用（OS 调用/网络/进程控制）全部经注入回调，默认空操作或内存记录。
- 非法输入 Fail-Closed 抛专用 Error（占位错误码，波末统一转正）。
- 同输入必同输出（确定性）；时钟/随机源全注入。

## 2. 接口

见代码 `__all__` 与 docstring。消费方=运行时装配批（统一注入点装配）。

## 3. 测试

`tests/data_security/test_data_masking_engine.py` —— 内存替身全覆盖：正常路径 + 边界 + Fail-Closed 分支 + 确定性。
