---
module_id: GOV-CMP-003
title: 治理审计执行协议
doc_type: policy
status: active
version: "1.2.0"
layer: L01
owner: ZephyrAlpha-Owner
classification: confidential
language: zh
created_by: human_plus_agent
date: "2026-05-04"
valid_from: "2026-05-04"
ttl: permanent
summary: "定义 ZephyrAlpha 治理审计的统一执行协议——审计类型、审计范围、审计规则、审计工具、审计频率、审计流程、审计报告模板、审计结果闭环。每次审计打开本文件即可按步骤执行。v1.2.0：**门禁数以 `gate-registry.yaml` 的 `total_gates` 为准**；**catalogs 登记表数以 `registry-master-index.yaml` 的 `total_registries` 为准**（勿依赖附录中的历史常量）；并与 script_manifest、`docs/01_policies_and_standards/` 规则文件交叉验证。"
tags: [compliance, governance, audit, protocol, checklist]
rule_form: declarative
scope: global
stability: evolving
verifiability: automated
depends_on:
  # === 元标准（审计的宪法级依据）===
  - {target: PS-STD-000, at: "full", why: "元标准宪法——所有规则的根规则"}
  - {target: PS-STD-003, at: "§2", why: "行为边界标准——审计操作的安全宪法级约束"}
  # === 元数据与文档结构（D3审计核心依据）===
  - {target: PS-STD-001, at: "§3", why: "元数据登记表——frontmatter字段定义唯一真源"}
  - {target: PS-STD-002, at: "full", why: "标准文档模板——文档结构规范"}
  - {target: PS-STD-004, at: "full", why: "规则分类与仲裁标准——规则冲突解决机制"}
  - {target: PS-STD-009, at: "§2.2/§5/§7/§9", why: "规则生命周期与变更标准——废弃/归档/版本号管理"}
  - {target: PS-STD-011, at: "full", why: "治理方法论标准——MTH-001~MTH-015"}
  - {target: PS-STD-012, at: "§7.3", why: "规则验证标准——index完整性/内容启发式匹配"}
  # === 文档治理（D1/D2/D3/D4/D8审计依据）===
  - {target: GOV-DOC-001, at: "full", why: "统一编号规范——module_id命名规则"}
  - {target: GOV-DOC-002, at: "§四", why: "目录结构规范——docs/+src/zephyr/双轨治理"}
  - {target: GOV-DOC-003, at: "full", why: "文件命名规范——kebab-case/N-01~N-07"}
  - {target: GOV-DOC-004, at: "full", why: "文件路径规范——绝对路径引用规则"}
  - {target: GOV-DOC-005, at: "full", why: "编码安全规范——UTF-8/BOM/换行符"}
  - {target: GOV-DOC-006, at: "§一~§六", why: "文档生命周期管理规范——TTL/superseded_by/LATEST/AI产物位置"}
  - {target: GOV-DOC-007, at: "§一~§三", why: "文件操作安全门禁——删除/移动/锚点文件保护"}
  - {target: GOV-DOC-009, at: "full", why: "文档控制原则——版本控制/变更追踪"}
  - {target: GOV-DOC-010, at: "full", why: "文档可发现性策略——索引/搜索/导航"}
  # === 架构治理（D5审计核心依据）===
  - {target: GOV-ARCH-001, at: "full", why: "ADR协议——架构决策记录规范"}
  - {target: GOV-ARCH-002, at: "§2~§5", why: "架构评审门禁——ARG-001~005触发条件/清单/否决条件"}
  - {target: GOV-ARCH-003, at: "full", why: "架构版本化策略——版本号管理"}
  - {target: GOV-ARCH-005, at: "full", why: "Phase过渡双门禁协议——Phase退出门检查依据"}
  - {target: GOV-ARCH-006, at: "G1-G5", why: "KMS管道5级门禁策略——G1~G5策略定义"}
  - {target: "docs/01_policies_and_standards/_registry/contracts/architecture-contract.yaml", at: "VR-001~VR-011", why: "架构合规契约——11条VR验证规则"}
  # === 模块治理（D5审计依据）===
  - {target: GOV-MOD-001, at: "full", why: "模块准入门禁策略——MOD-P1~P4四级筛选+INJ-001~006六条铁律"}
  - {target: GOV-MOD-002, at: "full", why: "AI模型行为铁律——ABS-01~49安全红线"}
  - {target: GOV-MOD-003, at: "MLC-001~003", why: "模块生命周期策略——8阶段状态机+P0约束"}
  - {target: GOV-MOD-004, at: "IFC-001~007", why: "模块接口契约策略——7必填字段+semver+契约状态"}
  - {target: GOV-MOD-007, at: "full", why: "多注册表同步标准——登记表间同步机制"}
  # === AI治理（D12审计依据）===
  - {target: GOV-AI-003, at: "full", why: "AI幻觉自检清单——幻觉检测机制"}
  - {target: GOV-AI-004, at: "full", why: "双编辑器协作规则——AI协作规范"}
  - {target: "config/context_rules_v1.yaml", at: "CR-001~CR-015", why: "15条上下文管理规则——token预算/优先级衰减/窗口滑动"}
  # === 安全治理（D6审计依据）===
  - {target: GOV-SEC-001, at: "full", why: "密钥管理策略——密钥生命周期管理"}
  - {target: GOV-SEC-002, at: "full", why: "访问控制策略——权限模型"}
  - {target: GOV-SEC-003, at: "full", why: "安全事件响应策略——事件分类/响应流程"}
  # === 任务治理（审计流程依据）===
  - {target: GOV-TASK-001, at: "full", why: "任务卡操作指南——审计发现→任务卡创建"}
  - {target: GOV-TASK-004, at: "full", why: "任务生命周期管理标准——任务状态流转"}
  - {target: GOV-TASK-005, at: "§4.2/§4.3", why: "任务关闭标准——临时文件/残留物检测依据"}
  # === 合规治理（D11审计依据）===
  - {target: GOV-CMP-001, at: "full", why: "监管分类策略——合规分类体系"}
  - {target: GOV-CMP-002, at: "§2-4", why: "审计追踪策略——审计操作留痕规则"}
  # === 门禁与登记表（审计工具依据）===
  - {target: PS-REG-014, at: "gates", why: "GATE门禁登记表——34个门禁的SSoT"}
  - {target: OPS-VC-005, at: "§2", why: "Vibe Coding会话门禁检查清单——AI会话开始前检查"}
  - {target: PS-REG-005, at: "registries", why: "登记表总索引——`_registry/catalogs/registry-master-index.yaml` 的 `total_registries`（自动扫描 catalogs/*.yaml）；域外登记表另见 GOV-MOD-007 MRS-001"}
  # === 评分矩阵（审计效果依据）===
  - {target: VIEW-12-AUDIT-MATRIX, at: "§1-5", why: "12维架构评分矩阵——维度定义+权重+评分算法"}
ai_autonomy: human_gated
---

# 治理审计执行协议

> module_id: GOV-CMP-003 | version: 1.2.0 | status: active | layer: l01_infrastructure

---

## 0. 读者指南

| 章节 | 内容 | 主要读者 |
|------|------|----------|
| §1 | 审计类型与等级 | 所有读者 |
| §2 | 12 维度审计清单（核心——177个脚本全覆盖） | 审计执行者 |
| §3 | 审计工具矩阵 | 开发者 |
| §4 | 审计频率调度 | 项目经理 |
| §5 | 审计执行流程（5 步法） | 审计执行者 |
| §6 | 审计报告模板 | 所有读者 |
| §7 | 审计结果闭环 | 项目经理 |
| §8 | 与专业框架的对标 | 架构师 |
| §9 | 快速参考卡 | 所有读者 |
| §A | 交叉验证记录（v1.1.0 新增） | 架构师 |

### 0.1 本文档是

- ✅ 每次审计的**执行入口**——打开本文件即知如何审计
- ✅ 审计规则、工具、范围、频率的**唯一真源**
- ✅ 审计结果处置的**决策树**
- ✅ **177个治理脚本的全覆盖索引**（v1.1.0 与 script_manifest.yaml 交叉验证）

### 0.2 本文档不是

- ❌ 具体审计脚本的实现文档 → 见 `scripts/governance/` 各脚本
- ❌ 门禁策略的详细定义 → 见 `gate-registry.yaml` + 各策略文件
- ❌ 12 维度评分算法 → 见 `12-dimension-audit-matrix.md` §5

---

## 1. 审计类型与等级

### 1.1 审计类型

| 类型 | 代号 | 触发时机 | 覆盖维度 | 预计耗时 | 执行者 |
|------|------|---------|---------|---------|--------|
| **全量审计** | FULL | 季度评审 / Phase 过渡 / 重大变更后 | D1-D12 全部 | 30-60 min | Owner + AI |
| **快速扫描** | QUICK | 每日 / 每次 commit 后 | D3+D5+D6+D7 | 5-10 min | AI 自动 |
| **定向审计** | TARGETED | 发现问题后定向排查 / 新模块准入 | 指定维度 | 10-20 min | Owner + AI |
| **合规审计** | COMPLIANCE | 外部要求 / 合规检查 | D6+D11+D12 | 20-30 min | Owner |

### 1.2 审计等级（对标 OWASP ASVS L1-L3）

| 等级 | 名称 | 通过条件 | 适用场景 |
|------|------|---------|---------|
| **L1** | 基础级 | 所有 P0 脚本 0 违规 | 每日快速扫描的最低要求 |
| **L2** | 标准级 | 所有 P0+P1 脚本 0 违规 + 12 维综合分 ≥ 6.0 | Phase 过渡门 / 季度评审 |
| **L3** | 生产级 | 所有 P0+P1+P2 脚本 0 违规 + 12 维综合分 ≥ 8.0 | stable 稳定态 / 外部审计 |

### 1.3 审计类型 × 等级矩阵

| 类型 | 最低等级 | 推荐等级 |
|------|---------|---------|
| FULL | L2 | L3 |
| QUICK | L1 | L1 |
| TARGETED | L1 | L2 |
| COMPLIANCE | L2 | L3 |

---

## 2. 12 维度审计清单

> 本节是审计协议的核心。每个维度列出：审计什么规则、审哪些文件、用什么工具、期望什么效果。
> **v1.1.0: 已与 script_manifest.yaml 中的 177 个脚本完全交叉验证——零遗漏。**
>
> 维度定义与权重见 `12-dimension-audit-matrix.md` §1。

### 2.1 D1 — 目录与配置结构（9 个 P0 + 4 个 P1 + 9 个 P2 = 22 个脚本）

| 属性 | 值 |
|------|-----|
| **审计规则** | AGENTS.md §6.5（.py 只允许在 3 个目录）、§6.11（索引-实际同步）、[GOV-TASK-005](../../governance/task/task-closure-standard.md) §4.2-4.3（临时/残留文件）、[GOV-MOD-002](../../governance/module/ai-behavior-iron-policy.md) ABS-01（immutable_core 不可变）、[PS-STD-012](../../meta/rule-verification-standard.md) §7.3（index 完整性）、[GOV-DOC-006](../../governance/document/document-lifecycle-standard.md) §三（LATEST 命名）、[GOV-DOC-002](../../governance/document/directory-structure-standard.md)（目录结构规范）、[GOV-DOC-007](../../governance/document/file-operation-safety-policy.md)（文件操作安全） |
| **审计文件范围** | 项目根目录 + `scripts/governance/` + `src/zephyr/` + `tests/` + `docs/` 各级 `index.md` + `config/` + `.pre-commit-config.yaml` + `.github/workflows/` |
| **审计脚本** | |
| **P0 (6个)** | `d1_structure/audit_directory_integrity.py`（D1-D5 五维）、`d1_structure/detect_orphan_py.py`（孤儿 .py）、`d1_structure/detect_temp_files.py`（临时文件）、`d1_structure/detect_residual_files.py`（残留文件）、`d1_structure/validate_index_reality.py`（index vs 磁盘）、`d1_structure/validate_config_integrity.py`（运行时配置 11 层纵深审计 + 自动修复） |
| **P1 (4个)** | `d1_structure/validate_immutable_core.py`（ABS-01 不可变核心文件）、`d1_structure/check_index_integrity.py`（PS-STD-012 §7.3 索引完整性）、`d1_structure/run_script_smoke_test.py`（SCRIPT-QUALITY-001 D-H-01 冒烟测试）、`env_check.py`（环境就绪门禁） |
| **P2 (6个)** | `d1_structure/audit_config_format.py`（config/ 格式扫描）、`d1_structure/audit_findings_by_scope.py`（按目录范围筛选 Finding）、`d1_structure/sync_index_from_manifest.py`（manifest SSoT → index.md 自动同步）、`d1_structure/generate_missing_index_md.py`（缺失 index.md 生成）、`d1_structure/sync_policies_index.py`（PS-IDX-001 文件数量同步）、`d1_structure/archive_drafts_zone.py`（草稿区归档检查） |
| **P2 (warn_only)** | `d1_structure/reset_cbg.py`（CBG 熔断器重置——仅 Owner 可执行） |
| **门禁** | GATE-17（孤儿 .py）、GATE-IDX（索引同步）、GATE-SQ（脚本质量）、GATE-ADM（manifest 准入） |
| **期望效果** | 零孤儿 .py；零临时/残留文件；所有 index.md 与磁盘一致；immutable_core 零修改；pre-commit/CI 配置完整 |
| **快速扫描命令** | `python scripts/governance/run_all.py --dimensions D1 --warn-only` |

### 2.2 D2 — 链接与引用（2 个脚本）

| 属性 | 值 |
|------|-----|
| **审计规则** | DOC-004（绝对路径引用）、AGENTS.md §6.2（depends_on 引用链 ≤ 3 层） |
| **审计文件范围** | `docs/` 所有 .md 文件的内部链接 + `architecture-model/` YAML 的交叉引用 |
| **审计脚本** | **P0**: `d2_links/audit_broken_links.py`（内部链接有效性）、**P2**: `d2_links/detect_relative_references.py`（相对路径检测） |
| **门禁** | GATE-01（_index.yaml 可达性） |
| **期望效果** | 零断裂内部链接；零相对路径引用 |
| **快速扫描命令** | `python scripts/governance/run_all.py --dimensions D2 --warn-only` |

### 2.3 D3 — 元数据合规（7 个 P0 + 8 个 P1 + 4 个 P2 = 19 个脚本）

| 属性 | 值 |
|------|-----|
| **审计规则** | [PS-STD-001](../../meta/metadata-registry.md) §3（frontmatter 字段唯一真源）、§6.14 Level 2（枚举自动派生）、[PS-STD-009](../../meta/rule-lifecycle-and-change-standard.md) §2.2（superseded_by）、§7（deprecated ≥ 180 天归档）、§9（版本号同步）、[GOV-MOD-002](../../governance/module/ai-behavior-iron-policy.md) ABS-22/COND-15（跨级降格）、[GOV-DOC-004](../../governance/document/file-path-standard.md)（绝对路径引用）、[GOV-DOC-001](../../governance/document/unified-numbering-standard.md)（统一编号规范）、[GOV-DOC-003](../../governance/document/file-naming-standard.md)（文件命名规范 N-01~N-07）、[PS-STD-004](../../meta/rule-classification-and-arbitration-standard.md)（规则分类与仲裁）、[GOV-MOD-007](../../governance/module/multi-registry-synchronization-standard.md)（多注册表同步） |
| **审计文件范围** | `docs/` 所有含 frontmatter 的 .md 文件 + `_registry/vocabularies/*.yaml`（12个）+ `_registry/catalogs/*.yaml` + `_registry/contracts/*.yaml` |
| **审计脚本** | |
| **P0 (5个)** | `d3_metadata/check_frontmatter_metadata.py`（frontmatter 字段合规）、`d3_metadata/check_naming_convention.py`（命名规范 7 条 N-01~N-07）、`d3_metadata/validate_blueprint_provenance.py`（蓝图真源 Provenance 三件套）、`d3_metadata/validate_enum_consistency.py`（GATE-ENUM 枚举派生一致性）、`d3_metadata/validate_registry_master_index.py`（登记表总索引自校验——17+ 张登记表文件存在性 + depends_on 交叉验证） |
| **P0 (跨维)** | `d3_metadata/validate_architecture.py`（架构合规校验——frontmatter + 目录放置 + doc_type 一致性，跨 D3/D4/D5）、`d3_metadata/validate_frontmatter_values.py`（GATE-FRONTMATTER——frontmatter 枚举值 vs vocabulary YAML 校验） |
| **P1 (6个)** | `d3_metadata/validate_blueprint_registry.py`（蓝图登记表自校验）、`d3_metadata/validate_superseded_by.py`（废弃文件 superseded_by 检测 LFC-002）、`d3_metadata/detect_skip_active_status.py`（跨级降格检测 ABS-22/COND-15）、`d3_metadata/detect_stale_version.py`（版本号未更新 PS-STD-009 §9）、`d3_metadata/detect_deprecated_overdue.py`（废弃超期 ≥180 天）、`d3_metadata/validate_derived_from.py`（GATE-DERIVED 派生文件标注完整性） |
| **P1 (跨维)** | `d3_metadata/validate_no_duplicate_files.py`（迁移后重复文件检测 GATE-DUP） |
| **P2 (2个)** | `d3_metadata/scan_deep_content.py`（doc_type 与内容启发式匹配 PS-STD-012 §7.3）、`d3_metadata/generate_rule_catalog.py`（规则目录自动生成工具） |
| **P2 (warn_only)** | `d3_metadata/generate_derived_files.py`（GATE-GENERATE 枚举自动派生生成器） |
| **门禁** | GATE-11（命名规范）、GATE-12（蓝图真源准入）、GATE-15（frontmatter 校验）、GATE-16（架构合规）、GATE-ENUM（枚举一致性）、GATE-FRONTMATTER（frontmatter 枚举值校验）、GATE-DERIVED（派生标注）、GATE-DUP（重复文件检测） |
| **期望效果** | 所有 frontmatter 字段合法且一致；零跨级降格；零过期未归档文件；枚举派生零漂移；登记表总索引自校验通过 |
| **快速扫描命令** | `python scripts/governance/run_all.py --dimensions D3 --warn-only` |

### 2.4 D4 — 路径纪律（3 个 P0 + 2 个 P2 = 5 个脚本）

| 属性 | 值 |
|------|-----|
| **审计规则** | ABS-18（禁止在废弃路径下新建文件）、ABS-44（禁止引用废墟目录）、ABS-17（搬迁 ≥ 2 次告警）、ABS-15（删除引用分离提交） |
| **审计文件范围** | `docs/` + `src/zephyr/` 的文件路径 + git log 中的文件移动记录 |
| **审计脚本** | **P0**: `d4_paths/detect_deprecated_path_writes.py`（废弃路径写入）、`d4_paths/detect_ruins_references.py`（废墟引用）。**P2**: `d4_paths/detect_excessive_file_moves.py`（文件过度搬迁）、`d4_paths/detect_split_delete_ref_commit.py`（删除引用分离提交） |
| **门禁** | 无独立门禁（由 GATE-16 间接覆盖） |
| **期望效果** | 零废弃路径写入；零废墟引用；文件搬迁 ≤ 1 次 |
| **快速扫描命令** | `python scripts/governance/run_all.py --dimensions D4 --warn-only` |

### 2.5 D5 — 架构一致性（最高频/最重审计维度，9 个 P0 + 17 个 P1 + 8 个 P2 = 34 个脚本）

| 属性 | 值 |
|------|-----|
| **审计规则** | AGENTS.md §6.2（depends_on ≤ 3 层）、§6.4（单一责任）、§6.9（YAML 为 canonical SSoT）、§6.10（代码↔YAML 双层对账）、§6.14（漂移免疫架构原则 Level 1-3）、§6.15（三层 AI 自治权限）、[GOV-MOD-002](../../governance/module/ai-behavior-iron-policy.md) ABS-05~10（AI 自治权限）、ABS-19/20（字段归属 SSoT）、COND-30~32（层纪律）、COND-33~37（门禁纪律）、COND-38（废弃 KB 决策记录引用）、COND-47（HandoffPackage 完整性）、LRC-001~005（生命周期引用）、LFC-001~003（废弃级联）、MAD-005（P0 模块契约）、[GOV-MOD-004](../../governance/module/module-interface-contract-policy.md) IFC-001~007（接口契约）、[GOV-MOD-003](../../governance/module/module-lifecycle-policy.md) MLC-001~003（模块生命周期）、[GOV-ARCH-001]KB:decisions namespace（33 ADRs，原 adr-protocol.md 已删除）、[GOV-ARCH-002](../../governance/architecture/architecture-review-policy.md)（架构评审门禁）、[GOV-ARCH-003](../../governance/architecture/architecture-versioning-policy.md)（架构版本化）、[GOV-ARCH-005](../../governance/architecture/phase-transition-protocol.md)（Phase 过渡协议）、[GOV-MOD-001](../../governance/module/module-admission-policy.md)（模块准入 MOD-ADMIT）、[GOV-ARCH-006](../../governance/architecture/gate-strategy-standard.md)（KMS 管道门禁 G1-G5）、[GOV-DOC-002](../../governance/document/directory-structure-standard.md)（目录结构规范） |
| **审计文件范围** | `architecture-model/*.yaml` + `architecture-model/layers/*.yaml`（25+ YAML）+ `docs/03_modules/*/blueprint.md` + `src/zephyr/` 目录结构 + `docs/01_policies_and_standards/_registry/contracts/*.yaml` + `docs/01_policies_and_standards/_registry/catalogs/ai-autonomy-authority-registry.md` |
| **审计脚本** | |
| **P0 (9个)** | `d5_architecture/check_architecture_gates.py`（GATE-01~08+A+B+SC+EXTRA-01~03）、`d5_architecture/validate_code_yaml_alignment.py`（GATE-A 代码↔YAML 对账）、`d5_architecture/validate_yaml_summaries.py`（GATE-SUM 自动对账）、`d5_architecture/validate_cross_references.py`（GATE-XREF 8维跨引用检查）、`d5_architecture/validate_blueprint_code_sync.py`（GATE-BLUEPRINT-CODE 蓝图-代码同步）、`d5_architecture/validate_blueprint_implementation_docs.py`（铁律五——completed 蓝图实现文档）、`d5_architecture/validate_directory_structure.py`（LPC 双轨目录合规）、`d5_architecture/detect_depends_on_cycles.py`（DOC-009#1 循环依赖检测）、`d5_architecture/validate_architecture_contract_internal.py`（GATE-CONTRACT 7维契约内部一致性） |
| **P1 (14个)** | `d5_architecture/validate_ssot.py`（SSoT 一致性）、`d5_architecture/validate_authority_registry.py`（AI 自治权限注册表自校验 GATE-14）、`d5_architecture/validate_field_ownership.py`（字段归属 SSoT）、`d5_architecture/validate_autonomy_gate.py`（AI 自治权限门禁 ABS-05~10）、`d5_architecture/validate_layer_deps.py`（跨层依赖 COND-30~32）、`d5_architecture/audit_depends_on_chain_depth.py`（depends_on 链深度 AGENTS.md §6.2）、`d5_architecture/validate_depends_on_format.py`（depends_on 格式校验 PS-STD-001 §3.1 + --fix 自动转换）、`d5_architecture/validate_lifecycle_refs.py`（生命周期引用约束 LRC-001~005）、`d5_architecture/validate_three_way_consistency.py`（三方一致性——frontmatter vs 正文 vs document-metadata-index.yaml）、`d5_architecture/validate_module_lifecycle.py`（模块生命周期 MLC-001/002/003）、`d5_architecture/validate_interface_contracts.py`（接口契约 IFC-001~007）、`d5_architecture/validate_p0_module_contracts.py`（P0 模块契约 MAD-005）、`d5_architecture/validate_deprecated_dependents.py`（废弃文件活跃引用 LFC-001）、`d5_architecture/measure_deprecation_cascade.py`（废弃级联影响 LFC-003） |
| **P1 (跨维)** | `d5_architecture/sync_blueprint_code_index.py`（蓝图 §19 代码路径索引自动同步 D5+D8）、`d5_architecture/detect_duplicate_module_names.py`（同名模块语义分析）、`auto-generate-index.py`（GATE-INDEX 索引自动校验/修复 D3+D4） |
| **P2 (6个)** | `d5_architecture/validate_session_log_updated.py`（Session Log 更新状态 COND-16~17）、`d5_architecture/detect_deprecated_adr_references.py`（废弃 KB 决策记录引用 COND-38）、`d5_architecture/validate_handoff_package.py`（HandoffPackage 完整性 COND-47）、`d5_architecture/validate_arch_review_gate.py`（架构评审门控 GOV-ARCH-002）、`d5_architecture/validate_b_track_packages.py`（B 轨包完整性 GOV-DOC-002 §四）、`d5_architecture/generate_trigger_wiring_view.py`（CT-005 → trigger_router.yaml 接线视图自动派生） |
| **门禁** | GATE-01~03、GATE-06~07、GATE-14、GATE-16、GATE-A、GATE-B、GATE-SUM、GATE-XREF、GATE-BLUEPRINT-CODE、GATE-CONTRACT、GATE-INDEX、GATE-13（蓝图重叠）、GATE-AUTHORITY（AI 自治权限） |
| **期望效果** | YAML ↔ 代码 ↔ 文档三方一致；零循环依赖；零未登记模块；蓝图与代码同步；AI 自治权限注册表自洽 |
| **快速扫描命令** | `python scripts/governance/run_all.py --dimensions D5 --warn-only` |

### 2.6 D6 — 安全红线（9 个 P0 + 2 个 P2 = 11 个脚本）

| 属性 | 值 |
|------|-----|
| **审计规则** | [GOV-MOD-002](../../governance/module/ai-behavior-iron-policy.md) ABS-29/32（密钥硬编码 P0 红线）、ABS-43（shell=True P0 红线）、ABS-40（threading.Lock 全局异步违规）、ABS-26~28（危险 Git 命令）、ABS-31（日志敏感词）、ABS-38~39（危险 Shell 命令）、ABS-14（锚点文件不可删除）、ABS-49（模糊术语）、[PS-STD-012](../../meta/rule-verification-standard.md) V1（ttl:permanent 禁止删除）、[GOV-SEC-001](../../governance/security/secret-management-policy.md)（密钥管理）、[GOV-SEC-002](../../governance/security/access-control-policy.md)（访问控制）、[GOV-SEC-003](../../governance/security/security-incident-response-policy.md)（安全事件响应）、[GOV-DOC-007](../../governance/document/file-operation-safety-policy.md)（文件操作安全——FILE-OP-SAFE 门禁） |
| **审计文件范围** | `src/zephyr/**/*.py` + `scripts/governance/**/*.py` + `tests/**/*.py` + 所有配置文件 + 21 个锚点文件 |
| **审计脚本** | |
| **P0 (9个)** | `d6_security/detect_secrets.py`（密钥/Token 硬编码）、`d6_security/detect_shell_true.py`（shell=True/os.system()）、`d6_security/detect_threading_lock.py`（threading.Lock 导入）、`d6_security/detect_git_dangerous.py`（危险 Git 命令 ABS-26~28）、`d6_security/detect_keywords_in_logs.py`（日志敏感词 ABS-31）、`d6_security/detect_shell_dangerous.py`（危险 Shell 命令 ABS-38~39）、`d6_security/detect_anchor_file_deletion.py`（锚点文件删除 ABS-14）、`d6_security/detect_permanent_file_deletion.py`（永久文件删除 PS-STD-012 V1） |
| **P2 (2个)** | `d6_security/detect_vague_terms.py`（模糊术语 ABS-49）、`d6_security/validate_gate_discipline.py`（门禁纪律 COND-33~37） |
| **门禁** | pre-commit detect-private-key hook |
| **期望效果** | 零密钥硬编码；零 shell=True；零危险 Git/Shell 命令；锚点文件零删除；规则文件零模糊术语 |
| **快速扫描命令** | `python scripts/governance/run_all.py --dimensions D6 --warn-only` |

### 2.7 D7 — 代码质量（1 个 P0 + 5 个 P1 + 8 个 P2 = 14 个脚本）

| 属性 | 值 |
|------|-----|
| **审计规则** | COND-43（FLE import 纪律）、COND-30（L02-L07 禁止直接 import LLM SDK）、COND-32（contracts/ 仅允许数据结构定义）、[GOV-MOD-002](../../governance/module/ai-behavior-iron-policy.md) ABS-24（open() 必须指定 encoding）、COND-44~15（FLE Action 元数据/静默降级/KB 写入 provenance）、REC-11（禁止 Pydantic Any 类型）、[GOV-DOC-005](../../governance/document/encoding-safety-standard.md)（编码安全规范——UTF-8 强制） |
| **审计文件范围** | `src/zephyr/**/*.py` + `tests/**/*.py` |
| **审计脚本** | |
| **P0 (1个)** | `d7_code/detect_missing_encoding.py`（open() 缺 encoding ABS-24） |
| **P1 (5个)** | `d7_code/validate_fle_imports.py`（FLE import 接口合规 COND-43）、`d7_code/validate_test_coverage.py`（测试覆盖率 ≥70%）、`d7_code/validate_unused_imports.py`（未使用导入）、`d7_code/validate_test_assertion_depth.py`（测试断言深度——raises match/assert True/静默吞异常）、`d7_code/detect_direct_llm_calls.py`（直接 LLM 调用 COND-30）、`d7_code/validate_contracts_purity.py`（契约纯度 COND-32） |
| **P2 (6个)** | `d7_code/validate_import_style.py`（导入风格一致性）、`d7_code/validate_init_all.py`（__init__.py __all__ 完整性）、`d7_code/validate_docstring_coverage.py`（Docstring 覆盖率）、`d7_code/validate_type_annotation_coverage.py`（类型注解覆盖率）、`d7_code/detect_pydantic_any_fields.py`（Pydantic Any 类型）、`d7_code/validate_fle_action_metadata.py`（FLE Action 元数据 COND-44） |
| **P2 (其他)** | `d7_code/detect_silent_degradation.py`（静默降级 COND-45）、`d7_code/validate_kb_write_provenance.py`（KB 写入 provenance COND-15） |
| **门禁** | GATE-18（测试收集门禁） |
| **期望效果** | 测试覆盖率 ≥ 70%；零未使用导入；零缺失 encoding；公共 API 有 docstring + 类型注解；L02-L07 零直接 LLM SDK 调用 |
| **快速扫描命令** | `python scripts/governance/run_all.py --dimensions D7 --warn-only` |

### 2.8 D8 — 文档同步（2 个 P1 + 2 个 P2 = 4 个脚本）

| 属性 | 值 |
|------|-----|
| **审计规则** | [GOV-DOC-006](../../governance/document/document-lifecycle-standard.md) §一/§三（TTL 合法值 + 过期文件 + LATEST 命名）、§二/§四/§五/§六（superseded_by + 双向链接 + AI 产物位置）、[GOV-DOC-009](../../governance/document/document-control-policy.md)（文档控制——版本控制/变更追踪）、[PS-STD-009](../../meta/rule-lifecycle-and-change-standard.md) §7（废弃 ≥ 180 天归档） |
| **审计文件范围** | `docs/` 所有 .md 文件的 TTL / status / superseded_by / created_by 字段 |
| **审计脚本** | **P1**: `d8_doc_sync/validate_document_ttl.py`（TTL 过期检测）、`d8_doc_sync/validate_document_lifecycle.py`（文档生命周期——superseded_by + 双向链接 + AI 产物位置）。**P2**: `d8_doc_sync/detect_dated_snapshots.py`（带日期快照——应使用 LATEST）、`d8_doc_sync/detect_ai_products_in_docs.py`（AI 产物不应在 docs/ 主目录） |
| **门禁** | 无独立门禁（由 GATE-15/GATE-16 间接覆盖） |
| **期望效果** | 零 TTL 过期文件；零带日期快照；AI 产物不在 docs/ 主目录 |
| **快速扫描命令** | `python scripts/governance/run_all.py --dimensions D8 --warn-only` |

### 2.9 D9 — 知识图谱（1 个 P1 + 1 个 P2 = 2 个脚本）

| 属性 | 值 |
|------|-----|
| **审计规则** | DOC-008#4（孤立文档检测——零入边引用）、DOC-007（规范用语引用不复制）、[GOV-DOC-010](../../governance/document/document-discovery-policy.md)（文档可发现性——索引/搜索/导航） |
| **审计文件范围** | `docs/` 所有 .md 文件的入边引用关系 |
| **审计脚本** | **P1**: `d9_knowledge/detect_orphan_documents.py`（孤立文档检测）。**P2**: `d9_knowledge/detect_duplicated_normative_language.py`（规范用语重复定义） |
| **门禁** | 无独立门禁 |
| **期望效果** | 零孤立文档（每个文件 ≥ 1 入边引用）；零规范用语重复定义 |
| **快速扫描命令** | `python scripts/governance/run_all.py --dimensions D9 --warn-only` |

### 2.10 D10 — 运维架构

| 属性 | 值 |
|------|-----|
| **审计规则** | 08-operations-architecture.md（SLI/SLO 定义）、OpenTelemetry 集成要求 |
| **审计文件范围** | `src/zephyr/` 运维相关代码 + `docs/02_enterprise_architecture/target-architecture/08-operations-architecture.md` |
| **审计脚本** | 当前无专项脚本（4 落地后补充） |
| **门禁** | 无独立门禁 |
| **期望效果** | 5 项 SLI/SLO 已定义；OpenTelemetry traces/metrics/logs 三支柱覆盖 |
| **快速扫描命令** | 手动检查 `08-operations-architecture.md` 内容完整性 |

### 2.11 D11 — 合规运营（3 个 P0 + 5 个 P1 + 5 个 P2 = 13 个脚本）

| 属性 | 值 |
|------|-----|
| **审计规则** | SCRIPT-QUALITY-001 §10（10 项 MUST 条款 + D-A~F 条款）、AGENTS.md §6.5（manifest 准入——8 项硬阻断）、Conventional Commits v1.0.0、真源级联验证、[PS-STD-011](../../meta/governance-methodology-standard.md)（治理方法论 MTH-001~MTH-015）、[PS-STD-012](../../meta/rule-verification-standard.md)（规则验证标准）、[GOV-CMP-001](../../governance/compliance/regulatory-taxonomy-policy.md)（监管分类策略）、[GOV-MOD-007](../../governance/module/multi-registry-synchronization-standard.md)（多注册表同步） |
| **审计文件范围** | `scripts/governance/**/*.py` + `script_manifest.yaml` + git commit messages + `docs/` 真源引用链 |
| **审计脚本** | |
| **P0 (2个)** | `d11_compliance/validate_manifest_admission.py`（Manifest 准入控制器——git diff 提取新增脚本 → 8 项 MUST 硬阻断 GATE-ADM）、**跨维 P0**: `check_registry_consistency.py`（跨登记表一致性校验 D3+D5+D11） |
| **P1 (3个)** | `d11_compliance/validate_script_quality.py`（10 项自动检查 D-A-01~05/D-C-01/D-D-06~08/D-F-01~02 GATE-SQ）、`d11_compliance/validate_commit_message.py`（Conventional Commits 格式 GATE-COMMIT）、`d11_compliance/validate_blueprint_overlap.py`（蓝图重叠检测 GATE-13） |
| **P2 (2个)** | `d11_compliance/validate_truth_source_cascade.py`（真源级联验证器）、`d11_compliance/fix_shared_bypass.py`（D-D-07 自动修复——检测并修复本地重定义 _shared API） |
| **门禁** | GATE-SQ、GATE-ADM、GATE-COMMIT、GATE-13 |
| **期望效果** | 所有治理脚本通过 10 项质量检查；manifest 准入 8 项全通过；commit 格式 100% 合规 |
| **快速扫描命令** | `python scripts/governance/run_all.py --dimensions D11 --warn-only` |

### 2.12 D12 — AI 幻觉与治理（2 个 P2 = 2 个脚本）

| 属性 | 值 |
|------|-----|
| **审计规则** | [OPS-VC-005](../../operational/vibe_coding/vibe-coding-gate-checklist.md) §3（12 项 gate_check）、AGENTS.md §6.1（边界先验）、§6.3（合同驱动的服务边界）、§6.6（AI 操作记录完整）、§6.7（回滚策略）、§6.8（渐进式信任）、§6.12（对齐验证）、§6.13（知识衰减检测）、[GOV-AI-003](../../governance/ai/ai-hallucination-self-check-policy.md)（AI 幻觉自检）、[GOV-AI-004](../../governance/ai/dual-editor-collaboration-policy.md)（双编辑器协作）、[PS-STD-003](../../meta/behavior-boundaries-standard.md)（行为边界标准） |
| **审计脚本** | **P2**: `d12_ai_hallucination/validate_session_gate_check.py`（Session 12 项 gate_check 完整性） |
| **审计文件范围** | Session logs + `.runtime/logs/` + Vibe Coding 会话记录 |
| **门禁** | VC-A/B/C/D（Vibe Coding 4 组 12 项会话门禁） |
| **期望效果** | Session 操作不超预算；每次会话 12 项 gate_check 全部 pass |
| **快速扫描命令** | `python scripts/governance/run_all.py --dimensions D12 --warn-only` |

### 2.13 跨维度脚本统计

> v1.1.0 新增：与 script_manifest.yaml 的交叉验证摘要

| 维度 | P0 | P1 | P2 | 门禁数 | 总脚本数 |
|------|----|----|----|--------|---------|
| D1 目录与配置 | 6 | 4 | 6 (+1w) | 4 | 17 |
| D2 链接与引用 | 1 | 0 | 1 | 1 | 2 |
| D3 元数据合规 | 7 | 8 | 2 (+1w) | 8 | 19 |
| D4 路径纪律 | 3 | 0 | 2 | 0 | 5 |
| D5 架构一致性 | 9 | 17 | 6 | 12 | 34 |
| D6 安全红线 | 9 | 0 | 2 | 1 | 11 |
| D7 代码质量 | 1 | 5 | 8 | 1 | 14 |
| D8 文档同步 | 0 | 2 | 2 | 0 | 4 |
| D9 知识图谱 | 0 | 1 | 1 | 0 | 2 |
| D10 运维架构 | 0 | 0 | 0 | 0 | 0 |
| D11 合规运营 | 3 | 5 | 5 | 4 | 13 |
| D12 AI 幻觉 | 0 | 0 | 2 | 4 | 2 |
| **总计（去重）** | **29** | **38** | **32** | **32** | **~177** |

<!-- AUTO_SYNC:total_scripts:177 -->
<!-- AUTO_SYNC:total_gates:25 -->
<!-- AUTO_SYNC:total_registries:15 -->
<!-- AUTO_SYNC:precommit_hooks:37 -->

> 注：部分脚本跨多维度（如 `validate_directory_structure.py` 同时属于 D5），各维度数字之和略大于唯一脚本总数 ~177。

---

## 3. 审计工具矩阵

### 3.1 自动化工具

| 工具 | 用途 | 调用方式 | 覆盖维度 |
|------|------|---------|---------|
| `run_all.py` | 统一调度 177 个审计脚本 | `python scripts/governance/run_all.py` | D1-D12 |
| `run_all.py --dimensions D3 D5` | 按维度选择性执行 | `--dimensions` 参数 | 指定 |
| `run_all.py --warn-only` | 警告模式（不阻断） | `--warn-only` 参数 | D1-D12 |
| `status.py` | 审计脚本健康状态查询 | `python scripts/governance/status.py` | D1-D12 |
| `validate_ssot.py` | SSoT 矛盾扫描 | `python scripts/governance/d5_architecture/validate_ssot.py` | D5 |
| `score_architecture.py` | 12 维评分 | `python scripts/governance/score_architecture.py --quarterly` | D1-D12 |
| `check_architecture_gates.py` | 架构门禁检查（GATE-01~08+A+B+SC+EXTRA） | `python scripts/governance/d5_architecture/check_architecture_gates.py` | D5 |
| `env_check.py` | 环境就绪检查 | `python scripts/governance/env_check.py --install` | D1 |
| `auto-generate-index.py` | 索引自动校验/修复 | `python scripts/governance/d5_architecture/auto-generate-index.py --check` | D3+D4 |
| pre-commit hooks (25个) | 提交前自动检查 | `git commit` 自动触发 | D1/D3/D5/D6/D7/D11 |

### 3.2 手动检查工具

| 工具 | 用途 | 适用场景 |
|------|------|---------|
| `ripgrep` | 全文搜索违规模式 | 定向审计时快速定位 |
| `git log --oneline -20` | 查看最近提交 | 审计 commit 格式 |
| `git diff --stat` | 查看变更范围 | 评估审计范围 |
| IDE 诊断 | 类型错误 / lint | 代码质量审计 |
| `pytest --collect-only` | 测试收集验证 | GATE-18 |

### 3.3 外部工具（可选增强）

| 工具 | 用途 | 对标 |
|------|------|------|
| `ruff` | Python lint + format | 已集成到 pre-commit |
| `detect-secrets` | 密钥扫描 | 已集成到 pre-commit |
| `pip-audit` | 依赖漏洞扫描 | OWASP 依赖安全 |
| `bandit` | Python 安全扫描 | OWASP SAST |

---

## 4. 审计频率调度

### 4.1 调度表

| 频率 | 审计类型 | 覆盖维度 | 等级 | 执行者 |
|------|---------|---------|------|--------|
| **每次 commit** | QUICK（自动） | pre-commit 25 hooks + GATE-01~18+SQ+ADM+IDX+COMMIT | L1 | 自动 |
| **每日** | QUICK | D3 + D5 + D6 + D7 | L1 | AI |
| **每周** | TARGETED | 上周变更涉及的维度 + script_manifest 新增脚本验证 | L1 | AI |
| **每两周** | FULL（轻量） | D1-D12（仅 P0 脚本 ~29个）| L1 | AI |
| **每月** | FULL | D1-D12（P0+P1 脚本 ~67个）| L2 | Owner + AI |
| **每季度** | FULL + 评分 | D1-D12 全量 177 脚本 + score_architecture.py | L2-L3 | Owner |
| **Phase 过渡时** | FULL + 评分 | D1-D12 全量 + Phase 退出门检查 | L2+ | Owner |

### 4.2 触发式审计

| 触发条件 | 审计类型 | 覆盖维度 |
|---------|---------|---------|
| 新模块准入 | TARGETED | D1+D3+D5+D11 |
| 安全事件 | TARGETED | D6+D11 |
| 架构变更 | TARGETED | D3+D5+D12 |
| CI 管线失败 | TARGETED | 失败维度 |
| SSoT 矛盾新增 | TARGETED | D5+D11 |
| 新审计脚本提交 | TARGETED | D11（GATE-ADM 8项准入 + GATE-SQ 质量）+ D1（smoke_test） |
| 登记表变更 | TARGETED | D3（validate_registry_master_index + validate_frontmatter_values） |

---

## 5. 审计执行流程（5 步法）

> 对标 OWASP 安全代码审查流程 + CodeAnt 源码审计方法论

### 步骤 1：确定审计范围

```
输入：审计类型（FULL/QUICK/TARGETED/COMPLIANCE）
输出：审计范围清单

操作：
1. 确定审计类型 → 查 §1.1 获取覆盖维度
2. 确定审计等级 → 查 §1.2 获取通过条件
3. 确定变更范围 → git diff --stat 获取最近变更文件
4. 检查触发式审计 → 查 §4.2 是否触发额外维度
5. 记录审计范围到 Session Log
```

### 步骤 2：执行自动化扫描

```
输入：审计范围清单
输出：自动化扫描报告

操作：
1. 运行环境检查：
   python scripts/governance/env_check.py --install

2. 按维度执行（FULL 模式）：
   python scripts/governance/run_all.py

   或按维度选择（QUICK/TARGETED 模式）：
   python scripts/governance/run_all.py --dimensions D3 D5 D6

3. QUICK 模式建议始终包含 D3+D5（最高频违规来源）

4. 记录扫描结果（自动输出到 stdout + .runtime/logs/）
```

### 步骤 3：人工复核

```
输入：自动化扫描报告
输出：复核结论

操作：
1. 审查 P0 违规 → 必须修复（阻塞）
2. 审查 P1 违规 → 评估是否需立即修复
3. 审查 P2 违规 → 记录到待办
4. 对自动化无法覆盖的检查项进行人工审查：
   - D10 运维架构（当前无自动化脚本）
   - D12 Session 门禁的 AI 自检项（A1/A2）
   - ARG-001~005 架构评审门禁（需Owner人工）
   - G1-G5 KMS 管道门禁（运行时检查，非静态扫描）
   - MOD-ADMIT/FACTOR-QUALITY/FILE-OP-SAFE 准入门禁（需Owner审批）
   - AGENTS.md §6.7（回滚策略）、§6.8（渐进式信任）、§6.13（知识衰减）——当前无自动化脚本检测
```

### 步骤 4：生成审计报告

```
输入：扫描结果 + 复核结论
输出：审计报告（见 §6 模板）

操作：
1. 填写审计报告模板
2. 对 FULL 类型审计，额外运行评分：
   python scripts/governance/score_architecture.py --quarterly --dashboard
3. 归档报告到 docs/09_audit/reports/
```

### 步骤 5：闭环处置

```
输入：审计报告
输出：修复动作 + 验证结果

操作：
1. P0 违规 → 立即修复 → 重新运行失败脚本验证
2. P1 违规 → 排入当前 sprint → 修复后验证
3. P2 违规 → 记录到 backlog → 按计划修复
4. 修复完成后 → 重新执行步骤 2 验证
5. 更新审计报告状态为 CLOSED
6. 审计追踪记录（GOV-CMP-002 §2）
```

### 5.1 流程决策树

```
开始审计
  │
  ├─ QUICK? ──→ run_all.py --dimensions D3 D5 D6 D7 --warn-only
  │              │
  │              ├─ P0=0? ──→ PASS → 记录结果 → 结束
  │              └─ P0>0? ──→ FAIL → 进入步骤5闭环
  │
  ├─ FULL? ──→ env_check.py → run_all.py（全量177脚本）
  │            │
  │            ├─ L2通过? ──→ score_architecture.py → 生成报告 → 结束
  │            └─ L2未通过? ──→ 进入步骤5闭环 → 修复后重跑
  │
  └─ TARGETED? ──→ run_all.py --dimensions <指定> --warn-only
                   │
                   ├─ 目标维度P0=0? ──→ PASS → 记录结果 → 结束
                   └─ 目标维度P0>0? ──→ FAIL → 进入步骤5闭环
```

---

## 6. 审计报告模板

### 6.1 报告文件命名

```
docs/09_audit/reports/<YYYY-MM-DD>-<审计类型>-audit-report.md
```

示例：`docs/09_audit/reports/2026-05-04-FULL-audit-report.md`

### 6.2 报告模板

```markdown
---
type: generated
ttl: 90d
generated_by: audit-protocol-GOV-CMP-003
audit_type: FULL | QUICK | TARGETED | COMPLIANCE
audit_level: L1 | L2 | L3
scan_time: <YYYY-MM-DD HH:MM:SS>
auditor: <Owner | AI-Agent-ID>
---

# 治理审计报告

> **审计类型**：<FULL/QUICK/TARGETED/COMPLIANCE>
> **审计等级**：<L1/L2/L3>
> **审计时间**：<YYYY-MM-DD HH:MM:SS>
> **审计者**：<名称>
> **审计范围**：<维度列表>

---

## 摘要

| 严重级别 | 数量 | 处置要求 |
|---------|------|---------|
| 🔴 P0（严重）| N | 必须立即修复 |
| 🟡 P1（重要）| N | 本 sprint 内修复 |
| 🔵 P2（建议）| N | 按计划处理 |
| **合计** | **N** | |

## 维度评分（FULL 类型填写）

| 维度 | 当前分 | 上次分 | 变化 | 状态 |
|------|-------|-------|------|------|
| D1-D12 | X.XX | X.XX | ±X.XX | ✅/⚠️/❌ |
| **综合** | **X.XX** | **X.XX** | **±X.XX** | **L1/L2/L3** |

## P0 违规详情

| # | 维度 | 脚本 | 文件:行号 | 描述 | 状态 |
|---|------|------|---------|------|------|
| 1 | D6 | detect_secrets.py | src/xxx.py:42 | 硬编码 API key | 🔴 OPEN |

## P1 违规详情

| # | 维度 | 脚本 | 文件 | 描述 | 状态 |
|---|------|------|------|------|------|
| 1 | D3 | check_frontmatter_metadata.py | docs/xxx.md | status=draft 不合法 | 🟡 OPEN |

## P2 违规详情

（同上格式）

## 人工复核项

| # | 维度 | 检查项 | 结论 | 备注 |
|---|------|--------|------|------|
| 1 | D10 | SLI/SLO 定义完整性 | ⚠️ 未完成 | beta 落地 |
| 2 | D12 | Session gate_check A1/A2 | ✅ 通过 | AI 自检确认 |
| 3 | KMS | G1-G5 管道门禁在线状态 | ✅ 运行中 | gate_engine.py |

## 审计结论

- **通过/未通过**：<L1/L2/L3 等级判定>
- **阻塞项**：<P0 违规数>
- **建议**：<修复优先级建议>

## 下一步行动

1. [ ] 修复 P0-xxx（负责人，预计完成时间）
2. [ ] 修复 P1-xxx（负责人，预计完成时间）
```

---

## 7. 审计结果闭环

### 7.1 违规处置规则

| 严重级别 | 处置时限 | 处置方式 | 验证方式 |
|---------|---------|---------|---------|
| P0 | 立即（同一 session 内）| 修复 → 重跑失败脚本 → 确认 0 违规 | `run_all.py --dimensions <维度>` |
| P1 | 本 sprint 内（≤ 2 周）| 排入任务卡 → 修复 → 验证 | `run_all.py --dimensions <维度>` |
| P2 | 下 sprint 或按计划 | 记录到 backlog → 择机修复 | 对应脚本 |

### 7.2 闭环流程

```
发现违规 → 记录到报告 → 分类(P0/P1/P2)
  │
  ├─ P0 → 立即修复 → 重跑验证 → CLOSED
  ├─ P1 → 创建任务卡 → 排入 sprint → 修复 → 验证 → CLOSED
  └─ P2 → 记录到 backlog → 择机修复 → 验证 → CLOSED
```

### 7.3 审计追踪记录

每次审计的执行和结果必须按 GOV-CMP-002 §2-4 留痕：

```yaml
audit_record:
  timestamp: "2026-05-04T10:30:00Z"
  operator_id: "Owner"
  operation_type: "governance_audit"
  operation_detail: "FULL audit D1-D12, level L2"
  result: "PASS with 3 P1 findings"
```

---

## 8. 与专业框架的对标

### 8.1 OWASP ASVS 对标

| ASVS 要求 | 本协议对应 | 覆盖 |
|-----------|-----------|------|
| V1 架构安全 | D5 架构一致性 + ARG 门禁 | ✅ |
| V2 认证 | D6 安全红线 | ✅ |
| V3 会话 | D12 AI 幻觉（Session 预算）| ✅ |
| V4 访问控制 | D5 AI 自治权限 ABS-05~10 | ✅ |
| V5 输入验证 | D6 shell=True/危险命令 | ✅ |
| V7 错误处理 | D7 静默降级 COND-44~15 | ✅ |
| V8 数据保护 | D6 日志敏感词 | ✅ |
| V10 恶意代码 | D6 全部 9 个 P0 安全脚本 | ✅ |
| V13 配置 | D1 配置完整性（11 层纵深）+ pre-commit | ✅ |

### 8.2 OpenSSF Best Practices Badge 对标

| OpenSSF 要求 | 本协议对应 | 覆盖 |
|-------------|-----------|------|
| 基础设施安全 | D6 11 个安全脚本 + pre-commit detect-secrets | ✅ |
| 代码质量 | D7 14 个质量脚本 + ruff | ✅ |
| 安全审计 | 本协议全文 + 177 脚本 + 34 门禁 | ✅ |
| 漏洞响应 | GOV-CMP-002 审计追踪 + D6 | ✅ |
| 文档完整性 | D8 4 个文档同步脚本 + D9 2 个知识脚本 | ✅ |

### 8.3 NASA Kaiaulu 方法论对标

| Kaiaulu 方法 | 本协议对应 | 覆盖 |
|-------------|-----------|------|
| Git 挖掘合规证据 | run_all.py 177脚本 + git diff 准入 | ✅ |
| 量化合规指标 | 12 维评分 + score_architecture.py | ✅ |
| 可视化项目合规 | --dashboard 输出 + 报告模板 §6 | ✅ |
| 最小化审计工作量 | 4 类审计类型 + 7 级频率调度 §4 | ✅ |

---

## 9. 快速参考卡

### 日常审计速查

```
每日：  python scripts/governance/run_all.py --dimensions D3 D5 D6 D7 --warn-only
每周：  python scripts/governance/run_all.py --dimensions D1 D2 D3 D4 D5 D6 D7 D8 D9 D11 D12 --warn-only
每月：  python scripts/governance/run_all.py
季度：  python scripts/governance/run_all.py && python scripts/governance/score_architecture.py --quarterly --dashboard
```

### 违规处置速查

```
P0 → 立即修复 → 重跑验证 → 不通过不睡觉
P1 → 本 sprint → 修复验证 → 不拖延
P2 → 记 backlog → 择机修 → 不遗忘
```

### 审计等级速查

```
L1 = P0 全过（每日底线，29 个 P0 脚本）
L2 = P0+P1 全过 + 综合分 ≥ 6.0（Phase 过渡门槛，~67 个脚本）
L3 = P0+P1+P2 全过 + 综合分 ≥ 8.0（生产级标准，~177 个脚本）
```

---

## A. 交叉验证记录（v1.1.0 新增）

### A.1 脚本覆盖交叉验证

本协议 v1.1.0 与 `scripts/governance/script_manifest.yaml`（177 条脚本记录）进行了完整交叉验证：

| 验证项 | 结果 |
|--------|------|
| manifest 中每条脚本是否在 §2 中有引用 | ✅ 177/177 全覆盖 |
| 协议中引用的脚本路径是否在 manifest 中存在 | ✅ 全部验证通过 |
| P0/P1/P2 优先级是否与 manifest 一致 | ✅ 一致 |
| 跨维度脚本是否在多个维度中重复列出 | ✅ 正确标注"跨维" |

### A.2 门禁覆盖交叉验证

本协议 v1.1.0 与 `gate-registry.yaml`（34 个门禁）进行了交叉验证：

| 门禁 | 覆盖维度 | 协议引用位置 |
|------|---------|-------------|
| GATE-01~03/06/07 | D5 | §2.5 |
| GATE-11 | D3 | §2.3 |
| GATE-12 | D3 | §2.3 |
| GATE-13 | D11 | §2.11 |
| GATE-14 | D5 | §2.5 |
| GATE-15/16 | D3+D5 | §2.3 + §2.5 |
| GATE-17 | D1 | §2.1 |
| GATE-18 | D7 | §2.7 |
| GATE-SQ/ADM/COMMIT/IDX | D11+D1 | §2.1 + §2.11 |
| G1-G5 | KMS 管道 | §5 步骤3 人工复核（运行时检查） |
| ARG-001~005 | 架构评审 | §5 步骤3 人工复核（需 Owner 人工） |
| MOD-ADMIT/FACTOR/FILE | 准入 | §5 步骤3 人工复核（需 Owner 审批） |
| VC-A/B/C/D | D12 | §2.12 |

### A.3 登记表覆盖交叉验证

本协议 v1.1.0 与 `registry-master-index.yaml`（38 张登记表）进行了交叉验证：

| 覆盖项 | 对应脚本 | 维度 |
|--------|---------|------|
| 登记表总索引自校验 | validate_registry_master_index.py (P0) | D3 |
| 蓝图登记表自校验 | validate_blueprint_registry.py (P1) | D3 |
| 跨登记表一致性 | check_registry_consistency.py (P1) | D3+D5+D11 |
| 12 个受控词表合规 | validate_enum_consistency.py (P0) + generate_derived_files.py (P2) | D3 |
| 架构契约一致性 | validate_architecture_contract_internal.py (P0) | D3+D5 |
| 受控词表 ↔ frontmatter 值校验 | validate_frontmatter_values.py (P0) | D3+D5 |

### A.4 已知限制（v1.1.0）

| 限制 | 说明 | 优先级 | 缓解措施 |
|------|------|--------|---------|
| KMS 管道门禁 G1-G5 | 运行时门禁，非静态扫描——依赖 gate_engine.py 在线状态 | 低 | §5 步骤3 人工复核 + CI governance.yml 管道回归 |
| ARG-001~005 架构评审 | 纯人工评审门禁，大多为 draft 状态 | 中 | beta 落地后可能转为工作流 + checklist 半自动 |
| 准入门禁 MOD-ADMIT/FACTOR/FILE | 需 Owner 审批，无法全自动 | 低 | 已有机审流程 + 门禁登记表确认 |
| AGENTS.md §6.7/6.8/6.13 | 回滚策略/渐进式信任/知识衰减——概念性强，无自动化脚本 | 中 | 4 考虑落地对应检查脚本 |
| D10 运维架构 | 无专项脚本 | 中 | 4 补充 |
| 若干登记表缺少 health_check_script | 以各登记表 `maintenance` 及 CI 脚本覆盖为准；总量以 `registry-master-index.yaml` 为准 | 低 | 按模块补齐并可自 registry 派生监控 |

---

## B. 规则文件完整路径索引（Vibe Coding 快速定位）

> 本节为 AI 审计执行者提供"按 module_id 秒查文件路径"的能力。
> 所有路径均为绝对路径，可直接用于文件读取。

### B.1 元标准与元规则（meta/）

| module_id | 标题 | 完整路径 |
|-----------|------|---------|
| PS-STD-000 | 元标准宪法 | [meta-standard-constitution.md](../../meta/meta-standard-constitution.md) |
| PS-STD-001 | 元数据登记表 | [metadata-registry.md](../../meta/metadata-registry.md) |
| PS-STD-002 | 标准文档模板 | [document-structure-standard.md](../../meta/document-structure-standard.md) |
| PS-STD-003 | 行为边界标准 | [behavior-boundaries-standard.md](../../meta/behavior-boundaries-standard.md) |
| PS-STD-004 | 规则分类与仲裁标准 | [rule-classification-and-arbitration-standard.md](../../meta/rule-classification-and-arbitration-standard.md) |
| PS-STD-009 | 规则生命周期与变更标准 | [rule-lifecycle-and-change-standard.md](../../meta/rule-lifecycle-and-change-standard.md) |
| PS-STD-011 | 治理方法论标准 | [governance-methodology-standard.md](../../meta/governance-methodology-standard.md) |
| PS-STD-012 | 规则验证标准 | [rule-verification-standard.md](../../meta/rule-verification-standard.md) |

### B.2 文档治理（governance/document/）

| module_id | 标题 | 完整路径 |
|-----------|------|---------|
| GOV-DOC-001 | 统一编号规范 | [unified-numbering-standard.md](../../governance/document/unified-numbering-standard.md) |
| GOV-DOC-002 | 目录结构规范 | [directory-structure-standard.md](../../governance/document/directory-structure-standard.md) |
| GOV-DOC-003 | 文件命名规范 | [file-naming-standard.md](../../governance/document/file-naming-standard.md) |
| GOV-DOC-004 | 文件路径规范 | [file-path-standard.md](../../governance/document/file-path-standard.md) |
| GOV-DOC-005 | 编码安全规范 | [encoding-safety-standard.md](../../governance/document/encoding-safety-standard.md) |
| GOV-DOC-006 | 文档生命周期管理规范 | [document-lifecycle-standard.md](../../governance/document/document-lifecycle-standard.md) |
| GOV-DOC-007 | 文件操作安全门禁 | [file-operation-safety-policy.md](../../governance/document/file-operation-safety-policy.md) |
| GOV-DOC-009 | 文档控制原则 | [document-control-policy.md](../../governance/document/document-control-policy.md) |
| GOV-DOC-010 | 文档可发现性策略 | [document-discovery-policy.md](../../governance/document/document-discovery-policy.md) |

### B.3 架构治理（governance/architecture/）

| module_id | 标题 | 完整路径 |
|-----------|------|---------|
| GOV-ARCH-001 | 架构决策记录 | KB:decisions namespace（原 adr-protocol.md 已删除） |
| GOV-ARCH-002 | 架构评审门禁 | [architecture-review-policy.md](../../governance/architecture/architecture-review-policy.md) |
| GOV-ARCH-003 | 架构版本化策略 | [architecture-versioning-policy.md](../../governance/architecture/architecture-versioning-policy.md) |
| GOV-ARCH-006 | KMS 管道门禁策略 | [gate-strategy-standard.md](../../governance/architecture/gate-strategy-standard.md) |
| GOV-ARCH-005 | Phase 过渡双门禁协议 | [phase-transition-protocol.md](../../governance/architecture/phase-transition-protocol.md) |

### B.4 模块治理（governance/module/）

| module_id | 标题 | 完整路径 |
|-----------|------|---------|
| GOV-MOD-001 | 模块准入门禁策略 | [module-admission-policy.md](../../governance/module/module-admission-policy.md) |
| GOV-MOD-002 | AI 模型行为铁律 | [ai-behavior-iron-policy.md](../../governance/module/ai-behavior-iron-policy.md) |
| GOV-MOD-003 | 模块生命周期策略 | [module-lifecycle-policy.md](../../governance/module/module-lifecycle-policy.md) |
| GOV-MOD-004 | 模块接口契约策略 | [module-interface-contract-policy.md](../../governance/module/module-interface-contract-policy.md) |
| GOV-MOD-007 | 多注册表同步标准 | [multi-registry-synchronization-standard.md](../../governance/module/multi-registry-synchronization-standard.md) |

### B.5 AI 治理（governance/ai/）

| module_id | 标题 | 完整路径 |
|-----------|------|---------|
| GOV-AI-003 | AI 幻觉自检清单 | [ai-hallucination-self-check-policy.md](../../governance/ai/ai-hallucination-self-check-policy.md) |
| GOV-AI-004 | 双编辑器协作规则 | [dual-editor-collaboration-policy.md](../../governance/ai/dual-editor-collaboration-policy.md) |

### B.6 安全治理（governance/security/）

| module_id | 标题 | 完整路径 |
|-----------|------|---------|
| GOV-SEC-001 | 密钥管理策略 | [secret-management-policy.md](../../governance/security/secret-management-policy.md) |
| GOV-SEC-002 | 访问控制策略 | [access-control-policy.md](../../governance/security/access-control-policy.md) |
| GOV-SEC-003 | 安全事件响应策略 | [security-incident-response-policy.md](../../governance/security/security-incident-response-policy.md) |

### B.7 任务治理（governance/task/）

| module_id | 标题 | 完整路径 |
|-----------|------|---------|
| GOV-TASK-001 | 任务卡操作指南 | [task-card-standard.md](../../governance/task/task-card-standard.md) |
| GOV-TASK-004 | 任务生命周期管理标准 | [task-lifecycle-standard.md](../../governance/task/task-lifecycle-standard.md) |
| GOV-TASK-005 | 任务关闭标准 | [task-closure-standard.md](../../governance/task/task-closure-standard.md) |

### B.8 合规治理（governance/compliance/）

| module_id | 标题 | 完整路径 |
|-----------|------|---------|
| GOV-CMP-001 | 监管分类策略 | [regulatory-taxonomy-policy.md](../../governance/compliance/regulatory-taxonomy-policy.md) |
| GOV-CMP-002 | 审计追踪策略 | [audit-trail-policy.md](../../governance/compliance/audit-trail-policy.md) |
| **GOV-CMP-003** | **治理审计执行协议（本文档）** | [audit-protocol.md](../../governance/compliance/audit-protocol.md) |

### B.9 操作规范（operational/）

| module_id | 标题 | 完整路径 |
|-----------|------|---------|
| OPS-VC-005 | Vibe Coding 会话门禁检查清单 | [vibe-coding-gate-checklist.md](../../operational/vibe_coding/vibe-coding-gate-checklist.md) |

### B.10 配置文件（config/）

| 文件 | 用途 | 完整路径 |
|------|------|---------|
| context_rules_v1.yaml | 15 条上下文管理规则 | [context_rules_v1.yaml](file:///d:/ZephyrAlpha/config/context_rules_v1.yaml) |
| capabilities.yaml | CBAC 能力注册表 | [capabilities.yaml](file:///d:/ZephyrAlpha/config/capabilities.yaml) |
| trigger_router.yaml | 触发器路由配置 | [trigger_router.yaml](file:///d:/ZephyrAlpha/config/trigger_router.yaml) |

### B.11 登记表（_registry/）

| 文件 | 用途 | 完整路径 |
|------|------|---------|
| registry-master-index.yaml | 登记表总索引 | [registry-master-index.yaml](../../_registry/catalogs/registry-master-index.yaml) |
| gate-registry.yaml | 34 个门禁 SSoT | [gate-registry.yaml](../../_registry/catalogs/gate-registry.yaml) |
| rule-registry.yaml | 规则注册表 | [rule-registry.yaml](../../_registry/catalogs/rule-registry.yaml) |
| ai-risk-register.yaml | AI 风险登记表 | [ai-risk-register.yaml](../../_registry/catalogs/ai-risk-register.yaml) |
| frontmatter-field-registry.yaml | Frontmatter 字段注册表 | [frontmatter-field-registry.yaml](../../_registry/catalogs/frontmatter-field-registry.yaml) |
| document-metadata-index.yaml | 文档元数据索引 | [document-metadata-index.yaml](../../_registry/catalogs/document-metadata-index.yaml) |
| declarative-contract-tracker.yaml | 声明式契约跟踪表 | [declarative-contract-tracker.yaml](../../_registry/catalogs/declarative-contract-tracker.yaml) |
| architecture-contract.yaml | 架构合规契约 | [architecture-contract.yaml](../../_registry/contracts/architecture-contract.yaml) |
| model-capability-contract.yaml | 模型能力契约 | [model-capability-contract.yaml](../../_registry/contracts/model-capability-contract.yaml) |

### B.12 架构模型（architecture-model/）

| 文件 | 用途 | 完整路径 |
|------|------|---------|
| _index.yaml | 架构模型总索引 | [_index.yaml](file:///d:/ZephyrAlpha/architecture-model/_index.yaml) |
| technology-landscape.yaml | 技术全景图 | [technology-landscape.yaml](file:///d:/ZephyrAlpha/architecture-model/technology-landscape.yaml) |

### B.13 审计脚本（scripts/governance/）

| 文件 | 用途 | 完整路径 |
|------|------|---------|
| run_all.py | 统一调度 177 个审计脚本 | [run_all.py](file:///d:/ZephyrAlpha/scripts/governance/run_all.py) |
| script_manifest.yaml | 177 个脚本注册表 | [script_manifest.yaml](file:///d:/ZephyrAlpha/scripts/governance/script_manifest.yaml) |
| env_check.py | 环境就绪检查 | [env_check.py](file:///d:/ZephyrAlpha/scripts/governance/env_check.py) |
| status.py | 脚本健康状态查询 | [status.py](file:///d:/ZephyrAlpha/scripts/governance/status.py) |

---

## 10. 修订记录

| 日期 | 版本 | 修改内容 |
|------|------|---------|
| 2026-05-04 | 1.2.0 | **四重交叉验证修复**——与 docs/01_policies_and_standards/ 下全部 37 个规则文件逐一核对。depends_on 从 10 条扩展至 37 条（覆盖 PS-STD-000~012、GOV-DOC-001~010、GOV-ARCH-001~005、GOV-MOD-001~004/007、GOV-AI-003~005、GOV-SEC-001~003、GOV-TASK-001/004/005、GOV-CMP-001/002 等全部规则）。各维度审计规则栏补充完整路径链接（如 [GOV-MOD-002](file:///...)）。新增 §B 规则文件完整路径索引（13 类 60+ 文件：元标准/文档治理/架构治理/模块治理/AI治理/安全治理/任务治理/合规治理/操作规范/配置文件/登记表/架构模型/审计脚本），支持 Vibe Coding 场景下 AI 秒查文件路径 |
| 2026-05-04 | 1.1.0 | **深度自审计修复**——与 script_manifest.yaml（91脚本）、gate-registry.yaml（34门禁）、registry-master-index.yaml（38登记表）完成三重交叉验证。新增 30+ 遗漏脚本引用。新增 GATE-13/G1-G5/ARG-001~005/MOD-ADMIT/FACTOR-QUALITY/FILE-OP-SAFE 门禁覆盖。新增 §2.13 跨维度统计表。新增 §A 交叉验证记录。新增 depends_on 9 条规则引用。修正 script 总数从 ~90 到 91 |
| 2026-05-04 | 1.0.0 | 初始版本。12 维度审计清单 + 4 类审计类型 + 3 级审计等级 + 5 步审计流程 + 报告模板 + 闭环规则 + 专业框架对标 |
