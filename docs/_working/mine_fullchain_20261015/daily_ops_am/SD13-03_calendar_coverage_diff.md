---
doc_type: mining_segment_doc
parent: docs/_working/mine_fullchain_20261015/00_skeleton.md
map_node: config/trading_day_cycle_map.yaml#D13-03
segment: fig13-A 盘前
mined: 2026-10-15
miner: daily_ops_am
ttl: task_bound
---

# SD13-03 交易日历逐日覆盖 diff

## 1. 定义

每日 07:10（全周）特殊槽 `calendar_coverage_check` 驱动日历覆盖检查器：对在册表族逐日 diff，治「补 max(date) 原理性失明」（只看最新日期会漏中间缺日）。决策问题：07:10 的逐日 diff 有没有检出缺日？检出之后动了谁的手？

地图在册态：wiring=wired、build=partial、downstream_action=detect_only、detection_evaporates=true（WARN 不落盘 + 报告 dict 被特殊槽分支丢弃=检出即蒸发）。

## 2. 六向台账

| 向 | 内容 | 文件路径证据 |
|---|---|---|
| 输入面 | 在册监控表名单（以机生 scanned 配置为准）+ 交易日历 + CH 表逐日行数 | `src/zephyr/data/calendar_coverage_checker.py`（run_coverage_checker）；`src/zephyr/data/trading_calendar.py` |
| 输出面 | 仅 WARN 日志行：alerter 对 WARN 不落盘、特殊槽分支只回 bool 并丢弃报告 dict——既无人看也无人修 | `tmp/scheduler_run.log`；`src/zephyr/data/scheduler.py:360-373`（实核：分支 `return {"calendar_coverage_check": bool(...)}`，报告 dict 未落任何面） |
| SSOT 真源 | 图13 节点契约（行 306-382）+ 外部对标表A-A7 同族登记 | `config/trading_day_cycle_map.yaml#D13-03`；`docs/_working/map_build/fig13_daycycle/01_盘前就绪链.md` |
| 代码模块 | 检查器执行体 + 调度器特殊槽分支（地图锚 scheduler.py:101/255，HEAD 实位 101 面属检查器内部、分支实位 360） | `src/zephyr/data/calendar_coverage_checker.py:101`；`src/zephyr/data/scheduler.py:360` |
| 门禁约束 | 无落盘面=审计不可达（表A-A7 no-drift 留痕缺口同族）；告警分级（WARN 不进 alerter 落盘） | `config/trading_day_cycle_map.yaml#D13-03` gap_refs/evidence；`AGENTS.md` §9 运维红线（留痕纪律） |
| 自动化触发 | mechanism=A_apscheduler，每日 07:10 全周；今晨 07:10 完成行 checked/breached 在日志（滞后 0）；30 日任务级 count=0（bool 返回无独立计数面） | `config/trading_day_cycle_map.yaml#D13-03` cadence_zh/trigger_facts |

## 3. 自审闸三态

| 向 | 态 | 依据 |
|---|---|---|
| 输入面 | pass | 监控名单与日历面齐备 |
| 输出面 | fail | 检出即蒸发：WARN 不落盘、报告 dict 被丢弃，产物方向零在位 |
| SSOT 真源 | pass | 节点契约完整，detection_evaporates 事实在册 |
| 代码模块 | pass | 执行体与分支实存实核（锚有漂移，本体在） |
| 门禁约束 | fail | 无留痕面可审：检出不可复核、不可追责，与运维红线留痕纪律冲突 |
| 自动化触发 | pass | 每日 1 拍滞后 0 在案 |

## 4. 缺口与建议

- 图13 全图缺口在本格的落点：无 G 节点；本格是「表达缺口 D13-G01（无产出证据态）」的同族案例——checked/breached 计数只在日志一闪。
- gap_refs 在册：benchmark:C1（detect_only 无落盘面，检出即蒸发，表A-A7 同族）。
- 建议：①分支把报告 dict 落 `data/failures/` 或专册（对齐 D13-02 的案卷面）；②breached>0 时升 ERROR 进 alerter；③监控名单与 D13-02 哨兵名单对齐治理（两名单差异即盲区清单，簿 01 O-4 在册先例）。
