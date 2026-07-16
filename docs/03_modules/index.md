---
classification: internal
date: "2026-06-22"
doc_type: index
module_id: MOD-074
status: Active
title: 03_modules — 模块蓝图目录索引
version: "3.0.0"
language: zh
created_by: human_plus_agent
ttl: permanent
summary: "模块蓝图目录索引。v3.0.0：对齐43域架构方案（27业务域+12平台域），统一下划线命名，移除14层并行分类引用。"
tags: [modules, blueprint, index, domain, architecture]
depends_on:
  - {target: GOV-DOC-002, at: "§一", why: "目录定位——模块蓝图在此目录；架构分类体系真源在 architecture_upgrade_discussion.md"}
---

# 03_modules — 模块蓝图目录索引

> **架构真源**：[architecture_upgrade_discussion.md](file:///D:/ZephyrAlpha/docs/02_enterprise_architecture/architecture_upgrade_discussion.md) §二（43域方案）+ §17.6（域方案 v4）
>
> **命名规范**：全项目统一下划线（snake_case）。禁止连字符（kebab-case）。

---

## 一、责任声明（Single Responsibility）

本目录只存放：**模块蓝图（blueprint.md）+ 模块级索引（index.md）+ 模块交付物（delivery/）+ 模块变更记录（changes/）**。

| Yes（本目录管） | No（不管 → 正确位置） |
|:--|:--|
| 各模块的蓝图文档 | 治理规范/标准 → `01_policies_and_standards/` |
| 模块级目录索引 | 企业架构视图 → `02_enterprise_architecture/` |
| 模块交付物与变更记录 | 具体实现代码 → `src/zephyr/` |
| 模块清单注册表 | 治理脚本 → `scripts/governance/` |

---

## 二、架构分类体系（43域方案）

> **裁定**：D19/D21 — 14层降级为域属性，43域为唯一分类体系。
> **状态**：阶段4搬家基本完成；D-DATA/D_SIMULATION 各拆4域待阶段5-8执行（D_SIGLEGACY 已删除，signal 层已拆分为 D_ASHARE_SIGNAL/D_FUNDAMENTAL_SIGNAL/D_SIGQC 3子域）。

### 2.1 业务域（27域，含3个待拆分域）

| 域目录 | 域 ID | 责任 | 状态 |
|--------|------|------|------|
| [_domain_data/](file:///D:/ZephyrAlpha/docs/03_modules/_domain_data/index.md) | D-DATA | 数据源（待拆分: D_MKT_DATA/D_DATA_ENG/D_DATA_GOV/D_DATA_SEC） | 待拆分 |
| [_domain_signal/](file:///D:/ZephyrAlpha/docs/03_modules/_domain_signal/index.md) | signal 层（D_ASHARE_SIGNAL/D_FUNDAMENTAL_SIGNAL/D_SIGQC） | 信号生成（3子域） | 活跃 |
| [_domain_simulation/](file:///D:/ZephyrAlpha/docs/03_modules/_domain_simulation/index.md) | D_SIMULATION | 实验仿真（待拆分: 4域） | 待拆分 |
| [_domain_factor/](file:///D:/ZephyrAlpha/docs/03_modules/_domain_factor/index.md) | D_FACTOR | Alpha 因子 | 活跃 |
| [_domain_portfolio_core/](file:///D:/ZephyrAlpha/docs/03_modules/_domain_portfolio_core/index.md) | D_PF_CORE | 组合核心 | 活跃 |
| [_domain_execution_core/](file:///D:/ZephyrAlpha/docs/03_modules/_domain_execution_core/index.md) | D_EX_CORE | 执行核心 | 活跃 |
| [_domain_risk/](file:///D:/ZephyrAlpha/docs/03_modules/_domain_risk/index.md) | D_RISK | 风险管理 | 活跃 |
| [_domain_research/](file:///D:/ZephyrAlpha/docs/03_modules/_domain_research/index.md) | D-RESEARCH | 研究创新 | 活跃 |
| [_domain_backtest/](file:///D:/ZephyrAlpha/docs/03_modules/_domain_backtest/blueprint.md) | D_BACKTEST | 回测引擎（双模式：向量化+事件驱动，2026-07-02 从 D-RESEARCH 独立） | 活跃 |
| [_domain_reporting/](file:///D:/ZephyrAlpha/docs/03_modules/_domain_reporting/index.md) | D_REPORTING | 报表分析 | 活跃 |
| [_domain_machine_learning_train/](file:///D:/ZephyrAlpha/docs/03_modules/_domain_machine_learning_train/index.md) | D_ML_TRAIN | ML 训练 | 活跃 |
| [_domain_knowledge/](file:///D:/ZephyrAlpha/docs/03_modules/_domain_knowledge/index.md) | D_KNOWLEDGE | 知识库 | 活跃 |
| [_domain_frontend/](file:///D:/ZephyrAlpha/docs/03_modules/_domain_frontend/index.md) | D_FRONTEND | 前端 | 活跃 |
| [_domain_compliance/](file:///D:/ZephyrAlpha/docs/03_modules/_domain_compliance/index.md) | D_COMPLIANCE | 合规 | 活跃 |
| [_domain_governance/](file:///D:/ZephyrAlpha/docs/03_modules/_domain_governance/index.md) | D_GOVERNANCE | 治理 | 活跃 |
| [_domain_infrastructure_operations/](file:///D:/ZephyrAlpha/docs/03_modules/_domain_infrastructure_operations/index.md) | D-INFRA-OPS | 基础设施运维 | 活跃 |
| [_domain_infrastructure_runtime/](file:///D:/ZephyrAlpha/docs/03_modules/_domain_infrastructure_runtime/index.md) | D_INFRA_RUNTIME | 基础设施运行时 | 活跃 |
| [_domain_integration/](file:///D:/ZephyrAlpha/docs/03_modules/_domain_integration/blueprint.md) | D_INTEGRATION | 集成 | 活跃 |
| [_domain_autonomy_core/](file:///D:/ZephyrAlpha/docs/03_modules/_domain_autonomy_core/agent_role_based_access_control/blueprint.md) | D_AUTONOMY_CORE | 自治核心 | 活跃 |
| [_domain_autonomy_perm/](file:///D:/ZephyrAlpha/docs/03_modules/_domain_autonomy_perm/budget_enforcer/blueprint.md) | D_AUTONOMY_PERM | 自治权限 | 活跃 |

### 2.2 平台域/跨层（12平台域 + 跨层模块）

| 目录 | 说明 | 入口 |
|------|------|------|
| [_cross_layer/](file:///D:/ZephyrAlpha/docs/03_modules/_cross_layer/index.md) | 跨层模块（agent_orchestrator, context_engine, feedback_loop, gate_engine, llm_security, mcp_servers, pipeline, shared_core 等 17 模块） | index.md |
| [_b_track_interfaces/](file:///D:/ZephyrAlpha/docs/03_modules/_cross_layer/_b_track_interfaces/index.md) | B 轨 6 大核心服务接口合同 | index.md（位于 _cross_layer/ 下） |
| [_master_blueprint/](file:///D:/ZephyrAlpha/docs/03_modules/_master_blueprint/index.md) | 集成总蓝图（MOD-MASTER_BLUEPRINT） | blueprint.md |
| [_system_master/](file:///D:/ZephyrAlpha/docs/03_modules/_system_master/index.md) | 系统主蓝图（SYS-MASTER-001） | blueprint.md |

### 2.3 遗留目录（已标记 Deprecated）

| 目录 | 说明 | 处置 |
|------|------|------|
| [_alpha_signal_domain/](file:///D:/ZephyrAlpha/docs/03_modules/_alpha_signal_domain/blueprint.md) | 旧 Alpha Signal 域（已被 signal 层 3 子域取代） | status=Deprecated，禁止新建引用；待 RULE-THREE 审判后删除或合并 |
| [_ml_experiment_domain/](file:///D:/ZephyrAlpha/docs/03_modules/_ml_experiment_domain/blueprint.md) | 旧 ML Experiment 域（已被 D_SIMULATION 取代） | status=Deprecated，禁止新建引用；待 RULE-THREE 审判后删除或合并 |

---

## 三、核心注册表

| 注册表文件 | 说明 | 格式 |
|-----------|------|:---:|
| [blueprint_registry.yaml](file:///D:/ZephyrAlpha/docs/03_modules/blueprint_registry.yaml) | 蓝图注册表（全项目模块清单·SSoT） | YAML |
| [template_registry.yaml](file:///D:/ZephyrAlpha/docs/03_modules/template_registry.yaml) | 模板注册表 | YAML |
| [path_ownership_map.yaml](file:///D:/ZephyrAlpha/docs/03_modules/path_ownership_map.yaml) | 路径归属映射 | YAML |
| [system_pathway_registry.yaml](file:///D:/ZephyrAlpha/docs/03_modules/system_pathway_registry.yaml) | [DEPRECATED 2026-07-16] 系统路径注册表（功能已被 path_ownership_map.yaml + blueprint_registry.yaml 覆盖） | YAML |

---

## 四、命名规范

| 对象 | 规范 | 示例 |
|------|------|------|
| 目录名 | snake_case | `_domain_data/`, `datasource_core/` |
| 文件名 | snake_case | `blueprint_registry.yaml`, `blueprint.md` |
| 域目录前缀 | `_domain_*` | `_domain_factor/` |
| 跨层目录前缀 | `_cross_layer` 或功能名 | `_cross_layer/` |

> **豁免**：`docker-compose.yml` / `docker-compose.yaml`（Docker 外部约定）。

---

## 五、架构升级状态（2026-06-22）

| 阶段 | 内容 | 状态 |
|------|------|------|
| 阶段 0-3 | 架构设计 + 工具链升级 | ✅ 完成 |
| 阶段 4 | 物理搬家（连字符→下划线） | ✅ 基本完成 |
| 阶段 5-8 | 业务层建设（R3-R6） | ⏳ 未开始 |

> **本索引为过渡版本**：阶段 5-8 完成后，D-DATA/D_SIMULATION 拆分落地（D_SIGLEGACY 已删除），本索引需同步更新。

---

## 六、导航

- [上级目录](file:///D:/ZephyrAlpha/docs/index.md)
- [架构真源](file:///D:/ZephyrAlpha/docs/02_enterprise_architecture/architecture_upgrade_discussion.md)
- [能力定位书](file:///D:/ZephyrAlpha/docs/02_enterprise_architecture/04_architecture_principles_decisions/dependency_path_panorama.md)
