---
module_id: MOD-SIG-138
title: "环境开关蓝图 — 六段状态×链启停查表"
doc_type: blueprint
status: Active
version: "0.1.2"
design_maturity: production
ttl: permanent
layer: L05_signal
layer_name: signal
functional_domain: signal
owner: ZephyrAlpha-Owner
created_by: agent
date: "2026-09-11"
last_updated: "2026-09-11"
priority: P0
blueprint_level: module
responsibility_domain: 
---

# MOD-SIG-138 Environment Switch — 环境开关查表 蓝图

> **module_id**: MOD-SIG-138 | **域**: D_ASHARE_SIGNAL | **消费节点**: TDM-E-L3-06；下游=L3-07 策略专属链启停（待接线）
> **出身**：晨审 st-tdm-review-20260911 §7.1 "确认查无，立缺口"；Owner 2026-09-11 夜班令"除币圈外开工"立项。

## 1. 查表语义（节点 TDM-E-L3-06 algo_note 逐条对码）

输入两个数查一张静态表，输出今天哪些链开哪些停：

1. **地量关首板**：两市成交额 < 8000 亿 → 首板筛选器停（实证：地量首板次日溢价为负）——任何情绪档位叠加此条；
2. **冰点停短线**：capitulation（冰点）→ 短线链全停只留波段链；
3. **疯狂反向收紧**：euphoria（极端高潮）→ tighten_risk=True（压仓位上限/提门槛，不止链）；
4. **退潮收短线**：distribution → 收短线留波段；
5. 其余档位（accumulation/ignition/expansion）→ 全开。

状态键=地图 state_matrix 六段列轴（capitulation/accumulation/ignition/expansion/euphoria/distribution）；
与 sentiment_cycle.SentimentPhase 五阶段的归并映射由调用方负责，本件只认六段封闭集。

## 2. 阈值（proposed，待实盘标定）

- LOW_TURNOVER_THRESHOLD_YI = 8000.0 亿（节点真源）；
- 开关表 6 行×4 列封闭（代码 `_SWITCH_TABLE`），查表静态可审计。

## 3. 查重分工

晨审实证：STRATEGY_DEPLOYMENT_MATRIX（3 策略×5 阶段）仅部分承载，"成交<8000 亿首板链停"
类环境开关查无专件。本件与 sentiment_cycle 正交：彼=情绪档推导（L2-05-1），此=档→链启停查表（L3-06）。

### §0.6 五图对齐视图

<!-- AUTOGEN: source=depgraph+dataflow+decision, generator=generate_blueprint_panorama.py, reconciler=sync_panorama_module.py -->

> **自动生成**：本节由 generate_blueprint_panorama.py 从全景真源派生，禁止手写。
> 生成命令：`python scripts/governance/d5_architecture/generators/generate_blueprint_panorama.py MOD-SIG-138`

#### 全景位置

| 图 | 位置 | 状态 | 链接 |
|----|------|------|------|
| 依赖图 (depgraph) | `blueprint_id=MOD-SIG-138` 的 1 个 file 节点 | production | `extract_depgraph.py --modules MOD-SIG-138` |
| 数据流图 (dataflow) | （无节点） | N/A | `apply_dataflowgraph.py --list-datasets` |
| 决策架构图 (decision) | 0 个决策节点 / 1 个决策层 | N/A | `generate_decision_diagram.py` |
| 蓝图 (blueprint) | 本文件 | Active | — |

#### 四核心字段

| 字段 | depgraph 值（真源） | 蓝图 frontmatter 值（声明） | 是否一致 |
|------|-------------------|--------------------------|:-------:|
| module_id | MOD-SIG-138 | MOD-SIG-138 | ✅ |
| domain_id | N/A | N/A | ✅ |
| build_status | stable | N/A | — |
| file_count | 1 文件 | N/A | — |

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
| `src/zephyr/signal_ashare/core/environment_switch.py` | ✅ 已实现 | |

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


