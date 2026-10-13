---
ttl: task_bound
title: B 流量性质判定——LM2002 量价动态二分自实现方案＋effort/result 现状挖（施工前挖矿作业簿）
created: '2026-10-13'
session: st-condaxis-20261013
status: mining_workbook
family_id: CONDAXIS-CAMPAIGN
completes_when: B 环节施工完成且随 CONDAXIS-CAMPAIGN 归档
---

# B 流量性质判定（2_B_flow_nature）

> 契约定位（研究册 §2.2-B）：增量诊断，日频——"今天的量是什么性质"。B1=量价动态二分（Llorente-Michaely-Saar-Wang 2002 RFS 15(4):1005-1047）：放量+收益正自相关=知情推动（趋势燃料）vs 放量+收益反转=流动性出货——同一根放量 K 线两种相反含义，此判据是最小可行版。B2=effort/result 偏离（Wyckoff 口径：量努力 vs 价结果）。
> **本册最重要更正**：研究册 §7.2 称 wyckoff_engine"在册"——实读发现其为 **WYF-3 证伪态**（详见 §1 台账），B2 施工基座须换。

## §1 逐项台账

| 件名 | 仓内真源路径:行号 | 现状标记 | 消费方 | 缺口 | 六向定位 |
|---|---|---|---|---|---|
| **B1 LM2002 量价动态二分** | 负存在断言：全 src grep `llorente\|LM2002\|dynamic.volume.return\|量价动态` 零命中（本车道 2026-10-13 复认，与总包核验一致） | ⬜ 零实现 | 无 | 自实现方案（§3.1）：数据面核验+滚动窗规格+A 股适配 | ③算法：LMSW 回归 c2 符号判知情/流动性；①上游：kline_daily；⑥字段：close/volume/amount 已备 |
| **B1' 量族指标基座**（17 指标） | `src/zephyr/factor/technical_indicators/volume.py:52-561`——OBV/MFI/VWAP/VR/AD/PVT/WVAD/VWMA/ADOSC/EOM/KVO/NVI/PVI/FORCE_INDEX/WAD/VO/MARKETFI 恰 17 类（grep 类清单逐一核对） | ✅实查在产：头注 `[MATURITY] production`（volume.py:7）；落 c1_market.technical_indicator 宽表列（obv/mfi_14/vwap/vr_26/ad/pvt/wvad_24/vwma_20/adosc/eom_14/kvo/nvi/pvi/fi_13/wad/vo/marketfi，CH DESCRIBE 实查在列） | internal_compute_provider autodiscover（volume.py:5）＋sleeve alpha 择时（头注声明） | 无性质判定语义——全部是量水平/累积量指标，无一回答"放量是知情还是流动性"（研究册 §8.5"量必须配价"陷阱的仓内实证） | ②下游：B1 立卡时作对照基线（"只用价量"基线=增量账对照物） |
| **B2 effort/result**（Wyckoff 口径） | `src/zephyr/regime/features/wyckoff_engine.py`（476 行全读）：detect_wyckoff_events:297-396（PS/SC/AR/ST/Spring/Test 六事件 FSM）＋wyckoff_score:439 | 🌑 **证伪态（WYF-3 裁定 2026-09-16，裁定#285）**：头注 INVARIANTS 明示 `_DIMENSION_STATUS=falsified ⇒ wyckoff_score 显式恒 0+一次性告警(禁静默恒零)`；实证=000300 5272 交易日 PS/SC=280/4、AR/ST/Spring/Test 全零触发，链从未闭合，门槛 60 结构性不可达；walk-forward 重校零样本外信息量 | MOD-REGIME-002 OverlaySignalsConstructor 消费 s2_wyckoff_score→S2 confirm（声明面，现恒 0 即不干预） | effort/result 作为**独立小构造**（量努力 z vs 价结果 z 的偏离）并不存在于该引擎——引擎做的是事件 FSM，不是 effort/result 连续指标；需另立件 | ③算法：effort/result=normalize(V) vs normalize(\|ΔP\|) 偏离（连续值）；④后端：sc_volume_leg（wyckoff_engine.py:265-294）=幸存的量能腿构件（vol_ratio/vol_epct/vol_qratio 三口径，PIT 安全）可复用作"努力"腿 |
| **B2' 相邻件：量能体制** | `src/zephyr/signal_ashare/volume_regime_adaptive.py`（MOD-SIG-129，头注实读） | ✅ production | 运行时装配批（量能×体制 3×3 策略矩阵）＋MOD-SIG-130 三维矩阵轴复用 | 量能三态（缩/平/放 vol/MA20）≠流量性质（知情/流动性）——正交件，B1 立卡禁与之混卡（骨架 SOP §3 验证口径变→拆） | ①上游同 kline_daily；②下游 strategy_matrix_3d |
| **B2'' 竞价微观结构** | `src/zephyr/signal_ashare/auction_microstructure_analyzer.py`（MOD-SIG-089，testing，竞价五族特征+抢筹/诱多/压价） | 🔨 testing | 候选：盘前计划 D_PLAN、打板监控 | 数据上游=tick_depth_5 竞价派生——**该链 2026-09-30 起断供**（6_data_audit §tick），B 线日内腿当前 blocked_on_data | ①上游：tick_depth_5（断供中）；⑥字段：竞价窗口逐拍五档 |

## §2 与既有资产边界

1. **wyckoff_score 禁止作为 B2 基座**：证伪件恒零（头注明令禁静默、阈值真源保持原值不动=可复算能力非生产推荐值）。B2 若做，是**新构造**（effort/result 偏离连续指标），与 wyckoff_score（事件累加评分）不同物——立卡时须声明"非 wyckoff 复活"。
2. **volume.py 17 指标=对照基线不是性质判定**：研究册 §8.5"任何单独的量指标不单独上岗，配 LM2002/effort-result 性质判定"——B1 卡的增量账对照物=17 指标族（SOP §8.5.2 对在册因子族残差化）。
3. **sc_volume_leg 复用纪律**：其头注明令"vol_z 腿由调用方传入序列承载（生产口径单一真源=RegimeFeatureBuilder F5），禁引擎内重算"——B2' 若借 sc_volume_leg，须走固定基准口径（vol_ratio 等）或从 F5 取 vol_z，禁第三处重算。
4. **与 MOD-SIG-129 量能三态正交**：三态管"量多量少"（水平），B1 管"量的性质"（信息含量），B2 管"量价匹配度"（偏离）——三卡分立。
5. **竞价腿（B2''）blocked_on_data**：tick_depth_5 断供未复（6_data_audit），禁日频近似冒充竞价面（SOP §8.5.3 模板 C 同款纪律）。

## §3 施工要点（实读代码的坑）

### 3.1 B1 LM2002 自实现方案（挖矿交付：数据面够不够＋规格草案——判据数值零自拟）

**数据面结论：kline_daily 够。** CH 实查 c1_market.kline_daily：1990-12-19..2026-10-13、11,691,370 行——LMSW 需要的个股日频 close/volume/amount 全史可用；volume 量纲已治本统一为"股"（chips.py:44-45 头注引 2026-09-22 量纲治本 memo，amount/close/volume 中位≈100 的"手"伪 VWAP 坑已修）。

**规格草案（预注册材料，全部待 P2 冻结）**：
1. 回归式（LMSW 原式日频化）：r_{i,t+1} = β0 + β1·r_{i,t} + β2·(r_{i,t} · V*_{i,t}) + ε，V*=量能变换（候选：换手率/成交量 z/成交额 z——三选一待冻结）；**β2 符号=判定面**：正=知情推动（量放大收益延续），负=流动性出货（量放大收益反转）。
2. 滚动窗规格：原文献用周频+半年窗；A 股日频适配候选窗=60/120/250 日（待冻结），min_history 与预热期入卡声明；输出=β2 估计值±t 值，判定=β2 的 z 或符号稳健度（待冻结）。
3. **A 股适配闸（三条，逐条过闸）**：①涨跌停日剔除（一字板日 r_t 与量被截断，自相关失真——研究册 §5 口径分裂警示同源）；②停牌/复牌跳变（kline 有 NaN 缺口，volume.py 族均按"停牌不衰减"处理，B1 同律）；③散户主导市场知情/流动性占比与美股不同——判定阈值禁照搬文献，P2 用仓内数据冻结。
4. 实现位：`factor/technical_indicators/` 新类（对齐 volume.py 注册表模式，category 新立"flow_nature"或挂 volume）——**先立卡后写码**（施工闭环 Step 1.9）。
5. e/r 位纪律：信号位=β2 面板/聚合序列；收益位=标的次日收益或指数次日收益（禁借外部指数冒充）。

### 3.2 B2 effort/result 独立小指标草案

- 构造：effort=z(volume or 成交额, 滚窗)、result=z(|pct_change|, 滚窗)，偏离=effort−result（放量滞涨=高 effort 低 result=出货嫌疑面；缩量急涨=反向）。与 B1 互补：B1 判性质（知情/流动性），B2 判匹配度（量价背离）。
- 坑：z 的滚窗与基准（固定基准 vs 滚动基准）直接决定可比性——wyckoff_engine.py:257-262 的 `_SC_VOL_MODE_TO_THRESHOLD` 口径表是现成的"基准量纲分派"设计范式，照此登记口径真源，禁散落字面值。
- 该指标与 17 指标族中 WVAD/VO/ADOSC 同域相邻——增量账须对这三者残差化后报增量。

### 3.3 wyckoff_engine 现状的处置建议（呈批件）

引擎保持 falsified 态不动（阈值真源不删=可复算能力，裁定#285 语义）；B2 新件**不 import 该引擎的 score**；sc_volume_leg 可 import 复用（构件非判定）。若 P1 呈批通过"B 线施工"，wyckoff_engine 文件头的 [CONSUMERS] 行应在施工批同步改为"已证伪恒零，消费面冻结"防误用（改头注属常规施工，非本作业簿职权）。

## §4 自审闸三态裁定

| 件 | 裁定 | 理由 |
|---|---|---|
| B1 LM2002 自实现（先立卡） | **施工** | 终局有位（量性质判定是 B 件核心、A/C/D 都消费它的输出）；数据零新闸（kline_daily 全史）；实现面小（一个指标类+一张卡）；研究册 §8.5 明令"量必须配价"——它是 17 个在产量指标的安全阀 |
| B2 effort/result 独立指标 | **施工（随 B1 同批立卡）** | 构造极小（两个 z 的差）；与 B1 同数据零增量成本；对 WVAD/VO/ADOSC 的增量账在卡内预注册 |
| B2-wyckoff（一切基于 wyckoff_score 的变体） | **方案封矿** | 终局不需要：WYF-3 walk-forward 实证零样本外信息量（5272 日链未闭合），终局全貌的资金行为层由 B1/B2/A/C/D 承担，证伪件不再喂第二春；封矿≠删件（可复算能力保留，裁定#285 原语义） |
| B2'' 竞价微观结构腿 | **挂起排期** | blocked_on_data（tick_depth_5 断供）；解锁条件=桥流恢复或模拟盘 T+1 回补通道落地（6_data_audit §tick）后重估 |

**反驳者一问**（B1 加试）：①β2 在散户主导市场可能普遍弱/不稳定（对策：卡内按板块/市值分层预注册+如实披露失败面）；②日频化偏离原文献周频口径，结论外推性存疑（对策：卡内声明口径差异，判据全按仓内数据冻结）；③与动量因子相关性（对策：对动量/反转族残差化增量账）。维持施工。
