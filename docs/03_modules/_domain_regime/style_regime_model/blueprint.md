---
blueprint_id: MOD-REGIME-014
module_name: style_regime_model
domain: D_REGIME
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
domain_id: D_REGIME
path: src/zephyr/regime/style_regime_model.py
granularity: file
---

# MOD-REGIME-014 style_regime_model 蓝图（市场风格体制识别模型）

> **module_id**: MOD-REGIME-014 | **域**: D_REGIME | **优先级**: P2
> **来源**: B10-01447（AUD-DRAFT-001-DIGEST P2 波 P2-W06，CAND-CYCLE-006，A1 模块32）
> 代码：`src/zephyr/regime/style_regime_model.py`

## 0. 定位

市场风格体制：大小盘/价值成长收益差风格序列构建+HMM风格态识别（注入hmm_runner，hmmlearn未装降级规则分档）+风格→策略参数映射表（按风格态输出参数档）+风格切换确认（连续N期同向防抖）。

## 1. 规则（确定性）

- 纯内存/DI 设计：外部副作用（OS 调用/网络/进程控制）全部经注入回调，默认空操作或内存记录。
- 非法输入 Fail-Closed 抛专用 Error（占位错误码，波末统一转正）。
- 同输入必同输出（确定性）；时钟/随机源全注入。

## 2. 接口

见代码 `__all__` 与 docstring。消费方=运行时装配批（统一注入点装配）。

## 3. 测试

`tests/regime/test_style_regime_model.py` —— 内存替身全覆盖：正常路径 + 边界 + Fail-Closed 分支 + 确定性。
