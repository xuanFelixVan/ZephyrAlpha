---
blueprint_id: MOD-SIG-116
module_name: wyckoff_secondary_test
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
path: src/zephyr/signal_ashare/wyckoff_secondary_test.py
granularity: file
---

# MOD-SIG-116 wyckoff_secondary_test 蓝图（Wyckoff二次测试模型）

> **module_id**: MOD-SIG-116 | **域**: D_ASHARE_SIGNAL | **优先级**: P2
> **来源**: B10-01372（AUD-DRAFT-001-DIGEST P2 波 P2-W05，CAND-TESTB-036，A1 模块18）
> 代码：`src/zephyr/signal_ashare/wyckoff_secondary_test.py`

## 0. 定位

Wyckoff ST缩量确认（回踩量<前波段均量阈值）+Markup/Markdown识别（ higher high/lower low 结构判定）+回调38.2%/61.8%历史概率表（滚动统计注入k线序列）+动量延续vs反转判定输出。

## 1. 规则（确定性）

- 纯内存/DI 设计：外部副作用（OS 调用/网络/进程控制）全部经注入回调，默认空操作或内存记录。
- 非法输入 Fail-Closed 抛专用 Error（占位错误码，波末统一转正）。
- 同输入必同输出（确定性）；时钟/随机源全注入。

## 2. 接口

见代码 `__all__` 与 docstring。消费方=运行时装配批（统一注入点装配）。

## 3. 测试

`tests/signal_ashare/test_wyckoff_secondary_test.py` —— 内存替身全覆盖：正常路径 + 边界 + Fail-Closed 分支 + 确定性。
