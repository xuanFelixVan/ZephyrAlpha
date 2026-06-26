---
module_id: POL-PARALLEL-SESSION-001
title: Parallel Session Coordination Policy / 并行 Session 协作策略
doc_type: policy
ttl: permanent
status: active
version: 1.0.0
layer: cross_layer
owner: ZephyrAlpha-Owner
classification: confidential
language: zh
created_by: agent
valid_from: 2026-06-26
supersedes: null
superseded_by: null
placement_note: "定义多 AI session 并发时的协作契约。承接 P2-SES SessionRegistry/Handoff/ConflictDetector 落地能力，定义注册/注销、held_files 协议、handoff 格式、冲突升级路径。"
related_rationale: []
related_open_questions: []
tags:
  - parallel-session
  - coordination
  - session-registry
  - handoff
  - conflict-detection
summary: 定义 ZephyrAlpha 多 AI session 并发协作契约。session 注册/注销、held_files 协议、handoff 交接包格式、冲突升级路径、close-door 多 session 协调。是并行 session 漂移治理的战略层契约（病根第三层）。
date: '2026-06-26'
---

# Parallel Session Coordination Policy
# 并行 Session 协作策略

---

## 0. 读者指南

| 章节 | 内容 | 主要读者 |
|------|------|----------|
| §1 | 策略动机：为什么需要并行 session 协作 | 所有人 |
| §2 | session 注册/注销契约 | 实现者 |
| §3 | held_files 协议 | 实现者 |
| §4 | handoff 交接包格式 | 实现者 |
| §5 | 冲突升级路径 | 所有人 |
| §6 | close-door 多 session 协调 | 所有人 |

---

## 1. 策略动机

### 1.1 问题

ZephyrAlpha 是 1 人 + 100% AI 开发项目。当多个 AI session 并发工作时（如 20 并发扫描、40 并发数据库全景写入），会产生：

1. **同文件覆盖**：session A 和 session B 同时编辑同一文件 → 后写覆盖前写
2. **状态丢失**：session A 结束，其工作状态（TODO、失败、幻觉事件）不传给 session B
3. **死锁累积**：session A 持有的锁未释放，session B 永远抢不到
4. **漂移静默累积**：并行 session 各自引入漂移，无统一视图

### 1.2 本策略的解决

定义并行 session 协作契约：
- **注册/注销**：session 启动注册，结束注销（生命周期可见）
- **held_files 协议**：session 声明持有的文件（事前预警）
- **handoff 交接**：session 结束写交接包，下一 session 读取
- **冲突升级**：检测到冲突时的处理路径

---

## 2. session 注册/注销契约

### 2.1 注册（session 启动）

```python
from zephyr.security.access_control.session_concurrency import SessionRegistry

registry = SessionRegistry()
registry.register(
    session_id="session-20260626-001",
    pid=os.getpid(),
    held_files=[],  # 初始为空，随 acquire_files 增长
)
```

**注册时机**：`phase_manager.session_startup()` 中自动调用（P4-T2 接入）。

**TTL**：3600s（1 小时）。超时未心跳的 session 自动清理。

### 2.2 心跳

```python
registry.heartbeat(session_id)  # 更新 last_heartbeat
```

**心跳频率**：GitCommitGateway 每次 commit 时附带心跳（P4-T1 接入）。

### 2.3 注销（session 结束）

```python
registry.unregister(session_id)
```

**注销时机**：`phase_manager.session_shutdown()` 中自动调用（P4-T2 接入）。

**异常清理**：进程崩溃未注销 → TTL 过期后自动清理（`list_active()` 时触发）。

---

## 3. held_files 协议

### 3.1 声明

session 在 commit 前声明将修改的文件：

```python
from zephyr.security.access_control.session_concurrency import (
    SessionRegistry, SessionConflictDetector
)

registry = SessionRegistry()
detector = SessionConflictDetector(registry)

# 预声明将修改的文件
conflicts = detector.acquire_files(session_id, ["src/foo.py", "scripts/bar.py"])
if conflicts:
    # 有其他 session 持有相同文件 → warning（不阻断）
    for f, owner in conflicts.items():
        print(f"WARNING: {f} held by {owner}")
```

### 3.2 冲突语义

| 场景 | 行为 |
|------|------|
| 无冲突 | acquire 成功，held_files 记录 |
| 有冲突（其他 session 持有）| **仅 warning，不阻断**（GitCommitGateway 全局串行锁已保证 commit 安全）|
| 重复 acquire（自己已持有）| 幂等，无副作用 |

**关键**：held_files 协议是**事前预警**，不是**阻断机制**。阻断由 GitCommitGateway 全局串行锁负责（commit 串行化）。held_files 提供可见性，让 session 知道"有人在改这个文件"，从而协调工作顺序。

### 3.3 释放

session 结束或文件修改完成后释放：

```python
detector.release_files(session_id, ["src/foo.py"])
```

`registry.unregister()` 也会自动清空该 session 的所有 held_files。

---

## 4. handoff 交接包格式

### 4.1 写入（session 结束）

```python
from zephyr.security.access_control.session_concurrency import SessionHandoff

handoff = SessionHandoff()
handoff.write_handoff(
    session_id="session-20260626-001",
    summary="完成 P2-T2 manifest reconciler 迁移",
    pending_tasks=["P2-T3 all_export_reconciler 未开始"],
    warnings=["depgraph 有 340 ghost nodes 未清理"],
)
```

**写入路径**：`.runtime/handoffs/handoff_<session_id>.json`

**写入时机**：`phase_manager.session_shutdown()` 自动调用（P4-T2 接入）。

### 4.2 读取（下一 session 启动）

```python
package = handoff.read_handoff("session-20260626-001")
if package:
    print(package.summary)        # 上一 session 摘要
    print(package.pending_tasks)  # 未完成任务
    print(package.warnings)       # 警告
```

**读取时机**：`phase_manager.session_startup()` 自动调用（P4-T2 接入）。

### 4.3 交接包 schema

```json
{
  "session_id": "session-20260626-001",
  "timestamp": "2026-06-26T12:00:00Z",
  "summary": "完成 P2-T2 manifest reconciler 迁移",
  "pending_tasks": ["P2-T3 all_export_reconciler 未开始"],
  "warnings": ["depgraph 有 340 ghost nodes 未清理"]
}
```

---

## 5. 冲突升级路径

### 5.1 冲突检测

`SessionConflictDetector.check_file_conflict(file)` 检测某文件是否被其他 session 持有。

### 5.2 升级路径

| 冲突级别 | 检测 | 处理 |
|---------|------|------|
| **L1 预警** | `acquire_files` 返回 conflicts | warning log，session 自行决定是否等待 |
| **L2 串行化** | GitCommitGateway 全局锁 | commit 串行化，后到者等锁 |
| **L3 阻断** | `lock_files.py` 文件锁 | RULE-ZERO 锁协议，LOCKED 后禁止写 |

**关键**：并行 session 协作**不新增阻断层**，复用既有 GitCommitGateway 串行锁 + RULE-ZERO 文件锁。SessionRegistry/held_files 仅增加**可见性**。

---

## 6. close-door 多 session 协调

close-door 流程（`project_rules.md` Session 开关门）已新增 STEP 0：

```
0. 检查活跃 session:
   python -c "from zephyr.security.access_control.session_concurrency import SessionRegistry; r=SessionRegistry(); active=r.list_active(); assert len(active)<=1, f'{len(active)} active sessions — 关门前须协调'"
```

**语义**：
- 关门前若活跃 session > 1 → 断言失败，提示协调
- 关门 session 须先与其他活跃 session 沟通（handoff 交接 + 等待其完成或显式注销）
- 仅当活跃 session ≤ 1（自己）时方可关门

---

## 7. 与既有机制的关系

| 机制 | 职责 | 与本策略关系 |
|------|------|------------|
| GitCommitGateway 全局串行锁 | commit 串行化 | 阻断层（L2），本策略不替代 |
| RULE-ZERO lock_files.py | 文件锁 | 阻断层（L3），本策略不替代 |
| StagingArea（草稿模式） | ≥2 AI 并发提交 | 草稿提交层，本策略的 held_files 是其预警补充 |
| SessionRegistry（本策略）| session 注册/held_files | 预警层（L1），可见性 |
| SessionHandoff（本策略）| 跨 session 状态交接 | 状态连续性 |

**层次**：本策略是**最外层可见性**，不替代任何阻断机制。阻断由 GitCommitGateway + lock_files 负责。

---

## 8. 实现状态

| 组件 | 状态 | 接入点 |
|------|------|--------|
| SessionRegistry | ✅ 已落地（P2-SES）+ ✅ 已接入 commit path（P4-T1 commit 2a5ebe48）| GitCommitGateway.claim_files/release_files + session-aware stash 三级决策 |
| SessionHandoff | ✅ 已落地（P2-SES）+ ✅ 已接入 phase_manager.session_shutdown（P4-T2 commit 01a99f1f+da66d3d0）| gateway commit() finally 每次 commit 写 .runtime/handoffs/handoff_\<sid\>.json |
| SessionConflictDetector | ✅ 已落地（P2-SES）| P4-T1 用 claim_file 取代（更简洁，session 隔离 stash 内联实现） |
| close-door STEP 0 | ✅ 已落地（P1-T1）| project_rules.md（P4-T1 落地后 registry 有数据，检查真正有效） |
| 本策略文档 | ✅ 已落地（P1-T1）| 本文件 |
