---
ttl: task_bound
completes_when: 孤儿分诊战役终裁落地（chief 终审+处置执行）后本册随 30/31 号转归档
title: 孤儿分诊证据包：src.zephyr.trading（29 台）
owner: st-orphtriage-20261004
---

# 41 号·分诊证据包：src.zephyr.trading（29 台）

> 宇宙口径=裁定#481；数据真源=30_attribution_table.yaml（join checker 机生）；处置=证据班建议，终裁归 GLM-5.3 chief，退役执行归 Owner 门位。
>
> tier 分布：suspect_orphan=7，wired=19，wired_by_header=2，wired_dynamic=1；初判汇总：dispute=7，mount=22

## 逐台证据（四字段+初判）

| file | 干什么的 | last_commit（距今） | import 信号 | 初判建议 |
|---|---|---|---|---|
| `src/zephyr/trading/_extensions/__init__.py` | trading/_extensions | 2026-09-15（19天） | in=0/out=0·suspect_orphan | **dispute**（suspect_orphan 但 19 天内有 commit（活着但零线零引）；①mount→TDM（交易日夜循环） ②retire→Owner 门位） |
| `src/zephyr/trading/api/__init__.py` | trading/api | 2026-09-15（19天） | in=0/out=0·suspect_orphan | **dispute**（suspect_orphan 但 19 天内有 commit（活着但零线零引）；①mount→TDM（交易日夜循环） ②retire→Owner 门位） |
| `src/zephyr/trading/core/__init__.py` | trading/core | 2026-09-15（19天） | in=0/out=0·suspect_orphan | **dispute**（suspect_orphan 但 19 天内有 commit（活着但零线零引）；①mount→TDM（交易日夜循环） ②retire→Owner 门位） |
| `src/zephyr/trading/infrastructure/__init__.py` | trading/infrastructure | 2026-09-15（19天） | in=0/out=0·suspect_orphan | **dispute**（suspect_orphan 但 19 天内有 commit（活着但零线零引）；①mount→TDM（交易日夜循环） ②retire→Owner 门位） |
| `src/zephyr/trading/models/__init__.py` | trading/models | 2026-09-15（19天） | in=0/out=0·suspect_orphan | **dispute**（suspect_orphan 但 19 天内有 commit（活着但零线零引）；①mount→TDM（交易日夜循环） ②retire→Owner 门位） |
| `src/zephyr/trading/services/__init__.py` | trading/services | 2026-09-15（19天） | in=0/out=0·suspect_orphan | **dispute**（suspect_orphan 但 19 天内有 commit（活着但零线零引）；①mount→TDM（交易日夜循环） ②retire→Owner 门位） |
| `src/zephyr/trading/trading_contracts/market/__init__.py` | Auto-generated contracts package — market | 2026-09-15（19天） | in=0/out=0·suspect_orphan | **dispute**（suspect_orphan 但 19 天内有 commit（活着但零线零引）；①mount→TDM（交易日夜循环） ②retire→Owner 门位） |
| `src/zephyr/trading/admission_controller.py` | （无文档头，按文件名语义：admission_controller） | 2026-09-15（19天） | in=1/out=0·wired | **mount**→TDM（交易日夜循环）（活线在身未挂线） |
| `src/zephyr/trading/decision_map.py` | ── 枚举常量（schema v1.1 词表）────────────────────────────────────────────── | 2026-09-30（4天） | in=5/out=0·wired | **mount**→TDM（交易日夜循环）（活线在身未挂线） |
| `src/zephyr/trading/reference_data_manager.py` | ReferenceDataManager — 证券主数据管理器（MOD-TRADING-014）。 | 2026-09-15（19天） | in=0/out=0·wired_by_header | **mount**→TDM（交易日夜循环）（活线在身未挂线） |
| `src/zephyr/trading/trading_contracts/execution/__init__.py` | trading-contracts.execution — order execution domain contracts. | 2026-09-18（16天） | in=0/out=0·wired_by_header | **mount**→TDM（交易日夜循环）（活线在身未挂线） |
| `src/zephyr/trading/trading_contracts/execution/capital_allocation_result.py` | ==== BEGIN CODGEN:CTR-P1-003 ==== | 2026-09-15（19天） | in=6/out=0·wired | **mount**→TDM（交易日夜循环）（活线在身未挂线） |
| `src/zephyr/trading/trading_contracts/execution/execution_rejection_error.py` | ==== BEGIN CODGEN:CTR-ERR-005 ==== | 2026-09-15（19天） | in=2/out=0·wired | **mount**→TDM（交易日夜循环）（活线在身未挂线） |
| `src/zephyr/trading/trading_contracts/execution/execution_report.py` | Re-export wrapper: ExecutionReport 真源在 zephyr.shared.contracts.execution_report（CTR-P1-007 codegen） | 2026-09-15（19天） | in=2/out=0·wired | **mount**→TDM（交易日夜循环）（活线在身未挂线） |
| `src/zephyr/trading/trading_contracts/execution/fill.py` | Re-export wrapper: Fill 真源在 zephyr.shared.contracts.fill（CTR-005 codegen） | 2026-09-15（19天） | in=3/out=0·wired | **mount**→TDM（交易日夜循环）（活线在身未挂线） |
| `src/zephyr/trading/trading_contracts/execution/model_serving_request.py` | ==== BEGIN CODGEN:CTR-P1-004 ==== | 2026-09-15（19天） | in=4/out=0·wired | **mount**→TDM（交易日夜循环）（活线在身未挂线） |
| `src/zephyr/trading/trading_contracts/execution/order.py` | Re-export wrapper: Order 真源在 zephyr.shared.contracts.order（CTR-004 codegen） | 2026-09-15（19天） | in=6/out=0·wired | **mount**→TDM（交易日夜循环）（活线在身未挂线） |
| `src/zephyr/trading/trading_contracts/execution/position.py` | Re-export wrapper: PositionSnapshot 真源在 zephyr.shared.contracts.position（CTR-006 codegen） | 2026-09-15（19天） | in=3/out=0·wired | **mount**→TDM（交易日夜循环）（活线在身未挂线） |
| `src/zephyr/trading/trading_contracts/factories.py` | trading-contracts/factories.py — 交易域数据契约工厂方法 | 2026-09-15（19天） | in=1/out=0·wired | **mount**→TDM（交易日夜循环）（活线在身未挂线） |
| `src/zephyr/trading/trading_contracts/market/instrument.py` | （无文档头，按文件名语义：instrument） | 2026-09-15（19天） | in=2/out=0·wired | **mount**→TDM（交易日夜循环）（活线在身未挂线） |
| `src/zephyr/trading/trading_contracts/market/signal_degradation_warning.py` | ==== BEGIN CODGEN:CTR-ERR-003 ==== | 2026-09-19（15天） | in=5/out=0·wired | **mount**→TDM（交易日夜循环）（活线在身未挂线） |
| `src/zephyr/trading/trading_contracts/risk/__init__.py` | trading-contracts.risk — risk management domain contracts. | 2026-09-18（16天） | in=2/out=0·wired | **mount**→TDM（交易日夜循环）（活线在身未挂线） |
| `src/zephyr/trading/trading_contracts/risk/compliance_rule.py` | ==== BEGIN CODGEN:CTR-P1-012 ==== | 2026-09-15（19天） | in=0/out=0·wired_dynamic | **mount**→TDM（交易日夜循环）（活线在身未挂线） |
| `src/zephyr/trading/trading_contracts/risk/risk_dashboard_snapshot.py` | ==== BEGIN CODGEN:CTR-P1-008 ==== | 2026-09-15（19天） | in=4/out=0·wired | **mount**→TDM（交易日夜循环）（活线在身未挂线） |
| `src/zephyr/trading/trading_contracts/risk/risk_limit_violation_error.py` | 5.113.1 修复：删除 __slots__。Exception 基类未声明 __slots__，所有 Exception 子类 | 2026-09-15（19天） | in=3/out=0·wired | **mount**→TDM（交易日夜循环）（活线在身未挂线） |
| `src/zephyr/trading/trading_contracts/risk/risk_limits.py` | risk_limits — re-export shim for zephyr.shared.contracts.risk_limits（CTR-003 真源）。 | 2026-09-05（29天） | in=2/out=0·wired | **mount**→TDM（交易日夜循环）（活线在身未挂线） |
| `src/zephyr/trading/trading_contracts/risk/risk_metrics.py` | ==== BEGIN CODGEN:CTR-P1-011 ==== | 2026-09-15（19天） | in=4/out=0·wired | **mount**→TDM（交易日夜循环）（活线在身未挂线） |
| `src/zephyr/trading/trading_contracts/risk/risk_validator_protocol.py` | 5.145.12 修复：limits: Any -> RiskLimits（SSoT: cross_layer_contracts.yaml CTR-003） | 2026-09-15（19天） | in=2/out=0·wired | **mount**→TDM（交易日夜循环）（活线在身未挂线） |
| `src/zephyr/trading/trigger_registry.py` | TriggerRegistry — 扳机清单注册与仲裁 (MOD-TRIG-001) | 2026-08-17（48天） | in=1/out=0·wired | **mount**→TDM（交易日夜循环）（活线在身未挂线） |
