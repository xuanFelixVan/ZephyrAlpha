---
ttl: task_bound
title: 深度审查作业簿——回踩质量分级
owner: st-deeprev-20260918
created: 2026-09-18
---

# 深度审查报告：回踩质量分级（P26）（GLM-5.3-Flash / 基线 2fa92002c3）

- 状态: **已审**
- 级别: P1｜类型: stage
- 基线 commit: 2fa92002c3（25 目标文件经 `git diff --stat 2fa92002c3` 核实零漂移）
- 审查者: GLM-5.3-Flash / st-deeprev-20260918
- 入口锚点: `src/zephyr/signal_ashare/sector/sector_pullback.py`
- TDM 节点: TDM-E-L2-07（stage）
- 备注: 阶段0对账补册对象（T08 缺口清册）
- 生产调用方: **0（grep 全仓零 import；头注 [CONSUMERS] 自declared"待 G05 选股引擎 / BM-BUY-04"=前向声明态）**
- 测试文件: `tests/signal_ashare/sector/test_sector_pullback.py`（29 用例，本班次实跑 29/29 绿）

## 1 对象快照

156 行纯函数模块，三函数：`fib_retrace_ratio`(:67)、`classify_volume_pattern`(:81)、`grade_pullback`(:106)+动作映射 `pullback_action`(:152)。Fib×量能×板块强度三维取最弱档定 A/B/C，时间窗 <2 或 >15 日返回 None 不评级。排除项：docs/03_modules algo_flow yaml 未审（数据外迁件非代码）。测试覆盖概况：边界（2/15/16 日、70/69.9、0.5/0.618、无效 swing raise）齐备，无假阳性嫌疑（断言精确到值非弱断言）。

## 2 六轴审查日志表

| 轴 | 发现 | 证据锚点 | 严重级 | 验证法 |
|---|---|---|---|---|
| A 深度 | 数学四问①：Fib 公式 `(high-current)/(high-low)` 正确，`max(0.0,·)` 下界钳制正确（创新高→0） | sector_pullback.py:78 | 通过 | 手算 (110-105)/10=0.5，tests:21 同值 |
| A 深度 | 边界②：除零已防（swing_high≤swing_low→ValueError:77）；NaN current_price 经 max 比较语义落入 grade_pullback 时 `NaN<=0.5/0.618` 均 False→C 档=最保守档，方向安全但静默 | sector_pullback.py:76-78,130-135 | P3 | `fib_retrace_ratio(110.,100.,float('nan'))` 观察；`grade_pullback(float('nan'),'SHRINKING',80.,5)` 返回 "C" |
| A 深度 | 文档 vs 代码③：docstring 称 A 档缩量"递减至 50 日均量 35-50% 区间达标"，代码只查 `latest<=0.50` 无 0.35 下界（0.05 也判 SHRINKING）；另"3-10 交易日健康窗"未编码进评级（11-15 日照常可评 A） | sector_pullback.py:21,41 vs :96,126 | P3 | `classify_volume_pattern([0.8,0.3])` 返回 SHRINKING 对照 docstring |
| A 深度 | checklist #1/#7 过：无分母漂移、无量纲/PIT 问题（纯函数不吃行情数据）；A 股口径 N/A（不涉 T+1/停牌/复权） | — | 通过 | — |
| B 上游 | 输入全为调用方算好的标量（fib_ratio/量比序列/强度分/天数），无数据表消费→checklist #6 断供恒0不适用；volume_ratios 空 list→MIXED（:88-89）保守正确 | sector_pullback.py:88-89 | 通过 | 传 `[]` 观察 |
| C 下游 | **孤儿裁定：全仓 grep `sector_pullback`/`grade_pullback` 零生产调用方**（仅包 `__init__.__all__`:7 与 config/trading_decision_map.yaml:1167 实现锚文本）；头注自declared"待 G05"=前向声明态非静默死亡 | grep 证据见 §4 验证法 | P1(接线期) | `grep -rn "sector_pullback\|grade_pullback" src/ scripts/ --include=*.py \| grep -v sector_pullback.py` |
| D 旁系 | checklist #4 双承载：无第二份 Fib 回撤/回踩分级实现（grep `fib_retrace\|grade_pullback` 全仓唯一）；TDM 节点文本与代码口径一致（config/trading_decision_map.yaml:1167"三维取最弱档"） | — | 通过 | 同上 grep |
| E 对抗 | 五问：①静默失败=NaN→C（保守向，无害）②假阳性=volume 单日 >1.0 即 EXPANDING（:90-92 先于序列判断，单日尖峰误判派发——docstring 本意"最新>均量=放量"，语义自洽）③断了没人知道=孤儿本体④重触发 N/A 纯函数⑤时序 N/A | sector_pullback.py:90-92 | P3 | `classify_volume_pattern([0.5,1.01])`→EXPANDING 单点跳变 |
| F 新鲜度 | Fib 回撤+缩量回踩买点是业界常规方法论（Investopedia Fibonacci Retracement；edgeful 实证 61.8% 为趋势延续最可靠档）。阈值档位（38.2/50/61.8/78.6）与业界惯例对齐=**对等已有**，无立卡点 | https://www.investopedia.com/terms/f/fibonacciretracement.asp ；https://www.edgeful.com/blog/posts/using-fibonacci-retracement-ltrading-guide | 通过 | WebSearch 2026-09-18 |

## 3 SOTA 对照

- 对等已有：Fib 分级阈值（≤50%A/50-61.8%B/>61.8%C/>78.6%结构破坏）与业界标准档位一致（Investopedia, 2024；edgeful, 2023 实证 61.8% 关键档）。
- 对等已有：缩量回踩确认（volume dry-up=A 档、回踩放量=派发 C 档）为经典量价学派做法（prorsi, 2024 拉回策略框架）。
- 立卡候选：无。驳回：无。

## 4 缺陷清单

1. P1（接线期地雷，非现行 P1）：**零生产调用方孤儿**（checklist #8）。现状=三函数全仓无生产 import；影响=突破失败降级与买入优先级链（BM-BUY-04）规划中的上游缺位；建议=G05 选股引擎接线时以本件为唯一实现并补 NaN 入参防御；验证法=`grep -rn "grade_pullback" src/ --include="*.py"`（仅测试命中）。
2. P3：NaN 输入静默落 C 档（保守向）——建议接线期在入参处显式 reject；验证法=§2 A 轴命令。
3. P3：docstring 35-50% 下界与健康窗 3-10 日两处文档-代码漂移——建议修 docstring 或补下界检查；验证法=`classify_volume_pattern([0.8,0.3])`。

## 5 挂起疑问

- spec §6 阈值待 G05/G08 校准（源码 :26 自declared）——校准属施工期裁定，非缺陷。

## 6 完备性自评

六轴全查（A/B/C/D/E 逐条有结论，F 带 URL）。长尾：①真实数据画像未做（无生产调用即无真实输入分布）②`classify_volume_pattern` 逐日严格递减在噪声量能下可能过严（MIXED 偏多）——留接线期观察。

## 7 收口裁定（收口方填）
