---
ttl: task_bound
---

# 2026-09-14 行情数据缺口修复报告（v2 重建版）

> **文件事故注记**：本报告 v1 与交接包、修复脚本目录在 2026-09-14 07:04 被并发会话/进程清空
> （docs/_working 全目录 108 个已跟踪文件 + 多个未跟踪文件，全仓多会话当日文档均中招，
> 他会话当日 commit 中亦有"落盘合并竞态被吞""文件恢复"记录）。已跟踪文件经
> `git checkout -- docs/_working/` 从 index 全数恢复（他会话 staged 修改保留）；
> 本报告、交接包、修复主脚本由接班会话凭上下文重建；`fill_gaps_tushare.py`、
> `verify_final.py`、`repair_kline5min_tz_deprecated_update_key.py` 三个未跟踪脚本
> 无副本，确认丢失（功能已由本轮脚本覆盖/不再需要）。教训：**工作区产物每轮即
> `git add`**（本次交接包因未 add 曾两度丢失，add 后未再丢）。
> 【根因结案 08:1x】清空者=commit 队列 serializer 落地时在主工作区跑 `git clean -fd`（队列
> 死信原文暴露，详见 §五-补），已立 **#ARCH-311** 登记证据，Owner 裁定交专门修复批；
> 短期避险=产物每轮 git add。

## 一、背景

Owner 发现 7、8 月行情缺数据。三轮修复：①（09-13/14 凌晨）tushare 补日线/估值/资金流缺口；
②（09-14 凌晨）5min/1min 2026-06~07 时区偏移修复 + QMT tick 下载验证；③（本会话 06:50 起）
派生表时区修复收官 + tick 三天批量补数 + 采集管线复活。

## 二、时区偏移修复（P0-1 收官 ✅）

病根：bdpan 采集器以 UTC 时间戳写 `DateTime64(...,'Asia/Shanghai')` 列，真实 09:30 存成 01:30。
约束：trade_time 是 ReplacingMergeTree 排序键首列，禁 UPDATE，只能 DELETE+INSERT SELECT +8h。

| 表 | 修复范围 | 结果 |
|---|---|---|
| kline_1min | 06-01~07-15 | ✅ 前会话完成（删 36.2M，双写月只删、唯一副本月删+回插） |
| kline_5min | 06-22~07-15 ✅ 前会话；**06-01~06-18 ✅ 本会话** | 06-01~08-01 残余偏移=0 |
| kline_15min | 06-01 整月 + 07-01/02/13/15 | ✅ 本会话，残余偏移=0 |
| kline_30min | 06-01 整月 + 07-01/02/13/14/15 | ✅ 本会话，残余偏移=0 |
| kline_60min | 06-01 整月 + 07-01/02/14/15 | ✅ 本会话，残余偏移=0 |

本会话方法论升级（两处，均已落码）：

1. **模式判定从"月级"改"天级"**。kline_5min 2026-06 是月内混合（06-01~06-18 唯一副本 +
   06-22 后已修复的正常行），按月判成"双写只删"会**直接抹掉 14 天唯一副本**——初版脚本
   已实际触发该误判路径，靠天级重写脚本在删除前拦截。
2. **"删+按缺口合并回插"替代"双写只删"**。实测双写天两个副本各缺一段（如 15min 07-13
   正常副本 83,152 + 偏移副本 41,576；30min 07-15 正常副本仅 13,002），纯删会丢盘后段
   （30min 07-15 实证需回插 23,710 根 bar）。回插用 LEFT ANTI JOIN 只补
   `(symbol, trade_time+8h)` 在正常副本缺失的 bar，正常副本已有则让位。
   校验三重：残余偏移=0 + 无重复 bar + 行数=删后行数+缺口数。

脚本：`scripts/data/repair_kline_tz_monthly.py`
（含 month_range 元组 bug 修复、--bak-suffix 防误清旧备份；实际收官跑的是
`scripts/data/finish_p0_1.py` 缺口合并版）。

备份表（保留可回滚，验证期后再删）：`kline_5min_tzbak_20260914`(4,456,056)、
`kline_1min_tzbak_20260914`(36,194,235)、`kline_5min_tzbak2_20260914`/`_tzbak3_20260914`
（本会话 5min 用，已清空壳）、15/30/60min `_tzbak_20260914`（已清空壳）。

## 三、QMT tick 三天补数（P0-3 ✅ 完成 08:11）

- 现状修复前：09-11 全缺、09-10 仅 4 标的 55,718 行、09-09 仅 466,616 行（qmt_bridge 严重不全）。
- 已验证 09-09 可从 QMT 服务器下载（600519 5,022 行），retention 边界比预期宽。
- 处置：三天残留先备份后清空（`tick_data_tzbak_20260914` 507,700 行可回滚；wipe 时
  count→INSERT 窗口内 ReplacingMergeTree 后台合并折叠 41,030 重复键行导致计数漂移，
  备份内容=全量去重集，无损失）。
- 回填格式=现役 `tick_subscriber.tick_to_row` 口径：15 列、裸代码、direction='中性盘'、
  data_source='miniqmt'、quality_flag=1，过滤 09:15:00~15:00:59 且 lastPrice>0
  （与交接包 §四.4 一致；存量 09-08 实测含 88,904 个 price=0 行，回填比存量更干净）。
- 入库实测核验：裸代码/物化列 exchange+symbol_canonical 自动派生/毫秒时间戳/五档一档，
  pilot 6 标的 26,396 行格式全对。
- 执行（✅ 08:11 完成，开盘前 80 分钟）：8,106 标的（沪深A股+京市A股+ETF/LOF+转债+指数，
  与订阅器 `_get_all_symbols` 同口径）× 3 天，6 分片并行（串行 0.6 标的/s→并行 ~7 标的/s），
  断点续跑（`.runtime/tmp/p0_tick_done_<date>.txt`）。
- **终验**：09-09 = 28,958,350 行 / 7,842 标的；09-10 = 28,346,312 / 7,815；
  09-11 = 29,792,684 / 7,830（健康基线 09-08 = 22.2M / 8,657；回填口径更严：price>0 强制、
  窗口 09:15:00~15:01:00 强裁、direction 恒中性盘、data_source 单一 miniqmt）。
  price<=0=0，无窗口外行。09-11 曾混入桥重放 6,000 行 qmt_bridge 快照（00:00:00 戳记），
  已按 data_source 精准清除。
- 期货 tick（IF/IC/IM/IH）三天缺口**未在本次范围**（A22 通道职责，`futures_tick_intraday`
  任务属盘中增量；历史补需另批）。
- 永久缺口维持登记：tick 07-03、07-06~07-09、08-05、08-06（bdpan 07-02 停更 + QMT retention 不够）。

## 四、采集管线退化诊断与复活（P1-4 ✅ 根因闭环）

时间线与根因（三层叠加）：

1. **机器 2026-09-14 01:27 重启** → 全部常驻采集进程死亡。
2. **`ZephyrAlpha_TickSubscriber` 计划任务处于 Disabled** → 重启/登录后不自启
   （同 Disabled 的还有 RestartMiniQmt、TradingWatchdog，后两者涉实盘/终端管理，未动，留 Owner 定）。
3. 09-09~09-11 期间 **QMT 终端未运行** → 桥源（qmt_bridge）与 miniqmt 直订均无数据，
   日线 5,554→5,206、stock_indicator 5,558→1,500 等骤减皆由此（历史缺口已由前两轮 tushare 补齐）。

已执行修复：

- `Enable-ScheduledTask` + `Start-ScheduledTask ZephyrAlpha_TickSubscriber`（07:24 起
  guard PID 循环守护 + 订阅器单实例运行，防崩自动拉起，任务恢复开机自启）。
- 数据链路确认为**桥模式**（`TICK_SOURCE=bridge`, bridge_env=sim → 尾读
  `E:\qmt_bridge_sim\ticks3.csv`，v19 全板块 5 档 25 列；#BRIDGE-WRONG-FILE 事故后
  默认文件已正确指向 ticks3）。桥写入方活着（ticks3.csv 当日 07:04 更新），
  订阅器启动后 received=written=8,392、errors=0。
- 沙箱重启重放防护：07:04 的快照重放把 6,000 标的 × 1 行星期五快照写入 09-11，
  属设计内已知行为（timetag 去重只防桥侧重读），将被 tick 批量补数按同键幂等覆盖，无残留影响。
- DataScheduler 本身健康（他会话 09-14 凌晨已复活，07:23 仍在正常跑任务）。
- **预期 09:15 后当日盘链路正常落库**（桥文件 09:15 重建 + offset 跨天归零，已有守护）。

遗留观察项（P2，不阻断）：

- local_replay 三表 schema drift 反复回灌失败噪音：hk_trade_calendar（Date 解析错位）、
  crypto_kline_daily（列子句语法错）、sim_trade_log（Code 27 列数不匹配）——均为历史
  TSV 重放与新 schema 不匹配，建议后续批清理死信 TSV 或修 replay 列映射。
- 桥模式沙箱重启重放会在非交易日/重启时写入"每日一行"快照（本例 09-11 的 6,000 行），
  可考虑桥侧加跨天 timetag 丢弃闸。

## 五、全历史时区重写（P0-2 ✅ Owner 批准，执行中）

- **Owner 裁定（08:0x 对话）**：批准，tick 批完成后启动，顺序 1min → 5min → 15min → 30min → 60min。
- **扫描确认**（轻量逐月单查询，08:0x 完成）：四派生表 2021-09~2026-05 全部 57 个月
  **100% 偏移、纯唯一副本**（normal=0）——60min 22,570,317 / 30min 45,140,609 /
  15min 90,281,209 / 5min 270,186,096；1min 11.3 亿（前会话扫描）。
  **P0-2 总量 ≈ 15.6 亿行**。
- **执行进度**：首轮 1min 完成 2021-09~2022-02 五个月（月级桶，30~70s/月，全部月级复验过）
  后，2022-03 的 25M 行单块备份 INSERT 撞 CH 7.17GiB 内存上限（Code 241 OvercommitTracker）。
  已加 `--by-day` 天级分块（天然小切片）续跑，自动跳过已完成月。
- 备份表后缀隔离：1min→`tzbak2`、5min→`tzbak4`、15/30/60min→`tzbak2`（不触碰 06 月批
  既有 `tzbak_20260914` 备份）。逐桶校验失败即停，`--only-month` 可断点续跑。
- 运行期两个 CH 内存坑（均已治本入码）：整月单块 INSERT（Code 241，改天级分块）、
  月级 `uniqExact(symbol, trade_time)` 校验（聚合哈希表超限，改按天累计）。
  中断在"删除后回插前"会把整月数据孤儿化进备份表——重启前必须先做 BAK 缺口恢复
  （2022-03/2022-04/2024-05 三次实战恢复，行数守恒校验全过）。

## 六、验证口径速查

- 时区：`SELECT countIf(trade_time < 当日09:00)` 于 06-01~08-01 = 0（四表全过）。
- tick：`trade_date` 行数/`uniqExact(symbol)`；窗口过滤 price0=0；
  dedup 键 `(market_type, symbol, trade_date, timestamp, price)` 幂等。
- 管线：`tmp/tick_subscriber_guard.log`（守护心跳 15s）+ `tmp/tick_subscriber_run.log`
  （统计 received/written/errors）+ `E:\qmt_bridge_sim\ticks3.csv` mtime。
