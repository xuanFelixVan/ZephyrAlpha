---
ttl: task_bound
title: L1 温度计环节册——六成分逐件挖矿＋daban 浅史回补方案＋合成分等权 vs PLS
created: '2026-10-13'
session: st-condaxis-20261013
status: mining_workbook
family_id: CONDAXIS-CAMPAIGN
completes_when: L1 温度计环节施工完成且随 CONDAXIS-CAMPAIGN 归档
---

# L1 温度计环节册（0-1 连续灰度，日频；分维度面板＋合成分）

> 契约定位（研究档 §7.1）：回答"现在市场多敢买"；首发消费方=预算带、考试条件轴；判据方向=适用域增量预测＋极端事件对照。
> 核心在册件=`src/zephyr/alt_data/emotion_index_builder.py`（MOD-ALT-EMOTION-INDEX-BUILDER，:7 experimental，:28-33 六成分，:76 观测<120→insufficient 权重重分配，:81-85 原料表，:89-124 NO-BARE-SQL 常量）。

## §1 逐项台账表

| 件名 | 仓内真源路径:行号 | 现状 | 消费方 | 缺口 | 六向定位 |
|---|---|---|---|---|---|
| C1 涨停温度（0.4 触板家数+0.3 最高连板+0.3 封住率） | emotion_index_builder.py:28、:89-93（_SQL_LIMITUP_DAILY） | 🔨（表链通、史浅降档中） | emotion_index 合成分→condition_package/sector_state_pipeline | **史浅**：daban FINAL 1,906 行仅 22 交易日（09-01→10-12），<120 观测→长期 insufficient | ①原料=market_daban_board_event:81 ②见 6_tdm ③分位法已定 ④史浅 ⑤dashboard 已有读数面 ⑥七要素在表（触板/封住/一字/首触/开板次数/封单代理/连板，skeleton_v0:41） |
| C2 晋级率（T-1 连板梯队∩T 再封住） | emotion_index_builder.py:29、:95-104（_SQL_PROMOTION，daban 自 JOIN） | 🔨（同 C1） | 同上 | 同 C1（纯 daban 自 JOIN，无外部依赖也无可替代源） | 同 C1；断供期替代面=limit_up_down 仅可替 C1 触板家数子项，**连板高度/炸板率/晋级率无替代**（skeleton_v0:156-157） |
| C3 广度（0.6 上涨家数占比+0.4 沪深300 日收益） | emotion_index_builder.py:30、:106-111 | ✅（kline 全史在产） | 同上 | 无（勿动，研究档 §8） | ①market_kline_daily:82+market_index_kline:83 ②同上 ③已定 ④通 ⑤— ⑥通 |
| C4 量能（0.5 两市成交额+0.5 换手率中位数） | emotion_index_builder.py:31 | ✅ | 同上 | 无（勿动） | 同 C3 |
| C5 两融杠杆（两融余额 20 日变化率，as-of 最近可得日） | emotion_index_builder.py:32、:118-121（_SQL_MARGIN_BAL，as-of 对齐） | ✅（半通：滞后 1-2 日已处理） | 同上 | 史浅：起点 07-20、约 40 观测 <120 门槛（skeleton_v0:58/:111）→insufficient 状态持续 | ①market_margin_trading:84（akshare_provider/miniqmt_provider 双源） ②同上 ③as-of 口径已定 ④观测数达标靠时间累积（零施工） ⑤— ⑥通 |
| C6 新闻情绪（5 日均值） | emotion_index_builder.py:33、:123 起（_SQL_NEWS_MEAN） | ✅（窗表在产，起点 02-25） | 同上 | 升级路径=LLM 打分（长尾矿脉，走 LSG 网关另立） | ①market_news_sentiment_window:85 ②同上 ③已定 ④通 ⑤— ⑥通 |
| option 衍生品维度（delta 全 0 修复） | option_sentiment.py:8/:28（delta 列全 0 实证；:15 module_id=MOD-SIG-059） | 🔨（三件套已建、delta 列不可用） | 候选=025 维度⑨（权重≤0.10 纪律） | delta 列 DEFAULT 未回填→选约不可用；iv_surface 27,881 行（2026-01-29 起）510300 3,667 行 127 交易日；08-14 源切换（miniqmt→akshare_sina 仅最近月） | ①option_iv_surface/option_kline ②025 注解维度 ③PCR/IV/Skew 已定 ④delta 回填或以最近月口径绕开 ⑤— ⑥iv 无 open_interest 列实证 |
| Gao 2025 相对情绪口径候选 | 研究档 §3.2/§8（SSRN 4122594→2025 IREF 见刊）；仓内雏形=option_sentiment 三件套 | ⬜（候选，Q-挂起项） | L1 衍生品维度面板 | 未施工：已实现矩−隐含矩之差需期权全链数据质量先行（delta 修复是其前置） | ①量价+期权 ②L1 面板候选行 ③口径见刊可引 ④依赖 delta 修复 ⑤— ⑥iv/kline 字段已核 |
| 合成分（可用成分等权） | emotion_index_builder.py:34-35（首版禁 PCA）、:365（usable 等权聚合） | ✅（机制在产） | c1_market.emotion_index 表→condition_package（v0.1.0 冻结公式）/sector_state_pipeline:59 | 等权 vs PLS 待裁（Q3 建议等权起步）；成分增删=minor、权重方案=major（契约红线 :35-36） | ①六成分 ②条件轴/预算带 ③等权起步 ④PLS 升级待增量检验 ⑤— ⑥250 观测分位窗 |
| daban 浅史回补+缺日修复 | gap_list_and_construction_proposal.md §6（复通终态：integrator 周窗重放 09-01→09-22，936→1,454 行）；核验实查 FINAL 1,906 行/22 交易日 | 🔨（Q5 第一优先，工作内容=回补+缺日） | C1/C2/E5 | ①09-25/29/30 三缺日补齐；②深史（09-01 前）akshare 涨停池族源侧仅存近约 30 交易日→**深史源需另寻**（源侧覆盖窗实查待施工班） | ①ak.stock_zt_pool_em=limit_up_pool_collector.py:280 ②C1/C2/E5 ③周窗重放法已验证 ④深史源缺口 ⑤— ⑥七要素 schema 已定 |

**状态标记证据指针**（skeleton SOP §5 纪律）：C1/C2 史浅=研究档核验更正记录②（ClickHouse 只读实查）；✅ 各项=emotion_index_builder.py 原料表常量+internal_compute_provider.py:766-767 capability 路由在册；🔨=复通但未达 120 观测门槛（builder.py:76 `_MIN_OBS=120`、:199 降档逻辑）。

## §2 与既有资产边界

1. **vs MOD-SIG-025 market_sentiment_analyzer（七维 0-100）**：025=D_ASHARE_SIGNAL 域信号件（:7 production），0-100 分制、含 distortion 降权；emotion_index=D_ALT_DATA 域市场级状态变量（0-1 分位制）。两件**不合并**（轴不同：025 是信号面综合分，index 是状态面温度计），但 L1 面板的"信号情绪"行可引 025 读数——经 4_validation 判据面统一校准口径后挂接。
2. **vs TDM-E-L1-S5 日级温度计（11 信号 5 档）**：S5 管**档**（5 档仓位条件，:650/:735 D20 定稿），emotion_index 管**灰度**（连续读数）——分层并存是 Q10 建议 A，但其依据（"温度计≠档位计"裁定）**不存在**，须先补登真裁定再动 S5（研究档 §11.2-1/Q10）。
3. **vs fear_greed 异轴顶替**：market_emotion_index 注册表 hard_constraint 明文禁异轴顶替（t0 判例，t0_six_phase_materialize.py 头部引）——拿温度计分位冒充六段词表=词表越轴，L1 与 L2 禁混。
4. **vs sector_state_pipeline**：:10-11 明文"消费 emotion_index@T close_final；板块热度禁回灌 emotion_index"（防同 ts 循环）——L1 施工不得反向引入板块热度成分。
5. **vs l9_readiness_aggregator**：:422"情绪聚合器定案挂起（纪要§8.3 不代建，f33 册）"——L1 面板化不做新聚合器，等 f33 定案。

## §3 施工要点（实读代码的坑）

1. **改公式=作废重开卡**：condition_package INVARIANTS 明文"情绪值消费 c1_market.emotion_index v0.1.0 冻结公式（本件只分档不改值，改公式=作废重开卡，st-emoreplay 纪律）"——C1/C2 史补后若分位窗重算导致全史值变，**必须走版本升 minor**（成分集变更=minor、权重=major，builder.py:35-36），禁原地改历史行。
2. **表级改写已实证**：close_final 全史由 09-23 单批 replay 建成，pre_open 2026-10-02 双行异值=改写实证（emotion_index_snapshot.py 头部）——史补作业必须经快照器留 PIT 证据，禁裸 UPDATE。
3. **stage 双态时戳**：close_final（15:10 定格）/pre_open（09:15，C1-C4 复用 T-1+C5/C6 as-of T）两 stage 各自成行——史补时两 stage 都要补，缺一档=下游 pre_open 面空洞。
4. **daban 深史源侧覆盖窗**：akshare 涨停池族（stock_zt_pool_em 等）源侧仅存近约 30 交易日是已知约束——施工班回补前先实查各接口覆盖窗，禁假设可无限回溯；深史若不可得，落点=申报"史浅为永久态、C1/C2 长期 insufficient 等权重分配运行"（机制已支持，非阻塞降级）。
5. **两融 as-of 对齐**：_SQL_MARGIN_BAL 按"最近可得日"取值（滞后 1-2 日），史补禁用"当日余额"硬对齐（会把 T+1 披露值前视进 T 日）。
6. **option delta 修复的绕行面**：即使 delta 不回填，最近月口径（当日 min expiry）跨源一致（option_sentiment.py:31-33）已立——修复方案优先评估"最近月选约+理论 delta 重算"而非等源侧回填。
7. **PIT 三段口径**：分位窗全部 ≤当根（builder INVARIANTS）；C1-C4 pre_open 复用 T-1；C5/C6 as-of 当日——任何成分改动先过这三段再动代码。

## §4 自审闸三态裁定（mining_sop §6）

**裁定=施工**。理由：
- 主判据（一票放行）：daban 浅史回补+缺日修复直接消灭 C1/C2 长期 insufficient 的人工盯守环节，向终局全貌（全自动情绪温度计）推进；Q5 已建议第一优先。
- 时序：三缺日补齐=纯机械（周窗重放法已验证）；深史回补**分两步走**——先补 akshare 可得窗（近约 30 交易日外扩实查），不可得部分申报永久史浅态（等权重分配机制已 fail-closed，不阻塞其余环节）。
- 反驳者一问（最强三条）：①深史可能根本不可得（源侧覆盖窗硬约束）→已纳入两步走方案，不可得即申报；②史补后分位全史漂移会作废 condition_package 卡→版本升 minor 纪律在案，重开卡成本可控；③等权可能弱于 PLS→Q3 等权起步+增量检验后再议升级，首版禁 PCA 判例延续。
- 权限面：C1/C2 史补=机械参数（数据源/断供补洞）=AI 自修留痕；成分增删/权重方案=语义参数=Owner 门位（5_self §3 权限分离表）。
