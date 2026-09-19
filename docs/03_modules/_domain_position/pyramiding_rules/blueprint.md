---
module_id: MOD-POS-027
title: "金字塔加仓规则蓝图 — 资格四重门+递减阶梯限次"
doc_type: blueprint
status: Active
version: "0.1.5"
design_maturity: production
ttl: permanent
layer: L03_position
layer_name: position
functional_domain: position
owner: ZephyrAlpha-Owner
created_by: agent
date: "2026-09-10"
last_updated: "2026-09-10"
priority: P0
blueprint_level: module
responsibility_domain: 
---

# MOD-POS-027 Pyramiding Rules — 加仓资格门+金字塔规则 蓝图

> **module_id**: MOD-POS-027 | **域**: D_POSITION | **消费节点**: TDM-P-P3-01/P3-02
> **CORE-ALGORITHM**: 是（晨审重点：递减比例/总上限/禁补亏损仓红线）

## 1. P3-01 加仓资格四重门（全过才进规则层）
①只加浮盈仓（现价>成本；**禁补亏损仓=红线**，平价也拒）；②情绪段权限
（点火/扩张才开，退潮/亢奋/冰点关）；③策略亲和度>0；④非熔断禁加期
（L2/L3/L4 全禁——熔断期买入走 MOD-POS-026 护盘白名单窄门，正交）。

## 2. P3-02 金字塔三规则
递减：首加=剩余预算×1/2，逐次减半（越加越少防重仓在顶部）；
阶梯：较上次买价涨幅 ≥2.5%（2.5-3% 区间取下限）才加，禁止平加；
限次：最多 3 次。跌破上次加仓价=停止后续计划；加仓=新交易须重新确认入场条件。

## 3. 查重分工
defensive_asset_whitelist=熔断期护盘窄门（特例通道）；position_sizing_engine=
首仓 sizing；本件=P3 链常态金字塔加仓。

### §0.6 五图对齐视图

<!-- AUTOGEN: source=depgraph+dataflow+decision, generator=generate_blueprint_panorama.py, reconciler=sync_panorama_module.py -->

> **自动生成**：本节由 generate_blueprint_panorama.py 从全景真源派生，禁止手写。
> 生成命令：`python scripts/governance/d5_architecture/generators/generate_blueprint_panorama.py MOD-POS-027`

#### 全景位置

| 图 | 位置 | 状态 | 链接 |
|----|------|------|------|
| 依赖图 (depgraph) | `blueprint_id=MOD-POS-027` 的 2 个 file 节点 | production | `extract_depgraph.py --modules MOD-POS-027` |
| 数据流图 (dataflow) | 0 个 Dataset / 1 个 Job | active | `apply_dataflowgraph.py --list-datasets` |
| 决策架构图 (decision) | 0 个决策节点 / 1 个决策层 | N/A | `generate_decision_diagram.py` |
| 蓝图 (blueprint) | 本文件 | Active | — |

#### 四核心字段

| 字段 | depgraph 值（真源） | 蓝图 frontmatter 值（声明） | 是否一致 |
|------|-------------------|--------------------------|:-------:|
| module_id | MOD-POS-027 | MOD-POS-027 | ✅ |
| domain_id | N/A | N/A | ✅ |
| build_status | stable | N/A | — |
| file_count | 2 文件 | N/A | — |

> 冲突时以 depgraph 为准（ARCH-056 + ARCH-MM-001 声明 vs 验证框架）。

---

## 4. 已实现代码完整路径索引

> **蓝图-代码同步强制约定**（稳定锚：AGENTS.md RULE-DEPGRAPH / RULE-PANORAMA；验证端 validate_blueprint_code_sync.py）——本节是蓝图与磁盘代码的「地址簿」。
> 蓝图声称的文件必须与磁盘实际一致。不一致 = 蓝图漂移 = 下一个 AI session 冷启动时被误导。
> **AUTOGEN**：本表由 sync_blueprint_code_index.py 从 depgraph.nodes 运营态（build_status∈generated/testing/stable）单向派生，禁止手写；重跑本脚本幂等更新。
> 

### 4.1 源码文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `src/zephyr/position/core/pyramiding_rules.py` | ✅ 已实现 | |

### 4.2 测试文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `tests/position/test_pyramiding_rules.py` | ✅ 已实现 | |

### 4.5 路径索引使用指南

**新 AI session 读取顺序**：
1. 读本蓝图 §4（本节）→ 知道「哪些已实现、在哪里」
2. 读模块分解 → 知道「每个模块的职责和 AI 自治权限」
3. 读施工 Phase 规划 → 知道「下一步该做什么」

**路径约定**：
- 所有路径相对于仓库根目录（REPO_ROOT，不写死盘符绝对路径）
- 源码在 `src/zephyr/` 下
- 测试在 `tests/` 下
- 配置在 `config/` 下
- 治理脚本在 `scripts/governance/` 下


