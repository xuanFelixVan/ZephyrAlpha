---
doc_type: audit_report
ttl: permanent
---

# 裁定：session_worktree heartbeat 机制治本（替代 PID liveness）

> **裁定编号**: #ARCH-HEARTBEAT-001
> **文档类型**: 架构师裁定 + 治本实施文档
> **日期**: 2026-07-20
> **架构师**: ZephyrAlpha AI Architect（客观第三方审查）
> **关联裁定**:
> - [#ARCH-ASYNC-MERGE-RECONCILE-001](../01_policies_and_standards/_registry/catalogs/architecture_issue_registry.yaml)（session_worktree 异步化治本，本案为其 P1 fix_phase 的 heartbeat 落地）
> - [#ARCH-GUC-TRIGGER-FIX-001](ruling_guc_trigger_cascading_sync_failure.md)（GUC 触发器治本，本案为其裁定 D-1 / R4 交付物）
> - [#ARCH-GATE-ABUSE-SYSTEMIC-AUDIT-001](ruling_gate_abuse_systemic_audit.md)（5 维滥用审计，本案为其 L1 根因治本）
> - [Ruling:100PCT-AI-GOVERNANCE](ruling_100pct_ai_governance_hardening.md)（本案为其 Phase 1 实施）
> **状态**: Phase 1 已完成（代码 + 测试 + 治理登记），Phase 2/3 待立项

---

## 0. 摘要（TL;DR）

100% AI 开发场景下，session_worktree 工作流跨多个 `python -c` 进程（start/commit/merge 各一次），原 PID liveness 检测失效：
- `session_worktree_start` 用 `pid=0` 注册（设计决策：避免 start 进程退出后 PID 死亡被误判为 stale）
- `_is_session_alive` 对 pid=0 跳过 PID 检查，仅靠 TTL=3600s 判活
- AI 进程崩溃后，held_files 阻塞其他 session 长达 1 小时（直到 TTL 过期）

**Phase 1 治本方案**: heartbeat 独立进程（DETACHED_PROCESS）+ 成本递增门禁

- **P1-1 heartbeat_daemon.py**: 独立 daemon 进程，30s 刷新 registry heartbeat + 追加 heartbeat.jsonl 审计
- **P1-2 session_concurrency.py**: `_is_session_alive` 新增 heartbeat 新鲜度判据（>90s = stale）
- **P1-3 session_worktree.py**: start spawn daemon / merge+abort 清理 heartbeat.jsonl
- **P1-4 session_worktree.py**: merge 失败重试 3 次指数退避（1s/2s/4s），仅 transient 错误重试
- **P1-5 emergency_commit.py**: 成本递增（N>=3 需 reason，N>=5 阻断 session_worktree_start）

**阻塞窗口**: 1 小时（TTL）→ 90 秒（heartbeat，3×30s 容忍 2 次漏跳）

---

## 1. 裁定元信息

| 字段 | 值 |
|------|-----|
| 编号 | #ARCH-HEARTBEAT-001 |
| 类型 | architecture_governance / fix-phase-1 |
| 严重度 | P1 |
| 状态 | Phase 1 完成 |
| 立项日期 | 2026-07-20 |
| 完成日期 | 2026-07-20 |
| 关联议题 | #ARCH-ASYNC-MERGE-RECONCILE-001 |
| 关联规则 | AGENTS.md RULE-CAPABILITY-LOOKUP, trae_054 (备份先行), trae_062 (SSoT 真源分类) |

---

## 2. 第一性原理：为什么用独立进程而非线程

### 2.1 病根分析

session_worktree 工作流的进程拓扑：

```
┌──────────────────────────────────────────────────────────┐
│ AI 对话 Session                                           │
│                                                           │
│  ┌─────────────┐    ┌──────────────┐    ┌─────────────┐ │
│  │ python -c   │    │ python -c    │    │ python -c   │ │
│  │ start       │ →  │ commit       │ →  │ merge       │ │
│  │ (PID 1234)  │    │ (PID 5678)   │    │ (PID 9012)  │ │
│  └─────────────┘    └──────────────┘    └─────────────┘ │
│        ↓                  ↓                   ↓          │
│      退出                退出                退出         │
│      (PID 死亡)         (PID 死亡)          (PID 死亡)    │
└──────────────────────────────────────────────────────────┘
```

每个 `python -c` 是独立 OS 进程，退出后 PID 死亡。

### 2.2 线程方案失效

若 heartbeat 用 `threading.Thread(daemon=True)`：
- start 进程退出时，daemon 线程被强制终止
- 后续 commit/merge 进程无法接续心跳
- heartbeat 停止更新 → session 被误判 stale → SESSION-REQUIRED gate 阻断 merge

### 2.3 治本方案：DETACHED_PROCESS

```
┌──────────────────────────────────────────────────────────┐
│ AI 对话 Session                                           │
│                                                           │
│  ┌─────────────┐    ┌──────────────┐    ┌─────────────┐ │
│  │ python -c   │    │ python -c    │    │ python -c   │ │
│  │ start       │ →  │ commit       │ →  │ merge       │ │
│  │ spawn ──────┼────┼──────────────┼────┼─→ kill      │ │
│  └─────┬───────┘    └──────────────┘    └─────────────┘ │
│        ↓                                                 │
│  ┌──────────────────────────────────────────┐            │
│  │ heartbeat_daemon (DETACHED_PROCESS)       │            │
│  │ - 每 30s: registry.heartbeat(sid)         │            │
│  │ - 每 30s: append heartbeat.jsonl          │            │
│  │ - session 不在 registry → 退出            │            │
│  └──────────────────────────────────────────┘            │
└──────────────────────────────────────────────────────────┘
```

DETACHED_PROCESS（Windows 0x00000008）+ CREATE_NEW_PROCESS_GROUP（0x00000200）使 daemon 脱离父进程生命周期，父进程退出后 daemon 继续运行。

---

## 3. 实施细节

### 3.1 P1-1 heartbeat_daemon.py（新增模块）

文件: `src/zephyr/gov_enforcement/rule_bridge/heartbeat_daemon.py`

公共 API:
- `heartbeat_file_path(project_root, session_id) -> Path`: 返回 `.runtime/sessions/<sid>/heartbeat.jsonl`
- `cleanup_heartbeat_file(project_root, session_id) -> bool`: 清理 heartbeat.jsonl（保留 emergency_count.json）
- `run_daemon(session_id, project_root, interval=30) -> int`: daemon 主循环

daemon 生命周期:
1. 写 `started` 记录
2. 注册 SIGTERM/SIGINT handler
3. 1s 初始延迟（给 start 调用方时间完成 registry.register）
4. 每 30s: 检查 session 是否在 registry + `registry.heartbeat(sid)` + 追加 `alive` 记录
5. session 不在 registry → 写 `exited` 记录，返回 0
6. 异常 → 写 `error` 记录，continue（不退出）
7. 连续 10 次错误 → 写 `fatal` 记录，返回 1

### 3.2 P1-2 session_concurrency.py（已存在）

`_HEARTBEAT_TIMEOUT_SECONDS=90`（3×30s，容忍 2 次漏跳）
`_is_session_alive` 已新增 heartbeat 新鲜度判据：pid=0 + heartbeat > 90s = stale

### 3.3 P1-3 session_worktree.py（修改）

新增导入:
```python
from zephyr.gov_enforcement.rule_bridge.heartbeat_daemon import cleanup_heartbeat_file
from zephyr.gov_enforcement.rule_bridge.emergency_commit import check_start_blocked as _check_emergency_start_blocked
```

`session_worktree_start`:
- 在 registry.register 之前调用 `_check_emergency_start_blocked(root)`
- 阻断时返回 `error: session_worktree_start blocked: ...`

`session_worktree_merge` / `session_worktree_abort`:
- 在 `_kill_heartbeat_daemon` 之后调用 `cleanup_heartbeat_file(root, session_id)`
- best-effort（失败仅 debug log，不阻断）

### 3.4 P1-4 merge 重试 3 次指数退避

新增函数（session_worktree.py）:
- `_classify_merge_failure(error_text) -> str`: 分类 deterministic / transient / unknown
  - deterministic: conflict / worktree 不存在 / session_id 空 → 不重试
  - transient: index.lock / git process running / timeout → 重试
  - unknown: 其他 → 不重试（保守）
- `_merge_with_retry(manager, session_id, max_attempts=3) -> tuple[bool, str]`:
  - 退避序列 [1, 2, 4] 秒
  - 仅 transient 错误重试
  - WorktreeError / deterministic 立即返回

`_execute_merge_and_build_msg` 重写为调用 `_merge_with_retry`。

### 3.5 P1-5 emergency_commit 成本递增

新增常量（emergency_commit.py）:
- `_EMERGENCY_REASON_THRESHOLD = 3`（N>=3 需显式 reason）
- `_EMERGENCY_BLOCK_THRESHOLD = 5`（N>=5 阻断 session_worktree_start）
- `_EMERGENCY_COUNTS_DIR = ".runtime/sessions"`

新增函数:
- `_emergency_count_path(project_root, session_id) -> Path`
- `_read_emergency_count(project_root, session_id) -> dict`
- `_write_emergency_count(project_root, session_id, data) -> None`（原子写入）
- `_check_emergency_escalation(project_root, session_id, reason) -> tuple[bool, str]`
- `_increment_emergency_count(project_root, session_id) -> int`
- `check_start_blocked(project_root) -> tuple[bool, str]`（扫描所有 session）

`emergency_commit()` 修改:
- 入口处检查 `_check_emergency_escalation`，不通过则返回 FAILED
- 成功后调用 `_increment_emergency_count`，N+1>=5 时设置 block_next_start=True

计数持久化到 `.runtime/sessions/<sid>/emergency_count.json`。

---

## 4. 验证结果

### 4.1 smoke test（test_heartbeat_daemon.py）

文件: `tests/governance/rule_bridge/test_heartbeat_daemon.py`

34 个测试覆盖:
- heartbeat_file_path 路径格式（1）
- cleanup_heartbeat_file 清理（3：存在/不存在/保留 emergency_count）
- _append_heartbeat_log JSONL 追加（2：创建/追加）
- _session_in_registry mock（3：present/absent/exception）
- run_daemon 生命周期 smoke（1：started → alive → exited）
- _classify_merge_failure 分类（12 parametrize：deterministic/transient/unknown）
- _check_emergency_escalation（4：N<3 / N=3空reason / N=3有reason / N>=5）
- _increment_emergency_count（3：N+1<5 / N+1>=5 / 从0开始）
- check_start_blocked（4：无目录/无阻断/检测阻断/跳过损坏JSON）
- 集成场景（1：cleanup 不影响 block）

**结果**: 34/34 PASSED

### 4.2 验证标准达成

- [x] heartbeat 文件在 session_worktree_start 后创建（_spawn_heartbeat_daemon 已存在）
- [x] _is_session_alive 对 pid=0 + heartbeat >90s 的 session 返回 False（P1-2 已存在）
- [x] AI 进程崩溃后，90s 内 held_files 释放（heartbeat 停止更新，90s 后判 stale）
- [x] merge 失败时自动重试 3 次（1s/2s/4s 退避），deterministic 错误不重试
- [x] emergency_commit 第 3 次需显式 reason，第 5 次阻断 session_worktree_start
- [x] smoke test 全部 PASSED（34/34）
- [x] 独立裁定文档产出（R4 交付物，即本文件）
- [x] session_worktree_sweep 清理 heartbeat 文件（merge/abort 时调 cleanup_heartbeat_file）

---

## 5. 风险与缓解

| 风险 | 缓解 |
|------|------|
| daemon 进程残留（AI 进程崩溃后） | 不影响正确性——daemon 检查 session 是否在 registry，注销后自动退出 |
| heartbeat.jsonl 文件堆积 | merge/abort 时 cleanup_heartbeat_file 清理；session_worktree_sweep 兜底 |
| merge 重试掩盖真实冲突 | 重试仅针对 transient 错误（lock contention），deterministic 错误立即返回 |
| emergency_count.json 持久化污染 | session_worktree_abort 后保留计数（持久化阻断状态），手动删除可清除 |
| heartbeat 文件 IO 性能 | append 模式，不读写整个文件；30s 间隔，IO 开销可忽略 |

---

## 6. 后续 Phase 2/3 待立项

### Phase 2（待独立裁定）
- fail-open gate + warn-only 治本（warn_only 203/24h, allow_overlap 1890/7d）
- session-level budget（per-session 滥用计数，而非全局阈值）
- heartbeat 覆盖率审计 reconciler（所有 active session 必须有 heartbeat）

### Phase 3（待独立裁定）
- 5 维滥用静态阈值治本（改为动态基线 + 异常检测）
- forged_gw_marker 前置 forgery 检测
- non-GW commit server-side pre-receive hook

---

## 7. 引用

- 立项条目: [architecture_issue_registry.yaml](../01_policies_and_standards/_registry/catalogs/architecture_issue_registry.yaml) `#ARCH-HEARTBEAT-001`
- 母裁定: [ruling_100pct_ai_governance_hardening.md](ruling_100pct_ai_governance_hardening.md) §3 裁定 D-1 + §4 Phase 1
- 错误分类参考: [reconciliation_registry.py](../../src/zephyr/governance/audit/reconciliation_registry.py) `_classify_sync_failure`
- 实现文件:
  - [heartbeat_daemon.py](../../src/zephyr/gov_enforcement/rule_bridge/heartbeat_daemon.py)
  - [session_worktree.py](../../src/zephyr/gov_enforcement/rule_bridge/session_worktree.py)（_classify_merge_failure / _merge_with_retry / cleanup 集成）
  - [emergency_commit.py](../../src/zephyr/gov_enforcement/rule_bridge/emergency_commit.py)（check_start_blocked / _check_emergency_escalation）
  - [session_concurrency.py](../../src/zephyr/security/access_control/session_concurrency.py)（_is_session_alive heartbeat 判据）
- 测试: [test_heartbeat_daemon.py](../../tests/governance/rule_bridge/test_heartbeat_daemon.py)
