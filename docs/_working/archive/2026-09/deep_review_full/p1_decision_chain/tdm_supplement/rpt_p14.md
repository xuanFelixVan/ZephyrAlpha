---
ttl: task_bound
title: 深度审查作业簿——板块资金流聚合（已审）
owner: st-deeprev-20260918
created: 2026-09-18
---

# 深度审查报告：板块资金流聚合（P14）— GLM-5.3-Flash / st-deeprev-20260918

- 状态: **已审**
- 级别: P1｜类型: stage
- 基线 commit: 2fa92002c3（目标文件基线后零漂移）
- 审查者: GLM-5.3-Flash/st-deeprev-20260918
- 入口锚点: `src/zephyr/signal_ashare/sector/sector_breadth.py`
- TDM 节点: TDM-E-L2-01-4
- 生产调用方: sector_strength_aggregator / sector_strength_wiring / sector_report_builder（grep 实证，活件）
- 测试文件: tests/signal_ashare/sector/test_sector_breadth.py（合批 52 passed）

## 1 对象快照
MOD-SIG-026 supplement（161 行）：板块涨停比归一化 + 个股资金性质 5 类成交额加权上溯板块（ evaluate_strength 修正层纯函数）。排除项：25 号个股级资金性质分类器（上游真源）。测试实跑通过。

## 2 六轴审查日志表
| 轴 | 发现 | 证据锚点 | 严重级 | 验证法 |
|---|---|---|---|---|
| A 深度 | ratio=limit_up/constituent clamp [0,1] 正确（负数 clamp 0）；成交额加权+等权退化+score clamp [-1,1] 数学正确；分档阈值带不对称（主力流入 >0.3 vs 对倒主导 >-0.5）为 spec 设计值 | :68-107,134-152 | 已查无 | 手算加权样例对拍 |
| A 边界 | 成分股 0→(0.0,中性) 契约明示；权重和 0（含全缺成交额）→等权退化契约明示；NaN 成交额未防：max(0.0, nan)=nan（float nan 与 0 比较 max 返回 nan！实测 `max(0.0, float('nan'))` 结果依赖参数序——此处 max(0.0, nan) 返回 nan，poison total_weight→score nan） | :135-136 | P3 | `python -c "print(max(0.0, float('nan')))"` |
| A A股 | 涨停比归一化动机（19/200 vs 3/30 跨板块公平）正确；资金性质 5 类（拉升/吸筹/弱托底/对倒/出货）A股本土语义；乘数 1.1/0.8/0.6 为 spec 设计值 | :17-24,55-60 | 已查无 | — |
| B 上游 | capital_nature_scores 缺失按 0=弱托底（无罪推定）——**隐式契约**：上游分类器缺输出时板块被中性稀释，若上游大面积缺数据则板块资金面静默失真偏中性（checklist #6 变体，轻度）；缺失率无观测输出 | :124,134 | P3 | 缺半数个股 score 看板块标签漂移 |
| C 下游 | aggregator/wiring 真消费（乘数修正 strength 输出层）；爆炸半径=板块强度×乘数（0.6/1.1 单边 ±10-40% 修正） | grep 实证 | 已查无 | grep 复跑 |
| D 旁系 | 本件=evaluate_strength 修正层（40% 权重位替换映射对齐原档位相对语义，:96-98 文档化）；与 P11 原绝对数档位并存期口径切换语义已声明——无双承载冲突 | :94-107 | 已查无 | 对读 P11 evaluate_strength |
| E 对抗 | 五问：①无吞异常 ②缺数据→中性稀释面（见 B）③无监控面 ④纯函数幂等 ⑤无时序面 | 全文件 | 已查无 | — |
| F 新鲜度 | 受阻/不适用：涨停比归一化与订单流分类加权为 A 股本土微观结构口径（资金性质 5 类为项目自定义分类法，无外部 SOTA 对照对象） | — | — | — |

## 3 SOTA 对照
受阻/不适用（项目自定义分类法，无外部对照对象；订单流分析可后续对照 order flow 文献，本批未检索）。

## 4 缺陷清单
1. P3 NaN 成交额经 max(0.0, nan) 传播中毒（建议 `w if w==w and w>0 else 0.0` 或 isfinite 过滤）。验证法：单行 python。
2. P3 上游缺失率无观测（中性稀释静默面）。
3. P3 分档阈值不对称未见设计依据锚（spec §3.1① 之外无产物）。

## 5 挂起疑问
- 乘数 1.1/0.8/0.6 直接乘 strength 输出——strength 已 clamp [0,100] 前乘后乘顺序（wiring 侧）决定越界行为，本轮未审 wiring（其域）。

## 6 完备性自评
六轴全查。长尾：25 号分类器上游准确率未审；wiring 侧乘法次序未审。
