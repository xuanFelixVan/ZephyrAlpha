---
ttl: task_bound
doc_type: report
title: 深度审查报告——持仓分诊（E05）
owner: st-deeprev-20260918
created: 2026-09-18
---

# 深度审查报告：持仓分诊（E05）

- 状态: **已审**
- 级别: P1｜类型: 卖出族分诊（#309 挂起族基础件）
- 基线 commit: 2fa92002c3（工作树 bf65648609；本文件自基线零变更，锚点双有效）
- 审查者: GLM-5.3-Flash / st-deeprev-20260918
- **裁定#309 约束声明**：卖出族整族挂起（ruling_registry.yaml:3833-3839）——审查照常，施工受裁定约束。
- 入口锚点: `src/zephyr/sell_decision/core/position_triage.py:166(triage)/:126(_triage_atr)/:72(StrategyType)`
- 接线现状（grep 实证）：包外零导入（`position.core.position_drift_monitor` 的 TriageLevel 枚举被本件复用为真源——反向依赖）；包内消费=take_profit/stop_loss 引 Snapshot/StrategyType；生产调用零。
- 测试文件: tests/sell_decision/test_position_triage.py
- 材料包缺项: 42 号 memo §3.2 spec 伪代码原文未取（等价性声明无法独立复核，见挂起 1）

## 1 对象快照

- 范围：triage 三档判定（WATCH<1.5×ATR / HOLD>3×ATR 盈利 / MONITOR 中间）+ threshold_delta 双向反馈（±0.10 封顶）+ ATR 缺失降级 MONITOR + StrategyType/SellPositionSnapshot 契约。
- 测试覆盖概况：专测在位。

## 2 六轴审查日志表

| 轴 | 发现 | 证据锚点 | 严重级 | 验证法 |
|---|---|---|---|---|
| A | **价格已跌破止损线的持仓判 MONITOR 而非 WATCH**：distance_abs=abs(current−stop)（:142）对称化——current<stop 时（止损击穿未执行/跳空穿越），abs 距离可>watch 阈→不 WATCH；profit_abs<0 也不 HOLD→落 MONITOR 中间档。最紧急状态被分诊为普通档 | position_triage.py:142-159 | **P2** | 构造 current=9/stop=10/entry=20 → MONITOR |
| A | WATCH 优先于 HOLD 的短路序正确实现"深度盈利**且远离**止损"复合条件（:152-157：先 WATCH 后 HOLD，近止损的深盈利持仓落 WATCH）——与 spec 复合语义等价 | position_triage.py:151-159 | 已查无（正面） | — |
| A | threshold_delta 语义实现正确：正 delta 缩 watch/hold 阈→更难 WATCH+更易 HOLD（放宽）；负值反向（收紧）；±0.10 硬封顶（:190）——契约兑现 | position_triage.py:144-149, :190 | 已查无（正面） | 数值手算对照 |
| A | **NaN threshold_delta 静默变 +0.10（最大放宽）**：输入校验只查价格/symbol（:111-123），delta 的 NaN 经 min/max 比较链（Python NaN 比较恒 False）得 0.1——反馈通道坏数据=最大放松方向 fail-open | position_triage.py:190 | P3 | triage(..., threshold_delta=float("nan")) 后内部 delta=0.1 |
| A | 等价性声明待证：docstring 称绝对量纲实现与 spec"距离%<1.5×ATR%"数学等价、"两边同乘 entry"（:132-136）——若 spec 分母是 current 价而非 entry，等价不成立（远离 entry 的持仓判定漂移）；spec 原文未取 | position_triage.py:132-136 | P3（挂起 1） | 取 42 号 memo §3.2 伪代码核对分母 |
| A | ATR 缺失降级 MONITOR（:192-196）：中间档保守选择有 spec 依据声明；debug 日志级别（同 E03 家族模式：资金相关状态切换低声） | position_triage.py:192-196 | P3 | — |
| B | 上游：stop_loss_price 来自 Chandelier（E03）——E03 降级锚缺陷会让本件判定锚整体漂移（上游错→本件无感知带病分诊，仅价>0 校验）；TriageLevel 枚举真源在 position 域（复用不复制，真源唯一声明兑现） | position_triage.py:46, :178 | P3 | 与 E03 缺陷 1 联动复演 |
| C | 下游：WATCH/MONITOR/HOLD 驱动"扫描频率与卖出决策权重"（头注）——实际生产无消费方（族级孤儿）；E03/E04 兄弟经 Snapshot 依赖本件数据契约 | grep 实证 | P1（族级，并入 E01） | 同族验证法 |
| D | StrategyType 四类（short_term/trend/mean_reversion/other）与 E03 降级%映射（4% only short_term）一致自洽；完整五类归 MOD-SELL-014（待 G04）——MVP 收窄有声明 | position_triage.py:72-82 | 已查无 | — |
| E | 重放/重入：@staticmethod 零状态；输入校验 fail-closed（raise）——除 NaN delta 外无静默吞点 | 全文 | 已查无 | — |
| E | A 股口径：ATR/价格均为量纲中性；停牌期间 current_price 陈旧→分诊基于旧价（调用方职责，本件无 as-of 校验）——接电前置项 | 设计边界 | P3 | — |

## 3 SOTA 对照

1. **持仓分诊分层监控（对等已有）**：按风险距离分级调度监控频率是组合风控常规（risk-tiered monitoring，SR 26-2 ongoing monitoring 分层口径，Federal Reserve，2026，https://www.federalreserve.gov/supervisionreg/srletters/SR2602.pdf）；ATR 归一化距离阈值属波动率自适应监控成法（同 E03 §3-1 ATR 实证源）。
2. **双向反馈 threshold 调整（立卡候选）**：BM-POS-09 式反馈调阈（正反馈放宽/负反馈收紧+硬封顶）在业界少有同名机制，属项目自研自适应；封顶 ±0.10 是必要的稳定性护栏——保留自研，登记接电后做回撤期参数冻结评估（反馈在趋势反转时可能正反馈放大风险）。
3. 结论：主体**对等已有**；反馈机制自研有护栏。

## 4 缺陷清单

1. **[P2] 止损击穿态（current<stop）分诊为 MONITOR**——证据 ：142-159；影响：接电后最紧急持仓吃中间档扫描频率（漏监控向偏移，方向与"距离止损近→WATCH"本意相反）；建议：distance 改符号判定或显式 `current<=stop → WATCH`（乃至新档 BREACH）；验证法：§2 A 首行构造。
2. **[P3] NaN delta→+0.10 最大放宽**（:190）——建议：math.isfinite 校验 raise；验证法：NaN 构造。
3. **[P3] 等价性声明的 spec 分母未核**（:132-136）——验证法：取 memo §3.2 对照。
4. **[P3] 降级日志 debug 级**（:195）——同 E03 家族模式。
5. **[P1-族级] 结构性孤儿**——并入 E01。

## 5 挂起疑问

1. spec §3.2 的距离分母（entry or current）——决定等价性声明真伪，需取 42 号 memo 原文。
2. 停牌/涨跌停期间 current_price 冻结时的分诊语义（旧价 WATCH 是否该升级为人工复核）——接电设计项。

## 6 完备性自评

- 六轴全查：是（全量逐行）。长尾：①position_drift_monitor 的 TriageLevel 消费端（position 域对象）；②42 号 memo 全文；③BM-POS-09 契约原始定义。

## 7 收口裁定（收口方填）
- 三态逐条:
- 修复 commit:
- 复检结论:
