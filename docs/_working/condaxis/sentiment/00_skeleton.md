---
ttl: task_bound
title: 情绪线环节骨架总册——四层契约 L1-L4 → 环节映射＋封顶声明
created: '2026-10-13'
session: st-condaxis-20261013
status: mining_workbook
family_id: CONDAXIS-CAMPAIGN
completes_when: 情绪线各环节施工完成且随 CONDAXIS-CAMPAIGN 归档
---

# 情绪线环节骨架总册（条件轴总包战役 st-condaxis-20261013 · 情绪域挖矿车道）

> **上游输入**：[研究档](../00_inputs/2026-10-13-sentiment-output-contract-research.md)（含文末核验更正记录）｜方法论=[mining_sop](../../../01_policies_and_standards/sop/mining_sop/mining_sop_policy.md)+[skeleton_mining](../../../01_policies_and_standards/sop/mining_sop/skeleton_mining_policy.md)。
> **两条已更正事实（本册全程遵守，禁回退旧表述）**：
> ①"温度计≠档位计"**在册裁定不存在**（ruling_registry.yaml #400 实为定桩战役纪要存真，撞号），Q10 依据悬空，P1 呈批须先补登真裁定；
> ②daban 已于 09-22 复通，DB 实查流至 10-12（FINAL 1,906 行/22 交易日，09-01→10-12），真缺口=**史浅（<120 观测→C1/C2 INSUFFICIENT）+09-25/29/30 三缺日**，Q5 工作内容="浅史回补+缺日修复"。
> **本册只挖不建**：零代码/零配置/零注册表改动；所有施工建议以台账+要点形式留矿，待总包呈批后由施工班领卡。

## §1 四层契约 → 环节映射（骨架路由表）

四层输出契约（研究档 §7.1，待批 v0）映射到本子树六件环节册：

| 层 | 形式 | 环节册 | 核心在册件 | 首发消费方 |
|---|---|---|---|---|
| L1 温度 | 0-1 连续灰度日频＋分维度面板 | [1_L1_thermometer.md](1_L1_thermometer.md) | emotion_index_builder 六成分（MOD-ALT-EMOTION-INDEX-BUILDER） | 预算带、考试条件轴 |
| L2 相位 | 离散段＋段灰度；唯一词表=官方六段 | [2_L2_phase.md](2_L2_phase.md) | EmotionCycleSixVocab＋t0_six_phase_materialize 物化链 | 预算带（在用）、策略适用域 |
| L3 事件 | 有限封闭事件集（触发+置信度+PIT 滞后） | [3_L3_events.md](3_L3_events.md) | MOD-SIG-099/101＋TDM-E-L1-S3 口径 | 大盘班拐点确认器（主接口） |
| — 判据 | 校准/区分度/事件命中率三判据机械化 | [4_validation.md](4_validation.md) | brier_calibration＋emotion_linkage_exam 先例 | 周批裁判（资格灯） |
| — 自维持 | 日批/周批/月批回路＋权限分离表 | [5_self_sustaining.md](5_self_sustaining.md) | daily_kline SUCCESS 事件门族 | 全自动闭环 |
| — 接线 | §7.5 三线接口→TDM 节点挂接 | [6_tdm_wiring.md](6_tdm_wiring.md) | trading_decision_map.yaml 挂点缺口 | TDM 地图 |
| L4 预测面 | 明日情绪概率＋盘中滚动 | **挂起不建**（Q6 已建议：TDM-E-L0-04 在册，重复建设违内收） | intraday_tomorrow_forecast | 隔夜仓位微调 |

**L4 边界声明**：L4 归 TDM-E-L0-04（config/trading_decision_map.yaml:350 起，module_mounts=MOD-PLAN-004/007+MOD-RK-20/23，四时点 10:00/11:00/13:30/14:30，D123-①②③ 三处反哺），情绪线只在 4_validation 为其提供校准判据复用面，**不在本子树新开 L4 环节册**（防两源）。

## §2 环节总台账（状态标记纪律：✅实查在产/🔨在建/⬜空白/💰花钱/🌑不可得）

| 环节 | 逐项数 | ✅ | 🔨/testing | ⬜ | 💰/🌑 | 汇总数源 |
|---|---|---|---|---|---|---|
| L1 六成分＋合成 | 8 件 | 4（C3/C4/C6 原料+表链） | 2（C1/C2 史浅降档中） | 2（option delta 修复🔨外围⬜、Gao 口径候选⬜） | 0 | 1_L1 §1 |
| L2 词表收编＋物化 | 7 件 | 4（E1/E2/E3 收编登记＋六段物化） | 1（A3 映射 proposed 待校准） | 2（段灰度输出、S5↔emotion_index 映射） | 0 | 2_L2 §1 |
| L3 八事件 | 8 件 | 0（无一件有运行时消费方） | 4（E1/E2/E3/E8 载体=099；E4 口径=TDM S3 在册） | 4（E5/E6/E7 待定义或史浅） | 0 | 3_L3 §1 |
| 三判据 | 7 件 | 3（Brier 先例/联动考先例/闭卷纪律） | 1（区分度单调性检验有雏形） | 3（概率含义声明、事件命中率规格、资格灯落表） | 0 | 4_validation §1 |
| 自维持回路 | 6 件 | 3（日批事件门/快照器/监控族） | 1（周批裁判先例= weekend 系） | 2（资格灯写位、月批呈批包模板） | 0 | 5_self §1 |
| TDM 挂接 | 7 件 | 2（L2 相位→预算带在用；S3 在册） | 1（025 两下游接线待排期） | 4（099/101 挂 S6、emotion_index 表 TDM 节点、unrouted fail-closed） | 0 | 6_tdm §1 |

## §3 挖矿日志（mining_sop §7 纪律）

| 轮 | 矿脉 | 判定 | 关键产出 |
|---|---|---|---|
| R1 | 研究档 17 条核验事实逐条抽验 | signal | 全部坐实；行号微调 3 处（025 CONSUMERS :5 非 :6、builder experimental :7 非 :6、module_id :20 非 :18——研究档行号按内容行偏移 1-2 行，语义零偏差） |
| R2 | 099/101 无消费方复认 | signal | 坐实+精化：bottom_confirmation_entry.py:21 引用 099 系 docstring 分工对账（"IC 加权多维确认 vs 双冰点事件"），非运行时消费；`__init__.py:30/:42` 仅包导出 |
| R3 | 四套词表收编现状 | signal（翻案级） | **收编登记已完成大半**：state_vocabulary_registry.yaml + 02_state_vocabulary_mapping_register.md E1/E2/E3/A3/E11 逐套登记官方映射+方向陷阱注记（02 册 :45-47/:24）。研究稿 §6"四套并存未收编"实况=登记在册，余量=INTRADAY_TO_SIX proposed 项校准+段灰度输出——2_L2 主体工作比研究稿预估轻 |
| R4 | L3 八事件载体全域 grep | signal | E4 载体=TDM-E-L1-S3:524"连续两天负溢价=退潮确认"＋lhb_premium_analyzer；E5 算法载体=sentiment_cycle.py:203 explosion_divergence（炸板率公式）；E6"放量反扑"**全仓零命中**（需新定义坐实）；E7=sentiment_cycle.py:201-202 连板高度归一 |
| R5 | t0 物化链+事件门 | signal | t0_condition_pack.py:32-41 事件链（daily_kline SUCCESS→t0_condition_pack_due→三步串行）；t0_six_phase_materialize.py 头部（auto_mount.R2SIX 法定映射、market_sentiment_panel 系币圈面板的坑、禁温度计分位冒充六段） |
| R6 | emotion_index 表消费方全域反查 | signal | sector_state_pipeline.py:59/:109 在读表（板块偏好重映射）；condition_package INVARIANTS 明文消费 v0.1.0 冻结公式——**表有消费方，缺的是 TDM 地图节点**（6_tdm 核心精化） |
| R7 | 校准/Brier 先例 | signal | plan_engine/brier_calibration.py＋intraday_tomorrow_forecast.py＋judgment_ledger/settler（B1/B2 先例族）；fexam/emotion_linkage_exam.py（裁定#489③ v1 三线） |
| R8 | 快照器与 PIT 证据 | signal | scripts/data/emotion_index_snapshot.py（append-only；pre_open 2026-10-02 双行异值=改写实证在案） |

**长尾矿脉清单（未挖，留待施工班或邻车道）**：①LLM 新闻打分升级路径（FinGPT 类，须走 LSG 网关，另立矿脉）；②百度指数/股吧另类文本面（合规评审前置，零新采数纪律下走裁定另立）；③券商金工中文研报补核（研究档 §4.2 两轮限流未果）；④daban 深史替代源全景（akshare 涨停池族之外，如通达信/同花顺 iFinD 导出面）——本期只登记不开挖。

## §4 封顶声明（skeleton_mining §6）

1. **封顶**：情绪线环节册=本册＋六件子册，不再增枝。后续增长只允许两种形态：①既有环节内的"叶→数据集/实现"落地（施工班领卡）；②新案例/新考古触发批次重开（须留理由+批次号回写本册 §3）。
2. **新增事件/成分的唯一入口**：L3 事件集若扩容（如 E9+），必须先过 L3 册 §2 封闭集判据（触发条件可机械化+PIT 滞后可申报+有确认器消费方）再入册——禁边挖边建。
3. **L4 不入本骨架**（§1 已声明）；与大盘班的接口三线只在 6_tdm 单册维护，防双真源。
4. 增枝须过 skeleton_mining §3 停止判据三问（生产者变/验证口径变→拆；仅标签参数变→不拆）。

## §5 全册状态汇总（自审闸三态，各子册 §4 详裁）

| 子册 | 三态裁定 | 一句话理由 |
|---|---|---|
| 1_L1_thermometer | **施工**（C1/C2 回补为第一优先） | Q5 已建议第一优先；史浅不补则 L1 长期退化弱版 |
| 2_L2_phase | **施工**（轻量：映射校准+段灰度） | R3 翻案后余量小；收编登记已在册 |
| 3_L3_events | **施工**（E1/E3/E4/E8 先发接线） | 件已在手零新码，缺的只是消费方接线 |
| 4_validation | **挂起排期→随 P2 判据冻结同批** | Q4 建议与大盘班同批，判据看数前冻结 |
| 5_self_sustaining | **施工**（日批已有件，补周批裁判） | 永久系统四要素合规化，终局必需 |
| 6_tdm_wiring | **施工**（挂接清单落 yaml 待批） | 不落节点则契约停在纸面（研究档 §11.2-2） |

**前置项（本车道无权处置，呈总包 P1）**：①补登"温度计≠档位计"真裁定（Q10 依据）；②Q1-Q14 呈批；③daban 深史回补排期（akshare 涨停池族源侧仅存近约 30 交易日，深史需另寻源——💰/⬜ 级缺口，见 1_L1 §1）。
