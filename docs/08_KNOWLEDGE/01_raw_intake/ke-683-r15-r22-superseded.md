---
module_id: KE-615---superseded-002
status: active
title: 关于 R15-R22 的 superseded 处理说明
category: documentation
---

# 关于 R15-R22 的 superseded 处理说明

关于 R15-R22 的 superseded 处理说明

上表中 R15 / R16 / R17 / R19 / R20 / R21 / R22 的 `status: superseded` 标记采用 **append-only 机制**（符合 discussion-document-standard v2.0.0 §6.2）：

- **原条目不删改**：保留原始结论描述，便于未来回溯"当时为什么这么想"
- **status 字段显式标注**：在描述中补 `status: superseded`
- **新结论写在后续 Stage / R 条目**：例如 R17 被后续新讨论覆盖时，应新增 R-N（N > 25）作为新版本，并在本表的"含义"栏链接
- **不使用删除线**：删除线只是视觉效果，不是机器可读状态

> 机构标准参考：KBG-0002 落地、ISO/IEC 11179 "Metadata Registries" 的状态管理规范。
