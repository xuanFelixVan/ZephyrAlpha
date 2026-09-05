---
module_id: MOD-RK-33
title: "Copula-GARCH 联合分布建模蓝图 — ≤50 标的联合尾部依赖与联合 VaR/ES"
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
design_maturity: production
build_status: production
responsibility_domain: 
---

# MOD-RK-33 Copula-GARCH Joint Model — Copula-GARCH 联合分布建模 蓝图

> **module_id**: MOD-RK-33 | **域**: D_RISK | **层**: L02 盘中实时监控（DCC 盘后批算）
> **优先级**: P0 | **来源**: CAND-RSK-036（B10-01410，AUD-DRAFT-001 裁定=做，★当前即做 ≤50 只）
> **SSoT**: depgraph MOD-RK-33
> **改号留痕**: 2026-08-25 原铸 MOD-RK-32，与 W1c 并行批（CAND-RSK-031~035，MOD-RK-28~32）撞号后改号 MOD-RK-33

## 1. 定位

多标的联合分布 F=C(F₁..F_N)：边缘分布（GARCH 波动过滤 / 条件密度预测注入）+
Gaussian Copula（DCC 动态相关）捕捉**联合尾部依赖**——"多只持仓同时暴跌"是
单标的 VaR 与账面分散化看不到的组合风险空白。

工程约束（候选登记真源）：持仓 ≤50 只（RTX3090：50 只 DCC≈5 分钟盘后批算可行）；
纯计算、无 IO、数据由调用方注入。

## 2. 输入 / 输出

- 输入：≤50 标的等长日收益率序列（T≥min_history）；可选边缘一步预测（μ/σ，由
  D_ASHARE_SIGNAL conditional_density_predictor 产出、调用方映射注入）；组合权重。
- 输出：联合尾部依赖矩阵（经验下尾共超限）、DCC 一步相关预测、联合 VaR/ES
  （Gaussian-Copula Monte Carlo，固定种子可复现）。

## 3. 核心规则

1. 边缘：GARCH(1,1) 方差定向过滤产出标准化残差 z；Qbar 复用 MOD-POS-011
   Ledoit-Wolf 收缩协方差（标准化为相关）。
2. DCC：Q_t=(1−a−b)·Q̄+a·z_{t−1}z′_{t−1}+b·Q_{t−1}，R_t 由 Q_t 标准化；
   (a,b) 为 C 类可调参数（默认 0.04/0.94，a+b<1 硬校验）。
3. Copula：经验 CDF 概率积分变换（不假设正态）；下尾依赖 = 超限共现经验概率
   P(u_i<q,u_j<q)/q（q 默认 0.05）。
4. 联合 VaR/ES：Cholesky(R_{T+1}) 相关正态 → 经验边缘逆 CDF → 组合损失分布；
   VaR 取分位数、ES 取尾部均值；置信度 C 类参数（默认 0.95/0.99）。
5. Fail-Closed：n>max_assets(50)/样本不足/非有限值/权重畸形 → 拒绝。

## 4. 依赖前置

- MOD-POS-011 covariance_estimator（收缩协方差复用）
- MOD-POS-012 correlation_regime_monitor（体制监控前提，场内已在）
- MOD-SIG-043 conditional_density_predictor（边缘密度预测，调用方映射注入）

## 5. 验收标准

- 单测全绿（尾部依赖矩阵对称/对角语义、DCC 相关合法、VaR≤ES、联合 VaR≥
  等权独立近似下限、非法输入拒绝）；tests/risk 域集成零回归。

### §0.6 五图对齐视图

<!-- AUTOGEN: source=depgraph+dataflow+decision, generator=generate_blueprint_panorama.py, reconciler=sync_panorama_module.py -->

> **自动生成**：本节由 generate_blueprint_panorama.py 从全景真源派生，禁止手写。
> 生成命令：`python scripts/governance/d5_architecture/generators/generate_blueprint_panorama.py MOD-RK-33`

#### 全景位置

| 图 | 位置 | 状态 | 链接 |
|----|------|------|------|
| 依赖图 (depgraph) | `blueprint_id=MOD-RK-33` 的 2 个 file 节点 | production | `extract_depgraph.py --modules MOD-RK-33` |
| 数据流图 (dataflow) | 0 个 Dataset / 1 个 Job | active | `apply_dataflowgraph.py --list-datasets` |
| 决策架构图 (decision) | 0 个决策节点 / 1 个决策层 | N/A | `generate_decision_diagram.py` |
| 蓝图 (blueprint) | 本文件 | Active | — |

#### 四核心字段

| 字段 | depgraph 值（真源） | 蓝图 frontmatter 值（声明） | 是否一致 |
|------|-------------------|--------------------------|:-------:|
| module_id | MOD-RK-33 | MOD-RK-33 | ✅ |
| domain_id | N/A | N/A | ✅ |
| build_status | production | production | ✅ |
| file_count | 2 文件 | N/A | — |

> 冲突时以 depgraph 为准（ARCH-056 + ARCH-MM-001 声明 vs 验证框架）。

---

## 6. 已实现代码完整路径索引

> **AGENTS.md §6.1 蓝图-代码同步强制约定**——本节是蓝图与磁盘代码的「地址簿」。
> 蓝图声称的文件必须与磁盘实际一致。不一致 = 蓝图漂移 = 下一个 AI session 冷启动时被误导。
> **AUTOGEN**：本表由 sync_blueprint_code_index.py 从 depgraph.nodes 运营态（build_status∈generated/testing/stable）单向派生，禁止手写；重跑本脚本幂等更新。
> 

### 6.1 测试文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `tests/risk/core/test_copula_garch_joint.py` | ✅ 已实现 | |

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


