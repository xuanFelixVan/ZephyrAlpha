---
ttl: task_bound
title: 深度审查作业簿——Regime BMA加权（W02）
owner: st-deeprev-20260918
created: 2026-09-18
---

# 深度审查报告：Regime BMA 加权 RegimeBmaWeighting（GLM-5.3-Flash / 基线 2fa92002c3）

- 状态: **已审**
- 级别: P1｜类型: 算法
- 基线 commit: 2fa92002c3（实测 HEAD=b93d923b95 为其后代）
- 审查者: GLM-5.3-Flash / st-deeprev-20260918
- 入口锚点: `src/zephyr/pf_alloc/core/regime_bma_weighting.py:122`
- 生产调用方: **零（grep 全仓仅自引用）——孤儿裁定：成立**
- 测试文件: tests/pf_alloc/test_regime_bma_weighting.py（29 测试，随批实跑通过）
- 备注: 头注宣称消费方"运行时装配批（signal_synthesis_combiner 权重源）"但 W01 并不 import 本件

## 1 对象快照

- 范围：`regime_bma_weighting.py` 全 245 行：滚动窗口精度估计（hit_rate/IC 二选一）→ 后验归一 → 体制切换半衰期混合 → 审计回调。纯内存确定性，时钟/审计注入。
- 排除项：`WeightAuditEvent` 载荷 schema（无独立消费方）。
- 测试覆盖概况：29 测试全绿；覆盖归一/切换混合/错误契约主路径；**无 NaN 观测拒收测试、无 min_samples=1 极端配置测试**。
- 材料包缺项声明：运行时证据包与数据画像未取（纯内存无表消费）；Python 3.12.8 已锁定。
- checklist 前置过检：命中 #8（孤儿）；#6 变体（权重生产断供=无人喂观测）间接命中；其余查无。

## 2 六轴审查日志表

| 轴 | 发现 | 证据锚点 | 严重级 | 验证法 |
|---|---|---|---|---|
| C 下游 | **孤儿裁定：成立**。grep `RegimeBmaWeighting` 全仓仅自引用；头注 line 5 宣称"运行时装配批（signal_synthesis_combiner 权重源 / 体制切换审计落库）"，但 signal_synthesis_combiner 无本件 import，编排器也无。W01 的 StrategySignal.weight 字段（signal_synthesis_combiner.py:126）在生产中无人供给→缺省 1.0 等权 | 头注 line 5；grep 结果 | P1 | `grep -rn "RegimeBmaWeighting" src/ scripts/ \| grep -v pf_alloc/core` → 空 |
| A 深度 | **IC 精度在 min_samples=2 下 winner-take-all**：两点 Pearson r≡±1（或零方差 0），负值截 0（line 113）→ 实测 s1/s2 各 2 条反向观测 → 权重 {1.0, 0.0}。min_samples 校验允许 =1（line 139-140 仅拒 <1），单样本 hit_rate ∈{0,1} 同样极端。样本充分性与度量类型不匹配（IC 需数十级样本才有稳定估计） | line 130,139-140,103-113 | P1 | `RegimeBmaWeighting(min_samples=2, metric=IC).update(bull, {s1:2条, s2:2条})` → {s1:1.0, s2:0.0} |
| A 深度 | **hit_rate 把 (forecast=0, realized=0) 计为命中**：`_sign` 相等即 hit（line 94-100），零预测/中性实现的 tie 抬高精度。实测 [(0,0),(0.1,0.2),(0.1,-0.2)] → 0.667 而非 0.5（有效方向样本口径） | line 94-100 | P2 | 直接调 `_hit_rate` 断言 2/3 |
| A 深度 | **负 IC 一律截 0**：持续反向预测的信号与无信息信号同权处理（line 113），不提供反向使用选项；叠加"全零证据→均匀先验"（line 165-166），一负一零 → 均匀。设计取舍但未在蓝图声明后果 | line 111-113,165-166 | P3 | IC 序列恒负 → 权重与全零输入相同 |
| A 深度(边界·查无) | NaN/inf 观测 fail-closed 拒收（line 189-193 isfinite 检查）；空 observations 拒收（line 182-183）；权重 Σ=1 全程维持（line 166,213-217）；新增/消失信号经并集混合自然衰减（line 209-217）。**NaN 不能穿透本件** | line 182-193 | — | update 带 NaN 观测 → RegimeBmaError |
| A.3 测试 | 主路径断言合理；NaN 拒收与 min_samples=1 两边界无测试 | tests/pf_alloc/test_regime_bma_weighting.py | P3 | grep 测试文件无 nan |
| B 上游 | 观测（forecast/realized）序列由调用方构造：**"forecast 必须先于 realized 产生"的 PIT 契约未文档化**——本件无法校验预测时点对齐，上游倒挂（用实现日已知信息造预测）会被照单全收并污染精度 | line 73-76（SignalOutcome 只有数值对） | P2 | 蓝图/头注无 PIT 声明（grep PIT 无命中） |
| C 下游 | 输出=weights dict + 审计回调；当前零消费方。审计 sink 异常被吞仅日志（line 171-174）——头注声明"sink 异常不阻断如实记录"属既定设计，但审计断链只有 log 一层，无告警/重试 | line 169-174 | P3 | 注入 raise 的 sink → 仅 log.exception |
| D 旁系 | W01 互指分工（权重生产侧 vs 消费侧）文档一致；与 allocation_inputs.confidence_signal（regime→shrinkage，另一权重轴）职责无重叠；无第二份 BMA 实现（查无） | regime_bma_weighting.py:30-31 | — | grep "bma\|BMA" src/ |
| E 对抗 | 状态机时序：**体制快速抖动（A→B→A 反复）每次重置 _updates_in_regime**（line 196-201）→ new_share 恒小（t=1 → 0.129），权重滞留旧体制 ~87%——抖动市况下权重迟钝为设计后果，未见文档声明。**重启丢态**：内存态 _weights/_prev_weights 无持久化，进程重启后 prev=None → effective=raw，半衰期平滑静默失效一轮 | line 149-152,195-208 | P2 | 交替 update 两种 regime 断言 new_share 序列；重启（新实例）后断言无混合 |
| E 对抗(幂等) | 同输入重复 update 非幂等（_updates_in_regime 递增 → new_share 漂移）——在线估计器本质如此，但重放攻击面：调用方重放同一批观测会持续稀释新证据。纯内存无副作用，无双下单风险 | line 201,208 | P3 | 两次同参 update 比对第二次 new_share<1.0 |

## 3 SOTA 对照

1. **对等已有（简化版）**：半衰期混合 ≈ 折扣型模型平均。引证：*A loss discounting framework for model averaging and forecast combination*（arXiv, 2022-2024 修订），https://arxiv.org/html/2201.12045v4 。
2. **立卡候选**：体制切换条件下的组合权重有直接文献支撑，比"精度点估计归一"更贴近本件宣称的 BMA：Elliott & Timmermann, *Optimal Forecast Combination Under Regime Switching*, 2004, https://rady.ucsd.edu/_files/faculty-research/timmermann/optimal-forecast-combination.pdf ；Shi, *BMA under Regime Switching*, Journal of Forecasting 2016, https://ideas.repec.org/a/wly/jforec/v35y2016i3p250-262.html 。适配点：以状态条件边际似然替代精度点估计。
3. **命名澄清（非检索）**：posterior_i = p_i/Σp（line 25,163-167）无先验/无边际似然，实为"精度加权组合"；docstring 自认"轻量版"（line 22）——头注 BMA 名义偏大，建议文档降格表述（P3，并入缺陷清单）。

## 4 缺陷清单

1. **[P1] 结构性孤儿**：权重生产侧从未接入，W01 权重字段缺省 1.0 等权，"体制条件加权"能力整段缺失。影响：决策系统性未按设计运行；接线后 P1-2 才有资金影响。建议：与 W01 成对接线裁决；接线前必须先修 P1-2。验证法：§2 C 轴 grep。
2. **[P1] IC/hit_rate 样本充分性缺失**：现状=min_samples=2 即可产 IC=±1 的 winner-take-all 权重（实测复现）。影响：接线后小样本噪声直接变成 0/1 极端权重。建议：按度量分设门槛（IC≥20、hit_rate≥30）或对 |IC| 做收缩（shrink to uniform）。验证法：§2 A 轴实测。
3. **[P2] hit_rate tie 口径**：零预测/零实现计命中，建议 tie 剔除分母或单列。验证法：§2 实测 0.667。
4. **[P2] PIT 契约未文档化**：SignalOutcome 无法表达预测时点，建议 docstring+蓝图补"forecast 须为 T 日可用信息"契约并留上游审计责任。验证法：grep 文档无 PIT。
5. **[P2] 重启丢态+体制抖动迟钝**：建议权重快照持久化（复用审计落库通道）与抖动检测（N 次/日内切换→冻结混合）。验证法：§2 E 轴两脚本。
6. **[P3] BMA 名义偏大/负 IC 截 0/审计断链仅日志/重放非幂等**：文档表述降格+审计告警升级，随接线批一并处理。

## 5 挂起疑问

- "体制切换审计落库"（头注 line 5）是否另有规划中的落库件（当前无）？若有，W02 的重启丢态修复应挂接该件——需 Owner/挖矿侧确认路线图。

## 6 完备性自评

- 六轴全查：A（四问+边界实测）/B/C/D/E 全查，F 见 §3；查无项=NaN 穿透、第二份 BMA 兄弟实现、线程使用场景（单线程日批前提成立）。
- 长尾：window=250 与体制驻留时长的匹配（体制寿命<窗口时精度估计混态）需真实 regime 序列数据画像才能评估——运行时证据包缺项所致，列长尾。

## 7 收口裁定（收口方填）
- 三态逐条: 
- 修复 commit: 
- 复检结论: 
