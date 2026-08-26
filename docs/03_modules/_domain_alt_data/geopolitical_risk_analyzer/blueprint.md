---
blueprint_id: MOD-ALT-014
module_name: geopolitical_risk_analyzer
domain: D_ALT_DATA
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
domain_id: D_ALT_DATA
path: src/zephyr/alt_data/geopolitical_risk_analyzer.py
granularity: file
---

# MOD-ALT-014 geopolitical_risk_analyzer 蓝图（地缘政治风险分析器）

> **module_id**: MOD-ALT-014 | **域**: D_ALT_DATA | **优先级**: P2
> **来源**: B5-07092（AUD-DRAFT-001-DIGEST P2 波 P2-W04，CAND-TESTA-025，B5 D-ALT-DATA-12）
> 代码：`src/zephyr/alt_data/geopolitical_risk_analyzer.py`

## 0. 定位

地缘风险分析：事件采集（免费新闻/RSS注入）+风险评分（国家/商品传导矩阵注入映射）+公开制裁名单比对筛查（名单注入，命中标记）+风险事件入事件总线回调仅作信号输入。

## 1. 规则（确定性）

- 纯内存/DI 设计：外部副作用（OS 调用/网络/进程控制）全部经注入回调，默认空操作或内存记录。
- 非法输入 Fail-Closed 抛专用 Error（占位错误码，波末统一转正）。
- 同输入必同输出（确定性）；时钟/随机源全注入。

## 2. 接口

见代码 `__all__` 与 docstring。消费方=运行时装配批（统一注入点装配）。

## 3. 测试

`tests/alt_data/test_geopolitical_risk_analyzer.py` —— 内存替身全覆盖：正常路径 + 边界 + Fail-Closed 分支 + 确定性。
