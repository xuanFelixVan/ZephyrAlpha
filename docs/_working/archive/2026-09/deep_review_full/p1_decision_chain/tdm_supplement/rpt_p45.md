---
ttl: task_bound
title: 深度审查作业簿——个股资金面分析
owner: st-deeprev-20260918
created: 2026-09-18
---

# 深度审查报告：个股资金面分析（P45）（GLM-5.3-Flash / 基线 2fa92002c3）

- 状态: **已审**
- 级别: P1｜类型: stage
- 基线 commit: 2fa92002c3（目标文件零漂移已核）
- 审查者: GLM-5.3-Flash / st-deeprev-20260918
- 入口锚点: `src/zephyr/signal_ashare/capital_flow_pattern_analyzer.py`
- TDM 节点: TDM-E-L3-12-1（stage）
- 备注: 阶段0对账补册对象（T08 缺口清册）；MOD-SIG-022/D-SIGNAL-22；出处文档锚 `D:\临时工作区\依赖图-D-SIGNAL-信号域.md` 为仓外路径已不可达（:36，与 P33 同族文档债）
- 生产调用方: **0（分析器零实例化：唯一消费声明为字段级——short_term_stock_selector.py:153 `capital_flow_pattern` 字段"来自 D-SIGNAL-22"、intraday_buy_sell_point_analyzer.py:4 同声明，但两消费方均无 import、字段无人生产恒"未知"——产消断链的字段级孤儿）**
- 测试文件: `tests/signal_ashare/test_capital_flow_pattern_analyzer.py`（28 用例，本班次实跑 28/28 绿）

## 1 对象快照

474 行四维分析器：五类形态识别（四线开花/机构独强/机构主力背离/弱势反弹/全线溃退，评分制 argmax，<20 分 UNKNOWN）、散户狂热反向指标（占比>50%→sell/≤15%→buy）、机构分歧机会（min(正和,负和)/总绝对值≥0.3）、多线共振（≥3 线同向）。全零输入→UNKNOWN 防误判（:257-259）；降级有日志+is_degraded。测试覆盖：五形态+四维度。排除项：两字段级消费方（S08 域已审/日内买卖点域）。

## 2 六轴审查日志表

| 轴 | 发现 | 证据锚点 | 严重级 | 验证法 |
|---|---|---|---|---|
| A 深度 | 数学①：五形态评分制 argmax+20 分门槛、全零防误判（:257-259）、分歧度 min/total ∈[0,0.5]（:389）、共振 3/4 线计数（:415-421）、综合分四权重复检 0.35+0.20+0.20+0.25=1.0（:444-449）——公式层全部自洽 | capital_flow_pattern_analyzer.py:257-259,389,415-449 | 通过 | 权重和验算 |
| A 深度 | **量纲②实锤：阈值单位失真——输入契约=净流入万元（:127），而 solo_min_institutional=1.0/divergence_min_abs=1.0（:87,:93）按万元解释=1 万元≈零门槛：机构 +10 万 vs 主力 −10 万即判"机构主力背离"满分 100（:306-311 两条件恒易满足）**；阈值显然按归一化单位设计（设计文档默认值）却作用在原始万元累计和上——形态判别在真实量级下退化为符号组合判定，阈值无甄别力（checklist #7 量纲失真族） | :87,93,127,306-314 | P2 | 构造 机构+10/主力−10（万元）观察 DIVERGENCE conf=100 |
| A 深度 | 边界③：NaN 输入滑过校验（_validate 只查非空 :427-434）→ sum NaN → 五形态比较全 False→best_score<20→UNKNOWN 静默（无日志、is_degraded=False）——fail-safe 但不可分辨"真未知"与"毒数据"；prices 首值 0/负→weak_rebound 价格腿跳过（:321 `prices[0]>0` 守卫）正确 | :257-259,276-277,321,427-434 | P3 | NaN 输入观察 UNKNOWN 无日志 |
| B 上游 | checklist #6 断供：四线序列由调用方注入（数据源=L2 资金流分类，"主力/机构/散户/游资"四分类本身是噪声明代理——见 F 轴文献）；空序列→降级有日志（:178-180）；market_sentiment_score 输入声明来自 D-SIGNAL-25 但**分析器内从未使用**（:133 字段注入后零引用——死输入契约） | :133,176-180 | P3 | grep market_sentiment_score 在本文件引用 |
| C 下游 | **孤儿裁定（字段级）：分析器零生产实例化**；消费方 selector:153 与 intraday_buy_sell_point 的 capital_flow_pattern 字段契约无生产者承载——**若未来消费方按字段非"未知"做分支，字段恒"未知"=下游分支死代码**（当前无害、接线时爆）；MATURITY=production 虚标同 P33 | selector:153 | P1(接线期) | `grep -rn "CapitalFlowPatternAnalyzer(" src/ --include=*.py` |
| D 旁系 | checklist #4 双承载：四线定义（主力/机构/散户/游资）与 money_flow 数据表分类（TF12 daily_capital 族）的类别词表是否同源未对账——本件按线求和依赖上游列语义，线定义真源缺位；与 S04 mainline_probability 资金维（0.6/0.4 公式）不同构无重复；五形态词表在 selector/日内买卖点两处字段消费（字符串耦合同 P37 案例） | :127-131 | P3 | 对照 money_flow 表列名 |
| E 对抗 | 五问：①静默失败=NaN→UNKNOWN 无日志（上述）②假阳性=万元阈值无甄别力致形态误判（实锤量纲案）③断供=空序列降级有痕④重触发幂等⑤时序=序列顺序无校验（乱序价格序列→涨幅腿反向，隐式"时间升序"契约未文档化） | :316-325 | P2(同量纲案) | 倒序 prices 观察 weak_rebound 误判 |
| F 新鲜度 | 主力资金净流入=大单分类噪声明代理（学界与业界共识：分类≠真实机构行为）；散户占比反向指标方向与 Tsinghua PBCSF 账户级研究一致（小散追涨杀跌、定时差）；**对等已有（方向性）+口径噪声声明建议**——五形态置信度应叠加"分类噪源"折扣 | https://www.pbcsf.tsinghua.edu.cn/__local/9/47/F4/AFC4D9BE22A5AFCDE4D29013AB5_5FEC9FB6_77594.pdf （Tsinghua PBCSF, Retail Trading and Return Predictability in China） | 通过 | WebSearch 2026-09-18 |

## 3 SOTA 对照

- 对等已有：散户资金占比反向指标有账户级实证支撑（方向正确）；主力线=大单分类噪声为已知局限。
- 立卡候选：阈值量纲归一（按流通市值或成交额占比归一四线）——修复 P2 量纲缺陷的正解。

## 4 缺陷清单

1. P2：**阈值量纲失真（万元输入 vs 1.0 阈值≈零门槛）**——五形态判别退化为符号组合；建议归一化输入（占比/市值比）或按真实万元量级重标阈值；验证法=§2 A 轴构造命令。
2. P1（接线期）：字段级孤儿（分析器零实例化+下游字段恒"未知"）；MATURITY=production 虚标；验证法=§2 C 轴 grep。
3. P3：NaN→UNKNOWN 静默无日志；market_sentiment_score 死输入字段；序列时序契约未文档化。

## 5 挂起疑问

- 四线分类与 money_flow 数据表列语义的真源关系——接线前需一份数据契约对账（否则 sum 的对象语义存疑）。

## 6 完备性自评

六轴全查（F 带 URL）。长尾：①28 测试全部按"设计单位"构造数据（万元量纲缺陷零覆盖=测试同源盲区）②出处文档锚仓外失效③ Overall 分数的四维权重无标定依据。

## 7 收口裁定（收口方填）
