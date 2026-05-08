---
module_id: KE-documentat-1_4_ssot-003
title: 1.4 SSoT 声明
category: documentation
---

# 1.4 SSoT 声明

1.4 SSoT 声明

| 内容 | 真源 | 非真源 |
|------|------|--------|
| doc_type 受控词表 | **doc_type-vocabulary.yaml**（canonical SSoT） | 本文件 §3（速查引用）、frontmatter-standard.md v1.0.0（已废弃） |
| 域 A 字段定义（文档 frontmatter） | **frontmatter-field-registry.yaml**（canonical SSoT） | 本文件 §2（字段规范/校验逻辑，非字段数据定义）、frontmatter-schema.json（自动生成产物） |
| 域 B 字段定义（任务卡） | **本文件 §7** | task-card-standard.md（字段定义以本注册表为准，该文件保留业务规则） |
| 域 C 字段定义（AI 治理） | **本文件 §8** | ai-autonomous-company-endgame-design.md（设计文档，字段定义以本注册表为准） |
| 受控枚举定义（category / domain / namespace / AgentRole） | **本文件 §9.1~§9.4** | — |
| 受控枚举定义（layer / source_type / priority） | **本文件 §9.5~§9.7** | triage.py VALID_LAYERS（需对齐）、kms-entry-schema.md source_type（需对齐）、**`src/zephyr/shared/schemas.py`** 中 AuditSeverity→Priority 演进（需随版本对齐） |
| module_id 命名规范 | **本文件 §5** | unified-numbering-standard.md（层编号部分仍有效，模块 ID 格式以本文件为准） |
| 状态语义 | **status-vocabulary.yaml**（canonical SSoT） | 本文件 §4（规范解释） |
| rule_form 映射 | **rule_form-vocabulary.yaml**（canonical SSoT） | 本文件 §2.6（一致性约束） |
| ttl 枚举 | **ttl-vocabulary.yaml**（canonical SSoT） | 本文件 §6（规范解释） |

**任何与本文件冲突的定义，以本文件为准。** 发现冲突时，应提决策记录（参见 MOD-KB-001 §3.9.5 三层决策记录模型）并修正冲突方。
