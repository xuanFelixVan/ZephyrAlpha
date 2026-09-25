---
ttl: task_bound
title: L04-S4 子模块挖矿簿 · 选股因子层与新闻活跃度维（因子登记/存储层/PIT 读取 + 新闻个股关联腿）
created: 2026-09-26
sid: st-qmine-20260925
lane: LANE-MINE-L04
status: MINE 完成（六向封口；W3+W6 合并成册，合并理由见 §① 末）
---

# L04 · S4 因子层 + 新闻活跃度维（W3 ⊕ W6）

覆盖父簿 SKEL.md 的 **W3（选股因子层）** 与 **W6（新闻活跃度维）** 两子块。
**合并理由（MECE 交代）**：W6 的产物在 05 号文/17 号文口径下就是一个待注册的因子（"近 30 日新闻条数十分位"，L04-C06），与本册 W3 共用同一条生命周期（registry → 存储层 → PIT 读 → IC 证据 → 接线）；把 W6 单列会与 W3 六向逐条重复，故合册不重不漏。

**① 职责一句话**：给个股层供"可回放的横截面分数"——因子定义、因子值存储、PIT 读取、IC 证据四件套，外加个股新闻活跃度这一条件维的原料与关联腿。

**② 现状实测**

| 项 | 实测值 | 出处 |
|---|---|---|
| 因子注册表真源 | `docs/01_policies_and_standards/_registry/catalogs/factor_registry.yaml`（**注意：不在 config/ 也不在 data/registers/**，SKEL W3② 只写文件名未写路径，本册补路径） | 本册 Glob/Grep 定位 |
| 注册规模（实测逐条统计） | **175 条**：status=candidate 170 / experimental 4 / deprecated 1（与 SKEL 基线一致）；前缀分布 TECH 31、MOM 30、SENT 23、INTRADAY 16、FQ 6、EXP 6、QUAL 2 | 本册 yaml 解析实测 |
| 机查"已算/未算"字段（实测） | `formula` 175/175、`version` 175/175、`pit_policy` 175/175、`entry_role` 175/175、`doc_ref`/`module_id` 175/175；**`code_path` 18/175、`code_symbol` 31/175、`code_fingerprint` 0/175、`evidence` 21/175、`ic` 14/175、`ir` 12/175、`null_rate` 0/175** | 本册 yaml 解析实测 |
| 因子值存储层 | **实测：CH 全库内 name LIKE '%factor%/%feature%/%alpha%' 只有 `c1_market.adj_factor`（21,055,072 行，复权因子非本域）→ 15 号文 §3.4 的"CH 特征宽表存储层"至今零施工** | 本册 `system.tables` 查询 |
| 因子实现域（文档基线） | `factor/core/factor_dag/dag.py` + 双执行器 + incremental_compute 已施工；`factor/indicator_reader.py`（PIT 入口，唯一消费方=demo）；`analysis/multifactor_synthesis.py`+`ic_ir_calc.py` | SKEL W3② 基线（本册未复核逐行） |
| 真消费因子数 | 文档基线 4 条有真码消费（FCT-FQ-001/002、FCT-EXP-002/006）；本册机查佐证=`ic` 字段仅 14 条有值、`ir` 12 条 → **注册表自身已能机查"14/175 有 IC"**（口径比 14 号文"仅 4 已算"宽，两者不矛盾：14 条有 IC 数字 vs 4 条有生产消费码） | 14 号文族⑥ + 本册实测 |
| 新闻原料（实测行存/新鲜度） | `c3_fundamental.news_data` **FINAL 7,931,664 行**（system.tables 未合 8,188,763），`publish_time` 2010-01-02..**2026-09-25 23:00**（当日到，在产健在，与 12 号文 :75 一致） | 本册 CH 实测 |
| 打分腿（实测，**改判 DU-05**） | `c3_fundamental.news_sentiment_score` FINAL 7,733,898 行；`max(publish_time)=2025-09-09`（语料断点复核成立）；**但 `max(scored_at)=2026-09-24 07:48 UTC`，且 `WHERE toDate(scored_at)>=today()-7` 命中 7,733,898=全表** → 打分器在近 7 日内**把全表重打了一遍**，只是**没有新语料可打** → 病根不在打分器，在"新语料进不来" | 本册 CH 实测 |
| 窗口腿（实测，**改判 DU-06**） | `c1_market.news_sentiment_window`（列含 `window_ts/window_end/window_type/scope/symbol/sentiment_index/avg_polarity/positive_count/.../window_date`）：scope='market' 186 行（2026-02-24..09-24，日均 1 行）；**scope='symbol' 19,635 行 / 4,857 只 / 2026-02-24..2026-09-24**，**日均仅 163.6 只（min 1 / max 603）** → SKEL W6②"symbol 级止 2026-08-20（DU-06）"**已被实测推翻：symbol 腿已到 09-24，但覆盖率只有 3%/日（163/5,400）** → 病从"断更"变"稀疏" | 本册 CH 实测 |
| **关联腿根因（实测）** | `SELECT countIf(related_symbol!=''), countIf(length(related_symbols)>0), count() FROM news_data WHERE toDate(publish_time)>=today()-30` → **`0 / 0 / 64,689`** = 近 30 日新闻的**个股关联字段 100% 空**（日均 2,156 条全无关联） | 本册 CH 实测 |
| 关联腿码件 | `src/zephyr/intelligence/news_symbol_linker.py`：优先级①公告 related_symbol(s) 直用（confidence=1.0）②6 位代码显式匹配须命中词表 ③简称归一化最长匹配；**零命中→symbols=() 即 market 级；词表为空 fail-open 不抛（全部 market 级）**（头注 :8/:23/:73/:243-256）→ 与实测"只有 163 只/日有 symbol 行"同构：**fail-open 静默把个股维降级成市场维** | 本册 grep |
| 窗口写方与调度 | 写方=`intelligence/news_sentiment_analyzer.py:31`（window_type='1h'）与 `news_llm_scorer.py:48`（data_source='llm' 对照期，C6 仍消费 rule 值）；构建脚本在 `scripts/governance/meta_question/wo_a2legs/{backfill_news_sentiment,build_news_sentiment_window}.py`（治理一次性脚本目录，非正式生产包）；`data/scheduler.py:270` 存留问题标记 `news_sentiment_window_no_scheduler_wiring 治本`；`data/calendar_coverage_checker.py:110` 明示"**news_sentiment_window 不入默认名单**（未注册 TableRegistry 品类）" → **该表不在断更哨兵覆盖面内**（稀疏/断更无人知，与实测一致） | 本册 grep |
| 调度口径劈叉（新发现） | 前端资产表 `frontend/dashboard/api_server.py:1320` 记 `news_sentiment_window` = "每日 08:20 自动打分"，而 12 号文补采表记 20:08 nightly cron → **同一表两个时间口径**（一个在仪表盘、一个在普查册），机查真源缺位 | 本册 grep |
| TDM 声明因子（文档基线） | L3 节点 factor_refs 族：FCT-MOM-003/009/010/016/029/030、FCT-QUAL-001、FCT-TECH-070/071/077/083/085、FCT-SENT-007、FCT-FQ-004（yaml 逐节点） | SKEL W3② 基线（本册未逐节点复核，长尾 T2） |

**③ 六向台账**

| 向 | 发现（内部反查 ＋ 全网搜索） |
|---|---|
| ①上游该喂什么 | 内部：因子定义面已齐（175 条 formula/pit_policy/universe/neutralization/lookback 全有值）；**缺的是"新闻→个股"关联腿这一上游**：实测近 30 日 related_symbol/related_symbols **全空**，linker 的第一优先级输入（公告直给）实际为 0，只能退到规则匹配；此外 `c3_fundamental` 29 表中 10 表 ZERO 消费（14 号文族⑧）也是"该喂未喂"。外部：**用共同搜索/关注度网络反推个股关联**是可考虑的第二关联源——《基于投资者在线共同搜索的股票网络和联动效应研究》（人发镜像 rdfybk，2026-08-19 http://www.rdfybk.com/qw/detail?id=926498 ）单源，**待验证级不入图**，仅登记为换轨候选 |
| ②下游该喂谁 | 内部：因子值的下游=①L3-03 双池评分与 L3-07 sleeve 链（需 `code_path` 非空才可算，实测仅 18/175 有码路径）②multifactor_synthesis 合成 ③池快照 `score_components` 列（S3 实测该列缺省 `{}`，即因子明细的落库位已留、无人填）④L04-C07 个股概率表的条件轴候选。外部：因子→组合的下游范式（截面归一 + TopK 换手）已在 SKEL §4 入图（qlib），沿用不重复登记 |
| ③算法/机制业界学界 | 内部：现役=FactorDAG 双执行器 + incremental_compute（15 号文 §3.4），IC 阈值四门禁在 15 号文 §3.5；注册表已含 `decay_halflife/decay_detection_method/last_decay_scan_at/turnover/capacity` 字段但**几乎无值**（`null_rate` 0/175）→ 字段先于数据。外部（两独立源，可入图）：A 股横截面收益与情绪/关注度**呈非线性且需条件化**——《Understanding the role of sentiment beta in China》ScienceDirect / Pacific-Basin Finance Journal（2025-06-01 https://www.sciencedirect.com/science/article/abs/pii/S0927538X2500037X ）与《Nonlinearity in the cross-section of stock returns: Evidence from China》ScienceDirect（2025-01-27 https://www.sciencedirect.com/science/article/abs/pii/S1059056023000217 ）→ **本册判：现役"z-score+rank_pct 线性合成"与该结论不完全适配**，十分位/分档口径（17 号文）正是非线性可容形态，故 L04-C06 的"近 30 日条数十分位"设计方向无需改，但因子合成阶段二（L04-C05 之后）应把"单调线性"假设列为待检验项。**A 股适配闸**：两源均为美股方法迁移至 A 股的检验，结论一致要求"散户主导/换手高"下的情绪指标改以**关注度（条数）而非情感极性**为主载荷——与本册实测"极性与语料同断、条数可当日更新"互相印证，支持 C06 选条数维 |
| ④后端代码缺什么 | 内部缺四件——(a) **因子值存储层零施工**（实测全库无特征宽表）→ 一切"IC 可机查"都只能靠注册表手填字段；(b) `indicator_reader`→`multifactor_synthesis` 断链（CNS-01 沿用）；(c) **注册表机查面缺"已算/未算"的权威字段**：`code_fingerprint` 0/175、`null_rate` 0/175 → L04-C05 验收"逐条已算/未算可机查"当前**无字段可机查**，需先把 `ic/ir/evidence` 的填写升为 gate 或补 `computed_at` 列；(d) 新闻关联腿无失败可见性（linker fail-open + 表不在哨兵名单）。外部：已查无（查法：以"open source factor store ClickHouse point-in-time"检索未见维护活跃件；qlib 的 provider 层与 15 号文"不引入重型框架"裁定相冲，已在 §4 判过，不重开） |
| ⑤前端怎么呈现（只登记） | 内部：`api_server.py:1320/:1461` 已把 `news_sentiment_window` 登记为"新闻情绪窗口"资产并给排期文案（**但排期文案与真源劈叉，见 §②**）→ 前端已消费该表名，构成"前端显示的调度时间与人手写的口径"这一人工环节，终局要机查。外部：已查无（查法：因子/情绪呈现惯例无争议，登记不施工） |
| ⑥数据字段有没有 | 内部逐字段：`publish_time/title/content/summary/source/source_url/related_symbol/related_symbols/sentiment_score/sentiment_label/quality_flag` 均在 news_data（实测列清单）；**"字段在但 100% 空"的有两个（related_symbol、related_symbols）**→ 闸 4 的教科书案例：news_data 行存 8M、当日到，**但"个股级新闻活跃度"不可得**，因为关联字段断供；窗口腿 `sentiment_index/avg_polarity/positive_count/total_count` ✓且当日到（market 级）。质量画像（本册补）：news_data 近 30 日 64,689 条（日均 2,156）；symbol 窗口日均 163.6 只、最小 1 只、最大 603 只（波动 3.7 倍）；打分语料断 2025-09-09（距今约 12 个月）。外部：业界"新闻活跃度"口径=条数/提及强度（mentions）而非情感分，与本册 A 股适配闸结论一致 |

**④ 缺口清单**（沿用 L04-Cxx／CNS-xx／DU-xx；新缺口续编并注"册内未见"）

| 编号 | 内容 | 状态 |
|---|---|---|
| L04-C05/C06（既有） | L3 声明因子计算链 / 新闻活跃度维因子 | 沿用；本册补**前置改判**（见下三行） |
| CNS-01 / CNS-09（既有） | indicator_reader→合成断链 / belongs_to_strategies 回填 | 沿用；本册实测 `belongs_to_strategies` 非空 **0/175**、`code_path` 非空 18/175 作为验收基线数字 |
| **DU-05（既有，本册改判性质）** | 原记"news_sentiment_score 停摆 1 年+" → 实测**打分器近 7 日全表重打**（scored_at=2026-09-24），真因=**上游语料无新条目进打分集**（关联腿空）→ 从"补采/修接线"改判为"修关联" | 改判（移交数据线复核生产 SQL） |
| **DU-06（既有，本册改判性质）** | 原记"symbol 腿止 2026-08-20" → 实测已到 2026-09-24，**新病=稀疏（日均 163 只/日，约 3% 覆盖）**；12 号文序 6"修接线即回"判语需重估 | 改判 + 加厚 |
| **L04-S4-G1** | 因子值存储层（CH 特征宽表）**零施工且无任何施工痕**（实测全库无表）→ L04-C05 的 IC 证据只能落在注册表字段，无法回放 → **册内未见**（15 号文记"待施工"，但此后至本册无任何进度登记） | 新登（实为 15 号文旧账的进度证伪） |
| **L04-S4-G2** | 注册表无"已算/未算"权威机查字段（code_fingerprint 0/175、null_rate 0/175、ic 14/175）→ C05/C06 验收口径不可机查 → **册内未见** | 新登 |
| **L04-S4-G3** | 新闻个股关联腿 100% 空 + linker fail-open + 表不入哨兵名单 = **三重静默**（个股新闻维在任何时点崩掉都无人知）→ **册内未见** | 新登 |
| **L04-S4-G4** | 因子构建脚本落在 `scripts/governance/meta_question/wo_a2legs/`（一次性治理脚本目录）而非正式生产包 → 永久系统四要素（自动触发/运行/维护/关闭）不成立 → **册内未见** | 新登 |
| **L04-S4-G5** | 前端资产表登记的 `news_sentiment_window` 排期（08:20）与普查册（20:08）两口径并存，无机查真源 → **册内未见** | 新登 |
| DU-11/D19/D21（既有） | 估值部分写入 / Universe 剔除浅史 / 流通股本 | 沿用（W4 册引用） |

**⑤ 自审闸三态裁定**

| 项 | 裁定 | 理由（量尺=终局全貌） |
|---|---|---|
| G1 因子存储层 | **挂起排期（不封矿）** | 终局必须要（无人盘要回放任意日任意因子值必须有库）；解锁条件=①L04-C05 首批 ≥3 条因子出 IC（先证"算得出"）②15 号文 §3.4 存储层设计补齐"分区键+PIT 读法+版本"三要素；禁以"现状只有 14 条有 IC、规模小"作封矿理由（AI 系统性偏差条款）；同时**禁现在就把宽表建空**（世界地图完备优先，先设计后施工） |
| G2 机查字段 | **施工（P1，随 C05 同批）** | 补 `computed_at`/`code_fingerprint` 两字段 + 生成器回填 = 把"哪些因子真的算了"从人问人变成机查；消灭一段固定人工盘问，主判据放行；净零：不新建注册表，扩既有 175 条 schema |
| G3 关联腿三重静默 | **施工（P0，本册头号）** | 一个 fail-visible 断言（关联非空率 <阈值即告警/落 issue）+ 把该表纳入 `calendar_coverage_checker` 默认名单，即消灭"人工发现新闻维已死"；这是"字段在≠数据可得"的标准治理动作（SOP 闸 4 成例同族） |
| G3 之补语料/重挂管线 | **移交数据线（挂起）** | DU-05/06 的补采与生产 SQL 判读归 12 号文班；本环节交付根因证据链（关联空→语料断→稀疏）即尽责，禁越界挖邻域 |
| G4 脚本归属 | **挂起排期** | 升永久管线的动作应与 C06 因子注册同批（一次到位建"自动触发"），先搬文件后接调度=两次返工；解锁条件=C06 立项 |
| G5 排期口径劈叉 | **施工（P3 顺手）** | 前端 `api_server.py` 该条改由 tasks/scheduler 机查生成（静态清单禁手工维护，宪法 §9.5）；单条改注记成本极低 |

**⑥ 挖矿日志**

| 轮 | 矿脉 | 判定 | signal/noise 与归因 |
|---|---|---|---|
| R1 | 内部：注册表定位 + 规模/字段逐条统计 | signal（改判级） | 机查字段真实覆盖率量化（18/31/0/14/12/0）；注册表实际路径与 SKEL 记载不同 |
| R2 | 内部：CH 实测特征宽表存在性 | signal | 全库无因子/特征存储表（仅 adj_factor），15 号文"待施工"至 2026-09-26 仍未开工 |
| R3 | 内部：CH 实测新闻双腿（语料/打分/窗口） | signal（三处改判） | DU-05/DU-06 性质改判 + 关联字段 100% 空根因 |
| R4 | 内部：linker / analyzer / scheduler / 哨兵名单 grep | signal | fail-open 语义 + 不入哨兵名单 + 脚本目录归属 + 前后端口径劈叉 |
| R5 | 外部：A 股新闻情绪/横截面非线性（1 轮） | signal 2 / noise 3 | noise 归因=①Baidu 学术聚合页（无原始发布方/年份，闸 1 剔）②豆丁网转载（不可溯）③气候关注度类（主题漂移，与本维无关）；有效两源=ScienceDirect 2025 两篇 |
| R6 | 内部：L3 节点 factor_refs 逐节点对表 | **未做**（预算内舍去） | 转长尾 T2 |

**长尾（本册调研未尽，明确列出）**
- T1 `multifactor_synthesis.py` / `ic_ir_calc.py` 逐行读 + 现役 IC 门禁与 15 号文 §3.5 四门禁对表（属施工级，SKEL §0 已列 90_methodology_open_questions.md 未读）。
- T2 TDM L3 各节点 `factor_refs` 与注册表 175 条的逐条交叉核对（哪些 FCT-id 在图上但不在册、哪些在册无码）。
- T3 个股新闻条数的**可达上限**：news_data 是否含足够 title/正文信息让 linker 规则匹配到 5,400 只（本册只测"现在 0 关联"，未测"可修到多少"）。

**本册封矿判据自评**：六向已填（含一处"已查无+查法"、一处"未做转长尾"），T1-T3 未清空 → **状态=MINING（长尾在册）**。
