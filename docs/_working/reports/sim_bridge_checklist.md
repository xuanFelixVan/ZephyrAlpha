---
ttl: task_bound
---

> ## 结案报告（2026-09-15 由 st-fullchain-20260914 核验）
> **总结论：证据不足，保守处理。处置=**保留**。**
>
> **✅ 已完成**：无显式完成信号
>
> **⚠️ 未完成**：无待办信号
>
> **核验方式**：全文扫描完成/待办信号 + 引用文件存在性核验（引用 2 个，其中判废弃 0、路径漂移 0）+ commit 提及 0 处。
>
> **处置建议**：保留。（本报告由清理批自动生成，判定依据=文档自身信号 + 代码侧核验）


# 回测→模拟盘桥梁检查单——`_SYNTHETIC_DEPTH` 不复用核验（外审 §4.2 承接）

> 2026-09-15 st-btfix-p14-20260914 班｜外审报告 §4"进模拟盘前的关键告警"第 2 项施工
> 结论先行：**模拟盘执行链路与回测合成盘口完全隔离，`_SYNTHETIC_DEPTH` 无复用路径**——
> 审查担心的"模拟盘复用回测无限深度假设"在当前代码结构下不成立，本单留证。

## 1. 隔离证据链（2026-09-15 实查）

| 证据 | 结论 |
|---|---|
| `grep _SYNTHETIC_DEPTH` 全仓 | 仅 `src/zephyr/backtest/core/matching_engine.py`（L104 定义 / L823-835 `_synthetic_order_book` 使用）；ex_core / trading / governance 零命中 |
| `src/zephyr/governance/adapters/simulation_broker.py` import 图 | 只依赖 `zephyr.shared.contracts.{fill,order,position}` + `trading_contracts.broker_interface`；**不 import 回测 matching_engine**，结构上无共享面 |
| 撮合共享边界 | 回测=实盘一致性的共享真源是 `MatchingLogic`（价格规则：费率/涨跌停/整手/T+1），**不含盘口深度**；深度数据回测侧来自真实 5 档 tick（`generate_fills_with_tick`），合成盘口仅是"无 5 档数据时的日频兜底" |
| 模拟盘成交路径 | SimulationBroker（`governance/adapters/simulation_broker.py`）按 Order→Fill 直接对价成交，走实时行情盘口（SIMULATION 模式 miniQMT 模拟通道）；撮合深度语义与回测 `_SYNTHETIC_DEPTH` 无交集 |

## 2. 上线模拟盘前检查单（后续班按序打勾）

1. **回测胜出策略准入**：进入模拟盘的策略必须带 P0-4 合理性护栏报告（无 quarantine 产物、CPCV/PBO/DSR 门通过）；
2. **预期差监控**：回测预测收益 vs 模拟盘实际成交 PnL 的周度偏差 >20% 触发复盘（防回测虚高假设漏网）；
3. **成交量约束口径确认**：日频回测的成交≤当日量 x% 参数与模拟盘真实流动性对照校准一次；
4. **KillSwitch 独立性确认**：交易熔断（`trading_contracts/risk/trading_kill_switch.py` + risk_layer_orchestrator）在 SIMULATION 模式的启用状态显式核验（P1-2 双向职责澄清已落库，本项为运行态确认）；
5. **本检查单归档**：模拟盘启动后把本单并入灾备/上线手册或销毁（ttl: task_bound）。

## 3. 审查原文对照

> 审查报告 §4.2："但务必确认模拟盘**不**复用回测的 `_SYNTHETIC_DEPTH` 假设。"

→ 核验结论：不复用（结构性隔离，见 §1）。审查报告 §4.3"模拟盘内部无资金红线自动熔断的
独立验证"由上表第 4 项承接（运行态确认项，非代码改动项）。
