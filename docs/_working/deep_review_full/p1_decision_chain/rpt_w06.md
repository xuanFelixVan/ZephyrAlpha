---
ttl: task_bound
doc_type: report
title: 深度审查作业簿——尾部对冲信号（W06）
owner: st-deeprev-20260918
created: 2026-09-18
---

# 深度审查报告：尾部对冲信号 tail_hedge_signal（GLM-5.3-Flash / 基线 2fa92002c3）

- 状态: **已审**
- 级别: P2｜类型: 算法
- 基线 commit: 2fa92002c3（实测 HEAD=b93d923b95 为其后代）
- 审查者: GLM-5.3-Flash / st-deeprev-20260918
- 入口锚点: `src/zephyr/pf_alloc/core/tail_hedge_signal.py:27`
- 生产调用方: **零（grep 全仓仅自引用）——孤儿裁定：成立**
- 测试文件: tests/pf_alloc/test_tail_hedge_signal.py（4 测试，随批实跑通过）
- 备注: STABILITY=experimental 标注诚实；头注宣称消费方"TDM UP-5/策略工厂 E8"查无

## 1 对象快照

- 范围：`tail_hedge_signal.py` 全 71 行：滚动历史分位 VaR 阈值 → 尾部均值 CVaR 近似 → 阈值比较出对冲建议 DataFrame。纯函数无 IO。
- 排除项：无。
- 测试覆盖概况：仅 4 测试；含暖机期 NaN 预期行为测试（test_no_nan_in_output，line 50-53）；**无窗口切片一致性、无含 NaN 输入、无空序列测试**。
- 材料包缺项声明：运行时证据包与数据画像未取；Python 3.12.8 + numpy/pandas。
- checklist 前置过检：#4（与 W05 的 CVaR 双实现漂移）命中；#7（口径/窗口量纲）命中；#8（孤儿）命中；其余查无。

## 2 六轴审查日志表

| 轴 | 发现 | 证据锚点 | 严重级 | 验证法 |
|---|---|---|---|---|
| A 深度 | **CVaR 尾部窗口多取 1 条（off-by-one）**：VaR 阈值用 `rolling(window)`（line 52，窗口=[i-window+1, i]），尾部均值切片 `r[max(0,i-window):i+1]`（line 61）=[i-window, i] 共 **window+1 条**。实测 window=20、i=60 → 尾部长度 21。阈值分位与尾部均值样本集不一致，且与 W05.predicted_cvar（window 条）互斥 | tail_hedge_signal.py:52,61 | P2 | `len(r[max(0,i-win):i+1])` 实测 == win+1 |
| A 深度 | **docstring 与实现矛盾**：line 19"CVaR 用分布预测的分位数计算（**非历史回溯**）"，实现=滚动历史模拟分位（line 51-63）。与 W05 头注同一措辞复制——同源文档漂移 | line 19 vs 51-63 | P2 | 对照读 |
| A 深度 | **含当日收益的 PIT 边界未文档化**：var/cvar 在 i 期窗口含 r[i] 本身（rolling 至 i 含端点）——若 T 日收盘前调用，r[T] 是不完整数据；若 T+1 决策用 T 序列则安全。调用时点契约无任何声明 | line 52,61（含端点切片） | P2 | 代码读+构造日内调用剧本 |
| A 深度(边界·查无) | window<10/confidence ∉(0,0.5) 拒收（line 46-49）；非数值 coerce→NaN；暖机期与全 NaN 窗口 → None→NaN→hedge=False（fail-soft，line 58-65）；tail 空 → None；实测 120 点序列运行无异常、hedge 列 bool、cvar 列 float64（pandas 把 None 收敛为 NaN）——**NaN 不致崩溃、不穿透成错误信号** | line 46-66 | — | 120 点随机序列实测 |
| A.3 测试 | 4 测试过薄：无 NaN 输入、无窗口一致性、无 cvar_excess 语义断言 | tests/.../test_tail_hedge_signal.py | P3 | 测试文件通读 |
| B 上游 | portfolio_returns 来源/复权口径/频率契约未声明（日收益假设隐含在 cvar_threshold=-0.03 量纲里）；输入换月/换频率后阈值静默失义 | line 36-38 | P3 | docstring 无契约段 |
| C 下游 | 零消费方=爆炸半径 0；输出三列语义自洽（hedgebool/excess=cvar-threshold，line 65-66）。equal 边界：cvar==threshold 不触发（严格 <），量纲上可接受 | line 65-70 | — | 构造等值输入 |
| D 旁系 | **CVaR 双实现漂移实锤**（与 W05 镜像登记）：W05 窗口=window 条、本件=window+1 条，同概念两处算结果不同——合并为单一工具函数（checklist #4） | tail_hedge_signal.py:61 vs risk_budget_allocator.py:92 | P2 | 同输入对拍首行 |
| D 旁系(文档) | "对标 Owner 2025-09 笔记 9.1"（line 17）内部引证无锚点路径，无法核真 | line 17 | P3 | 查无笔记文件路径 |
| E 对抗 | 纯函数幂等、无状态（查无重复触发/时序死角）；唯一时序面=PIT 边界（已单列） | 全文件 | — | 同输入两次调用比对 |

## 3 SOTA 对照

- 滚动历史模拟 CVaR 阈值触发对冲属常规做法（历史模拟法/分位门槛型风控信号）。战役检索预算 2 次已耗于 W02/W05，**本件未独立检索——如实记"受阻（预算受限未查证）"**；接线时建议对照：CVaR 的极值理论（EVT/POT）估计与已实现波动触发（VIX 门槛型）两条业界路径。

## 4 缺陷清单

1. **[P2] 窗口 off-by-one**：现状=尾部均值窗口比 VaR 阈值窗口多 1 条且与 W05 互斥（实测 21 vs 20）。影响：接线后 CVaR 口径与域内另一实现不可互换、回测/实盘口径漂移。建议：切片改 `r[i-window+1:i+1]` 并与 W05 收敛为共享函数。验证法：§2 实测长度断言。
2. **[P2] "非历史回溯"文档失实**：建议 docstring/蓝图改为"当前=历史模拟法；分布预测为升级路线"（与 W05 头注同步修）。验证法：对照读。
3. **[P2] PIT 时点契约缺失**：建议注明"T 序列须为已收盘收益，T 日决策消费至 T-1"。验证法：文档 grep。
4. **[P3] 测试过薄/输入契约未声明/内部笔记引证无锚**：随接线批补齐。

## 5 挂起疑问

- UP-5"预测 CVaR"的终极口径（车道 E 分布预测）与本件历史模拟实现的差距是文档问题还是施工欠账？若属后者，建议在 construction_backlog 登记升级项而非改文档措辞了事——需 Owner/挖矿侧裁定。

## 6 完备性自评

- 六轴全查：A/B/C/D/E 全查；F 受阻已记；查无项=NaN 崩溃路径、异常吞没、重复触发。
- 长尾：cvar_threshold=-0.03 对 A 股组合波动量纲的适配（涨跌停日尾部厚度）无数据画像支撑——数据画像缺项所致，列长尾。

## 7 收口裁定（收口方填）
- 三态逐条: 
- 修复 commit: 
- 复检结论: 
