---
ttl: task_bound
title: 深度审查作业簿——结构强度评估（已审）
owner: st-deeprev-20260918
created: 2026-09-18
---

# 深度审查报告：结构强度评估（P11）— GLM-5.3-Flash / st-deeprev-20260918

- 状态: **已审**
- 级别: P1｜类型: stage
- 基线 commit: 2fa92002c3（目标文件基线后零漂移）
- 审查者: GLM-5.3-Flash/st-deeprev-20260918
- 入口锚点: `src/zephyr/signal_ashare/sector/sector_analyzer.py`
- TDM 节点: TDM-E-L2-01-1
- 生产调用方: sector_report_builder.py / sector_strength_aggregator.py（grep 实证，活件）；docstring :5 "未接线待排期"声明已过时（双向文档漂移）
- 测试文件: tests/signal_ashare/sector/test_sector_analyzer.py（39 passed）

## 1 对象快照
MOD-SIG-026 全文件（420 行）：6 维度板块分析（强度/延续性/轮动预警/启动条件/风格适配/抱团瓦解）→ 综合状态。纯规则打分，无 IO。排除项：sector_strength_aggregator 聚合口径（其自身域）。测试 39 passed。

## 2 六轴审查日志表
| 轴 | 发现 | 证据锚点 | 严重级 | 验证法 |
|---|---|---|---|---|
| A 深度 | 权重和=1.0（0.30/0.20/0.20/0.15/0.15）；评分域 clamp [0,100] 全程成立；**默认分支状态误标（P2）**：_determine_status 对 strength∈[40,70) 无分支命中→一律返回"加速"——实测 strength=55 的中性板块状态="加速"；[20,40) 无 launch_ready 同样落"加速"。"加速"语义被污染为默认兜底 | :399-420；实测见验证法 | **P2** | `python -c "import sys; sys.path.insert(0,'src'); from zephyr.signal_ashare.sector.sector_analyzer import *; a=SectorAnalyzer(); d=SectorData(sector_name='x',limit_up_count=2,total_stocks=50,tier2_count=1,tier3_count=0,sector_index_change_pct=0.01,sector_index_volume_change_pct=0.0,consecutive_up_days=2,consecutive_volume_up_days=1,leader_change_pct=0.01,leader_lagging=False,net_inflow=1.0,has_policy_support=False,has_order_landing=False,technical_breakout=False); print(a.analyze(d).sector_status)"` |
| A 深度 | 死代码：`max_tier = max(tier2>0, tier3>0)` 计算后从未使用（:203）；ERROR_CONTRACT 声明 SectorDataError 但全文件无 raise 点（幽灵契约，checklist #9 变体——数据不完整实际不报错） | :203,171,13 | P3 | grep SectorDataError raise |
| A 边界 | 无除法无 NaN 传播面（纯阈值比较）；负涨停数/空板块等非法输入静默按 0 走弱分支（无校验，与幽灵契约互为表里） | :190-230 | P3 | 传 limit_up_count=-5 观察"弱"分支 |
| A A股 | 连板梯队/涨停数/妖股-趋势票风格/抱团瓦解——A股本土概念语义正确；成交额阈值单位=万亿为隐式契约（默认 1.0=1 万亿，签名未注明） | :129-130,315-322 | P3 | 传 turnover=15000（亿）被误判趋势票 |
| B 上游 | SectorData 纯调用方注入（无来源校验）；consecutive_up_days 与"大涨"语义（轮动预警用连续上涨近似连续大涨）口径靠约定 | :119-121 | P3 | — |
| C 下游 | 消费方实存两处（grep）；status/score 供聚合与报告——状态误标沿 strength_aggregator 传播；爆炸半径=板块层状态维度 | grep 实证 | 已查无 | grep 复跑 |
| D 旁系 | 与 sector_strength_aggregator/sector_ranking_engine 的"板块强度"三件并存：本件=规则6维、ranking=5因子百分位、aggregator=聚合——三套强度口径各异且无换算文档（同族多承载，checklist #4 高危形态，但功能分层尚清晰） | 三文件对读 | P3 | 三模块同板块输入对拍分值差 |
| E 对抗 | 五问：①无吞异常 ②状态误标=假阳性过关面（见 A）③无监控面 ④analyze 幂等除 timestamp=datetime.now(UTC)（输出不可重放比对，P3）⑤无时序面 | :384 | P3 | 同输入两次调用 timestamp 不同 |
| F 新鲜度 | 受阻/不适用：连板梯队情绪周期为 A 股本土游资打法（中文研报语境，无英文 SOTA 对照对象；政策轴 F 允许受阻如实记录） | — | — | — |

## 3 SOTA 对照
受阻/不适用（A股题材情绪周期本土方法论，本批未检索到可对照英文文献；如需可后续查中文金工研报）。

## 4 缺陷清单
1. **P2 默认分支状态误标**：[40,70) 强度板块被判"加速"，下游按状态路由会系统性高估中场板块动能。建议补 "中" 分支（如 40-70→PEAK 前中段状态枚举或 ROTATING/ACCELERATING 细分）。验证法：单行复现见轴 A。
2. P3 幽灵错误契约（SectorDataError 零 raise）+死变量 max_tier。
3. P3 timestamp 非注入（同输入不同输出，违反本仓"同输入必同输出"惯例）。
4. P3 成交额单位隐式契约。

## 5 挂起疑问
- "强度"三套口径（本件/aggregator/ranking_engine）是否 Owner 有意分层？若是，建议在 capability card 记录三口径边界防漂移。

## 6 完备性自评
六轴全查。长尾：sector_report_builder 消费侧对 status 的语义依赖未深钻；测试 39 条对状态机分支覆盖矩阵未逐条核对（抽查默认分支无测试命中）。
