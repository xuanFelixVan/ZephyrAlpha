---
module_id: ARCHITECTURE_001
version: 5.6.0
status: Active
created_date: 2026-04-01
last_updated: '2026-04-08'
owner: 首席文档架构师
standard_type: 专业量化机构文档
applicable_scope: 全系统技术架构 Layer 0-11
compliance_level: 专业标准
parent_document: ./INDEX.md
implementation_status: 进行中
responsibility:
  - 系统整体分层架构与跨层数据流权威说明
  - 与模块职责边界文档对齐（见 MODULE_RESPONSIBILITY_BOUNDARIES.md）
---

# 统一架构 (UNIFIED_ARCHITECTURE)
> **核心职责**: 定义清风量化系统的整体架构设计、模块组织和层级关系，作为系统架构的权威参考文档
> **职责边界**: 
> - ✅ 本文档负责：系统架构设计和模块关系说明相关内容
> - ❌ 本文档不负责：其他模块内容


> **版本**: v5.6
> **创建日期**: 2026-03-30
> **Layer**: Layer 0-11
> **职责**: Layer 0-11 技术架构定义  
> **父文档**: README.md

---

## 接口与契约（蓝图终稿）

- 全库 API 与事件约定真源：[`API_Contract.md`](../03_TRADING_TACTICS/API_Contract.md)。本文是架构权威说明，跨层数据流、模块调用与事件边界的最终口径以契约真源为准；如本文与契约冲突，以契约真源为准并在后续架构治理批次同步修订。

## 验收标准（可检查）

- Layer 0-11 分层表（§1）与“完整分层架构（§2）”一致，不出现编号/名称冲突。
- “跨层级数据流（§4）”中统一入口能跳转到 `API_Contract.md`。
- “相关文档（§5）”中的相对链接可点击跳转且不引入新的无效内链。

## 已知限制

- 本文包含实现侧与审计侧路径引用（例如施工目录或审计状态目录）；本文只提供架构与边界权威说明，具体实施细节与索引维护由对应专项批次负责。
- “旧层架构 ↔ 终极蓝图架构”映射为兼容说明，后续分层若调整需与 `API_Contract.md` 的契约边界同步更新。

> **🔔 重要更新说明 (2026-04-03)**
> 
> 本文档描述 **Layer 0-11 完整架构体系**，涵盖技术实现到战略决策全流程。  
> **新增顶层架构 (Layer 9-11)**：  
> - **Layer 9**：研究与创新层 — AI 虚拟研究、实验与创新孵化  
> - **Layer 10**：治理与合规层 — 内部控制体系 + 合规监控  
> - **Layer 11**：战略决策层 — 战略资产配置 + 风险预算分配  
> 
> **建议优先阅读**：  
> - **架构设计**：[PROFESSIONAL_MULTI_TIMEFRAME_ARCHITECTURE.md](./PROFESSIONAL_MULTI_TIMEFRAME_ARCHITECTURE.md) — 三级时间框架融合架构  
> - **实施指导**：[PROFESSIONAL_IMPLEMENTATION_BLUEPRINT.md](./PROFESSIONAL_IMPLEMENTATION_BLUEPRINT.md) — 实施路线图与开源集成策略  
> 
> **架构选择建议**：  
> - **技术实现**：继续使用本文档（Layer 0-11）  
> - **业务决策**：使用专业多时间框架架构  
> - **项目实施**：使用专业实施蓝图  
---

## 1. 双重架构关系

本系统采用 **双层架构** 设计。

以下是 **Layer 0-11** 自底向上栈位（与下表「架构对应关系」一致）：

| Layer | 名称 | 要点 |
|-------|------|------|
| 11 | 战略决策层 | 战略资产配置、风险预算 |
| 10 | 治理与合规层 | 内控与合规监控 |
| 9 | 研究与创新层 | AI 研究、创新孵化 |
| 8 | 人机交互层 | 授权、监控、报告 |
| 7 | AI 报告层 | 绩效与自动报告 |
| 6 | 组合优化层 | Barra、CVXPY 等 |
| 5 | 策略执行层 | 含 QMT 等执行通道 |
| 4 | 机器学习层 | ML Pipeline |
| 3 | 舆情分析层 | 新闻、情感、事件 |
| 2 | Alpha 因子层 | 大规模因子库 |
| 1 | 数据预处理层 | 清洗与对齐 |
| 0 | 数据源层 | iFind、SuperCommand 等 |

### 架构对应关系

| 旧层架构 | 终极蓝图架构 | 变化说明 |
|-----------|-------------|----------|
| Layer 0: 数据源（旧称） | Layer 0: 数据源层 | 名称优化 + iFind/SuperCommand |
| Layer 1: 前置（旧称） | Layer 1: 数据预处理层 | 名称优化 |
| Layer 2: Alpha（旧称） | Layer 2: Alpha 因子层 | 名称优化 + 5700+ 因子 |
| Layer 3: 风险（旧称） | （融入各层） | 重构为风险模型并贯穿各层 |
| Layer 4: 组合（旧称） | Layer 6: 组合优化层 | 升级 + Barra + CVXPY |
| Layer 5: 执行（旧称） | Layer 5: 策略执行层 | QMT API |
| Layer 6: 风控（旧称） | （融入各层） | 重构为风控贯穿各层 |
| Layer 7: 绩效（旧称） | Layer 7: AI 报告层 | 升级为 AI 自动报告 |
| **新增** | Layer 3: 舆情分析层 | 新闻 / 情感 / 事件 |
| **新增** | Layer 4: 机器学习层 | ML Pipeline |
| **新增** | Layer 8: 人机交互层 | 授权 / 监控 / 报告 |
| **新增** | Layer 9: 研究与创新层 | 研究能力 |
| **新增** | Layer 10: 治理与合规层 | 治理能力 |
| **新增** | Layer 11: 战略决策层 | 战略能力 |

---

## 2. 完整分层架构 (Layer 0-11)

```
Layer 0: 数据源层 (Data Sources)
  └─ Layer 1: 数据预处理层 (Preprocessing)
  └─ Layer 2: Alpha 因子层 (Alpha Factors)
  └─ Layer 3: 舆情分析层 (Sentiment & Events) 🆕
  └─ Layer 4: 机器学习层 (Machine Learning) 🆕
  └─ Layer 5: 策略执行层 (Strategy Execution)
  └─ Layer 6: 组合优化层 (Portfolio Optimization)
  └─ Layer 7: AI 报告层 (AI Reporting)
  └─ Layer 8: 人机交互层 (Human-AI Interface)
  └─ Layer 9: 研究与创新层 (Research & Innovation) 🆕
  └─ Layer 10: 治理与合规层 (Governance & Compliance) 🆕
  └─ Layer 11: 战略决策层 (Strategic Decision) 🆕
```

---

## 3. 详细分层架构

### Layer 0-11: 技术实现层

详细内容见本文第 1～2 节分层表与下文各 Layer 小节。
---

### Layer 9: 研究与创新层 🆕

**设计理由**：

- **持续创新**：量化市场快速变化，需要持续研究新因子、新策略。  
- **AI 辅助研究**：AI 可模拟研究团队，进行文献追踪与想法验证。  
- **知识积累**：研究成果需要系统化管理，避免重复造轮子。  
- **个人优势**：个人开发者可通过 AI 弥补团队规模劣势。  

| 模块 | 功能 | 技术方案 |
|------|------|----------|
| AI 虚拟研究实验室 | 模拟研究团队协作 | GLM-4.7-Flash 多角色 |
| 创新孵化器 | 新想法快速验证 | 回测框架 + AI 评估 |
| 学术前沿追踪 | 论文自动检索解析 | arXiv API + GLM-4 |
| 研究知识管理 | RAG 知识库 | ChromaDB + Embedding |

**详细蓝图**: [RESEARCH_INNOVATION_LAYER_BLUEPRINT.md](./RESEARCH_INNOVATION_LAYER_BLUEPRINT.md)

---

### Layer 10: 治理与合规层 🆕

**设计理由**：

- **风险控制**：金融交易风险高，需要完善的内部控制机制。  
- **合规要求**：即使个人交易也需遵循基本合规原则。  
- **决策审计**：所有 AI 决策需要可追溯、可解释。  
- **专业标准**：对标专业机构治理标准。  

| 模块 | 功能 | 技术方案 |
|------|------|----------|
| 内部控制系统 | 交易授权、操作审计 | 规则引擎 + AI 审核 |
| 合规监控系统 | 合规检查、预警 | 规则引擎 + 实时监控 |
| 决策审计追踪 | AI 决策记录、解释 | 日志系统 + 可解释 AI |
| 风险治理框架 | 风险评估、预算管理 | 风险模型 + AI 评估 |

**详细蓝图**: [GOVERNANCE_COMPLIANCE_LAYER_BLUEPRINT.md](./GOVERNANCE_COMPLIANCE_LAYER_BLUEPRINT.md)

---

### Layer 11: 战略决策层 🆕

**设计理由**：

- **资产配置**：长期投资成功的关键在于正确的资产配置  
- **风险预算**：科学分配风险预算，避免过度集中  
- **策略选择**：多策略环境下需要动态选择最优策略  
- **战略调整**：市场环境变化时需要及时调整战略  

| 模块 | 功能 | 技术方案 |
|------|------|----------|
| 战略资产配置 | 资产配置决策、经济范式判断 | 优化算法+AI判断 |
| 风险预算分配 | 风险预算分配、风险贡献分析 | 风险模型+AI分配 |
| 投资策略选择 | 策略评估、策略组合优化 | 优化算法+AI评估 |
| 战略调整决策 | 市场环境监控、战略调整 | 监控系统+AI决策 |
| 投资组合保险 | CPPI/TIPP/OBPI策略 | 保险策略引擎 |
| 融资融券管理 | 杠杆控制、保证金管理 | 风险控制引擎 |
| 业绩归因系统 | Brinson归因、因子归因 | 归因分析引擎 |
| 流动性管理 | 流动性监控、压力测试 | 流动性引擎 |
| 交易成本分析 | TCA分析、成本优化 | tcapy集成 |
| 再平衡决策 | 触发条件、再平衡执行 | 决策引擎 |
| 基准管理 | 基准跟踪、跟踪误差分析 | 基准管理器 |
| 情景分析 | 压力测试、情景模拟 | 情景引擎 |
| 市场状态识别 | HMM经济周期识别 | hmmlearn集成 |
| 投资限制管理 | 约束规则、实时检查 | 约束引擎 |
| 宏观因子系统 | 因子构建、暴露分析 | skfolio集成 |
| ESG投资系统 | ESG评分、约束优化 | PyPortfolioOpt |
| 税务管理系统 | 印花税计算、成本跟踪 | 批次管理器 |
| 多策略协调系统 | 信号冲突解决、资金协调 | 协调引擎 |
| IPS管理系统 | 投资政策声明、合规检查 | IPS管理器 |
| 资本配置系统 | 资本分配、效率优化 | Riskfolio-Lib |
| 投资决策审计 | 决策追溯、复盘分析 | 审计日志系统 |

**详细蓝图**: [STRATEGIC_DECISION_LAYER_BLUEPRINT.md](./STRATEGIC_DECISION_LAYER_BLUEPRINT.md) · 宏观因子专篇：[MACRO_FACTOR_SYSTEM_BLUEPRINT.md](../05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/MACRO_FACTOR_SYSTEM_BLUEPRINT.md)

**能力与实施蓝图对照（审计维护）**：[LAYER11_CAPABILITY_TO_BLUEPRINT_MAP_20260408.md](../09_AUDIT/STATE/LAYER11_CAPABILITY_TO_BLUEPRINT_MAP_20260408.md)（上表各模块 ↔ `01_BLUEPRINTS` / 战略决策卷；22 项均已链到具体蓝图）。

---

## 4. 跨层级数据流

### 4.1 核心数据流（Layer 0–11 纵览）

> 下图以**表格**替代旧版损坏的 ASCII 示意图；跨层接口细节见 **§4.2** 与 [API 接口契约](../03_TRADING_TACTICS/API_Contract.md)。

| Layer | 名称 | 主要产出 / 向下游传递 |
|-------|------|------------------------|
| 0 | 数据源层 | 原始数据（OHLCV、财务、新闻等） |
| 1 | 数据预处理层 | 清洗、标准化、对齐与校验后的数据 |
| 2 | Alpha 因子层 | 因子库与因子矩阵 |
| 3 | 舆情分析层 | 舆情信号与事件标签（→ Layer 5） |
| 4 | 机器学习层 | 预测信号、AI 因子（→ Layer 2 / 5） |
| 5 | 策略执行层 | 交易信号与目标仓位（与 Layer 6 往返风控与优化） |
| 6 | 组合优化层 | 满足约束的权重与组合方案 |
| 7 | AI 报告层 | 绩效与归因类分析报告 |
| 8 | 人机交互层 | 可视化、告警与人工授权/反馈（→ 各层） |
| 9 | 研究与创新层 | 新因子、新策略假设（→ Layer 2 / 5） |
| 10 | 治理与合规层 | 合规状态与审计记录（→ 各层） |
| 11 | 战略决策层 | 资产配置与风险预算（→ Layer 6 等） |

**反馈闭环**：Layer 8 人工输入、Layer 10 合规结论、Layer 11 战略调整均可反向影响上游执行与参数；具体以契约与蓝图为准。

### 4.2 关键数据接口

> **接口契约（单一入口）**：[API 接口契约](../03_TRADING_TACTICS/API_Contract.md) — 跨模块调用与数据边界约定；下表为 Layer 间数据流摘要，细节以契约为准。

| 数据流方向 | 数据类型 | 格式 | 频率 | 质量要求 |
|------------|----------|------|------|----------|
| **Layer 0 → Layer 1** | 原始市场数据 | OHLCV + 财务 + 新闻 | 实时/日频 | 完整度 ≥ 95% |
| **Layer 1 → Layer 2** | 清洗后数据 | 标准化 DataFrame | 日频 | 无关键缺失 |
| **Layer 2 → Layer 5** | 因子矩阵 | 因子值矩阵 | 日频 | IC > 0.05 |
| **Layer 3 → Layer 5** | 舆情信号 | 情感评分 + 事件标签 | 实时 | 准确率 ≥ 80% |
| **Layer 4 → Layer 2/5** | AI 预测信号 | 预测概率 + 置信度 | 日频 | 回测 Sharpe > 1.0 |
| **Layer 5 → Layer 6** | 策略信号 | 买卖信号 + 目标仓位 | 日频 | 通过风控检查 |
| **Layer 6 → Layer 5** | 优化后组合 | 权重向量 + 约束条件 | 日频 | 满足所有约束 |
| **Layer 5 → Layer 7** | 交易执行结果 | 订单 + 成交记录 | 实时 | 完整可审计 |
| **Layer 7 → Layer 8** | 绩效报告 | 归因分析 + 可视化 | 日/周 | 可解释性强 |
| **Layer 8 → 各层** | 人工指令 | 授权/否决/参数调整 | 按需 | 明确无歧义 |
| **Layer 9 → Layer 2/5** | 研究成果 | 新因子 / 新策略 | 按需 | 回测验证通过 |
| **Layer 10 → 各层** | 合规检查 | 合规状态 + 审计记录 | 实时 | 100% 合规 |
| **Layer 11 → Layer 6** | 战略配置 | 资产配置 / 风险预算 | 季度/年度 | 符合战略目标 |

### 4.3 数据流控制机制

1. **数据质量门控**
   - Layer 1：数据完整性检查（缺失率 ≤ 5%）
   - Layer 2：因子有效性检查（IC 显著 > 0）
   - Layer 5：信号质量检查（回测验证通过）
   - Layer 6：组合可行性检查（满足所有约束）
   - Layer 9：研究成果验证（回测 Sharpe > 1.5）
   - Layer 10：合规检查（100% 通过）
   - Layer 11：战略合理性检查（符合风险预算）

2. **异常处理流程**
   - 数据缺失：自动填充或降级使用  
   - 接口超时：重试机制 + 备选数据源  
   - 质量不达标：告警 + 人工干预  
   - 风控拒绝: 停止执行 + 记录原因
   - 合规违规: 立即停止 + 人工审核
   - 战略偏离: 预警 + 调整建议

3. **数据版本管理**
   - 原始数据：时间戳 + 数据源标识  
   - 处理数据：处理流水线版本号  
   - 因子数据: 因子定义版本 + 计算参数
   - 信号数据：策略版本 + 市场状态  
   - 研究成果：研究版本 + 验证结果  
   - 合规记录: 合规版本 + 审计日志
   - 战略决策: 决策版本 + 执行状态
---
## 5. 相关文档

| 文档 | 说明 |
|------|------|
| [MARKET_REGIME.md](./MARKET_REGIME.md) | 市场状态识别 |
| [HUMAN_AI_INTEGRATION_BLUEPRINT.md](./HUMAN_AI_INTEGRATION_BLUEPRINT.md) | 人机协作流程 |
| [TECH_STACK.md](./TECH_STACK.md) | 技术栈选择 |
| README.md | 框架总览 |
| [01_BLUEPRINTS 全目录索引](../05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/INDEX.md) | 实施侧全部蓝图/报告类 Markdown 列表（`generate_01_blueprints_index.py` 维护） |

### P0级核心蓝图
#### AI增强系统

| 文档 | 说明 |
|------|------|
| **[AI_EXPLAINABILITY_TOOLKIT_BLUEPRINT.md](./AI_EXPLAINABILITY_TOOLKIT_BLUEPRINT.md)** | **🆕 P0** AI 可解释性工具蓝图 |
| **[RAG_SYSTEM_BLUEPRINT.md](./RAG_SYSTEM_BLUEPRINT.md)** | **🆕 P0** RAG 知识系统（原 RAG_KNOWLEDGE 条目合并指向本蓝图） |
| **[ADAPTIVE_MODEL_SYSTEM_BLUEPRINT.md](./ADAPTIVE_MODEL_SYSTEM_BLUEPRINT.md)** | **🆕 P0** 统一自适应模型蓝图 |
| **[IMPLEMENTATION_ACCELERATION_BLUEPRINT.md](./IMPLEMENTATION_ACCELERATION_BLUEPRINT.md)** | **🆕 P0** 实施加速方案蓝图 |

#### 核心监控体系

| 文档 | 说明 |
|------|------|
| **[DATA_QUALITY_MONITORING_BLUEPRINT.md](./DATA_QUALITY_MONITORING_BLUEPRINT.md)** | **🆕 P0** 数据质量监控蓝图 |
| **[REALTIME_RISK_MONITORING_BLUEPRINT.md](./REALTIME_RISK_MONITORING_BLUEPRINT.md)** | **🆕 P0** 实时风险监控蓝图 |
| **[STRESS_TESTING_SYSTEM_BLUEPRINT.md](../05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/STRESS_TESTING_SYSTEM_BLUEPRINT.md)** | **🆕 P0** 压力测试系统蓝图 |
| **[COMPLIANCE_MONITORING_SYSTEM_BLUEPRINT.md](./COMPLIANCE_MONITORING_SYSTEM_BLUEPRINT.md)** | **🆕 P0** 合规监控系统蓝图 |

#### 顶层架构体系 (Layer 9-11)

| 文档 | 说明 |
|------|------|
| **[RESEARCH_INNOVATION_LAYER_BLUEPRINT.md](./RESEARCH_INNOVATION_LAYER_BLUEPRINT.md)** | **🆕 Layer 9** 研究与创新层蓝图：AI 虚拟研究实验与创新孵化 |
| **[GOVERNANCE_COMPLIANCE_LAYER_BLUEPRINT.md](./GOVERNANCE_COMPLIANCE_LAYER_BLUEPRINT.md)** | **🆕 Layer 10** 治理与合规层蓝图：内部控制体系与合规监控 |
| **[STRATEGIC_DECISION_LAYER_BLUEPRINT.md](./STRATEGIC_DECISION_LAYER_BLUEPRINT.md)** | **🆕 Layer 11** 战略决策层蓝图：战略资产配置与风险预算分配 |

#### 横向支撑体系

| 文档 | 说明 |
|------|------|
| **[DISASTER_RECOVERY_BLUEPRINT.md](./DISASTER_RECOVERY_BLUEPRINT.md)** | **📋 规划** 灾备体系蓝图：数据备份、故障恢复与异地容灾 |

---

**版本**: v5.6 | **更新**: 2026-04-08 | **状态**: 活跃
