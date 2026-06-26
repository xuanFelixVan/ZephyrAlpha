---
module_id: GOV-038
doc_type: index
status: Active
version: 1.0.0
generated: '2026-05-02'
depends_on:
- target: EA-ARCH-MODEL-INDEX
  at: §文件清单
  why: 父级 architecture_model 索引——contracts 为其子目录，引用父级文件清单
title: Contracts
ttl: permanent
---

# Contracts — 目录索引

## 责任声明（Single Responsibility）

本目录只存放：**跨层契约 YAML**。

## 文件清单

| 文件 | 说明 |
|------|------|
| cross_layer_contracts.yaml | YAML 契约 |

## 排除规则（不应放入本目录的内容）

- ❌ 层定义 YAML → `02_enterprise_architecture/target_architecture/architecture_model/layers/`

## 父级目录

- 父级：[architecture_model](../index.md)
