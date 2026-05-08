---
module_id: KE-documentat-layer_authority-004
title: 一、层架构权威 (Layer Authority)
category: documentation
---

# 一、层架构权威 (Layer Authority)

一、层架构权威 (Layer Authority)

> **🔷 双树声明（AUDIT-04 Remediation，对齐 `architecture-model/SCOPE.yaml`）**：仓库中存在两套 `architecture-model/`，职责**有意分离**，**禁止假定字节级一致**。
>
> | 树 | 路径 | SSoT 角色 |
> |----|------|-----------|
> | **EA 企业架构树** | `docs/02_enterprise_architecture/target-architecture/architecture-model/` | 跨层契约、不变量、能力热力图、`module-id-registry.yaml`（若仅存于此）、**完整** `technology/technology-landscape.yaml`、`events/`、`domain/`、`contracts/`、`cross-cutting/invariants.yaml` 等——**门禁与 validate_ssot 的层枚举权威仍以此树 `_index.yaml` + `layers/` 为真源**。 |
> | **施工分区树** | 仓库根 `architecture-model/` | `implementation_partition_registry`：C/B 双轨分区、代码目录对齐状态、`layers/*` 施工视图（与 EA 同名 partition id 可对账，非同一份文件）。 |
>
> **`AGENTS.md` §6.9** 中的泛称 `architecture-model/` → 必须先读 **SCOPE.yaml** 再判断改哪一棵树；单纯说「layers YAML」在未限定路径时默认指 **施工树根** + **并列扫描 docs 树**（与 `check_architecture_gates` / GATE-SC 行为一致）。

**权威来源（层 ID / frontmatter `layer` 合法值）**：`docs/02_enterprise_architecture/target-architecture/architecture-model/_index.yaml` + `layers/l{00..13}-*.yaml` + `layers/shared.yaml`（Stage D 后 14 层体系，L00~L13 + shared + cross_layer）

> **大小写约定**：本节 `valid_values` 使用大写 `L00`~`L13`（架构标识符惯例）。`_index.yaml` 分区 `id` 使用小写 `l00`~`l13`（文件系统标识符惯例）。两者指代同一事物，大小写差异是有意设计：大写用于架构层 ID（受保护字段），小写用于 YAML 分区 id（文件系统路径组件）。（注：`_schema.yaml` v3.0.0 已移除 `layer` 字段——模块级 layer 冗余，层归属由 partition id 承载。此大小写约定仍适用于 frontmatter `layer` 字段。）

> 本节 Layer 列表已升级为 14 层（L00-L13 + shared + cross_layer）视图，L12 (system-telemetry) / L13 (experiment-pipeline) / shared 已增补。原 Stage J 升级任务已完成。

| 层 ID     | 层名（英文）              | 层名（中文）   | 权威状态 |
|-----------|--------------------------|--------------|---------|
| L00       | Data Source Layer        | 数据源层       | Active  |
| L01       | Infrastructure Layer     | 基础设施层     | Active  |
| L02       | Alpha Factor Layer       | Alpha 因子层  | Active  |
| L03       | Signal Generation Layer  | 信号生成层     | Active  |
| L04       | Risk Management Layer    | 风险管理层     | Active  |
| L05       | Portfolio Construction   | 组合构建层     | Active  |
| L06       | Trade Execution Layer    | 交易执行层     | Active  |
| L07       | Post-Trade Analytics     | 交易后分析层   | Active  |
| L08       | Human-AI Interface       | 人机接口层     | Active  |
| L09       | Research & Innovation    | 研究创新层     | Active  |
| L10       | Governance & Compliance  | 治理合规层     | Active  |
| L11       | ML Platform              | ML 平台层     | Active  |
| L12       | System Telemetry         | 系统遥测层     | Active  |
| L13       | Experiment Pipeline      | 实验管线层     | Active  |
| shared    | Shared Concerns          | 共享关注点     | Active  |
| cross_layer | Cross-Layer Concerns   | 跨层关注点     | Active  |
