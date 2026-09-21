---
ttl: task_bound
title: 深度审查报告——I01 IntegratorScheduler 主调度
object: I01 IntegratorScheduler 主调度
target: src/zephyr/data/scheduler.py:449（类 IntegratorScheduler + 模块级 DAG 函数 L155-449 + main() L2445）
reviewer: GLM-5.3-Flash / st-deeprev-20260918
baseline: 2fa92002c3（HEAD=73d1d045 已前移；scheduler.py 较基线 +16 行=WORK-ORDER-3 配置指纹快照属他会话在途，按工作区现状审并备注）
date: 2026-09-18
status: 已审
---

# 深度审查报告：I01 IntegratorScheduler 主调度（GLM-5.3-Flash / 基线 2fa92002c3）

## 1 对象快照
- 范围：APScheduler 常驻编排主体——cron/interval 注册（L2096-2153）、交易日守卫（L169-201）、特殊时段分发（L204-310）、DAG 动态调度 `_run_schedule_dag`（L365-449）、任务执行 `run_task/_try_source`（L1444-1800）、断点续传/幂等清理（L1902-1964）、守护线程组（CH 探活/卡死 reap/本地回灌/破损 part）。排除项：监控端点+metrics=I02；backfill/catchup/integrity/consensus 内部=I11-I15。
- 协作模块已实读：task_queue.py、progress_store.py、buffered_writer.py、local_replay.py、ch_writer.py、ch_reader.py、schedule.yaml、tasks.yaml 调度分布（251 任务）。
- 测试覆盖：tests/zephyr/data/test_data_scheduler.py 存在；startup_probes=False 注入缝设计合理（#ARCH-DATA-015），未逐断言复核=长尾。
- 变更热力：99 commits（本批最高频，最近 2026-09-18）=反复返工高危区，与发现密度相符。

## 2 六轴审查日志表
| 轴 | 发现 | 锚点 | 级 | 验证法 |
|---|---|---|---|---|
| A | 幂等清理先 DELETE 后 fetch 非原子：删完 [start,today] 旧数据后 fetch 失败/进程崩溃 → 区间数据从 CH 消失至下次成功跑（Replacing 表豁免，仅 MergeTree+date_col 任务命中） | scheduler.py:1939-1964 | P2 | 挑 date_col 任务 run_task 中途 kill，查该日行数 |
| A | 上述 DELETE 返回值被忽略（delete_where 双通道失败仅 log；且 CH mutation 异步未等待完成即 INSERT）→ MergeTree 表双写/旧读窗口 | scheduler.py:1964 + ch_writer.py:954-982 | P2 | mock delete_where=False 跑单测，观察仍继续写入 |
| A | `_fetch_and_write` 遇 FetchResult.error 直接 break；因 last_error 非 None，L1672 的收尾 `writer.flush()` 被跳过——BufferedWriter 内存残留行随作用域丢弃，本地兜底也不触发；新闻类不可重放源=真丢数据 | scheduler.py:1978-1982,1672-1699 | P2 | 构造第二批 error，追第一批已 add 未 flush 行的去向 |
| A | `_compute_start_date` last_key 非 ISO 静默 start=today（窗口收窄无告警） | scheduler.py:1908-1914 | P3 | 手工写坏 last_key 跑 run_task 看日志 |
| E | 同源并发共享单 Provider 实例：`_get_provider` 缓存实例（L1209-1232），DAG 池 8 线程内同源任务并发 fetch；`meta.thread_safety="single_thread"` 声明无执行点强制 | scheduler.py:1209-1232 + provider_base.py:162,344-355 | P2 | grep thread_safety 消费点（仅展示）；同源两任务并行观察 QMT 会话错乱 |
| E | 单实例锁只在 main()/cli start 入口（L2465）；直接 `IntegratorScheduler().start()` 无屏障——双实例事故（#SCHED-DUAL-INSTANCE）口子收窄未封死 | scheduler.py:86-129,2462-2471 | P3 | 脚本直起两实例看双 task_runs |
| B | interval 型时段周末硬跳过 `weekday()>=5` 与日历注入（CAND-CRYPTO-001）矛盾：crypto 7×24 挂 interval 永不跑周末；当前 schedule.yaml 无 interval 槽=休眠缺陷 | scheduler.py:189-193 | P3 | interval 槽+crypto 日历单测复现 |
| B | 时区口径：`date.today()/datetime.now()` 裸本地时区遍布守卫/游标/窗口，机器 TZ≠CST 全链漂移（RULE-SCHEMA-TZ 只约束生成器，运行时无防线） | scheduler.py:185,190,1636,1909 | P3 | 拨 TZ 单测 |
| C | 多表写入 `total_rows += result.rows_fetched` 把旁表行数计入主任务指标=口径失真；0 行 SUCCESS 交易日 WARN+alerter（#ARCH-SILENT-SUCCESS）已闭环良好 | scheduler.py:2024,1735-1756 | P3 | 对比 task_runs.rows 与主表行数 |
| D | TRADING_DAY_GUARDED_SCHEDULES(9 槽) vs schedule.yaml 17 槽：不守卫槽各有注释声明，未见漂移 | trading_calendar.py:151-163 | 已查无 | 对表 |
| D | schedule.yaml `max_instances: 1`（3 处）调度器不读取（start 只取 cron/executor/type）=死配置键，靠 job_defaults=1 侥幸同语义 | scheduler.py:2096-2152 vs schedule.yaml L95,105,190 | P3 | 删键对比行为 |
| E | 局部 TaskQueue（#ARCH-CH-016 v2）方案核实无覆盖竞态；游标防超前推进（#ARCH-CURSOR-DRIFT）`rows>0 才推进`正确 | scheduler.py:384-427,2032 | 已查无 | 读码+并发单测 |

## 3 SOTA 对照
- 对照 Temporal/Airflow durable execution 惯例：本对象"游标断点续传+先删后写幂等+局部 DAG 队列"属 Airflow 式 task-retry+idempotent 设计；业界共识（Temporal retry policy 文档、ZenML 2025-2026 对比文）强调 retry 下 activity 须幂等或带幂等键——本对象幂等依赖"先删后写"但删写非原子（§2 行1），弱于 durable execution 的重放语义。结论：**立卡候选**（delete_where 结果纳入事务判定，或改原子去重写入）。来源：ZenML《Temporal vs Airflow》https://www.zenml.io/blog/temporal-vs-airflow（ZenML，2025-2026）；https://mlai.qa/blog/temporal-vs-airflow/（mlai.qa，2026）。
- APScheduler coalesce+misfire_grace_time=3600 配置与官方防风暴建议一致：**对等已有**（APScheduler 官方文档；未单独检索 URL=受阻如实记，检索预算已用于调度/CH 两题）。

## 4 缺陷清单（按严重级）
1. P2 幂等删写非原子+DELETE 返回值被忽略——影响全部 MergeTree+date_col 增量表；建议=失败即 FAIL 不写入+写后核 `system.mutations`；验证=mock 单测。
2. P2 同源 Provider 并发无互斥——爆炸半径=同源多任务时段；建议=per-source 互斥或 single_thread 分支加锁。
3. P2 error 路径缓冲丢弃——建议 break 前尝试 flush()/落地 fallback；爆炸半径=新闻/事件类不可重放源。
4. P3 组：interval 周末硬编码、裸本地时区、max_instances 死键、看门铃"今日"实为表内最新日（scheduler.py:1414，今日全缺时静默查昨日）、健康检查 age=None 源被永跳（scheduler.py:1517-1520）、限流睡眠持锁（provider_base.py:349-355）。

## 5 挂起疑问
- scheduler.py 含他会话在途 +16 行，若收口方 revert 需重验 L1088-1120 区域锚点。
- 特殊时段（catchup/backfill/integrity）不走 run_task 故无 task_runs 记录——是否 I14 任务级对账刻意排除，转 I14 判定。

## 6 完备性自评
六轴全查（A/B/C/D/E/F 均有结论）。长尾：test_data_scheduler.py 未逐断言；17 个 provider 工厂分支仅抽读（qmt_bridge 专列 I06）；policy_registry 内部未全读（grep 确认 register 无落盘，后果见 I03）。
