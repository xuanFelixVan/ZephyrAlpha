---
ttl: task_bound
title: 环节⓪ 板块口径路由——通达信880/申万/概念三套并存的唯一化方案矿
created: '2026-10-13'
session: st-condaxis-20261013
status: mining_workbook
family_id: CONDAXIS-CAMPAIGN
completes_when: 该环节施工完成且随 CONDAXIS-CAMPAIGN 归档
---

# 环节⓪ 板块口径路由（唯一化方案矿）

> **问题**（研究册 §6.1）：通达信 880 / 申万 / 概念多套并存，880 快照 582、86 板块因子、90 同花顺行业等数字互不一致，需路由规则与唯一主口径，避免复刻 D 族"两宏观轴 21% 分歧"事故（docs/_working/2026-10-12-d-family-qualification-freeze-draft.md §3.3）。
> **实查口径**：本册所有行数/新鲜度=2026-10-13 ClickHouse 只读实查（ch_reader），品类锚=docs/03_modules/_cross_layer/database/business_data_categories.yaml。

## §1 逐项台账表

| 件名 | 仓内真源路径:行号 | 现状标记 | 消费方 | 缺口 | 六向定位 |
|------|------------------|---------|--------|------|---------|
| kline_sector_880（880/881 日线） | c1_market 表；品类锚 business_data_categories.yaml:1101-1105；采集器 src/zephyr/data/sector_kline_downloader.py:7(MATURITY production) | ✅ 766,114 行；729 码=601×880xxx+128×881xxx；max(trade_date)=2026-10-13 当日新鲜 | sector_report_builder/mainline_candidates/sector_state_pipeline/position_sector_context（头注 DEPENDENCIES） | 881 与 880 同表混存无口径列区分 | ①tqcenter 盘后下载 ②五件套全环节 ③1d/1m/5m 三周期 ④ReplacingMergeTree 幂等已落 ⑤IDX-02 待接 ⑥齐且新鲜 |
| sector_snapshot（880 盘中快照） | src/zephyr/data/sector_snapshot_collector.py:7(production)；品类 :1149-1153 | ✅ 127,894 行 | sector_ranking_engine/sector_intraday_aggregator | 列含 trade_date+timestamp（实查 DESCRIBE），无主力净流入字段（aggregator 头注实证：inside/outside 近恒 0-4 不作资金口径） | ①tqcenter 99 推送+30s 轮询 ②盘中聚合 ③混合模式 ④已落 ⑤Dashboard ⑥量价齐资金缺 |
| sector_constituent（880 成分） | 品类 :1133-1137 | ✅ 106,625 行；727 码 | report_builder/mainline/leader/PIT SCD-2 过滤件 | 与 kline 729 码差 2 码（对账行） | ①盘中轮询池派生 ②成分映射 ③- ④已落 ⑤- ⑥齐 |
| sector_meta（同花顺行业 881 主数据） | 品类 :1053-1057 | ✅ 2,970 行；90 码（sector_type='同花顺行业' 全表唯一类型）；max=2026-10-13 | sector_code_bridge 源侧 | 仅 881 行业面，无 880 概念元数据 | ①THS ②code_bridge ③- ④已落 ⑤- ⑥齐 |
| kline_sector（旧板块K线，三源混存） | 品类 :1085-1089 | 🔨 87,439 行=data_source 三源：tqcenter 726 码(2026-06-17~10-13 新鲜)/tdx 593 码(2025-07-18~2026-07-31 已停)/tqcenter_880fix 2 码(2026-09-14/15 一次性) | 历史消费者（resampler 等） | **表内断代**：tdx 腿 2026-07-31 停，长历史只有 2025-07~2026-07 段；路由若不分 source 会拼出假连续序列 | ①双源 ②旧链 ③- ④已落待清洗 ⑤- ⑥历史腿断 |
| kline_sector_intraday（880 盘中） | 品类 :1117-1121 | ✅ 12,091,377 行 | sector_intraday_aggregator(production) | 分钟腿存于本表（880 有分钟），**板块分钟资金流**才是🌑（研究册 §4.4） | ①tqcenter ②盘中聚合 ③- ④已落 ⑤- ⑥量价分钟齐 |
| industry_class（申万 L1/L2/L3） | src/zephyr/data/implementations/tushare_provider.py:340-482（#ARCH-IFIND-FAILOVER，index_classify+index_member） | ✅ 31,414 行；L1/L2/L3 各 ~10,472 股；PIT valid_from/valid_to 列在表 | policy_theme_mapper（受益/受损映射）等 | **申万只有分类映射，无申万板块级行情/资金流表**——申万口径做主口径需补行情聚合层 | ①tushare ②④环节+报告 ③failover 已落 ④已落 ⑤- ⑥分类齐行情缺 |
| concept_board / concept_board_constituent / concept_sector（概念） | src/zephyr/data/implementations/akshare_provider.py:125-126/:5694-5698（stock_board_concept_name_ths + cons_em 双源 fallback _fetch_concept_cons_via_ths） | ✅ 376 板块/35,512 成分行/375 行；max(updated_at)=2026-10-13 10:08 当日 | concept_factor_mapper(design)、GAP-F-16 | 概念名→链/行业无路由；THS/EM 双源成分可能漂移（双源未对账） | ①akshare 双源 ②④/情绪 ③fallback 已落 ④已落 ⑤- ⑥齐 |
| sector_fund_flow（THS 即时资金流） | src/zephyr/data/implementations/sector_fund_flow_collector.py:4/:21-25（可用源=同花顺 ak.stock_fund_flow_industry/concept 实测 3/3） | 🔨 12,110 行**仅 industry 腿**（concept 腿未落库）；min=2026-09-15（29 交易日）×日均~418 快照行 | GAP-F-16 逆势榜资金卡（经 code_bridge） | concept 腿接线缺失；历史仅 1 个月（验证班硬约束）；tasks.yaml 接线待排期（头注 CONSUMERS） | ①THS 即时 ②②③环节资金腿 ③快照式 ④已落半 ⑤- ⑥行业面在概念面缺 |
| sector_code_bridge（THS881↔TDX880 映射） | src/zephyr/data/implementations/sector_code_bridge.py:7-10（90/90 全映射零缺失，纯函数） | ✅ testing 落码+单测 | counter_trend_board fund_flow 注入位 | 映射 SSoT=模块内常量（90 行），申万/概念不在桥上 | ①- ②资金流跨口径 ③SUM 多881 ④已落 ⑤- ⑥90 行业闭合 |
| stock_concept（PG 概念持仓） | scripts/industry_graph/apply_industry_graph_ddl.py:370-385 | ✅ 61,053 行（PG 实查） | 链图谱域 | 与 CH concept_board 两库并存（第 4 套概念真源），未对账 | ①ths_export ②图谱域 ③- ④已落 ⑤chainmap ⑥在 |
| 口径路由规则本体 | 无（grep "口径路由/universe" 零命中，⬜ 复认） | ⬜ 不存在 | 五件套全环节 | **本环节施工对象**：唯一主口径声明+降级序+跨口径映射桥 | ①-②-③-④⬜⑤-⑥- |
| 板块分钟资金流 | sector_fund_flow_collector.py:21-26 实测留痕：东财分钟端点 rc=102 空返+push2 持续断连 | 🌑 个人/当前形态不可得（外购=💰） | ③ 出场盘中腿 | 研究册 §6.3 呈 Owner | ①-②③③-④⬜⑤-⑥🌑 |

**数字互不一致实锤**（同日快照面）：880 族 729 码（kline）/727 码（constituent）/582 只盘中轮询（snapshot_collector 头注 2026-07-22 实测 454×880+128×881）/"86 板块因子"（研究册 §4.4 sector_factor_manager 面）/90 THS 行业（sector_meta）/376 概念（concept_board）——**六套数字六个口径源**，无一处声明谁是主口径。

## §2 与既有资产边界（复用/换参/新建三分）

- **复用**：全部 13 张既有表+3 采集器原样复用，零新建数据表；品类真源（business_data_categories.yaml）与 TableRegistry.table() 派生纪律（裁定 #ARCH-CH-024）不动。
- **换参**：kline_sector 三源混存表=消费端查询需强制 data_source 过滤（换查询不换表）；sector_fund_flow 的 concept 腿=采集器既有 sector_type 参数已支持，接 tasks.yaml 任务即可（换接线不换码）。
- **新建**：仅一件——**口径路由规则册**（声明态规则数据，按 RULE-SSOT 应落 YAML 同步；建议最小形态：主口径=880xxx（TDM 产线与五件套全链已挂）、行业语义轴=申万 L1/L2（industry_class PIT）、资金流跨口径=THS881 经 code_bridge、概念=辅口径（④传导与题材语境）、降级序=880→申万→THS90）。禁建第 5 套板块表。

## §3 施工要点（实读代码得出的坑）

1. **881 与 880 在 kline_sector_880 同表无类型列**：sector_meta 的 sector_type 只有'同花顺行业'（90 码）——881 的语义区分目前只能靠 sector_meta join 或 sector_code_bridge 常量，路由册须显式给判别式（如前缀 880/881 粗分+bridge 细分）。
2. **kline_sector 断代坑**：tdx 腿 2025-07-18~2026-07-31、tqcenter 腿 2026-06-17 起——重叠期 2026-06-17~07-31 两源并存，长回测拼接须按 source 段切，禁直接 UNION（重叠期双计）。
3. **582 与 729 之差是设计内**：snapshot_collector 轮询池=454×880+128×881（头注实测 2026-07-22），非全集；盘中面天然小于日全面——路由册要写明"盘中面=轮询池子集"防误判断供。
4. **market 统计指数 880001-880009 已被 aggregator 剔除**（intraday_aggregator 头注）——路由册沿用该剔除规则防双计大盘。
5. **concept 双源漂移**：akshare_provider 概念成分走 EM 主源+THS fallback（:5614/:5637），两源成分集不同——路由册给概念口径标"源版本敏感"，对账脚本属班外。
6. **表名禁硬编码**：一律 TableRegistry.table(category_id)（table_registry.py 头注 #ARCH-CH-024），路由册中的表名全部用品类 id 书写。

## §4 自审闸三态裁定（mining_sop §6）

**裁定：施工**（先行件）——理由：口径唯一化是①-⑤全部环节的前置（D 族 21% 分歧事故的板块版预防），消灭"每个新模块自选一套板块"的人工对账环节，终局全貌（100% AI 自制）必有一张机械可判的板块路由表；施工量极小（一册 YAML+判别式），无过度工程面。反问封矿三理由（终局无路由表/已有表覆盖/成本高）逐一不成立。
