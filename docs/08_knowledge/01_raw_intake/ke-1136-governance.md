---
module_id: KE-1051
title: A.1 脚本覆盖交叉验证
category: governance
ttl: permanent
doc_type: knowledge_entry
---

# A.1 脚本覆盖交叉验证

A.1 脚本覆盖交叉验证

本协议 v1.1.0 与 `scripts/governance/script-manifest.yaml`（177 条脚本记录）进行了完整交叉验证：

| 验证项 | 结果 |
|--------|------|
| manifest 中每条脚本是否在 §2 中有引用 | ✅ 177/177 全覆盖 |
| 协议中引用的脚本路径是否在 manifest 中存在 | ✅ 全部验证通过 |
| P0/P1/P2 优先级是否与 manifest 一致 | ✅ 一致 |
| 跨维度脚本是否在多个维度中重复列出 | ✅ 正确标注"跨维" |
