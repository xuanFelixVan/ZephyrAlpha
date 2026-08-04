---
doc_type: audit_report
title: 候选模块清单 — D_FACTOR
version: "1.0"
status: active
date: auto-generated
owner: auto-generator
ttl: permanent
---

# D_FACTOR 候选模块清单

> [← 返回索引](index.md)

> 本域候选 **200** 条（原有 2 + harvest 198）。
> harvest 去重四态: likely_new=83 / likely_implemented=115

## 完整清单

| ID | 名称 / Name | 大白话（干什么用） | 域 | 状态 | 一问卡点 | 优先级 | 触发信号摘要 | 下次复查 |
|------|------|------|------|------|------|:---:|------|------|
| CAND-HARVEST-0002 | Factor Factory 因子工厂 | C 027：因子工厂（P0） | D_FACTOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0003 | Pipeline 因子与信号生产管线 | C 009：因子与信号生产管线 | D_FACTOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0214 | Engine 引擎 | / D-FACTOR-01 / Engine / ✅ / 项目内有蓝图编号MOD-MASTER-001已建设 / 因子计算引擎+AST解析+算子库 / | D_FACTOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0215 | Registry 注册表 | / D-FACTOR-02 / Registry / ✅ / 项目内有蓝图编号MOD-MASTER-001已建设 / 因子注册表+版本树+依赖图 / | D_FACTOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0216 | Evaluation 评估器 | / D-FACTOR-03 / Evaluation / ✅ / 项目内有蓝图编号MOD-MASTER-001已建设 / 因子评估+过拟合检测+前视偏差 / | D_FACTOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0217 | Pipeline 管线 | / D-FACTOR-04 / Pipeline / ✅ / 项目内有蓝图编号MOD-MASTER-001已建设 / 因子管线+增量/批量/补算 / | D_FACTOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0218 | Barra Risk Model 模型风险 | / D-FACTOR-06 / Barra Risk Model / ✅ / / Barra风格因子10大+行业因子28申万 / | D_FACTOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0219 | A-Share Capital Flow Factor 因子 | / D-FACTOR-26 / A-Share Capital Flow Factor / ✅ / / A股资金流向因子四线 / | D_FACTOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0220 | A-Share Microstructure Factor 因子 | / D-FACTOR-27 / A-Share Microstructure Factor / ✅ / / A股微观结构因子 / | D_FACTOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0221 | Alpha Factor Calculation Engine 引擎因子 | / D-FACTOR-81 / Alpha Factor Calculation Engine / ✅ / / Alpha因子计算+价值+动量 / | D_FACTOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0375 | 模块39 多因子选股评分模型（Multi-Factor Stock Selection Scoring Model） | ### 模块39 多因子选股评分模型（Multi-Factor Stock Selection Scoring Model） | D_FACTOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0454 | L1 因子计算层 Factor Compute Layer | D-FACTOR Engine盘前全量+盘中增量计算 | D_FACTOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0455 | D-FACTOR Engine 因子计算引擎 | 因子计算引擎唯一因子计算逻辑来源SSoT | D_FACTOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0456 | 声明式因子定义 YAML DSL | 批/流双执行计划声明式定义 | D_FACTOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0457 | incremental_compute 增量因子计算 | 滑动窗口类因子避免全量重算 | D_FACTOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0458 | consistency_check 一致性引擎 | 日终离线/在线偏差检测 | D_FACTOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0486 | Volume Profile量能分布 Volume Profile | HVN/LVN节点Value Area POC量能分布分析 | D_FACTOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0487 | HVN/LVN节点 High/Low Volume Node | Volume Profile中成交量最大/最小的价格区间 | D_FACTOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0488 | Value Area 价值区域 | 日内70%成交量所在的价格区间 | D_FACTOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0489 | POC Point of Control 控制点 | 日内成交量最大的价格水平公允价值核心锚点 | D_FACTOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0490 | CVD买卖压力追踪 Cumulative Volume Delta | CVD=Σ(Buy Volume at Ask - Sell Volume at Bid) | D_FACTOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0491 | VPIN 知情交易概率 VPIN | 成交量切片买卖量不平衡累积概率VPIN高知情交易活跃 | D_FACTOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0497 | IRCF因子 Institutional Retail Contrarian Flow | 财通证券逆向资金流因子情境-特征匹配 | D_FACTOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0498 | OFI检测框架 Order Flow Imbalance | OFI=(Buy Volume-Sell Volume)/(Buy+Sell) | D_FACTOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0499 | Lee-Ready算法 Lee-Ready Algorithm | 交易价格≥中间价=买入≤中间价=卖出 | D_FACTOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0500 | BVC方法 Bulk Volume Classification | 聚合短时间窗口交易做统计推断准确率80-88% | D_FACTOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0505 | 统一技术图形识别引擎 Unified Technical Pattern Recognition Engine | DTW/CNN/Transformer统一识别所有图形类型 | D_FACTOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0506 | 图形模式库 Pattern Library | 反转/持续/趋势/支撑阻力/缠论/波浪图形 | D_FACTOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0507 | 统一识别算法 Unified Recognition Algorithm | DTW/CNN/Transformer/规则引擎 | D_FACTOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0508 | 多时间级别识别 Multi-Timeframe Recognition | 5min/15min/30min/60min/日线/周线/月线 | D_FACTOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0555 | 特征存储双存储架构 Feature Store Dual-Storage | > **对标**: AltStreet Quant 2.0 (2025) Feature Store / Databricks/Tecton Feature Store / Feature Store 2.0 (2025) 声明式定义 / | D_FACTOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0556 | 离线存储 Offline Store | Parquet按日分区支持PIT查询~100ms延迟 | D_FACTOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0557 | 在线存储 Online Store | Redis Hash Key:feature:{symbol}<5ms延迟 | D_FACTOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0558 | 特征注册表 Feature Registry | SQLite feature_registry.db因子元数据+血缘+质量+服务状态 | D_FACTOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0559 | 训练-服务一致性保证 Training-Serving Consistency | 单一定义原则+PIT正确性+版本对齐三重机制 | D_FACTOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0560 | 特征生命周期 Feature Lifecycle | 十阶段状态机CREATED→VALIDATED→...→RETIRED | D_FACTOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0561 | Governance 因子治理 | 标记废弃+停止在线服务+保留离线数据 | D_FACTOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0562 | DecayMonitor 因子衰减监控 | 持续IC/IR监控+衰减检测+相关性监控 | D_FACTOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0582 | 一致性引擎 Consistency Engine | / 7 / **一致性引擎（Consistency Engine）**：Feature Store 2.0核心组件，确保无论批处理还是流处理模式，特征在定义容差内产生等价结果。AltStreet Quant 2.0证实Feature Sto | D_FACTOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0583 | 实时特征计算管道 Real-time Feature Pipeline | / 26 / **Flink 2.x AI Functions**：Flink 2.2 (2025底)在SQL流处理中集成LLM能力，支持实时情感分析/智能分类/向量检索。阿里云AI_Translate/AI_Sentiment函数在流式计 | D_FACTOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0684 | Factor Orthogonalizer 因子正交化器 | 因子正交化对称正交PCA降维因子独立性检验共线性检测 | D_FACTOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0994 | Factor Exposure Calculator 因子暴露计算器 | 因子暴露计算器 | D_FACTOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0995 | Factor Risk Budget Allocator 因子风险预算分配器 | 因子风险预算分配器 | D_FACTOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1340 | Factor Correlation Analyzer 因子相关性分析器 | 滚动相关矩阵+条件相关性+聚类分析+共线性检测+因子语义去重 | D_FACTOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1341 | Factor Turnover Analyzer 因子换手率分析器 | 换手率计算+成本衰减模型+自相关系数+买卖价差估算 | D_FACTOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1342 | Causal Validator 因果验证器 | 因果因子验证(DoWhy/DML)+因果发现三阶段 | D_FACTOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1343 | ESG ESG因子 | ESG因子 | D_FACTOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1344 | Fundamental 基本面因子 | 基本面因子(基于iFind财务数据) | D_FACTOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1345 | Intraday 日内因子 | 日内因子(需3秒Tick管线) | D_FACTOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1346 | Factor Dependency Graph DAG 因子依赖图DAG | 因子依赖图DAG管理(Pipeline DAG子组件) | D_FACTOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1347 | Grayscale Rollout 灰度发布 | 灰度发布 | D_FACTOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1348 | SMC SMC因子 | SMC因子 | D_FACTOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1349 | IRL IRL因子 | IRL因子 | D_FACTOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1350 | Backpressure 背压控制 | 背压控制(Pipeline内部组件) | D_FACTOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1351 | 6-Step Flow 6步流程 | 6步流程 | D_FACTOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1352 | Lifecycle State Machine 生命周期状态机 | 生命周期状态机 | D_FACTOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1353 | IC/IR Evaluator IC/IR评估器 | Rank IC+ICIR计算(Evaluation子组件) | D_FACTOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1354 | CTR-001 Consumer CTR-001消费者 | CTR-001消费者(Engine内部组件) | D_FACTOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1355 | CTR-002/003 Producer CTR-002/003生产者 | CTR-002/003生产者(Engine内部组件) | D_FACTOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1356 | Batch Output 批量输出 | 批量输出(Pipeline内部组件) | D_FACTOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1357 | Multi-Factor Synthesis Validator 多因子合成验证器 | 多因子合成验证 | D_FACTOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1358 | 3-Level Judgment 三级判断 | 三级判断 | D_FACTOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1359 | IC Decay Analyzer IC衰减分析器 | IC衰减分析 | D_FACTOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1360 | IC_IR Calculator IC_IR计算器 | IC/IR计算子组件 | D_FACTOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1361 | 87-Alpha 87-Alpha因子 | 87-Alpha因子 | D_FACTOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1362 | Technical Indicator Factor 技术指标因子 | 技术指标因子(MA/MACD/RSI等) | D_FACTOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1363 | Pattern to Signal Converter 形态信号转化器 | 形态识别→信号转化 | D_FACTOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1364 | Market Structure Factor 市场结构因子 | 市场结构因子(涨跌家数比/涨停家数/市场宽度等) | D_FACTOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1365 | Sector Factor 板块因子 | 板块因子(板块强度/板块RS/风格因子暴露等) | D_FACTOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1366 | Institutional Behavior Factor 机构行为因子 | 机构行为因子(筹码集中度/机构净流入等) | D_FACTOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1367 | Layered Backtest 分层回测 | 分层回测 | D_FACTOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1368 | Cross-Market Factor 跨市场因子 | 跨市场因子(传导系数/VIX/美债利差等) | D_FACTOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1369 | Parameter Config Manager 参数配置管理器 | 参数配置管理 | D_FACTOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1370 | Factor Dependency DAG Manager 因子依赖DAG管理器 | 因子依赖DAG管理(基于53扩展) | D_FACTOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1371 | Distribution Feature Engineering 分布特征工程 | 分布特征工程(专供密度预测模型) | D_FACTOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1372 | Pastor-Stambaugh Liquidity Factor Pastor-Stambaugh流动性因子 | 系统性流动性风险因子 | D_FACTOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1373 | Correlation Redundancy Remover 相关性去冗余 | 相关性去冗余 | D_FACTOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1374 | Factor Portfolio Optimizer 因子组合优化器 | 因子组合优化 | D_FACTOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1375 | Factor Attribution 因子归因 | 因子归因(各因子对组合收益/风险的贡献度分析) | D_FACTOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1782 | Timing Engine 择时引擎 | 择时引擎(量能体制分类+条件IC分析) | D_FACTOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2252 | IC Decay Detection IC衰减检测 | IC衰减检测因子IC 60日移动平均趋势衰减大于50%为退化 | D_FACTOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2253 | Crowding Detection 拥挤度检测 | 拥挤度检测同策略参与者数量估计上升为超额收益将消失 | D_FACTOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2260 | D-FACTOR-04 Pipeline D-FACTOR-04管道 | D-FACTOR-04 Pipeline批次OpenLineage Run概念run_id=batch_id | D_FACTOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3634 | Overnight Global Market Contagion Model 隔夜全球市场传导模型 | 隔夜海外市场对A股传导效应 | D_FACTOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3635 | Global Market Contagion Quantification 全球市场传导量化 | 隔夜传导系数传导衰减波动率传导 | D_FACTOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3636 | Event Impact Assessment 事件影响评估 | 事件分类异常收益影响持续时间 | D_FACTOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3637 | Northbound Capital Flow Model 北向资金流向模型 | 北向资金Smart Money代理变量 | D_FACTOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3638 | Northbound Capital Signal 北向资金信号 | 净流入强度开盘30分钟信号行业偏好 | D_FACTOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3708 | Feature Serving API 特征服务API | 特征存储查询接口 | D_FACTOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3724 | D-FACTOR Engine 因子引擎 | D-FACTOR Engine batch/增量双模式 | D_FACTOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3886 | 因子计算 增量因子计算 Factor Incremental | Warm平面200ms延迟预算NumPy/Pandas向量化 | D_FACTOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3957 | CTR-001 Consumer 契约消费者 | Engine内部组件CTR-001消费者 | D_FACTOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3958 | CTR-002/003 Producer 契约生产者 | Engine内部组件CTR-002/003生产者 | D_FACTOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3959 | Backpressure 背压 | Pipeline内部组件背压 | D_FACTOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3960 | 因子依赖图DAG Factor Dependency DAG | Pipeline DAG子组件 | D_FACTOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3961 | 参数配置管理器 Parameter Config Manager | 配置管理 | D_FACTOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3962 | 因子依赖DAG管理器 Factor Dependency DAG Manager | 基于53扩展 | D_FACTOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3963 | Capital Flow 资金流 | 基于miniQMT资金流数据 | D_FACTOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3964 | Microstructure 微观结构 | 需Level-2逐笔成交数据 | D_FACTOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3965 | Fundamental 基本面 | 基于iFind财务数据 | D_FACTOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3966 | Intraday 日内 | 需3秒Tick管线稳定运行 | D_FACTOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3967 | SMC Smart Money Concept SMC聪明钱概念 | 需Level-2数据 | D_FACTOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3968 | IRL 机构行为识别 | 需Level-2大单数据+机构行为识别 | D_FACTOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3969 | Alpha Factor Alpha因子 | 基于Engine扩展量价动量价值情绪因子 | D_FACTOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3970 | 87-Alpha 87Alpha因子 | 需87个WorldQuant Alpha公式完整实现 | D_FACTOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3971 | 技术指标因子 Technical Indicator Factor | 基于Engine扩展MA MACD RSI等 | D_FACTOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3972 | 形态到信号转化 Pattern to Signal | 需统一图形识别引擎DTW CNN就绪 | D_FACTOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3973 | Pastor-Stambaugh Liquidity Factor PS流动性因子 | 系统性流动性风险因子 | D_FACTOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3974 | IC_IR计算 IC_IR Calculator | 70子组件 | D_FACTOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3975 | IC衰减分析器 IC Decay Analyzer | 需08 Decay Monitor就绪 | D_FACTOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3976 | 多因子合成验证器 Multi-Factor Synthesis Validator | 需大于5因子+70就绪 | D_FACTOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3977 | 相关性去冗余 Correlation Redundancy Remover | 需09 Correlation Analyzer就绪 | D_FACTOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3978 | 因子组合优化 Factor Portfolio Optimizer | 需84+D-PORTFOLIO就绪 | D_FACTOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3979 | Timing Engine 时机引擎 | 量能体制缩量平量放量GMM阈值分类 | D_FACTOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3980 | 量价因子 Price-Volume Factor | / 传导系数 🆕 / 交易决策 / Cross-Market Transmission Coefficient / D-FACTOR-102 Cross-Market Factor / VAR模型跨市场收益率Granger因果检验系数 / | D_FACTOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3981 | 波动率因子 Volatility Factor | ATR历史波动率下行波动率MDD VaR | D_FACTOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3982 | 成交量因子 Volume Factor | OBV VWAP MFI换手率量比 | D_FACTOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3983 | 市场结构因子 Market Structure Factor | 涨跌家数比涨停家数市场宽度NHNL封单率 | D_FACTOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3984 | 基本面因子 Fundamental Factor | PE PB ROE-TTM营收增速毛利率 | D_FACTOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3985 | Alpha因子 Alpha Factor | 价值动量质量成长波动率流动性情绪事件 | D_FACTOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3986 | 板块风格因子 Sector Style Factor | 板块强度板块RS风格因子暴露资金流入 | D_FACTOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3987 | 主力行为因子 Institutional Behavior Factor | 筹码集中度机构净流入龙虎榜北向 | D_FACTOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3988 | 另类因子 Alternative Factor | 舆情得分财报超预期龙虎榜融资融券 | D_FACTOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3989 | 宏观因子 Macro Factor | M2社融中美利差VIX Fed | D_FACTOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3990 | 跨市场因子 Cross-Market Factor | 传导系数VIX美债利差汇率A50期货 | D_FACTOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3991 | 风险因子 Risk Factor | 行业申万31规模价值动量 | D_FACTOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3992 | 统一图形识别引擎 Unified Pattern Recognition Engine | 1个统一引擎替代20+独立图形识别DTW CNN | D_FACTOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4004 | 一高七矮 Volume Profile HVN LVN | 日内量能Volume Profile HVN/LVN节点分布 | D_FACTOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4005 | 量能体制分类 Volume Regime Classification | 缩量平量放量GMM阈值分类成交量相对20日均值 | D_FACTOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4006 | 突破回踩动量因子 Breakout-Retest Momentum Factor | 突破N日高点回踩幅度量能放大 | D_FACTOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4007 | 体制条件因子有效性 Regime-Conditional Factor Effectiveness | 增量格局大盘蓝筹有效缩量格局小盘题材有效 | D_FACTOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4008 | 逆向资金买点 Contrarian Capital Flow Factor | 大盘下跌时个股资金净流入逆势强度比 | D_FACTOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4009 | 主力吸筹 Accumulation Factor | CVD上升价格横盘下跌买方压力积累 | D_FACTOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4010 | 主力派发 Distribution Factor | CVD下降价格横盘上涨卖方压力释放 | D_FACTOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4011 | 主力洗盘 Shakeout Factor | VPIN高价格急跌后快速恢复知情交易者洗盘 | D_FACTOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4012 | 缠论图形识别 Statistical Consolidation Zone | 笔线段中枢背驰MACD背离统计检测 | D_FACTOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4013 | 支撑阻力位检测 Support Resistance Level Detection | 局部极值点成交量聚集价位DTW匹配 | D_FACTOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4014 | 图表形态识别 Chart Pattern Recognition | 头肩顶双底W底三角形旗形DTW CNN分类 | D_FACTOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4015 | 冰山单检测 Hidden Order Detection Factor | 不可撤单阶段大额限价单占比隐藏意图指标 | D_FACTOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4016 | 开盘缺口因子 Opening Gap Factor | 开盘价前收盘前收盘匹配量权重 | D_FACTOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4017 | 抗跌因子 Downside Resistance Factor | 大盘跌X%时个股跌幅小于X×0.3 | D_FACTOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4018 | 逆涨因子 Contrarian Return Factor | 大盘跌X%时个股涨Y% | D_FACTOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4019 | 晚下单因子 Late Order Arrival Factor | 9:20-9:25下单比例知情交易者晚下单 | D_FACTOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4020 | 体制条件因子衰减 Regime-Conditional Factor Decay | 小市值因子在缩量环境下失效按Volume Regime分组 | D_FACTOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4021 | 庄家行为模式识别 Market Manipulation Pattern Detection | 异常交易模式识别自成交对倒拉抬打压 | D_FACTOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4022 | 群体博弈模拟 Game-Theoretic Agent Simulation | 多Agent博弈均衡价格偏离度 | D_FACTOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4023 | 筹码集中度 Ownership Concentration Factor | 股东户数变化十大流通股东持股比例集中度 | D_FACTOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4024 | 出货信号因子 Distribution Signal Factor | 波动率换手率交互项高波高换分布信号 | D_FACTOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4025 | 吸筹出货期检测 Accumulation Distribution Phase Detection | CVD趋势价格形态成交量模式三维度分类 | D_FACTOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4026 | IC因子替换 IC-Based Factor Replacement | 活跃池满N_max-4时新因子逐个对比池内IC最低者 | D_FACTOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4027 | 批量因子裁剪 Batch Factor Pruning | 全池大于64时按IC从休眠观察中裁撤 | D_FACTOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4028 | 主力净流入 Institutional Net Inflow Factor | 大单净买入金额总成交金额 | D_FACTOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4029 | 龙虎榜机构占比 Dragon-Tiger List Institutional Ratio | 龙虎榜买方机构席位占比 | D_FACTOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4030 | 北向持仓变化 Northbound Holding Change Factor | 沪深港通北向资金持股变化量流通股本 | D_FACTOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4031 | 板块强度 Sector Strength Factor | 板块指数相对大盘超额收益板块内上涨家数占比 | D_FACTOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4032 | 传导系数 Cross-Market Transmission Coefficient | VAR模型跨市场收益率Granger因果检验系数 | D_FACTOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4033 | 封单率 Limit Order Fill Rate Factor | 涨停封单量当日成交量 | D_FACTOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4034 | 市场宽度因子 Market Breadth Factors | 涨跌家数比涨停家数NHNL New High New Low | D_FACTOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4035 | HVN/LVN节点 Volume Profile HVN LVN | Volume Profile中成交量最大最小的价格区间 | D_FACTOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4036 | POC 公允价值核心 Point of Control | 日内成交量最大的价格水平公允价值锚点 | D_FACTOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4037 | CVD 累积买卖压力 Cumulative Volume Delta | 买方成交量减卖方成交量净买卖压力追踪 | D_FACTOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4038 | CVD价格背离 CVD Price Divergence | CVD下降价格创新高看跌背离机构卖出 | D_FACTOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4039 | 大盘下跌状态检测 Market Down State Detection | 3秒级检测大盘指数分时走势方向连续6个Tick绿盘下行 | D_FACTOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4040 | 下跌强度分级 Down Strength Classification | 缓跌中跌急跌3秒跌幅大于0.1%急跌 | D_FACTOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4041 | 逆势强度比 Contrarian Strength Ratio | 个股资金净流入大盘同期跌幅量化逆势程度 | D_FACTOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4042 | 逆势持续性 Contrarian Persistence | 连续N个3秒Tick个股资金净流入为正 | D_FACTOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4043 | 逆势个股排行 Contrarian Stock Ranking | 全市场按逆势强度比排序Top N自动关联板块概念 | D_FACTOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4044 | 虚拟开盘价轨迹 Virtual Open Price Trajectory | 9:15-9:25每5秒虚拟匹配价格收敛过程含信息 | D_FACTOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4045 | 虚拟匹配量 Virtual Match Volume | 每个时刻虚拟匹配成交量快速增长高参与度 | D_FACTOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4046 | 订单不平衡 Order Imbalance | 竞价期间买方委托量卖方委托量不平衡大于2x强方向信号 | D_FACTOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4047 | 价格偏离度 Price Deviation | 虚拟开盘价前收盘价前收盘价偏离大于2%信息驱动 | D_FACTOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4048 | 晚下单比例 Late Order Ratio | 9:20-9:25下单量总下单量知情交易者晚下单 | D_FACTOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4049 | 撤单率 Cancel Rate | 9:15-9:20可撤单阶段撤单比例高撤单率试探性报价 | D_FACTOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4050 | 冰山单占比 Iceberg Order Ratio | 9:20-9:25不可撤单阶段大额限价单占比隐藏真实意图 | D_FACTOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4051 | 滞后项构造 Lag Feature Construction | 因子k期滞后滚动窗口统计量因子变化率 | D_FACTOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4052 | 交互项构造 Interaction Feature Construction | 因子两两交互因子市场状态交互因子机构行为阶段交互 | D_FACTOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4053 | 分布形态统计量 Distribution Shape Statistics | 滚动收益率偏度峰度滚动VaR CVaR分布拟合度 | D_FACTOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4054 | 双存储架构 Dual Storage Architecture | 离线Parquet PIT训练回测在线Redis实时查询Feature Registry SQLite | D_FACTOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4055 | 特征注册表 Feature Registry Schema | 元数据数据血缘质量指标服务状态版本历史五表 | D_FACTOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4056 | 训练服务一致性引擎 Training Serving Consistency Engine | 单一定义原则PIT正确性版本对齐一致性引擎四重机制 | D_FACTOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4057 | 特征生命周期十阶段状态机 Feature Lifecycle State Machine | 2. **PIT正确性**: 训练时get_features(as_of=...)→DuckDB AS OF JOIN仅返回computed_at≤as_of的因子值；推理时get_online_features(symbol)→Redis | D_FACTOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4058 | 入池观察池 Probation Pool | 🆕 **入池观察(Probation Pool)**: 新因子IC显著但未通过Bonferroni/BH多重检验校正→进入观察池(非正式因子池)→等待更多数据积累后重新检验→通过后入池。与'衰减观察'区别：衰减观察=活跃因子IC衰退监控(退 | D_FACTOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4059 | PIT一致性保证 PIT Consistency Guarantee | 因子值时间不可逆财务数据公告日约束幸存者偏差修正三条公理 | D_FACTOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4060 | 因子注册表合规 Factor Registry Compliance | 因子ID版本代码指纹参数指纹模型注册表不可变 | D_FACTOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4061 | 因子血缘合规 Factor Lineage Compliance | OpenLineage标准数据血缘追踪因子血缘图 | D_FACTOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4062 | 因子暴露合规 Factor Exposure Compliance | C-004持仓检查行业基准对比因子暴露监控 | D_FACTOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4063 | 因子版本管理 Factor Version Management | 语义化版本号变更diff回滚需人工审核 | D_FACTOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4064 | 因子退役审计 Factor Retirement Audit | 退役策略指纹入库影响分析报告下游影响通知 | D_FACTOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4065 | 因子权重变更审批分级 Factor Weight Change Approval Tier | L1±5%AI自动L2±5%~20%AI自动24h人工复核 | D_FACTOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4066 | 因子计算审计日志 Factor Compute Audit Log | 输入数据指纹计算参数输出值时间戳哈希链保留5年 | D_FACTOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4067 | 因子数据血缘追踪 Factor Data Lineage Tracking | 原始数据源特征因子完整链路数据血缘图保留5年 | D_FACTOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4068 | 因子性能审计 Factor Performance Audit | IC IR换手率衰减率持续监控记录哈希链保留3年 | D_FACTOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4069 | 因子暴露审计 Factor Exposure Audit | 截面快照时序变化行业偏离记录哈希链保留5年 | D_FACTOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4070 | 研究Agent Researcher Agent | / 研究Agent(Researcher) / **产出→D-FACTOR**: 发现新因子后提交提案至因子域 / 消费: D-DATA行情+D-ALT-DATA另类+D-KNOWLEDGE知识图谱 → 产出: 新因子提案+策略代码草稿 / | D_FACTOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4071 | 信号Agent Signal Gen Agent | / 信号Agent(Signal Gen) / **消费←D-FACTOR**: 读取因子值作为信号生成输入 / 消费: D-FACTOR因子值(CTR-002)+D-SIGNAL策略信号+D-ML-SERVE模型推理 → 产出: 加权信号 | D_FACTOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4921 | Causal Factor Validation Layer 因果因子验证层 | DoWhy/DML→区分相关vs因果→因果因子加权提升 | D_FACTOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4922 | KAN Explainable Function Approximator KAN可解释函数逼近 | 替代QNN中MLP层参数更少 | D_FACTOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4923 | UFL Deterministic Fact Layer UFL确定性事实层 | / — / UFL确定性事实层 / FeatureStore子集，is_deterministic=True / ✅ / | D_FACTOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-FAC-001 | Factor Cache / 因子缓存 | 因子数量增长后,每日全量重算导致计算延迟>50ms | D_FACTOR | 延后（deferred） | 一问通过 | P2 | 因子数量>10(当前不足) 等3条 | 2027-07-31 |
| CAND-FAC-002 | FactorMeta Pydantic Migration / FactorMeta Pydantic迁移 | FactorMeta 使用 @dataclass 违反 KBG-0040 全局 Pydantic 强制约束,与系统其余 Pydantic 数据模型不一致,序列化/校验行为不统一 | D_FACTOR | 延后（deferred） | 一问通过 | P1 | KBG-0040 Pydantic 强制门禁启用(当前君子协定) 等3条 | 2026-11-30 |

## 按一问卡点分组（为什么没开发）

> 一问标准（裁定 2026-08-04）：仅 q1 已实现/重复。q1「是」即不进 depgraph 设计态，登记在候选库。原 q2/q3/q4 灰度已废。

### 待评估（198 条）

| ID | 名称 | 大白话（干什么用） | 域 | 卡点理由 | 替代方案 |
|------|------|------|------|------|------|
| CAND-HARVEST-0002 | Factor Factory 因子工厂 | C 027：因子工厂（P0） | D_FACTOR | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-0003 | Pipeline 因子与信号生产管线 | C 009：因子与信号生产管线 | D_FACTOR | harvest待评估（likely_new） |  |
| CAND-HARVEST-0214 | Engine 引擎 | / D-FACTOR-01 / Engine / ✅ / 项目内有蓝图编号MOD-MASTER-001已建设 / 因子计算引擎+AST解析+算子库 / | D_FACTOR | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-0215 | Registry 注册表 | / D-FACTOR-02 / Registry / ✅ / 项目内有蓝图编号MOD-MASTER-001已建设 / 因子注册表+版本树+依赖图 / | D_FACTOR | harvest待评估（likely_new） |  |
| CAND-HARVEST-0216 | Evaluation 评估器 | / D-FACTOR-03 / Evaluation / ✅ / 项目内有蓝图编号MOD-MASTER-001已建设 / 因子评估+过拟合检测+前视偏差 / | D_FACTOR | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-0217 | Pipeline 管线 | / D-FACTOR-04 / Pipeline / ✅ / 项目内有蓝图编号MOD-MASTER-001已建设 / 因子管线+增量/批量/补算 / | D_FACTOR | harvest待评估（likely_new） |  |
| CAND-HARVEST-0218 | Barra Risk Model 模型风险 | / D-FACTOR-06 / Barra Risk Model / ✅ / / Barra风格因子10大+行业因子28申万 / | D_FACTOR | harvest待评估（likely_new） |  |
| CAND-HARVEST-0219 | A-Share Capital Flow Factor 因子 | / D-FACTOR-26 / A-Share Capital Flow Factor / ✅ / / A股资金流向因子四线 / | D_FACTOR | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-0220 | A-Share Microstructure Factor 因子 | / D-FACTOR-27 / A-Share Microstructure Factor / ✅ / / A股微观结构因子 / | D_FACTOR | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-0221 | Alpha Factor Calculation Engine 引擎因子 | / D-FACTOR-81 / Alpha Factor Calculation Engine / ✅ / / Alpha因子计算+价值+动量 / | D_FACTOR | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-0375 | 模块39 多因子选股评分模型（Multi-Factor Stock Selection Scoring Model） | ### 模块39 多因子选股评分模型（Multi-Factor Stock Selection Scoring Model） | D_FACTOR | harvest待评估（likely_new） |  |
| CAND-HARVEST-0454 | L1 因子计算层 Factor Compute Layer | D-FACTOR Engine盘前全量+盘中增量计算 | D_FACTOR | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-0455 | D-FACTOR Engine 因子计算引擎 | 因子计算引擎唯一因子计算逻辑来源SSoT | D_FACTOR | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-0456 | 声明式因子定义 YAML DSL | 批/流双执行计划声明式定义 | D_FACTOR | harvest待评估（likely_new） |  |
| CAND-HARVEST-0457 | incremental_compute 增量因子计算 | 滑动窗口类因子避免全量重算 | D_FACTOR | harvest待评估（likely_new） |  |
| CAND-HARVEST-0458 | consistency_check 一致性引擎 | 日终离线/在线偏差检测 | D_FACTOR | harvest待评估（likely_new） |  |
| CAND-HARVEST-0486 | Volume Profile量能分布 Volume Profile | HVN/LVN节点Value Area POC量能分布分析 | D_FACTOR | harvest待评估（likely_new） |  |
| CAND-HARVEST-0487 | HVN/LVN节点 High/Low Volume Node | Volume Profile中成交量最大/最小的价格区间 | D_FACTOR | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-0488 | Value Area 价值区域 | 日内70%成交量所在的价格区间 | D_FACTOR | harvest待评估（likely_new） |  |
| CAND-HARVEST-0489 | POC Point of Control 控制点 | 日内成交量最大的价格水平公允价值核心锚点 | D_FACTOR | harvest待评估（likely_new） |  |
| CAND-HARVEST-0490 | CVD买卖压力追踪 Cumulative Volume Delta | CVD=Σ(Buy Volume at Ask - Sell Volume at Bid) | D_FACTOR | harvest待评估（likely_new） |  |
| CAND-HARVEST-0491 | VPIN 知情交易概率 VPIN | 成交量切片买卖量不平衡累积概率VPIN高知情交易活跃 | D_FACTOR | harvest待评估（likely_new） |  |
| CAND-HARVEST-0497 | IRCF因子 Institutional Retail Contrarian Flow | 财通证券逆向资金流因子情境-特征匹配 | D_FACTOR | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-0498 | OFI检测框架 Order Flow Imbalance | OFI=(Buy Volume-Sell Volume)/(Buy+Sell) | D_FACTOR | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-0499 | Lee-Ready算法 Lee-Ready Algorithm | 交易价格≥中间价=买入≤中间价=卖出 | D_FACTOR | harvest待评估（likely_new） |  |
| CAND-HARVEST-0500 | BVC方法 Bulk Volume Classification | 聚合短时间窗口交易做统计推断准确率80-88% | D_FACTOR | harvest待评估（likely_new） |  |
| CAND-HARVEST-0505 | 统一技术图形识别引擎 Unified Technical Pattern Recognition Engine | DTW/CNN/Transformer统一识别所有图形类型 | D_FACTOR | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-0506 | 图形模式库 Pattern Library | 反转/持续/趋势/支撑阻力/缠论/波浪图形 | D_FACTOR | harvest待评估（likely_new） |  |
| CAND-HARVEST-0507 | 统一识别算法 Unified Recognition Algorithm | DTW/CNN/Transformer/规则引擎 | D_FACTOR | harvest待评估（likely_new） |  |
| CAND-HARVEST-0508 | 多时间级别识别 Multi-Timeframe Recognition | 5min/15min/30min/60min/日线/周线/月线 | D_FACTOR | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-0555 | 特征存储双存储架构 Feature Store Dual-Storage | > **对标**: AltStreet Quant 2.0 (2025) Feature Store / Databricks/Tecton Feature Store / Feature Store 2.0 (2025) 声明式定义 / | D_FACTOR | harvest待评估（likely_new） |  |
| CAND-HARVEST-0556 | 离线存储 Offline Store | Parquet按日分区支持PIT查询~100ms延迟 | D_FACTOR | harvest待评估（likely_new） |  |
| CAND-HARVEST-0557 | 在线存储 Online Store | Redis Hash Key:feature:{symbol}<5ms延迟 | D_FACTOR | harvest待评估（likely_new） |  |
| CAND-HARVEST-0558 | 特征注册表 Feature Registry | SQLite feature_registry.db因子元数据+血缘+质量+服务状态 | D_FACTOR | harvest待评估（likely_new） |  |
| CAND-HARVEST-0559 | 训练-服务一致性保证 Training-Serving Consistency | 单一定义原则+PIT正确性+版本对齐三重机制 | D_FACTOR | harvest待评估（likely_new） |  |
| CAND-HARVEST-0560 | 特征生命周期 Feature Lifecycle | 十阶段状态机CREATED→VALIDATED→...→RETIRED | D_FACTOR | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-0561 | Governance 因子治理 | 标记废弃+停止在线服务+保留离线数据 | D_FACTOR | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-0562 | DecayMonitor 因子衰减监控 | 持续IC/IR监控+衰减检测+相关性监控 | D_FACTOR | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-0582 | 一致性引擎 Consistency Engine | / 7 / **一致性引擎（Consistency Engine）**：Feature Store 2.0核心组件，确保无论批处理还是流处理模式，特征在定义容差内产生等价结果。AltStreet Quant 2.0证实Feature Sto | D_FACTOR | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-0583 | 实时特征计算管道 Real-time Feature Pipeline | / 26 / **Flink 2.x AI Functions**：Flink 2.2 (2025底)在SQL流处理中集成LLM能力，支持实时情感分析/智能分类/向量检索。阿里云AI_Translate/AI_Sentiment函数在流式计 | D_FACTOR | harvest待评估（likely_new） |  |
| CAND-HARVEST-0684 | Factor Orthogonalizer 因子正交化器 | 因子正交化对称正交PCA降维因子独立性检验共线性检测 | D_FACTOR | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-0994 | Factor Exposure Calculator 因子暴露计算器 | 因子暴露计算器 | D_FACTOR | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-0995 | Factor Risk Budget Allocator 因子风险预算分配器 | 因子风险预算分配器 | D_FACTOR | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1340 | Factor Correlation Analyzer 因子相关性分析器 | 滚动相关矩阵+条件相关性+聚类分析+共线性检测+因子语义去重 | D_FACTOR | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1341 | Factor Turnover Analyzer 因子换手率分析器 | 换手率计算+成本衰减模型+自相关系数+买卖价差估算 | D_FACTOR | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1342 | Causal Validator 因果验证器 | 因果因子验证(DoWhy/DML)+因果发现三阶段 | D_FACTOR | harvest待评估（likely_new） |  |
| CAND-HARVEST-1343 | ESG ESG因子 | ESG因子 | D_FACTOR | harvest待评估（likely_new） |  |
| CAND-HARVEST-1344 | Fundamental 基本面因子 | 基本面因子(基于iFind财务数据) | D_FACTOR | harvest待评估（likely_new） |  |
| CAND-HARVEST-1345 | Intraday 日内因子 | 日内因子(需3秒Tick管线) | D_FACTOR | harvest待评估（likely_new） |  |
| CAND-HARVEST-1346 | Factor Dependency Graph DAG 因子依赖图DAG | 因子依赖图DAG管理(Pipeline DAG子组件) | D_FACTOR | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1347 | Grayscale Rollout 灰度发布 | 灰度发布 | D_FACTOR | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1348 | SMC SMC因子 | SMC因子 | D_FACTOR | harvest待评估（likely_new） |  |
| CAND-HARVEST-1349 | IRL IRL因子 | IRL因子 | D_FACTOR | harvest待评估（likely_new） |  |
| CAND-HARVEST-1350 | Backpressure 背压控制 | 背压控制(Pipeline内部组件) | D_FACTOR | harvest待评估（likely_new） |  |
| CAND-HARVEST-1351 | 6-Step Flow 6步流程 | 6步流程 | D_FACTOR | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1352 | Lifecycle State Machine 生命周期状态机 | 生命周期状态机 | D_FACTOR | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1353 | IC/IR Evaluator IC/IR评估器 | Rank IC+ICIR计算(Evaluation子组件) | D_FACTOR | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1354 | CTR-001 Consumer CTR-001消费者 | CTR-001消费者(Engine内部组件) | D_FACTOR | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1355 | CTR-002/003 Producer CTR-002/003生产者 | CTR-002/003生产者(Engine内部组件) | D_FACTOR | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1356 | Batch Output 批量输出 | 批量输出(Pipeline内部组件) | D_FACTOR | harvest待评估（likely_new） |  |
| CAND-HARVEST-1357 | Multi-Factor Synthesis Validator 多因子合成验证器 | 多因子合成验证 | D_FACTOR | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1358 | 3-Level Judgment 三级判断 | 三级判断 | D_FACTOR | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1359 | IC Decay Analyzer IC衰减分析器 | IC衰减分析 | D_FACTOR | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1360 | IC_IR Calculator IC_IR计算器 | IC/IR计算子组件 | D_FACTOR | harvest待评估（likely_new） |  |
| CAND-HARVEST-1361 | 87-Alpha 87-Alpha因子 | 87-Alpha因子 | D_FACTOR | harvest待评估（likely_new） |  |
| CAND-HARVEST-1362 | Technical Indicator Factor 技术指标因子 | 技术指标因子(MA/MACD/RSI等) | D_FACTOR | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1363 | Pattern to Signal Converter 形态信号转化器 | 形态识别→信号转化 | D_FACTOR | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1364 | Market Structure Factor 市场结构因子 | 市场结构因子(涨跌家数比/涨停家数/市场宽度等) | D_FACTOR | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1365 | Sector Factor 板块因子 | 板块因子(板块强度/板块RS/风格因子暴露等) | D_FACTOR | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1366 | Institutional Behavior Factor 机构行为因子 | 机构行为因子(筹码集中度/机构净流入等) | D_FACTOR | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1367 | Layered Backtest 分层回测 | 分层回测 | D_FACTOR | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1368 | Cross-Market Factor 跨市场因子 | 跨市场因子(传导系数/VIX/美债利差等) | D_FACTOR | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1369 | Parameter Config Manager 参数配置管理器 | 参数配置管理 | D_FACTOR | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1370 | Factor Dependency DAG Manager 因子依赖DAG管理器 | 因子依赖DAG管理(基于53扩展) | D_FACTOR | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1371 | Distribution Feature Engineering 分布特征工程 | 分布特征工程(专供密度预测模型) | D_FACTOR | harvest待评估（likely_new） |  |
| CAND-HARVEST-1372 | Pastor-Stambaugh Liquidity Factor Pastor-Stambaugh流动性因子 | 系统性流动性风险因子 | D_FACTOR | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1373 | Correlation Redundancy Remover 相关性去冗余 | 相关性去冗余 | D_FACTOR | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1374 | Factor Portfolio Optimizer 因子组合优化器 | 因子组合优化 | D_FACTOR | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1375 | Factor Attribution 因子归因 | 因子归因(各因子对组合收益/风险的贡献度分析) | D_FACTOR | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1782 | Timing Engine 择时引擎 | 择时引擎(量能体制分类+条件IC分析) | D_FACTOR | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-2252 | IC Decay Detection IC衰减检测 | IC衰减检测因子IC 60日移动平均趋势衰减大于50%为退化 | D_FACTOR | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-2253 | Crowding Detection 拥挤度检测 | 拥挤度检测同策略参与者数量估计上升为超额收益将消失 | D_FACTOR | harvest待评估（likely_new） |  |
| CAND-HARVEST-2260 | D-FACTOR-04 Pipeline D-FACTOR-04管道 | D-FACTOR-04 Pipeline批次OpenLineage Run概念run_id=batch_id | D_FACTOR | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-3634 | Overnight Global Market Contagion Model 隔夜全球市场传导模型 | 隔夜海外市场对A股传导效应 | D_FACTOR | harvest待评估（likely_new） |  |
| CAND-HARVEST-3635 | Global Market Contagion Quantification 全球市场传导量化 | 隔夜传导系数传导衰减波动率传导 | D_FACTOR | harvest待评估（likely_new） |  |
| CAND-HARVEST-3636 | Event Impact Assessment 事件影响评估 | 事件分类异常收益影响持续时间 | D_FACTOR | harvest待评估（likely_new） |  |
| CAND-HARVEST-3637 | Northbound Capital Flow Model 北向资金流向模型 | 北向资金Smart Money代理变量 | D_FACTOR | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-3638 | Northbound Capital Signal 北向资金信号 | 净流入强度开盘30分钟信号行业偏好 | D_FACTOR | harvest待评估（likely_new） |  |
| CAND-HARVEST-3708 | Feature Serving API 特征服务API | 特征存储查询接口 | D_FACTOR | harvest待评估（likely_new） |  |
| CAND-HARVEST-3724 | D-FACTOR Engine 因子引擎 | D-FACTOR Engine batch/增量双模式 | D_FACTOR | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-3886 | 因子计算 增量因子计算 Factor Incremental | Warm平面200ms延迟预算NumPy/Pandas向量化 | D_FACTOR | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-3957 | CTR-001 Consumer 契约消费者 | Engine内部组件CTR-001消费者 | D_FACTOR | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-3958 | CTR-002/003 Producer 契约生产者 | Engine内部组件CTR-002/003生产者 | D_FACTOR | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-3959 | Backpressure 背压 | Pipeline内部组件背压 | D_FACTOR | harvest待评估（likely_new） |  |
| CAND-HARVEST-3960 | 因子依赖图DAG Factor Dependency DAG | Pipeline DAG子组件 | D_FACTOR | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-3961 | 参数配置管理器 Parameter Config Manager | 配置管理 | D_FACTOR | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-3962 | 因子依赖DAG管理器 Factor Dependency DAG Manager | 基于53扩展 | D_FACTOR | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-3963 | Capital Flow 资金流 | 基于miniQMT资金流数据 | D_FACTOR | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-3964 | Microstructure 微观结构 | 需Level-2逐笔成交数据 | D_FACTOR | harvest待评估（likely_new） |  |
| CAND-HARVEST-3965 | Fundamental 基本面 | 基于iFind财务数据 | D_FACTOR | harvest待评估（likely_new） |  |
| CAND-HARVEST-3966 | Intraday 日内 | 需3秒Tick管线稳定运行 | D_FACTOR | harvest待评估（likely_new） |  |
| CAND-HARVEST-3967 | SMC Smart Money Concept SMC聪明钱概念 | 需Level-2数据 | D_FACTOR | harvest待评估（likely_new） |  |
| CAND-HARVEST-3968 | IRL 机构行为识别 | 需Level-2大单数据+机构行为识别 | D_FACTOR | harvest待评估（likely_new） |  |
| CAND-HARVEST-3969 | Alpha Factor Alpha因子 | 基于Engine扩展量价动量价值情绪因子 | D_FACTOR | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-3970 | 87-Alpha 87Alpha因子 | 需87个WorldQuant Alpha公式完整实现 | D_FACTOR | harvest待评估（likely_new） |  |
| CAND-HARVEST-3971 | 技术指标因子 Technical Indicator Factor | 基于Engine扩展MA MACD RSI等 | D_FACTOR | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-3972 | 形态到信号转化 Pattern to Signal | 需统一图形识别引擎DTW CNN就绪 | D_FACTOR | harvest待评估（likely_new） |  |
| CAND-HARVEST-3973 | Pastor-Stambaugh Liquidity Factor PS流动性因子 | 系统性流动性风险因子 | D_FACTOR | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-3974 | IC_IR计算 IC_IR Calculator | 70子组件 | D_FACTOR | harvest待评估（likely_new） |  |
| CAND-HARVEST-3975 | IC衰减分析器 IC Decay Analyzer | 需08 Decay Monitor就绪 | D_FACTOR | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-3976 | 多因子合成验证器 Multi-Factor Synthesis Validator | 需大于5因子+70就绪 | D_FACTOR | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-3977 | 相关性去冗余 Correlation Redundancy Remover | 需09 Correlation Analyzer就绪 | D_FACTOR | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-3978 | 因子组合优化 Factor Portfolio Optimizer | 需84+D-PORTFOLIO就绪 | D_FACTOR | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-3979 | Timing Engine 时机引擎 | 量能体制缩量平量放量GMM阈值分类 | D_FACTOR | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-3980 | 量价因子 Price-Volume Factor | / 传导系数 🆕 / 交易决策 / Cross-Market Transmission Coefficient / D-FACTOR-102 Cross-Market Factor / VAR模型跨市场收益率Granger因果检验系数 / | D_FACTOR | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-3981 | 波动率因子 Volatility Factor | ATR历史波动率下行波动率MDD VaR | D_FACTOR | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-3982 | 成交量因子 Volume Factor | OBV VWAP MFI换手率量比 | D_FACTOR | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-3983 | 市场结构因子 Market Structure Factor | 涨跌家数比涨停家数市场宽度NHNL封单率 | D_FACTOR | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-3984 | 基本面因子 Fundamental Factor | PE PB ROE-TTM营收增速毛利率 | D_FACTOR | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-3985 | Alpha因子 Alpha Factor | 价值动量质量成长波动率流动性情绪事件 | D_FACTOR | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-3986 | 板块风格因子 Sector Style Factor | 板块强度板块RS风格因子暴露资金流入 | D_FACTOR | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-3987 | 主力行为因子 Institutional Behavior Factor | 筹码集中度机构净流入龙虎榜北向 | D_FACTOR | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-3988 | 另类因子 Alternative Factor | 舆情得分财报超预期龙虎榜融资融券 | D_FACTOR | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-3989 | 宏观因子 Macro Factor | M2社融中美利差VIX Fed | D_FACTOR | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-3990 | 跨市场因子 Cross-Market Factor | 传导系数VIX美债利差汇率A50期货 | D_FACTOR | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-3991 | 风险因子 Risk Factor | 行业申万31规模价值动量 | D_FACTOR | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-3992 | 统一图形识别引擎 Unified Pattern Recognition Engine | 1个统一引擎替代20+独立图形识别DTW CNN | D_FACTOR | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-4004 | 一高七矮 Volume Profile HVN LVN | 日内量能Volume Profile HVN/LVN节点分布 | D_FACTOR | harvest待评估（likely_new） |  |
| CAND-HARVEST-4005 | 量能体制分类 Volume Regime Classification | 缩量平量放量GMM阈值分类成交量相对20日均值 | D_FACTOR | harvest待评估（likely_new） |  |
| CAND-HARVEST-4006 | 突破回踩动量因子 Breakout-Retest Momentum Factor | 突破N日高点回踩幅度量能放大 | D_FACTOR | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-4007 | 体制条件因子有效性 Regime-Conditional Factor Effectiveness | 增量格局大盘蓝筹有效缩量格局小盘题材有效 | D_FACTOR | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-4008 | 逆向资金买点 Contrarian Capital Flow Factor | 大盘下跌时个股资金净流入逆势强度比 | D_FACTOR | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-4009 | 主力吸筹 Accumulation Factor | CVD上升价格横盘下跌买方压力积累 | D_FACTOR | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-4010 | 主力派发 Distribution Factor | CVD下降价格横盘上涨卖方压力释放 | D_FACTOR | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-4011 | 主力洗盘 Shakeout Factor | VPIN高价格急跌后快速恢复知情交易者洗盘 | D_FACTOR | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-4012 | 缠论图形识别 Statistical Consolidation Zone | 笔线段中枢背驰MACD背离统计检测 | D_FACTOR | harvest待评估（likely_new） |  |
| CAND-HARVEST-4013 | 支撑阻力位检测 Support Resistance Level Detection | 局部极值点成交量聚集价位DTW匹配 | D_FACTOR | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-4014 | 图表形态识别 Chart Pattern Recognition | 头肩顶双底W底三角形旗形DTW CNN分类 | D_FACTOR | harvest待评估（likely_new） |  |
| CAND-HARVEST-4015 | 冰山单检测 Hidden Order Detection Factor | 不可撤单阶段大额限价单占比隐藏意图指标 | D_FACTOR | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-4016 | 开盘缺口因子 Opening Gap Factor | 开盘价前收盘前收盘匹配量权重 | D_FACTOR | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-4017 | 抗跌因子 Downside Resistance Factor | 大盘跌X%时个股跌幅小于X×0.3 | D_FACTOR | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-4018 | 逆涨因子 Contrarian Return Factor | 大盘跌X%时个股涨Y% | D_FACTOR | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-4019 | 晚下单因子 Late Order Arrival Factor | 9:20-9:25下单比例知情交易者晚下单 | D_FACTOR | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-4020 | 体制条件因子衰减 Regime-Conditional Factor Decay | 小市值因子在缩量环境下失效按Volume Regime分组 | D_FACTOR | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-4021 | 庄家行为模式识别 Market Manipulation Pattern Detection | 异常交易模式识别自成交对倒拉抬打压 | D_FACTOR | harvest待评估（likely_new） |  |
| CAND-HARVEST-4022 | 群体博弈模拟 Game-Theoretic Agent Simulation | 多Agent博弈均衡价格偏离度 | D_FACTOR | harvest待评估（likely_new） |  |
| CAND-HARVEST-4023 | 筹码集中度 Ownership Concentration Factor | 股东户数变化十大流通股东持股比例集中度 | D_FACTOR | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-4024 | 出货信号因子 Distribution Signal Factor | 波动率换手率交互项高波高换分布信号 | D_FACTOR | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-4025 | 吸筹出货期检测 Accumulation Distribution Phase Detection | CVD趋势价格形态成交量模式三维度分类 | D_FACTOR | harvest待评估（likely_new） |  |
| CAND-HARVEST-4026 | IC因子替换 IC-Based Factor Replacement | 活跃池满N_max-4时新因子逐个对比池内IC最低者 | D_FACTOR | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-4027 | 批量因子裁剪 Batch Factor Pruning | 全池大于64时按IC从休眠观察中裁撤 | D_FACTOR | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-4028 | 主力净流入 Institutional Net Inflow Factor | 大单净买入金额总成交金额 | D_FACTOR | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-4029 | 龙虎榜机构占比 Dragon-Tiger List Institutional Ratio | 龙虎榜买方机构席位占比 | D_FACTOR | harvest待评估（likely_new） |  |
| CAND-HARVEST-4030 | 北向持仓变化 Northbound Holding Change Factor | 沪深港通北向资金持股变化量流通股本 | D_FACTOR | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-4031 | 板块强度 Sector Strength Factor | 板块指数相对大盘超额收益板块内上涨家数占比 | D_FACTOR | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-4032 | 传导系数 Cross-Market Transmission Coefficient | VAR模型跨市场收益率Granger因果检验系数 | D_FACTOR | harvest待评估（likely_new） |  |
| CAND-HARVEST-4033 | 封单率 Limit Order Fill Rate Factor | 涨停封单量当日成交量 | D_FACTOR | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-4034 | 市场宽度因子 Market Breadth Factors | 涨跌家数比涨停家数NHNL New High New Low | D_FACTOR | harvest待评估（likely_new） |  |
| CAND-HARVEST-4035 | HVN/LVN节点 Volume Profile HVN LVN | Volume Profile中成交量最大最小的价格区间 | D_FACTOR | harvest待评估（likely_new） |  |
| CAND-HARVEST-4036 | POC 公允价值核心 Point of Control | 日内成交量最大的价格水平公允价值锚点 | D_FACTOR | harvest待评估（likely_new） |  |
| CAND-HARVEST-4037 | CVD 累积买卖压力 Cumulative Volume Delta | 买方成交量减卖方成交量净买卖压力追踪 | D_FACTOR | harvest待评估（likely_new） |  |
| CAND-HARVEST-4038 | CVD价格背离 CVD Price Divergence | CVD下降价格创新高看跌背离机构卖出 | D_FACTOR | harvest待评估（likely_new） |  |
| CAND-HARVEST-4039 | 大盘下跌状态检测 Market Down State Detection | 3秒级检测大盘指数分时走势方向连续6个Tick绿盘下行 | D_FACTOR | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-4040 | 下跌强度分级 Down Strength Classification | 缓跌中跌急跌3秒跌幅大于0.1%急跌 | D_FACTOR | harvest待评估（likely_new） |  |
| CAND-HARVEST-4041 | 逆势强度比 Contrarian Strength Ratio | 个股资金净流入大盘同期跌幅量化逆势程度 | D_FACTOR | harvest待评估（likely_new） |  |
| CAND-HARVEST-4042 | 逆势持续性 Contrarian Persistence | 连续N个3秒Tick个股资金净流入为正 | D_FACTOR | harvest待评估（likely_new） |  |
| CAND-HARVEST-4043 | 逆势个股排行 Contrarian Stock Ranking | 全市场按逆势强度比排序Top N自动关联板块概念 | D_FACTOR | harvest待评估（likely_new） |  |
| CAND-HARVEST-4044 | 虚拟开盘价轨迹 Virtual Open Price Trajectory | 9:15-9:25每5秒虚拟匹配价格收敛过程含信息 | D_FACTOR | harvest待评估（likely_new） |  |
| CAND-HARVEST-4045 | 虚拟匹配量 Virtual Match Volume | 每个时刻虚拟匹配成交量快速增长高参与度 | D_FACTOR | harvest待评估（likely_new） |  |
| CAND-HARVEST-4046 | 订单不平衡 Order Imbalance | 竞价期间买方委托量卖方委托量不平衡大于2x强方向信号 | D_FACTOR | harvest待评估（likely_new） |  |
| CAND-HARVEST-4047 | 价格偏离度 Price Deviation | 虚拟开盘价前收盘价前收盘价偏离大于2%信息驱动 | D_FACTOR | harvest待评估（likely_new） |  |
| CAND-HARVEST-4048 | 晚下单比例 Late Order Ratio | 9:20-9:25下单量总下单量知情交易者晚下单 | D_FACTOR | harvest待评估（likely_new） |  |
| CAND-HARVEST-4049 | 撤单率 Cancel Rate | 9:15-9:20可撤单阶段撤单比例高撤单率试探性报价 | D_FACTOR | harvest待评估（likely_new） |  |
| CAND-HARVEST-4050 | 冰山单占比 Iceberg Order Ratio | 9:20-9:25不可撤单阶段大额限价单占比隐藏真实意图 | D_FACTOR | harvest待评估（likely_new） |  |
| CAND-HARVEST-4051 | 滞后项构造 Lag Feature Construction | 因子k期滞后滚动窗口统计量因子变化率 | D_FACTOR | harvest待评估（likely_new） |  |
| CAND-HARVEST-4052 | 交互项构造 Interaction Feature Construction | 因子两两交互因子市场状态交互因子机构行为阶段交互 | D_FACTOR | harvest待评估（likely_new） |  |
| CAND-HARVEST-4053 | 分布形态统计量 Distribution Shape Statistics | 滚动收益率偏度峰度滚动VaR CVaR分布拟合度 | D_FACTOR | harvest待评估（likely_new） |  |
| CAND-HARVEST-4054 | 双存储架构 Dual Storage Architecture | 离线Parquet PIT训练回测在线Redis实时查询Feature Registry SQLite | D_FACTOR | harvest待评估（likely_new） |  |
| CAND-HARVEST-4055 | 特征注册表 Feature Registry Schema | 元数据数据血缘质量指标服务状态版本历史五表 | D_FACTOR | harvest待评估（likely_new） |  |
| CAND-HARVEST-4056 | 训练服务一致性引擎 Training Serving Consistency Engine | 单一定义原则PIT正确性版本对齐一致性引擎四重机制 | D_FACTOR | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-4057 | 特征生命周期十阶段状态机 Feature Lifecycle State Machine | 2. **PIT正确性**: 训练时get_features(as_of=...)→DuckDB AS OF JOIN仅返回computed_at≤as_of的因子值；推理时get_online_features(symbol)→Redis | D_FACTOR | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-4058 | 入池观察池 Probation Pool | 🆕 **入池观察(Probation Pool)**: 新因子IC显著但未通过Bonferroni/BH多重检验校正→进入观察池(非正式因子池)→等待更多数据积累后重新检验→通过后入池。与'衰减观察'区别：衰减观察=活跃因子IC衰退监控(退 | D_FACTOR | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-4059 | PIT一致性保证 PIT Consistency Guarantee | 因子值时间不可逆财务数据公告日约束幸存者偏差修正三条公理 | D_FACTOR | harvest待评估（likely_new） |  |
| CAND-HARVEST-4060 | 因子注册表合规 Factor Registry Compliance | 因子ID版本代码指纹参数指纹模型注册表不可变 | D_FACTOR | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-4061 | 因子血缘合规 Factor Lineage Compliance | OpenLineage标准数据血缘追踪因子血缘图 | D_FACTOR | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-4062 | 因子暴露合规 Factor Exposure Compliance | C-004持仓检查行业基准对比因子暴露监控 | D_FACTOR | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-4063 | 因子版本管理 Factor Version Management | 语义化版本号变更diff回滚需人工审核 | D_FACTOR | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-4064 | 因子退役审计 Factor Retirement Audit | 退役策略指纹入库影响分析报告下游影响通知 | D_FACTOR | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-4065 | 因子权重变更审批分级 Factor Weight Change Approval Tier | L1±5%AI自动L2±5%~20%AI自动24h人工复核 | D_FACTOR | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-4066 | 因子计算审计日志 Factor Compute Audit Log | 输入数据指纹计算参数输出值时间戳哈希链保留5年 | D_FACTOR | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-4067 | 因子数据血缘追踪 Factor Data Lineage Tracking | 原始数据源特征因子完整链路数据血缘图保留5年 | D_FACTOR | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-4068 | 因子性能审计 Factor Performance Audit | IC IR换手率衰减率持续监控记录哈希链保留3年 | D_FACTOR | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-4069 | 因子暴露审计 Factor Exposure Audit | 截面快照时序变化行业偏离记录哈希链保留5年 | D_FACTOR | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-4070 | 研究Agent Researcher Agent | / 研究Agent(Researcher) / **产出→D-FACTOR**: 发现新因子后提交提案至因子域 / 消费: D-DATA行情+D-ALT-DATA另类+D-KNOWLEDGE知识图谱 → 产出: 新因子提案+策略代码草稿 / | D_FACTOR | harvest待评估（likely_new） |  |
| CAND-HARVEST-4071 | 信号Agent Signal Gen Agent | / 信号Agent(Signal Gen) / **消费←D-FACTOR**: 读取因子值作为信号生成输入 / 消费: D-FACTOR因子值(CTR-002)+D-SIGNAL策略信号+D-ML-SERVE模型推理 → 产出: 加权信号 | D_FACTOR | harvest待评估（likely_new） |  |
| CAND-HARVEST-4921 | Causal Factor Validation Layer 因果因子验证层 | DoWhy/DML→区分相关vs因果→因果因子加权提升 | D_FACTOR | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-4922 | KAN Explainable Function Approximator KAN可解释函数逼近 | 替代QNN中MLP层参数更少 | D_FACTOR | harvest待评估（likely_new） |  |
| CAND-HARVEST-4923 | UFL Deterministic Fact Layer UFL确定性事实层 | / — / UFL确定性事实层 / FeatureStore子集，is_deterministic=True / ✅ / | D_FACTOR | harvest待评估（likely_implemented） |  |

### 一问通过（2 条）

| ID | 名称 | 大白话（干什么用） | 域 | 卡点理由 | 替代方案 |
|------|------|------|------|------|------|
| CAND-FAC-001 | Factor Cache / 因子缓存 | 因子数量增长后,每日全量重算导致计算延迟>50ms | D_FACTOR | 首次登记,待因子>10或计算延迟>50ms时重新评估 | 每次重算(当前实现)。代价:因子多时延迟增加 |
| CAND-FAC-002 | FactorMeta Pydantic Migration / FactorMeta Pydantic迁移 | FactorMeta 使用 @dataclass 违反 KBG-0040 全局 Pydantic 强制约束,与系统其余 Pydantic 数据模型不一致,序列化/校验行为不统一 | D_FACTOR | 首次登记。待 KBG-0040 强制启用或 FactorMeta 序列化出现兼容问题时晋升为 factor_base.py refactor 补丁(非新 depgraph 节点) | 维持 @dataclass。代价:违反 KBG-0040,与系统 Pydantic 统一性不一致 |

## 复查时间表

> 按 next_review_date 升序。复查时重新过一问，触发信号命中则晋升到 depgraph 设计态。

| 下次复查 | 复查频率 | ID | 名称 | 域 | 状态 | 上次复查结论 |
|------|------|------|------|------|------|------|
| 2026-11-30 | quarterly | CAND-FAC-002 | FactorMeta Pydantic Migration / FactorMeta Pydantic迁移 | D_FACTOR | 延后（deferred） | 首次登记。待 KBG-0040 强制启用或 FactorMeta 序列化出现兼容问题时晋升为 factor_base.py refactor 补丁(非新 depgraph 节点) |
| 2026-11-30 | quarterly | CAND-HARVEST-0002 | Factor Factory 因子工厂 | D_FACTOR | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-0003 | Pipeline 因子与信号生产管线 | D_FACTOR | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0214 | Engine 引擎 | D_FACTOR | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-0215 | Registry 注册表 | D_FACTOR | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0216 | Evaluation 评估器 | D_FACTOR | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-0217 | Pipeline 管线 | D_FACTOR | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0218 | Barra Risk Model 模型风险 | D_FACTOR | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0219 | A-Share Capital Flow Factor 因子 | D_FACTOR | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-0220 | A-Share Microstructure Factor 因子 | D_FACTOR | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-0221 | Alpha Factor Calculation Engine 引擎因子 | D_FACTOR | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-0375 | 模块39 多因子选股评分模型（Multi-Factor Stock Selection Scoring Model） | D_FACTOR | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0454 | L1 因子计算层 Factor Compute Layer | D_FACTOR | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-0455 | D-FACTOR Engine 因子计算引擎 | D_FACTOR | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-0456 | 声明式因子定义 YAML DSL | D_FACTOR | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0457 | incremental_compute 增量因子计算 | D_FACTOR | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0458 | consistency_check 一致性引擎 | D_FACTOR | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0486 | Volume Profile量能分布 Volume Profile | D_FACTOR | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0487 | HVN/LVN节点 High/Low Volume Node | D_FACTOR | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-0488 | Value Area 价值区域 | D_FACTOR | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0489 | POC Point of Control 控制点 | D_FACTOR | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0490 | CVD买卖压力追踪 Cumulative Volume Delta | D_FACTOR | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0491 | VPIN 知情交易概率 VPIN | D_FACTOR | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0497 | IRCF因子 Institutional Retail Contrarian Flow | D_FACTOR | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-0498 | OFI检测框架 Order Flow Imbalance | D_FACTOR | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-0499 | Lee-Ready算法 Lee-Ready Algorithm | D_FACTOR | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0500 | BVC方法 Bulk Volume Classification | D_FACTOR | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0505 | 统一技术图形识别引擎 Unified Technical Pattern Recognition Engine | D_FACTOR | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-0506 | 图形模式库 Pattern Library | D_FACTOR | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0507 | 统一识别算法 Unified Recognition Algorithm | D_FACTOR | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0508 | 多时间级别识别 Multi-Timeframe Recognition | D_FACTOR | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-0555 | 特征存储双存储架构 Feature Store Dual-Storage | D_FACTOR | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0556 | 离线存储 Offline Store | D_FACTOR | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0557 | 在线存储 Online Store | D_FACTOR | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0558 | 特征注册表 Feature Registry | D_FACTOR | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0559 | 训练-服务一致性保证 Training-Serving Consistency | D_FACTOR | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0560 | 特征生命周期 Feature Lifecycle | D_FACTOR | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-0561 | Governance 因子治理 | D_FACTOR | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-0562 | DecayMonitor 因子衰减监控 | D_FACTOR | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-0582 | 一致性引擎 Consistency Engine | D_FACTOR | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-0583 | 实时特征计算管道 Real-time Feature Pipeline | D_FACTOR | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0684 | Factor Orthogonalizer 因子正交化器 | D_FACTOR | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-0994 | Factor Exposure Calculator 因子暴露计算器 | D_FACTOR | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-0995 | Factor Risk Budget Allocator 因子风险预算分配器 | D_FACTOR | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1340 | Factor Correlation Analyzer 因子相关性分析器 | D_FACTOR | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1341 | Factor Turnover Analyzer 因子换手率分析器 | D_FACTOR | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1342 | Causal Validator 因果验证器 | D_FACTOR | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1343 | ESG ESG因子 | D_FACTOR | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1344 | Fundamental 基本面因子 | D_FACTOR | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1345 | Intraday 日内因子 | D_FACTOR | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1346 | Factor Dependency Graph DAG 因子依赖图DAG | D_FACTOR | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1347 | Grayscale Rollout 灰度发布 | D_FACTOR | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1348 | SMC SMC因子 | D_FACTOR | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1349 | IRL IRL因子 | D_FACTOR | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1350 | Backpressure 背压控制 | D_FACTOR | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1351 | 6-Step Flow 6步流程 | D_FACTOR | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1352 | Lifecycle State Machine 生命周期状态机 | D_FACTOR | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1353 | IC/IR Evaluator IC/IR评估器 | D_FACTOR | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1354 | CTR-001 Consumer CTR-001消费者 | D_FACTOR | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1355 | CTR-002/003 Producer CTR-002/003生产者 | D_FACTOR | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1356 | Batch Output 批量输出 | D_FACTOR | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1357 | Multi-Factor Synthesis Validator 多因子合成验证器 | D_FACTOR | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1358 | 3-Level Judgment 三级判断 | D_FACTOR | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1359 | IC Decay Analyzer IC衰减分析器 | D_FACTOR | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1360 | IC_IR Calculator IC_IR计算器 | D_FACTOR | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1361 | 87-Alpha 87-Alpha因子 | D_FACTOR | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1362 | Technical Indicator Factor 技术指标因子 | D_FACTOR | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1363 | Pattern to Signal Converter 形态信号转化器 | D_FACTOR | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1364 | Market Structure Factor 市场结构因子 | D_FACTOR | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1365 | Sector Factor 板块因子 | D_FACTOR | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1366 | Institutional Behavior Factor 机构行为因子 | D_FACTOR | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1367 | Layered Backtest 分层回测 | D_FACTOR | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1368 | Cross-Market Factor 跨市场因子 | D_FACTOR | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1369 | Parameter Config Manager 参数配置管理器 | D_FACTOR | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1370 | Factor Dependency DAG Manager 因子依赖DAG管理器 | D_FACTOR | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1371 | Distribution Feature Engineering 分布特征工程 | D_FACTOR | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1372 | Pastor-Stambaugh Liquidity Factor Pastor-Stambaugh流动性因子 | D_FACTOR | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1373 | Correlation Redundancy Remover 相关性去冗余 | D_FACTOR | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1374 | Factor Portfolio Optimizer 因子组合优化器 | D_FACTOR | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1375 | Factor Attribution 因子归因 | D_FACTOR | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1782 | Timing Engine 择时引擎 | D_FACTOR | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-2252 | IC Decay Detection IC衰减检测 | D_FACTOR | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-2253 | Crowding Detection 拥挤度检测 | D_FACTOR | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2260 | D-FACTOR-04 Pipeline D-FACTOR-04管道 | D_FACTOR | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-3634 | Overnight Global Market Contagion Model 隔夜全球市场传导模型 | D_FACTOR | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3635 | Global Market Contagion Quantification 全球市场传导量化 | D_FACTOR | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3636 | Event Impact Assessment 事件影响评估 | D_FACTOR | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3637 | Northbound Capital Flow Model 北向资金流向模型 | D_FACTOR | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-3638 | Northbound Capital Signal 北向资金信号 | D_FACTOR | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3708 | Feature Serving API 特征服务API | D_FACTOR | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3724 | D-FACTOR Engine 因子引擎 | D_FACTOR | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-3886 | 因子计算 增量因子计算 Factor Incremental | D_FACTOR | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-3957 | CTR-001 Consumer 契约消费者 | D_FACTOR | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-3958 | CTR-002/003 Producer 契约生产者 | D_FACTOR | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-3959 | Backpressure 背压 | D_FACTOR | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3960 | 因子依赖图DAG Factor Dependency DAG | D_FACTOR | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-3961 | 参数配置管理器 Parameter Config Manager | D_FACTOR | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-3962 | 因子依赖DAG管理器 Factor Dependency DAG Manager | D_FACTOR | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-3963 | Capital Flow 资金流 | D_FACTOR | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-3964 | Microstructure 微观结构 | D_FACTOR | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3965 | Fundamental 基本面 | D_FACTOR | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3966 | Intraday 日内 | D_FACTOR | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3967 | SMC Smart Money Concept SMC聪明钱概念 | D_FACTOR | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3968 | IRL 机构行为识别 | D_FACTOR | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3969 | Alpha Factor Alpha因子 | D_FACTOR | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-3970 | 87-Alpha 87Alpha因子 | D_FACTOR | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3971 | 技术指标因子 Technical Indicator Factor | D_FACTOR | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-3972 | 形态到信号转化 Pattern to Signal | D_FACTOR | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3973 | Pastor-Stambaugh Liquidity Factor PS流动性因子 | D_FACTOR | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-3974 | IC_IR计算 IC_IR Calculator | D_FACTOR | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3975 | IC衰减分析器 IC Decay Analyzer | D_FACTOR | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-3976 | 多因子合成验证器 Multi-Factor Synthesis Validator | D_FACTOR | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-3977 | 相关性去冗余 Correlation Redundancy Remover | D_FACTOR | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-3978 | 因子组合优化 Factor Portfolio Optimizer | D_FACTOR | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-3979 | Timing Engine 时机引擎 | D_FACTOR | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-3980 | 量价因子 Price-Volume Factor | D_FACTOR | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-3981 | 波动率因子 Volatility Factor | D_FACTOR | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-3982 | 成交量因子 Volume Factor | D_FACTOR | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-3983 | 市场结构因子 Market Structure Factor | D_FACTOR | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-3984 | 基本面因子 Fundamental Factor | D_FACTOR | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-3985 | Alpha因子 Alpha Factor | D_FACTOR | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-3986 | 板块风格因子 Sector Style Factor | D_FACTOR | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-3987 | 主力行为因子 Institutional Behavior Factor | D_FACTOR | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-3988 | 另类因子 Alternative Factor | D_FACTOR | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-3989 | 宏观因子 Macro Factor | D_FACTOR | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-3990 | 跨市场因子 Cross-Market Factor | D_FACTOR | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-3991 | 风险因子 Risk Factor | D_FACTOR | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-3992 | 统一图形识别引擎 Unified Pattern Recognition Engine | D_FACTOR | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-4004 | 一高七矮 Volume Profile HVN LVN | D_FACTOR | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4005 | 量能体制分类 Volume Regime Classification | D_FACTOR | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4006 | 突破回踩动量因子 Breakout-Retest Momentum Factor | D_FACTOR | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-4007 | 体制条件因子有效性 Regime-Conditional Factor Effectiveness | D_FACTOR | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-4008 | 逆向资金买点 Contrarian Capital Flow Factor | D_FACTOR | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-4009 | 主力吸筹 Accumulation Factor | D_FACTOR | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-4010 | 主力派发 Distribution Factor | D_FACTOR | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-4011 | 主力洗盘 Shakeout Factor | D_FACTOR | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-4012 | 缠论图形识别 Statistical Consolidation Zone | D_FACTOR | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4013 | 支撑阻力位检测 Support Resistance Level Detection | D_FACTOR | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-4014 | 图表形态识别 Chart Pattern Recognition | D_FACTOR | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4015 | 冰山单检测 Hidden Order Detection Factor | D_FACTOR | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-4016 | 开盘缺口因子 Opening Gap Factor | D_FACTOR | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-4017 | 抗跌因子 Downside Resistance Factor | D_FACTOR | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-4018 | 逆涨因子 Contrarian Return Factor | D_FACTOR | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-4019 | 晚下单因子 Late Order Arrival Factor | D_FACTOR | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-4020 | 体制条件因子衰减 Regime-Conditional Factor Decay | D_FACTOR | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-4021 | 庄家行为模式识别 Market Manipulation Pattern Detection | D_FACTOR | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4022 | 群体博弈模拟 Game-Theoretic Agent Simulation | D_FACTOR | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4023 | 筹码集中度 Ownership Concentration Factor | D_FACTOR | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-4024 | 出货信号因子 Distribution Signal Factor | D_FACTOR | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-4025 | 吸筹出货期检测 Accumulation Distribution Phase Detection | D_FACTOR | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4026 | IC因子替换 IC-Based Factor Replacement | D_FACTOR | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-4027 | 批量因子裁剪 Batch Factor Pruning | D_FACTOR | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-4028 | 主力净流入 Institutional Net Inflow Factor | D_FACTOR | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-4029 | 龙虎榜机构占比 Dragon-Tiger List Institutional Ratio | D_FACTOR | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4030 | 北向持仓变化 Northbound Holding Change Factor | D_FACTOR | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-4031 | 板块强度 Sector Strength Factor | D_FACTOR | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-4032 | 传导系数 Cross-Market Transmission Coefficient | D_FACTOR | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4033 | 封单率 Limit Order Fill Rate Factor | D_FACTOR | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-4034 | 市场宽度因子 Market Breadth Factors | D_FACTOR | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4035 | HVN/LVN节点 Volume Profile HVN LVN | D_FACTOR | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4036 | POC 公允价值核心 Point of Control | D_FACTOR | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4037 | CVD 累积买卖压力 Cumulative Volume Delta | D_FACTOR | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4038 | CVD价格背离 CVD Price Divergence | D_FACTOR | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4039 | 大盘下跌状态检测 Market Down State Detection | D_FACTOR | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-4040 | 下跌强度分级 Down Strength Classification | D_FACTOR | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4041 | 逆势强度比 Contrarian Strength Ratio | D_FACTOR | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4042 | 逆势持续性 Contrarian Persistence | D_FACTOR | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4043 | 逆势个股排行 Contrarian Stock Ranking | D_FACTOR | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4044 | 虚拟开盘价轨迹 Virtual Open Price Trajectory | D_FACTOR | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4045 | 虚拟匹配量 Virtual Match Volume | D_FACTOR | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4046 | 订单不平衡 Order Imbalance | D_FACTOR | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4047 | 价格偏离度 Price Deviation | D_FACTOR | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4048 | 晚下单比例 Late Order Ratio | D_FACTOR | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4049 | 撤单率 Cancel Rate | D_FACTOR | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4050 | 冰山单占比 Iceberg Order Ratio | D_FACTOR | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4051 | 滞后项构造 Lag Feature Construction | D_FACTOR | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4052 | 交互项构造 Interaction Feature Construction | D_FACTOR | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4053 | 分布形态统计量 Distribution Shape Statistics | D_FACTOR | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4054 | 双存储架构 Dual Storage Architecture | D_FACTOR | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4055 | 特征注册表 Feature Registry Schema | D_FACTOR | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4056 | 训练服务一致性引擎 Training Serving Consistency Engine | D_FACTOR | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-4057 | 特征生命周期十阶段状态机 Feature Lifecycle State Machine | D_FACTOR | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-4058 | 入池观察池 Probation Pool | D_FACTOR | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-4059 | PIT一致性保证 PIT Consistency Guarantee | D_FACTOR | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4060 | 因子注册表合规 Factor Registry Compliance | D_FACTOR | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-4061 | 因子血缘合规 Factor Lineage Compliance | D_FACTOR | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-4062 | 因子暴露合规 Factor Exposure Compliance | D_FACTOR | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-4063 | 因子版本管理 Factor Version Management | D_FACTOR | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-4064 | 因子退役审计 Factor Retirement Audit | D_FACTOR | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-4065 | 因子权重变更审批分级 Factor Weight Change Approval Tier | D_FACTOR | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-4066 | 因子计算审计日志 Factor Compute Audit Log | D_FACTOR | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-4067 | 因子数据血缘追踪 Factor Data Lineage Tracking | D_FACTOR | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-4068 | 因子性能审计 Factor Performance Audit | D_FACTOR | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-4069 | 因子暴露审计 Factor Exposure Audit | D_FACTOR | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-4070 | 研究Agent Researcher Agent | D_FACTOR | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4071 | 信号Agent Signal Gen Agent | D_FACTOR | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4921 | Causal Factor Validation Layer 因果因子验证层 | D_FACTOR | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-4922 | KAN Explainable Function Approximator KAN可解释函数逼近 | D_FACTOR | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4923 | UFL Deterministic Fact Layer UFL确定性事实层 | D_FACTOR | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2027-07-31 | yearly | CAND-FAC-001 | Factor Cache / 因子缓存 | D_FACTOR | 延后（deferred） | 首次登记,待因子>10或计算延迟>50ms时重新评估 |
