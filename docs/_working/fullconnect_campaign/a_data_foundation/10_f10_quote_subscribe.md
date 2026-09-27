---
ttl: task_bound
title: "F10 行情订阅分发——tick 常驻×桥模式×WAL 落盘复飞案卷"
session: zc-l01-20260927
---

# F10 行情订阅分发（复飞案卷，首次单独立卷）

> 前序：M1 册 01_ingest.md D10 面（tick 链）；本卷按总册职责独立立卷+本日复核。

## 一、六向台账

| 向 | 内容与实证 |
|---|---|
| 上游 | 券商行情源：xtdata（大 QMT）与桥文件 E:\qmt_bridge_sim\ticks3.csv（bridge 模式，tick_subscriber.py:1456 尾读+字节 offset 增量+timetag 去重）双模 |
| 下游 | wal_writer 段文件 drain→ch_writer 落 tick_data（8.95B 行）/tick_depth_5；tick_redis_cache H1 热缓存（盘中直供决策链）；local_replay 回灌 |
| 自动触发 | ZephyrAlpha_TickSubscriber **Running**（本日 schtasks 实测，桥模式 TICK_SOURCE=bridge，INARIANTS 行 8 自证）；ZephyrAlpha_QMTWatchdog Ready；wal_writer drain 线程进程内 |
| 真源注册表 | tick_subscriber.py（85KB 双模式）+wal_writer.py（段文件+drain）+buffered_writer.py+tick_depth_writer.py+tick_redis_cache.py；wal_codec/ 子包（codec_registry/tsv_codec）；qmt_bridge 2 任务+tick 桥（tasks.yaml 实查） |
| 门禁质量尺 | P0-1 主动落盘（WalWriter）；timetag 去重判重；tick 14 字段判重正门兜底（F05）；bdpan tick 看门狗 OS 任务 2026-09-24 已退役（known_data_gaps 头注），tick 深史缺口须人工触发=M1 册 B2 疤痕 |
| 运行状态 | **绿**：TickSubscriber Running+tick_data 实时链在产；TradingWatchdog Disabled（miniQMT 清退遗留，R-M1-07 在案） |

## 二、子模块三级枚举

1. 订阅核：tick_subscriber.py（xtdata/bridge 双模；INARIANTS）；qmt_bridge_provider.py（采集侧）
2. 落盘链：wal_writer.py→wal_codec/{codec_registry,tsv_codec}→buffered_writer→ch_writer；tick_depth_writer.py（五档）
3. 热缓存：tick_redis_cache.py（H1 db0 sim/db1 live/db2 治理）+infrastructure/redis_config（fail-closed）
4. 回灌/replay：local_replay.py；tick_depth_backfill.py（implementations/）
5. 备援：redundant_source/backup_tick_poller.py+heartbeat_monitor.py（断线备援族）
6. 相邻：姊妹定版卷 D-05 判 market_data（20 py）并入 F03/F10 消解双真源嫌疑——本卷登记待裁勿改总册；l2_tick_snapshot 任务（FAILED 腿"未知 capability"）挂 F01 census 账非本环节。

## 三、接线四态独立复核

- 总册：built/P1/D10。独立复核：**built 成立**（常驻 Running+落盘链全件在盘+H1 e2e 测试在册）。
- 复核与总册 F77 关系：F77"数据调度常驻"=scheduler+tick+槽位聚合环节（I 段），与本环节代码域同源——总册 DAG 已正确分列（F10 盘中直供/F77 调度常驻），无重复立卷冲突；本卷只挖 F10 数据面，F77 归 L08 带。
- 疤痕复核：M1 册 B2（tick 深史缺口人工触发）本日复核仍成立（bdpan 退役无替代触发器）。

## 四、缺口清单

| # | 缺口 | 处置 | 级 |
|---|---|---|---|
| T1 | tick 深史缺口无自动触发器（bdpan 看门狗退役） | 施工：挂 supply_sentinel 盲点腿或 catchup_guard 档期 | P1 |
| T2 | TradingWatchdog Disabled 未退役登记 | 施工：退役登记或立桥版新件（R-M1-07） | P2 |
| T3 | pause/resume 与 source_circuit_breaker 双轨熔断不感知 | 施工：合并熔断状态真源（policy_registry 单例落点现成） | P2 |
| T4 | market_data 双真源嫌疑消解 | 挂起+解锁=裁-5 打包（L00 D-05 并入判） | P1 |

## 五、自审闸三态

挖干可施工（常驻态 schtasks 实测+五件落盘链实列）；T1/T2/T3 可施工；T4 挂起。首次单独立卷，01 册沿用处已注明。

## 六、复跑命令

```bash
powershell -NoProfile -Command "Get-ScheduledTask |? {\$_.TaskName -match 'TickSubscriber|QMTWatchdog|TradingWatchdog'} | ft TaskName,State"
grep -n "TICK_SOURCE\|INARIANTS" src/zephyr/data/tick_subscriber.py | head -5
ls src/zephyr/data/wal_codec/ src/zephyr/data/redundant_source/
export PATH="$LOCALAPPDATA/Programs/Python/Python312:$PATH"
python -c "
from zephyr.infrastructure.database_service import get_db_service
print(get_db_service().get_clickhouse_conn().execute('SELECT max(trade_time) FROM c1_market.tick_data'))"
```
