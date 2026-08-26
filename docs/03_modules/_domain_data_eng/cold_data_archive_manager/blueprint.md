---
blueprint_id: MOD-DATENG-002
module_name: cold_data_archive_manager
domain: D_DATA_ENG
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
domain_id: D_DATA_ENG
path: src/zephyr/data_eng/cold_data_archive_manager.py
granularity: file
---

# MOD-DATENG-002 cold_data_archive_manager 蓝图（冷数据归档管理器）

> **module_id**: MOD-DATENG-002 | **域**: D_DATA_ENG | **优先级**: P2
> **来源**: B13-04331（AUD-DRAFT-001-DIGEST P2 波 P2-W02，CAND-DATENG-005，A3数据架构）
> 代码：`src/zephyr/data_eng/cold_data_archive_manager.py`

## 0. 定位

冷数据归档：CH老分区→Parquet(zstd)归档目录编排+归档索引（SQLite注入连接：partition/path/hash/archived_at）+按策略清理（保留期注册表+清理执行回调）+归档检索只读接口+auto_archive_scheduler周期计划生成。

## 1. 规则（确定性）

- 纯内存/DI 设计：外部副作用（OS 调用/网络/进程控制）全部经注入回调，默认空操作或内存记录。
- 非法输入 Fail-Closed 抛专用 Error（占位错误码，波末统一转正）。
- 同输入必同输出（确定性）；时钟/随机源全注入。

## 2. 接口

见代码 `__all__` 与 docstring。消费方=运行时装配批（统一注入点装配）。

## 3. 测试

`tests/data_eng/test_cold_data_archive_manager.py` —— 内存替身全覆盖：正常路径 + 边界 + Fail-Closed 分支 + 确定性。
