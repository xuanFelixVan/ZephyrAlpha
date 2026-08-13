---
ttl: task_bound
title: 架构评审记录——37号流动性危机 Protocol 施工（新增 MOD-RK-21）
owner: ZephyrAlpha-Owner
language: zh
status: active
version: "1.0.0"
date: 2026-08-13
topic: arch_review_liquidity_crisis_utils
scope: 07_trading_decision_architecture
session: AI-LIQ-001
---

# 架构评审记录——37号流动性危机 Protocol 施工（新增 MOD-RK-21）

> 触发类型：新增模块（trae_036 gov_arch_002 四类触发之一）。
> 评审执行：AI-LIQ-001（统筹会话书面委派施工 37 号 Protocol，按 SOP v1.4.0 Step 1.8 执行 6 项清单）。
> 变更简述：新建 `src/zephyr/risk/core/liquidity_crisis_manager.py`（MOD-RK-21，D_RISK），承载 37 号 memo 已定义但未落码的 6 项算法（§3.1.1 sell_pressure / §3.1.2 spread / §3.5.1 涨跌停检测 / §3.6 危机恢复 / §3.8 盘中编排 / §3.2a IPO 抽离预警）。

## 6 项评审清单

| # | 检查项 | 结论 | 证据 |
|---|---|---|---|
| 1 | KB 决策冲突 | PASS | 37号 memo §4.1 拒绝的是"独立新建 LiquidityCrisisProtocol **检测**模块"（防双真相源）。本模块不重复检测——检测逻辑委托 MOD-RK-10（import 复用 `AshareSystemicRiskDetector.check()`），本模块只承载 memo §3.1.1/§3.1.2/§3.5.1/§3.6/§3.8/§3.2a 已定义但未落码的算法。与 memo 决策①-⑧ 无冲突 |
| 2 | 跨层循环依赖 | PASS | 依赖方向单向：MOD-RK-21 → MOD-RK-10（import）+ zephyr.shared.foundation.errors。MOD-RK-10/08 不反向依赖本模块。无环 |
| 3 | 可观测性 | PASS | 编排函数 INFO/WARNING 日志埋点（危机触发/恢复判定/级别迁移），纯函数零副作用 |
| 4 | 数据一致性 | PASS | 纯函数设计；唯一状态对象 LiquidityRecoveryState 由调用方持有传入（非模块级全局状态），无双写 |
| 5 | 回滚方案 | PASS | 全部新增文件（1 代码 + 1 测试 + 1 蓝图 + 登记条目）。回滚 = 删文件 + `apply_depgraph.py --remove-design-node` + 注册表条目回退，不影响存量模块 |
| 6 | 性能退化 | PASS | 单标的单次调用 O(1)（5档盘口列表求和 + 阈值比较）；盘中 30s 轮询全市场 ~5200 标的 ≈ 52k 次简单浮点运算/秒，单机无压力 |

## 文档更新清单

| 文件 | 更新内容 | 状态 |
|---|---|---|
| 37_liquidity_crisis_protocol.md | 施工完毕标注 + 已施工设施盘点补 MOD-RK-21 + 版本升级 | 施工后执行 |
| 00_index_trading_decision.md | §0 目录版本同步 + §7.3 占用表 | **阻塞**：bm-fill 会话占用 → 遗留项登记 |
| architecture_issue_registry.yaml | 新增 ARCH 条目（新模块登记铁律） | **阻塞**：bm-fill 会话占用 → 遗留项登记 |

## 评审结论

**PASS**（6/6 通过，0 否决条件命中）。

- 评审日期：2026-08-13
- 评审人：AI-LIQ-001（委派）
- 关联设计真源：docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/37_liquidity_crisis_protocol.md v1.0.18
