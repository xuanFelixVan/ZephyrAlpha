---
doc_type: domain_architecture_doc
title: D-EXEC_SIM 执行仿真架构文档
version: "1.0"
status: active
date: 2026-06-24
owner: auto-generator
ttl: permanent
---

# 21_d_exec_sim / 执行仿真

> **文档作用 / Purpose**: 展示 执行仿真（D-EXEC_SIM）功能域的模块清单、域内依赖关系和跨域依赖关系，供架构审查和域治理参考。

> 本文档由 generate_domain_doc.py 从 depgraph.db 自动生成
> 最后更新: 2026-06-24 23:01:53
> 数据源: depgraph.db nodes表 + edges表

## 域基本信息 / Domain Overview

| 字段 | 值 | Field | Value |
|------|------|-------|-------|
| 编号 | 21 | Number | 21 |
| 域ID | D-EXEC_SIM | Domain ID | D-EXEC_SIM |
| 域名称 | 执行仿真 | Domain Name | 执行仿真 |
| 层级 | L2_domain | Layer | L2_domain |
| 模块数 | 8 | Module Count | 8 |
| 域内依赖 | 0 | Internal Dependencies | 0 |
| 跨域入边 | 0 | Cross-domain Incoming | 0 |
| 跨域出边 | 0 | Cross-domain Outgoing | 0 |
| 设计态模块 | 1 | Design Modules | 1 |
| 原型态模块 | 1 | Prototype Modules | 1 |
| 生产态模块 | 0 | Production Modules | 0 |
| 容量 | 8/150 (正常) | Capacity | 8/150 (正常) |
| 描述 | Split from D-SIMULATION | Description | Split from D-SIMULATION |

## 模块清单 / Module List

共 8 个模块（按路径排序，全部显示）

| 模块路径 / Module Path | 模块名称 / Module Name | 设计成熟度 / Maturity | 构建状态 / Build Status |
|---------|---------|-----------|---------|
| src/zephyr/execution_simulation/ | 执行仿真 | design | design_only |
| src/zephyr/execution_simulation/__init__.py |  | prototype | orphan |
| src/zephyr/execution_simulation/_extensions/__init__.py |  | scaffold_placeholder | orphan |
| src/zephyr/execution_simulation/api/__init__.py |  | scaffold_placeholder | orphan |
| src/zephyr/execution_simulation/core/__init__.py |  | scaffold_placeholder | orphan |
| src/zephyr/execution_simulation/infrastructure/__init__.py |  | scaffold_placeholder | orphan |
| src/zephyr/execution_simulation/models/__init__.py |  | scaffold_placeholder | orphan |
| src/zephyr/execution_simulation/services/__init__.py |  | scaffold_placeholder | orphan |

## 域内依赖图 / Internal Dependency Diagram

> 依赖图内嵌在本文档中，IDE 可直接渲染显示。每30个节点一组分页显示。
>
> **图例说明 / Legend**：
> - **实线边框 = 运营态模块**（production，已上线运行）
> - **虚线边框 = 设计态模块**（design，还在设计中）
> - **实线箭头 = 运营态依赖**（已生效的依赖关系）
> - **虚线箭头 = 设计态依赖**（计划中的依赖关系）

```mermaid
graph TD
    subgraph D_EXEC_SIM["D-EXEC_SIM 执行仿真"]
        src_zephyr_execution_simulation["执行仿真 design"]
        src_zephyr_execution_simulation_init_py["src/zephyr/execution_simulation/__init__.py prototype"]
        src_zephyr_execution_simulation_extensions_init_py["src/zephyr/execution_simulation/_extensions/__i... scaffold_placeholder"]
        src_zephyr_execution_simulation_api_init_py["src/zephyr/execution_simulation/api/__init__.py scaffold_placeholder"]
        src_zephyr_execution_simulation_core_init_py["src/zephyr/execution_simulation/core/__init__.py scaffold_placeholder"]
        src_zephyr_execution_simulation_infrastructure_init_py["src/zephyr/execution_simulation/infrastructure/... scaffold_placeholder"]
        src_zephyr_execution_simulation_models_init_py["src/zephyr/execution_simulation/models/__init__.py scaffold_placeholder"]
        src_zephyr_execution_simulation_services_init_py["src/zephyr/execution_simulation/services/__init... scaffold_placeholder"]
    end
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f5e9,stroke:#1b5e20,stroke-width:1px,color:#000
    classDef external_design fill:#fce4ec,stroke:#880e4f,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class src_zephyr_execution_simulation,src_zephyr_execution_simulation_init_py,src_zephyr_execution_simulation_extensions_init_py,src_zephyr_execution_simulation_api_init_py,src_zephyr_execution_simulation_core_init_py,src_zephyr_execution_simulation_infrastructure_init_py,src_zephyr_execution_simulation_models_init_py,src_zephyr_execution_simulation_services_init_py design
```

## 跨域依赖 / Cross-domain Dependencies

### 本域依赖的其他域（出边）/ Depends On

无跨域出边依赖 / No cross-domain outgoing dependencies

### 依赖本域的其他域（入边）/ Depended By

无跨域入边依赖 / No cross-domain incoming dependencies

## 说明 / Notes

- **数据源 / Data Source**: `depgraph.db` 的 `nodes`、`edges`、`domains` 表
- **生成器 / Generator**: `generate_domain_doc.py`
- **维护方式 / Maintenance**: 自动生成，全景图更新时刷新
- **文件名规则 / File Naming**: `{编号:02d}_{域ID小写}.md`，如 `16_d_trading.md`
