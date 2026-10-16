---
doc_type: mining_segment_doc
parent: docs/_working/mine_fullchain_20261015/00_skeleton.md
map_node: config/trading_day_cycle_map.yaml#D13-17
segment: fig13-B 盘中
mined: 2026-10-15
miner: daily_ops_am
ttl: task_bound
---

# SD13-17 事件驱动快新闻 + EDB 轮询

## 1. 定义

7×24 每 3 分钟 DAG 槽 `event_driven`（10 个有效任务）轮询快新闻与 EDB 宏观事件——全图最高频采集格（30d 61,335 拍）。结构约束：调度器「一任务只属一槽」由精确字符串匹配强制，故无法做盘中/盘后双节拍；提速至 3 分钟的理由=单轮耗时留余量（槽注释自证）。决策问题：快新闻轮询在转吗？全局 3 分钟与盘后多跑的取舍是什么？

地图在册态：wiring=wired、build=partial、tdm_refs=TDM-E-L9-A09；挂 G04 生产者腿。

## 2. 六向台账

| 向 | 内容 | 文件路径证据 |
|---|---|---|
| 输入面 | 快新闻源+EDB 宏观事件源（7×24） | `src/zephyr/data/news_collector.py`；`src/zephyr/data/config/schedule.yaml:57-59`（槽声明） |
| 输出面 | 新闻/事件表族（真表当日 FINAL 千行级，簿 04 三证齐）；下游清洗/比对族 20 个代码消费者 | `src/zephyr/ai_layer/cleaning/washer.py:8`、`auditor.py:10`、`comparator/compare_events.py:9`、`comparator/executor.py:9`（地图 consumers 在册） |
| SSOT 真源 | 图13 节点契约（行 1381-1456）+ 幽灵引用交叉登记（D13-G04：册面 c1_market 前缀新闻表不存在，真身在 c3_fundamental，改册面归图 12） | `config/trading_day_cycle_map.yaml#D13-17` gap_refs xref + D13-G04 节点 |
| 代码模块 | 采集器+调度器 DAG 槽（10 任务） | `src/zephyr/data/scheduler.py:491`（地图锚）；`src/zephyr/data/config/schedule.yaml:57` |
| 门禁约束 | 一任务一槽（精确字符串匹配强制）=双节拍不可能的结构约束；单轮耗时与 3 分钟节拍的余量取舍 | `src/zephyr/data/config/schedule.yaml:57-59`（槽注释）；`config/trading_day_cycle_map.yaml#D13-17` note_zh |
| 自动化触发 | mechanism=A_apscheduler，7×24 每 3 分钟；30d count=61,335（×10）；in_catchup_universe=true（always_on 桶，fallback=D13-01） | `config/trading_day_cycle_map.yaml#D13-17` trigger_facts/machine_facts |

## 3. 自审闸三态

| 向 | 态 | 依据 |
|---|---|---|
| 输入面 | pass | 7×24 高频 firing（61,335 拍/30d） |
| 输出面 | pass | 真表当日千行级在产（簿 04 生产者腿三证齐） |
| SSOT 真源 | warn | 供给本体健康，但册面引用名是幽灵（c1_market.news_data 不存在）——缺陷在引用名不在供给，地图明示不得据此下调本格态 |
| 代码模块 | pass | 采集器+槽实存实核 |
| 门禁约束 | warn | 幽灵名改册面归图 12/图 9 册处置权，本图只挂生产者腿——跨图治理悬置中 |
| 自动化触发 | pass | 每 3 分钟+可补跑 |

## 4. 缺口与建议

- 图13 全图缺口在本格的落点：**D13-G04（新闻产物表库名前缀写错的幽灵引用，segment=B）挂生产者腿于本格**（edges D13-17→D13-G04）；另 benchmark:A2（下游情绪窗原料新鲜度分级未接线）。
- 建议：①幽灵名改册走图 12 簿 11 §1-D 处置通道（本段无权改册，只在消费端防呆：按错库名订阅的消费者读到空表应报错而非静默）；②3 分钟全局节拍 vs 盘后多跑的取舍留一个 Owner 级注记（地图 decision_question 已问，无答主）。
