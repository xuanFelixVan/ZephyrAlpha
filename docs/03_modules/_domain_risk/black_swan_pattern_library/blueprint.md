---
module_id: MOD-RK-31
title: "C-038 黑天鹅模式库蓝图 — 7 模式特征模板+事前相似度匹配→提前降仓并触发 C-004 MVP"
doc_type: blueprint
status: Active
version: "0.1.1"
ttl: permanent
layer: L02_risk
layer_name: risk
functional_domain: risk
owner: ZephyrAlpha-Owner
created_by: agent
date: "2026-08-25"
last_updated: "2026-08-25"
priority: P0
blueprint_level: module
blueprint_id: MOD-RK-31
domain_id: D_RISK
path: src/zephyr/risk/core/black_swan_pattern_library.py
design_maturity: production
build_status: stable
granularity: file
ai_autonomy: ai_modifiable
safety: H
stability: evolving
responsibility_domain: 
---

# MOD-RK-31 C-038 黑天鹅模式库（Black Swan Pattern Library）蓝图

> **module_id**: MOD-RK-31 | **域**: D_RISK | **来源**: CAND-RSK-032（B1-00175，P0 波 W1c）

## 1. 定位

7 种黑天鹅模式（BS-001~BS-007）**事前**特征模板库：把当前市场体征（波动率倍数/
回撤/相关性/流动性萎缩/跳空/跌停潮/外围跌幅）与 7 个模式模板做加权相似度匹配，
超阈值 → 提前降仓建议；命中模式 ≥2（或显式 BS-007）→ `escalate_to_c004=True`
升级触发 C-004（MOD-RK-30，KILL_SWITCH 建议语义）。匹配记录以纯数据产出
（审计持久化由调用方完成）。

**与存量分工（不复制）**：
- 模式枚举唯一真源 = MOD-POS-008 drawdown_controller.BlackSwanMode（import 复用）；
- drawdown_controller 管**事中**响应（信号已触发 → cap 查表），本库管**事前**
  相似度匹配（特征逼近模板 → 提前降仓）；≥2 模式命中=BS-007 的语义两侧一致。

## 2. 输入 / 输出

| 方向 | 内容 | 契约 |
|------|------|------|
| 输入 | MarketFeatures（7 维体征，非负有限） | frozen dataclass |
| 输出 | BlackSwanScreenResult(matches/escalate_to_c004/suggested_position_scale/matching_log) | frozen dataclass |

## 3. 核心规则

1. 模板结构：每模式 = 特征权重表 + 参考水平 + 阈值 + 降仓建议（suggested_position_scale）。
2. 相似度：`score = Σ w_i·clamp(f_i/r_i, 0, 1) / Σ w_i`；score ≥ threshold → matched。
3. 升级规则：matched 数 ≥2 或 BS-007 命中 → escalate_to_c004=True
   （与 BlackSwanSignal.has_black_swan 语义对齐）。
4. 综合降仓建议 = 命中模式中最低 suggested_position_scale（最严）。
5. 纯函数无 IO；Fail-Closed 输入校验（InvalidMarketFeaturesError /
   InvalidBlackSwanConfigError）。

## 4. 依赖

| 依赖 | 模块 | 类型 |
|------|------|------|
| 模式枚举 | MOD-POS-008 drawdown_controller（BlackSwanMode） | import_depends |
| 升级触发 | MOD-RK-30 adaptive_risk_coordinator | 设计边（消费方接线） |

### §0.6 五图对齐视图

<!-- AUTOGEN: source=depgraph+dataflow+decision, generator=generate_blueprint_panorama.py, reconciler=sync_panorama_module.py -->

> **自动生成**：本节由 generate_blueprint_panorama.py 从全景真源派生，禁止手写。
> 生成命令：`python scripts/governance/d5_architecture/generators/generate_blueprint_panorama.py MOD-RK-31`

#### 全景位置

| 图 | 位置 | 状态 | 链接 |
|----|------|------|------|
| 依赖图 (depgraph) | `blueprint_id=MOD-RK-31` 的 2 个 file 节点 | production | `extract_depgraph.py --modules MOD-RK-31` |
| 数据流图 (dataflow) | （无节点） | N/A | `apply_dataflowgraph.py --list-datasets` |
| 决策架构图 (decision) | 0 个决策节点 / 1 个决策层 | N/A | `generate_decision_diagram.py` |
| 蓝图 (blueprint) | 本文件 | Active | — |

#### 四核心字段

| 字段 | depgraph 值（真源） | 蓝图 frontmatter 值（声明） | 是否一致 |
|------|-------------------|--------------------------|:-------:|
| module_id | MOD-RK-31 | MOD-RK-31 | ✅ |
| domain_id | N/A | N/A | ✅ |
| build_status | stable | stable | ✅ |
| file_count | 2 文件 | N/A | — |

> 冲突时以 depgraph 为准（ARCH-056 + ARCH-MM-001 声明 vs 验证框架）。

---

## 5. 已实现代码完整路径索引

> **AGENTS.md §6.1 蓝图-代码同步强制约定**——本节是蓝图与磁盘代码的「地址簿」。
> 蓝图声称的文件必须与磁盘实际一致。不一致 = 蓝图漂移 = 下一个 AI session 冷启动时被误导。
> **AUTOGEN**：本表由 sync_blueprint_code_index.py 从 depgraph.nodes 运营态（build_status∈generated/testing/stable）单向派生，禁止手写；重跑本脚本幂等更新。
> 

### 5.1 源码文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `src/zephyr/risk/core/black_swan_pattern_library.py` | ✅ 已实现 | |

### 5.2 测试文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `tests/risk/test_black_swan_pattern_library.py` | ✅ 已实现 | |

### 5.5 路径索引使用指南

**新 AI session 读取顺序**：
1. 读本蓝图 §5（本节）→ 知道「哪些已实现、在哪里」
2. 读模块分解 → 知道「每个模块的职责和 AI 自治权限」
3. 读施工 Phase 规划 → 知道「下一步该做什么」

**路径约定**：
- 所有路径相对于 `D:\ZephyrAlpha\\`
- 源码在 `src/zephyr/` 下
- 测试在 `tests/` 下
- 配置在 `config/` 下
- 治理脚本在 `scripts/governance/` 下
