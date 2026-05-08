---
task_id: "TASK-INF-0111"
source_blueprint: "MOD-INF-002"
source_section: "蓝图 §2.1-K 金融/交易系统专项 B5-K01~K12 + §5.3 TradingKillSwitch/SimulatedClock/DeterministicRandom 代码骨架"
title: "盲点关闭——K.交易系统基础设施 B5-K01~K12 + 交易专项代码骨架实现"
description: |
  关闭交易系统专项盲点 B5-K01~K12。量化交易系统"不是又一个软件系统"。
  B5-K01 Emergency Trading Kill Switch→§5.3 TradingKillSwitch 代码骨架实现（五步停止序列：标记KILLED→取消所有订单→清空EventBus交易事件→L05只读→审计记录）+
  B5-K02 Pre-Trade Risk Check Pipeline→订单→仓位限制→资金检查→敞口检查→合规检查→才到交易所+
  B5-K03 Order State Machine→FIX Protocol 标准化：NEW→PENDING→PARTIAL→FILLED/CANCELLED/REJECTED+
  B5-K04 Market Data Clock→NTP→PTP IEEE 1588 统一时间戳+
  B5-K05 Deterministic Simulation→§5.3 DeterministicRandom 代码骨架（确定性随机）+ SimulatedClock（模拟时钟）+
  B5-K06 Paper Trading Infrastructure→EventBus emit→sandbox account 而非真实broker+
  B5-K07 Trade Reconciliation→三方对账：系统订单 vs 经纪商回执 vs 清算报告+
  B5-K08 Position & Exposure Aggregation→全局仓位/净敞口实时计算+硬限额+
  B5-K09 EOD/SOD Processing→日终持仓结算/损益计算/保证金监控/数据归档+
  B5-K10 Market Circuit Breaker Integration→交易所熔断→系统自动暂停该标的交易+
  B5-K11 Slippage & Market Impact Modeling→Almgren-Chriss 滑点模型+
  B5-K12 Fee & Commission Attribution→每笔交易费用归属到模块→纳入RI-15 FinOps。
priority: "P1"
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\runtime-integration\\blueprint.md"
downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\l01_infrastructure\\trading_kill_switch.py"
    description: "TradingKillSwitch——§5.3代码骨架实现：NORMAL/PAPER_ONLY/READ_ONLY/KILLED四态+五步停止序列"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\shared\\production\\simulated_clock.py"
    description: "SimulatedClock——§5.3代码骨架实现：REAL/SIMULATED双模式+统一时间源now()/sleep()/advance_to()"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\shared\\production\\deterministic_random.py"
    description: "DeterministicRandom——§5.3代码骨架实现：全局共享种子+reseed()/uniform()/choice()"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\l01_infrastructure\\pre_trade_risk_pipeline.py"
    description: "PreTradeRiskPipeline——五阶段风控管道"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\l01_infrastructure\\order_state_machine.py"
    description: "OrderStateMachine——FIX Protocol 标准化状态机"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\l01_infrastructure\\paper_trading.py"
    description: "PaperTradingInfrastructure——sandbox account 隔离"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\l01_infrastructure\\trade_reconciliation.py"
    description: "TradeReconciliation——三方对账+diff告警"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\l01_infrastructure\\position_aggregation.py"
    description: "PositionExposureAggregation——全局仓位+净敞口+硬限额"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\l01_infrastructure\\market_clock.py"
    description: "MarketClock——NTP/PTP时间标准化"
allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\l01_infrastructure\\trading_kill_switch.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\production\\simulated_clock.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\production\\deterministic_random.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\l01_infrastructure\\pre_trade_risk_pipeline.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\l01_infrastructure\\order_state_machine.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\l01_infrastructure\\paper_trading.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\l01_infrastructure\\trade_reconciliation.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\l01_infrastructure\\position_aggregation.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\l01_infrastructure\\market_clock.py"
forbidden_touch:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\runtime-integration\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\**\\*.py"
applicable_rules:
  - module_id: "MOD-INF-002"
    section: "§5.3 TradingKillSwitch 代码骨架"
    reason: "activate(): 五步停止序列——标记KILLED→取消所有订单→清空EventBus→L05只读→审计永久记录"
  - module_id: "MOD-INF-002"
    section: "§5.3 SimulatedClock 代码骨架"
    reason: "now()统一时间源; sleep()回测瞬间跳过; advance_to()仅SIMULATED模式"
  - module_id: "MOD-INF-002"
    section: "§5.3 DeterministicRandom 代码骨架"
    reason: "reseed()重置种子→random.seed+numpy.random.seed对齐→seed相同=全系统随机行为完全相同"
context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\runtime-integration\\blueprint.md"
    reason: "§2.1-K 12项交易系统盲点 + §5.3 TradingKillSwitch/SimulatedClock/DeterministicRandom 代码骨架"
assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
  - "M2"
  - "M3"
  - "M4"
estimated_tokens: 38000
timeout_minutes: 120
acceptance_criteria:
  - "TradingKillSwitch.activate(): 五步停止序列全部执行→KILLED模式→所有交易订单取消→审计永久记录（B5-K01）"
  - "TradingKillSwitch.deactivate(): 仅 Owner 可解除（B5-K01）"
  - "PreTradeRiskPipeline: 5阶段检查链——任一阶段拒绝→交易不发出（B5-K02）"
  - "OrderStateMachine: FIX Protocol 标准——NEW→PENDING→PARTIAL→FILLED/CANCELLED/REJECTED（B5-K03）"
  - "MarketClock: 所有事件时间戳统一到交易所时钟 NTP/PTP（B5-K04）"
  - "DeterministicRandom: seed相同→全系统"随机"行为完全相同（B5-K05）"
  - "SimulatedClock: REAL模式 zero overhead / SIMULATED 模式时间推进（B5-M02）"
  - "PaperTrading: 所有交易模块自动支持 paper 模式（B5-K06）"
  - "TradeReconciliation: 三方对账 diff→0→系统一致（B5-K07）"
  - "PositionAggregation: 净敞口超限→自动拒绝新交易（B5-K08）"
rollback_instructions: |
  1. 删除 l01_infrastructure/ 下新增文件：trading_kill_switch.py / pre_trade_risk_pipeline.py / order_state_machine.py / paper_trading.py / trade_reconciliation.py / position_aggregation.py / market_clock.py
  2. 删除 shared/production/ 下新增文件：simulated_clock.py / deterministic_random.py
  3. 如 l01_infrastructure/ 目录仅剩这些文件→删除目录
depends_on:
  - "TASK-INF-0109"
blocked_by: []
status: "created"
tags_fn:
  - "infra"
  - "biz"
  - "security"
tags_ly: "l01_infrastructure"
tags_md: "deepseek"
tags_st: "active"
tags_mo:
  - "MOD-INF-002"
completed_gates: []
blocked_gates: {}
artifact_paths: []
audit_findings: []
ke_entries: []
ai_autonomy_level: "supervised"
autonomy_checklist: []
---
