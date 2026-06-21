---
module_id: KE-1004
status: active
title: 7.1 审计流程（四步法）
category: governance_rule
---

# 7.1 审计流程（四步法）

7.1 审计流程（四步法）

```
Step 1：字段扫描（自动化，对应 V1~V2）
    └── 遍历所有文件 frontmatter → 检查 doc_type 是否在受控词表中
    └── 检查 doc_type 是否匹配所在目录的合法值（如 governance/ 下不能有 operational_rule）
    └── 检查文件名后缀是否匹配 doc_type（§一.0 强制映射表）
    └── 产出："字段违规清单"

Step 2：内容读取（人工/AI 深度审查，对应 V5）
    └── 对 Step 1 通过的文件，逐文件打开并阅读正文内容
    └── 判断标准：
        ├── 声明式规则（policy/standard/protocol）→ 正文应是"什么必须/禁止/推荐"，不是"怎么做"
        ├── 过程式规则（operational_rule）→ 正文应是"Step 1→N 操作步骤"，不是声明式禁令
        ├── 注册表（register）→ 正文应是结构化数据清单，不是叙事散文
        └── 索引入口（index）→ 正文应只是目录导航，不含规则文本
    └── 产出："内容-标签不一致清单"

Step 3：交叉验证
    └── 对照 trae_028_doc_structure_naming.yaml 的反向映射表——确认每种内容类型是否在正确的目录
    └── 对照 module_id 命名空间——确认前缀是否匹配目录
    └── 对照 depends_on 引用链——确认引用的文件是否存在且 doc_type 一致
    └── 产出："跨文件一致性清单"

Step 4：判定与修复
    └── 对每个不一致项做出判定：
        ├── 放错目录 → 搬迁到正确目录（见 trae_028_doc_structure_naming.yaml §5.1.2 反向映射表）
        ├── doc_type 写错 → 修改 frontmatter doc_type 为正确值
        ├── 文件名误导 → 按 §一.0 强制映射表改名
        └── 内容根本不是规则 → 搬出 01_policies_and_standards/，放到正确位置
    └── 产出："修复操作清单" + "修复后验证"
```
