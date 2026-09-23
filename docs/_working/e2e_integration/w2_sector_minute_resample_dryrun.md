---
ttl: task_bound
title: 案卷·板块派生分钟K 假 SUCCESS 治修 + 12 日回补 dry-run 报数
created: 2026-09-23
sid: st-e2e-20260924
lane: e2e_integration
---

# W2 板块派生分钟K（假 SUCCESS 治修 + dry-run 报数）

对症缺口=`src/zephyr/data/config/known_data_gaps.yaml` 条目 `kline_sector_880_resample_false_success`
（sweep-tail 班 2026-09-23 登记，明文"修复归明晚 E2E 班"）。

## 一、真因四层（登记册只写到第一层，后三层本班实测）

| 层 | 位置 | 缺陷 | 实测证据 |
|---|---|---|---|
| L1 客户端吞错 | `src/zephyr/data/ch_writer.py` HTTP 分支 | 非 200 只 log `status=%s`、**不读响应体** → CH 服务端真因永久丢失 | 主区日志 16:32 只留 `HTTP query 失败: status=400`，无 Code |
| L2 循环吞错 | `tqcenter_provider._resample_kline` | `except` 后 log 并**继续下一周期**，异常不上传 | 同上：四语句全灭，任务仍走完 SUCCESS 分支 |
| L3 结果吞错 | 同上 `FetchResult` | `error=` 从不赋值、`rows=[]` 恒空 | scheduler 判 FAILED **只认** `result.error`（`_fetch_and_write`），三者皆空 ⇒ SUCCESS + 一条 WARN |
| L4 判据缺位 | `scheduler.py` 0 行分支 | #ARCH-SILENT-SUCCESS 把 0 行一律降 WARN（对分红/公告类是对的） | 派生层 0 行＝"没干活"，WARN 无人盯 ⇒ 缺口对下游不可见 |

登记册推测的"通道故障/服务端 readonly"**不成立**：TCP 通、服务端回的是
`Code: 62 Syntax error`。实跑对照（只读）：

```
SELECT toStartOfInterval(now(), INTERVAL 1 15minute)  → Code: 62（旧内联副本拼出的式子）
SELECT toStartOfInterval(now(), INTERVAL 15 minute)   → 2026-09-23 10:30:00
```

## 二、更深两层（登记册未察觉）

1. **同域双轮子**：仓库早有 production 级合成器 `src/zephyr/data/kline_resampler.py`
   （MOD-L00-004：`INTERVAL {n} MINUTE` 正确、支持日期窗、`mutations_sync=2`），
   provider 内另有一份残缺副本（语法错 + 只跑 today() + 吞错）。按 §4 内收铁律
   "同域重复簇→收敛唯一"，provider 侧改为**薄委托**，不再各写一份。
2. **表指向与列面双双过时**：两套实现都按 2026-07-22 分钟线分流**之前**的布局取源。
   实测 `c1_market.kline_sector_880` 只剩 `1d` 一档（436,736 行，2020-03-17→2026-09-23），
   分钟腿在 `c1_market.kline_sector_intraday`。而该表列面与 880 表**不同**：
   `trade_date DateTime64(3,'Asia/Shanghai')`（注释即"分钟K线时间戳"，无独立 timestamp 列）、
   板块码列名是 `code`（非 sector_code）、无 sector_name/forward_factor。
   ⇒ 换表不是改名：旧 Date 表的 `BETWEEN 'd1' AND 'd2'` 在 DateTime64 上会**静默漏掉末日全天**，
   已改为显式半开区间 `[start 00:00, end+1 00:00)`。
3. **换表后首次只读试跑当场抓出第二个错**：`Code: 215 Column 'trade_date' is not under
   aggregate function and not in GROUP BY keys` —— 因 SELECT 输出别名 `AS trade_date`
   与源列同名，把 `argMin(open, trade_date)` 里的引用带偏。已改位置化 SELECT 并复验通过。
   （若没有"只读试跑先行"这道动作，这里就是第二次假绿。）

## 三、幂等安全性预检（改表指向前必做）

`scheduler._cleanup_for_idempotency` 会对 `task.table` 按日期窗发批量 DELETE，
仅在非 ReplacingMergeTree 时生效。实测两表引擎：

```
kline_sector_880          ReplacingMergeTree
kline_sector_intraday     ReplacingMergeTree
```

⇒ 换表不触发批量删（666 万行 1m 源无险）。派生层自身的幂等仍由
`ALTER TABLE ... DELETE WHERE period=<档>` 承担，作用域只在本档窗口。

## 四、red/green 双向证据

新增钉：`tests/data/test_sector_resample_false_green.py`（11 例）。

```
修后（本班 worktree）：11 passed
修前（同一份测试文件放到 979091ad08 基线跑）：10 failed, 1 passed
   FAILED test_resample_target_table_is_minute_table
   FAILED test_resample_periods_propagates_ch_error
   FAILED test_resample_periods_unknown_period_fails_closed
   FAILED test_resample_periods_returns_counts_per_target
   FAILED test_provider_resample_sets_error_on_channel_failure
   FAILED test_provider_resample_reports_inserted_rows
   FAILED test_zero_rows_fail_only_when_declared
   FAILED test_resample_task_declares_the_two_flags
   FAILED test_extra_keys_survive_filter[require_nonzero_rows]
   FAILED test_extra_keys_survive_filter[trading_day_only]
   passed: test_synth_sql_uses_legal_interval_literal（该例钉的是 kline_resampler
           既有正确写法，基线本就绿——它防的是"以后改坏"，不是本次修好的东西，如实标注）
```

回归面：`tests/zephyr/data/test_kline_resampler.py` 6 例原把 880 列面钉成断言
（sector_code/BETWEEN 日期/`argMin(open, timestamp)`），已按真实列面重写并加 Code 215 防线；
合并跑 `tests/backtest tests/data/... ` = 1870 passed，余 10 failed/9 errors
经基线复跑证明**同样存在**（`vendor/Kronos` 与主区产物不在 fresh worktree 内），非本班引入。

## 五、dry-run 报数（只读，零写入，等总指挥判）

窗口 2026-09-11→2026-09-23，`[09-11 00:00, 09-24 00:00)`。

| 档 | 将插/日 | 有效源日 | 将插合计 | 将删 |
|---|---|---|---|---|
| 15m | 10,440 | 8 日 | 83,520 | 0 |
| 30m | 5,800 | 8 日 | 46,400 | 0 |
| 60m | 3,480 | 8 日 | 27,840 | 0 |

- 源侧：1m 逐日 139,780 行（=580 板 × 241 分钟，恰为合成器整日满铺特征）。
- 有效源日 8 天（09-11/14/15/16/17/18/21/22）；09-12、09-13 周末无源。
- **09-23（今日）自相矛盾，标 UNKNOWN**：按日期区间 count 查到 139,780 行 1m，
  但按 `toDate(window_start)` 分组的派生窗统计里 09-23 整日不出数。
  两种口径必有一错，回补前必须定位（疑点：`ingest_ts` 默认 `now()`、或 FINAL 未合并的
  多版本、或分区裁剪与 toDate 时区口径差异）。本班不外推、不猜。
- 将删=0 的口径说明：第一次查询返回空串被我按"测不到"拒答（`ch_writer/ch_reader.query()`
  失败返回 `''`，与真 0 行的 `'0\n'` 不同），第二次带显式时区区间查询成功，确认无行可删。

## 六、必须随数字一起呈的坏消息：源无量

```
1m 源 data_source 分布（trade_date>=09-10）：
  synth_sh   978,460 行  其中 volume=0 的 978,460（100%）
  synth_eq   139,780 行  其中 volume=0 的 139,780（100%）
  tdx         26,667 行  其中 volume=0 的     35（0.13%）
```

⇒ 回补得到的 15m/30m/60m：**OHLC 可信（argMin/argMax/max/min 自价格列），
volume 与 amount 结构性为 0**。而这两列在该表是非空 `UInt64`/`Decimal(18,2)`，无法写 NULL。

后果：任何吃量能的消费（板块拥挤度、换手、逆势榜量腿、成交额分位）会把"0"
当成真实读数——这正是 fullflow 战役 R-014 立过的判据：**宁可缺一个数，不可有一个错数**。

本班建议（二选一，等总指挥拍，不代裁）：
- 甲：灌，但 `data_source='synth_1m'` 显式标注 + 同批在 `known_data_gaps.yaml` 登记
  "09-11→09-23 板块派生分钟K volume/amount 结构性为 0，量能类消费禁读该窗"；
- 乙：不灌，保持裸缺口（下游看得到"没有数"，但板块分钟线派生层继续停摆 12 交易日）。

另有丙案（量能真值另行立项，价格形状先灌）风险在"两档口径混居一表"，本班不推荐自取。

## 七、复核命令

```bash
# L4 判据与委托面
PYTHONPATH=src python -m pytest tests/data/test_sector_resample_false_green.py -q
# 基线红证（同一份测试在未修字节上）
git worktree add --detach .runtime/tmp/e2e_20260924/wt_head 979091ad08
# 语法对照（只读）
PYTHONPATH=src python -c "from zephyr.data import ch_reader as c; print(repr(c.query('SELECT toStartOfInterval(now(), INTERVAL 1 15minute)')))"
# 表结构真源（只读）
PYTHONPATH=src python -c "from zephyr.data import ch_reader as c; print(c.query('DESCRIBE c1_market.kline_sector_intraday'))"
# dry-run 全量报数（只读）
PYTHONPATH=src python .runtime/tmp/e2e_20260924/dryrun_resample_counts.py
```
