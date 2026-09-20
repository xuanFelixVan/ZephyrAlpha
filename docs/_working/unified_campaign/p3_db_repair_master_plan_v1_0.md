---
ttl: task_bound
completes_when: 全部条目处方执行验收通过（随战役收官归档）
session: st-unified-plan-20260920
issue: UNIFIED-CAMPAIGN-001-P3-REPAIR
---

# 包③交付·数据库健康修复总方案 v1.0（st-unified-plan-20260920，2026-09-20）

> 定位（裁定#378①）：**处方真源**——以 dataqa 四报告（R1 ch_health/R2 gaps_registry/R3 test_health/R4 cross_findings，`docs/_working/dataqa_audit/`）为病历，逐条**复现→根因→处方→验收**。台账（ledger）管盘点、派工单（workorders）管执行路由，本件管医嘱。执行日铁律：**报告是死的库是活的，每条先复现再修**；CH 只读探针用 zephyr_reader；破坏性操作三步验证（必要性/真实性/可逆性）。通用探针入口：

```python
python -c "import sys; sys.path.insert(0,'src'); from zephyr.infrastructure.database_service import get_db_service; c=get_db_service().get_clickhouse_conn(role='reader'); print(c.execute('<SQL>')); c.disconnect()"
```

## 甲·P0 级（消费禁用级，WO-1，签字③）

### 病-1 index_valuation_daily 派生列 100% NULL+132 重复组复发（A1/N1/P0-1）
- **复现**：`SELECT countIf(cape_5y IS NULL), count() FROM c1_market.index_valuation_daily FINAL`（病历值 8125/8125）；`SELECT symbol, trade_date, count() FROM c1_market.index_valuation_daily GROUP BY 1,2 HAVING count()>1`（病历 132 组，000300/000905 于 08-28/08-31/09-17）。
- **根因**：多写者无 version 列结构病——两写路径同键各写一版，一版带派生列一版不带；09-18"止血（写前携带）"对该路径无效（R2 实证恶化）。
- **处方**（三选一，裁定#379 推荐①）：①加 version 列单写者合并（爆炸半径最小+对齐 ReplacingMergeTree 语义）②internal_compute 重算管道接电为唯一派生写入方③原始行与派生行分表。修复前估值分位/ERP 消费禁用声明（S2/regime 消费方自查）。
- **验收**：同复现命令 FINAL NULL 率=0（或分表后派生表覆盖率 100%）；重复组=0 且连续 5 交易日无复发（哨兵列填充率腿转绿）。

### 病-2 daily_valuation 价格腿全 0+周六污染+mock 假绿（A2/N2/P0-2）
- **复现**：`SELECT countIf(close>0), count() FROM c1_market.daily_valuation FINAL`（病历 0/271,266 且活体增长）；`SELECT trade_date, count() FROM c1_market.daily_valuation WHERE trade_date='2026-09-19'`（周六 3674 行）；fetch_perf daily_valuation_incremental 连日 mock rows=0 SUCCESS。
- **根因**：真实写者 akshare 行情腿断（data_source=100% local_valuation）；"0 行成功不告警"未修；任务无交易日 gate。
- **处方**（签字③随批，推荐=A1 行情腿同步修）：价格腿自 kline_daily 回填 close/amount/turnover 等 9 列+周六污染行冷存后清+交易日 gate（trade_calendar）+0 行成功告警（sentinel 告警腿）。
- **验收**：非零率>99%（历史回填段）；周六行=0；连续 5 交易日非零率>99% 且 mock 空转有告警留痕。

## 乙·断供止血级（P1，WO-2）

### 病-3 index_quote 09-16 停（A4/N4）
- **复现**：`SELECT max(trade_date), countIf(trade_date='2026-09-17'), countIf(trade_date='2026-09-18') FROM c1_market.index_quote`（病历 max=09-16，09-17/18=0）；fetch_perf 09-16 后无 index_quote 记录。
- **根因**：ZephyrAlpha_IndexMinuteEOD（xtdata 源）随 miniQMT 09-18 退役死亡，替代任务未接。
- **处方**：采集链换桥重建（qmt_bridge capability 挂 index EOD 或 akshare 替代源选型）；fetch_perf 接入（防再静默）。
- **验收**：重建后首交易日 max=当日+行数≥修复期基线（240 点/日量级）；哨兵新腿（A9）覆盖。

### 病-4 news_sentiment_window 09-14 停（A5/N5）
- **复现**：`SELECT max(window_date) FROM c1_market.news_sentiment_window`（病历 09-14）；fetch_perf 全无痕（内部函数直写）。
- **根因**：run_nightly_sentiment 静默失败（schedule 槽在 20 8 * * *、调度进程活、执行无痕=盲区形态）。
- **处方**：排查静默失败根因（日志定位）+该任务接入 fetch_perf 或独立心跳日志+修复后回补 09-15 起窗口。
- **验收**：max(window_date)=最新交易日+连续 3 日 fetch_perf 有痕。

### 病-5 auction 09-17 停（A6/N6）
- **复现**：`SELECT max(trade_date) FROM c1_market.auction_snapshot`（病历 09-16）；fetch_perf 09-17 `qmt_bridge auction 派生失败 [WinError 10038] 非套接字操作`+`ch_writer get_client() 返回 None（连接冷却期）`实锤。
- **根因**：桥派生 socket 错误+CH 连接冷却期叠加，无自愈重试。
- **处方**：派生任务加 socket 自愈重试（指数退避）+连接冷却期感知；修后回补 09-17 起竞价窗。
- **验收**：max=最新交易日+09-17 起缺口回补（tick_depth_5 有源可派生段）。

### 病-6 crypto_kline_daily 09-19 断（A7/N7）
- **复现**：`SELECT trade_date, count() FROM c1_market.crypto_kline_daily GROUP BY 1 ORDER BY 1 DESC LIMIT 5`（病历 108 行/日→09-18 51→09-19=0）。
- **根因**：daily_crypto 任务半死（09-18 半日+09-19 全断），时点与 miniQMT 退役吻合，依赖关系待排查（fc2dec40af 曾治本 executor: light 挂错池）。
- **处方**：任务依赖排查+修复+回补；7×24 资产断供=哨兵优先腿。
- **验收**：日行数回 108 量级+连续 3 日。

### 病-7 stock_indicator 09-18 半日（A8/W2）
- **复现**：`SELECT trade_date, count() FROM c1_market.stock_indicator GROUP BY 1 ORDER BY 1 DESC LIMIT 3`（病历 09-18=1000/5565）。
- **根因**：09-18 11:09 full_refresh 后未再触发（09-19/20 零执行）。
- **处方**：重跑刷新补齐 09-18+排查触发停因；周一 09-21 盘前消费受影响=最短路径优先。
- **验收**：09-18 行数=5565 量级+09-21 当日正常。

### 病-8 tilib 夜跑回填阵亡（C-5，2026-09-20 新发活体断供）
- **复现**：`tail -20 .runtime/tmp/tilib-probe/backfill_night.log`（09-20 04:03 Code 241 内存总闸 7.08>7.05GiB 阵亡；BufferedWriter 缓冲 132,834 行丢失——data/local_fallback/c1_market__technical_indicator/ 空壳实证落盘未成）；`SELECT countIf(gp_pred!=0), count() FROM c1_market.technical_indicator WHERE trade_date>='2026-06-01'`（本班实测 0/144,992,061）。
- **根因**：两会话同窗合击 CH 内存总闸（09-20 04:03 时点重 IO 并发）；缓冲区数据随进程死丢失（可重跑再生，非永久损失）。
- **处方**：低峰单进程重跑 dwm 回填（避开声明窗+其他 CH 负载）→新列（gp_pred/gp_sig/continuation_40/highpass_40/supersmoother_10 等批5/6 族）历史回填推进→全部 210 列验收核销（探针 audit_all_cols.py 思路）→夜跑健康=连续 3 日无 Code 241。
- **验收**：新列近月非零率>95%+夜跑日志连续 3 日无 ERROR+210 列验收台账闭环（WO-4 尾款）。

### 病-9 tick 09-17 永久缺口（A3/N3——登记型，不修库）
- **复现**：`SELECT countIf(trade_date='2026-09-17') FROM c1_market.tick_data` 与 tick_depth_5 同日双 0（交易日全黑）。
- **根因**：miniQMT 收摊与桥接管间真空日；QMT 历史下载随 09-18 退役+bdpan 归档 07-03 停更=**不可回补**。
- **处方**：known_data_gaps 登记留痕（同 07/08 月八日缺口先例）；kline_1min 合成近似 tick 仅评估（data_source=synth 标记，签字⑩默认=只登记不合成）。
- **验收**：gaps 册新增条目+下游消费方知晓注记。

## 丙·哨兵与监控（WO-3）

### 病-10 哨兵盲区（A9/P1-1）
- **复现**：sentinel check_tables() 实跑 checked=55/breached=9；index_quote/news_sentiment_window/auction_snapshot/tick_data 四表无阈值行；tick 09-17 内部洞证明 max-date 原理性失明。
- **根因**：哨兵只有 max-date 一维；新断供表未配腿；无日历维度检查。
- **处方**：data_supply_sentinel.yaml 补 4 行+新增交易日历逐日 diff 检查器（交易日历×表内日期集合差集，事件触发禁 cron）。
- **验收**：注入测试洞（删一日期望）检查器抓到=绿；四表新腿入 checked 数。

## 丁·卫生与空间（WO-6/WO-9，签字①②，Owner 在场）

### 病-11 备份/污染表 35.4G（A11=R1 §5 十七张清单）
- **复现**：R1 §5 表逐张 `SELECT count(), max(<date>) FROM <table>`；本班探针 top8 已见 news_data_corrupt 12.99G+news_data_pre_tz2 12.88G 在库。
- **根因**：时区修复回滚保险（5 张 etf tz_bak）+污染快照+旧备份累积。
- **处方**：逐表 export Parquet 双副本（F+G）→行数 verify→凭批文 drop（张数 12vs17 执行日实测仲裁——R1 §5 十七张 vs 包④清单十二张，drop 前逐张对两清单）；etf tz_bak 保留至修复后月度复盘（签字①批文可裁）。
- **验收**：尸体清零+内部空闲≥200G+export 副本行数=原表行数。

### 病-12 1970 假日期 18 表 43.6 万行（A12=R1 §4 双清单）
- **复现**：R1 §4 分区级（49 parts/12 表）+行级（18 表）双清单命令重跑。
- **根因**："无值写成 0"家族日期版（解禁日/披露日等哨兵零值）。
- **处方**（签字②推荐）：PIT 关死（登记 known_data_gaps）+补真值排 backlog；convertible_bond_list 1,054 行先补登记（未入册）。
- **验收**：1970 行数清零（关死段）+gaps 册逐表条目。

### 病-13 12 小表 parts 爆炸（A13=R1 §3.3 清单）
- **复现**：R1 §3.3 命令重跑（alt_regime_signal 886/alt_shipping_index 699/macro_data 736 等 12 张，三张 1 行/part 极端形态）。
- **根因**：调度高频小批量 INSERT 无合并（macro_* 每指标每期一行逐行 INSERT）。
- **处方**：写入端攒批（60s 窗，归甲 WO-3）+独占窗 OPTIMIZE FINAL 小表秒级（归乙 WO-6）；不改 schema。
- **验收**：parts<50/表+周复查不回升。

### 病-14 technical_indicator parts 高位（A10/P1-6）
- **复现**：`SELECT count() FROM system.parts WHERE active AND table='technical_indicator'`（dataqa 时 1339→**本班 09-20 实测 1181**，合并进行中）。
- **根因**：dwm 回填高频小批写（09-19 单日+289 parts）；09-15 曾 Code 241 全库拒查。
- **处方**：C-5 夜跑修复健康后（前置）观察 parts 显著回落→独占窗 OPTIMIZE FINAL（声明板排队，与批10 回填互斥）。
- **验收**：parts 回落至大表健康带（参照 kline_1min 264 量级）+单行 SELECT 成功。

### 病-15 欠账 24.9G archive-range（包④契约线）
- **复现**：data_retention_contract 对账（TI 窗口外 19.4G+冷线 5.5G）。
- **处方**：archiver 三阶段 export→verify→drop（唯一通道）；INV-RET-002 手动触发红线随签字⑤修订后滚动归档 reconciler 接线。
- **验收**：欠账清零+冷层副本对账。

## 戊·册账一致（WO-3，甲改册）

### 病-16 known_data_gaps 8 条改册+A19 漂移（A15）
- **复现**：R2 §2.1 八条逐条（etf 时区改 completed+consensus_daily_repaired 部分回填改口径+research_report hot_value 列消失改登记+stock_basic 09-16 缺日扩条目等）。
- **处方**：逐条改册（etf 时区条目记回滚窗口=bak 五张 440,481,332 行/8.11G）。
- **验收**：册账逐条 diff 实一致。

### 病-17 etf_list/index_list 存活行 1970（W4/W5）
- **复现**：R2 §3 W4/W5 命令（84 行/22 行 valid_to IS NULL 且 list_date=1970）。
- **处方**：改册+月度刷新机制修正（首跑漏段排查），与病-12 同族处置。
- **验收**：存活行 list_date 全真值或墓碑化。

### 病-18 周末写入无交易日 gate（A16/W3）
- **复现**：sector_fund_flow 09-19 周六 450 行+daily_valuation 09-19 3674 行。
- **处方**：两任务加 trade_calendar gate（随病-2 同批）。
- **验收**：下个周六零写入。

### 病-19 77 表未登记 data_asset_registry（A14/P2-6）
- **复现**：R1 §7 交叉命令（246 表中 77 live 未登记）。
- **处方**：生成器口径重建（禁手工；归丙 WO-13 执行，处方案在此归口）。
- **验收**：registry 覆盖率 100%+生成器可重跑幂等。

## 执行顺序医嘱（与波次网络对齐）

病-1/2（P0，签字③）→病-3..8（断供止血，可并行）→病-9/10（登记+哨兵）→病-11..15（签字①②后独占窗，Owner 在场）→病-16..19（改册随收口）。每病验收后回执六要素登记线内台账；本方案条目状态随 ledger §1-§4 同步销行。
