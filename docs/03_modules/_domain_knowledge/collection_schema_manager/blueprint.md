---
blueprint_id: MOD-KNW-010
module_name: collection_schema_manager
domain: D_KNOWLEDGE
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
domain_id: D_KNOWLEDGE
path: src/zephyr/knowledge/collection_schema_manager.py
granularity: file
---

# MOD-KNW-010 collection_schema_manager 蓝图（Collection模式管理器）

> **module_id**: MOD-KNW-010 | **域**: D_KNOWLEDGE | **优先级**: P2
> **来源**: B13-04346（AUD-DRAFT-001-DIGEST P2 波 P2-W03，CAND-KNW-012，A3 D-AUTONOMY-187）
> 代码：`src/zephyr/knowledge/collection_schema_manager.py`

## 0. 定位

8大Collection schema版本注册（schema_id/version/字段定义）+迁移脚本注册与执行编排（向量重建/元数据回填，执行经注入runner）+破坏性变更检测（字段删除/类型变更判定，CI报告）+跨Collection查询沿用语义。

## 1. 规则（确定性）

- 纯内存/DI 设计：外部副作用（OS 调用/网络/进程控制）全部经注入回调，默认空操作或内存记录。
- 非法输入 Fail-Closed 抛专用 Error（占位错误码，波末统一转正）。
- 同输入必同输出（确定性）；时钟/随机源全注入。

## 2. 接口

见代码 `__all__` 与 docstring。消费方=运行时装配批（统一注入点装配）。

## 3. 测试

`tests/knowledge/test_collection_schema_manager.py` —— 内存替身全覆盖：正常路径 + 边界 + Fail-Closed 分支 + 确定性。
