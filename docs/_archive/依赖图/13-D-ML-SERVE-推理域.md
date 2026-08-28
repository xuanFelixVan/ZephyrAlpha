# 13 — D-ML-SERVE 推理域

> **状态**: DRAFT | **核心层**: L13 推理层 | **成熟度**: L1 🔵 骨架
> **运行平面**: Warm(H=3) | **一句话**: 部署模型、推理服务、漂移监控

## §0 域定义

| 维度 | 内容 |
|------|------|
| 域ID | D-ML-SERVE |
| 域名 | 机器学习推理域 |
| 职责 | 模型推理、模型生命周期管理、漂移监控、LLM网关（Warm平面） |
| 核心层 | L13(推理层) |
| 成熟度 | L1 🔵骨架 |
| 优先级 | P1 |
| 架构定位 | 服务域——为其他域提供模型推理服务，自身不承载业务逻辑 |
| 核心Aggregate | AGG-008 Model（不变量：至多一个active版本；active⇒approval_ts≠None） |
| 核心事件 | E-OP-02 ModelDriftDetected |
| 运行平面 | Warm(H=3)，在线推理，延迟目标P50<50ms |
| 不变量执行 | INV-011(Cold→Hot禁止直接通信)：owner_domain=D-ML-SERVE，执行影子验证门禁 |

## §1 子模块清单（6个子模块，中等厚度）

> **骨架来源**：学习系统7阶段流水线(A8) S5 → SERVE覆盖"模型验证→部署→监控"的运行侧

| ID | 名称 | 职责 | 优先级 | 开发状态 | 对标能力 | 对标流水线 |
|----|------|------|:------:|:--------:|---------|-----------|
| MS-01 | ModelRegistry | 模型版本生命周期+持久化+审批：版本状态(DEVELOPMENT→VALIDATED→ACTIVE→DEPRECATED→ARCHIVED)、Git-like语义版本、血缘自动关联、INV-011影子验证门禁执行 | P0 | ✅ 已有(内存) | C-029◐模型工厂 | S5门禁 |
| MS-02 | InferenceEngine | GPU推理+CPU降级+批量推理：ONNX Runtime CUDA、CPU fallback、模型热加载、原子切换、推理熔断(连续失败→降级结果) | P0 | ✅ 已有(numpy) | C-014◐大盘预测 | S5部署 |
| MS-03 | DriftMonitor | 四维漂移监控：PSI(输入特征漂移)+性能衰减(预测MSE/MAE)+JS散度(输出分布漂移)+IC衰减(概念漂移)、共形漂移检测+多尺度漂移检测 | P0 | ❌ | C-025◐质量保障 | S5验证 |
| MS-04 | ModelValidator | 模型验证+压力测试+边界测试：回测验证、极端场景测试、稳定性检验、影子交易验证(INV-011执行)、AI Construction Governor(公式Hash+回归截断+值域偏差) | P0 | ❌ | C-029◐模型工厂 | S5门禁 |
| MS-05 | ServingManager | 模型路由+版本切换+回滚+健康检查：蓝绿部署、金丝雀发布、自动回滚、策略生命周期管理(7状态)、Backtest-to-Production Deployer、灰度发布(5%→20%→50%→100%) | P0 | ❌ | C-007○闭环优化 | S5部署 |
| MS-06 | LLMGateway | LLM API统一集成+降级+成本管理：DeepSeek V4 Pro+GLM-5.1+Claude Opus三API、降级策略、月成本$5-20、LLM Security Gateway九层防御、模型需求分级路由(40%无/35%中等/25%强) | P0 | ❌ | C-029◐模型工厂 | S4创建辅助 |

### 旧子模块归并映射

| 旧ID | 旧名称 | 归入 |
|------|--------|------|
| D-ML-02 / MS-01 | Model Registry | MS-01 |
| D-ML-03 / MS-02 | Inference Engine | MS-02 |
| D-ML-05 / MS-04 | Model Validator | MS-04 |
| D-ML-08 / MS-05 | Model Drift Monitor | MS-03 |
| D-ML-09 | Model A/B Tester | MS-04(内嵌) |
| D-ML-10 / MS-03 | Model Serving Manager | MS-05 |
| D-ML-14 | Model Performance Monitor | MS-03(内嵌) |
| D-ML-21 | Model Risk Governor | MS-04(内嵌) |
| D-ML-22 | TSFM Manager | MS-02(内嵌) |
| D-ML-23 | Model Compression Quantizer | MS-02(内嵌) |
| D-ML-24 | Model Fairness Detector | MS-04(内嵌) |
| D-ML-25 | Model Explanation Report | MS-03(内嵌) |
| D-ML-26 | Model Impact Analyzer | MS-01(内嵌) |
| D-ML-27 | Adversarial Attack Detector | MS-04(内嵌) |
| D-ML-28 | Model Version Manager | MS-01(内嵌) |
| D-ML-38 / MS-15 | KB Embedding BGE-M3-ONNX | MS-02(内嵌) |
| D-ML-39 / MS-14 | LLM API Integration | MS-06 |
| D-ML-72 | MLflow Model Update | MS-01(内嵌) |
| D-ML-73 | AI Model A/B Tester | MS-04(内嵌) |
| D-ML-74 | AI Decision Explanation | MS-03(内嵌) |
| D-ML-75 | Hybrid Deployment AI Manager | MS-05(内嵌) |
| D-ML-87 | Model Lifecycle Manager | MS-05(内嵌) |
| D-ML-126 | Model Deployment Pipeline | MS-05(内嵌) |
| D-ML-127 | Model Performance Drift Monitor | MS-03(内嵌) |
| D-ML-136 | 推理熔断器 | MS-02(内嵌) |
| MS-06~13 | A/B测试/性能监控/风险治理/公平性/解释/影响/对抗/版本 | 分别归入MS-03/MS-04/MS-05 |

### 能力覆盖检查

| 能力 | 优先级 | 角色 | 覆盖子模块 | 状态 |
|------|:------:|:----:|-----------|:----:|
| C-014 大盘预测与次日走势预判 | P1 | ◐辅助 | MS-02(推理服务) | ✅(核心在D-SIGNAL) |
| C-029 模型工厂 | P1 | ◐辅助 | MS-01+MS-04+MS-06 | ✅(核心在D-ML-TRAIN) |
| C-007 闭环优化 | P0 | ○间接 | MS-05(生命周期) | ✅(核心在D-AUTONOMY) |
| C-021 市场状态 | P1 | ○间接 | MS-02(推理服务) | ✅(核心在D-SIGNAL) |
| C-036 群体博弈 | P1 | ○间接 | MS-02(推理服务) | ✅(核心在D-SIGNAL) |

## §2 域内依赖图

```
D-ML-TRAIN ──E-ML-01/E-RS-03──▶ ┌──────────────────────────────────┐
                                 │         MS-01 ModelRegistry      │
                                 │  (INV-011门禁: 影子验证才可ACTIVE) │
                                 └──────────┬───────────┬───────────┘
                                            │           │
                              VALIDATED模型  │           │ ACTIVE模型
                                            ▼           ▼
                                 ┌────────────┐  ┌────────────┐
                                 │  MS-04     │  │  MS-02     │
                                 │  Model     │  │  Inference  │
                                 │  Validator │  │  Engine     │
                                 └─────┬──────┘  └──────┬─────┘
                                       │验证通过        │推理结果
                                       ▼               ▼
                                 ┌────────────┐  ┌──────────────┐
                                 │  MS-01     │  │ D-SIGNAL     │
                                 │  标记ACTIVE│  │ D-PF-CORE    │
                                 └────────────┘  └──────────────┘
                                           
                                 ┌────────────┐  ┌────────────┐
                                 │  MS-05     │  │  MS-03     │
                                 │  Serving   │  │  Drift     │
                                 │  Manager   │  │  Monitor   │
                                 └────────────┘  └──────┬─────┘
                                                       │E-OP-02
                                                       ▼
                                                 ┌────────────┐
                                                 │  MT-05     │
                                                 │  Drift     │
                                                 │  Adapter   │
                                                 └────────────┘
                                                       │
                                 ┌────────────┐        │
                                 │  MS-06     │        │
                                 │  LLM       │        │
                                 │  Gateway   │        │
                                 └────────────┘        │
                                    ▲                  │
                                    │LLM推理请求       │
                                 ┌──┴──────────────────┴──┐
                                 │     全域LLM消费者       │
                                 └────────────────────────┘
```

### 域内依赖关系表

| 源 | 目标 | 依赖类型 | 说明 |
|----|------|---------|------|
| MS-04 | MS-01 | 验证→注册 | ModelValidator验证通过→ModelRegistry标记ACTIVE |
| MS-02 | MS-01 | 加载模型 | InferenceEngine从ModelRegistry加载ACTIVE模型 |
| MS-05 | MS-01 | 部署管理 | ServingManager管理模型版本切换/回滚 |
| MS-05 | MS-02 | 服务编排 | ServingManager编排InferenceEngine的蓝绿/金丝雀部署 |
| MS-03 | MS-02 | 监控推理 | DriftMonitor监控InferenceEngine的输入/输出 |

## §3 域间接口

### 消费依赖（SERVE 依赖其他域）

| 契约/事件 | 供给域 | 强度 | 内容 | 消费子模块 |
|----------|--------|:----:|------|-----------|
| CTR-001 | D-DATA | H | NormalizedMarketData(推理时特征) | MS-02 |
| — | D-ML-TRAIN | H | 模型包格式(CR-MODEL) | MS-01, MS-02 |
| E-ML-01 | D-ML-TRAIN | E | ModelTrained事件 | MS-01 |
| E-RS-03 | D-ML-TRAIN | E | ModelValidated事件 | MS-01 |
| — | D-AUTONOMY-CORE | H | GPU资源+权限校验 | MS-02, MS-06 |
| — | D-INFRA-RUNTIME | S | 运行时调度 | MS-02 |
| E-SG-01 | D-SIGNAL | E | SignalGenerated(可选) | MS-02 |
| — | D-PF-CORE | E | 组合反馈 | MS-03 |
| — | D-PF-ALLOC | E | 分配反馈 | MS-03 |
| — | D-SIMULATION | S | 仿真环境(验证用) | MS-04 |
| — | D-REPORTING | E | 绩效报告 | MS-03 |

### 产出依赖（其他域依赖 SERVE）

| 产出 | 消费域 | 强度 | 说明 | 产出子模块 |
|------|--------|:----:|------|-----------|
| 推理结果 | D-SIGNAL / D-PF-CORE | H | 模型推理输出 | MS-02 |
| E-OP-02 ModelDriftDetected | D-OPS / D-ML-TRAIN / D-FRONTEND | E | 漂移告警 | MS-03 |
| 模型使用审计 | D-COMPLIANCE | E | 模型调用记录 | MS-01 |
| LLM推理服务 | 全域(通过D-AUTONOMY) | H | 统一LLM API | MS-06 |

### SERVE→TRAIN 通信约束（INV-011 + INV-019）

```
SERVE (Warm, H=3) ──✗── 直接调用 ──✗── TRAIN (Cold, H=2)
       │                                        │
       │  E-OP-02 ModelDriftDetected (event)    │
       ├───────────────────────────────────────▶│  MT-05 DriftAdapter
       │  ⚠ INV-019: Warm→Cold必须异步通信      │
       │  (Parquet/Redis Streams)               │
       │                                        │
       │  CR-MODEL 模型包格式 (import)           │
       ├───────────────────────────────────────▶│  MS-01/MS-02加载模型
       │  ⚠ E-0085: hard import依赖             │
       │  SERVE需要理解TRAIN的模型包Schema        │
```

## §4 域事件流

### 产出事件

| 事件ID | 事件名 | 触发条件 | 载荷 | 消费者 |
|--------|--------|---------|------|--------|
| E-OP-02 | ModelDriftDetected | MS-03检测到漂移超阈值 | model_id, drift_type(PSI/performance/JS/IC), drift_score, threshold, detected_at | D-OPS, D-ML-TRAIN(MT-05), D-FRONTEND |
| E-ML-04 | ModelActivated | MS-01标记模型ACTIVE | model_id, version, activated_by, activated_at | D-OPS, D-COMPLIANCE |
| E-ML-05 | ModelDeprecated | MS-01标记模型DEPRECATED | model_id, version, reason, deprecated_at | D-OPS |
| E-ML-06 | InferenceDegraded | MS-02推理熔断触发 | model_id, failure_count, fallback_strategy, degraded_at | D-OPS, D-RISK |

### 消费事件

| 事件ID | 事件名 | 供给域 | SERVE处理 |
|--------|--------|--------|----------|
| E-ML-01 | ModelTrained | D-ML-TRAIN | MS-01接收→注册为DEVELOPMENT状态 |
| E-RS-03 | ModelValidated | D-ML-TRAIN | MS-01接收→更新为VALIDATED→触发MS-04影子验证 |
| E-SG-01 | SignalGenerated | D-SIGNAL | MS-02可选消费(信号驱动的推理触发) |

### INV-011 影子验证门禁流程

```
E-ML-01 ModelTrained ──▶ MS-01 注册 DEVELOPMENT
                              │
E-RS-03 ModelValidated ──▶ MS-01 更新 VALIDATED
                              │
                              ▼
                         MS-04 ModelValidator
                         ├─ 1. 回测验证(Purged K-Fold + Walk-Forward)
                         ├─ 2. 影子交易(≥1周，5个交易日)
                         ├─ 3. 压力测试(极端场景)
                         ├─ 4. AI Construction Governor(Hash+截断+值域)
                         ├─ 5. 可解释性门控(SHAP/LIME)
                         └─ 6. 4级风控决策(APPROVE/REDUCE/REJECT/FLATTEN)
                              │
                         PASS ─┤─ MS-01 标记 ACTIVE ← INV-011门禁通过
                              │
                         FAIL ─┤─ MS-01 保持 VALIDATED + 通知TRAIN
                              │
                              ▼
                         MS-05 ServingManager
                         ├─ 灰度发布(5%→20%→50%→100%)
                         ├─ MS-02 InferenceEngine 加载新模型
                         └─ MS-03 DriftMonitor 开始监控
```

## §5 激活前提

| 前提 | 域 | 必要性 | 说明 |
|------|-----|:------:|------|
| TRAIN至少训练出一个模型 | D-ML-TRAIN | 必须 | MS-01需要模型包才能注册 |
| 数据管道就绪 | D-DATA | 必须 | CTR-001推理时特征可访问 |
| GPU资源可用 | D-AUTONOMY | 必须 | RTX 3090 VRAM分配≥2GB(推理) |
| ONNX Runtime已安装 | 基础设施 | 必须 | CUDA支持+CPU fallback |
| 仿真环境可用 | D-SIMULATION | 可选 | MS-04影子验证需要回测环境 |

### 激活阶段

| 阶段 | 前提 | 可激活子模块 |
|------|------|-------------|
| Phase 1 | TRAIN产出首个模型 | MS-01(注册)、MS-02(推理) |
| Phase 2 | Phase 1 + D-SIMULATION就绪 | MS-04(验证)、MS-05(部署管理) |
| Phase 3 | Phase 2 + 运行≥1周 | MS-03(漂移监控) |
| Phase 4 | Phase 1 + LLM API配置 | MS-06(LLM网关) |

## §6 设计决策记录

| # | 决策 | 理由 | 影响 |
|---|------|------|------|
| 1 | 46子模块→6子模块精简 | 旧草稿子模块粒度过细(MS-06~15全是单一功能点)，按S5流水线骨架归并 | 旧ID映射见§1归并表 |
| 2 | INV-011门禁在SERVE侧执行 | Cold→Hot禁止直接通信，影子验证是Warm平面的职责 | MS-04是INV-011的执行者 |
| 3 | ModelRegistry归SERVE而非TRAIN | 模型注册表是Cold→Hot的桥梁，必须在Warm侧才能执行影子验证门禁 | AGG-008 Model的domain_id=D-ML-SERVE |
| 4 | LLMGateway归SERVE | LLM推理是Warm平面在线服务，TRAIN只消费LLM服务 | D-ML-35~57全部归入MS-06 |
| 5 | Warm平面延迟目标P50<50ms | 推理在Warm执行，不在Hot；50ms满足盘中信号生成需求 | MS-02使用ONNX Runtime CUDA加速 |
| 6 | 推理熔断内嵌MS-02 | 模型推理连续失败时自动熔断+降级，不需要独立子模块 | D-ML-136归入MS-02 |
| 7 | E-0085(SERVE→TRAIN hard)解读 | SERVE需要import TRAIN的模型包格式定义(CR-MODEL Schema)，不是业务逻辑反向依赖 | 模型包格式由MT-01定义，SERVE消费 |
| 8 | 策略生命周期7状态映射Module Registry 4状态 | 草稿+回测+模拟→trial，上线→active，降级→trial，退役→deprecated→archived | MS-05管理策略级，MS-01管理模块级 |
| 9 | MS-06 LLM Security Gateway九层防御 | 所有LLM调用必须经Gateway，不可绕过 | 与D-SECURITY的AISG门禁(INV-015)联动 |
| 10 | D-ML-SERVE无●但有5项触及 | 推理域角色是"为其他域提供模型推理服务"，自身不承载业务逻辑 | 能力定位书§9.3注释6 |

### GPU资源分配(RTX 3090 24GB)——推理时段

| 用途 | VRAM | 说明 |
|------|:----:|------|
| ML模型推理 | 2GB | ONNX Runtime / TensorRT |
| 蒙特卡洛VaR | 2GB | CuPy/PyTorch (D-RISK Phase 2) |
| 本地LLM(qwen3:8b) | 8GB | Ollama管理 |
| 预留 | 12GB | OS + 其他 |

## §7 风险架构(A4)交叉内容

> 来源：风险架构 §1.2 模型风险 + §7 漂移检测与风险闭环 + 绩效归因与策略退化检测模型42

### §7.1 模型风险（§1.2）

> 因模型设定错误、实现错误、误用或漂移导致决策偏差的风险。对齐 Fed SR 26-2(2026.4.17，取代SR 11-7)模型风险管理三要素：Specification Error / Implementation Error / Misuse。注意：SR 26-2明确排除GenAI和Agentic AI（"novel and rapidly evolving"），本系统§15独立覆盖此类风险。

| 子类 | 识别方法 | 度量方法 | 处置机制 | 否决阈值 |
|------|---------|---------|---------|---------|
| 模型设定风险 | 概念健全性审查+基准对比 | 样本外Sharpe偏差+IC衰减 | 模型降级/退役 | 样本外Sharpe<0.5×样本内→否决上线 |
| 实现风险 | 训练-服务一致性校验+代码审计 | 因子计算偏差率+推理偏差 | 修复+回滚 | 因子偏差>0.1%→否决推理结果 |
| 误用风险 | 适用场景审查+输入范围检查 | 输入越界率+场景匹配度 | 拒绝推理+告警 | 输入超出训练分布→否决推理 |
| 概念漂移 | PSI+KS+Wasserstein+ADWIN+CUSUM | PSI>0.25 / KS p<0.01 / 性能衰减 | 触发重训+降级 | PSI>0.25→模型降级为"仅建议" |
| 过拟合风险 | Purged K-Fold+Walk-Forward+Permutation Test | 样本内外Sharpe比+Permutation p值 | 策略否决上线 | 样本外Sharpe<70%样本内→否决 |
| 模型组合风险 | 多模型交互产生的聚合风险：模型间假设不一致(同一风险因子不同分布假设)、对相同输入的共振反应、模型叠加的尾部放大 | SR 26-2(2026.4.17)新增关注点；当前仅单模型验证，组合风险度量暂无覆盖 | 模型注册表(架构预留)+模型间假设一致性检查+组合尾部应力测试 | 组合尾部ES>单模型ES之和→否决组合上线 |

### §7.2 漂移检测五分类

> 对齐 2025-2026 学术前沿

| 漂移类型 | 定义 | 检测方法 | 阈值 |
|---------|------|---------|------|
| 协变量漂移(Covariate Drift) | P_train(X) ≠ P_test(X) | PSI / KS / Wasserstein距离 | PSI>0.25 / KS p<0.01 |
| 概念漂移(Concept Drift) | P_train(Y\|X) ≠ P_test(Y\|X) | 性能衰减+ADWIN+DDM+CUSUM | AUC下降>5% |
| 标签漂移(Label Drift) | P_train(Y) ≠ P_test(Y) | 基准率监控+CUSUM | 基准率偏移>20% |
| 公平性漂移(Fairness Drift) | 子群体性能差异扩大 | 子群体AUC/Recall差异 | 子群体差异>10% |
| 上游数据漂移 | 数据管道Schema/质量变化 | Schema校验+空值率+格式检查 | 空值率>5% / Schema变更 |

### §7.3 CUSUM控制图

> 对齐 2025-2026 学术前沿，补充PSI/KS的持续性偏移检测

| 检测对象 | CUSUM参数 | 预警阈值 | 行动阈值 | 优势 |
|---------|----------|---------|---------|------|
| 模型预测偏差 | 参考值k=0.5σ, 决策区间h=5σ | 单侧累积和>3σ | 累积和>5σ | 检测持续性小幅偏移(PSI/KS可能漏检) |
| 因子IC趋势 | k=0.5×IC标准差 | IC CUSUM>2σ | IC CUSUM>4σ | 比滚动IC更早发现衰减趋势 |
| 交易成本趋势 | k=0.5×成本标准差 | 成本CUSUM>2σ | 成本CUSUM>4σ | 检测隐性成本上升(市场微观结构变化) |

### §7.4 事前PSI检测（§7.1）

**检测矩阵**：

| 检测对象 | 检测方法 | 频率 | 预警阈值 | 行动阈值 |
|---------|---------|------|---------|---------|
| 因子分布 | PSI+KS | 日频 | PSI>0.15 | PSI>0.25→模型降级 |
| 特征分布 | Wasserstein距离+KS | 日频 | W>0.1 | W>0.2→特征工程审查 |
| 模型输出 | 预测分布稳定性+CUSUM | 日频 | 分布偏移>10% | 偏移>20%→模型审查 |
| 上游数据 | Schema校验+空值率+格式 | 实时 | 空值率>2% | 空值率>5%→数据源切换 |

### §7.5 事中在线适应（§7.2）

**三层适应机制**：

| 层次 | 适应方法 | 触发条件 | 延迟 | 风控约束 |
|------|---------|---------|------|---------|
| L1 共形校准更新 | TWC/RWC校准窗口滚动更新 | 每日 | ≤5秒 | 校准后覆盖率不低于目标-1% |
| L2 模型降级 | 模型从"自主执行"降为"仅建议" | PSI>0.25 / 性能衰减>5% | ≤1秒 | 降级后所有决策需人工确认 |
| L3 风控参数收紧 | VaR限额收紧+仓位上限下调 | 市场状态变化(C-021) | ≤5秒 | 收紧幅度由市场状态档位决定 |

### §7.6 事后重训触发（§7.3）

**重训触发条件与流程**：

```
漂移检测超限(PSI>0.25 / 性能衰减>5% / CUSUM>5σ)
    │
    ├──→ [自动触发] 模型降级为"仅建议"模式
    │
    ├──→ [自动触发] 通知Trader+Risk Manager
    │
    ├──→ [自动触发] 收集漂移期间数据+标注
    │
    └──→ [人工审批] 触发重训流程
              │
              ├── 重训数据准备(PIT合规)
              ├── 重训+验证(V1-V6门禁)
              ├── 影子模式运行(≥5个交易日)
              ├── A/B对比(新模型vs旧模型)
              └── 人工审批上线/否决
```

**重训门禁**（对齐能力定位书§2-d约束七）：

| 门禁 | 验证内容 | 通过条件 |
|------|---------|---------|
| V1 因子验证 | 新因子IC/ICIR | \|IC\|>阈值+Purged K-Fold |
| V2 信号验证 | 信号方向准确率 | Walk-Forward通过 |
| V3 策略验证 | 策略PnL/Sharpe/回撤 | Walk-Forward+Permutation Test |
| V4 管线验证 | 全链路端到端 | Walk-Forward+模拟盘 |
| V5 上线验证 | 影子模式运行≥5日+与实盘一致性 | 影子模式PnL偏差<5%+人工审批 |
| V6 风控验证 | 风控触发/熔断/保护性减仓 | 极端场景重放 |

### §7.7 交易绩效归因与策略退化检测模型42

**架构现状**: 完全缺失。"交易绩效监控"无量化框架。

**核心逻辑**: 交易绩效监控不只是"看盈亏"，而是**Performance Attribution**（归因分析）+ **Strategy Degradation Detection**（策略退化检测）。因子IC衰减=策略退化，需要自动检测并降权。

**缺失功能**:

#### 42.1 绩效归因

| 功能点 | 量化方法 | 说明 |
|--------|---------|------|
| 收益归因 | Brinson模型：配置效应+选择效应+交互效应 | 分解收益来源 |
| 因子归因 | 各因子对组合收益的贡献 | 识别哪个因子在赚钱/亏钱 |
| 风险归因 | 各因子对组合风险的贡献 | 识别风险来源 |

#### 42.2 策略退化检测

| 功能点 | 量化方法 | 说明 |
|--------|---------|------|
| IC衰减检测 | 因子IC的60日移动平均趋势 | IC衰减>50%=策略退化 |
| 拥挤度检测 | 使用同一策略的参与者数量估计 | 拥挤度上升=超额收益将消失 |
| 自动降权 | 策略退化时自动将权重降为0 | Man Group AlphaGPT实践 |

#### 42.3 学术与业界对标

**对标1: Brinson "Determinants of Portfolio Performance" (1986, FAJ)**

Brinson模型是绩效归因的学术标准。分解为配置效应+选择效应。

**对标2: Man Group AlphaGPT实践**

因子失效时自动降权至0。每个信号的权重必须可解释。

**建议归属层**: L4 风控层（绩效归因+退化检测）+ 模块48（动态信号权重联动）

## §8 合规约束

> 来源：合规架构 §4 AI合规。核心目标：**AI的每个决策可解释、可追溯、可审计，且人类保留最终否决权**。AI合规是横切关注点，适用于所有合规域中的AI行为——不仅约束交易决策AI，也约束持仓决策AI、报告生成AI等。本节集中定义推理域视角下的AI合规框架。

**EU AI Act(Regulation 2024/1689)分阶段实施**（影响整个§8，非仅§8.3）：
- 2025.2 禁止AI实践条款生效
- 2025.8 通用AI模型义务生效
- 2026.8(原定)→推迟至2027.12.2 高风险AI系统义务(Annex III独立系统，Digital Omnibus 2026.5.7推迟)
- 2027.8(原定)→推迟至2028.8.2 Annex I嵌入式系统(同上推迟)
- 实质性义务不变仅延长过渡期；审慎合规规划仍以2027.12为约束期限

### §8.1 AI风险分类

> 对标EU AI Act风险分级框架(Regulation 2024/1689)。

| 分类 | 定义 | 本系统归属 | 合规义务 |
|------|------|-----------|---------|
| 不可接受风险 | 禁止的AI实践 | ❌不适用 | — |
| 高风险 | Annex III所列AI系统 | 🔶条件适用(GATE-006激活后; GATE-004若涉及EU法域则同时触发GATE-006) | 完整合规义务(Art.9-15) |
| 有限风险 | 透明度义务 | 排他分类(与最小风险二选一)：当前不适用(不满足"意图与自然人交互"这一有限风险触发条件)；GATE-004若涉及自然人交互则可能触发 | Art.50透明度义务(AI生成内容标识+信息披露) |
| 最小风险 | 无特别义务 | 排他分类(与有限风险二选一)：当前归入此类(不与自然人交互)；A6激活后若涉及自然人交互则可能升级为有限风险 | 自愿最佳实践 |

**关键判定**：当前单人使用、不对外服务，不触发EU AI Act高风险义务。但GATE-006(EU法域适用)激活后，本系统可能被归类为高风险AI系统，需满足Art.9-15全部义务(GATE-004若涉及EU法域则同时触发GATE-006)。ESMA 2026.2监管简报明确：AI驱动的算法交易不自动归为EU AI Act高风险用例，但若"意图与自然人交互"(如向客户提供投资建议)则可能属有限风险(Limited Risk)，须满足Art.50透明度义务。EBA 2025.11 AI Act映射评估结论：AI Act与欧盟银行法规无重大矛盾，二者互补——AI Act增加基本权利保护维度，银行法规提供审慎监管框架。

**推理域职责**：MS-02 InferenceEngine是AI风险分类的直接执行者——所有模型推理必须遵守对应风险层级的合规义务。MS-04 ModelValidator在模型上线前验证风险分类的适用性。

### §8.2 可解释性要求

> 对标FINRA Rule 3110(c)(2)、证监会《证券期货业人工智能算法监管指引(试行)》第十二条、SR 26-2模型风险管理(原SR 11-7)。

#### §8.2.1 模型风险分层

| 层级 | 定义 | 可解释性要求 | 方法 |
|------|------|-------------|------|
| Tier 1(最高风险) | 直接影响交易决策的模型 | 完整SHAP级可解释性+反事实分析 | SHAP+LIME双归因 |
| Tier 2(中等风险) | 辅助决策的信号/因子模型 | Top-5特征归因+方向解释 | SHAP摘要图 |
| Tier 3(低风险) | 市场状态/情绪等背景模型 | 全局特征重要性排序 | 特征重要性排名 |

**推理域职责**：MS-01 ModelRegistry在模型注册时记录风险层级；MS-02 InferenceEngine根据风险层级执行对应的可解释性要求。

#### §8.2.2 SHAP+LIME双归因架构

| 方法 | 优势 | 适用场景 | 延迟 |
|------|------|---------|------|
| SHAP | 全局稳定+理论保证(Shapley值) | 事后审计+模型验证 | 批量(非实时) |
| LIME | 局部可调+轻量 | 实时决策归因 | <12ms(缓存优化后) |

**实时归因流程**：
1. C-031分层决策触发时，同步调用LIME生成局部解释
2. 解释结果写入决策日志(→D-REPORTING §7.3.2 feature_attribution字段，由D-REPORTING-03消费)
3. 批量SHAP计算在盘后执行，校准LIME的局部解释一致性

**推理域职责**：MS-02 InferenceEngine在推理时同步调用LIME生成实时归因(<12ms)；MS-03 DriftMonitor在盘后批量执行SHAP校准。

#### §8.2.3 Conformal Prediction：监管级不确定性量化

> 参考Temporal Conformal Prediction(arXiv:2507.05470, 2025)、Action-Conditional Conformal Prediction(ICLR 2026)、TeraSystemsAI Conformal Suite(2025)。

**为什么传统置信度不够**：AI模型输出的概率(如"73%确信该交易安全")不提供有限样本覆盖保证。监管需要的是**数学保证**——"我保证95%的情况下真实结果在预测区间内"，而非概率估计。

| 方法 | 保证 | 分布假设 | 适用场景 |
|------|------|---------|---------|
| 传统VaR | 依赖分布假设 | 正态/GARCH | 参数模型有效时 |
| 贝叶斯方法 | 后验概率 | 先验选择敏感 | 先验可靠时 |
| **Conformal Prediction** | **有限样本覆盖保证** | **无分布假设** | **任何模型+任何分布** |

**核心保证**：P(Y_test ∈ C(X_test)) ≥ 1-α，对任何模型f、任何数据分布P、任何误覆盖水平α∈(0,1)成立，且在有限样本下有效。

**本系统应用**：

| 应用 | 方法 | 保证 | 合规架构章节 |
|------|------|------|------------|
| 交易决策安全保证 | Action-Conditional CP | 每个交易动作的条件安全保证 | §1.1(交易行为合规) |
| 模型预测区间 | Conformalized Quantile Regression | VaR覆盖率的有限样本保证 | §4.3 |
| 非平稳适应 | Adaptive Conformal Inference(ACI) | 分布漂移下的覆盖保持 | §4.2.3(本节)/§10.2 #40(门禁:GATE-003/006) |
| 组合选择 | Conformal Predictive Portfolio Selection | VaR覆盖率的组合级保证 | §2.1 |

**与SR 26-2的关联**：SR 26-2(原SR 11-7)要求模型验证包含"结果分析(Outcome Analysis)"，Conformal Prediction提供了分布无关的覆盖保证，是满足该要求的数学严格方法。SR 26-2(2026)虽排除GenAI/Agentic AI，但三支柱框架(独立验证+持续监控+文档化)仍适用。

Conformal Predictive Portfolio Selection(HKUST, DMO-FinTech 2026)将CP从风险度量扩展至组合选择——用CP构建的预测区间下界估计VaR，再以投影梯度下降优化组合权重，在禁止做空约束下一致优于等权组合和非CP对照。这为合规架构§2.1持仓合规提供了数学严格的风险预算方法。

**推理域职责**：MS-02 InferenceEngine集成Conformal Prediction为推理结果提供不确定性量化；MS-03 DriftMonitor使用Adaptive Conformal Inference(ACI)在分布漂移下保持覆盖。

### §8.3 模型注册与治理

> 参考Two Sigma欺诈事件(2025)教训——模型参数未受控访问导致$165M损失。

**SR 26-2模型风险管理(原SR 11-7，2026.4.17 Fed/OCC/FDIC联合发布)**：

| # | 关键变化 | 说明 |
|---|---------|------|
| ① | 物质性分层(Materiality-Based Tiering) | 取代统一监管——按模型暴露+模型目的二维评估决定治理强度 |
| ② | 模型定义收窄 | 需同时满足"复杂量化方法+统计/经济/金融理论+量化输出"三要素，简单算术/确定性规则/无理论支撑软件明确排除 |
| ③ | 验证独立性放宽 | 从组织结构要求放宽为"有效挑战"原则 |
| ④ | 验证频率触发式 | 从年度周期改为基于物质性+变更速度+数据可用性的触发式复审 |
| ⑤ | GenAI/Agentic AI排除 | 明确排除在范围外，机构计划单独发布AI模型风险RFI |
| ⑥ | 适用门槛 | 总资产>$30B的银行机构(本系统不满足适用门槛，无论门禁状态均不直接适用，但三支柱框架原则可参考) |
| ⑦ | 不可强制执行 | 不合规本身不导致监管批评(non-enforceable) |

SR 26-2三支柱框架(开发/验证/治理)仍为本系统模型风险管理基础；GenAI/Agentic AI排除意味着本系统AI交易模型暂无正式监管规则书，参照Turing Institute《GenAI MRM in Financial Services》(2025.12)及Treasury AIEOG AI词汇表+NIST AI RMF金融适配版(2026.2)补充。EU AI Act分阶段实施时间线见§8开头。

#### §8.3.1 模型注册表

| 字段 | 说明 | 不可变 |
|------|------|:------:|
| model_id | 全局唯一模型标识 | ✅ |
| version | 语义化版本号 | ✅ |
| code_hash | 模型代码SHA-256指纹 | ✅ |
| param_hash | 模型参数SHA-256指纹 | ✅ |
| training_data_hash | 训练数据集SHA-256指纹 | ✅ |
| approval_ts | 人工审批时间戳 | ✅ |
| active | 是否为当前活跃版本 | ❌ |
| performance | 最新性能指标(Sharpe/IC/回撤) | ❌ |

**铁律(来自Two Sigma教训)**：
1. 模型代码与模型参数**分离存储**，参数变更需独立审批
2. 模型参数存储区**读写分离**——写操作需人工审批+双人确认
3. 参数变更**实时监控**——任何未授权参数变更触发即时告警
4. 模型版本**不可变**——上线后代码和参数不可修改，只能发布新版本
5. 参数变更**密码学验证**——VCP v1.1(VCP-GOV)提出模型参数变更的哈希链验证，可在分钟级检测未授权修改(Two Sigma案例中4年未检测到的问题可在分钟级发现)

**推理域职责**：MS-01 ModelRegistry是模型注册表的直接实现者，必须严格执行8字段注册+5条铁律。AGG-008 Model的不变量(至多一个active版本；active⇒approval_ts≠None)是铁律4和审批要求的域模型保障。

#### §8.3.2 模型生命周期合规门禁

```
[开发] → [注册] → [验证] → [审批] → [上线] → [监控] → [退役]
   │        │        │        │        │        │        │
   │        │        │        │        │        │        └→ 退役策略指纹入库
   │        │        │        │        │        └→ 漂移检测+性能退化告警
   │        │        │        │        └→ 影子模式运行≥5个交易日
   │        │        │        └→ 人工审批(必须)
   │        │        └→ V3+V4验证通过(→能力定位书§2-d约束七)
   │        └→ 注册表写入(不可变)
   └→ 代码+参数+训练数据指纹绑定
```

**推理域职责**：MS-01 ModelRegistry执行[注册]→[审批]门禁；MS-04 ModelValidator执行[验证]门禁(含影子模式运行≥5个交易日)；MS-05 ServingManager执行[上线]门禁(灰度发布)；MS-03 DriftMonitor执行[监控]门禁(漂移检测+性能退化告警)。这与§4 INV-011影子验证门禁流程一致。

### §8.4 AI伦理声明

> 对标ESRB 2025年12月报告(AI与系统性风险)、FSB 2024年AI金融稳定报告。

| 原则 | 承诺 | 执行机制 |
|------|------|---------|
| 不操纵市场 | 所有交易决策基于公开信息和合法因子 | C-004市场操纵检测 |
| 不剥削散户 | 追求风险调整后合理收益 | 参与率限制+冲击成本控制 |
| 决策透明 | 每笔自主决策有完整决策溯源链 | C-030决策可解释性 |
| 遵守法规 | 遵守所在市场所有适用法规 | 合规架构§7法规映射表 |
| 反对AI军备竞赛 | 不参与速度竞争，专注策略质量 | B-017不做HFT |

**推理域职责**：MS-02 InferenceEngine的推理结果必须支持决策透明原则——每笔推理输出附带可解释性归因；MS-03 DriftMonitor确保模型不偏离伦理约束。

## §9 MLOps推理服务规格（源自学习系统架构A8 §9.1 + §11.4）

> **搬入来源**: 学习系统架构(A8) §9.1元学习维度中与推理/服务相关的部分 + §11.4 MLOps闭环中与模型服务相关的部分。推理域是MLOps闭环在模型部署侧的执行者——影子验证、金丝雀上线、A/B测试、模型版本热替换均由推理域承载。与D-OPS §8.8 MLOps闭环的关系：D-OPS关注运维流程编排，本节关注推理域如何执行MLOps闭环中的部署/验证/监控动作。

### §9.1 在线学习与模型推理集成（A8§9.1）

> 来源：学习系统架构(A8) §9.1元学习维度。元学习的三层参数优化中，第1层"实时微调"与推理域直接相关——在线学习微调参数需要推理域提供实时推理反馈。

**在线学习与推理集成架构**:

| 层次 | 方法 | 触发条件 | 推理域执行 | 延迟 | 风控约束 |
|------|------|---------|-----------|------|---------|
| L1 实时微调 | 在线学习微调参数 | 每日 | MS-02 InferenceEngine加载微调后参数 | ≤5秒 | 微调后模型性能不低于微调前-1% |
| L2 周期优化 | 每周/每月参数优化 | 定期 | MS-05 ServingManager编排优化→验证→部署 | 小时级 | 优化后模型必须通过MS-04影子验证 |
| L3 结构进化 | 季度级模型结构进化 | 季度 | MS-01→MS-04→MS-05完整生命周期 | 天级 | 结构进化必须通过V1-V6全部门禁 |

**在线学习推理约束**:

| 约束 | 说明 | 执行子模块 |
|------|------|-----------|
| 参数一致性 | 在线微调参数与训练侧参数必须通过Feature Store保证训练-服务一致性 | MS-02 + Feature Store(R-68) |
| 回滚能力 | 在线微调后性能下降→自动回滚至微调前参数 | MS-05 ServingManager |
| 推理不中断 | 参数更新期间推理服务不中断（原子切换） | MS-02 InferenceEngine |
| 审计追踪 | 每次在线微调记录参数变更+性能对比+审批记录 | MS-01 ModelRegistry |

### §9.2 影子验证门禁INV-011执行规格（A8§9.1 + §11.4）

> 来源：学习系统架构(A8) §9.1元学习维度 + §11.4 MLOps闭环。INV-011(Cold→Hot禁止直接通信)的影子验证门禁由推理域MS-04执行。§4已有INV-011流程图，本节补充推理域视角的执行规格。

**影子验证执行规格**:

| 阶段 | 执行者 | 输入 | 输出 | 通过条件 | 失败处理 |
|------|--------|------|------|---------|---------|
| 1.回测验证 | MS-04 | 新模型+历史数据 | BacktestReport | Purged K-Fold+Walk-Forward通过 | 保持VALIDATED+通知TRAIN |
| 2.影子交易 | MS-04 | 新模型+实时数据 | ShadowReport | ≥1周(5个交易日)影子PnL偏差<5% | 延长影子期或退回TRAIN |
| 3.压力测试 | MS-04 | 新模型+极端场景 | StressTestReport | 极端场景下不触发风控否决 | 标记风险+限制使用场景 |
| 4.AI Construction Governor | MS-04 | 新模型代码 | GovernanceReport | 公式Hash一致+回归截断+值域偏差<阈值 | 退回代码修正 |
| 5.可解释性门控 | MS-04 | 新模型+SHAP/LIME | ExplanationReport | Tier1/Tier2/Tier3对应可解释性要求满足 | 补充解释或降级模型层级 |
| 6.4级风控决策 | MS-04 | 全部验证结果 | DecisionResult | APPROVE | REDUCE→限制仓位/REJECT→退回/FLATTEN→紧急回滚 |

**影子验证与MLOps闭环的关系**:

```
MLOps闭环:  监控效果 → 漂移检测 → 重训练 → [影子验证] → 金丝雀上线 → 闭环
                                           ↑
                                    推理域MS-04执行
                                    ├─ 新模型与旧模型并行运行
                                    ├─ 仅比较不执行(不产生实际交易)
                                    ├─ 影子PnL偏差<5%才可通过
                                    └─ 通过→MS-01标记ACTIVE→MS-05灰度发布
```

### §9.3 模型版本热替换机制（A8§9.1）

> 来源：学习系统架构(A8) §9.1元学习维度。模型版本热替换是推理域的核心能力——在不中断推理服务的情况下切换模型版本。

**模型版本热替换流程**:

```
MS-01 ModelRegistry          MS-02 InferenceEngine         MS-05 ServingManager
     │                              │                            │
     │  新版本标记ACTIVE            │                            │
     ├─────────────────────────────→│                            │
     │                              │  1.预加载新模型到GPU        │
     │                              │  2.原子切换推理指针         │
     │                              │  3.旧模型保留在内存(回滚用) │
     │                              │  4.验证新模型推理正常       │
     │                              │  5.延迟释放旧模型内存       │
     │                              ├───────────────────────────→│
     │                              │                            │ 记录版本切换
     │                              │                            │ 通知D-OPS
```

**热替换约束**:

| 约束 | 说明 | 执行方式 |
|------|------|---------|
| 原子性 | 模型切换必须原子执行，不可出现半切换状态 | MS-02使用原子指针切换+GPU内存双缓冲 |
| 可回滚 | 热替换后5分钟内可一键回滚至旧版本 | MS-02保留旧模型在内存(延迟5分钟释放) |
| 推理不中断 | 热替换期间推理请求不丢失 | MS-02请求队列缓冲+新模型就绪后切换 |
| GPU内存安全 | 新旧模型同时加载时GPU VRAM不超限 | MS-02预检VRAM+不足时先卸载非必要模型 |
| 审计记录 | 每次热替换记录版本变更+时间戳+操作者 | MS-01 ModelRegistry记录+审计日志 |

### §9.4 模型部署与推理接口（A8§11.4）

> 来源：学习系统架构(A8) §11.4 MLOps闭环中与模型服务相关的接口定义。定义推理域对外提供的模型部署与推理服务接口。

**模型部署接口**:

| 接口 | 供给方 | 消费方 | 载荷 | 说明 |
|------|--------|--------|------|------|
| ModelDeployRequest | D-ML-TRAIN / D-OPS | MS-05 ServingManager | model_id, version, deploy_strategy(canary/blue-green), canary_pct | 请求部署新模型版本 |
| ModelDeployCompleted | MS-05 ServingManager | D-OPS / D-ML-TRAIN | model_id, version, deploy_status, active_pct | 部署完成通知 |
| ModelRollbackRequest | D-OPS | MS-05 ServingManager | model_id, reason, target_version | 请求回滚至指定版本 |
| ModelRollbackCompleted | MS-05 ServingManager | D-OPS | model_id, from_version, to_version, rollback_status | 回滚完成通知 |

**影子部署验证接口**:

| 接口 | 供给方 | 消费方 | 载荷 | 说明 |
|------|--------|--------|------|------|
| ShadowValidationStart | MS-04 ModelValidator | MS-05 ServingManager | model_id, new_version, shadow_duration | 启动影子验证 |
| ShadowMetricsReport | MS-04 ModelValidator | D-OPS / D-ML-TRAIN | model_id, shadow_pnl, shadow_ic, deviation_pct | 影子验证指标报告 |
| ShadowValidationResult | MS-04 ModelValidator | MS-01 ModelRegistry | model_id, result(PASS/FAIL), evidence | 影子验证结果 |

**A/B测试 for Model Serving接口**:

| 接口 | 供给方 | 消费方 | 载荷 | 说明 |
|------|--------|--------|------|------|
| ABTestStart | D-OPS / D-ML-TRAIN | MS-05 ServingManager | model_id, version_a, version_b, traffic_split, duration | 启动A/B测试 |
| ABTestMetricsReport | MS-05 ServingManager | D-OPS / D-ML-TRAIN | model_id, metrics_a, metrics_b, statistical_significance | A/B测试指标报告 |
| ABTestResult | MS-05 ServingManager | MS-01 ModelRegistry | model_id, winner(a/b/none), confidence_level | A/B测试结论 |

**A/B测试执行规格**:

| 参数 | 说明 | 默认值 |
|------|------|--------|
| traffic_split | 新旧模型流量分配比例 | 5%新/95%旧(初始)→20%→50%→100% |
| min_duration | 最短测试持续时间 | 5个交易日 |
| significance_level | 统计显著性水平 | p<0.05 |
| metrics | 比较指标 | IC/Sharpe/方向准确率/推理延迟 |
| auto_rollback | 效果差时自动回滚 | 是(新模型IC下降>20%自动回滚) |
| winner_criteria | 胜出判定标准 | 新模型IC显著优于旧模型(p<0.05)且绝对提升>5% |

### §9.5 漂移感知集成在推理域的执行（A8§11.4）

> 来源：学习系统架构(A8) §11.4 MLOps闭环。漂移感知集成(Drift-Aware Ensemble)在推理域的执行——根据各模型的漂移适应能力动态调整推理时的模型权重。

**漂移感知集成执行规格**:

| 执行步骤 | 执行者 | 说明 |
|---------|--------|------|
| 1.漂移适应能力评估 | MS-03 DriftMonitor | 评估各模型在当前市场制度下的漂移适应能力(近期IC稳定性+PSI趋势) |
| 2.权重重分配 | MS-02 InferenceEngine | 漂移适应能力强的模型获得更高推理权重 |
| 3.制度变化检测 | MS-03 DriftMonitor | 宏观漂移→触发权重重分配(与A8§3.2多尺度漂移检测联动) |
| 4.权重变更审计 | MS-01 ModelRegistry | 记录权重变更原因+漂移证据+变更前后权重 |

**漂移感知集成约束**:

| 约束 | 说明 |
|------|------|
| 权重变更频率 | ≤1次/交易日(防止过度调整) |
| 单模型权重上限 | ≤60%(防止单模型垄断) |
| 权重之和 | =1.0(归一化约束) |
| 权重变更审批 | 权重变化>10%需人工审批 |

### §9.6 Feature Store推理侧集成（A8§3.3）

> 来源：学习系统架构(A8) §3.3采集增强中Feature Store(R-68)与推理域的集成。Feature Store是消除训练-服务偏差的关键基础设施。

**Feature Store推理侧职责**:

| 职责 | 执行子模块 | 说明 |
|------|-----------|------|
| 在线特征服务 | MS-02 InferenceEngine | 推理时通过Feature Store获取PIT AS OF JOIN特征，确保与训练时特征一致 |
| 训练-服务一致性校验 | MS-04 ModelValidator | 验证推理时特征值与训练时特征值的一致性(偏差<0.1%) |
| 特征Schema版本管理 | MS-01 ModelRegistry | 模型注册时绑定特征Schema版本，推理时按版本查询 |
| 特征缺失降级 | MS-02 InferenceEngine | Feature Store不可用时降级为本地缓存特征+告警 |

**Feature Store与推理域数据流**:

```
Feature Store ──PIT AS OF JOIN──→ MS-02 InferenceEngine ──推理结果──→ D-SIGNAL/D-PF-CORE
       │                                │
       │  特征Schema版本                │  特征一致性校验
       ├───────────────────────────────→│
       │                                │
       │  特征分布统计                   │  漂移检测输入
       └───────────────────────────────→MS-03 DriftMonitor
```

---

## §8 运维架构(A9)规格

> **搬入来源**: 运维架构(A9) §1.3 GPU调度策略(推理视角) + §2.2 Hot平面(ML推理) + §4应急保命轨(ML降级)
> **搬入原则**: 将A9中D-ML-SERVE域承载的运维规格搬入本域，保持A9原文颗粒度。

### §8.1 GPU调度——推理视角（A9§1.3）

| 时段 | 推理模型 | 显存占用 | 热备状态 | 切换耗时 |
|------|---------|:--------:|---------|:--------:|
| 盘前(08:30-09:00) | Whisper+LLM-7B+风控NN | 8-10GB | CPU RAM热备 | — |
| 盘中(09:15-15:00) | Whisper+LLM-7B+风控NN | 8-10GB | CPU RAM热备 | — |
| 午休(11:30-13:00) | LLM-7B(最小集) | 4GB | CPU RAM热备 | ~30s |
| 盘后(15:00-15:30) | LLM-7B(最小集) | 4GB | CPU RAM热备 | ~60s |
| 夜间(15:30-08:30) | LLM-7B(最小集)+训练(时分) | 4GB互斥 | CPU RAM热备 | ~60s |

> **推理硬约束**：风控NN常驻显存2GB，不可卸载(即使在GPU OOM紧急卸载时也保留)。推理模型权重在CPU RAM保持热备，GPU卸载后可~5s恢复。

### §8.2 GPU异常处理——推理视角（A9§1.3.3）

| 异常 | 检测方式 | 推理域动作 | 恢复策略 |
|------|---------|-----------|---------|
| GPU OOM | CUDA Error捕获 | 1.终止当前推理任务 2.卸载非必要模型(保留风控NN) 3.告警 | 释放显存后重新加载最小集 |
| GPU温度>85°C | nvidia-smi监控 | 1.降频GPU 2.减少并发推理 3.告警 | 温度<80°C后恢复 |
| GPU驱动崩溃 | nvidia-smi无响应 | 1.P5进程重启 2.降级为CPU推理 3.告警 | nvidia-smi恢复后重新初始化 |
| 推理延迟>2×基线 | P5自监控 | 1.切换轻量模型 2.告警 | 延迟恢复后切回原模型 |

### §8.3 ML推理降级——保命轨视角（A9§4）

| 降级路径 | ML推理动作 | 对应子模块 |
|---------|-----------|-----------|
| D-L0→D-L1 | 释放GPU非必要模型(保留风控NN+LLM最小集) | MS-02 CPU降级+推理熔断 |
| D-L1→D-L2 | 仅保留风控NN，LLM推理降级为CPU | MS-02 CPU降级 |
| D-L2→D-L3 | 风控NN保持运行，其他推理全部停止 | MS-02 推理熔断 |
| GPU完全不可用 | 降级为CPU推理(延迟增大10-100×) | MS-02 CPU降级+推理熔断 |

## 来自Agent架构(A7)的内容

### 来自Agent架构(A7) §8.1 路由架构（级联控制器）— 本地模型推理部分

> 源自Agent架构(A7) §8.1 路由架构。推理域(D-ML-SERVE)是LLM Agent路由架构中本地LLM推理的执行者——MS-02 InferenceEngine承载本地模型推理，MS-06 LLMGateway管理LLM API统一集成。

**级联控制器中的推理域角色**：

```
┌─────────────────────────────────────────────────────────────────┐
│                    LLM Agent路由架构                              │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              Stage 1: 任务分类器                          │   │
│  │  输入: Agent请求（任务描述+上下文）                        │   │
│  │  输出: 任务类型标签 + 复杂度评分                           │   │
│  │  实现: 本地轻量分类器（规则引擎+少量LLM推理）              │   │
│  │  延迟: <50ms                                              │   │
│  └──────────────────────────┬──────────────────────────────┘   │
│                             │                                   │
│  ┌──────────────────────────▼──────────────────────────────┐   │
│  │              Stage 2: 模型选择器                          │   │
│  │  输入: 任务类型 + 复杂度评分 + 成本预算                    │   │
│  │  输出: 目标模型（本地/API）+ 推理参数                     │   │
│  │  实现: 成本-性能权衡路由（参考xRouter/CSCR）              │   │
│  │  延迟: <10ms                                              │   │
│  └──────────────────────────┬──────────────────────────────┘   │
│                             │                                   │
│  ┌──────────────────────────▼──────────────────────────────┐   │
│  │              Stage 3: 成本控制器                          │   │
│  │  输入: 模型选择结果 + 月度预算 + 已消耗成本               │   │
│  │  输出: 批准/降级/拒绝                                    │   │
│  │  实现: 预算管理+降级策略（参考BEST-Route）                │   │
│  │  延迟: <5ms                                               │   │
│  └──────────────────────────┬──────────────────────────────┘   │
│                             │                                   │
│              ┌──────────────┼──────────────┐                   │
│              │              │              │                    │
│  ┌───────────▼───┐  ┌──────▼──────┐  ┌───▼───────────┐       │
│  │ 本地LLM       │  │ API LLM     │  │ 规则引擎      │       │
│  │ (RTX 3090)    │  │ (DeepSeek/  │  │ (无LLM)       │       │
│  │               │  │  GLM/Claude)│  │               │       │
│  │ · Qwen2.5-7B  │  │            │  │ · 确定性规则   │       │
│  │ · DeepSeek-7B │  │ · DeepSeek  │  │ · 参数查找     │       │
│  │ · 本地微调模型 │  │   V4 Pro   │  │ · 阈值判断     │       │
│  │               │  │ · GLM-5.1   │  │               │       │
│  │ 显存预算:      │  │ · Claude    │  │ 延迟: <1ms    │       │
│  │ 盘中~6GB(含KV cache)│  │            │  │               │       │
│  │ 盘前~8GB(含KV cache)│  │ 成本: 按token│  │ 成本: 0       │       │
│  │ 延迟: 1-5s    │  │ 延迟: 2-10s │  │               │       │
│  └───────────────┘  └────────────┘  └───────────────┘       │
│       ↑MS-02执行         ↑MS-06执行    ↑无LLM                │
└─────────────────────────────────────────────────────────────────┘
```

**推理域在路由架构中的职责**：

| 路由目标 | 推理域执行子模块 | 说明 |
|---------|---------------|------|
| 本地LLM推理 | MS-02 InferenceEngine | Qwen2.5-7B/DeepSeek-7B本地推理，延迟1-5s |
| API LLM调用 | MS-06 LLMGateway | DeepSeek V4 Pro/GLM-5.1/Claude API统一管理 |
| 规则引擎 | 无需推理域 | 确定性规则，无LLM参与 |

### 来自Agent架构(A7) §8.2 本地/API分时分任务路由策略 — GPU显存分配/推理调度

> 源自Agent架构(A7) §8.2。推理域是GPU显存分配策略的直接执行者——MS-02管理本地LLM推理的显存占用，MS-06管理API LLM的调用调度。

**按任务类型路由（推理域视角）**：

| 任务类型 | 复杂度 | 路由目标 | 推理域执行 | 对应Agent |
|---------|:------:|---------|-----------|----------|
| 风控否决判定 | 低 | 规则引擎 | 无需推理 | 风控Agent |
| 信号权重微调 | 低 | 本地LLM | MS-02本地推理 | 信号Agent |
| 做T参数微调 | 低 | 本地LLM | MS-02本地推理 | 做T Agent |
| 异常分类 | 中 | 本地LLM | MS-02本地推理 | 监控Agent |
| 信号生成 | 中 | 本地LLM | MS-02本地推理 | 信号Agent |
| 市场状态判定 | 中-高 | API+本地混合 | MS-02+MS-06混合 | 市场状态Agent |
| 归因分析 | 中 | 本地LLM | MS-02本地推理 | 归因Agent |
| 策略代码生成 | 高 | API LLM | MS-06 API调用 | 研究Agent |
| 战略意图生成 | 高 | API LLM | MS-06 API调用 | 编排Agent |
| 自反反思(L1) | 中 | 本地LLM | MS-02本地推理 | 所有Agent |
| 自反反思(L2/L3) | 高 | API LLM | MS-06 API调用 | 所有Agent |

**按时段路由（推理域视角）**：

| 时段 | 本地LLM状态 | API LLM策略 | 推理域GPU显存分配 |
|------|-----------|-----------|-----------------|
| 盘前(8:00-9:15) | 可用（显存~8GB(含KV cache)） | 允许（研究/策略任务） | MS-02加载完整推理模型集 |
| 集合竞价(9:15-9:30) | 可用 | 限制（仅紧急任务） | MS-02预留交易推理资源 |
| 盘中(9:30-15:00) | 限制（显存~10GB（LLM~6GB+交易引擎~4GB）） | 限制（仅战略层+反思L2/L3） | MS-02仅保留最小推理集+风控NN |
| 盘后(15:00-24:00) | 可用（显存释放） | 允许（归因/研究/反思） | MS-02释放交易引擎显存→加载完整推理模型 |

**GPU显存分配策略（推理域执行）**：

| 时段 | 交易引擎 | 本地LLM | 剩余可用显存 | LLM模型选择 |
|------|---------|---------|------------|-----------|
| 盘中 | ~4GB | ~6GB(含KV cache) | ~14GB（24-4-6） | Qwen2.5-7B（量化4bit） |
| 盘前 | ~0GB | ~8GB(含KV cache) | ~16GB（24-0-8） | Qwen2.5-7B（量化4bit） |
| 盘后 | ~0GB | ~12GB(含KV cache) | ~12GB（24-0-12） | Qwen2.5-7B（量化4bit）或微调模型 |

> **注**：本地LLM显存含模型权重(~4GB)+KV cache运行时，详见§17.8 LP-008。14B模型AWQ 4-bit权重约8GB+KV cache，24GB显存下可用但紧张，建议48GB以上GPU使用。

### 来自Agent架构(A7) §8.3 成本控制 — 推理成本优化

> 源自Agent架构(A7) §8.3 成本控制。推理域是LLM成本控制的执行者——MS-06 LLMGateway管理API调用预算和降级策略。

**预算管理（推理域执行）**：

| 维度 | 预算 | 监控频率 | 超预算处理 | 推理域执行 |
|------|------|---------|-----------|-----------|
| 月度API总成本 | ¥500/月 | 日度 | 超预算110%→降级至本地LLM；超预算120%→暂停API调用 | MS-06执行降级/暂停 |
| 单日API成本 | ¥30/天（软限制） | 实时 | 超预算→当日剩余时间降级至本地LLM | MS-06切换路由策略 |
| 单次API调用成本 | ¥0.5/次 | 实时 | 超预算→降级至本地LLM或拒绝 | MS-06单次调用控制 |
| 月度本地推理成本 | 电费~¥50/月 | 月度 | 无硬限制（电费可控） | MS-02本地推理无额外成本 |

**成本感知路由（推理域执行）**：

| 路由决策 | 成本阈值 | 性能阈值 | 推理域执行 |
|---------|---------|---------|-----------|
| API→本地降级 | API成本>月预算80% | 性能损失<5% | MS-06降级至MS-02本地推理 |
| 本地→API升级 | 本地LLM推理失败/质量不足 | — | MS-02→MS-06升级至API |
| 小模型多次采样 | — | 性能损失<1% | MS-02本地7B模型采样3次+选最优 |
| 规则引擎兜底 | API+本地均不可用 | — | MS-02降级为规则引擎输出 |

**降级策略（推理域执行）**：

| 降级级别 | 触发条件 | 推理域降级行为 | 恢复条件 |
|---------|---------|--------------|---------|
| LLMDeg-0(正常) | 月度成本<80%预算 | 全功能路由（MS-06 API+MS-02本地） | — |
| LLMDeg-1(节约) | 月度成本80%-100%预算 | 非关键任务MS-06→MS-02降级 | 月度成本回落至80%以下 |
| LLMDeg-2(严格) | 月度成本100%-110%预算 | 仅战略层+反思L2/L3使用MS-06 API | 月度成本回落至100%以下 |
| LLMDeg-3(紧急) | 月度成本>110%预算 | 全部MS-06→MS-02降级+规则引擎 | 人工确认后恢复 |
| LLMDeg-4(熔断) | >120%预算 | 暂停所有MS-06 API调用，仅MS-02+规则引擎 | 紧急人工介入+预算重置 |

### 来自Agent架构(A7) §1.3 市场状态Agent(RegimeDet) — 对应域含D-ML-SERVE

> 源自Agent架构(A7) §1.3 战术Agent。市场状态Agent的归属域包含D-ML-SERVE——复杂市场状态判定需要ML模型推理支撑。

**市场状态Agent与推理域的关系**：

| 属性 | 市场状态Agent(Regime Det) — 推理域相关 |
|------|--------------------------------------|
| **职责** | 市场状态判定(11态)、状态转换预警——复杂状态需MS-02模型推理支撑 |
| **输入** | 量价数据、宏观因子、跨市场数据 |
| **输出** | 市场状态标签(11态)、状态转换概率 |
| **对应域(归属域)** | D-SIGNAL + **D-ML-SERVE** |
| **LLM路由** | API+本地混合（复杂状态需推理，简单状态本地处理） |

**市场状态Agent→推理域的数据流**：

```
市场状态Agent ──复杂状态推理请求──▶ MS-06 LLMGateway
                                      │
                                      ├── 简单状态(明确趋势/震荡) → MS-02本地LLM推理
                                      └── 复杂状态(混沌/转折点) → MS-06 API LLM推理
                                      │
                                      ▼
                                 市场状态标签(11态) + 状态转换概率
```

### 来自Agent架构(A7) §9.2.2 Agent→业务功能域消费映射 — 与推理域相关的Agent映射

> 源自Agent架构(A7) §9.2.2。推理域(D-ML-SERVE)是多个Agent的消费域——信号Agent和市场状态Agent均消费D-ML-SERVE的模型推理服务。

| Agent | 消费域 | 产出域 | 与D-ML-SERVE的关系 |
|-------|--------|--------|------------------|
| 信号Agent | D-FACTOR、D-SIGNAL、**D-ML-SERVE（模型推理）** | D-SIGNAL、D-SELL-DECISION | 消费域：MS-02模型推理→信号权重微调 |
| 市场状态Agent | D-DATA、D-CROSS-ASSET🔴、**D-ML-SERVE（模型推理）** | D-SIGNAL | 消费域：MS-02+MS-06混合推理→复杂市场状态判定 |

**LLM路由架构组件与推理域的映射**：

| 架构组件 | 对应功能域 | 与D-ML-SERVE的关系 |
|----------|----------|------------------|
| LLM路由 | D-AUTONOMY-CORE（主域）+ D-INFRA-OPS + D-INTEGRATION | 路由控制器决定请求发往MS-02(本地)还是MS-06(API) |

### 来自Agent架构(A7) §17 遗留问题裁定 — 与推理域相关的条目

> 源自Agent架构(A7) §17 遗留问题裁定。以下LP条目与推理域直接相关——涉及GPU显存、影子模式测试、本地LLM选型等推理域核心约束。

| 编号 | 遗留问题 | 裁定 | 硬边界门禁条件 | 与D-ML-SERVE的关系 |
|:----:|---------|:----:|--------------|------------------|
| LP-002 | Agent记忆向量检索(RAG) | 🔴 暂缓(不能建) | ①GPU显存≥48GB；②需要非结构化数据语义检索；③AUM≥500万 | 嵌入模型需~2GB显存，挤占MS-02推理配额；RAG检索需MS-02推理支撑 |
| LP-004 | 影子模式测试 | 🔴 暂缓(不能建) | ①GPU显存≥48GB；②多GPU架构；③或战略Agent影子测试走API推理 | 影子模式是MS-04 ModelValidator的核心验证方式，GPU限制导致无法本地并行运行新旧模型 |
| LP-006 | 混沌工程环境 | 🟢 能建 | —（在仿真环境D-SIMULATION执行） | 混沌实验可验证MS-02推理熔断和MS-06 API降级的容错性 |
| LP-008 | 本地LLM选型 | 🟢 能建 | Qwen2.5-7B-Instruct+DeepSeek-7B(备选)，均AWQ 4-bit | 直接决定MS-02本地推理模型选择和显存预算 |
| LP-014 | MCP×A2A集成框架 | 🔴 暂缓(不能建) | ①外部工具≥10个；②多Agent框架互操作；③有第二位开发人员加入 | MCP集成可能影响MS-06 LLMGateway的外部API调用方式 |

**LP-008 本地LLM选型详情**（推理域核心LP）：

| 维度 | 说明 |
|------|------|
| MVP选型 | Qwen2.5-7B-Instruct + DeepSeek-7B(备选)，均AWQ 4-bit量化（~4GB显存），用于战术层/执行层低延迟任务；战略层用API(DeepSeek V4 Pro/GLM-5.1) |
| 显存预算 | 盘中GPU：本地LLM ~6GB(含KV cache, 其中模型权重~4GB+KV cache~2GB) + 交易引擎 ~4GB = ~10GB，在24GB范围内 |
| 备选方案 | Qwen3-8B稳定版发布且AWQ 4-bit量化可用时可升级（需验证显存≤6GB） |
| 未来升级门禁 | ①Qwen3-8B稳定+AWQ可用时；②GPU≥48GB可跑14B模型；③本地LLM质量持续低于API且影响决策质量→全部切换API |
