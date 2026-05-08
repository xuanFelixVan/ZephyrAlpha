---
module_id: "MOD-INF-023"
title: "漂移运行时检测蓝图 — Git-native Drift Detection + 自动对账 + AI 施工专项 + 漂移预算与溯源"
doc_type: blueprint
status: Active
version: "1.0.1"
layer: cross_layer
owner: ZephyrAlpha-Owner
classification: confidential
language: zh
created_by: human_plus_agent
date: "2026-05-05"
valid_from: "2026-05-05"
ttl: permanent
construction_progress: operational
belongs_to: "MOD-MASTER-001"
summary: "ZephyrAlpha 漂移运行时检测蓝图——基于 git diff + YAML 对比的运行时漂移检测。整合现有 80+ 治理脚本为运行时检测 + 自动对账（可自动修复的漂移自动修，不可自动修复的生成修复建议）。增加基线快照、漂移状态机、时序趋势分析、AI 施工场景专项检测器（幻觉引用/跨Session不一致/死码/知识污染/重复造轮子）。对标 Terraform drift detection + K8s reconciliation loop + OPA decision trace + Datadog anomaly detection。"
tags: [drift-detection, reconciliation, runtime-check, consistency, git-native, infrastructure, ai-engineering, self-healing]
priority: P1
depends_on:
  - {target: "MOD-INF-007", at: "§5", why: "Gate Engine——漂移检测作为 G1 门禁的增强"}
  - {target: "MOD-INF-021", at: "§2", why: "Rollback——漂移修复失败时自动回滚"}
references:
  - {id: "MOD-INF-020", at: "§2", why: "审计写入——仅存 references"}
  - {target: "feedback_loop/evolution_engine.py", at: "§1", why: "Evolution Engine——漂移模式反向优化蓝图设计"}
---

## DOM-GOV-001 集成契约锚点

> 权威定义见 [`../../_domain-governance/blueprint.md`](../../_domain-governance/blueprint.md) §3。

| 契约 ID | 本模块角色 | 对端模块 |
|---------|------------|----------|
| G-CT-005 | 产出方（漂移信号 → Rollback） | MOD-INF-021 |

# 漂移运行时检测蓝图 — Git-native Drift Detection + AI 施工专项

> **module_id**: MOD-INF-023 | **version**: 0.3.0 | **status**: draft | **layer**: cross_layer

> **对标**：Terraform drift detection（`terraform plan -detailed-exitcode`）+ K8s controller reconciliation loop + OPA decision trace + Datadog anomaly detection + Backstage Catalog entity validation。

---

## 1. 概述与模块定位

### 1.1 模块身份

| 属性 | 值 |
|------|-----|
| module_id | MOD-INF-023 |
| 代码落位 | `src/zephyr/drift_detector/` |
| 运行时平面 | Warm memory（git commit 后触发 + 定期轮询 + MCP on-demand） |
| 核心职责 | 检测"蓝图声明"与"代码实际"的偏差——持续对账，自动修复，趋势分析，反馈进化 |
| 运行上下文 | 100% AI 施工 + 1人维护——需覆盖 AI 特有漂移模式 |

### 1.2 核心职能（一句话）

**Drift Detector 是系统的质检员 + 趋势分析师**——基于 git diff 与基线快照，持续检查蓝图、代码、配置三者的一致性。能自动修的自动修，不能的生成修复建议。漂移事件形成时序数据库，关联分析反馈到蓝图进化引擎。

### 1.3 运行场景约束

| 约束 | 影响 |
|------|------|
| 先干后验模式 | 漂移检测是后验的核心组件——AI 先干，drift detector 后验 |
| 80+ 现有治理脚本 | 不重写，整合为运行时检测的检测器 |
| 能自动绝不人工 | 可自动修复的漂移自动修，不可自动修复的生成修复建议 |
| 100% AI 施工 | 需覆盖 AI 特有的漂移模式：幻觉引用、跨 session 不一致、死码积累、知识污染 |
| 1人+AI 维护 | 检测器必须自己能发现自己的问题（自漂移检测），Owner 只看摘要 |

### 1.4 双轨约束

本模块遵循 AGENTS.md 定义的架构治理铁律：
- **双轨制**：YAML 检测器注册表为机器 SSoT，本 MD 为人类视图。冲突以 YAML 为准。
- **双层对齐闸门**：GATE-A（蓝图 YAML vs MD 视图对齐）+ GATE-B（蓝图 vs 代码对齐）。本模块为 GATE-B 的运行时执行体。

---

## 2. 核心架构

### 2.1 检测器注册表与维度清单（决策 D-023-01）

> **决策 D-023-01**：不重写检测逻辑，将现有 80+ 治理脚本整合为 drift detector 的检测器。新增检测器以声明式 YAML 注册，drift detector 负责动态发现、调度和汇总。
>
> **决策依据**：80+ 脚本已经覆盖了大部分漂移检测场景，重写是浪费。新增检测维度不应要求写 Python，声明式注册即可。

**检测器注册机制**：

```yaml
# _detector_registry.yaml — 声明式检测器注册表（机器 SSoT）
detectors:
  existing:
    - id: "blueprint_code_sync"
      script: "validate_blueprint_code_sync.py"
      drift_dimension: "D5_blueprint_code_sync"
      check_dims: ["D5", "D8"]
      severity: HIGH
      category: architecture

    - id: "code_yaml_alignment"
      script: "validate_code_yaml_alignment.py"
      drift_dimension: "D5_yaml_disk_sync"
      check_dims: ["D5"]
      severity: MEDIUM
      category: consistency

    - id: "static_manifest_drift"
      script: "validate_static_manifest_drift.py"
      drift_dimension: "D5_static_manifest"
      check_dims: ["D5"]
      severity: HIGH
      category: generators

    - id: "md_yaml_number_drift"
      script: "validate_md_yaml_number_drift.py"
      drift_dimension: "D3_D5_number_drift"
      check_dims: ["D3", "D5"]
      severity: HIGH
      category: consistency

    - id: "blueprint_implementation_docs"
      script: "validate_blueprint_implementation_docs.py"
      drift_dimension: "D5_implementation_docs"
      check_dims: ["D5"]
      severity: HIGH
      category: documentation

    - id: "three_way_consistency"
      script: "validate_three_way_consistency.py"
      drift_dimension: "D5_three_way"
      check_dims: ["D5"]
      severity: HIGH
      category: consistency

    - id: "ssot"
      script: "validate_ssot.py"
      drift_dimension: "D5_ssot"
      check_dims: ["D5"]
      severity: HIGH
      category: authority

    - id: "module_lifecycle"
      script: "validate_module_lifecycle.py"
      drift_dimension: "D5_lifecycle"
      check_dims: ["D5"]
      severity: MEDIUM
      category: lifecycle

    - id: "layer_deps"
      script: "validate_layer_deps.py"
      drift_dimension: "D4_layer_deps"
      check_dims: ["D4"]
      severity: HIGH
      category: architecture

    - id: "cross_references"
      script: "validate_cross_references.py"
      drift_dimension: "D5_cross_refs"
      check_dims: ["D5"]
      severity: MEDIUM
      category: consistency

    - id: "depends_on_format"
      script: "validate_depends_on_format.py"
      drift_dimension: "D5_depends_on"
      check_dims: ["D5"]
      severity: MEDIUM
      category: consistency

    - id: "interface_contracts"
      script: "validate_interface_contracts.py"
      drift_dimension: "D5_contracts"
      check_dims: ["D5"]
      severity: HIGH
      category: contracts

    - id: "directory_structure"
      script: "validate_directory_structure.py"
      drift_dimension: "D5_directory"
      check_dims: ["D5"]
      severity: MEDIUM
      category: structure

    - id: "deprecated_dependents"
      script: "validate_deprecated_dependents.py"
      drift_dimension: "D5_deprecated"
      check_dims: ["D5"]
      severity: HIGH
      category: lifecycle

    - id: "gate_yaml"
      script: "validate_gate_yaml.py"
      drift_dimension: "D5_gate_yaml"
      check_dims: ["D5"]
      severity: HIGH
      category: gates

    - id: "p0_module_contracts"
      script: "validate_p0_module_contracts.py"
      drift_dimension: "D5_p0_contracts"
      check_dims: ["D5"]
      severity: HIGH
      category: contracts

    - id: "architecture_contract_internal"
      script: "validate_architecture_contract_internal.py"
      drift_dimension: "D5_arch_contracts"
      check_dims: ["D5"]
      severity: HIGH
      category: contracts

    - id: "handoff_package"
      script: "validate_handoff_package.py"
      drift_dimension: "D5_handoff"
      check_dims: ["D5"]
      severity: MEDIUM
      category: process

  new:
    - id: "ai_hallucination_import"
      drift_dimension: "AI_import_hallucination"
      severity: HIGH
      category: ai_engineering
      method: "AST 解析所有 import/from 语句 → 交叉验证目标模块是否真实存在"
      status: "待实现"
      auto_fixable: false

    - id: "ai_dead_code"
      drift_dimension: "AI_dead_code"
      severity: MEDIUM
      category: ai_engineering
      method: "AST 分析：定义但未调用的函数/类、声明但未使用的变量"
      status: "待实现"
      auto_fixable: false

    - id: "ai_broken_logic"
      drift_dimension: "AI_broken_logic"
      severity: HIGH
      category: ai_engineering
      method: "检测 NotImplementedError 无 fallback、TODO 占比过高、上下文截断签名（函数签名与实现体不匹配）"
      status: "待实现"
      auto_fixable: false

    - id: "ai_duplicate_functionality"
      drift_dimension: "AI_duplicate_code"
      severity: MEDIUM
      category: ai_engineering
      method: "AST 级别函数签名相似度（Jaccard）+ 跨模块查重"
      status: "待实现"
      auto_fixable: false

    - id: "ai_session_style_drift"
      drift_dimension: "AI_style_drift"
      severity: LOW
      category: ai_engineering
      method: "检测跨模块/跨 session 的代码风格不一致（dataclass vs pydantic / sync vs async / 命名规范）"
      status: "待实现"
      auto_fixable: false

    - id: "ai_knowledge_pollution"
      drift_dimension: "AI_deprecated_api"
      severity: MEDIUM
      category: ai_engineering
      method: "代码中引用的库 API → 与最新版本 API 交叉对比，标记已废弃用法"
      status: "待实现"
      auto_fixable: false

    - id: "contract_implementation"
      drift_dimension: "D5_contract_implementation"
      severity: HIGH
      category: contracts
      method: "AST 级对比——蓝图 §3 接口 vs 代码实际接口签名"
      status: "待实现"
      auto_fixable: false

    - id: "semantic_drift"
      drift_dimension: "D5_semantic"
      severity: HIGH
      category: semantics
      method: "YAML 之间语义一致性——同一概念的枚举值/数量/命名在两个 YAML 中是否矛盾"
      status: "待实现"
      auto_fixable: false

    - id: "db_schema_drift"
      drift_dimension: "D5_db_schema"
      severity: HIGH
      category: database
      method: "SQLite schema vs ORM model vs migration 文件三方对账"
      status: "待实现"
      auto_fixable: false

    - id: "dep_version_drift"
      drift_dimension: "D5_dep_version"
      severity: MEDIUM
      category: dependencies
      method: "requirements.txt / pyproject.toml vs 实际 pip freeze 交叉对比"
      status: "待实现"
      auto_fixable: true

    - id: "security_policy_drift"
      drift_dimension: "D5_security"
      severity: HIGH
      category: security
      method: "安全规范要求（input sanitization / auth middleware）vs 所有端点实际实现"
      status: "待实现"
      auto_fixable: false

    - id: "doc_code_coevolution"
      drift_dimension: "D5_doc_coevolution"
      severity: MEDIUM
      category: documentation
      method: "代码文件最后修改时间 vs 对应蓝图/文档最后修改时间——文档滞后标记"
      status: "待实现"
      auto_fixable: false

    - id: "test_coverage_drift"
      drift_dimension: "D5_test_coverage"
      severity: MEDIUM
      category: quality
      method: "模块代码行数增长率 vs 测试代码行数增长率——覆盖率趋势对比"
      status: "待实现"
      auto_fixable: false
```

### 2.2 基线快照管理器（决策 D-023-03）

> **决策 D-023-03**：引入 Baseline Snapshot 机制——每个模块 phase 完成时自动生成基线快照。日常漂移检测 = baseline vs current，而非 current vs current。基线版本化管理，支持差异比较和慢蠕变（slow creep）检测。
>
> **决策依据**：没有基线，"当前一致"不等于"没有漂移"。AI 施工场景下，每次微调一点点，3 个月后模块面目全非但无人察觉——只有 baseline diff 能发现。

```yaml
baseline_manager:
  snapshot_content:
    - type: "tree_hash"
      description: "模块目录树结构 + 每个文件的 SHA256——快速完整性验证"
    - type: "interface_snapshot"
      description: "模块公开接口签名（函数名/参数/返回类型）——接口契约漂移检测"
    - type: "import_graph"
      description: "模块 import 依赖图——依赖漂移检测"
    - type: "config_snapshot"
      description: "模块相关 YAML/JSON 配置的 canonical 值——配置漂移检测"

  lifecycle:
    - trigger: "construction_progress 变更为 phase_*_complete"
      action: "自动拍摄基线快照 → 存入 data/drift_baselines/<module_id>/"
    - trigger: "Owner 手动触发"
      action: "重新拍摄基线（如：经审查确认当前状态为新的 known-good）"

  diff_mode:
    - type: "full_diff"
      description: "baseline vs current——全量差异"
      use_case: "phase 验收、on-demand 深度检查"
    - type: "slow_creep_detection"
      description: "current vs baseline 累计差异度 = Σ 每次 micro-drift"
      use_case: "周期性趋势告警——累计漂移超过阈值"
    - type: "contract_only"
      description: "仅比较接口契约（函数签名/参数/返回类型）"
      use_case: "post-commit 快速检查——10s 内完成"

  storage:
    path: "data/drift_baselines/"
    format: "JSON (human-readable) + SHA256 manifest"
    retention: "保留最近 10 个基线版本，旧版本自动归档"
```

### 2.3 漂移状态机（决策 D-023-04）

> **决策 D-023-04**：漂移事件必须拥有完整的生命周期状态机——从 DETECTED 到 RESOLVED / VERIFIED。状态变更记录到 SQLite drift_events 表。无人处理的漂移自动升级（DEAD_LETTER）。
>
> **决策依据**：没有状态机，漂移事件是一次性 log，无法追踪是否被处理。AI 之间（跨 session）可能反复修同一个漂移或完全忽略。

```yaml
drift_state_machine:
  states:
    DETECTED:
      description: "detector 检测到漂移，尚未人工/AI 确认"
      auto_transition: "无——需显式 ACK"
      ttl: "24h 后自动升级为 DEAD_LETTER"

    TRIAGED:
      description: "已分类——AUTO_FIXABLE / NEEDS_SUGGESTION / NEEDS_HUMAN"
      auto_transition: "AUTO_FIXABLE → RESOLVING（自动触发修复）"

    ACKNOWLEDGED:
      description: "Owner 或 AI 已确认此漂移为真实问题（非假阳性）"
      auto_transition: "无——需显式操作"

    RESOLVING:
      description: "正在修复中——自动修复脚本执行中 或 AI task 已派发"
      auto_transition: "修复成功 → RESOLVED / 修复失败 → FIX_FAILED"

    RESOLVED:
      description: "漂移已修复——等待验证"
      auto_transition: "下次 scan 通过 → VERIFIED"

    VERIFIED:
      description: "修复已验证——漂移不再存在"
      auto_transition: "终端状态——保留 30 天后归档"

    FIX_FAILED:
      description: "自动修复失败——已触发 auto-rollback"
      auto_transition: "升级为 NEEDS_HUMAN → 通知 Owner"

    FALSE_POSITIVE:
      description: "确认为误报——标记 detector 规则需调整"
      auto_transition: "终端状态——记录到 detector feedback 表"

    DEAD_LETTER:
      description: "超过 TTL 无人处理——升级告警"
      auto_transition: "通知 Owner（P0 告警）→ 等待 ACK"

    SUPPRESSED:
      description: "已知问题，当前维护窗口内不告警"
      auto_transition: "维护窗口结束后自动恢复为 DETECTED"

  storage:
    table: "drift_events"
    fields:
      - event_id: "UUID 主键"
      - module_id: "关联模块"
      - detector_id: "触发检测器"
      - drift_dimension: "漂移维度"
      - baseline_version: "基线版本"
      - state: "当前状态"
      - created_at: "发现时间"
      - updated_at: "最后状态变更时间"
      - resolved_by: "修复者（AI session ID / Owner）"
      - resolution_detail: "修复描述"
      - auto_fixed: "是否自动修复"
      - rollback_verified: "回滚后是否验证通过"
```

### 2.4 增量扫描与性能 SLO（决策 D-023-05）

> **决策 D-023-05**：引入增量扫描机制——git diff 驱动，只扫描变更影响范围。定义三级扫描深度与对应的性能 SLO。80+ 检测器全量扫描需要分级调度。
>
> **决策依据**：post-commit < 10s 约束下，全量扫描 80+ 脚本不可行。必须分级：commit 范围增量扫描 + 周期轻量扫描 + on-demand 全量扫描。

```yaml
scan_levels:
  LIGHT:
    description: "Post-commit 增量扫描——仅扫描 git diff 涉及的检测器"
    performance_slo: "< 5s"
    detectors: "仅触发变更文件关联的检测器（按 detector scope 匹配）"
    cache_strategy: "维护 git diff → detector 映射缓存，避免每次全量评估"

  STANDARD:
    description: "周期性扫描——每 30 分钟跑 HIGH severity 检测器"
    performance_slo: "< 30s"
    detectors: "HIGH severity（P0 等价）"
    parallelism: "最多 4 个检测器并行"

  DEEP:
    description: "On-demand / phase 验收全量扫描"
    performance_slo: "< 5min（1500 模块规模）"
    detectors: "ALL"
    parallelism: "最多 8 个检测器并行"
    note: "全量扫描允许长耗时，但需进度回调"

performance_optimizations:
  - mechanism: "检测器结果缓存"
    detail: "同一文件未变更 + 同一检测器 → 复用上次结果（SHA256 校验）"
  - mechanism: "增量依赖图"
    detail: "文件A变更 → 仅触发 import A 的模块关联检测器"
  - mechanism: "并行调度器"
    detail: "asyncio subprocess pool——80+ 脚本并行执行，结果汇总"
```

### 2.5 自动对账策略（决策 D-023-02 / 增强）

> **决策 D-023-02**（增强）：漂移检测后自动对账——可自动修复的漂移自动修，不可自动修复的生成修复建议。自动修复前拍 pre-fix 快照，修复失败触发 auto-rollback，**回滚后必须验证漂移是否真正消除**。

```yaml
reconciliation_strategy:
  pre_fix_snapshot:
    description: "自动修复前拍摄 pre-fix 快照——用于 rollback + diff trace"
    content: "受影响的文件 → temp backup + SHA256"
    retention: "修复验证通过后删除"

  auto_fixable:
    description: "可自动修复的漂移——脚本自动修复"
    examples:
      - "蓝图路径索引与磁盘不一致 → 自动更新路径索引"
      - "YAML 注册表缺少新模块 → 自动追加条目"
      - "blueprint-registry.yaml 统计数字不准 → 自动重新计算"
      - "requirements.txt 版本与 pip freeze 不一致 → 自动同步"
    action: "pre-fix 快照 → 自动修复 → 修复后验证 → 审计日志 → 通知 Owner"

  needs_suggestion:
    description: "不可自动修复的漂移——生成修复建议"
    examples:
      - "蓝图 §3 接口与代码实际接口不一致 → 生成结构化 diff"
      - "蓝图缺失章节 → 生成待补全模板"
      - "AI 幻觉引用不存在的模块 → 生成删除/替换建议"
      - "跨模块功能重复 → 生成合并建议 + 二选一推荐"
    action: "生成修复建议 → drift 状态 → NEEDS_SUGGESTION → 通知 Owner"

  auto_fix_failed:
    description: "自动修复失败 → 自动回滚 → 验证回滚结果"
    action:
      - "从 pre-fix 快照恢复文件"
      - "SHA256 校验恢复完整性"
      - "重新跑触发检测器 → 验证漂移是否回到修复前状态"
      - "若回滚验证失败（文件损坏/不一致）→ 升级为 P0 CRITICAL → 通知 Owner"
      - "审计日志记录全链路"
```

### 2.6 检测触发策略与维护窗口（决策 D-023-06）

> **决策 D-023-06**：扩展触发策略——增加维护窗口/冻结期概念。生产事故期间、大版本升级期间，漂移检测可降级为 shadow mode（仅记录不阻断）。
>
> **决策依据**：无维护窗口概念时，升级期间的大量预期漂移会导致告警风暴，掩盖真正的异常漂移。

```yaml
triggers:
  post_commit:
    description: "git commit 后自动触发——增量扫描（LIGHT）"
    scope: "受影响模块 + 依赖模块"
    latency: "< 5s"

  periodic_light:
    description: "每 30 分钟——HIGH severity 检测器（STANDARD）"
    scope: "global"
    latency: "< 30s"

  periodic_deep:
    description: "每 6 小时——全局 DEEP 扫描"
    scope: "global"
    latency: "< 5min"

  on_demand:
    description: "MCP Tool call / Owner 手动触发"
    scope: "指定范围"
    latency: "取决于 scan level 参数"

  phase_gate:
    description: "construction_progress 变更为 complete 时触发"
    scope: "目标模块"
    latency: "DEEP——拍摄基线 + 全量对账"
    action: "通过 → 拍摄新基线 / 不通过 → 拒绝 phase 变更"

maintenance_window:
  freeze_policy:
    - trigger: "Owner 声明维护窗口（start_time ~ end_time）"
      action: "drif_detector 进入 shadow mode——检测但不阻断，不触发告警"
    - trigger: "自动检测大规模 git diff（> 50 files changed）"
      action: "自动进入 shadow mode 2 小时——避免大版本升级告警风暴"

  suppression:
    - mechanism: "per-detector per-module 漂移抑制"
      detail: "Owner 可将已知漂移标记为 SUPPRESSED（含过期时间）"
    - mechanism: "抑制期结束自动恢复检测"
      detail: "expires_at 到达 → 漂移状态从 SUPPRESSED → DETECTED"
```

### 2.7 自漂移检测——Watcher 的 Watcher（决策 D-023-07）

> **决策 D-023-07**：Drift detector 自身不能成为漂移盲区。定期对 drift detector 的配置文件和检测器注册表做 checksum 验证。自漂移检测使用最小独立逻辑（纯 stdlib，零依赖），确保即使 drift detector 本身损坏也能自检。
>
> **决策依据**：Watcher 的 Watcher 是分布式系统的经典难题。最小自检必须是独立逻辑——不能用 drift detector 的代码检测 drift detector 自身。

```yaml
self_drift:
  checks:
    - target: "_detector_registry.yaml"
      method: "SHA256 checksum vs 上次已知值"
      frequency: "每次 scan 前执行"
    - target: "drift_detector.py"
      method: "SHA256 checksum vs git HEAD 版本"
      frequency: "每次 scan 前执行"
    - target: "reconciler.py"
      method: "SHA256 checksum vs git HEAD 版本"
      frequency: "每次 scan 前执行"

  bootstrap_self_check:
    description: "最小自检——纯 stdlib，独立于 drift detector 主逻辑"
    method: "验证核心文件存在性 + SHA256 完整性 + _detector_registry.yaml 可解析性"
    on_failure: "P0 告警——drift detector 自身可能已被损坏"
    code_path: "src/zephyr/drift_detector/self_check.py"
    constraint: "self_check.py 只导入 stdlib（pathlib + hashlib + yaml 安全解析），不导入 zephyr 任何模块"

  immutable_manifest:
    description: "drift detector 自身的不可变清单——存在 Git 中，定期对比"
    files:
      - "src/zephyr/drift_detector/_detector_registry.yaml"
      - "src/zephyr/drift_detector/self_check.py"
```

### 2.8 并发竞争与文件锁——Drift Detector 与 AI 施工的并发安全（决策 D-023-11）

> **决策 D-023-11**：Drift detector 的自动修复和 AI 施工可能同时修改同一文件。引入乐观并发控制——自动修复前检查文件 mtime，若在 pre-fix 快照后已被修改（AI 正在施工），则放弃自动修复，改为生成建议。AI 施工侧在 task 派发时携带 drift context，避免在已知漂移区域施工。
>
> **决策依据**：100% AI 施工 + 运行时自动修复，二者并发写同一文件是确定性事件。乐观锁成本最低，阻断成本最高。

```yaml
concurrency_control:
  auto_fix_guard:
    before_fix:
      - "拍摄 pre-fix 快照（文件内容 + mtime + SHA256）"
      - "记录快照时间戳 T0"
    before_commit:
      - "检查目标文件 mtime：若 > T0 → 文件已被外部修改"
      - "action: ABORT auto-fix → 生成修复建议 → 记录冲突事件"
      - "若 mtime == T0 → 安全提交修复"

  ai_construction_guard:
    pre_task_injection:
      description: "AI task 派发时自动注入目标模块的漂移上下文"
      content:
        - "当前模块的 active drift events（state ≠ VERIFIED）"
        - "上次 DEEP scan 时间与结果摘要"
        - "与目标文件相关的已知漂移及其修复状态"
      purpose: "AI 在施工前就知道哪些区域有漂移，避免在漂移区域施工或与自动修复冲突"

  lock_free_design:
    principle: "不引入文件锁（避免死锁 + 复杂度）。乐观并发 + 冲突检测 + 重试即可"
    max_retry: 3
    retry_backoff: "exponential: 1s → 2s → 4s"

  conflict_resolution:
    priority_rule: "AI 施工 > 自动修复"
    rationale: "AI 施工是主动变更（创造价值），自动修复是被动补偿（修正偏差）。施工优先，修复等施工完成后重新评估"
```

### 2.9 漂移预算与施工门禁（决策 D-023-12）

> **决策 D-023-12**：引入 SRE 式漂移预算——每个模块每月允许的漂移上限。预算耗尽后，该模块的新施工任务被门禁阻断，直到漂移清理到安全水位以下。漂移预算按模块优先级分级。
>
> **决策依据**：没有预算约束，漂移会无限积累——"先干后验"退化为"只干不验"。预算机制强制在继续施工前清理债务。

```yaml
drift_budget:
  tiers:
    P0_module:
      monthly_budget: 3
      hard_limit: "预算耗尽 → G1 门禁阻断新任务 → 必须 RESOLVE ≥ 50% 活跃漂移才能解封"
      grace_period: "0（P0 模块零容忍）"

    P1_module:
      monthly_budget: 8
      hard_limit: "预算耗尽 → 新任务降级为 P3（仅可做修复类任务）"
      grace_period: "24h 缓冲期"

    P2_module:
      monthly_budget: 15
      hard_limit: "预算耗尽 → 警告通知，不阻断"
      grace_period: "7d 缓冲期"

  budget_consumption:
    rule: "每产生一个非 FALSE_POSITIVE 漂移事件 → 消耗 1 预算"
    reset: "每月 1 日 00:00 UTC 重置"
    carry_over: "未使用的预算不累积（防止'攒着一起漂'的行为）"

  enforcement:
    integration: "Gate Engine G1 门禁——evaluate(task) 时检查目标模块漂移预算"
    bypass: "BREAK_GLASS 模式可绕过（需 Owner 审批 + 完整审计链）"

  budget_dashboard:
    - "每个模块的预算剩余量 / 总预算"
    - "本月预算消耗速率（消耗/天）→ 预估耗尽日期"
    - "历史预算超额模块 TOP 10"
```

### 2.10 崩溃恢复与检查点机制（决策 D-023-17）

> **决策 D-023-17**：Drift detector 在长扫描（DEEP 模式）中可能因 OOM、进程被杀、Python 异常等原因中途崩溃。引入检查点机制——每个检测器完成后写 checkpoint，崩溃后从最后一个 checkpoint 恢复，不重复执行已完成的检测器。
>
> **决策依据**：DEEP 扫描耗时 < 5min × 80+ 检测器，崩溃后从头重跑是不可接受的。1人维护下，崩溃不应导致数据丢失或结果不一致。

```yaml
crash_recovery:
  checkpoint:
    granularity: "per detector"
    content:
      - "scan_id: 当前 scan 的唯一 ID"
      - "completed_detectors: [已完成检测器 ID 列表]"
      - "last_checkpoint_time: 写入时间戳"
      - "scan_start_time: scan 开始时间"
    storage: "data/drift_checkpoints/<scan_id>.json"
    write_policy: "每个检测器完成后立即 fsync——不依赖 Python 进程正常退出"

  recovery:
    on_startup: "扫描 data/drift_checkpoints/ 寻找未完成的 scan_id"
    action: "若存在 → 加载已完成列表 → 从剩余检测器继续执行 → scan 完成后删除 checkpoint"
    staleness: "若 checkpoint 超过 24h 仍未被恢复 → 标记为 ORPHANED → 通知 Owner → 手动清理"

  transaction_safety:
    principle: "drift_events 写入使用 SQLite 事务"
    detail: |
      每个检测器的结果在单个事务中写入 drift_events。
      若进程在事务中崩溃 → SQLite WAL 自动回滚 → 不产生半截数据。
      checkpoint 只记录"已完成"的检测器 → 与 drift_events 中已提交的数据一致性由事务保证。

  graceful_shutdown:
    signal_handling: "SIGTERM / SIGINT → 完成当前检测器 → 写 checkpoint → 退出"
    max_wait: "30s（超时则强制退出，checkpoint 标记为 INCOMPLETE）"
```

### 2.11 漂移风暴与批量处理模式（决策 D-023-18）

> **决策 D-023-18**：当单次 scan 产生 > 50 个漂移时，进入 storm mode——批量处理、压缩摘要、暂停自动修复。防止因大型重构或基础设施变更引发的事件洪流淹没系统。
>
> **决策依据**：你提到"氛围编程社区的做法"——他们常一次性大规模重构（如全面的类型注解添加、统一的格式化）。500 个模块同时漂移是正常事件，不能按常规流程逐条处理。

```yaml
storm_mode:
  trigger: "单次 scan 产生 drift events > 50"

  behavior:
    - "暂停自动修复——批量变更下自动修复大概率产生冲突"
    - "漂移按维度聚合——不逐条报告，按 drift_dimension 分组摘要"
    - "每个维度的漂移只创建一条 bulk_drift_event（包含 affected_modules 列表）"
    - "severity 降级——明知是大规模重构引入的漂移，不应全部 P0 告警"

  classification:
    expected_storm:
      description: "因已知计划内变更引入的漂移（如：统一格式化、全局 import 重排）"
      action: "自动识别（commit message 含 REFACTOR/MIGRATION/REFORMAT）→ 自动进入 storm mode"

    unexpected_storm:
      description: "无已知原因的突然大规模漂移"
      action: "P0 告警——可能是基础设施损坏或恶意篡改"

  recovery:
    description: "storm mode 持续到连续 2 次 scan 漂移数 < 50 或 Owner 手动解除"
    post_storm: "对 bulk_drift_event 做 split——按 module 拆分为独立 drift 事件 → 进入正常生命周期"

  storm_cache:
    description: "storm mode 期间，增量扫描缓存标记为 DIRTY_AFTER_STORM → 强制下一次 LIGHT scan 重扫所有受影响模块"
```

### 2.12 热修复/紧急变更旁路（决策 D-023-19）

> **决策 D-023-19**：P0 热修复（hotfix）通常绕过 CI/CD 门禁直接在主干提交。Drift detector 会将其标记为漂移——但实际上这是 Owner 确认过的有意偏差。引入 hotfix_acknowledged 快速旁路。
>
> **决策依据**：严格的门禁制度在热修复场景下会成为阻碍。不能让 drift detector 在救火时报警。

```yaml
hotfix_bypass:
  trigger: "commit message 含 [HOTFIX] 或 [EMERGENCY] 前缀"

  behavior:
    - "当前 commit 产生的漂移自动标记为 HOTFIX_ACKNOWLEDGED"
    - "不消耗漂移预算"
    - "不触发告警"
    - "状态自动进入 SUPPRESSED（ttl=72h）"

  post_hotfix_reconciliation:
    description: "热修复 72h 后漂移状态恢复为 DETECTED"
    rationale: "热修复是临时的——72h 后必须正式修复或正规化，否则漂移会腐烂"
    action: "72h 过期 → 通知 Owner: 'hotfix {commit_hash} 引入的漂移尚在处理中，请确认是否转为正式修复'"

  audit:
    description: "HOTFIX 旁路记录到独立审计表 drift_hotfix_log"
    content: "commit_hash / module_ids / drift_dimensions / owner_ack / timestamp"
    ttl: "永久保留——热修复是高危操作，审计链不可丢"
```

### 2.13 环境感知与渐进部署漂移（决策 D-023-20）

> **决策 D-023-20**：多环境（dev / staging / production 或单机上不同的运行上下文）可能合法存在差异。Drift detector 需要环境感知——不将环境差异错误标记为漂移。同时需要感知渐进部署（canary rollout）中的部分不一致。
>
> **决策依据**：虽然当前是单节点场景，但"环境差异"的抽象仍然适用——不同 Python venv、不同配置文件、不同运行时参数都可能引入合法的不一致。

```yaml
environment_awareness:
  context_tags:
    description: "每个模块可声明其运行环境的 context tags"
    examples:
      - "python_version: 3.11 | 3.12"
      - "config_profile: dev | prod | test"
      - "feature_flags: [experimental_api_v2 ON | OFF]"

  differential_detection:
    description: "当同一模块在不同环境中表现不同时——标记为 ENV_DIFF 而非 DRIFT"
    rule: "若差异仅出现在 env_A 而不在 env_B → 非漂移（环境特异性配置）"
    rule: "若差异在所有环境中同时出现 → 真漂移"

  partial_deployment:
    description: "渐进部署（如：先改 10% 的模块结构，观察后再全量推）"
    detection: "检测到模块 A 已迁移到新结构、B 还在旧结构 → 标记为 MIGRATION_IN_PROGRESS"
    ttl: "24h 内未完成全部迁移 → 升级为 PARTIAL_MIGRATION_STALLED"
```

### 2.14 自动学习——假阳性模式识别与抑制（决策 D-023-21）

> **决策 D-023-21**：同一 (detector, pattern) 组合被多次标记为 FALSE_POSITIVE 后，自动学习该模式——在后续扫描中静默抑制，转为 shadow 观测。若抑制后漂移模式发生变化（可能假阳性变成真漂移），自动解除抑制。
>
> **决策依据**：1人维护下，反复手动标记假阳性是不可持续的。需要检测器具备自适应能力。

```yaml
auto_learning:
  false_positive_learning:
    trigger: "同一 (detector_id, module_id, pattern_hash) 组合被标记 FALSE_POSITIVE ≥ 3 次"
    action: "自动创建 suppression_rule → 后续匹配时自动抑制 + shadow 观测"
    shadow_mode: |
      抑制的漂移仍然在后台检测——每次 scan 对比 suppression_rule 创建时的 pattern 与当前 pattern。
      若 pattern 发生变化（如：之前误报是因为路径 A 匹配，现在路径 A 真的不存在了）→ 解除抑制 → 重新标记 DETECTED。

  pattern_hash:
    description: "漂移的归一化指纹——用于判断'同一模式'"
    composition:
      - "detector_id: 哪个检测器"
      - "drift_dimension: 哪个维度"
      - "diff_signature: 差异的结构化摘要（非精确文本匹配，而是结构匹配）"
    example: |
      蓝图路径不一致检测器 对 module_X 误报了 3 次
      → pattern_hash = SHA256(detector=blueprint_code_sync + dim=D5-BP-SYNC + diff_type=path_missing)
      → 自动抑制该组合

  suppression_review:
    frequency: "每 30 天自动提示 Owner review 所有活跃的 suppression_rule"
    metric: "每个 rule 的 shadow 命中次数 / 总 scan 次数"
    stale_rule: "若 rule 在 30 天内 shadow 命中次数 = 0 → 建议删除（模式可能已不存在）"
```

### 2.15 多实例竞态——Drift Detector 自身并发安全（决策 D-023-24）

> **决策 D-023-24**：Post-commit 触发 LIGHT scan + 定时 periodic scan + Owner 手动 on-demand scan 可能同时运行。引入 scan mutex——同一时间最多一个 scan 实例在运行。新触发排队或合并。scan_id 写入 lock file，避免两实例同时写 drift_events。
>
> **决策依据**：2.8 解决了 detector vs AI 的并发，但没有解决 detector vs detector 自身的并发。两个 scan 同时跑会导致 drift_events 重复写入 + 告警重复发送。

```yaml
instance_mutex:
  lock_mechanism:
    method: "文件锁——data/drift_scan.lock"
    content: "pid + scan_id + scan_start_time + scan_level"
    timeout: "锁持有超过 scan SLO × 2 → 判定为 stale lock → 强制清除 + 通知 Owner"

  collision_policy:
    same_level_collision:
      description: "两个 LIGHT scan 或两个 DEEP scan 同时触发"
      action: "后者排队——等待前者完成后执行（max wait = SLO × 2）"

    level_preemption:
      description: "LIGHT scan 正在跑，DEEP scan 被触发"
      action: "DEEP 排队等待 LIGHT 完成——LIGHT 优先级高（post-commit 必须快）"

    reverse_preemption:
      description: "DEEP scan 正在跑，LIGHT scan 被触发（post-commit）"
      action: "LIGHT scan 使用 DEEP scan 的当前进度作为缓存基础——不等待、不冲突"
      note: "DEEP scan 已完成模块的结果对 LIGHT scan 直接有效（只要 mtime 未变）"

  merge_strategy:
    description: "若排队队列中已有同 level scan → 合并（后者覆盖前者——因为后者基于更新的 HEAD）"
```

### 2.16 孤儿资源检测——磁盘有、注册表无、代码不引用（决策 D-023-25）

> **决策 D-023-25**：文件中三种情况：(a) 注册表有、磁盘有 → 正常；(b) 注册表有、磁盘无 → 漂移（已检测）；(c) 磁盘有、注册表无、代码不引用 → **孤儿资源**——无人知晓但占用磁盘空间。定期扫描并生成清理建议。
>
> **决策依据**：AI 施工会产生大量临时文件、中间产物、重命名残留。孤儿文件积累会污染目录结构 + 增加扫描时间 + 增大基线快照体积。

```yaml
orphan_detection:
  scope: "docs/03_modules/ + scripts/governance/ + src/zephyr/（排除 .git/ + data/ + __pycache__/ + *.pyc）"

  classification:
    true_orphan:
      description: "文件不在任何 YAML 注册表中、不被任何 import 引用、不在 .gitignore 豁免列表中"
      action: "生成清理建议——> 7 天未修改 → 建议删除"

    undocumented_asset:
      description: "文件被代码 import 引用但不在此模块的 YAML 注册表中"
      action: "标记为 UNDOCUMENTED——生成 YAML 注册补全建议"

    stale_artifact:
      description: "文件最后修改日期 > 90 天且不在注册表中"
      action: "标记为 STALE——建议归档或删除"

  safeguards:
    - "清理建议永远只是建议——不自动删除任何文件"
    - "Owner 必须显式确认后才能删除"
    - "删除前自动备份到 data/orphan_archive/<timestamp>/"
```

### 2.17 符号链接与子模块完整性（决策 D-023-26）

> **决策 D-023-26**：Git 仓库可能包含符号链接（symlink）和子模块（submodule）。这些特殊文件类型的漂移检测需要专门策略——symlink 目标是否有效、子模块 hash 是否匹配。
>
> **决策依据**：ZephyrAlpha 可能会使用符号链接做模块间共享（如共享的 scripts/），使用 git submodule 管理外部依赖。这些是传统漂移检测的盲区。

```yaml
symlink_drift:
  checks:
    - name: "broken_symlink"
      method: "os.path.islink() + os.path.exists() → 符号链接存在但目标不存在 → 断裂链接"
      severity: HIGH
    - name: "symlink_target_change"
      method: "baseline 中符号链接目标 vs 当前符号链接目标（SHA256 对比）"
      severity: MEDIUM
    - name: "circular_symlink"
      method: "符号链接链跟踪——防止循环引用（A→B→C→A）"
      severity: HIGH

  policy: "项目中符号链接应声明在 YAML 注册表的 symlinks 字段——便于审批和追踪"

submodule_drift:
  checks:
    - name: "dirty_submodule"
      method: "git submodule status → 检查是否包含 '+' (dirty) 前缀"
      severity: HIGH
    - name: "out_of_sync_submodule"
      method: ".gitmodules 声明的 commit hash vs 实际 submodule HEAD"
      severity: HIGH
    - name: "uninitialized_submodule"
      method: "git submodule status → 检查是否包含 '-' 前缀（未初始化）"
      severity: MEDIUM
```

### 2.18 文件底层属性漂移——编码、换行符、权限（决策 D-023-27）

> **决策 D-023-27**：文件内容可能完全一致但底层属性不一致——编码（UTF-8 BOM vs 无BOM）、换行符（CRLF vs LF）、文件权限（可执行位）——这些都可能导致跨平台问题且对 git diff 不可见。
>
> **决策依据**：AI 施工在不同 session 中可能在 Windows/Linux 间切换，产生换行符不一致。这是氛围编程社区的经典痛点——"在 Windows 上拉了 Linux 项目的代码，AI 改完提交，CI 在 Linux 上跑挂了"。

```yaml
file_attribute_drift:
  encoding:
    description: "UTF-8 BOM / UTF-16 LE / UTF-16 BE / Latin-1 等编码不一致"
    method: "chardet / cchardet 检测文件编码 → 与项目标准（UTF-8 无 BOM）对比"
    severity: MEDIUM
    auto_fixable: true
    auto_fix_action: "自动转换为 UTF-8 无 BOM"

  line_ending:
    description: "CRLF (Windows) vs LF (Unix) 混用"
    method: "检测文件中的 \r\n 出现频率 → 若同时存在 \r\n 和纯 \n → LINE_ENDING_MIXED"
    severity: MEDIUM
    auto_fixable: true
    auto_fix_action: |
      转换为 LF（Unix 标准）——写入 .gitattributes 强制 LF。
      不自动改已有文件（避免 diff 噪声），仅在 .gitattributes 中声明策略。

  file_permissions:
    description: "可执行位不一致——.py 文件不应该有 +x（除非是 CLI 入口脚本）"
    method: "检查 src/zephyr/**/*.py 的可执行位 → 非 __main__ 入口不应有 +x"
    severity: LOW
    auto_fixable: true

  gitattributes_enforcement:
    description: ".gitattributes 文件是否覆盖了所有关键文件类型的换行符/编码声明"
    check: "*.py text eol=lf / *.yaml text eol=lf / *.md text eol=lf"
```

### 2.19 冷启动策略——零基线状态下的漂移检测引导（决策 D-023-33）

> **决策 D-023-33**：Drift detector 首次运行时没有基线、没有 drift_events 历史、没有关联数据。不能要求先人工创建基线再开始工作——需要在"先信任当前状态为 known-good"的假设下自动引导。冷启动分三步：扫描→信任→建立基线。
>
> **决策依据**：1500 模块上线第一天，不能要求 Owner 逐个确认基线。自动信任当前 HEAD 为初始基线——后续漂移检测从此基线开始。

```yaml
cold_start:
  phase_1_bootstrap_scan:
    description: "首次运行——全量 DEEP scan 但模式为 BOOTSTRAP"
    behavior:
      - "运行所有检测器——但结果只记录为 INITIAL_BASELINE，不标记为 DETECTED"
      - "不消耗漂移预算"
      - "不触发告警"
    output: "COLD_START_REPORT: {N} 个问题在初始状态中已存在——不是漂移，是'遗产债务'"

  phase_2_trust_establishment:
    description: "Owner 审查 COLD_START_REPORT → 两种选择"
    option_a: "ACCEPT_CURRENT——接受当前状态为初始基线（known-good）"
    option_b: "DECLARE_DEBT——标记特定问题为 LEGACY_DEBT（已知债务，不计入预算，但持续追踪）"

  phase_3_baseline_creation:
    description: "初始基线拍摄——从此开始正常漂移检测生命周期"
    trigger: "Owner 完成 phase 2 审查"
    action: "拍摄全量基线快照 → 漂移状态机进入正常模式"

  re_bootstrap:
    description: "若 drift_events.db 损坏或丢失 → 触发重新冷启动"
    detection: "drift_events.db 不存在 或 所有 baseline 快照丢失"
    action: "保留旧数据到 backup → 重新执行冷启动流程"

  shallow_clone_awareness:
    description: "检测 git 是否为 shallow clone（git rev-parse --is-shallow-repository）"
    impact: "shallow clone → git bisect 不可用 → 禁用溯源功能 → 通知 Owner"
    resolution: "提示 Owner 运行 git fetch --unshallow 或接受无溯源模式"
```

### 2.20 Owner 缺席模式——1人维护的独特性挑战（决策 D-023-34）

> **决策 D-023-34**：1人维护下，Owner 可能因休假/出差/生病离线 1-2 周。在此期间漂移预算会重置、hotfix 会过期、storm 可能发生。Drift detector 不能在 Owner 缺席时堆积 P0 告警或错误地阻断施工。引入 absence mode——预设的降级运维策略。
>
> **决策依据**：这是 4 轮审查中从未触及的核心问题。所有 SRE/DevOps 方案都假设多人值班，但你是 1 人。缺席时系统必须能自我保护。

```yaml
absence_mode:
  activation:
    - manual: "Owner 手动声明 ABSENCE_START → ABSENCE_END"
    - auto_detect: "连续 48h 无人确认任何告警 → 自动进入 LENIENT_ABSENCE"

  modes:
    LENIENT:
      description: "Owner 短期离线（< 3 天）——宽松但不放任"
      policies:
        - "漂移预算消耗阈值从 100% 提升到 200%（双倍容忍）"
        - "自动修复仍执行（修复比不修复好）"
        - "告警聚合为日报（不逐条推送）"
        - "级联故障检测正常工作（P0 仍告警——因为这是安全问题）"

    SURVIVAL:
      description: "Owner 长期离线（> 3 天）——仅维持系统不崩溃"
      policies:
        - "漂移预算完全关闭（不阻断任何施工）"
        - "自动修复关闭（风险太高，无 Owner 审查）"
        - "告警静默存储，Owner 回来后批量推送摘要"
        - "所有扫描正常执行但结果仅存档"
        - "热修复 72h 过期规则暂停（因为没人处理）"

  return_handover:
    description: "Owner 标记 ABSENCE_END → 系统生成缺席期摘要"
    report_content:
      - "缺席期间产生的漂移总数 / 按维度分布"
      - "缺席期间自动修复执行次数 / 成功率"
      - "缺席期间级联故障 / 风暴事件"
      - "当前预算状态（哪些模块超支）"
      - "Top 5 需要 Owner 立即处理的事项（ROI 排序）"
    report_format: "Feishu 推送 + CLI 可读摘要"
```

### 2.21 告警可信度评分——防止"狼来了"效应（决策 D-023-35）

> **决策 D-023-35**：每个检测器维护一个 credibility score——基于 false positive rate、detection precision、历史误报纠正率。低可信度检测器的告警自动降级或延迟推送。Owner 可手动调整可信度权重。
>
> **决策依据**：1人维护下最大的风险不是漏报（false negative），而是告警疲劳导致 Owner 忽略所有告警（alert blindness）。可信度评分让 Owner 只关注"真正值得关注的"。

```yaml
credibility_scoring:
  formula: "credibility = base_score × (1 - fp_rate) × precision × recency_factor"

  base_score:
    new_detector: 0.5
    proven_detector: 1.0

  fp_rate:
    description: "FALSE_POSITIVE 标记数 / 总告警数（近 90 天）"
    impact: "fp_rate > 0.3 → credibility × 0.5 / fp_rate > 0.5 → credibility × 0.2"

  precision:
    description: "VERIFIED 的漂移在总告警中的占比（排除 FALSE_POSITIVE 后的实际修复率）"
    impact: "precision < 0.3 → 检测器可能过于敏感"

  recency_factor:
    description: "最近一次 false positive 纠正距今天数"
    impace: "> 90 天未纠正 → 检测器可能已过时 → credibility × 0.8"

  alert_modulation:
    high_credibility: "> 0.8 → 正常告警，最高优先级推送"
    medium_credibility: "0.4-0.8 → 告警但聚合到批次"
    low_credibility: "< 0.4 → 转为 shadow 观测，不推送，仅在仪表板可见"

  owner_override:
    description: "Owner 可手动设置特定检测器的 credibility_weight（如：我知道它误报多但暂时不想修）"
```

---

## 3. 漂移维度完整清单

检测器覆盖矩阵——每个维度至少一个检测器。📋 = 待实现。

| 维度 ID | 漂移维度 | 检测器 | 严重度 | 状态 |
|---------|---------|--------|:---:|:---:|
| D5-BP-SYNC | 蓝图-代码路径同步 | validate_blueprint_code_sync | HIGH | ✅ |
| D5-YAML-DISK | YAML 注册表 vs 磁盘 | validate_code_yaml_alignment | MEDIUM | ✅ |
| D5-MANIFEST | 静态清单生成器一致性 | validate_static_manifest_drift | HIGH | ✅ |
| D3-D5-NUM | MD vs YAML 数字漂移 | validate_md_yaml_number_drift | HIGH | ✅ |
| D5-IMPL-DOC | 蓝图实现文档合规 | validate_blueprint_implementation_docs | HIGH | ✅ |
| D5-THREE-WAY | 三向一致性（蓝图-YAML-代码） | validate_three_way_consistency | HIGH | ✅ |
| D5-SSOT | SSoT 权威性 | validate_ssot | HIGH | ✅ |
| D5-LIFECYCLE | 模块生命周期状态 | validate_module_lifecycle | MEDIUM | ✅ |
| D4-LAYER | 层级依赖合规 | validate_layer_deps | HIGH | ✅ |
| D5-XREF | 交叉引用完整性 | validate_cross_references | MEDIUM | ✅ |
| D5-DEPS-FMT | depends_on 格式合规 | validate_depends_on_format | MEDIUM | ✅ |
| D5-CONTRACTS | 接口契约对齐 | validate_interface_contracts | HIGH | ✅ |
| D5-DIR | 目录结构规范 | validate_directory_structure | MEDIUM | ✅ |
| D5-DEPRECATED | 废弃路径依赖检测 | validate_deprecated_dependents | HIGH | ✅ |
| D5-GATE-YAML | 门禁 YAML 合规 | validate_gate_yaml | HIGH | ✅ |
| D5-P0-CONTRACTS | P0 模块契约 | validate_p0_module_contracts | HIGH | ✅ |
| D5-ARCH-CONTRACTS | 架构内部契约 | validate_architecture_contract_internal | HIGH | ✅ |
| D5-HANDOFF | 交接包完整性 | validate_handoff_package | MEDIUM | ✅ |
| D5-CONTRACT-IMPL | 蓝图接口 vs 代码实现 | contract_implementation_detector | HIGH | 📋 |
| D5-SEMANTIC | YAML 间语义一致性 | semantic_drift | HIGH | 📋 |
| D5-DB-SCHEMA | DB Schema 三方对账 | db_schema_drift | HIGH | 📋 |
| D5-DEP-VER | 依赖版本一致性 | dep_version_drift | MEDIUM | 📋 |
| D5-SECURITY | 安全策略漂移 | security_policy_drift | HIGH | 📋 |
| D5-DOC-COEVOL | 文档-代码共演化 | doc_code_coevolution | MEDIUM | 📋 |
| D5-TEST-COV | 测试覆盖漂移 | test_coverage_drift | MEDIUM | 📋 |
| AI-IMPORT | AI 幻觉 import | ai_hallucination_import | HIGH | 📋 |
| AI-DEAD-CODE | AI 死码积累 | ai_dead_code | MEDIUM | 📋 |
| AI-BROKEN-LOGIC | AI 逻辑断裂 | ai_broken_logic | HIGH | 📋 |
| AI-DUP-FUNC | AI 重复功能 | ai_duplicate_functionality | MEDIUM | 📋 |
| AI-STYLE | AI 跨 session 风格漂移 | ai_session_style_drift | LOW | 📋 |
| AI-DEPRECATED-API | AI 知识污染 | ai_knowledge_pollution | MEDIUM | 📋 |

---

## 4. AI 施工场景专用检测器

### 4.1 为什么需要 AI 专用检测器

100% AI 施工 + 1人维护场景下，漂移有独特的产生模式，专业机构方案不会覆盖：

| AI 特有模式 | 传统检测器能否发现 | 需要的新检测能力 |
|---|---|---|
| 跨 session 不记忆→微调积累 | ❌ 每次只比 current vs current，看不出累积漂移 | Baseline diff + slow creep detection |
| 幻觉 import——引用不存在的模块 | ❌ 现有检测器检查"路径是否在磁盘"，但幻觉引用的是代码语义实体 | AST import 分析 + 模块存在性验证 |
| 上下文窗口截断→半成品代码 | ⚠️ 部分（TODO检测），但逻辑断裂检测不到 | AST 控制流分析 + 未使用定义检测 |
| 训练数据过时→废弃 API 用法 | ❌ 无法静态检测 | 废弃 API 知识库 + import 对照 |
| 重复造轮子——不知道已有实现 | ⚠️ 蓝图层有查重，代码层无 | 跨模块函数签名相似度 |
| 模型升级→行为风格变化 | ❌ | 基线快照 + 风格 lint 变化率 |

### 4.2 检测器设计详情

```yaml
ai_detectors:
  ai_hallucination_import:
    priority: "P0——AI 施工场景头号问题"
    method: |
      1. AST 解析目标模块所有 .py 文件
      2. 提取所有 import X / from X import Y 语句
      3. 对每个 X:
         a. 检查 sys.path 中是否存在 X（标准库/第三方库）→ 跳过
         b. 检查 X 是否为 zephyr 内部模块（src/zephyr/**/X.py 存在）→ 标记
         c. 检查 X 是否在 _detector_registry.yaml 中注册 → 标记
         d. 若 X 不满足 a/b/c → 幻觉引用 → 生成修复建议（删除/替换）
    auto_fixable: false

  ai_broken_logic:
    priority: "P1"
    sub_checks:
      - name: "context_window_truncation"
        method: |
          检测函数签名极复杂但实现体极短（签名参数 > 5 且 实现体 < 3 行）
          → 典型上下文窗口截断签名
      - name: "not_implemented_without_fallback"
        method: |
          检测 raise NotImplementedError 的所有位置
          若调用方没有 try/except 包裹 → 运行时必崩
      - name: "todo_ratio"
        method: |
          模块内 TODO/FIXME/PLACEHOLDER/TBD 行数 / 总行数
          若 > 5% → 标记为高 TODO 密度模块
    auto_fixable: false

  ai_duplicate_functionality:
    priority: "P2"
    method: |
      1. 对所有模块的公开函数签名做归一化（函数名 → lowercase + 移除下划线 + 去重词）
      2. Jaccard 相似度 > 0.7 的函数对 → 标记为疑似重复
      3. 进一步对比参数签名（参数名 + 类型注解 + 返回类型）
      4. 生成合并建议：列出两个实现 → 推荐保留哪个（基于实现完整度/测试覆盖）
    auto_fixable: false

  ai_session_style_drift:
    priority: "P3"
    method: |
      按模块分组——同一模块内：
      - 是否混用 dataclass 和 pydantic BaseModel
      - 是否混用 sync 和 async 函数
      - 命名规范是否一致（snake_case vs camelCase）
    auto_fixable: false

  ai_knowledge_pollution:
    priority: "P2"
    method: |
      1. 维护 deprecated_api_kb.yaml——已知废弃 API 清单
         （如：SQLAlchemy 1.x session.query() → 2.x select()）
      2. AST 扫描所有函数调用 → 与 deprecated_api_kb 匹配
      3. 命中 → 生成升级建议（含正确用法的文档链接）
    auto_fixable: false

  ai_cross_session_repair_conflict:
    priority: "P1"
    method: |
      在 drift_events 表中查询：
      同一 drift_id → 被多个不同 session_id 修复 → 标记为冲突修复
      检查最后一次修复后漂移是否真的消除
    auto_fixable: false
```

---

## 5. 可观测性与运维

### 5.1 时序存储与趋势分析（决策 D-023-08）

> **决策 D-023-08**：每个 scan 周期产出的漂移事件写入 SQLite drift_events 表，形成时序数据。趋势分析回答三个问题：哪个模块越来越容易漂移？哪种漂移类型发生频率在上升？漂移修复速率是否能跟上产生速率？
>
> **决策依据**：没有时序存储，trend analysis 就是空谈。SQLite 足够（单节点场景），无需引入 Prometheus/InfluxDB。

```yaml
time_series:
  storage:
    engine: "SQLite drift_events 表（已在 2.3 定义）"
    retention: "90 天热数据 + 按年归档到 JSONL"

  metrics:
    - name: "drift_velocity"
      description: "每个模块每周新产生的漂移事件数"
      aggregation: "COUNT(*) GROUP BY module_id, week"
      alert: "单模块 velocity > 5/week → 模块设计可能有问题"

    - name: "drift_resolution_rate"
      description: "状态变为 VERIFIED 的漂移 / 总漂移"
      aggregation: "COUNT(state=VERIFIED) / COUNT(*) per module per month"
      alert: "resolution_rate < 50% → 修复跟不上产生"

    - name: "mean_time_to_resolve"
      description: "从 DETECTED → VERIFIED 的平均时间"
      alert: "MTTR > 7 days → 升级"

    - name: "detector_false_positive_ratio"
      description: "FALSE_POSITIVE 标记数 / 该 detector 总触发数"
      aggregation: "per detector"
      alert: "> 30% false positive → detector 规则需调整"

  trend_alerts:
    - type: "spike"
      description: "单次 scan 漂移数 > 历史均值 + 3σ"
    - type: "slow_growth"
      description: "连续 4 周 drift_velocity 单调递增"
    - type: "silence"
      description: "连续 48h 零漂移（可能是检测器损坏，不是系统健康）"
```

### 5.2 关联引擎（决策 D-023-09）

> **决策 D-023-09**：模块间漂移关联分析——当模块 A 发生漂移时，检查模块 B 是否也在相近时间发生同维度漂移。使用简单的 Pearson 相关系数 + Jaccard 相似度。
>
> **决策依据**：系统性架构问题往往表现为多模块同时漂移。单模块视角看不到全局模式。

```yaml
correlation_engine:
  methods:
    - name: "co_occurrence"
      description: "同一 scan 周期内，哪些模块对经常同时出现漂移"
      algorithm: "Jaccard(模块A的scan_id集合, 模块B的scan_id集合)"

    - name: "causal_chain"
      description: "模块A先漂移 → 模块B随后漂移（A 依赖 B 或 B 依赖 A）"
      algorithm: "按时间排序的漂移事件 → Granger 因果关系检验（简化版）"

    - name: "dimension_cluster"
      description: "同一维度（如 D5-CONTRACTS）在哪些模块集中出现"
      algorithm: "对 detector_id 做模块聚类"

  output:
    - "漂移关联热力图——模块 × 模块 漂移共现矩阵"
    - "系统性风险告警：{N} 个模块在 {dimension} 维度同时漂移 → 可能根因在基础设施"
```

### 5.3 覆盖率仪表板

```yaml
coverage_dashboard:
  views:
    - name: "detector_coverage_matrix"
      description: "漂移维度 × 检测器 矩阵——哪些维度已有检测、哪些是盲区"
    - name: "module_health_index"
      description: "每个模块的综合漂移评分 = velocity × severity × resolution_rate"
    - name: "drift_heatmap"
      description: "按时间轴的漂移事件热力图——一眼看出哪个时段/模块最不稳定"

  export:
    - format: "MCP Tool call → 返回 JSON 摘要（< 500 token）"
    - format: "CLI 报告 → 文本表格"
```

### 5.4 告警路由与疲劳管理（决策 D-023-13）

> **决策 D-023-13**：定义告警路由策略——不同严重度、不同模块优先级的漂移走不同通知渠道。引入智能去重和聚合，避免告警风暴。
>
> **决策依据**：1人维护场景下，告警疲劳是最大的 operational risk。需要分级路由 + 自动聚合摘要。

```yaml
alert_routing:
  channels:
    P0_CRITICAL:
      description: "P0 模块漂移预算耗尽 / 自漂移检测失败 / 回滚验证失败"
      channel: "即时通知（Feishu @owner + 终端告警）"
      ack_required: true
      ack_timeout: "30min 未确认 → 升级（重复通知）"

    P0:
      description: "HIGH severity 漂移（AI 幻觉 import / 契约破坏 / SSoT 不一致）"
      channel: "Feishu 群消息（非 @）"
      ack_required: false
      aggregation: "每小时聚合一次 → 发送摘要（非逐条）"

    P1:
      description: "MEDIUM severity + 趋势告警"
      channel: "每日摘要报告（Feishu 定时推送）"
      ack_required: false

    P2:
      description: "LOW severity + 信息类"
      channel: "不推送——仅在 dashboard 可见"
      ack_required: false

  deduplication:
    - method: "同一 (module_id, detector_id, drift_dimension) 组合在 6h 内只告警一次"
    - method: "若同一漂移在连续 3 次 scan 中均出现 → 聚合为 persistent_alert"

  grouping:
    - method: "同一 scan 周期内 > 10 个漂移 → 聚合为 batch_alert（列出 TOP 3 + 总计 N）"
    - method: "同一根因（correlation engine 发现）→ 聚合为 causal_group_alert"

  silence_policy:
    - "夜间（22:00-08:00）→ 仅 P0_CRITICAL 通知"
    - "周末 → 仅 P0_CRITICAL + P0 聚合摘要（每条延迟到周一）"
    - "Owner 可声明 focus_time（2h 免打扰窗口）"
```

### 5.5 修复 ROI 优先级引擎（决策 D-023-14）

> **决策 D-023-14**：当同时存在多个漂移时，按 ROI（投入产出比）排序——不是"先检测到的先修"，而是"修了收益最大的先修"。ROI = impact × frequency / estimated_effort。
>
> **决策依据**：1人+AI 维护下，修复资源有限。盲目按时间或严重度排序会导致"修了一堆 P2，P0 还在漂"。

```yaml
roi_priority:
  formula: "ROI = (impact_weight × frequency_score) / effort_score"

  impact_weight:
    P0_module: 10
    P1_module: 5
    P2_module: 2
    # 基础权重 × 漂移严重度系数（HIGH=3, MEDIUM=2, LOW=1）

  frequency_score:
    description: "该漂移在近 30 天内被检测到的次数"
    scale: "1 + log2(frequency)  # 出现 1 次=1, 出现 4 次=3, 出现 16 次=5"

  effort_score:
    auto_fixable: 1
    needs_suggestion_simple: 3
    needs_suggestion_complex: 8
    needs_human: 20

  sort: "ROI 降序 → Top N 推送给 Owner / AI 修复队列"

  feedback:
    description: "实际修复耗时 vs effort_score —— 持续校准 effort 估算"
```

### 5.6 漂移溯源——Git Bisect 集成（决策 D-023-15）

> **决策 D-023-15**：当漂移被检测到时，自动 git bisect 定位引入漂移的 commit。利用 drift_events 的 created_at 时间窗口缩小 bisect 范围。
>
> **决策依据**：AI 施工场景下，漂移的根因溯源比修复本身更重要——知道"哪个 AI session 引入的"才能避免同样问题再次发生。传统 drift detection 只告诉你"漂了"，不告诉你"谁干的、什么时候干的"。

```yaml
git_bisect_integration:
  trigger: "DETECTED 事件——非周期性漂移（周期性漂移通常是系统性问题，非单点引入）"

  scope_narrowing:
    - "last_known_good: 上次 DEEP scan PASS 的 commit hash"
    - "first_known_bad: 当前 HEAD"
    - "bisect_range: [last_known_good, first_known_bad]"
    - "若范围 > 50 commits → 提示 Owner 缩小范围（可能基线过期）"

  automation:
    - "git bisect start first_known_bad last_known_good"
    - "对每个 bisect step → 跑触发该漂移的 detector（LIGHT 扫描）"
    - "detector PASS → git bisect good"
    - "detector FAIL → git bisect bad"
    - "定位到引入 commit → 记录到 drift_events.root_cause_commit"

  output:
    - "root_cause_commit: <hash>"
    - "author: <git author>"
    - "commit_message: <message>"
    - "changed_files: [list]"
    - "ai_session_hint: 从 commit message 中提取 session_id（若 AI commit 规范中包含）"

  bisect_cache:
    description: "缓存已 bisect 的 detector × commit 结果——避免重复跑"
    ttl: "永久（同一 commit 对同一 detector 的结果不变）"
```

---

## 6. 深度集成

### 6.1 Evolution Engine 反馈闭环（决策 D-023-10）

> **决策 D-023-10**：漂移时序数据定期喂给 Evolution Engine（`feedback_loop/evolution_engine.py`）。高频漂移模块的蓝图设计应被标记为"需要重构"或"接口设计有问题"。
>
> **决策依据**：漂移不只是需要修的问题——它是蓝图设计质量的信号。反复漂移 = 蓝图边界不清晰。

```yaml
evolution_integration:
  trigger: "每次 DEEP scan 完成后"
  payload:
    - module_id: "漂移模块"
    - drift_velocity_30d: "近 30 天漂移速度"
    - top_drift_dimensions: "最高频漂移维度 TOP 3"
    - suggested_action: "EVOLVE_BLUEPRINT | ADD_CONTRACT | SPLIT_MODULE"
  feedback_loop: "Evolution Engine → 更新 blueprint_scorer → 调整模块评分 → 影响施工优先级"
```

### 6.2 语义漂移检测

```yaml
semantic_drift:
  description: "YAML 间语义一致性检测——超越数字和路径层面的对比"
  checks:
    - name: "concept_cardinality"
      description: "同一概念（如'核心服务'）在 YAML-A 中定义了 N 个条目，在 YAML-B 中列出了 M 个名字"
      method: "跨 YAML 文件的实体名称集合对比——差异 > 0 → 语义漂移"
    - name: "enum_value_sync"
      description: "枚举值（如 status: [draft, review, approved]）在两个 YAML 中是否一致"
      method: "提取同名字段的枚举值集合并比对"
    - name: "ownership_consistency"
      description: "同一功能/模块的 owner 字段在多处是否一致"
```

### 6.3 DB Schema 漂移

```yaml
db_schema_drift:
  description: "SQLite schema vs ORM model vs migration 文件三方对账"
  checks:
    - name: "schema_vs_orm"
      method: "sqlite_master 中的表结构 vs SQLAlchemy/peewee model 定义"
    - name: "orm_vs_migration"
      method: "ORM model 字段 vs 最新 migration 文件中的字段"
    - name: "index_consistency"
      method: "ORM 中声明的索引 vs 数据库中实际索引"
```

### 6.4 依赖版本漂移

```yaml
dep_version_drift:
  description: "requirements.txt vs 实际 pip freeze"
  method: "subprocess.run(['pip', 'freeze']) → 解析 → 与 requirements.txt 行级对比"
  auto_fixable: true
  auto_fix_action: "自动更新 requirements.txt 为实际安装版本"
  caution: "自动更新需保留版本范围约束（>=, ~=）的语义，不可暴力锁定为 == 精确版本"
```

### 6.5 安全策略漂移

```yaml
security_policy_drift:
  description: "安全规范要求 vs 所有端点实际实现"
  checks:
    - name: "input_sanitization_coverage"
      method: "扫描所有 HTTP/CLI 入口点 → 检查是否每个入口都有 input_sanitizer 调用"
      reference: "src/zephyr/llm_security/input_sanitizer.py"
    - name: "auth_middleware_coverage"
      method: "检查所有 API 路由是否经过认证中间件"
    - name: "secrets_in_code"
      method: "复用 Gate Engine 的 secrets_detection CheckType——运行时而非仅 CI"
```

### 6.6 文档-代码共演化

```yaml
doc_code_coevolution:
  description: "代码改了但文档/蓝图没更新 = 反向漂移"
  checks:
    - name: "code_newer_than_blueprint"
      method: "max(代码文件 mtime) > blueprint.md mtime + 7 天 → 标记文档滞后"
    - name: "blueprint_interface_vs_code"
      method: "蓝图 §3 声明的接口列表 vs 代码实际公开接口——任一方向不一致 → 漂移"
```

### 6.7 测试覆盖漂移

```yaml
test_coverage_drift:
  description: "模块代码增长但测试比例下降"
  method: "定期统计每个模块的代码行数 vs 测试行数 → 比率趋势"
  alert: "覆盖率月环比下降 > 10%"
```

### 6.8 AI 上下文注入——施工前预检（决策 D-023-16）

> **决策 D-023-16**：在 AI 每次施工前，自动注入模块的漂移状态上下文——让 AI 在开发时就知道"这个地方有漂移，注意不要踩雷"。上下文注入分为三级：minimal（< 100 token）、standard（< 300 token）、full（完整 drift report）。
>
> **决策依据**：AI 不记忆跨 session 状态，施工前不告诉它漂移情况，它就会在漂移区域继续施工——导致漂移叠加。注入上下文是预防性措施，比事后修复便宜 10 倍。

```yaml
ai_context_injection:
  levels:
    minimal:
      description: "仅模块健康摘要——适合快速 task"
      content: "模块 {id} 漂移健康度: {score} | 活跃漂移: {n} | 预算剩余: {budget_left}/{budget_total}"
      token_budget: "< 100"

    standard:
      description: "活跃漂移清单 + 修复状态——适合常规 task"
      content: "活跃漂移 TOP 3（按 ROI 排序）+ 对应的修复建议/状态"
      token_budget: "< 300"

    full:
      description: "完整 drift report——适合 phase 验收前 task"
      content: "全部活跃漂移 + 趋势数据 + 关联模块漂移 + 历史基线 diff"
      token_budget: "< 1000"

  injection_point:
    - "session_manager 派发 task 时 → 从 drift_engine 查询模块状态 → 注入到 task context"
    - "MCP Tool `discover_applicable_gates` 返回结果中包含 drift context 字段"

  effect:
    - "AI 看到模块有活跃漂移 → 优先修复漂移而非新增功能"
    - "AI 知道预算即将耗尽 → 谨慎施工，减少引入新漂移的风险"
    - "AI 看到基线 diff → 理解模块的设计意图，避免偏离设计"
```

### 6.9 漂移演练手册自动生成

```yaml
drift_runbook:
  description: "每个漂移事件自动生成一份结构化演练手册，供 AI/Owner 按步骤修复"
  content:
    - metadata:
        - "漂移 ID / 模块 / 检测器 / 发现时间 / ROI 评分"
    - diagnosis:
        - "漂移描述（自然语言）"
        - "期望状态 vs 实际状态（结构化 diff）"
        - "根因分析（git bisect 结果 / 关联漂移）"
    - remediation:
        - "修复步骤（若 auto_fixable → 可以直接执行的命令/脚本）"
        - "若 needs_suggestion → 提供 2-3 种修复方案 + 推荐方案 + 理由"
        - "每步的验证方法（修复后如何确认成功）"
    - rollback:
        - "修复失败时的回滚步骤"
        - "回滚验证方法"
    - references:
        - "相关蓝图章节链接"
        - "相关 ADR 链接"
        - "历史类似漂移的处理记录"

  format: "Markdown + YAML frontmatter（机器可解析 + 人类可读）"
  storage: "data/drift_runbooks/<event_id>.md"
  ttl: "漂移 VERIFIED 后保留 30 天作为知识资产"
```

### 6.10 知识图谱实体化

```yaml
knowledge_graph_integration:
  description: "将漂移事件、检测器、模块、根因作为知识图谱实体——支持图谱查询和推理"

  entities:
    - type: "DriftEvent"
      relations:
        - "DETECTED_BY → Detector"
        - "AFFECTS → Module"
        - "INTRODUCED_BY → Commit"
        - "CORRELATED_WITH → DriftEvent"
        - "RESOLVED_BY → Session/AI"

    - type: "Detector"
      relations:
        - "COVERS → DriftDimension"
        - "PRODUCES → DriftEvent"

    - type: "Module"
      relations:
        - "DEPENDS_ON → Module"
        - "HAS_BUDGET → DriftBudget"
        - "AFFECTED_BY → DriftEvent"

  queries:
    - "哪些检测器从未产生过漂移？（可能太宽松）"
    - "哪些模块的漂移总是成对出现？（因果关系）"
    - "最近的漂移热点区域在哪？（最多漂移的子图）"

  implementation: "通过 mcp_Knowledge_Graph_Memory MCP server 读写"
```

### 6.11 检测器金丝雀部署（Canary Deployment）

```yaml
detector_canary:
  description: "检测器逻辑更新时，先以 shadow 模式对比新旧版本——确认行为变更符合预期后再全量切换"

  workflow:
    1. "新版本检测器部署为 canary_detector（独立 ID，结果不入 drift_events）"
    2. "对 N 个代表性模块同时跑 v1 和 v2 → 对比结果差异"
    3. "差异分类：NEW_FINDING（v2 发现 v1 没发现）/ LOST_FINDING（v1 发现 v2 没发现）/ CHANGED_SEVERITY"
    4. "Owner 审查差异 → approve → 全量切换 / reject → 回退 v2"

  metrics:
    - "false_positive_rate_change: v2 FP% - v1 FP%"
    - "new_findings_count / lost_findings_count"
    - "execution_time_change_ms"

  auto_rollback:
    condition: "v2 false_positive_rate > 2 × v1 false_positive_rate"
    action: "自动回退 v2，通知 Owner"
```

### 6.12 漂移作为 AI 训练数据闭环

```yaml
drift_training_loop:
  description: "漂移事件（尤其是 FALSE_POSITIVE 和频繁重复的漂移模式）反馈到 AI 施工的 system prompt，降低未来产生同类漂移的概率"

  pattern_extraction:
    - "聚合 30 天内频率最高的漂移维度 + 根因 commit 的 diff pattern"
    - "提取'AI 容易出错'的代码模式（如：忘记更新 blueprint-registry.yaml / 路径拼写错误 / 混用 sync/async）"

  injection:
    - "将高频漂移模式注入到 AGENTS.md 或施工 system prompt 中"
    - "格式：'常见漂移警示：在做 {action} 时，AI 经常忘记同步更新 {target}。请确认你已更新。'"

  effectiveness:
    - "追踪注入前后同类漂移的发生率变化"
    - "若下降 > 50% → 固化到 AGENTS.md §6.x"
    - "若无变化 → 说明这个 pattern 不适合 prompt 层面解决，需代码层强制执行"
```

### 6.13 混沌工程——主动漂移注入

```yaml
chaos_drift_injection:
  description: "定期主动注入可控漂移——测试 drift detector 的检测灵敏度和修复能力。与'故障演练'同理——不测试就不知道检测器是否真的有效"

  injection_types:
    - type: "path_rename"
      description: "随机重命名一个非关键文件 → 验证 blueprint_code_sync 检测器是否发现"
    - type: "yaml_field_flip"
      description: "将某个 YAML 字段值改为合法但不正确的值 → 验证语义漂移检测器"
    - type: "fake_todo_bomb"
      description: "在非关键模块注入高密度 TODO → 验证 broken_logic 检测器"
    - type: "import_hallucination"
      description: "注入一条不存在的 import → 验证 AI 幻觉检测器"

  schedule: "每周一次自动混沌演练（在维护窗口内执行）"

  safeguards:
    - "仅对 P2 模块注入（零生产影响）"
    - "注入前自动拍 pre-chaos 基线"
    - "检测通过后自动回滚注入（恢复 pre-chaos 状态）"
    - "若检测器未发现 → 标记检测器为 DEGRADED → 通知 Owner"

  metrics:
    - "detection_rate: 混沌注入被检测到的比例"
    - "time_to_detect: 注入到被检测到的延迟"
    - "false_negative_trend: 未被检测到的注入是否在增加"
```

### 6.14 跨 Session 修复上下文交接

```yaml
session_handoff:
  description: "AI session-1 检测到漂移并生成修复建议 → AI session-2 接手修复时，需要完整的上下文交接包"

  handoff_package:
    built_from:
      - "drift_runbook（6.9 生成的演练手册）"
      - "git bisect 结果（谁引入的、为什么引入）"
      - "pre-fix 快照（修复前的状态）"
      - "baseline diff（期望状态 vs 实际状态的完整差异）"
      - "关联漂移（是否有其他漂移需要在同一修复中处理）"

    format: "单个 JSON 文件 → data/drift_handoffs/<event_id>.json"
    size_constraint: "< 5000 token（确保 AI 上下文窗口能完整加载）"

  resume_workflow:
    1. "AI session-2 收到 task: '修复 drift {event_id}'"
    2. "自动加载 handoff_package → 注入到 context"
    3. "AI 按照演练手册步骤执行修复"
    4. "修复完成后 → 状态机推进到 RESOLVED"
    5. "下次 scan 验证 → VERIFIED"

  abort_condition:
    description: "若在修复过程中发现演练手册已过时（文件状态与手册描述不一致）"
    action: "重新生成演练手册（基于当前实际状态）→ 通知 Owner 确认"
```

### 6.15 级联故障检测——修复引入新漂移的循环中断（决策 D-023-22）

> **决策 D-023-22**：修复漂移 A → 引入漂移 B → 修复漂移 B → 引入漂移 C → ... 这是 AI 自动修复最危险的模式。引入级联检测——同一模块在 30 分钟内出现 ≥ 3 次新漂移且每次都被修复 → 判定为 cascade → 停止自动修复 → 通知 Owner。
>
> **决策依据**：AI 修复可能"治标不治本"——改对了语法但破坏了语义。不加控制的自动修复链会导致系统在非人工干预下持续恶化。

```yaml
cascade_detection:
  trigger: |
    drift_events 中同一 module_id:
    - 30min 内 NEW drift events ≥ 3（不包括首次发现漂移）
    - 且每次前一个被修复（state → RESOLVED/VERIFIED）后新漂移出现
    - 判定：CASCADE_DETECTED

  action:
    - "暂停该模块的自动修复——锁定 1h"
    - "所有新检测到的漂移归入 bulk_cascade_event"
    - "P0 通知 Owner：'模块 {id} 进入修复级联循环——{N} 次修复→新漂移循环'"
    - "生成完整的 cascade_forensics report：每次修复的 diff + 引入的新漂移"

  recovery:
    description: "Owner 确认根因并手动修复 → 解除 cascade lock"
    post_fix: "全量 DEEP scan → 验证链路的终止状态"

  prevention:
    description: "自动修复前做 dry-run 影响面分析"
    method: |
      修复 committed 前——在临时目录模拟应用修复 diff
      → 对变更文件跑所有关联检测器
      → 若预检出"新漂移"→ 阻止修复 → 通知 Owner
```

### 6.16 资源上限与优雅降级（决策 D-023-23）

> **决策 D-023-23**：1500 模块 DEEP scan 需定义资源上限——内存、磁盘 I/O、Python 进程数。超限时优雅降级而非 OOM 崩溃。定义降级路径：减少并行度 → 延长 SLO → 暂停非关键检测器。
>
> **决策依据**：单机场景下资源有限。Drift detector 不能无限膨胀。

```yaml
resource_limits:
  hard_limits:
    memory: "max 512MB（Python 进程 RSS）——超过则减少并行度"
    disk: "data/drift_baselines/ + data/drift_checkpoints/ + drift_events.db 合计 < 2GB"
    open_files: "max 200 个文件句柄"

  graceful_degradation:
    tier_1: "内存 > 384MB → 并行度减半（8→4 / 4→2）"
    tier_2: "内存 > 448MB → 暂停非 HIGH severity 检测器"
    tier_3: "内存 > 500MB → 触发 GC + 暂停当前 scan → checkpoint → 等待 5min 后重试"
    tier_4: "OOM 前 30s 预警（psutil.memory_percent > 90%）→ 紧急写 checkpoint → 主动退出"

  garbage_collection:
    description: "每次 DEEP scan 结束后自动清理"
    actions:
      - "清理超过 retention 期的 baseline 快照"
      - "VACUUM SQLite drift_events（删除 VERIFIED > 30 天的记录）"
      - "压缩旧的 runbook markdown 文件"

  scalability_validation:
    scaffold: "10 模块 → 验证基础功能"
    experimental: "100 模块 → 验证并行调度 + 资源使用"
    beta: "500 模块 → 验证 storm mode + cascade detection"
    production: "1500 模块 → 全量压力测试——必须控制在 2GB 磁盘 / 512MB 内存以内"
```

### 6.17 漂移取证——时间点系统状态回放

```yaml
drift_forensics:
  description: "重建'在时间 T 的系统状态是什么'——用于事后分析漂移链路的完整上下文"

  replay_capability:
    - "给定时间 T → 从 git 历史还原当时的代码状态（git checkout <hash_at_T>）"
    - "给定时间 T → 从 drift_events 表查询当时活跃的漂移（created_at ≤ T 且 resolved_at > T 或 null）"
    - "给定时间 T → 从 baseline 历史找到当时最新的基线快照"

  forensics_report:
    trigger: "P0 CRITICAL 事件 或 Owner 手动触发"
    content:
      - "timeline: 漂移事件的完整时间线（引入→发现→修复→验证）"
      - "state_diffs: 每个关键时间点的 baseline vs current diff"
      - "actor_trace: 每个操作的执行者（AI session ID / git author）"
      - "dependency_impact: 漂移影响了哪些下游模块"
    format: "Markdown → data/drift_forensics/<event_id>.md"

  use_cases:
    - "为什么这个模块连续漂了 4 周？→ 回放发现是因为依赖的接口每次微调一点"
    - "上次大规模重构到底改了哪些？→ 回放 storm 前后的完整差异"
```

### 6.18 跨语言漂移检测框架

```yaml
multi_language_drift:
  description: "当前项目主要为 Python，但架构已预留跨语言扩展。Drift detector 的检测维度应支持非 Python 语言"

  language_agnostic_dimensions:
    description: "以下维度不依赖特定语言——可跨语言复用"
    dimensions:
      - "D5-YAML-DISK: YAML 注册表 vs 磁盘文件（任何语言都有文件）"
      - "D5-MANIFEST: 静态清单生成器一致性（manifest 是语言无关的）"
      - "D3-D5-NUM: MD vs YAML 数字漂移（纯数据对账）"
      - "D5-DIR: 目录结构规范（树结构是语言无关的）"
      - "D5-SEMANTIC: YAML 间语义一致性（数据层）"
      - "D5-DB-SCHEMA: DB Schema 三方对账"
      - "D5-DEP-VER: 依赖版本一致性（用对应语言的包管理工具）"
      - "D5-SECURITY: 安全策略（规则是语言无关的，实现是语言特定的）"
      - "D5-DOC-COEVOL: 文档共演化"

  language_specific_extension:
    description: "每种新语言只需实现 3 个接口即可集成"
    interfaces:
      - "parse_imports(): 解析该语言的 import/dependency 声明"
      - "parse_public_api(): 提取公开接口签名（函数/类/方法）"
      - "detect_dead_code(): 死码检测（语言特定的 AST/静态分析工具）"
    supported_languages: "[Python]（当前），TypeScript / Go / Rust（预留接口）"
```

### 6.19 供应商锁定与基础设施迁移漂移

```yaml
vendor_lockin_drift:
  description: "当项目的底层基础设施（数据库、消息通知、文件存储）发生变化时，所有依赖模块同时漂移"

  scenarios:
    - type: "db_migration"
      description: "SQLite → PostgreSQL → DuckDB"
      detection: "所有包含 import sqlite3 的模块 + DB schema 检测器"
    - type: "notification_migration"
      description: "Feishu Webhook → Slack API → Email SMTP"
      detection: "所有包含 feishu/slack 调用的模块"

  migration_plan_integration:
    description: "Drift detector 感知迁移计划——在迁移窗口内，因迁移导致的漂移不告警"
    config: "drift_migration_plan.yaml —— 声明式迁移时间表 + 影响模块列表"
```

### 6.20 测试夹具与测试数据漂移（决策 D-023-28）

> **决策 D-023-28**：测试夹具（fixtures）、mock 数据、测试用例的预期输出可能与实际数据 schema 或代码行为漂移。当代码接口变了但测试夹具没更新，"测试仍通过但测的根本不是新逻辑"。
>
> **决策依据**：先干后验模式下，AI 改了业务逻辑但经常不更新测试。更危险的是——测试本身成了"漂移孵化器"：测试仍然通过（因为夹具覆盖了旧路径），但代码已经走了新路径。

```yaml
test_fixture_drift:
  checks:
    - name: "fixture_schema_drift"
      description: "测试夹具中的数据结构 vs ORM model / pydantic schema 定义"
      method: "扫描 conftest.py + tests/**/fixtures/ → 提取所有硬编码的数据结构 → 与对应 model 字段对比"
      example: "fixture 中有 user.age=25 但 User model 已改为 user.birth_date → schema drift"

    - name: "mock_target_drift"
      description: "mock.patch 的目标路径 vs 实际模块路径"
      method: "AST 扫描所有 mock.patch('module.path') → 验证 module.path 是否真实存在"
      severity: MEDIUM

    - name: "expected_output_drift"
      description: "测试中的 assert == expected_value 是否仍有效"
      method: "定期全量跑一遍测试 → 对 PASS 的测试重新检查 expected value 的来源（硬编码？配置文件？）"
      severity: LOW

  auto_fixable: false
  note: "测试漂移是所有漂移中最隐蔽的——因为测试通过不代表系统正确"
```

### 6.21 配置多源一致性——.env × YAML × hardcoded defaults（决策 D-023-29）

> **决策 D-023-29**：同一个配置值可能在 .env、config/*.yaml、Python 代码中的硬编码默认值三个地方同时存在。三者不一致时——三个都是"对"的（各自在其上下文中），但系统行为取决于加载顺序。检测三源配置漂移并统一为 YAML SSoT。
>
> **决策依据**：氛围编程社区非常容易出现"AI 在代码里硬编码了一个 API URL，但 .env 里配了另一个"的问题。这在单机上表现为"偶尔对偶尔错"的幽灵 bug。

```yaml
config_source_consistency:
  sources:
    - name: "env_file"
      path: ".env + .env.example"
    - name: "yaml_config"
      path: "config/**/*.yaml"
    - name: "hardcoded_defaults"
      method: "AST 扫描代码中的 os.getenv('KEY', 'default_value') → 提取 default_value"

  cross_source_check:
    description: "同一个配置键（如 DATABASE_URL）在三个源中的值"
    action: |
      提取所有配置键 → 对每个键：
      - 若 .env 有、YAML 有、默认值有、且三者不同 → CONFIG_CONFLICT
      - 若 .env.example 有、.env 无 → MISSING_SECRET_WARNING
      - 若 YAML 有、代码中从未被读取 → UNUSED_CONFIG

  resolution_policy:
    description: "YAML 为 SSoT——.env 和硬编码默认值必须在 YAML 中有对应声明"
    auto_fix: "生成 config_sync.yaml——列出需要同步的三源差异 → Owner 审查后一键应用"
```

### 6.22 Python 版本兼容性漂移（决策 D-023-30）

> **决策 D-023-30**：项目声明的 Python 版本范围（如 3.11+）vs 代码中实际使用的语法特性（如仅 3.12+ 支持的 type statement）。检测版本兼容性漂移——看似正确的代码在目标版本上实际无法运行。
>
> **决策依据**：AI 的训练数据可能包含最新 Python 版本的语法，但它不知道你的项目目标版本。这在 100% AI 施工中是高频问题——AI 用了 match/case（3.10+）但你的项目还声明支持 3.9。

```yaml
python_version_drift:
  target_version_source: "pyproject.toml 中的 requires-python 或 setup.py 中的 python_requires"

  checks:
    - name: "syntax_incompatibility"
      method: "pyright / mypy 在目标 Python 版本下做类型检查 → 标记不兼容的语法特性"
      example: |
        pyproject.toml: requires-python = ">=3.11"
        代码中: type Point = tuple[float, float]  # type statement 需要 3.12+

    - name: "stdlib_import_incompatibility"
      method: "扫描 import 语句 → 检查目标 Python 版本是否包含该标准库模块"
      example: "import tomllib → 仅 3.11+ / import zoneinfo → 仅 3.9+"

    - name: "type_hint_incompatibility"
      method: "检查类型注解语法是否与目标版本兼容"
      example: "dict[str, int] vs Dict[str, int] / X | Y vs Union[X, Y]"

  severity: HIGH
  auto_fixable: true
  auto_fix_action: "自动降级不兼容语法到目标版本最低支持形式"
```

### 6.23 向后兼容策略漂移（决策 D-023-31）

> **决策 D-023-31**：模块的公开 API 如果改变了函数签名、删除了参数、修改了返回类型——这是"破坏性变更"。在没有语义版本控制的情况下，没有人知道下游模块是否受影响。检测 API 的向后兼容性漂移。
>
> **决策依据**：AI 施工不遵守 SemVer——它可能直接删掉"看起来没用"的参数。而你的下游模块还依赖那个参数。这是大型 AI 建设项目的典型坍塌模式。

```yaml
backward_compatibility:
  baseline_source: "基线快照中的 interface_snapshot（2.2）"

  checks:
    - name: "removed_parameter"
      method: "基线 function(a, b, c) vs 当前 function(a, b) → c 被移除"
      severity: HIGH

    - name: "changed_return_type"
      method: "基线 → Optional[X] vs 当前 → X（None 可能性消失）"
      severity: HIGH

    - name: "renamed_function"
      method: "基线中的 function_X 在代码中找不到 → 搜索相似签名（Jaccard）判断是否被重命名"
      severity: MEDIUM

    - name: "changed_exception"
      method: "基线文档声明 raise ValueError vs 代码实际 raise CustomError"
      severity: MEDIUM

  impact_analysis:
    description: "标记为 BREAKING 的 API 变更 → 自动扫描所有调用方 → 列出受影响的下游模块"
    output: "BREAKING_CHANGE_REPORT: {api} changed, impacts {N} downstream modules → 修复建议"

  intentional_break:
    description: "Owner 可以将特定 API 变更标记为 INTENTIONAL_BREAK → 解除告警 → 记录到迁移计划"
```

### 6.24 .gitignore 完整性——应追踪但未追踪 / 不应追踪但已追踪（决策 D-023-32）

> **决策 D-023-32**：.gitignore 规则可能过时——新类型的生成文件未被忽略（污染 git status）、或关键配置文件被误忽略（丢失追踪）。检测 .gitignore 规则的有效性和完整性。
>
> **决策依据**：AI 可能生成新的文件类型（如 .pkl / .joblib / .cache），这些应该在 .gitignore 中但 AI 不会主动加。同时 AI 可能通过通配符误忽略了关键配置。

```yaml
gitignore_integrity:
  checks:
    - name: "untracked_generated_files"
      method: "扫描磁盘 → 识别可能是生成的文件（大文件 + 二进制 + 特定扩展名）→ 检查是否在 .gitignore 或已被 git tracked"
      pattern_hints: ["*.pyc", "*.pkl", "*.joblib", "*.cache", "*.db", "*.sqlite", "__pycache__/"]
      severity: LOW

    - name: "over_ignored_critical_files"
      method: ".gitignore 中的规则 → 模拟匹配整个仓库 → 检查是否误匹配了注册表中的 YAML/蓝图/代码"
      example: "*.yaml 在 .gitignore 中 → 所有蓝图被忽略 → 灾难"
      severity: HIGH

    - name: "gitignore_pattern_coverage"
      method: "对比项目文件类型分布 vs .gitignore 覆盖的文件类型"
      action: "若新文件类型出现且未被 .gitignore 覆盖 → 建议添加规则"
```

### 6.25 基线投毒防护——恶意/缺陷基线的事后检测（决策 D-023-36）

> **决策 D-023-36**：基线快照是漂移检测的"真理来源"。如果基线本身有缺陷（被错误代码污染、被恶意篡改），所有后续漂移检测都会失效——真正的漂移被当作"正常"，而正确的修复被当作"漂移"。引入基线完整性验证链和多基线交叉验证。
>
> **决策依据**：前四轮讨论了基线的好处，但从未讨论基线的风险。Git 中保留的原始代码是终极真理来源——定期将基线 vs git HEAD 的原始代码做交叉验证。

```yaml
baseline_poisoning_defense:
  cross_validation:
    description: "定期将基线快照 vs git 中对应 commit 的原始代码做 diff"
    rationale: "基线与 git 不一致 → 基线拍摄时出错或事后被篡改"
    frequency: "每次 DEEP scan 时做抽样交叉验证（10% 的基线随机抽样）"
    action_on_mismatch: "P0 告警 + 标记该基线为 SUSPECT + 触发重新拍摄"

  multi_baseline_voting:
    description: "保留最近 3 个基线版本 → 新的漂移判定需要至少 2 个基线版本'同意'"
    rationale: "单一基线被污染不影响漂移检测——多数基线投票胜出"
    exception: "若 Owner 声明 INTENTIONAL_RESET → 旧基线序列作废，从新基线开始"

  git_as_ultimate_truth:
    description: "Git 的 commit 历史是不可篡改的终极真理来源"
    mechanism: |
      baseline_hash_chain: SHA256(previous_baseline_hash + current_snapshot_hash)
      baseline_hash_chain 写入 git commit message（BASELINE_CHAIN: <hash>）
      任何时刻可验证：baseline snapshot → SHA256 → 与 git commit message 中的链式 hash 比对
    tampering_detection: "链式 hash 不匹配 → 基线被篡改 → P0 CRITICAL"

  integrity_manifest:
    description: "每次 DEEP scan 完成后生成 integrty_manifest.yaml → 签名后存入 Git"
    content:
      - "baseline_version: <version>"
      - "baseline_chain_hash: <hash>"
      - "drift_events_count: <count>"
      - "timestamp: <ISO 8601>"
      - "所有文件在 current HEAD 的 SHA256 树"
    purpose: "事后任何时刻可验证'某个 scan 的结果是否可信'"
```

### 6.26 Drift Detector 自身篡改检测与审计不可变性（决策 D-023-37）

> **决策 D-023-37**：如果攻击者或 bug 破坏了 drift_events.db（删除漂移记录、修改状态），整个漂移检测的审计链就断裂了。Drift_events 必须 append-only + 写入 Git 审计日志。自漂移检测（2.7）需要扩展为包含 drift_events 的完整性检查。
>
> **决策依据**：前四轮的自漂移检测只覆盖了代码文件。但数据（drift_events.db）也是漂移检测器的一部分——数据被篡改 = 检测器被攻破。

```yaml
tamper_proof_audit:
  append_only_events:
    mechanism: "drift_events 表使用 SQLite TRIGGER 禁止 UPDATE/DELETE（仅允许 INSERT）"
    exception: "状态变更通过插入新行 + tombstone 标记实现（event sourcing 模式）"
    rationale: "绝不可修改历史——只能追加新事实"

  git_commit_audit_log:
    description: "每次 DEEP scan 完成后 → 将摘要 commit 到 Git（独立于代码变更）"
    path: "data/drift_audit/AUDIT_<scan_id>.yaml"
    content:
      - "scan_id + timestamp + git_HEAD_hash"
      - "drift_events 当前总行数 + per state 计数"
      - "drift_events 的 SHA256 checksum"
      - "baseline_chain_hash"
    purpose: |
      即使 drift_events.db 被完全删除，
      Git 中的 AUDIT 日志可证明"某时间点的检测状态是什么"。
      用于事后取证的不可变证据链。

  anomaly_detection:
    description: "检测 drift_events 的异常模式——可能是篡改迹象"
    patterns:
      - "drift_events 总行数突然减少（< 上次记录）→ 数据被删除"
      - "无新 DETECTED 事件但大量事件突然变为 VERIFIED（批量清洗）"
      - "drift_events.db 的 mtime < 上次 scan 时间（回溯修改）"
    action: "任一异常 → P0 CRITICAL + 从 Git AUDIT 日志恢复上一已知良好状态"
```

### 6.27 命名约定漂移与魔数字符串常量漂移（决策 D-023-38）

> **决策 D-023-38**：同一模块内混用 `get_user` / `fetchUser` / `retrieve_user` 三种命名约定（AI 跨 session 引入了不一致风格）。同一魔数 `"pending_approval"` 在 5 个文件中以字符串硬编码出现——应提取为常量。检测命名不一致和魔数分散。
>
> **决策依据**：AI 每个 session 有自己的"风格偏好"。5 个 session 迭代同一模块后，命名规则变成大杂烩。魔数分散是 AI 代码生成的常见模式——AI 不知道"别人已经定义过这个常量了"。

```yaml
naming_convention_drift:
  checks:
    - name: "verb_synonym_drift"
      description: "同一语义的动词使用了不同词汇"
      method: "提取所有函数名前缀动词 → 做语义聚类（get/fetch/retrieve = 同义 / create/make/build = 同义）→ 标记不一致"
      action: "生成统一建议：将所有同义动词归一化到模块内最高频的那个"
      auto_fixable: false
      severity: LOW

    - name: "case_style_drift"
      description: "snake_case vs camelCase vs PascalCase 在函数名/变量名中的混用"
      method: "统计模块内各命名风格的使用比例 → 若次要风格 > 10% → 标记"
      auto_fixable: true
      auto_fix_action: "自动转换为模块主流风格"
      severity: LOW

    - name: "prefix_suffix_inconsistency"
      description: "同类函数有无统一前缀（如：is_/has_/can_ 谓词的一致性）"
      method: "返回 bool 的函数中 — 无 is_ 前缀的比例"
      severity: LOW

magic_string_drift:
  checks:
    - name: "duplicated_string_literal"
      description: "同一个非平凡字符串字面量（长度 > 10）在 ≥ 3 个文件中重复出现"
      method: "AST 提取所有字符串字面量 → 过滤短/通用字符串 → 统计出现次数 × 出现文件数"
      example: '"pending_approval" 出现在 config.py、validator.py、models.py、api.py → 应提取为常量'
      action: "生成 EXTRACT_CONSTANT 建议——列出字符串 + 出现位置 + 建议的常量名"
      auto_fixable: false
      severity: MEDIUM

    - name: "near_duplicate_constant"
      description: "不同文件中定义了语义相同但值不同的常量"
      method: "提取所有 CONSTANT_NAME = 'value' → 按 常量名相似度分组 → 检查同组内的值是否一致"
      example: "file_a: TIMEOUT_SECONDS = 30 / file_b: TIMEOUT_SEC = 60 → 疑似重复/冲突"
      action: "生成 MERGE_CONSTANT 建议"
      severity: MEDIUM
```

---

## 7. 文件组成

| 文件 | 职责 |
|------|------|
| `drift_engine.py` | 漂移检测引擎——读取检测器注册表、动态调度现有脚本、汇总结果、写入 drift_events |
| `reconciler.py` | 自动对账器——pre-fix 快照 → 乐观并发检查 → 自动修复 → 验证 → rollback（按 2.5+2.8 策略） |
| `state_machine.py` | 漂移状态机——DETECTED → TRIAGED → ... → VERIFIED（按 2.3 状态图，含 DEAD_LETTER 升级） |
| `baseline_manager.py` | 基线快照管理器——拍摄/存储/对比/版本化管理（按 2.2） |
| `incremental_scanner.py` | 增量扫描器——git diff 驱动，变更影响范围计算（按 2.4） |
| `detector_dispatcher.py` | 检测器调度器——并行调度 + 结果缓存 + SLO 监控（按 2.4） |
| `correlation_engine.py` | 关联分析引擎——漂移共现矩阵 + 因果链分析（按 5.2） |
| `trend_analyzer.py` | 趋势分析器——velocity / resolution_rate / MTTR 时序计算（按 5.1） |
| `roi_engine.py` | ROI 优先级引擎——多漂移排序 + effort 估算校准（按 5.5） |
| `git_bisector.py` | 漂移溯源器——git bisect 自动化 + 根因定位（按 5.6） |
| `runbook_generator.py` | 演练手册生成器——Markdown + YAML 结构化修复手册（按 6.9） |
| `ai_context_injector.py` | AI 上下文注入器——施工前漂移状态注入（按 6.8） |
| `chaos_injector.py` | 混沌漂移注入器——主动注入 + 自动回滚 + 检测器健康验证（按 6.13） |
| `handoff_manager.py` | Session 交接管理器——修复上下文打包/加载（按 6.14） |
| `canary_controller.py` | 检测器金丝雀部署控制器（按 6.11） |
| `cascade_detector.py` | 级联故障检测器——自动修复循环中断 + dry-run 影响面分析（按 6.15） |
| `resource_guard.py` | 资源上限守护——内存/磁盘/句柄监控 + 优雅降级（按 6.16） |
| `forensics_engine.py` | 漂移取证引擎——时间点状态回放 + 取证报告（按 6.17） |
| `drift_models.py` | 数据模型——DriftEvent / Baseline / ScanResult / DriftReport / DriftBudget / Runbook / CascadeEvent / BulkDriftEvent / ForensicsReport / ConfigConflict / BreakingChange / OrphanFile |
| `self_check.py` | 自漂移检测——纯 stdlib，独立于主逻辑（按 2.7） |
| `_detector_registry.yaml` | 检测器注册表——声明式 YAML（机器 SSoT，按 2.1） |
| `dashboard.py` | 覆盖率仪表板——MCP Tool 接口 + CLI 报告生成（按 5.3） |
| `alert_router.py` | 告警路由器——分级通知 + 去重 + 聚合 + 静默策略（按 5.4） |
| `migration_plan.yaml` | 基础设施迁移计划——供应商锁定漂移感知（按 6.19） |
| `orphan_scanner.py` | 孤儿资源扫描器——磁盘 vs 注册表 vs import 引用三方对比（按 2.16） |
| `symlink_checker.py` | 符号链接完整性检查器——断裂/目标变更/循环引用（按 2.17） |
| `file_attr_checker.py` | 文件底层属性检查器——编码/换行符/权限/.gitattributes（按 2.18） |
| `test_fixture_checker.py` | 测试夹具漂移检测器——schema / mock target / expected output（按 6.20） |
| `config_consistency.py` | 配置多源一致性——.env × YAML × 硬编码三角对账（按 6.21） |
| `python_compat.py` | Python 版本兼容性检测器——语法/标准库/类型注解三轴检查（按 6.22） |
| `backcompat_checker.py` | 向后兼容性检测器——API 签名变更 + 下游影响分析（按 6.23） |
| `gitignore_auditor.py` | .gitignore 完整性审计器（按 6.24） |
| `baseline_poisoning_guard.py` | 基线投毒防护——交叉验证 + 多基线投票 + 链式hash（按 6.25） |
| `tamper_proof_audit.py` | 防篡改审计——append-only events + Git AUDIT 日志（按 6.26） |
| `naming_magic_checker.py` | 命名约定/魔数字符串漂移——动词同义词 + 大小写风格 + 重复字面量（按 6.27） |
| `cold_start.py` | 冷启动引导器——bootstrap scan + 基线信任建立（按 2.19） |
| `absence_manager.py` | Owner 缺席管理器——LENIENT/SURVIVAL 模式切换 + 回归交接（按 2.20） |
| `credibility_engine.py` | 告警可信度评分引擎——per detector credibility + 告警调制（按 2.21） |
| `__init__.py` | 包初始化——模块入口 + 公开 API 导出 |
| `gate_persistence.py` | 门禁持久化——scan_result.json + drift_events.db SQLite + manifest.json + SHA256 防篡改 |
| `headless_scanner.py` | Headless 扫描器——LIGHT/DEEP 双模式 + 会话日志中断扫描 |
| `cross_module_score.py` | 跨模块全局健康度评分——加权平均 + 阈值 + 锈化系数 |
| `integration_test_runner.py` | 集成测试运行器——drift 事件触发测试 + 状态机验证 |
| `self_test_verifier.py` | 自测验证器——检测器自我验证 + 8 项收敛检查 |
| `drift_hotfix_bypass.py` | 热修复绕过——[HOTFIX] 识别 + 72h TTL + 审计链 |
| `scan_mutex.py` | 扫描互斥锁——多实例竞态控制 + 碰撞策略 + 扫描合并 |
| `suppression_learner.py` | 假阳性学习——pattern_hash 指纹 + 自动抑制 + 影子观测 |

---

## 8. 施工 Phase 规划

| Phase | 任务 | 状态 |
|:---:|------|:---:|
| **scaffold** | ① 整合现有 80+ 脚本为检测器 + DriftReport 模型 ② drift_events 表 + 基础 DETECTED → RESOLVED 状态机 ③ post-commit LIGHT 增量扫描 ④ 基线快照管理器（minimal——tree_hash + SHA256 manifest） ⑤ AI 幻觉 import 检测器（P0） ⑥ AI 上下文注入——minimal 级别（< 100 token） ⑦ 告警路由（P0_CRITICAL + P0 渠道） ⑧ 崩溃恢复与检查点机制（基本——per detector checkpoint + SQLite 事务安全） ⑨ 热修复旁路（commit message 识别） ⑩ 冷启动引导（bootstrap scan + 初始基线创建） ⑪ append-only drift_events 表（SQLite TRIGGER） | ✅ Done |
| **experimental** | ① 完整漂移状态机（全 10 状态） ② 自动对账 + pre-fix 快照 + 乐观并发控制 + rollback 验证闭环 ③ 契约-代码 AST 对比 ④ AI 死码/逻辑断裂/重复功能检测器 ⑤ 自漂移检测（self_check.py） ⑥ 漂移预算与施工门禁 ⑦ 修复 ROI 优先级引擎 ⑧ 漂移演练手册自动生成 ⑨ 级联故障检测——基础版（30min 窗口 + P0 告警） ⑩ 资源上限与优雅降级——基础版（内存阈值 + 并行度调控） ⑪ 多实例竞态控制 + scan mutex ⑫ 孤儿资源检测——基础版（true_orphan + undocumented_asset） ⑬ 文件底层属性（编码/换行符/权限） ⑭ Python 版本兼容性检测——基础版 ⑮ Owner 缺席模式——基础版（手动 LENIENT/SURVIVAL） ⑯ 告警可信度评分——基础版（per detector fp_rate tracking） | ✅ Done |
| **beta** | ① 时序存储 + 趋势分析（velocity / resolution_rate / MTTR） ② 关联引擎（共现矩阵 + 因果链） ③ 覆盖率仪表板（MCP Tool 接口） ④ 维护窗口 + shadow mode ⑤ Evolution Engine 反馈闭环 ⑥ AI 知识污染 + 风格漂移检测器 ⑦ Git Bisect 溯源集成 ⑧ 告警路由完整版（去重 + 聚合 + 静默策略） ⑨ Session 交接管理器 ⑩ AI 上下文注入——standard + full 级别 ⑪ 漂移风暴与批量处理模式 ⑫ 自动学习假阳性 ⑬ 级联故障检测——完整版（dry-run 影响面分析） ⑭ 跨语言漂移检测框架（接口预留） ⑮ 符号链接 + 子模块完整性 ⑯ 测试夹具漂移 ⑰ 配置多源一致性 ⑱ 向后兼容策略漂移 ⑲ 基线投毒防护（交叉验证 + 多基线投票 + 链式hash） ⑳ 命名约定与魔数漂移 | ✅ Done |
| **production** | ① 语义漂移检测 ② DB Schema / 依赖版本 / 安全策略 / 文档共演化 / 测试覆盖 漂移 ③ 1500 模块规模验证 + 性能调优 ④ 跨 session 修复冲突检测 ⑤ 知识图谱实体化 ⑥ 检测器金丝雀部署 ⑦ 漂移训练数据闭环——pattern → system prompt ⑧ 混沌工程——主动漂移注入 ⑨ 漂移取证——时间点回放 ⑩ 环境感知与渐进部署漂移 ⑪ 供应商锁定与基础设施迁移漂移 ⑫ .gitignore 完整性审计 ⑬ 防篡改审计——Git AUDIT 日志 + 异常检测 ⑭ Owner 缺席模式——完整版（自动检测 + 回归交接报告） ⑮ 告警可信度评分——完整版（自动调制 + Owner override） | ✅ Done |
| **cross-cutting** | G-CT-004 契约执行清单（G-CT-005 via MOD-INF-023 state_machine.trigger_rollback + cascade_detector._trigger_cascade_rollback） | ✅ Done |
| | G-CT-006 depends_on 依赖验证（全 65 张 TASK-INF 卡片 depends_on 一致） | ✅ Done |

---

## 决策记录

| 决策 ID | 决策内容 | 日期 | 依据 |
|---------|---------|------|------|
| D-023-01 | 整合现有 80+ 脚本为检测器，不重写。新增检测器以 YAML 声明式注册 | 2026-05-05 | 80+ 脚本已覆盖大部分场景，重写是浪费；声明式注册降低新增检测器门槛 |
| D-023-02 | 自动对账——可自动修的自动修，不能的生成建议。增加 pre-fix 快照 + 回滚后验证 | 2026-05-05 | 与先干后验一致；回滚验证防止"修坏了但不知道" |
| D-023-03 | 引入 Baseline Snapshot 机制——phase 完成时自动拍摄基线，漂移检测 = baseline vs current | 2026-05-05 | 没有基线无法检测慢蠕变漂移；AI 微调积累是真实威胁 |
| D-023-04 | 漂移事件引入完整生命周期状态机（DETECTED→...→VERIFIED） | 2026-05-05 | 无状态机则跨 session 无追踪能力；DEAD_LETTER 防止漂移被遗忘 |
| D-023-05 | 三级扫描深度 + 性能 SLO + 增量扫描 + 并行调度 | 2026-05-05 | 80+ 脚本全量扫描不可持续；post-commit < 5s 必须增量 |
| D-023-06 | 维护窗口/冻结期——升级期间 shadow mode + per-detector 漂移抑制 | 2026-05-05 | 避免告警风暴掩盖真异常；大版本升级是确定性事件 |
| D-023-07 | 自漂移检测——self_check.py 纯 stdlib，独立验证 drift detector 自身完整性 | 2026-05-05 | Watcher 的 Watcher 不可用自身代码检测自身 |
| D-023-08 | 时序存储 + 趋势分析——drift_velocity / resolution_rate / MTTR | 2026-05-05 | 趋势分析是 beta phase 承诺；SQLite 足够单节点场景 |
| D-023-09 | 关联引擎——模块间漂移共现矩阵 + 因果链分析 | 2026-05-05 | 系统性架构问题表现为多模块同时漂移 |
| D-023-10 | Evolution Engine 集成——高频漂移模块反馈到蓝图进化 | 2026-05-05 | 漂移不只是要修的问题——它是设计质量的信号 |
| D-023-11 | 并发安全——乐观并发控制（mtime 检查）+ AI 施工优先策略 | 2026-05-05 | 100% AI 施工 + 运行时自动修复，并发写同一文件是确定性事件；不引入文件锁避免死锁 |
| D-023-12 | 漂移预算——SRE 式错误预算，按模块优先级分级，耗尽阻断新施工 | 2026-05-05 | 没有预算约束漂移无限积累；'先干后验'退化为'只干不验' |
| D-023-13 | 告警路由——分级通知渠道 + 智能去重 + 聚合 + 静默策略 | 2026-05-05 | 1人维护下告警疲劳是最大 operational risk |
| D-023-14 | 修复 ROI 优先级——按 impact × frequency / effort 排序 | 2026-05-05 | 修复资源有限，盲目按时间/严重度排序低效 |
| D-023-15 | Git Bisect 溯源——自动定位引入漂移的 commit | 2026-05-05 | AI 施工场景下根因溯源比修复本身更重要——知道谁引入的才能避免复发 |
| D-023-16 | AI 上下文注入——施工前预检，三种注入级别 | 2026-05-05 | 预防性措施比事后修复便宜 10 倍；AI 不记忆跨 session 状态 |
| D-023-17 | 崩溃恢复——per detector checkpoint + SQLite 事务安全 + 优雅关闭 | 2026-05-05 | DEEP scan 崩溃后重跑不可接受；1人维护下崩溃不应导致数据丢失 |
| D-023-18 | 漂移风暴——> 50 漂移进入批量模式，暂停自动修复，按维度聚合 | 2026-05-05 | 氛围编程社区常做大规模重构；500 模块同时漂移是正常事件而非灾难 |
| D-023-19 | 热修复旁路——[HOTFIX] commit 自动标记、不消耗预算、72h 后必须正规化 | 2026-05-05 | 救火时 drift detector 不能成为阻碍；但热修复必须有时效性约束 |
| D-023-20 | 环境感知——context tags + 差异分类（ENV_DIFF vs DRIFT）+ 渐进部署感知 | 2026-05-05 | 多环境/Python venv 的合法差异不应被错误标记为漂移 |
| D-023-21 | 自动学习假阳性——同一 pattern 误报 3 次后自动抑制 + shadow 观测 + 定期审查 | 2026-05-05 | 1人维护下反复手动标记假阳性不可持续 |
| D-023-22 | 级联故障检测——30min 内 3 次修复→新漂移循环 → 锁定自动修复 → Owner 介入 | 2026-05-05 | AI 修复可能治标不治本；不加控制的自动修复链导致系统持续恶化 |
| D-023-23 | 资源上限——512MB 内存 / 2GB 磁盘 / 四级优雅降级 + 规模验证路线 | 2026-05-05 | 单机场景资源有限；drift detector 不能无限膨胀 |
| D-023-24 | 多实例竞态——scan mutex 文件锁 + 碰撞策略 + 扫描合并 | 2026-05-05 | Post-commit + 定时 + 手动三种触发可并发；两 scan 同时写 drift_events = 数据污染 |
| D-023-25 | 孤儿资源——磁盘有、注册表无、无引用三方比对 + 分级分类 + 手动清理 | 2026-05-05 | AI 施工产临时文件；孤儿积累污染目录 + 拖慢扫描 + 膨胀基线 |
| D-023-26 | 符号链接/子模块——断裂检测 + 目标变更 + 循环引用 + submodule dirty/out-of-sync | 2026-05-05 | 共享 scripts/ 可能用 symlink；外部依赖可能用 submodule；都是传统检测盲区 |
| D-023-27 | 文件底层属性——编码(BOM) + 换行符(CRLF vs LF) + 可执行位 + .gitattributes | 2026-05-05 | Windows/Linux 跨 session AI 施工→换行符混用是经典痛点；git diff 对此不可见 |
| D-023-28 | 测试夹具漂移——fixture schema vs model + mock target 存在性 + expected output 时效 | 2026-05-05 | 测试通过不代表系统正确；AI 常改逻辑忘改测试——测试成了"漂移孵化器" |
| D-023-29 | 配置多源一致性——.env × YAML × 硬编码三角对账 → YAML SSoT | 2026-05-05 | AI 易硬编码配置值；三源不一致→幽灵bug（"偶尔对偶尔错"） |
| D-023-30 | Python 版本兼容性——语法/标准库/类型注解 vs pyproject.toml requires-python | 2026-05-05 | AI 用最新语法但不知道项目目标版本；100% AI 施工高频问题 |
| D-023-31 | 向后兼容策略——API 签名变更检测 + 下游影响分析 + INTENTIONAL_BREAK 标记 | 2026-05-05 | AI 不守 SemVer，直接删"看起来没用"的参数→下游模块崩——大型AI项目典型坍塌模式 |
| D-023-32 | .gitignore 完整性——未忽略的生成文件 + 误忽略的关键配置 + 新文件类型覆盖 | 2026-05-05 | AI 生成新文件类型但不加 .gitignore；通配符误匹配 = 致命 |
| D-023-33 | 冷启动——bootstrap scan → trust → baseline + shallow clone 感知 | 2026-05-05 | 1500 模块上线第一天不能要求人工创建基线；首次扫描结果 = 遗产债务而非漂移 |
| D-023-34 | Owner 缺席模式——LENIENT(宽松) / SURVIVAL(维持) 双模式 + 回归交接报告 | 2026-05-05 | 1人维护的核心挑战——所有 SRE 方案假设多人值班，你不适用 |
| D-023-35 | 告警可信度评分——per detector credibility = fp_rate × precision × recency → alert 调制 | 2026-05-05 | 1人维护下最大风险不是漏报而是"狼来了"→Owner 忽略所有告警 |
| D-023-36 | 基线投毒防护——交叉验证 + 多基线投票 + 链式 hash + integrity_manifest | 2026-05-05 | 基线是真理来源——基线被污染 = 所有漂移检测失效；Git 是不可篡改的终极真理 |
| D-023-37 | 防篡改审计——append-only events + Git AUDIT 日志 + drift_events 异常检测 | 2026-05-05 | 自漂移检测只覆盖代码但数据(drift_events.db)也是检测器的一部分——数据被攻破 = 失明 |
| D-023-38 | 命名约定与魔数漂移——动词同义词 + 命名风格不一致 + 重复字符串字面量 + 重复常量 | 2026-05-05 | AI 跨 session 各有风格偏好；5 个 session 后模块变成命名大杂烩 |

---

## 变更记录

| 日期 | 版本 | 变更内容 |
|------|------|---------|
| 2026-05-05 | 0.7.0 | **第五轮独特性盲点**：① 新增 6 项决策（D-023-33~D-023-38，总计 38 项）② 新增冷启动策略（2.19）③ 新增 Owner 缺席模式（2.20）④ 新增告警可信度评分（2.21）⑤ 新增基线投毒防护（6.25）⑥ 新增防篡改审计——append-only + Git AUDIT 日志（6.26）⑦ 新增命名约定与魔数漂移（6.27）⑧ 文件组成 34→40 文件 ⑨ 施工 Phase——scaffold 11项 / experimental 16项 / beta 20项 / production 15项 |
| 2026-05-05 | 0.6.0 | **第四轮边缘盲点**：① 新增 9 项决策（D-023-24~D-023-32，总计 32 项）② 新增多实例竞态控制（2.15）③ 新增孤儿资源检测（2.16）④ 新增符号链接/子模块完整性（2.17）⑤ 新增文件底层属性——编码/换行符/权限（2.18）⑥ 新增测试夹具漂移（6.20）⑦ 新增配置三源一致性（6.21）⑧ 新增 Python 版本兼容性（6.22）⑨ 新增向后兼容策略漂移（6.23）⑩ 新增 .gitignore 完整性审计（6.24）⑪ 文件组成 25→34 文件 ⑫ 施工 Phase——experimental 14项 / beta 18项 / production 12项 |
| 2026-05-05 | 0.5.0 | **第三轮盲点扩展**：① 新增 7 项决策（D-023-17~D-023-23）② 新增崩溃恢复与检查点（2.10）③ 新增漂移风暴与批量处理（2.11）④ 新增热修复旁路（2.12）⑤ 新增环境感知与渐进部署（2.13）⑥ 新增自动学习假阳性（2.14）⑦ 新增级联故障检测（6.15）⑧ 新增资源上限与优雅降级（6.16）⑨ 新增漂移取证（6.17）⑩ 新增跨语言漂移框架（6.18）⑪ 新增供应商锁定漂移（6.19）⑫ 文件组成 20→25 文件 ⑬ 施工 Phase 再次细化——scaffold 9 项 / experimental 10 项 / beta 14 项 / production 11 项 |
| 2026-05-05 | 0.4.0 | **第二轮盲点扩展**：① 新增 6 项决策（D-023-11~D-023-16）② 新增并发竞争控制（2.8）③ 新增漂移预算机制（2.9）④ 新增告警路由与疲劳管理（5.4）⑤ 新增修复 ROI 优先级引擎（5.5）⑥ 新增 Git Bisect 溯源集成（5.6）⑦ 新增 AI 上下文注入（6.8）⑧ 新增漂移演练手册自动生成（6.9）⑨ 新增知识图谱实体化（6.10）⑩ 新增检测器金丝雀部署（6.11）⑪ 新增漂移训练数据闭环（6.12）⑫ 新增混沌漂移注入（6.13）⑬ 新增跨 Session 修复交接（6.14）⑭ 文件组成从 12 扩展为 20 文件 ⑮ 施工 Phase 细化——每阶段任务翻倍 |
| 2026-05-05 | 0.3.0 | **重大扩展**：① 新增 8 项决策（D-023-03~D-023-10）② 新增基线快照管理器、漂移状态机、增量扫描、自漂移检测 ③ 新增 AI 施工场景专用检测器（6 类）④ 新增时序存储/趋势分析/关联引擎/覆盖率仪表板 ⑤ 新增深度集成（Evolution Engine / 语义漂移 / DB Schema / 依赖版本 / 安全策略 / 文档共演化 / 测试覆盖）⑥ 漂移维度完整清单（31 维）⑦ 文件组成从 3 文件扩展为 12 文件 ⑧ 施工 Phase 从 3 级扩展为 4 级 |
| 2026-05-05 | 0.2.0 | 两项决策写入：D-023-01 整合现有脚本 + D-023-02 自动对账 |
| 2026-05-05 | 0.1.0 | 初始创建——漂移检测维度 + 对账循环 + 触发策略 |
| 2026-05-07 | 1.0.0 | **v1.0 AI 对话 #04/13 全量施工完成**：① 4 Phase（scaffold/experimental/beta/production）全部落盘 ② 65 张 TASK-INF-0001~0065 全部完成 ③ 47 文件完整产出（45 .py + 2 .yaml）④ G-CT-005 跨模块契约集成（state_machine.trigger_rollback + cascade_detector._trigger_cascade_rollback → MOD-INF-021 Rollback）⑤ G-CT-006 depends_on 依赖验证通过 ⑥ construction_progress: phase_production_complete
| 2026-05-08 | 1.0.1 | **系统集成打通（session-20260508-002）**：① 修复 BUG-1：`_write_drift_events()` 从 NO-OP 变为完整 SQLite 持久化（WAL + 原子事务 + 自动建表建索引）② 修复 BUG-2：`_detector_registry.yaml` 中 13 个 new 检测器的 `status` 从 `待实现` 更新为 `active`（与代码实际状态一致）③ 修复 BUG-3：3 个 AI 检测器空壳实现（`detect_ai_dead_code`/`detect_ai_duplicate_functionality`/`detect_ai_knowledge_pollution`——全部在临时目录上自测通过）④ 集成 BUG-4：冷启动序列新增 STEP 4.9（Drift Detector bootstrap + 预算检查——每个新 AI session 入项目自动激活）⑤ 集成 BUG-5：MCP governance_server 新增 3 个工具端点（`governance.drift_scan`/`governance.drift_report`/`governance.drift_budget`）⑥ construction_progress: completed → operational（系统可运行，下一步是红白对抗）
| 2026-05-08 | 1.0.1b | **红白对抗（session-20260508-002）**：① 混沌注入 4 类漂移（PATH_RENAME/YAML_FIELD_FLIP/FAKE_TODO_BOMB/IMPORT_HALLUCINATION）→ 检测率 100%（4/4），FN 率 0% ② 发现根源缺陷：`detect_ai_hallucination_import` 仅检查 `zephyr.drift_detector.*` 命名空间→盲区→修复为 `importlib.util.find_spec()` 全量解析 ③ 回归验证：4/4 再次 100%→根源修复有效 ④ 8/8 SelfTestVerifier 全 PASS ⑤ 对抗用例归档到 `tests/infrastructure/test_drift_red_blue_adversarial.py` ⑥ construction_progress: operational → battle_tested |


---

## 施工落盘确认（2026-05-08 session-20260508-002 审计 + 系统集成打通）

| 维度 | 修前状态 | 当前状态 |
|------|---------|---------|
| construction_progress | `completed`（不可运行） | `operational`（可运行） |
| _write_drift_events | `pass` (NO-OP) | SQLite WAL 持久化 ✅ |
| 注册表 status 一致性 | 13/39 = `待实现` | 39/39 = `active` ✅ |
| AI 检测器空壳 | 3 stubs (`return []`) | 3 实现（dead_code/duplicate/knowledge_pollution）✅ |
| Session 启动钩子 | 无 | STEP 4.9 cold-start 自动激活 ✅ |
| MCP Tool 端点 | 无 | governance.drift_scan / drift_report / drift_budget ✅ |
| 源码路径 | `src/zephyr/drift_detector/` | 不变 |
| 源码文件数 | 45 个 .py/.yaml | 不变（代码逻辑修复） |
| 自测 | 3/3 GCT-005 PASS | 3/3 GCT-005 PASS + 3/3 AI 检测器自测 PASS + self_check 全 GREEN |
| 红白对抗 | 未执行 | **✅ 完成** — 4/4 注入 100% 检出，0% FN，8/8 自检通过 |
| 对抗发现 | — | `detect_ai_hallucination_import` 盲区：仅检查 `zephyr.drift_detector.*` → 改为 `importlib.util.find_spec()` 全量杀 |
| 对抗产物 | — | [test_drift_red_blue_adversarial.py](file:///d:/ZephyrAlpha/tests/infrastructure/test_drift_red_blue_adversarial.py) |
| 版本 | — | v1.0.0 → v1.0.1 |
| construction_progress | `completed` | `operational → battle_tested` |
| E2E 全链路 | 未执行 | **✅ 完成** — 6/6 tests PASS，Gate Engine #19 drift_budget check_type 注册 |
| E2E 产物 | — | [test_drift_e2e_pipeline.py](file:///d:/ZephyrAlpha/tests/infrastructure/test_drift_e2e_pipeline.py) |
| 下一步 | — | 生产运行观测（真实 AI session 中自动触发 STEP 4.9 + MCP governance.drift_scan） |
