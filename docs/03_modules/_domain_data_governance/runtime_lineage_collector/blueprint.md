---
blueprint_id: MOD-DATA_GOV-006
module_name: runtime_lineage_collector
domain: D_DATA_GOV
doc_type: blueprint
ttl: permanent
design_maturity: design
stability: evolving
safety_level: L
ai_autonomy: ai_modifiable
version: "0.1.0"
created: 2026-08-25
last_updated: 2026-08-25
owner: ZephyrAlpha-Owner
priority: P1
blueprint_level: module
domain_id: D_DATA_GOV
path: src/zephyr/data_governance/core/runtime_lineage_collector.py
granularity: file
---

# MOD-DATA_GOV-006 runtime_lineage_collector 蓝图（M8-S03 动态采集器）

> **module_id**: MOD-DATA_GOV-006 | **域**: D_DATA_GOV | **优先级**: P1
> **来源**: B10-02315（AUD-DRAFT-001-DIGEST P1 波 W-P1-18，CAND-DATGOV-003，A1 交易决策架构 §30.4.3）
> 代码：`src/zephyr/data_governance/core/runtime_lineage_collector.py`

## 0. 定位

M8-S03 动态采集器——运行时血缘动态采集（TSV 现状：缺失）。在数据接入/因子计算/
信号生成关键路径插桩 emit 血缘事件（轻量缓冲写，**fail-open 不阻塞交易主链路**），
盘后汇总入 lineage_tracker。

查重分工（W-P1-18 探查结论，均不复制）：

| 既有件 | module_id | 职责 | 与本模块边界 |
|---|---|---|---|
| lineage_tracker | MOD-DATA_GOV-002 | 血缘边注册/上下游查询/环检测/幂等 | 本模块只做**运行时事件缓冲与汇总**，入图复用其实现不重造 |
| lineage_parser | MOD-DATA_GOV-004 | 契约/注解静态解析（M8-S01）+ ingest 语义 | 静态面归 S01/S02；本模块为**在线事件面**；盘后汇总复用 S01 `ingest_into_tracker` 不重造 |
| static_lineage_analyzer | MOD-DATA_GOV-005 | 代码/SQL 静态分析（M8-S02），离线批跑 | S02=离线静态，S03=在线动态采集；输入面互补不重叠 |

不做什么：不建后台线程/异步框架（emit=内存缓冲 append，O(1) 无锁竞争面；
异步落盘/消息队列接线归运行时装配批）、不重造入图幂等语义（复用 002/004）、
不在 emit 路径抛异常（fail-open：畸形事件/缓冲溢出/sink 失败一律计数不抛出）。

## 1. 采集与汇总规则

- **事件** `RuntimeLineageEvent`（frozen）：source/target/transformation/run_id/
  emitted_at/context——source/target 空白为畸形事件。
- **emit**：缓冲 append；畸形事件丢弃计 dropped；缓冲满（max_buffer）丢弃新事件
  计 dropped；任何异常不抛出（fail-open 不阻塞主链路）。返回 bool 是否入缓冲。
- **flush(sink)**：排空缓冲交注入式 sink 回调（异步写归属 sink 实现）；
  sink 异常捕获记 flush_errors 且事件回滚入缓冲（不丢数据），不抛出。
- **盘后汇总** `aggregate_into_tracker(tracker)`：排空缓冲 → LineageEdge 转换
  → 复用 S01 `ingest_into_tracker`（批内去重/幂等 updated/环 rejected 不中断）。
- **stats**：emitted/dropped/flush_errors/buffered 计数如实可查。

## 2. 接口

```python
class RuntimeLineageError(ValueError)
@dataclass(frozen=True)
class RuntimeLineageEvent: source / target / transformation / run_id / emitted_at / context
@dataclass(frozen=True)
class CollectorStats: emitted / dropped / flush_errors / buffered
class RuntimeLineageCollector:
    __init__(*, max_buffer: int = 4096)
    emit(source, target, transformation="runtime", *, run_id="", emitted_at="", context=None) -> bool
    flush(sink: Callable[[list[RuntimeLineageEvent]], None]) -> int
    aggregate_into_tracker(tracker) -> LineageParseReport
    stats() -> CollectorStats
```

## 3. 依赖前置

- MOD-DATA_GOV-002 lineage_tracker（边注册/环检测/幂等唯一真源）。
- MOD-DATA_GOV-004 lineage_parser（ingest_into_tracker 入图语义复用）。

## 4. 验收标准

- 单测全绿（emit 正常入缓冲、畸形事件丢弃计数 fail-open、缓冲溢出丢弃新事件、
  flush 成功排空/sink 失败回滚计数、盘后汇总入图复用语义、端到端 emit→汇总→上下游
  查询）；相关域集成零回归。
