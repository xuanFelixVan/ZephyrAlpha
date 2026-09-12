---
module_id: MOD-RK-26
title: "FHS 引擎蓝图 — Filtered Historical Simulation（GARCH 残差重采样 VaR/ES）MVP"
doc_type: blueprint
status: Active
version: "0.1.3"
ttl: permanent
layer: L02_risk
layer_name: risk
functional_domain: risk
owner: ZephyrAlpha-Owner
created_by: agent
date: "2026-08-18"
last_updated: "2026-08-18"
priority: P2
blueprint_level: module
responsibility_domain: 
design_maturity: production
build_status: production
---

# MOD-RK-26 FHS Engine — Filtered Historical Simulation 引擎 蓝图

> **module_id**: MOD-RK-26 | **域**: D_RISK | **层**: L02 盘中实时监控
> **优先级**: P2 | **成熟度**: evolving（MVP） | **设计真源**: [36_var_es_monitoring](../../02_enterprise_architecture/07_trading_decision_architecture/design_memos/36_var_es_monitoring.md) §3.16（FHS 施工规约）
> **来源**: CAND-AUTONOMYCORE-002 远期候选转正（2026-08-18 AI-FHS-001 施工）

## 1. 定位

FHS（Filtered Historical Simulation）——GARCH(1,1) 拟合收益序列 → 标准化残差 →
有放回重采样 → 逐日递归乘条件波动率预测 → 产出 FHS VaR/ES 的第三 VaR 方法论。

**并列方法论、独立模块**（2026-08-18 AI-FHS-001 裁定）：
- MOD-RK-05 var_calculator（参数法 + 历史模拟 + conservative_max）为 Phase 1 存量，
  R3 审查线在审、契约冻结——本模块**不集成进 var_calculator 存量**、不改 conservative_max 取大链；
- 本模块与 var_calculator **零代码耦合**（不 import 其错误类/函数），自建独立错误契约；
- 第三法纳入取大链 / memo 36 §3.10 RECALIBRATE 动作 4 的启用裁决属 RiskLayerOrchestrator
  层（远期接线），`should_switch_to_fhs()` 三触发 + `FHS_COOLDOWN_DAYS=10` 冷却期 +
  `FHS_PERMANENTLY_DISABLED` 升级路径均**不在本 MVP 范围**（memo §3.16 规约，远期编排层落地）。

**解决的问题**（CAND-AUTONOMYCORE-002）：Christoffersen 独立性失败（A 股波动率聚集下
超限聚集）时历史模拟法无自相关破缺手段——FHS 用 GARCH 残差重采样破自相关，
是 memo 36 §3.9.2 回测远期第 5 法。

## 2. 输入 / 输出

| 方向 | 内容 | 契约/事件 |
|------|------|-----------|
| 输入 | 日收益序列（1D np.ndarray）+ portfolio_value | — |
| 输出 | FHSResult(var/es/var_pct/es_pct/method_used/garch_params/historical_var/historical_es/…) | 无下游（设计契约消费者=RiskLayerOrchestrator RECALIBRATE 动作 4，远期接线） |
| 依赖 | `zephyr.shared.foundation.errors` + numpy + scipy.optimize | — |

## 3. 核心规则（memo 36 §3.16 施工规约落地）

### 3.1 算法（Barone-Adesi FHS）

| 步骤 | 内容 |
|------|------|
| ① 去均值 | eps_t = r_t − μ̂（两阶段估计，μ̂=样本均值） |
| ② GARCH(1,1) QMLE | σ_t² = ω + α·ε²_{t−1} + β·σ²_{t−1}；约束 ω>0, α≥0, β≥0, α+β<1（平稳性，二次罚项）；L-BFGS-B 双起点取较优 |
| ③ 标准化残差 | z_t = ε_t / σ_t |
| ④ 波动率预测 | σ²_{T+1} = ω + α·ε²_T + β·σ²_T |
| ⑤ 残差重采样 | z* ~ iid bootstrap(z)；逐日递归 ε*_s = σ*_s·z*_s，σ*²_{s+1} = ω + α·ε*²_s + β·σ*²_s |
| ⑥ 累积收益 | r* = Π(1 + μ̂ + ε*_s) − 1（多日复利，**非 √T 缩放**——前向波动率聚集传播是 FHS 的增量价值） |
| ⑦ VaR/ES | VaR = −quantile(r*, 1−c, method='lower')·V；ES = −mean(r*[r* ≤ q])·V；下限 0 |

### 3.2 不收敛回退（memo §3.16 "GARCH 不收敛→回退 historical+标记 FHS 不可用"）

- 触发：收益方差非正/非有限 / L-BFGS-B 双起点均未收敛 / 滤波后方差非正 / σ 预测非正非有限
- 默认 `fallback_to_historical=True`：回退历史模拟法，`method_used=HISTORICAL_FALLBACK` +
  `garch_converged=False` + `fallback_reason` + warning 日志（标记 FHS 不可用）
- `fallback_to_historical=False`：抛 `GarchConvergenceError` 供编排层显式处理
- **小样本守卫**：`garch_min_history=60`（memo §3.7 窗口 + CAND tech_notes "60 日小样本
  GARCH 拟合稳定性需最小样本守卫"）；`min_history(30) ≤ n < garch_min_history(60)` 时
  不尝试拟合直接回退 HS

### 3.3 HS 对照（合理性诊断）

`historical_var/historical_es` 始终计算（口径对齐 var_calculator._historical +
memo ES method='lower'，多日 √T 缩放）——供 FHS vs HS 偏离度审计
（memo §4.26 轻量提取 MODEL_DIVERGENCE 族思路），不回退时仅供诊断不混合。

### 3.4 ES 口径

`method='lower'`（实有样本点，不线性插值）对齐 memo 36 v1.11.0 F1 裁定——
尾部均值 ≤ 分位点 → ES ≥ VaR 构造性成立，无运行时强制校验。

### 3.5 输入校验（Fail-Closed）

- 非有限值（NaN/±Inf）过滤 + 计数 `nan_dropped`；占比 > `max_nonfinite_ratio`（默认 5%）
  抛 `ExcessiveFHSNonFiniteDataError`（口径对齐 var_calculator F2+F4 裁定）
- 有效样本 < `min_history`（30）抛 `InsufficientFHSHistoryError`
- `portfolio_value ≤ 0` 抛 `InvalidFHSConfigError`

### 3.6 可复现性

`random_seed` 配置注入；None 时随机取种并入 `FHSResult.random_seed_used` 留痕（审计可复现）。

## 4. 关键不变量（INVARIANTS）

- VaR ≥ 0 且 ES ≥ 0（损失额非负，下限 0）
- ES ≥ VaR（method='lower' 尾部均值 ≤ 实有分位点，构造性成立）
- 样本 < min_history → 抛 InsufficientFHSHistoryError（Fail-Closed）
- 非有限值占比超阈值 → 抛 ExcessiveFHSNonFiniteDataError（Fail-Closed）
- GARCH 不收敛 → 回退 historical（fallback 开启时）且 garch_converged=False
- 回退时 var == historical_var 且 es == historical_es
- α+β < 1（平稳性守卫，二次罚项 + 后验校验硬执行）
- 置信度 ∈ (0,1)；holding_period ≥ 1；同日同种子结果可复现

## 5. 错误契约

- `InvalidFHSConfigError` (ZA-RK-0026)：配置非法 / portfolio_value 非正 / 维度错误
- `InsufficientFHSHistoryError` (ZA-RK-0027)：有效样本 < min_history
- `ExcessiveFHSNonFiniteDataError` (ZA-RK-0028)：非有限值占比超阈值（Fail-Closed）
- `GarchConvergenceError` (ZA-RK-0029)：GARCH 不收敛且 fallback_to_historical=False

（错误码段 AI-ERR-001 对账对象；ZA-RK-0025 避让 ERR-001 重码改号计划 RK-0009→0025，四码顺延 0026~0029——Qwen 审查线 2026-08-18 撞码实证避让。与 var_calculator 错误类零共享保持独立审查面。）

## 6. 测试

- `tests/risk/test_fhs_engine.py`（28 用例）
- 覆盖：配置校验 / Fail-Closed 输入校验 / GARCH 拟合收敛与参数恢复（宽容差）/
  FHS 基本不变式 / **与历史模拟法对照合理性**（regime shift FHS>HS、平静尾 FHS<HS、
  iid 正态 FHS≈HS<50% 偏离）/ 多日递归 / 种子可复现 / 不收敛回退三路径
  （零方差/小样本守卫/禁用回退抛错）/ HS 对照始终产出 / to_dict / frozen

## 7. 依赖

- `zephyr.shared.foundation.errors`（ZephyrBaseError）
- `numpy`、`scipy.optimize`（L-BFGS-B）
- 消费者：无（设计契约消费者 RiskLayerOrchestrator，memo 36 §3.10 动作 4，远期接线 CAND-AUTONOMYCORE-002）
- **不依赖 var_calculator**（避让 R3 审查线契约冻结；独立模块裁定）

### §0.6 五图对齐视图

<!-- AUTOGEN: source=depgraph+dataflow+decision, generator=generate_blueprint_panorama.py, reconciler=sync_panorama_module.py -->

> **自动生成**：本节由 generate_blueprint_panorama.py 从全景真源派生，禁止手写。
> 生成命令：`python scripts/governance/d5_architecture/generators/generate_blueprint_panorama.py MOD-RK-26`

#### 全景位置

| 图 | 位置 | 状态 | 链接 |
|----|------|------|------|
| 依赖图 (depgraph) | `blueprint_id=MOD-RK-26` 的 2 个 file 节点 | production | `extract_depgraph.py --modules MOD-RK-26` |
| 数据流图 (dataflow) | 0 个 Dataset / 1 个 Job | active | `apply_dataflowgraph.py --list-datasets` |
| 决策架构图 (decision) | 0 个决策节点 / 1 个决策层 | N/A | `generate_decision_diagram.py` |
| 蓝图 (blueprint) | 本文件 | Active | — |

#### 四核心字段

| 字段 | depgraph 值（真源） | 蓝图 frontmatter 值（声明） | 是否一致 |
|------|-------------------|--------------------------|:-------:|
| module_id | MOD-RK-26 | MOD-RK-26 | ✅ |
| domain_id | N/A | N/A | ✅ |
| build_status | production | production | ✅ |
| file_count | 2 文件 | N/A | — |

> 冲突时以 depgraph 为准（ARCH-056 + ARCH-MM-001 声明 vs 验证框架）。

## 8. 已实现代码完整路径索引

> **AGENTS.md §6.1 蓝图-代码同步强制约定**——本节是蓝图与磁盘代码的「地址簿」。
> 蓝图声称的文件必须与磁盘实际一致。不一致 = 蓝图漂移 = 下一个 AI session 冷启动时被误导。
> **AUTOGEN**：本表由 sync_blueprint_code_index.py 从 depgraph.nodes 运营态（build_status∈generated/testing/stable）单向派生，禁止手写；重跑本脚本幂等更新。
> 

### 8.1 测试文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `tests/risk/test_fhs_engine.py` | ✅ 已实现 | |

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


