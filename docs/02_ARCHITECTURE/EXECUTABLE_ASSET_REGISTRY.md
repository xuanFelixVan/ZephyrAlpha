---
module_id: EXECUTABLE_ASSET_REGISTRY
version: 1.1.0
status: Active
created_date: 2026-04-16
last_updated: 2026-04-17
owner: AI Assistant
layer: cross_layer
---

# ZephyrAlpha 可执行资产清单 (Executable Asset Registry)

> **真源说明**：本文件是全库治理脚本、审计工具、CI/CD 工作流及 Pre-commit 钩子的权威清单。
> **AI 必读**：在创建任何新脚本或执行治理任务前，必须先在此检索现有工具。

---

## 一、术语 → 工具映射表 (Terminology Mapping)

当你想执行以下任务时，请使用对应的工具：

| 任务关键词 | 推荐工具/脚本 | 核心职责 |
|-----------|--------------|---------|
| **Sentinel / 哨兵** | `scripts/audit/sentinel_l1_governance_scan.py` | 全库链接可达性 + `module_id` 重复扫描 (L1) |
| **Orphan / 孤儿文件** | `scripts/audit/scan_index_health.py` | 查找未被任何 INDEX 引用的 Markdown 文件 |
| **Duplicate / 重复内容** | `scripts/audit/scan_duplicate_file_content.py` | 基于 SHA256 哈希检测文件内容重复 |
| **Collision / 命名碰撞** | `scripts/audit/scan_basename_collisions.py` | 查找不同路径下的同名文件 (Basename) |
| **Module ID 重复分析** | `scripts/audit/analyze_dup_module_ids.py` | 分析并消解 `module_id` 重复冲突 |
| **Module ID 批量补全** | `scripts/governance/backfill_missing_module_id.py` | 为缺失 `module_id` 的文件补全（支持 dry-run）|
| **Blueprint / 蓝图校验** | `scripts/hooks/validate_blueprint_frontmatter.py` | 校验蓝图元数据完整性 (Priority, Status 等) |
| **Link / 链接修复** | `scripts/audit/fix_dead_links.py` | 批量修复由 Sentinel 扫描出的死链 |
| **Registry / 注册表** | `scripts/governance/generate_blueprint_registry.py` | 从蓝图提取信息并更新 YAML 注册表 |
| **Subsystem / 子系统** | `scripts/governance/scan_subsystem_duplicates.py` | 检测 `docs/` 下的冗余或幽灵子系统 |
| **D 类蓝图重叠分档** | `scripts/audit/triage_blueprint_d_overlap_pairs.py` | 按评分分档（TIER_A/B/C），第一步 |
| **D 类蓝图二审包** | `scripts/governance/triage_blueprint_d_overlap_pairs.py` | 生成 TIER_B 内容摘要 JSONL，第二步 |

---

## 二、活跃治理与审计脚本 (Active Scripts)

### 2.1 审计辅助工具 (`scripts/audit/`)

| 脚本名称 | 功能描述 | 调用建议 |
|---------|---------|---------|
| `sentinel_l1_governance_scan.py` | 核心治理扫描器，检查链接、元数据、重复 ID | 每日/提交前运行 |
| `scan_index_health.py` | 索引健康度，识别孤儿文件（零入链文档）| 维护目录结构时运行 |
| `scan_duplicate_file_content.py` | 内容级去重（SHA256 哈希）| 大规模清理前运行 |
| `scan_basename_collisions.py` | 文件名碰撞检测（不同路径同名）| 移动文件前运行 |
| `fix_dead_links.py` | 自动修复死链 | 配合 Sentinel 运行 |
| `analyze_dup_module_ids.py` | 深度分析 `module_id` 冲突 | 修复元数据混乱时运行 |
| `dedupe_active_module_ids.py` | 消解活跃文件中的重复 `module_id` | 分析后执行修复 |
| `dedupe_archive_module_ids.py` | 消解归档相关重复 `module_id`（`--mode mixed` 或 `archive-only`，合并原 archive-only 脚本） | 分析后执行修复 |
| `triage_blueprint_d_overlap_pairs.py` | D 类蓝图评分分档（TIER_A/B/C）**第一步** | 蓝图重叠处理流程 |
| `report_orphan_files.py` | 孤儿文件决策报告 | 清理孤儿文件前运行 |
| `report_basename_collisions.py` | Basename 碰撞决策报告 | 清理碰撞前运行 |
| `resolve_orphan_files.py` | 执行孤儿文件解决方案 | Owner 确认后运行 |
| `resolve_basename_collisions.py` | 执行 Basename 碰撞解决方案 | Owner 确认后运行 |
| `mandatory_inbound_guard.py` | pre-commit 强制入链守卫 | pre-commit 触发 |

### 2.2 常驻治理工具 (`scripts/governance/`)

| 脚本名称 | 功能描述 | 调用建议 |
|---------|---------|---------|
| `backfill_missing_module_id.py` | 批量补全缺失的 `module_id`（支持 `--dry-run` 和 `--apply`）| 治理存量文件时运行 |
| `generate_blueprint_registry.py` | 从蓝图 frontmatter 提取并维护注册表 | 修改蓝图后运行 |
| `verify_manifest_paths_strict.py` | 校验系统清单路径准确性 | 更新清单后运行 |
| `scan_subsystem_duplicates.py` | 子系统目录一致性检查 | 调整 docs 结构时运行 |
| `scan_basename_collisions.py` | （与 audit/ 同功能，audit/ 版为权威）| 使用 audit/ 版 |
| `triage_blueprint_d_overlap_pairs.py` | 提取文档摘要，生成二审 JSONL **第二步** | 蓝图重叠处理流程 |
| `backfill_blueprint_priority.py` | 为缺失 priority 字段的蓝图批量补全 | 蓝图格式整顿时运行 |
| `diagnose_blueprint_layer_mismatch.py` | 诊断蓝图 layer 字段与实际内容的不一致 | 层级梳理时运行 |
| `verify_01_blueprints_index_links.py` | 校验蓝图 INDEX.md 内链有效性 | 更新索引后运行 |
| `generate_architecture_service_catalog.py` | 生成架构服务目录 + C4 视图 | 架构文档更新时运行 |
| `export_repo_directory_rollup.py` | 按目录前缀聚合路径数量统计 | 定期统计仓库结构 |
| `sample_docs_nav_coverage.py` | 抽样检查文档是否出现在导航中 | 导航完整性审查 |
| `consolidate_audit_standards.py` | 合并/对齐审计标准文档结构 | 标准目录整理时 |
| `trace_file_provenance.py` | 追溯文件来源与搬迁历史 | 删改高风险文件前 |
| `generate_project_health_dashboard.py` | 生成项目健康度仪表盘数据 | 周期性治理报告 |

---

## 三、Pre-commit 钩子（与 `.pre-commit-config.yaml` 逐项对应）

这些钩子在 `git commit` 时自动触发；下表 **entry** 列为 `.pre-commit-config.yaml` 中的可执行入口。

| Hook ID（节选） | entry | 检查项 / 职责 |
|----------------|-------|--------------|
| `validate-version-metadata` | `src/utils/validate_version_metadata.py` | 全库版本元数据阈值 |
| `check-version-in-filename` | `src/utils/validate_version_metadata.py` | 文件名版本信息 |
| `check-metadata-required-fields` | `src/utils/validate_version_metadata.py` | frontmatter 必选字段 |
| `check-document-placement` | `scripts/hooks/check_document_placement.py` | 根目录杂散文档放置 |
| `check-index-integrity` | `scripts/hooks/check_index_integrity.py` | 配置目录列表内索引存在性 |
| `doc-guard-pre-commit` | `scripts/hooks/doc_guard_pre_commit.py` | 文档缺陷防护（D-01/D-02 等）|
| `check-file-naming` | `scripts/hooks/doc_guard_pre_commit.py` | 文件命名规范 C-10 |
| `check-directory-naming` | `scripts/hooks/check_directory_naming.py` | 目录命名规范 D-07 |
| `source-guard` | `scripts/hooks/source_guard_pre_commit.py` | 双 YAML / module_id / frontmatter |
| `mandatory-inbound-guard` | `scripts/audit/mandatory_inbound_guard.py` | 新 md 强制入链 |
| `check-index-links` | `scripts/hooks/check_index_links.py` | INDEX 相对死链 G-02 |
| `check-related-documents` | `scripts/hooks/check_related_documents.py` | parent/related 路径存在性 |
| `check-standards-index-registration` | `scripts/hooks/check_standards_index_registration.py` | STANDARDS 新文件须登记 INDEX |
| `check-body-script-refs` | `scripts/hooks/check_body_script_refs.py` | 正文幽灵脚本命令 |
| `check-tdr-propagation` | `scripts/hooks/check_tdr_propagation.py` | TDR 变更联动暂存 |
| `check-directory-budget` | `scripts/hooks/check_directory_budget.py` | Write Gate 目录预算 + 文件名版本号 |
| `governance-health-snapshot` | `scripts/hooks/pre-commit-governance-check.py` | Sentinel L1 阈值门禁 |
| `validate-blueprint-frontmatter` | `scripts/hooks/validate_blueprint_frontmatter.py` | 蓝图 frontmatter 完整性 |
| `check-subsystem-registry` | `scripts/governance/scan_subsystem_duplicates.py` | 新建子目录须在 subsystem-registry 登记 |

> 另含 `pre-commit-hooks` 仓库的 `trailing-whitespace`、`end-of-file-fixer`、`check-yaml` 等社区钩子，无本仓库脚本路径。

---

## 四、CI/CD 工作流 (`.github/workflows/`)

### 4.1 当前活跃 Workflow（推荐使用）

| 工作流文件 | 触发条件 | 核心任务 |
|-----------|---------|---------|
| `governance-audit.yml` | PR / Push to main + `docs/**` | 运行 Sentinel L1 门禁校验 |
| `eternal-index-validation.yml` | 每小时 Cron | 验证全库索引编译与孤儿率 (<5%) |
| `periodic-audit.yml` | 周/月/季度 Cron | 执行深度审计报告生成 |
| `version-validation.yml` | Push | 版本元数据校验 |
| `code-quality.yml` | Push | 代码质量检查 |

### 4.2 遗留 Workflow（待清理，勿新增依赖）

> 以下 workflow 调用 `scripts/ci_audit/` 下已归档的旧脚本，且部分报告写入废弃路径。不会立即删除（保留历史兼容性），但禁止在新脚本中引用它们。

| 工作流文件 | 问题说明 |
|-----------|---------|
| `document_audit.yml` | 调用 `scripts/ci_audit/weekly_audit_optimized.py`（已归档）|
| `document_quality_check.yml` | 调用 `scripts/ci_audit/ci_cd_link_checker.py`（已归档），报告写入废弃路径 `04_OPERATIONS/audit_state/` |

---

## 五、工具类与模块 (`src/utils/`)

各模块职责明确，互不重叠：

| 模块名称 | 职责层次 | 备注 |
|---------|---------|-----|
| `link_validator.py` | 底层库：链接解析与验证类 | 供 hooks 和 audit 脚本调用 |
| `document_governance_checker.py` | 底层库：文档治理五大原则检查逻辑 | 核心校验逻辑 |
| `validate_version_metadata.py` | 底层库：版本元数据验证逻辑 | 供钩子调用 |
| `enhance_metadata.py` | 工具：元数据增强（补全缺失字段）| 与 `backfill_missing_module_id.py` 功能互补 |
| `migrate_version_metadata.py` | 工具：版本元数据迁移 | 格式迁移时使用 |

---

## 六、Phase 2 裁决记录 (2026-04-16)

以下是对原报告中识别的 6 处重复的正式裁决结果：

| 重复情况 | 裁决结论 | 具体操作 |
|---------|---------|---------|
| `audit/triage_` vs `governance/triage_`（同名不同功）| **保留两者**，功能不同：audit/ 版分档，governance/ 版生成二审包 | 在两个脚本头部添加了协作说明注释 |
| `audit/add_missing_module_ids.py` vs `governance/backfill_missing_module_id.py` | **audit/ 版降级为归档**，前者硬编码依赖特定快照文件（一次性脚本），后者为通用工具 | 已将 audit/ 版移入 `scripts/archive/` |
| `audit/scan_index_health.py` vs `audit/strict_orphan_inbound_scan.py` | **strict_orphan_inbound_scan.py 降级为归档**，其为简易脚本（功能子集），scan_index_health 为产品级工具 | 已将 strict_orphan 版移入 `scripts/archive/` |
| 链接验证三重实现（sentinel / link_validator / hooks）| **三者保留，职责分工明确**：sentinel 是全库扫描，link_validator 是底层库，hooks 是提交门禁 | 在本清单中标注分工 |
| 元数据验证三处（hooks / option_b / src/utils）| **三者保留，职责分工明确**：hooks 是门禁，option_b 是统计报告，utils 是底层库 | 在本清单中标注分工 |
| CI Workflow `document_audit.yml` + `document_quality_check.yml` | **标注为遗留 Workflow**，调用已归档脚本，禁止新建依赖 | 在本清单 § 4.2 中标注 |

---

## 六-B、补充登记：CI 审计脚本 (`scripts/ci_audit/`)（2026-04-16 补录）

> 以下脚本在 `.github/workflows/periodic-audit.yml` 中被调用，均为活跃状态。

| 脚本名称 | 功能描述 | 调用场景 |
|---------|---------|---------|
| `monthly_audit.py` | 月度审计报告生成 | `periodic-audit.yml` 月度任务 |
| `quarterly_audit.py` | 季度深度审计报告生成 | `periodic-audit.yml` 季度任务 |
| `blueprint_validator.py` | 蓝图结构与元数据批量校验 | `periodic-audit.yml` 季度任务 |
| `architecture_analyzer.py` | 架构健康度分析 | `periodic-audit.yml` 月度任务 |
| `documentation_debt_assessor.py` | 文档债务量化评估 | `periodic-audit.yml` 季度任务 |
| `link_checker.py` | CI/CD 链接有效性检查 | `periodic-audit.yml` 月度任务 |
| `generate_quality_report.py` | 文档质量评分报告 | CI 触发 |
| `boundary_checker.py` | 层级边界合规检查 | CI 触发 |
| `check_compliance_rate.py` | 规范符合率统计 | CI 触发 |
| `yaml_metadata_checker.py` | YAML frontmatter 批量校验 | CI 触发 |
| `document_structure_checker.py` | 文档结构完整性检查 | CI 触发 |
| `duplicate_detector.py` | 文档内容重复检测（ci_audit 版本） | CI 触发 |

**注意**：`ci_cd_link_checker.py` 和 `weekly_audit_optimized.py` 属于遗留脚本（见 §4.2），调用已废弃路径，不可新建依赖。

---

## 六-C、补充登记：审计工具补充 (`scripts/audit/`)（2026-04-16 补录）

| 脚本名称 | 功能描述 | 调用建议 |
|---------|---------|---------|
| `purge_expired_state.py` | 清理过期的状态文件（基于 TTL 策略）| 定期维护时运行 |
| `check_frontmatter_completeness.py` | 批量检查文档 frontmatter 完整性 | 存量文件审计时运行 |
| `scan_directory_naming_compliance.py` | 目录命名合规扫描（大写/下划线规范）| 调整目录结构前运行 |
| `option_b_frontmatter_scan.py` | frontmatter 覆盖率统计（统计报告版本）| 周期报告时运行 |
| `scan_blueprint_d_overlap_candidates.py` | D 类蓝图重叠候选识别（前置步骤）| `triage_blueprint_d_overlap_pairs.py` 之前运行 |
| `resolve_tier_a_overlaps.py` | TIER_A 已确认重叠的自动消解 | 蓝图重叠处理流程 |
| `audit_10_dimensions_script.py` | 10 维度蓝图质量评分脚本 | 蓝图批量评估时运行 |
| `audit_10d_scan.py` | 10 维度快速扫描（简化版）| 快速审计时运行 |
| `audit_detail_scan.py` | 单文件详细审计扫描 | 深度分析单个文档时运行 |
| `scanner.py` | 基础扫描器（底层组件，被其他脚本导入）| 不直接调用 |
| `temp_scan_module_ids.py` | 临时 module_id 扫描（deprecated 候选）| 标记为废弃，用 `analyze_dup_module_ids.py` 替代 |

---

## 六-D、补充登记：治理工具补充 (`scripts/governance/`)（2026-04-16 补录）

| 脚本名称 | 功能描述 | 调用建议 |
|---------|---------|---------|
| `consolidate_audit_standards.py` | 审计标准文档整合工具 | 标准合并时运行 |
| `trace_file_provenance.py` | 文件溯源分析（来源/历史路径）| 调查文件来历时运行 |
| `generate_project_health_dashboard.py` | 生成项目健康仪表盘（P0 缺失，待激活）| 定期运行（当前 P0 缺失状态）|
| `generate_01_blueprints_index.py` | 自动生成 01_FRAMEWORK 蓝图索引 | 蓝图批量变更后运行 |
| `generate_scattered_blueprints_manifest_task1.py` | Task 1：生成散落蓝图清单 | 蓝图迁移流水线 |
| `verify_scattered_blueprints_manifest_links.py` | 验证散落蓝图清单中的链接有效性 | 蓝图迁移流水线 |
| `hook_support.py` | hooks 公共支持库（不直接调用）| 被 hooks/ 脚本导入 |

---

## 六-E、补充登记：根目录历史脚本（deprecated 候选）（2026-04-16 补录）

> 以下脚本是历史上一次性任务遗留在 `scripts/` 根目录，均为潜在 deprecated 候选。
> **标记**：带 `temp_` 前缀为推荐处置方式（归档），下次清理 Wave 中处理。

| 脚本 | 推测用途 | 建议处置 |
|------|---------|---------|
| `index_compiler.py` | 索引编译器入口（CI 使用）| **保留**，在 `eternal-index-validation.yml` 中调用 |
| `sync_authority_source.py` | 权威来源同步（历史一次性）| 归档候选 |
| `integrate_p0_blueprints.py` | P0 蓝图集成（历史一次性）| 归档候选 |
| `integrate_layer_directories.py` | Layer 目录整合（历史一次性）| 归档候选 |
| `execute_phase1_cleanup.py` | Phase 1 清理（历史一次性）| 归档候选 |
| `disaster_recovery.py` | 灾难恢复脚本（紧急用途）| 保留（备用）|
| `cleanup_low_risk_directories.py` | 低风险目录清理（历史一次性）| 归档候选 |
| `analyze_and_fix_folder_structure.py` | 文件夹结构分析（历史一次性）| 归档候选 |
| `merge_blueprints.py` | 蓝图合并（历史一次性）| 归档候选 |
| `extract_implementation_details.py` | 实现细节提取（历史一次性）| 归档候选 |
| `comprehensive_system_cleanup_analysis.py` | 系统清理分析（历史一次性）| 归档候选 |

---

## 七、归档脚本说明 (`scripts/archive/`)

> **警告**：`scripts/archive/` 下的脚本已废弃或处于待命状态（共 692 个文件）。
> **AI 行为准则**：若搜索命中 archive/ 下的脚本，必须先查本清单确认是否有活跃替代工具。禁止直接运行归档脚本。

| 归档脚本模式 | 活跃替代工具 |
|-------------|-------------|
| `link_fixer.py`, `link_checker.py`, `smart_link_fixer.py` 等 | `scripts/audit/fix_dead_links.py` |
| `duplicate_detector.py`, `detect_duplicate_documents.py` 等 | `scripts/audit/scan_duplicate_file_content.py` |
| `weekly_audit_*.py`, `audit_scheduler.py` 等 | `.github/workflows/periodic-audit.yml` |
| `round*_issue_fixer.py`, `p0_issue_fixer.py` 等 | 对应问题域的最新活跃脚本（见本清单 §2）|
| `add_missing_module_ids.py`（2026-04-16 移入）| `scripts/governance/backfill_missing_module_id.py` |
| `strict_orphan_inbound_scan.py`（2026-04-16 移入）| `scripts/audit/scan_index_health.py` |
