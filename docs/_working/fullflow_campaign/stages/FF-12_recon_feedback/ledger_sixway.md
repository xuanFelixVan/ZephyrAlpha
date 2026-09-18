---
ttl: task_bound
completes_when: FF-11→FF-12→FF-02/06 闭环四件（台账读者/事件扇出/日终调度/运行时观测）全部出实测证据或转黄-门位
---

# FF-12 对账与反馈 · 六向台账（车道 st-ff-wirerecon-20260918 首轮）

> 环节定义（`skeleton/00_stage_skeleton.md:35`）：FF-12 上游 = FF-04/FF-09/**FF-11**，
> 下游 = **FF-02/FF-03/FF-06（闭环回流）**。本表只记本车道断点簇：BRK-020 / BRK-016 / BRK-017 / BRK-059。
> 所有格子均为**本车道亲跑**实测（命令见 `../lanes/wirerecon_BRK020_gap.md` §1），非引用他人结论。
> 表述纪律（裁定#325）：不写"全绿"，只写"本轮检出 N 件，绿 X/黄 Y/红 Z，绿件能红证据见附件"。

## 1. 六向台账表

| 子模块 | ①入口有料 | ②转化能跑 | ③出口有货 | ④下游能取 | ⑤哨兵在岗 | ⑥失败会响 | 三态 |
|---|---|---|---|---|---|---|---|
| `ex_core/execution_report_producer`（BRK-020，z-land 独占·本车道仅核验） | 终态订单源=柜台镜像：`E:\qmt_bridge_sim\Stock\Account.csv` mtime 17:57、`Order.csv` 336084B；同步线程 `observed=95` | `wire_e4_check.py` 真发单 rc=1（P3 盘后无回执，P4 撤单收敛 CANCELLED）；单元面 23 passed | **`c1_market.execution_report` FINAL count 0→1**；行=`f216058c… 510300.SH BUY 100/0 comm=0 qmt_sim NONE`；非 FINAL 亦 1（幂等成立） | **零读者**：`grep -rn execution_report src/zephyr/reporting` 仅注释命中，无表读取；事件扇出点不存在（`shared/event_bus.py:58` EventType 无执行域） | 无阈值行（表未进 `data_supply_sentinel.yaml`） | 旁路已写：`_build` 三处 Fail-Closed 计数（`commission_blocked`/`validation_failed`/`build_failed`）+ 超 3 轮转 abandoned 打 error；**但未在真链上注入验证** | **黄** |
| `position/position_reconciler`（BRK-016，本车道已改） | 事件载荷需调用方供两侧持仓；本轮无事件源（=④的上游断口） | `pytest tests/rollback/test_rollback_position_reconciler.py` → **34 passed**（旧 20 + 新 11 + 边界 3） | 结果 dict 落 `status/match/diffs/rule_id/escalate` + 计数 `unavailable_count/mismatch_count`；**无持久化 sink**（待 G6） | 零程序消费方（GOMAP `wiring=suspect_orphan` 现状未变，须 z-land 扇出后由装配批挂） | 无 | **已证明能红**：变异 `.get(k,{})` 还原 → 4 failed/30 passed rc=1；`escalation_sink` 抛异常被 Fail-Loud 兜住（新增测试钉） | **黄**（④⑤待扇出；⑥已证） |
| `orchestrator/execution/reconciliation_loop`（BRK-017，本车道已改） | n/a（它不吃成交数据） | `pytest tests/trading/test_reconciliation_loop.py` → **24 passed** | `ReconcileResult(invariants, all_ok, unobserved)` 内存态，无落盘 | 零消费方；**且普查误归因**：5 项不变量是编排器自完整性（契约校验和/熔断态/CBAC 矩阵/任务卡态机/DLQ），与 FF-11→FF-12 无关 | 无 | **已证明能红**：变异 `ok=False→True` → 2 failed/22 passed rc=1；恒真门（不传 states 全绿）已废除 | **黄**（作用域改判；建议从 GOMAP `L5_selfheal` 摘出） |
| depgraph `dataflow_runs`/`dataflow_datasets_metadata`/`dataflow_jobs_metadata`（BRK-059） | 上游=作业运行实例，**写入器不存在**：全仓 `grep "INSERT INTO dataflow_runs\|record_run"` 命中 3 件均与本表无关 | 未跑（无入口） | `dataflow_runs` **0 行**（普查 `panorama_registry.md` §健康度，本轮未直连 PG 复核） | 读者=`generate_panorama_registry.py`（只读报 0） | 无 | 未测 | **红→未启动**（本车道预算让位 020/016/017） |

**本轮本簇检出 4 件：绿 0 / 黄 3 / 红 1。**

## 2. 关键翻转（相对断点普查）

1. **BRK-020 从"红"翻"黄"**：`build_execution_report` 已不再是零调用
   （`execution_report_producer.py:70` import、`:324` 调用；生产端真落行）。
   留在黄的原因是 **④下游能取** 与 **⑤哨兵在岗**，而非"没人生产"。
   普查文本（`01_break_census.md:54`）在 z-land 落地后须改写。
2. **BRK-017 判为误归因**：不是"对账循环没接成交"，而是"治理自审循环被当成了成交对账循环"。
   按其字面接线会造出**假闭环**（把成交喂给只认 5 个治理键的循环）。
3. **BRK-016 病形改判**：真问题不是"一个孤儿模块"，而是 **对账域六件实现并存、六件全零程序消费**
   （明细见 `../lanes/wirerecon_BRK020_gap.md` §3）。且原实现的"production"名不副实：
   它在输入断供时**静默判平**（`match=True`），属普查 §J 第 1 条"恒真门禁未系统扫"的实例——
   本车道已把这一支加严为 Fail-Closed。

## 3. 打通闭环还差的 4 刀（按依赖序，非 Owner 门位）

| # | 缺什么 | 落在谁的独占文件 | 精确处方 |
|---|---|---|---|
| 1 | G1 四件套原子落地（untracked producer + unstaged broker 方法） | z-land（`ex_core/**`） | `gap.md` §2 G1（含落地后两条核验命令） |
| 2 | G4 未成交行 `slippage_bps=-10000` 修正 | z-land（`ex_core/execution_report.py:54`） | `gap.md` §2 G4 建议 A + 测试钉 |
| 3 | G6 ExecutionReport 事件扇出（producer `listeners` → `PositionReconciler.handle_execution_report` → escalation_sink） | z-land（producer/assembly）+ 运行时装配批 | `gap.md` §2 G6 |
| 4 | 日终对账调度（`recon_runner.run_daily_reconciliation` / `eod_reconciliation` 零消费者，需 15:30 档期） | **residG**（`tasks.yaml` 单一写者，本车道不代写） | 片段待 #1 落地后另批提交；须同时补 `execution_report` 的 `data_supply_sentinel.yaml` 阈值行（⑤） |

**Owner 门位**：本簇 0 项（成交台账/对账器/调度均不触实盘、注册表净删、flag 翻转、资金破坏性操作）。
FILLED 腿待 09-19 交易窗口补证，属时间窗非门位。

## 4. 附件（能红证据）

- 变异两轮（按字节还原 + sha256 校验）：`gap.md` §4 表末列，rc=1 实录。
- 真实落行 SQL 取证：`gap.md` §1 E3/E4。
- 驱动器与 JSON 结果：`.runtime/tmp/st-ff-wirerecon-20260918/{wire_e4_check.py, live_run1.log, wire_direct_result.json, smoke_run1.json}`。
- 测试计数：`tests/rollback/test_rollback_position_reconciler.py` 34 / `tests/trading/test_reconciliation_loop.py` 24 /
  `tests/ex_core/test_execution_report_producer.py` 23 / `tests/e/test_e_position_reconciler.py` 7 = 88 passed。
