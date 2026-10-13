---
ttl: task_bound
title: 环节[2] 状态机骨架——P-S 规则层＋jumpmodels 概率层双引擎；拓扑约束
created: '2026-10-13'
session: st-condaxis-20261013
status: mining_workbook
family_id: CONDAXIS-CAMPAIGN
completes_when: 该环节施工完成且随 CONDAXIS-CAMPAIGN 归档
---

# 1. 逐项台账（✅ 均为 2026-10-13 本车道 Read/grep 实查）

| 件名 | 仓内真源路径:行号 | 现状 | 消费方 | 缺口 | 六向定位 |
|---|---|---|---|---|---|
| 裁定 #229（态层=风险分档） | docs/01_policies_and_standards/_registry/catalogs/ruling_registry.yaml:1059-1078 实读（"态层降级为风险分档与 L1 谨慎度轴合流"原文） | ✅ 实查在册（active） | anchored_state_machine 语义基座 | 两态线新增"形态向"职责须反转/扩界裁定——**先决门**（研究册 §13-1） | ②下游 |
| 裁定 #230（方向判别归因子层） | ruling_registry.yaml:1079-1100 实读（"方向预测属因子层职责"原文） | ✅ 实查在册 | P0-002 结案 | 同上：单边↑/↓是形态向不是收益方向预测，边界措辞 P2 呈批 | ② |
| 裁定 #304（锚定重排+方向语义退役） | ruling_registry.yaml:1897-1901 实读（"态层职责=风险分档…方向判别归因子层；R1 锚定采纳"） | ✅ 实查在册 | regime_detector 锚定实现 | 两态规则层继承"锚定=结构性消除 label switching"方法论 | ③ |
| 锚定四档状态机（个股风险轴，施工模板） | src/zephyr/regime/core/anchored_state_machine.py 全文实读：classify_state 纯函数 :98-109、compute_features rolling PIT :112-133、结构常数区 :72-81、STATE_NAMES :86-91、落库 run_compute/FetchResult :185-204 | ✅ 实查在产 | scripts/ch/build_anchored_state_history.py；validate_p0_discrimination --prob-table | **两态 P-S 规则层的施工模板**：纯函数核+结构常数+热身期剔除+幂等重建 | ④后端 |
| HMM 7 态概率层 | regime_detector.py:107 REGIME_STATES；:8 INVARIANTS 4 基态+3 overlay | ✅ 实查在产 | 全 regime 链 | 过频切换③病（研究册 §5.1）由 jump 层治，HMM 层保持不动 | ③ |
| TRANSITION_CONFIG 阶梯状态机 | regime_detector.py:304-330 实读（T1/T2/T3 各 trigger/confirm/fail+strong_confirm，判定优先级取首个满足） | ✅ 实查在产 | overlay 态覆盖 | 拓扑约束的仓内先例：状态转移带阶段门槛——"单边↑↔↓须经横向或高门槛"可同款实现 | ③ |
| jumpmodels 概率层（JM/CJM/SJM） | 全仓 grep "jump_model\|jumpmodel" src+scripts 零命中；regime 包内 grep -i "jump" 零命中（2026-10-13） | ⬜ 空白待建 | [3] 灰度主轨（跳变代价+各态后验） | 外部依赖 jumpmodels（Apache-2.0，研究册 §7 已核）；sklearn 风格可本地封装 | ③+④ |
| P-S 规则层（牛熊年代学） | 全仓 grep "pagan\|sossounov\|dating_alg" src+scripts 零命中；"牛熊"仅 momentum.py:1100 Elder-Ray 牛熊力（不同物）与前端徽章文案（2026-10-13 实据） | ⬜ 空白待建 | [7] 标定集真值段；[4] 离线复核基底 | 参数（±8 月窗/15/6/16 月相位）为美股月频，A 股日频重标定=P2 预冻结+留证（研究册 §3.4） | ③ |
| 状态拓扑约束 | 无仓内对应件（TRANSITION_CONFIG 为单程 overlay 非闭合拓扑） | ⬜ 空白待建 | 状态机两引擎 | 研究册 §13-4：横向邻接双单边、↑↔↓ 互转须经横向或高门槛（Pang & Lin 三对角实证） | ③ |
| 多周期仲裁（周态→日态方向先验） | 无仓内对应件 | ⬜ 空白待建 | 状态机日层 | 研究册 §13-9：层级是先验不是裁决 | ③ |

# 2. 与既有资产的边界（不推倒重来清单）

1. **直接复用零改动**：HMM 7 态概率层（两态线在其上做语义重排，不改 regime_detector）；TRANSITION_CONFIG 阶梯判定模式（拓扑约束同款实现）；裁定 #304 锚定方法论。
2. **模板复用（新建件照抄骨架）**：P-S 规则层按 anchored_state_machine.py 骨架新建——结构常数区（窗/相位门槛）+纯函数核（build_states）+热身期剔除+FetchResult 幂等落库；**不改本尊**（本尊=个股风险四档语义，裁定 #229 冻结）。
3. **参数换面**：jump 层 walk-forward 节拍（建议同季度，省对账）；P-S 参数美股→A 股日频重标定。
4. **禁触碰**：regime_state_anchored 表语义（五消费者在产，grep 实据）；两态新状态**另立新表**。

# 3. 施工要点（代码实读中的坑）

1. **结构常数纪律**：anchored_state_machine.py:70-81 注释明示"锚定阈值，禁静默调整；调整须语义复核留痕"。P-S 的窗/相位/幅度门槛同款入结构常数区——A 股重标定换值=语义复核留痕事件，不是随手调参。
2. **热身期语义**：build_states 对 vol_pct NaN 行直接剔除不产出（:149 dropna）——P-S 层热身=首个完整 ±8 月窗（约 160-170 交易日，无权威出处须自标），首段边界前无状态日须显式标 warmup 而非默认横向。
3. **右端确认≠实时**：P-S censoring 需右端窗口确认（离线年代学），规则层输出的"段边界"带确认滞后——实时面状态归 [4] 拐点/日层，禁拿离线定案段冒充实时态（研究册 §3.3 分工）。
4. **锚定重排的自动跳过分支**：#304 原文"n_states≠4/列不足自动跳过"——两态 jump 层若做同款锚定，态数守卫必须显式（否则静默无锚定跨期漂移）。
5. **拓扑先行**：状态机拓扑（§13-4）要在参数标定**之前**钉死——转移矩阵结构（横向邻接）约束了 jump 层的可转移集与规则层的相位合并方向；先标参后钉拓扑会返工。
6. **裁定措辞精度**：#230 原文是"方向**预测**属因子层职责"（risk 组件 vs 收益考卷的层间职责错配论证）。两态"单边↑"的语义=形态向描述非收益方向预测——P2 呈批文书必须引原文精确对齐，防误读为推翻 #230。

# 4. 自审闸三态裁定

| 项 | 裁定 | 理由 |
|---|---|---|
| #229 反转/扩界裁定草案 | **施工**（P1 呈批件） | 先决门不过全线停摆；成本=文书一件 |
| P-S 规则层 | **施工** | 离线真值段=标定集与复核基底，无它则 [4][7] 无靶可打；模板现成边际成本低 |
| jump 概率层 | **施工** | 治③病+天然灰度后验喂 [3]；jumpmodels Apache-2.0 sklearn 风格集成成本低 |
| 拓扑约束件 | **施工** | 三对角实证+P2 呈批项 4 的落地载体；先钉后标参防返工 |
| sticky HDP-HMM 路线 | **方案封矿** | 研究册 §5.3 工程结论：MCMC 太重 PIT 生产不可行，终局由 jump 跳变惩罚替代——已有产物覆盖，留案底防重挖 |
| 多周期仲裁（周态先验） | **挂起排期** | 终局有位（多窗口分数混合），但依赖日层状态机先立；解锁条件=两态日层过 B4 事件吻合 |
