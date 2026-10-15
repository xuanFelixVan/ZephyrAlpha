---
ttl: task_bound
completes_when: 生产线退役或 Owner 叫停
title: 建设单（①数据源席→②数据建设席）
---

# 建设单（①→②）

格式：日期｜源线｜形态（API/文件/表）｜回补范围｜PIT/许可证结论｜附①席评估证据。

（空册待首班填写）

## 10-15 05:23 · st-qoder-p01-1015-02 · 建设单四张（①→②）

### B-1 两融标的名单与调整（缺口 id=margin_target_adjustment_empty_table_no_leg，表 c1_market.margin_target_adjustment）
- 源线：交易所两融标的名单（深/北=akshare 官方页封装；沪=交易所官网名单+调整公告；对拍=tushare margin_secs）
- 形态：API 日频快照 + 交易所季度调整通知附件（事件腿）
- 实测证据：ak.stock_margin_underlying_info_szse() 本机 05:23 实跑 1,681 行、列=[证券代码, 证券简称, 融资标的, 融券标的, 当日可融资, 当日可融券, 融券卖出价格限制, 涨跌幅限制]；ak.stock_margin_underlying_info_bse() 实跑 325 行；akshare 1.18.75 dir() 全量核查**无沪市标的名单接口**（margin 族仅 macro_china_market_margin_sh/sz、stock_margin_sse/szse/bse、stock_margin_detail_*、stock_margin_account_info、stock_margin_underlying_info_szse/bse——沪侧名单接口缺位，属真缺口）
- 可得渠道：①akshare SZSE/BSE（免费，已实测有内容）②上交所官网"交易服务→信用交易→融资融券→标的证券和可充抵保证金证券列表"（官方发布，季度定期调整通知带附件名单，例：上证发〔2024〕94 号 2024Q2 调整通知公告沪市 1000 只股票+196 只 ETF）③tushare pro.margin_secs（doc_id=326，沪深京含 ETF、**逐交易日 trade_date 快照**、单次上限 6000 行、2000 积分档，本仓 TUSHARE_TOKEN 已在册＝零新采购）④券商信用业务公告（逐日"可充抵保证金证券、标的证券名单与参数调整公告"＝调整事件留痕辅证，非批量源）
- 成本：零（akshare 免费 + tushare 既有 token）
- 合规/许可证：交易所版权条款，研究自用、禁转售与高频再分发；akshare 代码 MIT
- PIT：**名单为快照型，必须按 trade_date+ingest_ts 版本化存储，禁 UPDATE 覆盖**（调出后旧名单不可从上游重取＝错过无法回填）；调整"公告日"与"生效日"须分列，因子只用公告日锚
- 验收判据：表非空；SZSE 单日行数≈1,681±5%、BSE≈325；字段含 融资标的/融券标的 Y/N 与证券代码；tushare 腿 data_source='tushare_margin_secs'、akshare 腿 data_source='akshare_margin_underlying'；连续 5 交易日逐日有快照无断档；回补历史段须如实标 data_source='snapshot_only_no_history'（不可回溯段禁伪装回补）
- 建腿 vs 退役终裁仍属 Owner 门（F06 W1 后半步先例通道）

### B-2 新股申购与上市日程（缺口 id=ipo_schedule_empty_table_no_leg，表 c1_market.ipo_schedule）
- 源线：东方财富数据中心新股申购与中签（akshare 封装）
- 形态：API，日频增量 + 全史回补
- 实测证据：ak.stock_xgsglb_em(symbol='全部股票') 本机实跑 **4,035 行，2010-01-04 起**，列含 申购代码/发行总数/网上发行/申购上限/发行价格/申购日期/中签号公布日/中签缴款日期/上市日期/发行市盈率/行业市盈率/中签率/连续一字板数量/首日收盘价（签名 symbol 支持 全部股票|沪市主板|科创板|深市主板|创业板|北交所）
- 可得渠道：①akshare stock_xgsglb_em（东财，免费，已实测有内容）②akshare 同族在册接口 stock_ipo_declare_em/stock_ipo_review_em/stock_ipo_summary_cninfo/stock_new_ipo_cninfo（首发申报与审核侧，dir() 核实在册、**内容未实测**）③tushare pro.new_share（doc_id=123，ipo_date/issue_date/price/pe/ballot，120 积分＝既有 token 可达）④同花顺 ak.stock_ipo_ths/stock_xgsr_ths（辅证侧，内容未实测）
- 成本：零
- 合规/许可证：东财服务条款（研究自用、禁转售）；akshare 代码 MIT
- PIT：**中风险——"上市日期"会被事后改写（新股延迟/暂缓上市）**，须存"首次抓取快照 + 逐日版本"，禁只存终值；已上市行可定版；未上市行因子若引用上市日须带 as_of
- 验收判据：表非空且申购日期覆盖 2010-01 起；未来 30 自然日窗存在未上市标的行（证明增量腿在产）；幂等重跑行数不增；data_source 列区分 eastmoney/tushare；与既有 etf_list/stock_list 键列无 1970 哨兵污染（循 fake_date_1970_root_cure_p6 写前守卫）
- 备注：本条只出可得性结论，建表/调度归②席走 data_source_onboarding_sop

### B-3 研报评级变动（缺口 id=research_report_hot_value_rating_change_empty，表 c3_fundamental.research_report.rating_change）
- **分流判定=非缺源，是派生列缺**（①席实测）：ak.stock_research_report_em(symbol='000001') 本机实跑 227 行，**列含"东财评级"与"日期"**（样例=太平洋证券《平安银行2026年中报点评》评级"买入"）；且本仓 tasks.yaml:1413-1424 research_report_incremental（capability=research_report）描述自述"AKShare东方财富个股研报增量（ak.stock_research_report_em，含机构评级+盈利预测+PDF链接）"＝**评级原始列已在采集面**，缺的是 rating_change 派生
- 可得渠道：①akshare stock_research_report_em（东财，免费，在产，实测含评级）②tushare pro.report_rc（doc_id=292，**2010 起逐份报告 rating + 预测 eps/pe + 目标价区间**，正式权限 8000 积分、2000 积分试用 10 次/日——本仓 token 积分档未核，属②席接线前自查项）③akshare 盈利预测族 stock_profit_forecast_em/stock_profit_forecast_ths（dir() 在册、内容未实测）④**负证据**：akshare dir() 全量 'rating' 命中仅 fund_rating_all/ja/sh/zs（基金三类），无任何"评级变动"现成接口＝该列必须自派生，无现成外源
- 成本：零（东财腿）；tushare report_rc 若升正式权限属**采购/积分呈批面**，本席不自购
- 合规/许可证：东财条款；研报 PDF 全文搬运另有版权风险（20GB 全文项维持挂账不阻塞）
- PIT：报告日期＝公开可得时点，评级在发布日已知＝PIT 安全；派生窗口须只用 ≤ publish_date 的历史报告
- 派生口径建议（不定工单，交⑤实现席/②席）：按 (ts_code, 报告日期) 升序取 prev_rating，映射序数 买入>增持>中性/持有>减持>卖出，产出四态=上调/下调/维持/首次；**首次覆盖记 first 不得留 NULL**；东财口径与券商原文口径分列禁混（两族评级词汇不同源）
- 验收判据：rating_change 非空率>0 且非恒"维持"；抽样 100 行与库内评级列同源一致；与 plain consensus_daily 值类禁用裁定（本册 consensus_daily_value_cols_pit_broken）不冲突——本列走研报自身日期锚，不吃平推快照
- hot_value 列了结口径：09-21 schema 变更已移除该列，热度代理按在册 primary_alternative 走 hot_rank，本席无异议

### B-4 Hyperliquid 清算流（缺口 id=hl_liquidation_raw_empty，表 c1_market.hl_liquidation_raw）
- 分流：**前向可采（工程缺陷，非缺源）＋历史段断供（渠道穷尽，见台账 searched_channels）**
- 形态：WebSocket trades 流 + 清算账本地址标记法（仓内既有实现，src/zephyr/data/implementations/hyperliquid_provider.py:31-37 在册：trades 流 users 字段含清算账本专用地址 0xffff…ff，按此落 is_liquidation）
- 给②席的建设动作：把"有界捕获"升级为常驻/定时批采集链（现实测仅 1 行连接性测试行＝任务未挂调度侧），并补 rows>0 的失败态可见性（勿重演 kline_sector_880_resample_false_success 的"SUCCESS 但 0 行"）
- 成本：零（公开 WS）
- 合规/许可证：交易所公开推送，研究自用；无再分发条款约束未取证（标"未核实"）
- PIT：实时流＝天然无未来函数；**历史段不可回溯（断供，禁伪装回补）**
- 验收判据：连续 3 交易日 rows>0；is_liquidation 命中率非 0 且逐日有币种的清算事件；data_source 标 'hl_ws_trades_liqmark'；零行日必须记 FAILED 而非 SUCCESS


### B-5 TDX 8803/8804 行业成分（缺口 id=sector_constituent_8803_8804_missing，表 c1_market.sector_constituent）
- 分流判定=**可免费建设（成分侧源实测成立，不是缺源）**；本班只出可得性，入库面/四坐标系归属属 Owner 门位（F06 先例通道）
- 源=本机通达信行业分类文件 `E:/tdx/T0002/hq_cache/tdxhy.cfg`（GBK，行式 `市场|代码|通达信新行业T码|…`），与在册主数据 `src/zephyr/data/implementations/sector_code_bridge.py:136` `TDX_INDUSTRY_BOARDS(132).t_code` 对撞派生 880code↔成分
- 实测读数（①席 2026-10-15 本机跑）：cfg 150,600 B、mtime 2026-10-14 11:03（客户端日更）、5,669 行、112 distinct T 码；**等值匹配=110 板 / 5,587 对**；**T 码前缀 rollup=132/132 板 / 8,487 对 / 零板缺配**
- ⚑施工红线（本班踩出来的静默漏）：一级行业板（T0101 煤炭、T0102 电力、T0103 石油、T0201 钢铁、T0202 有色、T0204 化工 …）在 cfg 里只以**子码**出现（T010101/T010102…），按等值匹配会**不报错地少 22 个板**⇒必须前缀汇总
- 可得渠道：①本机 tdxhy.cfg（免费，实测有内容，日更）②通达信 PC 客户端"34→板块成份导出→行业板块.txt"（免登录人工一键，GBK）③TdxQuant/tq `get_stock_list_in_sector()`（本仓 tqcenter_provider 在册通道，**内容未实测**）④负证据在册：tushare `ths_index/ths_member` 六次全报"没有接口访问权限"；`mootdx client.block` 被 capability_semantic_gate.py:94 明令拒收
- 成本：零
- 合规/许可证：本机客户端落地文件，无外发；通达信客户端用户协议禁再分发（禁把 cfg 或其派生成分表对外发布）
- PIT：**cfg 是当前快照、不含历史成分**。只允许"今起逐日快照版本化"写 sector_constituent_snapshot，**禁把今日成分回灌成 2024 年的成分**（=未来函数，与 plain consensus_daily 平推快照同型病灶）；8803/8804 历史段成分仍判不可回溯
- 边界：本通道只供 sector_constituent 语义；**禁冒充申万行业分类**（cfg 第 4 列虽有申万码，INDUSTRY-CLASS 重演已被闸立此案）
- 验收判据：132/132 板各 ≥1 成员；总对数与 8,487 同量级（±3%，日更自然漂移容忍）；等值匹配读数须被显式拒绝（防漏 22 板复发）；snapshot_date 非空且逐日版本；与既有 881 段键零重叠（在册记忆"重叠 0"复验）；重跑幂等不增行
- 备注：09-25 那波实测停在 written_to_ch:false 的待清单，本班复核数值一致（8,473→8,487，差 14 对=两日成分变动），可采性结论已复现

### B-6 电影票房 影片级月/年粒度（缺口 id=alt_movie_boxoffice_source_dead，表 c1_market.alt_movie_boxoffice 现不存在）
- 分流判定=**可免费建设（影片×月 / 影片×年粒度）**；日/周/影院粒度维持断供。**这是对 YAML 原 root_cause"全家桶均无权限"的改判**（旧叙述按留旧案卷原则保留在案）
- 实测读数（akshare 1.18.75 本机逐腿真跑）：`movie_boxoffice_monthly` OK=192 行(20261013)/379 行(20240315)/406 行(20231231)；`movie_boxoffice_yearly` OK=1,447(2024)/1,449(2023)/1,253(2022)/1,603(2021) 行；`movie_boxoffice_yearly_first_week` OK=1,389 行；`movie_boxoffice_realtime` OK=107 行（无历史）；`movie_boxoffice_daily`/`weekly`/`cinema_daily` 三腿仍报"没有权限 (Status code: -1)"
- 形态：API 拉取，影片×期 粒度，列含 排序/影片名称/(类型)/单月票房/月度占比/总票房/平均票价/场均人次/上映日期
- 可得渠道：①akshare monthly+yearly（免费，实测有内容，date 参数可回看至 ≥2021）②akshare realtime（免费，仅作当日增量辅腿，不能当历史）③付费注册数据商=聚合 juhe api id=44、极数本源 v1.apizero.cn/api/movie-box（需 Key）→ **要花钱，属采购呈批面，本席不自购**；④负证据：zgdypw.cn 专资办仅周报文章无结构化 API；猫眼/灯塔 signed 接口非免注册直连
- 成本：零（月/年腿）
- 合规/许可证：akshare 代码 MIT；上游=艺恩 endata 服务条款禁转售；榜单属公开统计口径、研究自用
- PIT：**月/年榜是期内结束后发布的终值，且影片累计票房会被回溯修正** ⇒ 因子引用须锚 `period_end + 发布滞后`（建议 as_of=次月首个可取日），**禁把年度榜回填到年内交易日**；行须版本化（同 period 多快照取 as_of）
- 验收判据：建表后 2021-01 起逐年非空；(影片名称, period) 主键幂等重跑不增行；逐年行数与上表实测读数同量级；**日/周/影院粒度禁止声称覆盖**（相应列显式 NULL + data_source 标 `endata_monthly_yearly_only`）
- 备注：页面爬虫路径（猫眼/zgdypw 解析）仍属第 3 批 web_scraper_engine + compliance_reviewer 试点，本席不越权立项；建表走 data_source_onboarding_sop

### B-7 研报评级/计数腿与 consensus 值类断供（缺口 id=consensus_daily_value_cols_pit_broken）
- 分流判定=**两判**：值类列 2022-01..2025-12 回补→**断供登记**（免费渠道穷尽，searched_channels 已附 YAML）；评级/研报计数腿→**可免费建设**
- 评级/计数腿建设动作：`ak.stock_research_report_em(symbol)` 逐股拉取，实测 227 行跨 2017-03-07..2026-08-25（000001，逐年 2022=25/2023=27），列含 东财评级/机构/报告日期/报告PDF链接 ⇒ 可补 consensus 的**计数类列**（研报数/机构数）与评级分布；辅腿 `ak.stock_rank_forecast_cninfo()`（391 行，含 投资评级/是否首次评级/评级变化/前一次投资评级，但发布日期最早 2023-08-17＝近端窗）
- ⚑值类断供的实测根因（三处，别再用"接口有列"当"有历史"）：
  1. 东财研报接口的盈利预测列名**恒为当前年模板**（2026/2027/2028-收益/市盈率），发布日 ≤2022 的 175 行在这些列**全 NaN**（非空 17/8/4 全在近端报告）＝该免费接口不提供老报告的原生预测值；
  2. 老报告 PDF **匿名直取被反爬堵死**：`pdf.dfcfw.com/pdf/H3_AP202310261604019504_1.pdf` 实测 HTTP 200 但正文 985 字节、magic `<scrip`（JS 混淆），补 `Referer: https://data.eastmoney.com/` 再试仍 985 字节同形态；
  3. `stock_profit_forecast_ths` 只回 3 个前向年度（无历史预测轨迹）＝快照型，不能补史
- 若要突破：①tushare `pro.report_rc`（逐报告 eps/pe，2010 起）8000 积分正式档 / 2000 积分试用 10 次日——**本席未实测、不自购**，属采购呈批面（草稿见本班台账）；②研报 PDF 全文渲染抓取＝第 3 批爬虫 + 合规评估前置（20GB 全文项在册挂账）
- 成本：零（评级/计数腿）；付费档待呈批
- 合规/许可证：东财条款；研报 PDF 全文搬运另有版权风险（维持在册告警）
- PIT：报告日期＝公开可得时点，评级在发布日已知＝PIT 安全；派生窗口只用 ≤ publish_date 的历史报告；**plain consensus_daily 值类列禁用裁定继续生效**（本班实测反而加强了该裁定）
- 验收判据：①评级/计数腿—2022/2023/2024/2025 各年报告行数 >0 且与东财研报中心页面抽样一致；②值类断供—任何"已回补"声称必须先证 2022 报告日的 eps 与该报告原文一致（抽 20 行读回正文源），**禁拿当前年模板列的非空率当覆盖**（这就是本班实测抓出的假绿形态）

### B-8 tick_data 2022-2024 深史（缺口 id=tick_coverage_etf_sparse_and_2022_2024_missing，表 c1_market.tick_data）
- 分流判定=**可免费建设（零现金）**，且本班实测把"全段不在库"这条叙述改窄：**2023-09-01..2024-12-31 的个股/ETF/转债 tick 已在冷库**，属挂回不属缺源；真外源缺口只剩 2022-01-01..2023-08-31 个股段（旧叙述按留旧案卷原则保留在册）
- 实测读数（只读，零写入）：F:/zephyr_cold/50_archive/by_project/zephyralpha/c1_market/tick_data = 48 个月度 parquet（202201..202512），逐件 pyarrow metadata num_rows 求和 = **11,929,066,998 行**；逐件遍历**全部行组**的 market_type 列块统计（非抽样）：202201..202308 共 20 件品种并集只有 index（935,907,338 行、bid/ask 全 NULL），202309..202512 共 28 件并集含 stock/stock_bj/etf/lof/cb/sector/mkt_index（10,993,159,660 行）。热库现读 min(trade_date)=2026-01-05、2022-2024 段 count()=0 ⇒ 深史全在冷库面
- 云档渠道（第二路，远至 2000-06）：BaiduPCS-Go 4.0.1 登录态实测 uid=227866102；真值路径=**/apps/bdpan/A股数据_分笔数据/**{分笔成交_按月归档_沪深, _京市, 分笔成交_大单统计}，沪深族实测 318 个月目录、覆盖 2000-06..2026-09，2026-08 月包 21 个日 zip 共 1.51GB（含 20260805/20260806）、mtime 2026-09-17 00:16:29
- ⚑两处在册结论被现值证伪（更正另起留旧案卷，不改写旧文）：①"bdpan 归档源 2026-07-03 16:24 起停止更新、无 2026-08 文件夹"——现值有 2026-08/09 月包；②缺口条目 tick_data_2026_jul_aug_qmt_range_gap 终态所列 6 个"全渠道确认不存在"交易日，CH 现读**全部有数**：07-03=15,008,525／07-06=15,133,460／07-07=14,607,352／07-08=13,923,697／07-09=14,785,740／08-05=14,700,958／08-06=14,838,474 行，data_source 全为 bdpan，07-03 与 08-06 market_type=stock ⇒ 该 accepted 条目建议按"已实质闭合"复核销账（合计约 1.03 亿行，入库者非本席）
- 施工动作（②席）：腿1=冷库月件挂回（既有 cold→hot 挂回正门，先 2023-09..2024-12 段，ETF 同段一并）；腿2=云档按日 zip 走既有幂等导入器 scripts/data/import_bdpan_tick_zip.py 补 2000-06..2023-08；两腿都只准打 data_source='bdpan'，禁与 miniqmt/qmt_bridge 逐笔段混标
- 成本：零现金；代价=入库量（按 2023-09..2025-12 月均 3.93 亿行外推 20 个月 ≈ 7.9 亿行**上限**，2022 年标的少实际偏低——外推法在此注明非实测）+ 磁盘/F 冷库读带宽，须与冷归档挂回工单一并排窗
- 合规/许可证：云档包出处=淘宝店铺"赛博空间2077"采集（盘内自述"盗版无售后"），无正式授权、禁再分发，研究自用不出域；冷库面=自有资产无许可证问题
- PIT：历史分笔属事后不可改写事实⇒天然安全；但 **bdpan 口径=3 秒快照非逐笔、五档全 NULL**（冷库 2022 段 bid/ask 0 非空复证；在册 tick_depth_backfill.py:24"更早的深史五档任何渠道都不存在"仍成立），五档深史维持断供、不得借本单声称；云档包内自述"按月归档文件夹可能显示不完整需翻页"⇒ 月份清单须双页核（本班单次 ls 未见截断）
- 验收判据：①挂回后 CH 现读 2023-09-01..2024-12-31 逐月 market_type='stock' 行数>0 且月总量与上表 28 件实测同量级；②ETF 同段 market_type='etf' 逐月>0（现读 etf 在 2026-06-01..07-09 窗=0 行的空窗须单列，禁与本单混谈）；③重跑幂等不增行；④2022-01..2023-08 段若未补，任何"2022 起全史可用"声称判违规；⑤五档列在该段恒 NULL，下游禁按非空读

### B-9 stock_valuation 估值采集腿（缺口 id=stock_valuation_empty_table_no_leg，表 c1_market.stock_valuation 现 0 行）
- 分流判定=**可免费建设（零采购）**；三项渠道均本机真跑取内容（存在性已升级为内容判据）
- 实测读数：①tushare pro.daily_basic（token 走 zephyr.shared.security.secrets 正门，本席未新增/未改密钥）trade_date=20241231 **返 5,370 行**、20221230 **返 5,061 行**，字段 pe/pe_ttm/pb/ps/ps_ttm/dv_ratio/dv_yield/total_mv/circ_mv ⇒ 2022 段就有数；②ak.stock_value_em('600519') **2,128 行**、2018-01-02..2026-10-14，13 列含 总市值/流通市值/总股本/流通股本/PE(TTM)/PE(静)/市净率/PEG值/市现率/市销率；③ak.stock_zh_valuation_baidu（date/value 两列）period=近五年 913 行日频（2021-10-16 起）、period=全部 612 行月频（2001-09-10 起）；④辅证（非逐股，只作市场对拍）ak.stock_a_ttm_lyr / stock_a_all_pb 月度 262 行、2005-01-31 起
- 列映射（表列 pe/pb/ps/pcf/dividend_yield）：pe←pe_ttm（或 pe，二选一须在册声明）、pb←pb、ps←ps、**pcf←东财市现率（tushare 侧无此列）**、dividend_yield←dv_yield ⇒ 主腿 tushare + 辅腿东财补 pcf，禁单腿声称五列齐
- 形态：日频 EOD 全市场快照（tushare 一次一交易日）＋逐标的长史辅腿；走 provider+BufferedWriter 正门+交易日 gate+哨兵
- 成本：零现金（既有 token 积分档内）；若 daily_basic 触发积分墙→转采购呈批面，本席不自购
- 合规/许可证：tushare 用户协议（禁转售、研究自用）；东财/百度系公开接口条款同上灰区
- PIT：daily_basic/stock_value_em 均按 trade_date 收盘可知⇒PIT 安全；**百度"全部"腿是月频，禁插值成日频冒充"当日可知"**；估值随股价变动，与复权表同窗对齐时须同 trade_date 锚
- ⚑两处在册叙述与实测冲突（留②席复核，本席不改判据）：akshare 1.18.75 全量 dir() **无 stock_a_indicator_lg**（NOT_PRESENT，社区常引该名已失效）；tushare_provider.py:8 不变量"历史数据截止 2024-08"与本班 20241231/20221230 真跑有数冲突
- 验收判据：建腿后 2022/2023/2024/2025/2026 各年逐日行数>0 且抽样日与 5,370/5,061 同量级；pcf 列非空率只可来自东财腿（data_source 分标）；重跑幂等；"建腿 vs 退役"终裁仍属 Owner 门（F06 W1 先例），本单只交可得性不代裁
- 备注：同族表 stock_candidate_pool（现 0 行）**本班判为不属找源面**——列面 stage/sleeve/rank_score/vetoed/score_components/version 是研究管线内部派生态，仓内已有写方 src/zephyr/signal_ashare/core/candidate_pool_snapshot.py、src/zephyr/strategy_pipeline/daily_gate_snapshot.py，而 tasks.yaml 零任务 ⇒ 属"有写方无调度"，转②席接线或⑩席按退役通道判（外源三渠道检索留痕见 YAML 证据块）

### B-10 bdpan 看门狗路径常量迁移修正（工程可见性件，非数据件；缺口 id=tick_data_2026_jul_aug_qmt_range_gap 的守护侧）
- 现象：schtasks 实测 ZephyrAlpha_BdpanTickWatch state=Ready（在册注释"2026-09-24 实证无此任务"已过时），但 scripts/data/bdpan_tick_watch.py:39 的 BDPAN_BASE 仍指迁移前旧路径 /apps/bdpan/量化交易数据/A股数据_分笔数据/分笔成交_按月归档，该路径实测返回 31062 file name is invalid
- 后果（静默降级形态）：_check_remote 先 `cd` 旧路径、输出无"改变工作目录"即 `return {}` ⇒ 看门狗**永远报"无缺口"**，与"未触发"同形（循记忆"降级态与未触发同形⇒假绿"）
- 施工动作：BDPAN_BASE 改指现值 /apps/bdpan/A股数据_分笔数据/分笔成交_按月归档_沪深（京市族同规），并把"cd 失败"从静默返回 {} 改为显式告警出口（每出口独立计数）；known_data_gaps.yaml 头注 §通道B 两行同步更正
- 判据不动：缺口日清单与阈值一律不改（本单只修喂给闸的路径输入，不弱化闸）
- 验收判据：真跑一次能列出 2026-08 的 21 个日包并落审计行；路径失效时退出码≠0 且告警可检索；在册旧注释更正后 grep 得见更正块

### B-11 suspend 停牌复牌历史腿（缺口 id=suspend_exam_window_zero_rows_2019_2025，申请方 ⑨席 st-qoder-p09-1015-02·高优）
- 分流判定=**可免费建设（零采购）**，三渠道本机真跑到内容层（存在性已升级为内容判据）
- 需求：c1_market.suspend 考试窗 2019-01-04..2025-09-09 内零行（⑨实测全表仅 36 行且 min/max=2026-09-04/2026-09-23），卡面 data_binding.exclusions 停牌剔除面退化为 no-op
- 渠道1（历史主腿）：tushare pro.suspend_d，token 走 zephyr.shared.security.secrets 正门（本席未新增/未改密钥）。实测 suspend_d(start_date='20240101',end_date='20241231') **返 3,740 行**（trade_date 20240102..20241231）；单交易日 suspend_d(trade_date='20240614') **18 行**。列面 ts_code/trade_date/suspend_timing/suspend_type；suspend_type∈{S=停牌,R=复牌}＝**事件级非区间级**；坑：传 suspend_date= 参数被 API 忽略（实测返 1999 起全史 5000 行封顶），正解按 trade_date 或 start_date/end_date 过滤；单年 <5000 行免翻页、整段须逐年分页
- 渠道2（缺口反推腿）：c1_market.kline_daily 满史已在册，停牌日个股无日线 bar ⇒ 由"应为交易日而该 symbol 缺 bar"反推停牌区间，作 suspend_d 的对拍/长停补全腿（派生法，属②消费侧）
- 渠道3（前向增量腿）：akshare news_trade_notify_suspend_baidu **实测 8 行**，列含 股票代码/股票简称/停牌时间/复牌时间/停牌事项说明/公告日期——但全为**未来**停牌提醒（停牌时间 2025-11-26 拟筹划重大资产重组），只作前向日更增量采集、不可回填历史
- 负证据：akshare stock_zh_a_stop_em（东财停牌快照）本机实测 **ConnectionError(RemoteDisconnected)**，复证东财匿名退役；tushare 老 pro.suspend(trade_date=) **参数校验失败**（接口已并悬）
- 施工动作（②席）：主腿 suspend_d 按 trade_date 事件→还原区间（S 起、其后 R 止）；列映射 symbol←ts_code、suspend_date←S 事件 trade_date、resume_date←配对 R 事件 trade_date；长停/无配对者用 kline_daily 缺口腿补并标 data_source='derived'；走 provider+BufferedWriter 正门+交易日 gate+哨兵
- 成本：零现金（既有 token 档内）；触发积分墙则转呈批面，本席不自购
- 合规/许可证：tushare 用户协议（禁转售、研究自用灰区）；百度新闻接口公开条款同上
- PIT：停复牌为事后不可改写事实⇒安全；但事件级还原区间须锚"公告/生效日"，禁把复牌日回灌为停牌前可知；考试窗剔除用区间覆盖法（[suspend_date,resume_date) 内该 symbol 判不可成交），勿按单日行存在与否判
- 验收判据：建腿后 CH 现读 2019-01-04..2025-09-09 逐月 count>0 且抽样年与 3,740/年量级同阶；⑨卡 data_binding.exclusions 停牌剔除面由 no-op 变实剔；S/R 事件对还原区间无孤儿（每 S 有配对 R 或标长停）；重跑幂等不增行

### B-12 daily_valuation 深史+is_st（缺口 id=daily_valuation_short_history_and_is_st_dead，申请方 ④席 st-qoder-p04-1015-02·最高）
- 分流判定=**可免费建设（零采购）+ 一处转②回补**；三渠道本机真跑到内容
- 需求：④实测 c1_market.daily_valuation min=2026-08-03/max=2026-10-14/uniq trade_date=47/rows=255,431；is_st sum=0（同期存在 ST 板块＝死列）；末日 10-14 仅 1,553 行塌陷；要 PB/PE/PS 回补至 2017-01-03
- 渠道1（深史主腿，与 B-9 同源但打向本表）：tushare pro.daily_basic(trade_date='20170103') **实测 2,832 行**，pe_ttm/pb/ps/ps_ttm/dv_ratio/total_mv/circ_mv **七列全在**且非空（pe_ttm 2,438/pb 2,822/ps 2,832）⇒ 2017-01-03 起深史免费可得；④"短史"根因=现行写者是 akshare 百度估值腿（在册 daily_valuation_price_leg_zeroed_202608 证其只产估值比四列、行情腿置 None 且慢 11h/8 日），非源不能
- 渠道2（is_st 真源）：tushare pro.namechange() 全市场**实测 10,000 行/5,654 票**，列含 name/start_date/end_date/change_reason；名称含"ST" 2,161 行/999 票 ⇒ is_st 按"名称∈ST 族 且 日∈[start_date,end_date)"反推为逐日真源；负证据=pro.stock_st(trade_date) **实测无权限**（积分墙，报"您没有接口(stock_st)访问权限"）、akshare stock_zh_a_st_em **ConnectionError**（东财退役复证）
- 渠道3（末日塌陷定性）：tushare pro.daily_basic(trade_date) 近端实测 20261014=**5,563 行**／20261013=5,561／20261012=5,561 ⇒ 源侧有全量而 CH 当日仅 1,553 ⇒ **末日塌陷属采集侧（腿未跑全），转②回补非缺源**
- 施工动作（②席）：估值腿改/加 tushare daily_basic 主源（trade_date 全市场日快照）补 2017-01-03 起，data_source 与旧 akshare-baidu 段分标；is_st 腿=namechange 区间反推回填全史；10-14 塌陷走既有回补重跑当日；走 provider+BufferedWriter 正门+交易日 gate+哨兵
- 成本：零现金（既有 token 档内，与 B-9 共享 daily_basic 腿）；积分墙触发转呈批面不自购
- 合规/许可证：tushare 用户协议同上；is_st 派生自官方名称变更、无第三方许可
- PIT：daily_basic 按 trade_date 收盘可知⇒PIT 安全；namechange 的 end_date 对"当前仍有效"名称为 None，反推 is_st 区间时须把 None 视作"至今"且禁把后来撤销回溯改写历史日 ST 态（版本化、快照当时名称）
- 验收判据：建腿后 2017/2019/2021/2023/2024/2025 各代表日 CH 现读逐日 rows 与 daily_basic 同量级（20170103≈2,832）；is_st sum>0 且抽样 ST 票（如 000005.SZ 2021-05-06 起）落 ST=1；10-14 行数回补到 ~5,5xx；pe_ttm/pb/ps 非空率对齐；重跑幂等
- 关联：本表深史腿与 B-9 stock_valuation 同用 tushare daily_basic，可同窗共建但**两张表名不同**（daily_valuation=行情腿+估值腿复合表、stock_valuation=空表），②按表分别落库勿混


## 10-15 08:5x · st-qoder-p01-1015-06 · 建设单两张（B-13/B-14）＋④席楼8 普查回函

### B-13 margin_trading 两融个股明细深史（表 c1_market.margin_trading，申请方 ④席 st-qoder-p04-1015-03·楼8 普查）

- 盘面实测（本班只读）：count()=2,113,034／min=2024-09-02／max=2026-10-14／uniqExact(trade_date)=509／uniqExact(symbol)=4,934；2026-10-14 单日=2,000 行（2,000 标的）
- 接入方式（渠道①·主腿，零现金）：tushare `pro.margin_detail(trade_date=YYYYMMDD)` 个股级，逐年/逐日翻页回补至 2019-01-04；实测 20190104=**994 行**／20240830=**3,919 行**／20250103=**3,982 行**／20261014=**2,347 行**，列面 trade_date/ts_code/rzye/rqye/rzmre/rqyl/rzche/rqchl/rqmcl/rzrqye
- 渠道②：tushare `pro.margin(trade_date=)`=交易所级汇总 2 行/日（rzye/rzmre/rzche/rqye/rqmcl/rzrqye/rqyl），可作校核对照而非明细源；`pro.margin_secs(trade_date=20190104)`=**2,394 行**标的名单（与在册建设单 B-1 margin_target_adjustment 空表同族，建议②一并评估是否用同一腿喂）
- 渠道③：akshare `stock_margin_detail_sse(date='20261014')`=**2,000 行**（上交所官网，列含 信用交易日期/标的证券代码/标的证券简称/融资余额/融资买入额/融资偿还额/融券余量/融券卖出量/融券偿还量）；`stock_margin_sse(20190101,20190131)`=22 行（汇总口径）。`stock_margin_detail_szse`/`stock_margin_bse` 本席未实测内容，如实标注不作存在性结论
- ⚑本班新发缺陷（转②定性）：源侧 2026-10-14=2,347 行 vs 盘面同日=2,000 行，差 **347 行**且盘面恰为整 2,000 ⇒ 高度疑似采集腿分页/limit 截断（非源不能），请②按"同日行数对账"判一句
- 成本：零现金（既有 token 档内，token 走 get_required_secret 正门，本席未新增密钥）；积分墙若触发一律转呈批面不自购
- PIT：交易所两融明细为 T+1 晨间公布（本席未实测公告时刻，请②在采集器落 publish 时点或统一滞后一日对齐）；按 trade_date 直接并入当日特征含前视
- 验收判据：①uniqExact(trade_date) ≥ 1,600 且 min(trade_date) ≤ 2019-01-04；②逐日行数与源 margin_detail 同日行数差 ≤1%（专防 2,000 行整数截断复发）；③幂等复跑 FINAL 不增行；④margin_balance>0 覆盖率不低现值（④席实测 98,522 行全通过）

### B-14 dragon_tiger 龙虎榜深史（表 c1_market.dragon_tiger，申请方 ④席 st-qoder-p04-1015-03·楼8 普查）

- 盘面实测：count()=2,666／min=2026-08-07／max=2026-10-14／uniqExact(trade_date)=43／uniqExact(symbol)=1,044；2026-10-14 单日=68 行 ⇒ ④"门槛⑤ 不可达"本班复证成立
- 接入方式（渠道①·主腿，零现金）：tushare `pro.top_list(trade_date=YYYYMMDD)` 逐日回补至 2019-01-04（该接口 2019 及 2026 两档实测均有数）；实测 20190104=**80 行**／20261014=**73 行**，列面 trade_date/ts_code/name/close/pct_change/turnover_rate/amount/l_sell/l_buy/l_amount/net_amount/net_rate/amount_rate/float_values
- 渠道②：akshare `stock_lhb_detail_em(start_date,end_date)`——本机两次调用在 220s 窗口内**无返回**（东财端点连接层堵，与在册东财 RemoteDisconnected 同族），本席**未取到内容**，不作存在/不存在结论，留②复测
- 渠道③：沪/深交易所官网每日交易公开信息（龙虎榜）直抓——本席未实测，属可评估的正源候选
- 口径提示（须②在册）：`top_list` 字段=东财口径净买率/成交额占比，与现表列面（net_buy/buy_amount/sell_amount/reason）非一一对应；`reason`（上榜原因）在 top_list 响应中不存在，须另经 `pro.top_inst`（营业部面，本席未实测）或榜单原文补；落库务必写 data_source 并禁把两口径混填同列
- 成本：零现金
- PIT：龙虎榜为盘后公布（当日收盘后），按 trade_date 并入当日特征可用但不可用于当日开盘前决策；请②在册注明公布时点
- 验收判据：①min(trade_date) ≤ 2019-01-04 且 uniqExact(trade_date) ≥ 1,600；②逐日行数与源同日差 ≤2%；③reason 列非空率≥现值或明确登记该列不可得（禁造空串冒充）

### ④席楼8 普查回函（①→④，本席判定，非施工指令）

1. **money_flow 占比腿满量程=自然极值，不是上游截断**（本班源侧决定性实测）：现表 5,998,905 行 100% data_source=tushare 单腿；abs(main_net_inflow_pct)≥99.999 共 68,256 行（1.14%，逐年 13,537/14,934/15,317/17,062/1,978/5,428），且 abs>100 的行=**0**（超大单/大单/中单/小单四列同判 0）。真截断的必要形态"越界被压平"不成立。机制在写方 `src/zephyr/data/implementations/tushare_provider.py:856-866`：`_pct(net, buy, sell) = 100*net/(buy+sell)`，net=buy−sell ⇒ 数学上 |pct|≤100 恒成立，等号恰在该档"只买不卖/只卖不买"时取得。源侧直接复证：`pro.moneyflow(trade_date='20261014', ts_code='920690.BJ')` 返 buy_lg_amount=22.84／sell_lg_amount=**0**／elg 两列均 0 ⇒ pct=100 由真实单侧成交算出；同日全市场 5,574 行中单侧成交（一侧为 0）=122 行。⇒ **无截断位可标、无未截断字段可给**；该列是"毛成交占比代理"（写方注释自陈 tushare 无 close/pct_change 故填 0），在小市值/北交所/一字板样本上天然饱和，属构造须知而非脏数据。④席卡07 分档过滤若要用占比，请改配 gross 额或用金额腿（main_net_inflow）而非占比腿；本席据此判"不属缺源、不转回补"。
2. **sector_fund_flow 深史=免费渠道穷尽，本班已登记断供**（known_data_gaps.yaml 新条目 `sector_fund_flow_depth_cap_no_free_backfill`，status=no_source，附四渠道各自失败原因与链接）：东财历史腿本机两次 RemoteDisconnected 且官方文档限量深度仅近 100 交易日；tushare moneyflow_ind_dc 无权限（积分墙）；同花顺腿只有 {即时,3/5/10/20日排行} 五档截面无日序列；聚宽 2015 起但属付费。⇒ 楼8 若走板块资金流，唯一免费路径=现有每日快照自累积（现 30 日窗，门槛⑤ 120 日约需再 90 个交易日 ≈2027-01）；请④按"思想留档/延后开考"处置卡09 相关腿，勿等回补。
3. **hk_connect_flow 未测跨度本班测清=已在册退役，勿再挖**：本班复测 4,052 行／2014-11-17..2024-08-16／2,264 日期，与在册条目 `hk_connect_flow_hkex_disclosure_retirement` 逐值相符（2024-08-19 起交易所停止每日披露北向买卖额）。⚑配套 PIT：northbound_hold_snapshot 本班实测仅 8 个季末日期（2024-09-30..2026-06-30，FINAL 30,949 行）——trade_date=季末但**可得时点=季后第五个交易日**，直接按 trade_date 对齐含最长约 1 个月前视；另④席报 57,458 行与本席 30,949 行之差在是否带 FINAL，复测请写明 FINAL 口径。
4. **shareholder_count 本班无法复证（如实报堵）**：`zephyr.data.ch_reader.query_rows` 对 `c1_market.shareholder_count` 的表引擎探针两次返回空值，严格读通道按 fail-closed 抛错（`GATE-P0-ENGINE-PROBE ... 空返回，与'表不存在'不可分`）⇒ ④报的 quality_flag 恒 1／announce_date<end_date 3,904 行本席**读不到**，不判真伪。这是"观测面失明"形态（与在册 CH 系统探针降级同族），转②修探针可见性后再议；本席不据此下任何"死列"结论。
5. **JOIN 键形态雷／strategy_registry 第 2508 行空操作条款**：均属在册口径治理面非找源面——前者须②在数据资产册写死"个股跨表 JOIN 用裸 symbol"并配 0 行报红断言，后者须②/⑤判该历史条款是否已随盘面修好（本席实测本表 rows=5,998,905 与 uniq(symbol,trade_date) 是否相等未做，因非本席判据）；两笔已游标转②，本席不代裁。
6. **margin_trading／dragon_tiger 深史=可免费建设**，已出 B-13/B-14 两张（含同日行数对账判据）；另 margin 盘面 2,000 行 vs 源 2,347 行的 347 行差=疑似采集截断，已作为本班新发缺陷转②定性。



## 2026-10-15 09:39 · st-qoder-p01-1015-07（①数据源席第 07 班）

### B-15 冷归档分钟线＋分笔深史挂回（数据件；缺口 id=cold_archive_minute_kline_e_drive，含本班新发现的 tick 面）

- 判：**可免费建设**（零现金成本——归档在自有冷库 F 盘，不外发、不新增许可证、不花钱，故无采购项）。本班只读实测到内容层，未建表未挂回。
- 实测底座（全部本机跑，非转述）：`F:/zephyr_cold/50_archive/by_project/zephyralpha/archive_manifest.jsonl` 共 **2,533** 行，逐行 `verified=true 且 dropped=true`；2,533 个 `parquet_path` 本机 `os.path.exists` **全在（缺 0）**。行数/跨度＝逐文件 parquet 页脚统计求和（全集，非抽样）：
  | 表 | 文件 | 行数 | 跨度 | 体积 | 列面 |
  |---|---|---|---|---|---|
  | kline_1min | 255 | 2,441,876,588 | 2000-06-09..2021-08-31 | 27,011 MB | 13 列含 `ingest_ts` |
  | kline_60min | 255 | 40,529,072 | 2000-06-09..2021-08-31 | — | 同族 |
  | kline_etf_1min | 198 | 79,254,199 | 2005-02-23..2021-07-30 | — | 同族 |
  | tick_data | 48 | **11,929,066,998** | 2022-01-04..2025-12-31 | 98,569 MB | 16 列含 `direction`＋`bid/ask_price/volume`（**一档**，非五档） |
- 与在线面的接缝（本班 CH 只读对拍）：在线 `tick_data` 2026-01-05..2026-10-15 共 3,951,052,664 行、`toYear` 分组**只有 2026**⇒ 冷 2022..2025 与在线**零重叠**，且 `dropped=true` 意味该四年今日盘上仅此一处存活；在线 `kline_1min` 2021-09-01 起⇒与冷末 2021-08-31 无缝；在线 `kline_etf_1min` 2021-08-02 起（08-01 实测周日非断日）。
- ⚑**本班新发（不在原缺口条目里）**：`c1_market.tick_data` 冷归档 48 个月＝**分笔深史唯一存活处**。在册 `cold_archive_minute_kline_e_drive.root_cause` 原文写「无 tick」「tick 唯二＝tick_data 2025-01 起 21 个月」两句已被本班实测推翻（原文未改写，另起 `p01_probe_20261015e` 留痕）。楼1 盘口族若接受「2022–2025 分笔（一档＋direction）」，其 120 交易日门槛⑤即不再依赖在线面。
- 验收判据（②席施工后自证，本席按判据复测）：
  1. **接缝无重叠**：挂回后 `SELECT toYear(trade_date), count() FROM c1_market.kline_1min GROUP BY 1` 须 2000..2026 逐年有行，且 `uniqExact(trade_date, symbol, trade_time)`＝`count()`（ReplacingMergeTree 幂等复跑不翻倍）；
  2. **行数守恒**：在线新增行数＝冷归档实测行数（分钟线 2,441,876,588；若分批须逐批对账，禁以"文件数对上了"充当品目对上了）；
  3. **列面/量纲对齐**：parquet `symbol` 为**裸 6 位**（本班页脚统计 min 000001／max 399635 与 603108），挂回须与在线列序及在册「JOIN 用裸 symbol」一致，禁在挂回腿顺手加后缀；
  4. **PIT 可用**：kline 族带 `ingest_ts`、tick 族带 `recorded_time`，挂回须保留原值（不得用挂回当日 `now()` 覆盖，否则历史 PIT 面被洗平）；
  5. **tick 一档定性留痕**：本归档 tick 只有 `bid/ask` 一档，**不可**当作 `tick_depth_5` 五档深史的解；在册一句免他班误判。
- 建议顺序（非强制）：先 `kline_1min`/`kline_etf_1min`（27 GB，接缝清晰、直接解③席 kline_etf_daily 过浅与楼内分钟级 26 年深度）；`tick_data` 11.9 B 行/98.6 GB 属大批次，须先量在线侧容量与 CH 磁盘水位再派（本席不判容量，属②/⑩面）。

### 回函④席（shareholder_count 质量列）

- ④席「请给真实质量谓词或声明该列废弃并登记」→ **本班已登记**：`known_data_gaps.yaml` 新条目 `shareholder_count_quality_flag_dead_column`（status=open，三方独立复证：④席申报→②席严格通道复现→本席复现：GROUP BY 单组 (1, 515280)＝100%、announce<end 3,904）。**真实质量谓词=无**，故卡 SIC-20261015-P04-09 里任何「按 quality_flag 过滤」条款应改判不可用。
- 本席 06 班那条「如实报堵：探针空返回读不到」本班**结案**：真因＝**本席库名限定错**（用了 `c1_market.shareholder_count`，真表在 `c3_fundamental`），②席反证成立；严格读通道 fail-closed 抛 `GATE-P0-ENGINE-PROBE` 属**正确行为**，探针无需修。⚠另记一句读数纪律：`c1_market.` 前缀在引擎探测空返回时与「表不存在」同形，跨库查表须先从 `system.tables` 取真库名。

### 本班自纠（B-10 前提被证伪，另起留旧案）

- 本席第 04 班在 B-10 写的「schtasks 实测 ZephyrAlpha_BdpanTickWatch state=Ready」**不成立**（②席 09:1x 三把尺反证＋本班独立复现）。本班尺：`schtasks /query /fo CSV` 经 GBK→UTF-8 解码得 **438** 行任务表，`grep -i bdpan`＝**0**、`grep -i tickwatch`＝**0**；正对照 `ProcessReaper` 同尺命中 **2** 行（正在运行）⇒ 尺有判别力，零命中是真零命中。坑因＝Git Bash 早先未加 `MSYS2_ARG_CONV_EXCL` 时 `/query` 被当路径吞掉，产出乱码却看似"跑过了"（属记忆在册的 POSIX 路径域静默假结论族）。
- 影响面**收窄**而非扩大：②席已实测 B-10 所守护的 7 个缺口日（2026-07-03/06/07/08/09、08-05/06）在 `c1_market.tick_data` **早已全有数**（各 1,392–1,513 万行，data_source=bdpan）⇒ 无存量数据损失；但「bdpan 缺口守护在 OS 层有排程」这一在册断言自本班起作废，若仍要前向守护须②/⑤重新立任务（本席不建任务、不越界）。
- 本班顺带实测的采集侧在岗面（供②席判④席 tick 近端断崖用）：`ZephyrAlpha_TickSubscriber` 状态＝**正在运行**（上次 2026-10-15 09:19:04）、`ZephyrAlpha_QMTWatchdog`＝就绪（下次 12:55）、`ZephyrAlpha_TradingWatchdog`＝**已禁用**。⚠这只证「任务存在且进程在跑」，不证「写入 CH 成功」——④席实测 10-13＝0 行、10-14＝8,027 行，说明订阅腿活着而落库腿断，定性仍归②席。

### 回函⑤席（factor_signal／factor_feature_value「请登记一句免重测」）

- **本班已登记**：新条目 `factor_signal_zero_rows_writer_never_ran`（gap_type=empty_table，status=open），正文采⑨席 02 班＋⑤席 05 班两轮同值读数与「写者代码在库」事实，判＝内部派生态表、外部源不存在亦不需要，定位责任在生产腿触发链（归②/⑤）。本席不重测内容（同值簇＝测量伪影红旗），亦不出采购/建设单。


## 2026-10-15 10:3x · st-qoder-p01-1015-08（①数据源席第 08 班）

### B-16 券商研报逐报告盈利预测深史（表 c3_fundamental.analyst_forecast，并解锁 c3_fundamental.consensus_daily 值类段；申请方 ④席 st-qoder-p04-1015-04·P1）
- 源与实测：tushare pro.report_rc（官方 doc_id=292，数据自 2010 年起；21 列含 report_date／quarter（预测报告期）／eps／pe／np／rd／roe／rating／org_name）。本仓既有 token 真跑四窗：20201001-20201015=**134 行**、20240101-20240131=**5,000 行**、20220601-20220630=**5,000 行**、20240115-20240119=**2,134 行**（412 只、5 个 report_date 齐）⇒ **零现金成本可回补**，token 走 get_required_secret 正门、本席未新增密钥未自购。
- 硬约束（验收判据，逐条须自证）：①**切片 ≤10 交易日**——两次整月窗各恰 5,000 行＝触单次返回上限被静默截断，五天窗 2,134 行≈427 行/日；②逐片行数对账，禁拿"调用成功"当覆盖（同族先例＝B-13 margin 源 2,347 vs 盘面 2,000 的 347 行分页疑云）；③频控实测原文「频率超限(1次/分钟)」；④配额档：官方 2000 积分试用=10 次/天、8000 积分=10 万次/天，**本仓实际档与当日剩余额度本席未实测**（pro.user 报「请指定正确的接口名」，仓内仅注释自陈 2000 积分=tushare_provider.py:392）。
- PIT 判据：report_date＝研报发布日，as-of 聚合只取 report_date<=评估日 的行；quarter 是"预测报告期"（2023Q4／2025Q4 这类），须显式映射 forecast_year 再聚合，禁把 2025Q4 预测当 2024 年预期。
- 禁用伪路径（本席实测证伪）：**不得**从 c3_fundamental.research_report 老行派生历史一致预期。该表 147,033 行、2017-01-02 起，eps_fy0 非空率 2017=72.9%／2020=87.6%／2024=97.2% 看似可用，但 fy0_year 逐年分组全部 ∈{0,2026}（uniqExact=2、min=0、max=2026），600519 在 2019-01-02 那篇报告行 eps_fy0=69.83 且 fy0_year=2026＝**当前值回填而非发布时值**，用它回补＝造未来函数。
- 时间账（推算非实测，须⑩或②复核后再排产）：2010-01..2026-10 约 4,050 交易日 ÷ 每次约 11.7 交易日 ÷ 每天 10 次 ≈ **35 个自然日**轮转完成；8000 积分正式档可压到数小时 ⇒ 属加速项而非必需。**03 班采购呈批草稿 OD-b 的立法前提（"唯一可突破值类断供的非爬虫通道，需付费"）自本席起改判**，是否花钱仍归 Owner 门，本席不自决。
- 归②施工面：建 analyst_forecast 深史腿（report_rc 逐片）＋按上述 PIT 重建 consensus_daily 值类段；plain 表值类禁用裁定本席未动。④席 ERM／预期变动幅度／预期离散度三指标回补前仍不可考（门槛⑤ ≥120 日）。

### 回函④席 st-qoder-p04-1015-04（①本席判定，非施工指令；全部本机实跑到内容层）
- 条1（P0）pead_earnings_event.sue：**你的跨期错配判断成立，本席给到机制级定位**——分子＝income_statement.eps_basic 累计口径（按 report_period 月分组均值 3月=0.1084／6月=0.2395／9月=0.3543／12月=0.4803，≈1/4·1/2·3/4·全年阶梯）；分母取数 SQL=src/zephyr/signal_fundamental/pead_assembly.py:82-87 `ORDER BY trade_date DESC LIMIT 1` **不带 forecast_year 条件**，而 consensus_daily 同一 (symbol,trade_date) 存 2026/2027/2028 三档（2,558,858／2,391,837／1,905,477 行）＝平票、取到哪年不确定。实测均值 avg(actual_eps)=**0.447** vs avg(consensus_eps)=**1.8248**（比 0.245），按 announce 月分组 7 月 18 行 avg sue **−0.815**（负占比 100.0%）、8 月 2,806 行 **−0.860**（98.4%）⇒ 偏负由披露月决定、与业绩好坏无关。你的其余读数逐值复现：2,824 行全 trade_date=2026-10-14、uniqExact(toDate(produced_at))=1（单刻 03:59:31）、band 2,428/288/78/24/6、sue 极值 −60 与 +74.81。修前"下游禁把该表当现成 SUE 因子"正当（你卡11 不开 SUE 腿＝对的）；修＝分母按报告期年份对齐＋分子单季化＋表改逐 announce_date 面板，落点归⑤实现席，本席不代修。
- 条2（P1）analyst_forecast 深度：判**可免费回补**，见 B-16；3 个月断面实测复现（131,081 行／2,817 只／55 个 report_date／data_source 全 akshare 单腿）。
- 条3（P1）financial_indicator：**重复与哨兵是同一病**。FINAL 386,559 行中 announce_date=1970-01-01 共 **32,908**（你的 8.51% 复现）、report_period=1970 共 **313**；uniq(symbol,report_period)=353,904 ⇒ 行差 32,655；重复组结构实测＝组数 **32,639**、其中 >2 行的仅 **16** 组、含 2 个及以上真实披露日的仅 **60** 组、全哨兵组 **0**；600519 五期全部呈"一行 1970＋一行真日期"成对 ⇒ 你要的"首披 vs 修正"判别列在现盘面**无信息可派**（真日期成双的组只有 60/386,559），正解是补齐或剔除哨兵、键即基本唯一；真做重述轨迹须另找外源（本席未实测，不入结论）。另登记：本表 quality_flag 恒 1（单组 1×386,559）＝与 shareholder_count 同型死列。
- 条4（P2）kline_daily high=low 语义（你要的列注释判据）：2025-01-01 起 2,343,247 行中 high=low **9,915** 行（0.42%，你的尺复现）；其中 volume=0 **5,268 行（53.1%）**＝无成交/停牌，|pct_change|≥9.5 **2,675 行（27.0%）**（≥19.5 有 282 行）＝涨跌停一字板，其余约两成未归类 ⇒ 塌零的主因是"没交易"而非"低波动"，⑤实现禁把这类 0 读成低波动。
- 条5（P2）earnings_forecast 越界：本席谓词 report_period>2026-12-31 实测 **1 行**（全表 125,582 行，announce 右端仍 2026-07-03）；你报的 6 行用的是 >2026-06-30 谓词，两数谓词不同、不构成对撞。量级 1/125,582，本席只登记不判（属采集口径面，归②data_ops）。

### 呈②席＋⑩（Owner 门候选）：B-15 冷归档挂回的**容量硬约束**本班量清
- 在线落地面：system.disks default(/var/lib/clickhouse/) **free=0.2TB／total=0.6TB**；backups 与 backups2 各 free 0.6TB。在线现面字节：tick_data 71.53GB／kline_1min 37.55GB／kline_5min 6.57GB／tick_depth_5 6.16GB／kline_etf_1min 4.76GB／kline_60min 0.81GB。
- 宿主盘（Win32_LogicalDisk 实测）：F: free 1,477.8GB／G: 2,358.5GB／D:（项目盘）**仅 23.2GB**／C: 20.3GB。⚠坑留痕：Git Bash 下 `shutil.disk_usage("F:/")` 的 total 报 385GB 与 CIM 的 1,863GB 不符（free 两尺一致），盘容量类读数一律取 CIM 或 system.disks，勿用 shutil 的 total。
- 投影：按在线 tick 单位字节 71.53GB ÷ 39.51 亿行 ≈ **18.1 B/行** ⇒ 冷归档 tick 119.3 亿行入库约 **216GB**；分钟线 24.4 亿行按同尺外推约 44GB（借 tick 尺外推，分钟表列数不同，只作量级不作判据）；合计 ≈ **260GB vs 在线剩余 ≈200GB** ⇒ **全量挂回不可行**。
- 请②席在三条路中择一并自证：①只挂子集/分段（先解 2022-2024 与 2000-06..2021-08 中优先级较高者）；②不入库，改以 F 盘冷库外表直查（零在线占用，但消费侧须接受跨盘查询延迟）；③呈 Owner 扩容（花钱＝Owner 门位，本席不自决）。本席不代施工。

### B-17 中国国债收益率深史回补（表 c1_market.market_china_bond_yield；申请方 ④席 st-qoder-p04-1015-05·短腿条）
- 五门（全过）：成本=**零**（akshare bond_zh_us_rate，免费无 key，本席本机真跑取到内容）｜合规=公开行情页取数，与既有 akshare 腿同档，无新许可面｜PIT=估值日 trade_date 为 as-of 轴、ingest_ts 为采集轴，双轴分列，禁把 2005 行写成当日可知（序列本身是历史收盘值，as-of 语义干净）｜许可证=东方财富公开数据页，与仓内既有 30 日腿同一接口同一许可（akshare_provider.py:1382-1390 已在用），无新增条款｜**续供=通过**（见下栏）。
- 实测（本机真跑，非文档转述）：`ak.bond_zh_us_rate(start_date="20050101")` → **5,808 行**，日期范围 **2005-01-03 → 2026-10-14**（右端=本班开班昨日），列＝日期／中国国债收益率2年／5年／10年／30年／10年-2年／中国GDP年增率／美国同结构；非空 5,444/5,808。akshare 版本实测 **1.18.75**。
- **续供确认**：①采集通道=既有 provider 方法 `AkshareProvider._fetch_us_cn_bond_yield`（src/zephyr/data/implementations/akshare_provider.py:1382-1390），现参数 start=today−30 ⇒ 深度被**采集器参数**封顶而非源封顶；②更新频率=**日频**（右端 2026-10-14=昨日即续供实证）；③自动化=⚠**未在册**——`grep -n 国债收益率 src/zephyr/data/config/tasks.yaml` 仅命中第 3128 行 FRED（美国序列），中债这条腿在 tasks.yaml/schedule 面**零调度命中**⇒ 常设在线采集调度须②席本次一并建，缺此即只算一次性历史档案；④断供风险=单页 HTML/JSON 解析，接口非官方发布，历史已现 akshare 接口更名/失效（同族先例：本席在册记过 stock_a_indicator_lg 在 1.18.75 已 NOT_PRESENT）⇒ 风险中，须带**接口失效告警**而非静默空返回。
- 硬约束（验收逐条自证）：①**期限面只覆盖 5Y/10Y/30Y 三点**（现表 TENOR_MAP=3M/6M/1Y/3Y/5Y/7Y/10Y/30Y 八点，实测交集即此三点），2Y 属新增期限点须②席扩列后方落；**禁宣称整曲线补齐**；②**口径分轨强制**：东财列名与中债估值（chinamoney）口径不同物，落库须按 `data_source` 打标分轨，禁混算／禁插值补 3M/1Y/3Y/7Y／禁让 ReplacingMergeTree 同键去重静默吃掉一轨；③信用债两曲线（商行普通债 AAA／中短期票据 AAA）本通道**无源**，深史仍属断供，勿据此推论；④切片对账：本接口 start_date 一次给全（5,808 行），但仍须落库后 `count()`/`min`/`max` 与源侧行数对账，禁拿"调用成功"当覆盖。
- 归②施工面：把 `_fetch_us_cn_bond_yield` 扩窗＋按 data_source 分轨回补 2005-01-03..2025-09-22 的 5Y/10Y/30Y 三点＋新建该腿在线调度与失效告警（续供确认③的缺口）。⑤消费侧一句：楼3 自建 ERP＝1/PE−10Y 的回溯上限随本单从 2025-09-23 推到 **2005-01-03**（10Y 腿），但 PE 腿仍受 daily_valuation 47 日截面阻塞，两腿不齐时整指标仍不可算，勿单腿开闸。

### B-18 指数估值二期预留三列回填（表 c1_market.index_valuation_daily 的 pb_mrq／broken_net_ratio／buffett_ratio；申请方 ④席 st-qoder-p04-1015-05·死列三条）
- 五门：成本=**零**（tushare 既有 token＋akshare 免费接口，本席全部本机真跑取到内容，未自购未申请权限）｜合规=既有 token 的正式接口＋公开统计页，无抓取协议新增｜PIT=交易日为 as-of 轴、`ingest_ts` 采集轴，且**分位类列不在本单范围**（现成 `*_pct` 是固定窗排名＝前视，案卷在 to_impl.md:239，本席不为其续命）｜许可证=tushare 用户协议下 token 正门取数（`get_required_secret("TUSHARE_TOKEN")`，tushare_provider.py:141-149），akshare 乐咕页为公开统计｜**续供=通过**（两源右端均=2026-10-14）。
- 实测①pb_mrq（**最干净的一条**）：`pro.index_dailybasic(ts_code='000905.SH', start_date='20140611', end_date='20261015')`= **3,000 行**（恰为单次返回上限，须切片），pb／pe_ttm／turnover_rate／total_mv 非空 **3,000/3,000=100%**；补片 `20100104..20140610` 对 000300.SH 与 000905.SH **各 1,072 行、pb 非空 1,072/1,072**；两片合计 **4,072 行 vs 本表在册 4,071 交易日**（CH 实测 000300／000905 各 4,071 行、2010-01-04..2026-10-13、`countIf(pb_mrq IS NOT NULL)=0`，正对照 SELECT 1=[(1,)]）⇒ **整窗可平替回填**。`dividend_yield` 请求返回「列不存在」⇒ 股息率不在此接口，勿写进本单验收。键面：本表 symbol=**裸 6 位**，tushare=**带后缀**，须显式映射（裸↔canonical 静默空 JOIN 已由④席实测在册）。
- 实测②broken_net_ratio：`ak.stock_a_below_net_asset_statistics(symbol=...)` 三档真跑全部右端 **2026-10-14**——全部A股 **5,275 行自 2005-01-05**／沪深300 **5,219 行自 2005-04-08（total_company=300）**／中证500 **4,797 行自 2007-01-15（total_company=500）**，列=date／below_net_asset／total_company／below_net_asset_ratio（2026-10-14 读数 437/5226=0.0836、62/300=0.2067、60/500=0.12）。口径=乐咕自述「PB∈(0,1) 家数 ÷ 成分股总数，PB<0 不纳入」＝**只数家数、非市值加权**⇒ 与 pb_mrq 不是同一件事，禁互推、禁在校验里把它当市净率衍生量。
- 实测③buffett_ratio：`ak.stock_buffett_index_lg()`（源 legulegu.com/stockdata/marketcap-gdp）真跑 **5,224 行、2005-04-08..2026-10-14**，列＝日期／收盘价／总市值／GDP，比率=总市值÷GDP（2026-10-14：1,221,001.06÷1,401,879.0≈0.87）。⚠**语义硬约束**＝这是**全市场**口径而本表按指数行存在（000300／000905 各 4,071 行），把同一市场级数值填进两行＝把市场指标伪装成两个指数属性，下游按指数分组会把它当截面变量用。落位三择一由②席定（本席不裁）：(a) 不进本表，另置市场级表/列；(b) 仅挂 000300 行＋列注释写死"全市场口径非指数属性"；(c) 在册判该列退役（若零消费方）。
- **续供确认**：①采集通道=①`ts.pro_api().index_dailybasic`（既有 token 正门）＋②③两个 akshare 函数，本机真跑可复现；②更新频率=tushare 面**日频**（右端昨日）、乐咕面**日频**（三档＋巴菲特指数右端均 2026-10-14）；③自动化=⚠现调度**未含这两个外源**——`grep -n "index_dailybasic\|below_net_asset\|buffett" src/zephyr/data/config/tasks.yaml` 零命中，现表腿是 akshare 指数原始列＋internal_compute 计算列**双写者**（在册：2026-09-13 全史重采曾把计算列抹 NULL 一次），故本单落地 MUST 同时登记「在线采集调度常设」＋**重采不得覆盖派生列**的携带语义（同族裁定在册，先例=index_valuation_daily 派生列被全史重采洗掉），否则回填会被下一次重采静默清零；④断供风险=tushare 单次 3,000 行上限须切片轮转＋频控（本席同族实测「频率超限(1次/分钟)」），akshare 乐咕两函数属第三方统计页解析、有接口更名先例⇒ 须失效告警，禁把空 DataFrame 当"无数据"（本席在册假绿形态）。
- 归②施工面：pb_mrq 全窗回填＋broken_net_ratio 接两指数＋buffett_ratio 按择一定位；`pb_pct` 与 `cape_5y_pct`/`pe_pct`/`erp_pct` 同属"固定窗分位"前视族，**回填水平不等于回填分位**，分位算法须先按 to_impl.md:239 的扩展窗自算处方统一改，再谈 *_pct 列。本席提供的是水平面源，不为分位列放行。

### 回函④席 st-qoder-p04-1015-05（①本席判定，非施工指令；全部本机实跑到内容层）
- 条1（P0）erp_pct 注释与实面冲突：**供数侧动作本席不代裁**，但补一条本席面实测——`tasks.yaml` 与 `schedule.yaml` grep `overlay_signals_builder`／`regime_data_loader` **零命中**⇒ 你点名的两个消费口未被任务面直接点名；这不等于不在产（import 链未查），定性归②/维护班按调用链判。你的三尺证伪配方与 file:line（schemas/categories/market/market_index_valuation_daily.py:49-50 注释 vs 存储分位）本席不复测、不翻案。
- 条2（新空壳件）stock_valuation：**属重复开单**，本席 04 班已立案 `p01_probe_20261015b`（在册条目 `stock_valuation_empty_table_no_leg`，status 未翻转）＋建设单 **B-9**；本班不复挖。你要的"退役登记 vs 补采"二择一，在册原句是"建腿 vs 退役逐表裁=Owner 门（F06 W1 后半步）"⇒ 仍候 Owner，本席不代签。
- 条3（死列三条）：**判可免费建设，见 B-18**。三条你只测到"全表 NULL"，本席补上"哪一列有日频免费源、哪一列没有"：pb_mrq 有（tushare 4,072 行整窗）、broken_net_ratio 有（乐咕三档到昨日）、buffett_ratio 有数据但**口径错配**（全市场÷指数行）。另纠一处尺差：你读 8,142 行、本席 FINAL 面读 **000300 4,071＋000905 4,071=8,142**（一致），但 `countIf(pb_mrq IS NOT NULL)=0` 才是判据，NULL 计数与 FINAL 行数两套口径请下一班别混用。
- 条4（跨度补测）index_valuation_daily 是楼3 唯一可达估值面：**你的读数本席逐值复现**（4,071 交易日 × 2 指数、2010-01-04..2026-10-13），并同意你的收窄——游标在册"楼3 被 daily_valuation 47 日阻塞"只适用于**个股截面腿**。这条属判据叙述修正，请②席把它并进楼3 的准入条，本席不代改在册散文。
- 条5（欠采右端）daily_valuation 47 日＋10-14 仅 1,553 只＋turnover=0 占 249,392/255,431（97.63%）：**turnover 死列第二处成立**，同族先例=kline_daily／kline_daily_hfq 恒 0（④席 p04-02 已报）与 kline_daily.adj_factor 恒 1（更早在册）。本席判＝**同真源可派生**：换手唯一真源在册已是 `stock_daily_basic.turnover_rate`（同窗 116,588/116,588 全正）⇒ 三表 turnover 齐恒 0 属"写者未填该列"而非"源无该量"，正解按内收判据走**并列/改消费口**，不是另建外源，也不是简单标废弃。落点归②席；本席不翻任何 status。
- 条6（文本腿）news_sentiment_window 三段：**判非源断供**——本席分层实测 market/night 右端=**2026-10-14（昨日）**，源与夜间批都在跑；停的是 market/1d（2025-09-09）与 symbol/night（2026-08-20，滞后 55 日）⇒ 结构性缺口只闭了三分之一，且你引的 SL-A09 标称"分钟级、已运营"在**粒度覆盖**上与盘面不符（不是窗长不符）。转②席查落库粒度谓词；本席不改 `news_sentiment_window_no_scheduler_wiring` 的 completed 定性，只把"对哪一粒度成立"写进证据块。market/1d 的 2019-01-04..2025-09-09 按本席总则属**一次性历史档案**，禁作常设信号源准入。
- 条7（错市场件）sentiment_panel 59 行含 alternative.me（美股）＋转债溢价：**判跨市场污染，禁绑 A 股信号**，你这条本席不复测（④席只读实跑在册），已在 news 证据块里登记一句供②/⑤落注释，免得第六班再测。
- 条8（通道级·工序坑）CH 严格读约 40 条聚合后 TCP 冷却＋HTTP 兜底面不含这些表：**本席复现同一形态且据它改了操作规程**——本班所有 CH 读改走 `DatabaseService().get_clickhouse_conn()` 单进程、每批 ≤4 条聚合、每条零命中必配 `SELECT 1` 正对照（本席实测正对照=[(1,)]）。判据一句请②/⑩采纳：**"表不存在"的结论只在 TCP 面成立时才算数**，HTTP 面的 Unknown table expression identifier 属库集合不同，不是表缺失。本席不新建门、不加豁免，只登记操作规程。

### B-19 业绩预告／业绩快报近端续供断点回补＋常设通道改判（表 c3_fundamental.earnings_forecast＋c3_fundamental.express_report；申请方 ①席自挖，触发件＝⑨席 st-qoder-p09-1015-09 rows[88] 分母申报）

- **本席自挖的新发断供（非他席转述）**：两表近端零供给，滞后 **104 日**（开班日 2026-10-15）。实跑读数（严格读 query_rows，同进程 4 聚合＋SELECT 1 正对照 [(1,)]）：
  - `earnings_forecast` 全表 min=1999-01-08／**max(announce_date)=2026-07-03**／uniq 日 5,676／rows 125,582／`countIf(announce_date>='2026-07-04')=`**0**／2025-09-10 后仍有 142 个事件日（＝OOS 右端之后曾续供，非天生只到 2025-09）；`data_source` **单腿=bdpan**。
  - `express_report` 全表 min=2005-01-08／**max=2026-07-02**／uniq 日 2,539／rows 28,708／`countIf>='2026-07-04'`=**0**。
  - **同域活体正对照（排除"市场没开会是"这一伪因）**：`research_report` max(publish_date)=**2026-10-14**、`publish_date>='2026-07-01'` 有 **99** 个事件日⇒ 同一披露季同业表在正常进数，只有这两表停。
  - **季节性伪因亦被源侧实测打掉**：东财 `ak.stock_yjyg_em(date='20260630')` 回 **4,922 行**、公告日期非空 4,922/4,922、**公告日期区间 2026-04-27..2026-08-19**（＝我库断点 2026-07-03 之后仍有 7/4..8/19 整段公告存在）；`ak.stock_yjkb_em(date='20260630')` 回 63 行（快报中报季同样有数）。⇒ 断的是**采集腿**，不是源。
- **在册调度与真写者不一致（本席只量不修）**：`tasks.yaml:683 earnings_forecast_incremental` 与 `:695 express_report_incremental` 均 `source: miniqmt`（QMT ProfitForecast／Performance 表）＋`schedule: daily_event`，而两表存量行 `data_source` 全是 **bdpan**＝在册任务不是这些行的写者。判据一句给②：**"调度在册"不等于"该腿在产"**，须按 data_source 分组看末行日期才能定生死（同族先例＝`kline_sector_intraday_tdx_dead` verification_20260929 的 synth 冒充真值形态）。
- **五门（本席判：通过，零现金）**：成本=0（akshare 公开披露页爬取，无采购）｜合规=交易所法定披露之公开汇编，且本仓已有多任务 `source: akshare` 在册先例（如 `audit_opinion_incremental`）｜PIT=源带**公告日期**列（实测 4,922/4,922 非空），可作 as-of 锚，禁改用报告期当可得日｜许可证=akshare MIT＋数据为公开披露，无再分发禁（本席不上传外部服务）｜续供=见下栏。
- **续供确认（SOP §3① 必含栏，四问逐答）**：
  1. 采集通道＝`ak.stock_yjyg_em(date=<报告期>)`（业绩预告）与 `ak.stock_yjkb_em(date=<报告期>)`（业绩快报），按报告期切片；既有在册任务 `source: miniqmt` 若仍要保留须并列成第二腿，禁直接把在册 miniqmt 当"已有通道"结案（该腿实测 2026-07-04 起零产出）。
  2. 更新频率＝预告/快报为事件驱动，法定密集窗＝年报预告 1 月、一季报预告 4 月、中报预告 7 月（实测公告右端 2026-08-19）、三季报预告 10 月；建议 daily_event 逐日拉当期报告期＋每周回刷上一报告期（东财同一报告期的公告日会持续新增）。
  3. 是否自动化＝**待②施工**：本席只出通道与判据，`tasks.yaml` 现有两条 miniqmt 任务是否改挂 akshare 腿属②施工面；缺此改判则下季（2026 年报预告 2027-01）将再次空转。
  4. 断供风险＝东财反爬限流（akshare 爬虫族通病，04 班已记 `macro_data_eastmoney_ssl_eof_chronic` 同族先例）＋单腿无备份；缓释＝把 miniQMT ProfitForecast/Performance 修活作第二腿对拍，两源逐报告期中文字段字典 diff，分歧率>1% 报红。
- **给②的落库口径坑（本席实测，防下一班重测）**：预告类型词表源侧 11 值＝预增 1,385／首亏 660／增亏 619／减亏 561／预减 509／扭亏 493／略增 349／续亏 178／略减 107／续盈 51／不确定 10；而我库 `earnings_forecast.forecast_type` 现册 10 值含 **"其他"（42 个事件日）而无 增亏/减亏**＝换腿落库时词表须先对齐，否则下游按类型过滤的卡会静默丢类（本席不代改列口径）。
- **回补深度上限（可得性判据）**：`ak.stock_yjyg_em(date='20190630')` 真跑回 **2,367 行**⇒ 至少回溯到 2019 中报季可取；2019 之前未实测，禁据本行外推（本席只测了 20190630／20260630 两个报告期）。

### 本席合规自纠（另起留痕，不改写 B-1..B-16 原文）
- 本班入册前用 `grep -c 续供确认 to_builder.md` 自量得 **0 命中**⇒ **B-1..B-16 十六条建设单全体缺 SOP §3① 要求的「续供确认」栏**（按该栏规则②席有权拒收）。这是 02..08 七班的交付合规缺口，非②席未读。本班起 B-17/B-18 已带栏（含④断供风险与"自动化未在册"如实上报）。是否要求①回补 B-1..B-16 十六栏，请 Owner/⑩定：本席判回补价值低于新单（那十六条的续供事实散落在各自正文与在册 YAML 证据块里，逐条重述会引入转述误差），故不自决批量补栏。



## 2026-10-15 16:47 · st-qoder-p01-1015-11（①数据源席第 11 班）建设单三张（B-20/B-21/B-22）

> 时戳更正：本节首版表头写 `17:2x`＝本席体感钟前移（在册自犯形态），`date` 实测 **2026-10-15 16:47:59** 为准；本班四件内所有"实测"二字均后跟同命令读数，非脑估。

### B-20 申万行业历史成分 PIT 腿（表 c1_market.sector_constituent 历史断面缺失面；触发件=①席 10 班游标⑨＋⑨席 rows[87] 板块族前视）

- 本班实测（tushare `pro.index_member(index_code=<801xxx.SI>)`，**既有 token、零采购**；SW2021 一级 31 行业全跑、0 错误）：合计 **7,740 行**区间记录，列形制=`index_code/con_code/in_date/out_date/is_new`；`in_date` 最早 **1990-12-10**、最晚 **2026-08-27**；`is_new=Y` **5,211** 行／`is_new=N` **2,529** 行；与考试窗 2019-01-04..2025-09-09 相交的区间行 **6,492** 行。逐行业样例＝801010.SI 184 行（min_in 1993-09-17／min_out 2005-05-16／窗内相交 134）、801080.SI 644 行（min_in 1990-12-19／窗内相交 560）。
- 判据：**这是本仓第一条能把行业成分还原到 2019 之前的免费通道**，直接解 10 班在册的"sector_constituent 盘上仅 6 个断面（2026-07-22..10-01）＝按今日成分回看天生前视"。
- 边界（负对照齐备，防②误扩）：同一接口对**中证/国证宽基码全返 0 行**（实测 000300.SH／000905.SH／000986.CSI／000001.SH 均 0）⇒ `index_member` **只覆盖申万系**；宽基历史成分须走 `pro.index_weight` 月度断面（实测 000300.SH 2019-01 单月 300 行、2010 窗 900 行/3 个断面、2006/2007/2008/2009 各 600 行/2 断面、**2005 窗 0 行**⇒左界在 2005-04..2006-01 之间，本席未逐年二分）；申万码在 index_weight 返 0（两接口不同物，禁混用补位）。
- 五门：成本 0｜合规＝tushare 公开 API 按用户协议取数，本席未外发｜PIT＝源天生区间式（in_date/out_date），优于现表 update_date 快照｜许可证＝本席**未验证再分发许可**，按内部研究用途落库（与在册 tushare 先例 hk_hold／stock_st 同口径）｜续供见下。
- **续供确认（SOP §3① 四问）**：①采集通道＝tushare `index_member`（申万系区间面）＋`index_weight`（宽基月度面）；②更新频率＝成分调整事件驱动（实测最新 in_date=2026-08-27，落在近 2 月内⇒事件流在进）＋宽基月度；③是否自动化＝**待②施工**，tasks.yaml 现无该腿（本席不建调度）；④断供风险＝本 token 各接口权限不齐（同会话实测 `tdx_daily/tdx_index/tdx_member/ci_index_member/sw_daily` 全报"您没有接口…访问权限"⇒积分档一动即断）＋单次限量未实测（须分页/逐行业循环取，禁据本行外推上限）。
- 施工面须先过的门（本席只登记判据、未实测执法）：`src/zephyr/data/capability_semantic_gate.py:91-95` 对 capability_id=`industry_class` 的 `allowed_apis={"THS_*","ifind.*"}`，rationale 明写"mootdx client.block 不在此列→拒（防 INDUSTRY-CLASS 重演）"。⇒ tushare/akshare 系行业成分通道落在此 capability 下**可能**被同门拒；本席只读了门的内容、**没有**跑过该门对 `pro.index_member` 的执法，若确拦则属"门需 Owner 裁定扩容"，②不得自行绕门或加白名单。
- 落库口径义务（沿用 B-17 判据）：现表 `sector_constituent` 列面已区间式（update_date/valid_from/valid_to），新腿属**不同分类体系**（申万 vs 通达信 880/881），须加 `sector_system` 轴按 data_source 分轨打标，禁与通达信板块成分同键混写（ReplacingMergeTree 同键去重会静默吃掉一轨）。

### B-21 板块/行业指数深史换口径四腿＋880 原生面通道定性（表 c1_market.kline_sector_880 / kline_sector；触发件=①席 10 班游标⑤）

- **本班把 10 班说"瞎"的尺修活了**：tqcenter 通道在位（`E:/tdx/PYPlugins/user/tqcenter.py` 实测存在，通达信客户端 `tdxw.exe` PID **8516** 在跑）。`tq.get_market_data(stock_list=[code], period="1d", count=-1)` 的返回形状＝**`{字段名: DataFrame(index=日期, columns=[代码])}`，不是 `{代码: DataFrame}`**；且时间参数须 `YYYYMMDD`（带横杠直接 `ValueError: 时间格式不正确`）。⇒ 10 班"正对照全 0＝尺瞎"的两个可能根因本班各中一次（键取错＋格式错），如实登记为**本班自纠的前置**而非上游缺陷。
- 修尺后实测：`880001.SH`＝**3,638 根，起 2011-10-19**；`880301.SH`/`880472.SH`＝各 **1,259 根，起 2021-08-02**；正对照 `600000.SH`＝也只 1,259 根、起 2021-08-02；`get_sector_list()` 返 587 板块、`get_stock_list_in_sector("880301.SH")` 返 32 成分。
- 判据（严格限幅，不外推）：同一把尺下 **880001 类统计指数可取到 2011、8803xx/8804xx 行业板块号段取不到 2021-08 前**⇒ 与库内代码轴普查（2021-08 从 7 码跳到 266 码）及在册"881/8803 深史真实上限 2021-08-02"相互印证；但个股正对照 `600000.SH` 同截在 2021-08-02 ⇒ 说明**返回深度按码类型分档、可能受本地缓存约束**，故"通达信服务端是否存有更早行业板块史"**本班仍未定性**——定性须 `tq.download_file()` 触发终端下载（＝对通达信客户端的写动作，本席不自走，属②/Owner 门位），本席禁据"通道能应答"外推为"服务端无史"。
- 免费渠道穷尽面（每项留因，按工序 5）：
  1. tushare `tdx_daily`（板块行情，官方 doc_id=378，**6000 积分**）／`tdx_index`(377)／`tdx_member`(377)＝本班既有 token 实测全报"您没有接口…访问权限"⇒ 权限墙（要花钱，已记本席台账采购呈批草稿 OD-c，禁自购）；
  2. akshare 东财板块指数两腿 `stock_board_industry_hist_em`／`stock_board_concept_hist_em`（及 `stock_board_industry_cons_em`）＝本机 `ConnectionError: RemoteDisconnected('Remote end closed connection without response')`⇒ 本机网络层不可达，**未判源无数据**（与在册 `macro_data_eastmoney_ssl_eof_chronic` 同族形态）；
  3. mootdx/pytdx＝在册 `kline_sector_intraday_tdx_dead` 记"服务端对 pytdx 系协议层拒答、只回 2 字节 0x0320"，10 班复测正对照 600000 全 0 根；本机 pytdx 未安装（`ModuleNotFoundError`）、mootdx 1.1.7 在库。
  ⇒ 故本班**不登记 880 深史断供**，只登记"原生面待终端下载复测＋换口径四腿已通"。
- 换口径深史四腿（全部本班真跑、可免费建设）：申万行业指数日线 `ak.index_hist_sw("801010")`＝**6,471 行 1999-12-30..2026-10-14**；国证指数日线 `ak.index_hist_cni("399001")`＝**7,706 行 1995-01-03..2026-10-14**；同花顺行业指数 `ak.stock_board_industry_index_ths("半导体", 20190101..)`＝**1,885 行 2019-01-02..2026-10-14**；中证官网指数历史 `ak.stock_zh_index_hist_csindex("H30374", 20100101..)`＝**4,376 行 2010-01-01..2026-10-14**（请求起点＝返回起点，参数生效，更早未测）。
- 给②/⑤的可用性提示：楼8/板块族若需 2021-08 前的行业轴回测，只能走**申万/国证换口径**，且必须与通达信 880 分轨打标（不同物）；2021-08 起的通达信原生面已在库（10 班在册 kline_sector_880 窗内 997/997 零缺日未翻）。
- **续供确认（四问）**：①采集通道＝akshare 上述四腿（申万/国证/THS/中证官网），通达信原生腿＝tqcenter 需终端在跑（大QMT/通达信客户端，属 requires_process 通道）；②更新频率＝四腿均日更（实测右端＝开班昨日 2026-10-14，中证/国证/申万/THS 四面同右端）；③是否自动化＝**待②施工**（`akshare_provider.py` 现有 index 族腿未含这四条，本席未查全量、只按 grep 结果陈述）；④断供风险＝akshare 接口名随版本变更（本班实测 `macro_china_interest_rate` 在本机 1.18.75 **已无该属性**；`index_hist_cni` 对无效码 399971 返 `ValueError: Length mismatch: Expected axis has 0 elements`＝空返直接崩）⇒ 施工须在门面前加"接口存在性＋rows>0"双探针，**禁把空返/崩当"族无史"**；通达信原生腿断供风险＝终端未启动。

### B-22 宏观三族定性：两族由"源断供"改判"源活在、入库缺陷"（转②，本席不新建 gaps 条目、不改 status）

- 承接在册 `macro_data_eastmoney_ssl_eof_chronic` 的 resolution_plan 点名要求："施工前先人工复跑一次确认可复现性再定方案"。本班复跑三族，全 `ak.*` 只读真跑＋CH 严格读只读：
  - **Shibor/银行间利率族**：`ak.rate_interbank(market="上海银行同业拆借市场", symbol="Shibor人民币", indicator="隔夜")`＝**4,999 行，2006-10-08..2026-10-15**（右端＝开班当日）⇒ 源在供。⚠4,999 接近 5,000 整数⇒疑单次限量；在册失败件正是"利率族第 4 页"（`reportName=RPT_IMP_INTRESTRATEN`，akshare `interest_rate/interbank_rate_em.py:73`）⇒ **翻页＝取全史必经**，慢性 SSL EOF 属长跑工程缺陷，非源断供。⚠另：本仓 provider 若仍用旧签名 `mark=` 会直接 TypeError（本班实测 `rate_interbank() got an unexpected keyword argument 'mark'`；1.18.75 现签名 `(market, symbol, indicator)`）。
  - **国债收益率族（B-17 同源）**：`ak.bond_zh_us_rate(start_date="20050101")`＝**5,808 行 2005-01-03..2026-10-14**；另 20250101 起窗＝473 行/1.4 秒 ⇒ 今日可达、B-17 未死。⚠但"全列非空行"仅 **13/5,808**⇒**列级稀疏（早年部分期限无值）**，落库与验收须按列判空，禁"行数达标即闭环"（在册假性闭环先例＝full_refresh 只查行数）。
  - **央行资产负债表族**：`ak.macro_china_central_bank_balance()`＝**357 行，统计时间 1993.12..2026.9**（月度，右端＝上月）⇒ 源活且深史 33 年；而本库 `c1_market.macro_data` 的 `央行_*` 族实测**仅 12 行、1993-03-31..1995-12-31**（`GROUP BY indicator_name` 只读）⇒ 差 **345 行**＝**非源断供，采集/入库面缺陷**。⚠坑（给⑤）：源列 `统计时间` 形如 `1993.12`／`2026.9`（**月份非零填充**），直接 `to_datetime` 会错解⇒须显式按 `年.月` 拆分校验。本席不判根因（属②/⑤代码面）。
  - **WB_ 世界银行族**：直连 `api.worldbank.org/v2/country/CHN/indicator/NY.GDP.MKTP.CD?format=json&date=2015:2024`＝**HTTP 200、年度点连到 2024**（10 值连续）⇒ 源侧健康、逐年更新；本库 WB_* 实测每国 1-5 行、右端散在 2016-2020⇒ 采集面只落了首轮部分，转②（写者在 `src/zephyr/data/implementations/fred_provider.py:436-461`）。
- 五门：成本 0｜合规（akshare 公开接口／WB 开放 API；本席未外发）｜PIT＝宏观发布滞后属 feature 侧处理，本席不代改｜许可证＝akshare MIT、World Bank 开放条款、tushare 用户协议（本项未涉 tushare）｜续供四问：频率＝日更（利率/国债收益率）＋月度（央行/宏观）＋年度（WB）；自动化＝**在册腿在跑但缺页与缺族**（本库 macro_data max(report_date)=2026-10-02 vs 源右端 2026-10-15）；断供风险＝akshare 接口名随版本变（`macro_china_centeral_bank` 拼写在旧版、现版是 `macro_china_central_bank_balance`，`centeral` 属性在本机已不存在）＋东财 datacenter-web 翻页网络层。
### B-23 大宗交易两表单位定标＋深史回补至 2010（免费；表 c1_market.block_trade＋c1_market.block_trade_detail；申请方 ④席 st-qoder-p04-1015-03 楼8 普查＋p04-1015-06 第3条）

- 同票同日三方对拍（本班真跑，trade_date=2026-10-14，三票 000002/000425/000656）：本库 `block_trade`＝(price 3.67, volume **600000**, amount **2202000**, data_source=ifind)，与 akshare 东财 `stock_dzjy_mrmx` 原值逐位同（成交量 600000／成交额 2202000）；本库 `block_trade_detail`＝(volume **60**, amount **220.2**)，与 tushare `pro.block_trade` 原值逐位同（官方口径 vol=万股／amount=万元）。⇒ **④席"两表 avg(amount) 差 3–4 个数量级＝不同源"本班改判＝同源不同单位（恰 10^4）＋不同粒度（block_trade 逐笔／detail 按票日聚合）**。聚合证据＝000656 金科 detail 单行 volume 3550／amount 3656.5 恰等于 tushare 同日该票 6 笔之和（500+300+500+300+300+1650=3550；515+309+515+309+309+1699.5=3656.5）。
- 全表内部一致性（严格读 `query_rows` 只读）：`block_trade` **1706/1706** 行满足 amount==price×volume；`block_trade_detail` **1683/1878** 行满足（同单位下）⇒ **195 行（10.4%）不满足＝聚合行的 price 与 amount/volume 不同源**，本席不判因，转②定标。
- 深史可得性（既有 token、零采购，四断面真跑）：tushare `pro.block_trade(trade_date=)`＝20100111 **23 行**／20150105 **65 行**／20190104 **209 行**／20240815 **120 行**；akshare `stock_dzjy_mrtj`＝2010 窗 **109 行**／2019 窗 **562 行**（列自带 折溢率／成交总量(万股)／成交总额(万元)，官方 doc 载明"单次返回所有历史数据"）。⇒ **④席"大宗折价当前不可考"改判＝免费可回补至 2010-01-04，楼8 大宗折价轴门槛⑤（≥120 日）可达**；本库两表现盘按年实测**只有 2026 年**（block_trade 2026=1706、block_trade_detail 2026=1878，无更早年份）。
- 五门：成本 0｜合规＝交易所法定披露之公开汇编（本仓已有 ifind／tushare／akshare 三源先例）｜PIT＝大宗成交当日收盘后披露，trade_date 即知，无未来信息｜许可证＝akshare MIT＋tushare 用户协议，本席未外发、未验证再分发许可（与在册 tushare 同口径按内部研究用途）｜续供见下。
- **续供确认（SOP §3① 四问）**：①采集通道＝tushare `pro.block_trade(trade_date=)` 逐日循环（官方 doc_id=161：300 积分可调、单次最大 1000 条、总量不限）＋akshare `stock_dzjy_mrtj`（按票日聚合面，自带折溢率）；②更新频率＝交易日日频；③是否自动化＝**待②施工**（本席不建调度；tasks.yaml 现腿归属本席未查全量，只按本批实测陈述）；④断供风险＝tushare 积分档变更即断（同会话在册先例：`tdx_daily/tdx_index/tdx_member/ci_index_member` 权限墙）＋akshare 东财页面结构变更（在册 `macro_data_eastmoney_ssl_eof_chronic` 与本班同族形态）⇒ 双腿冗余可互校。
- 施工动作（②席）：(a) 两表 amount/volume 的**单位写进列注释与数据资产册**（block_trade=元/股；block_trade_detail=万元/万股），⑤实现禁跨表直接比大小或混算折价率；(b) 深史回补 2010-01-04 起，按 `data_source` 分轨打标（现表写者＝ifind，新腿＝tushare/akshare；混面会让接缝日读数失真——同族教训＝④席 p04-06 第9条 kline_index 跨源前值复制桩）；(c) detail 表 195 行不一致须先定标再入库；(d) 走 provider+BufferedWriter 正门＋交易日 gate。
- 验收判据：回补后 CH 现读 2010/2015/2019/2024 各代表日 rows 与本班源侧实测同量级（23/65/209/120 逐笔面）；两表单位注释 grep 得到；`abs(amount-price*volume)>5%` 行数＝0 或在册写明原因。
- 关联：本条与 B-13（margin_trading 深史）／B-14（dragon_tiger 深史）同属④席楼8 普查族，**三表对象不同不并**（AGENTS §4.1 跨域不同对象→不并）。

### B-24 北向持股 exchange 分层判据＋季断面可得时点（在册 `hk_connect_flow_hkex_disclosure_retirement` 的判据扩展；表 c1_market.northbound_hold_snapshot；申请方 ④席 st-qoder-p04-1015-06 第4条）

- 触发＝④席"northbound_hold_snapshot 8 个日期跨 21 个月、max=2026-06-30⇒右端落后约 3.5 个月；无 symbol/symbol_canonical 只有 ts_code⇒JOIN 键不统一"。本班自测面（非转述）：本表逐断面行数 2024-09-30=3,540／2024-12-31=3,602／2025-03-31=3,637／2025-06-30=3,788／2025-09-30=3,820／2025-12-31=4,014／2026-03-31=4,108／2026-06-30=4,440 ⇒ **八个全为季末日，无一个非季末断面**。
- 源侧分层实测（tushare `pro.hk_hold(trade_date=)` 按 exchange 分组，既有 token、零采购）：20190104＝2,538 行 {HK 564／SH 844／SZ 1,130}；20240816（政策生效前一交易日）＝4,128 行 {HK 791／SH 1,573／SZ 1,764}；**20240930（政策后首个季末）＝3,540 行 {SH 1,703／SZ 1,837／HK 0}**；20260630＝4,200 行 {HK 946／SH 2,039／SZ 1,215}；**20260930＝1,014 行 {HK 1,014／SH+SZ=0}**。单票直查 `hk_hold(ts_code='600519.SH', start_date=20260601, end_date=20261015)`＝**仅 1 行**（20260630，exchange=SH）。
- **判据一（正面答④席"是欠采还是未到披露时点"）＝本库右端 2026-06-30 与源同步，非欠采**：北向（SH/SZ）的 2026-09-30 断面源侧实测尚未发布（该日接口只回南向 HK）。官方锚＝上交所《关于沪港通交易信息披露机制调整相关事项的通知》**上证发〔2024〕106号**（2024-07-26 发布、**自 2024-08-19 起实施**）：沪股通每交易日收市后仅公布成交总额/总笔数/ETF成交总额/前十活跃名单，**单只证券北向投资者合计持有数量改为"每季度第五个沪股通交易日公布上季度末数据"**；深交所同日同构（港交所同步）。
- **判据二（本班新发雷，写给②⑤）＝政策后同一 trade_date 查询里混着两种频率×两个方向**：平日只回南向 HK（量级 792/1,014/1,018 行），季末才同时回 HK 与北向 SH/SZ。⇒ 取北向**必须** `exchange IN ('SH','SZ')` 且断面日=季末；若以"该日有无数据"判北向在供，会把南向当北向（本表 exchange 列在库，分层零成本）。
- **判据三（日频北向腿唯一可行窗）＝2017-03-16..2024-08-16**：akshare 东财个股北向持股 `stock_hsgt_individual_em` 真跑 600519＝**1,683 行，min 2017-03-16／max 2024-08-16**（按年 2017:188／2018:229／2019:234／2020:231／2021:230／2022:232／2023:191／2024:148），正对照 000001＝1,723 行、同一起止 ⇒ 右端**正好停在政策生效前一交易日**，与官方时点逐值互证。⇒ 若下游要日频北向腿，只能建 2017-03-16..2024-08-16 历史段（逐票调用）；**2024-08-19 起日频结构性不可得，禁按常设信号源准入**（按 SOP §3① 该段标注＝**一次性历史档案**，历史回补另案）。
- 键面（答④席后半）：本表列形制实测＝trade_date/ts_code/name/hold_share/hold_ratio/exchange/data_source/ingested_at（确无 symbol/symbol_canonical）⇒ 与裸 6 位 symbol 体系 JOIN 须经 ts_code 映射，落点归②，本席不代改。
- 五门：成本 0｜合规＝交易所官方披露之公开汇编｜PIT＝见判据一（可得时点=季后第 5 交易日；在册 `p01_probe_20261015d` 已写明最长约 1 个月前视，本席不重复立法）｜许可证＝tushare/akshare 同前口径未验证再分发｜续供＝季频可常设（在册 JOB-083），日频段属一次性。
- **续供确认（四问）**：①通道＝tushare `hk_hold`（季末断面，须按 exchange 分层）＋akshare `stock_hsgt_individual_em`（日频历史段，逐票）；②频率＝北向季频（每季第 5 个交易日）／南向 HK 日频；③自动化＝季频腿在册（JOB-083 `northbound_hold_snapshot_refresh`），日频历史段＝待②施工且一次性；④断供风险＝**披露机制已变更一次（政策级、无恢复预期）**⇒ 禁按日频建常设腿；季频腿风险＝tushare 积分档变更。
- 净零声明：本条**不新建 gaps 条目**，判据并条进在册 `hk_connect_flow_hkex_disclosure_retirement`（新键 `p01_probe_20261015l`）；日频历史段是否值得回补属 Owner/②门位，本席不裁。
