---
actual_disk_path: src/zephyr/backtest/
belongs_to: D_BACKTEST
classification: internal
construction_progress: partially_implemented
created_by: human_plus_agent
date: '2026-07-02'
depends_on: [MOD-L00-001, MOD-L02-001]
doc_type: blueprint
functional_domain: backtest
generation: 1
language: zh
last_updated: '2026-07-02'
last_verified: ''
layer: domain
module_id: MOD-BT-001
owner: ZephyrAlpha-Owner
parent_module: ''
priority: P1
references:
  - architecture_model/contracts/cross_layer_contracts.yaml#CTR-P1-016
  - architecture_model/events/domain_events.yaml#E-BT-01
rule_form: structural
scope: domain
ssot_claims:
  - backtest_engine_core
  - backtest_result_contract
  - backtest_event_lifecycle
stability: evolving
status: Active
summary: 'D_BACKTEST回测引擎域蓝图。双模式架构(向量化+事件驱动),统一归口回测引擎,消除research/intelligence/rollback多处置放。MVP 7个核心模块。'
tags: [backtest, D_BACKTEST, simulation]
template_for: ''
title: 'D_BACKTEST 回测引擎域蓝图'
ttl: permanent
verifiability: automated
version: 1.0.0
---

# Backtest Engine 蓝图+施工图 — D_BACKTEST回测引擎域,双模式架构统一归口

> module_id: MOD-BT-001 | version: 1.0.0 | status: Active | layer: domain
> actual_disk_path: src/zephyr/backtest/ | generation: 1 | construction_progress: partially_implemented
> 解除ARB-11 T2-deferred限制(2026-07-02),允许施工

<!-- temporal_type: permanent -->

## 概述

D_BACKTEST域是ZephyrAlpha量化系统的策略验证引擎。本蓝图定义回测引擎的架构设计、接口契约、施工指引和验收标准。

**核心架构决策(2026-07-02)**:
1. 回测引擎统一归口D_BACKTEST域,消除research/intelligence/rollback多处置放(已执行:删除5处碎片化代码,迁移到backtest/core+implementations)
2. 回测与仿真正交分离:回测(过去怎样)归D_BACKTEST,仿真(如果怎样)归D_SIMULATION
3. 双模式架构:向量化回测(快速筛选因子IC/IR)+事件驱动回测(精确验证策略PnL)
4. 解除ARB-11对回测的T2-deferred限制,允许施工——回测是因子库开发的前置依赖
5. BacktestResult注册为CTR-P1-016契约(source=D_BACKTEST, target=[D_PF_CORE, D_RISK, D_OPS])
6. 新增E-BT-01/02/03事件系列(BacktestCompleted/BacktestPassed/OverfittingDetected)

<!-- temporal_type: construction_temporary -->
## §0 代码对齐验证

### §0.1 代码文件清单

| 文件路径 | 状态 | 说明 |
|---------|------|------|
| src/zephyr/backtest/__init__.py | production | D_BACKTEST域入口,导出核心类 |
| src/zephyr/backtest/core/__init__.py | production | core子包入口 |
| src/zephyr/backtest/core/engine_base.py | production | BacktestEngineBase+BacktestResult+FactorDiscovery(冻结真源) |
| src/zephyr/backtest/implementations/__init__.py | production | implementations子包入口 |
| src/zephyr/backtest/implementations/vectorized_engine.py | production | DefaultBacktestEngine向量化回测 |
| src/zephyr/backtest/implementations/event_driven_engine.py | planned | 事件驱动回测(MVP待实现) |
| src/zephyr/backtest/core/matching_engine.py | planned | 撮合引擎(MVP待实现) |
| src/zephyr/backtest/core/portfolio.py | planned | 持仓/现金/PnL(MVP待实现) |
| src/zephyr/backtest/core/data_handler.py | planned | ClickHouse OHLCV按bar推送(MVP待实现) |
| src/zephyr/backtest/core/metrics.py | planned | Sharpe/Sortino/MaxDD/IC/IR(MVP待实现) |

**已清理的碎片化位置**(2026-07-02):
- ~~src/zephyr/research/backtest_base.py~~ → 迁移到backtest/core/engine_base.py
- ~~src/zephyr/research/default_backtest_engine.py~~ → 迁移到backtest/implementations/vectorized_engine.py
- ~~src/zephyr/intelligence/model_evaluation/backtest_base.py~~ → 已删除(未授权副本)
- ~~src/zephyr/intelligence/model_evaluation/implementations/default_backtest_engine.py~~ → 已删除(未授权副本)
- ~~src/zephyr/infrastructure/rollback/backtest_engine.py~~ → 已删除(回测代码误放回滚目录)

### §0.2 对齐验证矩阵

| 维度 | 声明 | 实际 | 一致性 |
|------|------|------|:------:|
| 域归属 | D_BACKTEST | src/zephyr/backtest/ | ✅ |
| 蓝图路径 | _domain_backtest/blueprint.md | 磁盘一致 | ✅ |
| module_id | MOD-BT-001 | 代码头一致 | ✅ |
| 冻结真源 | backtest/core/engine_base.py | freeze_manifest已更新 | ✅ |
| 契约注册 | CTR-P1-016 | cross_layer_contracts.yaml已注册 | ✅ |
| 事件注册 | E-BT-01/02/03 | domain_events.yaml已注册 | ✅ |

### §0.3 版本-代码映射

| 版本 | 代码状态 | 说明 |
|------|---------|------|
| v1.0.0 | engine_base.py + vectorized_engine.py已实现 | MVP基线,双模式中的向量化模式已就绪 |

### §0.4 SSoT与责任唯一性

- **回测引擎真源**: 本蓝图(MOD-BT-001) + src/zephyr/backtest/core/engine_base.py(冻结代码)
- **BacktestResult契约真源**: cross_layer_contracts.yaml#CTR-P1-016
- **回测事件真源**: domain_events.yaml#E-BT-01/02/03
- **冻结清单真源**: shared/contracts/freeze_manifest.yaml(L_BACKTEST层)

### §0.5 代码目录唯一性

D_BACKTEST域代码唯一存放于 `src/zephyr/backtest/`。禁止在research/、intelligence/、infrastructure/rollback/等目录存放回测代码。

<!-- temporal_type: permanent -->
## §1 设计背景与目标

### §1.1 背景

ZephyrAlpha数据库即将建成,因子库开发在即。回测引擎是验证因子有效性的"裁判"——没有可信的回测,因子库只是未经验证的数学公式集合。

**修复前状态**(2026-07-02调研发现35个问题):
- 回测代码散落在5处(research/intelligence×2/rollback/backtest空壳)
- 4个候选域(D_BACKTEST空壳/D_SIMULATION/D_INTELLIGENCE/D_RESEARCH不存在)互相矛盾
- BacktestResult未注册为契约,E-SIM-*事件不存在
- ARB-11 T2-deferred锁死导致蓝图-代码分离

### §1.2 目标范围

**MVP(v1.0.0)**:7个核心模块
1. core/engine_base.py — BacktestEngineBase + BacktestResult + FactorDiscovery ✅已实现
2. implementations/vectorized_engine.py — DefaultBacktestEngine向量化回测 ✅已实现
3. implementations/event_driven_engine.py — 事件驱动回测(待实现)
4. core/matching_engine.py — 撮合引擎(市价/限价/滑点)(待实现)
5. core/portfolio.py — 持仓/现金/PnL/净值曲线(待实现)
6. core/data_handler.py — 从ClickHouse读OHLCV按bar推送(PIT正确)(待实现)
7. core/metrics.py — Sharpe/Sortino/MaxDD/胜率/IC/IR(待实现)

**v1.1.0**:过拟合检测(SIM-18/38/56三层)+ Walk-Forward(SIM-19/25)

### §1.4 运行场景约束

- 回测为离线批量运行,非实时(单进程同步调用)
- 数据来源:ClickHouse(c1_market)通过DatabaseService访问,禁止裸clickhouse_driver.connect
- PIT(Point-in-Time)正确性:回测必须使用时间戳截面对齐,禁止未来函数
- A股特有约束:T+1锁定、涨跌停限制、停牌跳过、ST特别处理

### §1.5 利益相关者

| 角色 | 关注点 |
|------|--------|
| 因子研究员 | 向量化回测快速验证IC/IR |
| 策略开发者 | 事件驱动回测精确验证PnL |
| 组合管理(L05) | BacktestResult做策略遴选 |
| 风控(L04) | max_drawdown做风险预算校准 |
| 运维(L12) | 回测任务监控 |

### §1.6 差距

| 差距 | 严重度 | 修复计划 |
|------|:------:|---------|
| 事件驱动引擎未实现 | 高 | MVP Phase 2 |
| 撮合引擎未实现 | 高 | MVP Phase 1 |
| BacktestConfig未含risk_free_rate | 中 | v1.0.1 |
| DefaultBacktestEngine买入数量硬编码100股 | 中 | v1.0.1(改为按目标权重计算) |
| 手续费/滑点未实际扣除 | 中 | v1.0.1 |

### §1.7 典型场景

**场景1:因子快速筛选(向量化)**
研究员计算动量因子 → 向量化回测 → IC/IR/Sharpe → 筛选有效因子

**场景2:策略精确验证(事件驱动)**
策略开发者编写调仓逻辑 → 事件驱动回测 → 含滑点/手续费的PnL → 门禁检查 → E-BT-02 BacktestPassed

<!-- temporal_type: permanent -->
## §2 模块边界

### §2.1 职责边界

| 域 | 职责 | 边界声明 |
|----|------|---------|
| **D_BACKTEST** | 过去怎样:历史数据重放验证 | 回测引擎、撮合、PnL、绩效指标、过拟合检测 |
| D_SIMULATION | 如果怎样:场景生成/蒙特卡洛 | 蒙特卡洛模拟、压力测试、场景生成 |
| D_FACTOR | 因子计算 | 因子生产,不负责回测验证 |
| D_RESEARCH(概念) | 实验追踪 | 回测结果归档,不负责回测执行 |

**职责唯一性声明**:回测引擎的执行(撮合/PnL/绩效)唯一归口D_BACKTEST。D_SIMULATION可复用D_BACKTEST的撮合引擎做场景模拟,但不持有独立的回测执行代码。

## §3 架构设计

### §3.1 组件架构

```
┌──────────────────────── D_BACKTEST 域 ────────────────────────┐
│                                                                │
│  ┌─────────────────── core/ ───────────────────┐              │
│  │  engine_base.py    BacktestEngineBase(ABC)  │              │
│  │                    BacktestResult(dataclass)│              │
│  │                    FactorDiscovery          │              │
│  │  matching_engine.py 撮合引擎(市价/限价/滑点)│              │
│  │  portfolio.py      持仓/现金/PnL/净值       │              │
│  │  data_handler.py   ClickHouse→bar推送(PIT) │              │
│  │  metrics.py        Sharpe/Sortino/MaxDD/IC  │              │
│  └─────────────────────────────────────────────┘              │
│                                                                │
│  ┌─────────── implementations/ ───────────────┐               │
│  │  vectorized_engine.py   向量化回测(快速)   │               │
│  │  event_driven_engine.py 事件驱动回测(精确) │               │
│  └─────────────────────────────────────────────┘              │
│                                                                │
│  ┌─────────────────── api/ ───────────────────┐               │
│  │  (预留:对外API入口)                         │               │
│  └─────────────────────────────────────────────┘              │
│                                                                │
└────────────────────────────────────────────────────────────────┘
        ↑ CTR-001(行情)  ↑ CTR-002(因子信号)
        ↓ CTR-P1-016(BacktestResult)  ↓ E-BT-01/02/03(事件)
```

### §3.2 数据流

```
输入:
  D_MKT_DATA ──CTR-001 NormalizedMarketData──→ data_handler.py
  D_FACTOR   ──CTR-002 FactorSignal──────────→ vectorized_engine / event_driven_engine

处理:
  data_handler.py ──按bar推送OHLCV──→ engine
  engine ──信号──→ matching_engine.py ──成交──→ portfolio.py
  portfolio.py ──净值序列──→ metrics.py ──指标──→ BacktestResult

输出:
  BacktestResult(CTR-P1-016) ──→ D_PF_CORE(策略遴选)
                               ──→ D_RISK(风险预算)
                               ──→ D_OPS(任务监控)

事件:
  E-BT-01 BacktestCompleted ──→ L05/L04/L07/L08(P1-15,E-RS-02对齐,来源:01-跨域/20-D-RESEARCH)
  E-BT-02 BacktestPassed    ──→ L05/L08(触发E-PF-01)
  E-BT-03 OverfittingDetected ──→ L02(因子衰减)/L08
```

### §3.3 状态生命周期

```
[待启动] ──参数锁定──→ [数据准备] ──PIT快照──→ [回测运行]
                                                │
                                    ┌───────────┴───────────┐
                                    │                       │
                              [向量化完成]            [事件驱动完成]
                                    │                       │
                                    └───────┬───────────────┘
                                            ↓
                                    [绩效计算] ──→ [过拟合检测]
                                            │                       │
                                    ┌───────┴───────┐
                                    ↓               ↓
                              [通过门禁]      [过拟合/未通过]
                                    │               │
                              E-BT-02          E-BT-03
```

**3阶段决策门控(P0-14,来源:学习系统架构§8.1)**:
1. **IS(In-Sample)阶段**:样本内回测→参数优化→稳定性门控
2. **WFA(Walk-Forward Analysis)阶段**:滚动Walk-Forward→多数通过+灾难否决
3. **OOS(Out-of-Sample)阶段**:参数锁定(不可调整)→通过→正式上线(需人工审批)

**参数稳定性区域**:参数扫描→识别稳定高原→选高原中心→避悬崖型参数

**V1-V6分层验证门禁(P1-26)**:Walk-Forward贯穿V1(单元测试)→V2(集成测试)→V3(样本外回测)→V4(Walk-Forward)→V5(模拟交易)→V6(实盘灰度),每级门禁通过才进入下一级(来源:12-D-ML-TRAIN)

## §4 接口契约

### §4.1 公共 API

```python
# 向量化回测(快速)
from zephyr.backtest.implementations.vectorized_engine import DefaultBacktestEngine, BacktestConfig
engine = DefaultBacktestEngine()
result = engine.run(data=data_df, signals=signals_df, initial_capital=1_000_000)

# 事件驱动回测(精确) — MVP Phase 2
from zephyr.backtest.implementations.event_driven_engine import EventDrivenEngine
engine = EventDrivenEngine(config=BacktestConfig(...))
result = engine.run(data_handler=data_handler, strategy=strategy)

# OCP扩展(自定义引擎)
from zephyr.backtest.core.engine_base import BacktestEngineBase
class MyEngine(BacktestEngineBase):
    def run(self, signals, prices) -> BacktestResult: ...
```

### §4.2 数据模型

**BacktestResult**(CTR-P1-016契约,15字段):
- strategy_id: str
- start_date / end_date: datetime
- total_return / annual_return / sharpe_ratio / max_drawdown: float
- win_rate: float (0.0-1.0)
- trades_count: int
- timestamp: datetime
- overfitting_flag: bool (可选,默认False)
- benchmark_symbol: Optional[str]

**BacktestConfig**(5字段,P0补充risk_free_rate):
- initial_capital: Decimal (默认1,000,000)
- commission_rate: Decimal (手续费率)
- slippage_bps: Decimal (滑点bps)
- benchmark_symbol: str (基准标的)
- risk_free_rate: float (无风险利率,默认中国10年期国债收益率,用于Sharpe计算,来源:D-SIMULATION-23)

### §4.3 输入契约

| 契约 | 来源 | 用途 |
|------|------|------|
| CTR-001 NormalizedMarketData | D_MKT_DATA | 行情数据输入 |
| CTR-002 FactorSignal | D_FACTOR | 因子信号输入 |
| CTR-P1-010 SystemConfiguration | D_INFRA_OPS | 回测参数配置 |

### §4.4 输出契约

| 契约 | 目标 | 用途 |
|------|------|------|
| CTR-P1-016 BacktestResult | D_PF_CORE/D_RISK/D_OPS | 回测结果标准化传递 |

### §4.5 MCP 接口

无(回测为离线工具,不提供MCP接口)。

### §4.6 契约版本

| 契约 | 版本 | 冻结状态 |
|------|------|---------|
| CTR-001 | 1.0 | frozen/locked-5yr |
| CTR-002 | 1.0 | frozen/locked-5yr |
| CTR-P1-016 | 1.0 | frozen/upgradable |

### §4.7 OCP 扩展点

`BacktestEngineBase`是OCP扩展点(abc.ABC):
- 子类MUST实现`run()`方法
- 注册表机制:`BacktestEngineBase._registry`自动注册子类
- 已注册子类:DefaultBacktestEngine(向量化)、EventDrivenEngine(待实现)

## §5 约束条件

### §5.1 技术约束

**数据访问**:
- 数据库访问:必须通过DatabaseService访问ClickHouse(c1_market),禁止裸clickhouse_driver.connect
- 数据库连接:必须显式指定read_only=True
- **Feature Store PIT正确性 R-02**:回测数据源必须通过FeatureStore PIT接口获取,避免look-ahead bias,是回测可信性基石(来源:D-RESEARCH R-02)

**PIT铁律(零容忍,违反→fail_backtest直接失败退出)**:
- **INV-004 零前瞻偏差**:禁止使用未来数据,所有截面按timestamp对齐(来源:D-FACTOR INV-004)
- **INV-014 Survivorship Bias零容忍**:回测必须包含退市股票,幸存者偏差=假alpha(来源:D-DATA INV-014)
- **PIT三平面一致性**:训练/回测/推理三平面因子值必须一致,回测用事件回放(AS OF JOIN),禁止用未来截面(来源:01-跨域交叉点与因果链)
- **PIT隔离(P0-12)**:回测强制按时间点查询,禁止访问未来数据,数据访问接口强制AS OF(来源:安全架构)
- **PIT三公理+Embargo期(P0-13)**:三公理(时点标记/版本对齐/泄漏防护)+Embargo期(标签泄露隔离期)+pit_consistency_test() CI/CD(偏差>1%告警)(来源:数据架构)

**交易规则**:
- A股T+1:买入当日不可卖出,持仓锁定1日
- Decimal优先:价格计算用Decimal,禁止float算术(聚合指标IC/Sharpe可用float)

**过拟合否决(P0)**:
- **样本外Sharpe<70%样本内→否决上线(P0-9)**:过拟合否决阈值(来源:13-D-ML-SERVE/风险架构)

### §5.2 容量估算

| 维度 | 估算 | 说明 |
|------|------|------|
| 单次回测内存 | <2GB | 全A股4000+标的×252交易日×OHLCV |
| 向量化回测耗时 | <30s | 日频,1年回测期 |
| 事件驱动回测耗时 | <300s | 日频,1年回测期(含撮合) |
| 模块数 | 7(MVP)→15(v1.1) | 容量≤150,无需拆分 |

### §5.3 迁移

**已完成迁移**(2026-07-02):
- research/backtest_base.py → backtest/core/engine_base.py
- research/default_backtest_engine.py → backtest/implementations/vectorized_engine.py
- 删除3处未授权/误放副本
- 更新11处引用路径
- freeze_manifest.yaml冻结路径已更新

### §5.4 非功能需求与服务水平

| 指标 | SLA | 说明 |
|------|-----|------|
| 向量化回测可用性 | 99% | 离线工具,容忍偶尔失败 |
| 数据PIT正确性 | 100% | 零容忍未来函数 |
| 回测结果可复现 | 100% | 相同输入必须相同输出 |

### §5.5 自动化触发机制

- 触发方式:因子库提交后自动触发向量化回测(通过E-RS-01 FactorResearched事件)
- 事件驱动回测:策略代码提交后手动/CI触发
- **回测Sharpe准入门控(P0-10)**:Sharpe>0.5才能进入模拟阶段(来源:06-D-PF-ALLOC)
- **回测-实盘偏差监控(P0-11)**:偏差>30%告警,>50%策略退役;GAP-AP-07回测-实盘偏差监控器自动检测(来源:06-D-PF-ALLOC/23-D-AUT-PERM)
- **回测门禁C-007(P1-12)**:每轮迭代改动必须过回测门禁(Sharpe/MaxDD/换手率阈值),未过阻断合并(来源:交易决策架构)
- **R-126 Backtest-to-Production Deployer(P1-28)**:回测通过→门控审批→灰度发布→全量上线,自动化部署管道(来源:学习系统架构)

### §5.7 禁止模式与导入约束

- 禁止从zephyr.research导入回测代码(已迁移)
- 禁止从zephyr.intelligence.model_evaluation导入回测代码(已删除)
- 禁止在infrastructure/rollback/存放回测代码
- 禁止裸clickhouse_driver.connect,必须通过DatabaseService

## §6 错误处理

### §6.1 可观测性

- 回测开始/结束日志(含strategy_id、period、config_hash)
- 撮合失败日志(含symbol、reason)
- 过拟合检测结果日志(含detection_method、degradation_ratio)

### §6.2 退化矩阵

| 故障 | 退化行为 | 降级模式 |
|------|---------|---------|
| ClickHouse连接失败 | 抛出DatabaseConnectionError | 不降级(回测无法运行) |
| 数据缺失(停牌) | 跳过该标的该日 | 标记is_suspended |
| 撮合失败(涨跌停) | 撮合拒绝,记录日志 | 跳过该笔交易 |
| 过拟合检测异常 | 返回overfitting_flag=False | 保守放行,人工复核 |

## §8 安全考量

- 数据库连接read_only=True,防止回测误写数据库
- 回测代码在沙盒中运行,禁止访问生产交易系统
- 策略代码审查:回测通过后需人工review才可进入候选池(E-BT-02 causal_precondition)

## §9 测试策略

| 测试类型 | 覆盖范围 | 状态 |
|---------|---------|------|
| 单元测试 | engine_base/metrics/portfolio | planned |
| 集成测试 | vectorized_engine端到端 | planned |
| PIT正确性测试 | data_handler时间戳对齐 | planned |
| 回归测试 | 已知策略的已知结果复现 | planned |
| 过拟合检测测试 | 样本内外绩效差异 | v1.1.0 |

## §10 依赖关系

### §10.5 概念重叠声明

| 概念 | 域 | 关系 |
|------|-----|------|
| 回测(backtest) | D_BACKTEST | 过去怎样,历史重放 |
| 仿真(simulation) | D_SIMULATION | 如果怎样,场景生成 |
| 实验(experiment) | D_INTELLIGENCE | A/B对比,ExperimentPipeline |

回测与仿真正交,D_BACKTEST的撮合引擎可被D_SIMULATION复用。

### §10.6 依赖链风险评级

| 依赖 | 类型 | 风险 | 缓解 |
|------|------|:----:|------|
| CTR-001(行情) | 硬依赖 | 低 | 已冻结locked-5yr |
| CTR-002(因子) | 硬依赖 | 低 | 已冻结locked-5yr |
| ClickHouse | 硬依赖 | 中 | 通过DatabaseService抽象(待实现get_clickhouse_conn) |

## §11 产出物

| 产出物 | 契约 | consumer_min | 说明 |
|--------|------|-------------|------|
| BacktestResult | CTR-P1-016 | D_PF_CORE | 回测结果,策略遴选输入 |
| E-BT-01事件 | domain_events | L05/L04/L07 | 回测完成通知 |
| E-BT-02事件 | domain_events | L05/L08 | 回测通过门禁 |
| E-BT-03事件 | domain_events | L02/L08 | 过拟合检测告警 |

## §12 集成目标

| 集成点 | 目标域 | 状态 | 触发条件 |
|--------|--------|:----:|---------|
| 策略遴选 | D_PF_CORE | planned | E-BT-02 BacktestPassed |
| 风险预算 | D_RISK | planned | CTR-P1-016 max_drawdown |
| 因子衰减 | D_FACTOR | planned | E-BT-03 OverfittingDetected |
| 任务监控 | D_OPS | planned | E-BT-01 BacktestCompleted |
| 信号回测(P1-25) | D_SIGNAL | planned | 信号驱动回测+多重检验校正(来源:04-D-SIGNAL) |

## §13 需要更新

| 更新项 | 位置 | 说明 |
|--------|------|------|
| blueprint_registry.yaml | 新增MOD-BT-001注册项 | ✅已完成(2026-07-02, sync_registry_from_blueprints --write, 54→55) |
| depgraph PostgreSQL | D_BACKTEST域激活(10节点:3 production+6 prototype+1 deprecated, 全部关联MOD-BT-001) | ✅已完成(2026-07-02) |
| master_blueprint索引 | 加入D_BACKTEST入口 | ✅已完成(2026-07-02, index.md §2.1 + _system_master §40.2域归属声明) |

## §14 风险

| 风险 | 概率 | 影响 | 缓解 |
|------|:----:|:----:|------|
| PIT数据错误导致回测失真 | 中 | 高 | data_handler严格按timestamp对齐 |
| 过拟合检测未实现导致伪alpha | 高 | 高 | v1.1.0优先实现SIM-18/38/56 |
| 事件驱动引擎复杂度超预期 | 中 | 中 | MVP先做向量化,事件驱动Phase 2 |

## §16 施工指引

### §16.7 参考实现规格

**Phase 1(MVP核心,已部分完成)**:
1. ✅ core/engine_base.py — BacktestEngineBase+BacktestResult
2. ✅ implementations/vectorized_engine.py — DefaultBacktestEngine
3. ⬜ core/matching_engine.py — 撮合引擎(市价/限价/滑点模型)
4. ⬜ core/portfolio.py — 持仓/现金/PnL/净值曲线
5. ⬜ core/data_handler.py — 数据处理器(详见下方规格)
6. ⬜ core/metrics.py — 指标计算(详见下方规格)

**Phase 2(事件驱动)**:
7. ⬜ implementations/event_driven_engine.py — EventLoop+DataHandler+ExecutionHandler

**Phase 3(过拟合检测)**:
8. ⬜ core/overfitting_detector.py — 过拟合检测(详见下方规格)
9. ⬜ core/walk_forward.py — Walk-Forward优化

**metrics.py 详细规格**(P0,来源:D-SIMULATION-23/24/45):
- **Sharpe计算修正**:
  - 无风险利率:中国10年期国债收益率(从BacktestConfig.risk_free_rate传入)
  - 样本量<60:不计算Sharpe(样本不足,返回NaN)
  - 非正态分布:用Sortino替代(下行风险)
  - 年化:按回测频率自动选择(日频×sqrt(252)/周频×sqrt(52)/月频×sqrt(12))
  - 滚动rolling:支持滚动Sharpe(窗口可配,默认252)
- **DSR(Deflated Sharpe Ratio)**:
  - 多重测试偏差修正(试次数N调整)
  - DSR<0.5判定为过拟合
  - 来源:D-SIMULATION-24
- **统计显著性(P1-14)**:t检验(p<0.05显著),来源:D-SIMULATION-45
- 基础指标:Sharpe/Sortino/MaxDD/IC/IR/Calmar/WinRate
- **DSR扩展(P1-17)**:考虑策略间相关性的DSR修正,组合层面多重测试偏差校正(来源:学习系统架构§8.1)
- **Probabilistic Backtesting(P1-21)**:贝叶斯回测,计算P(Sharpe>0)后验概率,替代传统p-value(来源:学习系统架构§8.1)

**overfitting_detector.py 详细规格**(P0,来源:D-FACTOR-03/D-SIMULATION-18/56):
- **过拟合检测三维度**(D-FACTOR-03):
  1. Walk-Forward:滚动窗口样本外验证,参数稳定性
  2. 参数敏感性:参数微调±10%,收益变化幅度
  3. 泛化能力:跨时段/跨市场/跨标的稳健性
- **过拟合检测三层**(D-SIMULATION-18/38/56):
  1. SIM-18 研究时手动检测:因子/策略回测后人工审查
  2. SIM-38 样本内外对比:样本内vs样本外收益差异+交叉验证+多重比较偏差校正
  3. SIM-56 上线前自动门禁:overfitting_flag=True→阻断上线
- 输出:BacktestResult.overfitting_flag

**data_handler.py 详细规格**(P0,来源:01-跨域交叉点/D-RESEARCH R-02/D-SIMULATION-51):
- **PIT三平面一致性**:回测用事件回放(AS OF JOIN),与训练/推理平面因子值一致
- **Feature Store PIT接口**:通过DatabaseService→FeatureStore获取PIT数据(R-02)
- **数据质量检查(P1-13)**:缺失值检测+异常值检测(来源:D-SIMULATION-51)
- **bar推送**:按timestamp逐根K线推送,禁止未来数据泄漏
- **Look-Ahead Bias Detector(P1-27)**:幸存者偏差检测+重述数据检测,CI/CD自动扫描(来源:14-D-ALT-DATA/安全架构)
- **FeatureStore PIT AS OF JOIN + PITManager(P1-30)**:强制AS OF时间点查询+PITManager管理版本对齐(来源:15-D-DATA-ENG/02-D-DATA)

**matching_engine.py 详细规格**(P1,来源:D-SIMULATION-34/41/42/08-D-EX-CORE/09-D-EX-SOR):
- **撮合引擎详细设计(P1-9)**:真实市场模拟+撮合规则(市价/限价/条件单)+市场微观结构(订单簿/集合竞价)(来源:D-SIMULATION-34)
- **滑点模型(P1-10)**:实盘环境模拟(下单延迟+成交确认+市场冲击)+流动性模型+交易成本(来源:D-SIMULATION-41/42)
- **3级滑点模型(P1-22)**:Level 1固定滑点→Level 2平方根冲击模型→Level 3订单簿模拟,按精度需求选择(来源:08-D-EX-CORE/09-D-EX-SOR)
- **Almgren-Chriss市场冲击模型(P1-23)**:线性冲击+永久冲击+时间衰减,大单拆分优化(来源:09-D-EX-SOR/R-118)

**walk_forward.py 详细规格**(P1,来源:D-SIMULATION-19/25/学习系统架构§8.1):
- **Walk-Forward分析器(P1-11)**:滚动窗口+样本外验证+参数稳定性+WF审计(来源:D-SIMULATION-19/25)
- **R-93 Walk-Forward三模式(P1-29)**:滚动(固定窗口滑动)/锚定(扩展训练集)/扩展(逐步增长),按策略类型选择(来源:学习系统架构)
- **Adaptive Walk-Forward(P1-20)**:自适应窗口步进,根据波动率动态调整窗口大小(来源:学习系统架构§8.1)
- **CPCV v2(P1-18)**:Combinatorial Purged Cross-Validation,组合净化交叉验证,消除PIT泄漏(来源:学习系统架构§8.1)
- **White's Reality Check增强(P1-19)**:功效提升+30%,多重比较偏差校正(来源:学习系统架构§8.1)

**event_driven_engine.py 详细规格**(P1,来源:学习系统架构):
- **R-117/R-118/R-119模拟器(P1-24)**:R-117沙盒模拟器(隔离测试)/R-118滑点模拟器(实盘级精度)/R-119撮合模拟器(订单簿重放),Phase 2事件驱动引擎集成(来源:学习系统架构)

### §16.8 施工参考卡

```bash
# 验证回测引擎导入
py -3.12 -c "from zephyr.backtest import BacktestEngineBase, DefaultBacktestEngine; print('OK')"

# 验证契约注册
py -3.12 -c "import yaml; d=yaml.safe_load(open('architecture_model/contracts/cross_layer_contracts.yaml','r',encoding='utf-8')); print(any(c['id']=='CTR-P1-016' for c in d['contracts']))"

# 验证事件注册
py -3.12 -c "import yaml; d=yaml.safe_load(open('architecture_model/events/domain_events.yaml','r',encoding='utf-8')); print(any(e['id']=='E-BT-01' for e in d['events']))"
```

### §16.10 故障与操作

| 故障 | 操作 |
|------|------|
| import失败 | 检查src/zephyr/backtest/__init__.py导出 |
| ClickHouse连接失败 | 检查DatabaseService配置和read_only=True |
| 回测结果异常 | 检查PIT对齐和T+1锁定 |

### §16.12 并发操作

回测为离线工具,无并发约束。多个回测可并行运行(各自独立DatabaseService连接)。

## §17 容量升级

D_BACKTEST域当前7个模块(MVP),v1.1.0扩展到15个。容量阈值≤150,无需拆分。

## §18 决策记录

| 决策 | 日期 | 依据 |
|------|------|------|
| 回测统一归口D_BACKTEST | 2026-07-02 | 消除5处碎片化,激活空壳域 |
| 回测与仿真正交分离 | 2026-07-02 | 过去怎样vs如果怎样,方法论正交 |
| 双模式架构 | 2026-07-02 | 向量化快速筛选+事件驱动精确验证 |
| 解除ARB-11 T2-deferred | 2026-07-02 | 回测是因子库前置依赖,不可延迟 |
| CTR-P1-016注册 | 2026-07-02 | CTR-P1-014被ExperimentResult占用,新建编号 |
| E-BT-*事件系列 | 2026-07-02 | E-RS-02 payload_contract=null,需专用事件 |
| SIM-46/56→SIM-18合并(P1-16) | 2026-07-02 | 去重避免重复造轮子,统一归口SIM-18(来源:D-SIMULATION §0.1) |

## 术语表

| 术语 | 定义 |
|------|------|
| 回测(backtest) | 用历史数据验证策略/因子是否赚钱 |
| 仿真(simulation) | 用假设场景推演策略表现(蒙特卡洛等) |
| 向量化回测 | pandas/numpy矩阵运算,快速但简化 |
| 事件驱动回测 | EventLoop逐bar推进,精确但慢 |
| PIT | Point-in-Time,时间点正确性,禁止未来函数 |
| IC | Information Coefficient,信息系数 |
| IR | Information Ratio,信息比率 |
| Walk-Forward | 滚动窗口验证,防止过拟合 |

## 已知问题

| 问题 | 严重度 | 计划 |
|------|:------:|------|
| DefaultBacktestEngine买入数量硬编码100股 | 中 | v1.0.1改为按目标权重计算 |
| BacktestConfig未含risk_free_rate | 中 | v1.0.1 |
| 手续费/滑点未实际扣除 | 中 | v1.0.1 |
| 事件驱动引擎未实现 | 高 | Phase 2 |
| 过拟合检测未实现 | 高 | Phase 3 |

## 自检与闭合清单

- [x] 代码已统一到src/zephyr/backtest/
- [x] 5处碎片化代码已清理
- [x] CTR-P1-016契约已注册
- [x] E-BT-01/02/03事件已注册
- [x] CTR-001/002 target_domains含D_BACKTEST
- [x] freeze_manifest路径已更新
- [x] blueprint_registry.yaml注册MOD-BT-001
- [x] depgraph D_BACKTEST域激活
- [ ] MVP剩余5个模块实现

## 成熟度

| 维度 | 等级 | 说明 |
|------|------|------|
| 代码实现 | partially_implemented | 2/7模块已完成 |
| 契约注册 | complete | CTR-P1-016已注册 |
| 事件注册 | complete | E-BT-01/02/03已注册 |
| 测试覆盖 | planned | 单元测试待编写 |
| 文档完整性 | complete | 本蓝图v1.0.0 |

## 版本演进路线图

| 版本 | 目标 | 模块数 |
|------|------|:------:|
| v1.0.0 | MVP基线(engine_base+vectorized) | 2/7 |
| v1.0.1 | 修复已知问题(硬编码/手续费/滑点) | 2/7 |
| v1.1.0 | MVP完整(7模块)+事件驱动引擎 | 7/7 |
| v1.2.0 | 过拟合检测+Walk-Forward | 9/15 |
| v2.0.0 | 完整回测平台(含报告/缓存/可视化) | 15/15 |

<!-- pre_1: Vibe Coding -->
## Vibe Coding

允许AI在MVP范围内自主实现待实现模块(matching_engine/portfolio/data_handler/metrics/event_driven_engine),但MUST:
- 遵循BacktestEngineBase OCP扩展点
- 通过单元测试
- 不破坏已冻结的engine_base.py接口

<!-- pre_2: 安全删除 -->
## 安全删除

以下文件已于2026-07-02安全删除(迁移到backtest/):
- src/zephyr/research/backtest_base.py
- src/zephyr/research/default_backtest_engine.py
- src/zephyr/intelligence/model_evaluation/backtest_base.py
- src/zephyr/intelligence/model_evaluation/implementations/default_backtest_engine.py
- src/zephyr/infrastructure/rollback/backtest_engine.py

<!-- pre_3: 必备链接 -->
## 必备链接

- [CTR-P1-016 BacktestResult契约](file:///d:/ZephyrAlpha/architecture_model/contracts/cross_layer_contracts.yaml)
- [E-BT-01/02/03事件](file:///d:/ZephyrAlpha/architecture_model/events/domain_events.yaml)
- [freeze_manifest.yaml](file:///d:/ZephyrAlpha/src/zephyr/shared/contracts/freeze_manifest.yaml)
- [engine_base.py](file:///d:/ZephyrAlpha/src/zephyr/backtest/core/engine_base.py)
- [vectorized_engine.py](file:///d:/ZephyrAlpha/src/zephyr/backtest/implementations/vectorized_engine.py)

<!-- pre_4: 已有类似功能 -->
## 已有类似功能

- D_SIMULATION域(MOD-L13-001):仿真/场景生成,与回测正交,可复用D_BACKTEST的撮合引擎
- D_INTELLIGENCE域的ExperimentPipeline:实验管线,与回测是不同概念

<!-- pre_5: 涉及的文件范围 -->
## 涉及的文件范围

| 文件 | 操作 | 说明 |
|------|------|------|
| src/zephyr/backtest/core/engine_base.py | 已完成 | 迁移自research/backtest_base.py |
| src/zephyr/backtest/implementations/vectorized_engine.py | 已完成 | 迁移自research/default_backtest_engine.py |
| src/zephyr/backtest/core/matching_engine.py | 待创建 | MVP Phase 1 |
| src/zephyr/backtest/core/portfolio.py | 待创建 | MVP Phase 1 |
| src/zephyr/backtest/core/data_handler.py | 待创建 | MVP Phase 1 |
| src/zephyr/backtest/core/metrics.py | 待创建 | MVP Phase 1 |
| src/zephyr/backtest/implementations/event_driven_engine.py | 待创建 | MVP Phase 2 |
| architecture_model/contracts/cross_layer_contracts.yaml | 已修改 | 新增CTR-P1-016 |
| architecture_model/events/domain_events.yaml | 已修改 | 新增E-BT-01/02/03 |
