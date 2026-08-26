---
blueprint_id: MOD-CMP-013
module_name: evidence_chain_generator
domain: D_COMPLIANCE
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
domain_id: D_COMPLIANCE
path: src/zephyr/compliance/evidence_chain_generator.py
granularity: file
---

# MOD-CMP-013 evidence_chain_generator 蓝图（合规证据链生成器）

> **module_id**: MOD-CMP-013 | **域**: D_COMPLIANCE | **优先级**: P2
> **来源**: B1-00312（AUD-DRAFT-001-DIGEST P2 波 P2-W10，CAND-CMP-003，C2）
> 代码：`src/zephyr/compliance/evidence_chain_generator.py`

## 0. 定位

委托/成交/决策快照自动采集（采集器注册表注入）→哈希链式落盘（append-only+prev_hash链，复用compliance_log语义）+检索导出（按时间/类型/标的查询+导出JSONL）。WORM思想。

## 1. 规则（确定性）

- 纯内存/DI 设计：外部副作用（OS 调用/网络/进程控制）全部经注入回调，默认空操作或内存记录。
- 非法输入 Fail-Closed 抛专用 Error（占位错误码，波末统一转正）。
- 同输入必同输出（确定性）；时钟/随机源全注入。

## 2. 接口

见代码 `__all__` 与 docstring。消费方=运行时装配批（统一注入点装配）。

## 3. 测试

`tests/compliance/test_evidence_chain_generator.py` —— 内存替身全覆盖：正常路径 + 边界 + Fail-Closed 分支 + 确定性。
