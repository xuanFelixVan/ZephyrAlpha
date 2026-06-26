---
module_id: KE-3597
title: 5. DOC 域（文档治理规则）
category: governance_rule
ttl: permanent
---

# 5. DOC 域（文档治理规则）

5. DOC 域（文档治理规则）

> 来源：`01_policies_and_standards/governance/document/`

| 登记号 | 规则内容 | 对应 COND | 强制方式 | 来源路径 |
|--------|---------|----------|---------|---------|
| DOC-001 | 文件名禁止使用大写字母（历史遗留白名单除外） | COND-01 | doc | `governance/document/trae_028_doc_structure_naming.yaml` |
| DOC-002 | 文件名禁止使用版本号后缀 | COND-02 | doc | `governance/document/trae_028_doc_structure_naming.yaml` |
| DOC-003 | 文件名禁止使用日期后缀（LATEST 文件除外） | COND-03 | doc | `governance/document/trae_028_doc_structure_naming.yaml` |
| DOC-004 | 文件名禁止使用空格和特殊字符 | COND-04 | doc | `governance/document/trae_028_doc_structure_naming.yaml` |
| DOC-005 | L3 文档禁止使用 MUST/SHOULD | COND-05 | doc | `meta/document_structure_standard.yaml` |
| DOC-006 | L2 文档禁止使用 MUST | COND-06 | doc | `meta/document_structure_standard.yaml` |
| DOC-007 | B 轨禁止反向依赖 C 轨 | COND-07 | doc | `governance/document/trae_028_doc_structure_naming.yaml` |
| DOC-008 | C 轨内部禁止反向依赖 | COND-08 | doc | `governance/document/trae_028_doc_structure_naming.yaml` |
| DOC-009 | 永久豁免禁止 | COND-14 | doc | `meta/document_structure_standard.yaml` |
| DOC-010 | 禁止跳过 Step 2-4 直接删除 Active 标准 | COND-15 | doc | `meta/document_structure_standard.yaml` |
| DOC-011 | 修改规则后禁止不更新 Session Log | COND-16 | doc | `meta/rule_lifecycle_and_change_standard.yaml` |
| DOC-012 | 修改规则后禁止不更新文件版本号 | COND-17 | doc | `meta/rule_lifecycle_and_change_standard.yaml` |
| DOC-013 | 禁止使用未加密方式传输密钥 | COND-18 | doc | `meta/behavior_boundaries_standard.yaml` |
| DOC-014 | 禁止共享或复用凭证 | COND-19 | doc | `meta/behavior_boundaries_standard.yaml` |
| DOC-015 | 审计日志未启用时禁止执行关键操作 | ABS-45 | doc | `meta/behavior_boundaries_standard.yaml` |
| DOC-016 | 审计日志禁止出现间断 | COND-50 | doc | `meta/behavior_boundaries_standard.yaml` |
| DOC-017 | 禁止未记录的配置变更 | COND-21 | doc | `meta/behavior_boundaries_standard.yaml` |
| DOC-018 | AI 在高风险决策中禁止不提供决策理由 | COND-23 | doc | `meta/behavior_boundaries_standard.yaml` |
| DOC-019 | AI 禁止隐藏其行为的不确定性/置信度 | COND-24 | doc | `meta/behavior_boundaries_standard.yaml` |
| DOC-020 | AI 禁止在未声明的情况下使用外部工具/API | COND-25 | doc | `meta/behavior_boundaries_standard.yaml` |
| DOC-021 | 禁止部署未经测试的代码到生产环境 | ABS-46 | doc | `meta/behavior_boundaries_standard.yaml` |
| DOC-022 | 禁止在无回滚方案的情况下部署 | COND-52 | doc | `meta/behavior_boundaries_standard.yaml` |
| DOC-023 | 禁止绕过 kill switch / 紧急停止机制 | ABS-47 | doc | `meta/behavior_boundaries_standard.yaml` |
| DOC-024 | AI 禁止访问超出当前任务所需的文件/系统 | ABS-48 | doc | `meta/behavior_boundaries_standard.yaml` |
| DOC-025 | contracts 目录禁止放业务逻辑 | COND-32 | doc | `src/zephyr/shared/contracts/__init__.py` |

---
