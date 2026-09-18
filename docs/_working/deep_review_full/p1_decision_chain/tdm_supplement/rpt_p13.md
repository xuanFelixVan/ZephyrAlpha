---
ttl: task_bound
doc_type: report
title: 深度审查作业簿——多周期动量加权（已审）
owner: st-deeprev-20260918
created: 2026-09-18
---

# 深度审查报告：多周期动量加权（P13）— GLM-5.3-Flash / st-deeprev-20260918

- 状态: **已审**
- 级别: P1｜类型: stage
- 基线 commit: 2fa92002c3（目标文件基线后零漂移）
- 审查者: GLM-5.3-Flash/st-deeprev-20260918
- 入口锚点: `src/zephyr/signal_ashare/sector/sector_momentum.py`
- TDM 节点: TDM-E-L2-01-3
- 生产调用方: sector_strength_aggregator / mainline_candidates / sector_divergence / sector_leader / limit_up_potential_scorer / sector_momentum_persistence / risk ashare_stop_loss_engine / sector_report_builder（grep 实证，高扇入活件）
- 测试文件: tests/signal_ashare/sector/test_sector_momentum.py（合批 52 passed）

## 1 对象快照
MOD-SIG-026 supplement（113 行）：q3/q5/q20 多时间框架截面动量加权纯函数。权重 0.4/0.3/0.3 初拟待回测。排除项：sector_momentum_persistence（兄弟件）。测试实跑通过。

## 2 六轴审查日志表
| 轴 | 发现 | 证据锚点 | 严重级 | 验证法 |
|---|---|---|---|---|
| A 深度 | n_day_return 数学正确（base>0/长度守卫 fail-closed）；**并列取平均秩**实现正确（对比 P12 的非确定排名——同族两实现质量不一致，本件为佳） | :42-53,66-77 | 已查无 | 等值 dict 跑 percentile_ranks |
| A 边界 | 单板块→0.5 中性；空→{}；短序列板块整体跳过（含 q3/q5 本可算的——保守取舍已文档化）；NaN 收盘价未防：NaN 收益率进 percentile 排序（NaN 无全序→名次任意）→污染 strength_momentum | :60-65,102-103,110 | P3 | 传含 NaN closes 观察 q 值 |
| A A股 | T+1 可执行（盘后批量）声明；一日游应对动机（Top3 次日重合率 14.8%）有 spec 锚——A股口径过关 | :19-27 | 已查无 | — |
| B 上游 | closes_by_sector 调用方注入，时间升序契约 in-band 不可验（倒序喂入=负动量镜像，静默）；与 P08 同型契约盲区 | :88-89 | P3 | 传倒序序列对比输出 |
| C 下游 | 高扇入（8+ 文件）：动量分进 strength 综合层与主线候选——NaN/倒序污染爆炸半径=板块强度+候选池；无降级路径（跳过即出局） | grep 实证 | 已查无 | grep 复跑 |
| D 旁系 | 与 RRG（21d/63d/252d 相对强度）分工文档化（:23-24）；与 sector_momentum_persistence（持久性兄弟件）口径衔接未审（其域）；**权重 0.4/0.3/0.3 双承载风险**：本件常量 vs 22号 spec §6——初拟值待校准，spec 改权重需同步本件 | :38-39 | P3 | diff spec §6 与常量 |
| E 对抗 | 五问：①无吞异常（fail-closed ValueError）②跳过板块=静默出局（下游需容忍缺键——aggregator 侧行为未审）③无监控面 ④纯函数幂等 ⑤无时序面 | :48-53,100-105 | P3 | — |
| F 新鲜度 | **已检索**（动量族共享）：多期动量混合权重属经典做法（IRFA 2023 趋势规则交易成本敏感性，https://www.sciencedirect.com/science/article/pii/S1057521923004441 ）；短窗 overweight 应对 A 股短线化与学术动量衰减共识方向一致。结论：对等已有（无立卡必要），权重标定待回测（spec 已自知） | 同左 | — | — |

## 3 SOTA 对照
多 TF 动量加权：对等已有（经典动量框架内常规实现，来源见轴 F）。

## 4 缺陷清单
1. P3 NaN 收盘价未防（建议 isfinite 过滤跳过+notes）。
2. P3 时间升序契约 in-band 不可验。
3. P3 权重常量与 spec 双承载（待回测校准时易漂移）。

## 5 挂起疑问
- 跳过短序列板块后下游（aggregator/mainline）如何处理缺键——本轮未深钻（各消费方自身域），建议收口时抽查一处。

## 6 完备性自评
六轴全查。长尾：sector_momentum_persistence 兄弟件口径衔接未审（独立对象）；权重回测标定产物未见（spec 已声明待校准，不算缺陷算路线图）。
