---
module_id: PS-IDX-001
title: 规则体系总索引
doc_type: index
status: active
version: "2.1.0"
layer: cross_layer
owner: ZephyrAlpha-Owner
classification: confidential
language: zh
created_by: human_plus_agent
date: "2026-06-26"
ttl: permanent
summary: "01_policies_and_standards/ 的顶层导航入口。v2.1.0：P0 审查修复——§4.1 冷启动路径接入 trae_060 向内收三原则，目录树补全 058/059/060，修正规则计数 48→60。"
tags: [index, root, navigation, policies-and-standards]
rule_form: declarative
scope: global
stability: stable
verifiability: manual
---

# 规则体系总索引

> **module_id**: PS-IDX-001 | **version**: 2.0.0 | **status**: active

本文件是 `01_policies_and_standards/` 的顶层导航入口。**新 AI session 的第一站**——读完此文件即理解整个规则体系的全貌。

> **架构真源**：[architecture_upgrade_discussion.md](file:///D:/ZephyrAlpha/docs/02_enterprise_architecture/architecture_upgrade_discussion.md) §二（43域方案，14层降级为域属性）

---

## 一、目录结构速览

```
01_policies_and_standards/
├── rules/                       ← 规则文件唯一真源（60 个 trae_*.yaml）
│   ├── trae_001_file_operation_security.yaml       ← 文件操作安全（RULE-ZERO~FOUR）
│   ├── trae_002_anti_orphan_search_first.yaml      ← 搜索先行（RULE-EIGHT）
│   ├── trae_003_task_granularity_threshold.yaml    ← 任务粒度（RULE-SIX）
│   ├── trae_004_parallel_atomic_transaction.yaml   ← 并行原子事务（RULE-ONE）
│   ├── trae_005_modification_governance.yaml       ← 修改治理（RULE-SEVENTEEN）
│   ├── trae_006-009_anti_hallucination_*.yaml      ← 防幻觉四层（结构/行为/输出/安全）
│   ├── trae_010-012_code_*.yaml                    ← 代码命名/类型/测试
│   ├── trae_013-017_arch_*.yaml                    ← 架构治理（跨包/蓝图/路径/漂移/顺序）
│   ├── trae_018-023_behavior_*.yaml                ← 行为边界（禁止/条件）
│   ├── trae_024-027_methodology_*.yaml             ← 方法论（诊断/决策/质量/协作）
│   ├── trae_028-030_doc_*.yaml                     ← 文档（结构/操作/编号）
│   ├── trae_031_security_key_access.yaml           ← 安全密钥访问
│   ├── trae_032-033_module_*.yaml                  ← 模块生命周期/注册同步
│   ├── trae_034-035_task_*.yaml                    ← 任务卡标准/施工验证
│   ├── trae_036-039_arch_*.yaml                    ← 架构门控/版本/注入/幻觉检测
│   ├── trae_040_ai_model_routing.yaml              ← AI 模型路由
│   ├── trae_041-043_meta_rule_*.yaml               ← 元规则（分类/标准/元数据）
│   ├── trae_044_compliance_audit.yaml              ← 合规审计
│   ├── trae_045_data_quality_lineage.yaml          ← 数据质量血缘
│   ├── trae_046-047_engineering_*.yaml             ← 工程代码重构/文件头
│   ├── trae_048-049_ops_*.yaml                     ← 运维（Vibe Coding/域手册）
│   ├── trae_050-051_domain_policy_*.yaml           ← 域策略（因子/风险回测）
│   ├── trae_052_cross_blueprint_change_cleanup.yaml ← 跨蓝图变更清理
│   ├── trae_053_automation_dual_track.yaml         ← 自动化双轨
│   ├── trae_054_depgraph_access_protocol.yaml      ← 全景图访问协议
│   ├── trae_055_arch_domain_capacity.yaml          ← 架构域容量
│   ├── trae_056_module_creation_workflow.yaml      ← 模块创建工作流
│   ├── trae_057_ai_consumer_first.yaml             ← AI消费优先原则
│   ├── trae_058_depgraph_scan_exclusions.yaml      ← 全景图扫描排除
│   ├── trae_059_schema_version_write_protection.yaml ← schema_version写保护
│   └── trae_060_inward_consolidation.yaml          ← 向内收三原则（顶层统辖）
│
├── _registry/                   ← 注册表 + 验证契约（机器可读）
│   ├── catalogs/                ← 集中注册表（26 个 YAML/MD）
│   │   ├── registry_master_index.yaml             ← 注册表总索引（自动生成）
│   │   ├── gate_registry.yaml                      ← 门禁注册表
│   │   ├── functional_domain_registry.yaml         ← 功能域注册表（43域）
│   │   ├── frontmatter_field_registry.yaml         ← frontmatter 字段注册表
│   │   ├── rule_catalog_registry.yaml              ← 规则目录注册表
│   │   └── ...（其余 19 个 catalog 文件）
│   ├── contracts/               ← 架构合规契约
│   │   ├── architecture_contract.yaml              ← 架构合规自动验证契约
│   │   ├── contract_mapping_table.yaml             ← 契约映射表
│   │   └── model_capability_contract.yaml          ← 模型能力契约
│   ├── schemas/                 ← JSON Schema 定义
│   │   ├── frontmatter_schema.json                 ← frontmatter 字段校验 Schema
│   │   └── session_log_schema.yaml                 ← 会话日志 Schema
│   └── vocabularies/            ← 受控词表（29 个）
│       ├── glossary.yaml                           ← 术语表（仲裁源）
│       ├── terminology_mapping.yaml                ← 术语映射表
│       ├── doc_type_vocabulary.yaml                ← 文档类型受控枚举
│       ├── domain_vocabulary.yaml                  ← 域受控枚举
│       ├── layer_vocabulary.yaml                   ← 层级受控枚举
│       └── ...（其余 20 个 vocabulary 文件）
│
│
├── policies/                   ← 策略文件（3 个）
│   ├── parallel_session_coordination_policy.md     ← 并行 session 协调策略
│   ├── branch_strategy_policy.md                   ← 分支策略（单一主分支模型）
│   └── workspace_governance_policy.md              ← 工作区治理规则
│
└── templates/                   ← 文档模板（10 个标准模板，含 index.md）
    ├── blueprint_construction_template.md          ← 蓝图 + 施工指引统一模板
    ├── dependency_graph_template.md                ← 依赖图模板
    ├── playbook_runbook.md                         ← 操作手册模板
    ├── policy_template.md                          ← 策略模板（含已废弃 protocol 类型）
    ├── register_template.md                        ← 注册表模板
    ├── risk_register_template.md                   ← 风险登记表模板
    ├── roadmap_template.md                         ← 路线图模板
    ├── runbook_template.md                         ← 执行手册模板
    ├── standard_template.md                        ← 标准模板
    └── index.md
```

---

## 二、各子目录关键信息

| 子目录 | 职责 | 管辖文件数 | 索引入口 |
|--------|------|:---------:|---------|
| `rules/` | 规则文件唯一真源——60 个 trae_*.yaml（涵盖文件操作/防幻觉/架构/行为/方法论/文档/任务/运维/域策略） | 60 | [rule_catalog_registry.yaml](_registry/catalogs/rule_catalog_registry.yaml) |
| `_registry/` | 注册表+契约+Schema+词表——4 个子目录 | 56 | [_registry/index.md](_registry/index.md) |
| `templates/` | 文档模板——9 个标准模板 + index.md | 10 | [templates/index.md](templates/index.md) |

> **合计**：3 个子目录，115 个文件。
> **历史变更**：`meta/` 目录已于 2026-06 删除，规则文件合并至 `rules/`；`governance/`、`operational/`、`domains/` 目录已删除，内容合并至 `rules/` 对应 trae_*.yaml 文件。

---

## 三、本目录责任声明

### 3.1 责任范围（本目录管什么）

本目录是 ZephyrAlpha **规则体系**的唯一存放处，负责管理：

| 类别 | 存放位置 | 说明 |
|------|---------|------|
| **规则文件** | `rules/` | 60 个 trae_*.yaml——文件操作/防幻觉/架构/行为/方法论/文档/任务/运维/域策略 |
| **机器注册表** | `_registry/` | 自动索引、受控词表、验证契约、Schema |
| **文档模板** | `templates/` | 新建文件的起点 |

### 3.2 责任边界（本目录不管什么）

以下类型文件 **不在** 本目录管辖范围内：

| 文件类型 | 不在此目录的原因 | 正确位置 |
|---------|---------------|---------|
| 企业架构视图（TOGAF） | 架构模型不是规则 | `docs/02_enterprise_architecture/` |
| 架构决策记录（KB 决策记录） | 架构决策不是规则标准；凭证真源为 KB | **`KB:decisions`**（Git-backed） |
| 模块生命周期文档 | 蓝图+施工图+交付 | `docs/03_modules/` |
| 知识库条目 | 经验积累不是规则 | `docs/08_knowledge/` |
| 审计报告 | 事后评估不是规则 | `docs/_working/audit/` |
| 业务代码 | 可执行代码 | `src/zephyr/` |
| 治理/审计脚本 | 工具不是规则 | `scripts/governance/` / `scripts/audit/` |

### 3.3 规则分类体系

规则按 trae_XXX 编号分类，共 10 个工作线：

| 编号范围 | 工作线 | 说明 |
|---------|--------|------|
| trae_001-005 | 文件操作 + 任务粒度 | RULE-ZERO~EIGHT 施工铁律 |
| trae_006-009 | 防幻觉四层 | 结构/行为/输出/安全 |
| trae_010-012 | 代码构建 | 命名/类型/测试 |
| trae_013-017 | 架构治理 | 跨包/蓝图/路径/漂移/顺序 |
| trae_018-023 | 行为边界 | 绝对禁止/条件禁止 |
| trae_024-027 | 方法论 | 诊断/决策/质量/协作 |
| trae_028-030 | 文档治理 | 结构/操作/编号 |
| trae_031-035 | 安全+模块+任务 | 密钥/生命周期/注册/任务卡 |
| trae_036-039 | 架构门控+幻觉检测 | 门控/版本/注入/检测 |
| trae_040-060 | AI路由+元规则+运维+域策略+向内收 | 21 个规则文件（含 058 扫描排除/059 schema保护/060 向内收三原则） |

---

## 四、推荐阅读顺序

### 4.1 新 AI session 冷启动（所有任务通用）

```
1. 本文件（index.md）                              ← 3 分钟了解全貌
2. rules/trae_060_inward_consolidation.yaml        ← 向内收三原则（顶层统辖，必读真源）
3. _registry/catalogs/rule_catalog_registry.yaml   ← 规则索引全貌（自动生成）
4. _registry/vocabularies/glossary.yaml            ← 术语对齐
5. rules/trae_041_meta_rule_classification.yaml    ← 规则怎么分类
```

> **trae_060 接入说明**：本冷启动路径与 `.trae/rules/project_rules.md`「第二原则」均指向 `rules/trae_060_inward_consolidation.yaml` 真源，不复制内容（符合 trae_060 §2 唯一真源直读）。新 AI 经 IDE 入口或 docs 入口均能发现向内收三原则。

### 4.2 按任务类型定向阅读

| 你的任务 | 读完通用 4 步后，继续读 | Token 成本 |
|---------|----------------------|:---:|
| **修改/优化规则文件** | `rules/trae_032_module_lifecycle.yaml` | ~1500 |
| **创建新标准文档** | `rules/trae_030_doc_numbering_metadata.yaml` + `rules/trae_043_meta_rule_metadata.yaml` | ~2500 |
| **审查规则体系** | `rules/trae_044_compliance_audit.yaml` + `_registry/catalogs/registry_consistency_contract.yaml` | ~2000 |
| **操作具体文件夹** | 对应规则文件 | ~1000 |

---

## 五、关键注册表速查

| 注册表 | 路径 | 用途 |
|--------|------|------|
| **注册表之注册表** | [_registry/catalogs/registry_consistency_contract.yaml](_registry/catalogs/registry_consistency_contract.yaml) | 48 个注册表总索引 |
| **门禁注册表** | [_registry/catalogs/gate_registry.yaml](_registry/catalogs/gate_registry.yaml) | 全部门禁清单 |
| **功能域注册表** | [_registry/catalogs/functional_domain_registry.yaml](_registry/catalogs/functional_domain_registry.yaml) | 39 域清单 |
| **架构契约** | [_registry/contracts/architecture_contract.yaml](_registry/contracts/architecture_contract.yaml) | 架构合规自动验证契约 |
| **frontmatter Schema** | [_registry/schemas/frontmatter_schema.json](_registry/schemas/frontmatter_schema.json) | frontmatter 字段校验 Schema |
| **术语表** | [_registry/vocabularies/glossary.yaml](_registry/vocabularies/glossary.yaml) | 术语仲裁源 |
| **doc_type 词表** | [_registry/vocabularies/doc_type_vocabulary.yaml](_registry/vocabularies/doc_type_vocabulary.yaml) | 文档类型受控枚举 |
| **domain 词表** | [_registry/vocabularies/domain_vocabulary.yaml](_registry/vocabularies/domain_vocabulary.yaml) | 域受控枚举 |

---

## 六、变更记录

| 版本 | 日期 | 变更内容 |
|------|------|---------|
| 2.1.0 | 2026-06-26 | P0 审查修复。(1) §4.1 冷启动路径加入 trae_060（向内收三原则）作为第 2 步必读真源，与 `.trae/rules/project_rules.md` 第二原则对称接入。(2) 目录树补全 058/059/060。(3) 修正"48 个 trae_*.yaml"为"60 个"（3 处）+ 管辖文件数 49→61。(4) 分类体系表 040-057→040-060。对齐 trae_060 §2 唯一真源与 §4 新AI可发现性。 |
| 2.0.0 | 2026-06-22 | 架构升级对齐。(1) 删除 meta/ 目录引用（已物理删除，规则合并至 rules/）。(2) 删除 governance/、operational/、domains/ 目录引用（已删除，内容合并至 rules/）。(3) 新增 rules/ 目录（60 个 trae_*.yaml）。(4) 更新 _registry/ 文件数（catalogs 24 + contracts 3 + schemas 3 + vocabularies 25 = 55）。(5) 统一下划线命名（doc_type_vocabulary.yaml → doc_type_vocabulary.yaml 等）。(6) 移除14层引用（D19/D21 裁定：14层降级为域属性）。 |
| 1.4.0 | 2026-05-04 | 审计修复。meta/ 下已迁移文件注释行删除；文件数全面更新。 |
| 1.2.0 | 2026-05-02 | 审计修复——全量文件数对账。 |
| 1.1.0 | 2026-05-01 | 目录树全中文化 + 索引策略明确。 |
| 1.0.0 | 2026-05-01 | 初始创建。 |
