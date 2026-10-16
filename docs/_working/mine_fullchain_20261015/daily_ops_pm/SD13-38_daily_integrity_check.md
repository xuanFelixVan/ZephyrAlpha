---
ttl: task_bound
doc_type: mined_segment
parent_map: config/trading_day_cycle_map.yaml
segment: fig13-D (夜窗段)
node_id: D13-38
miner_lane: mine_fullchain_20261015/daily_ops_pm
created: 2026-10-15
---

# SD13-38 每日完整性巡检（只检测+告警，不补跑）

## 1. 定义

交易日 23:00（APScheduler 特殊槽 integrity_check）：全表达标巡检（动态发现真源清单），不达标
告警不动手。三路兜底分工的第三路：档期视角（D13-01）/行数视角（D13-35 有手）/只告警（本腿）——
其真源至今是排班文件散文注释，图 13 把它变成三条边（feedback edge D13-38→D13-35 在册）。
图内决策问题："23:00 巡检检出几条不达标？它自己动手吗？三路兜底边界谁在守？"——已知结构事实
（簿 09 3.3）：四路检测里只有 17:00 动手，23:00/23:30/06:50 一律落表/落文件。

## 2. 六向台账

### 2.1 输入面
- 全表当日数据达标面（动态发现真源清单，schedule.yaml:179 description）。
- 前置判定：当日各批次已跑完（否则误判缺——invalidation 在册，与 D13-35 同族误判面）。
- 入边：D13-37→D13-38（夜窗链）。

### 2.2 输出面
- 产物：巡检台账+告警通道（webhook 侧只认更高一级，故本腿落表即止）。
- feedback edge：D13-38→D13-35（23:00 只告警的行数缺口交给次日 17:00 行数视角补下载——三路
  兜底分工的第三条边）。
- consumers=count:11（code=9：src/zephyr/autonomy_core/context/integrity_check.py:2、
  src/zephyr/autonomy_core/context/local_llm_summarizer.py:4、
  src/zephyr/autonomy_core/context/__init__.py:49、
  src/zephyr/frontend/dashboard/api_server.py:1633）。

### 2.3 SSOT 真源
- config/trading_day_cycle_map.yaml#D13-38（wired/partial/🔨，downstream_action=alert_only）。
- 簿 09 3.3（四路检测只 17:00 动手）；骨架 §2 D13-38 行（三路分工真源=散文注释）。
- 槽契约：src/zephyr/data/config/schedule.yaml:175-179（L11，cron "00 23 * * 0-4"）；
  map 锚 :153/:159 已漂移（现 Wed monthly_static/注释行）。

### 2.4 代码模块
- module_ref=src/zephyr/data/integrity_checker.py（实存，"数据完整性巡检器——每天盘后检测全表
  当日数据是否达标"）。
- 槽面：schedule.yaml:176（integrity_check）；machine_facts：effective_task_count=0+
  special_branch_exists=true（特殊槽编排面，不入 tasks.yaml）。

### 2.5 门禁约束
- 图 laws 第 6 条适用：alert_only=设计上不动手（只检测+告警）——"检出即蒸发"风险由三路分工边
  （38→35）承接，缺该边即蒸发。
- gap_refs：benchmark:A7-no_drift_evidence 推广到巡检格；C1 alert/rerun 腿边界=本图三条边。
- casebooks=MEM-F13#断供补数。

### 2.6 自动化触发
- 机制=A_apscheduler 特殊槽；slot=integrity_check cron "00 23 * * 0-4"；calendar_guarded=true。
- trigger_facts：task_runs_30d=0（特殊槽不写计数面）；节拍证据=巡检台账落表面。

## 3. 自审闸三态（逐向）

| 向 | 态 | 判据 |
|---|---|---|
| 输入面 | pass | 动态发现清单+前置判定（误判条件）在册 |
| 输出面 | warn | 台账+webhook 落表即止；告警只认更高一级=低级缺口只在台账（可见性分级缺口） |
| SSOT 真源 | warn | 三路分工真源=排班文件散文注释（图已转三条边，但注释仍是原始真源） |
| 代码模块 | pass | integrity_checker.py 实存+槽面精确（:176） |
| 门禁约束 | warn | A7 no-drift 缺位推广到巡检格；alert_only 边界依赖 38→35 边承接 |
| 自动化触发 | warn | 特殊槽无计数面（task_runs=0），节拍靠台账面复核 |

## 4. 缺口与建议

- 本段 4 gap+11 未接线归属：不在主清单（wired）。
- 建议 1：把三路分工从散文注释升格为册面（三边已有，注释同步收敛），补 A7——巡检"零不达标"
  也落一行台账心跳（同 D13-G03 no-drift 同族）。
- 建议 2：webhook 只认更高一级的可见性分级留裁（C4）——低级缺口至少应有日报聚合出口，
  防"落表即止"变"落表即埋"。
