---
module_id: MOD-POS-029
title: "仓位配方编译器蓝图 — F-06 网格 schema 一次定型+活性谓词折叠+内容寻址出生证"
doc_type: blueprint
status: Active
version: "0.1.0"
design_maturity: design
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
responsibility_domain: position
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
