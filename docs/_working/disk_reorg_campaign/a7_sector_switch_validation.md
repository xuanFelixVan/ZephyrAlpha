---
ttl: task_bound
---

# [BLUEPRINT] | docs/_working/disk_reorg_campaign/a7_sector_switch_validation.md |
<!-- [MODULE]  -->
<!-- [STABILITY] evolving -->
<!-- [SAFETY] L -->

# a7 板块线切源前置校验批（a6 §F+ tdx→内部撮合切换的开工条件件）

> **⚠ 版本 2 勘误（2026-10-01 凌晨，st-c9-secktide 前役发现后全面修正）**：本件 v1 曾把
> 09-11~09-29 的 1m 数据误归因为"tdx 概念腿"——实为 **方案 J 合成腿**（synth_board_minute.py，
> synth_eq 等权口径，secktide 09-29 治愈役在案）。真 tdx 全族 09-10 死（服务端对 pytdx 系协议层
> 拒答 K 线族，secktide 取证破案）。据此：批A 对照物实为 J 合成值（连续性偏差），真 tdx 对照=
> 批B/批C（09-09 真值）。数字已按此重解读，结论不变反加强。

执行：st-storageswap-20260930 夜班（2026-09-30 深夜）｜性质：只读校验分析，未切源未改任务
校验脚本（24h TTL 临时件）：`.runtime/tmp/sector_eqw_validation_20260930.py`
逐板明细 CSV（24h TTL，数字已誊抄入本件）：`.runtime/tmp/sector_eqw_validation_concepts_20260929.csv` / `_industry_20260909.csv` / `_concepts_vs_tdx_20260909.csv`

## 一、校验结论：切源方法可行（PASS，附切法条件）

**批C 主批（等权 vs 真 tdx，2026-09-09，575 概念板）**：成员=sector_constituent as-of 当日；个股源=kline_1min；对照=真 tdx 1m 已入库值（死供前最后完整日）：

| 指标 | 中位 | p90 | max |
|---|---|---|---|
| 分钟路径 RMS 偏差 | **1.4 bps** | 22.5 | (毒条板 4024) |
| 日收益差（等权 vs 加权） | **17.4 bps** | 103.9 | (毒条板 237085) |
| 分钟收益相关 | **0.911** | (p25) 0.714 | (min) -0.09 |
| 路径 RMS<30bps 的板块占比 | **91%** | | |

**批B 行业族（同日真 tdx，127/132）**：路径 RMS 中位 **2.7 bps** / p90 9.2；相关中位 0.831（成员=当前快照，行业板 09-30 前无 PIT 真值，漂移注记见 §二.5）。

**批A 连续性批（等权 vs 方案 J 合成值，2026-09-29，575 概念板）**：路径 RMS 中位 4.3 bps / 相关 0.903 / 日收益差中位 25.9 bps——解读=两种成员等权合成的相互偏差（连续性参考），非 vs tdx 口径差。

**口径差定性**：等权 vs tdx 加权的结构性点位差（日收益 0.17~1.04pp @p50~p90）。切源可行域：
1. **收益/方向类消费（榜、重采样、信号触发）可切**，对真 tdx 路径偏差 bps 级、方向高度一致；
2. **绝对点位序列不可与 tdx 历史拼接**——切换日=基点重置（方案 J 的跨日链式=另一种选择，收敛裁定见 §六）；
3. **小成员板与毒条板敏感性**：批C 尾巴 ~8% 板 RMS>30bps（880864 等，真 tdx 时代即有毒条 3.9× 量级尖刺）——这些板的"偏差"实为对照物自身坏点，等权侧无辜；<30 成员板另过消费者敏感度。

## 二、重大发现（断链地图——v2 按 secktide 前役修正）

1. **tdx 全族（概念+行业）09-10 死，且死因已破案**：secktide 09-29 取证实锤=服务端对 pytdx 系客户端**协议层拒答 K 线族**（get_index_bars 只回 2 字节 0x0320 声称 800 根零数据体，同机 get_security_count 正常）——非网络、非本仓代码回归。v1 的"行业腿 09-10 死、概念腿撑到 09-30"归因有误：09-11 起 1m 数据全部是方案 J 合成腿（synth_eq），09-23 起人工腿断供、secktide 回补 23/24/28 并挂每日 15:50 计划任务 sector_board_synth_eod。
2. **重采样族（5/15/30/60m）09-10 停产至今**（J 腿只产 1m）；日K 族 kline_sector_880 健康一路到 09-30。
3. **码制暗伤**：行业板存裸码（`880301`）、概念板存后缀码（`880201.SH`）；J 腿沿用"行业板无成分映射"的旧认知（09-30 起已失效，见 §二.5），其登记未决缺口"132 行业板不可合成"实已可解。
4. **tdx 存量数据有毒（真值时代也有）**：行业板 880400/880403（09-09 各 29 根 3.9× 尖刺）+ 概念板批C 尾巴 ~8% 板（880864 等，最大 -2370%）——`data_source='tdx'` 的存量行整体不可尽信，切源必要性再加一等。
5. **行业板 09-30 起入 sector_constituent**（valid_from=2026-09-30，3616 行，L03-C01 扩面；tasks.yaml"该族不在册"注释过时）→ J 腿的未决缺口（行业板合成）现在有原料了。
6. **集合竞价缺口**：J 与本任务都只覆盖连续竞价分钟（kline_1min 无 09:25 集合竞价独条），竞价腿归 T2/auction 通道，非本件范围。

## 三、给白班施工班的设计输入（a6 §F+ 工单增补）

- 本任务施工件**已建**：`scripts/data/kline_sector_intraday_from_constituents.py`（等权链式五周期，纯函数核 6 测全绿，0929 实数据 pilot 通过）；**调度注册冻结**——不与在排班的 sector_board_synth_eod 双跑双真源，冻结解除=§六收敛裁定落地；
- 覆盖全 727 板（成员 SCD-2 PIT）；统一后缀码写入（存量裸码行迁移/双读由施工班定）；
- 切换日基点重置，不拼 tdx 历史（若下游依赖绝对点位连续性，见 §六方案甲的链式语义移植选项）；§一.3 尾巴板优先过敏感度清单；
- 重采样链（5/15/30/60m）本任务已直接产出，resample 任务可退役或仅作交叉复核；
- 验收链按工单：本件（校验批）→收敛裁定→切源→连续 3 交易日自动产出→逆势榜消费无感→tdx 四任务+J 腿（若裁退）退役留观。

## 四、同场附带发现（非 T3 范围，移交白班/Owner）

1. **26 封本地 replay 信件卡死**（实点=2026-09-30 深夜，`data/local_fallback/` 共 26 个 .tsv / 1.2G；处置日志 `.runtime/tmp/disk_audit_20260927/replay_triage.log` 尾行 RESULT replayed=0/failed=26/remaining=26）：tick_data/tick_depth_5/convertible_bond_list 三表=TSV 空字节损坏（HTTP 400）；index_list/etf_list=NULL list_date 撞非空列（HTTP 500，疑 09-10 index_list 切 tushare 后 schema 后遗症，对照 f09a0e8937b 批注）；另有 market_cffex_member_ranking（09-30 18:06）/news_data（04:09）等表各若干封。其中 09:35:57/58 两封 tick_data 可能含 CH 从未收到的 09:30-09:45 实盘行，值得抢救性 triage（09:30-10:00 桶现 419 万行，缺格面待量化）。
2. **tick T1 终态（本夜闭合）**：09-30 09:45-13:00 死机缺口，前会话 13:11-23:04 经 miniqmt 已回灌 1240 万行；本夜 23:17 探货证实数据中心 T+1 放货（000001.SZ 0945-1100 段 1500 行满额）。剩余 73 只"下午活/上午哑"标的经源端逐一实证**全部为 lastPrice=0 空报价帧（上午无成交）**，与直播加载不变量（lastPrice>0）口径一致——非真缺口，仅 161019 补入 2 行真值。automation-5f024c30（10-01 09:25 一次性）保留作独立复核网，幂等无害。
3. 前会话台账（cleanup_ledger_20260928.txt，24h TTL）关键结论已核对无新增债务；其"8 符号 1.1 万碎片"口径与本次"73 只上午哑（无一有上午成交）"为同一尾仓的不同时点快照，以本件 §四.2 终态为准。

## 五、死信抢救战果（2026-10-01 凌晨追加，st-storageswap-20260930）

26 封 fallback 死信处置终态（抢救脚本=.runtime/tmp/salvage_fallback_20261001.py，24h TTL，方法与对账数全录）：

| 表 | 处置 | 结果 |
|---|---|---|
| market_cffex_member_ranking ×8 | 派生 variety 补列插 | **恢复 0921-0930 全部交易日**（表原冻结于 09-18；0925=中秋节休市本就无数据，初判"缺 0925"有误已更正——对照 68fe30bd5f 休市改判）；多合约行与品种级 symbol 键合并收敛=健康期同款 8×21 形态 |
| index_list ×1 | 显式 valid_from | +8,000 行解冻（原冻结 09-10） |
| etf_list ×1 | 同上（63 行未上市 ETF list_date=NULL） | +2,193 行 |
| dividend ×2 | 逐行日期校验 | +68,496 行精确对账；原 .tsv 全文备份为同名 .bad 留证（数据第一公理第二副本） |
| kline_daily_hfq ×1 | 砍 2 个 MATERIALIZED 字段 | +2,850 行 |
| convertible_bond_list ×1 | 剥尾部空字段+显式 valid_from | +1,059 行精确对账 |
| news_data ×8 | 复用 news_dedup.NEWS_DATA_COLUMNS 列清单 | 1,188 行零坏行 |
| tick_data ×2 + tick_depth_5 ×1 | OD 实证 100% 空字节（崩溃未落盘） | 隔离 `_quarantine_20261001/`+README 留证；损失面=09:35:57-58 两个写入周期缓冲行 |
| technical_indicator ×1 | **不抢救改重算** | 36 万行是派生数据（契约 §2A 原则4 可由 kline_1min 确定性重算）；白班直接重跑 TI compute 任务更干净 |

**新发现的停摆事故（白班必办）**：technical_indicator 分钟级 1min/5min 停产自 **09-21**、15min/30min 自 09-23（daily 正常 09-30）——不只是这一封死信，后续夜批根本没跑，需重跑 compute 补窗。cffex 写端 09-21 回归（列清单漂移+多合约行共享品种级键）同日窗，两事故疑似同因，建议并案排查。

**死信面终态**：manifest 剩 1 条（TI，留档待白班重算后销）；抢救全程走 ch_writer.write_tsv 通道，逐表前后计数精确对账。

## 六、收敛裁定（本任务 vs 方案 J 合成腿——留白班/Owner 裁，本夜不独断）

**发现**：st-c9-secktide 09-29 治愈役已为同一断供给过方案 J 通道（`scripts/data/synth_board_minute.py` beta + 计划任务 sector_board_synth_eod 每日 15:50 + known_data_gaps `kline_sector_intraday_tdx_dead` 在案）。两件同真源家族（成员聚合等权主口径），按内收铁律 w5_1 必并。

| 维度 | 方案 J（secktide） | 本任务（st-storageswap-20260930） |
|---|---|---|
| 口径 | 等权主 + circ_mv 加权备选（后者被 -0.62 证伪） | 等权单口径（a7 批C vs 真 tdx RMS 中位 1.4bps） |
| 跨日语义 | **跨日链式**（prev_close 基，点位连续） | 逐日重置基点（禁拼历史） |
| 周期 | 1m | 1m+5/15/30/60m |
| 覆盖 | 580 概念板 | 727 板（**含行业板=J 的登记未决缺口**） |
| 幂等 | delete_where synth_* 再写（tdx 行保护） | ReplacingMergeTree 同键重写 |
| 测试 | --calibrate 对拍 | pytest 6/6 + 批A/B/C 三批背书 |
| 排班 | **已挂 15:50 计划任务（活）** | 无（冻结中） |

**收敛建议（供裁）**：方案甲=本任务为收敛终点（吃下行业板缺口+五周期），J 计划任务退役留观，J 的 synth_eq 历史行保留原 data_source 可溯；**风险=J 的跨日链式点位连续性本任务没有**，若逆势榜等下游依赖绝对点位水平（非仅收益），甲案需移植链式语义或接受基点跳变。方案乙=以 J 腿为基座，移植本件的行业板（成员册 09-30 起有料）+五周期桶聚合+测试。裁定要素=下游点位敏感度普查（逆势榜 MOD-SIG-071 首查）。**裁定前维持现状：J 腿独跑，本任务不注册不排班。**

（本件完）

**【裁定落地 2026-10-01 05:3x，总包依 Owner 授权自裁】**：采**方案甲-强化版**。裁定依据（M1 挖矿 A_mine.md）：①下游两处 SQL 消费（counter_trend_board L75-80 / index_contribution_decomposer L70-76）均为单日读取纯分钟收益口径，**绝对点位与跨日连续性零依赖**——甲案最大风险不存在；②J 的跨日链式强依赖 t-1 日K 管线@15:50，已三断（09-14 孤日/09-23 人工断/09-30 排班 0 行）=脆弱源；③本件批C vs 真 tdx RMS 中位 1.4bps+五周期+727 板 PIT。施工：本件吸收 J 双保险（tdx 真值保护实测 R2 PASS+回补清场 delete_where 非 tdx 旧行）；已注册 intraday_sector 组（tasks.yaml+cycle map）；J 计划任务遵 S12 不注销，runner 转 --dry-run 留观（ASCII 红线复核 0 非法字节）；tdx 五任务在 tasks.yaml 标注退役留观；resample 判死（kline_sector_880 全表仅 1d，异表永不可见）随 Owner 门位批退役。**连续 3 交易日验收自下一交易日（10-09）自动起算。**
