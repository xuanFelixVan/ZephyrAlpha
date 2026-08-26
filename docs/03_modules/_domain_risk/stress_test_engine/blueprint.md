---
module_id: MOD-RK-12
title: "压力测试引擎蓝图 — 历史情景 + 假设情景 + 反向压力 + 敏感性 + 传染效应"
doc_type: blueprint
status: Active
version: "0.1.2"
ttl: permanent
layer: L02_risk
layer_name: risk
functional_domain: risk
owner: ZephyrAlpha-Owner
created_by: agent
date: "2026-08-02"
last_updated: "2026-08-02"
priority: P1
blueprint_level: module
responsibility_domain: 
design_maturity: production
build_status: stable
---

# MOD-RK-12 Stress Test Engine — 压力测试引擎 蓝图

> **module_id**: MOD-RK-12 | **域**: D_RISK | **层**: 分析引擎
> **优先级**: P1 | **成熟度**: production | **对标能力**: C-040●
> **SSoT**: depgraph MOD-RK-12 | **设计真源**: D:\临时工作区\依赖图\11-D-RISK-风控域.md §1.2 RK-12, §2 依赖(RK-05→RK-12)

## 1. 定位

压力测试引擎——D-RISK 分析引擎核心模块。评估组合在极端情景下的潜在损失:
- 历史情景 (HISTORICAL): 2008 金融危机 / 2015 股灾 / 2020 疫情, 预置 shock 不可改
- 假设情景 (HYPOTHETICAL): 用户自定义 shock 向量
- 反向压力测试 (REVERSE): 给定目标损失, 二分搜索找出致损情景
- 敏感性分析 (SENSITIVITY): 单因子在 shock 范围内的 PnL 变化曲线
- 传染效应 (CONTAGION): 冲击经相关性矩阵放大后的组合损失

属 A 类基础设施 (情景叠加 + 二分搜索, 逻辑明确), 历史情景幅度为 C 类不可改真源。

## 2. 输入 / 输出

| 方向 | 内容 | 契约/事件 |
|------|------|-----------|
| 输入 | 权重 weights (dict) + 组合价值 portfolio_value + 情景定义 | — |
| 输出 | StressTestResult (loss/loss_pct/worst_shock/scenario_name/affected_symbols) | 联动 RK-03, RK-14 |
| 依赖 | RK-05 VaR (基准比较, 可选) | — |

## 3. 核心规则 (设计真源 §1.2 RK-12, §2)

### 3.1 历史情景 (预置 shock 不可改)

- 2008 金融危机: 全市场 -25%, 金融板块额外 -15%
- 2015 股灾: 全市场 -20%, 高估值股额外 -20%
- 2020 疫情: 全市场 -18%, 消费板块额外 -10%

### 3.2 压力损失计算

- loss = Σ w_i · shock_i · portfolio_value  (shock_i 为负=下跌)
- loss_pct = loss / portfolio_value

### 3.3 反向压力测试 (二分搜索)

- 给定 target_loss_pct, 二分搜索 shock_scale 使 loss >= target
- base_shocks 按比例缩放, 收敛于 [0, max_scale]

### 3.4 传染效应

- shocked_return_i = shock_i + Σ_j (ρ_ij · shock_j · contagion_factor)
- 传染放大损失 = Σ w_i · shocked_return_i · portfolio_value

### 3.5 敏感性分析

- 单因子 shock 在 [-range, +range] 内扫描, 输出 PnL 曲线

## 4. 关键不变量 (INVARIANTS)

- 历史情景 shock 幅度固定不可改 (C 类真源)
- 压力损失 = Σ(w_i · shock_i) (线性叠加)
- 反向压力测试二分搜索收敛 (单调性保证)
- 传染效应单调递增 (相关性放大损失)
- 权重归一化: Σw = 1

## 5. 错误契约

- `InvalidStressTestInputError` (ZA-RK-0012): 权重为空 / shock 维度不匹配 / 目标损失非正 / 相关性矩阵非方阵

## 6. 测试

- `tests/risk/test_stress_test_engine.py`
- 覆盖: 历史情景 (3 个预置) / 假设情景 / 反向压力 (二分收敛) / 敏感性分析 / 传染效应 / run_all_historical / 输入校验 / 严重性判定

## 7. 依赖

- `zephyr.shared.foundation.errors` (ZephyrBaseError)
- `numpy`
- 消费: RK-05 VaR (基准, 可选) ; 产出: RK-03 Portfolio Risk Monitor (压力告警), RK-14 Black Swan Library (情景匹配)

### §0.6 五图对齐视图

<!-- AUTOGEN: source=depgraph+dataflow+decision, generator=generate_blueprint_panorama.py, reconciler=sync_panorama_module.py -->

> **自动生成**：本节由 generate_blueprint_panorama.py 从全景真源派生，禁止手写。
> 生成命令：`python scripts/governance/d5_architecture/generators/generate_blueprint_panorama.py MOD-RK-12`

#### 全景位置

| 图 | 位置 | 状态 | 链接 |
|----|------|------|------|
| 依赖图 (depgraph) | `blueprint_id=MOD-RK-12` 的 2 个 file 节点 | production | `extract_depgraph.py --modules MOD-RK-12` |
| 数据流图 (dataflow) | 0 个 Dataset / 1 个 Job | active | `apply_dataflowgraph.py --list-datasets` |
| 决策架构图 (decision) | 0 个决策节点 / 1 个决策层 | N/A | `generate_decision_diagram.py` |
| 蓝图 (blueprint) | 本文件 | Active | — |

#### 四核心字段

| 字段 | depgraph 值（真源） | 蓝图 frontmatter 值（声明） | 是否一致 |
|------|-------------------|--------------------------|:-------:|
| module_id | MOD-RK-12 | MOD-RK-12 | ✅ |
| domain_id | N/A | N/A | ✅ |
| build_status | stable | stable | ✅ |
| file_count | 2 文件 | N/A | — |

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
| `src/zephyr/risk/core/stress_test_engine.py` | ✅ 已实现 | |

### 8.2 测试文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `tests/risk/test_stress_test_engine.py` | ✅ 已实现 | |

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


