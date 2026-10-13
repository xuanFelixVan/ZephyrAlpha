---
ttl: task_bound
title: 环节[3] 灰度双轨——后验主轨＋强度辅轨（t 值）；各自 B1/B2 验证
created: '2026-10-13'
session: st-condaxis-20261013
status: mining_workbook
family_id: CONDAXIS-CAMPAIGN
completes_when: 该环节施工完成且随 CONDAXIS-CAMPAIGN 归档
---

# 1. 逐项台账（✅ 均为 2026-10-13 本车道 Read/grep 实查）

| 件名 | 仓内真源路径:行号 | 现状 | 消费方 | 缺口 | 六向定位 |
|---|---|---|---|---|---|
| 灰度五档 band5（情绪轴先例） | src/zephyr/backtest/regime_validation/condition_package.py:45 _BAND_EDGES=(0.2,0.4,0.6,0.8)／:46 五标签／:56-63 grey_band() 实读 | ✅ 实查在产（冻结） | factory_grid_executor T1 分层键；f06_e4_wfa_exam | 两态灰度**不是**情绪五档复用——轴不同（研究册 §10 分层纪律：状态灰度=后验置信、信号灰度=转移概率） | ②下游 |
| 7 维概率=既有灰度语义 | regime_detector.py:8 INVARIANTS"不输出硬标签只输出7维灰度概率"实读 | ✅ 实查在产 | B2/面板 | 两态主轨=jump 后验同构物，口径对齐此语义 | ③ |
| B1 概率校准 | src/zephyr/regime/validation/phase2/b1_probability_calibration.py 文件头实读：ECE<0.10 PASS／0.10-0.15 REVIEW／≥0.15 FAIL；每态预期方向由数据推断非固定映射 | ✅ 实查在产 | phase2_runner | 两态双轨各过 B1（卡面声明用哪轨）——复用零改动 | ③ |
| B2 CRPS | src/zephyr/regime/validation/b2_crps.py 文件头实读：离散 CRPS=Σ(CDF−1{y≤k})² 对照 climatology | ✅ 实查在产 | 人工审查/11 号 memo | 同上复用 | ③ |
| B3 置信分布 | src/zephyr/regime/validation/b3_confidence_distribution.py（validation/ ls 实据） | ✅ 实查在产 | phase2 族 | 灰度分布健康度照跑 | ③ |
| D1 置信网格／confidence_calibrator | src/zephyr/regime/validation/d1_confidence_grid.py；phase2/confidence_calibrator.py（ls 实据） | ✅ 实查在产 | 校准链 | 灰度→判据换算的仓内先例 | ③ |
| jump 后验（主轨量源） | 全仓 grep "jumpmodel" 零命中（2026-10-13，见 [2] 台账） | ⬜ 空白待建（随 [2]） | 本环节主轨 | 后验置信度"我多确定现在是横向"；跳变代价=信号灰度辅源 | ③ |
| trend-scanning \|t\| 值（辅轨量源） | 全仓 grep "trend_scanning" src+scripts 零命中（2026-10-13） | ⬜ 空白待建 | 本环节辅轨 | span 网格 P2 钉死（网格敏感缺陷）；实时面只认已闭合 span（PIT 红线） | ③+④ |
| BOCPD run-length 后验（信号灰度量源） | grep "bocpd" 全仓唯一命中=src/zephyr/position/core/strategy_book.py:158,166——**接口占位非实现**（SentimentStageSignal confidence 字段注释"BOCPD 后验概率"）实读 | ⬜ 空白待建（随 [4]） | 信号灰度"横向快结束了" | robust 观测模型（Student-t）防厚尾失真 | ③ |
| "温度计≠档位计"裁定 | ruling_registry.yaml grep "温度计" 零命中；裁定#400 实读=定桩战役纪要存真（:3082-3084，撞号坐实）——**该裁定在册不存在** | 🌑 不可得（裁定级） | 本环节语义引用 | 两态册如需引用温度计分层语义，须走 P1 补登新裁定，禁凭空引"在册" | ①上游 |
| 灰度口径分离声明 | 研究册 §10（状态灰度/信号灰度分轨）；无仓内落地件 | ⬜ 空白待建 | 卡面/文档 | P2 双轨呈批（§13-3）的文书载体 | ⑤呈现 |

# 2. 与既有资产的边界（不推倒重来清单）

1. **直接复用零改动**：B1/B2/B3/D1 校准验证全族（两态双轨只是新输入面）；grey_band() 的**边界冻结纪律**作为方法论模板（值不抄——轴不同）。
2. **参数换面**：五档边界 (0.2,0.4,0.6,0.8] 是情绪轴冻结值，两态灰度分档（如需分档）另定边界并独立冻结——**禁跨轴复用数值**（同 EXTREME_STATE_ALIASES 的"禁自建别名"精神，market_state.py:27-28 实读）。
3. **新建**：主轨输出件（jump 后验+覆盖规则）、辅轨输出件（|t| 值逐日序列）、双轨卡面口径声明。
4. **语义边界钉死**：情绪灰度（emotion_index 五档，condition_package 情绪腿）／状态灰度（两态后验，本环节）／信号灰度（拐点转移概率，[4]）——三灰度三轴，卡面必须声明用哪轨哪轴。

# 3. 施工要点（代码实读中的坑）

1. **B1 的"方向由数据推断"设计**：b1 文件头明示每态预期方向=平均后续收益 sign 推断（避免无监督标签语义依赖）——两态层复用 B1 时，"单边↑"的预期方向应同理由数据推断而非预设"必涨"，否则同义反复（拿方向标签考方向概率）。
2. **overlay 概率不可混桶校准**：7 维中 r10-r12 是 TRANSITION_CONFIG 规则覆盖值（[1] 台账坑 5）；两态 jump 后验是似然族——B1 分桶前必须区分概率来源，规则覆盖值单列或剔除。
3. **t 值厚尾**：|t| 值分布厚尾（研究册 §4.3），直接线性归一化到 [0,1] 会被极端值拉伸失真——辅轨落档建议 rank 分位化（仓内先例=auto_mount PHASE_PCT_WINDOW 250 日滚动分位，scripts/backtest/auto_mount.py 实读同款手法）。
4. **band 边界左开右闭语义**：grey_band 用 `value <= edge` 逐边判、末档 fallback（:60-63）——两态灰度若分档，边界语义（含端点否）必须在冻结文书里写死，防实现歧义。
5. **越界即抛**：emotion_index 越界 [0,1] 抛 ValueError（:58-59）——两态后验同款 fail-closed（Σ=1 守卫，regime_detector INVARIANTS 先例）。

# 4. 自审闸三态裁定

| 项 | 裁定 | 理由 |
|---|---|---|
| 后验主轨（jump 后验+B1/B2） | **施工** | 条件轴精细分层（"灰度≥θ 才开考"）的连续量基础；验证器零边际复用 |
| t 值辅轨 | **施工** | 文献同构（López de Prado）+meta-labeling 咬合位；一个纯函数件成本 |
| 双轨卡面声明文书 | **施工** | 防三灰度混用（语义事故源）；纯文书成本 |
| conformal 校准附加 | **方案封矿** | 终局关键路径无位（研究册 §5.3：公认缺口但无代表作、非行业标准）；B1/B2 已覆盖终局验证诉求，留案底 |
| 灰度五档分档化（连续→档） | **挂起排期** | 终局有位（条件胞消费需档），但档边界设计依赖主轨分布先立；解锁=B1 首轮跑数后按分布呈批 |
