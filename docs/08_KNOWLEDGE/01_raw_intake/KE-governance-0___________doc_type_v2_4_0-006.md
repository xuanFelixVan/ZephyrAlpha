---
module_id: KE-governance-0___________doc_type_v2_4_0-006
title: 一.0 文件名后缀必须匹配 doc_type（v2.4.0 新增）
category: governance
---

# 一.0 文件名后缀必须匹配 doc_type（v2.4.0 新增）

一.0 文件名后缀必须匹配 doc_type（v2.4.0 新增）

> **对标**：K8s well-known labels（label=value 强制匹配）+ OpenAPI discriminator（discriminator 字段决定 schema 类型，不允许模糊）。

在 `01_policies_and_standards/` 目录下，**文件名后缀必须反映 doc_type**。不允许文件名使用与 doc_type 矛盾的后缀——做到"看名字就知道这个文件是什么类型的规则"。

**doc_type → 文件名后缀强制映射表**：

| doc_type | 文件名格式 | 示例 | 说明 |
|----------|-----------|------|------|
| `policy` | `{subject}-policy.md` | `secret-management-policy.md` | 声明式"必须/禁止"规则 |
| `standard` | `{subject}-standard.md` | `file-naming-standard.md` | 技术标准/度量规范 |
| `protocol` | `{subject}-protocol.md` | `architecture-review-policy.md` | 多方交互规则 |
| `operational_rule` | `{subject}-runbook.md` / `-playbook.md` / `-procedure.md` / `-checklist.md` | `architecture-change-playbook.md` | 过程式操作步骤——以上四个后缀均可，均属操作范畴 |
| `register` | `{subject}-registry.md` / `-register.md` | `rule-registry.md` | 结构化数据清单 |
| `index` | `index.md`（固定） | `index.md` | 目录导航入口，不可改名 |
| `terminology` | 术语特定命名 | `glossary.md`、`terminology-mapping.md` | 术语定义文件 |
| `template` | `{target_doc_type}-template.md` | `policy-template.md`、`blueprint-template.md` | templates/ 下模板文件，doc_type 取目标类型 |

**禁止的行为**：

| 禁止 | 例子（违规 → 合规） | 原因 |
|------|------|------|
| 声明式规则用过程式后缀 | `governance-runbook.md` → `governance-protocol.md` | protocol 不能叫 runbook |
| 策略文件用操作后缀 | `security-incident-playbook.md` → `security-incident-response-policy.md` | policy 不能叫 playbook |
| 策略文件用手册后缀 | `document-discovery-runbook.md` → `document-discovery-policy.md` | policy 不能叫 runbook |

**历史修正（2026-05-02）**：上述 3 个违规文件名已于同日修正。此前 `doc_type-vocabulary.yaml` v1.1.0 允许"文件名描述业务场景、doc_type 定义文档结构，两者不需要一致"——该条款已废除，被本条强制映射替代。

**验证方式（GATE-11 新检测规则 N-08）**：pre-commit hook 逐文件检查"文件名后缀 vs frontmatter doc_type"，不一致则 V1 阻断。
