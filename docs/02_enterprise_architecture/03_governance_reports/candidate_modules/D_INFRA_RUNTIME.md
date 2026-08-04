---
doc_type: audit_report
title: 候选模块清单 — D_INFRA_RUNTIME
version: "1.0"
status: active
date: auto-generated
owner: auto-generator
ttl: permanent
---

# D_INFRA_RUNTIME 候选模块清单

> [← 返回索引](index.md)

> 本域候选 **349** 条（原有 1 + harvest 348）。
> harvest 去重四态: likely_new=52 / likely_implemented=225 / likely_misplaced=71

## 完整清单

| ID | 名称 / Name | 大白话（干什么用） | 域 | 状态 | 一问卡点 | 优先级 | 触发信号摘要 | 下次复查 |
|------|------|------|------|------|------|:---:|------|------|
| CAND-HARVEST-0094 | Rebalance Scheduler再平衡调度器 | / PC-03 / Rebalance Scheduler再平衡调度器 / ✅ 能建 / / 阈值+日历+事件触发+税收感知+成本感知 / | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0225 | Signal Audit Logger 信号审计 | / D-SIGNAL-06 / Signal Audit Logger / ✅ / / 信号审计日志+WORM写入 / | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0276 | Audit Trail 审计追踪 | / D-AUTONOMY-02 / Audit Trail / ✅ 能建 / 📋 项目内有蓝图编号MOD-INF-020已建设 / Merkle哈希链+Agent签名 / | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0288 | High Performance HA Framework 高性能高可用保障框架 | / D-INFRA-46 / 高性能高可用保障框架 / ✅ 能建 / / SLA保障+故障自动切换+健康检查 / | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0611 | Database Layer 数据库层 | SQLite+DuckDB+PostgreSQL统一存储抽象 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0630 | 数据库管理器 Database Manager (16分片SQLite) | 16分片SQLite读写路由+分片策略+连接池 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0631 | 跨域事件总线 Cross-domain Event Bus | 跨域事件发布订阅+事件路由分发+事件持久化 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0632 | 缓存一致性管理器 Cache Consistency Manager | 多层缓存一致性维护+缓存失效策略+版本控制 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0633 | 数据质量监控器 Data Quality Monitor | 数据管线质量指标监控+数据异常与漂移检测 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0634 | 数据血缘追踪器 Data Lineage Tracker | 数据从源头到消费端完整路径与转换历史追踪 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0635 | 数据完整性校验器 Data Integrity Validator | 端到端数据完整性+哈希验证+Merkle树一致性检查 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0636 | 数据字段Schema版本管理器 Data Field Schema Version Manager | 数据字段定义Schema版本管理+迁移脚本生成 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0637 | 数据验证规则引擎 Data Validation Rule Engine | 声明式规则数据验证+组合规则+自定义校验器 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0805 | Auto Backtest Scheduler 自动回测调度器 | 自动回测调度器参数网格批量回测vectorbt向量化回测队列管理回测结果聚合 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0844 | 集成测试任务 Integration Task | 各模块集成测试的任务分解和时间估算 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0859 | Audit Trail 审计链 | 审计链操作日志+决策日志+变更日志+不可篡改+哈希链验证 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0860 | Process Manager 进程管理器 | 进程管理器NSSM+5进程P1~P5优先级+进程监控+进程重启+进程日志 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0861 | Redis Manager Redis管理器 | Redis管理器13命名空间+连接池+集群管理+持久化+内存策略 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0862 | GPU Scheduler GPU调度器 | GPU调度器CUDA设备管理+显存分区+时段优先调度+模型热交换+OOM防护 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0863 | ConfigManager 配置管理器 | / IF-INFRA-002 / D-INFRA-RUNTIME / `ConfigManager` / 软(E-0007) / 安全策略配置热更新 / | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0864 | Service Registry 服务注册表 | 服务注册表服务发现+健康检查+负载均衡+服务元数据 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0865 | Message Queue 消息队列 | 消息队列Redis Streams+发布订阅+消息持久化+消费者组+死信队列 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0895 | EventBus 事件总线 | / IF-INFRA-001 / D-INFRA-RUNTIME / `EventBus` / 软(E-0007) / 跨域事件发布/订阅 / | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0896 | Config Center 配置中心 | 配置中心YAML配置+环境变量+配置热更新+配置版本+配置校验+配置审计 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0897 | Health Checker 健康检查器 | 健康检查器存活检查+就绪检查+启动检查+健康报告+健康聚合 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0898 | Metrics Collector 指标采集器 | 指标采集器Prometheus格式+自定义指标+指标聚合+指标导出+指标查询 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0899 | Logger 日志器 | 日志器结构化日志+日志级别+日志路由+日志聚合+日志脱敏 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0900 | Retry & Circuit Breaker 重试与熔断器 | 重试与熔断器指数退避重试+熔断器状态机+舱壁隔离+超时控制+降级策略 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0901 | Task Scheduler 任务调度器 | 任务调度器定时任务+周期任务+一次性任务+任务依赖+任务重试+任务审计 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0902 | 审计系统 Audit System | 操作日志+决策日志+不可篡改+哈希链验证 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0907 | Runtime 运行时 | 运行时(进程管理+配置管理+服务注册+消息队列) | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0991 | Inference Circuit Breaker 推理熔断器 | 推理异常+熔断+降级+恢复 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1056 | MCP Gateway Rate-Limit Audit Manager MCP网关限流审计管理器 | 10QPS限流+审计+熔断降级 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1058 | Immutable Audit Log Writer 不可变审计日志写入器 | 不可变审计日志+哈希链+验证 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1059 | TaskCard Six-Dimension Anti-Drift Validator TaskCard六维防漂移校验器 | 31字段+六维漂移检测 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1060 | Audit-Persistence Dual-Write Coordinator 审计-持久化双写协调器 | 审计日志+任务状态双写一致性 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1130 | SystemHealthVisualization 系统健康可视化 | 系统健康可视化+三平面状态展示 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1166 | Service Degradation Manager 服务降级管理器 | 管理服务降级策略，在过载时自动切降非核心功能保障核心链路 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1167 | Connection Pool Manager 连接池管理器 | 管理数据库/缓存/消息队列等连接池的大小、超时与泄漏检测 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1170 | Failover Coordinator 故障转移协调器 | 协调服务故障检测、主备切换与故障恢复流程编排 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1230 | Risk Check Dependency Short-Circuit Evaluator 风控检查依赖短路评估器 | 风控检查依赖短路评估器 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1243 | Vector Index Health Monitor 向量索引健康监控器 | 索引健康监控+向量索引损坏检测/索引修复+索引性能监控 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1246 | Core Chain E2E Health Monitor 核心链路端到端健康监控器 | TaskCard→Gate→Pipeline→Security→Audit→Feedback核心链路监控 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1247 | Code Health Assessor 代码健康度评估器 | 1714文件/160315行/238TODO/184未实现等代码质量指标+健康评分 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1252 | System Health Five-Star Scorer 系统健康度五星评分器 | 架构设计/代码质量/必要功能比例/过度工程程度/AI可维护性5维度评分 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1258 | M10 Audit Report Finding Format Generator M10审计报告Finding格式生成器 | M10生成Finding格式报告+报告模板+报告数据填充+报告分发 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1290 | PERM Independent Health Checker PERM独立健康检查器 | 独立于CORE的健康检查，CORE崩溃时PERM仍可检测 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1291 | Trading Session Aware Ops Scheduler 交易时段感知运维调度器 | 交易时段仅监控+告警，修复延至盘后 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1335 | Financial Time Series Data Augmentation 金融时序数据增强 | TimeGAN/QuantGAN生成合成序列+条件扩散模型+时间扭曲/幅度缩放 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1417 | Multi-Process Isolation & Runtime Architecture 多进程隔离与运行时架构 | GPU分时调度隔离+共享内存零拷贝 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1418 | Model Registry & Experiment Management 模型注册与实验管理 | MLflow Model Registry追踪版本/指标/部署状态/退化+Experiment Tracking | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1419 | Time-Series Database & Tiered Storage 时序数据库与分层存储架构 | 4元组数据映射模型+DuckDB+Parquet三层Hot/Warm/Cold存储 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1420 | Feature Drift & Concept Drift Detection 特征漂移与概念漂移检测 | 特征漂移PSI/KL散度+概念漂移ADWIN/DDM/EDDM+标签漂移滚动KS | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1421 | Graph Neural Network for Stock Relations 图神经网络用于股票关系建模 | RGCN多关系图+TGN时变图+GAT注意力+6类知识图谱边 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1422 | Transformer Time-Series Architecture Transformer时序架构 | Informer+PatchTST+TimesNet+iTransformer→密度预测Phase2/3增强 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1423 | Signature Methods 签名方法 | Rough Path Theory迭代积分→自动提取任意高阶路径依赖+Log-signature降维 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1424 | Reinforcement Learning for Portfolio & Execution 强化学习用于组合优化与订单执行 | RL组合优化(PPO/SAC)+RL最优执行(DQN/PPO)+RL做T策略+6条安全约束 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1425 | LLM Agent for Fundamental Analysis 大语言模型Agent用于基本面分析 | 多Agent架构(财报Agent+新闻Agent+综合Agent)+本地Qwen2.5-7B/14B量化版 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1426 | Alternative Data Source Expansion 另类数据源扩展 | 社交媒体情绪+上市公司数字足迹+产业链供应链+卫星遥感 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1427 | Market Microstructure Deep Modeling 市场微观结构深度建模 | VPIN订单流毒性检测+LOB限价订单簿动力学+做市商行为推断 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1428 | Conformal Prediction 共形预测 | 分布无关收益预测区间+自适应共形ACI/EnbPI+在线VaR校准 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1429 | Survival Analysis 生存分析 | Cox比例风险模型→止盈/止损时间预测+市场状态持续时间预测 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1430 | Causal ML 深度补充 因果ML深度补充 | DML因子因果效应估计+Causal Forest+DoWhy反事实推演+因果发现 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1431 | Learning System Bridge Declaration 学习系统桥接声明 | 知识注入9条路径+反馈4条路径+6条全局约束→流水线从被动执行走向自我成长 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1432 | Mamba/SSM State Space Model Mamba/SSM状态空间模型 | 选择性扫描机制S6+O(L)线性复杂度+Prob-Mamba概率SSM+CMDMamba双层 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1434 | Time-Series Conformal Prediction Enhancement TCP/DDCI/CP-VaR 时序保形预测增强 | 已合并至§29.16第5小节；TCP-RM残差记忆+DDCI双反馈+CP-VaR等价回测 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1435 | A-Share Diffusion Model Data Augmentation A股扩散模型数据增强 | FWT检索增强扩散+GBM-Diffusion乘性噪声+InterDiff分类器无关引导 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1448 | Alternative Data Source Health & Degradation Manager 另类数据源健康度与降级管理器 | 另类数据源健康度监控+降级策略+自动切换 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1449 | Hardware Accelerator 硬件加速器 | GPU/TPU/FPGA等异构硬件加速资源的统一管理、分配与性能监控 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1450 | GPU Compute Pipeline Manager GPU计算管线管理器 | 管理GPU计算管线的任务调度、执行流编排与流水线并行优化 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1451 | GPU Memory Transfer Optimizer GPU内存传输优化器 | 优化GPU与主机间数据传输效率、内存拷贝合并与异步传输策略 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1452 | GPU Programming Abstraction Layer GPU编程抽象层 | 提供统一的GPU编程接口抽象，屏蔽底层硬件差异与驱动版本变更 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1453 | GPU Resource Monitor GPU资源监控器 | 实时监控GPU资源使用率、显存占用、温度与功耗，触发阈值告警 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1454 | GPU Inference Training Dynamic Allocator GPU推理训练动态分配器 | 动态分配GPU计算资源以平衡推理延迟敏感型与训练吞吐密集型工作负载 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1455 | GPU Kernel Launch Optimizer GPU内核启动优化器 | 优化GPU内核启动参数配置、内核融合策略与执行网格分块方案 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1456 | CPU Core Allocation Manager CPU核心分配管理器 | 管理CPU核心的亲和性绑定、核心隔离与动态分配调度策略 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1457 | Single-Machine Concurrency Mode Optimizer 单机并发模式优化器 | 并发模式选择/并发度优化/资源争抢避免+并发性能监控 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1458 | Inter-Process Communication Manager 进程间通信管理器 | 管理进程间通信通道的建立、消息序列化与通信性能监控 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1459 | Thread Pool Manager 线程池管理器 | 管理线程池的创建、动态扩缩容与任务队列调度策略 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1460 | System Startup Orchestrator 系统启动编排器 | 编排系统各组件的启动顺序、依赖等待与健康检查就绪验证 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1461 | Environment Variable Manager 环境变量管理器 | 管理环境变量的定义、分层继承、加密存储与运行时注入 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1462 | Process Daemon Monitor 进程守护监控器 | 监控守护进程的健康状态，执行异常进程自动重启与告警 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1463 | Graceful Shutdown Coordinator 优雅关闭协调器 | 系统优雅关闭的任务完成等待与状态保存协调 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1465 | Communication Protocol Adapter 通信协议适配器 | 适配多种通信协议之间的转换，提供统一通信抽象层 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1466 | Serialization Performance Optimizer 序列化性能优化器 | 优化数据序列化与反序列化性能，选择最优序列化方案 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1467 | Multi-Protocol Network Adapter 多协议网络适配器 | 适配多种网络协议的连接管理，提供统一网络通信接口 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1468 | Multi-Modal Input Router 多模态输入路由 | 语音/文字/文件输入智能路由分发 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1469 | Request Retry Manager 请求重试管理器 | 管理请求的重试策略，支持指数退避、抖动与熔断联动 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1470 | Data Transfer Validator 数据传输校验器 | 校验数据传输的完整性、顺序性与校验和一致性 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1471 | WebSocket Reconnection WebSocket断线重连 | 前端断线检测与自动重连 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1472 | Cross-Origin Resource Sharing Manager 跨域资源共享管理器 | 管理跨域资源共享策略，配置允许来源、方法与头部白名单 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1473 | Configuration Manager 配置管理器 | 管理运行时配置的集中存储、分发与版本控制，支撑配置热更新与灰度发布 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1474 | Runtime Configuration Validator 运行时配置校验器 | 校验运行时配置的格式合法性、逻辑一致性与类型安全 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1475 | Configuration Change Notifier 配置变更通知器 | 实时推送配置变更事件，通知订阅者更新运行时配置 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1476 | Configuration Diff Detector 配置差异检测器 | 检测配置版本间的差异，生成结构化的配置变更对比报告 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1477 | Configuration Merge Engine 配置合并引擎 | 合并多层配置源，按优先级策略解决配置冲突 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1478 | Environment Configuration Layering Manager 环境配置分层管理器 | 管理开发/测试/生产等多环境的分层配置与覆盖策略 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1479 | Configuration Encryption Manager 配置加密管理器 | 管理敏感配置的加解密，支持密钥轮换与访问控制 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1480 | Configuration Hot Update Engine 配置热更新引擎 | 在不停机情况下动态更新运行时配置，确保配置实时生效 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1481 | Configuration Dependency Mapper 配置依赖映射器 | 映射配置项之间的依赖关系，检测配置变更的级联影响 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1482 | Configuration Version Management & Rollback Framework 配置版本管理与回滚框架 | 配置变更的版本控制、diff对比与一键回滚 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1483 | Configuration Validation Engine 配置校验引擎 | 配置变更前的格式校验、逻辑一致性校验与冲突检测 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1484 | Unified Feature Toggle Framework 统一功能开关框架 | 各域新功能的特性开关统一管理与灰度控制 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1485 | Resource Scheduler 资源调度器 | 运行时计算资源的动态分配、优先级抢占调度与资源回收 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1486 | Elastic Scaling Manager 弹性伸缩管理器 | 基于负载指标动态调整服务实例数量，实现水平弹性伸缩 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1487 | Multi-Region Collaboration Manager 多区域协同管理器 | 管理多区域部署的服务协同、数据同步与区域间路由策略 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1488 | Request Forwarding & Load Balancer 请求转发与负载均衡器 | 请求转发+负载均衡+健康检查+故障转移 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1489 | Service Discovery Registrar 服务发现注册器 | 管理服务实例的自动注册、健康状态上报与服务发现查询 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1490 | Container Orchestrator 容器编排器 | 管理容器生命周期、调度策略、服务网络与存储挂载编排 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1491 | Network Policy Manager 网络策略管理器 | 定义并执行容器间网络访问控制策略与网络分段隔离规则 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1492 | Traffic Shaper 流量整形器 | 对进出流量实施速率限制、带宽分配与流量优先级控制 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1493 | Load Balancing Strategy Engine 负载均衡策略引擎 | 执行负载均衡策略决策，支持轮询/加权/最少连接等算法 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1494 | Container Image Cache Manager 容器镜像缓存管理器 | 管理容器镜像的分层缓存、预热拉取与镜像垃圾回收 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1495 | Container Resource Isolator 容器资源隔离器 | 实施容器间的CPU/内存/IO资源隔离与cgroup限制策略 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1496 | Service Rate Limiter 服务限流器 | 实施服务级别、用户级别与API级别的请求速率限制与配额管理 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1497 | Service Dependency Health Checker 服务依赖健康检查器 | 检查服务依赖链路的健康状况，逐级验证上下游服务可用性 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1498 | Runtime Infrastructure Self-Checker 运行时基础设施自检器 | 执行基础设施的全面自检，生成健康报告与异常诊断 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1499 | Live Data to Research Domain Feedback Channel 实盘数据→研究域反馈通道 | 实盘数据到研究域的反馈机制+监控评估→研究域洞察反馈+反馈闭环 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1500 | Message Queue Manager 消息队列管理器 | 管理消息队列的拓扑定义、消费者组协调与消息投递保证 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1501 | Distributed Lock Manager 分布式锁管理器 | 提供分布式环境下的互斥锁、读写锁与锁超时自动释放机制 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1502 | Cache Warmup Manager 缓存预热管理器 | 管理系统启动时缓存数据的预先加载与热点数据预测填充 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1503 | Cold Start Optimizer 冷启动优化器 | 优化服务冷启动速度，减少初始化延迟与首次请求响应时间 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1504 | Factor Warmup Manager 因子预热管理器 | 管理因子计算引擎的预热加载，减少首次计算延迟 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1505 | Signal Warmup Manager 信号预热管理器 | 管理信号生成管线的预热初始化，确保实时信号就绪 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1506 | Real-Time Data Warmer 实时数据预热器 | 预热实时数据接入通道，预加载高频数据源连接与会话 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1507 | Model Warmup Manager 模型预热管理器 | 管理模型的预加载到内存/显存，减少首次推理延迟 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1508 | Inference Engine Warmer 推理引擎预热器 | 预热推理引擎的计算图与执行环境，加速首Token生成 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1509 | Cache Data Preloader 缓存数据预加载器 | 在系统启动时预加载热点缓存数据，减少缓存击穿风险 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1510 | Data Compression Manager 数据压缩管理器 | 管理传输数据的压缩策略，平衡压缩率与CPU开销 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1511 | Inter-Layer Data Format Converter & Validator 层间数据格式转换与校验器 | 各层数据格式定义+格式转换器+格式校验+格式版本管理 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1512 | Data Format Version Coordinator 数据格式版本协调器 | 协调不同服务版本间的数据格式兼容性，管理格式版本演进 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1513 | Data Transformation Performance Optimizer 数据转换性能优化器 | 优化数据转换管线的处理性能，减少格式转换延迟 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1514 | Batch Data Processor 批量数据处理器 | 管理批量数据的聚合处理、窗口计算与批量写入优化 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1515 | Real-Time Data Stream Manager 实时数据流管理器 | 管理实时数据流的接入、背压控制与流式处理编排 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1516 | Data Buffer Pool Manager 数据缓冲池管理器 | 管理数据缓冲池的内存分配、容量控制与溢出处理策略 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1517 | Data Source Star Rating Dynamic Updater 数据源星级评分动态更新器 | 基于实际表现自动更新数据源星级评分 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1518 | Data Migration Script Generator 数据迁移脚本生成器 | 基于Schema版本差异自动生成数据迁移脚本与回滚脚本 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1519 | Database Schema Synchronizer 数据库Schema同步器 | 同步应用Schema定义与数据库实际Schema，检测差异并生成DDL | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1520 | Field Mapping Converter 字段映射转换器 | 执行不同Schema间的字段映射与数据转换，支持复杂映射规则 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1521 | Data Transformation Pipeline Orchestrator 数据转换管线编排器 | 编排多步骤数据转换流程，管理数据在各个转换阶段间的流转 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1522 | Data Aggregation View Manager 数据聚合视图管理器 | 管理数据聚合视图的定义、物化刷新与查询优化 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1523 | Telemetry Four-Stream Unified Collector 遥测四流统一采集器 | 统一采集指标/日志/追踪/事件四类遥测数据流，标准化格式输出 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1524 | Request Chain Tracer 请求链追踪器 | 端到端请求链路的分布式追踪、Span关联与延迟瓶颈定位 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1525 | MCP Sentinel System Monitor MCP哨兵系统监控器 | 基于MCP协议的哨兵式系统健康监控、异常探测与自动告警 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1526 | Monitoring Data Aggregator 监控数据聚合器 | 聚合多源监控数据，执行数据去重、降采样与时序对齐 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1527 | Real-Time Alert Engine 实时告警引擎 | 基于规则引擎实时评估监控指标，触发分级告警通知 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1528 | Alert Silence Manager 告警静默管理器 | 管理告警静默窗口、维护期抑制规则与告警去重合并 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1529 | Alert Escalation Strategy Engine 告警升级策略引擎 | 定义并执行告警升级策略，按时间和严重程度逐级升级 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1530 | Metric Anomaly Detector 指标异常检测器 | 基于统计模型检测指标异常波动，识别潜在系统问题 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1531 | Privacy-Preserving Computation 隐私保护计算 | 隐私数据的安全计算执行环境，基于TEE/MPC等隐私增强技术方案 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1532 | Data Sovereignty Manager 数据主权管理器 | 数据存储位置合规控制、跨区域数据传输管控与主权策略执行 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1533 | Clock Sync Service 时钟同步服务 | 分布式系统时钟同步、时间戳一致性与时钟漂移补偿保障 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1534 | Code Security Static Analyzer 代码安全静态分析器 | 静态扫描代码安全漏洞、敏感信息泄露与CWE合规性问题 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1535 | Document Search Indexer 文档搜索索引器 | 建立文档全文搜索索引，支持模糊匹配与语义搜索能力 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1536 | Module Version Dependency Resolver 模块版本依赖解析器 | 解析模块间版本依赖约束，执行版本兼容性校验与冲突检测 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1537 | Code Structure Visualizer 代码结构可视化器 | 生成代码结构拓扑图、类层次关系图与模块组织架构图 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1538 | Package Dependency Graph Generator 包依赖图生成器 | 自动生成包级别依赖关系的有向无环图，标注依赖方向与强度 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1539 | Code Complexity Analyzer 代码复杂度分析器 | 分析代码圈复杂度、认知复杂度与可维护性指数，生成复杂度报告 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1540 | Code Duplication Detector 代码重复检测器 | 检测代码库中的重复代码片段，计算相似度并生成去重建议 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1541 | Code Change Impact Analyzer 代码变更影响分析器 | 分析代码变更的影响范围，追踪变更传播路径与受影响模块 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1542 | Automated Code Reviewer 自动代码审查器 | 自动执行代码审查规则，检测代码异味、反模式与最佳实践偏离 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1543 | Code Standard Enforcer 代码规范强制执行器 | 强制执行代码风格规范、命名约定与格式化规则的自动化工具 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1544 | Architecture Compliance Checker 架构合规检查器 | 自动检查代码实现是否符合架构设计约束、分层规则与依赖方向 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1545 | Technical Debt Tracker 技术债务追踪器 | 量化追踪技术债务指标，生成偿还优先级排序与改进建议 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1546 | Architecture Evolution Planner 架构演进规划器 | 规划架构演进路径，评估架构变更风险与迁移成本 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1547 | Code Template Engine 代码模板引擎 | 基于模板和参数生成标准化代码骨架，支持条件逻辑与循环 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1548 | DAO Layer Code Generator DAO层代码生成器 | 基于数据模型自动生成DAO层CRUD代码与查询方法 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1549 | REST API Code Generator REST API代码生成器 | 基于接口契约自动生成REST API控制器代码与路由配置 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1550 | Test Code Generator 测试代码生成器 | 基于接口契约自动生成单元测试与集成测试代码骨架 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1551 | Configuration Code Generator 配置代码生成器 | 基于配置Schema自动生成类型安全的配置加载代码 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1552 | Interface Mock Generator 接口Mock生成器 | 基于接口定义自动生成Mock实现，支持行为配置与返回值预设 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1553 | Data Model Generator 数据模型生成器 | 基于Schema定义自动生成数据模型类、序列化与反序列化代码 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1554 | Validation Rule Generator 验证规则生成器 | 基于Schema约束自动生成数据验证规则代码与校验逻辑 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1555 | Error Handling Code Generator 错误处理代码生成器 | 自动生成统一的错误处理、异常映射与错误码管理代码 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1556 | API Version Manager API版本管理器 | 管理API版本生命周期，执行版本兼容性检查与废弃策略编排 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1557 | Module Interface Contract Manager 模块接口契约管理器 | 模块间接口定义+接口版本管理+接口兼容性验证+接口文档自动生成 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1558 | SDK Auto Generator SDK自动生成器 | 基于接口契约自动生成多语言SDK客户端代码与使用文档 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1559 | API Documentation Synchronizer API文档同步器 | 自动同步API实现与文档描述，检测文档不一致并触发更新 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1560 | Endpoint Response Format Validator 端点响应格式校验器 | 校验API端点响应是否匹配契约定义的格式与类型约束 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1561 | API Version Compatibility Detector API版本兼容检测器 | 检测API新版本与旧版本的向后兼容性，标记Breaking Changes | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1562 | Return Value Performance Monitor 返回值性能监控器 | 监控API返回值的大小、序列化耗时与传输延迟性能指标 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1563 | Inter-Module Communication Protocol Manager 模块间通信协议管理器 | 管理模块间通信协议的定义、版本协商与协议适配 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1564 | Module Lifecycle Manager 模块生命周期管理器 | 管理模块从加载、初始化、运行到卸载的完整生命周期状态 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1565 | Module Registry 模块注册中心 | 维护模块的注册信息，提供模块发现与元数据查询服务 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1566 | Module Dependency Injector 模块依赖注入器 | 管理模块间的依赖注入，执行构造函数注入与属性注入绑定 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1567 | Module Configuration Aggregator 模块配置聚合器 | 聚合各模块的分散配置为统一配置视图，处理配置覆盖与合并 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1568 | Module Health Checker 模块健康检查器 | 周期性探测各模块的健康状态，执行活性检查与就绪检查 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1569 | Module Hot Update Manager 模块热更新管理器 | 管理模块的热更新流程，支持不停机替换与灰度切换 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1570 | Module Feature Toggle Manager 模块功能开关管理器 | 管理模块级功能开关，支持运行时动态启用或禁用模块功能 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1571 | Plugin System Manager 插件系统管理器 | 管理插件系统的加载、隔离与生命周期，支持动态扩展机制 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1572 | Module Sandbox Isolator 模块沙箱隔离器 | 为模块提供沙箱执行环境，限制资源访问与权限边界 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1573 | Module Metrics Collector 模块度量采集器 | 采集各模块的运行度量指标，包括调用量、延迟与错误率 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1574 | Module Log Aggregator 模块日志聚合器 | 聚合各模块的分散日志，统一格式化与日志级别管理 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1575 | Module Exception Boundary Manager 模块异常边界管理器 | 定义模块异常边界，防止异常跨模块传播导致级联故障 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1576 | Module Performance Profiler 模块性能分析器 | 对模块运行时性能进行采样分析，识别热点路径与瓶颈 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1577 | Module Documentation Indexer 模块文档索引器 | 索引各模块的技术文档，支持关键词搜索与文档关联查询 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1578 | Module Test Runner 模块测试运行器 | 编排模块级测试的执行，支持并行测试与依赖排序 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1579 | Global Dependency Graph Calculator 全局依赖图计算器 | 计算全系统模块间的完整依赖图，分析依赖方向与深度 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1580 | Circular Dependency Detector 循环依赖检测器 | 检测模块间的循环依赖，定位循环路径并生成解除建议 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1581 | Dependency Version Lock Manager 依赖版本锁定管理器 | 管理依赖版本的锁定策略，生成锁文件并检测未授权变更 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1582 | Dependency Security Vulnerability Scanner 依赖安全漏洞扫描器 | 扫描依赖库的已知安全漏洞，输出CVE风险等级与修复建议 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1583 | Transitive Dependency Analyzer 传递依赖分析器 | 分析依赖的传递链路，识别间接依赖的版本冲突与风险 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1584 | Dependency Conflict Resolver 依赖冲突解决器 | 检测并解决多个依赖之间的版本冲突，执行依赖仲裁策略 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1585 | Dependency Upgrade Compatibility Checker 依赖升级兼容性检查器 | 检查依赖升级后的API兼容性与行为变更影响 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1586 | Dependency Graph Visualization Renderer 依赖图可视化渲染器 | 将全局依赖图渲染为交互式可视化图形，支持缩放与过滤 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1587 | Regression Test Orchestrator 回归测试编排器 | 编排回归测试套件的执行顺序、并行测试与测试结果汇总 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1588 | Test Coverage Tracker 测试覆盖率追踪器 | 追踪代码测试覆盖率的行/分支/条件覆盖度与覆盖率趋势 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1589 | Document Template Engine 文档模板引擎 | 基于模板生成标准化文档，支持模板变量替换与条件渲染 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1590 | Document Version Manager 文档版本管理器 | 管理文档版本与代码版本同步，维护文档版本树 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1591 | Terminology Consistency Validator 术语一致性校验器 | 校验文档中术语使用的一致性，检测同义异名与异义同名 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1592 | Specification Automation Checker 规范自动化检查器 | 自动检查文档内容是否满足规范模板的结构完整性要求 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1593 | Document Link Validator 文档链接验证器 | 验证文档间交叉引用的链接有效性，检测死链与过期引用 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1594 | Knowledge Base Indexer 知识库索引器 | 建立知识库的结构化索引，支持全文检索与语义查询 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1595 | Strategy Execution Plan Optimizer 策略执行计划优化器 | 优化策略执行计划的并行度、执行顺序与资源分配 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1596 | Strategy Backtesting Infrastructure 策略回测基础设施 | 提供策略回测所需的计算资源、数据管道与结果存储基础设施 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1598 | Strategy Portfolio Simulator 策略组合模拟器 | 模拟多个策略组合的运行效果，评估组合风险与收益 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1599 | Strategy Parameter Tuning Engine 策略参数调优引擎 | 自动化调优策略超参数，执行网格搜索与贝叶斯优化 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1600 | Strategy Correlation Matrix Calculator 策略相关性矩阵计算器 | 计算多策略收益率序列的相关性矩阵，识别策略间相关风险 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1601 | Resource Load Balancer 资源负载均衡器 | 开发资源分配与负载均衡 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1602 | Task Priority Scheduler 任务优先级调度器 | 基于任务优先级、截止时间与资源需求综合调度任务执行顺序 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1603 | Resource Reservation Manager 资源预约管理器 | 管理计算资源的预先预约、时间槽分配与资源预留策略 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1604 | Resource Quota Manager 资源配额管理器 | 管理各项目/团队/用户的资源配额分配与使用量统计 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1605 | Resource Usage Auditor 资源使用审计器 | 审计资源使用记录的合规性，生成资源使用报告与异常标记 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1606 | Workflow Version Management 工作流版本管理 | 工作流定义的版本控制与回滚 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1607 | Phase Synchronization Coordinator 阶段同步协调器 | 协调多个开发阶段的同步进度，确保阶段间依赖按时交付 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1608 | Cross-Phase State Propagator 跨阶段状态传递器 | 管理开发状态在阶段间的传递与转换，确保状态一致性 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1609 | Milestone Dependency Validator 里程碑依赖校验器 | 校验里程碑之间的依赖关系是否满足，检测依赖阻塞风险 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1610 | Deliverable Version Tracker 交付物版本追踪器 | 追踪各阶段交付物的版本演进，维护版本树与变更日志 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1611 | Phase Retrospective Analyzer 阶段回顾分析器 | 分析阶段执行数据，生成回顾报告与改进建议 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1612 | Continuous Improvement Engine 持续改进引擎 | 基于历史数据驱动持续改进流程，自动生成优化建议 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1613 | Schedule Conflict Detector 时间表冲突检测器 | 任务时间重叠/资源冲突自动告警+冲突解决建议 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1614 | Development Plan Visualizer 开发计划可视化器 | 可视化渲染开发计划的时间线与里程碑，支持甘特图与看板视图 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1615 | Resource Timeline Manager 资源时间线管理器 | 管理资源使用的时间线规划，检测资源时间冲突与过载 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1616 | Iteration Cycle Tracker 迭代周期追踪器 | 追踪迭代周期的执行进度、燃尽图与交付速率度量 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1617 | Panel Layout Engine 面板布局引擎 | 运行时面板布局的编排计算、视图排列与响应式自适应调整 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1618 | Region Collapse Manager 区域折叠管理器 | 管理面板区域的折叠/展开状态、动画过渡与可见性控制 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1619 | Dependency Visualizer 依赖可视化器 | 可视化渲染模块间依赖关系图，支持交互式探索与依赖路径追踪 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1620 | Deployment Topology Manager 部署拓扑管理器 | 管理部署拓扑的定义、编排与拓扑变更的自动化执行 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1621 | Feature Lifecycle Manager 功能生命周期管理器 | 管理功能从实验、灰度到全量发布的生命周期状态转换 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1622 | Domain-Driven Design Validator 领域驱动设计校验器 | 校验代码实现是否符合领域驱动设计约束，检查聚合边界与限界上下文 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1623 | Architecture Recommendation Engine 架构推荐引擎 | 基于项目特征推荐最佳架构模式与技术栈选型方案 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1624 | Infrastructure Topology Visualizer 基础设施拓扑可视化器 | 可视化渲染基础设施的物理与逻辑拓扑布局 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1625 | Application State Snapshotter 应用状态快照器 | 创建应用运行时状态的完整快照，支持状态恢复与回放 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1626 | Session Persistence Manager 会话持久化管理器 | 管理用户会话的持久化存储、过期清理与会话恢复机制 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1627 | User Preference Synchronizer 用户偏好同步器 | 跨设备同步用户偏好设置，解决冲突合并与一致性维护 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1628 | Multi-Device State Coordinator 多端状态协调器 | 协调多终端间的状态一致，执行乐观更新与冲突解决 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1629 | Conversation Context Compressor 对话上下文压缩 | 长对话上下文智能压缩与摘要 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1754 | Canary Dependency Mapper 金丝雀依赖映射器 | 金丝雀发布依赖映射 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1755 | Blue-Green Dependency Mapper 蓝绿依赖映射器 | 蓝绿部署依赖映射 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1756 | AB Test Dependency Mapper AB测试依赖映射器 | AB测试依赖映射 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1757 | Traffic Mirror Mapper 流量镜像映射器 | 流量镜像依赖映射 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1758 | Progressive Delivery Pre-check Enhancer 渐进交付前置检查增强 | 渐进交付前置检查增强 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1759 | Traffic Mirror Dependency Mapping Enhancer 流量镜像依赖映射增强 | 流量镜像依赖映射增强 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1760 | Policy Conflict Auto Detector 策略冲突自动检测器 | 策略冲突自动检测器 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1804 | VaR Recalculation Scheduler VaR重算调度器 | VaR重算调度器：事件触发+定时重算+增量计算 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2087 | Collection Scheduler 采集调度器 | §11.2 S0组件接收C-022质量报告调整数据源采集优先级 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2111 | Task Orchestration 任务编排 | 编排Agent技能任务编排ACTIVE | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2119 | Strategy Health Score 策略健康评分 | 归因Agent技能策略健康评分ACTIVE | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2120 | Circuit Breaker Trigger 熔断触发 | 风控Agent技能熔断触发ACTIVE | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2145 | Circuit Breaker 熔断器 | 熔断器Circuit Breaker Agent失败阈值熔断时间 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2173 | Working Memory 工作记忆 | 工作记忆Working Memory Redis内存单次会话 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2205 | Redis Redis内存数据库 | Redis消息总线进程内函数调用持久化发布订阅 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2206 | SQLite SQLite嵌入式数据库 | SQLite情景记忆温区语义记忆永久存储 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2207 | Parquet Parquet列式存储格式 | Parquet语义记忆永久存储冷存储归档 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2249 | Multi-Dimensional Quantitative Health Indicator 多维量化健康指标 | / strategy-health-score / 多维量化健康指标(Sharpe+IC+MaxDD+Calmar加权) / ACTIVE / | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2263 | strategy-health-score 策略健康评分 | / strategy-health-score / 多维量化健康指标(Sharpe+IC+MaxDD+Calmar加权) / ACTIVE / | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2285 | Redis Pub/Sub Redis发布订阅 | / JSON-RPC 2.0 over HTTP / JSON-RPC 2.0 over Redis Pub/Sub / 保留JSON-RPC 2.0语义，传输层替换为Redis / | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2344 | Success Metrics 成功指标 | 成功指标11项Agent决策延迟到协作成功率到自治边界违规次数到LLM路由成本控制率到自反Agent反思有效率等 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2433 | L10 Audit Trail 审计追踪与零知识审计 | C轨L10层审计追踪与零知识审计 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2449 | Audit Evidence Chain Architecture 审计证据链架构 | 三层审计架构对标EU AI Act Article 12 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2450 | Three Layer Audit Architecture 三层审计架构 | L1事件完整性+L2集合完整性+L3外部可验证性 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2451 | Hash Chain Audit 哈希链审计 | L1事件完整性SHA-256链式哈希 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2452 | Merkle Tree Audit Merkle树审计 | L2集合完整性日/周/月批量完整性证明 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2470 | Zero Knowledge Audit 零知识审计 | 可证明合规但不暴露策略细节的审计机制 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2477 | ZKP Circuit Library ZKP电路库 | zkCA架构组件参与率/自交易/持仓限额/操纵检测证明 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2501 | AI Training Data Audit AI训练数据审计 | 确保训练数据不含内幕信息 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2510 | Operation Process Audit 操作流程审计 | 关键操作流程自动化审计 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2585 | Audit Log 审计日志 | 交易审计+决策审计+数据访问审计+AI调用审计+系统变更审计 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2746 | Trading Audit Log 交易审计日志 | 审计日志每笔订单的完整生命周期≥7年 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2747 | Decision Audit Log 决策审计日志 | 审计日志每个决策的信号来源+推理过程≥3年 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2748 | Data Access Audit Log 数据访问审计日志 | 审计日志每次L3/L4数据访问记录≥1年 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2749 | AI Call Audit Log AI调用审计日志 | 审计日志每次LLM调用的脱敏前后数据≥1年 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2750 | System Change Audit Log 系统变更审计日志 | 审计日志配置变更/参数修改/权限变更≥1年 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3003 | AI自治行为审计 AI Autonomous Behavior Audit | 审计AI决策自治分类判定 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3052 | boundary_audit.py 自治行为审计 | 审计AI自治行为是否越界 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3376 | 熔断器模式 Circuit Breaker Pattern | / 熔断器模式 / 5次失败/60秒→OPEN(全拒)→30秒HALF-OPEN(探针)→CLOSED / OWASP ASI08 / Netflix Hystrix / | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3532 | asymmetric_audit.py 非对称审计 | DD-SEC-002归入AP非对称审计是自治审计 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3576 | 定时熔断 Timer Circuit Breaker | / 定时熔断 / <1ms / 交易时段核心进程无心跳>5秒 / 基础设施层 / | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3581 | L4审计隔离 L4 Audit Isolation | / L4 审计隔离 / 否决日志独立存储，策略模块不可写 / 不可篡改审计链(HC-RISK-05) / | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3613 | 审计可追溯缺口 Audit Traceability Gap | 保障缺口管理AI决策链可能不透明vs每笔决策可溯源C-030决策可解释性+审计链 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3647 | Redis Stream 消息通道 | 成交回报At-Least-Once+幂等消费 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3648 | Redis Pub/Sub 发布订阅 | 数据更新通知At-Most-Once | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3673 | External API Metrics 外部API调用指标 | / 外部API调用指标 / ✅能建 / `prometheus_client` Histogram+Counter / 无 / | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3674 | Circuit Breaker State Export 熔断器状态导出 | prometheus_client Gauge | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3722 | Redis Hash Redis哈希 | 原始交互记录存入工作记忆实时写入 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3723 | FAISS Vector Search FAISS向量检索 | FAISS向量检索+SQLite结构化查询 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3726 | ChromaDB Vector Database ChromaDB向量数据库 | / 向量存储 / ChromaDB+Faiss GPU(双轨已采用) / ChromaDB+Faiss GPU+Qdrant评估 / Qdrant/Chroma(独立服务) / | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3727 | Faiss GPU Vector Search Faiss GPU向量搜索 | Faiss GPU利用RTX 3090 24GB显存 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3728 | Qdrant Vector Database Qdrant向量数据库 | Qdrant/Chroma独立服务评估 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3729 | ClickHouse Database ClickHouse数据库 | ClickHouse替代DuckDB支持更复杂查询 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3730 | DuckDB Database DuckDB数据库 | DuckDB+Parquet温存储 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3736 | Kafka Message Queue Kafka消息队列 | Parquet+Kafka事件存储 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3737 | EventStoreDB Event Store EventStoreDB事件存储 | Kafka+EventStoreDB事件存储 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3743 | MinIO Object Storage MinIO对象存储 | 对象存储MinIO/NAS冷存储 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3744 | NAS Storage NAS存储 | 对象存储MinIO/NAS冷存储 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3746 | Parquet Columnar Storage Parquet列式存储 | Parquet列式存储温冷层 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3747 | Redis In-Memory Store Redis内存存储 | Redis热存储行情缓存 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3748 | SQLite Database SQLite数据库 | SQLite血缘追踪 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3775 | Blueprint Code Sync 蓝图代码同步 | src/zephyr/core/blueprint_code_sync.py,module,MOD-INF-016-CORE | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3776 | Base 基础 | src/zephyr/l02_alpha_factor/base.py,module,MOD-L02-001 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3778 | App 包装器 | src/zephyr/l08_human_ai_interface/dashboard/app.py,module,MOD-L08-001 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3779 | State Machine 状态机 | src/zephyr/shared/state_machine.py,module,MOD-INF-016-SHARED | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3876 | NSSM+自研Supervisor 进程守护层 | 进程守护层P1-P5优先级控制+自动重启+日志管理 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3878 | Redis共享状态 共享状态层 | 13命名空间AOF+RDB混合持久化 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3879 | GPU调度层 GPU调度 | RTX 3090 24GB盘中推理盘后训练 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3880 | Hot平面 热平面 | 小于10ms风控执行路径CPU核8-11 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3881 | Warm平面 温平面 | 10ms到1s信号策略路径CPU核4-7 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3882 | Cold平面 冷平面 | 大于1s训练研究路径CPU核16-19 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3892 | GPU调度上岗+热交换 GPU调度 | 盘中推理8-10GB盘后训练16-18GB | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3910 | 熔断器模式 Circuit Breaker | Netflix Hystrix三态熔断Closed Open Half-Open | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3911 | 应急保命轨 应急保命轨 Emergency Life-Saving Track | L0正常L1降级L2保命L3冻结四级 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3943 | 审计追踪依赖构建器 Audit Trail Dependency Builder | 审计追踪依赖构建器 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3948 | Audit Trail Dependency Integrity Verifier 审计追踪依赖完整性验证器 | 审计追踪依赖完整性验证器 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3995 | NSSM注册Windows服务 NSSM Windows Service | 5个Python进程注册为Windows服务开机自启崩溃重启 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3996 | 自研Python守护进程 Python Supervisor | 优先级启停健康检查XML-RPC控制 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3997 | pywin32supervisor pywin32监控器 | 0.0.1版本无社区验证不能建 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3998 | WinSW Windows Service Wrapper 服务 | MIT许可XML配置需NET Runtime不能建 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3999 | GPU MPS多进程并发 GPU Multi-Process Service | NVIDIA MPS允许多CUDA进程共享GPU上下文不能建 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4003 | Redis集群/哨兵 Redis Cluster Sentinel | 集群需多节点违反约束二单机部署不能建 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4122 | Monitoring Dashboard Process 监控面板进程 | A1迁移概念级进程P2 实时仪表盘告警展示持仓监控可重启 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4235 | Bandwidth Optimizer 带宽优化 | / bandwidth_optimizer.py / governance/ / 带宽优化 / ❌ 属于D-INFRA-RUNTIME——带宽是运行时基础设施 / | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4236 | Local First Architecture 本地优先架构 | / local_first_arch.py / governance/ / 本地优先架构 / ❌ 属于D-INFRA-RUNTIME——本地优先是运行时策略 / | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4237 | Environment Manager 环境管理 | / environment_manager.py / governance/ / 环境管理 / ❌ 属于D-INFRA-RUNTIME——环境管理是基础设施 / | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4238 | Path Resolver 路径解析 | / path_resolver.py / governance/ / 路径解析 / ❌ 属于D-INFRA-RUNTIME——路径解析是基础设施 / | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4254 | Governance Adapter 治理适配器 | / l01_infrastructure/a2a_protocol/governance/governance_adapter.py / l01_infrastructure/ (MOD-INF-025) / 治理适配器 / ⚠️ 双归属— | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4255 | Governance Protocol 治理协议 | / l01_infrastructure/a2a_protocol/governance/protocol.py / l01_infrastructure/ (MOD-INF-025) / 治理协议 / ⚠️ 双归属——协议层在D-INFR | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4418 | Effect Metric Trend 效果指标趋势 | / 效果指标趋势 / IC/Sharpe/胜率随时间变化趋势 / 日频 / S5效果评估 / F-05的策略评估子面板 / | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4467 | Signal Generation Audit Log 信号生成审计日志 | > **搬入原则**: 筛选与信号生成/决策/归因直接相关的合规约束，从D-SIGNAL视角重写。 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4860 | 幻觉检测指标 Hallucination Detection Metrics | 幻觉防护-事实核查通过率/一致性评分/数值异常率/置信度均值 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-5004 | Zero-Knowledge Audit 零知识审计 | 零知识证明合规验证 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-5007 | Circuit Breaker Matrix 熔断器矩阵 | 三态机+按外部系统差异化阈值交易通道人工恢复 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-5061 | Circuit Breaker State Machine 熔断器状态机 | / 5种熔断器(CB-001~CB-005) / ✅ 能建 / AP-06 Escalation Engine含CircuitBreaker三态管理 / | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-5076 | Cybersecurity Shield 网络安全防护组件 | / MOD-CMP-001 / D-INFRA-14 Cybersecurity Shield / 网络安全防护组件 / | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-5077 | Experiment and Resilience Testing 实验与韧性测试 | / MOD-EXP-001 / D-INFRA-15 Resilience Testing Engine / 实验与韧性测试 / | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-5078 | Knowledge Base Data Sovereignty 知识库数据主权管理 | / MOD-KB-002 / D-INFRA-12 Data Sovereignty Manager / 知识库数据主权管理 / | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-5079 | System Master Infrastructure 系统总蓝图基础设施支撑 | D-INFRA-01~D-INFRA-17 整体基础设施 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-5256 | Carbon-Aware Scheduler Optimizer 碳感知调度优化器 | §6设计决策 碳感知调度优化器 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-5277 | Data Change Audit 数据变更审计 | §13.4数据指纹与血缘合规 数据变更审计 | D_INFRA_RUNTIME | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-H1FS-001 | H1 Factor Source / H1 因子截面读取适配器 | (无真实痛点)设想为信号端提供友好因子读取接口,但读端已由 H1RedisReader 覆盖 | D_INFRA_RUNTIME | 否决（rejected） | 一问通过 | P2 | D_SIGNAL 信号域实际启动且需要批量多 symbol 截面读(PIPELINE)且 get_online_features 单标的不够用 | 2027-08-02 |

## 按一问卡点分组（为什么没开发）

> 一问标准（裁定 2026-08-04）：仅 q1 已实现/重复。q1「是」即不进 depgraph 设计态，登记在候选库。原 q2/q3/q4 灰度已废。

### 待评估（348 条）

| ID | 名称 | 大白话（干什么用） | 域 | 卡点理由 | 替代方案 |
|------|------|------|------|------|------|
| CAND-HARVEST-0094 | Rebalance Scheduler再平衡调度器 | / PC-03 / Rebalance Scheduler再平衡调度器 / ✅ 能建 / / 阈值+日历+事件触发+税收感知+成本感知 / | D_INFRA_RUNTIME | harvest待评估（likely_misplaced） |  |
| CAND-HARVEST-0225 | Signal Audit Logger 信号审计 | / D-SIGNAL-06 / Signal Audit Logger / ✅ / / 信号审计日志+WORM写入 / | D_INFRA_RUNTIME | harvest待评估（likely_misplaced） |  |
| CAND-HARVEST-0276 | Audit Trail 审计追踪 | / D-AUTONOMY-02 / Audit Trail / ✅ 能建 / 📋 项目内有蓝图编号MOD-INF-020已建设 / Merkle哈希链+Agent签名 / | D_INFRA_RUNTIME | harvest待评估（likely_misplaced） |  |
| CAND-HARVEST-0288 | High Performance HA Framework 高性能高可用保障框架 | / D-INFRA-46 / 高性能高可用保障框架 / ✅ 能建 / / SLA保障+故障自动切换+健康检查 / | D_INFRA_RUNTIME | harvest待评估（likely_new） |  |
| CAND-HARVEST-0611 | Database Layer 数据库层 | SQLite+DuckDB+PostgreSQL统一存储抽象 | D_INFRA_RUNTIME | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-0630 | 数据库管理器 Database Manager (16分片SQLite) | 16分片SQLite读写路由+分片策略+连接池 | D_INFRA_RUNTIME | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-0631 | 跨域事件总线 Cross-domain Event Bus | 跨域事件发布订阅+事件路由分发+事件持久化 | D_INFRA_RUNTIME | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-0632 | 缓存一致性管理器 Cache Consistency Manager | 多层缓存一致性维护+缓存失效策略+版本控制 | D_INFRA_RUNTIME | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-0633 | 数据质量监控器 Data Quality Monitor | 数据管线质量指标监控+数据异常与漂移检测 | D_INFRA_RUNTIME | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-0634 | 数据血缘追踪器 Data Lineage Tracker | 数据从源头到消费端完整路径与转换历史追踪 | D_INFRA_RUNTIME | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-0635 | 数据完整性校验器 Data Integrity Validator | 端到端数据完整性+哈希验证+Merkle树一致性检查 | D_INFRA_RUNTIME | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-0636 | 数据字段Schema版本管理器 Data Field Schema Version Manager | 数据字段定义Schema版本管理+迁移脚本生成 | D_INFRA_RUNTIME | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-0637 | 数据验证规则引擎 Data Validation Rule Engine | 声明式规则数据验证+组合规则+自定义校验器 | D_INFRA_RUNTIME | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-0805 | Auto Backtest Scheduler 自动回测调度器 | 自动回测调度器参数网格批量回测vectorbt向量化回测队列管理回测结果聚合 | D_INFRA_RUNTIME | harvest待评估（likely_misplaced） |  |
| CAND-HARVEST-0844 | 集成测试任务 Integration Task | 各模块集成测试的任务分解和时间估算 | D_INFRA_RUNTIME | harvest待评估（likely_misplaced） |  |
| CAND-HARVEST-0859 | Audit Trail 审计链 | 审计链操作日志+决策日志+变更日志+不可篡改+哈希链验证 | D_INFRA_RUNTIME | harvest待评估（likely_misplaced） |  |
| CAND-HARVEST-0860 | Process Manager 进程管理器 | 进程管理器NSSM+5进程P1~P5优先级+进程监控+进程重启+进程日志 | D_INFRA_RUNTIME | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-0861 | Redis Manager Redis管理器 | Redis管理器13命名空间+连接池+集群管理+持久化+内存策略 | D_INFRA_RUNTIME | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-0862 | GPU Scheduler GPU调度器 | GPU调度器CUDA设备管理+显存分区+时段优先调度+模型热交换+OOM防护 | D_INFRA_RUNTIME | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-0863 | ConfigManager 配置管理器 | / IF-INFRA-002 / D-INFRA-RUNTIME / `ConfigManager` / 软(E-0007) / 安全策略配置热更新 / | D_INFRA_RUNTIME | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-0864 | Service Registry 服务注册表 | 服务注册表服务发现+健康检查+负载均衡+服务元数据 | D_INFRA_RUNTIME | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-0865 | Message Queue 消息队列 | 消息队列Redis Streams+发布订阅+消息持久化+消费者组+死信队列 | D_INFRA_RUNTIME | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-0895 | EventBus 事件总线 | / IF-INFRA-001 / D-INFRA-RUNTIME / `EventBus` / 软(E-0007) / 跨域事件发布/订阅 / | D_INFRA_RUNTIME | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-0896 | Config Center 配置中心 | 配置中心YAML配置+环境变量+配置热更新+配置版本+配置校验+配置审计 | D_INFRA_RUNTIME | harvest待评估（likely_misplaced） |  |
| CAND-HARVEST-0897 | Health Checker 健康检查器 | 健康检查器存活检查+就绪检查+启动检查+健康报告+健康聚合 | D_INFRA_RUNTIME | harvest待评估（likely_misplaced） |  |
| CAND-HARVEST-0898 | Metrics Collector 指标采集器 | 指标采集器Prometheus格式+自定义指标+指标聚合+指标导出+指标查询 | D_INFRA_RUNTIME | harvest待评估（likely_misplaced） |  |
| CAND-HARVEST-0899 | Logger 日志器 | 日志器结构化日志+日志级别+日志路由+日志聚合+日志脱敏 | D_INFRA_RUNTIME | harvest待评估（likely_misplaced） |  |
| CAND-HARVEST-0900 | Retry & Circuit Breaker 重试与熔断器 | 重试与熔断器指数退避重试+熔断器状态机+舱壁隔离+超时控制+降级策略 | D_INFRA_RUNTIME | harvest待评估（likely_misplaced） |  |
| CAND-HARVEST-0901 | Task Scheduler 任务调度器 | 任务调度器定时任务+周期任务+一次性任务+任务依赖+任务重试+任务审计 | D_INFRA_RUNTIME | harvest待评估（likely_misplaced） |  |
| CAND-HARVEST-0902 | 审计系统 Audit System | 操作日志+决策日志+不可篡改+哈希链验证 | D_INFRA_RUNTIME | harvest待评估（likely_misplaced） |  |
| CAND-HARVEST-0907 | Runtime 运行时 | 运行时(进程管理+配置管理+服务注册+消息队列) | D_INFRA_RUNTIME | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-0991 | Inference Circuit Breaker 推理熔断器 | 推理异常+熔断+降级+恢复 | D_INFRA_RUNTIME | harvest待评估（likely_misplaced） |  |
| CAND-HARVEST-1056 | MCP Gateway Rate-Limit Audit Manager MCP网关限流审计管理器 | 10QPS限流+审计+熔断降级 | D_INFRA_RUNTIME | harvest待评估（likely_misplaced） |  |
| CAND-HARVEST-1058 | Immutable Audit Log Writer 不可变审计日志写入器 | 不可变审计日志+哈希链+验证 | D_INFRA_RUNTIME | harvest待评估（likely_misplaced） |  |
| CAND-HARVEST-1059 | TaskCard Six-Dimension Anti-Drift Validator TaskCard六维防漂移校验器 | 31字段+六维漂移检测 | D_INFRA_RUNTIME | harvest待评估（likely_misplaced） |  |
| CAND-HARVEST-1060 | Audit-Persistence Dual-Write Coordinator 审计-持久化双写协调器 | 审计日志+任务状态双写一致性 | D_INFRA_RUNTIME | harvest待评估（likely_misplaced） |  |
| CAND-HARVEST-1130 | SystemHealthVisualization 系统健康可视化 | 系统健康可视化+三平面状态展示 | D_INFRA_RUNTIME | harvest待评估（likely_misplaced） |  |
| CAND-HARVEST-1166 | Service Degradation Manager 服务降级管理器 | 管理服务降级策略，在过载时自动切降非核心功能保障核心链路 | D_INFRA_RUNTIME | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1167 | Connection Pool Manager 连接池管理器 | 管理数据库/缓存/消息队列等连接池的大小、超时与泄漏检测 | D_INFRA_RUNTIME | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1170 | Failover Coordinator 故障转移协调器 | 协调服务故障检测、主备切换与故障恢复流程编排 | D_INFRA_RUNTIME | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1230 | Risk Check Dependency Short-Circuit Evaluator 风控检查依赖短路评估器 | 风控检查依赖短路评估器 | D_INFRA_RUNTIME | harvest待评估（likely_misplaced） |  |
| CAND-HARVEST-1243 | Vector Index Health Monitor 向量索引健康监控器 | 索引健康监控+向量索引损坏检测/索引修复+索引性能监控 | D_INFRA_RUNTIME | harvest待评估（likely_misplaced） |  |
| CAND-HARVEST-1246 | Core Chain E2E Health Monitor 核心链路端到端健康监控器 | TaskCard→Gate→Pipeline→Security→Audit→Feedback核心链路监控 | D_INFRA_RUNTIME | harvest待评估（likely_misplaced） |  |
| CAND-HARVEST-1247 | Code Health Assessor 代码健康度评估器 | 1714文件/160315行/238TODO/184未实现等代码质量指标+健康评分 | D_INFRA_RUNTIME | harvest待评估（likely_misplaced） |  |
| CAND-HARVEST-1252 | System Health Five-Star Scorer 系统健康度五星评分器 | 架构设计/代码质量/必要功能比例/过度工程程度/AI可维护性5维度评分 | D_INFRA_RUNTIME | harvest待评估（likely_misplaced） |  |
| CAND-HARVEST-1258 | M10 Audit Report Finding Format Generator M10审计报告Finding格式生成器 | M10生成Finding格式报告+报告模板+报告数据填充+报告分发 | D_INFRA_RUNTIME | harvest待评估（likely_misplaced） |  |
| CAND-HARVEST-1290 | PERM Independent Health Checker PERM独立健康检查器 | 独立于CORE的健康检查，CORE崩溃时PERM仍可检测 | D_INFRA_RUNTIME | harvest待评估（likely_misplaced） |  |
| CAND-HARVEST-1291 | Trading Session Aware Ops Scheduler 交易时段感知运维调度器 | 交易时段仅监控+告警，修复延至盘后 | D_INFRA_RUNTIME | harvest待评估（likely_misplaced） |  |
| CAND-HARVEST-1335 | Financial Time Series Data Augmentation 金融时序数据增强 | TimeGAN/QuantGAN生成合成序列+条件扩散模型+时间扭曲/幅度缩放 | D_INFRA_RUNTIME | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1417 | Multi-Process Isolation & Runtime Architecture 多进程隔离与运行时架构 | GPU分时调度隔离+共享内存零拷贝 | D_INFRA_RUNTIME | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1418 | Model Registry & Experiment Management 模型注册与实验管理 | MLflow Model Registry追踪版本/指标/部署状态/退化+Experiment Tracking | D_INFRA_RUNTIME | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1419 | Time-Series Database & Tiered Storage 时序数据库与分层存储架构 | 4元组数据映射模型+DuckDB+Parquet三层Hot/Warm/Cold存储 | D_INFRA_RUNTIME | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1420 | Feature Drift & Concept Drift Detection 特征漂移与概念漂移检测 | 特征漂移PSI/KL散度+概念漂移ADWIN/DDM/EDDM+标签漂移滚动KS | D_INFRA_RUNTIME | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1421 | Graph Neural Network for Stock Relations 图神经网络用于股票关系建模 | RGCN多关系图+TGN时变图+GAT注意力+6类知识图谱边 | D_INFRA_RUNTIME | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1422 | Transformer Time-Series Architecture Transformer时序架构 | Informer+PatchTST+TimesNet+iTransformer→密度预测Phase2/3增强 | D_INFRA_RUNTIME | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1423 | Signature Methods 签名方法 | Rough Path Theory迭代积分→自动提取任意高阶路径依赖+Log-signature降维 | D_INFRA_RUNTIME | harvest待评估（likely_new） |  |
| CAND-HARVEST-1424 | Reinforcement Learning for Portfolio & Execution 强化学习用于组合优化与订单执行 | RL组合优化(PPO/SAC)+RL最优执行(DQN/PPO)+RL做T策略+6条安全约束 | D_INFRA_RUNTIME | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1425 | LLM Agent for Fundamental Analysis 大语言模型Agent用于基本面分析 | 多Agent架构(财报Agent+新闻Agent+综合Agent)+本地Qwen2.5-7B/14B量化版 | D_INFRA_RUNTIME | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1426 | Alternative Data Source Expansion 另类数据源扩展 | 社交媒体情绪+上市公司数字足迹+产业链供应链+卫星遥感 | D_INFRA_RUNTIME | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1427 | Market Microstructure Deep Modeling 市场微观结构深度建模 | VPIN订单流毒性检测+LOB限价订单簿动力学+做市商行为推断 | D_INFRA_RUNTIME | harvest待评估（likely_new） |  |
| CAND-HARVEST-1428 | Conformal Prediction 共形预测 | 分布无关收益预测区间+自适应共形ACI/EnbPI+在线VaR校准 | D_INFRA_RUNTIME | harvest待评估（likely_new） |  |
| CAND-HARVEST-1429 | Survival Analysis 生存分析 | Cox比例风险模型→止盈/止损时间预测+市场状态持续时间预测 | D_INFRA_RUNTIME | harvest待评估（likely_new） |  |
| CAND-HARVEST-1430 | Causal ML 深度补充 因果ML深度补充 | DML因子因果效应估计+Causal Forest+DoWhy反事实推演+因果发现 | D_INFRA_RUNTIME | harvest待评估（likely_new） |  |
| CAND-HARVEST-1431 | Learning System Bridge Declaration 学习系统桥接声明 | 知识注入9条路径+反馈4条路径+6条全局约束→流水线从被动执行走向自我成长 | D_INFRA_RUNTIME | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1432 | Mamba/SSM State Space Model Mamba/SSM状态空间模型 | 选择性扫描机制S6+O(L)线性复杂度+Prob-Mamba概率SSM+CMDMamba双层 | D_INFRA_RUNTIME | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1434 | Time-Series Conformal Prediction Enhancement TCP/DDCI/CP-VaR 时序保形预测增强 | 已合并至§29.16第5小节；TCP-RM残差记忆+DDCI双反馈+CP-VaR等价回测 | D_INFRA_RUNTIME | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1435 | A-Share Diffusion Model Data Augmentation A股扩散模型数据增强 | FWT检索增强扩散+GBM-Diffusion乘性噪声+InterDiff分类器无关引导 | D_INFRA_RUNTIME | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1448 | Alternative Data Source Health & Degradation Manager 另类数据源健康度与降级管理器 | 另类数据源健康度监控+降级策略+自动切换 | D_INFRA_RUNTIME | harvest待评估（likely_misplaced） |  |
| CAND-HARVEST-1449 | Hardware Accelerator 硬件加速器 | GPU/TPU/FPGA等异构硬件加速资源的统一管理、分配与性能监控 | D_INFRA_RUNTIME | harvest待评估（likely_new） |  |
| CAND-HARVEST-1450 | GPU Compute Pipeline Manager GPU计算管线管理器 | 管理GPU计算管线的任务调度、执行流编排与流水线并行优化 | D_INFRA_RUNTIME | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1451 | GPU Memory Transfer Optimizer GPU内存传输优化器 | 优化GPU与主机间数据传输效率、内存拷贝合并与异步传输策略 | D_INFRA_RUNTIME | harvest待评估（likely_new） |  |
| CAND-HARVEST-1452 | GPU Programming Abstraction Layer GPU编程抽象层 | 提供统一的GPU编程接口抽象，屏蔽底层硬件差异与驱动版本变更 | D_INFRA_RUNTIME | harvest待评估（likely_new） |  |
| CAND-HARVEST-1453 | GPU Resource Monitor GPU资源监控器 | 实时监控GPU资源使用率、显存占用、温度与功耗，触发阈值告警 | D_INFRA_RUNTIME | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1454 | GPU Inference Training Dynamic Allocator GPU推理训练动态分配器 | 动态分配GPU计算资源以平衡推理延迟敏感型与训练吞吐密集型工作负载 | D_INFRA_RUNTIME | harvest待评估（likely_new） |  |
| CAND-HARVEST-1455 | GPU Kernel Launch Optimizer GPU内核启动优化器 | 优化GPU内核启动参数配置、内核融合策略与执行网格分块方案 | D_INFRA_RUNTIME | harvest待评估（likely_new） |  |
| CAND-HARVEST-1456 | CPU Core Allocation Manager CPU核心分配管理器 | 管理CPU核心的亲和性绑定、核心隔离与动态分配调度策略 | D_INFRA_RUNTIME | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1457 | Single-Machine Concurrency Mode Optimizer 单机并发模式优化器 | 并发模式选择/并发度优化/资源争抢避免+并发性能监控 | D_INFRA_RUNTIME | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1458 | Inter-Process Communication Manager 进程间通信管理器 | 管理进程间通信通道的建立、消息序列化与通信性能监控 | D_INFRA_RUNTIME | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1459 | Thread Pool Manager 线程池管理器 | 管理线程池的创建、动态扩缩容与任务队列调度策略 | D_INFRA_RUNTIME | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1460 | System Startup Orchestrator 系统启动编排器 | 编排系统各组件的启动顺序、依赖等待与健康检查就绪验证 | D_INFRA_RUNTIME | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1461 | Environment Variable Manager 环境变量管理器 | 管理环境变量的定义、分层继承、加密存储与运行时注入 | D_INFRA_RUNTIME | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1462 | Process Daemon Monitor 进程守护监控器 | 监控守护进程的健康状态，执行异常进程自动重启与告警 | D_INFRA_RUNTIME | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1463 | Graceful Shutdown Coordinator 优雅关闭协调器 | 系统优雅关闭的任务完成等待与状态保存协调 | D_INFRA_RUNTIME | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1465 | Communication Protocol Adapter 通信协议适配器 | 适配多种通信协议之间的转换，提供统一通信抽象层 | D_INFRA_RUNTIME | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1466 | Serialization Performance Optimizer 序列化性能优化器 | 优化数据序列化与反序列化性能，选择最优序列化方案 | D_INFRA_RUNTIME | harvest待评估（likely_new） |  |
| CAND-HARVEST-1467 | Multi-Protocol Network Adapter 多协议网络适配器 | 适配多种网络协议的连接管理，提供统一网络通信接口 | D_INFRA_RUNTIME | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1468 | Multi-Modal Input Router 多模态输入路由 | 语音/文字/文件输入智能路由分发 | D_INFRA_RUNTIME | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1469 | Request Retry Manager 请求重试管理器 | 管理请求的重试策略，支持指数退避、抖动与熔断联动 | D_INFRA_RUNTIME | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1470 | Data Transfer Validator 数据传输校验器 | 校验数据传输的完整性、顺序性与校验和一致性 | D_INFRA_RUNTIME | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1471 | WebSocket Reconnection WebSocket断线重连 | 前端断线检测与自动重连 | D_INFRA_RUNTIME | harvest待评估（likely_new） |  |
| CAND-HARVEST-1472 | Cross-Origin Resource Sharing Manager 跨域资源共享管理器 | 管理跨域资源共享策略，配置允许来源、方法与头部白名单 | D_INFRA_RUNTIME | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1473 | Configuration Manager 配置管理器 | 管理运行时配置的集中存储、分发与版本控制，支撑配置热更新与灰度发布 | D_INFRA_RUNTIME | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1474 | Runtime Configuration Validator 运行时配置校验器 | 校验运行时配置的格式合法性、逻辑一致性与类型安全 | D_INFRA_RUNTIME | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1475 | Configuration Change Notifier 配置变更通知器 | 实时推送配置变更事件，通知订阅者更新运行时配置 | D_INFRA_RUNTIME | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1476 | Configuration Diff Detector 配置差异检测器 | 检测配置版本间的差异，生成结构化的配置变更对比报告 | D_INFRA_RUNTIME | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1477 | Configuration Merge Engine 配置合并引擎 | 合并多层配置源，按优先级策略解决配置冲突 | D_INFRA_RUNTIME | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1478 | Environment Configuration Layering Manager 环境配置分层管理器 | 管理开发/测试/生产等多环境的分层配置与覆盖策略 | D_INFRA_RUNTIME | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1479 | Configuration Encryption Manager 配置加密管理器 | 管理敏感配置的加解密，支持密钥轮换与访问控制 | D_INFRA_RUNTIME | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1480 | Configuration Hot Update Engine 配置热更新引擎 | 在不停机情况下动态更新运行时配置，确保配置实时生效 | D_INFRA_RUNTIME | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1481 | Configuration Dependency Mapper 配置依赖映射器 | 映射配置项之间的依赖关系，检测配置变更的级联影响 | D_INFRA_RUNTIME | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1482 | Configuration Version Management & Rollback Framework 配置版本管理与回滚框架 | 配置变更的版本控制、diff对比与一键回滚 | D_INFRA_RUNTIME | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1483 | Configuration Validation Engine 配置校验引擎 | 配置变更前的格式校验、逻辑一致性校验与冲突检测 | D_INFRA_RUNTIME | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1484 | Unified Feature Toggle Framework 统一功能开关框架 | 各域新功能的特性开关统一管理与灰度控制 | D_INFRA_RUNTIME | harvest待评估（likely_new） |  |
| CAND-HARVEST-1485 | Resource Scheduler 资源调度器 | 运行时计算资源的动态分配、优先级抢占调度与资源回收 | D_INFRA_RUNTIME | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1486 | Elastic Scaling Manager 弹性伸缩管理器 | 基于负载指标动态调整服务实例数量，实现水平弹性伸缩 | D_INFRA_RUNTIME | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1487 | Multi-Region Collaboration Manager 多区域协同管理器 | 管理多区域部署的服务协同、数据同步与区域间路由策略 | D_INFRA_RUNTIME | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1488 | Request Forwarding & Load Balancer 请求转发与负载均衡器 | 请求转发+负载均衡+健康检查+故障转移 | D_INFRA_RUNTIME | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1489 | Service Discovery Registrar 服务发现注册器 | 管理服务实例的自动注册、健康状态上报与服务发现查询 | D_INFRA_RUNTIME | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1490 | Container Orchestrator 容器编排器 | 管理容器生命周期、调度策略、服务网络与存储挂载编排 | D_INFRA_RUNTIME | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1491 | Network Policy Manager 网络策略管理器 | 定义并执行容器间网络访问控制策略与网络分段隔离规则 | D_INFRA_RUNTIME | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1492 | Traffic Shaper 流量整形器 | 对进出流量实施速率限制、带宽分配与流量优先级控制 | D_INFRA_RUNTIME | harvest待评估（likely_new） |  |
| CAND-HARVEST-1493 | Load Balancing Strategy Engine 负载均衡策略引擎 | 执行负载均衡策略决策，支持轮询/加权/最少连接等算法 | D_INFRA_RUNTIME | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1494 | Container Image Cache Manager 容器镜像缓存管理器 | 管理容器镜像的分层缓存、预热拉取与镜像垃圾回收 | D_INFRA_RUNTIME | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1495 | Container Resource Isolator 容器资源隔离器 | 实施容器间的CPU/内存/IO资源隔离与cgroup限制策略 | D_INFRA_RUNTIME | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1496 | Service Rate Limiter 服务限流器 | 实施服务级别、用户级别与API级别的请求速率限制与配额管理 | D_INFRA_RUNTIME | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1497 | Service Dependency Health Checker 服务依赖健康检查器 | 检查服务依赖链路的健康状况，逐级验证上下游服务可用性 | D_INFRA_RUNTIME | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1498 | Runtime Infrastructure Self-Checker 运行时基础设施自检器 | 执行基础设施的全面自检，生成健康报告与异常诊断 | D_INFRA_RUNTIME | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1499 | Live Data to Research Domain Feedback Channel 实盘数据→研究域反馈通道 | 实盘数据到研究域的反馈机制+监控评估→研究域洞察反馈+反馈闭环 | D_INFRA_RUNTIME | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1500 | Message Queue Manager 消息队列管理器 | 管理消息队列的拓扑定义、消费者组协调与消息投递保证 | D_INFRA_RUNTIME | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1501 | Distributed Lock Manager 分布式锁管理器 | 提供分布式环境下的互斥锁、读写锁与锁超时自动释放机制 | D_INFRA_RUNTIME | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1502 | Cache Warmup Manager 缓存预热管理器 | 管理系统启动时缓存数据的预先加载与热点数据预测填充 | D_INFRA_RUNTIME | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1503 | Cold Start Optimizer 冷启动优化器 | 优化服务冷启动速度，减少初始化延迟与首次请求响应时间 | D_INFRA_RUNTIME | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1504 | Factor Warmup Manager 因子预热管理器 | 管理因子计算引擎的预热加载，减少首次计算延迟 | D_INFRA_RUNTIME | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1505 | Signal Warmup Manager 信号预热管理器 | 管理信号生成管线的预热初始化，确保实时信号就绪 | D_INFRA_RUNTIME | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1506 | Real-Time Data Warmer 实时数据预热器 | 预热实时数据接入通道，预加载高频数据源连接与会话 | D_INFRA_RUNTIME | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1507 | Model Warmup Manager 模型预热管理器 | 管理模型的预加载到内存/显存，减少首次推理延迟 | D_INFRA_RUNTIME | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1508 | Inference Engine Warmer 推理引擎预热器 | 预热推理引擎的计算图与执行环境，加速首Token生成 | D_INFRA_RUNTIME | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1509 | Cache Data Preloader 缓存数据预加载器 | 在系统启动时预加载热点缓存数据，减少缓存击穿风险 | D_INFRA_RUNTIME | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1510 | Data Compression Manager 数据压缩管理器 | 管理传输数据的压缩策略，平衡压缩率与CPU开销 | D_INFRA_RUNTIME | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1511 | Inter-Layer Data Format Converter & Validator 层间数据格式转换与校验器 | 各层数据格式定义+格式转换器+格式校验+格式版本管理 | D_INFRA_RUNTIME | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1512 | Data Format Version Coordinator 数据格式版本协调器 | 协调不同服务版本间的数据格式兼容性，管理格式版本演进 | D_INFRA_RUNTIME | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1513 | Data Transformation Performance Optimizer 数据转换性能优化器 | 优化数据转换管线的处理性能，减少格式转换延迟 | D_INFRA_RUNTIME | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1514 | Batch Data Processor 批量数据处理器 | 管理批量数据的聚合处理、窗口计算与批量写入优化 | D_INFRA_RUNTIME | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1515 | Real-Time Data Stream Manager 实时数据流管理器 | 管理实时数据流的接入、背压控制与流式处理编排 | D_INFRA_RUNTIME | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1516 | Data Buffer Pool Manager 数据缓冲池管理器 | 管理数据缓冲池的内存分配、容量控制与溢出处理策略 | D_INFRA_RUNTIME | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1517 | Data Source Star Rating Dynamic Updater 数据源星级评分动态更新器 | 基于实际表现自动更新数据源星级评分 | D_INFRA_RUNTIME | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1518 | Data Migration Script Generator 数据迁移脚本生成器 | 基于Schema版本差异自动生成数据迁移脚本与回滚脚本 | D_INFRA_RUNTIME | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1519 | Database Schema Synchronizer 数据库Schema同步器 | 同步应用Schema定义与数据库实际Schema，检测差异并生成DDL | D_INFRA_RUNTIME | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1520 | Field Mapping Converter 字段映射转换器 | 执行不同Schema间的字段映射与数据转换，支持复杂映射规则 | D_INFRA_RUNTIME | harvest待评估（likely_new） |  |
| CAND-HARVEST-1521 | Data Transformation Pipeline Orchestrator 数据转换管线编排器 | 编排多步骤数据转换流程，管理数据在各个转换阶段间的流转 | D_INFRA_RUNTIME | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1522 | Data Aggregation View Manager 数据聚合视图管理器 | 管理数据聚合视图的定义、物化刷新与查询优化 | D_INFRA_RUNTIME | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1523 | Telemetry Four-Stream Unified Collector 遥测四流统一采集器 | 统一采集指标/日志/追踪/事件四类遥测数据流，标准化格式输出 | D_INFRA_RUNTIME | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1524 | Request Chain Tracer 请求链追踪器 | 端到端请求链路的分布式追踪、Span关联与延迟瓶颈定位 | D_INFRA_RUNTIME | harvest待评估（likely_new） |  |
| CAND-HARVEST-1525 | MCP Sentinel System Monitor MCP哨兵系统监控器 | 基于MCP协议的哨兵式系统健康监控、异常探测与自动告警 | D_INFRA_RUNTIME | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1526 | Monitoring Data Aggregator 监控数据聚合器 | 聚合多源监控数据，执行数据去重、降采样与时序对齐 | D_INFRA_RUNTIME | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1527 | Real-Time Alert Engine 实时告警引擎 | 基于规则引擎实时评估监控指标，触发分级告警通知 | D_INFRA_RUNTIME | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1528 | Alert Silence Manager 告警静默管理器 | 管理告警静默窗口、维护期抑制规则与告警去重合并 | D_INFRA_RUNTIME | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1529 | Alert Escalation Strategy Engine 告警升级策略引擎 | 定义并执行告警升级策略，按时间和严重程度逐级升级 | D_INFRA_RUNTIME | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1530 | Metric Anomaly Detector 指标异常检测器 | 基于统计模型检测指标异常波动，识别潜在系统问题 | D_INFRA_RUNTIME | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1531 | Privacy-Preserving Computation 隐私保护计算 | 隐私数据的安全计算执行环境，基于TEE/MPC等隐私增强技术方案 | D_INFRA_RUNTIME | harvest待评估（likely_new） |  |
| CAND-HARVEST-1532 | Data Sovereignty Manager 数据主权管理器 | 数据存储位置合规控制、跨区域数据传输管控与主权策略执行 | D_INFRA_RUNTIME | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1533 | Clock Sync Service 时钟同步服务 | 分布式系统时钟同步、时间戳一致性与时钟漂移补偿保障 | D_INFRA_RUNTIME | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1534 | Code Security Static Analyzer 代码安全静态分析器 | 静态扫描代码安全漏洞、敏感信息泄露与CWE合规性问题 | D_INFRA_RUNTIME | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1535 | Document Search Indexer 文档搜索索引器 | 建立文档全文搜索索引，支持模糊匹配与语义搜索能力 | D_INFRA_RUNTIME | harvest待评估（likely_new） |  |
| CAND-HARVEST-1536 | Module Version Dependency Resolver 模块版本依赖解析器 | 解析模块间版本依赖约束，执行版本兼容性校验与冲突检测 | D_INFRA_RUNTIME | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1537 | Code Structure Visualizer 代码结构可视化器 | 生成代码结构拓扑图、类层次关系图与模块组织架构图 | D_INFRA_RUNTIME | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1538 | Package Dependency Graph Generator 包依赖图生成器 | 自动生成包级别依赖关系的有向无环图，标注依赖方向与强度 | D_INFRA_RUNTIME | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1539 | Code Complexity Analyzer 代码复杂度分析器 | 分析代码圈复杂度、认知复杂度与可维护性指数，生成复杂度报告 | D_INFRA_RUNTIME | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1540 | Code Duplication Detector 代码重复检测器 | 检测代码库中的重复代码片段，计算相似度并生成去重建议 | D_INFRA_RUNTIME | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1541 | Code Change Impact Analyzer 代码变更影响分析器 | 分析代码变更的影响范围，追踪变更传播路径与受影响模块 | D_INFRA_RUNTIME | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1542 | Automated Code Reviewer 自动代码审查器 | 自动执行代码审查规则，检测代码异味、反模式与最佳实践偏离 | D_INFRA_RUNTIME | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1543 | Code Standard Enforcer 代码规范强制执行器 | 强制执行代码风格规范、命名约定与格式化规则的自动化工具 | D_INFRA_RUNTIME | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1544 | Architecture Compliance Checker 架构合规检查器 | 自动检查代码实现是否符合架构设计约束、分层规则与依赖方向 | D_INFRA_RUNTIME | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1545 | Technical Debt Tracker 技术债务追踪器 | 量化追踪技术债务指标，生成偿还优先级排序与改进建议 | D_INFRA_RUNTIME | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1546 | Architecture Evolution Planner 架构演进规划器 | 规划架构演进路径，评估架构变更风险与迁移成本 | D_INFRA_RUNTIME | harvest待评估（likely_new） |  |
| CAND-HARVEST-1547 | Code Template Engine 代码模板引擎 | 基于模板和参数生成标准化代码骨架，支持条件逻辑与循环 | D_INFRA_RUNTIME | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1548 | DAO Layer Code Generator DAO层代码生成器 | 基于数据模型自动生成DAO层CRUD代码与查询方法 | D_INFRA_RUNTIME | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1549 | REST API Code Generator REST API代码生成器 | 基于接口契约自动生成REST API控制器代码与路由配置 | D_INFRA_RUNTIME | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1550 | Test Code Generator 测试代码生成器 | 基于接口契约自动生成单元测试与集成测试代码骨架 | D_INFRA_RUNTIME | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1551 | Configuration Code Generator 配置代码生成器 | 基于配置Schema自动生成类型安全的配置加载代码 | D_INFRA_RUNTIME | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1552 | Interface Mock Generator 接口Mock生成器 | 基于接口定义自动生成Mock实现，支持行为配置与返回值预设 | D_INFRA_RUNTIME | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1553 | Data Model Generator 数据模型生成器 | 基于Schema定义自动生成数据模型类、序列化与反序列化代码 | D_INFRA_RUNTIME | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1554 | Validation Rule Generator 验证规则生成器 | 基于Schema约束自动生成数据验证规则代码与校验逻辑 | D_INFRA_RUNTIME | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1555 | Error Handling Code Generator 错误处理代码生成器 | 自动生成统一的错误处理、异常映射与错误码管理代码 | D_INFRA_RUNTIME | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1556 | API Version Manager API版本管理器 | 管理API版本生命周期，执行版本兼容性检查与废弃策略编排 | D_INFRA_RUNTIME | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1557 | Module Interface Contract Manager 模块接口契约管理器 | 模块间接口定义+接口版本管理+接口兼容性验证+接口文档自动生成 | D_INFRA_RUNTIME | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1558 | SDK Auto Generator SDK自动生成器 | 基于接口契约自动生成多语言SDK客户端代码与使用文档 | D_INFRA_RUNTIME | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1559 | API Documentation Synchronizer API文档同步器 | 自动同步API实现与文档描述，检测文档不一致并触发更新 | D_INFRA_RUNTIME | harvest待评估（likely_new） |  |
| CAND-HARVEST-1560 | Endpoint Response Format Validator 端点响应格式校验器 | 校验API端点响应是否匹配契约定义的格式与类型约束 | D_INFRA_RUNTIME | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1561 | API Version Compatibility Detector API版本兼容检测器 | 检测API新版本与旧版本的向后兼容性，标记Breaking Changes | D_INFRA_RUNTIME | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1562 | Return Value Performance Monitor 返回值性能监控器 | 监控API返回值的大小、序列化耗时与传输延迟性能指标 | D_INFRA_RUNTIME | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1563 | Inter-Module Communication Protocol Manager 模块间通信协议管理器 | 管理模块间通信协议的定义、版本协商与协议适配 | D_INFRA_RUNTIME | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1564 | Module Lifecycle Manager 模块生命周期管理器 | 管理模块从加载、初始化、运行到卸载的完整生命周期状态 | D_INFRA_RUNTIME | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1565 | Module Registry 模块注册中心 | 维护模块的注册信息，提供模块发现与元数据查询服务 | D_INFRA_RUNTIME | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1566 | Module Dependency Injector 模块依赖注入器 | 管理模块间的依赖注入，执行构造函数注入与属性注入绑定 | D_INFRA_RUNTIME | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1567 | Module Configuration Aggregator 模块配置聚合器 | 聚合各模块的分散配置为统一配置视图，处理配置覆盖与合并 | D_INFRA_RUNTIME | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1568 | Module Health Checker 模块健康检查器 | 周期性探测各模块的健康状态，执行活性检查与就绪检查 | D_INFRA_RUNTIME | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1569 | Module Hot Update Manager 模块热更新管理器 | 管理模块的热更新流程，支持不停机替换与灰度切换 | D_INFRA_RUNTIME | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1570 | Module Feature Toggle Manager 模块功能开关管理器 | 管理模块级功能开关，支持运行时动态启用或禁用模块功能 | D_INFRA_RUNTIME | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1571 | Plugin System Manager 插件系统管理器 | 管理插件系统的加载、隔离与生命周期，支持动态扩展机制 | D_INFRA_RUNTIME | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1572 | Module Sandbox Isolator 模块沙箱隔离器 | 为模块提供沙箱执行环境，限制资源访问与权限边界 | D_INFRA_RUNTIME | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1573 | Module Metrics Collector 模块度量采集器 | 采集各模块的运行度量指标，包括调用量、延迟与错误率 | D_INFRA_RUNTIME | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1574 | Module Log Aggregator 模块日志聚合器 | 聚合各模块的分散日志，统一格式化与日志级别管理 | D_INFRA_RUNTIME | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1575 | Module Exception Boundary Manager 模块异常边界管理器 | 定义模块异常边界，防止异常跨模块传播导致级联故障 | D_INFRA_RUNTIME | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1576 | Module Performance Profiler 模块性能分析器 | 对模块运行时性能进行采样分析，识别热点路径与瓶颈 | D_INFRA_RUNTIME | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1577 | Module Documentation Indexer 模块文档索引器 | 索引各模块的技术文档，支持关键词搜索与文档关联查询 | D_INFRA_RUNTIME | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1578 | Module Test Runner 模块测试运行器 | 编排模块级测试的执行，支持并行测试与依赖排序 | D_INFRA_RUNTIME | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1579 | Global Dependency Graph Calculator 全局依赖图计算器 | 计算全系统模块间的完整依赖图，分析依赖方向与深度 | D_INFRA_RUNTIME | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1580 | Circular Dependency Detector 循环依赖检测器 | 检测模块间的循环依赖，定位循环路径并生成解除建议 | D_INFRA_RUNTIME | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1581 | Dependency Version Lock Manager 依赖版本锁定管理器 | 管理依赖版本的锁定策略，生成锁文件并检测未授权变更 | D_INFRA_RUNTIME | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1582 | Dependency Security Vulnerability Scanner 依赖安全漏洞扫描器 | 扫描依赖库的已知安全漏洞，输出CVE风险等级与修复建议 | D_INFRA_RUNTIME | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1583 | Transitive Dependency Analyzer 传递依赖分析器 | 分析依赖的传递链路，识别间接依赖的版本冲突与风险 | D_INFRA_RUNTIME | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1584 | Dependency Conflict Resolver 依赖冲突解决器 | 检测并解决多个依赖之间的版本冲突，执行依赖仲裁策略 | D_INFRA_RUNTIME | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1585 | Dependency Upgrade Compatibility Checker 依赖升级兼容性检查器 | 检查依赖升级后的API兼容性与行为变更影响 | D_INFRA_RUNTIME | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1586 | Dependency Graph Visualization Renderer 依赖图可视化渲染器 | 将全局依赖图渲染为交互式可视化图形，支持缩放与过滤 | D_INFRA_RUNTIME | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1587 | Regression Test Orchestrator 回归测试编排器 | 编排回归测试套件的执行顺序、并行测试与测试结果汇总 | D_INFRA_RUNTIME | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1588 | Test Coverage Tracker 测试覆盖率追踪器 | 追踪代码测试覆盖率的行/分支/条件覆盖度与覆盖率趋势 | D_INFRA_RUNTIME | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1589 | Document Template Engine 文档模板引擎 | 基于模板生成标准化文档，支持模板变量替换与条件渲染 | D_INFRA_RUNTIME | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1590 | Document Version Manager 文档版本管理器 | 管理文档版本与代码版本同步，维护文档版本树 | D_INFRA_RUNTIME | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1591 | Terminology Consistency Validator 术语一致性校验器 | 校验文档中术语使用的一致性，检测同义异名与异义同名 | D_INFRA_RUNTIME | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1592 | Specification Automation Checker 规范自动化检查器 | 自动检查文档内容是否满足规范模板的结构完整性要求 | D_INFRA_RUNTIME | harvest待评估（likely_new） |  |
| CAND-HARVEST-1593 | Document Link Validator 文档链接验证器 | 验证文档间交叉引用的链接有效性，检测死链与过期引用 | D_INFRA_RUNTIME | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1594 | Knowledge Base Indexer 知识库索引器 | 建立知识库的结构化索引，支持全文检索与语义查询 | D_INFRA_RUNTIME | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1595 | Strategy Execution Plan Optimizer 策略执行计划优化器 | 优化策略执行计划的并行度、执行顺序与资源分配 | D_INFRA_RUNTIME | harvest待评估（likely_new） |  |
| CAND-HARVEST-1596 | Strategy Backtesting Infrastructure 策略回测基础设施 | 提供策略回测所需的计算资源、数据管道与结果存储基础设施 | D_INFRA_RUNTIME | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1598 | Strategy Portfolio Simulator 策略组合模拟器 | 模拟多个策略组合的运行效果，评估组合风险与收益 | D_INFRA_RUNTIME | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1599 | Strategy Parameter Tuning Engine 策略参数调优引擎 | 自动化调优策略超参数，执行网格搜索与贝叶斯优化 | D_INFRA_RUNTIME | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1600 | Strategy Correlation Matrix Calculator 策略相关性矩阵计算器 | 计算多策略收益率序列的相关性矩阵，识别策略间相关风险 | D_INFRA_RUNTIME | harvest待评估（likely_new） |  |
| CAND-HARVEST-1601 | Resource Load Balancer 资源负载均衡器 | 开发资源分配与负载均衡 | D_INFRA_RUNTIME | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1602 | Task Priority Scheduler 任务优先级调度器 | 基于任务优先级、截止时间与资源需求综合调度任务执行顺序 | D_INFRA_RUNTIME | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1603 | Resource Reservation Manager 资源预约管理器 | 管理计算资源的预先预约、时间槽分配与资源预留策略 | D_INFRA_RUNTIME | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1604 | Resource Quota Manager 资源配额管理器 | 管理各项目/团队/用户的资源配额分配与使用量统计 | D_INFRA_RUNTIME | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1605 | Resource Usage Auditor 资源使用审计器 | 审计资源使用记录的合规性，生成资源使用报告与异常标记 | D_INFRA_RUNTIME | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1606 | Workflow Version Management 工作流版本管理 | 工作流定义的版本控制与回滚 | D_INFRA_RUNTIME | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1607 | Phase Synchronization Coordinator 阶段同步协调器 | 协调多个开发阶段的同步进度，确保阶段间依赖按时交付 | D_INFRA_RUNTIME | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1608 | Cross-Phase State Propagator 跨阶段状态传递器 | 管理开发状态在阶段间的传递与转换，确保状态一致性 | D_INFRA_RUNTIME | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1609 | Milestone Dependency Validator 里程碑依赖校验器 | 校验里程碑之间的依赖关系是否满足，检测依赖阻塞风险 | D_INFRA_RUNTIME | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1610 | Deliverable Version Tracker 交付物版本追踪器 | 追踪各阶段交付物的版本演进，维护版本树与变更日志 | D_INFRA_RUNTIME | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1611 | Phase Retrospective Analyzer 阶段回顾分析器 | 分析阶段执行数据，生成回顾报告与改进建议 | D_INFRA_RUNTIME | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1612 | Continuous Improvement Engine 持续改进引擎 | 基于历史数据驱动持续改进流程，自动生成优化建议 | D_INFRA_RUNTIME | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1613 | Schedule Conflict Detector 时间表冲突检测器 | 任务时间重叠/资源冲突自动告警+冲突解决建议 | D_INFRA_RUNTIME | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1614 | Development Plan Visualizer 开发计划可视化器 | 可视化渲染开发计划的时间线与里程碑，支持甘特图与看板视图 | D_INFRA_RUNTIME | harvest待评估（likely_new） |  |
| CAND-HARVEST-1615 | Resource Timeline Manager 资源时间线管理器 | 管理资源使用的时间线规划，检测资源时间冲突与过载 | D_INFRA_RUNTIME | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1616 | Iteration Cycle Tracker 迭代周期追踪器 | 追踪迭代周期的执行进度、燃尽图与交付速率度量 | D_INFRA_RUNTIME | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1617 | Panel Layout Engine 面板布局引擎 | 运行时面板布局的编排计算、视图排列与响应式自适应调整 | D_INFRA_RUNTIME | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1618 | Region Collapse Manager 区域折叠管理器 | 管理面板区域的折叠/展开状态、动画过渡与可见性控制 | D_INFRA_RUNTIME | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1619 | Dependency Visualizer 依赖可视化器 | 可视化渲染模块间依赖关系图，支持交互式探索与依赖路径追踪 | D_INFRA_RUNTIME | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1620 | Deployment Topology Manager 部署拓扑管理器 | 管理部署拓扑的定义、编排与拓扑变更的自动化执行 | D_INFRA_RUNTIME | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1621 | Feature Lifecycle Manager 功能生命周期管理器 | 管理功能从实验、灰度到全量发布的生命周期状态转换 | D_INFRA_RUNTIME | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1622 | Domain-Driven Design Validator 领域驱动设计校验器 | 校验代码实现是否符合领域驱动设计约束，检查聚合边界与限界上下文 | D_INFRA_RUNTIME | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1623 | Architecture Recommendation Engine 架构推荐引擎 | 基于项目特征推荐最佳架构模式与技术栈选型方案 | D_INFRA_RUNTIME | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1624 | Infrastructure Topology Visualizer 基础设施拓扑可视化器 | 可视化渲染基础设施的物理与逻辑拓扑布局 | D_INFRA_RUNTIME | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1625 | Application State Snapshotter 应用状态快照器 | 创建应用运行时状态的完整快照，支持状态恢复与回放 | D_INFRA_RUNTIME | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1626 | Session Persistence Manager 会话持久化管理器 | 管理用户会话的持久化存储、过期清理与会话恢复机制 | D_INFRA_RUNTIME | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1627 | User Preference Synchronizer 用户偏好同步器 | 跨设备同步用户偏好设置，解决冲突合并与一致性维护 | D_INFRA_RUNTIME | harvest待评估（likely_new） |  |
| CAND-HARVEST-1628 | Multi-Device State Coordinator 多端状态协调器 | 协调多终端间的状态一致，执行乐观更新与冲突解决 | D_INFRA_RUNTIME | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1629 | Conversation Context Compressor 对话上下文压缩 | 长对话上下文智能压缩与摘要 | D_INFRA_RUNTIME | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1754 | Canary Dependency Mapper 金丝雀依赖映射器 | 金丝雀发布依赖映射 | D_INFRA_RUNTIME | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1755 | Blue-Green Dependency Mapper 蓝绿依赖映射器 | 蓝绿部署依赖映射 | D_INFRA_RUNTIME | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1756 | AB Test Dependency Mapper AB测试依赖映射器 | AB测试依赖映射 | D_INFRA_RUNTIME | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1757 | Traffic Mirror Mapper 流量镜像映射器 | 流量镜像依赖映射 | D_INFRA_RUNTIME | harvest待评估（likely_new） |  |
| CAND-HARVEST-1758 | Progressive Delivery Pre-check Enhancer 渐进交付前置检查增强 | 渐进交付前置检查增强 | D_INFRA_RUNTIME | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1759 | Traffic Mirror Dependency Mapping Enhancer 流量镜像依赖映射增强 | 流量镜像依赖映射增强 | D_INFRA_RUNTIME | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1760 | Policy Conflict Auto Detector 策略冲突自动检测器 | 策略冲突自动检测器 | D_INFRA_RUNTIME | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1804 | VaR Recalculation Scheduler VaR重算调度器 | VaR重算调度器：事件触发+定时重算+增量计算 | D_INFRA_RUNTIME | harvest待评估（likely_misplaced） |  |
| CAND-HARVEST-2087 | Collection Scheduler 采集调度器 | §11.2 S0组件接收C-022质量报告调整数据源采集优先级 | D_INFRA_RUNTIME | harvest待评估（likely_misplaced） |  |
| CAND-HARVEST-2111 | Task Orchestration 任务编排 | 编排Agent技能任务编排ACTIVE | D_INFRA_RUNTIME | harvest待评估（likely_misplaced） |  |
| CAND-HARVEST-2119 | Strategy Health Score 策略健康评分 | 归因Agent技能策略健康评分ACTIVE | D_INFRA_RUNTIME | harvest待评估（likely_misplaced） |  |
| CAND-HARVEST-2120 | Circuit Breaker Trigger 熔断触发 | 风控Agent技能熔断触发ACTIVE | D_INFRA_RUNTIME | harvest待评估（likely_misplaced） |  |
| CAND-HARVEST-2145 | Circuit Breaker 熔断器 | 熔断器Circuit Breaker Agent失败阈值熔断时间 | D_INFRA_RUNTIME | harvest待评估（likely_misplaced） |  |
| CAND-HARVEST-2173 | Working Memory 工作记忆 | 工作记忆Working Memory Redis内存单次会话 | D_INFRA_RUNTIME | harvest待评估（likely_new） |  |
| CAND-HARVEST-2205 | Redis Redis内存数据库 | Redis消息总线进程内函数调用持久化发布订阅 | D_INFRA_RUNTIME | harvest待评估（likely_new） |  |
| CAND-HARVEST-2206 | SQLite SQLite嵌入式数据库 | SQLite情景记忆温区语义记忆永久存储 | D_INFRA_RUNTIME | harvest待评估（likely_new） |  |
| CAND-HARVEST-2207 | Parquet Parquet列式存储格式 | Parquet语义记忆永久存储冷存储归档 | D_INFRA_RUNTIME | harvest待评估（likely_new） |  |
| CAND-HARVEST-2249 | Multi-Dimensional Quantitative Health Indicator 多维量化健康指标 | / strategy-health-score / 多维量化健康指标(Sharpe+IC+MaxDD+Calmar加权) / ACTIVE / | D_INFRA_RUNTIME | harvest待评估（likely_misplaced） |  |
| CAND-HARVEST-2263 | strategy-health-score 策略健康评分 | / strategy-health-score / 多维量化健康指标(Sharpe+IC+MaxDD+Calmar加权) / ACTIVE / | D_INFRA_RUNTIME | harvest待评估（likely_misplaced） |  |
| CAND-HARVEST-2285 | Redis Pub/Sub Redis发布订阅 | / JSON-RPC 2.0 over HTTP / JSON-RPC 2.0 over Redis Pub/Sub / 保留JSON-RPC 2.0语义，传输层替换为Redis / | D_INFRA_RUNTIME | harvest待评估（likely_new） |  |
| CAND-HARVEST-2344 | Success Metrics 成功指标 | 成功指标11项Agent决策延迟到协作成功率到自治边界违规次数到LLM路由成本控制率到自反Agent反思有效率等 | D_INFRA_RUNTIME | harvest待评估（likely_misplaced） |  |
| CAND-HARVEST-2433 | L10 Audit Trail 审计追踪与零知识审计 | C轨L10层审计追踪与零知识审计 | D_INFRA_RUNTIME | harvest待评估（likely_misplaced） |  |
| CAND-HARVEST-2449 | Audit Evidence Chain Architecture 审计证据链架构 | 三层审计架构对标EU AI Act Article 12 | D_INFRA_RUNTIME | harvest待评估（likely_misplaced） |  |
| CAND-HARVEST-2450 | Three Layer Audit Architecture 三层审计架构 | L1事件完整性+L2集合完整性+L3外部可验证性 | D_INFRA_RUNTIME | harvest待评估（likely_misplaced） |  |
| CAND-HARVEST-2451 | Hash Chain Audit 哈希链审计 | L1事件完整性SHA-256链式哈希 | D_INFRA_RUNTIME | harvest待评估（likely_misplaced） |  |
| CAND-HARVEST-2452 | Merkle Tree Audit Merkle树审计 | L2集合完整性日/周/月批量完整性证明 | D_INFRA_RUNTIME | harvest待评估（likely_misplaced） |  |
| CAND-HARVEST-2470 | Zero Knowledge Audit 零知识审计 | 可证明合规但不暴露策略细节的审计机制 | D_INFRA_RUNTIME | harvest待评估（likely_misplaced） |  |
| CAND-HARVEST-2477 | ZKP Circuit Library ZKP电路库 | zkCA架构组件参与率/自交易/持仓限额/操纵检测证明 | D_INFRA_RUNTIME | harvest待评估（likely_misplaced） |  |
| CAND-HARVEST-2501 | AI Training Data Audit AI训练数据审计 | 确保训练数据不含内幕信息 | D_INFRA_RUNTIME | harvest待评估（likely_misplaced） |  |
| CAND-HARVEST-2510 | Operation Process Audit 操作流程审计 | 关键操作流程自动化审计 | D_INFRA_RUNTIME | harvest待评估（likely_misplaced） |  |
| CAND-HARVEST-2585 | Audit Log 审计日志 | 交易审计+决策审计+数据访问审计+AI调用审计+系统变更审计 | D_INFRA_RUNTIME | harvest待评估（likely_misplaced） |  |
| CAND-HARVEST-2746 | Trading Audit Log 交易审计日志 | 审计日志每笔订单的完整生命周期≥7年 | D_INFRA_RUNTIME | harvest待评估（likely_misplaced） |  |
| CAND-HARVEST-2747 | Decision Audit Log 决策审计日志 | 审计日志每个决策的信号来源+推理过程≥3年 | D_INFRA_RUNTIME | harvest待评估（likely_misplaced） |  |
| CAND-HARVEST-2748 | Data Access Audit Log 数据访问审计日志 | 审计日志每次L3/L4数据访问记录≥1年 | D_INFRA_RUNTIME | harvest待评估（likely_misplaced） |  |
| CAND-HARVEST-2749 | AI Call Audit Log AI调用审计日志 | 审计日志每次LLM调用的脱敏前后数据≥1年 | D_INFRA_RUNTIME | harvest待评估（likely_misplaced） |  |
| CAND-HARVEST-2750 | System Change Audit Log 系统变更审计日志 | 审计日志配置变更/参数修改/权限变更≥1年 | D_INFRA_RUNTIME | harvest待评估（likely_misplaced） |  |
| CAND-HARVEST-3003 | AI自治行为审计 AI Autonomous Behavior Audit | 审计AI决策自治分类判定 | D_INFRA_RUNTIME | harvest待评估（likely_misplaced） |  |
| CAND-HARVEST-3052 | boundary_audit.py 自治行为审计 | 审计AI自治行为是否越界 | D_INFRA_RUNTIME | harvest待评估（likely_misplaced） |  |
| CAND-HARVEST-3376 | 熔断器模式 Circuit Breaker Pattern | / 熔断器模式 / 5次失败/60秒→OPEN(全拒)→30秒HALF-OPEN(探针)→CLOSED / OWASP ASI08 / Netflix Hystrix / | D_INFRA_RUNTIME | harvest待评估（likely_misplaced） |  |
| CAND-HARVEST-3532 | asymmetric_audit.py 非对称审计 | DD-SEC-002归入AP非对称审计是自治审计 | D_INFRA_RUNTIME | harvest待评估（likely_misplaced） |  |
| CAND-HARVEST-3576 | 定时熔断 Timer Circuit Breaker | / 定时熔断 / <1ms / 交易时段核心进程无心跳>5秒 / 基础设施层 / | D_INFRA_RUNTIME | harvest待评估（likely_misplaced） |  |
| CAND-HARVEST-3581 | L4审计隔离 L4 Audit Isolation | / L4 审计隔离 / 否决日志独立存储，策略模块不可写 / 不可篡改审计链(HC-RISK-05) / | D_INFRA_RUNTIME | harvest待评估（likely_misplaced） |  |
| CAND-HARVEST-3613 | 审计可追溯缺口 Audit Traceability Gap | 保障缺口管理AI决策链可能不透明vs每笔决策可溯源C-030决策可解释性+审计链 | D_INFRA_RUNTIME | harvest待评估（likely_misplaced） |  |
| CAND-HARVEST-3647 | Redis Stream 消息通道 | 成交回报At-Least-Once+幂等消费 | D_INFRA_RUNTIME | harvest待评估（likely_new） |  |
| CAND-HARVEST-3648 | Redis Pub/Sub 发布订阅 | 数据更新通知At-Most-Once | D_INFRA_RUNTIME | harvest待评估（likely_new） |  |
| CAND-HARVEST-3673 | External API Metrics 外部API调用指标 | / 外部API调用指标 / ✅能建 / `prometheus_client` Histogram+Counter / 无 / | D_INFRA_RUNTIME | harvest待评估（likely_misplaced） |  |
| CAND-HARVEST-3674 | Circuit Breaker State Export 熔断器状态导出 | prometheus_client Gauge | D_INFRA_RUNTIME | harvest待评估（likely_misplaced） |  |
| CAND-HARVEST-3722 | Redis Hash Redis哈希 | 原始交互记录存入工作记忆实时写入 | D_INFRA_RUNTIME | harvest待评估（likely_new） |  |
| CAND-HARVEST-3723 | FAISS Vector Search FAISS向量检索 | FAISS向量检索+SQLite结构化查询 | D_INFRA_RUNTIME | harvest待评估（likely_new） |  |
| CAND-HARVEST-3726 | ChromaDB Vector Database ChromaDB向量数据库 | / 向量存储 / ChromaDB+Faiss GPU(双轨已采用) / ChromaDB+Faiss GPU+Qdrant评估 / Qdrant/Chroma(独立服务) / | D_INFRA_RUNTIME | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-3727 | Faiss GPU Vector Search Faiss GPU向量搜索 | Faiss GPU利用RTX 3090 24GB显存 | D_INFRA_RUNTIME | harvest待评估（likely_new） |  |
| CAND-HARVEST-3728 | Qdrant Vector Database Qdrant向量数据库 | Qdrant/Chroma独立服务评估 | D_INFRA_RUNTIME | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-3729 | ClickHouse Database ClickHouse数据库 | ClickHouse替代DuckDB支持更复杂查询 | D_INFRA_RUNTIME | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-3730 | DuckDB Database DuckDB数据库 | DuckDB+Parquet温存储 | D_INFRA_RUNTIME | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-3736 | Kafka Message Queue Kafka消息队列 | Parquet+Kafka事件存储 | D_INFRA_RUNTIME | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-3737 | EventStoreDB Event Store EventStoreDB事件存储 | Kafka+EventStoreDB事件存储 | D_INFRA_RUNTIME | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-3743 | MinIO Object Storage MinIO对象存储 | 对象存储MinIO/NAS冷存储 | D_INFRA_RUNTIME | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-3744 | NAS Storage NAS存储 | 对象存储MinIO/NAS冷存储 | D_INFRA_RUNTIME | harvest待评估（likely_new） |  |
| CAND-HARVEST-3746 | Parquet Columnar Storage Parquet列式存储 | Parquet列式存储温冷层 | D_INFRA_RUNTIME | harvest待评估（likely_new） |  |
| CAND-HARVEST-3747 | Redis In-Memory Store Redis内存存储 | Redis热存储行情缓存 | D_INFRA_RUNTIME | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-3748 | SQLite Database SQLite数据库 | SQLite血缘追踪 | D_INFRA_RUNTIME | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-3775 | Blueprint Code Sync 蓝图代码同步 | src/zephyr/core/blueprint_code_sync.py,module,MOD-INF-016-CORE | D_INFRA_RUNTIME | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-3776 | Base 基础 | src/zephyr/l02_alpha_factor/base.py,module,MOD-L02-001 | D_INFRA_RUNTIME | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-3778 | App 包装器 | src/zephyr/l08_human_ai_interface/dashboard/app.py,module,MOD-L08-001 | D_INFRA_RUNTIME | harvest待评估（likely_new） |  |
| CAND-HARVEST-3779 | State Machine 状态机 | src/zephyr/shared/state_machine.py,module,MOD-INF-016-SHARED | D_INFRA_RUNTIME | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-3876 | NSSM+自研Supervisor 进程守护层 | 进程守护层P1-P5优先级控制+自动重启+日志管理 | D_INFRA_RUNTIME | harvest待评估（likely_new） |  |
| CAND-HARVEST-3878 | Redis共享状态 共享状态层 | 13命名空间AOF+RDB混合持久化 | D_INFRA_RUNTIME | harvest待评估（likely_new） |  |
| CAND-HARVEST-3879 | GPU调度层 GPU调度 | RTX 3090 24GB盘中推理盘后训练 | D_INFRA_RUNTIME | harvest待评估（likely_new） |  |
| CAND-HARVEST-3880 | Hot平面 热平面 | 小于10ms风控执行路径CPU核8-11 | D_INFRA_RUNTIME | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-3881 | Warm平面 温平面 | 10ms到1s信号策略路径CPU核4-7 | D_INFRA_RUNTIME | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-3882 | Cold平面 冷平面 | 大于1s训练研究路径CPU核16-19 | D_INFRA_RUNTIME | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-3892 | GPU调度上岗+热交换 GPU调度 | 盘中推理8-10GB盘后训练16-18GB | D_INFRA_RUNTIME | harvest待评估（likely_new） |  |
| CAND-HARVEST-3910 | 熔断器模式 Circuit Breaker | Netflix Hystrix三态熔断Closed Open Half-Open | D_INFRA_RUNTIME | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-3911 | 应急保命轨 应急保命轨 Emergency Life-Saving Track | L0正常L1降级L2保命L3冻结四级 | D_INFRA_RUNTIME | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-3943 | 审计追踪依赖构建器 Audit Trail Dependency Builder | 审计追踪依赖构建器 | D_INFRA_RUNTIME | harvest待评估（likely_misplaced） |  |
| CAND-HARVEST-3948 | Audit Trail Dependency Integrity Verifier 审计追踪依赖完整性验证器 | 审计追踪依赖完整性验证器 | D_INFRA_RUNTIME | harvest待评估（likely_misplaced） |  |
| CAND-HARVEST-3995 | NSSM注册Windows服务 NSSM Windows Service | 5个Python进程注册为Windows服务开机自启崩溃重启 | D_INFRA_RUNTIME | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-3996 | 自研Python守护进程 Python Supervisor | 优先级启停健康检查XML-RPC控制 | D_INFRA_RUNTIME | harvest待评估（likely_new） |  |
| CAND-HARVEST-3997 | pywin32supervisor pywin32监控器 | 0.0.1版本无社区验证不能建 | D_INFRA_RUNTIME | harvest待评估（likely_new） |  |
| CAND-HARVEST-3998 | WinSW Windows Service Wrapper 服务 | MIT许可XML配置需NET Runtime不能建 | D_INFRA_RUNTIME | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-3999 | GPU MPS多进程并发 GPU Multi-Process Service | NVIDIA MPS允许多CUDA进程共享GPU上下文不能建 | D_INFRA_RUNTIME | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-4003 | Redis集群/哨兵 Redis Cluster Sentinel | 集群需多节点违反约束二单机部署不能建 | D_INFRA_RUNTIME | harvest待评估（likely_new） |  |
| CAND-HARVEST-4122 | Monitoring Dashboard Process 监控面板进程 | A1迁移概念级进程P2 实时仪表盘告警展示持仓监控可重启 | D_INFRA_RUNTIME | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-4235 | Bandwidth Optimizer 带宽优化 | / bandwidth_optimizer.py / governance/ / 带宽优化 / ❌ 属于D-INFRA-RUNTIME——带宽是运行时基础设施 / | D_INFRA_RUNTIME | harvest待评估（likely_new） |  |
| CAND-HARVEST-4236 | Local First Architecture 本地优先架构 | / local_first_arch.py / governance/ / 本地优先架构 / ❌ 属于D-INFRA-RUNTIME——本地优先是运行时策略 / | D_INFRA_RUNTIME | harvest待评估（likely_new） |  |
| CAND-HARVEST-4237 | Environment Manager 环境管理 | / environment_manager.py / governance/ / 环境管理 / ❌ 属于D-INFRA-RUNTIME——环境管理是基础设施 / | D_INFRA_RUNTIME | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-4238 | Path Resolver 路径解析 | / path_resolver.py / governance/ / 路径解析 / ❌ 属于D-INFRA-RUNTIME——路径解析是基础设施 / | D_INFRA_RUNTIME | harvest待评估（likely_new） |  |
| CAND-HARVEST-4254 | Governance Adapter 治理适配器 | / l01_infrastructure/a2a_protocol/governance/governance_adapter.py / l01_infrastructure/ (MOD-INF-025) / 治理适配器 / ⚠️ 双归属— | D_INFRA_RUNTIME | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-4255 | Governance Protocol 治理协议 | / l01_infrastructure/a2a_protocol/governance/protocol.py / l01_infrastructure/ (MOD-INF-025) / 治理协议 / ⚠️ 双归属——协议层在D-INFR | D_INFRA_RUNTIME | harvest待评估（likely_new） |  |
| CAND-HARVEST-4418 | Effect Metric Trend 效果指标趋势 | / 效果指标趋势 / IC/Sharpe/胜率随时间变化趋势 / 日频 / S5效果评估 / F-05的策略评估子面板 / | D_INFRA_RUNTIME | harvest待评估（likely_misplaced） |  |
| CAND-HARVEST-4467 | Signal Generation Audit Log 信号生成审计日志 | > **搬入原则**: 筛选与信号生成/决策/归因直接相关的合规约束，从D-SIGNAL视角重写。 | D_INFRA_RUNTIME | harvest待评估（likely_misplaced） |  |
| CAND-HARVEST-4860 | 幻觉检测指标 Hallucination Detection Metrics | 幻觉防护-事实核查通过率/一致性评分/数值异常率/置信度均值 | D_INFRA_RUNTIME | harvest待评估（likely_misplaced） |  |
| CAND-HARVEST-5004 | Zero-Knowledge Audit 零知识审计 | 零知识证明合规验证 | D_INFRA_RUNTIME | harvest待评估（likely_misplaced） |  |
| CAND-HARVEST-5007 | Circuit Breaker Matrix 熔断器矩阵 | 三态机+按外部系统差异化阈值交易通道人工恢复 | D_INFRA_RUNTIME | harvest待评估（likely_misplaced） |  |
| CAND-HARVEST-5061 | Circuit Breaker State Machine 熔断器状态机 | / 5种熔断器(CB-001~CB-005) / ✅ 能建 / AP-06 Escalation Engine含CircuitBreaker三态管理 / | D_INFRA_RUNTIME | harvest待评估（likely_misplaced） |  |
| CAND-HARVEST-5076 | Cybersecurity Shield 网络安全防护组件 | / MOD-CMP-001 / D-INFRA-14 Cybersecurity Shield / 网络安全防护组件 / | D_INFRA_RUNTIME | harvest待评估（likely_new） |  |
| CAND-HARVEST-5077 | Experiment and Resilience Testing 实验与韧性测试 | / MOD-EXP-001 / D-INFRA-15 Resilience Testing Engine / 实验与韧性测试 / | D_INFRA_RUNTIME | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-5078 | Knowledge Base Data Sovereignty 知识库数据主权管理 | / MOD-KB-002 / D-INFRA-12 Data Sovereignty Manager / 知识库数据主权管理 / | D_INFRA_RUNTIME | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-5079 | System Master Infrastructure 系统总蓝图基础设施支撑 | D-INFRA-01~D-INFRA-17 整体基础设施 | D_INFRA_RUNTIME | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-5256 | Carbon-Aware Scheduler Optimizer 碳感知调度优化器 | §6设计决策 碳感知调度优化器 | D_INFRA_RUNTIME | harvest待评估（likely_misplaced） |  |
| CAND-HARVEST-5277 | Data Change Audit 数据变更审计 | §13.4数据指纹与血缘合规 数据变更审计 | D_INFRA_RUNTIME | harvest待评估（likely_misplaced） |  |

### 一问通过（1 条）

| ID | 名称 | 大白话（干什么用） | 域 | 卡点理由 | 替代方案 |
|------|------|------|------|------|------|
| CAND-H1FS-001 | H1 Factor Source / H1 因子截面读取适配器 | (无真实痛点)设想为信号端提供友好因子读取接口,但读端已由 H1RedisReader 覆盖 | D_INFRA_RUNTIME | rejected,q2无需求驱动+q1已由H1RedisReader.get_online_features覆盖。depgraph node7964707已deprecated。除非D_SIGNAL信号域启动且批量截面读性能不达标,否则不再评估 | 信号域直接用 H1RedisReader.get_online_features(蓝图 §9 既定接口)。若未来需批量截面读,在 D_SIGNAL 启动时按需新增,届时过一问标准 |

## 复查时间表

> 按 next_review_date 升序。复查时重新过一问，触发信号命中则晋升到 depgraph 设计态。

| 下次复查 | 复查频率 | ID | 名称 | 域 | 状态 | 上次复查结论 |
|------|------|------|------|------|------|------|
| 2026-11-30 | quarterly | CAND-HARVEST-0094 | Rebalance Scheduler再平衡调度器 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_misplaced） |
| 2026-11-30 | quarterly | CAND-HARVEST-0225 | Signal Audit Logger 信号审计 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_misplaced） |
| 2026-11-30 | quarterly | CAND-HARVEST-0276 | Audit Trail 审计追踪 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_misplaced） |
| 2026-11-30 | quarterly | CAND-HARVEST-0288 | High Performance HA Framework 高性能高可用保障框架 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0611 | Database Layer 数据库层 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-0630 | 数据库管理器 Database Manager (16分片SQLite) | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-0631 | 跨域事件总线 Cross-domain Event Bus | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-0632 | 缓存一致性管理器 Cache Consistency Manager | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-0633 | 数据质量监控器 Data Quality Monitor | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-0634 | 数据血缘追踪器 Data Lineage Tracker | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-0635 | 数据完整性校验器 Data Integrity Validator | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-0636 | 数据字段Schema版本管理器 Data Field Schema Version Manager | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-0637 | 数据验证规则引擎 Data Validation Rule Engine | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-0805 | Auto Backtest Scheduler 自动回测调度器 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_misplaced） |
| 2026-11-30 | quarterly | CAND-HARVEST-0844 | 集成测试任务 Integration Task | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_misplaced） |
| 2026-11-30 | quarterly | CAND-HARVEST-0859 | Audit Trail 审计链 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_misplaced） |
| 2026-11-30 | quarterly | CAND-HARVEST-0860 | Process Manager 进程管理器 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-0861 | Redis Manager Redis管理器 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-0862 | GPU Scheduler GPU调度器 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-0863 | ConfigManager 配置管理器 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-0864 | Service Registry 服务注册表 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-0865 | Message Queue 消息队列 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-0895 | EventBus 事件总线 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-0896 | Config Center 配置中心 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_misplaced） |
| 2026-11-30 | quarterly | CAND-HARVEST-0897 | Health Checker 健康检查器 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_misplaced） |
| 2026-11-30 | quarterly | CAND-HARVEST-0898 | Metrics Collector 指标采集器 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_misplaced） |
| 2026-11-30 | quarterly | CAND-HARVEST-0899 | Logger 日志器 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_misplaced） |
| 2026-11-30 | quarterly | CAND-HARVEST-0900 | Retry & Circuit Breaker 重试与熔断器 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_misplaced） |
| 2026-11-30 | quarterly | CAND-HARVEST-0901 | Task Scheduler 任务调度器 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_misplaced） |
| 2026-11-30 | quarterly | CAND-HARVEST-0902 | 审计系统 Audit System | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_misplaced） |
| 2026-11-30 | quarterly | CAND-HARVEST-0907 | Runtime 运行时 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-0991 | Inference Circuit Breaker 推理熔断器 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_misplaced） |
| 2026-11-30 | quarterly | CAND-HARVEST-1056 | MCP Gateway Rate-Limit Audit Manager MCP网关限流审计管理器 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_misplaced） |
| 2026-11-30 | quarterly | CAND-HARVEST-1058 | Immutable Audit Log Writer 不可变审计日志写入器 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_misplaced） |
| 2026-11-30 | quarterly | CAND-HARVEST-1059 | TaskCard Six-Dimension Anti-Drift Validator TaskCard六维防漂移校验器 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_misplaced） |
| 2026-11-30 | quarterly | CAND-HARVEST-1060 | Audit-Persistence Dual-Write Coordinator 审计-持久化双写协调器 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_misplaced） |
| 2026-11-30 | quarterly | CAND-HARVEST-1130 | SystemHealthVisualization 系统健康可视化 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_misplaced） |
| 2026-11-30 | quarterly | CAND-HARVEST-1166 | Service Degradation Manager 服务降级管理器 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1167 | Connection Pool Manager 连接池管理器 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1170 | Failover Coordinator 故障转移协调器 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1230 | Risk Check Dependency Short-Circuit Evaluator 风控检查依赖短路评估器 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_misplaced） |
| 2026-11-30 | quarterly | CAND-HARVEST-1243 | Vector Index Health Monitor 向量索引健康监控器 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_misplaced） |
| 2026-11-30 | quarterly | CAND-HARVEST-1246 | Core Chain E2E Health Monitor 核心链路端到端健康监控器 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_misplaced） |
| 2026-11-30 | quarterly | CAND-HARVEST-1247 | Code Health Assessor 代码健康度评估器 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_misplaced） |
| 2026-11-30 | quarterly | CAND-HARVEST-1252 | System Health Five-Star Scorer 系统健康度五星评分器 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_misplaced） |
| 2026-11-30 | quarterly | CAND-HARVEST-1258 | M10 Audit Report Finding Format Generator M10审计报告Finding格式生成器 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_misplaced） |
| 2026-11-30 | quarterly | CAND-HARVEST-1290 | PERM Independent Health Checker PERM独立健康检查器 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_misplaced） |
| 2026-11-30 | quarterly | CAND-HARVEST-1291 | Trading Session Aware Ops Scheduler 交易时段感知运维调度器 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_misplaced） |
| 2026-11-30 | quarterly | CAND-HARVEST-1335 | Financial Time Series Data Augmentation 金融时序数据增强 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1417 | Multi-Process Isolation & Runtime Architecture 多进程隔离与运行时架构 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1418 | Model Registry & Experiment Management 模型注册与实验管理 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1419 | Time-Series Database & Tiered Storage 时序数据库与分层存储架构 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1420 | Feature Drift & Concept Drift Detection 特征漂移与概念漂移检测 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1421 | Graph Neural Network for Stock Relations 图神经网络用于股票关系建模 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1422 | Transformer Time-Series Architecture Transformer时序架构 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1423 | Signature Methods 签名方法 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1424 | Reinforcement Learning for Portfolio & Execution 强化学习用于组合优化与订单执行 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1425 | LLM Agent for Fundamental Analysis 大语言模型Agent用于基本面分析 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1426 | Alternative Data Source Expansion 另类数据源扩展 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1427 | Market Microstructure Deep Modeling 市场微观结构深度建模 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1428 | Conformal Prediction 共形预测 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1429 | Survival Analysis 生存分析 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1430 | Causal ML 深度补充 因果ML深度补充 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1431 | Learning System Bridge Declaration 学习系统桥接声明 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1432 | Mamba/SSM State Space Model Mamba/SSM状态空间模型 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1434 | Time-Series Conformal Prediction Enhancement TCP/DDCI/CP-VaR 时序保形预测增强 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1435 | A-Share Diffusion Model Data Augmentation A股扩散模型数据增强 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1448 | Alternative Data Source Health & Degradation Manager 另类数据源健康度与降级管理器 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_misplaced） |
| 2026-11-30 | quarterly | CAND-HARVEST-1449 | Hardware Accelerator 硬件加速器 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1450 | GPU Compute Pipeline Manager GPU计算管线管理器 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1451 | GPU Memory Transfer Optimizer GPU内存传输优化器 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1452 | GPU Programming Abstraction Layer GPU编程抽象层 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1453 | GPU Resource Monitor GPU资源监控器 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1454 | GPU Inference Training Dynamic Allocator GPU推理训练动态分配器 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1455 | GPU Kernel Launch Optimizer GPU内核启动优化器 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1456 | CPU Core Allocation Manager CPU核心分配管理器 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1457 | Single-Machine Concurrency Mode Optimizer 单机并发模式优化器 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1458 | Inter-Process Communication Manager 进程间通信管理器 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1459 | Thread Pool Manager 线程池管理器 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1460 | System Startup Orchestrator 系统启动编排器 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1461 | Environment Variable Manager 环境变量管理器 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1462 | Process Daemon Monitor 进程守护监控器 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1463 | Graceful Shutdown Coordinator 优雅关闭协调器 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1465 | Communication Protocol Adapter 通信协议适配器 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1466 | Serialization Performance Optimizer 序列化性能优化器 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1467 | Multi-Protocol Network Adapter 多协议网络适配器 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1468 | Multi-Modal Input Router 多模态输入路由 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1469 | Request Retry Manager 请求重试管理器 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1470 | Data Transfer Validator 数据传输校验器 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1471 | WebSocket Reconnection WebSocket断线重连 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1472 | Cross-Origin Resource Sharing Manager 跨域资源共享管理器 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1473 | Configuration Manager 配置管理器 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1474 | Runtime Configuration Validator 运行时配置校验器 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1475 | Configuration Change Notifier 配置变更通知器 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1476 | Configuration Diff Detector 配置差异检测器 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1477 | Configuration Merge Engine 配置合并引擎 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1478 | Environment Configuration Layering Manager 环境配置分层管理器 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1479 | Configuration Encryption Manager 配置加密管理器 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1480 | Configuration Hot Update Engine 配置热更新引擎 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1481 | Configuration Dependency Mapper 配置依赖映射器 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1482 | Configuration Version Management & Rollback Framework 配置版本管理与回滚框架 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1483 | Configuration Validation Engine 配置校验引擎 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1484 | Unified Feature Toggle Framework 统一功能开关框架 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1485 | Resource Scheduler 资源调度器 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1486 | Elastic Scaling Manager 弹性伸缩管理器 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1487 | Multi-Region Collaboration Manager 多区域协同管理器 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1488 | Request Forwarding & Load Balancer 请求转发与负载均衡器 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1489 | Service Discovery Registrar 服务发现注册器 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1490 | Container Orchestrator 容器编排器 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1491 | Network Policy Manager 网络策略管理器 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1492 | Traffic Shaper 流量整形器 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1493 | Load Balancing Strategy Engine 负载均衡策略引擎 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1494 | Container Image Cache Manager 容器镜像缓存管理器 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1495 | Container Resource Isolator 容器资源隔离器 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1496 | Service Rate Limiter 服务限流器 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1497 | Service Dependency Health Checker 服务依赖健康检查器 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1498 | Runtime Infrastructure Self-Checker 运行时基础设施自检器 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1499 | Live Data to Research Domain Feedback Channel 实盘数据→研究域反馈通道 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1500 | Message Queue Manager 消息队列管理器 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1501 | Distributed Lock Manager 分布式锁管理器 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1502 | Cache Warmup Manager 缓存预热管理器 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1503 | Cold Start Optimizer 冷启动优化器 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1504 | Factor Warmup Manager 因子预热管理器 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1505 | Signal Warmup Manager 信号预热管理器 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1506 | Real-Time Data Warmer 实时数据预热器 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1507 | Model Warmup Manager 模型预热管理器 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1508 | Inference Engine Warmer 推理引擎预热器 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1509 | Cache Data Preloader 缓存数据预加载器 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1510 | Data Compression Manager 数据压缩管理器 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1511 | Inter-Layer Data Format Converter & Validator 层间数据格式转换与校验器 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1512 | Data Format Version Coordinator 数据格式版本协调器 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1513 | Data Transformation Performance Optimizer 数据转换性能优化器 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1514 | Batch Data Processor 批量数据处理器 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1515 | Real-Time Data Stream Manager 实时数据流管理器 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1516 | Data Buffer Pool Manager 数据缓冲池管理器 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1517 | Data Source Star Rating Dynamic Updater 数据源星级评分动态更新器 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1518 | Data Migration Script Generator 数据迁移脚本生成器 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1519 | Database Schema Synchronizer 数据库Schema同步器 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1520 | Field Mapping Converter 字段映射转换器 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1521 | Data Transformation Pipeline Orchestrator 数据转换管线编排器 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1522 | Data Aggregation View Manager 数据聚合视图管理器 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1523 | Telemetry Four-Stream Unified Collector 遥测四流统一采集器 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1524 | Request Chain Tracer 请求链追踪器 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1525 | MCP Sentinel System Monitor MCP哨兵系统监控器 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1526 | Monitoring Data Aggregator 监控数据聚合器 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1527 | Real-Time Alert Engine 实时告警引擎 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1528 | Alert Silence Manager 告警静默管理器 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1529 | Alert Escalation Strategy Engine 告警升级策略引擎 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1530 | Metric Anomaly Detector 指标异常检测器 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1531 | Privacy-Preserving Computation 隐私保护计算 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1532 | Data Sovereignty Manager 数据主权管理器 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1533 | Clock Sync Service 时钟同步服务 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1534 | Code Security Static Analyzer 代码安全静态分析器 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1535 | Document Search Indexer 文档搜索索引器 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1536 | Module Version Dependency Resolver 模块版本依赖解析器 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1537 | Code Structure Visualizer 代码结构可视化器 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1538 | Package Dependency Graph Generator 包依赖图生成器 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1539 | Code Complexity Analyzer 代码复杂度分析器 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1540 | Code Duplication Detector 代码重复检测器 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1541 | Code Change Impact Analyzer 代码变更影响分析器 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1542 | Automated Code Reviewer 自动代码审查器 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1543 | Code Standard Enforcer 代码规范强制执行器 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1544 | Architecture Compliance Checker 架构合规检查器 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1545 | Technical Debt Tracker 技术债务追踪器 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1546 | Architecture Evolution Planner 架构演进规划器 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1547 | Code Template Engine 代码模板引擎 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1548 | DAO Layer Code Generator DAO层代码生成器 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1549 | REST API Code Generator REST API代码生成器 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1550 | Test Code Generator 测试代码生成器 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1551 | Configuration Code Generator 配置代码生成器 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1552 | Interface Mock Generator 接口Mock生成器 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1553 | Data Model Generator 数据模型生成器 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1554 | Validation Rule Generator 验证规则生成器 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1555 | Error Handling Code Generator 错误处理代码生成器 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1556 | API Version Manager API版本管理器 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1557 | Module Interface Contract Manager 模块接口契约管理器 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1558 | SDK Auto Generator SDK自动生成器 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1559 | API Documentation Synchronizer API文档同步器 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1560 | Endpoint Response Format Validator 端点响应格式校验器 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1561 | API Version Compatibility Detector API版本兼容检测器 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1562 | Return Value Performance Monitor 返回值性能监控器 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1563 | Inter-Module Communication Protocol Manager 模块间通信协议管理器 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1564 | Module Lifecycle Manager 模块生命周期管理器 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1565 | Module Registry 模块注册中心 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1566 | Module Dependency Injector 模块依赖注入器 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1567 | Module Configuration Aggregator 模块配置聚合器 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1568 | Module Health Checker 模块健康检查器 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1569 | Module Hot Update Manager 模块热更新管理器 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1570 | Module Feature Toggle Manager 模块功能开关管理器 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1571 | Plugin System Manager 插件系统管理器 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1572 | Module Sandbox Isolator 模块沙箱隔离器 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1573 | Module Metrics Collector 模块度量采集器 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1574 | Module Log Aggregator 模块日志聚合器 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1575 | Module Exception Boundary Manager 模块异常边界管理器 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1576 | Module Performance Profiler 模块性能分析器 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1577 | Module Documentation Indexer 模块文档索引器 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1578 | Module Test Runner 模块测试运行器 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1579 | Global Dependency Graph Calculator 全局依赖图计算器 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1580 | Circular Dependency Detector 循环依赖检测器 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1581 | Dependency Version Lock Manager 依赖版本锁定管理器 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1582 | Dependency Security Vulnerability Scanner 依赖安全漏洞扫描器 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1583 | Transitive Dependency Analyzer 传递依赖分析器 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1584 | Dependency Conflict Resolver 依赖冲突解决器 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1585 | Dependency Upgrade Compatibility Checker 依赖升级兼容性检查器 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1586 | Dependency Graph Visualization Renderer 依赖图可视化渲染器 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1587 | Regression Test Orchestrator 回归测试编排器 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1588 | Test Coverage Tracker 测试覆盖率追踪器 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1589 | Document Template Engine 文档模板引擎 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1590 | Document Version Manager 文档版本管理器 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1591 | Terminology Consistency Validator 术语一致性校验器 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1592 | Specification Automation Checker 规范自动化检查器 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1593 | Document Link Validator 文档链接验证器 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1594 | Knowledge Base Indexer 知识库索引器 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1595 | Strategy Execution Plan Optimizer 策略执行计划优化器 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1596 | Strategy Backtesting Infrastructure 策略回测基础设施 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1598 | Strategy Portfolio Simulator 策略组合模拟器 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1599 | Strategy Parameter Tuning Engine 策略参数调优引擎 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1600 | Strategy Correlation Matrix Calculator 策略相关性矩阵计算器 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1601 | Resource Load Balancer 资源负载均衡器 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1602 | Task Priority Scheduler 任务优先级调度器 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1603 | Resource Reservation Manager 资源预约管理器 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1604 | Resource Quota Manager 资源配额管理器 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1605 | Resource Usage Auditor 资源使用审计器 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1606 | Workflow Version Management 工作流版本管理 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1607 | Phase Synchronization Coordinator 阶段同步协调器 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1608 | Cross-Phase State Propagator 跨阶段状态传递器 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1609 | Milestone Dependency Validator 里程碑依赖校验器 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1610 | Deliverable Version Tracker 交付物版本追踪器 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1611 | Phase Retrospective Analyzer 阶段回顾分析器 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1612 | Continuous Improvement Engine 持续改进引擎 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1613 | Schedule Conflict Detector 时间表冲突检测器 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1614 | Development Plan Visualizer 开发计划可视化器 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1615 | Resource Timeline Manager 资源时间线管理器 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1616 | Iteration Cycle Tracker 迭代周期追踪器 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1617 | Panel Layout Engine 面板布局引擎 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1618 | Region Collapse Manager 区域折叠管理器 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1619 | Dependency Visualizer 依赖可视化器 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1620 | Deployment Topology Manager 部署拓扑管理器 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1621 | Feature Lifecycle Manager 功能生命周期管理器 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1622 | Domain-Driven Design Validator 领域驱动设计校验器 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1623 | Architecture Recommendation Engine 架构推荐引擎 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1624 | Infrastructure Topology Visualizer 基础设施拓扑可视化器 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1625 | Application State Snapshotter 应用状态快照器 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1626 | Session Persistence Manager 会话持久化管理器 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1627 | User Preference Synchronizer 用户偏好同步器 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1628 | Multi-Device State Coordinator 多端状态协调器 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1629 | Conversation Context Compressor 对话上下文压缩 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1754 | Canary Dependency Mapper 金丝雀依赖映射器 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1755 | Blue-Green Dependency Mapper 蓝绿依赖映射器 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1756 | AB Test Dependency Mapper AB测试依赖映射器 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1757 | Traffic Mirror Mapper 流量镜像映射器 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1758 | Progressive Delivery Pre-check Enhancer 渐进交付前置检查增强 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1759 | Traffic Mirror Dependency Mapping Enhancer 流量镜像依赖映射增强 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1760 | Policy Conflict Auto Detector 策略冲突自动检测器 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1804 | VaR Recalculation Scheduler VaR重算调度器 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_misplaced） |
| 2026-11-30 | quarterly | CAND-HARVEST-2087 | Collection Scheduler 采集调度器 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_misplaced） |
| 2026-11-30 | quarterly | CAND-HARVEST-2111 | Task Orchestration 任务编排 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_misplaced） |
| 2026-11-30 | quarterly | CAND-HARVEST-2119 | Strategy Health Score 策略健康评分 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_misplaced） |
| 2026-11-30 | quarterly | CAND-HARVEST-2120 | Circuit Breaker Trigger 熔断触发 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_misplaced） |
| 2026-11-30 | quarterly | CAND-HARVEST-2145 | Circuit Breaker 熔断器 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_misplaced） |
| 2026-11-30 | quarterly | CAND-HARVEST-2173 | Working Memory 工作记忆 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2205 | Redis Redis内存数据库 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2206 | SQLite SQLite嵌入式数据库 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2207 | Parquet Parquet列式存储格式 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2249 | Multi-Dimensional Quantitative Health Indicator 多维量化健康指标 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_misplaced） |
| 2026-11-30 | quarterly | CAND-HARVEST-2263 | strategy-health-score 策略健康评分 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_misplaced） |
| 2026-11-30 | quarterly | CAND-HARVEST-2285 | Redis Pub/Sub Redis发布订阅 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2344 | Success Metrics 成功指标 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_misplaced） |
| 2026-11-30 | quarterly | CAND-HARVEST-2433 | L10 Audit Trail 审计追踪与零知识审计 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_misplaced） |
| 2026-11-30 | quarterly | CAND-HARVEST-2449 | Audit Evidence Chain Architecture 审计证据链架构 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_misplaced） |
| 2026-11-30 | quarterly | CAND-HARVEST-2450 | Three Layer Audit Architecture 三层审计架构 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_misplaced） |
| 2026-11-30 | quarterly | CAND-HARVEST-2451 | Hash Chain Audit 哈希链审计 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_misplaced） |
| 2026-11-30 | quarterly | CAND-HARVEST-2452 | Merkle Tree Audit Merkle树审计 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_misplaced） |
| 2026-11-30 | quarterly | CAND-HARVEST-2470 | Zero Knowledge Audit 零知识审计 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_misplaced） |
| 2026-11-30 | quarterly | CAND-HARVEST-2477 | ZKP Circuit Library ZKP电路库 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_misplaced） |
| 2026-11-30 | quarterly | CAND-HARVEST-2501 | AI Training Data Audit AI训练数据审计 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_misplaced） |
| 2026-11-30 | quarterly | CAND-HARVEST-2510 | Operation Process Audit 操作流程审计 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_misplaced） |
| 2026-11-30 | quarterly | CAND-HARVEST-2585 | Audit Log 审计日志 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_misplaced） |
| 2026-11-30 | quarterly | CAND-HARVEST-2746 | Trading Audit Log 交易审计日志 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_misplaced） |
| 2026-11-30 | quarterly | CAND-HARVEST-2747 | Decision Audit Log 决策审计日志 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_misplaced） |
| 2026-11-30 | quarterly | CAND-HARVEST-2748 | Data Access Audit Log 数据访问审计日志 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_misplaced） |
| 2026-11-30 | quarterly | CAND-HARVEST-2749 | AI Call Audit Log AI调用审计日志 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_misplaced） |
| 2026-11-30 | quarterly | CAND-HARVEST-2750 | System Change Audit Log 系统变更审计日志 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_misplaced） |
| 2026-11-30 | quarterly | CAND-HARVEST-3003 | AI自治行为审计 AI Autonomous Behavior Audit | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_misplaced） |
| 2026-11-30 | quarterly | CAND-HARVEST-3052 | boundary_audit.py 自治行为审计 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_misplaced） |
| 2026-11-30 | quarterly | CAND-HARVEST-3376 | 熔断器模式 Circuit Breaker Pattern | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_misplaced） |
| 2026-11-30 | quarterly | CAND-HARVEST-3532 | asymmetric_audit.py 非对称审计 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_misplaced） |
| 2026-11-30 | quarterly | CAND-HARVEST-3576 | 定时熔断 Timer Circuit Breaker | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_misplaced） |
| 2026-11-30 | quarterly | CAND-HARVEST-3581 | L4审计隔离 L4 Audit Isolation | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_misplaced） |
| 2026-11-30 | quarterly | CAND-HARVEST-3613 | 审计可追溯缺口 Audit Traceability Gap | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_misplaced） |
| 2026-11-30 | quarterly | CAND-HARVEST-3647 | Redis Stream 消息通道 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3648 | Redis Pub/Sub 发布订阅 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3673 | External API Metrics 外部API调用指标 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_misplaced） |
| 2026-11-30 | quarterly | CAND-HARVEST-3674 | Circuit Breaker State Export 熔断器状态导出 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_misplaced） |
| 2026-11-30 | quarterly | CAND-HARVEST-3722 | Redis Hash Redis哈希 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3723 | FAISS Vector Search FAISS向量检索 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3726 | ChromaDB Vector Database ChromaDB向量数据库 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-3727 | Faiss GPU Vector Search Faiss GPU向量搜索 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3728 | Qdrant Vector Database Qdrant向量数据库 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-3729 | ClickHouse Database ClickHouse数据库 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-3730 | DuckDB Database DuckDB数据库 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-3736 | Kafka Message Queue Kafka消息队列 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-3737 | EventStoreDB Event Store EventStoreDB事件存储 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-3743 | MinIO Object Storage MinIO对象存储 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-3744 | NAS Storage NAS存储 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3746 | Parquet Columnar Storage Parquet列式存储 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3747 | Redis In-Memory Store Redis内存存储 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-3748 | SQLite Database SQLite数据库 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-3775 | Blueprint Code Sync 蓝图代码同步 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-3776 | Base 基础 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-3778 | App 包装器 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3779 | State Machine 状态机 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-3876 | NSSM+自研Supervisor 进程守护层 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3878 | Redis共享状态 共享状态层 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3879 | GPU调度层 GPU调度 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3880 | Hot平面 热平面 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-3881 | Warm平面 温平面 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-3882 | Cold平面 冷平面 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-3892 | GPU调度上岗+热交换 GPU调度 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3910 | 熔断器模式 Circuit Breaker | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-3911 | 应急保命轨 应急保命轨 Emergency Life-Saving Track | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-3943 | 审计追踪依赖构建器 Audit Trail Dependency Builder | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_misplaced） |
| 2026-11-30 | quarterly | CAND-HARVEST-3948 | Audit Trail Dependency Integrity Verifier 审计追踪依赖完整性验证器 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_misplaced） |
| 2026-11-30 | quarterly | CAND-HARVEST-3995 | NSSM注册Windows服务 NSSM Windows Service | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-3996 | 自研Python守护进程 Python Supervisor | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3997 | pywin32supervisor pywin32监控器 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3998 | WinSW Windows Service Wrapper 服务 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-3999 | GPU MPS多进程并发 GPU Multi-Process Service | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-4003 | Redis集群/哨兵 Redis Cluster Sentinel | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4122 | Monitoring Dashboard Process 监控面板进程 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-4235 | Bandwidth Optimizer 带宽优化 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4236 | Local First Architecture 本地优先架构 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4237 | Environment Manager 环境管理 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-4238 | Path Resolver 路径解析 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4254 | Governance Adapter 治理适配器 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-4255 | Governance Protocol 治理协议 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4418 | Effect Metric Trend 效果指标趋势 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_misplaced） |
| 2026-11-30 | quarterly | CAND-HARVEST-4467 | Signal Generation Audit Log 信号生成审计日志 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_misplaced） |
| 2026-11-30 | quarterly | CAND-HARVEST-4860 | 幻觉检测指标 Hallucination Detection Metrics | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_misplaced） |
| 2026-11-30 | quarterly | CAND-HARVEST-5004 | Zero-Knowledge Audit 零知识审计 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_misplaced） |
| 2026-11-30 | quarterly | CAND-HARVEST-5007 | Circuit Breaker Matrix 熔断器矩阵 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_misplaced） |
| 2026-11-30 | quarterly | CAND-HARVEST-5061 | Circuit Breaker State Machine 熔断器状态机 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_misplaced） |
| 2026-11-30 | quarterly | CAND-HARVEST-5076 | Cybersecurity Shield 网络安全防护组件 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-5077 | Experiment and Resilience Testing 实验与韧性测试 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-5078 | Knowledge Base Data Sovereignty 知识库数据主权管理 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-5079 | System Master Infrastructure 系统总蓝图基础设施支撑 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-5256 | Carbon-Aware Scheduler Optimizer 碳感知调度优化器 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_misplaced） |
| 2026-11-30 | quarterly | CAND-HARVEST-5277 | Data Change Audit 数据变更审计 | D_INFRA_RUNTIME | 候选待评（candidate） | harvest待评估（likely_misplaced） |
| 2027-08-02 | yearly | CAND-H1FS-001 | H1 Factor Source / H1 因子截面读取适配器 | D_INFRA_RUNTIME | 否决（rejected） | rejected,q2无需求驱动+q1已由H1RedisReader.get_online_features覆盖。depgraph node7964707已deprecated。除非D_SIGNAL信号域启动且批量截面读性能不达标,否则不再评估 |
