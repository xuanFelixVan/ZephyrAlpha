---
module_id: GOV-049
doc_type: index
status: Active
generated: '2026-05-02'
title: Diagrams
ttl: permanent
---

# Diagrams — 目录索引

## 责任声明（Single Responsibility）

本目录只存放：**架构图 — Mermaid 格式（.mmd）：C4/序列图/拓扑图/数据流图/治理激活甘特图**。

## 文件清单

### C4 模型

| 文件 | 说明 |
|------|------|
| c4_l1_system_context.mmd | C4 Level 1 系统上下文图（ZephyrAlpha + 外部系统）|
| c4_l2_containers.mmd | C4 Level 2 容器图（四大运行时容器）|
| c4_l3_l00_data_source.mmd | C4 Level 3 L00 数据源组件图 |
| c4_l3_l11_ml_platform.mmd | C4 Level 3 L11 ML 平台组件图 |
| c4_l3_l06_trade_execution.mmd | C4 Level 3 L06 交易执行组件图 |

### 拓扑图

| 文件 | 说明 |
|------|------|
| togaf_layer_stack.mmd | TOGAF 四层堆叠图（BA → IA → AA → TA）|
| docs_drawer_topology.mmd | docs/ 抽屉拓扑图 |
| scripts_topology.mmd | scripts/ 治理代码拓扑图 |
| frontend_mfe_topology.mmd | 前端微前端拓扑（Module Federation Host + 4 Apps）|
| integration_topology.mmd | 集成拓扑图（外部系统 + 内部层 + EI 契约编号）|
| runtime_topology.mmd | 运行时拓扑（主进程内 L00-L13 数据流 + 外部系统）|
| runtime_planes_topology.mmd | Runtime Planes 三平面物理拓扑（Hot / Warm / Cold）|
| view_dependencies.mmd | 视图间依赖关系图（BA/IA/AA/TA/DA/INTEG/SEC/OPS）|
| readme_view_dependency_graph.mmd | README 视图依赖图（10视图 + 2正交视图节点关系）|

### 数据流图

| 文件 | 说明 |
|------|------|
| business_value_stream.mmd | 业务价值流图（市场假设→研究→信号→组合→执行→监控闭环）|
| data_flow.mmd | 跨域核心数据流图 |
| dataflow_terminal.mmd | 终端数据流全景图（外部系统→L00→L02-L13→外部系统）|
| deployment_experimental.mmd | experimental 部署拓扑（开发机单进程 + 本地存储）|
| frontend_build_pipeline.mmd | 前端构建流水线（changeset→CI→lint→test→build→publish）|

### 序列图

| 文件 | 说明 |
|------|------|
| seq_order_submit.mmd | 订单提交端到端时序（正常 / Retry 幂等 / Broker failover）|
| seq_fill_received.mmd | 成交回报处理时序（Order→Position→PnL→Risk→Strategy）|
| seq_risk_trigger.mmd | 风控触发三阶段时序（Pre-trade / At-trade / Post-trade）|
| seq_rebalance.mmd | 组合再平衡流程时序（Scheduler→数据准备→策略→融合→Risk→Optimizer→批量下单）|
| seq_exception_handling.mmd | 异常处置三场景时序（Vendor 故障 / Broker 断连 / 策略异常）|

### 治理

| 文件 | 说明 |
|------|------|
| governance_d2b_loop.mmd | 治理 Design-to-Build 闭环（Policy→Factory→Runtime→Audit）|
| governance_three_layers.mmd | 治理三层边界拓扑（被治理者 + Policy/Factory/Runtime）|
| governance_activation_gantt.mmd | 治理架构激活甘特图（Sprint 9/10/11/T4 方案B）|
| capability_heatmap_visual.mmd | 能力成熟度热力图可视化（53域 × 10能力域 L0-L5）|

## 排除规则

- ❌ 非 Mermaid 图表（.png/.svg）→ 由 .mmd 渲染生成，不入库
- ❌ 图表使用说明 → target_architecture/index.md §6

## 父级目录

- 父级：[target_architecture/index.md](../index.md)
