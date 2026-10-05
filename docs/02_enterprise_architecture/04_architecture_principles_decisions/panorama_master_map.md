---
doc_type: architecture_view
title: 全景总图（图之图）
version: "1.0"
status: active
date: auto-generated
owner: auto-generator
ttl: permanent
---

# 全景总图（图之图）

> 机生渲染，禁手改后不回生成。真源: config/panorama_master_map.yaml（nodes=15 edges=21 | 纵轴=9 横轴=6）；对账基准: docs/01_policies_and_standards/sop/governance_sop/alignment_checklist.md §3（在册 15 图，双闭校验随生成器）。

```mermaid
flowchart LR
    subgraph VERTICAL["纵轴·流程视图"]
        decisiongraph["决策流全景图<br/>decisiongraph"]
        TDMAP_001["交易决策地图<br/>TDMAP-001"]
        strategy_production_map["策略生产全景图<br/>strategy_production_map"]
        GOMAP_001["治理运行地图<br/>GOMAP-001"]
        dev_delivery_map["交付流水线全景图<br/>dev_delivery_map"]
        DSCMAP_012["数据供给链图<br/>DSCMAP-012"]
        trading_day_cycle_map["交易日循环全景图<br/>trading_day_cycle_map"]
        construction_workflow_map["AI 施工升级流图<br/>construction_workflow_map"]
        strategy_card_lifecycle_map["策略卡生命周期图<br/>strategy_card_lifecycle_map"]
    end
    subgraph HORIZONTAL["横轴·结构视图"]
        depgraph["依赖全景图<br/>depgraph"]
        dataflowgraph["数据流全景图<br/>dataflowgraph"]
        blueprint["模块蓝图<br/>blueprint"]
        battle_map["作战地图<br/>battle_map"]
        frontend_map["前端全景图<br/>frontend_map"]
        industry_chain_map["产业链全景图<br/>industry_chain_map"]
    end

    DSCMAP_012 -->|"数据供给（供料）"| TDMAP_001
    DSCMAP_012 -->|"数据供给（供料）"| strategy_production_map
    strategy_production_map -->|"策略上岗"| TDMAP_001
    strategy_production_map -->|"卡生命周期"| strategy_card_lifecycle_map
    TDMAP_001 -->|"决策时序投影"| trading_day_cycle_map
    dev_delivery_map -->|"施工变更唯一入口"| depgraph
    dev_delivery_map -->|"施工变更唯一入口"| dataflowgraph
    dev_delivery_map -->|"施工变更唯一入口"| decisiongraph
    dev_delivery_map -->|"施工变更唯一入口"| blueprint
    dev_delivery_map -->|"施工变更唯一入口"| battle_map
    dev_delivery_map -->|"施工变更唯一入口"| frontend_map
    dev_delivery_map -->|"施工变更唯一入口"| TDMAP_001
    dev_delivery_map -->|"施工变更唯一入口"| industry_chain_map
    dev_delivery_map -->|"施工变更唯一入口"| strategy_production_map
    dev_delivery_map -->|"施工变更唯一入口"| GOMAP_001
    dev_delivery_map -->|"施工变更唯一入口"| DSCMAP_012
    dev_delivery_map -->|"施工变更唯一入口"| trading_day_cycle_map
    dev_delivery_map -->|"施工变更唯一入口"| construction_workflow_map
    dev_delivery_map -->|"施工变更唯一入口"| strategy_card_lifecycle_map
    construction_workflow_map -->|"施工流终点接交付（Step10 交界）"| dev_delivery_map
    GOMAP_001 -->|"治理运行时守护交付"| dev_delivery_map
```
