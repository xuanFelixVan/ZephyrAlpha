---
ttl: task_bound
doc_type: report
title: 深度审查报告——卖出信号评分器（E02）
owner: st-deeprev-20260918
created: 2026-09-18
---

# 深度审查报告：卖出信号评分器（E02）

- 状态: **已审**
- 级别: P1｜类型: 卖出族评分
- 基线 commit: 2fa92002c3（工作树 bf65648609；本文件自基线零变更，锚点双有效）
- 审查者: GLM-5.3-Flash / st-deeprev-20260918
- **裁定#309 约束声明**：卖出族整族挂起（ruling_registry.yaml:3833-3839，2026-09-17）——审查照常，施工受裁定约束。
- 入口锚点: `src/zephyr/sell_decision/core/sell_signal_scorer.py:122(score_signals)/:86(AccuracyStat.adjusted_rate)/:68(InvalidScoreInputError)`
- 接线现状（grep 实证）：包外零导入——引用仅 core 内部（sell_signal_accuracy_monitor.py:45 消费 AccuracyStat）+测试；与 E01 同族结构性空转。
- 测试文件: tests/sell_decision/test_sell_signal_scorer.py
- 材料包缺项: 无（对象小而封闭）

## 1 对象快照

- 范围：score_signals 纯函数（confidence×strength×贝叶斯准确率×共振，[0,1] 封顶+确定性排序）+ AccuracyStat 收缩统计。纯函数无 IO，准确率由调用方注入。
- 测试覆盖概况：专测在位；负路径（统计矛盾/加成越界）有 INVALID 契约。

## 2 六轴审查日志表

| 轴 | 发现 | 证据锚点 | 严重级 | 验证法 |
|---|---|---|---|---|
| A | 贝叶斯收缩正确：`(hits+α·0.5)/(total+α)`=Beta(4,4) 先验后验均值，α=8；2/2→0.6 防"100% 命中"过拟合读数——数学对 | sell_signal_scorer.py:86-88, :63 | 已查无（正面） | adjusted_rate(2,2) 手算对照 |
| A | **无统计时全体信号 ×0.5**：accuracy 缺省取中性 0.5（:160），乘法结构下"未接统计"=系统性腰斩全部评分——与 E01 融合阈值（willingness>0.7 示例）联用时几乎不可达。文档已声明但系统级效应（默认降权）需接电前 Owner 知悉 | sell_signal_scorer.py:159-160, :165 | P2 | 无 stats 调 score_signals 看全体 score 减半 |
| A | strength 双侧 clamp [0,1]（:158）比 docstring">1 截断"更强（负值也截 0）——方向安全；confidence 未 clamp（信任 SELL-01），越界经乘法+封顶兜住（:166） | sell_signal_scorer.py:157-158, :166 | P3 | 构造越界输入观察 |
| A | 共振判定按 (symbol,direction) 组内 distinct timeframe≥2（:148-153）：UNKNOWN 计一种值但无法自共振（需≥2 不同值）——与 E01 的"双方非 UNKNOWN"口径略异（此处 UNKNOWN+另一 timeframe 可共振），两兄弟实现同概念不同判（checklist #14 同族） | sell_signal_scorer.py:148-153 vs sell_signal_fusion_engine.py:369-380 | **P2** | UNKNOWN+D1 两信号：scorer 判共振，fusion 不判——同输入两组件结论相反 |
| A | 空输入返回 []（:145-146）vs E01 空输入 raise InvalidFusionInputError——同族两入口对空输入行为相反，接电后调用方易踩 | sell_signal_scorer.py:145-146 vs fusion:294-295 | P3 | 对照两函数 |
| A | 排序确定性：(-score, symbol, signal_type.value) 三键（:180）——比 docstring"同分按 symbol"更细，确定性达标 | sell_signal_scorer.py:180 | 已查无（正面） | — |
| B | 上游 SellSignal.confidence/strength 契约信任 SELL-01 校验；accuracy_stats 由调用方注入（禁自造管道，:36 纪律声明）——负值/hits>total 显式 raise（:114-119）fail-closed | sell_signal_scorer.py:114-119 | 已查无（正面） | — |
| C | 下游：accuracy_monitor（包内）；融合/仲裁/紧迫度按头注为概念消费方，实际 grep 无 score_signals 生产调用——同族孤儿 | grep 实证 | P1（族级，并入 E01） | 同 E01 验证法 |
| D | 兄弟评分器：sell_urgency_scorer（317 行）另打紧迫分、fusion 打意愿分——三套打分（score/willingness/urgency）语义分工在 blueprint 声明，数值互相不可替（设计），但三套阈值体系接电后需对账表 | 包内结构 | P3 | 读三组件输出契约 |
| E | 重放/重入：纯函数零状态，同输入同输出（INVARIANTS 声明兑现）；异常仅两类 INVALID——无静默吞点 | 全文 | 已查无 | — |
| E | A 股口径：无市场微结构假设（信号级评分），T+1/跌停不在本层——同 E01 接电前置项 | 设计边界 | 已查无 | — |

## 3 SOTA 对照

1. **贝叶斯收缩准确率调整（对等已有）**：beta-binomial 收缩是小样本命中率标准做法（经验贝叶斯教科书口径）；置信度×强度乘法合成为集成信号评分常规结构（ensemble confidence-weighted scoring，Somisetti 2025 TechRxiv《Multi-Model Ensemble Approach for Stock Price Forecasting》同族；AIMS Press NHM 2026 ensemble thresholds 口径）。
2. **共振加成 ×1.15（对等已有/参数自定）**：多时间框架确认加成为技术分析常规（见 E01 报告 §3-2），0.15 幅度为项目自定。
3. 结论：**对等已有**；缺统计×0.5 的默认语义建议接电前 Owner 复核（非算法错误，是默认值政策）。

## 4 缺陷清单

1. **[P2] 无统计时全体评分 ×0.5 的默认降权**——证据 :159-160/:165；影响：接电后若调用方未接准确率统计管道，全部信号评分系统性减半，与下游阈值联用=漏报向偏移（不报错只偏）；建议：缺统计改为 1.0 中性+undiscounted 标记，或强校验"调用方必须供 stats"；验证法：无 stats 调用对照。
2. **[P2] 共振口径与 E01 不一致（UNKNOWN 参与共振的判定相反）**——证据 ：148-153 vs fusion:369-380；影响：同组信号在评分器获加成、在融合器无加成（或反之），两组件共振计数不可对账；建议：抽公共判定函数（单一真源）；验证法：同输入喂两组件 diff 结论。
3. **[P3] 空输入行为与 E01 相反**（:145 vs fusion:294）；验证法：对照调用。
4. **[P3] confidence 未 clamp 依赖上游**（:157）；验证法：越界构造。
5. **[P1-族级] 结构性孤儿**——并入 E01 族级发现（裁定#309 载体）。

## 5 挂起疑问

1. accuracy_stats 的注入方是谁（接电后）？stats 管道缺席时的默认政策（0.5 vs 1.0）需 Owner 裁定。
2. score 与 E01 willingness、urgency scorer 三套数值的下游使用优先级——接电设计文档缺口。

## 6 完备性自评

- 六轴全查：是（小对象全量逐行）。长尾：①SellSignal 校验细节（collector 对象）；②三套评分体系联动设计（接电时设计项）。

## 7 收口裁定（收口方填）
- 三态逐条:
- 修复 commit:
- 复检结论:
