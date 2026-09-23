---
ttl: task_bound
sid: st-gpu-final-20260924
lane: e2e_integration
---

# 全景图健康快照（2026-09-24）

> 数据源：meta_question.meta_question / meta_question.meta_question_exam_result（PG 只读探针，经 get_depgraph_pg_connection）；TDM 真源=config\trading_decision_map.yaml。探针脚本=.runtime/tmp/gpu_final_20260924/panorama_health_probe.py；机读结果=同目录 panorama_health_snapshot.json。
> **结论（fail-closed）：全景图当前不可判绿。** 6/6 分组全红；TDM 182 节点仅 7 个有题覆盖且全红，175 节点零题覆盖=健康度不可验证；254 条边零题引用=边健康度不可评估。

## 一、统计总表

### 1.1 题目级最终判定（每题取最新一条 exam_result）

| 指标 | 值 |
|---|---|
| 题目总数 | 283 |
| 答题结果行数 | 285（distinct 题=283） |
| 绿（全部 pass 的组） | 0 |
| 红（有 fail 的组） | 6/6 |
| 黄（有 insufficient 的组） | 6/6（含于红） |
| 灰（有题未答完的组） | 0 |
| 最终判定 pass | 142（50%） |
| 最终判定 fail | 45（15%） |
| 最终判定 insufficient（证据不足，不计健康） | 96（33%） |
| 未答完（exam_result 缺失） | 0 |

### 1.2 按 graph_ref 分组（绿/黄/红/灰）

| graph_ref | 组色 | 题数 | pass | fail | insufficient | missing | 映射 TDM 节点（经 tags） |
|---|---|---|---|---|---|---|---|
| G1 | 红 | 4 | 0 | 2 | 2 | 0 | TDM-E-L0-04, TDM-E-L9-G1 |
| G2 | 红 | 3 | 1 | 2 | 0 | 0 | TDM-E-L9-G2 |
| G3 | 红 | 4 | 2 | 2 | 0 | 0 | TDM-E-L9-G3 |
| G4 | 红 | 4 | 0 | 1 | 3 | 0 | TDM-E-L4-14, TDM-E-L9-G4 |
| G5 | 红 | 3 | 0 | 1 | 2 | 0 | TDM-E-L9-G5 |
| UNGRAPHED | 红 | 265 | 139 | 37 | 89 | 0 | （未挂图） |
| 合计 | — | 283 | 142 | 45 | 96 | 0 | 覆盖 7 节点 |

### 1.3 TDM 全景图侧

| 指标 | 值 |
|---|---|
| 节点总数 | 182 |
| 边总数 | 254 |
| 有题覆盖节点 | 7（色分布：红=7） |
| 零题覆盖节点 | 175（96%）=健康度不可验证，禁判绿 |
| 边健康度 | NOT_EVALUABLE（graph_ref 零边引用） |

## 二、结构级红旗（任务假设核对，fail-closed）

1. graph_ref 零边引用（任务假设的'边引用'形态不存在）：TDM 边健康度不可评估，禁判绿
2. 任务假设'graph_ref=形如 TDM-xxx'不成立：实测仅 G1-G5 组引用（18/283 题挂图），G* 经 TDM tags 映射到节点；任务所述 docs/01_policies_and_standards/trading_decision_map.yaml 路径不存在，真源=config/trading_decision_map.yaml
3. 复考降级在案：PQ-0032 由 pass 复考降为 insufficient；PQ-0033 由 insufficient 复考降为 fail（快照一律取最新判定）。探针运行期间 exam_result 行数 284→285，表在被活跃写入，本快照为时点值。

## 三、红段逐条清单（45 条 fail）

fail_type 分布：no_alpha=31（无alpha，策略证伪）、infra=14（机制未建成）。

| 题号 | graph_ref | fail_type | fail 原因摘要 |
|---|---|---|---|
| PQ-0004 | UNGRAPHED | infra | fail(infra)：degraded_check 事件占 register 事件比例 = 283/283 = 100% ≠ 0，threshold '=0' 不过。归因实证：283 条 degraded_check  |
| PQ-0011 | UNGRAPHED | no_alpha | 30 分钟 bar MA20 斜率因子（T 日末根 15:00 戳 bar 落定，slope=MA20/MA20_前5根-1）对次日开盘后 30 分钟收益（T+1 首根 10:00 戳 bar，ret=close1/op |
| PQ-0012 | UNGRAPHED | infra | 复权因子对齐链路抽检违例率≠0，fail（infra）。月度抽样 50 只×56 个月（2021-01~2025-08，闭卷窗），三表 JOIN 复算 53,134 个（symbol,日）点：按每股常数基座 k 检验 h |
| PQ-0015 | UNGRAPHED | no_alpha | fail(no_alpha)：财联社电报 30 分钟滚动密度事件研究在闭卷窗内无预测力。取 c3_fundamental.news_data source='财联社'（full_publish_time 含分钟级时戳）， |
| PQ-0017 | UNGRAPHED | no_alpha | fail(no_alpha)：上游价格冲击×ig_io_edge 直接消耗系数加权的传导信号对下游行业 20 日收益无正向预测力。实现：IO 部门经确定性关键词映射到申万一级（147 部门映射 127 个，非自身系数质量 |
| PQ-0018 | UNGRAPHED | infra | 两套板块口径成分重合率远低于 80%，fail（infra）。ig_node_company live（valid_to IS NULL）4,742 节点/8,254 条成员边；名称匹配（精确 12+包含 286）到 T |
| PQ-0023 | UNGRAPHED | no_alpha | fail(no_alpha)：EP(1/PE) 十分位月频分组回测（2015-01-30~2025-08-29 共 128 个月末截面，月均 2377 只，月末 T 分组、收益窗 T+1~次月末，等权）测得多空差（D10 |
| PQ-0024 | UNGRAPHED | no_alpha | 同窗双口径对照：IC 差=−0.0369<0，threshold ≥0 不满足，fail（no_alpha 型——但注意非典型：PIT 口径因子自身有正预测力，失败根源=未对齐口径的前视泄漏膨胀）。55 个信号月（202 |
| PQ-0028 | UNGRAPHED | no_alpha | fail(no_alpha)：户均持股市值分位因子的月频 IC 预设方向（IC>0.02 且 t>2）不成立，实际显著为负。因子=（balance_sheet.total_shares 按 announce_date P |
| PQ-0029 | UNGRAPHED | no_alpha | fail(no_alpha)：Hyperliquid 永续资金费率极值日后 3 日 A 股情绪代理指标未见显著回落，跨市场传导假设不成立。样本：hl_funding_history 切点前 851 个日度聚合日（2023 |
| PQ-0031 | UNGRAPHED | no_alpha | 因子构造：沪深300日收盘，趋势态 S=1 当且仅当 close>MA20 且 close>MA60 且 MA20斜率(MA20_t-MA20_{t-5})>0，否则 S=0；月末取态→月度转移矩阵，60个月滚动窗×bo |
| PQ-0033 | UNGRAPHED | no_alpha | 【三轮复核实证改判 insufficient→fail(no_alpha)】复核推翻原『三序列切点前不存在』前提：macro_data 以 FRED_* 英文命名在库（FRED_DGS10_US/FRED_DXY/FRE |
| PQ-0037 | UNGRAPHED | no_alpha | 因子构造：emotion_index(close_final 多源合成情绪，1991 起) 2023-01-01 起，trailing 250 日分位>95% 记极端情绪日；反转收益=中证全指 T+1 收盘→T+6 收盘 |
| PQ-0039 | UNGRAPHED | no_alpha | 因子构造：kline_sector_880 各板块(code) 收盘 20 交易日动量，月末截面排名，相邻月末 Spearman 秩自相关，要求公共板块≥50。共 37 个月度对（≥36 满足），平均 ρ=0.1207， |
| PQ-0046 | UNGRAPHED | no_alpha | 事件研究(路线A): 上证指数 000001, 20日已实现波动扩张历史分位迟滞状态(>=0.70高/<=0.30低), 低->高切换事件 n=18 (窗口 2006-02-06 ~ 2025-05-08), T+1收盘 |
| PQ-0047 | UNGRAPHED | no_alpha | 事件复盘(路线A): 全A(剔除pe<=0, 每日>=200只, 2599个交易日, 2015-01-05~2025-09-09) 中位数PE 的滚动756日(约3年)分位上穿80%触发, 主口径触发 n=8 次; 命中 |
| PQ-0048 | UNGRAPHED | no_alpha | 费率极值事件研究(路线A): hl_funding_history 206币种, 全窗 2023-05-12~2025-09-08 共851个UTC日; 极值=/日中位费率/>=95分位(0.00009/8h), 去重后 |
| PQ-0062 | UNGRAPHED | infra | fail(infra)：双轨对账单侧缺轨。JSONL 审计账 meta_question_audit.jsonl 全仓零命中（git ls-files 跟踪文件+磁盘递归扫描均 0）；PG 审计表 849 行且全部落在  |
| PQ-0064 | G1 | infra | 873 链中 871 链有节点（2 链零节点）。按全节点口径，节点→公司映射覆盖率≥80% 的 A 档链=288/871=33.07%，远低于 A 档链占比≥80% 阈值；剔除 2225 个'已并入'合并污染节点后的活跃 |
| PQ-0065 | G1 | no_alpha | CKG 2021 产品-产品边（ig_fact supplies_to+product_downstream_of，归一化后 56,978 对）与研报线抽取边（ig_edge 1,650 条非 ckg 来源边，归一化节点 |
| PQ-0067 | G2 | infra | CKG 2021 supplies_to（57,069 条事件）沿 subtype_of/sector_parent_of 树向上聚合后仅得 240 个行业对（56,800 条事件的产品名爬不到行业节点，可映射率 0.5 |
| PQ-0068 | G2 | infra | ig_fact 中 CKG 产品-产品边共 57,459 条（supplies_to 57,069 + product_downstream_of 390，按事件计），产品名消歧对齐到 ig_node 词表（name+去 |
| PQ-0071 | G3 | no_alpha | 两口径边集分层回归（y=对收益相关，2024-09~2025-09 共 250 交易日，控制=同 CKG 行业哑变量；对照=同池随机非关联对 60,000）。切点内十大股东口径现行对 194,008 行，派生可测上市-上 |
| PQ-0072 | G3 | infra | 质押公告事件（equity_pledge_detail，公告日≤2025-09-09 共 112,822 条/3,508 只，公告窗 2003-06-10~2025-09-09）与 edge_holding 股权边版本比 |
| PQ-0074 | G4 | no_alpha | Jaccard 置换检验（numpy 随机 1000 次，随机种子 20250909）：stock_concept 概念（≥3 家成分的 374 个概念，61,053 行/5,210 只）对 ig_node_compan |
| PQ-0078 | G5 | infra | ig_io_edge 16,859 条边 100% 挂零实锤：information_schema 实证该表无任何 node 挂接字段（列=from_sector_code/from_sector/to_sector_c |
| PQ-0081 | UNGRAPHED | no_alpha | 因子构造：沪深300 日对数收益 20 日滚动标准差=已实现波动 RV20，其 trailing 250 日分位∈[0,1] 为波动分位状态；AR(1) 回归 p_t=c+φ·p_{t-1}+ε，半衰期=ln(0.5)/ |
| PQ-0082 | UNGRAPHED | no_alpha | 因子构造：全A(kline_daily A_share) 逐日涨/跌家数比 B=adv/(adv+dec)，B5/B20 均线交叉为宽度拐点信号（金叉=看多/死叉=看空）；均线状态=沪深300 close>MA20，状态 |
| PQ-0088 | UNGRAPHED | no_alpha | 因子构造：shareholder_count 按 announce_date（公告日 PIT），每月末对每只取最近两期股东户数，户数下降家数占比=筹码情绪变量 x_m；IC=Spearman(x_m, 沪深300 月末后 |
| PQ-0091 | UNGRAPHED | no_alpha | 有/无择时对比回测(路线A): 动量因子=后复权收盘20日动量、5日再平衡、上下20%等权LS (kline_daily_hfq 7120264行, 个股覆盖2019年起, 有效再平衡320次); 情绪极值=emotio |
| PQ-0092 | UNGRAPHED | no_alpha | 事件研究(路线A): ig_io_edge(2020年表) 上游 006煤炭/007油气/009有色矿采 各取 coefficient 前12 下游边, 可映射到在库行业指数的边: 电力热力/燃气->000007公用,  |
| PQ-0099 | UNGRAPHED | infra | fail(infra)：状态分布双条件破线。全表 283 问状态分布：registered=283（100%），answered=0（0.0%，健康带要求 30-70% → 不过）；单状态最大占比=registered  |
| PQ-0102 | UNGRAPHED | infra | fail(infra)：与 PQ-0062 同一双轨缺口（第三道对账线）。JSONL 审计账全仓零命中（find+git ls-files 双重实证），PG 审计表 849 行（2026-09-23 单日）→ 当日差=8 |
| PQ-0110 | UNGRAPHED | no_alpha | 均线斜率+20日突破合成信号（sign(MA20/MA20_5日前-1)+1{close_adj>20日前高}）对全 A 池 1 日前瞻收益（raw x adj_factor 自算 hfq，close-to-close） |
| PQ-0111 | UNGRAPHED | no_alpha | 均线斜率+20日突破合成信号（sign(MA20/MA20_5日前-1)+1{close_adj>20日前高}）对全 A 池 5 日前瞻收益（raw x adj_factor 自算 hfq，close-to-close） |
| PQ-0112 | UNGRAPHED | no_alpha | 均线斜率+20日突破合成信号（sign(MA20/MA20_5日前-1)+1{close_adj>20日前高}）对全 A 池 20 日前瞻收益（raw x adj_factor 自算 hfq，close-to-close |
| PQ-0113 | UNGRAPHED | no_alpha | 尾盘主买净额占比信号（真尾盘 14:30-15:00，(主买额-主卖额)/总成交额，T 日收盘落定）对全 A 池 1 日前瞻收益（raw x adj_factor 自算 hfq）的逐日截面秩 IC：IC=-0.02776 |
| PQ-0114 | UNGRAPHED | no_alpha | 尾盘主买净额占比信号（真尾盘 14:30-15:00，(主买额-主卖额)/总成交额，T 日收盘落定）对全 A 池 5 日前瞻收益（raw x adj_factor 自算 hfq）的逐日截面秩 IC：IC=-0.01385 |
| PQ-0115 | UNGRAPHED | no_alpha | 尾盘主买净额占比信号（真尾盘 14:30-15:00，(主买额-主卖额)/总成交额，T 日收盘落定）对全 A 池 20 日前瞻收益（raw x adj_factor 自算 hfq）的逐日截面秩 IC：IC=-0.0063 |
| PQ-0122 | UNGRAPHED | no_alpha | fail(no_alpha)：业绩超预期（营收同比增速二阶差分>0，按 ann_date PIT 取『截至 T 日最新一期已公告值』作为持续截面因子）在全 A 池对 1 日前瞻收益的日频秩 IC=0.00548，虽统计显 |
| PQ-0123 | UNGRAPHED | no_alpha | fail(no_alpha)：业绩超预期持续因子（营收增速二阶差分>0，ann_date PIT 前向填充）对 5 日前瞻收益的日频秩 IC=0.0094<0.02（NW t(lag=5)=5.295>2 显著；样本外  |
| PQ-0124 | UNGRAPHED | no_alpha | fail(no_alpha)：业绩超预期持续因子（营收增速二阶差分>0，ann_date PIT 前向填充）对 20 日前瞻收益的日频秩 IC=0.0147<0.02（NW t(lag=20)=4.365>2 显著；样本 |
| PQ-0131 | UNGRAPHED | infra | U4 口径下同链路抽样审计（月度 30 条）违例样本≠0，fail（infra）。与 PQ-0012 同批数据：56 个月×50 只抽样中按每月前 30 只取子集口径，违例点全域 24,130/53,134（45.4%） |
| PQ-0172 | UNGRAPHED | infra | SL-A08 U3'日更（交易日）'核验为 fail(infra)：BDI 主序列日更合规（1988-10-19 起 13745 行切点前数据；2020-2025 年内 >7 天间隔仅 4 次且全部为元旦/春节假期 9~ |
| PQ-0196 | UNGRAPHED | infra | SL-A12 U3'实时/小时级'与 DS 册健康检查口径不一致，不一致项=1，判 fail(infra)：DS 册明确登记'免费版 1000 次/天'+note '每日积累'，库内实测为每日单批采（30 个 inges |

## 四、黄段逐条清单（96 条 insufficient，证据不足不计健康）

| 题号 | graph_ref | 不足原因摘要 |
|---|---|---|
| PQ-0001 | UNGRAPHED | W6 挖干注册批（actor=st-chainpile-20260922，2026-09-23 02:30-02:31 落账 register 283 条，对应 01_campaign_directi |
| PQ-0013 | UNGRAPHED | insufficient：合成强度分位的两个组件在闭卷窗（<=2025-09-09）内均无数据。组件A『板块新高家数占比』需板块→个股 PIT 成分映射，而全部映射表切点前为零行（sector_con |
| PQ-0014 | UNGRAPHED | insufficient：概念成分快照按日存证机制在闭卷窗内不存在。实测 sector_constituent_snapshot 全表仅 2026-09-14/15 两个快照日（各 95,124 行， |
| PQ-0016 | UNGRAPHED | insufficient：切点前不存在任何可用的新闻情绪分数据，'按发布时戳 PIT 计算的日度情感分位'序列无法构建，回归（HAC t 检验）无法执行。三处独立实证：(1) c3_fundament |
| PQ-0019 | UNGRAPHED | 开盘集合竞价买卖队列失衡度因子无法在闭卷窗构造：auction_book 与 auction_snapshot（以及 tick_depth_5）切点前样本数为 0（实证 count()=0，min/m |
| PQ-0025 | UNGRAPHED | 事件研究 t>2 需切点前主力净流入数据，闭卷窗内零样本无法执行，禁硬答。　闭卷窗内零样本：c1_market.money_flow 仅 2026-06-01 起（533,575 行）、sector_ |
| PQ-0026 | UNGRAPHED | Chow 断点检验需跨口径版本的历史主力净流入序列，闭卷窗内零样本；且切点后单版本数据无法构造版本切换断点。　闭卷窗内零样本：c1_market.money_flow 仅 2026-06-01 起（5 |
| PQ-0030 | UNGRAPHED | insufficient：清算量因子在闭卷窗内零样本，IC 无法计算。c1_market.hl_liquidation_raw 全表仅 5 行，trade_time 最小值 2026-09-18 03 |
| PQ-0032 | UNGRAPHED | 【复核实证改判 pass→insufficient】独立复核（verify_PQ-0032 系列探针，40+ 口径变体系统扫描）发现：均值回归方向在全部变体下稳定复现（高分位组 20 日收益差恒<0） |
| PQ-0034 | UNGRAPHED | insufficient：清算量数据切点前零样本——hl_liquidation_raw 切点前 0 行（全表 2026-09-18 起、仅 5 行心跳），hl_perp_snapshot_daily |
| PQ-0035 | UNGRAPHED | insufficient：双源在切点前均零样本——快讯情感源 news_sentiment_window 切点前 0 行（window_date 2026-02-24~2026-09-22）；散户关注 |
| PQ-0036 | UNGRAPHED | insufficient：两序列切点前均零样本——主力净流入 money_flow 切点前 0 行（2026-06 起），market_fund_flow_daily 切点前 0 行（2026-03- |
| PQ-0038 | UNGRAPHED | insufficient：千股千评源 alt_stock_comment（综合得分 composite_score/评级家数 org_participation）切点前 0 行（2026-09-11  |
| PQ-0040 | UNGRAPHED | insufficient：板块资金净流入 CR5 的分子数据切点前缺失——个股级 money_flow 切点前 0 行（2026-06 起）、板块级 sector_fund_flow 切点前 0 行（ |
| PQ-0041 | UNGRAPHED | insufficient：三要素均缺切点前数据——①互动易 irm_interactive_qa 切点前 0 行（question_date 2026-06-19 起，全表 500 行）；②快讯实体提 |
| PQ-0042 | UNGRAPHED | insufficient：天气事件源切点前缺失——weather_data（QWeather 40 城观测）切点前 0 行（record_date 2026-08-04 起）；exam_plan 引用 |
| PQ-0043 | UNGRAPHED | 风险预算仓位规则的实测回测样本为零: alloc_budget_daily 全量仅16行(2026-09-15~2026-09-22), alloc_shrinkage_daily 8行, decis |
| PQ-0044 | UNGRAPHED | 入库闸载体 c1_backtest.strategy_screen 全量 1340 行, ingest_ts 范围 2026-09-12 11:29:11.015000+00:00~2026-09-2 |
| PQ-0045 | UNGRAPHED | 双信号中'资金流'腿在闭卷窗内零样本: c1_market.money_flow 切点前 0 行(全量 533575 行, min=2026-06-01 在切点后), sector_fund_flow |
| PQ-0049 | UNGRAPHED | 审计对象不完整+零样本: ①'单因子组合权重上限15%'约束在代码中未定位——pf_alloc/position 全模块 0.15 命中均为异义常量(MaxDD 阈值/目标波动/成交量参与率), 组合 |
| PQ-0050 | UNGRAPHED | 审计对象不存在: ①'源线 PIT 风险升级事件'无运行时事件账——PG public 74 张表中事件类载体仅 domain_events(112 行, 列=event_id,name,source |
| PQ-0051 | UNGRAPHED | in_exam 及以后状态（in_exam/answered/reexam/suspended/merged/retired）问题=0 行（全表 283 问全部 registered，meta_que |
| PQ-0052 | UNGRAPHED | 审计对象'GPU 周五窗口 IBT 修卷任务账'不存在：meta_question_exam_result 0 行（考试循环从未运行），meta_question_audit 的 what CHECK |
| PQ-0053 | UNGRAPHED | 焊成本滑点偏差校准零合规样本：c1_backtest.sim_trade_log 总量 66 行，其中 trade_date <= '2025-09-09'（PIT 切点）的行=0，成交全部落在 20 |
| PQ-0054 | UNGRAPHED | 到期复考执行率无样本：全表 283 问无任何 answered 状态（全部 registered），meta_question_exam_result 0 行，回填唯一合法入口 writeback(q |
| PQ-0055 | UNGRAPHED | 考试记录 data_window 机检零对象：meta_question_exam_result 0 行（考试循环从未运行，283 问全部 registered），无任何考试窗口可做'样本外份额≥1/ |
| PQ-0056 | UNGRAPHED | exam_writeback 落账时延 P99 无样本：audit what 枚举含 exam_writeback 值但 849 条已落账事件中 exam_writeback=0；writeback  |
| PQ-0057 | UNGRAPHED | 三取二多数裁定零样本：reexam 状态问题=0（283 全 registered），exam_result 中 outcome='reexam' 记录=0（表 0 行），audit 账 exam_a |
| PQ-0060 | UNGRAPHED | illegal_transition 事件类型在 audit 表 CHECK 枚举（23 值实证：register/update/merge/retire/reexam/suspend/templat |
| PQ-0061 | UNGRAPHED | 乐观锁冲突样本=0：meta_question 有 version 整型列（NOT NULL）但 audit 表无 version 字段、what 枚举 23 值中无 VersionConflict/ |
| PQ-0063 | G1 | 三查不过，禁硬答：①响应侧缺失——'下游行业 20 日毛利变化'无可构造载体：c3_fundamental.financial_indicator.gross_margin 在库（319,394 非空 |
| PQ-0066 | G1 | 消歧桥 ig_entity_code_map 仅 88 行/87 个 master_id，对 ig_fact 264,072 条事实（distinct subject 100,421 + distin |
| PQ-0075 | G4 | 三查拦截：月度趋势斜率需要月度快照序列，两源均只有单一时点快照——①THS 侧：stock_concept 仅 source='ths_export' 单一 as_of=2026-09-14（61,0 |
| PQ-0076 | G4 | 三查拦截，闭卷窗内三要素全部缺样本：①快讯实体提及——c3_fundamental.news_data 切点前 7,887,387 行（2010-01-02~2025-09-09）但 related_ |
| PQ-0077 | G4 | 三查拦截：误杀率（被过滤标签中真概念占比）的审计对象不存在——①装载拒绝日志未留档：concept_ingest.py 的 MARKET_TAG 正则过滤对被过滤标签静默 continue，不写任何  |
| PQ-0079 | G5 | 三查拦截：ig_company_edge（58,207 行）不存在 confidence 字段——information_schema.columns 实证 27 列中无 confidence（近义候 |
| PQ-0080 | G5 | 三查拦截：ig_io_edge 在库仅 2020 一个年份版本（year 分布 {2020: 16,859}，as_of 全为 2020-12-31，source 全为 io_official），20 |
| PQ-0083 | UNGRAPHED | insufficient：主数据缺失——千股千评得分横截面离散度需 alt_stock_comment（composite_score），切点前 0 行（2026-09-11 起）；且题面'情绪极值后 |
| PQ-0084 | UNGRAPHED | insufficient：双源切点前均零样本——主力净流入（money_flow 2026-06 起，切点前 0 行；market_fund_flow_daily 2026-03 起，切点前 0 行） |
| PQ-0085 | UNGRAPHED | insufficient：'板块新高家数占比'需股票↔板块成分映射，全部映射源切点前为 0 行/2026 快照——industry_class（updated_at 2026-08 起）、sector |
| PQ-0086 | UNGRAPHED | insufficient：概念热度排名数据源缺切点前样本——互动易问答（irm_interactive_qa 2026-06 起）与快讯实体提及热度（管线 2026-02 起）切点前均 0 行，概念热 |
| PQ-0089 | UNGRAPHED | 波动率倒数加权(inverse-vol)风险预算规则的样本外回测样本为零: alloc_budget_daily 全量16行(2026-09-15~2026-09-22), decision_dail |
| PQ-0090 | UNGRAPHED | IR 贡献归因所需的决策/交易/归因账全部为切点后记录: decision_daily 全量 69 行(2026-09-16~2026-09-24), sim_trade_log 66 行, sim_ |
| PQ-0093 | UNGRAPHED | L5 证伪载体 node_verdict 全量 58 行(ingest 2026-09-11 23:06:10.072000+00:00~2026-09-17 17:54:10.609000+00:0 |
| PQ-0094 | UNGRAPHED | 代码审计(只读): pf_alloc 裁决中心(allocation_orchestrator.py)存在标的层单票硬上限——cap=min(策略层,最终硬限)=5%(较题面 10% 更严, 违例标签 |
| PQ-0095 | UNGRAPHED | 模板族字段不存在：meta_question 表无 tpl/template_id 列（information_schema.columns 实证 COLUMN_NOT_EXIST，25 列全量枚举核 |
| PQ-0096 | UNGRAPHED | PIT 抽检零对象：抽样比对需考试记录的取数时戳与决策时戳，meta_question_exam_result 0 行（考试循环从未运行），每周 20 条抽样无样本可抽，违例数无法统计（0 记录 ≠  |
| PQ-0097 | UNGRAPHED | GPU 周五硬前置三件（IBT 修卷/焊成本校准/新鲜窗重考）的任务账均不存在：exam_result 0 行、audit 无任务类事件（枚举实证）、三件对应的调度代码全仓零实现。整体周五完成率与连续 |
| PQ-0098 | UNGRAPHED | IC 类考试 0 场（exam_result 0 行）：功效无法按实际样本量×效应量计算；'降阈值事件'在 audit 枚举 23 值中无对应事件类型、零落账，降阈值=0 无法与'从未发生'区分。现状 |
| PQ-0103 | UNGRAPHED | claim_mismatch 事件类型在 audit 表 CHECK 枚举（23 值实证）中不存在，849 条已落账事件零越权尝试记录；回写鉴权（claimed_by==调用会话，13_exam_ba |
| PQ-0104 | UNGRAPHED | 审计对象(space_hash 预注册空间台账/批 manifest/N_eff 估计账)不存在: PG public 无 %space%/%manifest%/%combin%/%e1c% 表(命中 |
| PQ-0105 | UNGRAPHED | E1C 三轨同空间同考尺的产出账不存在: ①三轨标识未落库——hypothesis_precheck.birth_channel 现值 {'B': 15, 'D': 15, 'C': 10, 'I': |
| PQ-0106 | UNGRAPHED | 合并闸机制在产但口径不一致且无运行账: ①代码阈值——strategy_correlation_gate.py 为 Pearson 相关 reject=0.85/hard_reject=0.90+尾部 |
| PQ-0107 | UNGRAPHED | E1C 三轨统一考尺配置快照不存在：exam_plan 仅 method/criterion/threshold 自由文本键，无结构化考尺字段（IC>0.02/t>2/扣费多空年化>3%/样本外份额≥ |
| PQ-0108 | UNGRAPHED | 新鲜窗重考队列不存在：全表 0 条 answered（283 全 registered，无到期重考对象）、exam_result 0 行、重考到期/逾期记录零落账。月度滚动 20 日新鲜窗的逾期率分母 |
| PQ-0109 | UNGRAPHED | space_hash 台账(登记/扩容/封存流水)不存在: PG public 无 %space%/%seal%/%expand%/%manifest%/%e1c% 表(命中=[]); registr |
| PQ-0116 | UNGRAPHED | insufficient：『板块涨幅排名前十分位成分股跟随信号』= 板块动量排名（可算：kline_sector_880 闭卷窗内 322995 行/462 板块，2020-03-17~2025-09 |
| PQ-0117 | UNGRAPHED | insufficient：『板块涨幅排名前十分位成分股跟随信号』= 板块动量排名（可算：kline_sector_880 闭卷窗内 322995 行/462 板块，2020-03-17~2025-09 |
| PQ-0118 | UNGRAPHED | insufficient：『板块涨幅排名前十分位成分股跟随信号』= 板块动量排名（可算：kline_sector_880 闭卷窗内 322995 行/462 板块，2020-03-17~2025-09 |
| PQ-0125 | UNGRAPHED | 1 日前瞻 IC 需切点前全A 主力净流入占比截面，闭卷窗内零样本。　闭卷窗内零样本：c1_market.money_flow 仅 2026-06-01 起（533,575 行）、sector_fun |
| PQ-0126 | UNGRAPHED | 5 日前瞻 IC 同上，闭卷窗内零样本。　闭卷窗内零样本：c1_market.money_flow 仅 2026-06-01 起（533,575 行）、sector_fund_flow 2026-09 |
| PQ-0127 | UNGRAPHED | 20 日前瞻 IC 同上，闭卷窗内零样本。　闭卷窗内零样本：c1_market.money_flow 仅 2026-06-01 起（533,575 行）、sector_fund_flow 2026-0 |
| PQ-0139 | UNGRAPHED | SL-A02 U6 退役证伪方案（模拟成交 vs 实盘成交回执对比；证伪=tick 级信号无增量信息）当前不可重放：对比对象缺失——实盘回执表 c1_market.execution_report 切 |
| PQ-0143 | UNGRAPHED | insufficient：审计对象（概念成分按日存证管线）在闭卷窗内不存在。sector_constituent_snapshot 全表仅 2026-09-14/15 两日（95,124 行/日），闭 |
| PQ-0161 | UNGRAPHED | U4 口径版本存证审计：存证载体未建（库内无口径版本标记字段/表），且现有数据全为切点后单一版本，无历史版本切换可审计。 |
| PQ-0163 | UNGRAPHED | U6 退役判据（净流入极端日事件研究无显著超额即退役）判据文本可代码化（事件定义/超额口径/显著性检验三要素齐），但闭卷窗内零样本无法真实重放执行，按同批 U6 先例（PQ-0139/0181）记 i |
| PQ-0167 | UNGRAPHED | SL-A07 U4 审计对象（快照时点存证+不回填的入库执行记录）在闭卷窗内为零样本：alt_stock_comment 表起点 2026-09-11，trade_date<='2025-09-09' |
| PQ-0169 | UNGRAPHED | SL-A07 U6 退役判据（得分变化分组收益差检验；证伪=无领先性）当前不可重放：信号数据 alt_stock_comment 切点前 0 行（表起点 2026-09-11），'历史重放演练'无样本 |
| PQ-0181 | UNGRAPHED | insufficient：SL-A09 U6 退役判据（'情绪分位 vs 次日收益回归+极端情绪日事件研究；证伪=预测力不显著'）口径本身可代码化（回归+事件研究+t>2 均可机械执行，兄弟问 PQ- |
| PQ-0185 | UNGRAPHED | SL-A10 U4'vintage 初值/修正值修订风险被发布快照入库存证100%对冲'审计对象在闭卷窗内为零样本：FRED_ 全部行的 ingest_ts ∈ [2026-08-13, 2026-0 |
| PQ-0191 | UNGRAPHED | SL-A11 U4'周度值后续修订风险被按发布时戳 PIT 取数100%对冲'审计对象在闭卷窗内为零样本：EIA_ 全部行 ingest_ts ∈ [2026-08-13, 2026-09-20]，切 |
| PQ-0193 | UNGRAPHED | SL-A11 U6 退役判据'库存意外项对油价事件窗回归'当前不可按登记口径机械执行：核心回归子'库存意外项'=实际-预期，而预期基线源未登记——c1_market.calendar_event 无任 |
| PQ-0197 | UNGRAPHED | SL-A12 U4'预报滚动修订风险被预报值与实现值分字段存证100%对冲'审计对象在闭卷窗内为零样本：weather_data 表起点 2026-08-04，切点前 0 行，月度 30 条抽样无从执 |
| PQ-0199 | UNGRAPHED | SL-A12 U6 退役判据（天气冲击日板块事件研究；证伪=无异常收益）当前不可重放：天气信号切点前 0 行（表起点 2026-08-04），'历史重放演练'无样本可跑。文本审阅另有两处登记债：①'天 |
| PQ-0209 | UNGRAPHED | SL-A14 U4'问答内容编辑撤回风险被原文快照落 G 盘冷库并携 snapshot_path100%对冲'审计对象在闭卷窗内为零样本：切点前 answer_date/question_date 行 |
| PQ-0211 | UNGRAPHED | SL-A14 U6 退役判据（题材关键词命中后 N 日超额收益；证伪=无事件窗效应）当前不可重放：问答事件切点前 0 行（answer_date 起点 2026-08-25 且 500 行全部切点后装 |
| PQ-0227 | UNGRAPHED | SL-B01 卫星影像线 U4 PIT 控制执行审计：登记文本已含风险与对冲方案（『中——影像不可改，但解译算法版本改写历史估值，须冻结算法版本号』），但 B 档管线未建、入库链路不存在，抽样审计（月 |
| PQ-0228 | UNGRAPHED | SL-B01 卫星影像线 U5 消费方挂接核验：源线谱已登记消费方意图（『L3 板块（能源/零售）/ L2』）与层宪章七层词表相容，但 B 档未落库未挂线，层宪章/七层挂载表无该线实际挂接记录可对（挂 |
| PQ-0233 | UNGRAPHED | SL-B02 美国官方天气/海洋线 U4 PIT 控制执行审计：登记文本已含风险与对冲方案（『高（实测/警报不可改）；预报滚动修订须分版存』），但 B 档管线未建、入库链路不存在，抽样审计（月度 30 |
| PQ-0234 | UNGRAPHED | SL-B02 美国官方天气/海洋线 U5 消费方挂接核验：源线谱已登记消费方意图（『L3 板块（能源/农业）/ L4』）与层宪章七层词表相容，但 B 档未落库未挂线，层宪章/七层挂载表无该线实际挂接记 |
| PQ-0239 | UNGRAPHED | SL-B03 招聘 JD 线 U4 PIT 控制执行审计：登记文本已含风险与对冲方案（『中——JD 会下架改写，须即时快照存证；站点改版破坏口径连续性』），但 B 档管线未建、入库链路不存在，抽样审计 |
| PQ-0240 | UNGRAPHED | SL-B03 招聘 JD 线 U5 消费方挂接核验：源线谱已登记消费方意图（『L2（企业节点景气证据）/ L3 板块』）与层宪章七层词表相容，但 B 档未落库未挂线，层宪章/七层挂载表无该线实际挂接记 |
| PQ-0245 | UNGRAPHED | SL-B04 电商价格线 U4 PIT 控制执行审计：登记文本已含风险与对冲方案（『高（价格史平台侧不可改）；但排名口径随平台算法变』），但 B 档管线未建、入库链路不存在，抽样审计（月度 30 条） |
| PQ-0246 | UNGRAPHED | SL-B04 电商价格线 U5 消费方挂接核验：源线谱已登记消费方意图（『L3（消费景气）/ L4』）与层宪章七层词表相容，但 B 档未落库未挂线，层宪章/七层挂载表无该线实际挂接记录可对（挂载经 l |
| PQ-0251 | UNGRAPHED | SL-B05 招投标线 U4 PIT 控制执行审计：登记文本已含风险与对冲方案（『高——公告不可改，更正另发新公告须关联去重』），但 B 档管线未建、入库链路不存在，抽样审计（月度 30 条）无审计对 |
| PQ-0252 | UNGRAPHED | SL-B05 招投标线 U5 消费方挂接核验：源线谱已登记消费方意图（『L2（企业-订单边）/ L4』）与层宪章七层词表相容，但 B 档未落库未挂线，层宪章/七层挂载表无该线实际挂接记录可对（挂载经  |
| PQ-0257 | UNGRAPHED | SL-B06 社媒舆情 X/Reddit 线 U4 PIT 控制执行审计：登记文本已含风险与对冲方案（『中——删帖/封号致历史不可复现，必须即时落库存证』），但 B 档管线未建、入库链路不存在，抽样审 |
| PQ-0258 | UNGRAPHED | SL-B06 社媒舆情 X/Reddit 线 U5 消费方挂接核验：源线谱已登记消费方意图（『L3 情绪 / L4』）与层宪章七层词表相容，但 B 档未落库未挂线，层宪章/七层挂载表无该线实际挂接记录 |
| PQ-0263 | UNGRAPHED | SL-B07 雪球/股吧散户情绪线 U4 PIT 控制执行审计：登记文本已含风险与对冲方案（『中——删帖常见，即时快照落库是 PIT 前提』），但 B 档管线未建、入库链路不存在，抽样审计（月度 30 |
| PQ-0264 | UNGRAPHED | SL-B07 雪球/股吧散户情绪线 U5 消费方挂接核验：源线谱已登记消费方意图（『L3 情绪变量（与 SL-A09 互证双源）』）与层宪章七层词表相容，但 B 档未落库未挂线，层宪章/七层挂载表无该 |
| PQ-0269 | UNGRAPHED | SL-B08 APP 榜单线 U4 PIT 控制执行审计：登记文本已含风险与对冲方案（『中——下载量是平台估算非官方数，估算算法会调』），但 B 档管线未建、入库链路不存在，抽样审计（月度 30 条） |
| PQ-0270 | UNGRAPHED | SL-B08 APP 榜单线 U5 消费方挂接核验：源线谱已登记消费方意图（『L2（公司节点运营证据）/ L4』）与层宪章七层词表相容，但 B 档未落库未挂线，层宪章/七层挂载表无该线实际挂接记录可对 |
| PQ-0275 | UNGRAPHED | SL-B09 进出口贸易线 U4 PIT 控制执行审计：登记文本已含风险与对冲方案（『中高——月度数据有修订；HS 编码版次切换须对齐映射』），但 B 档管线未建、入库链路不存在，抽样审计（月度 30 |
| PQ-0276 | UNGRAPHED | SL-B09 进出口贸易线 U5 消费方挂接核验：源线谱已登记消费方意图（『L2（贸易链边权重）/ L3 板块』）与层宪章七层词表相容，但 B 档未落库未挂线，层宪章/七层挂载表无该线实际挂接记录可对 |
| PQ-0281 | UNGRAPHED | SL-B10 信用卡/支付消费线 U4 PIT 控制执行审计：登记文本已含风险与对冲方案（『高（官方汇总口径稳定）；proxy 与本体相关性须先证再用』），但 B 档管线未建、入库链路不存在，抽样审计 |
| PQ-0282 | UNGRAPHED | SL-B10 信用卡/支付消费线 U5 消费方挂接核验：源线谱已登记消费方意图（『L3（消费景气）/ L4』）与层宪章七层词表相容，但 B 档未落库未挂线，层宪章/七层挂载表无该线实际挂接记录可对（挂 |

## 五、灰段清单（未答完）

共 0 条——283 题全部有 exam_result，无未答完题。但零覆盖的 175 个 TDM 节点（无题可考）在覆盖意义上等同不可验证，已浮出于 §1.3。
