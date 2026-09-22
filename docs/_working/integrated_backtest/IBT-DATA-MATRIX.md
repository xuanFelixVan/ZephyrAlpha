---
ttl: task_bound
completes_when: 随首跑交付报告归档
session: st-integrated-bt-20260922
issue: IBT-DATA-MATRIX-001
---

# 数据完备性矩阵（分包1① 交付物）

> 机读真源=`ibt_data_matrix.yaml`（2026-09-22 01:0x 实测，wall 279s）；本文件=人读摘要。
> 探针法=表级 SQL 覆盖（行数/区间/交易日数）+ 策略级 build(start,end) 冒烟（E4 存活 17 条×4 窗）。

## 1. 表级覆盖（窗口全绿）

| 表 | W_IS 2019-04..2023-12 | W_OOS 2024-01..2025-09-08 | W_HOLDOUT 2025-09-09..2026-09-08 | W_POSTD |
|---|---|---|---|---|
| kline_daily_hfq | 484.7 万行/4996 标的/1156 日 | 207.1 万/5129/409 | 125.2 万/5216/242 | 4.7 万/5217/8 |
| stock_indicator(pe/pb/mv) | 511.7 万行 | 219.5 万 | 132.6 万 | 4.5 万 |
| stk_limit | 518.3 万行 | 220.0 万 | 132.8 万 | 6.1 万 |
| regime_snapshot_history | 2312 行(**2 run 重叠**) | 818(2 run) | 483(2 run) | 11(3 run) |
| index_constituent 000300.SH | 482 版本行 | 336 | 331 | 300 |
| kline_index 000300 | 1156 日 | 409 | 242 | 8 |
| kline_index 000852/000016/000001 | 同窗覆盖 | ✓ | ✓ | ✓ |

**结论：无阻断缺口。** regime 表多 run 重叠→消费必须锁定规范 run `VAL-P0-20260916-230726`
（2019-04-01..2026-09-15 全窗 1812 行，S-OWNER-001/002 考试同源）；2026-09-16..18 由
VAL-P0-20260921-050922 补尾（POSTD 段用，as-of PIT 读法天然兼容）。
financial_derived 探针列名不符（trade_date 不存在）——STR-VAL-001(8d00) 面板冒烟实跑通过，
其内部加载器自处理，探针报错仅为探测 SQL 列名问题，非数据缺失。

## 2. 策略级冒烟（17 条 × 4 窗）

| 成员 | W_IS | W_OOS | W_HOLDOUT | 备注 |
|---|---|---|---|---|
| FACT-4db4c41e [DR] | ✗ 特征行空 | ok 409×40 | ok 242×40 | 死刑件不入队 |
| FACT-4f749668 | ✗ 同上 | ok | ok | IS 生效起点后移 |
| FACT-4228020a | ✗ | ok | ok | 同上 |
| FACT-e293e217 | ✗ | ok | ok | 同上 |
| FACT-e831084c | ✗ | ok | ok | 同上 |
| FACT-4b200528 | ✗ | ok | ok | 同上 |
| CAND-8d000bf3ccc3 | ok 1156×4996 | ok 379nz | ok 210nz | STR-VAL-001；IS 耗时 56s 最重 |
| CAND-c4ec6332c07f | ok（1 列=000300 腿） | ok | ok | 指数腿 |
| CAND-e3da6fa71af1 | ok（1 列=000852 腿） | ok | ok | STR-VREV-025；指数腿 |
| CAND-4440d07f973f | ok 1156×3113 | ok | ok | STR-DABAN-023 |
| CAND-eaddc3f9db4e | ok（000300 腿） | ok | ok | RSRS |
| CAND-d06cab686cef | ok（000300 腿） | ok | ok | RSRS-opt |
| CAND-29eb91dbaf60 | ok（000300 腿） | ok | ok | 躲大跌 |
| CAND-a4543012b464 | ok 1156×451 | ok | ok | 趋势5 |
| CAND-e2e7f033d97c [DR] | ok | ok | ok | 死刑件不入队 |
| CAND-bd42540f86e4 | ok 1156×471 | ok | ok | PE+PB |
| CAND-6a6ec8869ddb | ok 1156×4996 | ok | ok | 动量反转 |

**FACT 族 IS 失败根因**（已定位，非数据缺损）：`build_factor_weights` 宇宙=生效起点前
365 自然日成交额 top40，且起点先回推 lookback×1.7≈425 天→2019-04-01 起点需 2017-02
数据，kline_daily_hfq 2019-01-02 起→宇宙空→"考卷窗口内无有效特征行"。
**处置（协议 §1 预注册）**：FACT 族 IS 段生效起点=2021-04-01（实测 build 通过：
669 行×40 列，首个信号日 2021-04-02），前段零贡献如实披露。

## 3. 缺口清单（登记+评估）

| 缺口 | 影响 | 处置 |
|---|---|---|
| FACT 族 2019-04..2021-03 无面板 | IS 前段 FACT 零贡献 | 已披露，不阻断首跑 |
| kline_etf_daily 仅 2026-07 起 | 卡1 300ETF 执行面不可用（卡1 已 FAIL 终态） | 不消费（#293） |
| regime 多 run 重叠 | 消费侧 run 混用风险 | runner 锁定规范 run |
| 指数腿不可实盘 | 000300/000852/000016 无可交易对应 | kline_index 并入 data 作代理+披露 |
| 600016 复权事件缺/老股 0.2-0.4% | 个别成员微偏 | 随附披露（甲线尾款在案） |
| tick 6 日永缺 | 做T 链（已终结） | 不消费（#304） |

**判定：现有数据足以首跑，无需回填。**
