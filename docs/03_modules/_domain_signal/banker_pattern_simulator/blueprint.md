---
blueprint_id: MOD-SIG-113
module_name: banker_pattern_simulator
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
path: src/zephyr/signal_ashare/banker_pattern_simulator.py
granularity: file
---

# MOD-SIG-113 banker_pattern_simulator 蓝图（庄家行为模式识别与模拟）

> **module_id**: MOD-SIG-113 | **域**: D_ASHARE_SIGNAL | **优先级**: P2
> **来源**: B1-00168（AUD-DRAFT-001-DIGEST P2 波 P2-W05，CAND-TESTB-030，C2 C-035）
> 代码：`src/zephyr/signal_ashare/banker_pattern_simulator.py`

## 0. 定位

庄家操纵六阶段子模式（建仓/洗盘/拉升/出货/对倒/护盘词表闭合）规则识别器（价量特征规则库+阶段转移判定）+反庄策略沙盒模拟（注入回测环境回调，仅回测/模拟语义标注）+风险警示与回避清单输出+识别结论不直接下单硬标注advisory。

## 1. 规则（确定性）

- 纯内存/DI 设计：外部副作用（OS 调用/网络/进程控制）全部经注入回调，默认空操作或内存记录。
- 非法输入 Fail-Closed 抛专用 Error（占位错误码，波末统一转正）。
- 同输入必同输出（确定性）；时钟/随机源全注入。

## 2. 接口

见代码 `__all__` 与 docstring。消费方=运行时装配批（统一注入点装配）。

## 3. 测试

`tests/signal_ashare/test_banker_pattern_simulator.py` —— 内存替身全覆盖：正常路径 + 边界 + Fail-Closed 分支 + 确定性。
