---
module_id: MOD-RK-05
title: "VaR 风险价值计算器蓝图 — 参数法+历史模拟法 Phase 1"
doc_type: blueprint
status: Active
version: "0.2.0"
ttl: permanent
layer: L02_risk
layer_name: risk
functional_domain: risk
owner: ZephyrAlpha-Owner
created_by: agent
date: "2026-08-02"
last_updated: "2026-08-18"
priority: P0
blueprint_level: module
responsibility_domain: 
design_maturity: production
build_status: stable
---

# MOD-RK-05 VaR Calculator — 风险价值计算器 蓝图

> **module_id**: MOD-RK-05 | **域**: D_RISK | **层**: L02 盘中实时监控
> **优先级**: P0 | **成熟度**: production | **对标能力**: C-004●
> **SSoT**: depgraph MOD-RK-05 | **设计真源**: D:\临时工作区\依赖图\11-D-RISK-风控域.md §1.2 RK-05, §6 VaR三阶段演进

## 1. 定位

VaR 风险价值计算器——Phase 1 实现参数法(方差-协方差)+历史模拟法并发计算, 取 max 作为保守估计。
供 RK-03 实时监控使用, 是组合潜在损失量化的核心基础设施。

Phase 2(未实现): +蒙特卡洛法(GPU CuPy/PyTorch)
Phase 3(未实现): Basel III 三角验证+乘数因子+压力 VaR

关键约束: 每阶段独立可用——Phase 1 完成即可上线风控。
属 A 类基础设施(正态分位数+经验分位数, 数学逻辑明确), 置信度/持有期为 C 类可调参数。

## 2. 输入 / 输出

| 方向 | 内容 | 契约/事件 |
|------|------|-----------|
| 输入 | 日收益序列 / 多资产收益矩阵+权重 | — |
| 输出 | VaRResult(value/value_pct/parametric_var/historical_var) | 联动 RK-03, RK-16 |
| 依赖 | portfolio_value, 历史收益(>=min_history) | — |

## 3. 核心规则 (设计真源 §1.2 RK-05, §6)

### 3.1 三方法

| 方法 | 公式 | 说明 |
|------|------|------|
| 参数法 | VaR = (z·σ - μ)·V·√T | 假设正态分布, z=|ppf(1-c)| |
| 历史模拟 | VaR = -quantile(r, 1-c)·V·√T | 经验分位数, 捕捉厚尾 |
| conservative_max | max(parametric, historical) | Phase 1 默认, 保守估计 |

### 3.2 多日缩放

- 多日 VaR ≈ 日 VaR · √T (平方根时间缩放法则)

### 3.3 样本要求

- 历史模拟法需 >= min_history(默认 30) 个有效样本
- 非有限值（NaN/±Inf）过滤并计数（`nan_dropped` 入 VaRResult，2026-08-16 双轮审查 F2+F4 裁定）；占比 > max_nonfinite_ratio（默认 5%）→ 抛 ExcessiveNonFiniteDataError（Fail-Closed，数据缺口期拒绝出 VaR）

## 4. 关键不变量 (INVARIANTS)

- VaR ≥ 0 (损失额非负, 高均值低波动时取 0 下限)
- conservative_max = max(parametric, historical)
- 样本不足 → 抛 InsufficientVaRHistoryError (Fail-Closed)
- 非有限值占比超阈值 → 抛 ExcessiveNonFiniteDataError (Fail-Closed)
- 置信度 ∈ (0,1); holding_period ≥ 1

## 5. 错误契约

- `InvalidVaRConfigError` (ZA-RK-0005): 配置非法(置信度/持有期)
- `InsufficientVaRHistoryError` (ZA-RK-0006): 历史样本不足
- `ExcessiveNonFiniteDataError` (ZA-RK-0024): 非有限值(NaN/±Inf)占比超阈值
  （编号终局 2026-08-18：#ARCH-ERRCODE-001 专项批 AI-ERR-001 裁定本类保留 ZA-RK-0024，stop_loss 重码方顺延 ZA-RK-0025）

## 6. 测试

- `tests/risk/test_var_calculator.py`
- 覆盖: 参数法/历史模拟/conservative_max、95%/99%、多日缩放、多资产组合、NaN/Inf 过滤+计数+超阈值 raise、样本不足、零下限

## 7. 依赖

- `zephyr.shared.foundation.errors` (ZephyrBaseError)
- `numpy`, `scipy.stats.norm`
- 消费者: RK-03 Portfolio Risk Monitor, RK-16 Risk Decomposition, RK-12 Stress Test, RK-15 Tail Risk

### §0.6 五图对齐视图

<!-- AUTOGEN: source=depgraph+dataflow+decision, generator=generate_blueprint_panorama.py, reconciler=sync_panorama_module.py -->

> **自动生成**：本节由 generate_blueprint_panorama.py 从全景真源派生，禁止手写。
> 生成命令：`python scripts/governance/d5_architecture/generators/generate_blueprint_panorama.py MOD-RK-05`

#### 全景位置

| 图 | 位置 | 状态 | 链接 |
|----|------|------|------|
| 依赖图 (depgraph) | `blueprint_id=MOD-RK-05` 的 2 个 file 节点 | production | `extract_depgraph.py --modules MOD-RK-05` |
| 数据流图 (dataflow) | 0 个 Dataset / 1 个 Job | active | `apply_dataflowgraph.py --list-datasets` |
| 决策架构图 (decision) | 0 个决策节点 / 1 个决策层 | N/A | `generate_decision_diagram.py` |
| 蓝图 (blueprint) | 本文件 | Active | — |

#### 四核心字段

| 字段 | depgraph 值（真源） | 蓝图 frontmatter 值（声明） | 是否一致 |
|------|-------------------|--------------------------|:-------:|
| module_id | MOD-RK-05 | MOD-RK-05 | ✅ |
| domain_id | N/A | N/A | ✅ |
| build_status | stable | stable | ✅ |
| file_count | 2 文件 | N/A | — |

> 冲突时以 depgraph 为准（ARCH-056 + ARCH-MM-001 声明 vs 验证框架）。

---

## 8. 已实现代码完整路径索引

> **AGENTS.md §6.1 蓝图-代码同步强制约定**——本节是蓝图与磁盘代码的「地址簿」。
> 蓝图声称的文件必须与磁盘实际一致。不一致 = 蓝图漂移 = 下一个 AI session 冷启动时被误导。
> **AUTOGEN**：本表由 sync_blueprint_code_index.py 从 depgraph.nodes 运营态（build_status=generated）单向派生，禁止手写；重跑本脚本幂等更新。
> 

### 8.1 测试文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `tests/risk/test_var_calculator.py` | ✅ 已实现 | |

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
