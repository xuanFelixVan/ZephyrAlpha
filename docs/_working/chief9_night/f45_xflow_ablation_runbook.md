---
ttl: task_bound
title: "F45 G45-2 · X 流消融实弹 runbook（预演+实弹+回滚；本档只记不跑）"
session: st-c9-f45
creation_token: f45-xflow-ablation-runbook-20260928
---

# X 流消融实弹 Runbook（G45-2 处方落盘——本文档只记命令，实弹不执行）

> **一句话**：把 09_f45 案卷 G45-2 与验证批 blueprint 处方中的 X 流消融实弹动作，
> 预写成可复核的三段式（预演→消融对照→实弹写台账）+ 前置清单 + 回滚预案。
> **实弹须 Owner 专门窗口放行后按本档逐步执行；st-c9-f45 本轮零实弹（纪律即本档存在原因）。**

## 0. 真源与安全口径（处方已定义，勿临场发明）

| 项 | 口径 | 真源 |
|---|---|---|
| §12 回放约束 | 参数定稿放行前**不得对 holdout 窗口实弹运行** | docs/03_modules/_domain_trading/validation/blueprint.md "不做"行 + ablation.py notes |
| holdout 纪律 | 保密考卷=最近 12 个月（holdout_months=12）；切分由 finalized_at="2026-09-09" 定稿锚点接管 | runner.py ValidationConfig（PB-08） |
| 预演语义 | `dry_run=True` 不写库不建档（验收预演专用） | runner.py run_validation L496/L597 |
| fail-closed | 写台账必须先建 run 过程档案；档案创建失败拒绝写台账 | runner.py SOP-D §4 底线（R1 批 2026-09-12） |
| 对照缺省 | ablation_diff 缺省时 verdict 如实降级 pending（不伪造对照） | runner.py compute_exit_counterfactual_metrics |
| 方向核对 | R1-03（护盘加仓白名单）动作方向为**买入**，消融放行时须单独核对方向 | blueprint.md §决策 5 |
| 台账 append-only | c1_backtest.node_verdict 只增不删不 UPDATE | RULE-DATA-OPS（trae_063） |

## 1. 前置检查清单（全勾才准进 §2）

- [ ] **Owner 放行**：专门窗口指令已登记（裁定/正式通道，口头不算——宪法 §9.11）。
- [ ] holdout 窗口确认：本次 run 的 as_of 与 finalized_at 组合下，`inside` 流水不含保密考卷窗；
      若消融回放窗口与 holdout 重叠 → 只允许通道 A 预演，通道 B/C 禁止。
- [ ] 原料在盘：`data/backtest_artifacts/` 当期回测流水（load_fills 输入）；
      `config/trading_decision_map.yaml` X 流 18 节点无漂移（`grep -c "node_id: TDM-X-S1"` =7）。
- [ ] 方向核对：actions 清单中无 R1-03 买入方向被误当卖出消融（sell_signals_to_xflow_actions
      只产 clear/reduce；若手工并入 R1-03 面须先核对方向语义）。
- [ ] 双档案位：run 档案目录可写（archive_root 缺省走 RunArchive 真源）；
      CH 台账链路可用（G/CH 单链口径按 INFRA-STORE-003，勿凭记忆连库）。

## 2. 通道 A——验证批预演（dry_run，随时可跑，不写库）

```bash
export PATH="/c/Users/fanzi/AppData/Local/Programs/Python/Python312:/c/Users/fanzi/AppData/Local/Programs/Python/Python312/Scripts:$PATH"
cd /d/ZephyrAlpha
python -c "
from zephyr.trading.validation.runner import run_validation
r = run_validation(batch='XFLOW', dry_run=True)
print('run_id=', r.run_id, 'rows=', len(r.rows), 'written=', r.written)
for row in r.rows[:3]: print(row['node_id'], row['verdict'], row['significance'])
"
```

验收：18 行 X 流 verdict 产出、`written=False`（零写入）、verdict 全 pending+insufficient_samples
如实披露；不建 run 档案（dry_run 语义）。

## 3. 通道 B——消融对照差额序列（回放，Owner 放行且非 holdout 窗才准跑）

```bash
python -c "
import pandas as pd
from zephyr.trading.validation.ablation import run_ablation, sell_signals_to_xflow_actions
# data=load_history 产物或 flat DataFrame(date/symbol/close)；panel_full=全量权重面板
# actions=sell_signals_to_xflow_actions(S1 信号清单)——来源=M8-002 扫描编排 S2 信封归集或回测流水重放
report = run_ablation(data=<DATA>, panel_full=<PANEL>, actions=<ACTIONS>, strategy_name='xflow_ablation')
print('rescued_total=', report.rescued_total)
print(report.notes)
"
```

要点：双 run 同一行情同一 config；差额=rescued（nav_full−nav_ablated）；notes 明示
"参数定稿放行前不得对 holdout 窗口实弹运行"。产出序列作为通道 C 的 `ablation_diff` 入参；
**不产/不合法 → 通道 C 照跑但对照缺失，verdict 自动 pending 降级（不阻塞、不伪造）**。

## 4. 通道 C——实弹写台账（Owner 专门窗口内执行）

```bash
python -c "
from zephyr.trading.validation.runner import run_validation
r = run_validation(batch='XFLOW', dry_run=False, ablation_diff=<通道B差额序列或None>)
print('run_id=', r.run_id, 'written=', r.written, 'archive=', r.archive_dir)
"
```

- 自动前置：fail-closed 建 run 档案成功才写台账；写台账未确认 CH_COMMITTED → 查 ch_writer
  落盘兜底（runner 内建语义，不需要人工补写）。
- 衰减巡检：写台账成功后尾随自动跑（事件驱动，无 cron）；失败不回滚验证批。

## 5. 验收查询（实弹后）

- 台账行数：`SELECT count() FROM c1_backtest.node_verdict WHERE run_id='<run_id>'` = 18。
- 过程可翻：`r.archive_dir` 目录含 metrics/nodes/cfg 归档（"结论必须能翻到过程"）。
- API 面：`/api/tdm/validation?node_id=TDM-X-S1-05` 可查回当轮 verdict。

## 6. 回滚与事故处置

1. **台账不可 DELETE**（append-only）：误弹/错弹 → 不删行；按 run_id 追加一条
   `verdict=invalidated` 说明行留痕，是否物理清理由 Owner 裁定走 RULE-DATA-OPS 三步验证。
2. **档案回滚**：未 finalize 的 run 档案目录（写台账失败态）→ 诚实保留为未归档态，
   勿手工补 finalize。
3. **消融回放**：纯内存计算零落库，无回滚面；面板误标重跑即可。
4. **全面回滚**：本批零代码侵入（消融件/runner 均存量），无需代码回滚；
   本 runbook 文档回滚=revert 本 commit。

## 7. 禁止事项

- 禁 holdout 窗口实弹（§12 铁律）；禁 dry_run 之外的"顺手试跑"；禁 DELETE/UPDATE 台账行；
- 禁裸连业务库（一律既有 DatabaseService/runner 通道）；禁把 pending 升格为 valid；
- 禁在本 runbook 之外另起命令变体（变更先改本档再执行）。
