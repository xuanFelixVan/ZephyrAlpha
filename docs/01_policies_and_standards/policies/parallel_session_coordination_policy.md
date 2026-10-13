---
module_id: POL-PARALLEL-SESSION-001
title: Parallel Session Coordination Policy / 并行 Session 协作策略
doc_type: policy
ttl: permanent
status: Active
version: 1.1.0
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
date: '2026-09-15'
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

**收班即清（Owner 2026-10-13 派工令 v2 段二，宪法 §2 第 9 条的细则落点）**：注销不是收尾的终点——
"收班留给下一班收"是死信、工棚车道、会话壳三重堆积的机制根。收班序列执行后，本班名下四类面
必须就地处置，不得遗留给下一班：

| 面 | 处置正门 | 判据 |
|---|---|---|
| worktree / `.aidrafts` 车道 | `session_worktree.py archive <车道绝对路径> --execute` | 死判与执行工具同源（`registry list_active`），活车道硬拒无逃生 |
| `.runtime/sessions/<sid>` 会话壳 | 同上 archive 尾部 `_prune_session_shell` | 只认精确单目录；空壳或仅剩心跳/PID 机制件才拆，有实质件保留并点名 |
| `.runtime/sessions/<sid>/staging/` | 有增量→promote 到 `docs/_working/`；无增量→随 TTL 清 | 成果未 promote 就删壳＝把未落地字节的第六态藏起来（在册红线：被清除面≠净收官） |
| 名下死信袋 | `commit_queue.py dead-archive --content-level --session <sid>` | 内容级四态判定＋机生台账行（qid/verdict/证据 sha），当日不隔夜 |

主区暂存区（git index）同批受规：无主 staged 残留一经发现即按 dev 现值复位并留存证——
车道/主区 index 都是多会话混合池，裸复位他人面属归属篡改，只可复位**确认无主**的件。

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

---

## 9. 主工作区施工纪律（#ARCH-311 删除事故教训，2026-09-15 增补）

背景：2026-09-14 docs/_working 多波删除事故（#ARCH-311）——并行会话的 safe-delete 沙箱
（CodeBuddy 内核 rm 包装 → Windows 回收站）被清理任务触发，单文件 git rm 意图被 vendor
级缺陷放大为脏文件集批量删除，未提交工作现场遭殃。三层防线已落地（B1 版本化 vault
ced73113 / B2 看门狗 auto-stage 护盾 0314d205 / 看门狗删除硬化 68d64742e3）。

纪律（对全体 AI 会话）：
1. **新建/重构 src/tests 代码 → 会话 worktree 正门**（session_worktree_start，物理隔离）。
   主工作区直改代码=把未提交工作暴露给一切共享区风险（本条为建议级；worktree 内 commit
   天然跳过搭便车三 gate，见 tracker #92）。
2. **docs/_working 文档可主区**——已有 B1 vault（每日 14 天版本快照）+ B2 护盾（untracked
   自动入 index）+ watchdog 删除硬化（两轮扫描内告警）三网兜底；产物每轮 git add 仍为
   铁律（staged 文件在本案删除潮中零损失）。
3. **任何"删除"一律走 ops_guard.guard_recycle**（统一回收站，永不物理删除）；未接
   guard 的删除工具/脚本禁止对 tracked 或他人未跟踪工作文件使用。
4. 发现有序恢复路径：新删除 → 先查 Windows 回收站（$I 元文件含原始路径，见
   .runtime/tmp/recycle_restore_report.json 的解析配方）→ 再查 B1 vault 昨日快照 →
   最后 git index/历史。


## 10. worktree 申请制（Owner 2026-09-15 采纳施工班建议，宪法 AGENTS.md §RULE-WORKTREE 同步修正）

背景：2026-09-14 单日四起同类事故（跨会话在途改写他人已提交文件 / docs 文件并发删除 /
热文件注册表四连环坏 / 在途 schema 重组批制造 63 条幻影悬空引用假警报）——全部属于
"共享工作树无隔离直改"事故类。业界共识（多智能体编码实践 2026）=每会话 worktree 物理隔离
为标准配置。宪法默认本就是隔离施工，本条把"降级直改"从自由裁量升级为**显式申请制**。

### 申请制三件

1. **登记原因（降级时必做）**：降级直改主区的会话，必须在当批 commit message 或任务
   登记中写明降级原因（如"worktree 合并冲突躲避/纯文档批/临时探针"）。现有 GitCommitGateway
   的 `[GW:<sid>:non-worktree]` 标记即自动留痕通道，无需新基建。
2. **自动计数（现有机制，一行命令）**：
   ```
   git log --format=%B | grep -c "non-worktree"
   ```
   按周执行（建议周六与 ZephyrAlpha_FactoryLaneC 同窗），按会话细查加
   `grep "GW:.*non-worktree"` 后按 sid 分组。计数=治理可见性指标，不设硬阈值。
3. **周审计**：计数结果纳入晨审/周六窗口巡检。连续两周环比上升 → 查明降级原因分布，
   属合并冲突躲避类的回炉 worktree 正门；属机制缺陷类的另立治理条目。

### 与既有条款的关系

- §9.1（主工作区施工纪律）由"建议级"升级为申请制（本条）；
- 宪法 AGENTS.md §0 冷启动 RULE-WORKTREE 与 §1 硬规则表第 3 条已同步修正（等长替换，
  总行数 139 不变）；
- 降级不是违规，未登记原因的降级才是；门禁对 non-worktree 提交的既有拦截面不变。


## 11. 活死判定与锁治理三通则（维护二班 T8 立法，2026-10-11；凭据=终清二期 00_ledger §五-23/§五-24/§五-25，总统统筹病根清偿令追认）

> 三通则同族：都是"账面判据与执行面不同源"引发的事故，故一并立、一并转播。
> 每一条都带实测凭据与可复跑判据，禁凭记忆引用。

### 通则一（§五-23）凡删除动作的最终判据必须与所用工具的守卫同源

尺上的"死"不算死。判定某一面可否被清理/归档/删除时，MUST 使用与执行工具内建守卫
同一把尺的同一份数据源；两套源读数不一致时，以执行工具守卫为准并停手。

- 实测凭据（st-finalclean2-20261010，2026-10-11 02:11 轮 3）：`liveness_verdict` 分片读数把
  6 面判成属主已死，而 `session_worktree.py archive` 的内建活跃硬拒守卫按
  `SessionRegistry.list_active` 判同一批属主**仍活跃**并硬拒绝——靠工具守卫才没出事；
  17 分钟内同一 14 面集合有 6 面翻转态别（纯因 90min 避让窗自然老化，非现实变化）。
- 可复跑口径：活性判定走 `list_active_readonly()`（`mutating=False`）——`list_active` 缺省
  会把判死写进接管台账，是"看一眼就立案"的放大器；巡检/取证一律用只读口。
- 适用范围：所有做活/死面判定的车道（清理班、归档班、巡检轮、接管班）。

### 通则二（§五-25）`lock_files.py cleanup` 摘锁前必须核活性三源

同一 sid 有两个写手时（主线程＋巡检轮/兄弟轮），任一方按宪法 §0.2 例行执行的
`cleanup` 会按心跳分片判死并摘走另一方**此刻仍活着**的 claim。心跳分片停更只证守护
进程死、不证会话死（在册铁律：判前任会话死须零写入三证齐）。

- 处方：摘锁前核三源，三者皆死才摘，任一活则跳过并留痕——
  ①`SessionRegistry.list_active`（与通则一同源）；
  ②该 sid 是否有其它在写面（同 sid 多面 fs 写 ≤90min）；
  ③该 claim 的最近持有心跳。
- 实测凭据（本班 2026-10-11 亲身复刻一次）：车道心跳守护 idle>1800s 自退
  （04:47:10 心跳末行留痕 `status=exited, idle_seconds=1803.1`），04:13 注册的条目随后被判死，
  提交被 `[SESSION-REQUIRED] session 未注册` 拦下；按 §0 正门重注册（pid=0）＋重拉守护即解
  （`.runtime/sessions/st-maint2-20261011/heartbeat.jsonl` 与 `list_active` 两面读数皆在盘，非推测）。
- 归属：`lock_files.py` 属全局工具，本通则只立法不代修他车道代码；执行面改造由锁治理车道承担。

### 通则三（§五-24）被清除面≠净收官

机械两 clause（终报进 dev ∧ 其车道零独有字节）判"净"**之前**必须先查**清除来源**
（archive/remove 记录）；清除来源≠属主自愿收口者一律单列"被迫收官"，禁与自然收官混计。

- 执行器已在册：`tools/t9_forced_close_audit.py`（终清二期 §九E 机生表），全集 54 面＝
  可计 9／不可计 42（被迫收官 35＋待追因 3＋面级已落终报而字节级仍未归 4）／零字节面 3；
  第三条尺实测**清除后又复活 5 面**＝"被清除面≠净收官"的物理证据。
- 首例＝`st-constland-20261010` 两面读法：面级自愿收官，字节级被迫清面（其 12:34:13 自建
  `T2-merge-transit` 袋被 `git stash clear` 抹掉，793 件字节至今只在袋内＝全仓唯一副本）⇒ 不得计入净收官。
- 账面纪律："已清 N 面"是**清除量**不是**收官量**，任何册上不得再以"某班已收官"口径叙述，
  只报"已清除＋其收官性质见 §九E"。
- 转正入工具面：本通则的执行器目前活在终清二班的 TTL 工棚（`.runtime/tmp/st-finalclean2-20261010/tools/`），
  随班清除即灭 ⇒ 候维护班把它永久化进 `scripts/governance/`（令卡 §二 T8 "执行器已有，转正入工具面"条）。
