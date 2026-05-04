---
module_id: EA-DIAGRAMS-INDEX
doc_type: index
status: active
generated: '2026-05-02'
---

# Diagrams — 目录索引

## 责任声明（Single Responsibility）

本目录只存放：**架构图 — Mermaid 格式（.mmd）：C4/序列图/拓扑图/数据流图/治理激活甘特图**。

## 文件清单

### C4 模型

| 文件 | 说明 |
|------|------|
| c4-l1-system-context.mmd | C4 Level 1 系统上下文图（ZephyrAlpha + 外部系统）|
| c4-l2-containers.mmd | C4 Level 2 容器图（四大运行时容器）|
| c4-l3-l00-data-source.mmd | C4 Level 3 L00 数据源组件图 |
| c4-l3-l11-ml-platform.mmd | C4 Level 3 L11 ML 平台组件图 |
| c4-l3-l06-trade-execution.mmd | C4 Level 3 L06 交易执行组件图 |

### 拓扑图

| 文件 | 说明 |
|------|------|
| togaf-layer-stack.mmd | TOGAF 四层堆叠图（BA → IA → AA → TA）|
| src-layer-stack.mmd | src/zephyr/ 14 层分层图（L00-L13）|
| docs-drawer-topology.mmd | docs/ 抽屉拓扑图 |
| scripts-topology.mmd | scripts/ 治理代码拓扑图 |
| frontend-mfe-topology.mmd | 前端微前端拓扑（Module Federation Host + 4 Apps）|
| integration-topology.mmd | 集成拓扑图（外部系统 + 内部层 + EI 契约编号）|
| runtime-topology.mmd | 运行时拓扑（主进程内 L00-L13 数据流 + 外部系统）|
| runtime-planes-topology.mmd | Runtime Planes 三平面物理拓扑（Hot / Warm / Cold）|
| view-dependencies.mmd | 视图间依赖关系图（BA/IA/AA/TA/DA/INTEG/SEC/OPS）|
| readme-view-dependency-graph.mmd | README 视图依赖图（10视图 + 2正交视图节点关系）|

### 数据流图

| 文件 | 说明 |
|------|------|
| business-value-stream.mmd | 业务价值流图（市场假设→研究→信号→组合→执行→监控闭环）|
| data-flow.mmd | 跨域核心数据流图 |
| dataflow-terminal.mmd | 终端数据流全景图（外部系统→L00→L02-L13→外部系统）|
| deployment-experimental.mmd | experimental 部署拓扑（开发机单进程 + 本地存储）|
| frontend-build-pipeline.mmd | 前端构建流水线（changeset→CI→lint→test→build→publish）|

### 序列图

| 文件 | 说明 |
|------|------|
| seq-order-submit.mmd | 订单提交端到端时序（正常 / Retry 幂等 / Broker failover）|
| seq-fill-received.mmd | 成交回报处理时序（Order→Position→PnL→Risk→Strategy）|
| seq-risk-trigger.mmd | 风控触发三阶段时序（Pre-trade / At-trade / Post-trade）|
| seq-rebalance.mmd | 组合再平衡流程时序（Scheduler→数据准备→策略→融合→Risk→Optimizer→批量下单）|
| seq-exception-handling.mmd | 异常处置三场景时序（Vendor 故障 / Broker 断连 / 策略异常）|

### 治理

| 文件 | 说明 |
|------|------|
| governance-d2b-loop.mmd | 治理 Design-to-Build 闭环（Policy→Factory→Runtime→Audit）|
| governance-three-layers.mmd | 治理三层边界拓扑（被治理者 + Policy/Factory/Runtime）|
| governance-activation-gantt.mmd | 治理架构激活甘特图（Sprint 9/10/11/T4 方案B）|
| capability-heatmap-visual.mmd | 能力成熟度热力图可视化（14层 × 7能力域 L0-L5）|

## 排除规则

- ❌ 非 Mermaid 图表（.png/.svg）→ 由 .mmd 渲染生成，不入库
- ❌ 图表使用说明 → target-architecture/index.md §6

## 父级目录

- 父级：[target-architecture/index.md](../index.md)
