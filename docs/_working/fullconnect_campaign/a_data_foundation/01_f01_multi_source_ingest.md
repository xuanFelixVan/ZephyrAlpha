---
ttl: task_bound
title: "F01 多源采集调度——271 任务×30 槽位×23 源采集底座复飞案卷"
session: zc-l01-20260927
---

# F01 多源采集调度（复飞案卷，2026-09-27 实测）

> 前序：M1 册 01_ingest.md（st-commitspeed-tbl-20260924）挖干；本卷=接线四态独立复核+当日增量（census 假绿 5 腿面/槽位三数漂移/NightlySentiment 状态翻转）。引用不重挖。

## 一、六向台账（今日实证锚点）

| 向 | 内容与实证 |
|---|---|
| 上游 | 外部 23 源 API；QMT 沙箱桥文件（tick_subscriber bridge 模式）；internal 本地计算 24 任务读 CH 自算；币安 vision 镜像（Owner 裁定，tasks.yaml 注）——源分布今日 yaml 实解：akshare 100/miniqmt 56/akshare_alt 36/internal 24/tushare 13/tqcenter 5/tdx 5/tickflow 4/hyperliquid 4/baostock 3/fred 3/其余 2×7+1×6=271 总 |
| 下游 | ch_writer 写前门禁（ch_writer.py:1006-1021 现行四门禁）→ F06 落库；progress 真源 data/integrator_progress.db；fetch_perf 落 c0_meta |
| 自动触发 | ZephyrAlpha_DataScheduler **Running**＋ZephyrAlpha_TickSubscriber **Running**（schtasks 2026-09-27 实测）；schedule.yaml `schedules` **30 槽**（yaml 实解）；熔断 source_circuit_breaker+policy_registry |
| 真源注册表 | 任务=src/zephyr/data/config/tasks.yaml（**271**）；槽位=src/zephyr/data/config/schedule.yaml（**30**）；缺口=src/zephyr/data/config/known_data_gaps.yaml（**63 条**实解）；能力画像=config/resource_profile_registry.yaml（data_slot_* 去重 **29**）；源资产=data_sources_registry.yaml v2.6.0 |
| 门禁质量尺 | validate_tasks_yaml WARN 不阻断（table_registry.py:181-195）；speed-tester/source_health_check/source_sla_tracker/fetch_perf_recorder；**假绿尺新增**：270 任务全扫 census（chain_fullflow_closeout/mine_pipe_false_green_census.md：GREEN_WITH_DATA 226/FALSE_GREEN 5/NEVER_RUN 10/NO_TARGET_TABLE 4/NOT_GREEN 25） |
| 运行状态 | **绿（带 census 疤痕）**。DataScheduler/TickSubscriber 双 Running；30h 窗 SUCCESS 1859/FAILED 36；主表 max_date=2026-09-24（09-25 中秋休市合法缺席）。疤痕：#ARCH-351 miniQMT 清退 56 任务在册（24 无退路子集）；**ZephyrAlpha_NightlySentiment 已 Ready**（M1 册 09-25 记 Disabled→今实测翻转，llm.enabled 生效，疤痕消除） |

## 二、子模块三级枚举（调度侧，src/zephyr/data/ 实扫）

1. 调度核：scheduler.py（IntegratorScheduler+单实例锁）/task_queue.py/progress_store.py
2. 韧性：policy_registry.py/source_circuit_breaker.py/source_health_check.py/error_classifier.py/speed_tester.py/fetch_perf_recorder.py/alerter.py/alert_webhook_dispatch.py
3. 回补：backfill_checker.py（48KB）/auto_backfiller.py/catchup_guard.py（L10/L10.5/L10.7 三班）
4. 配置：config/{tasks,schedule,data_supply_sentinel,known_data_gaps,policies,manual_calendar_events_schema}.yaml（6 件实列）
5. 十子包归属：implementations 46 py（F03）/calendar 4/connectors 3/normalizers 4/redundant_source 7/symbol_normalizer 2/transport 2/wal_codec 3/satellite_geospatial_engine 1（壳，见 F03 卷）/config 0 py
6. 对照账：tasks 271 vs census 分母 270（差 1=L-1 已知项，census 只扫有排产面任务）vs CH 表 253（骨架 252，见 F06 卷勘误）

## 三、接线四态独立复核

- 总册：built/P1/D1。独立复核：**built 成立**——调度常驻双 Running+census 226/270 GREEN_WITH_DATA+回补三班在册。
- 保留 P1 的证据：FALSE_GREEN 5 腿全部是本环节排产任务（suspend_status_premarket/postclose/derive_weekend+etf_benchmark_refresh+realtime_snapshot_incremental，tasks.yaml 实查任务 id 在册）；FAILED 8 腿中 2 腿 str/date 共因（consensus_daily_build/financial_derived_build）。
- 骨架勘误①：schedule.yaml 头注"16 槽"→M1 册记 29→**今日 yaml 实解 30**——三数漂移再 +1，头注释过期实锤（宪法 §4.4）。
- 骨架勘误②：总册 F01 下游列"F04/F06/F10"，census 证明还应列"观测面（recon_runner/哨兵班）"为一级消费端（SUCCESS 回执真值互证=C4 假绿尺的落点）。

## 四、缺口清单

| # | 缺口 | 处置 | 级 |
|---|---|---|---|
| G1 | FALSE_GREEN 5 腿（SUCCESS 但目标表 0 行；etf_benchmark date 列 ALL_NULL+suspend 3 腿 schema 在数据零） | 施工：C4 假绿灯交叉尺（task_runs 回执×目标表真行数互证+rows_written 回执） | P0 |
| G2 | FAILED 2 腿 str/date 共因（consensus_daily_build/financial_derived_build→一处 _norm_date 覆三实例；反例护栏 pattern_win_rate 不同根勿打包） | 施工：C1 共因修复 | P0 |
| G3 | FAILED 另 6 腿待裁（audit_opinion 停 05-29/etf_share_snapshot 停 09-18/l2_tick_snapshot 未知 capability/news_tushare 接口名/pattern_win_rate exit1/rights_issue 缺接口） | Owner 门（修接口/换源/退役逐腿裁） | P1 |
| G4 | NEVER_RUN 10 腿冗余注册 vs 应跑未跑逐腿核 | 挂起+解锁=census 逐腿判定单 | P1 |
| G5 | #ARCH-351 miniQMT 56 任务清退迁移 | 施工（退役映射表裁定#376 已授权） | P1 |
| G6 | 槽位头注 16 vs 实 30 漂移 | 施工（改引用生成器计数） | P2 |

## 五、自审闸三态

挖干可施工（引用 M1 册+今日四态复核+勘误两条）；G3/G4 待 Owner 门/逐腿判定；无新裁定需要。

## 六、复跑命令

```bash
export PATH="$LOCALAPPDATA/Programs/Python/Python312:$LOCALAPPDATA/Programs/Python/Python312/Scripts:$PATH"
python -c "import yaml;from collections import Counter;t=yaml.safe_load(open('src/zephyr/data/config/tasks.yaml',encoding='utf-8'))['tasks'];print(len(t),Counter(v['source'] for v in t).most_common(8))"
python -c "import yaml;print(len(yaml.safe_load(open('src/zephyr/data/config/schedule.yaml',encoding='utf-8'))['schedules']))"   # 30
powershell -NoProfile -Command "Get-ScheduledTask |? {\$_.TaskName -match 'DataScheduler|TickSubscriber|NightlySentiment'} | ft TaskName,State"
sed -n '1,40p' docs/_working/chain_fullflow_closeout/mine_pipe_false_green_census.md   # 判定分布
```
