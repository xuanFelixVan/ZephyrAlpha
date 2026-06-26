---
module_id: KE-2154-------mod-k-000
title: 3.8 Knowledge Base 集成（对接 MOD-KB-001）
category: module_blueprint
ttl: permanent
---

# 3.8 Knowledge Base 集成（对接 MOD-KB-001）

3.8 Knowledge Base 集成（对接 MOD-KB-001）

| 方向 | 触发条件 | 操作 |
|------|---------|------|
| Skill → KB | Skill 执行中发现新的代码模式/bug 模式 | 自动生成 KE 草稿（status=draft）→ 人工审查 → 发布 |
| KB → Skill | 一条 KE 被反复引用（≥5 次）且包含可执行步骤 | 人工审查 → 升级为 Skill 指令的一部分 |
| 双向同步 | Skill 的 freshness_score 下降 | 关联的 KE 也被标记为"待验证" |

---
