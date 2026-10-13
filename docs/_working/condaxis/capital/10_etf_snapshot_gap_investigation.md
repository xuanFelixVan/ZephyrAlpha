---
ttl: task_bound
title: ETF 份额快照断供调查——断因定位/哨兵层根因/修复判定（资金线 P2 车道产物）
created: '2026-10-13'
session: st-cdx-capital-20261013
status: investigation_report
family_id: CONDAXIS-CAMPAIGN
completes_when: 上报项处置完成且随 CONDAXIS-CAMPAIGN 归档
---

# ETF 份额快照断供调查（10_etf_snapshot_gap_investigation）

> 任务来源：6_data_audit §2-1（ETF 快照仅 2 交易日有数=daily_capital 排程 16 交易日缺失，只上报不擅修）。
> 本册 2026-10-13 21:30-21:45 实查定性：**断因已定位（源端断连为主因＋一日整槽缺位为次因），今日已自愈，无机械可修项，16 交易日=永久缺口**；另发现第二层根因（告警链路被动面无人读）呈报 Owner。
> 全程只读：integrator_progress.db（ro-uri）/CH 只读/外部源单次 GET 探测；零写库零改配置。

## §1 断因（integrator_progress.db task_runs 21 条实测）

| 层 | 证据（命令原文与读数） | 结论 |
|---|---|---|
| 任务面 | `SELECT run_id,started_at,status,rows_written,substr(error_msg,1,110) FROM task_runs WHERE task_id='etf_share_snapshot_refresh' ORDER BY started_at DESC` → 09-18 双跑 SUCCESS（03:42Z 手动口径＋10:00Z 排程，各 1,621 行）；09-21..10-11 每交易日 10:00Z（北京 18:00）排程**全部触发**但 FAILED（rows=0，error=`fund_etf_spot_em 失败: ('Connection aborted.', RemoteDisconnected('Remote end closed connection without response'))`）＋周末/假日 catchup 补跑 5 次同败；10-13T10:00:20Z SUCCESS 1,643 行 | **任务已启用且排程正常触发**——非"任务未启用"、非"排程间隙" |
| 源面 | 失败时长 2:30-5:16 分钟=重试指纹（policies.yaml akshare 槽 max_retries=5/backoff=jittered/initial 2s，retry_on 含 ConnectionError——RemoteDisconnected 在 requests 语义内=ConnectionError，重试确有发生且 5 次全败）；现场复核 2026-10-13 21:3x 直调 `ak.fund_etf_spot_em()`（akshare 1.18.75）23 秒 1,643 行 16 页成功 | **主因=东财 push2 ETF 实时列表源端断连**（09-21..10-11 段反爬/不稳定；同窗 09-18 与 10-13 成功证明任务与管道本身健康）；**当前已自愈** |
| 调度面 | `SELECT count(DISTINCT task_id) FROM task_runs WHERE started_at LIKE '2026-10-12T10:0%'` → **0**（对照：10-11=10、10-13=47；当日全部任务仅 2,059 跑 vs 邻日 2,957-3,333） | **次因=10-12（周一交易日）daily_capital 整槽未触发**——调度进程层缺位一天（非 tasks.yaml/schedule.yaml 配置问题；当日根因=调度进程停摆/重启，日志面移交数据运维） |
| 断供史口径修正 | 6_data_audit "16 交易日缺失"实测精化：源端断连失败=09-21..09-25、09-28..09-30、10-08、10-09、10-11（catchup 口径）＋10-12 整槽缺位；09-18 与 10-13 两个成功日恰=表内仅有的 2 个交易日 | 与 CH 表观（仅 2026-09-18/2026-10-13 有数）完全互证 |

## §2 哨兵层第二根因（为什么断 16 交易日无人知）

1. **检测面在岗**：data_supply_sentinel（schedule.yaml cron "50 6 * * *"＝每日 06:50）在册覆盖 `c1_market.market_etf_share_snapshot`（data_supply_sentinel.yaml:190-194，max_lag_days: 5，past_only: true）——断供 >5 自然日必然检出 breached。
2. **通知面静默**：Alerter 厂商外推通道（飞书/SMTP）2026-09-15 Owner 裁定裁撤（alerter.py:32-34 注释在案），现行通知面=前端页面/日志/失败汇总文件＋webhook 可插拔外推（**缺省 enabled=false fail-closed**）。实测 `data/runtime/alert_webhook_trail.jsonl` 190 条**全部 kind=blocked**（reason="enabled=false（缺省 fail-closed：无端点配置即不外发）"，2026-09-18 起）——哨兵检出后投影 OpsAlertFeed 通知板（R-021"写了没人读的通道等于没建"），但**通知板为被动面，无人建立巡检节奏 ⇒ 实际静默**。
3. 与前两例同族（"任务存在≠管线活着"第三例之后新增第四形态：**哨兵在岗≠有人读哨兵**）。

## §3 修复判定（车道职权内）

| 项 | 判定 | 理由 |
|---|---|---|
| tasks.yaml 任务配置 | **无需修** | schedule=daily_capital 正确挂载、source/fallback 配置正确、排程正常触发（21 条 run 记录） |
| schedule.yaml 排程 | **无需修** | 18:00 cron 正确；10-12 缺位是进程层非配置层 |
| 重试策略 | **无需修** | max_retries=5+jittered 已在岗且确实执行；源端整段断连时加次数无用 |
| 16 交易日缺口回补 | **不可回补（永久缺口）** | fund_etf_spot_em=当日实时快照（份额/IOPV/折溢价），无历史查询面；快照积累制固有属性（tasks.yaml:3705 注释在案）。**后果：C6 ETF 申赎差分（3_C §4 挂起项）的差分基线在 09-18→10-13 间断档，只能自 10-13 起重建相邻日差分** |
| 增量核验 | **无需跑** | 无修复即无核验对象；今日 18:00 排程已自然写入 1,643 行（10-13），车道直调复核同数 |

## §4 呈报项（Owner/数据运维面，非本车道职权）

1. **告警"有人读"闭环缺口**：OpsAlertFeed 通知板被动面＋外推裁撤组合=哨兵实际静默（本册 §2）。选项：重开 webhook 外推（需端点=密钥面+对外发布面=Owner 保留）或建立通知板日检节奏（运维流程面）。建议随 6_data_audit §3.2-甲"行数画像带"呈批合并裁定。
2. **10-12 daily_capital 整槽缺位**当日根因：调度进程当日 18:00 时段停摆/重启？（integrator 打卡侧只有缺位事实）——查当日 scheduler 进程日志（data 运维面）。
3. **快照积累制任务韧性**：源端反爬敏感时段（盘后 18:00）命中率不稳，可考虑午后/晚间二次尝试槽提高当日命中（RESOURCE-SCHEDULE 错峰治理域，呈批非本车道拍）。
4. 顺带观察项（非事故）：两融 margin_trading 10-12 缺日（6_data_audit §2-3）——margin 任务挂 nightly_financial 22:00 槽（tasks.yaml:109），10-12 22:00 跑 SUCCESS 4,108 行、10-13 22:00 未到点；按 T+1 晨披口径 10-12 数据预计**今晚 22:00 自愈**，建议明晨复核而非升级。

## §5 证据链命令原文（复核用）

- `sqlite3 file:D:/ZephyrAlpha/data/integrator_progress.db?mode=ro` → `SELECT ... FROM task_runs WHERE task_id='etf_share_snapshot_refresh'`（21 条全录 §1）
- `python -c "import akshare as ak; ak.fund_etf_spot_em()"`（1.18.75，2026-10-13 21:3x，23s/1,643 行成功）
- CH：`SELECT trade_date, count() FROM c1_market.market_etf_share_snapshot GROUP BY trade_date ORDER BY trade_date`（6_data_audit §1 已录：仅 09-18=1,621/10-13=1,643）
- `data/runtime/alert_webhook_trail.jsonl`（190 条 blocked 全量计数 2026-10-13 21:4x）
