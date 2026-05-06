---
module_id: "GOV-D10-README"
title: "d10_performance 维度 — 规划中"
doc_type: governance_readme
status: planned
version: "0.1.0"
owner: ZephyrAlpha-Owner
date: "2026-05-05"
summary: "性能治理维度当前处于规划阶段。本目录保留为空壳以维持治理体系12维度完整性。
  该维度的脚本将在基础设施层（VMS/CE/Orc/Pipeline）达到beta稳定态后创建。
  当前性能相关的门禁检查（如gate_timeout）由Gate Engine内置默认值覆盖。"
---

# d10_performance — 规划中

> **状态**: `planned` | **开工条件**: 至少 2 个 CT-* 契约从"规划"→"beta"

本维度负责系统的性能治理：会话预算监控、门禁耗时检查、Prompt冲突检测。
当前这些功能由 `d12_ai_hallucination` 维度的同名脚本桥接覆盖。

施工计划：
- `validate_session_budget.py`：检查单次AI session的token/时间消耗是否超标
- `validate_session_gate_check.py`：验证所有门禁规则在当前session中被触发
- `validate_gate_prompt_conflict.py`：检测AI收到的prompt指令间是否存在自相矛盾
