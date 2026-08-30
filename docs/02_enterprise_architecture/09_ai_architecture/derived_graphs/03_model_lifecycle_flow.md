---
ttl: permanent
doc_type: architecture_view
title: 模型全生命周期流（画像→考试→护照→路由→推理→退役）
owner: ZephyrAlpha-Owner
language: zh
status: generated
version: "0.1.0"
date: 2026-08-30
topic: model_lifecycle_flow
scope: 09_ai_architecture/derived_graphs
---

# 03 · 模型全生命周期流（画像→考试→护照→路由→推理→退役）

> **派生图声明**：本文是**视图不是真源**。生成时间 2026-08-29T23:47Z（本地 2026-08-30 07:47，UTC+8）；生成方式=aiarch 3.9 一次性批生成。若与真源漂移，以真源为准并重生成本文。
>
> **源真源**：[06_model_profiling_pipeline.md](../implementation_plans/06_model_profiling_pipeline.md) §2.1/§2.4（设施盘点与结案声明）+ MOD-INF-034（画像器/护照）/ MOD-INF-036（考试编排）/ MOD-INF-035（TaskGate）蓝图 + depgraph PG 簇实测（2026-08-30）。

```mermaid
flowchart LR
    subgraph GEN["能力生成段（GP0 手动链路已通）"]
        PROF["画像<br/>MOD-INF-034 profiler.py<br/>7 维 26 项 benchmark"]
        EXAM["考试<br/>MOD-INF-036 exam_orchestrator.py<br/>五轴：横/纵/速/幻/稳"]
        PP["护照<br/>capability_passport.py<br/>CapabilityPassport·HMAC-SHA256 签名+版本迁移钩子"]
    end
    subgraph USE["能力消费段"]
        GATE["门控<br/>MOD-INF-035 task_gate.py<br/>can_dispatch(model_id, capability)"]
        ROUTE["路由<br/>model_routing/ 级联编排<br/>（MOD-MODEL_ROUTER_ORCH）"]
        INF["推理执行<br/>L2 Ollama / L3 API（见 02 篇）"]
    end
    RET["退役<br/>护照版本迁移钩子 + 退役指纹库（13 号文 §，GP1+）"]

    PROF --> EXAM --> PP --> GATE --> ROUTE --> INF
    PP -.版本迁移/退役指纹.-> RET
```

## 既定口径（真源摘录）

- **链路现状**：画像/考试/护照/门控四环节代码各自 production，GP0 手动链路 5/5 PASS（P0-1~P0-5）；已产出 7 份护照（`data/brain/passports/`，deepseek-v4-flash/pro×thinking/non-thinking + qwen2.5-coder:14b/qwen3-coder:30b/qwen3:8b）。
- **画像 7 维 vs 考试五轴**：已实测裁定**互补不重复**（06 号文 §3.2）。
- **护照更新频率**：触发式更新（06 号文 §3.3 已裁定）。
- **未闭环段**：端到端自动闭环（自动画像→自动考试→自动发护照→自动门控调度器）未建，属 GP1+（06 号文结案声明）；护照落盘 schema 缺 cost/tool 字段，待下次 Standard 考试自然补齐（不单独施工）。
- **退役段**：指纹库与正式退役流为模块工厂/路由侧 GP1+ 项，本图以虚线标注设计意图。
