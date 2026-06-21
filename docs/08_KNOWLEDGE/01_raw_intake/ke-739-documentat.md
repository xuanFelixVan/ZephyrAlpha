---
module_id: KE-663
status: active
title: ZephyrAlpha 元数据登记表
category: documentation
---

# ZephyrAlpha 元数据登记表

ZephyrAlpha 元数据登记表

> **module_id**: PS-STD-001 | **version**: 5.7.0 | **status**: active
>
> 本注册表是 ZephyrAlpha **元数据标准**的唯一真源（Single Source of Truth）——
> 定义字段应该有什么属性、校验规则、分类体系。
> 覆盖三个域：文档 frontmatter（域 A）、任务卡（域 B）、AI 治理（域 C）。
> **字段的具体定义（字段名/类型/必填性/枚举值）以 PS-REG-012 [frontmatter-field-registry.md](../_registry/catalogs/frontmatter-field-registry.md) 为 canonical SSoT**
> （YAML 格式、字段级粒度、机器可校验——符合 AGENTS.md §6.9 YAML 优先原则）。
> 本文件管"规则"（字段应满足什么规范），PS-REG-012 管"数据"（每个字段具体是什么）。
> 所有工具、AI 员工、pre-commit 钩子、CI 流水线：**读字段定义 → 查 PS-REG-012；读字段规范/校验逻辑 → 查本文件**。
>
> 对标标准：ISO 11179（元数据登记表）、IETF Agent Audit Trail（AAT）、OpenLineage。

---

> ## ⚠️ 待解决问题（2 个）
>
> **任何修改本文件或使用 doc_type 的人/AI 必须知晓**：
>
> | # | 问题 | 严重度 | 状态 | 影响范围 |
> |---|------|:------:|------|---------|
> | 1 | ~~**旧 doc_type 长名未迁移**~~ | ~~🔴~~ | 📋 迁移方案已定 | 迁移方案见 §3.7，施工 beta 批量执行 |
> | 2 | **`internal` classification 值待迁移**：100 个文件标 `classification: internal`，已裁定删除 `internal` 改为 `confidential`，但尚未批量执行 | 🟡 | 待迁移 | 100 个 .md 文件 + 2 个 Python 文件 + 数据库 DDL |
>
> **处理原则**：问题 1 迁移方案已定义（§3.7），施工 beta 批量执行。问题 2 在后续 session 批量执行迁移。**在问题解决之前，不得新增使用旧长名或 `internal` 的文件。**
>
> > 拆分预判条件见 §6（文件末尾）👉 `metadata-registry.md#split-conditions`

---
