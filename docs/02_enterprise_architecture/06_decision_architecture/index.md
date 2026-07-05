# 决策流图架构（decisiongraph）索引

> 真源: `architecture_model/domain/decision_graph_model.yaml` → PostgreSQL `decision_*` 表
> 数据库: depgraph (PostgreSQL)（与 depgraph 共享实例，不同表前缀 `decision_*`）
> 创建日期: 2026-07-06
> 版本: 1.0.0

## 概述

决策流图（decisiongraph）是与依赖图（depgraph）、数据流图（dataflowgraph）正交的第三维度全景图。

| 全景图 | 维度 | 表达 | 物理实现 |
|--------|------|------|----------|
| depgraph | 模块依赖 | "谁依赖谁"（静态） | `depgraph.nodes` / `depgraph.edges` |
| dataflowgraph | 数据流 | "数据从哪流到哪"（动态） | `dataflow_datasets` / `dataflow_jobs` / `dataflow_edges` |
| **decisiongraph** | **决策流** | **"决策如何产生"（动态）** | **`decision_layers` / `decision_nodes` / `decision_edges` / `decision_tracks`** |

三张图通过 `module_id` 关联：决策节点 → 实现模块（depgraph）→ 数据流作业（dataflowgraph）。

## 设计模式与运营态

| 模式 | 别名 | 用途 | build_status |
|------|------|------|--------------|
| 设计态 | design | 规划中/未实现的决策节点 | `planned` / `generated` / `testing` |
| 运营态 | production | 已通过测试、生产就绪的决策节点 | `stable` |
| 终态 | - | 已弃用，不可再迁移 | `deprecated` |

状态机（单调推进，禁止跳态）:
```
planned → generated → testing → stable → deprecated
```

## Mermaid 图表

### 全景图
- [decision_graph_overview.mmd](decision_graph_overview.mmd) — L0-L6 决策流水线全景 + 四轨并行架构

### 决策层
- [decision_layers.mmd](decision_layers.mmd) — 10 层决策层（L0-L6，含 build_status 颜色）

### 不变量与状态机
- [decision_invariants.mmd](decision_invariants.mmd) — 五条承重墙不变量 + build_status 状态机 + 4 种边类型

## 统计

| 类型 | 数量 | 说明 |
|------|------|------|
| 四轨 (tracks) | 4 | model_driven / data_driven / human_override / emergency |
| 决策层 (layers) | 10 | L0, L1, L2A, L2B, L2C, L2D, L3, L4, L5, L6 |
| 节点类型 (node_types) | 6 | signal / portfolio_target / risk_check / order / compliance_check / sell_decision |
| 边类型 (edge_types) | 4 | triggering / informing / constraining / approving |
| 不变量 (invariants) | 5 | DEC-INV-001~005 |

## 四轨定义

| track_id | 轨名 | 优先级 | 激活条件 |
|----------|------|--------|----------|
| model_driven | 模型驱动轨 | 1 | 正常运行时 |
| data_driven | 数据驱动轨 | 2 | 模型驱动轨信号不足时补充 |
| human_override | 人工指令轨 | 3 | 人工干预时 |
| emergency | 应急保命轨 | 4 | 所有模型/策略/信号失效时 |

## 决策层清单（L0-L6）

| layer_id | 层名 | 轨 | 决策频率 | design_maturity | build_status |
|----------|------|----|----------|-----------------|--------------|
| L0 | 数据接入与预处理层 | model_driven | tick | production | stable |
| L1 | 因子计算层 | model_driven | daily | production | stable |
| L2A | 信号层 | model_driven | daily | design | planned |
| L2B | 主力行为层 | model_driven | daily | design | planned |
| L2C | 市场状态与大盘预测层 | model_driven | daily | design | planned |
| L2D | 知识图谱与因果推演层 | model_driven | daily | design | planned |
| L3 | 策略组合层 | model_driven | daily | design | planned |
| L4 | 风控层 | model_driven | realtime | production | stable |
| L5 | 学习层 | model_driven | weekly | design | planned |
| L6 | 自评估层 | model_driven | weekly | design | planned |

## 决策节点类型

| 类型 | 名称 | 输出契约 | 归属层 | DMN 等价 | 特殊能力 |
|------|------|----------|--------|----------|----------|
| signal | 信号节点 | Insight | L2A | Decision | 禁止直连 order |
| portfolio_target | 组合目标节点 | PortfolioTarget | L3 | Decision | - |
| risk_check | 风控检查节点 | RiskDecision | L4 | Decision | **veto（一票否决）** |
| order | 订单节点 | Order | L3 | Decision | 需 risk_check approving 入边 |
| compliance_check | 合规检查节点 | ComplianceDecision | L4 | Decision | - |
| sell_decision | 卖出决策节点 | SellDecision | L2A | Decision | 禁止直连 order |

## 决策边类型

| 类型 | 名称 | 语义 | DMN 等价 | 示例 |
|------|------|------|----------|------|
| triggering | 触发边 | u 直接触发 v 的创建 | Information Flow | risk_breach --triggering--> portfolio_rebalance |
| informing | 数据流入边 | u 的输出是 v 的输入数据 | Information Flow | market_state --informing--> portfolio_target |
| constraining | 约束边 | u 施加约束限制 v 的行动空间 | Knowledge Source | compliance_policy --constraining--> order |
| approving | 审批边 | u 审批授权 v 继续 | Knowledge Source | risk_check --approving--> order |

## 五条承重墙不变量

| ID | 名称 | 描述 | 约束位置 | 违规动作 |
|----|------|------|----------|----------|
| DEC-INV-001 | 风控一票否决 | order 节点必须有至少一条 approving 入边来自 risk_check | DB trigger | reject_insert |
| DEC-INV-002 | 信号仓位分离 | signal 节点不能直接连 order 节点 | DB CHECK | reject_insert |
| DEC-INV-003 | DAG 无环 | 图中不能有环（反馈循环用螺旋结构） | Tarjan SCC | reject_graph |
| DEC-INV-004 | 时间单调性 | forall (u,v) in E, tau(u) <= tau(v) | DB CHECK | reject_insert |
| DEC-INV-005 | 证据哈希必填 | 每个节点必须有 evidence_hash | DB NOT NULL | reject_insert |

## 程序化访问

| 脚本 | 用途 | 模式 |
|------|------|------|
| `scripts/governance/extract_decisiongraph.py` | 只读查询（summary/layers/nodes/edges/tracks/invariants/stats） | 读 |
| `scripts/governance/apply_decisiongraph.py` | 写入设计态节点/边 + 状态迁移 | 写（pg_advisory_lock=424244） |
| `scripts/governance/generate_decision_graph.py` | YAML→DB 同步（tracks + layers） | 写（--dry-run/--force/--validate-only） |
| `src/zephyr/governance/persistence/decision_graph_reader.py` | DecisionGraphReader 类（30+ 查询方法） | 读 |

## 关联

- **SSoT**: `architecture_model/domain/decision_graph_model.yaml`
- **Schema**: `src/zephyr/governance/persistence/decisiongraph_schema.py`
- **DDL**: `scripts/governance/migrate_sqlite_to_pg/03_create_decision_schema.sql`
- **词表**: `docs/01_policies_and_standards/_registry/vocabularies/decision_edge_type_vocabulary.yaml`
- **蓝图**: `docs/03_modules/_domain_governance/blueprint.md` §decision-graph
