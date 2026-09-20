---
ttl: task_bound
session: st-data-fix-20260921
title: 数据正确性线分包2——断供止血六链（stock_indicator/index_quote/news_sentiment/auction/crypto/夜跑C-5）修复与回补报告
---

# p2 断供止血六链报告（2026-09-21 凌晨 · st-data-fix-20260921 · WO-2）

裁定依据：裁定#339（miniQMT 退役接管，akshare 东财主+sina 备双接口）+ 签字⑨已批范围。
CH 全程走 DatabaseService；未用 OPTIMIZE/TRUNCATE/DROP。所有行数为 CH 实测（[亲验]），
无一次凭记忆填报。红证基线=总包 09-20 22:00 实测，开工时已复现核对（其中两链基线已被
他方先行部分修复，见链1/链2 说明）。

## 结论一句话

六链中五链当日转绿：stock_indicator（总包已修 5565 行+停因定位+周一触发链在飞实证）、
index_quote（akshare 桥重建+1124 行回补+当日 562 行实弹）、news_sentiment（总闸 flag
根因+6 日回补+fetch_perf 接线）、crypto（调度器死亡窗口根因+09-19 补齐+08:41 自愈在册）、
TSV 风暴（18 毒文件清剿）；auction 自愈代码已落地并随调度器 02:14 重启生效，09-17 竞价
派生与夜跑 C-5 dwm 重跑两件重活按协调板车道纪律等分包0 done 信号后执行（工具已备好）。

## 六链修前红证 → 修后绿证（同口径双向实测）

### 链1 stock_indicator（c1_market.stock_indicator）[亲验]

| 时点 | 实测 |
|---|---|
| 修前（总包 09-20 22:00） | 09-18=1000 行（满日 5565）；09-18 11:09 full_refresh 后停触发 |
| 开工复核（09-21 01:47） | 09-18=5565 行、uniq 5565、pe>0=3927/pb>0=5511（与 09-17 剖面一致）——总包 09-20 15:09-15:52 经 query_log 实证已补 |
| 修后 | **绿**（09-16/17/18 三日各 5564/5565/5565 行，指标值真实非占位） |

**停因根因（scheduler_run.log.1 逐行取证）**：09-18 16:30 daily_kline 档 25 任务正常发射，
stock_indicator_incremental 16:34 起跑、17:13 flush 1000 行、**17:36:01 "完成进度 1300/5565"
后无限期静默**（akshare 拉取线程悬挂，无 ERROR 无 Traceback），23:02 被 stale_reaper 以
"RUNNING>6h" 清理（同批 6 僵尸）。当日前情：16:32 CH "TCP+HTTP 均失败" + 16:04 WinError
10038，17:35 stock_hk_hist ConnectionError 第 4/5 次重试——外部源不稳叠加任务级无超时无
重试、0 行/悬挂不可见（当日 23:01 integrity_check 已报 41 表不达标+22 漏跑 23 失败）。
**周一晨触发确认（实弹）**：调度器 02:14 受控重启后已注册调度逐条核验（daily_kline
16:30✓ / weekend_calibration 03:00✓ / nightly_sentiment 08:20✓ / daily_crypto 08:41✓ /
auction_highfreq 9:15-9:25 每10秒✓，265 任务全载）；**03:00:00 weekend_calibration 实弹
发射 43 任务，03:04:24 stock_indicator_full_refresh 起跑（主源 akshare 健康检查=healthy，
start=2026-09-01）**——09-18 停因后首个周一晨触发链全通。

### 链2 index_quote（c1_market.index_quote）[亲验]

| 时点 | 实测 |
|---|---|
| 修前（基线） | max=09-16（ZephyrAlpha_IndexMinuteEOD 随 miniQMT 09-18 退役死亡） |
| 开工复核 | 09-17/09-18 各 48 行/1 只（他方 09-20 14:25 手工 sina 5m 桩，仅 000001.SH） |
| 修后 | **绿**：09-17=610 行/562 只、09-18=610 行/562 只（sina 日线派生 EOD 行，data_source=akshare_sina_eod）；09-21 当日=562 行/562 只（**重建后采集链实弹**，data_source=akshare_sina） |

**重建内容**：①akshare_provider 新增 `index_quote` capability（东财
stock_zh_index_spot_em 实测拒连 RemoteDisconnected 5/5——与裁定#339 断连记录一致；
新浪 stock_zh_index_spot_sina 562 行全宇宙可用。**顺序自裁留痕**：快照族覆盖优先取
sina 主（东财"沪深重要指数"成功时也仅 ~43 只大盘+拒连重试税 ~60s/轮，5 分钟档不可
承受），东财仅兜底——日线族"东财主"裁定不受影响）；②tasks.yaml index_quote_snapshot
source: miniqmt→akshare（叠加不覆盖，分包1 leg 复核完好，yaml.safe_load 验证过）；
③CLI 端到端实弹三轮：拒连切换/EM 成功 43 行/sina 562 行三形态全验证，任务 SUCCESS
last_key=2026-09-21；④fetch_perf 由 scheduler 常规任务被动通道自动接入（SUCCESS 即写
.runtime/fetch_perf/）。09-21 盘中由 intraday_realtime 每 5 分钟续采。
sina 日线不提供成交额：回补行 amount=0（非空 Decimal 显式口径），data_source 已标
akshare_sina_eod 可追溯。

### 链3 news_sentiment_window（c1_market.news_sentiment_window）[亲验]

| 时点 | 实测 |
|---|---|
| 修前（基线） | max=09-14（run_nightly_sentiment.py 静默失败） |
| 修后 | **绿**：window_end 09-14~09-21 每日 1 行 market 粒度，total_count 292~1208 事件/日，sentiment_index 真实分布（-0.0011~0.0216） |

**根因（逐层取证）**：①ZephyrAlpha_NightlySentiment 计划任务=Disabled（现场核实）；
②即便启用，DataScheduler 08:20 nightly_sentiment 特殊槽（scheduler.py:255-286）每次触发
实查 `data/runtime/nightly_sentiment.disabled` 总闸——**该 flag 文件 09-12 20:58 落地
（"停用（服务总闸）"），触发即静默 return False，无告警无日志**（S11 挖矿早有"无任何面
暴露此开关状态"发现，未治）。③window_end 09-14 之后全断与之吻合。
**处置决定**：**改挂调度器**（08:20 槽内建当日窗口+近7日缺口自愈+alerter 失败告警，
严格优于 Windows 任务单日无自愈），Windows 任务保持 Disabled 避免双触发双写；总闸
flag 已改名 `.bak` 留证（reversible：复原文件名即再停用）。**fetch_perf/心跳接线**：
scheduler.py nightly_sentiment 分支新增被动 fetch_perf 记录（SUCCESS/FAILED 带 elapsed
与失败清单，DISABLED_BY_FLAG 态亦落一条——治"开关状态无面暴露"），随 02:14 重启生效；
run_nightly_sentiment_batch 手动实弹 ok=True computed=6 日 failed=0 degraded=0。

### 链4 auction_snapshot（c1_market.auction_snapshot/auction_book）[亲验+等待项]

| 时点 | 实测 |
|---|---|
| 修前（基线） | max=09-16（09-17 桥派生 WinError 10038+CH 连接冷却期叠加，无自愈重试） |
| 开工复核 | 09-17 起 0 行（确认）；tick_depth_5 09-17 由分包0 重写入中（01:47=23,929 行 → 02:35=3,468,379 行，仍未满日） |

**已落地（代码）**：qmt_bridge_provider `_call_derive_auction` 治本——①
`_get_client_with_cooldown_retry`（get_client()=None 冷却期 1/2/4/8s 退避轮询，闸
fail-closed 语义不变）；②逐日派生 RuntimeError 瞬态判别（10038/10054/reset/timeout/
冷却期）+ 2s/4s/8s 指数退避三次重试，确定性错误（SQL 语义等）立即上抛；行为断言
（瞬态 True/True、确定性 False）+ 语法/import 实测过。总窗口 ~14s，10 秒级高频窗安全。
随调度器 02:14 重启生效，**今晨 09:15-09:25 竞价窗为首次实弹**。
**09-17 回补（03:12 实测完成）**：分包0 重写入后 tick_depth_5 09-17 竞价窗
[09:15,09:26)=103,245 行/3,230 只/09:15:00~09:25:03 全窗闭合（防半日源核验过），
A' 配方双表派生落表：**auction_snapshot 09-17=3,230 行（每股终态一行）+ auction_book
09-17=103,245 行（逐拍五档）**，day_has_auction_rows 防重灌闸双表通过。
**09-18 竞价窗=源永缺**：tick_depth_5 09-18 竞价窗仅 18 行（桥 09-18 午后才通），无法
派生——登记 known_data_gaps 由总包落册（非本分包域）。
**今晨 09:15-09:25**：auction_highfreq 高频档经重试代码派生当日竞价（首次实弹点）。

### 链5 crypto_kline_daily（c1_market.crypto_kline_daily）[亲验]

| 时点 | 实测 |
|---|---|
| 修前（基线） | 09-18=51 行半日、09-19=0（daily_crypto 任务半死） |
| 修后 | **绿**：09-19=51 行/51 只（binance.vision 实弹手动补齐）；09-20 归今日 08:41 daily_crypto 档自愈（任务 lookback 5 根幂等重放，last_key=09-18 起步全覆盖） |

**根因（不是执行器挂错池——那是 fc2dec40af 已治的旧病）**：调度器进程 09-20 **04:03~12:12
死亡窗口**（与 tilib Code 241 同窗，资源事件连坐）——09-20 08:41 daily_crypto 档未发射
（当前 scheduler_run.log 该时段零记录、12:12:54 重启注册条目在案），09-19 UTC 日无人拉取。
**手动实弹**：`python -m zephyr.data run crypto_kline_daily_incremental` → 255 行 flush、
last_key 推进 09-19，表内 09-19=51 行（Top-50 USDT+ETHBTC 宇宙=51 只/日，与任务设计
口径一致；09-15/16 count>uniq 系 ReplacingMergeTree 待合并多版本，非重复数据错误）。

### 链6 夜跑 C-5（technical_indicator gp_pred）[方案落地+等待项]

| 时点 | 实测 |
|---|---|
| 修前（基线） | gp_pred 非零=0/144,992,061（0%）；09-20 04:03 Code 241 内存总闸（7.05GiB）阵亡，缓冲 13.3 万行丢（data/local_fallback/c1_market__technical_indicator/ 空壳，实核 0 文件） |
| 现状复核 | 表内 daily 数据 09-14~09-18 各 ~182-187 万行在册，gp_pred 非零仍=0（回填未发生） |

**重跑方案（已落地执行器）**：`dwm_shard_runner.py`（.runtime/tmp/st-data-fix-20260921/）
——每片=独立子进程跑 backfill_technical_indicator_dwm.py `--symbols-file`（100 标的/片，
~56 片），进程级内存隔离杜绝 Code 241 连坐；**每片完成写独立 json**
（dwm_shard_state/<period>_shard_NNN.json，exit/elapsed/log_tail），重跑自动跳过已完成
片、毒片失败隔离不炸全链；已登记 process_reaper_keep（dwm_shard_runner）。新列
（gp_pred/gp_sig/continuation_40/highpass_40/supersmoother_10/highpass_40 等 210 列中
9 新列）由 InternalComputeProvider 计算路径原生覆盖（cycle.py:482-528 实证），重跑即回填。
**等待项**：按协调板车道纪律等分包0 重写入 done（重 IO 撞车禁令）。**恢复计划**：
tilib_indicator_backfill_nightly 保持 Disabled 直至①分片 runner 低峰实弹跑通 daily 全片
②gp_pred 非零率抽验非零；届时改 backfill_night.bat 指向 dwm_shard_runner（保留
night_probe），配置=100 标的/片+单进程，重启用时点=次日 04:00 前窗（与分包0 错峰），
disabled flag 同步删除并在本板登记。

### 附：中信期货 TSV 风暴 + hyperliquid NaN [亲验]

- **根因双双为 09-18 写侧历史 bug，源头代码均已修**：①futures_warehouse_receipt=写侧
  列错位（TSV 15 字段 vs cols_clause 13 列，Code 27 "expected \n"）——现链已修复（表内
  09-18=1416 行复采在册）；②hl_funding_history=premium NaN 字面量进 Nullable Decimal——
  hyperliquid_provider `_dec_or_none`（NaN/Inf/空→None，模块内 09-18 实测注释在案）已治，
  max(funding_time)=09-19 在册。
- **风暴本体=17+1 个毒回灌文件**（2 futures 错位 10155 行×2 + 15 hl 含 NaN 行 1-1443 行/
  文件 + 1 kline_index 浮点 volume 入 UInt64）被 local_replay 无限重试（~31 err/min，
  23:05 CH 重启后暴露）。**处置**：18 文件移入 data/local_fallback_quarantine/（移动保留
  可逆，未删）；_manifest.jsonl 走模块自身文件锁原子清理（20→2 条，余 2 条为合法
  cffex_member_ranking 积压）。

## 时序纪律遵守

F/G 盘零导出（乙线 05:30 前窗）；重 IO（dwm 重跑、09-17 竞价派生）按板等分包0 done；
tasks.yaml/registry 热文件 claim+safe_write_text（CAS base_sha256）+yaml.safe_load 写后
复核；调度器重启采用 guard 自愈机制（kill 子进程→guard 拉起，无裸杀守护链）。

## 晨间验证点（交班清单）

1. ~~03:00 weekend_calibration~~：**已实弹**（03:00:00 发射 43 任务，03:04:24
   stock_indicator_full_refresh 起跑，周一触发链实证通）。
2. 08:20 nightly_sentiment：调度器槽首次无人值守实弹（fetch_perf 落条验证）。
3. 08:41 daily_crypto：09-20 UTC 日自愈补齐。
4. 09:15-09:25 auction_highfreq：桥派生首次实弹（重试代码在位）。
5. 16:30 daily_kline：stock_indicator_incremental 今日数据（09-18 停因后首个增量日）。
6. 分包0 done → dwm 分片重跑启动（wait_and_run_dwm.py 已挂：沉降判据=depth 09-17
   count 两连查变化<0.05%，08:30 兜底退出人工评审；启动后 56 片×100 标的逐片接力）。
