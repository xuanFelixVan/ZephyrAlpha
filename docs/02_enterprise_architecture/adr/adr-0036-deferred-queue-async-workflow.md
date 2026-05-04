---
module_id: ADR-0036
refines: [ADR-0011]  # ADR-0011 runtime-planes-orthogonal-view \u7684\u7ec6\u5316\u51b3\u7b56
title: 异步工作流 Deferred Queue（WAITING→READY 调度层）技术选型
doc_type: adr
status: active
version: 1.0.0
layer: L01
owner: ZephyrAlpha-Owner
classification: confidential
language: zh
created_by: agent
valid_from: 2026-04-24
superseded_by: null
supersedes: null
related_rationale: R-PHASE1-ASYNC, R-ZERO-DEP
related_open_questions: []
tags: [async, queue, deferred, scheduler, phase-1, sqlite]
summary: Phase 1 的 WAITING→READY 调度层采用"SQLite 表 + 轮询批量唤醒 + Observer 事件触发"的零依赖组合，不引入 Celery / RQ / APScheduler / Airflow 等外部队列。调度器与事件源通过 Observer（ADR-0037）解耦；状态持久化复用 ADR-0030 的 tasks 表与 events 表。100 个 WAITING 任务 → READY 转换必须 < 1s。

date: '2026-04-24'
ttl: permanent
---

# ADR-0036：Deferred Queue（WAITING→READY 调度层）

## 1. 状态

- **当前状态**：`accepted`
- **拍板日期**：2026-04-24
- **决策者**：Claude Opus 4.7（终局裁决） + Project Owner
- **关联实现**：`scripts/infra/deferred_queue.py`（T-1-09，已落地骨架）

## 2. 背景（Context）

Phase 1 任务状态机包含 10 个状态，其中 `WAITING` → `READY` 转换是异步触发的：

- `WAITING` 任务带 `waiting_for` 字段（如 `waiting_for="file_event:docs/X.md"`）
- 当 Observer 收到匹配事件时，`DeferredQueue` 必须批量把命中 `waiting_for` 的任务 UPDATE 为 `READY`
- Phase 1 性能硬门禁：**100 个 WAITING → READY 转换 < 1s**（execution-order §Phase 1 完成标准）

同时必须满足：

1. **零外部服务**：不引入 Redis / RabbitMQ / Celery broker
2. **崩溃安全**：进程 kill 后重启，WAITING 任务必须仍在
3. **可审计**：每次状态转换必须写 `events` 表（审计链路）
4. **与 tasks 表字段严格对齐**：ADR-0030 的 `tasks.status / waiting_for / ready_at` 列即真源

## 3. 考虑过的方案

### 方案 A：Celery + Redis broker
- 工业级、成熟生态
- ❌ 引入 Redis 服务 → 违反"零运维"
- ❌ 任务序列化为 pickle → 与 Pydantic 契约层重复
- ❌ 单人项目 5K 任务/天远低于 Celery 合理规模

### 方案 B：RQ（Redis Queue）
- 比 Celery 轻量
- ❌ 仍需 Redis
- ❌ 无法与 SQLite tasks 表共享事务（跨系统一致性难保证）

### 方案 C：APScheduler
- 纯 Python、支持 SQLAlchemy JobStore
- ❌ 依赖 SQLAlchemy ORM，与 T-1-04 `task_repo.py`（手写 `sqlite3`）架构冲突
- ❌ 核心功能是"定时"，事件驱动部分能力弱

### 方案 D：Airflow / Prefect / Dagster
- 功能完备、DAG 语义强
- ❌ 重型服务进程（webserver + scheduler）
- ❌ Phase 1 仅需 WAITING→READY 单点能力，引入 DAG 编排即过度工程化

### 方案 E：asyncio.Queue / queue.Queue（进程内）
- 标准库
- ❌ 进程重启后队列清空（违反"崩溃安全"）
- ❌ 状态无处持久化

### 方案 F：**SQLite 表 + Observer 事件 + 批量 UPDATE（本 ADR 选定）**

- **优点**
  - ✅ **零依赖**：完全标准库 + 已登记的 Observer（ADR-0037）
  - ✅ **崩溃安全**：WAITING 任务持久化在 `tasks` 表，重启后 `DeferredQueue.resume()` 扫描 `status='WAITING'` 即恢复
  - ✅ **原子事务**：`BEGIN IMMEDIATE; UPDATE tasks SET status='READY' WHERE ...; INSERT INTO events(...); COMMIT;` 单事务完成状态转换 + 审计
  - ✅ **批量唤醒 < 1s**：单条 UPDATE 多行性能远超 100 条/秒（SQLite 简单 UPDATE 典型 10 000+/s）
  - ✅ **与 Observer 正交**：事件层与调度层解耦；未来可替换 Observer 为 pub/sub 而不改调度逻辑
  - ✅ **可引用 Event Sourcing**：`events` 表即事件日志，天然支持审计重放
- **缺点 / 权衡**
  - ⚠ 无优先级队列：Phase 1 暂不需要；需要时在 `tasks` 表增加 `priority` 列即可
  - ⚠ 无跨机分布式：单人项目场景不适用；破坏假设时重审
  - ⚠ 轮询 vs 事件：本方案以 Observer 事件驱动为主，仅在启动 `resume()` 时做一次 `SELECT WHERE status='WAITING'` 补漏
- **参考实现**：GitHub Actions runner 本地任务队列、dbt CLI `run_results.json`、Home Assistant automation engine

## 4. 决策

**最终选择：方案 F —— SQLite `tasks`/`events` 表 + Observer 事件 + 批量 UPDATE**。

### 4.1 调度接口（ADR 基线；细节由 T-1-09 承接）

```python
class DeferredQueue:
    def __init__(self, bus: Observer, db_path: str) -> None: ...
    def watch(self, task_id: str, waiting_for: str, ready_at: datetime | None = None) -> None:
        """注册 WAITING 任务：tasks.status='WAITING', waiting_for, ready_at"""
    def on_event(self, event_type: EventType, payload: dict[str, Any]) -> int:
        """Observer 触发：批量 UPDATE tasks SET status='READY'
        WHERE status='WAITING'
          AND waiting_for = :matched_condition
          AND (ready_at IS NULL OR ready_at <= :now)
        RETURNING task_id;
        返回被唤醒数量，并为每个 task_id INSERT events 记录"""
    def pop_ready(self, limit: int = 10) -> list[Task]:
        """调度侧消费：SELECT ... WHERE status='READY' LIMIT :limit"""
    def resume(self) -> None:
        """启动时补漏扫描（断电/崩溃恢复）"""
```

### 4.2 5 类事件源（与 ADR-0037 共用）

| event_type | 载荷示例 | 典型场景 |
|-----------|---------|---------|
| `file_event` | `{"path": "docs/foo.md", "action": "modified"}` | T-0 文件落盘触发依赖它的任务 |
| `time_event` | `{"at": "2026-04-24T10:00:00Z"}` | 每日定时任务 |
| `task_event` | `{"task_id": "T-1-04", "new_status": "VERIFIED"}` | 下游依赖任务的父任务完成 |
| `manual_event` | `{"reason": "Owner approve"}` | Owner 手动唤醒 |
| `metric_event` | `{"metric": "dead_link_count", "value": 42, "op": "<="}` | 指标达标触发 |

匹配规则：`tasks.waiting_for` 写为 `"<event_type>:<selector>"`，其中 selector 为正则或字面量。例：`"file_event:docs/03_blueprints/**/*.md"`。

### 4.3 性能硬门禁

| 场景 | 要求 | 验证方式（T-1-11） |
|------|------|-------------------|
| 100 个 WAITING → READY 批量转换 | < 1s | `time.perf_counter()` 断言 |
| 单次 emit → handler 同步返回 | < 10 ms | 同上（不含数据库 commit） |
| resume() 扫描 1000 个 WAITING | < 200 ms | 同上 |

### 4.4 事务边界

所有 `on_event` 回调必须在单个 SQLite 事务内完成：

```sql
BEGIN IMMEDIATE;
UPDATE tasks SET status='READY', updated_at=? WHERE ...;
INSERT INTO events(event_type, payload, task_id, created_at, processed_at) VALUES (...);
COMMIT;
```

若 commit 失败 → ROLLBACK 并 emit `metric_event:deferred_queue.commit_failed`（供 T-1-19 metrics 监控）。

## 5. 后果

### 5.1 正面
- Phase 1 调度层实施预算从 5 人日压缩至 2 人日
- 崩溃安全天然具备，无需独立 WAL
- 与 `metrics_collector.py`（T-1-19）解耦：DeferredQueue 只发事件，不直接写 metrics

### 5.2 负面 / 权衡
- 高吞吐场景（> 10K WAITING）需要分表或改为异步批处理：**缓解**——通过 §5.3 触发条件监控
- 单 Writer 限制继承自 ADR-0030：本 ADR 不新增约束

### 5.3 重审触发条件

| # | 条件 | 动作 |
|---|------|------|
| 1 | 单次批量唤醒 > 1000 行且 < 1s 断言失败 | 改为异步批处理 + LIMIT 分页 |
| 2 | 多 AI agent 并发唤醒冲突率 > 5% | 引入队列锁或切换 PostgreSQL LISTEN/NOTIFY |
| 3 | 需要跨机器任务分发 | 评估 NATS / Redis Streams |

## 6. 落地动作

- [x] 本 ADR 落盘
- [x] `scripts/infra/observer.py`（T-1-08，已存在骨架）
- [x] `scripts/infra/deferred_queue.py`（T-1-09，已存在骨架，需与本 ADR 对齐：确认 `watch/on_event/pop_ready/resume` 四方法签名）
- [ ] T-1-11 单元测试补齐 100 个 WAITING→READY < 1s 性能断言
- [ ] 与 ADR-0037 交叉引用落盘

## 7. 参考

- 相关 ADR：
  - ADR-0030（SQLite 元数据层，本 ADR 的存储基础）
  - ADR-0037（Observer 模式，本 ADR 的事件源）
  - ADR-0040（Pydantic v2 输出契约，`Task` 模型必须包含 `waiting_for` / `ready_at` 列）
- 相关文档：
  - `模块候选池/开发流程/脚本任务知识库架构/02-任务系统架构.md` §6 任务状态机
  - `模块候选池/开发流程/vibe-coding-execution-order-v1.md` §Phase 1.2
- 外部参考：
  - SQLite docs: *Write-Ahead Logging* <https://www.sqlite.org/wal.html>
  - M. Kleppmann, *Designing Data-Intensive Applications*, Ch.11 Stream Processing

## 8. 修订记录

| 日期 | 版本 | 变更 |
|------|------|------|
| 2026-04-24 | 1.0.0 | 初版：选定 SQLite + Observer 零依赖方案；5 类事件源；100/秒性能门禁；3 条重审触发条件 |
