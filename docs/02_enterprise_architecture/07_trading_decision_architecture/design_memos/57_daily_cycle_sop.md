---
ttl: permanent
completes_when: "日循环连续运行 5 个交易日且对账 G3-G7 施工完毕后转 maintenance（文档保留，流程图并入 55 号监控体系）"
doc_type: architecture_view
version: 1.0.0
created: 2026-08-21
owner: P0 批统筹代办，Owner 审批
---

# 57 · 交易日模拟盘+收盘后回测 日循环 SOP（P0-5）

> **用途**：把"到期前目标态"落成每个交易日可照做的运行手册——开盘前数据就绪检查 → 交易日模拟盘运行 → 15:30 收盘结算 → 当日回测跑批 → 对账 diff → 异常登记。与 55 号监控"日自动/周人工/月轻量"节奏对接。
> **铁律**：QMT 常开（Owner 裁定 2026-08-21，无法自动登录，不手动关闭就不关闭）；一切 DB 写操作留 Owner 窗口；本 SOP 所有命令默认只读或幂等。
> **对账口径真源** = 56 号文（56_backtest_vs_sim_reconciliation_plan.md）；本文是运行形态，不复述对账设计。

---

## 0. 日循环总览

| 时点 | 环节 | 形态 | 责任人 |
|---|---|---|---|
| 09:15 前 | ① 开盘前检查（QMT 在线+数据就绪） | 人工扫一眼+三条只读命令 | Owner 确认 QMT，AI 跑检查 |
| 09:30-15:00 | ② 盘中模拟盘运行 | 当前=手动启动会话（常驻服务=缺口 GAP-2） | AI/Owner |
| 15:30 后 | ③ 收盘结算管线 | 手动 dry-run（挂调度=缺口 GAP-3） | AI |
| 16:30 后 | ④ 当日回测跑批（daily_kline 落库后） | 库级调用+显式 sink 落盘 | AI |
| 随后 | ⑤ 对账 diff | 56 号文口径；G3-G7 未施工前=空对账走通+持仓 diff | AI |
| 当日 | ⑥ 异常登记 | tracker P0 节表（格式见 §6） | AI |

## 1. ① 开盘前检查（09:15 前，三条只读命令 + 一项人工确认）

```powershell
# C1 人工确认 QMT 在线（Owner 窗口项，常开口径）——进程存在即过：
Get-Process | Where-Object {$_.ProcessName -match "XtMiniQmt"}
# C2 调度器与今日任务状态（只读）：
python -m zephyr.data status
# C3 十源健康检查（只读探针，结果落 logs/source_health_YYYYMMDD.log）：
python -c "import sys;sys.path.insert(0,'src');from zephyr.data.source_health_check import run_source_health_check as f;print(f())"
```

| 判据 | 通过线 | 失败处置 |
|---|---|---|
| C1 QMT 进程 | XtMiniQmt 进程在 | **当日模拟盘标记 SKIP**，tracker 登记 C 类异常，通知 Owner 启动 |
| C2 关键任务 | kline_daily_incremental/stk_limit_premarket 最近运行 SUCCESS | 手动补跑 `python -m zephyr.data run <task_id>`（幂等写 CH） |
| C3 十源 | miniqmt 必须 connect_ok；其余源允许单源 fail（有 fallback） | 同源连续 3 天异常自动告警（source_health_check 内建） |

> 关键表新鲜度半缺口（GAP-4）：`python scripts/ch/_data_inventory.py` 只读盘点 min/max(trade_date)，但其 key_tables 清单未含 trade_calendar/stock_list/stk_limit/limit_up_down——扩清单属小改，已登记。

## 2. ② 盘中模拟盘运行（09:30-15:00）

**当前形态（如实）**：无常驻服务入口（GAP-2）。库级可执行体 = `TradingSession`（src/zephyr/ex_core/trading_session.py L191：start() L274 连接+回调注册、stop() L305 自动撤未成交单、rebalance() L321 手动单次）。

- 冒烟验证（非交易日/彩排用）：`python scripts/tests/smoke_test_trading_session.py`（mock 信号、限价不成交设计）。
- 交易日运行（过渡形态）：由 AI 会话在 09:25 前手动拉起 TradingSession 进程并保活；FillHandler 内存累计当日 Fill（**进程退出即失——56 号文 G3 Fill 落盘持久化未施工，当日 Fill 须 15:00 前在进程内导出**）。
- QMT 探活（只读）：`broker.get_positions()` 正常返回即在线（56 号文 C1 判据）。

## 3. ③ 收盘结算（15:30 后）

```powershell
# dry-run（未注入 reconcile_fn/audit_fn 时全 SKIPPED，零副作用）：
python -c "import sys;sys.path.insert(0,'src');from zephyr.trading.post_settlement_pipeline import run_post_settlement_pipeline as r;print(r('<YYYY-MM-DD>'))"
```

- 真实跑需注入 reconcile_fn（SettlementReconciler.reconcile）+ audit_fn（DailyAuditor.audit）——注入脚本未施工（GAP-3 同族）；reconciliation_differences 表 DDL 未执行（tracker #234 Owner 窗口）前真实跑也不落 DB。
- 挂调度（cron 30 15 * * * 规格已在 build_post_settlement_jobs 备好）= GAP-3，Owner 窗口批准后的接线动作。

## 4. ④ 当日回测跑批（16:30 daily_kline 落库后）

```powershell
# 向量化日频（只读 CH；窗口建议 [T-3月, T]，调仓频率 W——'B' 月末调仓在短窗口零调仓点是参数语义非断链，彩排实证）：
python -c "import sys;sys.path.insert(0,'src');from zephyr.pf_core.strategy_engine.strategy_runner import StrategyRunner,StrategyRunnerConfig;from zephyr.backtest.io.backtest_result_sink import sink_backtest_result;from zephyr.backtest.io.result_repository import build_artifact_from_data,save_artifact;r=StrategyRunner().run_backtest(<标的列表>,'<start>','<end>',StrategyRunnerConfig(strategy_id='topn-momentum',factor_ids=('momentum_20d',),rebalance_freq='W',top_n=2));p=save_artifact(build_artifact_from_data(sink_backtest_result(r)));print(p)"
```

- 产物落 `data/backtest_artifacts/{run_id}.json`（写文件无 DB 写）。
- **56 号文 I4 缺口（GAP-5）**：向量化路径 BacktestResult 只有 15 个汇总字段无逐笔 trade_log；EDE 路径（run_tick_backtest）有 BacktestFill 但需 QMT 在线。对账 L1 逐笔所需的明细产出属 G3-G7 施工面。
- 信号一致性：回测与模拟盘共用同一 StrategyBase 实例与 MatchingLogic（56 号文 I1/I2）。

## 5. ⑤ 对账 diff（56 号文口径）

G3-G7 未施工期的**过渡上限**（彩排实证可走通）：

```powershell
# L1 空对账冒烟（引擎接线验证）：
python -c "import sys;sys.path.insert(0,'src');from zephyr.trading.settlement_reconciliation import SettlementReconciler;print(SettlementReconciler().reconcile(system_fills=[],broker_records=[],settlement_date='<YYYY-MM-DD>').matched)"
# L2 持仓 diff：回测 trade_log 重放持仓 vs broker.get_positions() 逐标的比对（QMT 在线时）
```

- 归因三分类（A 滑点/B 部分成交/C 拒单缺失）与 10 项对照清单见 56 号文 §3/§6——费用差不判定（G1 费率口径待 Owner 裁定，tracker #233）。
- 当日无成交时无法区分 C 类拒单 vs 推送缺漏（56 号文 R2），只登记不判定。

## 6. ⑥ 异常登记（当日闭环）

登记处 = construction_progress_tracker.md 最新小节表（`| # | 遗留项 | 来源 | 说明 | 状态 |`）；对账异常按 56 号文 §3 三分类归因；闭环判据 = 56 号文 C10（当日全部 A/B/C 类差异有 tracker 条目或豁免理由，未闭环次日 SOP 首查）。

## 7. 缺口登记（施工排期，非本 SOP 阻塞项）

| # | 缺口 | 出处/登记 |
|---|---|---|
| GAP-1 | 56 号文 G3-G7（query_stock_trades 封装/BrokerSettlementRecord 适配器/适配层 A/recon_runner） | tracker #232 |
| GAP-2 | 盘中模拟盘常驻服务入口（LiveStrategyAdapter 未施工+TradingSession 无生产拉起件） | 架构评审 INT 族 |
| GAP-3 | post_settlement_pipeline 未挂调度+无 CLI/注入脚本 | 架构评审 INT-02 |
| GAP-4 | _data_inventory.py key_tables 扩 4 表（trade_calendar/stock_list/stk_limit/limit_up_down） | 本 SOP §1 |
| GAP-5 | 向量化路径无逐笔 trade_log（56 号文 I4 在向量化引擎不满足）+引擎→sink 无现成批处理脚本 | 56 号文 §4 |

## 8. 彩排记录（验收口径：无演练记录不予通过）

**2026-08-21 晚（收盘后）首跑**：

| 环节 | 结果 | 证据 |
|---|---|---|
| ① C2 调度状态 | ✅ 调度器活跃，今日任务 SUCCESS 在册（macro_data 8029 行等） | `python -m zephyr.data status` |
| ① C3 十源健康 | ⚠️ 8/10 healthy；miniqmt test_fail（connect_ok）、tqcenter connect_fail（通达信客户端未开） | source_health_check 实测输出 |
| ① C1 QMT 在线 | ❌ **XtMiniQmt 进程未运行**——Owner 窗口项，首日即命中检查项价值；次日开盘前 Owner 启动后复核 | Get-Process 实测空 |
| ④ 回测跑批 | ✅ 5 标的 2026-06-01~08-21 W 调仓：trades=17，total_return=+3.62%，引擎端到端走通 | run_backtest 实测 |
| ④ sink 落盘 | ✅ bt-e8405c0f.json（727B）落 data/backtest_artifacts/ | save_artifact 实测 |
| ③ 结算 dry-run | ✅ reconcile_status=SKIPPED/audit_status=SKIPPED 零副作用（未注入+未挂调度缺口实证） | run_post_settlement_pipeline 实测 |
| ⑤ 空对账 | ✅ matched=True（L1 引擎接线冒烟通过） | SettlementReconciler.reconcile 实测 |
| ② 盘中模拟盘 | ⏭️ 非交易时段不跑；当前形态=手动拉起（GAP-2） | — |

**彩排结论**：日循环骨架可走通；两处 Owner 窗口（QMT 启动、G1/G6 裁定）+五处 GAP 登记在案。下一交易日按 §1-§6 全流程复演。

## 9. 与 55 号监控节奏对接

- **日自动**：本 SOP ③⑤ 即 55 号"日自动"件（DailyAuditor 五件套+对账 diff），人只看 FAIL/C 类项。
- **周人工**：对账差异周汇总+滑点样本池复核进 55 号 run_weekly 通道。
- **月轻量**：SOP 本身月度评审（流程是否仍与实际接线一致）随 run_monthly 节奏。

---

> 本文 ttl=permanent + completes_when；运行中发现口径漂移立即更新本文（文档-现实漂移=治理事故族）。
