---
module_id: MOD-BT-021
title: "参数优化结果分析器蓝图 — 显著性+过拟合检测"
doc_type: blueprint
status: Active
version: "0.1.3"
design_maturity: production
build_status: production
ttl: permanent
layer: L_BACKTEST
layer_name: backtest
functional_domain: backtest
owner: ZephyrAlpha-Owner
created_by: agent
date: "2026-08-02"
last_updated: "2026-08-02"
priority: P2
blueprint_level: module
responsibility_domain: 
---

# MOD-BT-021 Parameter Analyzer — 参数优化结果分析器 蓝图

> **module_id**: MOD-BT-021 | **域**: D_BACKTEST | **层**: L_BACKTEST 回测引擎层
> **优先级**: P2 | **成熟度**: production | **建设标记**: ✅可建
> **SSoT**: depgraph MOD-BT-021 | **设计真源**: D:\临时工作区\依赖图\32-D-BACKTEST-回测引擎域.md §1 BT-21

## 1. 定位

参数优化结果分析器——对多组参数回测结果执行显著性分析和过拟合检测。
识别最优参数组合, 评估各参数对目标函数的敏感度, 检测 IS/OOS 性能差距,
评估优化结果的统计稳定性。支持结果缓存(复用 BT-020 CacheManager)。

属 A 类基础设施(纯统计分析+阈值判定, 逻辑明确), 阈值为 C 类可调参数。
纯工具模块, 数据由调用方传入, 可选缓存到 BT-020。

## 2. 输入 / 输出

| 方向 | 内容 | 契约/事件 |
|------|------|-----------|
| 输入 | list[ParamRun] (每组含 params + objective + 可选 IS/OOS) | 来自参数网格搜索 |
| 输出 | ParamAnalysisReport (最优参数+敏感度+过拟合+稳定性) | 供 BT-19 报告 / 人工审查 |

## 3. 核心分析

### 3.1 最优参数识别

```
best_run = max(runs, key=lambda r: r.objective)
```

### 3.2 参数敏感度

对每个参数 p:
- 按 p 的值分组, 计算每组的 objective 均值
- sensitivity = (max_group_mean - min_group_mean) / overall_std
- sensitivity > threshold → 参数显著 (对结果有实质影响)

### 3.3 过拟合检测

- IS/OOS 差距: overfit_score = (IS - OOS) / |IS| (IS>OOS 时为正)
- overfit_score > threshold (默认 0.5) → 过拟合风险高
- 无 OOS 数据 → 跳过

### 3.4 稳定性评估

- top_n 最优结果的 objective 变异系数 (CV = std/mean)
- CV < 0.1 → 稳定 (参数区域内表现一致)
- CV > 0.3 → 不稳定 (可能是噪声峰)

## 4. 关键不变量 (INVARIANTS)

- ParamRun / ParamSensitivity / OverfittingCheck / ParamAnalysisConfig / ParamAnalysisReport 为 frozen dataclass
- 空列表 → raise ParamAnalysisError
- 单条记录 → 敏感度/稳定性不可计算, 返回空列表 + None
- 不修改输入数据
- 可选缓存: 分析结果可存入 BT-020 CacheManager

## 5. 错误契约

- `ParamAnalysisError` (ZA-BT-0021): 输入为空 / 格式非法

## 6. 测试

- `tests/backtest/test_param_analyzer.py`
- 覆盖: 最优参数识别、敏感度计算、过拟合检测(IS/OOS)、稳定性评估、
  空列表拒绝、单条记录处理、缓存集成、配置自定义、frozen不可变

### §0.6 五图对齐视图

<!-- AUTOGEN: source=depgraph+dataflow+decision, generator=generate_blueprint_panorama.py, reconciler=sync_panorama_module.py -->

> **自动生成**：本节由 generate_blueprint_panorama.py 从全景真源派生，禁止手写。
> 生成命令：`python scripts/governance/d5_architecture/generators/generate_blueprint_panorama.py MOD-BT-021`

#### 全景位置

| 图 | 位置 | 状态 | 链接 |
|----|------|------|------|
| 依赖图 (depgraph) | `blueprint_id=MOD-BT-021` 的 2 个 file 节点 | production | `extract_depgraph.py --modules MOD-BT-021` |
| 数据流图 (dataflow) | 1 个 Dataset / 1 个 Job | planned | `apply_dataflowgraph.py --list-datasets` |
| 决策架构图 (decision) | 0 个决策节点 / 1 个决策层 | N/A | `generate_decision_diagram.py` |
| 蓝图 (blueprint) | 本文件 | Active | — |

#### 四核心字段

| 字段 | depgraph 值（真源） | 蓝图 frontmatter 值（声明） | 是否一致 |
|------|-------------------|--------------------------|:-------:|
| module_id | MOD-BT-021 | MOD-BT-021 | ✅ |
| domain_id | N/A | N/A | ✅ |
| build_status | production | production | ✅ |
| file_count | 2 文件 | N/A | — |

> 冲突时以 depgraph 为准（ARCH-056 + ARCH-MM-001 声明 vs 验证框架）。

---

## 7. 已实现代码完整路径索引

> **AGENTS.md §6.1 蓝图-代码同步强制约定**——本节是蓝图与磁盘代码的「地址簿」。
> 蓝图声称的文件必须与磁盘实际一致。不一致 = 蓝图漂移 = 下一个 AI session 冷启动时被误导。
> **AUTOGEN**：本表由 sync_blueprint_code_index.py 从 depgraph.nodes 运营态（build_status∈generated/testing/stable）单向派生，禁止手写；重跑本脚本幂等更新。
> 

### 7.1 测试文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `tests/backtest/test_param_analyzer.py` | ✅ 已实现 | |

### 7.5 路径索引使用指南

**新 AI session 读取顺序**：
1. 读本蓝图 §7（本节）→ 知道「哪些已实现、在哪里」
2. 读模块分解 → 知道「每个模块的职责和 AI 自治权限」
3. 读施工 Phase 规划 → 知道「下一步该做什么」

**路径约定**：
- 所有路径相对于 `D:\ZephyrAlpha\\`
- 源码在 `src/zephyr/` 下
- 测试在 `tests/` 下
- 配置在 `config/` 下
- 治理脚本在 `scripts/governance/` 下


