---
module_id: MOD-GOV-debt-rulings
title: 架构债务 DEFERRED-PERMANENT 裁定记录（第102轮架构师裁定）
version: 0.1.0
layer: L2_domain
depends_on: [architecture_debt_registry]
tags: [ruling, architecture-debt, permanent]
ttl: permanent
doc_type: audit_report
completes_when: 89 项 DEFERRED-PERMANENT 全部完成裁定并在 architecture_debt_registry.md 状态行回写
---

# 第102轮 DEFERRED-PERMANENT 架构裁定（裁定人：客观专业架构师，受 Owner 委托）

> 裁定原则（第一性原理 + 100% AI 开发 + 长远战略）：
> - P1 防复发 > 存量修复；P2 无回归测试不做高风险重构；P3 实际风险=0 的"违规"非债务；
> - P4 净收益必须为正；P5 可机械验证/执行的优先；P6 SSoT 唯一真源最高原则。
> - 裁定结论两类：EXECUTE（立即治本施工）/ RATIFY（确认前裁定，关闭为 wontfix-permanent 并验证防复发门禁在册）。

## 已核实证据的裁定（2026-07-19）

| 条目 | 裁定 | 证据与理由 |
|---|---|---|
| 5.93.1 zephyr/__init__.py import 副作用 | **RATIFY** | 2 个 daemon Timer 是 MOD-INF-015 auto_bootstrap 刻意设计（全面 monkey-patch 遥测，"零手动代码"），atexit 清理已在；NO-IMPORT-SIDE-EFFECT gate(priority=103) 已防新增。移除风险（遥测静默缺失）> 收益（import 纯净）。关闭 wontfix-permanent。 |
| 5.93.3 shared/__init__.py __all__ 170 名零 import | **EXECUTE** | 实测 `from zephyr.shared import X` 必失败（虚假广告=AI 幻觉陷阱），零消费者。方案：PEP 562 __getattr__ 惰性导出（若符号→子模块映射可机械派生）或裁剪 __all__ 至真实可导入集。 |
| 5.93.4 trading/__init__.py __all__ 41 名 | **RATIFY** | 实测 39 名全部是真实子模块（0 缺失），`from zephyr.trading import X` 经子模块机制可导入，非 bug。关闭。 |
| 5.93.8 未 scope 占位 | **RATIFY** | 空项，关闭。 |
| 5.100.15/5.100.16 asyncio API | **RATIFY** | 仅 fallback/CLI 单发路径，无实际风险；前裁定成立。 |
| 5.101 变量遮蔽 12 项 | **RATIFY** | LEGB 分析实例属性不参与作用域链，实际遮蔽风险=0；改名冲击 JSON 键/DB 列/API 契约，成本>收益（P3/P4）。 |
| 5.140.2 3 函数（100-200行） | **RATIFY** | 单一职责、认知复杂度在 AI 处理范围内；NO-HIGH-COMPLEXITY gate 已防新增。 |
| 5.143.20 ComplianceManagerBase | **RATIFY** | Phase B 骨架 OCP 扩展点，abc.ABC+runtime_checkable 双层防护，零运行时风险。 |
| 5.143.7-19 13 项盲盒 | **RATIFY** | 注册表从未记录条目，历 22 轮代码变化不可验证；ssot_redefinition_gate+cross_layer_contracts SSoT 提供覆盖。 |
| 5.145.13-26 系统性 Any（627处/100文件） | **RATIFY** | GATE-ANY-ABUSE 防复发已在（manual 阶段）；627 处一次性替换不可验证（错误标注比无标注更危险）；30-40% 为合理 Any。增量机会性清理为常态实践。 |
| 5.150.4 default_equity_strategy LSP | **DRIFTED（已修复）** | 实测签名 `generate_target_weights(universe, signals, constraints) -> dict[str, float]` 与 governance/strategies/strategy_base.py 基类一致（5.143.1 已修复）。状态从 DEFERRED-PERMANENT 改 FIXED。 |
| 5.150.1/2/3/7 God Class 4 处 | **EXECUTE（逐个，测试先行）** | 实测四类均有回归测试覆盖（tests/ 多文件），前裁定"无回归测试"前提已失效。100% AI 开发下 God Class 是 AI 上下文天敌（42 方法超单次注意力）。方案：Extract Class + 保留 facade 向后兼容 + 每步测试验证。执行顺序：ActionDispatcher(22)→ResourceOptimizationEngine(39)→FeedbackLoopScheduler(26)→AutoRuntimeCore(42)。 |
| 5.150.5/10/11 Long Parameter List | **EXECUTE** | factories.py 16/9/9 参数 → 引入参数对象（与 5.150.6 联动）。 |
| 5.150.6 RiskMetricsReport Data Class | **RATIFY** | 报告 DTO 17 字段 0 方法是合法模式（不可变数据载体），为加方法而加方法=过度工程（P4）。 |
| 5.150.16 Primitive Obsession | **RATIFY** | AgentCommunicationItem 7 个 str 参数影响序列化/契约，值对象重构冲击面大于收益（P4）。 |
| 5.152 #1 order.py 跨层 | **DRIFTED（已修复）** | 实测 OrderSide/OrderStatus/OrderType 已从 `zephyr.shared.contracts.enums.order_enums` 导入（shared 层下沉完成，AI-05）。状态改 FIXED。 |
| 5.152 其余 10 项跨层依赖 | **EXECUTE（逐边分析）** | NO-UPWARD-IMPORT gate(priority=97) 已防新增。存量 11 边需逐边判定：类型下沉 shared / 标记 sanctioned。专项施工。 |
| 5.153.11 CT_ 类 44 个 | **EXECUTE（评估序列化后）** | 实测位于 contracts/batch1_infra.py(15)/batch2_governance.py/batch3_integration.py；先验证类名是否进序列化键，再决定批量重命名或 wontfix。 |
| 5.153.13 TraceContext 函数 PascalCase | **EXECUTE（带兼容别名）** | logging.py:290 函数与 contracts.trace_context.TraceContext 类撞名（真实混淆源），65 消费文件。方案：改 trace_context() + 保留 TraceContext 别名（[DEPRECATED]+TTL 过渡），消费方迁移后删别名。 |
| 5.153.7/8/9/16-21 命名统一 | **RATIFY** | db verb/连接函数名/create_session 参数/布尔 is_ 前缀——差异各有历史语义（不同 DB 不同函数名是特性非 bug），改名冲击契约，净收益为负（P4）。 |
| 5.160.2 apply_depgraph 118 处裸 SQL | **RATIFY** | SAFETY=H + 无测试覆盖 SQL 路径，提取常量不可验证行为等价；NO-BARE-SQL gate(priority=87) 已防新增。触碰时顺带提取为常态实践。 |
| 5.176.4 7 处 gate subprocess 脚本调用 | **EXECUTE** | 提取共享 helper `run_checker_script()`（统一 cwd/timeout/exit 解析），消除 7×15 行样板。低风险一致性优化。 |
| 5.42.4/5.97.6 SKIP（human_gated 文件） | **EXECUTE（Owner 已授权）** | baseline_manager.py 方法嵌套结构 bug + audit_trail_cli.py——Owner 委托全权修复，按结构 bug 处理。 |
