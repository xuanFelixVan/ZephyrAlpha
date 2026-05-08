---
module_id: KE-governance-3_2____1_index_md-003
title: 3.2 路径 1：index.md 全局入口 [首选]
category: governance
---

# 3.2 路径 1：index.md 全局入口 [首选]

3.2 路径 1：index.md 全局入口 [首选]

**入口文件**：`docs/01_policies_and_standards/index.md`

**操作流程**：

```
1. 读取 index.md
   └── 查看 docs/ 全目录树 → 判断目标文件所在的大目录
2. 进入对应子目录
   └── 查看该目录下的文件列表 → 精确匹配文件名
3. 读取目标文件
   └── 验证 frontmatter module_id 与预期一致
```

**适用场景**：
- 找已知类别的文件（如"文档命名规则"→ governance/document/ 下）
- 浏览某个目录下的所有文件
- 新 AI session 初始对齐

**一票否决**：如果 index.md 中明确标注某文件不存在/已废弃，则路径 2 和 3 不需要继续——文件确实不存在。
