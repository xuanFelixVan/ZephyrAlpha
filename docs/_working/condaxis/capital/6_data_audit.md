---
ttl: task_bound
title: 数据面审计——逐源表名/主源/fallback/行数实查/PIT 滞后/披露制度漂移风险（含北向案例监测方案/tick 半断供/L2 可得性）
created: '2026-10-13'
session: st-condaxis-20261013
status: mining_workbook
family_id: CONDAXIS-CAMPAIGN
completes_when: 数据审计上报项处置完成且随 CONDAXIS-CAMPAIGN 归档
---

# 数据面审计（6_data_audit）

> 审计基准时点：2026-10-13 20:00-20:30，CH 只读实查（`SELECT min/max(trade_date),count()` 逐表＋分日分布＋DESCRIBE，命令留痕于各表格）。**本册发现四处供给缺口/险情**（§2），全部只上报不擅修（写车道纪律）。
> 逐源的 PIT 滞后与画像层台账在 3_C_actor_profile §1.2/§3.2，本册不重复——本册管**供给面本身**（行数/断供/制度漂移/可得性）。

## §1 逐源审计总表（2026-10-13 实查）

| 源 | 物理表 | 主源→fallback（tasks.yaml 证据） | 行数/覆盖窗（实查） | 新鲜度判定 | 披露制度漂移风险 |
|---|---|---|---|---|---|
| 大单五档（个股） | c1_market.money_flow | tushare pro.moneyflow 主源（5540 行/日级）→akshare fallback（tasks.yaml:182-195） | 6,021,194 行；2021-01-04..2026-10-13；uniqExact≈5,573/日；data_source 全表='tushare' | ✅ 当日全量（10-13=5,574 行 20:00 已到位） | **口径分裂高危族**（东财/同花顺/万得互不一致——研究册 §5）：换 fallback 即换因子，data_source 列钉死是唯一防线（§3.1 坑 2） |
| 大盘资金流 | c1_market.market_fund_flow_daily | akshare stock_market_fund_flow 唯一源，fallback 显式置空（tasks.yaml:3687-3699） | 233 行；2026-03-27..2026-10-13 | ✅ 当日 | 源端固定 ~120 交易日窗（窗外不可回补）——短窗件固有属性非漂移 |
| 板块资金流（盘中） | c1_market.sector_fund_flow | 桥源（在册） | 12,110 行；2026-09-15..2026-10-13 | ✅ 当日 | 低（新表） |
| 两融 | c1_market.margin_trading | akshare stock_margin_detail_sse/szse 合并（akshare_provider.py:1941 `_fetch_margin_trading`） | 2,104,817 行；2024-09-02..2026-10-09；日均 ~4,108 标的 | ⚠️ **10-12 缺**（截 10-13 20:00，滞后 1 交易日，§2-4 上报） | 低（交易所晨披制度稳定）；历史仅自 2024-09（建表窗） |
| 大宗交易 | c1_market.block_trade | akshare stock_dzjy_mrmx（tasks.yaml:119-128）；detail 伴表在册 | 1,697 行；**2026-08-07 起**（~2 个月） | ✅ 当日（49 行） | 低；**短史**是主约束（事件研究窗不足，3_C §1.2-C3） |
| 龙虎榜主表 | c1_market.dragon_tiger | akshare stock_lhb_detail_em（tasks.yaml:130-140） | 2,664 行；**2026-08-07 起**；日均 ~60-70 家 | ✅ 当日（62 行） | 低；同短史问题 |
| 龙虎席位明细 | c1_market.dragon_tiger_seat | akshare stock_lhb_stock_detail_em Top5 合并去重（tasks.yaml:142-153） | 622,847 行；2022-01-04..2026-10-13 | ✅ 当日 | 低；**与主表历史不对称（4.7 年 vs 2 个月）**——跨表 JOIN 事件研究只能用 2026-08 后窗 |
| 股东户数 | c3_fundamental.shareholder_count | akshare 东财 datacenter RPT_HOLDERNUM_DET 唯一免费口径（tasks.yaml:601-615；tushare 需 2000 分权限未开通） | 515,473 行；announce_date 1993-01-12..2026-10-13 | ✅ 当日 ingest（10:04） | **公告制不定时**＋断供前科（2026-07 断两月→supply_sentinel 诞生 yaml:11-12）——已在哨兵监控面 |
| 北向（季） | c1_market.northbound_hold_snapshot | tushare hk_hold 季度全量，无 fallback（预案交易所直抓未施工 tasks.yaml:2218） | 35,256 行；2024-09-30..2026-06-30 共 8 季 | ✅ 季频（下季 2026-09-30 数据 PIT 守卫最早 10-20 采） | **制度漂移现成案例**（§3.2）；2026-06-30 行数 8,747≈倍常值疑双版本重拉（ReplacingMergeTree 收敛中，消费 FINAL） |
| 北向（日频，已死） | c1_market.hk_connect_flow | —（任务 disabled 2026-09-16 裁定#257，tasks.yaml:197-208） | 4,052 行；2014-11-17..**2024-08-16 冻结** | 🌑 死表（lifecycle=permanent 保留） | 已发生的漂移终局样本（§3.2 案例库本体） |
| ETF 份额快照 | c1_market.market_etf_share_snapshot | akshare fund_etf_spot_em 唯一源（tasks.yaml:3701-3713） | **仅 2 个交易日有数**：2026-09-18（1,621）/2026-10-13（1,643） | 🔴 **供给缺口**（daily_capital 排程下 16 个交易日缺失，§2-1 上报） | 低（东财快照口径稳定）；积累制刚起步 |
| ETF 净值/清单 | c1_market.etf_nav / etf_list | tushare fund_nav 主源（akshare 源退化弃用 tasks.yaml:1921-1935）/tushare fund_basic(market=E)（tasks.yaml:2232-2238） | 100,428 行 2021-07-29..2026-10-12／4,388 行 | ✅ T+1 | 低 |
| 解禁 | c3_fundamental.share_unlock | 东财 stock_restricted_release_detail_em 唯一免费口径，fallback 显式置空（tasks.yaml:568-599） | 30,357 行；unlock_date 2010-01-04..2027-10-13（前瞻+1 年） | ✅（weekend_calibration 排程） | 低 |
| 日 K 线 | c1_market.kline_daily | 多源（tushare/baostock/BJ，hfq 伴表） | 11,691,370 行；1990-12-19..2026-10-13 | ✅ 当日 | 低（量纲已治本 2026-09-22） |
| 指标宽表 | c1_market.technical_indicator | internal_compute（chips/volume 落表） | period='daily'：2019-01-02..2026-10-12、~1,975 万行；chips_winner 日均 ~5.5k 标的非空 | ✅ T+0 晚（10-12 已算，10-13 盘后批待跑） | **count() 虚高坑**（ReplacingMergeTree 未合并版本 2-3 倍，§3.1 坑 1） |
| tick 三秒快照 | c1_market.tick_data | miniQMT 清退后**无在跑供给通道**（qmt_bridge no-op，data_supply_sentinel.yaml:633-634） | 39.5 亿行；2026-01-05..**2026-10-09** | 🔴 **半断供**（sentinel 案情在册；处置二选一挂 Owner 裁定：模拟盘 T+1 回补或 accepted gap） | — |
| tick 五档深度 | c1_market.tick_depth_5 | qmt_bridge 桥流实时 | 1.30 亿行；2026-07-24..**2026-09-30**；**09-29 仅 1 行** | 🔴 **新发现断链**（§2-2 上报）：停在 09-30，竞价派生链（ch_auction_derive，tasks.yaml:1845/1857）随之断供 |
| L2 逐笔 | c1_market.l2_tick | l2_tick_snapshot **退役冻结 2026-09-18**（miniQMT 退役，桥无 L2 通道，需 L2 权限，tasks.yaml:1818-1831） | 表在册（退役态） | 🌑 无通道 | **重定标路线（C1 五档升级）的唯一解锁件**（P1 呈批 10.4） |

## §2 供给缺口/险情上报（四项，只上报不擅修）

1. **ETF 份额快照日常化缺失**（最重）：排程 daily_capital 与实况（仅 09-18、10-13 两日）不符——"任务存在≠管线活着"第三例（前两例=股东户数断供、tick 半断供）。处置建议：查 daily_capital 调度组近 16 交易日该任务执行日志定位失联原因（车道权限外，移交数据运维）；修复前 ETF 申赎差分（C6）维持挂起（3_C §4 一致）。
2. **tick_depth_5 桥流断链**：max=2026-09-30 且 09-29 仅 1 行（写入半截实证）；级联=竞价快照两表（tasks.yaml:1845/1857 派生源）与 MOD-SIG-089 竞价分析全部 blocked_on_data。处置建议：与 tick_data 处置（sentinel 案情）合并 Owner 裁定。
3. **两融 10-12 缺日**：截至 10-13 20:00 margin_trading 无 10-12 行（10-12 为交易日；两融披露 T+1 晨，10-13 晨应可采）。处置建议：查当日调度日志；若连续缺日升级为 sentinel 告警。
4. **block_trade/dragon_tiger 主表短史**：均自 2026-08-07 起——事件研究/考试卡窗口设计必须按 2 个月窗声明（禁拿席位表 4.7 年史冒充主表史）。

## §3 专项审计

### §3.1 CH 消费通用坑（本车道实查沉淀，A/C 环节施工必读）

1. **ReplacingMergeTree count() 虚高**：money_flow 10-09 count()=16,719 vs uniqExact(symbol)=5,573（≈3 倍）；technical_indicator daily 行 15,885/5,562（≈2.86 倍）——一切行数断言/考试卡 evidence/信号聚合必须 `FINAL` 或 `uniqExact`/`argMax(ingest_ts)`（card_binding 头注 anyLast 纪律同源）。
2. **data_source 钉死**：money_flow 全表单值 'tushare'（fallback 从未启用）——一旦启用东财 fallback=换因子（口径分裂，研究册 §8.4），消费端必须随行携带 data_source 入证据链。
3. **period 列值**：technical_indicator period='daily'（非 '1day'），9 种 period 值混存，漏 WHERE 即污染。
4. **大宗折价率不是表列**：block_trade 无折价率列——折价=JOIN kline_daily 现算（cohort_daily_ledger.py:34-35 口径真源），直查表列必 404（本车道实测）。

### §3.2 披露制度漂移监测方案（北向已死案例的监测设计——候选件，判据零冻结）

**案例复盘（hk_connect_flow 之死）**：2024-04-12 港交所通告→2024-05-13 盘中实时披露停→表止于 2024-08-16（CH 实证）→任务空跑近两年至 2026-09-16 裁定#257 disabled。**病灶**：supply_sentinel 管"断供"（max(date) 停更），不管"制度变更"（源端语义变了但仍在供数/供数变稀）——北向日频死因是披露制度，非技术断供，哨兵无面。

**监测方案候选（供 P1 呈批，非施工）**：
- **甲 行数画像带**（可全自动，推荐优先）：对披露制敏感表（北向季/股东户数/两融/龙虎/大宗）建"预期披露日历×实际行数分位带"（如北向季表：预期=季度末+20 自然日后必有新季度行；两融：交易日必有 ~4.1k 行/日）——偏离带=告警。数据全在 CH，纯 sentinel 配置扩展（data_supply_sentinel.yaml 已有表侧 min_rows_in_window 机制可挂），**零新系统**。
- **乙 源端公告监测**（半自动）：交易所/港交所公告页 watch——需外网爬虫面，💰/治理成本高，仅对甲不可覆盖源考虑（如披露频率变更公告先于行数变化）。
- **丙 文档级登记**（零成本兜底）：本册 §1 表"漂移风险"列即纸面登记起点，每季度合并审计窗（宪法 §4.2）复核一次。
- 北向专用预警点：若 2026-10-20（PIT 守卫放行日）后 northbound_hold_snapshot 仍无 2026-09-30 季度行→制度再漂移红色信号（季频披露也变了）。

### §3.3 L2 逐笔委托可得性审计（P1 呈批 10.4 的矿料）

- **仓内现状**：唯一在册 L2 任务 l2_tick_snapshot（c1_market.l2_tick，miniQMT get_l2_quote）2026-09-18 随 miniQMT 清退**退役冻结**（tasks.yaml:1818-1831）；qmt_bridge 无 L2 通道；tick_data 3 秒快照主表半断供（§1）。
- **结论**：逐笔委托（订单流）与逐笔成交在当前形态均 🌑 不可得；"大单五档重定标"（开源金工路线，研究册 §5）blocked_on 此项。
- **候选通道三档**（供呈批，非本册裁定）：①模拟盘 T+1 回补（p0_sim_as_source_assessment 已实证通道、Owner 挂账中——data_supply_sentinel.yaml:635-637 案情内提及）；②商务 L2 源 💰（迅投/掘金等，a_stock_level2_data 目录线索=研究册 §6 ⭕）；③维持五档弱证据档（3_C §4 挂起项）。

## §4 自审闸三态裁定

| 件 | 裁定 | 理由 |
|---|---|---|
| 四处缺口上报（§2） | **施工（上报即产物）** | 险情在场每多一天=决策面带病运行；上报零成本高价值 |
| §3.2-甲 行数画像带监测 | **施工（候选设计→呈批）** | 纯 sentinel 配置扩展零新系统；北向案=已付学费，监测带=学费的复利；终局全自动化当然有位 |
| §3.2-乙 源端公告爬虫 | **挂起排期（💰）** | 甲覆盖绝大多数漂移面；乙边际收益低治理成本高，先挂账 |
| L2 采集（三档通道） | **挂起排期（💰）** | P1 呈批 10.4 本项；解锁 C1 重定标升级 |
| ETF 快照修复/桥流恢复 | **挂起排期（非本车道职权）** | 移交数据运维+Owner 裁定；解锁条件落 3_C/2_B 对应挂起项 |

**反驳者一问**（§3.2-甲 加试）：①行数带告警可能噪音大（披露节奏本有抖动）（对策：分位带＋方向性判据——"该有而没有"比"少了"灵敏，北向季表用日历锚非分位）；②监测面扩表=治理成本（对策：只挂披露制敏感五表，宪法 §4.1 净零——扩的是既有 sentinel 配置非新册）；③制度变更先公告后行数（对策：丙 文档登记兜底+季度窗复核）。维持施工。
