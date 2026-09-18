---
ttl: task_bound
doc_type: report
title: 深度审查作业簿——轮动状态五分类（已审）
owner: st-deeprev-20260918
created: 2026-09-18
---

# 深度审查报告：轮动状态五分类（P20）— GLM-5.3-Flash / st-deeprev-20260918

- 状态: **已审**
- 级别: P1｜类型: stage
- 基线 commit: 2fa92002c3（目标文件基线后零漂移）
- 审查者: GLM-5.3-Flash/st-deeprev-20260918
- 入口锚点: `src/zephyr/signal_ashare/sector/sector_rotation_state.py`
- TDM 节点: TDM-E-L2-04-1
- 生产调用方: sector_divergence（P15 逐日重放）、sector_report_builder、mainline_candidates（grep 实证，活件）
- 测试文件: tests/signal_ashare/sector/test_sector_rotation_state.py（合批 49 passed）

## 1 对象快照
MOD-SIG-026 supplement（113 行）：4 维输入→5 状态规则映射 + watch_score 固定映射（-0.10~+0.03）。被 P15 逐日重放消费（SEC-03 标定器样本源）。测试实跑通过。

## 2 六轴审查日志表
| 轴 | 发现 | 证据锚点 | 严重级 | 验证法 |
|---|---|---|---|---|
| A 深度 | 优先级序（派发>高潮>主线>分歧>中性）风险方向优先正确；快轮动期 CLIMAX 阈值放宽 0.30→0.35 防集中度天然偏高误判（自适应设计合理）；**但 DISTRIBUTION_RISK 未随 fast_rotation 放宽**——快轮动期 disp+hhi>0.25 组合在头部天然集中时更易误派发（不对称自适应，设计意图不明） | :99-103 | P3 | 造 fast_rotation=True 且 hhi=0.26+disp 对比两状态 |
| A 边界 | top_n_hhi 空/总额≤0→0.0；NaN 成交额：sum→NaN→`NaN<=0` False→排序含 NaN→hhi 可 NaN 返回（NaN 分位进 classify 比较全 False→NEUTRAL 兜底——行为安全但 score NaN 可透传 P15 hhi 序列污染 z-score） | :72-78 | P3 | 传含 nan 的 turnovers 看 hhi |
| A A股 | up_ratio/hhi/领涨连击/放量滞涨四维为 A 股板块生态语义；legulegu/rebuildingsociety 2026 依据为内部声明锚 | :26-27 | 已查无 | — |
| B 上游 | 输入比率超界"由调用方保证"（:13 显式弃守）——up_ratio>1/hhi<0 不校验静默参与判定；P15 重放侧实测传参正确（up_ratio∈[0,1] by construction :469）——当前链路成立，独立调用风险登记 | :13,81-97 | P3 | 传 up_ratio=1.5 观察 CLIMAX 误判 |
| C 下游 | watch_score 注入板块强度综合层（全板块统一加减）；DISTRIBUTION_RISK=-0.10→M2 降档触发（P15 :1003-1005）——状态误判直接驱动降档，爆炸半径=全仓仓位档位（本件最重下游面） | :63-69 vs sector_divergence.py:1003-1005 | 已查无 | grep 复跑 |
| D 旁系 | 与虹吸态（P21）绝对阈值/相对 z 分工文档化（:22-25）；与 regime 12 态正交声明成立；5 状态判据与 P19 高潮判据异构（见 rpt_p19 轴 D） | :22-25 | 已查无 | — |
| E 对抗 | 五问：①无吞异常 ②disp_signal∈{0,1} 非布尔校验（传 2 同 1 处理，宽容）③无监控面 ④纯函数幂等 ⑤无时序面 | :99 | 已查无 | 传 disp_signal=2 |
| F 新鲜度 | 受阻/不适用：5 状态分类为项目自定义市场生态分类（内部 spec 真源），无外部对照对象 | — | — | — |

## 3 SOTA 对照
受阻/不适用（项目自定义分类法）。

## 4 缺陷清单
1. P3 NaN 透传面（top_n_hhi 不滤 NaN）。
2. P3 快轮动自适应不对称（CLIMAX 放宽、DISTRIBUTION 不放宽，意图需 Owner 确认）。
3. P3 输入校验显式弃守（调用方契约，当前链路成立）。

## 5 挂起疑问
- 阈值初拟待 2026 实盘标定（:26-27 自声明）——同族标定欠账。

## 6 完备性自评
六轴全查（全文件 113 行逐行）。无长尾。
