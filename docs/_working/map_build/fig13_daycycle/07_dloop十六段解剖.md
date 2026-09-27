---
ttl: task_bound
completes_when: 图13 施工令下发且 D13-32/33/34 三格的节点字段可由生成器从本簿坐标抽出后，本件转"待消费"归档
title: 图13 簿07·dloop 十六段解剖（D13-32 D13-33 D13-34）——本图最大节点
owner: st-mapbuild-20260924 车道 W-I
---

# 07_dloop十六段解剖

> 车道 W-I｜2026-09-24 15:32（周四交易日，盘中段后、16:30 日K线层前）实测。
> 覆盖环节：**D13-32 日循环总扳手 / D13-33 收盘验证→三表结算 / D13-34 日度拍板**。
> 一句话族职责：把一条被排班的进程内链（16 段）拆到"每段可指认执行体、每段可判幂等与失败语义、每段可查最近是否真产出"的粒度，并实测图13↔TDM 的切分线在哪几段真切开、在哪几段切不开。
> 骨架坐标：`docs/_working/map_build/fig13_daycycle/00_skeleton.md` 第 0.1 节第 2 行（融合处置）、第 2 节 D13-32/33/34 三行、第 3 节切分表第 1 行。
> 本簿**不改骨架**；骨架外发现全部登记在末尾「溢出条目」交总包。

## §0 覆盖清单与三件前置实测

| 环节 | 一句话 | 本簿状态判定 |
|---|---|---|
| D13-32 | 16:45 `dloop_post` 特殊槽跑 `run_daily_loop(None)` 全 16 段 | ✅（三证齐，见 1.6） |
| D13-33 | postmarket 内 `close_verify` 恒先于 `settle` 的钩子序契约 + 三表结算落点 | 🔨（序契约成立，但 09-23 plan 未结算） |
| D13-34 | 末段 `decision` 拍板；GRADUATED_PACKAGES 恒空→结构性无实盘 | ✅（常量+实数据双证，见 3.2） |

**前置纠偏 A｜段数**：`PHASE_STAGES` 直接 import 实测 = `premarket 5 / intraday 4 / postmarket 8 / full 16`。
普查"十环节"**不成立**；docstring 叙述的"11 棒"（`daily_loop_master_switch.py` 第 24-29 行）也**不等于**段数——它是"复用的既有产出者棒数"叙述口径。三数并存（10/11/16）是本节点最大的考古债，见 1.7。

**前置纠偏 B｜常量位置**：骨架 D13-34 行写 `daily_loop_master_switch.py:239-243,44-45`。实测 `:44-45` 是**docstring 里的零下单声明**，`GRADUATED_PACKAGES` 常量**不在本件**，定义于 `src/zephyr/strategy_pipeline/daily_decision_orchestrator.py:122`。引用真源须改指后者，否则施工期 `ready_gate` 指针会落到注释上。

**前置纠偏 C｜幂等真源不在编排层，但"段状态"也不在底层**：编排层零自建键成立（第 8 行 INVARIANTS 自证，`dispatch` 表第 402-419 行确无幂等码）；然而 16 段里 **11 段的返回 `status` 是硬编码字符串 `"ok"`**（详见 1.3 的"状态硬编码"列），底层钩子的六态 `action` 被压成 ok。于是"段级失败可见性"两边都没有——本战役最值钱的一类发现（断供静默）在 dloop 的内部版本。

---

## §1 D13-32 日循环总扳手（16 段逐段解剖）

### 1.1 上（谁触发本环节、输入从哪来）

| 触发路 | 载体 | 实测 |
|---|---|---|
| 自动圈（唯一在册自动路） | APScheduler 特殊槽 `dloop_post`，cron `45 16 * * 0-4`，executor default，max_instances=1 | `src/zephyr/data/config/schedule.yaml:247-253`（注释含原 MANUAL-ONLY 解除留痕）；`src/zephyr/data/scheduler.py:366-433` 为唯一 handler |
| 人工逃生口 | `run_daily_loop(...)` 编程式入口 + `__main__`（无 argparse，门禁合规先例） | `daily_loop_master_switch.py:371-373`、`:440-441`；`docs/_working/daily_loop_campaign/e2e_manual_run_report.md` |
| 总闸 | `data/runtime/daily_loop_master.disabled`（每次触发实查，即时生效） | `scheduler.py:367-370`；本会话实查**不存在**=开着 |
| 日历闸 | **无**——`dloop_post` 不在 `TRADING_DAY_GUARDED_SCHEDULES` | `src/zephyr/data/trading_calendar.py:151-163` 实测 9 槽：intraday_realtime / intraday_minute / daily_kline / daily_capital / daily_event / nightly_financial / daily_backfill / integrity_check / auction_highfreq。法定假日空跑由 schedule.yaml:249-250 注释自陈"由底层幂等闸+数据就绪门（fail-closed）吸收" |
| 输入日 | `data_date=None` → `resolve_pf_alloc_trade_date()` = **行情最新入库日**（禁墙钟猜日） | `daily_loop_master_switch.py:378-381`；本会话实测返回 `'2026-09-23'`（今日 09-24 的日K线尚未产） |

**输入日语义是本节点第一处结构性风险**：16:45 圈解析的是"已入库最新日"，若 16:30 `daily_kline` 槽（heavy 池、实测挂 36 任务）延后或未产，整圈就在 **T-1 业务日**上重放一遍——每段的幂等闸全部命中 `already_emitted`，`fetch_perf` 仍记 SUCCESS。第 1.6 节用两圈的 elapsed 差把这个机制量化了。

### 1.2 段表（本簿主体；16 段逐段）

列义：**唤醒**＝编排层塞给底层钩子的 `task_id`（编排层自造，非真实事件唤醒词）；**幂等**＝底层查重判据；**失败语义**＝该段异常/返回非 ok 时整圈怎么办；**状态硬编码**＝编排层是否无条件写 `"status":"ok"`（是→底层六态被压平）。

| # | 段名 | 执行体（本文件行→被委托件行） | 唤醒 | 幂等判据 | 失败语义 | 状态硬编码 | 输出落点 |
|---|---|---|---|---|---|---|---|
| 1 | `data_readiness` | `:164-168` → 读 `c1_market.kline_index` max(trade_date)（`:89,:101-102`） | — | 纯读，无键 | **fail-closed**：max<data_date → `:429-433` 置 `blocked` 并 `break`（全圈唯一 break 点） | 否（可返 error） | 无（只判） |
| 2 | `regime_freshness` | `ensure_regime_fresh :127-158` → 子进程 `scripts/backtest/print_regime_history.py --start <max\|prev_bd> --end <data_date>`（`:142-147`，timeout 1800s） | — | 阈值判据：`max(trade_date) >= 前一交易日` 即 no-op（`:137-138`）；补印按缺口窗 | fail-open：`rc!=0` 或未追平 → `status=error` 留痕，**不 break** | 否 | `c1_backtest.regime_snapshot_history` |
| 3 | `warroom` | `_stage_warroom :171-180` → `daily_warroom_pipeline.run_daily_warroom_pipeline:359`；phase→wp 映射 `{"full":"both"}`（`:174`） | — | 业务日记号 `warroom_pipeline:<D>` **先落再动手** + `prediction_log UNIQUE(trade_date,module,prediction_type,input_hash)` 双保险（`pipeline_events.py:896-899`） | fail-open | 否（但只回 premarket/postmarket 两子状态） | `prediction_log`（governance.db）type=`scenario_plan`/`outcome` |
| 4 | `daily_plan` | `_stage_daily_plan :183-194` → `daily_plan.maybe_emit_daily_plan`（`daily_plan.py:723` 为 emit 体） | `daily_kline`（`_WAKE_DAILY :69`，编排层伪造传入） | `_SQL_ALREADY_EMITTED`：`module_id AND inputs_ref LIKE '%plan_date:D\|%'`；**直调 `emit_for_trade_date` 绕过查重**（`:186-188` 自证） | fail-open | **是**（`:189` 无条件 ok） | `c1_market.judgment_daily_plan` |
| 5 | `llm_premarket` | `_stage_llm_premarket :249-271` → `LLMRuntimeGateway().infer("premarket_analysis")` + `llm_premarket_analysis.run_llm_analysis:1672` | 注入 client | `UNIQUE(trade_date, model_version, prompt_version, input_hash)` 保首条（该件 INVARIANTS 第 8 行）；`llm_client=None` → `status=skipped_not_wired` 仍落库 | fail-open（网关构造失败→本段 error，:252-253 自陈） | **是**（`:271` ok） | `governance.db.llm_daily_analysis` |
| 6 | `next_day` | `_stage_next_day :197-201` → `next_day_forecaster.maybe_emit_next_day_forecast`（生成于 `:407-412`，骨架件 `judgment_ledger.run_judgment_emit_hook:508-559`；emit 体 `:319`） | `daily_kline` | `inputs_ref LIKE '%trade_date:D\|%'`（`next_day_forecaster.py:126-131`，注释记 2026-09-17 首键漏 `\|` 致幂等三连发事故） | fail-open | **是**（`:201` ok） | `c1_market.judgment_next_day_forecast` |
| 7 | `pf_alloc` | `_stage_pf_alloc :204-208` → `pipeline_events.maybe_emit_pf_alloc_daily:745` | `daily_kline` | 业务日记号（本件第 26 行 docstring 称"记号幂等"） | fail-open | **否——全链唯一按 rc 判定的委托段**（`:208` `out.get("rc",0)==0`） | `c1_backtest.alloc_budget_daily` |
| 8 | `intraday_l1` | `_stage_intraday_l1 :211-215` → `intraday_l1_tracker.maybe_track_intraday_state:585` | `kline_etf_60min`（`_WAKE_60MIN :68`，编排层伪造） | `bar_key` 查重（`pipeline_events.py` 注释：60min bar 到达=自然唤醒，bar_key 幂等） | fail-open | **是**（`:215`） | `c1_market.judgment_intraday_market_state` |
| 9 | `classify` | `_stage_classify :218-222` → `scenario_classifier.maybe_classify_intraday_scenario:367` | `kline_etf_60min` | 模块内情景记号（未取到行号，见 1.8 待补） | fail-open | **是**（`:222`） | 盘中情景归类（该件读写面未逐行核） |
| 10 | `sentiment_loop` | `_stage_sentiment_loop :274-291` → `data/intraday_sentiment_loop.run_once:331` | 无参 | **无业务日记号**——每次调用即一拍；仅 `prediction_log` UNIQUE 内容 hash 兜 | fail-open（该件 INVARIANTS 自陈"任一 I/O 边界单次失败→errors 留痕不抛"） | **是**（`:285`） | `prediction_log` type=`sentiment_score` |
| 11 | `auction_hit` | `_stage_auction_hit :294-313` → `auction_hit_recorder.record_auction_hit:307`；窗闸 `_AUCTION_WINDOW=(10:00,10:30)`（`:73`，判据 `:304-311`） | 墙钟实查（非唤醒词） | 业务日记号 `auction_hit_daily:<D>` 先落再动手 + 内容 hash（`pipeline_events.py:934-935`） | fail-open；**窗外恒 `status=skipped`** | 否（skipped 计入 skipped 桶） | `prediction_log` type=`auction_hit` |
| 12 | `close_verify` | `_stage_close_verify :225-229` → `close_verifier.verify_for_session:184`（事件路另有 `maybe_verify_plan_close:253`） | — | 验证行按 plan_judgment_id 追加（MergeTree 只增） | fail-open | **是**（`:229`） | `c1_market.judgment_plan_verification` |
| 13 | `settle` | `_stage_settle :232-236` → `judgment_settler.settle_all:550`，遍历 `JUDGMENT_TABLES`（`judgment_ledger.py:150`） | — | 回填带 `WHERE evaluated_at IS NULL` 双闸（重复回填第二次扫不到未结算行，该件 INVARIANTS 第 8 行） | fail-open（但底层 `get_client_strict` CH 异常严格上抛→本段 error） | **是**（`:236`） | 三表结算列组（mutation） |
| 14 | `similar_day` | `_stage_similar_day :316-321` → `similar_day_evaluator.evaluate_similar_day_hit_rate:299` | — | 纯只读，零写库（`:317` 自陈） | fail-open | **是**（`:321`） | 无（返回报告对象被截 300 字符留痕） |
| 15 | `attribution` | `_stage_attribution :324-332` → `scenario_attribution_stats.compute_scenario_attribution:312`，`window_days=20`，`as_of=data_date` | — | 纯统计只读 | fail-open | **是**（`:332`） | 无 |
| 16 | `decision` | `_stage_decision :239-243` → `daily_decision_orchestrator.run_daily_decision(data_date, force=force_decision)` | — | trade_date 快照行 + `force` 显式重拍逃生口（本件第 29 行） | fail-open | **是**（`:243`） | `c1_backtest.decision_daily` |

**四相切片**（`:337-368` 全量）：
- `premarket` 5 = data_readiness, regime_freshness, warroom, daily_plan, llm_premarket
- `intraday` 4 = intraday_l1, classify, sentiment_loop, auction_hit
- `postmarket` 8 = close_verify, warroom, next_day, pf_alloc, settle, similar_day, attribution, decision
- `full` 16 = premarket 5 + next_day, pf_alloc + intraday 4 + close_verify, settle, similar_day, attribution, decision

**四相不等价（新实测）**：`full` ≠ 三相并集按时序串接。① `warroom` 在 premarket 与 postmarket 各出现一次，`full` 只出现一次（第 3 位），靠 `:174` 的 `{"full":"both"}` 映射把两个角色折进一次调用——于是 **postmarket 相里 warroom 在 close_verify 之后（第 2 位），full 相里它在 close_verify 之前（第 3 vs 12 位）**，同一段在两相的因果位置相反。② `full` 无 `intraday` 相的 bar 语义：8/9/10/11 段拿的是伪造唤醒词 + 墙钟窗闸，16:45 跑时盘中性态已闭。

### 1.3 内（子模块/自动化程度清单）

16 段的委托件全清单见 1.2 第 3 列；自动化程度分三档实测：

- **全自动（16:45 圈真跑到并有产出留痕）**：段 1/2/3/4/5/7/8/10/12/13/16（11 段）。
- **自动但恒不产出（结构性）**：段 11 `auction_hit`——16:45 恒在 10:00-10:30 窗外→永久 `skipped`；能力活在事件链（见 1.5 与溢出 E-2）。
- **自动但幂等吸收成空转**：段 4/6/7 在"业务日未推进"的圈里全部命中 `already_emitted`，零写库零 error（=SUCCESS 空圈）。
- **只读诊断（无产出面可查）**：段 14/15——**这两段的"最近执行证据"当前形态不可得**，只能证明被调用过（`fetch_perf.rows=16` 说明循环走到了它们）。
- 编排层自身不含业务判断：`dispatch` 表 16 行全部 lambda/函数引用（`:402-419`），无 if/elif 链（查表派发，`:401` 注释自证 NO-HIGH-COMPLEXITY 合规）。

### 1.4 下（输出给谁）

| 输出 | 消费方 | 实测读数 |
|---|---|---|
| `report`（JSON） | ①`scheduler.py:394-425` 写 `fetch_perf` + 未全绿走 `Alerter.notify(level=ERROR)`；②人工逃生口 `print` | `D:/ZephyrAlpha/.runtime/fetch_perf/fetch_perf_YYYYMMDD.jsonl`（`.runtime` 落地区，主区只读） |
| `judgment_daily_plan` | `close_verify`（段 12）、`settle`（段 13）、Phase-5 归因 | 8 行，plan_date 覆盖 09-15/09-18/09-21/09-22/09-23 |
| `judgment_next_day_forecast` | `daily_plan`（作为 `forecaster:` 输入） | **4 行，业务日最新 09-18**（断供，见簿 09 D13-44） |
| `judgment_intraday_market_state` | `settle`、盘中 L1 消费链 | 20 行；09-18/21/22/23 各 4 行，09-24 已 4 行（未结算，horizon 未到） |
| `judgment_plan_verification` | 偏离归因、情景达成度 | 13 行；09-21 6 / 09-22 2 / 09-23 3 / 09-24 2 |
| `alloc_budget_daily` | `decision`（段 16）当日预算来源 | 18 行；trade_date 09-21 2 / 09-22 4 / 09-23 2 |
| `decision_daily` | Owner 每日拍板核对、仪表盘 | 69 行；最新 trade_date=09-24（asof_data_date=09-23） |
| `prediction_log`（governance.db） | `similar_day`（段 14）、`attribution`（段 15）、M3 情景注解 | 32 行；scenario_plan 5 / outcome 3 / sentiment_score 6 / auction_hit **1** / plan_revision 17 |

### 1.5 旁（撞车面与切分线实测——图13 存亡线）

骨架裁定口径：**段序/幂等/fail-open 归图13，decision_question 归 TDM**。本节逐段实测这条线切不切得开。测法=拿每段委托件的 `MOD-*` 与 `module_ref` 去 `config/trading_decision_map.yaml` 找接盘位（182 节点全扫，机生可复跑）。

| 段 | TDM 有无接盘位 | 实据 | 切分判定 |
|---|---|---|---|
| 3 `warroom` | **有** | `TDM-E-L0 盘前作战计划 / activation=premarket / point=盘前 / module_ref=src/zephyr/plan_engine/daily_warroom_pipeline.py / module_id=MOD-PLAN-018 / ai_autonomy=daily_review` | **切得开**：图13 只留时点+幂等+序，判什么走 `tdm_ref: TDM-E-L0` |
| 16 `decision` | **有（且是运行时直读）** | `daily_decision_orchestrator.py` 常量区 `_TDM_CONFIG="config/trading_decision_map.yaml"`、`_STATE_NODE="TDM-E-L1"`；实数据 `decision_daily.package_set_json.source_cell` = `"TDM-E-L1\|expansion"` | **切得开且已被代码兑现**：判据真源就是 TDM 的 state_matrix 格，图13 只需 `tdm_ref: TDM-E-L1` |
| 7 `pf_alloc` | **有（运行时直读 PP-001）** | `daily_loop_master_switch.py:110-121 _pp001_snapshot()` 用 `load_pp001_plan(config/trading_decision_map.yaml)`；`TDM-F-C3-03 sleeve权重调权 / module_ref=pf_alloc/core/regime_meta_allocator.py` | **切得开**，但须写明"配比格 PP-001 与状态格 TDM-E-L1 是两处" |
| 12 `close_verify` | 半有 | `TDM-E-L0-03 收盘复盘与明日边界 / postmarket / module_ref=tomorrow_boundary_planner.py / MOD-PLAN-001`——decision_question 已含"复盘计划达成度"，但 `close_verifier.py`（MOD-PLAN-032）**无节点** | **切开一半**：达成度"判什么"归 TDM-E-L0-03，"何时验/验完接 settle"归图13；`tdm_ref` 只能指到近邻节点 |
| 4 `daily_plan` | **无** | MOD-PLAN-030 在 182 节点中零命中；只有 `TDM-E-L0-01 计划生成 / MOD-PLAN-011` | **切不开**（决策侧无人接盘）：这是"今天买什么"的正面决策 |
| 6 `next_day` | **无** | MOD-PLAN-029 零命中；`TDM-E-L0-04 明日情绪盘中滚动预测 / MOD-PLAN-025` 是**同问题的另一条腿**（盘内滚动），不顶替盘后发射 | **切不开** |
| 8 `intraday_l1` | **无** | MOD-PLAN-028 零命中 | **切不开** |
| 9 `classify` | **无** | MOD-PLAN-031 零命中 | **切不开** |
| 5 `llm_premarket` | **无** | MOD-PLAN-007 零命中；该件自陈"LLM 是分析参考注解层不是信号真源" | **切不开但可标注为注解段**（其输出只进 prediction_log M3 注解，不进决策链） |
| 13 `settle` | 无（也不需要） | MOD-PLAN-027 零命中；`TDM-E-L9-V1/V3` 挂的是 `judgment_ledger.py`（发射器 MOD-PLAN-026），非结算器 | **纯运营，图13 独占**：结算=事实回填，无 decision_question 可填 |
| 1 `data_readiness` / 2 `regime_freshness` | 不需要 | 无判据语义，纯闸 | **图13 独占** |
| 10 `sentiment_loop` / 11 `auction_hit` | 无 | MOD-DATA-063 / MOD-PLAN-015 零命中 | **混合**：节拍与窗闸归图13；"命中了什么/情绪是什么"归 TDM（当前缺位） |
| 14 `similar_day` / 15 `attribution` | 无 | MOD-PLAN-016 / MOD-PLAN-009 零命中；`TDM-F-C3 绩效归因反馈`（module_ref 为空=红节点）语义相邻不同粒度 | **图13 独占（诊断观测段）**，或让渡 F-C3 扩节点 |

**结论（诚实版，给骨架第 3 节的实测补充）**：
1. 切分线**在时序侧完全成立**——段序、幂等判据、唯二 fail-closed 点、窗闸、唤醒词伪造口径，TDM 一条都表达不了（`activation` 只有 5 值窗标签，182 节点里 `MOD-PLAN-*` 仅 9 个）。
2. 切分线**在决策侧只兑现了 3/16**（warroom / decision / pf_alloc）。若图13 施工即执行禁则一"判据唯一出路 `tdm_ref`"，则 **D13-32 的 8 段（daily_plan/next_day/intraday_l1/classify/llm_premarket/close_verify/sentiment_loop/auction_hit）会写出悬空 tdm_ref**。
3. **该让渡给 TDM 扩节点的段名（按决策含量从高到低）**：`daily_plan`（MOD-PLAN-030）、`next_day`（MOD-PLAN-029）、`intraday_l1`（MOD-PLAN-028）、`classify`（MOD-PLAN-031）、`close_verify`（MOD-PLAN-032，可挂 TDM-E-L0-03 下作子节点）、`auction_hit`（MOD-PLAN-015）、`llm_premarket`（MOD-PLAN-007，注解档）、`sentiment_loop`（MOD-DATA-063）。
4. **应留在图13 的段**：`data_readiness`、`regime_freshness`、`pf_alloc`（时点与记号部分）、`settle`、`similar_day`、`attribution`、`decision`（时点与 force 逃生口部分）、`warroom`（时点部分）。
5. 施工期落地建议（不改骨架，登记为总包请求）：`tdm_ref` 在图13 本体做成**可空 + 空值语义"决策侧待 TDM 扩位"**，别在建成日就把 8 段判成红节点——那会把 TDM 的排期债转嫁成图13 的假缺口。

**其他撞车面**：`docs/_working/daily_loop_campaign/00_reuse_audit_ledger.md` 是本节点的**上游蓝图真源**（模块头 `[BLUEPRINT]` 与 `[MODIFY-GUARD]` 双向指它），其第 27 行"11 日度编排器…REUSE（安全态=裁定#305，GRADUATED_PACKAGES 恒空，禁手填）"、第 96 行"关键代码锚"六处行号（`pipeline_events.py:835-896` 九棒钩子序 / `judgment_settler.py:550` / `close_verifier.py:184`）本簿逐条复核**全部在位**。

### 1.6 最近执行证据（✅ 第三证）

**自动圈全史（`fetch_perf` 扫 09-20~09-24 共 9,457 行，`capability=daily_loop_master` 命中 2 条）**：

| ts（本地） | status | elapsed_sec | rows(=段数) | 读法 |
|---|---|---|---|---|
| 2026-09-22 16:50:26 | SUCCESS | **326.218** | 16 | 走到 16 段（无 break=就绪门过），error=0 |
| 2026-09-23 16:45:33 | SUCCESS | **33.531** | 16 | 同一批段，**耗时 1/10**＝幂等全命中空转 |
| 2026-09-24（今日） | — | — | — | 15:32 实测未到 16:45，**无行属正常**，非断供 |

零非-SUCCESS 行（`grep -v SUCCESS` 输出为空）。

**段级证据（用 prediction_log 的 UTC `created_at` +8h 对齐两圈时间窗，逐段可指认）**：

| 段 | 落在哪一圈/哪条链 | 读数 |
|---|---|---|
| 3 warroom | 09-22 圈内：id 1608 `scenario_plan(09-23)` **16:49:43**、id 1609 `outcome(09-22)` **16:49:55**；09-23 圈外：id 1681 **16:33:59**（事件链抢在 16:45 前 11 分） | 双路并存实证 |
| 4 daily_plan | 09-22 行 asof **16:49:59**（圈内）；09-23 行 asof **16:33:54**（事件链） | 同上 |
| 5 llm_premarket | `llm_daily_analysis` trade_date 09-22 created **16:50:21**、09-23 created **16:45:31**，均 `status=success`、`model_version=qwen-flash`、`prompt_version=pm-v1.0.0` | **盘前段实跑在 16:45 圈**（为 T+1 的 08:00 cutoff 先产注解）——时点归属须写"盘前段盘后跑"，见溢出 E-3 |
| 7 pf_alloc | `alloc_budget_daily` trade_date 09-21/22/23 = 2/4/2 行（全表 18） | 在产 |
| 8 intraday_l1 | `judgment_intraday_market_state` 09-18/21/22/23 各 4 行 + 09-24 已 4 行 | 在产 |
| 10 sentiment_loop | id 1610 (09-22) **16:50:23**、id 1685 (09-23) **16:45:32**；09-21 另有 13:34/14:05/15:05 三拍（人工） | **自动圈下每交易日只 1 拍且在收盘后**→"有节拍席位无节拍"实证的精确形态 |
| 11 auction_hit | 全表 type=`auction_hit` **仅 1 行**：id 1693，created **2026-09-24 10:01:34**（今日盘中） | 两圈 16:45 均 `skipped`；唯一成功来自**事件链 `_AUCTION_WAKE_TASKS`（kline_etf_1min/5min）**，非 dloop→骨架 D13-20 须改判（溢出 E-2） |
| 12 close_verify | `judgment_plan_verification` 09-21 6 / 09-22 2 / 09-23 3 / **09-24 2（10:28、11:22 CST）** | 盘中即触发，非仅 16:45 |
| 13 settle | `judgment_daily_plan.evaluated_at`：plan_date 09-21 结算于 09-22 02:18:10 UTC、09-22 于 09-23 02:58:04 UTC；**plan_date 09-23 `evaluated_at=NULL`** | 结算在跑，但 T 日行按 horizon 要到 T+1 |
| 16 decision | `decision_daily` trade_date 09-22 / 09-23 / **09-24**（`asof_data_date`=09-21/09-22/09-23） | 拍板逐交易日在产 |
| 1/2 data_readiness、regime_freshness | 间接：`kline_index` max=2026-09-23（3,100,590 行）→ 09-23 圈 data_date=09-23；`regime_snapshot_history` max=**2026-09-22**（3,627 行），required_min=前一交易日 09-22 → 判 fresh 不补印 | 闸在位、当前未触发补印 |
| 14/15 similar_day、attribution | **不可得**：纯只读零写库，唯一旁证是 `rows=16` 说明循环走到底 | 只能证"被调用"，不能证"产出"→ 本图 `last_run_evidence` 字段的正当用例 |

**事件链 vs 自动圈的因果实证（本节点最重要的结构结论）**：同一批 `maybe_*` 钩子有**两个触发源**——① `pipeline_events.py:1020-1075` 挂在 `daily_kline SUCCESS` 的事件链（宪法 §9.3 合规的活路），② dloop 用伪造 `task_id="daily_kline"` 在第 16:45 圈重放。09-22 是 dloop 先产出（16:49），09-23 是事件链先产出（16:33:54）而 dloop 只补到一个 `sentiment_loop`（16:45:32，无记号段）→ 于是 **dloop 的"全链兜底"角色退化为"给无幂等记号的段重放一次"**，elapsed 33.5s 即其形状。**判 D13-32 的价值不能看 SUCCESS，要看 elapsed 与产物增量**（图13 施工建议：节点字段 `elapsed_sec` 与 `emitted_stages` 优于 `status`）。

**唤醒词过滤的真实语义**：`judgment_ledger.py:479-480` `_EMIT_WAKE_POINT_KEYS=("daily_kline","kline_daily","kline_index")`；dloop 传 `_WAKE_DAILY="daily_kline"` → **过滤在 dloop 路恒为真**（第 335 行注释"段序契约要求唤醒词过滤通过"即此意）。所以"唤醒词"在图13 里不是时点，是**一次人造的自然唤醒**。

### 1.7 史（dloop 演化考古）

| 时点 | 事件 | 实档 |
|---|---|---|
| 2026-09-16 | 蓝图与对账总账立件（缺口①=无总扳手） | `daily_loop_master_switch.py` 第 1 行 `[BLUEPRINT] MOD-PLAN-033`；`docs/_working/daily_loop_campaign/00_reuse_audit_ledger.md`；`docs/_working/trading_vision/2026-09-16-daily-orchestrator-blueprint.md` |
| 2026-09-17 | 日度编排器八点保守自裁（=安全态法源） | 在册 `docs/01_policies_and_standards/_registry/catalogs/ruling_registry.yaml:4162` 裁定#305，第 2 点写明"首版接入包集合=**空**…GRADUATED_PACKAGES 空集常量禁手填" |
| 2026-09-21 | 本件**诞生即为 16 段**，且声明 MANUAL-ONLY | commit `495f759903`（2026-09-21）标题实读："手动总扳手MOD-PLAN-033(**16段**,薄委托9棒既有产出者,MANUAL-ONLY零下单)…扩面A类四段(LLM盘前经LSG实测/sentiment_loop/竞价时窗/盘后双统计)…E2E两圈实证(**09-18圈11/11+09-21圈15ok**)…[MODIFY-GUARD]" |
| 2026-09-21 | Owner 批准解除 MANUAL-ONLY（申请单 A 项） | `docs/_working/daily_loop_campaign/owner_gate_list.md` 第 10-17 行："A. 日循环挂任务表批…**✅ 已批（Owner 2026-09-21）已施工**"，第 12 行原话含 **"MANUAL-ONLY-PERMANENT 门禁合规"**——原约束字面写的是 PERMANENT，九天后被同一 Owner 解除。第 15 行记定序依据"挂表=排期表动作，按裁定#388 口径归 Owner 门位"（在册 `ruling_registry.yaml:5175` 裁定#388「排班表/排期表二分口径定案…排程词退役」，2026-09-21） |
| 2026-09-22 | 解除**落地**（批准日≠施工日） | commit `be05d1b01f`（2026-09-22）："A=总扳手挂16:45特殊槽dloop_post（schedule.yaml+scheduler.py handler+总闸 daily_loop_master.disabled+永不反噬，nightly_sentiment 先例路径，**原MANUAL-ONLY约束Owner批解除**）；B=regime阈值治本 `_REGIME_STALE_DAYS` 3→1…+缺口窗重印（--start max+1 --end今天，治全窗重印整表翻倍隐性病，09-16实证翻倍）" |
| 同日 | regime 供需阈值错位=2026-09-15~09-18 断供根因 | 本件第 8 行 INVARIANTS 自陈 + `owner_gate_list.md` B 项"调度器日志 09-17/18 三条'刷新体检 action=fresh 滞后=2/3日'零印制 vs 编排器同日 regime_missing no_trade——**供给方说新鲜、消费方说缺失的死亡窗口**"。实码见证：`decision_daily` trade_date=2026-09-21 有一行 `no_trade=1 / no_trade_reason='regime_missing'`，同 trade_date 另一行 `no_trade=0`（重拍） |

**"十环节/11 棒/9 棒/16 段"四数并存的来龙**：普查"十环节"=骨架层口语；"9 棒"=对账定案"复用既有产出者"数（commit 495 标题与 `00_reuse_audit_ledger.md` 口径）；"11 棒"=docstring 第 24-29 行按行叙述的棒数（含就绪门/新鲜度体检/拍板，且未含 2026-09-21 扩面四段）；**16 段=`PHASE_STAGES["full"]` 唯一可机生数**。施工期图本体此格必须走 `import PHASE_STAGES` 抽取，禁抄任何散文数（根宪法 §9 条目 5 静态清单禁手工维护在本节点的直接应用）。

### 1.8 新（最新形态与外部对标）

- 最新形态：2026-09-21 扩面四段（LLM 盘前/sentiment/竞价时窗/盘后双统计）是**唯一一次段集变更**，此后段数稳定 16（本件行号 `:246` 起为扩面段区块，与骨架引文一致）。
- 外部对标一句话结论：机构日终运维手册（券商/资管 trading-day operations runbook、ITIL daily ops）对"总扳手"的通行做法是 **orchestration DAG + per-step SLA 与 emit-count 断言**；本链有段序与 fail-open，**缺 per-step 产出断言**（1.5/1.6 实测的 SUCCESS 空转正是该缺口的表现），故图13 给 D13-32 加 `last_run_evidence` + `emitted_stages` 两字段是对业界口径的补课，不另造机制。

## §2 D13-33 收盘验证→三表结算（段序契约）

### 2.1 上
- 触发：`full` 相第 12→13 位（`:362-363`）、`postmarket` 相第 1→5 位（`:341,:345`）。两相均 verify 先于 settle，契约成立（第 335 行注释"postmarket 内 verify 恒先于 settle——钩子序契约"）。
- 输入：`verify_for_session(data_date)`（`close_verifier.py:184`）读当日 `judgment_daily_plan` 与其 payload 内情景触发条件；`settle_all(asof_day=data_date)`（`judgment_settler.py:550`）按 horizon 扫三表到期未结算行。
- **契约强度实测**：`settle_all` 遍历的是 `JUDGMENT_TABLES`（`judgment_ledger.py:150`）＝ `intraday_market_state / next_day_forecast / daily_plan` **三表**（本簿实测字典长度 3，与"三表结算"字面吻合）；`judgment_plan_verification` 是**结算侧事实表**，故意不进发射器注册表（`judgment_ledger.py:106-108` 注释 + 守卫测试 `tests/plan_engine/test_judgment_ledger.py::test_verification_table_ssot_untouched_by_emitter`）。→ **"三表"不含验证表**，施工期勿把 verify 行算进结算口径。

### 2.2 内
- verify：写 `c1_market.judgment_plan_verification`（列：verification_id/plan_judgment_id/scenario_hits/actual_scenario_id/plan_followed/deviations/plan_quality_score/verified_at/verified_by/synthetic）。实测 13 行、`synthetic` 恒 0（无冒烟污染）。09-24 已有 2 行，`plan_judgment_id=01M36PCRJY0F8WD93T0B2TV5KK`，`scenario_hits=[{"scenario_id":"S3_oscillation","trigger_ts":"2026-09-24 10:30:00.000",…}]`，`plan_followed=0`；09-22 行 `scenario_hits=[]`（零命中）。→ 验证行**同 plan_judgment_id 可多条**（09-23 同 id 3 条）＝MergeTree 只增，达成度按最新读，**跨条一致性靠消费者**。
- settle：回填 `evaluated_at/eval_score/eval_method/outcome_*`；不可结算写 `eval_method='unresolvable'`+原因（禁跳过式静默，该件 INVARIANTS）；双闸 `WHERE evaluated_at IS NULL`。
- 幂等实测读数：`judgment_daily_plan` plan_date 09-21 结算于 09-22 02:18:10、09-22 于 09-23 02:58:04，**plan_date 09-23 `evaluated_at=NULL`**（其 outcome 需 T+1 行情，今日 15:32 尚不可结）；`judgment_intraday_market_state` 09-24 的 4 行 settled=0（同因）。→ 这两处 NULL **不是断供**，是 horizon 未到；判 D13-33 的断供必须区分"未到期"与"到期未结"。

### 2.3 下
- 三表结算列组 → Phase-5 逐层归因与 Brier 校准（`judgment_settler.aggregate_report` 窗口 20 日）；`judgment_plan_verification` → 偏离监控（MOD-PLAN-022 / TDM-E-L0-02）。
- 段序因果暴露：**`settle`（第 13 位）先于 `decision`（第 16 位），但 `next_day`（第 6 位）产的行要等下一个交易日的 `settle` 才结**；而 `next_day` 当前断供 3 交易日（簿 09 D13-44）→ `settle` 扫不到新行 → 三表里 `next_day_forecast` 的结算样本停在 09-18。这条链是本簿对 D13-33 的实际后果评估：**结算段的"在产"里含一段空转**。

### 2.4 旁
- 与 battle_map：`flow_stage='reconciliation'`/BM-REC-* 承载装配落点（骨架第 0.1 节第 4 行），本格只做"verify→settle 等待关系"，不重画装配。
- 与 TDM：见 1.5 表——verify 的"判什么"半归 TDM-E-L0-03，settle 无决策语义。

### 2.5 史
- 结算器 2026-09-16 判定台账标准 v0 第 4 节立件（`judgment_settler.py` 第 1 行 `[BLUEPRINT]` 指 `docs/_working/trading_vision/2026-09-16-judgment-ledger-standard.md`）。
- 验证环从 0→6 行"历史首闭"发生在 2026-09-21（commit 495f759903 标题"验证环0→6行历史首闭+E2E两圈实证"）。实测现存 13 行 → 09-21 首闭后四日新增 7 行。
- 两件 `maybe_emit_*`（next_day / daily_plan）曾互为 100% extract 级克隆，按 R-002 走 `judgment_ledger.run_judgment_emit_hook` 合并治本（`next_day_forecaster.py:385-387` 注释 + `daily_plan.py:779` 同注）→ CLONE-GUARD 在册先例，本节点不得再复制骨架。

### 2.6 新
- 外部对标：机构口径下"验证/结算分离"对应 trade reconciliation 的 two-pass（先 fact-check 后 PnL 归属），与本件"判定器禁写结算列、结算列组唯一写方"一致（本件第 8 行 INVARIANTS）；无更优切法建议。

### 2.7 状态
🔨。理由：段序契约与三表口径均已实证；但"最近执行证据"有一处硬伤未闭合——`judgment_daily_plan` plan_date=09-23 未结算，而今日 16:45 圈的 `data_date` 仍解析为 09-23，故 09-24 行情未入库前 settle 不可能结它；要到 09-25 圈才见分晓。**降 🔨 不升 ✅**。

## §3 D13-34 日度拍板（裁定#305 安全态）

### 3.1 上
- 触发：`full`/`postmarket` 末段 `decision`（`:348,:366`）；委托 `daily_decision_orchestrator.run_daily_decision(data_date, force=force_decision)`（`:239-243`）；`force_decision` 是全链**唯一**带逃生口的段参数（`:372`）。
- 输入：`market_state` 来自 regime（段 2 的新鲜度口径：消费方阈值 1 交易日，Owner 2026-09-21 治本对齐，见 1.7）；`state_matrix` 格来自 `config/trading_decision_map.yaml` 的 `TDM-E-L1`；预算来自 `alloc_budget_daily`（段 7）。

### 3.2 内（"结构性无实盘"双证）
- **证一·常量在册**：`src/zephyr/strategy_pipeline/daily_decision_orchestrator.py:122` `GRADUATED_PACKAGES: Final[frozenset[str]] = frozenset()`；第 119-121 行注释给出法源（"S-OWNER-001 考试 FAIL、S-OWNER-002 机制验证 FAIL…禁手填"）。消费点唯一：`select_packages():395` `enabled = sorted(set(mounted) & set(GRADUATED_PACKAGES))` → 与空集交必空。
- **证二·实数据**：`c1_backtest.decision_daily` 最新 5 行 `package_set_json` 全部 `"enabled_packages": [], "per_package_cap": {}`，`note` 尾两条固定为"无已毕业包可启（挂载∩已毕业∅；v1 安全态，裁定#305 第 2 点）｜无已毕业包，今日不出手（v1 安全态，裁定#305 第 2 点）"。`mounted` 实际非空＝`["STR-MOMTREND-033"]`（另一历史值为 `[]`）→ **挂载有包、毕业集空、交集零**，安全态是在效而非未接。
- **法律后果（拍板永远进不了实盘的机制链）**：`enabled_packages=∅` → `per_package_cap=∅` → `position_cap` 无法按 cap/Σcap 切分（`:399` 注释"v1 包集空→恒 {}；接入时按 cap/Σcap 切分"）→ 不产执行单（裁定#305 第 6 点"首版分发=仅留痕+仪表盘，实盘行为零变更"，第 7 点"盘中修订权 v1 无自动实盘干预"）。解除的**唯一合法路径**在册：`docs/_working/live_readiness/admission_gate_design.md` G3 + `owner_gate_list.md` 第 33 行（走 S-OWNER 考试链毕业，禁手填）。
- **本会话新增实测（骨架未记）**：`decision_daily` 09-23 / 09-24 两行 `no_trade=1 / no_trade_reason='budget_run_missing' / position_cap=0.0 / degraded=1`，`note` 含"alloc_budget_daily 当日无 run（预算无来源=不出预算）"。而 `alloc_budget_daily` 实测确有 trade_date=09-23 的 2 行。**根因是段序错位的口径差**：段 7 产的是"数据日 D"的预算，段 16 拍的是"D 的下一交易日"的板（实数据：`decision_daily` trade_date=09-24 行的 `asof_data_date`=09-23）→ 同圈内 `budget_run_for(09-24)` 结构性不存在。这是 dloop 内部第 2 起"段间日口径不一致"（第 1 起＝1.6 节 data_date 双源）。图13 应在 D13-34 与 D13-32 之间显式画一条 `ready_gate: alloc_budget_daily[trade_date == next_trading_day(data_date)]` 的**永不满足**边，把它变成可查事实。

### 3.3 下
- 落 `c1_backtest.decision_daily`（69 行）→ Owner 每日拍板核对 + 仪表盘；`sit_out_list_json` 实测恒 `{"entries": [], "source": "sit_out_list:v1_feeds_unwired"}`＝禁做清单**v1 未接线**（第三个显性缺口，同族口径）。
- 与骨架 D13-32 的"留痕=decision_daily max=09-24"呼应：本簿确认该读数成立，并补 `asof_data_date=09-23` 口径（防把 trade_date 当数据日误读为"今日拍今日"）。

### 3.4 旁
- 与 TDM：**代码层已兑现引用方向**（`source_cell="TDM-E-L1|expansion"`，且该格 `source_confidence` 实测为 `proposed` 非 `verified`）→ 图13 此格 `tdm_ref: TDM-E-L1` 合法且不悬空；禁则二要求 TDM 侧回挂 `daycycle_ref: D13-34`。
- 与 live_readiness 案卷：`docs/_working/live_readiness/live_admission_checklist.md` 第 41 行 P4 项把"零下单安全态有效"的验收证据指向 `daily_loop_campaign/e2e_manual_run_report.md:78-79`，与骨架 D13-32 `[MODIFY-GUARD]` 同件 → 本簿不重复取证，只补 CH 侧第二证。

### 3.5 史
- 安全态法源=裁定#305 第 2 点（2026-09-17，在册行 4162），其"禁手填"三字直接塑造了 `:122` 的 `frozenset()` 常量形态。
- 2026-09-21 commit 495f759903 把 `decision` 收进总扳手末段（原编排器只被事件链"末棒"调用，`pipeline_events.py:1068-1075` 注释仍自陈"daily_kline SUCCESS 唤醒链**末棒**…钩子序契约：编排器必须最后"）→ **同一"末棒"契约现存两处真源**（事件链 + PHASE_STAGES 第 16 位），二者当前都是末位，语义不冲突但指针唯一性破坏，登记为溢出 E-4。
- `owner_gate_list.md` F 项记 pf_alloc 已在事件链接线（09-18 alloc-2026-09-18-82cb50 真实落地），与本簿 `alloc_budget_daily` 起算 09-15/16/17/18 读数一致。

### 3.6 新
- 外部对标：MiFID II RTS 6 Art.5(2) 部署要求与量化社区 staged rollout（shadow→paper→pilot→full，promote 需 sign-off）在 TDM 第 2.2.1 节已映射为 `ai_autonomy` 五档；本格实测 `decision_daily` 无任何 `ai_autonomy` 字段（表列 18 个，无该列）→ **实盘档位不在拍板表里，在 TDM 节点里**，图13 不得复制该字段（禁则一）。

### 3.7 状态
✅。三证：时点存在性（`schedule.yaml:248` 16:45 + 段 16 `:366`）、执行体存在性（`:239-243` → `run_daily_decision` → `select_packages:374-399`）、最近执行证据（`decision_daily` trade_date=09-24 行 + 两证安全态 + `fetch_perf` 两圈 SUCCESS rows=16）。附一条不可忽略的 `degraded=1`（09-23/09-24 两行），已在 3.2 定性为段序口径错位而非故障。

## §4 溢出条目（骨架外发现，交总包落笔，本车道未自改骨架）

| # | 条目 | 证据 | 建议归属 |
|---|---|---|---|
| E-1 | **`fetch_perf` JSONL 是 dloop 唯一逐圈留痕面，且 `rows` 字段语义=段数**（不是行数）；骨架 §2 的 `last_run_evidence` 字段应直接指它 | `scheduler.py:404-413`（`_stages_n` 传给 rows 位）+ `fetch_perf_20260922/23.jsonl` 两行 rows=16 | D13-32 字段口径（骨架第 2 节补注） |
| E-2 | **骨架 D13-20 判词须改**：16:45 圈恒 skipped 成立，但 `pipeline_events.py:929-941` 已挂 `maybe_record_auction_hit`（唤醒词 `kline_etf_1min/5min`），实测 `prediction_log` type=`auction_hit` 首行 created=2026-09-24 10:01:34 → 能力**活着**，不是"触发器不存在" | 本簿 1.6 段级表第 11 行 | D13-20（W-H 簿 04）+ 骨架第 2.1 节机制 C 行 |
| E-3 | **`premarket` 相的段（llm_premarket/daily_plan）实跑在 16:45**（为 T+1 的 08:00 PIT cutoff 预产），图13 若按"段归属=盘前"画时点会把它们错放到 08:xx | `llm_daily_analysis` created 16:45:31/16:50:21 两行 | 骨架第 2 节"段归属"字段定义（须区分"语义段"与"执行段"） |
| E-4 | **"编排器必须最后"钩子序契约现存两处真源**（事件链注释 + `PHASE_STAGES` 末位），同一纪律双写=INV-1 撞车面 | `pipeline_events.py:1068-1071` 注释 vs `daily_loop_master_switch.py:348,:366` | 骨架第 0.1 节第 2 行补注 + 总包收口请求追加一条 |
| E-5 | **dloop 的 16 段中 11 段 status 硬编码 "ok"**，底层钩子六态（`skipped_wake_point/already_emitted/emitted/emit_not_committed/data_insufficient/error`）被压平 → 圈级 SUCCESS 与段级产出无因果关系 | `:189,:201,:215,:222,:229,:236,:243,:271,:285,:313,:321,:332` 对照 `judgment_ledger.py:525-528` | 新环节候选：D13-32 的子格"段状态可见性缺口"；施工期可校验（可红用例） |
| E-6 | **`data_readiness` 是唯一 break 点，但它不校验"是不是今天"**：判据是 `max(kline_index.trade_date) >= data_date`，而 `data_date` 本身就取自 `max(...)` 同源口径 → 该门**结构上永不自锁**，节假日/停更整圈照样走完 15 段 | `:164-168` + `:378-381` + `resolve_pf_alloc_trade_date` 实测返回 09-23 | D13-32 幂等/闸口径（本战役"就绪门失配"类，与图12 共享） |
| E-7 | 段 9 `classify` 与段 14/15 的委托件内部行号/表未逐行核（轮次预算让位给本簿完整性），若总包要 ✅ 须补 | 本簿 1.8 与 1.3 标注 | 待补，见自审 |

## §5 自审裁定

**干**（本簿三格全部六向齐，D13-32/34 给到 ✅ 且第三证到秒级段归属，D13-33 判 🔨 并给出可复跑的升级判据）。**六向台账逐向覆盖度**：上 ✅／下 ✅／内 ✅（16 段全列，含状态硬编码列）／旁 ✅（16 段逐段 TDM 接盘位实测，切分线给"3/16 已兑现、8 段该让渡"的量化结论）／史 ✅（MANUAL-ONLY-PERMANENT→Owner 批 09-21→施工 commit 09-22 三档实档 + 四数并存来龙 + 判定台账合并史）／新 ✅（两段各一条外部对标结论，均落到"本图字段补课"而非空谈）。

**欠**（三处，均缺"内"向的执行体细节，不改变状态判定）：
1. 段 9 `classify` 的落库表与幂等键未逐行读 → 表内该行留"该件读写面未逐行核"。补法=读 `scenario_classifier.py:367-453` 全函数体。
2. 段 14/15 的"最近执行证据"当前形态不可得（纯只读零写库），已在 1.6 显性化为 `last_run_evidence` 用例；若总包要求可查，须在施工期为二者加一个 emit 计数（属新增资产，须声明替代项，本车道不自裁）。
3. 本簿未跑外部检索（对应骨架 B6 未跑之路第③扫的 dloop 侧面），"新"向只给一句话对标结论。

**溢**：7 条（E-1~E-7），全部未自改骨架。

## §6 实查命令（可复跑；本会话 2026-09-24 15:32 实跑）

```bash
export PATH="$LOCALAPPDATA/Programs/Python/Python312:$LOCALAPPDATA/Programs/Python/Python312/Scripts:$PATH"
cd /d/ZephyrAlpha/.aidrafts/st-mapbuild-20260924

# (1) 段数四相（期望 premarket 5 / intraday 4 / postmarket 8 / full 16）
PYTHONPATH=src python -c "from zephyr.plan_engine.daily_loop_master_switch import PHASE_STAGES as P;[print(k,len(v),v) for k,v in P.items()]"

# (2) GRADUATED_PACKAGES 常量与消费点（期望 :122 空 frozenset / :395 交集）
grep -n "GRADUATED_PACKAGES" src/zephyr/strategy_pipeline/daily_decision_orchestrator.py

# (3) 逐圈留痕（期望仅 09-22 16:50:26 与 09-23 16:45:33 两条 SUCCESS，rows=16）
grep -h daily_loop_master /d/ZephyrAlpha/.runtime/fetch_perf/fetch_perf_*.jsonl

# (4) 拍板安全态 + 预算口径错位（期望 enabled_packages=[] / mounted=["STR-MOMTREND-033"] / 09-23,09-24 no_trade_reason='budget_run_missing'）
export $(sed -n 's/^\([A-Z_]*\)=\(.*\)$/\1=\2/p' /d/ZephyrAlpha/config/.env.clickhouse | tr -d '"' | tr -d "'")
PYTHONPATH=src python -c "
from zephyr.infrastructure.database_service import get_db_service as G; c=G().get_clickhouse_conn()
print(c.execute('SELECT trade_date,asof_data_date,no_trade,no_trade_reason,position_cap,package_set_json FROM c1_backtest.decision_daily ORDER BY trade_date DESC LIMIT 5'))
print(c.execute('SELECT trade_date,count(*) FROM c1_backtest.alloc_budget_daily GROUP BY trade_date ORDER BY 1 DESC LIMIT 4'))"

# (5) 三表口径与验证表分离（期望 3 键 + VERIFICATION_TABLE 不在其中）
PYTHONPATH=src python -c "from zephyr.plan_engine.judgment_ledger import JUDGMENT_TABLES,VERIFICATION_TABLE as V; print(JUDGMENT_TABLES, V)"

# (6) 段级产出时间线（判"哪一段在哪一圈真跑"）
PYTHONPATH=src python -c "
from zephyr.infrastructure.database_service import get_db_service as G; g=G().get_governance_conn(read_only=True)
[print(tuple(r)) for r in g.execute('SELECT id,prediction_type,module,trade_date,created_at FROM prediction_log ORDER BY created_at')]"

# (7) TDM 接盘位扫描（16 段逐段，期望仅 MOD-PLAN-001/011/018/022/024/025/026 九节点在册）
PYTHONPATH=src python -c "
import yaml; n=yaml.safe_load(open('config/trading_decision_map.yaml',encoding='utf-8'))['nodes']
print(len(n)); [print(x['node_id'],x.get('module_id'),x.get('activation'),x.get('name_zh')) for x in n if str(x.get('module_id','')).startswith('MOD-PLAN')]"

# (8) MANUAL-ONLY 解除两档实档
git log --oneline --date=short --format='%h %ad %s' -2 -- src/zephyr/plan_engine/daily_loop_master_switch.py
sed -n '10,17p' docs/_working/daily_loop_campaign/owner_gate_list.md
grep -n "ruling_id: '裁定#305'\|ruling_id: '裁定#388'" docs/01_policies_and_standards/_registry/catalogs/ruling_registry.yaml

# (9) 日历守卫覆盖面（期望 9 槽，dloop_post 不在内）
grep -n "TRADING_DAY_GUARDED_SCHEDULES" -A 12 src/zephyr/data/trading_calendar.py
```
