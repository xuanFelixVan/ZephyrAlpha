---
module_id: MOD-RK-15
title: "尾部风险监控器蓝图 — ES/CVaR + POT模型 + 跳跃检测 + FRTB加价"
doc_type: blueprint
status: Active
version: "0.2.2"
ttl: permanent
layer: L02_risk
layer_name: risk
functional_domain: risk
owner: ZephyrAlpha-Owner
created_by: agent
date: "2026-08-02"
last_updated: "2026-08-18"
priority: P1
blueprint_level: module
responsibility_domain: 
design_maturity: production
build_status: production
---

# MOD-RK-15 Tail Risk Monitor — 尾部风险监控器 蓝图

> **module_id**: MOD-RK-15 | **域**: D_RISK | **层**: L2 Real-Time 盘中监控
> **优先级**: P1 | **成熟度**: production | **对标能力**: C-004●
> **SSoT**: depgraph MOD-RK-15 | **设计真源**: D:\临时工作区\依赖图\11-D-RISK-风控域.md §1.2 RK-15, §2 依赖(RK-05→RK-15)

## 1. 定位

尾部风险监控器——D-RISK L2 实时监控核心模块。度量与监控极端损失风险:
- 期望短缺 (Expected Shortfall / CVaR): 尾部条件期望
- POT 模型 (Peaks-Over-Threshold): 广义帕累托分布拟合, 识别厚尾
- 跳跃检测 (Jump Detection): 收益率绝对值超 σ 阈值计为跳跃
- 极值预警: ES 或 POT shape 超阈值分级告警
- FRTB 尾部风险加价: 基于 shape 的资本加价

属 A 类基础设施 (统计拟合 + 阈值判定, 数学逻辑明确), 阈值为 C 类可调参数。

## 2. 输入 / 输出

| 方向 | 内容 | 契约/事件 |
|------|------|-----------|
| 输入 | 收益率序列 returns (np.ndarray) + 配置 TailRiskConfig | — |
| 输出 | TailRiskSnapshot (var/es/es_var_ratio/pot/jump_count/frtb_addon/alert_level/pot_fallback_historical) | 联动 RK-03, RK-17 |
| 依赖 | RK-05 VaR (基准对比, 可选) | — |

## 3. 核心规则 (设计真源 §1.2 RK-15, §2)

### 3.1 VaR 与 ES

- VaR_α = -quantile(returns, 1-α)  (正数, 损失额比率)
- ES_α = -mean(R | R <= VaR_quantile)，VaR_quantile 取 method='lower'（实有样本点，2026-08-16 双轮审查 F1 裁定：防线性插值虚拟分位值致小样本尾部口径抖动）  (尾部条件期望, 正数)
- 不变量: ES >= VaR (尾部期望 >= 分位数)

### 3.2 POT 模型 (广义帕累托分布)

- 超过阈值 u 的超额值 X-u ~ GPD(ξ, β)
- ξ (shape): >0=厚尾(Fréchet), =0=指数(Gumbel), <0=有界(Weibull)
- β (scale): 尺度参数
- tail_index = 1/ξ (厚尾程度, 越小越厚尾)
- 拟合方法: scipy.stats.genpareto.fit
- 小样本降级（2026-08-16 双轮审查深挖③裁定）：样本 <min_samples / 负收益 <10 / exceedances <5 → 返回 None + warning 日志，snapshot.pot_fallback_historical=True（60 日窗口常态下 POT 与样本量不兼容，降级纯历史 ES 而非噪声拟合）

### 3.3 跳跃检测

- threshold = std(returns) × jump_threshold_sigma (默认 3.0σ)
- jump_count = |returns| > threshold 的数量
- 浮点近零保护: std < 1e-12 时返回 0 (恒定序列)

### 3.4 极值预警分级

- CRITICAL: POT shape >= critical_shape_threshold (默认 0.5)
- WARNING: POT shape >= heavy_tail_shape_threshold (默认 0.2) 或 ES/VaR >= es_warning_ratio (默认 1.5)
- NONE: 其余

### 3.5 FRTB 尾部风险加价

- frtb_addon = base_addon × (1 + shape × multiplier)
- shape 越大 (越厚尾), 加价越高, >= 0

## 4. 关键不变量 (INVARIANTS)

- ES >= VaR (尾部条件期望的损失 >= 分位数处的损失)
- POT shape > 0 = 厚尾
- tail_index = 1/shape
- jump_count 单调非减 (窗口内)
- FRTB 加价 >= 0
- 非有限值 Fail-Closed（2026-08-18 AI-R3 复审 P1）：isfinite 过滤+计数，占比 > max_nonfinite_ratio（默认 5%，与 var_calculator 同口径）→ 抛 InvalidTailRiskInputError（原仅静默滤 NaN，±Inf 穿透污染 ES/POT/jump）

## 5. 错误契约

- `InvalidTailRiskInputError` (ZA-RK-0015): 收益率序列过短 / 置信度非 (0,1) / 阈值非正 / 非有限值占比超阈值（Fail-Closed）

## 6. 测试

- `tests/risk/test_tail_risk_monitor.py`
- 覆盖: VaR/ES 计算 + ES>=VaR 不变量 / POT 拟合 (厚尾/轻尾/恒定) / 跳跃检测 (含零 std 浮点保护) / 告警分级 (NONE/WARNING/CRITICAL) / FRTB 加价 / assess 综合评估 / 输入校验

## 7. 依赖

- `zephyr.shared.foundation.errors` (ZephyrBaseError)
- `numpy`, `scipy.stats`
- 消费: RK-05 VaR (基准, 可选) ; 产出: RK-03 Portfolio Risk Monitor (尾部告警), RK-17 Kill Switch (极值触发)

### §0.6 五图对齐视图

<!-- AUTOGEN: source=depgraph+dataflow+decision, generator=generate_blueprint_panorama.py, reconciler=sync_panorama_module.py -->

> **自动生成**：本节由 generate_blueprint_panorama.py 从全景真源派生，禁止手写。
> 生成命令：`python scripts/governance/d5_architecture/generators/generate_blueprint_panorama.py MOD-RK-15`

#### 全景位置

| 图 | 位置 | 状态 | 链接 |
|----|------|------|------|
| 依赖图 (depgraph) | `blueprint_id=MOD-RK-15` 的 3 个 file 节点 | production | `extract_depgraph.py --modules MOD-RK-15` |
| 数据流图 (dataflow) | （无节点） | N/A | `apply_dataflowgraph.py --list-datasets` |
| 决策架构图 (decision) | 0 个决策节点 / 1 个决策层 | N/A | `generate_decision_diagram.py` |
| 蓝图 (blueprint) | 本文件 | Active | — |

#### 四核心字段

| 字段 | depgraph 值（真源） | 蓝图 frontmatter 值（声明） | 是否一致 |
|------|-------------------|--------------------------|:-------:|
| module_id | MOD-RK-15 | MOD-RK-15 | ✅ |
| domain_id | N/A | N/A | ✅ |
| build_status | production | production | ✅ |
| file_count | 3 文件 | N/A | — |

> 冲突时以 depgraph 为准（ARCH-056 + ARCH-MM-001 声明 vs 验证框架）。

---

## 8. 已实现代码完整路径索引

> **AGENTS.md §6.1 蓝图-代码同步强制约定**——本节是蓝图与磁盘代码的「地址簿」。
> 蓝图声称的文件必须与磁盘实际一致。不一致 = 蓝图漂移 = 下一个 AI session 冷启动时被误导。
> **AUTOGEN**：本表由 sync_blueprint_code_index.py 从 depgraph.nodes 运营态（build_status∈generated/testing/stable）单向派生，禁止手写；重跑本脚本幂等更新。
> 

### 8.1 测试文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `tests/risk/test_pot_failure_counter.py` | ✅ 已实现 | |

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


