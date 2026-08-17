---
module_id: GOV-005
title: 登记表体系目录索引
doc_type: index
status: Active
version: "3.2.0"
date: "2026-08-17"
summary: "_registry/ 目录导航。v3.2.0：AI-17 审计治本——子目录文件数实测更正（catalogs 26→67、contracts 4→6、vocabularies 30→40、schemas 3 不变），合计 63→116。"
tags: [index, registry, navigation]
rule_form: declarative
scope: global
stability: stable
verifiability: manual
ttl: permanent
---

# _Registry — 登记表体系目录索引

## 责任声明（Single Responsibility）

本目录是 ZephyrAlpha 项目**登记表体系的物理根目录**。所有 YAML 格式的登记表/注册表/清单、验证契约、受控词表、JSON Schema 均在此目录或其子目录下集中管理。

> **v3.2.0 更新（2026-08-17，AI-17 审计实测）**：各子目录文件数——`catalogs/` **67**（64 登记表 YAML + `_index.yaml` + `index.md` + `_archive/` 1）、`contracts/` **6**（5 契约 + index.md）、`vocabularies/` **40**（39 词表 + index.md）、`schemas/` **3**（2 Schema + index.md）（合计 **116**）；若**排除**四个子目录各自 `index.md` 后合计 **112** 个体系数据文件。

## 子目录结构

| 子目录 | 用途 | 文件数 | 索引 |
|--------|------|:---:|------|
| [`catalogs/`](catalogs/index.md) | 登记表集中存储——YAML/MD 格式的注册表/清单 | 67 | index.md |
| [`contracts/`](contracts/index.md) | 验证契约——pre-commit/CI 消费的 YAML 契约规则 | 6 | index.md |
| [`vocabularies/`](vocabularies/index.md) | 受控词表——doc_type/status/rule_form/ttl/layer 等 **39** 个词表 + index | 40 | index.md |
| [`schemas/`](schemas/index.md) | Schema——JSON/YAML 结构校验定义 | 3 | index.md |

## 快速入口

- **找登记表** → [catalogs/registry_master_index.yaml](../_registry/catalogs/registry_master_index.yaml)（总索引）
- **验证登记表真实性** → `python scripts/governance/validate_blueprint_registry.py`
- **一键全维度扫描** → `python scripts/governance/run_all.py`

## 排除规则（不应放入本目录的内容）

- ❌ .md 治理文档 → `docs/02_enterprise_architecture/`（知识条目走 KB 知识库/KE 管线，docs/08_knowledge/ 已退役）
- ❌ 架构模型 YAML → `architecture_model/`
- ❌ 运行时配置 YAML → `config/` 或 `src/zephyr/`
- ❌ Python 脚本中的注册表（如 SCRIPT_REGISTRY 代码嵌入）→ beta 后统一提取至 catalogs/

## 父级目录

- 父级：[01_policies_and_standards](../index.md)
