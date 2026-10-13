---
ttl: task_bound
title: 大盘两态形态识别线——环节骨架总册（施工前挖矿作业簿）
created: '2026-10-13'
session: st-condaxis-20261013
status: mining_workbook
family_id: CONDAXIS-CAMPAIGN
completes_when: 该环节施工完成且随 CONDAXIS-CAMPAIGN 归档
---

# 0. 本册定位与方法

- **定位**：条件轴总包战役（st-condaxis-20261013）两态域挖矿车道产出。Owner 三问（识别大盘/板块/宽基状态、反转信号在哪、信号与状态最重要）经研究册 [formreg_survey_2026_10_13.md](../00_inputs/formreg_survey_2026_10_13.md) 全网勘查后，本册把"大盘两态形态识别线"拆成**环节骨架**——每环节一件子作业簿（mining_workbook），供 P2 施工令直接领条目动工。
- **方法**：[mining_sop_policy.md](../../../01_policies_and_standards/sop/mining_sop/mining_sop_policy.md) §2 六向寻路＋§5 防噪音四闸＋§6 挖后自审闸；[skeleton_mining_policy.md](../../../01_policies_and_standards/sop/mining_sop/skeleton_mining_policy.md) §5 状态标记纪律（✅ 须附实查 file:line，本轮全部为 2026-10-13 本车道 Read/grep 实据，非研究册转述）＋§6 封矿判据（三扫收敛+封顶声明）。
- **判据纪律**：本册是挖矿作业簿，**零裁定、零开考、零数值自拟**——一切参数性默认均待研究册 §13 九项经 P2 呈批 Owner 裁决后才冻结。
- **先决门**：裁定 #229/#230/#304 在册现行口径＝"态层=风险分档、方向判别归因子层"（ruling_registry.yaml:1059-1100 实读；#304 见 :1897-1901）。两态线新增"形态向"职责须先立反转/扩界裁定（研究册 §13 裁决项 1）——**裁定未落地前，本骨架任何环节不得开工**。

# 1. 环节分解图（文字版）

```
                    ┌────────────────────────────────────────────────┐
                    │  [5] 词表登记（横切层：枚举+映射+登记路径）        │
                    │  两态词表 {单边↑/单边↓/横向/数据不可信}×灰度语义    │
                    └───────▲──────────────────────────▲─────────────┘
                            │ 供给枚举                   │ 供给字面量
  000300/标的 K 线 ──▶ [1] 特征桥 ──▶ [2] 状态机 ──▶ [3] 灰度双轨 ──▶ [6] condition_package 大盘腿
  （c1_market.kline_index）  │  regime 46py 复用   │  P-S规则层+jump概率层   │  后验主轨+t值辅轨      │  情绪灰度×大盘状态
                             │                     │  拓扑约束（横向邻接）    │  B1/B2 各自验证        │  升级点：状态轴换两态输出
                             ▼                     ▼                        ▼                       ▼
                    （FEATURE_NAMES/walk-forward） （7维概率输入之一）     （连续量∈[0,1]）          [7] 验证与打靶
                                                                                                    │  B1/B2 复用+锚点年表标定集
                                                    [4] 拐点信号 ◀────────────┘  预注册协议+A股重标定缺口
                                                    CUSUM/BOCPD；ARL 虚报率预算
                                                    PIT 滞后钉死（三元组：位置/方向/严重度）
```

数据流主线：**[1]→[2]→[3]→[6]**（状态的 nowcast 切片供给条件轴）；**[1]→[4]→[7]**（事件流供给信号卡与触发器）；**[5]** 横切约束 [2][3] 的输出字面量；**[7]** 对全线验收。

# 2. 每环节一段（职责/依赖/产出/P2 呈批项）

## [1] 特征层复用（1_feat_bridge.md）

- **职责**：把 regime 包（实数 46 py，`find src/zephyr/regime -name "*.py" | wc -l`＝46 实测）的 6 特征族（FEATURE_NAMES）、walk-forward 季度重拟合、7 维概率输出（4 HMM+3 overlay，regime_detector.py:8 INVARIANTS 实读）桥接为两态线输入；钉主目标指数。
- **依赖**：c1_market.kline_index（000300 实测在用，anchored_state_machine.py:165-171 实读）、广度源 399106（regime_feature_builder.py BREADTH_INDEX 实读，断更史在册）。
- **产出**：两态线输入面板（特征帧+7 维概率帧），PIT 口径继承。
- **P2 呈批项**：研究册 §13-2（主目标指数＝建议默认沪深300）。

## [2] 状态机骨架（2_state_machine.md）

- **职责**：双引擎——P-S 规则层（牛熊年代学，离线定"历史真值段"）＋jumpmodels 概率层（持久态+后验）；拓扑约束（横向邻接双单边）。规则层施工模板＝anchored_state_machine.py（纯函数核+结构常数+PIT+CH 落库，全文实读）。
- **依赖**：[1] 特征桥；裁定 #229 反转裁定（先决门）。
- **产出**：两态逐日状态+段边界（年代学），重排锚定概率（jump 层）。
- **P2 呈批项**：§13-1（#229 反转）、§13-4（拓扑）、§13-9（多周期仲裁：周态作日态方向先验）。

## [3] 灰度双轨（3_grayscale.md）

- **职责**：状态灰度=模型后验（主轨），强度灰度=回归 t 值（辅轨）；各自过 B1 校准/B2 CRPS；与 condition_package 灰度五档的语义边界（"温度计≠档位计"裁定在册不存在，ruling_registry grep "温度计" 零命中+#400＝定桩战役撞号，引用须走 P1 补登）。
- **依赖**：[2] 状态机输出；B1/B2（b1_probability_calibration.py/b2_crps.py 实读）。
- **产出**：双轨逐日灰度值+卡面口径声明。
- **P2 呈批项**：§13-3（灰度主口径＝双轨制建议默认）。

## [4] 拐点信号（4_turning_signal.md）

- **职责**：CUSUM/BOCPD 在线检测；ARL 虚报率预算先行（延迟是预算的结果）；输出拐点三元组（位置/方向/严重度）；PIT 滞后天数钉死+卡面披露。仓内 CUSUM 已有单边实现（correlation_drift_monitor.py:152 实读）可扩展，BOCPD 零实现（grep 实据）。
- **依赖**：[1] 特征桥；PIT_TAIL_LAG 机制（auto_mount.py:83 实读）；closed_book 纪律（closed_book_gate.py:31 实读）。
- **产出**：在线拐点信号流（含 p(r_t=0) 类转移概率）＋离线复核标注（ruptures）。
- **P2 呈批项**：§13-5（ARL 预算数值待 P2 反推呈批）。

## [5] 词表登记（5_vocab_registry.md）

- **职责**：两态词表 {单边↑/单边↓/横向/数据不可信}＋灰度语义登记 state_vocabulary_registry（REG-STATE-VOCAB-001）；预给与 7 态/锚定四档/情绪六段/盘中五态的映射表，避免"第 30 套词表"。
- **依赖**：market_state.py（SH-VOCAB-001，:50/:66/:81/:107 四词表实读）；执法门 STATE-VOCAB-REGISTRY。
- **产出**：词表枚举+映射表+登记条目草案（P2 落册）。
- **P2 呈批项**：§13-7（"数据不可信"态确认入枚举——大盘线本枚举留位，个股线消费）。

## [6] condition_package 大盘腿接线（6_condition_package.md）

- **职责**：现有 condition_package.py（MOD-BT-COND-PACKAGE，Owner 2026-09-23 夜裁①分层口径，:17 实读）的大盘状态腿从 F4_BDI_MOMENTUM_Z20 三态升级为两态输出，**不另立平行条件轴**；接口/不变量全继承。
- **依赖**：[2][3] 输出；c1_market 两表（market_emotion_index/market_alt_regime_signal，:52-53 实读）。
- **产出**：升级后的条件包（或并行新族 signal_id，P2 定）。
- **P2 呈批项**：§13-8（D 族接管声明同批改挂）。

## [7] 验证与打靶（7_validation.md）

- **职责**：B1/B2/E1/A1-A4/B3/B4/D1/D3 验证框架全复用；锚点年表标定集（historical_events.yaml 8 事件库+研究册 §8.1 三轮牛熊锚点）扩充两态段边界；预注册协议（recal 协议先例）；A 股重标定缺口（P-S 参数日频重校）留证方案。
- **依赖**：全线产物；D 族冻结稿（41.9%/21.09% 出处 :49/:57 实读）。
- **产出**：两态线验证协议草案+标定集清单。
- **P2 呈批项**：§13-6（信号池校正规则 SPA/DSR）。

# 3. 封顶声明（skeleton_mining_policy §6）

1. **环节封顶**：两态线环节=上述 7 件，对应研究册 §3-§11 的问题面全覆盖（状态建立 §3/§5→[2]；灰度 §5/§11→[3]；拐点 §4→[4]；跨标的 §9→[1] 桥参数组＋[5] 枚举；分层 §10→[5][6]；验证→[7]）。**此后增长＝环节内子件实现，不再增环节**；增环节须过 skeleton §3 停止判据（生产者变/验证口径变→拆；仅参数变→不拆）并留理由。
2. **三扫收敛假说**：①按生产者扫（regime 包 46 py+backtest 验证族+shared vocab 三族逐件过）✅本轮完成；②按外部方法扫（研究册四车道：学术/机构/开源/A 股）✅研究册完成；③按消费者扫（condition_package/t0 链/pf_alloc/board 面板四消费面）✅本轮完成。三扫后无未挖长尾——**板块线/个股线是姊妹车道**（sector_problem_definition_2026_10_13.md 在册），不在本线增枝，只在 [5] 映射表留接口。
3. **增枝候选清单（评估后不增枝）**：a) ETF/港美标的面——研究册 §9 已裁"原则同、各自标定"，属参数组非新环节；b) conformal 校准——研究册 §5.3 判"未查到代表作，研究性附加不进关键路径"，挂起不入骨架；c) LLM regime council——同判"早期未成体系"，不建；d) sticky HDP-HMM——工程结论"不引 MCMC"，由 jumpmodels 跳变惩罚近似，不建。四条均留档防重挖。
4. **🌑 清点**：本线无 🌑 不可得项（全部为仓内复用+开源可得+自建）；不可得面在研究册（SG Trend 专有规则等）已点名，不重复。

# 4. 挖矿日志（mining_sop §7 产出物纪律）

| 轮 | 矿脉 | 判定 | 关键产出 |
|---|---|---|---|
| R1 | regime 包清产核资（46 py 逐件 ls+关键件全文实读） | signal | FEATURE_NAMES:102、7 维概率 INVARIANTS:8、锚定重排 :118/:151/:596、TRANSITION_CONFIG :304+、anchored_state_machine 施工模板全文 |
| R2 | 验证族清产（validation/ 10 件+phase2/ 7 件） | signal | B1 ECE 三档门槛、B2 climatology 对照、E1 46 季度、B4+historical_events.yaml 8 事件库 |
| R3 | 条件轴与消费面（condition_package 全文+t0 链+pf_alloc 消费者 grep） | signal | 选族铁规 :51、五档边界 :45、闭卷窗 :47-48、regime_state_anchored 五消费者 |
| R4 | 词表与登记面（market_state.py+state_vocabulary_registry.yaml 头部+执法门） | signal | 四词表行号、vocabularies 29 条主区块、proposed 待校准先例 |
| R5 | 负存在复认（jumpmodels/trend_scanning/P-S 规则/BOCPD/温度计裁定，全仓 grep） | 查无（有效结论） | jump/trend_scanning 在 src 零命中；BOCPD 仅 strategy_book.py:158 接口占位；P-S 规则层零命中；"温度计"裁定零命中（#400 撞号坐实） |
| R6 | CUSUM 既有矿（grep cusum 全仓） | signal | correlation_drift_monitor.py:152 单边 CUSUM+PSI；drift_observatory L2→L4 联动先例 |

# 5. 自审闸三态汇总（细节在各子册 §4）

| 环节 | 三态裁定 | 一句话理由（终局全貌量尺） |
|---|---|---|
| [1] 特征桥 | 施工 | 消灭"两态线人工拼特征"环节；regime 46py 复用边际成本极低 |
| [2] 状态机（规则层） | 施工 | 状态 nowcast=考试条件轴缺口（41.9% unrouted 治本）；anchored_state_machine 模板现成 |
| [2] 状态机（jump 概率层） | 施工 | 治 HMM 过频切换③病，输出后验直接喂 [3] 主轨 |
| [3] 灰度双轨 | 施工 | 灰度=条件轴精细分层的连续量基础，B1/B2 现成 |
| [4] 拐点信号（CUSUM 双边扩展） | 施工 | 仓内单边实现扩展成本低；Owner"反转信号"直问 |
| [4] 拐点信号（BOCPD） | 施工（P2 后排期内） | p(r_t=0) 天然灰度信号，但引 robust 观测模型成本实算后定先后 |
| [4] 离线复核（ruptures 集成） | 挂起排期 | 终局有位（P3 离线标注），但依赖 [2] 规则层先立真值段；解锁条件=两态段边界冻结 |
| [5] 词表登记 | 施工 | STATE-VOCAB-REGISTRY 门强制（不登记=提交面记违规）；映射表防第 30 套词表 |
| [5] 个股可标注性过滤器 | 挂起排期 | 个股线姊妹车道职责；本线只在词表留"数据不可信"枚举位 |
| [6] condition_package 接线 | 施工 | 不另立平行轴＝净零纪律；接口不变量现成 |
| [7] 验证与打靶 | 施工 | B1/B2 复用零边际；A 股重标定留证是考试资格前提 |
| [7] conformal 校准 | 方案封矿 | 终局全貌里无关键位（研究册 §5.3 缺口判定+非行业标准），留案底不预建 |

# 6. 骨架 10 问自查（skeleton_mining_policy §9）

①职责一句话：大盘两态（单边↑/↓/横向×灰度）nowcast+拐点 event——说得清 ✅；②环节 MECE：状态/信号/灰度/词表/接线/验证六面+特征桥，无交叉（[2] 出态、[4] 出事件、[3] 出连续量）✅；③环节=完整性检查单元非功能清单 ✅；④叶层停在"实现件代表"（每子册 §1 台账即叶）✅；⑤三重扫描各跑一轮（§3）✅；⑥案例批=historical_events 8 事件+D 族 21.09% 分歧案 ✅；⑦考古批=R5 负存在复认+recal 协议归档考古 ✅；⑧✅ 全附实查 file:line ✅；⑨三扫收敛+封顶声明落盘（§3）✅；⑩路由（各子册台账）/计分板（§5 汇总）/防腐（封顶+增枝留档）三职责挂接 ✅。
