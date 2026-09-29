---
module_id: MOD-SELL-016
title: "S1 信号扫描编排器蓝图 — 事件触发单次扫描串S1族至S2-01路由口"
doc_type: blueprint
status: Active
version: "0.1.0"
ttl: permanent
design_maturity: design
layer: L03_sell_decision
layer_name: sell_decision
functional_domain: sell_decision
responsibility_domain: 
owner: ZephyrAlpha-Owner
created_by: agent
date: "2026-09-28"
last_updated: "2026-09-28"
priority: P0
blueprint_level: module
---

# MOD-SELL-016 | S1 Signal Scan Orchestrator 信号扫描编排器

> **域**: D_SELL_DECISION | **层**: L03 卖出决策 | **优先级**: P0 | **safety**: L | **ai_autonomy**: ai_modifiable
> **状态**: testing | **版本**: 0.1.0 | **SSoT**: depgraph MOD-SELL-016
> **真源案卷**: docs/_working/fullconnect_campaign/e_decision_chain/09_f45_s1_sell_signal.md §四 G45-1

## 1. 模块定位

G45-1 治缺口件——09_f45 案卷实证 S1 全族纯库挂机（`from zephyr.sell_decision` 包外零消费者，
离场实际靠人）。本模块把 TDM-X-S1 六节点串成**一次可被事件/既有槽位触发的扫描**：
providers 产信号 → S1-05 融合出 willingness → 紧迫度评分 → 结构化信封投递 S2-01 路由口
（f46 卷 S2-01 入口的消费契约）。无常驻线程，无 cron/sleep-loop（宪法 §9.3）。

## 2. 不变量 (INVARIANTS)

- **单次触发语义**: `scan_once` 纯编排无内部循环；节拍责任在槽位持有方。
- **共享单循环（D104）**: `triage_levels` 必须来自与 P1-02 position_triage 同一扫描循环，
  本模块只随信封留痕不二次判定——防两套 ticker。
- **paper 档硬默认**: 构造期禁 live（G45-1 处方先 paper 档）；live 须 `scan_once(allow_live=True)`
  单次显式解锁。
- **诚实空跑**: 零 provider/零信号 → `empty_run=True`，不伪造信号不假装消费。
- **显式跳过留痕**: 未接线节点（provider 未注册/触发扫描件未建）逐节点 `NodeTrace` 留痕。
- **验证态如实披露**: 18 节点台账（VAL-20260909-164042）全 `pending` 以常量携带，
  刻意不连业务库（宪法 §9.1），不升格不猜测。
- **分工红线（09_f45 勘误 3）**: KillSwitch 组合级熔断归 X-R1/F47 既有横切线；
  本模块 S1-06 侧只收单仓强清触发（黑天鹅/K≥3/主力弃庄）。
- **故障隔离**: 单 provider/触发源/sink 故障隔离为 trace，不阻断其余节点（同 collector 契约）。

## 3. S2-01 路由口契约

`S1RouteEnvelope` schema=`TDM-X-S2-01_INBOX/v1`：scan_id/node_id/symbol/mode/willingness/
urgency/execution_strategy/validation_state/reason/contributing_signal_count/created_at/payload
（triage 留痕）。`S2RouteSink` 协议三实现：InMemorySink（默认/影子）、FileOutboxSink
（paper 档 JSONL append-only，默认落 `data/runtime/s1_scan_outbox/`）、f46 卷 S2-01 执行器
（未来替换实现，编排器零改动）。

## 4. 就绪面（机生勿抄）

`readiness()` 六节点盘点：code_ready（module_ref 在盘，S1-06 真身在 src/zephyr/trading/）、
validation_state（全 pending）、wired（结构位常在/provider 已注册）。缺省构造=诚实空跑：
结构位（S1-01/S1-05）在但无信号源，判定族与绕过通道显式跳过。

## 5. 上下游

- **上游**: S1-01 collector providers；S1-02/03/04 node providers；S1-06 bypass triggers。
- **下游**: S2-01 路由口（f46 卷 TDM-X-S2-01 执行方式路由）。

## 6. 测试面

tests/sell_decision/test_s1_scan_orchestrator.py（18 用例）：档位硬锁/诚实空跑/就绪面披露/
显式跳过留痕/投递 mock+tmp_path 落盘/sink 故障隔离/绕过通道/共享 triage 留痕/报告可序列化。
