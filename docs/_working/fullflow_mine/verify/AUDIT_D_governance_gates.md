---
ttl: task_bound
title: "治理项与门位包两日后复核"
owner: st-datasop-20260930
language: zh
status: active
version: "1.0.0"
date: 2026-10-04
---

# 治理项与门位包两日后复核（AUDIT-D，2026-10-04）

> 只读复核：基线=00_ORCHESTRATION §六批(6-1~6-7)+§第〇批(0-1~0-8)，取证日 2026-10-04；CH 全程 zephyr_reader 只读，governance.db 以 `file:...?mode=ro` 打开；未改任何既有文件、零 git 写。

## 一、治理 7 项逐项判定

| # | 项 | 现状实测（2026-10-04） | 判定 |
|---|----|------------------------|------|
| 6-1 | 指标册三层口径 143/102/41 | 册实测 143 条且 `entry_count: 143`（v1.6.1，tilib-b10 批 138→141→143 自洽）；ROOR `entry_count: 102`+description"102 条"未跟随，REG-TECHNICAL-INDICATOR-001 漂移仍在；"41"已注记为 2026-08-14 历史快照（第三层口径已消） | **仍需**（部分改善：41 层已消；143 vs 102 reconciler 专项未动，且增量口径随批继续漂） |
| 6-2 | census/wiring_registry 增 state=armed | wiring_registry 消费岛 20 条仍 `wiring_status: unwired`；census ledger（updated 2026-10-01）状态集仍 active/zero/retired（329/460/8），全仓 grep 无 armed 落地；提案仅存 L10b Q6+总包清单 | **仍需**（提案未实现） |
| 6-3 | costs 表野生 DDL | costs 表在 governance.db 仍 0 行；全仓 grep `CREATE TABLE costs/INSERT INTO costs/FROM costs` 零命中，sqlite_schema.py 无定义——建表来源仍不明 | **仍需**（净删归 0-2 Owner 门位） |
| 6-4 | 双胞胎收敛 task_events vs events；audit_trail vs audit-trail | 物理仍在：governance.db `task_events`(0 行) 与 `events`(3125 行) 并存；data/audit_trail(191M) 与 data/audit-trail(12K) 并存。写侧已收敛：`shared/io/paths.py` AUDIT_DATA_DIR 真源=data/audit_trail，gov_audit 两 bridge 已注记 AI-AUDIT12 弃裸连字符路径，连字符目录 last write=07-21 成化石 | **仍需**（半修：写侧 SSoT 已达成可降紧急度；物理双目录/双表净删未做） |
| 6-5 | api_server 只读引用 5 张退役候选表 | api_server.py 仍引用：edb_data(L1577)/ipo_schedule(L1581)/margin_target_adjustment(L1584)/msci_adjustment(L1586)/stock_valuation(L1589) 显示名映射+L2021-2029 事件频率分类；5 表未退役、端点未切换 | **仍需**（与退役批互为前置，顺序不变） |
| 6-6 | 战役册 frontmatter topic 与目录名一致性 | fullflow_mine 战役 33 件 topic 全为 `fullflow_mine_20261001`，实际目录=`docs/_working/fullflow_mine`（无日期后缀）；W4/V1 两件无 topic 字段另计。W3 曾载 R5-DIGIT-SUFFIX 拦截史（目录原名带后缀后改名） | **仍需**（失配全量未动） |
| 6-7 | capability 册旧路径 token 失配清查 | capability_canonical_file_registry.yaml 31 处引用全为 `fullflow_mine/` 正路径、0 处旧 token；data/capability_cards/ 0 命中；pickaxe 证实 capability 卡从未携带旧 token（6eb3ab18 曾还原投影册私改） | **已修**（登记面干净，可销项；残留仅在 6-6 的 topic 字段，归 6-6 处置） |

小结：已修 1（6-7）、仍需 6（6-1~6-6，其中 6-4 半修降紧急度）。

## 二、门位 8 项证据复核表（呈批包两日后）

| # | 项 | 基线（10-01） | 现状（10-04 实测） | 成立? |
|---|----|--------------|--------------------|-------|
| 0-1 | CH 备份/隔离表 9 张+_tmp_mat_test | 9 张+4 视图+_tmp_mat_test，DDL 导出 G:/zephyr_cold/retire_c267_20260930 | 8 张仍在且行数逐张一致（daily_hfq_legacy 8,426,036/preversion 10,079,242/quarantine 10,475/recalc 100,054/monthly_legacy 502,496/monthly_r1 524,474/weekly_legacy 2,127,400/weekly_r1 1,856,391）；**index_valuation_daily_quar_20260920 已 ABSENT**；_tmp_mat_test 仍在（0 行）；4 视图仍在；DDL 导出目录在（4 子目录+live_ddl_export_20260930.sql 等 5 件）；c1_market 204→202 表（另 -1 未归属净变化） | **成立，数字更新 9→8** |
| 0-2 | 治理空表 3+空目录 3 | audit_trail/costs/report_archive 0 行；fills/gate_cache/scans 空 | 三表仍 0 行（governance.db 现 46 表）；三目录仍 0 文件 | **成立** |
| 0-3 | 候退役指标 25+因子 8 名单 | L12 §C：IND 17+FCT 8，只登记不执行 | 17/17 indicator + 8/8 factor 逐条在册（factor_registry 现 175 条）；wiring_registry consumption_islands 仍 20 条；census ledger islands=460（zero 口径，active 329/retired 8） | **成立，名单零变化，净删未执行** |
| 0-4 | hk_kline 被覆盖 | kline_hk_daily 覆盖 hk_kline | hk_kline 6,107 行 max trade_date=09-15、max ingest_ts=09-16 01:03 UTC（**已停写 18 天**）；kline_hk_daily 216,584 行 max=09-30；tasks.yaml 仍挂 hk_kline_incremental(intraday)+hk_kline_full_refresh(weekend) 双写任务 | **成立且增强**（停写降低退役风险） |
| 0-5 | 策略 6 卡挂载与三证 | E-TIMING-001 verified 三证齐全排第一；9 处挂点 | 卡状态未变（E-TIMING-001/MF-098/099=active，VREV-001/MOMTREND-002/019=candidate）；TDM 9 处挂点全在（E-L1×3/E-L3/X-FLOW/F-FLOW×2/P-FLOW×2，语义 verified/proposed 同基线）；sim_trade_log 77 行 max=10-03 在考（基线 17 笔持续累积）；总挂载 37+9→50 | **成立**（附注：新增 verified 卡 VREV-025/026/027/MOMTREND-033/DABAN-023/TSMALL-001/VAL-001，名单可扩容） |
| 0-6 | alt_sz 两巨表 | reservoir_level 7,546 万行→日聚合；house_listing 归档 | alt_sz_reservoir_level=75,264,932 行 max tdate=07-31（源停 07 月未变）；alt_sz_house_listing=2,434,879 行 max publish_date=07-07 | **成立**（量级与停更状态不变） |
| 0-7 | JOB-028~038 幽灵引用 11 处 | 11 处 active job→candidate DS | 逐 job 实测 JOB-028~038 全 status=active，outputs 逐一引用 DS-029→DS-039，11/11 纹丝未动；11 张 DS 全 candidate+degradation_note | **成立** |
| 0-8 | hl_* 4 表 defer 扩面 | 4 表在，Owner 09-30 口谕 defer | 4 表全在且鲜活：hl_funding_history 4,738,843 行 max funding_time=10-03；hl_liquidation_raw 13 行 max=10-03 01:11；hl_oi_snapshot_daily 3,276/hl_perp_snapshot_daily 3,276 max=10-03 | **成立**（仍在活流，defer 未解禁，不动） |

## 三、呈批包更新建议

1. **0-1 更新后保留呈批**：净删清单 9→8 张（index_valuation_daily_quar_20260920 已不在库，建议先追认删除主体与 G:/backup 覆盖再销该项）；_tmp_mat_test+8 张+4 视图照旧呈批。
2. **0-4 证据增强可优先批**：hk_kline 自 09-16 停写且被 kline_hk_daily 完整覆盖，双写任务仍在册，批准退役同时应摘 tasks.yaml 两任务。
3. **0-5 保留并附注扩容选项**：6 卡证据原样成立；4~7 张新 verified 卡（4-1 考试产出）如需同窗转正审批，建议 Owner 裁定并入或另批。
4. **0-2/0-3/0-6/0-7/0-8 原样保留呈批**：证据全部复核成立，无变化。
5. **治理侧销 1 留 6**：6-7 销项；6-4 降紧急度（写侧已 SSoT）；6-1/6-2/6-3/6-5/6-6 维持原排期。
