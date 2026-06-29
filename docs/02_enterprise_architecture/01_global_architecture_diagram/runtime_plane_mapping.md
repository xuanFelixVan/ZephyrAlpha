---
doc_type: register
title: 运行平面映射图
version: "1.0"
status: active
date: 2026-06-25
owner: auto-generator
ttl: permanent
---

# 运行平面映射图 / Runtime Plane Mapping

> **文档作用 / Purpose**: 展示各功能域模块在数据平面、控制平面、管理平面的分布，用于分析系统运行时职责划分。

> 本文档由 generate_runtime_plane_mapping.py 从 depgraph.db 自动生成
> 最后更新 / Last updated: 2026-06-25 20:00:21
> 数据源 / Data source: depgraph.db nodes表 runtime_plane 字段

> 注：数据库 runtime_plane 字段采用 SDN 风格三平面分类（data/control/management），
> 与 runtime_planes.yaml 定义的延迟平面（Hot/Warm/Cold）为正交视图。

## 统计概览 / Statistics Overview

| 指标 / Metric | 值 / Value |
|------|-----|
| 模块总数 / Total modules | 6841 |
| 域总数 / Total domains | 49 |
| 运行平面数 / Runtime planes | 4 |

## 各运行平面模块总数 / Module Count by Plane

| 运行平面 / Runtime Plane | 中文名 / Chinese | 模块数 / Modules | 占比 / Ratio |
|------|------|:---:|:---:|
| data_plane | 数据平面 | 211 | 3.1% |
| control_plane | 控制平面 | 2056 | 30.1% |
| management_plane | 管理平面 | 4266 | 62.4% |
| (null) | 未标注 | 308 | 4.5% |

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
| D_ALT_DATA | 另类数据 | L1_foundation | - | 1 | 6 | 1 | 8 |
| D-ASHARE_SIGNAL | A股特色信号 | L2_domain | - | 1 | 26 | - | 27 |
| D_AUTONOMY_CORE | 自治核心 | L1_foundation | 3 | 5 | 169 | 4 | 181 |
| D-AUTONOMY_PERM | 自治保护 | L2_domain | - | 8 | 80 | - | 88 |
| D-BACKTEST | 回测 | L2_domain | 6 | 1 | - | - | 7 |
| D_BEHAVIORAL_AUDIT | 行为审计 | L1_foundation | - | - | 60 | 19 | 79 |
| D-COMPLIANCE | 合规 | L2_domain | - | 1 | 29 | - | 30 |
| D-CROSS_ASSET | 跨资产 | L2_domain | 1 | 1 | 13 | - | 15 |
| D_DATA_ENG | 数据工程 | L1_foundation | 6 | 1 | 4 | - | 11 |
| D_DATA_SEC | 数据安全与契约 | L1_foundation | 7 | 1 | 2 | - | 10 |
| D-DIGITAL_TWIN | 数字孪生 | L2_domain | - | 1 | 11 | - | 12 |
| D-EXEC_SIM | 执行仿真 | L2_domain | 6 | 1 | - | - | 7 |
| D-EX_CORE | 执行核心 | L2_domain | 1 | 1 | 12 | - | 14 |
| D-EX_SOR | 执行路由 | L2_domain | - | 1 | 6 | - | 7 |
| D-FACTOR | 因子 | L2_domain | 16 | 1 | - | - | 17 |
| D_FRONTEND | 前端 | L1_foundation | - | 1 | 32 | - | 33 |
| D-FUNDAMENTAL_SIGNAL | 基本面信号 | L2_domain | - | 1 | 24 | - | 25 |
| D-GOV-DOCS | architecture_docs | L2_domain | 1 | 55 | 95 | - | 151 |
| D-GOV-ENFORCEMENT | rule_enforcement | L2_domain | - | 107 | - | - | 107 |
| D-GOV-SCRIPTS | code_dedup | L2_domain | 1 | 308 | 107 | - | 416 |
| D-GOVERNANCE | 生命周期管理 | L2_domain | 51 | 790 | 1941 | 61 | 2843 |
| D-GOV_AUDIT | 审计追踪 | L2_domain | - | 187 | 1 | 1 | 189 |
| D-GOV_AUDIT_TESTS | audit_test_suite | L2_domain | - | - | 10 | 142 | 152 |
| D-GOV_DRIFT | 漂移检测 | L2_domain | - | 13 | 11 | 1 | 25 |
| D-GOV_RULE | 规则治理 | L2_domain | - | 2 | 9 | 1 | 12 |
| D_INFRA_A2A | a2a_communication | L0_infrastructure | - | 114 | - | - | 114 |
| D_INFRA_OPS | 基础设施运维 | L0_infrastructure | - | 10 | 24 | 12 | 46 |
| D_INFRA_RECOVERY | rollback_recovery | L0_infrastructure | - | 105 | - | 2 | 107 |
| D_INFRA_RUNTIME | 运行时集成 | L0_infrastructure | - | 135 | 13 | - | 148 |
| D_INFRA_TELEMETRY | observability_profiling | L0_infrastructure | - | 51 | - | - | 51 |
| D_INTEGRATION | 管线路由 | L1_foundation | 36 | 1 | 266 | 11 | 314 |
| D-INTELLIGENCE | 上下文管理 | L2_domain | 2 | 1 | 53 | 1 | 57 |
| D-KNOWLEDGE | 知识管理 | L2_domain | 12 | 28 | 10 | - | 50 |
| D_MKT_DATA | 行情数据 | L1_foundation | 8 | 1 | 1 | - | 10 |
| D-ML_SERVE | 推理 | L2_domain | 6 | 1 | 1 | - | 8 |
| D-ML_TRAIN | 训练 | L2_domain | 10 | 1 | 2 | - | 13 |
| D_OPS | 反馈循环 | L1_foundation | 2 | 15 | 406 | 22 | 445 |
| D-PF_ALLOC | 组合分配 | L2_domain | - | 1 | 14 | - | 15 |
| D-PF_CORE | 组合核心 | L2_domain | - | 1 | 47 | - | 48 |
| D-POSITION | 仓位管理 | L2_domain | - | 1 | 7 | - | 8 |
| D_REPORTING | 报告 | L1_foundation | - | 1 | 17 | 1 | 19 |
| D-RISK | 风控 | L2_domain | 2 | 1 | 79 | - | 82 |
| D_SECURITY | 对抗验证 | L1_foundation | 1 | 1 | 270 | 4 | 276 |
| D-SELL_DECISION | 卖出决策 | L2_domain | - | 1 | 6 | - | 7 |
| D_SHARED | 共享服务 | L1_foundation | 10 | 3 | 271 | 19 | 303 |
| D-SIGLEGACY | 信号遗留设计态 | L2_domain | - | - | 45 | - | 45 |
| D-SIGQC | 信号质量控制 | L2_domain | - | 1 | 16 | - | 17 |
| D-SIMULATION | 仿真 | L2_domain | 22 | 1 | - | - | 23 |
| D-TRADING | 交易运营 | L2_domain | 1 | 92 | 70 | 6 | 169 |

## 数据平面 / Data Plane（data_plane）详情

> 模块总数 / Total modules: 211

| 域ID / Domain ID | 域名称 / Domain Name | 模块数 / Modules | 占比 / Ratio |
|------|------|:---:|:---:|
| D-GOVERNANCE | 生命周期管理 | 51 | 24.2% |
| D_INTEGRATION | 管线路由 | 36 | 17.1% |
| D-SIMULATION | 仿真 | 22 | 10.4% |
| D-FACTOR | 因子 | 16 | 7.6% |
| D-KNOWLEDGE | 知识管理 | 12 | 5.7% |
| D-ML_TRAIN | 训练 | 10 | 4.7% |
| D_SHARED | 共享服务 | 10 | 4.7% |
| D_MKT_DATA | 行情数据 | 8 | 3.8% |
| D_DATA_SEC | 数据安全与契约 | 7 | 3.3% |
| D-BACKTEST | 回测 | 6 | 2.8% |
| D_DATA_ENG | 数据工程 | 6 | 2.8% |
| D-EXEC_SIM | 执行仿真 | 6 | 2.8% |
| D-ML_SERVE | 推理 | 6 | 2.8% |
| D_AUTONOMY_CORE | 自治核心 | 3 | 1.4% |
| D-INTELLIGENCE | 上下文管理 | 2 | 0.9% |
| D_OPS | 反馈循环 | 2 | 0.9% |
| D-RISK | 风控 | 2 | 0.9% |
| D-CROSS_ASSET | 跨资产 | 1 | 0.5% |
| D-EX_CORE | 执行核心 | 1 | 0.5% |
| D-GOV-DOCS | architecture_docs | 1 | 0.5% |
| D-GOV-SCRIPTS | code_dedup | 1 | 0.5% |
| D_SECURITY | 对抗验证 | 1 | 0.5% |
| D-TRADING | 交易运营 | 1 | 0.5% |

## 控制平面 / Control Plane（control_plane）详情

> 模块总数 / Total modules: 2056

| 域ID / Domain ID | 域名称 / Domain Name | 模块数 / Modules | 占比 / Ratio |
|------|------|:---:|:---:|
| D-GOVERNANCE | 生命周期管理 | 790 | 38.4% |
| D-GOV-SCRIPTS | code_dedup | 308 | 15.0% |
| D-GOV_AUDIT | 审计追踪 | 187 | 9.1% |
| D_INFRA_RUNTIME | 运行时集成 | 135 | 6.6% |
| D_INFRA_A2A | a2a_communication | 114 | 5.5% |
| D-GOV-ENFORCEMENT | rule_enforcement | 107 | 5.2% |
| D_INFRA_RECOVERY | rollback_recovery | 105 | 5.1% |
| D-TRADING | 交易运营 | 92 | 4.5% |
| D-GOV-DOCS | architecture_docs | 55 | 2.7% |
| D_INFRA_TELEMETRY | observability_profiling | 51 | 2.5% |
| D-KNOWLEDGE | 知识管理 | 28 | 1.4% |
| D_OPS | 反馈循环 | 15 | 0.7% |
| D-GOV_DRIFT | 漂移检测 | 13 | 0.6% |
| D_INFRA_OPS | 基础设施运维 | 10 | 0.5% |
| D-AUTONOMY_PERM | 自治保护 | 8 | 0.4% |
| D_AUTONOMY_CORE | 自治核心 | 5 | 0.2% |
| D_SHARED | 共享服务 | 3 | 0.1% |
| D-GOV_RULE | 规则治理 | 2 | 0.1% |
| D_ALT_DATA | 另类数据 | 1 | 0.0% |
| D-ASHARE_SIGNAL | A股特色信号 | 1 | 0.0% |
| D-BACKTEST | 回测 | 1 | 0.0% |
| D-COMPLIANCE | 合规 | 1 | 0.0% |
| D-CROSS_ASSET | 跨资产 | 1 | 0.0% |
| D_DATA_ENG | 数据工程 | 1 | 0.0% |
| D_DATA_SEC | 数据安全与契约 | 1 | 0.0% |
| D-DIGITAL_TWIN | 数字孪生 | 1 | 0.0% |
| D-EXEC_SIM | 执行仿真 | 1 | 0.0% |
| D-EX_CORE | 执行核心 | 1 | 0.0% |
| D-EX_SOR | 执行路由 | 1 | 0.0% |
| D-FACTOR | 因子 | 1 | 0.0% |
| D_FRONTEND | 前端 | 1 | 0.0% |
| D-FUNDAMENTAL_SIGNAL | 基本面信号 | 1 | 0.0% |
| D_INTEGRATION | 管线路由 | 1 | 0.0% |
| D-INTELLIGENCE | 上下文管理 | 1 | 0.0% |
| D_MKT_DATA | 行情数据 | 1 | 0.0% |
| D-ML_SERVE | 推理 | 1 | 0.0% |
| D-ML_TRAIN | 训练 | 1 | 0.0% |
| D-PF_ALLOC | 组合分配 | 1 | 0.0% |
| D-PF_CORE | 组合核心 | 1 | 0.0% |
| D-POSITION | 仓位管理 | 1 | 0.0% |
| D_REPORTING | 报告 | 1 | 0.0% |
| D-RISK | 风控 | 1 | 0.0% |
| D_SECURITY | 对抗验证 | 1 | 0.0% |
| D-SELL_DECISION | 卖出决策 | 1 | 0.0% |
| D-SIGQC | 信号质量控制 | 1 | 0.0% |
| D-SIMULATION | 仿真 | 1 | 0.0% |

## 管理平面 / Management Plane（management_plane）详情

> 模块总数 / Total modules: 4266

| 域ID / Domain ID | 域名称 / Domain Name | 模块数 / Modules | 占比 / Ratio |
|------|------|:---:|:---:|
| D-GOVERNANCE | 生命周期管理 | 1941 | 45.5% |
| D_OPS | 反馈循环 | 406 | 9.5% |
| D_SHARED | 共享服务 | 271 | 6.4% |
| D_SECURITY | 对抗验证 | 270 | 6.3% |
| D_INTEGRATION | 管线路由 | 266 | 6.2% |
| D_AUTONOMY_CORE | 自治核心 | 169 | 4.0% |
| D-GOV-SCRIPTS | code_dedup | 107 | 2.5% |
| D-GOV-DOCS | architecture_docs | 95 | 2.2% |
| D-AUTONOMY_PERM | 自治保护 | 80 | 1.9% |
| D-RISK | 风控 | 79 | 1.9% |
| D-TRADING | 交易运营 | 70 | 1.6% |
| D_BEHAVIORAL_AUDIT | 行为审计 | 60 | 1.4% |
| D-INTELLIGENCE | 上下文管理 | 53 | 1.2% |
| D-PF_CORE | 组合核心 | 47 | 1.1% |
| D-SIGLEGACY | 信号遗留设计态 | 45 | 1.1% |
| D_FRONTEND | 前端 | 32 | 0.8% |
| D-COMPLIANCE | 合规 | 29 | 0.7% |
| D-ASHARE_SIGNAL | A股特色信号 | 26 | 0.6% |
| D-FUNDAMENTAL_SIGNAL | 基本面信号 | 24 | 0.6% |
| D_INFRA_OPS | 基础设施运维 | 24 | 0.6% |
| D_REPORTING | 报告 | 17 | 0.4% |
| D-SIGQC | 信号质量控制 | 16 | 0.4% |
| D-PF_ALLOC | 组合分配 | 14 | 0.3% |
| D-CROSS_ASSET | 跨资产 | 13 | 0.3% |
| D_INFRA_RUNTIME | 运行时集成 | 13 | 0.3% |
| D-EX_CORE | 执行核心 | 12 | 0.3% |
| D-DIGITAL_TWIN | 数字孪生 | 11 | 0.3% |
| D-GOV_DRIFT | 漂移检测 | 11 | 0.3% |
| D-GOV_AUDIT_TESTS | audit_test_suite | 10 | 0.2% |
| D-KNOWLEDGE | 知识管理 | 10 | 0.2% |
| D-GOV_RULE | 规则治理 | 9 | 0.2% |
| D-POSITION | 仓位管理 | 7 | 0.2% |
| D_ALT_DATA | 另类数据 | 6 | 0.1% |
| D-EX_SOR | 执行路由 | 6 | 0.1% |
| D-SELL_DECISION | 卖出决策 | 6 | 0.1% |
| D_DATA_ENG | 数据工程 | 4 | 0.1% |
| D_DATA_SEC | 数据安全与契约 | 2 | 0.0% |
| D-ML_TRAIN | 训练 | 2 | 0.0% |
| D-GOV_AUDIT | 审计追踪 | 1 | 0.0% |
| D_MKT_DATA | 行情数据 | 1 | 0.0% |
| D-ML_SERVE | 推理 | 1 | 0.0% |

## 未标注 / Unassigned（(null)）详情

> 模块总数 / Total modules: 308

| 域ID / Domain ID | 域名称 / Domain Name | 模块数 / Modules | 占比 / Ratio |
|------|------|:---:|:---:|
| D-GOV_AUDIT_TESTS | audit_test_suite | 142 | 46.1% |
| D-GOVERNANCE | 生命周期管理 | 61 | 19.8% |
| D_OPS | 反馈循环 | 22 | 7.1% |
| D_BEHAVIORAL_AUDIT | 行为审计 | 19 | 6.2% |
| D_SHARED | 共享服务 | 19 | 6.2% |
| D_INFRA_OPS | 基础设施运维 | 12 | 3.9% |
| D_INTEGRATION | 管线路由 | 11 | 3.6% |
| D-TRADING | 交易运营 | 6 | 1.9% |
| D_AUTONOMY_CORE | 自治核心 | 4 | 1.3% |
| D_SECURITY | 对抗验证 | 4 | 1.3% |
| D_INFRA_RECOVERY | rollback_recovery | 2 | 0.6% |
| D_ALT_DATA | 另类数据 | 1 | 0.3% |
| D-GOV_AUDIT | 审计追踪 | 1 | 0.3% |
| D-GOV_DRIFT | 漂移检测 | 1 | 0.3% |
| D-GOV_RULE | 规则治理 | 1 | 0.3% |
| D-INTELLIGENCE | 上下文管理 | 1 | 0.3% |
| D_REPORTING | 报告 | 1 | 0.3% |
