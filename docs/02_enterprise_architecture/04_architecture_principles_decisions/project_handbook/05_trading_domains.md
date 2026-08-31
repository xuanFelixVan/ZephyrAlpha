---
ttl: permanent
doc_type: architecture_view
title: 交易与策略域 / Trading Domains
owner: ZephyrAlpha-Owner
language: zh
---

# 05 · 交易与策略域

> 大白话项目现状。端到端交易链路 + 关键类 + AUTO 域清单 + 外链域文档。

## 1. 端到端数据流

```
D_MKT_DATA (NormalizedMarketData, CTR-001)
    │
    ▼
D_FACTOR (FactorBase.compute → FactorSignal, CTR-002)
    │  [FactorRegistry 装饰器自注册; AlphaSignalPipeline 驱动 5 阶段]
    ▼
D_SIGNAL (AlphaSignalPipeline: 合成→验证→分配; D_SIGQC 监控降级)
    │
    ▼
D_RISK (RiskLimitsCalculator → RiskLimits CTR-003; RiskValidator 预交易; 止损/熔断)
    │
    ▼
D_PORTFOLIO_CORE (StrategyBase.generate_target_weights, 受 RiskLimits 约束)
    │  [StrategyRegistry 自动发现]
    ▼
D_EX_CORE (ExecutionEngine.execute_order → OrderManager → Broker; 产出 Fill CTR-005)
    │
    ▼
D_BACKTEST (镜像实盘路径 via MatchingEngine+Portfolio+metrics, DecisionGate 门控 IS→WFA→OOS)
```

## 2. 关键域与类

### backtest（回测引擎）
- `MatchingEngine` — 撮合（委托纯函数 MatchingLogic，保证回测=实盘；A 股 T+1/涨跌停/停牌/100 股）
- `DecisionGate` — 3 阶段门控 IS→WFA→OOS（不可跳过；IS Sharpe>0.5 准入；OOS Sharpe≥70% IS）
- `PITManager` — PIT 铁律（AS-OF JOIN + Embargo，零前瞻）
- `WalkForward` — Walk-Forward 分析（滚动/锚定/扩展 + White's Reality Check）

### factor（因子框架）
- `FactorBase`（ABC，OCP 扩展点；`compute(data)->Series`）+ `FactorRegistry`（单例，装饰器自注册）

### signal_fundamental（信号管线）
- `AlphaSignalPipeline` 5 阶段：FACTOR_DISCOVERY → FACTOR_COMPUTE → SIGNAL_SYNTHESIS → SIGNAL_VALIDATION → CAPITAL_ALLOCATION

### risk（风险管理）
- `RiskManagerBase`（预+后+熔断）/ `RiskLimitsCalculator`（L1 硬限/L2 软限/L3 熔断）/ `RiskValidator`（HALT 抛异常，WARNING 仅日志）
- 不变量：熔断延迟 <1ms、日亏硬限、所有调用携带 idempotency_key

### ex_core（执行核心）
- `ExecutionEngine`（TWAP/VWAP/冰山 + SOR）/ `OrderManager`（PENDING→SUBMITTED→FILLED）/ `BrokerInterface`（OCP-003 扩展点）

### pf_core（组合核心）
- `StrategyBase`（`generate_target_weights`，OCP-002 扩展点）+ `StrategyRegistry`（装饰器自注册）

## 3. 域清单（AUTO）

<!-- AUTO-START:domain_list -->
<!-- 数据源：depgraph (PostgreSQL) | 最后同步：2026-08-17 -->

| 域 ID | 域名 | 层 | 节点数 |
|-------|------|----|-------|
| `D_GOVERNANCE` | 生命周期管理 | L2_domain | 763 |
| `D_GOV_SCRIPTS` | 脚本治理 | L2_domain | 544 |
| `D_AUTONOMY_CORE` | 自治核心 | L1_foundation | 507 |
| `D_AUDITTEST` | 审计测试套件 | L2_domain | 506 |
| `D_INFRA_RUNTIME` | 运行时集成 | L0_infrastructure | 467 |
| `D_DATA` | 数据接入层 | L1_foundation | 399 |
| `D_SHARED` | 共享服务 | L0_infrastructure | 393 |
| `D_GOV_AUDIT` | 审计追踪 | L2_domain | 389 |
| `D_GOV_CODE_QUALITY` | 代码质量治理 | L1_foundation | 243 |
| `D_FEEDBACK_LOOP` | 反馈循环引擎 | L1_foundation | 242 |
| `D_SECURITY` | 对抗验证 | L1_foundation | 237 |
| `D_GOV_ENFORCEMENT` | 规则执行 | L2_domain | 195 |
| `D_TRADING` | 交易运营 | L2_domain | 176 |
| `D_ASHARE_SIGNAL` | A股特色信号 | L2_domain | 161 |
| `D_INTELLIGENCE` | 上下文管理 | L2_domain | 159 |
| `D_FACTOR` | 因子 | L2_domain | 157 |
| `D_RISK` | 风控 | L2_domain | 143 |
| `D_INFRA_A2A` | A2A通信 | L0_infrastructure | 135 |
| `D_GOV_OPS_RESILIENCE` | 运维弹性治理 | L1_foundation | 117 |
| `D_EX_CORE` | 执行核心 | L2_domain | 114 |
| `D_GOV_DOCS` | 架构文档治理 | L2_domain | 103 |
| `D_INFRA_RECOVERY` | 回滚恢复 | L0_infrastructure | 100 |
| `D_ORCHESTRATOR` | 代理编排器 | L1_foundation | 97 |
| `D_INTEGRATION` | 管线路由 | L1_foundation | 92 |
| `D_BACKTEST` | 回测 | L2_domain | 84 |
| `D_SECURITY_LLM` | LLM防御 | L1_foundation | 79 |
| `D_GOV_DRIFT` | 漂移检测 | L2_domain | 77 |
| `D_FBL_DIAGNOSERS` | 反馈诊断器 | L1_foundation | 76 |
| `D_FRONTEND` | 前端 | L2_domain | 71 |
| `D_INFRASTRUCTURE` | 跨层契约基础设施 | L0_infrastructure | 71 |
| `D_FBL_VERIFICATION` | 反馈验证 | L1_foundation | 67 |
| `D_FBL_DETECTORS` | 反馈检测器 | L1_foundation | 66 |
| `D_REGIME` | 市场状态 | L2_domain | 64 |
| `D_REPORTING` | 报告 | L1_foundation | 58 |
| `D_COMPLIANCE` | 合规 | L2_domain | 51 |
| `D_ML_TRAIN` | 训练 | L2_domain | 47 |
| `D_AUTONOMY_PERM` | 自治保护 | L2_domain | 44 |
| `D_PF_CORE` | 组合核心 | L2_domain | 41 |
| `D_POSITION` | 仓位管理 | L2_domain | 40 |
| `D_GOV_RULE` | 规则治理 | L2_domain | 38 |
| `D_ALT_DATA` | 另类数据 | L1_foundation | 34 |
| `D_FUNDAMENTAL_SIGNAL` | 基本面信号 | L2_domain | 33 |
| `D_DATA_ENG` | 数据工程 | L1_foundation | 32 |
| `D_MKT_DATA` | 行情数据 | L1_foundation | 32 |
| `D_PLAN` | 预案引擎 | L2_domain | 31 |
| `D_SELL_DECISION` | 卖出决策 | L2_domain | 31 |
| `D_SIMULATION` | 仿真 | L2_domain | 30 |
| `D_INFRA_TELEMETRY` | 可观测性 | L0_infrastructure | 29 |
| `D_ARCH_SCRIPTS` | 架构治理脚本 | L2_domain | 27 |
| `D_DATA_GOV` | 数据治理 | L1_foundation | 26 |
| `D_EX_SOR` | 执行路由 | L2_domain | 22 |
| `D_KNOWLEDGE` | 知识管理 | L2_domain | 22 |
| `D_META_SCRIPTS` | 元治理脚本 | L2_domain | 21 |
| `D_PF_ALLOC` | 组合分配 | L2_domain | 20 |
| `D_OPS` | 反馈循环 | L1_foundation | 17 |
| `D_GOV_REPAIR` | 治理修复 | L2_domain | 16 |
| `D_CONTRACTS` | 共享契约 | L0_infrastructure | 15 |
| `D_SIGQC` | 信号质量控制 | L2_domain | 13 |
| `D_INFRA_OPS` | 基础设施运维 | L0_infrastructure | 12 |
| `D_ML_SERVE` | 推理 | L2_domain | 11 |
| `D_DATA_SEC` | 数据安全与契约 | L1_foundation | 10 |
| `D_DIGITAL_TWIN` | 数字孪生 | L2_domain | 8 |
| `D_EXEC_SIM` | 执行仿真 | L2_domain | 8 |
| `D_CROSS_ASSET` | 跨资产 | L2_domain | 7 |
| `D_ARCHIVE_SCRIPTS` | Archived Scripts | L2_domain | 6 |
| `D_INTEGRATION_GATEWAY` | 集成网关 | L1_foundation | 4 |
| `D_ARCH_GUARD` | 架构守护脚本 | L2_domain | 3 |
| `D_COMPLIANCE_SCRIPTS` | 合规治理脚本 | L2_domain | 3 |
| `D_DATA_SCRIPTS` | 数据治理脚本 | L2_domain | 2 |
| `D_RESEARCH` | 研究域 | — | 2 |
| `D_CODE_SCRIPTS` | 代码质量脚本 | L2_domain | 1 |
| `D_SEC_SCRIPTS` | 安全治理脚本 | L2_domain | 1 |
| `D_STRUCT_SCRIPTS` | 结构治理脚本 | L2_domain | 1 |
| `D_SIGLEGACY` | 信号遗留设计态 | L2_domain | 0 |

**合计 74 个域**
<!-- AUTO-END:domain_list -->

## 4. 外部权威源（逐域详解）

| 权威源 | 内容 | 路径 |
|--------|------|------|
| 域架构文档 | 逐域职责/类/函数/成熟度详解 | `docs/02_enterprise_architecture/02_domain_architecture_docs/`（`generate_domain_doc.py`） |
| 跨域矩阵 | 域间依赖 | `docs/02_enterprise_architecture/01_global_architecture_diagram/cross_domain_matrix.md` |
