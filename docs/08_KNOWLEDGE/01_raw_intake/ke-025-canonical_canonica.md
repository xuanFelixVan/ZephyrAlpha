---
module_id: KE-025--------canonica-002
status: active
title: 6.17 Canonical 物理位置铁律（Canonical Physical Location Mandate）
category: agent_instruction
ttl: permanent
---

# 6.17 Canonical 物理位置铁律（Canonical Physical Location Mandate）

6.17 Canonical 物理位置铁律（Canonical Physical Location Mandate）

> **v1.0.0（2026-05-04）**：对标 OpenAPI spec.yaml 放 CI 消费点 / K8s types.go 放代码生成器消费点 / Cursor CLAUDE.md 放自动加载点。

**核心原则**：Canonical 定义的物理位置 = AI 加载它的位置——不是"放在某处靠引用"，而是放在 AI 必然读到的地方。

- Canonical 定义文件必须在 §8.2 热记忆或领域触发清单中
- Canonical 定义文件禁止在 §8.3 冷记忆中 → 发现即 P0 缺陷，须同一 session 内提 ADR 迁移
- 与 §6.9 关系：§6.9 定义"谁有权定义"（canonical 权威），§6.17 定义"定义放在哪"（物理位置）——互补
- 多消费点需要同一信息 → 自动派生摘要（标注 `derived_from` + `derived_version`），不复制
- 审查每对"热记忆摘要 vs 冷记忆 canonical"：如果热记忆摘要已足够完整 → 删冷记忆独立的 canonical 文件。少一份文档 = 少一个漂移风险
