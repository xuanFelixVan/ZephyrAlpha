---
ttl: task_bound
session: st-dloop-20260921
issue: DLOOP-V2-E2E-RUN
completes_when: 两圈全记录完毕（本稿=终版结构，数字随圈更新）
---

# E2E 手动全链运转记录（段C）

> 全程观察/记录模式零下单；时点均北京时间；台账行数对照口径=c1_market 四表+decision_daily+prediction_log。

## 0. 跑前合规
- 时序板核过：乙线 00:30-05:30 为 F→G 盘间镜像（CH 零影响声明），本班 CH 小量读写避开 02:30 夜跑带；
- 09-18 为最近完整交易日（周五），09-21 为次交易日（周一，实时）。

## 1. 第一圈：2026-09-18（历史完整日，05:41 手动 full 圈，--force-decision）

| 段 | 结果 | 实证 |
|---|---|---|
| data_readiness | ok | kline_index max=09-18 |
| regime_freshness | ok fresh | required≥09-17，实际 09-18（本班 05:09 逃生口补印 09-16~18 三行后） |
| warroom | premarket=**ok（史上首批 scenario_plan）** postmarket=skipped:no_prediction（诚实：09-18 无预案可回写） | prediction_log scenario_plan×1 trade_date=09-21 |
| daily_plan | ok 落库 | 判定为"此刻预案"（asof=09-20 UTC=PIT 语义） |
| next_day | ok 落库 | 同上 |
| pf_alloc | skipped:already_queued_or_done | 记号幂等（09-18 16:34 已 alloc） |
| intraday_l1 | no_new_bar | bar_key 幂等 |
| classify | no_bars | 墙钟未开盘，诚实 |
| close_verify | no_plan（plan_date=09-17 缺） | 09-17 场次无预案=历史空洞，不伪造 |
| settle | 三表扫描 | 见台账对照 |
| decision | **adjudicated target=09-21 state=expansion@1.00 cap=60.00% no_trade=0 degraded=1(D2:L2)** | regime 修复直接解锁非降级核心行 |

**首圈前置修复**（非圈本身但为圈解锁条件）：
- regime_snapshot_history 09-15→09-18（print_regime_history.py 官方逃生口，run 已归档）；
- verify_for_session("2026-09-16") → **verification 表 0→1（历史首行）**：actual=S3_oscillation，
  plan_quality=0.7388，盘中命中 n_hits=1。

## 2. 第二圈：2026-09-21（实时圈）

### 2a. 盘中段（事件链自动+总扳手手动采样双轨，10:35/11:35/14:05/15:05 四拍全过）
- 事件链按 60min bar 自动产盘中五态行+归类验证行（10:30 bar 归类 appended n_hits=1；
  11:30/14:05/15:05 采样 no_change=查重闸实证，verification 表盘中行 2 行）；
- 情绪环（扩面 A2）首两拍落库：prediction_log id=1571/1572，degraded=False；
- 竞价命中（扩面 A3）：窗外诚实 skipped（10:00-10:30 闸生效，14:05 now=14:05:12 实证）。

### 2b. 盘后段（16:35 数据落地 → 16:52 事件链自动 9 棒 → 17:30 总扳手 full 补漏+实证）
- **16:52 自动链实录**（调度器日志）：[REGIME-SNAPSHOT] 体检 09-21 → [JUDGMENT-SETTLE]
  intraday scan=4 settled=4 / next_day scan=1 settled=1 / daily_plan pending=1（新预案 grace 正确）
  → pf_alloc:09-21 → **[DAILY-DECISION] 拍板完成 target=2026-09-22 state=expansion@1.00
  cap=60.00% no_trade=0(-) packages=∅ degraded=1(D2:L2) 投递=ch_committed**；
- close_verifier 16:52 写 session 09-21 EOD 验证行（联结 plan_date:09-18 最新修订行）；
- 17:30 总扳手 full 16 段：见 §3 终数（TBD 终圈后填）。

### 2c. 修复行演进实录（验证环自愈节奏实证）
- 修订行 01M30BBDM（05:38 建行）→ 13:10 被未知源写 unresolvable（调度器日志无结算行为，
  疑似挖矿子代理触写，存疑已记录）→ 但其验证行 16:52 正常联结；
- 补发修订行 01M31K3WZ（16:5x）→ 立即 verify_for_session：**actual=S3_oscillation，
  plan_quality=0.73872，n_hits=1** → brier 结算按 T+1 grace 由明日自动链落地（环的自然节奏）。

## 3. 台账前后行数对照（05:00 基线 → 17:35 终态）

| 表 | 跑前 | 跑后 | 新增 | 备注 |
|---|---|---|---|---|
| judgment_intraday_market_state | 4 | 8 | +4 | 今日 10:30/11:30/14:00/15:00 四 bar（事件链自动+采样幂等） |
| judgment_next_day_forecast | 3 | 4 | +1 | 09-21 行（16:52 自动链产，已结算 settled=1） |
| judgment_daily_plan | 2 | 6 | +4 | 含修订行×3+今晚新预案（09-21 建，服务 09-22） |
| judgment_plan_verification | **0** | **6** | **+6** | **历史首行+盘中命中行+EOD 定格行——验证环从 0 到常态** |
| c1_backtest.decision_daily | 45 | 49 | +4 | 含 09-21 强制重拍+09-22 自动拍板（均 expansion@1.00 cap=60% no_trade=0） |
| c1_backtest.regime_snapshot_history | 3621(max 09-15) | 3624(max 09-18) | +3 | 本班 05:09 逃生口补印（断供修复） |
| c1_backtest.alloc_budget_daily(trade_date≥09-18) | 2 | 4 | +2 | 09-21 数据日 run（16:52 自动链） |
| prediction_log | 17 | 25 | +8 | **scenario_plan×3（史上首批）+sentiment_score×4+outcome×1（史上首行 outcome 回写）** |

**17:30 终圈 16 段实录**：15 ok+1 skipped（auction 窗外诚实跳）+0 error。亮点：warroom
postmarket=ok（09-21 scenario outcome 回写落地）；attribution sample_size=1（W0 归因开始
吃真数据）；classify=frozen_by_eod（EOD 冻结闸生效）；close_verify=already_verified（16:5x
手动验证被幂等识别）；decision=skipped_marker（自动链 16:52 已拍板，总扳手不重复）。

## 4. 零下单声明
- 全链仅写判定台账/验证/结算列/决策快照/预测日志（记录面）；拍板体=#305 安全态
  （GRADUATED_PACKAGES 恒空，enabled_packages=∅，不产执行单）；盘中段只读记录不换策略。

## 5. fail-open/fail-closed 实弹
- fail-closed：--data-date 2026-12-31 → 数据就绪门整圈阻断（kline_index_missing_date），零写入；
- fail-open：单测注入 warroom 炸段 → 留痕继续，summary 计 error（test_stage_fail_open_continues）。

## 6. Owner 扩面令施工实录（09-21 下午）
- 挖矿三路→清单 01_unwired_inventory.md（A/B/C/D/E/F 六类）；
- A 类四段入总扳手：llm_premarket（deepseek-v4-flash-0731 经 LSG 实测 success×2：09-18+09-21）、
  sentiment_loop（4 拍 4 行 prediction_log）、auction_hit（窗外闸实测）、similar_day+attribution
  （postmarket 观察，attribution 已吃 scenario_plan outcome 真数据）；
- B 类两钩子上事件链：maybe_run_warroom_pipeline + maybe_record_auction_hit（唤醒词/时窗/
  记号三重过滤，4+5 单测全绿；生效于 DataScheduler 下次重启——运行中进程不热载，今日由
  总扳手兜底）；
- C 类六件设计稿 wiring_proposals_*.md×3（18 批点全呈 Owner 未代批）；
- 两圈总测：09-18 圈 11/11 → 扩面后 17:30 圈 15 ok+1 skipped+0 error。

## 7. 两轮循环检查（段D）
- 第一轮：pytest 43 用例（总扳手5+扩面钩子4+pipeline_events 34）+ ruff 双文件；
- 第二轮：终圈后复跑（数字见终版提交前记录）；两轮零回归零新问题。
