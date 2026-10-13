---
ttl: task_bound
title: 环节[7] 验证与打靶——B1/B2 复用、锚点年表标定集、预注册协议、A股重标定缺口
created: '2026-10-13'
session: st-condaxis-20261013
status: mining_workbook
family_id: CONDAXIS-CAMPAIGN
completes_when: 该环节施工完成且随 CONDAXIS-CAMPAIGN 归档
---

# 1. 逐项台账（✅ 均为 2026-10-13 本车道 Read/grep/ls 实查）

| 件名 | 仓内真源路径:行号 | 现状 | 消费方 | 缺口 | 六向定位 |
|---|---|---|---|---|---|
| B1 概率校准 | src/zephyr/regime/validation/phase2/b1_probability_calibration.py 文件头实读（ECE<0.10 PASS/0.10≤ECE<0.15 REVIEW/≥0.15 FAIL，2026-08-08 修订门槛） | ✅ 实查在产 | phase2_runner | 两态双轨各跑（[3] 台账坑 2：overlay 覆盖值禁混桶） | ③ |
| B2 CRPS | src/zephyr/regime/validation/b2_crps.py 文件头实读（离散 CRPS 对照 climatology；"climatology CRPS=0(单一类别样本)→无法评估,抛错"） | ✅ 实查在产 | 人工审查/11 号 memo | 两态层若某段样本近单一类别会触发抛错分支——预跑分布体检 | ③ |
| A1 样本充分性／A2 HMM 过拟合 | src/zephyr/regime/validation/phase2/a1_sample_sufficiency.py、a2_hmm_overfitting.py（ls+FEATURE_NAMES grep 实据） | ✅ 实查在产 | phase2_runner | 两态段级样本量（段数少）是 A1 的重考面 | ③ |
| A3 转移覆盖／A4 特征重要性 | src/zephyr/regime/validation/a3_transition_coverage.py、a4_feature_importance.py（ls 实据） | ✅ 实查在产 | phase2 族 | A3=拓扑约束的验证器（转移矩阵覆盖率 vs 拓扑白名单） | ③ |
| B3 置信分布／B4 转移准确性 | b3_confidence_distribution.py（ls）；phase2/b4_transition_accuracy.py+historical_events.yaml（:1-50 头部实读：8 事件/±5 交易日/≥6 命中 PASS） | ✅ 实查在产 | phase2 族 | B4=两态拐点打靶靶场（[4] 台账） | ③+⑥ |
| D1 置信网格／D3 聚合扰动 | d1_confidence_grid.py、d3_aggregation_perturbation.py（ls 实据） | ✅ 实查在产 | phase2 族 | 灰度→判据换算与稳健性 | ③ |
| E1 walk-forward 稳定性 | e1_walkforward_cv.py 文件头实读（train_years=5/refit QE/46 季度边界，CV<0.5 门槛） | ✅ 实查在产 | 11 号 memo E1 | 两态层沿同 46 季度边界跑，跨层可比 | ③ |
| 预注册协议先例（recal） | docs/_working/archive/2026-09/regime_recal/regime_recal_protocol_2026_09_17.md 实读（§1 诊断目标→§6 落库边界六节全结构；"跑数前写死"纪律；#304 记载协议先于跑数 commit 26ac558b） | ✅ 实查在册（已归档） | #304 重校批 | 两态重标定协议照此六节结构起草，跑数前 commit 冻结 | ③ |
| D 族资格冻结稿（接管对象） | docs/_working/2026-10-12-d-family-qualification-freeze-draft.md 实读：:49（unrouted 762 日=41.9% 出处）、:55（§3.1）、:57（§3.3 两源分歧 21.09%） | ✅ 实查在册（draft_for_ruling） | D 族呈批 | 两态线接管声明（§13-8）：全标的覆盖+唯一宏观轴，治 3.1/3.3 | ①上游 |
| 闭卷切点与 PIT 尾窗 | closed_book_gate.py:31 实读（cutoff 派生自 finalized_at=2026-09-09+holdout_months=12，不落第二常数）；auto_mount.py:83 PIT_TAIL_LAG=1 实读 | ✅ 实查在产 | 全验证窗 | 两态验证窗同守；三源滞后（P-S 右端/BOCPD 在线/span 闭合）各自钉死披露 | ③+⑥ |
| 多重检验校正先例 | auto_mount.py 实读：FDR_Q=0.10（BHY 族级 FDR）、FDR_LARGE_FAMILY=100、T_STAR_HLZ=2.8（Harvey-Liu-Zhu） | ✅ 实查在产 | 判定窗 | 研究册 §13-6 呈批：信号池入场 SPA/DSR（建议默认）vs 简易 BH——BHY/HLZ 是仓内现行简易系，升级与否 Owner 裁 | ③ |
| A 股牛熊锚点年表标定集 | 研究册 §8.1（998.23 2005-06-06→6124.04 2007-10-16；1849.65 2013-06-25→5178.19 2015-06-12；2440.91 2019-01-04→3731.69 2021-02-18；来源人民网/上海统计局） | ⬜ 空白待建（P3 标定集） | [2] P-S 重标定；[4] 打靶 | CH 数据 2010 起（historical_events 头注），2005-2007 段仅文献锚；锚点年表须落 yaml（同 historical_events 格式）+每锚留来源引文 | ⑥数据字段 |
| P-S 参数 A 股日频重标定 | 研究册 §3.4（未查到日频/中国市场正式重校文献——缺口即我们的活） | ⬜ 空白待建（P2 预冻结） | [2] 规则层 | 重标定协议=recal 六节结构+锚点年表对照+留证 | ③ |
| 信号池预注册假设卡 | 研究册 §11 问题 5（引 recal 协议先例） | ⬜ 空白待建 | 拐点信号入场 | 池规模 SPA/DSR 校正后才许进 P3（§13-6） | ③ |

# 2. 与既有资产的边界（不推倒重来清单）

1. **直接复用零改动**：B1/B2/A1-A4/B3/B4/D1/D3/E1 十一件验证器全族+historical_events 靶场+closed_book/PIT 机制+BHY/HLZ 校正现行件。**行业标准做法已在仓**（研究册 §2.8：B1/Brier、B2/CRPS 即行业标准），两态线只换输入面。
2. **模板复用**：recal 协议六节结构（诊断目标/数据口径/统计清单禁选择性报告/决策树/验收标准跑数前冻结/落库边界）——两态重标定协议照抄骨架换内容。
3. **新建**：A 股锚点年表 yaml（historical_events 姊妹件）、两态重标定协议、信号池预注册卡模板。
4. **接管而非并存**：D 族 3.1/3.3 的 unrouted/两源分歧由两态线接管（§13-8）——接管后 D 族冻结稿同批改挂，禁两套宏观轴并存打靶。

# 3. 施工要点（代码实读中的坑）

1. **B2 单一类别抛错**：climatology CRPS=0 时抛错（文件头 INVARIANTS 实读）——两态层强趋势段子样本可能近单一态；预跑分布体检，禁为过 B2 剔样本（选择性报告=recal §3 禁令）。
2. **跑数前冻结的 commit 纪律**：#304 先例=协议 commit（26ac558b）先于跑数（ruling_registry #304 summary 实读"WYF-3 先例纪律"）——两态重标定协议必须先 commit 后跑数，事后补写=无效预注册。
3. **统计清单禁选择性报告**：recal §3"全部产出，禁选择性报告"（标题实读）——两态验证的 B1-B4/E1 全量出数，FAIL 项如实入台账（Owner 永久原则：闭卷考试=最终考试，折减抬线不替代考试，mining_sop 总则实读）。
4. **锚点年表的三段两段问题**：2010 数据起点截掉 2005-2007 段——P-S 重标定的"完整周期"统计只有 2013 段、2019 段两轮大样本+若干中级行情；样本量先天不足须在协议里写明（相位门槛的置信区间宽=如实呈现，禁拔高）。
5. **多重校正的族定义**：auto_mount 的 FDR 族=全部 (sid×相位) 检验（:88-89 实读）——两态信号池的"族"=全池 (信号×转移方向) 检验，族定义跑数前写死，禁事后缩池减族凑显著。
6. **B4 命中窗与 ARL 预算的关系**：±5 交易日是 B4 现行窗（historical_events 头注）；两态拐点的验收窗应=ARL 预算标定的确认延迟（[4] 台账坑 3）——两窗数值独立各自留证，禁互相挪用。

# 4. 自审闸三态裁定

| 项 | 裁定 | 理由 |
|---|---|---|
| 验证器复用接线（B1-B4/E1 换面跑） | **施工** | 零边际复用；不接线则两态产物无验收=不可入条件轴 |
| A 股锚点年表 yaml | **施工** | P-S 重标定与拐点打靶的对照集基础；一个 yaml+来源引文成本 |
| 两态重标定协议（recal 六节） | **施工** | 考试资格前提（判据数值零自拟的实现载体）；文书成本 |
| D 族接管改挂 | **施工**（P1 呈批件） | 净零内收（两套并存=重复簇违规）；接管声明随 §13-8 |
| SPA/DSR 校正升级 | **挂起排期** | 终局有位（池规模扩大后简易系不够），但信号池未建无池可校；解锁=首批拐点信号预注册卡 ≥10 张 |
| 锚点年表权威化（单一权威定义追溯） | **方案封矿** | 研究册 §8.1 已证"无单一权威定义"；终局以自标定集+来源引文为真源，外部权威化无终点，留案底 |
