---
module_id: KE-583
title: D-SSOT：SSOT 权威源映射
category: documentation
ttl: permanent
doc_type: knowledge_entry
---

# D-SSOT：SSOT 权威源映射

D-SSOT：SSOT 权威源映射

| 检查项 | 结果 | 说明 |
|--------|:----:|------|
| ssot-authority-map.md 准确性 | ✅ | 每个概念的唯一权威源指向正确 |
| 双树主从关系 | ✅ | `architecture_model/` 为主源，`docs/02/.../architecture_model/` 为副本（revision-history v2.2.0 已声明） |
| 模块 ID 一致性 | ✅ | module_id_registry.yaml 与施工树 layers/*.yaml 中的 module_id 一致 |

**结论**：SSOT 映射无问题。`ssot-authority-map.md` v2.3.0 已移除历史误标，矛盾追踪拆分活跃/已解决，状态健康。

---
