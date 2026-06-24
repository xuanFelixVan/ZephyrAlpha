---
doc_type: domain_architecture_diagram
title: D-SIGNAL_FUNDAMENTAL 基本面信号架构图
version: "1.0"
status: active
date: 2026-06-24
owner: auto-generator
ttl: permanent
---

# 40_d_signal_fundamental / 基本面信号 架构图

> **文档作用 / Purpose**: 以ASCII art可视化展示基本面信号（D-SIGNAL_FUNDAMENTAL）功能域的模块分层架构和依赖关系。

> 本文档由 generate_domain_architecture_diagram.py 从 depgraph.db 自动生成
> 最后更新 / Last Updated: 2026-06-24 21:40:10
> 数据源 / Data Source: depgraph.db nodes表 + edges表

## 架构全景图 / Architecture Overview

> 按 architecture_layer 分层显示 基本面信号（D-SIGNAL_FUNDAMENTAL）的模块分布。共 24 个模块 / 24 modules。

```

┌──────────────────────────────────────────────────────────────────┐
│              L2 领域层 / Domain Layer (24 modules)               │
├──────────────────────────────────────────────────────────────────┤
│   基本面信号  [design]                                           │
│   src/zephyr/signal_fundamental/_extensions/__init__.py  [sca... │
│   src/zephyr/signal_fundamental/api/__init__.py  [scaffold_pl... │
│   src/zephyr/signal_fundamental/capital/__init__.py  [prototype] │
│   src/zephyr/signal_fundamental/capital/capital_allocation_re... │
│   src/zephyr/signal_fundamental/capital/capital_allocator.py ... │
│   src/zephyr/signal_fundamental/capital/default_capital_alloc... │
│   src/zephyr/signal_fundamental/combiner/__init__.py  [protot... │
│   src/zephyr/signal_fundamental/combiner/impl/__init__.py  [p... │
│   src/zephyr/signal_fundamental/combiner/synthesized_signal.p... │
│   src/zephyr/signal_fundamental/core/__init__.py  [scaffold_p... │
│   src/zephyr/signal_fundamental/gen/__init__.py  [prototype]     │
│   src/zephyr/signal_fundamental/gen/aggregator_base.py  [prot... │
│   src/zephyr/signal_fundamental/gen/implementations/__init__.... │
│   src/zephyr/signal_fundamental/gen/implementations/default_s... │
│   src/zephyr/signal_fundamental/infrastructure/__init__.py  [... │
│   src/zephyr/signal_fundamental/models/__init__.py  [scaffold... │
│   src/zephyr/signal_fundamental/services/__init__.py  [scaffo... │
│   ...还有 6 个模块 / 6 more modules                              │
└──────────────────────────────────────────────────────────────────┘

```

## 模块分层清单 / Module Layered List

> 按 architecture_layer 分组的模块清单（共 24 个模块 / 24 modules）。

### L2 领域层 / Domain Layer (24 modules)

| # | 模块路径 / Module Path | 模块名称 / Module Name | 成熟度 / Maturity | 构建状态 / Build Status |
|:--:|---------|---------|:---:|:---:|
| 1 | src/zephyr/signal_fundamental/ | 基本面信号 | design | design_only |
| 2 | src/zephyr/signal_fundamental/_extensions/__init__.py | src/zephyr/signal_fundamental/_extens... | scaffold_placeholder | orphan |
| 3 | src/zephyr/signal_fundamental/api/__init__.py | src/zephyr/signal_fundamental/api/__i... | scaffold_placeholder | orphan |
| 4 | src/zephyr/signal_fundamental/capital/__init__.py | src/zephyr/signal_fundamental/capital... | prototype | draft |
| 5 | src/zephyr/signal_fundamental/capital/capital_allocation_... | src/zephyr/signal_fundamental/capital... | prototype | draft |
| 6 | src/zephyr/signal_fundamental/capital/capital_allocator.py | src/zephyr/signal_fundamental/capital... | prototype | draft |
| 7 | src/zephyr/signal_fundamental/capital/default_capital_all... | src/zephyr/signal_fundamental/capital... | prototype | draft |
| 8 | src/zephyr/signal_fundamental/combiner/__init__.py | src/zephyr/signal_fundamental/combine... | prototype | draft |
| 9 | src/zephyr/signal_fundamental/combiner/impl/__init__.py | src/zephyr/signal_fundamental/combine... | prototype | draft |
| 10 | src/zephyr/signal_fundamental/combiner/synthesized_signal.py | src/zephyr/signal_fundamental/combine... | prototype | draft |
| 11 | src/zephyr/signal_fundamental/core/__init__.py | src/zephyr/signal_fundamental/core/__... | scaffold_placeholder | orphan |
| 12 | src/zephyr/signal_fundamental/gen/__init__.py | src/zephyr/signal_fundamental/gen/__i... | prototype | draft |
| 13 | src/zephyr/signal_fundamental/gen/aggregator_base.py | src/zephyr/signal_fundamental/gen/agg... | prototype | draft |
| 14 | src/zephyr/signal_fundamental/gen/implementations/__init_... | src/zephyr/signal_fundamental/gen/imp... | prototype | draft |
| 15 | src/zephyr/signal_fundamental/gen/implementations/default... | src/zephyr/signal_fundamental/gen/imp... | production | draft |
| 16 | src/zephyr/signal_fundamental/infrastructure/__init__.py | src/zephyr/signal_fundamental/infrast... | scaffold_placeholder | orphan |
| 17 | src/zephyr/signal_fundamental/models/__init__.py | src/zephyr/signal_fundamental/models/... | scaffold_placeholder | orphan |
| 18 | src/zephyr/signal_fundamental/services/__init__.py | src/zephyr/signal_fundamental/service... | scaffold_placeholder | orphan |
| 19 | src/zephyr/signal_fundamental/strategy/__init__.py | src/zephyr/signal_fundamental/strateg... | prototype | draft |
| 20 | src/zephyr/signal_fundamental/strategy/capital_allocator.py | src/zephyr/signal_fundamental/strateg... | prototype | draft |
| 21 | src/zephyr/signal_fundamental/strategy/implementations/__... | src/zephyr/signal_fundamental/strateg... | prototype | draft |
| 22 | src/zephyr/signal_fundamental/strategy/implementations/de... | src/zephyr/signal_fundamental/strateg... | production | draft |
| 23 | src/zephyr/signal_fundamental/synth/__init__.py | src/zephyr/signal_fundamental/synth/_... | prototype | draft |
| 24 | src/zephyr/signal_fundamental/synth/signal_synthesizer.py | src/zephyr/signal_fundamental/synth/s... | production | draft |

## 依赖关系图 / Dependency Graph

> 域内模块依赖关系（共 19 条 / 19 edges）。按依赖类型分组，使用 → 表示方向。

```

┌──────────────────────────────────────────────────────────────────┐
│       依赖关系图 / Dependency Graph (共 19 条 / 19 edges)        │
├──────────────────────────────────────────────────────────────────┤
│   依赖类型数 / Dependency Types: 2                               │
│   [import_depends]: 17 条 / edges                                │
│   [config_depends]: 2 条 / edges                                 │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│                 [import_depends] (17 条 / edges)                 │
├──────────────────────────────────────────────────────────────────┤
│   capital_allocator.py → aggregator_base.py                      │
│   __init__.py → capital_allocator.py                             │
│   __init__.py → capital_allocation_result.py                     │
│   __init__.py → default_capital_allocator.py                     │
│   default_capital_allocator.py → aggregator_base.py              │
│   __init__.py → default_signal_aggregator.py                     │
│   __init__.py → default_capital_allocator.py                     │
│   __init__.py → aggregator_base.py                               │
│   __init__.py → capital_allocator.py                             │
│   __init__.py → signal_synthesizer.py                            │
│   default_signal_aggregator.py → aggregator_base.py              │
│   __init__.py → default_signal_aggregator.py                     │
│   default_capital_allocator.py → aggregator_base.py              │
│   __init__.py → capital_allocator.py                             │
│   __init__.py → default_capital_allocator.py                     │
│   capital_allocator.py → aggregator_base.py                      │
│   __init__.py → signal_synthesizer.py                            │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│                 [config_depends] (2 条 / edges)                  │
├──────────────────────────────────────────────────────────────────┤
│   synthesized_signal.py → __init__.py                            │
│   __init__.py → aggregator_base.py                               │
└──────────────────────────────────────────────────────────────────┘

```

## 说明 / Notes

- **数据源 / Data Source**: `depgraph.db` 的 `nodes`、`edges`、`domains` 表
- **生成器 / Generator**: `generate_domain_architecture_diagram.py`
- **维护方式 / Maintenance**: 自动生成，depgraph.db 变更时 CI 自动刷新
- **文件名规则 / File Naming**: `{编号:02d}_{域ID小写}_architecture.md`，如 `40_d_signal_fundamental_architecture.md`
- **图例说明 / Legend**: `[production]`=已上线 / `[design]`=设计中 / `[prototype]`=原型 / `[unknown]`=未知
