---
ttl: task_bound
doc_type: report
title: 深度审查作业簿——市场内部结构传感器（已审）
owner: st-deeprev-20260918
created: 2026-09-18
---

# 深度审查报告：市场内部结构传感器（P09）— GLM-5.3-Flash / st-deeprev-20260918

- 状态: **已审**
- 级别: P1｜类型: stage
- 基线 commit: 2fa92002c3（目标文件基线后零漂移）
- 审查者: GLM-5.3-Flash/st-deeprev-20260918
- 入口锚点: `src/zephyr/signal_ashare/limit_up/limit_up_followthrough.py`
- TDM 节点: TDM-E-L1-S2
- 生产调用方: limit_up_ecosystem_leadership.py（同包活件）+ __init__ 导出
- 测试文件: tests/signal_ashare/limit_up/test_limit_up_followthrough.py（合批 187 passed）

## 1 对象快照
MOD-SIG-078 全文件（399 行）：昨封板池/昨炸板池今表现 + 市场炸板率三腿统计，纯函数核+薄加载层。观测层（不接交易）。排除项：limit_up_ecosystem_leadership / war_pool_generator 等同包兄弟。测试实跑通过。

## 2 六轴审查日志表
| 轴 | 发现 | 证据锚点 | 严重级 | 验证法 |
|---|---|---|---|---|
| A 深度 | 炸板定义（high≥limit_up 且 close<limit_up）、炸板率 (attempted−sealed)/attempted（attempted≤0 守卫）正确；**NaN 中毒实证**：today_pct 单值 NaN→avg/median/max 全 NaN 且 degraded=False 静默出账（数学四问 NaN 项命中） | :69-77,201,255-258；实测见验证法 | **P2** | `python -c "import sys; sys.path.insert(0,'src'); from zephyr.signal_ashare.limit_up.limit_up_followthrough import *; r=compute_followthrough_stats('2026-09-18','2026-09-17',[PoolStock(symbol='600519')],[],{'600519': float('nan')}, 100, 90, None); print(r.sealed, r.degraded)"` |
| A 边界 | 双池全空→degraded；今日缺数据票跳过+notes（停牌票自然缺——口径正确）；双端榜排序带 symbol tiebreak 确定性 | :199-204,265-270 | 已查无 | 空 df/缺 kline 各测（测试已覆盖） |
| A A股 | 昨池×今表现=T+1 语义；stk_limit 当日涨停价 join 正确；quality_flag=1 过滤；上市首日无涨停价（limit_up NULL）自动排除炸板池——A股口径过关 | :69-77 | 已查无 | — |
| B 上游 | 四腿独立降级（单腿异常 notes 不炸）——好；但 NaN/None pct 无校验（见 A）；limit_type='涨停' 硬编码默认含 ST 5% 板与主板 10% 板混算（统计语义 Owner 应知情） | :352-374,108 | P3 | 注入含 None 的 today_pct 观察 float() 抛 ValueError 未接 notes |
| C 下游 | 消费方=limit_up_ecosystem_leadership（同包，grep 实证）+包导出；情绪页指标卡候选未接线——观测值失真沿 leadership 链传播；爆炸半径=情绪观测维度 | grep 实证 | 已查无 | grep 命令复跑 |
| D 旁系 | 与 MOD-SIG-025 YesterdayLimitUpPerformance 消费侧 dataclass 在码复用（docstring :22-23）；market_breadth_snapshot attempted/sealed 字段复用口径声明——无双承载冲突 | :8,22-27 | 已查无 | 读 breadth 快照 DDL |
| E 对抗 | 五问：①单腿降级全 notes 留痕（好）②attempted=0 不适用（None）防假阳性 ③无心跳（日频批件）④纯函数幂等 ⑤prev>current 日期倒置无校验（T<T-1 时静默空池 degraded，语义仍对但留痕无解释） | :241-244,330-331 | P3 | 传 prev>current 看输出 |
| F 新鲜度 | **已检索**：涨停止板次日表现文献——Liu 2022（Economic Modelling，涨停后过度反应/反转）；Wan 2015（PLOS ONE，涨停次日 continuation/reversal 概率无单调趋势）；Zhang 2024（IREF，A股短期反转显著、动量不显著）。结论：**对等已有且兼容**——本件为观测层无方向主张，文献结论（反转倾向）恰好提示下游勿把"昨涨停今表现均值高"当正向动量用 | https://www.sciencedirect.com/science/article/abs/pii/S0264999322001560 ；https://pmc.ncbi.nlm.nih.gov/articles/PMC4395215/ ；https://www.sciencedirect.com/science/article/abs/pii/S1059056024006452 | — | — |

## 3 SOTA 对照
涨停次日表现观测：对等已有（文献：Liu 2022 / Wan 2015 / Zhang 2024，见轴 F）；本件无 alpha 主张，与文献张力点在消费侧解读（登记于 §5）。

## 4 缺陷清单
1. **P2 NaN 静默中毒**：建议 _pool_stats 入口 isfinite 校验（NaN/Inf 跳过+notes）。验证法：单行复现见轴 A。
2. P3 limit_type 默认混板统计语义需 Owner 知情。
3. P3 日期倒置（prev>current）无显式校验/留痕。

## 5 挂起疑问
- 文献显示 A 股涨停后短线反转倾向——下游（leadership/情绪页）若将 sealed 池高均值解读为"接力强"需谨慎，建议在消费侧文档标注反转证据。

## 6 完备性自评
六轴全查。长尾：market_breadth_snapshot 的 attempted/sealed 上游口径（他件产出）未审；同包 leadership 消费侧对 NaN 的二次防御未审。
