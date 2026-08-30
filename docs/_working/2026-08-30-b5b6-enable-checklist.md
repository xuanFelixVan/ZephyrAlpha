---
ttl: task_bound
---

# B5/B6 启用冒烟 Checklist（Owner 一键启用前逐项核查）

> **用途**：44 号 M1/M2/M3 模块群（B5）与 recon_runner（B6）从 testing 封顶切 production 前，Owner 按本清单逐项确认通过标准，无勾选=不得翻生产开关。
> **真源**：44_premarket_intraday_decision_upgrade.md、56_backtest_vs_sim_reconciliation_plan.md、construction_backlog.md、remaining_construction_roadmap.md B5/B6 项。
> **Owner 动作**：逐项打勾 → 签字/日期 → 最后执行 `Enable-ScheduledTask ZephyrAlpha_PaperSession`（B5）与 `Enable-ScheduledTask ZephyrAlpha_PostSettlement` + recon_runner 注入接线（B6）。
> **前置**：本清单不替代代码 review，仅覆盖"Owner 窗口 + 外部条件"阻塞项；代码侧已由全量审查批实证（2026-08-28）通过。

---

## B5 项：44 号 M1/M2/M3 模块群 production 启用

### B5-1 数据源就绪
| # | 检查点 | 通过标准 | 勾选 |
|---|---|---|---|
| B5-1.1 | auction_book 竞价盘口采集任务在采（9:15-9:25 五档） | `SELECT max(trade_date) FROM auction_book` = 最近交易日，且行数 >0 | ☐ |
| B5-1.2 | us_index 美股隔夜数据新鲜 | `SELECT max(trade_date) FROM us_index` ≥ T-1（非节假日缺口 ≤3 天可接受） | ☐ |
| B5-1.3 | 期指日频 kline_futures IF/IC/IM/IH 主力连续已回补 | 阶段二批回填实证：IF0/IC0/IH0 各 ≥2329 行，IM0 ≥991 行 | ☐ |
| B5-1.4 | 国内股指期货 tick/分钟采集已配置（futures_kline_qmt symbols） | `tasks.yaml` 或调度器配置中 futures_kline_qmt symbols 非空，含 IF/IC/IM/IH 主力连续 | ☐ |
| B5-1.5 | A50 期指数据源可用（新浪主源兜底） | `a50_futures_daily` 表 max(trade_date) ≥ T-3，且非全空值 | ☐ |
| B5-1.6 | ES/NQ 美股期指盘中实时通道已配 | L1 调度族新增 `futures_foreign_commodity_realtime` 任务，1min 轮询，akshare 接口可达 | ☐ |
| B5-1.7 | calendar_event 写入任务已注册（P0-4② 回填） | `calendar_event` 派生函数写入任务已在 `tasks.yaml` 注册，日更 | ☐ |

### B5-2 模块级健康
| # | 检查点 | 通过标准 | 勾选 |
|---|---|---|---|
| B5-2.1 | M1 MOD-SIG-025 情绪增量特征组管道可跑通 | `python -m zephyr.signal_ashare.market_sentiment_analyzer` 不报 ImportError，关键字段 time_series 存在 | ☐ |
| B5-2.2 | M2 boundary_revision_engine 可生成修正边界 | 调用 `BoundaryRevisionEngine.revise()` 返回非空 BoundaryRevision，且不抛异常 | ☐ |
| B5-2.3 | M3-⑨ llm_premarket_analysis 可完成一次全链路 dry-run | `python scripts/start_paper_session.py --dry-run` 或 `run_llm_analysis` 测试注入返回 status=success（含 mock llm_client） | ☐ |
| B5-2.4 | M3 盘前多情景方案可消费 auction_book | scenario_planner / boundary_revision_engine 能读到当日 auction_book 快照并参与边界匹配 | ☐ |
| B5-2.5 | daily_warroom_pipeline 产出无异常 | `python -m zephyr.plan_engine.daily_warroom_pipeline` 或调度器任务状态 SUCCESS | ☐ |

### B5-3 成本与预算
| # | 检查点 | 通过标准 | 勾选 |
|---|---|---|---|
| B5-3.1 | LLM API 预算已设定（日/月上限） | `BudgetEngine` / `cost_budget` 日预算 ≤ Owner 批准值（建议 ≤ ¥5/日） | ☐ |
| B5-3.2 | DeepSeek 账户余额可覆盖 3 个月谷时跑批 | 余额 ≥ ¥20（v1 730 日 ≈ ¥15, v2 ≈ ¥19）或 Qwen 降级链已验证可用 | ☐ |
| B5-3.3 | Qwen 降级链已真实跑通 | `llm_call_log` 有 ≥1 条 qwen-flash 成功记录（status=ok, cost_yuan>0） | ☐ |
| B5-3.4 | PIT 回填成本已知情 | Owner 已读 `scripts/estimate_pit_backfill_cost.py` 输出并确认 3 年回填预算 | ☐ |

### B5-4 基础设施与调度
| # | 检查点 | 通过标准 | 勾选 |
|---|---|---|---|
| B5-4.1 | `llm_daily_analysis` 表已建（DDL-as-Code） | `ensure_llm_daily_analysis_table()` 幂等建表成功，字段含 tokens_in/tokens_out/cost_yuan | ☐ |
| B5-4.2 | `ZephyrAlpha_PaperSession` 任务已注册且状态 DISABLED | `schtasks /query /tn ZephyrAlpha_PaperSession` 显示 TaskName 存在、State=Disabled | ☐ |
| B5-4.3 | deadman_switch 第四路已纳入（live_strategy_biz） | `scripts/deadman_switch.ps1` 包含 live_strategy_biz 心跳检查段落（biz stale >10min 告警） | ☐ |
| B5-4.4 | 盘前 8:00 前自动跑批链路可触发 | 手动跑一次 `scripts/start_paper_session_daily.ps1`（或等次日 09:25 观察 wrapper 日志），`paper_session.log` 写入且 is_trading_day 守卫正常 | ☐ |
| B5-4.5 | QMT 常开口径已确认 | Owner 已阅读 57 号文 §1 C1：XtMiniQmt 进程需人工启动；09:25 前必须在线；不在则当日 SKIP（不 crash-loop） | ☐ |

---

## B6 项：recon_runner production 启用

### B6-1 前置 Owner 窗口项
| # | 检查点 | 通过标准 | 勾选 |
|---|---|---|---|
| B6-1.1 | `reconciliation_differences` 表 DDL 已执行 | `SELECT name FROM sqlite_master WHERE type='table' AND name='reconciliation_differences'` 返回 1 行 | ☐ |
| B6-1.2 | 费率口径已统一（56 号文 G1） | `matching_logic` / `pnl_calculator` / `t0_cost_model` 三处费率与券商实际交割单一致（万 0.854/万 5/万 0.1） | ☐ |
| B6-1.3 | 对账 L3 期初持仓快照数据源已裁定（B20） | Owner 已阅读 `docs/_working/2026-08-30-l3-snapshot-datasource-adjudication.md` 并勾选推荐方案 | ☐ |

### B6-2 管线注入
| # | 检查点 | 通过标准 | 勾选 |
|---|---|---|---|
| B6-2.1 | post_settlement_pipeline 已注入 reconcile_fn | `run_post_settlement_pipeline` 调用时 `reconcile_fn` 不为 None（ SettlementReconciler.reconcile 或等价实现） | ☐ |
| B6-2.2 | post_settlement_pipeline 已注入 audit_fn | `run_post_settlement_pipeline` 调用时 `audit_fn` 不为 None（DailyAuditor.audit 或等价实现） | ☐ |
| B6-2.3 | `ZephyrAlpha_PostSettlement` 任务已注册且状态 ENABLED | `schtasks /query /tn ZephyrAlpha_PostSettlement` 显示 State=Ready/Running；15:30 触发 | ☐ |

### B6-3 对账链路冒烟
| # | 检查点 | 通过标准 | 勾选 |
|---|---|---|---|
| B6-3.1 | L1 交易级 diff 可跑通 | `run_daily_reconciliation(..., broker=b)` 返回 `l1_result` 且 `drifts` 为 list（空/非空均可，不抛异常） | ☐ |
| B6-3.2 | L2 持仓级 diff 可跑通 | `l2_result.drifts` 为 list，不抛异常 | ☐ |
| B6-3.3 | L3 PnL 级 diff 可跑通（或 SKIPPED 有理由） | `l3_result` 非 None（有 equity_curve）或日志明确标注 "L3 跳过：回测 artifact 缺 equity_curve" | ☐ |
| B6-3.4 | 差异可落库 | 跑一次对账后 `reconciliation_differences` 表新增行数 ≥0（MATCH 时 0 行亦通过，只要不抛异常） | ☐ |
| B6-3.5 | C 类拒单/缺失当日告警链路通 | 模拟构造一笔回测有实盘无的 diff，C 类项在 `result.c_class_items` 中列出，且 tracker 登记成功 | ☐ |

---

## 综合启用动作（全部勾选后执行）

| 动作 | 命令 | 执行人 |
|---|---|---|
| B5 翻生产 | `Enable-ScheduledTask ZephyrAlpha_PaperSession` | Owner |
| B5 验证 | `schtasks /run /tn ZephyrAlpha_PaperSession`（交易日 09:25 前手动触发一次，观察 `tmp/live_strategy_biz.heartbeat` 生成且 deadman_switch 不告警） | Owner |
| B6 翻生产 | 确认 `ZephyrAlpha_PostSettlement` 已 Enable（若此前已挂调度则只需复核 State=Ready） | Owner |
| B6 验证 | 交易日 15:30 后观察 `post_settlement.log`：reconcile_status / audit_status 不为 SKIPPED（=已注入真实 reconcile_fn/audit_fn） | Owner |
| 归档 | 本 checklist 勾选页拍照/截图存入 `docs/_archive/owner_approvals/` | Owner |

---

## 修订记录

| 日期 | 版本 | 改动 | 理由 |
|---|---|---|---|
| 2026-08-30 | 1.0.0 | 初版 | B5/B6 启用无统一冒烟口径，补 checklist 真源 |
