---
ttl: task_bound
completes_when: 孤儿分诊战役终裁落地（chief 终审+处置执行）后本册随 30/31 号转归档
title: 孤儿分诊证据包：src.zephyr.ex_core（22 台）
owner: st-orphtriage-20261004
---

# 41 号·分诊证据包：src.zephyr.ex_core（22 台）

> 宇宙口径=裁定#481；数据真源=30_attribution_table.yaml（join checker 机生）；处置=证据班建议，终裁归 GLM-5.3 chief，退役执行归 Owner 门位。
>
> tier 分布：suspect_orphan=4，wired=7，wired_by_header=11；初判汇总：dispute=4，mount=18

## 逐台证据（四字段+初判）

| file | 干什么的 | last_commit（距今） | import 信号 | 初判建议 |
|---|---|---|---|---|
| `src/zephyr/ex_core/_extensions/__init__.py` | ex_core/_extensions | 2026-09-15（19天） | in=0/out=0·suspect_orphan | **dispute**（suspect_orphan 但 19 天内有 commit（活着但零线零引）；①mount→图12（数据供给链） ②retire→Owner 门位） |
| `src/zephyr/ex_core/api/__init__.py` | ex_core/api | 2026-09-15（19天） | in=0/out=0·suspect_orphan | **dispute**（suspect_orphan 但 19 天内有 commit（活着但零线零引）；①mount→图12（数据供给链） ②retire→Owner 门位） |
| `src/zephyr/ex_core/core/__init__.py` | ex_core/core | 2026-09-15（19天） | in=0/out=0·suspect_orphan | **dispute**（suspect_orphan 但 19 天内有 commit（活着但零线零引）；①mount→图12（数据供给链） ②retire→Owner 门位） |
| `src/zephyr/ex_core/infrastructure/__init__.py` | ex_core/infrastructure | 2026-09-15（19天） | in=0/out=0·suspect_orphan | **dispute**（suspect_orphan 但 19 天内有 commit（活着但零线零引）；①mount→图12（数据供给链） ②retire→Owner 门位） |
| `src/zephyr/ex_core/audit_journal/__init__.py` | D_EXECUTION_CORE — Execution Audit Journal 包 | 2026-09-15（19天） | in=0/out=0·wired_by_header | **mount**→图12（数据供给链）（活线在身未挂线） |
| `src/zephyr/ex_core/audit_journal/auditor.py` | Execution Audit Logger — 执行审计记录器 (MOD-EX-003 / D-EX-CORE-15) | 2026-09-15（19天） | in=6/out=0·wired | **mount**→图12（数据供给链）（活线在身未挂线） |
| `src/zephyr/ex_core/bridge_instruction_kernel.py` | QMT 文件桥指令协议内核（TRD-A10 两缺陷的共用真源）。 | 2026-10-04（0天） | in=0/out=0·wired_by_header | **mount**→图12（数据供给链）（活线在身未挂线） |
| `src/zephyr/ex_core/broker_link_probe.py` | D_EX_CORE — miniQMT 下单链路探针（55 号 §3.2 缺口，随 40 号 P0 清单施工）。 | 2026-09-17（17天） | in=0/out=0·wired_by_header | **mount**→图12（数据供给链）（活线在身未挂线） |
| `src/zephyr/ex_core/daban_exit_decision.py` | 打板次日出场决策族（24_daban_strategy_detail §3.13 缺失#1/#7 施工）。 | 2026-09-17（17天） | in=1/out=0·wired | **mount**→图12（数据供给链）（活线在身未挂线） |
| `src/zephyr/ex_core/daban_instant_circuit_breaker.py` | 打板专用瞬时风控（24_daban_strategy_detail §3.13 缺失#2 施工，首批实盘前必做）。 | 2026-09-17（17天） | in=0/out=0·wired_by_header | **mount**→图12（数据供给链）（活线在身未挂线） |
| `src/zephyr/ex_core/daban_load_producer.py` | D_EXECUTION_CORE — daban 四引擎应用层负载日频批产生产者（T3⑧ / 挖矿 LUE-1 治本）。 | 2026-09-17（17天） | in=2/out=0·wired | **mount**→图12（数据供给链）（活线在身未挂线） |
| `src/zephyr/ex_core/daban_monitors.py` | 打板监控族（24_daban_strategy_detail §3.14#9 + §3.13#6 施工）。 | 2026-09-17（17天） | in=0/out=0·wired_by_header | **mount**→图12（数据供给链）（活线在身未挂线） |
| `src/zephyr/ex_core/daban_named_functions.py` | 打板 8 具名函数（24_daban_strategy_detail §3.1/§3.9/§3.11 施工，首批回测校准项）。 | 2026-09-17（17天） | in=0/out=0·wired_by_header | **mount**→图12（数据供给链）（活线在身未挂线） |
| `src/zephyr/ex_core/daban_signal_decision.py` | 打板信号前置门控 + 7 类交易动作决策（24_daban_strategy_detail §3.14#8 + §3.13#3 施工）。 | 2026-09-17（17天） | in=1/out=0·wired | **mount**→图12（数据供给链）（活线在身未挂线） |
| `src/zephyr/ex_core/execution_param_optimizer.py` | ExecutionParamOptimizer — 执行运营自优化器（MOD-EX-064）。 | 2026-09-15（19天） | in=0/out=0·wired_by_header | **mount**→图12（数据供给链）（活线在身未挂线） |
| `src/zephyr/ex_core/execution_strategy_selector.py` | Execution Strategy Selector — 执行策略选择器 (MOD-EX-062) | 2026-09-15（19天） | in=0/out=0·wired_by_header | **mount**→图12（数据供给链）（活线在身未挂线） |
| `src/zephyr/ex_core/miniqmt_channel_manager.py` | miniQMT 交易通道管理器 (MOD-EX-058) | 2026-09-29（5天） | in=0/out=0·wired_by_header | **mount**→图12（数据供给链）（活线在身未挂线） |
| `src/zephyr/ex_core/multi_contract_adapter.py` | D_EX_CORE — Multi-Contract Adapter (多契约生产适配器) | 2026-09-15（19天） | in=1/out=0·wired | **mount**→图12（数据供给链）（活线在身未挂线） |
| `src/zephyr/ex_core/performance_monitor.py` | 执行核心性能监控器（MOD-EX-036）——单机轻量实现。 | 2026-09-15（19天） | in=0/out=0·wired_by_header | **mount**→图12（数据供给链）（活线在身未挂线） |
| `src/zephyr/ex_core/post_close_pricing.py` | D_EX_CORE — 盘后固定价格交易通道（40 号 §6.1 gap 16，函数级 MVP）。 | 2026-09-17（17天） | in=0/out=0·wired_by_header | **mount**→图12（数据供给链）（活线在身未挂线） |
| `src/zephyr/ex_core/rules/base.py` | 交易规则包抽象接口（Trading Rule Pack，CAND-CRYPTO-006 / 94号 §4.3）。 | 2026-09-15（19天） | in=3/out=0·wired | **mount**→图12（数据供给链）（活线在身未挂线） |
| `src/zephyr/ex_core/saga_compensation_registry.py` | Saga Compensation Registry — 订单 Saga 补偿动作注册表 (MOD-EX-057-R1 / F53 夜战批) | 2026-09-30（4天） | in=2/out=0·wired | **mount**→图12（数据供给链）（活线在身未挂线） |
