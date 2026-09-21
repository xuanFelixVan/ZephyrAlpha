---
ttl: task_bound
title: 深度审查作业簿——信号合成器（W01）
owner: st-deeprev-20260918
created: 2026-09-18
---

# 深度审查报告：信号合成器 SignalSynthesisCombiner（GLM-5.3-Flash / 基线 2fa92002c3）

- 状态: **已审**
- 级别: P1｜类型: 算法
- 基线 commit: 2fa92002c3（实测 HEAD=b93d923b95 为其后代；两 commit 间 pf_alloc 无代码变更）
- 审查者: GLM-5.3-Flash / st-deeprev-20260918
- 入口锚点: `src/zephyr/pf_alloc/core/signal_synthesis_combiner.py:209`
- 生产调用方: **零（grep src/scripts/services 仅自引用）——孤儿裁定：成立**
- 测试文件: tests/pf_alloc/test_signal_synthesis_combiner.py（17 测试，随批实跑通过）
- 备注: 显式审查项=src 内零生产调用方孤儿嫌疑裁定；checklist #8 历史案例 d9c5f4bb12 即本域

## 1 对象快照

- 范围：`signal_synthesis_combiner.py` 全 363 行：输入校验 → 加权投票 → 共振分级 → 冲突裁决（#208-⑤）→ 跨策略仓位合并。纯内存无 IO。
- 排除项：`ConfidenceCalibrator` 协议（R-96 预留，line 187-197，全仓无实现方）只审契约不审实现。
- 测试覆盖概况：17 测试全绿（7 套件批跑 160 passed / 2.66s）；主路径覆盖可；**无 NaN 拒收、NEUTRAL 带 target_weight、Σweight≠1 三类边界测试**。
- 材料包缺项声明：运行时证据包（日志/reconcile）与数据画像未取（对象纯内存无表消费，画像不适用）；运行环境锁定 Python 3.12.8。
- 缺陷 checklist 前置过检：命中 #8（孤儿死码）；其余 14 条查无。

## 2 六轴审查日志表

| 轴 | 发现 | 证据锚点 | 严重级 | 验证法 |
|---|---|---|---|---|
| C 下游 | **孤儿裁定：成立**。grep `SignalSynthesisCombiner` 全仓仅命中自身（定义/`__all__`/docstring 示例）；头注宣称消费方 MOD-PA-003/D-PF-CORE/D-POSITION（line 5）均无 import；C01 编排器管线为 regime→MetaAllocator→BudgetHandler（allocation_orchestrator.py:18,790），不含本件。MATURITY=production（line 7）与事实不符 | 头注 line 5/7；allocation_orchestrator.py:18 | P1 | `grep -rn "SignalSynthesisCombiner" src/ scripts/ \| grep -v pf_alloc/core` → 空 |
| A 深度 | **NEUTRAL 信号 target_weight 并入方向仓位**：无冲突分支 `relevant = sigs` 不过滤方向（line 330），NEUTRAL（sign=0 不投票）携带的 target_weight 照样累加进 merged_position_weight。实测 LONG(tw=0.4)+NEUTRAL(tw=0.7) → merged=1.0（触 cap） | signal_synthesis_combiner.py:329-344 | P1 | 构造上述两条信号 combine，断言 merged_position_weight==1.0 |
| A 深度 | **Σweight=1 契约无校验→置信度通胀**：docstring 声明"Σ权重=1.0"（line 126），`__post_init__` 只验单条 ∈[0,1]（line 145-152）；confidence=abs(score)/Σweight（line 277-279）。实测 weight=0.25/0.25、conf=1.0/0.0 反向 → conf=0.5（按契约应为 0.25） | line 126,145-152,277-279 | P2 | 上述输入 combine，断言 confidence==0.5 |
| A 深度 | **单信号/全同向即 STRONG 共振**：共振分母只数方向性信号（line 260-262,302-313），1 LONG+2 NEUTRAL → ratio=1.0 → STRONG；NEUTRAL 席位不稀释共振 | line 260-263,302-313 | P2 | 单条 LONG → resonance==STRONG |
| A 深度 | **全 NEUTRAL 输出自相矛盾**：direction=NEUTRAL 且 conflict=False → merged=Σ(tw)>0，方向中性却带仓位语义 | line 330-344 | P2 | 两条 NEUTRAL tw=0.6 → direction==NEUTRAL 且 merged>0 |
| A 深度(边界·查无) | NaN/inf/负权重 fail-closed：`0.0<=val<=1.0` 对 NaN 为 False → InvalidStrategySignalError（line 145-152）；position_cap ∉(0,1] 拒收（line 231-232）。**NaN 不能穿透本件** | line 140-152,231-232 | — | `StrategySignal("a","b",LONG,float("nan"))` → raise |
| A.3 测试 | 主路径断言合理；A 轴三条 P1/P2 边界均无测试钉住 | tests/pf_alloc/test_signal_synthesis_combiner.py | P3 | grep 测试文件无 nan/NEUTRAL-target 用例 |
| B 上游 | 输入=内存列表；"weight 从哪来"无生产答案——天然供给方 W02 头注互指本件（regime_bma_weighting.py:5,30-31）但无人装配；上游断供形态=从未被喂而非喂错 | line 125-126；regime_bma_weighting.py:30-31 | P2 | 见 rpt_w02.md C 轴 |
| C 下游 | 当前零消费方=爆炸半径 0；接线后 merged_position_weight 被 PA-03/PF-CORE 消费，P1 缺陷放大口寸。内部无 except 吞没（grep 0 处，查无） | 全文件 | — | `grep -c except <本文件>` → 0 |
| D 旁系 | 与 W02 分工双方头注互认（本件=投票消费权重、W02=权重生产侧）；与 MOD-PA-003 分层无口径重叠；#208-⑤ 裁决文本忠实性已落地且与头注 INVARIANTS 一致（line 8 vs 269-275,346-363） | 头注 line 8；line 269-363 | — | 对照两文件头注 |
| E 对抗 | 纯函数无状态：幂等、重复触发安全、无时序依赖（查无）；输出顺序=输入分组序（defaultdict 保序） | line 235-246 | — | 同输入两次 combine 逐字段比对 |

## 3 SOTA 对照

- 置信度加权投票合成 = 预测组合（forecast combination）文献的规则化特例。相邻引证：Elliott & Timmermann, *Optimal Forecast Combination Under Regime Switching*, 2004，https://rady.ucsd.edu/_files/faculty-research/timmermann/optimal-forecast-combination.pdf 。结论：**对等已有（简化特例）**。战役检索预算 2 次已分配 W02/W05，本件未独立检索——如实记"受限预算未独立查证"。

## 4 缺陷清单

1. **[P1] 结构性孤儿**：现状=决策链设计件零生产调用方，"合成→分配"上半段缺失且 MATURITY 标注失实。影响：治理误导（头注宣称 production/消费方）；当前爆炸半径 0，接线即激活 P1 数学缺陷。建议：与 W02 成对接线裁决进挖矿/施工队列，或降级 MATURITY=experimental。验证法：§2 C 轴 grep。
2. **[P1] NEUTRAL target_weight 并入方向仓位**：现状=line 330 无冲突分支不过滤方向。影响：接线后未投票方向的仓位建议放大口寸（实测 0.4+0.7→1.0 触 cap）。建议：`relevant` 无条件过滤 `s.direction == direction`，或强制 NEUTRAL 的 target_weight=0 并入校验。验证法：§2 实测脚本。
3. **[P2] Σweight 无校验**：建议 combine() 入口校验 Σweight≈1 或按固定常数归一 confidence。验证法：§2 实测。
4. **[P2] 共振 STRONG 通胀**：建议 directional==0 或 directional<信号总数时封顶 MODERATE（产品口径裁定后落码）。验证法：单信号用例。
5. **[P2] 全 NEUTRAL 带 merged>0**：随发现 2 消除。验证法：§2 实测。
6. **[P3] 测试边界缺口**：补 NaN 拒收/NEUTRAL 合并/Σweight 三用例（轴 A 边界发现→转 property-based 候选，衔接测试工厂）。

## 5 挂起疑问

- 若蓝图对"NEUTRAL 策略的 target_weight"另有语义（如表示持仓维持量，蓝图未写明），发现 2 修法需 Owner 先裁语义——本审查按"NEUTRAL=不投票不贡献仓位"理解。

## 6 完备性自评

- 六轴全查：A（四问+边界实测）/B/C/D/E 全查；查无项=NaN 穿透、except 吞没、时序竞态、重复触发。
- 长尾：calibrator（Platt/Isotonic）全仓无实现，R-96 接入时需复审校准置信度对投票符号的影响；蓝图文件未逐条反查（以代码为真源，蓝图路径见头注 line 1）。

## 7 收口裁定（收口方填）
- 三态逐条: 
- 修复 commit: 
- 复检结论: 
