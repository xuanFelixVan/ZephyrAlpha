---
ttl: task_bound
doc_type: report
title: 深度审查报告——I07 Tick 订阅器
object: I07 Tick订阅器
target: src/zephyr/data/tick_subscriber.py:225（TickSubscriber + BridgeTickSource L1453 + main L1737）
reviewer: GLM-5.3-Flash / st-deeprev-20260918
baseline: 2fa92002c3（HEAD=73d1d045；按工作区现状审）
date: 2026-09-18
status: 已审
---

# 深度审查报告：I07 Tick 订阅器（GLM-5.3-Flash / 基线 2fa92002c3）

## 1 对象快照
- 范围：盘中高频采集全链——xtdata 回调→queue→flush 批转换→WalWriter（先落盘后异步 drain）；桥模式尾读（offset 增量+残行回退+timetag 去重）；业务心跳+看门狗自愈；五档旁路（TICK_DEPTH5=1）。
- 测试：tests/zephyr/data/test_tick_subscriber.py 存在（Stage 4 公共化别名缝设计良好）。
- 变更热力：36 commits（高频返工区）；当前生产=桥模式（9/8 起唯一实时源）。

## 2 六轴审查日志表
| 轴 | 发现 | 锚点 | 级 | 验证法 |
|---|---|---|---|---|
| E | **P2 xtdata 模式午休重订阅风暴**：`_is_market_open_now` 包络=09:30-15:00 含午休（注释自认"含午休"），午休 90 分钟无 tick → idle>300s → 每 15s 循环清空重订阅全市场 ~8400 只（9 批 whole_quote）→ 单午休 ~360 次全市场重订阅，无冷却/退避（universe 路径有退避、重订阅路径没有）。当前桥模式分支跳过（L865-869）=休眠缺陷，回切 xtdata 即触发 | tick_subscriber.py:791-808,863-892 | P2 | xtdata 模式下拨钟至午休看日志 resub 频次 |
| B | **P2 WAL critical 背压=唯一真丢数据路径**：队列满已改溢出暂存（A4b），但 WalWriter.add 因 WAL 容量≥90% 背压拒绝时 `_drain_batch` 直接判丢（L559-561 计 dropped）——CH 长时间断供（WAL 2GB 上限）后 tick 数据持续真丢（有 metrics 有日志，属"可观测的丢弃"） | tick_subscriber.py:555-562 + wal_writer.py:69,249-253 | P2 | 人为填满 WAL 目录看 dropped 增长 |
| A | 桥 offset 时序=读 chunk→先存 offset→再入队：崩溃窗口丢 chunk（at-most-once）；offset 写失败则重启重读，但 `_last_timetag` 内存态清零→重读段重复入库（at-least-once）——两种语义并存无文档 | tick_subscriber.py:1606-1633,1517-1536 | P3 | kill -9 于两窗口分别复现 |
| B | 时区口径：fromtimestamp/datetime.now 裸本地时区（timetag 注释自认"本地时区解释，QMT 时间=北京时间"）——机器 TZ≠CST 则 trade_date/延迟分析全错 | tick_subscriber.py:181-186,1693-1716 | P3 | 拨 TZ 单测 |
| A | `_timetag_to_epoch_ms` 数字提取归一（17 字符/14 位/毫秒尾缀）边界处理完备；`len<14` 拒绝 | tick_subscriber.py:1693-1716 | 已查无 | 单测 |
| E | 看门狗自愈链（业务心跳 15s+无 tick 重订阅+0 标的指数退避 #117）与 #ARCH-DATA-017 三裁定对齐，心跳 JSON 含 mode/last_tick_age_s 供 deadman 判活——治"活进程零采集"历史放大器 | tick_subscriber.py:810-943 | 已查无 | 停桥文件写侧看心跳字段 |
| C | 方向列硬编码"中性盘"——QMT 不提供，已声明为已知限制；volume 负值过滤（UInt64 溢出 #ARCH-CH-033）在 backfill 侧有、订阅侧 tick_to_row 无同款过滤（依赖上游无损） | tick_subscriber.py:215 vs backfill_checker.py:477-483 | P3 | 对照两处转换器 |
| D | main() docstring/argparse help 仍写 ticks.csv（v18）——#BRIDGE-WRONG-FILE 后 ENV_CONFIG 已升级 v19，说明文本未跟（文档漂移=前科同族） | tick_subscriber.py:1741-1758 vs 1480-1483 | P3 | 读码对照 |
| E | stop() 收尾顺序正确（先停尾读→flush 溢出→WAL stop）；flush 线程 join 30s 超时后队列残留丢失（极端） | tick_subscriber.py:1262-1322 | P3 | 大队列下 stop 计数 |
| B | 新鲜度闸门只 WARNING 留痕不告警不重连——"沙箱停摆可见"依赖人盯日志/guard 消费心跳；告警链依赖 deadman（外部） | tick_subscriber.py:1718-1734 | P3 | 停沙箱策略看是否有主动告警 |

## 3 SOTA 对照
- 桥模式（文件桥尾读+offset 边车+撕裂行处理+去重）与低延迟行情采集的 ring-buffer/WAL 惯例对等：先落盘后上库（WAL-first）是标准做法。**对等已有**。来源：量化行情系统工程通识+Kafka/WAL 持久化范式（未单独检索 URL=受阻如实记，检索预算已用于 I01/I08）。
- 回调线程最小工作量（put_nowait）+无锁计数：与交易所 feed handler 惯例一致。**对等已有**。

## 4 缺陷清单
1. P2 午休重订阅风暴（xtdata 模式，休眠）：修法=看门狗加午休时段排除或 resub 冷却（如 5min）。触发剧本=miniQMT 回切窗口。
2. P2 WAL 背压真丢：修法=背压时把批转存独立溢出 WAL（已有 deque 机制可复用）或至少 CRITICAL 告警升级（当前仅 log.error+metrics）。
3. P3 组：offset 时序双语义、裸时区、v18 文档残留、stop 超时残留、新鲜度闸门不接告警。

## 5 挂起疑问
- 五档旁路 depth_writer 实际开关状态（TICK_DEPTH5 环境变量）未在运行环境核实；其写入质量门禁同样走 WalWriter（旁路）=I08 旁路发现关联项。

## 6 完备性自评
六轴全查。长尾：wal_writer.py 342 行仅骨架级审（锁/背压/复用 local_replay 已核）；SourceSwitcher/BackupTickPoller 双源切换链未审（P1-3 可选装配，当前未见装配证据）；test_tick_subscriber.py 断言强度未逐条审。
