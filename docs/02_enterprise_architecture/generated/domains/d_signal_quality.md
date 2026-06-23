---
doc_type: domain_architecture_doc
title: D-SIGNAL_QUALITY 信号质量架构文档
version: "1.0"
status: active
date: 2026-06-23
owner: auto-generator
ttl: permanent
---

# D-SIGNAL_QUALITY 信号质量架构文档

> 本文档由 generate_domain_doc.py 从 depgraph.db 自动生成
> 最后更新: 2026-06-23 13:28:28
> 数据源: depgraph.db nodes表 + edges表

## 域概览

| 属性 | 值 |
|------|-----|
| 域ID | D-SIGNAL_QUALITY |
| 域名称 | 信号质量 |
| 架构层 | L2_domain |
| 模块总数 | 18 |
| 设计态模块 | 11 |
| 原型态模块 | 1 |
| 生产态模块 | 0 |
| 容量 | 0/150 (正常) |
| 描述 | 信号质量域。负责信号质量评估与监控，包括信号衰减检测、信号相关性分析、信号稳定性评估、信号噪声过滤。拆分自原D-SIGNAL域。 |

## 模块清单

共 18 个模块（按路径排序，最多显示前 200 个）

| 模块路径 | 蓝图ID | 构建状态 | 设计成熟度 | 入度 | 出度 |
|---------|--------|---------|-----------|:---:|:---:|
| src/zephyr/signal_quality/ | MOD-SIGNAL_QUALITY | design_only | design | 0 | 0 |
| src/zephyr/signal_quality/__init__.py | MOD-SIGNAL_QUALITY | orphan | prototype | 0 | 0 |
| src/zephyr/signal_quality/_extensions/__init__.py | MOD-SIGNAL_QUALITY | orphan | scaffold_placeholder | 0 | 0 |
| src/zephyr/signal_quality/api/__init__.py | MOD-SIGNAL_QUALITY | orphan | scaffold_placeholder | 0 | 0 |
| src/zephyr/signal_quality/core/__init__.py | MOD-SIGNAL_QUALITY | orphan | scaffold_placeholder | 0 | 0 |
| src/zephyr/signal_quality/infrastructure/__init__.py | MOD-SIGNAL_QUALITY | orphan | scaffold_placeholder | 0 | 0 |
| src/zephyr/signal_quality/models/__init__.py | MOD-SIGNAL_QUALITY | orphan | scaffold_placeholder | 0 | 0 |
| src/zephyr/signal_quality/services/__init__.py | MOD-SIGNAL_QUALITY | orphan | scaffold_placeholder | 0 | 0 |
| 信号域-信号处理/D-SIGNAL-69 | MOD-SIGNAL_QUALITY | design_only | design | 0 | 0 |
| 信号域-信号处理/D-SIGNAL-71 | MOD-SIGNAL_QUALITY | design_only | design | 0 | 0 |
| 信号域-冲突融合/D-SIGNAL-130 | MOD-SIGNAL_QUALITY | design_only | design | 0 | 0 |
| 信号域-冲突融合/D-SIGNAL-132 | MOD-SIGNAL_QUALITY | design_only | design | 0 | 0 |
| 信号域-合成分配/D-SIGNAL-92 | MOD-SIGNAL_QUALITY | design_only | design | 0 | 0 |
| 信号域-技术指标/D-SIGNAL-118 | MOD-SIGNAL_QUALITY | design_only | design | 0 | 0 |
| 信号域-策略运行时/D-SIGNAL-156 | MOD-SIGNAL_QUALITY | design_only | design | 0 | 0 |
| 信号域-质量降级/D-SIGNAL-77 | MOD-SIGNAL_QUALITY | design_only | design | 0 | 0 |
| 信号域-质量降级/D-SIGNAL-81 | MOD-SIGNAL_QUALITY | design_only | design | 0 | 0 |
| 信号域-质量降级/D-SIGNAL-83 | MOD-SIGNAL_QUALITY | design_only | design | 0 | 0 |

## 跨域依赖

### 本域依赖的其他域（出边）

无跨域出边依赖

### 依赖本域的其他域（入边）

无跨域入边依赖

## 域内依赖图

详见 [d_signal_quality_dependency.mmd](d_signal_quality_dependency.mmd)
