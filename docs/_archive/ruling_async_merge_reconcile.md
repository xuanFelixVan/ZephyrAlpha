---
ttl: permanent
---

# 裁定：session_worktree 异步化治本（emergency_commit / allow_overlap 滥用 L1 根因消除）

> **裁定编号**: #ARCH-ASYNC-MERGE-RECONCILE-001
> **文档类型**: 架构师裁定 + 治本路线图
> **日期**: 2026-07-20
> **架构师**: ZephyrAlpha AI Architect（客观第三方审查）
> **关联裁定**:
> - [#ARCH-HEARTBEAT-001](ruling_session_worktree_heartbeat.md)（P1 fix_phase 落地——heartbeat daemon 替代 PID liveness）
> - [#ARCH-GATE-ABUSE-SYSTEMIC-AUDIT-001](ruling_gate_abuse_systemic_audit.md)（5 维滥用审计，本案为其 L1 根因治本）
> - [Ruling:100PCT-AI-GOVERNANCE](ruling_100pct_ai_governance_hardening.md)（本案为其 R2 阈值调整 + P3 收尾复核产物）
> **状态**: Layer 2 已完成 / P1 heartbeat 已完成 / P1 异步化待立项 / P2 阈值收紧待治本后执行

---

## 0. 摘要（TL;DR）

100% AI 开发场景下，`session_worktree_merge` 同步阻塞 + 跨进程 PID liveness 失效是 `emergency_commit`（21/24h）和 `allow_overlap`（1890/7d）滥用的 **L1 最深层根因**：

| 维度 | 病根 | 滥用后果 |
|------|------|----------|
| 同步阻塞 | git subprocess（add/commit/checkout/merge）在 worktree 数量增长或 git lock 争用时延迟 5-15s | AI 对话往返压力下走 `emergency_commit` 逃生（17 次/24h sprint，全合法治理 commit） |
| PID liveness 失效 | 跨进程 PID 检测在 Windows PID 复用 / Linux PID wraparound 下不可靠 | `allow_overlap` 频繁触发（1890/7d），AI 不得不逃生才能提交 |

**治本方向**: session_worktree 异步化（fire-and-forget + 后台 worker + heartbeat 替代 PID）

**当前进展**:
- Layer 2 立项登记 ✅（2026-07-20）
- R2 阈值过渡调整 ✅（emergency 30→20，allow_overlap 30→500）
- P1 heartbeat 落地 ✅（2026-07-20，#ARCH-HEARTBEAT-001）
- P1 异步化改造 ⏳（待独立裁定立项）
- P2 阈值收紧 ⏳（治本完成后执行）

---

## 1. 裁定元信息

| 字段 | 值 |
|------|-----|
| 编号 | #ARCH-ASYNC-MERGE-RECONCILE-001 |
| 类型 | architecture_governance / root-cause-elimination |
| 严重度 | P1 |
| 状态 | open（heartbeat 子议题已闭环，异步化子议题待立项） |
| 立项日期 | 2026-07-20 |
| 关联议题 | #ARCH-HEARTBEAT-001（P1 fix_phase 落地）, #ARCH-GATE-ABUSE-SYSTEMIC-AUDIT-001（L1 根因引用） |
| 关联规则 | AGENTS.md RULE-CAPABILITY-LOOKUP（L1 根因消除）, trae_054（备份先行）, trae_053（双轨判定） |

---

## 2. 第一性原理：L1 根因分析

### 2.1 滥用数据基线（2026-07-19 复核）

`commit_gateway_abuse_monitor_reconciler.py` 5 维滥用检测结果：

| 维度 | 7d 计数 | 阈值 | 倍数 | 表象根因 |
|------|:---:|:---:|:---:|------|
| emergency_commit | 21/24h | 10 | 2.1× | AI 因 git 性能压力绕过 session_worktree |
| allow_overlap | 1890/7d | 30 | 62× | PID liveness 失效导致 held_files 误阻断 |
| warn_only | 55/24h | 50 | 1.1× | per-hour 阈值抓不到持续低频滥用 |
| forged_gw_marker | 4 个 commit | 0 | — | 非 GW 提交伪造 GW 标记（独立排查报告） |

### 2.2 L1 最深层根因（追问到底）

```
表象: emergency_commit 21/24h
  └─ 为什么 AI 走 emergency_commit？
     └─ session_worktree_merge 同步阻塞 5-15s，AI 对话超时压力
        └─ 为什么 merge 阻塞？
           └─ git subprocess 串行 + lock 争用
              └─ 为什么不异步化？
                 └─ session_worktree 设计为同步 API（L1 根因）

表象: allow_overlap 1890/7d
  └─ 为什么 AI 走 allow_overlap？
     └─ HELD_OVERLAP_VIOLATION 误阻断（文件被 stale session 持有）
        └─ 为什么 stale session 持有文件？
           └─ PID liveness 失效，stale session 不被清理
              └─ 为什么 PID liveness 失效？
                 └─ 跨进程 PID 检测在 Windows PID 复用 / Linux PID wraparound 下不可靠（L1 根因）
```

### 2.3 治本 vs 治标

| 方案 | 层面 | 同类问题重现 | 可泛化 |
|------|------|:---:|:---:|
| 提高 emergency_commit 阈值 | 症状层 | 会 | 否 |
| 提高 allow_overlap 阈值 | 症状层 | 会 | 否 |
| heartbeat 替代 PID liveness | 系统设计层 | **不会** | 是（消除跨进程 PID 失效） |
| session_worktree 异步化 | 系统设计层 | **不会** | 是（消除同步阻塞） |

---

## 3. 治本路线图

### 3.1 Phase 分层

| Phase | 内容 | 状态 | 关联议题 |
|:---:|------|:---:|------|
| Layer 2 | 立项登记 + R2 阈值过渡 | ✅ 完成 | 本案 |
| P1 heartbeat | detached daemon 替代 PID liveness | ✅ 完成 | #ARCH-HEARTBEAT-001 |
| P1 异步化 | commit/merge 改 fire-and-forget + 后台 worker | ⏳ 待立项 | 本案 |
| P2 阈值收紧 | 治本后 emergency 20→5, allow_overlap 500→200 | ⏳ 待治本完成 | 本案 |
| P3 长期 | heartbeat 覆盖率审计 + 治本后滥用自然下降验证 | ⏳ 待立项 | 本案 |

### 3.2 Layer 2 已完成项（2026-07-20）

| 交付物 | 文件 | 说明 |
|------|------|------|
| 立项登记 | architecture_issue_registry.yaml | 本案条目登记 |
| R2 阈值过渡 | commit_gateway_abuse_monitor_reconciler.py | emergency 30→20, allow_overlap 30→500 |
| 引用注释 | commit_gateway_abuse_monitor_reconciler.py | #ARCH-ASYNC-MERGE-RECONCILE-001 引用 |

### 3.3 P1 heartbeat 已完成项（2026-07-20，#ARCH-HEARTBEAT-001）

| 交付物 | 文件 | 说明 |
|------|------|------|
| daemon 入口 | src/zephyr/gov_enforcement/rule_bridge/heartbeat_daemon.py | detached subprocess, 30s 刷新 heartbeat |
| 判活逻辑 | src/zephyr/security/access_control/session_concurrency.py | _is_session_alive 双轨判据（pid=0 用 90s heartbeat 超时） |
| spawn/kill 集成 | src/zephyr/gov_enforcement/rule_bridge/session_worktree.py | start spawn / merge+abort kill |
| smoke test | tests/governance/rule_bridge/test_heartbeat_daemon.py | 10 测试全 PASSED |
| 治理登记 | capability_canonical_file_registry.yaml | creation_tokens 登记 |
| 独立裁定 | ruling_session_worktree_heartbeat.md | R4 交付物 |

**效果**: stale session 持有 held_files 的阻塞窗口从 1h（TTL）缩短到 90s（heartbeat 3×30s）

### 3.4 P1 异步化待立项项

| 改造点 | 当前 | 目标 |
|------|------|------|
| session_worktree_commit | 同步 git add + commit | 异步 fire-and-forget，返回 token |
| session_worktree_merge | 同步 git merge + cleanup | 异步 fire-and-forget，返回 token |
| 后台 worker | 无 | 串行处理 git 操作（消除 lock 争用） |
| 状态查询 | 无 | AI 通过 token 查询 commit/merge 状态 |

### 3.5 P2 阈值收紧（治本完成后）

| 阈值 | 过渡期（当前） | 稳态基线（治本后） |
|------|:---:|:---:|
| _EMERGENCY_24H_THRESHOLD | 20 | 5 |
| _ALLOW_OVERLAP_7D_THRESHOLD | 500 | 200 |

收紧条件：P1 异步化完成 + 30d 观察期 emergency/allow_overlap 自然下降到稳态基线以下。

---

## 4. R2 阈值过渡依据

| 阈值 | 原值 | 过渡值 | 依据 |
|------|:---:|:---:|------|
| emergency_commit 24h | 30 | 20 | 容忍单次 governance sprint <20，仍捕获日常滥用 >20 |
| allow_overlap 7d | 30 | 500 | 适配 100% AI 开发 7d 累积流量，治本前避免持续误报 |

过渡期阈值避免在治本未完成前持续误报，治本完成后收紧到稳态基线。

---

## 5. 风险与缓解

| 风险 | 缓解 |
|------|------|
| P1 异步化改造期间滥用持续 | R2 过渡阈值兜底，不阻断合法治理 commit |
| heartbeat daemon 残留 | daemon 检查 session 是否在 registry，注销后自动退出（#ARCH-HEARTBEAT-001 已处理） |
| 异步化后 token 管理复杂度 | token 持久化到 .runtime/sessions/<sid>/tokens.jsonl，AI 通过 session_id 查询 |
| 治本后阈值收紧过激 | 30d 观察期 + 动态基线（P3 长期目标） |

---

## 6. 验证标准

### 6.1 P1 heartbeat 验证（已完成）

- [x] heartbeat 文件在 session_worktree_start 后创建
- [x] _is_session_alive 对 pid=0 + heartbeat >90s 的 session 返回 False
- [x] AI 进程崩溃后，90s 内 held_files 释放
- [x] smoke test 全部 PASSED（10/10）
- [x] 独立裁定文档产出（#ARCH-HEARTBEAT-001）

### 6.2 P1 异步化验证（待立项）

- [ ] session_worktree_commit 返回 token，不阻塞
- [ ] session_worktree_merge 返回 token，不阻塞
- [ ] 后台 worker 串行处理，无 lock 争用
- [ ] AI 通过 token 查询状态，超时 <1s
- [ ] emergency_commit 24h 计数下降到 <5（稳态基线）

### 6.3 P2 阈值收紧验证（待治本完成）

- [ ] emergency_commit 24h 计数 30d 平均 <5
- [ ] allow_overlap 7d 计数 30d 平均 <200
- [ ] 无误报（合法治理 sprint 不被阻断）

---

## 7. 引用

- 立项条目: [architecture_issue_registry.yaml](../01_policies_and_standards/_registry/catalogs/architecture_issue_registry.yaml) `#ARCH-ASYNC-MERGE-RECONCILE-001`
- P1 heartbeat 落地裁定: [ruling_session_worktree_heartbeat.md](ruling_session_worktree_heartbeat.md)（#ARCH-HEARTBEAT-001）
- L1 根因分析引用: [ruling_gate_abuse_systemic_audit.md](ruling_gate_abuse_systemic_audit.md)（#ARCH-GATE-ABUSE-SYSTEMIC-AUDIT-001）
- 母裁定: [ruling_100pct_ai_governance_hardening.md](ruling_100pct_ai_governance_hardening.md)（R2 阈值调整 + P3 收尾复核）
- 滥用监控实现: [commit_gateway_abuse_monitor_reconciler.py](../../src/zephyr/governance/audit/commit_gateway_abuse_monitor_reconciler.py)
- session_worktree 实现: [session_worktree.py](../../src/zephyr/gov_enforcement/rule_bridge/session_worktree.py)
