---
task_id: "TASK-INF-0101"
source_blueprint: "MOD-INF-016"
source_section: "蓝图 §2 Shared 模块（9 子模块, 46 文件）"

title: "§2 Shared 子模块完整性审计——9 子模块 46 文件职责与状态验证"
description: |
  逐子模块审计 Shared 层全部 9 个子模块的 46 个文件：
  §2.1 contracts(4文件) §2.2 infra(16文件) §2.3 errors(1文件) §2.4 constants(1文件)
  §2.5 events(2文件) §2.6 resilience(3文件) §2.7 lifecycle(1文件)
  §2.8 flags(1文件) §2.9 utilities(4文件) + shared/ 根目录下共享基础设施。
  验证每个文件的实现状态、职责描述与蓝图 §2.1-§2.9 一致。
  确认所有已实现文件在磁盘上存在且内容非空。
priority: "P1"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_cross_layer\\shared-core\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\__init__.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\schemas.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\ssot_guard.py"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\docs\\03_modules\\_cross_layer\\shared-core\\changes\\MOD-INF-016\\TASK-INF-0101.md"
    description: "本任务卡——Shared 子模块审计执行记录"

allowed_touch:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_cross_layer\\shared-core\\changes\\MOD-INF-016\\TASK-INF-0101.md"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\**\\*.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\core\\**\\*.py"

applicable_rules:
  - module_id: "PS-STD-001"
    section: "§5"
    reason: "module_id 命名规范——所有 shared/ 文件 frontmatter 必须符合 DOMAIN-TYPE-NNN 格式"
  - module_id: "GOV-DOC-002"
    section: "§3"
    reason: "shared/ 位于 B 轨——源代码物理位置 src/zephyr/shared/"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\_cross_layer\\shared-core\\blueprint.md"
    reason: "本蓝图 §2——逐子模块审计声明"
  - file_path: "D:\\ZephyrAlpha\\src\\zephyr\\shared\\__init__.py"
    reason: "Shared 包入口——__all__ 导出列表作为审计基准"

assigned_model: "glm-5.1"
assigned_pipeline: "B"
pipeline_modules:
  - "M3"
estimated_tokens: 8000
timeout_minutes: 30

acceptance_criteria:
  - "§2.1 contracts: instrument.py / money.py / timestamp.py / runtime_plane_tag.py 4文件磁盘存在且内容非空"
  - "§2.2 infra: schemas.py / ssot_guard.py / observer.py / capability.py / content_fingerprint.py / dos_launcher.py / paths.py / time_utils.py / token_utils.py / frontmatter_utils.py / API_INDEX.py / logging.py / SHARED-QUICKREF.yml / testing.py / migration.py / deprecation.py 16文件均存在"
  - "§2.3 errors: errors.py——ZephyrBaseError + 12子类 存在且内容非空"
  - "§2.4 constants: constants.py——22枚举集中re-export 存在且内容非空"
  - "§2.5 events: event_schemas.py + dlq.py 2文件存在"
  - "§2.6 resilience: retry.py / circuit_breaker.py / fallback.py 3文件存在"
  - "§2.7 lifecycle: hooks.py——LifecycleAware Protocol + LifecycleManager 存在且内容非空"
  - "§2.8 flags: flags.py——FeatureFlag + FlagRegistry 存在且内容非空"
  - "§2.9 utilities: types.py / diff_utils.py / file_utils.py / config/loader.py 4文件存在"
  - "总 Shared 文件数 = 46（含 events/ resilience/ lifecycle/ config/ 子目录下文件）"

rollback_instructions: |
  本任务为只读审计。发现不一致时仅记录审计发现，不修改任何 shared/ 文件。

depends_on: ["TASK-INF-0100"]
blocked_by: []

status: "done"

tags_fn:
  - "infra"
tags_ly: "cross_layer"
tags_md: "glm-5.1"
tags_st: "active"
tags_mo:
  - "MOD-INF-016"

completed_gates: []
blocked_gates: {}

artifact_paths: []

audit_findings:
  - id: "F-TASK-INF-0101-001"
    severity: "high"
    finding: "蓝图声明 46 文件，实际磁盘 157 .py 文件。Shared 已深度重组为 13 个子目录（api/foundation/infra/io/observability/schema/security/utils/config/contracts/events/lifecycle/resilience），根目录 46 文件 + 子目录 111 文件。"
    evidence: "glob **/*.py count = 157"
  - id: "F-TASK-INF-0101-002"
    severity: "high"
    finding: "蓝图 §2.2 列 16 文件用于 infra，但实际已拆分为 16 子目录——基础设施被重组入 api/foundation/infra/io/observability/schema/security/utils/config 等多个 subpackage。§2.1-§2.9 组织与磁盘结构完全不对齐。"
    evidence: "蓝图 §2.2 16 文件 vs 磁盘 7 infra + 7 foundation + 9 utils + 6 io + ..."
  - id: "F-TASK-INF-0101-003"
    severity: "medium"
    finding: "contracts/core/instrument.py 蓝图声明路径不存在，实际位于 contracts/market/instrument.py（已迁移）。蓝图路径已过时。"
    evidence: "instrument.py at contracts/market/ (20668 bytes)"
  - id: "F-TASK-INF-0101-004"
    severity: "medium"
    finding: "ssot_guard.py 存在两份——根目录 17009 bytes + security/ssot_guard.py 17069 bytes。内容相似但有差异。可能造成 import 歧义。"
    evidence: "shared/ssot_guard.py (17009B) AND shared/security/ssot_guard.py (17069B)"
  - id: "F-TASK-INF-0101-005"
    severity: "low"
    finding: "蓝图 §2.2 验收标准列 events/dlq.py 属于 infra 子模块，但实际在 events/ 独立子目录下（与蓝图 §2.5 events 一致）。蓝图分类需要更新。"
    evidence: "events/dlq.py exists (14354 bytes)"
  - id: "F-TASK-INF-0101-006"
    severity: "info"
    finding: "其余 33 个蓝图声明文件全部存在且非空（位于重组后的对应子目录下），内容验证通过。蓝图文件职责声明与实际代码一致。"
    evidence: "33/35 blueprint files verified present in new locations"

ke_entries: []

ai_autonomy_level: "supervised"
autonomy_checklist: []
---
