---
ttl: task_bound
title: "五车道与交易日循环修复报告"
owner: st-datasop-20260930
language: zh
status: active
version: "1.0.0"
date: 2026-10-04
---

# EXEC-3 五车道与交易日循环修复报告（2026-10-04）

> 工单=①策略工厂五条进货车道停摆诊断修复 ②D13-20 竞价窗闸错位 ③D13-44 日界交接断供。
> 只动代码/诊断面；tasks.yaml/schedule.yaml/A 队互斥清单/config *map*.yaml 零触碰。

## 一、五车道诊断与处置

### lane_c（FactoryLaneC 计划任务，10-02 rc=3）——已修代码面
- 根因（日志 `.runtime/logs/factory_lane_c.log` 实读）：20:00 点火 → E0 闸
  `gate_deny_calendar_unknown`。但 CH 日历表 `c1_market.trade_calendar` **有** 10-02 行
  （is_open=0 国庆休市，实测 range 1990-12-19~2026-12-31 共 8807 行）——是
  `fetch_is_trading_day` 的 **CH 通道瞬时异常被静默吞成 None**（原 `except: return None`
  零留痕零重试），与"日历真缺行"同判 → fail-closed 拒 → mine rc=3 短路。
- 修复（`scripts/backtest/compute_window_gate.py`）：①吞异常前 log 留痕；②通道异常
  有界重试（1 首查+2 补试、1s 间隔，事件内短重试非常驻循环）；③日历真缺行（rows 空）
  =确定性答案不重试。fail-closed 语义不变。
- 实测复算：`check_gate('lane_c_gp_mine','local_gpu', 2026-10-02 20:00)` →
  `allowed=True / gate_allow_off_hours`（同参数原逻辑=rc3）。

### lane_b / three_high（产物停 10-01 05:34）——休市非根因，是 lane_c 短路的下游
- 判定：**非国庆休市正常语义**。10-01（休市日）20:00 前实为 05:34 跑成过一轮
  （`three_high_candidates.csv`/`lane_b_candidates.csv`/`lane_c_candidates.csv` 三件同刻
  05:34）→ 休市日语义可跑。10-02 起停产是 wrapper 先 mine 后 intake 的短路链：
  mine rc=3 → `factory_intake_pipeline.py` intake/construct/translate 全 SKIP。
- 处置：无独立代码缺陷，lane_c 重试修复后随下一交易日 20:00 圈自动恢复
  （10-08 为节后首个交易日；wrapper 周一至五 20:00 点火，假期夜本就可跑重活）。

### lane_g（停 09-23，11 天）——挂载缺失（移交 EXEC-1），上游 inbox 亦停
- 实测：`lane_g_intake_sweep.disabled` 总闸**不在**（代码槽活）；产物
  `lane_g_candidates.csv` 停 09-17，游标 `lane_g_seen_urls.csv` 停 09-23；
  inbox `docs/_working/automation/inbox/` 仅 1 个 `intel-20260916.md`（mtime 09-29）。
- 根因两层：①`lane_g_intake_sweep` 调度槽 tasks 零绑定（工单已载）——慢路径兜底槽
  从未被点；②快路径上游 L3 `intel_harvester` 也停产出（inbox 无新件）——**上游断供
  超出本车道代码面**。代码槽 `src/zephyr/data/scheduler.py:544` 本身健在，无需修。

### lane_e（零产物）——结构性无产物面（移交 EXEC-1 决策）
- 实测：`scripts/backtest/lane_e_enhanced.py`（MOD-BT-089）是三模型分位回归**对比实验
  CLI**，`lane_e_enhanced_cli.py` 只 `print(json)` 到 stdout，**全仓无 lane_e 落盘产物
  路径**；且不在 `factory_intake_pipeline._LANE_SPECS`（六车道=D/B/C/F/G/I）内、
  trading_day_cycle_map 无 lane_e 槽。
- 判定：lane_e 不是"停摆"而是"从未有产物面"。补产物=要么给 CLI 加 `--out` 落盘+
  挂槽，要么正式退出进货车道编队（净零判据 w5_1：零消费→退役候选）。**非代码 bug，
  不擅动**，两条路报 EXEC-1/Owner 裁。

## 二、D13-20 竞价窗闸错位——已修+回归 2 例

- 根因（fig13 簿09 结构性诊断复核属实）：`_stage_auction_hit` 墙钟窗 10:00-10:30
  硬 skip；唯一自动触发=16:45 `dloop_post` 圈恒落窗外 → 命中格**永无产物**。
  复核 `record_auction_hit` 全部 SQL：指数日线 ≤T、ETF 分钟窗恒 [09:30,10:00)
  ——**输入全以数据时间戳为界，与执行时刻无关**，16:45 回看判定与 10:00 实时
  判定同 PIT 口径，墙钟闸是唯一阻断。
- 修复（`src/zephyr/plan_engine/daily_loop_master_switch.py` + `auction_hit_recorder.py`）：
  ①`<10:00`（走势窗未闭合）仍 skipped（PIT 卫生保留，reason 改
  `auction_window_not_closed` 如实）；②`≥10:30` 回看补判照常落库，
  `record_auction_hit(..., late_eval=True)` 新参 annotation 留痕（phase 仍
  intraday_1000——判定时点语义由输入界别保证）；③stage 加 `now` 注入位（测试/
  手动补跑用，调度派发不传）。
- 回归：`test_auction_hit_stage_late_eval_at_1615_circle`（16:45 → ok+late_eval=True+
  落库调用断言）、`test_auction_hit_stage_still_skips_before_window_close`（09:00 →
  skipped 零落库）、recorder 侧 `test_late_eval_annotation_persisted`/
  `test_late_eval_default_off_no_annotation`。

## 三、D13-44 日界交接断供——已修（Y-4 三处）+回归 3 例

按 fig13 簿09 Y-4 锁定根因逐条修（`src/zephyr/plan_engine/next_day_forecaster.py`、
`daily_loop_master_switch.py`）：
1. **主杀**：`cond_prob_from_history` 原 `use_ranges = same` 把同桶【收益】列表喂给
   振幅字段 → `expected_range_pct` 实为均值次日收益，下行桶为负被
   `judgment_ledger ≥0` 校验 fail-closed 拒发（30 交易日杀率 70%）。修：新增
   `same_rng = next_ranges.get(key)`，非 fallback 用同桶振幅。回归
   `test_cond_prob_range_uses_same_bucket_ranges_not_returns`（构造同桶次日收益恒
   -1%/振幅恒 +2.02%，断言 expected_range_pct=2.02 非 -1）。
2. **第二杀**：三分量独立 `round(6)` 和≠1 超 ledger 1e-6 容差。修：舍入余差归最大
   分量（|δ|≤1.5e-6，最大分量 ≥1/3 吸收后稳在 [0,1]）。回归
   `test_cond_prob_prob_sum_exact_across_seeds`（30 种子扫描，和距 1.0 ≤1e-12，
   远紧于容差）。
3. **真静默位**：`_stage_next_day` 原硬编码 `status:"ok"`（data_insufficient 也报 ok，
   dloop_post 汇总永远全绿）。修：钩子 action 透出——emitted/already_emitted/
   skipped_wake_point=ok，data_insufficient/emit_not_committed/error=error（error 字段
   明写"日界交接缺口"）→ 16:45 圈 `summary.error>0` 即 ERROR 告警，**交接缺口告警
   可见**。回归 `test_next_day_stage_surfaces_handover_gap` +
   `test_next_day_stage_ok_actions`（不误报）。
- 修复后链路自愈路径：下一交易日 16:45 dloop_post 圈 → 段 6 以正确振幅发射 →
  `judgment_next_day_forecast` 恢复日更（09-28 后断供终止）；若再断，告警直达。

## 四、验证读数

| 面 | 命令 | 读数 |
|---|---|---|
| 关联四件 | pytest tests/backtest/test_compute_window_gate.py + tests/plan_engine/{test_daily_loop_master_switch,test_next_day_forecaster,test_auction_hit_recorder}.py | **67 passed**（含新回归 11 例） |
| 扩大面 | pytest tests/plan_engine/ | **754 passed** |
| 跨套件 | pytest tests/ -k 相关词（消费方六件：ignition_gate/factory_intake/exam_trigger/sleeve_provenance/judgment_ledger/resource_profile） | **168 passed + 3 failed**；3 失败全在 `test_generate_resource_profile_registry.py`（槽位 33 vs 26）——根因=他会话在途改动（`schedule.yaml`/`generate_resource_profile_registry.py`/`resource_profile_registry.yaml` 主区未提交 M 态），与本次 diff 零交集，按"他会话在途不代修"拆批留痕 |
| E0 闸复算 | check_gate('lane_c_gp_mine','local_gpu',10-02 20:00) | allowed=True / gate_allow_off_hours |

## 五、移交 EXEC-1（任务挂载需求，tasks.yaml/schedule.yaml 归其批）

1. **lane_g**：`lane_g_intake_sweep` 槽在 tasks 绑定到 `scripts.backtest.lane_g_stomach_intake:run_intake_sweep`
   （慢路径兜底，代码槽 `scheduler.py:544` 已在）；同时上游 L3 `intel_harvester` inbox
   停产（09-16 后无新件）需另开工单——本车道只修到兜底槽可用。
2. **lane_e**：报 Owner 二选一——给 `lane_e_enhanced_cli` 加落盘产物面+挂槽，或按
   净零判据（零消费零产物）退役 lane_e 进货车道编队（`_LANE_SPECS` 本就无 E）。
3. **D13-20 增强项（可选）**：若要 10:00 实时命中（而非 16:45 回看补判），需新增
   交易日 10:05 盘中槽——现有修复已保证产物必有，实时性属增量。

## 六、涉及文件（8）

- `scripts/backtest/compute_window_gate.py`（重试+留痕）
- `src/zephyr/plan_engine/daily_loop_master_switch.py`（auction_hit 回看补判/next_day 状态透出）
- `src/zephyr/plan_engine/auction_hit_recorder.py`（late_eval 留痕位）
- `src/zephyr/plan_engine/next_day_forecaster.py`（use_ranges 虫/概率和精确）
- tests 三件 + `tests/plan_engine/test_auction_hit_recorder.py`（回归 11 例，tmp_path 隔离）
