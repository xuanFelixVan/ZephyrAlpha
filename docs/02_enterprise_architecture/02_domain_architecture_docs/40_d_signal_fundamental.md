---
doc_type: domain_architecture_doc
title: D-SIGNAL_FUNDAMENTAL 基本面信号架构文档
version: "1.0"
status: active
date: 2026-06-24
owner: auto-generator
ttl: permanent
---

# 40_d_signal_fundamental 域文档

> 本文档由 generate_domain_doc.py 从 depgraph.db 自动生成
> 最后更新: 2026-06-24 02:24:12
> 数据源: depgraph.db nodes表 + edges表

## 域基本信息 / Domain Overview

| 字段 | 值 | Field | Value |
|------|------|-------|-------|
| 编号 | 40 | Number | 40 |
| 域ID | D-SIGNAL_FUNDAMENTAL | Domain ID | D-SIGNAL_FUNDAMENTAL |
| 域名称 | 基本面信号 | Domain Name | 基本面信号 |
| 层级 | L2_domain | Layer | L2_domain |
| 模块数 | 24 | Module Count | 24 |
| 域内依赖 | 19 | Internal Dependencies | 19 |
| 跨域入边 | 7 | Cross-domain Incoming | 7 |
| 跨域出边 | 15 | Cross-domain Outgoing | 15 |
| 设计态模块 | 1 | Design Modules | 1 |
| 原型态模块 | 14 | Prototype Modules | 14 |
| 生产态模块 | 3 | Production Modules | 3 |
| 容量 | 24/150 (正常) | Capacity | 24/150 (正常) |
| 描述 | 基本面信号域。负责基本面分析信号生成，包括财务指标信号、估值信号、成长性信号、盈利能力信号。拆分自原D-SIGNAL域。 | Description | 基本面信号域。负责基本面分析信号生成，包括财务指标信号、估值信号、成长性信号、盈利能力信号。拆分自原D-SIGNAL域。 |

## 模块清单 / Module List

共 24 个模块（按路径排序，最多显示前 200 个）

| 模块路径 | 模块名称 | 设计成熟度 | 构建状态 | Module Path | Module Name | Maturity | Build Status |
|---------|---------|-----------|---------|-------------|-------------|----------|--------------|
| src/zephyr/signal_fundamental/ | 基本面信号 | design | design_only | src/zephyr/signal_fundamental/ | 基本面信号 | design | design_only |
| src/zephyr/signal_fundamental/_extensions/__init__.py |  | scaffold_placeholder | orphan | src/zephyr/signal_fundamental/_extensions/__init__.py |  | scaffold_placeholder | orphan |
| src/zephyr/signal_fundamental/api/__init__.py |  | scaffold_placeholder | orphan | src/zephyr/signal_fundamental/api/__init__.py |  | scaffold_placeholder | orphan |
| src/zephyr/signal_fundamental/capital/__init__.py |  | prototype | draft | src/zephyr/signal_fundamental/capital/__init__.py |  | prototype | draft |
| src/zephyr/signal_fundamental/capital/capital_allocation_result.py |  | prototype | draft | src/zephyr/signal_fundamental/capital/capital_allocation_result.py |  | prototype | draft |
| src/zephyr/signal_fundamental/capital/capital_allocator.py |  | prototype | draft | src/zephyr/signal_fundamental/capital/capital_allocator.py |  | prototype | draft |
| src/zephyr/signal_fundamental/capital/default_capital_allocator.py |  | prototype | draft | src/zephyr/signal_fundamental/capital/default_capital_allocator.py |  | prototype | draft |
| src/zephyr/signal_fundamental/combiner/__init__.py |  | prototype | draft | src/zephyr/signal_fundamental/combiner/__init__.py |  | prototype | draft |
| src/zephyr/signal_fundamental/combiner/impl/__init__.py |  | prototype | draft | src/zephyr/signal_fundamental/combiner/impl/__init__.py |  | prototype | draft |
| src/zephyr/signal_fundamental/combiner/synthesized_signal.py |  | prototype | draft | src/zephyr/signal_fundamental/combiner/synthesized_signal.py |  | prototype | draft |
| src/zephyr/signal_fundamental/core/__init__.py |  | scaffold_placeholder | orphan | src/zephyr/signal_fundamental/core/__init__.py |  | scaffold_placeholder | orphan |
| src/zephyr/signal_fundamental/gen/__init__.py |  | prototype | draft | src/zephyr/signal_fundamental/gen/__init__.py |  | prototype | draft |
| src/zephyr/signal_fundamental/gen/aggregator_base.py |  | prototype | draft | src/zephyr/signal_fundamental/gen/aggregator_base.py |  | prototype | draft |
| src/zephyr/signal_fundamental/gen/implementations/__init__.py |  | prototype | draft | src/zephyr/signal_fundamental/gen/implementations/__init__.py |  | prototype | draft |
| src/zephyr/signal_fundamental/gen/implementations/default_signal_aggregator.py |  | production | draft | src/zephyr/signal_fundamental/gen/implementations/default_signal_aggregator.py |  | production | draft |
| src/zephyr/signal_fundamental/infrastructure/__init__.py |  | scaffold_placeholder | orphan | src/zephyr/signal_fundamental/infrastructure/__init__.py |  | scaffold_placeholder | orphan |
| src/zephyr/signal_fundamental/models/__init__.py |  | scaffold_placeholder | orphan | src/zephyr/signal_fundamental/models/__init__.py |  | scaffold_placeholder | orphan |
| src/zephyr/signal_fundamental/services/__init__.py |  | scaffold_placeholder | orphan | src/zephyr/signal_fundamental/services/__init__.py |  | scaffold_placeholder | orphan |
| src/zephyr/signal_fundamental/strategy/__init__.py |  | prototype | draft | src/zephyr/signal_fundamental/strategy/__init__.py |  | prototype | draft |
| src/zephyr/signal_fundamental/strategy/capital_allocator.py |  | prototype | draft | src/zephyr/signal_fundamental/strategy/capital_allocator.py |  | prototype | draft |
| src/zephyr/signal_fundamental/strategy/implementations/__init__.py |  | prototype | draft | src/zephyr/signal_fundamental/strategy/implementations/__init__.py |  | prototype | draft |
| ...phyr/signal_fundamental/strategy/implementations/default_capital_allocator.py |  | production | draft | ...phyr/signal_fundamental/strategy/implementations/default_capital_allocator.py |  | production | draft |
| src/zephyr/signal_fundamental/synth/__init__.py |  | prototype | draft | src/zephyr/signal_fundamental/synth/__init__.py |  | prototype | draft |
| src/zephyr/signal_fundamental/synth/signal_synthesizer.py |  | production | draft | src/zephyr/signal_fundamental/synth/signal_synthesizer.py |  | production | draft |

## 域内依赖图 / Internal Dependency Diagram

> 依赖图内嵌在本文档中，IDE 可直接渲染显示。
>
> **图例说明 / Legend**：
> - **实线边框 = 运营态模块**（production，已上线运行）
> - **虚线边框 = 设计态模块**（design，还在设计中）
> - **实线箭头 = 运营态依赖**（已生效的依赖关系）
> - **虚线箭头 = 设计态依赖**（计划中的依赖关系）

```mermaid
graph TD
    subgraph D_SIGNAL_FUNDAMENTAL["D-SIGNAL_FUNDAMENTAL 基本面信号"]
        src_zephyr_signal_fundamental["基本面信号 design"]
        src_zephyr_signal_fundamental_extensions_init_py["src/zephyr/signal_fundamental/_extensions/__ini... scaffold_placeholder"]
        src_zephyr_signal_fundamental_api_init_py["src/zephyr/signal_fundamental/api/__init__.py scaffold_placeholder"]
        src_zephyr_signal_fundamental_capital_init_py["src/zephyr/signal_fundamental/capital/__init__.py prototype"]
        src_zephyr_signal_fundamental_capital_capital_allocation_result_py["src/zephyr/signal_fundamental/capital/capital_a... prototype"]
        src_zephyr_signal_fundamental_capital_capital_allocator_py["src/zephyr/signal_fundamental/capital/capital_a... prototype"]
        src_zephyr_signal_fundamental_capital_default_capital_allocator_py["src/zephyr/signal_fundamental/capital/default_c... prototype"]
        src_zephyr_signal_fundamental_combiner_init_py["src/zephyr/signal_fundamental/combiner/__init__.py prototype"]
        src_zephyr_signal_fundamental_combiner_impl_init_py["src/zephyr/signal_fundamental/combiner/impl/__i... prototype"]
        src_zephyr_signal_fundamental_combiner_synthesized_signal_py["src/zephyr/signal_fundamental/combiner/synthesi... prototype"]
        src_zephyr_signal_fundamental_core_init_py["src/zephyr/signal_fundamental/core/__init__.py scaffold_placeholder"]
        src_zephyr_signal_fundamental_gen_init_py["src/zephyr/signal_fundamental/gen/__init__.py prototype"]
        src_zephyr_signal_fundamental_gen_aggregator_base_py["src/zephyr/signal_fundamental/gen/aggregator_ba... prototype"]
        src_zephyr_signal_fundamental_gen_implementations_init_py["src/zephyr/signal_fundamental/gen/implementatio... prototype"]
        src_zephyr_signal_fundamental_gen_implementations_default_signal_aggregator_py["src/zephyr/signal_fundamental/gen/implementatio... production"]
        src_zephyr_signal_fundamental_infrastructure_init_py["src/zephyr/signal_fundamental/infrastructure/__... scaffold_placeholder"]
        src_zephyr_signal_fundamental_models_init_py["src/zephyr/signal_fundamental/models/__init__.py scaffold_placeholder"]
        src_zephyr_signal_fundamental_services_init_py["src/zephyr/signal_fundamental/services/__init__.py scaffold_placeholder"]
        src_zephyr_signal_fundamental_strategy_init_py["src/zephyr/signal_fundamental/strategy/__init__.py prototype"]
        src_zephyr_signal_fundamental_strategy_capital_allocator_py["src/zephyr/signal_fundamental/strategy/capital_... prototype"]
        src_zephyr_signal_fundamental_strategy_implementations_init_py["src/zephyr/signal_fundamental/strategy/implemen... prototype"]
        src_zephyr_signal_fundamental_strategy_implementations_default_capital_allocator_py["src/zephyr/signal_fundamental/strategy/implemen... production"]
        src_zephyr_signal_fundamental_synth_init_py["src/zephyr/signal_fundamental/synth/__init__.py prototype"]
        src_zephyr_signal_fundamental_synth_signal_synthesizer_py["src/zephyr/signal_fundamental/synth/signal_synt... production"]
    end
    src_zephyr_signal_fundamental_capital_capital_allocator_py -.->|import_depends| src_zephyr_signal_fundamental_gen_aggregator_base_py
    src_zephyr_signal_fundamental_capital_init_py -.->|import_depends| src_zephyr_signal_fundamental_capital_capital_allocator_py
    src_zephyr_signal_fundamental_capital_init_py -.->|import_depends| src_zephyr_signal_fundamental_capital_capital_allocation_result_py
    src_zephyr_signal_fundamental_capital_init_py -.->|import_depends| src_zephyr_signal_fundamental_capital_default_capital_allocator_py
    src_zephyr_signal_fundamental_capital_default_capital_allocator_py -.->|import_depends| src_zephyr_signal_fundamental_gen_aggregator_base_py
    src_zephyr_signal_fundamental_combiner_impl_init_py -.->|import_depends| src_zephyr_signal_fundamental_gen_implementations_default_signal_aggregator_py
    src_zephyr_signal_fundamental_combiner_impl_init_py -.->|import_depends| src_zephyr_signal_fundamental_strategy_implementations_default_capital_allocator_py
    src_zephyr_signal_fundamental_combiner_synthesized_signal_py -.->|config_depends| src_zephyr_signal_fundamental_combiner_init_py
    src_zephyr_signal_fundamental_combiner_init_py -.->|import_depends| src_zephyr_signal_fundamental_gen_aggregator_base_py
    src_zephyr_signal_fundamental_combiner_init_py -.->|import_depends| src_zephyr_signal_fundamental_strategy_capital_allocator_py
    src_zephyr_signal_fundamental_combiner_init_py -.->|import_depends| src_zephyr_signal_fundamental_synth_signal_synthesizer_py
    src_zephyr_signal_fundamental_gen_implementations_default_signal_aggregator_py -.->|import_depends| src_zephyr_signal_fundamental_gen_aggregator_base_py
    src_zephyr_signal_fundamental_gen_init_py -.->|config_depends| src_zephyr_signal_fundamental_gen_aggregator_base_py
    src_zephyr_signal_fundamental_gen_implementations_init_py -.->|import_depends| src_zephyr_signal_fundamental_gen_implementations_default_signal_aggregator_py
    src_zephyr_signal_fundamental_strategy_implementations_default_capital_allocator_py -.->|import_depends| src_zephyr_signal_fundamental_gen_aggregator_base_py
    src_zephyr_signal_fundamental_strategy_init_py -.->|import_depends| src_zephyr_signal_fundamental_strategy_capital_allocator_py
    src_zephyr_signal_fundamental_strategy_implementations_init_py -.->|import_depends| src_zephyr_signal_fundamental_strategy_implementations_default_capital_allocator_py
    src_zephyr_signal_fundamental_strategy_capital_allocator_py -.->|import_depends| src_zephyr_signal_fundamental_gen_aggregator_base_py
    src_zephyr_signal_fundamental_synth_init_py -.->|import_depends| src_zephyr_signal_fundamental_synth_signal_synthesizer_py
    D_TRADING["D-TRADING production"]
    src_zephyr_signal_fundamental_capital_capital_allocator_py -.->|import_depends| D_TRADING
    src_zephyr_signal_fundamental_capital_default_capital_allocator_py -.->|import_depends| D_TRADING
    src_zephyr_signal_fundamental_capital_default_capital_allocator_py -.->|import_depends| D_TRADING
    src_zephyr_signal_fundamental_gen_aggregator_base_py -.->|import_depends| D_TRADING
    src_zephyr_signal_fundamental_gen_aggregator_base_py -.->|import_depends| D_TRADING
    src_zephyr_signal_fundamental_gen_aggregator_base_py -.->|import_depends| D_TRADING
    src_zephyr_signal_fundamental_gen_aggregator_base_py -.->|import_depends| D_TRADING
    src_zephyr_signal_fundamental_combiner_init_py -.->|import_depends| D_TRADING
    src_zephyr_signal_fundamental_gen_implementations_default_signal_aggregator_py -->|import_depends| D_TRADING
    src_zephyr_signal_fundamental_gen_implementations_default_signal_aggregator_py -->|import_depends| D_TRADING
    src_zephyr_signal_fundamental_strategy_implementations_default_capital_allocator_py -->|import_depends| D_TRADING
    src_zephyr_signal_fundamental_strategy_implementations_default_capital_allocator_py -->|import_depends| D_TRADING
    src_zephyr_signal_fundamental_strategy_capital_allocator_py -.->|import_depends| D_TRADING
    src_zephyr_signal_fundamental_synth_signal_synthesizer_py -->|import_depends| D_TRADING
    src_zephyr_signal_fundamental_synth_signal_synthesizer_py -->|import_depends| D_TRADING
    D_GOVERNANCE["D-GOVERNANCE prototype"]
    D_GOVERNANCE -.->|test_depends| src_zephyr_signal_fundamental_gen_implementations_default_signal_aggregator_py
    D_GOVERNANCE -.->|test_depends| src_zephyr_signal_fundamental_gen_implementations_default_signal_aggregator_py
    D_GOVERNANCE -.->|test_depends| src_zephyr_signal_fundamental_gen_implementations_default_signal_aggregator_py
    D_GOVERNANCE -.->|test_depends| src_zephyr_signal_fundamental_strategy_implementations_default_capital_allocator_py
    D_SIGNAL["D-SIGNAL production"]
    D_SIGNAL -->|import_depends| src_zephyr_signal_fundamental_synth_signal_synthesizer_py
    D_GOVERNANCE -.->|test_depends| src_zephyr_signal_fundamental_synth_signal_synthesizer_py
    D_GOVERNANCE -.->|test_depends| src_zephyr_signal_fundamental_synth_signal_synthesizer_py
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f5e9,stroke:#1b5e20,stroke-width:1px,color:#000
    classDef external_design fill:#fce4ec,stroke:#880e4f,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class src_zephyr_signal_fundamental_gen_implementations_default_signal_aggregator_py,src_zephyr_signal_fundamental_strategy_implementations_default_capital_allocator_py,src_zephyr_signal_fundamental_synth_signal_synthesizer_py production
    class src_zephyr_signal_fundamental,src_zephyr_signal_fundamental_extensions_init_py,src_zephyr_signal_fundamental_api_init_py,src_zephyr_signal_fundamental_capital_init_py,src_zephyr_signal_fundamental_capital_capital_allocation_result_py,src_zephyr_signal_fundamental_capital_capital_allocator_py,src_zephyr_signal_fundamental_capital_default_capital_allocator_py,src_zephyr_signal_fundamental_combiner_init_py,src_zephyr_signal_fundamental_combiner_impl_init_py,src_zephyr_signal_fundamental_combiner_synthesized_signal_py,src_zephyr_signal_fundamental_core_init_py,src_zephyr_signal_fundamental_gen_init_py,src_zephyr_signal_fundamental_gen_aggregator_base_py,src_zephyr_signal_fundamental_gen_implementations_init_py,src_zephyr_signal_fundamental_infrastructure_init_py,src_zephyr_signal_fundamental_models_init_py,src_zephyr_signal_fundamental_services_init_py,src_zephyr_signal_fundamental_strategy_init_py,src_zephyr_signal_fundamental_strategy_capital_allocator_py,src_zephyr_signal_fundamental_strategy_implementations_init_py,src_zephyr_signal_fundamental_synth_init_py design
    class D_TRADING,D_SIGNAL external_prod
    class D_GOVERNANCE external_design
```

## 跨域依赖 / Cross-domain Dependencies

### 本域依赖的其他域（出边）/ Depends On

| 目标域 | 依赖数 | 依赖类型 | Target Domain | Count | Type |
|--------|:---:|---------|---------------|:---:|------|
| D-TRADING | 15 | import_depends | D-TRADING | 15 | import_depends |

### 依赖本域的其他域（入边）/ Depended By

| 源域 | 依赖数 | 依赖类型 | Source Domain | Count | Type |
|------|:---:|---------|---------------|:---:|------|
| D-GOVERNANCE | 6 | test_depends | D-GOVERNANCE | 6 | test_depends |
| D-SIGNAL | 1 | import_depends | D-SIGNAL | 1 | import_depends |

## 说明 / Notes

- **数据源 / Data Source**: `depgraph.db` 的 `nodes`、`edges`、`domains` 表
- **生成器 / Generator**: `generate_domain_doc.py`
- **维护方式 / Maintenance**: 自动生成，全景图更新时刷新
- **文件名规则 / File Naming**: `{编号:02d}_{域ID小写}.md`，如 `16_d_trading.md`
