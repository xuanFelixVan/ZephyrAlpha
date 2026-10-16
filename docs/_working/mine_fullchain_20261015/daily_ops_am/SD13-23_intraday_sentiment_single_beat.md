---
doc_type: mining_segment_doc
parent: docs/_working/mine_fullchain_20261015/00_skeleton.md
map_node: config/trading_day_cycle_map.yaml#D13-23
segment: fig13-B 盘中
mined: 2026-10-15
miner: daily_ops_am
ttl: task_bound
---

# SD13-23 盘中情绪环单拍（有节拍席位、无节拍）

## 1. 定义

dloop 盘中族段 `sentiment_loop`：盘中情绪环单拍执行体就绪（run_once），**无节拍**——段注释自陈「单拍就绪没节拍——本段=节拍席位」。唯一调用方是 dloop；无业务日记号，每次调用即一拍。自动圈下每交易日恰 1 拍且落在收盘后 16:45–16:50 窗（feedback 边 D13-32→D13-23 的段界折叠）；人工日另有盘中三拍。决策问题：盘中有没有拍？每日几拍？拍落在什么时刻？

地图在册态：wiring=partial、build=partial、red_reason=unwired、cadence_gap=true（盘中应产 N 拍实产 0）。

## 2. 六向台账

| 向 | 内容 | 文件路径证据 |
|---|---|---|
| 输入面 | 情绪采集产物（D13-17 快新闻族供料+情绪环上下文） | `src/zephyr/plan_engine/daily_loop_master_switch.py:274`（地图锚）；`src/zephyr/data/intraday_sentiment_loop.py`（run_once 导入实核 :329） |
| 输出面 | 情绪环单拍产物（无业务日记号，调用即一拍）；自动圈产物落收盘后窗 | `config/trading_day_cycle_map.yaml#D13-23` evidence（簿 07 1.6 表段 10） |
| SSOT 真源 | 图13 节点契约（行 1816-1887）+ 簿 07 段 10 + fail_open_register 消费注 | `config/trading_day_cycle_map.yaml#D13-23`；`docs/01_policies_and_standards/_registry/catalogs/fail_open_register.yaml:329`（消费者在册）；`docs/_working/map_build/fig13_daycycle/07_dloop十六段解剖.md` |
| 代码模块 | _stage_sentiment_loop 段（「节拍席位」docstring 实核 :323-329） | `src/zephyr/plan_engine/daily_loop_master_switch.py:323-329`；daily_loop_master_switch.py:472（段注册表实核） |
| 门禁约束 | cadence_gap=true 在册=席位无节拍的结构缺口显式化；PHASE_STAGES 盘中族序 sentiment_loop 在 auction_hit 前（与环节编号逆向的段序契约边） | `config/trading_day_cycle_map.yaml#D13-23` cadence_gap；feedback_loops D13-23→D13-20 边注 |
| 自动化触发 | mechanism=C_inprocess_stage（dloop_stages=[sentiment_loop]）；observed=每日恰 1 拍（收盘后）；盘中零拍；no_count_reason=进程内段无独立产物表面 | `config/trading_day_cycle_map.yaml#D13-23` cadence_zh/trigger_facts |

## 3. 自审闸三态

| 向 | 态 | 依据 |
|---|---|---|
| 输入面 | pass | 情绪供料链（D13-17 等）在产 |
| 输出面 | fail | 盘中应产 N 拍实产 0（自动圈唯一一拍在收盘后=盘中语义空转） |
| SSOT 真源 | pass | 节点契约+簿 07+段注释三方一致（缺口是显式登记的，非漂移） |
| 代码模块 | pass | run_once 执行体实存实核 |
| 门禁约束 | warn | cadence_gap 显式在册但无补偿机制（fallback=无，盘中零拍无兜底器） |
| 自动化触发 | warn | 触发关系存在（16:45 圈）但时点与段语义（盘中）错位——段界折叠的直接受害格 |

## 4. 缺口与建议

- 图13 全图缺口在本格的落点：本格自身 red_reason=unwired（cadence_gap 型，非 no_caller/slot_hollow 计数项）；benchmark:A4（盘中应产 N 拍实产 0）。
- 建议：①给 sentiment_loop 配真实盘中节拍（如 60 分钟K唤醒词族或独立 30 分钟间隔触发器）——触发器接线归 dloop/调度器车道；②若 Owner 认可「收盘后单拍」为现行语义，则回写段名与 decision_question（去掉「盘中」误导），消除席位与节拍的语义错位。
