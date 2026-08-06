---
title: 107 环节决策表（已填"怎么搞到手"列）
date: 2026-08-05
status: active
related:
  - docs/_working/107_pending_steps_inventory.md
  - docs/_working/2026-08-05_decision_table_and_plan_engine_design.md
ttl: task_bound
---

# 107 环节决策表 — "🎯 怎么搞到手"列已填

> 每个环节给出：🎯怎么搞到手（🔴自建/🟢开源替代/🟡借鉴增强/⬜弃用）+ 理由 + 开源候选
> 用户逐行拍板后，据此安排施工/采购/弃用。

## 总览统计

| 决策 | 数量 | 占比 | 大白话 |
|---|---|---|---|
| 🔴 自建 | 49 | 46% | 自己车间造（核心alpha+A股特色） |
| 🟡 借鉴增强 | 43 | 40% | 自建为主，局部复用开源组件 |
| 🟢 开源替代 | 14 | 13% | 网上有现成货，搬来直接用 |
| ⬜ 弃用 | 1 | 1% | 暂不做（EU AI Act 非A股优先） |

> 📌 **2026-08-05 二次审查调整**：原 🔴自建65/🟡借鉴27，经二次扫描发现 7 个环节可借开源算法库（SciPy/hmmlearn/statsmodels/networkx/Presidio 等），调整为 🟡借鉴。净省 7 个自建工作量。
>
> 📌 **2026-08-05 三次审查调整**：经第三轮循环审查，再发现 9 个环节可借开源（Kedro/learn2learn/hmmlearn/networkx/eventstudy/sklearn），调整为 🟡借鉴。净省 9 个自建工作量。
>
> 📌 **循环审查结论**：第三轮后剩余 49 个🔴自建，经第四轮逐个复核确认均为"核心alpha/A股特色/合规硬约束/业务特有"，无可再借开源。**开源/借鉴可挖=0，循环结束**。

---

## 一、设计态 57 个（已画图未造）

### 阶段 02 模型训练（8 个）

| step_id | 中文名 | 🎯怎么搞 | 理由 | 开源候选 |
|---|---|---|---|---|
| BM-MT-01 | 训练流水线 | 🔄🟡借鉴 | 训练流水线框架借开源，业务逻辑自建 | **Kedro / PyTorch Lightning** |
| BM-MT-01-B | AI辅助代码生成 | 🟡借鉴 | 代码生成借开源，业务逻辑自建 | LangChain/Copilot |
| BM-MT-01-C | 策略数字孪生 | 🔴自建 | 策略特有，无通用开源 | — |
| BM-MT-02-A | 模型灰度发布影子部署 | 🟡借鉴 | 发布框架借开源，影子逻辑自建 | MLflow Models |
| BM-MT-02-B | 对抗鲁棒性验证 | 🟡借鉴 | 对抗攻击库借开源，A股场景自建 | CleverHans/ART |
| BM-MT-06 | 元学习自我进化 | 🔄🟡借鉴（后置） | 元学习算法借开源，自我进化逻辑自建 | **learn2learn** |
| BM-MT-06-A | 元学习RSI四维度 | 🔄🟡借鉴（后置） | 元学习算法借开源，RSI四维度自建 | **learn2learn** |
| BM-MT-06-B | 学习效果反馈闭环 | 🔴自建（后置） | 反馈闭环偏业务，无通用开源 | — |

### 阶段 03 回测验证（1 个）

| step_id | 中文名 | 🎯怎么搞 | 理由 | 开源候选 |
|---|---|---|---|---|
| BM-BT-08 | 试运行验证 | 🔴自建 | 已有回测引擎，试运行是它的延伸 | — |

### 阶段 05 选股（19 个）⭐核心 alpha 战场

| step_id | 中文名 | 🎯怎么搞 | 理由 | 开源候选 |
|---|---|---|---|---|
| BM-SEL-26 | 决策可解释性 | 🟡借鉴 | 可解释性库借开源，业务解释自建 | SHAP/LIME |
| BM-SEL-03 | 市场状态感知 | 🔄🟡借鉴 | 市场状态分类借HMM，A股状态定义自建 | **hmmlearn** |
| BM-SEL-04 | 次日8态走势预测 | 🔴自建 | A股T+1特色，BM-PLAN核心依赖 | — |
| BM-SEL-06 | 跨市场传导感知 | 🔄🟡借鉴 | 传导分析借图论库，A股传导自建 | **networkx + Diebold-Yilmaz** |
| BM-SEL-07 | 体制转换检测 | 🟡借鉴 | 变点检测+HMM体制切换借开源，A股体制自建 | ruptures + hmmlearn |
| BM-SEL-09 | 调整周期追踪 | 🔄🟡借鉴 | 信号处理（Welch功率谱/周期图）借SciPy，A股应用自建 | **SciPy信号处理** |
| BM-SEL-10 | 行情生命周期阶段 | 🔄🟡借鉴 | HMM生命周期状态建模借开源，A股阶段自建 | **hmmlearn** |
| BM-SEL-11 | 知识图谱因果推演 | 🟡借鉴 | 因果推断库借开源，金融场景自建 | DoWhy/CausalNex |
| BM-SEL-12 | 分布特征工程 | 🟡借鉴 | 特征工程库借开源，A股因子自建 | tsfresh |
| BM-SEL-13 | 收益率条件密度预测 | 🔄🟡借鉴 | 条件分布拟合借开源，A股应用自建 | **statsmodels/neuralforecast** |
| BM-SEL-02-M | 因果因子验证层 | 🟡借鉴 | 因果验证库借开源，因子定义自建 | DoWhy/DML |
| BM-SEL-14 | 共形预测 | 🟡借鉴 | 共形预测库借开源，A股应用自建 | MAPIE |
| BM-SEL-14-A | 自适应保形覆盖(TCP-RM) | 🔴自建 | 前沿研究，无成熟开源 | — |
| BM-SEL-15 | Survival止盈止损 | 🟡借鉴 | 生存分析库借开源，止盈策略自建 | lifelines |
| BM-SEL-16 | 分级指标过滤 | 🔴自建 | A股特色（ST/退市/停牌过滤） | — |
| BM-SEL-17 | 初筛漏斗 | 🔴自建 | 选股核心 | — |
| BM-SEL-18 | 精筛评分 | 🔴自建 | 选股核心 | — |
| BM-SEL-19 | 事件驱动分布筛选 | 🔄🟡借鉴 | 事件研究法库借开源，A股事件自建 | **eventstudy** |
| BM-SEL-03-B | 市场状态传感器 | 🔴自建 | A股特色 | — |

### 阶段 06 买入（14 个）

| step_id | 中文名 | 🎯怎么搞 | 理由 | 开源候选 |
|---|---|---|---|---|
| BM-BUY-10 | 合规技术深度 | 🔴自建 | A股合规 | — |
| BM-BUY-11 | 合规持续运营 | 🔴自建 | A股合规 | — |
| BM-BUY-12 | 硬边界裁定 | 🔴自建 | A股合规 | — |
| BM-BUY-13 | 合规扩展EU AI Act | ⬜弃用 | 暂不做EU，非A股优先 | — |
| BM-BUY-15 | 交易合规检测 | 🔴自建 | A股合规 | — |
| BM-BUY-04 | 分批建仓 | 🔴自建 | A股特色 | — |
| BM-BUY-02-A-1 | 市场状态预测 | 🔄🟡借鉴 | 分类算法借sklearn，A股状态定义自建 | **scikit-learn** |
| BM-BUY-02-A-1-a | 3×3矩阵分类 | 🔄🟡借鉴 | 矩阵分类借sklearn，3×3定义自建 | **scikit-learn** |
| BM-BUY-02-A-1-b | 2叠加态检测 | 🔴自建 | A股特色 | — |
| BM-BUY-02-A-1-c | T+1次日8态预测 | 🔴自建 | A股T+1特色，BM-PLAN依赖 | — |
| BM-BUY-02-A-1-d | 体制转换检测 | 🟡借鉴 | 变点检测库借开源 | ruptures |
| BM-BUY-02-A-2 | 因子直通裁决 | 🔴自建 | 核心决策（横切机制归轨） | — |
| BM-BUY-08-A | 四项必做清单检测 | 🔴自建 | A股特色 | — |
| BM-BUY-08-B | 四项严禁检测 | 🔴自建 | A股合规 | — |

### 阶段 07 卖出（7 个）

| step_id | 中文名 | 🎯怎么搞 | 理由 | 开源候选 |
|---|---|---|---|---|
| BM-SELL-07 | 卖出情景预案 | 🔴自建（改造） | 退化为BM-PLAN-01卖出侧边界提供者（已决策） | — |
| BM-SELL-04 | 止盈止损族 | 🔴自建 | A股特色 | — |
| BM-SELL-04-A | 止盈族 | 🔴自建 | A股特色 | — |
| BM-SELL-04-B | 止损族 | 🔴自建 | A股特色 | — |
| BM-SELL-04-E | 分批退出 | 🔴自建 | A股特色 | — |
| BM-SELL-08 | 做T日内套利 | 🔴自建 | A股T+0做T特色 | — |
| BM-SELL-09 | 卖出闭环优化 | 🔴自建 | 闭环反馈 | — |

### 阶段 09 风控（4 个）

| step_id | 中文名 | 🎯怎么搞 | 理由 | 开源候选 |
|---|---|---|---|---|
| BM-RC-10 | 风险否决权 | 🔴自建 | 风控核心 | — |
| BM-RC-11 | 独立风险数据管道 | 🔴自建 | 风控核心 | — |
| BM-RC-04-F | AI/Agent风险监控 | 🔄🟡借鉴 | AI安全监控框架借开源，A股风控自建 | **Presidio/Nemesis** |
| BM-RC-10-A | 否决执行引擎 | 🔴自建 | 风控核心 | — |

### 阶段 10 执行（3 个）

| step_id | 中文名 | 🎯怎么搞 | 理由 | 开源候选 |
|---|---|---|---|---|
| BM-EXE-04 | Pre-Trade合规检查 | 🔴自建 | A股2026.4.7新规，合规硬约束 | — |
| BM-EXE-05 | 智能订单路由拆单 | 🟡借鉴 | AC内核借开源，miniQMT外壳自建 | AlmgrenChriss-Execution-Analytics-Platform |
| BM-EXE-06 | 成交回报持仓更新 | 🔴自建 | A股T+1结算+佣金/印花税特色 | — |

### 阶段 11 对账清算（1 个）

| step_id | 中文名 | 🎯怎么搞 | 理由 | 开源候选 |
|---|---|---|---|---|
| BM-REC-02-B | 绩效归因 | 🟡借鉴 | 归因库借开源，A股归因自建 | pyfolio |

---

## 二、候选态 50 个（候选池，未定性）

### 阶段 01 研究孵化（27 个）🟢开源为主

| step_id | 中文名 | 🎯怎么搞 | 理由 | 开源候选 |
|---|---|---|---|---|
| BM-RES-08 | 知识清洗与结构化 | 🟡借鉴 | LLM清洗借开源，金融知识自建 | LangChain |
| BM-RES-09 | 知识分类与策略提取 | 🟡借鉴 | LLM分类借开源，策略提取自建 | LangChain |
| BM-RES-10 | 模块映射与工厂匹配 | 🔴自建 | 业务特有 | — |
| BM-RES-11 | 多模态知识采集 | 🟡借鉴 | 多模态框架借开源 | LangChain |
| BM-RES-01-B | 特征存储与PIT正确性 | 🟢开源替代 | 特征存储成熟开源 | **Feast** |
| BM-RES-01-C | 研究数据沙箱 | 🟡借鉴 | 版本化借开源，隔离墙自建 | DVC |
| BM-RES-01-D | 研究资产版本化 | 🟢开源替代 | 数据版本化成熟开源 | **DVC** |
| BM-RES-02-A | 实验记录与对比 | 🟢开源替代 | 实验追踪成熟开源 | **MLflow** |
| BM-RES-02-B | 可复现性管理 | 🟢开源替代 | 复现管理成熟开源 | **MLflow+DVC** |
| BM-RES-02-C | 实验异常检测 | 🟡借鉴 | 框架借MLflow，异常规则自建 | MLflow |
| BM-RES-02-D | 复现包生成 | 🟢开源替代 | MLflow内置 | **MLflow** |
| BM-RES-03 | 假设管理与发现沉淀 | 🔴自建 | 业务特有，无通用开源 | — |
| BM-RES-03-A | 假设生命周期管理 | 🔴自建 | 业务特有 | — |
| BM-RES-03-B | 研究发现知识库 | 🟡借鉴 | 向量DB借开源，知识结构自建 | Qdrant/Chroma |
| BM-RES-03-C | 研究目录与搜索 | 🟢开源替代 | 向量搜索成熟开源 | **Qdrant** |
| BM-RES-04 | 研究工作流编排 | 🟢开源替代 | 工作流编排成熟开源 | **Prefect** |
| BM-RES-04-A | DAG编排与任务调度 | 🟢开源替代 | DAG调度成熟开源 | **Prefect/Airflow** |
| BM-RES-05 | Notebook与协作 | 🟢开源替代 | Notebook平台成熟开源 | **JupyterHub** |
| BM-RES-05-A | Notebook转生产 | 🟢开源替代 | Papermill成熟开源 | **Papermill** |
| BM-RES-05-B | 研究协作中心 | 🟡借鉴 | 协作框架借开源，定制自建 | — |
| BM-RES-05-C | 研究信息隔离墙 | 🔴自建 | 合规特色，无通用开源 | — |
| BM-RES-06-A | LLM研究助手 | 🟡借鉴 | LLM框架借开源，研究prompt自建 | LangChain |
| BM-RES-06-B | 论文追踪 | 🟢开源替代 | 论文追踪成熟开源 | **arxiv-daily** |
| BM-RES-07-A | 策略进化与因子挖掘 | 🔴自建（后置） | 核心 alpha，地基打好后再做 | — |
| BM-RES-08-A | 知识清洗流水线 | 🟡借鉴 | 同BM-RES-08 | LangChain |
| BM-RES-09-A | 知识类型分类体系 | 🟡借鉴 | 同BM-RES-09 | LangChain |
| BM-RES-10-A | 模块工厂架构 | 🔴自建 | 业务特有 | — |

### 阶段 02 模型训练（5 个）

| step_id | 中文名 | 🎯怎么搞 | 理由 | 开源候选 |
|---|---|---|---|---|
| BM-MT-02 | 实验追踪与自动晋升 | 🟢开源替代 | MLflow成熟 | **MLflow** |
| BM-MT-03 | AutoML与超参优化 | 🟢开源替代 | Optuna成熟 | **Optuna** |
| BM-MT-04 | 因子发现与因果发现 | 🟡借鉴 | 因果发现库借开源，金融因子自建 | CausalNex |
| BM-MT-05 | 漂移检测与自适应重训练 | 🟡借鉴 | 漂移检测库借开源，重训练策略自建 | evidently |
| BM-MT-05-A | 持续学习防遗忘 | 🟡借鉴 | 持续学习库借开源，A股模型自建 | AvalancheLIB |

### 阶段 04 仿真验证（1 个）

| step_id | 中文名 | 🎯怎么搞 | 理由 | 开源候选 |
|---|---|---|---|---|
| BM-SIM-01 | 市场仿真器 | 🟢开源替代 | 撮合内核用market-sim，多Agent用ABIDES | **ABIDES+market-sim** |

### 阶段 05 选股（6 个）

| step_id | 中文名 | 🎯怎么搞 | 理由 | 开源候选 |
|---|---|---|---|---|
| BM-SEL-02-J | 信号工厂子阶段流水线 | 🔴自建 | 替代弃用因子管线，核心 | — |
| BM-SEL-02-K | 多策略投票与加权 | 🔴自建 | 核心决策 | — |
| BM-SEL-02-L | 信号聚合器架构 | 🔴自建 | 核心决策 | — |
| BM-SEL-05-D | 主力行为自迭代推演 | 🔴自建（后置） | A股特色，高级能力 | — |
| BM-SEL-05-E | 庄家行为识别与模拟 | 🔴自建 | A股特色 | — |
| BM-SEL-05-F | 多方博弈模拟 | 🟡借鉴 | 博弈论库借开源，A股博弈自建 | Axelrod |

### 阶段 06 买入（1 个）

| step_id | 中文名 | 🎯怎么搞 | 理由 | 开源候选 |
|---|---|---|---|---|
| BM-BUY-06 | 外部指令盯盘 | 🔴自建 | 横切，A股特色 | — |

### 阶段 08 仓位管理（1 个）

| step_id | 中文名 | 🎯怎么搞 | 理由 | 开源候选 |
|---|---|---|---|---|
| BM-SEL-20 | 多策略交叉投票 | 🔄🟡借鉴 | 投票机制借sklearn，策略组合自建 | **scikit-learn VotingClassifier** |

### 阶段 09 风控（9 个）

| step_id | 中文名 | 🎯怎么搞 | 理由 | 开源候选 |
|---|---|---|---|---|
| BM-RC-12 | 极端事件与黑天鹅 | 🔴自建 | 风控核心 | — |
| BM-RC-04-E | 流动性风险监控 | 🔴自建 | 风控核心 | — |
| BM-RC-05-C | 亏损限额强制停盘 | 🔴自建 | A股特色（日2%周5%月10%） | — |
| BM-RC-06-D | 拥挤度检测 | 🔄🟡借鉴 | 拥挤度因子学术实现借开源，A股应用自建 | **CrowdingFactor库** |
| BM-RC-11-A | 独立风险指标计算 | 🔴自建 | 风控核心 | — |
| BM-RC-11-B | 风险报告生成 | 🟡借鉴 | 报告模板借开源，A股风控自建 | — |
| BM-RC-12-A | 黑天鹅模式库 | 🔴自建 | 风控核心 | — |
| BM-RC-12-B | 跨市场传导与传染 | 🔄🟡借鉴 | 传染模型借Diebold-Yilmaz指数+networkx，A股应用自建 | **networkx + Diebold-Yilmaz** |
| BM-RC-12-C | 流动性危机模拟 | 🔴自建 | 风控核心 | — |

---

## 三、弃用态 3 个（已废弃，记录用）

| step_id | 中文名 | 🎯怎么搞 | 理由 |
|---|---|---|---|
| BM-SEL-02 | 因子计算与信号生成 | ⬜已弃用 | 被 BM-SEL-02-J/K/L 信号工厂取代 |
| BM-SEL-02-A | 因子计算引擎 | ⬜已弃用 | 同上 |
| BM-SEL-02-C | 因子管线双模调度 | ⬜已弃用 | 同上 |

> ⚠️ 这 3 个按铁律应补做弃用流程：apply_depgraph 软删 build_status→deprecated + candidate_module_registry 记 rejected 理由。

---

## 四、按决策类型汇总（施工排期参考）

### 🟢 开源替代 14 个（最快落地——采购+集成）

| 开源项目 | 替代的环节 | 数量 |
|---|---|---|
| **MLflow** | BM-RES-02-A/B/D, BM-MT-02 | 4 |
| **DVC** | BM-RES-01-D | 1 |
| **Feast** | BM-RES-01-B | 1 |
| **Prefect/Airflow** | BM-RES-04/04-A | 2 |
| **JupyterHub** | BM-RES-05 | 1 |
| **Papermill** | BM-RES-05-A | 1 |
| **Qdrant** | BM-RES-03-C | 1 |
| **arxiv-daily** | BM-RES-06-B | 1 |
| **Optuna** | BM-MT-03 | 1 |
| **ABIDES+market-sim** | BM-SIM-01 | 1 |

### 🟡 借鉴增强 43 个（自建为主，局部复用开源组件）

| 开源组件 | 借鉴的环节 | 数量 |
|---|---|---|
| SHAP/LIME | BM-SEL-26 | 1 |
| ruptures + hmmlearn | BM-SEL-07, BM-BUY-02-A-1-d | 2 |
| **SciPy 信号处理** | BM-SEL-09 | 1 |
| **hmmlearn** | BM-SEL-03, BM-SEL-10 | 2 |
| DoWhy/CausalNex | BM-SEL-11, BM-SEL-02-M, BM-MT-04 | 3 |
| tsfresh | BM-SEL-12 | 1 |
| **statsmodels/neuralforecast** | BM-SEL-13 | 1 |
| MAPIE | BM-SEL-14 | 1 |
| lifelines | BM-SEL-15 | 1 |
| **eventstudy** | BM-SEL-19 | 1 |
| pyfolio | BM-REC-02-B | 1 |
| MLflow(组件) | BM-MT-02-A, BM-RES-02-C | 2 |
| CleverHans/ART | BM-MT-02-B | 1 |
| evidently | BM-MT-05 | 1 |
| AvalancheLIB | BM-MT-05-A | 1 |
| LangChain | BM-MT-01-B, BM-RES-08/09/11/08-A/09-A, BM-RES-06-A | 7 |
| DVC(组件) | BM-RES-01-C | 1 |
| Qdrant(组件) | BM-RES-03-B | 1 |
| AlmgrenChriss | BM-EXE-05 | 1 |
| Axelrod | BM-SEL-05-F | 1 |
| **CrowdingFactor库** | BM-RC-06-D | 1 |
| **Presidio/Nemesis** | BM-RC-04-F | 1 |
| **networkx + Diebold-Yilmaz** | BM-SEL-06, BM-RC-12-B | 2 |
| **Kedro / PyTorch Lightning** | BM-MT-01 | 1 |
| **learn2learn** | BM-MT-06, BM-MT-06-A | 2 |
| **scikit-learn** | BM-BUY-02-A-1, BM-BUY-02-A-1-a, BM-SEL-20 | 3 |

### 🔴 自建 49 个（核心，排工期）

按优先级分三档：
- **P0 先做**：BM-SEL-04 次日预测（BM-PLAN 依赖）、BM-SELL-07 改造、BM-EXE-04 合规、BM-EXE-06 Fill
- **P1 跟进**：BM-BUY-04 分批建仓、BM-SELL-04 止盈止损族、BM-RC-10 否决权
- **P2 后置**：BM-MT-06-B 学习反馈闭环、BM-RES-07-A 策略进化、BM-SEL-05-D 主力推演

### ⬜ 弃用 1 个

| step_id | 理由 |
|---|---|
| BM-BUY-13 | EU AI Act 合规扩展，暂不做，非A股优先 |

---

## 五、变更日志

| 日期 | 变更 |
|---|---|
| 2026-08-05 | 初建。107 行"怎么搞到手"全部填完。统计：🔴自建65/🟡借鉴27/🟢开源14/⬜弃用1 |
| 2026-08-05 | 二次审查调整 7 个：BM-SEL-09/10/13/07、BM-RC-06-D/04-F/12-B 从🔴自建改为🟡借鉴（新增 SciPy/hmmlearn/statsmodels/CrowdingFactor/Presidio/networkx）。统计：🔴自建58/🟡借鉴34/🟢开源14/⬜弃用1。净省7个自建工作量 |
| 2026-08-05 | 三次审查调整 9 个：BM-MT-01/06/06-A、BM-SEL-03/06/19、BM-BUY-02-A-1/02-A-1-a、BM-SEL-20 从🔴自建改为🟡借鉴（新增 Kedro/learn2learn/hmmlearn/eventstudy/sklearn）。统计：🔴自建49/🟡借鉴43/🟢开源14/⬜弃用1。净省9个自建工作量。第四轮复核确认剩余49个均不可再借，循环结束 |
