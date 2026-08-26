---
blueprint_id: MOD-SIG-121
module_name: orderflow_network_panic
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
path: src/zephyr/signal_ashare/orderflow_network_panic.py
granularity: file
---

# MOD-SIG-121 orderflow_network_panic 蓝图（跨资产订单流网络与亏钱扩散）

> **module_id**: MOD-SIG-121 | **域**: D_ASHARE_SIGNAL | **优先级**: P2
> **来源**: B10-01388（AUD-DRAFT-001-DIGEST P2 波 P2-W05，CAND-TESTB-041，A1 模块52）
> 代码：`src/zephyr/signal_ashare/orderflow_network_panic.py`

## 0. 定位

大幅回撤事件检测（窗口回撤>30%）+板块内Moran's I空间聚集统计（>0.3聚集判定，注入地理/行业邻接矩阵）+恐慌传导时滞（Granger 1-2日注入检验器）+扩散路径与强度输出。

## 1. 规则（确定性）

- 纯内存/DI 设计：外部副作用（OS 调用/网络/进程控制）全部经注入回调，默认空操作或内存记录。
- 非法输入 Fail-Closed 抛专用 Error（占位错误码，波末统一转正）。
- 同输入必同输出（确定性）；时钟/随机源全注入。

## 2. 接口

见代码 `__all__` 与 docstring。消费方=运行时装配批（统一注入点装配）。

## 3. 测试

`tests/signal_ashare/test_orderflow_network_panic.py` —— 内存替身全覆盖：正常路径 + 边界 + Fail-Closed 分支 + 确定性。
