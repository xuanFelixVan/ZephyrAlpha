---
ttl: task_bound
title: 深度审查作业簿——赚钱效应传感器（已审）
owner: st-deeprev-20260918
created: 2026-09-18
---

# 深度审查报告：赚钱效应传感器（P10）— GLM-5.3-Flash / st-deeprev-20260918

- 状态: **已审**
- 级别: P1｜类型: stage
- 基线 commit: 2fa92002c3（目标文件基线后零漂移）
- 审查者: GLM-5.3-Flash/st-deeprev-20260918
- 入口锚点: `src/zephyr/signal_ashare/limit_up/lhb_premium_analyzer.py`
- TDM 节点: TDM-E-L1-S3
- 生产调用方: llm_premarket_analysis.py / limit_up_potential_scorer.py / limit_up_ecosystem_leadership.py（grep 实证，活件）；docstring CONSUMERS"（MVP 阶段无）"已过时（文档漂移 P3）
- 测试文件: tests/signal_ashare/limit_up/test_lhb_premium_analyzer.py（合批 187 passed）

## 1 对象快照
MOD-SIG-057 全文件（460 行）：T 日龙虎榜→T+1 预判三名单（高开候选/低开风险/反核观察）+溢价系数降权（独食/一日游 ×0.3）。席位身份经 seat_registry.yaml。degraded 语义完备。排除项：seat_pattern_analyzer（MOD-SIG-056 正交件）。

## 2 六轴审查日志表
| 轴 | 发现 | 证据锚点 | 严重级 | 验证法 |
|---|---|---|---|---|
| A 深度 | 净买率=net/(buy+sell) 口径自洽；降权规则链完整可追溯（tags+reasons）；隔日卖出率分母排"次日不可观测"（披露 Top5 卖出不可见常态）——统计口径诚实 | :236-276,241-245 | 已查无 | 造 history 样本手算 rate |
| A 深度 | **混合口径不可比**：summary 行在→turnover=全量 buy+sell；缺行→回退席位行合计（Top5）——同一次运行内不同标的 turnover 分母口径不同，净买率跨标的不可比（docstring 已声明但仍构成横截面排序风险，若下游按 ratio 排序） | :344-351 | P3 | 对同一标的造/删 summary 行对比 ratio |
| A 深度 | 反核规则依赖 reason 文本含"跌停"关键词——交易所上榜原因标准措辞（"日跌幅偏离值达7%"等）是否含"跌停"二字未经数据实测（checklist #13 外部契约未实测），fanhe_watchlist 可能结构性近空 | :99,381-387 | **P2** | `SELECT reason, count() FROM c1_market.dragon_tiger WHERE trade_date=近一日 GROUP BY reason LIMIT 20` 查含"跌停"占比 |
| A 边界 | turnover≤0 跳过；空榜单→degraded=True"不可用于决策"（checklist #6 合规：断供不是恒 0 而是显式降级）；日期格式非法 fail-closed | :314-315,352-353,152-158 | 已查无 | 传非交易日日期看 degraded |
| B 上游 | seat_registry 缺文件/解析失败→降级空档案（is_top_youzi 全 False→高开候选阈值实质收紧，静默口径漂移——registry 空转时高开候选可能归零且仅 log.warning） | :172-182,200-207 | **P2** | 传 registry_path=不存在路径，对比高开候选名单缩水 |
| C 下游 | 三消费方实存（llm_premarket_analysis/potential_scorer/ecosystem_leadership）；premium_factor 供次日预判加权——错值直接影响候选排序，爆炸半径=M3-⑤ 次日预案维度 | grep 实证 | 已查无 | grep 复跑 |
| D 旁系 | 与 MOD-SIG-056 正交分工文档化（:29-33）；youzi 白名单 ("龙头连板","首板") 与 056 youzi_follow_styles 声称对齐——**双承载**（两处常量各自维护，registry 风格标签改名则两处需同步，checklist #4） | :98 vs seat_pattern_analyzer 白名单 | P3 | diff 两文件白名单常量 |
| E 对抗 | 五问：①历史复核失败仅 log 跳过动态口径（留痕 OK）②degraded 防"无数据当有数据"③registry 空转面（见 B）④重跑幂等（纯读+内存）⑤次日映射用"历史出现日∪当日"近似交易日序列——长假期间 LHB 日期跳跃时 next_day 近似仍成立（LHB 日必为交易日，其下一 LHB 日≈下一交易日，近似合理） | :404-415,253 | P3 | 造跨节假日样本对拍 |
| F 新鲜度 | **已检索**（limit_up 族共享）：Liu 2022（Economic Modelling：涨停后过度反应与反转）；Zhang 2024（IREF：A股短期反转显著/动量不显著）；Wan 2015（PLOS ONE：涨停次日 continuation/reversal 无单调趋势）。结论：**立卡候选（验证向）**——本件"高开候选=次日高开概率升"是延续性主张，与文献主流（反转）存在张力；但本件以"净买率+机构/一线席位"为条件（聪明钱条件），非朴素涨停延续，文献不直接否定；建议对 high_open_candidates 做 T+1 实证回测后再进决策链 | 同 rpt_p09 轴 F 三链接 | — | — |

## 3 SOTA 对照
高开候选延续性主张 vs 文献反转主流：立卡候选（回测验证向），三来源带 URL 见轴 F。

## 4 缺陷清单
1. **P2 反核关键词契约未实测**（"跌停"在 reason 字段的命中率决定规则④生死）。验证法：SQL 抽查。
2. **P2 registry 空转静默收紧**：seat_registry 缺失/空档时高开候选静默缩水（仅 warning），建议 degraded 或 notes 显式留痕。验证法：传空 registry 对比名单。
3. P3 docstring CONSUMERS"（MVP 阶段无）"与实际三消费方漂移（文档先行失真）。
4. P3 youzi 白名单双承载（056/057 两处常量）。
5. P3 turnover 回退口径混合（横截面可比性）。

## 5 挂起疑问
- premium_factor∈{1.0,0.3} 二值离散——0.3 的标定依据未见产物锚（44号 §9.7 口径来源=yueniuzq 2026-07，非实证产物）；同 §5 建议一并回测标定。

## 6 完备性自评
六轴全查。长尾：dragon_tiger/dragon_tiger_seat 表数据质量（缺行率/字段空值率）未画像（需 DB 访问授权）；seat_registry.yaml 覆盖率未清点。
