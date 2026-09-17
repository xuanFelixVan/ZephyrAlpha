---
ttl: task_bound
title: 深度审查报告——持仓对账器(ex_core/position 双实现)（R02）
owner: st-deeprev-20260918
created: 2026-09-18
reviewer: GLM-5.3-Flash/st-deeprev-20260918
baseline_commit: 2fa92002c3
---

# 深度审查报告：持仓对账器（R02）

- 状态: **已审**
- 级别: P0｜类型: 算法+旁系合并案
- 基线 commit: 2fa92002c3
- 审查者: GLM-5.3-Flash / st-deeprev-20260918
- 入口锚点: `src/zephyr/ex_core/position_reconciler.py:101`；**D 轴显式项**: `src/zephyr/position/position_reconciler.py:41`
- 生产调用方（ex_core 版）: risk_layer_orchestrator.py:466 / eod_reconciliation.py:47,126 / recon_runner.py:78,433 / scripts/start_paper_session.py:457
- 测试文件: tests/ex_core/test_position_reconciler.py（399 行）；position 版: tests/rollback/test_rollback_position_reconciler.py + tests/e/test_e_position_reconciler.py

## 1 对象快照

- **范围**：两个同名 PositionReconciler 全文。ex_core 版（MOD-EX-056，218 行，盘中持仓对账+冻结）与 position 版（MOD-INF-022，99 行，自称事件驱动对账+升级判定）。口径一致性与合并建议为本簿主轴。
- **排除项**：recon_runner/eod 的调用侧语义分别在 R04/R03 簿；PositionTracker 成本口径归 R05 簿（对账只比数量不比成本，无影响）。
- **测试覆盖概况**：ex_core 版 399 行测试覆盖冻结/解冻/容差/on_drift 吞异常/并发 is_frozen；position 版两套测试合计约 234 行覆盖 reconcile/handle_execution_report/should_escalate。全部运行通过（2026-09-18 实录，四文件合计 67 passed）。
- **材料包缺项声明**：同 R01（无运行时日志证据包）；数据画像未做（holdings 表画像属 TDM 域）。

## 2 六轴审查日志表

| 轴 | 发现 | 证据锚点 | 严重级 | 验证法 |
|---|---|---|---|---|
| A | ex_core 版数学正确：Decimal-only、diff=sys−broker、`abs(diff)>tolerance(默认0)` 冻结、冻结集全量重算非累加、纯读不改源 | ex_core/position_reconciler.py:143-171 + 头部 INVARIANTS:8 | （正面） | 跑 tests/ex_core/test_position_reconciler.py |
| A | position 版无类型约束：裸 dict + `i != e` 比较，float 持仓可产生假差异；与 ex_core Decimal 口径不一致 | position/position_reconciler.py:57-63 | P2 | 传 {s:0.1+0.2} vs {s:0.3} 观察假 diff |
| A | position 版 should_escalate 按**笔数**≥3 升级 P0-FATAL——单标的巨量差异（count=1）不升级，口径可疑 | position/position_reconciler.py:97-99 | P2 | reconcile 1 个标的 diff=10 万股，断言 should_escalate(1)=False |
| A.3 | 两套测试各自全绿但各测各的实现——双份承载漂移在测试层同样成立（无跨实现一致性测试） | 两测试目录 | P3 | 无（结构性缺位） |
| B | ex_core 版输入契约=PositionSnapshot.holdings dict[str,Decimal]（CTR-006）明确；position 版无契约文档 | ex_core:53-60 vs position:47 | P3 | 读两文件头 |
| C | **position 版生产调用方=0**（全仓 grep 仅 tests/rollback + tests/e 两处 import）→ 孤儿死码（checklist #8）；其头部 [CONSUMERS] 字段为空自证 | position/position_reconciler.py:5 + grep `from zephyr.position.position_reconciler import` | **P1** | `grep -rn "zephyr.position.position_reconciler" src/ scripts/` 零命中 |
| C | ex_core 版爆炸半径：冻结→trading_session 下单硬拦（fail-closed 正确路径）；reconcile 抛错→R01 tick 吞（见 R01 簿） | trading_session.py:778 | （正面/关联） | — |
| D | **双承载口径漂移（checklist #4）**：同名同职责两实现，语义相反——ex_core=Decimal+冻结+定时调度；position=裸 dict+无冻结+自称"事件触发（禁止时间触发）"。**两处对账口径不一致** | ex_core:101-218 vs position:41-99 + position 头 INVARIANTS:8 | **P1** | 并排读两文件 reconcile 段 |
| D | position 版 INVARIANTS 宣称"P0-FATAL 必须触发硬中断"，实现只返回 dict 无任何执行方——文档承诺与代码漂移 | position/position_reconciler.py:8 vs 80-95 | P2 | grep 全仓无消费其 rule_id(POS-RECON-001) 的中断执行器 |
| E | reconcile 幂等（纯读+冻结重算）；重放安全 | ex_core:8,169-171 | （正面） | 重复调用结果一致 |
| E | 时窗内新成交：双源两次 get_positions 非原子（151-152），中间落地成交=瞬时假 drift→冻结+告警噪音；下一轮自动解冻 | ex_core/position_reconciler.py:151-170 | P2 | mock 两源之间注入成交，观察假冻结 |
| E | 自动解冻依赖"下一轮对账发生"：对账环停止时冻结永不解除且无提醒（与 R01 静默死亡耦合） | ex_core:166-171 + risk_layer_orchestrator.py:1791-1798 | P2 | stop 循环后冻结标的持续 is_frozen=True |

## 3 SOTA 对照

- 业界对账形态（Juspay《Payment Reconciliation Across Multiple PSPs》，juspay.io/blog，2025；Oceanobe《Event-Driven Reconciliation》，oceanobe.com，年份未标注/检索 2026-09-18）=「实时事件检测 + 周期全量兜底」混合制。本对象：ex_core 版=周期全量（兜底腿，可用）；position 版自封"事件触发"（实时腿）却零接线。**结论：两腿各自半成品且互不相认**。合并案（ex_core 唯一真源承载兜底腿 + 事件触发腿按裁定#317 挂 orchestrator + position 版退役）与 SOTA 混合制对齐。

## 4 缺陷清单

1. **P1 双实现孤儿+口径漂移（合并建议主案）**
   现状→`zephyr.position.position_reconciler.PositionReconciler` 零生产调用方；与 ex_core 版同名同职责但口径不一致（Decimal 冻结制 vs 裸 dict 计数升级制）。
   证据→grep 实录（仅 2 测试文件 import）；ex_core/position_reconciler.py:101 vs position/position_reconciler.py:41。
   影响与爆炸半径→未来任何一方接线都可能接错版本（同名类 import 混淆）；position 版测试绿=假完成状态，维护成本持续；"P0-FATAL 硬中断"承诺悬空。
   建议修法→三步：①确认 position 版退役（注册表净删=high 门位走 Owner，MOD-INF-022）；②若需保留升级语义，并入 ex_core 版作告警策略字段；③两个测试文件改指向 ex_core 版或随删退役。
   验证法→`grep -rn "position_reconciler" src/ --include="*.py"` 收敛为单实现；蓝图表 MOD-INF-022 状态更新。
2. **P2 position 版升级阈值口径错误（若保留须修）**
   现状→`should_escalate(diff_count, threshold=3)` 按差异标的**笔数**判定硬中断（97-99），单标的重大差异不触发。
   证据→锚点如上。
   影响与爆炸半径→若按其头部承诺接线，单标的全仓错账（对账最危险形态）反而静默。
   建议修法→升级判据改「任一标的 abs(diff)>幅度阈值 OR 笔数阈值」双条件取或。
   验证法→单标的 10 万股 diff 断言升级=True。
3. **P2 双源非原子快照假漂移**
   现状→system 与 broker 两次独立快照（151-152），间隙成交=假 drift 冻结+on_drift 噪音；且未计入在途挂单。
   证据→ex_core/position_reconciler.py:143-170；open_orders_provider 未接入（R01 簿缺陷4 同源）。
   影响与爆炸半径→高频窗口冻结抖动+告警疲劳——对账的意义在抓真差异，系统性假阳性=狼来了（任务书点名的"差异容忍"高危区反例：本件反向问题是假阳性过高）。
   建议修法→broker 侧单快照透传（reconcile 入参接受快照而非再查）+在途量调整。
   验证法→并发成交 mock 下统计假冻结率。
4. **P3 冻结集生命周期与对账环耦合**
   现状→解冻仅发生于下一轮 reconcile；环停→冻结滞留无提醒。
   证据→ex_core:166-171 + R01 缺陷1。
   建议修法→随 R01 staleness 暴露一并给 frozen_symbols 加冻结时刻。
   验证法→stop 后断言有滞留告警。

## 5 挂起疑问

- position 版（MOD-INF-022）当初立项的 rollback 场景消费方是否从未施工？蓝图表 `docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md` 未逐一核对（若其中另有接线约定，退役前须核）。
- QMT `pos.stock_code` 格式隐式契约（同 R01 疑问②）：格式漂移=全标的假冻结，建议实单 smoke 后把格式归一化断言写进 broker 适配层。

## 6 完备性自评

- 六轴全查：A/B/C/D/E/F 均有结论。核心问题=轴 D 双承载（checklist #4/#8 双命中），已给合并案与 SOTA 对照。
- 长尾清单：①ex_core 版并发测试无量级压力；②position 版 tests/e 61 行覆盖极薄（若退役则无所谓）；③holdings 数据画像（缺失率/极端值）未做。

## 7 收口裁定（收口方填）
- 三态逐条: 
- 修复 commit: 
- 复检结论: 
