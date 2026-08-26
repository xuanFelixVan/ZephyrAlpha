---
blueprint_id: MOD-INF-091
module_name: config_center
domain: D_INFRASTRUCTURE
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
domain_id: D_INFRASTRUCTURE
path: src/zephyr/infrastructure/config/config_center.py
granularity: file
---

# MOD-INF-091 config_center 蓝图（统一配置中心）

> **module_id**: MOD-INF-091 | **域**: D_INFRASTRUCTURE | **优先级**: P2
> **来源**: B1-00203（AUD-DRAFT-001-DIGEST P2 波 P2-W01，CAND-INFRASTR-001，C2）
> 代码：`src/zephyr/infrastructure/config/config_center.py`

## 0. 定位

统一配置注册表（YAML/内存后端）+参数版本快照（每次变更version递增+快照留存）+变更审计日志（注入audit回调）+回滚API（按版本回退），整合现有热更新守卫语义（守卫校验钩子注入）。Nacos/Apollo单机化。

## 1. 规则（确定性）

- 纯内存/DI 设计：外部副作用（OS 调用/网络/进程控制）全部经注入回调，默认空操作或内存记录。
- 非法输入 Fail-Closed 抛专用 Error（占位错误码，波末统一转正）。
- 同输入必同输出（确定性）；时钟/随机源全注入。

## 2. 接口

见代码 `__all__` 与 docstring。消费方=运行时装配批（统一注入点装配）。

## 3. 测试

`tests/infrastructure/test_config_center.py` —— 内存替身全覆盖：正常路径 + 边界 + Fail-Closed 分支 + 确定性。
