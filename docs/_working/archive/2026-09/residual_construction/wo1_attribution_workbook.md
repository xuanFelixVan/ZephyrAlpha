---
ttl: task_bound
title: WO-1 收益归因例行轻量作业簿——策略级 P&L 分解/成本拖累/基准相对/风险贡献
owner: ZephyrAlpha-Owner
session: st-residual-20260917
date: 2026-09-17
status: mining_light
---

# WO-1 收益归因例行 · 轻量作业簿

> **真源**：[pending_items_plan.md](pending_items_plan.md) WORK-ORDER-1。按挖矿分级走轻量（复用件多、边界清晰），实底来自 WO-2/WO-5 两批勘察（sim 家族/pipeline_events 已探），免再勘察。

## 1. 落点与复用

- **新件**：`scripts/backtest/sim_attribution_report.py`，与 `sim_paper_ledger.py`/`sim_deviation_report.py`/`sim_governance.py` 同族并列。
- **输入**：`c1_backtest.sim_pocket_daily`（账本，现 62 行/2026-07-01 起）；`strategy_registry`（策略映射）；`kline_index`（基准，000300 在用——**开放点 O-1：中证1000 000852 是否在库，施工时核**，组合以中小盘为主建议双基准都出）；`regime_snapshot_history`（regime 分段归因可选）。
- **复用**：`backtest/core/cost_attribution.py` + `cost_model_calibration.py`（成本归因已有件，先读接口再决定复用还是引用参数）；成本参数真源=`config` 佣金/滑点/¥5 地板（做T 成本解剖 001 的口径）。

## 2. 输出设计

- **新表**：`c1_backtest.sim_attribution_daily`，**长表**（裁定抄 WO-5 S1 先例）：trade_date / strategy_id / pnl_gross / pnl_cost（佣金+滑点+地板）/ pnl_net / benchmark_rel（vs 基准日收益）/ risk_contrib（波动贡献占比）/ detail JSON / ingest_ts。RMT 只增不改。
- **四段答案**（对应主单验收）：钱哪个策略赚的（strategy_id 分解）/成本吃多少（pnl_gross-pnl_net）/相对基准超额多少（benchmark_rel）/风险贡献怎么分（risk_contrib）。
- 与 `sim_deviation_report` 的分工：偏差="当时说 vs 实际走"，归因="实际走的钱从哪来"——两件并列不合并。

## 3. 接线

- `pipeline_events`：`maybe_emit_sim_daily` 成功后追加 `maybe_emit_attribution_daily`（deps=sim 账本当日 marker），超时/幂等/marker 机制照抄 `run_sim_ledger_daily`（:393-401）同款。
- 调度：不新增计划任务，走事件链（与全链自动化惯例一致）。

## 4. 验收

1. 62 天存量账本全量回放，`pnl_net` 加总与 `sim_pocket_daily` 对平（差异=0，对不上的每一笔都能指到口径）。
2. 此后每日自动落行，marker 留痕。
3. 四段字段齐全，单策略期 risk_contrib=100%（sanity check）。

## 5. 边界与自审

- **不做**：逐笔 trade-level 归因（账本日频颗粒度）、前端页（先数据表）、Brinson 多层分解（单策略期无意义，多策略转正后再升级——挂长尾 M-11）。
- **自审闸**：北极星=E7 攒 30 笔样本期"钱从哪来"自动可答，消灭 Owner 手工对账；复用度高（账本/成本件/事件链全现成）；成本 1-2 会话 → **施工**。
- **红蓝预登记**：成本参数若与账本实际记账口径不一致，归因会系统性错——施工时先对 `sim_paper_ledger` 的成本记账代码逐行核口径，禁直接引用 config 默认值。
