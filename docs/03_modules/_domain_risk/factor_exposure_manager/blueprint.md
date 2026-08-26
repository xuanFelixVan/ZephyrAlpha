---
module_id: MOD-RK-38
title: "Factor Exposure Manager 因子敞口管理器蓝图 — 持仓×因子载荷→组合敞口矩阵+超限预警"
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
priority: P1
blueprint_level: module
design_maturity: production
build_status: stable
responsibility_domain: 
---

# MOD-RK-38 Factor Exposure Manager — 因子敞口管理器 蓝图

> **module_id**: MOD-RK-38 | **域**: D_RISK | **层**: L02 组合风险监控
> **优先级**: P1 | **来源**: CAND-RSK-041（B10-02083，PC-14，AUD-DRAFT-001 裁定=做，A1 §30.1.3）
> **SSoT**: depgraph MOD-RK-38

## 0. 查重裁定（RULE-EIGHT 探查结论）

候选 spec：输入持仓+风格/行业因子载荷，输出组合因子敞口矩阵+敞口超限预警
（业界对标 Barra USE3/CNE5、riskfolio-lib）。场内既有件逐一探查：

- MOD-RK-16 risk_decomposition（production）：因子/残差**风险方差分解**（需协方差
  矩阵三件套，事后归因口径）——不做"载荷加权敞口矩阵+超限预警"；
- MOD-RK-07 concentration_monitor（production）：行业**权重**集中度（HHI/单行业
  权重上限）——无因子载荷维度；
- MOD-RK-13 crowding_monitor（production）：跨策略因子**拥挤度**（overlap/consensus，
  输入为策略级单值敞口）——非组合×因子矩阵；
- D_PF_CORE performance_attribution_engine：因子暴露×因子收益的**绩效归因**
  （事后，D_PF_CORE 域）——非风控超限预警；
- multifactor_constraint_arbitration C6_factor_exposure_max：约束仲裁中的敞口上限
  常量消费方——非敞口计算件。

**裁定：无一覆盖"持仓×风格/行业因子载荷→组合因子敞口矩阵+敞口超限预警"判定核心，
独立缺口成立，按补充层施工（不复制任何既有件算法）。**

## 1. 定位

Barra 式组合因子敞口计量：组合在某因子上的敞口 = Σ(个股权重 × 个股因子载荷)。
输出全因子敞口矩阵（字典）+ 逐因子超限判定（|exposure| 超上限→BREACH，
≥上限×warn_ratio→WARNING），供风控预警与盘前/实时监控消费。

纯函数判定核心：无 IO、不直连数据源（持仓权重与因子载荷由调用方注入，
D_POSITION 持仓 / D_FACTOR 载荷，三维解耦）；超限仅产预警信号（处置委托
MOD-RK-02 Pre-Trade / MOD-RK-03 监控等既有执行面）。

## 2. 输入 / 输出

- 输入：positions {symbol: weight}（long-only 非负，自动归一化 Σw=1）；
  factor_loadings {symbol: {factor: loading}}（缺失标的记 uncovered，载荷按 0 计）；
  config（limits {factor: 上限>0}、warn_ratio∈(0,1)）。
- 输出：FactorExposureReport（exposures {factor: 组合敞口}、breaches 逐因子
  ExposureBreach(factor/exposure/limit/severity)、uncovered_symbols、weight_sum）。
- 审计：超限事件经注入 audit_sink 回调留痕（委托 D_GOV_AUDIT，本模块不落盘）。

## 3. 核心规则

1. 敞口公式：exposure[f] = Σ_s w_s × loading[s][f]（w 归一化后；缺载荷按 0 计
   并列 uncovered_symbols 如实披露）。
2. 因子全集 = limits 键 ∪ 载荷中出现的因子；limits 未覆盖的因子只计量不预警。
3. 超限分级：|exposure| > limit → BREACH；|exposure| ≥ limit×warn_ratio → WARNING；
   否则 OK。多空敞口对称取绝对值。
4. 权重归一化：Σw>0 时 w/=Σw（与 MOD-RK-16 族口径一致）；Σw=0 拒绝。
5. Fail-Closed：负权重、非有限权重/载荷、空持仓、limit≤0、warn_ratio∉(0,1) →
   InvalidFactorExposureInputError。
6. 报告 frozen 不可变；breaches 按 |exposure/limit| 降序。

## 4. 依赖前置

- D_FACTOR 因子载荷（调用方注入，本模块不越域取数）
- D_POSITION 持仓权重（调用方注入）
- 分工边：MOD-RK-16（风险分解归因）/ MOD-RK-07（行业集中度）/ MOD-RK-13（拥挤度）

## 5. 验收标准

- 单测全绿：敞口加权求和（含缺载荷 uncovered 披露）、归一化、超限 WARNING/BREACH
  分级与降序、limits 外因子只计量不预警、非法输入 Fail-Closed、audit_sink 回调触发；
  tests/risk 域零回归。

### §0.6 五图对齐视图

<!-- AUTOGEN: source=depgraph+dataflow+decision, generator=generate_blueprint_panorama.py, reconciler=sync_panorama_module.py -->

> **自动生成**：本节由 generate_blueprint_panorama.py 从全景真源派生，禁止手写。
> 生成命令：`python scripts/governance/d5_architecture/generators/generate_blueprint_panorama.py MOD-RK-38`

#### 全景位置

| 图 | 位置 | 状态 | 链接 |
|----|------|------|------|
| 依赖图 (depgraph) | `blueprint_id=MOD-RK-38` 的 2 个 file 节点 | production | `extract_depgraph.py --modules MOD-RK-38` |
| 数据流图 (dataflow) | （无节点） | N/A | `apply_dataflowgraph.py --list-datasets` |
| 决策架构图 (decision) | 0 个决策节点 / 1 个决策层 | N/A | `generate_decision_diagram.py` |
| 蓝图 (blueprint) | 本文件 | Active | — |

#### 四核心字段

| 字段 | depgraph 值（真源） | 蓝图 frontmatter 值（声明） | 是否一致 |
|------|-------------------|--------------------------|:-------:|
| module_id | MOD-RK-38 | MOD-RK-38 | ✅ |
| domain_id | N/A | N/A | ✅ |
| build_status | stable | stable | ✅ |
| file_count | 2 文件 | N/A | — |

> 冲突时以 depgraph 为准（ARCH-056 + ARCH-MM-001 声明 vs 验证框架）。

---

## 6. 已实现代码完整路径索引

> **AGENTS.md §6.1 蓝图-代码同步强制约定**——本节是蓝图与磁盘代码的「地址簿」。
> 蓝图声称的文件必须与磁盘实际一致。不一致 = 蓝图漂移 = 下一个 AI session 冷启动时被误导。
> **AUTOGEN**：本表由 sync_blueprint_code_index.py 从 depgraph.nodes 运营态（build_status∈generated/testing/stable）单向派生，禁止手写；重跑本脚本幂等更新。
> 

### 6.1 源码文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `src/zephyr/risk/core/factor_exposure_manager.py` | ✅ 已实现 | |

### 6.2 测试文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `tests/risk/core/test_factor_exposure_manager.py` | ✅ 已实现 | |

### 6.5 路径索引使用指南

**新 AI session 读取顺序**：
1. 读本蓝图 §6（本节）→ 知道「哪些已实现、在哪里」
2. 读模块分解 → 知道「每个模块的职责和 AI 自治权限」
3. 读施工 Phase 规划 → 知道「下一步该做什么」

**路径约定**：
- 所有路径相对于 `D:\ZephyrAlpha\\`
- 源码在 `src/zephyr/` 下
- 测试在 `tests/` 下
- 配置在 `config/` 下
- 治理脚本在 `scripts/governance/` 下
