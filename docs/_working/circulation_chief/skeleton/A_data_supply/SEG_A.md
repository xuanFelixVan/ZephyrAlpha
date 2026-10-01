---
ttl: task_bound
title: A 段·数据供给链 16 环节六向挖矿档（S3 W3-1）
session: st-ffchief-20261001
date: 2026-10-01
status: mined
creation_token: seg-a-data-supply-w31-20261001
---

# SEG_A · 数据供给链（A-01..A-16，16 环节）代码级核验

> 方法：以代码为准（grep 调用点/消费方/调度注册），skeleton 行是线索非结论。证据=路径:行 或实跑输出。基线复核：TDM 182 节点/null 37/FAC 16/scheduler.py:537 lane_g 沿/57 域目录，全部与 00_skeleton.md §0.2 吻合。

## 六向台账

| 环节 | 上游 | 下游 | 生产者代码(路径:行) | 消费者代码 | 自动化态 | 运行态 | 三态复核 |
|------|------|------|---------------------|------------|----------|--------|----------|
| A-01(F01) 多源采集调度 | 外部 10 源 | F04/F06/F10 | src/zephyr/data/scheduler.py:2748 `main()`；data/__main__.py:29（re-export cli.main）；src/zephyr/data/config/tasks.yaml 计 **271 task_id**（实跑 grep -c） | CH 252 表全消费端；config/resource_profile_registry.yaml entities=**101**（yaml.safe_load 实跑，skeleton 写 96=漂移在案） | 定时（trading_calendar.py TRADING_DAY_GUARDED_SCHEDULES 守卫） | 绿（tasks.yaml 271 任务在册，调度槽 cross_validation/integrity_check/pf_alloc_rebalance_check 均活） | **维持挖干**（96→101 计数漂移登记 §4 口径） |
| A-02(F02) 源接入生命周期 | F31/F96 | F01 | **src/zephyr/data/onboarding_wizard.py:130-255**（MOD-L00-004，十环编排壳，CLI `python -m zephyr.data.onboarding_wizard start\|resume\|confirm\|status`）+ docs/01_policies_and_standards/sop/data_ops_sop/data_source_onboarding_sop.md | 数据上架会话（人工驱动，头注 CONSUMERS 声明"无调度器消费"=设计内） | 手动（宪法 §9.3 禁自动轮询注册=设计内人工） | 黄（wizard **experimental**；data/runtime/onboarding/ 不存在=**零运行痕**） | **存疑维持但判级变迁**：§3#6"串接空地/无流水线承载"过期——承载件已建成未投运；断链级降为存疑（详 F02.md） |
| A-03(F03) Provider 实现与路由 | F02 | F01 | src/zephyr/data/implementations/ **46 py**，grep "class.*Provider" 命中 **30 文件**（miniqmt/akshare/baostock/cls/crypto/eia 等） | scheduler.py 经 tasks.yaml `source:` 字段路由 | 定时（随采集槽） | 绿（10 源族齐备，crypto 族独立在册） | **维持挖干** |
| A-04(F04) 清洗校验与坏数修复 | F01 | F06 | ①cross_source_validator.py+②backfill_checker.py+③cleaning 三引擎（cleaning_engines.py:119 engines_status 四引擎门面） | ①→scheduler.py:239-273 cross_validation 槽；②→integrity_checker.py:43+catchup_guard.py:178；③→**零生产调用方**（cleaning_anomaly_engine.py:5 "built-not-wired"） | ①②定时（23:15/23:00 错峰）；③断（Owner 门 C1） | 黄（① 09-27 接线翻绿：scheduler.py:239+trading_calendar.py:161；③ 三 data_eng 引擎 Owner 门挂起） | **存疑维持，断链判词半过期**：§3#1"三引擎零接线"已不成立（详 F04.md） |
| A-05(F05) 判重与数据审计 | F01 | F12 | scripts/governance/data_quality/check_tick_duplication.py（manifest:6385 登记） | integrity_checker.py:211（路径锚）+**:368**（subprocess 正门调用）→scheduler integrity_check 槽 | 定时（每日巡检内嵌） | 绿（14 字段全同判重规则，fail 经 alerter） | **维持挖干** |
| A-06(F06) CH 热库落库 | F04 | 全消费端 | src/zephyr/data/ch_config.py（7 处 import 消费）；scripts/ch/apply_*_ddl.py **25 件** | 全部读端（ch_reader CONSUMERS 声明） | 定时 | 绿 | **维持挖干** |
| A-07(F07) PG 架构库 | 生成器 | 治理端 | scripts/governance/generate_project_depgraph.py | ROOR/alignment/gates 全家 | 事件（生成器触发） | 绿 | **维持挖干** |
| A-08(F08) 冷库归档运维 | F06 | 长周期回测 | scripts/ch/archiver.py + src/zephyr/data/storage_tiering.py + data/quality/archive_sla_burnrate.py + data_compression_archiver.py | 回测 ch_tick_replay 冷读 | 定时 | 绿（tiering 族 4 件比 skeleton 锚更厚，待深挖注记维持） | **维持挖干(待深挖)** |
| A-09(F09) 备份 3-2-1 双链 | 全库 | 灾备 | scripts/backup/backup.ps1 + backup_ch_vm.ps1 | config/resource_profile_registry.yaml:1351 ops_daily_backup + :1493 ops_weekly_vm_backup；scripts/register_library_ledger_backup_task.ps1（MOD-INF-043） | 定时（日/周计划任务） | 绿（双任务在 96 实体册登记） | **维持挖干** |
| A-10(F10) 行情订阅分发 | F01/券商 | 盘中决策链 | src/zephyr/data/tick_subscriber.py:225 `class TickSubscriber` | scheduler 常驻槽位；盘中链 | 常驻 | 绿（底册 0929/0930 双日 57M+ 行） | **维持挖干** |
| A-11(F11) TDM 交叉轴挂接 | 各注册表 | TDM 全图 | src/zephyr/trading/decision_map.py:105 `_XREF_SPECS` 实点 **13 轴**（pattern/seat/macro/cycle/universe/cost/event/risk_limit/portfolio/benchmark/threshold/model/chain） | decision_map 加载即挂 | 事件（注册表加载） | 绿（13 轴机读确认；宪法"16 表"口径漂移维持两说并记） | **维持挖干(漂移在案)** |
| A-12(F12) 产业链图谱 | F05 | F18/F32 | docs/01_policies_and_standards/_registry/catalogs/chain_registry.yaml（**873 chain_id** 实跑）；生成器 scripts/governance/generate_chain_registry.py | TDM chain_refs 轴（decision_map.py R45）+ F18/F32 | 机生 | 绿（873 条=吸收对齐 583/873 口径吻合） | **维持挖干** |
| A-13(F123) DB schema 迁移通道 | B-9 迁移册 | A 段全库面 | docs/01_policies_and_standards/_registry/catalogs/migration_registry.yaml（**实为模块迁移映射册**：MATURITY=deprecated、maintenance=frozen、status: pending 计 **13 条**；grep migration_id=0） | 头注 CONSUMERS=scripts/migration/governance_root_split.py 等 3 个历史脚本 | 未建（无 DB schema migration runner：database_service.py 无 migrate/ALTER 编排） | 红 | **维持盲区(P0)**——且册锚错位：册本体非"schema 迁移通道"（详 F123.md） |
| A-14(F125) data_governance 治理本体 | A/K 交界 | 治理层 | src/zephyr/data_governance/ **21 py**（core/lineage_tracker、schema_registry、metadata_registry 等） | **src/zephyr/data/data_service.py:4**（DEPENDENCIES 声明 core.lineage_tracker）；alt_data 两件注入语义引用 | 静态库+被动加载 | 黄（有实件有消费方，无调度面） | **盲区→存疑（变迁）**：非"未挖"，血缘/元数据族已建成被 data_service 消费（详 F125.md） |
| A-15(F126) 字段字典 REG-FLD-001 | A/K 交界 | schema 治理面 | docs/registry_of_registries.yaml:725 REG-FLD-001（8280 行 schema v2.0 册） | 静态册引用态 | 静态册 | 黄 | **维持盲区(P1 新号)**（册在、六向台账首次建档） |
| A-16(F127) data_eng 工程域 | A 段 | 冷储/湖 | src/zephyr/data_eng/ **15 py**（skeleton 写 16=计数漂移） | src/zephyr/data/cleaning_engines.py、cleaning_anomaly_hosting.py、data/quality/sla_burnrate_predictor（DEPENDENCIES 实引） | 静态库+清洗门面惰性调用 | 黄（清洗三件 built-not-wired 挂 Owner 门，冷储件在岗） | **盲区→存疑（变迁）**（详 F127.md） |

## 段内附注

- **TI 派生链**（§3#10）：`ti_minute_recalc.py` 文件名在 src/scripts **未寻获**（锚漂移）；实锚=src/zephyr/data/config/tasks.yaml:2287-2315"技术指标日线增量/全量刷新（internal 9 周期遍历 1min~monthly）"。回填中状态沿底册，判黄不降级。
- **板块分钟生产者**：internal_eqw 实锚=scripts/kline_sector_intraday_from_constituents.py（全仓唯一命中）；kline_sector 任务链 tasks.yaml:949-955（tqcenter 换道+错峰注记在案）。
- **计数漂移**：resource_profile entities 实跑 101 vs skeleton 96；data_eng 15 vs 16；normalized 592 txt vs 597 条。均登记不裁。

## 本段三态变迁

| 环节 | 原判 | 复核判 | 证据 |
|------|------|--------|------|
| A-02(F02) | 断链（§3#6 工段串接空地） | 存疑（承载件已建成未投运） | onboarding_wizard.py 十环壳+零运行痕 |
| A-04(F04) | 存疑(P0"三引擎零接线") | 存疑维持，断链判词半过期（cross_validation 已接线翻绿） | scheduler.py:239+trading_calendar.py:161 |
| A-14(F125) | 盲区(未挖) | 存疑 | 21 py+data_service.py:4 消费 |
| A-16(F127) | 盲区(未挖) | 存疑 | 15 py+cleaning_engines 消费 |
