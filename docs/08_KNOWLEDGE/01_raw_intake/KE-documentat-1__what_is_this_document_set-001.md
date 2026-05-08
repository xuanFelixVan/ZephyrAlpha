---
module_id: KE-documentat-1__what_is_this_document_set-001
title: 1. What is this document set / 本文档组是什么
category: documentation
---

# 1. What is this document set / 本文档组是什么

1. What is this document set / 本文档组是什么

This is the **canonical Architecture Description Set** for ZephyrAlpha 2.0.

It describes the target architecture using the **ISO 42010 + TOGAF four-layer + C4 composite approach**:

- **ISO 42010** — defines the methodology: an Architecture Description (AD) consists of multiple Views, each addressing specific Stakeholder Concerns under a defined Viewpoint.
- **TOGAF** — defines the four view layers: Business / Information / Application / Technology.
- **C4 Model** — defines application-level visualization: System Context (L1) and Container (L2).

> **Relation to `AGENTS.md` §6.9**: Markdown views here are the narrative *Architecture Description Set*; machine-consumable facts live under `architecture-model/` YAML with the dual-tree split declared in repo-root **`architecture-model/SCOPE.yaml`**. On conflict, YAML + SCOPE win; record rationale in `architecture-rationale-log.md`.

---

本文档组是 ZephyrAlpha 2.0 的**架构描述集（Architecture Description Set）** canonical 真源。

采用 **ISO 42010 + TOGAF 四视图 + C4 合成方案**：

- **ISO 42010** — 定方法论：Architecture Description 由多个 View 组成，每个 View 针对特定 Stakeholder 的 Concern。
- **TOGAF** — 定四层视图：Business / Information / Application / Technology。
- **C4 Model** — 定应用视图的可视化：系统上下文（L1）和容器（L2）。

> **与 `AGENTS.md` §6.9 的关系**：本目录下 **TOGAF/C4 视图 Markdown** 充当 *Architecture Description Set* 的阅读真源；**可机读事实**（分层登记、跨层契约、不变量、technology-landscape 全量等）以 `architecture-model/` 下 YAML + 仓库根 **`architecture-model/SCOPE.yaml`** 双树分工为准。二者冲突时——以 YAML + SCOPE 为机器裁决依据，并回写 rationale-log。

---

---
