---
ttl: task_bound
title: C 主体画像——七类主体逐类台账＋七源逐源挖（现状/PIT 滞后/证据强度）（施工前挖矿作业簿）
created: '2026-10-13'
session: st-condaxis-20261013
status: mining_workbook
family_id: CONDAXIS-CAMPAIGN
completes_when: C 环节施工完成且随 CONDAXIS-CAMPAIGN 归档
---

# C 主体画像（3_C_actor_profile）

> 契约定位（研究册 §2.2-C）：行为归因，日频+事件——"谁在买谁在卖"。七类主体封闭枚举=MOD-SIG-088 `CapitalClass`（capital_behavior_orchestrator.py:78-87：北向/公募/私募/游资/量化/散户/产业资本）；每类输出=方向/强度/置信度/**证据链**。
> **A 股"资金出场"五条腿**（研究册 §8.3）：卖出+两融偿还+解禁减持+大宗折价出货+ETF 赎回；融券做空腿 2024-07 后可忽略；北向日频已死（2024-05-13）。
> **本册核心结论**：数据面七源六源在产（✅），但**归因层零实现**——没有任何代码把七源证据组装成 CapitalObservation（SIG-088 观测"由上游注入"而上游不存在，实读 §3.3）。C 环节的施工主体=观测适配器层。

## §1.1 七类主体逐类台账（画像面）

方向/强度/置信度输出口=MOD-SIG-088 `CapitalObservation`(capital_behavior_orchestrator.py:109-124: capital_class/net_inflow/participation/confidence)→`CapitalProfile`(:142-156)。逐类可用证据与置信语义：

| 主体类 | 首选证据源（仓内） | 次级/验证源 | 证据强度（研究册 §2.2-C 分级） | 现状判定 |
|---|---|---|---|---|
| 北向 | northbound_hold_snapshot（**季度**，见 §1.2-C5） | 无 | 季频诊断级（日频 smart money 用法已死——研究册 §5 北向披露制度漂移案） | 🌑 日频/✅ 季频 |
| 公募 | **无直接源**（基金季报重仓未采集——负存在断言：tasks.yaml 无对应 task，grep fund quarterly/重仓 零命中） | ETF 份额（配置盘代理）＋大宗溢价（利益输送面 ⭕） | 弱代理 | ⬜ 数据缺口 |
| 私募 | 无直接源 | 大宗折价（减持/接盘面）＋龙虎席位（部分私募席位） | 弱代理 | ⬜ 数据缺口 |
| 游资 | dragon_tiger+dragon_tiger_seat（席位明细） | seat_pattern_analyzer（design 态，§1.2-C4） | 事件级证据（龙虎榜=交易所披露硬数据，但朴素跟随负收益在案——研究册 §3/§5） | ✅ 数据/🔨 归因器 design |
| 量化 | 无直接源（算法拆单伪装——研究册 §8.1"大单≠主力"根源） | 竞价微观结构（MOD-SIG-089，blocked_on_data）；LM2002 β2（B1，建成后） | 推断级（最难直接观测） | ⬜ 间接面 blocked |
| 散户 | money_flow 小单净流入（五档口径）＋股东户数（结果验证） | market_fund_flow_daily 小单档（大盘口径） | 中（五档小单=散户代理，口径钉死 data_source 列——研究册 §8.4） | ✅ |
| 产业资本 | share_unlock（解禁前瞻）＋大宗折价减持通道 | 股东户数（集中度侧证） | 事件级（解禁日历=硬数据，卖出行为=推断） | ✅ 数据/⬜ 行为推断未建 |

**画像面结论**：七类中 3 类（游资/散户/产业资本）有硬数据面，2 类（北向/公募）低频或缺口，2 类（私募/量化）只能推断。C 环节 MVP 边界建议（呈批项）：先做有硬证据的三类＋杠杆盘（两融虽不在七类枚举内，但它是"资金出场五条腿"之一——枚举扩展或挂散户/量化类下作为观测通道，P1 呈批定）。

## §1.2 七源逐源台账（数据面；行数=本车道 2026-10-13 CH 只读实查，命令=SELECT min/max/count 各表）

| 源 | 仓内真源路径:行号 | 现状标记（附实查） | 消费方 | 缺口 | 六向定位 |
|---|---|---|---|---|---|
| **C1 大单五档（个股）** | tasks.yaml:182-195（money_flow_incremental：tushare pro.moneyflow 主源 5540 行/日级，akshare stock_individual_fund_flow fallback）；表 c1_market.money_flow | ✅实查在产：2021-01-04..2026-10-13、6,021,194 行；分日 uniqExact(symbol)≈5,573-5,574（10-13 当日 5,574 已到位）；data_source 全表单值 tushare（fallback 从未启用） | cohort_daily_ledger 杠杆/游资腿（cohort_daily_ledger.py:30-35）；market_fund_flow 另有大盘口径（见下） | **重定标**依赖逐笔委托（🌑 见 6_data_audit §L2）；count() 虚高坑（ReplacingMergeTree 未合并版本 2-3 倍，消费必须 FINAL/uniqExact） | ⑥字段：五档净流入+主力净额；①上游 fallback 闲置；②下游 C 适配器 |
| **C1' 大盘聚合** | tasks.yaml:3687-3699（market_fund_flow_refresh：akshare stock_market_fund_flow 东财大盘口径，fallback 显式置空，全窗重放 ~120 交易日） | ✅实查：2026-03-27..2026-10-13、233 行 | 无信号消费方 | 窗外历史不可回补（源端固定窗口）——2019-2026 长窗考试不可用，只能短窗 | ⑥字段：主力/超大/大/中/小单净流入五档 |
| **C1'' 盘中板块级** | c1_market.sector_fund_flow（tasks.yaml 在册） | ✅实查：2026-09-15..2026-10-13、12,110 行（当日新鲜） | sector_siphon/sector_divergence 相邻 | 盘中面与日频面口径分立 | ②下游 sector 族 |
| **C2 两融** | akshare_provider.py:1941（`_fetch_margin_trading`：逐日 stock_margin_detail_sse/szse 合并）；tasks.yaml margin task；表 c1_market.margin_trading | ✅实查在产：2024-09-02..2026-10-09、2,104,817 行、日均 ~4,108 标的；**新鲜度：10-12 缺**（截 10-13 20:00，滞后 1 交易日待查调度） | **同域已开考先例**：exam_cards/entry_flow/L1/TDM-E-L1-S0__calibration__07_margin_flow_shortwindow（status=examined，score row 32）——两融 5 日环比卡已出分！ | 因子面（个股级两融因子）未建；07 卡=大盘面先例 | ②下游：07 卡消费链已通；PIT=T+1 晨（研究册 §8.7） |
| **C3 大宗折价** | tasks.yaml:119-128（block_trade_incremental：akshare stock_dzjy_mrmx）；折价率=cohort_daily_ledger.py:34-35（口径 `折价率=1−price/当日 kline_daily close，JOIN 算`）＋:354（_build_inst_config inst_config 腿） | ✅实查在产：2026-08-07..2026-10-13、1,697 行（**历史仅 ~2 个月**）；近月折价率实查 2.94%~8.65%（日均值，JOIN 现算）——与研究册 §5"均值约 6.6%"同量级 | cohort_daily_ledger inst_config 腿（盘后结算层） | **短史**：2026-08 前无数据（事件研究窗不足）；深折价/溢价分事件研究未做 | ③算法：Seppi 1992 折价-知情理论（研究册 §4）；②下游 C 适配器+D 派发族 |
| **C4 龙虎席位** | tasks.yaml:130-153（dragon_tiger_incremental=stock_lhb_detail_em＋dragon_tiger_seat_incremental=stock_lhb_stock_detail_em Top5 席位）；seat_pattern_analyzer=src/zephyr/signal_ashare/limit_up/seat_pattern_analyzer.py（MOD-SIG-056）；lhb_premium_analyzer.py 同目录；event_dragon_tiger.py=src/zephyr/intelligence/ | ✅数据双表实查：dragon_tiger 2026-08-07..2026-10-13、2,664 行（日均 ~60-70 家，**主表短史**）；dragon_tiger_seat 2022-01-04..2026-10-13、622,847 行（4.7 年）——**两表历史严重不对称**；🔨 归因器：seat_pattern_analyzer 头注 `[MATURITY] design`、MVP 阶段零消费方、v0.1 只落六维中三维（席位画像/联动/跟随分） | seat_pattern_analyzer（design）；lhb_premium/event_dragon_tiger 相邻件 | 席位→主体身份映射（seat_registry 15 席位匹配）覆盖面有限；胜率字段 registry 为 null（v0.1 不用）；**负结果红线：朴素跟随负收益**——席位证据只进事件研究不进跟随信号 | ②下游 C 适配器；③算法：席位网络/营业部画像（研究册 §5） |
| **C5 北向（季度）** | tasks.yaml:2207-2218（northbound_hold_snapshot_refresh：tushare hk_hold 季度末全量，SH/SZ 拆分双调用，nightly+PIT 守卫=季度末+20 自然日才采新季度）；退役件 hk_connect_flow（tasks.yaml:197-208：止于 2024-08-16，任务 disabled 2026-09-16 裁定#257） | ✅季度在产：2024-09-30..2026-06-30、8 个季度、35,256 行（2026-06-30 行 8,747≈其他季度两倍，疑重拉双版本，ReplacingMergeTree 收敛中——消费用 FINAL）；🌑 日频已死（hk_connect_flow 表 4,052 行冻结） | regime_feature_builder.get_hk_connect_flow（NaN→fillna(0) 降级语义保留，tasks.yaml:207） | 下一季度 2026-09-30 数据 PIT 守卫最早 2026-10-20 采——**当周可用**；季度差分→增减仓信号未建 | ①上游单源无 fallback（预案交易所官网直抓未施工，tasks.yaml:2218）；②下游季频诊断卡 |
| **C6 ETF 申赎** | tasks.yaml:3701-3713（etf_share_snapshot_refresh：akshare fund_etf_spot_em 全市场快照 ~1,600 只，**注释明示"相邻日差分=净申赎"**＝派生未立项）；etf_nav（tasks.yaml:1921-1935，tushare fund_nav 主源）/etf_list（tasks.yaml:2232-2238） | ⚠️ **半断供**（本次挖矿新发现）：market_etf_share_snapshot 仅 2 个交易日有数——2026-09-18（1,621 只）与 2026-10-13（1,643 只），**daily_capital 排程下 16 个交易日快照缺失**（"任务存在≠管线活着"又一例）；✅ etf_nav 2021-07-29..2026-10-12、100,428 行；✅ etf_list 4,388 行 | 无信号消费方（快照积累制刚起步） | 申赎差分派生工程未立项（P1 呈批 10.6）＋**快照日常化缺口上报**（6_data_audit）；当前可用差分对仅 1 对 | ⑥字段：份额/IOPV/折溢价/成交/主力净流入一表全；②下游 C6 配置盘信号（需差分） |
| **C7 解禁** | tasks.yaml:568-599（share_unlock_incremental＋share_unlock_forward_refresh：东财 stock_restricted_release_detail_em，前瞻窗 [today,+365d]，weekend_calibration 排程）；表 c3_fundamental.share_unlock | ✅实查在产：unlock_date 2010-01-04..2027-10-13、30,357 行（前瞻已铺到 2027-10） | 无信号消费方（前瞻日历在库） | 前瞻窗口因子（解禁市值/流通市值比、临近度）未建；PIT=公告制 | ②下游 D 派发族+风控预警（研究册 §2.4-4） |
| **C8 股东户数（验证源）** | 见 1_A_structure.md §1 A4（c3_fundamental.shareholder_count，✅ 515,473 行新鲜） | ✅ | — | — | 归 A 件管辖，交叉引用禁重立 |

## §2 与既有资产边界

1. **cohort_daily_ledger=盘后结算层**（cohort_daily_ledger.py:30-35 头注：纯计算禁写库、CH insert 归总统筹批、bias_note 强制标注）——它已按杠杆/游资/机构配置/产业五腿消费 C1/C2/C3/C4 四源。C 环节观测适配器**消费同表、不重算口径**，禁第二实现；适配器输出=CapitalObservation，台账输出=cohort 行，两层职责分立。
2. **seat_pattern_analyzer（design）与 lhb_premium_analyzer/event_dragon_tiger**：三件席位域相邻件，C4 适配器应以 seat_registry.yaml（15 席位）为身份映射唯一真源（seat_pattern_analyzer.py:6 DEPENDENCIES），禁自带映射表。
3. **两融 07 卡先例**：C2 的考试卡通道已被两融 5 日环比卡走通（examined）——个股级/事件级新卡对齐其 data_binding 证据格式（含实查命令原文），不另起格式。
4. **与 D 合成层边界**：C 只产观测与证据链（含置信度），合成/推演/校准全归 MOD-SIG-088（4_D_synthesis 管辖）；C 不做"合力"。
5. **与研究册 §8.1"大单≠主力"的边界**：C1 五档数据在 C 层一律降级为**弱证据**（confidence 低档位注入），重定标级证据（逐笔委托）到位前禁当强证据（💰 待 P1 10.4）。

## §3 施工要点（实读代码的坑）

### 3.1 money_flow 的三个坑（实查实证）

1. **count() 虚高**：ReplacingMergeTree 未合并版本使 count() 达真实 2-3 倍（10-09：count 16,719 vs uniqExact 5,573）——一切行数断言/考试卡 evidence 必须 uniqExact 或 FINAL。
2. **口径钉死**：data_source 全表='tushare'；一旦东财 fallback 启用即换因子（研究册 §8.4）——适配器读取时必须随行携带 data_source 进证据链。
3. **当日盘中半截**：10-13 当日 20:00 已有 5,574 行（全量到位）——money_flow 是 T+0 盘后件，但"当日是否终态"要以调度日志为准，适配器禁以"行数=前日"自行判定。

### 3.2 PIT 滞后钉死表（研究册 §8.7 × 实查互证）

| 源 | 披露时点 | 信号可用时点（PIT 锚） |
|---|---|---|
| C1 money_flow | 盘后 T+0 晚 | T+0 收盘后（10-13 当日已全量为实证） |
| C2 两融 | T+1 晨（交易所晨披） | T+1 开盘前；**新鲜度实测 10-12 缺（10-13 20:00）——适配器需带 freshness 告警** |
| C3 大宗 | T+1 | T+1 |
| C4 龙虎 | T+1 晚间 | T+2 早（保守锚，待冻结） |
| C5 北向季 | 季度末+~20 自然日（PIT 守卫在 provider 内，tasks.yaml:2211） | 守卫放行当晚 |
| C6 ETF 份额 | T+1 快照 | T+1（快照日常化修好后） |
| C7 解禁 | 公告制（事前披露日历） | 事件日历前瞻（unlock_date 面向未来） |
| 股东户数 | 公告制不定时 | announce_date 当日 |

### 3.3 归因层现状的硬事实

MOD-SIG-088 `CapitalObservation` 的 docstring："单类主力观测（**上游资金流/龙虎榜件注入**）"（capital_behavior_orchestrator.py:110-111）——但全 src 无任何代码构造该 list（import 反查唯一引用=signal_ashare/__init__.py:29 再导出＋测试）。**观测注入层不存在=C 环节的真实空白**，也是"078 骨架在、跑不起来"的根因。适配器施工形态建议：`capital_observation_builder.py`（signal_ashare 域），逐源一个 builder 函数，输出 (CapitalObservation, 证据链 dict)，证据链含 data_source/表行号级指针/PIT 锚/降级原因——对齐 cohort_daily_ledger 的 bias_note 纪律。

### 3.4 席位身份映射的坑

seat_registry.yaml 仅 15 席位模板（seat_pattern_analyzer.py 头注），覆盖游资头部；大量营业部席位无身份——未识别席位归"未分类"档，禁 LLM 猜身份（指令/数据边界：席位名=数据非指令）。胜率字段 null 期间跟随分禁用胜率加权（v0.1 明令）。

## §4 自审闸三态裁定

| 件 | 裁定 | 理由 |
|---|---|---|
| C 观测适配器骨架（游资/散户/产业资本三硬源先行） | **施工** | SIG-088 的激活前提；消灭"画像层零实现"这段空白=终局资金行为层的必经路；数据全在产零新闸 |
| C1 五档→重定标级证据 | **挂起排期（💰）** | 解锁=逐笔委托采集（P1 呈批 10.4，l2_tick 退役件复活或商务源）；挂起期五档按弱证据注入 |
| C5 北向季频差分卡 | **施工（随适配器批）** | 数据在产、PIT 守卫在 provider 内现成；2026-09-30 季度 10-20 后到位正好作首考窗 |
| C6 ETF 申赎差分工程 | **挂起排期** | 依赖快照日常化修复（6_data_audit 上报项）＋P1 10.6 立项裁定；当前仅 1 个差分对无法开工 |
| C4 席位跟随类信号 | **方案封矿（跟随变体）** | 负收益实证在案（研究册 §3/§5）；终局只需要席位作**事件证据**入画像，跟随策略终局无位——席位证据卡（画像面）仍施工，跟随变体封矿 |
| 公募/私募直接源采集 | **挂起排期（💰候选）** | 基金季报重仓/13F 类无免费结构化源在册；先以 ETF 份额+大宗代理挂账，商务源进 P1 呈批清单 |

**反驳者一问**（适配器骨架加试）：①七类中三类无硬源，画像先天残缺（对策：封闭枚举保留七类，缺源类 confidence=0 注入即透明降级——SIG-088 空观测 NEUTRAL 语义现成）；②代理变量易被当成真主体（对策：bias_note 纪律沿袭 cohort 层+"弱证据"档位强制）；③适配器与 cohort_daily_ledger 职责重叠风险（对策：§2.1 边界条款——同表消费不重算）。维持施工。
