---
blueprint_id: MOD-SIG-127
module_name: causal_ml_engine
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
path: src/zephyr/signal_ashare/causal_ml_engine.py
granularity: file
---

# MOD-SIG-127 causal_ml_engine 蓝图（因果ML引擎）

> **module_id**: MOD-SIG-127 | **域**: D_ASHARE_SIGNAL | **优先级**: P2
> **来源**: B10-01858（AUD-DRAFT-001-DIGEST P2 波 P2-W06，CAND-TESTB-051，A1 §29.18）
> 代码：`src/zephyr/signal_ashare/causal_ml_engine.py`

## 0. 定位

因果ML：DML因子因果效应估计（注入dml_runner，econml未装降级）+CausalForest异质效应（注入）+DoWhy因果图证伪（注入dowhy_runner降级标记）+PC/LiNGAM因果发现（注入discovery_runner）+盘前预计算因果图缓存+效应显著性筛选。canonical承接TESTB-035/047归并。

## 1. 规则（确定性）

- 纯内存/DI 设计：外部副作用（OS 调用/网络/进程控制）全部经注入回调，默认空操作或内存记录。
- 非法输入 Fail-Closed 抛专用 Error（占位错误码，波末统一转正）。
- 同输入必同输出（确定性）；时钟/随机源全注入。

## 2. 接口

见代码 `__all__` 与 docstring。消费方=运行时装配批（统一注入点装配）。

## 3. 测试

`tests/signal_ashare/test_causal_ml_engine.py` —— 内存替身全覆盖：正常路径 + 边界 + Fail-Closed 分支 + 确定性。
