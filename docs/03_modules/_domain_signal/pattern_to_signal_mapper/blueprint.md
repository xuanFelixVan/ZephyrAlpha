---
blueprint_id: MOD-SIG-115
module_name: pattern_to_signal_mapper
domain: D_ASHARE_SIGNAL
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
domain_id: D_ASHARE_SIGNAL
path: src/zephyr/signal_ashare/pattern_to_signal_mapper.py
granularity: file
---

# MOD-SIG-115 pattern_to_signal_mapper 蓝图（形态信号转化层）

> **module_id**: MOD-SIG-115 | **域**: D_ASHARE_SIGNAL | **优先级**: P2
> **来源**: B1-00849（AUD-DRAFT-001-DIGEST P2 波 P2-W05，CAND-TESTB-033，C2 97）
> 代码：`src/zephyr/signal_ashare/pattern_to_signal_mapper.py`

## 0. 定位

97形态→信号转化层：消费PatternEvent（类型+置信度+关键点位+方向+历史胜率）→方向/强度/止损位映射（形态→方向映射表+强度=置信度×胜率加权+止损=关键点位外扩k%）+CTR-002兼容FactorSignal输出（注入产出校验）。

## 1. 规则（确定性）

- 纯内存/DI 设计：外部副作用（OS 调用/网络/进程控制）全部经注入回调，默认空操作或内存记录。
- 非法输入 Fail-Closed 抛专用 Error（占位错误码，波末统一转正）。
- 同输入必同输出（确定性）；时钟/随机源全注入。

## 2. 接口

见代码 `__all__` 与 docstring。消费方=运行时装配批（统一注入点装配）。

## 3. 测试

`tests/signal_ashare/test_pattern_to_signal_mapper.py` —— 内存替身全覆盖：正常路径 + 边界 + Fail-Closed 分支 + 确定性。
