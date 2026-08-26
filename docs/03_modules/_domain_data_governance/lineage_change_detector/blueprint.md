---
blueprint_id: MOD-DATA_GOV-010
module_name: lineage_change_detector
domain: D_DATA_GOV
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
domain_id: D_DATA_GOV
path: src/zephyr/data_governance/lineage_change_detector.py
granularity: file
---

# MOD-DATA_GOV-010 lineage_change_detector 蓝图（血缘变更检测器）

> **module_id**: MOD-DATA_GOV-010 | **域**: D_DATA_GOV | **优先级**: P2
> **来源**: B10-02319（AUD-DRAFT-001-DIGEST P2 波 P2-W02，CAND-DATGOV-007，A1 M8-S07）
> 代码：`src/zephyr/data_governance/lineage_change_detector.py`

## 0. 定位

血缘图快照diff：周期快照（边集合指纹）+新增/删除/改向边检测+下游影响集合计算（DFS）+变更报告生成+下游依赖方通知回调，接入drift检测器注册语义（detector_id/schedule元数据）。canonical 承接 CAND-DATGOV-012 归并。

## 1. 规则（确定性）

- 纯内存/DI 设计：外部副作用（OS 调用/网络/进程控制）全部经注入回调，默认空操作或内存记录。
- 非法输入 Fail-Closed 抛专用 Error（占位错误码，波末统一转正）。
- 同输入必同输出（确定性）；时钟/随机源全注入。

## 2. 接口

见代码 `__all__` 与 docstring。消费方=运行时装配批（统一注入点装配）。

## 3. 测试

`tests/data_governance/test_lineage_change_detector.py` —— 内存替身全覆盖：正常路径 + 边界 + Fail-Closed 分支 + 确定性。
