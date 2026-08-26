---
blueprint_id: MOD-INF-087
module_name: runtime_topology_visualizer
domain: D_INFRA_OPS
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
domain_id: D_INFRA_OPS
path: src/zephyr/infra_ops/runtime_topology_visualizer.py
granularity: file
---

# MOD-INF-087 runtime_topology_visualizer 蓝图（运行时依赖拓扑器）

> **module_id**: MOD-INF-087 | **域**: D_INFRA_OPS | **优先级**: P2
> **来源**: B14-04635（AUD-DRAFT-001-DIGEST P2 波 P2-W01，CAND-INFRAOPS-005，A9运维架构）
> 代码：`src/zephyr/infra_ops/runtime_topology_visualizer.py`

## 0. 定位

运行时依赖拓扑数据模型：P1~P5/Redis/GPU/miniQMT/iFind节点注册+心跳状态着色（green/yellow/red判定）+数据流边标注（Pub/Sub/KV/List），快照输出JSON字典供仪表盘消费（本件只做后端数据，不做前端页面接线），随健康检查注入刷新。

## 1. 规则（确定性）

- 纯内存/DI 设计：外部副作用（OS 调用/网络/进程控制）全部经注入回调，默认空操作或内存记录。
- 非法输入 Fail-Closed 抛专用 Error（占位错误码，波末统一转正）。
- 同输入必同输出（确定性）；时钟/随机源全注入。

## 2. 接口

见代码 `__all__` 与 docstring。消费方=运行时装配批（统一注入点装配）。

## 3. 测试

`tests/infra_ops/test_runtime_topology_visualizer.py` —— 内存替身全覆盖：正常路径 + 边界 + Fail-Closed 分支 + 确定性。
