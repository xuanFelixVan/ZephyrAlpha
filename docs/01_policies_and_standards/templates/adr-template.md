---
module_id: ""
title: ""
doc_type: adr
status: draft
version: "0.1.0"
layer: cross_layer
owner: ZephyrAlpha-Owner
classification: confidential
language: zh
created_by: human_plus_agent
date: ""
ttl: permanent
summary: ""
tags: []
rule_form: declarative
scope: global
stability: evolving
verifiability: manual
depends_on: []
---

# {标题}

> module_id: {填写} | version: 0.1.0 | status: draft | date: {YYYY-MM-DD} | deciders: {决策者}
>
> 本文档为 ADR（Architecture Decision Record），遵循 Michael Nygard 原始格式（5 段极轻结构）。
> 按 PS-STD-002 v3.2.0，ADR 归入 L3 基础模板——信息性决策记录，不要求 L2 治理章。

---

## 1. 目的与范围

### 1.1 目的

<!-- 填写：这个 ADR 记录什么决策？为什么需要记录？ -->

### 1.2 上下文（Context）

<!-- 描述当时的技术现状、业务约束、为什么需要做这个决策。1~3 段即可。 -->
{填写}

### 1.3 责任范围（本文档管什么）

<!-- 填写：本文档记录 {模块} 的 {决策名称} 决策及其理由、后果、否决方案 -->

### 1.4 责任边界（本文档不管什么）

<!-- 填写：本文档仅记录决策——不涉及具体实施步骤（蓝图和施工图负责） -->
- 具体实施步骤 → 以蓝图和施工图为准

---

## 2. 主体内容

### 2.1 决策（Decision）

<!-- 我们决定怎么做。一句话总结，然后展开细节。 -->
{填写}

### 2.2 理由（Rationale）

<!-- 为什么选择这个方案而不是其他方案。引用专业框架/数据/实验来支持。 -->
{填写}

### 2.3 后果（Consequences）

<!-- 采纳这个决策后，会产生什么正面和负面影响？哪些事情变容易了，哪些变难了？ -->
{填写}

### 2.4 否决方案（Alternatives Considered）

<!-- 记录了哪些方案被否决以及否决原因。AI 读到此处能理解"为什么不能选B"。 -->

## 3. AI 自治权限标注

<!-- 填写：AI 对本 ADR 的操作权限。ADR 是已做出的决策记录，通常 human_gated——AI 可以补充内容，但不应推翻决策。 -->

| 操作 | AI 自治权限 | 说明 |
|------|:---:|------|
| 补充否决方案/后果 | ai_editable | AI 可自主补充分析细节 |
| 修正错别字/格式 | ai_editable | AI 可自主修正 |
| 修改决策内容 | human_gated | 推翻已做出的决策需 Owner 审批 |
| 修改理由 | human_gated | 决策理由不可事后篡改 |

## 4. TTL 与生命周期

<!-- 填写：ADR 通常是 permanent（决策记录应长期保留），即使被新的 ADR 取代也保留原记录。 -->

| 字段 | 值 |
|------|-----|
| TTL | permanent |
| 状态流转 | draft → active → deprecated（被新 ADR 取代 → 保留原记录，superseded_by 指向新 ADR） |
| 审查周期 | 决策生效后审查一次，后续按需 |
| 最后审查日期 | {YYYY-MM-DD} |

## 5. 变更记录

| 日期 | 版本 | 变更内容 |
|------|------|---------|
| {YYYY-MM-DD} | 0.1.0 | 初始版本
