---
module_id: MOD-TRADING-015
title: "交易决策地图蓝图 — 决策链真源加载与引用校验"
doc_type: blueprint
status: Active
version: "0.1.1"
ttl: permanent
layer: L03_trading
layer_name: trading
functional_domain: trading
owner: ZephyrAlpha-Owner
created_by: agent
date: "2026-09-04"
last_updated: "2026-09-04"
priority: P1
blueprint_level: module
responsibility_domain: 
design_maturity: production
build_status: production
---

# MOD-TRADING-015 Trading Decision Map — 交易决策地图 蓝图

> **module_id**: MOD-TRADING-015 | **域**: D_TRADING | **层**: L03 交易运营
> **优先级**: P1 | **成熟度**: design（worktree 外直接施工，验收后转 production）
> **设计真源**: [69_trading_decision_map.md](../../../02_enterprise_architecture/07_trading_decision_architecture/design_memos/69_trading_decision_map.md)（Owner D1-D6 裁定）

## 1. 定位

交易决策地图 V0 后端骨架——决策内容索引层（项目第 7 张地图性质）。回答"**什么市场情况、在决策链哪个环节、用哪个策略/因子、靠哪些数据、由哪段代码实现**"。

与既有六图分工：六图管"系统怎么运转"（工程视图），本模块管"钱怎么赚"（决策内容视图）。地图自身**不复制内容**：决策链环节骨架是唯一新增真源（config/trading_decision_map.yaml），策略/因子/数据/模块四层全部按稳定标识符（STR-*/FCT-*/DS-*/MOD-*）引用既有注册表。

**纯函数库：load → validate → GapReport，无运行时状态、无常驻进程。**

## 2. 输入 / 输出

| 方向 | 内容 | 契约 |
|------|------|------|
| 输入 | config/trading_decision_map.yaml（决策链真源） | 本模块定义 schema v1.0 |
| 输入 | docs/01_policies_and_standards/_registry/catalogs/{strategy,factor,data_asset}_registry.yaml | 只读引用校验 |
| 输出 | DecisionMap（不可变 dataclass：nodes/edges/state_matrix/markets） | load_decision_map() |
| 输出 | (bool, list[GapReportItem])（引用缺口报告） | validate_decision_map() |
| 异常 | DecisionMapSchemaError（结构错误） | load 阶段 |

## 3. 核心规则

### 3.1 校验规则（R1-R8）

- R1 节点结构：必填字段+枚举（market: cn_a|crypto；flow: entry_flow|position_flow|exit_flow；node_type: gate|stage|sensor|aggregation|cross_cutting；point: 盘前|盘中|盘后|持续）
- R2 边端点存在性 + edge_type 枚举（sequence|broadcast|feedback）
- R3 strategy_ref 存在性（REG-STR-001 entries[].strategy_id，STR-*）
- R4 factor_refs 存在性（REG-FCT-001 entries[].factor_id，FCT-*）
- R5 data_refs 存在性（REG-DATAFLOW-001 datasets[].dataset_id，DS-*）
- R6 strategy_mounts.confidence 枚举（verified|proposed|untested）+ verified 必带 evidence
- R7 state_matrix.cells 引用环节与策略存在性
- R8 sequence 边无环（有依赖的地图才能推理，成环=骨架错误）

缺口分级：引用不存在=error；module_ref 缺失=warning（V0 允许，缺口可视化输入，对应地图"红节点"语义）。

### 3.2 三流骨架（真源内容约定）

建仓流 L1-L4（内嵌 Owner 漏斗：大盘总闸→板块→个股→买卖点）+ 持仓流 P1-P3（三个做T策略挂载 P2）+ 离场流 S1-S2 + 风控横切 X。L1=四路传感器阵列（指数/内部结构/赚钱效应/波动率可选）汇聚市场状态判定。双市场同 schema（cn_a 全量，crypto 空壳）。

## 4. 依赖

| 依赖 | 类型 | 说明 |
|------|------|------|
| PyYAML | 外部库 | safe_load |
| strategy_registry.yaml | 数据（只读） | REG-STR-001 |
| factor_registry.yaml | 数据（只读） | REG-FCT-001 |
| data_asset_registry.yaml | 数据（只读） | REG-DATAFLOW-001 |

无 zephyr 内部模块依赖（V0）；V1 API 端点为消费方单向依赖本模块。

## 5. 不变量（INVARIANTS）

- INV-1：地图 YAML 不复制任何注册表条目内容，只持稳定标识符引用
- INV-2：load 产出的 DecisionMap 全部 frozen dataclass（防消费方篡改）
- INV-3：validate 纯函数（同输入同输出，无副作用）
- INV-4：error=0 才可被下游（V1 API）视为可消费真源

## 6. 测试

tests/trading/test_decision_map.py：正常加载/schema 错误/三类引用缺口/module_ref warning/成环检测/verified-evidence 联动/仓库真源自检（加载真实 config/trading_decision_map.yaml 校验全绿——防真源漂移回归锚）。

### §0.6 五图对齐视图

<!-- AUTOGEN: source=depgraph+dataflow+decision, generator=generate_blueprint_panorama.py, reconciler=sync_panorama_module.py -->

> **自动生成**：本节由 generate_blueprint_panorama.py 从全景真源派生，禁止手写。
> 生成命令：`python scripts/governance/d5_architecture/generators/generate_blueprint_panorama.py MOD-TRADING-015`

#### 全景位置

| 图 | 位置 | 状态 | 链接 |
|----|------|------|------|
| 依赖图 (depgraph) | `blueprint_id=MOD-TRADING-015` 的 2 个 file 节点 | production | `extract_depgraph.py --modules MOD-TRADING-015` |
| 数据流图 (dataflow) | 0 个 Dataset / 1 个 Job | active | `apply_dataflowgraph.py --list-datasets` |
| 决策架构图 (decision) | 0 个决策节点 / 1 个决策层 | N/A | `generate_decision_diagram.py` |
| 蓝图 (blueprint) | 本文件 | Active | — |

#### 四核心字段

| 字段 | depgraph 值（真源） | 蓝图 frontmatter 值（声明） | 是否一致 |
|------|-------------------|--------------------------|:-------:|
| module_id | MOD-TRADING-015 | MOD-TRADING-015 | ✅ |
| domain_id | N/A | N/A | ✅ |
| build_status | production | production | ✅ |
| file_count | 2 文件 | N/A | — |

> 冲突时以 depgraph 为准（ARCH-056 + ARCH-MM-001 声明 vs 验证框架）。

---

## 7. 已实现代码完整路径索引

> **AGENTS.md §6.1 蓝图-代码同步强制约定**——本节是蓝图与磁盘代码的「地址簿」。
> 蓝图声称的文件必须与磁盘实际一致。不一致 = 蓝图漂移 = 下一个 AI session 冷启动时被误导。
> **AUTOGEN**：本表由 sync_blueprint_code_index.py 从 depgraph.nodes 运营态（build_status∈generated/testing/stable）单向派生，禁止手写；重跑本脚本幂等更新。
> 

### 7.1 测试文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `tests/trading/test_decision_map.py` | ✅ 已实现 | |

### 7.5 路径索引使用指南

**新 AI session 读取顺序**：
1. 读本蓝图 §7（本节）→ 知道「哪些已实现、在哪里」
2. 读模块分解 → 知道「每个模块的职责和 AI 自治权限」
3. 读施工 Phase 规划 → 知道「下一步该做什么」

**路径约定**：
- 所有路径相对于 `D:\ZephyrAlpha\\`
- 源码在 `src/zephyr/` 下
- 测试在 `tests/` 下
- 配置在 `config/` 下
- 治理脚本在 `scripts/governance/` 下
