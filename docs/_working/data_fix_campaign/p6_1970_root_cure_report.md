---
ttl: task_bound
session: st-data-fix-20260921
title: 数据正确性线分包6——1970 假日期治本三步（来源清单/写入端治本/存量修复）交付报告
---

# p6 1970 假日期治本报告（2026-09-21 · st-data-fix-20260921）

真源：`docs/_working/archive/2026-09/dataqa_audit/ch_health_report.md` §4（报告是死的
库是活的，每表先复现）｜ 修前基线快照
`.runtime/tmp/st-data-fix-20260921/p6/p1_row_counts_before.json` ｜ 修后实测
`p1_row_counts.json` ｜ 修复进度台账 `p2_progress.json` ｜ 可逆导出 `E:/{db}/p6_1970_export/`。

## 结论一句话

**写入端三层病根全部治本（scrub 守卫+哨兵改 NULL+两处坏 writer 修复），存量
43.6 万行假日期中 39.9 万行已 NULL 化、1.1 万空壳行已可逆删除；剩余 4.69 万行
（7 表 9 列）因是 PARTITION/ORDER BY 键列被 CH 结构性禁止 NULL 化，如实保留
哨兵并登记 known_data_gaps 待键表重设计/补真源**。修前实测（06:05）与修后实测
（06:50）逐列数字见下表，无虚报凑零。

## 一、来源清单（表×写入端×行号×病因，12 业务表逐条）

病根三层（机制总纲）：

- **机制 A｜硬编码哨兵**：provider 把无源日期写成 `'1970-01-01'` 或
  `datetime.date(1970,1,1)`（列非 Nullable 时的历史通行做法，部分在
  business_data_categories.yaml 有"约定口径"背书）。
- **机制 B｜空串落默认值**：`_norm_date_str` 空值返 `""`，TSV 空字段/
  NULL 写入非 Nullable Date 列时被 CH `input_format_null_as_default` 补成
  默认值 1970-01-01（`ch_writer.tsv_escape` 仅对 None 出 `\N`）。
- **机制 C｜列名漂移**：writer 产出的 FetchResult 列名与表结构不符，被
  `write_result/_init_columns` 列过滤削剩 symbol 单列，其余列全部落
  列 DEFAULT（Date=1970-01-01）。

| # | 表 | 写入端（文件:位置） | 机制 | 修前 rows@1970 |
|---|----|--------------------|------|---------------|
| 1 | c3_fundamental.restricted_shares | akshare_provider `_fetch_restricted_shares`（列 release_date 族过期，实证 data_source='' 10,927 行=unlock_date 1970 计数）＋bdpan 批量导入（announce_date 空值，10.1M 行通道） | C+B | announce 343,298；unlock 10,927 |
| 2 | c3_fundamental.financial_indicator | akshare_provider `_fetch_financial_indicator`（新浪源无公告日，L10461 硬编码哨兵+docstring"YAML 约定口径"） | A | announce 34,339；report_period 64 |
| 3 | c3_fundamental.disclosure_plan | akshare_provider `_fetch_disclosure_plan`（写 None，落非 Nullable 列） | B | announce 33,638 |
| 4 | c3_fundamental.dividend | akshare_provider `_parse_dividend_row`（空串族）；dividend_year 无 Python writer（bdpan 导入缺年度） | B | announce 6,749；dividend_year 983 |
| 5 | c3_fundamental.equity_pledge_detail | akshare_provider `_fetch_equity_pledge`（INSERT 列清单根本不含 announce_date → 列缺省 DEFAULT 1970） | C' | announce 4,588（报告 2,294，库活增长） |
| 6 | c1_market.index_list | akshare_provider `_fetch_index_list`（L7927/7929 硬编码 date(1970,1,1)）；tushare_provider（L637/639 缺源哨兵） | A | base 1,724；list 1,722 |
| 7 | c1_market.convertible_bond_list | akshare_provider `_parse_convertible_bond_row`（end/delist/convert_start/convert_end/stop_convert 五列硬编码"新结构无"哨兵；start/list 缺源 or 1970） | A | start 1,051；list 1,054；end/delist/convert×3 全表 2,102 |
| 8 | c3_fundamental.audit_opinion | akshare writer 空 yield（真源=bdpan 导入） | B(通道外) | announce 150 |
| 9 | c1_market.etf_list | akshare_provider `_parse_etf_list_row`（sina 无成立/上市日，L7589-7590 哨兵，docstring 自证 2026-08-14 有意设计）；tushare_provider L723-724 | A | setup 55；list 84 |
| 10 | c3_fundamental.shareholder_count | akshare writer 已有 skip 守卫（真源=bdpan 少量缺公告行） | B(通道外) | announce 47 |
| 11 | c1_market.stock_list | miniqmt_provider 退市闭合（L3635 `list_date or "1970-01-01"`）；delist_date 空串=在市语义 | A+B | list 2；delist 5,555 |
| 12 | c1_market.rate_decision_calendar | akshare_provider `_fetch_rate_decision_calendar`（decision_date 空串族） | B | decision_date 1 |

（设计内不算病：index_list 1,700 行 valid_to=1970 PIT 关死墓碑，
known_data_gaps `index_list_wrong_universe` 在案。）

## 二、写入端治本（已落地，commit 见文末）

1. **防再犯守卫**：`src/zephyr/data/ch_writer.py` 新增
   `scrub_1970_date_sentinels`——写前对日期类列（`*_date`/`*_period`/
   `dividend_year`）的 `''`/`'1970-01-01'`/date/datetime(1970,1,1) 统一置
   None（\N），`write_result` 与 `BufferedWriter.add` 两个 TSV 构造入口接线，
   拦截即 warning 留痕；PIT 轴 `valid_from`/`valid_to` 豁免（墓碑设计）。
   全 provider 通道（akshare/tushare/miniqmt）一并受保护。
2. **哨兵改 None**（机制 A 清除）：akshare financial_indicator（新浪无公告日）、
   convertible_bond_list 五列硬编码+两列缺源、etf_list、index_list；
   tushare index_list/etf_list；miniqmt stock_list 闭合。相关 docstring 同步
   作废"1970 约定口径"表述。
3. **坏 writer 修复**：`_fetch_restricted_shares` 列名对齐真实表结构
   （announce_date=None/unlock_date/float_shares/float_ratio）——既止住
   DEFAULT-1970 生成又复活断写链路；`_fetch_equity_pledge` 显式带
   announce_date=None（禁列缺省）。
4. **Schema 使能**（Phase2 已执行）：13 表 15 列 `ALTER ... Nullable(Date)`
   （admin 通道）；键列豁免见下节。
5. 测试：`tests/zephyr/data/test_scrub_1970_sentinels.py` 6 例（哨兵转换/PIT
   豁免/幂等/非日期列不动），与既有 test_ch_writer 45 例同批 51 passed。

## 三、存量修复对照表（修前→修后，逐列实测）

**A 族（可 NULL 化，已清零，398,740 格 NULL + 10,927 空壳行删除）**：

| 表.列 | 修前 | 修后 | 动作 |
|-------|------|------|------|
| restricted_shares.announce_date | 343,298 | **0** | 3 批 symbol 区间 UPDATE→NULL（批 102,636/100,793/102,051） |
| restricted_shares.unlock_date（空壳行） | 10,927 | **0** | 实证五业务列零载荷（data_source=''/float 双 NULL/无股东名）后，可逆 ALTER DELETE（行数 10,177,657→10,166,730=纯 bdpan 口径） |
| disclosure_plan.announce_date | 33,638 | **0** | UPDATE→NULL |
| shareholder_count.announce_date | 47 | **0** | UPDATE→NULL |
| index_list.base_date / list_date | 1,724 / 1,722 | **0 / 0** | UPDATE→NULL（valid_from/valid_to 设计轴不动） |
| convertible_bond_list.start/list/end/delist/convert_start/convert_end/stop_convert | 1,051/1,054/2,102×4 | **全 0** | 7 列 UPDATE→NULL |
| etf_list.setup_date / list_date | 55 / 84 | **0 / 0** | UPDATE→NULL |
| stock_list.list_date / delist_date | 2 / 5,555 | **0 / 0** | UPDATE→NULL（pit_query 幸存者偏差走 valid_to，delist_date 仅信息列，消费方零过滤依赖已核） |

**B 族（PARTITION/ORDER BY 键列，CH 禁 ALTER Nullable——结构性残留 46,905 行，
如实保留哨兵并登记 gaps 待补真/键表重设计）**：

| 表.列 | 残留 | 键约束 | 补真可行性 |
|-------|------|--------|-----------|
| financial_indicator.announce_date | 34,339 | ORDER BY 键 | 新浪源无公告日；东财 em 接口 akshare 1.18.75 实测损坏（在案），需换源立项 |
| financial_indicator.report_period | 64 | PARTITION 键 | 无锚行（report 期缺失） |
| dividend.announce_date / dividend_year | 6,749 / 983 | ORDER BY/PARTITION 键 | akshare 分红接口有公告日期列，可后续重拉对账补真 |
| equity_pledge_detail.announce_date | 4,588 | PARTITION 键 | 接口无公告日，真实来源待找 |
| audit_opinion.announce_date | 150 | ORDER BY 键 | 真源=bdpan，待专项 |
| rights_issue.announce_date | 31 | PARTITION 键 | 源有配股公告日列，可重拉补真 |
| rate_decision_calendar.decision_date | 1 | PARTITION 键 | 单行待人工核 |

**设计内保留（非病，不动）**：index_list valid_to=1,700（PIT 墓碑，gaps 在案）；
valid_from 1970 残迹 index 1,722/convertible 1,054/etf 84/stock 2（"自纪元可见"
PIT 语义+键列）；4×*_bak_1970clean_20260914 与 kline_daily_bak_256（备份表保留原样）。

**哨兵观察**：修后两轮全 18 表 probe（06:50 第一轮+第二轮复核同数字）无新增
1970 行；写前守卫对后续写入实时拦截。known_data_gaps 1970 治本条目与本报告
数字一致（条目最后写）。

## 四、restricted_shares 解禁日真值渠道验证（裁定待办留存）

ak.stock_restricted_release_queue_em(symbol='000001') 实测可用（6 行历史队列，
解禁时间/数量全真值）——**渠道可行**。但 10,927 行 unlock-1970 为断写期空壳
（无数量/股东名指纹可对齐），直接重拉会产生无指纹可合并的新行，故本班按空壳
删除处理；后续解禁数据回补建议：按 symbol 重拉全队列整段替换（非逐行补丁），
设计要点已留 `p2_progress.json` 同级台账。

## 五、bak 参照原料使用记录（裁定 #382 建档，只读未动）

读了什么：4×*_bak_1970clean_20260914 全表（2,395/2,402/2,585/2,401 行），
交叉比对 live 三表+financial_indicator 的 (symbol,report_period) 键，并抽样
指标列载荷。核对结论（逐条）：

1. **零误清**：4 张 bak 全部行 report_period=1970（真 report_period 行数=0），
   09-14 清理只删了"报告期无锚行"，未伤真值行。
2. **零可找回价值**：抽样 bak 行指标列（eps_basic/roe/debt_ratio）全 NULL——
   被清行本身就是空壳（含日期列全 1970+指标全空），不存在"误清的好数据"。
3. **键比对**：balance/cashflow/income 的 bak 键在 live 全缺失（整段被清）；
   financial_indicator 2,538/2,585 缺失、47 键已被后续采集以新行重建。
4. bak 表本体未做任何写操作，处置（保留/退役）仍归乙线呈报流程。

## 六、可逆留痕与复跑

- 修前受影响行整行快照（13 Parquet，06:32 落盘）：
  `E:/c3_fundamental/p6_1970_export/*_pre_fix_20260921.parquet`、
  `E:/c1_market/p6_1970_export/*_pre_fix_20260921.parquet`
- 复跑核数：`.runtime/tmp/st-data-fix-20260921/p6/p1_probe_1970.py`（只读）；
  修复编排（幂等 resume）：同目录 `p2_mutate_1970.py`（export/ddl/mutate/verify 分级）。
- 全程无 OPTIMIZE/TRUNCATE/DROP；删除类变更仅上述空壳行（导出先行）。

## 七、提交与登记

- 代码批：qid q-20260921-st-data-fix-20260921-0035→0036→0037（0035 阵亡
  MUTABLE-CONST-WITHOUT-FINAL 已改 Final 注解；0036 阵亡 UP009 已删 utf-8
  声明；两次 dead_reason 均留队列台账）——落地 hash 以 `git log` 为准。
- known_data_gaps.yaml 1970 治本条目：本报告定稿后最后写入（CAS+release）。
- 停手项：B 族 46,905 行不硬闯键列约束（ALTER 被服务端禁止实证 Code 524），
  如实登记；restricted_shares 解禁日整段重拉替换属新工单，未开工。
