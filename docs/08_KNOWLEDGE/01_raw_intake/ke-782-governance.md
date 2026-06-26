---
module_id: KE-705
title: 一.1.4 防幻觉完整路径映射表
category: governance
ttl: permanent
---

# 一.1.4 防幻觉完整路径映射表

一.1.4 防幻觉完整路径映射表

> AI 新建目录时，查这张表确定命名风格。

| 目录层级 | 命名风格 | 完整路径示例 | 理由 |
|---------|---------|------------|------|
| `docs/` 顶级目录 | 数字编号+单词 | `01_policies_and_standards/` | 已有规范（trae_028_doc_structure_naming.yaml §二） |
| `governance/` 子目录 | 单词 | `governance/security/` | 语义单一，一个词就够了 |
| `operational/` 子目录 | 单词 或 snake_case | `operational/devops/` 或 `operational/vibe_coding/` | 一个词够就用单词；不够就用 snake_case |
| `domains/` 子目录 | L{XX}_snake_case | `domains/L00_data_source/` | 对应架构层，必须带层编号 |
| `domains/L{XX}_*/` 子目录 | 单词 | `domains/L00_data_source/governance/` | governance/operational 是固定词 |
| `_registry/` 子目录 | 单词 | `_registry/contracts/` | 语义单一 |
| `meta/` | 无子目录 | — | 固定不增长 |
| `templates/` | 无子目录 | — | 固定不增长 |
