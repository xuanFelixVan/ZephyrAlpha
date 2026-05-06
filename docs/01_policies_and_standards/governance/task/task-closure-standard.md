---
module_id: GOV-TASK-005
title: "任务关闭标准"
doc_type: standard
status: active
version: "1.1.0"
layer: cross_layer
owner: ZephyrAlpha-Owner
classification: confidential
language: zh
created_by: human_plus_agent
date: "2026-05-01"
valid_from: "2026-05-01"
ttl: permanent
summary: "定义 ZephyrAlpha 任务从 IN_PROGRESS 到终态（VERIFIED/CANCELLED）的完整关闭流程：完成定义、清扫检查、验证门禁、残留物检测。本标准是任务关闭的唯一规则来源，合并并扩展 task-card-standard.md §8 和 task-completion-cleanup-gate.md 的内容。"
tags: [task, closure, cleanup, gate, verification, governance]
rule_form: declarative
scope: global
stability: stable
verifiability: manual
depends_on:
  - {target: PS-STD-001, at: "§7", why: "metadata-registry.md §7 定义的任务卡字段 schema 为 deliverables/acceptance/status 等字段的 SSoT"}
supersedes:
  - path: docs/01_policies_and_standards/governance/task/task-card-standard.md
    version: 2.0.0
    reason: "从 task-card-standard.md §8 提取完成门禁定义，扩展为完整关闭流程"
  - path: docs/01_policies_and_standards/governance/document/task-completion-cleanup-gate.md
    version: 1.0.0
    reason: "合并清扫三步法内容，原文件已于 2026-05-01 安全删除"
ai_autonomy: immutable_core
---

# 任务关闭标准

> **module_id**: GOV-TASK-005 | **version**: 1.1.0 | **status**: active
>
> 本标准定义任务从"执行中"到"关闭"的完整流程。
> `03_modules/l01_infrastructure/task-system/blueprint.md` §5.2-§5.3 定义状态机和门禁映射，
> `task-lifecycle-standard.md` 定义治理规则（取消权限、优先级裁决、升级治理），
> 本标准定义关闭流程中每个步骤的具体检查内容和操作方法。
>
> 对标：ITIL Incident Closure + Jira Resolution + ServiceNow Close + Azure DevOps Done Criteria。

## 1. 目的与范围

### 1.1 目的

确保每个任务在关闭前：

1. **交付物完整**——所有承诺的产出物都存在且合规
2. **环境干净**——无临时文件、残留文件、副产品
3. **验收通过**——所有验收指标达标
4. **审计可追溯**——关闭决策有据可查

> **负向责任**：本标准**不涉及**任务卡字段定义（→ [GOV-TASK-001](../../governance/task/task-card-standard.md)）、不涉及任务生命周期治理规则（→ [GOV-TASK-004](../../governance/task/task-lifecycle-standard.md)）、不涉及状态机实现和门禁检查逻辑（→ [MOD-INF-006](../../../03_modules/l01_infrastructure/task-system/blueprint.md) §5.2-§5.3）。

### 1.2 适用范围

- 所有从 IN_PROGRESS 转换到 COMPLETED 的任务
- 所有从 COMPLETED 转换到 VERIFIED 的任务
- 所有因取消而关闭的任务（IN_PROGRESS/FAILED/BLOCKED/WAITING/READY → CANCELLED）

### 1.3 SSoT 声明

| 内容 | 真源 | 非真源 |
|------|------|--------|
| IN_PROGRESS → COMPLETED 的准入条件 | 本文件 §2 | task-card-standard.md §8（以本文件为准） |
| COMPLETED → VERIFIED 的准入条件 | 本文件 §3 | task-card-standard.md §8（以本文件为准） |
| 清扫三步法 | 本文件 §4 | task-completion-cleanup-gate.md（已删除；以本文件为准） |
| 残留物分类与处置 | 本文件 §4.3 | task-completion-cleanup-gate.md（已删除；以本文件为准） |
| 取消关闭流程 | 本文件 §5 | — |

### 1.4 老树教训

Vibe Coding 流水线执行 120 个任务后，老树残留了大量骨架测试、临时脚本、重复文件。这些残留物未被任何门禁检测，直到手动排查才发现。根因是任务完成流程缺少"清扫"环节。

## 2. 完成定义（IN_PROGRESS → COMPLETED）

任务从 IN_PROGRESS 转换到 COMPLETED，必须满足以下**全部条件**：

### 2.1 交付物完整性

| 检查项 | 通过条件 | 不通过处置 |
|--------|---------|-----------|
| 交付物存在 | deliverables 中所有文件物理存在 | 继续执行或报告 FAILED |
| 交付物在声明路径 | 所有交付物在 deliverables 指定路径下 | 将文件移到正确路径，或更新 deliverables |
| 无未声明副产品 | 无 deliverables 之外的产出文件 | 声明并说明理由，或删除 |

### 2.2 验收达标

| 检查项 | 通过条件 | 不通过处置 |
|--------|---------|-----------|
| 验收指标全部满足 | acceptance 中所有指标达到目标值 | 继续执行或报告 FAILED |
| 验收可量化 | 每条验收标准有明确的通过/不通过判断 | 补充量化标准 |

### 2.3 编码合规

| 检查项 | 通过条件 | 不通过处置 |
|--------|---------|-----------|
| 文件编码 | UTF-8 无 BOM | 修复编码 |
| 换行符 | LF（Unix 风格） | 转换换行符 |

### 2.4 依赖完整

| 检查项 | 通过条件 | 不通过处置 |
|--------|---------|-----------|
| 无未完成依赖 | depends_on 中所有任务状态为 VERIFIED 或 COMPLETED | 报告 BLOCKED |

## 3. 验证定义（COMPLETED → VERIFIED）

任务从 COMPLETED 转换到 VERIFIED，必须满足以下**全部条件**：

### 3.1 清扫通过

- task_completion_gate.py `--scan` 退出码为 0（无残留）
- 或退出码为 1 且已执行 `--clean` 后重新扫描通过

### 3.2 编码合规

- 所有交付物 UTF-8 无 BOM + LF 换行
- 无 .backup/.tmp/temp_* 残留文件

### 3.3 验收确认

| 验证者 | 适用场景 |
|--------|---------|
| Owner | safety_level: H 的任务 |
| AI 自验证 | safety_level: L/M 的任务，但必须在 Session Log 中记录验证结果 |
| 指定验证者 | Owner 委派 |

### 3.4 验证不通过

验证不通过时，任务走返工路径：COMPLETED → IN_PROGRESS

- 返工原因必须记录在 Session Log 的 decisions_made 中
- 返工后需重新通过 G4 完成门禁

## 4. 清扫三步法

> 每个任务在声明 COMPLETED 之前，必须执行以下三步。
> 清扫在 G4 门禁之前执行，清扫不通过不得声明 COMPLETED。

### 4.1 Step 1：产出物核验

| 检查项 | 通过条件 | 不通过处置 |
|--------|---------|-----------|
| 所有产出文件在 deliverables 内 | 100% 在指定路径 | 将文件移到正确路径，或更新 deliverables |
| 无 deliverables 之外的副产品 | 零个未声明文件 | 声明并说明理由，或删除 |
| 产出文件编码正确 | UTF-8 无 BOM + LF | 修复编码后重新验证 |

### 4.2 Step 2：临时文件清除

以下模式的文件必须在同一 session 内删除：

| 模式 | 示例 | 处置 |
|------|------|------|
| `temp_*` | `temp_scan_result.json` | 删除 |
| `*.backup` | `schemas.py.backup` | 删除 |
| `*-v2.*` / `*-v3.*` / `*-round2.*` | `config-v2.yaml` | 删除（版本历史用 git） |
| `__pycache__/` | 任何 `__pycache__/` 目录 | 删除 |
| `*.pyc` | 编译缓存 | 删除 |
| `tmp_*` 脚本 | `tmp_replace_composer.py` | 删除 |
| `ttl: session` 的文件 | session 内临时工具 | 删除 |

### 4.3 Step 3：残留物检测

任务完成后，检查任务操作路径下是否有不属于本次任务的残留文件：

```bash
python src/zephyr/gates/task_completion_gate.py \
  --task-id {TASK_ID} \
  --scope-paths "{scope_path_1}" "{scope_path_2}"
```

检测逻辑：
1. 扫描 `--scope-paths` 下所有文件
2. 与 deliverables + files_in_scope 做差集
3. 差集文件按以下规则分类：

| 分类 | 判定条件 | 处置 |
|------|---------|------|
| ORPHAN_SHELL | 文件大小 < 100 bytes 且内容为空壳/占位 | 删除 |
| STALE_SKELETON | import 路径指向已不存在的模块 | 删除 |
| DUPLICATE | 与项目其他文件内容完全相同 | 删除老副本 |
| LEGACY_TEST | 测试文件引用已删除的源代码 | 删除 |
| VALID_FILE | 不属于以上任何分类 | 在报告中声明，由 Owner 判定 |

### 4.4 脚本未就绪时的后备方案

`task_completion_gate.py` 尚未实现时，AI 必须执行以下手动检查清单：

| 检查项 | 方法 | 通过条件 |
|--------|------|---------|
| 临时文件扫描 | 在 scope-paths 下搜索 `temp_*`、`*-v2.*`、`*-v3.*`、`*-round2.*`、`*.backup`、`__pycache__` | 零匹配 |
| 空壳文件检测 | 检查 scope-paths 下文件大小 < 100 bytes 的文件内容是否为空壳/占位 | 无空壳 |
| 文件一致性 | 对比 `deliverables` 列表与 scope-paths 下实际文件列表 | 无遗漏、无多余 |
| 编码检测 | 检查所有产出文件是否为 UTF-8 无 BOM + LF 换行 | 全部合规 |

手动检查结果必须记录在 Session Log 中：

```yaml
- topic: 任务 {task_id} 清扫检查（手动后备——task_completion_gate.py 尚未实现）
  decision: 通过 / 不通过（附具体不通过项）
  rationale: <检查摘要，列出执行的具体命令和结果>
```

## 5. 取消关闭流程

任务因取消而关闭（→ CANCELLED）时，不需要执行清扫三步法，但必须：

### 5.1 取消前检查

| 检查项 | 要求 |
|--------|------|
| 取消原因 | 必须在 Session Log 中记录取消原因 |
| 部分产出物 | 如有已完成的交付物，标记为"部分完成"，不删除 |
| 临时文件 | 取消后仍需执行 Step 2（临时文件清除） |

### 5.2 取消审批

> 取消权限规则以 [task-lifecycle-standard.md §2.1](../../governance/task/task-lifecycle-standard.md) 为唯一真源。摘要：P0/P1 需 Owner 审批，P2/P3/P4 AI 可自主取消但需在 Session Log 记录原因。

## 6. 自动化脚本

清扫门禁的自动化脚本位于：

```
src/zephyr/gates/task_completion_gate.py
```

### 6.1 脚本功能

| 命令 | 功能 | 完整调用示例 |
|------|------|-------------|
| `--scan` | 扫描指定路径，输出残留文件分类报告 | `python src/zephyr/gates/task_completion_gate.py --scan --task-id {TASK_ID} --scope-paths "{PATH1}" "{PATH2}"` |
| `--clean` | 自动删除 ORPHAN_SHELL / STALE_SKELETON / DUPLICATE / LEGACY_TEST 类别的文件 | `python src/zephyr/gates/task_completion_gate.py --clean --task-id {TASK_ID} --scope-paths "{PATH1}"` |
| `--verify` | 验证任务产出物全部在 deliverables 内 | `python src/zephyr/gates/task_completion_gate.py --verify --task-id {TASK_ID}` |

### 6.2 脚本退出码

| 退出码 | 含义 |
|--------|------|
| 0 | 扫描通过，无残留 |
| 1 | 存在可自动清理的残留（需 `--clean`） |
| 2 | 存在需人工判定的 VALID_FILE 残留 |
| 3 | 产出物不在 deliverables 内 |

## 7. 违规处理

| 违规级别 | 情形 | 处理 |
|---------|------|------|
| WARNING | 任务报告未提及清扫结果 | 下次 session 补扫 |
| ERROR | 发现 temp_*/backup 残留 | 立即删除，session log 记录 |
| CRITICAL | 产出物不在 deliverables 内且未声明 | 任务标记为需返工 |

## 8. 任务卡模板更新

所有新任务卡的 `acceptance` 字段必须包含以下条目：

```yaml
acceptance:
  - ...（原有验收条件）
  - 无 temp_*/backup/*-v2 残留文件
  - 所有产出文件在 deliverables 指定路径下
  - task_completion_gate.py 扫描通过（0 个 ORPHAN/STALE/DUPLICATE/LEGACY）
```

## 9. 与其他规则的关系

| 规则 | 与本标准的关系 |
|------|-------------|
| task-system/blueprint.md §5.2-§5.3 | 状态机实现和 G4/G5 门禁的触发时机与检查逻辑 |
| task-lifecycle-standard.md | 治理规则：取消权限 + 优先级裁决 + 升级治理 |
| task-card-standard.md | 该文件定义 deliverables/acceptance 字段格式，本标准定义如何检查这些字段 |
| file-operation-safety-policy.md | 安全门禁管"删除前"，本标准管"完成后" |
| document-lifecycle-standard.md | 生命周期管"文档 TTL"，本标准管"任务副产品" |
| encoding-safety-standard.md | 编码管"写入格式"，本标准管"残留检测" |
| handoff-protocol.md | 交接协议管跨 session 上下文，本标准管单次 session 的关闭质量 |

## 10. 历史教训记录

| 日期 | 事件 | 根因 | 本标准对应条款 |
|------|------|------|-------------|
| 2026-04-24 | 老树 tests/unit/ 残留 8 个骨架测试 + 1 个漏迁文件 | T-2-34 搬迁任务只搬 files_in_scope 内文件，未检测 scope 外残留 | §4.3 残留物检测 |
| 2026-04-24 | 老树 scripts/infra/ 搬迁后目录空壳残留 | 搬迁脚本不删除空目录 | §4.3 ORPHAN_SHELL 分类 |
| 2026-04-24 | tmp_replace_composer*.py 未清理 | 临时脚本无 TTL 标记 | §4.2 temp_* 清除 |

## 11. 消费者注册表

| 消费者 | 依赖内容 | 同步要求 |
|--------|---------|---------|
| src/zephyr/gates/task_completion_gate.py | 残留物分类规则、退出码定义 | 分类规则变更必须同 commit 更新 |
| src/zephyr/db/task_repo.py | COMPLETED/VERIFIED 状态转换条件 | 转换条件变更必须同 commit 更新 |
| scripts/governance/check_handoff_protocol.py | 任务状态校验 | 状态语义变更需同步 |

## 12. 变更记录

| 版本 | 日期 | 变更内容 |
|------|------|---------|
| 1.1.0 | 2026-05-01 | 微调：§5.2 取消审批表改为引用 lifecycle-standard §2.1（消重复）；depends_on 补 GOV-TASK-004 + CP-TASK-CARD-KMS-001；PS-STD-001 引用从 §4.2 改为 §7；status draft→active |
| 1.0.0 | 2026-04-29 | 合并 task-card-standard.md §8（G5 门禁）+ task-completion-cleanup-gate.md（清扫三步法），新增完成定义（§2）、验证定义（§3）、取消关闭流程（§5）；统一任务关闭规则 |
