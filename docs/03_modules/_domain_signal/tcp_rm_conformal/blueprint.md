---
blueprint_id: MOD-SIG-128
module_name: tcp_rm_conformal
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
path: src/zephyr/signal_ashare/tcp_rm_conformal.py
granularity: file
---

# MOD-SIG-128 tcp_rm_conformal 蓝图（时序保形预测增强器）

> **module_id**: MOD-SIG-128 | **域**: D_ASHARE_SIGNAL | **优先级**: P2
> **来源**: B10-01854（AUD-DRAFT-001-DIGEST P2 波 P2-W06，CAND-TESTB-050，A1 §29.16-5）
> 代码：`src/zephyr/signal_ashare/tcp_rm_conformal.py`

## 0. 定位

TCP-RM时序保形预测：Robbins-Monro在线校准（分位数误差反馈步长衰减更新阈值）+DDCI双反馈（覆盖不足/过宽双向调节）+CP-VaR回测语义（注入回测序列）+覆盖率统计报告。

## 1. 规则（确定性）

- 纯内存/DI 设计：外部副作用（OS 调用/网络/进程控制）全部经注入回调，默认空操作或内存记录。
- 非法输入 Fail-Closed 抛专用 Error（占位错误码，波末统一转正）。
- 同输入必同输出（确定性）；时钟/随机源全注入。

## 2. 接口

见代码 `__all__` 与 docstring。消费方=运行时装配批（统一注入点装配）。

## 3. 测试

`tests/signal_ashare/test_tcp_rm_conformal.py` —— 内存替身全覆盖：正常路径 + 边界 + Fail-Closed 分支 + 确定性。
