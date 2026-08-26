---
blueprint_id: MOD-ALT-007
module_name: alt_data_connector
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
path: src/zephyr/alt_data/alt_data_connector.py
granularity: file
---

# MOD-ALT-007 alt_data_connector 蓝图（另类数据统一接入器）

> **module_id**: MOD-ALT-007 | **域**: D_ALT_DATA | **优先级**: P2
> **来源**: B5-07081（AUD-DRAFT-001-DIGEST P2 波 P2-W04，CAND-TESTA-022，B5 D-ALT-DATA-01）
> 代码：`src/zephyr/alt_data/alt_data_connector.py`

## 0. 定位

统一另类数据接入层：新闻/公告/社交三类连接器注册表（免费源优先）+格式适配（适配器协议）+增量同步游标（断点续传checkpoint持久化）+API密钥加密存储（注入cipher）+落原始层登记source_health。AkShare/巨潮RSS语义，API全注入不真发。

## 1. 规则（确定性）

- 纯内存/DI 设计：外部副作用（OS 调用/网络/进程控制）全部经注入回调，默认空操作或内存记录。
- 非法输入 Fail-Closed 抛专用 Error（占位错误码，波末统一转正）。
- 同输入必同输出（确定性）；时钟/随机源全注入。

## 2. 接口

见代码 `__all__` 与 docstring。消费方=运行时装配批（统一注入点装配）。

## 3. 测试

`tests/alt_data/test_alt_data_connector.py` —— 内存替身全覆盖：正常路径 + 边界 + Fail-Closed 分支 + 确定性。
