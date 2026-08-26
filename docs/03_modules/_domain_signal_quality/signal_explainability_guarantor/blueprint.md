---
blueprint_id: MOD-SIGQC-006
module_name: signal_explainability_guarantor
domain: D_SIGQC
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
domain_id: D_SIGQC
path: src/zephyr/signal_quality/signal_explainability_guarantor.py
granularity: file
---

# MOD-SIGQC-006 signal_explainability_guarantor 蓝图（信号可解释性强制保障器）

> **module_id**: MOD-SIGQC-006 | **域**: D_SIGQC | **优先级**: P2
> **来源**: B2-05485（AUD-DRAFT-001-DIGEST P2 波 P2-W15，CAND-SIGQC-005，B2 D-SIGNAL-211）
> 代码：`src/zephyr/signal_quality/signal_explainability_guarantor.py`

## 0. 定位

可解释性强制契约：信号输出必须携带理由链（触发因子+规则命中+置信度依据三要素）+缺失即阻断+告警+解释字段入decision_snapshot/signal_audit链（注入sink）+事后回放支持（按signal_id反查）。

## 1. 规则（确定性）

- 纯内存/DI 设计：外部副作用（OS 调用/网络/进程控制）全部经注入回调，默认空操作或内存记录。
- 非法输入 Fail-Closed 抛专用 Error（占位错误码，波末统一转正）。
- 同输入必同输出（确定性）；时钟/随机源全注入。

## 2. 接口

见代码 `__all__` 与 docstring。消费方=运行时装配批（统一注入点装配）。

## 3. 测试

`tests/signal_quality/test_signal_explainability_guarantor.py` —— 内存替身全覆盖：正常路径 + 边界 + Fail-Closed 分支 + 确定性。
