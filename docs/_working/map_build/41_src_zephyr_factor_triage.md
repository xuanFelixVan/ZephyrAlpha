---
ttl: task_bound
completes_when: 孤儿分诊战役终裁落地（chief 终审+处置执行）后本册随 30/31 号转归档
title: 孤儿分诊证据包：src.zephyr.factor（38 台）
owner: st-orphtriage-20261004
---

# 41 号·分诊证据包：src.zephyr.factor（38 台）

> 宇宙口径=裁定#481；数据真源=30_attribution_table.yaml（join checker 机生）；处置=证据班建议，终裁归 GLM-5.3 chief，退役执行归 Owner 门位。
>
> tier 分布：suspect_orphan=4，wired=25，wired_by_header=9；初判汇总：dispute=4，mount=34

## 逐台证据（四字段+初判）

| file | 干什么的 | last_commit（距今） | import 信号 | 初判建议 |
|---|---|---|---|---|
| `src/zephyr/factor/_extensions/__init__.py` | factor/_extensions | 2026-09-15（19天） | in=0/out=0·suspect_orphan | **dispute**（suspect_orphan 但 19 天内有 commit（活着但零线零引）；①mount→FACTORY（策略工厂） ②retire→Owner 门位） |
| `src/zephyr/factor/api/__init__.py` | factor/api | 2026-09-15（19天） | in=0/out=0·suspect_orphan | **dispute**（suspect_orphan 但 19 天内有 commit（活着但零线零引）；①mount→FACTORY（策略工厂） ②retire→Owner 门位） |
| `src/zephyr/factor/infrastructure/__init__.py` | factor/infrastructure | 2026-09-15（19天） | in=0/out=0·suspect_orphan | **dispute**（suspect_orphan 但 19 天内有 commit（活着但零线零引）；①mount→FACTORY（策略工厂） ②retire→Owner 门位） |
| `src/zephyr/factor/services/__init__.py` | factor/services | 2026-09-15（19天） | in=0/out=0·suspect_orphan | **dispute**（suspect_orphan 但 19 天内有 commit（活着但零线零引）；①mount→FACTORY（策略工厂） ②retire→Owner 门位） |
| `src/zephyr/factor/analysis/bhy_fdr.py` | D_FACTOR — BHY FDR 多重检验校正（90 号 Phase2 项，#2 因子IC 双轨采纳） | 2026-09-18（16天） | in=6/out=0·wired | **mount**→FACTORY（策略工厂）（活线在身未挂线） |
| `src/zephyr/factor/analysis/correlation_analyzer.py` | D-FACTOR-ANA-04 因子相关性分析——计算因子间相关性矩阵。 | 2026-09-15（19天） | in=1/out=0·wired | **mount**→FACTORY（策略工厂）（活线在身未挂线） |
| `src/zephyr/factor/analysis/correlation_block_bootstrap.py` | D_FACTOR — G07 multivariate stationary block-bootstrap 引擎（23 号 memo §3.2） | 2026-09-17（17天） | in=1/out=0·wired | **mount**→FACTORY（策略工厂）（活线在身未挂线） |
| `src/zephyr/factor/analysis/correlation_dedup.py` | D-FACTOR-ANA-05 因子相关性去重——基于相关性矩阵去除冗余因子。 | 2026-09-15（19天） | in=0/out=0·wired_by_header | **mount**→FACTORY（策略工厂）（活线在身未挂线） |
| `src/zephyr/factor/analysis/correlation_drift_monitor.py` | D_FACTOR — G07 §5.4 相关性漂移监控（上线后持续，函数级） | 2026-09-17（17天） | in=1/out=0·wired | **mount**→FACTORY（策略工厂）（活线在身未挂线） |
| `src/zephyr/factor/analysis/correlation_neff.py` | D_FACTOR — G07 组合层有效下注数 Neff 引擎（23 号 memo §3.1⑤） | 2026-09-17（17天） | in=1/out=0·wired | **mount**→FACTORY（策略工厂）（活线在身未挂线） |
| `src/zephyr/factor/analysis/correlation_overfitting_audit.py` | D_FACTOR — G07 过拟合检测引擎（23 号 memo §3.3，PDR/PSI/DFR 自实现核心） | 2026-09-17（17天） | in=1/out=0·wired | **mount**→FACTORY（策略工厂）（活线在身未挂线） |
| `src/zephyr/factor/analysis/correlation_preprocessing.py` | D_FACTOR — G07 策略相关性验证·数据预处理 pipeline（23 号 memo §3.1①） | 2026-09-17（17天） | in=1/out=0·wired | **mount**→FACTORY（策略工厂）（活线在身未挂线） |
| `src/zephyr/factor/analysis/correlation_sentiment_stratifier.py` | D_FACTOR — G07 情绪周期分层标签器（23 号 memo §3.1②，消费 BM-SEL-23-B） | 2026-09-17（17天） | in=1/out=0·wired | **mount**→FACTORY（策略工厂）（活线在身未挂线） |
| `src/zephyr/factor/analysis/factor_similarity_cluster.py` | 因子相似度聚类器（GAP-F-38，factor/analysis 子包）。 | 2026-09-02（32天） | in=0/out=0·wired_by_header | **mount**→FACTORY（策略工厂）（活线在身未挂线） |
| `src/zephyr/factor/bus_factor_defense.py` | 向后兼容别名（原 check_bus_factor 重命名为 evaluate_bus_factor） | 2026-09-15（19天） | in=2/out=0·wired | **mount**→FACTORY（策略工厂）（活线在身未挂线） |
| `src/zephyr/factor/core/backpressure/__init__.py` | D_FACTOR core backpressure 子包——进程内在途并发限流器。 | 2026-09-15（19天） | in=0/out=0·wired_by_header | **mount**→FACTORY（策略工厂）（活线在身未挂线） |
| `src/zephyr/factor/core/backpressure/limiter.py` | D_FACTOR core backpressure.limiter——进程内在途并发限流器。 | 2026-09-15（19天） | in=3/out=0·wired | **mount**→FACTORY（策略工厂）（活线在身未挂线） |
| `src/zephyr/factor/core/config_manager/__init__.py` | D_FACTOR core config_manager 子包——core 基础设施模块策略参数加载器。 | 2026-09-15（19天） | in=0/out=0·wired_by_header | **mount**→FACTORY（策略工厂）（活线在身未挂线） |
| `src/zephyr/factor/core/config_manager/loader.py` | D_FACTOR core config_manager 加载器——加载 core/_config.yaml 策略参数。 | 2026-09-15（19天） | in=5/out=0·wired | **mount**→FACTORY（策略工厂）（活线在身未挂线） |
| `src/zephyr/factor/core/ctr001_consumer/__init__.py` | CTR-001 NormalizedMarketData 消费者包入口。 | 2026-09-15（19天） | in=0/out=0·wired_by_header | **mount**→FACTORY（策略工厂）（活线在身未挂线） |
| `src/zephyr/factor/core/ctr001_consumer/converter.py` | CTR-001 NormalizedMarketData 消费者——数据适配层。 | 2026-09-15（19天） | in=1/out=0·wired | **mount**→FACTORY（策略工厂）（活线在身未挂线） |
| `src/zephyr/factor/core/ctr002_producer/__init__.py` | CTR-002 FactorSignal 生产者包入口。 | 2026-09-15（19天） | in=0/out=0·wired_by_header | **mount**→FACTORY（策略工厂）（活线在身未挂线） |
| `src/zephyr/factor/core/ctr002_producer/converter.py` | CTR-002 FactorSignal 生产者——信号适配层。 | 2026-09-15（19天） | in=1/out=0·wired | **mount**→FACTORY（策略工厂）（活线在身未挂线） |
| `src/zephyr/factor/core/distribution_feature_engineer.py` | 分布特征工程器（MOD-L02-026，D_FACTOR core）。 | 2026-09-17（17天） | in=0/out=0·wired_by_header | **mount**→FACTORY（策略工厂）（活线在身未挂线） |
| `src/zephyr/factor/core/evaluation/metrics.py` | D-FACTOR-03 因子评估指标——纯函数模块（无 IO 依赖）。 | 2026-09-15（19天） | in=4/out=0·wired | **mount**→FACTORY（策略工厂）（活线在身未挂线） |
| `src/zephyr/factor/expectations.py` | expectations — 分析师一致预期因子族（消费端 C2 预备，2026-09-12）。 | 2026-09-14（20天） | in=2/out=0·wired | **mount**→FACTORY（策略工厂）（活线在身未挂线） |
| `src/zephyr/factor/fundamentals.py` | fundamentals — 财报事实侧因子族（消费端 F2，2026-09-14）。 | 2026-09-14（20天） | in=3/out=0·wired | **mount**→FACTORY（策略工厂）（活线在身未挂线） |
| `src/zephyr/factor/governance/__init__.py` | D_FACTOR governance 子包——因子生命周期治理工具链。 | 2026-09-15（19天） | in=4/out=0·wired | **mount**→FACTORY（策略工厂）（活线在身未挂线） |
| `src/zephyr/factor/governance/factor_pool_manager.py` | D-FACTOR-08 因子池容量管理——活跃池/休眠池 + IC末位淘汰 + 批量裁剪。 | 2026-09-15（19天） | in=0/out=0·wired_by_header | **mount**→FACTORY（策略工厂）（活线在身未挂线） |
| `src/zephyr/factor/technical_indicators/chips.py` | 筹码族技术指标（3 个，批10 施工 2026-09-21）。 | 2026-09-22（12天） | in=2/out=0·wired | **mount**→FACTORY（策略工厂）（活线在身未挂线） |
| `src/zephyr/factor/technical_indicators/cycle.py` | 循环族技术指标（8 个指标/11 输出列；HT 五件套 2026-09-14 批 3 新建， | 2026-09-20（14天） | in=0/out=0·wired_by_header | **mount**→FACTORY（策略工厂）（活线在身未挂线） |
| `src/zephyr/factor/technical_indicators/indicator_base.py` | 技术指标基类与注册表（#ARCH-DATA-TI-001，骨架先行 2026-08-10）。 | 2026-09-15（19天） | in=11/out=0·wired | **mount**→FACTORY（策略工厂）（活线在身未挂线） |
| `src/zephyr/factor/technical_indicators/momentum.py` | 动量类技术指标（43 个；2026-09-14 A股标配批+3、批2a +1、批2b +8、批6 +9；2026-09-20 批7 清欠 +6：RMI/PFE/FOSC/CTI/VHF/ER）。 | 2026-10-01（3天） | in=2/out=0·wired | **mount**→FACTORY（策略工厂）（活线在身未挂线） |
| `src/zephyr/factor/technical_indicators/reversal.py` | 反转类技术指标（4 个，v1.0.0 全部施工完成；原第 5 件 CandlestickPattern 已按裁定#233 退役）。 | 2026-09-21（13天） | in=1/out=0·wired | **mount**→FACTORY（策略工厂）（活线在身未挂线） |
| `src/zephyr/factor/technical_indicators/statistics.py` | 统计族技术指标（9 个指标/10 输出列，2026-09-14 统计族批新建，2026-09-20 回归扩展批 | 2026-10-01（3天） | in=2/out=0·wired | **mount**→FACTORY（策略工厂）（活线在身未挂线） |
| `src/zephyr/factor/technical_indicators/trend.py` | 趋势类技术指标（38 个；2026-09-14 A股标配批+1、批2a +5、批2b +1、批3 +1 Ichimoku[复合类]、批6 +1 BBI、 | 2026-10-01（3天） | in=5/out=0·wired | **mount**→FACTORY（策略工厂）（活线在身未挂线） |
| `src/zephyr/factor/technical_indicators/volatility.py` | 波动类技术指标（18 个，v1.0.0 全部施工完成）。 | 2026-10-01（3天） | in=2/out=0·wired | **mount**→FACTORY（策略工厂）（活线在身未挂线） |
| `src/zephyr/factor/technical_indicators/volume.py` | 成交量类技术指标（17 个，v1.0.0 全部施工完成）。 | 2026-10-01（3天） | in=1/out=0·wired | **mount**→FACTORY（策略工厂）（活线在身未挂线） |
