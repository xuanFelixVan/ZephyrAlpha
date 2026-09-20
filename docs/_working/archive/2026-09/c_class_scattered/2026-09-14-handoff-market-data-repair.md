---
ttl: task_bound
---

> ## 结案报告（2026-09-15 由 st-fullchain-20260914 核验）
> **总结论：未结案（仍有待办）。处置=**保留**。**
>
> **✅ 已完成（9 条，摘录）**
> - L7: > 交接原因：本会话已完成大部分修复，剩余任务较多（全历史重写需 Owner 批准、tick 批量补数、
> - L19: - 前一轮（09-14 凌晨早些）已补齐：kline_30min 6 天(249,312行)、stock_indicator 7月整月(127,010行)、
> - L24: ## 二、已完成（勿重做）
> - L32: | 【接班会话】P0-1 四表收官 | ✅ 15/30/60min 06 月+7 月混合天、5min 06-01~06-18 全部回正；缺口合并回插法；残余偏移=0 |
> - L42: ### P0-1 修 15/30/60min 表 2026-06~07 的时区偏移（✅ 已完成，见缺口报告 v2）
> - L58: ### P1-4 采集管线退化诊断（✅ 已闭环，根因三层：重启/任务 Disabled/QMT 未开）
> - （另有 3 条完成信号，见正文）
>
> **⚠️ 未完成（1 条，逐条摘录）**
> - L40: ## 三、待办任务（按优先级）
>
> **核验方式**：全文扫描完成/待办信号 + 引用文件存在性核验（引用 6 个，其中判废弃 0、路径漂移 0）+ commit 提及 0 处。
>
> **处置建议**：保留。（本报告由清理批自动生成，判定依据=文档自身信号 + 代码侧核验）






# 2026-09-14 行情数据时区修复与 tick 补数 — 会话交接包

> 交接原因：本会话已完成大部分修复，剩余任务较多（全历史重写需 Owner 批准、tick 批量补数、
> 采集管线诊断），Owner 要求开新会话继续。本文档为新会话的唯一入口。
> 【2026-09-14 07:04 事故注记】docs/_working 当晨 07:04 被并发进程/会话清空，本文件由
> 接班会话凭开局完整阅读的上下文逐字重建（未跟踪文件被清，108 个已跟踪文件已从 git index 恢复）。
> 【08:30 事故注记二】本文件与 repair_kline_tz_monthly.py 约 08:2x 再次被清（含 git index
> staged 条目被卸），已再次重建并立即提交。删除者仍逍遥，取证见缺口报告 §文件事故。

## 一、任务背景（30 秒版）

Owner 怀疑 7、8 月行情缺了几天，要求：①实测全部行情表缺口；②能补的直接下载补齐；
③修复三个已知问题（5min 时区偏移 / 采集管线退化 / 1min 时区双写）；④测试 miniQMT 能否下载历史 tick。

- 前一轮（09-14 凌晨早些）已补齐：kline_30min 6 天(249,312行)、stock_indicator 7月整月(127,010行)、
  money_flow 6-7月+09-11(233,806行)、kline_index 07-10、kline_5min 07-14、kline_daily 09-09~09-11（tushare 源）。
  报告：`docs/_working/2026-09-14-market-data-gap-report.md`（v2 重建版，本会话已更新完）。
- 本会话（09-14 凌晨后半）完成了 5min/1min 的 2026 年 6-7 月时区修复，并测通 QMT tick 下载。

## 二、已完成（勿重做）

| 事项 | 结果 |
|---|---|
| kline_5min 06-22~07-15 时区回正 | ✅ 删 4,090,344 偏移行 + 从备份 +8h 回插；区间总行数 4,456,056 与备份一致；残余偏移=0 |
| kline_1min 06-15~07-15 | ✅ 删 23,644,642 偏移行；06-15~06-30（唯一副本）+8h 回插；07-01~07-15（双写）只删 |
| kline_1min 06-01~06-12 | ✅ 删 12,549,593 + 回插（唯一副本）；06-01~07-15 残余偏移=0 |
| QMT tick 下载验证 | ✅ 09-10/09-11 可下载（600519 各 ~5000 条 3 秒快照，含五档）；08-06/07-03 服务器不给（retention 上限在 2~26 个交易日之间） |
| 【接班会话】P0-1 四表收官 | ✅ 15/30/60min 06 月+7 月混合天、5min 06-01~06-18 全部回正；缺口合并回插法；残余偏移=0 |
| 【接班会话】P1 管线复活 | ✅ 根因=01:27 重启×TickSubscriber 任务 Disabled×QMT 未开；已 Enable+Start，桥链路恢复 |

备份表（保留，可回滚）：
- `c1_market.kline_5min_tzbak_20260914`（4,456,056 行 = 06-22~07-15 全量原始数据）
- `c1_market.kline_1min_tzbak_20260914`（36,194,235 行 = 06-01~07-15 偏移行原始数据）
- `c1_market.tick_data_tzbak_20260914`（507,700 行 = 三天残留去重集，tick 重灌前备份）

## 三、待办任务（按优先级）

### P0-1 修 15/30/60min 表 2026-06~07 的时区偏移（✅ 已完成，见缺口报告 v2）

### P0-2 全历史时区重写（✅ 已批准+已完成——Owner 09-14 08:0x 批准、11:14 五表归零完成；回写消除「已决未回写」，裁定#323 2026-09-17）
`kline_1min` 2021-09 ~ 2026-05 全部 100% 偏移（约 11.3 亿行，月度扫描证据见五-4）。
5/15/30/60min 表起点也是 01:35/01:45/02:00/02:30 → 大概率全历史同样偏移（需先按月扫描确认）。
脚本已备好：`scripts/data/repair_kline_tz_monthly.py`
（逐月 备份→删除→+8h回插→校验，校验失败自动终止，支持 --only-month 断点续跑）。
预估数小时 IO；建议顺序：1min → 5min → 15min → 30min → 60min。

### P0-3 QMT tick 批量补数（09-09/09-10/09-11 三天）（✅ 进行中，6 分片并行）
- 交接班时在跑：脚本 `p0_tick_backfill.py`（同目录），done 断点=`.runtime/tmp/p0_tick_done_<date>.txt`，
  分片参数 `--shard i --shard-count 6 --symbols-file .runtime/tmp/p0_universe.txt`。
- 格式=现役 `tick_subscriber.tick_to_row` 口径（裸代码/中性盘/quality_flag=1），过滤
  09:15:00~15:00:59 + lastPrice>0；ReplacingMergeTree 同键幂等。
- 期货 tick（IF/IC/IM/IH）三天缺口未在本次范围（A22 通道职责）。

### P1-4 采集管线退化诊断（✅ 已闭环，根因三层：重启/任务 Disabled/QMT 未开）

### P1-5 收尾
- 更新 `docs/_working/2026-09-14-market-data-gap-report.md`（✅ v2 已重建）。
- 全部验证后可删 tzbak 备份表（TRUNCATE 无权限，试 `DROP TABLE`，不行用 ALTER TABLE DELETE）。
- 追加 `D:/ZephyrAlpha/.workbuddy/memory/2026-09-14.md`（✅ 已追加下半场条目）。

## 四、环境与硬约束（新会话必读）

1. **Python**：`C:/Users/fanzi/AppData/Local/Programs/Python/Python312/python.exe`（3.12.x，
   PATH 修正见宪法 RULE-ENV）。依赖（clickhouse_driver/akshare/tushare/xtquant）都已装好。
2. **宪法**：`D:\ZephyrAlpha\AGENTS.md`（冷启动七步 + 十二硬规则；本任务是数据操作，
   重点 RULE-DATA-OPS / RULE-SCHEMA-TZ / §9 运维红线）。
3. **CH 连接**（只读）：`sys.path.insert(0, r"D:/ZephyrAlpha/src")` →
   `from zephyr.data.ch_config import load_ch_reader_config` → clickhouse_driver.Client(...)。
   写入：`import zephyr.data.ch_writer as chw; w = chw.get_client()`。
4. **表结构铁律**：
   - 分钟表（kline_1min/5min/15min/30min/60min）**没有 trade_date 列**，分组用 `toDate(trade_time)`；
     trade_time 是 ReplacingMergeTree 排序键首列 → **禁 UPDATE 键列**，删改只能 DELETE+INSERT。
   - tick_data 用 **`timestamp`** 列（不是 trade_time），有 trade_date(Date) 列；
     **Date 列入库必须传 date 对象**（str 报 'str' has no 'year'）。
   - 全部表 ReplacingMergeTree，同键写入幂等（重复写会去重）；**raw count() 会随后台合并
     漂移**（wipe 计数对不上的真相，勿当并发事故查）。
   - zephyr_writer 账号：无 TRUNCATE 权限；CREATE/INSERT/ALTER DELETE/UPDATE(mutations) 可用。
   - tick_data 的时间字段：timestamp/recorded_time/ingest_ts 都是 DateTime64；A股 tick 只取
     09:15~15:00 且 price>0（过滤盘前 price=0 快照）。
5. **数据口径**（tushare 补数时已验证）：amount×1000、pe←pe_ttm、vol 1:1、资金流四档=买-卖；
   重采样：`toStartOfInterval(m, INTERVAL n MINUTE)+INTERVAL n MINUTE`，11:30/15:00 封口。
6. **tick 入库格式真源实为 `tick_subscriber.tick_to_row`**（15 列裸代码/中性盘/miniqmt/
   quality_flag=1）；miniqmt_provider._parse_tick_rows 的 direction='none' 是旧口径。

## 五、关键实测数据（免重扫）

1. 交易日范围：2026 年 74 个交易日（01-02~09-11）；06-19 端午休市（1min 无数据是正常的）。
2. 1min 正常日行数 ≈ 1.25M（~5,200 标的 × 241 bar）；5min ≈ 249,600；15min ≈ 83,312；
   30min ≈ 41,656；60min ≈ 20,828。tick 正常日 ≈ 2,000 万行。
3. 1min/5min/15min/30min/60min 2026-06-01~07-31 现已零偏移（全部修复完毕）。
4. **kline_1min 全历史月度扫描**（2026-09-14 实测）：2021-09 ~ 2026-05 每月 100% 偏移
   （正常行=0），合计 ≈ 1,132,704,317 行；2026-06 双写混合；2026-07 起正常。1min 表总行数 1,452,635,004。
5. QMT tick 服务器 retention：09-09（3 个交易日前）已验证可下（600519 5,022 行）；
   08-06（26 个交易日前）不可下；精确边界未测。
6. 本地 QMT datadir：`E:\国金证券QMT交易端\userdata_mini\datadir`（tick 在 `SH\0\<code>\YYYYMMDD.dat`、
   `SZ\0\<code>\...`）。E 盘空闲 256G 充足。tick 生产链=桥模式（TICK_SOURCE=bridge,
   bridge_env=sim → `E:\qmt_bridge_sim\ticks3.csv` v19 全板块 5 档）；桥写入方活着。
7. 东财接口（push2his.eastmoney.com）被墙，akshare A 股主接口不可用；tushare token 有效
   （走 `zephyr.shared.security.secrets` 取），腾讯/新浪日 K 备用。
8. 双写天两副本各缺一段（15min 07-13 正常 83,152+偏移 41,576；30min 07-15 正常仅 13,002），
   纯"只删"会丢盘后段——必须缺口合并回插（finish_p0_1.py）。

## 六、工作文件清单

- 交接文档（本文件）：`D:\ZephyrAlpha\docs\_working\2026-09-14-handoff-market-data-repair.md`
- 缺口报告 v2：`D:\ZephyrAlpha\docs\_working\2026-09-14-market-data-gap-report.md`
- 修复脚本目录：`D:\ZephyrAlpha\docs\_working\2026-09-14-market-repair-scripts\`
  - `repair_kline_tz_monthly.py`（P0-2 全历史段主力，天级模式判定）
  - `finish_p0_1.py`（P0-1 收官实际运行版：缺口合并回插）
  - `p0_tick_backfill.py`（tick 批量补数，支持 --shard 分片）
  - `wipe_tick3days.py`（三天残留清理）
  - 前一轮 `fill_gaps_tushare.py`/`verify_final.py`/`repair_kline5min_tz_deprecated_update_key.py`
    在 07:04 清空案中丢失未重建（前两个功能已被覆盖，最后一个本就废弃）
- 项目记忆：`D:\ZephyrAlpha\.workbuddy\memory\2026-09-14.md`（下半场条目已追加）
- tick 入库映射真源：`src/zephyr/data/tick_subscriber.py`（tick_to_row 现役格式）+
  `src/zephyr/data/implementations/miniqmt_provider.py`（_fetch_tick_data 旧口径）
- 采集任务注册表：`src/zephyr/data/config/tasks.yaml`；订阅器脚本 `scripts/start_tick_subscriber.ps1`
- 项目宪法：`D:\ZephyrAlpha\AGENTS.md`

## 七、新会话第一步建议

1. 读本文件 + 缺口报告 v2 + `AGENTS.md` 冷启动。
2. P0-2 全历史重写等 Owner 批（本会话已在请示中）。
3. tick 批量若未跑完：读 done 断点续跑即可。
4. **docs/_working 有周期性删除者在逃**：产物写完立即 `git add`，发现文件消失先查
   `git status` 与 index（本会话两度中招，恢复路径=从 index checkout 或凭上下文重建）。
