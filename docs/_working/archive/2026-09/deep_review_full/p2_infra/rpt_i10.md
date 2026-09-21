---
ttl: task_bound
title: 深度审查报告——I10 缓冲写入器
object: I10 缓冲写入器
target: src/zephyr/data/buffered_writer.py:62（class BufferedWriter，全文 231 行）
reviewer: GLM-5.3-Flash / st-deeprev-20260918
baseline: 2fa92002c3（HEAD=73d1d045；按工作区现状审）
date: 2026-09-18
status: 已审
---

# 深度审查报告：I10 缓冲写入器（GLM-5.3-Flash / 基线 2fa92002c3）

## 1 对象快照
- 范围：BufferedWriter 全文（攒批阈值 max_rows=50000/max_seconds=30 默认，per-task buffer_max_seconds 可配至 300；列过滤；write_tsv_outcome 三态对接）。
- 消费方：scheduler._try_source（主链）、_fetch_and_write 多表路径（tmp writer）。
- 测试：头注自述 [TESTS] none——**全仓无 import 本模块的测试，确认缺口**（2026-09-05 AI-00 已登记过一次）。
- 变更热力：15 commits。

## 2 六轴审查日志表
| 轴 | 发现 | 锚点 | 级 | 验证法 |
|---|---|---|---|---|
| E | **P2 300s 内存窗口崩溃丢失**：news_data 等 buffer_max_seconds=300 的任务，缓冲行最长驻留 300s；进程崩溃/被杀时窗口内已拉取行全部丢失（无 WAL、无落盘、不在 local_fallback——兜底只在 flush 失败时触发）。可重放源（K线）由重跑覆盖，不可重放源（新闻窗口）=真丢 | buffered_writer.py:83-128 + scheduler.py:1665-1666 | P2 | add 后 kill 进程查行数；对照 news 任务 |
| E | **P2 flush 失败后缓冲行命运取决于调用方**：flush 失败保留缓冲"待重试"，但本类无重试定时器；scheduler 在 last_error 非 None 时不 flush 直接 FAILED 退出作用域=整批丢弃（write_tsv_outcome 已把该批落 local_fallback 的除外——outcome=LOCAL_DURABLE 时数据在盘上，但任务状态 FAILED 而非 DEFERRED，回灌与重跑的顺序竞态可致 MergeTree 双写） | buffered_writer.py:200-206 + scheduler.py:1672-1725 | P2 | mock CH 半失败跑任务，对账 local_fallback 与重跑行数 |
| A | add() 列过滤基于**首个** FetchResult 固定 keep_indices：后续批次列集变化时短列 IndexError（fail-visible）、长列静默截断——流内 schema 漂移无显式告警 | buffered_writer.py:111-128 | P3 | 变列批单测 |
| A | `if self._keep_indices and ...` 空列表 falsy 分支走全列 extend——分析证明 keep_indices 非空时才可能进入过滤分支，当前不可达空列表；脆弱但无实害 | buffered_writer.py:115-119,130-165 | P3 | 构造空交集用例 |
| B | 300s flush 阈值与 nightly_sentiment 08:20 窗口错峰 20 分钟的留痕设计（schedule.yaml 注释）自洽；阈值 per-task 可配（裁定 #ARCH-CH-013 Phase 4） | scheduler.py:1661-1666 + schedule.yaml nightly_sentiment 注释 | 已查无 | 对读 |
| C | total_flushed/total_added/pending 暴露充分，DEFERRED_PERSISTENCE 判定用 last_outcome 三态正确对接 | buffered_writer.py:208-231 + scheduler.py:1673-1698 | 已查无 | 读码 |
| D | 与 WalWriter 的分工注释清晰（BufferedWriter=直写降级兜底 vs WalWriter=先落盘后异步）——两套缓冲语义并存是有意架构非漂移 | buffered_writer.py:22-26 + wal_writer.py:22-26 | 已查无 | 对读 |

## 3 SOTA 对照
- 应用层微批（行数+时间双阈值）与 Kafka producer batch.size/linger.ms 同构：**对等已有**。来源：Apache Kafka producer 文档模式（apache.org，2020-2025；未单独检索 URL=受阻如实记，检索预算已用于 I01/I08）。
- 差距：Kafka producer 有 buffer.memory+批丢弃回调（可观测丢弃），本类崩溃窗口静默丢——业界通行的 WAL-before-buffer 本对象未做（WalWriter 有、BufferedWriter 无，双轨差额即风险面）。

## 4 缺陷清单
1. P2 崩溃丢失窗口（300s 任务面最大）：修法=不可重放源换 WalWriter 或缩短 buffer_max_seconds+任务级显式确认。
2. P2 flush 失败弃置+回灌竞态：修法=error 路径也尝试 flush（write_tsv_outcome 已有三态，直接对接 DEFERRED 判定）；MergeTree 表加回灌前重查。
3. P3：首批定列无告警、空列表脆弱分支、无测试（建议补 add/flush/列过滤三组单测——最小回归网）。

## 5 挂起疑问
- news_data 生产任务的 buffer_max_seconds 实配值（tasks.yaml 在途改动，以工作区为准核）。

## 6 完备性自评
六轴全查。长尾：write_tsv_outcome 三态与回灌全序已在 I01/I08 交叉覆盖；本文件性能（TSV 拼接大缓冲内存峰值）未量化。
