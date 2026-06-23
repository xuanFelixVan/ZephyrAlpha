---
doc_type: domain_architecture_doc
title: D-BACKTEST 回测架构文档
version: "1.0"
status: active
date: 2026-06-23
owner: auto-generator
ttl: permanent
---

# D-BACKTEST 回测架构文档

> 本文档由 generate_domain_doc.py 从 depgraph.db 自动生成
> 最后更新: 2026-06-23 23:25:14
> 数据源: depgraph.db nodes表 + edges表

## 域概览

| 属性 | 值 |
|------|-----|
| 域ID | D-BACKTEST |
| 域名称 | 回测 |
| 架构层 | L2_domain |
| 模块总数 | 9 |
| 设计态模块 | 2 |
| 原型态模块 | 1 |
| 生产态模块 | 0 |
| 容量 | 0/150 (正常) |
| 描述 | 历史回测、参数寻优、过拟合检测、绩效归因。策略验证引擎。 |

## 模块清单

共 9 个模块（按路径排序，最多显示前 200 个）

| 模块路径 | 蓝图ID | 构建状态 | 设计成熟度 | 入度 | 出度 |
|---------|--------|---------|-----------|:---:|:---:|
| D-BACKTEST/Backtest Pipeline Process 回测管线进程 |  | design_only | design | 0 | 0 |
| src/zephyr/backtest/ | MOD-BACKTEST | design_only | design | 0 | 0 |
| src/zephyr/backtest/__init__.py | MOD-BACKTEST | orphan | prototype | 0 | 2 |
| src/zephyr/backtest/_extensions/__init__.py | MOD-BACKTEST | orphan | scaffold_placeholder | 0 | 0 |
| src/zephyr/backtest/api/__init__.py | MOD-BACKTEST | orphan | scaffold_placeholder | 0 | 0 |
| src/zephyr/backtest/core/__init__.py | MOD-BACKTEST | orphan | scaffold_placeholder | 0 | 0 |
| src/zephyr/backtest/infrastructure/__init__.py | MOD-BACKTEST | orphan | scaffold_placeholder | 0 | 0 |
| src/zephyr/backtest/models/__init__.py | MOD-BACKTEST | orphan | scaffold_placeholder | 0 | 0 |
| src/zephyr/backtest/services/__init__.py | MOD-BACKTEST | orphan | scaffold_placeholder | 0 | 0 |

## 跨域依赖

### 本域依赖的其他域（出边）

| 目标域 | 依赖数 | 依赖类型 |
|--------|:---:|---------|
| D-RISK | 3 | data,event,contract |
| D-SIMULATION | 1 | contract |
| D-SIGNAL | 1 | contract |
| D-FACTOR | 1 | contract |
| D-COMPLIANCE | 1 | contract |

### 依赖本域的其他域（入边）

无跨域入边依赖

## 域内依赖图

详见 [d_backtest_dependency.mmd](d_backtest_dependency.mmd)
