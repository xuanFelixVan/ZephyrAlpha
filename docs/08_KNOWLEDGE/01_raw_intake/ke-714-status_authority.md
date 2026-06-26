---
module_id: KE-639
status: active
title: 二、状态字段权威 (Status Authority) — 文档生命周期状态
category: documentation
ttl: permanent
---

# 二、状态字段权威 (Status Authority) — 文档生命周期状态

二、状态字段权威 (Status Authority) — 文档生命周期状态

> ⚠️ **scope 声明**：本节定义的是【文档生命周期状态】（Markdown/YAML 文件的 frontmatter 元数据），适用于 `docs/` 下所有文档。
> 这与 `architecture_model/layers/schema.yaml` 定义的【代码模块实现状态】（planned/candidate/approved/in_development/active/completed/deprecated）
> 是两套完全不同的枚举。字段名都叫 `status`，但适用对象不同——混淆会导致 CI 误报或不报。
> 判断标准：看你读的文件是"文档本身"还是"描述代码模块的数据条目"。前者用本节枚举，后者用 `_schema.yaml`。

**权威来源**：`docs/01_policies_and_standards/` 目录下各 standard 文件（status 枚举由各标准文档自带分散定义；Stage J 建议合并至单独 `status-lifecycle-standard.md`）

| 状态值       | 含义                          | 允许场景         |
|-------------|-------------------------------|----------------|
| Draft       | 草稿，未经审核                  | 施工前期         |
| Review      | 审核中                        | 等待 Owner 批准  |
| Active      | 已批准并生效                   | 正式使用         |
| Superseded  | 已被更新版本替代                | 保留历史         |
| Deprecated  | 废弃，不应引用                  | 淘汰中           |
| Retired     | 已归档，不再维护                | 历史存档         |
| proposed    | 提议阶段（注册表专用）           | 注册表           |
