---
module_id: KE-572
status: active
title: 企业架构树中的 architecture_model（镜像说明）
category: documentation
ttl: permanent
---

# 企业架构树中的 architecture_model（镜像说明）

企业架构树中的 architecture_model（镜像说明）

本目录为 **交付/查阅视图**，与仓库根目录 [`architecture_model/`](../../../../architecture_model/) **并行存在**。

- **施工真源（canonical）**：以仓库根 `architecture_model/` 为准（含 `layers/`、`SCOPE.yaml`、与代码子目录对齐的模块条目）。
- **本树角色**：便于在 `docs/02_enterprise_architecture/` 下与叙事文档同区浏览；字段约束见本目录 `layers/schema.yaml`，变更应优先在根 `architecture_model` 落地后再同步镜像（避免双源漂移）。

`module_id_registry.yaml` **文档规则类 module_id（PS-REG-/GOV-/DOM- 等）** 的权威登记仍以此文件为准（见文件头说明）；与 `architecture_model` 中的 **MOD-*** 代码模块编号二者分工不同，详见 `layers/schema.yaml` 的 `id_namespace_note`。
