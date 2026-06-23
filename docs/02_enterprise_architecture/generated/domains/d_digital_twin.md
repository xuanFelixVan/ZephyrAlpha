---
doc_type: domain_architecture_doc
title: D-DIGITAL_TWIN 数字孪生架构文档
version: "1.0"
status: active
date: 2026-06-23
owner: auto-generator
ttl: permanent
---

# D-DIGITAL_TWIN 数字孪生架构文档

> 本文档由 generate_domain_doc.py 从 depgraph.db 自动生成
> 最后更新: 2026-06-23 13:28:28
> 数据源: depgraph.db nodes表 + edges表

## 域概览

| 属性 | 值 |
|------|-----|
| 域ID | D-DIGITAL_TWIN |
| 域名称 | 数字孪生 |
| 架构层 | L2_domain |
| 模块总数 | 13 |
| 设计态模块 | 6 |
| 原型态模块 | 1 |
| 生产态模块 | 0 |
| 容量 | 0/150 (正常) |
| 描述 | 数字孪生与虚拟市场仿真 |

## 模块清单

共 13 个模块（按路径排序，最多显示前 200 个）

| 模块路径 | 蓝图ID | 构建状态 | 设计成熟度 | 入度 | 出度 |
|---------|--------|---------|-----------|:---:|:---:|
| src/zephyr/digital_twin/ | MOD-DIGITAL_TWIN | design_only | design | 0 | 0 |
| src/zephyr/digital_twin/ | MOD-DIGITAL_TWIN | design_only | design | 0 | 3 |
| src/zephyr/digital_twin/__init__.py | MOD-DIGITAL_TWIN | orphan | prototype | 0 | 0 |
| src/zephyr/digital_twin/_extensions/__init__.py | MOD-DIGITAL_TWIN | orphan | scaffold_placeholder | 0 | 0 |
| src/zephyr/digital_twin/agent_sim/ | MOD-DIGITAL_TWIN | design_only | design | 0 | 0 |
| src/zephyr/digital_twin/api/__init__.py | MOD-DIGITAL_TWIN | orphan | scaffold_placeholder | 0 | 0 |
| src/zephyr/digital_twin/core/__init__.py | MOD-DIGITAL_TWIN | orphan | scaffold_placeholder | 0 | 0 |
| src/zephyr/digital_twin/infrastructure/__init__.py | MOD-DIGITAL_TWIN | orphan | scaffold_placeholder | 0 | 0 |
| src/zephyr/digital_twin/market_sim/ | MOD-DIGITAL_TWIN | design_only | design | 0 | 0 |
| src/zephyr/digital_twin/models/__init__.py | MOD-DIGITAL_TWIN | orphan | scaffold_placeholder | 0 | 0 |
| src/zephyr/digital_twin/orderbook_sim/ | MOD-DIGITAL_TWIN | design_only | design | 0 | 0 |
| src/zephyr/digital_twin/scenario/ | MOD-DIGITAL_TWIN | design_only | design | 0 | 0 |
| src/zephyr/digital_twin/services/__init__.py | MOD-DIGITAL_TWIN | orphan | scaffold_placeholder | 0 | 0 |

## 跨域依赖

### 本域依赖的其他域（出边）

无跨域出边依赖

### 依赖本域的其他域（入边）

无跨域入边依赖

## 域内依赖图

详见 [d_digital_twin_dependency.mmd](d_digital_twin_dependency.mmd)
