---
module_id: MOD-RK-28
title: "前瞻 VaR 共形预判层蓝图 — 条件PDF VaR/CVaR + 共形VaR 盘前预判（C-004 ①预判层）MVP"
doc_type: blueprint
status: Active
version: "0.1.2"
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
blueprint_id: MOD-RK-28
domain_id: D_RISK
path: src/zephyr/risk/core/adaptive_risk_forecast.py
design_maturity: production
build_status: production
granularity: file
ai_autonomy: ai_modifiable
safety: M
stability: evolving
responsibility_domain: 
---

# MOD-RK-28 前瞻 VaR 共形预判层（Adaptive Risk Forecast）蓝图

> **module_id**: MOD-RK-28 | **域**: D_RISK | **层**: C-004 三层体系 ①预判层
> **优先级**: P0 | **来源**: CAND-RSK-034（B10-01216，AUD-DRAFT-001-DIGEST P0 波 W1c）

## 1. 定位

C-004 自适应风控三层体系（battle_map_positioning L4：预判层+监控层+熔断层）的
**①预判层能力底座**：盘前用条件 PDF（MOD-SIG-043）产出前瞻 VaR/CVaR，外裹共形
安全缓冲（MOD-SIG-044，有限样本边际覆盖率数学保证），对照风险限额产出
limit_scale / sit_out 盘前建议；输出作为 MOD-RK-05D var_intraday_recalc 的盘前基线。

**底座复用裁定（W1c 同族整合）**：本模块不重复实现 VaR/密度/共形算法——
- 条件 PDF：import `zephyr.signal_ashare.conditional_density_predictor`（MOD-SIG-043）
- 共形缓冲：import `zephyr.signal_ashare.conformal_predictor`（MOD-SIG-044）
- 限额对照/基线契约：对齐 MOD-RK-05 / MOD-RK-05D（不改其存量代码）

与 C-004 编排层（MOD-RK-30）的分工：本模块只产出**数据契约**，裁决与三层联动在
MOD-RK-30 薄装配。

## 2. 输入 / 输出

| 方向 | 内容 | 契约 |
|------|------|------|
| 输入 | 历史收益序列 + 平行条件标签（可空）+ 共形校准 (预测,实际) 对（可空） | — |
| 输出 | ForwardVarForecast(var_pct/cvar_pct/conformal_margin_pct/conformal_var_pct/limit_scale/limit_breached/sit_out/degraded/n_samples/n_calibration) | frozen dataclass |

## 3. 核心规则

1. 条件 PDF VaR/CVaR：`conditional_density(...).var_95/cvar_95`（负值口径）取负得损失占比。
2. 共形 VaR：校准集非 conformity 分数经 `SplitConformalPredictor.fit` 得 q̂，
   `conformal_var_pct = var_pct + q̂`；无校准集 → margin=0 且 degraded=True（无覆盖率保证，保守）。
3. 限额挂接：`limit_scale = min(1, var_limit_pct / conformal_var_pct)`；
   `limit_breached = conformal_var_pct > var_limit_pct`；
   `sit_out = conformal_var_pct >= sit_out_var_pct`。
4. 纯函数无 IO；Fail-Closed 配置校验（InvalidForwardVarConfigError）。

## 4. 依赖

| 依赖 | 模块 | 类型 |
|------|------|------|
| 条件密度 | MOD-SIG-043 conditional_density_predictor | import_depends |
| 共形预测 | MOD-SIG-044 conformal_predictor | import_depends |
| VaR 基线契约 | MOD-RK-05 var_calculator | import_depends（口径对齐） |
| 盘中重算基线 | MOD-RK-05D var_intraday_recalc | import_depends（盘前基线消费口） |

### §0.6 五图对齐视图

<!-- AUTOGEN: source=depgraph+dataflow+decision, generator=generate_blueprint_panorama.py, reconciler=sync_panorama_module.py -->

> **自动生成**：本节由 generate_blueprint_panorama.py 从全景真源派生，禁止手写。
> 生成命令：`python scripts/governance/d5_architecture/generators/generate_blueprint_panorama.py MOD-RK-28`

#### 全景位置

| 图 | 位置 | 状态 | 链接 |
|----|------|------|------|
| 依赖图 (depgraph) | `blueprint_id=MOD-RK-28` 的 2 个 file 节点 | production | `extract_depgraph.py --modules MOD-RK-28` |
| 数据流图 (dataflow) | 0 个 Dataset / 1 个 Job | active | `apply_dataflowgraph.py --list-datasets` |
| 决策架构图 (decision) | 0 个决策节点 / 1 个决策层 | N/A | `generate_decision_diagram.py` |
| 蓝图 (blueprint) | 本文件 | Active | — |

#### 四核心字段

| 字段 | depgraph 值（真源） | 蓝图 frontmatter 值（声明） | 是否一致 |
|------|-------------------|--------------------------|:-------:|
| module_id | MOD-RK-28 | MOD-RK-28 | ✅ |
| domain_id | N/A | N/A | ✅ |
| build_status | production | production | ✅ |
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
| — | — | 本模块尚无已实现代码 |

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


