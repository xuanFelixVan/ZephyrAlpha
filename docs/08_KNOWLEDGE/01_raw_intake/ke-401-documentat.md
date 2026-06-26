---
module_id: KE-365
status: active
title: 4.5.5 否决方案
category: documentation
ttl: permanent
doc_type: knowledge_entry
---

# 4.5.5 否决方案

4.5.5 否决方案

| 方案 | 否决理由 |
|------|---------|
| `.md` 首字母大写 + `.yaml` 小写（旧规则） | 两套规则增加认知负担；AI 容易写错；宪法文件自身都写成了小写，说明规则不可执行 |
| Title Case（OpenSSF 方案） | 为人类视觉优化，不为 AI 优化；AI 严格区分大小写，Title Case 反而增加出错概率 |
| PascalCase（Open Data Fabric 方案） | 多词值可读性差（`NotApplicable`）；AI 需要额外映射逻辑 |
| 全部统一大写 | 枚举值大写（`STATUS: ACTIVE`）增加 AI 出错概率；跟文件名小写规则冲突；无专业机构先例 |
| 全部统一小写（包括标识符） | 标识符小写（`l00-ds-001`）跟文件路径混淆；AI 无法快速区分"这是编号还是路径"；跟 Stage F 正交性裁定矛盾 |

> TaskStatus 和 KeStatus 在代码中全大写（`PENDING` / `COMPLETED` / `DRAFT` / `INDEXED` 等），
> 这是 Python 枚举的惯例，与 frontmatter 枚举值无关——它们是域 B/C 专用，不在 frontmatter 中使用。
> pre-commit 校验时，域 A 枚举值只接受小写，标识符只接受大写。
