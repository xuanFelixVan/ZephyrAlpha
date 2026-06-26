---
module_id: KE-1206----------------------005
status: active
title: 🔴 RULE-FOUR：创建即注册协议 — 不注册，不落盘（与 RULE-ZERO / RULE-ONE / RULE-TWO / RULE-THREE 同级）
category: governance_rule
ttl: permanent
doc_type: knowledge_entry
---

# 🔴 RULE-FOUR：创建即注册协议 — 不注册，不落盘（与 RULE-ZERO / RULE-ONE / RULE-TWO / RULE-THREE 同级）

🔴 RULE-FOUR：创建即注册协议 — 不注册，不落盘（与 RULE-ZERO / RULE-ONE / RULE-TWO / RULE-THREE 同级）

> **触因**：`g6-ctr-compliance.yaml` 未被 `gates/_registry.yaml` 登记——创建文件时没有强制"创建=注册"。<br>
> **根因**：手工流程依赖 AI 记忆 → 遗忘 → 孤儿 → 注册表滞后不可信。<br>
> **根治**：`scaffold.py` 作为**唯一创建入口**——绕过它就无法落盘。
