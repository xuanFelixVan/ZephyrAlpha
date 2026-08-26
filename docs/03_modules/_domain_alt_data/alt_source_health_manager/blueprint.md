---
blueprint_id: MOD-ALT-011
module_name: alt_source_health_manager
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
path: src/zephyr/alt_data/alt_source_health_manager.py
granularity: file
---

# MOD-ALT-011 alt_source_health_manager 蓝图（另类数据源健康度管理器）

> **module_id**: MOD-ALT-011 | **域**: D_ALT_DATA | **优先级**: P2
> **来源**: B14-04617（AUD-DRAFT-001-DIGEST P2 波 P2-W04，CAND-TESTA-019，A9 D-ALT-DATA-31）
> 代码：`src/zephyr/alt_data/alt_source_health_manager.py`

## 0. 定位

另类数据源健康度：成功率/新鲜度/延迟滑动窗口评分+自动降级阶梯（降权→切源→标记停用状态机）+恢复探测（半开试探）+质量事件接告警回调。

## 1. 规则（确定性）

- 纯内存/DI 设计：外部副作用（OS 调用/网络/进程控制）全部经注入回调，默认空操作或内存记录。
- 非法输入 Fail-Closed 抛专用 Error（占位错误码，波末统一转正）。
- 同输入必同输出（确定性）；时钟/随机源全注入。

## 2. 接口

见代码 `__all__` 与 docstring。消费方=运行时装配批（统一注入点装配）。

## 3. 测试

`tests/alt_data/test_alt_source_health_manager.py` —— 内存替身全覆盖：正常路径 + 边界 + Fail-Closed 分支 + 确定性。
