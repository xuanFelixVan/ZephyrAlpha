---
doc_type: domain_architecture_doc
title: D-DIGITAL_TWIN 数字孪生架构文档
version: "1.0"
status: active
date: 2026-06-25
owner: auto-generator
ttl: permanent
---

# 26_d_digital_twin / 数字孪生

> **文档作用 / Purpose**: 展示 数字孪生（D-DIGITAL_TWIN）功能域的模块清单、域内依赖关系和跨域依赖关系，供架构审查和域治理参考。

> 本文档由 generate_domain_doc.py 从 depgraph.db 自动生成
> 最后更新: 2026-06-25 18:42:45
> 数据源: depgraph.db nodes表 + edges表

## 域基本信息 / Domain Overview

| 字段 | 值 | Field | Value |
|------|------|-------|-------|
| 编号 | 26 | Number | 26 |
| 域ID | D-DIGITAL_TWIN | Domain ID | D-DIGITAL_TWIN |
| 域名称 | 数字孪生 | Domain Name | 数字孪生 |
| 层级 | L2_domain | Layer | L2_domain |
| 模块数 | 12 | Module Count | 12 |
| 域内依赖 | 0 | Internal Dependencies | 0 |
| 跨域入边 | 0 | Cross-domain Incoming | 0 |
| 跨域出边 | 0 | Cross-domain Outgoing | 0 |
| 设计态模块 | 5 | Design Modules | 5 |
| 原型态模块 | 7 | Prototype Modules | 7 |
| 生产态模块 | 0 | Production Modules | 0 |
| 容量 | 0/150 (正常) | Capacity | 0/150 (正常) |
| 描述 | 数字孪生与虚拟市场仿真 | Description | 数字孪生与虚拟市场仿真 |

## 模块清单 / Module List

共 12 个模块（按路径排序，全部显示）

| 模块路径 / Module Path | 模块名称 / Module Name | 设计成熟度 / Maturity | 构建状态 / Build Status |
|---------|---------|-----------|---------|
| src/zephyr/digital_twin/ | 数字孪生域 | design | planned |
| src/zephyr/digital_twin/__init__.py |  | prototype | deprecated |
| src/zephyr/digital_twin/_extensions/__init__.py |  | prototype | deprecated |
| src/zephyr/digital_twin/agent_sim/ | 智能体仿真 | design | planned |
| src/zephyr/digital_twin/api/__init__.py |  | prototype | deprecated |
| src/zephyr/digital_twin/core/__init__.py |  | prototype | deprecated |
| src/zephyr/digital_twin/infrastructure/__init__.py |  | prototype | deprecated |
| src/zephyr/digital_twin/market_sim/ | 虚拟市场仿真 | design | planned |
| src/zephyr/digital_twin/models/__init__.py |  | prototype | deprecated |
| src/zephyr/digital_twin/orderbook_sim/ | 订单簿仿真 | design | planned |
| src/zephyr/digital_twin/scenario/ | 场景引擎 | design | planned |
| src/zephyr/digital_twin/services/__init__.py |  | prototype | deprecated |

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
    subgraph D_DIGITAL_TWIN["D-DIGITAL_TWIN 数字孪生"]
        src_zephyr_digital_twin["数字孪生域 design"]
        src_zephyr_digital_twin_init_py["src/zephyr/digital_twin/__init__.py prototype"]
        src_zephyr_digital_twin_extensions_init_py["src/zephyr/digital_twin/_extensions/__init__.py prototype"]
        src_zephyr_digital_twin_agent_sim["智能体仿真 design"]
        src_zephyr_digital_twin_api_init_py["src/zephyr/digital_twin/api/__init__.py prototype"]
        src_zephyr_digital_twin_core_init_py["src/zephyr/digital_twin/core/__init__.py prototype"]
        src_zephyr_digital_twin_infrastructure_init_py["src/zephyr/digital_twin/infrastructure/__init__.py prototype"]
        src_zephyr_digital_twin_market_sim["虚拟市场仿真 design"]
        src_zephyr_digital_twin_models_init_py["src/zephyr/digital_twin/models/__init__.py prototype"]
        src_zephyr_digital_twin_orderbook_sim["订单簿仿真 design"]
        src_zephyr_digital_twin_scenario["场景引擎 design"]
        src_zephyr_digital_twin_services_init_py["src/zephyr/digital_twin/services/__init__.py prototype"]
    end
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f5e9,stroke:#1b5e20,stroke-width:1px,color:#000
    classDef external_design fill:#fce4ec,stroke:#880e4f,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class src_zephyr_digital_twin,src_zephyr_digital_twin_init_py,src_zephyr_digital_twin_extensions_init_py,src_zephyr_digital_twin_agent_sim,src_zephyr_digital_twin_api_init_py,src_zephyr_digital_twin_core_init_py,src_zephyr_digital_twin_infrastructure_init_py,src_zephyr_digital_twin_market_sim,src_zephyr_digital_twin_models_init_py,src_zephyr_digital_twin_orderbook_sim,src_zephyr_digital_twin_scenario,src_zephyr_digital_twin_services_init_py design
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
