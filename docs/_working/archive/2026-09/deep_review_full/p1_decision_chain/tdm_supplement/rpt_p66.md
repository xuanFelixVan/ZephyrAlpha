---
ttl: task_bound
title: 深度审查作业簿——减仓与再平衡
owner: st-deeprev-20260918
created: 2026-09-18
---

# 深度审查报告：减仓与再平衡（P66）

- 状态: **已审**
- 级别: P1｜类型: stage
- 基线 commit: 2fa92002c3（已核：本对象文件在基线/HEAD/工作区零漂移）
- 审查者: GLM-5.3-Flash / st-deeprev-20260918
- 入口锚点: `src/zephyr/position/core/rebalance_engine.py:151`（RebalanceEngine.evaluate:208）
- TDM 节点: TDM-P-P2-04（stage，config/trading_decision_map.yaml:2896，ai_autonomy: paper）
- 生产调用方: **零**——RebalanceEngine( 全仓仅自身 docstring（:155）；header 声明的 D-EX-CORE/D-PF-CORE/D-GOVERNANCE 零实际调用；与 P62 漂移监控声明的 DEVIATION 事件链（消费 DriftDetectedEvent）两端都未在网
- 测试文件: tests/position/test_rebalance_engine.py（63 passed 同批，与 P67/P68 合跑 1.20s）

## 1 对象快照

- 范围：RebalanceEngine 全文件（405 行）——三级触发（CALENDAR/DEVIATION/EVENT）→调仓指令生成（target−actual）→成本收益判定（成本>改善跳过/改善比<2 跳过/CALENDAR 例外）→压力态成本系数 1.5→E-POS-03 事件。
- 排除项：置换减仓路（TDM 声明与 MOD-SELL-006 replacement_rebalance_seller 共享触发，归 sell_decision 域）；风控减仓>做T 优先级（D44，图面语义）；D55 隔夜资格门（TDM 自记欠账）。
- 测试覆盖概况：三级触发/成本判定/指令方向覆盖良好；**无 actual 独有持仓场景、无改善量纲场景审查**。
- 材料包缺项声明：运行时证据包未取；数据画像不适用。

## 2 六轴审查日志表

| 轴 | 发现 | 证据锚点 | 严重级 | 验证法 |
|---|---|---|---|---|
| A | **改善量纲与成本量纲不可通约（数学口径缺陷）**：expected_improvement=Σdrift²（权重² 量纲，自注"以漂移幅度近似"），transaction_cost=turnover×cost_rate（权重×费率 量纲）——两者直接比值的阈值 2.0 无标定常数支撑，"改善>2×成本才动"（TDM 口径，改善应为收益单位）在本实现中是**不同量纲之比**；漂移 3% 时 improvement≈0.0009 vs cost（20% 换手×0.1%）=0.0002，比值 3 纯属巧合量级——阈值 2.0 的经济含义未兑现。INVARIANTS"交易成本>预期收益改善时MUST跳过"在这一代理上执行=形似神非 | rebalance_engine.py:244-254,366-390（docstring 自认近似）；:31-34（设计声明） | P2 | 构造同漂移不同换手两组合对比 ratio，验证阈值 2.0 无稳定经济含义 |
| A | **改善代理双路径不同标尺**：drift_event 路径只累加超阈告警的 drift²（:377-383），fallback 路径累加全部标的 drift²（:385-390）——同一组合走两路得不同改善值（亚阈漂移计不计入），判定结果可随调用方式翻转 | rebalance_engine.py:377-390 | P3 | 同权重两路调用对比 expected_improvement |
| C | **actual 独有持仓无 SELL 指令（与 P62 同族盲区，此处后果更重）**：_compute_orders 只遍历 target（:342）——从目标清单移除但仍持有的仓不会生成卖出指令，"减多少=回到目标权重"对退清单仓永不成立，残余敞口静默长存；配合 P62 的 KEPT 无告警，退清单仓在整条 P1-05→P2-04 链上双向隐身 | rebalance_engine.py:339-358 | P2 | actual={A:0.1, KEPT:0.1} target={A:0.1} 跑 evaluate 看 orders 无 KEPT |
| A | CALENDAR"强制"只绕过改善比门不绕过成本门：分支 1（成本>改善→SKIP）对 CALENDAR 同样生效（:259-264），仅分支 2 有日历例外（:266-273）——"周频强制触发（仍走成本判定）"的声明与实现勉强一致但"强制"名不副实，日历触发在微漂移时同样被静默跳过 | rebalance_engine.py:259-278 | P3 | CALENDAR 触发+微漂移输入看 should_rebalance=False |
| A | _post_rebalance_deviation 恒返 0（:392-398，自注"此处返回 0"）——"再平衡后偏差约束校验"是恒过 stub，:290 的 warning 不可达；假安全检查（checklist #3 同族轻症，代码已自认） | rebalance_engine.py:286-294,392-398 | P3 | 读代码序确认 warning 不可达 |
| B | 成本模型单参数 cost_rate（0.1% 默认，自注含佣金+滑点+冲击）vs TDM CST-ASTOCK-001 结构化费率（佣金+印花税卖出单边+过户费）——A 股卖出印花税单边使买卖成本不对称，本模型对称单边率近似；压力态 ×1.5 无校准锚 | rebalance_engine.py:166-170,360-364 | P3 | 对照 CST-ASTOCK-001 参数复算典型减仓成本 |
| A(亮点) | 指令方向语义正确（超配 SELL/低配 BUY，delta 有符号）；Σ|Δ|=turnover 定义清晰；1e-9 平加过滤；验证完备（越界/target⊆actual）；监听隔离 | rebalance_engine.py:338-358,328-336,400-405 | — | — |

## 3 SOTA 对照

- 成本收益门（改善>2×成本才再平衡）：**对等已有**——阈值/带式再平衡的成本意识是标准实践（Princeton Asset Drift-or-Rebalance 回测指南 princetonasset.com，2026-06：阈值法省成本；Guardfolio 5/25 法则 guardfolio.ai，2026，同 P62 引）；但业界改善度量用**预期收益差或跟踪误差改善**（收益量纲），非 drift² 代理——本模块代理属偷懒近似（本报告轴 A 主发现）。
- 日历+偏离双触发：**对等已有**——calendar/threshold 混合再平衡是机构常规（Russell Investments ideal rebalancing range，russellinvestments.com，2026）；"日历触发仍受成本门"本项目实现与业界"calendar 通常无条件"略有差异（本报告 P3 已记）。
- 压力态收紧交易（成本系数 ×1.5）：**立卡候选**——压力期放大成本估计是合理保守方向，业界更常用"压力期暂停非必要再平衡"；×1.5 数值无校准源（TDM/蓝图均无锚，checklist #15 问句命中：关键数字无底层产物锚）。

## 4 缺陷清单

1. **[P2] 改善/成本量纲不可通约，阈值 2.0 无经济含义**。建议修法：improvement 改为收益量纲估计（如跟踪误差改善×目标权重，或漂移×预期回归半衰期收益），或显式引入标定常数并回测定标。验证法：§2 轴 A 对比探针。
2. **[P2] 退清单仓无 SELL 指令**。建议修法：遍历 target∪actual，actual-only 视 target=0 生成清仓 SELL。验证法：KEPT 探针。
3. **[P2] 孤儿死码**（DEVIATION 事件链上游 P62 也未在网，双端孤儿）。建议修法：接线批次与 P62/P1-06 统一排期；接线前降 draft。验证法：grep。
4. **[P3] CALENDAR 强制语义不完整+后偏差校验 stub+压力系数无锚+成本模型对称近似**。建议修法：日历例外提至分支 1 之前或改注释；stub 补实现或删校验；压力系数补锚或降格经验值；成本模型对接 CST-ASTOCK-001。验证法：各自探针。

## 5 挂起疑问

- 置换减仓路（1.5× 预期收益差换仓）的承载件 MOD-SELL-006 与本模块的触发共享方式（事件互喂 vs 参数直传）未审（sell_decision 域对象）——两件并存的边界需在接线时防双触发。
- 风控减仓>做T>新开的冲突仲裁（D44）无代码承载——归 P2-04 编排面还是 X-S2-01 输入仲裁（R2-05 已声明四路优先级）请 Owner 指定唯一落点。

## 6 完备性自评

六轴全查（A 数学四问：delta/turnover/改善代理逐个过、量纲不可通约已立、边界=零漂移/负值/平加已测；B 上游=drift_event 契约+cost_rate 注入已查；C 下游=零调用方判孤儿+KEPT 盲区已立；D=与 TDM 两路触发对账（置换路在别处）+与 P62 双端链核查；E 五问：静默失败=日历静默跳过、假阳性=stub 校验、断供=不适用、重复触发=evaluate 幂等、时序=clock 注入）。长尾：①MOD-SELL-006 置换件未审；②D55 隔夜资格门欠账（TDM 已记）未施工无从审；③63 测试逐断言抽查级。

## 7 收口裁定（收口方填）
- 三态逐条: 
- 修复 commit: 
- 复检结论: 
