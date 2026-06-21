---
module_id: MOD-005
title: B 轨接口规范 — 目录索引
doc_type: index
status: Active
version: "2.2.0"
layer: cross_layer
owner: ZephyrAlpha-Owner
classification: internal
language: zh
created_by: human_plus_agent
date: "2026-05-06"
ttl: permanent
summary: "B 轨 6 大核心服务接口索引。v2.2.0：truth_source 统一指向各 MOD-INF 蓝图 + architecture-model b_*.yaml；目录说明对齐 Phase 5（l01 + _cross_layer）。"
tags: [b-track, service-interface, index, ai-engineering, interface-spec]
depends_on:
  - {target: GOV-DOC-002, at: "§一", why: "目录定位——接口在此目录；对应模块蓝图在 docs/03_modules/_domain-infra_ops/ 与 docs/03_modules/_cross_layer/（以 module-registry path 为准）"}
---

# B 轨接口规范 — 目录索引

> **目录定位**：`03_modules/_b_track_interfaces/` — 6 大 B 轨核心服务的接口合同存放处。
>
> **v2.0.0 迁移**：原位于 `docs/07_ai_engineering/`，2026-05-03 迁移至此。
> 迁移理由见 [GOV-DOC-002 §一](file:///D:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_028_doc_structure_naming.yaml)。

---

## 一、目录职责

| Yes（本目录管） | No（不管 → 正确位置） |
|:--|:--|
| 6 大 B 轨核心服务的接口合同（Protocol + Pydantic Schemas + API 签名） | 模块蓝图 → `docs/03_modules/_domain-infra_ops/{module}/blueprint.md` **或** `docs/03_modules/_cross_layer/{module}/blueprint.md`（见 `module-registry.yaml` 的 path） |
| 跨服务依赖拓扑声明 | 施工计划 → 同上模块目录 |
| 渐进路线（scaffold→4）与 SLO | 具体实现代码 → `src/zephyr/` |
| 错误码与降级策略 | 部署/CI/CD → `04_automation/` |

---

## 二、6 大服务清单

各接口 frontmatter 已登记 `mod_master_blueprint: MOD-MASTER-001` 与 `mod_master_contracts`（CT-* 编号），与集成总蓝图 §2.1 契约总表对齐。

| # | 文件 | module_id | 职责（一句话） |
|:-:|------|-----------|------|
| 1 | `vector-memory-service-interface.md` | AI-ENG-VMS-001 | 向量记忆的持久化、语义检索与 Collection 治理 |
| 2 | `context-engine-interface.md` | AI-ENG-CTX-001 | 上下文三源汇聚、压缩、校验、注入 |
| 3 | `agent-orchestrator-interface.md` | AI-ENG-ORC-001 | 任务全生命周期编排 |
| 4 | `feedback-loop-engine-interface.md` | AI-ENG-FLE-001 | 运营指标分析、异常检测、反馈闭环 |
| 5 | `llm-security-gateway-interface.md` | AI-ENG-LSG-001 | LLM 流量纵深安全防护（fail-closed） |
| 6 | `task-pipeline-service-interface.md` | AI-ENG-PIP-001 | M1–M11 双管线路由与门禁剖面（真源 MOD-INF-009） |
