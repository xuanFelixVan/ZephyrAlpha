---
blueprint_id: MOD-SIG-131
module_name: signal_weight_adjuster
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
path: src/zephyr/signal_ashare/signal_weight_adjuster.py
granularity: file
---

# MOD-SIG-131 signal_weight_adjuster 蓝图（信号权重调节器）

> **module_id**: MOD-SIG-131 | **域**: D_ASHARE_SIGNAL | **优先级**: P2
> **来源**: B11-02593（AUD-DRAFT-001-DIGEST P2 波 P2-W06，CAND-TESTB-054，A7 技能signal-weight-adjust）
> 代码：`src/zephyr/signal_ashare/signal_weight_adjuster.py`

## 0. 定位

滚动IC/胜率/回撤动态调权重（滚动窗口三指标→加权得分→目标权重）+限幅20%单次调整+权重变更审计回调+回滚接口（按版本回退）+漂移告警。

## 1. 规则（确定性）

- 纯内存/DI 设计：外部副作用（OS 调用/网络/进程控制）全部经注入回调，默认空操作或内存记录。
- 非法输入 Fail-Closed 抛专用 Error（占位错误码，波末统一转正）。
- 同输入必同输出（确定性）；时钟/随机源全注入。

## 2. 接口

见代码 `__all__` 与 docstring。消费方=运行时装配批（统一注入点装配）。

## 3. 测试

`tests/signal_ashare/test_signal_weight_adjuster.py` —— 内存替身全覆盖：正常路径 + 边界 + Fail-Closed 分支 + 确定性。
