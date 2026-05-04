---
module_id: REG-IDX-001
title: 登记表体系目录索引
doc_type: index
status: active
version: "2.1.0"
layer: cross_layer
owner: ZephyrAlpha-Owner
classification: confidential
language: zh
created_by: human_plus_agent
date: "2026-05-04"
summary: "_registry/ 目录的导航入口。登记表体系的物理根目录——包含 catalogs/ contracts/ vocabularies/ schemas/ 四个子目录共 35 个体系文件（不含 4 个 index.md）。详见 PS-REG-005 registry-master-index.yaml。v3.0.1：计数全面对账。"
tags: [index, registry, navigation]
rule_form: declarative
scope: global
stability: stable
verifiability: manual
---

# _Registry — 登记表体系目录索引

## 责任声明（Single Responsibility）

本目录是 ZephyrAlpha 项目**登记表体系的物理根目录**。所有 YAML 格式的登记表/注册表/清单、验证契约、受控词表、JSON Schema 均在此目录或其子目录下集中管理。

> **v3.0.1 更新（2026-05-04 审计修复）**：现包含 20 个 catalogs/ 登记表 + 2 个 contracts/ + 11 个 vocabularies/ + 2 个 schemas/
> = 共 35 个体系文件（不含索引文件）。详见 PS-REG-005 registry-master-index.yaml。

## 子目录结构

| 子目录 | 用途 | 文件数 | 索引 |
|--------|------|:---:|------|
| [`catalogs/`](../_registry/catalogs/index.md) | 登记表集中存储——YAML/MD 格式的注册表/清单 | 20 | index.md |
| [`contracts/`](../_registry/contracts/) | 验证契约——pre-commit/CI 消费的 YAML 契约规则 | 2 | index.md |
| [`vocabularies/`](../_registry/vocabularies/) | 受控词表——doc_type/status/rule_form/ttl/layer 等 11 个词表 | 11 | index.md |
| [`schemas/`](../_registry/schemas/) | Schema——JSON/YAML 结构校验定义 | 2 | index.md |

## 快速入口

- **找登记表** → [catalogs/registry-master-index.yaml](../_registry/catalogs/registry-master-index.yaml)（总索引）
- **验证登记表真实性** → `python scripts/governance/validate_blueprint_registry.py`
- **一键全维度扫描** → `python scripts/governance/run_all.py`

## 排除规则（不应放入本目录的内容）

- ❌ .md 治理文档 → `01_policies_and_standards/governance/` 或 `operational/`
- ❌ 架构模型 YAML → `02_enterprise_architecture/target-architecture/architecture-model/`
- ❌ 运行时配置 YAML → `config/` 或 `src/zephyr/`
- ❌ Python 脚本中的注册表（如 SCRIPT_REGISTRY 代码嵌入）→ beta 后统一提取至 catalogs/

## 父级目录

- 父级：[01_policies_and_standards](../index.md)
