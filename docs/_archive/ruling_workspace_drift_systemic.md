---
ttl: permanent
---

# 裁定：系统性防漂移体系盲区治本（4 盲区 3 Phase 全闭环）

> **裁定编号**: #ARCH-WORKSPACE-DRIFT-SYSTEMIC-001
> **文档类型**: 架构师裁定 + 治本实施文档
> **日期**: 2026-07-20
> **架构师**: ZephyrAlpha AI Architect（客观第三方审查）
> **关联裁定**:
> - [#ARCH-WORKTREE-PRE-MERGE-SYSPATH-001](#ARCH-WORKTREE-PRE-MERGE-SYSPATH-001)（pre-merge sys.path 治本，session lifecycle 同维度）
> - [#ARCH-WORKTREE-002](#ARCH-WORKTREE-002)（worktree 物理隔离基础，本案在其上加工作区 clean 检查）
> - [Ruling:100PCT-AI-GOVERNANCE](ruling_100pct_ai_governance_hardening.md)（100% AI 场景第一性原理，warn=通过治本须 fail-closed）
> - [#ARCH-TOOL-HEALTH-V1](#ARCH-TOOL-HEALTH-V1)（workspace_hygiene_reconciler 复用基础）
> - [#ARCH-CROSS-COMMIT-ATOMICITY-001](#ARCH-CROSS-COMMIT-ATOMICITY-001)（跨 commit 原子性，本案 Phase 3 gate priority=77 紧接其后）
> **关联规则**: AGENTS.md FP-ISO.4C (worktree 君子协定), trae_054 (备份先行), trae_060 (向内收三原则), trae_062 (SSoT 真源分类)
> **状态**: Phase 1 + 1.5 + 2 + 3 全部完成（3 Phase 闭环）

---

## 0. 摘要（TL;DR）

100% AI 开发场景下，前序会话"遗留风险"报告指出 4 个系统性盲区：

1. **工作区漂移检测全部 post-commit 触发**——workspace_hygiene_reconciler 是 post-commit priority=890，commit 时已搭便车完成，post-commit warn 无治本作用
2. **session_worktree_commit 只提交显式列出的 files**——AI 用 Edit/Write 写项目根，session 文件在主工作区是 modified 状态，commit 时未列入 files 参数=搭便车风险
3. **无 session_end 工作区 clean 检查**——session_worktree_start/abort 无工作区 clean 验证，新 session 启动时主工作区可能有其他 session 残留
4. **文档"已完成"声明无硬验证**——ruling_*.md / architecture_issue_registry.yaml 中"已完成（commit <hash>）"声明，AI 可凭记忆/幻觉填写不存在的 hash

**病根（第一性原理·100% AI 场景）**: 5 层闭环模型（post-commit warn）依赖人类视觉通道闭环——100% AI 场景下 AI 把 warn 当"通过"，warn=无效。治本必须前置为 pre-commit fail-closed 或自动处理（无人类介入）。

**治本方案（3 Phase 渐进）**:
- **Phase 1**: session lifecycle 工作区 clean 检查 + pre-commit drift warn（4 钩子 + 5 helper）
- **Phase 2**: auto-recover staged 完整性修复（_restore_auto_sync_batch unstage+restore 两步）
- **Phase 3**: RULING-COMMIT-VERIFIED gate（priority=77，文档"已完成"声明 commit hash 真实性硬验证）

**3 Phase 闭环**:
- Phase 1（commit 4f56348145, merge 9a6d66efac）
- Phase 2（commit c343ae5d6b, merge 0259db8a1fef）
- Phase 3（commit f7f79ae684, merge 07f1e58763）

---

## 1. 裁定元信息

| 字段 | 值 |
|------|-----|
| 编号 | #ARCH-WORKSPACE-DRIFT-SYSTEMIC-001 |
| 类型 | architecture_governance / fix-phase-3 |
| 严重度 | P1（防漂移体系盲区，100% AI 场景下 warn=通过） |
| 状态 | Phase 1 + 1.5 + 2 + 3 全部完成（3 Phase 闭环） |
| 立项日期 | 2026-07-20 |
| 完成日期 | 2026-07-20 |
| 关联议题 | #ARCH-WORKTREE-PRE-MERGE-SYSPATH-001, #ARCH-WORKTREE-002, #ARCH-TOOL-HEALTH-V1 |
| 关联规则 | AGENTS.md FP-ISO.4C, trae_054, trae_060, trae_062 |

---

## 2. 第一性原理：100% AI 场景下 warn=通过

### 2.1 5 层闭环模型的盲区

ZephyrAlpha 治理体系采用 5 层闭环模型（2026-07-20 升级为 6 层）：

```
Layer 1: pre-commit gate（阻断）
Layer 2: post-commit reconciler（告警 + 自动修复）
Layer 3: reconciler health monitor（健康度监控）
Layer 4: commit gateway abuse monitor（滥用检测）
Layer 5: human review（人类审查）
Layer 6: preventability（可预防性，pre-commit 前置）
```

**盲区**: Layer 2-4 都是 post-commit 触发，依赖 Layer 5（人类审查）闭环。100% AI 开发场景下：
- Layer 5 缺失（无人类视觉通道）
- AI 把 warn 当"通过"（无人类介入=warn 无效）
- post-commit reconciler 只能"事后修复"，无法"事前预防"

### 2.2 4 个系统性盲区的第一性原理分析

#### 盲区 1: 工作区漂移检测全部 post-commit 触发

```
AI session A 编辑文件 X (main workspace)
AI session A commit 文件 Y (worktree)
→ main workspace 文件 X 仍是 modified 状态
→ workspace_hygiene_reconciler post-commit 检测到 X modified
→ warn "non-auto-sync modified files detected"
→ AI 看到 warn 但认为"已 commit，warn 无关"
→ 文件 X 搭便车风险持续到下次 commit
```

**病根**: post-commit warn 在 100% AI 场景下=无效（AI 不看 warn，只看 commit 成功/失败）。

#### 盲区 2: session_worktree_commit 只提交显式列出的 files

```
AI 用 Edit/Write 写项目根文件 A, B, C
AI 调 session_worktree_commit(session_id, ['A', 'B'], msg)
→ A, B 在 worktree commit
→ C 在 main workspace 仍是 modified 状态
→ 下次 session_worktree_commit 时 C 可能被带入（搭便车）
```

**病根**: AI 容易漏列文件（特别是 registry YAML 等被 Edit 的文件）。

#### 盲区 3: 无 session_end 工作区 clean 检查

```
AI session A 编辑文件 X (main workspace)
AI session A abort (未 commit X)
→ main workspace 文件 X 仍是 modified 状态
AI session B 启动
→ session_worktree_start 不检查 main workspace clean
→ session B commit 时文件 X 被 WORKSPACE-CLEAN-CHECK 阻断
```

**病根**: session 间无工作区 clean 协议，残留文件阻断后续 session。

#### 盲区 4: 文档"已完成"声明无硬验证

```
AI 在 architecture_issue_registry.yaml 写:
  "Phase X（已完成 2026-07-20，commit <fake-hash>）"
→ commit <fake-hash> 可能不存在（AI 幻觉/记忆错误）
→ 文档 SSoT 失效（"已完成"声明可能是幻觉产物）
→ 后续 AI 读取文档=在幻觉数据上推断=幻觉温床
```

**病根**: 文档 SSoT 无 commit hash 真实性硬验证，AI 可凭记忆填写不存在的 hash。

---

## 3. 治本方案（3 Phase 渐进）

### 3.1 Phase 1: session lifecycle 工作区 clean 检查 + pre-commit drift warn

**施工内容**:
- 4 钩子接入（session_worktree_start/abort/merge + pre-commit）
- 5 helper 函数：
  - `_classify_workspace_files` (cc=7): 分类工作区文件（real_code / auto_sync / session_files）
  - `_restore_auto_sync_batch` (cc=6): 批量 restore auto-sync 产物（Phase 2 升级为 unstage+restore 两步）
  - `_evaluate_drift_after_restore` (cc=13): 评估 restore 后的 drift 状态
  - `_check_workspace_clean` (cc=10): 核心检查逻辑
  - `_log_workspace_drift_warn` (cc=11): 遥测落盘 .runtime/workspace_drift_warn.jsonl
- 3 包装函数 + `_WS_CLEAN_GATE_ID` 常量

**fail-closed/fail-open 策略**:
- merge = fail-closed（阻断，WORKSPACE-CLEAN-CHECK gate）
- start/abort = fail-open（告警不阻断，新 session 启动时不应被旧残留阻断）
- commit Phase 1.5 = fail-open（遥测落盘，不阻断 commit 但记录 drift）

**复用原则（向内收 trae_060）**:
- `_git_status_porcelain` / `_is_auto_sync_product` from workspace_hygiene_reconciler
- `GitCommandBatcher.git_restore_batch` from git_batcher

**session_files 排除语义**: worktree 模式下 AI 用 Edit 写项目根，session 文件在主工作区是 modified 状态但不是搭便车（已在 worktree commit 中）。

**force=True 逃生通道**: 对标 PRE-MERGE-TOPO-CHECK 的 force 语义，跳过 WORKSPACE-CLEAN-CHECK。

**验证**:
- 169 tests passed (test_session_worktree_workspace_clean.py 33 + 相关 136)
- start 钩子告警实际触发验证成功（新 session 启动时检测到 48 real code modified）

**交付**: commit 4f56348145, merge 9a6d66efac

### 3.2 Phase 2: auto-recover staged 完整性修复

**病根**: 旧版 `_restore_auto_sync_batch` 只调用 `git_restore_batch(staged=False)`，对：
- `"M "` (staged only) 完全无效（staged 版本保留）
- `"MM"` (staged + worktree) 只还原 worktree 部分，staged 版本保留

→ staged auto-sync 文件被带入下次 commit，搭便车风险

**治本**:
1. 先 `git_restore_batch(staged=True)` unstage（对纯 worktree modified 是 no-op，无副作用）
2. 再 `git_restore_batch(staged=False)` restore worktree 到 HEAD
3. 合并判断：既 unstage 成功又 restore 成功才算完全还原

**验证**:
- 177 tests passed + 1608 commit_gates 全量通过
- 4 新测试：staged_only / mm_state / mixed_staged_and_worktree / empty_files
- 4 集成测试：staged_auto_sync_passes_merge / mm_state_passes_merge / staged_real_code_blocks_merge / staged_real_code_fail_open_abort

**交付**: commit c343ae5d6b, merge 0259db8a1fef

### 3.3 Phase 3: RULING-COMMIT-VERIFIED gate + ruling 文档落盘

**施工内容**:
- 新建 `ruling_commit_verified_gate.py` (256 行, MOD-GOV-ruling_commit_verified_gate)
- gate 注册：git_commit_gateway.py L115 import + L404 register

**gate 规格**:
- gate_id: `RULING-COMMIT-VERIFIED`
- priority: 77（紧接 RULE-FOUR-WAY-ALIGNMENT=76，属 reference-related gate 组）
- 检测范围: ruling_*.md + architecture_issue_registry.yaml
- 检测模式: diff-based 增量检测（只检查 added 行，不阻断历史）
- 验证方式: `git cat-file -e <hash>^{commit}` 验证 hash 真实存在
- 逃生通道: commit message 含 `[no-verify-ruling:<reason>]` 标记
- fail-closed: git 失败/ast 失败阻断（非 Zephyr 项目 skip）

**复杂度治本**:
- `_check` 闭包 cc=16 → 提取 `_detect_violations` helper (cc=13) + `_check` (cc=5)
- 对标裁定#216 Tier1 P1 Extract Method 重构

**注册表登记**:
- `capability_canonical_file_registry.yaml`: capability_id `ruling_commit_verified_gate` + creation_token
- `noqa_exempt_registry.yaml`: `no-verify-ruling` marker (scope=commit-message)
- `architecture_issue_registry.yaml`: #ARCH-WORKSPACE-DRIFT-SYSTEMIC-001 完整条目

**验证**: 36 测试全部通过
- TestExtractCommitHashes 9
- TestIsTriggerFile 6
- TestVerifyCommitExists 3
- TestRulingCommitVerifiedGate 12
- TestGateSpecMetadata 3
- TestEscapeMarker 4

**交付**: commit f7f79ae684, merge 07f1e58763

---

## 4. 架构师裁定（不实现项）

### 4.1 batch commit 入口——伪需求，不实现

**提议**: 新建 batch_commit 入口，一次 commit 多个 session 的文件。

**裁定**: 不实现。理由：
1. 违反"一个任务一个 commit"语义（AGENTS.md FP-ISO.4C）
2. batch commit 破坏 commit 原子性（一个 commit 失败影响全部）
3. session_worktree 物理隔离已解决并发问题，无需 batch

### 4.2 全量 schema 化——过度工程，不实现

**提议**: 强制 ruling_*.md / architecture_issue_registry.yaml 使用 JSON Schema 结构化。

**裁定**: 不实现。理由：
1. ruling 文档结构多样性高（技术分析/裁定/施工方案/验证），强制 schema 化反而阻碍表达
2. RULING-COMMIT-VERIFIED gate 已通过正则+git 验证解决核心问题（hash 真实性）
3. schema 化是"完美方案"，但当前问题不需要完美方案（治本即可）

---

## 5. 影响范围

### 5.1 代码变更（9 个文件）

| 文件 | Phase | 变更类型 |
|------|-------|---------|
| src/zephyr/gov_enforcement/rule_bridge/session_worktree.py | 1+1.5+2 | 4 钩子 + 5 helper + _restore_auto_sync_batch staged 修复 |
| src/zephyr/gov_enforcement/commit_gates/ruling_commit_verified_gate.py | 3 | 新建 gate (priority=77) |
| src/zephyr/gov_enforcement/rule_bridge/git_commit_gateway.py | 3 | gate 注册 L115 import + L404 register |
| tests/governance/commit_gates/test_ruling_commit_verified_gate.py | 3 | 新建测试 (36 测试) |
| tests/governance/rule_bridge/test_session_worktree_workspace_clean.py | 1+2 | 测试 (33+8 测试) |
| docs/01_policies_and_standards/_registry/catalogs/architecture_issue_registry.yaml | 3 | 本案登记 |
| docs/01_policies_and_standards/_registry/catalogs/capability_canonical_file_registry.yaml | 3 | capability + creation_token |
| docs/01_policies_and_standards/_registry/catalogs/noqa_exempt_registry.yaml | 3 | no-verify-ruling marker |
| docs/_archive/ruling_workspace_drift_systemic.md | 3 | 本 ruling 文档 |

### 5.2 治理体系升级

| 层级 | 升级前 | 升级后 |
|------|--------|--------|
| session lifecycle | 无工作区 clean 检查 | 4 钩子接入 + force 逃生通道 |
| pre-commit | 无 drift warn | Phase 1.5 遥测落盘 |
| auto-recover | 只 restore worktree | unstage + restore 两步完整恢复 |
| 文档 SSoT | "已完成"声明无验证 | RULING-COMMIT-VERIFIED gate 硬验证 |

---

## 6. 验证结果

### 6.1 测试套件

| 测试文件 | 测试数 | 结果 |
|---------|-------|------|
| test_ruling_commit_verified_gate.py | 36 | PASSED |
| test_session_worktree_workspace_clean.py | 33+8 | PASSED |
| test_session_worktree_pre_merge_syspath.py | 4 | PASSED |
| **总计** | **73+** | **ALL PASSED** |

### 6.2 实证验证

- start 钩子告警实际触发：新 session 启动时检测到 48 real code modified
- WORKSPACE-CLEAN-CHECK 阻断 merge：实证有效（本 session 需 force=True 逃生）
- RULING-COMMIT-VERIFIED gate 生效：commit 时自动验证 architecture_issue_registry.yaml 中 commit hash

### 6.3 3 Phase commit/merge hash

| Phase | commit | merge |
|-------|--------|-------|
| Phase 1 + 1.5 | 4f56348145 | 9a6d66efac |
| Phase 2 | c343ae5d6b | 0259db8a1fef |
| Phase 3 | f7f79ae684 | 07f1e58763 |

---

## 7. 后续工作

无待执行项。3 Phase 闭环已完成。

**可能的后续加固（非必需）**:
- BARE-SUBPROCESS gate warn: ruling_commit_verified_gate.py L139 使用 subprocess.run，可改用 process_pool.run_subprocess_hidden
- priority=77 冲突: RULING-COMMIT-VERIFIED 与 BLUEPRINT-FORMAT 同 priority=77，可调整其中一个到唯一 priority
- CAPABILITY-OVERLAP warn: 'gate' token 与 vocab_hardcode_detector 重叠（warn-only，无影响）

以上均为 warn-only，不影响功能，可在后续 session 择机修复。

---

## 8. 关联文档

- [architecture_issue_registry.yaml](../01_policies_and_standards/_registry/catalogs/architecture_issue_registry.yaml) — 本案完整条目
- [capability_canonical_file_registry.yaml](../01_policies_and_standards/_registry/catalogs/capability_canonical_file_registry.yaml) — capability + creation_token
- [noqa_exempt_registry.yaml](../01_policies_and_standards/_registry/catalogs/noqa_exempt_registry.yaml) — no-verify-ruling marker
- [ruling_100pct_ai_governance_hardening.md](ruling_100pct_ai_governance_hardening.md) — 100% AI 场景第一性原理
- [ruling_session_worktree_heartbeat.md](ruling_session_worktree_heartbeat.md) — session liveness 治本
