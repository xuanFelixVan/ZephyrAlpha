---
ttl: task_bound
lane: M1 数据链
segment: D6 CH 热库落库 + D7 PG 架构库（数据面）+ H1 Redis 热缓存
mined_at: 2026-09-25
session: st-commitspeed-tbl-20260924
---

# 03_ch_warehouse — 入库/热储段作业簿（D6/D7）

## 一、环节定义与边界

一句话：clean 数据经 ch_writer（TCP TSV）落到 ClickHouse 热层（c0_meta/c1_market/c1_backtest/c3_fundamental 四库 252 表），PG depgraph 承架构数据、Redis H1 承热键。
- **供料方**：01_ingest（FetchResult）→ 02_cleaning（门禁后行）。
- **消费方**：回测/模拟/仪表盘/API server（M2/M6）、pit_query、派生层 internal_compute 回写、04_cold_storage 归档源。

## 二、六向台账

| 向 | 内容与实证 |
|---|---|
| 上游输入 | ch_writer.write_result（:893 起）/BufferedWriter 攒批/WalWriter 段文件 drain 三路写入口 |
| 下游消费 | 全仓 CH 消费方经 DatabaseService.get_clickhouse_conn(role, slot) 领连接（database_service.py:161-214 "全仓唯一 Client 构造点"）；reader=zephyr_reader readonly（RBAC #ARCH-CH-027）/writer=zephyr_writer/admin=DDL 专用 |
| 自动化触发 | ZephyrAlpha_DataScheduler Running（APScheduler 日批承载写入）；ZephyrAlpha_CHHealthProbe **Running**（CH 存活探针）；ZephyrAlpha-CH-OptimizeMerge-Weekly Ready（optimize_merge.py 周合并）；ch_parts_monitor.py parts>100 告警（64号 Q8，防 2026-07-09 merge 满载崩溃重演） |
| 真源与注册表 | 连接配置唯一真源=config/.env.clickhouse（ch_config.py:8/:52，fail-closed 抛 CHConfigError）；表名/品类唯一真源=docs/03_modules/_cross_layer/database/business_data_categories.yaml（**338 条 category_id**，grep 实数）；消费层=table_registry.py（table() KeyError fail-closed 禁编表名）；DDL-as-Code=schemas/categories/*.py + scripts/ch/apply_*_ddl.py（25 件 ls 实数）；Redis 配置=config/.env.redis（redis_config.py，fail-closed） |
| 门禁与质量尺 | 写前四门禁（见 02 册）；列集缓存失效 invalidate_table_schema_cache（ch_writer.py:647-657，2026-09-14 news_data 死信事故治本②b）；防再犯守卫（:549 拦截点在 write_result/BufferedWriter.add 两处）；RBAC 三账号（apply_rbac.py）；RULE-SCHEMA-TZ：DateTime64(3)+显式时区（apply_market_tables_ddl.py 'Asia/Shanghai'+'UTC' 双列 14 处） |
| 当前运行状态 | **绿（带卫生债）**。实测（2026-09-25 DatabaseService 只读）：c0_meta 1 表 / c1_backtest 16 / c1_market **201** / c3_fundamental 34 = 252 表；行数：tick_data **8,953,165,904**、kline_1min 1,486,013,551、kline_daily 10,108,926、kline_daily_hfq 10,079,242、tick_depth_5 103,506,452、news_data 8,249,360；主表 max_date=2026-09-24（昨收齐）。**l2_tick=0 行**（空表疑点，见堵点）。Redis H1=172.24.30.100:6379 与 CH 同 VM（database_service.py:34 D1 决策），db0 sim/db1 live/db2 治理。PG depgraph 连接 get_depgraph_conn（:136，9148 节点口径见骨架册 D7） |

## 三、子模块清单

| 模块 | 入口 | 状态 |
|---|---|---|
| DatabaseService 单例 | database_service.py:365-378 get_db_service（atexit close_all；2026-09-14 连接统一治本，根治多会话 Code:181 断连） | production |
| ch_config | ch_config.py（ensure_ch_env_loaded 幂等；裁定 #ARCH-CH-017/#019） | production |
| ch_writer | ch_writer.py（1131 行：TSV 序列化/DESCRIBE 列缓存/HTTP fallback 链 :792-815） | production |
| buffered_writer / wal_writer / tick_depth_writer / tick_redis_cache | 攒批直写/主动 WAL/五档/热缓存 | production |
| ch_reader | ch_reader.py（只读查询封装；check_tick_duplication 依赖） | production |
| pit_query | pit_query.py:73,79（≤1970-01-02 不可见，D1 裁定） | production |
| TableRegistry 消费层 | table_registry.py:133-150（category_id→"{db}.{table}"；validate WARN 不阻断） | production（Phase 4 升 block 未做，模块头 :48-49 自述） |
| DDL 兵器 | scripts/ch/apply_*_ddl.py 25 件（market/fundamental/cross_asset/crypto_shadow/sim 族/regime/pattern 等）+apply_rbac.py+apply_timezone_migration.py | production，DDL-as-Code |
| CH 运维件 | optimize_merge.py（周计划任务）/ch_parts_monitor.py/waste_table_scanner.py/verify_schema_truth.py/verify_exchange_coverage.py/_data_inventory.py/_recovery_drill.py | production/manual 混合 |
| Redis H1 | infrastructure/redis_config.py+redis_state_layer_ssot.py+h1_redis_hot/（backup/ 下 test_h1_* 三件 e2e 在册） | production |
| PG depgraph | governance/depgraph_schema.py get_depgraph_pg_connection；generate_project_depgraph.py --force 重建（宪法 §9.10） | production |

## 四、堵点与病灶

| # | 现象 | 根因 | 修法草案 | 工作量 | 本车道可修 |
|---|---|---|---|---|---|
| W1 | **表卫生债**：c1_market 物理 201 表 vs business_data_categories 品类 338 条 vs 该 YAML 头注释"114 条（2026-08-15 实测）"——三个数互相矛盾；库内可见 quarantine/legacy 家族 8+ 张（kline_daily_hfq_legacy_20260924 843 万行、kline_daily_hfq_preversion_20260925 1007 万行、kline_daily_hfq_quarantine_20260925 10,475 行、index_valuation_daily_quar_20260920 8,125 行、weekly/monthly_hfq_legacy×2、index_valuation_daily_v2、macro_data_compat/latest/vintage 多版本） | WO-004 复权重算（2026-09-24）与 C-36 等事件按"留观影子表"处置后无 TTL/退役通道；YAML 头手工计数未随批更新（宪法 §4.4 文档矛盾=事故） | ①影子表退役流水线（archiver export→verify→drop 正门复用+7 天留观计时）；②品类 YAML 计数改生成器产出 | 2 天 | 影子表净删=Owner 门待裁；流水线可施工 |
| W2 | l2_tick 0 行空表 | 用途不明（tick_depth_5 才是五档落点） | waste_table_scanner 跑一轮+退役评审 | 0.5 天 | 待裁（净删归 Owner） |
| W3 | table_registry.validate_tasks_yaml 仅 WARN——双真源漂移不阻断（模块自述 Phase 4 升 block 未做） | 渐进式收紧停在 Phase 2 | 升 commit gate block（GATE-TABLE-NAME-REGISTRY） | 0.5 天 | 是（归 M3 门禁侧协作） |
| W4 | 病灶闭环核验：①tick/kline 1970+时区亿行事故→哨兵+修复**已闭环**；②news 死信→schema 缓存失效**已闭环**（防复发四件套②，:647-657；其余①③④仍未立项，2026-09-14 gap report :14-16）；③parts 爆炸→监控+周合并**已闭环**；④Code:181 断连→连接统一治本**已闭环**（2026-09-14） | — | — | — | — |

## 五、提速与合并机会

1. **macro_data 四表家族**（macro_data/compat/latest/vintage）+index_valuation_daily（v2+quar）同域多版本——按内收判据"同真源可派生→必并"评估收敛。
2. DDL 25 件 apply_* 可表驱动化（一器多 DDL 声明），与 schema_file 字段（business_data_categories.yaml 已有）打通=单一 DDL 声明面。
3. ch_reader/ch_writer 双文件 1700+ 行中 DESCRIBE 缓存/TSV 转义/列过滤三套逻辑重复——抽 shared 内核。

## 六、自审闸三态

**挖干可施工**（W3 升 block 可直开；W1 流水线施工可开，净删动作=待裁入 pending_rulings.md；W2 待裁）。

## 七、复核命令

```bash
export PATH="$LOCALAPPDATA/Programs/Python/Python312:$PATH"
python -c "
from zephyr.infrastructure.database_service import get_db_service
c=get_db_service().get_clickhouse_conn()
print(c.execute(\"SELECT database, count() FROM system.tables WHERE database NOT IN ('system','INFORMATION_SCHEMA','information_schema') GROUP BY database\"))
print(c.execute('SELECT count() FROM c1_market.tick_data'))"
grep -c "category_id" docs/03_modules/_cross_layer/database/business_data_categories.yaml  # 338
sed -n '161,178p' src/zephyr/infrastructure/database_service.py   # 唯一 Client 构造点
sed -n '647,657p' src/zephyr/data/ch_writer.py                    # 列缓存失效治本
```
