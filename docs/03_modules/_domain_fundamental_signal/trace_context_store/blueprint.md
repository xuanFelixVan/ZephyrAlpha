---
blueprint_id: MOD-SIG-111
module_name: trace_context_store
domain: D_FUNDAMENTAL_SIGNAL
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
domain_id: D_FUNDAMENTAL_SIGNAL
path: src/zephyr/signal_fundamental/audit/trace_context_store.py
granularity: file
---

# MOD-SIG-111 trace_context_store 蓝图（D-SIGNAL-100 信号追踪上下文存储）

> **module_id**: MOD-SIG-111 | **域**: D_FUNDAMENTAL_SIGNAL | **优先级**: P1
> **来源**: B2-05117（AUD-DRAFT-001-DIGEST P1 波 W-P1-25，CAND-FUNDAMEN-002，D-SIGNAL §1.1）
> 代码：`src/zephyr/signal_fundamental/audit/trace_context_store.py`

## 0. 定位

因子→信号→下单链路的**运行时实例级追踪上下文存储**：SQLite 追踪上下
文表（trace_id→因子批次/信号/订单 span 记录）+ 单笔信号**反查**因子批
次与原始行情引用 + 与 lineage_tracker 对接（结构级血缘边登记）。

查重分工（W-P1-25 铁律②探查）：

| 既有件 | module_id | 职责 | 与本模块边界 |
|---|---|---|---|
| FactorSignal.trace_context / SynthesizedSignal.trace_context | CTR-002/CTR-P1-015（codegen） | 契约**字段已嵌入**（TraceContext dataclass） | 字段在案但全仓仅 1 处 `trace_context=None` 填充——本件=字段的**持久化与反查面**，不改 codegen 契约 |
| signal_audit_logger | MOD-SIG-006 | WORM 审计事件（含 trace_id 字段，append-only 哈希链） | 审计=合规留痕（不可变事件流）；本件=运行时追踪表（可按 trace_id 反查链路），二者互补不重复 |
| lineage_tracker | MOD-DATA_GOV-002 | 表/因子/信号**结构级**血缘 DAG（add_edge+环检测） | 本件=**实例级**（某一笔信号）追踪；对接方式=把 trace 链路摘要登记为血缘边，不重建 DAG |
| ctr002_producer_validator | MOD-CON-002 | CTR-002 出厂前字段/PIT 验证 | 验证门禁，与追踪存储零交集 |
| record_lineage_tracker | MOD-DATA_GOV-008 | 记录级数据血缘（数据域） | 数据记录粒度；本件=信号链路粒度（因子批次→信号→订单） |

TSV 裁定原文："trace_id仅存在于审计事件结构，信号输出契约未嵌入追踪上
下文，因子→信号→下单链路血缘断链"——施工形态=SQLite 追踪上下文表 +
反查服务 + lineage 对接（DI 注入，不 import D_DATA_GOV）。

## 1. 规则（确定性；SQLite 落盘，注入路径）

- **Span 记录** TraceSpanRecord：trace_id/span_id/parent_span_id/layer
  （data|factor|signal|order）/ref_id（因子批次号|signal_id|order_id|
  行情批次号）/recorded_at（注入时钟）/detail。
- **写入**：`record_span(record)`——同 (trace_id, span_id) 幂等（重复
  写拒绝留痕）；layer 非法/ref_id 空 → Fail-Closed。
- **反查**：
  - `trace_chain(trace_id)` → 全链路 span 按 (recorded_at, span_id)
    确定性排序；
  - `signal_origin(signal_id)` → 该信号 span + 上游 factor 批次 span +
    上游 data 行情 span（沿 parent_span_id 回溯），支持"单笔信号反查
    因子值与原始行情引用"。
- **lineage 对接**：`sync_to_lineage(tracker_sink)`——sink 为注入回调
  （契约同 lineage_tracker.add_edge(source, target, transformation)），
  把 factor_batch→signal→order 摘要登记为结构级边；sink 异常不阻断
  本地写入（log + 计数）。
- SQLite 表 `trace_span`（trace_id, span_id, parent_span_id, layer,
  ref_id, recorded_at, detail，主键 (trace_id, span_id)）；`:memory:`
  默认（单测），文件路径注入；WAL 不开（单写者语义）。

## 2. 接口

```python
class TraceLayer(str, Enum): DATA/FACTOR/SIGNAL/ORDER
@dataclass(frozen=True) class TraceSpanRecord: trace_id/span_id/parent_span_id/layer/ref_id/recorded_at/detail
@dataclass(frozen=True) class SignalOrigin: signal_span/factor_spans/data_spans/order_spans

class TraceContextStore:
    __init__(db_path=":memory:", *, clock=None, lineage_sink=None)
    record_span(record: TraceSpanRecord) -> bool
    trace_chain(trace_id: str) -> list[TraceSpanRecord]
    signal_origin(signal_id: str) -> SignalOrigin
    sync_to_lineage(trace_id: str) -> int  # 登记边数
TraceContextStoreError(ZephyrBaseError)  # 占位 ZA-SIG-UNREGISTERED-TRACE-STORE（纪律⑦）
```

## 3. 依赖

- 设计边：`lineage_tracker`（node 10624719，对接语义）、
  `signal_audit_logger`（node 10627368，审计 vs 追踪分工）。
- 运行时装配（非本件）：FactorSignal/SynthesizedSignal 生产侧填充
  trace_context 后写本件；订单层 span 由 EX_CORE 装配批写入。

## 4. 测试

`tests/signal_fundamental/audit/test_trace_context_store.py`（[TTL] permanent）。
