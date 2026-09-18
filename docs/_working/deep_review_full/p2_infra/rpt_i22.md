---
ttl: task_bound
doc_type: report
title: 深度审查作业簿——分钟K重采样
owner: st-deeprev-20260918
created: 2026-09-18
---

# 深度审查报告：分钟K重采样（I22）

- 状态: **已审**
- 级别: P3｜类型: 管线
- 基线 commit: 2fa92002c3（工作区 HEAD=b80084c0df）
- 审查者: GLM-5.3-Flash / st-deeprev-20260918
- 入口锚点: `src/zephyr/data/kline_resampler.py:172`（main）
- 生产调用方: 无编程调用方（CLI-only，STARTUP=manual；ch_tick_kline.py:20 复用其模式但独立实现）；multi_timeframe_fusion.py:25 有查重裁定记录（分工明确：本对象=880 板块 K 线）
- 测试文件: tests/zephyr/data/test_kline_resampler.py
- 备注: TTL=task_bound（头注自承临时件）

## 1 对象快照

- 审查范围：`kline_resampler.py` 全文 213 行：1m→15m/30m/60m 的 DB 内聚合（toStartOfInterval + argMin/argMax OHLC）、ALTER DELETE(mutations_sync=2)+INSERT 幂等写入、CLI 参数。
- 排除项：multi_timeframe_fusion（内存侧 resample，已有查重裁定分工）；ch_tick_kline（tick→1m/5m 上游）；表 DDL 归 I25。
- 测试覆盖概况：单测在；SQL 生成与窗口边界用例覆盖度待核。
- 材料包缺项：880 表 timestamp 时区/标签语义实况未取证（需生产 CH 查询）；15m/60m 数据新鲜度监控现状未查。
- 变更热力：9 次提交，低热区。

## 2 六轴审查日志表

| 轴 | 发现 | 证据锚点 | 严重级 | 验证法 |
|---|---|---|---|---|
| A 深度 | `any(forward_factor)` 任取窗口内一行因子：因子在窗口内变化时（880 板块 forward_factor 是否恒定未证）合成 K 线挂错因子——聚合口径隐患 | kline_resampler.py:86 | P2 | 查 880 表 forward_factor 同日多值存在性：`SELECT sector_code, toDate(timestamp), count(DISTINCT forward_factor) FROM {880} WHERE period='1m' GROUP BY 1,2 HAVING count(DISTINCT forward_factor)>1` |
| A 深度 | 窗口对齐隐含假设未对账：toStartOfInterval 按钟点对齐（:00/:15/:30/:45），若源 1m 时间戳为 bar 收盘标签（如 09:31 标 09:30-09:31 bar），60m 窗口落在 09:00/10:00/11:00/13:00/14:00——与 A 股 60m 惯例四根（10:30/11:30/14:00/15:00）错位；1m 标签语义（开盘/收盘标）全仓无文档 | kline_resampler.py:91 + docstring:22-28（未提标签口径） | P2 | 抽一天 60m 合成结果首根 timestamp，与 tqcenter 原生 60m（若有）或人工 09:30-10:30 聚合对拍 |
| A 深度 | `toDate(window_start)` 隐含 timestamp=市场本地时区：若 880 表 timestamp 为 UTC 误标（本仓 2026-09-18 ETF 分钟族 4.12 亿行时区误标事故同型），跨日界行归错 trade_date | kline_resampler.py:76 + 事故先例 commit 60ed3aa49c | P2 | `SELECT min(timestamp), max(timestamp), toTypeName(timestamp) FROM {880} WHERE period='1m' AND trade_date=昨天` 核对时区归属 |
| E 对抗 | DELETE+INSERT 非单事务且无 single-flight：两进程并发跑同区间→双删双插→重复行（表若非 ReplacingMergeTree 则永久双份）；单进程崩溃于删后插前→窗口数据缺失至下次重跑 | kline_resampler.py:140-147 | P3 | 双终端同时跑 `--period 15m --days 1`，查行数翻倍 |
| B 上游 | SQL 值全部 f-string 内插（target/period/start/end），CLI 日期无格式断言——`--start "x' OR '1'='1"` 直达 SQL（内部工具低危）；start/end 只校验周期名不校验日期格式 | kline_resampler.py:64-68, 184-194 | P3 | 传非法日期串看 CH 报错 |
| C 下游 | 调度归属未明：INVARIANTS 自述"盘后批量执行"但全仓无调度/巡检挂接（[CONSUMERS] 空）——15m/30m/60m 断更无人知（依赖人工记得跑）；supply_sentinel 是否覆盖 880 派生周期未查 | kline_resampler.py:5, 8 + grep 无生产调用方 | P2 | grep scheduler/tasks.yaml 无 resampler 项；查 15m 表 max(trade_date) 距今天数 |
| D 旁系 | docstring 声称源=1m/5m（:19），_SYNTH_MAP 实际三周期全用 1m 源（:57-61）——5m 源路径从未存在或已删，文档漂移 | kline_resampler.py:19 vs :57-61 | P3 | code review |
| A 深度 | `--start` 单独传入（无 --end）被静默忽略走 --days 默认 7 天——参数假完成 | kline_resampler.py:184-187 | P3 | `--start 2026-08-01` 单参数跑，日志显示日期范围非 08-01 |
| A 深度 | 默认 end=UTC 今天（:164）：A股盘前（CST 08:00 前=UTC 前一日）跑会缺当日——盘后运行场景无碍，非惯例时段运行语义漂 | kline_resampler.py:162-166 | P3 | 拨钟验证 |

## 3 SOTA 对照

| 对照项 | 结论 | 来源 |
|---|---|---|
| bar 窗口标签/闭合口径（label left/right、closed left/right 需显式声明防前视偏差） | **立卡候选**：业界明确要求显式声明 bar 标签口径（pandas resample 的 label/closed、Databento/Deltix vendor 口径均文档化）；本对象既未声明源 1m 的标签语义也未文档化合成窗口口径——回测消费 15m/60m 时若按"timestamp=可知时刻"理解会产生前视。建议立卡：在本模块与 880 表 schema 文档显式登记窗口 [start,end) 与标签=start | pandas.DataFrame.resample 官方文档（label/closed 语义）, pandas.pydata.org, 2025：https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.resample.html ；QuantPython OHLCV Resampling（(09:30,09:45] 标 09:45 陷阱）, quantpython.substack.com, 2025；Databento OHLCV resampling docs, databento.com, 2025 |
| DB 内聚合合成（避免搬运） | **对等已有**：ClickHouse toStartOfInterval 聚合属官方推荐用法（group by time bucket），与业界在库内做 bar 合成一致 | ClickHouse 官方文档 toStartOfInterval, clickhouse.com, 2025（文档域常规入口） |
| 会话对齐（origin=start 按开盘对齐而非钟点） | 立卡候选：若确认 60m 需按 A 股四段切分，需 origin 对齐 09:30/13:00 自定义窗口（CH 可用 date_diff 手工分桶），钟点对齐不够 | Stack Overflow pandas resample 1min→1h 会话对齐讨论, stackoverflow.com, 2017 存档 |

## 4 缺陷清单

1. **D-1（P2）窗口标签/时区两类隐含假设未对账**（轴 A 行 2、3）
   - 现状：合成正确性完全依赖"源 1m 时间戳=本地时区+已知标签语义"两条未文档化假设；同型时区事故在本仓已有 4.12 亿行先例。
   - 影响：15m/30m/60m 全量 K 线窗口错位或跨日归错 trade_date→下游策略按错 bar 决策（静默）。爆炸半径=所有消费 880 派生周期的策略/回测。
   - 建议修法：①对拍一天合成 60m vs 人工聚合；②在模块 docstring+表 schema 登记 timestamp 时区与标签口径；③若时区混标，先治表（参考 ETF 修复件 repair_etf_minute_tz_split.py 模式）。
   - 验证法：轴 A 行给的两条 SQL/对拍法。
2. **D-2（P2）forward_factor any() 口径**（轴 A 行 1）：改 min/max 或按窗口最后值 argMax(factor, timestamp) 并登记语义。
3. **D-3（P2）派生周期断更无监控**：15m/30m/60m 无 freshness 哨兵挂接，调度未明。建议 supply_sentinel 或 tasks.yaml 登记盘后任务（幂等，重跑安全）。
4. **D-4（P3）并发重入无防护**：加 CLI 锁文件（.runtime/tmp lockfile）或表转 ReplacingMergeTree 消重。
5. **D-5（P3）SQL 内插无日期格式断言 + --start 单参静默忽略 + UTC end 边界**：一次性卫生批。

## 5 挂起疑问

- 880 表当前引擎（MergeTree/Replacing）与 ORDER BY 键未取证（DDL 归 I25 顺带核），决定 D-4 重复行的实际后果。
- forward_factor 对 880 板块指数的实际语义（板块指数通常无复权概念？若恒 1 则 D-2 降级 P3）。
- 本工具是否已被运维惯例固定（shell history/cron 外置仓外），决定 D-3 的接线方式。

## 6 完备性自评

- 六轴全查：A（OHLC 四问：公式正确/假设两条未证/边界（午休/尾盘/UTC end）已列）、B（SQL 注入面+源数据语义）、C（无消费方=调度悬空）、D（fusion 查重裁定+ch_tick_kline 模式复用确认边界清晰）、E（重入/崩溃窗口）、F（三来源带 URL）。
- 长尾：tests/test_kline_resampler.py 断言强度未逐条审；880 表 ORDER BY 与 TTL 策略归 I25。
