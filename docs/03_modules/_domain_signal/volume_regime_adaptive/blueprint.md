---
blueprint_id: MOD-SIG-129
module_name: volume_regime_adaptive
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
path: src/zephyr/signal_ashare/volume_regime_adaptive.py
granularity: file
---

# MOD-SIG-129 volume_regime_adaptive 蓝图（量能体制自适应策略）

> **module_id**: MOD-SIG-129 | **域**: D_ASHARE_SIGNAL | **优先级**: P2
> **来源**: B10-01445（AUD-DRAFT-001-DIGEST P2 波 P2-W06，CAND-TESTB-045，A1 模块23）
> 代码：`src/zephyr/signal_ashare/volume_regime_adaptive.py`

## 0. 定位

量能三态（vol/MA20：缩量<0.7/平量0.7-1.3/放量>1.3，极端分位标记）+量能×体制3×3策略矩阵查找表（趋势/均值回归/混沌×三态，参数由回测填参注入）+查找表查询接口+极端分位护栏。

## 1. 规则（确定性）

- 纯内存/DI 设计：外部副作用（OS 调用/网络/进程控制）全部经注入回调，默认空操作或内存记录。
- 非法输入 Fail-Closed 抛专用 Error（占位错误码，波末统一转正）。
- 同输入必同输出（确定性）；时钟/随机源全注入。

## 2. 接口

见代码 `__all__` 与 docstring。消费方=运行时装配批（统一注入点装配）。

## 3. 测试

`tests/signal_ashare/test_volume_regime_adaptive.py` —— 内存替身全覆盖：正常路径 + 边界 + Fail-Closed 分支 + 确定性。
