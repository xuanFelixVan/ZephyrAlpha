---
ttl: task_bound
title: L2 相位环节册——官方六段收编工程余量＋段灰度＋t0 物化链依赖
created: '2026-10-13'
session: st-condaxis-20261013
status: mining_workbook
family_id: CONDAXIS-CAMPAIGN
completes_when: L2 相位环节施工完成且随 CONDAXIS-CAMPAIGN 归档
---

# L2 相位环节册（离散段＋段灰度；唯一词表=官方情绪六段）

> 契约定位（研究档 §7.1）：回答"处在情绪周期哪一段"；首发消费方=预算带（在用）、策略适用域；判据方向=重放幂等＋段际转移准确率。
> **挖矿翻案声明（R3）**：研究稿 §6 称"四套并存词表未收编"，实查**收编登记已完成大半**——本环节主体工作是余量收尾而非从零收编。

## §1 逐项台账表

| 件名 | 仓内真源路径:行号 | 现状 | 消费方 | 缺口 | 六向定位 |
|---|---|---|---|---|---|
| 官方六段词表（唯一基准） | market_state.py:66-77（EmotionCycleSixVocab）；语义真源=vocab_legislation/01_official_state_vocabulary.md:45-50（已归档 archive/2026-10/vocab_legislation/） | ✅（立法+镜像在册） | TDM state_matrix 列轴、t0 物化链 | 无 | ①e.cycle.* 六值 ②预算带/条件轴 ③— ④— ⑤— ⑥— |
| 词表一：SentimentPhase 五段（28 号 memo） | sentiment_cycle.py:51-61 | ✅（收编登记在册） | sentiment_cycle_evaluator:47/similar_day_inference:67（02 册 E1 行） | 无（映射已登记：FREEZING→capitulation、STARTING→ignition 过渡、FERMENTING→expansion、CONSENSUS→euphoria、EBING→distribution） | ①daban 量价 ②evaluator ③区间判据 :73-130 ④原位保留 ⑤— ⑥七要素 |
| 词表二：SentimentPhase 4+1 硬标签 | market_sentiment_analyzer.py:89-96（枚举）/:989-1000（方向陷阱本尊：最热(≥80)→RETREATING）/:430（GRAYSCALE_PHASE_CENTERS） | ✅（收编登记在册+方向注记） | intraday_sentiment_loop:68/llm_premarket_analysis:135/boundary_revision_engine:87/099/101（02 册 E2 行） | 无（跨引擎传值必须经映射册 E2 行方向注记，禁直传） | ①七维分数 ②盘中回路/盘前 LLM ③灰度中心 :430 ④原位保留 ⑤— ⑥— |
| 词表三：EmotionPhase 4+1（youzi 引擎） | youzi_relay_emotion_engine.py:60-68（枚举）/:450-453（最热→MANIA 对照面） | ✅（收编登记在册+方向注记） | daban_sleeve_strategy:75/dual_engine_fusion:57（02 册 E3 行；registry:457 同步登记） | 无（同上方向注记纪律） | ①daban ②sleeve/融合 ③— ④原位保留 ⑤— ⑥— |
| 词表四：盘中五态（A3） | market_state.py:81-93（IntradayFiveVocab）+:98-104（INTRADAY_TO_SIX） | 🔨（映射在案 **proposed** 待 Owner 校准） | 盘中情绪/盘面强度轴降采样 | **EUPHORIC→IGNITION 为 proposed**（:96/:103 自标"亢奋亦可主张 EUPHORIA，等 4 态收敛专项定论"）——Q1 收编最后一块 | ①盘中判别 ②六段降采样 ③映射 dict ④待校准 ⑤— ⑥— |
| 六段历史物化链（t0 依赖） | scripts/audit/t0_six_phase_materialize.py（SH-SCRIPT-001；auto_mount.R2SIX+phase_overlay+resolve_six_phase 法定映射，PHASE_PREEMPT 优先；PHASE_VERSION=sixphase-v1，1,816 日） | ✅（production，做 T 考试族情绪轴真源件） | t0_conditional_e4_v2_exam、GPU 条件维输入包六段轴、红蓝 PIT 断言 | unrouted 762 日（41.9%，D 族冻结稿:49）r1/r2 不路由——**Q12 建议维持 A 保持不路由+卡面 bucket 单列**（冻结稿:55 未冻点 3.1） | ①宏观腿 regime_snapshot_history+微观腿 399106/EQW_ALLA ②E4 双门/GPU 包 ③零自定阈值 ④物化在产 ⑤— ⑥routed 留空串禁硬塞 |
| 段灰度输出（L2 契约"离散段＋段灰度"的后半） | market_sentiment_analyzer.py:1005（analyze_grayscale→5 维灰度概率 Σ=1+dominant_phase+confidence+fallback_triggered，BM-SEL-25 升级） | ✅（原料在产） | 现无外部消费方（纯增量契约，:62-66 注） | 六段制下的**段灰度**尚无（025 灰度是自家五段制）；需把六段物化输出配段灰度（候选=物化链加概率列或轻量映射层） | ①025 七维 ②预算带候选 ③灰度概率法已在 025 验证 ④六段版待建 ⑤— ⑥— |
| D125 折算通道（三套词汇→6 态再查表） | trading_decision_map_layering_policy.md:104（"温度计态（月12态/周三段日5档）与指标库 regime_valid 一律折算到 state_matrix 6 态再查表，防三套词汇漂移"）＋config/trading_decision_map.yaml:4369（F-C1-01 查表真源） | ✅（Owner 2026-10-05 批） | 策略路由 F-C1 | 无——Q1 收编的现成通道，新词表映射沿此登记 | ①各层温度计 ②路由查表 ③折算规则 ④— ⑤— ⑥— |
| state_vocabulary_registry 登记路径 | docs/01_policies_and_standards/_registry/catalogs/state_vocabulary_registry.yaml（REG-STATE-VOCAB-001）；执法门=state_vocab_registry_gate.py（STATE-VOCAB-REGISTRY） | ✅ | 提交面执法 | 无（Q8 答案=是：新增任何状态值先登记；本环节不新增，只校准 A3 映射） | ①— ②commit gate ③— ④— ⑤— ⑥— |

## §2 与既有资产边界

1. **收编≠重命名**：三套五段/4+1 枚举**原位保留**（02 册 disposition），跨模块取值必须经映射——L2 施工禁顺手把存量枚举改拼写（会炸 sentiment_cycle_evaluator 等 7 个在册消费方）。
2. **vs 温度计（L1）**：拿 emotion_index 连续分位冒充六段=词表越轴（market_emotion_index 注册表 hard_constraint+t0 判例明文禁）——段灰度必须从六段制内部生长（025 灰度法移植），不从 L1 分位切档。
3. **vs TDM-E-L1-S5 五档**：S5 是"日级条件档"（D20 定稿），不属情绪六段词表面——两者关系走 D125 折算通道，禁把 S5 五档登记为情绪词表第五套。
4. **vs t0_six_phase_materialize**：六段↔状态轴映射法定真源=auto_mount.R2SIX+phase_overlay+resolve_six_phase（物化件 INVARIANTS"禁自造六段映射"）——L2 任何映射变更必须先改 auto_mount 法定件+预注册卡（MODIFY-GUARD：改动=考试情绪轴变更，作废重开）。
5. **market_sentiment_panel 陷阱**：该表注册表定性=**币圈宏观情绪面板**（29 行，t0 物化件头部实证）——与 A 股情绪面同名异义，施工禁误用。
6. **PHASE_VERSION 升版纪律**：sixphase-v1 映射变更须升版禁原地改（D 族冻结稿:45）——A3 映射校准若影响 resolve_six_phase 合成，同批升版。

## §3 施工要点（实读代码的坑）

1. **A3 校准是最小施工面**：INTRADAY_TO_SIX 五行 dict（market_state.py:98-104），改动=EUPHORIC 一行的值+去 proposed 标注；但牵动立法真源（02_state_vocabulary_unification.md §3 第二步挂起项"等 4 态收敛专项定论"）——呈批包须带 4 态收敛专项的状态核实，否则校准依据仍悬空。
2. **方向陷阱双注记不可拆**：E2"最热→RETREATING"（025 自家退潮判定：阶段中心 :430 RETREATING=90.0）与 E3"最热→MANIA"（youzi :450-453 仅广度<0.4 :457 或高连板频繁开板 :461 才改判）语义相反——立法件 §3 裁定"两引擎行为各自原位保留，跨引擎传值必须经 E2/E3 方向注记；新消费方接六段按官方语义（最热=euphoria，distribution 只由派发证据触发）"——L2 施工引入新消费方时必须引用此条。
3. **段灰度输出的实现位选择**：两条路——①025 的 analyze_grayscale 旁挂六段版（同件双制，BM-SEL-25 纯增量先例可循）；②t0 物化链加概率列（改 MODIFY-GUARD 面大、须作废重开卡）。**建议①**：025 已有 fallback_triggered 纪律，六段版沿同构升级 minor。
4. **STARTING/REVERSAL 的过渡映射已定**：两套五段的"反核"均映射 accumulation/ignition 过渡、取 ignition（02 册 E1/E2 行）——段灰度若做七值（六段+过渡态）违封闭集纪律，过渡按两段概率分摊。
5. **重放幂等验收**：同码本两次重放 dominant 序列逐日一致（regime_recal_protocol §5 先例，D 族冻结稿:47 建议立为 D 族重建资格判据）——A3 校准后的验收复用此判据，六段版同标。
6. **unrouted 41.9% 与 L2 无关**：unrouted 是宏观腿 r1/r2 不映射的既定态（D125 框架内合法），L2 不得为消 unrouted 而扩六段映射（Q12 建议 A：卡面 bucket 单列）——那是宏观域的裁决面，越轴。

## §4 自审闸三态裁定

**裁定=施工（轻量）**。理由：
- R3 翻案后主体（三套词表收编登记+物化链+折算通道）已是 ✅，余量=A3 映射校准（一行+立法真源同步）+段灰度输出（025 同构升级）——量小且都有现成通道，属"终局有位、时序已到"。
- A3 校准前置=Owner 批准（语义参数，02 立法件挂起项的定论）——施工班只备呈批材料（4 态收敛专项状态+EUPHORIC 两案对照表），**不自行改 proposed 值**。
- 段灰度=施工（AI 可为，025 件 ai_autonomy=ai_modifiable，BM-SEL-25 纯增量先例）。
- 挂起面：六段↔S5 档位互映射（研究档 §11.2-1 建议）——**挂起**，依赖 Q10（"温度计≠档位计"补登裁定）先落，否则映射层级依据悬空。
