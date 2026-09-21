---
ttl: task_bound
title: 深度审查作业簿——双源交叉验证
owner: st-deeprev-20260918
created: 2026-09-18
---

# 深度审查报告：双源交叉验证（I16）

- 状态: **已审**
- 级别: P3｜类型: 管线
- 基线 commit: 2fa92002c3（工作区 HEAD=b80084c0df，其后仅文档/治理批，不影响本对象）
- 审查者: GLM-5.3-Flash / st-deeprev-20260918
- 入口锚点: `src/zephyr/data/cross_source_validator.py:105`（CrossSourceValidator 类）
- 生产调用方: **无（见 D-1）**
- 测试文件: tests/zephyr/data/test_cross_source_validator.py
- 备注: —

## 1 对象快照

- 审查范围：`cross_source_validator.py` 全文 302 行（ValidationReport 数据类 + CrossSourceValidator 类 + 2 个 SQL 模板）。逻辑：查最近 N 分钟 market_tick 按 symbol+data_source 取 argMax 最新价/量，QMT 主源 vs TDX 备源比价/比量，结果写 cross_validation_log。
- 排除项：`consensus_crosscheck.py`（独立对象，仅作为旁系与同表写入方审视）；`ch_reader/ch_writer` 下沉为上游依赖只审契约。
- 测试覆盖概况：11 个用例，分支覆盖较好（无数据/价格过/价格挂/双 missing/volume warn/写日志/畸形行跳过），全部 mock ch_reader/ch_writer，无真实 CH 集成。
- 材料包缺项：无运行时证据包（该模块无生产调用方，本就无运行日志可取，见 D-1）；数据画像未取（依赖 tick 双源同时在线窗口）。
- 变更热力：`git log --follow` = 7 次，近 3 次全是 ALGO_FLOW 锚点补票/文档批，核心逻辑 2026-07 后稳定。低热区。

## 2 六轴审查日志表

| 轴 | 发现 | 证据锚点 | 严重级 | 验证法 |
|---|---|---|---|---|
| A 深度 | 备源 price/volume==0 时比较被静默跳过，不进任何 log entry，report 照常 passed/no-fail——备源退化成全 0 时校验"全绿" | cross_source_validator.py:213-214, 247-248 | P1 | mock 备源 volume=0 跑 validate()，观察 report 无 warning 且 is_healthy=True |
| A 深度 | argMax 取各源自适应最新 tick 比对：两源时间戳不同步时价差/量差含"时间偏移噪声"，5 分钟窗口内活跃股必然假 fail/假 pass；隐含假设（两源 tick 对齐）未文档化 | cross_source_validator.py:55-63 | P2 | 对同一 symbol 双源查 `argMax(timestamp)` 各自时间戳差，>秒级即证 |
| A 深度 | volume 比对语义假设"最后一笔 volume=当日累计量"：若 market_tick 存的是逐笔量而非累计量，5% 阈值完全失义（tick 级随机差 ≫5%） | cross_source_validator.py:57-58, 236-250 | P2 | `SELECT volume FROM market_tick WHERE symbol='600519' ORDER BY timestamp DESC LIMIT 5` 看是否单调递增 |
| B 上游 | ch_reader.query 失败返回空串（吞错设计），validate() 无法区分"无数据"与"CH 挂了"，两者都返回全零健康报告 | cross_source_validator.py:135-138 + ch_reader.py:95-109（"失败时返回空字符串"） | P2 | 停 CH 后跑 validate()，确认返回 is_healthy=True 且无告警 |
| B 上游 | `minutes` 直接 format 进 SQL（f-string），类型不设防；symbol 来自 CH 回读未转义直插 INSERT | cross_source_validator.py:60, 287-291 | P3 | code review；传 `time_window_minutes="5 MINUTE) OR (1=1"` 类字符串验证 |
| C 下游 | 生产调用方为零：全仓 grep 仅测试文件引用 CrossSourceValidator；头注声明的消费者 `scheduler.run_schedule("cross_validation")` 不存在——scheduler 只挂 `consensus_crosscheck`（另一实现） | cross_source_validator.py:5 vs scheduler.py:288-309；grep "CrossSourceValidator" 仅 src 本体+test | P1 | `grep -rn "CrossSourceValidator" src/ scripts/` 排除本体/测试即证 |
| D 旁系 | 双写同表：cross_source_validator 与 consensus_crosscheck 都写 c1_market.cross_validation_log，口径完全不同（tick 逐标的 vs 一致预期聚合 symbol='*AGG*'）；表消费方需按 symbol/metric 猜行来源 | consensus_crosscheck.py:65, 251-254 vs cross_source_validator.py:66-71 | P2 | `SELECT DISTINCT metric, symbol FROM cross_validation_log` 看两族行混居 |
| E 对抗 | `_write_log` 裸 except 吞写入失败仅 log.warning：校验跑了、结果丢了，报告方仍显示成功完成 | cross_source_validator.py:299-302 | P2 | 临时给 ch_writer.query 打异常桩跑 validate()，观察仅 warning |
| E 对抗 | 畸形行静默 continue（parts<4 / Decimal 解析失败），无计数器、不进报告；上游 schema 漂移时校验静默变空转 | cross_source_validator.py:142-151 | P3 | 造一行 3 列数据验证 total_symbols 不含且无提示 |
| A 深度(测试) | 测试全 mock，无覆盖"备源为 0 静默跳过"分支；test_validate_no_data 断言 is_healthy=True 恰好固化了"CH 挂=健康"语义 | tests/zephyr/data/test_cross_source_validator.py:52-59 | P2 | 在 mock 中注入 `600519\ttdx_backup\t0\t0` 行跑现有断言外新增检查 |

## 3 SOTA 对照

| 对照项 | 结论 | 来源 |
|---|---|---|
| 双源 tick 供应商数据对账（per-vendor reconciliation + gap detection + price jump 阈值） | **对等已有**（本对象=简化版逐标的对账；业界另配 gap/停流告警，本对象 missing 检测部分覆盖） | CoinAPI tick data validation rules, coinapi.io, 2025（https://www.coinapi.io/blog/tick-data-vs-order-book-snapshots-complete-guide）；Quant StackExchange vendor discrepancy 讨论, quant.stackexchange.com |
| 数据质量/可观测（freshness、null率、分布监控内置进数仓+告警闭环） | **立卡候选**：业界 2025 主流把校验做成数据平台内置 monitor（row count/freshness/distribution）+ 告警闭环，而非一次性脚本报告；本对象校验结果落表但无消费方读它告警 | OneUptime ClickHouse data quality monitoring, 2026-03（https://oneuptime.com/blog/post/2026-03-31-clickhouse-data-quality-monitoring/view）；Metaplane data quality vs observability（https://www.metaplane.dev/blog/data-quality-vs-data-observability）；ClickStack 发布, clickhouse.com, 2025-05 |
| 学术侧 tick 数据清洗（跳变/不一致检测） | 对等已有，无需引入 | Tick Data Quality Control, ResearchGate, 2025（https://www.researchgate.net/publication/391971666） |

## 4 缺陷清单

1. **D-1（P1）孤儿死码+幽灵消费者声明**
   - 现状：CrossSourceValidator 无任何生产调用方；头注 `[CONSUMERS] zephyr.data.scheduler.run_schedule("cross_validation")`（cross_source_validator.py:5）指向不存在的调度项——scheduler 实际挂的是 consensus_crosscheck（scheduler.py:290）。
   - 证据：grep 全仓 `CrossSourceValidator` 仅本体+测试；scheduler.py:288-309 只接 consensus_crosscheck。
   - 影响：QMT-vs-TDX 内容级双源比对（P1-4 立项初衷）从未运行；header 幽灵引用会误导后续维护以为"双源校验在跑"→ 数据源静默死亡（模式 #6/#8 复合）。爆炸半径=备源数据劣化无独立探测。
   - 建议修法：要么在 scheduler 注册 `cross_validation` 调度项（走 consensus_crosscheck 同款 disabled flag 惯例），要么按孤儿死码流程退役并修 header。
   - 验证法：接通后 `run_schedule("cross_validation")` 跑一次，查 cross_validation_log 出现 metric in ('price','volume') 行。
2. **D-2（P1）备源零值静默跳过 → 校验假绿**
   - 现状：`b_price==0`/`b_vol==0` 直接 return（:213-214, :247-248），无日志项无计数。
   - 影响：备源（tdx_backup）整体退化（断流后补 0、表损坏）时，比对静默缩水，report.passed 偏高、is_healthy=True。模式 #6 变体。
   - 建议修法：零值记 `status='fail'`（备源价量不可为 0，除权日价格也≠0）或至少计入 `skipped` 计数器并进 summary。
   - 验证法：单测注入零值行断言 failures>0。
3. **D-3（P2）CH 故障与无数据不可区分**
   - 现状：ch_reader 失败返回空串→validate 走"无 tick 数据"分支返回健康空报告（:135-138）。
   - 影响：任何下游若消费 is_healthy，CH 停机窗口=校验静默通过。
   - 建议修法：validate 前置 `SELECT 1` 探活或在报告中加 `data_available: bool` 字段。
   - 验证法：停 CH 实跑观察返回。
4. **D-4（P2）argMax 最新 tick 比对的时间偏移噪声**（见轴 A 行）——建议 SQL 改为对齐到同秒/同分钟快照（如按 minute bucket 取 last price），或在 detail 中记录双源时间戳差供阈值豁免。
5. **D-5（P2）同表双写方口径混居**（见轴 D 行）——建议 cross_validation_log 增加 `validator` 来源列或分表。
6. **D-6（P3）SQL 拼接卫生**：symbol 未转义、minutes 未 isinstance(int) 断言、detail 用 `\\'` 转义依赖 CH 方言。建议参数化或至少断言类型。
7. **D-7（P3）客户端 today vs 服务端 now() 跨午夜时区错位**：`_add_log_entry` 用本地 date + CH `now()`（:283-290），服务器非东八区时 check_date 与 check_time 差一天。

## 5 挂起疑问

- market_tick.volume 的存储口径（逐笔量还是当日累计）未在表 schema 注释中确认，D-4 的严重度依赖此答案。
- P1-4 立项文档（data_source_integrator_blueprint.md）是否已将"内容级双源比对"责任移交 consensus_crosscheck？若已移交，D-1 应走退役而非接通。

## 6 完备性自评

- 六轴全查：A（数学四问：偏差公式/除零/量纲逐项过）、B、C、D、E（五问逐条）、F 均有结论。
- 长尾：未做真实双源数据画像（依赖交易时段双源在线）；未审 cross_validation_log 表 TTL/膨胀（若 D-1 接通，每 5 分钟全标的比对行会高频写入，需估行量与 TTL）。
