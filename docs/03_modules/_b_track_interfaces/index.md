---
module_id: BTRACK-IFACE-INDEX-001
title: B 轨接口规范 — 目录索引
doc_type: index
status: active
version: "2.0.0"
layer: cross_layer
owner: ZephyrAlpha-Owner
classification: internal
language: zh
created_by: human_plus_agent
date: "2026-05-03"
ttl: permanent
summary: "_b_track_interfaces/ 目录的责任声明与 5 大 B 轨核心服务接口规范的导航索引。v2.0.0：从 docs/07_ai_engineering/ 迁移至此——与蓝图、施工计划统一在 03_modules/ 下，实现 AI 冷启动单目录树遍历。"
tags: [b-track, service-interface, index, ai-engineering, interface-spec]
depends_on:
  - {target: GOV-DOC-002, at: "§一", why: "目录定位——B轨接口规范在此，蓝图在 l01_infrastructure/"}
---

# B 轨接口规范 — 目录索引

> **目录定位**：`03_modules/_b_track_interfaces/` — 5 大 B 轨核心服务的接口合同存放处。
>
> **v2.0.0 迁移**：原位于 `docs/07_ai_engineering/`，2026-05-03 迁移至此。
> 迁移理由见 [GOV-DOC-002 §一](file:///D:/ZephyrAlpha/docs/01_policies_and_standards/governance/document/directory-structure-standard.md)。

---

## 一、目录职责

| Yes（本目录管） | No（不管 → 正确位置） |
|:--|:--|
| 5 大 B 轨核心服务的接口合同（Protocol + Pydantic Schemas + API 签名） | 蓝图 → `l01_infrastructure/{module}/blueprint.md` |
| 跨服务依赖拓扑声明 | 施工计划 → `l01_infrastructure/{module}/` |
| 渐进路线（scaffold→4）与 SLO | 具体实现代码 → `src/zephyr/` |
| 错误码与降级策略 | 部署/CI/CD → `04_automation/` |

---

## 二、5 大服务清单

| # | 文件 | module_id | 职责（一句话） |
|:-:|------|-----------|------|
| 1 | `vector-memory-service-interface.md` | AI-ENG-VMS-001 | 向量记忆的持久化、语义检索与 Collection 治理 |
| 2 | `context-engine-interface.md` | AI-ENG-CTX-001 | 上下文三源汇聚、压缩、校验、注入 |
| 3 | `agent-orchestrator-interface.md` | AI-ENG-ORC-001 | 任务全生命周期编排 |
| 4 | `feedback-loop-engine-interface.md` | AI-ENG-FLE-001 | 运营指标分析、异常检测、反馈闭环 |
| 5 | `llm-security-gateway-interface.md` | AI-ENG-LSG-001 | LLM 流量四层安全防护（fail-closed） |
