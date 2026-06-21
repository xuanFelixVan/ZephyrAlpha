---
module_id: ""
title: ""
doc_type: register
status: Draft
version: "0.1.0"
layer: cross_layer
owner: ZephyrAlpha-Owner
classification: confidential
language: zh
created_by: human_plus_agent
date: ""
ttl: permanent
summary: "注册表文档创建模板——结构化数据清单，新建 register 类文档时使用此模板"
completeness: "unknown"
template_for: register
tags: []
rule_form: data
scope: global
stability: evolving
verifiability: manual
depends_on: []
---

<!--
COMPLIANCE_CHECKLIST — 机器可解析合规清单
注册表文档模板 MUST 包含以下所有标题（精确匹配关键词）。缺一 = 不合规。
脚本：python scripts/governance/d3_metadata/check_template_compliance.py <文档路径> --template register
-->
<!--
REQUIRED_SECTIONS:
  s1: "1. 目的与范围"
  s2: "2. 使用说明"
  s3: "3. 注册条目"
  s4: "4. 条目 schema"
  s5: "5. AI 自治权限标注"
  s6: "6. TTL 与生命周期"
  s7: "7. 变更记录"
END_REQUIRED_SECTIONS
-->

# {注册表名称}

> module_id: {填写} | version: 0.1.0 | status: draft | layer: cross_layer

---

## 1. 目的与范围

### 1.1 注册表元数据

<!-- 填写：此注册表是给谁用的——AI 导航还是人工审计？ -->

| 字段 | 值 |
|------|-----|
| 注册表用途 | {描述此注册表追踪什么} |
| 使用对象 | {AI Agent / 人类 Owner / 两者} |
| 条目类型 | {此注册表收录条目的 doc_type 或类别} |
| 条目生命周期 | {条目的状态机：proposed → active → deprecated} |
| 条目准入条件 | {什么条件下允许新增条目} |
| 维护方式 | {手动 / 自动生成（脚本名：xxx.py）} |
| 唯一键 | {每个条目的唯一标识字段：如 module_id、entry_id} |

### 1.2 责任范围（本文档管什么）

<!-- 填写：正向声明——此注册表追踪什么、覆盖什么范围 -->

- {覆盖的条目范围}

### 1.3 责任边界（本文档不管什么）

<!-- 填写：负向声明——此注册表明确不收录什么类型的条目、以哪个文件为准 -->

- {排除的条目类型 → 以哪个注册表为准}

---

## 2. 使用说明

<!-- 填写：什么场景下应该查这个注册表？什么决策应该参考它？ -->

{例如：AI 创建新模块前，须查此注册表确认所有 module_id 不冲突。}

---

## 3. 注册条目

<!-- 一个条目一行。条目数是注册表的价值指标，不是一次性填满的——按需逐步加入。 -->

| ID | 类型 | 名称 | 状态 | 说明 |
|----|------|------|------|------|
| {ID-001} | {类型} | {名称} | active | {说明} |

---

## 4. 条目 schema

```yaml
# 每个注册条目的 YAML schema
- id: ""
  type: ""
  name: ""
  status: active
  description: ""
  depends_on: []
```

---

## 5. AI 自治权限标注

<!-- 填写：AI 对本注册表的操作权限。注册表类文档通常 ai_editable——AI 可自主新增/修改条目。 -->

| 操作 | AI 自治权限 | 说明 |
|------|:---:|------|
| 新增条目 | ai_editable | AI 可自主新增注册条目 |
| 修改条目 | ai_editable | AI 可自主修改条目内容 |
| 删除条目 | human_gated | 删除需 Owner 确认——可能被其他文件引用 |
| 修改 schema | human_gated | Schema 变更影响所有消费者 |

## 6. TTL 与生命周期

<!-- 填写：注册表通常是 permanent（长期维护）。 -->

| 字段 | 值 |
|------|-----|
| TTL | permanent |
| 审查周期 | 每 90 天 |
| 过期处理 | 如被新注册表取代，按废弃流程标记 deprecated |
| 最后审查日期 | {YYYY-MM-DD} |

## 7. 变更记录

| 日期 | 版本 | 变更内容 |
|------|------|---------|
| {YYYY-MM-DD} | 0.1.0 | 初始版本 |
