---
ttl: task_bound
doc_type: index
title: L04 板块→个股传导 · 子模块总勾表与本环节穷尽性声明
created: 2026-09-26
sid: st-qmine-20260925
lane: LANE-MINE-L04
status: 环节 4 子层挖干交付（六簿齐；父簿 SKEL 的 W0-W7 全部归位，无孤儿子块）
---

# L04 · 子模块总勾表（父层=SKEL.md，本表=子层唯一入口）

> 读法：`SKEL.md`=环节级骨架（八子块树 W0-W7 + L04-C01~C08 施工项）；本目录 `sN_*/MINE.md`=子模块级挖干簿（六项齐：①职责 ②现状实测 ③六向台账 ④缺口清单 ⑤自审闸三态 ⑥挖矿日志）。
> 编号沿用：L04-Cxx（SKEL 施工项）/Dxx（需求册）/LK-xx（09 号文）/DU-xx（12 号文普查）/CNS-xx（14 号文消费普查）/IBT-xx（11 号文回测审计）；本层新缺口一律编 `L04-Sn-Gm` 并注"册内未见"。
> **本子层切分=6 簿覆盖父层 8 子块**（W4+W5 合册、W3+W6 合册，合并理由与 MECE 交代各写在册首 §①）；目录名不以数字结尾（R5-DIGIT-SUFFIX）。

## 1. 子模块清单与状态

| 子簿 | 覆盖父层子块 | 主覆盖件 | 状态 | 净新增缺口 | 对 SKEL 的改判 |
|---|---|---|---|---|---|
| `s1_conduction_gate` | W0 | sector_conduction(99 行全文)/sector_gate/sector_leader + yaml L2-06 段 | MINING（长尾 3） | 4 | 龙头件"无生产调用方"→ **库内调用方非零**；"两字段无落库载体"→ **载体列已建、值未填** |
| `s2_constituent_mapping` | W1 | sector_constituent(+snapshot)/index_constituent DDL 与 CH 实测 | MINING（长尾 3） | 5 | 8803/8804 零行从"数据缺口"改判为**设计如此（该族不在成分表）**；DU-01/02 验收线暴露**两口径歧义（板块层 729 vs 成分腿 595）** |
| `s3_candidate_pool_chain` | W2 | candidate_pool_snapshot(MOD-SIG-152)/池 DDL/门快照侧带 | MINING（长尾 3） | 8（含 1 待核） | **L04-C01/C02 从"待建"改判为"载体+挂点侧带已落地"**；LK-04 ✗→🟡（挂点在、池为空）；D22/M-41 建议销账为"已落地待验收" |
| `s4_factor_layer_and_news_dim` | W3 ⊕ W6 | factor_registry(175 条逐条统计)/因子存储层实测/新闻双腿+linker | MINING（长尾 3） | 5 | **DU-05 改判**：打分器近 7 日全表重打（真因=新语料进不来）；**DU-06 改判**：symbol 腿已到 09-24，新病=稀疏（日均 163.6 只）；**关联字段近 30 日 100% 空=两 DU 同根因** |
| `s5_tradability_filters` | W4 ⊕ W5 | tiered_screening_filter/tradability_preflight + 八表 CH 实测 | MINING（长尾 3） | 6 | BM-SEL-16"三参数全 proposed"→ **参数已实装**；suspend"无批量源"→ **三任务在册零产出**；**CNS-10 接 ipo_schedule=接空表（实测 0 行）**；DU-11 阶梯恶化逐日实测 |
| `s6_stock_state_axis` | W7 | 池史深度/daban_engine_load 先例/market_pattern_win_rate 范式 | MINING（长尾 3） | 5 | **LK-05"概率表仓内未立项"改判**：仓内已在产一张条件胜率表（4,239 行，五元组+n_events+low_sample+baseline）→ C07 从"立项"改"换轴复用" |

**合计 6 子簿**：状态全部 MINING（各簿长尾 3 条未清空，共 **18 条长尾**），无一簿以"轮数/现状规模"封矿（挖矿 SOP §3 结构判据）。

## 2. 本环节新缺口汇总（子层净增 32 条 + 待核 1 条）

| 编号 | 一句话 | 三态 |
|---|---|---|
| S1-G1 / G2 / G3 / G4 | 传导挂载对象与 lead-lag 主机制不同构 / 两套"谁是龙头"零对表 / admission_gate 零调用而同件 water_temp 在产（半接电） / L2-06 节点 data_refs+factor_refs 双空 | 挂起 / 施工 / 挂起 / 施工 |
| S2-G1~G5 | PIT 成分读门面缺 / SCD 仅 4 版本（归属史 2026-07 起） / 板块宇宙三真源 / 快照断日实测 / 板块腿无权重字段 | 施工 / 挂起 / 施工 / 移交 / 挂起 |
| S3-G1~G8 | 池读方 0 / 注入源未注册 / 零行无哨兵 / 日内 stage 无产码 / 池变更流无表 / 机账 category 重复 / 漏斗阶段存活数不落库 / 挂点归属待核 | 施工(编 C09) / 挂起(等 LANE-BUILD) / 施工 / 挂起 / 挂起 / 施工 / 施工 / 待核 |
| S4-G1~G5 | 因子存储层零施工且无进度痕 / 注册表无"已算"权威字段 / 新闻关联腿三重静默 / 因子件住在一次性治理脚本目录 / 前后端调度时间两口径 | 挂起 / 施工 / **施工 P0** / 挂起 / 施工 |
| S5-G1~G6 | 硬过滤淘汰原因零落库 / 涨跌停幅度表三处并存 / 市值双真源 / 输入 fail-open 无留痕 / 停牌零产出 / 绝对额门槛未相对化 | **施工(编 C10)** / **施工 P0** / 挂起(等 SSOT 判定) / 施工 / 移交 / 挂起 |
| S6-G1~G5 | 被复用的先例本身断更（16 日+止 09-22） / 状态轴史深不对称无日历锚 / 零史期无回补路径 / 概率表归属包未指定 / 池 PIT 只在注释 | 移交+挂起 / 施工 / 施工(编 C11) / 施工 / 施工 |

**建议新立施工项（供总筹并入主 backlog，均声明内收）**
- **L04-C09** 池 PIT 读门面（并 S3-G1 + S3-G5 + S6-G5 三缺口一件解，消灭"各下游自写 shift(1)"）
- **L04-C10** 硬过滤 reject 流落库（并 S5-G1 + S5-G4 + S3-G7 漏斗存活数，一次扩列不新建表）
- **L04-C11** 池史回补（S6-G3，带 `data_source='replay'` + `version` 隔离尺；排期在真值日批稳定之后）
- 其余归并入既有 C01~C08：C01（载体→接线后验收"首行真值日"）、C02（LK-04 通电→补"注入源注册"验收）、C03（DU-11 排期紧迫度按阶梯衰减重评）、C04（改为"状态回填+淘汰率实测+fail-open 治理"）、C05（前置补 G2 机查字段）、C06（前置改为"修关联"非"补采"）、C07（换轴复用 MOD-SIG-145 范式 + 两条硬约束）、C08（补 sector_strength 注入腿缺件事实）。

## 3. 本环节穷尽性声明

**扫过的源（全部只读，未写一行业务代码）**

- 地图与战役册：`config/trading_decision_map.yaml` L2-06/L2-06-1 段（实测行号 1073-1130）、`09_link_skeletons.md` 环节 4 全节（①-⑧）、`links/L04_stock_wire/SKEL.md` 全文、`17_quantified_acceptance.md`（DU-01/02 验收线行）、`links/L01_regime/{_INDEX,s1_hmm_kernel/MINE}.md`（格式与判据对表）。
- 方法真源：`mining_sop_policy.md` 全文（§2 六向/§3 终止判据/§5 四闸/§6 自审闸，阈值与判据**零改动**）。
- 代码：`signal_ashare/core/sector_conduction.py`（99 行全读）、`sector/sector_gate.py`、`sector/sector_leader.py`、`core/candidate_pool_snapshot.py`、`core/candidate_pool_aggregator.py`（签名级）、`screening/tiered_screening_filter.py`、`signal_ashare/tradability_preflight.py`（五查函数体）、`limit_up/limit_up_ecosystem_leadership.py`、`intelligence/news_symbol_linker.py`、`strategy_pipeline/{daily_gate_snapshot,daily_decision_orchestrator}.py`、`ex_core/daban_load_producer.py`（头注）、`data/implementations/{tqcenter_provider,tdx_provider,sector_code_bridge,internal_compute_provider}.py`（grep 级）、`frontend/dashboard/api_server.py`（grep 级）。
- DDL/机账：`schemas/categories/market/{market_sector_constituent,market_stock_candidate_pool}.py`、`scripts/ch/apply_market_tables_ddl.py`、`docs/03_modules/_cross_layer/database/business_data_categories.yaml`、`data/config/tasks.yaml`（sector_constituent/index_constituent/suspend×3/daban_engine_load_daily/pattern_win_rate_materialize/池任务反查）。
- 注册表：`docs/01_policies_and_standards/_registry/catalogs/factor_registry.yaml`（**175 条逐条统计**：status/前缀分布/code_path 18·code_symbol 31·code_fingerprint 0·ic 14·ir 12·evidence 21·null_rate 0）。
- **ClickHouse 只读实测（经 `zephyr.data.ch_reader.query`，FINAL 自动注入）**：sector_constituent（含族分布/8803-8804/SCD 版本数）、sector_constituent_snapshot、sector_state、sector_list、sector_code_name_map、sector_meta、index_constituent（五指数逐指数起止）、stock_candidate_pool（存在性+行数）、daban_engine_load、market_pattern_win_rate、daily_valuation（逐日行存）、stock_daily_basic、stock_indicator、suspend、limit_up_down、stk_limit、stock_basic、ipo_schedule、news_data、news_sentiment_score、news_sentiment_window（双腿按 scope）、`system.tables`/`system.columns` 结构盘点。
- **全网检索 6 轮**（每轮双动作，全部过防噪音四闸）：①行业动量溢出/lead-lag（海通研报 BigQuant 镜像 2018、CNKI 学位论文 2025、经济关联与股票回报）②成分 PIT 与幸存者偏差（东方财富财富号 2026-09-07、同花顺量化 2026-06-09，两独立源）③换池/池维护（ESWA ranking-matching 2025、arXiv RL 组合 2026-02）④A 股情绪横截面非线性（Pacific-Basin Finance Journal 2025、IREF 2025）⑤涨跌停制度与流动性可交易性（CUHK 2019、ResearchGate 打板策略 2025、arXiv 换手约束 2025）⑥小样本格子收缩（**全部降级为题录，不入图**：工具站文档 + 镜像 PDF，不可溯原发布方）。

**仍未挖的长尾（18 条，逐簿列在各册 §⑥ 尾，此处汇总归类）**
1. 载体级：`sector_constituent_sw_history` 列与起止（可能直接解 S2-G2 归属史）；`kline_sector`/`kline_sector_880` 板块 K 线史深未测（大表查询受阻，非查无）；881 族 K 线落表位置。
2. 代码级：`instrument_master.py`（MOD-DATA-069）存储载体与 `is_suspended` 写入方（S5-T1）；`selection_funnel.py` 九阶段阈值与 yaml L3-02 对表（S3-T2）；`multifactor_synthesis/ic_ir_calc` 与 15 号文 §3.5 四门禁对表（S4-T1）；TDM L3 各节点 `factor_refs` × 注册表 175 条交叉核对（S4-T2）。
3. 数据级：新闻条数经 linker 规则可达的**个股关联上限**（S4-T3）；battle_map_05 BM-SEL-16 六件套原文与实测参数逐条对表（S5-T2）；市值五分位与 30 亿下限是否互抵（S5-T3）；`daban_engine_load` 断尾原因（S6-T2）；`fwd_ret` 既有计算件位置（S6-T3）。
4. 链路级：AutoRuntime 生产日循环是否真调 `collect_gate_snapshot`（S3-T1，决定 LK-04 终勾）；`war_pool_generator`/`mainline_probability` 自身挂点（S1-T1）；前端 D-05 龙头榜资产查重（S1-T2）。
5. 指针级：SKEL §0 所列 12 件未读指针，本班**补读/部分补读 4 件**（factor_registry 本体统计、tradability_preflight 函数体、instrument_master 注释级、news_sentiment_analyzer/llm_scorer grep 级），**仍余 8 件未读**（24/25 号策略 detail、2026-09-11-l308-aggregator-construction、69 号文 §2.16、algo_flow 出仓三件、90_methodology_open_questions、2026-09-12-fundamental-consumption-design、stk_limit S16 三级解析链、emotion_line exam_report_v1 的 C6 归因）。

**封顶判据自评**：六簿六向**无空格**（每向为"有发现"或"已查无/受阻+查法"）；父层 W0-W7 全部归位且各册首交代合并理由；未以现状规模小封任何矿；未以轮数或连续噪音封矿；本环节**不达 SEALED**（18 条长尾 + 8 件未读指针在案），交总筹按"矿脉枯竭=六向全查无+无未挖长尾"复核后决定续挖或转施工。

## 4. 边界声明（越界不挖，只登记）

- **同目录邻卷归属交代**：`du11_daily_valuation_partial_write_root_cause.md`（2026-09-25 21:52）**非本车道产物**，属 LANE-BUILD 的 DU-11 写侧根因案卷；本车道 S5 册对 daily_valuation 的逐日实测量与该卷**独立双测完全吻合**（5,002/5,003/2,504/1,500），互为旁证，故本表 files 清单不含该卷（落地时勿按"同目录同批"误并入 L04 挖矿交付）。
- 板块层内部（sector_state 算法/水温/RRG）归 L03 车道；G9 边界冲突事实已记档（S1/W0），本线按"独立层"挖。
- 池实现接线（selection_funnel→negative_veto→aggregator 三来源注册）归 **LANE-BUILD**，本线零改实现码，只挖"接完之后还缺哪些下游"（S3 全册）。
- DU-05/06/11 与 suspend 失败史、成分表刷新纪律归 **12 号文数据线**；`sector_constituent_sw_history` 判读归数据线。
- 因子存储层设计归 15 号文特征仓库线（本线只登记"零施工且无进度痕"事实）。
- 盘中事件通道与日内选股挂点归 L05/日循环编排器另案（09 号文 §8.3.2）。
- 概率表考试卡的**判据数值**（n≥30/Wilson LB/四门禁）一律未改，只登记复用关系。
