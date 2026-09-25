---
ttl: task_bound
title: L05 个股做T · 子模块深挖总勾表与穷尽性声明（六矿 43 条新缺口）
created: "2026-09-26"
sid: st-qmine-20260925
lane: L05 个股做T（深挖车道，只读挖掘+写文档，零 git 操作）
family_id: L05-T0-MINE-INDEX
inputs:
  - docs/_working/decision_map_campaign_20260924/links/L05_t0/SKEL.md（环节骨架，本表只挖其缺口面，不改其判定）
  - docs/01_policies_and_standards/sop/mining_sop/mining_sop_policy.md §2/§5/§6（六向/四闸/自审闸）
---

# L05 · 个股做T 子模块深挖 总勾表

> 与 SKEL 的关系：SKEL §6 已判 47/48 子块 SEALED（挖的是**骨架完成度**）；本表挖的是**同一骨架之下的缺口面**（口径实现细节、数据质量画像、消费与注册正门）。两轴正交，本表**不改** SKEL 任何三态判定与判据阈值。

## 1. 六矿总勾

| 子模块（slug） | 覆盖 SKEL | 三态裁定 | 新缺口 | 一句话结论 |
|---|---|---|---|---|
| `period_axis_semantics` | §5 D1（L05-C03） | 施工（披露小件）+ 部分挂起 | 6（L05-PA-G01..G06） | 120min 唯一真源=常量拒入；60min 档样本底与其它档不同；仓内 bar 合成语义两套并存无对账 |
| `rule_card_candidate_surface` | §4 C 族（L05-C03 扩面） | 候选池成立（禁自行加卡）+ 小件施工 | 8（L05-CR-G1..G8） | 卡化硬边界=**同日两腿配对契约**（`cost_trio_exam.py:78-90`），跨日腿族结构性不可卡而排除清单缺此条 |
| `tick_imbalance_material` | §4 C-F5 / §5 D5（L05-C08/C13） | 挂起排期（主）+ 1 小件施工 | 8（L05-TK-G1..G8） | 一档 89.5 亿行但**研究窗交集仅约 165 交易日**；五档研究窗 0 行且几乎只剩一个月滚动料 |
| `etf_t0_cost_and_pool` | §5 D4（L05-C06/C13） | 施工（三小件）+ 挂起 | 8（L05-ET-G1..G8） | 仓内已并存两套 ETF 往返成本口径（31.2bp vs ≈11.7bp 档位代理，差 2.7 倍），"逐只实测"件不存在 |
| `news_dimension_pit` | §5 D3（L05-C11） | 1 小件施工 + 挂起 + 1 永久留案 | 7（L05-NW-G1..G7） | 归因是"采集侧丢失"非"无料"（巨潮 98.2 万行零归因）；但历史段 `crawl_time` 全缺 ⇒ 可见时刻永不可证 |
| `state_match_downstream_surface` | §5 D2（L05-C04/C10） | 施工（三小件）+ 挂起 | 6（L05-DS-G1..G6） | 矩阵现生消费者=0（二次实证 LK-05）；接线配方只覆盖旧包；做T 试验数不入 DSR 分母 |

合计：6 矿 / **43 条新缺口**（其中各矿 §⑤ 自判"可施工小件"共 15 条——PA 4 / CR 3 / TK 1 / ET 3 / NW 1 / DS 3，全部为披露、登记、防呆、画像级，**零新判据、零阈值改动、零新规则卡**）。

## 2. 六向丰贫榜（跨六矿汇总）

| 向 | 丰贫 | 依据 |
|---|---|---|
| ⑥数据字段 | **最富** | 六矿全部在此出硬数（表列面/填充率/日期范围/时区类型/重复率），且多条直接改写在册结论 |
| ②下游 | 富 | 消费面为零=可登记的负发现密集区；跨链消费点（L04-C07 概率表）在此接上 |
| ④后端 | 中富 | 复用件盘点（`cost_model_calibration` 地板佣金族、`resample_period` symbol-agnostic）省掉未来重造 |
| ③算法/机制 | 中 | 外部题录全部经 Crossref 取回（DOI+发布方+年份）；多数为单源→按闸 2 只登记不入图 |
| ①上游 | 中贫 | 主要产出是"应喂而未喂"清单（amount 列、公告归因、母单起止字段），无新方法论 |
| **⑤前端** | **最贫（六矿全阴性）** | 六矿此向均无消费者无呈现件；按 SOP §8 记"内部轮即够"，未硬造外部惯例引文 |

## 3. 已过四闸的外部论断（本环节唯一入图集）

| 论断 | 来源（URL+发布方+年份） | 独立源数 | 状态 |
|---|---|---|---|
| 日内开盘段信息可延续至收盘（r04 ORB 的方法族依据） | Gao/Han/Li/Zhou《Market Intraday Momentum》SSRN 2014 https://doi.org/10.2139/ssrn.2440866 ；Jin《Market Intraday Momentum in Japan》SSRN 2024 https://doi.org/10.2139/ssrn.4816793 ；Xu《Reversal, Momentum and Intraday Returns》SSRN 2017 https://doi.org/10.2139/ssrn.2991183 | 3（不同团队） | 入图（已过 A 股适配闸：只取日内形态，"次日腿"因同日两腿契约驳回） |
| 回测须配 PBO/DSR 族多重检验校正（17 §三.2 双轨判据的外部依据，**不改阈值**） | Bailey/Borwein/López de Prado/Zhu SSRN 2013 https://doi.org/10.2139/ssrn.2326253 ；同文期刊版 *JCF* 2016 https://doi.org/10.21314/jcf.2016.322 | 2 记录（同团队）→ 判"待补独立第二团队" | 登记 |
| LLM/新闻情绪收益预测的前视偏差是可研究缺陷 | Glasserman & Lin SSRN 2023 https://doi.org/10.2139/ssrn.4586726 ；*JFDS* 2023 https://doi.org/10.3905/jfds.2023.1.143 | 2 记录（同团队） | 登记 |
| 新闻活跃度与情绪指标是两条不同轴 | Heston & Sinha《News versus Sentiment》SSRN 2013 https://doi.org/10.2139/ssrn.2311310 | 1 | 待验证 |
| 盘口失衡/OFI 类信号族（法 5.1 依据） | Yagi 等 *Complexity* 2023 https://doi.org/10.1155/2023/3996948 ；Zhu 等 SSRN 2023 https://doi.org/10.2139/ssrn.4513622 ；Dong 2024 https://doi.org/10.63575/cia.2024.20204 | 3（不同团队，均非 A 股一档口径） | 登记（不入图为方法，仅定义族） |
| 开源标准件候选：PBO 计算 | `pbo` CRAN 包（Barry 2014）https://doi.org/10.32614/cran.package.pbo | 1 | 只登记依赖候选，不引入 |

**未过闸如实记录**：A 股 ETF 是否免印花税/过户费（关系到 31.2bp 对 ETF 的口径错配方向）——本环节**未取到权威源**，挂"待验证"，禁当既成事实使用（见 `etf_t0_cost_and_pool` L05-ET-G7）。
**已查无（含查法，见各件日志）**：分钟 bar 分桶对齐的公开标准实现、网格交易盈利的可信学术源、新闻 PIT 审计标准件、同类呈现惯例。

## 4. 本环节穷尽性声明（对照 mining_sop §3 终止判据）

1. **已挖到底的**：SKEL §5 Owner 方法论六条（D1-D6）之中，D1/D2/D3/D4 四条已各自成矿并给出可机检判据；SKEL §4 的 34 法可卡性已按"输入可得性 × 口径可卡性"二分穷尽（含排除清单的两处缺项）。
2. **未挖长尾（如实列出，不宣称枯竭）**：
   - L1 `data/backtest_artifacts/t0_rule_engine/` 与 `t0_state_match_matrix_*.csv` 的**实测格分布**（各相位/周期实际 n、INSUFFICIENT 占比）——LANE-T0 在跑，本车道禁碰其产物，属**交接项非遗漏**。
   - L2 分钟库质量画像三项：零成交分钟 bar 是否入库、缺 bar 日按周期分布、`kline_5min` 原生 vs 1min 派生对账（禁跑批，让路）。
   - L3 ETF 宇宙规模 `uniqExact(symbol)`、`etf_share`/申赎面普查、跨境 ETF 涨跌幅适配。
   - L4 个股 `kline_15/30/60min` 的 `amount` 列在研究窗的完整度（分钟面成交额维若能补，可解锁 A1 量能闸门分钟原生）。
   - L5 SKEL §5 D6 自陈的唯一未探项 `exam_loop` 4 件源码（本矿未重复登记，承 SKEL MINING 状态）。
   - L6 `publish_time` vs `full_publish_time` 语义差抽样、`quality_flag`/`direction` 取值字典。
   - L7 转债族（C-F7）作为"真 T+0 主场"的独立挖矿（其成本 1~8bp 使盘口/网格信号唯一起死回生的场所——本矿判定它是 L05 里终局价值最高的外溢方向，**属另一条矿脉，本环节未开**）。
3. **封矿口径**：本环节 **不封矿**（存在上述 7 条长尾，六向中⑤前端虽全阴性但其余五向仍在出发现）。各矿内部的"永久留案"仅两处（新闻 `keyword` 模糊归因通道、日频顶替日内），性质=已判不做的可行通道留案底，非矿脉枯竭。
4. **判据零改动声明**：31.2bp / ≥30bp 前置 / 30 对土规 / WFE≥50% / Wilson LB 衰减≤30% / 周期集 {1,5,15,30,60}min / 5,853 只 / 研究窗 2021-09→2025-09-09 全部原样引用，本环节新增的任何"口径错配"发现均以"须另立预注册卡或 Owner 门位"收口，未改一字。
5. **零越界声明**：未跑任何批算、未读/未写 LANE-T0 产物与进程、未起 GPU、未 `git add/commit/push`、未改 SKEL 与他人件、未新增规则卡；CH 查询全部 `DatabaseService` 只读探针且限于元数据/边界/小样本聚合；临时探针脚本住 `.runtime/tmp/`。

## 5. 交接指针

- 待落清单（唯一出口=LANE-LAND）：`docs/_working/decision_map_campaign_20260924/cmd_successor_20260925/landing/lane_mine_l05.yaml`。
- 本表 43 条缺口的**统一编号归口**由总筹裁定（各矿前缀 `L05-{PA,CR,TK,ET,NW,DS}-G*` 为车道内局部名，防撞号）。
