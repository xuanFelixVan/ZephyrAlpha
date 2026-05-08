---
module_id: KE-documentat-8_1-001
title: 8.1 根因分析
category: documentation
---

# 8.1 根因分析

8.1 根因分析

| 根因 | 表现 | 影响的审计维度 |
|------|------|--------------|
| **批量创建时缺少 frontmatter 格式校验** | 28 个文件 `ttl: permanent---` 粘连 | Frontmatter 分隔符 |
| **status 字段大小写无自动校验** | 48 个文件使用小写 `active` | Frontmatter status |
| **B 轨代码先于架构模型开发** | 14 个 B 轨目录无 YAML 定义 | 架构图对齐 |
| **老树迁移时编码损坏未完全修复** | 3 个蓝图文件 BOM/乱码 | Frontmatter 编码 |
| **Stage G 修复范围未覆盖 archive/** | 1 个 archive 文件命名违规 | 文件命名 |
| **蓝图 layer 字段历史误标未纠正** | 8 个蓝图 layer 与目录不一致 | SSoT 一致性 |
