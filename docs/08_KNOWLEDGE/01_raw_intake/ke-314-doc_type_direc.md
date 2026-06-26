---
module_id: KE-314
title: 3.4.1 防幻觉三向映射（doc_type → directory → rule_form）
category: documentation
ttl: permanent
---

# 3.4.1 防幻觉三向映射（doc_type → directory → rule_form）

3.4.1 防幻觉三向映射（doc_type → directory → rule_form）

> AI 判断"这个文件该放哪、该是什么格式"时，查这张表。三个维度**一一对应**，不允许交叉。

| doc_type | 唯一目录 | rule_form | 反向验证 |
|----------|---------|-----------|---------|
| `policy` | `governance/` | 声明式 | governance/ 下只能是 policy / standard / protocol |
| `standard` | `governance/` | 声明式 | 同上 |
| `protocol` | `governance/` | 声明式 | 同上 |
| `operational_rule` | `operational/` | 过程式 | operational/ 下只能是 operational_rule |
| `register` | `_registry/` | 数据 | _registry/ 下只能是 register |
| `template` | `templates/` | 结构 | templates/ 下模板文件的 doc_type 取目标文档类型。"template"作为 doc_type 仅用于"模板的模板"（如本目录结构模板本身）；cookbook template（用于生成目标文档的预填骨架）其 doc_type = 目标类型（如 blueprint-construction-template.md 的 doc_type: blueprint）。对标：K8s Helm template 不改 kind 为 Template，ITIL 模板不改标题加 "Template" 前缀。 |
