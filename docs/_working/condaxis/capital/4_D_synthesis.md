---
ttl: task_bound
title: D 合成状态＋拐点信号集——CapitalConsensus 骨架现状/strength 标定方案/拐点族立卡（施工前挖矿作业簿）
created: '2026-10-13'
session: st-condaxis-20261013
status: mining_workbook
family_id: CONDAXIS-CAMPAIGN
completes_when: D 环节施工完成且随 CONDAXIS-CAMPAIGN 归档
---

# D 合成状态＋拐点信号集（4_D_synthesis）

> 契约定位（研究册 §2.2-D）：对齐状态识别的"状态+拐点"——D1 净积累/派发状态（连续值 [-1,+1]＋离散三态＋置信度）；D2 拐点信号集候选（建仓完成族/派发启动族，**判据面零冻结**，仅列方向待 P2 预冻结）。
> 本册管"合成与拐点"；单主体证据归 C（3_C_actor_profile）；四模块谁吞谁归 5_module_consolidation。

## §1 逐项台账

| 件名 | 仓内真源路径:行号 | 现状标记 | 消费方 | 缺口 | 六向定位 |
|---|---|---|---|---|---|
| **D1 合成骨架** CapitalConsensus | `src/zephyr/signal_ashare/capital_behavior_orchestrator.py`（306 行全读）：`CapitalConsensus`(:159-176: symbol/direction/strength[-1,1]/phase/expected_next_phase/profiles/notes)；`analyze`(:216-267) 画像打分→合力聚合→六阶段推演；`_infer_next_phase`(:197-206) | 🔨 testing（头注:7 `[MATURITY] testing`）；**零真实消费方**——import 反查全 src 仅 `signal_ashare/__init__.py:29` 再导出；头注 [CONSUMERS]=候选（C-014 大盘预测后续波次、盘前计划编排） | 无（候选面） | ①观测上游不存在（3_C §3.3——CapitalObservation 无构造方）；②strength 标定（下件）；③纯内存无 DB 直连（头注:8 不变量——持久化通道未定） | ②下游：C-014/盘前编排（候选）；③算法：EMA 偏置自迭代 review(:269-306) 已在（限幅±0.5:75） |
| **D1' strength 标定** | 公式在文件 docstring :34-36：`strength = Σ(sign(net)×\|net\|×conf×(1+bias)) / Σ(\|net\|×conf)`——头注明示"**MVP 初拍值，待标定批替换**"；阈值 `CapitalBehaviorConfig`(:127-139)：long_threshold=0.15/short_threshold=-0.15/calibration_alpha=0.3 | ⬜ 待标定（MVP 初拍在册） | — | **标定方案**（§3.1）＝转正前提（研究册 §7.2）；阈值与 strength 量纲联动标定 | ③算法：分位映射/事件研究标定（见 §3.1）；判据数值=P2 领地 |
| **D2-a 建仓完成族** 信号立卡（候选） | 组合证据全部在册：股东户数连降（A4 表）＋底部单峰密集（A3 待建）＋缩量企稳（volume.py VO/vol_z 族） | ⬜ 零实现（信号族未立卡） | — | 每信号一张卡（研究册 §8.8 多重检验：信号池规模→通过门槛校正规则）；组合逻辑（AND/加权）待冻结 | ②下游：择时/关注池（研究册 §2.4-1）；与隔壁形态班 P1 供料关系 |
| **D2-b 派发启动族** 信号立卡（候选） | 组合证据在册：放量滞涨（B2' effort/result）＋获利盘高位（A1 chips_winner）＋大单转净流出（C1）＋两融偿还加速（C2，07 卡先例） | ⬜ 零实现 | — | 同上；五条出场腿证据组合（§2 边界） | ②下游：减仓预警/风控 |
| **D3 条件轴挂接**（资金行为腿） | `src/zephyr/backtest/regime_validation/condition_package.py`（MOD-BT-COND-PACKAGE，实读头注）：现两轴=情绪灰度五档(0.2/0.4/0.6/0.8)×大盘状态（F4_BDI_MOMENTUM_Z20 三态）；**板块腿 observational-only 且 columns_forbidden=[capital_score, net_inflow_pct]**（头注 INVARIANTS） | 🔨 experimental（在册挂点） | factory_grid_executor（T1 条件维分层键）/f06_e4_wfa_exam | 资金行为腿=第三腿候选——须先 observational（行级标注）后统计（禁直接进判据，对齐板块腿先例） | ②下游：GPU 网格条件轴；③算法：闭卷窗纪律（2019-01-04..2025-09-09 窗外禁入） |
| （相邻）s2_wyckoff_score 维度 | regime 管道 S2 confirm 位 | 🌑 证伪恒零（2_B §1） | OverlaySignalsConstructor（恒 0 不干预） | D1 合成**不得**借位该维度 | 边界件，禁混 |

## §2 与既有资产边界

1. **D1 与 C 的边界**：C 产 CapitalObservation（单类观测），D 合成为 CapitalConsensus；review() 校准偏置属 D（类级 EMA），证据置信度属 C（观测级）——两层置信度禁混用。
2. **D1 与 SIG-021 六阶段的边界**：BehaviorPhase 主链=SIG-021 职责（"不重写六阶段识别算法"——orchestrator 头注:38-39 明令）；D1 只做推演（`_infer_next_phase` 不可跳跃不变量 :8）。5_module_consolidation 的合并方案改变此依赖时须保该不变量。
3. **拐点信号族与隔壁形态班**：形态班管"价在做什么"的拐点（单边启动信号 P1）；资金族信号是**信号池供料方**（研究册 §2.3）——立卡时 node_id 挂资金线，禁挂在形态班节点下。
4. **条件轴纪律**：condition_package 闭卷窗（2019-01-04..2025-09-09）与 30 交易日胞地板是既有真源；资金腿进轴前其自身序列必须先过考试（D3 的解锁条件），且首形态=observational 行级标注（板块腿先例），columns_forbidden 模式照抄。
5. **多重检验预算**：D2 信号族池=研究册 §8.8 预冻结必含项；本册只登记信号名与证据组合，禁给任何门柱数值。

## §3 施工要点（实读代码的坑）

### 3.1 strength 标定方案（结构草案，数值零自拟）

现状：strength 公式 MVP 初拍（docstring :34-36），方向阈值 ±0.15（CapitalBehaviorConfig 默认值）——两者联动失配即"strength 量纲漂移"（换观测源 net 口径=换量纲，阈值即失效，头注:114 明示"口径随上游，仅相对比较"）。

标定方案候选（P2 冻结选一或组合）：
- **甲 分位映射**：strength 历史分布→分位档（如 P20/P80 作阈值），对观测源口径变化天然免疫；坑：分布漂移需滚动窗，窗长待冻结。
- **乙 事件研究锚定**：以"强 strength 事件"后 N 日收益的方向命中率反推最优阈值（对齐 07 卡 events 分桶法）；坑：多重检验账（每次扫阈=一次试次，入 n_trial_ledger）。
- **丙 复盘校准自迭代已建**：review() EMA 偏置（:269-306）是**类间相对**校准，不是 strength→阈值标定——两者正交，勿混（常见误读：以为 review 能替代标定）。
- 前置依赖：观测适配器在产（C 环节）——**没有观测流就没有标定样本**，D1 标定排期在 C 后（P2）。

### 3.2 拐点信号立卡的坑

1. **组合信号=组合多重检验**：AND 组合的每一腿单独过闸+组合再过闸（试次账双计）；预注册时把"腿清单"冻结死，禁事后增删腿（反挪门柱）。
2. **证据 PIT 异频混合**：D2-a 用到季频（户数）+日频（量价）混合证据——信号可用时点=最慢腿（季频 announce_date），卡内 pit_anchor 必须显式声明最慢腿。
3. **建仓完成族的语义坑**："缩量企稳"的企稳=形态班语义——跨班借腿时以形态班输出为输入（输入-输出关系），禁在资金线重写企稳判定（第二实现禁令）。
4. **信号池供料先于拐点判定**：先"供料卡"（信号→前向收益事件研究）后"拐点状态卡"（拐点时点判定）——两级分开立卡防一步到位过度工程。

### 3.3 CapitalConsensus 持久化与消费面（呈批项）

现纯内存（头注:8 不变量）。终局消费面=C-014 大盘预测波次+盘前编排——两候选都未建。建议：持久化通道随首个真实消费者一并定（避免先建表后改 schema）；挂条件轴 observational 腿（D3）是**最小消费面**（行级标注不进判据），作为 D1 的第一条激活路径。

## §4 自审闸三态裁定

| 件 | 裁定 | 理由 |
|---|---|---|
| D3 资金腿挂条件轴 observational | **施工（随 C 适配器后第二批）** | 最小激活路径；板块腿 observational 先例+columns_forbidden 模式现成；不进统计判据零考试风险 |
| D1 strength 标定 | **挂起排期** | 解锁条件=C 观测适配器在产（标定样本依赖）＋P2 判据冻结窗；方案甲/乙结构已备，禁现在拍数值 |
| D2 建仓完成/派发启动族立卡 | **挂起排期（登记池）** | 证据腿三缺一（A3 未建/B2' 未建）；终局有位（拐点=状态识别对偶核心）；解锁=各腿卡过考后组合卡进 P2 |
| wyckoff 借位方案 | **方案封矿** | 同 2_B §4（证伪件终局无位） |
| CapitalConsensus 持久化 | **挂起排期** | 随首个真实消费者定（§3.3），现在建=提前建中间件 |

**反驳者一问**（D3 observational 腿加试）：①条件轴已有两轴+板块腿，第三腿边际价值未证（对策：observational 期零统计成本，纯标注积累——正是"先看数据再定进判据"的纪律本体）；②CapitalConsensus 未标定就挂轴=污染轴（对策：只挂 direction/strength 原值列禁挂派生档位，轴分层键不动）。维持施工。
