---
ttl: task_bound
doc_type: report
title: 深度审查作业簿——budget变动三级升级
owner: st-deeprev-20260918
created: 2026-09-18
---

# 深度审查报告：budget 变动三级升级（P56）

- 状态: **已审**
- 级别: P1｜类型: stage
- 基线 commit: 2fa92002c3（已核：本对象文件在基线/HEAD/工作区零漂移）
- 审查者: GLM-5.3-Flash / st-deeprev-20260918
- 入口锚点: `src/zephyr/position/core/budget_change_handler.py:320`（BudgetChangeHandler；主入口 handle_budget_change:373）
- TDM 节点: TDM-F-C2-04（stage，config/trading_decision_map.yaml:3850）
- 生产调用方: `pf_alloc/allocation_orchestrator.py:813,833`（BudgetChangeHandler(persist_path)→sync_from_allocator）——但 allocation_orchestrator 自身零生产实例化（pf_alloc 链孤儿，checklist 案例 d9c5f4bb12 在案）→ **继承性不可达**（接线适配器已就绪、编排层未接）
- 测试文件: tests/position/test_budget_change_handler.py（694 行，与 P54/P55 同批 151 passed 7.00s）

## 1 对象快照

- 范围：BudgetChangeHandler 全文件（1020 行）——防抖（日内<5% 忽略/累计>10% 强触）→三级升级（Tier1 冻结+Tier2 自主 rebalance 同发、Tier3 超时/违例强裁）+收敛检测（5% 容差×1 日持续性）+re-target 豁免+E-POS-40/41 进程内事件+JSON 快照持久化（schema 版本+原子写+fail-closed 恢复）+on_firm_violation 直触 Tier3。
- 排除项：RegimeMetaAllocator budget 计算（pf_alloc 域）；ForcedTrim 执行侧 retain_ratio 消费（执行层域）。
- 测试覆盖概况：694 行覆盖三级流转/防抖/re-target/持久化恢复/事件隔离；**多日连续小幅下调的"日间累计"场景无测试**（恰为本次实证缺陷）。
- 材料包缺项声明：运行时证据包未取（无生产运行痕迹）；数据画像不适用。

## 2 六轴审查日志表

| 轴 | 发现 | 证据锚点 | 严重级 | 验证法 |
|---|---|---|---|---|
| A | **"日间累计趋势>10% 强触发"机制失效（实证）**：cumulative_budget_change 在每个新交易日**重置为 0**（:429-433）再累加——"累计"实际只在单日内有效。实测连续 3 日各 -4%（三日累计 -11.5%>10% 阈值）三天全部 DEBOUNCE 忽略，永不触发升级。与模块自身 docstring「日间累计趋势>10% 强制触发」（:43）、常量注释「连降累计>10% 必须执行（日间趋势）」（:80）、TDM「连降>10% 强触」三方矛盾。后果：阴跌式预算收缩被无限期静默吞掉，策略维持超配 budget——fail-open 方向的错误 | budget_change_handler.py:429-433,79-80,43；探针实测三日连降全 DEBOUNCE | P2（接线后=P1） | 本报告探针复跑（0.30→0.288→0.2765→0.2654 三日 -4%）；或读 ：429 重置逻辑 |
| D | **TDM 三级语义 vs 代码三级语义不同轴**：TDM-F-C2-04=「Tier1 降<10% 封锁；Tier2 降 10-25% 差异化窗口；Tier3 降>25% 按比例强裁」——**按跌幅分档**。代码=任何 ≥5%（或累计≥10%）下调立即同发 Tier1+Tier2，Tier3 仅收敛窗口超时/违例触发——**按时间升级**。跌幅分档阈值（10%/25%）在代码零承载：代码里 -6% 即触发 Tier1+Tier2（TDM 口径应只 Tier1），-30% 也要等窗口超时才强裁（TDM 口径应即 Tier3）。两套口径各自自洽但互斥，TDM 把代码语义误写成分档语义 | config/trading_decision_map.yaml:3854-3858 vs budget_change_handler.py:32-35,445-454,833-889 | P2 | 读两处文本对照；构造 -6% 与 -30% 两次调用看指令差异 |
| C | 继承性孤儿：sync_from_allocator 接线适配器已就绪且质量好（duck-typing 依赖倒置+下线策略不误强裁的 fail-closed+快照记忆），但唯一调用链 allocation_orchestrator 自身零生产实例化——TDM 注释已如实声明「BudgetChanged 事件链未接线（33 号复核注记，随装配排期）」（诚实度高于 P54/P55 同链对象） | budget_change_handler.py:590-651；pf_alloc/allocation_orchestrator.py:813,833；config/trading_decision_map.yaml:3863 | P2 | `grep -rn "AllocationOrchestrator(" src/ scripts/ --include=*.py` 零生产 |
| A | check_convergence 的"持续性 ε_days 日"按**调用次数**计数不按日历日：无日期守卫（对照 handle_budget_change 有 current_date 防抖重置）——调用方一天调两次即 2/1 日"达标"，提前 CONVERGED；调用节奏契约未文档化 | budget_change_handler.py:461-526 | P3 | 同日两次 check_convergence(exposure=收敛值) 看直接 CONVERGED |
| A | on_firm_violation 从 IDLE 直触 Tier3 时，E-POS-41 事件的 from_tier 硬编码 TIER_2（:981）——审计轨迹失真（实际 IDLE→TIER_3 记成 TIER_2→TIER_3） | budget_change_handler.py:703-708,981 | P3 | 无活跃状态直接 on_firm_violation 后查事件 payload.from_tier |
| B | budget 输入无数值校验：负 budget/old=0 边界未拒（change_pct=0 分支静默）；snapshot 恢复的 last_effective_budgets 与调用方显式 previous_budgets 冲突时显式参优先（已文档化）——正向契约清楚，负向边界松 | budget_change_handler.py:422,642-649 | P3 | handle_budget_change('s',0,-0.1) 看行为 |
| E | 持久化面：原子写（tmp+os.replace）+schema 版本不符 fail-closed+PermissionError 清理——质量好；残余面=同 persist_path 多实例并发写为 last-writer-wins（快照启动时读一次，运行中他进程更新不可见） | budget_change_handler.py:776-831 | P3 | 两实例同 path 交替写后重启看状态以最后写者为准 |
| A(亮点) | PFA-1 车道 D 治理已落：ForcedTrim trim_ratio/retain_ratio 双字段+口径注释（削掉比例 vs 执行乘子）消解历史矛盾（:172-197）；事件订阅者异常隔离（:726-732）；re-target 收敛中上调即停强裁（:900-916） | budget_change_handler.py:172-197,726-732,900-916 | — | — |

## 3 SOTA 对照

- 三级升级（尊重自主→超时强裁）：**对等已有**——multi-strategy 平台风险预算收缩的"先通知 PM 自主降、限时未达标中央强裁"是标准治理（Mercer Multi-Manager Platforms due diligence 框架，mercer.com，2025-2026；The Hedge Fund Journal pod shop 治理记载，2025）；本模块时间升级制与该范式同构。
- 跌幅分档软去杠杆（TDM 口径）：**对等已有**——机构软去杠杆阶梯（TDM 已引 breakingalpha：DD 10-12%→80% 仓/12-15%→60%/15-18%→40%）；2025 年 3 月与 7 月对冲基金去风险潮为实证背景（Goldman Sachs prime brokerage 数据经 Reuters/Investing.com 报道，2025-03；JPMorgan 强制去杠杆评论经 AInvest，2025）。**TDM 的分档口径有业界依据、代码的时间升级制也有依据——但两者必须二选一写清楚**（本报告轴 D 发现）。
- 防抖 5% 阈值：**驳回（外部记忆断言不核）**——docstring 引"theledgermind 2026-05 实证 5% 为 return/cost trade-off 最优点"无底层产物锚（checklist #15 问句命中：关键数字无底层产物锚）；建议补锚或降格为经验参数声明。

## 4 缺陷清单

1. **[P2] 日间累计防抖失效（三日 -4% 连降全吞）**——代码 vs 自身 docstring vs TDM 三方矛盾，fail-open 方向。建议修法：累计不按日重置（或另设 N 日滚动窗累计变量），重置仅发生在升级触发或 budget 回升后；补多日连降回归测试。验证法：本报告三日探针。
2. **[P2] TDM 分档语义（10%/25% 跌幅档）与代码时间升级制互斥**。建议修法：Owner 裁定口径——保留时间升级制则改写 TDM algo_note；保留分档制则代码补跌幅分档映射（改动大）。裁定前 TDM 节点应注记两套口径不可混读。验证法：§2 轴 D 对照法。
3. **[P2] 继承性孤儿（接线适配器就绪、编排未接）**。建议修法：随 G15→G14 编排件立项接线（TDM 已挂装配排期），接线前本节点维持"已建未接"声明。验证法：grep AllocationOrchestrator 生产实例化。
4. **[P3] check_convergence 持续性按调用计数**。建议修法：加 last_check_date 日历日守卫。验证法：同日两调探针。
5. **[P3] E-POS-41 from_tier 硬编码失真+负 budget 边界松+theledgermind 5% 引证无锚**。建议修法：from_tier 记录真实前态；budget 校验；引证补锚或降格。验证法：各自探针/查证。

## 5 挂起疑问

- 三级语义裁定（时间升级 vs 跌幅分档）请 Owner 终裁——本报告倾向保留代码现状（时间升级制与 30 号 §2.4 原文一致且实现成熟），改 TDM 文本；但 -30% 级急跌是否需要跳过窗口直触 Tier3（现只能靠 on_firm_violation 旁路）值得在接线设计时回答。
- 防抖累计失效修复后，"日内多次小幅+跨日累计"的组合触发边界（何时重置）需与 RegimeMetaAllocator 的分配周期对齐后定稿。

## 6 完备性自评

六轴全查（A 数学四问：change_pct/trim_ratio=1-retain/收敛容差公式全过、边界 target=0 与 exposure=0 已读；B 上游=sync_from_allocator 输入校验逐分支查；C 下游=调用链追到 allocation_orchestrator 判继承孤儿；D=与 TDM 口径逐条对账+与 StrategyBook/RegimeMetaAllocator 分工在 header 声明；E 五问：静默失败=日间累计吞降级（已立）、假阳性=持续性计数、断供=快照损坏 fail-closed（已防）、重复触发=re-target 幂等、时序=now 可注入（部分方法））。长尾：①StrategyBook 侧 rebalance_to_budget 契约履行（"策略不能说我不卖"的执行面）归 MOD-POS-020 对象；②事件消费方（Trader/归因）未接线故 E-POS-40/41 实际零订阅；③694 行测试逐断言复核为抽查级。

## 7 收口裁定（收口方填）
- 三态逐条: 
- 修复 commit: 
- 复检结论: 
