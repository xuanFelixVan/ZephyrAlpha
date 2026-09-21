---
ttl: task_bound
title: 深度审查作业簿——任务水位存储
owner: st-deeprev-20260918
created: 2026-09-18
---

# 深度审查报告：任务水位存储（I19）

- 状态: **已审**
- 级别: P2｜类型: 存储
- 基线 commit: 2fa92002c3（工作区 HEAD=b80084c0df）
- 审查者: GLM-5.3-Flash / st-deeprev-20260918
- 入口锚点: `src/zephyr/data/progress_store.py:57`（ProgressStore 类）
- 生产调用方: zephyr.data.scheduler（:508-510 启动 reap、:1640 start_run、:1678/:1705/:1727/:1780 save_progress、:1908 get_last_key、:2036 RUNNING 水位）、zephyr.data.cli（status/rerun-failed 读）
- 测试文件: tests/zephyr/data/test_progress_store.py
- 备注: —

## 1 对象快照

- 审查范围：`progress_store.py` 全文 397 行：SQLite WAL 单连接+threading.Lock 全读写串行化，task_progress（UPSERT 水位）/task_runs（运行史）两表，reap_stale_runs 卡死清理，模块级单例。
- 排除项：scheduler 侧断点续传编排（`_compute_start_date`/DEFERRED_PERSISTENCE 流）作为上游消费方只审契约；BufferedWriter/local_replay 归 I23。
- 测试覆盖概况：单测在（含 conn 属性验证）；reap 竞态/错误降级路径未见覆盖。
- 材料包缺项：无运行时证据包（integrator_progress.db 实际行量未查——生产 DB 只读访问未获授权，用代码侧推断）。
- 变更热力：中热区（Phase 3-B reap 治本、SQLITE_MISUSE 锁修复两个历史治本批）。

## 2 六轴审查日志表

| 轴 | 发现 | 证据锚点 | 严重级 | 验证法 |
|---|---|---|---|---|
| B 上游 | last_key 契约无校验且消费端危险降级：last_key 非 ISO 日期时 `_compute_start_date` 返回 `(today, last_key)`——增量任务从今天拉=静默跳过 last_key→today 的全部历史断档（缺陷在 scheduler，根在水位契约未防御） | scheduler.py:1908-1914 + progress_store.py:134-148（存入侧不校验格式） | P1 | 存一行 last_key='garbage' 后跑增量任务，观察 payload.start=today |
| A 深度 | get_last_key/get_task_status 错误时返回 None=「从未运行」语义：SQLite 瞬时故障（锁忙/磁盘满/库损坏）被解读为无水位→增量任务静默降级为"月初全量"重拉（幂等表可救，非幂等表如 news 产生重复）；错误与从未运行不可区分 | progress_store.py:146-148, 158-160 | P2 | 对 get_last_key 注入 sqlite3.OperationalError 桩，观察返回 None |
| E 对抗 | reap_stale_runs 误伤活跃任务：task_progress 每 task_id 一行——旧 run 卡死超 24h 被 reap 时，若同 task_id 的新 run 已重启并写入 last_status='RUNNING'，Step 3 会把**新 run 的进度行**改标 STALE | progress_store.py:348-355（条件仅 last_status='RUNNING'，不区分 run 归属） | P2 | 造旧 RUNNING run+新 run 双记录，跑 reap 验证进度行被误标 |
| E 对抗 | reap 多语句无事务（autocommit 模式）：逐条 UPDATE 中途崩溃→部分 STALE；幂等可重跑救回，低危 | progress_store.py:339-356 + :76（isolation_level=None） | P3 | code review |
| C 下游 | DEFERRED_PERSISTENCE 水位语义：CH 写失败但本地持久化成功时 last_key 照常前进（scheduler.py:1678-1682 传 latest_key）——若 local_replay 回灌链死亡，水位已前进→断档被水位"已到"掩盖（5510 件滞留史案的存储侧同谋结构） | scheduler.py:1674-1682 + progress_store.py:164-207（save_progress 不区分数据是否真落 CH） | P2 | DEFERRED 后查 task_progress.last_key 已前进且 status=DEFERRED_PERSISTENCE；停回灌器观察水位不再回退 |
| A 深度 | task_runs 无 TTL/归档：run 史无限增长（每任务每日 N run，多年级百万行）；list_recent_runs ORDER BY started_at（字符串比较）依赖 isoformat 格式恒定 | progress_store.py:100-115, 254-264 | P3 | 查生产 db 行量（收口方执行） |
| B 上游 | now_utc() 带 tzinfo → isoformat 含 '+00:00' 后缀，与 `started_at < ?` 字符串比较一致的前提是所有写入同格式；register_sqlite_datetime_str_adapter 的适配口径若与 isoformat 输出不同（空格分隔 vs T 分隔）会破坏比较 | progress_store.py:186, 213, 321-323 + time_utils.py:109-117（注释自述"空格分隔"格式） | P2 | 对比 now_utc().isoformat() 与 adapter 产物格式，若一个是 `2026-09-18T..+00:00` 另一个是 `2026-09-18 ..`，reap 的 `<` 比较全错 |
| A 深度 | conn 属性裸暴露底层连接（绕过 _lock）：头部记载的 SQLITE_MISUSE 并发 bug 可经此再入；注释"只读暴露供测试"无机制强制 | progress_store.py:122-125 | P3 | 多线程经 .conn 并发 execute 复现 misuse |
| E 对抗 | get_store(db_path) 非 None 时整体替换单例且旧实例不 close：生产误传路径参数→全局水位库被静默切换+旧连接泄漏 | progress_store.py:386-397 | P3 | code review |
| A 深度(测试) | 未覆盖：reap 与新 run 并存、错误降级路径、时间格式比较边界 | tests/zephyr/data/test_progress_store.py | P3 | grep 测试无上述用例 |

## 3 SOTA 对照

| 对照项 | 结论 | 来源 |
|---|---|---|
| 增量作业水位/检查点管理（checkpoint store） | **对等已有**：Airflow/ Luigi 的 watermark+checkpoint 语义一致（state DB 与数据解耦、UPSERT 水位）；业界明确要求 checkpoint 更新必须与输出提交原子或可恢复（exactly-once 语义） | Apache Airflow docs: checkpoointing/watermark 惯例, airflow.apache.org, 2025；Luigi pipeline targets 文档, luigi.readthedocs.io, 2025（URL 为文档域常规入口，未实时核验——本轴 F 同受 429 限流影响） |
| 运行史保留策略 | 立卡候选：业界调度器（Airflow cleanup policies、Prometheus retention）默认有 retention；task_runs 建议加 90 天归档 | 同上受阻口径 |
| exactly-once / at-least-once 语义显式化 | 立卡候选：DEFERRED_PERSISTENCE 水位前进=at-most-once 记账，与回灌链组合后实际语义依赖 I23 的可靠性——建议文档化组合语义 | Kafka exactly-once 语义文档作为概念参照, kafka.apache.org, 2025（受阻同上） |

## 4 缺陷清单

1. **D-1（P1）last_key 非 ISO 日期→增量静默跳档（消费端危险降级）**
   - 现状→证据→影响：scheduler.py:1913-1914 ValueError 时 `return today, last_key`；last_key 可能因手工修库/旧版本格式/截断而损坏。爆炸半径=该任务所有源的数据断档，且 STATUS=SUCCESS 无告警。
   - 建议修法：ValueError 分支改 `return datetime.date.fromisoformat(默认回看 N 天), ""` 或直接 fail 该任务+告警；progress_store 存入侧加 ISO 日期断言（source 侧 last_key 语义按 capability 分：日期型/序号型分别校验）。
   - 验证法：`UPDATE task_progress SET last_key='xxx' WHERE task_id='kline_daily_incremental'` 后 dry-run `_compute_start_date`。
2. **D-2（P2）水位读取错误与从未运行不可区分**
   - 建议修法：get_last_key/get_task_status 失败抛异常或返回哨兵对象，调用方 fail-closed（宁可任务失败告警，不可静默全量重拉）。
   - 验证法：错误桩单测断言不返回 None。
3. **D-3（P2）reap 误标活跃 run 的进度行**
   - 建议修法：task_progress 加 current_run_id 列（或 reap Step 3 加时间条件 `last_run_at < cutoff`），只清 truly-stale 行。
   - 验证法：双 run 并存场景单测。
4. **D-4（P2）时间字符串格式双源风险（isoformat vs adapter 空格式）**
   - time_utils.py:110-117 自述 sqlite 存储格式为"空格分隔"而本模块用 `.isoformat(timespec="seconds")`（T 分隔+时区后缀）——若历史行由 adapter 写入（空格式），reap 的 `started_at < cutoff` 字符串比较会把 `'2026-09-18 ...'` 与 `'2026-09-18T..+00:00'` 混排，日期同日时比较结果错。建议统一经 now_utc_str()。
   - 验证法：`SELECT started_at FROM task_runs LIMIT 5` 看实际格式是否统一。
5. **D-5（P2）DEFERRED_PERSISTENCE 组合语义未闭环**：水位前进+本地待回灌=数据"账面已到"，真源在 I23 回灌器的存活率上——建议 task_progress 增加回灌对账（DEFERRED 行数 vs 已回灌行数）或至少让 reaper 监控 DEFERRED 积压（5510 件案教训的存储侧防线）。
6. **D-6（P3）task_runs 无 retention**；**D-7（P3）conn 裸暴露**；**D-8（P3）get_store 单例替换泄漏**。

## 5 挂起疑问

- 生产 integrator_progress.db 的 task_runs 行量与 started_at 格式实况（需 DB 只读访问，审查环境未取）——决定 D-4/D-6 是现实问题还是理论问题。
- last_key 的语义注册（哪些任务=日期型、哪些=序号型）是否存在于 tasks.yaml，未查。

## 6 完备性自评

- 六轴全查：A（锁模型/UPSERT 原子性/字符串时间比较逐项）、B、C（scheduler 全消费点列引）、D（与 task_queue/DB 三套状态承载的关系未深挖=长尾）、E（reap 竞态+降级链）、F（受限流影响如实记）。
- 长尾：task_queue（tq.mark_*）与 progress 的双状态一致性未审（旁系对象）；WAL 文件在备份/会话 worktree 场景的行为未审。
