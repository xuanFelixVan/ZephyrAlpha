---
doc_type: domain_architecture_doc
title: D-SIGNAL_ASHARE A股特色信号架构文档
version: "1.0"
status: active
date: 2026-06-23
owner: auto-generator
ttl: permanent
---

# D-SIGNAL_ASHARE A股特色信号架构文档

> 本文档由 generate_domain_doc.py 从 depgraph.db 自动生成
> 最后更新: 2026-06-23 13:28:28
> 数据源: depgraph.db nodes表 + edges表

## 域概览

| 属性 | 值 |
|------|-----|
| 域ID | D-SIGNAL_ASHARE |
| 域名称 | A股特色信号 |
| 架构层 | L2_domain |
| 模块总数 | 27 |
| 设计态模块 | 20 |
| 原型态模块 | 1 |
| 生产态模块 | 0 |
| 容量 | 0/150 (正常) |
| 描述 | A股特色信号域。负责A股市场特有的信号生成，包括资金流向信号、龙虎榜信号、融资融券信号、限售股解禁信号。拆分自原D-SIGNAL域。 |

## 模块清单

共 27 个模块（按路径排序，最多显示前 200 个）

| 模块路径 | 蓝图ID | 构建状态 | 设计成熟度 | 入度 | 出度 |
|---------|--------|---------|-----------|:---:|:---:|
| src/zephyr/signal_ashare/__init__.py | MOD-SIGNAL_ASHARE | orphan | prototype | 0 | 0 |
| src/zephyr/signal_ashare/_extensions/__init__.py | MOD-SIGNAL_ASHARE | orphan | scaffold_placeholder | 0 | 0 |
| src/zephyr/signal_ashare/api/__init__.py | MOD-SIGNAL_ASHARE | orphan | scaffold_placeholder | 0 | 0 |
| src/zephyr/signal_ashare/core/__init__.py | MOD-SIGNAL_ASHARE | orphan | scaffold_placeholder | 0 | 0 |
| src/zephyr/signal_ashare/infrastructure/__init__.py | MOD-SIGNAL_ASHARE | orphan | scaffold_placeholder | 0 | 0 |
| src/zephyr/signal_ashare/models/__init__.py | MOD-SIGNAL_ASHARE | orphan | scaffold_placeholder | 0 | 0 |
| src/zephyr/signal_ashare/services/__init__.py | MOD-SIGNAL_ASHARE | orphan | scaffold_placeholder | 0 | 0 |
| 信号域-A股特色-主力资金/D-SIGNAL-21 | MOD-SIGNAL_ASHARE | design_only | design | 0 | 0 |
| 信号域-A股特色-主力资金/D-SIGNAL-23 | MOD-SIGNAL_ASHARE | design_only | design | 0 | 0 |
| 信号域-A股特色-主力资金/D-SIGNAL-36 | MOD-SIGNAL_ASHARE | design_only | design | 0 | 0 |
| 信号域-A股特色-买卖点/D-SIGNAL-47 | MOD-SIGNAL_ASHARE | design_only | design | 0 | 0 |
| 信号域-A股特色-决策评估/D-SIGNAL-27 | MOD-SIGNAL_ASHARE | design_only | design | 0 | 0 |
| 信号域-A股特色-决策评估/D-SIGNAL-45 | MOD-SIGNAL_ASHARE | design_only | design | 0 | 0 |
| 信号域-A股特色-分时技术/D-SIGNAL-29 | MOD-SIGNAL_ASHARE | design_only | design | 0 | 0 |
| 信号域-A股特色-分时技术/D-SIGNAL-40 | MOD-SIGNAL_ASHARE | design_only | design | 0 | 0 |
| 信号域-A股特色-分时技术/D-SIGNAL-51 | MOD-SIGNAL_ASHARE | design_only | design | 0 | 0 |
| 信号域-A股特色-大盘阶段/D-SIGNAL-31 | MOD-SIGNAL_ASHARE | design_only | design | 0 | 0 |
| 信号域-A股特色-大盘阶段/D-SIGNAL-49 | MOD-SIGNAL_ASHARE | design_only | design | 0 | 0 |
| 信号域-A股特色-情绪周期/D-SIGNAL-25 | MOD-SIGNAL_ASHARE | design_only | design | 0 | 0 |
| 信号域-A股特色-情绪周期/D-SIGNAL-33 | MOD-SIGNAL_ASHARE | design_only | design | 0 | 0 |
| 信号域-A股特色-板块轮动/D-SIGNAL-63 | MOD-SIGNAL_ASHARE | design_only | design | 0 | 0 |
| 信号域-A股特色-涨停封单/D-SIGNAL-53 | MOD-SIGNAL_ASHARE | design_only | design | 0 | 0 |
| 信号域-A股特色-特殊信号/D-SIGNAL-38 | MOD-SIGNAL_ASHARE | design_only | design | 0 | 0 |
| 信号域-A股特色-特殊信号/D-SIGNAL-42 | MOD-SIGNAL_ASHARE | design_only | design | 0 | 0 |
| 信号域-A股特色-特殊信号/D-SIGNAL-55 | MOD-SIGNAL_ASHARE | design_only | design | 0 | 0 |
| 信号域-A股特色-特殊信号/D-SIGNAL-61 | MOD-SIGNAL_ASHARE | design_only | design | 0 | 0 |
| 信号域-A股特色-量化双引擎/D-SIGNAL-57 | MOD-SIGNAL_ASHARE | design_only | design | 0 | 0 |

## 跨域依赖

### 本域依赖的其他域（出边）

无跨域出边依赖

### 依赖本域的其他域（入边）

无跨域入边依赖

## 域内依赖图

详见 [d_signal_ashare_dependency.mmd](d_signal_ashare_dependency.mmd)
