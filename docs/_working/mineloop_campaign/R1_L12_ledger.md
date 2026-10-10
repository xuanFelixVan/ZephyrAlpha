---
ttl: task_bound
title: R1 L12 复挖车道台账——TDM-E-L2-07/07-1 与 TDM-E-L2-09/09-1/09-2（前役 L1 自报封矿复挖）
created: "2026-10-10"
sid: st-mineloop-20261010
lane: L12-rework-entry_flow-L2-pullback-catalyst
family_id: MENELOOP-CAMPAIGN
---

# R1 L12 车道台账（复挖：回踩质量分级簇 + 催化剂识别簇）

工作根=`D:/ZephyrAlpha/.aidrafts/st-mineloop-20261010`。共用任务书=`.runtime/tmp/st-mineloop-20261010/MINING_BRIEF_R1.md`。
前役凭据=`D:/ZephyrAlpha/docs/_working/nightmine_campaign/L1_ledger.md`（L1 车道，sid=st-nightmine-20261010，
其 §7 mined_out 名单含 TDM-E-L2-07 / TDM-E-L2-07-1 / TDM-E-L2-09，blocked 名单含 TDM-E-L2-09-1 / TDM-E-L2-09-2）。
节点真源=`config/trading_decision_map.yaml` 第 1438-1638 行（全文读，含 decision_question/algo_note_zh/invalidation/fallback/data_refs/edges）。
方法论=mining_sop v1.8.0 §2 六向 / §3 枯竭判据 + 复挖硬门（自报封矿不自证成立）。

## 0. 车道立法（本车道新增必填面与红线）

- 复挖口径：凡前役标"受阻=未尝试"或 blocked 的向=本车道突破口；找漏矿=成功，确认封矿须附六向逐条"查无"凭据。
- 禁立同假设重复卡：L2-09 已有 02（研报密度，status=examined 已出分）/03（评级上调占比）/04（业绩净占比），
  L2-07 已有 ablation/02（离散化与门控），L2-07-1 已有 calibration/02（四因子合成分响应曲线），
  09-1 已有 calibration/02（图谱命中置信度），09-2 已有 ablation/02（跳数/衰减/方向口径）。
  逐字对照见 §2，本车道每张新卡在 frozen_note 内写明与同节点既有卡的分工边界。
- 取数红线：21:00-22:30 禁 CH 重查询 ⇒ 本车道 `data_window_evidence` 只引用在册实测（任务书 §3、
  前役 L1 台账 §3-P1..P18、同战役 L3 车道卡面 evidence、同节点 04 卡 evidence），
  未自取一条新数；需要新实测的两张卡一律 status=blocked_on_data 并把缺哪表哪一段写死。
- 源码直读（非 CH 查询）在本车道算合法凭据：所有代码侧断言均带 文件+行号+原文摘录（§3-C 段）。
- 判据面（窗口/分桶/阈值）一经写死不得回改（G4-5）。
- 全卡已机检：7/7 YAML 解析通过、必填面齐、`或`字零出现（歧义未择一风险已消除）、无 generated 标记、
  card_id 无碰撞（机检脚本只读输出，本车道未落任何临时件到项目根）。

## 1. 台账总表（逐节点一行，机读优先）

| node_id | ①上游 | ②下游 | ③算法 | ④后端 | ⑤呈现 | ⑥数据 | 新卡数 | 族分布 | mined_out? | blocked 原因 |
|---|---|---|---|---|---|---|---|---|---|---|
| TDM-E-L2-07 | **漏矿**：原文"追高和低吸的胜负率差一倍"（第 1450 行）从未入卡（前役只考离散化/门控） | **翻案**：前役记"L4 仓位分配"无 grep 凭据；本车道 Grep 实测 sector_pullback/grade_pullback/pullback_action/PULLBACK_ACTIONS 在 src+scripts+config 零生产消费方（仅包导出+单测）⇒ 输出未接线 | 族 S6（Investopedia 2025／JIFM 2022／Springer 2009，前役 §2-S6 已挖，本车道复用不重挖）；新增离散化之外的"第四类归属"题型 | **漏矿**：pullback_action(None)→WATCH_OR_DOWNGRADE（第 152-156 行）＝时间窗外样本被静默并入零仓，地图未写、前役未考 | ABC 等级→买入优先级动作（BM-BUY-04），只登记一句 | 板块指数面 880 行业族 2021-08-02 起可考（P4）；个股面需成分（P6）⇒ 严格锁板块对象 | 2 | comparison×1 + ablation×1 | **推翻**（①②④三向有漏） | 无（两卡均 preregistered） |
| TDM-E-L2-07-1 | **漏矿**：invalidation 三条边界（>15 日横盘失效／<2 日洗盘／>78.6% 结构破坏，第 1495 行）从未立可判卡 | 在册边第 6195 行 07-1→TDM-E-L4（feed/signal/**intraday**/lag 0d/pit_proof=legacy-unaudited）；代码侧零消费方（同上 Grep） | 族 S6 复用；新增"死常量两腿"与"单位口径错配"两题型（前役无） | **翻案+漏矿**：前役记"在码三维 vs 地图四维（缺时间窗）"不成立——时间窗在码是硬门（第 126-127 行 return None）；真正未落地的是 FIB_STRUCTURE_BREAK=0.786（第 39 行）与 PULLBACK_HEALTHY_MAX_DAYS=10（第 45 行）**两个死常量**（grade_pullback 内零引用）；另地图">7"（第 1484 行）vs 在码 70.0/40.0（第 48-49 行，docstring 注 0-100）vs 接线 strength_score 0-100 直用 vs L2-06-3 卡按 10 分制＝四处单位不齐 | 四因子 0-1 分→A/B/C，只登记一句 | 880 OHLC 满配（P4）；板块宇宙 376→729 在扩⇒分母族冻结 189 codes（P9）；节点 activation=intraday 而日内面仅 2026-07-20 起约 55 日（P7）⇒ 日线近似并声明 | 2 | ablation×1 + calibration×1 | **推翻**（①④两向有漏，⑥向日内面 blocked 精确化） | 日内专卡 blocked_on_data（缺 2021-08-02..2023-12-31 板块级日内史） |
| TDM-E-L2-09 | **漏矿两条**：①data_refs=[DS-107] 声明源（news_sentiment_window，盘前夜窗）从未被本节点任何卡消费；②原文"有当下催化剂的板块加权 20%"（第 1552 行）——**加权形式**从未入卡 | 在册边第 6197 行 09→L2-01（feed/signal/daily/lag 0d）；代码侧以节点号反查仅命中 intelligence 三件与两个生成器/文档性引用 ⇒ 未见"催化剂→L2-01 加权 20%"实现＝地图在册、代码未接 | 族 S7 复用（研报评级聚集/PEAD，前役 §2-S7）；新增"恒定加权 vs 指数衰减"形式对照题型 | **翻案**：在码 EventScreenConfig（第 91-94 行）四字段无"20%"常数；实际实现是标的级 weight=1+direction×strength×2^(−age/H)（第 27、124-129 行），_EVENT_HALFLIFE EARNINGS=4.0／MERGER=2.0（第 65-67 行，注"初拟待校准"），EventCategory 六类含 POLICY（第 53-61 行）⇒ 地图与代码是两个不同对象 | 催化剂标签＋排序权重，只登记一句 | research_report 2017 起 146940 行/207 industry（P13）；earnings_forecast 125582 行/1999-01-08..2026-07-03/5707 symbols（04 卡在册）；news_sentiment_window scope='market' 2622 行满窗、scope='symbol' **仅 2026-02-24..2026-08-20**（L3 卡在册复证 P12）⇒ 板块级夜窗聚合不可算 | 2 | comparison×1 + calibration×1 | **推翻**（①⑥向各抓到一条实质漏矿） | calibration/05=blocked_on_data（缺 symbol 面 2019-01-04..2025-09-09 段）；政策/事件五类腿 blocked_on_data（缺类别标注落库史） |
| TDM-E-L2-09-1 | 上游=L1-S0-1（在册边第 6383 行）与事件评分；前役 02 卡已覆盖"命中+置信"主张，本车道未找到未卡的判据性陈述 | 在册边第 6384 行 09-1→09-2（sequence/continuous）；代码=news_chain_node_linker（MOD-INT-NEWS-CHAIN，testing，55 单测在册） | 族 S7/S8 复用；对照既有 02 卡：墓碑/泛化词对照臂已在卡内，无可加独立假设而不摊薄 | module_ref=news_chain_node_linker.py（第 1594 行）在岗，无历史落库面 | 命中+置信清单，只登记一句 | **前役理由部分错置**：ig_node 与 ig_node_company **均有 valid_to 列**（api_server.py 第 3935/3941/3949/3964/4109/4111 行、chain_impact_resolver.py 第 8/25/377 行一律 valid_to IS NULL）⇒ "无版本化/PIT"不成立；真实约束=构建史 created_at 2026-08-28..2026-09-24（P15）+ symbol 新闻面窗不相交 ⇒ 仍不可考，但根因变了 | 0 | — | **推翻理由、维持结论**（六向查无凭据补齐，唯⑥向理由改写） | blocked_on_data：缺 ig_* 2026-08-28 前构建史与 valid_to 历史分布实测（本车道禁查未取） |
| TDM-E-L2-09-2 | 上游=09-1 命中节点＋图谱边；既有 02 卡已考跳数/衰减/方向三口径 | 在册边第 6385-6386 行 09-2→L3-04（feed/daily）与 09-2→L0-02（feed/intraday）；代码=chain_impact_resolver.py + chain_impact_stream.py（Grep 实测命中，前役未列凭据） | **翻案**：既有 02 卡三组臂都不含"valid_to 过滤"这一臂——而它正是前役判 blocked 的理由本体；把它变成可消融臂=把"回放即前视"从断言变为可测量 | 第 8 行 INVARIANTS 原文"公司映射只取 ig_node_company.valid_to IS NULL（PIT 有效行）"、第 377 行 SQL 常量、±0.15 死区与 0.6^hop 均为在码值（非卡新拟） | 冲击清单＋方向分级，只登记一句 | 同 09-1＋(2) 种子输入面 scope='symbol' 2026-02-24..2026-08-20 与图谱窗 2026-08-28 起**不相交**（两条独立在册实测交叉）⇒ 冻结窗内种子零行 | 1 | ablation×1 | **推翻**（③⑥两向：理由错置＋新臂可测未立卡） | blocked_on_data：缺 valid_to 历史分布实测＋两窗重叠 ≥250 交易日 |

## 2. 已存在卡对照表（防重复假设，逐字核）

| 既有卡 | 其假设对象（一句话） | 本车道新卡如何避开 |
|---|---|---|
| TDM-E-L2-07/ablation/02（preregistered） | A/B/C 离散化＋门控 相对连续映射/不门控/mean 定级的边际 | 新卡一考"不评级样本的仓位归属"（第四类），新卡二（07-1）考强度维单位；arm 集合与 02 无交集，两卡 note 内已写明 |
| TDM-E-L2-07-1/calibration/02 | 四因子（含量能/强度）合成分对板块 5 日超额的响应曲线单调性 | 新 calibration/03 **刻意不含量能与强度**，只考地图 invalidation 对应的 Fib 五档×时间四档两腿；新 ablation/03 只摘强度维一臂 |
| TDM-E-L2-09/calibration/02（examined，已出分，score_row=rows[9]） | 研报条数密度 z 分（关注度）对次日/5 日的单调正效应 + >95 分位反向腿 | 本车道不碰"密度读数预测力"；comparison/02 考**加权形式**（板块恒定 +20% vs 标的指数衰减），calibration/05 考**另一张表的盘前情绪读数** |
| TDM-E-L2-09/calibration/03 | 5 日评级上调占比（方向共识）与 02 同场对比 | 同上，两新卡对象均非评级方向 |
| TDM-E-L2-09/calibration/04（by st-nightmine-20261010-RXA） | 业绩预告净占比（预增+扭亏−预减−首亏）预测力 + 未兑现复核 | comparison/02 用同一张 earnings_forecast 表但对象是**权重形式对照**（direction×strength×衰减），非净占比预测力；且沿用其 symbol→industry 派生映射口径（引用不改）；calibration/05 表不同（news_sentiment_window） |
| TDM-E-L2-09-1/calibration/02（blocked_on_data） | 图谱命中数×置信的预测力，含墓碑/泛化词对照臂 | 本车道不给 09-1 立新卡（避免摊薄）；valid_to 臂归 09-2 对象 |
| TDM-E-L2-09-2/ablation/02（blocked_on_data） | 1 跳/2 跳/衰减 0.6 vs 不衰减 vs 0.3、全链同向 vs 成本反号 | 新 ablation/03 只加"valid_to 过滤 vs 不过滤"一臂，扩散参数两臂同值不动，frozen_note 已写"与 02 卡对象不同不得合并出分" |

## 3. 六向逐向重查凭据日志

### 3-A 节点原文（①上游，config/trading_decision_map.yaml 全文读）
- L2-07 第 1447-1453 行：decision_question="这次回踩是 A/B/C 哪级、值不值得买给多少仓"；
  algo_note_zh 含"回踩是买点质量的核心判据——追高和低吸的胜负率差一倍"、"Fib×量能×强度三维取最弱档定级；
  A=满额优先建仓/B=半仓分批/C=观望，pullback_action 映射在码"；第 1461 行 activation=intraday、第 1456-1458 行
  module_ref=sector_pullback.py / MOD-SIG-026、第 1468 行 module_mounts=[MOD-SIG-116]、第 1456 行 data_refs=[DS-170]。
- L2-07-1 第 1482-1495 行：decision_question="Fib 位置×量能衰减×板块强度×时间窗合出 A/B/C 哪级"；
  algo_note_zh="四因子各 0-1 分加权定 A/B/C"、"38.2% 附近=A 的必要条件"、"量能衰减（回调缩到峰值 1/3）"、
  "板块强度（>7）"、"时间窗（回调 3-8 天）"；**第 1495 行 invalidation**="回踩>15 交易日转横盘失效；
  <2 日属盘中洗盘不入级；>78.6% 趋势结构破坏"；第 1492 行 algo_refs=[DAL-PULLBACK-ABC]。
- L2-09 第 1548-1571 行：decision_question="这个板块有没有当下催化剂（政策/业绩/事件）加持"；
  algo_note_zh="催化剂扫描：政策（部委文件/产业规划）、业绩（行业龙头超预期）、事件（涨价/突破/签约）。
  有当下催化剂的板块加权 20%——有故事的资金才敢接力"；**第 1557 行 data_refs=[DS-107]**、
  第 1562 行 activation=premarket、**第 1565 行 fallback**="DS-107 缺失→催化剂维度降权（纯量价判定）"；
  第 1569 行 module_mounts=[MOD-SIG-106]；第 1539 行 battle_map_refs=[BM-SEL-10]（裁定#483/#487 在册边）。
- L2-09-1 第 1575-1606 行、L2-09-2 第 1607-1638 行：模块、data_refs（DS-224/DS-225）、
  09-2 扩散口径原文（第 1620-1621 行"ig_edge 无向 BFS 默认 2 跳×每跳置信 0.6 衰减；方向=情绪 polarity ±0.15 死区外映射
  利好/利空、全链同向（成本反号传导留事件类型细分后迭代）"）。

### 3-B 消费方反查（②下游，本车道用 Grep 工具替代前役 git grep；命令语义=Grep -l 于 src/scripts/config/tests）
- `sector_pullback|grade_pullback|pullback_action|PULLBACK_ACTIONS` → src/zephyr/signal_ashare/sector/sector_pullback.py
  （定义自身）、src/zephyr/signal_ashare/sector/__init__.py（包导出）、
  config/trading_decision_map.yaml（地图）、tests/research/research/signal_ashare/sector/test_sector_pullback.py
  （单测，另两处 __pycache__ 路径为编译产物不计）。⇒ **零生产消费方**；
  前役 §1 L2-07 行写"②下游=L4 仓位分配"、§4-A3 未把 L2-07 列入 grep 清单 ⇒ ②向无凭据（本车道补齐）。
- `TDM-E-L2-07|TDM-E-L2-09`（节点号反查）→ src/zephyr/intelligence/chain_impact_resolver.py、
  chain_impact_stream.py、news_chain_node_linker.py、src/zephyr/signal_ashare/__init__.py、
  scripts/governance/d5_architecture/generators/generate_trading_day_cycle_map.py、
  config/trading_day_cycle_map.yaml、config/trading_decision_map.yaml。
  ⇒ 09-2 有代码件引用（前役未列）、L2-07/L2-09 主节点在 src 侧无消费件（催化剂加权未见实现）。
- 在册边（②向的地图侧凭据）：第 6195 行 `from_node: TDM-E-L2-07-1, to_node: TDM-E-L4, edge_type: feed,
  payload_type: signal, frequency: intraday, lag: "0d", pit_proof: legacy-unaudited`；
  第 6197 行 09→01（daily）；第 6383-6386 行 S0-1→09-1、09-1→09-2、09-2→L3-04、09-2→L0-02。
  注：07-1→L4 边 frequency=**intraday** 而 880 面是日线、09-1/09-2 边 pit_proof=legacy-unaudited ⇒ 已入卡面声明。

### 3-C 源码直读凭据（③④向，非 CH 取数；均为本车道 2026-10-10 实读）
- `src/zephyr/signal_ashare/sector/sector_pullback.py`（157 行全文读）：
  第 39 行 `FIB_STRUCTURE_BREAK = 0.786  # >78.6% 趋势结构破坏，回踩转反转`、
  第 45 行 `PULLBACK_HEALTHY_MAX_DAYS = 10  # 3-10 交易日健康窗` ⇒ **两常量在 grade_pullback（第 111-149 行）内零引用＝死常量**
  （实读第 129-149 行只用到 FIB_SHALLOW_MAX/FIB_DEEP_MAX/STRENGTH_*/VOLUME_*/_GRADE_ORDER）；
  第 126-127 行 `if pullback_days < PULLBACK_MIN_DAYS or pullback_days > PULLBACK_STALE_DAYS: return None`
  ⇒ 时间窗在码是**硬门**（前役"缺时间窗"表述不成立）；
  第 141-146 行强度维按 STRENGTH_STRONG=70.0/STRENGTH_MEDIUM=40.0（第 48-49 行）定档，
  docstring 注明 sector_strength=板块强度分 0-100；
  第 148-149 行三维取最弱档；第 152-156 行 `pullback_action(grade=None)` 返回 `PULLBACK_ACTIONS["C"]`
  ⇒ 不评级样本被并入"观望=零仓"（地图未写，前役未考）。
- `src/zephyr/signal_ashare/core/sector_strength_wiring.py` 第 27 行"结构强度=strength_score（0-100 直用）"
  ⇒ 与地图">7"、L2-06-3 卡"10 分制"三处单位不齐（本车道 ablation/03 的立卡依据）。
- `src/zephyr/signal_ashare/screening/event_driven_screener.py`（186 行）：
  第 27 行"保留标的按事件衰减曲线赋排序权重：weight = 1 + direction×strength×2^(−age/半衰期)"、
  第 124-129 行 `_event_weight` 实作、第 65-67 行 `_EVENT_HALFLIFE`（EARNINGS=4.0、MERGER=2.0，注"26 号 memo §2.4
  经验区间中点，初拟待校准"）、第 53-61 行 EventCategory 六类（EARNINGS/MERGER/POLICY/SUDDEN/IPO/GEO）、
  第 91-94 行 EventScreenConfig（min_confidence=0.7、extreme_reaction_pct=3.0、conduction_risk_max=0.7、
  capacity_target=30）⇒ **配置里不存在"20%"任何形式**，地图"板块加权 20%"在码无对应实现。
- `src/zephyr/intelligence/chain_impact_resolver.py` 第 8 行 INVARIANTS 原文含
  "公司映射只取 ig_node_company.valid_to IS NULL（PIT 有效行）"、第 377 行模块级 SQL 常量同谓词；
  `src/zephyr/frontend/dashboard/api_server.py` 第 3935/3941/3949/3964/4109/4111 行、
  `chainmap_equity_graph.py` 第 139/148 行 ⇒ ig_node 与 ig_node_company **都有 valid_to**，
  "图谱无版本化/PIT"（前役 §1 L2-09-1/09-2 行与 §7 blocked 表原文）与代码事实矛盾。
- `src/zephyr/intelligence/nightly_sentiment_window.py`（MOD-INT-NEWS-NIGHT）蓝图 §0 原文：
  "夜间窗口=前一交易日 18:00（含）→交易日 08:00（不含）左闭右开……persist=True 时写
  c1_market.news_sentiment_window（#138，DS-107）" ⇒ DS-107 实体=该表，且天然盘前 PIT（本车道 calibration/05 的口径依据）。

### 3-D 数据向复证（⑥向，全部引用在册实测，未自取新数）
- 880 行业族 industry_l1=2021-08-02..2026-10-08/78263 行、industry_ths=同窗/163038 行、OHLC+amount 满配（前役 §3-P4）。
- sector_state.strength 2022..2025 全 0、capital_score 全史 0 ⇒ 强度读数必须重算禁直读（§3-P9/A6）；
  codes 376→729 在扩 ⇒ 分位分母族冻结（§3-P9）。
- kline_index 000300=2005-01-04..2026-10-09/5284 行（§3-P10）；kline_daily_hfq=1990-12-19..2026-09-30/10098785 行，
  2026-09-30 后 9 日缺口（§3-P10，影响 09-2 卡辅轴终点，已在卡内写明"按实际可得行截断并登记，截断不改判据面"）。
- kline_sector_intraday=2026-07-20..2026-10-09 约 55 交易日（§3-P7）⇒ L2-07-1 日内口径 blocked。
- sector_constituent=2026-07-22..2026-10-01/323175 行/**仅 6 个 update_date**（§3-P6）⇒ 板块内个股一律不可算（前役 S10 内部矿脉复证）。
- research_report=2017-01-02..2026-09-30/146940 行/207 industry/116 org，逐年 2019=11967…2025=16237（§3-P13）。
- news_data=2010-01-02..2026-10-10/8219185 行，逐年 2024=759512、**2025=31425**、2026=259401（§3-P14）
  ⇒ 本车道复核：该表≠DS-107 实体（DS-107=news_sentiment_window），前役 blocked 理由错引此表（翻案 R6）。
- news_sentiment_window=2019-01-04..2026-10-08/22257 行，symbol/night=19635、market/night=201、market/1d=2421（§3-P12）；
  **分 scope 覆盖窗**（同战役 L3 车道在册，见 TDM-E-L1-S0-1__calibration__03 卡 evidence）：
  scope='market' 1 标的/2622 行/2019-01-04..2026-10-08、分年 362/366/365/365/362/358/243/201；
  scope='symbol' 4857 标的/19635 行/**2026-02-24..2026-08-20**；上游逐条面 news_sentiment_score=7947739 行
  （含 caliber_version）⇒ 板块级盘前情绪在本战役冻结窗内不可聚合（calibration/05 blocked 的实测支点）。
- earnings_forecast=125582 行/1999-01-08..2026-07-03/5707 symbols/forecast_type 十类（同节点 04 卡在册实测）。
- PG 图谱 ig_chain=873、ig_node=5560、ig_edge=1726、ig_node_company=25559，
  ig_node_company created_at=2026-08-28 04:08:55+08:00..2026-09-24 15:47:33+08:00，ig_* 在 depgraph 库不在治理库（§3-P15）。
  ⇒ 本车道新增断言：valid_to 非空行数与历史界**未实测**（禁查时段）＝09-2 卡 blocked 的第 (1) 条缺口。
- 涨停判定口径（任务书 §3）：MUST 用不复权 c1_market.kline_daily 配 stk_limit；stk_limit=2015-01-05..2026-10-09/9254772 行（§3-P7）。

### 3-E 族级外部矿脉（③向）
- 复用前役已挖族级日志：S6 回踩/Fibonacci（Investopedia 2025、JIFM ScienceDirect 2022、Springer 2009）、
  S7 研报评级/PEAD（百度学术转载 2025×2、Discovery Researcher 2025）、S5 消融/IS-OOS 防过拟合
  （arXiv 2026、quant67 2026、聚宽 2026）。本车道**未重挖外部**（同题型族级挖一次已跨节点复用；
  前役 §2 已带 URL+发布方+年份，本车道卡面 sources 只引台账锚点，未新增外部条目=零单源风险）。

## 4. 未挖长尾清单（明列，不降格封矿）

1. **EventCategory 五类半衰期（POLICY/SUDDEN/MERGER/IPO/GEO）**：在码标"初拟待校准"，
   但类别标签无历史落库表可证（本车道禁查未查）⇒ 待总包 22:30 后实测 event 标注面；有表则半衰期矩阵卡立刻可立。
2. **strength_score 真实取值域（0-10 vs 0-100）未实测定格**：ablation/03 用两臂对照吸收了该不确定性，
   但地图文字该不该改要一次实测（读 sector_report_builder MOD-L00-009 日频报告 JSON 一天即可判）。
3. **板块级日内回踩专卡**：节点 activation=intraday（第 1461/1494 行）与日线口径差异；
   kline_sector_intraday 仅约 55 日⇒ blocked（已写死在 L2-07-1/calibration/03 的 blocked_scope），解锁=板块日内史补至 2021-08-02 起 ≥250 日。
4. **Fib 档位三口径并存**（地图 38.2% 必要条件／07-1/02 卡 38.2±0.1 带宽／07-1/03 卡五档／在码 0.50-0.618 两档）：
   本车道未裁、只登记⇒属施工与裁定面（不改地图，不改已冻卡）。
5. **催化剂→L2-01 加权 20% 的接线缺口**：地图在册边第 6197 行、代码零实现；comparison/02 出分后才有改法依据。
6. **news_sentiment_window 的 caliber_version 口径变更史审计**：L3 卡已列"跨口径混算"风险，本车道未做（属数据质量画像）。
7. **前役 §5-8"念想引擎（LSG qwen）向"仍=受阻未尝试**：本车道同样未调用（≤预算优先源码与在册复证）⇒
   继续按"受阻=未尝试"挂账，禁判查无。
8. **09-2 的 valid_to 历史分布实测**（缺 (1) 条）：一条 SQL 即可解锁翻案幅度量化，须总包 22:30 后执行。

## 5. 复挖结论（逐节点，推翻/确认）

| node | 前役自报 | 本车道结论 | 一句凭据 |
|---|---|---|---|
| TDM-E-L2-07 | mined_out | **推翻** | 地图原文"追高和低吸的胜负率差一倍"（第 1450 行）与在码"不评级→观望"（第 152-156 行）两处可判断言从未入卡，本车道一次补立 comparison/03＋ablation/03 两张 |
| TDM-E-L2-07-1 | mined_out | **推翻** | FIB_STRUCTURE_BREAK=0.786（第 39 行）与 PULLBACK_HEALTHY_MAX_DAYS=10（第 45 行）在 grade_pullback 内零引用＝死常量，而地图 invalidation（第 1495 行）三边界从未可判化；且强度维四处单位不齐（">7" vs 70/40 vs 0-100 直用 vs 10 分制）前役只登记"三维 vs 四维"而未登记真矛盾 |
| TDM-E-L2-09 | mined_out | **推翻** | 节点 data_refs=[DS-107]（第 1557 行）声明源从未被本节点任何卡消费，前役 blocked 理由错引 c3_fundamental.news_data（另一张表，其真身 news_sentiment_window 满窗 2019-2026 已在册 P12）；同时"加权 20%"在 EventScreenConfig 中不存在、在码是 2^(−age/H) 标的级衰减⇒"加权形式"从未入卡 |
| TDM-E-L2-09-1 | blocked_on_data（六向留痕齐） | **理由推翻、结论维持** | "图谱无版本化/PIT"与 ig_node/ig_node_company 的 valid_to 列及其全域使用（api_server 第 3935-4111 行、resolver 第 8/377 行）矛盾；但 symbol 新闻面窗（2026-02-24..08-20）与图谱构建窗（2026-08-28 起）不相交，仍不可考⇒本车道未立新卡（避免摊薄），blocked 表述由 09-2 卡与本台账 §4-8 精确化 |
| TDM-E-L2-09-2 | blocked_on_data（六向留痕齐） | **推翻** | ③向既有 ablation/02 三组臂不含"valid_to 过滤"臂，而该谓词正是前役判 blocked 的理由本体；把断言变成可测对照（新立 ablation/03，status=blocked_on_data，两条缺口写死），同时补齐前役未列的②向代码消费凭据（resolver/stream/linker 三件） |

- 程序性结论：前役 L1 §7 的 mined_out 名单对本车道 5 节点中 **3 个直接推翻**、**1 个理由推翻结论维持**、
  **1 个理由与结论双翻**；其 §1 六向表对 L2-07/L2-07-1/L2-09 的②向**无任何 grep 凭据**（§4-A3 未列入），
  按 v1.8.0 §3"确认封矿须附六向逐条查无凭据"的标准，这三行的封矿在程序上亦不成立。

## 6. 收尾汇总（本车道）

- **节点总数**：5（TDM-E-L2-07、TDM-E-L2-07-1、TDM-E-L2-09、TDM-E-L2-09-1、TDM-E-L2-09-2）。
- **新卡总数**：7；卡名与 status（全为新建文件，未触碰任何既有卡件与骨架件）：
  1. `TDM-E-L2-07/comparison/03_追高与低吸胜率对照` — preregistered
  2. `TDM-E-L2-07/ablation/03_时间窗外不评级并入观望的边际` — preregistered
  3. `TDM-E-L2-07-1/ablation/03_强度维单位口径错配` — preregistered
  4. `TDM-E-L2-07-1/calibration/03_死常量两腿_结构破坏与超窗横盘` — preregistered
  5. `TDM-E-L2-09/comparison/02_催化剂加权形式板块恒定与标的指数衰减` — preregistered
  6. `TDM-E-L2-09/calibration/05_板块级盘前新闻情绪催化剂腿` — blocked_on_data
  7. `TDM-E-L2-09-2/ablation/03_图谱PIT有效行过滤臂` — blocked_on_data
- **族分布**：calibration 2、ablation 3、comparison 2、shadow 0。
- **status 分布**：preregistered 5、blocked_on_data 2、blocked_on_impl 0。
- **未挖长尾**：见 §4（8 条明列，其中 2 条只需一条 SQL 即可解锁，均已点名缺哪表哪段）。
- **交叉复挖建议（20% 名单，含前役封矿不成立的具体节点+理由）**：
  1. **TDM-E-L2-08**（前役 mined_out）：其 blocked 理由同样是"涨停池仅 28 日"，但本车道发现 stk_limit 触及判定
     （不复权 kline_daily 配 stk_limit，§3-P7 满史）足以构造"板块触及涨停家数占比"的生命周期确认腿替代 limit_up_pool 时序⇒ 同一 blocked 理由可复制翻案。
  2. **TDM-E-L2-03**（前役 mined_out）：与本车道 L2-07-1 共用 sector_pullback 同族常量与"扩散维 0.3 权重不可算"的
     blocked 声明；死常量/单位口径的审计法可平移（其 80% 门控与倒 U 先验对冲是否也在码有死常量）。
  3. **TDM-E-L2-01-1 / L2-06-2 / L2-03-1 / L2-10**（前役 blocked_on_data，理由=成分口径）：
     本车道无新数可查，但 09-2 卡揭示"blocked 理由须与代码在册读取口径对表"的通则——建议逐条复挖其 blocked 表述是否也错置了表名。
  4. **TDM-E-L2-09-1**（本车道维持结论）：一旦 valid_to 历史分布（§4-8）实测为有值，09-1 与 09-2 两张 blocked
     卡可同时转 preregistered，是全班解锁成本最低的一对。
  5. **L2-05/L2-05-2**（前役 mined_out，⑤向只登记一句）：fallback 字段"DS-107 缺失→降权"在 L2-09，
     同族 fallback 面（水温档缺失时的放行比例）建议按本车道 comparison 形式对照法复挖一次。
- **本车道对全战役的一条硬结论**：封矿与 blocked 的**理由文本必须与代码在册读取口径对表**——
  本车道 5 个节点里 3 处 blocked 理由（news_data 断供、图谱无版本化、在码缺时间窗）都与实读源码或实读地图不符，
  错置理由会把可解锁的面永久冻结成"不可考"；建议全班把"④后端断言须带 文件+行号+原文"设为卡面硬必填。
