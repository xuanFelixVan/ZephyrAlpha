---
ttl: task_bound
---

# 三系统升级施工总方案 + 暂缓功能清单（数据库 / 因子 / 回测）

> **范围**：基于全景图设计态 vs 运营态对比，识别关键缺口，实施非过度升级。
> **原则**：最小可用实现 + 复用现有模式 + 代码复杂度 < 15 + 纯函数优先 + 配置不硬编码。
> **状态**：T1-T7 施工任务全部完成，本文件保留为暂缓功能登记册。

## §1 设计态 vs 运营态差异总结

### 1.1 因子域 (D-FACTOR)

| 模块 | 设计态要求 | 运营态现状 | 缺口 |
|------|-----------|-----------|------|
| D-FACTOR-01 Engine | incremental_compute() 滑动窗口 | FactorBase.compute() 全量计算 | ✅ T2已完成 |
| D-FACTOR-04 Pipeline | 双模运行(盘前全量+盘中增量) | dag_manager/executor 单模 | ✅ T6已完成 |
| D-FACTOR-08 Pool | 因子池容量管理 N_max≈64 | 无因子池管理 | ✅ T1已完成 |
| D-FACTOR-GOV | 治理引擎 | ✅ 六步流程+灰度+ABS001 | ✅ 已完成 |

### 1.2 回测域 (D_BACKTEST)

| 模块 | 设计态要求 | 运营态现状 | 缺口 |
|------|-----------|-----------|------|
| BT-01~16 核心引擎 | 16模块 | ✅ 16/16 production | ✅ 已完成 |
| BT-17 scheduler | 自动回测调度器 | services/ 仅空 __init__.py | ✅ T3已完成 |
| BT-18~26 辅助 | 衰减/报告/缓存等 | 未启动 | ⏸ 见§7.1 |

### 1.3 数据治理域 (D-DATA-GOVERNANCE / D-DATA-ENG)

| 模块 | 设计态要求 | 运营态现状 | 缺口 |
|------|-----------|-----------|------|
| schema_registry | Schema注册管理 | 纯脚手架(仅__init__) | ✅ T5已完成 |
| lineage_tracker | 血缘追踪 | 纯脚手架 | ✅ T5已完成 |
| metadata_registry | 元数据管理 | 纯脚手架 | ✅ T5已完成 |

## §2 施工任务总表

| 任务 | 优先级 | 模块 | 产出文件 | 状态 |
|------|:------:|------|---------|:----:|
| T1 因子池容量管理 | P0 | D-FACTOR-08 | governance/factor_pool_manager.py + 测试 | ✅ |
| T2 incremental_compute() | P0 | D-FACTOR-01 | factor_base.py扩展 + 具体因子 + 测试 | ✅ |
| T3 回测自动调度器 | P0 | D-BACKTEST BT-17 | backtest/services/scheduler.py + 测试 | ✅ |
| T4 依赖图文档补登 | ✅ | D-BACKTEST | 32-D-BACKTEST.md | ✅ |
| T5 data_governance最小实现 | P1 | D-DATA-GOV | schema_registry + lineage_tracker + metadata_registry | ✅ |
| T6 因子04 Pipeline双模 | P1 | D-FACTOR-04 | dag_manager/executor 双模切换 + 测试 | ✅ |
| T7 回测↔因子IC e2e | ✅ | 跨域 | tests/factor/test_backtest_factor_e2e.py | ✅ |

## §3 任务详细设计

### T1: 因子池容量管理

**文件**: `src/zephyr/factor/governance/factor_pool_manager.py`
**核心逻辑**:
- 活跃池(active): 容量 N_max-4 ≈ 60，参与实盘信号生成
- 休眠池(dormant): 容量 ≤ 4，IC衰退但待恢复
- 核心因子(core): 标记 `is_core=True`，不参与末位淘汰
- IC-Based末位淘汰: 活跃池满时，新因子对比池内IC最低者
- 批量裁剪: 全池≥N_max时，按IC从休眠池裁撤

**验收标准**: 活跃池不超容 / 核心因子不被淘汰 / IC末位淘汰正确替换 / 批量裁剪按IC排序

### T2: incremental_compute() 滑动窗口

**文件**: `src/zephyr/factor/factor_base.py` (扩展) + `src/zephyr/factor/momentum_factor.py` (覆盖)
**核心逻辑**:
- FactorBase 新增 `incremental_compute()` 方法，默认回退 `compute()`（向后兼容）
- 滑动窗口: 只重算窗口内新数据，拼接已有缓存结果

**验收标准**: 默认回退正确 / momentum增量与全量结果一致 / 窗口边界正确

### T3: 回测自动调度器

**文件**: `src/zephyr/backtest/services/scheduler.py`
**核心逻辑**:
- 参数网格: 展开参数组合为任务列表
- 队列管理: FIFO队列 + 最大并发数控制
- 结果聚合: 收集所有回测结果，按 strategy_id 分组汇总

**验收标准**: 参数网格正确展开 / 队列FIFO / 结果聚合正确 / 并发不丢任务

### T5: data_governance 最小实现

**文件**: `src/zephyr/data_governance/core/{schema_registry,lineage_tracker,metadata_registry}.py`
**核心逻辑**:
- schema_registry: 复用 `data/table_registry.py` 模式
- lineage_tracker: 记录因子→信号→策略→决策→执行 血缘链
- metadata_registry: 统一元数据存储

**验收标准**: Schema注册/查询 / 血缘链追加查询 / 元数据CRUD

### T6: 因子04 Pipeline双模运行

**文件**: `src/zephyr/factor/core/dag_manager/executor.py` (扩展)
**核心逻辑**:
- 双模切换: `mode="batch"`(盘前全量) / `mode="incremental"`(盘中增量)
- 时间窗口: 03:00-09:15 → batch, 09:30-15:00 → incremental
- 增量模式调用 `incremental_compute()`

**验收标准**: 模式切换正确 / 时间窗口判断 / 增量调用incremental_compute

### T7: 回测↔因子IC评估端到端集成验证

**文件**: `tests/factor/test_backtest_factor_e2e.py`
**核心逻辑**: 构造合成数据 → 因子计算 → IC评估 → 回测调度 → 结果验证
**验收标准**: 端到端数据流通畅 / IC评估结果正确传递 / 回测结果包含因子信息

## §4 依赖关系

```
T1(因子池) ──────────────┐
T2(incremental) ─────────┤
                          ├──→ T6(双模Pipeline) ──→ T7(e2e验证)
T3(回测调度器) ──────────┤
T5(data_governance) ─────┘
```

## §5 风险评估

| 风险 | 缓解措施 |
|------|---------|
| 因子池管理复杂度膨胀 | 严格控制在<15，用辅助函数拆分 |
| incremental_compute 向后兼容 | 默认回退 compute()，不破坏现有因子 |
| 回测调度器并发安全 | 使用 ThreadPoolExecutor + 锁 |
| data_governance 过度设计 | 只做最小实现，复用已有 data/ 组件 |

## §6 三个值得记录的观察

> 以下三项在全面检查中发现，经评估**无需新增施工任务**，仅作记录备案。

### 观察1：BT-18 vs factor/analysis/decay_monitor.py 职责区分

| 维度 | BT-18 策略衰减监控 | factor/analysis/decay_monitor.py 因子IC衰减监控 |
|------|-------------------|------------------------------------------------|
| 设计位置 | D_BACKTEST services/ | D_FACTOR analysis/ |
| 监控对象 | 策略PnL衰减（实盘vs回测收益偏离） | 因子IC衰减（因子预测能力随时间下降） |
| 触发条件 | 实盘收益持续低于回测预期 | IC时序CUSUM突破2σ/4σ阈值 |
| 当前状态 | 未实现（设计文档BT-18） | ✅ 已实现（67行，production） |
| 结论 | 因子侧IC衰减监控已覆盖，策略级衰减监控可后续按需添加，当前不紧急 |

### 观察2：D-FACTOR-02 Registry 功能够用

| 维度 | 设计态要求 | 运营态现状 |
|------|-----------|-----------|
| 元数据Schema | 因子元数据Schema完整 | FactorMeta dataclass 含 factor_id/name/domain/dependencies/version |
| 版本树 | 因子版本树+废弃流程 | governance/lifecycle_state_machine.py 管生命周期6态 |
| 依赖图 | 因子依赖图 | FactorMeta.dependencies 字段 + factor_dag/dag.py 构建DAG |
| 四维索引 | 名称/类别/状态/SLA索引 | FactorRegistry dict基础查询（按factor_id） |
| 结论 | 当前FactorRegistry是dict基础实现，功能上够用。版本树/四维索引增强属过度升级，待因子数>50时再评估 |

### 观察3：D-DATA-ENG域 实际部分覆盖

| 设计态模块 | 运营态实际覆盖 | 状态 |
|-----------|--------------|:----:|
| D-DATA-ENG-01 ETLPipeline | data/scheduler.py（1500行，ETL+增量+断点续传） | ✅ 已覆盖 |
| D-DATA-ENG-02 PipelineOrchestrator | data/scheduler.py（DAG调度+依赖管理+分时段） | ✅ 已覆盖 |
| D-DATA-ENG-03 FeatureStore | 未独立实现（因子值直接存ClickHouse） | ⏸ 唯一真正缺失 |
| D-DATA-ENG-04 DataQualityMonitor | data/cross_source_validator.py + integrity_checker.py | ✅ 已覆盖 |
| D-DATA-ENG-05 DataLineageTracker | T5: data_governance/core/lineage_tracker.py | ✅ T5已覆盖 |
| D-DATA-ENG-06 StreamProcessingEngine | 未实现 | ⛔ 需Kafka/Flink |
| 结论 | D-DATA-ENG标注"未启动"但实际D-DATA代码已覆盖5/6核心模块。FeatureStore是唯一缺失项，但它是独立大模块，当前因子值直接存ClickHouse可行，暂不急需 |

## §7 暂缓功能清单（全量登记）

> 以下功能经全面检查后确认**当前不宜施工**，按原因分为三类：
> - ⛔ **受限**：需外部依赖（GPU/付费数据/Level-2数据/Kafka-Flink等）或门禁未解除
> - ⏸ **P2暂缓**：优先级低，当前实施属过度升级
> - ⚠️ **部分覆盖**：已有代码部分覆盖，完整版暂不急需
>
> **depgraph 对应字段**（写入全景图设计态时使用）：
> - `build_status` = `'planned'`（暂缓/未建）
> - `can_build` = `0`（受限不可建）或 `1`（P2可建但不急）
> - `gate_reason` = 暂缓原因文本
> - `design_maturity` = `'design'`（设计态）
> - `nodes_metadata.module_name_cn` / `description_cn` = 中文名称/功能简介

### §7.1 回测域暂缓模块（D_BACKTEST BT-18~26）

| ID | 中文名称 | 功能简介 | 用处 | 暂缓原因 | can_build | gate_reason |
|----|---------|---------|------|:--------:|:---------:|:-----------:|
| BT-18 | 策略衰减监控告警器 | 监控策略实盘收益vs回测收益的偏离趋势，当实盘收益持续低于回测预期时发出衰减告警 | 防止策略上线后性能退化未被及时发现 | ⚠️ 因子侧已有decay_monitor覆盖IC衰减 | 1 | 暂缓：因子侧decay_monitor已覆盖IC衰减监控 |
| BT-19 | 回测报告自动生成器 | 自动生成回测报告（PDF/HTML格式），含净值曲线、回撤分析、交易明细、绩效归因等 | 便于向非技术人员展示回测结果，替代手动截图 | ⏸ P2暂缓 | 1 | 暂缓：P2优先级，当前无报告展示需求 |
| BT-20 | 回测缓存管理器 | 缓存回测中间结果与最终结果，相同参数组合直接复用，避免重复计算 | 大规模参数网格搜索时减少70%+重复计算 | ⏸ P2暂缓 | 1 | 暂缓：P2优先级，当前回测量不大 |
| BT-21 | 参数优化结果分析器 | 分析参数网格搜索结果的参数显著性（t统计量）与过拟合风险（参数敏感性） | 判断最优参数是真实有效还是过拟合偶然结果 | ⚠️ scheduler已有get_summary | 1 | 暂缓：scheduler已含best/worst/mean摘要 |
| BT-22 | 回测数据质量检查器 | 回测前检查输入数据质量：缺失日期检测、异常值检测、数据连续性验证 | 防止垃圾数据导致回测结果失真 | ⚠️ data域已有quality_gate | 1 | 暂缓：data域已有quality_gate+integrity_checker |
| BT-23 | 回测异常诊断器 | 回测失败时自动诊断错误原因并给出修复建议（数据缺失/参数越界/引擎异常等） | 减少回测失败时的排查时间 | ⏸ P2暂缓 | 1 | 暂缓：P2优先级，当前回测失败率低 |
| BT-24 | 回测结果对比器 | 对比多次回测结果的差异（参数变化/数据更新/策略迭代带来的收益变化） | 量化策略改动的实际效果，支持A/B对比 | ⏸ P2暂缓 | 1 | 暂缓：P2优先级，当前无多次对比需求 |
| BT-25 | 回测结果一键部署器 | 将通过验证的回测策略一键部署到实盘环境（参数迁移+风控配置+监控初始化） | 缩短从回测验证到实盘上线的路径 | ⚠️ 需D-EX-CORE就绪 | 0 | 暂缓：涉及实盘安全，需D-EX-CORE执行域就绪 |
| BT-26 | 指标计算NaN处理器 | 智能处理指标计算中的NaN值（前向填充/插值/剔除），避免NaN传播导致绩效指标失真 | 保证Sharpe/MaxDD等指标在数据有缺失时仍可计算 | ⏸ P2暂缓 | 1 | 暂缓：P2优先级，当前数据缺失率低 |

### §7.2 因子域受限主模块（D-FACTOR）

| ID | 中文名称 | 功能简介 | 用处 | 受限原因 | can_build | gate_reason |
|----|---------|---------|------|---------|:---------:|:-----------:|
| D-FACTOR-05 | 因子挖掘智能体 | 并发AI因子挖掘（多Agent并行生成因子假设→投票选最优）+相关性去重(>0.85丢弃)+自动验证闭环+自动入库。支持表达式组合/遗传编程/LLM辅助(qwen3:8b)三种发现方法 | 自动发现新Alpha因子，替代人工因子研发 | ⛔ 需GPU+多Agent框架 | 0 | 受限：需GPU硬件+多Agent框架(GATE-05-01~03) |
| D-FACTOR-06 | Barra风险模型 | Barra风格因子(10大：规模/价值/动量/波动/流动性等)+行业因子(28申万一级行业)+正交化处理+因子中性化(行业/市值/风格中性) | 提供标准化风险因子框架，支撑因子暴露分析与风险归因 | ⛔ 需付费Barra数据 | 0 | 受限：需付费Barra数据(GATE-06-01~03) |
| D-FACTOR-07 | 因子治理引擎(完整版) | 因子准入门禁+运行时监控+废弃审批+39类漂移检测器(均值漂移/方差漂移/IC漂移/分布漂移等)+因子-模型联合优化 | 全生命周期因子质量保障，防止劣质因子污染信号 | ⛔ 需39类漂移检测器 | 0 | 受限：完整版需39类漂移检测器(GATE-07-01~03)，基础版engine.py已实现 |
| D-FACTOR-09 | 因子相关性分析器(完整版) | 滚动相关矩阵+条件相关性+聚类分析+共线性检测(VIF)+LLM语义去重(判断经济学逻辑等价性) | 防止因子池冗余，识别数值不同但逻辑等价的因子 | ⛔ 需LLM语义判断 | 0 | 受限：完整版需LLM语义判断(GATE-09-01~02)，基础版correlation_analyzer.py已实现 |
| D-FACTOR-10 | 因子换手率分析器 | 换手率计算+成本衰减模型+自相关系数+买卖价差估算 | 评估因子的交易成本影响，高换手率因子可能被成本吃掉Alpha | ⛔ P2 | 0 | 受限：P2优先级(GATE-10-01~02) |
| D-FACTOR-11 | 因子暴露计算器 | 实时因子暴露(L1<1秒/Tick)+截面因子暴露+行业偏离+风格暴露约束 | 实时监控组合在各因子上的风险敞口 | ⛔ 需D-FACTOR-06就绪 | 0 | 受限：需D-FACTOR-06 Barra风险模型就绪(GATE-11-01) |
| D-FACTOR-24 | 因子风险预算分配器 | 按因子IC/IR分配风险预算+因子暴露约束+风险限额检查 | 优化因子权重分配，高IC因子获得更多风险预算 | ⛔ 需06+11+D-RISK就绪 | 0 | 受限：需06+11就绪+D-RISK域就绪(GATE-24-01~02) |

### §7.3 因子域受限子模块（FAC-ASHARE A股因子）

| ID | 中文名称 | 功能简介 | 用处 | 受限原因 | can_build | gate_reason |
|----|---------|---------|------|---------|:---------:|:-----------:|
| FAC-27 | 微观结构因子 | 基于Level-2逐笔成交数据计算微观结构因子（买卖压力不平衡/成交单大小分布/大单净买入比例等） | 捕捉盘中微观交易行为信号 | ⛔ 需Level-2数据 | 0 | 受限：需Level-2逐笔成交数据(GATE-27-01) |
| FAC-29 | 日内因子 | 基于3秒Tick数据计算日内因子（开盘冲击/尾盘异常/盘中动量等） | 捕捉日内交易模式，区别于日频因子 | ⛔ 需3秒Tick管线 | 0 | 受限：需3秒Tick管线稳定运行(GATE-29-01) |
| FAC-55 | SMC因子 | Smart Money Concepts智能资金概念因子（订单块/公平价值缺口/流动性池等） | 识别机构资金的关键价位行为 | ⛔ GATE-55 | 0 | 受限：GATE-55-01~02未解除 |
| FAC-56 | IRL因子 | 逆强化学习因子（从市场行为反推机构隐含策略） | 推断机构交易意图 | ⛔ GATE-56 | 0 | 受限：GATE-56-01未解除 |
| FAC-92 | 87-Alpha因子 | WorldQuant 87因子全集实现（从经典Alpha#1~#177中筛选87个有效因子） | 覆盖学术界验证的经典Alpha因子库 | ⛔ GATE-92 | 0 | 受限：GATE-92-01未解除 |
| FAC-97 | 形态转信号 | K线形态识别（头肩顶/双底/三角形等）转化为量化信号 | 将传统技术分析形态量化为可回测信号 | ⛔ GATE-97 | 0 | 受限：GATE-97-01未解除 |
| FAC-100 | 机构行为因子 | 基于龙虎榜+北向资金+大宗交易数据计算机构行为因子（筹码集中度/机构净流入/龙虎榜机构占比/北向持仓变化） | 跟踪机构资金动向 | ⛔ 需iFind数据 | 0 | 受限：需iFind龙虎榜+北向+大宗数据(GATE-100-01) |
| FAC-102 | 跨市场因子 | 跨市场传导因子（VIX恐慌指数/美债利差/汇率波动/A50期货溢价等对A股的传导效应） | 捕捉全球市场对A股的溢出效应 | ⛔ 需iFind全球数据 | 0 | 受限：需iFind全球市场数据(GATE-102-01) |
| FAC-106 | 流动性因子 | Pastor-Stambaugh系统性流动性风险因子（市场流动性溢价的度量） | 衡量系统性流动性风险 | ⛔ 需iFind+统计库 | 0 | 受限：需iFind全球市场数据+统计回归库(GATE-106-01) |

### §7.4 数据域/数据工程域暂缓模块

| ID | 中文名称 | 功能简介 | 用处 | 暂缓原因 | can_build | gate_reason |
|----|---------|---------|------|---------|:---------:|:-----------:|
| D-DATA-04 | 实时行情推送管理器 | 管理实时行情数据流（WebSocket/TCP推送），支持多订阅者+断线重连+数据校验 | 盘中实时行情接入，支撑盘中增量计算 | ⛔ 需Kafka/Flink | 0 | 受限：需Kafka/Flink流处理基础设施 |
| D-DATA-20 | Tick数据管理器 | 管理Level-2 Tick数据（采集/存储/清洗/重放），支持秒级和逐笔数据 | 支撑Tick级回测与微观结构因子 | ⛔ 需Level-2授权 | 0 | 受限：需Level-2数据源授权 |
| D-DATA-ENG-03 | 特征存储 | PIT查询(DuckDB AS OF JOIN)+特征版本管理+特征服务API+在线/离线存储分离 | 统一特征管理，保证训练/推理特征一致性 | ⏸ 独立大模块 | 1 | 暂缓：独立大模块，当前因子值直接存ClickHouse可行 |
| D-DATA-ENG-06 | 流处理引擎 | 实时计算+窗口聚合+事件时间对齐+水位线+背压控制 | 盘中实时因子计算与信号生成 | ⛔ 需Kafka/Flink | 0 | 受限：需Kafka/Flink基础设施 |
| D-DATA-ENG-07 | 漂移感知调度器 | ADWIN/DDM漂移检测+共形漂移检测+多尺度漂移检测+双层优化(任务模型+规划器) | 自动检测数据分布变化并触发重训练 | ⏸ P1需D-AUTONOMY | 1 | 暂缓：P1优先级，需D-AUTONOMY就绪 |
| D-DATA-ENG-08 | PIT管理器 | DuckDB AS OF JOIN时间旅行查询+任意历史时点特征快照重建+PIT门控联动 | 保证回测时只使用当时可获得的数据(PIT铁律) | ⚠️ pit_query.py已有 | 1 | 暂缓：data/pit_query.py已有基础PIT查询 |
| D-DATA-ENG-09 | 训练数据管理器 | 训练数据版本管理+质量检查+数据增强+分层采样 | 保证ML模型训练数据的可追溯与可复现 | ⏸ P1需D-ML-TRAIN | 1 | 暂缓：P1优先级，需D-ML-TRAIN就绪 |
| D-DATA-ENG-10 | 知识清洗流水线 | 格式转换+去重+去噪+术语标准化+说话人分离+信息价值评分 | 将非结构化文本(新闻/研报)转化为可量化知识 | ⏸ P1需D-KNOWLEDGE | 1 | 暂缓：P1优先级，需D-KNOWLEDGE就绪 |
| D-DATA-ENG-11 | GPU资源管理器 | PyTorch CUDA内存分区+时段优先调度+显存预算管理+OOM防护 | 管理GPU资源分配，防止训练OOM | ⏸ P1需GPU | 1 | 暂缓：P1优先级，需GPU硬件 |
| D-DATA-ENG-12 | 数据湖管理器 | 分层存储(热/温/冷)+生命周期管理+自动分层迁移 | 降低存储成本，冷数据自动归档 | ⏸ P2 | 1 | 暂缓：P2优先级 |
| D-DATA-ENG-13 | 数据压缩归档 | 冷热分离+自动归档(Parquet/ZSTD压缩) | 减少历史数据存储占用 | ⏸ P2 | 1 | 暂缓：P2优先级 |
| D-DATA-ENG-14 | Schema演进管理器 | Schema演进+兼容性检查(前向/后向)+自动迁移 | 管理表结构变更，防止Breaking Change | ⏸ P2 | 1 | 暂缓：P2优先级 |
| D-DATA-ENG-15 | 数据复制同步 | 跨源同步+一致性保证(CDC/Debezium) | 多数据源实时同步 | ⏸ P2 | 1 | 暂缓：P2优先级 |
| D-DATA-ENG-16 | 数据画像 | 统计分布+异常检测+数据质量评分 | 自动发现数据质量问题 | ⏸ P2 | 1 | 暂缓：P2优先级 |
| D-DATA-ENG-17 | 数据目录同步 | 元数据自动采集+搜索(DataHub集成) | 企业级数据资产目录 | ⏸ P2 | 1 | 暂缓：P2优先级 |
| D-DATA-ENG-18 | 合成数据生成器 | SMOTE过采样+轻量GAN生成合成行情数据(仅训练增强) | 解决训练数据不足问题 | ⏸ P2 | 1 | 暂缓：P2优先级 |
| D-DATA-ENG-19 | 数据可观测性平台 | 健康度监控+根因分析+SLA追踪 | 全链路数据质量监控 | ⏸ P2 | 1 | 暂缓：P2优先级 |
| D-DATA-ENG-20 | 数据产品管理器 | 产品定义+目录+版本+评估+退役 | 管理数据产品生命周期 | ⏸ P2 | 1 | 暂缓：P2优先级 |

### §7.5 暂缓功能统计

| 类别 | 数量 | can_build=0 | can_build=1 | 说明 |
|------|:----:|:-----------:|:-----------:|------|
| ⛔ 受限（需外部依赖） | 18项 | 18 | 0 | 需GPU/付费数据/Level-2/Kafka-Flink等，当前无法施工 |
| ⏸ P2暂缓（过度升级） | 16项 | 0 | 16 | 优先级低，当前实施属过度升级 |
| ⚠️ 部分覆盖（基础版已有） | 6项 | 1 | 5 | 已有基础实现，完整版暂不急需 |
| **合计** | **40项** | **19** | **21** | 均为当前不宜施工，待外部条件具备后按需启动 |

### §7.6 解锁路径（按优先级排序）

| 解锁条件 | 可解锁模块 | 预计时机 |
|---------|-----------|---------|
| 获取iFind付费数据 | D-FACTOR-06 Barra → D-FACTOR-11 暴露 → D-FACTOR-24 风险预算 + FAC-100/102/106 | 数据采购后 |
| 获取Level-2数据 | FAC-27 微观结构 + D-DATA-20 Tick管理 + FAC-29 日内 | 数据采购后 |
| 部署Kafka/Flink | D-DATA-04 实时推送 + D-DATA-ENG-06 流处理 | 实盘立项后 |
| 获取GPU | D-FACTOR-05 因子挖掘 + D-DATA-ENG-11 GPU管理 | 硬件采购后 |
| 因子数>50 | D-FACTOR-02 Registry增强(版本树/四维索引) | 因子池扩张后 |
| D-AUTONOMY就绪 | D-DATA-ENG-07 漂移调度 + D-DATA-ENG-09 训练数据 | 自治系统就绪后 |
| 实盘立项 | BT-25 结果部署 + D-DATA-ENG-03 FeatureStore | 实盘阶段 |

### §7.7 写入全景图设计态的字段映射

> 将暂缓模块写入 depgraph 设计态时，按以下字段映射设置：

| depgraph 字段 | 值 | 说明 |
|--------------|---|------|
| `design_maturity` | `'design'` | 设计态（非 production） |
| `build_status` | `'planned'` | 暂缓/未建 |
| `can_build` | `0`（受限）或 `1`（P2暂缓） | 受限模块=0，P2暂缓=1 |
| `gate_reason` | 暂缓原因文本 | 如"受限：需GPU硬件(GATE-05-01~03)" |
| `nodes_metadata.module_name_cn` | 中文名称 | 如"因子挖掘智能体" |
| `nodes_metadata.description_cn` | 功能简介 | 如"并发AI因子挖掘+去重+自动验证闭环" |

## §8 三图对齐设计与执行结果（2026-07-29）

> **目标**：将42项暂缓模块写入 depgraph 设计态，并通过 `sync_panorama_module.py` 派生到 dataflowgraph / decisiongraph，实现3图对齐。
> **执行脚本**：`scripts/governance/register_deferred_modules.py`
> **铁律依据**：TRAE-080 四图对齐铁律——入口是 depgraph 设计态，sync 自动派生其余3图，align 验证对齐。

### §8.1 三图对齐机制

```
depgraph (PostgreSQL)          dataflowgraph              decisiongraph
┌─────────────────┐     sync_panorama_module.py    ┌──────────────────┐
│ nodes 表        │    ─────────────────────────→  │ dataflow_jobs    │
│  build_status   │    自动派生 module_placeholder  │  entity_type=    │
│  can_build      │    ─────────────────────────→  │   'module_       │
│  gate_reason    │                                │   placeholder'   │
│  design_maturity│                                └──────────────────┘
└─────────────────┘                                ┌──────────────────┐
                                                    │ decision_layers  │
                                                    │  track=          │
                                                    │   'placeholder'  │
                                                    └──────────────────┘
```

- **depgraph**（依赖图）：节点(path/blueprint_id/domain/build_status/can_build/gate_reason) + 边(依赖关系)
- **dataflowgraph**（数据流图）：sync 自动派生 `dataflow_jobs` 占位记录，按 blueprint_id 聚合
- **decisiongraph**（决策图）：sync 自动派生 `decision_layers` 占位记录，track='placeholder'
- **对齐验证**：`align_panoramas.py` 检查4类问题(孤儿/状态漂移/域不一致/设计态孤立)

### §8.2 模块分类与处理方式

| 分类 | 数量 | 处理方式 | 说明 |
|------|:----:|---------|------|
| Category A: 已注册 | 17项 | 更新元数据 | 已有目录级设计态节点，补充 gate_reason/can_build/module_name_cn/description_cn |
| Category B: 新增 | 25项 | add_design_node + 更新元数据 | 完全未注册，新增节点后 sync 自动派生到3图 |
| Category C: 已覆盖 | 3项 | 跳过 | D-DATA-ENG-04/05/08 已被生产代码覆盖 |
| **合计** | **45项** | **42项写入** | 3项跳过 |

### §8.3 Category A — 已注册节点元数据更新（17项）

> 这些模块已作为目录级设计态节点存在于 depgraph（MOD-L02-001/MOD-L00-004 下，build_status=planned），但 gate_reason 为空、无中文名。

| 设计ID | depgraph path | 中文名 | can_build | gate_reason |
|--------|--------------|--------|:---------:|-------------|
| FAC-27 | factor/ashare/microstructure/ | 微观结构因子 | 0 | 受限：需Level-2逐笔成交数据(GATE-27-01) |
| FAC-29 | factor/ashare/intraday/ | 日内因子 | 0 | 受限：需3秒Tick管线稳定运行(GATE-29-01) |
| FAC-55 | factor/ashare/smc/ | SMC因子 | 0 | 受限：GATE-55-01~02未解除 |
| FAC-56 | factor/ashare/irl/ | IRL因子 | 0 | 受限：GATE-56-01未解除 |
| FAC-92 | factor/ashare/alpha87/ | 87-Alpha因子 | 0 | 受限：GATE-92-01未解除 |
| FAC-97 | factor/ashare/pattern_signal/ | 形态转信号 | 0 | 受限：GATE-97-01未解除 |
| FAC-100 | factor/ashare/institutional/ | 机构行为因子 | 0 | 受限：需iFind龙虎榜+北向+大宗数据(GATE-100-01) |
| FAC-102 | factor/ashare/cross_market/ | 跨市场因子 | 0 | 受限：需iFind全球市场数据(GATE-102-01) |
| FAC-106 | factor/ashare/ps_liquidity/ | 流动性因子 | 0 | 受限：需iFind全球市场数据+统计回归库(GATE-106-01) |
| D-FACTOR-05 | factor/mine/mining_agent/ | 因子挖掘智能体 | 0 | 受限：需GPU硬件+多Agent框架(GATE-05-01~03) |
| D-FACTOR-06 | factor/barra/risk_model/ | Barra风险模型 | 0 | 受限：需付费Barra数据(GATE-06-01~03) |
| D-FACTOR-07 | factor/governance/engine/ | 因子治理引擎(完整版) | 0 | 受限：完整版需39类漂移检测器(GATE-07-01~03) |
| D-FACTOR-09 | factor/analysis/correlation_analyzer/ | 因子相关性分析器(完整版) | 0 | 受限：完整版需LLM语义判断(GATE-09-01~02) |
| D-FACTOR-11 | factor/barra/exposure_calculator/ | 因子暴露计算器 | 0 | 受限：需D-FACTOR-06 Barra风险模型就绪(GATE-11-01) |
| D-FACTOR-24 | factor/barra/risk_budget_allocator/ | 因子风险预算分配器 | 0 | 受限：需06+11就绪+D-RISK域就绪(GATE-24-01~02) |
| D-DATA-ENG-03 | data/feature_store/ | 特征存储 | 1 | 暂缓：独立大模块，当前因子值直接存ClickHouse可行 |
| D-DATA-ENG-19 | data/data_observability/ | 数据可观测性平台 | 1 | 暂缓：P2优先级 |

### §8.4 Category B — 新增设计态节点（25项）

| 设计ID | blueprint_id | domain | path | 中文名 | can_build |
|--------|-------------|--------|------|--------|:---------:|
| BT-18 | MOD-BT-018 | D_BACKTEST | backtest/services/decay_monitor.py | 策略衰减监控告警器 | 1 |
| BT-19 | MOD-BT-019 | D_BACKTEST | backtest/services/report_generator.py | 回测报告自动生成器 | 1 |
| BT-20 | MOD-BT-020 | D_BACKTEST | backtest/services/cache_manager.py | 回测缓存管理器 | 1 |
| BT-21 | MOD-BT-021 | D_BACKTEST | backtest/services/param_analyzer.py | 参数优化结果分析器 | 1 |
| BT-22 | MOD-BT-022 | D_BACKTEST | backtest/services/data_quality_checker.py | 回测数据质量检查器 | 1 |
| BT-23 | MOD-BT-023 | D_BACKTEST | backtest/services/anomaly_diagnoser.py | 回测异常诊断器 | 1 |
| BT-24 | MOD-BT-024 | D_BACKTEST | backtest/services/result_comparator.py | 回测结果对比器 | 1 |
| BT-25 | MOD-BT-025 | D_BACKTEST | backtest/services/result_deployer.py | 回测结果一键部署器 | 0 |
| BT-26 | MOD-BT-026 | D_BACKTEST | backtest/services/nan_processor.py | 指标计算NaN处理器 | 1 |
| D-FACTOR-10 | MOD-L02-001 | D_FACTOR | factor/analysis/turnover_analyzer/ | 因子换手率分析器 | 0 |
| D-DATA-04 | MOD-L00-004 | D_DATA | data/realtime_push_manager/ | 实时行情推送管理器 | 0 |
| D-DATA-20 | MOD-L00-004 | D_DATA | data/tick_data_manager/ | Tick数据管理器 | 0 |
| D-DATA-ENG-06 | MOD-DATA_ENG | D_DATA_ENG | data_eng/services/stream_processing/ | 流处理引擎 | 0 |
| D-DATA-ENG-07 | MOD-DATA_ENG | D_DATA_ENG | data_eng/services/drift_aware_scheduler/ | 漂移感知调度器 | 1 |
| D-DATA-ENG-09 | MOD-DATA_ENG | D_DATA_ENG | data_eng/services/training_data_manager/ | 训练数据管理器 | 1 |
| D-DATA-ENG-10 | MOD-DATA_ENG | D_DATA_ENG | data_eng/services/knowledge_cleaning/ | 知识清洗流水线 | 1 |
| D-DATA-ENG-11 | MOD-DATA_ENG | D_DATA_ENG | data_eng/services/gpu_resource_manager/ | GPU资源管理器 | 1 |
| D-DATA-ENG-12 | MOD-DATA_ENG | D_DATA_ENG | data_eng/services/data_lake_manager/ | 数据湖管理器 | 1 |
| D-DATA-ENG-13 | MOD-DATA_ENG | D_DATA_ENG | data_eng/services/data_compression/ | 数据压缩归档 | 1 |
| D-DATA-ENG-14 | MOD-DATA_ENG | D_DATA_ENG | data_eng/services/schema_evolution/ | Schema演进管理器 | 1 |
| D-DATA-ENG-15 | MOD-DATA_ENG | D_DATA_ENG | data_eng/services/data_replication/ | 数据复制同步 | 1 |
| D-DATA-ENG-16 | MOD-DATA_ENG | D_DATA_ENG | data_eng/services/data_profiling/ | 数据画像 | 1 |
| D-DATA-ENG-17 | MOD-DATA_ENG | D_DATA_ENG | data_eng/services/data_catalog/ | 数据目录同步 | 1 |
| D-DATA-ENG-18 | MOD-DATA_ENG | D_DATA_ENG | data_eng/services/synthetic_data/ | 合成数据生成器 | 1 |
| D-DATA-ENG-20 | MOD-DATA_ENG | D_DATA_ENG | data_eng/services/data_product_manager/ | 数据产品管理器 | 1 |

### §8.5 三图数据流位置设计

> 每个模块在3图中的数据流位置由 depgraph 边的 `api_contract_refs` / `event_ref` 决定。
> sync_panorama_module.py 按 blueprint_id 聚合派生 dataflow_jobs / decision_layers 占位记录。

| 域 | 模块 | 数据流(消费) | 数据流(产出) | 决策位 |
|----|------|-------------|-------------|--------|
| D_FACTOR | FAC-27~106 | CTR-001 NormalizedMarketData ← D_DATA | CTR-002 FactorSignal → D_FACTOR-01 Engine | — |
| D_FACTOR | D-FACTOR-05 挖掘 | CTR-001 ← D_DATA | E-RS-01 FactorResearched → D_FACTOR-02 | L5: 因子准入 |
| D_FACTOR | D-FACTOR-06 Barra | CTR-001 + Barra数据 ← D_DATA | CTR-002 → D_SIGNAL | — |
| D_FACTOR | D-FACTOR-07 治理 | 因子metrics ← D_FACTOR-03 | 治理决策 → D_FACTOR-02 | L5: 因子废弃 |
| D_FACTOR | D-FACTOR-11 暴露 | CTR-002 ← D_FACTOR-06 | 暴露数据 → D_RISK | — |
| D_FACTOR | D-FACTOR-24 预算 | 暴露 ← D_FACTOR-11 | 风险预算 → D_RISK | L5: 风险限额 |
| D_BACKTEST | BT-18 衰减 | BacktestResult ← BT-01 | E-BT-04 → D_GOVERNANCE | L5: 衰减告警 |
| D_BACKTEST | BT-19~24 | BacktestResult ← BT-01/17 | 报告/分析 → D_FRONTEND/D_GOVERNANCE | — |
| D_BACKTEST | BT-25 部署 | validated Result ← BT-16 | DeploymentConfig → D_EX_CORE | L5: 部署决策 |
| D_DATA | D-DATA-04 推送 | raw market data | real-time stream → D_FACTOR-04 | — |
| D_DATA | D-DATA-20 Tick | Level-2 data | Tick data → D_BACKTEST | — |
| D_DATA_ENG | D-DATA-ENG-06 流处理 | real-time stream | processed stream → D_FACTOR-04 | — |
| D_DATA_ENG | D-DATA-ENG-07 漂移 | data metrics | drift events → D_AUTONOMY | L5: 漂移检测 |
| D_DATA_ENG | D-DATA-ENG-14 Schema | schema changes | migrated schemas | L5: 兼容性 |

### §8.6 执行结果

| 指标 | 值 | 状态 |
|------|---|:----:|
| depgraph 新增节点 | 25 (node_id=7304075~7304099) | ✅ |
| depgraph 更新元数据 | 17 (Category A) | ✅ |
| gate_reason 非空节点 | 47 (原5 + 新42) | ✅ |
| module_name_cn 非空节点 | 42 | ✅ |
| dataflow_jobs module_placeholder | 542 (含42项暂缓) | ✅ |
| decision_layers placeholder | 648 (含42项暂缓) | ✅ |
| sync_panorama_module --all | 717模块同步，0失败 | ✅ |
| align_panoramas: domain_mismatches | 0 | ✅ 硬门禁通过 |
| align_panoramas: state_drifts | 6 (均为既有，多数投票机制导致) | ⚠️ 君子协定 |
| align_panoramas: orphans | 255 (25项新无边 + ~230既有) | ⚠️ 君子协定 |
| align_panoramas: design_isolated | 18 (既有) | ⚠️ 君子协定 |

### §8.7 Category C — 已被生产代码覆盖（3项，跳过）

| 设计ID | 覆盖代码 | 说明 |
|--------|---------|------|
| D-DATA-ENG-04 DataQualityMonitor | data/cross_source_validator.py + integrity_checker.py | 已production |
| D-DATA-ENG-05 DataLineageTracker | data_governance/core/lineage_tracker.py | T5已完成 |
| D-DATA-ENG-08 PIT管理器 | data/pit_query.py | 已production |
