---
ttl: task_bound
session: st-data-fix-20260921
title: 数据正确性线分包3——哨兵补盲+改册收口（哨兵 4 腿+日历逐日 diff 检查器+gaps 改册+12 小表 60s 攒批）交付报告
---

# p3 哨兵补盲+改册收口报告（2026-09-21 早 · st-data-fix-20260921 · WO-3）

> 前情承接：分包1 哨兵/gaps 首批（226db0d2bc）、分包0 tick 09-17 找回（c65ffa5a06）、
> 分包2 六链修复（363e4fa1ed，移交单①竞价缺口登记+②哨兵新腿数据）。本批在其基础上追加，
> 未重做上述任何已落地件。

## 一、哨兵补 4 行（src/zephyr/data/config/data_supply_sentinel.yaml）

四腿全部「先实测库现状、后定档」，阈值行内注释均写明依据：

| 表 | 腿 | 定档依据（实测 09-21） |
|---|---|---|
| index_quote | trading_days/2 + floor 300/7日 | 09-20 重建后新常态=盘后 EOD 日快照：09-17/18 各 609 行/562 只、09-21 盘中 1,167 行/569 只 [亲验] |
| news_sentiment_window | calendar/3 + floor 3/7日 | 每日 1 行 market 粒度、周末照跑（09-19/20 各 1 行 [亲验]）→日历日口径 |
| auction_snapshot | 原行升级 trading_days/2 + floor 1300/7日 | 桥流 09-17=3,230 行/日 vs miniqmt 时代 5,218-5,220（宇宙收窄，禁按旧宇宙定档）[亲验] |
| tick_data | trading_days/3 + floor 800万/7日 | 交易日 2,000-3,400 万行（09-16=2,390.9 万、09-17=2,832.7 万 [分包0 亲验]）；qmt_bridge 对 tick_data=no-op（provider L446-449 [亲验代码]）→维持现状将于 09-24 起红=真阳性，处置=模拟盘 T+1 回补接线（p0 评估件）或 Owner 裁定 accepted |

- **红证（双向之红）**：四腿阈值按「非交易日不假红」语义配置——新鲜度腿 lag_basis=trading_days
  （FF-12 判定链同档），行数地板沿用 daily_valuation 先例（7 自然日窗、地板≈0.4 个交易量级
  =只捕近全停，周末两日自然容忍）。
- **绿证（双向之绿）**：`_load_config` 结构校验通过 58 腿；`find_heartbeat_only_blind_spots`=空；
  `yaml.safe_load` 写后进程外复核过；test_supply_sentinel 22/22 过（含 shipped-config 结构
  钉死组）。
- ** tick_data 腿点亮后 09-24 起红属设计内真阳性**（当前无在跑供给通道），已在行内注释写明
  处置路径，禁为过检降档。

## 二、交易日历逐日 diff 检查器（新模块 zephyr.data.calendar_coverage_checker）

治「max-date 原理性失明」：交易日历逐日 × 表内日期集合双向差集 → missing_days（内部洞）+
extra_days（非交易日落行污染）。

- **红证（注入测试洞必被抓）**：tests/zephyr/data/test_calendar_coverage_checker.py 11/11 过——
  ①5 交易日删 2 日 → missing 精确命中；②全覆盖 → ok（对照证非口径噪音）；③周六落行 →
  extra 抓到；④calendar 节奏周末照跑不算 extra；⑤since 通道起点前史双向不期望；
  ⑥runner 炸/空返回 → error 记账不抛不阻断；⑦日历删一日 → 期望与实有同缺不鸣/表有则报
  extra（坏日历下行为自洽、宁报不漏）。全程假 runner 注入=等价 tmp_path 隔离语义，
  零生产路径。
- **绿证（全量表实跑零误报）**：默认观察名单活体实跑（窗 09-07~09-20）——首轮 breached=3，
  逐条核实：stock_basic 09-16（真缺，已扩册）、auction 09-18（真缺，已立新条）、
  auction 09-04/07（A3 家族 9 月上旬缺采日真缺）；index_quote 6 个「extra」为 since 前史
  误报 → 修 since 语义（前史双向不期望）+两表 since 推进到已登记永久洞之后（BRK-046
  告警疲劳红线：已入册永久洞禁每日重鸣）。终轮：**ok=True，checked=7，breached=0**。
  news_sentiment_window 因未注册 TableRegistry 品类（TABLE-NAME-REGISTRY 门禁禁硬编码
  表名）从默认名单摘除，其断供监控由本批哨兵 calendar/3+floor3 腿承接；落地路径共过
  五道门禁死信并逐项修正（CREATE-GUARD/15字段头/NO-HIGH-COMPLEXITY 拆函数/
  NO-BARE-SQL noqa/ALGO-FLOW-LINK 摘锚/DEPGRAPH 转 testing），全部留痕队列死信。
- **首战战果（检查器上线即抓到 max-date 类盲区）**：daily_valuation 09-16=2,165/09-17=4,676/
  09-18=4,676 行=增量链部分写入病未根治（符号覆盖缺 15-61%），该形态对 max-date 与 7 日
  行数地板均不可见——已写入 gaps 册 verification_20260921，逐日监控归本检查器。
- **挂载（事件触发，签字⑨已批任务表）**：schedule.yaml `calendar_coverage_check` 槽
  （cron 07:10，哨兵 06:50 之后）+ scheduler.py 同名分支（惰性导入+异常降级 ERROR 告警
  不炸调度器，仿 data_supply_sentinel 先例）。未入 tasks.yaml（本仓纪律：特殊时段槽位
  一律不入 tasks.yaml，见 tasks.yaml L3659 在案注释）；无自建 cron/Timer/sleep-loop 常驻
  （宪法 §9.3）。
- **全合规链**：①capability_lookup.find 13 次查询留痕 `.runtime/lookup_audit/st-data-fix-20260921.jsonl`
  （同域零命中=无重复建设）；②creation_token `datafix-calcover-20260921` 入
  capability_canonical_file_registry.yaml 顶级 creation_tokens 节（四行式+行尾换行+
  yaml.safe_load 验证，9,244 token）；③apply_depgraph.py --add-design-node 登记
  （node_id=14905533，granularity=file）；④add_module_translation.py 登记大白话简介
  （15 字段蓝图头+[A_module] 全，entries 7,155 条）。

## 三、known_data_gaps 改册（57→59 条，16 处锚定改动，全部先查实况后落笔）

§2.1 八条逐条实测核验（「报告是死的库是活的」，两处实测推翻报告口径）：

| 条目 | 报告建议 | 实况核验 [亲验 09-21] | 本批处置 |
|---|---|---|---|
| index_valuation_daily_duplicate_rows | 退回 open | 报告测于 WO-1 重建前；现 FINAL=8,120、重复组=0、cape 近窗腿绿 | **resolved**（恶化判定被 WO-1 重建超越，如实记录） |
| daily_valuation_2026_09_10_missing | 维持 reopened | 原窗 09-09~14 全修复（5,548-5,562 行/日、close>0 99.8%+）；新证 09-16/17/18 部分写入 15-61% | **mitigated**（残余归检查器+full_refresh 重跑工单） |
| daily_valuation_price_legs_zero_mislabeled | 维持 open | FINAL=189,087、close>0=99.91%；残余=data_source 标注+ps_ttm 语义+turnover 源缺 | **resolved**（0 值主病灶亡；三项元数据残余如实登记另立小工单） |
| etf_minute_tz_split_pre_202607 | 改 completed | 五张 bak 全在，合计 **439,164,446 行/7.53 GiB**（1min=325,198,058/5min=71,775,532/15min=24,302,647/30min=11,932,683/60min=5,955,526）；live 旧纪元行=0 | **completed**（记回滚窗口=反向换名；与报告 440,481,332/8.11GB 的差=测量基准，两口径并记；执行授权链差异不追溯归因） |
| consensus_daily_value_cols_pit_broken | 更新口径 | FINAL 1,563,996 行：2017=300,566/2018=349,219/2019=311,934/2020=260,490/2021=250,420/2026=91,367（max 09-15）；2022-2025 仍 0 | 口径更新（报告 2026=182,734 系 raw 双版本未合并视角=FINAL 恰 2 倍，已收敛）；**open 维持** |
| research_report_hot_value_rating_change_empty | 更新登记 | system.columns 实测 hot_value 不存在、rating_change 在 | 口径收窄（hot_value 了结、rating_change 承续）；**open 维持** |
| reservoir_level_source_stale | 维持 monitoring | max(tdate)=07-31（滞后 52 天）/ingest=09-18 | monitoring 维持+新验证段 |
| technical_indicator_duplicate_rows_ingest_ts | 维持 monitoring | dwm 分片重跑在飞，避让未重扫 | monitoring 维持+回填期注记（argMax 口径加倍必须） |

移交件与新发：

- **新条 auction_20260918_transition_gap**（分包2 移交①）：auction_snapshot 09-18=0 [亲验]
  （09-17=3,230）、tick_depth_5 09-18 竞价窗 18 行 [移交实测]、桥午后才通=竞价窗落真空；
  status=no_source 仿 A3 先例（过程数据永缺不可派生）。
- **新条 list_tables_surviving_1970_sentinel_rows**（W4/W5+cb_list 收口）：etf_list 存活行
  1970=**84**/2,184、index_list 存活行=**22**（1,700 墓碑设计内）、convertible_bond_list
  1,051 行中 3 行存活 1970+五列（end_date/delist_date/convert_*）全表 1970 占位 [皆亲验]。
  cb_list 现状（1,051/3）与报告（2,102/1,054）不一致=两轮测量间他方去重/修复，两口径并记、
  以亲验为准；**1970 治本条目留白分包6**（文件 release 后其改）。
- **扩条 stock_basic_snapshot_days_missing**（W1）：09-16 整日 0 行 [亲验]（09-15=5,562、
  09-17/18=5,565），缺日清单扩为 5 交易日。

## 四、12 小表攒批写入端（60s 窗）

- 病灶（ch_health §3.3）：12 表 parts>300 且行数<10 万，共性=高频小批量 INSERT+30s 默认
  flush 窗（1 行/part 形态）。
- 改造（最小 diff）：tasks.yaml per-task `buffer_max_seconds: 60`（#ARCH-CH-013 Phase 4
  既有机制，news_data=300 先例同配方）——12 表全部 **21 个任务**（含 macro_data 的
  eia/fred/worldbank 变体与各 full_refresh 双胞胎）全部生效，yaml.safe_load 前后双验，
  任务总数 265 不变。
- **红证（flush 语义）**：tests/zephyr/data/test_buffered_writer_60s_batch.py 3/3 过——
  ①单表单批：60s 窗内小批 add 不自动 flush、手动 flush 恰一次 INSERT 全量行数守恒
  （macro_credit_money 真表名打桩验证，ch_writer 三出口 monkeypatch 零真实写入）；
  ②窗满触发：+30s 不 flush（若仍 30s 旧窗语义此步即红）、+61s 自动 flush 一次全量；
  ③配置契约：12 表全部任务 buffer==60（防回归漂移）。
- 相邻回归：test_data_scheduler/test_supply_sentinel/test_quality_sentinel/test_data_task_queue
  合计 154 过（含顺手收口 1 项陈旧钉死，见 §五）。禁 OPTIMIZE（乙线独占窗）未触碰。

## 五、顺手收口与偏差披露

- **test_supply_sentinel 陈旧钉死收口**：shipped-config 测试仍钉 daily_valuation 填充率腿
  cols=[close,amount,turnover]，而分包1 WO-1 已依法拆出 turnover（kline_daily 源近窗非零
  0.9% 属源端缺口，永久红腿=BRK-046 告警疲劳，yaml 同批注释+gaps 工单在案）——该测试自
  WO-1 起持续红（非本批引入）。按同会话收口原则更新钉死为 [close,amount]+守卫意图保留
  （仍禁粗断言），变异 μ3 语义不变。
- **检查器首版两处修正**（红证过程中发现并修复）：since 前史日期误计 extra（语义修正：
  双向不期望）；start/end 边界对实有日期集合未过滤（比较类型 bug）。均有对应测试钉住。
- tick_data 09-18 有少量行 [亲验 max(trade_date)=09-18]：桥切换日下午重叠期写入，不影响
  「无在跑通道」判定（bridge capability 对 tick_data=no-op）。

## 六、册账 diff 一致性核验与停手项

- 册账一致性：known_data_gaps 59 条 id 全局唯一（脚本断言）；gaps 与哨兵互指一致
  （auction 09-18 条 ↔ 哨兵行注释；daily_valuation 残余 ↔ 检查器职责）；本报告数字与
  各 yaml 行内注释同源（同批写入）。
- **停手项（未做，均有主）**：①tick_data 09-24 起真红后的处置（模拟盘接线 or accepted）
  =Owner 门位；②daily_valuation 09-16/17/18 全符号覆盖重跑（11h 级）=后续工单排期；
  ③1970 治本条目=分包6（本文件已 release，其可安全后改）；④data_source/ps_ttm 元数据
  修正小工单；⑤auction 09-04/07 等 A3 家族永久洞已在册不再施工。
- 证据等级：[亲验]=本会话 ch_reader 轻查询/system.parts 实测；[移交实测]=分包2 移交单
  数字（未重扫重 IO 面）；代码行号引用为当版实读。
