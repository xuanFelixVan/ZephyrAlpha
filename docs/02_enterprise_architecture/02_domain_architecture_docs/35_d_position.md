---
doc_type: domain_architecture_doc
title: D-POSITION 仓位管理架构文档
version: "1.0"
status: active
date: 2026-06-24
owner: auto-generator
ttl: permanent
---

# 35_d_position / 仓位管理

> **文档作用 / Purpose**: 展示 仓位管理（D-POSITION）功能域的模块清单、域内依赖关系和跨域依赖关系，供架构审查和域治理参考。

> 本文档由 generate_domain_doc.py 从 depgraph.db 自动生成
> 最后更新: 2026-06-24 21:40:08
> 数据源: depgraph.db nodes表 + edges表

## 域基本信息 / Domain Overview

| 字段 | 值 | Field | Value |
|------|------|-------|-------|
| 编号 | 35 | Number | 35 |
| 域ID | D-POSITION | Domain ID | D-POSITION |
| 域名称 | 仓位管理 | Domain Name | 仓位管理 |
| 层级 | L2_domain | Layer | L2_domain |
| 模块数 | 77 | Module Count | 77 |
| 域内依赖 | 68 | Internal Dependencies | 68 |
| 跨域入边 | 113 | Cross-domain Incoming | 113 |
| 跨域出边 | 37 | Cross-domain Outgoing | 37 |
| 设计态模块 | 69 | Design Modules | 69 |
| 原型态模块 | 2 | Prototype Modules | 2 |
| 生产态模块 | 0 | Production Modules | 0 |
| 容量 | 77/150 (正常) | Capacity | 77/150 (正常) |
| 描述 | 持仓跟踪、仓位计算、盈亏归因、仓位调整。仓位账本。 | Description | 持仓跟踪、仓位计算、盈亏归因、仓位调整。仓位账本。 |

## 模块清单 / Module List

共 77 个模块（按路径排序，全部显示）

| 模块路径 / Module Path | 模块名称 / Module Name | 设计成熟度 / Maturity | 构建状态 / Build Status |
|---------|---------|-----------|---------|
| D-POSITION/Anti-Pyramiding Scaler倒金字塔减仓器 | Anti-Pyramiding Scaler倒金字塔减仓器 | design | design_only |
| D-POSITION/Calendar Position Constraint 日历仓位约束 | Calendar Position Constraint 日历仓位约束 | design | design_only |
| D-POSITION/CalendarPositionAlert 日历仓位预警 | CalendarPositionAlert 日历仓位预警 | design | design_only |
| D-POSITION/Capital Curve Manager资金曲线管理器 | Capital Curve Manager资金曲线管理器 | design | design_only |
| D-POSITION/CapitalCurve 资金曲线 | CapitalCurve 资金曲线 | design | design_only |
| D-POSITION/CapitalCurveUpdated 资金曲线已更新 | CapitalCurveUpdated 资金曲线已更新 | design | design_only |
| D-POSITION/Cash Manager现金管理器 | Cash Manager现金管理器 | design | design_only |
| D-POSITION/Corporate Action Processor 公司行为处理器 | Corporate Action Processor 公司行为处理器 | design | design_only |
| D-POSITION/Correlation Regime Monitor Gate 相关性状态监控器门禁 | Correlation Regime Monitor Gate 相关性状态... | design | design_only |
| D-POSITION/Correlation Regime Monitor相关性体制监控器 | Correlation Regime Monitor相关性体制监控器 | design | design_only |
| D-POSITION/Covariance Estimator Gate 协方差估计器门禁 | Covariance Estimator Gate 协方差估计器门禁 | design | design_only |
| D-POSITION/Covariance Estimator协方差矩阵估计器 | Covariance Estimator协方差矩阵估计器 | design | design_only |
| D-POSITION/Cross-Strategy Position Merger Gate 多策略同标仓位合并门禁 | Cross-Strategy Position Merger Gate 多... | design | design_only |
| D-POSITION/Cross-Strategy Position Merger跨策略仓位合并器 | Cross-Strategy Position Merger跨策略仓位合并器 | design | design_only |
| D-POSITION/D-POSITION 仓位 | D-POSITION 仓位 | design | design_only |
| D-POSITION/Daily Loss 5% AUM Liquidation 单日亏损超过AUM 5%清仓 | Daily Loss 5% AUM Liquidation 单日亏损超过A... | design | design_only |
| D-POSITION/Drawdown Controller回撤控制器 | Drawdown Controller回撤控制器 | design | design_only |
| D-POSITION/DriftDetected 漂移已检测 | DriftDetected 漂移已检测 | design | design_only |
| D-POSITION/Dynamic Level Decision 动态级决策 | Dynamic Level Decision 动态级决策 | design | design_only |
| D-POSITION/Every Order Must Pass Risk Check 每笔订单必须经过风控检查 | Every Order Must Pass Risk Check 每笔订单... | design | design_only |
| D-POSITION/Four-track Position Decision Architecture 仓位 | Four-track Position Decision Architec... | design | design_only |
| D-POSITION/Hot Plane Position Data Isolation 仓位 | Hot Plane Position Data Isolation 仓位 | design | design_only |
| D-POSITION/Intraday Position Constraint Gate 日内仓位约束门禁 | Intraday Position Constraint Gate 日内仓... | design | design_only |
| D-POSITION/Intraday Position Constraint 日内仓位约束 | Intraday Position Constraint 日内仓位约束 | design | design_only |
| D-POSITION/KS-L4 Derated Operation KS-L4降级运行 | KS-L4 Derated Operation KS-L4降级运行 | design | design_only |
| D-POSITION/L3 to L3.5 Position Sizing L3→L3.5仓位裁决 | L3 to L3.5 Position Sizing L3→L3.5仓位裁决 | design | design_only |
| D-POSITION/Liquidity Downgrade Mode 流动性降级模式 | Liquidity Downgrade Mode 流动性降级模式 | design | design_only |
| D-POSITION/Liquidity Spiral Three Phases 流动性螺旋三阶段 | Liquidity Spiral Three Phases 流动性螺旋三阶段 | design | design_only |
| D-POSITION/Loss Position Add Hard Block Invariant 亏损标的加仓Hard Block不变量 | Loss Position Add Hard Block Invarian... | design | design_only |
| D-POSITION/No Buy at Limit Up 涨停板不买入 | No Buy at Limit Up 涨停板不买入 | design | design_only |
| D-POSITION/No Order Outside Trading Hours 非交易时段不下单 | No Order Outside Trading Hours 非交易时段不下单 | design | design_only |
| D-POSITION/No Sell at Limit Down 跌停板不卖出 | No Sell at Limit Down 跌停板不卖出 | design | design_only |
| D-POSITION/Order Saga Position Step 仓位订单 | Order Saga Position Step 仓位订单 | design | design_only |
| D-POSITION/Portfolio Level Decision 组合 | Portfolio Level Decision 组合 | design | design_only |
| D-POSITION/Position Arbitration Cannot Bypass Invariant 仓位裁决不可绕过不变量 | Position Arbitration Cannot Bypass In... | design | design_only |
| D-POSITION/Position Audit Logger仓位审计日志 | Position Audit Logger仓位审计日志 | design | design_only |
| D-POSITION/Position Behavior Classifier Gate 持仓行为分类器门禁 | Position Behavior Classifier Gate 持仓行... | design | design_only |
| D-POSITION/Position Behavior Classifier 持仓行为分类器 | Position Behavior Classifier 持仓行为分类器 | design | design_only |
| D-POSITION/Position Drift Monitor仓位漂移监控器 | Position Drift Monitor仓位漂移监控器 | design | design_only |
| D-POSITION/Position Limit Enforcer 持仓限额执行器 | Position Limit Enforcer 持仓限额执行器 | design | design_only |
| D-POSITION/Position Limit Enforcer仓位限制执行器 | Position Limit Enforcer仓位限制执行器 | design | design_only |
| D-POSITION/Position Management 仓位管理唯一裁决中心 | Position Management 仓位管理唯一裁决中心 | design | design_only |
| D-POSITION/Position RPO Zero Invariant 持仓RPO=0不变量 | Position RPO Zero Invariant 持仓RPO=0不变量 | design | design_only |
| D-POSITION/Position Risk Monitor 持仓风险监控器 | Position Risk Monitor 持仓风险监控器 | design | design_only |
| D-POSITION/Position Sizing Engine标级仓位决策引擎 | Position Sizing Engine标级仓位决策引擎 | design | design_only |
| D-POSITION/Position State Machine持仓状态机 | Position State Machine持仓状态机 | design | design_only |
| D-POSITION/Position Time Budget Gate 仓位时间预算门禁 | Position Time Budget Gate 仓位时间预算门禁 | design | design_only |
| D-POSITION/Position Time Budget持仓时间预算器 | Position Time Budget持仓时间预算器 | design | design_only |
| D-POSITION/Position Tracker 持仓跟踪器 | Position Tracker 持仓跟踪器 | design | design_only |
| D-POSITION/Position 持仓聚合根 | Position 持仓聚合根 | design | design_only |
| D-POSITION/PositionPlan 仓位方案 | PositionPlan 仓位方案 | design | design_only |
| D-POSITION/PositionPlan 仓位方案契约 | PositionPlan 仓位方案契约 | design | design_only |
| D-POSITION/PositionSized 仓位已定 | PositionSized 仓位已定 | design | design_only |
| D-POSITION/PositionUpdated 持仓更新契约 | PositionUpdated 持仓更新契约 | design | design_only |
| D-POSITION/Rebalance Engine再平衡决策引擎 | Rebalance Engine再平衡决策引擎 | design | design_only |
| D-POSITION/RebalanceTriggered 再平衡已触发 | RebalanceTriggered 再平衡已触发 | design | design_only |
| D-POSITION/Risk Budget Allocator Gate 风险预算分配器门禁 | Risk Budget Allocator Gate 风险预算分配器门禁 | design | design_only |
| D-POSITION/Risk Budget Allocator风险配额分配器 | Risk Budget Allocator风险配额分配器 | design | design_only |
| D-POSITION/ST/Delisting Risk Next Day Liquidation 持仓股票ST/退市风险次日清仓 | ST/Delisting Risk Next Day Liquidatio... | design | design_only |
| D-POSITION/Scaling-Out Executor Gate 减仓执行器门禁 | Scaling-Out Executor Gate 减仓执行器门禁 | design | design_only |
| D-POSITION/Sell-Position Bidirectional Link卖出-仓位双向联动器 | Sell-Position Bidirectional Link卖出-仓位... | design | design_only |
| D-POSITION/Semi-Kelly Hard Cap Invariant 半Kelly为硬上限不变量 | Semi-Kelly Hard Cap Invariant 半Kelly为... | design | design_only |
| D-POSITION/Single Position 10% AUM Cap 单票持仓不超过AUM的10% | Single Position 10% AUM Cap 单票持仓不超过AU... | design | design_only |
| D-POSITION/State-Position Mapping Immutable Invariant 状态→仓位映射不可AI修改不变量 | State-Position Mapping Immutable Inva... | design | design_only |
| D-POSITION/StateChanged 状态已变更 | StateChanged 状态已变更 | design | design_only |
| D-POSITION/Strategy Level Decision 策略 | Strategy Level Decision 策略 | design | design_only |
| D-POSITION/Symbol Level Decision 标的级决策 | Symbol Level Decision 标的级决策 | design | design_only |
| D-POSITION/Total Position 30% AUM Cap 总仓位不超过AUM的30% | Total Position 30% AUM Cap 总仓位不超过AUM的30% | design | design_only |
| D-POSITION/Unfilled Position Disaster Recovery 仓位 | Unfilled Position Disaster Recovery 仓位 | design | design_only |
| src/zephyr/position/__init__.py |  | prototype | orphan |
| src/zephyr/position/_extensions/__init__.py |  | scaffold_placeholder | orphan |
| src/zephyr/position/api/__init__.py |  | scaffold_placeholder | orphan |
| src/zephyr/position/core/__init__.py |  | scaffold_placeholder | orphan |
| src/zephyr/position/infrastructure/__init__.py |  | scaffold_placeholder | orphan |
| src/zephyr/position/models/__init__.py |  | scaffold_placeholder | orphan |
| src/zephyr/position/position_reconciler.py |  | prototype | draft |
| src/zephyr/position/services/__init__.py |  | scaffold_placeholder | orphan |

## 域内依赖图 / Internal Dependency Diagram

> 依赖图内嵌在本文档中，IDE 可直接渲染显示。每30个节点一组分页显示。
>
> **图例说明 / Legend**：
> - **实线边框 = 运营态模块**（production，已上线运行）
> - **虚线边框 = 设计态模块**（design，还在设计中）
> - **实线箭头 = 运营态依赖**（已生效的依赖关系）
> - **虚线箭头 = 设计态依赖**（计划中的依赖关系）

### 第 1 页 / 共 3 页 / Page 1 of 3

```mermaid
graph TD
    subgraph D_POSITION["D-POSITION 仓位管理"]
        D_POSITION_Anti_Pyramiding_Scaler["Anti-Pyramiding Scaler倒金字塔减仓器 design"]
        D_POSITION_Calendar_Position_Constraint["Calendar Position Constraint 日历仓位约束 design"]
        D_POSITION_CalendarPositionAlert["CalendarPositionAlert 日历仓位预警 design"]
        D_POSITION_Capital_Curve_Manager["Capital Curve Manager资金曲线管理器 design"]
        D_POSITION_CapitalCurve["CapitalCurve 资金曲线 design"]
        D_POSITION_CapitalCurveUpdated["CapitalCurveUpdated 资金曲线已更新 design"]
        D_POSITION_Cash_Manager["Cash Manager现金管理器 design"]
        D_POSITION_Corporate_Action_Processor["Corporate Action Processor 公司行为处理器 design"]
        D_POSITION_Correlation_Regime_Monitor_Gate["Correlation Regime Monitor Gate 相关性状态监控器门禁 design"]
        D_POSITION_Correlation_Regime_Monitor["Correlation Regime Monitor相关性体制监控器 design"]
        D_POSITION_Covariance_Estimator_Gate["Covariance Estimator Gate 协方差估计器门禁 design"]
        D_POSITION_Covariance_Estimator["Covariance Estimator协方差矩阵估计器 design"]
        D_POSITION_Cross_Strategy_Position_Merger_Gate["Cross-Strategy Position Merger Gate 多策略同标仓位合并门禁 design"]
        D_POSITION_Cross_Strategy_Position_Merger["Cross-Strategy Position Merger跨策略仓位合并器 design"]
        D_POSITION_D_POSITION["D-POSITION 仓位 design"]
        D_POSITION_Daily_Loss_5_AUM_Liquidation_AUM_5["Daily Loss 5% AUM Liquidation 单日亏损超过AUM 5%清仓 design"]
        D_POSITION_Drawdown_Controller["Drawdown Controller回撤控制器 design"]
        D_POSITION_DriftDetected["DriftDetected 漂移已检测 design"]
        D_POSITION_Dynamic_Level_Decision["Dynamic Level Decision 动态级决策 design"]
        D_POSITION_Every_Order_Must_Pass_Risk_Check["Every Order Must Pass Risk Check 每笔订单必须经过风控检查 design"]
        D_POSITION_Four_track_Position_Decision_Architecture["Four-track Position Decision Architecture 仓位 design"]
        D_POSITION_Hot_Plane_Position_Data_Isolation["Hot Plane Position Data Isolation 仓位 design"]
        D_POSITION_Intraday_Position_Constraint_Gate["Intraday Position Constraint Gate 日内仓位约束门禁 design"]
        D_POSITION_Intraday_Position_Constraint["Intraday Position Constraint 日内仓位约束 design"]
        D_POSITION_KS_L4_Derated_Operation_KS_L4["KS-L4 Derated Operation KS-L4降级运行 design"]
        D_POSITION_L3_to_L3_5_Position_Sizing_L3_L3_5["L3 to L3.5 Position Sizing L3→L3.5仓位裁决 design"]
        D_POSITION_Liquidity_Downgrade_Mode["Liquidity Downgrade Mode 流动性降级模式 design"]
        D_POSITION_Liquidity_Spiral_Three_Phases["Liquidity Spiral Three Phases 流动性螺旋三阶段 design"]
        D_POSITION_Loss_Position_Add_Hard_Block_Invariant_Hard_Block["Loss Position Add Hard Block Invariant 亏损标的加仓Ha... design"]
        D_POSITION_No_Buy_at_Limit_Up["No Buy at Limit Up 涨停板不买入 design"]
    end
    D_POSITION_Cross_Strategy_Position_Merger -.->|import_depends| D_POSITION_Cash_Manager
    D_POSITION_Cross_Strategy_Position_Merger -.->|config_depends| D_POSITION_Covariance_Estimator_Gate
    D_POSITION_Cross_Strategy_Position_Merger -.->|config_depends| D_POSITION_No_Buy_at_Limit_Up
    D_POSITION_Cash_Manager -.->|import_depends| D_POSITION_Capital_Curve_Manager
    D_POSITION_Cash_Manager -.->|import_depends| D_POSITION_Liquidity_Downgrade_Mode
    D_POSITION_Capital_Curve_Manager -.->|import_depends| D_POSITION_Drawdown_Controller
    D_POSITION_Capital_Curve_Manager -.->|event| D_POSITION_DriftDetected
    D_POSITION_Capital_Curve_Manager -.->|config_depends| D_POSITION_Intraday_Position_Constraint_Gate
    D_POSITION_Drawdown_Controller -.->|config_depends| D_POSITION_Cross_Strategy_Position_Merger_Gate
    D_POSITION_Covariance_Estimator -.->|import_depends| D_POSITION_Correlation_Regime_Monitor
    D_POSITION_Covariance_Estimator -.->|config_depends| D_POSITION_Daily_Loss_5_AUM_Liquidation_AUM_5
    D_POSITION_Covariance_Estimator -.->|import_depends| D_POSITION_Hot_Plane_Position_Data_Isolation
    D_POSITION_Correlation_Regime_Monitor -.->|import_depends| D_POSITION_Dynamic_Level_Decision
    D_POSITION_Corporate_Action_Processor -.->|import_depends| D_POSITION_Calendar_Position_Constraint
    D_POSITION_Calendar_Position_Constraint -.->|import_depends| D_POSITION_Intraday_Position_Constraint
    D_POSITION_Calendar_Position_Constraint -.->|event| D_POSITION_CapitalCurveUpdated
    D_POSITION_Calendar_Position_Constraint -.->|event| D_POSITION_CalendarPositionAlert
    D_POSITION_Intraday_Position_Constraint -.->|import_depends| D_POSITION_Four_track_Position_Decision_Architecture
    D_TRADING["D-TRADING design"]
    D_POSITION_D_POSITION -.->|domain_dependency| D_TRADING
    D_EX_SOR["D-EX_SOR design"]
    D_POSITION_Cash_Manager -.->|contract| D_EX_SOR
    D_DATA_ENG["D-DATA_ENG design"]
    D_POSITION_Capital_Curve_Manager -.->|contract| D_DATA_ENG
    D_MKT_DATA["D-MKT_DATA design"]
    D_POSITION_Drawdown_Controller -.->|data| D_MKT_DATA
    D_POSITION_Covariance_Estimator -.->|contract| D_TRADING
    D_POSITION_Anti_Pyramiding_Scaler -.->|data| D_MKT_DATA
    D_FACTOR["D-FACTOR design"]
    D_POSITION_Corporate_Action_Processor -.->|data| D_FACTOR
    D_POSITION_Corporate_Action_Processor -.->|event| D_FACTOR
    D_EX_CORE["D-EX_CORE design"]
    D_POSITION_Intraday_Position_Constraint -.->|data| D_EX_CORE
    D_POSITION_CalendarPositionAlert -.->|config_depends| D_MKT_DATA
    D_POSITION_Cross_Strategy_Position_Merger_Gate -.->|data| D_FACTOR
    D_POSITION_Covariance_Estimator_Gate -.->|data| D_TRADING
    D_POSITION_Loss_Position_Add_Hard_Block_Invariant_Hard_Block -.->|event| D_TRADING
    D_POSITION_Every_Order_Must_Pass_Risk_Check -.->|config_depends| D_DATA_ENG
    D_POSITION_KS_L4_Derated_Operation_KS_L4 -.->|event| D_EX_CORE
    D_REPORTING["D-REPORTING design"]
    D_REPORTING -.->|domain_dependency| D_POSITION_D_POSITION
    D_RISK["D-RISK design"]
    D_RISK -.->|domain_dependency| D_POSITION_D_POSITION
    D_SELL_DECISION["D-SELL_DECISION design"]
    D_SELL_DECISION -.->|domain_dependency| D_POSITION_D_POSITION
    D_INFRA_OPS["D-INFRA_OPS design"]
    D_INFRA_OPS -.->|contract| D_POSITION_Cross_Strategy_Position_Merger
    D_COMPLIANCE["D-COMPLIANCE design"]
    D_COMPLIANCE -.->|contract| D_POSITION_Cross_Strategy_Position_Merger
    D_INTEGRATION["D-INTEGRATION design"]
    D_INTEGRATION -.->|event| D_POSITION_Cross_Strategy_Position_Merger
    D_GOVERNANCE["D-GOVERNANCE design"]
    D_GOVERNANCE -.->|config_depends| D_POSITION_Cross_Strategy_Position_Merger
    D_RISK -.->|data| D_POSITION_Cash_Manager
    D_COMPLIANCE -.->|contract| D_POSITION_Cash_Manager
    D_RISK -.->|contract| D_POSITION_Capital_Curve_Manager
    D_COMPLIANCE -.->|config_depends| D_POSITION_Capital_Curve_Manager
    D_KNOWLEDGE["D-KNOWLEDGE design"]
    D_KNOWLEDGE -.->|data| D_POSITION_Drawdown_Controller
    D_INTELLIGENCE["D-INTELLIGENCE design"]
    D_INTELLIGENCE -.->|config_depends| D_POSITION_Drawdown_Controller
    D_RISK -.->|data| D_POSITION_Drawdown_Controller
    D_SELL_DECISION -.->|data| D_POSITION_Correlation_Regime_Monitor
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f5e9,stroke:#1b5e20,stroke-width:1px,color:#000
    classDef external_design fill:#fce4ec,stroke:#880e4f,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class D_POSITION_Anti_Pyramiding_Scaler,D_POSITION_Calendar_Position_Constraint,D_POSITION_CalendarPositionAlert,D_POSITION_Capital_Curve_Manager,D_POSITION_CapitalCurve,D_POSITION_CapitalCurveUpdated,D_POSITION_Cash_Manager,D_POSITION_Corporate_Action_Processor,D_POSITION_Correlation_Regime_Monitor_Gate,D_POSITION_Correlation_Regime_Monitor,D_POSITION_Covariance_Estimator_Gate,D_POSITION_Covariance_Estimator,D_POSITION_Cross_Strategy_Position_Merger_Gate,D_POSITION_Cross_Strategy_Position_Merger,D_POSITION_D_POSITION,D_POSITION_Daily_Loss_5_AUM_Liquidation_AUM_5,D_POSITION_Drawdown_Controller,D_POSITION_DriftDetected,D_POSITION_Dynamic_Level_Decision,D_POSITION_Every_Order_Must_Pass_Risk_Check,D_POSITION_Four_track_Position_Decision_Architecture,D_POSITION_Hot_Plane_Position_Data_Isolation,D_POSITION_Intraday_Position_Constraint_Gate,D_POSITION_Intraday_Position_Constraint,D_POSITION_KS_L4_Derated_Operation_KS_L4,D_POSITION_L3_to_L3_5_Position_Sizing_L3_L3_5,D_POSITION_Liquidity_Downgrade_Mode,D_POSITION_Liquidity_Spiral_Three_Phases,D_POSITION_Loss_Position_Add_Hard_Block_Invariant_Hard_Block,D_POSITION_No_Buy_at_Limit_Up design
    class D_TRADING,D_EX_SOR,D_DATA_ENG,D_MKT_DATA,D_FACTOR,D_EX_CORE,D_REPORTING,D_RISK,D_SELL_DECISION,D_INFRA_OPS,D_COMPLIANCE,D_INTEGRATION,D_GOVERNANCE,D_KNOWLEDGE,D_INTELLIGENCE external_design
```

### 第 2 页 / 共 3 页 / Page 2 of 3

```mermaid
graph TD
    subgraph D_POSITION["D-POSITION 仓位管理"]
        D_POSITION_No_Order_Outside_Trading_Hours["No Order Outside Trading Hours 非交易时段不下单 design"]
        D_POSITION_No_Sell_at_Limit_Down["No Sell at Limit Down 跌停板不卖出 design"]
        D_POSITION_Order_Saga_Position_Step["Order Saga Position Step 仓位订单 design"]
        D_POSITION_Portfolio_Level_Decision["Portfolio Level Decision 组合 design"]
        D_POSITION_Position_Arbitration_Cannot_Bypass_Invariant["Position Arbitration Cannot Bypass Invariant 仓位... design"]
        D_POSITION_Position_Audit_Logger["Position Audit Logger仓位审计日志 design"]
        D_POSITION_Position_Behavior_Classifier_Gate["Position Behavior Classifier Gate 持仓行为分类器门禁 design"]
        D_POSITION_Position_Behavior_Classifier["Position Behavior Classifier 持仓行为分类器 design"]
        D_POSITION_Position_Drift_Monitor["Position Drift Monitor仓位漂移监控器 design"]
        D_POSITION_Position_Limit_Enforcer["Position Limit Enforcer 持仓限额执行器 design"]
        D_POSITION_Position_Limit_Enforcer_1["Position Limit Enforcer仓位限制执行器 design"]
        D_POSITION_Position_Management["Position Management 仓位管理唯一裁决中心 design"]
        D_POSITION_Position_RPO_Zero_Invariant_RPO_0["Position RPO Zero Invariant 持仓RPO=0不变量 design"]
        D_POSITION_Position_Risk_Monitor["Position Risk Monitor 持仓风险监控器 design"]
        D_POSITION_Position_Sizing_Engine["Position Sizing Engine标级仓位决策引擎 design"]
        D_POSITION_Position_State_Machine["Position State Machine持仓状态机 design"]
        D_POSITION_Position_Time_Budget_Gate["Position Time Budget Gate 仓位时间预算门禁 design"]
        D_POSITION_Position_Time_Budget["Position Time Budget持仓时间预算器 design"]
        D_POSITION_Position_Tracker["Position Tracker 持仓跟踪器 design"]
        D_POSITION_Position["Position 持仓聚合根 design"]
        D_POSITION_PositionPlan["PositionPlan 仓位方案 design"]
        D_POSITION_PositionPlan_1["PositionPlan 仓位方案契约 design"]
        D_POSITION_PositionSized["PositionSized 仓位已定 design"]
        D_POSITION_PositionUpdated["PositionUpdated 持仓更新契约 design"]
        D_POSITION_Rebalance_Engine["Rebalance Engine再平衡决策引擎 design"]
        D_POSITION_RebalanceTriggered["RebalanceTriggered 再平衡已触发 design"]
        D_POSITION_Risk_Budget_Allocator_Gate["Risk Budget Allocator Gate 风险预算分配器门禁 design"]
        D_POSITION_Risk_Budget_Allocator["Risk Budget Allocator风险配额分配器 design"]
        D_POSITION_ST_Delisting_Risk_Next_Day_Liquidation_ST["ST/Delisting Risk Next Day Liquidation 持仓股票ST/退... design"]
        D_POSITION_Scaling_Out_Executor_Gate["Scaling-Out Executor Gate 减仓执行器门禁 design"]
    end
    D_POSITION_Position_Sizing_Engine -.->|import_depends| D_POSITION_Position_State_Machine
    D_POSITION_Position_Sizing_Engine -.->|config_depends| D_POSITION_No_Order_Outside_Trading_Hours
    D_POSITION_Position_Sizing_Engine -.->|import_depends| D_POSITION_Portfolio_Level_Decision
    D_POSITION_Position_State_Machine -.->|import_depends| D_POSITION_Position_Drift_Monitor
    D_POSITION_Position_State_Machine -.->|contract| D_POSITION_PositionUpdated
    D_POSITION_Position_Drift_Monitor -.->|import_depends| D_POSITION_Rebalance_Engine
    D_POSITION_Position_Drift_Monitor -.->|config_depends| D_POSITION_Scaling_Out_Executor_Gate
    D_POSITION_Position_Drift_Monitor -.->|import_depends| D_POSITION_Position
    D_POSITION_Rebalance_Engine -.->|import_depends| D_POSITION_PositionPlan
    D_POSITION_Position_Audit_Logger -.->|import_depends| D_POSITION_Position_Limit_Enforcer_1
    D_POSITION_Position_Tracker -.->|import_depends| D_POSITION_Position_Risk_Monitor
    D_POSITION_Position_Risk_Monitor -.->|import_depends| D_POSITION_Position_Limit_Enforcer
    D_POSITION_Position_Risk_Monitor -.->|config_depends| D_POSITION_Position_Time_Budget_Gate
    D_POSITION_Position_Limit_Enforcer -.->|config_depends| D_POSITION_Position_Behavior_Classifier_Gate
    D_FACTOR["D-FACTOR design"]
    D_POSITION_Position_Limit_Enforcer_1 -.->|data| D_FACTOR
    D_POSITION_Position_Time_Budget -.->|contract| D_FACTOR
    D_POSITION_Position_Tracker -.->|contract| D_FACTOR
    D_POSITION_Position_Risk_Monitor -.->|event| D_FACTOR
    D_EX_CORE["D-EX_CORE design"]
    D_POSITION_RebalanceTriggered -.->|contract| D_EX_CORE
    D_POSITION_Scaling_Out_Executor_Gate -.->|config_depends| D_FACTOR
    D_MKT_DATA["D-MKT_DATA design"]
    D_POSITION_Position_Time_Budget_Gate -.->|data| D_MKT_DATA
    D_TRADING["D-TRADING design"]
    D_POSITION_Position_Behavior_Classifier_Gate -.->|contract| D_TRADING
    D_DATA_ENG["D-DATA_ENG design"]
    D_POSITION_Position_Arbitration_Cannot_Bypass_Invariant -.->|data| D_DATA_ENG
    D_INFRA_RUNTIME["D-INFRA_RUNTIME design"]
    D_POSITION_No_Sell_at_Limit_Down -.->|event| D_INFRA_RUNTIME
    D_POSITION_No_Order_Outside_Trading_Hours -.->|contract| D_INFRA_RUNTIME
    D_POSITION_ST_Delisting_Risk_Next_Day_Liquidation_ST -.->|data| D_TRADING
    D_POSITION_Order_Saga_Position_Step -.->|data| D_MKT_DATA
    D_FRONTEND["D-FRONTEND design"]
    D_FRONTEND -.->|contract| D_POSITION_Position_Management
    D_ML_SERVE["D-ML_SERVE design"]
    D_ML_SERVE -.->|data| D_POSITION_Position_State_Machine
    D_RISK["D-RISK design"]
    D_RISK -.->|event| D_POSITION_Position_State_Machine
    D_SIGNAL["D-SIGNAL design"]
    D_SIGNAL -.->|data| D_POSITION_Position_State_Machine
    D_SIGNAL -.->|contract| D_POSITION_Position_State_Machine
    D_COMPLIANCE["D-COMPLIANCE design"]
    D_COMPLIANCE -.->|data| D_POSITION_Position_Drift_Monitor
    D_SECURITY["D-SECURITY design"]
    D_SECURITY -.->|contract| D_POSITION_Position_Drift_Monitor
    D_PF_CORE["D-PF_CORE design"]
    D_PF_CORE -.->|contract| D_POSITION_Rebalance_Engine
    D_AUTONOMY_CORE["D-AUTONOMY_CORE design"]
    D_AUTONOMY_CORE -.->|contract| D_POSITION_Rebalance_Engine
    D_SELL_DECISION["D-SELL_DECISION design"]
    D_SELL_DECISION -.->|event| D_POSITION_Position_Audit_Logger
    D_INFRA_OPS["D-INFRA_OPS design"]
    D_INFRA_OPS -.->|event| D_POSITION_Position_Audit_Logger
    D_INFRA_OPS -.->|config_depends| D_POSITION_Position_Audit_Logger
    D_GOVERNANCE["D-GOVERNANCE design"]
    D_GOVERNANCE -.->|event| D_POSITION_Position_Limit_Enforcer_1
    D_SIGNAL -.->|event| D_POSITION_Position_Time_Budget
    D_SECURITY -.->|contract| D_POSITION_PositionUpdated
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f5e9,stroke:#1b5e20,stroke-width:1px,color:#000
    classDef external_design fill:#fce4ec,stroke:#880e4f,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class D_POSITION_No_Order_Outside_Trading_Hours,D_POSITION_No_Sell_at_Limit_Down,D_POSITION_Order_Saga_Position_Step,D_POSITION_Portfolio_Level_Decision,D_POSITION_Position_Arbitration_Cannot_Bypass_Invariant,D_POSITION_Position_Audit_Logger,D_POSITION_Position_Behavior_Classifier_Gate,D_POSITION_Position_Behavior_Classifier,D_POSITION_Position_Drift_Monitor,D_POSITION_Position_Limit_Enforcer,D_POSITION_Position_Limit_Enforcer_1,D_POSITION_Position_Management,D_POSITION_Position_RPO_Zero_Invariant_RPO_0,D_POSITION_Position_Risk_Monitor,D_POSITION_Position_Sizing_Engine,D_POSITION_Position_State_Machine,D_POSITION_Position_Time_Budget_Gate,D_POSITION_Position_Time_Budget,D_POSITION_Position_Tracker,D_POSITION_Position,D_POSITION_PositionPlan,D_POSITION_PositionPlan_1,D_POSITION_PositionSized,D_POSITION_PositionUpdated,D_POSITION_Rebalance_Engine,D_POSITION_RebalanceTriggered,D_POSITION_Risk_Budget_Allocator_Gate,D_POSITION_Risk_Budget_Allocator,D_POSITION_ST_Delisting_Risk_Next_Day_Liquidation_ST,D_POSITION_Scaling_Out_Executor_Gate design
    class D_FACTOR,D_EX_CORE,D_MKT_DATA,D_TRADING,D_DATA_ENG,D_INFRA_RUNTIME,D_FRONTEND,D_ML_SERVE,D_RISK,D_SIGNAL,D_COMPLIANCE,D_SECURITY,D_PF_CORE,D_AUTONOMY_CORE,D_SELL_DECISION,D_INFRA_OPS,D_GOVERNANCE external_design
```

### 第 3 页 / 共 3 页 / Page 3 of 3

```mermaid
graph TD
    subgraph D_POSITION["D-POSITION 仓位管理"]
        D_POSITION_Sell_Position_Bidirectional_Link["Sell-Position Bidirectional Link卖出-仓位双向联动器 design"]
        D_POSITION_Semi_Kelly_Hard_Cap_Invariant_Kelly["Semi-Kelly Hard Cap Invariant 半Kelly为硬上限不变量 design"]
        D_POSITION_Single_Position_10_AUM_Cap_AUM_10["Single Position 10% AUM Cap 单票持仓不超过AUM的10% design"]
        D_POSITION_State_Position_Mapping_Immutable_Invariant_AI["State-Position Mapping Immutable Invariant 状态→仓... design"]
        D_POSITION_StateChanged["StateChanged 状态已变更 design"]
        D_POSITION_Strategy_Level_Decision["Strategy Level Decision 策略 design"]
        D_POSITION_Symbol_Level_Decision["Symbol Level Decision 标的级决策 design"]
        D_POSITION_Total_Position_30_AUM_Cap_AUM_30["Total Position 30% AUM Cap 总仓位不超过AUM的30% design"]
        D_POSITION_Unfilled_Position_Disaster_Recovery["Unfilled Position Disaster Recovery 仓位 design"]
        src_zephyr_position_init_py["src/zephyr/position/__init__.py prototype"]
        src_zephyr_position_extensions_init_py["src/zephyr/position/_extensions/__init__.py scaffold_placeholder"]
        src_zephyr_position_api_init_py["src/zephyr/position/api/__init__.py scaffold_placeholder"]
        src_zephyr_position_core_init_py["src/zephyr/position/core/__init__.py scaffold_placeholder"]
        src_zephyr_position_infrastructure_init_py["src/zephyr/position/infrastructure/__init__.py scaffold_placeholder"]
        src_zephyr_position_models_init_py["src/zephyr/position/models/__init__.py scaffold_placeholder"]
        src_zephyr_position_position_reconciler_py["src/zephyr/position/position_reconciler.py prototype"]
        src_zephyr_position_services_init_py["src/zephyr/position/services/__init__.py scaffold_placeholder"]
    end
    D_GOVERNANCE["D-GOVERNANCE production"]
    src_zephyr_position_position_reconciler_py -.->|config_depends| D_GOVERNANCE
    D_SHARED["D-SHARED design"]
    src_zephyr_position_models_init_py -.->|contract| D_SHARED
    D_MKT_DATA["D-MKT_DATA design"]
    D_POSITION_Sell_Position_Bidirectional_Link -.->|contract| D_MKT_DATA
    D_TRADING["D-TRADING design"]
    D_POSITION_Sell_Position_Bidirectional_Link -.->|data| D_TRADING
    D_POSITION_State_Position_Mapping_Immutable_Invariant_AI -.->|event| D_MKT_DATA
    D_DATA_ENG["D-DATA_ENG design"]
    D_POSITION_Unfilled_Position_Disaster_Recovery -.->|contract| D_DATA_ENG
    D_KNOWLEDGE["D-KNOWLEDGE design"]
    D_KNOWLEDGE -.->|contract| D_POSITION_StateChanged
    D_RISK["D-RISK design"]
    D_RISK -.->|contract| D_POSITION_StateChanged
    D_INTEGRATION["D-INTEGRATION design"]
    D_INTEGRATION -.->|data| D_POSITION_StateChanged
    D_AUTONOMY_CORE["D-AUTONOMY_CORE design"]
    D_AUTONOMY_CORE -.->|contract| D_POSITION_Semi_Kelly_Hard_Cap_Invariant_Kelly
    D_RISK -.->|event| D_POSITION_Semi_Kelly_Hard_Cap_Invariant_Kelly
    D_RISK -.->|data| D_POSITION_State_Position_Mapping_Immutable_Invariant_AI
    D_ML_TRAIN["D-ML_TRAIN design"]
    D_ML_TRAIN -.->|config_depends| D_POSITION_Single_Position_10_AUM_Cap_AUM_10
    D_RISK -.->|data| D_POSITION_Strategy_Level_Decision
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f5e9,stroke:#1b5e20,stroke-width:1px,color:#000
    classDef external_design fill:#fce4ec,stroke:#880e4f,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class D_POSITION_Sell_Position_Bidirectional_Link,D_POSITION_Semi_Kelly_Hard_Cap_Invariant_Kelly,D_POSITION_Single_Position_10_AUM_Cap_AUM_10,D_POSITION_State_Position_Mapping_Immutable_Invariant_AI,D_POSITION_StateChanged,D_POSITION_Strategy_Level_Decision,D_POSITION_Symbol_Level_Decision,D_POSITION_Total_Position_30_AUM_Cap_AUM_30,D_POSITION_Unfilled_Position_Disaster_Recovery,src_zephyr_position_init_py,src_zephyr_position_extensions_init_py,src_zephyr_position_api_init_py,src_zephyr_position_core_init_py,src_zephyr_position_infrastructure_init_py,src_zephyr_position_models_init_py,src_zephyr_position_position_reconciler_py,src_zephyr_position_services_init_py design
    class D_GOVERNANCE external_prod
    class D_SHARED,D_MKT_DATA,D_TRADING,D_DATA_ENG,D_KNOWLEDGE,D_RISK,D_INTEGRATION,D_AUTONOMY_CORE,D_ML_TRAIN external_design
```

## 跨域依赖 / Cross-domain Dependencies

### 本域依赖的其他域（出边）/ Depends On

| 目标域 / Target Domain | 依赖数 / Count | 依赖类型 / Type |
|--------|:---:|---------|
| D-MKT_DATA | 8 | data,contract,config_depends,event |
| D-FACTOR | 8 | data,contract,event,config_depends |
| D-TRADING | 7 | domain_dependency,contract,data,event |
| D-DATA_ENG | 4 | contract,data,config_depends |
| D-EX_SOR | 3 | contract,event |
| D-EX_CORE | 3 | data,contract,event |
| D-INFRA_RUNTIME | 2 | event,contract |
| D-SHARED | 1 | contract |
| D-GOVERNANCE | 1 | config_depends |

### 依赖本域的其他域（入边）/ Depended By

| 源域 / Source Domain | 依赖数 / Count | 依赖类型 / Type |
|------|:---:|---------|
| D-RISK | 18 | domain_dependency,event,data,contract,config_depends |
| D-GOVERNANCE | 14 | config_depends,event,contract,data |
| D-SECURITY | 8 | contract,event,data |
| D-INFRA_OPS | 8 | contract,event,config_depends,data |
| D-COMPLIANCE | 8 | data,contract,config_depends,event |
| D-AUTONOMY_CORE | 7 | contract,data,event |
| D-SELL_DECISION | 5 | domain_dependency,event,data,contract |
| D-REPORTING | 5 | domain_dependency,event,contract,data |
| D-INTELLIGENCE | 5 | config_depends,contract |
| D-SIGNAL | 4 | data,contract,event |
| D-OPS | 4 | config_depends,contract,event |
| D-KNOWLEDGE | 4 | data,contract,config_depends |
| D-INTEGRATION | 4 | event,contract,data |
| D-ML_TRAIN | 3 | contract,data,config_depends |
| D-ML_SERVE | 3 | data,contract |
| D-AUTONOMY_PERM | 3 | data |
| D-PF_CORE | 2 | contract |
| D-PF_ALLOC | 2 | config_depends,contract |
| D-FRONTEND | 2 | contract,config_depends |
| D-ALT_DATA | 2 | contract,data |
| D-DATA_SEC | 1 | event |
| D-DATA_GOV | 1 | event |

## 说明 / Notes

- **数据源 / Data Source**: `depgraph.db` 的 `nodes`、`edges`、`domains` 表
- **生成器 / Generator**: `generate_domain_doc.py`
- **维护方式 / Maintenance**: 自动生成，全景图更新时刷新
- **文件名规则 / File Naming**: `{编号:02d}_{域ID小写}.md`，如 `16_d_trading.md`
