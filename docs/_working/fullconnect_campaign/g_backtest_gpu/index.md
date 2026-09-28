---
status: active
title: "g_backtest_gpu — 目录索引"
module_id: ""
blueprint_id: ""
version: "1.0.0"
created: "2026-09-28"
updated: "2026-09-28"
ttl: "task_bound"
---

# g_backtest_gpu

> 本文件由 `generate_missing_index_md.py` 自动生成
> 生成日期：2026-09-28

## 目录内容

| 文件/目录 | 类型 | 说明 |
|-----------|------|------|
| [01_f58_execution_cost_feedback.md](01_f58_execution_cost_feedback.md) | Markdown | F58 执行成本反馈——执行质量评分→选型回写（G4 增长批闭环） |
| [02_f59_risk_limit_stoploss.md](02_f59_risk_limit_stoploss.md) | Markdown | F59 风控限额与止损引擎——REG-RLM-001 117 条九类+ATR/持仓风控 |
| [03_f60_drawdown_state_machine.md](03_f60_drawdown_state_machine.md) | Markdown | F60 回撤状态机与熔断——回撤分级状态机+清算守卫+券商端止损双保险 |
| [04_f61_killswitch_instances.md](04_f61_killswitch_instances.md) | Markdown | F61 KillSwitch 三实例族——交易级/容量级/回滚级+状态存储 |
| [05_f62_compliance_report_gate.md](05_f62_compliance_report_gate.md) | Markdown | F62 合规门与程序化交易报告——ReportGate C-002 拒单+FeatureGate 硬边界（码成闸空） |
| [06_f63_position_reconciliation.md](06_f63_position_reconciliation.md) | Markdown | F63 仓位管理与对账——持仓状态机/对账/NAV 记录/仓位漂移 |
| [07_f64_backtest_triad_registries.md](07_f64_backtest_triad_registries.md) | Markdown | F64 回测三件套——universe 7/benchmark 9/cost_model 6 每测 MUST 指定 |
| [08_f65_backtest_engine_family.md](08_f65_backtest_engine_family.md) | Markdown | F65 回测引擎族——事件驱动引擎+CH tick replay+撮合+组合核算（backtest 九子包） |
| [09_f66_backtest_prereg_loop.md](09_f66_backtest_prereg_loop.md) | Markdown | F66 回测预注册与七步循环——REG-BTB-001 跑前写死阈值；无注册不归档 |
| [10_f67_experiment_registry.md](10_f67_experiment_registry.md) | Markdown | F67 实验登记与档案——experiment_registry 11 条 FallbackBackend+Panel 实验 Tab |
| [11_f68_gpu_matrix_grid.md](11_f68_gpu_matrix_grid.md) | Markdown | F68 GPU 矩阵/工厂格子——prereg 冻结 v2→T0/T1→判卷→DSR（T1 dedup 完赛 all_green=false 本日新态） |
| [12_f69_t0_cost_gate_ibt.md](12_f69_t0_cost_gate_ibt.md) | Markdown | F69 T0/成本门/IBT——T0 成本模型+考试成本双口径门+复权降级 |

## 导航

- [上级目录](../index.md)
