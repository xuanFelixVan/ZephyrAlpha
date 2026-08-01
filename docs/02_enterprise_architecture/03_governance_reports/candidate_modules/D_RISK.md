---
doc_type: audit_report
title: 候选模块清单 — D_RISK
version: "1.0"
status: active
date: auto-generated
owner: auto-generator
ttl: permanent
---

# D_RISK 候选模块清单

> [← 返回索引](index.md)

> 本域候选 **499** 条（原有 2 + harvest 497）。
> harvest 去重四态: likely_new=241 / likely_implemented=224 / likely_planned=30 / uncertain=2

## 完整清单

| ID | 名称 / Name | 大白话（干什么用） | 域 | 状态 | 四问卡点 | 优先级 | 触发信号摘要 | 下次复查 |
|------|------|------|------|------|------|:---:|------|------|
| CAND-HARVEST-0072 | Risk Control 自适应风控 | C 004：自适应风控 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0074 | Systematic Stress Testing 系统性压力测试 | C 040：系统性压力测试 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0085 | Systematic Overfitting Protection 过拟合系统性防护 | C 033：过拟合系统性防护 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0092 | 黑天鹅模式库与预判 Black Swan Pattern Library and Prediction | C 038：黑天鹅模式库与预判 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0093 | 资金曲线自诊断与结构预警 Capital Curve Self-Diagnosis and Structure Warning | C 032：资金曲线自诊断与结构预警 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0176 | Risk Policy Manager风控策略管理 | / D-RISK-01 / Risk Policy Manager风控策略管理 / ✅ 能建 / 📋 项目内有蓝图编号MOD-L04-001部分建设 / 风控策略CRUD+版本管理+规则引擎 / | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0177 | Pre-Trade Checker盘前检查 | / D-RISK-02 / Pre-Trade Checker盘前检查 / ✅ 能建 / 📋 项目内有蓝图编号MOD-L04-001部分建设 / 下单前5步检查链+幂等+Fail-Closed(50ms) / | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0178 | Portfolio Risk Monitor持仓实时监控 | / D-RISK-03 / Portfolio Risk Monitor持仓实时监控 / ✅ 能建 / 📋 项目内有蓝图编号MOD-L04-001部分建设 / 持仓实时监控+VaR+回撤+告警 / | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0179 | Stop Loss Engine止损引擎 | / D-RISK-04 / Stop Loss Engine止损引擎 / ✅ 能建 / 📋 项目内有蓝图编号MOD-L04-001部分建设 / 止损评估(4种模式)+Kill Switch触发/重置 / | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0180 | Stress Test Engine压力测试引擎 | / D-RISK-05 / Stress Test Engine压力测试引擎 / ✅ 能建 / / 场景定义器/冲击传导器/损失聚合器 / | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0181 | VaR Calculator VaR计算器 | / D-RISK-07 / VaR Calculator VaR计算器 / ✅ 能建 / / 参数法+历史模拟→蒙特卡洛GPU→Basel III三角验证。与§29.16共形VaR互补: D-RISK-07提供传统VaR基线, §29.16 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0182 | Risk Budget Allocator风险预算分配 | / D-RISK-10 / Risk Budget Allocator风险预算分配 / ✅ 能建 / / 优化求解器+风险贡献计算器+再平衡触发器 / | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0183 | Risk Decomposition Engine风险分解引擎 | / D-RISK-12 / Risk Decomposition Engine风险分解引擎 / ✅ 能建 / / 因子贡献+残差+边际风险+成分风险分析 / | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0184 | Concentration Risk Monitor集中度风险监控 | / D-RISK-13 / Concentration Risk Monitor集中度风险监控 / ✅ 能建 / / HHI计算+行业暴露+对手方集中度+预警 / | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0185 | Risk Limit Manager风险限额管理 | / D-RISK-14 / Risk Limit Manager风险限额管理 / ✅ 能建 / / 限额定义/消耗追踪/预警分级/审批流 / | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0186 | Credit Risk Engine信用风险引擎 | / D-RISK-20 / Credit Risk Engine信用风险引擎 / ❌ 不能建 / / 门禁: ①50万AUM无信用风险敞口 ②D-CROSS-ASSET域就绪 / | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0187 | A-Share Stop-Loss Rule Engine A股特色止损 | / D-RISK-27 / A-Share Stop-Loss Rule Engine A股特色止损 / ✅ 能建 / / 6种止损模式+亏损限制(日2%/周5%/月10%) / | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0188 | A-Share Systemic Risk Detector A股系统性风险检测 | / D-RISK-28 / A-Share Systemic Risk Detector A股系统性风险检测 / ✅ 能建 / / 5大信号(融资盘/量化踩踏/流动性/政策/外围) / | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0189 | A-Share Loss Limit Enforcer A股亏损限额强制执行 | / D-RISK-30 / A-Share Loss Limit Enforcer A股亏损限额强制执行 / ✅ 能建 / / 日2%/周5%/月10%限额+强制停盘1-3天 / | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0190 | Stop-Loss Engine止损引擎 | / D-RISK-94 / Stop-Loss Engine止损引擎(L04) / ✅ 能建 / 📋 项目内有蓝图编号MOD-L04-001部分建设 / 与D-RISK-04合并，统一止损规则/触发/执行/审计 / | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0191 | 仓位限制预检器 Position | / D-RISK-12 / Risk Decomposition Engine风险分解引擎 / ✅ 能建 / / 因子贡献+残差+边际风险+成分风险分析 / | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0192 | 保证金比例安全检查器 Security | / D-RISK-97 / 保证金比例安全检查器 / ❌ 不能建 / / 门禁: Long-Only无保证金交易 / | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0193 | 风险指标体系定义器 Risk | / D-RISK-102 / 风险指标体系定义器 / ✅ 能建 / / VaR+CVaR+波动率+最大回撤+夏普+索提诺 / | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0194 | 紧急停止安全确认 Security | / D-RISK-115 / 紧急停止安全确认 / ✅ 能建 / 📋 项目内有蓝图编号MOD-INF-001部分建设 / 紧急操作二次确认与审计日志 / | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0641 | VaR Compute Data Prefetcher VaR计算数据预取器 | / D-DATA-44 / VaR Compute Data Prefetcher / VaR计算数据预取器(DuckDB读Parquet预取+预取缓冲区+预取策略+I/O瓶颈监控) / ✅能建。在D-RISK VaR计算中增加prefet | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0671 | 历史数据代表性验证器 Historical Data Representativeness Validator | 历史窗口充足性+结构性断点检测+制度转换检测+数据新鲜度 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0672 | Risk Policy Persister 风控策略持久化 | / D-RISK-49 / Risk Policy Persister / 风控策略SQLite持久化+版本管理(risk_policy+risk_limit+risk_policy_version表) / ✅能建。当前风控策略已在代码中定 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0673 | 双时态PositionSnapshot管理器 Bitemporal Position Snapshot Manager | / D-RISK-81 / 双时态PositionSnapshot管理器 / bitemporal双时态PositionSnapshot+双时态查询/版本管理/一致性 / ✅能建。与§13 PIT双时态建模对齐(即§13的system_ti | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0674 | VaR DuckDB历史模拟查询构建器 VaR DuckDB Query Builder | / D-RISK-82 / VaR DuckDB历史模拟查询构建器 / VaR用DuckDB历史模拟复用数据域Parquet+查询构建/优化/缓存 / ✅能建。当前VaR计算已使用DuckDB查询Parquet，增量改进：增加查询缓存+性能 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0675 | 风险指标计算数据源依赖管理器 Risk Metric Data Dependency Manager | 风险指标计算跨模块数据依赖管理+依赖图 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0712 | C-004 风控 Risk Control | 风控Level-2数据 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0718 | C-038 黑天鹅检测 Black Swan Detection | 黑天鹅检测VIX | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0728 | 风控状态物化视图 Risk Status View | / 风控状态 / risk:status / Hash / 实时 / <5ms / | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0749 | Risk Budget Allocator 风险预算分配器 | 风险预算分配优化求解器风险贡献计算器再平衡触发约束处理器 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0764 | Risk Policy Manager 风险策略管理器 | 风控策略CRUD版本管理策略状态机DRAFT ACTIVE DEPRECATED冲突检测 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0765 | Pre-Trade Checker 盘前检查器 | 5步检查链仓位限额行业集中度杠杆率合规规则Kill Switch Fail-Closed 50ms SLA | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0766 | Portfolio Risk Monitor 组合风险监控器 | 持仓实时监控VaR回撤告警因子暴露计算相关性矩阵 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0767 | Risk Limit Manager 风险限额管理器 | 9种限额类型消耗追踪预警分级审批流 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0768 | Concentration Risk Monitor 集中度风险监控器 | HHI行业暴露监控申万31行业个股集中度实时计算集中度告警 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0769 | A-Share Stop-Loss Rule Engine A股止损规则引擎 | 6种A股止损固定比例7%关键支撑破位逻辑失效竞价不及预期分时破位板块退潮 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0770 | A-Share Systemic Risk Detector A股系统性风险检测器 | 5大信号融资盘平仓潮量化踩踏流动性危机政策转向外围冲击三级警报 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0771 | Drawdown Real-Time Tracker 回撤实时跟踪器 | 最大回撤实时跟踪三级阈值-5%WARNING -10%CRITICAL -15%EMERGENCY回撤恢复检测 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0772 | Crowding Risk Monitor 拥挤风险监控器 | 同质度检测器资金流监控器踩踏预警器拥挤度指标器跨策略传染网络 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0773 | Black Swan Pattern Library 黑天鹅模式库 | 极端事件模式识别历史重放预案匹配黑天鹅事件分类自动根因分析 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0774 | Tail Risk Monitor 尾部风险监控器 | EVT POT模型尾部依赖矩阵Copula跳跃检测极值预警FRTB尾部风险加价 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0775 | Kill Switch Integration Kill Switch集成 | 状态机OPEN CLOSED 3种触发条件冷却期30min多域通知Owner确认重置 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0776 | Fail-Closed Degradation Handler Fail-Closed降级处理器 | 检查超时拒绝Fail-Closed超时检测50ms SLA降级逻辑恢复逻辑降级统计 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0777 | Configurable Rule Engine 可配置规则引擎 | YAML DSL规则文件运行时加载规则版本管理热更新规则测试沙箱规则回滚 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0778 | Post-Trade Daily Auditor 盘后日终审计器 | 日终PnL对账归因偏差检测合规报告生成日终检查清单问题追溯修正 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0995 | Scenario Analyzer 情景分析器 | 情景分析器：假设情景+敏感性分析+传染效应 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0996 | Liquidity Risk Monitor 流动性风险监控器 | 流动性风险监控：买卖价差+深度+冲击成本+流动性评分 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0997 | Risk Breach Logger 风险违规日志 | 风险违规日志：违规事件记录+分类+升级+追踪 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0998 | Counterfactual Analyzer 反事实分析器 | 反事实分析器：假设替代决策+影响量化+归因 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0999 | Risk Rule DSL Compiler 风控规则DSL编译器 | 风控规则DSL编译器：DSL→可执行规则+语法校验 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1000 | Risk Dashboard Generator 风险仪表盘生成器 | 风险仪表盘生成器：实时风险可视化+KPI+趋势 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1001 | Risk Report Auto-Generator 风险报告自动生成器 | 风险报告自动生成器：日/周/月风险报告+模板 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1002 | Risk Policy Backtester 风控策略回测器 | 风控策略回测器：策略历史回测+效果评估 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1003 | Limit Consumption Predictor 限额消耗预测器 | 限额消耗预测器：限额消耗趋势+预警+建议 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1004 | Leverage Dynamic Manager 杠杆动态管理器 | 杠杆动态管理器：杠杆率动态调整+约束+监控 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1005 | A-Share Stock Blacklist Manager A股股票黑名单管理器 | A股股票黑名单管理器：ST/退市/违规+自动更新 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1006 | A-Share Stop-Loss/Circuit Breaker Series A股特色止损/熔断系列 | 逆向专用止损/系统性风险三级告警/首分钟止损/级联熔断等(8项) | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1007 | VaR Enhancement Series VaR增强系列 | 正态性检验/方法差异分析/快速预筛/精确确认/并发编排/交叉验证等(8项) | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1008 | Permission/Idempotency/Kill Switch/Approval Series 权限/幂等/Kill Switch/审批系列 | 持仓写入权限/幂等保证/冷却期/审批网关/检查链编排等(11项) | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1009 | VaR Scheduling/Concentration/ATR/Monte Carlo Series VaR调度/集中度/ATR/蒙特卡洛系列 | VaR重算调度/行业集中度/ATR动态止损/蒙特卡洛精度/协方差分解等(14项) | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1010 | YAML/SQLite/SLA/Contract/Migration Series YAML加载/SQLite/SLA/契约/迁移系列 | YAML运行时加载/SQLite Schema/50ms SLA/契约提供者/迁移适配器等(15项) | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1011 | Gate/Dashboard/Profile/DSL/Warehouse Series 门禁/仪表盘/画像/DSL/仓储系列 | 策略相关性门禁/杠杆限额门禁/风险画像/DSL引擎/值对象/迁移适配等(33项) | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1020 | Risk Report Engine 风险报告引擎 | / D-REPORTING-08 / Risk Report Engine / 风险报告引擎(日度/周度/事件/月度4类风险报告生成)。消费D-RISK诊断结果 / ✅可建 / — / | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1117 | Risk Assessment 风险评估 | 风控Agent技能风险评估ACTIVE | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1318 | Trading Behavior Compliance Detector 交易行为合规检测器 | 四类异常交易检测：瞬时申报速率异常+频繁瞬时撤单+频繁拉抬打压+短时间大额成交 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1319 | Limit Up/Down Trading Constraint Executor 涨跌停交易约束执行器 | 涨停板不买入+跌停板不卖出；RK-02 Pre-Trade Checker实时价格检查 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1320 | Trading Rate Constraint Executor 交易速率约束执行器 | 单标的成交量占比≤5%+Almgren-Chriss冲击模型约束+订单停留≥50微秒 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1321 | Position Limit Compliance Detector 持仓限额合规检测器 | 单一持仓上限≤5%NAV+举牌义务(架构预留)+ST股限制≤5%NAV | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1322 | Industry Concentration Compliance Detector 行业集中度合规检测器 | 行业偏离≤基准±10%(极端±15%，绝对上限30%)+风格暴露≤±0.3标准差 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1323 | Pre-Trade Three Block Mode Engine Pre-Trade三种阻塞模式引擎 | Hard Block(不可绕过)+Soft Block(合规官审批后可放行)+Warning(自动放行+记录) | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1324 | Market Manipulation Prevention Detector 市场操纵防护检测器 | Spoofing(幌骗)+Layering(分层)+Wash Trade(洗盘)+尾盘操纵检测 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1325 | Fake Move Identification Signal Engine 假动作识别信号引擎 | 6种假动作识别+7维量化信号体系+Spoofing核心指标(CER/CancelVelocity/OrderLifeDuration) | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1326 | Collaborative Trading Behavior Detector 协同交易行为检测器 | 交易所标准(幌骗/对敲/关联账户协同/异常波动)+机构级+高级(GNN/TCN/联邦学习) | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1327 | Information Asymmetry Period Manipulation Detector 信息不对称期操纵检测器 | 空窗期异常检测(定期报告间隔>90天)+操纵行为检测(幌骗/对敲/尾盘操纵) | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1459 | Liquidity Evaporation 流动性蒸发 | 成交量骤降至30%+买卖价差扩大3倍→参与率约束收紧至5%+暂停做T | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1460 | Correlation Collapse 相关性崩塌 | 跨板块相关性<0.1+分散化失效→集中度强制分散+降总仓位 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1461 | Volatility Eruption 波动率爆发 | VIX类指标>2σ+已实现波动率翻倍→仓位减半+暂停新开仓 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1462 | Margin Call Stampede 融资盘踩踏 | 两融余额单日降>10%+融资保证金上调→降杠杆敞口+暂停融资标的 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1463 | Cross-Market Contagion 跨市场传导 | 外围市场暴跌+北向资金大幅流出→降仓位至市场状态对应档位 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1464 | Policy Black Swan 政策黑天鹅 | 交易规则突变/印花税调整/行业禁令→暂停受影响标的交易+评估 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1465 | Systemic Risk 系统性风险 | 多个BS模式同时触发→Kill Switch(P0) | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1806 | Pre-Trade Idempotency Guarantor 盘前幂等保证器 | 盘前幂等保证器：同步拦截+幂等检查+重复请求防护 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1807 | Pre-Trade Check Chain Orchestrator 盘前检查链编排器 | 盘前检查链编排器：5步检查链编排+顺序执行+首个Hard Block即终止 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1808 | Pre-Trade 50ms SLA Monitor 盘前50ms SLA监控器 | 盘前50ms SLA监控器：延迟<50ms+超时检测+SLA告警 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1809 | Pre-Trade RiskCheckResult Router 盘前风控结果路由器 | 盘前风控结果路由器：检查结果分发+Hard Block/Soft Block/Warning三级路由 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1810 | Order Generation Risk Pre-Check 订单生成风控前置 | 订单风控前置检查：订单生成前风控拦截+否决执行 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1811 | Max Drawdown Real-Time Tracker 最大回撤实时跟踪器 | 最大回撤实时跟踪器：峰值谷值+三级阈值(-5%/-10%/-15%)+回撤恢复检测 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1812 | Sector Concentration Real-Time Calculator 行业集中度实时计算器 | 行业集中度实时计算器：申万31行业+偏离度±10%+风格暴露±0.3σ | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1813 | RiskLimit 9-Type Enum Manager 风险限额9类枚举管理器 | 风险限额9类枚举管理器：SINGLE_INSTRUMENT/SECTOR/GROSS/NET/VAR_95/VAR_99/MAX_DD/LEVERAGE/FACTOR | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1814 | Enforcement 3-Level Executor 执行3级执行器 | 执行3级执行器：HARD_BLOCK(不可绕过)/SOFT_WARN(合规官审批)/POST_ONLY(记录) | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1815 | Liquidity Limit Filter 流动性限制过滤器 | 流动性限制过滤：参与率约束≤5%+流动性评分+Almgren-Chriss冲击模型 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1816 | Dynamic Position Adjuster 动态仓位调整器 | 动态仓位调整：风险信号→仓位自动调整+市场状态联动 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1817 | Abnormal Trade Detection Interceptor 异常交易检测拦截器 | 异常交易检测拦截：4类异常交易(瞬时申报>15笔/秒/撤单率>15%/拉抬打压/大额成交)+Hard Block | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1818 | Risk Audit Trail Writer 风险审计轨迹写入器 | 风险审计轨迹写入器：审计链完整性+事件溯源+不可篡改记录 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1819 | Normality Test Engine 正态性检验引擎 | 正态性检验引擎：参数法VaR前提+Jarque-Bera/Shapiro-Wilk分布检验 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1820 | VaR Method Discrepancy Analyzer VaR方法差异分析器 | VaR方法差异分析器：模型风险+参数法vs历史模拟vs蒙特卡洛对比 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1821 | VaR Fast Pre-Screen Alerter VaR快速预筛告警器 | VaR快速预筛告警器：L1实时监控+参数法快速筛选(<1ms) | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1822 | VaR Precise Confirmer VaR精确确认器 | VaR精确确认器：L2日频+历史模拟精确计算(~5ms) | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1823 | Two-Tier Alert Strategy Engine 双层告警策略引擎 | 双层告警策略引擎：L1快速预筛+L2精确确认双层告警路由 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1824 | VaR Concurrent Compute Orchestrator VaR并发计算编排器 | VaR并发计算编排器：多方法并发计算+ThreadPoolExecutor+结果聚合 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1825 | VaR Cross-Validation Engine VaR交叉验证引擎 | VaR交叉验证引擎：回测+Basel交通灯测试(Kupiec+Christoffersen) | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1827 | VaR Phase Independence Guarantor VaR阶段独立性保证器 | VaR阶段独立性保证器：三阶段独立可用+Phase1完成即可上线 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1828 | Basel III Multiplier Factor Manager Basel III乘数因子管理器 | Basel III乘数因子管理器：交通灯测试+乘数因子(3×基础)+压力VaR | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1829 | Monte Carlo Precision Level Manager 蒙特卡洛精度级别管理器 | 蒙特卡洛精度级别管理器：精度控制+收敛检测+模拟次数自适应 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1830 | Covariance Matrix Decomposer 协方差矩阵分解器 | 协方差矩阵分解器：协方差估计+Cholesky分解+指数加权(EWMA) | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1831 | Risk Budget Adjuster 风险预算调整器 | 风险预算调整：因子暴露+预算再平衡+优化求解器 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1832 | Risk Stress Tester 风控压力测试器 | 风控压力测试：情景构建+冲击模拟+历史情景回放(2008/2015/2020) | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1833 | A-Share PDF Tail Risk Auto-Hedger A股PDF尾部风险自动对冲器 | A股PDF尾部风险自动对冲器❌不能建：需A股期权市场日均成交量>100亿元(RD-22) | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1834 | A-Share Contrarian Dedicated Stop-Loss A股逆向专用止损 | A股逆向专用止损：逆向策略专用止损逻辑+参数独立 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1835 | A-Share Systemic Risk 3-Level Alerter A股系统性风险三级告警器 | A股系统性风险三级告警器：1因子停开仓/2因子降30%/≥3因子清仓 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1836 | A-Share First-Minute Stop-Loss Executor A股首分钟止损执行器 | A股首分钟止损执行器：开盘首分钟异常止损+竞价不及预期 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1837 | A-Share Contrarian Time-Based Stop-Loss A股逆向时间止损 | A股逆向时间止损：逆向策略时间维度止损+持仓超时平仓 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1838 | A-Share Multi-Level Loss Circuit Breaker A股多级亏损熔断器 | A股多级亏损熔断器：亏损分级+熔断触发+冷却期 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1839 | A-Share 5-Signal Systemic Risk Scanner A股5信号系统性风险扫描器 | A股5信号系统性风险扫描器：BS-001~007黑天鹅信号扫描 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1840 | A-Share Cascading Circuit Breaker A股级联熔断器 | A股级联熔断器：跨策略/跨市场级联熔断+传染隔离 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1841 | AISG Regulatory Compliance Checker AISG监管合规检查器 | AISG监管合规检查器：程序化交易合规+2026.4.7新规(15笔/秒)+报单停留≥50μs | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1842 | Kill Switch Cooldown Manager Kill Switch冷却期管理器 | Kill Switch冷却期管理器：30min冷却期+状态锁定+重置 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1843 | Kill Switch Trading System Integrator Kill Switch交易系统集成器 | Kill Switch交易系统集成器：撤单+暂停+通知+多域协调 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1844 | Kill Switch Multi-Domain Notifier Kill Switch多域通知器 | Kill Switch多域通知器：D-EX-CORE撤单+D-PF-CORE暂停+D-AUTONOMY告警 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1845 | Kill Switch State Machine Manager Kill Switch状态机管理器 | Kill Switch状态机管理器：OPEN/CLOSED+转换+持久化 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1846 | Kill Switch New Order Rejector Kill Switch新订单拒绝器 | Kill Switch新订单拒绝器：CLOSED状态下新订单拦截+拒绝 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1847 | Kill Switch Owner Confirmation Reset Gateway Kill Switch Owner确认重置网关 | Kill Switch Owner确认重置网关：Owner确认+状态重置+审计记录 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1848 | ATR Dynamic Stop Loss Calculator ATR动态止损计算器 | ATR动态止损计算器：ATR倍数+动态调整+波动率自适应 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1849 | Time-Based Stop Loss Evaluator 时间止损评估器 | 时间止损评估器：时间维度止损+持仓超时平仓+逻辑失效检测 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1850 | Risk Policy Approval Gateway 风险策略审批网关 | 风险策略审批网关：四级审批+审批流+合规官审批 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1851 | Risk Policy DDD Aggregate Root AGG-007 Manager 风险策略DDD聚合根AGG-007管理器 | 风险策略DDD聚合根AGG-007管理器：聚合根+事件溯源+状态机(DRAFT→ACTIVE→DEPRECATED) | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1852 | RiskDashboardSnapshot CTR-P1-008 Builder 风险仪表盘快照CTR-P1-008构建器 | 风险仪表盘快照CTR-P1-008构建器：契约快照+数据聚合+序列化 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1853 | RiskMetricsReport CTR-P1-011 Generator 风险指标报告CTR-P1-011生成器 | 风险指标报告CTR-P1-011生成器：契约报告+指标计算+格式化 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1854 | Daily Risk Report Generator 每日风险报告生成器 | 每日风险报告：日度摘要+关键指标+异常事件汇总 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1855 | Custom Risk Report Generator 风险报告自定义生成器 | 风险报告自定义：用户自定义报告模板+输出格式+筛选条件 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1856 | Real-time Risk Warning and Report Generator 实时风险预警与报告生成器 | 实时风险预警报告：事件快报+实时告警+推送通知 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1857 | Strategy Correlation Gate Checker 策略相关性门禁检查器 | 策略相关性门禁检查器：VR-013策略拥挤+相关性阈值+Hard Block | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1858 | Leverage Limit Gate Checker 杠杆限额门禁检查器 | 杠杆限额门禁检查器：杠杆率门禁+限额检查+Hard Block | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1859 | Risk Rule User Configurator 风险规则用户配置器 | 风险规则用户配置：用户自定义规则+参数配置+预览 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1860 | Risk Control Rule Engine 风险控制规则引擎 | 风险控制规则引擎：否决规则5级引擎+执行+评估 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1861 | Risk Rule Validation and Stress Tester 风控规则验证与压力测试器 | 风控规则验证+压力测试：规则测试沙箱+模拟执行+回归测试 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1862 | Rule Priority Sorter (Inter-Rule) 规则优先级排序(规则间) | 规则优先级排序(规则间)：规则冲突检测+优先级排序+依赖解析 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1863 | Risk Rule DSL Engine 风控规则DSL引擎 | 风控规则DSL引擎：DSL解析+执行+AST构建 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1864 | Risk Engine Rule DSL 风控引擎规则DSL | 风控引擎规则DSL：DSL语法定义+关键字+操作符 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1865 | Risk Rule Versioning and Hot Updater 风控规则版本化与热更新器 | 风控规则版本化+热更新：版本管理+运行时热更新+回滚 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1866 | Rule Priority Sorter (Inter-Strategy) 规则优先级排序(策略间) | 规则优先级排序(策略间)：策略冲突+优先级+仲裁 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1867 | CTR-006 PositionSnapshot Provider CTR-006仓位快照提供者 | CTR-006仓位快照提供者：仓位快照契约+实时快照+序列化 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1868 | CTR-004 Order Consumer CTR-004订单消费者 | CTR-004订单消费者：风险数据流+订单消费+事件驱动 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1869 | CTR-003 RiskLimits Producer CTR-003风险限额生产者 | CTR-003风险限额生产者：限额契约+生产+版本管理 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1870 | Position Write Authority Arbiter 仓位写入权限仲裁器 | 仓位写入权限仲裁器：DDD聚合根边界+写入权仲裁+事件驱动写入 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1871 | Rule Engine vs Statistical Engine Router 双引擎路由器 | 双引擎路由器：规则引擎(确定性→硬阻断)vs统计引擎(概率性→告警+建议)路由 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1872 | Risk Rule YAML Runtime Loader 风险规则YAML运行时加载器 | 风险规则YAML运行时加载器：YAML加载+热加载+语法校验 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1873 | Risk Policy SQLite Schema Designer 风险策略SQLite Schema设计器 | 风险策略SQLite Schema设计器：Schema设计+迁移脚本+版本管理 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1874 | IV Parametric VaR to Historical Simulation Migrator 参数法VaR→历史模拟法迁移器 | 参数法VaR→历史模拟法迁移器：方法迁移+数据转换+回滚 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1875 | DefaultRiskValidator to Configurable Rule Engine Migrator DefaultRiskValidator→可配置规则引擎迁移器 | DefaultRiskValidator→可配置规则引擎迁移器：硬编码→可配置迁移+兼容性 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1876 | Execution Result Feedback Consumption Bridger 执行结果反馈消费桥接器 | 执行结果反馈消费桥接：执行域→风控域反馈+事件消费+参数优化 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1877 | Risk Domain Value Object Definition 风控域值对象定义 | 风控域值对象定义：DDD值对象+类型安全+不可变 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1878 | Risk Rule Engine Upgrade Migration Adapter 风控规则引擎升级迁移适配器 | 风控规则引擎升级迁移适配：版本升级+迁移脚本+向后兼容 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1879 | Counterparty Risk Manager 交易对手风险管理器 | 交易对手风险管理器：需开展衍生品/融资融券/回购业务(远期) | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1880 | Market Digital Twin 市场数字孪生 | 市场数字孪生：需ABIDES-MARL研究基础设施+GPU资源(远期) | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1881 | Climate Risk Engine 气候风险引擎 | 气候风险引擎：需ESG数据源+ESG因子纳入风险模型(远期) | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1882 | Monte Carlo Batch Backtester 蒙特卡洛批量回测器 | 蒙特卡洛批量回测器：需GPU资源可用(远期) | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1883 | Monte Carlo Portfolio PnL Sorter 蒙特卡洛组合PnL排序器 | 蒙特卡洛组合PnL排序器：需GPU资源可用(远期) | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1884 | AI-Enhanced Risk Engine AI增强风控引擎 | AI增强风控引擎：需D-ML域Phase2就绪+AI风控可解释性验证(远期) | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1885 | AI Risk Engine Implementer AI风控引擎实现器 | AI风控引擎实现器：同D-RISK-95门禁条件(远期) | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1886 | Personalized Risk Profile Builder 个性化风险画像构建器 | 个性化风险画像：风险偏好+画像构建+历史行为分析 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2002 | 风险传播建模 Risk Propagation Modeling | NetworkX图传播模拟:系统性风险→行业→个股级联传播 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2047 | VaR Calculator 风险价值计算器 | 蒙特卡洛VaR计算:基于GPU加速蒙特卡洛的VaR/CVaR估计(❌) | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2049 | 绩效归因 Performance Attribution | Brinson模型:配置效应+选择效应+交互效应分解收益来源 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2050 | Brinson模型 Brinson Model | 绩效归因学术标准分解为配置效应+选择效应 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2052 | IC衰减检测 IC Decay Detection | 因子IC的60日移动平均趋势IC衰减>50%=策略退化 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2053 | 拥挤度检测 Crowding Detection | 使用同一策略的参与者数量估计拥挤度上升=超额收益将消失 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2054 | 自动降权 Auto Weight Reduction | / 自动降权 / 策略退化时自动将权重降为0 / Man Group AlphaGPT实践 / | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2112 | Risk Manager Agent 风控Agent | 战略层风控Agent战略级风控评估仓位上限决策 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2141 | Hedge Execution 独立对冲执行 | 风控Agent技能独立对冲执行ACTIVE | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2243 | Kill Switch 紧急制动 | / Kill Switch日志 / 触发条件/时间/恢复时间/人工确认 / ≥7年 / 哈希链+独立存储 / | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2315 | Amihud Illiquidity Amihud非流动性指标 | / 日度风险摘要 / 每日收盘 / VaR/CVaR/因子暴露/否决统计/漂移状态/Amihud非流动性 / Trader+Risk Manager / | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2316 | Reverse RST 反向RST指标 | / 周度风险深度 / 每周五 / 压力测试+漂移趋势+策略拥挤度+模型健康度+反向RST / Risk Manager / | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2317 | PSI/KS/CUSUM PSI/KS/CUSUM漂移检测指标 | / 漂移检测日志 / PSI/KS/CUSUM值/检测时间/处置动作 / ≥3年 / 哈希链 / | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2344 | Veto Flow 否决流 | / **否决流** / 风控Agent→任意层（横向穿透） / 熔断指令、仓位上限、交易禁止 / 否决流为最高优先级，可穿透任意层；否决信号为immutable级，任何Agent收到后必须终止当前操作 / | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2345 | P0-Emergency P0紧急指令 | / P1-高 / 仓位上限调整、交易禁止 / 风控Agent/战略层 / 优先处理，可中断当前非紧急指令 / | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2346 | P1-High P1高优先级指令 | P1-高仓位上限调整交易禁止风控Agent/战略层优先处理可中断当前非紧急指令 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2382 | Risk Report 风险报告 | 风险报告4类型日度风险摘要到周度风险深度到事件风险快报到月度风险治理来源A4§4.3 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2383 | Risk Audit 风控审计 | / 日度风险摘要 / 每日收盘 / VaR/CVaR/因子暴露/否决统计/漂移状态/Amihud非流动性 / Trader+Risk Manager / | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2618 | Black Swan Pattern Library 黑天鹅模式库7种模式 | 7种模式库BS-001~007+跨市场传导4渠道 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2624 | Model Risk SR 26-2 模型风险 | SR 26-2/5类漂移检测/CUSUM/过拟合防护 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2625 | Liquidity Risk 流动性风险 | / 流动性风险（参与率/LVaR/Amihud/Kyle/退出时间/流动性螺旋） / 数据存储方案（→A3） / | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2626 | Operational Risk 操作风险 | 系统故障/人为错误/Agent失控/级联失败 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2627 | AI Agent Specific Risk AI/Agent特有风险 | OWASP ASI+AST+MCP完整映射 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2674 | A Share Compliance Rule A股合规规则代管 | 不操纵市场/持仓限额/涨跌停约束/A股风险日历 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2675 | Drift Detection Risk Closed Loop 漂移检测与风险闭环 | 事前PSI/事中在线适应/事后重训触发 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2676 | Extreme Event Black Swan 极端事件与黑天鹅 | 7种模式库BS-001~007+跨市场传导4渠道 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2677 | AI Agent Risk Governance AI/Agent风险治理 | 有界自治5级+保障缺口管理+治理漂移防护 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2986 | Risk Control Agent 风险 | 仓位上限决策+熔断触发+独立对冲执行 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2996 | 风控域规则目录 Risk Domain Rule Catalog | 风控参数熔断机制止损 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3089 | ESRB 2025系统性风险报告 | AI放大系统性风险11渠道 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3094 | Unleash 2026 Kill Switch Unleash 2026紧急制动 | 细粒度Kill Switch本地评估 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3134 | 顺周期性 Pro-cyclicality | ESRB系统性风险AI羊群行为 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3135 | 速度 Speed | ESRB系统性风险Kill Switch<1ms | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3139 | 集中度 Concentration | ESRB系统性风险单票集中度 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3198 | KS-L1 软暂停 Kill Switch | 滑点超限/单策略日内亏损超限暂停新开仓 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3199 | KS-L2 会话熔断 Kill Switch | 连续N笔亏损/模型漂移超阈值禁用策略 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3200 | KS-L3 通道断开 Kill Switch | 下单拒绝率飙升/miniQMT心跳失败断开交易通道 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3201 | KS-L4 硬停机 Kill Switch | 持仓异常/账户级日亏损超硬限终止所有自动化 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3216 | LVaR价差模型 | LVaR=VaR+½×S×W正常市场+小仓位 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3217 | LVaR Amihud冲击模型 | LVaR=VaR+ILLIQ×(Q/V)^α大仓位+非标资产 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3218 | LVaR EVT尾部模型 | LVaR=VaR+EVT尾部流动性溢价极端行情 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3219 | CoVaR跨市场传染 | CoVaR条件VaR给定i机构压力系统性风险 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3220 | Grinold & Kahn容量公式 | 策略容量=f(ADV,参与率上限 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3304 | EVT极值理论 | 尾部相关EVT极值理论 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3323 | 市场风险 Market Risk | §1.1因市场价格不利变动导致投资组合价值损失 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3324 | 价格风险 Price Risk | 市场风险子类实时P&L监控+因子暴露监控 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3325 | 波动率风险 Volatility Risk | 市场风险子类VIX类指标+已实现vs隐含波动率 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3326 | 相关性风险 Correlation Risk | 市场风险子类滚动相关矩阵+条件相关性 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3327 | 尾部风险 Tail Risk | 市场风险子类极值理论EVT+共形VaR超限频率 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3328 | L1实时监控 L1 Real-time Monitoring | 三层度量体系实时P&L+因子暴露+集中度+Amihud | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3329 | L2日频因子风险模型 L2 Daily Factor Risk Model | 三层度量体系申万31行业+4风格因子+VaR/CVaR/ES | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3330 | L3压力测试 L3 Stress Testing | 三层度量体系历史回放+假设情景+程式化冲击 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3331 | 风险分级预警 Risk Tiered Alert | 系统性风险分级预警与尾部风险管理模型 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3332 | 模型风险 Model Risk | §1.2因模型设定错误实现错误误用或漂移导致决策偏差 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3333 | 模型设定风险 Model Specification Risk | 模型风险子类概念健全性审查+基准对比 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3334 | 实现风险 Implementation Risk | 模型风险子类训练-服务一致性校验+代码审计 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3335 | 误用风险 Misuse Risk | 模型风险子类适用场景审查+输入范围检查 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3336 | 过拟合风险 Overfitting Risk | / 过拟合风险 / Purged K-Fold+Walk-Forward+Permutation Test / 样本内外Sharpe比+Permutation p值 / 策略否决上线 / 样本外Sharpe<70%样本内→否决 / | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3337 | 模型组合风险 Model Combination Risk | 模型风险子类多模型交互产生聚合风险 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3338 | 协变量漂移 Covariate Drift | 漂移检测五分类P_train(X)≠P_test(X) | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3339 | 概念漂移 Concept Drift Type | 漂移检测五分类P_train(Y/X)≠P_test(Y/X) | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3340 | 标签漂移 Label Drift | 漂移检测五分类P_train(Y)≠P_test(Y) | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3341 | 公平性漂移 Fairness Drift | 漂移检测五分类子群体性能差异扩大 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3342 | 上游数据漂移 Upstream Data Drift | 漂移检测五分类数据管道Schema/质量变化 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3343 | CUSUM控制图 CUSUM Control Chart | 补充PSI/KS的持续性偏移检测 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3344 | 流动性风险 Liquidity Risk | §1.3因市场流动性不足导致无法以合理价格/时间完成交易 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3345 | 市场深度风险 Market Depth Risk | 流动性风险子类实时买卖盘深度+成交量 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3346 | 冲击成本风险 Impact Cost Risk | 流动性风险子类Almgren-Chriss模型+历史冲击 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3347 | 退出时间风险 Exit Time Risk | 流动性风险子类退出时间估算模型 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3348 | 流动性螺旋风险 Liquidity Spiral Risk | 流动性风险子类资金流动性vs市场流动性交互 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3349 | 策略容量风险 Strategy Capacity Risk | 流动性风险子类策略可管理最大AUM | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3350 | Amihud ILLIQ 非流动性指标 | 流动性四维学术度量价格冲击单位成交量引起的价格变动 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3351 | Kyle Lambda 凯尔lambda | 流动性四维学术度量永久价格冲击单位订单流的价格影响 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3352 | Roll Spread Estimator 罗尔价差估计器 | 流动性四维学术度量隐含买卖价差无需报价数据 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3353 | Pastor-Stambaugh 流动性因子 | 流动性四维学术度量系统性流动性风险因子 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3354 | Almgren-Chriss最优执行框架 Almgren-Chriss Optimal Execution Framework | 临时冲击+永久冲击+风险厌恶+参与率上限 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3355 | 日内时变参与率 Intraday Time-Varying Participation Rate | A股日内成交量U型分布时变参与率降低执行成本 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3356 | 流动性降级模式 Liquidity Degradation Mode | 正常/降级/极端三级VaR处理+溢价 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3357 | 流动性调整VaR LVaR Liquidity-adjusted VaR | 价差模型+Amihud冲击模型+EVT尾部模型+CoVaR | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3358 | CoVaR跨市场传染 CoVaR Cross-Market Contagion | LVaR模型系统性流动性风险评估 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3359 | 流动性螺旋模型 Liquidity Spiral Model | 价差异常+强制卖出+流动性冻结三阶段 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3360 | 操作风险 Operational Risk | §1.4因系统故障人为错误流程缺陷或外部事件导致损失 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3361 | 系统故障 System Failure | 操作风险子类健康检查+心跳+进程监控 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3362 | 人为错误 Human Error | 操作风险子类操作审计+异常行为检测 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3363 | Agent失控 Agent Out-of-Control | 操作风险子类行为边界监控+涌现行为检测 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3364 | 买入后即时验证与快速纠错模型 Post-Entry Instant Validation Model | 买入后5-15分钟即时验证Intraday Momentum | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3365 | AI/Agent特有风险 AI/Agent Specific Risk | §1.5 AI自治系统引入的全新风险类别 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3366 | 策略同质化 Strategy Homogeneity | 策略同质化与串谋风险因子/策略相似度检测 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3368 | 影子MCP服务器 Shadow MCP | > MCP(Model Context Protocol)已成为Agent工具集成的默认协议层。OWASP MCP Top 10(2026.2)覆盖MCP协议特有风险——与AST10(Skills执行层)互补。Mental Model：AS | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3369 | 交易对手风险 Counterparty Risk | §1.6因交易对手违约导致损失当前不能建 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3370 | 信用风险 Credit Risk | §1.7因发行人信用恶化导致持仓资产价值损失当前不能建 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3371 | VaR风险价值 Value at Risk | §2.1核心度量指标95%/99%置信度历史模拟+参数法 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3372 | CVaR/ES条件风险价值 Conditional Value at Risk | §2.1核心度量指标97.5%尾部风险度量FRTB标准 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3373 | 密度感知VaR Density-Aware VaR | §2.1核心度量指标概率密度预测+分位数提取 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3374 | 共形VaR Conformal VaR | §2.1核心度量指标共形预测校准层分布无关覆盖率 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3375 | 时间加权共形风险控制 Time-Weighted Conformal | 共形VaR默认方法Schmitt 2026计算简单漂移下强默认 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3376 | 分位数预测共形校准 TCP Conformal | / 共形VaR / 95% / 1日 / 共形预测校准层 / 分布无关覆盖率保证 / TWC(默认,Schmitt 2026) / TCP(Aich et al. 2026) / RWC(增强,Schmitt 2026) / | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3377 | 体制加权共形风险控制 Regime-Weighted Conformal | 共形VaR增强方法Schmitt 2026体制条件校准稳定性 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3378 | 状态自适应贝叶斯共形预测 State-Adaptive Bayesian CP | / SA-BCP / Fang & Lee (arXiv:2605.00432, 2026.5) / 状态自适应贝叶斯共形预测：空间核密度证据门控长期时间惯性 / 解决ACI系统性覆盖不足+减少贝叶斯CP区间膨胀10-37% / 波动性金融 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3379 | 共形VaR回测 CP-VaR Backtesting | / CP-VaR回测 / Retzlaff et al. (COPA 2025) / CP与VaR形式等价→VaR回测方法可用于统计评估CP覆盖率 / Dynamic Binary Test+Geometric Conformal Back | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3380 | 压力测试 Stress Testing | §2.2压力测试回答市场崩溃时系统能否存活 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3381 | 情景分析 Scenario Analysis | §2.2情景分析回答如果X发生组合会怎样 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3382 | 反向压力测试 Reverse Stress Testing | §2.2反向压力测试回答什么情景会导致系统崩溃 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3383 | 流动性骤降 Liquidity Sudden Drop | A股特有压力情景日成交量缩至日均10%+价差扩大5倍 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3384 | 融资盘强平 Margin Call Forced Liquidation | A股特有压力情景两融余额单日下降15% | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3385 | 政策黑天鹅 Policy Black Swan | A股特有压力情景印花税上调/交易规则突变 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3386 | 跨市场传导 Cross-Market Transmission | A股特有压力情景港股暴跌→A股联动 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3387 | 黑天鹅加T+1锁定 Black Swan with T+1 Lock | A股特有压力情景极端事件当日无法卖出+次日跳空 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3388 | 风险否决权 Risk Veto Power | §3风控可否决一切交易决策但不可修改策略逻辑 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3389 | Kill Switch 紧急停止开关 | 否决五级分类系统性风险/风控崩溃/AI自治熔断 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3390 | 强制减仓 Forced Position Reduction | 否决五级分类单日亏损超阈值/回撤超限 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3391 | 否决新开仓 Reject New Position | 否决五级分类VaR超限/集中度超限/流动性不足 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3392 | 否决单笔订单 Reject Single Order | 否决五级分类单笔金额超限/涨跌停买入 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3393 | 建议性告警 Advisory Alert | 否决五级分类风险指标接近阈值/漂移检测预警 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3394 | Pod级止损机制 Pod-Level Stop Loss | **Pod级止损机制**（对齐 Citadel/Millennium/Point72多管理人平台实践）： | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3395 | 否决执行引擎 Veto Execution Engine | §3.2否决执行机制同步拦截<50ms P99 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3397 | Kill Switch多路径激活 Kill Switch Multi-Path Activation | AI自动/人工一键/定时熔断/外部信号四路径 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3398 | 四层隔离防护 Four-Layer Isolation | §3.3否决与策略逻辑的隔离代码/数据/权限/审计 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3399 | ATR动态止损与Bayesian参数优化模型 ATR Dynamic Stop-Loss Model | 基于波动率的动态止损+参数优化框架 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3400 | 独立风险数据管道 Independent Risk Data Pipeline | §4.1风险数据流独立于交易数据流BCBS 239 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3401 | 风险指标计算引擎 Risk Indicator Computing Engine | 计算层VaR/CVaR/ES/密度VaR/共形VaR | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3402 | 漂移检测引擎 Drift Detection Engine | │  [漂移检测引擎] ────→ PSI/KS/Wasserstein/ADWIN/CUSUM   │ | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3403 | 压力测试引擎 Stress Test Engine Risk | 计算层情景P&L/流动性压力/传导/反向RST | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3404 | Agent行为监控 Agent Behavior Monitor | 计算层ASI+AST+MCP行为边界/涌现/串谋 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3406 | 风险仪表盘 Risk Dashboard | 消费层日频风险报告 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3407 | 告警系统 Alert System | 消费层风险事件+漂移告警 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3408 | 日度风险摘要 Daily Risk Summary | §4.3风险报告每日收盘VaR/CVaR/因子暴露 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3409 | 周度风险深度 Weekly Risk Deep Report | §4.3风险报告每周五压力测试+漂移趋势 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3410 | 月度风险治理 Monthly Risk Governance | §4.3风险报告月末风控参数变更审计 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3411 | 四级审批流 Four-Level Approval Flow | §5.1风控规则变更审批L1紧急→L2参数→L3规则→L4架构 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3412 | 三平面一致性 Three-Plane Consistency | §5.2风控参数版本管理代码/配置/运行时一致性 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3413 | 不操纵市场规则 No Market Manipulation Rules | §6.1 A股合规规则代管禁止幌骗/分层/自交易 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3414 | 幌骗检测 Spoofing Detection | 禁止幌骗下单意图校验+撤单率监控 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3415 | 分层操纵检测 Layering Detection | 禁止分层操纵多档位挂单模式检测 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3416 | 自交易检测 Self-Trading Detection | 禁止自交易账户内对倒检测 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3417 | 程序化交易合规 Programmatic Trading Compliance | **程序化交易合规**（对齐 2025.7《程序化交易管理实施细则》+ 2026.4.7新版实施细则+ 2026.1《沪深股通程序化交易报告指引》+ 证监会吴清2026.3两会表态）： | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3418 | 私募基金合规 Private Fund Compliance | 证监会信息披露办法2026.9.1生效 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3419 | 信息不对称期与操纵行为检测模型 Information Asymmetry Detection Model | 庄股操作识别量化框架ESMA MABUM | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3420 | A股风险日历 A-Share Risk Calendar | §6.4可预测周期性风险事件日历 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3421 | 漂移检测与风险闭环 Drift Detection Risk Loop | §7事前PSI→事中适应→事后重训 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3422 | 交易绩效归因与策略退化检测模型 Performance Attribution Model | Brinson模型归因+IC衰减检测+自动降权 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3424 | Autoencoder重构异常检测 Autoencoder Anomaly Detection | 深度学习异常检测训练正常数据极端事件重构误差飙升 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3425 | GAN对抗检测 GAN Adversarial Detection | / GAN对抗检测 / Generator生成正常分布，Discriminator检测偏离分布的极端模式 / '未知的未知'模式(不依赖预定义黑天鹅库) / 训练不稳定；生成质量依赖数据 / L3压力测试增强方法 / | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3426 | Transformer时序异常 Transformer Time-Series Anomaly | 深度学习异常检测注意力机制捕捉多变量时序异常 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3427 | 跨市场传导模型 Cross-Market Transmission Model | §14.2港股→A股/美股→A股/期货→现货/汇率→A股 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3428 | 流动性危机模拟 Liquidity Crisis Simulation | §14.3成交量骤降/买卖价差扩大/T+1锁定风险 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3429 | 反向压力测试引擎 Reverse Stress Testing Engine | §14.4从崩溃阈值反推致崩溃情景 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3430 | 二阶效应与传染模型 Second-Order Effect Contagion Model | §14.5流动性螺旋/相关性传染/策略拥挤踩踏/信心传染 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3431 | 凸性预算框架 Convexity Budget Framework | **尾部风险对冲——凸性预算框架**（对齐 Jabłecki et al. 2026 + Landl 2026.3 + StockAlpha 2026.2）： | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3432 | 相关性体制转换 Correlation Regime Switching | 1970-82滞胀/2000-21负相关/2022通胀冲击/2026危机窗口 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3433 | ESRB 14个AI风险放大向量 ESRB 14 AI Risk Amplification Vectors | 欧洲系统性风险委员会系统性识别14个渠道 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3435 | 保障缺口管理 Guarantee Gap Management | §15.2 AI概率可靠性与所需可执行保证间差距 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3436 | 治理漂移防护 Governance Drift Protection | §15.3自治权渐进扩张但治理未同步更新 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3437 | Agent行为监控 Agent Behavior Monitoring | §15.4 OWASP ASI 10类+串谋+隐性串谋监控 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3438 | Agent红队测试 Agent Red Team Testing | **Agent红队测试与防御**（对齐 FinJailbreak Li et al. AAAI 2026 + AutoRedTrader Liu et al. 2026.5 + FinRedTeamBench Dimino et al. 2 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3439 | 金融治理越狱 FinJailbreak | Agent红队攻击向量领域特定对抗提示绕过安全对齐 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3440 | 合成虚假信息注入 AutoRedTrader | Agent红队攻击向量行为偏差操纵+文本微扰 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3441 | BFSI领域自适应红队 FinRedTeamBench | Agent红队攻击向量多轮自适应交互+领域危害分类 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3442 | 交易管线扰动 TradeTrap | Agent红队攻击向量单组件微扰传播全决策闭环 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3443 | ARS双轨结算模型 ARS Dual-Track Settlement | §15.5 Fee Track+Principal Track金融级保障 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3444 | Fee Track费用轨道 Fee Track | ARS双轨仅涉及服务报酬的任务托管Escrow机制 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3445 | Principal Track本金轨道 Principal Track | ARS双轨涉及资金操作的任务承保+抵押机制 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3446 | Named Accountability命名问责人 Named Accountability | §15.6每个Agent必须有命名问责人 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3447 | Risk Management Core 风险管理核心 | / MOD-L04-001 / Risk Management Core / 🔧部分实现 / risk_manager/risk_limits/stop_loss/risk_validator+G10/G11/G12门禁 / §3+§5+§ | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3562 | 反推致崩溃情景 Reverse Derive Crash Scenario | / 反向压力测试 / 从崩溃阈值反推致崩溃情景 / '什么情景会导致组合亏损>15%?'→反推所需冲击组合 / 每季度 / | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3563 | 评估情景合理性 Evaluate Scenario Plausibility | 反向压力测试步骤判断反推情景是否合理但极端 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3564 | 设计防护措施 Design Protection Measures | 反向压力测试步骤为每个合理致崩溃情景设计预防/缓解措施 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3565 | DPG七场景 DPG Seven Scenarios | / 程式化情景 / 对关键风险因子施加标准化冲击 / DPG七场景：利率±100bp / 波动率±20% / 股指±10% / 汇率±6% / 每月 / | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3566 | 管线验证 Pipeline Validation | 重训门禁全链路端到端 Walk-Forward+模拟盘 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3567 | ARA五项原则 ARA Five Principles | 治理速度≥自治速度/持续验证/最小代理权/基础设施层Kill Switch/自适应治理参数 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3568 | ARA治理方程 ARA Governance Equation | 期望损失=(攻击概率×Agent自治度×资产暴露)÷治理系数 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3569 | ARS状态机语义 ARS State Machine Semantics | 请求→协商→执行→评估→结算确定性状态机用户损失减少61% | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3570 | TCP+Robbins-Monro偏移 TCP-RM | / TCP-RM / 同上 / TCP+在线Robbins-Monro偏移 / 实时调整覆盖率 / 需要调参(学习率γ) / | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3571 | 自适应共形推断 Adaptive Conformal Inference | / TCP / Aich et al. (2026) arXiv:2507.05470 / 分位数预测器+滚动split-conformal校准层 / 非平稳时序下覆盖率接近目标 / 有足够校准窗口(≥250日) / | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3572 | Portfolio CP 组合共形预测 | / Portfolio CP / Jia & Han (DMO-FinTech 2026) HKUST(Guangzhou) / 共形预测估计VaR→组合优化 / 分布无关+覆盖率保证+可整合任何回归方法 / 短卖约束+投资者指定约束 / | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3573 | QRF+Conformal 分位数回归森林+共形 | / QRF+Conformal / Wang et al. (2026.2) Renmin Univ / 分位数回归森林+OSOA框架+共形校准层 / 实时VaR+一致性+覆盖率有效性理论保证 / 需离线模拟训练+≥250日校准窗口 / | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3574 | Phase 1参数化高斯混合 Phase 1 Parametric Gaussian Mixture | / Phase 1 / 参数化(高斯混合) / CRPS<基准10% / 概率校准度偏离对角线<5% / | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3575 | Phase 2 QNN量子神经网络 Phase 2 QNN | / Phase 2 / QNN(量子神经网络近似) / CRPS<Phase1 / 尾部校准VaR覆盖率误差<2% / | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3576 | Phase 3非参数化KDE Phase 3 Non-parametric KDE | / Phase 3 / 非参数化(KDE/核密度) / CRPS<Phase2 / 8态概率从PDF积分派生 / | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3577 | 追踪止损 Trailing Stop | / 追踪止损 / Trailing_Stop = max(历史最高价 - k × ATR, 前一日止损位) / 只上移不下移，锁定盈利 / | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3578 | Grid Search 网格搜索 | / Grid Search / 遍历k∈[1.0, 5.0]步长0.5，计算各k的Sharpe/MaxDD / 全局搜索但计算量大 / | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3579 | Bayesian优化 Bayesian Optimization | / Bayesian优化 / 用高斯过程建模k→Sharpe映射，聚焦有前景区域 / amhieu(2025)：比Grid Search更高效 / | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3580 | Walk-Forward验证 Walk-Forward Validation | / Walk-Forward验证 / 样本内优化k→样本外验证→滚动前进 / 防止过拟合 / | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3581 | 体制自适应 Regime Adaptive | / 体制自适应 / 不同市场体制（趋势/均值回归/混沌）使用不同k / 趋势市k=3-4（宽止损）/ 均值回归市k=1.5-2（紧止损） / | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3582 | ATR动态止盈 ATR Dynamic Take Profit | / ATR动态止盈 / Target = Entry + m × ATR / m通常为k的1.5-2倍（盈亏比>1.5） / | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3583 | 分批止盈 Batch Take Profit | / 分批止盈 / 1/3仓位在1R止盈+1/3在2R+1/3追踪止损 / R=初始风险(Entry-Stop) / | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3584 | 时间止损 Time Stop Loss | ATR止盈策略持仓N日未达1R盈利→平仓适用于短期动量策略 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3585 | LVaR价差模型 LVaR Spread Model | / LVaR(价差模型) / LVaR = VaR + ½ × S × W / 正常市场+小仓位 / S=买卖价差(%), W=仓位价值 / | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3586 | LVaR Amihud冲击模型 LVaR Amihud Impact Model | / LVaR(Amihud冲击模型) / LVaR = VaR + ILLIQ × (Q/V)^α / 大仓位+非标资产 / ILLIQ=Amihud比率, Q=交易量, V=日均成交量, α≈0.5 / | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3587 | LVaR EVT尾部模型 LVaR EVT Tail Model | / LVaR(EVT尾部模型) / LVaR = VaR + EVT_尾部流动性溢价 / 极端行情+流动性枯竭 / EVT拟合流动性指标尾部分布→尾部风险溢价 / | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3588 | 空窗期定义 Window Period Definition | / 空窗期定义 / 定期报告披露间隔>90天的时期 / 11月-次年4月30日 / | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3589 | 空窗期异常 Window Period Anomaly | / 空窗期异常 / 空窗期内换手率/波动率/收益率偏离正常水平 / z-score>2=异常 / | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3590 | 对敲交易检测 Wash Trade Detection | 操纵行为检测间隔≤5秒+偏离≤1%+占比≥5%沪深交易所标准 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3591 | 尾盘操纵检测 End-of-day Manipulation Detection | 操纵行为检测最后5分钟价格变化>2%+成交量集中疑似操纵 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3592 | 收益归因 Return Attribution | **核心逻辑**: 交易绩效监控不只是'看盈亏'，而是**Performance Attribution**（归因分析）+ **Strategy Degradation Detection**（策略退化检测）。因子IC衰减=策略退化，需要自 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3593 | 自动降权 Auto De-weighting | / 自动降权 / 策略退化时自动将权重降为0 / Man Group AlphaGPT实践 / | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3594 | AI自动触发 AI Auto Trigger | / 熔断器 / 电路断路器可在微秒内平仓 / 'hair-trigger'风险切割 / 熔断器模式(5次/60秒→OPEN) / | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3595 | 人工一键触发 Manual One-click Trigger | / 熔断器 / 电路断路器可在微秒内平仓 / 'hair-trigger'风险切割 / 熔断器模式(5次/60秒→OPEN) / | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3597 | 外部信号触发 External Signal Trigger | / 外部信号触发 / <1s / A9运维架构告警信号 / 基础设施层 / | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3598 | L1代码隔离 L1 Code Isolation | / L1 代码隔离 / 风控代码与策略代码分属不同域(D-RISK vs D-SIGNAL/D-PF-*) / 域边界+依赖方向约束(INV-008) / | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3599 | L2数据隔离 L2 Data Isolation | 四层隔离防护风险数据流独立于交易数据流独立管道+独立计算 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3600 | L3权限隔离 L3 Permission Isolation | / L3 权限隔离 / 风控引擎只读策略信号，只写否决指令 / RBAC+最小权限 / | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3602 | 独立风险数据接入 Independent Risk Data Access | │  iFind数据 ────┤──→ [独立风险数据接入] ──→ 风险数据清洗  │ | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3603 | 风险数据清洗 Risk Data Cleaning | 风险数据管道数据源层清洗+质量校验+属性级血缘 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3604 | 因子分布检测 Factor Distribution Detection | 事前PSI检测矩阵PSI+KS日频PSI>0.25→模型降级 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3605 | 特征分布检测 Feature Distribution Detection | 事前PSI检测矩阵Wasserstein距离+KS日频W>0.2→特征工程审查 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3606 | 模型输出检测 Model Output Detection | 事前PSI检测矩阵预测分布稳定性+CUSUM日频偏移>20%→模型审查 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3607 | 上游数据检测 Upstream Data Detection | 事前PSI检测矩阵Schema校验+空值率+格式实时空值率>5%→数据源切换 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3608 | L1共形校准更新 L1 Conformal Calibration Update | 事中在线适应三层机制TWC/RWC校准窗口滚动更新每日≤5秒 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3609 | L2模型降级 L2 Model Degradation | / L2 模型降级 / 模型从'自主执行'降为'仅建议' / PSI>0.25 / 性能衰减>5% / ≤1秒 / 降级后所有决策需人工确认 / | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3610 | L3风控参数收紧 L3 Risk Parameter Tightening | 事中在线适应三层机制VaR限额收紧+仓位上限下调≤5秒 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3611 | 否决日志 Veto Log | / 否决日志 / 时间/规则/触发值/被否决指令 / ≥7年 / 哈希链+独立存储 / | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3612 | 参数变更日志 Parameter Change Log | / 参数变更日志 / 变更前/后/审批人/时间/理由 / ≥7年 / 哈希链+独立存储 / | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3613 | Kill Switch日志 Kill Switch Log | / Kill Switch日志 / 触发条件/时间/恢复时间/人工确认 / ≥7年 / 哈希链+独立存储 / | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3614 | 漂移检测日志 Drift Detection Log | / 漂移检测日志 / PSI/KS/CUSUM值/检测时间/处置动作 / ≥3年 / 哈希链 / | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3615 | Agent行为日志 Agent Behavior Log | / Agent行为日志 / 行为记录/越界检测/OWASP ASI分类/处置动作 / ≥3年 / 哈希链 / | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3616 | Pod级止损日志 Pod-level Stop Loss Log | 风控审计策略ID/回撤值/止损级别/处置动作保留≥3年哈希链 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3617 | 港股→A股传导 HK-to-A-Share Transmission | / 港股→A股 / 恒生指数/AH溢价/北向资金 / T+0(盘中) / AH联动股受冲击 / 降AH联动股权重 / | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3618 | 美股→A股传导 US-to-A-Share Transmission | / 美股→A股 / 隔夜美股/VIX/美债收益率 / T+1(次日开盘) / 开盘跳空风险 / 预调仓位(盘前) / | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3619 | 期货→现货传导 Futures-to-Spot Transmission | 跨市场传导渠道股指期货升贴水/基差T+0盘中期货领跌/领涨 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3620 | 汇率→A股传导 FX-to-A-Share Transmission | 跨市场传导渠道人民币汇率/外汇储备T+0~T+1资金流入流出 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3621 | 成交量骤降模拟 Volume Drop Simulation | 流动性危机模拟滑点放大0.1%→5%+订单阻塞90%无法成交 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3622 | 买卖价差扩大模拟 Spread Widening Simulation | 流动性危机模拟价差扩大5-10倍+深度枯竭退出成本估算 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3623 | T+1锁定风险模拟 T+1 Lock Risk Simulation | 流动性危机模拟极端事件当日无法卖出+次日跳空隔夜风险敞口 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3624 | 相关性传染 Correlation Contagion | / 相关性传染 / 板块A暴跌→恐慌蔓延→板块B/C跟跌 / 条件相关性模型：危机时相关性趋近1 / 相关性崩塌模式(BS-002)自动处置 / | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3625 | 策略拥挤踩踏 Strategy Crowding Stampede | / 策略拥挤踩踏 / 因子同质化→同步信号→同步卖出→价格崩塌 / AFMM执行耦合参数+策略指纹相似度 / 策略多样性约束(VR-013)+执行去耦(随机延迟) / | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3626 | 信心传染 Confidence Contagion | / 信心传染 / 外围暴跌→国内恐慌→资金外流→进一步暴跌 / 跨市场传导模型(§14.2)+情绪指标 / 跨市场传导模式(BS-005)自动处置 / | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3627 | Carry持有成本 Carry | 凸性预算框架维持对冲的预期年化拖累期权费+融资成本/名义敞口 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3628 | Convexity凸性收益 Convexity | > 尾部风险不是保险问题，是凸性问题(Landl 2026.3)。传统对冲(买Put)面临'Greek Trilemma'：Carry(持有成本) vs. Convexity(凸性收益) vs. Reliability(危机可靠性)——三者 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3629 | Reliability危机可靠性 Reliability | > 尾部风险不是保险问题，是凸性问题(Landl 2026.3)。传统对冲(买Put)面临'Greek Trilemma'：Carry(持有成本) vs. Convexity(凸性收益) vs. Reliability(危机可靠性)——三者 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3630 | 决策正确性缺口 Decision Correctness Gap | 保障缺口管理AI概率性95%准确率vs 100%风险底线风控否决权兜底HC-RISK-01 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3631 | 行为可预测缺口 Behavior Predictability Gap | 保障缺口管理AI非确定性LLM输出vs行为在预期边界内行为边界监控+Kill Switch | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3632 | 故障可恢复缺口 Failure Recoverability Gap | 保障缺口管理AI可能产生级联错误vs故障隔离+快速恢复熔断器模式+降级策略 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3634 | 资金安全缺口 Fund Safety Gap | 保障缺口管理Agent可能执行非预期交易vs资金损失有补偿机制ARS双轨结算 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3635 | 自治等级未经审批升级 Autonomy Level Unauthorized Upgrade | 治理漂移场景自治等级变更审计+运行时等级校验需人工审批 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3636 | 风控参数渐进放松 Risk Parameter Gradual Relaxation | / 风控参数渐进放松 / 风控参数趋势分析+偏差检测 / 风控参数变更需人工审批(HC-RISK-04) / | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3637 | 人类监督频率降低 Human Supervision Frequency Decrease | / 人类监督频率降低 / 人类确认频率监控+超时告警 / 人类确认不可跳过(HC-RISK-02) / | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3638 | 静态治理规则过时 Static Governance Rules Outdated | ### §15.3 治理漂移(Governance Drift)防护 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3639 | 承保人 Underwriter | / 承保人(Underwriter) / 独立第三方评估Agent风险+收取保费 / 无独立第三方(单人系统) / ❌不能建——门禁条件：AUM增长到可聘请独立风控顾问 / | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3640 | 抵押 Collateral | / Principal Track / 涉及资金操作的任务(如交易执行/仓位调整) / 承保(Underwriting)+抵押(Collateral)：承保人评估风险+要求抵押，失败时补偿 / AI执行交易→风控否决权兜底(HC-RISK- | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3641 | 托管 Escrow | ARS要素报酬预存+条件释放人工确认机制作为人工托管 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3642 | 保费 Premium | ARS要素基于Agent风险等级的动态保费本系统无保费机制 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3903 | Tick风控 Tick风控检查 | Hot平面2ms延迟预算CPU核8-11 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3904 | 订单风控 订单风控检查 Risk Control Order | Hot平面3ms延迟预算 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3952 | 买入后即时验证与快速纠错模型 Post-Entry Validation | 买入后5-15分钟即时验证Intraday Momentum | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3953 | 系统性风险分级预警与尾部风险管理模型 Tail Risk Management | VaR CVaR压力测试分级预警递进风控 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4102 | 违约风险 Default Risk | > 因交易对手违约导致损失的风险。当前系统为A股纯股票多头+单人管理，无OTC衍生品/融资融券/回购等交易对手敞口。D-RISK-09 Counterparty Risk Manager已定义但当前❌不能建——门禁条件未满足。 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4103 | 结算风险 Settlement Risk | 交收失败监控结算周期跟踪结算失败率未结算敞口 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4104 | 发行人体质恶化 Issuer Deterioration | 财务指标监控信用评级变动违约距离Merton模型DD | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4105 | ESRB顺周期性风险向量 ESRB Procyclicality | 市场压力期间AI羊群行为策略同质化检测VR-013 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4106 | ESRB速度风险向量 ESRB Speed | 亚毫秒级连锁故障本系统小于10笔秒非高频天然免疫 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4107 | ESRB不透明性风险向量 ESRB Opacity | 黑箱决策链C-030决策可解释性审计链每笔决策可溯源 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4108 | ESRB模型同质性风险向量 ESRB Model Homogeneity | 相关故障模式策略指纹相似度相似度大于90%否决上线 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4109 | ESRB数据依赖风险向量 ESRB Data Dependency | 单一来源脆弱性数据源双源校验数据源切换空值率监控 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4110 | ESRB互联性风险向量 ESRB Interconnectedness | 放大的传染效应级联失败监控熔断器隔离OWASP ASI08 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4111 | ESRB运营风险向量 ESRB Operational Risk | AI系统故障健康检查心跳自动重启Kill Switch | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4112 | ESRB网络脆弱性风险向量 ESRB Cyber Vulnerability | 模型投毒记忆完整性校验ASI06哈希校验清除受污染记忆 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4113 | ESRB市场操纵风险向量 ESRB Market Manipulation | 复杂AI幌骗撤单率监控行为模式检测撤单率大于15%限制 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4114 | ESRB监管套利风险向量 ESRB Regulatory Arbitrage | AI驱动规避穿透监管审计不可篡改同一实控人合并计算 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4115 | ESRB集中风险向量 ESRB Concentration Risk | AI提供商垄断模型数据源多样性多源数据模型异质性约束 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4116 | ESRB过度信任风险向量 ESRB Overreliance | / 12 / 过度信任(Overreliance) / 顺境中AI优异表现→过度信任→增加风险承担+阻碍监督 / 人类确认不可跳过(HC-RISK-02)+自治等级上限(风险架构§15.1) / | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4117 | ESRB历史约束风险向量 ESRB History-Constrained | / 13 / 历史约束(History-Constrained) / AI依赖历史数据→无法应对未预见尾部事件→过度风险承担 / 反向压力测试(风险架构§14.4)+黑天鹅模式库(风险架构§14.1)+EVT尾部建模 / | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4118 | ESRB法律地位未定风险向量 ESRB Untested Legal Status | / 14 / 法律地位未定(Untested Legal Status) / AI行为法律责任归属不明→系统性风险 / Named Accountability(风险架构§15.6)+AI输出视为工具输出(风险架构§9) / | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4321 | Risk Manager 风控管理器(代码实现) | / l04_risk_management/risk_manager.py / RK-01 Risk Policy Manager / ✅已有 / | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4322 | Risk Validator 风控校验器(代码实现) | / l04_risk_management/risk_validator.py / RK-02 Pre-Trade Checker / ✅已有 / | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4323 | Stop Loss 止损(代码实现) | / l04_risk_management/stop_loss.py / RK-04 Stop Loss Engine / ✅已有 / | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4324 | Risk Metrics 风控指标(代码实现) | / shared/contracts/risk/risk_metrics.py / RK-03 指标定义 / ✅已有 / | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4325 | Kill Switch 紧急开关(代码实现) | / agent_rbac/kill_switch.py / RK-17 Kill Switch / ✅已有 / | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4326 | Kill Switch Latency Check 紧急开关延迟检查(代码实现) | / check_kill_switch_latency.py / INV-001 验证 / ✅已有 / | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4327 | Risk Params Consistency Check 风控参数一致性检查(代码实现) | / check_risk_params_consistency.py / INV-013 验证 / ✅已有 / | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4340 | Fake Rally Real Distribution 假拉升真出货 | 假动作模式-盘中快速拉升吸引追涨+拉升时大单卖出>买入 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4341 | Fake Support Real Lure 假护盘真诱多 | 假动作模式-权重股拉升稳定指数+题材股不动 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4342 | Fake Rebound Real Distribution 假反弹真派发 | 假动作模式-超跌后反弹看似见底+反弹缩量+底部筹码未加长 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4343 | Spoofing Detection 幌骗交易检测 | / Spoof概率 / 综合Spoofing检测模型输出 / CNN/Transformer分类器 / Spoof概率>85%→暂停追涨 / | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4344 | Related Account Coordination 关联账户协同性检测 | 协同交易检测-同步报撤单比例≥60%+方向一致性≥80% | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4345 | Information Asymmetry Window 信息不对称空窗期 | 操纵行为检测-定期报告披露间隔>90天的时期(11月-次年4月30日) | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4346 | Default Risk Validator 默认风控校验器(代码实现) | / l04_risk_management/implementations/default_risk_validator.py / RK-02 实现 / ✅已有 / | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4347 | Default Risk Limits Calculator 默认风险限额计算器(代码实现) | / l04_risk_management/implementations/default_risk_limits_calculator.py / RK-03 实现 / ✅已有 / | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4348 | Default Risk Manager Orchestrator 默认风控管理器编排器(代码实现) | / l04_risk_management/implementations/default_risk_manager_orchestrator.py / RK-01 编排 / ✅已有 / | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4349 | Default Position Limit Checker 默认持仓限额检查器(代码实现) | / l04_risk_management/implementations/default_position_limit_checker.py / RK-06 实现 / ✅已有 / | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4350 | Default Stop Loss Engine 默认止损引擎(代码实现) | / l04_risk_management/implementations/default_stop_loss_engine.py / RK-04 实现 / ✅已有 / | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4433 | Instant Order Rate Anomaly 瞬时申报速率异常 | / 瞬时申报速率异常 / 短时间内申报量远超正常水平 / 每秒申报笔数超15笔/秒(2026.4.7新规异常交易行为阈值，同高频交易认定标准) / Hard Block:自动限速+告警 / 交易所实施细则 / | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4434 | Frequent Instant Cancellation 频繁瞬时撤单 | / 频繁瞬时撤单 / 短时间内频繁申报和撤单 / 撤单率>15%(2026.4.7新规) / Hard Block:拒绝后续撤单+告警 / 交易所实施细则 / | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4435 | Frequent Push-Pull 频繁拉抬打压 | / 频繁拉抬打压 / 多只股票小幅拉抬打压 / 价格偏离度+成交量占比 / Hard Block:暂停交易+告警 / 交易所实施细则 / | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4436 | Short-time Large Volume 短时间大额成交 | / 短时间大额成交 / 同一机构多产品集中同向交易 / 合并持仓变动率 / Hard Block:限仓+告警 / 交易所实施细则 / | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4437 | Almgren-Chriss Impact Model Almgren-Chriss冲击模型 | / 参与率冲击模型 / ≤Almgren-Chriss模型计算的市场冲击合理比例(须≤5%上限，取两者较小值) / Almgren-Chriss冲击模型约束 / 行业最佳实践(5%为法规上限，模型计算值通常更低；与上行5%上限共同构成双重约 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4438 | Sequential Evaluation 顺序评估 | **规则评估策略**：顺序评估(Sequential Evaluation)——规则按优先级排序，顺序评估：首个触发的Hard Block即终止评估并拒绝；Soft Block暂停等待审批；Warning记录告警但不阻断评估，继续评估后续规 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4439 | Fail-Closed 引擎故障处置 | §7.6 Pre-Trade合规检查模式-引擎故障处置-合规规则引擎不可用时C-004默认拒绝所有订单(Fail-Closed) | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4440 | Spoofing 幌骗 | §7.7市场操纵防护-Spoofing幌骗-挂单-撤单模式识别+意图分析-C-004风控引擎实时检测(RK-02) | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4441 | Layering 分层 | §7.7市场操纵防护-Layering分层-多价位同方向虚假挂单检测-C-004风控引擎实时检测(RK-02) | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4442 | Wash Trade 洗盘 | / 洗盘(Wash Trade) / 自交易检测：同一实控账户互为对手方 / C-002执行域订单前检查(独立于C-004，因需跨账户数据)(→D-EX-CORE §7.4) / SEC Rule 10b-5；CFTC洗盘禁令 / | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4443 | Late Session Manipulation 尾盘操纵 | §7.7市场操纵防护-尾盘操纵-收盘前N分钟异常交易检测-C-004风控引擎(RK-03) | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4444 | Emergent Manipulation 涌现操纵模式 | §7.7 AI驱动操纵-涌现操纵模式-市场影响的严格责任-C-007闭环优化检测策略行为模式变化 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4445 | Volume-Price Consistency 量价一致性 | / 量价一致性 / 拉升段主动买入占比 / >65%（真拉升） / <40%（假拉升，对倒或卖单主导） / | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4446 | Dragon-Tiger List Verification 龙虎榜验证 | §7.8.2假动作识别量化信号-龙虎榜验证-机构/游资席位行为-机构买入真吸筹游资一日游+机构卖出假动作 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4447 | CER Cancellation-to-Execution Ratio 撤单成交比 | / CER（Cancellation-to-Execution Ratio） / 撤单量/成交量的比率 / CER>95%在100ms窗口内=高概率Spoofing / 个股CER>90%=假动作嫌疑→Hard Block拒绝追涨 / | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4448 | Order Life Duration 订单存续时间 | / Order Life Duration / 大单挂出后存续时间（毫秒） / 存续<100ms即撤=虚假挂单 / 大单存续<1秒即撤=虚假挂单嫌疑 / | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4449 | Spoof Probability Spoof概率 | / CER（Cancellation-to-Execution Ratio） / 撤单量/成交量的比率 / CER>95%在100ms窗口内=高概率Spoofing / 个股CER>90%=假动作嫌疑→Hard Block拒绝追涨 / | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4450 | Key Position Support Strength 关键点位护盘强度 | / 关键点位护盘强度 / 整数关口/前低附近的买一挂单量/日均成交额 / >5%且持续>30分钟=疑似护盘 / | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4451 | Spoofing Trade Detection 幌骗交易检测(操纵行为) | §7.10.2操纵行为检测-幌骗交易-偏离≥2%+申报量≥10%+5秒内撤单≥80%-沪深交易所(2025.7)标准 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4452 | Wash Trade Detection 对敲交易检测(操纵行为) | §7.10.2操纵行为检测-对敲交易-间隔≤5秒+偏离≤1%+占比≥5%-沪深交易所(2025.7)标准 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4453 | Late Session Manipulation Detection 尾盘操纵检测 | §7.10.2操纵行为检测-尾盘操纵-最后5分钟价格变化>2%+成交量集中-疑似操纵 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4454 | VaR Phase 1 VaR三阶段Phase 1 | §6设计决策-VaR三阶段演进-Phase 1-历史模拟法VaR(基础阶段) | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4455 | VaR Phase 2 VaR三阶段Phase 2 | §6设计决策-VaR三阶段演进-Phase 2-密度感知VaR+共形预测(增强阶段) | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4456 | VaR Phase 3 VaR三阶段Phase 3 | §6设计决策-VaR三阶段演进-Phase 3-极值理论EVT+蒙特卡洛(高级阶段) | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4457 | SignalAggregator 信号聚合器 | §3.5跨域铁三角-SignalAggregator-信号聚合器-D-SIGNAL→D-PF-CORE/D-RISK | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4458 | OMS Order Management System 订单管理系统 | §3.5跨域铁三角-OMS-订单管理系统-D-PF-CORE/D-RISK→D-EX-CORE | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4459 | Risk Intercept 风控拦截 | §4风控熔断因果链-风控拦截-Pre-Trade检查未通过→订单被拦截 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4460 | Position Circuit Breaker 持仓熔断 | §4风控熔断因果链-持仓熔断-持仓超限→持仓熔断触发 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4461 | A-Share Stop Loss A股止损 | §4风控熔断因果链-A股止损-A股特有止损规则触发 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4462 | L1 Pre-Trade L1盘前拦截 | / 职责 / **自适应风控**。Pre/Post-Trade风控+实时监控+熔断+Kill Switch+VaR+压力测试+拥挤度检测+黑天鹅模式库——资金安全的决策中枢 / | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4463 | L2 Real-Time L2盘中监控 | §0三层防线-L2 Real-Time盘中监控-实时持仓+风险指标监控 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4464 | L3 Post-Trade L3盘后审计 | / 职责 / **自适应风控**。Pre/Post-Trade风控+实时监控+熔断+Kill Switch+VaR+压力测试+拥挤度检测+黑天鹅模式库——资金安全的决策中枢 / | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4465 | Rule Engine 规则引擎(双引擎) | §0双引擎-规则引擎-确定性硬阻断-合规规则硬编码自动执行 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4466 | Statistical Engine 统计引擎(双引擎) | §0双引擎-统计引擎-概率性告警-基于统计模型的风险预警 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4495 | A-Share Stop Loss 6 Patterns A股特色止损6种模式 | / 2026-05-26 / A股特色止损6种模式 / 固定比例-7%/支撑破位/逻辑失效/竞价不及预期/分时破位/板块退潮 / A股T+1制度+行为金融学 / | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4496 | A-Share Systemic Risk 5 Signals A股系统性风险5信号 | / 2026-05-26 / A股系统性风险5信号 / 融资盘/量化踩踏/流动性危机/政策转向/外围冲击 / A股市场特色 / | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4497 | Rule Engine Configurable 规则引擎可配置化 | / 2026-05-26 / 规则引擎可配置化 / YAML/DSL规则文件+运行时加载，1500模块规模下硬编码不可维护 / 规则引擎标准实践 / | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4498 | Dual-Engine Routing 双引擎路由 | / 2026-05-26 / 双引擎路由 / 确定性规则引擎→硬阻断/概率性统计引擎→告警+建议 / Basel III / | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4499 | VaR Phase 1 Parameter Method VaR Phase 1参数法 | / Phase 3 / Basel III三角验证+乘数因子+压力VaR / 合规级风控 / 满足监管要求 / Phase 1+2 / | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4500 | VaR Phase 2 Monte Carlo VaR Phase 2蒙特卡洛法 | / Phase 3 / Basel III三角验证+乘数因子+压力VaR / 合规级风控 / 满足监管要求 / Phase 1+2 / | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4501 | VaR Phase 3 Basel III VaR Phase 3 Basel III三角验证 | / Phase 3 / Basel III三角验证+乘数因子+压力VaR / 合规级风控 / 满足监管要求 / Phase 1+2 / | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4808 | Distribution Fitting Engine 分布拟合引擎 | 旧子模块归并-→D-RISK | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4886 | TailRiskManagement 灾难逃生 | VaR/CVaR/压力测试5级预警+递进风控动作 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4938 | Market Risk 市场风险 | VaR/CVaR/ES/压力测试/情景分析/密度感知VaR/共形VaR | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4939 | Model Risk 模型风险 | SR 26-2/5类漂移检测/CUSUM/过拟合防护/训练-服务一致性 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4940 | AI/Agent Risk AI/Agent风险 | OWASP ASI+AST+MCP完整映射 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4941 | Risk Veto 风险否决权 | / — / 风险否决权 / 13条主规则VR-001~013+KillSwitch多路径激活+否决与策略逻辑隔离 / ✅ / | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4942 | A-Share Compliance Custody A股合规代管 | 不操纵市场/持仓限额/涨跌停约束/A股风险日历 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4943 | Counterparty Risk 交易对手风险 | 需衍生品业务 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4944 | Credit Risk 信用风险 | 需债券持仓 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4945 | ESG Risk ESG风险 | 需ESG数据源 | D_RISK | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-RSK-014 | Black Swan Pattern Library / 黑天鹅模式库 | 像2015股灾、2020疫情底这种极端行情，现有风控挡不住。这个库把历史极端事件存成模式，实盘遇到相似走势自动预警并触发熔断，保命用的。 | D_RISK | 延后（deferred） | q2 无需求驱动 | P1 | 实盘出现单日跌幅>5%的极端行情 等3条 | 2027-01-31 |
| CAND-PTC-001 | Pre-Trade Checker / 盘前统一检查器 | 下单前先查一遍：持仓够不够、资金够不够、有没有违规。但这功能已有三个模块组合起来做了，再单建一个等于重复造轮子。 | D_RISK | 否决（rejected） | q1 已实现/重复 | P2 | risk_validation_bridge 出现性能瓶颈或校验漏项 等2条 | 2027-07-31 |

## 按四问卡点分组（为什么没开发）

> 四问过滤：q1已实现 / q2需求驱动 / q3域活着 / q4 AI替代。任一问「否」即不进 depgraph 设计态，登记在候选库。

### q1 已实现/重复（1 条）

| ID | 名称 | 大白话（干什么用） | 域 | 卡点理由 | 替代方案 |
|------|------|------|------|------|------|
| CAND-PTC-001 | Pre-Trade Checker / 盘前统一检查器 | 下单前先查一遍：持仓够不够、资金够不够、有没有违规。但这功能已有三个模块组合起来做了，再单建一个等于重复造轮子。 | D_RISK | rejected,q1已实现。除非 risk_validation_bridge 组合出现重大缺口,否则不再评估 | 维持现有 risk_validation_bridge 组合。代价:无,组合已完整 |

### q2 无需求驱动（1 条）

| ID | 名称 | 大白话（干什么用） | 域 | 卡点理由 | 替代方案 |
|------|------|------|------|------|------|
| CAND-RSK-014 | Black Swan Pattern Library / 黑天鹅模式库 | 像2015股灾、2020疫情底这种极端行情，现有风控挡不住。这个库把历史极端事件存成模式，实盘遇到相似走势自动预警并触发熔断，保命用的。 | D_RISK | 首次登记,待VaR Phase2就绪或实盘极端行情时重新评估 | 靠 RK-05 VaR 压力测试 + 人工判断。代价:极端行情响应慢 |

### 待评估（497 条）

| ID | 名称 | 大白话（干什么用） | 域 | 卡点理由 | 替代方案 |
|------|------|------|------|------|------|
| CAND-HARVEST-0072 | Risk Control 自适应风控 | C 004：自适应风控 | D_RISK | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-0074 | Systematic Stress Testing 系统性压力测试 | C 040：系统性压力测试 | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-0085 | Systematic Overfitting Protection 过拟合系统性防护 | C 033：过拟合系统性防护 | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-0092 | 黑天鹅模式库与预判 Black Swan Pattern Library and Prediction | C 038：黑天鹅模式库与预判 | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-0093 | 资金曲线自诊断与结构预警 Capital Curve Self-Diagnosis and Structure Warning | C 032：资金曲线自诊断与结构预警 | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-0176 | Risk Policy Manager风控策略管理 | / D-RISK-01 / Risk Policy Manager风控策略管理 / ✅ 能建 / 📋 项目内有蓝图编号MOD-L04-001部分建设 / 风控策略CRUD+版本管理+规则引擎 / | D_RISK | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-0177 | Pre-Trade Checker盘前检查 | / D-RISK-02 / Pre-Trade Checker盘前检查 / ✅ 能建 / 📋 项目内有蓝图编号MOD-L04-001部分建设 / 下单前5步检查链+幂等+Fail-Closed(50ms) / | D_RISK | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-0178 | Portfolio Risk Monitor持仓实时监控 | / D-RISK-03 / Portfolio Risk Monitor持仓实时监控 / ✅ 能建 / 📋 项目内有蓝图编号MOD-L04-001部分建设 / 持仓实时监控+VaR+回撤+告警 / | D_RISK | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-0179 | Stop Loss Engine止损引擎 | / D-RISK-04 / Stop Loss Engine止损引擎 / ✅ 能建 / 📋 项目内有蓝图编号MOD-L04-001部分建设 / 止损评估(4种模式)+Kill Switch触发/重置 / | D_RISK | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-0180 | Stress Test Engine压力测试引擎 | / D-RISK-05 / Stress Test Engine压力测试引擎 / ✅ 能建 / / 场景定义器/冲击传导器/损失聚合器 / | D_RISK | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-0181 | VaR Calculator VaR计算器 | / D-RISK-07 / VaR Calculator VaR计算器 / ✅ 能建 / / 参数法+历史模拟→蒙特卡洛GPU→Basel III三角验证。与§29.16共形VaR互补: D-RISK-07提供传统VaR基线, §29.16 | D_RISK | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-0182 | Risk Budget Allocator风险预算分配 | / D-RISK-10 / Risk Budget Allocator风险预算分配 / ✅ 能建 / / 优化求解器+风险贡献计算器+再平衡触发器 / | D_RISK | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-0183 | Risk Decomposition Engine风险分解引擎 | / D-RISK-12 / Risk Decomposition Engine风险分解引擎 / ✅ 能建 / / 因子贡献+残差+边际风险+成分风险分析 / | D_RISK | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-0184 | Concentration Risk Monitor集中度风险监控 | / D-RISK-13 / Concentration Risk Monitor集中度风险监控 / ✅ 能建 / / HHI计算+行业暴露+对手方集中度+预警 / | D_RISK | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-0185 | Risk Limit Manager风险限额管理 | / D-RISK-14 / Risk Limit Manager风险限额管理 / ✅ 能建 / / 限额定义/消耗追踪/预警分级/审批流 / | D_RISK | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-0186 | Credit Risk Engine信用风险引擎 | / D-RISK-20 / Credit Risk Engine信用风险引擎 / ❌ 不能建 / / 门禁: ①50万AUM无信用风险敞口 ②D-CROSS-ASSET域就绪 / | D_RISK | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-0187 | A-Share Stop-Loss Rule Engine A股特色止损 | / D-RISK-27 / A-Share Stop-Loss Rule Engine A股特色止损 / ✅ 能建 / / 6种止损模式+亏损限制(日2%/周5%/月10%) / | D_RISK | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-0188 | A-Share Systemic Risk Detector A股系统性风险检测 | / D-RISK-28 / A-Share Systemic Risk Detector A股系统性风险检测 / ✅ 能建 / / 5大信号(融资盘/量化踩踏/流动性/政策/外围) / | D_RISK | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-0189 | A-Share Loss Limit Enforcer A股亏损限额强制执行 | / D-RISK-30 / A-Share Loss Limit Enforcer A股亏损限额强制执行 / ✅ 能建 / / 日2%/周5%/月10%限额+强制停盘1-3天 / | D_RISK | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-0190 | Stop-Loss Engine止损引擎 | / D-RISK-94 / Stop-Loss Engine止损引擎(L04) / ✅ 能建 / 📋 项目内有蓝图编号MOD-L04-001部分建设 / 与D-RISK-04合并，统一止损规则/触发/执行/审计 / | D_RISK | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-0191 | 仓位限制预检器 Position | / D-RISK-12 / Risk Decomposition Engine风险分解引擎 / ✅ 能建 / / 因子贡献+残差+边际风险+成分风险分析 / | D_RISK | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-0192 | 保证金比例安全检查器 Security | / D-RISK-97 / 保证金比例安全检查器 / ❌ 不能建 / / 门禁: Long-Only无保证金交易 / | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-0193 | 风险指标体系定义器 Risk | / D-RISK-102 / 风险指标体系定义器 / ✅ 能建 / / VaR+CVaR+波动率+最大回撤+夏普+索提诺 / | D_RISK | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-0194 | 紧急停止安全确认 Security | / D-RISK-115 / 紧急停止安全确认 / ✅ 能建 / 📋 项目内有蓝图编号MOD-INF-001部分建设 / 紧急操作二次确认与审计日志 / | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-0641 | VaR Compute Data Prefetcher VaR计算数据预取器 | / D-DATA-44 / VaR Compute Data Prefetcher / VaR计算数据预取器(DuckDB读Parquet预取+预取缓冲区+预取策略+I/O瓶颈监控) / ✅能建。在D-RISK VaR计算中增加prefet | D_RISK | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-0671 | 历史数据代表性验证器 Historical Data Representativeness Validator | 历史窗口充足性+结构性断点检测+制度转换检测+数据新鲜度 | D_RISK | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-0672 | Risk Policy Persister 风控策略持久化 | / D-RISK-49 / Risk Policy Persister / 风控策略SQLite持久化+版本管理(risk_policy+risk_limit+risk_policy_version表) / ✅能建。当前风控策略已在代码中定 | D_RISK | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-0673 | 双时态PositionSnapshot管理器 Bitemporal Position Snapshot Manager | / D-RISK-81 / 双时态PositionSnapshot管理器 / bitemporal双时态PositionSnapshot+双时态查询/版本管理/一致性 / ✅能建。与§13 PIT双时态建模对齐(即§13的system_ti | D_RISK | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-0674 | VaR DuckDB历史模拟查询构建器 VaR DuckDB Query Builder | / D-RISK-82 / VaR DuckDB历史模拟查询构建器 / VaR用DuckDB历史模拟复用数据域Parquet+查询构建/优化/缓存 / ✅能建。当前VaR计算已使用DuckDB查询Parquet，增量改进：增加查询缓存+性能 | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-0675 | 风险指标计算数据源依赖管理器 Risk Metric Data Dependency Manager | 风险指标计算跨模块数据依赖管理+依赖图 | D_RISK | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-0712 | C-004 风控 Risk Control | 风控Level-2数据 | D_RISK | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-0718 | C-038 黑天鹅检测 Black Swan Detection | 黑天鹅检测VIX | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-0728 | 风控状态物化视图 Risk Status View | / 风控状态 / risk:status / Hash / 实时 / <5ms / | D_RISK | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-0749 | Risk Budget Allocator 风险预算分配器 | 风险预算分配优化求解器风险贡献计算器再平衡触发约束处理器 | D_RISK | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-0764 | Risk Policy Manager 风险策略管理器 | 风控策略CRUD版本管理策略状态机DRAFT ACTIVE DEPRECATED冲突检测 | D_RISK | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-0765 | Pre-Trade Checker 盘前检查器 | 5步检查链仓位限额行业集中度杠杆率合规规则Kill Switch Fail-Closed 50ms SLA | D_RISK | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-0766 | Portfolio Risk Monitor 组合风险监控器 | 持仓实时监控VaR回撤告警因子暴露计算相关性矩阵 | D_RISK | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-0767 | Risk Limit Manager 风险限额管理器 | 9种限额类型消耗追踪预警分级审批流 | D_RISK | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-0768 | Concentration Risk Monitor 集中度风险监控器 | HHI行业暴露监控申万31行业个股集中度实时计算集中度告警 | D_RISK | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-0769 | A-Share Stop-Loss Rule Engine A股止损规则引擎 | 6种A股止损固定比例7%关键支撑破位逻辑失效竞价不及预期分时破位板块退潮 | D_RISK | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-0770 | A-Share Systemic Risk Detector A股系统性风险检测器 | 5大信号融资盘平仓潮量化踩踏流动性危机政策转向外围冲击三级警报 | D_RISK | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-0771 | Drawdown Real-Time Tracker 回撤实时跟踪器 | 最大回撤实时跟踪三级阈值-5%WARNING -10%CRITICAL -15%EMERGENCY回撤恢复检测 | D_RISK | harvest待评估（likely_planned） |  |
| CAND-HARVEST-0772 | Crowding Risk Monitor 拥挤风险监控器 | 同质度检测器资金流监控器踩踏预警器拥挤度指标器跨策略传染网络 | D_RISK | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-0773 | Black Swan Pattern Library 黑天鹅模式库 | 极端事件模式识别历史重放预案匹配黑天鹅事件分类自动根因分析 | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-0774 | Tail Risk Monitor 尾部风险监控器 | EVT POT模型尾部依赖矩阵Copula跳跃检测极值预警FRTB尾部风险加价 | D_RISK | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-0775 | Kill Switch Integration Kill Switch集成 | 状态机OPEN CLOSED 3种触发条件冷却期30min多域通知Owner确认重置 | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-0776 | Fail-Closed Degradation Handler Fail-Closed降级处理器 | 检查超时拒绝Fail-Closed超时检测50ms SLA降级逻辑恢复逻辑降级统计 | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-0777 | Configurable Rule Engine 可配置规则引擎 | YAML DSL规则文件运行时加载规则版本管理热更新规则测试沙箱规则回滚 | D_RISK | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-0778 | Post-Trade Daily Auditor 盘后日终审计器 | 日终PnL对账归因偏差检测合规报告生成日终检查清单问题追溯修正 | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-0995 | Scenario Analyzer 情景分析器 | 情景分析器：假设情景+敏感性分析+传染效应 | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-0996 | Liquidity Risk Monitor 流动性风险监控器 | 流动性风险监控：买卖价差+深度+冲击成本+流动性评分 | D_RISK | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-0997 | Risk Breach Logger 风险违规日志 | 风险违规日志：违规事件记录+分类+升级+追踪 | D_RISK | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-0998 | Counterfactual Analyzer 反事实分析器 | 反事实分析器：假设替代决策+影响量化+归因 | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-0999 | Risk Rule DSL Compiler 风控规则DSL编译器 | 风控规则DSL编译器：DSL→可执行规则+语法校验 | D_RISK | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1000 | Risk Dashboard Generator 风险仪表盘生成器 | 风险仪表盘生成器：实时风险可视化+KPI+趋势 | D_RISK | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1001 | Risk Report Auto-Generator 风险报告自动生成器 | 风险报告自动生成器：日/周/月风险报告+模板 | D_RISK | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1002 | Risk Policy Backtester 风控策略回测器 | 风控策略回测器：策略历史回测+效果评估 | D_RISK | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1003 | Limit Consumption Predictor 限额消耗预测器 | 限额消耗预测器：限额消耗趋势+预警+建议 | D_RISK | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1004 | Leverage Dynamic Manager 杠杆动态管理器 | 杠杆动态管理器：杠杆率动态调整+约束+监控 | D_RISK | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1005 | A-Share Stock Blacklist Manager A股股票黑名单管理器 | A股股票黑名单管理器：ST/退市/违规+自动更新 | D_RISK | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1006 | A-Share Stop-Loss/Circuit Breaker Series A股特色止损/熔断系列 | 逆向专用止损/系统性风险三级告警/首分钟止损/级联熔断等(8项) | D_RISK | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1007 | VaR Enhancement Series VaR增强系列 | 正态性检验/方法差异分析/快速预筛/精确确认/并发编排/交叉验证等(8项) | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-1008 | Permission/Idempotency/Kill Switch/Approval Series 权限/幂等/Kill Switch/审批系列 | 持仓写入权限/幂等保证/冷却期/审批网关/检查链编排等(11项) | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-1009 | VaR Scheduling/Concentration/ATR/Monte Carlo Series VaR调度/集中度/ATR/蒙特卡洛系列 | VaR重算调度/行业集中度/ATR动态止损/蒙特卡洛精度/协方差分解等(14项) | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-1010 | YAML/SQLite/SLA/Contract/Migration Series YAML加载/SQLite/SLA/契约/迁移系列 | YAML运行时加载/SQLite Schema/50ms SLA/契约提供者/迁移适配器等(15项) | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-1011 | Gate/Dashboard/Profile/DSL/Warehouse Series 门禁/仪表盘/画像/DSL/仓储系列 | 策略相关性门禁/杠杆限额门禁/风险画像/DSL引擎/值对象/迁移适配等(33项) | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-1020 | Risk Report Engine 风险报告引擎 | / D-REPORTING-08 / Risk Report Engine / 风险报告引擎(日度/周度/事件/月度4类风险报告生成)。消费D-RISK诊断结果 / ✅可建 / — / | D_RISK | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1117 | Risk Assessment 风险评估 | 风控Agent技能风险评估ACTIVE | D_RISK | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1318 | Trading Behavior Compliance Detector 交易行为合规检测器 | 四类异常交易检测：瞬时申报速率异常+频繁瞬时撤单+频繁拉抬打压+短时间大额成交 | D_RISK | harvest待评估（likely_planned） |  |
| CAND-HARVEST-1319 | Limit Up/Down Trading Constraint Executor 涨跌停交易约束执行器 | 涨停板不买入+跌停板不卖出；RK-02 Pre-Trade Checker实时价格检查 | D_RISK | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1320 | Trading Rate Constraint Executor 交易速率约束执行器 | 单标的成交量占比≤5%+Almgren-Chriss冲击模型约束+订单停留≥50微秒 | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-1321 | Position Limit Compliance Detector 持仓限额合规检测器 | 单一持仓上限≤5%NAV+举牌义务(架构预留)+ST股限制≤5%NAV | D_RISK | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1322 | Industry Concentration Compliance Detector 行业集中度合规检测器 | 行业偏离≤基准±10%(极端±15%，绝对上限30%)+风格暴露≤±0.3标准差 | D_RISK | harvest待评估（likely_planned） |  |
| CAND-HARVEST-1323 | Pre-Trade Three Block Mode Engine Pre-Trade三种阻塞模式引擎 | Hard Block(不可绕过)+Soft Block(合规官审批后可放行)+Warning(自动放行+记录) | D_RISK | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1324 | Market Manipulation Prevention Detector 市场操纵防护检测器 | Spoofing(幌骗)+Layering(分层)+Wash Trade(洗盘)+尾盘操纵检测 | D_RISK | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1325 | Fake Move Identification Signal Engine 假动作识别信号引擎 | 6种假动作识别+7维量化信号体系+Spoofing核心指标(CER/CancelVelocity/OrderLifeDuration) | D_RISK | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1326 | Collaborative Trading Behavior Detector 协同交易行为检测器 | 交易所标准(幌骗/对敲/关联账户协同/异常波动)+机构级+高级(GNN/TCN/联邦学习) | D_RISK | harvest待评估（likely_planned） |  |
| CAND-HARVEST-1327 | Information Asymmetry Period Manipulation Detector 信息不对称期操纵检测器 | 空窗期异常检测(定期报告间隔>90天)+操纵行为检测(幌骗/对敲/尾盘操纵) | D_RISK | harvest待评估（likely_planned） |  |
| CAND-HARVEST-1459 | Liquidity Evaporation 流动性蒸发 | 成交量骤降至30%+买卖价差扩大3倍→参与率约束收紧至5%+暂停做T | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-1460 | Correlation Collapse 相关性崩塌 | 跨板块相关性<0.1+分散化失效→集中度强制分散+降总仓位 | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-1461 | Volatility Eruption 波动率爆发 | VIX类指标>2σ+已实现波动率翻倍→仓位减半+暂停新开仓 | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-1462 | Margin Call Stampede 融资盘踩踏 | 两融余额单日降>10%+融资保证金上调→降杠杆敞口+暂停融资标的 | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-1463 | Cross-Market Contagion 跨市场传导 | 外围市场暴跌+北向资金大幅流出→降仓位至市场状态对应档位 | D_RISK | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1464 | Policy Black Swan 政策黑天鹅 | 交易规则突变/印花税调整/行业禁令→暂停受影响标的交易+评估 | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-1465 | Systemic Risk 系统性风险 | 多个BS模式同时触发→Kill Switch(P0) | D_RISK | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1806 | Pre-Trade Idempotency Guarantor 盘前幂等保证器 | 盘前幂等保证器：同步拦截+幂等检查+重复请求防护 | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-1807 | Pre-Trade Check Chain Orchestrator 盘前检查链编排器 | 盘前检查链编排器：5步检查链编排+顺序执行+首个Hard Block即终止 | D_RISK | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1808 | Pre-Trade 50ms SLA Monitor 盘前50ms SLA监控器 | 盘前50ms SLA监控器：延迟<50ms+超时检测+SLA告警 | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-1809 | Pre-Trade RiskCheckResult Router 盘前风控结果路由器 | 盘前风控结果路由器：检查结果分发+Hard Block/Soft Block/Warning三级路由 | D_RISK | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1810 | Order Generation Risk Pre-Check 订单生成风控前置 | 订单风控前置检查：订单生成前风控拦截+否决执行 | D_RISK | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1811 | Max Drawdown Real-Time Tracker 最大回撤实时跟踪器 | 最大回撤实时跟踪器：峰值谷值+三级阈值(-5%/-10%/-15%)+回撤恢复检测 | D_RISK | harvest待评估（likely_planned） |  |
| CAND-HARVEST-1812 | Sector Concentration Real-Time Calculator 行业集中度实时计算器 | 行业集中度实时计算器：申万31行业+偏离度±10%+风格暴露±0.3σ | D_RISK | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1813 | RiskLimit 9-Type Enum Manager 风险限额9类枚举管理器 | 风险限额9类枚举管理器：SINGLE_INSTRUMENT/SECTOR/GROSS/NET/VAR_95/VAR_99/MAX_DD/LEVERAGE/FACTOR | D_RISK | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1814 | Enforcement 3-Level Executor 执行3级执行器 | 执行3级执行器：HARD_BLOCK(不可绕过)/SOFT_WARN(合规官审批)/POST_ONLY(记录) | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-1815 | Liquidity Limit Filter 流动性限制过滤器 | 流动性限制过滤：参与率约束≤5%+流动性评分+Almgren-Chriss冲击模型 | D_RISK | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1816 | Dynamic Position Adjuster 动态仓位调整器 | 动态仓位调整：风险信号→仓位自动调整+市场状态联动 | D_RISK | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1817 | Abnormal Trade Detection Interceptor 异常交易检测拦截器 | 异常交易检测拦截：4类异常交易(瞬时申报>15笔/秒/撤单率>15%/拉抬打压/大额成交)+Hard Block | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-1818 | Risk Audit Trail Writer 风险审计轨迹写入器 | 风险审计轨迹写入器：审计链完整性+事件溯源+不可篡改记录 | D_RISK | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1819 | Normality Test Engine 正态性检验引擎 | 正态性检验引擎：参数法VaR前提+Jarque-Bera/Shapiro-Wilk分布检验 | D_RISK | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1820 | VaR Method Discrepancy Analyzer VaR方法差异分析器 | VaR方法差异分析器：模型风险+参数法vs历史模拟vs蒙特卡洛对比 | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-1821 | VaR Fast Pre-Screen Alerter VaR快速预筛告警器 | VaR快速预筛告警器：L1实时监控+参数法快速筛选(<1ms) | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-1822 | VaR Precise Confirmer VaR精确确认器 | VaR精确确认器：L2日频+历史模拟精确计算(~5ms) | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-1823 | Two-Tier Alert Strategy Engine 双层告警策略引擎 | 双层告警策略引擎：L1快速预筛+L2精确确认双层告警路由 | D_RISK | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1824 | VaR Concurrent Compute Orchestrator VaR并发计算编排器 | VaR并发计算编排器：多方法并发计算+ThreadPoolExecutor+结果聚合 | D_RISK | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1825 | VaR Cross-Validation Engine VaR交叉验证引擎 | VaR交叉验证引擎：回测+Basel交通灯测试(Kupiec+Christoffersen) | D_RISK | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1827 | VaR Phase Independence Guarantor VaR阶段独立性保证器 | VaR阶段独立性保证器：三阶段独立可用+Phase1完成即可上线 | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-1828 | Basel III Multiplier Factor Manager Basel III乘数因子管理器 | Basel III乘数因子管理器：交通灯测试+乘数因子(3×基础)+压力VaR | D_RISK | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1829 | Monte Carlo Precision Level Manager 蒙特卡洛精度级别管理器 | 蒙特卡洛精度级别管理器：精度控制+收敛检测+模拟次数自适应 | D_RISK | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1830 | Covariance Matrix Decomposer 协方差矩阵分解器 | 协方差矩阵分解器：协方差估计+Cholesky分解+指数加权(EWMA) | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-1831 | Risk Budget Adjuster 风险预算调整器 | 风险预算调整：因子暴露+预算再平衡+优化求解器 | D_RISK | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1832 | Risk Stress Tester 风控压力测试器 | 风控压力测试：情景构建+冲击模拟+历史情景回放(2008/2015/2020) | D_RISK | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1833 | A-Share PDF Tail Risk Auto-Hedger A股PDF尾部风险自动对冲器 | A股PDF尾部风险自动对冲器❌不能建：需A股期权市场日均成交量>100亿元(RD-22) | D_RISK | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1834 | A-Share Contrarian Dedicated Stop-Loss A股逆向专用止损 | A股逆向专用止损：逆向策略专用止损逻辑+参数独立 | D_RISK | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1835 | A-Share Systemic Risk 3-Level Alerter A股系统性风险三级告警器 | A股系统性风险三级告警器：1因子停开仓/2因子降30%/≥3因子清仓 | D_RISK | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1836 | A-Share First-Minute Stop-Loss Executor A股首分钟止损执行器 | A股首分钟止损执行器：开盘首分钟异常止损+竞价不及预期 | D_RISK | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1837 | A-Share Contrarian Time-Based Stop-Loss A股逆向时间止损 | A股逆向时间止损：逆向策略时间维度止损+持仓超时平仓 | D_RISK | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1838 | A-Share Multi-Level Loss Circuit Breaker A股多级亏损熔断器 | A股多级亏损熔断器：亏损分级+熔断触发+冷却期 | D_RISK | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1839 | A-Share 5-Signal Systemic Risk Scanner A股5信号系统性风险扫描器 | A股5信号系统性风险扫描器：BS-001~007黑天鹅信号扫描 | D_RISK | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1840 | A-Share Cascading Circuit Breaker A股级联熔断器 | A股级联熔断器：跨策略/跨市场级联熔断+传染隔离 | D_RISK | harvest待评估（likely_planned） |  |
| CAND-HARVEST-1841 | AISG Regulatory Compliance Checker AISG监管合规检查器 | AISG监管合规检查器：程序化交易合规+2026.4.7新规(15笔/秒)+报单停留≥50μs | D_RISK | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1842 | Kill Switch Cooldown Manager Kill Switch冷却期管理器 | Kill Switch冷却期管理器：30min冷却期+状态锁定+重置 | D_RISK | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1843 | Kill Switch Trading System Integrator Kill Switch交易系统集成器 | Kill Switch交易系统集成器：撤单+暂停+通知+多域协调 | D_RISK | harvest待评估（likely_planned） |  |
| CAND-HARVEST-1844 | Kill Switch Multi-Domain Notifier Kill Switch多域通知器 | Kill Switch多域通知器：D-EX-CORE撤单+D-PF-CORE暂停+D-AUTONOMY告警 | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-1845 | Kill Switch State Machine Manager Kill Switch状态机管理器 | Kill Switch状态机管理器：OPEN/CLOSED+转换+持久化 | D_RISK | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1846 | Kill Switch New Order Rejector Kill Switch新订单拒绝器 | Kill Switch新订单拒绝器：CLOSED状态下新订单拦截+拒绝 | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-1847 | Kill Switch Owner Confirmation Reset Gateway Kill Switch Owner确认重置网关 | Kill Switch Owner确认重置网关：Owner确认+状态重置+审计记录 | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-1848 | ATR Dynamic Stop Loss Calculator ATR动态止损计算器 | ATR动态止损计算器：ATR倍数+动态调整+波动率自适应 | D_RISK | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1849 | Time-Based Stop Loss Evaluator 时间止损评估器 | 时间止损评估器：时间维度止损+持仓超时平仓+逻辑失效检测 | D_RISK | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1850 | Risk Policy Approval Gateway 风险策略审批网关 | 风险策略审批网关：四级审批+审批流+合规官审批 | D_RISK | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1851 | Risk Policy DDD Aggregate Root AGG-007 Manager 风险策略DDD聚合根AGG-007管理器 | 风险策略DDD聚合根AGG-007管理器：聚合根+事件溯源+状态机(DRAFT→ACTIVE→DEPRECATED) | D_RISK | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1852 | RiskDashboardSnapshot CTR-P1-008 Builder 风险仪表盘快照CTR-P1-008构建器 | 风险仪表盘快照CTR-P1-008构建器：契约快照+数据聚合+序列化 | D_RISK | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1853 | RiskMetricsReport CTR-P1-011 Generator 风险指标报告CTR-P1-011生成器 | 风险指标报告CTR-P1-011生成器：契约报告+指标计算+格式化 | D_RISK | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1854 | Daily Risk Report Generator 每日风险报告生成器 | 每日风险报告：日度摘要+关键指标+异常事件汇总 | D_RISK | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1855 | Custom Risk Report Generator 风险报告自定义生成器 | 风险报告自定义：用户自定义报告模板+输出格式+筛选条件 | D_RISK | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1856 | Real-time Risk Warning and Report Generator 实时风险预警与报告生成器 | 实时风险预警报告：事件快报+实时告警+推送通知 | D_RISK | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1857 | Strategy Correlation Gate Checker 策略相关性门禁检查器 | 策略相关性门禁检查器：VR-013策略拥挤+相关性阈值+Hard Block | D_RISK | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1858 | Leverage Limit Gate Checker 杠杆限额门禁检查器 | 杠杆限额门禁检查器：杠杆率门禁+限额检查+Hard Block | D_RISK | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1859 | Risk Rule User Configurator 风险规则用户配置器 | 风险规则用户配置：用户自定义规则+参数配置+预览 | D_RISK | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1860 | Risk Control Rule Engine 风险控制规则引擎 | 风险控制规则引擎：否决规则5级引擎+执行+评估 | D_RISK | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1861 | Risk Rule Validation and Stress Tester 风控规则验证与压力测试器 | 风控规则验证+压力测试：规则测试沙箱+模拟执行+回归测试 | D_RISK | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1862 | Rule Priority Sorter (Inter-Rule) 规则优先级排序(规则间) | 规则优先级排序(规则间)：规则冲突检测+优先级排序+依赖解析 | D_RISK | harvest待评估（likely_planned） |  |
| CAND-HARVEST-1863 | Risk Rule DSL Engine 风控规则DSL引擎 | 风控规则DSL引擎：DSL解析+执行+AST构建 | D_RISK | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1864 | Risk Engine Rule DSL 风控引擎规则DSL | 风控引擎规则DSL：DSL语法定义+关键字+操作符 | D_RISK | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1865 | Risk Rule Versioning and Hot Updater 风控规则版本化与热更新器 | 风控规则版本化+热更新：版本管理+运行时热更新+回滚 | D_RISK | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1866 | Rule Priority Sorter (Inter-Strategy) 规则优先级排序(策略间) | 规则优先级排序(策略间)：策略冲突+优先级+仲裁 | D_RISK | harvest待评估（likely_planned） |  |
| CAND-HARVEST-1867 | CTR-006 PositionSnapshot Provider CTR-006仓位快照提供者 | CTR-006仓位快照提供者：仓位快照契约+实时快照+序列化 | D_RISK | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1868 | CTR-004 Order Consumer CTR-004订单消费者 | CTR-004订单消费者：风险数据流+订单消费+事件驱动 | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-1869 | CTR-003 RiskLimits Producer CTR-003风险限额生产者 | CTR-003风险限额生产者：限额契约+生产+版本管理 | D_RISK | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1870 | Position Write Authority Arbiter 仓位写入权限仲裁器 | 仓位写入权限仲裁器：DDD聚合根边界+写入权仲裁+事件驱动写入 | D_RISK | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1871 | Rule Engine vs Statistical Engine Router 双引擎路由器 | 双引擎路由器：规则引擎(确定性→硬阻断)vs统计引擎(概率性→告警+建议)路由 | D_RISK | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1872 | Risk Rule YAML Runtime Loader 风险规则YAML运行时加载器 | 风险规则YAML运行时加载器：YAML加载+热加载+语法校验 | D_RISK | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1873 | Risk Policy SQLite Schema Designer 风险策略SQLite Schema设计器 | 风险策略SQLite Schema设计器：Schema设计+迁移脚本+版本管理 | D_RISK | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1874 | IV Parametric VaR to Historical Simulation Migrator 参数法VaR→历史模拟法迁移器 | 参数法VaR→历史模拟法迁移器：方法迁移+数据转换+回滚 | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-1875 | DefaultRiskValidator to Configurable Rule Engine Migrator DefaultRiskValidator→可配置规则引擎迁移器 | DefaultRiskValidator→可配置规则引擎迁移器：硬编码→可配置迁移+兼容性 | D_RISK | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1876 | Execution Result Feedback Consumption Bridger 执行结果反馈消费桥接器 | 执行结果反馈消费桥接：执行域→风控域反馈+事件消费+参数优化 | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-1877 | Risk Domain Value Object Definition 风控域值对象定义 | 风控域值对象定义：DDD值对象+类型安全+不可变 | D_RISK | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1878 | Risk Rule Engine Upgrade Migration Adapter 风控规则引擎升级迁移适配器 | 风控规则引擎升级迁移适配：版本升级+迁移脚本+向后兼容 | D_RISK | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1879 | Counterparty Risk Manager 交易对手风险管理器 | 交易对手风险管理器：需开展衍生品/融资融券/回购业务(远期) | D_RISK | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1880 | Market Digital Twin 市场数字孪生 | 市场数字孪生：需ABIDES-MARL研究基础设施+GPU资源(远期) | D_RISK | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1881 | Climate Risk Engine 气候风险引擎 | 气候风险引擎：需ESG数据源+ESG因子纳入风险模型(远期) | D_RISK | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1882 | Monte Carlo Batch Backtester 蒙特卡洛批量回测器 | 蒙特卡洛批量回测器：需GPU资源可用(远期) | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-1883 | Monte Carlo Portfolio PnL Sorter 蒙特卡洛组合PnL排序器 | 蒙特卡洛组合PnL排序器：需GPU资源可用(远期) | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-1884 | AI-Enhanced Risk Engine AI增强风控引擎 | AI增强风控引擎：需D-ML域Phase2就绪+AI风控可解释性验证(远期) | D_RISK | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1885 | AI Risk Engine Implementer AI风控引擎实现器 | AI风控引擎实现器：同D-RISK-95门禁条件(远期) | D_RISK | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1886 | Personalized Risk Profile Builder 个性化风险画像构建器 | 个性化风险画像：风险偏好+画像构建+历史行为分析 | D_RISK | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-2002 | 风险传播建模 Risk Propagation Modeling | NetworkX图传播模拟:系统性风险→行业→个股级联传播 | D_RISK | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-2047 | VaR Calculator 风险价值计算器 | 蒙特卡洛VaR计算:基于GPU加速蒙特卡洛的VaR/CVaR估计(❌) | D_RISK | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-2049 | 绩效归因 Performance Attribution | Brinson模型:配置效应+选择效应+交互效应分解收益来源 | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-2050 | Brinson模型 Brinson Model | 绩效归因学术标准分解为配置效应+选择效应 | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-2052 | IC衰减检测 IC Decay Detection | 因子IC的60日移动平均趋势IC衰减>50%=策略退化 | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-2053 | 拥挤度检测 Crowding Detection | 使用同一策略的参与者数量估计拥挤度上升=超额收益将消失 | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-2054 | 自动降权 Auto Weight Reduction | / 自动降权 / 策略退化时自动将权重降为0 / Man Group AlphaGPT实践 / | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-2112 | Risk Manager Agent 风控Agent | 战略层风控Agent战略级风控评估仓位上限决策 | D_RISK | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-2141 | Hedge Execution 独立对冲执行 | 风控Agent技能独立对冲执行ACTIVE | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-2243 | Kill Switch 紧急制动 | / Kill Switch日志 / 触发条件/时间/恢复时间/人工确认 / ≥7年 / 哈希链+独立存储 / | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-2315 | Amihud Illiquidity Amihud非流动性指标 | / 日度风险摘要 / 每日收盘 / VaR/CVaR/因子暴露/否决统计/漂移状态/Amihud非流动性 / Trader+Risk Manager / | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-2316 | Reverse RST 反向RST指标 | / 周度风险深度 / 每周五 / 压力测试+漂移趋势+策略拥挤度+模型健康度+反向RST / Risk Manager / | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-2317 | PSI/KS/CUSUM PSI/KS/CUSUM漂移检测指标 | / 漂移检测日志 / PSI/KS/CUSUM值/检测时间/处置动作 / ≥3年 / 哈希链 / | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-2344 | Veto Flow 否决流 | / **否决流** / 风控Agent→任意层（横向穿透） / 熔断指令、仓位上限、交易禁止 / 否决流为最高优先级，可穿透任意层；否决信号为immutable级，任何Agent收到后必须终止当前操作 / | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-2345 | P0-Emergency P0紧急指令 | / P1-高 / 仓位上限调整、交易禁止 / 风控Agent/战略层 / 优先处理，可中断当前非紧急指令 / | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-2346 | P1-High P1高优先级指令 | P1-高仓位上限调整交易禁止风控Agent/战略层优先处理可中断当前非紧急指令 | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-2382 | Risk Report 风险报告 | 风险报告4类型日度风险摘要到周度风险深度到事件风险快报到月度风险治理来源A4§4.3 | D_RISK | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-2383 | Risk Audit 风控审计 | / 日度风险摘要 / 每日收盘 / VaR/CVaR/因子暴露/否决统计/漂移状态/Amihud非流动性 / Trader+Risk Manager / | D_RISK | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-2618 | Black Swan Pattern Library 黑天鹅模式库7种模式 | 7种模式库BS-001~007+跨市场传导4渠道 | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-2624 | Model Risk SR 26-2 模型风险 | SR 26-2/5类漂移检测/CUSUM/过拟合防护 | D_RISK | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-2625 | Liquidity Risk 流动性风险 | / 流动性风险（参与率/LVaR/Amihud/Kyle/退出时间/流动性螺旋） / 数据存储方案（→A3） / | D_RISK | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-2626 | Operational Risk 操作风险 | 系统故障/人为错误/Agent失控/级联失败 | D_RISK | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-2627 | AI Agent Specific Risk AI/Agent特有风险 | OWASP ASI+AST+MCP完整映射 | D_RISK | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-2674 | A Share Compliance Rule A股合规规则代管 | 不操纵市场/持仓限额/涨跌停约束/A股风险日历 | D_RISK | harvest待评估（likely_planned） |  |
| CAND-HARVEST-2675 | Drift Detection Risk Closed Loop 漂移检测与风险闭环 | 事前PSI/事中在线适应/事后重训触发 | D_RISK | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-2676 | Extreme Event Black Swan 极端事件与黑天鹅 | 7种模式库BS-001~007+跨市场传导4渠道 | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-2677 | AI Agent Risk Governance AI/Agent风险治理 | 有界自治5级+保障缺口管理+治理漂移防护 | D_RISK | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-2986 | Risk Control Agent 风险 | 仓位上限决策+熔断触发+独立对冲执行 | D_RISK | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-2996 | 风控域规则目录 Risk Domain Rule Catalog | 风控参数熔断机制止损 | D_RISK | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-3089 | ESRB 2025系统性风险报告 | AI放大系统性风险11渠道 | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-3094 | Unleash 2026 Kill Switch Unleash 2026紧急制动 | 细粒度Kill Switch本地评估 | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-3134 | 顺周期性 Pro-cyclicality | ESRB系统性风险AI羊群行为 | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-3135 | 速度 Speed | ESRB系统性风险Kill Switch<1ms | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-3139 | 集中度 Concentration | ESRB系统性风险单票集中度 | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-3198 | KS-L1 软暂停 Kill Switch | 滑点超限/单策略日内亏损超限暂停新开仓 | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-3199 | KS-L2 会话熔断 Kill Switch | 连续N笔亏损/模型漂移超阈值禁用策略 | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-3200 | KS-L3 通道断开 Kill Switch | 下单拒绝率飙升/miniQMT心跳失败断开交易通道 | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-3201 | KS-L4 硬停机 Kill Switch | 持仓异常/账户级日亏损超硬限终止所有自动化 | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-3216 | LVaR价差模型 | LVaR=VaR+½×S×W正常市场+小仓位 | D_RISK | harvest待评估（uncertain） |  |
| CAND-HARVEST-3217 | LVaR Amihud冲击模型 | LVaR=VaR+ILLIQ×(Q/V)^α大仓位+非标资产 | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-3218 | LVaR EVT尾部模型 | LVaR=VaR+EVT尾部流动性溢价极端行情 | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-3219 | CoVaR跨市场传染 | CoVaR条件VaR给定i机构压力系统性风险 | D_RISK | harvest待评估（uncertain） |  |
| CAND-HARVEST-3220 | Grinold & Kahn容量公式 | 策略容量=f(ADV,参与率上限 | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-3304 | EVT极值理论 | 尾部相关EVT极值理论 | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-3323 | 市场风险 Market Risk | §1.1因市场价格不利变动导致投资组合价值损失 | D_RISK | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-3324 | 价格风险 Price Risk | 市场风险子类实时P&L监控+因子暴露监控 | D_RISK | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-3325 | 波动率风险 Volatility Risk | 市场风险子类VIX类指标+已实现vs隐含波动率 | D_RISK | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-3326 | 相关性风险 Correlation Risk | 市场风险子类滚动相关矩阵+条件相关性 | D_RISK | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-3327 | 尾部风险 Tail Risk | 市场风险子类极值理论EVT+共形VaR超限频率 | D_RISK | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-3328 | L1实时监控 L1 Real-time Monitoring | 三层度量体系实时P&L+因子暴露+集中度+Amihud | D_RISK | harvest待评估（likely_planned） |  |
| CAND-HARVEST-3329 | L2日频因子风险模型 L2 Daily Factor Risk Model | 三层度量体系申万31行业+4风格因子+VaR/CVaR/ES | D_RISK | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-3330 | L3压力测试 L3 Stress Testing | 三层度量体系历史回放+假设情景+程式化冲击 | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-3331 | 风险分级预警 Risk Tiered Alert | 系统性风险分级预警与尾部风险管理模型 | D_RISK | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-3332 | 模型风险 Model Risk | §1.2因模型设定错误实现错误误用或漂移导致决策偏差 | D_RISK | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-3333 | 模型设定风险 Model Specification Risk | 模型风险子类概念健全性审查+基准对比 | D_RISK | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-3334 | 实现风险 Implementation Risk | 模型风险子类训练-服务一致性校验+代码审计 | D_RISK | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-3335 | 误用风险 Misuse Risk | 模型风险子类适用场景审查+输入范围检查 | D_RISK | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-3336 | 过拟合风险 Overfitting Risk | / 过拟合风险 / Purged K-Fold+Walk-Forward+Permutation Test / 样本内外Sharpe比+Permutation p值 / 策略否决上线 / 样本外Sharpe<70%样本内→否决 / | D_RISK | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-3337 | 模型组合风险 Model Combination Risk | 模型风险子类多模型交互产生聚合风险 | D_RISK | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-3338 | 协变量漂移 Covariate Drift | 漂移检测五分类P_train(X)≠P_test(X) | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-3339 | 概念漂移 Concept Drift Type | 漂移检测五分类P_train(Y/X)≠P_test(Y/X) | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-3340 | 标签漂移 Label Drift | 漂移检测五分类P_train(Y)≠P_test(Y) | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-3341 | 公平性漂移 Fairness Drift | 漂移检测五分类子群体性能差异扩大 | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-3342 | 上游数据漂移 Upstream Data Drift | 漂移检测五分类数据管道Schema/质量变化 | D_RISK | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-3343 | CUSUM控制图 CUSUM Control Chart | 补充PSI/KS的持续性偏移检测 | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-3344 | 流动性风险 Liquidity Risk | §1.3因市场流动性不足导致无法以合理价格/时间完成交易 | D_RISK | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-3345 | 市场深度风险 Market Depth Risk | 流动性风险子类实时买卖盘深度+成交量 | D_RISK | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-3346 | 冲击成本风险 Impact Cost Risk | 流动性风险子类Almgren-Chriss模型+历史冲击 | D_RISK | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-3347 | 退出时间风险 Exit Time Risk | 流动性风险子类退出时间估算模型 | D_RISK | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-3348 | 流动性螺旋风险 Liquidity Spiral Risk | 流动性风险子类资金流动性vs市场流动性交互 | D_RISK | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-3349 | 策略容量风险 Strategy Capacity Risk | 流动性风险子类策略可管理最大AUM | D_RISK | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-3350 | Amihud ILLIQ 非流动性指标 | 流动性四维学术度量价格冲击单位成交量引起的价格变动 | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-3351 | Kyle Lambda 凯尔lambda | 流动性四维学术度量永久价格冲击单位订单流的价格影响 | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-3352 | Roll Spread Estimator 罗尔价差估计器 | 流动性四维学术度量隐含买卖价差无需报价数据 | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-3353 | Pastor-Stambaugh 流动性因子 | 流动性四维学术度量系统性流动性风险因子 | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-3354 | Almgren-Chriss最优执行框架 Almgren-Chriss Optimal Execution Framework | 临时冲击+永久冲击+风险厌恶+参与率上限 | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-3355 | 日内时变参与率 Intraday Time-Varying Participation Rate | A股日内成交量U型分布时变参与率降低执行成本 | D_RISK | harvest待评估（likely_planned） |  |
| CAND-HARVEST-3356 | 流动性降级模式 Liquidity Degradation Mode | 正常/降级/极端三级VaR处理+溢价 | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-3357 | 流动性调整VaR LVaR Liquidity-adjusted VaR | 价差模型+Amihud冲击模型+EVT尾部模型+CoVaR | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-3358 | CoVaR跨市场传染 CoVaR Cross-Market Contagion | LVaR模型系统性流动性风险评估 | D_RISK | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-3359 | 流动性螺旋模型 Liquidity Spiral Model | 价差异常+强制卖出+流动性冻结三阶段 | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-3360 | 操作风险 Operational Risk | §1.4因系统故障人为错误流程缺陷或外部事件导致损失 | D_RISK | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-3361 | 系统故障 System Failure | 操作风险子类健康检查+心跳+进程监控 | D_RISK | harvest待评估（likely_planned） |  |
| CAND-HARVEST-3362 | 人为错误 Human Error | 操作风险子类操作审计+异常行为检测 | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-3363 | Agent失控 Agent Out-of-Control | 操作风险子类行为边界监控+涌现行为检测 | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-3364 | 买入后即时验证与快速纠错模型 Post-Entry Instant Validation Model | 买入后5-15分钟即时验证Intraday Momentum | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-3365 | AI/Agent特有风险 AI/Agent Specific Risk | §1.5 AI自治系统引入的全新风险类别 | D_RISK | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-3366 | 策略同质化 Strategy Homogeneity | 策略同质化与串谋风险因子/策略相似度检测 | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-3368 | 影子MCP服务器 Shadow MCP | > MCP(Model Context Protocol)已成为Agent工具集成的默认协议层。OWASP MCP Top 10(2026.2)覆盖MCP协议特有风险——与AST10(Skills执行层)互补。Mental Model：AS | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-3369 | 交易对手风险 Counterparty Risk | §1.6因交易对手违约导致损失当前不能建 | D_RISK | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-3370 | 信用风险 Credit Risk | §1.7因发行人信用恶化导致持仓资产价值损失当前不能建 | D_RISK | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-3371 | VaR风险价值 Value at Risk | §2.1核心度量指标95%/99%置信度历史模拟+参数法 | D_RISK | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-3372 | CVaR/ES条件风险价值 Conditional Value at Risk | §2.1核心度量指标97.5%尾部风险度量FRTB标准 | D_RISK | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-3373 | 密度感知VaR Density-Aware VaR | §2.1核心度量指标概率密度预测+分位数提取 | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-3374 | 共形VaR Conformal VaR | §2.1核心度量指标共形预测校准层分布无关覆盖率 | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-3375 | 时间加权共形风险控制 Time-Weighted Conformal | 共形VaR默认方法Schmitt 2026计算简单漂移下强默认 | D_RISK | harvest待评估（likely_planned） |  |
| CAND-HARVEST-3376 | 分位数预测共形校准 TCP Conformal | / 共形VaR / 95% / 1日 / 共形预测校准层 / 分布无关覆盖率保证 / TWC(默认,Schmitt 2026) / TCP(Aich et al. 2026) / RWC(增强,Schmitt 2026) / | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-3377 | 体制加权共形风险控制 Regime-Weighted Conformal | 共形VaR增强方法Schmitt 2026体制条件校准稳定性 | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-3378 | 状态自适应贝叶斯共形预测 State-Adaptive Bayesian CP | / SA-BCP / Fang & Lee (arXiv:2605.00432, 2026.5) / 状态自适应贝叶斯共形预测：空间核密度证据门控长期时间惯性 / 解决ACI系统性覆盖不足+减少贝叶斯CP区间膨胀10-37% / 波动性金融 | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-3379 | 共形VaR回测 CP-VaR Backtesting | / CP-VaR回测 / Retzlaff et al. (COPA 2025) / CP与VaR形式等价→VaR回测方法可用于统计评估CP覆盖率 / Dynamic Binary Test+Geometric Conformal Back | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-3380 | 压力测试 Stress Testing | §2.2压力测试回答市场崩溃时系统能否存活 | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-3381 | 情景分析 Scenario Analysis | §2.2情景分析回答如果X发生组合会怎样 | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-3382 | 反向压力测试 Reverse Stress Testing | §2.2反向压力测试回答什么情景会导致系统崩溃 | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-3383 | 流动性骤降 Liquidity Sudden Drop | A股特有压力情景日成交量缩至日均10%+价差扩大5倍 | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-3384 | 融资盘强平 Margin Call Forced Liquidation | A股特有压力情景两融余额单日下降15% | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-3385 | 政策黑天鹅 Policy Black Swan | A股特有压力情景印花税上调/交易规则突变 | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-3386 | 跨市场传导 Cross-Market Transmission | A股特有压力情景港股暴跌→A股联动 | D_RISK | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-3387 | 黑天鹅加T+1锁定 Black Swan with T+1 Lock | A股特有压力情景极端事件当日无法卖出+次日跳空 | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-3388 | 风险否决权 Risk Veto Power | §3风控可否决一切交易决策但不可修改策略逻辑 | D_RISK | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-3389 | Kill Switch 紧急停止开关 | 否决五级分类系统性风险/风控崩溃/AI自治熔断 | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-3390 | 强制减仓 Forced Position Reduction | 否决五级分类单日亏损超阈值/回撤超限 | D_RISK | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-3391 | 否决新开仓 Reject New Position | 否决五级分类VaR超限/集中度超限/流动性不足 | D_RISK | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-3392 | 否决单笔订单 Reject Single Order | 否决五级分类单笔金额超限/涨跌停买入 | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-3393 | 建议性告警 Advisory Alert | 否决五级分类风险指标接近阈值/漂移检测预警 | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-3394 | Pod级止损机制 Pod-Level Stop Loss | **Pod级止损机制**（对齐 Citadel/Millennium/Point72多管理人平台实践）： | D_RISK | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-3395 | 否决执行引擎 Veto Execution Engine | §3.2否决执行机制同步拦截<50ms P99 | D_RISK | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-3397 | Kill Switch多路径激活 Kill Switch Multi-Path Activation | AI自动/人工一键/定时熔断/外部信号四路径 | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-3398 | 四层隔离防护 Four-Layer Isolation | §3.3否决与策略逻辑的隔离代码/数据/权限/审计 | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-3399 | ATR动态止损与Bayesian参数优化模型 ATR Dynamic Stop-Loss Model | 基于波动率的动态止损+参数优化框架 | D_RISK | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-3400 | 独立风险数据管道 Independent Risk Data Pipeline | §4.1风险数据流独立于交易数据流BCBS 239 | D_RISK | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-3401 | 风险指标计算引擎 Risk Indicator Computing Engine | 计算层VaR/CVaR/ES/密度VaR/共形VaR | D_RISK | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-3402 | 漂移检测引擎 Drift Detection Engine | │  [漂移检测引擎] ────→ PSI/KS/Wasserstein/ADWIN/CUSUM   │ | D_RISK | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-3403 | 压力测试引擎 Stress Test Engine Risk | 计算层情景P&L/流动性压力/传导/反向RST | D_RISK | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-3404 | Agent行为监控 Agent Behavior Monitor | 计算层ASI+AST+MCP行为边界/涌现/串谋 | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-3406 | 风险仪表盘 Risk Dashboard | 消费层日频风险报告 | D_RISK | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-3407 | 告警系统 Alert System | 消费层风险事件+漂移告警 | D_RISK | harvest待评估（likely_planned） |  |
| CAND-HARVEST-3408 | 日度风险摘要 Daily Risk Summary | §4.3风险报告每日收盘VaR/CVaR/因子暴露 | D_RISK | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-3409 | 周度风险深度 Weekly Risk Deep Report | §4.3风险报告每周五压力测试+漂移趋势 | D_RISK | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-3410 | 月度风险治理 Monthly Risk Governance | §4.3风险报告月末风控参数变更审计 | D_RISK | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-3411 | 四级审批流 Four-Level Approval Flow | §5.1风控规则变更审批L1紧急→L2参数→L3规则→L4架构 | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-3412 | 三平面一致性 Three-Plane Consistency | §5.2风控参数版本管理代码/配置/运行时一致性 | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-3413 | 不操纵市场规则 No Market Manipulation Rules | §6.1 A股合规规则代管禁止幌骗/分层/自交易 | D_RISK | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-3414 | 幌骗检测 Spoofing Detection | 禁止幌骗下单意图校验+撤单率监控 | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-3415 | 分层操纵检测 Layering Detection | 禁止分层操纵多档位挂单模式检测 | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-3416 | 自交易检测 Self-Trading Detection | 禁止自交易账户内对倒检测 | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-3417 | 程序化交易合规 Programmatic Trading Compliance | **程序化交易合规**（对齐 2025.7《程序化交易管理实施细则》+ 2026.4.7新版实施细则+ 2026.1《沪深股通程序化交易报告指引》+ 证监会吴清2026.3两会表态）： | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-3418 | 私募基金合规 Private Fund Compliance | 证监会信息披露办法2026.9.1生效 | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-3419 | 信息不对称期与操纵行为检测模型 Information Asymmetry Detection Model | 庄股操作识别量化框架ESMA MABUM | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-3420 | A股风险日历 A-Share Risk Calendar | §6.4可预测周期性风险事件日历 | D_RISK | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-3421 | 漂移检测与风险闭环 Drift Detection Risk Loop | §7事前PSI→事中适应→事后重训 | D_RISK | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-3422 | 交易绩效归因与策略退化检测模型 Performance Attribution Model | Brinson模型归因+IC衰减检测+自动降权 | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-3424 | Autoencoder重构异常检测 Autoencoder Anomaly Detection | 深度学习异常检测训练正常数据极端事件重构误差飙升 | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-3425 | GAN对抗检测 GAN Adversarial Detection | / GAN对抗检测 / Generator生成正常分布，Discriminator检测偏离分布的极端模式 / '未知的未知'模式(不依赖预定义黑天鹅库) / 训练不稳定；生成质量依赖数据 / L3压力测试增强方法 / | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-3426 | Transformer时序异常 Transformer Time-Series Anomaly | 深度学习异常检测注意力机制捕捉多变量时序异常 | D_RISK | harvest待评估（likely_planned） |  |
| CAND-HARVEST-3427 | 跨市场传导模型 Cross-Market Transmission Model | §14.2港股→A股/美股→A股/期货→现货/汇率→A股 | D_RISK | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-3428 | 流动性危机模拟 Liquidity Crisis Simulation | §14.3成交量骤降/买卖价差扩大/T+1锁定风险 | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-3429 | 反向压力测试引擎 Reverse Stress Testing Engine | §14.4从崩溃阈值反推致崩溃情景 | D_RISK | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-3430 | 二阶效应与传染模型 Second-Order Effect Contagion Model | §14.5流动性螺旋/相关性传染/策略拥挤踩踏/信心传染 | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-3431 | 凸性预算框架 Convexity Budget Framework | **尾部风险对冲——凸性预算框架**（对齐 Jabłecki et al. 2026 + Landl 2026.3 + StockAlpha 2026.2）： | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-3432 | 相关性体制转换 Correlation Regime Switching | 1970-82滞胀/2000-21负相关/2022通胀冲击/2026危机窗口 | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-3433 | ESRB 14个AI风险放大向量 ESRB 14 AI Risk Amplification Vectors | 欧洲系统性风险委员会系统性识别14个渠道 | D_RISK | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-3435 | 保障缺口管理 Guarantee Gap Management | §15.2 AI概率可靠性与所需可执行保证间差距 | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-3436 | 治理漂移防护 Governance Drift Protection | §15.3自治权渐进扩张但治理未同步更新 | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-3437 | Agent行为监控 Agent Behavior Monitoring | §15.4 OWASP ASI 10类+串谋+隐性串谋监控 | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-3438 | Agent红队测试 Agent Red Team Testing | **Agent红队测试与防御**（对齐 FinJailbreak Li et al. AAAI 2026 + AutoRedTrader Liu et al. 2026.5 + FinRedTeamBench Dimino et al. 2 | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-3439 | 金融治理越狱 FinJailbreak | Agent红队攻击向量领域特定对抗提示绕过安全对齐 | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-3440 | 合成虚假信息注入 AutoRedTrader | Agent红队攻击向量行为偏差操纵+文本微扰 | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-3441 | BFSI领域自适应红队 FinRedTeamBench | Agent红队攻击向量多轮自适应交互+领域危害分类 | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-3442 | 交易管线扰动 TradeTrap | Agent红队攻击向量单组件微扰传播全决策闭环 | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-3443 | ARS双轨结算模型 ARS Dual-Track Settlement | §15.5 Fee Track+Principal Track金融级保障 | D_RISK | harvest待评估（likely_planned） |  |
| CAND-HARVEST-3444 | Fee Track费用轨道 Fee Track | ARS双轨仅涉及服务报酬的任务托管Escrow机制 | D_RISK | harvest待评估（likely_planned） |  |
| CAND-HARVEST-3445 | Principal Track本金轨道 Principal Track | ARS双轨涉及资金操作的任务承保+抵押机制 | D_RISK | harvest待评估（likely_planned） |  |
| CAND-HARVEST-3446 | Named Accountability命名问责人 Named Accountability | §15.6每个Agent必须有命名问责人 | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-3447 | Risk Management Core 风险管理核心 | / MOD-L04-001 / Risk Management Core / 🔧部分实现 / risk_manager/risk_limits/stop_loss/risk_validator+G10/G11/G12门禁 / §3+§5+§ | D_RISK | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-3562 | 反推致崩溃情景 Reverse Derive Crash Scenario | / 反向压力测试 / 从崩溃阈值反推致崩溃情景 / '什么情景会导致组合亏损>15%?'→反推所需冲击组合 / 每季度 / | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-3563 | 评估情景合理性 Evaluate Scenario Plausibility | 反向压力测试步骤判断反推情景是否合理但极端 | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-3564 | 设计防护措施 Design Protection Measures | 反向压力测试步骤为每个合理致崩溃情景设计预防/缓解措施 | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-3565 | DPG七场景 DPG Seven Scenarios | / 程式化情景 / 对关键风险因子施加标准化冲击 / DPG七场景：利率±100bp / 波动率±20% / 股指±10% / 汇率±6% / 每月 / | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-3566 | 管线验证 Pipeline Validation | 重训门禁全链路端到端 Walk-Forward+模拟盘 | D_RISK | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-3567 | ARA五项原则 ARA Five Principles | 治理速度≥自治速度/持续验证/最小代理权/基础设施层Kill Switch/自适应治理参数 | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-3568 | ARA治理方程 ARA Governance Equation | 期望损失=(攻击概率×Agent自治度×资产暴露)÷治理系数 | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-3569 | ARS状态机语义 ARS State Machine Semantics | 请求→协商→执行→评估→结算确定性状态机用户损失减少61% | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-3570 | TCP+Robbins-Monro偏移 TCP-RM | / TCP-RM / 同上 / TCP+在线Robbins-Monro偏移 / 实时调整覆盖率 / 需要调参(学习率γ) / | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-3571 | 自适应共形推断 Adaptive Conformal Inference | / TCP / Aich et al. (2026) arXiv:2507.05470 / 分位数预测器+滚动split-conformal校准层 / 非平稳时序下覆盖率接近目标 / 有足够校准窗口(≥250日) / | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-3572 | Portfolio CP 组合共形预测 | / Portfolio CP / Jia & Han (DMO-FinTech 2026) HKUST(Guangzhou) / 共形预测估计VaR→组合优化 / 分布无关+覆盖率保证+可整合任何回归方法 / 短卖约束+投资者指定约束 / | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-3573 | QRF+Conformal 分位数回归森林+共形 | / QRF+Conformal / Wang et al. (2026.2) Renmin Univ / 分位数回归森林+OSOA框架+共形校准层 / 实时VaR+一致性+覆盖率有效性理论保证 / 需离线模拟训练+≥250日校准窗口 / | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-3574 | Phase 1参数化高斯混合 Phase 1 Parametric Gaussian Mixture | / Phase 1 / 参数化(高斯混合) / CRPS<基准10% / 概率校准度偏离对角线<5% / | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-3575 | Phase 2 QNN量子神经网络 Phase 2 QNN | / Phase 2 / QNN(量子神经网络近似) / CRPS<Phase1 / 尾部校准VaR覆盖率误差<2% / | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-3576 | Phase 3非参数化KDE Phase 3 Non-parametric KDE | / Phase 3 / 非参数化(KDE/核密度) / CRPS<Phase2 / 8态概率从PDF积分派生 / | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-3577 | 追踪止损 Trailing Stop | / 追踪止损 / Trailing_Stop = max(历史最高价 - k × ATR, 前一日止损位) / 只上移不下移，锁定盈利 / | D_RISK | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-3578 | Grid Search 网格搜索 | / Grid Search / 遍历k∈[1.0, 5.0]步长0.5，计算各k的Sharpe/MaxDD / 全局搜索但计算量大 / | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-3579 | Bayesian优化 Bayesian Optimization | / Bayesian优化 / 用高斯过程建模k→Sharpe映射，聚焦有前景区域 / amhieu(2025)：比Grid Search更高效 / | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-3580 | Walk-Forward验证 Walk-Forward Validation | / Walk-Forward验证 / 样本内优化k→样本外验证→滚动前进 / 防止过拟合 / | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-3581 | 体制自适应 Regime Adaptive | / 体制自适应 / 不同市场体制（趋势/均值回归/混沌）使用不同k / 趋势市k=3-4（宽止损）/ 均值回归市k=1.5-2（紧止损） / | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-3582 | ATR动态止盈 ATR Dynamic Take Profit | / ATR动态止盈 / Target = Entry + m × ATR / m通常为k的1.5-2倍（盈亏比>1.5） / | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-3583 | 分批止盈 Batch Take Profit | / 分批止盈 / 1/3仓位在1R止盈+1/3在2R+1/3追踪止损 / R=初始风险(Entry-Stop) / | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-3584 | 时间止损 Time Stop Loss | ATR止盈策略持仓N日未达1R盈利→平仓适用于短期动量策略 | D_RISK | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-3585 | LVaR价差模型 LVaR Spread Model | / LVaR(价差模型) / LVaR = VaR + ½ × S × W / 正常市场+小仓位 / S=买卖价差(%), W=仓位价值 / | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-3586 | LVaR Amihud冲击模型 LVaR Amihud Impact Model | / LVaR(Amihud冲击模型) / LVaR = VaR + ILLIQ × (Q/V)^α / 大仓位+非标资产 / ILLIQ=Amihud比率, Q=交易量, V=日均成交量, α≈0.5 / | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-3587 | LVaR EVT尾部模型 LVaR EVT Tail Model | / LVaR(EVT尾部模型) / LVaR = VaR + EVT_尾部流动性溢价 / 极端行情+流动性枯竭 / EVT拟合流动性指标尾部分布→尾部风险溢价 / | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-3588 | 空窗期定义 Window Period Definition | / 空窗期定义 / 定期报告披露间隔>90天的时期 / 11月-次年4月30日 / | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-3589 | 空窗期异常 Window Period Anomaly | / 空窗期异常 / 空窗期内换手率/波动率/收益率偏离正常水平 / z-score>2=异常 / | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-3590 | 对敲交易检测 Wash Trade Detection | 操纵行为检测间隔≤5秒+偏离≤1%+占比≥5%沪深交易所标准 | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-3591 | 尾盘操纵检测 End-of-day Manipulation Detection | 操纵行为检测最后5分钟价格变化>2%+成交量集中疑似操纵 | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-3592 | 收益归因 Return Attribution | **核心逻辑**: 交易绩效监控不只是'看盈亏'，而是**Performance Attribution**（归因分析）+ **Strategy Degradation Detection**（策略退化检测）。因子IC衰减=策略退化，需要自 | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-3593 | 自动降权 Auto De-weighting | / 自动降权 / 策略退化时自动将权重降为0 / Man Group AlphaGPT实践 / | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-3594 | AI自动触发 AI Auto Trigger | / 熔断器 / 电路断路器可在微秒内平仓 / 'hair-trigger'风险切割 / 熔断器模式(5次/60秒→OPEN) / | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-3595 | 人工一键触发 Manual One-click Trigger | / 熔断器 / 电路断路器可在微秒内平仓 / 'hair-trigger'风险切割 / 熔断器模式(5次/60秒→OPEN) / | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-3597 | 外部信号触发 External Signal Trigger | / 外部信号触发 / <1s / A9运维架构告警信号 / 基础设施层 / | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-3598 | L1代码隔离 L1 Code Isolation | / L1 代码隔离 / 风控代码与策略代码分属不同域(D-RISK vs D-SIGNAL/D-PF-*) / 域边界+依赖方向约束(INV-008) / | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-3599 | L2数据隔离 L2 Data Isolation | 四层隔离防护风险数据流独立于交易数据流独立管道+独立计算 | D_RISK | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-3600 | L3权限隔离 L3 Permission Isolation | / L3 权限隔离 / 风控引擎只读策略信号，只写否决指令 / RBAC+最小权限 / | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-3602 | 独立风险数据接入 Independent Risk Data Access | │  iFind数据 ────┤──→ [独立风险数据接入] ──→ 风险数据清洗  │ | D_RISK | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-3603 | 风险数据清洗 Risk Data Cleaning | 风险数据管道数据源层清洗+质量校验+属性级血缘 | D_RISK | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-3604 | 因子分布检测 Factor Distribution Detection | 事前PSI检测矩阵PSI+KS日频PSI>0.25→模型降级 | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-3605 | 特征分布检测 Feature Distribution Detection | 事前PSI检测矩阵Wasserstein距离+KS日频W>0.2→特征工程审查 | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-3606 | 模型输出检测 Model Output Detection | 事前PSI检测矩阵预测分布稳定性+CUSUM日频偏移>20%→模型审查 | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-3607 | 上游数据检测 Upstream Data Detection | 事前PSI检测矩阵Schema校验+空值率+格式实时空值率>5%→数据源切换 | D_RISK | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-3608 | L1共形校准更新 L1 Conformal Calibration Update | 事中在线适应三层机制TWC/RWC校准窗口滚动更新每日≤5秒 | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-3609 | L2模型降级 L2 Model Degradation | / L2 模型降级 / 模型从'自主执行'降为'仅建议' / PSI>0.25 / 性能衰减>5% / ≤1秒 / 降级后所有决策需人工确认 / | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-3610 | L3风控参数收紧 L3 Risk Parameter Tightening | 事中在线适应三层机制VaR限额收紧+仓位上限下调≤5秒 | D_RISK | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-3611 | 否决日志 Veto Log | / 否决日志 / 时间/规则/触发值/被否决指令 / ≥7年 / 哈希链+独立存储 / | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-3612 | 参数变更日志 Parameter Change Log | / 参数变更日志 / 变更前/后/审批人/时间/理由 / ≥7年 / 哈希链+独立存储 / | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-3613 | Kill Switch日志 Kill Switch Log | / Kill Switch日志 / 触发条件/时间/恢复时间/人工确认 / ≥7年 / 哈希链+独立存储 / | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-3614 | 漂移检测日志 Drift Detection Log | / 漂移检测日志 / PSI/KS/CUSUM值/检测时间/处置动作 / ≥3年 / 哈希链 / | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-3615 | Agent行为日志 Agent Behavior Log | / Agent行为日志 / 行为记录/越界检测/OWASP ASI分类/处置动作 / ≥3年 / 哈希链 / | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-3616 | Pod级止损日志 Pod-level Stop Loss Log | 风控审计策略ID/回撤值/止损级别/处置动作保留≥3年哈希链 | D_RISK | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-3617 | 港股→A股传导 HK-to-A-Share Transmission | / 港股→A股 / 恒生指数/AH溢价/北向资金 / T+0(盘中) / AH联动股受冲击 / 降AH联动股权重 / | D_RISK | harvest待评估（likely_planned） |  |
| CAND-HARVEST-3618 | 美股→A股传导 US-to-A-Share Transmission | / 美股→A股 / 隔夜美股/VIX/美债收益率 / T+1(次日开盘) / 开盘跳空风险 / 预调仓位(盘前) / | D_RISK | harvest待评估（likely_planned） |  |
| CAND-HARVEST-3619 | 期货→现货传导 Futures-to-Spot Transmission | 跨市场传导渠道股指期货升贴水/基差T+0盘中期货领跌/领涨 | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-3620 | 汇率→A股传导 FX-to-A-Share Transmission | 跨市场传导渠道人民币汇率/外汇储备T+0~T+1资金流入流出 | D_RISK | harvest待评估（likely_planned） |  |
| CAND-HARVEST-3621 | 成交量骤降模拟 Volume Drop Simulation | 流动性危机模拟滑点放大0.1%→5%+订单阻塞90%无法成交 | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-3622 | 买卖价差扩大模拟 Spread Widening Simulation | 流动性危机模拟价差扩大5-10倍+深度枯竭退出成本估算 | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-3623 | T+1锁定风险模拟 T+1 Lock Risk Simulation | 流动性危机模拟极端事件当日无法卖出+次日跳空隔夜风险敞口 | D_RISK | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-3624 | 相关性传染 Correlation Contagion | / 相关性传染 / 板块A暴跌→恐慌蔓延→板块B/C跟跌 / 条件相关性模型：危机时相关性趋近1 / 相关性崩塌模式(BS-002)自动处置 / | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-3625 | 策略拥挤踩踏 Strategy Crowding Stampede | / 策略拥挤踩踏 / 因子同质化→同步信号→同步卖出→价格崩塌 / AFMM执行耦合参数+策略指纹相似度 / 策略多样性约束(VR-013)+执行去耦(随机延迟) / | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-3626 | 信心传染 Confidence Contagion | / 信心传染 / 外围暴跌→国内恐慌→资金外流→进一步暴跌 / 跨市场传导模型(§14.2)+情绪指标 / 跨市场传导模式(BS-005)自动处置 / | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-3627 | Carry持有成本 Carry | 凸性预算框架维持对冲的预期年化拖累期权费+融资成本/名义敞口 | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-3628 | Convexity凸性收益 Convexity | > 尾部风险不是保险问题，是凸性问题(Landl 2026.3)。传统对冲(买Put)面临'Greek Trilemma'：Carry(持有成本) vs. Convexity(凸性收益) vs. Reliability(危机可靠性)——三者 | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-3629 | Reliability危机可靠性 Reliability | > 尾部风险不是保险问题，是凸性问题(Landl 2026.3)。传统对冲(买Put)面临'Greek Trilemma'：Carry(持有成本) vs. Convexity(凸性收益) vs. Reliability(危机可靠性)——三者 | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-3630 | 决策正确性缺口 Decision Correctness Gap | 保障缺口管理AI概率性95%准确率vs 100%风险底线风控否决权兜底HC-RISK-01 | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-3631 | 行为可预测缺口 Behavior Predictability Gap | 保障缺口管理AI非确定性LLM输出vs行为在预期边界内行为边界监控+Kill Switch | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-3632 | 故障可恢复缺口 Failure Recoverability Gap | 保障缺口管理AI可能产生级联错误vs故障隔离+快速恢复熔断器模式+降级策略 | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-3634 | 资金安全缺口 Fund Safety Gap | 保障缺口管理Agent可能执行非预期交易vs资金损失有补偿机制ARS双轨结算 | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-3635 | 自治等级未经审批升级 Autonomy Level Unauthorized Upgrade | 治理漂移场景自治等级变更审计+运行时等级校验需人工审批 | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-3636 | 风控参数渐进放松 Risk Parameter Gradual Relaxation | / 风控参数渐进放松 / 风控参数趋势分析+偏差检测 / 风控参数变更需人工审批(HC-RISK-04) / | D_RISK | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-3637 | 人类监督频率降低 Human Supervision Frequency Decrease | / 人类监督频率降低 / 人类确认频率监控+超时告警 / 人类确认不可跳过(HC-RISK-02) / | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-3638 | 静态治理规则过时 Static Governance Rules Outdated | ### §15.3 治理漂移(Governance Drift)防护 | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-3639 | 承保人 Underwriter | / 承保人(Underwriter) / 独立第三方评估Agent风险+收取保费 / 无独立第三方(单人系统) / ❌不能建——门禁条件：AUM增长到可聘请独立风控顾问 / | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-3640 | 抵押 Collateral | / Principal Track / 涉及资金操作的任务(如交易执行/仓位调整) / 承保(Underwriting)+抵押(Collateral)：承保人评估风险+要求抵押，失败时补偿 / AI执行交易→风控否决权兜底(HC-RISK- | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-3641 | 托管 Escrow | ARS要素报酬预存+条件释放人工确认机制作为人工托管 | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-3642 | 保费 Premium | ARS要素基于Agent风险等级的动态保费本系统无保费机制 | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-3903 | Tick风控 Tick风控检查 | Hot平面2ms延迟预算CPU核8-11 | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-3904 | 订单风控 订单风控检查 Risk Control Order | Hot平面3ms延迟预算 | D_RISK | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-3952 | 买入后即时验证与快速纠错模型 Post-Entry Validation | 买入后5-15分钟即时验证Intraday Momentum | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-3953 | 系统性风险分级预警与尾部风险管理模型 Tail Risk Management | VaR CVaR压力测试分级预警递进风控 | D_RISK | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-4102 | 违约风险 Default Risk | > 因交易对手违约导致损失的风险。当前系统为A股纯股票多头+单人管理，无OTC衍生品/融资融券/回购等交易对手敞口。D-RISK-09 Counterparty Risk Manager已定义但当前❌不能建——门禁条件未满足。 | D_RISK | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-4103 | 结算风险 Settlement Risk | 交收失败监控结算周期跟踪结算失败率未结算敞口 | D_RISK | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-4104 | 发行人体质恶化 Issuer Deterioration | 财务指标监控信用评级变动违约距离Merton模型DD | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-4105 | ESRB顺周期性风险向量 ESRB Procyclicality | 市场压力期间AI羊群行为策略同质化检测VR-013 | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-4106 | ESRB速度风险向量 ESRB Speed | 亚毫秒级连锁故障本系统小于10笔秒非高频天然免疫 | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-4107 | ESRB不透明性风险向量 ESRB Opacity | 黑箱决策链C-030决策可解释性审计链每笔决策可溯源 | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-4108 | ESRB模型同质性风险向量 ESRB Model Homogeneity | 相关故障模式策略指纹相似度相似度大于90%否决上线 | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-4109 | ESRB数据依赖风险向量 ESRB Data Dependency | 单一来源脆弱性数据源双源校验数据源切换空值率监控 | D_RISK | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-4110 | ESRB互联性风险向量 ESRB Interconnectedness | 放大的传染效应级联失败监控熔断器隔离OWASP ASI08 | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-4111 | ESRB运营风险向量 ESRB Operational Risk | AI系统故障健康检查心跳自动重启Kill Switch | D_RISK | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-4112 | ESRB网络脆弱性风险向量 ESRB Cyber Vulnerability | 模型投毒记忆完整性校验ASI06哈希校验清除受污染记忆 | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-4113 | ESRB市场操纵风险向量 ESRB Market Manipulation | 复杂AI幌骗撤单率监控行为模式检测撤单率大于15%限制 | D_RISK | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-4114 | ESRB监管套利风险向量 ESRB Regulatory Arbitrage | AI驱动规避穿透监管审计不可篡改同一实控人合并计算 | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-4115 | ESRB集中风险向量 ESRB Concentration Risk | AI提供商垄断模型数据源多样性多源数据模型异质性约束 | D_RISK | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-4116 | ESRB过度信任风险向量 ESRB Overreliance | / 12 / 过度信任(Overreliance) / 顺境中AI优异表现→过度信任→增加风险承担+阻碍监督 / 人类确认不可跳过(HC-RISK-02)+自治等级上限(风险架构§15.1) / | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-4117 | ESRB历史约束风险向量 ESRB History-Constrained | / 13 / 历史约束(History-Constrained) / AI依赖历史数据→无法应对未预见尾部事件→过度风险承担 / 反向压力测试(风险架构§14.4)+黑天鹅模式库(风险架构§14.1)+EVT尾部建模 / | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-4118 | ESRB法律地位未定风险向量 ESRB Untested Legal Status | / 14 / 法律地位未定(Untested Legal Status) / AI行为法律责任归属不明→系统性风险 / Named Accountability(风险架构§15.6)+AI输出视为工具输出(风险架构§9) / | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-4321 | Risk Manager 风控管理器(代码实现) | / l04_risk_management/risk_manager.py / RK-01 Risk Policy Manager / ✅已有 / | D_RISK | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-4322 | Risk Validator 风控校验器(代码实现) | / l04_risk_management/risk_validator.py / RK-02 Pre-Trade Checker / ✅已有 / | D_RISK | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-4323 | Stop Loss 止损(代码实现) | / l04_risk_management/stop_loss.py / RK-04 Stop Loss Engine / ✅已有 / | D_RISK | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-4324 | Risk Metrics 风控指标(代码实现) | / shared/contracts/risk/risk_metrics.py / RK-03 指标定义 / ✅已有 / | D_RISK | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-4325 | Kill Switch 紧急开关(代码实现) | / agent_rbac/kill_switch.py / RK-17 Kill Switch / ✅已有 / | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-4326 | Kill Switch Latency Check 紧急开关延迟检查(代码实现) | / check_kill_switch_latency.py / INV-001 验证 / ✅已有 / | D_RISK | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-4327 | Risk Params Consistency Check 风控参数一致性检查(代码实现) | / check_risk_params_consistency.py / INV-013 验证 / ✅已有 / | D_RISK | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-4340 | Fake Rally Real Distribution 假拉升真出货 | 假动作模式-盘中快速拉升吸引追涨+拉升时大单卖出>买入 | D_RISK | harvest待评估（likely_planned） |  |
| CAND-HARVEST-4341 | Fake Support Real Lure 假护盘真诱多 | 假动作模式-权重股拉升稳定指数+题材股不动 | D_RISK | harvest待评估（likely_planned） |  |
| CAND-HARVEST-4342 | Fake Rebound Real Distribution 假反弹真派发 | 假动作模式-超跌后反弹看似见底+反弹缩量+底部筹码未加长 | D_RISK | harvest待评估（likely_planned） |  |
| CAND-HARVEST-4343 | Spoofing Detection 幌骗交易检测 | / Spoof概率 / 综合Spoofing检测模型输出 / CNN/Transformer分类器 / Spoof概率>85%→暂停追涨 / | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-4344 | Related Account Coordination 关联账户协同性检测 | 协同交易检测-同步报撤单比例≥60%+方向一致性≥80% | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-4345 | Information Asymmetry Window 信息不对称空窗期 | 操纵行为检测-定期报告披露间隔>90天的时期(11月-次年4月30日) | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-4346 | Default Risk Validator 默认风控校验器(代码实现) | / l04_risk_management/implementations/default_risk_validator.py / RK-02 实现 / ✅已有 / | D_RISK | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-4347 | Default Risk Limits Calculator 默认风险限额计算器(代码实现) | / l04_risk_management/implementations/default_risk_limits_calculator.py / RK-03 实现 / ✅已有 / | D_RISK | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-4348 | Default Risk Manager Orchestrator 默认风控管理器编排器(代码实现) | / l04_risk_management/implementations/default_risk_manager_orchestrator.py / RK-01 编排 / ✅已有 / | D_RISK | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-4349 | Default Position Limit Checker 默认持仓限额检查器(代码实现) | / l04_risk_management/implementations/default_position_limit_checker.py / RK-06 实现 / ✅已有 / | D_RISK | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-4350 | Default Stop Loss Engine 默认止损引擎(代码实现) | / l04_risk_management/implementations/default_stop_loss_engine.py / RK-04 实现 / ✅已有 / | D_RISK | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-4433 | Instant Order Rate Anomaly 瞬时申报速率异常 | / 瞬时申报速率异常 / 短时间内申报量远超正常水平 / 每秒申报笔数超15笔/秒(2026.4.7新规异常交易行为阈值，同高频交易认定标准) / Hard Block:自动限速+告警 / 交易所实施细则 / | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-4434 | Frequent Instant Cancellation 频繁瞬时撤单 | / 频繁瞬时撤单 / 短时间内频繁申报和撤单 / 撤单率>15%(2026.4.7新规) / Hard Block:拒绝后续撤单+告警 / 交易所实施细则 / | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-4435 | Frequent Push-Pull 频繁拉抬打压 | / 频繁拉抬打压 / 多只股票小幅拉抬打压 / 价格偏离度+成交量占比 / Hard Block:暂停交易+告警 / 交易所实施细则 / | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-4436 | Short-time Large Volume 短时间大额成交 | / 短时间大额成交 / 同一机构多产品集中同向交易 / 合并持仓变动率 / Hard Block:限仓+告警 / 交易所实施细则 / | D_RISK | harvest待评估（likely_planned） |  |
| CAND-HARVEST-4437 | Almgren-Chriss Impact Model Almgren-Chriss冲击模型 | / 参与率冲击模型 / ≤Almgren-Chriss模型计算的市场冲击合理比例(须≤5%上限，取两者较小值) / Almgren-Chriss冲击模型约束 / 行业最佳实践(5%为法规上限，模型计算值通常更低；与上行5%上限共同构成双重约 | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-4438 | Sequential Evaluation 顺序评估 | **规则评估策略**：顺序评估(Sequential Evaluation)——规则按优先级排序，顺序评估：首个触发的Hard Block即终止评估并拒绝；Soft Block暂停等待审批；Warning记录告警但不阻断评估，继续评估后续规 | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-4439 | Fail-Closed 引擎故障处置 | §7.6 Pre-Trade合规检查模式-引擎故障处置-合规规则引擎不可用时C-004默认拒绝所有订单(Fail-Closed) | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-4440 | Spoofing 幌骗 | §7.7市场操纵防护-Spoofing幌骗-挂单-撤单模式识别+意图分析-C-004风控引擎实时检测(RK-02) | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-4441 | Layering 分层 | §7.7市场操纵防护-Layering分层-多价位同方向虚假挂单检测-C-004风控引擎实时检测(RK-02) | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-4442 | Wash Trade 洗盘 | / 洗盘(Wash Trade) / 自交易检测：同一实控账户互为对手方 / C-002执行域订单前检查(独立于C-004，因需跨账户数据)(→D-EX-CORE §7.4) / SEC Rule 10b-5；CFTC洗盘禁令 / | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-4443 | Late Session Manipulation 尾盘操纵 | §7.7市场操纵防护-尾盘操纵-收盘前N分钟异常交易检测-C-004风控引擎(RK-03) | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-4444 | Emergent Manipulation 涌现操纵模式 | §7.7 AI驱动操纵-涌现操纵模式-市场影响的严格责任-C-007闭环优化检测策略行为模式变化 | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-4445 | Volume-Price Consistency 量价一致性 | / 量价一致性 / 拉升段主动买入占比 / >65%（真拉升） / <40%（假拉升，对倒或卖单主导） / | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-4446 | Dragon-Tiger List Verification 龙虎榜验证 | §7.8.2假动作识别量化信号-龙虎榜验证-机构/游资席位行为-机构买入真吸筹游资一日游+机构卖出假动作 | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-4447 | CER Cancellation-to-Execution Ratio 撤单成交比 | / CER（Cancellation-to-Execution Ratio） / 撤单量/成交量的比率 / CER>95%在100ms窗口内=高概率Spoofing / 个股CER>90%=假动作嫌疑→Hard Block拒绝追涨 / | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-4448 | Order Life Duration 订单存续时间 | / Order Life Duration / 大单挂出后存续时间（毫秒） / 存续<100ms即撤=虚假挂单 / 大单存续<1秒即撤=虚假挂单嫌疑 / | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-4449 | Spoof Probability Spoof概率 | / CER（Cancellation-to-Execution Ratio） / 撤单量/成交量的比率 / CER>95%在100ms窗口内=高概率Spoofing / 个股CER>90%=假动作嫌疑→Hard Block拒绝追涨 / | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-4450 | Key Position Support Strength 关键点位护盘强度 | / 关键点位护盘强度 / 整数关口/前低附近的买一挂单量/日均成交额 / >5%且持续>30分钟=疑似护盘 / | D_RISK | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-4451 | Spoofing Trade Detection 幌骗交易检测(操纵行为) | §7.10.2操纵行为检测-幌骗交易-偏离≥2%+申报量≥10%+5秒内撤单≥80%-沪深交易所(2025.7)标准 | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-4452 | Wash Trade Detection 对敲交易检测(操纵行为) | §7.10.2操纵行为检测-对敲交易-间隔≤5秒+偏离≤1%+占比≥5%-沪深交易所(2025.7)标准 | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-4453 | Late Session Manipulation Detection 尾盘操纵检测 | §7.10.2操纵行为检测-尾盘操纵-最后5分钟价格变化>2%+成交量集中-疑似操纵 | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-4454 | VaR Phase 1 VaR三阶段Phase 1 | §6设计决策-VaR三阶段演进-Phase 1-历史模拟法VaR(基础阶段) | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-4455 | VaR Phase 2 VaR三阶段Phase 2 | §6设计决策-VaR三阶段演进-Phase 2-密度感知VaR+共形预测(增强阶段) | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-4456 | VaR Phase 3 VaR三阶段Phase 3 | §6设计决策-VaR三阶段演进-Phase 3-极值理论EVT+蒙特卡洛(高级阶段) | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-4457 | SignalAggregator 信号聚合器 | §3.5跨域铁三角-SignalAggregator-信号聚合器-D-SIGNAL→D-PF-CORE/D-RISK | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-4458 | OMS Order Management System 订单管理系统 | §3.5跨域铁三角-OMS-订单管理系统-D-PF-CORE/D-RISK→D-EX-CORE | D_RISK | harvest待评估（likely_planned） |  |
| CAND-HARVEST-4459 | Risk Intercept 风控拦截 | §4风控熔断因果链-风控拦截-Pre-Trade检查未通过→订单被拦截 | D_RISK | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-4460 | Position Circuit Breaker 持仓熔断 | §4风控熔断因果链-持仓熔断-持仓超限→持仓熔断触发 | D_RISK | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-4461 | A-Share Stop Loss A股止损 | §4风控熔断因果链-A股止损-A股特有止损规则触发 | D_RISK | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-4462 | L1 Pre-Trade L1盘前拦截 | / 职责 / **自适应风控**。Pre/Post-Trade风控+实时监控+熔断+Kill Switch+VaR+压力测试+拥挤度检测+黑天鹅模式库——资金安全的决策中枢 / | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-4463 | L2 Real-Time L2盘中监控 | §0三层防线-L2 Real-Time盘中监控-实时持仓+风险指标监控 | D_RISK | harvest待评估（likely_planned） |  |
| CAND-HARVEST-4464 | L3 Post-Trade L3盘后审计 | / 职责 / **自适应风控**。Pre/Post-Trade风控+实时监控+熔断+Kill Switch+VaR+压力测试+拥挤度检测+黑天鹅模式库——资金安全的决策中枢 / | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-4465 | Rule Engine 规则引擎(双引擎) | §0双引擎-规则引擎-确定性硬阻断-合规规则硬编码自动执行 | D_RISK | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-4466 | Statistical Engine 统计引擎(双引擎) | §0双引擎-统计引擎-概率性告警-基于统计模型的风险预警 | D_RISK | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-4495 | A-Share Stop Loss 6 Patterns A股特色止损6种模式 | / 2026-05-26 / A股特色止损6种模式 / 固定比例-7%/支撑破位/逻辑失效/竞价不及预期/分时破位/板块退潮 / A股T+1制度+行为金融学 / | D_RISK | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-4496 | A-Share Systemic Risk 5 Signals A股系统性风险5信号 | / 2026-05-26 / A股系统性风险5信号 / 融资盘/量化踩踏/流动性危机/政策转向/外围冲击 / A股市场特色 / | D_RISK | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-4497 | Rule Engine Configurable 规则引擎可配置化 | / 2026-05-26 / 规则引擎可配置化 / YAML/DSL规则文件+运行时加载，1500模块规模下硬编码不可维护 / 规则引擎标准实践 / | D_RISK | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-4498 | Dual-Engine Routing 双引擎路由 | / 2026-05-26 / 双引擎路由 / 确定性规则引擎→硬阻断/概率性统计引擎→告警+建议 / Basel III / | D_RISK | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-4499 | VaR Phase 1 Parameter Method VaR Phase 1参数法 | / Phase 3 / Basel III三角验证+乘数因子+压力VaR / 合规级风控 / 满足监管要求 / Phase 1+2 / | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-4500 | VaR Phase 2 Monte Carlo VaR Phase 2蒙特卡洛法 | / Phase 3 / Basel III三角验证+乘数因子+压力VaR / 合规级风控 / 满足监管要求 / Phase 1+2 / | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-4501 | VaR Phase 3 Basel III VaR Phase 3 Basel III三角验证 | / Phase 3 / Basel III三角验证+乘数因子+压力VaR / 合规级风控 / 满足监管要求 / Phase 1+2 / | D_RISK | harvest待评估（likely_new） |  |
| CAND-HARVEST-4808 | Distribution Fitting Engine 分布拟合引擎 | 旧子模块归并-→D-RISK | D_RISK | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-4886 | TailRiskManagement 灾难逃生 | VaR/CVaR/压力测试5级预警+递进风控动作 | D_RISK | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-4938 | Market Risk 市场风险 | VaR/CVaR/ES/压力测试/情景分析/密度感知VaR/共形VaR | D_RISK | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-4939 | Model Risk 模型风险 | SR 26-2/5类漂移检测/CUSUM/过拟合防护/训练-服务一致性 | D_RISK | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-4940 | AI/Agent Risk AI/Agent风险 | OWASP ASI+AST+MCP完整映射 | D_RISK | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-4941 | Risk Veto 风险否决权 | / — / 风险否决权 / 13条主规则VR-001~013+KillSwitch多路径激活+否决与策略逻辑隔离 / ✅ / | D_RISK | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-4942 | A-Share Compliance Custody A股合规代管 | 不操纵市场/持仓限额/涨跌停约束/A股风险日历 | D_RISK | harvest待评估（likely_planned） |  |
| CAND-HARVEST-4943 | Counterparty Risk 交易对手风险 | 需衍生品业务 | D_RISK | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-4944 | Credit Risk 信用风险 | 需债券持仓 | D_RISK | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-4945 | ESG Risk ESG风险 | 需ESG数据源 | D_RISK | harvest待评估（likely_implemented） |  |

## 复查时间表

> 按 next_review_date 升序。复查时重新过四问，触发信号命中则晋升到 depgraph 设计态。

| 下次复查 | 复查频率 | ID | 名称 | 域 | 状态 | 上次复查结论 |
|------|------|------|------|------|------|------|
| 2026-11-30 | quarterly | CAND-HARVEST-0072 | Risk Control 自适应风控 | D_RISK | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-0074 | Systematic Stress Testing 系统性压力测试 | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0085 | Systematic Overfitting Protection 过拟合系统性防护 | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0092 | 黑天鹅模式库与预判 Black Swan Pattern Library and Prediction | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0093 | 资金曲线自诊断与结构预警 Capital Curve Self-Diagnosis and Structure Warning | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0176 | Risk Policy Manager风控策略管理 | D_RISK | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-0177 | Pre-Trade Checker盘前检查 | D_RISK | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-0178 | Portfolio Risk Monitor持仓实时监控 | D_RISK | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-0179 | Stop Loss Engine止损引擎 | D_RISK | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-0180 | Stress Test Engine压力测试引擎 | D_RISK | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-0181 | VaR Calculator VaR计算器 | D_RISK | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-0182 | Risk Budget Allocator风险预算分配 | D_RISK | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-0183 | Risk Decomposition Engine风险分解引擎 | D_RISK | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-0184 | Concentration Risk Monitor集中度风险监控 | D_RISK | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-0185 | Risk Limit Manager风险限额管理 | D_RISK | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-0186 | Credit Risk Engine信用风险引擎 | D_RISK | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-0187 | A-Share Stop-Loss Rule Engine A股特色止损 | D_RISK | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-0188 | A-Share Systemic Risk Detector A股系统性风险检测 | D_RISK | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-0189 | A-Share Loss Limit Enforcer A股亏损限额强制执行 | D_RISK | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-0190 | Stop-Loss Engine止损引擎 | D_RISK | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-0191 | 仓位限制预检器 Position | D_RISK | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-0192 | 保证金比例安全检查器 Security | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0193 | 风险指标体系定义器 Risk | D_RISK | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-0194 | 紧急停止安全确认 Security | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0641 | VaR Compute Data Prefetcher VaR计算数据预取器 | D_RISK | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-0671 | 历史数据代表性验证器 Historical Data Representativeness Validator | D_RISK | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-0672 | Risk Policy Persister 风控策略持久化 | D_RISK | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-0673 | 双时态PositionSnapshot管理器 Bitemporal Position Snapshot Manager | D_RISK | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-0674 | VaR DuckDB历史模拟查询构建器 VaR DuckDB Query Builder | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0675 | 风险指标计算数据源依赖管理器 Risk Metric Data Dependency Manager | D_RISK | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-0712 | C-004 风控 Risk Control | D_RISK | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-0718 | C-038 黑天鹅检测 Black Swan Detection | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0728 | 风控状态物化视图 Risk Status View | D_RISK | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-0749 | Risk Budget Allocator 风险预算分配器 | D_RISK | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-0764 | Risk Policy Manager 风险策略管理器 | D_RISK | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-0765 | Pre-Trade Checker 盘前检查器 | D_RISK | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-0766 | Portfolio Risk Monitor 组合风险监控器 | D_RISK | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-0767 | Risk Limit Manager 风险限额管理器 | D_RISK | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-0768 | Concentration Risk Monitor 集中度风险监控器 | D_RISK | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-0769 | A-Share Stop-Loss Rule Engine A股止损规则引擎 | D_RISK | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-0770 | A-Share Systemic Risk Detector A股系统性风险检测器 | D_RISK | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-0771 | Drawdown Real-Time Tracker 回撤实时跟踪器 | D_RISK | 候选待评（candidate） | harvest待评估（likely_planned） |
| 2026-11-30 | quarterly | CAND-HARVEST-0772 | Crowding Risk Monitor 拥挤风险监控器 | D_RISK | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-0773 | Black Swan Pattern Library 黑天鹅模式库 | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0774 | Tail Risk Monitor 尾部风险监控器 | D_RISK | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-0775 | Kill Switch Integration Kill Switch集成 | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0776 | Fail-Closed Degradation Handler Fail-Closed降级处理器 | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0777 | Configurable Rule Engine 可配置规则引擎 | D_RISK | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-0778 | Post-Trade Daily Auditor 盘后日终审计器 | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0995 | Scenario Analyzer 情景分析器 | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0996 | Liquidity Risk Monitor 流动性风险监控器 | D_RISK | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-0997 | Risk Breach Logger 风险违规日志 | D_RISK | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-0998 | Counterfactual Analyzer 反事实分析器 | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0999 | Risk Rule DSL Compiler 风控规则DSL编译器 | D_RISK | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1000 | Risk Dashboard Generator 风险仪表盘生成器 | D_RISK | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1001 | Risk Report Auto-Generator 风险报告自动生成器 | D_RISK | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1002 | Risk Policy Backtester 风控策略回测器 | D_RISK | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1003 | Limit Consumption Predictor 限额消耗预测器 | D_RISK | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1004 | Leverage Dynamic Manager 杠杆动态管理器 | D_RISK | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1005 | A-Share Stock Blacklist Manager A股股票黑名单管理器 | D_RISK | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1006 | A-Share Stop-Loss/Circuit Breaker Series A股特色止损/熔断系列 | D_RISK | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1007 | VaR Enhancement Series VaR增强系列 | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1008 | Permission/Idempotency/Kill Switch/Approval Series 权限/幂等/Kill Switch/审批系列 | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1009 | VaR Scheduling/Concentration/ATR/Monte Carlo Series VaR调度/集中度/ATR/蒙特卡洛系列 | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1010 | YAML/SQLite/SLA/Contract/Migration Series YAML加载/SQLite/SLA/契约/迁移系列 | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1011 | Gate/Dashboard/Profile/DSL/Warehouse Series 门禁/仪表盘/画像/DSL/仓储系列 | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1020 | Risk Report Engine 风险报告引擎 | D_RISK | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1117 | Risk Assessment 风险评估 | D_RISK | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1318 | Trading Behavior Compliance Detector 交易行为合规检测器 | D_RISK | 候选待评（candidate） | harvest待评估（likely_planned） |
| 2026-11-30 | quarterly | CAND-HARVEST-1319 | Limit Up/Down Trading Constraint Executor 涨跌停交易约束执行器 | D_RISK | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1320 | Trading Rate Constraint Executor 交易速率约束执行器 | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1321 | Position Limit Compliance Detector 持仓限额合规检测器 | D_RISK | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1322 | Industry Concentration Compliance Detector 行业集中度合规检测器 | D_RISK | 候选待评（candidate） | harvest待评估（likely_planned） |
| 2026-11-30 | quarterly | CAND-HARVEST-1323 | Pre-Trade Three Block Mode Engine Pre-Trade三种阻塞模式引擎 | D_RISK | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1324 | Market Manipulation Prevention Detector 市场操纵防护检测器 | D_RISK | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1325 | Fake Move Identification Signal Engine 假动作识别信号引擎 | D_RISK | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1326 | Collaborative Trading Behavior Detector 协同交易行为检测器 | D_RISK | 候选待评（candidate） | harvest待评估（likely_planned） |
| 2026-11-30 | quarterly | CAND-HARVEST-1327 | Information Asymmetry Period Manipulation Detector 信息不对称期操纵检测器 | D_RISK | 候选待评（candidate） | harvest待评估（likely_planned） |
| 2026-11-30 | quarterly | CAND-HARVEST-1459 | Liquidity Evaporation 流动性蒸发 | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1460 | Correlation Collapse 相关性崩塌 | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1461 | Volatility Eruption 波动率爆发 | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1462 | Margin Call Stampede 融资盘踩踏 | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1463 | Cross-Market Contagion 跨市场传导 | D_RISK | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1464 | Policy Black Swan 政策黑天鹅 | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1465 | Systemic Risk 系统性风险 | D_RISK | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1806 | Pre-Trade Idempotency Guarantor 盘前幂等保证器 | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1807 | Pre-Trade Check Chain Orchestrator 盘前检查链编排器 | D_RISK | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1808 | Pre-Trade 50ms SLA Monitor 盘前50ms SLA监控器 | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1809 | Pre-Trade RiskCheckResult Router 盘前风控结果路由器 | D_RISK | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1810 | Order Generation Risk Pre-Check 订单生成风控前置 | D_RISK | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1811 | Max Drawdown Real-Time Tracker 最大回撤实时跟踪器 | D_RISK | 候选待评（candidate） | harvest待评估（likely_planned） |
| 2026-11-30 | quarterly | CAND-HARVEST-1812 | Sector Concentration Real-Time Calculator 行业集中度实时计算器 | D_RISK | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1813 | RiskLimit 9-Type Enum Manager 风险限额9类枚举管理器 | D_RISK | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1814 | Enforcement 3-Level Executor 执行3级执行器 | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1815 | Liquidity Limit Filter 流动性限制过滤器 | D_RISK | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1816 | Dynamic Position Adjuster 动态仓位调整器 | D_RISK | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1817 | Abnormal Trade Detection Interceptor 异常交易检测拦截器 | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1818 | Risk Audit Trail Writer 风险审计轨迹写入器 | D_RISK | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1819 | Normality Test Engine 正态性检验引擎 | D_RISK | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1820 | VaR Method Discrepancy Analyzer VaR方法差异分析器 | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1821 | VaR Fast Pre-Screen Alerter VaR快速预筛告警器 | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1822 | VaR Precise Confirmer VaR精确确认器 | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1823 | Two-Tier Alert Strategy Engine 双层告警策略引擎 | D_RISK | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1824 | VaR Concurrent Compute Orchestrator VaR并发计算编排器 | D_RISK | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1825 | VaR Cross-Validation Engine VaR交叉验证引擎 | D_RISK | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1827 | VaR Phase Independence Guarantor VaR阶段独立性保证器 | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1828 | Basel III Multiplier Factor Manager Basel III乘数因子管理器 | D_RISK | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1829 | Monte Carlo Precision Level Manager 蒙特卡洛精度级别管理器 | D_RISK | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1830 | Covariance Matrix Decomposer 协方差矩阵分解器 | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1831 | Risk Budget Adjuster 风险预算调整器 | D_RISK | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1832 | Risk Stress Tester 风控压力测试器 | D_RISK | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1833 | A-Share PDF Tail Risk Auto-Hedger A股PDF尾部风险自动对冲器 | D_RISK | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1834 | A-Share Contrarian Dedicated Stop-Loss A股逆向专用止损 | D_RISK | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1835 | A-Share Systemic Risk 3-Level Alerter A股系统性风险三级告警器 | D_RISK | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1836 | A-Share First-Minute Stop-Loss Executor A股首分钟止损执行器 | D_RISK | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1837 | A-Share Contrarian Time-Based Stop-Loss A股逆向时间止损 | D_RISK | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1838 | A-Share Multi-Level Loss Circuit Breaker A股多级亏损熔断器 | D_RISK | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1839 | A-Share 5-Signal Systemic Risk Scanner A股5信号系统性风险扫描器 | D_RISK | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1840 | A-Share Cascading Circuit Breaker A股级联熔断器 | D_RISK | 候选待评（candidate） | harvest待评估（likely_planned） |
| 2026-11-30 | quarterly | CAND-HARVEST-1841 | AISG Regulatory Compliance Checker AISG监管合规检查器 | D_RISK | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1842 | Kill Switch Cooldown Manager Kill Switch冷却期管理器 | D_RISK | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1843 | Kill Switch Trading System Integrator Kill Switch交易系统集成器 | D_RISK | 候选待评（candidate） | harvest待评估（likely_planned） |
| 2026-11-30 | quarterly | CAND-HARVEST-1844 | Kill Switch Multi-Domain Notifier Kill Switch多域通知器 | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1845 | Kill Switch State Machine Manager Kill Switch状态机管理器 | D_RISK | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1846 | Kill Switch New Order Rejector Kill Switch新订单拒绝器 | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1847 | Kill Switch Owner Confirmation Reset Gateway Kill Switch Owner确认重置网关 | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1848 | ATR Dynamic Stop Loss Calculator ATR动态止损计算器 | D_RISK | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1849 | Time-Based Stop Loss Evaluator 时间止损评估器 | D_RISK | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1850 | Risk Policy Approval Gateway 风险策略审批网关 | D_RISK | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1851 | Risk Policy DDD Aggregate Root AGG-007 Manager 风险策略DDD聚合根AGG-007管理器 | D_RISK | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1852 | RiskDashboardSnapshot CTR-P1-008 Builder 风险仪表盘快照CTR-P1-008构建器 | D_RISK | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1853 | RiskMetricsReport CTR-P1-011 Generator 风险指标报告CTR-P1-011生成器 | D_RISK | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1854 | Daily Risk Report Generator 每日风险报告生成器 | D_RISK | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1855 | Custom Risk Report Generator 风险报告自定义生成器 | D_RISK | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1856 | Real-time Risk Warning and Report Generator 实时风险预警与报告生成器 | D_RISK | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1857 | Strategy Correlation Gate Checker 策略相关性门禁检查器 | D_RISK | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1858 | Leverage Limit Gate Checker 杠杆限额门禁检查器 | D_RISK | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1859 | Risk Rule User Configurator 风险规则用户配置器 | D_RISK | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1860 | Risk Control Rule Engine 风险控制规则引擎 | D_RISK | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1861 | Risk Rule Validation and Stress Tester 风控规则验证与压力测试器 | D_RISK | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1862 | Rule Priority Sorter (Inter-Rule) 规则优先级排序(规则间) | D_RISK | 候选待评（candidate） | harvest待评估（likely_planned） |
| 2026-11-30 | quarterly | CAND-HARVEST-1863 | Risk Rule DSL Engine 风控规则DSL引擎 | D_RISK | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1864 | Risk Engine Rule DSL 风控引擎规则DSL | D_RISK | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1865 | Risk Rule Versioning and Hot Updater 风控规则版本化与热更新器 | D_RISK | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1866 | Rule Priority Sorter (Inter-Strategy) 规则优先级排序(策略间) | D_RISK | 候选待评（candidate） | harvest待评估（likely_planned） |
| 2026-11-30 | quarterly | CAND-HARVEST-1867 | CTR-006 PositionSnapshot Provider CTR-006仓位快照提供者 | D_RISK | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1868 | CTR-004 Order Consumer CTR-004订单消费者 | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1869 | CTR-003 RiskLimits Producer CTR-003风险限额生产者 | D_RISK | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1870 | Position Write Authority Arbiter 仓位写入权限仲裁器 | D_RISK | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1871 | Rule Engine vs Statistical Engine Router 双引擎路由器 | D_RISK | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1872 | Risk Rule YAML Runtime Loader 风险规则YAML运行时加载器 | D_RISK | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1873 | Risk Policy SQLite Schema Designer 风险策略SQLite Schema设计器 | D_RISK | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1874 | IV Parametric VaR to Historical Simulation Migrator 参数法VaR→历史模拟法迁移器 | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1875 | DefaultRiskValidator to Configurable Rule Engine Migrator DefaultRiskValidator→可配置规则引擎迁移器 | D_RISK | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1876 | Execution Result Feedback Consumption Bridger 执行结果反馈消费桥接器 | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1877 | Risk Domain Value Object Definition 风控域值对象定义 | D_RISK | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1878 | Risk Rule Engine Upgrade Migration Adapter 风控规则引擎升级迁移适配器 | D_RISK | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1879 | Counterparty Risk Manager 交易对手风险管理器 | D_RISK | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1880 | Market Digital Twin 市场数字孪生 | D_RISK | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1881 | Climate Risk Engine 气候风险引擎 | D_RISK | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1882 | Monte Carlo Batch Backtester 蒙特卡洛批量回测器 | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1883 | Monte Carlo Portfolio PnL Sorter 蒙特卡洛组合PnL排序器 | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1884 | AI-Enhanced Risk Engine AI增强风控引擎 | D_RISK | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1885 | AI Risk Engine Implementer AI风控引擎实现器 | D_RISK | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1886 | Personalized Risk Profile Builder 个性化风险画像构建器 | D_RISK | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-2002 | 风险传播建模 Risk Propagation Modeling | D_RISK | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-2047 | VaR Calculator 风险价值计算器 | D_RISK | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-2049 | 绩效归因 Performance Attribution | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2050 | Brinson模型 Brinson Model | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2052 | IC衰减检测 IC Decay Detection | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2053 | 拥挤度检测 Crowding Detection | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2054 | 自动降权 Auto Weight Reduction | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2112 | Risk Manager Agent 风控Agent | D_RISK | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-2141 | Hedge Execution 独立对冲执行 | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2243 | Kill Switch 紧急制动 | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2315 | Amihud Illiquidity Amihud非流动性指标 | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2316 | Reverse RST 反向RST指标 | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2317 | PSI/KS/CUSUM PSI/KS/CUSUM漂移检测指标 | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2344 | Veto Flow 否决流 | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2345 | P0-Emergency P0紧急指令 | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2346 | P1-High P1高优先级指令 | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2382 | Risk Report 风险报告 | D_RISK | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-2383 | Risk Audit 风控审计 | D_RISK | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-2618 | Black Swan Pattern Library 黑天鹅模式库7种模式 | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2624 | Model Risk SR 26-2 模型风险 | D_RISK | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-2625 | Liquidity Risk 流动性风险 | D_RISK | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-2626 | Operational Risk 操作风险 | D_RISK | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-2627 | AI Agent Specific Risk AI/Agent特有风险 | D_RISK | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-2674 | A Share Compliance Rule A股合规规则代管 | D_RISK | 候选待评（candidate） | harvest待评估（likely_planned） |
| 2026-11-30 | quarterly | CAND-HARVEST-2675 | Drift Detection Risk Closed Loop 漂移检测与风险闭环 | D_RISK | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-2676 | Extreme Event Black Swan 极端事件与黑天鹅 | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2677 | AI Agent Risk Governance AI/Agent风险治理 | D_RISK | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-2986 | Risk Control Agent 风险 | D_RISK | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-2996 | 风控域规则目录 Risk Domain Rule Catalog | D_RISK | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-3089 | ESRB 2025系统性风险报告 | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3094 | Unleash 2026 Kill Switch Unleash 2026紧急制动 | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3134 | 顺周期性 Pro-cyclicality | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3135 | 速度 Speed | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3139 | 集中度 Concentration | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3198 | KS-L1 软暂停 Kill Switch | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3199 | KS-L2 会话熔断 Kill Switch | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3200 | KS-L3 通道断开 Kill Switch | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3201 | KS-L4 硬停机 Kill Switch | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3216 | LVaR价差模型 | D_RISK | 候选待评（candidate） | harvest待评估（uncertain） |
| 2026-11-30 | quarterly | CAND-HARVEST-3217 | LVaR Amihud冲击模型 | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3218 | LVaR EVT尾部模型 | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3219 | CoVaR跨市场传染 | D_RISK | 候选待评（candidate） | harvest待评估（uncertain） |
| 2026-11-30 | quarterly | CAND-HARVEST-3220 | Grinold & Kahn容量公式 | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3304 | EVT极值理论 | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3323 | 市场风险 Market Risk | D_RISK | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-3324 | 价格风险 Price Risk | D_RISK | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-3325 | 波动率风险 Volatility Risk | D_RISK | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-3326 | 相关性风险 Correlation Risk | D_RISK | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-3327 | 尾部风险 Tail Risk | D_RISK | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-3328 | L1实时监控 L1 Real-time Monitoring | D_RISK | 候选待评（candidate） | harvest待评估（likely_planned） |
| 2026-11-30 | quarterly | CAND-HARVEST-3329 | L2日频因子风险模型 L2 Daily Factor Risk Model | D_RISK | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-3330 | L3压力测试 L3 Stress Testing | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3331 | 风险分级预警 Risk Tiered Alert | D_RISK | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-3332 | 模型风险 Model Risk | D_RISK | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-3333 | 模型设定风险 Model Specification Risk | D_RISK | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-3334 | 实现风险 Implementation Risk | D_RISK | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-3335 | 误用风险 Misuse Risk | D_RISK | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-3336 | 过拟合风险 Overfitting Risk | D_RISK | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-3337 | 模型组合风险 Model Combination Risk | D_RISK | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-3338 | 协变量漂移 Covariate Drift | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3339 | 概念漂移 Concept Drift Type | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3340 | 标签漂移 Label Drift | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3341 | 公平性漂移 Fairness Drift | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3342 | 上游数据漂移 Upstream Data Drift | D_RISK | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-3343 | CUSUM控制图 CUSUM Control Chart | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3344 | 流动性风险 Liquidity Risk | D_RISK | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-3345 | 市场深度风险 Market Depth Risk | D_RISK | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-3346 | 冲击成本风险 Impact Cost Risk | D_RISK | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-3347 | 退出时间风险 Exit Time Risk | D_RISK | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-3348 | 流动性螺旋风险 Liquidity Spiral Risk | D_RISK | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-3349 | 策略容量风险 Strategy Capacity Risk | D_RISK | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-3350 | Amihud ILLIQ 非流动性指标 | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3351 | Kyle Lambda 凯尔lambda | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3352 | Roll Spread Estimator 罗尔价差估计器 | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3353 | Pastor-Stambaugh 流动性因子 | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3354 | Almgren-Chriss最优执行框架 Almgren-Chriss Optimal Execution Framework | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3355 | 日内时变参与率 Intraday Time-Varying Participation Rate | D_RISK | 候选待评（candidate） | harvest待评估（likely_planned） |
| 2026-11-30 | quarterly | CAND-HARVEST-3356 | 流动性降级模式 Liquidity Degradation Mode | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3357 | 流动性调整VaR LVaR Liquidity-adjusted VaR | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3358 | CoVaR跨市场传染 CoVaR Cross-Market Contagion | D_RISK | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-3359 | 流动性螺旋模型 Liquidity Spiral Model | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3360 | 操作风险 Operational Risk | D_RISK | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-3361 | 系统故障 System Failure | D_RISK | 候选待评（candidate） | harvest待评估（likely_planned） |
| 2026-11-30 | quarterly | CAND-HARVEST-3362 | 人为错误 Human Error | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3363 | Agent失控 Agent Out-of-Control | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3364 | 买入后即时验证与快速纠错模型 Post-Entry Instant Validation Model | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3365 | AI/Agent特有风险 AI/Agent Specific Risk | D_RISK | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-3366 | 策略同质化 Strategy Homogeneity | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3368 | 影子MCP服务器 Shadow MCP | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3369 | 交易对手风险 Counterparty Risk | D_RISK | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-3370 | 信用风险 Credit Risk | D_RISK | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-3371 | VaR风险价值 Value at Risk | D_RISK | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-3372 | CVaR/ES条件风险价值 Conditional Value at Risk | D_RISK | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-3373 | 密度感知VaR Density-Aware VaR | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3374 | 共形VaR Conformal VaR | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3375 | 时间加权共形风险控制 Time-Weighted Conformal | D_RISK | 候选待评（candidate） | harvest待评估（likely_planned） |
| 2026-11-30 | quarterly | CAND-HARVEST-3376 | 分位数预测共形校准 TCP Conformal | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3377 | 体制加权共形风险控制 Regime-Weighted Conformal | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3378 | 状态自适应贝叶斯共形预测 State-Adaptive Bayesian CP | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3379 | 共形VaR回测 CP-VaR Backtesting | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3380 | 压力测试 Stress Testing | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3381 | 情景分析 Scenario Analysis | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3382 | 反向压力测试 Reverse Stress Testing | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3383 | 流动性骤降 Liquidity Sudden Drop | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3384 | 融资盘强平 Margin Call Forced Liquidation | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3385 | 政策黑天鹅 Policy Black Swan | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3386 | 跨市场传导 Cross-Market Transmission | D_RISK | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-3387 | 黑天鹅加T+1锁定 Black Swan with T+1 Lock | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3388 | 风险否决权 Risk Veto Power | D_RISK | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-3389 | Kill Switch 紧急停止开关 | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3390 | 强制减仓 Forced Position Reduction | D_RISK | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-3391 | 否决新开仓 Reject New Position | D_RISK | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-3392 | 否决单笔订单 Reject Single Order | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3393 | 建议性告警 Advisory Alert | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3394 | Pod级止损机制 Pod-Level Stop Loss | D_RISK | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-3395 | 否决执行引擎 Veto Execution Engine | D_RISK | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-3397 | Kill Switch多路径激活 Kill Switch Multi-Path Activation | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3398 | 四层隔离防护 Four-Layer Isolation | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3399 | ATR动态止损与Bayesian参数优化模型 ATR Dynamic Stop-Loss Model | D_RISK | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-3400 | 独立风险数据管道 Independent Risk Data Pipeline | D_RISK | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-3401 | 风险指标计算引擎 Risk Indicator Computing Engine | D_RISK | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-3402 | 漂移检测引擎 Drift Detection Engine | D_RISK | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-3403 | 压力测试引擎 Stress Test Engine Risk | D_RISK | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-3404 | Agent行为监控 Agent Behavior Monitor | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3406 | 风险仪表盘 Risk Dashboard | D_RISK | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-3407 | 告警系统 Alert System | D_RISK | 候选待评（candidate） | harvest待评估（likely_planned） |
| 2026-11-30 | quarterly | CAND-HARVEST-3408 | 日度风险摘要 Daily Risk Summary | D_RISK | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-3409 | 周度风险深度 Weekly Risk Deep Report | D_RISK | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-3410 | 月度风险治理 Monthly Risk Governance | D_RISK | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-3411 | 四级审批流 Four-Level Approval Flow | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3412 | 三平面一致性 Three-Plane Consistency | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3413 | 不操纵市场规则 No Market Manipulation Rules | D_RISK | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-3414 | 幌骗检测 Spoofing Detection | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3415 | 分层操纵检测 Layering Detection | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3416 | 自交易检测 Self-Trading Detection | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3417 | 程序化交易合规 Programmatic Trading Compliance | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3418 | 私募基金合规 Private Fund Compliance | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3419 | 信息不对称期与操纵行为检测模型 Information Asymmetry Detection Model | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3420 | A股风险日历 A-Share Risk Calendar | D_RISK | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-3421 | 漂移检测与风险闭环 Drift Detection Risk Loop | D_RISK | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-3422 | 交易绩效归因与策略退化检测模型 Performance Attribution Model | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3424 | Autoencoder重构异常检测 Autoencoder Anomaly Detection | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3425 | GAN对抗检测 GAN Adversarial Detection | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3426 | Transformer时序异常 Transformer Time-Series Anomaly | D_RISK | 候选待评（candidate） | harvest待评估（likely_planned） |
| 2026-11-30 | quarterly | CAND-HARVEST-3427 | 跨市场传导模型 Cross-Market Transmission Model | D_RISK | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-3428 | 流动性危机模拟 Liquidity Crisis Simulation | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3429 | 反向压力测试引擎 Reverse Stress Testing Engine | D_RISK | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-3430 | 二阶效应与传染模型 Second-Order Effect Contagion Model | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3431 | 凸性预算框架 Convexity Budget Framework | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3432 | 相关性体制转换 Correlation Regime Switching | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3433 | ESRB 14个AI风险放大向量 ESRB 14 AI Risk Amplification Vectors | D_RISK | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-3435 | 保障缺口管理 Guarantee Gap Management | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3436 | 治理漂移防护 Governance Drift Protection | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3437 | Agent行为监控 Agent Behavior Monitoring | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3438 | Agent红队测试 Agent Red Team Testing | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3439 | 金融治理越狱 FinJailbreak | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3440 | 合成虚假信息注入 AutoRedTrader | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3441 | BFSI领域自适应红队 FinRedTeamBench | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3442 | 交易管线扰动 TradeTrap | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3443 | ARS双轨结算模型 ARS Dual-Track Settlement | D_RISK | 候选待评（candidate） | harvest待评估（likely_planned） |
| 2026-11-30 | quarterly | CAND-HARVEST-3444 | Fee Track费用轨道 Fee Track | D_RISK | 候选待评（candidate） | harvest待评估（likely_planned） |
| 2026-11-30 | quarterly | CAND-HARVEST-3445 | Principal Track本金轨道 Principal Track | D_RISK | 候选待评（candidate） | harvest待评估（likely_planned） |
| 2026-11-30 | quarterly | CAND-HARVEST-3446 | Named Accountability命名问责人 Named Accountability | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3447 | Risk Management Core 风险管理核心 | D_RISK | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-3562 | 反推致崩溃情景 Reverse Derive Crash Scenario | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3563 | 评估情景合理性 Evaluate Scenario Plausibility | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3564 | 设计防护措施 Design Protection Measures | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3565 | DPG七场景 DPG Seven Scenarios | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3566 | 管线验证 Pipeline Validation | D_RISK | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-3567 | ARA五项原则 ARA Five Principles | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3568 | ARA治理方程 ARA Governance Equation | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3569 | ARS状态机语义 ARS State Machine Semantics | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3570 | TCP+Robbins-Monro偏移 TCP-RM | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3571 | 自适应共形推断 Adaptive Conformal Inference | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3572 | Portfolio CP 组合共形预测 | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3573 | QRF+Conformal 分位数回归森林+共形 | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3574 | Phase 1参数化高斯混合 Phase 1 Parametric Gaussian Mixture | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3575 | Phase 2 QNN量子神经网络 Phase 2 QNN | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3576 | Phase 3非参数化KDE Phase 3 Non-parametric KDE | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3577 | 追踪止损 Trailing Stop | D_RISK | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-3578 | Grid Search 网格搜索 | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3579 | Bayesian优化 Bayesian Optimization | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3580 | Walk-Forward验证 Walk-Forward Validation | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3581 | 体制自适应 Regime Adaptive | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3582 | ATR动态止盈 ATR Dynamic Take Profit | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3583 | 分批止盈 Batch Take Profit | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3584 | 时间止损 Time Stop Loss | D_RISK | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-3585 | LVaR价差模型 LVaR Spread Model | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3586 | LVaR Amihud冲击模型 LVaR Amihud Impact Model | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3587 | LVaR EVT尾部模型 LVaR EVT Tail Model | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3588 | 空窗期定义 Window Period Definition | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3589 | 空窗期异常 Window Period Anomaly | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3590 | 对敲交易检测 Wash Trade Detection | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3591 | 尾盘操纵检测 End-of-day Manipulation Detection | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3592 | 收益归因 Return Attribution | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3593 | 自动降权 Auto De-weighting | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3594 | AI自动触发 AI Auto Trigger | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3595 | 人工一键触发 Manual One-click Trigger | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3597 | 外部信号触发 External Signal Trigger | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3598 | L1代码隔离 L1 Code Isolation | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3599 | L2数据隔离 L2 Data Isolation | D_RISK | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-3600 | L3权限隔离 L3 Permission Isolation | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3602 | 独立风险数据接入 Independent Risk Data Access | D_RISK | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-3603 | 风险数据清洗 Risk Data Cleaning | D_RISK | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-3604 | 因子分布检测 Factor Distribution Detection | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3605 | 特征分布检测 Feature Distribution Detection | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3606 | 模型输出检测 Model Output Detection | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3607 | 上游数据检测 Upstream Data Detection | D_RISK | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-3608 | L1共形校准更新 L1 Conformal Calibration Update | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3609 | L2模型降级 L2 Model Degradation | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3610 | L3风控参数收紧 L3 Risk Parameter Tightening | D_RISK | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-3611 | 否决日志 Veto Log | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3612 | 参数变更日志 Parameter Change Log | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3613 | Kill Switch日志 Kill Switch Log | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3614 | 漂移检测日志 Drift Detection Log | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3615 | Agent行为日志 Agent Behavior Log | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3616 | Pod级止损日志 Pod-level Stop Loss Log | D_RISK | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-3617 | 港股→A股传导 HK-to-A-Share Transmission | D_RISK | 候选待评（candidate） | harvest待评估（likely_planned） |
| 2026-11-30 | quarterly | CAND-HARVEST-3618 | 美股→A股传导 US-to-A-Share Transmission | D_RISK | 候选待评（candidate） | harvest待评估（likely_planned） |
| 2026-11-30 | quarterly | CAND-HARVEST-3619 | 期货→现货传导 Futures-to-Spot Transmission | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3620 | 汇率→A股传导 FX-to-A-Share Transmission | D_RISK | 候选待评（candidate） | harvest待评估（likely_planned） |
| 2026-11-30 | quarterly | CAND-HARVEST-3621 | 成交量骤降模拟 Volume Drop Simulation | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3622 | 买卖价差扩大模拟 Spread Widening Simulation | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3623 | T+1锁定风险模拟 T+1 Lock Risk Simulation | D_RISK | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-3624 | 相关性传染 Correlation Contagion | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3625 | 策略拥挤踩踏 Strategy Crowding Stampede | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3626 | 信心传染 Confidence Contagion | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3627 | Carry持有成本 Carry | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3628 | Convexity凸性收益 Convexity | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3629 | Reliability危机可靠性 Reliability | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3630 | 决策正确性缺口 Decision Correctness Gap | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3631 | 行为可预测缺口 Behavior Predictability Gap | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3632 | 故障可恢复缺口 Failure Recoverability Gap | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3634 | 资金安全缺口 Fund Safety Gap | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3635 | 自治等级未经审批升级 Autonomy Level Unauthorized Upgrade | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3636 | 风控参数渐进放松 Risk Parameter Gradual Relaxation | D_RISK | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-3637 | 人类监督频率降低 Human Supervision Frequency Decrease | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3638 | 静态治理规则过时 Static Governance Rules Outdated | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3639 | 承保人 Underwriter | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3640 | 抵押 Collateral | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3641 | 托管 Escrow | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3642 | 保费 Premium | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3903 | Tick风控 Tick风控检查 | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3904 | 订单风控 订单风控检查 Risk Control Order | D_RISK | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-3952 | 买入后即时验证与快速纠错模型 Post-Entry Validation | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3953 | 系统性风险分级预警与尾部风险管理模型 Tail Risk Management | D_RISK | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-4102 | 违约风险 Default Risk | D_RISK | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-4103 | 结算风险 Settlement Risk | D_RISK | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-4104 | 发行人体质恶化 Issuer Deterioration | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4105 | ESRB顺周期性风险向量 ESRB Procyclicality | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4106 | ESRB速度风险向量 ESRB Speed | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4107 | ESRB不透明性风险向量 ESRB Opacity | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4108 | ESRB模型同质性风险向量 ESRB Model Homogeneity | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4109 | ESRB数据依赖风险向量 ESRB Data Dependency | D_RISK | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-4110 | ESRB互联性风险向量 ESRB Interconnectedness | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4111 | ESRB运营风险向量 ESRB Operational Risk | D_RISK | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-4112 | ESRB网络脆弱性风险向量 ESRB Cyber Vulnerability | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4113 | ESRB市场操纵风险向量 ESRB Market Manipulation | D_RISK | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-4114 | ESRB监管套利风险向量 ESRB Regulatory Arbitrage | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4115 | ESRB集中风险向量 ESRB Concentration Risk | D_RISK | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-4116 | ESRB过度信任风险向量 ESRB Overreliance | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4117 | ESRB历史约束风险向量 ESRB History-Constrained | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4118 | ESRB法律地位未定风险向量 ESRB Untested Legal Status | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4321 | Risk Manager 风控管理器(代码实现) | D_RISK | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-4322 | Risk Validator 风控校验器(代码实现) | D_RISK | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-4323 | Stop Loss 止损(代码实现) | D_RISK | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-4324 | Risk Metrics 风控指标(代码实现) | D_RISK | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-4325 | Kill Switch 紧急开关(代码实现) | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4326 | Kill Switch Latency Check 紧急开关延迟检查(代码实现) | D_RISK | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-4327 | Risk Params Consistency Check 风控参数一致性检查(代码实现) | D_RISK | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-4340 | Fake Rally Real Distribution 假拉升真出货 | D_RISK | 候选待评（candidate） | harvest待评估（likely_planned） |
| 2026-11-30 | quarterly | CAND-HARVEST-4341 | Fake Support Real Lure 假护盘真诱多 | D_RISK | 候选待评（candidate） | harvest待评估（likely_planned） |
| 2026-11-30 | quarterly | CAND-HARVEST-4342 | Fake Rebound Real Distribution 假反弹真派发 | D_RISK | 候选待评（candidate） | harvest待评估（likely_planned） |
| 2026-11-30 | quarterly | CAND-HARVEST-4343 | Spoofing Detection 幌骗交易检测 | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4344 | Related Account Coordination 关联账户协同性检测 | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4345 | Information Asymmetry Window 信息不对称空窗期 | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4346 | Default Risk Validator 默认风控校验器(代码实现) | D_RISK | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-4347 | Default Risk Limits Calculator 默认风险限额计算器(代码实现) | D_RISK | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-4348 | Default Risk Manager Orchestrator 默认风控管理器编排器(代码实现) | D_RISK | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-4349 | Default Position Limit Checker 默认持仓限额检查器(代码实现) | D_RISK | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-4350 | Default Stop Loss Engine 默认止损引擎(代码实现) | D_RISK | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-4433 | Instant Order Rate Anomaly 瞬时申报速率异常 | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4434 | Frequent Instant Cancellation 频繁瞬时撤单 | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4435 | Frequent Push-Pull 频繁拉抬打压 | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4436 | Short-time Large Volume 短时间大额成交 | D_RISK | 候选待评（candidate） | harvest待评估（likely_planned） |
| 2026-11-30 | quarterly | CAND-HARVEST-4437 | Almgren-Chriss Impact Model Almgren-Chriss冲击模型 | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4438 | Sequential Evaluation 顺序评估 | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4439 | Fail-Closed 引擎故障处置 | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4440 | Spoofing 幌骗 | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4441 | Layering 分层 | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4442 | Wash Trade 洗盘 | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4443 | Late Session Manipulation 尾盘操纵 | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4444 | Emergent Manipulation 涌现操纵模式 | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4445 | Volume-Price Consistency 量价一致性 | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4446 | Dragon-Tiger List Verification 龙虎榜验证 | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4447 | CER Cancellation-to-Execution Ratio 撤单成交比 | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4448 | Order Life Duration 订单存续时间 | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4449 | Spoof Probability Spoof概率 | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4450 | Key Position Support Strength 关键点位护盘强度 | D_RISK | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-4451 | Spoofing Trade Detection 幌骗交易检测(操纵行为) | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4452 | Wash Trade Detection 对敲交易检测(操纵行为) | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4453 | Late Session Manipulation Detection 尾盘操纵检测 | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4454 | VaR Phase 1 VaR三阶段Phase 1 | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4455 | VaR Phase 2 VaR三阶段Phase 2 | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4456 | VaR Phase 3 VaR三阶段Phase 3 | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4457 | SignalAggregator 信号聚合器 | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4458 | OMS Order Management System 订单管理系统 | D_RISK | 候选待评（candidate） | harvest待评估（likely_planned） |
| 2026-11-30 | quarterly | CAND-HARVEST-4459 | Risk Intercept 风控拦截 | D_RISK | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-4460 | Position Circuit Breaker 持仓熔断 | D_RISK | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-4461 | A-Share Stop Loss A股止损 | D_RISK | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-4462 | L1 Pre-Trade L1盘前拦截 | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4463 | L2 Real-Time L2盘中监控 | D_RISK | 候选待评（candidate） | harvest待评估（likely_planned） |
| 2026-11-30 | quarterly | CAND-HARVEST-4464 | L3 Post-Trade L3盘后审计 | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4465 | Rule Engine 规则引擎(双引擎) | D_RISK | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-4466 | Statistical Engine 统计引擎(双引擎) | D_RISK | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-4495 | A-Share Stop Loss 6 Patterns A股特色止损6种模式 | D_RISK | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-4496 | A-Share Systemic Risk 5 Signals A股系统性风险5信号 | D_RISK | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-4497 | Rule Engine Configurable 规则引擎可配置化 | D_RISK | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-4498 | Dual-Engine Routing 双引擎路由 | D_RISK | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-4499 | VaR Phase 1 Parameter Method VaR Phase 1参数法 | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4500 | VaR Phase 2 Monte Carlo VaR Phase 2蒙特卡洛法 | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4501 | VaR Phase 3 Basel III VaR Phase 3 Basel III三角验证 | D_RISK | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4808 | Distribution Fitting Engine 分布拟合引擎 | D_RISK | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-4886 | TailRiskManagement 灾难逃生 | D_RISK | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-4938 | Market Risk 市场风险 | D_RISK | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-4939 | Model Risk 模型风险 | D_RISK | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-4940 | AI/Agent Risk AI/Agent风险 | D_RISK | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-4941 | Risk Veto 风险否决权 | D_RISK | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-4942 | A-Share Compliance Custody A股合规代管 | D_RISK | 候选待评（candidate） | harvest待评估（likely_planned） |
| 2026-11-30 | quarterly | CAND-HARVEST-4943 | Counterparty Risk 交易对手风险 | D_RISK | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-4944 | Credit Risk 信用风险 | D_RISK | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-4945 | ESG Risk ESG风险 | D_RISK | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2027-01-31 | half_yearly | CAND-RSK-014 | Black Swan Pattern Library / 黑天鹅模式库 | D_RISK | 延后（deferred） | 首次登记,待VaR Phase2就绪或实盘极端行情时重新评估 |
| 2027-07-31 | yearly | CAND-PTC-001 | Pre-Trade Checker / 盘前统一检查器 | D_RISK | 否决（rejected） | rejected,q1已实现。除非 risk_validation_bridge 组合出现重大缺口,否则不再评估 |
