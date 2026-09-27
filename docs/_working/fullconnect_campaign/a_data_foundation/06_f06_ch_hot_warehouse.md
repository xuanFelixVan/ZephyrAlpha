---
ttl: task_bound
title: "F06 CH 热库落库——253 表×四库×空壳表/影子表卫生债复飞案卷"
session: zc-l01-20260927
---

# F06 CH 热库落库（复飞案卷）

> 前序：M1 册 03_ch_warehouse.md+90_backfill_wave.md（三数互斥/影子表取证）；本卷=当日实测复核+空壳表 9 张新账。

## 一、六向台账（本日 DatabaseService 只读实测）

| 向 | 内容与实证 |
|---|---|
| 上游 | ch_writer.write_result/BufferedWriter/WalWriter 三路写入口+F04 四门禁放行行 |
| 下游 | 全仓经 DatabaseService.get_clickhouse_conn 唯一构造点（database_service.py:161-214，RBAC 三账号）；回测/模拟/仪表盘/派生 internal_compute 回写/F08 归档源 |
| 自动触发 | DataScheduler Running（写入承载）+CHHealthProbe **Running**（存活探针）+CH-OptimizeMerge-Weekly Ready+ch_parts_monitor（parts>100 告警） |
| 真源注册表 | 连接=config/.env.clickhouse（fail-closed）；品类=business_data_categories.yaml（category_id 338 实数）；消费层=table_registry.py（KeyError fail-closed）；DDL-as-Code=schemas/categories/*.py+apply_*_ddl.py 25 件 |
| 门禁质量尺 | 写前四门禁+列集缓存失效（ch_writer.py:647-657）+RBAC #ARCH-CH-027+RULE-SCHEMA-TZ（DateTime64(3)+双时区 14 处）；**表卫生尺**：waste_table_scanner（只登记永不自动删，裁定#380①/#382 逐表批制） |
| 运行状态 | **绿（带卫生债）**。四库=c0_meta 1+c1_backtest 16+c1_market **202**+c3_fundamental 34=**253 表**（本日实测；tick_data 8.95B 行）；主表 max_date=2026-09-24；影子表 8 张≈2,154 万行在库无 TTL；空壳表账见 §三 |

## 二、子模块三级枚举

1. 连接层：database_service（单例 atexit）/ch_config（裁定 #ARCH-CH-017/#019）/redis_config（H1 172.24.30.100 与 CH 同 VM）
2. 写入层：ch_writer.py（1131 行 TSV/DESCRIBE 缓存/HTTP fallback :792-815）/buffered_writer/wal_writer/tick_depth_writer/tick_redis_cache
3. 读取层：ch_reader/pit_query（≤1970-01-02 不可见 D1 裁定）/table_registry（validate WARN Phase 4 未升）
4. DDL 层：apply_*_ddl.py 25 件+apply_rbac+apply_timezone_migration
5. 运维层：optimize_merge/ch_parts_monitor/waste_table_scanner/verify_schema_truth/_data_inventory/_recovery_drill
6. 卫生债面：影子表 8 张（hfq legacy/preversion/quarantine 族，90 册逐表行数）+macro_data 四表家族+index_valuation 多版本+**空壳表 9 张**（§三）

## 三、接线四态独立复核

- 总册：built/P1/D6。独立复核：**built 成立**（写入链三班在产+census 主力 GREEN_WITH_DATA）。
- 骨架勘误⑧：总册/骨架写"**252 CH 表**"→90 册 09-25 实测 253→**本日复测仍 253**（c1_market 202）——252 为过期数，以 DatabaseService 实测为准。
- 空壳表 9 张新账（wiring §2.3-2+census 补齐）：ipo_schedule/msci_adjustment/stock_valuation/stock_candidate_pool/market_index_meta/margin_target_adjustment **6 张未登记 known_data_gaps.yaml**（本日 grep 复证六表均不在册且不在 tasks.yaml）+suspend/etf_benchmark（FALSE_GREEN 腿，schema 在数据零，etf_benchmark date 列 ALL_NULL）+第 9 张 l2_tick（census 复核补齐；l2_tick **已**在 known_data_gaps 且 l2_tick_snapshot 任务在册=未知 capability FAILED 腿）。
- 勘误⑨：90 册 §3.2 记"202 vs 338 vs 114 三数互斥"至今未收敛（品类 YAML 头注仍写 114，本日 grep 338/CH 202 复证成立）——计数生成器化义务持续挂账。

## 四、缺口清单

| # | 缺口 | 处置 | 级 |
|---|---|---|---|
| W1 | 空壳表 6 张补登记 known_data_gaps 为前置，随后逐表建腿 vs 退役 | 施工（补登记）→Owner 门（建腿/退役逐表裁） | P0 |
| W2 | FALSE_GREEN 3 腿落点（suspend 3 腿/etf_benchmark schema 在数据零） | 施工：与 F01 G1 假绿交叉尺同袋+C4 修 | P0 |
| W3 | 影子表 8 张 2,154 万行无 TTL | 施工：五步退役判据流水线（90 册 §3.4）；净删=Owner 门（R-M1-01） | P1 |
| W4 | 三数互斥（202/338/114） | 施工：计数生成器化 | P1 |
| W5 | validate_tasks_yaml 仅 WARN | 施工：升 block gate（归 M3 协作） | P2 |
| W6 | kline_weekly/monthly_hfq 补 lineage_version 列 | Owner 门（wiring §2.3-1 DDL 项） | P1 |

## 五、自审闸三态

挖干可施工（本日实测 253 表+空壳 6 张未登记复证）；W1 补登记/W3 流水线/W4 生成器可施工；净删与 DDL=Owner 门。勘误两条（253 表/三数互斥持续）已登记。

## 六、复跑命令

```bash
export PATH="$LOCALAPPDATA/Programs/Python/Python312:$LOCALAPPDATA/Programs/Python/Python312/Scripts:$PATH"
python -c "
from zephyr.infrastructure.database_service import get_db_service
c=get_db_service().get_clickhouse_conn()
print(c.execute(\"SELECT database,count() FROM system.tables WHERE database LIKE 'c%' GROUP BY database ORDER BY database\"))"
grep -c "category_id" docs/03_modules/_cross_layer/database/business_data_categories.yaml   # 338
sed -n '7,11p' docs/03_modules/_cross_layer/database/business_data_categories.yaml          # 头注 114
python - <<'EOF'
import yaml
shells=['ipo_schedule','msci_adjustment','stock_valuation','stock_candidate_pool','market_index_meta','margin_target_adjustment']
g=open('src/zephyr/data/config/known_data_gaps.yaml',encoding='utf-8').read()
print([s for s in shells if s not in g])   # 6 张未登记
EOF
```
