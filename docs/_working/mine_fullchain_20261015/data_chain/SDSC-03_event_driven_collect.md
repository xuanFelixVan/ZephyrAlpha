---
ttl: task_bound
---
# SDSC-03 事件驱动采集（新闻/宏观/研报/另类/加密；口径=数据源事件）

> 挖矿工程：全链路图12 数据供给链 S1 采集段 3/3｜真源=config/data_supply_chain_map.yaml#DSC-03｜挖矿时点=2026-10-15（含当日只读复跑）
> 自审闸口径：pass=证据实存且复核一致；warn=在册但有未证项/漂移/限定；fail=结构性断裂且无兜底证据。

## 1. 定义

- 环节全名（图12）：事件驱动采集（新闻/宏观/研报/另类/加密；口径=数据源事件），node_type=stage，build_status=built，verified_scope=production（行级 ✅）。
- 职责一句话：7×24 事件流（event_driven */3 全周+news_slow/research_nightly/daily_alt_fx/daily_crypto/nightly_sentiment）采集新闻/宏观/研报/另类/加密五族；本节点语义限定数据源事件，与交易域 position 事件入口（R-015）是两套事件面。
- 决策问句（图原文）：7×24 事件流今天还在进吗？新鲜度该用哪个尺读才不会假绿？

## 2. 六向台账

| 向 | 台账要点 | 文件路径证据 |
|---|---|---|
| 输入面 | DSC-SRC→本环节（事件/另类流）；akshare_alt/rss/fred/eia/qweather/crypto_binance/cls/eastmoney_news 等事件族源；源侧停供与断链分性（road_freight_index 源侧滞后在册勿误判） | config/data_supply_chain_map.yaml edges DSC-SRC→DSC-03+machine.slots（event_driven 11/daily_crypto 6/news_slow 2/research_nightly 2/daily_alt_fx 1/nightly_sentiment 0 special） |
| 输出面 | c3_fundamental.news_data/c1_market.macro_data/alt_fx_rate_ecb/c3_fundamental.research_report/crypto_kline_daily→DSC-04 攒批写+DSC-08（research_report→consensus_daily_build 上游边）；本批复跑：news_data 8,246,648 行 max=2026-10-15T23:30+08、macro_data 67,491 行 max=2026-10-15、research_report max=2026-10-14——五族全鲜 | config/data_supply_chain_map.yaml#DSC-03 data_refs；src/zephyr/data/news_dedup.py（标题 MD5+ReplacingMergeTree 幂等） |
| SSOT 真源 | 槽位真源=schedule.yaml event_driven 等 6 槽；语义层=图12 DSC-03；新鲜度主口径=近窗计数（裸 max(publish_time) 含未来污染，在册禁用） | src/zephyr/data/config/schedule.yaml；config/data_supply_chain_map.yaml#DSC-03 freshness_evidence（近 6h ingest_ts 计数为主口径） |
| 代码模块 | module_id=MOD-L00-004，module_ref=src/zephyr/data/news_dedup.py；执行体 news_dedup.py+implementations/internal_compute_provider.py 实存 | src/zephyr/data/news_dedup.py；src/zephyr/data/implementations/internal_compute_provider.py（本批 ls） |
| 门禁约束 | 禁依赖 system.* 枚举面（09-25 macro 0 字节部件事故判例）；静默失败即假绿；max 未来污染=第三型假读判例（非空串非 1970） | config/data_supply_chain_map.yaml laws+DSC-03 gaps；DSC-GAP-MACRO 节点（事故已解除退役留痕） |
| 自动化触发 | wired_cron：event_driven */3 全周+四日档+nightly_sentiment 特殊分派（dispatched_slots 在册）；task_runs 7 日窗 20,247 笔 alive；fred 源熔断今日 10+ 件留痕（纯内存重启复位，🌑-4 残留） | config/data_supply_chain_map.yaml#DSC-03 machine+trigger_facts；data/failures/20261015__circuit_breaker_fred_*.json（本批 ls 10+ 件） |

## 3. 自审闸三态

| 向 | 三态 | 判据（本批复核 2026-10-15） |
|---|---|---|
| 输入面 | warn | 事件源任务面在册在跑；但 fred 熔断高频触发（今日 10+ 件）、news 族失败件约 3,400 件（7 日窗旁证）、road_freight 源侧停供在册——源健康度分层事实清楚但无收敛指标 |
| 输出面 | pass | 五族产物本批全鲜：news 8.25M 行/今晚 23:30 仍在进、macro 今日、research 昨日、DSC-08 预期链上游边健康 |
| SSOT 真源 | pass | 槽位三层一致；"max 未来污染→近窗计数"口径修正已入 freshness_evidence 字段（判例化） |
| 代码模块 | pass | 两执行体实存 |
| 门禁约束 | warn | 去重靠排序键与全字段判重（DSC-06）不同口径的 residual 在册；未来污染源（脏值少量）未清洗只绕行 |
| 自动化触发 | pass | 6 槽 cron/特殊分派在机、20,247 runs/7 日窗 alive、今晚 news 23:30 仍进数=节拍实测闭合 |

## 4. 缺口与建议

1. 【warn 持续】熔断留痕不可持久（🌑-4）：per-source 熔断纯内存重启复位，事后无法证明熔过没有；今日 fred 10+ 件失败即实例。建议给熔断事件落 append-only jsonl（一行一事件），挂 DSC-13 告警面同目录。
2. 【warn 持续】news_data 未来污染脏值：主口径已绕行（近窗计数），建议清洗腿按 ingest_ts 与 publish_time 差值判非法行进 valid_to 软删（修复纪律走 DSC-16，勿物理删）。
3. 【warn 观察】ssl EOF 失败族（MACRO 残病，failures 1,026 件）处方 IN1-34b（重试退避+页级断点续跑）仍待施工，归数据班。
4. 【正向证据】DSC-GAP-NEWSGHOST 幽灵引用已在消费册侧修正：config/strategy_production_map.yaml:102 现引真身 c3_fundamental.news_data（注记"幽灵名退役留档=防再引节点"），CH 侧 c1_market.news_data 仍应永不存在（本批复跑 Code 60=防再引节点继续有效）。
