---
ttl: task_bound
doc_type: report
title: 深度审查作业簿——回撤限额分配（W07）
owner: st-deeprev-20260918
created: 2026-09-18
---

# 深度审查报告：回撤限额分配器 MaxDdLimitAllocator（GLM-5.3-Flash / 基线 2fa92002c3）

- 状态: **已审**
- 级别: P1｜类型: 闸门
- 基线 commit: 2fa92002c3（实测 HEAD=b93d923b95 为其后代）
- 审查者: GLM-5.3-Flash / st-deeprev-20260918
- 入口锚点: `src/zephyr/pf_alloc/core/maxdd_limit_allocator.py:88`（主类 :157）
- 生产调用方: **零（grep 全仓仅自引用）**
- 测试文件: tests/pf_alloc/test_maxdd_limit_allocator.py（12 测试，随批实跑通过）
- 备注: MATURITY=production 标注与零调用方事实不符；头注"当前回撤缺失/未知策略→Fail-Closed"存在 NaN 旁路（见 A1）

## 1 对象快照

- 范围：`maxdd_limit_allocator.py` 全 224 行：输入校验（Fail-Closed）→ utilization 三档动作（NORMAL/DERATE/SUSPEND）→ 加权归一/全暂停兜底。纯函数无 IO。
- 排除项：无。
- 测试覆盖概况：12 测试全绿；覆盖三档/校验/全暂停；**无 NaN 回撤、NaN base_weight 测试**。
- 材料包缺项声明：运行时证据包与数据画像未取；Python 3.12.8。
- checklist 前置过检：#7 变体（NaN 口径旁路）命中；#8（孤儿+production 失实标注）命中；其余查无。

## 2 六轴审查日志表

| 轴 | 发现 | 证据锚点 | 严重级 | 验证法 |
|---|---|---|---|---|
| A 深度 | **NaN 回撤绕过 Fail-Closed 判 NORMAL**：`dd < 0` 对 NaN 为 False（line 203）、`utilization >= 1.0` 与 `>= derate_threshold` 对 NaN 均为 False（line 205-209）→ action=NORMAL、factor=1.0。实测 {"a":nan,"b":0.05} → actions 双 NORMAL、weights {0.5,0.5}。**回撤爆表的策略被 NaN 静默洗白成满配**——与头注 INVARIANTS"当前回撤缺失/未知策略→Fail-Closed"（line 8）直接冲突（NaN 既非缺失也非未知，恰好旁路） | maxdd_limit_allocator.py:201-213 | P1 | `MaxDdLimitAllocator().allocate((S("a",1,0.1),S("b",1,0.1)), {"a":nan,"b":.05})` → actions[a]==NORMAL |
| A 深度 | **NaN base_weight → 全 NaN 权重**：`base_weight <= 0` 放过 NaN（line 136），raw=nan → total=nan → `total <= 0` False → weights 全 NaN 无告警。实测 {'a':nan} | line 133-137,215-219 | P2 | 同上单策略实测 |
| A 深度 | **"只减不增"表述与终权重行为不符**：DERATE/SUSPEND 策略因子只减，但归一化（line 219）使存活策略终权重**上升**（例：两策略一方 DERATE ×0.5 → 另一方 0.5→0.667）。头注 line 8"降档/暂停只减不增"按因子口径成立、按最终权重口径失实——预算向健康策略再集中是合理设计但表述误导 | line 8,215-219 | P2 | 两策略一方 dd 触 DERATE 对比前后权重 |
| A 深度(边界·查无) | 空预算表/重复 id/未知策略/缺失回撤/负回撤/预算 NaN（`0.0<nan<=1.0`=False 拒收，line 138）/config NaN（line 113-116）全部 fail-closed 抛 ZA-PA-0013；u==1.0 边界=SUSPEND 正确；全暂停→全零+all_suspended=True 零除防护（line 216-218）——**除 NaN dd/base_weight 外边界查无** | line 185-218 | — | 逐条构造实测 |
| A.3 测试 | 主路径与校验路径覆盖合理；NaN 两路径（P1/P2）零测试 | tests/.../test_maxdd_limit_allocator.py | P3 | grep 测试文件无 nan |
| B 上游 | current_drawdowns 契约=正数幅度（docstring line 43），**NaN 语义未写**——正是 A1 旁路的文档成因；来源 D_RISK drawdown_tracker 的产出是否可能 NaN（资金曲线断点）未契约化 | line 41-44,176-183 | P2 | 蓝图/docstring grep 无 NaN 条款 |
| C 下游 | 零消费方=当前爆炸半径 0；接线后 weights 喂资金分配，A1 直接决定"回撤爆表策略是否继续拿钱"——资金安全面。对象内无 except（查无吞没） | 全文件 | — | grep except → 0 |
| D 旁系 | 与 MOD-PA-003（组合级 MaxDD>15% 一刀切，multi_strategy_capital_allocator.py:31）分工有明文（本件 line 30-31"按策略颗粒度"）；但两者**均未接线**（C01 链无 import）——"组合级 vs 逐策略"两套回撤减仓机制并存且都空转，登记合并/择一接线评估（挖矿联动） | maxdd_limit_allocator.py:30-31 | P3 | grep MultiStrategyCapitalAllocator/MaxDdLimitAllocator 调用方 |
| E 对抗 | 纯函数幂等、无状态、无时序依赖（查无）；重复触发安全 | 全文件 | — | 同输入两次 allocate 比对 |

## 3 SOTA 对照

- 逐策略回撤预算（drawdown budget）+ 阈值降档/暂停属机构风险预算常规实践（回撤控制 overlay 家族）。战役检索预算 2 次已耗于 W02/W05，**本件未独立检索——如实记"受阻（预算受限未查证）"**；接线时建议对照：组合层 drawdown control（Grossman/Zhou 型时序风险约束文献系）与 CPPI 型乘数纪律的阈值衔接。

## 4 缺陷清单

1. **[P1] NaN 回撤→NORMAL 满配（旁路 Fail-Closed）**：现状=NaN dd 三重比较全 False → 满权重（实测）。影响：接线后风控关键输入被污染（drawdown_tracker 断点、上游表 NaN）时暂停机制整体失效且无声——资金安全面缺陷；当前零调用方未爆发。建议：line 202 后加 `math.isfinite(dd)` 校验，非法抛 InvalidMaxDdInputError（与头注 Fail-Closed 声明对齐）；base_weight 同加（P2 项一并）。验证法：§2 实测一行复现。
2. **[P1] 结构性孤儿 + MATURITY=production 失实**：现状=零生产调用方（grep），头注 production/consumer 声明（line 5-7）无实物。影响：治理错觉——以为逐策略回撤闸在运行。建议：接线裁决（C01 链挂接点=screen_panel 后、budget 分配前）或降级标注。验证法：§2 grep。
3. **[P2] NaN base_weight → 全 NaN 权重**：随发现 1 修法一并补 isfinite。验证法：§2 实测。
4. **[P2] "只减不增"头注表述失实**：建议改为"因子只减不增；终权重经归一化后健康策略可升（预算再集中）"。验证法：§2 实测。
5. **[P2] dd 契约未含 NaN/断点语义**：建议蓝图补"drawdown_tracker 产出须有限值，NaN=风控事件应显式失败"。验证法：文档 grep。
6. **[P3] 与 MOD-PA-003 双闸并存均空转/测试缺口**：登记挖矿联动与用例补齐。

## 5 挂起疑问

- 接线优先级建议：本件若与 C01 接线，其 utilization 所需"策略级资金曲线"（当前 D_RISK 是否产出策略颗粒度回撤）未确证——接线施工前需先核 drawdown_tracker 的产出粒度，否则 A1 旁路会在缺数据形态下高频触发。

## 6 完备性自评

- 六轴全查：A（四问+边界实测×2 组 NaN 复算）/B/C/D/E 全查；F 受阻已记。
- 长尾：max_dd_budget 与 C01 max_single_sleeve/单名 cap 的量纲衔接（预算 vs 仓位上限两层约束的先后序）需接线设计时专项——本报告未展开。

## 7 收口裁定（收口方填）
- 三态逐条: 
- 修复 commit: 
- 复检结论: 
