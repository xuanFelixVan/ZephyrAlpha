---
module_id: VIEW-04TER-CAPABILITY-HEATMAP
title: Target Architecture — Capability Maturity Heatmap (Orthogonal View) / 目标架构：能力成熟度热力图正交视图 （被恢复）
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
summary: ZephyrAlpha 2.0 能力成熟度热力图正交视图（v2.0.0）。基于§2.1裁定，热力图改为53域×10能力域二维矩阵。原14层×7能力域矩阵废弃。成熟度数据由depgraph派生。
date: '2026-06-26'
ttl: permanent
---

## 1. Purpose & 为什么需要能力热力图

### 1.1 本视图要回答的问题

| 问题 | 答案所在 |
|---|---|
| ZephyrAlpha 的核心业务能力是什么？每一项当前多成熟？| §3 53域×10能力域热力图 |
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
- 原14层×7能力域矩阵 → 改为53域×10能力域矩阵
- 14层降级为域属性，不再作为热力图维度
- 成熟度数据由depgraph `nodes.design_maturity`派生

---

## 2. Maturity model / 成熟度模型

### 2.1 五档成熟度定义

| 档位 | 名称 | 定义 | depgraph映射 |
|:---:|------|------|----------------|
| **L0** | 缺失 | 能力完全不存在，无设计无代码 | 域无节点 |
| **L1** | 设计 | 仅有设计文档/蓝图，无代码 | `design_maturity='design'` |
| **L2** | 草稿 | 有原型代码，未集成 | `design_maturity='design'` |
| **L3** | 可用 | 代码可用但未生产验证 | `design_maturity='production'` + `build_status!='active'` |
| **L4** | 生产级 | 生产环境稳定运行 | `design_maturity='production'` + `build_status='active'` |
| **L5** | 顶级机构对标 | 达到Goldman/BlackRock水平 | 待评估 |

### 2.2 评分规则

- 域成熟度 = 该域所有节点的最高成熟度
- 能力域成熟度 = 该能力域下所有域成熟度的加权平均（按节点数加权）

---

## 3. 53域×10能力域热力图

> 数据源：depgraph `domains` + `nodes` 表
> 派生工具：`scripts/governance/d5_architecture/generators/generate_design_vs_production.py`

### 3.1 能力域定义（10能力域=7业务+3横切）

| 能力域 | 类型 | 包含域 |
|--------|:---:|--------|
| 数据接入 | 业务 | D_MKT_DATA, D_ALT_DATA, D_DATA_ENG |
| 因子研究 | 业务 | D_FACTOR, D_SIGLEGACY, D_FUNDAMENTAL_SIGNAL, D_ASHARE_SIGNAL, D_SIGQC |
| 策略决策 | 业务 | D_PF_CORE, D_PF_ALLOC, D_SELL_DECISION, D_CROSS_ASSET |
| 执行交易 | 业务 | D_EX_CORE, D_EX_SOR, D_TRADING, D_POSITION |
| 风险控制 | 业务 | D_RISK, D_COMPLIANCE |
| 回测仿真 | 业务 | D_BACKTEST, D_SIMULATION, D_EXEC_SIM, D_DIGITAL_TWIN |
| ML平台 | 业务 | D_ML_TRAIN, D_ML_SERVE |
| 治理（横切） | 横切 | D_GOVERNANCE, D_GOV_RULE, D_GOV_AUDIT, D_GOV_DRIFT, D_GOV_ENFORCEMENT, D-GOV_REPAIR, D_GOV_SCRIPTS |
| 安全（横切） | 横切 | D_SECURITY, D_SECURITY_LLM, D_BEHAVIORAL_AUDIT, D_DATA_SEC, D_AUTONOMY_PERM |
| 基础设施（横切） | 横切 | D_INFRA_OPS, D_INFRA_RUNTIME, D_INTEGRATION, D_INTEGRATION_GATEWAY, D_SHARED, D_FRONTEND, D_REPORTING, D_KNOWLEDGE, D_INTELLIGENCE, D_AUTONOMY_CORE, D_OPS |


### 3.2 域成熟度快照（53域）

> 完整域成熟度数据见 [`generated/design_vs_production.md`](../generated/design_vs_production.md)

| 域ID | 域名称 | layer_id | 节点数 | production | design | prototype | 成熟度评级 |
|------|--------|----------|:---:|:---:|:---:|:---:|:---:|
| `D_GOV_REPAIR` | rollback | `N/A` | 0 | 0 | 0 | 0 | L0 |
| `D_INFRA_A2A` | a2a_communication | `L0_infrastructure` | 114 | 114 | 0 | 0 | L3+ |
| `D_INFRA_OPS` | resource_optimization | `L0_infrastructure` | 34 | 7 | 1 | 26 | L3+ |
| `D_INFRA_RECOVERY` | rollback_recovery | `L0_infrastructure` | 107 | 107 | 0 | 0 | L3+ |
| `D_INFRA_RUNTIME` | runtime_integration | `L0_infrastructure` | 145 | 139 | 0 | 6 | L3+ |
| `D_INFRA_TELEMETRY` | observability_profiling | `L0_infrastructure` | 51 | 51 | 0 | 0 | L3+ |
| `D_ALT_DATA` | 另类数据 | `L1_foundation` | 8 | 1 | 0 | 7 | L3+ |
| `D_AUTONOMY_CORE` | agent_communication | `L1_foundation` | 176 | 2 | 0 | 174 | L3+ |
| `D_BEHAVIORAL_AUDIT` | 行为审计 | `L1_foundation` | 79 | 79 | 0 | 0 | L3+ |
| `D_DATA_ENG` | 数据工程(增值+融合+知识) | `L1_foundation` | 7 | 0 | 0 | 7 | L2 |
| `D_DATA_GOV` | 数据治理(质量+血缘+参考) | `L1_foundation` | 0 | 0 | 0 | 0 | L0 |
| `D_DATA_SEC` | 数据安全与契约 | `L1_foundation` | 10 | 0 | 0 | 10 | L2 |
| `D_FRONTEND` | 前端 | `L1_foundation` | 23 | 7 | 0 | 16 | L3+ |
| `D_INTEGRATION` | pipeline_routing | `L1_foundation` | 296 | 70 | 0 | 226 | L3+ |
| `D_INTEGRATION_GATEWAY` | mcp_servers | `L1_foundation` | 0 | 0 | 0 | 0 | L0 |
| `D_MKT_DATA` | 行情数据(接入+存储) | `L1_foundation` | 9 | 1 | 0 | 8 | L3+ |
| `D_OPS` | feedback-loop | `L1_foundation` | 433 | 24 | 1 | 408 | L3+ |
| `D_REPORTING` | 报告 | `L1_foundation` | 15 | 1 | 0 | 14 | L3+ |
| `D_SECURITY` | adversarial_validation | `L1_foundation` | 244 | 132 | 0 | 112 | L3+ |
| `D_SECURITY_LLM` | llm_defense | `L1_foundation` | 0 | 0 | 0 | 0 | L0 |
| `D_SHARED` | shared_services | `L1_foundation` | 296 | 93 | 0 | 203 | L3+ |
| `D_ASHARE_SIGNAL` | ashare_signal | `L2_domain` | 7 | 0 | 0 | 7 | L2 |
| `D_AUDITTEST` | audit_test_suite | `L2_domain` | 152 | 142 | 0 | 10 | L3+ |
| `D_AUTONOMY_PERM` | escalation | `L2_domain` | 70 | 2 | 1 | 67 | L3+ |
| `D_BACKTEST` | 回测 | `L2_domain` | 7 | 0 | 0 | 7 | L2 |
| `D_COMPLIANCE` | 合规 | `L2_domain` | 25 | 0 | 0 | 25 | L2 |
| `D_CROSS_ASSET` | 跨资产 | `L2_domain` | 11 | 1 | 1 | 9 | L3+ |
| `D_DIGITAL_TWIN` | 数字孪生 | `L2_domain` | 8 | 0 | 1 | 7 | L2 |
| `D_EXEC_SIM` | 执行仿真 | `L2_domain` | 7 | 0 | 0 | 7 | L2 |
| `D_EX_CORE` | 执行核心 | `L2_domain` | 14 | 3 | 0 | 11 | L3+ |
| `D_EX_SOR` | 执行路由 | `L2_domain` | 7 | 0 | 0 | 7 | L2 |
| `D_FACTOR` | 因子 | `L2_domain` | 17 | 2 | 0 | 15 | L3+ |
| `D_FUNDAMENTAL_SIGNAL` | fundamental_signal | `L2_domain` | 25 | 4 | 0 | 21 | L3+ |
| `D_GOVERNANCE` | lifecycle_management | `L2_domain` | 2831 | 117 | 50 | 2664 | L3+ |
| `D_GOV_AUDIT` | audit-trail | `L2_domain` | 188 | 54 | 2 | 132 | L3+ |
| `D_GOV_DOCS` | architecture_docs | `L2_domain` | 127 | 78 | 0 | 49 | L3+ |
| `D_GOV_DRIFT` | drift_detection | `L2_domain` | 24 | 9 | 1 | 14 | L3+ |
| `D_GOV_ENFORCEMENT` | rule_enforcement | `L2_domain` | 107 | 69 | 0 | 38 | L3+ |
| `D_GOV_RULE` | rule_governance | `L2_domain` | 11 | 11 | 0 | 0 | L3+ |
| `D_GOV_SCRIPTS` | code_dedup | `L2_domain` | 416 | 26 | 0 | 390 | L3+ |
| `D_INTELLIGENCE` | context_management | `L2_domain` | 56 | 18 | 0 | 38 | L3+ |
| `D_KNOWLEDGE` | knowledge_management | `L2_domain` | 41 | 1 | 2 | 38 | L3+ |
| `D_ML_SERVE` | 推理 | `L2_domain` | 7 | 0 | 0 | 7 | L2 |
| `D_ML_TRAIN` | model_profiling | `L2_domain` | 12 | 0 | 1 | 11 | L2 |
| `D_PF_ALLOC` | 组合分配 | `L2_domain` | 11 | 0 | 1 | 10 | L2 |
| `D_PF_CORE` | 组合核心 | `L2_domain` | 44 | 6 | 26 | 12 | L3+ |
| `D_POSITION` | 仓位管理 | `L2_domain` | 8 | 0 | 0 | 8 | L2 |
| `D_RISK` | 风控 | `L2_domain` | 25 | 9 | 0 | 16 | L3+ |
| `D_SELL_DECISION` | 卖出决策 | `L2_domain` | 7 | 0 | 0 | 7 | L2 |
| `D_SIGLEGACY` | siglegacy | `L2_domain` | 0 | 0 | 0 | 0 | L0 |
| `D_SIGQC` | signal_quality | `L2_domain` | 7 | 0 | 0 | 7 | L2 |
| `D_SIMULATION` | 仿真 | `L2_domain` | 19 | 4 | 1 | 14 | L3+ |
| `D_TRADING` | 交易运营 | `L2_domain` | 163 | 20 | 0 | 143 | L3+ |


### 3.3 能力域成熟度汇总

| 能力域 | 域数量 | 总节点 | production占比 | 整体成熟度 |
|--------|:---:|:---:|:---:|:---:|
| 数据接入 | 3 | 24 | 8.3% | L1-L2 |
| 因子研究 | 5 | 56 | 10.7% | L2-L3 |
| 策略决策 | 4 | 73 | 9.6% | L1-L2 |
| 执行交易 | 4 | 192 | 12.0% | L2-L3 |
| 风险控制 | 2 | 50 | 18.0% | L2-L3 |
| 回测仿真 | 4 | 41 | 9.8% | L1-L2 |
| ML平台 | 2 | 19 | 0.0% | L1-L2 |
| 治理（横切） | 6 | 3577 | 8.0% | L1-L2 |
| 安全（横切） | 5 | 403 | 52.9% | L3+ |
| 基础设施（横切） | 11 | 1515 | 23.9% | L2-L3 |


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
| production节点占比 | 1404/6501 (21.6%) | >30% | >80% | 见`generated/design_vs_production.md` |
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
| `business_principles.md` + `value_stream_map.yaml` | 01-BA定义"业务做什么"（永恒方法论在 principles，运营结构化数据在 YAML）；本视图给每项能力打成熟度分 |
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
| 2026-06-26 | **v2.0.0（DM-200912 Phase4-A）**：基于§2.1裁定重写——热力图改为53域×10能力域矩阵；原14层×7能力域矩阵废弃；成熟度数据由depgraph派生；新增§1.4 v2.0.0变更说明、§2.1五档成熟度depgraph映射、§3.2域成熟度快照、§3.3能力域成熟度汇总。 |
| 2026-04-22 | v1.0.0：建立能力热力图正交视图。 |
