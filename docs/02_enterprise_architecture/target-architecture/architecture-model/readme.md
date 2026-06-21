---
blueprint_id: DOM-GOV-001
---

# 企业架构树中的 architecture-model（镜像说明）

本目录为 **交付/查阅视图**，与仓库根目录 [`architecture-model/`](../../../../architecture-model/) **并行存在**。

- **施工真源（canonical）**：以仓库根 `architecture-model/` 为准（含 `layers/`、`SCOPE.yaml`、与代码子目录对齐的模块条目）。
- **本树角色**：便于在 `docs/02_enterprise_architecture/` 下与叙事文档同区浏览；字段约束见本目录 `layers/_schema.yaml`，变更应优先在根 `architecture-model` 落地后再同步镜像（避免双源漂移）。

`module-id-registry.yaml` **文档规则类 module_id（PS-REG-/GOV-/DOM- 等）** 的权威登记仍以此文件为准（见文件头说明）；与 `architecture-model` 中的 **MOD-*** 代码模块编号二者分工不同，详见 `layers/_schema.yaml` 的 `id_namespace_note`。
