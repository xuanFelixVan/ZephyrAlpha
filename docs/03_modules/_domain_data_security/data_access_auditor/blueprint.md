---
blueprint_id: MOD-DATSEC-002
module_name: data_access_auditor
domain: D_DATA_SEC
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
domain_id: D_DATA_SEC
path: src/zephyr/data_security/data_access_auditor.py
granularity: file
---

# MOD-DATSEC-002 data_access_auditor 蓝图（数据访问审计器）

> **module_id**: MOD-DATSEC-002 | **域**: D_DATA_SEC | **优先级**: P2
> **来源**: B13-04294（AUD-DRAFT-001-DIGEST P2 波 P2-W02，CAND-DATSEC-002，A3数据架构）
> 代码：`src/zephyr/data_security/data_access_auditor.py`

## 0. 定位

数据访问审计：CH/SQLite/Parquet访问日志统一采集（AccessEvent schema）+查询模式基线（按主体常用表/时段/量级画像）+异常访问检测（非常用表/大批量导出/非常时段三维规则）+敏感数据访问追踪（敏感表注册表），事件写gov_audit回调。UEBA轻量版。

## 1. 规则（确定性）

- 纯内存/DI 设计：外部副作用（OS 调用/网络/进程控制）全部经注入回调，默认空操作或内存记录。
- 非法输入 Fail-Closed 抛专用 Error（占位错误码，波末统一转正）。
- 同输入必同输出（确定性）；时钟/随机源全注入。

## 2. 接口

见代码 `__all__` 与 docstring。消费方=运行时装配批（统一注入点装配）。

## 3. 测试

`tests/data_security/test_data_access_auditor.py` —— 内存替身全覆盖：正常路径 + 边界 + Fail-Closed 分支 + 确定性。
