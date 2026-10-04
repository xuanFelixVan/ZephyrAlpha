---
ttl: task_bound
completes_when: 孤儿分诊战役终裁落地（chief 终审+处置执行）后本册随 30/31 号转归档
title: 孤儿分诊证据包：src.zephyr.signal_fundamental（24 台）
owner: st-orphtriage-20261004
---

# 41 号·分诊证据包：src.zephyr.signal_fundamental（24 台）

> 宇宙口径=裁定#481；数据真源=30_attribution_table.yaml（join checker 机生）；处置=证据班建议，终裁归 GLM-5.3 chief，退役执行归 Owner 门位。
>
> tier 分布：suspect_orphan=10，wired=9，wired_by_header=5；初判汇总：dispute=10，mount=14

## 逐台证据（四字段+初判）

| file | 干什么的 | last_commit（距今） | import 信号 | 初判建议 |
|---|---|---|---|---|
| `src/zephyr/signal_fundamental/_extensions/__init__.py` | signal/_extensions | 2026-09-16（18天） | in=0/out=0·suspect_orphan | **dispute**（suspect_orphan 但 18 天内有 commit（活着但零线零引）；①mount→FACTORY（原料端）/图12 备选 ②retire→Owner 门位） |
| `src/zephyr/signal_fundamental/api/__init__.py` | signal/api | 2026-09-16（18天） | in=0/out=0·suspect_orphan | **dispute**（suspect_orphan 但 18 天内有 commit（活着但零线零引）；①mount→FACTORY（原料端）/图12 备选 ②retire→Owner 门位） |
| `src/zephyr/signal_fundamental/core/__init__.py` | signal/core | 2026-09-16（18天） | in=0/out=0·suspect_orphan | **dispute**（suspect_orphan 但 18 天内有 commit（活着但零线零引）；①mount→FACTORY（原料端）/图12 备选 ②retire→Owner 门位） |
| `src/zephyr/signal_fundamental/gen/__init__.py` | Signal Generation sub-package | 2026-09-18（16天） | in=0/out=0·suspect_orphan | **dispute**（suspect_orphan 但 16 天内有 commit（活着但零线零引）；①mount→FACTORY（原料端）/图12 备选 ②retire→Owner 门位） |
| `src/zephyr/signal_fundamental/infrastructure/__init__.py` | signal/infrastructure | 2026-09-16（18天） | in=0/out=0·suspect_orphan | **dispute**（suspect_orphan 但 18 天内有 commit（活着但零线零引）；①mount→FACTORY（原料端）/图12 备选 ②retire→Owner 门位） |
| `src/zephyr/signal_fundamental/models/__init__.py` | signal_fundamental/models | 2026-09-16（18天） | in=0/out=0·suspect_orphan | **dispute**（suspect_orphan 但 18 天内有 commit（活着但零线零引）；①mount→FACTORY（原料端）/图12 备选 ②retire→Owner 门位） |
| `src/zephyr/signal_fundamental/services/__init__.py` | signal/services | 2026-09-16（18天） | in=0/out=0·suspect_orphan | **dispute**（suspect_orphan 但 18 天内有 commit（活着但零线零引）；①mount→FACTORY（原料端）/图12 备选 ②retire→Owner 门位） |
| `src/zephyr/signal_fundamental/strategy/__init__.py` | Signal Strategy sub-package | 2026-09-18（16天） | in=0/out=0·suspect_orphan | **dispute**（suspect_orphan 但 16 天内有 commit（活着但零线零引）；①mount→FACTORY（原料端）/图12 备选 ②retire→Owner 门位） |
| `src/zephyr/signal_fundamental/strategy/implementations/__init__.py` | Signal Strategy Concrete Implementations | 2026-09-18（16天） | in=0/out=0·suspect_orphan | **dispute**（suspect_orphan 但 16 天内有 commit（活着但零线零引）；①mount→FACTORY（原料端）/图12 备选 ②retire→Owner 门位） |
| `src/zephyr/signal_fundamental/synth/__init__.py` | Signal Synthesis sub-package | 2026-09-18（16天） | in=0/out=0·suspect_orphan | **dispute**（suspect_orphan 但 16 天内有 commit（活着但零线零引）；①mount→FACTORY（原料端）/图12 备选 ②retire→Owner 门位） |
| `src/zephyr/signal_fundamental/audit/__init__.py` | D-SIGNAL-06 信号审计日志子域 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→FACTORY（原料端）/图12 备选（活线在身未挂线） |
| `src/zephyr/signal_fundamental/audit/decision_snapshot.py` | D_FUNDAMENTAL_SIGNAL — 结构化决策快照（90 号 §22.5 C-030 溯源链最小实现） | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→FACTORY（原料端）/图12 备选（活线在身未挂线） |
| `src/zephyr/signal_fundamental/audit/signal_audit_logger.py` | D-SIGNAL-06 — 信号审计日志 | 2026-09-16（18天） | in=2/out=0·wired | **mount**→FACTORY（原料端）/图12 备选（活线在身未挂线） |
| `src/zephyr/signal_fundamental/audit/trace_context_store.py` | TraceContextStore — 信号追踪上下文存储（MOD-SIG-111）。 | 2026-09-16（18天） | in=1/out=0·wired | **mount**→FACTORY（原料端）/图12 备选（活线在身未挂线） |
| `src/zephyr/signal_fundamental/capital/capital_allocation_result.py` | D_FUNDAMENTAL_SIGNAL — CapitalAllocationResult re-export shim | 2026-09-16（18天） | in=1/out=0·wired | **mount**→FACTORY（原料端）/图12 备选（活线在身未挂线） |
| `src/zephyr/signal_fundamental/capital/default_capital_allocator.py` | D_SIGNAL — Default Capital Allocator（兼容 re-export shim） | 2026-09-16（18天） | in=1/out=0·wired | **mount**→FACTORY（原料端）/图12 备选（活线在身未挂线） |
| `src/zephyr/signal_fundamental/combiner/impl/__init__.py` | D_SIGNAL — Signal Combiner Concrete Implementations | 2026-09-18（16天） | in=0/out=0·wired_by_header | **mount**→FACTORY（原料端）/图12 备选（活线在身未挂线） |
| `src/zephyr/signal_fundamental/gen/aggregator_base.py` | D_SIGNAL — Signal Generation Layer | 2026-09-16（18天） | in=4/out=0·wired | **mount**→FACTORY（原料端）/图12 备选（活线在身未挂线） |
| `src/zephyr/signal_fundamental/gen/implementations/__init__.py` | D_SIGNAL — Signal Generation Concrete Implementations | 2026-09-18（16天） | in=0/out=0·wired_by_header | **mount**→FACTORY（原料端）/图12 备选（活线在身未挂线） |
| `src/zephyr/signal_fundamental/gen/implementations/default_signal_aggregator.py` | D_SIGNAL — Default Signal Aggregator | 2026-09-16（18天） | in=2/out=0·wired | **mount**→FACTORY（原料端）/图12 备选（活线在身未挂线） |
| `src/zephyr/signal_fundamental/sector_rotation_score_mapping.py` | 板块轮动 → SynthesizedSignal.score 映射（21 号 memo §3.1 v1.1.16，随 G06 批次落地）。 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→FACTORY（原料端）/图12 备选（活线在身未挂线） |
| `src/zephyr/signal_fundamental/strategy/capital_allocator.py` | D_FUNDAMENTAL_SIGNAL — Capital Allocator（兼容导出） | 2026-09-16（18天） | in=3/out=0·wired | **mount**→FACTORY（原料端）/图12 备选（活线在身未挂线） |
| `src/zephyr/signal_fundamental/strategy/implementations/default_capital_allocator.py` | D_SIGNAL — Default Capital Allocator | 2026-09-16（18天） | in=3/out=0·wired | **mount**→FACTORY（原料端）/图12 备选（活线在身未挂线） |
| `src/zephyr/signal_fundamental/synth/signal_synthesizer.py` | D_SIGNAL — Signal Synthesizer | 2026-09-16（18天） | in=3/out=0·wired | **mount**→FACTORY（原料端）/图12 备选（活线在身未挂线） |
