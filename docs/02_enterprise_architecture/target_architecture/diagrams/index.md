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

本目录只存放：**架构图 — Mermaid 格式（.mmd）：C4/序列图/拓扑图/数据流图**。

## 文件清单

### C4 模型

| 文件 | 说明 |
|------|------|
| c4_l1_system_context.mmd | C4 Level 1 系统上下文图（ZephyrAlpha + 外部系统）|
| c4_l2_containers.mmd | C4 Level 2 容器图（四大运行时容器）|
| c4_l3_d_mkt_data.mmd | C4 Level 3 数据源组件图（D_MKT_DATA）|
| c4_l3_d_ml_train.mmd | C4 Level 3 ML 平台组件图（D_ML_TRAIN）|
| c4_l3_d_ex_core.mmd | C4 Level 3 交易执行组件图（D_EX_CORE）|

### 拓扑图

| 文件 | 说明 |
|------|------|
| togaf_layer_stack.mmd | TOGAF 四层堆叠图（BA → IA → AA → TA）|
| docs_drawer_topology.mmd | docs/ 抽屉拓扑图 |
| scripts_topology.mmd | scripts/ 治理代码拓扑图 |
| integration_topology.mmd | 集成拓扑图（外部系统 + 内部层 + EI 契约编号）|
| runtime_topology.mmd | 运行时拓扑（主进程内全域数据流 + 外部系统）|

### 数据流图

| 文件 | 说明 |
|------|------|
| business_value_stream.mmd | 业务价值流图（市场假设→研究→信号→组合→执行→监控闭环）|
| data_flow.mmd | 跨域核心数据流图 |
| dataflow_terminal.mmd | 终端数据流全景图（外部系统→D_MKT_DATA→各业务域→外部系统）|
| deployment_experimental.mmd | experimental 部署拓扑（开发机单进程 + 本地存储）|

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
| capability_heatmap_visual.mmd | 能力成熟度热力图可视化（53域 × 10能力域 L0-L5）|

## 排除规则

- ❌ 非 Mermaid 图表（.png/.svg）→ 由 .mmd 渲染生成，不入库
- ❌ 图表使用说明 → target_architecture/index.md §6

## 父级目录

- 父级：[target_architecture/index.md](../index.md)
