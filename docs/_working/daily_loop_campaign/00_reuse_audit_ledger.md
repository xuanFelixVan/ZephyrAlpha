---
ttl: task_bound
session: st-dloop-20260921
issue: DLOOP-V2-REUSE-AUDIT
completes_when: 段B 补缺按本账结论执行完毕、E2E 一圈落地
---

# 00 对账总账（段A）——丁线日循环通电线 v2

> 铁律：每环节动手前先查已建成证据，已建成=REUSE 续用禁重做（裁定#390 前科）。
> 对账时间：2026-09-21 04:30-06:00；方法=四路只读审计子代理（蓝图/plan_engine/编排器/状态配比T）+ 主会话 DB 实测（表行数/幂等记号/调度器日志/运行痕迹）。

## 1. 排班链路环节级对账总表

| # | 环节 | 在不在 | 挂没挂 | 跑没跑 | 台账行数 | 判定 |
|---|------|--------|--------|--------|---------|------|
| 1 | 数据面（kline_daily/index/etf_60min） | ✅ | ✅ DataScheduler+43计划任务 | ✅ 09-18 齐（5558股+595指数） | — | REUSE |
| 2 | regime_snapshot_history（HMM 7态，编排器S2输入） | ✅ fw_backtest.ensure_regime_snapshot | ✅ 事件链第1棒 | ⚠️ 印到09-15后停（阈值错位，见§4） | 3621行 max=09-15→本班补印09-16~18 | STALE（已修） |
| 3 | regime_state_anchored（vol_pct 4档结构轴） | ✅ anchored_state_machine | ✅ tasks.yaml anchored_state_build | ✅ | 2235行 max=09-18 新鲜 | REUSE |
| 4 | daily_plan（MOD-PLAN-030 晨间预案） | ✅ | ✅ 事件链（Phase 2b 首棒） | ⚠️ 09-17/18 各1行（疑似手动/事件痕迹） | 2行 | REUSE |
| 5 | scenario_classifier（MOD-PLAN-031 盘中归类） | ✅ | ✅ 事件链（60min bar 唤醒） | ❌ 零产出痕迹 | verification 0行 | REUSE（未实证，E2E验） |
| 6 | close_verifier（MOD-PLAN-032 收盘验证定格） | ✅ | ✅ 事件链（daily_kline 唤醒，序先于结算） | ❌ 零产出 | verification 0行 | REUSE（未实证，E2E验） |
| 7 | judgment_settler（MOD-PLAN-027 三表结算） | ✅ | ✅ 事件链+人工逃生口 settle_all() | ⚠️ 记号落了09-17/18，结算列未见回填 | — | REUSE（E2E验） |
| 8 | intraday_l1_tracker（MOD-PLAN-028 盘中五态） | ✅ | ✅ 事件链（60min bar 唤醒，bar_key 幂等） | ✅ 09-18 盘中4行（10:30/11:30/14:00/15:00） | 4行 | REUSE（缺口③实为已挂——原判"零调用方"过时） |
| 9 | next_day_forecaster（MOD-PLAN-029 次日概率） | ✅ | ✅ 事件链（daily_kline 唤醒） | ✅ 09-17/18 各有行 | 3行 | REUSE |
| 10 | daily_warroom_pipeline（MOD-PLAN-018 scenario_plan族） | ✅ | ❌ **全仓零调用方**（自称挂57号SOP环节④，无接线实证） | ❌ prediction_log 仅17行且全是 boundary_revision（08-21） | scenario_plan 0行 | **GAP（缺口② warroom 段=真缺口）** |
| 11 | 日度编排器 daily_decision_orchestrator（MOD-BT-214） | ✅ | ✅ 事件链末棒（结算/验证/分配/账本后才拍板） | ✅ 09-18 晚跑出 09-21 决策行 | 45行（44行=09-16测试簇+1行09-21 no_trade=1 regime_missing） | REUSE（安全态=#305，GRADUATED_PACKAGES 恒空，禁手填） |
| 12 | pf_alloc 分配链（maybe_emit_pf_alloc_daily） | ✅ | ✅ 事件链（先于账本/拍板） | ✅ 09-18 alloc-2026-09-18-82cb50 落地 | alloc_budget_daily 有 run | REUSE（缺口⑤"接线"条件已满足——已在接线状态） |
| 13 | PP-001 配比 | ✅ TDM yaml L4549-4583 16 sleeves（proposed；六条verified起步0.05，后全域×0.90=0.045） | ✅ 消费端 fw_composer/pf_alloc allocation_inputs 只读 | — | — | REUSE（权重≠verified，是 proposed 先验） |
| 14 | 判定台账四表 | ✅ DDL 在产 | — | — | **4/3/2/0**（#388"近空"实锤；0=verification 从未闭过） | 缺口②验证环=真缺口 |
| 15 | T 管道（tick_t0/tick_matrix） | ✅ 文档战役资产已封存 | ❌ 禁重做（#331 做T砍+ #390 五卡全测毕，复活唯一口=新假设新卡快签） | 已终局 | — | 封存勿动（策略槽空置） |
| 16 | cohort_daily_ledger | ✅ src/zephyr/alt_data/ | ❌ 未接线（头注自证"二期由总统筹接线"） | — | — | 挂起（投产=Owner 门位） |
| 17 | intraday_tomorrow_forecast（MOD-PLAN-025） | ✅ design | ❌ 三消费点全未接线 | — | — | 挂起（与做T无关，勿被名字误导） |

## 2. §2 起点清单七项逐项结论

1. **蓝图四件套**：全在。增补件已并入蓝图§十一（2026-09-17），真源=蓝图单本。蓝图间矛盾5处已提炼（六态vs五态枚举未定义映射→缺口④路由表稿必须补；decision_daily 已建勿按草案DDL重写）。
2. **生产管线**：plan_engine 36 模块全活，`daily_warroom_pipeline.run_daily_warroom_pipeline(data_date, phase=)` 入口完整可手动跑；但 scenario_plan 族**零接线零产出**——五缺口里唯一"模块级真缺挂接"。
3. **编排器 v1**：本体=`strategy_pipeline/daily_decision_orchestrator.py`（不在 trading/ 下，conductor/autopilot 是 AI 任务认领族勿混）。安全态=全链跑流程不交易（#305：包集恒空+不产执行单+盘中修订权 Owner 保留）。**不缺、已挂末棒**。
4. **状态序列**：双轴并跑——anchored（新鲜）+ HMM 7态（断供已修）。TDM yaml 有他会话 staged 在途，绝对只读。
5. **PP-001**：真源 TDM portfolio_plan（fw-tdm-current 是生成器旧快照少 097/027 两 sleeve，一代 drift 属幂等设计内，等 TDM 落地后 --check 核对，本班不核）。
6. **T 管道**：封存。**裁定号勘误：砍做T=#331（原#304撞号改号），#304 现为 regime HMM 锚定重校准（regime_detector.py 代码绑定）**。引用"#304砍做T"=旧口径。
7. **验活命令四查**：台账四表 4/3/2/0；warroom 最近运行=无（prediction_log 无 scenario_plan 行）；43 计划任务+tasks.yaml 双查=零日循环条目（DataScheduler 常驻是事件链物理入口）；挂接真面=事件驱动 9 棒（见§3）。

## 3. 触发面真相（比"纯手动零触发"乐观得多）

DataScheduler 常驻（计划任务 5 分钟拉起）→ `task_completed`（唤醒词 daily_kline/kline_daily/kline_index）→ pipeline_events 9 棒顺序：
①regime刷新 → ②daily_plan → ③盘中归类 → ④收盘验证（序契约：先于结算）→ ⑤三表结算 → ⑥盘中L1 → ⑦次日概率 → ⑧pf_alloc → ⑨编排器拍板（末棒）。
**判定族+编排器已半自动**；缺的只有 warroom scenario_plan 族一棒 + 时序板上的"真日转"因 regime 断供退化成 no_trade。

幂等记号时间线（.runtime/strategy_pipeline/last_audit.json）：
- 09-16 15:07Z regime:2026-09-15 → 全窗印制成功（run VAL-P0-20260916-230726 已归档）
- 09-17 11:46Z regime:2026-09-16 → "fresh 滞后2日"零印制
- 09-18 00:41Z settle:09-16 / 00:42Z alloc:09-16 → 结算+分配跑了
- 09-18 08:34Z regime:2026-09-17 + settle:09-17 → "fresh 滞后3日"零印制
- 09-18 08:34Z pf_alloc:2026-09-18 → alloc-2026-09-18-82cb50 落地
- 09-18 11:11Z decision-2026-09-18-491f37（trade_date=09-21）→ no_trade=1 regime_missing
- 09-18 08:34Z regime:2026-09-18 → "fresh 滞后3日"零印制

## 4. 头号病灶诊断：regime 断供根因链（已修+待Owner治本）

**现象**：regime_snapshot_history 冻结在 09-15 → 编排器 D1 fail-closed → 09-21 决策行 no_trade=1 regime_missing。

**根因=供需阈值错位**（调度器日志实锤：`[REGIME-SNAPSHOT] 刷新体检 action=fresh 滞后=2/3日`三次零印制）：
- 供给方闸门：`fw_backtest._REGIME_STALE_DAYS=3`——滞后≤3天判"fresh"直接返回，不重印；
- 消费方（编排器 D1，蓝图：27）：regime 快照滞后 >1 交易日=fail-closed no_trade。
- **滞后 2~3 交易日的死亡窗口**：供给方说新鲜、消费方说缺失，且无任何一方有义务补——链路结构性断供。

**本班处置**：补印走官方逃生口 `print_regime_history.py --start 2026-09-16 --end 2026-09-18`（不受幂等闸约束）→ 表恢复新鲜 → 编排器可出非降级行。**治本（改 _REGIME_STALE_DAYS=1 或编排器放宽，属 fw_backtest.py=strategy_pipeline 域，非本班写域）→ Owner/治理线清单**。

**次生病灶（本班自伤自清）**：dry-run 会在 runs/ 留未归档 run 挡死 create_run（SOP-D §9.6 禁双 run），本班 VAL-P0-20260921-050255 已删（零行可复现，qa 报告路径留档 .runtime/tmp/regime_reprint_0916_18.log）。

## 5. 真缺口重定义（段B施工依据）

| 原缺口单 | 对账后真身 | 段B动作 |
|---------|-----------|--------|
| ①触发面总扳手 | 真缺：无单一入口手动跑全链；warroom 棒未挂 | 建 `plan_engine/daily_loop_master_switch.py`：串 regime体检补印→warroom→daily_plan→盘中→验证→结算→拍板，幂等可重跑，不挂调度器 |
| ②验证环历史闭环 | 真缺：verification 0 行（判定器写行从未发生，非结算器坏） | 总扳手对 09-18 圈显式调 classify+verify+settle 补历史欠账 |
| ③intraday_l1_tracker 接线 | **原判过时**：已挂事件链且有 09-18 盘中4行 | 不接线；总扳手盘中段=手动触发等价钩子（tick/分钟只读记录） |
| ④路由表 v1 设计稿 | 真缺：六段↔五态映射全仓无定义 | 出 routing_table_v1_draft.md（TDM 矩阵+bizmine 判定+PP-001 原料；config 落地=Owner 门） |
| ⑤pf_alloc 接线 | **条件已满足**：事件链已在接线状态（09-18 实跑落地） | 不动；触发路径说明入 Owner 清单（#257② 口径=已触发无需再接） |

## 6. 对账中新发现资产（禁漏）

- `maybe_settle_judgment_ledger`/`maybe_track_intraday_state`/`maybe_emit_next_day_forecast`/`maybe_emit_daily_plan`/`maybe_classify_intraday_scenario`/`maybe_verify_plan_close`：pipeline_events 已注册的全套钩子，总扳手复用其函数本体（同参数签名 `task_id=唤醒词, success=True`），禁另写平行实现。
- MOD-PLAN-016 撞号（execution_deviation_attributor 与 similar_day_evaluator 同号）→ depgraph 治理清单。
- fw-tdm-current 与 TDM 一代 drift（少 097/027）→ 等 TDM staged 落地后 `generate_framework_plan_from_tdm.py --check`。
- 时序板：乙线 00:30-05:30 F→G 镜像（CH 零影响）；本班 CH 小量写避开 02:30 夜跑带即可，已合规。

## 7. 证据索引

- 表行数实测：judgment 四表 `4/3/2/0`（c1_market，2026-09-21 05:00）；decision_daily 45 行；prediction_log 17 行（max trade_date 2026-08-21）；regime_state_anchored 2235 行 max=09-18；regime_snapshot_history 3621 行 max=09-15（补印前）。
- 幂等记号：`.runtime/strategy_pipeline/last_audit.json`；决策记号：`daily_decision_marker.json`。
- 调度器日志：`tmp/scheduler_run.log*`（09-18 08:41/16:34 两条"刷新体检 action=fresh 滞后=3日"=阈值错位实锤）。
- 四路审计子代理全报告：见本班交接包（蓝图摘要/36模块枚举/编排器双查/状态配比T验活）。
- 关键代码锚：pipeline_events.py:835-896（9棒钩子序契约）、daily_warroom_pipeline.py:359（run入口）、daily_decision_orchestrator.py:122（GRADUATED_PACKAGES 恒空）、fw_backtest.py:1111（ensure_regime_snapshot）、judgment_settler.py:550（settle_all）、close_verifier.py:184（verify_for_session）。
