---
module_id: KE-179
title: 2.2 决策与记忆类
category: documentation
ttl: permanent
doc_type: knowledge_entry
---

# 2.2 决策与记忆类

2.2 决策与记忆类

| 大白话 | 行业术语 | 解释 | 关联文档 |
|-------|---------|------|---------|
| 为什么这么定 / 理由记录 | Architecture Decision Record (ADR) | 一份决策的永久凭证，含背景、方案对比、最终选择、后果 | **`KB:decisions`**（Git-backed） |
| 推导链 / 讨论记录 | Rationale Log / Design Rationale | 推导出当前结论的时间轴 | `architecture-rationale-log.md` |
| 还没想清楚的事 | Open Question / Open Issue | 已识别但未拍板的问题 | ~~`open-questions-register.md`~~（待建立） |
| 可能出坏事的事 | Risk | 已识别的威胁，需要缓解或接受 | `_registry/catalogs/ai-risk-registry.md` |
| 记笔记 / 会议纪要 | Session Log / Meeting Notes | 一次会话/会议的记录 | `governance/ai/handoff-protocol.md`、`docs/19_development_workspace/session-logs/` |
| 事后复盘 | Post-Mortem / Retrospective | 事件/阶段结束后的回顾 | （未启用） |
| 组织记忆 | Organizational Memory | 团队层面的经验、决策、知识的系统化沉淀 | ~~`organizational-memory-system-design.md`~~（待建立） |
| 决策记忆 | Decision Memory | 组织记忆中专门记录"决策与理由"的子系统 | 同上 |
| 升格 / 转正 | Promotion / Publish / Accept | 从草稿状态升为正式状态（active / accepted） | `metadata_registry.yaml` §11 |
| 作废 / 被取代 | Superseded | 被新文档或新决策取代，原文保留作为历史 | `metadata_registry.yaml` §6.2 |
| 只追加不删改 | Append-only | 只允许新增，不允许修改或删除已有记录 | 同上 |
