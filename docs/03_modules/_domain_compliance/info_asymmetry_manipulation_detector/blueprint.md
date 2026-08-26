---
blueprint_id: MOD-CMP-014
module_name: info_asymmetry_manipulation_detector
domain: D_COMPLIANCE
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
domain_id: D_COMPLIANCE
path: src/zephyr/compliance/info_asymmetry_manipulation_detector.py
granularity: file
---

# MOD-CMP-014 info_asymmetry_manipulation_detector 蓝图（信息不对称期与操纵检测器）

> **module_id**: MOD-CMP-014 | **域**: D_COMPLIANCE | **优先级**: P2
> **来源**: B10-01426（AUD-DRAFT-001-DIGEST P2 波 P2-W10，CAND-CMP-005，A1 模块54）
> 代码：`src/zephyr/compliance/info_asymmetry_manipulation_detector.py`

## 0. 定位

空窗期（披露间隔>90天/11月-次年4月30日窗口判定）异常波动z>2扫描+操纵嫌疑评分（幌骗/对敲/尾盘操纵三模式规则：偏离度+撤单率+间隔+量集中度注入数据）+回避名单输出供漏斗排除。

## 1. 规则（确定性）

- 纯内存/DI 设计：外部副作用（OS 调用/网络/进程控制）全部经注入回调，默认空操作或内存记录。
- 非法输入 Fail-Closed 抛专用 Error（占位错误码，波末统一转正）。
- 同输入必同输出（确定性）；时钟/随机源全注入。

## 2. 接口

见代码 `__all__` 与 docstring。消费方=运行时装配批（统一注入点装配）。

## 3. 测试

`tests/compliance/test_info_asymmetry_manipulation_detector.py` —— 内存替身全覆盖：正常路径 + 边界 + Fail-Closed 分支 + 确定性。
