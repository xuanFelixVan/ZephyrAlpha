---
module_id: KE-documentat-d-align___________yaml-006
title: D-ALIGN：架构文档 ↔ 模型 YAML 一致性
category: documentation
---

# D-ALIGN：架构文档 ↔ 模型 YAML 一致性

D-ALIGN：架构文档 ↔ 模型 YAML 一致性

| 检查项 | 结果 | 说明 |
|--------|:----:|------|
| 架构视图文档 ↔ architecture-model YAML 一致性 | ⚠️ | 双树 L13 命名不一致（见 P0-001） |
| 两套 architecture-model 主从关系 | ✅ | `architecture-model/` = 施工树主源；`docs/02/.../architecture-model/` = 企业架构树副本，revision-history v2.2.0 已声明 |
| ADR 决策 ↔ 技术全景 YAML 一致性 | ✅ | ADR-0015~0020 与 vibe-coding-infrastructure-tech-stack.yaml 17 项技术选型一一对应 |

**P0-001**：`architecture-model/layers/l13_experimentation.yaml`（施工树）与 `docs/.../architecture-model/layers/l13-experiment-pipeline.yaml`（企业架构树）文件名不一致。根因：施工树采用 `l13_experimentation`（与 src/ 目录一致），企业架构树采用 `l13-experiment-pipeline`（与 03-AA 视图历史命名一致）。**状态**：被 session-20260506-003 锁定（AUDIT-03 任务），待其释放后统一。

**P1-001**：B 轨 12 个目录（context_engine, core, dashboard, db, feedback_loop, gates, kb, llm_security, mcp, orchestrator, rules, vector_memory）在施工树 `architecture-model/layers/` 中已定义，但在企业架构树 `docs/.../architecture-model/layers/` 中仅有 `b_mcp.yaml` 一个文件，其余 11 个 B 轨层未同步。**根因**：SCOPE.yaml R3 明确允许同一 partition.id 两侧各有不同文件名的 YAML；B 轨为施工视图专属。**状态**：按 SCOPE.yaml R3 允许差异，GATE-DTS 检查降级为 P2。

**P1-002**：`architecture-model/technology-landscape.yaml`（施工树，40 行极简版）与 `docs/.../architecture-model/technology/technology-landscape.yaml`（企业架构树，570 行完整版）内容差异巨大。**状态**：✅ 已修复——施工树版本已声明 `status: deprecated` + `deprecation_reason`，指向 EA 树完整版真源。

**P2-001**：`00-overview.md` §5A.2 描述 6 大核心服务属于 L12，但 `architecture-model/infra/core-services.yaml` 未显式声明与 L12 的归属关系。**状态**：✅ 已修复——已增加 `parent_layer: L12` 字段。

---
