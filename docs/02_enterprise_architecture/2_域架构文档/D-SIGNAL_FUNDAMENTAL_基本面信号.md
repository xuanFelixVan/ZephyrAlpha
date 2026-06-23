---
doc_type: domain_architecture_doc
title: D-SIGNAL_FUNDAMENTAL 基本面信号架构文档
version: "1.0"
status: active
date: 2026-06-23
owner: auto-generator
ttl: permanent
---

# D-SIGNAL_FUNDAMENTAL 基本面信号架构文档

> 本文档由 generate_domain_doc.py 从 depgraph.db 自动生成
> 最后更新: 2026-06-23 23:25:14
> 数据源: depgraph.db nodes表 + edges表

## 域概览

| 属性 | 值 |
|------|-----|
| 域ID | D-SIGNAL_FUNDAMENTAL |
| 域名称 | 基本面信号 |
| 架构层 | L2_domain |
| 模块总数 | 24 |
| 设计态模块 | 1 |
| 原型态模块 | 14 |
| 生产态模块 | 3 |
| 容量 | 3/150 (正常) |
| 描述 | 基本面信号域。负责基本面分析信号生成，包括财务指标信号、估值信号、成长性信号、盈利能力信号。拆分自原D-SIGNAL域。 |

## 模块清单

共 24 个模块（按路径排序，最多显示前 200 个）

| 模块路径 | 蓝图ID | 构建状态 | 设计成熟度 | 入度 | 出度 |
|---------|--------|---------|-----------|:---:|:---:|
| src/zephyr/signal_fundamental/ | MOD-SIGNAL_FUNDAMENTAL | design_only | design | 0 | 0 |
| src/zephyr/signal_fundamental/_extensions/__init__.py | MOD-SIGNAL_FUNDAMENTAL | orphan | scaffold_placeholder | 0 | 0 |
| src/zephyr/signal_fundamental/api/__init__.py | MOD-SIGNAL_FUNDAMENTAL | orphan | scaffold_placeholder | 0 | 0 |
| src/zephyr/signal_fundamental/capital/__init__.py | MOD-L03-001 | draft | prototype | 0 | 3 |
| src/zephyr/signal_fundamental/capital/capital_allocation_result.py | MOD-INF-016 | draft | prototype | 1 | 0 |
| src/zephyr/signal_fundamental/capital/capital_allocator.py | MOD-L03-001 | draft | prototype | 1 | 2 |
| src/zephyr/signal_fundamental/capital/default_capital_allocator.py | MOD-L03-001 | draft | prototype | 1 | 3 |
| src/zephyr/signal_fundamental/combiner/__init__.py | MOD-L03-001 | draft | prototype | 1 | 4 |
| src/zephyr/signal_fundamental/combiner/impl/__init__.py | MOD-L03-001 | draft | prototype | 0 | 2 |
| src/zephyr/signal_fundamental/combiner/synthesized_signal.py | MOD-INF-016 | draft | prototype | 0 | 1 |
| src/zephyr/signal_fundamental/core/__init__.py | MOD-SIGNAL_FUNDAMENTAL | orphan | scaffold_placeholder | 0 | 0 |
| src/zephyr/signal_fundamental/gen/__init__.py | MOD-L03-001 | draft | prototype | 0 | 1 |
| src/zephyr/signal_fundamental/gen/aggregator_base.py | MOD-L03-001 | draft | prototype | 7 | 4 |
| src/zephyr/signal_fundamental/gen/implementations/__init__.py | MOD-L03-001 | draft | prototype | 0 | 1 |
| src/zephyr/signal_fundamental/gen/implementations/default_signal_aggregator.py | MOD-L03-001 | draft | production | 5 | 3 |
| src/zephyr/signal_fundamental/infrastructure/__init__.py | MOD-SIGNAL_FUNDAMENTAL | orphan | scaffold_placeholder | 0 | 0 |
| src/zephyr/signal_fundamental/models/__init__.py | MOD-SIGNAL_FUNDAMENTAL | orphan | scaffold_placeholder | 0 | 0 |
| src/zephyr/signal_fundamental/services/__init__.py | MOD-SIGNAL_FUNDAMENTAL | orphan | scaffold_placeholder | 0 | 0 |
| src/zephyr/signal_fundamental/strategy/__init__.py | MOD-L03-001 | draft | prototype | 0 | 1 |
| src/zephyr/signal_fundamental/strategy/capital_allocator.py | MOD-L03-001 | draft | prototype | 2 | 2 |
| src/zephyr/signal_fundamental/strategy/implementations/__init__.py | MOD-L03-001 | draft | prototype | 0 | 1 |
| ...phyr/signal_fundamental/strategy/implementations/default_capital_allocator.py | MOD-L03-001 | draft | production | 3 | 3 |
| src/zephyr/signal_fundamental/synth/__init__.py | MOD-L03-001 | draft | prototype | 0 | 1 |
| src/zephyr/signal_fundamental/synth/signal_synthesizer.py | MOD-L03-001 | draft | production | 5 | 2 |

## 跨域依赖

### 本域依赖的其他域（出边）

| 目标域 | 依赖数 | 依赖类型 |
|--------|:---:|---------|
| D-TRADING | 15 | import_depends |

### 依赖本域的其他域（入边）

| 源域 | 依赖数 | 依赖类型 |
|------|:---:|---------|
| D-GOVERNANCE | 6 | test_depends |
| D-SIGNAL | 1 | import_depends |

## 域内依赖图

详见 [d_signal_fundamental_dependency.mmd](d_signal_fundamental_dependency.mmd)
