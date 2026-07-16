---
ttl: permanent
archived_at: 2026-07-16
archived_from: docs/_working/2026-07-15-panorama_orphan_governance_spec.md
archive_reason: ARCH-057 四图孤儿治理已完成（问题总数=0），spec 已落地
---

# 四图孤儿治理与同步闭环设计文档 (ARCH-057)

> **Status**: Draft
> **Date**: 2026-07-15
> **Spec**: ARCH-057 四图孤儿治理

## 1. 问题陈述

2026-07-10 ARCH-056 修复后四图对齐为 0 问题。2026-07-15 重跑检测发现 4 个新问题（孤儿=3, 状态漂移=1），均由 5 天内新增代码/文档未在四图同步登记导致。

### 1.1 孤儿模块详情

| module_id | 仅存图 | 实际内容 | 根因 |
|---|---|---|---|
| MOD-004 | blueprint | FLE 接口规范文档（有价值） | ID 三重分裂：MOD-004 / AI-ENG-FLE-001 / MOD-FEEDBACK_LOOP（canonical） |
| MOD-BIZ-002 | decision | 纯占位空记录（无价值） | sync_panorama_module.py 只 UPSERT 不 DELETE，depgraph 删模块后 decision_layers 残留 |
| MOD-GOV_SCRIPTS-001 | depgraph | 复杂度扫描脚本（有价值） | 命名不规范，应复用已有 MOD-GOV-SCRIPTS |

### 1.2 状态漂移

MOD-004 blueprint 缺 `design_maturity` 字段（同目录兄弟文件均有此字段）。

## 2. 根因分析（第一性原理）

### 2.1 核心矛盾

四图同步是**单向设计**（depgraph → 其他 3 图），但实际工作流是**多入口**的。在 100% AI 开发模式下，新模块从任意一图进入时，其他图不会被通知。

### 2.2 五个系统性缺陷

| # | 缺陷 | 后果 | 本期处理 |
|---|---|---|---|
| 1 | sync 只 UPSERT 不 DELETE | depgraph 删模块后 decision_layers 占位层残留 | ✅ B1 |
| 2 | dataflow/decision 写入器无 sync 钩子 | 从这两图新增节点不同步到其他图 | ❌ 后续专项 |
| 3 | dataflowgraph 写入器不写 module_id | 新增 Job 对齐引擎看不见 | ❌ 后续专项 |
| 4 | gate 触发条件窄（不含 docs/03_modules/*.md） | 新建蓝图文件不触发对齐检测 | ✅ B2 |
| 5 | AGENTS.md §9 onboarding 不覆盖四图 | AI 新增模块时不知要先登记 depgraph | ✅ B3 |

## 3. 裁定结果

### A. 数据修复

| 裁定 | 模块 | 处置 | 理由 |
|---|---|---|---|
| A1 | MOD-004 | frontmatter `module_id: MOD-004` → `MOD-FEEDBACK_LOOP` + 补 `design_maturity`/`build_status`/`responsibility_domain` | canonical ID 已在 100+ 测试文件使用；接口规范是派生文档不应占独立 module_id；MOD-FEEDBACK_LOOP 已在 depgraph 四图登记 |
| A2 | MOD-BIZ-002 | 由 sync_panorama_module.py `--prune-orphans` 自动删除 | 纯占位空记录，无 blueprint/源码/depgraph 节点 |
| A3 | MOD-GOV_SCRIPTS-001 | 文件头 `[BLUEPRINT] MOD-GOV_SCRIPTS-001` → `MOD-GOV-SCRIPTS` + depgraph 节点合并 | 同目录 36 个脚本已有 MOD-GOV-SCRIPTS 作为合法归属模块 |

### B. 系统治本

| 裁定 | 内容 |
|---|---|
| B1 | sync_panorama_module.py 增加 `--prune-orphans` 选项：删除 decision_layers 中 `track='placeholder'` 且 layer_id 不在 depgraph.nodes.blueprint_id 中的记录 |
| B2 | panorama_alignment_gate `_TRIGGER_PATTERNS` 增加 `docs/03_modules/` 路径模式 |
| B3 | AGENTS.md §9 增加"四图注册步骤"：apply_depgraph → sync_panorama → align_panoramas 验证 |

### 不在本期处理

- dataflow/decision 写入器增加 sync 钩子（范围大，需专项工程）
- dataflowgraph 写入器补 module_id 字段（涉及 CLI + INSERT + YAML schema 联动）
- sync 失败从 warn-only 改为阻断（需评估对现有工作流影响）

## 4. 验证标准

- align_panoramas.py 报告：问题总数 = 0
- sync_panorama_module.py --prune-orphans：0 个孤儿占位层
- 全部测试通过
