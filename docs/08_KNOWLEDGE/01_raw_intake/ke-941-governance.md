---
module_id: KE-863----2-003
status: active
title: 3.3 路径 2：注册表查询 [次选]
category: governance
ttl: permanent
---

# 3.3 路径 2：注册表查询 [次选]

3.3 路径 2：注册表查询 [次选]

**注册表文件**：

| 注册表 | 路径 | 覆盖范围 |
|--------|------|---------|
| 文档元数据索引 | `_registry/catalogs/document-metadata-index-registry.yaml` | 所有 governance/ + meta/ 下的规则文件 |
| 文档清单 | `_registry/catalogs/document-metadata-index-registry.yaml` | 所有文档文件的 inventory（auto-generated，取代已废弃的 master-document-inventory-registry.md） |
| 规则注册表 | PS-REG-001 `_registry/catalogs/_index.yaml` | 所有规则的索引 |

**操作流程**：

```
1. 根据目标文件的 module_id 前缀判断注册表
   └── PS-STD-XXX → meta/ 注册表
   └── GOV-XXX-XXX → governance/ 注册表
   └── DOM-LXX-XXX → domains/ 注册表
   └── OPS-XXX-XXX → operational/ 注册表
2. 打开对应注册表 → 搜索 module_id
   └── 找到 → 获取完整路径 → 读取文件
3. 如果注册表中未找到
   └── 该文件可能：（a）尚未注册 （b）已废弃 （c）不存在 → 进入路径 3
```

**适用场景**：
- 知道文件 module_id 但不知道路径（如 GREP 结果中引用了 GOV-DOC-010）
- index.md 中没有该文件的条目（新文件尚未更新到 index）
- 批量验证某个目录下应有哪些文件
