---
module_id: KE-governance-unknown-001
title: 四、归档流程
category: governance
---

# 四、归档流程

四、归档流程

当文档需要归档（保留历史但不再活跃使用）时：

```
1. 将文件移动到对应的 archive/ 子目录
   - 审计报告 → 09_audit/archive/
   - 架构文档 → 02_enterprise_architecture/archive/
2. 更新文件 frontmatter：status: deprecated，ttl: 30d
3. 更新所有引用该文件的链接（或移除引用）
4. 重新生成 document-metadata-index.yaml
5. 在同一 commit 中完成以上所有操作
```
