---
ttl: task_bound
title: 深度审查作业簿——执行引擎
owner: st-deeprev-20260918
created: 2026-09-18
---

# 深度审查报告：执行引擎（X03）

- 状态: **已审**
- 级别: P0｜类型: 管线
- 基线 commit: 2fa92002c3
- 审查者: GLM-5.3-Flash / st-deeprev-20260918
- 入口锚点: `src/zephyr/ex_core/execution_engine.py:129`
- 生产调用方: **全仓零生产构造方（已查无）**——仅 `ex_core/__init__.py:52,64` 懒加载导出 + execution_report.py:41 仅 import RunRecord 类型；骨架所记 risk_validation_bridge.py:81 装配经查为 RiskValidationPort 通用装配非本对象（已核实）
- 测试文件: tests/trading/unit/test_execution_engine_unit.py（8 passed，实测；文件头 [TESTS] 空置、[CONSUMERS] 所记 tests/ex_core/test_execution_engine_unit.py 路径漂移）
- 备注: 算法单(TWAP/VWAP/ICEBERG)+SOR 门面

## 1 对象快照

- **范围**：execution_engine.py 全文 473 行（execute_order 风控前置+四算法分派、_execute_sliced G7 切片接入、select_broker 伪 SOR、_record_run 执行记录）。
- **排除项**：切片算法数学内部在 X04（AlgoTradingEngine.generate_plan）；execution_report.py（CTR-P1-007 换算）仅审接口衔接。
- **测试覆盖概况**：8 passed（3.82s，真实路径 tests/trading/unit/）。覆盖：切片守恒/量剖 VWAP/ICEBERG 隐藏量/超限拒/无注入整笔回退。**未覆盖**：风控权重口径、切片循环中途失败、RunRecord 时效性。
- **材料包缺项声明**：运行时证据包无；数据画像不适用；checklist 15 条已过——**命中 #8 孤儿死码（第二例）、#12 假完成邻近（RunRecord 提交时点快照冒充执行报告）**。

## 2 六轴审查日志表

| 轴 | 发现 | 证据锚点 | 严重级 | 验证法 |
|---|---|---|---|---|
| A | **风控 target_weight 口径造假**：weight=数量/1,000,000 硬编码常数（无价格无 NAV 量纲）——qty≤10 万股恒过 max_single_position=0.10 闸；9.99 万股×300 元≈3000 万元单也放行。5.105.5 修复只把 Decimal 域算干净，常数语义未治 | execution_engine.py:194-196 | P1 | 造 qty=99_999 高价单观察 validate_order 收到 0.0999 |
| A | **风控限额硬编码**：RiskLimits 就地 new（max_single_position=0.10、无杠杆限额、as_of=now），上游 config.risk_limits 不透传——与 session/saga 侧限额真源三处各自为政 | execution_engine.py:198-202 | P2 | 改 config 限额观察引擎侧不生效 |
| A | **TWAP/VWAP/ICEBERG 静默降级整笔**：algo_engine 未注入时"占位整笔提交"，调用方语义上是算法单、市场收到的是一笔全量单（冲击成本）——测试 :197 把该行为固化为"backward compat"特性 | execution_engine.py:292-305,311-318,325-326; test:197 | P2 | 不注入 algo_engine 调 execute_order(TWAP) 断言单笔整量提交 |
| A | 切片循环注释称"HB-07 零重试：单片失败不重试，记录后继续"，实际循环**无 try/except**——第 k 片失败中断后续且 :453 母子关联/审计记录未写，已提交的 1..k-1 片成无母单跟踪的孤儿 | execution_engine.py:423-453 | P2 | mock 第 2 片 submit 抛异常，断言 algo_orders 无该母单条目 |
| A | `_build_algo_params` 参与率 0 → 回退 MAX_PARTICIPATION_RATE(5%)：配置 0 应语义为拒绝/报错，静默放大到上限是反方向 fail-open | execution_engine.py:353-355 | P3 | config.participation_rate=0 观察 pr=0.05 |
| A | RunRecord 数学：fill_rate 除零防护✓；slippage_bps/commission 恒 0 占位 | execution_engine.py:124-126,280-281 | P3(占位) | 读审 |
| B | 上游：MarketContextProvider.get_context 失败异常直接冒泡（无降级）→execute_order 抛非 ValueError 异常，execute_batch 只捕 ValueError→批内后续订单全部中断 | execution_engine.py:409,226-232 | P2 | mock get_context 抛 RuntimeError 观察批中断 |
| B | execute_order 假定 order 已注册 OrderManager（直接 submit），传值对象→ValueError("Order not found")——与 X01/X02 的 create-then-submit 契约相反，三处入口三种契约 | execution_engine.py:294,317,330 vs order_manager.py:285-292 | P3 | 传未注册 Order 复现 |
| C | 消费方清单：**零生产调用方**；execution_report.py 仅类型消费。爆炸半径=接线后算法单全量 | ex_core/__init__.py:52 | 记录(见 D/E) | grep 实证 |
| D | **孤儿死码第二例（checklist#8）**：ExecutionEngine 生产构造方全仓已查无（仅懒加载导出表）；select_broker/update_broker_score 全仓零调用（伪 SOR 纯死码）；与 X02 Saga 同型——执行域"基础设施层"系统性未接线 | execution_engine.py:237-251 + grep 实证 | P1 | `grep -rn "ExecutionEngine(" src/ scripts/ --include=*.py` |
| D | 文档漂移：文件头 [CONSUMERS] 记 tests/ex_core/test_execution_engine_unit.py，实际在 tests/trading/unit/；[TESTS] 空；INVARIANTS=none/SAFETY=L 与 P0 钱路径定位不符（注册表口径 vs 实际职责漂移） | execution_engine.py:5,8,11,14 | P3 | ls 两路径对照 |
| E | 静默失败：execute_batch 吞 ValueError 仅 log，返回列表不含被拒单（调用方无从分辨哪单失败）；非 ValueError 直接中断批 | execution_engine.py:226-232 | P2 | 两单其一被拒，断言返回列表长度 1 且无失败标记 |
| E | 假完成：_record_run 在提交时点拍快照（filled=0/avg=0/status=SUBMITTED），成交后永不刷新——get_engine_run_record 消费者拿到的是"提交时刻"冒充"执行报告"（checklist#12 邻近） | execution_engine.py:270-286 | P2 | 提交后注入成交再查 RunRecord 仍全零 |
| E | 重复触发/时序：execute_order 无幂等键管理（依赖 OrderManager FSM）；切片循环中断留下的孤儿子单无撤单补偿（与 A 轴同源） | execution_engine.py:426-453 | P2(并入) | 同 A 轴切片失败用例 |
| F | 见 §3 | — | — | — |

## 3 SOTA 对照

1. **SOR 与执行算法集成**：对等已有（方向）。业界 SOR 与 TWAP/VWAP 切片算法集成为标准架构（Horizon Trading SOR 指南， https://www.horizontrading.io/whats-a-smart-order-router-sor-sor/ ，2025-2026；B2BITS Dash Financial SOR 案例， https://www.b2bits.com/about/success-stories/smart-order-router-system-for-dash-financial ）；大单不宜整笔执行、应切片控冲击是执行算法基本共识（AlgoTrader 执行算法文档， https://algotrader.ch/resources/execution-algorithms/ ；CFA L3 Trade Execution 讲义， https://analystprep.com/study-notes/cfa-level-iii/trade-execution/ ）。本对象"算法单静默降级整笔"与该共识相悖；本仓真算法在 X04（generate_plan）——降级路径属兼容层但缺告警。
2. **SOR 券商评分路由**：立卡候选。真实 SOR 按价格/流动性/费率多因子动态路由（quantt.co.uk SOR 指南， https://www.quantt.co.uk/resources/smart-order-routing/guide ，2026；Wikipedia SOR 综述， https://en.wikipedia.org/wiki/Smart_order_routing ）。本对象 EWMA 单因子评分（0.9/0.1）且零调用方——若启用需补路由因子与评分来源；当前建议登记为占位设施而非"生产 SOR"。

## 4 缺陷清单

**P1-1 风控 target_weight 口径造假（数量/1,000,000 硬编码）**
- 现状：权重=股数÷一百万，无价格无净值量纲；≤10 万股恒过 10% 单票闸。
- 证据：execution_engine.py:194-196。
- 影响：接线后该风控前置形同虚设，大额订单假阳性过关（轴E 问 2 命中）。爆炸半径=经本引擎的全部订单。
- 建议修法：注入 NAV/价格源按 (qty×price)/NAV 算真权重，或显式标注本闸仅 fat-finger 数量阈值并按绝对金额设限。
- 验证法：单测造 9.9 万股×300 元单，断言 validate_order 入参 weight≈0.0999（与 3000 万元名义不符）。

**P1-2 ExecutionEngine 零生产接线（孤儿死码第二例，checklist#8）**
- 现状：生产构造方全仓查无；select_broker/update_broker_score 纯死码；RunRecord 类型被 execution_report 消费但生产数据流不存在。
- 证据：grep 实证（见 §2 D 轴）；ex_core/__init__.py:52,64 仅导出。
- 影响：与 X02 Saga 同型——执行域"引擎层"系统性未接线，CTR 契约（CTR-P1-007）生产链断裂。爆炸半径=架构口径。
- 建议修法：与 X02 P1-1 同批裁定（接线或登记为模拟设施）；select_broker 死码删除或补调用方。
- 验证法：grep 复核；对照装配层（qmt_trading_session/live_strategy_adapter）确认无注入点。

**P2-1 切片循环无容错且中断丢审计**（execution_engine.py:423-453；注释与行为不符；中途失败致已提交子单失母单跟踪+无补偿撤单；修法：逐片 try/except 记录续跑+失败片登记，finally 写 algo_orders；验证法：mock 第 2 片抛异常断言 algo_orders 有部分条目）。
**P2-2 TWAP/VWAP/ICEBERG 静默降级整笔无告警**（execution_engine.py:292-326；市场冲击语义漂移；修法：降级时 WARNING+RunRecord 标记 degraded；验证法：无注入路径断言告警日志）。
**P2-3 RunRecord 提交时点快照冒充执行报告**（execution_engine.py:270-286；slippage/commission 恒 0；修法：挂 fill 回调刷新或标 snapshot-at-submit；验证法：成交后查记录仍零）。
**P2-4 风控限额硬编码不透传**（execution_engine.py:198-202；与 session/saga 三处限额真源漂移；修法：限额注入化；验证法：改 config 断言引擎侧不变）。
**P2-5 execute_batch 失败单无痕**（execution_engine.py:226-232；修法：返回 (submitted, rejected) 或失败清单；验证法：混批拒一单查返回结构）。
**P2-6 get_context 失败中断整批**（execution_engine.py:409 vs :226-232；修法：归一化为 ValueError 契约；验证法：mock 抛 RuntimeError）。
**P3**：①参与率 0 回退 5% fail-open（:353-355）；②三处下单入口三种契约（:294 vs X01/X02）；③文件头 [TESTS]/[CONSUMERS]/SAFETY=L 漂移（:5,14,11）；④select_broker 评分默认 1.0 无区分度（:158,237-246）。

## 5 挂起疑问

1. P1-2 与 X02 P1-1（Saga 孤儿）合并裁定：执行域引擎/Saga 双设施均未接线——需 Owner 明确钱路径正门到底是 TradingSession 裸路径还是引擎+Saga 组合，再定两设施的接线或退役。
2. ExecutionEngineRunRecord 被 execution_report.py（CTR-P1-007 换算真源）消费——若引擎退役，该换算链的输入源需重接（跨对象影响）。
3. G7 切片路径（_can_use_algo 双注入）是否有装配层试点——未在装配真源中找到，归 X04 联动核实。

## 6 完备性自评

- 六轴全查：A（风控口径/降级语义/切片容错/参数钳制/RunRecord 数学）、B（ctx 失败传播/契约不一致）、C（零消费方实证）、D（孤儿第二例+文档漂移）、E（五问：静默=P2-5、假阳性=P1-1、断了没人知道=P2-3、重复触发=依赖 FSM、时序=P2-1）、F（2 条带来源对照+1 立卡）。
- 长尾：①generate_plan 内部数学归 X04 未深审；②execution_report 换算正确性归独立对象；③MarketContextProvider 实现未审。

## 7 收口裁定（收口方填）
- 三态逐条：
- 修复 commit:
- 复检结论:
