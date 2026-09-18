---
ttl: task_bound
doc_type: report
title: 深度审查作业簿——执行算法
owner: st-deeprev-20260918
created: 2026-09-18
---

# 深度审查报告：执行算法（P50）（GLM-5.3-Flash / 基线 2fa92002c3）

- 状态: **已审**
- 级别: P1｜类型: stage
- 基线 commit: 2fa92002c3（目标文件零漂移已核）
- 审查者: GLM-5.3-Flash / st-deeprev-20260918
- 入口锚点: `src/zephyr/ex_sor/core/algo_execution_selector.py`
- TDM 节点: TDM-E-L4-06（stage）
- 备注: 阶段0对账补册对象（T08 缺口清册）；MOD-XS-011/XS-11，SAFETY=H 本批最高
- 生产调用方: **0（精确 import grep 零命中；依赖边 XS-011→XS-005 两端互认（algo_trading_engine.py:5,797 get_algo_types"XS-011 Selector 消费"）但均未接线——与 X04/X03 同属 ex_sor/ex_core 零接线族；[MATURITY]=production 虚标）**
- 测试文件: `tests/ex_sor/test_algo_execution_selector.py`（43 用例，本班次实跑 43/43 绿）

## 1 对象快照

677 行评分驱动算法选择器（六算法 TWAP/VWAP/ICEBERG/POV/IS/ALT）：OrderFeatures 构造即校验（urgency∈[0,1]/quantity>0/ADV>0）→三维评分（size 0.40+urgency 0.35+liquidity 0.25，权重可配且和=1 校验）→max 选取（列表序稳定平局）→全候选 breakdowns 审计留痕；DefaultAlgoEvaluator 效果评估（IS bps+效率分+verdict 三档）。工程纪律好（错误码族/审计内存日志/recommend 无副作用入口）。测试覆盖：特征校验/评分/选取/评估。排除项：algo_trading_engine 深审（X04 域已审）。

## 2 六轴审查日志表

| 轴 | 发现 | 证据锚点 | 严重级 | 验证法 |
|---|---|---|---|---|
| A 深度 | 评分①：三维分段查表单调自洽（size 六算法档位:501-563、urgency 线性/钟形:565-592 全≥0 数学核验、liquidity 未知→中性 0.5:601-602）；权重和=1 校验（:417-422）；max 平局取列表序=确定性（:461-463） | algo_execution_selector.py:417-422,461-463,501-631 | 通过 | 逐档位边界手推 |
| A 深度 | **IS 口径②实锤：DefaultAlgoEvaluator 用 `abs(is_bps)`（:341）不区分方向——docstring:326-328 明文 BUY/SELL 两式（卖单 avg_fill<decision 为成本），实现绝对值化后卖单有利偏差（成交价高于决策价=价格改善）被计为正成本→efficiency 被罚、verdict 误判 poor**；注释:338 自认"不区分方向，方向由调用方在 outcome 构造时体现"但 ExecutionOutcome 无方向字段（:273-291）——调用方无处体现，效果评估回路（喂 P53 执行质量回写）系统性失真 | :326-328,338-345,273-291 | P2 | SELL outcome（decision=10, fill=10.05）评估得 is_bps=+50→poor（应为 -50 改善） |
| A 深度 | 简化③：fill_rate 二值化（filled>0→1.0 :343-345 Phase 1 注释声明诚实）——部分成交高成交率失真（10% 成交=满分成交率），与 IS 复合后效率分高估；声明在案但与 INVARIANTS"选最高分算法"的质量回路耦合 | :343-345 | P3 | 部分成交 outcome 观察 fill_rate=1.0 |
| B 上游 | checklist #6 断供：MarketContext 注入（ADV≤0 raise :165-169）；spread 缺失→-1→中性 0.5（保守中性正确）；**ADV 单位契约（股数）隐式**——adv_frac=quantity/adv（:170）若上游给成交额则量纲错 10 倍级（X04 引擎域契约，接线对账项） | :157-184 | P3 | 对照 X04 MarketContext.adv 语义 |
| C 下游 | **孤儿裁定：零生产调用方**（MOD-XS-005 引擎消费 AlgoSelection 未接线、OMS 算法推荐入口未建）；爆炸半径=算法选择缺位时 X04 六算法无自动选型（人工指定）；`_selections` 内存审计列表无上限裁剪（常驻进程缓慢泄漏，clear 手动） | :407,474,654-666 | P1(接线期)+P3(泄漏) | `grep -rn "AlgoExecutionSelector(" src/ scripts/ --include=*.py` |
| D 旁系 | checklist #4 双承载：与 P53 execution_quality_scorer（TDM-E-L4-14 执行成本反馈回写）职责相邻——本件 evaluator 是 Phase 1 简版，P53 若已实现完整 IS 则**两处执行质量评估并存**（P53 未在本批，接线对账项）；评分权重 0.40/0.35/0.25 与 §2.2 XS-11 文档双承载（常量+文档一致已核）；与 X06 拆单器（X04 引擎内 TWAP/VWAP 切片）分层清晰（选择→拆分→定价 P48——**三层链当前全部零接线**） | :388-391 | P3 | 对照 P48/P53 报告 |
| E 对抗 | 五问：①静默失败=无（错误码族完整）②假阳性=SELL 改善误判 poor（上述 P2）+ liquidity 未知恒中性使价差维度退化（信息缺省不惩罚）③断供=注册表空 NoAlgoAvailableError 显式④重触发幂等（除审计追加）⑤时序=now 可注入测试友好；urgency 缺省 0.5 由调用方拍（缺数据=中等紧急，对 TWAP/ALT 影响中性偏可） | :449-456 | P2(同②) | — |
| F 新鲜度 | TWAP/VWAP/IS/POV/冰山为执行算法标准谱系（Almgren-Chriss IS 框架正源；BestEx 2024 实务 72% 交易者用 VWAP 降 IS）；评分驱动选型（vs 规则 if-else）与业界 SOR/自适应选型方向一致；RL 选型（:43 Phase 2 声明）为学界前沿正确留白=**对等已有（Phase 1 简化声明诚实）** | https://www.quantitativebrokers.com/blog/a-brief-history-of-implementation-shortfall ；https://www.bestexresearch.com/insights/is-zero-reinventing-vwap-algorithms-to-minimize-implementation-shortfall | 通过 | WebSearch 2026-09-18 |

## 3 SOTA 对照

- 对等已有：六算法族+IS 效果评估为 Almgren-Chriss 谱系标准实践；评分驱动选型为 Phase 1 合理简化。
- 立卡候选：方向感知 IS（BUY/SELL 分式）+完整 fill_rate（订单总量入参）——评估回路接 P53 前必修，否则回写信号毒化选型迭代。

## 4 缺陷清单

1. P2：**IS 绝对值口径把卖单有利偏差计为成本（docstring 方向式 vs 实现矛盾，ExecutionOutcome 无方向字段可体现）**——建议 outcome 加 side 字段并按 docstring 两式计算；验证法=§2 A 轴 SELL outcome 构造。
2. P1（接线期）：零生产调用方孤儿+[MATURITY] 虚标（依赖边两端互认未接线）；验证法=§2 C 轴 grep。
3. P3：fill_rate 二值化失真（声明在案）；审计列表无界增长；ADV 单位契约未文档化。

## 5 挂起疑问

- 与 P53 execution_quality_scorer 的评估职责切分（本件 Phase 1 简版 vs P53 完整版）——建议收口时裁定唯一真源（倾向 P53 为真源、本件 evaluator 降级为内部 quick-check 或删除）。

## 6 完备性自评

六轴全查（F 带 URL）。长尾：①评分查表阈值（0.1%/1%/5% ADV 档）无实证标定记录②43 测试未覆盖 SELL 方向 evaluator case（IS 口径缺陷零覆盖=测试盲区与缺陷互证）③六算法评分表之间的相对序合理性无组合校验测试。

## 7 收口裁定（收口方填）
