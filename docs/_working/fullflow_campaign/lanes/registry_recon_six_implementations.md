---
ttl: task_bound
completes_when: 对账域唯一权威入口由 Max 裁定并落地（合并批完成）后本表归档
---

# 对账域六件（实测七件）差异对照表 · 交 Max 直接开工用

> 车道 `st-ff-registry-20260918`（注册表一致性车道）按 R-015 出：**不合并、不删**，
> 只出"谁该是唯一权威入口"的**建议 + 论证**。合并定权威触注册表净删 = Owner 门位，归 Max。
> 全部事实为 2026-09-18 本机实测（读文件头 + `find tests` + depgraph 查询），非转抄普查。

## 0. 先纠一处普查口径（R-013 要求的语义核对）

R-015 与普查记"六件并存"。**实测是七件**（`src/zephyr/trading/` 下不止 `recon_runner` +
`three_way_reconciliation`，还有 `settlement_reconciliation.py`，MOD-TRADING-003，
`maturity=production`，含独立测试）。本表按七件给，避免 Max 按"六件"清单开工漏掉一件。

`find tests -name "test_*<件名>*.py"` 实测**七件全部有测试**——"零程序消费"指的是
**src/ 下无生产消费方**（ORPHAN-MODULE 门口径：`scripts/` 的 import 不算引用），
不是"没测试"。这一点若被误读，会把"缺接线"错判成"缺实现"。

## 1. 逐件档案

| # | 路径 | 它实际在算什么 | 输入来源 | 输出去向 | 测试 | 头注释自陈 CONSUMERS |
|---|---|---|---|---|---|---|
| R1 | `src/zephyr/position/position_reconciler.py`（207 行，MOD-INF-022，D_POSITION，production） | **事件驱动的持仓漂移纠偏**：收成交/终态事件 → 比对本地持仓与外部持仓 → 产 DriftItem | 方法入口 `handle_execution_report`（事件形参），无 DB 直连 | 返回结果对象；**无落库、无告警下游** | `tests/rollback/test_rollback_position_reconciler.py` | "无生产消费方（BRK-016 在册断点；事件入口=handle_execution_report，待 ex_core 终态事件扇出后由装配批挂接）" |
| R2 | `src/zephyr/ex_core/position_reconciler.py`（218 行，MOD-EX-056，D_EX_CORE，production） | **同源持仓体检的另一实现**：`PositionSource` 抽象 + `ReconcileResult`/`DriftItem` 契约 | `zephyr.shared.contracts.position`；注入式 `PositionSource` | `ReconcileResult` | `tests/ex_core/test_position_reconciler.py` | `zephyr.ex_core.trading_session`、`zephyr.governance.adapters.simulation_broker`（**有声称消费方**，与"零消费"矛盾，见 §3） |
| R3 | `src/zephyr/ex_core/eod_reconciliation.py`（254 行，MOD-L06-003，D_EX_CORE，evolving） | **日终结算三合一对账**：委托 R2 做持仓腿 + order_manager 做委托腿 + position_tracker 做现金腿 | `ex_core.order_manager` / `position_reconciler` / `position_tracker.tracker` | `EodReconcileResult`（含 `EodReconciliationError` 失败契约） | `tests/ex_core/test_eod_reconciliation.py` | "运行时装配批(盘后 15:30 任务链/日终调度接线)"——**等待接线** |
| R4 | `src/zephyr/trading/recon_runner.py`（480 行，最大件，MOD-TRADING-007，D_TRADING，production） | **日频编排器**：`run_daily_reconciliation()` 串起券商源→L1/L3 漂移分类→差异落库→归因；是唯一的"跑批入口"形 | `ex_core.adapters.miniqmt_broker`、`ex_core.position_reconciler`(=R2)、`trading.settlement_reconciliation`(=R6)、`backtest.io.result_repository`、`risk.core.daily_auditor` | `_persist_differences` → **落库**；`ReconDailyResult` | `tests/trading/test_recon_runner.py` | "57号文日循环SOP（人工/后续调度触发）" |
| R5 | `src/zephyr/trading/three_way_reconciliation.py`（441 行，MOD-TRADING-013，D_TRADING，production） | **交易流↔持仓流↔现金流三向核对 + 异常分类与跟进台账**（AnomalyClass/FollowUpStatus） | 内部自带 `TradeFlow/PositionFlow/CashFlow` 数据结构（不 import 其他件） | `ReconReport` | `tests/trading/test_three_way_reconciliation.py` | "运行时装配批（盘后三向对账调度 / 告警路由接线 / 未匹配台账跟进工作台）" |
| R6 | `src/zephyr/trading/settlement_reconciliation.py`（431 行，MOD-TRADING-003，D_TRADING，production） | **清算对账**：券商清算记录 vs 本地 fill 契约的 DriftType 判定与 `SettlementReport` | `zephyr.shared.contracts.fill`、`BrokerSettlementRecord` | `SettlementReport`（被 R4 import 复用） | `tests/trading/test_settlement_reconciliation.py` | `zephyr.reporting`、`zephyr.governance` |
| R7 | `src/zephyr/orchestrator/execution/reconciliation_loop.py`（122 行，MOD-INF-039，D_ORCHESTRATOR，production） | **不是成交对账**：调和编排器自完整性 5 不变量（契约校验和/熔断态/CBAC 矩阵/任务卡态机/DLQ） | `zephyr.shared.utils.time_utils`（仅时间）；输入是编排器自身状态 | `ReconcileResult`（不变量违例表） | `tests/trading/test_reconciliation_loop.py` | "无生产消费方（BRK-017 在册断点；本件调和的是**编排器自身完整性**5 项不变量，非 FF-11→FF-12 成交对账链）" |

## 2. 语义差异（这七件不是同一件事的七次复制）

按"对的是什么账"分三层，**不是可随意合并的重复**：

- **持仓层（同一概念的两种实现）**：R1（事件驱动、无落库）↔ R2（注入式 `PositionSource`、被 R3/R4 复用）。
  二者**是真正的重复**：都在算"本地持仓 vs 外部持仓的 DriftItem"，且 R1 自己的头注释就承认
  它的入口 `handle_execution_report` 等待 R2 侧的事件扇出。
- **日终编排层**：R3（ex_core 内三腿合流）↔ R4（trading 侧跑批入口，且**已在 import R2 与 R6**）。
  R4 是唯一带"落库 + 调度语义"的件；R3 是它的 ex_core 侧近亲。
- **账目维度层**：R5（三向核对 + 跟进台账）↔ R6（清算记录核对）。R4 用了 R6，R5 谁都没用。
- **异物**：R7 与对账无关（R-013 已裁普查该条为误归因，本表实测复核=成立）。

## 3. 建议与论证（供 Max 裁）

**建议：唯一权威入口 = R4 `trading/recon_runner.py::run_daily_reconciliation`（日终批），
盘中事件入口 = R1 `position/position_reconciler.py::handle_execution_report`，
R2/R3/R5/R6 降为其组件、R7 摘出对账域。**

论证（五条，按可核证据排序）：

1. **只有 R4 有"跑批"语义**：480 行中唯一暴露 `run_daily_reconciliation()` 顶层函数并做
   `_persist_differences` 落库；其余六件全部返回内存对象、零落库（实测：仅 R4 有 `_persist_*` 函数）。
   验收规范 §1 的第③向"出口有货"要求产出**落进声明的 sink**——只有 R4 满足。
2. **R4 已经在复用别人，说明它是收敛点而不是竞争者**：它 import R2 + R6（实测 import 清单）。
   把权威定在"已经吸收他人的一方"，合并动作最小（净删面最小），风险最低。
3. **R2 的头注释声称有消费方（`ex_core.trading_session` / `governance.adapters.simulation_broker`），
   与普查"全部零程序消费"矛盾**——需 Max 先实测复核这两处 import 是否真在 src/ 生效
   （`git grep -n "position_reconciler" src`）。若真在，则普查 R-015 的"六件全部零消费"要改判为
   "五件零消费 + 一件有消费"；这直接改变合并方向（有消费方的一方不能先删）。
4. **R3 是"未来的日终件"**：它 maturity=evolving、CONSUMERS 写"盘后 15:30 任务链等待接线"，
   而 R4 的 CONSUMERS 写"人工/后续调度触发"。二者争的是同一个档期。建议明确：**R4 为调度入口，
   R3 为其调用腿**，避免"两个 15:30 权威"。
5. **R7 必须摘出对账域**（与 R-013 同判）：它调的是编排器自完整性 5 不变量。
   留在对账域里，任何"对账结论"都无法判断是谁算的——这正是 R-015 担心的语义污染，
   且它同时挂 GOMAP `families.L5_selfheal` 会误导自愈链归属。

**落地次序建议（不新增删除，零 Owner 门位）**：
① 在 `governance_operations_map.yaml` 给 R1..R7 各加 `superseded_by` / `role` 注记（R7 摘出 L5_selfheal）；
② 把 R4 接进调度（`tasks.yaml` 归 residG 单一写者 → 出 YAML 片段交转，见 req_wirerecon_03 同类先例）；
③ R2/R3/R5/R6 的合并与 R1 的处置走**注册表净删门位**（Owner 批），本车道未动。

**风险与回滚**：本轮零代码行为变化（只出本表），回滚=删本文件。
