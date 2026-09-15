---
module_id: MOD-POS-029
title: "仓位配方编译器蓝图 — F-06 网格 schema 一次定型+活性谓词折叠+内容寻址出生证"
doc_type: blueprint
status: Active
version: "0.1.1"
design_maturity: production
ttl: permanent
layer: L03_position
layer_name: position
functional_domain: position
owner: ZephyrAlpha-Owner
created_by: agent
date: "2026-09-15"
last_updated: "2026-09-15"
priority: P0
blueprint_level: module
responsibility_domain: 
---

# MOD-POS-029 Position Recipe Compiler — 仓位配方编译器 蓝图

> **module_id**: MOD-POS-029 | **域**: D_POSITION | **层**: L03 仓位管理
> **优先级**: P0 | **成熟度**: design（雏形，F-06 第一期） | **建设标记**: ✅已建（design 态）
> **SSoT**: depgraph MOD-POS-029 | **设计真源**: `docs/_working/2026-09-14-combination-layer-exhaustive-charter.md` §十/§十二 + `docs/_working/2026-09-14-full-chain-factory-blueprint.md` §十（活性谓词机制）
> **schema 真源**: `config/position_recipe_grid_schema.yaml`（v2 十三维，F/J/K 休眠）

## 1. 定位

F-06 组合层穷尽网格的**编译器雏形**——把「维度 schema + 求值上下文」确定性编译为
`PositionRecipe` 候选全集。对应全链路方案五部件中的 **C 编译器**（蓝图 §8.1）在 F-06 域的
第一个实例化；接口按通用件设计，待第二个消费者（F-02 因子工厂接线）出现才提炼通用件
（蓝图裁定 §十一-8）。

**边界**: 不执行回测（批次 A 执行器职责）；不评分（判定权在 E4/E5）；不落库
（recipe 落 `data/strategy_intake/` 属执行器）；signal 前缀共享只做分组键
（`prefix_key`），缓存引擎属执行器。

## 2. 机制（三铁律 → 三能力）

| 铁律（蓝图 §8.2） | 本模块实现 |
|---|---|
| Schema 一次定型，执行分期 | `DimensionSpec`/`from_yaml`——维度存在性写死在 schema 真源 |
| 退化维由编译器折叠，不被人裁剪 | `active_if` 受控求值（白名单内建，异常 fail-closed=ZA-POS-0045）→ 折叠为 `baseline` |
| 失活维对 N 贡献 = 1 | `count_n_raw`（O(维数) 预算）与 `compile().n_raw` 同口径 |

机制出处：条件/树结构参数空间（SMAC 2011 / TPE 2011 / Add-Tree 2017；蓝图附录 A-C1，
内部反查查无→属新建）。验收锚已锁进测试：立项稿 §十 名义 N=362,880（F/J/K 折叠）、
全激活 N=11,612,160。

## 3. 输入 / 输出

**输入**: ① schema（dict list / YAML）② context（`strategy_pool`/`phase`/`capital_ramp_enabled`，
谓词可引用；未提供谓词所需键=fail-closed）。

**输出**: `GridExpansion`——recipes（每条带 `recipe_id`=sha1(规范取值)[:12] 内容寻址出生证、
全维取值、`folded_dimensions` 折叠记录、`prefix_key` signal 侧分组键）+ `n_raw` N 记账 +
`schema_digest`。

## 4. ALGO_FLOW

```
I1 schema(dict/YAML) → A1 校验(id 重复/baseline∈values/depends_on 无环/依赖已声明)
I2 context → A2 拓扑排序+逐维 active_if 受控求值(白名单, fail-closed)
A2 → A3 失活维折叠为 baseline; A4 活跃维笛卡尔积展开; A5 内容寻址+prefix_key 分组
A3-A5 → O1 GridExpansion(recipes/n_raw/folded/schema_digest)
```

## 5. 不变量（INVARIANTS）

同 schema+context 编译结果确定性（recipe_id 集合相等）；失活维贡献=1；谓词求值受控命名
空间（`len/abs/min/max/sum/int/float/bool/round` 白名单）异常 fail-closed；编译器内部零时钟
取用（时间戳由调用方盖）；`estimate_max_z` 与官方件 `deflated_sharpe_calculator` 同公式，
唯真源仍是官方件（本方法只服务网格预算预览）。

## 6. 消费者与后续

| 消费方 | 状态 |
|---|---|
| F-06 批次 A 执行器（正交表/分层抽样 ~2 万条） | planned（立项稿 §十二） |
| E2 预审（position_recipe 候选面，落 data/strategy_intake/） | planned |
| N 账本（G 部件，累计口径） | planned（批次 B 硬前置，裁定记录） |

## 7. 测试

`tests/position/test_position_recipe_compiler.py` 12 项：折叠计数/确定性/fail-closed 三铁律
+ prefix_key 分组 + 官方件 E[max] 对齐 + 立项稿 §十 数字断言。

### §0.6 五图对齐视图

<!-- AUTOGEN: source=depgraph+dataflow+decision, generator=generate_blueprint_panorama.py, reconciler=sync_panorama_module.py -->

> **自动生成**：本节由 generate_blueprint_panorama.py 从全景真源派生，禁止手写。
> 生成命令：`python scripts/governance/d5_architecture/generators/generate_blueprint_panorama.py MOD-POS-029`

#### 全景位置

| 图 | 位置 | 状态 | 链接 |
|----|------|------|------|
| 依赖图 (depgraph) | `blueprint_id=MOD-POS-029` 的 1 个 file 节点 | production | `extract_depgraph.py --modules MOD-POS-029` |
| 数据流图 (dataflow) | 0 个 Dataset / 1 个 Job | active | `apply_dataflowgraph.py --list-datasets` |
| 决策架构图 (decision) | 0 个决策节点 / 1 个决策层 | N/A | `generate_decision_diagram.py` |
| 蓝图 (blueprint) | 本文件 | Active | — |

#### 四核心字段

| 字段 | depgraph 值（真源） | 蓝图 frontmatter 值（声明） | 是否一致 |
|------|-------------------|--------------------------|:-------:|
| module_id | MOD-POS-029 | MOD-POS-029 | ✅ |
| domain_id | N/A | N/A | ✅ |
| build_status | stable | N/A | — |
| file_count | 1 文件 | N/A | — |

> 冲突时以 depgraph 为准（ARCH-056 + ARCH-MM-001 声明 vs 验证框架）。

---

## 8. 已实现代码完整路径索引

> **AGENTS.md §6.1 蓝图-代码同步强制约定**——本节是蓝图与磁盘代码的「地址簿」。
> 蓝图声称的文件必须与磁盘实际一致。不一致 = 蓝图漂移 = 下一个 AI session 冷启动时被误导。
> **AUTOGEN**：本表由 sync_blueprint_code_index.py 从 depgraph.nodes 运营态（build_status∈generated/testing/stable）单向派生，禁止手写；重跑本脚本幂等更新。
> 

### 8.1 源码文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `src/zephyr/position/core/position_recipe_compiler.py` | ✅ 已实现 | |

### 8.5 路径索引使用指南

**新 AI session 读取顺序**：
1. 读本蓝图 §8（本节）→ 知道「哪些已实现、在哪里」
2. 读模块分解 → 知道「每个模块的职责和 AI 自治权限」
3. 读施工 Phase 规划 → 知道「下一步该做什么」

**路径约定**：
- 所有路径相对于 `D:\ZephyrAlpha\\`
- 源码在 `src/zephyr/` 下
- 测试在 `tests/` 下
- 配置在 `config/` 下
- 治理脚本在 `scripts/governance/` 下
