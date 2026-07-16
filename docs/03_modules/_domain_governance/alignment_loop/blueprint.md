---
module_id: MOD-GOV-ALIGNMENT-LOOP
title: "蓝图-代码对齐长效闭环引擎蓝图 — drift自动检测→自动修复→自动验证闭环"
doc_type: blueprint
status: Active
version: "1.0.0"
layer: L1_foundation
layer_name: cross_layer
functional_domain: governance
owner: ZephyrAlpha-Owner
classification: internal
language: zh
created_by: AI-GLM-5.2
valid_from: "2026-07-14"
submodule_path: src/zephyr/gov_drift/; src/zephyr/governance/audit/
date: "2026-07-14"
ttl: permanent
construction_progress: not_started
actual_disk_path: "src/zephyr/gov_drift/; src/zephyr/governance/audit/reconciliation_registry.py"
belongs_to: "MOD-MASTER_BLUEPRINT"
parent_module: ""
codification_level: L1
last_updated: "2026-07-14"
generation: 1
rule_form: structural
scope: global
stability: evolving
verifiability: design_review
references:
  - path: "D:\\ZephyrAlpha\\docs\\03_modules\\_domain_governance\\drift_detector\\blueprint.md"
    section: "§2.5 自动对账策略"
    why: "drift 检测引擎——S1 全量扫描的基础设施"
  - path: "D:\\ZephyrAlpha\\docs\\03_modules\\_cross_layer\\auto_fix_engine\\blueprint.md"
    section: "§4 自动修复 pipeline"
    why: "自动修复引擎——S2 分级自治的基础设施"
  - path: "D:\\ZephyrAlpha\\docs\\03_modules\\_domain_governance\\panorama_alignment_engine\\blueprint.md"
    section: "§2 同步引擎"
    why: "四图对齐引擎——S3 增量同步的基础设施"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\governance\\audit\\reconciliation_registry.py"
    section: "post-commit 对账注册表"
    why: "reconciler 注册表——S1/S2 的注册入口"
depends_on:
  - target: MOD-INF-023
    at: "§2.5"
    why: "drift 检测引擎——S1 全量扫描复用其39检测器"
  - target: MOD-INF-031
    at: "§4"
    why: "auto_fix_engine——S2 分级自治修复复用其 pre_fix_snapshot+验证闭环"
  - target: MOD-GOV-SYNC-PANORAMA
    at: "§2"
    why: "四图对齐引擎——S3 增量同步扩展其同步能力"
  - target: MOD-INF-005
    at: "§reconciler注册"
    why: "governance_automation——reconciler 注册与调度"
  - target: MOD-INF-016
    at: "§EventBus"
    why: "shared_core——事件总线，merge.completed 事件分发"
  - target: MOD-INF-024
    at: "§GCT-024"
    why: "budget_enforcer——drift 扫描的预算控制"
tags: [alignment-loop, drift-scan, auto-fix, depgraph-sync, module-id-recommend, dashboard, long-term-mechanism, phase5]
priority: P2
runtime_plane: warm
responsibility_domain: D_GOV_DRIFT
build_status: planned
design_maturity: design
---

# 蓝图-代码对齐长效闭环引擎蓝图 — drift自动检测→自动修复→自动验证闭环

## 概述

本蓝图定义 ZephyrAlpha 项目的**蓝图-代码对齐长效闭环机制**——把"人工发现 drift → 人工修复 → 手动验证"升级为"自动检测 → 自动修复 → 自动验证"的无人值守闭环。

### 问题背景

Phase 0-4 蓝图格式统一化任务将 drift 从 683 降至 0，但这一成果依赖**人工全量修复**。项目已有大量 post-commit 自动化（depgraph 同步、蓝图重生、20+ reconciler），但存在 6 个 gap 导致 drift 仍会积累：

1. drift 全量检测不定期自动运行（仅 GCT-024 `--warn-only`，severity=info）
2. drift 修复需人工审批（AutoFixer `human_gated`，prototype 成熟度）
3. depgraph 同步效率低（裁定#209 阶段1全量重跑，无增量）
4. 新建文件 module_id 不自动分配（门禁阻断但不推荐/不修复）
5. drift 趋势无持续监控（dashboard 存在但不定期更新）
6. 两套检测体系未整合（drift_engine 39检测器 vs check_blueprint_code_alignment）

### 设计目标

构建一个**事件驱动的闭环编排层**，编排现有的检测（drift_detector）、修复（auto_fix_engine）、同步（panorama_alignment_engine）能力，实现：

- **自动检测**：merge 事件触发全量 drift 扫描，结果入库
- **自动修复**：分级自治（LOW 全自动 / HIGH 可匹配则自动 / 不可匹配则人工）
- **自动验证**：修复后重跑检测确认 drift 减少
- **持续监控**：drift 趋势 dashboard 自动更新

### 核心铁律

| 铁律 | 本蓝图遵守方式 |
|------|-------------|
| reconciler 必须事件触发 | S1 订阅 `merge.completed` 事件，非 cron |
| 永久系统必须全自动 | S1/S2 全自动运行，无需手工干预 |
| 自动修复必须验证闭环 | S2 复用 AutoFixer 的 pre_fix_snapshot + 验证机制 |
| SSoT 真源分类 | drift 结果存 governance DB（架构数据→DB 真源） |

---

## §0 代码对齐验证

### §0.1 代码文件清单

<!-- AUTOGEN: source=depgraph.nodes, generator=extract_depgraph.py, reconciler=blueprint_frontmatter_reconciler.py -->
> **⚠️ 自动化提示**：文件清单真源在 PostgreSQL depgraph.nodes 表，本节手写内容可能过时。
> 查询最新文件清单：`python scripts/governance/extract_depgraph.py --modules MOD-GOV-ALIGNMENT-LOOP`
> 以下手写内容保留职责描述（depgraph 无此信息），文件列表以 depgraph 为准。

> **完整文件清单 SSoT**：`python scripts/governance/extract_depgraph.py --modules GOV-ALIGNMENT-LOOP`

| # | 文件名 | 对应蓝图章节 | 职责 | 存在性 |
|---|--------|------------|------|:---:|
| 1 | reconciliation_registry.py（扩展） | §4.S1 | 新增 `make_drift_scan_reconciler`，merge 事件触发全量 drift 扫描 | 已存在（扩展） |
| 2 | reconciler.py（扩展） | §4.S2 | AutoFixer 从 human_gated 升级为分级自治 | 已存在（扩展） |
| 3 | generate_project_depgraph.py（扩展） | §4.S3 | 文件级 hash fingerprint 增量同步 | 已存在（扩展） |
| 4 | validate_module_id_naming.py（扩展） | §4.S4 | 新建文件 module_id 自动推荐 | 已存在（扩展） |
| 5 | dashboard.py（扩展） | §4.S5 | drift 趋势持续监控 | 已存在（扩展） |

### §0.2 对齐验证矩阵

| 验证项 | 验证方法 | 结果 |
|--------|---------|:---:|
| construction_progress = not_started → §0.1 全部待建/扩展 | 逐文件核对 | ☐ |
| 5 个子任务依赖的现有模块均已 production | depgraph 查询 | ☐ |
| 闭环验证：S1 检测 → S2 修复 → 重跑 S1 确认 drift 减少 | 端到端测试 | ☐ |

### §0.3 版本-代码映射

| 蓝图版本 | 代码覆盖范围 | 缺失组件 | 缺失原因 |
|---------|------------|---------|---------|
| v1.0.0 (本版) | 无新代码（设计态） | S1-S5 全部 | not_started（编排层设计，待施工） |

---

## §1 设计背景与目标

### §1.1 现状分析

项目已有大量 post-commit 自动化机制：

| 已自动化 | 机制 | 触发方式 | 文件 |
|---------|------|---------|------|
| depgraph 同步 | `make_depgraph_ops_reconciler`（裁定#209阶段1） | commit .py 后自动 | reconciliation_registry.py:516 |
| 蓝图文档重生 | `make_regenerate_reconciler` | commit PG写入脚本后自动 | reconciliation_registry.py:1938 |
| module_id 一致性校验 | `make_module_id_consistency_reconciler` | post-commit warn | reconciliation_registry.py:2842 |
| 20+ reconciler 对账 | `ReconciliationRegistry.reconcile_for` | post-commit 按 priority | reconciliation_registry.py |
| commit gate 阻断 | BLUEPRINT-FORMAT/ARCH-REFERENCE/TEST-SOURCE-CONSISTENCY | pre-commit 硬阻断 | commit_gates/ |
| drift 检测（39检测器） | `drift_engine.py` | 手动/CLI 触发 | gov_drift/drift_engine.py |
| 蓝图-代码对齐检测 | `check_blueprint_code_alignment.py` | GCT-024 `--warn-only` | d5_architecture/checkers/ |
| 自动修复 | `AutoFixer`（human_gated） | 手动触发 | gov_drift/reconciler.py |

### §1.2 Gap 识别

| # | Gap | 现状 | 影响 | 本蓝图解决 |
|---|-----|------|------|----------|
| G1 | drift 全量检测不定期自动跑 | 仅 GCT-024 `--warn-only`，severity=info | drift 积累到 683 才人工发现 | S1: merge 事件触发全量扫描 |
| G2 | drift 修复需人工审批 | AutoFixer `human_gated`，prototype | 检测到 drift 但不自动修 | S2: 分级自治修复 |
| G3 | depgraph 同步效率低 | 阶段1全量重跑，每次 commit .py | 浪费 IO/CPU | S3: hash fingerprint 增量 |
| G4 | 新建文件 module_id 不自动分配 | 门禁阻断但不推荐 | AI 需手动查蓝图 | S4: 自动推荐+注入 |
| G5 | drift 趋势无持续监控 | dashboard 不定期更新 | 看不到漂移趋势 | S5: 扫描驱动更新 |
| G6 | 两套检测体系未整合 | drift_engine vs check_alignment | 职责重叠 | S1: 统一编排入口 |

### §1.3 目标范围

| # | 类型 | 内容 | 标准/原因 |
|---|:----:|------|----------|
| 1 | ✅ 包含 | merge 事件触发全量 drift 扫描 | 覆盖历史遗留+本次变更 drift |
| 2 | ✅ 包含 | 分级自治 drift 自动修复 | LOW 全自动 / HIGH 可匹配自动 / 不可匹配人工 |
| 3 | ✅ 包含 | depgraph 增量同步 | 裁定#209 阶段3，hash fingerprint |
| 4 | ✅ 包含 | 新建文件 module_id 自动推荐 | 从 blueprint_registry 路径匹配 |
| 5 | ✅ 包含 | drift 持续监控 dashboard | 趋势+成功率+分布 |
| 6 | ✅ 包含 | 闭环验证 | 修复后重跑检测确认 drift 减少 |
| 7 | ❌ 排除 | 新建 drift 检测器 | drift_detector (MOD-INF-023) 负责 |
| 8 | ❌ 排除 | 新建修复策略 | auto_fix_engine (MOD-INF-031) 负责 |
| 9 | ❌ 排除 | 新建同步引擎 | panorama_alignment_engine 负责 |
| 10 | ❌ 排除 | commit gate 框架 | governance_automation (MOD-INF-005) 负责 |

### §1.4 约束

| 约束 | 影响 |
|------|------|
| reconciler 必须事件触发（硬约束） | S1 订阅 merge.completed 事件，禁止 cron |
| 永久系统必须全自动（硬约束） | S1/S2 全自动运行，禁止需手工干预的设计 |
| 自动修复必须验证闭环（铁律） | S2 复用 AutoFixer pre_fix_snapshot + 验证 |
| session_worktree 流程 | S2 自动提交走 session_worktree_commit |
| SSoT 真源分类（TRAE-062） | drift 结果→DB（架构数据）；规则→YAML（规则数据） |

### §1.5 利益相关者映射

| 角色 | 关注点 | 参与阶段 | 约束 |
|------|--------|---------|------|
| Owner | 架构决策 | 设计+审批 | 审批权限 |
| MOD-INF-023 drift_detector | 39检测器能力供给 | S1 施工 | 检测器接口复用 |
| MOD-INF-031 auto_fix_engine | AutoFixer 能力供给 | S2 施工 | pre_fix_snapshot+验证复用 |
| MOD-GOV-SYNC-PANORAMA | 同步引擎能力供给 | S3 施工 | 增量同步扩展 |
| MOD-INF-005 governance_automation | reconciler 注册调度 | S1/S2 施工 | 注册表接口复用 |
| GitCommitGateway | post-commit 触发点 | S1 集成 | merge 后事件发布 |

---

## §2 模块边界

### §2.1 职责边界

| # | 类型 | 职责 | 详情 | 负责方 |
|---|:----:|------|------|--------|
| 1 | ✅ 包含 | 闭环编排 | 编排检测→修复→验证的完整闭环 | 本模块 |
| 2 | ✅ 包含 | merge 事件订阅 | 订阅 session_worktree_merge 的 merge.completed 事件 | 本模块 |
| 3 | ✅ 包含 | drift 结果入库 | 扫描结果写入 governance DB drift 表 | 本模块 |
| 4 | ✅ 包含 | 分级自治决策 | LOW/HIGH/不可匹配 三级分流 | 本模块 |
| 5 | ✅ 包含 | 闭环验证 | 修复后重跑检测，确认 drift 减少 | 本模块 |
| 6 | ✅ 包含 | dashboard 更新 | 扫描结果驱动 dashboard 更新 | 本模块 |
| 7 | ❌ 排除 | drift 检测器实现 | 39检测器 | MOD-INF-023 |
| 8 | ❌ 排除 | 修复策略实现 | pre_fix_snapshot/验证 | MOD-INF-031 |
| 9 | ❌ 排除 | 同步引擎实现 | 四图同步 | MOD-GOV-SYNC-PANORAMA |
| 10 | ❌ 排除 | gate 框架实现 | commit gate 注册/调度 | MOD-INF-005 |

### §2.2 排除项

| # | 排除项 | 原因 | 归属模块 |
|---|--------|------|---------|
| 1 | 新建 drift 检测器 | 已有39检测器 | MOD-INF-023 |
| 2 | 新建修复算法 | 已有 AutoFixer | MOD-INF-031 |
| 3 | 新建同步引擎 | 已有四图同步 | MOD-GOV-SYNC-PANORAMA |
| 4 | commit gate 框架 | 已有 GitCommitGateway | MOD-INF-005 |

---

## §3 架构设计

### §3.1 闭环架构

```
session_worktree_merge()
    │
    ├─ 发布 merge.completed 事件
    │
    ▼
┌─────────────────────────────────┐
│  S1: make_drift_scan_reconciler │  ← 事件触发（非cron）
│  ────────────────────────────── │
│  1. 跑 check_blueprint_code_    │
│     alignment.py 全量检测        │
│  2. 跑 drift_engine 39检测器     │
│  3. 结果写入 governance DB       │
│  4. 更新 dashboard              │
└──────────────┬──────────────────┘
               │ drift 列表
               ▼
┌─────────────────────────────────┐
│  S2: 分级自治修复 pipeline       │
│  ────────────────────────────── │
│  ┌─ LOW (CODE_NOT_IN_DEPGRAPH) │
│  │  → 自动跑 depgraph 增量同步  │
│  │  → session_worktree_commit  │
│  │  → 验证                      │
│  │                              │
│  ├─ HIGH (ORPHAN_MODULE_ID)    │
│  │  → 从 blueprint_registry 匹配│
│  │  → 自动修复 [BLUEPRINT] 头部 │
│  │  → session_worktree_commit  │
│  │  → 验证                      │
│  │                              │
│  └─ 不可匹配                    │
│     → 生成 AuditFinding         │
│     → 人工审批                   │
└──────────────┬──────────────────┘
               │ 修复后
               ▼
┌─────────────────────────────────┐
│  闭环验证                       │
│  ────────────────────────────── │
│  重跑 S1 检测                   │
│  确认 drift 减少 or =0          │
│  记录修复成功率                  │
└──────────────┬──────────────────┘
               │
               ▼
┌─────────────────────────────────┐
│  S5: dashboard 更新             │
│  ────────────────────────────── │
│  drift 趋势（时间序列）          │
│  自动修复成功率                  │
│  各类 drift 分布                 │
└─────────────────────────────────┘
```

### §3.2 数据流

| 流向 | 生产者 | 消费者 | 数据类型 | 传输方式 |
|------|--------|--------|---------|---------|
| 事件 | session_worktree_merge | S1 reconciler | merge.completed 事件 | EventBus |
| 检测 | S1 | governance DB | drift 记录 | SQLite INSERT |
| 修复 | S2 | 代码文件/depgraph | [BLUEPRINT] 头部/depgraph 节点 | session_worktree_commit |
| 验证 | 闭环验证 | governance DB | 修复结果 | SQLite UPDATE |
| 展示 | S5 | dashboard | 趋势数据 | SQLite SELECT |

### §3.3 与现有模块对接

| 现有模块 | 对接点 | 复用能力 | 本蓝图扩展 |
|---------|--------|---------|----------|
| MOD-INF-023 drift_detector | drift_engine.run_scan() | 39检测器 | S1 编排其全量运行 |
| MOD-INF-031 auto_fix_engine | AutoFixer.pre_fix_snapshot/fix/verify | 快照+修复+验证 | S2 分级自治决策 |
| MOD-GOV-SYNC-PANORAMA | sync_panorama_module.py | 四图同步 | S3 增量 hash |
| MOD-INF-005 governance_automation | ReconciliationRegistry.register() | reconciler 注册 | S1 注册新 reconciler |
| MOD-INF-016 shared_core | EventBus.publish() | 事件分发 | S1 订阅 merge.completed |
| MOD-INF-024 budget_enforcer | BudgetEngine.pre_flight_check() | 预算控制 | S1/S2 扫描预算 |

---

## §4 子任务设计

### §4.S1 merge 事件触发的全量 drift 扫描（P0）

**目标**：merge 完成后自动全量扫描 drift，结果入库。

**实现**：

1. **事件源**：`session_worktree_merge()` 完成后发布 `merge.completed` 事件到 EventBus
2. **reconciler**：新建 `make_drift_scan_reconciler(gateway)` 注册到 ReconciliationRegistry
   - trigger: 匹配 merge 事件（非文件匹配）
   - reconcile: 跑 `check_blueprint_code_alignment.py` + `drift_engine` 全量检测
   - 结果写入 governance DB `drift_scan_results` 表
   - action: clean（无drift）/ warn（有drift，转S2）
3. **DB schema**：
   ```sql
   CREATE TABLE IF NOT EXISTS drift_scan_results (
       scan_id TEXT PRIMARY KEY,
       scan_time TEXT NOT NULL,
       trigger_event TEXT NOT NULL,  -- merge.completed
       total_drifts INTEGER NOT NULL,
       high_count INTEGER NOT NULL,
       low_count INTEGER NOT NULL,
       auto_fixable INTEGER NOT NULL,
       details_json TEXT
   );
   ```

**遵守硬约束**：事件触发（merge.completed），非 cron，非手动。

### §4.S2 分级自治 drift 自动修复 pipeline（P0）

**目标**：检测到 drift 后，按风险分级自动修复。

**分级策略**：

| drift 类型 | 风险 | 修复动作 | 自治级别 |
|-----------|------|---------|---------|
| CODE_NOT_IN_DEPGRAPH (LOW) | 低 | 自动跑 generate_project_depgraph.py 增量同步 → commit | 全自动 |
| ORPHAN_MODULE_ID (HIGH, 可匹配) | 中 | 从 blueprint_registry §4 文件清单匹配路径 → 修复 [BLUEPRINT] 头部 → commit | 全自动 |
| ORPHAN_MODULE_ID (HIGH, 不可匹配) | 高 | 生成 AuditFinding → 人工审批 | 半自动 |

**闭环验证**：
1. pre_fix_snapshot（复用 AutoFixer 已有机制）
2. 执行修复
3. 重跑 S1 检测
4. 确认 drift 减少 → 成功 / 未减少 → 回滚 + 升级为人工

**自动提交**：走 `session_worktree_commit`（遵守 worktree 君子协定）。

### §4.S3 depgraph 增量同步（P1）

**目标**：实现裁定#209 阶段3——文件级 hash fingerprint，替代全量重跑。

**实现**：
1. 新增 `file_hash_fingerprints` 表：
   ```sql
   CREATE TABLE IF NOT EXISTS file_hash_fingerprints (
       file_path TEXT PRIMARY KEY,
       content_hash TEXT NOT NULL,
       last_synced TEXT NOT NULL
   );
   ```
2. commit .py 时，计算变更文件的 hash，与 fingerprint 表比对
3. 只同步 hash 变化的文件到 depgraph
4. 更新 fingerprint 表

**收益**：从 O(全项目) 降到 O(变更文件)。

### §4.S4 新建文件 module_id 自动推荐（P1）

**目标**：BLUEPRINT-FORMAT gate 检测到新建 .py 无合规 module_id 时，自动推荐+注入。

**实现**：
1. gate 检测到新建 .py 文件无 [BLUEPRINT] 头部或 module_id 不合规
2. 从 `blueprint_registry.yaml` 的 §4 文件清单匹配文件路径
3. 匹配成功 → 自动注入合规 [BLUEPRINT] 头部
4. 匹配失败 → 阻断 + 提示 AI 查蓝图

**匹配算法**：文件路径 → 蓝图 §4 文件清单的路径模式匹配。

### §4.S5 drift 持续监控 dashboard（P2）

**目标**：展示 drift 趋势、自动修复成功率、各类 drift 分布。

**实现**：
1. 扩展 `gov_drift/dashboard.py`
2. 从 `drift_scan_results` 表读取时间序列数据
3. 展示：
   - drift 数量趋势（折线图）
   - 自动修复成功率（百分比）
   - 各类 drift 分布（饼图：HIGH/LOW）
   - 人工干预次数
4. 由 S1 扫描结果驱动更新

---

## §5 依赖关系与优先级

### §5.1 依赖图

```
S1 (全量扫描, P0) ──→ S2 (自动修复, P0) ──→ S5 (dashboard, P2)
                                           ↑
S4 (module_id推荐, P1) ────────────────────┘ (独立，防蔓延)
S3 (增量同步, P1) ────────────────────────── (独立，效率优化)
```

### §5.2 优先级矩阵

| 子任务 | 优先级 | 依赖 | 预期收益 |
|--------|:------:|------|---------|
| S1 全量扫描 | P0 | EventBus, drift_engine | drift 不再积累 |
| S2 自动修复 | P0 | S1, AutoFixer | 修复不再依赖人工 |
| S4 module_id推荐 | P1 | BLUEPRINT-FORMAT gate | 新建文件不蔓延 |
| S3 增量同步 | P1 | generate_project_depgraph.py | 效率提升 |
| S5 dashboard | P2 | S1 | 可视化监控 |

### §5.3 实施顺序

1. **第一批（P0）**：S1 → S2（检测+修复闭环）
2. **第二批（P1）**：S4 + S3（防蔓延+效率，可并行）
3. **第三批（P2）**：S5（可视化）

---

## §6 合规性矩阵

| 硬约束/铁律 | 本蓝图合规方式 | 验证方法 |
|------------|-------------|---------|
| reconciler 必须事件触发 | S1 订阅 merge.completed 事件 | 代码审查：无 cron/sleep |
| 永久系统必须全自动 | S1/S2 全自动，无手工干预 | 端到端测试 |
| 自动修复必须验证闭环 | S2 复用 pre_fix_snapshot+验证 | 闭环测试 |
| SSoT 真源分类 (TRAE-062) | drift 结果→DB；规则→YAML | 真源审查 |
| session_worktree 流程 | S2 自动提交走 session_worktree_commit | 代码审查 |
| 依赖关系先行 (L1) | 本蓝图登记 depgraph 设计态后施工 | depgraph 查询 |
| 设计态基于最新运营态 (L2) | 施工前确认运营态就绪 | generate_project_depgraph.py |
| 容量治理二元规则 | 本模块 production_nodes ≤150 | depgraph 统计 |

---

## §7 变更记录

### v1.0.0 (2026-07-14) 初版
- **蓝图创建**：Phase 5 长效机制规划
- **5个子任务**：S1 merge事件全量drift扫描(P0)、S2 分级自治drift自动修复(P0)、S3 depgraph增量同步(P1)、S4 新建文件module_id自动推荐(P1)、S5 drift持续监控dashboard(P2)
- **设计态**：build_status=planned, design_maturity=design
- **待施工**：依赖关系先行铁律(L1)要求施工前先登记depgraph设计态
