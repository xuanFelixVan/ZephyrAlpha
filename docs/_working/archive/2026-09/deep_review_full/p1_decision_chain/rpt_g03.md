---
ttl: task_bound
title: 深度审查报告——G03 负面事实否决闸（negative_veto）
owner: st-deeprev-20260918
reviewer_model: GLM-5.3-Flash
baseline_commit: 2fa92002c3
created: 2026-09-18
---

# 深度审查报告：G03 负面事实否决闸（GLM-5.3-Flash / 基线 2fa92002c3）

- 状态: **已审**
- 级别: P1（作业簿标 P0"否决失效=踩雷股放行"；本审查判定实际接线态下为筛选层 fail-open 设计，定级讨论见 §4-1）｜类型: 闸门（纯函数核）
- 审查者: GLM-5.3-Flash / st-deeprev-20260918
- 入口锚点: `src/zephyr/signal_fundamental/negative_veto.py:42(Error)(:98 apply_negative_veto)`
- 生产调用方: **apply_negative_veto 直接调用方=0**；已对接的下游=candidate_pool_aggregator.py 的"零 import 鸭型镜像"消费 NegativeVetoVerdict 姿态（:187 姿态转换）；fundamentals.py:241 应计剔除器标注"生产接线待 SOP-C C5 解冻"
- 测试文件: tests/signal_fundamental/test_negative_veto.py（存在）
- 变更热力: 2026 年 2 commits（低热）
- 材料包缺项: 运行时证据包缺（纯函数件+未接线）

## 1 对象快照

六项负面清单+黑名单+高应计的一票否决纯函数：None=证据不足不否决（筛选层 fail-open，与下单闸 fail-closed 方向相反——docstring :26-27 显式声明）；全量披露命中原因不短路；frozen 同输入同输出。排除项：risk_veto_engine（订单级硬否决，语义正交已查重）、candidate_pool_aggregator 本体。

## 2 六轴审查日志表

| 轴 | 发现 | 证据锚点 | 严重级 | 验证法 |
|---|---|---|---|---|
| A | 数学/边界四问全过：None 不否决 ✓（:107-111 只认 v is True）；unlock_ratio NaN 检查（v!=v）✓、[0,1] 越界 NegativeVetoError ✓（:72-76）；阈值严格 >（=阈值不否决）与"解禁>5%"口径一致 ✓；config (0,1] 校验 ✓；全量披露 ✓；frozen 纯函数 ✓ | :87-113, 52-56, 72-76 | ✓ 查无 | 单测+构造边界输入 |
| C | **半孤儿（姿态对接、调用未接线）**：candidate_pool_aggregator 以零 import 鸭型镜像消费 verdict 姿态（vetoed 沉底留痕不占容量），但没有任何生产代码调 apply_negative_veto 产出该 verdict——"负面事实由调用方算好注入"（:4）的调用方尚不存在于生产 | negative_veto.py:4-5; candidate_pool_aggregator.py:10, 187; fundamentals.py:241 | P2（模式#8 已声明型） | grep `apply_negative_veto(` 生产命中=0（已做） |
| D | **header INVARIANTS 漂移**：:8 写"六项负面清单+黑名单"，代码 _REASON_KEYS 实为八项判定（六项+黑名单+高应计 high_accrual，裁定#231 追加 :70, :94）——invariant 行未随裁定#231 更新 | :8 vs :87-95 | P3 | 对读 |
| B | 数据语义口径依赖上游：unlock_ratio 定义"待解禁市值/流通盘"（:66）——若上游误传"占总股本"或百分比（5.0 而非 0.05）形态，>1 越界会 fail-closed 抛错 ✓ 安全方向，但"占总股本<流通盘比例"的偏低形态（0.03 vs 0.05 实义）无防御——隐含契约未文档化 | :66, 72-76 | P3 | 构造 0.03 实义解禁看不否决 |
| E | 一票否决失效面：本件 fail-open 设计（None/漏传=放行）——若上游事件源断供（负面字段全 None），否决闸整体空转无告警（模式#6"数据源静默死亡"的结构性暴露面）；且不否决无计数统计（对比 M01 有 stats） | :26-27, 98-113 | P2（接线前须补） | 全 None facts 批量跑，观察 vetoed 全 False 无告警 |
| D | 查重分工声明清晰（vs risk_veto_engine/strategy_cross_vote_funnel 三层正交）✓ | :29-32 | ✓ 查无 | 对读三件 header |

## 3 SOTA 对照

- 负面清单一票否决（业绩暴雷/立案/减持/解禁/商誉/配股）为中文卖方金工与固+"踩雷防范"研报常规框架——**受阻未搜**（检索预算已用于 WQ101/保形/TA-Lib；规则集为仓内策略库 STR-MULTIFACTOR-034~041 承载，对等对照=内部策略库真源）。
- 驳回：无外部替代建议（规则集本身是业务裁定产物，非算法问题）。

## 4 缺陷清单

1. **P2 半孤儿+失效面组合**：单件数学零缺陷，但"否决失效=踩雷股放行"的真实风险不在本件逻辑，在**接线态**：调用方不存在（直接调用=0）+上游断供静默空转（全 None 全放行）+无否决率统计。作业簿 P0 定级在本件当前态（未接线）不成立——无资金路径可达；**接线后**若上游数据完整性无保障，P0 定级成立。建议：接线批同步补 (a) 否决率/None 率监控计数（对接 M01 stats 模式），(b) 负面字段覆盖率告警（对接 399106 断供教训的模式#6 检查）。验证法：grep 调用方；全 None facts 批跑。
2. **P3** header invariant 八项漂移、unlock_ratio 口径隐含契约。

## 5 挂起疑问

- high_accrual 的上游（fundamentals.accrual_negative_screen，裁定#231）"待 SOP-C C5 解冻"的排期与 G03 接线是否同批——不同批则 high_accrual 恒 None，第八项否决长期空转（结构性，无告警可见）。

## 6 完备性自评

六轴全查（F 受阻记）。数学四问全过（纯函数件，边界逐一）。长尾：①黑名单数据源（Owner/风控维护 :69）的更新通道与 SLA 未审（上游件）；②reasons 中文标签是否需经三层翻译 loader（i18n 红线：本件为逻辑判定非生成器输出，判定不适用，留档）。

## 7 收口裁定（收口方填）
- 三态逐条:
- 修复 commit:
- 复检结论:
