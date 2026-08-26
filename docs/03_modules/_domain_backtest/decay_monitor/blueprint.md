---
module_id: MOD-BT-018
title: "策略衰减监控告警器蓝图 — 短期/长期均值对比+趋势检测"
doc_type: blueprint
status: Active
version: "0.1.2"
design_maturity: production
build_status: stable
ttl: permanent
layer: L_BACKTEST
layer_name: backtest
functional_domain: backtest
owner: ZephyrAlpha-Owner
created_by: agent
date: "2026-08-02"
last_updated: "2026-08-02"
priority: P1
blueprint_level: module
responsibility_domain: 
---

# MOD-BT-018 Decay Monitor — 策略衰减监控告警器 蓝图

> **module_id**: MOD-BT-018 | **域**: D_BACKTEST | **层**: L_BACKTEST
> **优先级**: P1 | **成熟度**: L1 → production | **建设标记**: ✅可建
> **SSoT**: depgraph MOD-BT-018 | **设计真源**: 32-D-BACKTEST §1 BT-18 + blueprint.md L245

## 1. 定位

策略衰减监控告警器——跟踪策略性能指标(Sharpe/收益/胜率等)随时间的变化,
通过短期vs长期均值对比和线性趋势检测识别策略衰减, 产出4级告警。

属A类基础设施(统计计算+阈值判定, 逻辑明确), 纯numpy/pandas工具。

## 2. 输入 / 输出

| 方向 | 内容 |
|------|------|
| 输入 | 策略性能指标值(浮点数) 或 性能指标时间序列(Series) |
| 输出 | DecayReport (衰减级别+短期/长期均值+衰减比例+趋势斜率) |

## 3. 衰减检测方法

### 3.1 短期/长期均值对比
- short_window (默认20): 近N期均值
- long_window (默认60): 近M期均值
- decay_ratio = (long_mean - short_mean) / |long_mean| (正=衰减)

### 3.2 线性趋势检测
- 对近期指标用最小二乘法拟合斜率
- 斜率<0 且显著 → 衰减趋势

## 4. 4级告警

| 级别 | 条件 |
|------|------|
| STABLE | short_mean ≥ long_mean |
| WARNING | decay_ratio > warning_threshold (默认0.15) |
| DECAYING | 持续负斜率趋势 |
| CRITICAL | decay_ratio > critical_threshold (默认0.30) 或 short_mean < 0 |

整体级别取最严重。

## 5. 不变量

- 样本数 < short_window 时返回 STABLE (不报错, 数据不足)
- 指标值必须为有限浮点数 (非NaN/Inf)
- update() 维护内部状态, evaluate() 无状态

## 6. 测试

`tests/backtest/test_decay_monitor.py`

## 7. 依赖

- numpy, pandas
- zephyr.shared.foundation.errors

### §0.6 五图对齐视图

<!-- AUTOGEN: source=depgraph+dataflow+decision, generator=generate_blueprint_panorama.py, reconciler=sync_panorama_module.py -->

> **自动生成**：本节由 generate_blueprint_panorama.py 从全景真源派生，禁止手写。
> 生成命令：`python scripts/governance/d5_architecture/generators/generate_blueprint_panorama.py MOD-BT-018`

#### 全景位置

| 图 | 位置 | 状态 | 链接 |
|----|------|------|------|
| 依赖图 (depgraph) | `blueprint_id=MOD-BT-018` 的 2 个 file 节点 | production | `extract_depgraph.py --modules MOD-BT-018` |
| 数据流图 (dataflow) | 1 个 Dataset / 1 个 Job | planned | `apply_dataflowgraph.py --list-datasets` |
| 决策架构图 (decision) | 0 个决策节点 / 1 个决策层 | N/A | `generate_decision_diagram.py` |
| 蓝图 (blueprint) | 本文件 | Active | — |

#### 四核心字段

| 字段 | depgraph 值（真源） | 蓝图 frontmatter 值（声明） | 是否一致 |
|------|-------------------|--------------------------|:-------:|
| module_id | MOD-BT-018 | MOD-BT-018 | ✅ |
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
| `src/zephyr/backtest/services/decay_monitor.py` | ✅ 已实现 | |

### 8.2 测试文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `tests/backtest/test_decay_monitor.py` | ✅ 已实现 | |

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


