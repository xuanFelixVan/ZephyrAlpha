---
module_id: ADR-0037
refines: [ADR-0011]  # ADR-0011 runtime-planes-orthogonal-view \u7684\u7ec6\u5316\u51b3\u7b56
title: Observer 发布订阅模式（零依赖事件总线）技术选型
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
tags: [observer, pub-sub, event-bus, phase-1, standard-library]
summary: Phase 1 事件层采用"纯标准库 Observer（threading.RLock + dict[EventType, set[Handler]]）"方案，不引入 blinker / PyDispatcher / Redis pub-sub / Kafka。公开 API subscribe/emit/unsubscribe；支持 5 类事件源；handler 异常隔离；once 订阅；线程安全。服务于 DeferredQueue（ADR-0036）与 ContextBudgetTracker（T-1-24）。

date: '2026-04-24'
ttl: permanent
---

# ADR-0037：Observer 发布订阅模式（零依赖事件总线）

## 1. 状态

- **当前状态**：`accepted`
- **拍板日期**：2026-04-24
- **决策者**：Claude Opus 4.7（终局裁决）
- **关联实现**：`scripts/infra/observer.py`（T-1-08，骨架已落地）

## 2. 背景（Context）

Phase 1 需要一个事件总线完成两件事：

1. 将"外部事件"（文件变化、任务完成、指标达标、手动触发、定时到点）分发给订阅者
2. 作为 `DeferredQueue`（ADR-0036）的 WAITING→READY 触发器与 `ContextBudgetTracker`（T-1-24）的 L1/L2/L3 阈值告警通道

约束：

- **标准库 only**：不新增依赖
- **线程安全**：Phase 1 暂无多进程，但 CLI 子命令与调度器可能在不同线程写入
- **异常隔离**：单个 handler 抛错不得影响其他 handler
- **可取消订阅**：支持 `once` 订阅（一次性 webhook 风格）
- **轻量**：代码 < 150 行，易审计

## 3. 考虑过的方案

### 方案 A：blinker（pypi）
- Flask 生态使用；API 成熟
- ❌ 新增依赖，违反零依赖原则
- ❌ signal 粒度与 EventType 枚举模型不对齐（blinker 是字符串信号名）

### 方案 B：PyDispatcher
- Django 风格
- ❌ 维护度下滑（最近更新多年前）
- ❌ 弱类型 signal 名

### 方案 C：asyncio.Event / asyncio.Queue
- 标准库
- ❌ 绑定 asyncio 事件循环；Phase 1 基础设施尚未切 async/await
- ❌ 多订阅者广播需要额外包装

### 方案 D：threading.Event + 自研派发
- 纯标准库
- ❌ Event 只支持 0/1 两态，不支持"订阅者集合"

### 方案 E：Redis pub/sub / Kafka / NATS
- 分布式事件流
- ❌ 需要外部服务进程（违反零运维）
- ❌ 单人项目量级远低于合理使用场景

### 方案 F：**手写 Observer（dict[EventType, set[Handler]] + threading.RLock）（本 ADR 选定）**

- **优点**
  - ✅ 100% 标准库
  - ✅ `@unique` Enum EventType 提供类型安全，防止 handler 订阅到错误字符串
  - ✅ `RLock` 允许 handler 在回调内再次调用 `subscribe/emit`（典型于 DeferredQueue 的级联唤醒）
  - ✅ `once` 订阅通过 `_once_flags: Set[Handler]` 实现一次性
  - ✅ 异常隔离：每个 handler 包 `try/except`，失败写入 `_error_log`
  - ✅ 代码 < 150 行（已在 `scripts/infra/observer.py` 验证）
- **缺点 / 权衡**
  - ⚠ 无持久化：订阅者信息只存内存，重启后清空 —— Phase 1 可接受，订阅关系由 DeferredQueue `resume()` + CLI 主函数重新注册
  - ⚠ 无回压：大量事件淹没时 handler 会串行执行 —— 性能测试不超标暂不处理
  - ⚠ 不支持主题通配（`file_event.docs.*`）：Phase 1 的 5 类事件足够扁平；需要时下沉到 handler 内部过滤
- **机构案例**：GTK+ signal、Qt QObject::connect（线程安全事件派发）、dbt manifest observer

## 4. 决策

**最终选择：方案 F —— dict[EventType, set[Handler]] + threading.RLock 纯标准库实现。**

### 4.1 公开 API（与当前 `scripts/infra/observer.py` 对齐）

```python
@unique
class EventType(str, Enum):
    FILE_EVENT = "file_event"
    TIME_EVENT = "time_event"
    TASK_EVENT = "task_event"
    MANUAL_EVENT = "manual_event"
    METRIC_EVENT = "metric_event"


EventHandler = Callable[[EventType, Dict[str, Any]], None]


class Observer:
    def subscribe(self, event_type: EventType, handler: EventHandler, *, once: bool = False) -> None: ...
    def unsubscribe(self, event_type: EventType, handler: EventHandler) -> None: ...
    def emit(self, event_type: EventType, payload: Optional[Dict[str, Any]] = None) -> int:
        """返回成功调用的 handler 数量。异常被捕获并记录到内部 _error_log。"""
```

### 4.2 5 类事件源（与 ADR-0036 同源）

- `FILE_EVENT` / `TIME_EVENT` / `TASK_EVENT` / `MANUAL_EVENT` / `METRIC_EVENT`

新增事件类型**必须先走 ADR 增补**，不得私自扩展枚举。

### 4.3 handler 契约

- handler 签名固定为 `(event_type: EventType, payload: dict[str, Any]) -> None`
- handler **必须纯函数 + 幂等**：同一事件多次投递不得产生副作用冲突
- handler **必须 ≤ 100 ms 返回**；长任务必须 offload 到 task_repo（通过 emit 回到 DeferredQueue）

### 4.4 线程与异常模型

- `subscribe/unsubscribe/emit` 内部用 `threading.RLock` 串行化
- `emit` 先快照（`list(self._subscribers[et])`），释放锁后调用 handlers，避免 handler 内回调触发重入死锁
- 每个 handler 包 try/except：异常被捕获并追加到 `_error_log: list[tuple[EventType, Exception]]`
- `once` handler 调用后立即 unsubscribe（哪怕抛错也移除）

## 5. 后果

### 5.1 正面
- 事件层代码 < 150 行，审计成本低
- 编译期（mypy --strict）可捕获"订阅了不存在的 EventType"
- 与 SQLite tasks 表无直接耦合：DeferredQueue 作为中介，保持分层纯净

### 5.2 负面 / 权衡
- 重启丢失订阅：**缓解**——所有生产订阅必须在应用入口统一注册（由 T-1-20 CLI 启动脚本承担）
- 同步执行：**缓解**——handler 耗时门禁 100 ms，超时被 metrics 捕获

### 5.3 重审触发条件

| # | 条件 | 动作 |
|---|------|------|
| 1 | EventType 枚举扩张到 > 15 项 | 考虑引入主题层次（dot-separated topic） |
| 2 | handler 平均耗时 > 100 ms 持续 | 引入 async/await 版本 ObserverAsync |
| 3 | 需要跨进程事件 | 评估 ZeroMQ / multiprocessing.Queue |

## 6. 落地动作

- [x] 本 ADR 落盘
- [x] `scripts/infra/observer.py` 骨架已存在（T-1-08 完成）
- [ ] T-1-11 单元测试：subscribe 幂等、emit 返回计数、handler 异常不中断其他 handler、once 正确一次性移除
- [ ] 与 ADR-0036 互引（DeferredQueue 订阅 5 类 EventType）

## 7. 参考

- 相关 ADR：
  - ADR-0030（SQLite 元数据层 —— `events` 表与本 ADR 不直接耦合，但 DeferredQueue 会把 emit 持久化进去）
  - ADR-0036（Deferred Queue —— 本 ADR 的头号消费者）
  - ADR-0040（Pydantic v2 输出契约 —— handler payload 可选 Pydantic 校验）
- 外部参考：
  - Gamma et al., *Design Patterns*, Observer pattern
  - PEP 435 — Adding an Enum type to the Python standard library

## 8. 修订记录

| 日期 | 版本 | 变更 |
|------|------|------|
| 2026-04-24 | 1.0.0 | 初版：选定手写 dict+RLock 零依赖方案；锁定 5 类 EventType；handler 契约与异常隔离规则；3 条重审触发 |
