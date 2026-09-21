---
ttl: task_bound
title: 深度审查作业簿——RRG 轮动序列（已审）
owner: st-deeprev-20260918
created: 2026-09-18
---

# 深度审查报告：RRG 轮动序列（P16）— GLM-5.3-Flash / st-deeprev-20260918

- 状态: **已审**
- 级别: P1｜类型: stage
- 基线 commit: 2fa92002c3（目标文件基线后零漂移）
- 审查者: GLM-5.3-Flash/st-deeprev-20260918
- 入口锚点: `src/zephyr/signal_ashare/sector/sector_rrg.py`
- TDM 节点: TDM-E-L2-02-1
- 生产调用方: mainline_candidates / mainline_probability / sector_rotation_score_mapping（grep 实证，活件）
- 测试文件: tests/signal_ashare/sector/test_sector_rrg.py（合批 81 passed）

## 1 对象快照
MOD-SIG-026 supplement（236 行）：JdK DualEma RRG（RS-Ratio/RS-Momentum/四象限）+ whipsaw 2 日确认 + z-score 跨象限修正，纯函数。排除项：RRG 增强未施工项（transition matrix/三 TF/角度法，收缩登记 :32-33 已声明）。测试实跑通过。

## 2 六轴审查日志表
| 轴 | 发现 | 证据锚点 | 严重级 | 验证法 |
|---|---|---|---|---|
| A 深度 | JdK 公式正确（RS=100×P_s/P_b；Ratio=EMA10/EMA26×100；Mom=EMA10(Ratio)/EMA26(Ratio)×100）；EMA 种子=首值（通达信 adjust=False 等价）声明与实现一致 | :19-22,93-101,138-145 | 已查无 | 手算 5 点小样对拍 |
| A 深度 | **EMA 预热期简并点未标注（P3）**：种子=首值使早期 RS-Ratio/Momentum 恒=(100,100)，classify_quadrant 严格 >100 判定→简并点全判 LAGGING（实测前 6 点 (100.0,100.0)→LAGGING）——下游若重放全序列会把预热期当真实滞后态 | :155-157；实测见验证法 | P3 | `python -c "import sys; sys.path.insert(0,'src'); from zephyr.signal_ashare.sector.sector_rrg import *; n=70; ps=[100.0]*40+[100.0+0.5*(i-40) for i in range(40,n)]; pts=compute_rrg_series(ps,[200.0]*n); print(pts[0], pts[5].quadrant)"` |
| A 边界 | 长度不一致/不足 62/基准价≤0 全 fail-closed；ema 空序列→[]；z-score 样本<2 或 σ=0→0.0（中性不修正） | :130-136,210-218 | 已查无 | 造 61 日应抛 |
| A A股 | 基准 880001 由调用方注入（缺省全板块均值替代声明）；四象限→交易信号映射（LAGGING=AVOID）为项目裁量 | :62-67 | 已查无 | — |
| B 上游 | 输入纯序列无升序校验（倒序=RSM 镜像，静默）——同族契约盲区第三例（P08/P13 同型） | :119-121 | P3 | 倒序喂入对比象限 |
| C 下游 | 三消费方实存（主线候选/主线概率/轮动打分映射）；象限错判→主线候选增删，爆炸半径=主线池构成 | grep 实证 | 已查无 | grep 复跑 |
| D 旁系 | 与 ranking_engine 因子 5 的分工声明（截面快照 vs 时序轮动）文档化且成立（:29-30）；whipsaw 确认与 z 修正为本件自有增强（spec 内含） | :29-33 | 已查无 | — |
| E 对抗 | 五问：①无吞异常 ②whipsaw 2 日确认防单日假信号（好）③无监控面 ④纯函数幂等 ⑤无时序面（预热期简并=时间起点攻击面，见 A） | :165-197 | 已查无 | — |
| F 新鲜度 | **已检索**：JdK RS-Ratio/RS-Momentum 四象限方法学=Julius de Kempenaer 原创口径，StockCharts ChartSchool 官方文档与 Kempenaer 本人站点（relativerotationgraphs.com）确认为业界标准实现。结论：**对等已有**（本件公式与标准 DualEma 口径一致；whipsaw 确认+Z 修正为合理自有增强） | https://chartschool.stockcharts.com/table-of-contents/chart-analysis/chart-types/relative-rotation-graphs-rrg-charts ；https://relativerotationgraphs.com/educational/the-building-blocks-for-rrg/ （Kempenaer 官方） | — | — |

## 3 SOTA 对照
RRG JdK DualEma：对等已有（与标准方法学一致，双来源见轴 F，Kempenaer 官方+StockCharts）。

## 4 缺陷清单
1. P3 EMA 预热期简并点（全 LAGGING）无标注/裁剪——建议 compute_rrg_series 跳过前 long×2 点或输出 warmup 标记。验证法：见轴 A 单行。
2. P3 序列升序契约 in-band 不可验（族共性）。

## 5 挂起疑问
- 消费方是否重放全序列（含预热简并段）——建议收口时抽查 mainline_candidates 的 RRG 消费起点。

## 6 完备性自评
六轴全查。长尾：Z-score 修正阈值 ±2 的标定依据无产物锚（与族内其他初拟参数同状态，spec 已声明待校准）。
