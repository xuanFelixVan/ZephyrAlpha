---
ttl: task_bound
title: 深度审查报告——TF03 intraday_sector板块分钟族(5任务)
object: TF03 intraday_sector 板块分钟K任务族
target: src/zephyr/data/config/tasks.yaml:2299-2372（kline_sector_{1,5,15,30,60}min_incremental）；schedule.yaml:47-50
reviewer: GLM-5.3-Flash / st-deeprev-20260918
baseline: 2fa92002c3（HEAD=b80084c0df；按工作区现状审；任务书锚 2147-2207 已漂移，实锚=2299-2372）
date: 2026-09-18
status: 已审
---

# 深度审查报告：TF03 intraday_sector板块分钟族（GLM-5.3-Flash / 基线 2fa92002c3）

## 1 对象快照
- 实测 **5 任务**（1/5/15/30/60min，tasks.yaml:2299-2372），全部 `source: tdx`、capability 同名 `kline_sector`、写同表 `c1_market.kline_sector_intraday`（period 列区分）。mootdx index_bars TCP 直连（不依赖 tdx 客户端盘后文件，tasks.yaml:2291-2294）。executor=intraday_sector(2线程) 独立池（schedule.yaml:47-50；scheduler.py:2200）。
- 代表深查=tdx_provider.py（_resolve_sector_symbols:295、include_industry_boards 旗标:321-337、CapabilityContract("kline_sector")）。

## 2 六轴审查日志表
| 轴 | 发现 | 锚点 | 级 | 验证法 |
|---|---|---|---|---|
| B | **同厂通道退化前科在案**：2026-09-11 日K任务 kline_sector_incremental 因"mootdx 对 K 线请求回 0 行（三次实证）"换道 tqcenter（tasks.yaml:873）。本族 5 任务仍走 mootdx——虽为不同访问路径（TCP 直连 index_bars vs tqcenter SDK），但同属通达信系，0 行退化风险同源 | tasks.yaml:873 vs 2291-2294 | P2 | 跑 `run_task("kline_sector_1min_incremental")` 数返回行数 vs 594+132 板块预期 |
| E | **0 行静默成功面**：mootdx 退化模式=回 0 行而非抛错。调度器对 0 行=SUCCESS+WARN（交易日 gate 内才 notify，scheduler.py:1749-1756）——非交易日/节假日被 gate 合理压噪的同时，若通道恒 0 且告警被当成"节假日合法空转"误读，退化可潜伏。表级兜底=integrity_check 对 kline_sector_intraday 的当日行数阈值 | scheduler.py:1735-1756；integrity_checker.py:153-200 | P2 | 观察近 5 日 kline_sector_intraday 当日行数稳定性 |
| A | 时段守卫缺口：`intraday_sector` **不在** TRADING_DAY_GUARDED_SCHEDULES（trading_calendar.py:151-163 九元素无它），节假日 cron 照触发（9-15 点 0-4 周内）；5 任务也无 trading_day_only。节假日空跑→mootdx 返回旧数据或 0 行→0 行 WARN 被交易日 gate 抑制=安静通过。影响小（写幂等/无数据）但属守卫清单遗漏 | trading_calendar.py:151-163；tasks.yaml:2299-2372（无 trading_day_only） | P3 | 法定节假日看日志有无 intraday_sector 批次空跑 |
| D | _filter_schedule_tasks 的拼写防护只覆盖 miniqmt/qmt_bridge 两源（scheduler.py:346-357），tdx 源在非守卫时段缺 trading_day_only 不会被告警——防护面与新源扩容不同步 | scheduler.py:346-357 | P3 | grep 该 frozenset 字面量 |
| A | 5 任务共 capability=kline_sector 靠 extra.period/count 参数化路由（tdx_provider 295-352）——同 capability 多周期复用使启动契约校验（supports_incremental 等合约）无法按周期区分，属设计取舍非缺陷 | tdx_provider.py:295-352 | 已查无 | 读 tdx meta |
| C | include_industry_boards=true 并入 132 条 8803/8804 行业板，SSoT=sector_code_bridge.TDX_INDUSTRY_BOARDS（tasks.yaml:2295-2297）；逆势榜消费链已接线——下游单点但来源有 SSoT | tasks.yaml:2295-2312 | 已查无 | grep TDX_INDUSTRY_BOARDS 消费方 |
| E | 告警被动化（无推送通道，alerter.py:28-29）复用系统发现 S1（TF01 报告 §2 E 行定义）。 | alerter.py:28-29 | P2 | 同 TF01 |

## 3 SOTA 对照
- 受阻（未检索）。mootdx/TDX 板块指数（880xxx）为国内特产数据源，无国际对标对象；"独立执行器防慢任务阻塞"设计与分池隔离惯例对等（训练记忆陈述）。

## 4 缺陷清单
1. P2 mootdx 通道退化监控：建议给本族加"当日板块数<594"专用哨兵（data_supply_sentinel.yaml 加一行表级阈值即可，现配置 16 表未含 kline_sector_intraday）→验证法=人为清空当日行看 06:50 哨兵是否报。
2. P3 intraday_sector 加入 TRADING_DAY_GUARDED_SCHEDULES（或给 5 任务补 trading_day_only: true）。
3. P3 拼写防护 frozenset 扩到 tdx/tqcenter。

## 5 挂起疑问
- 9/11 mootdx 0 行退化的根因结论（SDK vs TCP 通道）未见归档文档——若 TCP 直连同样退化过，本族风险升级 P1。

## 6 完备性自评
六轴全查（F 受阻）。长尾：mootdx index_bars 返回字段与表 DDL 列序逐列核未做；594+132 板块清单与 sector_constituent 表一致性对账未做。

## 7 收口裁定（收口方填）
- 三态逐条:
- 修复 commit:
- 复检结论:
