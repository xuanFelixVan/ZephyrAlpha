---
doc_type: index
title: 域总览索引
version: "1.0"
status: active
date: auto-generated
owner: auto-generator
ttl: permanent
---

# 域总览索引

> **文档作用 / Purpose**: 列出所有功能域的编号、ID、名称、层级、模块数等基本信息，是域架构文档的入口索引。

> 本文档由 generate_domain_index.py 从 depgraph (PostgreSQL) 自动生成
> 最后更新以 git log 为准
> 数据源: depgraph (PostgreSQL) domains表 + nodes表

## 这是什么？大白话讲依赖图

这份"域总览索引"背后是一张**依赖图**。在往下看清单之前，先用大白话讲清楚它是什么、有什么用、为什么要看。

### 一、依赖关系是什么意思？

一个模块要用到另一个模块，就叫"依赖"。
比如"订单中心"要调用"风控引擎"做风险检查，就说 **订单中心依赖风控引擎**——订单中心离不开风控引擎，箭头是 `订单中心 → 风控引擎`（"我需要你"）。

把项目里所有这种"谁离不开谁"的关系记下来，就是**依赖关系**。

### 二、依赖图是什么？

把项目里**所有模块**当成点，把**所有依赖关系**当成连线，画成一张大网，就是依赖图。

- 它不是一张图片，是存在数据库（`depgraph`）里的一张表
- 它记清楚了：项目有多少功能域、每个域有多少模块、模块之间谁依赖谁、哪些已经造好、哪些还在图纸上

### 三、依赖图有什么用？为什么要看它？

这个项目是 **100% AI 开发**，依赖图专门治 AI 的几个老毛病：

| 看依赖图 | 不看依赖图 |
|---|---|
| 造模块前先查：在不在图里？ | AI 自己编一个不存在的模块（幻觉） |
| 改模块前先查：谁依赖我？ | 改完才发现连累一片，返工 |
| 建文件前先查：放哪个域？容量够吗？ | 文件乱放，域越塞越乱 |
| 对着图走路 | 凭记忆瞎猜，做着做着跑偏 |

**一句话**：依赖图是这个项目的"地图"，AI 干活前必须先看图，不能凭感觉瞎走。

### 四、这份索引主要看什么？

这份"域总览索引"是依赖图的**入口**，主要看三件事：

1. **有多少域** —— 项目分成若干功能域（D_DATA 数据、D_RISK 风控、D_POSITION 仓位…），每个域管一类事
2. **每个域多大** —— 看"模块数"列，知道这个域塞了多少模块
3. **域的状态** —— 看"生产态/设计态"列：生产态 = 已经造好跑起来了，设计态 = 还在图纸上没动工

想看某个域的详细模块清单，点右边"📄 文档"链接进入该域的专属文档。

> 想深入了解依赖图的设计和裁定，看 [依赖与路径全景图能力定位书](../04_architecture_principles_decisions/panorama/dependency_path_panorama.md)。

---

## 统计概览

| 指标 / Metric | 值 / Value |
|------|-----|
| 域总数 | 72 |
| 模块总数 | 3789 |
| 生产态模块 | 3567 |
| 设计态模块 | 222 |

## 域清单（按架构层分组）

### L0 基础设施层 / L0 Infrastructure (8 个域 / 8 domains)

| 域ID / Domain ID | 域名称 / Domain Name | 模块数 / Modules | 生产态 / Production | 设计态 / Design | 容量 / Capacity | 文档 / Doc |
|------|--------|:---:|:---:|:---:|------|------|
| D_CONTRACTS | 共享契约 / D_CONTRACTS | 0 | 0 | 0 | 0/150 (OK) | [📄 01_d_contracts.md](01_d_contracts.md) |
| D_INFRASTRUCTURE | 跨层契约基础设施 / Cross-Layer Contract Infrastructure | 26 | 26 | 0 | 26/150 (OK) | [📄 02_d_infrastructure.md](02_d_infrastructure.md) |
| D_INFRA_A2A | A2A通信 / A2A Communication | 72 | 72 | 0 | 72/150 (OK) | [📄 03_d_infra_a2a.md](03_d_infra_a2a.md) |
| D_INFRA_OPS | 基础设施运维 / Asset Inventory | 2 | 2 | 0 | 2/150 (OK) | [📄 04_d_infra_ops.md](04_d_infra_ops.md) |
| D_INFRA_RECOVERY | 回滚恢复 / Rollback Recovery | 55 | 55 | 0 | 55/150 (OK) | [📄 05_d_infra_recovery.md](05_d_infra_recovery.md) |
| D_INFRA_RUNTIME | 运行时集成 / Runtime Integration | 173 | 171 | 2 | 173/150 (超容) | [📄 06_d_infra_runtime.md](06_d_infra_runtime.md) |
| D_INFRA_TELEMETRY | 可观测性 / Observability | 0 | 0 | 0 | 0/150 (OK) | [📄 07_d_infra_telemetry.md](07_d_infra_telemetry.md) |
| D_SHARED | 共享服务 / Shared Services | 177 | 177 | 0 | 177/150 (超容) | [📄 08_d_shared.md](08_d_shared.md) |

### L1 基础平台层 / L1 Foundation (20 个域 / 20 domains)

| 域ID / Domain ID | 域名称 / Domain Name | 模块数 / Modules | 生产态 / Production | 设计态 / Design | 容量 / Capacity | 文档 / Doc |
|------|--------|:---:|:---:|:---:|------|------|
| D_ALT_DATA | 另类数据 / Alternative Data | 8 | 7 | 1 | 8/150 (OK) | [📄 09_d_alt_data.md](09_d_alt_data.md) |
| D_AUTONOMY_CORE | 自治核心 / Autonomy Core | 130 | 130 | 0 | 130/150 (OK) | [📄 10_d_autonomy_core.md](10_d_autonomy_core.md) |
| D_DATA | 数据接入层 / Data Access Layer | 185 | 172 | 13 | 185/150 (超容) | [📄 11_d_data.md](11_d_data.md) |
| D_DATA_ENG | 数据工程 / Data Engineering | 20 | 7 | 13 | 20/150 (OK) | [📄 12_d_data_eng.md](12_d_data_eng.md) |
| D_DATA_GOV | 数据治理 / Data Governance | 10 | 10 | 0 | 10/150 (OK) | [📄 13_d_data_gov.md](13_d_data_gov.md) |
| D_DATA_SEC | 数据安全与契约 / Data Security & Contracts | 7 | 7 | 0 | 7/150 (OK) | [📄 14_d_data_sec.md](14_d_data_sec.md) |
| D_FBL_DETECTORS | 反馈检测器 / Feedback Detectors | 65 | 65 | 0 | 65/150 (OK) | [📄 15_d_fbl_detectors.md](15_d_fbl_detectors.md) |
| D_FBL_DIAGNOSERS | 反馈诊断器 / Feedback Diagnosers | 76 | 76 | 0 | 76/150 (OK) | [📄 16_d_fbl_diagnosers.md](16_d_fbl_diagnosers.md) |
| D_FBL_VERIFICATION | 反馈验证 / Feedback Verification | 71 | 71 | 0 | 71/150 (OK) | [📄 17_d_fbl_verification.md](17_d_fbl_verification.md) |
| D_FEEDBACK_LOOP | 反馈循环引擎 / Feedback Loop Engine | 125 | 125 | 0 | 125/150 (OK) | [📄 18_d_feedback_loop.md](18_d_feedback_loop.md) |
| D_GOV_CODE_QUALITY | 代码质量治理 / Code Quality Governance | 215 | 215 | 0 | 215/150 (超容) | [📄 19_d_gov_code_quality.md](19_d_gov_code_quality.md) |
| D_GOV_OPS_RESILIENCE | 运维弹性治理 / Ops Resilience Governance | 115 | 115 | 0 | 115/150 (OK) | [📄 20_d_gov_ops_resilience.md](20_d_gov_ops_resilience.md) |
| D_INTEGRATION | 管线路由 / Pipeline Routing | 71 | 71 | 0 | 71/150 (OK) | [📄 21_d_integration.md](21_d_integration.md) |
| D_INTEGRATION_GATEWAY | 集成网关 / Integration Gateway | 0 | 0 | 0 | 0/150 (OK) | [📄 22_d_integration_gateway.md](22_d_integration_gateway.md) |
| D_MKT_DATA | 行情数据 / Market Data | 26 | 26 | 0 | 26/150 (OK) | [📄 23_d_mkt_data.md](23_d_mkt_data.md) |
| D_OPS | 反馈循环 / Feedback Loop | 11 | 11 | 0 | 11/150 (OK) | [📄 24_d_ops.md](24_d_ops.md) |
| D_ORCHESTRATOR | 代理编排器 / Agent Orchestrator | 72 | 70 | 2 | 72/150 (OK) | [📄 25_d_orchestrator.md](25_d_orchestrator.md) |
| D_REPORTING | 报告 / Reporting | 20 | 19 | 1 | 20/150 (OK) | [📄 26_d_reporting.md](26_d_reporting.md) |
| D_SECURITY | 对抗验证 / Adversarial Validation | 171 | 171 | 0 | 171/150 (超容) | [📄 27_d_security.md](27_d_security.md) |
| D_SECURITY_LLM | LLM防御 / LLM Defense | 0 | 0 | 0 | 0/150 (OK) | [📄 28_d_security_llm.md](28_d_security_llm.md) |

### L2 业务域层 / L2 Domain (44 个域 / 44 domains)

| 域ID / Domain ID | 域名称 / Domain Name | 模块数 / Modules | 生产态 / Production | 设计态 / Design | 容量 / Capacity | 文档 / Doc |
|------|--------|:---:|:---:|:---:|------|------|
| D_ARCHIVE_SCRIPTS | Archived Scripts / D_ARCHIVE_SCRIPTS | 0 | 0 | 0 | 0/150 (OK) | [📄 29_d_archive_scripts.md](29_d_archive_scripts.md) |
| D_ARCH_GUARD | 架构守护脚本 / D_ARCH_GUARD | 0 | 0 | 0 | 0/150 (OK) | [📄 30_d_arch_guard.md](30_d_arch_guard.md) |
| D_ARCH_SCRIPTS | 架构治理脚本 / D_ARCH_SCRIPTS | 0 | 0 | 0 | 0/150 (OK) | [📄 31_d_arch_scripts.md](31_d_arch_scripts.md) |
| D_ASHARE_SIGNAL | A股特色信号 / A-Share Signal | 37 | 16 | 21 | 37/150 (OK) | [📄 32_d_ashare_signal.md](32_d_ashare_signal.md) |
| D_AUDITTEST | 审计测试套件 / Audit Test Suite | 1 | 1 | 0 | 1/150 (OK) | [📄 33_d_audittest.md](33_d_audittest.md) |
| D_AUTONOMY_PERM | 自治保护 / Autonomy Protection | 2 | 2 | 0 | 2/150 (OK) | [📄 34_d_autonomy_perm.md](34_d_autonomy_perm.md) |
| D_BACKTEST | 回测 / Backtest | 42 | 41 | 1 | 42/150 (OK) | [📄 35_d_backtest.md](35_d_backtest.md) |
| D_BEHAVIORAL_AUDIT | 行为审计 / Behavioral Audit | 0 | 0 | 0 | 0/150 (OK) | [📄 36_d_behavioral_audit.md](36_d_behavioral_audit.md) |
| D_CODE_SCRIPTS | 代码质量脚本 / D_CODE_SCRIPTS | 0 | 0 | 0 | 0/150 (OK) | [📄 37_d_code_scripts.md](37_d_code_scripts.md) |
| D_COMPLIANCE | 合规 / Compliance | 10 | 2 | 8 | 10/150 (OK) | [📄 38_d_compliance.md](38_d_compliance.md) |
| D_COMPLIANCE_SCRIPTS | 合规治理脚本 / D_COMPLIANCE_SCRIPTS | 0 | 0 | 0 | 0/150 (OK) | [📄 39_d_compliance_scripts.md](39_d_compliance_scripts.md) |
| D_CROSS_ASSET | 跨资产 / Cross Asset | 7 | 7 | 0 | 7/150 (OK) | [📄 40_d_cross_asset.md](40_d_cross_asset.md) |
| D_DATA_SCRIPTS | 数据治理脚本 / D_DATA_SCRIPTS | 0 | 0 | 0 | 0/150 (OK) | [📄 41_d_data_scripts.md](41_d_data_scripts.md) |
| D_DIGITAL_TWIN | 数字孪生 / Digital Twin | 7 | 7 | 0 | 7/150 (OK) | [📄 42_d_digital_twin.md](42_d_digital_twin.md) |
| D_EXEC_SIM | 执行仿真 / Execution Simulation | 7 | 7 | 0 | 7/150 (OK) | [📄 43_d_exec_sim.md](43_d_exec_sim.md) |
| D_EX_CORE | 执行核心 / Execution Core | 43 | 18 | 25 | 43/150 (OK) | [📄 44_d_ex_core.md](44_d_ex_core.md) |
| D_EX_SOR | 执行路由 / Execution Routing | 18 | 17 | 1 | 18/150 (OK) | [📄 45_d_ex_sor.md](45_d_ex_sor.md) |
| D_FACTOR | 因子 / Factor | 109 | 65 | 44 | 109/150 (OK) | [📄 46_d_factor.md](46_d_factor.md) |
| D_FRONTEND | 前端 / Frontend | 24 | 20 | 4 | 24/150 (OK) | [📄 47_d_frontend.md](47_d_frontend.md) |
| D_FUNDAMENTAL_SIGNAL | 基本面信号 / Fundamental Signal | 14 | 12 | 2 | 14/150 (OK) | [📄 48_d_fundamental_signal.md](48_d_fundamental_signal.md) |
| D_GOVERNANCE | 生命周期管理 / Lifecycle Management | 451 | 451 | 0 | 451/150 (超容) | [📄 49_d_governance.md](49_d_governance.md) |
| D_GOV_AUDIT | 审计追踪 / Audit Trail | 195 | 192 | 3 | 195/150 (超容) | [📄 50_d_gov_audit.md](50_d_gov_audit.md) |
| D_GOV_DOCS | 架构文档治理 / Architecture Docs Governance | 27 | 2 | 25 | 27/150 (OK) | [📄 51_d_gov_docs.md](51_d_gov_docs.md) |
| D_GOV_DRIFT | 漂移检测 / Drift Detection | 73 | 72 | 1 | 73/150 (OK) | [📄 52_d_gov_drift.md](52_d_gov_drift.md) |
| D_GOV_ENFORCEMENT | 规则执行 / Rule Enforcement | 122 | 121 | 1 | 122/150 (OK) | [📄 53_d_gov_enforcement.md](53_d_gov_enforcement.md) |
| D_GOV_REPAIR | 治理修复 / Governance Repair | 1 | 1 | 0 | 1/200 (OK) | [📄 54_d_gov_repair.md](54_d_gov_repair.md) |
| D_GOV_RULE | 规则治理 / Rule Governance | 36 | 36 | 0 | 36/200 (OK) | [📄 55_d_gov_rule.md](55_d_gov_rule.md) |
| D_GOV_SCRIPTS | 脚本治理 / Script Governance | 422 | 422 | 0 | 422/150 (超容) | [📄 56_d_gov_scripts.md](56_d_gov_scripts.md) |
| D_INTELLIGENCE | 上下文管理 / Context Management | 33 | 31 | 2 | 33/150 (OK) | [📄 57_d_intelligence.md](57_d_intelligence.md) |
| D_KNOWLEDGE | 知识管理 / Knowledge Management | 1 | 0 | 1 | 1/150 (OK) | [📄 58_d_knowledge.md](58_d_knowledge.md) |
| D_META_SCRIPTS | 元治理脚本 / D_META_SCRIPTS | 0 | 0 | 0 | 0/150 (OK) | [📄 59_d_meta_scripts.md](59_d_meta_scripts.md) |
| D_ML_SERVE | 推理 / Inference | 7 | 7 | 0 | 7/150 (OK) | [📄 60_d_ml_serve.md](60_d_ml_serve.md) |
| D_ML_TRAIN | 训练 / Training | 13 | 3 | 10 | 13/150 (OK) | [📄 61_d_ml_train.md](61_d_ml_train.md) |
| D_PF_ALLOC | 组合分配 / Portfolio Allocation | 10 | 5 | 5 | 10/150 (OK) | [📄 62_d_pf_alloc.md](62_d_pf_alloc.md) |
| D_PF_CORE | 组合核心 / Portfolio Core | 18 | 16 | 2 | 18/150 (OK) | [📄 63_d_pf_core.md](63_d_pf_core.md) |
| D_POSITION | 仓位管理 / Position Management | 28 | 15 | 13 | 28/150 (OK) | [📄 64_d_position.md](64_d_position.md) |
| D_RISK | 风控 / Risk Control | 44 | 35 | 9 | 44/150 (OK) | [📄 65_d_risk.md](65_d_risk.md) |
| D_SEC_SCRIPTS | 安全治理脚本 / D_SEC_SCRIPTS | 0 | 0 | 0 | 0/150 (OK) | [📄 66_d_sec_scripts.md](66_d_sec_scripts.md) |
| D_SELL_DECISION | 卖出决策 / Sell Decision | 25 | 13 | 12 | 25/150 (OK) | [📄 67_d_sell_decision.md](67_d_sell_decision.md) |
| D_SIGLEGACY | 信号遗留设计态 / Signal Legacy (Design) | 0 | 0 | 0 | 0/150 (OK) | [📄 68_d_siglegacy.md](68_d_siglegacy.md) |
| D_SIGQC | 信号质量控制 / Signal Quality Control | 2 | 2 | 0 | 2/150 (OK) | [📄 69_d_sigqc.md](69_d_sigqc.md) |
| D_SIMULATION | 仿真 / Simulation | 15 | 15 | 0 | 15/150 (OK) | [📄 70_d_simulation.md](70_d_simulation.md) |
| D_STRUCT_SCRIPTS | 结构治理脚本 / D_STRUCT_SCRIPTS | 0 | 0 | 0 | 0/150 (OK) | [📄 71_d_struct_scripts.md](71_d_struct_scripts.md) |
| D_TRADING | 交易运营 / Trading Operations | 42 | 42 | 0 | 42/150 (OK) | [📄 72_d_trading.md](72_d_trading.md) |
