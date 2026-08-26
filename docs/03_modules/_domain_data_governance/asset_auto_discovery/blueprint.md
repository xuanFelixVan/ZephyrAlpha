---
blueprint_id: MOD-DATA_GOV-014
module_name: asset_auto_discovery
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
path: src/zephyr/data_governance/asset_auto_discovery.py
granularity: file
---

# MOD-DATA_GOV-014 asset_auto_discovery 蓝图（数据资产自动发现器）

> **module_id**: MOD-DATA_GOV-014 | **域**: D_DATA_GOV | **优先级**: P2
> **来源**: B10-02326（AUD-DRAFT-001-DIGEST P2 波 P2-W02，CAND-DATGOV-011，A1 M8-NEW-07）
> 代码：`src/zephyr/data_governance/asset_auto_discovery.py`

## 0. 定位

资产自动发现：扫描源注册（ClickHouse表/因子注册表/信号注册表三类scanner注入）+自动生成数据资产卡片（asset_id/类型/owner/更新频率/质量分默认）+入metadata_registry（注入注册表回调）+定时增量更新（指纹diff只更新变更）。

## 1. 规则（确定性）

- 纯内存/DI 设计：外部副作用（OS 调用/网络/进程控制）全部经注入回调，默认空操作或内存记录。
- 非法输入 Fail-Closed 抛专用 Error（占位错误码，波末统一转正）。
- 同输入必同输出（确定性）；时钟/随机源全注入。

## 2. 接口

见代码 `__all__` 与 docstring。消费方=运行时装配批（统一注入点装配）。

## 3. 测试

`tests/data_governance/test_asset_auto_discovery.py` —— 内存替身全覆盖：正常路径 + 边界 + Fail-Closed 分支 + 确定性。
