---
blueprint_id: MOD-GOVERNANCE
title: architecture_model README
module_id: GOV-046
ttl: permanent
doc_type: readme
---

# 企业架构树中的 architecture_model（双树职责分离说明）

本目录为 **EA 企业架构树**，与仓库根 [`architecture_model/`](../../../../architecture_model/)（**施工分区树**）**职责有意分离，禁止假定字节级一致**（AUDIT-04 Remediation，对齐 [`scope.yaml`](../../../../architecture_model/scope.yaml) R1/R2/R3）。

| 树 | 路径 | SSoT 角色 |
|----|------|-----------|
| **EA 企业架构树**（本目录） | `docs/02_enterprise_architecture/target_architecture/architecture_model/` | 跨层契约、不变量、能力热力图、`module_id_registry.yaml`、`technology/`、`events/`、`domain/`、`contracts/`、`cross_cutting/invariants.yaml`——**门禁与 validate_ssot 的层枚举权威以此树 `_index.yaml` + `layers/` 为真源** |
| **施工分区树** | 仓库根 `architecture_model/` | `implementation_partition_registry`：C/B 双轨分区、代码目录对齐状态、`layers/*` 施工视图 |

**职责分工铁律**（scope.yaml R1/R2/R3）：
- R1：契约 / 不变量 / cross-layer-contracts 的修改 MUST 在本树（EA 树）下进行
- R2：代码目录登记、partition 施工状态、B 轨分区 MUST 在施工树（仓库根）`_index.yaml` + `layers/` 下维护
- R3：同一 partition.id（如 l12）允许两侧各有 YAML：施工视图 vs EA 视图；禁止假定两侧文件字节级一致

`module_id_registry.yaml` **文档规则类 module_id（PS-REG-/GOV-/DOM- 等）** 的权威登记以此文件为准；与施工树中的 **MOD-*** 代码模块编号二者分工不同。
