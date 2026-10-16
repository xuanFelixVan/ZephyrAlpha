---
ttl: task_bound
doc_type: mined_segment
parent_map: config/trading_day_cycle_map.yaml
segment: fig13-C (盘后段)
node_id: D13-30
miner_lane: mine_fullchain_20261015/daily_ops_pm
created: 2026-10-15
---

# SD13-30 盘后日K线层（当日主行情落库=下游全链就绪门）

## 1. 定义

交易日 16:30（APScheduler heavy 池槽 daily_kline，29 个有效挂载任务），日/周/月K线+复权+估值+
指标+ETF净值当日主行情落库。本格是本段唯一 ready_gate=true 的收盘就绪门（与开盘前就绪门
D13-09 同字不同轴，防合并），下游就绪门对象=D13-32（dloop 圈）、D13-33、D13-35。
图内决策问题："16:30 批次收口了吗？标的数看门铃响了吗？本图全链就绪门成立否？"
trigger_facts：task_runs 30 日窗 404 次（slot=daily_kline 任务级求和×29）——本段计数最实的格。

## 2. 六向台账

### 2.1 输入面
- 交易所日终批处理（gate 语义前置=推定完成，🌑-4 无外部真源，缺格事实记 gate 语义本身）。
- 兜底入边：D13-01（调度对账补跑）→ D13-30；fallback=D13-01 档期对账 + D13-35 行数视角补下载。
- invalidation：16:30 批次收口前 max(trade_date)=T-1 属正常，不作断供判据（骨架 §7 复跑注意 1）。

### 2.2 输出面
- 产物：日/周/月K线+复权+估值+指标+ETF净值落库（kline_daily/kline_index 面）+批后标的数看门铃。
- 就绪门出边（admission_edges 顶层在册）：
  - D13-30→D13-32：dloop data_readiness 腿以当日主行情为前置，缺则整圈 T-1 重放仍记 SUCCESS
    （fail-closed 唯二腿之一）。
  - D13-30→D13-35：17:00 补下载以"16:30 heavy 批已收口"为前置——实测该前置缺失⇒同表两实例
    并发写（簿 08 X-11；应然而非实然，缺格事实记在 D13-35 的 ready_gate_absent_zh）。
- consumers=count:22（code=20：src/zephyr/backtest/core/data_handler.py:373、
  src/zephyr/frontend/dashboard/api_server.py:1616、
  src/zephyr/governance/data_governance/miniqmt_provider.py:293、
  src/zephyr/infra_ops/config_effect_checker.py:107）。

### 2.3 SSOT 真源
- config/trading_day_cycle_map.yaml#D13-30（wired/built/✅，production，ready_gate=true）。
- 簿 08（X-11 并发写缺陷在案）；docs/_working/map_build/fig13_daycycle/08_盘后批次与当日回测.md。
- 槽契约：src/zephyr/data/config/schedule.yaml:79-82（cron "30 16 * * 0-4"，executor=heavy）。

### 2.4 代码模块
- module_id=MOD-L00-004；module_ref=src/zephyr/data/scheduler.py:2265（实存；当前行内容=
  跳闸冷却注释，锚漂移）；槽+看门铃 grep 复跑路径在 exec_evidence 在册。

### 2.5 门禁约束
- gap_refs benchmark:A1/C2：收盘就绪门与开盘就绪门同字不同轴（防两门合并成一格，已实证钉死于
  D13-09 注记）。
- admission_denied_zh 在册：未过门=下游拒绝就绪准入（两条拒准入出边已列）。
- casebooks=MEM-F13#时区与假绿。

### 2.6 自动化触发
- 机制=A_apscheduler；slot=daily_kline；machine_facts：effective_task_count=29、
  calendar_guarded=true、in_catchup_universe=true。
- trigger_facts：task_runs_30d=404（29 任务×30 日窗），evidence"交易日每日 1 批"。

## 3. 自审闸三态（逐向）

| 向 | 态 | 判据 |
|---|---|---|
| 输入面 | pass | 交易所日终批+双兜底（D13-01/D13-35）在图；404 次/30 日窗实跑证据 |
| 输出面 | pass | 两条 admission 出边+22 条 consumers 机生在册；就绪门语义完整 |
| SSOT 真源 | pass | 图节点+簿 08+骨架三层齐；就绪门字段（ready_gate/readiness_gate_for/admission_denied_zh）满配 |
| 代码模块 | warn | scheduler.py 实存但锚 :2265 行内容漂移（跳闸注释）；槽面锚 schedule.yaml:79 精确 |
| 门禁约束 | warn | X-11 已知真缺陷（收口未判→17:00 补下载并发写同表）；门体前置=交易所批处理推定（🌑-4） |
| 自动化触发 | pass | 29 挂载+calendar_guarded+catchup 在册+404 次节拍证据 |

## 4. 缺口与建议

- 不在本段 4 gap/11 未接线清单内（本段 wired 样板格）。
- 建议 1：X-11 缺陷收口——16:30 批次加"收口完成"标记（批次水位/实例互斥），17:00 补下载以该
  标记为前置闸，消除同表两实例并发写。
- 建议 2：gate 前置"交易所日终批推定完成"补一个最小可查面（标的数看门铃即现成载体），把 🌑-4
  从推定升为可查。
