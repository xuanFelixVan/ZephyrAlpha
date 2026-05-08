---
module_id: KE-governance-5_2__02_enterprise_architectur-006
title: 5.2 `02_enterprise_architecture/`
category: governance
---

# 5.2 `02_enterprise_architecture/`

5.2 `02_enterprise_architecture/`

**用途**：企业架构文档（TOGAF 视图 + 架构模型 YAML）

**ADR 变更说明**：2026-05-05（session-012），全部 33 条 ADR 已迁入 KB:decisions namespace，
物理 `adr/` 目录已删除。架构决策的完整推导链见 `architecture-rationale-log.md`。

**准入规则**：
- ✅ TOGAF 架构视图（`0X-*-architecture.md`）
- ✅ 架构决策推导记录（`architecture-rationale-log.md`，ADR 权威真源）
- ✅ 架构模型 YAML（`layers/l<NN>-*.yaml`、`contracts/*.yaml`、`events/*.yaml` 等）
- ✅ 架构快照（`snapshots/architecture-snapshot-*.yaml`）
- ❌ 治理规范（→ `01_policies_and_standards/`）
- ❌ 模块蓝图（→ `03_modules/`）
- ❌ 独立 ADR .md 文件（→ KB:decisions namespace，不经由此目录管理）
