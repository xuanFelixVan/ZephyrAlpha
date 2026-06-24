---
doc_type: runtime_plane_mapping
title: 运行平面映射图
version: "1.0"
status: active
date: 2026-06-24
owner: auto-generator
ttl: permanent
---

# 运行平面映射图 / Runtime Plane Mapping

> **文档作用 / Purpose**: 展示各功能域模块在数据平面、控制平面、管理平面的分布，用于分析系统运行时职责划分。

> 本文档由 generate_runtime_plane_mapping.py 从 depgraph.db 自动生成
> 最后更新 / Last updated: 2026-06-24 21:39:38
> 数据源 / Data source: depgraph.db nodes表 runtime_plane 字段

> 注：数据库 runtime_plane 字段采用 SDN 风格三平面分类（data/control/management），
> 与 runtime_planes.yaml 定义的延迟平面（Hot/Warm/Cold）为正交视图。

## 统计概览 / Statistics Overview

| 指标 / Metric | 值 / Value |
|------|-----|
| 模块总数 / Total modules | 14397 |
| 域总数 / Total domains | 43 |
| 运行平面数 / Runtime planes | 4 |

## 各运行平面模块总数 / Module Count by Plane

| 运行平面 / Runtime Plane | 中文名 / Chinese | 模块数 / Modules | 占比 / Ratio |
|------|------|:---:|:---:|
| data_plane | 数据平面 | 866 | 6.0% |
| control_plane | 控制平面 | 2704 | 18.8% |
| management_plane | 管理平面 | 10822 | 75.2% |
| (null) | 未标注 | 5 | 0.0% |

## 运行平面定义 / Runtime Plane Definitions

| 运行平面 / Plane | 中文名 / Chinese | 英文名 / English | 说明 / Description |
|------|------|------|------|
| data_plane | 数据平面 | Data Plane | 承载业务数据流转与实际处理（行情/因子/信号/订单等数据通路） |
| control_plane | 控制平面 | Control Plane | 协调与调度决策（路由/编排/策略分发/状态机驱动） |
| management_plane | 管理平面 | Management Plane | 配置、监控与治理管理（治理脚本/审计/注册表/运维管理） |
| (null) | 未标注 | Unassigned | 未标注运行平面 / Runtime plane not assigned |

## 域×运行平面映射矩阵 / Domain × Plane Matrix

| 域ID / Domain ID | 域名称 / Domain Name | 架构层 / Layer | 数据平面 / Data Plane | 控制平面 / Control Plane | 管理平面 / Management Plane | 未标注 / Unassigned | 总计 / Total |
|------|------|------|------|------|------|------|------|
| D-ALT_DATA | 另类数据 | L1_foundation | 1 | 1 | 66 | - | 68 |
| D-AUTONOMY_CORE | 自治核心 | L1_platform | 6 | 9 | 635 | - | 650 |
| D-AUTONOMY_PERM | 自治保护 | L2_domain | 5 | 18 | 247 | - | 270 |
| D-BACKTEST | 回测 | L2_domain | 8 | 1 | - | - | 9 |
| D-BEHAVIORAL_AUDIT | 行为审计 | L1_foundation | - | - | 60 | - | 60 |
| D-COMPLIANCE | 合规 | L2_domain | 6 | 10 | 900 | - | 916 |
| D-CROSS_ASSET | 跨资产 | L2_domain | 2 | 1 | 76 | - | 79 |
| D-DATA_ENG | 数据工程 | L1_foundation | 10 | 1 | 136 | - | 147 |
| D-DATA_GOV | 数据治理 | L1_foundation | 1 | 1 | 36 | - | 38 |
| D-DATA_SEC | 数据安全与契约 | L1_foundation | 7 | 1 | 22 | - | 30 |
| D-DIGITAL_TWIN | 数字孪生 | L2_domain | - | 1 | 12 | - | 13 |
| D-EXEC_SIM | 执行仿真 | L2_domain | 7 | 1 | - | - | 8 |
| D-EX_CORE | 执行核心 | L2_domain | 4 | 1 | 130 | - | 135 |
| D-EX_SOR | 执行路由 | L2_domain | - | 1 | 130 | - | 131 |
| D-FACTOR | 因子 | L2_domain | 317 | 3 | - | - | 320 |
| D-FRONTEND | 前端 | L1_platform | 5 | 4 | 228 | - | 237 |
| D-GOVERNANCE | 生命周期管理 | L2_domain | 52 | 1715 | 2137 | 4 | 3908 |
| D-GOV_AUDIT | 审计追踪 | L2_domain | - | 253 | 15 | - | 268 |
| D-GOV_DRIFT | 漂移检测 | L2_domain | - | 23 | 15 | - | 38 |
| D-GOV_RULE | 规则治理 | L2_domain | 1 | 64 | 113 | - | 178 |
| D-INFRA_OPS | 基础设施运维 | L0_infrastructure | 3 | 10 | 405 | - | 418 |
| D-INFRA_RUNTIME | 运行时集成 | L0_infrastructure | 22 | 407 | 297 | 1 | 727 |
| D-INTEGRATION | 管线路由 | L1_platform | 38 | 4 | 664 | - | 706 |
| D-INTELLIGENCE | 上下文管理 | L2_domain | 9 | 2 | 262 | - | 273 |
| D-KNOWLEDGE | 知识管理 | L2_domain | 156 | 28 | 10 | - | 194 |
| D-MKT_DATA | 行情数据 | L1_foundation | 19 | 3 | 244 | - | 266 |
| D-ML_SERVE | 推理 | L2_domain | 6 | 1 | 62 | - | 69 |
| D-ML_TRAIN | 训练 | L2_domain | 12 | 1 | 106 | - | 119 |
| D-OPS | 反馈循环 | L1_platform | 4 | 21 | 672 | - | 697 |
| D-PF_ALLOC | 组合分配 | L2_domain | - | 1 | 113 | - | 114 |
| D-PF_CORE | 组合核心 | L2_domain | 3 | 2 | 197 | - | 202 |
| D-POSITION | 仓位管理 | L2_domain | - | 1 | 76 | - | 77 |
| D-REPORTING | 报告 | L1_platform | 5 | 1 | 126 | - | 132 |
| D-RISK | 风控 | L2_domain | 13 | 9 | 753 | - | 775 |
| D-SECURITY | 对抗验证 | L1_platform | 4 | 4 | 841 | - | 849 |
| D-SELL_DECISION | 卖出决策 | L2_domain | - | 1 | 63 | - | 64 |
| D-SHARED | 共享服务 | L1_platform | 10 | 3 | 277 | - | 290 |
| D-SIGNAL | 信号 | L2_domain | 2 | - | 474 | - | 476 |
| D-SIGNAL_ASHARE | A股特色信号 | L2_domain | - | 1 | 26 | - | 27 |
| D-SIGNAL_FUNDAMENTAL | 基本面信号 | L2_domain | - | 1 | 23 | - | 24 |
| D-SIGNAL_QUALITY | 信号质量 | L2_domain | - | 1 | 17 | - | 18 |
| D-SIMULATION | 仿真 | L2_domain | 127 | 1 | - | - | 128 |
| D-TRADING | 交易运营 | L2_domain | 1 | 92 | 156 | - | 249 |

## 数据平面 / Data Plane（data_plane）详情

> 模块总数 / Total modules: 866

| 域ID / Domain ID | 域名称 / Domain Name | 模块数 / Modules | 占比 / Ratio |
|------|------|:---:|:---:|
| D-FACTOR | 因子 | 317 | 36.6% |
| D-KNOWLEDGE | 知识管理 | 156 | 18.0% |
| D-SIMULATION | 仿真 | 127 | 14.7% |
| D-GOVERNANCE | 生命周期管理 | 52 | 6.0% |
| D-INTEGRATION | 管线路由 | 38 | 4.4% |
| D-INFRA_RUNTIME | 运行时集成 | 22 | 2.5% |
| D-MKT_DATA | 行情数据 | 19 | 2.2% |
| D-RISK | 风控 | 13 | 1.5% |
| D-ML_TRAIN | 训练 | 12 | 1.4% |
| D-DATA_ENG | 数据工程 | 10 | 1.2% |
| D-SHARED | 共享服务 | 10 | 1.2% |
| D-INTELLIGENCE | 上下文管理 | 9 | 1.0% |
| D-BACKTEST | 回测 | 8 | 0.9% |
| D-DATA_SEC | 数据安全与契约 | 7 | 0.8% |
| D-EXEC_SIM | 执行仿真 | 7 | 0.8% |
| D-AUTONOMY_CORE | 自治核心 | 6 | 0.7% |
| D-COMPLIANCE | 合规 | 6 | 0.7% |
| D-ML_SERVE | 推理 | 6 | 0.7% |
| D-AUTONOMY_PERM | 自治保护 | 5 | 0.6% |
| D-FRONTEND | 前端 | 5 | 0.6% |
| D-REPORTING | 报告 | 5 | 0.6% |
| D-EX_CORE | 执行核心 | 4 | 0.5% |
| D-OPS | 反馈循环 | 4 | 0.5% |
| D-SECURITY | 对抗验证 | 4 | 0.5% |
| D-INFRA_OPS | 基础设施运维 | 3 | 0.3% |
| D-PF_CORE | 组合核心 | 3 | 0.3% |
| D-CROSS_ASSET | 跨资产 | 2 | 0.2% |
| D-SIGNAL | 信号 | 2 | 0.2% |
| D-ALT_DATA | 另类数据 | 1 | 0.1% |
| D-DATA_GOV | 数据治理 | 1 | 0.1% |
| D-GOV_RULE | 规则治理 | 1 | 0.1% |
| D-TRADING | 交易运营 | 1 | 0.1% |

## 控制平面 / Control Plane（control_plane）详情

> 模块总数 / Total modules: 2704

| 域ID / Domain ID | 域名称 / Domain Name | 模块数 / Modules | 占比 / Ratio |
|------|------|:---:|:---:|
| D-GOVERNANCE | 生命周期管理 | 1715 | 63.4% |
| D-INFRA_RUNTIME | 运行时集成 | 407 | 15.1% |
| D-GOV_AUDIT | 审计追踪 | 253 | 9.4% |
| D-TRADING | 交易运营 | 92 | 3.4% |
| D-GOV_RULE | 规则治理 | 64 | 2.4% |
| D-KNOWLEDGE | 知识管理 | 28 | 1.0% |
| D-GOV_DRIFT | 漂移检测 | 23 | 0.9% |
| D-OPS | 反馈循环 | 21 | 0.8% |
| D-AUTONOMY_PERM | 自治保护 | 18 | 0.7% |
| D-COMPLIANCE | 合规 | 10 | 0.4% |
| D-INFRA_OPS | 基础设施运维 | 10 | 0.4% |
| D-AUTONOMY_CORE | 自治核心 | 9 | 0.3% |
| D-RISK | 风控 | 9 | 0.3% |
| D-FRONTEND | 前端 | 4 | 0.1% |
| D-INTEGRATION | 管线路由 | 4 | 0.1% |
| D-SECURITY | 对抗验证 | 4 | 0.1% |
| D-FACTOR | 因子 | 3 | 0.1% |
| D-MKT_DATA | 行情数据 | 3 | 0.1% |
| D-SHARED | 共享服务 | 3 | 0.1% |
| D-INTELLIGENCE | 上下文管理 | 2 | 0.1% |
| D-PF_CORE | 组合核心 | 2 | 0.1% |
| D-ALT_DATA | 另类数据 | 1 | 0.0% |
| D-BACKTEST | 回测 | 1 | 0.0% |
| D-CROSS_ASSET | 跨资产 | 1 | 0.0% |
| D-DATA_ENG | 数据工程 | 1 | 0.0% |
| D-DATA_GOV | 数据治理 | 1 | 0.0% |
| D-DATA_SEC | 数据安全与契约 | 1 | 0.0% |
| D-DIGITAL_TWIN | 数字孪生 | 1 | 0.0% |
| D-EXEC_SIM | 执行仿真 | 1 | 0.0% |
| D-EX_CORE | 执行核心 | 1 | 0.0% |
| D-EX_SOR | 执行路由 | 1 | 0.0% |
| D-ML_SERVE | 推理 | 1 | 0.0% |
| D-ML_TRAIN | 训练 | 1 | 0.0% |
| D-PF_ALLOC | 组合分配 | 1 | 0.0% |
| D-POSITION | 仓位管理 | 1 | 0.0% |
| D-REPORTING | 报告 | 1 | 0.0% |
| D-SELL_DECISION | 卖出决策 | 1 | 0.0% |
| D-SIGNAL_ASHARE | A股特色信号 | 1 | 0.0% |
| D-SIGNAL_FUNDAMENTAL | 基本面信号 | 1 | 0.0% |
| D-SIGNAL_QUALITY | 信号质量 | 1 | 0.0% |
| D-SIMULATION | 仿真 | 1 | 0.0% |

## 管理平面 / Management Plane（management_plane）详情

> 模块总数 / Total modules: 10822

| 域ID / Domain ID | 域名称 / Domain Name | 模块数 / Modules | 占比 / Ratio |
|------|------|:---:|:---:|
| D-GOVERNANCE | 生命周期管理 | 2137 | 19.7% |
| D-COMPLIANCE | 合规 | 900 | 8.3% |
| D-SECURITY | 对抗验证 | 841 | 7.8% |
| D-RISK | 风控 | 753 | 7.0% |
| D-OPS | 反馈循环 | 672 | 6.2% |
| D-INTEGRATION | 管线路由 | 664 | 6.1% |
| D-AUTONOMY_CORE | 自治核心 | 635 | 5.9% |
| D-SIGNAL | 信号 | 474 | 4.4% |
| D-INFRA_OPS | 基础设施运维 | 405 | 3.7% |
| D-INFRA_RUNTIME | 运行时集成 | 297 | 2.7% |
| D-SHARED | 共享服务 | 277 | 2.6% |
| D-INTELLIGENCE | 上下文管理 | 262 | 2.4% |
| D-AUTONOMY_PERM | 自治保护 | 247 | 2.3% |
| D-MKT_DATA | 行情数据 | 244 | 2.3% |
| D-FRONTEND | 前端 | 228 | 2.1% |
| D-PF_CORE | 组合核心 | 197 | 1.8% |
| D-TRADING | 交易运营 | 156 | 1.4% |
| D-DATA_ENG | 数据工程 | 136 | 1.3% |
| D-EX_CORE | 执行核心 | 130 | 1.2% |
| D-EX_SOR | 执行路由 | 130 | 1.2% |
| D-REPORTING | 报告 | 126 | 1.2% |
| D-GOV_RULE | 规则治理 | 113 | 1.0% |
| D-PF_ALLOC | 组合分配 | 113 | 1.0% |
| D-ML_TRAIN | 训练 | 106 | 1.0% |
| D-CROSS_ASSET | 跨资产 | 76 | 0.7% |
| D-POSITION | 仓位管理 | 76 | 0.7% |
| D-ALT_DATA | 另类数据 | 66 | 0.6% |
| D-SELL_DECISION | 卖出决策 | 63 | 0.6% |
| D-ML_SERVE | 推理 | 62 | 0.6% |
| D-BEHAVIORAL_AUDIT | 行为审计 | 60 | 0.6% |
| D-DATA_GOV | 数据治理 | 36 | 0.3% |
| D-SIGNAL_ASHARE | A股特色信号 | 26 | 0.2% |
| D-SIGNAL_FUNDAMENTAL | 基本面信号 | 23 | 0.2% |
| D-DATA_SEC | 数据安全与契约 | 22 | 0.2% |
| D-SIGNAL_QUALITY | 信号质量 | 17 | 0.2% |
| D-GOV_AUDIT | 审计追踪 | 15 | 0.1% |
| D-GOV_DRIFT | 漂移检测 | 15 | 0.1% |
| D-DIGITAL_TWIN | 数字孪生 | 12 | 0.1% |
| D-KNOWLEDGE | 知识管理 | 10 | 0.1% |

## 未标注 / Unassigned（(null)）详情

> 模块总数 / Total modules: 5

| 域ID / Domain ID | 域名称 / Domain Name | 模块数 / Modules | 占比 / Ratio |
|------|------|:---:|:---:|
| D-GOVERNANCE | 生命周期管理 | 4 | 80.0% |
| D-INFRA_RUNTIME | 运行时集成 | 1 | 20.0% |
