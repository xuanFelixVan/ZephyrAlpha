---
ttl: permanent
completes_when: "日循环连续运行 5 个交易日且对账 G3-G7 施工完毕后转 maintenance（文档保留，流程图并入 55 号监控体系）"
doc_type: architecture_view
status: active
version: 1.1.0
created: 2026-08-21
owner: P0 批统筹代办，Owner 审批
---

# 57 · 交易日模拟盘+收盘后回测 日循环 SOP（P0-5）

> ## 结案报告（2026-08-28 全量审查批，代码实证）
> **实际开发**：六环节 SOP 定稿；首跑彩排已过（2026-08-21 晚收盘后）；GAP-2 start_paper_session.py（模拟盘启动 MVP）；GAP-3 run_post_settlement.py（结算 CLI 真跑 exit 0，已挂计划任务 ZephyrAlpha_PostSettlement 每日 15:30）；GAP-4 _data_inventory 扩表+None 行数修复；GAP-5 转 CAND-BT-003。
> **最终成果**：SOP active v1.1.0 + 日循环链路可跑通（回测跑批/sink 落盘/结算 dry-run/空对账全实证）。
> **未做+原因**：①GAP-2 常驻服务化（LiveStrategyAdapter）未做，待排期；②QMT 开盘前在线人工确认=常态 Owner 动作（QMT 无法自动登录，保持常开口径）；③RUN-05 真实断网断电演练留 Owner 窗口。

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
- **trading 主进程看门狗已备（INT-03，2026-08-22）**：`scripts/start_trading.ps1`（while-true 守护+单实例锁+15s 心跳 `tmp/trading.heartbeat`+孤儿清理，守护对象 `python -m zephyr.trading`）；注册块已入 `scripts/register_guard_tasks.ps1`（**Disabled 态**，92 号 D3 裁定：当前无常驻 trading 生产进程，enabled 会拉起本不在跑的进程=生产变更，disabled 保留恢复可能）。执行注册=统筹/Owner 窗口；翻开=`Enable-ScheduledTask ZephyrAlpha_TradingWatchdog` Owner 一键。翻开后进程级自愈 RTO<5min（5min 重点火+心跳接管，同数据域看门狗三件套口径）；**QMT 崩溃/掉线场景端到端 RTO 仍依赖人工重登**（QMT 无法自动登录，同 RestartMiniQmt disable 先例），对齐 system_charter 约束五"交易时段 RTO<5 分钟"。启用时配套：把 `tmp/trading.heartbeat` 加入 deadman_switch.ps1 `$Heartbeats` 第四路（Disabled 态不纳入，防 MISSING 误报）。

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

**G3-G7 已施工（2026-08-21，#ARCH-135）——当前可执行形态**：

```powershell
# 当日全流程（QMT 在线+当日回测已 sink 落盘前提下）：
python -c "import sys;sys.path.insert(0,'src');from zephyr.ex_core.adapters.miniqmt_broker import MiniQmtBroker;from zephyr.trading.recon_runner import run_daily_reconciliation;b=MiniQmtBroker(path='<QMT_SIM_PATH>',session_id='sop-recon',account_id='<QMT_SIM_ACCOUNT>');b.connect();r=run_daily_reconciliation(trade_date='<YYYY-MM-DD>',run_id='<当日回测 run_id>',broker=b);print(r.to_dict())"
# 差异自动落 governance.db reconciliation_differences；C 类（拒单/缺失）清单在 result.c_class_items——当日告警+tracker 登记
```

- 归因三分类（A 滑点/B 部分成交/C 拒单缺失）与 10 项对照清单见 56 号文 §3/§6——费用差仅参考列不判定（#233 已统一费率口径，万0.854/万5/万0.1）。
- 配对键口径={symbol}|{seq:03d}（broker_settlement_adapter 真源）；实盘拆单错位由 C4 笔数差 ≤5% 兜底。
- L3 PnL 级当前为期初空仓假设代理口径——滚动持仓场景的期初快照数据源是窗口项（§7 GAP 表外追加项）。
- 当日无成交时无法区分 C 类拒单 vs 推送缺漏（56 号文 R2），只登记不判定。

## 6. ⑥ 异常登记（当日闭环）

登记处 = construction_progress_tracker.md 最新小节表（`| # | 遗留项 | 来源 | 说明 | 状态 |`）；对账异常按 56 号文 §3 三分类归因；闭环判据 = 56 号文 C10（当日全部 A/B/C 类差异有 tracker 条目或豁免理由，未闭环次日 SOP 首查）。

## 7. 缺口登记（施工排期，非本 SOP 阻塞项）

| # | 缺口 | 状态（2026-08-21 Owner 全批后） |
|---|---|---|
| GAP-1 | 56 号文 G3-G7 | ✅ 已施工（#ARCH-135：query_trades_today 兜底+Fill JSONL 落盘+双适配器+recon_runner，testing 封顶） |
| GAP-2 | 盘中模拟盘常驻服务入口 | ◐ 部分闭环：start_paper_session.py 拉起脚本已落（交易日 09:25 前手动执行）；LiveStrategyAdapter 与常驻服务化仍登记后续批 |
| GAP-3 | post_settlement 挂调度+CLI | ◐ 部分闭环：run_post_settlement.py CLI 已落实证 exit 0；挂调度（cron 30 15 规格已备）=Owner 窗口待批 |
| GAP-4 | _data_inventory 关键表 | ✅ 已闭环（+trade_calendar/stk_limit/limit_up_down+None 行数存量 bug 修复） |
| GAP-5 | 向量化逐笔 trade_log+跑批脚本 | ✅ 登记 CAND-BT-003（触发=对账需向量化基准；当前 EDE 路径分工不缺口）；跑批显式串 sink 见 §4 命令 |
| 追加 | recon_runner L3 期初持仓快照数据源 | ⏳ 登记（滚动持仓场景 L3 精确化的前置） |
| 追加 | kline_daily/stk_limit 数据滞后 2 交易日（最新 2026-08-19） | ⏳ 周一开盘前 §1 C2 核查（GAP-4 实证发现） |

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

**2026-08-21 深夜第二场（QMT 模拟盘在线后补演，Owner 批准）**：

| 环节 | 结果 | 证据 |
|---|---|---|
| ① C1 QMT 在线 | ✅ XtMiniQmt 进程在（PID 62132，22:44 启动）；broker.connect+get_positions 实测通过——PositionSnapshot cash=10,000,000 模拟资金、holdings={} | MiniQmtBroker 实测 |
| P0-7 drift 复产 | ✅ scheduled_light 扫描 11 事件全写入（807→818 行，written>0），Dashboard data_as_of=2026-08-21T14:57:07Z 实时可见——断链 3 个月修复后首个受控生产验证 | drift_events 行数对账+data_as_of |
| ④ EDE tick 回放回测 | ✅ Path A 端到端（CH 日K→因子→权重→tick callback→EDE→5 档撮合→成交）：trades=2，验收三步全 OK | smoke_test_ede_path_a.py |
| ⑤ 空对账 | ✅（沿首场） | — |

**彩排总结论**：目标态六环节全部实证可走通——开盘前检查（含 QMT 人工确认）、回测双引擎（向量化+EDE tick）、sink 落盘、结算管线、对账冒烟、drift 监控复产。盘中模拟盘段待下一交易日（09:30-15:00）按 §2 过渡形态复演。

## 9. 断网断电断点恢复演练（RUN-05，宪章约束五 RPO=0 实证）

> 来源：architecture_review_2026_08_module_upgrade_audit.md §5.3（唯一新增项）。宪章约束五「断电断网→策略状态机断点恢复、持仓 RPO=0」此前无演练项，彩排清单（§1-§6）未覆盖家用最高概率故障。本节为文档口径预置；**真实演练留 Owner 窗口**（断网断电是物理操作，须 Owner 执行或在场，AI 不得自行断电/断网），首次实测排期后按 §8 格式回填演练记录。

**频次**：随彩排日每演 1 次；**验收口径**：彩排日实测留记录（无演练记录不予通过，同 §8）。

**演练步骤**：

1. **前置**：日循环 ② 盘中形态运行中——TradingSession（或 `scripts/start_paper_session.py` 拉起的模拟盘会话）保活、数据调度在跑、当日已有 fill 流入（无成交日用 §2 冒烟单造 1 笔 mock fill）。
2. **故障注入**：杀 trading 进程 + data 调度进程（`Get-Process python | Where-Object 命令行匹配即停`）；Owner 断网 **5 分钟**（拔网线/禁用网卡）。
3. **恢复**：恢复网络 → 重启 data 调度与 trading 进程（看门狗翻开态由 `scripts/start_trading.ps1` 自动接管，Disabled 态手动拉起）。
4. **三项核对（全部自 state_store 重建核对，RPO=0 判据）**：

   | # | 核对项 | 通过线 |
   |---|---|---|
   | K1 | KillSwitch 状态 | `state_store.load("kill_switch")` 记录与故障前一致——未误触发、状态机断点连续（state_store 损坏须 raise StateCorruptError 而非静默重置） |
   | K2 | 持仓 | 重启后 PositionTracker 自 fill 持久化日志重建持仓 == `broker.get_positions()` 实盘快照逐标的一致（RPO=0） |
   | K3 | fill 去重集 | AppendOnlyDedupSet 持久化去重集重启后完整加载，重放当日 fill 零重复入账（at-most-once 实证，FillHandler/PositionTracker 双路径各核一遍） |

5. **记录**：按下表格式留证并追加到 §8（故障注入时刻/恢复时刻/RTO/三项核对结果/异常处置）。

   | 环节 | 结果 | 证据 |
   |---|---|---|
   | 故障注入+恢复 | ⏳ 待 Owner 窗口首演 | — |
   | K1 KillSwitch 状态 | ⏳ | — |
   | K2 持仓 RPO=0 | ⏳ | — |
   | K3 fill 去重零重复 | ⏳ | — |

**当前状态（2026-08-24）**：文档节已入册；首次真实演练待 Owner 窗口排期，实测后本节子表回填并同步 55 号监控月评审。

## 10. 与 55 号监控节奏对接

- **日自动**：本 SOP ③⑤ 即 55 号"日自动"件（DailyAuditor 五件套+对账 diff），人只看 FAIL/C 类项。
- **周人工**：对账差异周汇总+滑点样本池复核进 55 号 run_weekly 通道。
- **月轻量**：SOP 本身月度评审（流程是否仍与实际接线一致）随 run_monthly 节奏。

---

> 本文 ttl=permanent + completes_when；运行中发现口径漂移立即更新本文（文档-现实漂移=治理事故族）。
