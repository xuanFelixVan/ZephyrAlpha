---
blueprint_id: MOD-DATA-065
module_name: tushare_news_connector
domain: D_DATA
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
domain_id: D_DATA
path: src/zephyr/data/implementations/tushare_news_connector.py
granularity: file
---

# MOD-DATA-065 tushare_news_connector 蓝图（tushare新闻源接入器）

> **module_id**: MOD-DATA-065 | **域**: D_DATA | **优先级**: P2
> **来源**: B13-04043（AUD-DRAFT-001-DIGEST P2 波 P2-W02，CAND-DAT-019，A3数据架构）
> 代码：`src/zephyr/data/implementations/tushare_news_connector.py`

## 0. 定位

tushare新闻权限开通后的接入面（API调用全注入，不真发请求）：news快讯接口接入news_collector管道语义+与现有源去重（标题+时间窗指纹）+历史数据回补校验（回补区间完整性检查）+质量门控挂接（注入gate回调）。权限开通属Owner窗口，本件=接入契约逻辑。

## 1. 规则（确定性）

- 纯内存/DI 设计：外部副作用（OS 调用/网络/进程控制）全部经注入回调，默认空操作或内存记录。
- 非法输入 Fail-Closed 抛专用 Error（占位错误码，波末统一转正）。
- 同输入必同输出（确定性）；时钟/随机源全注入。

## 2. 接口

见代码 `__all__` 与 docstring。消费方=运行时装配批（统一注入点装配）。

## 3. 测试

`tests/data/implementations/test_tushare_news_connector.py` —— 内存替身全覆盖：正常路径 + 边界 + Fail-Closed 分支 + 确定性。
