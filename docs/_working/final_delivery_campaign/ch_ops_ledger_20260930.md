---
ttl: task_bound
title: "CH 实弹批六件——VM 离线阻塞移交账"
session: st-finaldel-chief-20260930
---

# CH 实弹批六件——VM 离线阻塞移交账（2026-09-30）

> Owner 已批（裁定#431 内 CH 实弹三件+补数+8 张空壳表 DROP）。执行窗勘验：172.24.30.100 tcp:9000 / http:8123 **双路关闭（VM 未开机）**，本车道零生产写入安全收兵。按 Ollama 先例 AI 不代开机器——**VM 开机后任意班次按下表执行即可，全部材料已备**。

| # | 事项 | 状态 | 材料与移交 |
|---|---|---|---|
| 1 | apply_market_tables_ddl --apply | 待 VM | 三步验证框架在本表；DDL 清单脚本 --dry-run 即得 |
| 2 | intake_ledger_recon rebuild | 待 VM | 处方=F16 卷（fullconnect b 段）；优先新表+对账切换 |
| 3 | #20 realtime 换源（东财→腾讯） | 待 VM | 方案件在 M4 工单 C45 族；旧源配置注释保底可回滚 |
| 4 | gap134 补齐（sector_constituent 880+881 主轴） | 待 VM | 真源裁定=裁定#431+universe_registry v1.2.4（UNI-SECTOR-880-001）；写入前 dump 快照 |
| 5 | C344 补 4 日期（8225 票·日） | 待 VM | known_data_gaps.yaml 在册；治本码件在 .worktrees/st-zmaster2-20260926 |
| 6 | 空壳表 DROP（权威口径 13 张确证 0 行） | 待 VM | 行数/判定 CSV+JSON+l2_tick DDL 导出=G:/zephyr_cold/retire_c267_20260930/shell_tables_c1_market/；移交凭证=同目录 HANDOVER_TO_C_LANE.json（五步清单）；每张三步验证不过即跳 |

执行纪律：逐件三步验证（必要性/真实性/可逆性）留证到本账追加节；写入前快照；验证不过即跳登记。


## §执行回填 2026-09-30 13:xx（CH 实弹车道 st-finaldel-chgo-20260930，裁定#431 全六件照账执行）

前置勘验：Python 3.12.8 PATH 修正在岗；reaper 存活（last_run 2026-09-30 13:17:26，dry_run=False）；CH 172.24.30.100 tcp:9000 OPEN + http:8123 ping=Ok（13:2x 复勘）。会话 tmp=.runtime/tmp/st-finaldel-chgo-20260930/。

### 件1 apply_market_tables_ddl —— 执行（幂等重放，零结构变更）
- 三步验证：必要性=校验 c1_market schema 完整性（脚本无 --dry-run/--apply 参数，默认即 apply+verify，以 --verify+源内 _ALL_DDL 清单代预演）；真实性=DDL 真源 schemas/categories/*.py fail-closed 导入+ch_writer 通道+system.tables 引擎对照探针；可逆性=全 CREATE TABLE IF NOT EXISTS 纯增量，回滚=对新建表 DROP（本轮 0 新建故无需）。
- before/after：c1_market 204 表→204 表（0 新建=全部已在位）；增量迁移探针 93/93 OK；verify 终判 [OK] 全引擎一致。
- 备注：①本车道 --help 误触一轮默认 apply（幂等无害，如实入账）；②41 条 DDL 语句在 CH 26.6.1 服务端解析失败（MATERIALIZED 语法族，预存现象非本轮造成），对应表全部已在位且引擎匹配，无实际缺口。

### 件2 intake_ledger_recon rebuild —— 收口（无需写入）
- 三步验证：必要性=check before 实证原 11 行蒸发已由 09-29 班补回（lane_b csv=15 行，missing_in_csv 仅剩 1）；真实性=CH 残余缺行 CAND-x 经查证为 2026-09-28 探针残留（hypothesis_zh=占位文本/birth_batch=b1/defer_llm_unreachable），rebuild 预演被内容寻址校验拒绝（rebuild_candidates=0，refused=[CAND-x id 与假说原文不符]）；可逆性=未写盘（applied=false，csv 15→15）。
- 回滚方式：无写入无回滚。残余 CAND-x 建议由治理道另案清理 CH 探针行（不在本车道六件范围）。

### 件3 #20 realtime 换源实弹验证 —— 验证通过但发现 -8h 时区缺陷，本批已回滚+移交
- 事实：tasks.yaml 换源已由 99#20 班于 09-29 完成（source=akshare/tencent_qt，东财 TCP RST/新浪 403 退役注记在案）；本车道实弹单次验证：18 批拉取 5,572 行、flush 5572/5572、symbol=ts_code 形状、OHLC+量额健康（11 行停牌 0 值=源端语义）。
- 缺陷（代码级实锤）：akshare_provider.py _fetch_realtime_snapshot 以 now_utc() 直写 DateTime64(3,'Asia/Shanghai') 列→snapshot_time -8h（13:28+08 落库 05:28+08；今晨 01:00:30 批同病=09:00:30+08 所写）。违反 RULE-SCHEMA-TZ。
- 三步验证（回滚件）：必要性=错标批污染盘中快照时间轴（freshness/去重消费者误判）；真实性=5,572 行单值 snapshot_time=05:28:27+08+run 日志 last_key 留证；可逆性=修复后幂等重拉可复原，单键批删精确还原 before 态。
- 回滚执行：ALTER DELETE（mutations_sync=1）删 05:28:27+08/tencent_qt 批，total 11,143→5,571（精确=before）。01:00:30 旧批（他会话件）不碰，缺陷登记移交 zc9-lane-d（工单明示换源域禁代修）；配置回滚=git revert 99#20 tasks.yaml 提交。

### 件4 gap134 sector_constituent 880+881 补齐 —— 执行（132/134 落地，2 码源端真空登记）
- 写入前 dump 快照：before total=96,104、8803=0、8804=0、gap134 覆盖=0（JSON 留证 tmp）。
- 探针翻案：get_stock_list_in_sector 对 .SH 后缀 8803/8804 码实弹回成分（880301→32/880401→149/880801→200），09-15 在册 root_cause（源无此号段）证伪一半——只是 get_sector_list 名单端点不含该段；补齐通道=既有 provider 能力+显式码表（w178 案卷要求的新采集腿，本次以最小面落地）。
- 执行：TQCenterProvider._fetch_sector_constituent（134 码显式传入，行形状/列集与存量 convention 一致）+BufferedWriter 正门；写入 8,475 行，after total=104,579（+8,475 对账精确）；8803=61、8804=71（与 strict 案卷拆解逐一吻合）；抽查 880301.SH=32 只且成员逐一命中探针、880401.SH=149。幂等=ReplacingMergeTree(sector_code,stock_code)。
- 残差：880851.SH/880890.SH 双探针实弹回 0（源端真空），132/134；此 2 码维持 known_data_gaps 在册，独立采集腿另案。
- 回滚方式：ALTER DELETE WHERE sector_code IN (132 码) AND update_date=2026-09-30（精确键），before 快照 JSON 在 tmp。

### 件5 C344/DU-11 daily_valuation 补 4 日期 —— 执行中（后台批，reaper keep 已登记）
- 现状比账本恶化：09-21=5,002/09-22=5,003/09-23=3,557/09-24=3,952（baseline 5,570；账面 8,225 系旧读数），且 09-25 零行、09-28=2,594、09-29=1,000 亦部分写入——**超裁定#431 ⑤ 授权范围（仅 09-21~24），扩大缺口不写、另行登记呈批**。
- 通道=AkshareIngestProvider._fetch_daily_valuation 参数化窗口（start=09-21 end=09-24 incremental=false），HEAD 侧证：resume 预查在非增量路径与治本件同行为（辅助函数 diff=IDENTICAL，仅增量门禁差异）；5 只小样本探针：续跑预查跳 4 只已完成、仅补 000002 全窗 4 行，~5s/只。
- 幂等=ReplacingMergeTree(symbol,trade_date)；完成后 per-day 对账+判据 5,560±5%（17号文§五），不足则同脚本再跑（续跑语义只补缺）。

### 件6 13 张空壳表 DROP —— 全部跳过（0/13），逐张判据留证
- 行数双次活体复验（禁照抄 09-26 读数）：3 张非 0——account_nav_daily=1、etf_benchmark=2,373、realtime_snapshot=5,571 → 跳过。
- 消费者 grep（src/scripts 含 yaml，排除 test）：10 张 0 行表全部 prod_refs>0 → 跳过。edb_data=6（known_data_gaps 在册 gap 替代源）、ipo_schedule=4、l2_tick=6（DDL 真源+known_data_gaps）、margin_target_adjustment=3、market_index_meta=3、msci_adjustment=3、reconciliation_differences=12、stock_candidate_pool=6（活生产者 candidate_pool_snapshot+apply DDL）、stock_valuation=3（frontend/api_server 活消费）、index_valuation_daily_v2=1（wave3 recheck 探针自身）。
- 归档补全（HANDOVER 五步之 2 已完成）：13/13 张 SHOW CREATE 活体导出=G:/zephyr_cold/retire_c267_20260930/shell_tables_c1_market/live_ddl_export_20260930.sql（stock_valuation 经 create_table_query 列补齐）。
- 结论：G 盘 09-26 vacuum 口径已过期（3 张复活），其余 10 张仍被活代码引用——按逐张三步验证不过即跳纪律，全部跳过并登记；DROP 择期另案（须先收代码引用面+已知 gap 翻案）。

### 件5 续跑记录（14:37 总筹接手，后台恢复）
- 勘验：chgo 车道超时后 fill 进程死亡（日志 14:34 冻结）；进程检查=0 活体；reaper keep 第 228 行 fill_c344.py 在册。
- 已实现进度（死亡时点）：09-21=7,955 / 09-22=7,956 / 09-23=5,457 / 09-24=6,496（启动前 5,002/5,003/3,557/3,952）；批计 cum=9,000。
- 总筹 14:37 后台续跑（exec_6a47ebe4，续跑语义只补缺，幂等=ReplacingMergeTree(symbol,trade_date)）；完成后 per-day 对账（判据 5,560±5%，17号文§五）回填本节。
- 超授权缺口登记（呈 Owner）：09-25=0 / 09-28=2,594 / 09-29=1,000 亦部分缺——超出裁定#431 ⑤ 授权窗（仅 09-21~24），未扩写。
