---
ttl: task_bound
session: st-circ-a7-20260930
parent: 00_skeleton.md（总包）
scope: 全流通 P0 断链施工车道 A7（F82 / F27+F48 / F92）
---

# S5-FIX-A — A7 车道 P0 断链施工进度册

> 开工 2026-09-30 深夜，收笔 2026-10-01 00:5x。纪律：CapabilityLookup 已反查（order_daemon→
> ai_scheduling_l5 命中；pipeline_events/alloc_budget 无卡=代码考古定位）；reaper 在岗（23:55:51）；
> 锁=pipeline_events.py/test_pipeline_events.py/allocation_inputs.py/test_sleeve_provenance.py/
> test_sim_ledger_allocation_wiring.py/test_pf_alloc_event_wiring.py（均 st-circ-a7-20260930）。

## 逐项结果

### 1. F82 order_daemon 无生产 spawn 点（P0-1）——已治
- 断因核实（未被他会话治）：OrderDaemon 本体全在（单例锁/断点续读/毒丸，order_daemon.py:372
  process_once），全仓无任何生产调用；SchedulingJournal（.runtime/ai_scheduling/）不存在=零消费。
- 落地：pipeline_events.py 新增 `maybe_drain_order_daemon`（journal 非空才起守护跑一轮
  process_once，空=零成本跳过；异常 WARN 不反噬唤醒链；消费沿=数据任务完成事件，禁 cron 合规），
  `wire_data_scheduler` 装配点接入（scan_c1_c2_backlog 后）；唤醒链尾四棒 fail-isolation（见②）。
- 验证：单测 4 件（空跳过/非空起守护/异常不反噬/毒丸与失败任务跳过）+实弹探针——
  生产 journal 空→`journal_empty` 零成本；tmp 注入真胜者事件→`OrderDaemon.process_once`
  消费产出工单 `WO-20260930-001`（探针证据缺 criteria_ref→held_incomplete=必填机检按设计
  咬合），事件出队 pending_left=0。测试 43+31 全绿。

### 2. F27+F48 E8/C1 资金组装停摆（P0-2）——已治（三层根因）
- 簿载断因修正：调度触发器**在岗**（maybe_emit_pf_alloc_daily 09-15..09-28 marker 实证）；
  真根因三层：
  ①**分袋断链码虫**（主根）：a349ddc1fec（09-28 08:28，末次成功分配前 11 分钟）落了
    orchestrator 读侧 `base.sleeve_phases`（allocation_orchestrator.py:1058），其数据侧
    allocation_inputs.py 以"勿碰令"移出袋外——`BaseWeightTable.sleeve_phases` 字段+解析 API
    从未落地→此后每次分配 rc=1 AttributeError（E8/C1 全停）；
  ②唤醒链尾四棒（pf_alloc 发射/sim 日件发射/月度档/drain）裸奔无 fail-isolation，任一异常
    整段砍断只 log.debug 静默（09-30 08:39 实证：regime/judgment/warroom 三 marker 齐而尾段
    全灭）；
  ③并发赤字：发射链与活跃守护共用 journal，竞态读即炸（②的放大器）。
- 落地：①补齐丢失半截——`BaseWeightTable.sleeve_phases` 字段+`Pp001PlanDetail`+
  `load_pp001_plan_detail`+`build_base_weights` 相位贯通（按 test_sleeve_provenance.py 钉死
  契约，该测试件自带"落地后移除 skip 恢复运行"通道已启用，7 用例绿）；
  ②尾段四棒各自 try+ERROR 出声（单棒炸不连坐，下个唤醒点按幂等闸重评）；
  ③同批顺带治净两处 F48 域既有红测试（非本笔致、HEAD 实证同红）：
  test_sim_ledger_allocation_wiring 6 用例（09-22 R5 注册表卫兵落地未同步打桩，按卫兵
  docstring 指明的隔离通道补桩）+test_pf_alloc_event_wiring 1 用例（断言"带占位符模板 in
  已格式化串"恒假，改模块常量格式化等值）。两件 format 既有漂移一并治净防撞门。
- 补跑（处方"对 09-29/30 两日补跑"）：跑前探生产表锁态=system.processes 零活跃 alloc 查询；
  09-29=orchestrator 正门 `--date 2026-09-29`（三表 ch_committed，run=alloc-2026-09-29-dfb15b，
  STR-E-TIMING-001=392127.02/STR-VREV-025=692909.93）+补 handler 同款记号防次日同日双写；
  09-30=**事件链全路径**（emit pf_alloc_daily→drain→handler→子进程 orchestrator，验新码+验
  消费链）run=alloc-2026-09-30-79d73e（总盘 200 万，钱包 TIMING=392424.81/VREV=691917.32，
  regime r3@09-30 滞后 0）。CH 终态：alloc_budget_daily 09-28/29/30 各 2 行，max=09-30，
  shrinkage/change_log 同步；修复前毒丸残留已备份至 pending_events.jsonl.poisonbak-20261001-a7
  后清出（09-23 三件陈旧毒丸未动，属他会话前账）。

### 3. F92 原问题账本空转（P1-5）——已治
- 簿载断因修正：PG 三表全非空（meta_question=422/exam_result=337/audit=1779 行，snapshot
  row_count=283@09-22）——"entry_count=0"为过时读数；真断因=Windows 计划任务
  `ZephyrAlpha_MetaqAuditReconcile` 不存在（register ps1 真源+registry 条目 window=50 3 * * *
  均在，schtasks 查无此任务=调度载体脱锚）。
- 落地：跑 `scripts/register_metaq_audit_reconcile_task.ps1`（幂等 in-place 先例）→
  `[OK] registered` + `state=Ready next=2026-10-01 03:50`。
- 验证：实弹探针 `check_meta_question_audit_reconcile.py --days 1` → EXIT 0 平盘
  （逐日相等+双向差集空+零畸形行）；明晨 03:50 首跑落 tmp/metaq_audit_reconcile_report.log。

## 让位登记

- 无。两主目标文件开工时工作区干净（他会话无在途修改；pipeline_events 末笔=3992e4b024
  st-c9-final 已落地）。allocation_inputs 虽有 09-28 勿碰令（st-gpu-final 74a00a3605），
  该提交已落地收口（09-28 在库），令已失效；本笔补齐的正是该令拆散的另一半。

## 交接备注

- 09-30 21:04-21:09 crisis_gate_log 出现 trade_date=09-03/07-17 crisis 探针行（action=not_wired，
  疑他会话实弹探测），未吸收未处置。
- 明晨 03:50 起 metaq 对账任务自动跑；下一交易日 alloc 由唤醒链自动发射（发射链尾段已带
  fail-isolation+ERROR 出声，若再现停摆告警面当场可见）。
- 毒丸残留 bak：pending_events.jsonl.poisonbak-20261001-a7（本笔 1 件，09-29 已落地故清）。
