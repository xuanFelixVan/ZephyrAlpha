---
module_id: GOV-039
doc_type: index
status: Active
version: 1.0.0
generated: '2026-05-02'
depends_on:
- target: EA-ARCH-MODEL-INDEX
  at: §文件清单
  why: 父级 architecture_model 索引——cross_cutting 为其子目录，引用父级文件清单
title: Cross Cutting
ttl: permanent
---

# Cross Cutting — 目录索引

## 责任声明（Single Responsibility）

本目录只存放：**横切关注点 YAML — 能力热力图、运行时不变量、运行时平面**。

## 文件清单

| 文件 | 说明 |
|------|------|
| capability_heatmap.yaml | YAML 结构定义 |
| invariants.yaml | YAML 结构定义 |
| runtime_planes.yaml | YAML 结构定义 |

## 排除规则（不应放入本目录的内容）

- ❌ 层定义 YAML → `02_enterprise_architecture/target_architecture/architecture_model/layers/`

## 父级目录

- 父级：[architecture_model](../index.md)
