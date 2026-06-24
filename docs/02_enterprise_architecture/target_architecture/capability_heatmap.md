---
module_id: VIEW-04TER-CAPABILITY-HEATMAP
title: Target Architecture — Capability Maturity Heatmap (Orthogonal View) / 目标架构：能力成熟度热力图正交视图
doc_type: architecture_view
status: Active
version: 2.0.0
layer: cross_layer
owner: ZephyrAlpha-Owner
classification: confidential
language: zh
created_by: agent
valid_from: 2026-04-19
superseded_by: null
supersedes: null
related_rationale:
- R70
related_open_questions:
- OQ-084
related_kb:
- KBG-0012
tags:
- target-architecture
- capability-heatmap
- maturity
- archimate
- capability-map
- business-architecture
- gap-analysis
- orthogonal-view
- domain-driven
- depgraph-derived
summary: ZephyrAlpha 2.0 能力成熟度热力图正交视图（v2.0.0）。基于§2.1裁定，热力图改为43域×10能力域二维矩阵。原14层×7能力域矩阵废弃。成熟度数据由depgraph.db派生。
date: '2026-06-23'
ttl: permanent
---

## 1. Purpose & 为什么需要能力热力图

### 1.1 本视图要回答的问题

| 问题 | 答案所在 |
|---|---|
| ZephyrAlpha 的核心业务能力是什么？每一项当前多成熟？| §3 43域×10能力域热力图 |
| 哪些能力是"顶级机构标配但我们缺失"的 P0 短板？| §5 Gap-to-Target 差距表 |
| 达到顶级机构对标水平还需要多少投入？| §6 投入估算 |
| 能力成熟度何时刷新？谁负责？| §7 季度 review 机制 |
| 本视图与 `capability_heatmap.yaml` 的承载关系？| §8 数据承载关系 |

### 1.2 为什么要做能力热力图

**外部评审驱动**（`tests/外部评审.md` 四家 AI 共识，P1 级短板）：
> "ZephyrAlpha 缺少一张'全局能力地图 + 成熟度视觉化'让架构师 / 用户 / 外部审计在 5 分钟内抓住'我们强在哪、弱在哪'。"

**本视图价值**：
1. C-level 视角：一张图回答"系统现在多成熟、距离顶级多远"
2. Gap 识别：精准识别 P0/P1/P2 短板
3. 季度 review 锚点：固定每季度刷新，形成"能力进化曲线"
4. 招聘 / 融资 / 审计输出物

### 1.3 业界对标

| 机构 | 能力地图实现 | 成熟度模型 | 刷新频率 |
|---|---|---|---|
| **Goldman Sachs** | Enterprise Architecture Capability Dashboard | 5 档 | 季度 |
| **BlackRock** | Aladdin Capability Heatmap | 5 档 | 季度 |
| **Gartner IT Capability Framework** | Generic Capability Map | 5 档（CMMI-aligned）| 半年 |

**ZephyrAlpha 采纳**：Goldman / BlackRock / Gartner 共识的 5 档模型，季度刷新。

### 1.4 v2.0.0变更说明

基于§2.1裁定：
- 原14层×7能力域矩阵 → 改为43域×10能力域矩阵
- 14层降级为域属性，不再作为热力图维度
- 成熟度数据由depgraph.db `nodes.design_maturity`派生

---

## 2. Maturity model / 成熟度模型

### 2.1 五档成熟度定义

| 档位 | 名称 | 定义 | depgraph.db映射 |
|:---:|------|------|----------------|
| **L0** | 缺失 | 能力完全不存在，无设计无代码 | 域无节点 |
| **L1** | 设计 | 仅有设计文档/蓝图，无代码 | `design_maturity='design'` |
| **L2** | 草稿 | 有原型代码，未集成 | `design_maturity='prototype'` |
| **L3** | 可用 | 代码可用但未生产验证 | `design_maturity='production'` + `build_status!='active'` |
| **L4** | 生产级 | 生产环境稳定运行 | `design_maturity='production'` + `build_status='active'` |
| **L5** | 顶级机构对标 | 达到Goldman/BlackRock水平 | 待评估 |

### 2.2 评分规则

- 域成熟度 = 该域所有节点的最高成熟度
- 能力域成熟度 = 该能力域下所有域成熟度的加权平均（按节点数加权）

---

## 3. 43域×10能力域热力图

> 数据源：depgraph.db `domains` + `nodes` 表
> 派生工具：`scripts/governance/d5_architecture/generators/generate_design_vs_production.py`

### 3.1 能力域定义（10能力域=7业务+3横切）

| 能力域 | 类型 | 包含域 |
|--------|:---:|--------|
| 数据接入 | 业务 | D-MKT_DATA, D-ALT_DATA, D-DATA_ENG |
| 因子研究 | 业务 | D-FACTOR, D-SIGNAL, D-SIGNAL_FUNDAMENTAL, D-SIGNAL_ASHARE, D-SIGNAL_QUALITY |
| 策略决策 | 业务 | D-PF_CORE, D-PF_ALLOC, D-SELL_DECISION, D-CROSS_ASSET |
| 执行交易 | 业务 | D-EX_CORE, D-EX_SOR, D-TRADING, D-POSITION |
| 风险控制 | 业务 | D-RISK, D-COMPLIANCE |
| 回测仿真 | 业务 | D-BACKTEST, D-SIMULATION, D-EXEC_SIM, D-DIGITAL_TWIN |
| ML平台 | 业务 | D-ML_TRAIN, D-ML_SERVE |
| 治理（横切） | 横切 | D-GOVERNANCE, D-GOV_RULE, D-GOV_AUDIT, D-GOV_DRIFT, D-GOV_ENFORCEMENT, D-GOV_REPAIR, D-GOV_SCRIPTS |
| 安全（横切） | 横切 | D-SECURITY, D-SECURITY-LLM, D-BEHAVIORAL_AUDIT, D-DATA_SEC, D-AUTONOMY_PERM |
| 基础设施（横切） | 横切 | D-INFRA_OPS, D-INFRA_RUNTIME, D-INTEGRATION, D-INTEGRATION-GATEWAY, D-SHARED, D-FRONTEND, D-REPORTING, D-KNOWLEDGE, D-INTELLIGENCE, D-AUTONOMY_CORE, D-OPS |


### 3.2 域成熟度快照（43域）

> 完整域成熟度数据见 [`generated/design_vs_production.md`](../generated/design_vs_production.md)

| 域ID | 域名称 | layer_id | 节点数 | production | design | prototype | 成熟度评级 |
|------|--------|----------|:---:|:---:|:---:|:---:|:---:|
| `D-AUTONOMY-CORE` | agent_communication | `N/A` | 0 | 0 | 0 | 0 | L0 |
| `D-AUTONOMY-PERM` | escalation | `N/A` | 0 | 0 | 0 | 0 | L0 |
| `D-GOV-ENFORCEMENT` | rule_enforcement | `N/A` | 0 | 0 | 0 | 0 | L0 |
| `D-GOV-REPAIR` | rollback | `N/A` | 0 | 0 | 0 | 0 | L0 |
| `D-GOV-SCRIPTS` | code_dedup | `N/A` | 0 | 0 | 0 | 0 | L0 |
| `D-INFRA-OPS` | resource_optimization | `N/A` | 0 | 0 | 0 | 0 | L0 |
| `D-INTEGRATION-GATEWAY` | mcp_servers | `N/A` | 0 | 0 | 0 | 0 | L0 |
| `D-ML-TRAIN` | model_profiling | `N/A` | 0 | 0 | 0 | 0 | L0 |
| `D-SECURITY-LLM` | llm_defense | `N/A` | 0 | 0 | 0 | 0 | L0 |
| `D-INFRA_A2A` | a2a_communication | `L0_infrastructure` | 114 | 114 | 0 | 0 | L3+ |
| `D-INFRA_OPS` | 基础设施运维 | `L0_infrastructure` | 404 | 3 | 387 | 8 | L3+ |
| `D-INFRA_RECOVERY` | rollback_recovery | `L0_infrastructure` | 107 | 107 | 0 | 0 | L3+ |
| `D-INFRA_RUNTIME` | runtime_integration | `L0_infrastructure` | 148 | 139 | 3 | 0 | L3+ |
| `D-INFRA_TELEMETRY` | observability_profiling | `L0_infrastructure` | 51 | 51 | 0 | 0 | L3+ |
| `D-ALT_DATA` | 另类数据 | `L1_foundation` | 68 | 0 | 61 | 1 | L2 |
| `D-BEHAVIORAL_AUDIT` | 行为审计 | `L1_foundation` | 79 | 79 | 0 | 0 | L3+ |
| `D-DATA_ENG` | 数据工程(增值+融合+知识) | `L1_foundation` | 147 | 0 | 140 | 1 | L2 |
| `D-DATA_GOV` | 数据治理(质量+血缘+参考) | `L1_foundation` | 38 | 0 | 38 | 0 | L1 |
| `D-DATA_SEC` | 数据安全与契约 | `L1_foundation` | 30 | 0 | 20 | 4 | L2 |
| `D-MKT_DATA` | 行情数据(接入+存储) | `L1_foundation` | 266 | 1 | 257 | 2 | L3+ |
| `D-AUTONOMY_CORE` | 自治核心 | `L1_platform` | 650 | 1 | 475 | 168 | L3+ |
| `D-FRONTEND` | 前端 | `L1_platform` | 237 | 7 | 213 | 11 | L3+ |
| `D-INTEGRATION` | pipeline_routing | `L1_platform` | 706 | 62 | 416 | 223 | L3+ |
| `D-OPS` | feedback-loop | `L1_platform` | 641 | 1 | 259 | 375 | L3+ |
| `D-REPORTING` | 报告 | `L1_platform` | 132 | 0 | 118 | 8 | L2 |
| `D-SECURITY` | adversarial_validation | `L1_platform` | 849 | 134 | 603 | 106 | L3+ |
| `D-SHARED` | shared_services | `L1_platform` | 288 | 62 | 7 | 219 | L3+ |
| `D-AUTONOMY_PERM` | 自治保护 | `L2_domain` | 206 | 0 | 192 | 8 | L2 |
| `D-BACKTEST` | 回测 | `L2_domain` | 9 | 0 | 2 | 1 | L2 |
| `D-COMPLIANCE` | 合规 | `L2_domain` | 916 | 0 | 891 | 19 | L2 |
| `D-CROSS_ASSET` | 跨资产 | `L2_domain` | 79 | 1 | 66 | 6 | L3+ |
| `D-DIGITAL_TWIN` | 数字孪生 | `L2_domain` | 13 | 0 | 6 | 1 | L2 |
| `D-EXEC_SIM` | 执行仿真 | `L2_domain` | 8 | 0 | 1 | 1 | L2 |
| `D-EX_CORE` | 执行核心 | `L2_domain` | 135 | 3 | 120 | 6 | L3+ |
| `D-EX_SOR` | 执行路由 | `L2_domain` | 131 | 0 | 124 | 1 | L2 |
| `D-FACTOR` | 因子 | `L2_domain` | 320 | 2 | 302 | 10 | L3+ |
| `D-GOV-DOCS` | 架构文档 | `L2_domain` | 151 | 100 | 0 | 0 | L3+ |
| `D-GOV-ENFORCEMENT` | 规则执行 | `L2_domain` | 107 | 69 | 0 | 0 | L3+ |
| `D-GOV-SCRIPTS` | 治理脚本 | `L2_domain` | 416 | 26 | 0 | 0 | L3+ |
| `D-GOVERNANCE` | lifecycle_management | `L2_domain` | 2843 | 117 | 62 | 0 | L3+ |
| `D-GOV_AUDIT` | audit-trail | `L2_domain` | 189 | 54 | 3 | 0 | L3+ |
| `D-GOV_AUDIT_TESTS` | audit_test_suite | `L2_domain` | 152 | 142 | 0 | 0 | L3+ |
| `D-GOV_DRIFT` | drift_detection | `L2_domain` | 22 | 22 | 0 | 0 | L3+ |
| `D-GOV_RULE` | 规则治理 | `L2_domain` | 12 | 11 | 1 | 0 | L3+ |
| `D-INTELLIGENCE` | context_management | `L2_domain` | 273 | 18 | 217 | 32 | L3+ |
| `D-KNOWLEDGE` | knowledge_management | `L2_domain` | 160 | 0 | 153 | 1 | L2 |
| `D-ML_SERVE` | 推理 | `L2_domain` | 69 | 0 | 62 | 1 | L2 |
| `D-ML_TRAIN` | 训练 | `L2_domain` | 118 | 0 | 107 | 5 | L2 |
| `D-PF_ALLOC` | 组合分配 | `L2_domain` | 114 | 0 | 104 | 4 | L2 |
| `D-PF_CORE` | 组合核心 | `L2_domain` | 202 | 6 | 183 | 7 | L3+ |
| `D-POSITION` | 仓位管理 | `L2_domain` | 77 | 0 | 69 | 2 | L2 |
| `D-RISK` | 风控 | `L2_domain` | 775 | 9 | 749 | 11 | L3+ |
| `D-SELL_DECISION` | 卖出决策 | `L2_domain` | 64 | 0 | 57 | 1 | L2 |
| `D-SIGNAL` | 信号 | `L2_domain` | 476 | 1 | 474 | 1 | L3+ |
| `D-SIGNAL_ASHARE` | A股特色信号 | `L2_domain` | 27 | 0 | 20 | 1 | L2 |
| `D-SIGNAL_FUNDAMENTAL` | 基本面信号 | `L2_domain` | 24 | 3 | 1 | 14 | L3+ |
| `D-SIGNAL_QUALITY` | 信号质量 | `L2_domain` | 18 | 0 | 11 | 1 | L2 |
| `D-SIMULATION` | 仿真 | `L2_domain` | 128 | 4 | 110 | 8 | L3+ |
| `D-TRADING` | 交易运营 | `L2_domain` | 249 | 16 | 89 | 138 | L3+ |


### 3.3 能力域成熟度汇总

| 能力域 | 域数量 | 总节点 | production占比 | 整体成熟度 |
|--------|:---:|:---:|:---:|:---:|
| 数据接入 | 3 | 481 | 0.2% | L1-L2 |
| 因子研究 | 5 | 865 | 0.7% | L1-L2 |
| 策略决策 | 4 | 459 | 1.5% | L1-L2 |
| 执行交易 | 4 | 592 | 3.2% | L1-L2 |
| 风险控制 | 2 | 1691 | 0.5% | L1-L2 |
| 回测仿真 | 4 | 158 | 2.5% | L1-L2 |
| ML平台 | 2 | 187 | 0.0% | L1-L2 |
| 治理（横切） | 4 | 4555 | 8.9% | L1-L2 |
| 安全（横切） | 5 | 1145 | 16.9% | L2-L3 |
| 基础设施（横切） | 11 | 4217 | 13.4% | L2-L3 |


---

## 4. Gap-to-Target / 差距分析

### 4.1 目标状态定义

| 里程碑 | 目标 | 触发条件 |
|--------|------|---------|
| **T1** | 真实资金接入 | 模拟盘稳定运行3个月 |
| **T3** | AI自治升格 | 6大核心服务全部L4 |
| **T-ENDGAME** | 顶级机构对标 | 全域能力L4+，30%域L5 |

### 4.2 当前差距（基于§3.2快照）

| 指标 | 当前 | T1目标 | T-ENDGAME目标 | 差距 |
|------|:---:|:---:|:---:|------|
| production节点占比 | 1207/14388 (8.4%) | >30% | >80% | 见`generated/design_vs_production.md` |
| L4+域数量 | 待评估 | >10 | >40 | 需逐域评估 |
| L0域数量 | 待统计 | 0 | 0 | 见§3.2 |

---

## 5. 季度 review 机制

### 5.1 刷新流程

1. 运行`generate_design_vs_production.py`刷新§3.2快照
2. 架构师逐域评估L4/L5达标情况
3. 更新§4.2差距表
4. 识别P0/P1/P2短板→纳入下季度任务卡

### 5.2 刷新频率

- 季度例行：每3个月
- 事件驱动：真实资金接入/架构重大变更

---

## 6. 与其他视图的边界

| 其他视图 | 本视图与其关系 |
|---|---|
| `business_architecture.md` | 01-BA定义"业务做什么"；本视图给每项能力打成熟度分 |
| `architecture_model/cross_cutting/capability_heatmap.yaml` | YAML是机器可读能力清单（canonical schema）；本视图是人类可读热力图视觉化 |
| `generated/design_vs_production.md` | 派生视图提供原始统计数据；本视图做能力域聚合分析 |

---

## 7. 投入估算（人月 + KB 决策记录数 + Sprint数）

> 详见各能力域蓝图。本节仅摘要。

- T1→T3：预计需6大核心服务全部升L4，约24人月
- T3→T-ENDGAME：预计需全域L4+，约60人月

---

## 8. Revision history / 修订记录

| Date / 日期 | Description / 说明 |
|------------|-------------------|
| 2026-06-23 | **v2.0.0（DM-200912 Phase4-A）**：基于§2.1裁定重写——热力图改为43域×10能力域矩阵；原14层×7能力域矩阵废弃；成熟度数据由depgraph.db派生；新增§1.4 v2.0.0变更说明、§2.1五档成熟度depgraph.db映射、§3.2域成熟度快照、§3.3能力域成熟度汇总。 |
| 2026-04-22 | v1.0.0：建立能力热力图正交视图。 |
