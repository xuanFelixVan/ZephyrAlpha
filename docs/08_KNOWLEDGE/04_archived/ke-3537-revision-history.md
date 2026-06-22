---
module_id: KE-3537
title: 8. Revision history / 修订记录
category: documentation
---

# 8. Revision history / 修订记录

8. Revision history / 修订记录

> 完整历史见 [revision_history.md](revision_history.md)。本处仅保留最近 3 次修订。

| Date / 日期 | Description / 说明 |
|------------|-------------------|
| 2026-05-06 | **v2.2.0（AUDIT-04 / 治理收口）**：双树与 SCOPE/SSoT 地图对齐；Python ≥3.11 基线贯通；`09_audit/findings` 与契约 `ownership_model`；`validate_ssot` + 登记表 + `batch_create_index_md` 修正；INV-005 源码/EA 分层消歧。详情见 [revision_history.md](revision_history.md)。 |
| 2026-05-02 | **v2.1.0（审计修复批次）**：修复 4 项 SSoT 对齐问题：(a) `architecture-model/infra/` 创建 core_services.yaml + shared_infra.yaml 骨架文件，消除 `_index.yaml` 引用不存在文件的问题；(b) `architecture_principles.md` v1.1.0 §0 新增安全红线 4 条（R1-R4），`overview.md` 同步改为引用链接，消除安全红线双源；(c) `ssot-authority-map.md` v2.3.0 移除 `layer_01` 历史误标、拆分矛盾追踪为活跃/已解决；(d) 修订历史归档至 `revision_history.md`，index.md 仅保留最近 3 条。 |
| 2026-05-01 | **v2.0.0（架构审查 P0 修复批次）**：(a) **删除 `dependency-graph-framework.md`**，其唯一独有价值——依赖置信度分级（L1/L2/L3）已提取迁入 `architecture-model/layers/schema.yaml` v2.1。(b) **by-domain 双轨结构调整**：§1bis 整节切除 + §2 文档清单 5 行 by-domain 删除。(c) **同步 06/08 视图状态**：`security_architecture.md` skeleton → active v1.0.0；`operations_architecture.md` skeleton → draft v0.2.0。 |
