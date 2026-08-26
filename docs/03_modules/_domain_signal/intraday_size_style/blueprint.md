---
blueprint_id: MOD-SIG-120
module_name: intraday_size_style
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
path: src/zephyr/signal_ashare/intraday_size_style.py
granularity: file
---

# MOD-SIG-120 intraday_size_style 蓝图（分时微结构与大小盘风格）

> **module_id**: MOD-SIG-120 | **域**: D_ASHARE_SIGNAL | **优先级**: P2
> **来源**: B10-01385（AUD-DRAFT-001-DIGEST P2 波 P2-W05，CAND-TESTB-040，A1 模块45）
> 代码：`src/zephyr/signal_ashare/intraday_size_style.py`

## 0. 定位

Size因子（大盘-小盘收益差序列）+风格持续性统计（同向>5天判定）+前半小时动量预测后半小时（Gao 2018 日内动量：首30min收益与次30min收益滚动相关+信号输出）+VWAP偏差+分时ADX辅助。

## 1. 规则（确定性）

- 纯内存/DI 设计：外部副作用（OS 调用/网络/进程控制）全部经注入回调，默认空操作或内存记录。
- 非法输入 Fail-Closed 抛专用 Error（占位错误码，波末统一转正）。
- 同输入必同输出（确定性）；时钟/随机源全注入。

## 2. 接口

见代码 `__all__` 与 docstring。消费方=运行时装配批（统一注入点装配）。

## 3. 测试

`tests/signal_ashare/test_intraday_size_style.py` —— 内存替身全覆盖：正常路径 + 边界 + Fail-Closed 分支 + 确定性。
